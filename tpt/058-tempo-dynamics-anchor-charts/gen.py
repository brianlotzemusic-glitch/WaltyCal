#!/usr/bin/env python3
"""Tempo and Dynamics Anchor Charts (TpT 058): build the resource and verify it.

    python3 gen.py           build everything (PDFs, PNGs, UPLOAD.md, tpt.json) into this folder
    python3 gen.py --check   re-read the rendered pages and verify every term, abbreviation, meaning, ordering, quiz key,
                             count, cross-reference, drawing and the layout

--check does not trust the tables in this file. It loads the rendered HTML in Chromium and reads back what is really on the pages,
then compares it with a second, separately typed table (EXPECT_*) and recomputes every quiz answer from the meanings.
Rendering uses Playwright + Chromium (HTML/SVG -> PDF/PNG) with the OFL fonts in ../fonts (Bravura for the dynamic letters).
"""
import json
import math
import os
import random
import re
import subprocess
import sys
from html import escape

HERE = os.path.dirname(os.path.abspath(__file__))
TPT = os.path.dirname(HERE)
FONTS = os.path.join(TPT, "fonts")
BUILD = os.path.join(HERE, "build")
ART = os.path.join(HERE, "art")
RENDER_JS = os.path.join(TPT, "tools", "render.js")

SLUG = "tempo-dynamics-anchor-charts"
PDF = os.path.join(HERE, f"{SLUG}.pdf")
PREVIEW_PDF = os.path.join(HERE, f"{SLUG}-PREVIEW.pdf")
COVER_PNG = os.path.join(HERE, "cover.png")
PREVIEW_PNGS = [os.path.join(HERE, f"preview-{i}.png") for i in (1, 2, 3)]
UPLOAD = os.path.join(HERE, "UPLOAD.md")
TPT_JSON = os.path.join(HERE, "tpt.json")

STORE = "Brian Lotze"
BRAND = "Hudson Beat"
YEAR = 2026
ACCENT = "#2F7FBF"
TINT = "#DCEBF7"
DISCLOSURE = "Created with the help of digital and AI tools. Notation and answer keys are verified before release."
TITLE = "Dynamics & Tempo"
LISTING_TITLE = "Music Dynamics & Tempo Posters | Anchor Charts, Reference Sheet, Quiz Gr 2-8"
PRICE = "4.00"
TAGS = ["Posters", "Word Walls", "Bulletin Board Ideas", "Printables", "Handouts", "Assessment"]
SUBJECTS = ["Music", "Instrumental Music", "Vocal Music"]
GRADES = ["3rd-grade", "4th-grade", "5th-grade", "6th-grade"]

# ------------------------------------------------------------------ content tables
# glyph = SMuFL code point in Bravura. rank = place in the order softest -> loudest, or slowest -> fastest.
DYN = [
    dict(key="pp", term="pianissimo", abbr="pp", meaning="very soft", glyph=0xE52B, rank=1),
    dict(key="p", term="piano", abbr="p", meaning="soft", glyph=0xE520, rank=2),
    dict(key="mp", term="mezzo piano", abbr="mp", meaning="medium soft", glyph=0xE52C, rank=3),
    dict(key="mf", term="mezzo forte", abbr="mf", meaning="medium loud", glyph=0xE52D, rank=4),
    dict(key="f", term="forte", abbr="f", meaning="loud", glyph=0xE522, rank=5),
    dict(key="ff", term="fortissimo", abbr="ff", meaning="very loud", glyph=0xE52F, rank=6),
]
CHANGE = [
    dict(key="cresc", term="crescendo", abbr="cresc.", meaning="gradually louder", sym="hairpin-open"),
    dict(key="decresc", term="decrescendo", abbr="decresc.", meaning="gradually softer", sym="hairpin-close"),
    dict(key="dim", term="diminuendo", abbr="dim.", meaning="gradually softer", sym="hairpin-close"),
]
TEMPO = [
    dict(key="largo", term="largo", abbr="", meaning="very slow", bpm="40–60", rank=1, gauge=0.08),
    dict(key="adagio", term="adagio", abbr="", meaning="slow", bpm="66–76", rank=2, gauge=0.25),
    dict(key="andante", term="andante", abbr="", meaning="walking pace", bpm="76–108", rank=3, gauge=0.45),
    dict(key="moderato", term="moderato", abbr="", meaning="moderate speed", bpm="108–120", rank=4, gauge=0.6),
    dict(key="allegro", term="allegro", abbr="", meaning="fast", bpm="120–156", rank=5, gauge=0.78),
    dict(key="presto", term="presto", abbr="", meaning="very fast", bpm="168–200", rank=6, gauge=0.95),
]
TCHANGE = [
    dict(key="accel", term="accelerando", abbr="accel.", meaning="gradually faster", bpm="", sym="dots-fast"),
    dict(key="rit", term="ritardando", abbr="rit.", meaning="gradually slower", bpm="", sym="dots-slow"),
]
D = {x["key"]: x for x in DYN + CHANGE + TEMPO + TCHANGE}
DYN_ORDER = [x["key"] for x in sorted(DYN, key=lambda x: x["rank"])]
TEMPO_ORDER = [x["key"] for x in sorted(TEMPO, key=lambda x: x["rank"])]

TIPS = {
    "pp": ("Pianissimo means very soft. Sing or play so quietly that the room feels hushed.", "Think: a whisper"),
    "p": ("Piano means soft. Keep your sound gentle and calm.", "Think: a quiet voice in a library"),
    "mp": ("Mezzo piano means medium soft. It is a little louder than piano.", "Think: a soft talking voice"),
    "mf": ("Mezzo forte means medium loud. It is a little softer than forte.", "Think: a normal speaking voice"),
    "f": ("Forte means loud. Sing or play with a strong, full sound.", "Think: a big, strong voice, never a shout"),
    "ff": ("Fortissimo means very loud. It is the loudest of the six common dynamics.", "Loud and full, with a beautiful tone"),
}
# posters: each is a list of keys on that page
POSTERS = [["pp"], ["p"], ["mp"], ["mf"], ["f"], ["ff"], ["cresc"], ["decresc", "dim"],
           ["largo", "adagio"], ["andante", "moderato"], ["allegro", "presto"], ["accel", "rit"]]
NPOST = len(POSTERS)
BPM_NOTE = "BPM means beats per minute. These are common ranges: books, teachers and conductors use slightly different numbers."

# ------------------------------------------------------------------ the quiz
# Each multiple-choice question: ask = ("term", key) -> options are meanings; ("meaning", key) -> options are terms/abbreviations
# ("hairpin", key) -> options are meanings. Exactly one option must be true; the letter is computed, never typed.
MC = [
    dict(n=3, text="What does mf mean?", ask=("term", "mf"), opts=["medium soft", "medium loud", "loud", "very loud"], order=[0, 1, 2, 3]),
    dict(n=4, text="Which symbol means very soft?", ask=("meaning", "very soft"), opts=["mf", "ff", "p", "pp"], order=[0, 1, 2, 3]),
    dict(n=5, text="Look at this symbol. What should the musicians do?", ask=("hairpin", "cresc"),
         opts=["gradually louder", "gradually softer", "gradually faster", "gradually slower"], order=[0, 1, 2, 3]),
    dict(n=6, text="Which word means to get gradually slower?", ask=("meaning", "gradually slower"),
         opts=["accelerando", "ritardando", "allegro", "crescendo"], order=[0, 1, 2, 3]),
    dict(n=9, text="Which tempo marking means a walking pace?", ask=("meaning", "walking pace"),
         opts=["presto", "largo", "allegro", "andante"], order=[0, 1, 2, 3]),
    dict(n=10, text="A composer wants the music to get gradually softer. Which word could they write?", ask=("meaning", "gradually softer"),
         opts=["crescendo", "forte", "diminuendo", "accelerando"], order=[0, 1, 2, 3]),
]
MATCH_DYN = dict(n=1, items=["f", "pp", "mp", "ff", "p", "mf"], meanings=["very loud", "soft", "medium loud", "very soft", "loud", "medium soft"])
MATCH_TEMPO = dict(n=2, items=["allegro", "largo", "presto", "andante", "adagio", "moderato"],
                   meanings=["walking pace", "very slow", "fast", "moderate speed", "very fast", "slow"])
ORDER_DYN = dict(n=7, items=["mf", "pp", "ff", "p", "f", "mp"])
ORDER_TEMPO = dict(n=8, items=["presto", "adagio", "allegro", "largo", "moderato", "andante"])
NQ = 10
LET = "ABCDEF"


def meaning_of(key):
    return D[key]["meaning"]


def abbr_or_term(x):
    return D[x]["abbr"] if x in D and D[x].get("abbr") and x in [d["key"] for d in DYN] else x


def mc_truth(q):
    """Return the list of option letters that are true for this question, computed from the tables."""
    kind, val = q["ask"]
    good = []
    for i, o in enumerate(q["opts"]):
        if kind in ("term", "hairpin"):
            ok = (meaning_of(val) == o)
        else:
            ok = (any(x["meaning"] == val and o in (x["term"], x["abbr"]) for x in D.values()))
        if ok:
            good.append("ABCD"[i])
    return good


def match_key(m, kind):
    letter_of = {mm: LET[i] for i, mm in enumerate(m["meanings"])}
    return {it: letter_of[meaning_of(it)] for it in m["items"]}


QUIZ_POINTS = len(MATCH_DYN["items"]) + len(MATCH_TEMPO["items"]) + len(MC) + 2   # 1 point per matching item, MC, and each ordering question

# ------------------------------------------------------------------ page map
P_COVER, P_TEACH, P_POST0 = 1, 2, 3
P_REF = P_POST0 + NPOST          # 15
P_Q1, P_Q2 = P_REF + 1, P_REF + 2
P_KEY = P_Q2 + 1
P_TERMS = P_KEY + 1
TOTAL_PAGES = P_TERMS
PAGEOF = {"cover": P_COVER, "teacher": P_TEACH, "ref": P_REF, "quiz1": P_Q1, "quiz2": P_Q2, "key": P_KEY, "terms": P_TERMS}
PAGE_NAMES = {"cover": "Cover", "teacher": "Teacher Notes", "ref": "Student Reference Sheet", "quiz1": "Quiz, Page 1 of 2",
              "quiz2": "Quiz, Page 2 of 2", "key": "Quiz Answer Key", "terms": "Terms of Use"}
for _i in range(NPOST):
    PAGEOF[f"poster{_i + 1}"] = P_POST0 + _i
    PAGE_NAMES[f"poster{_i + 1}"] = f"Poster {_i + 1} of {NPOST}"


def R(kind, cap=False):
    return f'<span data-ref="{kind}" data-n="{PAGEOF[kind]}">{"Page" if cap else "page"} {PAGEOF[kind]}</span>'


def RR(k1, k2, cap=False):
    return (f'<span data-ref="{k1}" data-n="{PAGEOF[k1]}" data-ref2="{k2}" data-n2="{PAGEOF[k2]}">'
            f'{"Pages" if cap else "pages"} {PAGEOF[k1]}–{PAGEOF[k2]}</span>')


def gl(key, cls="bv"):
    return f'<span class="{cls}" data-g="{D[key]["glyph"]:X}">{chr(D[key]["glyph"])}</span>'


# ------------------------------------------------------------------ drawings (code; stroke SW inside a 200 x 200 box, >= 2 strokes of padding)
SW = 8
STY = f'stroke="#000" stroke-width="{SW}" stroke-linecap="round" stroke-linejoin="round"'


def svg_icon(kind, body, vb="0 0 200 200", extra=""):
    return (f'<svg class="icon {extra}" viewBox="{vb}" data-sw="{SW}" data-icon="{kind}" xmlns="http://www.w3.org/2000/svg">'
            f'<g class="art" {STY}>{body}</g></svg>')


def icon_bars(level):
    body = ""
    for i in range(6):
        h = 26 + i * 18
        fill = ACCENT if i < level else "#fff"
        body += f'<rect x="{26 + i * 26}" y="{168 - h}" width="18" height="{h}" rx="4" fill="{fill}"/>'
    return svg_icon(f"bars{level}", body)


def icon_gauge(f, name):
    th = math.pi * (1 - f)
    nx, ny = 100 + 56 * math.cos(th), 128 - 56 * math.sin(th)
    body = (f'<path d="M28 128 A72 72 0 0 1 172 128 Z" fill="{TINT}"/>'
            f'<line x1="100" y1="128" x2="{nx:.1f}" y2="{ny:.1f}" stroke="{ACCENT}" stroke-width="{SW + 2}"/>'
            f'<circle cx="100" cy="128" r="10" fill="#000"/>')
    return svg_icon(f"gauge-{name}", body)


def icon_dots(fast):
    gaps = [50, 38, 30, 24] if fast else [24, 30, 38, 50]
    x, body = 29, ""
    xs = [x]
    for g in gaps:
        x += g
        xs.append(x)
    for xx in xs:
        body += f'<circle cx="{xx}" cy="86" r="5" fill="{ACCENT}"/>'
    body += '<path d="M30 140 H170 M150 122 L170 140 L150 158" fill="none"/>'
    return svg_icon("dots-fast" if fast else "dots-slow", body)


