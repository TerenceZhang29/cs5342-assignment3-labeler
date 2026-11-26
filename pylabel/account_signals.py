"""
Account and behavior detectors (policy §3.2 step 3c and the "Behavior" row of §3.1).

  * account age (scam campaigns use freshly created accounts)
  * impersonation: handle / display name imitating a prominent figure or project
  * verified project source: post comes from a project's own domain handle (@uniswap.org),
    which the policy's domain-handle nudge treats as the trustworthy channel
  * coordinated links: the same link posted by several *new* accounts is added to a
    behavior-level blocklist, and later posts with it are labeled automatically

Account signals only ever affect the *post's* label. Per policy §3.1 "No account is banned
on automated signals alone": impersonation is sent to the review queue as a referral, never
applied as an account label.
"""

import re
from datetime import datetime, timezone
from typing import Dict, List, Optional, Set

from . import config
from .link_signals import extract_links, is_same_or_subdomain, registrable_domain
from .models import PostRecord, Signal
from .resources import Resources


def _signal(name: str, evidence: str, group: str = "account") -> Signal:
    return Signal(name=name, group=group, weight=config.WEIGHTS[name], evidence=evidence)


def _squash(name: str) -> str:
    """'Elon.Musk_2024' -> 'elonmusk' (lower-case, letters only)."""
    return re.sub(r"[^a-z]", "", (name or "").lower())


def account_age_days(record: PostRecord) -> Optional[float]:
    """Age of the author's account when the post was made (None if unknown)."""
    if record.author_created_at is None:
        return None
    reference = record.post_created_at or datetime.now(timezone.utc)
    return (reference - record.author_created_at).total_seconds() / 86400.0


def detect_account_age(record: PostRecord, res: Resources) -> List[Signal]:
    age = account_age_days(record)
    if age is None:
        return []
    if age < config.VERY_NEW_ACCOUNT_DAYS:
        return [_signal("very_new_account", f"{age:.1f} days old")]
    if age < config.NEW_ACCOUNT_DAYS:
        return [_signal("new_account", f"{age:.0f} days old")]
    return []


def detect_impersonation(record: PostRecord, res: Resources) -> List[Signal]:
    """Handle or display name contains a prominent name but isn't that person's real handle."""
    handle = (record.author_handle or "").lower()
    if detect_verified_project_source(record, res):
        return []  # the project's own domain handle is not an impersonator
    local_part = handle.removesuffix(".bsky.social")
    candidates = [_squash(local_part), _squash(record.author_display_name)]
    for target in res.impersonation_targets:
        if target.canonical_handle and handle == target.canonical_handle:
            continue
        for keyword in target.keywords:
            squashed = _squash(keyword)
            if squashed and any(squashed in c for c in candidates if c):
                return [_signal("impersonation_handle", f"@{handle} ~ {target.name}")]
    return []


def detect_verified_project_source(record: PostRecord, res: Resources) -> List[Signal]:
    """Author's handle is the project's own domain (e.g. @uniswap.org)."""
    handle = (record.author_handle or "").lower()
    if not handle or handle.endswith(".bsky.social"):
        return []
    for domain, project in res.known_project_domains.items():
        if is_same_or_subdomain(handle, registrable_domain(domain)):
            return [_signal("verified_project_source", f"@{handle} ({project})", group="counter")]
    return []


class CoordinatedLinkTracker:
    """
    Behavior-level blocklist (policy §3.1).

    Remembers which new accounts posted each external link. Once a link has been posted by
    `COORDINATED_LINK_MIN_AUTHORS` distinct new accounts it is treated as blocklisted, and
    that post plus every later post containing it gets a `coordinated_link` signal.

    State lives in memory for the lifetime of the labeler (a stream processor in production;
    one pass over data.csv in evaluation, processed in post-time order).
    """

    def __init__(self, min_authors: int = config.COORDINATED_LINK_MIN_AUTHORS):
        self.min_authors = min_authors
        self.authors_by_link: Dict[str, Set[str]] = {}
        self.blocklist: Set[str] = set()
        # v2: identical-text campaigns from accounts of any age.
        self.posts_by_text: Dict[str, List] = {}  # text key -> [(time, author)]
        self.campaign_texts: Set[str] = set()

    @staticmethod
    def _text_key(text: str) -> Optional[str]:
        """Normalized text with URLs/handles/numbers removed; None if too short to compare."""
        key = re.sub(r"https?://\S+|\S+\.\w{2,}/\S*|@\S+|\d+", " ", (text or "").lower())
        key = re.sub(r"[^a-z]+", " ", key).strip()
        return key if len(key) >= config.COORDINATED_TEXT_MIN_CHARS else None

    def _observe_text(self, record: PostRecord, author: str) -> Optional[str]:
        """Flag identical text posted by several distinct accounts within the time window."""
        key = self._text_key(record.text)
        if key is None or not author:
            return None
        when = record.post_created_at
        posts = self.posts_by_text.setdefault(key, [])
        posts.append((when, author))
        if when is not None:
            window = config.COORDINATED_TEXT_WINDOW_HOURS * 3600
            recent = {a for t, a in posts if t is not None and abs((when - t).total_seconds()) <= window}
        else:
            recent = {a for _, a in posts}
        if len(recent) >= config.COORDINATED_TEXT_MIN_AUTHORS:
            self.campaign_texts.add(key)
        return key if key in self.campaign_texts else None

    @staticmethod
    def _key(url: str) -> str:
        key = re.sub(r"^[a-z]+://", "", url.lower()).removeprefix("www.")
        return key.rstrip("/")

    def observe(self, record: PostRecord, res: Resources) -> List[Signal]:
        """Record this post's links and return a signal if any of them is (now) blocklisted."""
        age = account_age_days(record)
        is_new = age is not None and age < config.NEW_ACCOUNT_DAYS
        author = record.author_did or record.author_handle
        hit: Optional[str] = None
        for link in extract_links(record, res.known_tlds):
            if (is_same_or_subdomain(link.host, "bsky.app")
                    or is_same_or_subdomain(link.host, "bsky.social")
                    or any(is_same_or_subdomain(link.host, d) for d in res.known_project_domains)):
                continue
            key = self._key(link.url)
            if is_new and author:
                authors = self.authors_by_link.setdefault(key, set())
                authors.add(author)
                if len(authors) >= self.min_authors:
                    self.blocklist.add(key)
            if key in self.blocklist and hit is None:
                hit = key
        if hit is None:
            text_hit = self._observe_text(record, author) if extract_links(record, res.known_tlds) else None
            if text_hit is None:
                return []
            count = len({a for _, a in self.posts_by_text[text_hit]})
            return [_signal("coordinated_link",
                            f"identical text posted by {count} accounts: '{text_hit[:40]}...'",
                            group="behavior")]
        count = len(self.authors_by_link.get(hit, ()))
        return [_signal("coordinated_link", f"{hit} posted by {count} new accounts",
                        group="behavior")]


ACCOUNT_DETECTORS = {
    "account_age": detect_account_age,
    "impersonation_handle": detect_impersonation,
    "verified_project_source": detect_verified_project_source,
}
