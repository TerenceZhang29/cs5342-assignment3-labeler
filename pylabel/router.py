"""
Routing (policy §3.2 step 4): turn a bag of signals into a label decision.

    hard indicator, not contested            -> crypto-scam        (warn + human takedown queue)
    score >= MEDIUM_THRESHOLD and the post
      actually promotes an airdrop/giveaway  -> unverified-airdrop (stays visible, review queue)
    link on the behavior blocklist           -> at least unverified-airdrop
    otherwise                                -> no label

"Contested" means a counter-signal that changes what the hard indicator means — e.g. the
words "send 0.1 ETH, get 0.2 back" inside a post that says "PSA: this is a scam". Contested
hard indicators only add DOWNGRADED_HARD_WEIGHT to the score instead of forcing a label,
which is how scam warnings (policy Example 7) stay unlabeled.
"""

from typing import List

from . import config
from .models import Decision, Signal


def _add_combo_signals(signals: List[Signal]) -> List[Signal]:
    """Derive hard indicators from combinations (config.HARD_COMBOS)."""
    names = {s.name for s in signals}
    has_cta = bool(names & config.CALL_TO_ACTION_SIGNALS)
    derived = []
    for combo_name, required in config.HARD_COMBOS:
        needed = set(required) - {"call_to_action"}
        if needed <= names and ("call_to_action" not in required or has_cta):
            parts = sorted(needed) + (["call_to_action"] if "call_to_action" in required else [])
            derived.append(Signal(name=combo_name, group="combo", weight=0.0, hard=True,
                                  evidence=" + ".join(parts)))
    return signals + derived


def route(signals: List[Signal]) -> Decision:
    """Apply the two-tier routing rules to the signals of one post."""
    signals = _add_combo_signals(signals)
    names = {s.name for s in signals}
    # v2: account age only amplifies posts that already carry a concrete risk signal.
    if not names & config.ACCOUNT_AMPLIFIES:
        signals = [s for s in signals if s.name not in config.ACCOUNT_AGE_SIGNALS]
        names = {s.name for s in signals}
    contested = bool(names & config.CONTESTING_SIGNALS)
    hard = [s for s in signals if s.hard]

    score = 0.0
    for sig in signals:
        if sig.hard and contested:
            score += config.DOWNGRADED_HARD_WEIGHT if sig.group != "combo" else 0.0
        else:
            score += sig.weight

    hard_names = [s.name for s in hard]
    if hard and not contested:
        return Decision(labels=[config.SCAM_LABEL], tier="scam", score=score,
                        signals=signals, hard_indicators=hard_names)

    promotes_airdrop = bool(names & config.AIRDROP_CONTEXT_SIGNALS)
    behavior_blocklisted = "coordinated_link" in names and not contested
    threshold = config.MEDIUM_THRESHOLD + (config.CONTESTED_THRESHOLD_BONUS if contested else 0)
    if behavior_blocklisted or (score >= threshold and promotes_airdrop):
        return Decision(labels=[config.UNVERIFIED_LABEL], tier="review", score=score,
                        signals=signals, hard_indicators=hard_names)

    return Decision(labels=[], tier="none", score=score, signals=signals,
                    hard_indicators=hard_names)
