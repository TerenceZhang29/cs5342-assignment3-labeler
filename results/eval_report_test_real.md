# Evaluation report — split: `test_real` (111 posts)

Gold label distribution: crypto-scam=10, unverified-airdrop=26, none=75

## Full labeler

Accuracy: **0.721**

| gold \ predicted | crypto-scam | unverified-airdrop | none |
|---|---|---|---|
| **crypto-scam** | 10 | 0 | 0 |
| **unverified-airdrop** | 0 | 17 | 9 |
| **none** | 1 | 21 | 53 |

| label | precision | recall | F1 | support |
|---|---|---|---|---|
| crypto-scam | 0.909 | 1.000 | 0.952 | 10 |
| unverified-airdrop | 0.447 | 0.654 | 0.531 | 26 |
| none | 0.855 | 0.707 | 0.774 | 75 |
| *any label (binary)* | 0.551 | 0.750 | 0.635 | 36 |

Policy targets (§3.3): `crypto-scam` precision ≥ 0.90 → **0.909** (met); recall proxy (any label on harmful posts) ≥ 0.80 → **0.750** (NOT met).

## Baseline and ablations

Keyword baseline = label every post containing a crypto-promotion keyword (the 'blocking crypto keywords' alternative rejected in policy §3.5).

| system | accuracy | macro F1 | scam P | scam R | any-label P | any-label R |
|---|---|---|---|---|---|---|
| keyword baseline | 0.324 | 0.238 | 0.123 | 1.000 | 0.395 | 0.889 |
| text only | 0.640 | 0.401 | 0.125 | 0.100 | 0.421 | 0.222 |
| text + counter | 0.712 | 0.444 | 0.500 | 0.100 | 0.727 | 0.222 |
| text + counter + link | 0.739 | 0.764 | 0.909 | 1.000 | 0.574 | 0.750 |
| + account | 0.721 | 0.752 | 0.909 | 1.000 | 0.551 | 0.750 |
| full (+ behavior) | 0.721 | 0.752 | 0.909 | 1.000 | 0.551 | 0.750 |

## Accuracy by category

| category | n | correct | accuracy | mistakes (gold→pred) |
|---|---|---|---|---|
| real/crypto-scam | 10 | 10 | 1.00 |  |
| real/none | 75 | 53 | 0.71 | r188: none→unverified-airdrop, r538: none→unverified-airdrop, r177: none→unverified-airdrop, r505: none→unverified-airdrop, r213: none→unverified-airdrop, r210: none→unverified-airdrop, r398: none→unverified-airdrop, r086: none→unverified-airdrop, r512: none→unverified-airdrop, r127: none→unverified-airdrop, r126: none→unverified-airdrop, r392: none→unverified-airdrop, r029: none→unverified-airdrop, r026: none→unverified-airdrop, r109: none→unverified-airdrop, r025: none→unverified-airdrop, r013: none→unverified-airdrop, r151: none→unverified-airdrop, r150: none→unverified-airdrop, r446: none→unverified-airdrop, r340: none→unverified-airdrop, r311: none→crypto-scam |
| real/unverified-airdrop | 26 | 17 | 0.65 | r195: unverified-airdrop→none, r194: unverified-airdrop→none, r499: unverified-airdrop→none, r526: unverified-airdrop→none, r519: unverified-airdrop→none, r578: unverified-airdrop→none, r124: unverified-airdrop→none, r123: unverified-airdrop→none, r051: unverified-airdrop→none |

## Efficiency (offline mode)

- Resource load (incl. 119,002-domain MetaMask blocklist): 300 ms, peak 20.0 MB
- Per-post latency: mean 1.203 ms, median 1.309 ms, p95 1.820 ms, max 4.987 ms
- Extra peak memory while scoring all posts: 12400 KB
- Network calls: 0 (live mode adds 2 API calls per post + up to 5 HEAD requests per shortened link)
- Posts dropped by prefilter: 2/111
- Behavior blocklist at end of stream: ['eth-drop.claims/go']

## Errors

- **r195** gold `unverified-airdrop` → pred `none` (score 1.0) — 'Little Pepe Mega Giveaway wn.nr/SmHhUZd'
  - signals: unverified_airdrop_link ("wn.nr")
- **r194** gold `unverified-airdrop` → pred `none` (score 1.0) — 'Little Pepe Mega Giveaway wn.nr/SmHhUZd'
  - signals: unverified_airdrop_link ("wn.nr")
- **r188** gold `none` → pred `unverified-airdrop` (score 2.5) — 'airdrop, free mint, giveaway, $SOL, $ETH, $BTC, pump, moonshot, 100x, gem, presale, whitelist, WL spot, alpha '
  - signals: giveaway_offer ("airdrop, free mint, giveaway, $sol"); unverified_airdrop_link ("x.com")
