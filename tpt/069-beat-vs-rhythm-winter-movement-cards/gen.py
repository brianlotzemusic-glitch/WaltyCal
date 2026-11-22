#!/usr/bin/env python3
"""Beat vs Rhythm Movement Cards and Echo Strips (TpT 069): build the resource and verify it.

    python3 gen.py           build everything (PDFs, PNGs, UPLOAD.md, tpt.json) into this folder
    python3 gen.py --check   re-read the rendered HTML and verify every card, rhythm, strip, pictogram, page number and layout

Twelve winter movement pictograms (pics.py) and every rhythm (rhythm.py) are drawn in code. The twelve movements each appear twice:
as a steady beat card (cards 1-12) and as a rhythm card (cards 13-24, card n + 12). `--check` does not trust the data: it parses the
rendered SVG of every rhythm (cards, echo strips, vocabulary samples), finds the noteheads, stems, beams and rests from their real
geometry, derives the pattern and the beat total (must be 4 in every bar), tests stem side and direction against the middle line,
beam ends, evenly spaced beat dots, the ta / ti-ti syllable lines and the spoken words, measures pictogram and notation padding on
rendered pixels, and checks layout (8 px footer gap, blank bands, watermarks), page numbers, UPLOAD.md and tpt.json.
"""
import json
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from html import escape

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pics as PC  # noqa: E402
import rhythm as RH  # noqa: E402

TPT = os.path.dirname(HERE)
FONTS = os.path.join(TPT, "fonts")
BUILD = os.path.join(HERE, "build")
RENDER_JS = os.path.join(TPT, "tools", "render.js")
HERO = os.path.join(HERE, "art", "hero.png")

SLUG = "beat-vs-rhythm-movement-cards"
PDF = os.path.join(HERE, f"{SLUG}.pdf")
PREVIEW_PDF = os.path.join(HERE, f"{SLUG}-PREVIEW.pdf")
COVER_PNG = os.path.join(HERE, "cover.png")
PREVIEW_PNGS = [os.path.join(HERE, f"preview-{i}.png") for i in (1, 2, 3)]
UPLOAD = os.path.join(HERE, "UPLOAD.md")
TPT_JSON = os.path.join(HERE, "tpt.json")

STORE = "Brian Lotze"
BRAND = "Hudson Beat"
YEAR = 2026
ACCENT = "#2F86B8"
DISCLOSURE = "Created with the help of digital and AI tools. Notation and answer keys are verified before release."
TITLE = "Beat vs Rhythm Movement Cards"
LISTING_TITLE = "Beat vs Rhythm Movement Cards and Echo Strips, Music Games, K-2"
PRICE = "3.50"
TAGS = ["Winter", "Task Cards", "Games", "Activities", "Printables", "Centers"]
SUBJECTS = ["Music", "Physical Education"]
GRADES = ["kindergarten", "1st-grade", "2nd-grade"]

# ------------------------------------------------------------------ data
MOVES = PC.MOVES                      # 12 movements: id, drawing, title, beat direction, rhythm verb
N_MOVES = len(MOVES)
# rhythm cards 13-24: one four-beat bar each. Q = ta, E = ti-ti, R = quarter rest. Each has at least one ti-ti or rest.
CARD_PATS = ["QQEQ", "EQQQ", "QEQQ", "QQQR", "EEQQ", "QRQQ", "EQEQ", "QQEE", "QEQR", "EQQR", "QEEQ", "RQEQ"]
# echo strips 1-12, all different from the card rhythms
STRIP_PATS = ["QQQQ", "QQRQ", "QEQE", "EEEQ", "QQQE", "EEQE", "ERQQ", "QRQE", "EEEE", "EQRE", "QERE", "RQQE"]
assert len(CARD_PATS) == len(STRIP_PATS) == N_MOVES
assert len(set(CARD_PATS + STRIP_PATS)) == 24 and all(len(p) == 4 for p in CARD_PATS + STRIP_PATS)
BEAT_CARDS = list(range(1, 13))
RHYTHM_CARDS = list(range(13, 25))

SORT_ITEMS = [  # statement, kind, answer
    ("Pat your knees on every pulse, like a heartbeat.", "text", "BEAT"),
    ("", "notation", "RHYTHM"),
    ("It stays steady. It never speeds up or slows down.", "text", "BEAT"),
    ("It is a pattern of long and short sounds.", "text", "RHYTHM"),
    ("", "dots", "BEAT"),
    ("ta (rest) ta ta", "text", "RHYTHM"),
]

# pages
P_COVER, P_T1, P_T2, P_GUIDE = 1, 2, 3, 4
P_BEAT1, P_BEAT2, P_RHY1, P_RHY2, P_ECHO1, P_ECHO2 = 5, 6, 7, 8, 9, 10
P_SORT, P_CHECK, P_ICAN, P_VOCAB, P_TERMS = 11, 12, 13, 14, 15
TOTAL_PAGES = P_TERMS


