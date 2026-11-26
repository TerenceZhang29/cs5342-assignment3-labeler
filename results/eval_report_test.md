# Evaluation report — split: `test` (224 posts)

Gold label distribution: crypto-scam=40, unverified-airdrop=48, none=136

## Full labeler

Accuracy: **0.830**

| gold \ predicted | crypto-scam | unverified-airdrop | none |
|---|---|---|---|
| **crypto-scam** | 36 | 0 | 4 |
| **unverified-airdrop** | 0 | 39 | 9 |
| **none** | 1 | 24 | 111 |

| label | precision | recall | F1 | support |
|---|---|---|---|---|
| crypto-scam | 0.973 | 0.900 | 0.935 | 40 |
| unverified-airdrop | 0.619 | 0.812 | 0.703 | 48 |
| none | 0.895 | 0.816 | 0.854 | 136 |
| *any label (binary)* | 0.750 | 0.852 | 0.798 | 88 |

Policy targets (§3.3): `crypto-scam` precision ≥ 0.90 → **0.973** (met); recall proxy (any label on harmful posts) ≥ 0.80 → **0.852** (met).

## Baseline and ablations

Keyword baseline = label every post containing a crypto-promotion keyword (the 'blocking crypto keywords' alternative rejected in policy §3.5).

| system | accuracy | macro F1 | scam P | scam R | any-label P | any-label R |
|---|---|---|---|---|---|---|
| keyword baseline | 0.420 | 0.306 | 0.218 | 0.775 | 0.486 | 0.784 |
| text only | 0.688 | 0.594 | 0.552 | 0.400 | 0.683 | 0.489 |
| text + counter | 0.750 | 0.649 | 0.941 | 0.400 | 0.878 | 0.489 |
| text + counter + link | 0.817 | 0.807 | 0.971 | 0.825 | 0.760 | 0.830 |
| + account | 0.830 | 0.831 | 0.973 | 0.900 | 0.750 | 0.852 |
| full (+ behavior) | 0.830 | 0.831 | 0.973 | 0.900 | 0.750 | 0.852 |

## Accuracy by category

| category | n | correct | accuracy | mistakes (gold→pred) |
|---|---|---|---|---|
| none/airdrop-discussion | 8 | 8 | 1.00 |  |
| none/ambiguous-terms | 8 | 8 | 1.00 |  |
| none/crypto-talk | 8 | 8 | 1.00 |  |
| none/disclosed-promo | 2 | 2 | 1.00 |  |
| none/hard-negative | 3 | 2 | 0.67 | p170: none→unverified-airdrop |
| none/legit-airdrop | 4 | 4 | 1.00 |  |
| none/links | 4 | 4 | 1.00 |  |
| none/new-account | 2 | 2 | 1.00 |  |
| none/non-crypto-giveaway | 6 | 4 | 0.67 | p122: none→unverified-airdrop, p127: none→unverified-airdrop |
| none/satire | 4 | 4 | 1.00 |  |
| none/victim-question | 2 | 2 | 1.00 |  |
| none/warning | 10 | 10 | 1.00 |  |
| real/crypto-scam | 10 | 10 | 1.00 |  |
| real/none | 75 | 53 | 0.71 | r188: none→unverified-airdrop, r538: none→unverified-airdrop, r177: none→unverified-airdrop, r505: none→unverified-airdrop, r213: none→unverified-airdrop, r210: none→unverified-airdrop, r398: none→unverified-airdrop, r086: none→unverified-airdrop, r512: none→unverified-airdrop, r127: none→unverified-airdrop, r126: none→unverified-airdrop, r392: none→unverified-airdrop, r029: none→unverified-airdrop, r026: none→unverified-airdrop, r109: none→unverified-airdrop, r025: none→unverified-airdrop, r013: none→unverified-airdrop, r151: none→unverified-airdrop, r150: none→unverified-airdrop, r446: none→unverified-airdrop, r340: none→unverified-airdrop, r311: none→crypto-scam |
| real/unverified-airdrop | 26 | 17 | 0.65 | r195: unverified-airdrop→none, r194: unverified-airdrop→none, r499: unverified-airdrop→none, r526: unverified-airdrop→none, r519: unverified-airdrop→none, r578: unverified-airdrop→none, r124: unverified-airdrop→none, r123: unverified-airdrop→none, r051: unverified-airdrop→none |
| review/claim-no-link | 1 | 1 | 1.00 |  |
| review/connect-urgency | 9 | 9 | 1.00 |  |
| review/coordinated | 3 | 3 | 1.00 |  |
| review/dm-claim | 1 | 1 | 1.00 |  |
| review/evasion-leet | 1 | 1 | 1.00 |  |
| review/giveaway-link | 2 | 2 | 1.00 |  |
| review/shortener | 2 | 2 | 1.00 |  |
| review/unofficial-claim | 3 | 3 | 1.00 |  |
| scam/blocklisted-domain | 3 | 3 | 1.00 |  |
| scam/credential | 6 | 6 | 1.00 |  |
| scam/evasion-homoglyph | 1 | 1 | 1.00 |  |
| scam/evasion-paraphrase | 1 | 0 | 0.00 | p009: crypto-scam→none |
| scam/evasion-spacing | 1 | 1 | 1.00 |  |
| scam/image-only | 1 | 0 | 0.00 | p045: crypto-scam→none |
| scam/impersonation | 4 | 4 | 1.00 |  |
| scam/lookalike-domain | 3 | 3 | 1.00 |  |
| scam/send-to-receive | 5 | 3 | 0.60 | p005: crypto-scam→none, p008: crypto-scam→none |
| scam/upfront-fee | 5 | 5 | 1.00 |  |

## Efficiency (offline mode)

- Resource load (incl. 119,002-domain MetaMask blocklist): 318 ms, peak 20.0 MB
- Per-post latency: mean 0.874 ms, median 0.673 ms, p95 1.843 ms, max 5.330 ms
- Extra peak memory while scoring all posts: 12397 KB
- Network calls: 0 (live mode adds 2 API calls per post + up to 5 HEAD requests per shortened link)
- Posts dropped by prefilter: 10/224
- Behavior blocklist at end of stream: ['eth-drop.claims/go']

