"""
Human review queue (policy §3.2 step 4b, §3.1 "Actor" row).

Running a real Ozone instance needs a hosted service, so the queue is written as JSON Lines
whose entries mirror the payload of Ozone's `tools.ozone.moderation.emitEvent`:

  * every labeled post -> a `modEventLabel` entry. `crypto-scam` entries get priority
    "takedown-review" (a human decides on takedown); `unverified-airdrop` entries get "review".
  * suspected impersonators -> a `modEventReport` *referral* on the account. The labeler
    never labels or bans accounts itself (policy: "No account is banned on automated
    signals alone").

A moderator tool (or a script) can replay these entries into Ozone unchanged.
"""

import json
from datetime import datetime, timezone
from typing import Dict, List, Optional

from . import config
from .models import Decision, PostRecord


class ReviewQueue:
    """Collects review entries in memory and optionally appends them to a JSONL file."""

    def __init__(self, path: Optional[str] = None):
        self.path = path
        self.entries: List[Dict] = []

    def _write(self, entry: Dict) -> None:
        self.entries.append(entry)
        if self.path:
            with open(self.path, "a", encoding="utf-8") as handle:
                handle.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def add(self, record: PostRecord, decision: Decision) -> None:
        """Queue a labeled post (and, if relevant, an account referral)."""
        if not decision.labels:
            return
        now = datetime.now(timezone.utc).isoformat()
        priority = "takedown-review" if config.SCAM_LABEL in decision.labels else "review"
        self._write({
            "createdAt": now,
            "priority": priority,
            "subject": {"$type": "com.atproto.repo.strongRef",
                        "uri": record.uri or record.post_id, "cid": record.cid},
            "event": {"$type": "tools.ozone.moderation.defs#modEventLabel",
                      "createLabelVals": decision.labels, "negateLabelVals": [],
                      "comment": "; ".join(decision.reasons)},
            "score": round(decision.score, 2),
            "hardIndicators": decision.hard_indicators,
        })
        if any(s.name == "impersonation_handle" for s in decision.signals):
            self._write({
                "createdAt": now,
                "priority": "account-referral",
                "subject": {"$type": "com.atproto.admin.defs#repoRef",
                            "did": record.author_did, "handle": record.author_handle},
                "event": {"$type": "tools.ozone.moderation.defs#modEventReport",
                          "reportType": "com.atproto.moderation.defs#reasonMisleading",
                          "comment": ("Possible impersonation in crypto giveaway post "
                                      f"{record.uri or record.post_id}. Needs human "
                                      "verification before any account action.")},
            })
