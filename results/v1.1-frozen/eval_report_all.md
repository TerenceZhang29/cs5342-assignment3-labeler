# Evaluation report — split: `all` (172 posts)

Gold label distribution: crypto-scam=46, unverified-airdrop=34, none=92

## Full labeler

Accuracy: **0.919**

| gold \ predicted | crypto-scam | unverified-airdrop | none |
|---|---|---|---|
| **crypto-scam** | 40 | 2 | 4 |
| **unverified-airdrop** | 0 | 27 | 7 |
| **none** | 0 | 1 | 91 |

| label | precision | recall | F1 | support |
|---|---|---|---|---|
| crypto-scam | 1.000 | 0.870 | 0.930 | 46 |
| unverified-airdrop | 0.900 | 0.794 | 0.844 | 34 |
| none | 0.892 | 0.989 | 0.938 | 92 |
| *any label (binary)* | 0.986 | 0.863 | 0.920 | 80 |

Policy targets (§3.3): `crypto-scam` precision ≥ 0.90 → **1.000** (met); recall proxy (any label on harmful posts) ≥ 0.80 → **0.863** (met).

## Baseline and ablations

Keyword baseline = label every post containing a crypto-promotion keyword (the 'blocking crypto keywords' alternative rejected in policy §3.5).

| system | accuracy | macro F1 | scam P | scam R | any-label P | any-label R |
|---|---|---|---|---|---|---|
| keyword baseline | 0.512 | 0.372 | 0.344 | 0.696 | 0.613 | 0.713 |
| text only | 0.692 | 0.625 | 0.742 | 0.500 | 0.812 | 0.487 |
| text + counter | 0.738 | 0.663 | 1.000 | 0.500 | 0.975 | 0.487 |
| text + counter + link | 0.860 | 0.829 | 1.000 | 0.783 | 0.984 | 0.750 |
| + account | 0.919 | 0.904 | 1.000 | 0.870 | 0.986 | 0.863 |
| full (+ behavior) | 0.919 | 0.904 | 1.000 | 0.870 | 0.986 | 0.863 |

## Accuracy by category

| category | n | correct | accuracy | mistakes (gold→pred) |
|---|---|---|---|---|
| none/airdrop-discussion | 12 | 12 | 1.00 |  |
| none/ambiguous-terms | 12 | 12 | 1.00 |  |
| none/crypto-talk | 12 | 12 | 1.00 |  |
| none/disclosed-promo | 2 | 2 | 1.00 |  |
| none/hard-negative | 4 | 3 | 0.75 | p170: none→unverified-airdrop |
| none/legit-airdrop | 6 | 6 | 1.00 |  |
| none/links | 6 | 6 | 1.00 |  |
| none/new-account | 4 | 4 | 1.00 |  |
| none/non-crypto-giveaway | 10 | 10 | 1.00 |  |
| none/satire | 5 | 5 | 1.00 |  |
| none/victim-question | 4 | 4 | 1.00 |  |
| none/warning | 15 | 15 | 1.00 |  |
| review/claim-no-link | 1 | 0 | 0.00 | p072: unverified-airdrop→none |
| review/connect-urgency | 13 | 11 | 0.85 | p054: unverified-airdrop→none, p069: unverified-airdrop→none |
| review/coordinated | 5 | 4 | 0.80 | p074: unverified-airdrop→none |
| review/dm-claim | 1 | 1 | 1.00 |  |
| review/evasion-leet | 1 | 1 | 1.00 |  |
| review/giveaway-link | 2 | 2 | 1.00 |  |
| review/high-return | 1 | 0 | 0.00 | p062: unverified-airdrop→none |
| review/new-account-giveaway | 2 | 2 | 1.00 |  |
| review/shortener | 2 | 2 | 1.00 |  |
| review/telegram | 1 | 1 | 1.00 |  |
| review/unofficial-claim | 4 | 3 | 0.75 | p056: unverified-airdrop→none |
| review/wallet-farming | 1 | 0 | 0.00 | p059: unverified-airdrop→none |
| scam/blocklisted-domain | 5 | 5 | 1.00 |  |
| scam/credential | 7 | 7 | 1.00 |  |
| scam/evasion-homoglyph | 2 | 2 | 1.00 |  |
| scam/evasion-leet | 1 | 1 | 1.00 |  |
| scam/evasion-obfuscated-link | 1 | 1 | 1.00 |  |
| scam/evasion-paraphrase | 2 | 0 | 0.00 | p009: crypto-scam→none, p019: crypto-scam→none |
| scam/evasion-spacing | 1 | 1 | 1.00 |  |
| scam/image-only | 1 | 0 | 0.00 | p045: crypto-scam→unverified-airdrop |
| scam/impersonation | 7 | 6 | 0.86 | p046: crypto-scam→unverified-airdrop |
| scam/lookalike-domain | 4 | 4 | 1.00 |  |
| scam/send-to-receive | 8 | 6 | 0.75 | p005: crypto-scam→none, p008: crypto-scam→none |
| scam/upfront-fee | 7 | 7 | 1.00 |  |

## Efficiency (offline mode)

- Resource load (incl. 119,002-domain MetaMask blocklist): 306 ms, peak 20.0 MB
- Per-post latency: mean 0.473 ms, median 0.319 ms, p95 1.174 ms, max 2.332 ms
- Extra peak memory while scoring all posts: 12040 KB
- Network calls: 0 (live mode adds 2 API calls per post + up to 5 HEAD requests per shortened link)
- Posts dropped by prefilter: 13/172
- Behavior blocklist at end of stream: ['eth-drop.claims/go']

