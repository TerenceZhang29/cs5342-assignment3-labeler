"""
Regression tests for the v2 changes (tuned on the real dev split). Each test reproduces the
pattern of the dev post that motivated the change; see ITERATIONS.md "v2".
"""

from datetime import timedelta

from pylabel import config
from pylabel.models import Signal
from pylabel.router import route
from tests.conftest import NOW, make_post

SCAM, REVIEW = config.SCAM_LABEL, config.UNVERIFIED_LABEL


def test_faucet_guide_is_not_send_to_receive(labeler):
    """Real dev r250/r253/r257: 'Click Send me ETH ... to receive faucet tokens'."""
    text = ("Get faucet. Go to www.alchemy.com/faucets/ethereum-sepolia, enter EVM address, "
            "click 'Send me ETH'. You need at least 0.001 $ETH on mainnet to receive faucet tokens.")
    assert labeler.moderate_record(make_post(text, age_days=17)).labels == []


def test_faucet_wording_does_not_excuse_airdrop_farming(labeler):
    """Synthetic dev p056 / real dev r412: real rewards promised -> no faucet exemption."""
    text = "Testnet rewards claimable now via monad-rewards.org, verify your wallet for your airdrop"
    assert labeler.moderate_record(make_post(text)).labels == [REVIEW]


def test_news_about_deepfake_scam_is_not_labeled(labeler):
    """Real dev r273."""
    text = "“How did Coinbase stop deepfake Elon Musk’s promise to double your crypto?” — AMBCrypto"
    assert labeler.moderate_record(make_post(text)).labels == []


def test_first_person_gas_complaint_is_not_upfront_fee(labeler):
    """Real dev r035."""
    text = "Paying $45 in gas fees to claim an $8 airdrop because free money is free money"
    assert SCAM not in labeler.moderate_record(make_post(text)).labels


def test_contested_post_needs_extra_score():
    """Real dev r130: a 'spot the scam' answer quoting several indicators."""
    signals = [Signal("giveaway_offer", "text", config.WEIGHTS["giveaway_offer"]),
               Signal("connect_wallet", "text", config.WEIGHTS["connect_wallet"]),
               Signal("urgency", "text", config.WEIGHTS["urgency"]),
               Signal("scam_warning", "counter", config.WEIGHTS["scam_warning"])]
    assert route(signals).labels == []


def test_account_age_alone_does_not_push_a_post_over_the_threshold():
    """Real dev r001/r271: vague giveaway wording + new account, no concrete risk signal."""
    signals = [Signal("giveaway_offer", "text", config.WEIGHTS["giveaway_offer"]),
               Signal("very_new_account", "account", config.WEIGHTS["very_new_account"])]
    decision = route(signals)
    assert decision.labels == []
    assert "very_new_account" not in {s.name for s in decision.signals}


def test_account_age_still_amplifies_concrete_risk():
    signals = [Signal("giveaway_offer", "text", config.WEIGHTS["giveaway_offer"]),
               Signal("claim_cta", "text", config.WEIGHTS["claim_cta"]),
               Signal("very_new_account", "account", config.WEIGHTS["very_new_account"])]
    assert "very_new_account" in {s.name for s in route(signals).signals}


def test_address_request_is_a_call_to_action(labeler):
    """Synthetic dev p065."""
    text = "Daily ETH giveaway 🎁 Reply with your ETH address and follow to enter!"
    assert labeler.moderate_record(make_post(text, age_days=1)).labels == [REVIEW]


def test_identical_text_campaign_from_old_accounts(labeler):
    """Real dev r215-r227: same text + link from several established accounts."""
    text = ("BTC is knocking on the door again. We are celebrating this comeback moment in "
            "Bitcoin history with a giveaway for the community. 👉 promo-site.example.com")
    labels = [labeler.moderate_record(make_post(text, handle=f"user{i}.bsky.social",
                                                age_days=700, minutes_offset=i)).labels
              for i in range(4)]
    assert labels[2:] == [[REVIEW], [REVIEW]]


def test_identical_text_outside_window_is_not_a_campaign(resources):
    from pylabel.account_signals import CoordinatedLinkTracker
    tracker = CoordinatedLinkTracker()
    text = "A long enough promotional message about a giveaway that repeats word for word here x.example.com"
    hours = config.COORDINATED_TEXT_WINDOW_HOURS + 1
    hits = []
    for i in range(3):
        post = make_post(text, handle=f"u{i}", age_days=700)
        post.post_created_at = NOW + timedelta(hours=hours * i)
        hits.append(tracker.observe(post, resources))
    assert hits == [[], [], []]


def test_kalshi_brand_domain_with_giveaway_link_is_scam(labeler):
    """Real dev r215-r227: brand inside an unofficial domain + call to action."""
    text = "Celebrating with a 1 BTC giveaway 👉 insurance-kalshi.com"
    assert labeler.moderate_record(make_post(text, age_days=700)).labels == [SCAM]


def test_double_crypto_giveaway_is_money_flip(labeler):
    """Real dev r174."""
    text = "Thank you for the 2x crypto giveaway, a game-changing gift! https://tsocial.click"
    assert labeler.moderate_record(make_post(text)).labels == [SCAM]