def hairpin(opening, w, h, sw, cls="hp"):
    pad = sw * 2
    cy = h / 2
    if opening:
        d = f"M{pad} {cy} L{w - pad} {pad} M{pad} {cy} L{w - pad} {h - pad}"
    else:
        d = f"M{pad} {pad} L{w - pad} {cy} M{pad} {h - pad} L{w - pad} {cy}"
    return (f'<svg class="icon {cls}" viewBox="0 0 {w} {h}" data-sw="{sw}" data-icon="hairpin-{"open" if opening else "close"}" xmlns="http://www.w3.org/2000/svg">'
            f'<g class="art" stroke="#000" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round" fill="none"><path d="{d}"/></g></svg>')


# ------------------------------------------------------------------ css
def font_css():
    f = os.path.relpath(FONTS, BUILD)
    faces = [("Oswald", 300, "normal", "oswald-latin-300-normal"), ("Oswald", 500, "normal", "oswald-latin-500-normal"),
             ("Oswald", 700, "normal", "oswald-latin-700-normal"),
             ("Source Sans 3", 400, "normal", "source-sans-3-latin-400-normal"),
             ("Source Sans 3", 400, "italic", "source-sans-3-latin-400-italic"),
             ("Source Sans 3", 600, "normal", "source-sans-3-latin-600-normal"),
             ("Source Sans 3", 700, "normal", "source-sans-3-latin-700-normal"),
             ("Bravura", 400, "normal", "bravura")]
    return "".join(f"@font-face{{font-family:'{n}';font-weight:{w};font-style:{s};src:url('{f}/{file}.woff2') format('woff2');}}"
                   for n, w, s, file in faces)


CSS = """
@page { size: 8.5in 11in; margin: 0; }
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; background: #fff; color: #000; }
body { font-family: 'Source Sans 3', sans-serif; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
.page { width: 8.5in; height: 11in; position: relative; overflow: hidden; page-break-after: always; break-after: page;
        padding: 0.42in 0.5in 0.38in; display: flex; flex-direction: column; }
.page:last-child { page-break-after: auto; break-after: auto; }
.bv { font-family: 'Bravura'; font-weight: 400; font-style: normal; line-height: 1; display: inline-block; height: 1em; width: auto; white-space: nowrap; position: relative; top: .15em; }
.h { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; letter-spacing: .01em; line-height: 1; }
.l { font-family: 'Oswald'; font-weight: 300; }
.top { display: flex; justify-content: space-between; align-items: flex-end; border-bottom: 2.2pt solid #000; padding-bottom: 6pt; }
.top .t { font-size: 25pt; }
.top .t small { display: block; font-family: 'Oswald'; font-weight: 300; text-transform: none; font-size: 12pt; letter-spacing: 0; margin-top: 4pt; }
.tag { text-align: right; flex: 0 0 auto; margin-left: 12pt; }
.tag .lv { display: inline-block; background: #000; color: #fff; font-family: 'Oswald'; font-weight: 700; font-size: 15pt; padding: 3pt 9pt 4pt; border-radius: 4pt; letter-spacing: .04em; }
.tag.key .lv { background: ACCENT; }
.tag .ln { font-family: 'Oswald'; font-weight: 300; font-size: 11pt; margin-top: 3pt; }
.name { display: flex; gap: 14pt; font-size: 12pt; margin: 9pt 0 7pt; align-items: flex-end; }
.name span { flex: 1; border-bottom: 1pt solid #000; height: 15pt; }
.name span.s { flex: 0 0 1.3in; }
.foot { display: flex; justify-content: space-between; font-size: 8.5pt; color: #333; border-top: .8pt solid #000; padding-top: 3pt; margin-top: auto; }
.wm { position: absolute; left: 50%; top: 50%; transform: translate(-50%, -50%) rotate(-38deg); font-family: 'Oswald'; font-weight: 700;
      font-size: 150pt; color: rgba(0,0,0,.13); letter-spacing: .06em; white-space: nowrap; pointer-events: none; z-index: 9; }
.fill { flex: 1; }
.doc h1 { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 30pt; margin: 0 0 4pt; line-height: 1; }
.doc h2 { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 13pt; margin: 9pt 0 3pt; letter-spacing: .02em; }
.doc p, .doc li { font-size: 10.6pt; line-height: 1.33; margin: 0 0 4pt; text-wrap: pretty; }
.doc ul, .doc ol { margin: 0 0 3pt; padding-left: 16pt; }
.doc .rule { border-bottom: 2.2pt solid #000; margin-bottom: 8pt; padding-bottom: 6pt; }
.doc .cols { display: flex; gap: 20pt; }
.doc .cols > div { flex: 1; min-width: 0; }
.small { font-size: 9.5pt !important; color: #333; }
/* posters */
.poster { align-items: center; justify-content: space-between; text-align: center; padding: 0.42in 0.6in 0.38in; }
.poster > * { flex-shrink: 0; }
.poster .foot { width: 100%; margin-top: 0; }
.poster .pk { font-family: 'Oswald'; font-weight: 500; text-transform: uppercase; letter-spacing: .26em; font-size: 12pt; }
.poster .pt { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 76pt; line-height: 1.25; width: 100%; letter-spacing: .005em; text-wrap: balance; }
.poster .pt.m { font-size: 58pt; line-height: 1.2; }
.poster .pt small { display: block; font-size: 40pt; font-weight: 500; margin-top: 0; }
.poster .pt small.ab { font-family: 'Source Sans 3'; font-style: italic; font-weight: 600; text-transform: none; font-size: 34pt; line-height: 1.1; }
.symrow { display: flex; align-items: center; justify-content: center; gap: 0.5in; width: 100%; }
.symbox { width: 3.4in; height: 2.6in; display: flex; align-items: center; justify-content: center; border: 2.2pt solid #000; border-radius: 12pt; }
.symbox .bv { font-size: 150pt; }
.symrow .icon { width: 2.4in; height: 2.4in; display: block; }
.poster .pm { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 54pt; line-height: 1.05; background: TINT; width: 100%; border-radius: 8pt; padding: 8pt 10pt 10pt; }
.poster .psub { font-size: 21pt; line-height: 1.28; width: 100%; font-weight: 600; text-wrap: balance; }
.poster .prem { width: 100%; background: #000; color: #fff; font-family: 'Oswald'; font-weight: 500; font-size: 16pt; letter-spacing: .04em;
                text-transform: uppercase; padding: 9pt 14pt 10pt; border-radius: 5pt; line-height: 1.2; }
.strip { display: flex; gap: 7pt; width: 100%; justify-content: center; align-items: stretch; }
.strip .s { flex: 1; border: 1.4pt solid #000; border-radius: 6pt; text-align: center; padding: 4pt 2pt 3pt; min-width: 0; display: flex; align-items: center; justify-content: center;
            font-family: 'Oswald'; font-weight: 500; font-size: 11pt; text-transform: uppercase; letter-spacing: .02em; }
.strip .s .bv { font-size: 24pt; }
.strip .s.on { background: ACCENT; color: #fff; border-color: #000; }
.stripcap { font-family: 'Oswald'; font-weight: 300; font-size: 12pt; width: 100%; display: flex; justify-content: space-between; margin-bottom: 3pt; }
.demo { display: flex; align-items: center; justify-content: center; gap: 0.3in; width: 100%; }
.demo .bv { font-size: 60pt; }
.demo .icon.hp { width: 3.2in; height: 0.9in; }
.demo.big .icon.hp { width: 5.2in; height: 1.8in; }
.symbox.wide { width: 100%; height: 2.3in; }
.symbox.wide .icon.hp { width: 4.9in; height: 1.66in; }
.abbr { font-family: 'Source Sans 3'; font-style: italic; font-size: 32pt; font-weight: 600; margin-left: 12pt; }
.tb { display: flex; align-items: center; gap: 0.3in; width: 100%; border: 2.2pt solid #000; border-radius: 12pt; padding: 10pt 16pt; text-align: left; }
.tb .icon { flex: 0 0 1.9in; width: 1.9in; height: 1.9in; display: block; }
.tb .tx { flex: 1; min-width: 0; }
.tb .tn { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 42pt; line-height: 1.25; }
.tb .tn .ab { font-family: 'Source Sans 3'; font-style: italic; font-weight: 600; text-transform: none; font-size: 22pt; margin-left: 8pt; }
.tb .tm { font-family: 'Oswald'; font-weight: 500; text-transform: uppercase; font-size: 26pt; letter-spacing: .03em; margin-top: 2pt; }
.tb .tb2 { display: inline-block; background: #000; color: #fff; font-family: 'Oswald'; font-weight: 500; font-size: 16pt; letter-spacing: .04em; padding: 3pt 10pt 4pt; border-radius: 5pt; margin-top: 6pt; }
.tb .tb2.n { background: ACCENT; }
.pnote { font-size: 11pt; line-height: 1.3; color: #222; width: 100%; }
/* reference sheet and quiz */
table.rt { border-collapse: collapse; width: 100%; table-layout: fixed; margin: 3pt 0 8pt; }
table.rt th, table.rt td { border: 1pt solid #000; padding: 1pt 8pt; text-align: left; vertical-align: middle; font-size: 11.5pt; }
table.rt th { font-family: 'Oswald'; font-weight: 500; text-transform: uppercase; font-size: 10.5pt; background: #000; color: #fff; letter-spacing: .04em; }
table.rt td.sy { text-align: center; }
table.rt td.sy .bv { font-size: 22pt; }
table.rt td.sy .icon.hp { width: 0.9in; height: 0.32in; display: inline-block; vertical-align: middle; }
table.rt td.tm { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 13pt; letter-spacing: .02em; }
table.rt tr { height: 0.33in; }
.ordline { display: flex; align-items: center; gap: 8pt; border: 1.3pt solid #000; border-radius: 7pt; padding: 5pt 10pt; margin: 0 0 6pt; font-size: 12pt; }
.ordline b { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 11pt; letter-spacing: .03em; flex: 0 0 auto; }
.ordline .bv { font-size: 24pt; }
.ordline .ar { font-family: 'Oswald'; font-weight: 300; font-size: 14pt; }
.q { border: 1.3pt solid #000; border-radius: 7pt; padding: 6pt 12pt 8pt; margin-bottom: 8pt; }
.q .qh { font-size: 12pt; line-height: 1.3; font-weight: 600; margin-bottom: 4pt; display: flex; gap: 8pt; align-items: center; }
.q .qh i { font-style: normal; font-family: 'Oswald'; font-weight: 700; color: ACCENT; font-size: 14pt; flex: 0 0 auto; }
.q .qh .pt1 { font-family: 'Oswald'; font-weight: 300; font-size: 10.5pt; margin-left: auto; flex: 0 0 auto; }
.q .qh .icon.hp { width: 1.1in; height: 0.4in; flex: 0 0 auto; }
.q .op { display: flex; gap: 8pt; align-items: center; font-size: 12pt; margin: 2pt 0 2pt 14pt; }
.q .op b { flex: 0 0 16pt; font-family: 'Oswald'; font-weight: 700; }
.q .op .bv { font-size: 22pt; }
.q .opgrid { display: grid; grid-template-columns: 1fr 1fr; gap: 0 12pt; }
.mt { display: grid; grid-template-columns: 1fr 1fr; gap: 6pt 24pt; font-size: 12pt; }
.mt .it { display: flex; align-items: center; gap: 6pt; min-height: 0.3in; }
.mt .it .bk { flex: 0 0 0.45in; border-bottom: 1pt solid #000; height: 18pt; }
.mt .it .bv { font-size: 24pt; }
.mt .it .wd { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 12pt; }
.mt .mn { display: flex; gap: 6pt; align-items: center; min-height: 0.3in; }
.mt .mn b { font-family: 'Oswald'; font-weight: 700; flex: 0 0 14pt; }
.mt .mn span::first-letter { text-transform: uppercase; }
.mt .col { display: flex; flex-direction: column; gap: 4pt; }
.ordgrid { display: flex; flex-wrap: wrap; gap: 6pt 8pt; }
.ordgrid .it { display: flex; align-items: center; gap: 6pt; width: 31%; }
.ordgrid .it .bk { flex: 0 0 0.4in; border-bottom: 1pt solid #000; height: 18pt; }
.ordgrid .it .bv { font-size: 22pt; }
.ordgrid .it .wd { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 11.5pt; }
.q .hint { font-size: 10pt; color: #333; margin: 0 0 4pt; }
.kq { border: 1.3pt solid #000; border-radius: 7pt; padding: 5pt 12pt 6pt; margin-bottom: 5pt; }
.kq .kh { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 12.5pt; letter-spacing: .02em; margin-bottom: 3pt; }
.kq .kh i { font-style: normal; color: ACCENT; }
.kq .kl { display: flex; flex-wrap: wrap; gap: 3pt 12pt; font-size: 11.5pt; }
.kq .kl span b { font-family: 'Oswald'; font-weight: 700; margin-right: 5pt; }
.kq .kl .bv { font-size: 18pt; vertical-align: middle; }
.kq .kl .ok { background: TINT; border-radius: 4pt; padding: 0 4pt; }
.kq p { margin: 2pt 0 0; font-size: 10.6pt; line-height: 1.3; }
.cover { align-items: center; justify-content: space-between; padding: 0.55in 0.6in 0.5in; }
.store { font-family: 'Oswald'; font-weight: 500; font-size: 13pt; letter-spacing: .32em; text-transform: uppercase; }
.ctitle { text-align: center; }
.ctitle .a { font-family: 'Oswald'; font-weight: 700; font-size: 50pt; line-height: 1; letter-spacing: .02em; }
.ctitle .b { font-family: 'Oswald'; font-weight: 700; white-space: nowrap; font-size: 72pt; line-height: .95; letter-spacing: .01em; }
.ctitle .c { font-family: 'Oswald'; font-weight: 300; font-size: 17pt; margin-top: 8pt; }
.cband { width: 100%; background: #000; color: #fff; text-align: center; font-family: 'Oswald'; font-weight: 500; font-size: 14pt;
         letter-spacing: .08em; text-transform: uppercase; padding: 8pt 0 9pt; border-radius: 4pt; }
.cband em { font-style: normal; color: #8FC3EC; }
""".replace("ACCENT", ACCENT).replace("TINT", TINT)


