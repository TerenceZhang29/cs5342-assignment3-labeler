"""
Loads the reference lists in `labeler-inputs/` once at start-up.

Keeping the lists as plain text/CSV files (instead of hard-coding them) lets moderators
update them without touching code — e.g. refreshing the MetaMask blocklist snapshot, or
pre-blocking look-alike domains before a big token launch (policy §3 "Anticipate").
"""

import csv
import os
from dataclasses import dataclass, field
from typing import Dict, List, Set


# Real ccTLDs that mostly appear in posts as file extensions.
_FILE_EXTENSION_TLDS = {"md", "sh", "rs", "py", "js", "ts", "pl", "cs", "so", "zip", "mov"}


def _read_list(path: str) -> List[str]:
    """Read a one-item-per-line file, skipping blanks and `#` comments; lower-cased."""
    items = []
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line and not line.startswith("#"):
                items.append(line.lower())
    return items


def _read_csv(path: str) -> List[Dict[str, str]]:
    """Read a CSV with a header row, skipping `#` comment lines before/inside it."""
    with open(path, encoding="utf-8") as handle:
        lines = [ln for ln in handle if ln.strip() and not ln.lstrip().startswith("#")]
    return list(csv.DictReader(lines))


@dataclass
class ImpersonationTarget:
    """A public figure or project commonly impersonated in giveaway scams."""

    name: str
    canonical_handle: str  # real Bluesky handle, or "" if none known
    keywords: List[str]  # lower-case, separator-free strings to look for in handles


@dataclass
class Resources:
    """All reference data the detectors need."""

    crypto_terms: List[str] = field(default_factory=list)
    urgency_phrases: List[str] = field(default_factory=list)
    shorteners: Set[str] = field(default_factory=set)
    suspicious_tlds: Set[str] = field(default_factory=set)
    known_project_domains: Dict[str, str] = field(default_factory=dict)  # domain -> project
    impersonation_targets: List[ImpersonationTarget] = field(default_factory=list)
    phishing_blocklist: Set[str] = field(default_factory=set)
    phishing_allowlist: Set[str] = field(default_factory=set)
    known_tlds: Set[str] = field(default_factory=set)  # every TLD in the lists above

    @classmethod
    def load(cls, input_dir: str) -> "Resources":
        """Load every list from `input_dir` (the starter code's `labeler-inputs`)."""

        def path(name: str) -> str:
            return os.path.join(input_dir, name)

        targets = [
            ImpersonationTarget(
                name=row["name"],
                canonical_handle=(row.get("canonical_handle") or "").strip().lower(),
                keywords=[k.strip().lower() for k in row["keywords"].split("|") if k.strip()],
            )
            for row in _read_csv(path("prominent_handles.csv"))
        ]
        resources = cls(
            crypto_terms=_read_list(path("crypto_terms.txt")),
            urgency_phrases=_read_list(path("urgency_phrases.txt")),
            shorteners=set(_read_list(path("shorteners.txt"))),
            suspicious_tlds=set(_read_list(path("suspicious_tlds.txt"))),
            known_project_domains={
                row["domain"].strip().lower(): row["project"]
                for row in _read_csv(path("known_project_domains.csv"))
            },
            impersonation_targets=targets,
            phishing_blocklist=set(_read_list(path("metamask_blocklist.txt"))),
            phishing_allowlist=set(_read_list(path("metamask_allowlist.txt"))),
        )
        domains = (resources.phishing_blocklist | resources.phishing_allowlist
                   | set(resources.known_project_domains) | resources.shorteners)
        tlds = {d.rsplit(".", 1)[-1] for d in domains if "." in d}
        # Keep alphabetic TLDs only, minus ones that are usually file extensions in text
        # ("README.md", "install.sh").
        resources.known_tlds = {t for t in tlds if t.isalpha()} - _FILE_EXTENSION_TLDS
        resources.known_tlds |= resources.suspicious_tlds
        return resources
