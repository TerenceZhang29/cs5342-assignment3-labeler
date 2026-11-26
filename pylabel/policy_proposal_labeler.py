"""
Crypto giveaway / airdrop scam labeler — implementation of Group 8's Assignment 2 policy
"Fraudulent Cryptocurrency Giveaway and Airdrop Promotions on Bluesky".

Pipeline (policy §3.2):

    PostRecord ─► prefilter ─► text / link / account / behavior signals ─► counter-signals
               ─► router ─► ["crypto-scam"] | ["unverified-airdrop"] | []
                         └► review queue (Ozone-style JSONL) for every labeled post

Usage:

    # offline (evaluation, no login needed)
    labeler = PolicyProposalLabeler(None, "labeler-inputs")
    decision = labeler.moderate_record(record)          # labels + score + reasons

    # live (same constructor signature as the starter code's AutomatedLabeler)
    labeler = PolicyProposalLabeler(client, "labeler-inputs")
    labels = labeler.moderate_post("https://bsky.app/profile/<handle>/post/<rkey>")
"""

from typing import Iterable, List, Optional

from . import config
from .account_signals import ACCOUNT_DETECTORS, CoordinatedLinkTracker
from .ingest import fetch_post_record
from .link_signals import ShortenerExpander, analyze_links, extract_links
from .models import Decision, PostRecord, Signal
from .prefilter import build_term_pattern, normalize, passes_prefilter
from .resources import Resources
from .review_queue import ReviewQueue
from .router import route
from .text_signals import COUNTER_DETECTORS, TEXT_DETECTORS


class PolicyProposalLabeler:
    """Two-tier crypto giveaway/airdrop scam labeler."""

    def __init__(self, client, input_dir: str, *, expand_links: Optional[bool] = None,
                 review_queue_path: Optional[str] = None,
                 enabled_groups: Optional[Iterable[str]] = None):
        """
        Args:
            client: logged-in `atproto.Client`, or None for offline use.
            input_dir: directory with the reference lists (labeler-inputs/).
            expand_links: follow URL-shortener redirects (network). Defaults to True only
                when a client is given, so offline evaluation never touches the network.
            review_queue_path: if set, review-queue entries are appended to this JSONL file.
            enabled_groups: subset of config.SIGNAL_GROUPS to use (for ablation studies).
        """
        self.client = client
        self.resources = Resources.load(input_dir)
        self.crypto_pattern = build_term_pattern(self.resources.crypto_terms)
        self.expander = ShortenerExpander(enabled=client is not None if expand_links is None
                                          else expand_links)
        self.link_tracker = CoordinatedLinkTracker()
        self.review_queue = ReviewQueue(review_queue_path)
        self.enabled_groups = set(enabled_groups or config.SIGNAL_GROUPS)
        self.api_calls = 0  # Bluesky API calls made by moderate_post (for efficiency stats)

    # ------------------------------------------------------------------ public API
    def moderate_post(self, url: str) -> List[str]:
        """Starter-compatible entry point: fetch a live post by URL and return its labels."""
        if self.client is None:
            raise RuntimeError("moderate_post needs a logged-in atproto Client; "
                               "use moderate_record for offline posts.")
        record = fetch_post_record(self.client, url)
        self.api_calls += 2  # getRecord + getProfile
        return self.moderate_record(record).labels

    def moderate_record(self, record: PostRecord) -> Decision:
        """Score one post and return the full decision (labels, tier, score, reasons)."""
        norm = normalize(record.text)
        crypto_context = any(self.crypto_pattern.search(v) for v in norm.views())
        has_links = bool(extract_links(record, self.resources.known_tlds))
        if not passes_prefilter(norm, has_links, self.crypto_pattern):
            return Decision(labels=[], tier="skipped", score=0.0)

        signals = self._collect_signals(record, norm, crypto_context)
        decision = route(signals)
        self.review_queue.add(record, decision)
        return decision

    @property
    def network_calls(self) -> int:
        """Total network requests made so far (API fetches + shortener expansion)."""
        return self.api_calls + self.expander.network_calls

    # ------------------------------------------------------------------ helpers
    def _collect_signals(self, record: PostRecord, norm, crypto_context: bool) -> List[Signal]:
        """Run every enabled detector and return the signals they produce."""
        res = self.resources
        signals: List[Signal] = []
        for detector in TEXT_DETECTORS.values():
            signals.extend(detector(norm, record, res))
        for detector in COUNTER_DETECTORS.values():
            signals.extend(detector(norm, record, res))
        signals.extend(analyze_links(record, res, self.expander, crypto_context))
        for detector in ACCOUNT_DETECTORS.values():
            signals.extend(detector(record, res))
        # Always observe links so the tracker's state does not depend on ablation settings.
        behavior = self.link_tracker.observe(record, res)
        signals.extend(behavior)
        return [s for s in signals if s.group in self.enabled_groups]