def html_doc(pages, title="doc"):
    return (f'<!doctype html><html><head><meta charset="utf-8"><title>{escape(title)}</title>'
            f'<style>{font_css()}{CSS}</style></head><body>{"".join(pages)}</body></html>')


COPY = f"© {YEAR} {STORE} · {BRAND} · For single-classroom use"


def foot(right):
    return f'<div class="foot"><span>{COPY}</span><span>{right}</span></div>'


def page(kind, inner, wm=False, cls="", right=None):
    n = PAGEOF[kind]
    w = '<div class="wm">PREVIEW</div>' if wm else ""
    return (f'<section class="page {cls}" data-page="{n}" data-kind="{kind}" data-name="{escape(PAGE_NAMES[kind])}">{w}{inner}'
            f'{foot(right or f"Page {n}")}</section>')


def top(title, sub, tag, tagline, cls=""):
    return (f'<div class="top"><div class="h t">{title}<small>{sub}</small></div>'
            f'<div class="tag {cls}"><div class="lv">{tag}</div><div class="ln">{tagline}</div></div></div>')


def namebar():
    return '<div class="name">Name<span></span>Date<span class="s"></span></div>'


# ------------------------------------------------------------------ posters
def strip(keys, on, order, caption):
    items = ""
    for k in order:
        inner = gl(k) if k in [d["key"] for d in DYN] else D[k]["term"]
        items += f'<div class="s{" on" if k in on else ""}" data-s="{k}">{inner}</div>'
    return (f'<div class="blk" style="width:100%"><div class="stripcap"><span>{caption[0]}</span><span>{caption[1]}</span></div>'
            f'<div class="strip" data-strip="{",".join(order)}">{items}</div></div>')


def term_attrs(x):
    return (f'data-term="{x["term"]}" data-abbr="{x["abbr"]}" data-meaning="{x["meaning"]}" data-bpm="{x.get("bpm", "")}"')


def poster_page(i, wm=False):
    keys = POSTERS[i - 1]
    kick = f'<div class="pk blk">{TITLE} · Poster {i} of {NPOST}</div>'
    k0 = keys[0]
    if k0 in DYN_ORDER:
        x = D[k0]
        sub, tip = TIPS[k0]
        inner = (kick +
                 f'<div class="pt blk" data-poster="{i}" {term_attrs(x)} data-g="{x["glyph"]:X}" data-rank="{x["rank"]}">{x["term"]}</div>'
                 f'<div class="symrow blk"><div class="symbox">{gl(k0)}</div>{icon_bars(x["rank"])}</div>'
                 f'<div class="pm blk">{x["meaning"]}</div>'
                 f'<div class="psub blk">{sub}</div>'
                 + strip(keys, [k0], DYN_ORDER, ("softest", "loudest")) +
                 f'<div class="prem blk">{tip}</div>')
    elif k0 in ("cresc", "decresc"):
        opening = k0 == "cresc"
        xs = [D[k] for k in keys]
        if opening:
            x = xs[0]
            head = f'<div class="pt blk" data-poster="{i}" {term_attrs(x)}>{x["term"]}<small class="ab">{x["abbr"]}</small></div>'
            demo = f'<div class="demo blk">{gl("p")}{hairpin(True, 520, 150, 9, "hp")}{gl("f")}</div>'
            sub = "Crescendo means gradually getting louder. The hairpin opens wider as the sound grows, so start soft and build."
            tip = "Think: a wave rolling in"
        else:
            head = (f'<div class="pt blk m" data-poster="{i}">DECRESCENDO'
                    f'<small>or diminuendo</small></div>')
            demo = f'<div class="demo blk">{gl("f")}{hairpin(False, 520, 150, 9, "hp")}{gl("p")}</div>'
            sub = ("Decrescendo and diminuendo both mean gradually getting softer. The hairpin closes as the sound fades, "
                   "so start louder and ease down. Short forms: decresc. and dim.")
            tip = "Think: a wave rolling out"
        inner = (kick + head +
                 f'<div class="symrow blk"><div class="symbox wide">{hairpin(opening, 560, 190, 10, "hp")}</div></div>'
                 f'<div class="pm blk">{xs[0]["meaning"]}</div>'
                 f'<div class="psub blk">{sub}</div>' + demo +
                 f'<div class="prem blk">{tip}</div>')
    else:
        blocks = ""
        for k in keys:
            x = D[k]
            if k in TEMPO_ORDER:
                ic = icon_gauge(x["gauge"], k)
                chip = f'<div class="tb2">About {x["bpm"]} BPM</div>'
                ab = ""
            else:
                ic = icon_dots(k == "accel")
                chip = '<div class="tb2 n">The beat speeds up</div>' if k == "accel" else '<div class="tb2 n">The beat slows down</div>'
                ab = f'<span class="ab">{x["abbr"]}</span>'
            blocks += (f'<div class="tb blk" data-poster-term="{i}" {term_attrs(x)}>{ic}<div class="tx">'
                       f'<div class="tn">{x["term"]}{ab}</div><div class="tm">{x["meaning"]}</div>{chip}</div></div>')
        title = " &amp; ".join(D[k]["term"] for k in keys)
        small = " m" if len(title) > 14 else ""
        if k0 in TEMPO_ORDER:
            sub = ""
            bottom = (strip(keys, keys, TEMPO_ORDER, ("slowest", "fastest")) + f'<div class="pnote blk">{BPM_NOTE}</div>')
        else:
            bottom = ('<div class="psub blk">Accelerando means the tempo gradually gets faster. Ritardando means it gradually gets slower. '
                      'Both change the speed a little at a time, never all at once.</div>'
                      '<div class="prem blk">Think: a train leaving the station, then pulling in</div>')
        inner = (kick + f'<div class="pt m blk" data-poster="{i}">{title}</div>' + blocks + bottom)
    return page(f"poster{i}", inner, wm, "poster")


# ------------------------------------------------------------------ reference sheet
def reference_page(wm=False):
    rows = ""
    for k in DYN_ORDER:
        x = D[k]
        rows += (f'<tr data-refrow="{k}" data-term="{x["term"]}" data-abbr="{x["abbr"]}" data-meaning="{x["meaning"]}"><td class="tm">{x["term"]}</td>'
                 f'<td class="sy">{gl(k)}</td><td>{x["meaning"]}</td></tr>')
    for k, op in (("cresc", True), ("decresc", False), ("dim", False)):
        x = D[k]
        rows += (f'<tr data-refrow="{k}" data-term="{x["term"]}" data-abbr="{x["abbr"]}" data-meaning="{x["meaning"]}"><td class="tm">{x["term"]} ({x["abbr"]})</td>'
                 f'<td class="sy">{hairpin(op, 90, 32, 3, "hp")}</td><td>{x["meaning"]}</td></tr>')
    dyn = (f'<table class="rt blk"><tr><th style="width:36%">Dynamics</th><th style="width:20%">Symbol</th><th>Meaning</th></tr>{rows}</table>')
    trows = ""
    for k in TEMPO_ORDER + ["accel", "rit"]:
        x = D[k]
        bpm = f'about {x["bpm"]}' if x.get("bpm") else "changes gradually"
        ab = f' ({x["abbr"]})' if x["abbr"] else ""
        trows += (f'<tr data-refrow="{k}" data-term="{x["term"]}" data-abbr="{x["abbr"]}" data-meaning="{x["meaning"]}" data-bpm="{x.get("bpm", "")}">'
                  f'<td class="tm">{x["term"]}{ab}</td><td>{x["meaning"]}</td><td>{bpm}</td></tr>')
    tem = (f'<table class="rt blk"><tr><th style="width:36%">Tempo</th><th style="width:30%">Meaning</th><th>BPM (common ranges)</th></tr>{trows}</table>')
    dline = "".join(gl(k) + ('<span class="ar">→</span>' if k != DYN_ORDER[-1] else "") for k in DYN_ORDER)
    tline = " <span class='ar'>→</span> ".join(f'<span class="wd" style="font-family:Oswald;font-weight:700;text-transform:uppercase;font-size:11pt">{k}</span>' for k in TEMPO_ORDER)
    inner = (top("Student Reference Sheet", f"{TITLE}: every term, symbol and meaning", "REFERENCE", "keep in your folder") + namebar() + dyn + tem +
             f'<div class="ordline blk" data-order="dyn" data-seq="{",".join(DYN_ORDER)}"><b>Softest to loudest</b>{dline}</div>'
             f'<div class="ordline blk" data-order="tempo" data-seq="{",".join(TEMPO_ORDER)}"><b>Slowest to fastest</b>{tline}</div>'
             f'<div class="small blk" style="font-size:9.5pt">{BPM_NOTE}</div>')
    return page("ref", inner, wm, "doc")


# ------------------------------------------------------------------ quiz
def sym_html(k):
    return gl(k) if k in DYN_ORDER else f'<span class="wd">{k}</span>'


def match_block(m, kind):
    left = "".join(f'<div class="it" data-item="{it}"><div class="bk"></div>{sym_html(it)}</div>' for it in m["items"])
    right = "".join(f'<div class="mn" data-letter="{LET[i]}" data-val="{mm}"><b>{LET[i]}.</b><span>{mm}</span></div>' for i, mm in enumerate(m["meanings"]))
    ttl = "Match each dynamic symbol to its meaning. Write the letter on the line." if kind == "dyn" else "Match each tempo word to its meaning. Write the letter on the line."
    return (f'<div class="q blk" data-qn="{m["n"]}" data-qtype="match-{kind}"><div class="qh"><i>{m["n"]}.</i><span>{ttl}</span><span class="pt1">{len(m["items"])} points</span></div>'
            f'<div class="mt"><div class="col">{left}</div><div class="col">{right}</div></div></div>')


def mc_block(q):
    kind, val = q["ask"]
    extra = hairpin(True, 110, 40, 4, "hp") if kind == "hairpin" else ""
    opts = ""
    for i, o in enumerate(q["opts"]):
        shown = sym_html(o) if (kind == "meaning" and o in DYN_ORDER) else escape(("Get " + o) if kind == "hairpin" else o)
        if kind == "term":
            shown = o.capitalize()
        elif kind == "meaning" and o not in DYN_ORDER:
            shown = o
        opts += f'<div class="op" data-opt="{"ABCD"[i]}" data-val="{escape(o)}"><b>{"ABCD"[i]}.</b><span>{shown}</span></div>'
    return (f'<div class="q blk" data-qn="{q["n"]}" data-qtype="mc" data-ask="{kind}:{val if kind != "hairpin" else "cresc"}"><div class="qh"><i>{q["n"]}.</i><span>{escape(q["text"])}</span>{extra}'
            f'<span class="pt1">1 point</span></div><div class="opgrid">{opts}</div></div>')


def order_block(m, kind):
    items = "".join(f'<div class="it" data-item="{it}"><div class="bk"></div>{sym_html(it)}</div>' for it in m["items"])
    if kind == "dyn":
        ttl, hint = "Put these dynamics in order from softest to loudest.", "Write 1 for the softest and 6 for the loudest."
    else:
        ttl, hint = "Put these tempo words in order from slowest to fastest.", "Write 1 for the slowest and 6 for the fastest."
    return (f'<div class="q blk" data-qn="{m["n"]}" data-qtype="order-{kind}"><div class="qh"><i>{m["n"]}.</i><span>{ttl}</span><span class="pt1">1 point</span></div>'
            f'<div class="hint">{hint}</div><div class="ordgrid">{items}</div></div>')


QBLOCKS = {}


def quiz1_page(wm=False):
    inner = (top("Quiz", f"{TITLE} · {NQ} questions · {QUIZ_POINTS} points in all", "QUIZ", "page 1 of 2") + namebar() +
             match_block(MATCH_DYN, "dyn") + match_block(MATCH_TEMPO, "tempo") +
             mc_block(MC[0]) + mc_block(MC[1]))
    return page("quiz1", inner, wm, "doc")


def quiz2_page(wm=False):
    inner = (top("Quiz", f"{TITLE} · questions 5 to {NQ}", "QUIZ", "page 2 of 2") + namebar() +
             mc_block(MC[2]) + mc_block(MC[3]) + order_block(ORDER_DYN, "dyn") + order_block(ORDER_TEMPO, "tempo") +
             mc_block(MC[4]) + mc_block(MC[5]))
    return page("quiz2", inner, wm, "doc")


