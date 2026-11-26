# Evaluation report — split: `dev_real` (57 posts)

Gold label distribution: crypto-scam=6, unverified-airdrop=13, none=38

## Full labeler

Accuracy: **0.561**

| gold \ predicted | crypto-scam | unverified-airdrop | none |
|---|---|---|---|
| **crypto-scam** | 0 | 1 | 5 |
| **unverified-airdrop** | 0 | 7 | 6 |
| **none** | 5 | 8 | 25 |

| label | precision | recall | F1 | support |
|---|---|---|---|---|
| crypto-scam | 0.000 | 0.000 | 0.000 | 6 |
| unverified-airdrop | 0.438 | 0.538 | 0.483 | 13 |
| none | 0.694 | 0.658 | 0.676 | 38 |
| *any label (binary)* | 0.381 | 0.421 | 0.400 | 19 |

Policy targets (§3.3): `crypto-scam` precision ≥ 0.90 → **0.000** (NOT met); recall proxy (any label on harmful posts) ≥ 0.80 → **0.421** (NOT met).

## Baseline and ablations

Keyword baseline = label every post containing a crypto-promotion keyword (the 'blocking crypto keywords' alternative rejected in policy §3.5).

| system | accuracy | macro F1 | scam P | scam R | any-label P | any-label R |
|---|---|---|---|---|---|---|
| keyword baseline | 0.368 | 0.270 | 0.146 | 1.000 | 0.439 | 0.947 |
| text only | 0.561 | 0.285 | 0.000 | 0.000 | 0.125 | 0.053 |
| text + counter | 0.596 | 0.295 | 0.000 | 0.000 | 0.167 | 0.053 |
| text + counter + link | 0.596 | 0.351 | 0.000 | 0.000 | 0.364 | 0.211 |
| + account | 0.561 | 0.386 | 0.000 | 0.000 | 0.381 | 0.421 |
| full (+ behavior) | 0.561 | 0.386 | 0.000 | 0.000 | 0.381 | 0.421 |

## Accuracy by category

| category | n | correct | accuracy | mistakes (gold→pred) |
|---|---|---|---|---|
| real/crypto-scam | 6 | 0 | 0.00 | r227: crypto-scam→none, r225: crypto-scam→none, r222: crypto-scam→none, r218: crypto-scam→none, r215: crypto-scam→none, r174: crypto-scam→unverified-airdrop |
| real/none | 38 | 25 | 0.66 | r257: none→crypto-scam, r253: none→crypto-scam, r250: none→crypto-scam, r539: none→unverified-airdrop, r214: none→unverified-airdrop, r561: none→unverified-airdrop, r130: none→unverified-airdrop, r556: none→unverified-airdrop, r035: none→crypto-scam, r273: none→crypto-scam, r054: none→unverified-airdrop, r271: none→unverified-airdrop, r001: none→unverified-airdrop |
| real/unverified-airdrop | 13 | 7 | 0.54 | r200: unverified-airdrop→none, r189: unverified-airdrop→none, r405: unverified-airdrop→none, r400: unverified-airdrop→none, r125: unverified-airdrop→none, r113: unverified-airdrop→none |

## Efficiency (offline mode)

- Resource load (incl. 119,002-domain MetaMask blocklist): 305 ms, peak 20.0 MB
- Per-post latency: mean 0.987 ms, median 1.083 ms, p95 1.516 ms, max 1.563 ms
- Extra peak memory while scoring all posts: 12348 KB
- Network calls: 0 (live mode adds 2 API calls per post + up to 5 HEAD requests per shortened link)
- Posts dropped by prefilter: 2/57
- Behavior blocklist at end of stream: ['eth-drop.claims/go']

## Errors

- **r257** gold `none` → pred `crypto-scam` (score 7.5) — "1/ Get faucet\n\n⭕✨ Go to : www.alchemy.com/faucets/eth...\n\n➖ Click 'Signin'\n\n➖ Enter EVM address\n\n➖ Complete ca"
  - signals: send_to_receive ("send me eth' 👉 you need at least 0.001 $eth on the mainne..."); giveaway_offer ("receive faucet tokens"); new_account ("17 days old")
