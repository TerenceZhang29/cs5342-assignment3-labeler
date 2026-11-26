# Evaluation report — split: `test_real` (111 posts)

Gold label distribution: crypto-scam=10, unverified-airdrop=26, none=75

## Full labeler

Accuracy: **0.559**

| gold \ predicted | crypto-scam | unverified-airdrop | none |
|---|---|---|---|
| **crypto-scam** | 2 | 0 | 8 |
| **unverified-airdrop** | 0 | 13 | 13 |
| **none** | 5 | 23 | 47 |

| label | precision | recall | F1 | support |
|---|---|---|---|---|
| crypto-scam | 0.286 | 0.200 | 0.235 | 10 |
| unverified-airdrop | 0.361 | 0.500 | 0.419 | 26 |
| none | 0.691 | 0.627 | 0.657 | 75 |
| *any label (binary)* | 0.349 | 0.417 | 0.380 | 36 |

Policy targets (§3.3): `crypto-scam` precision ≥ 0.90 → **0.286** (NOT met); recall proxy (any label on harmful posts) ≥ 0.80 → **0.417** (NOT met).

## Baseline and ablations

Keyword baseline = label every post containing a crypto-promotion keyword (the 'blocking crypto keywords' alternative rejected in policy §3.5).

| system | accuracy | macro F1 | scam P | scam R | any-label P | any-label R |
|---|---|---|---|---|---|---|
| keyword baseline | 0.324 | 0.238 | 0.123 | 1.000 | 0.395 | 0.889 |
| text only | 0.613 | 0.312 | 0.125 | 0.100 | 0.250 | 0.083 |
| text + counter | 0.640 | 0.325 | 0.167 | 0.100 | 0.333 | 0.083 |
| text + counter + link | 0.721 | 0.532 | 0.286 | 0.200 | 0.619 | 0.361 |
| + account | 0.559 | 0.437 | 0.286 | 0.200 | 0.349 | 0.417 |
| full (+ behavior) | 0.559 | 0.437 | 0.286 | 0.200 | 0.349 | 0.417 |

## Accuracy by category

| category | n | correct | accuracy | mistakes (gold→pred) |
|---|---|---|---|---|
| real/crypto-scam | 10 | 2 | 0.20 | r226: crypto-scam→none, r224: crypto-scam→none, r223: crypto-scam→none, r221: crypto-scam→none, r220: crypto-scam→none, r219: crypto-scam→none, r217: crypto-scam→none, r216: crypto-scam→none |
| real/none | 75 | 47 | 0.63 | r259: none→unverified-airdrop, r258: none→crypto-scam, r255: none→crypto-scam, r252: none→crypto-scam, r177: none→unverified-airdrop, r505: none→unverified-airdrop, r520: none→unverified-airdrop, r213: none→unverified-airdrop, r210: none→unverified-airdrop, r398: none→unverified-airdrop, r512: none→unverified-airdrop, r558: none→unverified-airdrop, r126: none→unverified-airdrop, r109: none→unverified-airdrop, r025: none→unverified-airdrop, r274: none→crypto-scam, r454: none→unverified-airdrop, r013: none→unverified-airdrop, r450: none→unverified-airdrop, r151: none→unverified-airdrop, r150: none→unverified-airdrop, r446: none→unverified-airdrop, r340: none→unverified-airdrop, r442: none→unverified-airdrop, r142: none→unverified-airdrop, r053: none→unverified-airdrop, r418: none→unverified-airdrop, r311: none→crypto-scam |
| real/unverified-airdrop | 26 | 13 | 0.50 | r195: unverified-airdrop→none, r194: unverified-airdrop→none, r499: unverified-airdrop→none, r530: unverified-airdrop→none, r526: unverified-airdrop→none, r519: unverified-airdrop→none, r578: unverified-airdrop→none, r401: unverified-airdrop→none, r076: unverified-airdrop→none, r124: unverified-airdrop→none, r123: unverified-airdrop→none, r018: unverified-airdrop→none, r051: unverified-airdrop→none |

## Efficiency (offline mode)