def seq_html(keys):
    return " ".join(f'<span class="ok">{sym_html(k)}</span>' if False else f'<span>{sym_html(k)}</span>' for k in keys)


def key_page(wm=False):
    def kmatch(m, kind):
        kk = match_key(m, kind)
        cells = "".join(f'<span data-keyitem="{it}" data-answer="{kk[it]}"><b>{kk[it]}</b>{sym_html(it)}</span>' for it in m["items"])
        return (f'<div class="kq blk" data-keyq="{m["n"]}"><div class="kh">Question {m["n"]} <i>· 1 point for each correct match</i></div>'
                f'<div class="kl">{cells}</div></div>')

    def kmc(q):
        good = mc_truth(q)[0]
        opts = "".join(f'<span class="{"ok" if "ABCD"[i] == good else ""}"><b>{"ABCD"[i]}.</b>'
                       f'{(sym_html(o) if (q["ask"][0] == "meaning" and o in DYN_ORDER) else escape(o))}</span>' for i, o in enumerate(q["opts"]))
        return (f'<div class="kq blk" data-keyq="{q["n"]}" data-answer="{good}"><div class="kh">Question {q["n"]} <i>· Answer: {good}</i></div>'
                f'<div class="kl">{opts}</div></div>')

    def korder(m, kind):
        order = DYN_ORDER if kind == "dyn" else TEMPO_ORDER
        pos = {k: i + 1 for i, k in enumerate(order)}
        cells = "".join(f'<span data-keyitem="{it}" data-answer="{pos[it]}"><b>{pos[it]}</b>{sym_html(it)}</span>' for it in m["items"])
        seq = " → ".join(order)
        return (f'<div class="kq blk" data-keyq="{m["n"]}" data-seq="{",".join(order)}"><div class="kh">Question {m["n"]} <i>· 1 point for the whole order</i></div>'
                f'<div class="kl">{cells}</div><p>In order: {" → ".join(sym_html(k) if k in DYN_ORDER else k for k in order)}</p></div>')

    body = (kmatch(MATCH_DYN, "dyn") + kmatch(MATCH_TEMPO, "tempo") + "".join(kmc(q) for q in MC[:2]) + "".join(kmc(q) for q in MC[2:4]) +
            korder(ORDER_DYN, "dyn") + korder(ORDER_TEMPO, "tempo") + "".join(kmc(q) for q in MC[4:]))
    inner = (top("Quiz Answer Key", f"{NQ} questions · {QUIZ_POINTS} points in all", "ANSWER KEY", f"for {R('quiz1')} and {R('quiz2')}", "key") +
             '<div class="doc" style="margin-top:8pt">' + body +
             f'<p class="small">Scoring: {QUIZ_POINTS} points. Questions 1 and 2 give 1 point for each correct match, questions 3 to 6, 9 and 10 give 1 point each, '
             f'and questions 7 and 8 give 1 point each when the whole order is right.</p></div>')
    return page("key", inner, wm)


# ------------------------------------------------------------------ teacher notes, terms, cover
def teacher_page(wm=False):
    inner = (f'<div class="rule"><h1>Teacher Notes</h1><div class="l" style="font-size:13pt">{TITLE} anchor charts: {NPOST} posters, a reference sheet and a quiz</div></div>'
             f'<div class="cols"><div>'
             f'<h2>What is inside</h2><p>{RR("poster1", f"poster{NPOST}", True)} hold {NPOST} posters. Posters 1 to 6 each show one dynamic from pianissimo to fortissimo. '
             f'Poster 7 is crescendo, poster 8 is decrescendo and diminuendo, and posters 9 to 12 show the tempo words in pairs: largo and adagio, andante and moderato, allegro and presto, '
             f'accelerando and ritardando. The reference sheet is on {R("ref")}, the {NQ}-question quiz on {RR("quiz1", "quiz2")} and the key on {R("key")}.</p>'
             f'<h2>How to display</h2><ul><li>Print each poster on one US Letter page. For smaller charts, print two to a sheet from your printer settings.</li>'
             f'<li>Hang the dynamics posters 1 to 6 in a row from softest to loudest, with the crescendo and decrescendo posters under them.</li>'
             f'<li>Hang the tempo posters on another wall, slowest to fastest, so the order is part of the picture.</li>'
             f'<li>Prints well in black and white. The blue is one accent color.</li></ul>'
             f'<h2>Rotating word wall</h2><p>Post two or three posters at a time. Each week add the next poster, move the oldest to a folder, '
             f'and start class by asking students to point to the word that fits the day\'s song. Keep the reference sheet in student folders so every term stays in reach.</p>'
             f'<h2>About the BPM ranges</h2><p>BPM means beats per minute. The tempo posters give common ranges, such as largo about 40–60 and presto about 168–200. '
             f'Books, apps and teachers use slightly different numbers, and a conductor may choose a speed inside or outside a range, so treat them as guides, not rules.</p>'
             f'</div><div>'
             f'<h2>Games</h2><ul><li><b>Point and play.</b> Point to a dynamics poster. The class says a short rhyme at that level.</li>'
             f'<li><b>Human crescendo.</b> The class starts at pp and, row by row, grows to ff as you raise your hand.</li>'
             f'<li><b>Tempo walk.</b> Set a metronome app to about 60, 90, 120 and 170 BPM. Students walk to the beat and name the tempo word.</li>'
             f'<li><b>Mystery poster.</b> Cover a poster\'s heading. Students guess the term from the meaning.</li>'
             f'<li><b>Order race.</b> Teams line up cards pp to ff, or largo to presto, as fast as they can.</li></ul>'
             f'<h2>Grades 2 to 4</h2><ul><li>Start with the six dynamics and the four words largo, andante, allegro and presto.</li>'
             f'<li>Use the posters orally: point, say, echo and move.</li>'
             f'<li>Give the quiz aloud or in small groups, and read each question to the class.</li></ul>'
             f'<h2>Grades 5 to 8</h2><ul><li>Add the symbols, abbreviations and all eight tempo words, plus the BPM ranges.</li>'
             f'<li>Students find three dynamic or tempo markings in their own band, choir or orchestra music and explain what they ask the player to do.</li>'
             f'<li>Give the quiz on its own as an assessment. Use the key on {R("key")} to score it out of {QUIZ_POINTS} points.</li></ul>'
             f'<h2>A note on meanings</h2><p>Mezzo means medium or half. Piano means soft and forte means loud, so mezzo piano is a little louder than piano and mezzo forte is a little softer than forte.</p>'
             f'</div></div><div class="fill"></div>')
    return page("teacher", inner, wm, "doc")


def terms_page(wm=False):
    inner = (f'<div class="rule"><h1>Terms of Use</h1><div class="l" style="font-size:13pt">Thank you for your purchase!</div></div>'
             f'<p>© {YEAR} {STORE}. {BRAND} by {STORE}. All rights reserved. This purchase gives <b>one teacher</b> a license to use this resource with their own students.</p>'
             f'<h2>You may</h2><ul><li>Print and copy pages for your own classroom and students, year after year.</li>'
             f'<li>Share pages with your own students through a password-protected class site or learning platform.</li>'
             f'<li>Use the pages with your own students when you have a substitute teacher.</li></ul>'
             f'<h2>You may not</h2><ul><li>Share, email or copy this resource for other teachers, a whole school or a district. '
             f'Additional licenses are available on Teachers Pay Teachers.</li>'
             f'<li>Post any part of it on a public website, shared drive or social media.</li>'
             f'<li>Sell, give away or claim any part of it as your own, or edit it into a new product.</li></ul>'
             f'<h2>Questions?</h2><p>Please use the Q&amp;A tab on the {BRAND} by {STORE} store on Teachers Pay Teachers. '
             f'If something looks wrong, let me know there and I will fix it.</p>'
             f'<h2>Credits</h2><ul>'
             f'<li>Posters, reference sheet, quiz, key and icons: original work, {BRAND} by {STORE}.</li>'
             f'<li>Cover illustration: house-style line art made with digital tools by {BRAND}.</li>'
             f'<li>Dynamic letters: Bravura © Steinberg Media Technologies GmbH, SIL Open Font License 1.1.</li>'
             f'<li>Text fonts: Oswald (The Oswald Project Authors) and Source Sans 3 (Adobe), SIL Open Font License 1.1.</li></ul>'
             f'<h2>What is in this file</h2><p>{R("cover", True)} cover, {R("teacher")} teacher notes, {RR("poster1", f"poster{NPOST}")} the {NPOST} posters, '
             f'{R("ref")} student reference sheet, {RR("quiz1", "quiz2")} quiz, {R("key")} quiz answer key and {R("terms")} these terms: '
             f'{TOTAL_PAGES} pages in all.</p>'
             f'<p class="small">{DISCLOSURE}</p><div class="fill"></div>')
    return page("terms", inner, wm, "doc")


SUBTITLE = f"{NPOST} music posters, a student reference sheet and a quiz with key"


def cover_page():
    return (f'<section class="page cover" data-page="1" data-kind="cover" data-name="Cover"><div class="store">{BRAND}</div>'
            f'<div style="height:4.4in;display:flex;align-items:center;justify-content:center"><img src="../art/hero.png" style="height:4.2in;display:block" alt=""></div>'
            f'<div class="ctitle"><div class="a">DYNAMICS &amp; TEMPO</div><div class="b">ANCHOR CHARTS</div>'
            f'<div class="c">{SUBTITLE}</div></div>'
            f'<div class="cband">Grades 2–8 <em>·</em> {NPOST} posters <em>·</em> {TOTAL_PAGES} pages</div></section>')


def all_pages(wm=False):
    p = [cover_page(), teacher_page(wm)] + [poster_page(i, wm) for i in range(1, NPOST + 1)]
    p += [reference_page(wm), quiz1_page(wm), quiz2_page(wm), key_page(wm), terms_page(wm)]
    return p


SHOT_PAGES = {k: v for k, v in PAGEOF.items() if k != "cover"}
PREVIEW_ORDER = ["poster1", "poster9", "ref", "key"]

# ------------------------------------------------------------------ square images
SQ_CSS = """
.sq { width: 1000px; height: 1000px; position: relative; overflow: hidden; background: #fff; display: flex; flex-direction: column; align-items: center; }
.sq .store { font-family: 'Oswald'; font-weight: 500; letter-spacing: .32em; text-transform: uppercase; font-size: 22px; margin-top: 34px; }
.sq .hd { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; text-align: center; line-height: .95; }
.sq .sub { font-family: 'Oswald'; font-weight: 300; text-align: center; }
.sq .band { position: absolute; left: 0; right: 0; bottom: 0; background: #000; color: #fff; text-align: center; font-family: 'Oswald';
            font-weight: 500; text-transform: uppercase; letter-spacing: .1em; font-size: 26px; padding: 16px 0 18px; }
.sq .band em { font-style: normal; color: #8FC3EC; }
.shot { background: #fff; border: 2px solid #000; box-shadow: 8px 8px 0 #000; position: relative; overflow: hidden; }
.shot img { display: block; width: 100%; }
.lbl { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 22px; text-align: center; margin-top: 18px; }
.lbl span { font-weight: 300; text-transform: none; display: block; font-size: 19px; margin-top: 2px; }
"""


def sq_doc(body):
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{font_css()}'
            f'html,body{{margin:0;background:#fff}}{SQ_CSS}</style></head><body>{body}</body></html>')


def cover_square():
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div>'
        f'<div style="flex:1;display:flex;flex-direction:column;justify-content:space-evenly;align-items:center;width:100%;padding:0 0 76px">'
        f'<div style="height:540px;display:flex;align-items:center;justify-content:center"><img src="../art/hero.png" style="height:540px;display:block" alt=""></div>'
        f'<div><div class="hd" style="font-size:70px">Dynamics &amp; Tempo</div>'
        f'<div class="hd" style="font-size:118px">Anchor Charts</div>'
        f'<div class="sub" style="font-size:28px;margin-top:12px">{SUBTITLE}</div></div>'
        f'</div><div class="band">Grades 2–8 <em>·</em> {NPOST} posters <em>·</em> {TOTAL_PAGES} pages</div></div>')


def shots(items, w, gap, grid=False, lblsize=22):
    out = "".join(f'<div style="width:{w}px"><div class="shot"><img src="{src}"></div><div class="lbl" style="font-size:{lblsize}px;margin-top:{lblsize - 6}px">{lab}</div></div>' for src, lab in items)
    return out


def shots_row(headline, sub, items, band, w):
    gap = 40
    return sq_doc(f'<div class="sq"><div class="store">{BRAND}</div>'
                  f'<div class="hd" style="font-size:66px;margin-top:24px">{headline}</div>'
                  f'<div class="sub" style="font-size:27px;margin-top:8px">{sub}</div>'
                  f'<div style="flex:1;display:flex;align-items:center;padding-bottom:74px"><div style="display:flex;gap:{gap}px;align-items:flex-start">{shots(items, w, gap)}</div></div>'
                  f'<div class="band">{band}</div></div>')


