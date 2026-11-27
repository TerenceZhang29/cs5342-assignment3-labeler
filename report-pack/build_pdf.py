"""Build the Group 8 report & demo source pack PDF (run with the scratch pdfenv)."""
import json, os, sys
from xml.sax.saxutils import escape

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, Frame, Image, KeepTogether, PageBreak,
                                PageTemplate, Paragraph, CondPageBreak, Spacer, Table, TableStyle)

S = os.path.dirname(os.path.abspath(__file__))
ROOT = "/Users/terence/Desktop/Cornell Tech/CS5342/assignment3"
OUT = os.path.join(ROOT, "report-pack", "Group8_A3_report_and_demo_pack.pdf")
D = json.load(open(os.path.join(S, "data.json")))
PRED = pd.read_csv(os.path.join(ROOT, "results", "predictions.csv"), dtype=str, keep_default_na=False)
CH = os.path.join(S, "charts"); os.makedirs(CH, exist_ok=True)

# ---------------------------------------------------------------- fonts & palette
FD = "/System/Library/Fonts/Supplemental/"
pdfmetrics.registerFont(TTFont("Body", FD + "Arial.ttf"))
pdfmetrics.registerFont(TTFont("Body-Bold", FD + "Arial Bold.ttf"))
pdfmetrics.registerFont(TTFont("Body-Italic", FD + "Arial Italic.ttf"))
pdfmetrics.registerFont(TTFont("Mono", FD + "Andale Mono.ttf"))
from reportlab.lib.fonts import addMapping
addMapping("Body", 0, 0, "Body"); addMapping("Body", 1, 0, "Body-Bold")
addMapping("Body", 0, 1, "Body-Italic"); addMapping("Body", 1, 1, "Body-Bold")
_GLYPHS = set(pdfmetrics.getFont("Body").face.charToGlyph.keys())

INK = colors.HexColor("#1d2329"); MUTED = colors.HexColor("#5b6670")
ACCENT = colors.HexColor("#0f5e6e"); RULE = colors.HexColor("#d5dade")
TINT = colors.HexColor("#eef3f4"); WARN = colors.HexColor("#8a4b0f"); WARNBG = colors.HexColor("#fbf3e8")
# chart colours: baseline grey, v1.1 light teal, v2 deep teal; scam / review / none
C_BASE, C_V11, C_V2 = "#b8bfc5", "#7fb3bd", "#0f5e6e"
C_SCAM, C_REVIEW, C_NONE = "#b5472d", "#d99a2b", "#9aa5ae"

for f in ["Arial.ttf", "Arial Bold.ttf"]:
    font_manager.fontManager.addfont(FD + f)
plt.rcParams.update({"font.family": "Arial", "font.size": 9, "axes.edgecolor": "#5b6670",
                     "axes.labelcolor": "#1d2329", "xtick.color": "#1d2329", "ytick.color": "#1d2329",
                     "axes.spines.top": False, "axes.spines.right": False, "axes.titlesize": 10,
                     "axes.titleweight": "bold", "legend.frameon": False, "savefig.dpi": 220})


def clean(text):
    """Escape for Paragraph markup and drop glyphs Arial can't draw (emoji)."""
    return escape("".join(ch if (ord(ch) in _GLYPHS or ch in "\n\t") else "" for ch in text))


# ---------------------------------------------------------------- styles
base = dict(fontName="Body", textColor=INK, leading=13.2, fontSize=9.6, alignment=TA_LEFT)
ST = {
    "body": ParagraphStyle("body", **base, spaceAfter=5),
    "small": ParagraphStyle("small", **{**base, "fontSize": 8.2, "leading": 10.6, "textColor": MUTED}),
    "cell": ParagraphStyle("cell", **{**base, "fontSize": 8.3, "leading": 10.4}),
    "cellb": ParagraphStyle("cellb", **{**base, "fontSize": 8.3, "leading": 10.4, "fontName": "Body-Bold"}),
    "h1": ParagraphStyle("h1", **{**base, "fontName": "Body-Bold", "fontSize": 17, "leading": 21,
                                  "spaceBefore": 4, "spaceAfter": 8, "textColor": INK}),
    "h2": ParagraphStyle("h2", **{**base, "fontName": "Body-Bold", "fontSize": 11.5, "leading": 15,
                                  "spaceBefore": 10, "spaceAfter": 5, "textColor": ACCENT}),
    "kicker": ParagraphStyle("kicker", **{**base, "fontName": "Body-Bold", "fontSize": 8, "textColor": ACCENT,
                                          "leading": 10, "spaceAfter": 2, "spaceBefore": 12}),
    "bullet": ParagraphStyle("bullet", **base, leftIndent=12, bulletIndent=2, spaceAfter=2.5),
    "code": ParagraphStyle("code", **{**base, "fontName": "Mono", "fontSize": 8, "leading": 10.5,
                                      "backColor": TINT, "borderPadding": (5, 6, 5, 6),
                                      "spaceBefore": 4, "spaceAfter": 8}),
    "title": ParagraphStyle("title", **{**base, "fontName": "Body-Bold", "fontSize": 26, "leading": 31}),
    "sub": ParagraphStyle("sub", **{**base, "fontSize": 12, "leading": 16, "textColor": MUTED}),
    "statn": ParagraphStyle("statn", **{**base, "fontName": "Body-Bold", "fontSize": 20, "leading": 23,
                                        "textColor": ACCENT}),
    "statl": ParagraphStyle("statl", **{**base, "fontSize": 8, "leading": 10, "textColor": MUTED}),
}
story = []
P = lambda t, s="body": story.append(Paragraph(t, ST[s]))


def bullets(items, style="bullet"):
    for it in items:
        story.append(Paragraph(it, ST[style], bulletText="•"))


def table(rows, widths, header=True, bold_last=False, zebra=True, highlight_rows=()):
    data = [[c if not isinstance(c, str) else Paragraph(c, ST["cellb" if (header and i == 0) else "cell"])
             for c in r] for i, r in enumerate(rows)]
    t = Table(data, colWidths=widths, repeatRows=1 if header else 0, hAlign="LEFT")
    cmds = [("VALIGN", (0, 0), (-1, -1), "TOP"), ("TOPPADDING", (0, 0), (-1, -1), 3.2),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3.2), ("LEFTPADDING", (0, 0), (-1, -1), 5),
            ("RIGHTPADDING", (0, 0), (-1, -1), 5), ("LINEBELOW", (0, -1), (-1, -1), 0.6, RULE)]
    if header:
        cmds += [("LINEBELOW", (0, 0), (-1, 0), 0.9, INK)]
    if zebra:
        for i in range(1 if header else 0, len(rows)):
            if i % 2 == 0:
                cmds.append(("BACKGROUND", (0, i), (-1, i), colors.HexColor("#f6f8f9")))
    for i in highlight_rows:
        cmds.append(("BACKGROUND", (0, i), (-1, i), TINT))
    t.setStyle(TableStyle(cmds))
    story.append(t); story.append(Spacer(1, 6))


def callout(title, text, warn=False):
    p = Paragraph(f"<b>{title}</b> {text}", ST["body"])
    t = Table([[p]], colWidths=[6.9 * inch])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), WARNBG if warn else TINT),
                           ("LINEBEFORE", (0, 0), (0, -1), 2.2, WARN if warn else ACCENT),
                           ("LEFTPADDING", (0, 0), (-1, -1), 9), ("RIGHTPADDING", (0, 0), (-1, -1), 9),
                           ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
    story.append(t); story.append(Spacer(1, 7))