- Resource load (incl. 119,002-domain MetaMask blocklist): 302 ms, peak 20.0 MB
- Per-post latency: mean 1.052 ms, median 1.076 ms, p95 1.578 ms, max 5.111 ms
- Extra peak memory while scoring all posts: 12337 KB
- Network calls: 0 (live mode adds 2 API calls per post + up to 5 HEAD requests per shortened link)
- Posts dropped by prefilter: 2/111
- Behavior blocklist at end of stream: ['eth-drop.claims/go']

## Errors

- **r259** gold `none` → pred `unverified-airdrop` (score 4.0) — '4/ Claim USDT & USDC\n\n⭕✨ Go to https://discord.gg/HAuVnEC7aq\n\n➖ Verify yourself\n\n➖ Go to #faucet channel and s'
  - signals: giveaway_offer ("claim usdt"); unverified_airdrop_link ("discord.gg"); very_new_account ("4.1 days old")
- **r258** gold `none` → pred `crypto-scam` (score 9.0) — "2/ Claim faucet\n\n⭕✨ Go to : https://www.alchemy.com/faucets/ethereum-sepolia\n\n➖ Click 'Signin'\n\n➖ Enter EVM ad"
  - signals: send_to_receive ("send me eth' 👉 you need at least 0.001 $eth on the mainne..."); giveaway_offer ("receive faucet tokens"); unverified_airdrop_link ("www.alchemy.com"); very_new_account ("5.1 days old")
- **r255** gold `none` → pred `crypto-scam` (score 7.5) — "2/ Unofficial faucet\n\n⭕✨ Go to : www.alchemy.com/faucets/bas...\n\n➖ Click 'Signin'\n\n➖ Enter EVM address\n\n➖ Comp"
  - signals: send_to_receive ("send me eth' 👉 you need at least 0.001 $eth on the base m..."); giveaway_offer ("receive faucet tokens"); new_account ("20 days old")
- **r252** gold `none` → pred `crypto-scam` (score 6.5) — "2/ Get faucet\n\n⭕✨ Go to : www.alchemy.com/faucets/eth...\n\n➖ Click 'Signin'\n\n➖ Enter EVM address\n\n➖ Complete ca"
  - signals: send_to_receive ("send me eth' 👉 you need at least 0.001 $eth on the mainne..."); giveaway_offer ("receive faucet tokens")
- **r195** gold `unverified-airdrop` → pred `none` (score 1.0) — 'Little Pepe Mega Giveaway wn.nr/SmHhUZd'
  - signals: unverified_airdrop_link ("wn.nr")
- **r194** gold `unverified-airdrop` → pred `none` (score 1.0) — 'Little Pepe Mega Giveaway wn.nr/SmHhUZd'
  - signals: unverified_airdrop_link ("wn.nr")
- **r499** gold `unverified-airdrop` → pred `none` (score -2.0) — 'Airdrop Link: Tinyurl.com/bd9m86mj\nBeware of scams & phishing attempts. Always DYOR. Airdrops & crypto mining '
  - signals: scam_warning ("beware"); shortened_link ("tinyurl.com"); unverified_airdrop_link ("tinyurl.com")
- **r530** gold `unverified-airdrop` → pred `none` (score 2.5) — '🚀 Join the Spores x MST Blockchain Presale Boosting Giveaway!  \nComplete tasks, boost engagement, and win:\n⭐ 5'
  - signals: giveaway_offer ("win: ⭐ 50 winners get $usdt"); unverified_airdrop_link ("wn.nr")
- **r526** gold `unverified-airdrop` → pred `none` (score 2.5) — 'AiMASH Exclusive Airdrop Campaign wn.nr/PErPQRc'
  - signals: unverified_airdrop_link ("wn.nr"); very_new_account ("0.0 days old")
- **r177** gold `none` → pred `unverified-airdrop` (score 3.5) — '$100 Sol giveaway \n\n🔸 Follow me \n🔸 Like & RT this post \n🔸Tag 2 friends\n\n#BTC #Sol #BNB #ETH #ADA #Dot #XRP #TR'
  - signals: giveaway_offer ("$100 sol giveaway"); impersonation_handle ("@binancearmy.bsky.social ~ Binance")
- **r505** gold `none` → pred `unverified-airdrop` (score 3.5) — 'Check gas fees on crypto airdrops. Focuses on checking gas fees when claiming airdrops without deposit verific'
  - signals: giveaway_offer ("claiming airdrops"); unverified_airdrop_link ("wakeuptocrypto.com"); new_account ("14 days old")
