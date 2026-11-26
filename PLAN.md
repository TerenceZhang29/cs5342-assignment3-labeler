# Implementation Plan — Crypto Giveaway/Airdrop Scam Labeler (CS 5342 A3)

**Group 8:** Terence Zhang, Lucas Sumartha, Ziqiao Gao, Lillian (Xintong) Li

Goal: implement the Assignment 2 policy ("Fraudulent Cryptocurrency Giveaway and Airdrop
Promotions on Bluesky") as a two-tier Bluesky labeler, plus a reproducible evaluation on
~150–200 hand-annotated posts.

---

## 1. What the policy says → what the code must do

| Policy element (proposal §) | Implementation |
|---|---|
| Two-tier labels (§3.1) | `crypto-scam` (hard indicators, warn/hide + queue for takedown) and `unverified-airdrop` (medium score, stays visible, queued for review). Otherwise no label. |
| Prefilter (§3.2 step 2) | Keep posts that contain a link **or** crypto terms (airdrop, giveaway, ETH, BTC, SOL, wallet, claim, token, seed phrase, …). Everything else returns `[]` immediately (cheap path). |
| Text signals (§3.2 3a) | Send-to-receive / "double your" promises, recovery-phrase / private-key requests, upfront-fee requests, urgency cues, claim CTAs, wallet-connect requests, raw wallet addresses. |
| Link signals (§3.2 3b) | Shortener expansion, MetaMask `eth-phishing-detect` blocklist (local snapshot), look-alike domains vs. known project domains (edit distance + homoglyph/punycode), suspicious TLDs. Domain age is optional (see §6). |
| Account signals (§3.2 3c) | Account age, handle similarity to prominent accounts / projects (impersonation), domain-handle vs `*.bsky.social` (nudge in §3.4), identical links across accounts. |
| Behavior-level blocklist (§3.1) | In-memory/persisted map `link → {distinct authors}`; once a claim link is posted by ≥N new accounts it joins a dynamic blocklist and later posts with it are auto-labeled. |
| Allowed content (§1, Ex. 6–7) | Counter-signals: scam warnings/education ("never share your seed phrase", "PSA", "this is a scam"), negation, reported speech, "nothing to claim". These dampen the score so warnings are **not** labeled. |
| "Every label states its reason" (§3.7) | Each decision carries a list of fired signals → human-readable reason string, logged and attached to review-queue entries. |
| Human review in Ozone (§3.2 4b) | Local `review_queue.jsonl` mirroring Ozone's `tools.ozone.moderation.emitEvent` shape (subject, label, reasons, score). Real Ozone deployment is out of scope (it's a hosted service). |
| "No account banned on automated signals" (§3.1) | Labeler only labels posts; account-level output is a *referral* entry in the review queue, never an account label. |
| Thresholds unpublished (§3.6) | Weights/thresholds live in a config file; the report describes the method, not exact values. |

## 2. Architecture

```
data.csv / live post URL / (optional) Jetstream
        │
        ▼
 PostRecord (text, links, facets, author handle/DID, account createdAt, embeds)
        │
   prefilter ──no──► []
        │yes
        ▼
 ┌─────────────┬──────────────┬────────────────┐
 │ TextSignals │ LinkSignals  │ AccountSignals │   each returns [Signal(name, weight, hard?, evidence)]
 └─────────────┴──────────────┴────────────────┘
        │
   counter-signals (warning / negation / satire) → dampen
        ▼
   router: hard indicator + crypto context → crypto-scam
           score ≥ T_medium                 → unverified-airdrop (+ review queue)
           else                             → []
        ▼
   Decision(labels, score, reasons) → label_post() (starter label.py, only with --emit)
```

Scoring is a transparent weighted rule system (explainable on appeal, per §3.5), not an LLM.

## 3. Starter code and files to create

**Starter code** (`cornelltech/cs5342-spring2025/bluesky-assign3`): reviewed and it's small and
clean, so we **reuse it**:
- **Keep as-is:** `pylabel/label.py` (`post_from_url`, `label_post`, `label_account`,
  `did_from_handle`), `.env-TEMPLATE` (`USERNAME`, `PW`), `.gitignore`.
- **Keep the pattern:** `test_labeler.py`'s CSV-of-URLs → `moderate_post` → optional
  `--emit_labels` loop. Our `run_labeler.py` reuses this for the live path.
