"""
Link detectors (policy §3.2 step 3b).

  * extract URLs/domains from facets, link cards and the text itself (incl. bare domains
    such as "claim-eth.xyz" written without http://)
  * expand URL shorteners (live mode only; HEAD requests, never renders the page)
  * check the MetaMask eth-phishing-detect blocklist (local snapshot)
  * detect counterfeit domains: look-alikes ("un1swap.org"), brand names inside unofficial
    domains ("uniswap-airdrop.xyz"), Unicode homoglyphs ("uniswаp.org") and punycode
  * flag shorteners and throwaway TLDs as weak signals

Google Web Risk (in the original proposal) is not used: it is a paid API. The MetaMask list
plus the heuristics below cover the same ground for crypto phishing specifically.
"""

import re
import unicodedata
from dataclasses import dataclass
from typing import Dict, List, Optional, Set
from urllib.parse import urlparse

from . import config
from .models import PostRecord, Signal
from .resources import Resources

# Second-level public suffixes we care about (a tiny stand-in for the Public Suffix List).
_MULTI_PART_SUFFIXES = {"co.uk", "com.au", "co.jp", "com.br", "co.in", "org.uk", "co.kr"}

# Common TLDs used to recognise bare domains written in post text ("visit eth-gift.xyz").
_COMMON_TLDS = {
    "com", "org", "net", "io", "co", "app", "xyz", "top", "click", "online", "site", "live",
    "icu", "buzz", "cfd", "sbs", "shop", "fun", "rest", "cyou", "claims", "gift", "lol", "mom",
    "pro", "finance", "network", "fi", "ag", "to", "me", "ly", "gg", "info", "biz", "dev",
    "ai", "us", "uk", "de", "social", "link", "club", "vip", "win", "money", "exchange",
    "foundation", "tech", "world", "news", "page", "art", "ee", "at", "id", "gd", "cc", "so",
}

_URL_IN_TEXT = re.compile(r"(?:https?://|www\.)[^\s<>\"')\]]+", re.IGNORECASE)
_BARE_DOMAIN = re.compile(
    r"(?<![@\w.\-/])((?:[\w\-]+\.)+([a-z]{2,12}))(?:/[^\s]*)?(?![\w\-])", re.IGNORECASE
)
_AIRDROP_WORD = re.compile(r"\b(?:airdrop\w*|giveaway\w*|stakedrop|claim\w*)\b")
# Labels shorter than this are too generic for "brand inside domain" matching
# (e.g. "ton" would match "button.com").
_MIN_BRAND_LEN = 6


@dataclass
class LinkInfo:
    """A link found in the post, with its host in both raw and ASCII-skeleton form."""

    url: str
    host: str  # as written (may contain Unicode)
    expanded_from: Optional[str] = None  # shortener host, if this came from expansion


# ---------------------------------------------------------------------------------------
# Domain helpers
# ---------------------------------------------------------------------------------------
def registrable_domain(host: str) -> str:
    """'claim.app.uniswap.org' -> 'uniswap.org'; handles a few multi-part suffixes."""
    parts = host.lower().strip(".").split(".")
    if len(parts) >= 3 and ".".join(parts[-2:]) in _MULTI_PART_SUFFIXES:
        return ".".join(parts[-3:])
    return ".".join(parts[-2:])


def is_same_or_subdomain(host: str, domain: str) -> bool:
    host = host.lower()
    return host == domain or host.endswith("." + domain)


def levenshtein(a: str, b: str) -> int:
    """Classic edit distance (small strings only)."""
    if a == b:
        return 0
    previous = list(range(len(b) + 1))
    for i, char_a in enumerate(a, 1):
        current = [i]
        for j, char_b in enumerate(b, 1):
            current.append(min(previous[j] + 1, current[j - 1] + 1,
                               previous[j - 1] + (char_a != char_b)))
        previous = current
    return previous[-1]


def ascii_skeleton(host: str) -> str:
    """Map Unicode look-alike letters to ASCII ('uniswаp.org' with Cyrillic а -> 'uniswap.org')."""
    from .prefilter import normalize  # local import avoids a cycle at module load

    return normalize(host).plain