def card_page(n):
    return {1: P_BEAT1, 2: P_BEAT2, 3: P_RHY1, 4: P_RHY2}[(n - 1) // 6 + 1]


def strip_page(n):
    return P_ECHO1 if n <= 6 else P_ECHO2


PAGE_NAMES = {P_COVER: "cover", P_T1: "Teacher notes: the big idea", P_T2: "Teacher notes: games and pacing", P_GUIDE: "Reading guide",
              P_BEAT1: "Steady beat cards 1–6", P_BEAT2: "Steady beat cards 7–12", P_RHY1: "Rhythm cards 13–18", P_RHY2: "Rhythm cards 19–24",
              P_ECHO1: "Echo strips 1–6", P_ECHO2: "Echo strips 7–12", P_SORT: "Sort mat", P_CHECK: "Assessment checklist", P_ICAN: "I can sheet",
              P_VOCAB: "Vocabulary", P_TERMS: "Terms of use"}
assert sorted(PAGE_NAMES) == list(range(1, TOTAL_PAGES + 1))
XREFS = []        # (page it is printed on, page it points to, text)


def xref(frm, to, text):
    XREFS.append((frm, to, text))
    return text


# ------------------------------------------------------------------ CSS / frame
def font_css():
    f = os.path.relpath(FONTS, BUILD)
    faces = [("Oswald", 300, "normal", "oswald-latin-300-normal"), ("Oswald", 500, "normal", "oswald-latin-500-normal"),
             ("Oswald", 700, "normal", "oswald-latin-700-normal"), ("Oswald", 400, "normal", "oswald-latin-500-normal"),
             ("Source Sans 3", 400, "normal", "source-sans-3-latin-400-normal"), ("Source Sans 3", 400, "italic", "source-sans-3-latin-400-italic"),
             ("Source Sans 3", 600, "normal", "source-sans-3-latin-600-normal"), ("Source Sans 3", 700, "normal", "source-sans-3-latin-700-normal"),
             ("Bravura", 400, "normal", "bravura")]
    return "".join(f"@font-face{{font-family:'{n}';font-weight:{w};font-style:{s};src:url('{f}/{file}.woff2') format('woff2');}}" for n, w, s, file in faces)


CSS = """
@page { size: 8.5in 11in; margin: 0; }
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; background: #fff; color: #000; }
body { font-family: 'Source Sans 3', sans-serif; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
.page { width: 8.5in; height: 11in; position: relative; overflow: hidden; page-break-after: always; break-after: page;
        padding: 0.42in 0.5in 0.38in; display: flex; flex-direction: column; }
.page:last-child { page-break-after: auto; break-after: auto; }
.top { display: flex; justify-content: space-between; align-items: flex-end; border-bottom: 2.2pt solid #000; padding-bottom: 6pt; }
.top .t { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; letter-spacing: .01em; line-height: 1; font-size: 18pt; white-space: nowrap; }
.top .t small { display: block; font-family: 'Oswald'; font-weight: 300; text-transform: none; font-size: 11pt; letter-spacing: 0; margin-top: 3pt; }
.top .tag { flex: none; white-space: nowrap; text-align: right; }
.tag .lv { display: inline-block; background: #000; color: #fff; font-family: 'Oswald'; font-weight: 700; font-size: 15pt; padding: 3pt 9pt 4pt; border-radius: 4pt; letter-spacing: .04em; }
.tag .lv.ak { background: ACCENT; }
.tag .ln { font-family: 'Oswald'; font-weight: 300; font-size: 11pt; margin-top: 3pt; }
.foot { display: flex; justify-content: space-between; font-size: 8.5pt; color: #333; border-top: .8pt solid #000; padding-top: 3pt; }
.wm { position: absolute; left: 50%; top: 50%; transform: translate(-50%, -50%) rotate(-38deg); font-family: 'Oswald'; font-weight: 700;
      font-size: 150pt; color: rgba(0,0,0,.13); letter-spacing: .06em; white-space: nowrap; pointer-events: none; z-index: 9; }
.doc h1 { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 30pt; margin: 0 0 4pt; line-height: 1; }
.doc h2 { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 14pt; margin: 9pt 0 3pt; letter-spacing: .02em; }
.doc p, .doc li { font-size: 10.8pt; line-height: 1.34; margin: 0 0 5pt; }
.doc ul { margin: 0 0 4pt; padding-left: 16pt; }
.doc .rule { border-bottom: 2.2pt solid #000; margin-bottom: 8pt; padding-bottom: 6pt; }
.doc table { border-collapse: collapse; width: 100%; table-layout: fixed; font-size: 10pt; margin: 2pt 0 4pt; }
.doc td, .doc th { border: 1pt solid #000; padding: 3pt 6pt; text-align: left; vertical-align: middle; }
.doc th { font-family: 'Oswald'; font-weight: 500; text-transform: uppercase; font-size: 9.5pt; background: #000; color: #fff; }
.terms p, .terms li { font-size: 11.8pt !important; }
.small { font-size: 9pt !important; color: #333; }
.box { border: 1.3pt solid #000; border-radius: 7pt; padding: 7pt 10pt 4pt; margin: 6pt 0; }
.box h3 { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 12.5pt; margin: 0 0 3pt; letter-spacing: .02em; }
.box p { margin: 0 0 4pt !important; font-size: 10.6pt !important; }
.cols { display: flex; gap: 12pt; }
.cols .box { flex: 1; margin: 6pt 0; }
.nd { display: flex; align-items: flex-end; gap: 6pt; font-size: 10.5pt; margin: 7pt 0 0; }
.nd .ln { flex: 1; border-bottom: 1pt solid #000; height: 11pt; }
.stack { flex: 1; display: flex; flex-direction: column; justify-content: space-between; gap: 7pt; padding: 7pt 0 9pt; }
.inst { font-size: 11pt; line-height: 1.3; margin: 0; }
.dsvg svg { display: block; margin: 2pt auto 4pt; }
.cgrid { flex: 1; display: grid; grid-template-columns: 1fr 1fr; grid-template-rows: 1fr 1fr 1fr; margin: 10pt 0 14px; border-top: 1.2pt dashed #000; border-left: 1.2pt dashed #000; }
.card { border-right: 1.2pt dashed #000; border-bottom: 1.2pt dashed #000; padding: 10px 12px 8px; display: flex; flex-direction: column; justify-content: space-between; overflow: hidden; }
.ctop { display: flex; justify-content: space-between; align-items: center; }
.ck { background: #000; color: #fff; font-family: 'Oswald'; font-weight: 700; letter-spacing: .08em; font-size: 12pt; padding: 1pt 8pt 2pt; border-radius: 3pt; }
.ck.r { background: ACCENT; }
.cn { font-family: 'Oswald'; font-weight: 700; font-size: 13pt; letter-spacing: .04em; }
.cmid { display: flex; align-items: center; gap: 12px; }
.cpic { flex: none; width: 112px; height: 112px; }
.cpic svg { display: block; width: 112px; height: 112px; }
.ctext { flex: 1; }
.ct { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 15.5pt; line-height: 1.02; letter-spacing: .01em; margin-bottom: 4pt; }
.cd { font-size: 11.6pt; line-height: 1.22; }
.cd b { font-family: 'Oswald'; font-weight: 500; letter-spacing: .03em; }
.cbot { display: flex; justify-content: center; align-items: flex-end; padding-top: 2px; }
.cbot svg { display: block; }
.cbot .lab { font-family: 'Oswald'; font-weight: 500; font-size: 10pt; letter-spacing: .08em; text-transform: uppercase; margin-right: 10px; width: 44px; line-height: 1.1; }
.egrid { flex: 1; display: grid; grid-template-rows: repeat(6, 1fr); margin: 10pt 0 14px; border-top: 1.2pt dashed #000; }
.strip { border-bottom: 1.2pt dashed #000; display: flex; align-items: center; gap: 14px; padding: 4px 6px 4px 4px; }
.strip .eh { flex: none; width: 104px; text-align: center; }
.strip .eh .bx { display: inline-block; background: ACCENT; color: #fff; font-family: 'Oswald'; font-weight: 700; font-size: 15pt; letter-spacing: .05em; padding: 2pt 9pt 3pt; border-radius: 4pt; }
.strip .eh .sm { font-family: 'Oswald'; font-weight: 300; font-size: 10.5pt; line-height: 1.15; margin-top: 4pt; }
.strip svg { display: block; flex: none; margin-left: auto; }
.part { border: 1.3pt solid #000; border-radius: 7pt; padding: 7pt 11pt 6pt; }
.part h3 { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 13pt; margin: 0 0 3pt; letter-spacing: .02em; }
.part p { margin: 0 0 4pt; font-size: 10.8pt; line-height: 1.28; }
.part svg { display: block; margin: 3pt 0; }
.two { display: flex; gap: 14pt; }
.two > * { flex: 1; }
.mat { border: 1.4pt dashed #000; border-radius: 8pt; flex: 1; display: flex; align-items: center; justify-content: center; font-family: 'Oswald'; font-weight: 300; font-size: 12pt; color: #333; }
.q { display: flex; align-items: center; gap: 10pt; border-bottom: .8pt solid #999; padding: 5pt 0; min-height: 46pt; }
.q .qn { flex: none; width: 20pt; font-family: 'Oswald'; font-weight: 700; font-size: 14pt; }
.q .qt { flex: 1; font-size: 11.6pt; line-height: 1.2; }
.q .opt { flex: none; display: inline-block; border: 1.3pt solid #000; border-radius: 14pt; padding: 2pt 12pt 3pt; font-family: 'Oswald'; font-weight: 500; letter-spacing: .06em; font-size: 11pt; margin-left: 4pt; }
.vgrid { flex: 1; display: grid; grid-template-columns: 1fr 1fr; grid-template-rows: repeat(4, 1fr); gap: 9pt 12pt; padding: 8pt 0 9pt; margin-bottom: 14px; }
.vc { border: 1.3pt solid #000; border-radius: 7pt; padding: 7pt 10pt; display: flex; flex-direction: column; justify-content: space-between; }
.vc .vw { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 16pt; letter-spacing: .02em; line-height: 1; }
.vc .vw span { font-family: 'Source Sans 3'; font-weight: 400; text-transform: none; font-size: 10.5pt; letter-spacing: 0; margin-left: 6pt; color: #333; }
.vc .vm { font-size: 11pt; line-height: 1.25; }
.vc .vp { display: flex; justify-content: center; align-items: center; min-height: 52pt; }
.vc .vp svg { display: block; }
.chk th, .chk td { text-align: center !important; }
.chk td:first-child, .chk th:first-child { text-align: left !important; }
.chk td { height: 35pt; }
.ic { display: flex; align-items: center; gap: 12pt; border: 1.3pt solid #000; border-radius: 7pt; padding: 5pt 10pt; flex: 1; }
.ic .ib { flex: none; width: 24pt; height: 24pt; border: 1.5pt solid #000; border-radius: 4pt; }
.ic .it { flex: 1; font-size: 13pt; font-weight: 600; line-height: 1.15; }
.ic .it small { display: block; font-weight: 400; font-size: 10.5pt; color: #333; }
.ic .ir { flex: none; display: flex; gap: 8pt; }
.ic .ir i { display: block; width: 24pt; height: 24pt; border: 1.5pt solid #000; border-radius: 50%; }
.cover { align-items: center; justify-content: space-between; padding: 0.55in 0.6in 0.5in; }
.store { font-family: 'Oswald'; font-weight: 500; font-size: 13pt; letter-spacing: .32em; text-transform: uppercase; }
.ctitle { text-align: center; }
.ctitle .a { font-family: 'Oswald'; font-weight: 700; font-size: 46pt; line-height: 1; letter-spacing: .02em; }
.ctitle .b { font-family: 'Oswald'; font-weight: 700; white-space: nowrap; font-size: 62pt; line-height: .95; letter-spacing: .01em; }
.ctitle .c { font-family: 'Oswald'; font-weight: 300; font-size: 17pt; margin-top: 8pt; }
.cband { width: 100%; background: #000; color: #fff; text-align: center; font-family: 'Oswald'; font-weight: 500; font-size: 14pt;
         letter-spacing: .08em; text-transform: uppercase; padding: 8pt 0 9pt; border-radius: 4pt; white-space: nowrap; }
.cband em { font-style: normal; color: ACCENT; }
""".replace("ACCENT", ACCENT)


def html_doc(pages, title="doc"):
    return (f'<!doctype html><html><head><meta charset="utf-8"><title>{escape(title)}</title><style>{font_css()}{CSS}</style></head>'
            f'<body>{"".join(pages)}</body></html>')


COPY = f"© {YEAR} {STORE} · {BRAND} · For single-classroom use"


def foot(left, right):
    return f'<div class="foot"><span>{left}</span><span>{right}</span></div>'


def wm_div(on):
    return '<div class="wm">PREVIEW</div>' if on else ""


def top_block(sub, tag, tagline, ak=False):
    return (f'<div class="top"><div class="t">{TITLE}<small>{sub}</small></div>'
            f'<div class="tag"><div class="lv{" ak" if ak else ""}">{tag}</div><div class="ln">{tagline}</div></div></div>')


def doc_head(h1, sub):
    return f'<div class="rule"><h1>{h1}</h1><div style="font-family:Oswald;font-weight:300;font-size:13pt">{sub}</div></div>'


NAME_DATE = '<div class="nd">Name <span class="ln"></span> Date <span class="ln" style="max-width:130pt;flex:none;width:130pt"></span></div>'


def pg_foot(page, extra=""):
    return foot(COPY + (f" · {extra}" if extra else ""), f"Page {page}")


# ------------------------------------------------------------------ drawings
def acc(svg):
    return svg.replace("ACC", ACCENT)


def rh(pat, sp=7, bw=62, **kw):
    return rhythm_acc(pat, sp, bw, **kw)[0]


def rhythm_acc(pat, sp, bw, **kw):
    s, w, h = RH.rhythm_svg(pat, sp=sp, bw=bw, **kw)
    return acc(s), w, h


def dots_even(width=300, r=9, gap=62, label=None):
    xs = [(width - 3 * gap) / 2 + i * gap for i in range(4)]
    return acc(RH.dots_svg(xs, width, r=r, label=label)[0])


def pic(i, size=None, cls="pic"):
    return PC.pic_svg(i, ACCENT, size=size, cls=cls)


# ------------------------------------------------------------------ cards
def beat_card(n):
    i = n - 1
    return (f'<div class="card" data-card="{n}" data-kind="beat" data-move="{MOVES[i][0]}"><div class="ctop"><span class="ck">STEADY BEAT</span><span class="cn">Card {n}</span></div>'
            f'<div class="cmid"><div class="cpic">{pic(i)}</div><div class="ctext"><div class="ct">{MOVES[i][2]}</div><div class="cd">{MOVES[i][3]}</div></div></div>'
            f'<div class="cbot">{dots_even(label=f"beat-card-{n}")}</div></div>')


def rhythm_direction(i, pat):
    verb = MOVES[i][4]
    t = f'Say <b class="say">{RH.words(pat)}</b>. {verb} once for each sound.'
    if "R" in pat:
        t += " Freeze on the rest."
    else:
        t += " Make each ti-ti quick."
    return t


def rhythm_card(n):
    i = n - 13
    pat = CARD_PATS[i]
    return (f'<div class="card" data-card="{n}" data-kind="rhythm" data-move="{MOVES[i][0]}"><div class="ctop"><span class="ck r">RHYTHM</span><span class="cn">Card {n}</span></div>'
            f'<div class="cmid"><div class="cpic">{pic(i)}</div><div class="ctext"><div class="ct">{MOVES[i][2]}</div><div class="cd">{rhythm_direction(i, pat)}</div></div></div>'
            f'<div class="cbot">{rh(pat, sp=7, bw=62, label=f"rhythm-card-{n}")}</div></div>')


def card_page_html(first, wm=False):
    kind_beat = first <= 12
    page = card_page(first)
    cards = "".join((beat_card if kind_beat else rhythm_card)(n) for n in range(first, first + 6))
    return (f'<section class="page doc" data-page="{page}">{wm_div(wm)}'
            f'{top_block(PAGE_NAMES[page], "STEADY BEAT" if kind_beat else "RHYTHM", "Cut on the dashed lines", ak=not kind_beat)}'
            f'<div class="cgrid">{cards}</div>'
            f'{pg_foot(page, xref(page, P_GUIDE, f"Reading guide on page {P_GUIDE}"))}</section>')


def strip_row(n):
    pat = STRIP_PATS[n - 1]
    return (f'<div class="strip" data-strip="{n}"><div class="eh"><span class="bx">ECHO {n}</span><div class="sm">Teacher claps.<br>Class echoes.</div></div>'
            f'{rh(pat, sp=9, bw=112, label=f"echo-strip-{n}")}</div>')


def echo_page_html(first, wm=False):
    page = strip_page(first)
    rows = "".join(strip_row(n) for n in range(first, first + 6))
    return (f'<section class="page doc" data-page="{page}">{wm_div(wm)}{top_block(PAGE_NAMES[page], "ECHO STRIPS", "Cut on the dashed lines", ak=True)}'
            f'<div class="egrid">{rows}</div>{pg_foot(page, xref(page, P_T2, f"How to play on page {P_T2}"))}</section>')


# ------------------------------------------------------------------ teacher and student pages
def teacher1(wm=False):
    sp, bw = 7, 62
    xs = RH.beat_xs(sp, bw)
    s, w, _ = RH.rhythm_svg("QQEQ", sp=sp, bw=bw, rows=("num", "syl"), label="notes-1")
    dots = acc(RH.dots_svg(xs, w, r=8, nums=False, label="notes-dots")[0])
    return (f'<section class="page doc" data-page="{P_T1}">{wm_div(wm)}{doc_head("Teacher Notes", PAGE_NAMES[P_T1])}'
            f'<p>Young children feel the steady beat in their bodies long before they can read a note. These cards connect the two ideas that every musician needs: the <b>beat</b> and the <b>rhythm</b>. '
            f'Each card gives a winter movement, such as marching like a penguin or rolling a snowball, and asks children to move in one of two ways.</p>'
            f'<div class="cols"><div class="box"><h3>Beat</h3><p>The beat is the <b>steady pulse</b> of the music, like a heartbeat. It stays the same speed. You can pat it, step it or tap it. '
            f'Steady beat cards show a row of four dots: move on every dot.</p></div>'
            f'<div class="box"><h3>Rhythm</h3><p>Rhythm is the pattern of <b>long and short sounds</b> that fits on top of the beat. The words of a song have a rhythm, and so does your name. '
            f'Rhythm cards show the pattern in notes: move to the words.</p></div></div>'
            f'<div class="part" style="margin-top:2pt"><h3>Beat and rhythm together</h3><p style="margin-bottom:0">The dots are the beat. The notes sit on top of it. Count the dots, then say the words: ta, ta, ti-ti, ta.</p>'
            f'<div class="dsvg">{dots}{s}</div></div>'
            f'<h2>Try this first (two minutes)</h2><ul>'
            f'<li>Put a hand on your chest and feel your heartbeat. Pat it gently on your knees. That is the <b>beat</b>.</li>'
            f'<li>Keep patting the beat and say “hot co-coa”. Clap only the words. That is the <b>rhythm</b>. “Hot” is one long sound (ta). “Co-coa” is two quick sounds (ti-ti).</li>'
            f'<li>Ask: “Which one stayed steady, the pat or the words?” The pat did. The words moved on top of it.</li></ul>'
            f'<div class="box"><h3>Same movement, two ways</h3><p>Each of the twelve movements appears twice. First children feel it on every beat (cards 1–12). Later they move to a rhythm (cards 13–24). '
            f'Clap a rhythm while the class pats the beat, so they hear the rhythm sit on top of the beat.</p></div>'
            f'<h2>What is inside ({TOTAL_PAGES} pages)</h2>'
            f'<ul><li>{xref(P_T1, P_GUIDE, f"Page {P_GUIDE}")}: reading guide for ta, ti-ti, the quarter rest and 4/4.</li>'
            f'<li>Pages {P_BEAT1}–{P_BEAT2}: 12 steady beat cards (cards 1–12). Pages {P_RHY1}–{P_RHY2}: 12 rhythm cards (cards 13–24). Card 13 is the rhythm version of card 1, card 14 of card 2, and so on, so children feel the same movement two ways.</li>'
            f'<li>Pages {P_ECHO1}–{P_ECHO2}: 12 rhythm echo strips. Teacher claps, class echoes.</li>'
            f'<li>Page {P_SORT}: sort mat. Page {P_CHECK}: assessment checklist. Page {P_ICAN}: I can sheet. Page {P_VOCAB}: vocabulary. Page {P_TERMS}: terms of use.</li></ul>'
            f'<div style="flex:1"></div>{pg_foot(P_T1, xref(P_T1, P_T2, f"Games and pacing on page {P_T2}"))}</section>')


def teacher2(wm=False):
    pacing = [("Lesson 1 (10–15 min)", "Feel the beat. Do the heartbeat activity from page 2, then try steady beat cards 1–6 and play the freeze game.", f"{P_GUIDE}, {P_BEAT1}"),
              ("Lesson 2 (10–15 min)", "More beat movements. Steady beat cards 7–12. Let children take turns choosing a card.", f"{P_BEAT2}"),
              ("Lesson 3 (10–15 min)", "Meet rhythm. Read the guide together and say ta, ti-ti and rest. Try rhythm cards 13–18, then echo strips 1–6.", f"{P_GUIDE}, {P_RHY1}, {P_ECHO1}"),
              ("Lesson 4 (10–15 min)", "Beat or rhythm? Rhythm cards 19–24 and echo strips 7–12. Play the sorting game, then use the checklist and the I can sheet.", f"{P_RHY2}, {P_ECHO2}, {P_SORT}–{P_ICAN}")]
    prow = "".join(f'<tr><td><b>{a}</b></td><td>{b}</td><td style="text-align:center">{c}</td></tr>' for a, b, c in pacing)
    return (f'<section class="page doc" data-page="{P_T2}">{wm_div(wm)}{doc_head("Teacher Notes", PAGE_NAMES[P_T2])}'
            f'<h2 style="margin-top:2pt">Three games</h2>'
            f'<div class="part" style="margin-bottom:6pt"><h3>1. Beat vs rhythm sorting game</h3><p>Spread out all 24 cards. Cover the colored label at the top of each card with a sticky note. '
            f'Children look at the bottom of the card: a row of dots means <b>steady beat</b>, and notes or rests mean <b>rhythm</b>. They place each card on the matching side of the sort mat '
            f'({xref(P_T2, P_SORT, f"page {P_SORT}")}), then lift the sticky note to check. Play in pairs or at a center.</p></div>'
            f'<div class="part" style="margin-bottom:6pt"><h3>2. Echo game</h3><p>Keep a steady beat on your knees or a drum. Show one echo strip ({xref(P_T2, P_ECHO1, f"pages {P_ECHO1}–{P_ECHO2}")}). '
            f'First say the syllables together (ta, ti-ti, rest). Then clap the strip while the class keeps the beat softly. Then clap it once and let the class echo you. Later a child can be the leader. '
            f'Each strip has four beats, so the echo always fits in one bar.</p></div>'
            f'<div class="part" style="margin-bottom:6pt"><h3>3. Freeze game</h3><p>Play a slow, steady beat. Children move the way a card says, one move on every beat. When the beat stops, everyone freezes like an icicle. '
            f'With rhythm cards, children move once for each sound and freeze on the quarter rest, which is one beat of silence.</p></div>'
            f'<h2>Pacing</h2><table class="vt"><tr><th style="width:23%">Lesson</th><th>Plan</th><th style="width:18%;text-align:center">Pages</th></tr>{prow}</table>'
            f'<h2>Tips</h2><ul><li>Start slowly, at about the speed of a calm walk. A steady beat matters more than a fast one.</li>'
            f'<li>For kindergarten, use steady beat cards 1–12 and rhythm cards 13–15, and echo only strips 1–4. For second grade, let children lead the games and write their own rhythm on the I can sheet.</li>'
            f'</ul>'
            f'<h2>Notes</h2><p>This resource does not cite standards. Match the activities to the music goals your school uses. No songs, lyrics or copyrighted characters are used. '
            f'For assessment, see {xref(P_T2, P_CHECK, f"page {P_CHECK}")} (teacher checklist) and {xref(P_T2, P_ICAN, f"page {P_ICAN}")} (children&rsquo;s I can sheet).</p>'
            f'<div style="flex:1"></div>{pg_foot(P_T2)}</section>')


def guide_page(wm=False):
    sp, bw = 9.5, 100
    xs = RH.beat_xs(sp, bw)
    s, w, _ = RH.rhythm_svg("QQEQ", sp=sp, bw=bw, label="guide-big")
    dots = acc(RH.dots_svg(xs, w, r=10, nums=False, label="guide-dots")[0])
    mini = lambda p: RH.rhythm_svg(p, sp=8, bw=64, clef=False, rows=("syl",), label=f"guide-{p}")[0]
    tiles = [("Q", "ta", "quarter note", "1 beat"), ("E", "ti-ti", "two eighth notes, joined by a beam", "1 beat, two quick sounds"), ("R", "rest", "quarter rest", "1 beat of silence")]
    tl = "".join(f'<div class="part" style="flex:1;text-align:center"><h3 style="margin-bottom:0">{a}</h3><div style="display:flex;justify-content:center">{mini(p)}</div>'
                 f'<p style="margin:0"><b>{b}</b></p><p style="margin:0">{c}</p></div>' for p, a, b, c in tiles)
    return (f'<section class="page doc" data-page="{P_GUIDE}">{wm_div(wm)}{top_block(PAGE_NAMES[P_GUIDE], "READ IT", "Beat and rhythm, step by step")}'
            f'<div class="stack" style="justify-content:space-between">'
            f'<div class="part"><h3>Beat = steady pulse</h3><p style="margin:0">The beat is like a heartbeat. It is steady, like a clock. Move on every dot.</p><div class="dsvg">{acc(RH.dots_svg(xs, w, r=11, nums=True, label="guide-beat")[0])}</div></div>'
            f'<div class="part"><h3>Rhythm = long and short sounds on top of the beat</h3><p style="margin:0">Rhythm is the pattern of sounds. Say the words and move once for each sound. The beat keeps going underneath.</p>'
            f'<div class="dsvg">{dots}{s}</div></div>'
            f'<div><h2 style="margin:0 0 4pt">The three symbols on the cards</h2><div class="two">{tl}</div></div>'
            f'<div class="part"><h3>4/4: four beats in each bar</h3><p style="margin:0">Every rhythm card and echo strip is one bar of four beats. A ta fills one beat. A ti-ti fills one beat. A rest fills one beat too. '
            f'The numbers 1 2 3 4 under each strip count the beats.</p></div></div>'
            f'{pg_foot(P_GUIDE)}</section>')


def sort_page(wm=False):
    rows = []
    for k, (txt, kind, ans) in enumerate(SORT_ITEMS, 1):
        if kind == "notation":
            body = rh("QQEQ", sp=5.5, bw=40, rows=(), label=f"sort-{k}")
        elif kind == "dots":
            body = dots_even(width=190, r=8, gap=44, label=f"sort-{k}").replace('class="dots"', 'class="dots" data-sort="1"')
        else:
            body = txt
        rows.append(f'<div class="q" data-q="{k}" data-ans="{ans}"><span class="qn">{k}</span><div class="qt">{body}</div>'
                    f'<span class="opt">BEAT</span><span class="opt">RHYTHM</span></div>')
    answers = ", ".join(f"{k} {a.lower()}" for k, (_, _, a) in enumerate(SORT_ITEMS, 1))
    return (f'<section class="page doc" data-page="{P_SORT}">{wm_div(wm)}{top_block(PAGE_NAMES[P_SORT], "SORT IT", "Beat or rhythm?")}{NAME_DATE}'
            f'<div class="stack" style="justify-content:flex-start;gap:9pt">'
            f'<p class="inst">Place each card on the side of the mat where it belongs. Then circle <b>BEAT</b> or <b>RHYTHM</b> for each clue below.</p>'
            f'<div class="two" style="flex:1;min-height:0">'
            f'<div class="part" style="display:flex;flex-direction:column"><h3>BEAT</h3><p>Steady pulse, like a heartbeat. Move on every beat.</p>{dots_even(width=170, r=7, gap=40, label="sort-mat-beat")}<div class="mat">Place beat cards here</div></div>'
            f'<div class="part" style="display:flex;flex-direction:column"><h3>RHYTHM</h3><p>Long and short sounds on top of the beat. Move to the words.</p>'
            f'{rh("EQQR", sp=5, bw=34, rows=(), label="sort-mat-rhythm")}<div class="mat">Place rhythm cards here</div></div></div>'
            f'<div class="part" style="padding-bottom:2pt"><h3>Circle it</h3>{"".join(rows)}</div>'
            f'<p class="small" style="margin:0">Teacher answers: {answers}.</p></div>'
            f'{pg_foot(P_SORT)}</section>')


CRITERIA = ["Keeps a steady beat while moving", "Tells beat from rhythm", "Says ta, ti-ti and rest", "Echoes a four-beat rhythm"]


def check_page(wm=False):
    head = "".join(f"<th>{c}</th>" for c in CRITERIA)
    rows = "".join(f"<tr><td></td>{'<td></td>' * len(CRITERIA)}<td></td></tr>" for _ in range(14))
    return (f'<section class="page doc" data-page="{P_CHECK}">{wm_div(wm)}{top_block(PAGE_NAMES[P_CHECK], "CHECKLIST", "Teacher observation")}'
            f'<div class="stack" style="justify-content:flex-start;gap:6pt">'
            f'<p class="inst">Watch children during the games and mark each skill: <b>3</b> every time, <b>2</b> sometimes, <b>1</b> not yet. Class: ____________________ &nbsp; Date: ____________</p>'
            f'<table class="chk"><tr><th style="width:21%">Student</th>{head}<th style="width:16%">Notes</th></tr>{rows}</table>'
            f'<p class="small" style="margin:0">Steady beat: moves on every beat without speeding up. Beat vs rhythm: sorts cards correctly. Syllables: says ta for one sound, ti-ti for two quick sounds and nothing on a rest. '
            f'Echo: repeats a four-beat strip after the teacher.</p></div>'
            f'{pg_foot(P_CHECK)}</section>')


ICAN = [("I can keep a steady beat.", "Pat it, step it or tap it.", "dots"), ("I can tell beat from rhythm.", "Beat is steady. Rhythm is long and short sounds.", None),
        ("I can say ta, ti-ti and rest.", "One sound, two quick sounds, no sound.", None), ("I can move to a rhythm.", "One move for each sound. Freeze on a rest.", None),
        ("I can echo a rhythm.", "Listen, then clap it back.", None), ("I can make my own rhythm.", "Four beats, in the bar below.", None)]


def ican_page(wm=False):
    rows = "".join(f'<div class="ic"><div class="ib"></div><div class="it">{a}<small>{b}</small></div></div>' for a, b, _ in ICAN)
    blank = acc(RH.rhythm_svg(None, sp=8, bw=100, rows=("num", "syl"), label="ican-blank")[0])
    return (f'<section class="page doc" data-page="{P_ICAN}">{wm_div(wm)}{top_block(PAGE_NAMES[P_ICAN], "I CAN", "Show what you know")}{NAME_DATE}'
            f'<div class="stack" style="justify-content:flex-start;gap:8pt"><p class="inst">Color the box when you can do it. Then try the last one.</p>'
            f'<div style="flex:1;display:flex;flex-direction:column;gap:7pt">{rows}</div>'
            f'<div class="part"><h3>My own rhythm</h3><p style="margin-bottom:0">Draw ta, ti-ti or rest on each beat. Write the words under your notes.</p>{blank}</div></div>'
            f'{pg_foot(P_ICAN)}</section>')


VOCAB = [("beat", "BEET", "The steady pulse of music, like a heartbeat.", "dots"), ("rhythm", "RITH-um", "The pattern of long and short sounds that fits on top of the beat.", "QQEQ"),
         ("ta", "tah", "A quarter note. It gets one beat.", "Q"), ("ti-ti", "tee-tee", "Two eighth notes joined by a beam. Together they get one beat.", "E"),
         ("rest", "rest", "A quarter rest. One beat of silence.", "R"), ("echo", "EK-oh", "Listen, then repeat what you heard.", "echo"),
         ("bar", "bar", "One group of beats. A bar in 4/4 has four beats.", "QQQQ"), ("4/4", "four-four", "Four beats in each bar.", "ts")]


def vocab_page(wm=False):
    cells = []
    for w, say, meaning, pv in VOCAB:
        if pv == "dots":
            vp = dots_even(width=200, r=8, gap=48, label="vocab-dots")
        elif pv == "echo":
            vp = PC.pic_svg(9, ACCENT, size=64, cls="pic")
        elif pv == "ts":
            vp = (f'<svg class="tsx" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 60 82" width="60" height="82"><text x="12" y="30" style="font-family:Bravura" font-size="44">{chr(RH.CP_TS4)}</text>'
                  f'<text x="12" y="52" style="font-family:Bravura" font-size="44">{chr(RH.CP_TS4)}</text></svg>')
        elif pv == "QQEQ":
            vp = rh("QQEQ", sp=5.5, bw=46, rows=(), label="vocab-rhythm")
        elif pv == "QQQQ":
            vp = rh("QQQQ", sp=5.5, bw=46, rows=(), label="vocab-bar")
        else:
            vp = RH.rhythm_svg(pv, sp=8, bw=64, clef=False, rows=("syl",), label=f"vocab-{pv}")[0]
        cells.append(f'<div class="vc"><div class="vw">{w}<span>say: {say}</span></div><div class="vp">{vp}</div><div class="vm">{meaning}</div></div>')
    return (f'<section class="page doc" data-page="{P_VOCAB}">{wm_div(wm)}{top_block(PAGE_NAMES[P_VOCAB], "WORDS", "Say it, see it")}'
            f'<div class="vgrid">{"".join(cells)}</div>{pg_foot(P_VOCAB)}</section>')


def terms_page(wm=False):
    return (f'<section class="page doc terms" data-page="{P_TERMS}">{wm_div(wm)}{doc_head("Terms of Use", "Thank you for your purchase!")}'
            f'<p>© {YEAR} {STORE}. {BRAND} by {STORE}. All rights reserved. This purchase gives <b>one teacher</b> a license to use this resource with their own students.</p>'
            f'<h2>You may</h2><ul><li>Print and copy pages for your own classroom and students, year after year.</li>'
            f'<li>Share pages with your own students through a password-protected class site or learning platform.</li>'
            f'<li>Use the pages with your own students when you have a substitute teacher.</li></ul>'
            f'<h2>You may not</h2><ul><li>Share, email or copy this resource for other teachers, a whole school or a district. Additional licenses are available on Teachers Pay Teachers.</li>'
            f'<li>Post any part of it on a public website, shared drive or social media.</li>'
            f'<li>Sell, give away or claim any part of it as your own, or edit it into a new product.</li></ul>'
            f'<h2>Questions?</h2><p>Please use the Q&amp;A tab on the {BRAND} by {STORE} store on Teachers Pay Teachers. If something looks wrong, let me know there and I will fix it.</p>'
            f'<h2>Credits</h2><ul>'
            f'<li>The cards, pictograms, rhythms, echo strips and pages are original work, {BRAND} by {STORE}.</li>'
            f'<li>The cover illustration is made with AI tools. The pictograms, notation, tables and text are drawn in code.</li>'
            f'<li>Music notation font: Bravura © Steinberg Media Technologies GmbH, SIL Open Font License 1.1.</li>'
            f'<li>Text fonts: Oswald (The Oswald Project Authors) and Source Sans 3 (Adobe), SIL Open Font License 1.1.</li></ul>'
            f'<h2>Printing tips</h2><ul><li>Print the card and strip pages single-sided on cardstock, then cut on the dashed lines. Color or black and white both work.</li>'
            f'<li>Laminate the cards if you want them to last. Pages {P_SORT}–{P_ICAN} are for copying.</li></ul>'
            f'<h2>What is in this file ({TOTAL_PAGES} pages)</h2><p>Page 1 cover, pages {P_T1}–{P_T2} teacher notes, page {P_GUIDE} reading guide, pages {P_BEAT1}–{P_BEAT2} steady beat cards, '
            f'pages {P_RHY1}–{P_RHY2} rhythm cards, pages {P_ECHO1}–{P_ECHO2} echo strips, page {P_SORT} sort mat, page {P_CHECK} checklist, page {P_ICAN} I can sheet, page {P_VOCAB} vocabulary and page {P_TERMS} these terms.</p>'
            f'<p class="small">{DISCLOSURE}</p><div style="flex:1"></div>{pg_foot(P_TERMS)}</section>')


def cover_art_img(height):
    return f'<img src="../art/hero.png" alt="" style="display:block;height:{height};width:auto">'


def cover_page():
    return (f'<section class="page cover"><div class="store">{BRAND}</div>'
            f'<div style="height:4.6in;display:flex;align-items:center;justify-content:center">{cover_art_img("4.6in")}</div>'
            f'<div class="ctitle"><div class="a">BEAT VS RHYTHM</div><div class="b">MOVEMENT CARDS</div>'
            f'<div class="c">24 movement cards · 12 echo strips · music games</div></div>'
            f'<div class="cband">Grades K–2 <em>·</em> 24 cards <em>·</em> {TOTAL_PAGES} pages</div></section>')


def full_pages():
    XREFS.clear()
    pages = [cover_page(), teacher1(), teacher2(), guide_page(), card_page_html(1), card_page_html(7), card_page_html(13), card_page_html(19),
             echo_page_html(1), echo_page_html(7), sort_page(), check_page(), ican_page(), vocab_page(), terms_page()]
    assert len(pages) == TOTAL_PAGES, len(pages)
    return pages


PREVIEW_PAGES = [P_GUIDE, P_BEAT1, P_RHY1, P_ECHO1]


def preview_pages():
    return [guide_page(True), card_page_html(1, True), card_page_html(13, True), echo_page_html(1, True)]


# ------------------------------------------------------------------ square images
SQ_CSS = """
.sq { width: 1000px; height: 1000px; position: relative; overflow: hidden; background: #fff; display: flex; flex-direction: column; align-items: center; }
.sq .store { font-family: 'Oswald'; font-weight: 500; letter-spacing: .32em; text-transform: uppercase; font-size: 22px; margin-top: 34px; }
.sq .hd { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; text-align: center; line-height: .95; }
.sq .sub { font-family: 'Oswald'; font-weight: 300; text-align: center; }
.sq .band { position: absolute; left: 0; right: 0; bottom: 0; background: #000; color: #fff; text-align: center; font-family: 'Oswald';
            font-weight: 500; text-transform: uppercase; letter-spacing: .1em; font-size: 26px; padding: 16px 0 18px; }
.sq .band em { font-style: normal; color: ACCENT; }
.shot { background: #fff; border: 2px solid #000; box-shadow: 8px 8px 0 #000; position: relative; overflow: hidden; }
.shot img { display: block; width: 100%; }
.lbl { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 22px; text-align: center; margin-top: 16px; }
.lbl span { font-weight: 300; text-transform: none; display: block; font-size: 18px; }
.swm { position: absolute; left: 50%; top: 50%; transform: translate(-50%,-50%) rotate(-38deg); font-family: 'Oswald'; font-weight: 700;
       color: rgba(0,0,0,.13); white-space: nowrap; letter-spacing: .06em; pointer-events: none; z-index: 5; }
.pill { border: 2px solid #000; border-radius: 30px; padding: 6px 22px; font-family: Oswald; font-weight: 500; font-size: 24px; letter-spacing: .06em; text-transform: uppercase; white-space: nowrap; }
""".replace("ACCENT", ACCENT)


def sq_doc(body):
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{font_css()}html,body{{margin:0;background:#fff;font-family:"Source Sans 3",sans-serif}}{SQ_CSS}</style></head><body>'
            f'{body}</body></html>')


def cover_square():
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div>'
        f'<div style="flex:1;display:flex;flex-direction:column;justify-content:space-evenly;align-items:center;width:100%;padding:0 0 76px">'
        f'<div style="height:500px;overflow:visible;display:block;margin-top:20px"><img src="../art/hero.png" alt="" style="display:block;height:860px;width:auto;margin:-200px 0 0 0"></div>'
        f'<div><div class="hd" style="font-size:74px">Beat vs Rhythm</div><div class="hd" style="font-size:112px">Movement Cards</div>'
        f'<div class="sub" style="font-size:28px;margin-top:12px">24 movement cards · 12 echo strips · music games</div></div>'
        f'</div><div class="band">Grades K–2 <em>·</em> 24 cards <em>·</em> {TOTAL_PAGES} pages</div></div>')


def swm_over(size=230):
    return f'<div class="swm" style="font-size:{size}px">PREVIEW</div>'


def shot(src, w):
    return f'<div class="shot" style="width:{w}px"><img src="{src}"></div>'


def pill_row(items):
    return '<div style="display:flex;gap:18px">' + "".join(f'<div class="pill">{t}</div>' for t in items) + "</div>"


def trio(img, caps, head, sub, pills, bandtxt):
    shots = "".join(
        f'<div style="width:290px;display:flex;flex-direction:column;align-items:center">{shot(img[i], 290)}'
        f'<div class="lbl" style="font-size:22px;margin-top:20px">{caps[i][0]}</div>'
        f'<div style="font-family:Oswald;font-weight:300;font-size:20px;line-height:1.25;text-align:center;margin-top:8px;width:270px">{caps[i][1]}</div></div>' for i in range(3))
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div><div class="hd" style="font-size:72px;margin-top:28px">{head}</div>'
        f'<div class="sub" style="font-size:28px;margin-top:10px">{sub}</div>'
        f'<div style="flex:1;display:flex;flex-direction:column;align-items:center;justify-content:space-evenly;padding-bottom:70px">'
        f'<div style="display:flex;gap:22px;align-items:flex-start">{shots}</div>{pill_row(pills)}</div>'
        f'{swm_over(230)}<div class="band">{bandtxt}</div></div>')


