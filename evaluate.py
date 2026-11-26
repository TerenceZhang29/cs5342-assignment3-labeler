"""
Offline evaluation of the crypto giveaway / airdrop scam labeler on data.csv.

No login and no network calls: every post is read from data.csv and scored with
`PolicyProposalLabeler.moderate_record`.

Posts are processed in post-time order over the *whole* dataset (as a stream would be, so
the coordinated-link tracker sees the campaign build up), and metrics are reported for the
requested split. Tune on `--split dev`; report `--split test`.

Usage:
    python evaluate.py                     # test split, full report
    python evaluate.py --source real       # real Bluesky posts only (or --source synthetic)
    python evaluate.py --split dev         # the split used for tuning
    python evaluate.py --split all --show-errors

Outputs (in --out, default results/):
    eval_report.md     metrics, baseline, ablations, per-category table, efficiency
    predictions.csv    one row per post: gold, predicted, score, reasons
    review_queue.jsonl Ozone-style review queue produced by the full labeler
"""

import argparse
import os
import re
import statistics
import time
import tracemalloc
from collections import Counter, defaultdict
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import pandas as pd

from pylabel import PolicyProposalLabeler
from pylabel import config
from pylabel.ingest import record_from_row

CLASSES = [config.SCAM_LABEL, config.UNVERIFIED_LABEL, config.NO_LABEL]


# ---------------------------------------------------------------------------------------
# Metrics (pure functions, unit-tested in tests/test_evaluate.py)
# ---------------------------------------------------------------------------------------
def confusion_matrix(gold: Sequence[str], pred: Sequence[str],
                     classes: Sequence[str] = CLASSES) -> Dict[str, Dict[str, int]]:
    """matrix[gold][pred] = count."""
    matrix = {g: {p: 0 for p in classes} for g in classes}
    for g, p in zip(gold, pred):
        matrix[g][p] += 1
    return matrix


def precision_recall_f1(gold: Sequence[str], pred: Sequence[str], positive: str
                        ) -> Tuple[float, float, float, int]:
    """Precision, recall, F1 and support for one class (0.0 when undefined)."""
    tp = sum(g == positive and p == positive for g, p in zip(gold, pred))
    fp = sum(g != positive and p == positive for g, p in zip(gold, pred))
    fn = sum(g == positive and p != positive for g, p in zip(gold, pred))
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return precision, recall, f1, tp + fn


def accuracy(gold: Sequence[str], pred: Sequence[str]) -> float:
    return sum(g == p for g, p in zip(gold, pred)) / len(gold) if gold else 0.0


def to_binary(labels: Iterable[str]) -> List[str]:
    """Collapse to 'flagged' (any label) vs 'none'."""
    return ["flagged" if l != config.NO_LABEL else config.NO_LABEL for l in labels]


def summarize(gold: Sequence[str], pred: Sequence[str]) -> Dict[str, float]:
    """Headline numbers used in tables."""
    per_class = {c: precision_recall_f1(gold, pred, c) for c in CLASSES}
    flagged = precision_recall_f1(to_binary(gold), to_binary(pred), "flagged")
    return {
        "accuracy": accuracy(gold, pred),
        "macro_f1": statistics.mean(per_class[c][2] for c in CLASSES),
        "scam_p": per_class[config.SCAM_LABEL][0], "scam_r": per_class[config.SCAM_LABEL][1],
        "review_p": per_class[config.UNVERIFIED_LABEL][0],
        "review_r": per_class[config.UNVERIFIED_LABEL][1],
        "flag_p": flagged[0], "flag_r": flagged[1], "flag_f1": flagged[2],
    }


# ---------------------------------------------------------------------------------------
# Baseline: keyword blocking (policy §3.5 "Alternatives considered")
# ---------------------------------------------------------------------------------------
_BASELINE_KEYWORDS = re.compile(
    r"\b(airdrop|giveaway|seed phrase|recovery phrase|private key|free (eth|btc|tokens?|crypto)"
    r"|claim|connect (your )?wallet|double your)\b", re.IGNORECASE)


def keyword_baseline(text: str) -> str:
    """Label every post containing a crypto-promotion keyword as `crypto-scam`."""
    return config.SCAM_LABEL if _BASELINE_KEYWORDS.search(text or "") else config.NO_LABEL


# ---------------------------------------------------------------------------------------
# Running the labeler
# ---------------------------------------------------------------------------------------
def load_dataset(path: str) -> pd.DataFrame:
    """Load data.csv in post-time (stream) order, keeping only annotated rows."""
    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    df = df[df["expected_label"].isin(CLASSES)].copy()
    df["_t"] = pd.to_datetime(df["post_created_at"], utc=True, errors="coerce", format="ISO8601")
    return df.sort_values(["_t", "id"]).reset_index(drop=True)