def _host_of(url: str) -> str:
    if not re.match(r"^[a-z]+://", url, re.IGNORECASE):
        url = "http://" + url
    try:
        return (urlparse(url).hostname or "").lower()
    except ValueError:
        return ""


# ---------------------------------------------------------------------------------------
# Extraction
# ---------------------------------------------------------------------------------------
def extract_links(record: PostRecord, extra_tlds: Optional[Set[str]] = None) -> List[LinkInfo]:
    """
    Collect every link in the post: facet/embed URLs plus URLs and bare domains in the text.

    Bluesky clients turn typed URLs into facets, but scammers often write domains without
    http:// (or with spaces/brackets) precisely so they are *not* linkified, so the text is
    scanned too.

    `extra_tlds` extends the built-in TLD list; the labeler passes every TLD seen in the
    phishing blocklist and reference lists, so new scam TLDs (".support", ".claims") are
    recognised without code changes.
    """
    tlds = _COMMON_TLDS | (extra_tlds or set())
    seen: Set[str] = set()
    links: List[LinkInfo] = []

    def add(url: str) -> None:
        url = url.rstrip(".,;:!?")
        host = _host_of(url)
        if host and "." in host and host not in seen:
            seen.add(host)
            links.append(LinkInfo(url=url, host=host))

    for url in record.links:
        add(url)
    text = unicodedata.normalize("NFKC", record.text or "")
    # "claim-eth[.]xyz" / "claim-eth (dot) xyz" de-obfuscation.
    text = re.sub(r"\s*(?:\[\.\]|\(\.\)|\(dot\)|\[dot\])\s*", ".", text, flags=re.IGNORECASE)
    for match in _URL_IN_TEXT.finditer(text):
        add(match.group(0))
    for match in _BARE_DOMAIN.finditer(text):
        tld = match.group(2).lower()
        if tld in tlds:
            add(match.group(0))
    return links


# ---------------------------------------------------------------------------------------
# Shortener expansion (live mode only)
# ---------------------------------------------------------------------------------------
class ShortenerExpander:
    """
    Follows redirects of shortened links with HEAD requests (no page bodies are fetched,
    so we never load a phishing page). Results are cached; network calls are counted so
    evaluate.py can report network cost.
    """

    def __init__(self, enabled: bool):
        self.enabled = enabled
        self.cache: Dict[str, str] = {}
        self.network_calls = 0

    def expand(self, url: str) -> str:
        if not self.enabled:
            return url
        if url in self.cache:
            return self.cache[url]
        import requests  # imported lazily so offline mode needs no network stack

        current = url if "://" in url else "https://" + url
        for _ in range(config.SHORTENER_MAX_HOPS):
            try:
                self.network_calls += 1
                response = requests.head(current, allow_redirects=False,
                                         timeout=config.SHORTENER_TIMEOUT_SECONDS)
            except requests.RequestException:
                break
            location = response.headers.get("Location")
            if response.status_code not in (301, 302, 303, 307, 308) or not location:
                break
            current = requests.compat.urljoin(current, location)
        self.cache[url] = current
        return current


# ---------------------------------------------------------------------------------------
# Detectors
# ---------------------------------------------------------------------------------------
def _signal(name: str, evidence: str, hard: bool = False, group: str = "link") -> Signal:
    return Signal(name=name, group=group, weight=config.WEIGHTS[name], hard=hard,
                  evidence=evidence)


def _official_project_for(host: str, res: Resources) -> Optional[str]:
    for domain, project in res.known_project_domains.items():
        if is_same_or_subdomain(host, domain):
            return project
    return None


def _in_blocklist(host: str, res: Resources) -> bool:
    """True if the host or any parent domain is on the MetaMask phishing list."""
    parts = host.split(".")
    for i in range(len(parts) - 1):
        candidate = ".".join(parts[i:])
        if candidate in res.phishing_allowlist:
            return False
        if candidate in res.phishing_blocklist:
            return True
    return False


