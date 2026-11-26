# Evaluation report — split: `dev_real` (57 posts)

Gold label distribution: crypto-scam=6, unverified-airdrop=13, none=38

## Full labeler

Accuracy: **0.807**

| gold \ predicted | crypto-scam | unverified-airdrop | none |
|---|---|---|---|
| **crypto-scam** | 6 | 0 | 0 |
| **unverified-airdrop** | 0 | 3 | 10 |
| **none** | 0 | 1 | 37 |

| label | precision | recall | F1 | support |
|---|---|---|---|---|
| crypto-scam | 1.000 | 1.000 | 1.000 | 6 |
| unverified-airdrop | 0.750 | 0.231 | 0.353 | 13 |
| none | 0.787 | 0.974 | 0.871 | 38 |
| *any label (binary)* | 0.900 | 0.474 | 0.621 | 19 |

Policy targets (§3.3): `crypto-scam` precision ≥ 0.90 → **1.000** (met); recall proxy (any label on harmful posts) ≥ 0.80 → **0.474** (NOT met).

## Baseline and ablations

Keyword baseline = label every post containing a crypto-promotion keyword (the 'blocking crypto keywords' alternative rejected in policy §3.5).

| system | accuracy | macro F1 | scam P | scam R | any-label P | any-label R |
|---|---|---|---|---|---|---|
| keyword baseline | 0.368 | 0.270 | 0.146 | 1.000 | 0.439 | 0.947 |
| text only | 0.596 | 0.344 | 0.143 | 0.167 | 0.250 | 0.105 |
| text + counter | 0.702 | 0.415 | 1.000 | 0.167 | 1.000 | 0.105 |
| text + counter + link | 0.807 | 0.741 | 1.000 | 1.000 | 0.900 | 0.474 |
| + account | 0.807 | 0.741 | 1.000 | 1.000 | 0.900 | 0.474 |
| full (+ behavior) | 0.807 | 0.741 | 1.000 | 1.000 | 0.900 | 0.474 |

## Accuracy by category

| category | n | correct | accuracy | mistakes (gold→pred) |
|---|---|---|---|---|
| real/crypto-scam | 6 | 6 | 1.00 |  |
| real/none | 38 | 37 | 0.97 | r054: none→unverified-airdrop |
| real/unverified-airdrop | 13 | 3 | 0.23 | r200: unverified-airdrop→none, r189: unverified-airdrop→none, r412: unverified-airdrop→none, r517: unverified-airdrop→none, r405: unverified-airdrop→none, r400: unverified-airdrop→none, r071: unverified-airdrop→none, r125: unverified-airdrop→none, r046: unverified-airdrop→none, r113: unverified-airdrop→none |

## Efficiency (offline mode)

- Resource load (incl. 119,002-domain MetaMask blocklist): 313 ms, peak 20.0 MB
- Per-post latency: mean 1.105 ms, median 1.191 ms, p95 1.788 ms, max 1.896 ms
- Extra peak memory while scoring all posts: 12351 KB
- Network calls: 0 (live mode adds 2 API calls per post + up to 5 HEAD requests per shortened link)
- Posts dropped by prefilter: 2/57
- Behavior blocklist at end of stream: ['eth-drop.claims/go']

## Errors

- **r200** gold `unverified-airdrop` → pred `none` (score 1.0) — 'Little Pepe Mega Giveaway wn.nr/SmHhUZd'
  - signals: unverified_airdrop_link ("wn.nr")
- **r189** gold `unverified-airdrop` → pred `none` (score 1.0) — 'Little Pepe Mega Giveaway wn.nr/SmHhUZd'
  - signals: unverified_airdrop_link ("wn.nr")
- **r412** gold `unverified-airdrop` → pred `none` (score 2.5) — '🆕 Umia Testnet is now Live \n\n✔️Wallet: EVM\n✔️Network: Base Sepolia\n✔️Faucet: on Web\n\n🔍 Register 👉 app.testnet.'
  - signals: giveaway_offer ("claim faucet (base sepolia usdc"); unverified_airdrop_link ("app.testnet.umia.finance")
- **r517** gold `unverified-airdrop` → pred `none` (score 2.5) — "Let's join KuCoin X YOM X Space giveaway for 2,000 USDT wn.nr/rj2LhdS"
  - signals: giveaway_offer ("giveaway for 2,000 usdt"); unverified_airdrop_link ("wn.nr")
- **r405** gold `unverified-airdrop` → pred `none` (score 1.0) — 'The path to your rewards is simple and clear.  \nFinish KYC Step 1 as the first required step.  \nHold the minim'
  - signals: claim_cta ("claim your")
- **r400** gold `unverified-airdrop` → pred `none` (score 2.5) — 'Titan Exchange Airdrop 🟢💲\n\nExplore Waitlist: waitlist.titanx.cc?ref=E9EA7234C4\n\n🔹CONNECT WALLET ➞ EVM Wallet ➞'
  - signals: connect_wallet ("connect wallet"); unverified_airdrop_link ("waitlist.titanx.cc")
- **r071** gold `unverified-airdrop` → pred `none` (score 2.0) — '🏛️ Guardians of the Afterlife — both collections, one page\n\nLive supply straight from BNB Chain.\n\n⏳ Paid Genes'
  - signals: urgency ("⏳"); unverified_airdrop_link ("guardians-of-the-afterlife.pages.dev")
- **r125** gold `unverified-airdrop` → pred `none` (score 0.0) — '🔥 $GIDO CHAIN IS GETTING MORE INTERESTING! 🔥\n\n⛏️ FREE MINING\n💎 21M Total Supply — reported\n📅 15 Dec 2026 — rep'
  - signals: (none)
- **r046** gold `unverified-airdrop` → pred `none` (score 2.0) — '⏳ 19 HOURS LEFT — $KEMET airdrop snapshot Nov 11, 10:00 UTC\n\nAnubis Agents & Osiris Guardians (BSC): 10,000 $K'
  - signals: urgency ("⏳"); unverified_airdrop_link ("guardians-of-the-afterlife.pages.dev")
- **r113** gold `unverified-airdrop` → pred `none` (score 2.5) — 'PolloCoin is just getting started. Take advantage of this opportunity to receive free POLLO by joining our Dis'
  - signals: giveaway_offer ("airdrop #rain #crypto"); unverified_airdrop_link ("discord.gg")
- **r054** gold `none` → pred `unverified-airdrop` (score 3.5) — 'Binance Alpha airdrop claims are live NOW! 🚀 Distro starts Nov 20, 2026, 18:00 (UTC+8). Need 250+ Alpha points'
  - signals: giveaway_offer ("airdrop claims are live"); claim_cta ("claims are live"); unverified_airdrop_link ("cryptovka.com")