def fig(path, width=6.9, caption=None):
    img = Image(path); r = img.imageHeight / img.imageWidth
    img.drawWidth = width * inch; img.drawHeight = width * inch * r
    items = [img]
    if caption:
        items.append(Paragraph(caption, ST["small"]))
    story.append(KeepTogether(items)); story.append(Spacer(1, 8))


def section(kicker, title):
    story.append(Paragraph(kicker.upper(), ST["kicker"])); story.append(Paragraph(title, ST["h1"]))


f3 = lambda x: f"{x:.3f}"
f2 = lambda x: f"{x:.2f}"
SL = D["slices"]

# ---------------------------------------------------------------- charts
def chart_headline():
    v11 = {"real": dict(accuracy=.559, scam_p=.286, scam_r=.200, flag_p=.349, flag_r=.417),
           "synthetic": dict(accuracy=.929, scam_p=1.0, scam_r=.867, flag_p=.979, flag_r=.885)}
    metrics = [("accuracy", "Accuracy"), ("scam_p", "Scam\nprecision"), ("scam_r", "Scam\nrecall"),
               ("flag_p", "Any-label\nprecision"), ("flag_r", "Any-label\nrecall")]
    fig_, axes = plt.subplots(1, 2, figsize=(7.4, 2.9), sharey=True)
    for ax, src, n in [(axes[0], "real", 111), (axes[1], "synthetic", 113)]:
        b = SL[f"{src}_test"]["baseline"]; v2 = SL[f"{src}_test"]["full"]
        xs = range(len(metrics)); w = 0.26
        for k, (vals, c, lab) in enumerate([(b, C_BASE, "Keyword baseline"), (v11[src], C_V11, "v1.1"),
                                            (v2, C_V2, "v2")]):
            ys = [vals[m] for m, _ in metrics]
            bars = ax.bar([x + (k - 1) * w for x in xs], ys, w, color=c, label=lab)
            if lab == "v2":
                for bar, y in zip(bars, ys):
                    ax.text(bar.get_x() + w / 2, y + .02, f"{y:.2f}", ha="center", fontsize=7, color="#0f5e6e")
        ax.axhline(0.9, color="#b5472d", lw=0.8, ls=(0, (3, 2)), label="0.90 scam-precision target")
        ax.axhline(0.8, color="#8a4b0f", lw=0.8, ls=(0, (1, 2)), label="0.80 recall target")
        ax.set_xticks(list(xs)); ax.set_xticklabels([l for _, l in metrics], fontsize=7.6)
        ax.set_title(f"{src.capitalize()} posts, held-out test (n={n})", loc="left")
        ax.set_ylim(0, 1.12); ax.set_yticks([0, .2, .4, .6, .8, 1])
    h, l = axes[0].get_legend_handles_labels()
    fig_.tight_layout(rect=(0, 0.08, 1, 1))
    fig_.legend(h, l, loc="lower center", ncol=5, fontsize=7.4); p = os.path.join(CH, "headline.png"); fig_.savefig(p, bbox_inches="tight"); plt.close()
    return p


def chart_ablation():
    stages = ["keyword\nbaseline", "text\nonly", "+ counter-\nsignals", "+ links", "+ account", "full\n(+ behavior)"]
    keys = ["text only", "text + counter", "text + counter + link", "+ account", "full (+ behavior)"]
    fig_, ax = plt.subplots(figsize=(7.2, 2.6))
    for src, c, lab in [("synthetic", C_V11, "Synthetic test"), ("real", C_V2, "Real test")]:
        s = SL[f"{src}_test"]
        ys = [s["baseline"]["accuracy"]] + [s["ablations"][k]["accuracy"] for k in keys]
        ax.plot(range(6), ys, marker="o", color=c, lw=2, label=lab)
        for x, y in enumerate(ys):
            ax.text(x, y + (0.035 if src == "synthetic" else -0.075), f"{y:.2f}", ha="center", fontsize=7.2, color=c)
    ax.set_xticks(range(6)); ax.set_xticklabels(stages, fontsize=7.6)
    ax.set_ylim(0.2, 1.05); ax.set_ylabel("Accuracy (v2)")
    ax.legend(loc="lower right", fontsize=8)
    ax.set_title("Ablation: adding signal groups one at a time", loc="left")
    fig_.tight_layout(); p = os.path.join(CH, "ablation.png"); fig_.savefig(p, bbox_inches="tight"); plt.close()
    return p


def chart_sweep():
    fig_, axes = plt.subplots(1, 2, figsize=(7.4, 2.5), sharey=True)
    for ax, src in [(axes[0], "real"), (axes[1], "synthetic")]:
        sw = D["sweep"][src]; ts = sorted(float(t) for t in sw)
        for m, c, lab in [("accuracy", C_V2, "Accuracy"), ("flag_p", C_SCAM, "Any-label precision"),
                          ("flag_r", C_REVIEW, "Any-label recall")]:
            ax.plot(ts, [sw[str(t)][m] for t in ts], marker="o", ms=3.5, lw=1.8, color=c, label=lab)
        ax.axvline(2.0, color="#1d2329", lw=0.7, ls=(0, (2, 2)))
        ax.text(2.05, 0.23, "chosen 2.0", fontsize=6.8)
        ax.set_xticks(ts); ax.set_xlabel("MEDIUM_THRESHOLD")
        ax.set_title(f"{src.capitalize()} dev split", loc="left"); ax.set_ylim(0.2, 1.05)
    axes[0].legend(fontsize=7.4, loc="upper left", bbox_to_anchor=(0, -0.25), ncol=3)
    fig_.tight_layout(); p = os.path.join(CH, "sweep.png"); fig_.savefig(p, bbox_inches="tight"); plt.close()
    return p


def chart_composition():
    rows = [("Synthetic dev", "synthetic|dev"), ("Synthetic test", "synthetic|test"),
            ("Real dev", "real|dev"), ("Real test", "real|test")]
    fig_, ax = plt.subplots(figsize=(7.2, 1.9))
    for i, (lab, k) in enumerate(rows[::-1]):
        c = D["composition"][k]; left = 0
        for cls, col in [("crypto-scam", C_SCAM), ("unverified-airdrop", C_REVIEW), ("none", C_NONE)]:
            ax.barh(i, c[cls], left=left, color=col, height=0.62, label=cls if i == 0 else None)
            if c[cls] >= 5:
                ax.text(left + c[cls] / 2, i, str(c[cls]), ha="center", va="center", fontsize=7.5, color="white")
            left += c[cls]
        ax.text(left + 1.5, i, f"{left}", va="center", fontsize=7.5, color="#5b6670")
    ax.set_yticks(range(4)); ax.set_yticklabels([r[0] for r in rows[::-1]])
    ax.set_xlabel("posts"); ax.legend(ncol=3, loc="upper left", bbox_to_anchor=(0, -0.32), fontsize=7.6)
    ax.spines["left"].set_visible(False); ax.tick_params(axis="y", length=0)
    fig_.tight_layout(); p = os.path.join(CH, "composition.png"); fig_.savefig(p, bbox_inches="tight"); plt.close()
    return p