def run_labeler(df: pd.DataFrame, input_dir: str, enabled_groups: Optional[Iterable[str]] = None,
                review_queue_path: Optional[str] = None) -> Tuple[List, List[float], Dict]:
    """Score every row in order; return decisions, per-post latencies and resource stats."""
    tracemalloc.start()
    t0 = time.perf_counter()
    labeler = PolicyProposalLabeler(None, input_dir, expand_links=False,
                                    review_queue_path=review_queue_path,
                                    enabled_groups=enabled_groups)
    load_seconds = time.perf_counter() - t0
    load_peak = tracemalloc.get_traced_memory()[1]
    tracemalloc.reset_peak()

    decisions, latencies = [], []
    for _, row in df.iterrows():
        record = record_from_row(row.to_dict())
        start = time.perf_counter()
        decisions.append(labeler.moderate_record(record))
        latencies.append(time.perf_counter() - start)
    run_peak = tracemalloc.get_traced_memory()[1]
    tracemalloc.stop()
    stats = {"load_seconds": load_seconds, "load_peak_bytes": load_peak,
             "run_peak_bytes": run_peak, "network_calls": labeler.network_calls,
             "behavior_blocklist": sorted(labeler.link_tracker.blocklist)}
    return decisions, latencies, stats


def predicted_label(decision) -> str:
    return decision.labels[0] if decision.labels else config.NO_LABEL


# ---------------------------------------------------------------------------------------
# Report formatting
# ---------------------------------------------------------------------------------------
def fmt_matrix(matrix: Dict[str, Dict[str, int]]) -> str:
    header = "| gold \\ predicted | " + " | ".join(CLASSES) + " |"
    lines = [header, "|" + "---|" * (len(CLASSES) + 1)]
    for g in CLASSES:
        lines.append(f"| **{g}** | " + " | ".join(str(matrix[g][p]) for p in CLASSES) + " |")
    return "\n".join(lines)


def fmt_per_class(gold, pred) -> str:
    lines = ["| label | precision | recall | F1 | support |", "|---|---|---|---|---|"]
    for c in CLASSES:
        p, r, f, n = precision_recall_f1(gold, pred, c)
        lines.append(f"| {c} | {p:.3f} | {r:.3f} | {f:.3f} | {n} |")
    p, r, f, n = precision_recall_f1(to_binary(gold), to_binary(pred), "flagged")
    lines.append(f"| *any label (binary)* | {p:.3f} | {r:.3f} | {f:.3f} | {n} |")
    return "\n".join(lines)


def fmt_summary_row(name: str, s: Dict[str, float]) -> str:
    return (f"| {name} | {s['accuracy']:.3f} | {s['macro_f1']:.3f} | {s['scam_p']:.3f} | "
            f"{s['scam_r']:.3f} | {s['flag_p']:.3f} | {s['flag_r']:.3f} |")


SUMMARY_HEADER = ("| system | accuracy | macro F1 | scam P | scam R | any-label P | any-label R |\n"
                  "|---|---|---|---|---|---|---|")

ABLATIONS = [
    ("text only", {"text"}),
    ("text + counter", {"text", "counter"}),
    ("text + counter + link", {"text", "counter", "link"}),
    ("+ account", {"text", "counter", "link", "account"}),
    ("full (+ behavior)", set(config.SIGNAL_GROUPS)),
]