def shots_grid(headline, sub, items, band, w):
    return sq_doc(f'<div class="sq"><div class="store">{BRAND}</div>'
                  f'<div class="hd" style="font-size:66px;margin-top:24px">{headline}</div>'
                  f'<div class="sub" style="font-size:27px;margin-top:8px">{sub}</div>'
                  f'<div style="flex:1;display:flex;flex-direction:column;align-items:center;justify-content:space-evenly;padding-bottom:74px"><div style="display:flex;flex-wrap:wrap;justify-content:center;gap:30px 12px;width:900px">'
                  f'{shots(items, w, 12, True, 14)}</div>'
                  f'<div class="sub" style="font-size:30px">Dynamics: posters 1 to 8 <em style="font-style:normal">·</em> Tempo: posters 9 to {NPOST}</div></div><div class="band">{band}</div></div>')


def label(kind, extra):
    return f'{PAGE_NAMES[kind]}<span>{extra}</span>'


def poster_title(i):
    return " &amp; ".join(D[k]["term"] for k in POSTERS[i - 1]).replace("decrescendo &amp; diminuendo", "decrescendo &amp; diminuendo")


def square_pages():
    return [
        shots_grid(f"{NPOST} printable posters", "Dynamics and tempo, each with a symbol, a meaning and a simple picture",
                   [(f"shot-poster{i}.png", label(f"poster{i}", poster_title(i))) for i in range(1, NPOST + 1)],
                   f"{NPOST} posters <em>·</em> grades 2–8 <em>·</em> no prep", 136),
        shots_row("Reference sheet and quiz", f"Every term on one page, then a {NQ}-question quiz",
                  [("shot-ref.png", label("ref", "all terms, symbols and meanings")),
                   ("shot-quiz1.png", label("quiz1", "matching and multiple choice"))],
                  f"{NQ} questions <em>·</em> {QUIZ_POINTS} points <em>·</em> {TOTAL_PAGES} pages", 420),
        shots_row("Quiz with answer key", "One correct answer for every question",
                  [("shot-quiz2.png", label("quiz2", "order the dynamics and the tempos")),
                   ("shot-key.png", label("key", f"{QUIZ_POINTS} points in all"))],
                  f"{NQ} questions <em>·</em> {QUIZ_POINTS} points <em>·</em> key included", 420),
    ]


# ------------------------------------------------------------------ render / build
def node_env():
    env = dict(os.environ)
    if not env.get("NODE_PATH"):
        env["NODE_PATH"] = subprocess.run(["npm", "root", "-g"], capture_output=True, text=True).stdout.strip()
    return env


def render(jobs):
    path = os.path.join(BUILD, "jobs.json")
    with open(path, "w") as f:
        json.dump(jobs, f)
    subprocess.run(["node", RENDER_JS, path], check=True, env=node_env())


def write(name, text):
    p = os.path.join(BUILD, name)
    with open(p, "w") as f:
        f.write(text)
    return p


def upload_md():
    return f"""# UPLOAD: {LISTING_TITLE} (TpT 058)

These fields follow the order of TpT's "Add a resource" form. Evergreen: no season, sell all year (strongest at the start of the school year and before concerts).

**Files to attach**
- Resource (digital download): `{SLUG}.pdf`, {TOTAL_PAGES} pages, US Letter.
- Thumbnails, in this order: `cover.png`, `preview-1.png`, `preview-2.png`, `preview-3.png` (all 2000 × 2000).
- Preview file: `{SLUG}-PREVIEW.pdf`, 4 watermarked pages.

## 1. Title

```
{LISTING_TITLE}
```
({len(LISTING_TITLE)} characters; the limit is 80.) Plain search words first, no seasonal words.

## 2. Description

```
Make music dynamics and tempo easy to see with {NPOST} printable anchor chart posters, a one-page student reference sheet and a {NQ}-question quiz with an answer key. Each poster has a large heading, a short definition, a simple picture and the symbol where there is one. It works for general music, band, orchestra and choir in grades 2 to 8, and nothing in it is tied to a season or a holiday.

WHAT'S INCLUDED ({TOTAL_PAGES} pages, PDF, US Letter)
• Cover (1 page)
• Teacher notes: how to display the posters, a rotating word wall, games, and differentiation for grades 2-4 and grades 5-8 (1 page)
• {NPOST} printable posters, one per page (12 pages): pianissimo (pp), piano (p), mezzo piano (mp), mezzo forte (mf), forte (f), fortissimo (ff), crescendo (cresc.), decrescendo and diminuendo (decresc., dim.), largo and adagio, andante and moderato, allegro and presto, accelerando (accel.) and ritardando (rit.)
• Student reference sheet with all terms, symbols and meanings (1 page)
• Quiz with {NQ} questions worth {QUIZ_POINTS} points: matching, multiple choice, order the dynamics from softest to loudest, order the tempos from slowest to fastest (2 pages)
• Quiz answer key (1 page)
• Terms of use and credits (1 page)
Total: {TOTAL_PAGES} pages.

HOW TO USE
Hang the posters as a word wall or rotate two or three at a time, hand out the reference sheet, and finish with the quiz. The tempo posters give about BPM ranges (beats per minute), such as largo about 40-60 and presto about 168-200, and say that books and teachers use slightly different numbers.

• Grades 2–8 (differentiation for grades 2-4 and grades 5-8 in the teacher notes)
• Prints well in black and white; one accent color
• No songs, lyrics or copyrighted characters

{DISCLOSURE}
```

## 3. Grades

3, 4, 5, 6 (TpT allows four; the product is written for grades 2 to 8).

## 4. Subjects and tags

- Subjects: {", ".join(SUBJECTS)}
- Tags: {", ".join(TAGS)}

## 5. Page count by section (totals {TOTAL_PAGES})

- Cover: 1
- Teacher notes: 1
- Posters: {NPOST}
- Student reference sheet: 1
- Quiz: 2
- Quiz answer key: 1
- Terms of use and credits: 1
- Total: {TOTAL_PAGES}

## 6. Standards

None cited. The teacher notes ask teachers to match the activities to their own curriculum.

## 7. Price

**${PRICE}** (paid; owner range $3–5).

## 8. Preview

Paid. Preview PDF: poster 1, poster 9, the student reference sheet and the quiz answer key, all watermarked.

## 9. Before you click publish

- [ ] Evergreen: no season, no holiday words.
- Open owner question: logo beside HUDSON BEAT (see tpt/STYLE.md).
"""


def tpt_json():
    return {
        "price": PRICE, "license_price": PRICE, "tax_code": "Other Digital Goods - No Physical Media",
        "grades": GRADES, "subjects": SUBJECTS, "tags": TAGS, "formats": ["PDF"], "pages": TOTAL_PAGES,
        "files": {"product": f"{SLUG}.pdf", "preview": f"{SLUG}-PREVIEW.pdf", "thumb1": "cover.png", "thumb2": "preview-1.png",
                  "thumb3": "preview-2.png", "thumb4": "preview-3.png"},
    }


def build():
    os.makedirs(BUILD, exist_ok=True)
    full = write("resource.html", html_doc(all_pages(False), TITLE))
    shot = write("shots.html", html_doc(all_pages(True), "Preview shots"))
    sq = [write("cover.html", cover_square())]
    render([{"html": full, "pdf": PDF}, {"html": shot, "pdf": os.path.join(BUILD, "shots.pdf")}])
    from pypdf import PdfReader, PdfWriter
    rd = PdfReader(os.path.join(BUILD, "shots.pdf"))
    wr = PdfWriter()
    for k in PREVIEW_ORDER:
        wr.add_page(rd.pages[SHOT_PAGES[k] - 1])
    with open(PREVIEW_PDF, "wb") as f:
        wr.write(f)
    for k, n in SHOT_PAGES.items():
        subprocess.run(["pdftoppm", "-png", "-r", "150", "-f", str(n), "-l", str(n), "-singlefile",
                        os.path.join(BUILD, "shots.pdf"), os.path.join(BUILD, f"shot-{k}")], check=True)
    for i, h in enumerate(square_pages(), 1):
        sq.append(write(f"p{i}.html", h))
    render([{"html": h, "png": o, "width": 1000, "height": 1000, "scale": 2} for h, o in zip(sq, [COVER_PNG] + PREVIEW_PNGS)])
    with open(UPLOAD, "w") as f:
        f.write(upload_md())
    with open(TPT_JSON, "w") as f:
        json.dump(tpt_json(), f, indent=2)
        f.write("\n")
    print(f"built {PDF}, {PREVIEW_PDF}, cover + 3 previews, UPLOAD.md, tpt.json")


# ------------------------------------------------------------------ checks
# A second table, typed separately from the one above: every poster, abbreviation, meaning and BPM range the buyer will see.
EXPECT_TERMS = {
    "pianissimo": ("pp", "very soft", "", 0xE52B), "piano": ("p", "soft", "", 0xE520), "mezzo piano": ("mp", "medium soft", "", 0xE52C),
    "mezzo forte": ("mf", "medium loud", "", 0xE52D), "forte": ("f", "loud", "", 0xE522), "fortissimo": ("ff", "very loud", "", 0xE52F),
    "crescendo": ("cresc.", "gradually louder", "", 0), "decrescendo": ("decresc.", "gradually softer", "", 0),
    "diminuendo": ("dim.", "gradually softer", "", 0),
    "largo": ("", "very slow", "40–60", 0), "adagio": ("", "slow", "66–76", 0), "andante": ("", "walking pace", "76–108", 0),
    "moderato": ("", "moderate speed", "108–120", 0), "allegro": ("", "fast", "120–156", 0), "presto": ("", "very fast", "168–200", 0),
    "accelerando": ("accel.", "gradually faster", "", 0), "ritardando": ("rit.", "gradually slower", "", 0),
}
EXPECT_POSTER_TERMS = [["pianissimo"], ["piano"], ["mezzo piano"], ["mezzo forte"], ["forte"], ["fortissimo"], ["crescendo"],
                       ["decrescendo", "diminuendo"], ["largo", "adagio"], ["andante", "moderato"], ["allegro", "presto"],
                       ["accelerando", "ritardando"]]
EXPECT_DYN_ORDER = "pp,p,mp,mf,f,ff"
EXPECT_TEMPO_ORDER = "largo,adagio,andante,moderato,allegro,presto"
EXPECT_BY_ABBR = {v[0]: k for k, v in EXPECT_TERMS.items() if v[0]}
SPELL = ["pianissimo", "fortissimo", "diminuendo", "accelerando", "ritardando", "crescendo", "decrescendo", "mezzo piano", "mezzo forte"]