def chart_errors():
    fp = [("News & explainers", 6), ("Exchange / product promos, referrals", 6),
          ("Casino & adult-token spam", 4), ("Gas-price bot", 2), ("Testnet faucet guide", 1),
          ("Official security notice", 1), ("Follow/RT engagement giveaway", 1),
          ("\"no seed phrase required\" (scam FP)", 1)]
    fn = [("Bare title + shortener link", 4), ("Promo without airdrop wording", 2),
          ("Airdrop link wrapped in a warning", 1), ("Non-English post", 1), ("Unfolded Cyrillic homoglyphs", 1)]
    fig_, axes = plt.subplots(1, 2, figsize=(7.4, 2.7), gridspec_kw={"width_ratios": [1.15, 1]})
    for ax, data, col, title in [(axes[0], fp, C_REVIEW, "False positives: 22 legit posts flagged"),
                                 (axes[1], fn, C_SCAM, "False negatives: 9 airdrop posts missed")]:
        labs = [d[0] for d in data][::-1]; vals = [d[1] for d in data][::-1]
        ax.barh(labs, vals, color=col, height=0.6)
        for i, v in enumerate(vals):
            ax.text(v + 0.1, i, str(v), va="center", fontsize=7.5)
        ax.set_title(title, loc="left", fontsize=9); ax.tick_params(axis="y", labelsize=7.4, length=0)
        ax.spines["left"].set_visible(False); ax.set_xticks([])
        ax.spines["bottom"].set_visible(False)
    fig_.tight_layout(); p = os.path.join(CH, "errors.png"); fig_.savefig(p, bbox_inches="tight"); plt.close()
    return p


def chart_pipeline():
    fig_, ax = plt.subplots(figsize=(7.4, 2.25)); ax.axis("off"); ax.set_xlim(0, 100); ax.set_ylim(0, 30)
    def box(x, y, w, h, title, sub, fc="#eef3f4", ec="#0f5e6e"):
        ax.add_patch(matplotlib.patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.4,rounding_size=1.2",
                                                       fc=fc, ec=ec, lw=1))
        ax.text(x + w / 2, y + h - 2.6, title, ha="center", va="top", fontsize=8, weight="bold", color="#1d2329")
        ax.text(x + w / 2, y + h - 7.2, sub, ha="center", va="top", fontsize=6.4, color="#5b6670", linespacing=1.3)
    def arrow(x1, x2, y=15):
        ax.annotate("", (x2, y), (x1, y), arrowprops=dict(arrowstyle="-|>", color="#5b6670", lw=1))
    box(0, 6, 12, 18, "Ingest", "data.csv row\nor bsky.app URL\n→ PostRecord")
    box(16, 6, 13, 18, "Prefilter", "normalize:\nleetspeak, homoglyph,\nzero-width, s p a c e s\nskip if no link and\nno crypto term")
    box(33, 2, 30, 26, "Signal detectors", "text: send-to-receive, seed phrase,\nupfront fee, giveaway, claim CTA,\nwallet connect, urgency\nlink: MetaMask list (119k), look-alike,\nhomoglyph, brand-in-domain, shortener\naccount: age, impersonation, official\nhandle, coordinated campaigns\ncounter: warning, negation, satire,\nnews, faucet, nothing-to-claim")
    box(67, 6, 14, 18, "Router", "hard + uncontested\n→ crypto-scam\nscore ≥ 2.0 + airdrop\n→ unverified-airdrop\nelse → none")
    box(85, 6, 15, 18, "Outputs", "label + reasons\nOzone-style review\nqueue (JSONL)\naccount referral\n(no auto action)", fc="#fbf3e8", ec="#8a4b0f")
    for a, b in [(12.8, 15.2), (29.8, 32.2), (63.8, 66.2), (81.8, 84.2)]:
        arrow(a, b)
    fig_.tight_layout(); p = os.path.join(CH, "pipeline.png"); fig_.savefig(p, bbox_inches="tight"); plt.close()
    return p


charts = dict(headline=chart_headline(), ablation=chart_ablation(), sweep=chart_sweep(),
              composition=chart_composition(), errors=chart_errors(), pipeline=chart_pipeline())

# ================================================================ CONTENT
# ---------------- cover
story.append(Spacer(1, 0.55 * inch))
P("CS 5342 · ASSIGNMENT 3 · GROUP 8", "kicker")
P("Report &amp; demo source pack", "title")
story.append(Spacer(1, 6))
P("Bluesky labeler for fraudulent cryptocurrency giveaway and airdrop promotions", "sub")
story.append(Spacer(1, 10))
P("Terence Zhang · Lucas Sumartha · Ziqiao Gao · Lillian (Xintong) Li", "body")
P("Every number, table, chart and example we can use in the written report and the demo video, "
  "taken from the v2 code in the GitHub repo (TerenceZhang29/cs5342-assignment3-labeler, commit c2f5553) "
  "and regenerated on 27 Nov 2026. This is working material, not the report itself.", "small")
story.append(Spacer(1, 16))

rt, st_ = SL["real_test"]["full"], SL["synthetic_test"]["full"]
stats = [(f3(rt["accuracy"]), "real test accuracy (v2)\nup from 0.559 in v1.1"),
         (f3(rt["scam_p"]), "real test crypto-scam precision\nup from 0.286 (target ≥ 0.90)"),
         (f3(st_["accuracy"]), "synthetic test accuracy\nkeyword baseline: 0.513"),
         ("0.65 ms", "median time per post\n0 network calls offline")]
cells = [[Paragraph(n, ST["statn"]) for n, _ in stats],
         [Paragraph(clean(l).replace("\n", "<br/>"), ST["statl"]) for _, l in stats]]
t = Table(cells, colWidths=[1.72 * inch] * 4, hAlign="LEFT")
t.setStyle(TableStyle([("LINEABOVE", (0, 0), (-1, 0), 1.4, ACCENT), ("TOPPADDING", (0, 0), (-1, 0), 8),
                       ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                       ("VALIGN", (0, 0), (-1, -1), "TOP")]))
story.append(t); story.append(Spacer(1, 18))

P("What's inside", "h2")
toc = [("1", "Story in one page", "the narrative arc for both the report and the video"),
       ("2", "Policy and labels", "what the labeler enforces, and how the code departs from the proposal"),
       ("3", "How it works", "pipeline diagram, signal weights, routing rules, design choices"),
       ("4", "Data", "340 posts, how they were collected and labeled, disclosures"),
       ("5", "Results", "headline tables, confusion matrices, baseline, ablations"),
       ("6", "Iteration history", "v0 → v1 → v1.1 → real data → v2, with the evidence for each change"),
       ("7", "Error analysis", "what still fails and why"),
       ("8", "Efficiency", "latency, memory, network cost"),
       ("9", "Limitations, ethics, next steps", "caveats we must state"),
       ("10", "Demo video kit", "run of show, commands, worked examples with their signals"),
       ("A", "Appendix", "reproduction commands, file map, full error list")]
table([["#", "Section", "Use it for"]] + [[a, f"<b>{b}</b>", c] for a, b, c in toc],
      [0.35 * inch, 2.2 * inch, 4.35 * inch])
callout("Check against the spec.", "The assignment PDF isn't in the repo, so the report outline and video "
        "timings here are suggestions. Match section names, page limit and video length to the official "
        "Assignment 3 instructions before submitting.", warn=True)
story.append(PageBreak())