def build_report(df, mask, decisions, latencies, stats, baseline_pred, ablation_rows,
                 split: str, show_errors: bool) -> str:
    sub = df[mask]
    gold = list(sub["expected_label"])
    pred = [predicted_label(d) for d, m in zip(decisions, mask) if m]
    out: List[str] = [f"# Evaluation report — split: `{split}` ({len(gold)} posts)\n"]

    counts = Counter(gold)
    out.append("Gold label distribution: " + ", ".join(f"{c}={counts.get(c, 0)}" for c in CLASSES))
    out.append("\n## Full labeler\n")
    out.append(f"Accuracy: **{accuracy(gold, pred):.3f}**\n")
    out.append(fmt_matrix(confusion_matrix(gold, pred)) + "\n")
    out.append(fmt_per_class(gold, pred) + "\n")
    scam_p = precision_recall_f1(gold, pred, config.SCAM_LABEL)[0]
    flag_r = precision_recall_f1(to_binary(gold), to_binary(pred), "flagged")[1]
    out.append(f"Policy targets (§3.3): `crypto-scam` precision ≥ 0.90 → **{scam_p:.3f}** "
               f"({'met' if scam_p >= 0.9 else 'NOT met'}); recall proxy (any label on "
               f"harmful posts) ≥ 0.80 → **{flag_r:.3f}** "
               f"({'met' if flag_r >= 0.8 else 'NOT met'}).\n")

    out.append("## Baseline and ablations\n")
    out.append("Keyword baseline = label every post containing a crypto-promotion keyword "
               "(the 'blocking crypto keywords' alternative rejected in policy §3.5).\n")
    out.append(SUMMARY_HEADER)
    out.append(fmt_summary_row("keyword baseline", summarize(gold, list(baseline_pred[mask]))))
    for name, summary in ablation_rows:
        out.append(fmt_summary_row(name, summary))
    out.append("")

    out.append("## Accuracy by category\n")
    out.append("| category | n | correct | accuracy | mistakes (gold→pred) |")
    out.append("|---|---|---|---|---|")
    by_cat = defaultdict(list)
    for (_, row), p in zip(sub.iterrows(), pred):
        by_cat[row["category"]].append((row["id"], row["expected_label"], p))
    for cat in sorted(by_cat):
        items = by_cat[cat]
        ok = sum(g == p for _, g, p in items)
        wrong = ", ".join(f"{i}: {g}→{p}" for i, g, p in items if g != p)
        out.append(f"| {cat} | {len(items)} | {ok} | {ok / len(items):.2f} | {wrong} |")
    out.append("")

    lat_ms = sorted(l * 1000 for l, m in zip(latencies, mask) if m)
    skipped = sum(d.tier == "skipped" for d, m in zip(decisions, mask) if m)
    out.append("## Efficiency (offline mode)\n")
    out.append(f"- Resource load (incl. {stats['blocklist_size']:,}-domain MetaMask blocklist): "
               f"{stats['load_seconds'] * 1000:.0f} ms, peak {stats['load_peak_bytes'] / 1e6:.1f} MB")
    out.append(f"- Per-post latency: mean {statistics.mean(lat_ms):.3f} ms, "
               f"median {statistics.median(lat_ms):.3f} ms, "
               f"p95 {lat_ms[int(0.95 * (len(lat_ms) - 1))]:.3f} ms, max {lat_ms[-1]:.3f} ms")
    out.append(f"- Extra peak memory while scoring all posts: {stats['run_peak_bytes'] / 1e3:.0f} KB")
    out.append(f"- Network calls: {stats['network_calls']} (live mode adds 2 API calls per "
               "post + up to 5 HEAD requests per shortened link)")
    out.append(f"- Posts dropped by prefilter: {skipped}/{len(gold)}")
    out.append(f"- Behavior blocklist at end of stream: {stats['behavior_blocklist'] or 'empty'}\n")

    if show_errors:
        out.append("## Errors\n")
        for (_, row), d, p in zip(sub.iterrows(), [d for d, m in zip(decisions, mask) if m], pred):
            if row["expected_label"] != p:
                out.append(f"- **{row['id']}** gold `{row['expected_label']}` → pred `{p}` "
                           f"(score {d.score:.1f}) — {row['text'][:110]!r}\n  - signals: "
                           f"{'; '.join(d.reasons) or '(none)'}")
    return "\n".join(out)


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate the labeler on data.csv (offline).")
    parser.add_argument("--data", default="data.csv")
    parser.add_argument("--input-dir", default="labeler-inputs")
    parser.add_argument("--split", choices=["dev", "test", "all"], default="test")
    parser.add_argument("--source", choices=["all", "synthetic", "real"], default="all",
                        help="restrict metrics to synthetic or real posts")
    parser.add_argument("--out", default="results")
    parser.add_argument("--show-errors", action="store_true", help="list every misclassified post")
    args = parser.parse_args()

    os.makedirs(args.out, exist_ok=True)
    queue_path = os.path.join(args.out, "review_queue.jsonl")
    if os.path.exists(queue_path):
        os.remove(queue_path)

    df = load_dataset(args.data)
    mask = (df["split"] == args.split) if args.split != "all" else pd.Series(True, index=df.index)
    if args.source != "all":
        mask &= df["source"] == args.source
    tag = args.split if args.source == "all" else f"{args.split}_{args.source}"

    decisions, latencies, stats = run_labeler(df, args.input_dir, review_queue_path=queue_path)
    from pylabel.resources import Resources
    stats["blocklist_size"] = len(Resources.load(args.input_dir).phishing_blocklist)

    gold_sub = list(df[mask]["expected_label"])
    ablation_rows = []
    for name, groups in ABLATIONS:
        abl_decisions, _, _ = run_labeler(df, args.input_dir, enabled_groups=groups)
        abl_pred = [predicted_label(d) for d, m in zip(abl_decisions, mask) if m]
        ablation_rows.append((name, summarize(gold_sub, abl_pred)))
    baseline_pred = df["text"].map(keyword_baseline)

    report = build_report(df, mask, decisions, latencies, stats, baseline_pred, ablation_rows,
                          tag, args.show_errors)
    with open(os.path.join(args.out, f"eval_report_{tag}.md"), "w", encoding="utf-8") as f:
        f.write(report + "\n")

    pd.DataFrame({
        "id": df["id"], "split": df["split"], "source": df["source"], "category": df["category"],
        "expected_label": df["expected_label"],
        "predicted_label": [predicted_label(d) for d in decisions],
        "tier": [d.tier for d in decisions],
        "score": [round(d.score, 2) for d in decisions],
        "hard_indicators": [";".join(d.hard_indicators) for d in decisions],
        "reasons": [" | ".join(d.reasons) for d in decisions],
        "latency_ms": [round(l * 1000, 4) for l in latencies],
        "text": df["text"],
    }).to_csv(os.path.join(args.out, "predictions.csv"), index=False)

    print(report)
    print(f"\nWrote {args.out}/eval_report_{tag}.md, predictions.csv, review_queue.jsonl")


if __name__ == "__main__":
    main()
