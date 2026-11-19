#!/usr/bin/env python3
"""Winter Note Speller (TpT 060): build the resource and verify it.

    python3 gen.py           build everything (PDFs, PNGs, UPLOAD.md, tpt.json) into this folder
    python3 gen.py --check   re-read the rendered pages and verify every worksheet item, key entry, riddle, drawing and the layout

--check does not trust the tables in this file. It parses the drawn staves (staff lines, clef glyph, notehead centres, ledger
lines, stems) from the rendered HTML, recomputes every note letter from that geometry alone, and compares the spelled words
with the answer keys, with a second separately typed word table (EXPECT_*) and with the riddle clues.
Rendering uses Playwright + Chromium (HTML/SVG -> PDF/PNG) with the OFL fonts in ../fonts (Bravura for notation).
"""
import json
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

SLUG = "winter-note-speller"
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
TITLE = "Winter Note Speller"
LISTING_TITLE = "Note Naming Worksheets: Spell the Word, Treble & Bass Clef, Riddles, Gr 3-6"
PRICE = "3.50"
TAGS = ["Worksheets", "Printables", "Activities", "Games", "Handouts", "Winter"]
SUBJECTS = ["Music", "Instrumental Music"]
GRADES = ["3rd-grade", "4th-grade", "5th-grade", "6th-grade"]

# ------------------------------------------------------------------ content tables
AG = "ABCDEFG"
# Word pools (3 to 7 letters, only the letters A-G). Level A and level B each hold two pages of eight words; both clefs use the pool.
POOL = {
    "A": ["BAD", "BEG", "DAD", "FED", "ADD", "FAD", "GAB", "EDGE",
          "AGED", "DEED", "BEEF", "FADED", "FACED", "ADDED", "DECADE", "BEADED"],
    "B": ["AGE", "DAB", "EBB", "BEE", "CAB", "CAGE", "BABE", "ACED",
          "BADE", "ADAGE", "EBBED", "DECAF", "FACADE", "BEGGED", "BAGGED", "GABBED"],
}
# Letter -> allowed staff steps. Step 0 is the bottom line, each step is half a staff space (line, space, line ...).
OPTS = {
    ("treble", "A"): {"A": [3], "B": [4], "C": [5], "D": [6], "E": [0, 7], "F": [1, 8], "G": [2]},
    ("treble", "B"): {"A": [-4, 3, 10], "B": [-3, 4], "C": [-2, 5], "D": [-1, 6], "E": [0, 7], "F": [1, 8], "G": [2, 9]},
    ("bass", "A"): {"A": [1, 8], "B": [2], "C": [3], "D": [4], "E": [5], "F": [6], "G": [0, 7]},
    ("bass", "B"): {"A": [1, 8], "B": [2, 9], "C": [3, 10], "D": [-3, 4, 11], "E": [-2, 5], "F": [-1, 6], "G": [0, 7]},
}
BASE = {"treble": 4, "bass": 6}        # index in "ABCDEFG" of the bottom line: E for treble, G for bass
CLEF_NAME = {"treble": "Treble clef", "bass": "Bass clef"}
CLEF_GLYPH = {"treble": 0xE050, "bass": 0xE062}
GLYPH_CLEF = {v: k for k, v in CLEF_GLYPH.items()}
CLEF_STEP = {"treble": 2, "bass": 6}   # staff step the clef glyph's origin sits on (G line, F line)
HEAD_GLYPH = 0xE0A4
HEAD_W = 1.18
PER_PAGE = 8


def letter_at(clef, step):
    return AG[(BASE[clef] + step) % 7]


def needs_ledger(step):
    return step <= -2 or step >= 10


def pick_steps(clef, level, word, tag=""):
    rng = random.Random(f"{clef}|{level}|{word}|{tag}")
    opts = OPTS[(clef, level)]
    for _ in range(500):
        st = [rng.choice(opts[c]) for c in word]
        if level == "A" or any(needs_ledger(s) for s in st):
            for s, c in zip(st, word):
                assert letter_at(clef, s) == c
            return st
    raise SystemExit(f"cannot place {word} for {clef} {level}")


# worksheet sets: id, clef, level, set number
SETS = []
for _clef, _cp in (("treble", "T"), ("bass", "B")):
    for _lv in ("A", "B"):
        for _n in (1, 2):
            _words = POOL[_lv][(_n - 1) * PER_PAGE:_n * PER_PAGE]
            if _clef == "bass":
                _words = _words[::-1]
            SETS.append(dict(id=f"{_cp}-{_lv}{_n}", clef=_clef, level=_lv, n=_n, words=_words))
for _s in SETS:
    _s["steps"] = [pick_steps(_s["clef"], _s["level"], w, "ws") for w in _s["words"]]

# riddles: answer, clef, level, clue, token (a phrase that only this clue holds), gloss (shown in the key)
RIDDLES = [
    dict(set=1, clef="treble", level="A", answer="FACE", token="carrot nose", gloss="the part of his head with the eyes and the nose",
         clue="A snowman has two coal eyes and a carrot nose on this part of his head."),
    dict(set=1, clef="treble", level="A", answer="FEED", token="scatter seeds", gloss="to give food to hungry birds, such as by scattering seeds",
         clue="Birds cannot find food under the snow, so you scatter seeds outside to do this for them."),
    dict(set=1, clef="treble", level="A", answer="EGG", token="hen lays", gloss="a hen lays it; scramble or boil it",
         clue="A hen lays one of these. You can scramble it or boil it for a warm breakfast."),
    dict(set=1, clef="treble", level="A", answer="BED", token="warm quilt", gloss="where you sleep under a quilt",
         clue="You curl up under a warm quilt in this on a cold winter night."),
    dict(set=2, clef="bass", level="A", answer="BAG", token="handle or a strap", gloss="carries hat, mittens, boots",
         clue="You pack your hat, mittens and boots in this and carry it to school. It has a handle or a strap."),
    dict(set=2, clef="bass", level="A", answer="CAFE", token="hot cocoa", gloss="a shop for cocoa and muffins",
         clue="A small shop where you can sip hot cocoa and eat a warm muffin. Write it without the accent mark."),
    dict(set=2, clef="bass", level="A", answer="ACE", token="highest card", gloss="the highest card, one big symbol",
         clue="In many card games this is the highest card, and it shows just one big symbol."),
    dict(set=2, clef="bass", level="A", answer="FADE", token="weaker and dimmer", gloss="daylight slowly dims",
         clue="On a winter afternoon the daylight begins to do this: it slowly gets weaker and dimmer."),
    dict(set=3, clef="treble", level="B", answer="BEAD", token="small round piece", gloss="strung on thread for an ornament",
         clue="You string this small round piece onto a thread to make a snowflake ornament."),
    dict(set=3, clef="bass", level="B", answer="BADGE", token="pin or patch", gloss="a pin you earn",
         clue="A small pin or patch that shows you earned something, such as for finishing ski school."),
    dict(set=3, clef="treble", level="B", answer="CABBAGE", token="tightly packed leaves", gloss="a round, leafy winter vegetable",
         clue="A round green vegetable with tightly packed leaves. It keeps well all winter and goes into soup."),
    dict(set=3, clef="bass", level="B", answer="BAGGAGE", token="suitcases", gloss="the suitcases and bags on a trip",
         clue="The suitcases and bags you take with you on a trip."),
]
for _i, _r in enumerate(RIDDLES, 1):
    _r["n"] = _i
    _r["steps"] = pick_steps(_r["clef"], _r["level"], _r["answer"], "riddle")
NRID = len(RIDDLES)
RIDDLE_SETS = [1, 2, 3]

# spell-it page: students draw the notes; the key shows one correct set
SPELL = [("treble", "FEE"), ("treble", "GAFFE"), ("treble", "EGGED"), ("treble", "DECADE"),
         ("bass", "CAGED"), ("bass", "DEFACE"), ("bass", "EFFACE"), ("bass", "CEDE")]
SPELL_STEPS = [pick_steps(c, "A", w, "spell") for c, w in SPELL]
OWN_ROWS = [("treble", 4), ("bass", 4)]

NWORDS = sum(len(s["words"]) for s in SETS)         # 64
NSPELL = len(SPELL)
NOWN = sum(n for _, n in OWN_ROWS)

# ------------------------------------------------------------------ page map
PAGE_ORDER = (["cover", "teacher", "ref"] + ["ws-" + s["id"] for s in SETS] + [f"riddle{n}" for n in (1, 2, 3)] +
              ["own", "spell", "keyT", "keyB", "keyR", "terms"])
PAGEOF = {k: i + 1 for i, k in enumerate(PAGE_ORDER)}
TOTAL_PAGES = len(PAGE_ORDER)
PAGE_NAMES = {"cover": "Cover", "teacher": "Teacher Notes", "ref": "Note Letter Reference", "own": "Write Your Own Word",
              "spell": "Spell It with Notes", "keyT": "Answer Key: Treble Clef", "keyB": "Answer Key: Bass Clef",
              "keyR": "Answer Key: Riddles and Spell It", "terms": "Terms of Use"}
for _s in SETS:
    PAGE_NAMES["ws-" + _s["id"]] = f"{CLEF_NAME[_s['clef']]}, Level {_s['level']}: Set {_s['n']}"
for _n in RIDDLE_SETS:
    PAGE_NAMES[f"riddle{_n}"] = f"Winter Riddles: Set {_n}"
KEY_OF = {"treble": "keyT", "bass": "keyB"}
SECTION_PAGES = [("Cover", 1), ("Teacher notes", 1), ("Note letter reference sheet", 1),
                 ("Treble clef worksheets, Level A and Level B", 4), ("Bass clef worksheets, Level A and Level B", 4),
                 ("Winter riddles", 3), ("Write your own word", 1), ("Spell it with notes", 1), ("Answer keys", 3),
                 ("Terms of use and credits", 1)]
assert sum(c for _, c in SECTION_PAGES) == TOTAL_PAGES


def R(kind, cap=False):
    return f'<span data-ref="{kind}" data-n="{PAGEOF[kind]}">{"Page" if cap else "page"} {PAGEOF[kind]}</span>'


def RR(k1, k2, cap=False):
    return (f'<span data-ref="{k1}" data-n="{PAGEOF[k1]}" data-ref2="{k2}" data-n2="{PAGEOF[k2]}">'
            f'{"Pages" if cap else "pages"} {PAGEOF[k1]}–{PAGEOF[k2]}</span>')


# ------------------------------------------------------------------ notation drawing (pt units)
TOPM, BOTM = 2.9, 3.0          # space above the top line and below the bottom line, in staff spaces


def fx(v):
    return f"{v:.2f}"


def g(cp, x, y, size, cls="", fill="#000"):
    c = f' class="{cls}"' if cls else ""
    return f'<text{c} x="{fx(x)}" y="{fx(y)}" font-family="Bravura" font-size="{fx(size)}" fill="{fill}">&#x{cp:X};</text>'


def stem_len(step, S):
    return max(3.5 * S, abs(step - 4) / 2 * S)