- **r253** gold `none` → pred `crypto-scam` (score 7.5) — "1/ Claim faucet\n\n⭕✨ Go to : www.alchemy.com/faucets/eth...\n\n➖ Click 'Signin'\n\n➖ Enter EVM address\n\n➖ Complete "
  - signals: send_to_receive ("send me eth' 👉 you need at least 0.001 $eth on the mainne..."); giveaway_offer ("receive faucet tokens"); unverified_airdrop_link ("www.alchemy.com")
- **r250** gold `none` → pred `crypto-scam` (score 6.5) — "2/ Faucet\n\n⭕✨ Go to : www.alchemy.com/faucets/bas...\n\n➖ Click 'Signin'\n\n➖ Enter EVM address\n\n➖ Complete captch"
  - signals: send_to_receive ("send me eth' 👉 you need at least 0.001 $eth on base mainn..."); giveaway_offer ("receive faucet tokens")
- **r200** gold `unverified-airdrop` → pred `none` (score 1.0) — 'Little Pepe Mega Giveaway wn.nr/SmHhUZd'
  - signals: unverified_airdrop_link ("wn.nr")
- **r189** gold `unverified-airdrop` → pred `none` (score 1.0) — 'Little Pepe Mega Giveaway wn.nr/SmHhUZd'
  - signals: unverified_airdrop_link ("wn.nr")
- **r539** gold `none` → pred `unverified-airdrop` (score 3.5) — '🚀 HTX Exchange launches "$HTX Frenzy" campaign April 24 - May 15, 2026! Win from a $100K USDT prize pool & ele'
  - signals: giveaway_offer ("win from a $100k usdt"); urgency ("don't miss"); unverified_airdrop_link ("cryptovka.com")
- **r227** gold `crypto-scam` → pred `none` (score 2.5) — '🚨 BTC is knocking on the $80K door.\n\nWe’re marking this comeback moment in Bitcoin history. 🔥\n\nAfter the swing'
  - signals: giveaway_offer ("1 btc giveaway"); unverified_airdrop_link ("insurance-kalshi.com")
- **r225** gold `crypto-scam` → pred `none` (score 2.5) — '🚨 BTC is knocking on the $80K door.\n\nWe’re marking this comeback moment in Bitcoin history. 🔥\n\nAfter the swing'
  - signals: giveaway_offer ("1 btc giveaway"); unverified_airdrop_link ("insurance-kalshi.com")
- **r222** gold `crypto-scam` → pred `none` (score 2.5) — '🚨 BTC is knocking on the $80K door.\n\nWe’re marking this comeback moment in Bitcoin history. 🔥\n\nAfter the swing'
  - signals: giveaway_offer ("1 btc giveaway"); unverified_airdrop_link ("insurance-kalshi.com")
- **r218** gold `crypto-scam` → pred `none` (score 2.5) — '🚨 BTC is knocking on the $80K door.\n\nWe’re marking this comeback moment in Bitcoin history. 🔥\n\nAfter the swing'
  - signals: giveaway_offer ("1 btc giveaway"); unverified_airdrop_link ("insurance-kalshi.com")
- **r215** gold `crypto-scam` → pred `none` (score 2.5) — '🚨 BTC is knocking on the $80K door.\n\nWe’re marking this comeback moment in Bitcoin history. 🔥\n\nAfter the swing'
  - signals: giveaway_offer ("1 btc giveaway"); unverified_airdrop_link ("insurance-kalshi.com")
- **r214** gold `none` → pred `unverified-airdrop` (score 4.0) — 'The spin-and-win game declared @Kay33_pls the winner, sending .1 BTC their way. Want a chance to win? Visit th'
  - signals: giveaway_offer ("giveaway #bitcoin"); unverified_airdrop_link ("thrill.com"); very_new_account ("2.7 days old")
- **r405** gold `unverified-airdrop` → pred `none` (score 1.0) — 'The path to your rewards is simple and clear.  \nFinish KYC Step 1 as the first required step.  \nHold the minim'
  - signals: claim_cta ("claim your")
