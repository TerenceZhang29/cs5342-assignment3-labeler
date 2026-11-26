# Evaluation report — split: `test_synthetic` (113 posts)

Gold label distribution: crypto-scam=30, unverified-airdrop=22, none=61

## Full labeler

Accuracy: **0.938**

| gold \ predicted | crypto-scam | unverified-airdrop | none |
|---|---|---|---|
| **crypto-scam** | 26 | 0 | 4 |
| **unverified-airdrop** | 0 | 22 | 0 |
| **none** | 0 | 3 | 58 |

| label | precision | recall | F1 | support |
|---|---|---|---|---|
| crypto-scam | 1.000 | 0.867 | 0.929 | 30 |
| unverified-airdrop | 0.880 | 1.000 | 0.936 | 22 |
| none | 0.935 | 0.951 | 0.943 | 61 |
| *any label (binary)* | 0.941 | 0.923 | 0.932 | 52 |

Policy targets (§3.3): `crypto-scam` precision ≥ 0.90 → **1.000** (met); recall proxy (any label on harmful posts) ≥ 0.80 → **0.923** (met).

## Baseline and ablations

Keyword baseline = label every post containing a crypto-promotion keyword (the 'blocking crypto keywords' alternative rejected in policy §3.5).

| system | accuracy | macro F1 | scam P | scam R | any-label P | any-label R |
|---|---|---|---|---|---|---|
| keyword baseline | 0.513 | 0.372 | 0.344 | 0.700 | 0.607 | 0.712 |
| text only | 0.735 | 0.700 | 0.714 | 0.500 | 0.795 | 0.673 |
| text + counter | 0.788 | 0.744 | 1.000 | 0.500 | 0.921 | 0.673 |
| text + counter + link | 0.894 | 0.876 | 1.000 | 0.767 | 0.939 | 0.885 |
| + account | 0.938 | 0.936 | 1.000 | 0.867 | 0.941 | 0.923 |
| full (+ behavior) | 0.938 | 0.936 | 1.000 | 0.867 | 0.941 | 0.923 |

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

- Resource load (incl. 119,002-domain MetaMask blocklist): 334 ms, peak 20.0 MB
- Per-post latency: mean 0.525 ms, median 0.350 ms, p95 1.386 ms, max 1.563 ms
- Extra peak memory while scoring all posts: 12400 KB
- Network calls: 0 (live mode adds 2 API calls per post + up to 5 HEAD requests per shortened link)
- Posts dropped by prefilter: 8/113
- Behavior blocklist at end of stream: ['eth-drop.claims/go']

## Errors

- **p005** gold `crypto-scam` → pred `none` (score 1.5) — 'Send any amount of SOL to 7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU and receive 3x back. Not a scam, 100% l'
  - signals: legitimacy_assurance ("not a scam")
- **p008** gold `crypto-scam` → pred `none` (score 0.0) — "Congrats, your wallet was selected! Send 0.05 ETH for gas and we'll send your 2 ETH prize right after."
  - signals: (none)
- **p009** gold `crypto-scam` → pred `none` (score 0.0) — "Got extra ETH sitting around? I'll flip it for you. You send 1, I send 2. Simple as that."
  - signals: (none)
- **p045** gold `crypto-scam` → pred `none` (score 1.5) — '🎁 see image for details 👇 #airdrop #eth #giveaway'
  - signals: giveaway_offer ("airdrop #eth")
- **p122** gold `none` → pred `unverified-airdrop` (score 2.0) — 'Tote bag giveaway! Free shipping for the first 100 orders too. Link in bio.'
  - signals: claim_cta ("link in bio"); urgency ("first 100")
- **p127** gold `none` → pred `unverified-airdrop` (score 2.0) — 'Loyalty card update: collect 10 stamps, claim your free latte. Limited time double-stamp days!'
  - signals: claim_cta ("claim your"); urgency ("limited time")
- **p170** gold `none` → pred `unverified-airdrop` (score 5.0) — "Moderation note: posts asking you to 'connect your wallet to claim free tokens before midnight' are being revi"
  - signals: giveaway_offer ("claim free tokens"); claim_cta ("claim free"); connect_wallet ("connect your wallet"); urgency ("before midnight")