# ---------------- 1 story
section("Section 1", "The story in one page")
P("Use this arc for the report introduction and as the spine of the video.")
arc = [("Problem", "Crypto giveaway and airdrop scams on Bluesky ask people to send crypto first, hand over a seed "
        "phrase, pay a fee, or visit a counterfeit claim site. Blocking crypto keywords would also hit warnings, "
        "news and legitimate airdrops."),
       ("Approach", "An explainable rule-based labeler with two tiers. <b>crypto-scam</b> fires on uncontested hard "
        "indicators. <b>unverified-airdrop</b> fires on a medium risk score for posts that really promote an "
        "airdrop. Counter-signals (warnings, negation, satire, news) stop us from labeling the people "
        "warning about scams."),
       ("First result", f"On synthetic posts written to the rubric, v1.1 scored <b>0.929</b> accuracy against a 0.513 "
        "keyword baseline, with perfect scam precision."),
       ("Reality check", "On 168 real Bluesky posts, the same frozen code dropped to <b>0.559</b> accuracy and "
        "<b>0.29</b> scam precision. It flagged faucet guides, deepfake news and gas-fee jokes, and it missed a "
        "13-account \"1 BTC giveaway\" campaign posted from established accounts."),
       ("Iteration", "v2 changed only what the real <i>dev</i> split justified: faucet and news counter-signals, account "
        "age as an amplifier only, an any-age campaign detector, new brands, and a lower review threshold."),
       ("Outcome", f"Real test accuracy <b>{f3(rt['accuracy'])}</b>, scam precision <b>{f3(rt['scam_p'])}</b>, recall "
        f"<b>{f3(rt['scam_r'])}</b>. Synthetic test improved to <b>{f3(st_['accuracy'])}</b>. The scam-precision "
        "target is met; the 0.80 recall target is met on synthetic but not on real posts (0.75)."),
       ("Honest caveats", "8 of the 10 real test scams are one campaign, so real recall is optimistic (0.70 accuracy "
        "without it). The real test set isn't fully blind. One AI annotator labeled the real posts, which no person "
        "has checked yet."),
       ("Takeaway", "Synthetic data written alongside the rules overstates performance. Real data found the gaps, "
        "and explainable signals made each fix traceable to a specific post.")]
table([[f"<b>{a}</b>", b] for a, b in arc], [1.15 * inch, 5.75 * inch], header=False)
story.append(PageBreak())

# ---------------- 2 policy
section("Section 2", "Policy and labels")
P("The labeler implements our Assignment 2 policy, <i>Fraudulent Cryptocurrency Giveaway and Airdrop Promotions "
  "on Bluesky</i>. Each label carries the list of signals that caused it, so it can be explained on appeal.")
table([["Label", "Applied when", "Effect (policy §3.1)"],
       ["<b>crypto-scam</b>", "An uncontested hard indicator: send-X-get-2X, seed phrase or private key request, "
        "upfront fee to unlock a reward, a known phishing domain, a look-alike or homoglyph domain, an "
        "impersonated account running a giveaway with a call to action, or a brand inside an unofficial claim domain.",
        "Warn/blur; queue for human takedown review."],
       ["<b>unverified-airdrop</b>", "Risk score ≥ 2.0 on a post that actually promotes an airdrop or giveaway, "
        "or a link or text pushed by a coordinated set of accounts.", "Stays visible; informs; queued for review."],
       ["<i>no label</i>", "Warnings and education (even when quoting scam text), news, legitimate airdrops from "
        "a project's own domain handle, satire, victims asking for help, non-crypto giveaways.", "Nothing."]],
      [1.25 * inch, 3.95 * inch, 1.7 * inch])

P("The seven policy examples, as regression tests", "h2")
P("All seven enforcement examples from the proposal are pytest cases (tests/test_policy_examples.py) and pass.")
ex_rows = [["Ex.", "Post (abridged)", "Policy says", "Labeler"]]
pex = {1: "crypto-scam", 2: "crypto-scam", 3: "crypto-scam", 4: "unverified-airdrop", 5: "unverified-airdrop",
       6: "none", 7: "none"}
dm = {d["title"].split(":")[0]: d for d in D["demos"]}
texts = {1: dm["Policy Ex. 1"]["text"], 2: dm["Policy Ex. 2"]["text"], 3: dm["Policy Ex. 3"]["text"],
         4: "\"gm 👀 eth-drop.claims/go\" posted by 4 new accounts", 5: dm["Policy Ex. 5"]["text"],
         6: dm["Policy Ex. 6"]["text"], 7: dm["Policy Ex. 7"]["text"]}
for i in range(1, 8):
    ex_rows.append([str(i), clean(texts[i][:95]), pex[i], f"{pex[i]} (match)"])
table(ex_rows, [0.35 * inch, 4.1 * inch, 1.2 * inch, 1.25 * inch])

P("Where the implementation departs from the proposal", "h2")
table([["Proposal", "Implementation", "Why"],
       ["Ingest from Jetstream", "CSV offline; live posts by URL (run_labeler.py)",
        "The assignment specifies CSV input, and graders can reproduce results with no network."],
       ["Google Web Risk link checks", "Not used", "Paid API. The free MetaMask list (119k crypto phishing domains) "
        "plus look-alike, homoglyph and brand-in-domain checks replace it."],
       ["Domain-age check", "Not used", "WHOIS/RDAP is slow and rate-limited. Account age and cheap TLDs are proxies."],
       ["Human review in Ozone", "review_queue.jsonl mirroring Ozone emitEvent payloads",
        "Running Ozone needs a hosted service; entries can be replayed unchanged."],
       ["Hard indicator → crypto-scam", "Hard indicators can be contested by counter-signals",
        "Otherwise scam warnings that quote scam text get labeled (Example 7)."],
       ["Two tiers", "Two tiers, and unverified-airdrop requires airdrop context",
        "A label must describe the post it's on."],
       ["(LLM tier deferred)", "No LLM", "Cost, determinism and explainability (§3.5)."]],
      [1.6 * inch, 2.35 * inch, 2.95 * inch])
story.append(CondPageBreak(2.2 * inch))

# ---------------- 3 how it works
section("Section 3", "How it works")
fig(charts["pipeline"], caption="Figure 1. Pipeline. Every stage is deterministic; a post's label can be traced to "
    "named signals with evidence strings.")
P("Signal weights (v2)", "h2")
W = D["weights"]
groups = [("Hard indicators (any one, uncontested, gives crypto-scam)",
           ["send_to_receive", "credential_request", "upfront_fee", "blocklisted_domain", "lookalike_domain",
            "homoglyph_domain"]),
          ("Medium text signals", ["giveaway_offer", "connect_wallet", "high_return_promise", "legitimacy_assurance",
                                   "claim_cta", "urgency", "wallet_address", "unofficial_official_claim", "dm_to_claim"]),
          ("Link signals", ["brand_in_domain", "punycode_domain", "shortened_link", "suspicious_tld",
                            "unverified_airdrop_link"]),
          ("Account and behavior", ["coordinated_link", "impersonation_handle", "very_new_account", "new_account"]),
          ("Counter-signals", ["verified_project_source", "scam_warning", "credential_negation", "nothing_to_claim",
                               "reported_speech", "faucet_context", "news_framing", "satire", "official_links_only"])]
rows = [["Group", "Signals and weights"]]
for g, names in groups:
    rows.append([f"<b>{g}</b>", ", ".join(f"{n} <b>{W[n]:+g}</b>" for n in names)])
