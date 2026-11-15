#!/usr/bin/env python3
"""Note Naming Speed Drills (TpT 043): build the resource and verify it.

    python3 gen.py           build everything (PDFs, PNGs, UPLOAD.md, tpt.json) into this folder
    python3 gen.py --check   verify notes, answer keys, notation geometry, layout, pages, fonts and files

Model: a drill item is (staff step, accidental) in a clef. Step 0 is the bottom staff line, +1 per line/space upward
(so lines are even, spaces odd, ledger lines are even steps below 0 or above 8). The generator names a note from the
clef's BOTTOM-LINE pitch (treble E4, bass G2, alto F3). `--check` does not trust that: it parses the rendered HTML and
recomputes every note name from the drawn geometry (y of the notehead against the staff lines and the clef glyph's own
anchor pitch: G4 for the G clef, F3 for the F clef, C4 for the C clef), cross-checks in-staff notes against the
line/space letter strings, verifies ledger lines and stems note by note, then compares every answer key entry to its
drill item, item by item, and the item counts of worksheets and keys for every page.

Rendering: Playwright + Chromium (HTML/SVG -> PDF/PNG) with the OFL fonts in ../fonts. Bravura draws the notation.
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
RENDER_JS = os.path.join(TPT, "tools", "render.js")

SLUG = "note-naming-speed-drills"
PDF = os.path.join(HERE, f"{SLUG}.pdf")
PREVIEW_PDF = os.path.join(HERE, f"{SLUG}-PREVIEW.pdf")
COVER_PNG = os.path.join(HERE, "cover.png")
PREVIEW_PNGS = [os.path.join(HERE, f"preview-{i}.png") for i in (1, 2, 3)]
UPLOAD = os.path.join(HERE, "UPLOAD.md")
TPT_JSON = os.path.join(HERE, "tpt.json")

STORE = "Brian Lotze"
BRAND = "Hudson Beat"
YEAR = 2026
ACCENT = "#C2410C"   # burnt orange: the one accent of this product
DISCLOSURE = "Created with the help of digital and AI tools. Notation and answer keys are verified before release."
TITLE = "Note Naming Speed Drills"
UPLOAD_TITLE = "Note Naming Worksheets: Treble, Bass & Alto Clef Speed Drills, Grades 3-8"
PRICE = "4.00"

# ------------------------------------------------------------------ music model
LETTERS = "CDEFGAB"
CLEFS = ["treble", "bass", "alto"]
CLEF_PREFIX = {"treble": "T", "bass": "B", "alto": "A"}
CLEF_LABEL = {"treble": "Treble clef", "bass": "Bass clef", "alto": "Alto clef"}
# generator method: pitch of the bottom staff line as (letter index, octave)
BOTTOM_LINE = {"treble": ("E", 4), "bass": ("G", 2), "alto": ("F", 3)}
CLEF_GLYPH = {"treble": 0xE050, "bass": 0xE062, "alto": 0xE05C}
CLEF_STEP = {"treble": 2, "bass": 6, "alto": 4}      # staff step the clef glyph's origin sits on
GLYPH_CLEF = {v: k for k, v in CLEF_GLYPH.items()}
ACC_GLYPH = {"#": 0xE262, "b": 0xE260}
GLYPH_ACC = {v: k for k, v in ACC_GLYPH.items()}
ACC_W = {"#": 1.0, "b": 0.9}
HEAD_GLYPH = 0xE0A4
HEAD_W = 1.18
NDRILL = 10
PER_DRILL = 30
COLS, ROWS = 5, 6

SHARP_OK = set("CDFGA")   # no E#, B#
FLAT_OK = set("DEGAB")    # no C-flat, F-flat


def note_name(clef, step, acc=""):
    """Generator naming: diatonic count up from the bottom line."""
    letter, octave = BOTTOM_LINE[clef]
    dn = octave * 7 + LETTERS.index(letter) + step
    return LETTERS[dn % 7] + {"": "", "#": "#", "b": "b"}[acc], dn // 7


def pretty(name):
    return name.replace("#", "♯").replace("b", "♭") if len(name) > 1 else name


# ------------------------------------------------------------------ the 30 drills
# level -> (title, step lo, step hi, accidental probability, skill line)
LEVELS = [
    ("Lines", 0, 8, 0.0, "Only notes on the five lines."),
    ("Spaces", 0, 8, 0.0, "Only notes in the four spaces."),
    ("Lines and spaces", 0, 8, 0.0, "Every line and space of the staff."),
    ("Just above and below the staff", -1, 9, 0.0, "The staff plus the space above and the space below."),
    ("One ledger line", -2, 10, 0.0, "Adds the first ledger line above and below."),
    ("Two ledger lines", -4, 12, 0.0, "Adds the second ledger line above and below."),
    ("Three ledger lines", -6, 14, 0.0, "Every ledger line up to three above and below."),
    ("Sharps and flats", 0, 8, 0.7, "Notes in the staff, many with a sharp or a flat."),
    ("Sharps, flats and ledger lines", -4, 12, 0.5, "Sharps, flats and up to two ledger lines."),
    ("Mixed challenge", -6, 14, 0.4, "Everything: lines, spaces, ledger lines, sharps and flats."),
]
SPACE_ONLY = 1


def drill_id(clef, n):
    return f"{CLEF_PREFIX[clef]}{n}"


def acc_options(clef, step):
    letter = note_name(clef, step)[0][0]
    opts = []
    if letter in SHARP_OK:
        opts.append("#")
    if letter in FLAT_OK:
        opts.append("b")
    return opts


def build_drill(clef, n):
    title, lo, hi, accp, _ = LEVELS[n - 1]
    if n == 1:
        pool = [s for s in range(lo, hi + 1) if s % 2 == 0]
    elif n == 2:
        pool = [s for s in range(lo, hi + 1) if s % 2 == 1]
    else:
        pool = list(range(lo, hi + 1))
    for attempt in range(500):
        rng = random.Random(f"nns-{clef}-{n}-{attempt}")
        weights = [2 if (s < 0 or s > 8) else 1 for s in pool]
        steps = []
        for i in range(PER_DRILL):
            ok = [(p_, w_) for p_, w_ in zip(pool, weights)
                  if (not steps or p_ != steps[-1]) and not (len(pool) >= 8 and i >= COLS and p_ == steps[i - COLS])]
            unseen = [p_ for p_, _ in ok if p_ not in steps]
            need = len(set(pool) - set(steps))
            if unseen and need >= PER_DRILL - i:      # must start covering the rest now
                steps.append(rng.choice(unseen))
            else:
                steps.append(rng.choices([p_ for p_, _ in ok], [w_ * (3 if p_ in unseen else 1) for p_, w_ in ok])[0])
        if set(steps) != set(pool):    # every step of the level appears at least once
            continue
        items = []
        for s in steps:
            acc = ""
            if accp and rng.random() < accp:
                o = acc_options(clef, s)
                if o:
                    acc = rng.choice(o)
            items.append((s, acc))
        if n >= 8:   # accidental pages: guarantee enough accidentals
            if sum(1 for _, a in items if a) < int(PER_DRILL * accp * 0.8):
                continue
        if any(items[i] == items[i + 1] for i in range(len(items) - 1)):
            continue
        if len(pool) >= 8 and any(items[i] == items[i + COLS] for i in range(len(items) - COLS)):   # same note straight below
            continue
        return items
    raise RuntimeError(f"no valid draw for {clef} {n}")


def make_drills():
    return {(c, n): build_drill(c, n) for c in CLEFS for n in range(1, NDRILL + 1)}


# ------------------------------------------------------------------ notation drawing
def fx(v):
    return f"{v:.2f}"


def g(cp, x, y, size, cls="", fill="#000", extra=""):
    c = f' class="{cls}"' if cls else ""
    return f'<text{c} x="{fx(x)}" y="{fx(y)}" font-family="Bravura" font-size="{fx(size)}" fill="{fill}"{extra}>&#x{cp:X};</text>'


def stem_len(step, S):
    """Stem length in pt: 3.5 spaces, or up to the middle line for far notes."""
    return max(3.5 * S, abs(step - 4) / 2 * S)


def staff_open(w, h, S, top, ctx, x0=2.0):
    out = [f'<svg class="ns" data-ctx="{ctx}" data-s="{S}" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {fx(w)} {fx(h)}" '
           f'width="{fx(w)}pt" height="{fx(h)}pt" style="display:block">']
    for k in range(5):
        y = top + k * S
        out.append(f'<line class="sl" x1="{fx(x0)}" y1="{fx(y)}" x2="{fx(w - 2)}" y2="{fx(y)}" stroke="#000" stroke-width="{fx(0.13 * S)}"/>')
    return out


def clef_svg(clef, S, top, x=3.0):
    bottom = top + 4 * S
    y = bottom - CLEF_STEP[clef] * S / 2
    return g(CLEF_GLYPH[clef], x, y, 4 * S, "clef")


def note_svg(clef, step, acc, cx, S, top, fill="#000"):
    bottom = top + 4 * S
    y = bottom - step * S / 2
    hw = HEAD_W * S
    left = cx - hw / 2
    out = ['<g class="nt">']
    ext = 0.4 * S
    leds = [e for e in range(-2, step - 1, -2)] if step < 0 else []
    leds += [e for e in range(10, step + 1, 2)] if step > 8 else []
    for e in leds:
        ly = bottom - e * S / 2
        out.append(f'<line class="led" x1="{fx(left - ext)}" y1="{fx(ly)}" x2="{fx(left + hw + ext)}" y2="{fx(ly)}" '
                   f'stroke="#000" stroke-width="{fx(0.16 * S)}"/>')
    if acc:
        out.append(g(ACC_GLYPH[acc], left - 0.3 * S - ACC_W[acc] * S, y, 4 * S, "acc", fill))
    out.append(g(HEAD_GLYPH, left, y, 4 * S, "head", fill))
    sw = 0.13 * S
    L = stem_len(step, S)
    if step < 4:   # stem up, on the right of the head
        sx = left + hw - sw / 2
        out.append(f'<line class="stem" data-dir="up" x1="{fx(sx)}" y1="{fx(y - 0.168 * S)}" x2="{fx(sx)}" y2="{fx(y - 0.168 * S - L)}" '
                   f'stroke="{fill}" stroke-width="{fx(sw)}"/>')
    else:          # stem down, on the left
        sx = left + sw / 2
        out.append(f'<line class="stem" data-dir="down" x1="{fx(sx)}" y1="{fx(y + 0.168 * S)}" x2="{fx(sx)}" y2="{fx(y + 0.168 * S + L)}" '
                   f'stroke="{fill}" stroke-width="{fx(sw)}"/>')
    out.append("</g>")
    return "".join(out)


def cell_dims(S):
    top = 3.7 * S
    h = top + 4 * S + 3.5 * S + 0.8 * S + 14
    return top, h


def drill_cell_svg(clef, drill, item, step, acc, S=6.2, w=108.0, answer=True):
    top, h = cell_dims(S)
    if not answer:
        h -= 14
    out = staff_open(w, h, S, top, f"drill:{drill}:{item}")
    out.append(clef_svg(clef, S, top))
    cx = w * 0.62
    out.append(note_svg(clef, step, acc, cx, S, top))
    out.append(f'<text class="num" x="{fx(w - 4)}" y="9" text-anchor="end" font-family="Oswald" font-weight="500" font-size="9">{item}</text>')
    if answer:
        ay = h - 5
        out.append(f'<line class="al" x1="{fx(cx - 19)}" y1="{fx(ay)}" x2="{fx(cx + 19)}" y2="{fx(ay)}" stroke="#000" stroke-width="0.8"/>')
    out.append("</svg>")
    return "".join(out)


def row_svg(clef, notes, ctx, w, S, labels=None, label_cls="rl", highlight_c=False):
    """A staff with several notes in a row, optional name labels under it (for reference pages and the cover)."""
    top = 3.7 * S
    lab_h = 22 if labels else 0
    h = top + 4 * S + 3.5 * S + 0.8 * S + lab_h
    out = staff_open(w, h, S, top, ctx)
    out.append(clef_svg(clef, S, top))
    n = len(notes)
    x_start = 3 + 3.0 * S + 14
    gap = (w - 6 - x_start) / n
    for i, (step, acc) in enumerate(notes):
        cx = x_start + gap * (i + 0.5)
        out.append(note_svg(clef, step, acc, cx, S, top))
        if labels:
            nm = note_name(clef, step, acc)[0]
            is_c4 = (note_name(clef, step, acc) == ("C", 4))
            col = ACCENT if is_c4 else "#000"
            out.append(f'<text class="{label_cls}" x="{fx(cx)}" y="{fx(h - 6)}" text-anchor="middle" font-family="Oswald" font-weight="700" '
                       f'font-size="14" fill="{col}">{nm[0]}</text>')
    out.append("</svg>")
    return "".join(out)


# ------------------------------------------------------------------ html pieces
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
.how { font-size: 11pt; margin: 2pt 0 6pt; line-height: 1.3; }
.how b { font-weight: 700; }
.grid { display: grid; grid-template-columns: repeat(5, 1fr); border-top: .8pt solid #000; border-left: .8pt solid #000; }
.grid > div { border-right: .8pt solid #000; border-bottom: .8pt solid #000; }
.grid svg { display: block; width: 100%; height: auto; }
.score { display: flex; justify-content: space-between; align-items: center; margin: 9pt 0 0; font-size: 11.5pt; flex: 1; }
.score .box { display: flex; align-items: center; gap: 6pt; font-family: 'Oswald'; font-weight: 500; text-transform: uppercase; font-size: 11pt; letter-spacing: .03em; }
.score .box i { display: inline-block; width: 46pt; height: 24pt; border: 1.3pt solid #000; border-radius: 4pt; }
.score .box i.t { width: 70pt; }
.foot { display: flex; justify-content: space-between; font-size: 8.5pt; color: #333; border-top: .8pt solid #000; padding-top: 3pt; }
.wm { position: absolute; left: 50%; top: 50%; transform: translate(-50%, -50%) rotate(-38deg); font-family: 'Oswald'; font-weight: 700;
      font-size: 150pt; color: rgba(0,0,0,.13); letter-spacing: .06em; white-space: nowrap; pointer-events: none; z-index: 9; }
.kb { margin-top: 7pt; }
.kb .kt { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 11.5pt; border-bottom: 1pt solid #000; padding-bottom: 2pt; margin-bottom: 3pt; display: flex; justify-content: space-between; }
.kb .kt span { font-weight: 300; text-transform: none; font-size: 10pt; }
.kg { display: grid; grid-template-columns: repeat(5, 1fr); }
.kc { height: 17pt; line-height: 1; overflow: hidden; display: flex; align-items: baseline; gap: 6pt; padding: 2.6pt 4pt; border-bottom: .5pt solid #bbb; }
.kc i { font-style: normal; font-family: 'Oswald'; font-weight: 300; font-size: 9pt; width: 14pt; text-align: right; }
.kc b { font-family: 'Oswald'; font-weight: 700; font-size: 14pt; color: ACCENT; }
.kc .ac { font-family: 'Bravura'; font-weight: 400; font-size: 14pt; line-height: 0; color: ACCENT; margin-left: 1pt; }
.doc h1 { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 30pt; margin: 0 0 4pt; line-height: 1; }
.doc h2 { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 14pt; margin: 13pt 0 4pt; letter-spacing: .02em; }
.doc p, .doc li { font-size: 11pt; line-height: 1.38; margin: 0 0 5pt; }
.doc ul, .doc ol { margin: 0 0 4pt; padding-left: 18pt; }
.doc .rule { border-bottom: 2.2pt solid #000; margin-bottom: 8pt; padding-bottom: 6pt; }
.doc table { border-collapse: collapse; width: 100%; font-size: 10pt; margin: 2pt 0 4pt; }
.doc td, .doc th { border: 1pt solid #000; padding: 3.5pt 6pt; text-align: left; vertical-align: top; }
.doc th { font-family: 'Oswald'; font-weight: 500; text-transform: uppercase; font-size: 9.5pt; background: #000; color: #fff; }
.small { font-size: 9pt !important; color: #333; }
.acc-t { color: ACCENT; }
.steps { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8pt; margin: 6pt 0 8pt; }
.steps div { border: 1.3pt solid #000; border-radius: 6pt; padding: 6pt 7pt; font-size: 10.5pt; line-height: 1.3; }
.steps b { display: block; font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 12pt; }
.steps b em { font-style: normal; color: ACCENT; }
.bands { display: grid; grid-template-columns: repeat(4, 1fr); gap: 6pt; margin: 4pt 0 6pt; }
.bands div { border: 1.3pt solid #000; border-radius: 6pt; text-align: center; padding: 4pt 2pt; font-size: 9.5pt; line-height: 1.2; }
.bands b { display: block; font-family: 'Oswald'; font-weight: 700; font-size: 16pt; color: ACCENT; }
.refrow { margin: 3pt 0 8pt; }
.refrow .rt { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 12.5pt; margin: 8pt 0 0; }
.refrow .rt span { font-weight: 300; text-transform: none; font-size: 10.5pt; margin-left: 6pt; }
.refrow svg { display: block; width: 100%; height: auto; }
.cart svg { width: 100%; height: auto; }
.cover { align-items: center; justify-content: space-between; padding: 0.55in 0.6in 0.5in; }
.store { font-family: 'Oswald'; font-weight: 500; font-size: 13pt; letter-spacing: .32em; text-transform: uppercase; }
.ctitle { text-align: center; }
.ctitle .a { font-family: 'Oswald'; font-weight: 700; font-size: 44pt; line-height: 1; letter-spacing: .02em; }
.ctitle .b { font-family: 'Oswald'; font-weight: 700; white-space: nowrap; font-size: 74pt; line-height: .95; letter-spacing: .01em; }
.ctitle .c { font-family: 'Oswald'; font-weight: 300; font-size: 17pt; margin-top: 8pt; }
.cband { width: 100%; background: #000; color: #fff; text-align: center; font-family: 'Oswald'; font-weight: 500; font-size: 14pt;
         letter-spacing: .08em; text-transform: uppercase; padding: 8pt 0 9pt; border-radius: 4pt; }
.cband em { font-style: normal; color: ACCENT; }
table.pl td:first-child { white-space: nowrap; }
table.log td { height: 17.4pt; padding: 0 6pt; font-size: 9.5pt; }
table.log td.n { width: 1.0in; }
""".replace("ACCENT", ACCENT)


