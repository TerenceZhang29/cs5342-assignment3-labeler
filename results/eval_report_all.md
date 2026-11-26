# Evaluation report — split: `all` (340 posts)

Gold label distribution: crypto-scam=62, unverified-airdrop=73, none=205

## Full labeler

Accuracy: **0.853**

| gold \ predicted | crypto-scam | unverified-airdrop | none |
|---|---|---|---|
| **crypto-scam** | 56 | 1 | 5 |
| **unverified-airdrop** | 0 | 60 | 13 |
| **none** | 1 | 30 | 174 |

| label | precision | recall | F1 | support |
|---|---|---|---|---|
| crypto-scam | 0.982 | 0.903 | 0.941 | 62 |
| unverified-airdrop | 0.659 | 0.822 | 0.732 | 73 |
| none | 0.906 | 0.849 | 0.877 | 205 |
| *any label (binary)* | 0.791 | 0.867 | 0.827 | 135 |

Policy targets (§3.3): `crypto-scam` precision ≥ 0.90 → **0.982** (met); recall proxy (any label on harmful posts) ≥ 0.80 → **0.867** (met).

## Baseline and ablations

Keyword baseline = label every post containing a crypto-promotion keyword (the 'blocking crypto keywords' alternative rejected in policy §3.5).

| system | accuracy | macro F1 | scam P | scam R | any-label P | any-label R |
|---|---|---|---|---|---|---|
| keyword baseline | 0.426 | 0.311 | 0.223 | 0.774 | 0.498 | 0.793 |
| text only | 0.685 | 0.593 | 0.543 | 0.403 | 0.688 | 0.489 |
| text + counter | 0.753 | 0.652 | 0.962 | 0.403 | 0.904 | 0.489 |
| text + counter + link | 0.838 | 0.826 | 0.981 | 0.839 | 0.797 | 0.844 |
| + account | 0.853 | 0.850 | 0.982 | 0.903 | 0.791 | 0.867 |
| full (+ behavior) | 0.853 | 0.850 | 0.982 | 0.903 | 0.791 | 0.867 |

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
| none/non-crypto-giveaway | 10 | 8 | 0.80 | p122: none→unverified-airdrop, p127: none→unverified-airdrop |
| none/satire | 5 | 5 | 1.00 |  |
| none/victim-question | 4 | 4 | 1.00 |  |
| none/warning | 15 | 15 | 1.00 |  |
| real/crypto-scam | 16 | 16 | 1.00 |  |
| real/none | 113 | 85 | 0.75 | r188: none→unverified-airdrop, r538: none→unverified-airdrop, r177: none→unverified-airdrop, r505: none→unverified-airdrop, r214: none→unverified-airdrop, r213: none→unverified-airdrop, r210: none→unverified-airdrop, r398: none→unverified-airdrop, r086: none→unverified-airdrop, r512: none→unverified-airdrop, r561: none→unverified-airdrop, r127: none→unverified-airdrop, r126: none→unverified-airdrop, r556: none→unverified-airdrop, r392: none→unverified-airdrop, r029: none→unverified-airdrop, r026: none→unverified-airdrop, r109: none→unverified-airdrop, r025: none→unverified-airdrop, r023: none→unverified-airdrop, r013: none→unverified-airdrop, r054: none→unverified-airdrop, r151: none→unverified-airdrop, r150: none→unverified-airdrop, r446: none→unverified-airdrop, r340: none→unverified-airdrop, r005: none→unverified-airdrop, r311: none→crypto-scam |
| real/unverified-airdrop | 39 | 26 | 0.67 | r200: unverified-airdrop→none, r195: unverified-airdrop→none, r194: unverified-airdrop→none, r189: unverified-airdrop→none, r499: unverified-airdrop→none, r526: unverified-airdrop→none, r519: unverified-airdrop→none, r578: unverified-airdrop→none, r405: unverified-airdrop→none, r125: unverified-airdrop→none, r124: unverified-airdrop→none, r123: unverified-airdrop→none, r051: unverified-airdrop→none |
| review/claim-no-link | 1 | 1 | 1.00 |  |
| review/connect-urgency | 13 | 13 | 1.00 |  |
| review/coordinated | 5 | 5 | 1.00 |  |
| review/dm-claim | 1 | 1 | 1.00 |  |
| review/evasion-leet | 1 | 1 | 1.00 |  |
| review/giveaway-link | 2 | 2 | 1.00 |  |
| review/high-return | 1 | 1 | 1.00 |  |
| review/new-account-giveaway | 2 | 2 | 1.00 |  |
| review/shortener | 2 | 2 | 1.00 |  |
| review/telegram | 1 | 1 | 1.00 |  |
| review/unofficial-claim | 4 | 4 | 1.00 |  |
| review/wallet-farming | 1 | 1 | 1.00 |  |
| scam/blocklisted-domain | 5 | 5 | 1.00 |  |
| scam/credential | 7 | 7 | 1.00 |  |
| scam/evasion-homoglyph | 2 | 2 | 1.00 |  |
| scam/evasion-leet | 1 | 1 | 1.00 |  |
| scam/evasion-obfuscated-link | 1 | 1 | 1.00 |  |
| scam/evasion-paraphrase | 2 | 0 | 0.00 | p009: crypto-scam→none, p019: crypto-scam→none |
| scam/evasion-spacing | 1 | 1 | 1.00 |  |
| scam/image-only | 1 | 0 | 0.00 | p045: crypto-scam→none |
| scam/impersonation | 7 | 6 | 0.86 | p046: crypto-scam→unverified-airdrop |
| scam/lookalike-domain | 4 | 4 | 1.00 |  |
| scam/send-to-receive | 8 | 6 | 0.75 | p005: crypto-scam→none, p008: crypto-scam→none |
| scam/upfront-fee | 7 | 7 | 1.00 |  |

## Efficiency (offline mode)

- Resource load (incl. 119,002-domain MetaMask blocklist): 317 ms, peak 20.0 MB
- Per-post latency: mean 0.827 ms, median 0.637 ms, p95 1.768 ms, max 3.412 ms
- Extra peak memory while scoring all posts: 12409 KB
- Network calls: 0 (live mode adds 2 API calls per post + up to 5 HEAD requests per shortened link)
- Posts dropped by prefilter: 17/340
- Behavior blocklist at end of stream: ['eth-drop.claims/go']

