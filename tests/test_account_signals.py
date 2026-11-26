"""Account and behavior detector tests."""

from pylabel import account_signals as acc
from pylabel import config
from tests.conftest import make_post


def test_account_age_buckets(resources):
    assert [s.name for s in acc.detect_account_age(make_post("x", age_days=2), resources)] \
        == ["very_new_account"]
    assert [s.name for s in acc.detect_account_age(make_post("x", age_days=20), resources)] \
        == ["new_account"]
    assert acc.detect_account_age(make_post("x", age_days=400), resources) == []


def test_impersonation_by_handle_and_display_name(resources):
    post = make_post("x", handle="elonmusk-giveaway.bsky.social")
    assert acc.detect_impersonation(post, resources)[0].name == "impersonation_handle"
    post = make_post("x", handle="randomname.bsky.social", display_name="Michael Saylor")
    assert acc.detect_impersonation(post, resources)


def test_canonical_and_official_handles_are_not_impersonators(resources):
    assert acc.detect_impersonation(make_post("x", handle="support.bsky.app"), resources) == []
    assert acc.detect_impersonation(make_post("x", handle="uniswap.org"), resources) == []


def test_verified_project_source(resources):
    signals = acc.detect_verified_project_source(make_post("x", handle="uniswap.org"), resources)
    assert signals and signals[0].group == "counter"
    assert acc.detect_verified_project_source(make_post("x", handle="uniswap.bsky.social"),
                                              resources) == []


def test_coordinated_link_tracker_blocklists_after_threshold(resources):
    tracker = acc.CoordinatedLinkTracker(min_authors=3)
    url = "https://eth-drop.claims/go"
    results = [tracker.observe(make_post("gm", handle=f"bot{i}.bsky.social", age_days=2,
                                         links=[url]), resources) for i in range(4)]
    assert [bool(r) for r in results] == [False, False, True, True]
    # An old account posting the link afterwards is still caught by the blocklist.
    assert tracker.observe(make_post("hi", age_days=900, links=[url]), resources)


def test_coordinated_link_tracker_ignores_old_accounts_and_official_links(resources):
    tracker = acc.CoordinatedLinkTracker(min_authors=2)
    for i in range(3):
        assert tracker.observe(make_post("x", handle=f"old{i}", age_days=900,
                                         links=["https://news.example.com/a"]), resources) == []
        assert tracker.observe(make_post("x", handle=f"new{i}", age_days=1,
                                         links=["https://app.uniswap.org"]), resources) == []
    assert tracker.blocklist == set()


def test_default_threshold_matches_config():
    assert acc.CoordinatedLinkTracker().min_authors == config.COORDINATED_LINK_MIN_AUTHORS