def preview_square_1(img):
    caps = [(PAGE_NAMES[P_BEAT1], "A pictogram, a direction and four beat dots"), (PAGE_NAMES[P_RHY1], "Move to the words in ta and ti-ti"), (PAGE_NAMES[P_ECHO1], "Teacher claps, class echoes")]
    return trio(img, caps, "What is inside", "Three kinds of pages, one big idea", ["12 beat cards", "12 rhythm cards", "12 echo strips"],
                "Beat <em>·</em> Rhythm <em>·</em> Echo")


def preview_square_2(a, b):
    pair = "".join(f'<div style="width:380px">{shot(src, 380)}<div class="lbl">{lab}<span>{sub}</span></div></div>'
                   for src, lab, sub in ((a, PAGE_NAMES[P_GUIDE], "Beat is a steady pulse. Rhythm sits on top."), (b, PAGE_NAMES[P_SORT], "Sort the cards, then circle beat or rhythm")))
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div><div class="hd" style="font-size:72px;margin-top:24px">Beat vs rhythm</div>'
        f'<div class="sub" style="font-size:27px;margin-top:8px">Teach it, then sort it</div>'
        f'<div style="flex:1;display:flex;align-items:center;padding-bottom:70px"><div style="display:flex;gap:44px;align-items:flex-start">{pair}</div></div>'
        f'{swm_over(230)}<div class="band">Reading guide <em>·</em> Sorting game <em>·</em> 4/4 bars</div></div>')


