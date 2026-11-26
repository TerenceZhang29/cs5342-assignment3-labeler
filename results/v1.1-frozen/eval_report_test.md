# Evaluation report — split: `test` (224 posts)

Gold label distribution: crypto-scam=40, unverified-airdrop=48, none=136

## Full labeler

Accuracy: **0.746**

| gold \ predicted | crypto-scam | unverified-airdrop | none |
|---|---|---|---|
| **crypto-scam** | 28 | 1 | 11 |
| **unverified-airdrop** | 0 | 32 | 16 |
| **none** | 5 | 24 | 107 |

| label | precision | recall | F1 | support |
|---|---|---|---|---|
| crypto-scam | 0.848 | 0.700 | 0.767 | 40 |
| unverified-airdrop | 0.561 | 0.667 | 0.610 | 48 |
| none | 0.799 | 0.787 | 0.793 | 136 |
| *any label (binary)* | 0.678 | 0.693 | 0.685 | 88 |

Policy targets (§3.3): `crypto-scam` precision ≥ 0.90 → **0.848** (NOT met); recall proxy (any label on harmful posts) ≥ 0.80 → **0.693** (NOT met).

## Baseline and ablations

Keyword baseline = label every post containing a crypto-promotion keyword (the 'blocking crypto keywords' alternative rejected in policy §3.5).

| system | accuracy | macro F1 | scam P | scam R | any-label P | any-label R |
|---|---|---|---|---|---|---|
| keyword baseline | 0.420 | 0.306 | 0.218 | 0.775 | 0.486 | 0.784 |
| text only | 0.652 | 0.513 | 0.552 | 0.400 | 0.644 | 0.330 |
| text + counter | 0.692 | 0.546 | 0.762 | 0.400 | 0.806 | 0.330 |
| text + counter + link | 0.799 | 0.745 | 0.833 | 0.625 | 0.857 | 0.614 |
| + account | 0.746 | 0.723 | 0.848 | 0.700 | 0.678 | 0.693 |
| full (+ behavior) | 0.746 | 0.723 | 0.848 | 0.700 | 0.678 | 0.693 |

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
| none/non-crypto-giveaway | 6 | 6 | 1.00 |  |
| none/satire | 4 | 4 | 1.00 |  |
| none/victim-question | 2 | 2 | 1.00 |  |
| none/warning | 10 | 10 | 1.00 |  |
| real/crypto-scam | 10 | 2 | 0.20 | r226: crypto-scam→none, r224: crypto-scam→none, r223: crypto-scam→none, r221: crypto-scam→none, r220: crypto-scam→none, r219: crypto-scam→none, r217: crypto-scam→none, r216: crypto-scam→none |
| real/none | 75 | 47 | 0.63 | r259: none→unverified-airdrop, r258: none→crypto-scam, r255: none→crypto-scam, r252: none→crypto-scam, r177: none→unverified-airdrop, r505: none→unverified-airdrop, r520: none→unverified-airdrop, r213: none→unverified-airdrop, r210: none→unverified-airdrop, r398: none→unverified-airdrop, r512: none→unverified-airdrop, r558: none→unverified-airdrop, r126: none→unverified-airdrop, r109: none→unverified-airdrop, r025: none→unverified-airdrop, r274: none→crypto-scam, r454: none→unverified-airdrop, r013: none→unverified-airdrop, r450: none→unverified-airdrop, r151: none→unverified-airdrop, r150: none→unverified-airdrop, r446: none→unverified-airdrop, r340: none→unverified-airdrop, r442: none→unverified-airdrop, r142: none→unverified-airdrop, r053: none→unverified-airdrop, r418: none→unverified-airdrop, r311: none→crypto-scam |
| real/unverified-airdrop | 26 | 13 | 0.50 | r195: unverified-airdrop→none, r194: unverified-airdrop→none, r499: unverified-airdrop→none, r530: unverified-airdrop→none, r526: unverified-airdrop→none, r519: unverified-airdrop→none, r578: unverified-airdrop→none, r401: unverified-airdrop→none, r076: unverified-airdrop→none, r124: unverified-airdrop→none, r123: unverified-airdrop→none, r018: unverified-airdrop→none, r051: unverified-airdrop→none |
| review/claim-no-link | 1 | 0 | 0.00 | p072: unverified-airdrop→none |
| review/connect-urgency | 9 | 7 | 0.78 | p054: unverified-airdrop→none, p069: unverified-airdrop→none |
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
| scam/image-only | 1 | 0 | 0.00 | p045: crypto-scam→unverified-airdrop |
| scam/impersonation | 4 | 4 | 1.00 |  |
| scam/lookalike-domain | 3 | 3 | 1.00 |  |
| scam/send-to-receive | 5 | 3 | 0.60 | p005: crypto-scam→none, p008: crypto-scam→none |
| scam/upfront-fee | 5 | 5 | 1.00 |  |

## Efficiency (offline mode)

- Resource load (incl. 119,002-domain MetaMask blocklist): 305 ms, peak 20.0 MB
- Per-post latency: mean 0.762 ms, median 0.591 ms, p95 1.546 ms, max 5.483 ms
- Extra peak memory while scoring all posts: 12347 KB
- Network calls: 0 (live mode adds 2 API calls per post + up to 5 HEAD requests per shortened link)
- Posts dropped by prefilter: 10/224
- Behavior blocklist at end of stream: ['eth-drop.claims/go']

