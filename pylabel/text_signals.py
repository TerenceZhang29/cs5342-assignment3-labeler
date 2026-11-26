"""
Text detectors (policy §3.2 step 3a) and counter-signal detectors (policy §1: scam warnings,
discussion, satire and legitimate airdrops must stay unlabeled).

Every detector is a small function `(norm, record, resources) -> List[Signal]` so it can be
unit-tested on its own and turned on/off for ablation studies.
"""

import re
from typing import Callable, Dict, List, Optional

from . import config
from .models import PostRecord, Signal
from .prefilter import NormalizedText
from .resources import Resources

# ---------------------------------------------------------------------------------------
# Shared vocabulary
# ---------------------------------------------------------------------------------------
_COIN = (r"(?:eth|ether|ethereum|btc|bitcoin|sol|solana|usdt|usdc|bnb|xrp|doge|dogecoin|ton"
         r"|crypto|coins?|tokens?)")
_AMOUNT = re.compile(r"\d+(?:[.,]\d+)?\s*\$?" + _COIN + r"\b")
_WALLET_ADDRESS = re.compile(
    r"\b0x[a-fA-F0-9]{40}\b"                       # Ethereum / EVM
    r"|\bbc1[a-z0-9]{25,59}\b"                      # Bitcoin bech32
    r"|\b[13][a-km-zA-HJ-NP-Z1-9]{25,34}\b"         # Bitcoin legacy
    r"|\bT[1-9A-HJ-NP-Za-km-z]{33}\b"               # TRON
)
_CREDENTIAL = (r"(?:seed[\s\-]?phrase|recovery[\s\-]?phrase|secret(?: recovery)?[\s\-]?phrase"
               r"|mnemonic(?: phrase)?|private[\s\-]?keys?|(?:12|24)[\s\-]?words?(?: phrase)?"
               r"|wallet phrase|passphrase|seed words)")
_NEGATION = re.compile(
    r"\b(?:never|don'?t|dont|do not|no one|nobody|won'?t|will not|shouldn'?t|should never"
    r"|not ask|stop|no legit\w*|no real)\b"
)
# Sentence split that does not break "0.1 eth" or "app.uniswap.org".
_SENTENCE_SPLIT = re.compile(r"(?<![\d\w])[.!?]+|[.!?]+(?=\s|$)|\n")


def _snippet(text: str, match: re.Match, width: int = 60) -> str:
    """Short excerpt of the match for reviewer-facing evidence."""
    snippet = text[match.start():match.end()]
    return snippet if len(snippet) <= width else snippet[: width - 3] + "..."


def _search_views(pattern: re.Pattern, norm: NormalizedText) -> Optional[re.Match]:
    """Search both normalized views; return the first match (and remember which text)."""
    for view in norm.views():
        match = pattern.search(view)
        if match:
            return match
    return None


def _first_evidence(pattern: re.Pattern, norm: NormalizedText) -> Optional[str]:
    for view in norm.views():
        match = pattern.search(view)
        if match:
            return _snippet(view, match)
    return None


def _sentences(text: str) -> List[str]:
    return [s.strip() for s in _SENTENCE_SPLIT.split(text) if s and s.strip()]


def _signal(name: str, group: str, evidence: str = "", hard: bool = False) -> Signal:
    return Signal(name=name, group=group, weight=config.WEIGHTS[name], hard=hard,
                  evidence=evidence)


# ---------------------------------------------------------------------------------------
# Hard indicators (policy Examples 1-3)
# ---------------------------------------------------------------------------------------
_SEND_TO_RECEIVE = re.compile(
    r"\b(?:send|sent|transfer|deposit|contribute)\w*\b.{0,140}?"
    r"\b(?:receive|get back|get \d|gets? \d|sends? back|sent back|send you back|return(?:ed|s)?"
    r"|double[ds]?|2x|x2|triple[ds]?|3x|x3|twice)\b"
)
_DOUBLE_YOUR = re.compile(
    r"\b(?:double|triple|2x|3x|10x) (?:your|ur|the) (?:crypto|eth|ether|btc|bitcoin|ethereum"
    r"|coins?|tokens?|sol|money|investment|deposit)\b"
    # v2: "2x crypto giveaway" / "double BTC giveaway" money-flip phrasing (real dev r174)
    r"|\b(?:2x|x2|3x|double|triple)\s+(?:crypto|eth|btc|bitcoin|ethereum|sol|usdt)?\s*"
    r"(?:giveaway|airdrop|promo|event)\b"
)