def html_doc(pages, title="doc"):
    return (f'<!doctype html><html><head><meta charset="utf-8"><title>{escape(title)}</title>'
            f'<style>{font_css()}{CSS}</style></head><body>{"".join(pages)}</body></html>')


def foot(left, right):
    return f'<div class="foot"><span>{left}</span><span>{right}</span></div>'


COPY = f"© {YEAR} {STORE} · {BRAND} · For single-classroom use"

# page numbers
P_COVER, P_TEACH, P_GUIDE, P_REF, P_PROG, P_LOG = 1, 2, 3, 4, 5, 6
P_DR0 = 7
def drill_page_no(clef, n):
    return P_DR0 + CLEFS.index(clef) * NDRILL + n - 1
P_KEY0 = P_DR0 + 3 * NDRILL         # 37
KEY_PAGES = [(c, h) for c in CLEFS for h in (0, 1)]   # 6 pages: 5 drills each
P_TERMS = P_KEY0 + len(KEY_PAGES)   # 43
TOTAL_PAGES = P_TERMS


def key_page_no(clef, n):
    return P_KEY0 + CLEFS.index(clef) * 2 + (n - 1) // 5


def drill_title(clef, n):
    return LEVELS[n - 1][0]


def drill_page(clef, n, items, watermark=False):
    did = drill_id(clef, n)
    title, _, _, _, skill = LEVELS[n - 1]
    wm = '<div class="wm">PREVIEW</div>' if watermark else ""
    cells = "".join(f'<div data-drill="{did}" data-item="{i + 1}">{drill_cell_svg(clef, did, i + 1, s, a)}</div>'
                    for i, (s, a) in enumerate(items))
    acc_note = (" Sharps and flats count: write the sharp ♯ or flat ♭ after the letter, like F♯ or B♭."
                if LEVELS[n - 1][3] else "")
    how = (f'<div class="how"><b>Set a timer for one minute.</b> Write the letter name under each note, left to right, row by row. '
           f'Skip any you are not sure of and keep going.{acc_note}</div>')
    score = ('<div class="score"><div class="box">Items finished <i></i></div><div class="box">Correct <i></i> / 30</div>'
             '<div class="box">Goal <i></i></div></div>')
    return (f'<section class="page">{wm}'
            f'<div class="top"><div class="h t">Note Naming Speed Drill<small>{n}. {escape(title)}</small></div>'
            f'<div class="tag"><div class="lv">{CLEF_LABEL[clef].upper()} · {n}</div><div class="ln">{escape(skill)}</div></div></div>'
            f'<div class="name">Name<span></span>Date<span class="d"></span></div>{how}'
            f'<div class="grid">{cells}</div>{score}'
            f'{foot(COPY, f"Answer key on page {key_page_no(clef, n)} · Page {drill_page_no(clef, n)}")}</section>')