- **r538** gold `none` → pred `unverified-airdrop` (score 2.5) — 'BTCC partners with Argentine Football Association (AFA) for "Legends" campaign, uniting digital finance & spor'
  - signals: giveaway_offer ("giveaway! ⚽️ 💰 #btcc #afa #crypto"); unverified_airdrop_link ("cryptovka.com")
- **r499** gold `unverified-airdrop` → pred `none` (score -2.0) — 'Airdrop Link: Tinyurl.com/bd9m86mj\nBeware of scams & phishing attempts. Always DYOR. Airdrops & crypto mining '
  - signals: scam_warning ("beware"); shortened_link ("tinyurl.com"); unverified_airdrop_link ("tinyurl.com")
- **r526** gold `unverified-airdrop` → pred `none` (score 1.0) — 'AiMASH Exclusive Airdrop Campaign wn.nr/PErPQRc'
  - signals: unverified_airdrop_link ("wn.nr")
- **r177** gold `none` → pred `unverified-airdrop` (score 3.5) — '$100 Sol giveaway \n\n🔸 Follow me \n🔸 Like & RT this post \n🔸Tag 2 friends\n\n#BTC #Sol #BNB #ETH #ADA #Dot #XRP #TR'
  - signals: giveaway_offer ("$100 sol giveaway"); impersonation_handle ("@binancearmy.bsky.social ~ Binance")
- **r505** gold `none` → pred `unverified-airdrop` (score 2.5) — 'Check gas fees on crypto airdrops. Focuses on checking gas fees when claiming airdrops without deposit verific'
  - signals: giveaway_offer ("claiming airdrops"); unverified_airdrop_link ("wakeuptocrypto.com")
- **r519** gold `unverified-airdrop` → pred `none` (score 1.0) — 'AiMASH Exclusive Airdrop Campaign wn.nr/MnBRwZh'
  - signals: unverified_airdrop_link ("wn.nr")
- **r213** gold `none` → pred `unverified-airdrop` (score 2.5) — 'Spin-and-win game winners get BTC. You can join the fun at thrill.com with code YOURMOM for a chance to win bi'
  - signals: giveaway_offer ("win game winners get btc"); unverified_airdrop_link ("thrill.com")
- **r578** gold `unverified-airdrop` → pred `none` (score 0.0) — 'Yakkamon — новый Free Mint на Ronin! Попади в экосистему от создателей Sunflower Land. Всего 10k NFT, низкий п'
  - signals: (none)
- **r210** gold `none` → pred `unverified-airdrop` (score 2.5) — 'Place.bet is a crypto-focused online gaming and casino platform. The pre-launch platform at play.place.bet let'
  - signals: giveaway_offer ("1 btc giveaway"); unverified_airdrop_link ("place.bet")
- **r398** gold `none` → pred `unverified-airdrop` (score 6.0) — '1. Go to → qms.finance/news/welcome...\n\n2. Add QMS Testnet to your wallet\n\n3. Claim free test tokens from the '
  - signals: giveaway_offer ("claim free test tokens"); claim_cta ("claim free"); suspicious_tld ("testnet.qwap.xyz"); unverified_airdrop_link ("qms.finance"); very_new_account ("0.0 days old")
- **r086** gold `none` → pred `unverified-airdrop` (score 2.5) — 'Dola AI Presale Launch: Airdrop Claims and October 2026 Listing Plans \n\nDola AI Presale is live today with a 7'
  - signals: giveaway_offer ("750k airdrop"); unverified_airdrop_link ("mwww.coingabbar.com")
- **r512** gold `none` → pred `unverified-airdrop` (score 2.5) — 'Sell your TF2 items in minutes.\n\n🔑 Sign in through Steam and see what we pay for every item\n🤝 Accept one trade'
  - signals: giveaway_offer ("get paid in keys or crypto"); unverified_airdrop_link ("tf2.gg")
- **r127** gold `none` → pred `unverified-airdrop` (score 2.5) — "✅ CALL CLOSED AND GRADED\nA*************'s $**** 5 day call just closed out and they got a +8.4% gain! Graded o"
  - signals: giveaway_offer ("airdrop tokens"); unverified_airdrop_link ("stockhyper.io")
- **r126** gold `none` → pred `unverified-airdrop` (score 2.5) — '⚡ Your meme deserves better than staying in a folder.\nMake it a Solana token with Solsmint.\n0.05 SOL creation\n'
  - signals: giveaway_offer ("free mint, burn, airdrop"); unverified_airdrop_link ("solsmint.com")