INSPECT_JS = r"""
const { chromium } = require('playwright');
const url = require('url');
(async () => {
  const b = await chromium.launch();
  const out = {};
  for (const f of process.argv.slice(2)) {
    const p = await b.newPage({ viewport: { width: 816, height: 1056 } });
    await p.goto(url.pathToFileURL(f).href, { waitUntil: 'load' });
    await p.evaluate(() => document.fonts.ready);
    out[f.split('/').pop()] = await p.evaluate(() => {
      const T = el => el ? el.innerText.replace(/\s+/g, ' ').trim() : '';
      const A = (sel, fn) => [...document.querySelectorAll(sel)].map(fn);
      const pageNo = el => { const pg = el.closest('.page'); return pg ? +pg.dataset.page : 0; };
      const d = {};
      d.pages = A('.page', pg => ({ n: +pg.dataset.page, kind: pg.dataset.kind, name: pg.dataset.name, wms: pg.querySelectorAll('.wm').length }));
      d.posterPages = A('.page.poster', pg => ({
        n: +pg.dataset.page, text: T(pg),
        terms: [...pg.querySelectorAll('[data-term]')].map(e => ({ term: e.dataset.term, abbr: e.dataset.abbr, meaning: e.dataset.meaning, bpm: e.dataset.bpm || '', g: e.dataset.g || '' })),
        pm: T(pg.querySelector('.pm')), tms: A2(pg.querySelectorAll('.tm'), T),
        glyphs: [...pg.querySelectorAll('.symbox .bv')].map(e => e.dataset.g),
        strip: pg.querySelector('[data-strip]') ? pg.querySelector('[data-strip]').dataset.strip : '',
        on: [...pg.querySelectorAll('.strip .s.on')].map(e => e.dataset.s),
        heads: T(pg.querySelector('.pt')),
        icons: [...pg.querySelectorAll('svg.icon')].map(s => s.dataset.icon)
      }));
      function A2(list, fn) { return [...list].map(fn); }
      d.refrows = A('[data-refrow]', e => ({ k: e.dataset.refrow, term: e.dataset.term, abbr: e.dataset.abbr, meaning: e.dataset.meaning, bpm: e.dataset.bpm || '', text: T(e), page: pageNo(e),
                                             g: [...e.querySelectorAll('.bv')].map(x => x.dataset.g), hp: [...e.querySelectorAll('svg.icon')].map(s => s.dataset.icon) }));
      d.orders = A('[data-order]', e => ({ k: e.dataset.order, seq: e.dataset.seq, page: pageNo(e), g: [...e.querySelectorAll('.bv')].map(x => x.dataset.g), txt: T(e) }));
      d.qs = A('[data-qn]', e => ({ n: +e.dataset.qn, type: e.dataset.qtype, ask: e.dataset.ask || '', page: pageNo(e),
        opts: [...e.querySelectorAll('[data-opt]')].map(o => ({ l: o.dataset.opt, val: o.dataset.val })),
        items: [...e.querySelectorAll('[data-item]')].map(o => ({ k: o.dataset.item, blanks: o.querySelectorAll('.bk').length })),
        letters: [...e.querySelectorAll('[data-letter]')].map(o => ({ l: o.dataset.letter, val: o.dataset.val })),
        hp: [...e.querySelectorAll('svg.icon')].map(s => s.dataset.icon), pts: T(e.querySelector('.pt1')) }));
      d.keys = A('[data-keyq]', e => ({ n: +e.dataset.keyq, answer: e.dataset.answer || '', seq: e.dataset.seq || '', page: pageNo(e),
        items: [...e.querySelectorAll('[data-keyitem]')].map(o => ({ k: o.dataset.keyitem, a: o.dataset.answer })),
        ok: [...e.querySelectorAll('.ok')].map(o => T(o)), head: T(e.querySelector('.kh')) }));
      d.refs = A('[data-ref]', e => ({ page: pageNo(e), kind: e.dataset.ref, n: +e.dataset.n, kind2: e.dataset.ref2 || '', n2: +(e.dataset.n2 || 0), txt: T(e) }));
      d.pagetext = A('.page', pg => { const c = pg.cloneNode(true); c.querySelectorAll('.foot,.wm').forEach(x => x.remove()); return c.innerText.replace(/\s+/g, ' ').trim(); });
      d.icons = A('svg.icon', s => {
        const g = s.querySelector('g.art'); const bb = g.getBBox(); const sw = +s.dataset.sw; const vb = s.viewBox.baseVal;
        return { page: pageNo(s), icon: s.dataset.icon, x0: bb.x, y0: bb.y, x1: bb.x + bb.width, y1: bb.y + bb.height, sw, w: vb.width, h: vb.height };
      });
      const res = []; d.gaps = [];
      document.querySelectorAll('.page').forEach((pg, i) => {
        const n = i + 1, pr = pg.getBoundingClientRect();
        const ft = pg.querySelector('.foot');
        const ftop = ft ? ft.getBoundingClientRect().top : pr.bottom;
        if (pg.scrollHeight > pg.clientHeight + 1) res.push(`page ${n}: content overflows the page`);
        let low = 0; const boxes = [];
        pg.querySelectorAll('.blk, .top, .name, .doc p, .doc li, .doc table, .doc h2, .q, .kq, .rt').forEach(el => {
          if (ft && ft.contains(el)) return;
          const r = el.getBoundingClientRect();
          if (r.height === 0) return;
          low = Math.max(low, r.bottom);
          if (r.bottom > ftop - 9) res.push(`page ${n}: ${el.tagName}.${el.className} bottom ${(r.bottom - ftop).toFixed(1)}px vs footer rule (needs <= -9)`);
          if (r.right > pr.right - 0.35 * 96 + 0.5 || r.left < pr.left + 0.35 * 96 - 0.5) res.push(`page ${n}: ${el.tagName}.${el.className} too close to the page edge`);
          if (el.matches('.blk')) boxes.push([el, r]);
        });
        for (let a = 0; a < boxes.length; a++) for (let c = a + 1; c < boxes.length; c++) {
          const A = boxes[a][1], C = boxes[c][1];
          if (boxes[a][0].contains(boxes[c][0]) || boxes[c][0].contains(boxes[a][0])) continue;
          const gx = Math.max(A.left, C.left) - Math.min(A.right, C.right);
          const gy = Math.max(A.top, C.top) - Math.min(A.bottom, C.bottom);
          if (gx < 4 && gy < 4) res.push(`page ${n}: ${boxes[a][0].className} and ${boxes[c][0].className} touch or overlap (no gutter)`);
        }
        d.gaps.push(Math.round(ftop - low));
        pg.querySelectorAll('.pt, .pm, .psub, .prem, .pk, .tb, .tn, .tm, .tb2, .symbox, .strip .s, .pnote, .q, .kq, .it, .mn, .op, td, th, .ordline, .stripcap').forEach(el => {
          if (getComputedStyle(el).display === 'inline') return;
          const hasG = !!el.querySelector('.bv') || el.matches('.pt, .tn, .pm, .tm'); if ((!hasG && el.scrollHeight > el.clientHeight + 2) || el.scrollWidth > el.clientWidth + 2) res.push(`page ${n}: text clipped in ${el.tagName}.${el.className} (${el.scrollWidth}x${el.scrollHeight} in ${el.clientWidth}x${el.clientHeight}) ${el.innerText.slice(0,30)}`);
        });
        // every text run and every symbol box on a poster stays inside the page margins and inside its parent box
        pg.querySelectorAll('.pt, .pm, .psub, .prem, .pk, .tn, .tm, .tb2, .pnote, .strip .s, .symbox, .tb').forEach(el => {
          const range = document.createRange(); range.selectNodeContents(el);
          for (const rc of range.getClientRects()) if (rc.left < pr.left + 0.35 * 96 || rc.right > pr.right - 0.35 * 96) res.push(`page ${n}: text reaches the page edge in ${el.className}`);
        });
        pg.querySelectorAll('.symbox, .tb, .strip .s').forEach(box => {
          const br = box.getBoundingClientRect();
          box.querySelectorAll('.bv, svg.icon').forEach(ch => {
            const r = ch.getBoundingClientRect();
            const isG = ch.classList.contains('bv'); if (r.left < br.left + 6 || r.right > br.right - 6 || (!isG && (r.top < br.top + 2 || r.bottom > br.bottom - 2))) res.push(`page ${n}: ${ch.className.baseVal || ch.className} does not sit inside its box with padding`);
          });
        });
        pg.querySelectorAll('img').forEach(im => {
          const r = im.getBoundingClientRect();
          if (r.left < pr.left + 0.2 * 96 || r.right > pr.right - 0.2 * 96 || r.top < pr.top + 0.2 * 96 || r.bottom > ftop) res.push(`page ${n}: an image is too near the page edge`);
          if (!im.complete || im.naturalWidth === 0) res.push(`page ${n}: broken image`);
        });
      });
      d.layout = res;
      return d;
    });
    await p.close();
  }
  await b.close();
  console.log(JSON.stringify(out));
})().catch(e => { console.error(e); process.exit(1); });
"""

ALONE_JS = r"""
// Render every reusable drawing alone on a transparent ground, so its pixels can be checked against the image edge.
const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const spec = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 900, height: 700 } });
  await p.goto(require('url').pathToFileURL(spec.page).href, { waitUntil: 'load' });
  await p.evaluate(() => document.fonts.ready);
  for (const id of spec.ids) await p.locator('#' + id).screenshot({ path: spec.dir + '/' + id + '.png', omitBackground: true });
  await b.close();
})().catch(e => { console.error(e); process.exit(1); });
"""


def inspect_html(files):
    js = os.path.join(BUILD, "inspect.js")
    with open(js, "w") as f:
        f.write(INSPECT_JS)
    r = subprocess.run(["node", js, *files], capture_output=True, text=True, env=node_env())
    if r.returncode != 0:
        sys.exit(f"inspect failed: {r.stderr[-500:]}")
    return json.loads(r.stdout.strip().splitlines()[-1])


UK_SPELLINGS = ["practise", "colour", "favourite", "centre", "metre", "recognise", "organise", "behaviour", "neighbour", "programme", "theatre", "licence"]
QA_WORDS = ["recomputed", "--check", "checked by hand", "handmade", "hand-checked", "classroom-tested", "verified by", "inspector", "QA"]
SEASONAL = r"winter|snow|holiday|christmas|\bfall\b|autumn|spring|summer|halloween|new year|thanksgiving|december"


def count_claims(text, where):
    errs = []
    for m in re.finditer(r"(\d+)[ -](posters?)\b", text):
        if int(m.group(1)) != NPOST:
            errs.append(f"{where}: claims '{m.group(0)}', expected {NPOST}")
    for m in re.finditer(r"(\d+)[ -](questions?)\b", text):
        if int(m.group(1)) not in (NQ, 1):
            errs.append(f"{where}: claims '{m.group(0)}', expected {NQ}")
    for m in re.finditer(r"(\d+) points in all", text):
        if int(m.group(1)) != QUIZ_POINTS:
            errs.append(f"{where}: claims '{m.group(0)}', expected {QUIZ_POINTS}")
    for m in re.finditer(r"(\d+) pages", text):
        if int(m.group(1)) not in (TOTAL_PAGES, NPOST, 2, 1, 4):
            errs.append(f"{where}: claims '{m.group(0)}'")
    return errs


