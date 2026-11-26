"""Link extraction and link detector tests."""

import pytest

from pylabel import link_signals as ls
from tests.conftest import make_post


def link_names(text, resources, links=None, crypto=True):
    expander = ls.ShortenerExpander(enabled=False)
    return {s.name for s in ls.analyze_links(make_post(text, links=links), resources,
                                             expander, crypto)}


def test_registrable_domain():
    assert ls.registrable_domain("claim.app.uniswap.org") == "uniswap.org"
    assert ls.registrable_domain("shop.example.co.uk") == "example.co.uk"


def test_levenshtein():
    assert ls.levenshtein("uniswap", "un1swap") == 1
    assert ls.levenshtein("metamask", "metamaks") == 2
    assert ls.levenshtein("abc", "abc") == 0


@pytest.mark.parametrize("text,host", [
    ("go to https://claim-eth.xyz/now", "claim-eth.xyz"),
    ("visit claim-eth.xyz today", "claim-eth.xyz"),
    ("obfuscated arbitrum-claims[.]xyz here", "arbitrum-claims.xyz"),
    ("bonus 3ton-airdrop.pages.dev", "3ton-airdrop.pages.dev"),
])
def test_extract_links_from_text(text, host, resources):
    hosts = [l.host for l in ls.extract_links(make_post(text), resources.known_tlds)]
    assert host in hosts


def test_extract_links_ignores_amounts_and_mentions(resources):
    text = "send 0.1 eth to @friend.bsky.social, version 2.0 is out"
    assert ls.extract_links(make_post(text), resources.known_tlds) == []


def test_blocklisted_domain_is_hard(resources):
    assert "blocklisted_domain" in link_names("claim at openmsea.io/claim", resources)


def test_typosquat_is_lookalike(resources):
    assert "lookalike_domain" in link_names("airdrop at un1swap.org", resources)
    assert "lookalike_domain" in link_names("update metamaks.io", resources)


def test_homoglyph_domain(resources):
    url = "https://uniswаp.org/claim"  # Cyrillic а
    assert "homoglyph_domain" in link_names(url, resources, links=[url])


def test_brand_inside_unofficial_domain(resources):
    assert "brand_in_domain" in link_names("claim at uniswap-airdrop.xyz", resources)


def test_official_domain_is_not_flagged(resources):
    found = link_names("claim at app.uniswap.org", resources)
    assert found == {"official_links_only"}


def test_short_brand_names_do_not_match_substrings(resources):
    # "ton" (TON) must not match "button"
    assert "brand_in_domain" not in link_names("see buttonshop.com", resources)


def test_weak_link_signals_only_in_crypto_context(resources):
    assert "shortened_link" in link_names("bit.ly/abc", resources, crypto=True)
    assert link_names("bit.ly/abc", resources, crypto=False) == set()


def test_unverified_airdrop_link(resources):
    assert "unverified_airdrop_link" in link_names("airdrop live: pepe2drop.xyz", resources)


def test_shortener_expander_disabled_makes_no_calls():
    expander = ls.ShortenerExpander(enabled=False)
    assert expander.expand("https://bit.ly/x") == "https://bit.ly/x"
    assert expander.network_calls == 0
