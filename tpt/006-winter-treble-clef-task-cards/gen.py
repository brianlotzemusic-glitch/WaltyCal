#!/usr/bin/env python3
"""Treble Clef Note-Name Task Cards, Winter Edition (TpT 006): build the resource and verify it.

    python3 gen.py            build everything (PDFs, PNGs, tpt.json) into this folder
    python3 gen.py --lowres   same, but square images at scale 1 (self-check only; --check rejects them)
    python3 gen.py --check    verify notes, keys, pages, fonts and files

Grades 2-5. 72 task cards in three levels, plus a student reference page, three
recording sheets, three worksheets and answer keys:

    Level A  one note per card, on the staff only (E4-F5), 3 answer choices (clip cards)
    Level B  three notes per card, D4-G5 (adds the space below and above the staff)
    Level C  "spell the word": 3-7 notes per card, C4-A5 (adds the ledger-line C and A)

Musical accuracy is checked end to end: every staff gets drawn to SVG, the SVG is
parsed back (staff lines, clef, noteheads, ledger lines, stems) and each notehead's
height is turned into a pitch from the staff geometry alone. That pitch must equal
the answer printed on the card, the recording-sheet key and the answer-key pages.

Notation uses Bravura (SMuFL) through item 001's notation.py; winter art (snowflake,
mitten, knit hat) comes from item 003's art.py. Non-denominational, no songs.
Rendering uses Playwright + Chromium through ../tools/render.js, fonts from ../fonts.
"""
import importlib.util
import json
import os
import random
import re
import subprocess
import sys
from html import escape

HERE = os.path.dirname(os.path.abspath(__file__))
TPT = os.path.dirname(HERE)


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, os.path.join(TPT, rel))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


N = _load("notation001", "001-halloween-color-by-note/notation.py")
A3 = _load("art003", "003-winter-rhythm-bingo/art.py")
art = A3.art

FONTS = os.path.join(TPT, "fonts")
BUILD = os.path.join(HERE, "build")
RENDER_JS = os.path.join(TPT, "tools", "render.js")

SLUG = "winter-treble-clef-task-cards"
PDF = os.path.join(HERE, f"{SLUG}.pdf")
PREVIEW_PDF = os.path.join(HERE, f"{SLUG}-PREVIEW.pdf")
COVER_PNG = os.path.join(HERE, "cover.png")
PREVIEW_PNGS = [os.path.join(HERE, f"preview-{i}.png") for i in (1, 2, 3)]
UPLOAD = os.path.join(HERE, "UPLOAD.md")
TPT_JSON = os.path.join(HERE, "tpt.json")

STORE = "Brian Lotze"      # copyright holder
BRAND = "Hudson Beat"      # store line on covers and previews (owner, 4 Oct)
YEAR = 2026
ACCENT = "#3A86C8"         # this product's single accent (icy winter blue)
TITLE = "Treble Clef Task Cards"
PRICE = "4.00"
LOW_RES = "--lowres" in sys.argv

BANNED = ("christmas", "xmas", "santa", "hanukkah", "chanukah", "kwanzaa", "nativity", "jesus", "holiday", "advent",
          "reindeer", "jingle", "carol", "menorah", "elf", "elves")

# ---------------------------------------------------------------- the content
STAFF_ONLY = ["E4", "F4", "G4", "A4", "B4", "C5", "D5", "E5", "F5"]          # Level A
LEVEL_B_RANGE = ["D4"] + STAFF_ONLY + ["G5"]                                  # Level B
OCTAVES = {"C": ["C5", "C4"], "D": ["D4", "D5"], "E": ["E4", "E5"], "F": ["F4", "F5"],   # Level C: rotate through these
           "G": ["G4", "G5"], "A": ["A4", "A5"], "B": ["B4"]}
CARD_WORDS = ["ACE", "AGE", "BAG", "BED", "BEE", "CAB", "CAGE", "DAD", "EGG", "FACE", "FADE", "BEAD",
              "BADGE", "CAFE", "BEEF", "FEED", "ADD", "EDGE", "FED", "ACED", "BAGGED", "DECADE", "CABBAGE", "BAGGAGE"]
WS_C_WORDS = ["BEG", "DEED", "EBB", "DAB", "AGED", "CAGED", "FACED", "FADED", "BEADED", "ADDED"]


def spell(words, counters):
    out = []
    for w in words:
        ps = []
        for ch in w:
            opts = OCTAVES[ch]
            ps.append(opts[counters[ch] % len(opts)])
            counters[ch] += 1
        out.append(ps)
    return out


def make_content():
    rnd = random.Random(6006)
    # Level A: every staff note 2-3 times, shuffled with no repeat next to each other
    while True:
        a = (STAFF_ONLY * 3)[:24]
        rnd.shuffle(a)
        if all(a[i] != a[i + 1] for i in range(23)):
            break
    # Level B: 3 notes per card, no repeated note inside a card, every pitch used
    while True:
        b = [rnd.sample(LEVEL_B_RANGE, 3) for _ in range(24)]
        if {p for c in b for p in c} == set(LEVEL_B_RANGE) and sum(c.count("D4") + c.count("G5") for c in b) >= 8:
            break
    counters = {k: 0 for k in OCTAVES}
    c = spell(CARD_WORDS, counters)
    # Level A clip-card choices: the answer plus its two staff neighbours (the usual mix-ups), answer spot rotated
    choices = []
    spots = [0, 1, 2] * 8
    rnd.shuffle(spots)
    for p, spot in zip(a, spots):
        letter = p[0]
        i = "CDEFGAB".index(letter)
        near = ["CDEFGAB"[(i - 1) % 7], "CDEFGAB"[(i + 1) % 7]]
        rnd.shuffle(near)
        ch = near[:]
        ch.insert(spot, letter)
        choices.append(ch)
    # worksheets
    ws_a = []
    while len(ws_a) < 16:
        p = rnd.choice(STAFF_ONLY)
        if not ws_a or ws_a[-1] != p:
            ws_a.append(p)
    ws_b = [rnd.sample(LEVEL_B_RANGE, 3) for _ in range(8)]
    ws_c = spell(WS_C_WORDS, {k: 1 for k in OCTAVES})       # start on the other octave so the sheet differs from the cards
    return a, choices, b, c, ws_a, ws_b, ws_c


LEVEL_A, CHOICES, LEVEL_B, LEVEL_C, WS_A, WS_B, WS_C = make_content()
LINE_NOTES = ["E4", "G4", "B4", "D5", "F5"]
SPACE_NOTES = ["F4", "A4", "C5", "E5"]
WS_B_LINES = LINE_NOTES
WS_B_SPACES = SPACE_NOTES

# ---------------------------------------------------------------- notation
S_CARD = 6.4


def staff_svg(pitches, x0, yb, s, length, head="quarter", start=4.1, labels=None, label_fill=ACCENT, numbers=False,
              blanks=False, color="#000"):
    """A treble staff (clef + notes) with its bottom line at yb. Returns (svg, note centre xs)."""
    out = []
    for i in range(5):
        y = yb - i * s
        out.append(f'<line x1="{x0:.2f}" y1="{y:.2f}" x2="{x0 + length:.2f}" y2="{y:.2f}" stroke="#000" '
                   f'stroke-width="{N.STAFF_W * s:.2f}"/>')
    out.append(N.glyph("gClef", x0 + 0.25 * s, yb - s, s))
    area0 = x0 + start * s
    area = length - start * s - 0.6 * s
    gap = area / max(1, len(pitches))
    hw = N.GLYPH["noteheadWhole" if head == "whole" else "noteheadBlack"][2][0] * s
    xs = []
    for i, p in enumerate(pitches):
        cx = area0 + gap * (i + 0.5)
        out.append(N.note_svg(p, "treble", cx - hw / 2, yb, s, head))
        xs.append(cx)
        if labels is not None:
            out.append(f'<text x="{cx:.2f}" y="{yb + 4.4 * s:.2f}" font-family="Oswald" font-weight="700" font-size="{2.3 * s:.2f}" '
                       f'text-anchor="middle" fill="{label_fill}">{labels[i]}</text>')
        elif blanks:
            out.append(f'<line x1="{cx - 1.3 * s:.2f}" y1="{yb + 4.4 * s:.2f}" x2="{cx + 1.3 * s:.2f}" y2="{yb + 4.4 * s:.2f}" '
                       f'stroke="#000" stroke-width="0.9" class="blank"/>')
        if numbers:
            out.append(f'<text x="{cx:.2f}" y="{yb + 4.2 * s:.2f}" font-family="Oswald" font-weight="500" font-size="{1.5 * s:.2f}" '
                       f'text-anchor="middle" fill="#777">{i + 1}</text>')
    return "".join(out), xs


