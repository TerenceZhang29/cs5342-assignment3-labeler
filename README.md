# Crypto Giveaway & Airdrop Scam Labeler — CS 5342 Assignment 3

**Group 8:** Terence Zhang, Lucas Sumartha, Ziqiao Gao, Lillian (Xintong) Li

This is a Bluesky labeler that implements our Assignment 2 policy, *Fraudulent Cryptocurrency
Giveaway and Airdrop Promotions on Bluesky*. It applies two labels:

| Label | When | Effect (per policy §3.1) |
|---|---|---|
| `crypto-scam` | A **hard indicator** that is not contradicted by context. Hard indicators are a "send X, get 2X back" promise, a seed/recovery phrase or private key request, an upfront fee to unlock a reward, a known phishing domain, a look-alike or homoglyph domain of a real project, an impersonated account running a giveaway with a call to action, or a brand name inside an unofficial claim domain. | Warn/blur, and queue for human takedown review. |
| `unverified-airdrop` | A **medium score** on a post that actually promotes an airdrop/giveaway (for example wallet connect + urgency + unofficial link), or a link posted by several new accounts. | Stays visible; queue for review. |

Scam warnings, airdrop news, legitimate airdrops from a project's own domain handle, satire and
non-crypto giveaways get no label. Every label carries the list of signals that caused it,
so it can be explained on appeal.

---

## Quick start

Requires Python 3.10+ (tested on 3.13).

```bash
python3 -m venv .venv
```
```bash
source .venv/bin/activate
```
```bash
pip install -r requirements.txt
```

Run the unit tests (97 tests, about 1 s, no network):

```bash
python -m pytest -q
```

Reproduce our evaluation (offline, no login or network needed):

```bash
python evaluate.py --split test --show-errors
```

This prints the report and writes `results/eval_report_test.md`, `results/predictions.csv`
and `results/review_queue.jsonl`. Use `--split dev` for the tuning split or `--split all`
for everything.

### Live mode (optional, needs a Bluesky account)

1. Copy `.env-TEMPLATE` to `.env` and fill in `USERNAME` and `PW`. Use an app password, and
   never commit `.env`.
2. Label live posts by URL. The CSV needs a `URL` column and an optional `Labels` JSON column,
   the same format as the starter's test files:
   ```bash
   python run_labeler.py labeler-inputs live-posts.csv
   ```
   Add `--emit_labels` only to actually publish labels; this is outward-facing.
3. Collect real candidate posts for annotation:
   ```bash
   python collect_posts.py --out candidates.csv
   ```

---

## How it works

```
data.csv row / bsky.app URL
        │  ingest.py
        ▼
   PostRecord ──► prefilter.py ── no link & no crypto term ──► [] (skipped)
        │            (normalization undoes leetspeak, homoglyphs, zero-width chars, s p a c i n g)
        ▼
  text_signals.py      send-to-receive · credential request · upfront fee · giveaway offer ·
                       claim CTA · wallet connect · urgency · wallet address · "not a scam" tell
  link_signals.py      MetaMask blocklist (119k domains) · look-alike · homoglyph · punycode ·
                       brand-in-domain · shortener · cheap TLD · unverified airdrop link
  account_signals.py   account age · impersonation · official domain handle ·
                       coordinated-link tracker (behavior blocklist)
  counter-signals      scam warning · "never share your seed phrase" · nothing to claim ·
                       reported speech / victim questions · satire
        ▼
   router.py  hard & uncontested → crypto-scam;  score ≥ threshold & airdrop context →
              unverified-airdrop;  else none
        ▼
   review_queue.py  Ozone-style JSONL (label events + account *referrals* for impersonation)
```

Key design choices, each tied to the policy:

- **Rules, not an LLM** (§3.5): every decision is explainable, deterministic and cheap.
  Scoring takes under 1 ms per post.
- **Counter-signals "contest" hard indicators.** The same words "send 1 ETH, get 2 back"
  produce a label in a scam and no label in a PSA quoting it (Example 7).
- **Scammer reassurance is a tell, not a warning.** "Not a scam! Beware of fakes, this is the
  only real one" adds suspicion instead of cancelling it.
- **The `unverified-airdrop` label requires airdrop context.** A post can't get a label whose
  name doesn't describe it ("be precise about what you call the labeler").
- **No account actions on automated signals** (§3.1): impersonation produces a *referral*
  entry in the review queue, never an account label.
- **Paid services left out:** Google Web Risk and an LLM classifier are not used. The free
  MetaMask list plus domain heuristics cover crypto phishing.

---

## Results (held-out test split, v2)

`data.csv` holds 340 posts: 172 synthetic and 168 real. Each source has its own dev/test
split. v2 was tuned on the dev splits only (see [ITERATIONS.md](ITERATIONS.md)).

| test set | system | accuracy | macro F1 | `crypto-scam` P | `crypto-scam` R | any-label P | any-label R |
|---|---|---|---|---|---|---|---|
| synthetic (113) | keyword baseline | 0.513 | 0.372 | 0.344 | 0.700 | 0.607 | 0.712 |
| synthetic (113) | v1.1 | 0.929 | 0.919 | 1.000 | 0.867 | 0.979 | 0.885 |
| synthetic (113) | **v2** | **0.938** | **0.936** | **1.000** | **0.867** | **0.941** | **0.923** |
| real (111) | keyword baseline | 0.324 | 0.238 | 0.123 | 1.000 | 0.395 | 0.889 |
| real (111) | v1.1 | 0.559 | 0.437 | 0.286 | 0.200 | 0.349 | 0.417 |
| real (111) | **v2** | **0.721** | **0.752** | **0.909** | **1.000** | **0.551** | **0.750** |