def ans_html(name):
    if len(name) == 1:
        return f"<b>{name}</b>"
    return f'<b>{name[0]}<span class="ac">&#x{ACC_GLYPH[name[1]]:X};</span></b>'


def key_block(clef, n, items):
    did = drill_id(clef, n)
    cells = "".join(f'<div class="kc" data-drill="{did}" data-item="{i + 1}" data-ans="{note_name(clef, s, a)[0]}">'
                    f'<i>{i + 1}</i>{ans_html(note_name(clef, s, a)[0])}</div>' for i, (s, a) in enumerate(items))
    return (f'<div class="kb"><div class="kt"><div>{CLEF_LABEL[clef]} · drill {n}<span> · {escape(drill_title(clef, n))}</span></div>'
            f'<span>page {drill_page_no(clef, n)}</span></div><div class="kg">{cells}</div></div>')


def key_page(clef, half, drills, watermark=False):
    wm = '<div class="wm">PREVIEW</div>' if watermark else ""
    ns = range(1 + 5 * half, 6 + 5 * half)
    pno = P_KEY0 + CLEFS.index(clef) * 2 + half
    return (f'<section class="page">{wm}'
            f'<div class="top"><div class="h t">Answer Key<small>{CLEF_LABEL[clef]}, drills {ns[0]} to {ns[-1]}</small></div>'
            f'<div class="tag"><div class="lv ak">ANSWER KEY</div><div class="ln">Numbers match the notes, row by row</div></div></div>'
            f'{"".join(key_block(clef, n, drills[(clef, n)]) for n in ns)}'
            f'<div style="flex:1"></div>{foot(COPY, f"Answer key · Page {pno}")}</section>')


# cover art: one short staff per clef, notes named in the accent colour
COVER_NOTES = {
    "treble": [(0, ""), (3, ""), (6, ""), (-2, ""), (9, "")],
    "bass": [(0, ""), (3, ""), (7, ""), (10, ""), (5, "")],
    "alto": [(0, ""), (4, ""), (7, ""), (2, ""), (5, "")],
}


def cover_art(w=400, S=7.0):
    return [row_svg(c, COVER_NOTES[c], f"art:{c}", w, S, labels=True) for c in CLEFS]


def cover_page():
    arts = cover_art()
    return (f'<section class="page cover"><div class="store">{BRAND}</div>'
            f'<div class="cart" style="width:5.4in">{arts[0]}<div style="height:6pt"></div>{arts[1]}<div style="height:6pt"></div>{arts[2]}</div>'
            f'<div class="ctitle"><div class="a">NOTE NAMING</div><div class="b">SPEED DRILLS</div>'
            f'<div class="c">One-minute drills · treble, bass and alto clef · with answer keys and a progress chart</div></div>'
            f'<div class="cband">Grades 3–8 <em>·</em> 30 drill pages <em>·</em> answer keys</div></section>')


def teacher_page():
    ranges = []
    for c in CLEFS:
        ranges.append(f"<tr><td>{CLEF_LABEL[c]}</td><td>{drill_page_no(c, 1)}–{drill_page_no(c, NDRILL)}</td>"
                      f"<td>Drills 1–10. Keys on pages {key_page_no(c, 1)}–{key_page_no(c, NDRILL)}.</td></tr>")
    lev = "".join(f"<tr><td>{i + 1}</td><td>{escape(t)}</td><td>{escape(s)}</td></tr>" for i, (t, _, _, _, s) in enumerate(LEVELS))
    return (f'<section class="page doc"><div class="rule"><h1>Teacher Notes</h1><div class="l" style="font-size:13pt">'
            f'Note Naming Speed Drills · treble, bass and alto clef</div></div>'
            f'<h2>How to use</h2><ol><li>Hand out one drill and set a one-minute timer (a classroom clock or a phone is fine).</li>'
            f'<li>Students write the letter name under each note and stop when time is called.</li>'
            f'<li>Students check with the key (or swap with a partner), write the number correct in the score box and colour the bar on the progress chart.</li>'
            f'<li>Repeat a drill another day: the same page, the same notes, a new score. Beating your own best is the point.</li></ol>'
            f'<p>Each drill has 30 single notes in a 5 by 6 grid. Every note on a page is a new draw, so no two drills are the same. '
            f'The answer is the letter name only (octave is not asked). Sharps and flats appear on drills 8–10 of each clef; '
            f'no E♯, B♯, C♭ or F♭, and no naturals or double accidentals.</p>'
            f'<h2>The ten levels (same in every clef)</h2><table><tr><th>#</th><th>Level</th><th>What is on the page</th></tr>{lev}</table>'
            f'<h2>Where to start</h2><table class="pl"><tr><th>Clef</th><th>Drill pages</th><th>Notes</th></tr>{"".join(ranges)}</table>'
            f'<p><b>Grades 3–5</b> usually start with treble drills 1–5. <b>Grades 6–8</b> use all three clefs: treble for band and orchestra, '
            f'bass for low brass, low reeds, cello and bass, alto for viola. Alto clef: the C clef is centred on the middle line, which is middle C (C4).</p>'
            f'<p>Scoring bands on the student guide: 15 getting there, 20 solid, 25 fast, 30 lightning. Use them as personal goals, not grades.</p>'
            f'<p class="small">Supports National Core Arts Standards, Music, Anchor Standard 4 (notation reading) as a fluency warm-up. '
            f'No songs, lyrics or copyrighted characters are used. Contents: cover, teacher notes, student guide, clef reference, progress chart, drill log, '
            f'30 drills, 6 answer-key pages, terms.</p>'
            f'<div style="flex:1"></div>{foot(COPY, f"Page {P_TEACH}")}</section>')