def verify_content(d):
    errs = []
    # --- tables agree with each other
    for k, x in D.items():
        e = EXPECT_TERMS[x["term"]]
        if (x["abbr"], x["meaning"], x.get("bpm", "")) != e[:3]:
            errs.append(f"table: {x['term']} differs from the expected table")
        if x.get("glyph", 0) != e[3]:
            errs.append(f"table: {x['term']} glyph differs")
    if ",".join(DYN_ORDER) != EXPECT_DYN_ORDER:
        errs.append("table: dynamic order is not pp < p < mp < mf < f < ff")
    if ",".join(TEMPO_ORDER) != EXPECT_TEMPO_ORDER:
        errs.append("table: tempo order is not largo < adagio < andante < moderato < allegro < presto")
    # --- posters
    pp = d["posterPages"]
    if len(pp) != NPOST or NPOST != 12:
        errs.append(f"expected 12 posters, found {len(pp)}")
    for i, pg in enumerate(pp):
        want = EXPECT_POSTER_TERMS[i]
        if pg["n"] != P_POST0 + i:
            errs.append(f"poster {i + 1} is on page {pg['n']}")
        txt = pg["text"].lower()
        for t in want:
            e = EXPECT_TERMS[t]
            if t not in txt:
                errs.append(f"poster {i + 1}: term '{t}' missing from the page text")
            if e[1] not in txt:
                errs.append(f"poster {i + 1}: meaning '{e[1]}' missing")
            if e[0] and e[0].lower() not in txt and not e[3]:
                errs.append(f"poster {i + 1}: abbreviation '{e[0]}' missing")
            if e[2] and e[2] not in pg["text"]:
                errs.append(f"poster {i + 1}: BPM range '{e[2]}' missing")
            if not e[2] and re.search(r"about \d+", txt) and i < 8:
                errs.append(f"poster {i + 1}: unexpected BPM")
        if i < 6:
            e = EXPECT_TERMS[want[0]]
            h = pg["terms"][0]
            if (h["term"], h["abbr"], h["meaning"]) != (want[0], e[0], e[1]) or h["g"] != f"{e[3]:X}":
                errs.append(f"poster {i + 1}: heading data {h} differs from {want[0]}")
            if pg["glyphs"] != [f"{e[3]:X}"]:
                errs.append(f"poster {i + 1}: symbol glyph {pg['glyphs']} is not {e[0]}")
            if pg["pm"].lower() != e[1]:
                errs.append(f"poster {i + 1}: meaning banner '{pg['pm']}' != '{e[1]}'")
            if pg["heads"].lower() != want[0]:
                errs.append(f"poster {i + 1}: heading '{pg['heads']}'")
            if pg["strip"] != EXPECT_DYN_ORDER:
                errs.append(f"poster {i + 1}: strip order {pg['strip']}")
            if pg["on"] != [e[0]]:
                errs.append(f"poster {i + 1}: highlighted strip item {pg['on']}")
            if pg["icons"] != [f"bars{i + 1}"]:
                errs.append(f"poster {i + 1}: loudness icon {pg['icons']} does not show level {i + 1} of 6")
            # the loudness scale position equals the order position
            if EXPECT_DYN_ORDER.split(",").index(e[0]) != i:
                errs.append(f"poster {i + 1}: poster order differs from the dynamic order")
        elif i == 6:
            if "cresc." not in pg["text"] or "hairpin-open" not in pg["icons"] or "hairpin-close" in pg["icons"]:
                errs.append("poster 7: crescendo needs the opening hairpin and 'cresc.'")
            if "gradually louder" not in pg["pm"].lower():
                errs.append("poster 7: meaning banner")
        elif i == 7:
            for a in ("decresc.", "dim.", "decrescendo", "diminuendo", "gradually softer"):
                if a not in pg["text"] and a not in pg["text"].lower():
                    errs.append(f"poster 8: missing '{a}'")
            if "hairpin-close" not in pg["icons"] or "hairpin-open" in pg["icons"]:
                errs.append("poster 8: needs the closing hairpin")
        elif i < 11:
            got = [t["term"] for t in pg["terms"]]
            if got != want:
                errs.append(f"poster {i + 1}: terms {got} != {want}")
            for t in pg["terms"]:
                e = EXPECT_TERMS[t["term"]]
                if (t["abbr"], t["meaning"], t["bpm"]) != e[:3]:
                    errs.append(f"poster {i + 1}: {t['term']} data differs")
            if pg["strip"] != EXPECT_TEMPO_ORDER or pg["on"] != [w for w in EXPECT_TEMPO_ORDER.split(",") if w in want]:
                errs.append(f"poster {i + 1}: tempo strip {pg['strip']} / {pg['on']}")
            gauges = [x for x in pg["icons"] if x.startswith("gauge-")]
            if gauges != [f"gauge-{w}" for w in want]:
                errs.append(f"poster {i + 1}: gauge icons {gauges}")
            if "common ranges" not in pg["text"] or "BPM" not in pg["text"]:
                errs.append(f"poster {i + 1}: must say these are common ranges")
        else:
            got = [t["term"] for t in pg["terms"]]
            if got != want:
                errs.append(f"poster 12: terms {got}")
            if pg["icons"] != ["dots-fast", "dots-slow"]:
                errs.append(f"poster 12: icons {pg['icons']}")
            for t in pg["terms"]:
                e = EXPECT_TERMS[t["term"]]
                if (t["abbr"], t["meaning"]) != e[:2]:
                    errs.append(f"poster 12: {t['term']} data differs")
    # tempo order across posters 9-11 (slowest to fastest) and dynamics across posters 1-6
    seq = [t["term"] for pg in pp[8:11] for t in pg["terms"]]
    if ",".join(seq) != EXPECT_TEMPO_ORDER.replace(",", ","):
        errs.append(f"posters 9-11 are not in tempo order: {seq}")
    bpms = []
    for w in EXPECT_TEMPO_ORDER.split(","):
        lo = int(EXPECT_TERMS[w][2].split("–")[0])
        bpms.append(lo)
    if bpms != sorted(bpms) or len(set(bpms)) != 6:
        errs.append("BPM ranges are not in increasing order")
    # --- reference sheet
    rows = {r["k"]: r for r in d["refrows"]}
    for t, e in EXPECT_TERMS.items():
        k = next(kk for kk, x in D.items() if x["term"] == t)
        r = rows.get(k)
        if not r:
            errs.append(f"reference sheet: no row for {t}")
            continue
        if (r["term"], r["abbr"], r["meaning"], r["bpm"]) != (t, e[0], e[1], e[2]):
            errs.append(f"reference sheet: row {t} differs from the expected table")
        if e[2] and f"about {e[2]}" not in r["text"]:
            errs.append(f"reference sheet: {t} does not show its BPM range")
        if e[3] and r["g"] != [f"{e[3]:X}"]:
            errs.append(f"reference sheet: {t} symbol")
        if t in ("crescendo",) and r["hp"] != ["hairpin-open"]:
            errs.append("reference sheet: crescendo hairpin")
        if t in ("decrescendo", "diminuendo") and r["hp"] != ["hairpin-close"]:
            errs.append(f"reference sheet: {t} hairpin")
    for o in d["orders"]:
        want = EXPECT_DYN_ORDER if o["k"] == "dyn" else EXPECT_TEMPO_ORDER
        if o["seq"] != want:
            errs.append(f"reference sheet: {o['k']} order {o['seq']}")
        if o["k"] == "dyn" and o["g"] != [f"{EXPECT_TERMS[next(x['term'] for x in D.values() if x['abbr'] == a)][3]:X}" for a in want.split(",")]:
            errs.append("reference sheet: dynamic order line shows the wrong symbols")
        if o["k"] == "tempo":
            shown = re.findall(r"[a-z]+", o["txt"].lower().replace("slowest to fastest", ""))
            if [s for s in shown if s in want.split(",")] != want.split(","):
                errs.append("reference sheet: tempo order line differs")
    # --- quiz: every question, exactly one correct answer, key equals it
    qs = {q["n"]: q for q in d["qs"]}
    keys = {k["n"]: k for k in d["keys"]}
    if sorted(qs) != list(range(1, NQ + 1)) or NQ != 10:
        errs.append(f"quiz has questions {sorted(qs)}, expected 1..10")
    if sorted(keys) != list(range(1, NQ + 1)):
        errs.append(f"key has questions {sorted(keys)}")
    meaning_by_abbr = {v[0]: v[1] for v in EXPECT_TERMS.values() if v[0]}
    meaning_by_term = {t: v[1] for t, v in EXPECT_TERMS.items()}

    def mean(w):
        return meaning_by_term.get(w) or meaning_by_abbr.get(w)
    points = 0
    for n, q in qs.items():
        k = keys.get(n)
        if not k:
            continue
        if q["type"] == "mc":
            kind, val = q["ask"].split(":", 1)
            good = []
            for o in q["opts"]:
                if kind in ("term", "hairpin"):
                    want = mean(val) if kind == "term" else meaning_by_term["crescendo"]
                    ok = o["val"] == want
                else:
                    ok = mean(o["val"]) == val
                if ok:
                    good.append(o["l"])
            if len(q["opts"]) != 4 or len(good) != 1:
                errs.append(f"quiz question {n}: {len(good)} correct options (must be exactly 1)")
            elif k["answer"] != good[0] or len(k["ok"]) != 1:
                errs.append(f"quiz question {n}: key says {k['answer']}, recomputed answer is {good}")
            if kind == "hairpin" and q["hp"] != ["hairpin-open"]:
                errs.append(f"quiz question {n}: symbol shown is not the opening hairpin")
            points += 1
        elif q["type"].startswith("match"):
            letters = {x["val"]: x["l"] for x in q["letters"]}
            if len(letters) != len(q["letters"]) or len(q["letters"]) != len(q["items"]) or len({mean(i["k"]) for i in q["items"]}) != len(q["items"]):
                errs.append(f"quiz question {n}: matching is not one-to-one with distinct meanings")
            kk = {x["k"]: x["a"] for x in k["items"]}
            for it in q["items"]:
                if kk.get(it["k"]) != letters.get(mean(it["k"])):
                    errs.append(f"quiz question {n}: key for {it['k']} is {kk.get(it['k'])}, recomputed {letters.get(mean(it['k']))}")
                if it["blanks"] != 1:
                    errs.append(f"quiz question {n}: {it['k']} has no answer line")
            points += len(q["items"])
        else:
            order = (EXPECT_DYN_ORDER if q["type"].endswith("dyn") else EXPECT_TEMPO_ORDER).split(",")
            if sorted(i["k"] for i in q["items"]) != sorted(order) or [i["k"] for i in q["items"]] == order:
                errs.append(f"quiz question {n}: items must be a shuffle of {order}")
            pos = {w: i + 1 for i, w in enumerate(order)}
            if k["seq"] != ",".join(order):
                errs.append(f"quiz question {n}: key order {k['seq']}")
            for it in k["items"]:
                if str(pos.get(it["k"])) != it["a"]:
                    errs.append(f"quiz question {n}: key position for {it['k']} is {it['a']}, expected {pos.get(it['k'])}")
            if len(k["items"]) != 6:
                errs.append(f"quiz question {n}: key lists {len(k['items'])} items")
            points += 1
    if points != QUIZ_POINTS or QUIZ_POINTS != 20:
        errs.append(f"quiz points add to {points}, expected 20")
    # shuffled dynamics: the asked order must be pp<p<mp<mf<f<ff in the key and unequal to the printed order
    # --- cross references
    pn = {p["kind"]: p["n"] for p in d["pages"]}
    for r in d["refs"]:
        if pn.get(r["kind"]) != r["n"]:
            errs.append(f"page {r['page']}: reference '{r['txt']}' points to {r['n']}, page is {pn.get(r['kind'])}")
        if r["kind2"] and pn.get(r["kind2"]) != r["n2"]:
            errs.append(f"page {r['page']}: reference '{r['txt']}' ends at {r['n2']}, page is {pn.get(r['kind2'])}")
    if len(d["pages"]) != TOTAL_PAGES:
        errs.append(f"resource has {len(d['pages'])} pages, expected {TOTAL_PAGES}")
    for p in d["pages"]:
        if p["name"] != PAGE_NAMES[p["kind"]]:
            errs.append(f"page {p['n']} name")
    # --- spelling and wording
    alltext = " ".join(d["pagetext"])
    low = alltext.lower()
    for w in SPELL:
        if w not in low:
            errs.append(f"spelling: '{w}' never appears")
    for bad in ("pianisimo", "fortisimo", "diminuendo,", "accelerando.", "acellerando", "ritardando ritardando", "crescendo crescendo", "diminuendo diminuendo"):
        if bad in low and bad not in ("diminuendo,", "accelerando."):
            errs.append(f"spelling: '{bad}'")
    for w in UK_SPELLINGS:
        if w in low:
            errs.append(f"non-US spelling: {w}")
    for w in QA_WORDS:
        if w.lower() in low.replace("q&a", ""):
            errs.append(f"internal wording on a page: {w}")
    if re.search(SEASONAL, low):
        errs.append("a seasonal word appears in the product")
    errs += count_claims(alltext, "pages")
    if DISCLOSURE not in alltext:
        errs.append("terms page lacks the disclosure line")
    for i, pg in enumerate(d["pagetext"]):
        if len(pg) < 60:
            errs.append(f"page {i + 1} looks blank")
    return errs


def pdf_fonts(path):
    out = subprocess.run(["pdffonts", path], capture_output=True, text=True, check=True).stdout.splitlines()[2:]
    return [(line.split()[0], line.split()[-5]) for line in out]


def load_json(name):
    return json.load(open(os.path.join(TPT, name)))


def verify_drawings(icons):
    """DOM boxes of every drawing + a rendered-pixel check of each reusable drawing alone on a transparent ground."""
    errs = []
    for ic in icons:
        pad = 1.5 * ic["sw"]
        if ic["x0"] < pad or ic["y0"] < pad or ic["x1"] > ic["w"] - pad or ic["y1"] > ic["h"] - pad:
            errs.append(f"page {ic['page']}: drawing {ic['icon']} comes closer than its stroke to the edge of its box ({ic['x0']:.0f},{ic['y0']:.0f},{ic['x1']:.0f},{ic['y1']:.0f} in {ic['w']}x{ic['h']})")
    from PIL import Image
    d = os.path.join(BUILD, "alone")
    os.makedirs(d, exist_ok=True)
    cells, ids = "", []
    seen = set()
    for kind, svg in ([(f"bars{i}", icon_bars(i)) for i in range(1, 7)] + [(f"gauge-{x['key']}", icon_gauge(x["gauge"], x["key"])) for x in TEMPO] +
                      [("dots-fast", icon_dots(True)), ("dots-slow", icon_dots(False)),
                       ("hairpin-open-big", hairpin(True, 560, 190, 10)), ("hairpin-close-big", hairpin(False, 560, 190, 10)),
                       ("hairpin-open-med", hairpin(True, 520, 150, 9)), ("hairpin-close-med", hairpin(False, 520, 150, 9)),
                       ("hairpin-open-ref", hairpin(True, 90, 32, 3)), ("hairpin-close-ref", hairpin(False, 90, 32, 3)),
                       ("hairpin-open-q", hairpin(True, 110, 40, 4))]):
        if kind in seen:
            continue
        seen.add(kind)
        ids.append(kind)
        svg = svg.replace('class="icon ', 'style="width:100%;height:100%;display:block" class="icon ', 1)
        vbm = re.search(r'viewBox="0 0 (\d+) (\d+)"', svg)
        w, h = int(vbm.group(1)), int(vbm.group(2))
        sc = 400 / max(w, h)
        cells += f'<div id="{kind}" style="width:{w * sc:.0f}px;height:{h * sc:.0f}px;margin:6px">{svg}</div>'
    for x in DYN:
        gid = f"glyph-{x['key']}"
        ids.append(gid)
        cells += (f'<div id="{gid}" style="width:340px;height:240px;margin:6px;display:flex;align-items:center;justify-content:center">'
                  f'<span class="bv" style="font-size:150pt">{chr(x["glyph"])}</span></div>')
        gid2 = f"glyph-small-{x['key']}"
        ids.append(gid2)
        cells += (f'<div id="{gid2}" style="width:64px;height:48px;margin:6px;display:flex;align-items:center;justify-content:center">'
                  f'<span class="bv" style="font-size:24pt">{chr(x["glyph"])}</span></div>')
    html = (f'<!doctype html><html><head><meta charset="utf-8"><style>{font_css()}{CSS}html,body{{background:transparent!important;margin:0}}'
            f'body{{display:flex;flex-wrap:wrap}}</style></head><body>{cells}</body></html>')
    write("alone.html", html)
    spec = os.path.join(BUILD, "alone.json")
    json.dump({"page": os.path.join(BUILD, "alone.html"), "ids": ids, "dir": d}, open(spec, "w"))
    js = os.path.join(BUILD, "alone.js")
    open(js, "w").write(ALONE_JS)
    r = subprocess.run(["node", js, spec], capture_output=True, text=True, env=node_env())
    if r.returncode != 0:
        return errs + [f"drawing render failed: {r.stderr[-300:]}"]
    for i in ids:
        im = Image.open(os.path.join(d, i + ".png")).convert("RGBA")
        a = im.getchannel("A").point(lambda v: 255 if v > 8 else 0)
        bb = a.getbbox()
        if not bb:
            errs.append(f"drawing {i}: renders nothing")
            continue
        w, h = im.size
        small = i.startswith("glyph-small")
        pad = 2 if small else (3 if "ref" in i or i.endswith("-q") else 8)
        if bb[0] < pad or bb[1] < pad or bb[2] > w - pad or bb[3] > h - pad:
            errs.append(f"drawing {i}: rendered pixels {bb} touch or come within {pad}px of the edge of its {w}x{h} image")
    return errs


