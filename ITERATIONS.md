# Iteration log

This log records how the implementation evolved and where it departs from the Assignment 2
proposal. It's meant as material for the report and video ("what we had to go back on").

## Departures from the proposal

| Proposal | Implementation | Why |
|---|---|---|
| Ingest from Jetstream (§3.2 step 1) | CSV (`data.csv`) offline; live posts by URL via `run_labeler.py` | The assignment specifies CSV input, and graders must be able to reproduce results without network access. The `PostRecord` interface means a Jetstream consumer would plug in unchanged. |
| Google Web Risk for links (§3.2 3b) | Not used | Web Risk is a paid API. The MetaMask eth-phishing-detect list (free, 119k crypto phishing domains) plus look-alike, homoglyph and brand-in-domain heuristics replace it for crypto specifically. |
| Domain-age check (§3.2 3b) | Not used | WHOIS/RDAP lookups are slow, rate-limited and unreliable. Account age is used instead, and `suspicious_tld` is a weak proxy for throwaway domains. |
| Human review in Ozone (§3.2 4b) | `review_queue.jsonl` entries that mirror Ozone `emitEvent` payloads | Running Ozone needs a hosted service. The entries can be replayed into Ozone unchanged. |
| "Hard indicators → crypto-scam" | Hard indicators are **contested** by counter-signals | The first sketch labeled scam warnings that quote scam text (Example 7). See v0 below. |
| Two tiers only | Two tiers, plus the rule that `unverified-airdrop` requires airdrop context | Otherwise a new account posting a crypto link with no giveaway could get an "airdrop" label it doesn't deserve. |

## v0: smoke test on the proposal's examples

- Example 2 ("Claim free tokens by **entering** your wallet recovery phrase") was missed,
  because the verb list only had base forms. **Fix:** the credential-request verbs now
  accept inflections.
- Uniswap's own account (`@uniswap.org`) was flagged as *impersonating* Uniswap. **Fix:** a
  project's own domain handle is exempt from impersonation and gets a
  `verified_project_source` counter-signal. This implements the policy's domain-handle nudge
  (§3.4).
- Leetspeak folding first turned `$eth` into `seth` and `now!!` into `nowii`. **Fix:**
  cashtags and @mentions are left alone, and `!` is no longer treated as leetspeak.

## v1: tuned on the dev split only (59 posts)

The first dev run scored accuracy 0.831 and `crypto-scam` precision 1.000 / recall 0.688.
These changes came from **dev errors only**:

| Dev error | Change |
|---|---|
| `3ton-airdrop.pages.dev` (blocklisted) not detected | Bug: bare domains starting with a digit were skipped. Removed that condition. |
| `arbitrum-claims[.]xyz` + "connect your wallet" only reached `unverified-airdrop` | Brand-in-domain plus **any** call to action is now a hard combo, because a counterfeit claim site needs no "giveaway" wording. |
| "giving every user 50 USDT" not recognized as a giveaway | Added `giving`/`gifting` to the offer verbs. |
| "Arbitrum round 2 claim is open" | Added "claim(s) is/are open/live" as a call to action. |
| Airdrop posts linking to unknown sites scored too low | New signal `unverified_airdrop_link` (proposal Example 4, "unverified airdrop link"). |

After these changes the dev split scored accuracy 0.898 and `crypto-scam` P 1.000 / R 0.875.
**The weights were then frozen.**

**First held-out test run** (frozen copy in `results/v1-frozen/`): accuracy **0.920**,
`crypto-scam` P **1.000** / R **0.833**, any-label recall 0.865.

## v1.1: bug fix found in the test run (disclosed)

Test error `p035` (`opensea.support`, which is on the MetaMask list) was missed because
`.support` wasn't in the hard-coded list of TLDs used to spot bare domains in text. This is
a coverage **bug**, not a threshold choice. The fix derives the recognized TLDs from every
domain in the blocklist and reference lists (542 TLDs), minus file-extension-like ones such
as `.md` and `.sh`. No weights changed.

Test after the fix: accuracy **0.929**, `crypto-scam` P **1.000** / R **0.867**, any-label
recall **0.885**. We report both numbers. v1 is the clean held-out number, and v1.1 is the
current code.

## Remaining errors (test, v1.1) and what they teach us