- **r520** gold `none` → pred `unverified-airdrop` (score 3.5) — 'Bitget exchange offers up to $500 in NVIDIA stock and crypto rewards Bitget announced August promotions giving'
  - signals: giveaway_offer ("free uni tokens"); unverified_airdrop_link ("cryptocycleindex.com"); new_account ("25 days old")
- **r519** gold `unverified-airdrop` → pred `none` (score 1.0) — 'AiMASH Exclusive Airdrop Campaign wn.nr/MnBRwZh'
  - signals: unverified_airdrop_link ("wn.nr")
- **r226** gold `crypto-scam` → pred `none` (score 2.5) — '🚨 BTC is knocking on the $80K door.\n\nWe’re marking this comeback moment in Bitcoin history. 🔥\n\nAfter the swing'
  - signals: giveaway_offer ("1 btc giveaway"); unverified_airdrop_link ("insurance-kalshi.com")
- **r224** gold `crypto-scam` → pred `none` (score 2.5) — '🚨 BTC is knocking on the $80K door.\n\nWe’re marking this comeback moment in Bitcoin history. 🔥\n\nAfter the swing'
  - signals: giveaway_offer ("1 btc giveaway"); unverified_airdrop_link ("insurance-kalshi.com")
- **r223** gold `crypto-scam` → pred `none` (score 2.5) — '🚨 BTC is knocking on the $80K door.\n\nWe’re marking this comeback moment in Bitcoin history. 🔥\n\nAfter the swing'
  - signals: giveaway_offer ("1 btc giveaway"); unverified_airdrop_link ("insurance-kalshi.com")
- **r221** gold `crypto-scam` → pred `none` (score 2.5) — '🚨 BTC is knocking on the $80K door.\n\nWe’re marking this comeback moment in Bitcoin history. 🔥\n\nAfter the swing'
  - signals: giveaway_offer ("1 btc giveaway"); unverified_airdrop_link ("insurance-kalshi.com")
- **r220** gold `crypto-scam` → pred `none` (score 2.5) — '🚨 BTC is knocking on the $80K door.\n\nWe’re marking this comeback moment in Bitcoin history. 🔥\n\nAfter the swing'
  - signals: giveaway_offer ("1 btc giveaway"); unverified_airdrop_link ("insurance-kalshi.com")
- **r219** gold `crypto-scam` → pred `none` (score 2.5) — '🚨 BTC is knocking on the $80K door.\n\nWe’re marking this comeback moment in Bitcoin history. 🔥\n\nAfter the swing'
  - signals: giveaway_offer ("1 btc giveaway"); unverified_airdrop_link ("insurance-kalshi.com")
- **r217** gold `crypto-scam` → pred `none` (score 2.5) — '🚨 BTC is knocking on the $80K door.\n\nWe’re marking this comeback moment in Bitcoin history. 🔥\n\nAfter the swing'
  - signals: giveaway_offer ("1 btc giveaway"); unverified_airdrop_link ("insurance-kalshi.com")
- **r216** gold `crypto-scam` → pred `none` (score 2.5) — '🚨 BTC is knocking on the $80K door.\n\nWe’re marking this comeback moment in Bitcoin history. 🔥\n\nAfter the swing'
  - signals: giveaway_offer ("1 btc giveaway"); unverified_airdrop_link ("insurance-kalshi.com")
- **r213** gold `none` → pred `unverified-airdrop` (score 4.0) — 'Spin-and-win game winners get BTC. You can join the fun at thrill.com with code YOURMOM for a chance to win bi'
  - signals: giveaway_offer ("win game winners get btc"); unverified_airdrop_link ("thrill.com"); very_new_account ("3.8 days old")
- **r578** gold `unverified-airdrop` → pred `none` (score 0.0) — 'Yakkamon — новый Free Mint на Ronin! Попади в экосистему от создателей Sunflower Land. Всего 10k NFT, низкий п'
  - signals: (none)
- **r210** gold `none` → pred `unverified-airdrop` (score 4.0) — 'Place.bet is a crypto-focused online gaming and casino platform. The pre-launch platform at play.place.bet let'
  - signals: giveaway_offer ("1 btc giveaway"); unverified_airdrop_link ("place.bet"); very_new_account ("0.0 days old")