def verify_poster_pixels():
    """Render the product PDF and check that every page keeps a clear margin (nothing printed within 0.3 in of the edge)."""
    errs = []
    from PIL import Image
    out = os.path.join(BUILD, "px")
    os.makedirs(out, exist_ok=True)
    subprocess.run(["pdftoppm", "-png", "-r", "80", PDF, os.path.join(out, "pg")], check=True)
    files = sorted(f for f in os.listdir(out) if f.startswith("pg") and f.endswith(".png"))
    for n, f in enumerate(files, 1):
        im = Image.open(os.path.join(out, f)).convert("L")
        w, h = im.size
        m = int(0.3 * 80)
        px = im.load()
        dark = 0
        for y in range(h):
            for x in list(range(0, m)) + list(range(w - m, w)):
                if px[x, y] < 200:
                    dark += 1
        for y in list(range(0, m)) + list(range(h - m, h)):
            for x in range(w):
                if px[x, y] < 200:
                    dark += 1
        if dark:
            errs.append(f"PDF page {n}: {dark} printed pixels within 0.3 in of the page edge")
    return errs


def verify_images():
    errs = []
    from PIL import Image
    for p in [COVER_PNG, *PREVIEW_PNGS]:
        im = Image.open(p).convert("L")
        name = os.path.basename(p)
        if im.size != (2000, 2000):
            errs.append(f"{name}: not 2000x2000")
            continue
        px = im.load()
        rows = [sum(1 for x in range(0, 2000, 8) if px[x, y] < 200) for y in range(0, 2000, 2)]
        ytop = 2000
        while ytop > 1000 and px[2, ytop - 1] < 40:
            ytop -= 1
        run = best = 0
        for y in range(120, ytop, 2):
            if rows[y // 2] == 0:
                run += 2
                best = max(best, run)
            else:
                run = 0
        if best > 200:
            errs.append(f"{name}: blank band of {best}px (more than 10% of the image)")
        last = max((y for y in range(0, ytop, 2) if rows[y // 2] > 0), default=0)
        if ytop - last > 200:
            errs.append(f"{name}: {ytop - last}px blank above the bottom band")
        e = 4
        dark = 0
        for y in range(0, ytop - 4):
            for x in list(range(0, e)) + list(range(2000 - e, 2000)):
                if px[x, y] < 235:
                    dark += 1
        for y in range(0, e):
            for x in range(2000):
                if px[x, y] < 235:
                    dark += 1
        if dark:
            errs.append(f"{name}: {dark} non-white pixels touch the top, left or right edge (art or text is clipped or too close)")
        for y in range(1996, 2000):
            if any(px[x, y] > 40 for x in range(2000)):
                errs.append(f"{name}: bottom edge row {y} is not solid black")
                break
        if name != "cover.png":
            gapdark = sum(1 for y in range(ytop - 14, ytop - 2) for x in range(0, 2000, 4) if px[x, y] < 200)
            if gapdark > 20:
                errs.append(f"{name}: page shots or art run into the black band (no clear gap above it)")
        cols = [x for x in range(2000) if any(px[x, y] < 235 for y in range(0, ytop - 4, 4))]
        if cols and (min(cols) < 40 or max(cols) > 1959):
            errs.append(f"{name}: content comes within 40px of the left or right edge ({min(cols)}..{max(cols)})")
        # even margins: left and right content margins differ by less than 60px
        if cols and abs(min(cols) - (1999 - max(cols))) > 60:
            errs.append(f"{name}: uneven side margins ({min(cols)} left, {1999 - max(cols)} right)")
    a = Image.open(os.path.join(ART, "hero.png")).getchannel("A").point(lambda v: 255 if v > 100 else 0)
    bb = a.getbbox()
    if not bb or bb[0] < 5 or bb[1] < 5 or bb[2] > a.width - 5 or bb[3] > a.height - 5:
        errs.append(f"art/hero.png: opaque pixels come within 5px of the image edge {bb}")
    return errs


def verify_files():
    errs = []
    from pypdf import PdfReader
    for p in [PDF, PREVIEW_PDF, COVER_PNG, *PREVIEW_PNGS, UPLOAD, TPT_JSON, os.path.join(TPT, "STYLE.md"), RENDER_JS, os.path.join(ART, "hero.png")]:
        if not os.path.exists(p):
            errs.append(f"missing {os.path.relpath(p, TPT)}")
    if errs:
        return errs
    for path, want in ((PDF, TOTAL_PAGES), (PREVIEW_PDF, 4)):
        rd = PdfReader(path)
        if len(rd.pages) != want:
            errs.append(f"{os.path.basename(path)}: {len(rd.pages)} pages, expected {want}")
        for i, pg in enumerate(rd.pages):
            w, h = float(pg.mediabox.width), float(pg.mediabox.height)
            if abs(w - 612) > 1 or abs(h - 792) > 1:
                errs.append(f"{os.path.basename(path)} p{i + 1}: {w:.0f}x{h:.0f}pt, not US Letter")
        fonts = pdf_fonts(path)
        for name, emb in fonts:
            if emb != "yes":
                errs.append(f"{os.path.basename(path)}: font {name} not embedded")
        names = " ".join(n for n, _ in fonts).lower().replace(" ", "")
        for fam in ("oswald", "sourcesans3", "bravura"):
            if fam not in names:
                errs.append(f"{os.path.basename(path)}: {fam} not found in PDF fonts")
    rd = PdfReader(PDF)
    for i, pg in enumerate(rd.pages):
        t = pg.extract_text() or ""
        if len(t.strip()) < 20:
            errs.append(f"PDF page {i + 1} looks blank")
        if "PREVIEW" in t.upper():
            errs.append(f"product PDF page {i + 1} carries a PREVIEW watermark")
    allpdf = " ".join((pg.extract_text() or "") for pg in rd.pages).replace("\n", " ")
    if f"{TOTAL_PAGES} pages" not in allpdf:
        errs.append("PDF never states its page count")
    prd = PdfReader(PREVIEW_PDF)
    want_pages = [SHOT_PAGES[k] for k in PREVIEW_ORDER]
    for i in range(4):
        t = prd.pages[i].extract_text() or ""
        if t.count("PREVIEW") != 1:
            errs.append(f"preview PDF page {i + 1}: expected exactly one PREVIEW watermark")
        if f"Page {want_pages[i]}" not in t.replace("\n", " "):
            errs.append(f"preview PDF page {i + 1} is not page {want_pages[i]} of the product")
    errs += verify_images()
    errs += verify_poster_pixels()
    for h in ("cover.html", "p1.html", "p2.html", "p3.html"):
        p = os.path.join(BUILD, h)
        if os.path.exists(p):
            s = open(p).read()
            txt = re.sub(r"<[^>]+>", " ", re.sub(r"<style>.*?</style>", "", s, flags=re.S))
            errs += count_claims(txt, h)
            if "swm" in s or "PREVIEW" in s:
                errs.append(f"{h}: has its own watermark layer (the page shots already carry one)")
            if "_art" in s:
                errs.append(f"{h}: references tpt/_art")
            for m in re.finditer(r'<div class="lbl"[^>]*>([^<]*)<span>', s):
                if m.group(1) not in PAGE_NAMES.values():
                    errs.append(f"{h}: label '{m.group(1)}' is not a real page name")
            if h != "cover.html":
                for m in re.finditer(r'src="(shot-[a-z0-9]+\.png)"', s):
                    if not os.path.exists(os.path.join(BUILD, m.group(1))):
                        errs.append(f"{h}: missing {m.group(1)}")
    # the grid preview shows all posters
    p1 = open(os.path.join(BUILD, "p1.html")).read()
    if len(re.findall(r'src="shot-poster\d+\.png"', p1)) != NPOST:
        errs.append(f"preview-1 does not show all {NPOST} posters")
    cov = open(os.path.join(BUILD, "cover.html")).read()
    if f"{TOTAL_PAGES} pages" not in cov or f"{NPOST} posters" not in cov:
        errs.append("cover band disagrees with the PDF")
    up = open(UPLOAD).read()
    m = re.search(r"^## 1\. Title\s*\n+```\n(.+?)\n```", up, re.M | re.S)
    if not m:
        errs.append("UPLOAD.md: title block not found")
    else:
        title = m.group(1).strip()
        if len(title) > 80:
            errs.append(f"UPLOAD.md: title is {len(title)} chars (max 80)")
        if re.search(SEASONAL, title, re.I):
            errs.append("UPLOAD.md: seasonal word in the title")
    for need in (DISCLOSURE, f"${PRICE}", f"{TOTAL_PAGES} pages", f"{NPOST} printable", f"{NQ} questions worth {QUIZ_POINTS} points"):
        if need not in up:
            errs.append(f"UPLOAD.md: missing '{need}'")
    errs += count_claims(up.split("## 3. Grades")[0].split("## 1. Title")[1], "UPLOAD.md")
    sec = up.split("## 5. Page count by section")[1].split("##")[0]
    nums = [int(x) for x in re.findall(r"^- (?!Total)[^\n]*: (\d+)$", sec, re.M)]
    if sum(nums) != TOTAL_PAGES:
        errs.append(f"UPLOAD.md page list sums to {sum(nums)}, PDF has {TOTAL_PAGES}")
    desc = up.split("## 2. Description")[1].split("## 3.")[0]
    bullets = [int(x) for x in re.findall(r"\((?:[^()]*? )?(\d+) pages?\)(?=\s*(?:: |$|\n))", desc, re.M)]
    bullets = [int(x) for x in re.findall(r"\((\d+) pages?\)\s*(?:: [^\n]*)?$", desc, re.M)] or bullets
    lines = [l for l in desc.splitlines() if l.startswith("• ") and re.search(r"\((?:[^()]*? )?(\d+) pages?\)", l)]
    tot = 0
    for l in lines:
        tot += int(re.findall(r"\((?:[^()]*? )?(\d+) pages?\)", l)[-1])
    if tot != TOTAL_PAGES:
        errs.append(f"UPLOAD.md description bullets sum to {tot} pages, PDF has {TOTAL_PAGES}")
    if re.search("|".join(QA_WORDS), up.replace("Q&A", ""), re.I):
        errs.append("UPLOAD.md: forbidden claim or internal QA wording")
    for w in UK_SPELLINGS:
        if w in desc.lower():
            errs.append(f"UPLOAD.md: non-US spelling {w}")
    for t in EXPECT_TERMS:
        pass
    tj = json.load(open(TPT_JSON))
    tags, subs = set(load_json("TAG-OPTIONS.json")["options"]), set(load_json("SUBJECT-OPTIONS.json"))
    if not 1 <= len(tj["tags"]) <= 6 or any(t not in tags for t in tj["tags"]):
        errs.append(f"tpt.json tags invalid: {tj['tags']}")
    if not 1 <= len(tj["subjects"]) <= 3 or any(s not in subs for s in tj["subjects"]):
        errs.append(f"tpt.json subjects invalid: {tj['subjects']}")
    if not 1 <= len(tj["grades"]) <= 4:
        errs.append("tpt.json grades must be 1-4")
    if tj.get("pages") != TOTAL_PAGES:
        errs.append(f"tpt.json pages {tj.get('pages')} != {TOTAL_PAGES}")
    if tj["price"] != PRICE:
        errs.append("tpt.json price mismatch")
    return errs


def check():
    files = [os.path.join(BUILD, "resource.html"), os.path.join(BUILD, "shots.html")]
    if not all(os.path.exists(x) for x in files):
        sys.exit("build html missing: run gen.py first")
    data = inspect_html(files)
    res, shots = data["resource.html"], data["shots.html"]
    errs = verify_content(res)
    errs += verify_drawings(res["icons"])
    errs += ["resource: " + e for e in res["layout"]] + ["shots: " + e for e in shots["layout"]]
    for p in shots["pages"]:
        if p["kind"] != "cover" and p["wms"] != 1:
            errs.append(f"shots: page {p['n']} has {p['wms']} watermarks, expected 1")
    for p in res["pages"]:
        if p["wms"] != 0:
            errs.append(f"resource: page {p['n']} has a watermark")
    for k in PREVIEW_ORDER:
        n = SHOT_PAGES[k]
        gap = res["gaps"][n - 1]
        if gap > 105:
            errs.append(f"preview page {k} (page {n}): {gap}px blank above the footer (max 105)")
    errs += verify_files()
    if errs:
        print("CHECK FAILED")
        print("\n".join(" - " + e for e in errs[:80]))
        sys.exit(1)
    print(f"CHECK OK: {NPOST} posters (term, abbreviation, meaning, BPM, symbol and order read back against a second table), dynamic order pp<p<mp<mf<f<ff and "
          f"tempo order largo<...<presto in posters, reference sheet, quiz and key; {NQ} quiz questions / {QUIZ_POINTS} points, each with exactly one correct answer equal to the key; "
          f"drawings inside their boxes and clear of image edges (rendered-pixel check); no clipped text, 0.3 in clear margin on every PDF page; "
          f"PDF {TOTAL_PAGES} Letter pages, preview 4 (one watermark each), fonts embedded; cover and previews 2000x2000 with clear edges; UPLOAD.md and tpt.json agree.")


if __name__ == "__main__":
    if "--check" in sys.argv:
        check()
    else:
        build()
