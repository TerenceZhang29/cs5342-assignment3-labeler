"""
Configuration for the crypto giveaway / airdrop scam labeler.

All tunable numbers live here so they can be adjusted in one place (and, per the policy's
risk assessment §3.6, kept out of public-facing documentation so scammers cannot probe them).

Weights were set on the *dev* split of data.csv only; see ITERATIONS.md for the history.
"""

# --------------------------------------------------------------------------------------
# Label identifiers (policy §3.1 — two-tier labeling)
# --------------------------------------------------------------------------------------
SCAM_LABEL = "crypto-scam"
UNVERIFIED_LABEL = "unverified-airdrop"
NO_LABEL = "none"  # used only in evaluation output; never emitted

ALL_LABELS = [SCAM_LABEL, UNVERIFIED_LABEL]

# Label definitions in the shape Bluesky's labeler service declaration expects
# (app.bsky.labeler.service#policies.labelValueDefinitions). Each label states its reason
# and how to appeal (policy §3.7).
LABEL_DEFINITIONS = [
    {
        "identifier": SCAM_LABEL,
        "severity": "alert",
        "blurs": "content",
        "defaultSetting": "warn",
        "adultOnly": False,
        "locales": [
            {
                "lang": "en",
                "name": "Likely crypto giveaway scam",
                "description": (
                    "This post shows strong signs of a fraudulent crypto giveaway or airdrop "
                    "(e.g. 'send X, get 2X back', a request for your seed/recovery phrase, an "
                    "upfront fee, or a known phishing domain). Real airdrops never ask for your "
                    "recovery phrase or an upfront payment. It has been queued for human "
                    "review. We never contact you by DM. Think this is wrong? Report the label "
                    "to appeal."
                ),
            }
        ],
    },
    {
        "identifier": UNVERIFIED_LABEL,
        "severity": "inform",
        "blurs": "none",
        "defaultSetting": "warn",
        "adultOnly": False,
        "locales": [
            {
                "lang": "en",
                "name": "Unverified airdrop / giveaway",
                "description": (
                    "This post promotes a crypto airdrop or giveaway we could not verify "
                    "(e.g. wallet-connect request with time pressure, unofficial domain, or a "
                    "link shared by many new accounts). It is not confirmed fraud. Check the "
                    "project's official account before connecting a wallet. Report the label "
                    "to appeal."
                ),
            }
        ],
    },
]

# --------------------------------------------------------------------------------------
# Routing thresholds (policy §3.2 step 4)
# --------------------------------------------------------------------------------------
# Score at/above which a post with airdrop/giveaway context gets `unverified-airdrop`.
# v2: lowered 3.0 -> 2.0 after a sweep on the dev splits (real dev accuracy 0.807 -> 0.825,
# any-label recall 0.47 -> 0.79, precision 0.90 -> 0.71). Acceptable because this tier only
# informs and queues for review; it never hides content. See ITERATIONS.md.
MEDIUM_THRESHOLD = 2.0

# When a hard indicator is "contested" by a counter-signal (e.g. it appears inside a scam
# warning), it no longer forces `crypto-scam`; it contributes this weight to the score instead.
DOWNGRADED_HARD_WEIGHT = 2.0

# --------------------------------------------------------------------------------------
# Signal weights. Positive = more suspicious, negative = counter-signal.
# Hard indicators (policy Examples 1-3) are flagged `hard=True` in the signal modules and
# route straight to `crypto-scam` unless contested.
# --------------------------------------------------------------------------------------
WEIGHTS = {
    # --- text (policy §3.2 3a) ---
    "send_to_receive": 5.0,          # hard
    "credential_request": 5.0,       # hard
    "upfront_fee": 5.0,              # hard
    "giveaway_offer": 1.5,
    "claim_cta": 1.0,
    "connect_wallet": 1.5,
    "urgency": 1.0,
    "wallet_address": 1.0,
    "high_return_promise": 1.5,
    "legitimacy_assurance": 1.5,     # "not a scam", "only official one" — scammer tell
    "unofficial_official_claim": 1.0,  # "official airdrop" from a non-domain handle
    "dm_to_claim": 1.0,
    # --- links (policy §3.2 3b) ---
    "blocklisted_domain": 5.0,       # hard
    "lookalike_domain": 5.0,         # hard
    "homoglyph_domain": 5.0,         # hard
    "brand_in_domain": 2.0,
    "shortened_link": 1.0,
    "suspicious_tld": 1.0,
    "punycode_domain": 2.0,
    "unverified_airdrop_link": 1.0,  # airdrop/giveaway post linking to a non-official site
    # --- accounts (policy §3.2 3c) ---
    "very_new_account": 1.5,
    "new_account": 1.0,
    "impersonation_handle": 2.0,
    # --- behavior (policy §3.1 "Behavior" row) ---
    "coordinated_link": 3.0,         # also forces at least `unverified-airdrop`
    # --- counter-signals (policy §1: warnings, discussion, legit airdrops stay allowed) ---
    "scam_warning": -4.0,
    "credential_negation": -4.0,
    "nothing_to_claim": -3.0,
    "reported_speech": -3.0,
    "satire": -1.5,
    "faucet_context": -2.0,          # v2: testnet/faucet guides (real dev r250, r253, r257)
    "news_framing": -2.0,            # v2: news/announcement framing (real dev r273, r539)
    "verified_project_source": -5.0,
    "official_links_only": -1.5,
}