table(rows, [2.0 * inch, 4.9 * inch])
P("Hard combos: <b>impersonated_giveaway</b> = impersonation handle + giveaway + call to action; "
  "<b>brand_domain_claim</b> = brand inside an unofficial domain + call to action.", "small")
P("Routing rules", "h2")
bullets(["<b>Hard indicator, not contested</b> → crypto-scam.",
         "<b>Contested</b> (a warning, negation, reported speech, faucet context, news framing or a verified project "
         "source is present): each hard indicator adds only +2.0, and the review threshold rises by +3.0.",
         "<b>Score ≥ 2.0 and the post promotes an airdrop or giveaway</b> → unverified-airdrop.",
         "<b>Coordinated campaign</b> (same link from ≥ 3 new accounts, or identical text + link from ≥ 3 accounts of "
         "any age within 48 h) → at least unverified-airdrop.",
         "<b>Account age</b> only counts when the post already has a concrete risk signal (v2).",
         "Impersonation creates an <b>account referral</b> in the review queue, never an automatic account label."])
P("Design choices worth explaining", "h2")
bullets(["<b>Rules, not an LLM:</b> explainable, deterministic, free, under 1 ms per post.",
         "<b>Context changes meaning:</b> the words \"send 1 ETH, get 2 back\" produce a label in a scam and no label "
         "in a PSA quoting it.",
         "<b>Scammer reassurance is a tell:</b> \"Not a scam! Beware of fakes, this is the only real one\" adds "
         "suspicion instead of cancelling it.",
         "<b>Evasion handling:</b> NFKC normalization, zero-width removal, Cyrillic/Greek homoglyph folding, "
         "leetspeak un-folding, joining s p a c e d letters, de-obfuscating [.] in links.",
         "<b>Free data sources:</b> MetaMask eth-phishing-detect snapshot (119,002 domains, 26 Nov 2026); "
         "official project domains and impersonation targets are editable CSVs."])
story.append(CondPageBreak(2.2 * inch))

# ---------------- 4 data
section("Section 4", "Data")
P(f"data.csv holds <b>340 posts</b>: 172 synthetic and 168 real. Each source has its own dev/test split "
  f"(every third post per label goes to dev). Tuning used dev only; all headline numbers are on test.")
fig(charts["composition"], caption="Figure 2. Dataset composition by source, split and gold label.")
P("Real posts", "h2")
bullets([f"Collected on 26 Nov 2026 with collect_posts.py: Bluesky searchPosts, 16 queries (airdrop, giveaway eth, "
         f"seed phrase, claim tokens, …), <b>{D['n_candidates']} unique posts</b>.",
         "<b>168 annotated:</b> every post v1.1 flagged (64), a random 6 unflagged posts per query (96, seed 5342), "
         f"and all {D['kalshi_posts']} posts of the \"1 BTC giveaway / insurance-kalshi.com\" campaign.",
         "Text is frozen at collection time so results stay reproducible if posts are deleted.",
         "Because flagged posts are over-sampled, metrics describe behavior on scam-adjacent search results, not "
         "platform-wide prevalence.",
         "Safety: linked sites were never opened; labels come from post text, domain and author profile only."])
callout("Disclosure we must include.", "The real posts were labeled by Claude (an AI assistant) acting as a single "
        "annotator, following ANNOTATION.md. It drafted labels, re-read every post in full, and changed 4. "
        "There's no second annotator, so no Cohen's κ, and the labels may share blind spots with the rules. "
        "Recommended before submitting: a team member spot-checks 20–30 random posts plus all 16 crypto-scam "
        "posts and reports the agreement rate.", warn=True)
P("Synthetic posts", "h2")
cats = D["synthetic_categories"]
def catline(prefix):
    return ", ".join(f"{k.split('/')[1]} ({v})" for k, v in cats.items() if k.startswith(prefix))
table([["Bucket", "Categories (count)"],
       ["<b>crypto-scam</b> (46)", catline("scam/")],
       ["<b>unverified-airdrop</b> (34)", catline("review/")],
       ["<b>none</b> (92)", catline("none/")]], [1.55 * inch, 5.35 * inch])
P("Some synthetic posts are deliberately out of reach for rules (paraphrase, image-only) so the evaluation "
  "measures limits rather than only confirming the rules. Because the same team wrote the rules and the "
  "synthetic posts, synthetic results are optimistic.", "small")
P("Annotation rubric (short form)", "h2")
bullets(["<b>Judge intent, not vocabulary:</b> quoting \"send 1 ETH get 2 back\" to warn people is none.",
         "<b>Victims and questions are none:</b> \"Got a DM saying I won, is this a scam?\"",
         "<b>A project's own domain handle</b> linking to its own domain is none, even with \"claim now\".",
         "<b>Unsure between scam and airdrop?</b> Choose unverified-airdrop; the strong label is for clear fraud.",
         "<b>Faucet/testnet guides</b> on the project's own domain with no real reward are none."])
story.append(CondPageBreak(2.2 * inch))

# ---------------- 5 results
section("Section 5", "Results")
fig(charts["headline"], caption="Figure 3. Held-out test results: keyword baseline vs v1.1 vs v2. Dashed lines are "
    "the policy's §3.3 targets. Any-label = binary flagged vs not flagged.")
P("Headline table (held-out test)", "h2")
v11 = {"real": [.559, .437, .286, .200, .349, .417], "synthetic": [.929, .919, 1.0, .867, .979, .885]}
rows = [["Test set", "System", "Acc.", "Macro F1", "Scam P", "Scam R", "Any P", "Any R"]]
hl = []
for src, n in [("synthetic", 113), ("real", 111)]:
    b = SL[f"{src}_test"]["baseline"]; v = SL[f"{src}_test"]["full"]
    keys = ["accuracy", "macro_f1", "scam_p", "scam_r", "flag_p", "flag_r"]
    rows.append([f"{src} ({n})", "keyword baseline"] + [f3(b[k]) for k in keys])
    rows.append([f"{src} ({n})", "v1.1"] + [f3(x) for x in v11[src]])
    rows.append([f"{src} ({n})", "<b>v2</b>"] + [f"<b>{f3(v[k])}</b>" for k in keys]); hl.append(len(rows) - 1)
k = D["real_test_excl_kalshi"]
rows.append(["real excl. Kalshi (103)", "v2"] + [f3(k[x]) for x in ["accuracy", "macro_f1", "scam_p", "scam_r",
                                                                     "flag_p", "flag_r"]])
table(rows, [1.45 * inch, 1.15 * inch] + [0.72 * inch] * 6, highlight_rows=hl)
bullets(["<b>Scam precision target (≥ 0.90):</b> met on both test sets (1.000 synthetic, 0.909 real).",
         "<b>Recall target (≥ 0.80, any label on harmful posts):</b> met on synthetic (0.923), not on real (0.750).",
         "<b>Keyword blocking</b> (the alternative the policy rejected) reaches high recall but scam precision of only "
         "0.34 synthetic / 0.12 real: it would label most warnings and news."])