def _lookalike_target(host: str, res: Resources) -> Optional[str]:
    """
    Return the official domain this host imitates, if any.

    A host imitates `uniswap.org` when its registrable label is within a small edit
    distance of 'uniswap' (typosquat: 'un1swap', 'uniiswap') or identical with a different
    TLD ('uniswap.xyz'), and it is not an official domain itself.
    """
    reg = registrable_domain(host)
    label = reg.split(".")[0]
    for domain in res.known_project_domains:
        official_label = registrable_domain(domain).split(".")[0]
        if len(official_label) < 5 or reg == registrable_domain(domain):
            continue
        allowed = 1 if len(official_label) < 8 else 2
        if levenshtein(label, official_label) <= allowed:
            return domain
    return None


def _brand_inside(host: str, res: Resources) -> Optional[str]:
    """'uniswap-airdrop.xyz' contains the brand 'uniswap' but is not an official domain."""
    labels = re.split(r"[.\-]", registrable_domain(host))
    flat = "".join(labels)
    for domain, project in res.known_project_domains.items():
        brand = registrable_domain(domain).split(".")[0]
        if len(brand) >= _MIN_BRAND_LEN and brand in flat:
            return project
    return None


def analyze_links(record: PostRecord, res: Resources, expander: ShortenerExpander,
                  crypto_context: bool) -> List[Signal]:
    """
    Run every link check and return the resulting signals (at most one per signal name).

    `crypto_context` is True when the text mentions crypto; weak link signals (shortener,
    cheap TLD) only count in that context so that, e.g., a bit.ly link to a recipe is ignored.
    """
    signals: Dict[str, Signal] = {}
    all_official = True
    links = extract_links(record, res.known_tlds)

    for link in links:
        host = link.host
        if is_same_or_subdomain(host, "bsky.app") or is_same_or_subdomain(host, "bsky.social"):
            continue  # internal links (other posts, profiles)
        # Shorteners: flag, then (live mode) expand and analyse the real destination.
        if registrable_domain(host) in res.shorteners or host in res.shorteners:
            if crypto_context:
                signals.setdefault("shortened_link", _signal("shortened_link", host))
            expanded_host = _host_of(expander.expand(link.url))
            if expanded_host and expanded_host != host:
                host = expanded_host
            else:
                all_official = False
                continue

        skeleton = ascii_skeleton(host)
        if host.startswith("xn--") or ".xn--" in host:
            signals.setdefault("punycode_domain", _signal("punycode_domain", host))
        if skeleton != host and _official_project_for(skeleton, res):
            # Unicode look-alike of an official domain: uniswаp.org (Cyrillic а).
            signals.setdefault("homoglyph_domain",
                               _signal("homoglyph_domain", f"{host} ~ {skeleton}", hard=True))
            all_official = False
            continue

        if _official_project_for(host, res):
            continue
        all_official = False

        if _in_blocklist(host, res) or _in_blocklist(skeleton, res):
            signals.setdefault("blocklisted_domain",
                               _signal("blocklisted_domain", host, hard=True))
            continue
        target = _lookalike_target(skeleton, res)
        if target:
            signals.setdefault("lookalike_domain",
                               _signal("lookalike_domain", f"{host} ~ {target}", hard=True))
            continue
        project = _brand_inside(skeleton, res)
        if project:
            signals.setdefault("brand_in_domain", _signal("brand_in_domain", f"{host} ({project})"))
        if crypto_context and skeleton.split(".")[-1] in res.suspicious_tlds:
            signals.setdefault("suspicious_tld", _signal("suspicious_tld", host))

    if not all_official and _AIRDROP_WORD.search(ascii_skeleton(record.text or "")):
        external = [l.host for l in links if not _official_project_for(l.host, res)
                    and not is_same_or_subdomain(l.host, "bsky.app")
                    and not is_same_or_subdomain(l.host, "bsky.social")]
        if external:
            signals["unverified_airdrop_link"] = _signal("unverified_airdrop_link", external[0])
    if links and all_official and crypto_context:
        signals["official_links_only"] = _signal("official_links_only",
                                                 ", ".join(l.host for l in links),
                                                 group="counter")
    return list(signals.values())