def preview_square_3(img):
    caps = [(PAGE_NAMES[P_CHECK], "Four skills to watch for"), (PAGE_NAMES[P_ICAN], "Self-check and a rhythm to write"), (PAGE_NAMES[P_VOCAB], "Eight words with pictures")]
    return trio(img, caps, "Check and review", "Grades K–2", ["Checklist", "I can sheet", "Vocabulary"],
                "Assess <em>·</em> Review <em>·</em> Reuse")


# ------------------------------------------------------------------ render / build
def node_env():
    env = dict(os.environ)
    if not env.get("NODE_PATH"):
        env["NODE_PATH"] = subprocess.run(["npm", "root", "-g"], capture_output=True, text=True).stdout.strip()
    return env


def render(jobs):
    path = os.path.join(BUILD, "jobs.json")
    with open(path, "w") as fh:
        json.dump(jobs, fh)
    subprocess.run(["node", RENDER_JS, path], check=True, env=node_env())


def write(name, text):
    p = os.path.join(BUILD, name)
    with open(p, "w") as fh:
        fh.write(text)
    return p


PAGE_LIST = [("Cover", 1), ("Teacher notes: the big idea, how to play and pacing", 2), ("Reading guide for beat, rhythm, ta, ti-ti, rest and 4/4", 1),
             ("Steady beat cards 1–12", 2), ("Rhythm cards 13–24", 2), ("Rhythm echo strips 1–12", 2), ("Sort mat with circle-it questions", 1),
             ("Assessment checklist", 1), ("I can sheet", 1), ("Vocabulary", 1), ("Terms of use and credits", 1)]
assert sum(c for _, c in PAGE_LIST) == TOTAL_PAGES


