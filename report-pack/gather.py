"""Collect every number the report-pack PDF needs into one JSON file (run with project venv)."""
import json, os, sys, statistics
ROOT = "/Users/terence/Desktop/Cornell Tech/CS5342/assignment3"
sys.path.insert(0, ROOT); os.chdir(ROOT)
import pandas as pd
from pylabel import config
import evaluate as ev
from tests.conftest import make_post
from pylabel import PolicyProposalLabeler

out = {}
df = ev.load_dataset("data.csv")

# --- dataset composition
comp = df.groupby(["source", "split", "expected_label"]).size().unstack(fill_value=0)
out["composition"] = {f"{s}|{sp}": row.to_dict() for (s, sp), row in comp.iterrows()}
out["synthetic_categories"] = (df[df.source == "synthetic"].groupby("category").size()
                               .sort_index().to_dict())
cand = pd.read_csv("annotation/all_candidates.csv", dtype=str, keep_default_na=False)
out["n_candidates"] = len(cand)

# --- full run, ablations, baseline for 4 slices
decisions, lat, stats = ev.run_labeler(df, "labeler-inputs")
pred = [ev.predicted_label(d) for d in decisions]
df["pred"] = pred
df["score"] = [d.score for d in decisions]
df["reasons"] = [" | ".join(d.reasons) for d in decisions]
abl = {name: [ev.predicted_label(d) for d in ev.run_labeler(df, "labeler-inputs", enabled_groups=g)[0]]
       for name, g in ev.ABLATIONS}
base = list(df["text"].map(ev.keyword_baseline))
slices = {}
for src in ["synthetic", "real"]:
    for sp in ["dev", "test"]:
        m = (df.source == src) & (df.split == sp)
        gold = list(df[m].expected_label)
        idx = [i for i, x in enumerate(m) if x]
        row = {"n": int(m.sum()), "full": ev.summarize(gold, [pred[i] for i in idx]),
               "baseline": ev.summarize(gold, [base[i] for i in idx]),
               "ablations": {k: ev.summarize(gold, [v[i] for i in idx]) for k, v in abl.items()},
               "confusion": ev.confusion_matrix(gold, [pred[i] for i in idx])}
        slices[f"{src}_{sp}"] = row
out["slices"] = slices

# real test excluding Kalshi campaign
m = (df.source == "real") & (df.split == "test") & ~df.text.str.contains("kalshi", case=False)
idx = [i for i, x in enumerate(m) if x]
out["real_test_excl_kalshi"] = {"n": len(idx), **ev.summarize(list(df[m].expected_label), [pred[i] for i in idx])}
out["kalshi_posts"] = int(((df.source == "real") & df.text.str.contains("kalshi", case=False)).sum())

# --- threshold sweep on dev splits
orig = config.MEDIUM_THRESHOLD
sweep = {}
for t in [1.5, 2.0, 2.5, 3.0, 3.5]:
    config.MEDIUM_THRESHOLD = t
    p = [ev.predicted_label(d) for d in ev.run_labeler(df, "labeler-inputs")[0]]
    for src in ["synthetic", "real"]:
        mm = (df.source == src) & (df.split == "dev")
        ii = [i for i, x in enumerate(mm) if x]
        sweep.setdefault(src, {})[t] = ev.summarize(list(df[mm].expected_label), [p[i] for i in ii])
config.MEDIUM_THRESHOLD = orig
out["sweep"] = sweep

# --- efficiency
out["latency_ms"] = {"mean": statistics.mean(lat) * 1000, "median": statistics.median(lat) * 1000,
                     "p95": sorted(lat)[int(0.95 * len(lat))] * 1000, "max": max(lat) * 1000}
out["stats"] = {k: (v if not isinstance(v, float) else round(v, 4)) for k, v in stats.items()}
out["prefilter_dropped"] = sum(1 for d in decisions if not d.signals and d.tier == "none")

# --- errors (test, both sources)
errs = df[(df.split == "test") & (df.expected_label != df.pred)]
out["test_errors"] = [{"id": r.id, "source": r.source, "gold": r.expected_label, "pred": r.pred,
                       "score": round(r.score, 1), "text": r.text[:150].replace("\n", " "),
                       "reasons": r.reasons[:220]} for r in errs.itertuples()]

# --- demo walkthroughs (fresh labeler each, like the tests)
demos = [
    ("Policy Ex. 1: send-to-receive", "Send 0.1 ETH to 0x52908400098527886E0F7030069857D2E4169EE7 and we return 0.2 ETH.", "promo.bsky.social", 3, []),
    ("Policy Ex. 2: seed phrase", "Claim free tokens by entering your wallet recovery phrase.", "promo.bsky.social", 3, []),
    ("Policy Ex. 3: impersonation + fee", "Elon is giving away 5,000 BTC! A small verification fee of 0.01 BTC is required.", "elonmusk-official.bsky.social", 3, []),
    ("Policy Ex. 5: wallet connect + urgency", "Connect your wallet to claim free tokens before midnight!", "promo.bsky.social", 30, []),
    ("Policy Ex. 6: nothing to claim", "Update: the 10M pot is an airdrop. Nothing to claim.", "bunkyseal.bsky.social", 900, []),
    ("Policy Ex. 7: scam warning", "Beware of scammers promising large airdrops if you send them crypto first.", "dinosr.bsky.social", 900, []),
    ("Evasion: homoglyph + leetspeak", "S3nd 0.5 ЕТН, g3t 1 ЕТН b4ck! Limited time!", "promo.bsky.social", 2, []),
    ("Look-alike domain", "Uniswap airdrop is live, claim at https://uniswaap-claim.org now", "uni-drops.bsky.social", 5, ["https://uniswaap-claim.org"]),
    ("Official project handle", "Our airdrop claim is open now at https://app.uniswap.org", "uniswap.org", 900, ["https://app.uniswap.org"]),
    ("Real dev: faucet guide (v2 fix)", "Get faucet. Go to www.alchemy.com/faucets/ethereum-sepolia, enter EVM address, click 'Send me ETH'. You need at least 0.001 $ETH on mainnet to receive faucet tokens.", "dev.bsky.social", 17, []),
    ("Real dev: Kalshi campaign (v2 fix)", "Celebrating with a 1 BTC giveaway 👉 insurance-kalshi.com", "user.bsky.social", 700, []),
]
demo_out = []
for title, text, handle, age, links in demos:
    lab = PolicyProposalLabeler(None, "labeler-inputs", expand_links=False)
    d = lab.moderate_record(make_post(text, handle=handle, age_days=age, links=links))
    demo_out.append({"title": title, "text": text, "handle": handle, "age": age,
                     "labels": d.labels, "tier": d.tier, "score": round(d.score, 1),
                     "signals": [f"{s.name} ({s.weight:+g}{', hard' if s.hard else ''})" for s in d.signals]})
out["demos"] = demo_out
out["weights"] = config.WEIGHTS
out["thresholds"] = {"MEDIUM": config.MEDIUM_THRESHOLD, "CONTESTED_BONUS": config.CONTESTED_THRESHOLD_BONUS,
                     "DOWNGRADED_HARD": config.DOWNGRADED_HARD_WEIGHT}
json.dump(out, open(sys.argv[1], "w"), indent=1, default=str, ensure_ascii=False)
print("ok", len(out["test_errors"]), "errors")
for d in demo_out: print(d["title"], d["labels"], d["score"], d["signals"])