def note_svg(step, cx, S, top):
    bottom = top + 4 * S
    y = bottom - step * S / 2
    hw = HEAD_W * S
    left = cx - hw / 2
    out = ['<g class="nt">']
    ext = 0.4 * S
    leds = list(range(-2, step - 1, -2)) if step < 0 else []
    leds += list(range(10, step + 1, 2)) if step > 8 else []
    for e in leds:
        ly = bottom - e * S / 2
        out.append(f'<line class="led" x1="{fx(left - ext)}" y1="{fx(ly)}" x2="{fx(left + hw + ext)}" y2="{fx(ly)}" '
                   f'stroke="#000" stroke-width="{fx(0.16 * S)}"/>')
    out.append(g(HEAD_GLYPH, left, y, 4 * S, "head"))
    sw = 0.13 * S
    L = stem_len(step, S)
    if step < 4:       # stem up, on the right of the head
        sx = left + hw - sw / 2
        out.append(f'<line class="stem" data-dir="up" x1="{fx(sx)}" y1="{fx(y - 0.168 * S)}" x2="{fx(sx)}" y2="{fx(y - 0.168 * S - L)}" '
                   f'stroke="#000" stroke-width="{fx(sw)}"/>')
    else:              # stem down, on the left of the head
        sx = left + sw / 2
        out.append(f'<line class="stem" data-dir="down" x1="{fx(sx)}" y1="{fx(y + 0.168 * S)}" x2="{fx(sx)}" y2="{fx(y + 0.168 * S + L)}" '
                   f'stroke="#000" stroke-width="{fx(sw)}"/>')
    out.append("</g>")
    return "".join(out)


def staff_svg(clef, steps, ctx, w, S, spacing=None, labels=False, sub=None):
    """One staff with a clef and a row of quarter notes. labels: draw the letter under each note (computed from the steps)."""
    top = TOPM * S
    base_h = top + 4 * S + BOTM * S
    h = base_h
    if labels:
        h = base_h + 1.9 * S + 5 + (1.5 * S if sub else 0)
    out = [f'<svg class="ns" data-ctx="{ctx}" data-s="{S}" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {fx(w)} {fx(h)}" '
           f'width="{fx(w)}pt" height="{fx(h)}pt" style="display:block">']
    for k in range(5):
        y = top + k * S
        out.append(f'<line class="sl" x1="2.00" y1="{fx(y)}" x2="{fx(w - 2)}" y2="{fx(y)}" stroke="#000" stroke-width="{fx(0.13 * S)}"/>')
    out.append(f'<line class="bar" x1="{fx(w - 3)}" y1="{fx(top)}" x2="{fx(w - 3)}" y2="{fx(top + 4 * S)}" stroke="#000" stroke-width="{fx(0.2 * S)}"/>')
    bottom = top + 4 * S
    out.append(g(CLEF_GLYPH[clef], 3.0, bottom - CLEF_STEP[clef] * S / 2, 4 * S, "clef"))
    x_start = 3 + 3.2 * S + 12
    sp = spacing or 6 * S
    x0 = x_start + sp / 2
    for i, st in enumerate(steps):
        cx = x0 + sp * i
        out.append(note_svg(st, cx, S, top))
        if labels:
            out.append(f'<text class="rl" x="{fx(cx)}" y="{fx(base_h + 1.9 * S)}" text-anchor="middle" font-family="Oswald" font-weight="700" '
                       f'font-size="{fx(S * 1.9)}" fill="#000">{letter_at(clef, st)}</text>')
            if sub and sub.get(i):
                out.append(f'<text class="rs" x="{fx(cx)}" y="{fx(h - 3)}" text-anchor="middle" font-family="Oswald" font-weight="500" '
                           f'font-size="{fx(S * 1.25)}" fill="{ACCENT}">{sub[i]}</text>')
    out.append("</svg>")
    return "".join(out)


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


ROWH, ROWGAP, RIDH, SPH = 64.0, 4.0, 137.0, 62.0
CSS = """
@page { size: 8.5in 11in; margin: 0; }
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; background: #fff; color: #000; }
body { font-family: 'Source Sans 3', sans-serif; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
.page { width: 8.5in; height: 11in; position: relative; overflow: hidden; page-break-after: always; break-after: page;
        padding: 0.42in 0.5in 0.38in; display: flex; flex-direction: column; }
.page:last-child { page-break-after: auto; break-after: auto; }
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
.how { font-size: 11pt; line-height: 1.32; margin: 0 0 8pt; }
.foot { display: flex; justify-content: space-between; font-size: 8.5pt; color: #333; border-top: .8pt solid #000; padding-top: 3pt; margin-top: auto; }
.wm { position: absolute; left: 50%; top: 50%; transform: translate(-50%, -50%) rotate(-38deg); font-family: 'Oswald'; font-weight: 700;
      font-size: 150pt; color: rgba(0,0,0,.13); letter-spacing: .06em; white-space: nowrap; pointer-events: none; z-index: 9; }
.fill { flex: 1; }
.doc h1 { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 30pt; margin: 0 0 4pt; line-height: 1; }
.doc h2 { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 12.5pt; margin: 8pt 0 3pt; letter-spacing: .02em; }
.doc p, .doc li { font-size: 10.3pt; line-height: 1.32; margin: 0 0 4pt; }
.doc ul, .doc ol { margin: 0 0 3pt; padding-left: 16pt; }
.doc .rule { border-bottom: 2.2pt solid #000; margin-bottom: 8pt; padding-bottom: 6pt; }
.doc .cols { display: flex; gap: 20pt; }
.doc .cols > div { flex: 1; min-width: 0; }
.small { font-size: 9.5pt !important; color: #333; }
.num { font-style: normal; font-family: 'Oswald'; font-weight: 700; font-size: 15pt; color: ACCENT; flex: 0 0 20pt; text-align: right; }
.rows { display: flex; flex-direction: column; gap: ROWGAPpt; }
.wrow { display: flex; align-items: center; gap: 10pt; height: ROWHpt; border-bottom: .6pt solid #bbb; }
.wd { flex: 1; display: flex; align-items: flex-end; gap: 5pt; font-family: 'Oswald'; font-weight: 300; font-size: 11pt; height: 24pt; }
.wd b { flex: 1; border-bottom: 1.2pt solid #000; height: 18pt; }
.rid { border: 1.3pt solid #000; border-radius: 8pt; padding: 7pt 12pt 6pt; display: flex; flex-direction: column; justify-content: space-between; height: RIDHpt; }
.rid .rt { display: flex; gap: 10pt; align-items: flex-start; }
.rid .rt p { margin: 0; font-size: 12pt; line-height: 1.28; font-weight: 600; flex: 1; }
.rid .rt .cl { font-family: 'Oswald'; font-weight: 500; text-transform: uppercase; font-size: 9.5pt; letter-spacing: .06em; background: TINT; border-radius: 4pt; padding: 2pt 6pt 3pt; flex: 0 0 auto; margin-top: 2pt; }
.rid .rb { display: flex; align-items: center; gap: 12pt; }
.sp { display: flex; align-items: center; gap: 10pt; height: SPHpt; border-bottom: .6pt solid #bbb; }
.sp .w { flex: 0 0 1.25in; font-family: 'Oswald'; font-weight: 700; font-size: 23pt; letter-spacing: .08em; }
.sp .w small { display: block; font-weight: 300; font-size: 9.5pt; letter-spacing: .02em; }
.own { display: flex; align-items: center; gap: 10pt; height: SPHpt; border-bottom: .6pt solid #bbb; }
.own .wd { flex: 0 0 1.5in; }
.rb2 { display: flex; gap: 12pt; }
.rb2 > div { flex: 1; min-width: 0; }
.cap { font-family: 'Oswald'; font-weight: 500; text-transform: uppercase; font-size: 10.5pt; letter-spacing: .05em; margin: 2pt 0 0; }
.cap span { font-weight: 300; text-transform: none; letter-spacing: 0; font-size: 10.5pt; margin-left: 4pt; }
.cl2 { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 17pt; margin: 6pt 0 0; letter-spacing: .02em; }
.cl2 span { font-weight: 300; text-transform: none; font-size: 11.5pt; margin-left: 8pt; letter-spacing: 0; }
.tip { border: 1.3pt solid #000; border-radius: 8pt; padding: 6pt 12pt; font-size: 10.6pt; line-height: 1.32; }
.tip b { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; letter-spacing: .03em; }
.tip p { margin: 0 0 3pt; }
.tips { display: flex; gap: 12pt; }
.tips > .tip { flex: 1; }
.kblk { margin: 0 0 10pt; }
.kblk .kt { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 12pt; border-bottom: 1.2pt solid #000; padding-bottom: 2pt; margin-bottom: 4pt; display: flex; justify-content: space-between; gap: 10pt; }
.kblk .kt span { font-weight: 300; text-transform: none; font-size: 10.5pt; }
.kgrid { display: grid; grid-template-columns: 1fr 1fr; gap: 0 22pt; }
.kit { display: flex; align-items: baseline; gap: 8pt; padding: 3pt 4pt; border-bottom: .5pt solid #bbb; }
.kit i { font-style: normal; font-family: 'Oswald'; font-weight: 300; font-size: 10pt; width: 14pt; text-align: right; }
.kit b { font-family: 'Oswald'; font-weight: 700; font-size: 15pt; letter-spacing: .06em; color: ACCENT; flex: 0 0 1.1in; }
.kit span { font-size: 10pt; color: #333; }
.rkey .kit b { flex: 0 0 0.9in; }
.skgrid { display: grid; grid-template-columns: 1fr 1fr; gap: 6pt 18pt; }
.sk { border: 1pt solid #000; border-radius: 6pt; padding: 3pt 6pt 2pt; }
.sk .skh { font-family: 'Oswald'; font-weight: 700; font-size: 11pt; letter-spacing: .06em; color: ACCENT; }
.sk .skh span { font-weight: 300; color: #000; font-size: 9.5pt; letter-spacing: 0; margin-left: 6pt; }
.cover { align-items: center; justify-content: space-between; padding: 0.55in 0.6in 0.5in; }
.store { font-family: 'Oswald'; font-weight: 500; font-size: 13pt; letter-spacing: .32em; text-transform: uppercase; }
.ctitle { text-align: center; }
.ctitle .a { font-family: 'Oswald'; font-weight: 700; font-size: 50pt; line-height: 1; letter-spacing: .02em; }
.ctitle .b { font-family: 'Oswald'; font-weight: 700; white-space: nowrap; font-size: 80pt; line-height: .95; letter-spacing: .01em; }
.ctitle .c { font-family: 'Oswald'; font-weight: 300; font-size: 17pt; margin-top: 8pt; }
.cband { width: 100%; background: #000; color: #fff; text-align: center; font-family: 'Oswald'; font-weight: 500; font-size: 14pt;
         letter-spacing: .08em; text-transform: uppercase; padding: 8pt 0 9pt; border-radius: 4pt; }
.cband em { font-style: normal; color: #8FC3EC; }
"""
CSS = (CSS.replace("ACCENT", ACCENT).replace("TINT", TINT).replace("ROWHpt", f"{ROWH}pt").replace("ROWGAPpt", f"{ROWGAP}pt")
       .replace("RIDHpt", f"{RIDH}pt").replace("SPHpt", f"{SPH}pt"))


def html_doc(pages, title="doc"):
    return (f'<!doctype html><html><head><meta charset="utf-8"><title>{escape(title)}</title>'
            f'<style>{font_css()}{CSS}</style></head><body>{"".join(pages)}</body></html>')