| Post | Gold → predicted | Why it was missed | Possible next step |
|---|---|---|---|
| p005 "Send any amount of SOL to 7xKX… receive 3x back" | scam → none | No numeric amount, and the Solana address format isn't recognized, so the crypto-context check failed. | Add Solana base58 addresses when "SOL" is nearby, and accept "any amount". |
| p008 "Send 0.05 ETH for gas and we'll send your 2 ETH prize" | scam → none | "send your prize" isn't a return verb, and "for gas" isn't the word "fee". | Treat "for gas" as a fee, and match "send … send your" patterns. |
| p009 "You send 1, I send 2" | scam → none | Paraphrase with no coin next to the amounts. | Expected limitation of rules. This is a candidate for the deferred LLM tier on medium-score posts. |
| p045 image-only scam | scam → review | Scam text is in the image. | OCR on images (policy §3.6 already lists it). |
| p054, p069, p072 low-signal promotions | review → none | Score 2.5, just under the threshold of 3.0. | Calibrate the threshold on more real data. Lowering it to 2.5 trades precision for recall. |
| p170 moderator note quoting Example 5 | none → review | The quote has no warning words ("being reviewed", "don't engage"). | Detect quotation marks around scam text, and add moderator/report vocabulary. |

## v1.1 on real data (2026-11-26)

We collected 584 real posts with `collect_posts.py` (16 search queries). 168 of them were
labeled by Claude as a single AI annotator (see the disclosure in ANNOTATION.md): everything
the labeler flagged, 6 random unflagged posts per query, and a 13-post coordinated campaign.
They were merged into `data.csv` with their own dev/test split. **The labeler was not changed
after seeing these posts**, so these are clean held-out numbers for v1.1.

| real test (111 posts) | accuracy | scam P | scam R | any-label P | any-label R |
|---|---|---|---|---|---|
| keyword baseline | 0.324 | 0.123 | 1.000 | 0.395 | 0.889 |
| text only | 0.613 | 0.125 | 0.100 | 0.250 | 0.083 |
| + counter-signals | 0.640 | 0.167 | 0.100 | 0.333 | 0.083 |
| + links | **0.721** | 0.286 | 0.200 | 0.619 | 0.361 |
| + accounts | 0.559 | 0.286 | 0.200 | 0.349 | 0.417 |
| full (+ behavior) | 0.559 | 0.286 | 0.200 | 0.349 | 0.417 |

Compared with the synthetic test set (accuracy 0.929, scam precision 1.000), this is a large
drop. Synthetic posts written alongside the rules overstate performance.

**Failure modes found on real posts:**

- **Testnet faucet guides** (8 posts from one account, plus a related Discord-faucet post): "Click 'Send me ETH' … to
  receive faucet tokens" fires `send_to_receive`. Faucets are the legitimate inverse of the scam.
- **News and commentary about scams**: "a deepfake Elon promised to double your crypto".
  `deepfake` isn't a warning word, and news framing isn't detected.
- **"no seed phrase required"**: "no" is missing from the negation list.
- **Satire**: "Paying $45 in gas fees to claim an $8 airdrop" is read as an upfront fee.
- **A coordinated campaign from old accounts** (8 of the 10 missed real scams): 13 accounts
  created between 2024 and 2025 posted identical "1 BTC giveaway 👉 insurance-kalshi.com" text.
  The coordinated-link tracker only counts *new* accounts, and "kalshi" isn't in the brand list.
- **Account-age signals hurt on real data** (0.721 → 0.559): many legitimate real posters,
  such as bots, newsletters and newly migrated users, have accounts under 30 days old, so
  `new_account` pushes ordinary crypto promotion over the threshold.
- **Airdrop-farming guides** ("connect wallet → claim faucet → trade daily") make up most real
  `unverified-airdrop` traffic and are flagged inconsistently.

**Next steps (v2, to be tuned on the real *dev* split only):**

1. Count identical text and links across *any* accounts within a time window, not only new
   accounts.
2. Add news and reporting framing (`deepfake`, `reportedly`, a headline plus a news domain)
   as a contesting counter-signal.
3. Add "no … required" to the negation list, and an exemption for faucet language (a "Send
   me ETH" button, testnet).
4. Make account age only *amplify* other signals instead of adding score on its own.
5. Have a human spot-check the AI annotations and report the agreement rate.

## v2: tuned on the real dev split (2026-11-26)

v1.1 reports are frozen in `results/v1.1-frozen/`. Every v2 change is justified by **dev**
posts, cited inline in the code with comments marked `v2:`. Unit tests in
`tests/test_v2_changes.py` reproduce each motivating pattern.

| Dev evidence | Change |
|---|---|
| r250, r253, r257: faucet guides → `crypto-scam` | `faucet_context` counter-signal (contesting), only when no airdrop or reward is promised |
| r273: "deepfake Elon's promise to double your crypto — AMBCrypto" | `deepfake` added to the warning words; new `news_framing` counter (−2) |
| r035: "Paying $45 in gas fees to claim an $8 airdrop" | Upfront-fee rule skips first-person descriptions (paying/paid/spent) |
| r130: "spot the scam" answer quoting several indicators | Contested posts need +3 extra score for `unverified-airdrop` |
| r001, r214, r271, r556, r561: new account plus a vague mention | Account age only *amplifies* posts with a concrete risk signal |
| r215–r227: identical "1 BTC giveaway" posts from old accounts | Tracker also flags identical text + link from ≥3 accounts of any age within 48 h |
| same posts, and r174 "2x crypto giveaway" | Kalshi, Polymarket and Robinhood added to the brand list; "2x/double … giveaway" added as a money-flip phrase |
| synthetic dev p050, p056: first faucet rule hid "testnet rewards" farming | Faucet rule narrowed (above) |
| synthetic dev p059, p065: "Reply with your ETH address" | Public address requests count as a call to action |
| Threshold sweep on both dev splits (2.0 / 2.5 / 3.0 / 3.5) | `MEDIUM_THRESHOLD` 3.0 → 2.0. Real dev accuracy 0.807 → 0.825 and any-label recall 0.47 → 0.79; precision falls 0.90 → 0.71, which is acceptable for an inform-only tier. |

Considered but **not** applied, because only test posts motivated them: "no seed phrase
required" negation (r311), and same-author repetition (r189/r200 is in dev but has one
author, so Example 4's "multiple accounts" doesn't apply).