- **`crypto-scam` precision target (≥ 0.90):** met on both test sets.
- **Recall target (≥ 0.80):** met on synthetic data, not on real data (0.75).
- **Real scam recall is optimistic:** 8 of the 10 real test scams belong to one campaign whose
  dev posts shaped v2. Excluding it, real test accuracy is 0.699 and `crypto-scam` is 2/3
  precision, 2/2 recall.
- **Remaining real-data errors:** mostly `unverified-airdrop` on exchange news, casino promos
  and airdrop explainers. That is the cost of the lower review threshold; this tier only
  informs and never hides content.
- **Who labeled the real posts:** Claude, as a single AI annotator (`annotation_status =
  ai-annotated`), disclosed in [ANNOTATION.md](ANNOTATION.md). A human spot-check is
  recommended.

Reports are in `results/` (`eval_report_test_real.md`, `eval_report_test_synthetic.md`, and
the `dev` versions), with every error and the signals behind it. Earlier versions are frozen
in `results/v1-frozen/` and `results/v1.1-frozen/`. Reproduce them with:

```bash
python evaluate.py --split test --source real --show-errors
```

**Efficiency (offline):** loading the resources, including the 119k-domain blocklist, takes
about 75 ms and 15 MB. Scoring takes about 0.7 ms median and under 2 ms p95 per post, with zero
network calls. Live mode adds 2 Bluesky API calls per post (record and profile), plus up to 5
HEAD requests per shortened link (cached).

---

## Files

| Path | Description |
|---|---|
| `pylabel/policy_proposal_labeler.py` | **Required.** `PolicyProposalLabeler`, with the same constructor as the starter's `AutomatedLabeler`. Offers `moderate_post(url)` for live posts and `moderate_record(record)` for offline posts. |
| `pylabel/config.py` | Label definitions (with reason and appeal text), weights, thresholds, combo rules. |
| `pylabel/models.py` | `PostRecord`, `Signal` and `Decision` data classes. |
| `pylabel/resources.py` | Loads the reference lists in `labeler-inputs/`. |
| `pylabel/prefilter.py` | Text normalization (evasion handling) and the cheap prefilter. |
| `pylabel/text_signals.py` | Text detectors and counter-signal detectors. |
| `pylabel/link_signals.py` | URL extraction, shortener expansion, blocklist and look-alike checks. |
| `pylabel/account_signals.py` | Account age, impersonation, official handles, coordinated-link tracker. |
| `pylabel/router.py` | Two-tier routing rules. |
| `pylabel/review_queue.py` | Ozone-style review queue (JSONL). |
| `pylabel/ingest.py` | Builds `PostRecord`s from data.csv rows or the live Bluesky API. |
| `pylabel/label.py` | Course starter code (Bluesky/Ozone helpers), unchanged. |
| `labeler-inputs/` | Reference lists: crypto terms, urgency phrases, shorteners, suspicious TLDs, official project domains, impersonation targets, MetaMask blocklist/allowlist snapshot (fetched 2026-11-26). |
| `data.csv` | **Required.** 340 labeled posts (172 synthetic + 168 real). Schema is below. |
| `evaluate.py` | Offline evaluation: metrics, keyword baseline, ablations, per-category table, efficiency. |
| `run_labeler.py` | Live runner for post URLs (adapted from the starter's `test_labeler.py`). |
| `collect_posts.py` | Crawls Bluesky search for real candidate posts to annotate. |
| `tests/` | pytest suite: unit tests per module, router rules, policy Examples 1–7, metrics, and v2 regressions (`test_v2_changes.py`). |
| `results/` | Generated reports. `results/v1-frozen/` holds the first held-out run. |
| `annotation/` | Real Bluesky posts: all 584 candidates, the 168-post annotation sheet, Claude's draft labels (kept separate), and `merge_annotations.py` (Cohen's κ + merge into data.csv). |
| `ANNOTATION.md` | Annotation rubric and procedure. |
| `ITERATIONS.md` | What we changed and why (for the report and video). |
| `PLAN.md` | Original implementation plan. |
| `.env-TEMPLATE`, `.gitignore`, `requirements.txt` | Setup. |

### `data.csv` schema

| column | meaning |
|---|---|
| `id` | `p###` = synthetic, `r###` = real (collected) |
| `split` | `dev` (used for tuning, ~1/3 per label) or `test` (held out) |
| `source` | `synthetic` or `real` |
| `post_url` | bsky.app URL for real posts |
| `author_handle`, `author_display_name`, `author_created_at` | author info (account age = post time − created) |
| `post_created_at` | ISO time; evaluation processes posts in this order, like a stream |
| `text` | post text, frozen at collection time |
| `links` | JSON list of facet / link-card URLs |
| `expected_label` | `crypto-scam`, `unverified-airdrop` or `none` |
| `category` | stress-test bucket, e.g. `scam/evasion-homoglyph`, `none/warning` |
| `rationale` | why this label was assigned |
| `annotation_status` | `synthetic-by-design`, `ai-annotated` (real posts labeled by Claude), or `adjudicated` / `human-verified` |

### Updating the labeler

- To add an official project or impersonation target, edit `labeler-inputs/known_project_domains.csv`
  or `labeler-inputs/prominent_handles.csv`. No code changes are needed.
- To refresh the phishing blocklist, regenerate `labeler-inputs/metamask_blocklist.txt` from
  [eth-phishing-detect](https://github.com/MetaMask/eth-phishing-detect) `src/config.json`.
- To add a detector, write `detect_x(norm, record, resources) -> List[Signal]`, register it
  in `TEXT_DETECTORS`, add a weight in `config.WEIGHTS`, and add a test.
