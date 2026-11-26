# Evaluation report — split: `dev` (116 posts)

Gold label distribution: crypto-scam=22, unverified-airdrop=25, none=69

## Full labeler

Accuracy: **0.897**

| gold \ predicted | crypto-scam | unverified-airdrop | none |
|---|---|---|---|
| **crypto-scam** | 20 | 1 | 1 |
| **unverified-airdrop** | 0 | 21 | 4 |
| **none** | 0 | 6 | 63 |

| label | precision | recall | F1 | support |
|---|---|---|---|---|
| crypto-scam | 1.000 | 0.909 | 0.952 | 22 |
| unverified-airdrop | 0.750 | 0.840 | 0.792 | 25 |
| none | 0.926 | 0.913 | 0.920 | 69 |
| *any label (binary)* | 0.875 | 0.894 | 0.884 | 47 |

Policy targets (§3.3): `crypto-scam` precision ≥ 0.90 → **1.000** (met); recall proxy (any label on harmful posts) ≥ 0.80 → **0.894** (met).

## Baseline and ablations

Keyword baseline = label every post containing a crypto-promotion keyword (the 'blocking crypto keywords' alternative rejected in policy §3.5).

| system | accuracy | macro F1 | scam P | scam R | any-label P | any-label R |
|---|---|---|---|---|---|---|
| keyword baseline | 0.440 | 0.322 | 0.233 | 0.773 | 0.521 | 0.809 |
| text only | 0.681 | 0.591 | 0.529 | 0.409 | 0.697 | 0.489 |
| text + counter | 0.759 | 0.658 | 1.000 | 0.409 | 0.958 | 0.489 |
| text + counter + link | 0.879 | 0.865 | 1.000 | 0.864 | 0.872 | 0.872 |
| + account | 0.897 | 0.888 | 1.000 | 0.909 | 0.875 | 0.894 |
| full (+ behavior) | 0.897 | 0.888 | 1.000 | 0.909 | 0.875 | 0.894 |

## Accuracy by category

| category | n | correct | accuracy | mistakes (gold→pred) |
|---|---|---|---|---|
| none/airdrop-discussion | 4 | 4 | 1.00 |  |
| none/ambiguous-terms | 4 | 4 | 1.00 |  |
| none/crypto-talk | 4 | 4 | 1.00 |  |
| none/hard-negative | 1 | 1 | 1.00 |  |
| none/legit-airdrop | 2 | 2 | 1.00 |  |
| none/links | 2 | 2 | 1.00 |  |
| none/new-account | 2 | 2 | 1.00 |  |
| none/non-crypto-giveaway | 4 | 4 | 1.00 |  |
| none/satire | 1 | 1 | 1.00 |  |
| none/victim-question | 2 | 2 | 1.00 |  |
| none/warning | 5 | 5 | 1.00 |  |
| real/crypto-scam | 6 | 6 | 1.00 |  |
| real/none | 38 | 32 | 0.84 | r214: none→unverified-airdrop, r561: none→unverified-airdrop, r556: none→unverified-airdrop, r023: none→unverified-airdrop, r054: none→unverified-airdrop, r005: none→unverified-airdrop |
| real/unverified-airdrop | 13 | 9 | 0.69 | r200: unverified-airdrop→none, r189: unverified-airdrop→none, r405: unverified-airdrop→none, r125: unverified-airdrop→none |
| review/connect-urgency | 4 | 4 | 1.00 |  |
| review/coordinated | 2 | 2 | 1.00 |  |
| review/high-return | 1 | 1 | 1.00 |  |
| review/new-account-giveaway | 2 | 2 | 1.00 |  |
| review/telegram | 1 | 1 | 1.00 |  |
| review/unofficial-claim | 1 | 1 | 1.00 |  |
| review/wallet-farming | 1 | 1 | 1.00 |  |
| scam/blocklisted-domain | 2 | 2 | 1.00 |  |
| scam/credential | 1 | 1 | 1.00 |  |
| scam/evasion-homoglyph | 1 | 1 | 1.00 |  |
| scam/evasion-leet | 1 | 1 | 1.00 |  |
| scam/evasion-obfuscated-link | 1 | 1 | 1.00 |  |
| scam/evasion-paraphrase | 1 | 0 | 0.00 | p019: crypto-scam→none |
| scam/impersonation | 3 | 2 | 0.67 | p046: crypto-scam→unverified-airdrop |
| scam/lookalike-domain | 1 | 1 | 1.00 |  |
| scam/send-to-receive | 3 | 3 | 1.00 |  |
| scam/upfront-fee | 2 | 2 | 1.00 |  |

## Efficiency (offline mode)

- Resource load (incl. 119,002-domain MetaMask blocklist): 309 ms, peak 20.0 MB
- Per-post latency: mean 0.806 ms, median 0.634 ms, p95 1.609 ms, max 1.870 ms
- Extra peak memory while scoring all posts: 12401 KB
- Network calls: 0 (live mode adds 2 API calls per post + up to 5 HEAD requests per shortened link)
- Posts dropped by prefilter: 7/116
- Behavior blocklist at end of stream: ['eth-drop.claims/go']