COPY = f"© {YEAR} {STORE} · {BRAND} · For single-classroom use"


def foot(right):
    return f'<div class="foot"><span>{COPY}</span><span>{right}</span></div>'


def page(kind, inner, wm=False, cls="", right=None):
    n = PAGEOF[kind]
    w = '<div class="wm">PREVIEW</div>' if wm else ""
    rt = right if right else f"Page {n}"
    return (f'<section class="page {cls}" data-page="{n}" data-kind="{kind}" data-name="{escape(PAGE_NAMES[kind])}">{w}{inner}'
            f'{foot(rt)}</section>')


def top(title, sub, tag, tagline, cls=""):
    return (f'<div class="top blk"><div class="h t">{title}<small>{sub}</small></div>'
            f'<div class="tag {cls}"><div class="lv">{tag}</div><div class="ln">{tagline}</div></div></div>')


def namebar():
    return '<div class="name blk">Name<span></span>Date<span class="s"></span></div>'


# ------------------------------------------------------------------ pages
WS_S, WS_W = 6.2, 352.0       # staff space and width of a worksheet staff, pt


def ws_page(s, wm=False):
    sid = s["id"]
    kind = "ws-" + sid
    lv = s["level"]
    how = ("Read each note and name it by its letter. Write the letters as a word on the line. Every word uses only the letters A to G."
           if lv == "A" else
           "Some notes sit above or below the staff, and some need ledger lines. Name each note, then write the word on the line. "
           "Every word uses only the letters A to G.")
    rows = ""
    for i, st in enumerate(s["steps"], 1):
        svg = staff_svg(s["clef"], st, "ws:%s:%d" % (sid, i), WS_W, WS_S, spacing=40)
        rows += (f'<div class="wrow blk" data-ws="{sid}" data-item="{i}"><i class="num">{i}</i>{svg}'
                 f'<div class="wd">Word<b></b></div></div>')
    inner = (top(TITLE, f'{CLEF_NAME[s["clef"]]} · Spell the Word · Set {s["n"]} of 2', f"LEVEL {lv}",
                 "Notes inside the staff" if lv == "A" else "Ledger lines")
             + namebar() + f'<div class="how blk">{how}</div><div class="rows">{rows}</div>')
    return page(kind, inner, wm, "ws", right=f'Page {PAGEOF[kind]} · Answer key on {R(KEY_OF[s["clef"]])}')


def riddle_page(setn, wm=False):
    kind = f"riddle{setn}"
    rs = [r for r in RIDDLES if r["set"] == setn]
    sub = {1: "Treble clef · Level A", 2: "Bass clef · Level A", 3: "Treble and bass clef · Level B"}[setn]
    box = ""
    for r in rs:
        svg = staff_svg(r["clef"], r["steps"], "rid:%d" % r["n"], 340.0, 6.6, spacing=40)
        box += (f'<div class="rid blk" data-riddle="{r["n"]}"><div class="rt"><i class="num">{r["n"]}</i><p>{escape(r["clue"])}</p>'
                f'<div class="cl">{CLEF_NAME[r["clef"]]}</div></div>'
                f'<div class="rb">{svg}<div class="wd">Answer<b></b></div></div></div>')
    how = ("Read the clue. Then read the notes and write the word they spell. The word should answer the riddle, so if it does not fit, "
           "read the notes again. Every answer uses only the letters A to G.")
    inner = (top("Winter Riddles", sub, f"SET {setn}", "Read, spell, solve")
             + namebar() + f'<div class="how blk">{how}</div><div class="rows" style="gap:9pt">{box}</div>')
    return page(kind, inner, wm, "ws", right=f'Page {PAGEOF[kind]} · Answer key on {R("keyR")}')


def own_page(wm=False):
    rows = ""
    k = 0
    for clef, n in OWN_ROWS:
        for _ in range(n):
            k += 1
            svg = staff_svg(clef, [], "own:%d:%s" % (k, clef), 300.0, WS_S, spacing=40)
            rows += (f'<div class="own blk" data-own="{k}"><i class="num">{k}</i>'
                     f'<div class="wd">My word<b></b></div>{svg}</div>')
    how = ("Think of a word that uses only the letters A to G, such as BAG, CAGE or FACED. Write it on the line, then draw one note on the staff "
           "for each letter. Trade papers with a partner. Can your partner read your word?")
    inner = (top(TITLE, "Treble and bass clef · Write Your Own Word", "YOUR TURN", "Blank staves")
             + namebar() + f'<div class="how blk">{how}</div><div class="rows" style="gap:4pt">{rows}</div>')
    return page("own", inner, wm, "ws")


def spell_page(wm=False):
    rows = ""
    for i, (clef, w) in enumerate(SPELL, 1):
        svg = staff_svg(clef, [], "spell:%d:%s" % (i, clef), 350.0, WS_S, spacing=40)
        rows += (f'<div class="sp blk" data-spell="{i}" data-word="{w}"><i class="num">{i}</i>'
                 f'<div class="w">{w}<small>{CLEF_NAME[clef]}</small></div>{svg}</div>')
    how = ("Spell each word with notes. Draw one quarter note for every letter: a filled notehead with a stem. The stem points up for a note below "
           "the middle line and down for a note on or above it. Any correct place for a letter is fine, so read your notes back to check them.")
    inner = (top(TITLE, "Treble and bass clef · Spell It with Notes", "YOUR TURN", "Draw the notes")
             + namebar() + f'<div class="how blk">{how}</div><div class="rows" style="gap:4pt">{rows}</div>')
    return page("spell", inner, wm, "ws", right=f'Page {PAGEOF["spell"]} · Answer key on {R("keyR")}')


REF = {
    "treble": dict(lines=[0, 2, 4, 6, 8], spaces=[1, 3, 5, 7], outside=[-4, -3, -2, -1, 9, 10],
                   sub={2: "middle C"}, mn="Every Good Boy Does Fine", sp="F A C E spells FACE"),
    "bass": dict(lines=[0, 2, 4, 6, 8], spaces=[1, 3, 5, 7], outside=[-3, -2, 9, 10, 11],
                 sub={3: "middle C"}, mn="Good Boys Do Fine Always", sp="All Cows Eat Grass"),
}
REF_S = 6.6


def ref_page(wm=False):
    blocks = ""
    for clef in ("treble", "bass"):
        d = REF[clef]
        a = staff_svg(clef, d["lines"], f"ref:{clef}:lines", 254.0, REF_S, spacing=36, labels=True)
        b = staff_svg(clef, d["spaces"], f"ref:{clef}:spaces", 254.0, REF_S, spacing=36, labels=True)
        c = staff_svg(clef, d["outside"], f"ref:{clef}:outside", 520.0, REF_S, spacing=52, labels=True, sub=d["sub"])
        blocks += (f'<div class="blk"><div class="cl2">{CLEF_NAME[clef]}<span>Lines: {d["mn"]}. Spaces: {d["sp"]}.</span></div>'
                   f'<div class="rb2"><div><div class="cap">Lines <span>from the bottom up</span></div>{a}</div>'
                   f'<div><div class="cap">Spaces <span>from the bottom up</span></div>{b}</div></div>'
                   f'<div class="cap">Outside the staff <span>notes above and below, some on ledger lines</span></div>{c}</div>')
    tips = ('<div class="tips blk"><div class="tip"><p><b>Seven letters</b></p><p>Music uses only the letters A, B, C, D, E, F and G. '
            'After G the letters start again at A, so every word in this book is spelled with just those seven letters.</p></div>'
            '<div class="tip"><p><b>Ledger lines</b></p><p>A ledger line is a short line added above or below the staff for a note that does not fit. '
            'Middle C sits on a ledger line below the treble staff and on a ledger line above the bass staff.</p></div></div>')
    inner = (top("Note Letter Reference", "Treble and bass clef: lines, spaces and notes outside the staff", "REFERENCE", "Keep it on your desk")
             + f'<div style="display:flex;flex-direction:column;justify-content:space-between;flex:1;padding:6pt 0 12pt">{blocks}{tips}</div>')
    return page("ref", inner, wm, "ws")


def key_set_block(s):
    items = ""
    for i, w in enumerate(s["words"], 1):
        items += f'<div class="kit" data-kset="{s["id"]}" data-item="{i}" data-ans="{w}"><i>{i}</i><b>{w}</b><span>{len(w)} notes</span></div>'
    return (f'<div class="kblk blk"><div class="kt">{CLEF_NAME[s["clef"]]} · Level {s["level"]} · Set {s["n"]}'
            f'<span>{R("ws-" + s["id"], True)}</span></div><div class="kgrid">{items}</div></div>')


def key_clef_page(clef, wm=False):
    kind = KEY_OF[clef]
    cp = "T" if clef == "treble" else "B"
    blocks = "".join(key_set_block(s) for s in SETS if s["clef"] == clef)
    rng = f'Pages {PAGEOF["ws-" + cp + "-A1"]}–{PAGEOF["ws-" + cp + "-B2"]}'
    inner = (top("Answer Key", f"{CLEF_NAME[clef]} · Spell the Word", "KEY", rng, "key")
             + f'<div style="margin-top:10pt">{blocks}</div>')
    return page(kind, inner, wm, "ws")


def key_riddle_page(wm=False):
    items = ""
    for r in RIDDLES:
        items += (f'<div class="kit" data-krid="{r["n"]}" data-ans="{r["answer"]}"><i>{r["n"]}</i><b>{r["answer"]}</b>'
                  f'<span>{r["gloss"]}</span></div>')
    sk = ""
    for i, ((clef, w), st) in enumerate(zip(SPELL, SPELL_STEPS), 1):
        svg = staff_svg(clef, st, "spellkey:%d" % i, 252.0, 4.8, spacing=28, labels=True)
        sk += (f'<div class="sk blk" data-kspell="{i}" data-ans="{w}"><div class="skh">{i}. {w}<span>{CLEF_NAME[clef]}</span></div>{svg}</div>')
    tagl = f'Pages {PAGEOF["riddle1"]}–{PAGEOF["riddle3"]} and {PAGEOF["spell"]}'
    inner = (top("Answer Key", "Winter riddles and Spell It with notes", "KEY", tagl, "key")
             + f'<div class="kblk blk" style="margin-top:10pt"><div class="kt">Winter riddles<span>{RR("riddle1", "riddle3", True)}</span></div>'
               f'<div class="kgrid rkey">{items}</div></div>'
             f'<div class="kblk blk"><div class="kt">Spell it with notes<span>{R("spell", True)}: one correct set of notes for each word</span></div>'
             f'<div class="skgrid">{sk}</div></div>')
    return page("keyR", inner, wm, "ws")