### v2 held-out results

| test split | version | accuracy | macro F1 | scam P | scam R | any-label P | any-label R |
|---|---|---|---|---|---|---|---|
| real (111) | v1.1 | 0.559 | 0.437 | 0.286 | 0.200 | 0.349 | 0.417 |
| real (111) | **v2** | **0.721** | **0.752** | **0.909** | **1.000** | **0.551** | **0.750** |
| real, excl. Kalshi campaign (103) | **v2** | 0.699 | 0.702 | 0.667 | 1.000 | 0.463 | 0.679 |
| synthetic (113) | v1.1 | 0.929 | 0.919 | 1.000 | 0.867 | 0.979 | 0.885 |
| synthetic (113) | **v2** | **0.938** | **0.936** | **1.000** | **0.867** | **0.941** | **0.923** |

**Honesty notes:**

- **The real test set isn't perfectly blind.** We looked at real test errors (in the v1.1
  analysis) before designing v2, and only dev-motivated changes were applied.
- **8 of the 10 real test scams are the same Kalshi campaign** whose dev posts motivated the
  brand-list and campaign-tracker fixes. Real scam recall of 1.00 is therefore optimistic,
  and the "excl. Kalshi" row is the fairer view. On it, `crypto-scam` precision is 2 of 3
  (one false positive, r311 "no seed phrase required") and recall is 2 of 2.
- **The real-data labels come from a single AI annotator** (see ANNOTATION.md).

**What v2 fixed and what it didn't:**

- `crypto-scam` precision on real data rose from 0.29 to 0.91, and the scam false positives
  from faucets, deepfake news and gas-fee satire are gone. Synthetic results also improved
  slightly, with no regression.
- The policy's §3.3 recall target (≥ 0.80) is met on synthetic data but not real (0.75).
- **New trade-off:** 21 real `none` posts now get `unverified-airdrop`. These are exchange
  campaign news, casino promos, AI-token referral codes, airdrop explainers and gas bots.
  This is the cost of the lower threshold. The review queue absorbs it; it never hides
  content.
- Account signals still slightly hurt on real data (0.739 → 0.721 in the ablation).
  Removing them entirely is the next experiment.
- **Efficiency:** about 0.7 ms per post (median), slower than v1 because of the campaign
  tracker's text normalization, and still with zero network calls offline.

### Next steps after v2

1. Add a news/promo-source allowlist (exchange news accounts) and casino/gambling exclusion.
2. Add "no … required" to the negation list, and test it on fresh data.
3. Run a human spot-check of the AI annotations, then collect a *fresh* real test set (new
   search date) to get an uncontaminated number.
4. Cluster same-author repetition (r189/r200 "Little Pepe") as a weaker spam signal.

## Ablations (synthetic test split)

| system | accuracy | scam P | scam R | any-label R |
|---|---|---|---|---|
| keyword baseline | 0.513 | 0.344 | 0.700 | 0.712 |
| text only | 0.690 | 0.714 | 0.500 | 0.500 |
| + counter-signals | 0.743 | 1.000 | 0.500 | 0.500 |
| + links | 0.876 | 1.000 | 0.767 | 0.788 |
| + accounts | 0.929 | 1.000 | 0.867 | 0.885 |
| + behavior (full) | 0.929 | 1.000 | 0.867 | 0.885 |

- Counter-signals are what make scam precision perfect: they remove every warning,
  victim-question and satire false positive.
- Link and account signals bring most of the recall.
- The behavior tracker adds nothing measurable here, because the campaign posts it catches
  already had other signals. Its value is against campaigns whose text is innocuous, which
  this dataset barely covers. A future test could add a larger campaign with bland text.
