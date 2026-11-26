"""
Turning posts into `PostRecord`s (policy §3.2 step 1).

Two sources:
  * `record_from_row`   — a row of data.csv (offline; no network, no login)
  * `fetch_post_record` — a live bsky.app post URL via the AT Protocol SDK

In production the same `PostRecord` would be built from Jetstream events; the assignment
asks for CSV input, so that is the primary path.
"""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from .models import PostRecord


def parse_time(value: Any) -> Optional[datetime]:
    """Parse an ISO-8601 timestamp ('2025-01-02T03:04:05Z'); None if blank/invalid."""
    if not value or (isinstance(value, float) and value != value):  # NaN from pandas
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None


def parse_links(value: Any) -> List[str]:
    """data.csv stores links as a JSON list; tolerate blanks and a bare URL."""
    if not value or (isinstance(value, float) and value != value):
        return []
    text = str(value).strip()
    if text.startswith("["):
        return [str(u) for u in json.loads(text)]
    return [text]


def record_from_row(row: Dict[str, Any]) -> PostRecord:
    """Build a PostRecord from a data.csv row (see README for the column schema)."""

    def text(key: str) -> str:
        value = row.get(key, "")
        return "" if value is None or (isinstance(value, float) and value != value) else str(value)

    return PostRecord(
        text=text("text"),
        links=parse_links(row.get("links")),
        author_handle=text("author_handle"),
        author_display_name=text("author_display_name"),
        author_did=text("author_did") or text("author_handle"),
        author_created_at=parse_time(row.get("author_created_at")),
        post_created_at=parse_time(row.get("post_created_at")),
        uri=text("post_url"),
        post_id=text("id"),
    )


def _links_from_post_record(value: Any) -> List[str]:
    """Pull link URLs out of a post's rich-text facets and link-card embed."""
    links: List[str] = []
    for facet in getattr(value, "facets", None) or []:
        for feature in getattr(facet, "features", None) or []:
            uri = getattr(feature, "uri", None)
            if uri:
                links.append(uri)
    embed = getattr(value, "embed", None)
    for candidate in (embed, getattr(embed, "media", None)):
        external = getattr(candidate, "external", None)
        if external is not None and getattr(external, "uri", None):
            links.append(external.uri)
    return links


def fetch_post_record(client, url: str) -> PostRecord:
    """
    Fetch a live post by its bsky.app URL and its author's profile (2 API calls).

    Uses the starter code's `post_from_url` helper.
    """
    from .label import post_from_url  # needs atproto + .env; imported only in live mode

    post = post_from_url(client, url)
    handle = url.split("/")[-3]
    profile = client.get_profile(handle)
    value = post.value
    return PostRecord(
        text=getattr(value, "text", "") or "",
        links=_links_from_post_record(value),
        author_handle=getattr(profile, "handle", handle) or handle,
        author_display_name=getattr(profile, "display_name", "") or "",
        author_did=getattr(profile, "did", "") or "",
        author_created_at=parse_time(getattr(profile, "created_at", None)),
        post_created_at=parse_time(getattr(value, "created_at", None)),
        uri=post.uri,
        cid=post.cid,
    )