def teacher_page(wm=False):
    inner = (f'<div class="rule"><h1>Teacher Notes</h1><div class="l" style="font-size:13pt">{TITLE}: spell-the-word worksheets, riddles and answer keys</div></div>'
             f'<div class="cols"><div>'
             f'<h2>What students do</h2><p>Students read a row of notes, name each note by its letter and write the word the notes spell. '
             f'Every word uses only the seven music letters A, B, C, D, E, F and G, so a student who reads every note correctly can spell every word.</p>'
             f'<h2>What is inside</h2><ul>'
             f'<li><b>Reference sheet:</b> {R("ref")}. Lines, spaces and notes outside the staff in both clefs.</li>'
             f'<li><b>Treble clef:</b> {RR("ws-T-A1", "ws-T-B2")}, with Level A on {RR("ws-T-A1", "ws-T-A2")} and Level B on {RR("ws-T-B1", "ws-T-B2")}.</li>'
             f'<li><b>Bass clef:</b> {RR("ws-B-A1", "ws-B-B2")}, with Level A on {RR("ws-B-A1", "ws-B-A2")} and Level B on {RR("ws-B-B1", "ws-B-B2")}.</li>'
             f'<li><b>Winter riddles:</b> {RR("riddle1", "riddle3")}, {NRID} riddles in three sets.</li>'
             f'<li><b>Write your own word:</b> {R("own")}. <b>Spell it with notes:</b> {R("spell")}.</li>'
             f'<li><b>Answer keys:</b> {RR("keyT", "keyR")}. <b>Terms of use:</b> {R("terms")}.</li></ul>'
             f'<p>Each worksheet page has eight words, so the {len(SETS)} worksheet pages hold {NWORDS} words in all. '
             f'Words run from three letters, such as BAD, to seven letters in the riddles.</p>'
             f'<h2>The two levels</h2><p><b>Level A:</b> every note sits on a line or in a space inside the staff.</p>'
             f'<p><b>Level B:</b> some notes sit above or below the staff, and every word has at least one note that needs a ledger line. '
             f'In treble clef those are A and B below the staff, middle C and high A. In bass clef they are D and E below the staff, and middle C and D above it.</p>'
             f'<h2>The riddles</h2><p>Each riddle has a clue, a row of notes and a line for the answer. The notes spell the answer, so students can check their reading '
             f'against the clue. If the word does not fit the clue, the notes need a second look. Sets 1 and 2 use Level A notes, and set 3 uses Level B notes.</p>'
             f'</div><div>'
             f'<h2>Suggested path</h2><ol><li>Read the reference sheet together and practice the sayings for the lines and spaces.</li>'
             f'<li>Do treble clef Level A, then bass clef Level A.</li>'
             f'<li>Move to Level B when students can name notes inside the staff without the reference sheet.</li>'
             f'<li>Use the riddles as a challenge or an early-finisher task.</li></ol>'
             f'<h2>Write your own and spell it</h2><p>On {R("own")} students choose their own words and draw the notes. On {R("spell")} the word is given and students draw the notes. '
             f'Quarter notes are used on every page, so the notes show pitch only. Stems point up for notes below the middle line and down for notes on or above it. '
             f'Students can trade papers and read each other\'s words. Answers on these two pages will vary, and {R("keyR")} shows one correct set for {R("spell")}.</p>'
             f'<h2>Grades 3 to 4</h2><ul><li>Start with Level A in one clef and keep the reference sheet on the desk.</li>'
             f'<li>Work in pairs: one student reads the notes aloud and the other writes the word.</li>'
             f'<li>Read the riddle clues aloud to the class.</li></ul>'
             f'<h2>Grades 5 to 6</h2><ul><li>Use Level B and both clefs as fluency practice, without the reference sheet.</li>'
             f'<li>Time a page for a friendly challenge and ask students to beat their own time.</li>'
             f'<li>Have students write riddles of their own with answers spelled from A to G.</li></ul>'
             f'<h2>Standards and printing</h2><p>These pages practice reading notes in standard notation, which supports the performing and reading goals in the National Core Arts Standards for music. '
             f'The pages print well in black and white. The blue is one accent color. No songs, lyrics or copyrighted characters are used.</p>'
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
             f'<li>Worksheets, riddles, reference sheet and answer keys: original work, {BRAND} by {STORE}.</li>'
             f'<li>Cover illustration: house-style line art made with digital tools by {BRAND}.</li>'
             f'<li>Music notation: Bravura © Steinberg Media Technologies GmbH, SIL Open Font License 1.1.</li>'
             f'<li>Text fonts: Oswald (The Oswald Project Authors) and Source Sans 3 (Adobe), SIL Open Font License 1.1.</li></ul>'
             f'<h2>What is in this file</h2><p>{R("cover", True)} cover, {R("teacher")} teacher notes, {R("ref")} reference sheet, '
             f'{RR("ws-T-A1", "ws-B-B2")} the {len(SETS)} worksheet pages ({NWORDS} words), {RR("riddle1", "riddle3")} {NRID} winter riddles, '
             f'{R("own")} write your own word, {R("spell")} spell it with notes, {RR("keyT", "keyR")} answer keys and {R("terms")} these terms: '
             f'{TOTAL_PAGES} pages in all.</p>'
             f'<p class="small">{DISCLOSURE}</p><div class="fill"></div>')
    return page("terms", inner, wm, "doc")


SUBTITLE = "Spell-the-word worksheets in treble and bass clef, with winter riddles and answer keys"
BAND = f'Grades 3–6 <em>·</em> {NWORDS} words <em>·</em> {NRID} riddles <em>·</em> {TOTAL_PAGES} pages'


def cover_page():
    return (f'<section class="page cover" data-page="1" data-kind="cover" data-name="Cover"><div class="store">{BRAND}</div>'
            f'<div style="height:4.4in;display:flex;align-items:center;justify-content:center"><img src="../art/hero.png" style="height:4.2in;display:block" alt=""></div>'
            f'<div class="ctitle"><div class="a">WINTER</div><div class="b">NOTE SPELLER</div>'
            f'<div class="c">{SUBTITLE}</div></div>'
            f'<div class="cband">{BAND}</div></section>')


def all_pages(wm=False):
    p = [cover_page(), teacher_page(wm), ref_page(wm)] + [ws_page(s, wm) for s in SETS] + [riddle_page(n, wm) for n in RIDDLE_SETS]
    p += [own_page(wm), spell_page(wm), key_clef_page("treble", wm), key_clef_page("bass", wm), key_riddle_page(wm), terms_page(wm)]
    return p


SHOT_PAGES = {k: v for k, v in PAGEOF.items() if k != "cover"}
PREVIEW_ORDER = ["ws-T-A1", "ws-B-B1", "riddle1", "keyT"]

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
        f'<div style="height:520px;display:flex;align-items:center;justify-content:center"><img src="../art/hero.png" style="height:520px;display:block" alt=""></div>'
        f'<div><div class="hd" style="font-size:72px">Winter</div>'
        f'<div class="hd" style="font-size:122px">Note Speller</div>'
        f'<div class="sub" style="font-size:27px;margin-top:12px;padding:0 40px">{SUBTITLE}</div></div>'
        f'</div><div class="band">{BAND}</div></div>')


def shots(items, w):
    return "".join(f'<div style="width:{w}px"><div class="shot"><img src="{src}"></div><div class="lbl">{lab}</div></div>' for src, lab in items)


def shots_row(headline, sub, items, band, w):
    return sq_doc(f'<div class="sq"><div class="store">{BRAND}</div>'
                  f'<div class="hd" style="font-size:66px;margin-top:24px">{headline}</div>'
                  f'<div class="sub" style="font-size:27px;margin-top:8px">{sub}</div>'
                  f'<div style="flex:1;display:flex;align-items:center;padding-bottom:74px"><div style="display:flex;gap:44px;align-items:flex-start">{shots(items, w)}</div></div>'
                  f'<div class="band">{band}</div></div>')


def label(kind, extra):
    return f'{PAGE_NAMES[kind]}<span>{extra}</span>'