- **r400** gold `unverified-airdrop` → pred `none` (score 2.5) — 'Titan Exchange Airdrop 🟢💲\n\nExplore Waitlist: waitlist.titanx.cc?ref=E9EA7234C4\n\n🔹CONNECT WALLET ➞ EVM Wallet ➞'
  - signals: connect_wallet ("connect wallet"); unverified_airdrop_link ("waitlist.titanx.cc")
- **r561** gold `none` → pred `unverified-airdrop` (score 3.5) — '⚡ Have an idea people might actually love?\nGive it a token.\nSolsmint makes Solana token creation 0.05 SOL with'
  - signals: giveaway_offer ("free mint, burn, airdrop"); unverified_airdrop_link ("solsmint.com"); new_account ("7 days old")
- **r130** gold `none` → pred `unverified-airdrop` (score 3.0) — '🕐 Fri Nov 6, 2026 · 10:12 AM PT\n✅ SPOT THE SCAM — Day 5 answer\nFlags: free airdrop bait, connect wallet to unk'
  - signals: upfront_fee ("fee to claim"); giveaway_offer ("free airdrop"); connect_wallet ("connect wallet"); urgency ("ends soon"); scam_warning ("scam"); new_account ("14 days old")
- **r556** gold `none` → pred `unverified-airdrop` (score 3.5) — 'Building Solsmint, an all-in-one platform for the Solana ecosystem.\n\nLaunch SPL tokens without \ncoding for jus'
  - signals: giveaway_offer ("free mint & burn free airdrops"); unverified_airdrop_link ("solsmint.com"); new_account ("14 days old")
- **r125** gold `unverified-airdrop` → pred `none` (score 1.5) — '🔥 $GIDO CHAIN IS GETTING MORE INTERESTING! 🔥\n\n⛏️ FREE MINING\n💎 21M Total Supply — reported\n📅 15 Dec 2026 — rep'
  - signals: very_new_account ("0.0 days old")
- **r035** gold `none` → pred `crypto-scam` (score 6.5) — 'Paying $45 in gas fees to claim an $8 airdrop because leaving free money on the table violates your personal m'
  - signals: upfront_fee ("fees to claim"); giveaway_offer ("claim an $8 airdrop")
- **r113** gold `unverified-airdrop` → pred `none` (score 2.5) — 'PolloCoin is just getting started. Take advantage of this opportunity to receive free POLLO by joining our Dis'
  - signals: giveaway_offer ("airdrop #rain #crypto"); unverified_airdrop_link ("discord.gg")
- **r174** gold `crypto-scam` → pred `unverified-airdrop` (score 4.5) — 'Thank you for the 2x crypto giveaway—a game-changing gift that’s putting real wealth in the hands of everyday '
  - signals: giveaway_offer ("crypto giveaway"); suspicious_tld ("tsocial.click"); unverified_airdrop_link ("tsocial.click"); new_account ("11 days old")
- **r273** gold `none` → pred `crypto-scam` (score 5.0) — '“How did Coinbase stop deepfake Elon Musk’s promise to double your crypto?” — AMBCrypto\n\n#DeepfakeNews #Deepfa'
  - signals: send_to_receive ("double your crypto")
- **r054** gold `none` → pred `unverified-airdrop` (score 3.5) — 'Binance Alpha airdrop claims are live NOW! 🚀 Distro starts Nov 20, 2026, 18:00 (UTC+8). Need 250+ Alpha points'
  - signals: giveaway_offer ("airdrop claims are live"); claim_cta ("claims are live"); unverified_airdrop_link ("cryptovka.com")
- **r271** gold `none` → pred `unverified-airdrop` (score 3.0) — 'You can actually collect free crypto coins while driving in Car Simulator 2. Learn where the secret chests hid'
  - signals: giveaway_offer ("free crypto"); very_new_account ("6.4 days old")
- **r001** gold `none` → pred `unverified-airdrop` (score 3.0) — 'Jupiter is distributing tokens to Solana users. Eligible traders can now check their status to claim rewards f'
  - signals: giveaway_offer ("distributing tokens"); very_new_account ("5.9 days old")