- **r401** gold `unverified-airdrop` → pred `none` (score 2.5) — 'Sleepagotchi Loyalty Airdrop Event is Now Live! 🩶 | Project Raised $3.5M Funding & Backed by Shima Capital, Al'
  - signals: giveaway_offer ("airdrop event is now"); unverified_airdrop_link ("da.gd")
- **r398** gold `none` → pred `unverified-airdrop` (score 6.0) — '1. Go to → qms.finance/news/welcome...\n\n2. Add QMS Testnet to your wallet\n\n3. Claim free test tokens from the '
  - signals: giveaway_offer ("claim free test tokens"); claim_cta ("claim free"); suspicious_tld ("testnet.qwap.xyz"); unverified_airdrop_link ("qms.finance"); very_new_account ("0.0 days old")
- **r512** gold `none` → pred `unverified-airdrop` (score 4.0) — 'Sell your TF2 items in minutes.\n\n🔑 Sign in through Steam and see what we pay for every item\n🤝 Accept one trade'
  - signals: giveaway_offer ("get paid in keys or crypto"); unverified_airdrop_link ("tf2.gg"); very_new_account ("0.0 days old")
- **r076** gold `unverified-airdrop` → pred `none` (score 2.5) — '#Airdrop  begins 4PM ET 10/30/26 - access drops only in the StockHyper Discord: discord.gg/NPu8TetrEz'
  - signals: giveaway_offer ("airdrop begins"); unverified_airdrop_link ("discord.gg")
- **r558** gold `none` → pred `unverified-airdrop` (score 3.0) — 'First paid mint is in. 🧾\n\nThe free 100 went in hours. Now NFT #101 minted for 0.0005 BNB (~$0.35) — the first '
  - signals: giveaway_offer ("free 100 went in hours. now nft"); very_new_account ("0.4 days old")
- **r126** gold `none` → pred `unverified-airdrop` (score 3.5) — '⚡ Your meme deserves better than staying in a folder.\nMake it a Solana token with Solsmint.\n0.05 SOL creation\n'
  - signals: giveaway_offer ("free mint, burn, airdrop"); unverified_airdrop_link ("solsmint.com"); new_account ("14 days old")
- **r124** gold `unverified-airdrop` → pred `none` (score 1.5) — '🔥 $GIDO CHAIN IS GETTING MORE INTERESTING! 🔥\n\n⛏️ FREE MINING\n💎 21M Total Supply — reported\n\n🤝 50 GIDO for each'
  - signals: very_new_account ("0.0 days old")
- **r123** gold `unverified-airdrop` → pred `none` (score 1.5) — '$GIDO CHAIN IS GETTING MORE INTERESTING! 🔥\n\n⛏️ FREE MINING\n💎 21M Total Supply — reported\n\n🤝 50 GIDO for each a'
  - signals: very_new_account ("0.0 days old")
- **r109** gold `none` → pred `unverified-airdrop` (score 3.5) — 'Faucet vs airdrop. Two ways to get free crypto\n\nhttps://faucetpayme.com/blog/faucet-vs-airdrop?utm_source=blue'
  - signals: giveaway_offer ("airdrop. two ways to get free crypto"); unverified_airdrop_link ("faucetpayme.com"); new_account ("8 days old")
- **r025** gold `none` → pred `unverified-airdrop` (score 4.5) — ' exchange?\n\nJoin Toobit now and unlock up to $15,000 in welcome rewards! 🎁\n\n👇 Sign up with my invite link and '
  - signals: giveaway_offer ("rewards are limited! ⏳ #crypto"); claim_cta ("claim your"); urgency ("don't miss"); unverified_airdrop_link ("www.toobit.com")
- **r274** gold `none` → pred `crypto-scam` (score 6.0) — 'AI agent diary, day 29: honesty check.\n\nA deepfake promised to double your crypto. I still promise nothing. Th'
  - signals: send_to_receive ("double your crypto"); new_account ("28 days old")
- **r018** gold `unverified-airdrop` → pred `none` (score 2.0) — '🌿 Step into the Enchanted Bonsai Bazaar. Secure exclusive merch & your RWA airdrop. Discover the future of dig'
  - signals: suspicious_tld ("t3kno-logic.xyz"); unverified_airdrop_link ("t3kno-logic.xyz")