def detect_send_to_receive(norm: NormalizedText, record: PostRecord, res: Resources) -> List[Signal]:
    """'Send 0.1 ETH, receive 0.2 ETH' / 'double your crypto' (policy Example 1)."""
    evidence = _first_evidence(_DOUBLE_YOUR, norm)
    if evidence is None:
        match = _search_views(_SEND_TO_RECEIVE, norm)
        # Require crypto context so "send me the doc and I'll return it" doesn't fire.
        has_crypto = _search_views(_AMOUNT, norm) or _WALLET_ADDRESS.search(norm.original)
        if match and has_crypto:
            evidence = _snippet(match.string, match)
    return [_signal("send_to_receive", "text", evidence, hard=True)] if evidence else []


_CREDENTIAL_REQUEST = re.compile(
    r"\b(?:enter|submit|provide|shar|send|type|typ|past|paste|verify|verif|validat|import|input"
    r"|dm|sync|upload|fill(?:ing)? in|give us|drop|confirm|restor)(?:e|es|s|ing|ed|ied|ies)?\b"
    r".{0,60}?\b" + _CREDENTIAL
    + r"|\b" + _CREDENTIAL + r"\b.{0,40}?\b(?:required|needed|to (?:claim|verify|validate|sync"
    r"|receive|unlock|activate|connect))\b"
)


def detect_credential_request(norm: NormalizedText, record: PostRecord, res: Resources) -> List[Signal]:
    """
    Requests for a seed/recovery phrase or private key (policy Example 2).

    Checked sentence by sentence: if the sentence also contains a negation ("never share
    your seed phrase"), it is a warning and produces a `credential_negation` counter-signal
    instead of the hard indicator.
    """
    signals: List[Signal] = []
    for view in norm.views():
        for sentence in _sentences(view):
            match = _CREDENTIAL_REQUEST.search(sentence)
            if not match:
                continue
            if _NEGATION.search(sentence):
                signals.append(_signal("credential_negation", "counter", _snippet(sentence, match)))
            else:
                signals.append(_signal("credential_request", "text", _snippet(sentence, match),
                                       hard=True))
                return signals[-1:]  # one hard hit is enough
    # Also catch the negation phrasing when there's no request verb at all.
    negated = re.compile(r"\b(?:never|don'?t|do not|no one|nobody|no legit\w*)\b.{0,50}?" + _CREDENTIAL)
    if not signals:
        evidence = _first_evidence(negated, norm)
        if evidence:
            signals.append(_signal("credential_negation", "counter", evidence))
    return signals[:1]


_UPFRONT_FEE = re.compile(
    r"\b(?:pay|send|deposit)\b.{0,50}?\bfees?\b.{0,40}?\b(?:to|before|and)\b"
    r"|\bfees?\b.{0,40}?\b(?:to (?:claim|receive|unlock|withdraw|activate|verify|release)"
    r"|required|must be paid|before (?:claiming|withdraw\w*|receiving))\b"
    r"|\b(?:verification|activation|unlock(?:ing)?|registration|withdrawal|release|processing"
    r"|validation|whitelist(?:ing)?) fee\b"
)


# v2: "Paying $45 in gas fees to claim an $8 airdrop" describes an experience, it does not
# request a payment (real dev r035).
_FIRST_PERSON_FEE = re.compile(r"\b(?:paying|paid|spent|spend|spending|i pay|we pay)\b")


def detect_upfront_fee(norm: NormalizedText, record: PostRecord, res: Resources) -> List[Signal]:
    """Requests for an upfront payment to unlock a reward (policy Example 3)."""
    for view in norm.views():
        for match in _UPFRONT_FEE.finditer(view):
            before = view[max(0, match.start() - 30):match.start() + 12]
            if _FIRST_PERSON_FEE.search(before):
                continue
            return [_signal("upfront_fee", "text", _snippet(view, match), hard=True)]
    return []