def upload_md():
    lst = "\n".join(f"- {n}: {c}" for n, c in PAGE_LIST)
    return f"""# UPLOAD: {LISTING_TITLE} (TpT 069)

These fields follow the order of TpT's "Add a resource" form. Winter-themed content, non-religious; the title leaves out seasonal words.

**Files to attach**
- Resource (digital download): `{SLUG}.pdf`, {TOTAL_PAGES} pages, US Letter.
- Thumbnails, in this order: `cover.png`, `preview-1.png`, `preview-2.png`, `preview-3.png` (all 2000 × 2000).
- Preview file: `{SLUG}-PREVIEW.pdf`, 4 watermarked pages.

## 1. Title

```
{LISTING_TITLE}
```
({len(LISTING_TITLE)} characters; the limit is 80.) Plain search words first, no seasonal words in the title.

## 2. Description

```
Help young children feel the difference between the BEAT and the RHYTHM. Beat vs Rhythm Movement Cards gives you 24 cut-apart movement cards with simple winter pictograms (marching like a penguin, skating, snowshoe walking, shoveling snow, rolling a snowball, sled sliding, tiptoeing on ice and more), plus 12 rhythm echo strips for a clap-and-echo game. Everything is non-religious and winter themed (snow, boots, mittens and cocoa), so it fits any school calendar.

BEAT = a steady pulse, like a heartbeat. RHYTHM = long and short sounds that fit on top of the beat. The cards teach both ideas through movement.

12 STEADY BEAT CARDS (cards 1-12): one winter movement, a one-line direction and a row of four beat dots. Children move on every beat.

12 RHYTHM CARDS (cards 13-24): the same twelve movements and pictograms as cards 1-12 (12 different pictures, each used on two cards, n and n+12), now with a four-beat rhythm in kid-friendly notation (ta, ti-ti and the quarter rest) and the words to say. Children move to the words.

12 RHYTHM ECHO STRIPS: four beats each, with notes, beamed pairs of eighth notes and rests drawn correctly, plus a ta / ti-ti syllable line and beat numbers. The teacher claps, the class echoes. Every card and strip is one bar of 4/4.

WHAT'S INCLUDED ({TOTAL_PAGES} pages, PDF, US Letter)
• Cover (1 page)
• Teacher notes with the big idea, three games (beat vs rhythm sorting, echo and freeze) and pacing over four short lessons (2 pages)
• Reading guide for beat, rhythm, ta, ti-ti, rest and 4/4 (1 page)
• Steady beat cards 1-12, six per page (2 pages)
• Rhythm cards 13-24, six per page (2 pages)
• Rhythm echo strips 1-12, six per page (2 pages)
• Sort mat with circle-it questions (1 page)
• Assessment checklist (1 page)
• I can sheet (1 page)
• Vocabulary (1 page)
• Terms of use and credits (1 page)
Total: {TOTAL_PAGES} pages.

HOW TO USE
Print the card and strip pages on cardstock, cut on the dashed lines and laminate if you like. Use them for a music center, a movement break, a warm-up or a sub plan. Children sort cards into beat and rhythm, move to the cards, echo the strips and show what they know on the checklist and I can sheet.

• Grades K-2
• Prints well in black and white
• No songs, lyrics or copyrighted characters
• No standards cited: match the activities to your own music goals

{DISCLOSURE}
```

## 3. Grades

Kindergarten, 1st and 2nd.

## 4. Subjects and tags

- Subjects: {", ".join(SUBJECTS)}
- Tags: {", ".join(TAGS)}

## 5. Page count by section (totals {TOTAL_PAGES})

{lst}
- Total: {TOTAL_PAGES}

## 6. Standards

None cited. The teacher notes say so and ask teachers to match the activities to their own music goals.

## 7. Price

**${PRICE}** (paid; owner range $3-5).

## 8. Preview

Paid. Preview PDF: the reading guide (page {P_GUIDE}), steady beat cards 1-6 (page {P_BEAT1}), rhythm cards 13-18 (page {P_RHY1}) and echo strips 1-6 (page {P_ECHO1}), all watermarked.

## 9. Before you click publish

- Season: winter, non-religious. Build window: December and January.
- Art: the cover illustration (snow boots, footprints and a hand drum) is made with AI tools (the disclosure line covers it); pictograms, notation and pages are drawn in code.
- Open owner question: logo beside HUDSON BEAT (see tpt/STYLE.md).
"""


def tpt_json():
    return {"price": PRICE, "license_price": PRICE, "tax_code": "Other Digital Goods - No Physical Media", "grades": GRADES, "subjects": SUBJECTS, "tags": TAGS,
            "formats": ["PDF"], "pages": TOTAL_PAGES, "answer_key": "Not Included",
            "files": {"product": f"{SLUG}.pdf", "preview": f"{SLUG}-PREVIEW.pdf", "thumb1": "cover.png", "thumb2": "preview-1.png", "thumb3": "preview-2.png", "thumb4": "preview-3.png"}}


SHOT_PAGES = [P_BEAT1, P_RHY1, P_ECHO1, P_GUIDE, P_SORT, P_CHECK, P_ICAN, P_VOCAB]


def build():
    os.makedirs(BUILD, exist_ok=True)
    full = write("resource.html", html_doc(full_pages(), TITLE))
    prev = write("preview.html", html_doc(preview_pages(), "Preview"))
    render([{"html": full, "pdf": PDF}, {"html": prev, "pdf": PREVIEW_PDF}])
    for i in SHOT_PAGES:
        subprocess.run(["pdftoppm", "-png", "-r", "150", "-f", str(i), "-l", str(i), "-singlefile", PDF, os.path.join(BUILD, f"pg{i}")], check=True)
    sq = [write("cover.html", cover_square()),
          write("p1.html", preview_square_1([f"pg{P_BEAT1}.png", f"pg{P_RHY1}.png", f"pg{P_ECHO1}.png"])),
          write("p2.html", preview_square_2(f"pg{P_GUIDE}.png", f"pg{P_SORT}.png")),
          write("p3.html", preview_square_3([f"pg{P_CHECK}.png", f"pg{P_ICAN}.png", f"pg{P_VOCAB}.png"]))]
    render([{"html": h, "png": o, "width": 1000, "height": 1000, "scale": 2} for h, o in zip(sq, [COVER_PNG] + PREVIEW_PNGS)])
    with open(UPLOAD, "w") as fh:
        fh.write(upload_md())
    with open(TPT_JSON, "w") as fh:
        json.dump(tpt_json(), fh, indent=2)
        fh.write("\n")
    print(f"built {PDF}, {PREVIEW_PDF}, cover + 3 previews, UPLOAD.md, tpt.json")


if __name__ == "__main__" and "--check" not in sys.argv:
    build()


# ------------------------------------------------------------------ checks
# Everything below re-reads the rendered HTML/SVG/PDF. It does not import the pattern lists except to compare against them.
SVG_RE = re.compile(r'<svg class="(?:rh)".*?</svg>', re.S)
SVG_ANY = re.compile(r'<svg class="(?:rh|dots|pic|tsx)"[^>]*>.*?</svg>', re.S)


def local(tag):
    return tag.split("}")[-1]


def num(v):
    return float(v)


def parse_rh(svg):
    """Return (derived pattern, list of errors) from the geometry of one rendered rhythm SVG."""
    errs = []
    root = ET.fromstring(svg)
    sp = num(root.get("data-sp"))
    bw = num(root.get("data-bw"))
    x0 = num(root.get("data-x0"))
    lead = num(root.get("data-lead"))
    beats_attr = int(root.get("data-beats"))
    has_clef = root.get("data-clef") == "1"
    label = root.get("data-label") or "?"
    lines = sorted(num(e.get("y1")) for e in root.iter() if local(e.tag) == "line" and e.get("class") == "sl")
    if len(lines) != 5 or any(abs((lines[i + 1] - lines[i]) - sp) > 0.05 for i in range(4)):
        errs.append(f"{label}: staff is not five lines one space apart")
        return "", errs
    top, bottom, mid = lines[0], lines[4], lines[2]
    heads, stems, beams, rests, syl, cnt, ts, clef, bars = [], [], [], [], [], [], [], [], []
    for e in root.iter():
        t, c = local(e.tag), e.get("class")
        if t == "text":
            ch = (e.text or "").strip()
            d = {"x": num(e.get("x")), "y": num(e.get("y")), "t": ch}
            if c == "nh":
                heads.append(d)
            elif c == "rest":
                rests.append(d)
            elif c == "syl":
                syl.append(d)
            elif c == "cnt" or c == "num":
                cnt.append(d)
            elif c == "ts":
                ts.append(d)
            elif c == "clef":
                clef.append(d)
        elif t == "rect":
            d = {"x": num(e.get("x")), "y": num(e.get("y")), "w": num(e.get("width")), "h": num(e.get("height"))}
            (stems if c == "stem" else beams if c == "beam" else bars if c == "bar" else []).append(d)
    for h in heads:
        if h["t"] != chr(0xE0A4):
            errs.append(f"{label}: a notehead is not the Bravura black notehead")
    for r in rests:
        if r["t"] != chr(0xE4E5) or abs(r["y"] - mid) > 0.05 * sp:
            errs.append(f"{label}: a quarter rest is not the quarter rest glyph on the middle line")
    # stems: each notehead needs exactly one stem on the correct side for its staff position
    for h in heads:
        step = round((bottom - h["y"]) / (sp / 2))          # half-spaces above the bottom line
        want_down = step >= 4                               # on or above the middle line: stem down
        if not want_down:
            errs.append(f"{label}: a notehead below the middle line would need an up stem")
        mine = [s for s in stems if abs(s["x"] - h["x"]) < 0.5 * sp or abs(s["x"] + s["w"] - (h["x"] + 1.18 * sp)) < 0.5 * sp]
        mine = [s for s in mine if abs((s["x"]) - h["x"]) < 0.02 * sp or abs((s["x"] + s["w"]) - (h["x"] + 1.18 * sp)) < 0.02 * sp]
        if len(mine) != 1:
            errs.append(f"{label}: notehead at x={h['x']:.1f} has {len(mine)} stems")
            continue
        s = mine[0]
        on_left = abs(s["x"] - h["x"]) < 0.02 * sp
        on_right = abs((s["x"] + s["w"]) - (h["x"] + 1.18 * sp)) < 0.02 * sp
        goes_down = s["y"] + s["h"] / 2 > h["y"]
        if want_down and not (on_left and goes_down):
            errs.append(f"{label}: a down stem must sit on the left edge of the notehead and go down")
        if not want_down and not (on_right and not goes_down):
            errs.append(f"{label}: an up stem must sit on the right edge and go up")
        if abs(s["y"] - (h["y"] - 0.168 * sp)) > 0.03 * sp or abs(s["h"] - 3.5 * sp) > 0.05 * sp:
            errs.append(f"{label}: stem does not start at the notehead edge or is not 3.5 spaces long")
        s["head"] = h
    if len(stems) != len(heads):
        errs.append(f"{label}: {len(stems)} stems for {len(heads)} noteheads")
    # beams: every beam covers exactly two consecutive stems and ends flush with their ends
    beamed = set()
    for bm in beams:
        inside = [s for s in stems if s["x"] >= bm["x"] - 0.02 * sp and s["x"] + s["w"] <= bm["x"] + bm["w"] + 0.02 * sp]
        if len(inside) != 2:
            errs.append(f"{label}: a beam joins {len(inside)} stems, expected 2")
            continue
        a, b = sorted(inside, key=lambda s: s["x"])
        if abs(bm["x"] - a["x"]) > 0.02 * sp or abs(bm["x"] + bm["w"] - (b["x"] + b["w"])) > 0.02 * sp:
            errs.append(f"{label}: a beam does not run from the first stem to the second")
        if abs((bm["y"] + bm["h"]) - (a["y"] + a["h"])) > 0.02 * sp or abs(bm["h"] - 0.5 * sp) > 0.05 * sp:
            errs.append(f"{label}: a beam is not flush with the stem ends or is the wrong thickness")
        if abs((b["head"]["x"] - a["head"]["x"]) - bw / 2) > 0.05 * sp:
            errs.append(f"{label}: beamed eighths are not half a beat apart")
        beamed.update((id(a), id(b)))
    # events on the beat grid
    ev = []
    for s in stems:
        h = s.get("head")
        if h is None:
            continue
        dur = 0.5 if id(s) in beamed else 1.0
        ev.append((h["x"], dur, "e" if dur == 0.5 else "q"))
    for r in rests:
        ev.append((r["x"], 1.0, "r"))
    ev.sort()
    t, seq = 0.0, []
    for x, dur, kind in ev:
        onset = (x - x0 - lead) / bw
        if abs(onset - t) > 0.02:
            errs.append(f"{label}: event at beat position {onset:.2f} but the bar has reached {t:.2f}")
        t += dur
        seq.append((kind, dur))
    if abs(t - beats_attr) > 0.001:
        errs.append(f"{label}: the bar adds up to {t} beats, expected {beats_attr}")
    pat = ""
    i = 0
    while i < len(seq):
        k, d = seq[i]
        if k == "e":
            if i + 1 >= len(seq) or seq[i + 1][0] != "e":
                errs.append(f"{label}: a lone eighth note")
                break
            pat += "E"
            i += 2
        else:
            pat += "Q" if k == "q" else "R"
            i += 1
    if root.get("data-pat") != "" and root.get("data-pat") != pat:
        errs.append(f"{label}: drawn rhythm {pat} differs from the stored pattern {root.get('data-pat')}")
    # syllables and counts: one per beat, centred on the beat's sound, matching what is drawn
    want_syl = ["(rest)" if c == "R" else {"Q": "ta", "E": "ti-ti"}[c] for c in pat]
    got = [s["t"] for s in sorted(syl, key=lambda d: d["x"])]
    if syl and got != want_syl:
        errs.append(f"{label}: syllable line {got} does not match the notation {want_syl}")
    if cnt and [c["t"] for c in sorted(cnt, key=lambda d: d["x"])] != [str(k + 1) for k in range(len(pat))]:
        errs.append(f"{label}: beat numbers are not 1..{len(pat)}")
    for k, s in enumerate(sorted(syl, key=lambda d: d["x"])):
        if not (x0 + k * bw <= s["x"] <= x0 + (k + 1) * bw):
            errs.append(f"{label}: syllable {k + 1} sits outside its beat")
    # clef, time signature, barlines
    if has_clef:
        if len(clef) != 1 or clef[0]["t"] != chr(0xE069) or abs(clef[0]["y"] - mid) > 0.05 * sp:
            errs.append(f"{label}: percussion clef missing or off the middle line")
        digs = sorted(ts, key=lambda d: d["y"])
        if len(digs) != 2 or any(d["t"] != chr(0xE084) for d in digs) or abs(digs[0]["y"] - (mid - sp)) > 0.05 * sp or abs(digs[1]["y"] - (mid + sp)) > 0.05 * sp:
            errs.append(f"{label}: time signature is not 4 over 4 centred in the staff")
    else:
        if clef or ts:
            errs.append(f"{label}: a bare symbol sample carries a clef or time signature")
    thick = [b for b in bars if abs(b["w"] - 0.5 * sp) < 0.02 * sp]
    thin = sorted((b for b in bars if abs(b["w"] - 0.16 * sp) < 0.02 * sp), key=lambda b: b["x"])
    if len(thick) != 1 or len(thin) != 2:
        errs.append(f"{label}: expected a start barline and a final barline (thin + thick)")
    elif ev and ev[-1][0] + 1.18 * sp > thin[-1]["x"]:
        errs.append(f"{label}: the last note touches the final barline")
    for b in bars:
        if abs(b["y"] - top) > 0.02 * sp or abs(b["h"] - 4 * sp) > 0.02 * sp:
            errs.append(f"{label}: a barline does not span the staff")
    return pat, errs


