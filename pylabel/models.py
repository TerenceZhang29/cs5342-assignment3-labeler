"""Plain data classes shared by every stage of the labeling pipeline."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class PostRecord:
    """
    Everything the labeler needs to know about one post.

    Built either from a row of data.csv (offline evaluation) or from the Bluesky API
    (live mode, see ingest.fetch_post_record).
    """

    text: str
    links: List[str] = field(default_factory=list)  # URLs from facets / link-card embeds
    author_handle: str = ""
    author_display_name: str = ""
    author_did: str = ""
    author_created_at: Optional[datetime] = None
    post_created_at: Optional[datetime] = None
    uri: str = ""  # at:// URI or bsky.app URL; used as the review-queue subject
    cid: str = ""
    post_id: str = ""  # dataset id, for evaluation bookkeeping


@dataclass
class Signal:
    """
    One piece of evidence produced by a detector.

    Attributes:
        name: machine-readable signal name; must be a key in config.WEIGHTS (or a combo).
        group: "text" | "link" | "account" | "behavior" | "counter".
        weight: contribution to the post's score (negative for counter-signals).
        hard: True for hard indicators that route straight to `crypto-scam`.
        evidence: the matched text / domain, shown to reviewers and in the label reason.
    """

    name: str
    group: str
    weight: float
    hard: bool = False
    evidence: str = ""

    def describe(self) -> str:
        """Human-readable one-liner, e.g. `send_to_receive ("send 0.1 eth ... get 0.2")`."""
        return f'{self.name} ("{self.evidence}")' if self.evidence else self.name


@dataclass
class Decision:
    """Final outcome for one post."""

    labels: List[str]
    tier: str  # "scam" | "review" | "none" | "skipped" (failed prefilter)
    score: float
    signals: List[Signal] = field(default_factory=list)
    hard_indicators: List[str] = field(default_factory=list)

    @property
    def reasons(self) -> List[str]:
        """Why this decision was made — attached to the label / review-queue entry."""
        return [s.describe() for s in self.signals]
