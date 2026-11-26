"""
Merge the two independent annotations of real posts into data.csv.

Workflow (see ANNOTATION.md):
  1. Two team members fill `annotator_a` and `annotator_b` in real_posts_to_annotate.csv
     independently, using crypto-scam / unverified-airdrop / none.
  2. `python annotation/merge_annotations.py --check` prints Cohen's kappa and lists every
     disagreement. Discuss them and write the agreed label in BOTH columns (or put
     `final:<label>` in `notes`).
  3. `python annotation/merge_annotations.py --write [--status ai-annotated]` appends the adjudicated posts to
     data.csv with source=real, split assigned (every 3rd post per label -> dev), and
     annotation_status=adjudicated. Run it once; it refuses to add ids already in data.csv.
"""

import argparse
import csv
import os
from collections import Counter, defaultdict
from typing import Dict, List, Optional, Sequence

LABELS = ["crypto-scam", "unverified-airdrop", "none"]
HERE = os.path.dirname(os.path.abspath(__file__))
SHEET = os.path.join(HERE, "real_posts_to_annotate.csv")
DATA = os.path.join(os.path.dirname(HERE), "data.csv")


def cohens_kappa(a: Sequence[str], b: Sequence[str]) -> float:
    """Cohen's kappa for two annotators' label lists (1.0 = perfect agreement)."""
    n = len(a)
    if n == 0:
        return 0.0
    observed = sum(x == y for x, y in zip(a, b)) / n
    count_a, count_b = Counter(a), Counter(b)
    expected = sum(count_a[l] * count_b[l] for l in set(a) | set(b)) / (n * n)
    return 1.0 if expected == 1 else (observed - expected) / (1 - expected)


def final_label(row: Dict[str, str]) -> Optional[str]:
    """Agreed label, or the `final:<label>` override in notes; None if unresolved."""
    note = (row.get("notes") or "").strip()
    if note.startswith("final:"):
        label = note[6:].split("|", 1)[0].strip()
        if label in LABELS:
            return label
    a, b = row["annotator_a"].strip(), row["annotator_b"].strip()
    return a if a == b and a in LABELS else None


def main() -> None:
    parser = argparse.ArgumentParser(description="Check / merge real-post annotations.")
    parser.add_argument("--write", action="store_true", help="append adjudicated rows to data.csv")
    parser.add_argument("--status", default="adjudicated",
                        help="annotation_status to record (e.g. ai-annotated, human-verified)")
    args = parser.parse_args()

    rows = list(csv.DictReader(open(SHEET, encoding="utf-8")))
    both = [r for r in rows if r["annotator_a"].strip() in LABELS and r["annotator_b"].strip() in LABELS]
    print(f"{len(both)}/{len(rows)} posts labeled by both annotators")
    if both:
        kappa = cohens_kappa([r["annotator_a"].strip() for r in both],
                             [r["annotator_b"].strip() for r in both])
        print(f"Cohen's kappa: {kappa:.3f}")
    unresolved = [r for r in rows if final_label(r) is None]
    for r in unresolved:
        print(f"  unresolved {r['id']}: A={r['annotator_a'] or '-'} B={r['annotator_b'] or '-'} "
              f"| {' '.join(r['text'].split())[:90]}")
    if not args.write:
        return
    if unresolved:
        raise SystemExit(f"{len(unresolved)} posts unresolved; adjudicate them first.")

    existing = {r["id"] for r in csv.DictReader(open(DATA, encoding="utf-8"))}
    clash = existing & {r["id"] for r in rows}
    if clash:
        raise SystemExit(f"ids already in data.csv: {sorted(clash)[:5]}... (already merged?)")
    per_label: Dict[str, int] = defaultdict(int)
    fieldnames = next(csv.reader(open(DATA, encoding="utf-8")))
    with open(DATA, "a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        for r in sorted(rows, key=lambda r: r["post_created_at"]):
            label = final_label(r)
            split = "dev" if per_label[label] % 3 == 0 else "test"
            per_label[label] += 1
            writer.writerow({
                "id": r["id"], "split": split, "source": "real", "post_url": r["post_url"],
                "author_handle": r["author_handle"], "author_display_name": r["author_display_name"],
                "author_created_at": r["author_created_at"], "post_created_at": r["post_created_at"],
                "text": r["text"], "links": r["links"], "expected_label": label,
                "category": f"real/{label}",
                "rationale": (r.get("notes") or "").split("|", 1)[-1].strip(),
                "annotation_status": args.status,
            })
    print(f"Appended {len(rows)} real posts to data.csv: {dict(per_label)}")


if __name__ == "__main__":
    main()