def cm_table(key, title):
    cm = SL[key]["confusion"]; cls = ["crypto-scam", "unverified-airdrop", "none"]
    rows = [[f"<b>{title}</b><br/>gold ↓ / pred →"] + cls]
    for g in cls:
        rows.append([f"<b>{g}</b>"] + [f"<b>{cm[g][p]}</b>" if g == p else str(cm[g][p]) for p in cls])
    data = [[Paragraph(c, ST["cell"]) for c in r] for r in rows]
    t = Table(data, colWidths=[1.05 * inch, 0.85 * inch, 1.1 * inch, 0.45 * inch])
    t.setStyle(TableStyle([("LINEBELOW", (0, 0), (-1, 0), 0.9, INK), ("FONTSIZE", (0, 0), (-1, -1), 8),
                           ("BACKGROUND", (1, 1), (1, 1), TINT), ("BACKGROUND", (2, 2), (2, 2), TINT),
                           ("BACKGROUND", (3, 3), (3, 3), TINT), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                           ("LEFTPADDING", (0, 0), (-1, -1), 4)]))
    return t
P("Confusion matrices (v2, test)", "h2")
pair = Table([[cm_table("real_test", "Real test (111)"), cm_table("synthetic_test", "Synthetic test (113)")]],
             colWidths=[3.5 * inch, 3.5 * inch], hAlign="LEFT")
pair.setStyle(TableStyle([("LEFTPADDING", (0, 0), (-1, -1), 0), ("VALIGN", (0, 0), (-1, -1), "TOP")]))
story.append(pair); story.append(Spacer(1, 8))
P("Per-class (v2, test)", "h2")
rows = [["Label", "Real P", "Real R", "Synthetic P", "Synthetic R"]]
for lab, pk, rk in [("crypto-scam", "scam_p", "scam_r"), ("unverified-airdrop", "review_p", "review_r")]:
    rows.append([lab, f3(rt[pk]), f3(rt[rk]), f3(st_[pk]), f3(st_[rk])])
rows.append(["any label (binary)", f3(rt["flag_p"]), f3(rt["flag_r"]), f3(st_["flag_p"]), f3(st_["flag_r"])])
table(rows, [1.9 * inch] + [1.25 * inch] * 4)
story.append(CondPageBreak(2.2 * inch))

fig(charts["ablation"], caption="Figure 4. Ablation on the test splits (v2 code). Each point enables one more signal "
    "group.")
P("What the ablation shows", "h2")
bullets(["<b>Counter-signals buy precision:</b> on synthetic posts, scam precision goes 0.71 → 1.00 once warnings, "
         "negation and satire are recognized.",
         "<b>Links buy recall:</b> the biggest single jump on both sets (real 0.71 → 0.74, synthetic 0.79 → 0.89); on "
         "real posts it lifts scam recall 0.10 → 1.00, mostly through the brand-in-domain combo.",
         "<b>Account signals cut both ways:</b> +0.04 on synthetic, −0.02 on real. Many legitimate real posters (bots, "
         "newsletters, newly migrated users) have young accounts. v2 already limits them to amplifying other risk; "
         "removing them is the next experiment.",
         "<b>The behavior tracker adds nothing measurable here,</b> because campaign posts already carry other signals. "
         "It matters for campaigns with bland text, which this dataset barely covers."])
rows = [["Stage", "Real acc.", "Real scam P/R", "Synth. acc.", "Synth. scam P/R"]]
for name, key in [("keyword baseline", None), ("text only", "text only"), ("+ counter-signals", "text + counter"),
                  ("+ links", "text + counter + link"), ("+ account", "+ account"), ("full (+ behavior)", "full (+ behavior)")]:
    r = SL["real_test"]["baseline"] if key is None else SL["real_test"]["ablations"][key]
    s = SL["synthetic_test"]["baseline"] if key is None else SL["synthetic_test"]["ablations"][key]
    rows.append([name, f3(r["accuracy"]), f"{f2(r['scam_p'])} / {f2(r['scam_r'])}", f3(s["accuracy"]),
                 f"{f2(s['scam_p'])} / {f2(s['scam_r'])}"])
table(rows, [1.7 * inch, 1.1 * inch, 1.3 * inch, 1.1 * inch, 1.3 * inch])
story.append(CondPageBreak(2.2 * inch))

# ---------------- 6 iteration
section("Section 6", "Iteration history")
P("This is the \"what we had to go back on\" material. Each fix traces to a specific post; v2 code comments marked "
  "<i>v2:</i> cite the dev post that motivated them, and tests/test_v2_changes.py reproduces each one.")
table([["Version", "What happened", "Key number"],
       ["<b>v0</b>", "Smoke test on the proposal's 7 examples. Fixed: \"entering your recovery phrase\" missed (verb "
        "inflections); @uniswap.org flagged as impersonating Uniswap (official-handle exemption); leetspeak turned "
        "$eth into \"seth\".", "7/7 examples"],
       ["<b>v1</b>", "Tuned on the 59-post synthetic dev split, then weights frozen. Fixed a digit-leading domain bug; "
        "brand-in-domain + any call to action became a hard combo; added giving/gifting, \"claims are open\", and "
        "the unverified_airdrop_link signal.", "synthetic test 0.920"],
       ["<b>v1.1</b>", "Disclosed bug fix found in the test run: opensea.support was missed because .support wasn't a "
        "known TLD. TLDs are now derived from the 119k-domain blocklist. No weights changed.", "synthetic test 0.929"],
       ["<b>Real data</b>", "168 real posts labeled and run against frozen v1.1: faucet guides, deepfake news, gas-fee "
        "satire and an old-account campaign broke it.", "real test 0.559; scam P 0.29"],
       ["<b>v2</b>", "Tuned on real + synthetic dev only (table below). Threshold swept on dev.",
        "real test 0.721; scam P 0.91"]],
      [0.85 * inch, 4.6 * inch, 1.45 * inch], highlight_rows=(5,))
P("v2 changes and the dev evidence behind each", "h2")
table([["Dev evidence", "Change"],
       ["r250, r253, r257: faucet guides (\"click 'Send me ETH' … to receive faucet tokens\") → crypto-scam",
        "faucet_context counter-signal, only when no real reward is promised"],
       ["r273: \"deepfake Elon's promise to double your crypto — AMBCrypto\"", "deepfake is a warning word; new news_framing counter (−2)"],
       ["r035: \"Paying $45 in gas fees to claim an $8 airdrop\"", "Upfront-fee rule skips first-person paying/paid/spent"],
       ["r130: a \"spot the scam\" answer quoting several indicators", "Contested posts need +3 extra score"],
       ["r001, r214, r271, r556, r561: new account + vague mention", "Account age only amplifies concrete risk"],
       ["r215–r227: identical \"1 BTC giveaway\" posts from 13 old accounts", "Identical text + link from ≥ 3 accounts of any age within 48 h"],
       ["same campaign; r174 \"2x crypto giveaway\"", "Kalshi, Polymarket, Robinhood added as brands; \"2x/double … giveaway\" = money flip"],
       ["synthetic p050, p056: first faucet rule hid \"testnet rewards\" farming", "Faucet rule narrowed"],
       ["synthetic p059, p065: \"Reply with your ETH address\"", "Public address request = call to action"],
       ["Threshold sweep on both dev splits", "MEDIUM_THRESHOLD 3.0 → 2.0 (Figure 5)"]],
      [3.6 * inch, 3.3 * inch])
P("Considered but <b>not</b> applied, because only test posts motivated them: a \"no seed phrase required\" negation "
  "(r311), and same-author repetition.", "small")