def square_pages():
    return [
        shots_row("Spell the word in two clefs", "Read the notes, name each letter and write the word",
                  [("shot-ws-T-A1.png", label("ws-T-A1", "eight words, notes inside the staff")),
                   ("shot-ws-B-B1.png", label("ws-B-B1", "bass clef with ledger lines"))],
                  f"{NWORDS} words <em>·</em> treble and bass clef <em>·</em> 2 levels", 420),
        shots_row("Riddles and answer keys", "The notes spell the answer to each clue",
                  [("shot-riddle1.png", label("riddle1", "four riddles to solve")),
                   ("shot-keyT.png", label("keyT", "every word listed"))],
                  f"{NRID} riddles <em>·</em> answer keys included <em>·</em> {TOTAL_PAGES} pages", 420),
        shots_row("Reference and note drawing", "Keep the letters handy, then draw the notes for a word",
                  [("shot-ref.png", label("ref", "lines, spaces and ledger lines")),
                   ("shot-spell.png", label("spell", "draw the notes for each word"))],
                  f"Reference sheet <em>·</em> spell it with notes <em>·</em> {TOTAL_PAGES} pages", 420),
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
    sec = "\n".join(f"- {n}: {c}" for n, c in SECTION_PAGES)
    nt = sum(len(s["words"]) for s in SETS if s["clef"] == "treble")
    nb = sum(len(s["words"]) for s in SETS if s["clef"] == "bass")
    return f"""# UPLOAD: {LISTING_TITLE} (TpT 060)

These fields follow the order of TpT's "Add a resource" form. Winter theme (riddles and art); the title itself carries no seasonal word. Preferred title if TpT rejects the one below: "Note Naming Worksheets: Spell the Word, Treble & Bass Clef, Gr 3-6".

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
Students read a row of notes on the staff, name each note by its letter and write the word the notes spell. Every word uses only the letters A to G, so each note has exactly one answer and the words are real ones such as BAD, CAGE, FADED and DECADE. This set has {NWORDS} spell-the-word items in treble clef and bass clef, {NRID} winter riddles whose answers are spelled in notes, a reference sheet, blank staves for writing your own word, a page for drawing the notes of a given word, and answer keys for every page. Made for general music, band, orchestra and choir in grades 3 to 6.

WHAT'S INCLUDED ({TOTAL_PAGES} pages, PDF, US Letter)
• Cover (1 page)
• Teacher notes: levels, a suggested path, ideas for grades 3-4 and grades 5-6 (1 page)
• Note letter reference sheet: lines, spaces, ledger-line notes and the sayings for both clefs (1 page)
• Treble clef spell-the-word worksheets: Level A with notes inside the staff, Level B with ledger-line notes, 8 words per page and {nt} words in all (4 pages)
• Bass clef spell-the-word worksheets: Level A and Level B, 8 words per page and {nb} words in all (4 pages)
• Winter riddles: {NRID} riddles in 3 sets, each with a clue, a row of notes and a line for the answer (3 pages)
• Write your own word: {NOWN} blank staves in treble and bass clef (1 page)
• Spell it with notes: {NSPELL} given words for students to draw (1 page)
• Answer keys: both clefs, the riddles and the spell-it page (3 pages)
• Terms of use and credits (1 page)
Total: {TOTAL_PAGES} pages.

HOW TO USE
Print the pages you need. Students can start with Level A in one clef and move to Level B and the riddles when they are ready. The riddles make a good early-finisher task, and the write-your-own page lets partners trade words.

• Grades 3-6 (grades 3-4 with the reference sheet, grades 5-6 without it)
• Quarter notes on every page, so the pages practice pitch only
• Prints well in black and white; one accent color
• No songs, lyrics or copyrighted characters

{DISCLOSURE}
```

## 3. Grades

3, 4, 5, 6.

## 4. Subjects and tags

- Subjects: {", ".join(SUBJECTS)}
- Tags: {", ".join(TAGS)}

## 5. Page count by section (totals {TOTAL_PAGES})

{sec}
- Total: {TOTAL_PAGES}

## 6. Standards

None cited by code. The teacher notes say the pages support the reading and performing goals in the National Core Arts Standards for music.

## 7. Price

**${PRICE}** (paid; owner range $3-5).

## 8. Preview

Paid. Preview PDF: page {PAGEOF["ws-T-A1"]} (treble clef Level A), page {PAGEOF["ws-B-B1"]} (bass clef Level B), page {PAGEOF["riddle1"]} (winter riddles, set 1) and page {PAGEOF["keyT"]} (treble clef answer key), all watermarked.

## 9. Before you click publish

- [ ] Title has no seasonal word.
- Open owner question: logo beside HUDSON BEAT (see tpt/STYLE.md).
"""


def tpt_json():
    return {
        "price": PRICE, "license_price": PRICE, "tax_code": "Other Digital Goods - No Physical Media",
        "grades": GRADES, "subjects": SUBJECTS, "tags": TAGS, "formats": ["PDF"], "pages": TOTAL_PAGES, "answer_key": "Included",
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
# A second table, typed separately from the one above: every word the buyer will see, by worksheet page (treble order; bass is reversed per page).
EXPECT_WORDS = {
    "A1": "BAD BEG DAD FED ADD FAD GAB EDGE", "A2": "AGED DEED BEEF FADED FACED ADDED DECADE BEADED",
    "B1": "AGE DAB EBB BEE CAB CAGE BABE ACED", "B2": "BADE ADAGE EBBED DECAF FACADE BEGGED BAGGED GABBED",
}
EXPECT_RIDDLES = ["FACE", "FEED", "EGG", "BED", "BAG", "CAFE", "ACE", "FADE", "BEAD", "BADGE", "CABBAGE", "BAGGAGE"]
EXPECT_SPELL = ["FEE", "GAFFE", "EGGED", "DECADE", "CAGED", "DEFACE", "EFFACE", "CEDE"]
EXPECT_REF = {
    "treble": dict(lines="EGBDF", spaces="FACE", outside=[("A", 3), ("B", 3), ("C", 4), ("D", 4), ("G", 5), ("A", 5)]),
    "bass": dict(lines="GBDFA", spaces="ACEG", outside=[("D", 2), ("E", 2), ("B", 3), ("C", 4), ("D", 4)]),
}
SEASONAL = r"winter|snow|holiday|christmas|\bfall\b|autumn|spring|summer|halloween|new year|thanksgiving|december"
UK_SPELLINGS = ["practise", "colour", "favourite", "centre", "metre", "recognise", "organise", "behaviour", "neighbour", "programme", "theatre", "licence"]
QA_WORDS = ["recomputed", "--check", "checked by hand", "handmade", "hand-checked", "classroom-tested", "verified by", "inspector", "QA"]
CLOCK = "CDEFGAB"

NUM = r"(-?[\d.]+)"
RX_SVG = re.compile(r'<svg class="ns" data-ctx="([^"]*)" data-s="([\d.]+)"[^>]*viewBox="0 0 ([\d.]+) ([\d.]+)"[^>]*>(.*?)</svg>', re.S)
RX_SL = re.compile(rf'<line class="sl" x1="{NUM}" y1="{NUM}" x2="{NUM}" y2="{NUM}"')
RX_CLEF = re.compile(rf'<text class="clef" x="{NUM}" y="{NUM}" font-family="Bravura" font-size="{NUM}"[^>]*>&#x([0-9A-F]+);</text>')
RX_NT = re.compile(r'<g class="nt">(.*?)</g>', re.S)
RX_LED = re.compile(rf'<line class="led" x1="{NUM}" y1="{NUM}" x2="{NUM}" y2="{NUM}"')
RX_HEAD = re.compile(rf'<text class="head" x="{NUM}" y="{NUM}" font-family="Bravura" font-size="{NUM}"[^>]*>&#x([0-9A-F]+);</text>')
RX_STEM = re.compile(rf'<line class="stem" data-dir="(up|down)" x1="{NUM}" y1="{NUM}" x2="{NUM}" y2="{NUM}"')
RX_LABEL = re.compile(rf'<text class="rl" x="{NUM}"[^>]*>([A-G])</text>')
LINE_LETTERS = {"treble": "EGBDF", "bass": "GBDFA"}      # bottom to top
SPACE_LETTERS = {"treble": "FACE", "bass": "ACEG"}


def parse_staff(body, S, w, h, ctx):
    """Parse one rendered staff. Every letter is recomputed from drawn geometry only: staff lines, clef glyph and notehead centres.
    Returns (clef, notes, errors, labels); clef is None when the staff cannot be read."""
    errs = []
    lines = [float(m.group(2)) for m in RX_SL.finditer(body)]
    if len(lines) != 5:
        return None, [], [f"{ctx}: {len(lines)} staff lines"], []
    if any(abs((lines[i + 1] - lines[i]) - S) > 0.02 for i in range(4)):
        errs.append(f"{ctx}: staff line spacing is not {S}")
    bottom = max(lines)
    if len(RX_CLEF.findall(body)) != 1:
        return None, [], [f"{ctx}: not exactly one clef"], []
    cm = RX_CLEF.search(body)
    clef = GLYPH_CLEF.get(int(cm.group(4), 16))
    if clef is None:
        return None, [], [f"{ctx}: unknown clef glyph"], []
    anchor_letter, anchor_oct = {"treble": ("G", 4), "bass": ("F", 3)}[clef]      # G clef curls round G4, F clef marks F3
    cy = float(cm.group(2))
    want_anchor = {"treble": 2, "bass": 6}[clef]
    if round((bottom - cy) / (S / 2)) != want_anchor:
        errs.append(f"{ctx}: {clef} clef glyph sits on step {round((bottom - cy) / (S / 2))}, must be {want_anchor}")
    if abs(float(cm.group(3)) - 4 * S) > 0.01:
        errs.append(f"{ctx}: clef size")
    notes = []
    xs = []
    for nt in RX_NT.finditer(body):
        b = nt.group(1)
        hm = RX_HEAD.search(b)
        hx, hy = float(hm.group(1)), float(hm.group(2))
        if abs(float(hm.group(3)) - 4 * S) > 0.01:
            errs.append(f"{ctx}: notehead size")
        off = (cy - hy) / (S / 2)
        if abs(off - round(off)) > 0.02:
            errs.append(f"{ctx}: notehead off the line/space grid ({off:.2f})")
        off = round(off)
        pos = CLOCK.index(anchor_letter) + off
        letter, octave = CLOCK[pos % 7], anchor_oct + pos // 7
        step = round((bottom - hy) / (S / 2))
        if 0 <= step <= 8:
            want = LINE_LETTERS[clef][step // 2] if step % 2 == 0 else SPACE_LETTERS[clef][step // 2]
            if want != letter:
                errs.append(f"{ctx}: line/space rule says {want}, geometry says {letter}")
        hw = HEAD_W * S
        need = set(range(-2, step - 1, -2)) if step < 0 else set()
        if step > 8:
            need |= set(range(10, step + 1, 2))
        got = []
        for lm in RX_LED.finditer(b):
            x1, y1, x2, y2 = (float(lm.group(i)) for i in range(1, 5))
            if abs(y1 - y2) > 0.01:
                errs.append(f"{ctx}: tilted ledger line")
            if not (x1 <= hx - 0.2 * S and x2 >= hx + hw + 0.2 * S):
                errs.append(f"{ctx}: ledger line does not cover the notehead")
            if x2 - x1 > hw + 1.0 * S:
                errs.append(f"{ctx}: ledger line too long")
            e = (bottom - y1) / (S / 2)
            if abs(e - round(e)) > 0.02:
                errs.append(f"{ctx}: ledger line off grid")
            got.append(round(e))
        if sorted(got) != sorted(need):
            errs.append(f"{ctx}: ledger lines {sorted(got)} but the note at step {step} needs {sorted(need)}")
        sm = RX_STEM.search(b)
        if not sm:
            errs.append(f"{ctx}: note has no stem")
        else:
            d, x1, y1, x2, y2 = sm.group(1), *(float(sm.group(i)) for i in range(2, 6))
            want_dir = "up" if step < 4 else "down"
            if d != want_dir:
                errs.append(f"{ctx}: stem {d} at step {step}, should be {want_dir}")
            if abs(x1 - x2) > 0.01:
                errs.append(f"{ctx}: stem not vertical")
            if d == "up":
                if abs(x1 - (hx + hw)) > 0.13 * S:
                    errs.append(f"{ctx}: up-stem not on the right edge of the head")
                length, end_y = y1 - y2, y2
                if abs(y1 - (hy - 0.168 * S)) > 0.05:
                    errs.append(f"{ctx}: up-stem does not start at the head")
                if y2 > bottom - 4 * (S / 2) + 0.05:
                    errs.append(f"{ctx}: up-stem does not reach the middle line")
            else:
                if abs(x1 - hx) > 0.13 * S:
                    errs.append(f"{ctx}: down-stem not on the left edge of the head")
                length, end_y = y2 - y1, y2
                if abs(y1 - (hy + 0.168 * S)) > 0.05:
                    errs.append(f"{ctx}: down-stem does not start at the head")
                if end_y < bottom - 4 * (S / 2) - 0.05:
                    errs.append(f"{ctx}: down-stem does not reach the middle line")
            if length < 3.5 * S - 0.05:
                errs.append(f"{ctx}: stem shorter than 3.5 spaces")
            if min(y1, y2) < 0 or max(y1, y2) > h:
                errs.append(f"{ctx}: stem leaves the drawing")
        if hy - 0.6 * S < 0 or hy + 0.6 * S > h:
            errs.append(f"{ctx}: notehead clipped by the drawing edge")
        if hx + hw + 0.2 * S > w - 3:
            errs.append(f"{ctx}: note runs into the end barline")
        if len(RX_HEAD.findall(b)) != 1 or "&#xE0A4;" not in b:
            errs.append(f"{ctx}: a note must be exactly one filled quarter-note head")
        xs.append(hx)
        notes.append(dict(clef=clef, step=step, letter=letter, octave=octave, x=hx))
    if any(xs[i + 1] - xs[i] < 3.0 * HEAD_W * S - 0.01 for i in range(len(xs) - 1)):
        errs.append(f"{ctx}: notes crowded (need at least 3 head widths between note centres)")
    if xs != sorted(xs):
        errs.append(f"{ctx}: notes out of order")
    if xs and xs[0] < 3 + 3.0 * S + 8:
        errs.append(f"{ctx}: first note too close to the clef")
    labels = [(float(m.group(1)), m.group(2)) for m in RX_LABEL.finditer(body)]
    return clef, notes, errs, labels


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
      d.refs = A('[data-ref]', e => ({ page: pageNo(e), kind: e.dataset.ref, n: +e.dataset.n, kind2: e.dataset.ref2 || '', n2: +(e.dataset.n2 || 0), txt: T(e) }));
      d.pagetext = A('.page', pg => { const c = pg.cloneNode(true); c.querySelectorAll('.foot,.wm').forEach(x => x.remove()); return c.innerText.replace(/\s+/g, ' ').trim(); });
      d.foottext = A('.page', pg => T(pg.querySelector('.foot')));
      d.rowsWs = A('[data-ws]', e => ({ id: e.dataset.ws, item: +e.dataset.item, page: pageNo(e), blanks: e.querySelectorAll('.wd b').length }));
      d.rid = A('[data-riddle]', e => ({ n: +e.dataset.riddle, page: pageNo(e), clue: T(e.querySelector('.rt p')), blanks: e.querySelectorAll('.wd b').length, clef: T(e.querySelector('.cl')) }));
      d.own = A('[data-own]', e => ({ n: +e.dataset.own, page: pageNo(e), blanks: e.querySelectorAll('.wd b').length }));
      d.spell = A('[data-spell]', e => ({ n: +e.dataset.spell, word: e.dataset.word, page: pageNo(e), shown: T(e.querySelector('.w')) }));
      d.kset = A('[data-kset]', e => ({ id: e.dataset.kset, item: +e.dataset.item, ans: e.dataset.ans, shown: T(e.querySelector('b')), num: T(e.querySelector('i')), page: pageNo(e), txt: T(e) }));
      d.krid = A('[data-krid]', e => ({ n: +e.dataset.krid, ans: e.dataset.ans, shown: T(e.querySelector('b')), page: pageNo(e) }));
      d.kspell = A('[data-kspell]', e => ({ n: +e.dataset.kspell, ans: e.dataset.ans, head: T(e.querySelector('.skh')), page: pageNo(e) }));
      const res = []; d.gaps = [];
      document.querySelectorAll('.page').forEach((pg, i) => {
        const n = i + 1, pr = pg.getBoundingClientRect();
        const ft = pg.querySelector('.foot');
        const ftop = ft ? ft.getBoundingClientRect().top : pr.bottom;
        if (pg.scrollHeight > pg.clientHeight + 1) res.push(`page ${n}: content overflows the page`);
        let low = 0; const boxes = [];
        pg.querySelectorAll('.blk, .doc p, .doc li, .doc h2, .tip').forEach(el => {
          if (ft && ft.contains(el)) return;
          const r = el.getBoundingClientRect();
          if (r.height === 0) return;
          low = Math.max(low, r.bottom);
          if (r.bottom > ftop - 9) res.push(`page ${n}: ${el.tagName}.${el.className} bottom ${(r.bottom - ftop).toFixed(1)}px vs footer rule (needs <= -9)`);
          if (r.right > pr.right - 0.35 * 96 + 0.5 || r.left < pr.left + 0.35 * 96 - 0.5) res.push(`page ${n}: ${el.tagName}.${el.className} too close to the page edge`);
          if (el.matches('.blk') && !el.matches('.top, .name, .how')) boxes.push([el, r]);
        });
        for (let a = 0; a < boxes.length; a++) for (let c = a + 1; c < boxes.length; c++) {
          const A = boxes[a][1], C = boxes[c][1];
          if (boxes[a][0].contains(boxes[c][0]) || boxes[c][0].contains(boxes[a][0])) continue;
          const gx = Math.max(A.left, C.left) - Math.min(A.right, C.right);
          const gy = Math.max(A.top, C.top) - Math.min(A.bottom, C.bottom);
          if (gx < 4 && gy < 4) res.push(`page ${n}: ${boxes[a][0].className} and ${boxes[c][0].className} touch or overlap (no gutter)`);
        }
        d.gaps.push(Math.round(ftop - low));
        pg.querySelectorAll('.rid, .sk, .tip, .kit, .wd, .w, .cap, .cl2, .how, .tag').forEach(el => {
          if (getComputedStyle(el).display === 'inline') return;
          if (el.scrollHeight > el.clientHeight + 2 || el.scrollWidth > el.clientWidth + 2) res.push(`page ${n}: text clipped in ${el.tagName}.${el.className} (${el.scrollWidth}x${el.scrollHeight} in ${el.clientWidth}x${el.clientHeight}) ${el.innerText.slice(0,30)}`);
        });
        pg.querySelectorAll('svg.ns').forEach(sv => {
          const br = sv.getBoundingClientRect(); const par = sv.parentElement.getBoundingClientRect();
          if (br.right > par.right + 1 || br.left < par.left - 1) res.push(`page ${n}: a staff sticks out of its box`);
          if (br.right > pr.right - 0.4 * 96 || br.left < pr.left + 0.4 * 96) res.push(`page ${n}: a staff is too close to the page edge`);
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
// Render every distinct drawing alone on a transparent ground, so its pixels can be checked against the image edge.
const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const spec = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
  const b = await chromium.launch();
  const ctx = await b.newContext({ viewport: { width: 900, height: 700 }, deviceScaleFactor: 3 });
  const p = await ctx.newPage();
  await p.goto(require('url').pathToFileURL(spec.page).href, { waitUntil: 'load' });
  await p.evaluate(() => document.fonts.ready);
  for (const id of spec.ids) await p.locator('#' + id).screenshot({ path: spec.dir + '/' + id + '.png', omitBackground: true });
  await b.close();
})().catch(e => { console.error(e); process.exit(1); });
"""


def inspect_html(files):
    js = os.path.join(BUILD, "inspect.js")
    open(js, "w").write(INSPECT_JS)
    r = subprocess.run(["node", js, *files], capture_output=True, text=True, env=node_env())
    if r.returncode != 0:
        sys.exit("inspect failed: " + r.stderr[-500:])
    return json.loads(r.stdout)


def count_claims(text, where):
    errs = []
    for m in re.finditer(r"(\d+)[ -]words?\b", text):
        if int(m.group(1)) not in (NWORDS, 32, 16, 8):
            errs.append(f"{where}: claims '{m.group(0)}'")
    for m in re.finditer(r"(\d+)[ -]riddles?\b", text):
        if int(m.group(1)) not in (NRID, 1):
            errs.append(f"{where}: claims '{m.group(0)}', expected {NRID}")
    for m in re.finditer(r"(\d+) pages", text):
        if int(m.group(1)) not in (TOTAL_PAGES, 1, 3, 4):
            errs.append(f"{where}: claims '{m.group(0)}'")
    return errs


def parse_all(html):
    """Return {ctx: (clef, notes, labels)} and a list of errors, from every drawn staff in the HTML."""
    out, errs = {}, []
    for pm in RX_SVG.finditer(html):
        ctx, S, w, h, body = pm.group(1), float(pm.group(2)), float(pm.group(3)), float(pm.group(4)), pm.group(5)
        clef, notes, e, labels = parse_staff(body, S, w, h, ctx)
        errs += e
        if clef is None:
            continue
        if ctx in out:
            errs.append(f"{ctx}: drawn twice")
        out[ctx] = (clef, notes, labels)
    return out, errs


def verify_content(res_html, d):
    errs = []
    staves, e = parse_all(res_html)
    errs += e
    nnotes = sum(len(v[1]) for v in staves.values())
    # ---- worksheets: word read from the geometry == data == second table; level rules; counts
    expect_pages = {}
    for s in SETS:
        want = EXPECT_WORDS[f"{s['level']}{s['n']}"].split()
        expect_pages[s["id"]] = want[::-1] if s["clef"] == "bass" else want
    ws_words = {}
    seen_rows = {}
    for r in d["rowsWs"]:
        seen_rows.setdefault(r["id"], []).append(r)
        if r["blanks"] != 1:
            errs.append(f"{r['id']} item {r['item']}: needs exactly one blank word line")
    for s in SETS:
        sid = s["id"]
        rows = seen_rows.get(sid, [])
        if [r["item"] for r in rows] != list(range(1, PER_PAGE + 1)):
            errs.append(f"{sid}: worksheet items are not 1..{PER_PAGE}")
        if any(r["page"] != PAGEOF["ws-" + sid] for r in rows):
            errs.append(f"{sid}: items on the wrong page")
        got = []
        for i in range(1, PER_PAGE + 1):
            v = staves.get(f"ws:{sid}:{i}")
            if not v:
                errs.append(f"{sid} item {i}: no staff drawn")
                got.append(None)
                continue
            clef, notes, _ = v
            if clef != s["clef"]:
                errs.append(f"{sid} item {i}: drawn in {clef}, page is {s['clef']}")
            word = "".join(n["letter"] for n in notes)
            got.append(word)
            ws_words[(sid, i)] = word
            if not word or any(c not in AG for c in word):
                errs.append(f"{sid} item {i}: word '{word}' uses a letter outside A-G")
            steps = [n["step"] for n in notes]
            if s["level"] == "A" and any(not 0 <= st <= 8 for st in steps):
                errs.append(f"{sid} item {i}: a Level A note outside the staff")
            if s["level"] == "B" and not any(st <= -2 or st >= 10 for st in steps):
                errs.append(f"{sid} item {i}: Level B word without a ledger-line note")
            if s["level"] == "B" and any(st < -4 or st > 11 for st in steps):
                errs.append(f"{sid} item {i}: note beyond the ledger lines used in the reference sheet")
            if not 3 <= len(word) <= 7:
                errs.append(f"{sid} item {i}: word length {len(word)}")
        if got != expect_pages[sid]:
            errs.append(f"{sid}: words read from the notes {got} differ from the expected table {expect_pages[sid]}")
        if got != s["words"]:
            errs.append(f"{sid}: words read from the notes differ from the generator data")
        if len(set(got)) != len(got):
            errs.append(f"{sid}: a word appears twice on the page")
    pa, pb = set(POOL["A"]), set(POOL["B"])
    if pa & pb:
        errs.append(f"pools share words: {pa & pb}")
    if (pa | pb) & set(EXPECT_RIDDLES):
        errs.append(f"a riddle answer is also a worksheet word: {(pa | pb) & set(EXPECT_RIDDLES)}")
    # ---- answer keys: item by item against the worksheet read from geometry
    keyed = {}
    for k in d["kset"]:
        keyed[(k["id"], k["item"])] = k
        if k["ans"] != k["shown"]:
            errs.append(f"key {k['id']} item {k['item']}: shows {k['shown']}, data-ans {k['ans']}")
        if k["num"] != str(k["item"]):
            errs.append(f"key {k['id']} item {k['item']}: numbered {k['num']}")
        if f"{len(k['ans'])} notes" not in k["txt"]:
            errs.append(f"key {k['id']} item {k['item']}: note count missing or wrong")
        want_page = PAGEOF["keyT"] if k["id"][0] == "T" else PAGEOF["keyB"]
        if k["page"] != want_page:
            errs.append(f"key {k['id']} item {k['item']}: on page {k['page']}, expected {want_page}")
    if len(d["kset"]) != len(SETS) * PER_PAGE or len(keyed) != len(d["kset"]):
        errs.append(f"key holds {len(d['kset'])} worksheet entries, worksheets have {len(SETS) * PER_PAGE}")
    for (sid, i), w in ws_words.items():
        k = keyed.get((sid, i))
        if not k:
            errs.append(f"key: {sid} item {i} missing")
        elif k["shown"] != w:
            errs.append(f"key {sid} item {i}: key {k['shown']} vs worksheet notes {w}")
    # ---- reference sheet
    for clef in ("treble", "bass"):
        e = EXPECT_REF[clef]
        for kind in ("lines", "spaces", "outside"):
            v = staves.get(f"ref:{clef}:{kind}")
            if not v:
                errs.append(f"reference {clef} {kind}: missing")
                continue
            c, notes, labels = v
            if c != clef:
                errs.append(f"reference {clef} {kind}: wrong clef")
            if [l for _, l in labels] != [n["letter"] for n in notes]:
                errs.append(f"reference {clef} {kind}: labels {[l for _, l in labels]} vs geometry {[n['letter'] for n in notes]}")
            for (lx, _), n in zip(labels, notes):
                if abs(lx - (n["x"] + HEAD_W * REF_S / 2)) > 0.6:
                    errs.append(f"reference {clef} {kind}: a label is not centred under its note")
            if kind in ("lines", "spaces"):
                if "".join(n["letter"] for n in notes) != e[kind]:
                    errs.append(f"reference {clef} {kind}: reads {''.join(n['letter'] for n in notes)}, expected {e[kind]}")
                want_steps = [0, 2, 4, 6, 8] if kind == "lines" else [1, 3, 5, 7]
                if [n["step"] for n in notes] != want_steps:
                    errs.append(f"reference {clef} {kind}: notes are not on the {kind}")
            else:
                if [(n["letter"], n["octave"]) for n in notes] != e["outside"]:
                    errs.append(f"reference {clef} outside: {[(n['letter'], n['octave']) for n in notes]} vs {e['outside']}")
                cs = [n for n in notes if (n["letter"], n["octave"]) == ("C", 4)]
                if len(cs) != 1 or cs[0]["step"] != {"treble": -2, "bass": 10}[clef]:
                    errs.append(f"reference {clef}: middle C not on its ledger line")
    # ---- riddles
    if [r["answer"] for r in RIDDLES] != EXPECT_RIDDLES:
        errs.append("riddle answers differ from the second table")
    if len(set(EXPECT_RIDDLES)) != NRID or NRID != 12:
        errs.append("riddle answers are not 12 distinct words")
    tokens = {r["answer"]: r["token"].lower() for r in RIDDLES}
    page_riddles = {r["n"]: r for r in d["rid"]}
    for r in RIDDLES:
        v = staves.get(f"rid:{r['n']}")
        dr = page_riddles.get(r["n"])
        if not v or not dr:
            errs.append(f"riddle {r['n']}: not on the page")
            continue
        clef, notes, _ = v
        word = "".join(n["letter"] for n in notes)
        if word != r["answer"] or word != EXPECT_RIDDLES[r["n"] - 1]:
            errs.append(f"riddle {r['n']}: notes spell {word}, answer is {r['answer']}")
        if clef != r["clef"] or CLEF_NAME[clef].lower() != dr["clef"].lower():
            errs.append(f"riddle {r['n']}: clef label '{dr['clef']}' vs drawn {clef}")
        want_pg = PAGEOF["riddle%d" % r["set"]]
        if dr["page"] != want_pg:
            errs.append(f"riddle {r['n']}: on page {dr['page']}, expected {want_pg}")
        if dr["blanks"] != 1:
            errs.append(f"riddle {r['n']}: needs one answer line")
        steps = [n["step"] for n in notes]
        if r["level"] == "A" and any(not 0 <= s <= 8 for s in steps):
            errs.append(f"riddle {r['n']}: Level A note outside the staff")
        if r["level"] == "B" and not any(s <= -2 or s >= 10 for s in steps):
            errs.append(f"riddle {r['n']}: Level B riddle without a ledger-line note")
        clue = dr["clue"].lower()
        if tokens[r["answer"]] not in clue:
            errs.append(f"riddle {r['n']}: the clue does not contain its key phrase '{tokens[r['answer']]}'")
        for ans, tok in tokens.items():
            if ans != r["answer"] and tok in clue:
                errs.append(f"riddle {r['n']}: the clue also holds the key phrase of {ans}")
        if re.search(rf"\b{r['answer'].lower()}s?\b", clue):
            errs.append(f"riddle {r['n']}: the clue gives away the answer")
        if r["gloss"] == "" or r["answer"].lower() in r["gloss"].lower().split():
            errs.append(f"riddle {r['n']}: gloss gives the answer away or is empty")
        _w = lambda t: {x[:4] for x in re.findall(r"[a-z]+", t.lower()) if len(x) >= 4}
        _shared = _w(r["gloss"]) & _w(dr["clue"])
        if not _shared:
            errs.append(f"riddle {r['n']}: key gloss shares no content word with the clue")
        print(f"  riddle {r['n']:2d} {r['answer']:8s} clue: {dr['clue']}\n{'':23s}gloss: {r['gloss']}  [shared: {', '.join(sorted(_shared))}]")
        if not re.search(r"[.?!]$", dr["clue"]):
            errs.append(f"riddle {r['n']}: clue is not a complete sentence")
    ridkeys = {k["n"]: k for k in d["krid"]}
    if sorted(ridkeys) != list(range(1, NRID + 1)):
        errs.append("riddle key does not list riddles 1..12")
    for n, k in ridkeys.items():
        v = staves.get(f"rid:{n}")
        if v and k["shown"] != "".join(x["letter"] for x in v[1]):
            errs.append(f"riddle key {n}: {k['shown']} vs notes {''.join(x['letter'] for x in v[1])}")
        if k["ans"] != k["shown"] or k["page"] != PAGEOF["keyR"]:
            errs.append(f"riddle key {n}: wrong page or data")
    for sn in RIDDLE_SETS:
        if sum(1 for r in d["rid"] if r["page"] == PAGEOF[f"riddle{sn}"]) != 4:
            errs.append(f"riddle page {sn} does not hold 4 riddles")
    # ---- write your own: blank staves, treble and bass counts
    clefs_own = [staves[k][0] for k in sorted((k for k in staves if k.startswith("own:")), key=lambda x: int(x.split(":")[1]))]
    if clefs_own != ["treble"] * 4 + ["bass"] * 4:
        errs.append(f"write-your-own staves are {clefs_own}")
    if any(staves[k][1] for k in staves if k.startswith("own:")):
        errs.append("a write-your-own staff has notes on it")
    if len(d["own"]) != NOWN or any(o["blanks"] != 1 for o in d["own"]):
        errs.append("write-your-own rows are not 8 with one word line each")
    # ---- spell it with notes
    if [s["word"] for s in d["spell"]] != EXPECT_SPELL or EXPECT_SPELL != [w for _, w in SPELL]:
        errs.append("spell-it words differ from the second table")
    for s in d["spell"]:
        if s["shown"].split()[0] != s["word"] or any(c not in AG for c in s["word"]):
            errs.append(f"spell-it {s['n']}: word shown '{s['shown']}' vs {s['word']}")
        v = staves.get(f"spell:{s['n']}:{SPELL[s['n'] - 1][0]}")
        if not v or v[1]:
            errs.append(f"spell-it {s['n']}: the student staff must be blank")
        elif v[0] != SPELL[s["n"] - 1][0]:
            errs.append(f"spell-it {s['n']}: wrong clef")
        if CLEF_NAME[SPELL[s["n"] - 1][0]] not in s["shown"]:
            errs.append(f"spell-it {s['n']}: clef name missing")
    for k in d["kspell"]:
        v = staves.get(f"spellkey:{k['n']}")
        if not v:
            errs.append(f"spell-it key {k['n']}: no staff")
            continue
        word = "".join(n["letter"] for n in v[1])
        if word != k["ans"] or word != EXPECT_SPELL[k["n"] - 1]:
            errs.append(f"spell-it key {k['n']}: notes spell {word}, word is {k['ans']}")
        if v[0] != SPELL[k["n"] - 1][0]:
            errs.append(f"spell-it key {k['n']}: wrong clef")
        if [l for _, l in v[2]] != [n["letter"] for n in v[1]]:
            errs.append(f"spell-it key {k['n']}: labels disagree with the notes")
        if any(not 0 <= n["step"] <= 8 for n in v[1]):
            errs.append(f"spell-it key {k['n']}: a model note outside the staff")
    if len(d["kspell"]) != NSPELL:
        errs.append("spell-it key does not show all 8 words")
    # ---- cross-references: every data-ref points at the page of that kind
    kinds = {p["kind"]: p["n"] for p in d["pages"]}
    for r in d["refs"]:
        if kinds.get(r["kind"]) != r["n"]:
            errs.append(f"page {r['page']}: reference '{r['txt']}' points at {r['kind']} which is page {kinds.get(r['kind'])}")
        if r["kind2"] and kinds.get(r["kind2"]) != r["n2"]:
            errs.append(f"page {r['page']}: reference '{r['txt']}' second end wrong")
        want = f"{r['n']}–{r['n2']}" if r["kind2"] else f"{r['n']}"
        if not r["txt"].endswith(want):
            errs.append(f"page {r['page']}: reference text '{r['txt']}' does not show {want}")
    if [p["kind"] for p in d["pages"]] != PAGE_ORDER:
        errs.append("page order differs from PAGE_ORDER")
    for p in d["pages"]:
        if p["name"] != PAGE_NAMES[p["kind"]]:
            errs.append(f"page {p['n']}: name '{p['name']}'")
    for s in SETS:
        n = PAGEOF["ws-" + s["id"]]
        if f"Answer key on page {PAGEOF[KEY_OF[s['clef']]]}" not in d["foottext"][n - 1]:
            errs.append(f"page {n}: footer does not point at the {s['clef']} key")
    for n in RIDDLE_SETS:
        if f"Answer key on page {PAGEOF['keyR']}" not in d["foottext"][PAGEOF[f"riddle{n}"] - 1]:
            errs.append(f"riddle page {n}: footer does not point at the riddle key")
    if f"Answer key on page {PAGEOF['keyR']}" not in d["foottext"][PAGEOF["spell"] - 1]:
        errs.append("spell-it page footer does not point at its key")
    # ---- text rules on every page
    for i, t in enumerate(d["pagetext"], 1):
        low = t.lower()
        for w in UK_SPELLINGS:
            if w in low:
                errs.append(f"page {i}: non-US spelling '{w}'")
        for w in QA_WORDS:
            if re.search(re.escape(w), t.replace("Q&A", ""), 0 if w == "QA" else re.I):
                errs.append(f"page {i}: internal QA wording '{w}'")
        errs += count_claims(t, f"page {i}")
    allp = " ".join(d["pagetext"])
    if f"{TOTAL_PAGES} pages in all" not in allp:
        errs.append("terms page does not state the page count")
    if f"{NWORDS} words" not in allp:
        errs.append("pages never state the word count")
    return errs, nnotes, len(ws_words)


def pdf_fonts(path):
    out = subprocess.run(["pdffonts", path], capture_output=True, text=True, check=True).stdout.splitlines()[2:]
    return [(line.split()[0], line.split()[-5]) for line in out]


def load_json(name):
    return json.load(open(os.path.join(TPT, name)))


def verify_drawings(res_html):
    """Every distinct staff drawing rendered alone on a transparent ground: its pixels must keep clear of the image edge."""
    errs = []
    from PIL import Image
    d = os.path.join(BUILD, "alone")
    os.makedirs(d, exist_ok=True)
    seen, cells, ids = {}, "", []
    for pm in RX_SVG.finditer(res_html):
        ctx, w, h, body = pm.group(1), pm.group(3), pm.group(4), pm.group(0)
        sig = re.sub(r'data-ctx="[^"]*"', "", body)
        if sig in seen:
            continue
        seen[sig] = ctx
        i = f"d{len(ids)}"
        ids.append(i)
        cells += f'<div id="{i}" style="width:{w}pt;height:{h}pt;margin:8px;flex:0 0 auto">{body}</div>'
    html = (f'<!doctype html><html><head><meta charset="utf-8"><style>{font_css()}html,body{{background:transparent!important;margin:0}}'
            f'body{{display:flex;flex-wrap:wrap}}</style></head><body>{cells}</body></html>')
    write("alone.html", html)
    spec = os.path.join(BUILD, "alone.json")
    json.dump({"page": os.path.join(BUILD, "alone.html"), "ids": ids, "dir": d}, open(spec, "w"))
    js = os.path.join(BUILD, "alone.js")
    open(js, "w").write(ALONE_JS)
    r = subprocess.run(["node", js, spec], capture_output=True, text=True, env=node_env())
    if r.returncode != 0:
        return [f"drawing render failed: {r.stderr[-300:]}"], 0
    ctxs = list(seen.values())
    for i, ctx in zip(ids, ctxs):
        im = Image.open(os.path.join(d, i + ".png")).convert("RGBA")
        a = im.getchannel("A").point(lambda v: 255 if v > 8 else 0)
        bb = a.getbbox()
        if not bb:
            errs.append(f"drawing {ctx}: renders nothing")
            continue
        w, h = im.size
        pad = 6      # px at 3x: a stroke is about 3 px, so this is at least two strokes
        if bb[0] < pad or bb[1] < pad or bb[2] > w - pad or bb[3] > h - pad:
            errs.append(f"drawing {ctx}: rendered pixels {bb} come within {pad}px of the edge of its {w}x{h} image")
    return errs, len(ids)


def verify_pdf_pixels():
    """Render the product PDF: nothing printed within 0.3 in of the page edge."""
    errs = []
    from PIL import Image
    out = os.path.join(BUILD, "px")
    os.makedirs(out, exist_ok=True)
    for f in os.listdir(out):
        os.remove(os.path.join(out, f))
    subprocess.run(["pdftoppm", "-png", "-r", "80", PDF, os.path.join(out, "pg")], check=True)
    files = sorted(f for f in os.listdir(out) if f.startswith("pg") and f.endswith(".png"))
    for n, f in enumerate(files, 1):
        im = Image.open(os.path.join(out, f)).convert("L")
        w, h = im.size
        m = int(0.3 * 80)
        px = im.load()
        dark = sum(1 for y in range(h) for x in list(range(0, m)) + list(range(w - m, w)) if px[x, y] < 200)
        dark += sum(1 for y in list(range(0, m)) + list(range(h - m, h)) for x in range(w) if px[x, y] < 200)
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
        dark = sum(1 for y in range(0, ytop - 4) for x in list(range(0, e)) + list(range(2000 - e, 2000)) if px[x, y] < 235)
        dark += sum(1 for y in range(0, e) for x in range(2000) if px[x, y] < 235)
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
        if cols and abs(min(cols) - (1999 - max(cols))) > 60:
            errs.append(f"{name}: uneven side margins ({min(cols)} left, {1999 - max(cols)} right)")
    a = Image.open(os.path.join(ART, "hero.png")).getchannel("A").point(lambda v: 255 if v > 100 else 0)
    bb = a.getbbox()
    if not bb or bb[0] < 5 or bb[1] < 5 or bb[2] > a.width - 5 or bb[3] > a.height - 5:
        errs.append(f"art/hero.png: opaque pixels come within 5px of the image edge {bb}")
    hero = Image.open(os.path.join(ART, "hero.png"))
    if hero.mode != "RGBA" or hero.getpixel((2, 2))[3] != 0:
        errs.append("art/hero.png: corner is not transparent (needs a transparent ground to sit on white)")
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
    prd = PdfReader(PREVIEW_PDF)
    want_pages = [SHOT_PAGES[k] for k in PREVIEW_ORDER]
    for i in range(4):
        t = prd.pages[i].extract_text() or ""
        if t.count("PREVIEW") != 1:
            errs.append(f"preview PDF page {i + 1}: expected exactly one PREVIEW watermark")
        if f"Page {want_pages[i]}" not in t.replace("\n", " "):
            errs.append(f"preview PDF page {i + 1} is not page {want_pages[i]} of the product")
    errs += verify_images()
    errs += verify_pdf_pixels()
    for h in ("cover.html", "p1.html", "p2.html", "p3.html"):
        p = os.path.join(BUILD, h)
        if not os.path.exists(p):
            errs.append(f"build/{h} missing")
            continue
        s = open(p).read()
        txt = re.sub(r"<[^>]+>", " ", re.sub(r"<style>.*?</style>", "", s, flags=re.S))
        errs += count_claims(txt, h)
        if "swm" in s or "PREVIEW" in s:
            errs.append(f"{h}: has its own watermark layer (the page shots already carry one)")
        if "_art" in s:
            errs.append(f"{h}: references tpt/_art")
        for m in re.finditer(r'<div class="lbl">([^<]*)<span>', s):
            if m.group(1) not in PAGE_NAMES.values():
                errs.append(f"{h}: label '{m.group(1)}' is not a real page name")
        for m in re.finditer(r'src="(shot-[A-Za-z0-9-]+\.png)"', s):
            if not os.path.exists(os.path.join(BUILD, m.group(1))):
                errs.append(f"{h}: missing {m.group(1)}")
    cov = open(os.path.join(BUILD, "cover.html")).read()
    for need in (f"{TOTAL_PAGES} pages", f"{NWORDS} words", f"{NRID} riddles"):
        if need not in cov:
            errs.append(f"cover band lacks '{need}'")
    pdfcov = open(os.path.join(BUILD, "resource.html")).read().split('data-kind="cover"')[1].split("</section>")[0]
    for need in (f"{TOTAL_PAGES} pages", f"{NWORDS} words", f"{NRID} riddles"):
        if need not in pdfcov:
            errs.append(f"PDF cover band lacks '{need}'")
    pv = [open(os.path.join(BUILD, f"p{i}.html")).read() for i in (1, 2, 3)]
    if not ("shot-ws-T-A1.png" in pv[0] and "shot-ws-B-B1.png" in pv[0]):
        errs.append("preview-1 does not show treble level A and bass level B worksheets")
    if not ("shot-riddle1.png" in pv[1] and "shot-keyT.png" in pv[1]):
        errs.append("preview-2 does not show riddles and a key")
    up = open(UPLOAD).read()
    m = re.search(r"^## 1\. Title\s*\n+```\n(.+?)\n```", up, re.M | re.S)
    if not m:
        errs.append("UPLOAD.md: title block not found")
    else:
        title = m.group(1).strip()
        if title != LISTING_TITLE:
            errs.append("UPLOAD.md: title differs from LISTING_TITLE")
        if len(title) > 80:
            errs.append(f"UPLOAD.md: title is {len(title)} chars (max 80)")
        if re.search(SEASONAL, title, re.I):
            errs.append("UPLOAD.md: seasonal word in the title")
    for need in (DISCLOSURE, f"${PRICE}", f"{TOTAL_PAGES} pages", f"{NWORDS} spell-the-word items", f"{NRID} winter riddles"):
        if need not in up:
            errs.append(f"UPLOAD.md: missing '{need}'")
    desc = up.split("## 2. Description")[1].split("## 3.")[0]
    errs += count_claims(desc, "UPLOAD.md")
    sec = up.split("## 5. Page count by section")[1].split("##")[0]
    nums = [int(x) for x in re.findall(r"^- (?!Total)[^\n]*: (\d+)$", sec, re.M)]
    if sum(nums) != TOTAL_PAGES:
        errs.append(f"UPLOAD.md page list sums to {sum(nums)}, PDF has {TOTAL_PAGES}")
    tot = 0
    for l in desc.splitlines():
        mm = re.search(r"\((\d+) pages?\)$", l)
        if l.startswith("• ") and mm:
            tot += int(mm.group(1))
    if tot != TOTAL_PAGES:
        errs.append(f"UPLOAD.md description bullets sum to {tot} pages, PDF has {TOTAL_PAGES}")
    if re.search("|".join(QA_WORDS), up.replace("Q&A", "")):
        errs.append("UPLOAD.md: forbidden claim or internal QA wording")
    for w in UK_SPELLINGS:
        if w in desc.lower():
            errs.append(f"UPLOAD.md: non-US spelling {w}")
    if "Winter" not in up.split("## 4.")[1].split("## 5.")[0]:
        errs.append("UPLOAD.md: the winter tag is missing")
    tj = json.load(open(TPT_JSON))
    tags, subs = set(load_json("TAG-OPTIONS.json")["options"]), set(load_json("SUBJECT-OPTIONS.json"))
    if not 1 <= len(tj["tags"]) <= 6 or any(t not in tags for t in tj["tags"]):
        errs.append(f"tpt.json tags invalid: {tj['tags']}")
    if not 1 <= len(tj["subjects"]) <= 3 or any(s not in subs for s in tj["subjects"]):
        errs.append(f"tpt.json subjects invalid: {tj['subjects']}")
    if not 1 <= len(tj["grades"]) <= 4:
        errs.append("tpt.json grades must be 1-4")
    if tj.get("pages") != TOTAL_PAGES or tj["price"] != PRICE:
        errs.append("tpt.json pages or price mismatch")
    return errs


def check():
    files = [os.path.join(BUILD, "resource.html"), os.path.join(BUILD, "shots.html")]
    if not all(os.path.exists(x) for x in files):
        sys.exit("build html missing: run gen.py first")
    data = inspect_html(files)
    res, shots = data["resource.html"], data["shots.html"]
    res_html = open(files[0]).read()
    errs, nnotes, nitems = verify_content(res_html, res)
    de, ndraw = verify_drawings(res_html)
    errs += de
    errs += ["resource: " + e for e in res["layout"]] + ["shots: " + e for e in shots["layout"]]
    for p in shots["pages"]:
        if p["kind"] != "cover" and p["wms"] != 1:
            errs.append(f"shots: page {p['n']} has {p['wms']} watermarks, expected 1")
    for p in res["pages"]:
        if p["wms"] != 0:
            errs.append(f"resource: page {p['n']} has a watermark")
    for k in PREVIEW_ORDER + ["ref", "spell"]:
        n = SHOT_PAGES[k]
        gap = res["gaps"][n - 1]
        if gap > 105:
            errs.append(f"preview page {k} (page {n}): {gap}px blank above the footer (max 105)")
    errs += verify_files()
    if errs:
        print("CHECK FAILED")
        print("\n".join(" - " + e for e in errs[:80]))
        sys.exit(1)
    print(f"CHECK OK: {nitems} worksheet words ({NWORDS} expected) and {NRID} riddles read back from the drawn staves ({nnotes} notes: letters recomputed from staff lines, clef glyph, "
          f"notehead centres and ledger lines; middle C on its ledger line in both clefs), all letters A-G, level rules, stems and ledger lines; keys equal the worksheets item by item; "
          f"riddle clues hold exactly their own key phrase; reference, spell-it and write-your-own pages; {ndraw} distinct drawings pixel-checked alone on a transparent ground; "
          f"no clipped text, 0.3 in clear margin on every PDF page; PDF {TOTAL_PAGES} Letter pages, preview 4 (one watermark each), fonts embedded; "
          f"cover and previews 2000x2000 with clear edges; counts, cross-references, UPLOAD.md and tpt.json agree.")


if __name__ == "__main__":
    if "--check" in sys.argv:
        check()
    else:
        build()
