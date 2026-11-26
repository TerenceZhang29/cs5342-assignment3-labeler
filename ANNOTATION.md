# Annotation rubric

The ground truth in `data.csv` follows the enforcement examples in our policy proposal (§1.1).
Annotators label each post with exactly one value.

| Label | Apply when | Policy examples |
|---|---|---|
| `crypto-scam` | The post **solicits** something that only a scammer needs: crypto sent first in exchange for more back, a seed/recovery phrase or private key, an upfront fee to unlock a reward, or a visit to a counterfeit or known-phishing claim site. Impersonating a public figure or project while running a giveaway with a call to action also counts. | 1, 2, 3 |
| `unverified-airdrop` | The post **promotes** a crypto airdrop/giveaway and asks the reader to act (connect a wallet, claim, check eligibility, click, DM, post an address), but nothing proves deception. Also applies when the same link is spread by several new accounts. | 4, 5 |
| `none` | Everything else: scam warnings and education (even when they quote scam text), news and discussion about airdrops, legit announcements from a project's own domain handle, disclosed promotions, tip jars and donations, satire, victims asking for help, and non-crypto giveaways. | 6, 7 |

Decision rules for tricky cases:

1. **Judge the speaker's intent, not the vocabulary.** A post quoting "send 1 ETH get 2 back"
   in order to warn people is `none`.
2. **Victims and questions are `none`.** For example: "Got a DM saying I won, is this a scam?"
3. **A project's own domain handle** (e.g. `@uniswap.org`) linking to its own domain is `none`,
   even with "claim now" wording.
4. **Image-only posts:** label from the image if you can see it, and note it in `rationale`.
5. **When unsure between `crypto-scam` and `unverified-airdrop`, choose `unverified-airdrop`.**
   The policy reserves the strong label for clear fraud.

## Files in `annotation/`

| File | Purpose |
|---|---|
| `all_candidates.csv` | All 584 unique posts returned by `collect_posts.py` (16 queries, collected 2026-11-26). |
| `real_posts_to_annotate.csv` | **The annotation sheet: 168 posts.** It contains every post the v1.1 labeler flagged (64), a random sample of 6 unflagged posts per query (96, seed 5342), and all 13 posts of the "1 BTC giveaway / insurance-kalshi.com" campaign. Annotators fill `annotator_a` / `annotator_b`. The sheet shows neither the labeler's output nor any draft label. |
| `draft_labels_claude.csv` | Claude's draft label and rationale for each post, plus the labeler's prediction. **Annotators should not open it until both have finished.** It's a third opinion for adjudication, not ground truth. |
| `merge_annotations.py` | Prints Cohen's κ and disagreements (`--check`), then appends adjudicated posts to `data.csv` (`--write`). |

Because the sheet over-samples flagged posts, metrics on it describe labeler behaviour on
scam-adjacent search results. They are not platform-wide prevalence.

## How the 168 real posts were actually labeled (disclosure)

The two-human procedure below was the original plan. To save time, the team instead asked
**Claude (an AI assistant) to annotate the real posts as a single annotator**:

1. Claude first drafted labels from truncated previews.
2. Claude then re-read every post in full (text, links, account age) and changed 4 labels
   (r174 → `crypto-scam`; r398, r399 → `none`; r578 → `unverified-airdrop`).
3. Final labels and rationales are in `annotation/draft_labels_claude.csv`, and in the
   sheet's `annotator_a` / `notes` columns. They were merged into `data.csv` with
   `annotation_status = ai-annotated`.

One extra consistency rule was applied: testnet/faucet guides that link to the project's own
domain and promise no real rewards are `none`. Farming promotions that promise token rewards
through shortened or referral links are `unverified-airdrop`.

**Limitations:** there is no second annotator, so no inter-annotator agreement (κ) can be
reported. The labels may also share blind spots with the rules, since the same assistant
helped write both. Recommended mitigation: a team member spot-checks a random 20–30 posts
(plus all 16 `crypto-scam` posts), and the agreement rate is reported. If they change a label,
edit `data.csv` and set `annotation_status = human-verified`.

## Procedure for real posts (collected with `collect_posts.py`)

1. Two team members label every candidate **independently**, without seeing each other's labels.
2. Compute Cohen's κ on the two label sets and report it.
3. Disagreements are discussed and resolved against this rubric. The final label goes in
   `expected_label`, with `annotation_status = adjudicated` and the reason in `rationale`.
4. Assign `split` before looking at the labeler's output: every third post per label goes to
   `dev`, the rest to `test`.
5. **Safety (course policy):** never open the linked sites. Judge from the post text, the
   domain name and the author's profile only. Skip anything illegal or severely harmful.

## Synthetic posts (`annotation_status = synthetic-by-design`)

The 172 synthetic posts were written to cover the policy examples and to stress-test the
labeler. Their categories are:

- **Scams:** send-to-receive, credential requests, upfront fees, impersonation, blocklisted
  domains, look-alike domains.
- **Evasion:** leetspeak, homoglyphs, letter spacing, `[.]` obfuscation, paraphrase, and
  image-only text.
- **Hard negatives:** warnings, discussion, legit airdrops, ambiguous words (ETH Zürich,
  eth0, Sol LeWitt, insurance claims, Minecraft seeds), satire, tip jars, and new accounts.

Each post's label was assigned by design from this rubric, and the `rationale` column explains
it. Some posts were **intentionally written to be hard for the labeler** (for example
`scam/evasion-paraphrase` and `scam/image-only`), so that the evaluation measures limits
instead of only confirming the rules. Because the same people wrote the rules and the
synthetic posts, results on synthetic data are optimistic. The real-post annotation above is
the more honest test.