def parse_dots(svg):
    root = ET.fromstring(svg)
    cs = sorted((num(e.get("cx")), num(e.get("cy")), num(e.get("r"))) for e in root.iter() if local(e.tag) == "circle")
    return cs, root.get("data-label")


def verify_html():
    errs = []
    html = open(os.path.join(BUILD, "resource.html")).read()
    # map every card / strip to the page it is on
    secs = re.split(r'<section class="page', html)[1:]
    page_of = {}
    for sec in secs:
        m = re.search(r'data-page="(\d+)"', sec)
        pg = int(m.group(1)) if m else 1
        for c in re.findall(r'data-card="(\d+)"', sec):
            page_of[("card", int(c))] = pg
        for c in re.findall(r'data-strip="(\d+)"', sec):
            page_of[("strip", int(c))] = pg
    if sorted(n for k, n in page_of if k == "card") != list(range(1, 25)):
        errs.append("cards are not numbered 1-24 exactly once")
    if sorted(n for k, n in page_of if k == "strip") != list(range(1, 13)):
        errs.append("echo strips are not numbered 1-12 exactly once")
    for n in range(1, 25):
        if page_of.get(("card", n)) != card_page(n):
            errs.append(f"card {n} is on page {page_of.get(('card', n))}, expected {card_page(n)}")
    for n in range(1, 13):
        if page_of.get(("strip", n)) != strip_page(n):
            errs.append(f"strip {n} is on page {page_of.get(('strip', n))}, expected {strip_page(n)}")
    # cards
    parts = re.split(r'(?=<div class="card" data-card=)', html)[1:]
    cards = []
    for p in parts:
        m = re.match(r'<div class="card" data-card="(\d+)" data-kind="(\w+)" data-move="(\w+)">', p)
        cards.append((m.group(1), m.group(2), m.group(3), p.split('<div class="foot">')[0]))
    if len(cards) != 24:
        errs.append(f"found {len(cards)} cards in the rendered HTML")
    derived = {}
    movenames = [m[0] for m in MOVES]
    for n, kind, move, body in cards:
        n = int(n)
        if (kind == "beat") != (n <= 12):
            errs.append(f"card {n}: kind {kind} is wrong for its number")
        if move != movenames[(n - 1) % 12]:
            errs.append(f"card {n}: movement {move} does not match card {(n - 1) % 12 + 1}'s movement")
        pm = re.search(r'<svg class="pic" data-pic="(\w+)"', body)
        if not pm or pm.group(1) != move:
            errs.append(f"card {n}: pictogram does not match its movement")
        tm = re.search(r'<div class="ct">([^<]+)</div>', body)
        if not tm or tm.group(1) != MOVES[(n - 1) % 12][2]:
            errs.append(f"card {n}: title does not match the movement")
        if f">Card {n}<" not in body:
            errs.append(f"card {n}: number label missing")
        want_tag = "STEADY BEAT" if kind == "beat" else "RHYTHM"
        if f">{want_tag}<" not in body:
            errs.append(f"card {n}: wrong type label")
        if kind == "beat":
            if "rh" in re.findall(r'<svg class="(\w+)"', body):
                errs.append(f"card {n}: a beat card carries notation")
            dm = re.search(r'<svg class="dots".*?</svg>', body, re.S)
            if not dm:
                errs.append(f"card {n}: no beat-dot row")
                continue
            cs, _ = parse_dots(dm.group(0))
            if len(cs) != 4 or len({round(c[1], 2) for c in cs}) != 1 or len({c[2] for c in cs}) != 1:
                errs.append(f"card {n}: the beat row is not four same-size dots on one line")
            else:
                gaps = [cs[i + 1][0] - cs[i][0] for i in range(3)]
                if max(gaps) - min(gaps) > 0.01 or gaps[0] < 2.2 * cs[0][2]:
                    errs.append(f"card {n}: the four beat dots are not evenly spaced")
            if "on every beat" not in body:
                errs.append(f"card {n}: direction does not say to move on every beat")
        else:
            sm = SVG_RE.search(body)
            if not sm:
                errs.append(f"card {n}: no rhythm notation")
                continue
            pat, e = parse_rh(sm.group(0))
            errs += e
            derived[("card", n)] = pat
            if "R" not in pat and "E" not in pat:
                errs.append(f"card {n}: a rhythm card needs a ti-ti or a rest")
            say = re.search(r'<b class="say">([^<]+)</b>', body)
            if not say or say.group(1) != RH.words(pat) or say.group(1) != " ".join("(rest)" if c == "R" else {"Q": "ta", "E": "ti-ti"}[c] for c in pat):
                errs.append(f"card {n}: the spoken words do not match the drawn rhythm {pat}")
            if ("Freeze on the rest" in body) != ("R" in pat):
                errs.append(f"card {n}: rest instruction does not match the rhythm")
            if pat != CARD_PATS[n - 13]:
                errs.append(f"card {n}: drawn rhythm {pat} differs from the data")
    # echo strips
    strips = [(m.group(1), p.split('<div class="foot">')[0]) for p in re.split(r'(?=<div class="strip" data-strip=)', html)[1:]
              for m in [re.match(r'<div class="strip" data-strip="(\d+)">', p)]]
    if len(strips) != 12:
        errs.append(f"found {len(strips)} echo strips")
    for n, body in strips:
        n = int(n)
        sm = SVG_RE.search(body)
        if not sm:
            errs.append(f"strip {n}: no notation")
            continue
        pat, e = parse_rh(sm.group(0))
        errs += e
        derived[("strip", n)] = pat
        if f">ECHO {n}<" not in body:
            errs.append(f"strip {n}: label missing")
        if pat != STRIP_PATS[n - 1]:
            errs.append(f"strip {n}: drawn rhythm {pat} differs from the data")
    allp = list(derived.values())
    if len(allp) != 24 or len(set(allp)) != 24:
        errs.append("the 12 card rhythms and 12 echo strips are not 24 different patterns")
    # every other rhythm drawing in the book (guide, vocabulary, sort mat, teacher notes, I can)
    other = 0
    for m in SVG_RE.finditer(html):
        s = m.group(0)
        lab = re.search(r'data-label="([^"]*)"', s).group(1)
        if lab.startswith(("rhythm-card", "echo-strip")):
            continue
        other += 1
        pat, e = parse_rh(s) if 'data-pat=""' not in s else ("", [])
        errs += e
        if 'data-pat=""' in s and lab != "ican-blank":
            errs.append(f"{lab}: an empty staff outside the I can sheet")
    if other < 8:
        errs.append(f"only {other} supporting notation drawings found")
    # sort mat answers
    qs = re.findall(r'<div class="q" data-q="(\d+)" data-ans="(\w+)">(.*?)<span class="opt">', html, re.S)
    if len(qs) != len(SORT_ITEMS):
        errs.append(f"sort mat has {len(qs)} questions")
    for q, ans, body in qs:
        has_notes = 'class="rh"' in body
        has_dots = 'class="dots"' in body
        if has_notes and ans != "RHYTHM" or has_dots and ans != "BEAT":
            errs.append(f"sort question {q}: answer {ans} does not match its drawing")
        if has_dots:
            cs, _ = parse_dots(re.search(r'<svg class="dots".*?</svg>', body, re.S).group(0))
            gaps = [cs[i + 1][0] - cs[i][0] for i in range(len(cs) - 1)]
            if len(cs) != 4 or max(gaps) - min(gaps) > 0.01:
                errs.append(f"sort question {q}: dots not four and even")
        if not has_notes and not has_dots:
            t = re.sub(r"<[^>]+>", "", body).lower()
            beat_words = ("pulse" in t or "steady" in t or "heartbeat" in t)
            rhy_words = ("long and short" in t or "ta " in t)
            if ans == "BEAT" and not beat_words or ans == "RHYTHM" and not rhy_words:
                errs.append(f"sort question {q}: the clue text does not fit the answer {ans}")
    ans_line = re.search(r"Teacher answers: ([^<]+)\.", html)
    want = ", ".join(f"{k} {a.lower()}" for k, (_, _, a) in enumerate(SORT_ITEMS, 1))
    if not ans_line or ans_line.group(1) != want:
        errs.append("sort mat answer line does not match the questions")
    # vocabulary samples: ta, ti-ti, rest
    for lab, want_pat in (("vocab-Q", "Q"), ("vocab-E", "E"), ("vocab-R", "R"), ("guide-Q", "Q"), ("guide-E", "E"), ("guide-R", "R")):
        m = re.search(r'<svg class="rh"[^>]*data-label="%s".*?</svg>' % lab, html, re.S)
        if not m or parse_rh(m.group(0))[0] != want_pat:
            errs.append(f"{lab}: symbol sample missing or not {want_pat}")
    # pictogram set: twelve different, each used on exactly two cards
    from collections import Counter
    use = Counter(re.findall(r'<div class="card" data-card="\d+" data-kind="\w+" data-move="(\w+)"', html))
    if sorted(use) != sorted(movenames) or any(v != 2 for v in use.values()):
        errs.append("each of the 12 movements must appear on exactly two cards")
    return errs


