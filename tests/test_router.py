"""Routing rule tests (independent of the detectors)."""

from pylabel import config
from pylabel.models import Signal
from pylabel.router import route


def sig(name, group="text", hard=False):
    weight = config.WEIGHTS.get(name, 0.0)
    return Signal(name=name, group=group, weight=weight, hard=hard)


def test_uncontested_hard_indicator_is_scam():
    decision = route([sig("send_to_receive", hard=True)])
    assert decision.labels == [config.SCAM_LABEL]
    assert decision.hard_indicators == ["send_to_receive"]


def test_contested_hard_indicator_is_downgraded():
    decision = route([sig("send_to_receive", hard=True), sig("scam_warning", "counter")])
    assert decision.labels == []
    assert decision.score == config.DOWNGRADED_HARD_WEIGHT + config.WEIGHTS["scam_warning"]


def test_medium_score_with_airdrop_context_is_review():
    decision = route([sig("giveaway_offer"), sig("connect_wallet"), sig("urgency")])
    assert decision.labels == [config.UNVERIFIED_LABEL]


def test_medium_score_without_airdrop_context_is_not_labeled():
    # High score but nothing promoting an airdrop/giveaway -> label name would be wrong.
    decision = route([sig("very_new_account", "account"), sig("suspicious_tld", "link"),
                      sig("high_return_promise")])
    assert decision.score >= config.MEDIUM_THRESHOLD
    assert decision.labels == []


def test_impersonated_giveaway_combo_is_hard():
    decision = route([sig("impersonation_handle", "account"), sig("giveaway_offer"),
                      sig("claim_cta")])
    assert decision.labels == [config.SCAM_LABEL]
    assert "impersonated_giveaway" in decision.hard_indicators


def test_brand_domain_combo_needs_call_to_action():
    assert route([sig("brand_in_domain", "link"), sig("connect_wallet")]).labels == \
        [config.SCAM_LABEL]
    assert config.SCAM_LABEL not in route([sig("brand_in_domain", "link")]).labels


def test_coordinated_link_forces_review():
    decision = route([sig("coordinated_link", "behavior")])
    assert decision.labels == [config.UNVERIFIED_LABEL]


def test_no_signals_no_label():
    assert route([]).labels == []