# ---------------------------------------------------------------------------------------
# Medium indicators (policy Examples 4-5 and §1.2 indicator list)
# ---------------------------------------------------------------------------------------
_GIVEAWAY_OFFER = re.compile(
    r"\b(?:free|claim(?:ing)?|win|winning|get|grab|receive|giving(?: away)?|give away|gifting"
    r"|giveaway"
    r"|airdropp?(?:ing|ed)?|rewards?|bonus|distribut\w+)\b.{0,40}?"
    r"\b(?:\$[a-z]{2,6}|" + _COIN[3:-1] + r"|nfts?|airdrops?)\b"
    r"|\b(?:airdrop|giveaway)s?\b.{0,30}?\b(?:is |are )?(?:live|now|open|started|ongoing|begins"
    r"|here)\b"
    r"|\b(?:eth|btc|bitcoin|crypto|token|nft|usdt|sol)\s+(?:giveaway|airdrop)\b"
    r"|\$?\d[\d,.]*k?\s*(?:usdt|usdc|eth|btc|sol)?\s+(?:giveaway|airdrop)\b"
)
_CLAIM_CTA = re.compile(
    r"\bclaim (?:your|ur|now|here|it|them|free|at|via|before|on|the|yours|today)\b"
    r"|\bclaim (?:link|page|site|portal)\b|\bclaims? (?:is |are )?(?:now )?(?:open|live)\b"
    r"|\b(?:check|verify) (?:your |ur )?eligib\w*"
    r"|\b(?:you are|you're|ur|you r) eligible\b|\blink in (?:bio|profile)\b"
    r"|\bclick (?:here|the link|below|link)\b|\btap (?:here|the link)\b"
    # v2: asking people to post their address publicly (synthetic dev p059, p065)
    r"|\b(?:reply|comment|drop|post|leave|share) (?:with )?(?:your|ur) (?:eth |sol |btc |bnb "
    r"|usdt |evm |wallet |crypto )?(?:wallet )?address(?:es)?\b"
)
_CONNECT_WALLET = re.compile(
    r"\b(?:connect|link|sync|verify|validate|authorize|approve)\s+(?:your |ur |a |the )?"
    r"(?:wallet|metamask|phantom|trust ?wallet|ledger)\b"
)
_URGENCY_EXTRA = re.compile(
    r"\b(?:only|just) \d+ (?:hours?|hrs?|minutes?|mins?|spots?|left)\b"
    r"|\b\d+\s*(?:hours?|hrs?|mins?|minutes?) (?:left|remaining)\b|[⏰⏳]"
)
_HIGH_RETURN = re.compile(
    r"\bguaranteed\b.{0,20}?\b(?:profits?|returns?|income|gains?)\b"
    r"|\b\d{2,4}% (?:daily|weekly|monthly|per day|a day|every day)\b"
    r"|\b(?:10|20|50|100|1000)x (?:your|ur) (?:money|investment|crypto|eth|btc)\b"
    r"|\brisk[- ]free\b.{0,20}?\b(?:profits?|returns?|income)\b"
)
_LEGITIMACY_ASSURANCE = re.compile(
    r"\b(?:not a scam|no scam|not scam|100% legit|100% real|totally legit|legit giveaway"
    r"|real giveaway|this is not fake|not fake|only (?:real|legit|official) (?:one|giveaway"
    r"|airdrop|link|site)|the only real)\b"
)
_OFFICIAL_CLAIM = re.compile(
    r"\bofficial (?:airdrop|giveaway|claim|event|distribution|rewards?|token launch)\b"
)
_DM_TO_CLAIM = re.compile(
    r"\b(?:dm|message|inbox) (?:me|us)\b.{0,30}?\b(?:claim|receive|get|wallet|win|eligible"
    r"|details|address)\b|\bcheck (?:your|ur) (?:dms?|inbox)\b"
)


def _simple_detector(name: str, pattern: re.Pattern) -> Callable:
    """Factory for detectors that are a single regex over the normalized text."""

    def detector(norm: NormalizedText, record: PostRecord, res: Resources) -> List[Signal]:
        evidence = _first_evidence(pattern, norm)
        return [_signal(name, "text", evidence)] if evidence else []

    detector.__name__ = f"detect_{name}"
    detector.__doc__ = f"Fires `{name}` when /{pattern.pattern[:60]}.../ matches."
    return detector