fig(charts["sweep"], caption="Figure 5. Threshold sweep on the dev splits. 2.0 gives the best accuracy on both; on "
    "real dev it trades any-label precision (0.90 → 0.71) for recall (0.47 → 0.79), acceptable for an inform-only "
    "tier. Values above 3.0 change nothing.")
story.append(CondPageBreak(2.2 * inch))

# ---------------- 7 errors
section("Section 7", "Error analysis (v2, test)")
fig(charts["errors"], caption="Figure 6. The 31 remaining real-test errors, grouped by hand from the signals in "
    "results/eval_report_test_real.md.")
P("Real posts", "h2")
bullets(["<b>Over-flagging is the main cost of the 2.0 threshold.</b> Exchange campaign news, casino promos, referral "
         "codes, explainers and a gas-price bot mention airdrops with a link, which scores 2.5. This tier never hides "
         "content, and the review queue absorbs it.",
         "<b>The one scam false positive (r311)</b> is a developer bio saying \"no seed phrase required\". The negation "
         "isn't handled yet (deliberately not tuned on test).",
         "<b>Misses are low-text promos:</b> \"AiMASH Exclusive Airdrop Campaign wn.nr/…\" has only one signal (score 1.0).",
         "<b>Evasion gap:</b> r051 mixes Cyrillic letters (в, т, с, н) our homoglyph map doesn't fold."])
P("Synthetic posts (7 errors)", "h2")
table([["Post", "Gold → pred", "Why"],
       ["p005 \"Send any amount of SOL to 7xKX… receive 3x back\"", "scam → none", "No amount; Solana address format not recognized"],
       ["p008 \"Send 0.05 ETH for gas and we'll send your 2 ETH prize\"", "scam → none", "\"for gas\" isn't read as a fee"],
       ["p009 \"You send 1, I send 2\"", "scam → none", "Paraphrase with no coin; expected limit of rules"],
       ["p045 image-only scam", "scam → none", "Text is in the image; needs OCR"],
       ["p122, p127 non-crypto giveaways", "none → review", "Generic giveaway wording + link"],
       ["p170 moderator note quoting Example 5", "none → review", "Quote has no warning words"]],
      [3.3 * inch, 1.05 * inch, 2.55 * inch])

# ---------------- 8 efficiency
story.append(CondPageBreak(2.4 * inch)); P("Section 8 · Efficiency", "h2")
L = D["latency_ms"]; stt = D["stats"]
table([["Measure", "Value (offline, all 340 posts)"],
       ["Resource load incl. 119,002-domain blocklist", f"{stt['load_seconds'] * 1000:.0f} ms, peak {stt['load_peak_bytes'] / 1e6:.0f} MB"],
       ["Per-post latency", f"median {L['median']:.2f} ms · mean {L['mean']:.2f} ms · p95 {L['p95']:.2f} ms · max {L['max']:.2f} ms"],
       ["Extra memory while scoring", f"{stt['run_peak_bytes'] / 1e6:.1f} MB peak"],
       ["Network calls", "0 offline. Live: 2 Bluesky API calls per post (record + profile), plus up to 5 cached "
        "HEAD requests per shortened link"],
       ["Posts skipped by the cheap prefilter", "17 of 340"],
       ["Paid services", "None (no LLM, no Web Risk). Running cost is compute only."]],
      [2.6 * inch, 4.3 * inch])
P("At ~0.65 ms per post a single process could score roughly 1,500 posts per second. That's an extrapolation "
  "from offline timing, not a firehose measurement.", "small")
story.append(CondPageBreak(2.2 * inch))

# ---------------- 9 limitations
section("Section 9", "Limitations, ethics and next steps")
P("Caveats to state plainly", "h2")
bullets(["<b>Real recall is optimistic.</b> 8 of the 10 real test scams are the Kalshi campaign whose dev posts shaped "
         "v2. Excluding it: accuracy 0.699, scam precision 2/3, recall 2/2.",
         "<b>The real test set isn't perfectly blind.</b> We read its v1.1 errors before designing v2; only "
         "dev-motivated changes were applied.",
         "<b>Single AI annotator</b> for real posts, with no human check yet and no κ.",
         "<b>Small real sample:</b> 16 real scam posts in total; per-class numbers have wide uncertainty.",
         "<b>Sampling bias:</b> search-query collection over-represents scam-adjacent posts.",
         "<b>Synthetic optimism:</b> the same team wrote the rules and the synthetic posts.",
         "<b>Not covered:</b> image-only scams (no OCR), DMs, non-English posts, link destinations (never opened)."])
P("Ethics and harm trade-offs", "h2")
bullets(["<b>False positives on warnings</b> would punish the people fighting scams, so counter-signals contest hard "
         "indicators, and the ablation shows they're what makes scam precision high.",
         "<b>The lower-severity tier only informs.</b> unverified-airdrop never hides content, which is why we accepted "
         "lower precision there for recall.",
         "<b>No automated account actions.</b> Impersonation creates a referral for human review, never an account label.",
         "<b>Explainability and appeal.</b> Each label stores the signals and evidence behind it; label definitions "
         "include appeal text.",
         "<b>Adversarial pressure.</b> Weights and thresholds live in config and shouldn't be published in detail (§3.6); "
         "evasion handling is tested (leetspeak, homoglyphs, spacing, [.] links).",
         "<b>Privacy and safety.</b> Real posts are stored only in a private repo; scam links were never opened; the "
         "Bluesky password stays in a git-ignored .env; labels are emitted only with an explicit --emit_labels flag."])
story.append(CondPageBreak(2.6 * inch)); P("Next steps", "h2")
table([["#", "Next step", "Addresses"],
       ["1", "Human spot-check of AI labels (20–30 random + all 16 scams), report agreement", "Annotation validity"],
       ["2", "Collect a fresh real test set on a new date", "Contaminated real test"],
       ["3", "News / exchange-source allowlist, casino and gambling exclusion", "22 real false positives"],
       ["4", "\"no … required\" negation; Solana addresses; \"for gas\" as a fee", "r311, p005, p008"],
       ["5", "Try removing account signals entirely", "Account signals hurt on real (−0.02)"],
       ["6", "Wider homoglyph map; OCR for image posts; non-English terms", "r051, p045, r578"],
       ["7", "Optional LLM tier for medium-score posts only (needs cost approval)", "Paraphrase misses (p009)"],
       ["8", "Jetstream consumer for live time-to-label measurement", "Proposal §3.2 step 1"]],
      [0.3 * inch, 4.4 * inch, 2.2 * inch])
story.append(PageBreak())

# ---------------- 10 demo kit
section("Section 10", "Demo video kit")
callout("Timing is a suggestion.", "Built for about 5 minutes. Scale it to the length the assignment asks for. "
        "Everything runs offline in about 2 seconds, so the demo can be live on screen.", warn=True)