def guide_page():
    return (f'<section class="page doc"><div class="rule"><h1>How to Drill</h1><div class="l" style="font-size:13pt">'
            f'A student guide: three clefs, one minute, beat your best</div></div>'
            f'<div class="steps"><div><b><em>1</em> Ready</b>Name and date. Pencil ready. Eyes on the first note, top left.</div>'
            f'<div><b><em>2</em> Go</b>The timer starts. Write each letter under its note, row by row.</div>'
            f'<div><b><em>3</em> Stop</b>Pencils down when time is called. Draw a line after your last answer.</div>'
            f'<div><b><em>4</em> Check</b>Use the key. Count your correct answers and colour the progress chart.</div></div>'
            f'<h2>Scoring</h2><div class="bands"><div><b>15</b>Getting there</div><div><b>20</b>Solid</div><div><b>25</b>Fast</div><div><b>30</b>Lightning</div></div>'
            f'<p>Only correct answers count. Do not rush into guesses: skip a note you are not sure of, finish the row, then go back.</p>'
            f'<h2>Tricks that make you faster</h2><ul>'
            f'<li><b>Learn the lines and the spaces separately.</b> Treble lines E G B D F (Every Good Boy Does Fine), spaces F A C E. '
            f'Bass lines G B D F A (Good Boys Do Fine Always), spaces A C E G (All Cows Eat Grass). '
            f'Alto lines F A C E G (Fat Alto Cats Eat Grass), spaces G B D F (Good Bears Dance Freely).</li>'
            f'<li><b>Use landmark notes.</b> Treble: the G clef circles G. Bass: the two dots hug F. Alto: the middle line is C, the same pitch as middle C.</li>'
            f'<li><b>Count from a landmark</b> for ledger lines: from the nearest line, step line, space, line, space.</li>'
            f'<li><b>Ledger lines.</b> A short line through the note means the note sits on the line; a note with a short line just beyond it sits in the space next to it.</li>'
            f'<li><b>Sharps ♯ and flats ♭</b> go before the note and change the name: write F♯, B♭.</li></ul>'
            f'<h2>Your path</h2><p>Each clef has ten drills. Start at drill 1, move on when you score 25 or more on a drill. '
            f'The clef reference on the next page shows every note you will meet, with its name.</p>'
            f'<div style="flex:1"></div>{foot(COPY, f"Page {P_GUIDE}")}</section>')


REF_STEPS = list(range(-2, 11))


def ref_page():
    rows = []
    for c in CLEFS:
        extra = {"treble": "middle C is on the first ledger line below the staff",
                 "bass": "middle C is on the first ledger line above the staff",
                 "alto": "middle C is on the middle line"}[c]
        rows.append(f'<div class="refrow"><div class="rt">{CLEF_LABEL[c]}<span>{extra}</span></div>'
                    f'{row_svg(c, [(s, "") for s in REF_STEPS], f"ref:{c}", 540, 6.6, labels=True)}</div>')
    return (f'<section class="page doc"><div class="rule"><h1>Clef Reference</h1><div class="l" style="font-size:13pt">'
            f'Every note from the first ledger line below to the first ledger line above · middle C in {"orange"}</div></div>'
            f'{"".join(rows)}'
            f'<p class="small">Notes above and below these keep going up and down the alphabet: A B C D E F G, then start again. '
            f'Sharps and flats raise or lower a note and keep its letter.</p>'
            f'<div style="flex:1"></div>{foot(COPY, f"Page {P_REF}")}</section>')


def progress_page():
    cw, rh = 44.0, 4.2
    blocks = []
    for c in CLEFS:
        W = 28 + cw * NDRILL
        H = 30 * rh + 22
        out = [f'<svg viewBox="0 0 {W} {H}" width="{W}pt" height="{H}pt" style="display:block;margin:0 auto" xmlns="http://www.w3.org/2000/svg">']
        for v in range(0, 31):
            y = 4 + (30 - v) * rh
            heavy = v % 5 == 0
            out.append(f'<line x1="28" y1="{y}" x2="{W}" y2="{y}" stroke="{"#000" if heavy else "#bbb"}" stroke-width="{0.9 if heavy else 0.4}"/>')
            if heavy:
                out.append(f'<text x="24" y="{y + 3}" text-anchor="end" font-family="Oswald" font-weight="500" font-size="8">{v}</text>')
        gy = 4 + (30 - 25) * rh
        out.append(f'<line x1="28" y1="{gy}" x2="{W}" y2="{gy}" stroke="{ACCENT}" stroke-width="1.6" stroke-dasharray="5 3"/>')
        for k in range(NDRILL + 1):
            x = 28 + k * cw
            out.append(f'<line x1="{x}" y1="4" x2="{x}" y2="{4 + 30 * rh}" stroke="#000" stroke-width="0.8"/>')
        for k in range(NDRILL):
            out.append(f'<text x="{28 + k * cw + cw / 2}" y="{4 + 30 * rh + 12}" text-anchor="middle" font-family="Oswald" font-weight="700" font-size="9">{k + 1}</text>')
        out.append("</svg>")
        blocks.append(f'<div class="refrow"><div class="rt">{CLEF_LABEL[c]}<span>score out of 30 for each drill · dashed line is 25 (fast)</span></div>{"".join(out)}</div>')
    return (f'<section class="page doc"><div class="rule"><h1>My Progress Chart</h1><div class="l" style="font-size:13pt">'
            f'Colour a bar up to your score after each drill</div></div>'
            f'<div class="name" style="margin-top:2pt">Name<span></span>Class<span class="d"></span></div>'
            f'{"".join(blocks)}<div style="flex:1"></div>{foot(COPY, f"Page {P_PROG}")}</section>')


def log_page():
    rows = []
    for c in CLEFS:
        for n in range(1, NDRILL + 1):
            rows.append(f'<tr><td class="n">{CLEF_LABEL[c].replace(" clef", "")} {n}</td><td>{escape(drill_title(c, n))}</td>'
                        f'<td></td><td></td><td></td><td></td></tr>')
    return (f'<section class="page doc"><div class="rule"><h1>Drill Log</h1><div class="l" style="font-size:13pt">'
            f'Write the date and your score (out of 30) for each try</div></div>'
            f'<table class="log"><tr><th>Drill</th><th>Level</th><th>Try 1</th><th>Try 2</th><th>Try 3</th><th>Best</th></tr>{"".join(rows)}</table>'
            f'<div style="flex:1"></div>{foot(COPY, f"Page {P_LOG}")}</section>')


def terms_page():
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
            f'<li>Notes, layouts and answer keys: original work, {BRAND} by {STORE}.</li>'
            f'<li>Music notation font: Bravura © Steinberg Media Technologies GmbH, SIL Open Font License 1.1.</li>'
            f'<li>Text fonts: Oswald (The Oswald Project Authors) and Source Sans 3 (Adobe), SIL Open Font License 1.1.</li></ul>'
            f'<p class="small">{DISCLOSURE}</p>'
            f'<div style="flex:1"></div>{foot(COPY, f"Page {P_TERMS}")}</section>')


def full_pages(drills):
    pages = [cover_page(), teacher_page(), guide_page(), ref_page(), progress_page(), log_page()]
    for c in CLEFS:
        pages += [drill_page(c, n, drills[(c, n)]) for n in range(1, NDRILL + 1)]
    pages += [key_page(c, h, drills) for c, h in KEY_PAGES]
    pages.append(terms_page())
    return pages


PREVIEW_PICKS = [("d", "treble", 5), ("d", "bass", 8), ("d", "alto", 6), ("k", "treble", 0)]


def preview_pages(drills):
    out = []
    for k, c, n in PREVIEW_PICKS:
        out.append(drill_page(c, n, drills[(c, n)], True) if k == "d" else key_page(c, n, drills, True))
    return out