detect_giveaway_offer = _simple_detector("giveaway_offer", _GIVEAWAY_OFFER)
detect_claim_cta = _simple_detector("claim_cta", _CLAIM_CTA)
detect_connect_wallet = _simple_detector("connect_wallet", _CONNECT_WALLET)
detect_high_return_promise = _simple_detector("high_return_promise", _HIGH_RETURN)
detect_legitimacy_assurance = _simple_detector("legitimacy_assurance", _LEGITIMACY_ASSURANCE)
detect_dm_to_claim = _simple_detector("dm_to_claim", _DM_TO_CLAIM)


def detect_urgency(norm: NormalizedText, record: PostRecord, res: Resources) -> List[Signal]:
    """Time-pressure cues from labeler-inputs/urgency_phrases.txt plus countdown patterns."""
    for view in norm.views():
        for phrase in res.urgency_phrases:
            if phrase in view:
                return [_signal("urgency", "text", phrase)]
    evidence = _first_evidence(_URGENCY_EXTRA, norm)
    return [_signal("urgency", "text", evidence)] if evidence else []


def detect_wallet_address(norm: NormalizedText, record: PostRecord, res: Resources) -> List[Signal]:
    """A raw wallet address in the post (case-sensitive, so run on the original text)."""
    match = _WALLET_ADDRESS.search(norm.original)
    if not match:
        return []
    address = match.group(0)
    return [_signal("wallet_address", "text", address[:8] + "..." + address[-4:])]


def detect_unofficial_official_claim(norm: NormalizedText, record: PostRecord,
                                     res: Resources) -> List[Signal]:
    """
    'Official airdrop' claimed by a non-domain handle (*.bsky.social).

    Implements the policy's domain-handle nudge (§3.4): real projects can announce from a
    verified domain handle such as @project.org.
    """
    handle = (record.author_handle or "").lower()
    if not handle.endswith(".bsky.social"):
        return []
    evidence = _first_evidence(_OFFICIAL_CLAIM, norm)
    return [_signal("unofficial_official_claim", "text", evidence)] if evidence else []


# ---------------------------------------------------------------------------------------
# Counter-signals (policy §1: "Legitimate airdrops, ordinary discussion, scam warnings,
# and disclosed promotions remain allowed"; Examples 6-7)
# ---------------------------------------------------------------------------------------
_SCAM_WARNING = re.compile(
    r"\b(?:scams?|scammers?|scamming|scammy|phishing|phish|fraud|fraudulent|fakes?|drainers?"
    r"|beware|psa|warning|heads up|be careful|watch out|stay safe|don'?t fall for"
    r"|do not fall for|don'?t click|do not click|report and block|block and report"
    r"|impersonat\w+|deepfakes?)\b"
)
_NOTHING_TO_CLAIM = re.compile(
    r"\bnothing to claim\b|\bno (?:need|reason) to (?:send|pay|connect|claim)\b"
    r"|\bno claim(?:ing)? (?:needed|necessary|required)\b"
    r"|\b(?:automatically|auto)[- ]?(?:sent|distributed|credited|airdropped)\b"
    r"|\bno action (?:needed|required)\b"
)
_REPORTED_SPEECH = re.compile(
    r"\b(?:got|received|getting|keep getting|i get) (?:a |an |this |these |some |so many )?"
    r"(?:dms?|messages?|emails?|repl(?:y|ies))\b"
    r"|\bsomeone (?:sent|messaged|dmed|is offering|offered|replied)\b"
    r"|\b(?:they|these accounts|this account|bots?|scammers?) (?:ask|asked|want|wants|promise"
    r"|promised|promising|claim|claims|tell|told)\b"
    r"|\bis this (?:a )?(?:scam|legit|real)\b|\banyone (?:else )?(?:get|got|seen|seeing)\b"
)
# v2: faucet guides — the legitimate inverse of a send-to-receive scam (test tokens are free
# and worthless; real dev r250, r253, r257). Only counts when no real reward is promised:
# "testnet rewards claimable, connect wallet" is airdrop farming (synthetic dev p050, p056;
# real dev r412).
_FAUCET = re.compile(r"\b(?:faucets?|test tokens?)\b")
_REAL_REWARD = re.compile(r"\b(?:airdrops?|rewards?|points?|allocation|eligib\w*|tge)\b")
# v2: news / announcement framing (real dev r273, r539).
_NEWS = re.compile(
    r"\b(?:launches|launched|announces|announced|reportedly|according to|reports that"
    r"|headline|press release)\b|#(?:\w*news|deepfakenews)\b|\u2014 [A-Z][\w]+$"
)
_SATIRE = re.compile(r"(?:^|\s)/s\b|\b(?:jk|just kidding|satire|parody|lmao|lmfao|lol)\b|😂|🤣")


