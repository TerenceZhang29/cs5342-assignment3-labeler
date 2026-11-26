"""Shared pytest fixtures."""

import os
import sys
from datetime import datetime, timedelta, timezone

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from pylabel import PolicyProposalLabeler, PostRecord  # noqa: E402
from pylabel.resources import Resources  # noqa: E402

INPUT_DIR = os.path.join(ROOT, "labeler-inputs")
NOW = datetime(2026, 11, 1, 12, 0, tzinfo=timezone.utc)


@pytest.fixture(scope="session")
def resources() -> Resources:
    return Resources.load(INPUT_DIR)


@pytest.fixture
def labeler() -> PolicyProposalLabeler:
    """Fresh offline labeler (fresh coordinated-link state for every test)."""
    return PolicyProposalLabeler(None, INPUT_DIR, expand_links=False)


def make_post(text: str, handle: str = "someone.bsky.social", age_days: float = 400,
              links=None, display_name: str = "", minutes_offset: int = 0) -> PostRecord:
    """Build a PostRecord with an account of the given age."""
    post_time = NOW + timedelta(minutes=minutes_offset)
    return PostRecord(text=text, links=list(links or []), author_handle=handle,
                      author_did=handle, author_display_name=display_name,
                      author_created_at=post_time - timedelta(days=age_days),
                      post_created_at=post_time)