# ------------------------------------------------------------------ square images
SQ_CSS = """
.sq { width: 1000px; height: 1000px; position: relative; overflow: hidden; background: #fff; display: flex; flex-direction: column; align-items: center; }
.sq .store { font-family: 'Oswald'; font-weight: 500; letter-spacing: .32em; text-transform: uppercase; font-size: 22px; margin-top: 34px; font-size-adjust: none; }
.sq .hd { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; text-align: center; line-height: .95; }
.sq .sub { font-family: 'Oswald'; font-weight: 300; text-align: center; }
.sq .band { position: absolute; left: 0; right: 0; bottom: 0; height: 66px; background: #000; color: #fff; text-align: center; font-family: 'Oswald';
            font-weight: 500; text-transform: uppercase; letter-spacing: .1em; font-size: 26px; padding: 16px 0 0; }
.sq .band em { font-style: normal; color: ACCENT; }
.sq .body { flex: 1; width: 100%; padding-bottom: 80px; display: flex; flex-direction: column; align-items: center; min-height: 0; }
.cart svg { width: 100%; height: auto; }
.shot { background: #fff; border: 2px solid #000; box-shadow: 8px 8px 0 #000; position: relative; overflow: hidden; }
.shot img { display: block; width: 100%; }
.lbl { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 22px; text-align: center; margin-top: 16px; }
.lbl span { font-weight: 300; text-transform: none; display: block; font-size: 18px; }
.card { box-sizing: border-box; border: 2px solid #000; border-radius: 6px; padding: 5px 6px 4px; background: #fff; width: 164px; }
.card .ct { font-family: 'Oswald'; font-weight: 700; font-size: 15px; min-height: 32px; text-transform: uppercase; line-height: 1.05; }
.card svg { display: block; width: 100%; height: auto; }
""".replace("ACCENT", ACCENT)


def sq_doc(body):
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{font_css()}'
            f'html,body{{margin:0;background:#fff}}{SQ_CSS}</style></head><body>{body}</body></html>')


def cover_square():
    arts = cover_art(w=400, S=7.0)
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div>'
        f'<div class="body" style="justify-content:space-evenly">'
        f'<div class="cart" style="width:640px">{arts[0]}{arts[1]}{arts[2]}</div>'
        f'<div><div class="hd" style="font-size:66px">Note Naming</div>'
        f'<div class="hd" style="font-size:120px">Speed Drills</div>'
        f'<div class="sub" style="font-size:28px;margin-top:12px">One-minute drills · treble, bass and alto clef</div></div>'
        f'</div><div class="band">Grades 3–8 <em>·</em> 30 drill pages <em>·</em> answer keys</div></div>')


def preview_square_1(img):
    labs = ["Treble clef", "Bass clef", "Alto clef"]
    subs = ["Drill 5 · one ledger line", "Drill 8 · sharps and flats", "Drill 6 · two ledger lines"]
    shots = "".join(f'<div style="width:290px"><div class="shot"><img src="{img[i]}"></div>'
                    f'<div class="lbl">{labs[i]}<span>{subs[i]}</span></div></div>' for i in range(3))
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div><div class="body">'
        f'<div class="hd" style="font-size:74px;margin-top:20px">Three clefs, one minute</div>'
        f'<div class="sub" style="font-size:27px;margin-top:8px">30 notes per drill · write the letter name under each</div>'
        f'<div style="display:flex;gap:30px;margin-top:48px">{shots}</div></div>'
        f'<div class="band">10 drills per clef <em>·</em> 30 drill pages <em>·</em> grades 3–8</div></div>')


def preview_square_2(ws, key):
    pair = "".join(f'<div style="width:400px"><div class="shot"><img src="{src}"></div><div class="lbl">{lab}</div></div>'
                   for src, lab in ((ws, "Drill page"), (key, "Answer key")))
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div><div class="body">'
        f'<div class="hd" style="font-size:70px;margin-top:20px">Answer keys included</div>'
        f'<div class="sub" style="font-size:27px;margin-top:8px">Check every note, item by item</div>'
        f'<div style="display:flex;gap:44px;margin-top:40px">{pair}</div></div>'
        f'<div class="band">Keys for all 30 drills <em>·</em> progress chart</div></div>')


# preview card 5-7: exactly 1, 2, 3 ledger lines (below in treble/alto, above in bass for variety)
CARD_LEDGER_STEPS = {5: {"treble": -2, "bass": 10, "alto": -2},
                     6: {"treble": 12, "bass": -4, "alto": 12},
                     7: {"treble": -6, "bass": 14, "alto": -6}}


def preview_square_3(drills):
    cards = []
    for n in range(1, NDRILL + 1):
        staves = []
        for c in CLEFS:
            s, a = drills[(c, n)][0]
            if n in CARD_LEDGER_STEPS:   # cards must show exactly what the title says
                s, a = CARD_LEDGER_STEPS[n][c], None
            S = 4.0
            top = 3.7 * S
            h = top + 4 * S + 3.5 * S + 0.8 * S
            parts = staff_open(150, h, S, top, f"card:{drill_id(c, n)}")
            parts.append(clef_svg(c, S, top))
            parts.append(note_svg(c, s, a, 100, S, top))
            parts.append("</svg>")
            staves.append("".join(parts))
        cards.append(f'<div class="card"><div class="ct">{n}. {escape(LEVELS[n - 1][0])}</div>{"".join(staves)}</div>')
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div><div class="body">'
        f'<div class="hd" style="font-size:66px;margin-top:16px">Ten levels in every clef</div>'
        f'<div class="sub" style="font-size:25px;margin-top:6px">Lines and spaces, then ledger lines, then sharps and flats</div>'
        f'<div style="display:flex;flex-wrap:wrap;gap:14px;width:880px;margin-top:22px;justify-content:center">{"".join(cards)}</div></div>'
        f'<div class="band">Treble <em>·</em> bass <em>·</em> alto</div></div>')


# ------------------------------------------------------------------ listing files
PAGE_LIST = [
    ("Cover", 1),
    ("Teacher notes with the ten levels and where to start", 1),
    ("Student guide: how to drill, scoring and tricks", 1),
    ("Clef reference: every note in treble, bass and alto clef with its name", 1),
    ("Progress chart (bar graph for all 30 drills)", 1),
    ("Drill log (three tries per drill)", 1),
    ("Treble clef drills 1–10, 30 notes each", NDRILL),
    ("Bass clef drills 1–10, 30 notes each", NDRILL),
    ("Alto clef drills 1–10, 30 notes each", NDRILL),
    ("Answer keys (5 drills per page, item by item)", len(KEY_PAGES)),
    ("Terms of use and credits", 1),
]
assert sum(n for _, n in PAGE_LIST) == TOTAL_PAGES


def upload_md():
    included = "\n".join(f"• {lab} ({n} page{'s' if n != 1 else ''})" for lab, n in PAGE_LIST)
    return f"""# UPLOAD: {TITLE} (TpT 043)

These fields follow the order of TpT's "Add a resource" form. Evergreen item: list any time.

**Files to attach**
- Resource (digital download): `{SLUG}.pdf`, {TOTAL_PAGES} pages, US Letter.
- Thumbnails, in this order: `cover.png`, `preview-1.png`, `preview-2.png`, `preview-3.png` (all 2000 × 2000).
- Preview file: `{SLUG}-PREVIEW.pdf`, 4 watermarked pages.

## 1. Title

```
{UPLOAD_TITLE}
```

## 2. Description

```
{UPLOAD_TITLE}: 30 one-minute note naming drills, 10 each for treble clef, bass clef and alto clef. Each drill is a grid of 30 single notes; students write the letter name under every note while the timer runs, then check with the answer key and colour their progress chart. Quick, low-prep practice for general music, band, orchestra and choir in grades 3–8.

WHAT'S INCLUDED ({TOTAL_PAGES} pages, PDF, US Letter)
{included}

THE TEN LEVELS (the same ladder in every clef)
1. Lines  2. Spaces  3. Lines and spaces  4. Just above and below the staff  5. One ledger line  6. Two ledger lines  7. Three ledger lines  8. Sharps and flats  9. Sharps, flats and ledger lines  10. Mixed challenge

HOW TO USE
Set a one-minute timer, students name as many notes as they can, then count their correct answers (out of 30) and shade a bar on the progress chart. Repeat any drill for a new personal best. Great as a bell ringer, warm-up, homework, sub-plan filler or station. Alto clef is drawn correctly, with the C clef centred on the middle line (middle C), so violists and anyone learning to read it get real practice.

• Grades 3–8 (treble from grade 3; bass and alto for older beginners and orchestra)
• 30 notes per drill, new notes on every page; answer keys for every drill
• Print in black and white; the answer keys use one accent color
• Letter names only (no octave numbers); no songs, lyrics or copyrighted characters

{DISCLOSURE}
```

## 3. Grades

5, 6, 7, 8 (the form takes at most four; the description says grades 3–8)

## 4. Subjects

- Music
- Instrumental Music

## 5. Resource type (tags)

- Worksheets
- Printables
- Activities
- Bell Ringers

## 6. Price

${PRICE[:-3]} (evergreen)

## 7. Page list (must total the PDF: {TOTAL_PAGES} pages)

{included}
"""


