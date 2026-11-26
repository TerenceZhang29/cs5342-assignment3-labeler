"""
Text normalization and the cheap prefilter (policy §3.2 step 2).

Normalization defeats the evasion tactics listed in the policy's "Anticipate" stage:
  * Unicode look-alikes      "аirdrоp" (Cyrillic а/о)       -> "airdrop"
  * zero-width characters    "air​drop"                -> "airdrop"
  * leetspeak                "a1rdr0p", "s33d phr4se"       -> "airdrop", "seed phrase"
  * spaced-out letters       "a i r d r o p", "f.r.e.e"     -> "airdrop", "free"

Two views of the text are produced:
  * `plain`  — NFKC + homoglyph folding + lower-case. Digits are kept, so amounts such as
               "0.1 ETH" are still readable by the text detectors.
  * `folded` — `plain` with leetspeak undone inside mixed letter/digit tokens and spaced-out
               letters joined. Used for keyword/phrase matching.
"""

import re
import unicodedata
from dataclasses import dataclass
from typing import Iterable, List

# Invisible characters scammers insert to break keyword filters.
_INVISIBLE = dict.fromkeys(map(ord, "​‌‍⁠﻿­᠎"), None)

# Common Cyrillic / Greek characters that render like Latin letters.
_HOMOGLYPHS = str.maketrans({
    "а": "a", "е": "e", "о": "o", "р": "p", "с": "c", "у": "y", "х": "x", "і": "i",
    "ј": "j", "ѕ": "s", "ԁ": "d", "ɡ": "g", "һ": "h", "ӏ": "l", "ո": "n", "ս": "u",
    "А": "a", "В": "b", "Е": "e", "К": "k", "М": "m", "Н": "h", "О": "o", "Р": "p",
    "С": "c", "Т": "t", "Х": "x", "І": "i",
    "α": "a", "ο": "o", "ρ": "p", "ε": "e", "ι": "i", "κ": "k", "ν": "v", "τ": "t",
    "Α": "a", "Β": "b", "Ε": "e", "Ι": "i", "Κ": "k", "Μ": "m", "Ν": "n", "Ο": "o",
    "Ρ": "p", "Τ": "t", "Χ": "x",
})

# Leetspeak substitutions, applied only inside tokens that mix letters and digits/symbols.
_LEET = str.maketrans({"0": "o", "1": "i", "3": "e", "4": "a", "5": "s", "7": "t",
                       "@": "a", "$": "s"})

_MIXED_TOKEN = re.compile(r"[a-z0-9@$]+")
# 4+ single letters separated by spaces/dots/dashes/underscores: "a i r d r o p".
_SPACED_LETTERS = re.compile(r"\b(?:[a-z][ .\-_*]){3,}[a-z]\b")
_WHITESPACE = re.compile(r"\s+")


@dataclass
class NormalizedText:
    """The original text plus the two normalized views described in the module docstring."""

    original: str
    plain: str
    folded: str

    def views(self) -> List[str]:
        """Both views, for detectors that should match either one."""
        return [self.plain, self.folded] if self.folded != self.plain else [self.plain]


def _unleet_token(match: re.Match) -> str:
    """Undo leetspeak in a token only if it mixes letters with digits/symbols.

    "a1rdr0p" -> "airdrop", but "0.1", "2024", "web3" (single digit suffix kept below),
    and wallet addresses ("0x...") are left alone.
    """
    token = match.group(0)
    letters = sum(ch.isalpha() for ch in token)
    others = len(token) - letters
    if letters < 2 or others == 0 or token.startswith("0x"):
        return token
    # Cashtags ("$eth") and @mentions are meaningful as-is.
    if token[0] in "$@" and token[1:].isalpha():
        return token
    # Keep a trailing number like "web3"/"eth2" when the rest is all letters.
    if token[:-1].isalpha() and token[-1].isdigit():
        return token
    return token.translate(_LEET)


def normalize(text: str) -> NormalizedText:
    """Produce the `plain` and `folded` views of a post's text."""
    plain = unicodedata.normalize("NFKC", text or "")
    plain = plain.translate(_INVISIBLE).translate(_HOMOGLYPHS).lower()
    plain = _WHITESPACE.sub(" ", plain).strip()

    folded = _MIXED_TOKEN.sub(_unleet_token, plain)
    folded = _SPACED_LETTERS.sub(lambda m: re.sub(r"[ .\-_*]", "", m.group(0)), folded)
    return NormalizedText(original=text or "", plain=plain, folded=folded)


def build_term_pattern(terms: Iterable[str]) -> re.Pattern:
    """Compile a whole-word regex for a list of terms (multi-word terms allow any spacing)."""
    parts = []
    for term in sorted(set(terms), key=len, reverse=True):
        words = [re.escape(w) for w in term.split()]
        parts.append(r"[\s\-_]*".join(words))
    return re.compile(r"(?<![a-z0-9])(?:" + "|".join(parts) + r")(?![a-z0-9])")


def passes_prefilter(norm: NormalizedText, has_links: bool, crypto_pattern: re.Pattern) -> bool:
    """
    Keep a post for scoring if it has a link or mentions a crypto term (policy §3.2 step 2).

    This is the cheap first stage: at firehose scale the vast majority of posts are dropped
    here with a single regex search, which is why the full scoring can afford to be thorough.
    """
    if has_links:
        return True
    return any(crypto_pattern.search(view) for view in norm.views())