LAYOUT_JS = r"""
const { chromium } = require('playwright');
const url = require('url');
(async () => {
  const b = await chromium.launch();
  const out = [];
  for (const f of process.argv.slice(2)) {
    const p = await b.newPage({ viewport: { width: 1000, height: 1056 }, deviceScaleFactor: 1 });
    await p.goto(url.pathToFileURL(f).href, { waitUntil: 'load' });
    await p.evaluate(() => document.fonts.ready);
    const r = await p.evaluate(() => {
      const res = [];
      const BOX = '.card, .strip, .egrid, .cgrid, .part, .vc, .ic, .q, .top, .nd, .doc table, .doc p, .doc ul, .box, .vgrid, .mat';
      document.querySelectorAll('.page').forEach((pg, i) => {
        const pr = pg.getBoundingClientRect();
        const ft = pg.querySelector('.foot');
        if (pg.scrollHeight > pg.clientHeight + 1) res.push(`page ${i + 1}: content overflows the page`);
        if (!ft) return;
        const ftop = ft.getBoundingClientRect().top;
        const skip = el => ft.contains(el) || el.closest('.wm');
        pg.querySelectorAll(BOX + ', svg, img').forEach(el => {
          if (skip(el)) return;
          const r = el.getBoundingClientRect();
          if (r.height === 0) return;
          if (r.bottom > ftop - 8) res.push(`page ${i + 1}: ${el.tagName}.${el.getAttribute('class')} bottom ${(r.bottom - ftop).toFixed(1)}px vs footer rule (needs <= -8)`);
          if (r.right > pr.right - 0.35 * 96 + 0.5 || r.left < pr.left + 0.35 * 96 - 0.5) res.push(`page ${i + 1}: ${el.tagName}.${el.getAttribute('class')} too close to the page edge`);
        });
        pg.querySelectorAll('*').forEach(el => {
          if (skip(el) || el.children.length || !(el.textContent || '').trim() || el.closest('svg')) return;
          const r = el.getBoundingClientRect();
          if (r.height && r.bottom > ftop - 8) res.push(`page ${i + 1}: text "${el.textContent.trim().slice(0, 30)}" ends ${(r.bottom - ftop).toFixed(1)}px from the footer rule`);
        });
        // drawings stay inside their cards / strips / boxes with padding
        pg.querySelectorAll('.card, .strip, .part, .vc, .q, .ic').forEach(bx => {
          if (bx.scrollWidth > bx.clientWidth + 1 || bx.scrollHeight > bx.clientHeight + 1) res.push(`page ${i + 1}: content overflows a ${bx.className} box`);
          const br = bx.getBoundingClientRect();
          bx.querySelectorAll('svg').forEach(sv => {
            const s = sv.getBoundingClientRect();
            if (s.left < br.left + 3 || s.right > br.right - 3 || s.top < br.top + 3 || s.bottom > br.bottom - 3) res.push(`page ${i + 1}: a drawing is too close to its ${bx.className} box edge`);
          });
          bx.querySelectorAll('.cd, .ct, .qt, .vm, .vw, .it').forEach(t => {
            const s = t.getBoundingClientRect();
            if (s.left < br.left + 3 || s.right > br.right - 3 || s.top < br.top + 2 || s.bottom > br.bottom - 2) res.push(`page ${i + 1}: text too close to its ${bx.className} box edge`);
          });
        });
        // text next to a pictogram must not overlap it
        pg.querySelectorAll('.cmid').forEach(m => {
          const a = m.querySelector('.cpic').getBoundingClientRect(), t = m.querySelector('.ctext').getBoundingClientRect();
          if (a.right + 6 > t.left) res.push(`page ${i + 1}: pictogram and text too close`);
        });
        pg.querySelectorAll('.top .t').forEach(t => { if (t.getBoundingClientRect().right > pg.querySelector('.top .tag').getBoundingClientRect().left - 8) res.push(`page ${i + 1}: title crowds the tag`); });
        let maxb = 0;
        pg.querySelectorAll('*').forEach(el => { if (skip(el)) return; const r = el.getBoundingClientRect(); if (r.height > 0 && r.width > 0 && ((el.children.length === 0 && ((el.textContent || '').trim() || el.matches('svg, img'))) || el.matches('.part, .box, table, .card, .strip, .vc, .ic, .mat'))) maxb = Math.max(maxb, r.bottom); });
        if (i > 0 && ftop - maxb > 105) res.push(`page ${i + 1}: blank band of ${(ftop - maxb).toFixed(0)}px above the footer (over 10% of the page)`);
        const kids = [...pg.querySelectorAll(':scope > *, :scope > .stack > *')].filter(e => !skip(e) && e.getBoundingClientRect().height > 0 && !e.classList.contains('stack')).map(e => e.getBoundingClientRect()).sort((a, b) => a.top - b.top);
        for (let k = 0; k < kids.length - 1; k++) if (kids[k + 1].top - kids[k].bottom > 105) res.push(`page ${i + 1}: blank band of ${(kids[k + 1].top - kids[k].bottom).toFixed(0)}px between blocks`);
        // blank band inside the table / boxes: gaps between sibling blocks in a flex column
        pg.querySelectorAll('.stack').forEach(st => {
          const k2 = [...st.children].filter(e => e.getBoundingClientRect().height > 0).map(e => e.getBoundingClientRect());
          for (let k = 0; k < k2.length - 1; k++) if (k2[k + 1].top - k2[k].bottom > 105) res.push(`page ${i + 1}: blank band of ${(k2[k + 1].top - k2[k].bottom).toFixed(0)}px inside the page body`);
        });
      });
      document.querySelectorAll('.sq').forEach((sq, i) => {
        const sr = sq.getBoundingClientRect();
        const btop = sq.querySelector('.band').getBoundingClientRect().top;
        const shots = [];
        sq.querySelectorAll('.shot').forEach(sh => {
          const r = sh.getBoundingClientRect(); shots.push(r);
          if (r.left < sr.left + 24 || r.right + 8 > sr.right - 24) res.push(`square ${i + 1}: a page shot is too close to the side edge`);
          if (r.bottom + 8 > btop - 8) res.push(`square ${i + 1}: a page shot shadow is within 8px of the band`);
        });
        for (let a = 0; a < shots.length; a++) for (let c = a + 1; c < shots.length; c++) if (shots[a].right + 16 > shots[c].left && shots[a].left < shots[c].left && shots[a].bottom > shots[c].top) res.push(`square ${i + 1}: page shots lack a gutter`);
        sq.querySelectorAll('.lbl, .lbl span, .pill, .sub, .hd').forEach(el => {
          const r = el.getBoundingClientRect();
          if (r.bottom > btop - 8) res.push(`square ${i + 1}: text "${el.textContent.trim().slice(0, 24)}" within 8px of the band`);
          if (r.left < sr.left + 24 || r.right > sr.right - 24) res.push(`square ${i + 1}: text "${el.textContent.trim().slice(0, 24)}" too close to the side edge`);
        });
        sq.querySelectorAll('.shot img').forEach(im => { if (!im.complete || im.naturalWidth === 0) res.push(`square ${i + 1}: an image did not load`); });
      });
      document.querySelectorAll('.cover').forEach(pg => {
        const pr = pg.getBoundingClientRect();
        pg.querySelectorAll('.ctitle .b, .cband, .ctitle .c, img').forEach(el => {
          const r = el.getBoundingClientRect();
          if (r.left < pr.left + 0.45 * 96 || r.right > pr.right - 0.45 * 96) res.push(`cover: ${el.className || el.tagName} too close to the side edge`);
        });
        const kids = [...pg.children].map(c => c.getBoundingClientRect());
        for (let a = 0; a < kids.length - 1; a++) if (kids[a].bottom + 8 > kids[a + 1].top) res.push('cover: blocks lack a gutter');
      });
      return res;
    });
    out.push(...r.map(x => f.split('/').pop() + ': ' + x));
    await p.close();
  }
  await b.close();
  console.log(JSON.stringify(out));
})().catch(e => { console.error(e); process.exit(1); });
"""

PIX_JS = r"""
const { chromium } = require('playwright');
const url = require('url');
(async () => {
  // every pictogram and every notation drawing alone on a transparent ground at 4x: the page lists one svg per entry
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 700, height: 500 }, deviceScaleFactor: 4 });
  await p.goto(url.pathToFileURL(process.argv[2]).href, { waitUntil: 'load' });
  await p.evaluate(() => document.fonts.ready);
  const hs = await p.$$('svg');
  let n = 0;
  for (const h of hs) await h.screenshot({ path: process.argv[3] + '/s' + String(n++).padStart(3, '0') + '.png', omitBackground: true });
  await b.close();
  console.log(n);
})().catch(e => { console.error(e); process.exit(1); });
"""


def verify_layout():
    js = os.path.join(BUILD, "layout.js")
    with open(js, "w") as fh:
        fh.write(LAYOUT_JS)
    files = [os.path.join(BUILD, x) for x in ("resource.html", "preview.html", "cover.html", "p1.html", "p2.html", "p3.html")]
    if not all(os.path.exists(x) for x in files):
        return ["build html missing: run gen.py first"]
    r = subprocess.run(["node", js, *files], capture_output=True, text=True, env=node_env())
    if r.returncode != 0:
        return [f"layout script failed: {r.stderr[-300:]}"]
    errs = json.loads(r.stdout.strip().splitlines()[-1])
    # rendered pixels: every drawing alone on a transparent ground; ink must keep padding (at least the stroke width) inside its svg box
    from PIL import Image
    html = open(os.path.join(BUILD, "resource.html")).read()
    seen, items = set(), []
    for m in SVG_ANY.finditer(html):
        s = m.group(0)
        key = re.sub(r'data-label="[^"]*"', "", s)
        if key in seen:
            continue
        seen.add(key)
        items.append(s)
    page = (f'<!doctype html><html><head><meta charset="utf-8"><style>{font_css()}html,body{{margin:0;background:transparent}}svg{{display:block;margin:20px}}svg.pic{{width:100px;height:100px}}</style></head>'
            f'<body>{"".join(items)}</body></html>')
    write("pix.html", page)
    shots = os.path.join(BUILD, "pixshots")
    os.makedirs(shots, exist_ok=True)
    for x in os.listdir(shots):
        os.remove(os.path.join(shots, x))
    jsp = os.path.join(BUILD, "pix.js")
    with open(jsp, "w") as fh:
        fh.write(PIX_JS)
    r = subprocess.run(["node", jsp, os.path.join(BUILD, "pix.html"), shots], capture_output=True, text=True, env=node_env())
    if r.returncode != 0:
        return errs + [f"pixel script failed: {r.stderr[-300:]}"]
    names = sorted(os.listdir(shots))
    if len(names) != len(items):
        errs.append(f"pixel check rendered {len(names)} drawings, expected {len(items)}")
    for nm, s in zip(names, items):
        im = Image.open(os.path.join(shots, nm)).convert("RGBA")
        bb = im.getchannel("A").point(lambda v: 255 if v > 8 else 0).getbbox()
        w, h = im.size
        kind = re.match(r'<svg class="(\w+)"', s).group(1)
        lab = (re.search(r'data-pic="(\w+)"', s) or re.search(r'data-label="([^"]*)"', s) or re.search(r'class="(\w+)"', s)).group(1)
        if bb is None:
            errs.append(f"rendered pixels: {kind} {lab} is blank")
            continue
        edge = min(bb[0], bb[1], w - bb[2], h - bb[3])
        if kind == "pic":
            need = PC.SW * (w / 100.0)       # padding at least the stroke width, in rendered pixels
        else:
            need = 4 * 2                       # 2 CSS px at 4x for notation and dots (hairline strokes)
        if edge < need:
            errs.append(f"rendered pixels: {kind} {lab} ink comes within {edge}px of its box edge (needs {need:.0f}px)")
    return errs