# ---------------------------------------------------------------- the accuracy check (reads the drawn SVG back)
LETTERS = "CDEFGAB"


def pitch_from_step(step):
    """Independent of notation.py: the bottom treble line is E4, and each half-space is one letter up."""
    k = LETTERS.index("E") + step
    return f"{LETTERS[k % 7]}{4 + k // 7}"


def read_staff(svgtxt, s):
    """Parse a staff drawn by staff_svg back into pitches, using only the drawn geometry."""
    errs = []
    lines = [(float(a), float(b), float(c), float(d), w) for a, b, c, d, w in
             re.findall(r'<line x1="([-\d.]+)" y1="([-\d.]+)" x2="([-\d.]+)" y2="([-\d.]+)" stroke="#000" stroke-width="([\d.]+)"/>', svgtxt)]
    staff = sorted({round(l[1], 2) for l in lines if l[4] == f"{N.STAFF_W * s:.2f}" and abs(l[1] - l[3]) < 0.01})
    if len(staff) != 5:
        return None, [f"found {len(staff)} staff lines"]
    gaps = [staff[i + 1] - staff[i] for i in range(4)]
    sp = sum(gaps) / 4
    if max(gaps) - min(gaps) > 0.05:
        errs.append("staff lines unevenly spaced")
    yb = staff[-1]
    clefs = re.findall(r'<text x="([\d.]+)" y="([\d.]+)" font-family="Bravura" font-size="([\d.]+)" fill="[^"]+">&#xE050;</text>', svgtxt)
    if len(clefs) != 1 or abs(float(clefs[0][1]) - (yb - sp)) > 0.05:
        errs.append("treble clef is not sitting on the G line (line 2)")
    if any(g in svgtxt for g in ("&#xE062;", "&#xE05C;")):
        errs.append("a non-treble clef is drawn")
    heads = [(float(x), float(y), g) for x, y, g in
             re.findall(r'<text x="([\d.]+)" y="([\d.]+)" font-family="Bravura" font-size="[\d.]+" fill="[^"]+">&#x(E0A4|E0A2);</text>', svgtxt)]
    heads.sort()
    ledgers = [l for l in lines if l[4] == f"{N.LEDGER_W * s:.2f}"]
    stems = [l for l in lines if l[4] == f"{N.STEM_W * s:.2f}"]
    pitches = []
    for hx, hy, g in heads:
        st = (yb - hy) / (sp / 2)
        if abs(st - round(st)) > 0.02:
            errs.append(f"notehead at y={hy} is between a line and a space")
        st = round(st)
        p = pitch_from_step(st)
        pitches.append(p)
        hw = (1.18 if g == "E0A4" else 1.688) * sp
        mine = sorted(round((yb - l[1]) / (sp / 2)) for l in ledgers if l[0] < hx + hw / 2 < l[2])
        want = sorted(list(range(-2, st - 1, -2)) if st <= -2 else list(range(10, st + 1, 2)) if st >= 10 else [])
        if mine != want:
            errs.append(f"{p}: ledger lines at steps {mine}, should be {want}")
        if g == "E0A4":
            st_lines = [l for l in stems if hx - 0.3 < l[0] < hx + hw + 0.3]
            if len(st_lines) != 1:
                errs.append(f"{p}: {len(st_lines)} stems")
            else:
                l = st_lines[0]
                up = min(l[1], l[3]) < hy - sp
                if up != (st < 4):
                    errs.append(f"{p}: stem {'up' if up else 'down'}; notes below the middle line take stems up, others down")
                if abs(abs(l[1] - l[3]) - 3.5 * sp) > 0.6 * sp:
                    errs.append(f"{p}: stem length off")
                if up and abs(l[0] - (hx + hw)) > 0.15 * sp or (not up) and abs(l[0] - hx) > 0.15 * sp:
                    errs.append(f"{p}: stem on the wrong side of the notehead")
    return pitches, errs