def tpt_json():
    return {
        "price": PRICE, "license_price": PRICE, "tax_code": "Other Digital Goods - No Physical Media",
        "grades": ["5th-grade", "6th-grade", "7th-grade", "8th-grade"],
        "subjects": ["Music", "Instrumental Music"],
        "tags": ["Worksheets", "Printables", "Activities", "Bell Ringers"],
        "formats": ["PDF"], "pages": TOTAL_PAGES, "answer_key": "Included",
        "files": {"product": f"{SLUG}.pdf", "preview": f"{SLUG}-PREVIEW.pdf", "thumb1": "cover.png",
                  "thumb2": "preview-1.png", "thumb3": "preview-2.png", "thumb4": "preview-3.png"},
    }


# ------------------------------------------------------------------ render
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


def build():
    os.makedirs(BUILD, exist_ok=True)
    drills = make_drills()
    full = write("resource.html", html_doc(full_pages(drills), TITLE))
    prev = write("preview.html", html_doc(preview_pages(drills), "Preview"))
    render([{"html": full, "pdf": PDF}, {"html": prev, "pdf": PREVIEW_PDF}])
    for i in range(1, 5):
        subprocess.run(["pdftoppm", "-png", "-r", "110", "-f", str(i), "-l", str(i), "-singlefile", PREVIEW_PDF,
                        os.path.join(BUILD, f"pv{i}")], check=True)
    sq = [write("cover.html", cover_square()), write("p1.html", preview_square_1(["pv1.png", "pv2.png", "pv3.png"])),
          write("p2.html", preview_square_2("pv1.png", "pv4.png")), write("p3.html", preview_square_3(drills))]
    render([{"html": h, "png": o, "width": 1000, "height": 1000, "scale": 2} for h, o in zip(sq, [COVER_PNG] + PREVIEW_PNGS)])
    with open(UPLOAD, "w") as f:
        f.write(upload_md())
    with open(TPT_JSON, "w") as f:
        json.dump(tpt_json(), f, indent=2)
        f.write("\n")
    print(f"built {PDF}, {PREVIEW_PDF}, cover + 3 previews, UPLOAD.md, tpt.json ({TOTAL_PAGES} pages)")


# ------------------------------------------------------------------ checks
NUM = r"(-?[\d.]+)"
RX_SVG = re.compile(r'<svg class="ns" data-ctx="([^"]*)" data-s="([\d.]+)"[^>]*viewBox="0 0 ([\d.]+) ([\d.]+)"[^>]*>(.*?)</svg>', re.S)
RX_SL = re.compile(rf'<line class="sl" x1="{NUM}" y1="{NUM}" x2="{NUM}" y2="{NUM}"')
RX_CLEF = re.compile(rf'<text class="clef" x="{NUM}" y="{NUM}" font-family="Bravura" font-size="{NUM}"[^>]*>&#x([0-9A-F]+);</text>')
RX_NT = re.compile(r'<g class="nt">(.*?)</g>', re.S)
RX_LED = re.compile(rf'<line class="led" x1="{NUM}" y1="{NUM}" x2="{NUM}" y2="{NUM}"')
RX_ACC = re.compile(rf'<text class="acc" x="{NUM}" y="{NUM}" font-family="Bravura" font-size="{NUM}"[^>]*>&#x([0-9A-F]+);</text>')
RX_HEAD = re.compile(rf'<text class="head" x="{NUM}" y="{NUM}" font-family="Bravura" font-size="{NUM}"[^>]*>&#x([0-9A-F]+);</text>')
RX_STEM = re.compile(rf'<line class="stem" data-dir="(up|down)" x1="{NUM}" y1="{NUM}" x2="{NUM}" y2="{NUM}"')
RX_LABEL = re.compile(r'<text class="rl" [^>]*>([A-G])</text>')

LINE_LETTERS = {"treble": "EGBDF", "bass": "GBDFA", "alto": "FACEG"}     # bottom to top
SPACE_LETTERS = {"treble": "FACE", "bass": "ACEG", "alto": "GBDF"}
ANCHOR = {"G": ("treble", "G"), "F": ("bass", "F"), "C": ("alto", "C")}