table([["Time", "Segment", "Show", "Say"],
       ["0:00", "Problem & policy", "Section 2 label table", "Crypto giveaway scams; why keyword blocking fails warnings and news; two labels."],
       ["0:40", "Architecture", "Figure 1", "Ingest → normalize → signals → router → review queue. Rules, not an LLM, so every label is explainable."],
       ["1:20", "Live: tests", "pytest -q, then the policy-example tests", "All 97 tests pass; the 7 proposal examples are encoded as tests."],
       ["1:50", "Live: worked examples", "demo snippet below", "Same words, different context: scam vs PSA; homoglyph evasion; official handle; Kalshi campaign."],
       ["2:50", "Live: evaluation", "evaluate.py --split test --source real", "Confusion matrix, baseline, ablations, latency, printed in about a second."],
       ["3:30", "The plot twist", "Figure 3 + iteration table", "0.93 on synthetic, 0.56 on real; what broke; dev-only fixes; 0.72 and 0.91 precision."],
       ["4:20", "Limits & next steps", "Section 9", "Optimistic recall, AI labels, over-flagging; what we'd do next."]],
      [0.45 * inch, 1.15 * inch, 1.9 * inch, 3.4 * inch])
P("Commands", "h2")
for cmd in ["source .venv/bin/activate",
            "python -m pytest -q",
            "python -m pytest -v tests/test_policy_examples.py",
            "python evaluate.py --split test --source real --show-errors",
            "python evaluate.py --split test --source synthetic"]:
    story.append(Paragraph(escape(cmd), ST["code"]))
P("Worked-example snippet (paste into python from the repo root):", "small")
snippet = ("from pylabel import PolicyProposalLabeler\n"
           "from tests.conftest import make_post\n"
           "def show(text, handle='promo.bsky.social', age=3):\n"
           "    d = PolicyProposalLabeler(None, 'labeler-inputs', expand_links=False) \\\n"
           "        .moderate_record(make_post(text, handle=handle, age_days=age))\n"
           "    print(d.labels or ['none'], round(d.score, 1)); [print('  ', r) for r in d.reasons]\n"
           "show('Send 0.1 ETH to 0x5290...9EE7 and we return 0.2 ETH.')\n"
           "show('Beware of scammers promising large airdrops if you send them crypto first.', age=900)")
story.append(Paragraph(escape(snippet).replace("\n", "<br/>").replace("  ", "&nbsp;&nbsp;"), ST["code"]))
P("Live mode (optional): <font face='Mono'>python run_labeler.py labeler-inputs posts.csv</font> needs a .env "
  "with a Bluesky app password. <b>Don't add --emit_labels on camera</b>; it publishes labels.", "small")

P("Worked examples and their signals", "h2")
P("Real output of the v2 labeler. Signal weights in parentheses; \"hard\" marks a hard indicator.", "small")
pick = ["Policy Ex. 1: send-to-receive", "Policy Ex. 7: scam warning", "Policy Ex. 3: impersonation + fee",
        "Policy Ex. 5: wallet connect + urgency", "Evasion: homoglyph + leetspeak", "Official project handle",
        "Real dev: faucet guide (v2 fix)", "Real dev: Kalshi campaign (v2 fix)"]
dd = {d["title"]: d for d in D["demos"]}
rows = [["Case", "Post", "Result", "Signals"]]
for title in pick:
    d = dd[title]
    rows.append([f"<b>{clean(title)}</b><br/><font color='#5b6670'>@{d['handle']}, {d['age']}-day account</font>",
                 clean(d["text"][:120]), f"<b>{(d['labels'] or ['none'])[0]}</b><br/>score {d['score']}",
                 clean("; ".join(d["signals"]))])
for pid in ["p039", "p042", "p034"]:
    r = PRED[PRED.id == pid].iloc[0]
    rows.append([f"<b>Dataset {pid}: {r.category.split('/')[1]}</b>", clean(r.text[:120]),
                 f"<b>{r.predicted_label}</b><br/>score {r.score}", clean(r.reasons[:200])])
table(rows, [1.4 * inch, 2.2 * inch, 0.95 * inch, 2.35 * inch])
P("Talking point: Ex. 1 and Ex. 7 share the words \"send … crypto\", but the warning's counter-signals push it to "
  "−7.0. The faucet guide still triggers send_to_receive, but faucet_context contests it, so it gets no label. That's "
  "the v2 fix for r250–r257.", "small")
story.append(PageBreak())

# ---------------- appendix
section("Appendix", "Reproduction, files, full error list")
P("Reproduce every number in this pack", "h2")
for cmd in ["python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt",
            "python evaluate.py --split test --source real      # real test",
            "python evaluate.py --split test --source synthetic # synthetic test",
            "python evaluate.py --split dev  --source real      # dev (tuning) split",
            "python evaluate.py --split all                     # everything; writes predictions.csv"]:
    story.append(Paragraph(escape(cmd).replace("  ", "&nbsp;&nbsp;"), ST["code"]))
P("Frozen earlier versions are in results/v1-frozen/ and results/v1.1-frozen/. Figure 5 comes from re-running the "
  "evaluation with MEDIUM_THRESHOLD set to 1.5–3.5 on the dev splits.", "small")
P("Files to point graders at", "h2")
table([["Path", "What it is"],
       ["pylabel/policy_proposal_labeler.py", "Required labeler class (moderate_post for URLs, moderate_record offline)"],
       ["pylabel/config.py", "Labels, weights, thresholds, combo rules"],
       ["pylabel/*_signals.py, router.py", "Detectors and routing"],
       ["data.csv", "Required dataset: 340 labeled posts with rationale and annotation status"],
       ["evaluate.py", "Offline evaluation: metrics, baseline, ablations, efficiency"],
       ["tests/", "97 pytest tests incl. policy Examples 1–7 and v2 regressions"],
       ["results/eval_report_*.md", "Generated reports with every error and its signals"],
       ["README.md, ITERATIONS.md, ANNOTATION.md", "Usage, iteration log, annotation rubric and disclosure"]],
      [2.6 * inch, 4.3 * inch])
P("All test-split errors (v2)", "h2")
rows = [["ID", "Gold → pred", "Score", "Post (truncated)"]]
for e in sorted(D["test_errors"], key=lambda e: (e["source"], e["id"])):
    short = {"crypto-scam": "scam", "unverified-airdrop": "review", "none": "none"}
    rows.append([e["id"], f"{short[e['gold']]} → {short[e['pred']]}", str(e["score"]), clean(e["text"][:105])])
table(rows, [0.5 * inch, 1.05 * inch, 0.5 * inch, 4.85 * inch])


# ---------------------------------------------------------------- page template
def decorate(canvas, doc):
    canvas.saveState()
    if doc.page > 1:
        canvas.setFont("Body", 7.5); canvas.setFillColor(MUTED)
        canvas.drawString(0.8 * inch, 0.5 * inch, "Group 8 · CS 5342 Assignment 3 · report & demo source pack")
        canvas.drawRightString(letter[0] - 0.8 * inch, 0.5 * inch, str(doc.page))
        canvas.setStrokeColor(RULE); canvas.setLineWidth(0.5)
        canvas.line(0.8 * inch, 0.65 * inch, letter[0] - 0.8 * inch, 0.65 * inch)
    canvas.restoreState()


os.makedirs(os.path.dirname(OUT), exist_ok=True)
doc = BaseDocTemplate(OUT, pagesize=letter, leftMargin=0.8 * inch, rightMargin=0.8 * inch,
                      topMargin=0.75 * inch, bottomMargin=0.85 * inch,
                      title="Group 8 — A3 report & demo source pack", author="CS 5342 Group 8")
frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="f", leftPadding=0, rightPadding=0,
              topPadding=0, bottomPadding=0)
doc.addPageTemplates([PageTemplate(id="p", frames=[frame], onPage=decorate)])
doc.build(story)
print("wrote", OUT)
