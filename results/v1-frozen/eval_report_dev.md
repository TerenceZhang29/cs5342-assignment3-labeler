# Evaluation report — split: `dev` (59 posts)

Gold label distribution: crypto-scam=16, unverified-airdrop=12, none=31

## Full labeler

Accuracy: **0.898**

| gold \ predicted | crypto-scam | unverified-airdrop | none |
|---|---|---|---|
| **crypto-scam** | 14 | 1 | 1 |
| **unverified-airdrop** | 0 | 8 | 4 |
| **none** | 0 | 0 | 31 |

| label | precision | recall | F1 | support |
|---|---|---|---|---|
| crypto-scam | 1.000 | 0.875 | 0.933 | 16 |
| unverified-airdrop | 0.889 | 0.667 | 0.762 | 12 |
| none | 0.861 | 1.000 | 0.925 | 31 |
| *any label (binary)* | 1.000 | 0.821 | 0.902 | 28 |

Policy targets (§3.3): `crypto-scam` precision ≥ 0.90 → **1.000** (met); recall proxy (any label on harmful posts) ≥ 0.80 → **0.821** (met).

## Baseline and ablations

Keyword baseline = label every post containing a crypto-promotion keyword (the 'blocking crypto keywords' alternative rejected in policy §3.5).

| system | accuracy | macro F1 | scam P | scam R | any-label P | any-label R |
|---|---|---|---|---|---|---|
| keyword baseline | 0.508 | 0.371 | 0.344 | 0.688 | 0.625 | 0.714 |
| text only | 0.695 | 0.620 | 0.800 | 0.500 | 0.867 | 0.464 |
| text + counter | 0.729 | 0.647 | 1.000 | 0.500 | 1.000 | 0.464 |
| text + counter + link | 0.831 | 0.775 | 1.000 | 0.812 | 1.000 | 0.679 |
| + account | 0.898 | 0.874 | 1.000 | 0.875 | 1.000 | 0.821 |
| full (+ behavior) | 0.898 | 0.874 | 1.000 | 0.875 | 1.000 | 0.821 |

## Accuracy by category

| category | n | correct | accuracy | mistakes (gold→pred) |
|---|---|---|---|---|
| none/airdrop-discussion | 4 | 4 | 1.00 |  |
| none/ambiguous-terms | 4 | 4 | 1.00 |  |
| none/crypto-talk | 4 | 4 | 1.00 |  |
| none/hard-negative | 1 | 1 | 1.00 |  |
| none/legit-airdrop | 2 | 2 | 1.00 |  |
| none/links | 2 | 2 | 1.00 |  |
| none/new-account | 2 | 2 | 1.00 |  |
| none/non-crypto-giveaway | 4 | 4 | 1.00 |  |
| none/satire | 1 | 1 | 1.00 |  |
| none/victim-question | 2 | 2 | 1.00 |  |
| none/warning | 5 | 5 | 1.00 |  |
| review/connect-urgency | 4 | 4 | 1.00 |  |
| review/coordinated | 2 | 1 | 0.50 | p074: unverified-airdrop→none |
| review/high-return | 1 | 0 | 0.00 | p062: unverified-airdrop→none |
| review/new-account-giveaway | 2 | 2 | 1.00 |  |
| review/telegram | 1 | 1 | 1.00 |  |
| review/unofficial-claim | 1 | 0 | 0.00 | p056: unverified-airdrop→none |
| review/wallet-farming | 1 | 0 | 0.00 | p059: unverified-airdrop→none |
| scam/blocklisted-domain | 2 | 2 | 1.00 |  |
| scam/credential | 1 | 1 | 1.00 |  |
| scam/evasion-homoglyph | 1 | 1 | 1.00 |  |
| scam/evasion-leet | 1 | 1 | 1.00 |  |
| scam/evasion-obfuscated-link | 1 | 1 | 1.00 |  |
| scam/evasion-paraphrase | 1 | 0 | 0.00 | p019: crypto-scam→none |
| scam/impersonation | 3 | 2 | 0.67 | p046: crypto-scam→unverified-airdrop |
| scam/lookalike-domain | 1 | 1 | 1.00 |  |
| scam/send-to-receive | 3 | 3 | 1.00 |  |
| scam/upfront-fee | 2 | 2 | 1.00 |  |

## Efficiency (offline mode)

- Resource load (incl. 119,002-domain MetaMask blocklist): 75 ms, peak 14.7 MB
- Per-post latency: mean 0.447 ms, median 0.296 ms, p95 1.090 ms, max 1.912 ms
- Extra peak memory while scoring all posts: 11973 KB
- Network calls: 0 (live mode adds 2 API calls per post + up to 5 HEAD requests per shortened link)
- Posts dropped by prefilter: 5/59
- Behavior blocklist at end of stream: ['eth-drop.claims/go']

## Errors

- **p019** gold `crypto-scam` → pred `none` (score 1.5) — 'Recovery phrase verification — wallet support team here. Reply with your words and we will restore access to y'
  - signals: very_new_account ("5.0 days old")
- **p046** gold `crypto-scam` → pred `unverified-airdrop` (score 6.0) — 'Ethereum foundation airdrop for long-term holders. Only official link, beware of fakes: eth-foundation-airdrop'
  - signals: legitimacy_assurance ("only official link"); unverified_airdrop_link ("eth-foundation-airdrop.com"); very_new_account ("3.0 days old"); impersonation_handle ("@vitalik-eth-official.bsky.social ~ Vitalik Buterin")
- **p056** gold `unverified-airdrop` → pred `none` (score 2.5) — 'Airdrop hunters: Monad testnet rewards claimable now via monad-rewards.org — verify your wallet to see your al'
  - signals: connect_wallet ("verify your wallet"); unverified_airdrop_link ("monad-rewards.org")
- **p059** gold `unverified-airdrop` → pred `none` (score 1.5) — 'Drop your SOL address below for a free airdrop 👇 like + repost to qualify'
  - signals: giveaway_offer ("free airdrop")
- **p062** gold `unverified-airdrop` → pred `none` (score 2.5) — 'Staking pool airdrop: guaranteed returns of 3% daily for early depositors. Claim your spot now'
  - signals: claim_cta ("claim your"); high_return_promise ("guaranteed returns")
- **p074** gold `unverified-airdrop` → pred `none` (score 2.0) — 'this is actually paying out lol eth-drop.claims/go'
  - signals: satire ("lol"); suspicious_tld ("eth-drop.claims"); unverified_airdrop_link ("eth-drop.claims"); very_new_account ("1.0 days old")