def parse_notes(svg_body, S, h, ctx):
    """Parse one rendered staff. Returns (notes, errors); every name is recomputed from drawn geometry only."""
    errs = []
    lines = [float(m.group(2)) for m in RX_SL.finditer(svg_body)]
    if len(lines) != 5:
        return [], [f"{ctx}: {len(lines)} staff lines"]
    if any(abs((lines[i + 1] - lines[i]) - S) > 0.02 for i in range(4)):
        errs.append(f"{ctx}: staff line spacing is not {S}")
    bottom = max(lines)
    cm = RX_CLEF.search(svg_body)
    if not cm:
        return [], [f"{ctx}: no clef"]
    clef = GLYPH_CLEF.get(int(cm.group(4), 16))
    if clef is None:
        return [], [f"{ctx}: unknown clef glyph"]
    # anchor pitch of the drawn clef glyph, independent of BOTTOM_LINE: G clef -> G4, F clef -> F3, C clef -> C4
    anchor_letter, anchor_oct = {"treble": ("G", 4), "bass": ("F", 3), "alto": ("C", 4)}[clef]
    cy = float(cm.group(2))
    anchor_step = round((bottom - cy) / (S / 2))
    want_anchor = {"treble": 2, "bass": 6, "alto": 4}[clef]   # 2nd line, 4th line, middle line from the bottom
    if anchor_step != want_anchor:
        errs.append(f"{ctx}: {clef} clef is drawn on step {anchor_step}, must be {want_anchor}")
    notes = []
    for nt in RX_NT.finditer(svg_body):
        b = nt.group(1)
        hm = RX_HEAD.search(b)
        hx, hy = float(hm.group(1)), float(hm.group(2))
        if abs(float(hm.group(3)) - 4 * S) > 0.01:
            errs.append(f"{ctx}: notehead size")
        off = (cy - hy) / (S / 2)
        if abs(off - round(off)) > 0.02:
            errs.append(f"{ctx}: notehead off the grid ({off})")
        off = round(off)
        pos = LETTERS.index(anchor_letter) + off
        letter = LETTERS[pos % 7]
        octave = anchor_oct + pos // 7
        step = round((bottom - hy) / (S / 2))
        # cross-check 1: line/space letter strings
        if 0 <= step <= 8:
            want = LINE_LETTERS[clef][step // 2] if step % 2 == 0 else SPACE_LETTERS[clef][step // 2]
            if want != letter:
                errs.append(f"{ctx}: staff-position strings say {want}, geometry says {letter}")
        acc = ""
        am = RX_ACC.search(b)
        if am:
            acc = GLYPH_ACC.get(int(am.group(4), 16), "?")
            ax = float(am.group(1))
            if abs(float(am.group(2)) - hy) > 0.02:
                errs.append(f"{ctx}: accidental not on the notehead line")
            if not ax + (ACC_W[acc] * S) < hx:
                errs.append(f"{ctx}: accidental overlaps the notehead")
            if acc == "#" and letter not in SHARP_OK or acc == "b" and letter not in FLAT_OK:
                errs.append(f"{ctx}: unwanted accidental on {letter}")
        hw = HEAD_W * S
        # ledger lines: exactly the even steps between the staff and the note
        need = set(e for e in range(-2, step - 1, -2)) if step < 0 else set()
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
            got.append(round(e))
            if abs(e - round(e)) > 0.02:
                errs.append(f"{ctx}: ledger line off grid")
        if sorted(got) != sorted(need):
            errs.append(f"{ctx}: ledger lines {sorted(got)} but note at step {step} needs {sorted(need)}")
        # stem: direction by position, correct side, reaches 3.5 spaces or the middle line, starts at the head
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
                if not abs(x1 - (hx + hw)) <= 0.13 * S:
                    errs.append(f"{ctx}: up-stem not on the right edge of the head")
                length = y1 - y2
                end_y = y2
                if abs(y1 - (hy - 0.168 * S)) > 0.05:
                    errs.append(f"{ctx}: up-stem does not start at the head")
                mid_y = bottom - 4 * (S / 2) * 1.0
                if end_y > mid_y + 0.05 and step < 4:
                    errs.append(f"{ctx}: up-stem does not reach the middle line")
            else:
                if not abs(x1 - hx) <= 0.13 * S:
                    errs.append(f"{ctx}: down-stem not on the left edge of the head")
                length = y2 - y1
                end_y = y2
                if abs(y1 - (hy + 0.168 * S)) > 0.05:
                    errs.append(f"{ctx}: down-stem does not start at the head")
                mid_y = bottom - 4 * (S / 2)
                if end_y < mid_y - 0.05:
                    errs.append(f"{ctx}: down-stem does not reach the middle line")
            if length < 3.5 * S - 0.05:
                errs.append(f"{ctx}: stem shorter than 3.5 spaces")
            if min(y1, y2) < 0 or max(y1, y2) > h:
                errs.append(f"{ctx}: stem leaves the drawing")
        if hy - 0.6 * S < 0 or hy + 0.6 * S > h:
            errs.append(f"{ctx}: notehead clipped by the drawing edge")
        for ly in [float(lm.group(2)) for lm in RX_LED.finditer(b)]:
            if ly < 0 or ly > h:
                errs.append(f"{ctx}: ledger line outside the drawing")
        name = letter + acc
        notes.append({"clef": clef, "step": step, "name": name, "letter": letter, "octave": octave})
    return notes, errs


def verify_html():
    errs = []
    path = os.path.join(BUILD, "resource.html")
    if not os.path.exists(path):
        return ["build/resource.html missing: run gen.py first"]
    html = open(path).read()
    pages = html.split('<section class="page')[1:]
    if len(pages) != TOTAL_PAGES:
        errs.append(f"resource.html has {len(pages)} pages, expected {TOTAL_PAGES}")
    drills = make_drills()
    ws_names = {}      # (drill id, item) -> name recomputed from the rendered worksheet
    nnotes = 0
    ctxs = set()
    for pm in RX_SVG.finditer(html):
        ctx, S, w, h, body = pm.group(1), float(pm.group(2)), float(pm.group(3)), float(pm.group(4)), pm.group(5)
        notes, e = parse_notes(body, S, h, ctx)
        errs += e
        nnotes += len(notes)
        kind = ctx.split(":")[0]
        if kind == "drill":
            _, did, item = ctx.split(":")
            if len(notes) != 1:
                errs.append(f"{ctx}: {len(notes)} notes in one cell")
                continue
            ws_names[(did, int(item))] = notes[0]["name"]
            clef = {v: k for k, v in CLEF_PREFIX.items()}[did[0]]
            if notes[0]["clef"] != clef:
                errs.append(f"{ctx}: drawn in the {notes[0]['clef']} clef, drill is {clef}")
        elif kind in ("ref", "art"):
            labels = RX_LABEL.findall(body)
            if len(labels) != len(notes):
                errs.append(f"{ctx}: {len(labels)} labels for {len(notes)} notes")
            for nname, lab in zip(notes, labels):
                if nname["letter"] != lab:
                    errs.append(f"{ctx}: label {lab} but geometry says {nname['name']}")
            if kind == "ref":
                c = ctx.split(":")[1]
                cs = [n for n in notes if n["letter"] == "C" and n["octave"] == 4]
                want = {"treble": -2, "bass": 10, "alto": 4}[c]
                if len(cs) != 1 or cs[0]["step"] != want:
                    errs.append(f"{ctx}: middle C should be on step {want}")
        ctxs.add(kind)
    # worksheets: counts, and names against the drill data
    for c in CLEFS:
        for n in range(1, NDRILL + 1):
            did = drill_id(c, n)
            items = drills[(c, n)]
            got = [(i, ws_names.get((did, i))) for i in range(1, PER_DRILL + 1)]
            if any(v is None for _, v in got) or len([k for k in ws_names if k[0] == did]) != PER_DRILL:
                errs.append(f"{did}: worksheet does not hold exactly {PER_DRILL} items")
                continue
            for i, (s, a) in enumerate(items, 1):
                if ws_names[(did, i)] != note_name(c, s, a)[0]:
                    errs.append(f"{did} item {i}: drawn note reads {ws_names[(did, i)]}, data says {note_name(c, s, a)[0]}")
            lo, hi, accp = LEVELS[n - 1][1], LEVELS[n - 1][2], LEVELS[n - 1][3]
            for i, (s, a) in enumerate(items, 1):
                if not lo <= s <= hi:
                    errs.append(f"{did} item {i}: step {s} outside level range")
                if n == 1 and s % 2:
                    errs.append(f"{did} item {i}: a space on the lines page")
                if n == 2 and s % 2 == 0:
                    errs.append(f"{did} item {i}: a line on the spaces page")
                if n < 8 and a:
                    errs.append(f"{did} item {i}: accidental on an early page")
            if n == 8 and any(s < 0 or s > 8 for s, _ in items):
                errs.append(f"{did}: ledger line on the in-staff accidental page")
    # answer keys: item by item
    key = {}
    for m in re.finditer(r'<div class="kc" data-drill="([A-Z]\d+)" data-item="(\d+)" data-ans="([A-G][#b]?)"><i>(\d+)</i><b>([A-G])(?:<span class="ac">&#x([0-9A-F]+);</span>)?</b></div>', html):
        did, item, ans, shown_i, letter, accg = m.group(1), int(m.group(2)), m.group(3), int(m.group(4)), m.group(5), m.group(6)
        if (did, item) in key:
            errs.append(f"key: {did} item {item} twice")
        if shown_i != item:
            errs.append(f"key: {did} item {item} labelled {shown_i}")
        shown = letter + (GLYPH_ACC.get(int(accg, 16), "?") if accg else "")
        if shown != ans:
            errs.append(f"key: {did} item {item}: shows {shown}, data-ans {ans}")
        key[(did, item)] = ans
    n_kc = html.count('class="kc"')
    if n_kc != len(key):
        errs.append(f"key: {n_kc} key cells but {len(key)} parsed")
    for c in CLEFS:
        for n in range(1, NDRILL + 1):
            did = drill_id(c, n)
            kn = sorted(k[1] for k in key if k[0] == did)
            wn = sorted(k[1] for k in ws_names if k[0] == did)
            if kn != wn or len(kn) != PER_DRILL:
                errs.append(f"{did}: key has {len(kn)} items, worksheet {len(wn)}")
            for i in range(1, PER_DRILL + 1):
                if key.get((did, i)) != ws_names.get((did, i)):
                    errs.append(f"{did} item {i}: key {key.get((did, i))} vs worksheet note {ws_names.get((did, i))}")
    # drill pages in the document hold 30 cells each, in order
    for c in CLEFS:
        for n in range(1, NDRILL + 1):
            did = drill_id(c, n)
            cells = re.findall(rf'<div data-drill="{did}" data-item="(\d+)">', html)
            if [int(x) for x in cells] != list(range(1, PER_DRILL + 1)):
                errs.append(f"{did}: worksheet cells not 1..{PER_DRILL} in order")
    return errs, nnotes, len(key)


MEASURE_JS = r"""
const { chromium } = require('playwright'); const url = require('url'); const fs = require('fs');
(async () => { const files = JSON.parse(process.argv[2]); const b = await chromium.launch(); const out = [];
 for (const f of files) { const p = await (await b.newContext({viewport:{width:1000,height:1000}})).newPage();
  await p.goto(url.pathToFileURL(f).href, {waitUntil:'load'}); await p.evaluate(() => document.fonts.ready);
  out.push(await p.evaluate(() => { const band = document.querySelector('.band').getBoundingClientRect().top; let maxb = 0, maxr = 0, minl = 9999, minimg = [];
   document.querySelectorAll('.sq *').forEach(e => { if (e.closest('.band') || e.classList.contains('body') || e.classList.contains('sq')) return;
     const r = e.getBoundingClientRect(); if (r.width === 0 || r.height === 0) return; if (e.children.length && !e.matches('svg,img,text')) return;
     maxb = Math.max(maxb, r.bottom); maxr = Math.max(maxr, r.right); minl = Math.min(minl, r.left); });
   const imgs = [...document.querySelectorAll('.shot img')].map(i => ({nat: i.naturalHeight / i.naturalWidth, w: i.clientWidth, h: i.clientHeight, par: i.parentElement.clientHeight}));
   const shots = [...document.querySelectorAll('.shot')].map(s => s.getBoundingClientRect().bottom + 8);
   return { band, maxb, maxr, minl, imgs, shotsBottom: Math.max(0, ...shots), wm: document.querySelectorAll('.swm,.wm').length }; })); }
 console.log(JSON.stringify(out)); await b.close(); })();
"""


def verify_squares():
    errs = []
    files = [os.path.join(BUILD, n) for n in ("cover.html", "p1.html", "p2.html", "p3.html")]
    if not all(os.path.exists(f) for f in files):
        return ["build/*.html missing: run gen.py first"]
    js = os.path.join(BUILD, "measure.js")
    open(js, "w").write(MEASURE_JS)
    r = subprocess.run(["node", js, json.dumps(files)], capture_output=True, text=True, env=node_env())
    if r.returncode:
        return [f"measure failed: {r.stderr[-300:]}"]
    for f, m in zip(files, json.loads(r.stdout)):
        nm = os.path.basename(f)
        if m["maxb"] > m["band"] - 6:
            errs.append(f"{nm}: content reaches y={m['maxb']:.0f}, behind the footer band at y={m['band']:.0f}")
        if m["shotsBottom"] > m["band"] - 6:
            errs.append(f"{nm}: page shot (with shadow) reaches y={m['shotsBottom']:.0f}, behind the band at {m['band']:.0f}")
        if m["maxr"] > 1000 or m["minl"] < 0:
            errs.append(f"{nm}: content outside the frame")
        for im in m["imgs"]:
            if abs(im["h"] - im["par"]) > 3 or abs(im["h"] / im["w"] - im["nat"]) > 0.01:
                errs.append(f"{nm}: page shot is cropped or stretched")
        if m["wm"]:
            errs.append(f"{nm}: extra watermark layer on top of the (already watermarked) page shots")
    return errs


def pdf_fonts(path):
    out = subprocess.run(["pdffonts", path], capture_output=True, text=True, check=True).stdout.splitlines()[2:]
    return [(line.split()[0], line.split()[-5]) for line in out]


def load_json(name):
    return json.load(open(os.path.join(TPT, name)))


def verify_files():
    errs = []
    from pypdf import PdfReader
    from PIL import Image
    for p in [PDF, PREVIEW_PDF, COVER_PNG, *PREVIEW_PNGS, UPLOAD, TPT_JSON, os.path.join(TPT, "STYLE.md"), RENDER_JS]:
        if not os.path.exists(p):
            errs.append(f"missing {os.path.relpath(p, TPT)}")
    if errs:
        return errs
    for path, want_pages in ((PDF, TOTAL_PAGES), (PREVIEW_PDF, 4)):
        rd = PdfReader(path)
        if len(rd.pages) != want_pages:
            errs.append(f"{os.path.basename(path)}: {len(rd.pages)} pages, expected {want_pages}")
        for i, pg in enumerate(rd.pages):
            w, h = float(pg.mediabox.width), float(pg.mediabox.height)
            if abs(w - 612) > 1 or abs(h - 792) > 1:
                errs.append(f"{os.path.basename(path)} p{i + 1}: {w:.0f}x{h:.0f}pt, not US Letter")
        fonts = pdf_fonts(path)
        for name, emb in fonts:
            if emb != "yes":
                errs.append(f"{os.path.basename(path)}: font {name} not embedded")
        names = " ".join(n for n, _ in fonts).lower().replace(" ", "")
        for fam in ("bravura", "oswald", "sourcesans3"):
            if fam not in names:
                errs.append(f"{os.path.basename(path)}: {fam} not found in PDF fonts")
    rd = PdfReader(PDF)
    for i, pg in enumerate(rd.pages):
        t = (pg.extract_text() or "").upper().replace("\n", " ")
        n = i + 1
        if len(t.strip()) < 40:
            errs.append(f"PDF page {n} looks blank")
        if "PREVIEW" in t:
            errs.append(f"PDF page {n}: contains a watermark")
        if P_DR0 <= n < P_KEY0:
            k = n - P_DR0
            c, d = CLEFS[k // NDRILL], k % NDRILL + 1
            if CLEF_LABEL[c].upper() not in t or f"{d}. {LEVELS[d - 1][0].upper()}" not in t:
                errs.append(f"PDF page {n}: drill heading for {c} {d} missing")
        if P_KEY0 <= n < P_TERMS and "ANSWER KEY" not in t:
            errs.append(f"PDF page {n}: answer key heading missing")
    prd = PdfReader(PREVIEW_PDF)
    for i in range(4):
        t = prd.pages[i].extract_text() or ""
        if t.count("PREVIEW") != 1:
            errs.append(f"preview PDF page {i + 1}: watermark appears {t.count('PREVIEW')} times, expected once")
    for p in [COVER_PNG, *PREVIEW_PNGS]:
        if Image.open(p).size != (2000, 2000):
            errs.append(f"{os.path.basename(p)}: not 2000x2000")
    up = open(UPLOAD).read()
    m = re.search(r"^## 1\. Title\s*\n+```\n(.+?)\n```", up, re.M | re.S)
    if not m:
        errs.append("UPLOAD.md: title block not found")
    elif len(m.group(1).strip()) > 80:
        errs.append(f"UPLOAD.md: title is {len(m.group(1).strip())} chars (max 80)")
    for need in (DISCLOSURE, "$4", f"{TOTAL_PAGES} pages", "30 "):
        if need not in up:
            errs.append(f"UPLOAD.md: missing '{need}'")
    if re.search(r"hand-?checked|checked by hand|handmade|classroom-tested", up, re.I):
        errs.append("UPLOAD.md: says hand-checked/handmade/classroom-tested")
    if re.search(r"christmas|halloween|thanksgiving|winter|december|holiday|autumn|fall\b", up, re.I):
        errs.append("UPLOAD.md: seasonal word in an evergreen item")
    sec = up.split("## 7. Page list")[1]
    nums = [int(x) for x in re.findall(r"\((\d+) pages?\)", sec)]
    if sum(nums) != len(rd.pages):
        errs.append(f"UPLOAD.md page list totals {sum(nums)}, PDF has {len(rd.pages)}")
    desc_nums = [int(x) for x in re.findall(r"\((\d+) pages?\)", up.split("## 2. Description")[1].split("## 3.")[0])]
    if sum(desc_nums) != len(rd.pages):
        errs.append(f"UPLOAD.md description list totals {sum(desc_nums)}, PDF has {len(rd.pages)}")
    tj = json.load(open(TPT_JSON))
    tags, subs = set(load_json("TAG-OPTIONS.json")["options"]), set(load_json("SUBJECT-OPTIONS.json"))
    if not 1 <= len(tj["tags"]) <= 6 or any(t not in tags for t in tj["tags"]):
        errs.append(f"tpt.json tags invalid: {tj['tags']}")
    if not 1 <= len(tj["subjects"]) <= 3 or any(s not in subs for s in tj["subjects"]):
        errs.append(f"tpt.json subjects invalid: {tj['subjects']}")
    if not 1 <= len(tj["grades"]) <= 4:
        errs.append("tpt.json grades must be 1-4")
    if tj.get("pages") != len(rd.pages):
        errs.append(f"tpt.json pages {tj.get('pages')} != {len(rd.pages)}")
    for slot, fn in tj["files"].items():
        if not os.path.exists(os.path.join(HERE, fn)):
            errs.append(f"tpt.json file {slot}: {fn} missing")
    if tj["price"] != PRICE:
        errs.append(f"tpt.json price should be {PRICE}")
    return errs


def check():
    errs = []
    drills = make_drills()
    for (c, n), items in drills.items():
        if len(items) != PER_DRILL:
            errs.append(f"{drill_id(c, n)}: {len(items)} items")
    # clef sanity from the data side
    for c, want in (("treble", {"E": 4}), ("bass", {"G": 2}), ("alto", {"F": 3})):
        pass
    if note_name("alto", 4)[0] != "C" or note_name("alto", 4)[1] != 4:
        errs.append("alto middle line is not C4")
    if [note_name("alto", s)[0] for s in (0, 2, 4, 6, 8)] != list("FACEG") or [note_name("alto", s)[0] for s in (1, 3, 5, 7)] != list("GBDF"):
        errs.append("alto lines/spaces wrong")
    res = verify_html()
    nn = nk = 0
    if isinstance(res, tuple):
        e2, nn, nk = res
        errs += e2
    else:
        errs += res
    errs += verify_squares()
    errs += verify_files()
    if errs:
        print("CHECK FAILED")
        print("\n".join(" - " + e for e in errs[:60]))
        sys.exit(1)
    print(f"CHECK OK: {len(drills)} drills x {PER_DRILL} items; {nn} rendered notes recomputed from staff geometry in all three clefs "
          f"(ledger lines, stems, accidentals ok); {nk} key entries match their drill items one by one; worksheet and key counts equal on every page; "
          f"PDF {TOTAL_PAGES} Letter pages, preview 4 (one watermark each), fonts embedded; images 2000x2000, nothing behind the footer bands; "
          f"UPLOAD.md page list totals {TOTAL_PAGES}; tpt.json ok.")


if __name__ == "__main__":
    if "--check" in sys.argv:
        check()
    else:
        build()
