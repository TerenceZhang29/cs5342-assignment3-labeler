# Evaluation report — split: `test` (113 posts)

Gold label distribution: crypto-scam=30, unverified-airdrop=22, none=61

## Full labeler

Accuracy: **0.920**

| gold \ predicted | crypto-scam | unverified-airdrop | none |
|---|---|---|---|
| **crypto-scam** | 25 | 1 | 4 |
| **unverified-airdrop** | 0 | 19 | 3 |
| **none** | 0 | 1 | 60 |

| label | precision | recall | F1 | support |
|---|---|---|---|---|
| crypto-scam | 1.000 | 0.833 | 0.909 | 30 |
| unverified-airdrop | 0.905 | 0.864 | 0.884 | 22 |
| none | 0.896 | 0.984 | 0.938 | 61 |
| *any label (binary)* | 0.978 | 0.865 | 0.918 | 52 |

Policy targets (§3.3): `crypto-scam` precision ≥ 0.90 → **1.000** (met); recall proxy (any label on harmful posts) ≥ 0.80 → **0.865** (met).

## Baseline and ablations

Keyword baseline = label every post containing a crypto-promotion keyword (the 'blocking crypto keywords' alternative rejected in policy §3.5).

| system | accuracy | macro F1 | scam P | scam R | any-label P | any-label R |
|---|---|---|---|---|---|---|
| keyword baseline | 0.513 | 0.372 | 0.344 | 0.700 | 0.607 | 0.712 |
| text only | 0.690 | 0.628 | 0.714 | 0.500 | 0.788 | 0.500 |
| text + counter | 0.743 | 0.671 | 1.000 | 0.500 | 0.963 | 0.500 |
| text + counter + link | 0.867 | 0.843 | 1.000 | 0.733 | 0.976 | 0.769 |
| + account | 0.920 | 0.910 | 1.000 | 0.833 | 0.978 | 0.865 |
| full (+ behavior) | 0.920 | 0.910 | 1.000 | 0.833 | 0.978 | 0.865 |

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
| review/claim-no-link | 1 | 0 | 0.00 | p072: unverified-airdrop→none |
| review/connect-urgency | 9 | 7 | 0.78 | p054: unverified-airdrop→none, p069: unverified-airdrop→none |
| review/coordinated | 3 | 3 | 1.00 |  |
| review/dm-claim | 1 | 1 | 1.00 |  |
| review/evasion-leet | 1 | 1 | 1.00 |  |
| review/giveaway-link | 2 | 2 | 1.00 |  |
| review/shortener | 2 | 2 | 1.00 |  |
| review/unofficial-claim | 3 | 3 | 1.00 |  |
| scam/blocklisted-domain | 3 | 2 | 0.67 | p035: crypto-scam→none |
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

- Resource load (incl. 119,002-domain MetaMask blocklist): 74 ms, peak 14.7 MB
- Per-post latency: mean 0.456 ms, median 0.297 ms, p95 1.159 ms, max 2.339 ms
- Extra peak memory while scoring all posts: 11973 KB
- Network calls: 0 (live mode adds 2 API calls per post + up to 5 HEAD requests per shortened link)
- Posts dropped by prefilter: 8/113
- Behavior blocklist at end of stream: ['eth-drop.claims/go']

## Errors

- **p005** gold `crypto-scam` → pred `none` (score 3.0) — 'Send any amount of SOL to 7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU and receive 3x back. Not a scam, 100% l'
  - signals: legitimacy_assurance ("not a scam"); very_new_account ("3.0 days old")
- **p008** gold `crypto-scam` → pred `none` (score 1.5) — "Congrats, your wallet was selected! Send 0.05 ETH for gas and we'll send your 2 ETH prize right after."
  - signals: very_new_account ("6.0 days old")
- **p009** gold `crypto-scam` → pred `none` (score 1.0) — "Got extra ETH sitting around? I'll flip it for you. You send 1, I send 2. Simple as that."
  - signals: new_account ("8 days old")
- **p035** gold `crypto-scam` → pred `none` (score 1.5) — 'Having trouble listing your NFTs? Our team can fix it fast, start here opensea.support'
  - signals: very_new_account ("3.0 days old")
- **p045** gold `crypto-scam` → pred `unverified-airdrop` (score 3.0) — '🎁 see image for details 👇 #airdrop #eth #giveaway'
  - signals: giveaway_offer ("airdrop #eth"); very_new_account ("2.0 days old")
- **p054** gold `unverified-airdrop` → pred `none` (score 2.5) — 'New memecoin $MOON airdrop — check eligibility in bio 🚀🚀'
  - signals: claim_cta ("check eligibility"); very_new_account ("3.0 days old")
- **p069** gold `unverified-airdrop` → pred `none` (score 2.5) — 'Points → tokens conversion is LIVE. Link your wallet before the snapshot or lose your allocation ⚠️'
  - signals: connect_wallet ("link your wallet"); new_account ("19 days old")
- **p072** gold `unverified-airdrop` → pred `none` (score 2.5) — "Psst, $HYPE2 airdrop claims are open. Claim your tokens before they're gone"
  - signals: giveaway_offer ("2 airdrop"); claim_cta ("claims are open")
- **p170** gold `none` → pred `unverified-airdrop` (score 5.0) — "Moderation note: posts asking you to 'connect your wallet to claim free tokens before midnight' are being revi"
  - signals: giveaway_offer ("claim free tokens"); claim_cta ("claim free"); connect_wallet ("connect your wallet"); urgency ("before midnight")