- **r124** gold `unverified-airdrop` → pred `none` (score 0.0) — '🔥 $GIDO CHAIN IS GETTING MORE INTERESTING! 🔥\n\n⛏️ FREE MINING\n💎 21M Total Supply — reported\n\n🤝 50 GIDO for each'
  - signals: (none)
- **r123** gold `unverified-airdrop` → pred `none` (score 0.0) — '$GIDO CHAIN IS GETTING MORE INTERESTING! 🔥\n\n⛏️ FREE MINING\n💎 21M Total Supply — reported\n\n🤝 50 GIDO for each a'
  - signals: (none)
- **r392** gold `none` → pred `unverified-airdrop` (score 2.5) — 'Prime handles are strictly first-come, first-served. Once minted, nobody else can ever take it.\n\nHow to claim:'
  - signals: connect_wallet ("connect wallet"); unverified_airdrop_link ("unbanker.com")
- **r029** gold `none` → pred `unverified-airdrop` (score 2.5) — '⛽🟢 Low gas right now\nFast: 0.077131487 gwei  ·  Safe: 0.070119534 gwei\n\nA cheaper time for routine transaction'
  - signals: giveaway_offer ("claim an "airdrop"); unverified_airdrop_link ("t.me")
- **r026** gold `none` → pred `unverified-airdrop` (score 2.5) — '⛽🟢 Low gas right now\nFast: 0.185475413 gwei  ·  Safe: 0.168614012 gwei\n\nA cheaper time for routine transaction'
  - signals: giveaway_offer ("claim an "airdrop"); unverified_airdrop_link ("t.me")
- **r109** gold `none` → pred `unverified-airdrop` (score 2.5) — 'Faucet vs airdrop. Two ways to get free crypto\n\nhttps://faucetpayme.com/blog/faucet-vs-airdrop?utm_source=blue'
  - signals: giveaway_offer ("airdrop. two ways to get free crypto"); unverified_airdrop_link ("faucetpayme.com")
- **r025** gold `none` → pred `unverified-airdrop` (score 4.5) — ' exchange?\n\nJoin Toobit now and unlock up to $15,000 in welcome rewards! 🎁\n\n👇 Sign up with my invite link and '
  - signals: giveaway_offer ("rewards are limited! ⏳ #crypto"); claim_cta ("claim your"); urgency ("don't miss"); unverified_airdrop_link ("www.toobit.com")
- **r013** gold `none` → pred `unverified-airdrop` (score 2.5) — 'Treehouse users must claim their TREE airdrop tokens by November 25 before the window closes. Check your walle'
  - signals: giveaway_offer ("claim their tree airdrop"); unverified_airdrop_link ("infosaphere.blogspot.com")
- **r151** gold `none` → pred `unverified-airdrop` (score 4.0) — 'STRIPCHAT #TOKENS #STRIPCHAT FREE - Official - StripChat Free Tokens 2026/2027 striptokens.live GET HUGE BONUS'
  - signals: giveaway_offer ("free - official - stripchat free tokens"); suspicious_tld ("striptokens.live"); very_new_account ("0.0 days old")
- **r150** gold `none` → pred `unverified-airdrop` (score 4.0) — '#stripchat stripchat tokens free stripchat tokens stripchat free tokens how to get free tokens on stripchat ho'
  - signals: giveaway_offer ("free stripchat tokens"); suspicious_tld ("striptokens.live"); very_new_account ("0.0 days old")
- **r446** gold `none` → pred `unverified-airdrop` (score 3.0) — 'Fresh crypto airdrops are arriving late this November. Learn how to test new apps safely and claim free tokens'
  - signals: giveaway_offer ("claim free tokens"); claim_cta ("claim free"); news_framing ("#cryptonews"); unverified_airdrop_link ("promptstore.wuaze.com"); very_new_account ("2.8 days old")
- **r340** gold `none` → pred `unverified-airdrop` (score 2.5) — '🔐 Sécurité : la seule adresse officielle est https://startarcoins.com. Aucune « conversion » ni « airdrop » ne'
  - signals: legitimacy_assurance ("only official site"); unverified_airdrop_link ("startarcoins.com")
- **r051** gold `unverified-airdrop` → pred `none` (score 1.5) — '🪂 Live ЕТH Airdrop: Airdroр еligiвiliту снеск live. 🪂 Airdrоp sеasoп is нerе.'
  - signals: giveaway_offer ("eth airdrop")
- **r311** gold `none` → pred `crypto-scam` (score 5.0) — 'I build crypto you can check instead of trust.\n\nAll mine, all live:\nZenland: escrow, no middleman\nNYKNYC: wall'
  - signals: credential_request ("seed phrase required")