# Combination rules that escalate to a hard indicator (policy Example 3 and "counterfeit
# airdrop sites"). Each entry: (derived signal name, set of required signal names).
HARD_COMBOS = [
    ("impersonated_giveaway", {"impersonation_handle", "giveaway_offer", "call_to_action"}),
    ("brand_domain_claim", {"brand_in_domain", "call_to_action"}),
]
# Signals that count as a "call_to_action" for the combos above.
CALL_TO_ACTION_SIGNALS = {"claim_cta", "connect_wallet", "wallet_address", "dm_to_claim",
                          "unverified_airdrop_link"}

# A post can only receive `unverified-airdrop` if it actually promotes a giveaway/airdrop
# (keeps the label name truthful — policy: "be precise about what you call the labeler").
AIRDROP_CONTEXT_SIGNALS = {"giveaway_offer", "claim_cta", "connect_wallet", "dm_to_claim",
                           "coordinated_link", "unverified_airdrop_link"}

# Counter-signals strong enough to contest (downgrade) a hard text indicator.
CONTESTING_SIGNALS = {"scam_warning", "credential_negation", "reported_speech",
                      "nothing_to_claim", "verified_project_source", "faucet_context"}

# v2: a contested post (e.g. a scam warning that quotes several scam indicators) needs this
# much *extra* score to get `unverified-airdrop` (real dev r130).
CONTESTED_THRESHOLD_BONUS = 3.0

# v2: account-age signals only *amplify* a post that already carries one of these concrete
# risk signals; on their own they over-flag legitimate new accounts (real dev r001, r214,
# r271, r556, r561; on the real test split account signals cut accuracy 0.72 -> 0.56 in v1.1).
ACCOUNT_AMPLIFIES = {"claim_cta", "connect_wallet", "wallet_address", "dm_to_claim",
                     "shortened_link", "suspicious_tld", "brand_in_domain", "punycode_domain",
                     "impersonation_handle", "coordinated_link"}
ACCOUNT_AGE_SIGNALS = {"new_account", "very_new_account"}

# --------------------------------------------------------------------------------------
# Account thresholds
# --------------------------------------------------------------------------------------
VERY_NEW_ACCOUNT_DAYS = 7
NEW_ACCOUNT_DAYS = 30

# Behavior-level blocklist: a link posted by this many *distinct new* accounts is
# blocklisted and later posts containing it are labeled automatically.
COORDINATED_LINK_MIN_AUTHORS = 3

# v2: identical text (+ same link) from this many distinct accounts of ANY age within the
# window is also a coordinated campaign — catches hijacked established accounts (real dev
# r215-r227, the "1 BTC giveaway / insurance-kalshi.com" campaign).
COORDINATED_TEXT_MIN_AUTHORS = 3
COORDINATED_TEXT_WINDOW_HOURS = 48
COORDINATED_TEXT_MIN_CHARS = 60

# --------------------------------------------------------------------------------------
# Network (live mode only; offline evaluation makes zero network calls)
# --------------------------------------------------------------------------------------
SHORTENER_TIMEOUT_SECONDS = 3.0
SHORTENER_MAX_HOPS = 5

# Signal groups — used for ablation studies in evaluate.py.
SIGNAL_GROUPS = ("text", "link", "account", "behavior", "counter")
