"""Text detector tests: each hard indicator, medium indicators and counter-signals."""

import pytest

from pylabel import text_signals as ts
from pylabel.prefilter import normalize
from tests.conftest import make_post


def names(detector, text, resources, handle="someone.bsky.social"):
    return [s.name for s in detector(normalize(text), make_post(text, handle), resources)]


# ---------------------------------------------------------------- hard indicators
@pytest.mark.parametrize("text", [
    "Send 0.1 ETH and receive 0.2 ETH back",
    "Double your crypto with our program",
    "contribute 0.5 ETH and get 1 ETH returned",
    "S3nd 0.2 3TH g3t 0.4 3TH b4ck",
])
def test_send_to_receive_fires(text, resources):
    assert names(ts.detect_send_to_receive, text, resources) == ["send_to_receive"]


def test_send_to_receive_needs_crypto_context(resources):
    assert names(ts.detect_send_to_receive, "send me the doc and I'll return it", resources) == []


@pytest.mark.parametrize("text", [
    "Claim free tokens by entering your wallet recovery phrase",
    "import your seed phrase into the claim portal",
    "DM us your private key so we can whitelist you",
    "Paste your 24 words here",
])
def test_credential_request_fires(text, resources):
    signals = ts.detect_credential_request(normalize(text), make_post(text), resources)
    assert [s.name for s in signals] == ["credential_request"]
    assert signals[0].hard


@pytest.mark.parametrize("text", [
    "Never share your seed phrase with anyone",
    "No legit project will ask you to enter your recovery phrase",
    "Don't type your 12 words into any website",
])
def test_credential_negation_is_a_counter_signal(text, resources):
    assert names(ts.detect_credential_request, text, resources) == ["credential_negation"]


@pytest.mark.parametrize("text", [
    "Pay the 50 USDT activation fee to release your prize",
    "A one-time unlock fee is required before claiming",
    "you must pay a small gas fee of 0.02 ETH first to our wallet",
])
def test_upfront_fee_fires(text, resources):
    assert names(ts.detect_upfront_fee, text, resources) == ["upfront_fee"]


def test_gas_fee_complaint_is_not_upfront_fee(resources):
    assert names(ts.detect_upfront_fee, "Gas fees are insane right now", resources) == []


# ---------------------------------------------------------------- medium indicators
def test_medium_indicators(resources):
    text = "Free $PEPE airdrop is live! Connect your wallet and claim now, only 3 hours left"
    found = {s.name for d in ts.TEXT_DETECTORS.values()
             for s in d(normalize(text), make_post(text), resources)}
    assert {"giveaway_offer", "connect_wallet", "claim_cta", "urgency"} <= found


def test_wallet_address_detected_on_original_case(resources):
    text = "tips: 0x52908400098527886E0F7030069857D2E4169EE7"
    assert names(ts.detect_wallet_address, text, resources) == ["wallet_address"]


def test_official_claim_only_flags_non_domain_handles(resources):
    text = "Official airdrop is live"
    assert names(ts.detect_unofficial_official_claim, text, resources) == ["unofficial_official_claim"]
    assert names(ts.detect_unofficial_official_claim, text, resources, handle="uniswap.org") == []


# ---------------------------------------------------------------- counter-signals
def test_scam_warning(resources):
    assert names(ts.detect_scam_warning, "PSA: this airdrop is a scam", resources) == ["scam_warning"]


def test_scammer_reassurance_is_not_a_warning(resources):
    text = "Not a scam, 100% legit! Beware of fakes, this is the only real giveaway"
    assert names(ts.detect_scam_warning, text, resources) == []
    assert names(ts.detect_legitimacy_assurance, text, resources) == ["legitimacy_assurance"]


@pytest.mark.parametrize("detector,text,expected", [
    (ts.detect_nothing_to_claim, "the 10M pot is an airdrop. Nothing to claim.", "nothing_to_claim"),
    (ts.detect_reported_speech, "Got a DM saying I won 5000 USDT", "reported_speech"),
    (ts.detect_reported_speech, "is this a scam?", "reported_speech"),
    (ts.detect_satire, "send me 1 ETH and I'll send you 2 back /s", "satire"),
])
def test_counter_signals(detector, text, expected, resources):
    assert names(detector, text, resources) == [expected]