def verify_images():
    errs = []
    from PIL import Image
    h = Image.open(HERO)
    a = h.getchannel("A").point(lambda v: 255 if v > 24 else 0)
    bb = a.getbbox()
    if bb is None or bb[0] < 10 or bb[1] < 10 or h.width - bb[2] < 10 or h.height - bb[3] < 10:
        errs.append(f"hero.png touches its image edge: {bb}")
    if h.size != (1400, 1400):
        errs.append("hero.png is not the pre-made 1400x1400 file")
    for p in [COVER_PNG, *PREVIEW_PNGS]:
        name = os.path.basename(p)
        im = Image.open(p).convert("L")
        if im.size != (2000, 2000):
            errs.append(f"{name}: not 2000x2000")
            continue
        px = im.load()
        rows = [sum(1 for x in range(0, 2000, 8) if px[x, y] < 200) for y in range(0, 2000, 2)]
        ytop = 2000
        for y in range(1999, 0, -1):
            if px[2, y] < 60 and px[1997, y] < 60:
                ytop = y
            else:
                break
        for edge, pts in (("top", [(x, y) for x in range(0, 2000, 2) for y in range(0, 14)]),
                          ("left", [(x, y) for x in range(0, 14) for y in range(0, ytop - 4, 2)]),
                          ("right", [(x, y) for x in range(1986, 2000) for y in range(0, ytop - 4, 2)])):
            if any(px[x, y] < 235 for x, y in pts):
                errs.append(f"{name}: art or ink touches the {edge} edge")
        if ytop > 1990 or ytop < 1700:
            errs.append(f"{name}: bottom band not found (starts at {ytop})")
        run = best = 0
        for y in range(120, ytop, 2):
            if rows[y // 2] == 0:
                run += 2
                best = max(best, run)
            else:
                run = 0
        if best > 200:
            errs.append(f"{name}: blank band of {best}px")
        last = max((y for y in range(0, ytop, 2) if rows[y // 2] > 0), default=0)
        if ytop - last > 200:
            errs.append(f"{name}: {ytop - last}px blank above the bottom band")
        cols = [x for x in range(0, 2000, 2) if any(px[x, y] < 200 for y in range(120, ytop - 4, 4))]
        if cols and (min(cols) < 40 or max(cols) > 1960):
            errs.append(f"{name}: content within 40px of the left or right edge")
    names = set(PAGE_NAMES.values())
    for hn in ("p1.html", "p2.html", "p3.html"):
        t = open(os.path.join(BUILD, hn)).read()
        for cap in re.findall(r'<div class="lbl"[^>]*>([^<]+)(?:<span>[^<]*</span>)?</div>', t):
            if cap not in names:
                errs.append(f"{hn}: label '{cap}' is not a page name")
        if t.count('class="swm"') != 1:
            errs.append(f"{hn}: expected exactly one PREVIEW watermark")
    return errs


def pdf_fonts(path):
    out = subprocess.run(["pdffonts", path], capture_output=True, text=True, check=True).stdout.splitlines()[2:]
    return [(p.split()[0], p.split()[-5]) for p in out]


def verify_files():
    errs = []
    from pypdf import PdfReader
    for p in [PDF, PREVIEW_PDF, COVER_PNG, *PREVIEW_PNGS, UPLOAD, TPT_JSON, HERO, os.path.join(TPT, "STYLE.md"), RENDER_JS]:
        if not os.path.exists(p):
            errs.append(f"missing {os.path.relpath(p, TPT)}")
    if errs:
        return errs
    for path, want in ((PDF, TOTAL_PAGES), (PREVIEW_PDF, 4)):
        rd = PdfReader(path)
        if len(rd.pages) != want:
            errs.append(f"{os.path.basename(path)}: {len(rd.pages)} pages, expected {want}")
        for i, pg in enumerate(rd.pages):
            if abs(float(pg.mediabox.width) - 612) > 1 or abs(float(pg.mediabox.height) - 792) > 1:
                errs.append(f"{os.path.basename(path)} p{i + 1}: not US Letter")
        fonts = pdf_fonts(path)
        for name, emb in fonts:
            if emb != "yes":
                errs.append(f"{os.path.basename(path)}: font {name} not embedded")
        names = " ".join(n for n, _ in fonts).lower().replace(" ", "")
        for fam in ("bravura", "oswald", "sourcesans3"):
            if fam not in names:
                errs.append(f"{os.path.basename(path)}: {fam} not found in PDF fonts")
    rd = PdfReader(PDF)
    texts = [" ".join((pg.extract_text() or "").split()) for pg in rd.pages]
    for i, t in enumerate(texts):
        if len(t) < 40:
            errs.append(f"PDF page {i + 1} looks blank")
        if "PREVIEW" in t.upper():
            errs.append(f"product PDF page {i + 1} carries a PREVIEW watermark")
        if i + 1 != 1 and f"Page {i + 1}" not in t:
            errs.append(f"PDF page {i + 1} does not print its own page number")
    for pg, name in PAGE_NAMES.items():
        if pg != P_COVER and name.lower() not in texts[pg - 1].lower():
            errs.append(f"page {pg} does not show its name '{name}'")
    full_pages()
    for frm, to, text in XREFS:
        if text not in texts[frm - 1]:
            errs.append(f"page {frm}: cross-reference text '{text}' not found")
        m = re.search(r"page (\d+)", text)
        if m and int(m.group(1)) != to:
            errs.append(f"cross-reference '{text}' on page {frm} should point to {to}")
    # card and strip numbers printed on their pages
    for n in range(1, 25):
        if not re.search(rf"Card {n}(?!\d)", texts[card_page(n) - 1]):
            errs.append(f"card {n} is not printed on page {card_page(n)}")
    for n in range(1, 13):
        if not re.search(rf"ECHO {n}(?!\d)", texts[strip_page(n) - 1]):
            errs.append(f"echo strip {n} not printed on page {strip_page(n)}")
    for i, t in enumerate(texts):
        for m in re.finditer(r"(?i)\bpages? (\d+)(?:–(\d+))?", t):
            a, b = int(m.group(1)), int(m.group(2) or m.group(1))
            if a < 1 or b > TOTAL_PAGES or b < a:
                errs.append(f"page {i + 1}: reference '{m.group(0)}' is outside the {TOTAL_PAGES}-page file")
    # "cards a–b" claims on the teacher pages agree with where the cards really are
    t1, t2 = texts[P_T1 - 1], texts[P_T2 - 1]
    for need in (f"Pages {P_BEAT1}–{P_BEAT2}: 12 steady beat cards (cards 1–12)", f"Pages {P_RHY1}–{P_RHY2}: 12 rhythm cards (cards 13–24)", f"Pages {P_ECHO1}–{P_ECHO2}: 12 rhythm echo strips",
                 f"({TOTAL_PAGES} pages)", f"Page {P_SORT}: sort mat", f"Page {P_CHECK}: assessment checklist", f"Page {P_ICAN}: I can sheet", f"Page {P_VOCAB}: vocabulary", f"Page {P_TERMS}: terms of use"):
        if need.lower() not in t1.lower():
            errs.append(f"teacher notes lack '{need}'")
    assert card_page(1) == P_BEAT1 and card_page(12) == P_BEAT2 and card_page(13) == P_RHY1 and card_page(24) == P_RHY2
    for need in ("steady beat cards 1–6", "cards 7–12", "rhythm cards 13–18", "echo strips 1–6", "rhythm cards 19–24", "echo strips 7–12"):
        if need.lower() not in t2.lower():
            errs.append(f"pacing table lacks '{need}'")
    lessons = re.findall(r"Lesson (\d) \(", t2)
    if lessons != ["1", "2", "3", "4"]:
        errs.append(f"pacing should list 4 lessons, found {lessons}")
    for need in ("sorting game", "echo game", "freeze game"):
        if need not in t2.lower().replace("beat vs rhythm ", ""):
            errs.append(f"teacher notes lack the {need}")
    for need in ("heartbeat", "steady pulse", "long and short sounds"):
        if need not in t1.lower():
            errs.append(f"teacher notes lack '{need}'")
    pt = " ".join(texts[p - 1] for p in range(1, TOTAL_PAGES + 1))
    if "does not cite standards" not in t2:
        errs.append("teacher notes should say the resource does not cite standards")
    for bad in ("National Core", "NCAS", "CCSS", "standard MU"):
        if bad in pt:
            errs.append(f"standards wording '{bad}' in the product")
    terms = texts[P_TERMS - 1]
    for need in (f"Page 1 cover, pages {P_T1}–{P_T2}", f"page {P_GUIDE} reading guide", f"pages {P_BEAT1}–{P_BEAT2} steady beat cards", f"pages {P_RHY1}–{P_RHY2} rhythm cards", f"pages {P_ECHO1}–{P_ECHO2} echo strips",
                 f"page {P_SORT} sort mat", f"page {P_CHECK} checklist", f"page {P_ICAN} I can sheet", f"page {P_VOCAB} vocabulary", f"({TOTAL_PAGES} pages)"):
        if need.lower() not in terms.lower():
            errs.append(f"terms page 'what is in this file' lacks '{need}'")
    if DISCLOSURE not in terms:
        errs.append("terms page lacks the disclosure line")
    prd = PdfReader(PREVIEW_PDF)
    for i in range(4):
        t = prd.pages[i].extract_text() or ""
        if t.count("PREVIEW") != 1:
            errs.append(f"preview PDF page {i + 1}: expected exactly one PREVIEW watermark")
        if PAGE_NAMES[PREVIEW_PAGES[i]].lower() not in t.lower():
            errs.append(f"preview PDF page {i + 1} is not '{PAGE_NAMES[PREVIEW_PAGES[i]]}'")
    errs += verify_images()
    up = open(UPLOAD).read()
    m = re.search(r"^## 1\. Title\s*\n+```\n(.+?)\n```", up, re.M | re.S)
    if not m:
        errs.append("UPLOAD.md: title block not found")
    else:
        title = m.group(1).strip()
        if len(title) > 80 or title != LISTING_TITLE:
            errs.append("UPLOAD.md: title is over 80 chars or differs from the generator")
        if re.search(r"winter|snow|holiday|christmas|december|halloween|thanksgiving|season", title, re.I):
            errs.append("UPLOAD.md: seasonal word in the title")
    if re.search(r"winter|snow|holiday", TITLE + " " + texts[0], re.I):
        errs.append("cover or title carries a seasonal word")
    for need in (DISCLOSURE, f"${PRICE}", f"{TOTAL_PAGES} pages", "Grades K-2", "Kindergarten, 1st and 2nd", "cards 1-12", "cards 13-24", "12 rhythm echo strips"):
        if need not in up:
            errs.append(f"UPLOAD.md: missing '{need}'")
    sec = up.split("## 5. Page count by section")[1].split("##")[0]
    nums = [int(x) for x in re.findall(r"^- (?!Total)[^\n]*: (\d+)$", sec, re.M)]
    if sum(nums) != TOTAL_PAGES:
        errs.append(f"UPLOAD.md page list sums to {sum(nums)}, PDF has {TOTAL_PAGES}")
    desc = up.split("## 2. Description")[1].split("## 3.")[0]
    dn = [int(x) for x in re.findall(r"^• [^\n]*\((\d+) pages?\)", desc, re.M)]
    if sum(dn) != TOTAL_PAGES:
        errs.append(f"UPLOAD.md description page list sums to {sum(dn)}, PDF has {TOTAL_PAGES}")
    low = up.lower()
    for bad in ("checked by hand", "handmade", "recomputed", "classroom-tested", "classroom tested", "hand-checked"):
        if bad in low:
            errs.append(f"UPLOAD.md says '{bad}'")
    tj = json.load(open(TPT_JSON))
    topts = json.load(open(os.path.join(TPT, "TAG-OPTIONS.json")))["options"]
    headings = {"Audience", "Language", "Programs & Methods", "Resource Type", "Instruction", "Student Assessment", "Student Practice", "Teacher Tools", "Supports", "Specialty", "Speech Therapy",
                "Theme", "Holiday", "Seasonal"}
    subs = json.load(open(os.path.join(TPT, "SUBJECT-OPTIONS.json")))
    sub_headings = {"Arts", "Art", "English Language Arts", "Math", "Performing Arts", "Science", "Social Studies", "World Languages", "Social Emotional", "For All Subjects"}
    if any(t not in topts or t in headings or t == "Student Practice" for t in tj["tags"]) or any(s not in subs or s in sub_headings for s in tj["subjects"]):
        errs.append("tpt.json tags or subjects invalid, or a heading")
    if not 1 <= len(tj["tags"]) <= 6 or not 1 <= len(tj["subjects"]) <= 3:
        errs.append("tpt.json tag or subject count out of range")
    if tj.get("pages") != TOTAL_PAGES or tj["price"] != PRICE or not 1 <= len(tj["grades"]) <= 4:
        errs.append("tpt.json pages, price or grades mismatch")
    first = texts[0].lower()
    if f"{TOTAL_PAGES} pages" not in first or "24 cards" not in first or "grades k–2" not in first:
        errs.append("cover text does not state the page count, cards and grades")
    allt = pt.lower()
    for bad in ("colour", "favourite", "metre", "crotchet", "quaver", "minim", "semibreve", "analyse", "recomputed", "checker", "grey"):
        if bad in allt:
            errs.append(f"unwanted wording '{bad}'")
    for bad in ("christmas", "santa", "holiday", "hanukkah", "kwanzaa", "easter", "church", "pray"):
        if bad in allt:
            errs.append(f"holiday or religious word '{bad}' in the product")
    return errs


def check():
    errs = verify_html()
    errs += verify_layout()
    errs += verify_files()
    if errs:
        print("CHECK FAILED")
        print("\n".join(" - " + e for e in errs[:80]))
        if len(errs) > 80:
            print(f" ... and {len(errs) - 80} more")
        sys.exit(1)
    print(f"CHECK OK: 24 cards (12 steady beat with four evenly spaced dots, 12 rhythm) and 12 echo strips re-read from the rendered SVG; every bar adds up to 4 beats; stems sit on the left edge going down from "
          f"noteheads on the middle line; beams join exactly two eighths flush with the stem ends; rests, clef and 4/4 placed correctly; syllable lines and spoken words match the notation; all 24 rhythms differ; "
          f"pictograms and notation keep padding on rendered pixels; layout and footer gaps clear; PDF {TOTAL_PAGES} Letter pages, preview 4 (one watermark each); images 2000x2000 with clean edges; "
          f"page numbers, cross-references, UPLOAD.md and tpt.json agree.")


if __name__ == "__main__" and "--check" in sys.argv:
    check()