- **r454** gold `none` → pred `unverified-airdrop` (score 3.0) — "Muse (Meta's new AI app) is live in Australia 🇦🇺 Sign up free, then within 48 hours open Settings and enter co"
  - signals: giveaway_offer ("get 1 billion bonus tokens"); very_new_account ("0.0 days old")
- **r013** gold `none` → pred `unverified-airdrop` (score 4.0) — 'Treehouse users must claim their TREE airdrop tokens by November 25 before the window closes. Check your walle'
  - signals: giveaway_offer ("claim their tree airdrop"); unverified_airdrop_link ("infosaphere.blogspot.com"); very_new_account ("4.6 days old")
- **r450** gold `none` → pred `unverified-airdrop` (score 3.0) — "Just joined Meta's Muse in Australia? You have 48 hours to add an invite code in Settings. Mine is 1LARBG and "
  - signals: giveaway_offer ("bonus tokens"); very_new_account ("1.1 days old")
- **r151** gold `none` → pred `unverified-airdrop` (score 4.0) — 'STRIPCHAT #TOKENS #STRIPCHAT FREE - Official - StripChat Free Tokens 2026/2027 striptokens.live GET HUGE BONUS'
  - signals: giveaway_offer ("free - official - stripchat free tokens"); suspicious_tld ("striptokens.live"); very_new_account ("0.0 days old")
- **r150** gold `none` → pred `unverified-airdrop` (score 4.0) — '#stripchat stripchat tokens free stripchat tokens stripchat free tokens how to get free tokens on stripchat ho'
  - signals: giveaway_offer ("free stripchat tokens"); suspicious_tld ("striptokens.live"); very_new_account ("0.0 days old")
- **r446** gold `none` → pred `unverified-airdrop` (score 5.0) — 'Fresh crypto airdrops are arriving late this November. Learn how to test new apps safely and claim free tokens'
  - signals: giveaway_offer ("claim free tokens"); claim_cta ("claim free"); unverified_airdrop_link ("promptstore.wuaze.com"); very_new_account ("2.8 days old")
- **r340** gold `none` → pred `unverified-airdrop` (score 3.5) — '🔐 Sécurité : la seule adresse officielle est https://startarcoins.com. Aucune « conversion » ni « airdrop » ne'
  - signals: legitimacy_assurance ("only official site"); unverified_airdrop_link ("startarcoins.com"); new_account ("14 days old")
- **r442** gold `none` → pred `unverified-airdrop` (score 4.0) — 'The only real thing on the 17th was a routine one-minute FEMA alert test, announced in advance. Ask what a vir'
  - signals: legitimacy_assurance ("the only real"); unverified_airdrop_link ("ilands.ai"); very_new_account ("1.2 days old")
- **r142** gold `none` → pred `unverified-airdrop` (score 3.5) — 'Coinbase says its AI defences blocked $4.7 million in transfers to a deepfake Elon Musk crypto giveaway, stopp'
  - signals: giveaway_offer ("crypto giveaway"); unverified_airdrop_link ("www.outlookmoney.com"); new_account ("13 days old")
- **r053** gold `none` → pred `unverified-airdrop` (score 3.0) — 'The Linea airdrop is live. Learn how to bridge your assets and complete ecosystem tasks to qualify for token r'
  - signals: giveaway_offer ("airdrop is live"); very_new_account ("2.9 days old")
- **r051** gold `unverified-airdrop` → pred `none` (score 1.5) — '🪂 Live ЕТH Airdrop: Airdroр еligiвiliту снеск live. 🪂 Airdrоp sеasoп is нerе.'
  - signals: giveaway_offer ("eth airdrop")
- **r418** gold `none` → pred `unverified-airdrop` (score 3.0) — 'The ZKsync network has opened its massive token claim for early users. Thousands of eligible wallets are claim'
  - signals: giveaway_offer ("rewards on the blockchain right now. #crypto"); very_new_account ("5.6 days old")
- **r311** gold `none` → pred `crypto-scam` (score 6.5) — 'I build crypto you can check instead of trust.\n\nAll mine, all live:\nZenland: escrow, no middleman\nNYKNYC: wall'
  - signals: credential_request ("seed phrase required"); very_new_account ("0.7 days old")
