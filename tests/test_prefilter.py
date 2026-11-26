"""Normalization (evasion handling) and prefilter tests."""

import re

from pylabel.prefilter import build_term_pattern, normalize, passes_prefilter


def test_lowercases_and_collapses_whitespace():
    assert normalize("  Claim   NOW ").plain == "claim now"


def test_strips_zero_width_characters():
    assert normalize("air​drop").plain == "airdrop"


def test_folds_cyrillic_homoglyphs():
    assert normalize("Clаim yоur ЕTH").plain == "claim your eth"  # Cyrillic а, о, Е


def test_undoes_leetspeak_in_folded_view_only():
    norm = normalize("a1rdr0p s33d phr4se")
    assert norm.folded == "airdrop seed phrase"
    assert "a1rdr0p" in norm.plain  # plain view keeps the original token


def test_leetspeak_leaves_numbers_tickers_and_addresses_alone():
    norm = normalize("send 0.1 $eth to 0xabc123def and web3 rocks")
    assert "0.1" in norm.folded
    assert "$eth" in norm.folded
    assert "0xabc123def" in norm.folded
    assert "web3" in norm.folded


def test_joins_spaced_out_letters():
    assert "seedphrase" in normalize("enter your s e e d p h r a s e").folded


def test_term_pattern_matches_whole_words_and_flexible_spacing():
    pattern = build_term_pattern(["seed phrase", "eth"])
    assert pattern.search("your seed-phrase")
    assert pattern.search("1 eth")
    assert not pattern.search("ethernet")


def test_prefilter_keeps_crypto_or_links_and_drops_the_rest():
    pattern = build_term_pattern(["airdrop", "eth"])
    assert passes_prefilter(normalize("new a1rdr0p!"), False, pattern)
    assert passes_prefilter(normalize("look at this"), True, pattern)
    assert not passes_prefilter(normalize("lovely weather today"), False, pattern)
