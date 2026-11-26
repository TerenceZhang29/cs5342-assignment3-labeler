"""
pylabel — Group 8's crypto giveaway / airdrop scam labeler.

`label.py` is the course starter code (Bluesky/Ozone helpers). It needs `atproto` and a
`.env`, so it is not imported here; import it explicitly (`from pylabel.label import ...`)
in live scripts. Offline evaluation only needs `PolicyProposalLabeler`.
"""

from .models import Decision, PostRecord, Signal
from .policy_proposal_labeler import PolicyProposalLabeler

__all__ = ["PolicyProposalLabeler", "PostRecord", "Decision", "Signal"]