- **Drop:** Part 0 files (`automated_labeler.py`, `labeler-inputs/`, `test-data/`, dog images,
  `get_post_test.py`). They're optional and ungraded, and we're not doing Part 0.
- **Fix:** the starter has no `requirements.txt`, so we add one (`atproto`, `python-dotenv`,
  `pandas`, `requests`, `pytest`). The starter logs in unconditionally; our offline
  evaluation must **not** need credentials, so login only happens on the live path.

All new code goes in the starter's `pylabel/` package so imports match the starter README.

| File | Purpose | Team owner (per proposal) |
|---|---|---|
| `pylabel/policy_proposal_labeler.py` | **Required.** `PolicyProposalLabeler(client, input_dir)` (same constructor signature as the starter) with `moderate_post(url) -> List[str]` (live, fetches via atproto) and `moderate_record(record) -> Decision` (offline, used for eval). Thin orchestration only. | Terence |
| `pylabel/ingest.py` | Fetch a post by URL via atproto (`post_from_url`, `get_profile`), extract text, facet links, external-embed URIs, author createdAt; CSV row → `PostRecord`. | Ziqiao |
| `pylabel/prefilter.py` | Text normalization (lowercase, NFKC, strip zero-width chars, leetspeak/homoglyph folding) + crypto-term / link prefilter. | Ziqiao |
| `pylabel/text_signals.py` | Regex/phrase detectors for each text indicator + counter-signal detectors. | Lillian |
| `pylabel/link_signals.py` | URL extraction, shortener expansion (cached, `HEAD` only, never renders page; off in offline mode), blocklist lookup, look-alike detection. | Lillian |
| `pylabel/account_signals.py` | Account age, impersonation similarity, domain-handle check, cross-account link tracker / dynamic blocklist. | Lillian / Terence |
| `pylabel/router.py` | Score aggregation, counter-signal dampening, tier routing, reason strings. | Terence |
| `pylabel/review_queue.py` | Writes Ozone-style JSONL entries for medium-tier posts and account referrals. | Terence |
| `pylabel/config.py` | Weights, thresholds, label definitions (identifier, severity, blurb with appeal note). | Terence |
| `labeler-inputs/` | `crypto_terms.txt`, `urgency_phrases.txt`, `shorteners.txt`, `known_project_domains.csv`, `prominent_handles.csv`, `metamask_blocklist.json` (snapshot + date), `suspicious_tlds.txt`. Passed as `input_dir`, like the starter. | Lillian |
| `collect_posts.py` | Crawl Bluesky search (`app.bsky.feed.searchPosts`) for queries like "airdrop", "giveaway eth", "seed phrase", "send eth receive", "claim tokens"; dump candidates for annotation. Run once; output frozen into `data.csv`. | Ziqiao / Lucas |
| `data.csv` | **Required.** Final annotated dataset (schema in §4). | Lucas |
| `evaluate.py` | Runs labeler over `data.csv` **offline, no login**; prints/saves confusion matrix, accuracy, per-label precision/recall/F1, baseline, ablations, latency, memory. | Lucas |
| `run_labeler.py` | Live path adapted from starter `test_labeler.py`: CSV of post URLs → `moderate_post` → optional `--emit_labels`. | Terence |
| `tests/` | pytest unit tests per signal module + router + regression tests for proposal Examples 1–7. | all |
| `README.md` | Group 8 + names, file list, setup, how to run tests/eval/live/emit. | all |

## 4. Dataset (`data.csv`)

Target ~180 posts, roughly: 40 `crypto-scam`, 40 `unverified-airdrop`, 100 `none`
(deliberately heavy on hard negatives).

Columns:
`id, source (real|synthetic), post_uri, author_handle, author_created_at, text, links, expected_label, category, annotator_a, annotator_b, notes`

Composition (stress-test buckets, tracked in `category`):
- **Scam (real + synthetic):** send-to-receive, seed-phrase request, upfront/verification fee, celebrity/project impersonation, look-alike domains, blocklisted domains.
- **Needs-review:** connect-wallet + urgency, unverified airdrop links, same link from multiple new accounts.
- **Hard negatives:** scam warnings/PSAs (Ex. 7), airdrop news/discussion (Ex. 6), legit airdrops from domain handles, non-crypto giveaways (books, art), "ETH" ≠ Ethereum (ETH Zürich, Ethernet), satire/memes, crypto price talk.
- **Evasion red-team (§3 Anticipate):** misspellings/leetspeak (`a1rdr0p`, `s33d phrase`), zero-width chars, Unicode homoglyphs, URL shorteners, punycode domains, text split across emoji.