def detect_scam_warning(norm: NormalizedText, record: PostRecord, res: Resources) -> List[Signal]:
    """
    Warning / educational language ("PSA", "beware", "this is a scam").

    Scammers often write "not a scam!" or "beware of fakes, this is the only real one" — a
    well-known tell. Those reassurance phrases are removed before looking for warning words,
    so they cannot be used to dodge the labeler.
    """
    for view in norm.views():
        cleaned = _LEGITIMACY_ASSURANCE.sub(" ", view)
        cleaned = re.sub(r"\bbeware of (?:fakes?|copycats?|imposters?|clones?)\b", " ", cleaned) \
            if _LEGITIMACY_ASSURANCE.search(view) else cleaned
        match = _SCAM_WARNING.search(cleaned)
        if match:
            return [_signal("scam_warning", "counter", _snippet(cleaned, match))]
    return []


def _counter_detector(name: str, pattern: re.Pattern) -> Callable:
    def detector(norm: NormalizedText, record: PostRecord, res: Resources) -> List[Signal]:
        evidence = _first_evidence(pattern, norm)
        return [_signal(name, "counter", evidence)] if evidence else []

    detector.__name__ = f"detect_{name}"
    return detector


detect_nothing_to_claim = _counter_detector("nothing_to_claim", _NOTHING_TO_CLAIM)
detect_reported_speech = _counter_detector("reported_speech", _REPORTED_SPEECH)
detect_satire = _counter_detector("satire", _SATIRE)
def detect_faucet_context(norm: NormalizedText, record: PostRecord, res: Resources) -> List[Signal]:
    """Faucet/test-token guide that promises no real reward (see _FAUCET comment)."""
    if any(_REAL_REWARD.search(v) for v in norm.views()):
        return []
    evidence = _first_evidence(_FAUCET, norm)
    return [_signal("faucet_context", "counter", evidence)] if evidence else []


def detect_news_framing(norm: NormalizedText, record: PostRecord, res: Resources) -> List[Signal]:
    """News/announcement framing; checked on the original text so '— Source' casing works."""
    match = _NEWS.search(norm.plain) or _NEWS.search(norm.original.strip())
    return [_signal("news_framing", "counter", match.group(0).strip())] if match else []


# Ordered registry used by the labeler. Keys are only for readability/debugging.
TEXT_DETECTORS: Dict[str, Callable] = {
    "send_to_receive": detect_send_to_receive,
    "credential_request": detect_credential_request,  # may also emit credential_negation
    "upfront_fee": detect_upfront_fee,
    "giveaway_offer": detect_giveaway_offer,
    "claim_cta": detect_claim_cta,
    "connect_wallet": detect_connect_wallet,
    "urgency": detect_urgency,
    "wallet_address": detect_wallet_address,
    "high_return_promise": detect_high_return_promise,
    "legitimacy_assurance": detect_legitimacy_assurance,
    "unofficial_official_claim": detect_unofficial_official_claim,
    "dm_to_claim": detect_dm_to_claim,
}

COUNTER_DETECTORS: Dict[str, Callable] = {
    "scam_warning": detect_scam_warning,
    "nothing_to_claim": detect_nothing_to_claim,
    "reported_speech": detect_reported_speech,
    "satire": detect_satire,
    "faucet_context": detect_faucet_context,
    "news_framing": detect_news_framing,
}