# ---------------------------------------------------------------- html scaffolding (from 005)
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
.h { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; letter-spacing: .01em; line-height: 1; }
.l { font-family: 'Oswald'; font-weight: 300; }
.top { display: flex; justify-content: space-between; align-items: flex-end; border-bottom: 2.2pt solid #000; padding-bottom: 6pt; }
.top .t { font-size: 25pt; }
.top .t small { display: block; font-family: 'Oswald'; font-weight: 300; text-transform: none; font-size: 12pt; letter-spacing: 0; margin-top: 4pt; }
.tag { text-align: right; }
.tag .lv { display: inline-block; background: #000; color: #fff; font-family: 'Oswald'; font-weight: 700; font-size: 15pt; padding: 3pt 9pt 4pt; border-radius: 4pt; letter-spacing: .04em; }
.tag .lv.ak { background: ACCENT; }
.tag .ln { font-family: 'Oswald'; font-weight: 300; font-size: 11pt; margin-top: 3pt; }
.name { display: flex; gap: 18pt; font-size: 12pt; margin: 9pt 0 5pt; }
.name span { flex: 1; border-bottom: 1pt solid #000; height: 15pt; }
.name span.d { flex: 0 0 1.6in; }
.how { font-size: 11pt; margin: 7pt 0 6pt; }
.main { flex: 1; display: flex; flex-direction: column; }
.foot { display: flex; justify-content: space-between; font-size: 8.5pt; color: #333; border-top: .8pt solid #000; padding-top: 3pt; }
.wm { position: absolute; left: 50%; top: 50%; transform: translate(-50%, -50%) rotate(-38deg); font-family: 'Oswald'; font-weight: 700;
      font-size: 150pt; color: rgba(0,0,0,.13); letter-spacing: .06em; white-space: nowrap; pointer-events: none; z-index: 9; }
.doc h1 { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 30pt; margin: 0 0 4pt; line-height: 1; }
.doc h2, .sec { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 13.5pt; margin: 10pt 0 4pt; letter-spacing: .02em; }
.doc h2 .acc, .sec .acc { color: ACCENT; }
.doc p, .doc li { font-size: 10.6pt; line-height: 1.32; margin: 0 0 4pt; }
.doc ul, .doc ol { margin: 0 0 4pt; padding-left: 15pt; }
.doc .rule { border-bottom: 2.2pt solid #000; margin-bottom: 6pt; padding-bottom: 6pt; }
.doc table { border-collapse: collapse; width: 100%; font-size: 10pt; margin: 2pt 0 4pt; }
.doc td, .doc th { border: 1pt solid #000; padding: 2.4pt 5pt; text-align: left; vertical-align: middle; }
.doc th, .tb th { font-family: 'Oswald'; font-weight: 500; text-transform: uppercase; font-size: 9.5pt; background: #000; color: #fff;
                  letter-spacing: .04em; }
.cols { display: flex; gap: 22pt; }
.cols > div { flex: 1; min-width: 0; }
.small { font-size: 9pt !important; color: #333; }
.box { border: 1.4pt solid #000; border-radius: 8pt; padding: 8pt 11pt; }
.grid { display: grid; grid-template-columns: 1fr 1fr; gap: 9pt 12pt; margin-top: 10pt; justify-items: center; }
.cards { flex: 1; display: flex; flex-direction: column; justify-content: center; }
.rec { display: grid; grid-template-columns: repeat(4, 1fr); gap: 0; border-top: 1.2pt solid #000; border-left: 1.2pt solid #000; margin-top: 8pt; }
.rec > div { border-right: 1.2pt solid #000; border-bottom: 1.2pt solid #000; height: 92pt; padding: 5pt 7pt; position: relative; }
.rec .n { display: inline-block; background: #000; color: #fff; font-family: 'Oswald'; font-weight: 700; font-size: 10.5pt;
          padding: 1pt 6pt 2pt; border-radius: 3pt; letter-spacing: .03em; }
.rec .ans { position: absolute; left: 7pt; right: 7pt; bottom: 9pt; display: flex; gap: 8pt; justify-content: center; }
.rec .ans span { flex: 1; border-bottom: 1.1pt solid #000; height: 30pt; text-align: center; font-family: 'Oswald'; font-weight: 700;
                 font-size: 22pt; color: ACCENT; line-height: 30pt; }
.ws { display: grid; gap: 10pt 14pt; margin-top: 6pt; }
.ws > div { border: 1.3pt solid #000; border-radius: 8pt; padding: 4pt 6pt 6pt; position: relative; }
.ws .n { position: absolute; left: 6pt; top: 4pt; font-family: 'Oswald'; font-weight: 700; font-size: 11pt; }
.ls { display: flex; justify-content: center; gap: 8pt; font-family: 'Oswald'; font-weight: 500; font-size: 9pt; letter-spacing: .06em; }
.ls span { padding: 1pt 6pt; border: 1.2pt solid transparent; border-radius: 9pt; }
.ls span.on { border-color: ACCENT; color: ACCENT; font-weight: 700; }
.keyt { border-collapse: collapse; width: 100%; table-layout: fixed; }
.keyt td { border-bottom: .8pt solid #bbb; padding: 2.2pt 6pt; font-size: 11pt; }
.keyt td.c { font-family: 'Oswald'; font-weight: 700; width: 34pt; }
.keyt td.a { font-family: 'Oswald'; font-weight: 700; color: ACCENT; font-size: 12.5pt; letter-spacing: .08em; }
.keyt th { font-family: 'Oswald'; font-weight: 700; background: #000; color: #fff; text-transform: uppercase; font-size: 12pt; padding: 3pt 6pt;
           letter-spacing: .05em; text-align: left; }
.cover { align-items: center; justify-content: space-between; padding: 0.55in 0.6in 0.5in; }
.store { font-family: 'Oswald'; font-weight: 500; font-size: 13pt; letter-spacing: .32em; text-transform: uppercase; }
.ctitle { text-align: center; }
.ctitle .a { font-family: 'Oswald'; font-weight: 700; font-size: 44pt; line-height: 1; letter-spacing: .02em; }
.ctitle .b { white-space: nowrap; font-family: 'Oswald'; font-weight: 700; font-size: 72pt; line-height: .95; letter-spacing: .01em; }
.ctitle .c { font-family: 'Oswald'; font-weight: 300; font-size: 16pt; margin-top: 8pt; }
.cband { width: 100%; background: #000; color: #fff; text-align: center; font-family: 'Oswald'; font-weight: 500; font-size: 14pt;
         letter-spacing: .08em; text-transform: uppercase; padding: 8pt 0 9pt; border-radius: 4pt; }
.cband em { font-style: normal; color: ACCENT; }
""".replace("ACCENT", ACCENT)


def html_doc(pages, title="doc"):
    return (f'<!doctype html><html><head><meta charset="utf-8"><title>{escape(title)}</title>'
            f'<style>{font_css()}{CSS}</style></head><body>{"".join(pages)}</body></html>')


COPY = f"© {YEAR} {STORE} · {BRAND} · For single-classroom use"


def foot(right):
    return f'<div class="foot"><span>{COPY}</span><span>{right}</span></div>'


def top(sub, tag, tagsub, ak=False, title=TITLE):
    return (f'<div class="top"><div class="h t">{escape(title)}<small>{sub}</small></div>'
            f'<div class="tag"><div class="lv{" ak" if ak else ""}">{tag}</div><div class="ln">{tagsub}</div></div></div>')


NAME = '<div class="name">Name<span></span>Date<span class="d"></span></div>'


def wm(on):
    return '<div class="wm">PREVIEW</div>' if on else ""


def svg(w, h, body, style="display:block"):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}pt" height="{h}pt" viewBox="0 0 {w} {h}" style="{style}">{body}</svg>'


def text(x, y, s, size, weight=700, family="Oswald", anchor="middle", fill="#000", upper=False, extra=""):
    t = escape(s.upper() if upper else s)
    family = f"'{family}'" if " " in family else family
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{family}" font-weight="{weight}" font-size="{size}" '
            f'text-anchor="{anchor}" fill="{fill}" {extra}>{t}</text>')


def page(sub, tag, tagsub, inner, n, watermark=False, name=False, ak=False, right=None):
    r = f"Page {n}" if right is None else f"{right} · Page {n}"
    return (f'<section class="page">{wm(watermark)}{top(sub, tag, tagsub, ak=ak)}{NAME if name else ""}'
            f'<div class="main">{inner}</div>{foot(r)}</section>')


# ---------------------------------------------------------------- plan and page index
PLAN = ["cover", "teacher", "reference", "cards_a1", "cards_a2", "cards_a3", "cards_b1", "cards_b2", "cards_b3",
        "cards_c1", "cards_c2", "cards_c3", "rec_a", "rec_b", "rec_c", "ws_a", "ws_b", "ws_c",
        "key_cards", "key_ws_a", "key_ws_b", "key_ws_c", "terms"]
IX = {k: i + 1 for i, k in enumerate(PLAN)}

PARTS = [  # (label, first key, last key, use)
    ("Note-name reference", "reference", "reference", "lines, spaces, ledger C and A"),
    ("Level A task cards 1–24", "cards_a1", "cards_a3", "one note, staff only, 3 choices"),
    ("Level B task cards 1–24", "cards_b1", "cards_b3", "three notes, D below to G above"),
    ("Level C task cards 1–24", "cards_c1", "cards_c3", "spell a word, ledger C and A"),
    ("Recording sheets A, B, C", "rec_a", "rec_c", "one per level"),
    ("Worksheets A, B, C", "ws_a", "ws_c", "one per level"),
    ("Answer keys", "key_cards", "key_ws_c", "all cards + all worksheets"),
    ("Terms of use", "terms", "terms", "license and credits"),
]


def prange(a, b):
    return str(IX[a]) if a == b else f"{IX[a]}–{IX[b]}"


LEVELS = {
    "A": {"cards": LEVEL_A, "range": "E to F, on the staff", "prompt": "What is the note name?"},
    "B": {"cards": LEVEL_B, "range": "D below to G above the staff", "prompt": "Name all 3 notes, in order."},
    "C": {"cards": LEVEL_C, "range": "low C to high A (ledger lines)", "prompt": "Name the notes to spell a word."},
}


def answers(level):
    cards = LEVELS[level]["cards"]
    if level == "A":
        return [p[0] for p in cards]
    if level == "B":
        return [" ".join(p[0] for p in c) for c in cards]
    return ["".join(p[0] for p in c) for c in cards]


def card_pitches(level, i):
    c = LEVELS[level]["cards"][i]
    return [c] if level == "A" else c


# ---------------------------------------------------------------- task cards
CW, CH = 258, 150
CARD_ART = [("snowflake", {"line": ACCENT}), ("mitten", {"fill": ACCENT}), ("snowflake", {"line": "#000"}), ("hat", {"fill": ACCENT})]


def card_staff(level, i, x0=None, yb=86):
    ps = card_pitches(level, i)
    length = {"A": 150, "B": 196, "C": 120 + 15 * len(ps)}[level]
    length = min(length, CW - 24)
    x0 = (CW - length) / 2 if x0 is None else x0
    return staff_svg(ps, x0, yb, S_CARD, length, numbers=(level == "B"), blanks=(level == "C"))


def card_svg(level, i, accent=ACCENT):
    num = f"{level}{i + 1}"
    pic, kw = CARD_ART[i % 4]
    st, _ = card_staff(level, i)
    out = [f'<rect x="1" y="1" width="{CW - 2}" height="{CH - 2}" rx="10" fill="#fff" stroke="#000" stroke-width="1.6"/>',
           f'<rect x="10" y="10" width="{18 + 7.2 * len(num)}" height="20" rx="4" fill="#000"/>',
           text(19 + 3.6 * len(num), 25, num, 13, 700, fill="#fff", extra='letter-spacing="0.03em"'),
           text(52 + 7.2 * (len(num) - 2), 24.5, LEVELS[level]["prompt"], 10.5, 600, family="Source Sans 3", anchor="start"),
           art(pic, CW - 36, 7, 26, 1.3, **kw), st]
    if level == "A":
        for k, ch in enumerate(CHOICES[i]):
            cx = CW / 2 + (k - 1) * 62
            out.append(f'<rect x="{cx - 23}" y="112" width="46" height="26" rx="13" fill="#fff" stroke="#000" stroke-width="1.4"/>')
            out.append(text(cx, 131, ch, 17, 700))
    elif level == "B":
        out.append(text(CW / 2, 138, "Write the 3 letters on your recording sheet.", 8.5, 400, family="Source Sans 3", fill="#555"))
    else:
        out.append(text(CW / 2, 140, "One letter for each note.", 8.5, 400, family="Source Sans 3", fill="#555"))
    return svg(CW, CH, "".join(out))


def cards_page(level, k, n, watermark=False):
    lo = k * 8
    cards = "".join(card_svg(level, i) for i in range(lo, lo + 8))
    inner = f'<div class="cards"><div class="grid">{cards}</div></div>'
    return page(f"Level {level} · {LEVELS[level]['range']} · cut on the outlines", f"LEVEL {level}", f"Cards {lo + 1}–{lo + 8}",
                inner, n, watermark, right=f"Answer key on page {IX['key_cards']}")


# ---------------------------------------------------------------- reference page
def reference_page(n):
    s = 9.5
    big, _ = staff_svg(N.CLEFS["treble"]["range"], 10, 70, s, 520, head="whole", labels=[p[0] for p in N.CLEFS["treble"]["range"]],
                       label_fill="#000")
    lines, _ = staff_svg(LINE_NOTES, 6, 58, 8, 250, head="whole", labels=[p[0] for p in LINE_NOTES])
    spaces, _ = staff_svg(SPACE_NOTES, 6, 58, 8, 250, head="whole", labels=[p[0] for p in SPACE_NOTES])
    ledg, _ = staff_svg(["C4", "D4", "G5", "A5"], 6, 64, 8, 250, head="whole", labels=["C", "D", "G", "A"])
    deco = (art("snowflake", 0, 0, 40, 1.5, line=ACCENT) + art("mitten", 50, 2, 40, 1.5, fill=ACCENT) + art("snowflake", 100, 0, 40, 1.5))
    inner = (f'<div class="how">Keep this page next to the task cards. Every note sits <b>on a line</b> (the line runs through it) or '
             f'<b>in a space</b> (between two lines).</div>'
             f'<div class="box" style="margin-top:4pt"><div class="sec" style="margin-top:0">The treble staff, low C to high A<span class="acc"> ·</span></div>'
             f'{svg(540, 112, big, "display:block;margin:0 auto")}</div>'
             f'<div class="cols" style="margin-top:12pt;gap:16pt">'
             f'<div class="box"><div class="sec" style="margin-top:0">Line notes<span class="acc"> ·</span></div>'
             f'{svg(262, 92, lines)}<p style="font-size:11pt;margin:2pt 0 0">Bottom to top: <b>E G B D F</b><br>'
             f'“<b>E</b>very <b>G</b>ood <b>B</b>ird <b>D</b>oes <b>F</b>ly”</p></div>'
             f'<div class="box"><div class="sec" style="margin-top:0">Space notes<span class="acc"> ·</span></div>'
             f'{svg(262, 92, spaces)}<p style="font-size:11pt;margin:2pt 0 0">Bottom to top: <b>F A C E</b><br>'
             f'The spaces spell “<b>FACE</b>”, like a face in the snow.</p></div></div>'
             f'<div class="cols" style="margin-top:12pt;gap:16pt">'
             f'<div class="box"><div class="sec" style="margin-top:0">Just outside the staff<span class="acc"> ·</span></div>'
             f'{svg(262, 98, ledg)}<p style="font-size:11pt;margin:2pt 0 0"><b>D</b> hangs under the bottom line and <b>G</b> sits on top. '
             f'<b>Low C</b> and <b>high A</b> sit on their own short line, a <i>ledger line</i>.</p></div>'
             f'<div class="box"><div class="sec" style="margin-top:0">Tips<span class="acc"> ·</span></div>'
             f'<ul style="margin:0;padding-left:14pt;font-size:11pt;line-height:1.35">'
             f'<li>The treble clef curls around the <b>G line</b> (line 2). It is also called the G clef.</li>'
             f'<li>Count up or down from a note you know. Each step from a line to the next space is the next letter.</li>'
             f'<li>The music alphabet only uses A B C D E F G, then starts again at A.</li></ul>'
             f'<div style="margin-top:8pt">{svg(140, 42, deco)}</div></div></div>')
    return page("Student reference · lines and spaces", "REFERENCE", "Keep it handy", inner, n)


# ---------------------------------------------------------------- recording sheets
def rec_page(level, n, key=False, watermark=False):
    ans = answers(level)
    cells = []
    for i in range(24):
        if level == "B":
            slots = "".join(f"<span>{ans[i].split()[k] if key else ''}</span>" for k in range(3))
        else:
            slots = f"<span>{ans[i] if key else ''}</span>"
        cells.append(f'<div><span class="n">{level}{i + 1}</span><div class="ans">{slots}</div></div>')
    how = {"A": "Find the card's number, name the note, and write its letter in the box.",
           "B": "Write the three note names in order, one letter on each line.",
           "C": "Name each note and write the word it spells."}[level]
    inner = f'<div class="how">{how}</div><div class="rec">{"".join(cells)}</div>'
    return page(f"Recording sheet · Level {level} task cards", f"LEVEL {level}", "Recording sheet", inner, n, watermark,
                name=True, right=f"Answer key on page {IX['key_cards']}")


# ---------------------------------------------------------------- worksheets
def ws_a_page(n, key=False, watermark=False):
    cells = []
    for i, p in enumerate(WS_A):
        st, _ = staff_svg([p], 6, 52, 6.6, 96)
        on_line = p in LINE_NOTES
        lab = f'<span class="{"on" if key and on_line else ""}">LINE</span><span class="{"on" if key and not on_line else ""}">SPACE</span>'
        blank = (f'<div style="text-align:center;font-family:Oswald;font-weight:700;font-size:20pt;color:{ACCENT};height:26pt;'
                 f'border-bottom:1.1pt solid #000;width:40pt;margin:0 auto 4pt;line-height:26pt">{p[0] if key else ""}</div>')
        cells.append(f'<div><span class="n">{i + 1}</span>{svg(108, 72, st, "display:block;margin:0 auto")}{blank}<div class="ls">{lab}</div></div>')
    inner = (f'<div class="how">Write the letter name of each note. Then circle <b>LINE</b> or <b>SPACE</b>.</div>'
             f'<div class="ws" style="grid-template-columns:repeat(4,1fr)">{"".join(cells)}</div>'
             f'<div class="box" style="margin-top:12pt;display:flex;gap:14pt;align-items:center">'
             f'<b style="font-family:Oswald;font-size:12pt;text-transform:uppercase">Snowy challenge</b>'
             f'<span style="font-size:11pt">How many of your notes were on a line? {_blank(0.5, str(sum(p in LINE_NOTES for p in WS_A)) if key else "")} '
             f'In a space? {_blank(0.5, str(sum(p in SPACE_NOTES for p in WS_A)) if key else "")}</span></div>')
    if key:
        return page("Worksheet A answer key", "ANSWER KEY", "Worksheet A", inner, n, watermark, ak=True)
    return page("Worksheet A · lines and spaces", "LEVEL A", "Worksheet", inner, n, watermark, name=True,
                right=f"Answer key on page {IX['key_ws_a']}")


def _blank(w_in, val=""):
    return (f'<span style="display:inline-block;width:{w_in}in;border-bottom:1pt solid #000;text-align:center;font-family:Oswald;'
            f'font-weight:700;color:{ACCENT};font-size:13pt">{val or "&nbsp;"}</span>')


def ws_b_page(n, key=False, watermark=False):
    cells = []
    for i, ps in enumerate(WS_B):
        st, _ = staff_svg(ps, 10, 54, 7, 210, labels=[p[0] for p in ps] if key else None, blanks=not key)
        cells.append(f'<div><span class="n">{i + 1}</span>{svg(230, 92, st, "display:block;margin:0 auto")}</div>')
    lines, _ = staff_svg(WS_B_LINES, 8, 50, 7, 230, head="whole", labels=[p[0] for p in WS_B_LINES] if key else None, blanks=not key)
    spaces, _ = staff_svg(WS_B_SPACES, 8, 50, 7, 230, head="whole", labels=[p[0] for p in WS_B_SPACES] if key else None, blanks=not key)
    inner = (f'<div class="how">Write the letter name under each note.</div>'
             f'<div class="ws" style="grid-template-columns:1fr 1fr">{"".join(cells)}</div>'
             f'<div class="sec" style="margin-top:12pt">Lines and spaces<span class="acc"> ·</span></div>'
             f'<div class="cols" style="gap:14pt"><div class="box" style="padding:4pt 6pt"><div class="small" style="font-weight:600">The LINE notes, bottom to top</div>'
             f'{svg(250, 86, lines)}</div>'
             f'<div class="box" style="padding:4pt 6pt"><div class="small" style="font-weight:600">The SPACE notes, bottom to top</div>{svg(250, 86, spaces)}</div></div>')
    if key:
        return page("Worksheet B answer key", "ANSWER KEY", "Worksheet B", inner, n, watermark, ak=True)
    return page("Worksheet B · D below to G above", "LEVEL B", "Worksheet", inner, n, watermark, name=True,
                right=f"Answer key on page {IX['key_ws_b']}")


def ws_c_page(n, key=False, watermark=False):
    cells = []
    for i, ps in enumerate(WS_C):
        w = "".join(p[0] for p in ps)
        st, _ = staff_svg(ps, 8, 47, 6.6, 214, labels=list(w) if key else None, blanks=not key)
        word = (f'<div style="display:flex;align-items:flex-end;gap:6pt;margin:0 6pt 2pt"><b style="font-family:Oswald;font-weight:500;'
                f'font-size:9.5pt;letter-spacing:.06em">THE WORD IS</b><span style="flex:1;border-bottom:1.1pt solid #000;height:20pt;'
                f'font-family:Oswald;font-weight:700;font-size:16pt;color:{ACCENT};letter-spacing:.12em;padding-left:6pt">{w if key else ""}</span></div>')
        cells.append(f'<div><span class="n">{i + 1}</span>{svg(230, 76, st, "display:block;margin:0 auto")}{word}</div>')
    inner = (f'<div class="how">Snowy word decoder: name each note, then write the word it spells.</div>'
             f'<div class="ws" style="grid-template-columns:1fr 1fr;gap:6pt 14pt">{"".join(cells)}</div>')
    if key:
        return page("Worksheet C answer key", "ANSWER KEY", "Worksheet C", inner, n, watermark, ak=True)
    return page("Worksheet C · word decoder with ledger lines", "LEVEL C", "Worksheet", inner, n, watermark, name=True,
                right=f"Answer key on page {IX['key_ws_c']}")


# ---------------------------------------------------------------- answer key for the cards
def key_cards_page(n, watermark=False):
    cols = []
    for lv in "ABC":
        ans = answers(lv)
        rows = "".join(f'<tr><td class="c">{lv}{i + 1}</td><td class="a">{a}</td></tr>' for i, a in enumerate(ans))
        cols.append(f'<div><table class="keyt"><tr><th colspan="2">Level {lv}</th></tr>{rows}</table></div>')
    inner = (f'<div class="how">Answers for all 72 task cards. Level A clip cards: the answer is also one of the three choices on the card.</div>'
             f'<div class="cols" style="gap:18pt">{"".join(cols)}</div>')
    return page("Task card answer key · Levels A, B and C", "ANSWER KEY", "Cards A1–C24", inner, n, watermark, ak=True)


# ---------------------------------------------------------------- teacher notes and terms
def teacher_page(n):
    trs = "".join(f"<tr><td><b>{a}</b></td><td style='white-space:nowrap'>{prange(f, l)}</td><td>{u}</td></tr>" for a, f, l, u in PARTS)
    return (f'<section class="page doc"><div class="rule"><h1>Teacher Notes</h1>'
            f'<div class="l" style="font-size:13pt">Treble Clef Note-Name Task Cards, Winter Edition · grades 2–5</div></div>'
            f'<div class="cols"><div>'
            f'<h2>What it is</h2>'
            f'<p>72 winter task cards for reading treble clef note names, in three levels, with a student reference page, '
            f'recording sheets, three worksheets and full answer keys. Snowflakes and mittens, nothing tied to one celebration.</p>'
            f'<h2>The three levels</h2><ul>'
            f'<li><b>Level A</b> (cards A1–A24): one note on the staff, E to F. Three answer choices, so they work as clip cards.</li>'
            f'<li><b>Level B</b> (B1–B24): three notes per card, adding D below and G above the staff.</li>'
            f'<li><b>Level C</b> (C1–C24): name 3–7 notes to spell a word, adding low C and high A on ledger lines.</li></ul>'
            f'<p>Rough guide: Level A for grade 2 or first treble lessons, B for grades 3–4, C for grades 4–5 or fast finishers.</p>'
            f'<h2>Ways to use them</h2><ul>'
            f'<li><b>Scoot / around the room:</b> tape cards around the room; students write answers on their recording sheet.</li>'
            f'<li><b>Clip cards (Level A):</b> students clip a clothespin on the answer. Mark the back with a dot to self-check.</li>'
            f'<li><b>Centers, partners, early finishers, sub days.</b></li>'
            f'<li><b>Quick check:</b> show one card under a document camera as a warm-up or exit ticket.</li></ul>'
            f'<h2>Prep</h2><p>Print the card pages on card stock and cut on the outlines (8 per page). Laminate if you like. '
            f'Print the recording sheets and worksheets on plain paper. Everything prints well in black and white.</p>'
            f'</div><div>'
            f'<h2>What’s inside</h2><table><tr><th>Part</th><th>Pages</th><th>Use</th></tr>{trs}</table>'
            f'<h2>About the notation</h2>'
            f'<p>Every card shows a treble clef and quarter notes engraved with a professional music font. Stems follow the usual rule: '
            f'below the middle line, stems go up; on or above it, stems go down. Each note’s position was checked by computer against '
            f'its answer, and every answer key comes from the same checked data.</p>'
            f'<h2>Standards</h2><p>Supports reading melodic patterns in standard notation (National Core Arts Standards, Music, '
            f'MU:Pr4.2, grades 2–5).</p>'
            f'<h2>Memory aids</h2><p>Lines: <b>E G B D F</b> (“Every Good Bird Does Fly”). Spaces: <b>F A C E</b>. '
            f'Use any saying your students already know.</p>'
            f'<p class="small">All cards, words, art and layouts are original. No songs, lyrics or copyrighted characters are used.</p>'
            f'</div></div><div style="flex:1"></div>{foot(f"Page {n}")}</section>')


def terms_page(n):
    return (f'<section class="page doc"><div class="rule"><h1>Terms of Use</h1>'
            f'<div class="l" style="font-size:13pt">Thank you for your purchase!</div></div>'
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
            f'<li>Art, cards, words and layouts: original work, {BRAND} by {STORE}.</li>'
            f'<li>Music notation font: Bravura © Steinberg Media Technologies GmbH, SIL Open Font License 1.1.</li>'
            f'<li>Text fonts: Oswald (The Oswald Project Authors) and Source Sans 3 (Adobe), SIL Open Font License 1.1.</li></ul>'
            f'<p class="small">Designed with the help of digital and AI tools, and checked by hand.</p>'
            f'<div style="flex:1"></div>{foot(f"Page {n}")}</section>')


# ---------------------------------------------------------------- cover
COVER_WORD = ["F4", "A4", "C5", "E5"]      # the space notes, spelled FACE on the cover


def hero_svg(width_css):
    s = 11
    st, _ = staff_svg(COVER_WORD, 90, 92, s, 420, labels=list("FACE"), label_fill=ACCENT)
    c1 = f'<g transform="translate(40 178) rotate(-5 129 75) scale(1.02)">{_card_body("A", 0)}</g>'
    c2 = f'<g transform="translate(300 182) rotate(4 129 75) scale(1.02)">{_card_body("C", 9)}</g>'
    deco = (art("snowflake", 6, 6, 64, 2.2, line=ACCENT, rotate=10) + art("snowflake", 534, 10, 52, 2.0, rotate=-8)
            + art("mitten", 540, 120, 56, 2.0, fill=ACCENT, rotate=14) + art("snowflake", 12, 112, 38, 1.8))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 348" width="{width_css}" style="display:block">'
            f'{st}{deco}{c1}{c2}</svg>')


def _card_body(level, i):
    full = card_svg(level, i)
    return re.sub(r"^<svg[^>]*>|</svg>$", "", full)


def cover_page():
    return (f'<section class="page cover"><div class="store">{BRAND}</div>'
            f'<div style="width:6.9in">{hero_svg("100%")}</div>'
            f'<div class="ctitle"><div class="a">WINTER TREBLE CLEF</div><div class="b">NOTE NAMES</div>'
            f'<div class="c">72 task cards · lines and spaces · ledger lines · worksheets · answer keys</div></div>'
            f'<div class="cband">Grades 2–5 <em>·</em> 3 levels <em>·</em> 72 cards <em>·</em> {len(PLAN)} pages</div></section>')


# ---------------------------------------------------------------- assemble
def render_page(key, watermark=False):
    n = IX[key]
    if key.startswith("cards_"):
        return cards_page(key[6].upper(), int(key[7]) - 1, n, watermark)
    if key.startswith("rec_"):
        return rec_page(key[4].upper(), n, watermark=watermark)
    return {
        "cover": cover_page, "teacher": lambda: teacher_page(n), "reference": lambda: reference_page(n),
        "ws_a": lambda: ws_a_page(n, watermark=watermark), "ws_b": lambda: ws_b_page(n, watermark=watermark),
        "ws_c": lambda: ws_c_page(n, watermark=watermark), "key_cards": lambda: key_cards_page(n, watermark),
        "key_ws_a": lambda: ws_a_page(n, key=True, watermark=watermark), "key_ws_b": lambda: ws_b_page(n, key=True, watermark=watermark),
        "key_ws_c": lambda: ws_c_page(n, key=True, watermark=watermark), "terms": lambda: terms_page(n),
    }[key]()


PREVIEW_PICKS = ["cards_a1", "cards_b1", "cards_c1", "key_ws_a"]


def preview_pages():
    return [render_page(p, watermark=True) for p in PREVIEW_PICKS]


# ---------------------------------------------------------------- square images (2000 x 2000)
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
       color: rgba(0,0,0,.14); white-space: nowrap; letter-spacing: .06em; }
""".replace("ACCENT", ACCENT)

FONT_PRIME = ('<div style="position:absolute;left:-9999px;font-family:\'Source Sans 3\'">'
              '<span style="font-weight:400">a</span><span style="font-weight:600">a</span>'
              '<i style="font-weight:400">a</i><span style="font-family:Bravura">&#xE0A4;</span></div>')


def sq_doc(body):
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{font_css()}'
            f'html,body{{margin:0;background:#fff}}{SQ_CSS}</style></head><body>{FONT_PRIME}{body}</body></html>')


def cover_square():
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div>'
        f'<div style="width:860px;margin-top:22px">{hero_svg("100%")}</div>'
        f'<div class="hd" style="font-size:64px;margin-top:4px">Winter Treble Clef</div>'
        f'<div class="hd" style="font-size:128px">Note Names</div>'
        f'<div class="sub" style="font-size:29px;margin-top:10px">72 task cards · lines &amp; spaces · ledger lines · answer keys</div>'
        f'<div class="band">Grades 2–5 <em>·</em> 3 levels <em>·</em> {len(PLAN)} pages</div></div>')


def preview_square_1(img):
    items = [(img[0], "Level A", "1 note · 3 choices"), (img[1], "Level B", "3 notes · D to G"),
             (img[2], "Level C", "spell a word · ledger lines")]
    shots = "".join(
        f'<div style="width:290px"><div class="shot"><img src="{src}"><div class="swm" style="font-size:64px">PREVIEW</div></div>'
        f'<div class="lbl">{a}<span>{b}</span></div></div>' for src, a, b in items)
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div>'
        f'<div class="hd" style="font-size:76px;margin-top:20px">3 levels · 72 cards</div>'
        f'<div class="sub" style="font-size:27px;margin-top:8px">From first line-and-space notes to ledger-line word puzzles</div>'
        f'<div style="display:flex;gap:28px;margin-top:70px;align-items:flex-start">{shots}</div>'
        f'<div class="band">Recording sheets <em>·</em> clip cards <em>·</em> scoot <em>·</em> centers</div></div>')


def preview_square_2(a, b):
    pair = "".join(
        f'<div style="position:absolute;left:{x}px;top:{y}px;width:470px"><div class="shot"><img src="{src}">'
        f'<div class="swm" style="font-size:100px">PREVIEW</div></div>'
        f'<div class="lbl" style="position:absolute;{side}:-2px;top:-44px;margin:0">{lab}</div></div>'
        for src, lab, x, y, side in ((a, "Worksheet", 50, 250, "left"), (b, "Answer key", 476, 300, "right")))
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div>'
        f'<div class="hd" style="font-size:72px;margin-top:20px">Checked answer keys</div>'
        f'<div class="sub" style="font-size:27px;margin-top:8px">Every card and worksheet, keyed from note positions checked by computer</div>'
        f'{pair}'
        f'<div class="band">3 worksheets <em>·</em> 3 recording sheets <em>·</em> 4 keys</div></div>')


def preview_square_3(imgs):
    cells = "".join(
        f'<div style="width:196px"><div class="shot" style="box-shadow:5px 5px 0 #000"><img src="{src}">'
        f'<div class="swm" style="font-size:44px">PREVIEW</div></div><div class="lbl" style="font-size:17px;margin-top:9px">{lab}</div></div>'
        for src, lab in imgs)
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div>'
        f'<div class="hd" style="font-size:70px;margin-top:16px">Everything inside</div>'
        f'<div class="sub" style="font-size:27px;margin-top:8px">Reference page, 9 card pages, recording sheets and worksheets</div>'
        f'<div style="display:grid;grid-template-columns:repeat(4,196px);gap:20px 26px;margin-top:34px">{cells}</div>'
        f'<div class="band">{len(PLAN)} pages <em>·</em> US Letter PDF <em>·</em> prints in black &amp; white</div></div>')


SHOTS1 = ["cards_a1", "cards_b2", "cards_c3"]
SHOTS2 = ["ws_b", "key_ws_b"]
SHOTS3 = [("reference", "Reference"), ("cards_a2", "Level A"), ("cards_b3", "Level B"), ("cards_c1", "Level C"),
          ("rec_a", "Recording sheet"), ("ws_a", "Worksheet A"), ("ws_c", "Worksheet C"), ("key_cards", "Card key")]


# ---------------------------------------------------------------- render
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


def write(name, txt):
    p = os.path.join(BUILD, name)
    with open(p, "w") as f:
        f.write(txt)
    return p


def tpt_json(pages):
    return {
        "price": PRICE, "license_price": PRICE,
        "tax_code": "Other Digital Goods - No Physical Media",
        "grades": ["2nd-grade", "3rd-grade", "4th-grade", "5th-grade"],
        "subjects": ["Music"],
        "tags": ["Winter"],
        "formats": ["PDF"],
        "pages": pages,
        "answer_key": "Included",
        "files": {"product": f"{SLUG}.pdf", "preview": f"{SLUG}-PREVIEW.pdf", "thumb1": "cover.png",
                  "thumb2": "preview-1.png", "thumb3": "preview-2.png", "thumb4": "preview-3.png"},
    }


def pdf_png(src, page_no, out, res=110):
    subprocess.run(["pdftoppm", "-png", "-r", str(res), "-f", str(page_no), "-l", str(page_no), "-singlefile", src,
                    os.path.join(BUILD, out)], check=True)


def build():
    os.makedirs(BUILD, exist_ok=True)
    problems = verify_data()
    if problems:
        print("\n".join(problems))
        sys.exit("data check failed; not rendering")
    full = write("resource.html", html_doc([render_page(p) for p in PLAN], TITLE))
    prev = write("preview.html", html_doc(preview_pages(), "Preview"))
    render([{"html": full, "pdf": PDF}, {"html": prev, "pdf": PREVIEW_PDF}])
    res = 50 if LOW_RES else 110
    for key in set(SHOTS1 + SHOTS2 + [k for k, _ in SHOTS3]):
        pdf_png(PDF, IX[key], key, res if key not in dict(SHOTS3) else (40 if LOW_RES else 80))
    sq = [write("cover.html", cover_square()), write("p1.html", preview_square_1([f"{k}.png" for k in SHOTS1])),
          write("p2.html", preview_square_2(*[f"{k}.png" for k in SHOTS2])),
          write("p3.html", preview_square_3([(f"{k}.png", lab) for k, lab in SHOTS3]))]
    render([{"html": h, "png": o, "width": 1000, "height": 1000, "scale": 1 if LOW_RES else 2}
            for h, o in zip(sq, [COVER_PNG] + PREVIEW_PNGS)])
    with open(TPT_JSON, "w") as f:
        json.dump(tpt_json(len(PLAN)), f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"built {PDF} ({len(PLAN)} pages), {PREVIEW_PDF}, cover + 3 previews, tpt.json" + (" [LOW RES]" if LOW_RES else ""))


# ---------------------------------------------------------------- checks
def staff_check(label, svgtxt, s, want):
    got, errs = read_staff(svgtxt, s)
    errs = [f"{label}: {e}" for e in errs]
    if got is not None and got != want:
        errs.append(f"{label}: drawn notes read back as {got}, data says {want}")
    return errs, got


def verify_data():
    errs = []
    # 1. every card's drawn notes read back to its pitches, and the printed answer matches the read-back letters
    for lv in "ABC":
        ans = answers(lv)
        if len(LEVELS[lv]["cards"]) != 24:
            errs.append(f"level {lv}: {len(LEVELS[lv]['cards'])} cards, expected 24")
        for i in range(24):
            st, _ = card_staff(lv, i)
            e, got = staff_check(f"card {lv}{i + 1}", st, S_CARD, card_pitches(lv, i))
            errs += e
            if got:
                letters = [p[0] for p in got]
                printed = ans[i].replace(" ", "")
                if "".join(letters) != printed:
                    errs.append(f"card {lv}{i + 1}: answer {ans[i]} but the staff shows {letters}")
    # 2. level ranges
    for i, p in enumerate(LEVEL_A):
        if p not in STAFF_ONLY:
            errs.append(f"A{i + 1}: {p} is outside Level A's range")
    for i, c in enumerate(LEVEL_B):
        if len(c) != 3 or any(p not in LEVEL_B_RANGE for p in c):
            errs.append(f"B{i + 1}: {c} breaks Level B's rule (3 notes, D4-G5)")
    for i, c in enumerate(LEVEL_C):
        if "".join(p[0] for p in c) != CARD_WORDS[i]:
            errs.append(f"C{i + 1}: notes do not spell {CARD_WORDS[i]}")
        if any(N.diatonic(p) < N.diatonic("C4") or N.diatonic(p) > N.diatonic("A5") for p in c):
            errs.append(f"C{i + 1}: note outside C4-A5")
    ledger = sum(p in ("C4", "A5") for c in LEVEL_C for p in c)
    if ledger < 8:
        errs.append(f"level C has only {ledger} ledger-line notes")
    if len(set(CARD_WORDS)) != 24 or len(set(WS_C_WORDS)) != len(WS_C_WORDS) or set(CARD_WORDS) & set(WS_C_WORDS):
        errs.append("words repeat")
    for w in CARD_WORDS + WS_C_WORDS:
        if set(w) - set("ABCDEFG"):
            errs.append(f"word {w} uses a letter outside A-G")
    # 3. Level A choices: exactly one is the answer, three different letters, answer spot spread out
    spots = [0, 0, 0]
    for i, (p, ch) in enumerate(zip(LEVEL_A, CHOICES)):
        if len(set(ch)) != 3 or ch.count(p[0]) != 1:
            errs.append(f"A{i + 1}: choices {ch} must hold the answer {p[0]} exactly once")
        else:
            spots[ch.index(p[0])] += 1
    if min(spots) < 6:
        errs.append(f"Level A answer positions are lopsided: {spots}")
    # 4. worksheets and the reference/cover staffs read back correctly
    for i, p in enumerate(WS_A):
        errs += staff_check(f"worksheet A #{i + 1}", staff_svg([p], 6, 52, 6.6, 96)[0], 6.6, [p])[0]
    for i, ps in enumerate(WS_B):
        errs += staff_check(f"worksheet B #{i + 1}", staff_svg(ps, 10, 54, 7, 210)[0], 7, ps)[0]
    for i, ps in enumerate(WS_C):
        errs += staff_check(f"worksheet C #{i + 1}", staff_svg(ps, 8, 47, 6.6, 214)[0], 6.6, ps)[0]
    rng = N.CLEFS["treble"]["range"]
    for label, ps, s, length in (("reference staff", rng, 9.5, 520), ("line notes", LINE_NOTES, 8, 250),
                                 ("space notes", SPACE_NOTES, 8, 250), ("ledger notes", ["C4", "D4", "G5", "A5"], 8, 250),
                                 ("cover", COVER_WORD, 11, 420)):
        errs += staff_check(label, staff_svg(ps, 10, 70, s, length, head="whole" if label != "cover" else "quarter")[0], s, ps)[0]
    # the line/space facts used on the reference page and worksheet A, from staff steps alone
    for p in STAFF_ONLY:
        st = N.diatonic(p) - N.diatonic("E4")
        if (st % 2 == 0) != (p in LINE_NOTES) or (st % 2 == 1) != (p in SPACE_NOTES):
            errs.append(f"{p}: line/space label is wrong")
    if "".join(p[0] for p in LINE_NOTES) != "EGBDF" or "".join(p[0] for p in SPACE_NOTES) != "FACE":
        errs.append("line/space mnemonics do not match the notes")
    if "".join(p[0] for p in COVER_WORD) != "FACE":
        errs.append("cover word")
    # 5. plan
    if len(PLAN) != len(set(PLAN)):
        errs.append("plan has a repeated page")
    covered = set()
    for _, a, b, _ in PARTS:
        covered |= set(PLAN[IX[a] - 1:IX[b]])
    if covered | {"cover", "teacher"} != set(PLAN):
        errs.append(f"teacher table misses pages: {sorted(set(PLAN) - covered - {'cover', 'teacher'})}")
    for name, cp in {"gClef": 0xE050, "noteheadBlack": 0xE0A4, "noteheadWhole": 0xE0A2}.items():
        if N.GLYPH[name][0] != cp:
            errs.append(f"{name} codepoint wrong")
    return errs


def pdf_fonts(path):
    out = subprocess.run(["pdffonts", path], capture_output=True, text=True, check=True).stdout.splitlines()[2:]
    return [(ln.split()[0], ln.split()[-5]) for ln in out]


def footer_errors(path, safe=0.35 * 72):
    out = subprocess.run(["pdftotext", "-bbox", path, "-"], capture_output=True, text=True, check=True).stdout
    errs = []
    for i, pg in enumerate(re.findall(r'<page width="([\d.]+)" height="([\d.]+)">(.*?)</page>', out, re.S)):
        ph = float(pg[1])
        ys = [float(m) for m in re.findall(r'yMax="([\d.]+)">Lotze', pg[2])]
        if i == 0 and not ys:
            continue
        if not ys:
            errs.append(f"{os.path.basename(path)} p{i + 1}: footer not found on the page")
        elif max(ys) > ph - safe:
            errs.append(f"{os.path.basename(path)} p{i + 1}: footer ends {ph - max(ys):.1f}pt from the bottom edge (< {safe:.0f}pt)")
    return errs


def key_text_errors(txt):
    """The answers printed in the PDF's key pages equal the checked data."""
    errs = []
    t = re.sub(r"\s+", " ", txt[IX["key_cards"] - 1])
    for lv in "ABC":
        for i, a in enumerate(answers(lv)):
            if not re.search(rf"\b{lv}{i + 1} {re.escape(a)}\b", t):
                errs.append(f"card key page: '{lv}{i + 1} {a}' not found")
    kc = re.sub(r"\s+", "", txt[IX["key_ws_c"] - 1])
    for ps in WS_C:
        if "".join(p[0] for p in ps) not in kc:
            errs.append(f"worksheet C key: word {''.join(p[0] for p in ps)} missing")
    return errs


def verify_files():
    errs = []
    from pypdf import PdfReader
    from PIL import Image
    for p in [PDF, PREVIEW_PDF, COVER_PNG, *PREVIEW_PNGS, UPLOAD, TPT_JSON]:
        if not os.path.exists(p):
            errs.append(f"missing {os.path.basename(p)}")
    if errs:
        return errs
    for path, items in ((PDF, PLAN), (PREVIEW_PDF, PREVIEW_PICKS)):
        rd = PdfReader(path)
        if len(rd.pages) != len(items):
            errs.append(f"{os.path.basename(path)}: {len(rd.pages)} pages, expected {len(items)}")
        for i, pg in enumerate(rd.pages):
            w, h = float(pg.mediabox.width), float(pg.mediabox.height)
            if abs(w - 612) > 1 or abs(h - 792) > 1:
                errs.append(f"{os.path.basename(path)} p{i + 1}: {w:.0f}x{h:.0f}pt, not US Letter")
        errs += footer_errors(path)
        fonts = pdf_fonts(path)
        for name, emb in fonts:
            if emb != "yes":
                errs.append(f"{os.path.basename(path)}: font {name} not embedded")
        names = " ".join(n for n, _ in fonts).lower()
        for fam in ("bravura", "oswald", "sourcesans3"):
            if fam not in names.replace(" ", ""):
                errs.append(f"{os.path.basename(path)}: {fam} not found in PDF fonts")
        for name, _ in fonts:
            if not re.search(r"bravura|oswald|sourcesans", name.lower()):
                errs.append(f"{os.path.basename(path)}: unexpected font {name} (a glyph fell back to a system font)")
    rd = PdfReader(PDF)
    txt = [subprocess.run(["pdftotext", "-layout", "-f", str(i + 1), "-l", str(i + 1), PDF, "-"], capture_output=True, text=True,
                          check=True).stdout for i in range(len(rd.pages))]
    flat = [re.sub(r"\s+", " ", t) for t in txt]
    for i, t in enumerate(flat):
        if i > 0 and "Brian Lotze · Hudson Beat" not in t:
            errs.append(f"page {i + 1}: footer missing")
        if i > 0 and f"Page {i + 1}" not in t:
            errs.append(f"page {i + 1}: page number in the footer is wrong")
    errs += key_text_errors(txt)
    alltext = " ".join(flat).lower()
    for bad in BANNED:
        if re.search(rf"\b{bad}\b", alltext):
            errs.append(f"resource text mentions '{bad}' (must stay non-denominational)")
    for m in re.finditer(r"pages? (\d+)(?:–(\d+))?", " ".join(flat[1:])):
        for g in m.groups():
            if g and not 1 <= int(g) <= len(PLAN):
                errs.append(f"cross-reference to page {g} does not exist")
    for key, target in (("cards_a1", "key_cards"), ("ws_a", "key_ws_a"), ("ws_b", "key_ws_b"), ("ws_c", "key_ws_c")):
        if f"Answer key on page {IX[target]}" not in flat[IX[key] - 1]:
            errs.append(f"{key}: answer-key cross-reference missing")
    ptxt = [PdfReader(PREVIEW_PDF).pages[i].extract_text() for i in range(len(PREVIEW_PICKS))]
    if sum("PREVIEW" in t for t in ptxt) != len(PREVIEW_PICKS):
        errs.append("preview PDF: watermark missing on some pages")
    for p in [COVER_PNG, *PREVIEW_PNGS]:
        if Image.open(p).size != (2000, 2000):
            errs.append(f"{os.path.basename(p)}: not 2000x2000 (low-res build?)")
    tj = json.load(open(TPT_JSON))
    if tj["pages"] != len(rd.pages):
        errs.append("tpt.json pages != PDF pages")
    if tj["price"] != PRICE or tj["license_price"] != PRICE or not tj.get("tax_code"):
        errs.append("tpt.json price/license_price/tax_code")
    for k, f in tj["files"].items():
        if not os.path.exists(os.path.join(HERE, f)):
            errs.append(f"tpt.json file {k} missing: {f}")
    if not (1 <= len(tj["grades"]) <= 4 and 1 <= len(tj["subjects"]) <= 3 and 1 <= len(tj["tags"]) <= 6):
        errs.append("tpt.json grade/subject/tag counts out of range")
    up = open(UPLOAD).read()
    m = re.search(r"^## 1\. Title\s*\n+```\n(.+?)\n```\n\((\d+) characters", up, re.M | re.S)
    if not m:
        errs.append("UPLOAD.md: title block or its character count not found")
    else:
        n = len(m.group(1).strip())
        if n > 80:
            errs.append(f"UPLOAD.md: title is {n} chars (max 80)")
        if int(m.group(2)) != n:
            errs.append(f"UPLOAD.md: says {m.group(2)} characters, title has {n}")
    m2 = re.search(r"^## 2\. Description\s*\n+```\n(.+?)\n```", up, re.M | re.S)
    if not m2 or "Designed with the help of digital and AI tools, and checked by hand." not in m2.group(1):
        errs.append("UPLOAD.md: description block missing the disclosure line")
    elif any(re.search(rf"\b{b}\b", m2.group(1).lower()) for b in BANNED):
        errs.append("UPLOAD.md: description uses a holiday word")
    for need in (f"${PRICE}", f"{len(rd.pages)} pages"):
        if need not in up:
            errs.append(f"UPLOAD.md: missing '{need}'")
    for f in ("release", "uploaded"):
        if os.path.exists(os.path.join(HERE, f)):
            errs.append(f"{f} exists: only the Manager / uploader writes it")
    return errs


def check():
    errs = verify_data() + verify_files()
    if errs:
        print("CHECK FAILED")
        print("\n".join(" - " + e for e in errs))
        sys.exit(1)
    nnotes = 24 + 72 + sum(len(c) for c in LEVEL_C)
    print(f"CHECK OK: {nnotes} card notes + all worksheet/reference/cover notes read back from the drawn SVG "
          f"(staff lines, G-line clef, line/space position, ledger lines, stem direction) and match every printed answer; "
          f"card key and worksheet C key text in the PDF match; Level A choices hold the answer once (spots spread); "
          f"{len(PLAN)} Letter pages with footers and page numbers; only Bravura/Oswald/Source Sans 3, all embedded; "
          f"no holiday words; preview {len(PREVIEW_PICKS)} watermarked pages; images 2000x2000; tpt.json and UPLOAD.md ok.")


if __name__ == "__main__":
    if "--check" in sys.argv:
        check()
    else:
        build()
