"""
End-to-end regression tests: the seven enforcement examples from our policy proposal
(§1.1) must be labeled exactly as the policy says, plus key edge cases.
"""

import json

import pytest

from pylabel import config
from tests.conftest import make_post

SCAM, REVIEW = config.SCAM_LABEL, config.UNVERIFIED_LABEL


@pytest.mark.parametrize("example,text,handle,age,expected", [
    (1, "Send 0.1 ETH to 0x52908400098527886E0F7030069857D2E4169EE7 and we return 0.2 ETH.",
     "promo.bsky.social", 3, [SCAM]),
    (2, "Claim free tokens by entering your wallet recovery phrase.",
     "promo.bsky.social", 3, [SCAM]),
    (3, "Elon is giving away 5,000 BTC! A small verification fee of 0.01 BTC is required.",
     "elonmusk-official.bsky.social", 3, [SCAM]),
    (5, "Connect your wallet to claim free tokens before midnight!",
     "promo.bsky.social", 30, [REVIEW]),
    (6, "Update: the 10M pot is an airdrop. Nothing to claim.",
     "bunkyseal.bsky.social", 900, []),
    (7, "Beware of scammers promising large airdrops if you send them crypto first.",
     "dinosr.bsky.social", 900, []),
])
def test_policy_examples(example, text, handle, age, expected, labeler):
    decision = labeler.moderate_record(make_post(text, handle=handle, age_days=age))
    assert decision.labels == expected, f"Example {example}: {decision.reasons}"


def test_policy_example_4_repeated_link_from_new_accounts(labeler):
    """Example 4: the same unverified airdrop link from several new accounts -> review."""
    url = "https://eth-drop.claims/go"
    labels = [labeler.moderate_record(make_post("gm 👀", handle=f"bot{i}.bsky.social",
                                                age_days=2, links=[url], minutes_offset=i)).labels
              for i in range(4)]
    assert labels[2:] == [[REVIEW], [REVIEW]]


def test_legit_airdrop_from_official_domain_handle(labeler):
    text = "Our airdrop is live! Claim your UNI at app.uniswap.org"
    assert labeler.moderate_record(make_post(text, handle="uniswap.org")).labels == []


def test_scam_warning_quoting_scam_text(labeler):
    text = "If someone tells you to send 1 ETH and you'll get 2 ETH back, it's a scam."
    assert labeler.moderate_record(make_post(text)).labels == []


def test_scammer_reassurance_does_not_dodge(labeler):
    text = "Send 0.1 ETH, receive 0.2 ETH back. Not a scam! Beware of fakes, this is the only real one"
    assert labeler.moderate_record(make_post(text, age_days=2)).labels == [SCAM]


def test_non_crypto_post_is_skipped_by_prefilter(labeler):
    decision = labeler.moderate_record(make_post("Lovely weather for a walk today"))
    assert decision.tier == "skipped" and decision.labels == []


def test_every_label_has_reasons_and_is_queued(tmp_path, labeler):
    labeler.review_queue.path = str(tmp_path / "queue.jsonl")
    decision = labeler.moderate_record(make_post(
        "Claim your $UNI airdrop now at uniswap-airdrop.xyz", handle="uni-fan.bsky.social"))
    assert decision.labels == [SCAM] and decision.reasons
    entries = [json.loads(l) for l in open(tmp_path / "queue.jsonl")]
    assert entries[0]["priority"] == "takedown-review"
    assert entries[0]["event"]["createLabelVals"] == [SCAM]


def test_impersonation_creates_account_referral_not_account_label(labeler):
    labeler.moderate_record(make_post("Giving away 500 BTC, claim now at btc-saylor.live",
                                      handle="saylor-btc.bsky.social", age_days=2))
    priorities = [e["priority"] for e in labeler.review_queue.entries]
    assert "account-referral" in priorities
    referral = next(e for e in labeler.review_queue.entries if e["priority"] == "account-referral")
    assert referral["event"]["$type"].endswith("modEventReport")  # a report, not a label


def test_moderate_post_requires_client(labeler):
    with pytest.raises(RuntimeError):
        labeler.moderate_post("https://bsky.app/profile/x/post/y")