Ground truth: two annotators label independently using a rubric built from the proposal's
Example table (Violation → `crypto-scam`, Needs Review → `unverified-airdrop`, Allowed → none);
report Cohen's κ; disagreements resolved by discussion and logged in `notes`.
Real posts: public posts only, store URI + text; no DMs; **never open scam links in a browser** —
record domains only. Avoid illegal/severe content per course policy.

Split: 30% dev (used to tune weights/thresholds), 70% held-out test (reported numbers) to avoid
overfitting the rules to the eval set.

## 5. Evaluation (`evaluate.py`)

- 3-class confusion matrix; accuracy; per-label precision/recall/F1; also binary "any label vs none".
- Map to proposal metrics: `crypto-scam` precision target ≥90%, recall proxy ≥80%.
- **Baseline comparison:** keyword-only rule (proposal §3.5 "blocking crypto keywords") to show it
  false-positives on warnings — supports the policy argument.
- **Ablations:** text only → +links → +accounts → +counter-signals.
- **Per-category breakdown** (which stress buckets fail) and a dump of every FP/FN with reasons.
- **Efficiency:** per-post latency (mean/p50/p95, `time.perf_counter`), peak memory (`tracemalloc`),
  network calls per post (counted in ingest/link modules), prefilter pass rate. Offline mode = 0
  network calls; live mode measured separately.
- Optional stress test: emit ~150 labels to the course labeler account (only with `--emit`).

## 6. Things that cost money or need decisions (CLAUDE.md cost rule)

- **Google Web Risk** (proposal §3.2b): paid per lookup beyond the free tier. Plan: **leave it out**,
  use the free MetaMask blocklist snapshot + look-alike heuristics; leave a pluggable stub.
- **LLM classifier:** proposal defers it — not used.
- **Domain age (WHOIS/RDAP):** free but flaky/rate-limited; plan: optional, cached, off in eval
  (value pre-recorded in `data.csv` where known).
- **Bluesky API:** free; needs a Bluesky account + app password in `.env` (never committed).
  Only `collect_posts.py` and `run_labeler.py` need it.
- **Emitting labels:** free, but publishes to the network — only run with explicit `--emit_labels`.
- **Jetstream live consumer:** dropped from the required scope (see §6a); optional stretch goal.

## 6a. Is live-data testing required? No.

- The spec says test posts "can be from real posts online or synthetic posts", and that the
  labeler ingests posts **from a CSV file** for this assignment.
- Our labeler is a classifier, so the rubric asks for accuracy/precision/recall on a ground-truth
  set. The "emit ~150 labels" stress test applies only to solutions that *aren't*
  classification-oriented.
- "Demo in real time" in the video means running our tests/eval live on screen, not running on the
  live firehose.
- Graders must reproduce our results, which a frozen offline `data.csv` makes easy. Real posts can
  be deleted, so we store their text at collection time.

**So:** the primary evaluation is offline on `data.csv`. Real posts collected once via the API are
mixed in (stronger than purely synthetic data, and the spec says to gather data on the harm), but
grading never depends on network access. `moderate_post(url)` still works live for the video demo.

## 7. Build order

1. Copy reusable starter files (`pylabel/label.py`, `.env-TEMPLATE`, `.gitignore`) into the repo;
   add `requirements.txt`; set up venv.
2. `config.py`, `prefilter.py`, `text_signals.py` + unit tests from proposal Examples 1–7.
3. `link_signals.py` (+ MetaMask snapshot, look-alike detection) + tests.
4. `account_signals.py` + cross-account tracker + tests.
5. `router.py`, `review_queue.py`, `policy_proposal_labeler.py` (offline path first).
6. `ingest.py` (atproto fetch) → `moderate_post(url)` working with `run_labeler.py`.
7. `collect_posts.py` → candidate pool → annotate → `data.csv` (+ synthetic stress posts).
8. `evaluate.py`; tune on dev split, freeze, report on test split; write iteration log
   (`ITERATIONS.md`) for the video/report ("what we had to go back on").
9. `README.md`. Stretch only: Jetstream live demo for the "time to label" metric.
