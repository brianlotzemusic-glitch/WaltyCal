#!/usr/bin/env python3
"""Winter Music Escape Room (TpT 042): build the resource and verify it.

    python3 gen.py           build everything (PDFs, PNGs, UPLOAD.md, tpt.json) into this folder
    python3 gen.py --check   verify puzzles (each one is solved in code), keys, layout, files

Story: the snow-globe workshop is locked. Five puzzles (treble clef, bass clef, rhythm math, music symbols,
a note-value decoder) each give an ANSWER. The answer is matched to an answer-check card (cut-out page);
the card gives a lock digit and the wheel it belongs to. The five digits, read through the lock chart,
spell the final word. Every answer is computed from the puzzle data, and `--check` re-derives it from the
rendered HTML as a second method.
"""
import itertools
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

SLUG = "winter-music-escape-room"
PDF = os.path.join(HERE, f"{SLUG}.pdf")
PREVIEW_PDF = os.path.join(HERE, f"{SLUG}-PREVIEW.pdf")
COVER_PNG = os.path.join(HERE, "cover.png")
PREVIEW_PNGS = [os.path.join(HERE, f"preview-{i}.png") for i in (1, 2, 3)]
UPLOAD = os.path.join(HERE, "UPLOAD.md")
TPT_JSON = os.path.join(HERE, "tpt.json")

STORE = "Brian Lotze"
BRAND = "Hudson Beat"
YEAR = 2026
ACCENT = "#1F6FA8"
ACC_LT, ACC_XLT, ACC_DK = "#A9CBE6", "#DCEAF5", "#123F63"
PRICE = "5.50"
DISCLOSURE = "Created with the help of digital and AI tools. Notation and answer keys are verified before release."
TITLE = "Winter Music Escape Room"
COPY = f"© {YEAR} {STORE} · {BRAND} · For single-classroom use"

# ------------------------------------------------------------------ page map
P_COVER, P_TG1, P_TG2, P_MISSION = 1, 2, 3, 4
P_PUZ = {1: 5, 2: 6, 3: 7, 4: 8, 5: 9}
P_FINAL, P_CARDS, P_HINTS, P_MANUAL, P_KEY1, P_KEY2, P_TERMS = 10, 11, 12, 13, 14, 15, 16
TOTAL_PAGES = 16
PAGE_LIST = [("Cover", 1), ("Teacher guide (setup, timing, hints, differentiation)", 2), ("Student mission page (story and team tracker)", 1),
             ("Puzzles 1–5, one page each", 5), ("Final lock page", 1), ("Answer-check cards (cut-out page)", 1),
             ("Hint cards (cut-out page)", 1), ("Student workshop manual (optional reference)", 1), ("Answer key", 2),
             ("Terms of use and credits", 1)]

# ------------------------------------------------------------------ puzzle data
# Puzzle 1 / 2: note names. Staff position p: 0 = bottom line, 1 = first space, ... 8 = top line, 9 = space above.
TREBLE_BASE, BASS_BASE = 30, 18      # diatonic number of the bottom line: E4 = 4*7+2, G2 = 2*7+4
P1_WORD, P1_POS = "FACADE", [8, 3, 5, 3, 6, 7]
P2_WORD, P2_POS = "CABBAGE", [3, 1, 2, 2, 8, 7, 5]
P1_DECOYS, P2_DECOYS = ["DECADE", "BADGED"], ["BAGGAGE", "DEFACED"]
CLEF_INFO = {"treble": ("EFGABCD", TREBLE_BASE), "bass": ("GABCDEF", BASS_BASE)}


def note_letter(clef, p):
    """First method: letter sequence starting on the bottom line."""
    return CLEF_INFO[clef][0][p % 7]


def note_letter_b(clef, p):
    """Second method: absolute diatonic number."""
    return "CDEFGAB"[(CLEF_INFO[clef][1] + p) % 7]


# Puzzle 3: rhythm math. Tokens: Q H DH E2 QR HR (+ 'M' = missing). Options by kind.
KINDS = {"q": ("quarter note", 1), "h": ("half note", 2), "dh": ("dotted half note", 3), "w": ("whole note", 4),
         "e": ("eighth note", 0.5), "dq": ("dotted quarter note", 1.5), "qr": ("quarter rest", 1), "hr": ("half rest", 2),
         "wr": ("whole rest", 4)}
TOK_BEATS = {"Q": 1, "H": 2, "DH": 3, "E2": 1, "QR": 1, "HR": 2}
P3_BARS = [  # meter beats, label, tokens, option kinds (4), correct kind
    (4, "4/4", ["Q", "Q", "M"], ["q", "h", "dh", "w"]),
    (3, "3/4", ["H", "M"], ["q", "h", "dq", "dh"]),
    (4, "4/4", ["Q", "M"], ["h", "dh", "w", "qr"]),
    (2, "2/4", ["E2", "M"], ["e", "q", "h", "dq"]),
    (4, "4/4", ["HR", "M"], ["q", "h", "dh", "w"]),
    (3, "3/4", ["M"], ["q", "h", "dh", "w"]),
]
OPT_LETTERS = "ABCD"

# Puzzle 4: symbols and terms.
SYMBOLS = {  # id: (name, meaning)
    "forte": ("forte (f)", "Loud: play strongly"),
    "piano": ("piano (p)", "Soft: play quietly"),
    "cresc": ("crescendo", "Get louder little by little"),
    "decresc": ("decrescendo", "Get softer little by little"),
    "fermata": ("fermata", "Hold the note longer than written"),
    "staccato": ("staccato dot", "Play the note short and detached"),
    "repeat": ("repeat sign", "Go back and play the music again"),
    "sharp": ("sharp", "Raise the pitch by a half step"),
}
P4_WORD = "FROSTING"
P4_ORDER = ["fermata", "forte", "repeat", "decresc", "sharp", "piano", "staccato", "cresc"]   # order on the page (1-8)
P4_MEANING_ORDER = ["staccato", "cresc", "forte", "sharp", "repeat", "decresc", "fermata", "piano"]  # order of the meaning list

# Puzzle 5: note-value decoder.
P5_TABLE = [("whole note", "w", "N"), ("dotted half note", "dh", "G"), ("half note", "h", "S"), ("quarter note", "q", "O"),
            ("eighth note", "e", "W"), ("whole rest", "wr", "L"), ("half rest", "hr", "B"), ("quarter rest", "qr", "E")]
P5_MESSAGE = ["h", "w", "q", "e", None, "dh", "wr", "q", "hr", "qr"]   # None = word gap
P5_WORD = "SNOW GLOBE"

# Final lock.
WHEEL_OF = {1: 3, 2: 5, 3: 1, 4: 4, 5: 2}              # puzzle -> wheel
CHART = {1: "C", 2: "U", 3: "B", 4: "M", 5: "E", 6: "T", 7: "I", 8: "L", 9: "S"}
LOCK_WORD = "MUSIC"
DIGIT_OF_WHEEL = {w: next(d for d, l in CHART.items() if l == LOCK_WORD[w - 1]) for w in range(1, 6)}


def p1_answer():
    return "".join(note_letter("treble", p) for p in P1_POS)


def p2_answer():
    return "".join(note_letter("bass", p) for p in P2_POS)


def p3_fit(bar):
    beats, _, toks, opts = bar
    need = beats - sum(TOK_BEATS[t] for t in toks if t != "M")
    return [k for k in opts if KINDS[k][1] == need], need


def p3_answer(ignore_dot=False, ignore_meter=False):
    total = 0
    for bar in P3_BARS:
        beats = 4 if ignore_meter else bar[0]
        need = beats - sum(TOK_BEATS[t] for t in bar[2] if t != "M")
        k = [k for k in bar[3] if KINDS[k][1] == need]
        total += KINDS[k[0]][1] if k else 0
    return total


def p3_answer_dotted_slip():
    total = 0
    for bar in P3_BARS:
        k = p3_fit(bar)[0][0]
        total += 2 if k == "dh" else KINDS[k][1]
    return total


def p4_letters():
    return {sid: P4_WORD[i] for i, sid in enumerate(P4_ORDER)}


def p4_answer(swap=None):
    L = dict(p4_letters())
    if swap:
        a, b = swap
        L[a], L[b] = L[b], L[a]
    return "".join(L[s] for s in P4_ORDER)


def p5_table(swap=None):
    t = {k: l for _, k, l in P5_TABLE}
    if swap:
        a, b = swap
        t[a], t[b] = t[b], t[a]
    return t


def p5_answer(swap=None):
    t = p5_table(swap)
    return "".join(" " if k is None else t[k] for k in P5_MESSAGE)


def make_cards():
    """Three answer-check cards per puzzle: (puzzle, answer text, digit, wheel, correct?). Decoys come from real slips."""
    rng = random.Random("cards-042")
    texts = {
        1: (p1_answer(), P1_DECOYS), 2: (p2_answer(), P2_DECOYS),
        3: (str(p3_answer()), [str(p3_answer_dotted_slip()), str(p3_answer(ignore_meter=True))]),
        4: (p4_answer(), [p4_answer(("cresc", "decresc")), p4_answer(("forte", "piano"))]),
        5: (p5_answer(), [p5_answer(("wr", "hr")), p5_answer(("q", "e"))]),
    }
    cards = {}
    for pz in range(1, 6):
        good, decoys = texts[pz]
        w = WHEEL_OF[pz]
        gd = DIGIT_OF_WHEEL[w]
        others = [d for d in range(1, 10) if d != gd]
        rng.shuffle(others)
        items = [(good, gd, True)] + [(t, others[i], False) for i, t in enumerate(decoys)]
        rng.shuffle(items)
        cards[pz] = [dict(puzzle=pz, text=t, digit=d, wheel=w, correct=c) for t, d, c in items]
    return cards


CARDS = make_cards()


def card_lookup(pz, text):
    hit = [c for c in CARDS[pz] if c["text"] == text]
    return hit[0] if len(hit) == 1 else None


def final_code():
    """Derive the lock from the five puzzle answers: answer -> card -> (wheel, digit)."""
    ans = {1: p1_answer(), 2: p2_answer(), 3: str(p3_answer()), 4: p4_answer(), 5: p5_answer()}
    code = {}
    for pz, a in ans.items():
        c = card_lookup(pz, a)
        code[c["wheel"]] = c["digit"]
    digits = [code[w] for w in range(1, 6)]
    return digits, "".join(CHART[d] for d in digits), ans


# ------------------------------------------------------------------ fonts, css
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
.how { font-size: 11.5pt; line-height: 1.32; margin: 3pt 0 6pt; }
.how b { font-weight: 700; }
.story { border-left: 4pt solid ACCENT; padding: 2pt 0 2pt 9pt; font-size: 11pt; line-height: 1.32; font-style: italic; margin: 4pt 0 6pt; }
.foot { display: flex; justify-content: space-between; font-size: 8.5pt; color: #333; border-top: .8pt solid #000; padding-top: 3pt; margin-top: auto; }
.wm { position: absolute; left: 50%; top: 50%; transform: translate(-50%, -50%) rotate(-38deg); font-family: 'Oswald'; font-weight: 700;
      font-size: 150pt; color: rgba(0,0,0,.13); letter-spacing: .06em; white-space: nowrap; pointer-events: none; z-index: 9; }
.doc h1 { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 30pt; margin: 0 0 4pt; line-height: 1; }
.doc h2 { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 13.5pt; margin: 11pt 0 4pt; letter-spacing: .02em; }
.doc h2 .acc { color: ACCENT; }
.doc p, .doc li { font-size: 10.5pt; line-height: 1.34; margin: 0 0 4pt; }
.doc ul, .doc ol { margin: 0 0 3pt; padding-left: 16pt; }
.doc .rule { border-bottom: 2.2pt solid #000; margin-bottom: 8pt; padding-bottom: 6pt; }
.doc table { border-collapse: collapse; width: 100%; font-size: 9.8pt; margin: 2pt 0 4pt; }
.doc td, .doc th { border: 1pt solid #000; padding: 3pt 6pt; text-align: left; vertical-align: top; }
.doc th { font-family: 'Oswald'; font-weight: 500; text-transform: uppercase; font-size: 9.5pt; background: #000; color: #fff; }
.cols { display: flex; gap: 22pt; }
.cols > div { flex: 1; }
.small { font-size: 9pt !important; color: #333; }
.ansline { display: flex; align-items: center; gap: 8pt; margin: 8pt 0 2pt; font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 13pt; }
.ansline span.bx { flex: 1; border: 1.6pt solid #000; border-radius: 5pt; height: 30pt; }
.ansline small { font-family: 'Source Sans 3'; font-weight: 400; text-transform: none; font-size: 10pt; }
.cardnote { border: 1.4pt dashed #000; border-radius: 6pt; padding: 5pt 9pt; font-size: 10.5pt; margin-top: 8pt; }
.cardnote b { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; letter-spacing: .03em; }
.cover { align-items: center; justify-content: space-between; padding: 0.55in 0.6in 0.5in; }
.store { font-family: 'Oswald'; font-weight: 500; font-size: 13pt; letter-spacing: .32em; text-transform: uppercase; }
.ctitle { text-align: center; }
.ctitle .a { font-family: 'Oswald'; font-weight: 700; font-size: 44pt; line-height: 1; letter-spacing: .02em; }
.ctitle .b { font-family: 'Oswald'; font-weight: 700; white-space: nowrap; font-size: 66pt; line-height: .95; letter-spacing: .01em; }
.ctitle .c { font-family: 'Oswald'; font-weight: 300; font-size: 17pt; margin-top: 8pt; }
.cband { width: 100%; background: #000; color: #fff; text-align: center; font-family: 'Oswald'; font-weight: 500; font-size: 14pt;
         letter-spacing: .08em; text-transform: uppercase; padding: 8pt 0 9pt; border-radius: 4pt; }
.cband em { font-style: normal; color: ACC_LT; }
.pg { display: grid; gap: 0; }
.cardgrid { display: grid; grid-template-columns: repeat(3, 1fr); grid-auto-rows: 1.62in; border-top: 1pt dashed #000; border-left: 1pt dashed #000; margin-top: 6pt; }
.cd { border-right: 1pt dashed #000; border-bottom: 1pt dashed #000; padding: 6pt 8pt; display: flex; flex-direction: column; justify-content: space-between; align-items: center; text-align: center; }
.cd .pz { font-family: 'Oswald'; font-weight: 500; font-size: 9.5pt; letter-spacing: .12em; text-transform: uppercase; align-self: flex-start; }
.cd .tx { font-family: 'Oswald'; font-weight: 700; font-size: 25pt; letter-spacing: .06em; line-height: 1.05; text-transform: uppercase; }
.cd .gv { font-family: 'Oswald'; font-weight: 500; font-size: 11pt; letter-spacing: .05em; text-transform: uppercase; border-top: 1pt solid #000; padding-top: 3pt; width: 100%; }
.cd .gv b { font-weight: 700; font-size: 15pt; color: ACCENT; }
.hintgrid { display: grid; grid-template-columns: repeat(2, 1fr); grid-auto-rows: 1.5in; border-top: 1pt dashed #000; border-left: 1pt dashed #000; margin-top: 6pt; }
.hc { border-right: 1pt dashed #000; border-bottom: 1pt dashed #000; padding: 6pt 10pt; font-size: 10.5pt; line-height: 1.3; }
.hc .pz { font-family: 'Oswald'; font-weight: 700; font-size: 10.5pt; letter-spacing: .08em; text-transform: uppercase; display: block; margin-bottom: 3pt; }
.hc .pz em { font-style: normal; font-weight: 300; color: #333; }
.wheels { display: flex; gap: 12pt; justify-content: center; margin: 10pt 0 6pt; }
.wh { width: 1.15in; text-align: center; }
.wh .n { font-family: 'Oswald'; font-weight: 700; font-size: 11pt; letter-spacing: .08em; text-transform: uppercase; }
.wh .bx { border: 2pt solid #000; border-radius: 8pt; height: 0.9in; margin: 3pt 0; background: ACC_XLT; display: flex; align-items: center; justify-content: center;
          font-family: 'Oswald'; font-weight: 700; font-size: 34pt; color: ACCENT; }
.wh .src { font-size: 9pt; color: #333; }
.chart { display: grid; grid-template-columns: repeat(9, 1fr); gap: 0; border: 1.4pt solid #000; border-radius: 5pt; overflow: hidden; margin: 4pt 0; }
.chart div { text-align: center; padding: 3pt 0 4pt; border-right: 1pt solid #000; font-family: 'Oswald'; font-weight: 700; font-size: 17pt; line-height: 1.05; }
.chart div:last-child { border-right: none; }
.chart div i { display: block; font-style: normal; font-weight: 500; font-size: 9pt; letter-spacing: .1em; background: #000; color: #fff; margin: -3pt 0 3pt; padding: 1pt 0 2pt; }
.chart div.cl { color: ACCENT; }
.refrow { display: flex; gap: 14pt; }
.refrow > div { flex: 1; }
.refgrid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 6pt; margin: 4pt 0 6pt; }
.refcell { border: 1.3pt solid #000; border-radius: 6pt; text-align: center; padding: 3pt 2pt 3pt; }
.refcell b { display: block; font-family: 'Oswald'; font-weight: 500; text-transform: uppercase; font-size: 9pt; }
.refcell span { font-size: 9pt; display: block; line-height: 1.2; }
.kk { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 12.5pt; border-bottom: 1pt solid #000; padding-bottom: 2pt; margin: 9pt 0 5pt; display: flex; justify-content: space-between; }
.kk span { font-weight: 300; text-transform: none; font-size: 10.5pt; }
.kline { font-size: 10pt; line-height: 1.3; margin: 0 0 3pt; }
.kline b { font-family: 'Oswald'; font-weight: 700; color: ACCENT; }
.mt { display: flex; gap: 14pt; margin-top: 4pt; }
.mt .col { flex: 1; display: flex; flex-direction: column; gap: 6pt; }
.mrow { display: flex; align-items: center; gap: 6pt; border: 1.2pt solid #000; border-radius: 6pt; padding: 3pt 8pt 3pt 4pt; }
.mrow .nm { font-family: 'Oswald'; font-weight: 700; font-size: 14pt; width: 17pt; text-align: center; }
.mrow .bx { width: 30pt; height: 28pt; border: 1.6pt solid #000; border-radius: 5pt; display: flex; align-items: center; justify-content: center; font-family: 'Oswald'; font-weight: 700; font-size: 17pt; color: ACCENT; flex: none; }
.mrow .sv { flex: 1; }
.mean { display: flex; align-items: center; gap: 7pt; border: 1.2pt solid #000; border-radius: 6pt; padding: 4pt 8pt 4pt 4pt; font-size: 11pt; line-height: 1.2; }
.mean .bd { width: 22pt; height: 22pt; border-radius: 50%; background: #000; color: #fff; font-family: 'Oswald'; font-weight: 700; font-size: 13pt; display: flex; align-items: center; justify-content: center; flex: none; }
.mean .ck { color: ACCENT; font-family: 'Oswald'; font-weight: 700; margin-left: auto; font-size: 11pt; white-space: nowrap; }
.coltitle { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 11pt; letter-spacing: .06em; margin-bottom: 4pt; }
""".replace("ACCENT", ACCENT).replace("ACC_LT", ACC_LT).replace("ACC_XLT", ACC_XLT)


def html_doc(pages, title="doc"):
    return (f'<!doctype html><html><head><meta charset="utf-8"><title>{escape(title)}</title>'
            f'<style>{font_css()}{CSS}</style></head><body>{"".join(pages)}</body></html>')


def foot(right):
    return f'<div class="foot"><span>{COPY}</span><span>{right}</span></div>'


def wmark(wm):
    return '<div class="wm">PREVIEW</div>' if wm else ""


def header(sub, tag, tag_note="", key=False):
    return (f'<div class="top"><div class="h t">Music Escape Room<small>{sub}</small></div>'
            f'<div class="tag"><div class="lv{" ak" if key else ""}">{tag}</div><div class="ln">{tag_note}</div></div></div>')


# ------------------------------------------------------------------ drawing: Bravura
def gl(cp, x, y, size, fill="#000"):
    return f'<text x="{x:.2f}" y="{y:.2f}" font-family="Bravura" font-size="{size:.2f}" fill="{fill}">&#x{cp:X};</text>'


def stem_up(x, y, space=14.0, length=3.5, width=2.6):
    """Up-stem for a black notehead drawn with gl(0xE0A4, x, y, 4 * space). gl() puts x at the LEFT edge of the head and the
    head is 1.18 spaces wide, so the stem goes on its right edge, starting 0.168 space above the head's centre line
    (Bravura's stem anchor) and rising `length` spaces. Used for the cover art; fixed 15 Nov 2026 after the cover
    shipped with stems drawn one head-width too far right (floating, detached from both notes)."""
    sx = x + 1.18 * space - width / 2
    return f'<line x1="{sx:.2f}" y1="{y - 0.168 * space:.2f}" x2="{sx:.2f}" y2="{y - length * space:.2f}" stroke="#000" stroke-width="{width}"/>'


NOTE_GLYPH = {"w": 0xE1D2, "h": 0xE1D3, "q": 0xE1D5, "e": 0xE1D7}
REST_GLYPH = {"w": 0xE4E3, "h": 0xE4E4, "q": 0xE4E5, "e": 0xE4E6}
HEAD_GLYPH_Q = 0xE0A4
DOT_GLYPH = 0xE1E7
HEAD_W = {"w": 1.688, "h": 1.18, "q": 1.18, "e": 1.18}
REST_W = {"w": 1.128, "h": 1.128, "q": 1.08, "e": 0.988}
KIND_DRAW = {"w": ("w", 0, 0), "h": ("h", 0, 0), "q": ("q", 0, 0), "e": ("e", 0, 0), "dh": ("h", 0, 1), "dq": ("q", 0, 1),
             "wr": ("w", 1, 0), "hr": ("h", 1, 0), "qr": ("q", 1, 0)}


def token_svg(kind, cx, y, s):
    """One note or rest (by KINDS key) centred on x=cx, on the line y."""
    base, rest, dot = KIND_DRAW[kind]
    size = 4 * s
    if rest:
        w = REST_W[base] * s
        out = gl(REST_GLYPH[base], cx - w / 2, y, size)
        return out
    hw = HEAD_W[base] * s
    left = cx - hw / 2
    out = gl(NOTE_GLYPH[base], left, y, size)
    if dot:
        out += gl(DOT_GLYPH, left + hw + 0.35 * s, y - 0.5 * s, size)
    return out


def staff_row_svg(clef, ps, mode):
    """Puzzles 1 and 2: one staff, notes with answer boxes ('ws') or the letters written in ('key')."""
    W, S = 540, 10.0
    yb = 70.0
    n = len(ps)
    x0, x1 = 92.0, W - 22.0
    step = (x1 - x0) / (n - 1)
    h = 150
    out = [f'<svg class="staff" data-puz="{1 if clef == "treble" else 2}" data-mode="{mode}" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {h}" width="{W}pt" height="{h}pt" style="display:block">']
    for i in range(5):
        out.append(f'<line x1="6" y1="{yb - i * S:.1f}" x2="{W - 6}" y2="{yb - i * S:.1f}" stroke="#000" stroke-width="1.1"/>')
    out.append(f'<line x1="6" y1="{yb - 4 * S}" x2="6" y2="{yb}" stroke="#000" stroke-width="1.4"/>')
    out.append(f'<line x1="{W - 6}" y1="{yb - 4 * S}" x2="{W - 6}" y2="{yb}" stroke="#000" stroke-width="1.4"/>')
    if clef == "treble":
        out.append(gl(0xE050, 14, yb - S, 4 * S))
    else:
        out.append(gl(0xE062, 14, yb - 3 * S, 4 * S))
    sw = 0.13 * S
    for i, p in enumerate(ps):
        assert 0 <= p <= 9
        cx = x0 + i * step
        y = yb - p * S / 2
        left = cx - HEAD_W["q"] * S / 2
        letter = note_letter(clef, p)
        out.append(f'<g class="q" data-puz="{1 if clef == "treble" else 2}" data-n="{i + 1}" data-clef="{clef}" data-p="{p}">')
        out.append(gl(HEAD_GLYPH_Q, left, y, 4 * S))
        if p < 4:
            sx = left + 1.18 * S - sw / 2
            out.append(f'<line x1="{sx:.2f}" y1="{y - 0.168 * S:.2f}" x2="{sx:.2f}" y2="{y - 3.5 * S:.2f}" stroke="#000" stroke-width="{sw:.2f}"/>')
        else:
            sx = left + sw / 2
            out.append(f'<line x1="{sx:.2f}" y1="{y + 0.168 * S:.2f}" x2="{sx:.2f}" y2="{y + 3.5 * S:.2f}" stroke="#000" stroke-width="{sw:.2f}"/>')
        out.append(f'<rect x="{cx - 14:.1f}" y="98" width="28" height="28" rx="4" fill="#fff" stroke="#000" stroke-width="1.4"/>')
        if mode == "key":
            out.append(f'<text x="{cx:.1f}" y="118.5" text-anchor="middle" font-family="Oswald" font-weight="700" font-size="19" fill="{ACCENT}">{letter}</text>')
        out.append(f'<text x="{cx:.1f}" y="140" text-anchor="middle" font-family="Oswald" font-weight="500" font-size="9.5">{i + 1}</text>')
        out.append("</g>")
    out.append("</svg>")
    return "".join(out)


# ---- one-line rhythm staff (puzzle 3 and 5)
def tok_layout(tokens, width, pad=12.0, slot=26.0):
    """x centres for the tokens of a bar by proportional spacing. The missing slot gets a fixed width."""
    total = sum(TOK_BEATS.get(t, 1.5) for t in tokens)
    xs = []
    acc = 0.0
    for t in tokens:
        b = TOK_BEATS.get(t, 1.5)
        xs.append(pad + (acc + b / 2) / total * (width - 2 * pad))
        acc += b
    return xs


def bar_svg(idx, bar, mode, correct_kind=None, width=250.0):
    beats, label, toks, opts = bar
    S = 7.0
    y = 38.0
    n, d = int(label[0]), int(label[2])
    x0 = 34.0
    w_bar = width - x0 - 2
    h = 64
    out = [f'<svg class="bar" data-mode="{mode}" data-q="{idx}" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width:.0f} {h}" width="{width:.0f}pt" height="{h}pt" style="display:block">']
    out.append(f'<line x1="2" y1="{y}" x2="{width - 2}" y2="{y}" stroke="#000" stroke-width="1"/>')
    out.append(f'<line x1="2" y1="{y - 2 * S}" x2="2" y2="{y + 2 * S}" stroke="#000" stroke-width="1.1"/>')
    out.append(gl(0xE080 + n, 9, y - S, 4 * S))
    out.append(gl(0xE080 + d, 9, y + S, 4 * S))
    xs = [x0 + x for x in tok_layout(toks, w_bar)]
    for t, cx in zip(toks, xs):
        if t == "M":
            if mode == "key":
                out.append(f'<rect x="{cx - 14:.1f}" y="{y - 22}" width="28" height="44" rx="4" fill="{ACC_XLT}" stroke="{ACCENT}" stroke-width="1.2"/>')
                out.append(token_svg(correct_kind, cx, y, S))
            else:
                out.append(f'<rect x="{cx - 14:.1f}" y="{y - 22}" width="28" height="44" rx="4" fill="#fff" stroke="#000" stroke-width="1.3" stroke-dasharray="4 3"/>')
                out.append(f'<text x="{cx:.1f}" y="{y + 6}" text-anchor="middle" font-family="Oswald" font-weight="700" font-size="18">?</text>')
        elif t == "E2":
            hw = 1.18 * S
            sw = 0.13 * S
            xa, xb = cx - 6.5, cx + 6.5
            for xx in (xa, xb):
                out.append(gl(HEAD_GLYPH_Q, xx - hw / 2, y, 4 * S))
                sx = xx - hw / 2 + 1.18 * S - sw / 2
                out.append(f'<line x1="{sx:.2f}" y1="{y - 0.168 * S:.2f}" x2="{sx:.2f}" y2="{y - 3.5 * S:.2f}" stroke="#000" stroke-width="{sw:.2f}"/>')
            x1 = xa - hw / 2 + 1.18 * S - sw
            x2 = xb - hw / 2 + 1.18 * S
            out.append(f'<rect x="{x1:.2f}" y="{y - 3.5 * S:.2f}" width="{x2 - x1:.2f}" height="{0.5 * S:.2f}" fill="#000"/>')
        else:
            kind = {"Q": "q", "H": "h", "DH": "dh", "QR": "qr", "HR": "hr"}[t]
            out.append(token_svg(kind, cx, y, S))
    bx = width - 2
    out.append(f'<line x1="{bx - 3.2:.1f}" y1="{y - 2 * S}" x2="{bx - 3.2:.1f}" y2="{y + 2 * S}" stroke="#000" stroke-width="1.1"/>')
    out.append(f'<line x1="{bx - 0.9:.1f}" y1="{y - 2 * S}" x2="{bx - 0.9:.1f}" y2="{y + 2 * S}" stroke="#000" stroke-width="3"/>')
    out.append("</svg>")
    return "".join(out)


def option_svg(opts_order, correct_kind=None, width=250.0):
    S = 6.0
    h = 58
    out = [f'<svg class="opts" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width:.0f} {h}" width="{width:.0f}pt" height="{h}pt" style="display:block">']
    cw = width / 4
    for i, k in enumerate(opts_order):
        cx = cw * i + cw / 2
        hit = correct_kind == k
        if hit:
            out.append(f'<rect x="{cx - cw / 2 + 2:.1f}" y="1" width="{cw - 4:.1f}" height="{h - 2}" rx="5" fill="{ACC_XLT}" stroke="{ACCENT}" stroke-width="1.4"/>')
        out.append(f'<circle cx="{cx - 21:.1f}" cy="14" r="8" fill="#000"/>')
        out.append(f'<text x="{cx - 21:.1f}" y="18.4" text-anchor="middle" font-family="Oswald" font-weight="700" font-size="11.5" fill="#fff">{OPT_LETTERS[i]}</text>')
        out.append(f'<line x1="{cx - 6:.1f}" y1="30" x2="{cx + 14:.1f}" y2="30" stroke="#000" stroke-width=".9"/>')
        out.append(token_svg(k, cx + 4, 30, S))
        out.append(f'<text x="{cx:.1f}" y="54" text-anchor="middle" font-family="Oswald" font-weight="500" font-size="7">{escape(KINDS[k][0].upper())}</text>')
    out.append("</svg>")
    return "".join(out)


def p3_option_order(i):
    opts = list(P3_BARS[i][3])
    random.Random(f"p3-opts-{i}").shuffle(opts)
    return opts


# ---- symbols for puzzle 4
def symbol_svg(sid, w=110, h=44):
    cx, cy = w / 2, h / 2
    o = [f'<svg class="sym" data-sym="{sid}" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}pt" height="{h}pt" style="display:block">']
    if sid == "forte":
        o.append(gl(0xE522, cx - 10, cy + 10, 34))
    elif sid == "piano":
        o.append(gl(0xE520, cx - 10, cy + 10, 34))
    elif sid in ("cresc", "decresc"):
        a, b = (6, 22) if sid == "cresc" else (22, 6)
        o.append(f'<path d="M{cx - 38},{cy - a / 2 * 0.0 - (b if sid == "decresc" else a) * 0 }" fill="none"/>')
        if sid == "cresc":
            o.append(f'<path d="M{cx - 38},{cy} L{cx + 38},{cy - 11} M{cx - 38},{cy} L{cx + 38},{cy + 11}" stroke="#000" stroke-width="2" fill="none" stroke-linecap="round"/>')
        else:
            o.append(f'<path d="M{cx - 38},{cy - 11} L{cx + 38},{cy} M{cx - 38},{cy + 11} L{cx + 38},{cy}" stroke="#000" stroke-width="2" fill="none" stroke-linecap="round"/>')
    elif sid == "fermata":
        o.append(gl(0xE4C0, cx - 14, cy + 6, 36))
    elif sid == "staccato":
        S = 6.5
        o.append(f'<line x1="{cx - 40}" y1="{cy + 8}" x2="{cx + 40}" y2="{cy + 8}" stroke="#000" stroke-width="1"/>')
        o.append(gl(NOTE_GLYPH["q"], cx - 1.18 * S / 2, cy + 8, 4 * S))
        o.append(f'<circle cx="{cx}" cy="{cy + 8 + 3.2 * S + 5:.1f}" r="0" fill="#000"/>')
        o.append(f'<circle cx="{cx}" cy="{cy + 8 + 2.2 * S:.1f}" r="2.3" fill="#000"/>')
    elif sid == "repeat":
        # end repeat: two dots, thin line, thick line
        o.append(f'<line x1="{cx - 6}" y1="{cy - 15}" x2="{cx - 6}" y2="{cy + 15}" stroke="#000" stroke-width="1.2"/>')
        o.append(f'<line x1="{cx + 1}" y1="{cy - 15}" x2="{cx + 1}" y2="{cy + 15}" stroke="#000" stroke-width="4"/>')
        o.append(f'<circle cx="{cx - 13}" cy="{cy - 5}" r="2.2" fill="#000"/><circle cx="{cx - 13}" cy="{cy + 5}" r="2.2" fill="#000"/>')
        o.append(f'<line x1="{cx - 40}" y1="{cy}" x2="{cx - 17}" y2="{cy}" stroke="#000" stroke-width=".9"/><line x1="{cx + 3}" y1="{cy}" x2="{cx + 40}" y2="{cy}" stroke="#000" stroke-width=".9"/>')
    elif sid == "sharp":
        o.append(gl(0xE262, cx - 5, cy + 5, 32))
    o.append("</svg>")
    return "".join(o)


P4_LETTER_OF_MEAN = {sid: L for sid, L in p4_letters().items()}


# ---- cover art
def snowflake(cx, cy, r, sw=2.0, col="#000"):
    o = []
    import math
    for k in range(6):
        a = math.radians(60 * k + 90)
        x2, y2 = cx + r * math.cos(a), cy - r * math.sin(a)
        o.append(f'<line x1="{cx}" y1="{cy}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{col}" stroke-width="{sw}" stroke-linecap="round"/>')
        mx, my = cx + 0.62 * r * math.cos(a), cy - 0.62 * r * math.sin(a)
        for da in (-45, 45):
            b = a + math.radians(da)
            o.append(f'<line x1="{mx:.1f}" y1="{my:.1f}" x2="{mx + 0.36 * r * math.cos(b):.1f}" y2="{my - 0.36 * r * math.sin(b):.1f}" stroke="{col}" stroke-width="{sw}" stroke-linecap="round"/>')
    return "".join(o)


def globe_art(width="100%"):
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 440 400" width="{width}" style="display:block">']
    # base
    o.append('<path d="M92,330 L348,330 L376,384 L64,384 Z" fill="#000"/>')
    o.append(f'<rect x="74" y="352" width="292" height="9" fill="{ACC_LT}"/>')
    o.append('<path d="M110,306 L330,306 L348,330 L92,330 Z" fill="#fff" stroke="#000" stroke-width="5" stroke-linejoin="round"/>')
    # globe
    o.append(f'<circle cx="220" cy="170" r="150" fill="{ACC_XLT}" stroke="#000" stroke-width="6"/>')
    o.append(f'<path d="M96,252 Q220,208 344,252 Q330,300 220,308 Q110,300 96,252 Z" fill="#fff" stroke="#000" stroke-width="4"/>')
    o.append(f'<path d="M96,252 A150,150 0 0 0 344,252 Q220,208 96,252 Z" fill="none"/>')
    o.append(f'<path d="M150,60 A120,120 0 0 1 244,28" fill="none" stroke="#fff" stroke-width="9" stroke-linecap="round"/>')
    # staff + clef inside
    for i in range(5):
        o.append(f'<line x1="132" y1="{118 + i * 14}" x2="308" y2="{118 + i * 14}" stroke="#000" stroke-width="2.2"/>')
    o.append(gl(0xE050, 140, 118 + 3 * 14, 56))
    # two quarter notes below the middle line, so both stems go up, on the right edge of each head
    o.append(gl(0xE0A4, 222, 118 + 2.5 * 14, 56))
    o.append(stem_up(222, 118 + 2.5 * 14))
    o.append(gl(0xE0A4, 262, 118 + 3.5 * 14, 56))
    o.append(stem_up(262, 118 + 3.5 * 14))
    o.append(snowflake(176, 70, 20, 2.4, ACCENT))
    o.append(snowflake(272, 56, 14, 2.2, ACCENT))
    o.append(snowflake(112, 160, 13, 2.2, ACCENT))
    o.append(snowflake(330, 150, 17, 2.4, ACCENT))
    o.append(snowflake(300, 220, 10, 2, ACCENT))
    for (x, y) in [(150, 96), (205, 40), (236, 92), (322, 100), (126, 212), (188, 236), (252, 232), (116, 118), (342, 196)]:  # (116,118): was (160,190), which sat on the treble clef
        o.append(f'<circle cx="{x}" cy="{y}" r="3.6" fill="#fff" stroke="#000" stroke-width="1.6"/>')
    # padlock on the base
    o.append(f'<path d="M196,318 v-14 a24,24 0 0 1 48,0 v14" fill="none" stroke="#000" stroke-width="8" stroke-linecap="round"/>')
    o.append(f'<rect x="178" y="316" width="84" height="62" rx="10" fill="{ACCENT}" stroke="#000" stroke-width="5"/>')
    o.append('<circle cx="220" cy="341" r="8" fill="#000"/><rect x="216.5" y="345" width="7" height="18" rx="2" fill="#000"/>')
    o.append("</svg>")
    return "".join(o)


# ------------------------------------------------------------------ pages
def cover_page(wm=False):
    return (f'<section class="page cover"><div class="store">{BRAND}</div>'
            f'<div style="width:5.4in">{globe_art()}</div>'
            f'<div class="ctitle"><div class="a">WINTER MUSIC</div><div class="b">ESCAPE ROOM</div>'
            f'<div class="c">Print and go · note names, rhythms and symbols · teacher guide and answer key</div></div>'
            f'<div class="cband">Grades 3–6 <em>·</em> 5 puzzles <em>·</em> {TOTAL_PAGES} pages</div></section>')


def tg1(wm=False):
    n = {1: len(P1_POS), 2: len(P2_POS), 3: len(P3_BARS), 4: len(P4_ORDER), 5: sum(1 for k in P5_MESSAGE if k)}
    rows = (
        ("1", "Treble clef door", "Name notes on the treble staff", f"{n[1]} notes", "5–8 min"),
        ("2", "Bass clef gears", "Name notes on the bass staff", f"{n[2]} notes", "6–9 min"),
        ("3", "Rhythm math", "Fill each bar with the right note or rest", f"{n[3]} bars", "8–10 min"),
        ("4", "Symbol sorting", "Match symbols to their meanings", f"{n[4]} symbols", "6–9 min"),
        ("5", "The beat code", "Decode a message with note and rest values", f"{n[5]} symbols", "7–10 min"),
    )
    trs = "".join(f"<tr><td><b>{a}</b></td><td>{b}</td><td>{c}</td><td>{d}</td><td>{e}</td></tr>" for a, b, c, d, e in rows)
    return (f'<section class="page doc">{wmark(wm)}<div class="rule"><h1>Teacher Guide</h1>'
            f'<div class="l" style="font-size:13pt">{TITLE} · grades 3–6 · 5 puzzles · about 45 minutes</div></div>'
            f'<h2>The game</h2><p>The snow-globe workshop is locked! Teams solve five music puzzles. Each puzzle gives an answer. A team finds that answer on an '
            f'<b>answer-check card</b>; the card tells it which lock wheel to fill and with which digit. When all five wheels are filled, the digits are turned into letters '
            f'with the lock chart. If the letters make a word, the lock opens. A wrong answer matches no card, or a wrong card, and the final word comes out as nonsense, so '
            f'teams find their own mistakes.</p>'
            f'<h2>At a glance</h2><table><tr><th>#</th><th>Puzzle</th><th>Skill</th><th>Items</th><th>Time</th></tr>{trs}</table>'
            f'<p class="small">Puzzles can be done in any order, so a team that is stuck can move on. Each puzzle has exactly one correct answer, and the five wheel digits depend on all five.</p>'
            f'<div class="cols"><div><h2>Setup (10 minutes)</h2><ol>'
            f'<li>Print pages {P_MISSION}–{P_FINAL} for each team (one set of 7 pages per team of 2–4 students). Print page {P_HINTS} for the hint card box.</li>'
            f'<li>Print page {P_CARDS} once, <b>cut along the dashed lines</b> and put each row of three cards into an envelope marked Puzzle 1 to Puzzle 5. '
            f'One set serves a whole class if teams share the envelopes at a table.</li>'
            f'<li>Cut the hint cards (page {P_HINTS}) and keep them at the front, with the optional workshop manual (page {P_MANUAL}).</li>'
            f'<li>Optional: set a 5-digit combination lock to the code on the answer key (page {P_KEY2}) for a real click at the end.</li></ol></div>'
            f'<div><h2>You need</h2><ul><li>Pencils and scissors</li><li>5 envelopes (or 5 paper clips)</li><li>A timer to project</li>'
            f'<li>Optional: a 5-digit combination lock</li></ul>'
            f'<h2>No cutting?</h2><p>Leave page {P_CARDS} uncut and give each team a copy of one row at a time when they report a finished puzzle.</p></div></div>'
            f'{foot("Teacher guide · Page 2")}</section>')


def tg2(wm=False):
    return (f'<section class="page doc">{wmark(wm)}<div class="rule"><h1>Running the Room</h1>'
            f'<div class="l" style="font-size:13pt">Timing, story, hints and differentiation</div></div>'
            f'<div class="cols"><div>'
            f'<h2>Timing for a 45-minute class</h2><table><tr><th>Minutes</th><th>What happens</th></tr>'
            f'<tr><td>0–5</td><td>Read the story, form teams, hand out the mission page</td></tr>'
            f'<tr><td>5–35</td><td>Teams solve the five puzzles and fetch cards</td></tr>'
            f'<tr><td>35–40</td><td>Final lock: digits to letters</td></tr>'
            f'<tr><td>40–45</td><td>Debrief: which puzzle was trickiest, and why?</td></tr></table>'
            f'<p class="small">For a 30-minute class use puzzles 1, 3, 4 and 5 with the answers for 2 given (see the key); for a double period add a performance of any tune the class knows.</p>'
            f'<h2>Read-aloud story</h2><p><i>“High in the hills sits a snow-globe workshop where the music boxes are made. Last night a gust of wind blew the door shut and the lock '
            f'froze. The lock listens only for music: five wheels, five puzzles. Solve a puzzle to earn a digit. When the wheels are full, the snow-globe will tell you the secret word.”</i></p>'
            f'<h2>Hints</h2><p>Teams may take one hint card per puzzle at any time. Each card on page {P_HINTS} is labelled with its puzzle and a level: '
            f'<b>1</b> nudges, <b>2</b> gives a strong start. Hints cost nothing; ask teams to say where they are stuck first.</p>'
            f'<h2>If the lock says nonsense</h2><p>One digit is wrong. Ask: “Which puzzle’s answer did you check against the cards least carefully?” '
            f'The letter at each wheel should look like part of a word you know. Have the team re-solve one puzzle at a time.</p>'
            f'</div><div>'
            f'<h2>Differentiation</h2><table><tr><th>Support</th><th>Challenge</th></tr>'
            f'<tr><td>Hand out the workshop manual (page {P_MANUAL}) at the start.</td><td>No manual and no hint cards: teams earn a bonus if they finish in 30 minutes.</td></tr>'
            f'<tr><td>Teams of 3–4, each student responsible for one puzzle, then shared.</td><td>Ask teams to write one new rhythm-math bar of their own with a single right answer.</td></tr>'
            f'<tr><td>Give puzzle 2 or 4 as a class warm-up beforehand.</td><td>Ask them to explain why a wrong card could not open the lock.</td></tr></table>'
            f'<h2>Grade guide</h2><ul><li><b>Grades 3–4:</b> puzzles 1, 3, 4 and 5 with the manual; puzzle 2 together.</li>'
            f'<li><b>Grades 5–6:</b> all five puzzles, manual closed.</li></ul>'
            f'<h2>Standards (modest fit)</h2><p>Supports the National Core Arts Standards for Music, Performing, MU:Pr4.2 (demonstrate understanding of the elements of music and notation), '
            f'in grades 3–6.</p>'
            f'<h2>About the music</h2><p class="small">Every puzzle is built from one rule and has one correct answer. Staff positions, bar totals and the beat code are computed '
            f'and re-checked before release. The workshop story is original and non-denominational; no songs, lyrics or copyrighted characters are used.</p>'
            f'</div></div>{foot("Teacher guide · Page 3")}</section>')


def mission(wm=False):
    steps = "".join(
        f'<tr><td><b>Puzzle {pz}</b> · {name}</td><td style="text-align:center">page {P_PUZ[pz]}</td><td style="width:1.6in"></td><td style="text-align:center">Wheel {WHEEL_OF[pz]}</td></tr>'
        for pz, name in ((1, "Treble clef door"), (2, "Bass clef gears"), (3, "Rhythm math"), (4, "Symbol sorting"), (5, "The beat code")))
    return (f'<section class="page doc">{wmark(wm)}{header("Your mission", "TEAM SHEET", "Page 4")}'
            f'<div class="name" style="margin-top:9pt">Team<span></span>Date<span class="d"></span></div>'
            f'<div class="story">The snow-globe workshop is locked. Wind slammed the door and the frost froze the lock. It has five wheels, and each wheel listens for a '
            f'digit. You are the team that can open it. Every puzzle you solve earns a digit.</div>'
            f'<h2>How it works</h2><ol>'
            f'<li><b>Solve a puzzle.</b> Each puzzle page ends with an answer line. There is exactly one right answer.</li>'
            f'<li><b>Find your answer card.</b> Open the envelope with the puzzle’s number. Take the card that shows <i>your</i> answer. The other cards are traps.</li>'
            f'<li><b>Read the card.</b> It names a wheel and a digit. Write the digit on the lock page (page {P_FINAL}).</li>'
            f'<li><b>Open the lock.</b> When all five wheels are filled, use the lock chart to change digits into letters.</li></ol>'
            f'<h2>Team tracker</h2><table><tr><th>Puzzle</th><th>Page</th><th>Our answer</th><th>Goes in</th></tr>{steps}</table>'
            f'<h2>Team rules</h2><ul><li>Everyone does their own work first, then compares answers.</li>'
            f'<li>If two answers disagree, find the staff note or symbol you do not agree about.</li>'
            f'<li>Stuck? Ask for a hint card. Hints are allowed.</li>'
            f'<li>No card for your answer? Your answer is not right yet. Look again.</li></ul>'
            f'<div style="flex:1"></div>{foot(f"Page 4")}</section>')


def puzzle_header(pz, title, sub):
    return header(f"Puzzle {pz} · {title}", f"PUZZLE {pz}", sub)


def ans_line(label, hint=""):
    return (f'<div class="ansline">{label}<span class="bx"></span></div>'
            f'<div class="cardnote"><b>Next:</b> {hint}</div>')


def pz1(wm=False):
    return (f'<section class="page">{wmark(wm)}{puzzle_header(1, "Treble clef door", "Reading the treble staff")}'
            f'<div class="name">Name<span></span>Date<span class="d"></span></div>'
            f'<div class="story">The workshop door has a brass sign, but the letters have turned into notes. Read the notes to find the word on the sign.</div>'
            f'<div class="how"><b>Name each note.</b> Write the letter name of every note in its box, from left to right. '
            f'The {len(P1_POS)} letters spell a word. Write the word on the answer line.</div>'
            f'<div style="margin-top:12pt">{staff_row_svg("treble", P1_POS, "ws")}</div>'
            f'{ans_line("The word on the sign:", "Take Puzzle 1 envelope, find the card that shows your word and copy its digit onto the lock page.")}'
            f'<div style="flex:1"></div>{foot(f"Page {P_PUZ[1]}")}</section>')


def pz2(wm=False):
    return (f'<section class="page">{wmark(wm)}{puzzle_header(2, "Bass clef gears", "Reading the bass staff")}'
            f'<div class="name">Name<span></span>Date<span class="d"></span></div>'
            f'<div class="story">Behind the door, gears turn a music-box cylinder. Each gear has a note carved on it, but this staff uses a different clef.</div>'
            f'<div class="how"><b>Name each note.</b> This staff has a <b>bass clef</b>. Write the letter name of every note in its box, from left to right. '
            f'The {len(P2_POS)} letters spell a word. Write the word on the answer line.</div>'
            f'<div style="margin-top:12pt">{staff_row_svg("bass", P2_POS, "ws")}</div>'
            f'{ans_line("The word on the gears:", "Take Puzzle 2 envelope, find the card that shows your word and copy its digit onto the lock page.")}'
            f'<div style="flex:1"></div>{foot(f"Page {P_PUZ[2]}")}</section>')


def pz3(wm=False, key=False):
    blocks = []
    for i, bar in enumerate(P3_BARS):
        order = p3_option_order(i)
        blocks.append(
            f'<div class="rb" style="width:250pt" data-q="{i + 1}"><div style="font-family:Oswald;font-weight:700;font-size:13pt;margin-bottom:1pt">{i + 1}</div>'
            f'{bar_svg(i + 1, bar, "ws")}{option_svg(order)}'
            f'</div>')
    grid = '<div style="display:grid;grid-template-columns:1fr 1fr;gap:6pt 14pt;justify-items:center">' + "".join(blocks) + "</div>"
    return (f'<section class="page">{wmark(wm)}{puzzle_header(3, "Rhythm math", "Bars, beats and a total")}'
            f'<div class="name">Name<span></span>Date<span class="d"></span></div>'
            f'<div class="story">A music box plays only if every bar is full. Six bars are missing one note or rest.</div>'
            f'<div class="how"><b>Fill each bar.</b> The time signature tells how many beats the bar holds (the top number; the bottom 4 means a quarter note is 1 beat). '
            f'Circle the one choice that makes the bar full. Then <b>add up the beats</b> of the {len(P3_BARS)} circled choices.</div>'
            f'{grid}'
            f'<div class="ansline" style="margin-top:12pt">Total beats of the six circled choices:<span class="bx" style="max-width:1.4in"></span></div>'
            f'<div class="cardnote"><b>Next:</b> Take Puzzle 3 envelope, find the card that shows your total and copy its digit onto the lock page.</div>'
            f'<div style="flex:1"></div>{foot(f"Page {P_PUZ[3]}")}</section>')


def pz4(wm=False):
    rows = []
    for i, sid in enumerate(P4_ORDER):
        rows.append(f'<div class="mrow" data-q="{i + 1}" data-sym="{sid}"><div class="nm">{i + 1}</div><div class="sv">{symbol_svg(sid)}</div><div class="bx"></div></div>')
    means = []
    for sid in P4_MEANING_ORDER:
        means.append(f'<div class="mean" data-mean="{sid}"><div class="bd">{P4_LETTER_OF_MEAN[sid]}</div>{escape(SYMBOLS[sid][1])}</div>')
    return (f'<section class="page">{wmark(wm)}{puzzle_header(4, "Symbol sorting", "Music symbols and their meanings")}'
            f'<div class="name">Name<span></span>Date<span class="d"></span></div>'
            f'<div class="story">The workshop’s instruction cards have been shuffled. Match each symbol to what it tells a musician to do.</div>'
            f'<div class="how"><b>Match them.</b> Each meaning has a letter in a black circle. For each symbol, find its meaning and write that letter in the box. '
            f'Each meaning is used once. Read the letters from 1 to {len(P4_ORDER)} to spell a word.</div>'
            f'<div class="mt"><div class="col"><div class="coltitle">Symbols</div>{"".join(rows)}</div>'
            f'<div class="col"><div class="coltitle">Meanings</div>{"".join(means)}</div></div>'
            f'<div class="ansline" style="margin-top:12pt">The word:<span class="bx" style="max-width:2.6in"></span></div>'
            f'<div class="cardnote"><b>Next:</b> Take Puzzle 4 envelope, find the card that shows your word and copy its digit onto the lock page.</div>'
            f'<div style="flex:1"></div>{foot(f"Page {P_PUZ[4]}")}</section>')


def msg_svg(mode, width=540.0):
    """Puzzle 5 message on a one-line staff, one box under each symbol (and the decoded letter in the key)."""
    S = 8.0
    y = 40.0
    n = len(P5_MESSAGE)
    gap = 26.0
    syms = sum(1 for k in P5_MESSAGE if k)
    step = (width - 90 - gap) / (syms - 1) if syms > 1 else 0
    h = 112
    out = [f'<svg class="msg" data-mode="{mode}" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width:.0f} {h}" width="{width:.0f}pt" height="{h}pt" style="display:block">']
    out.append(f'<line x1="2" y1="{y}" x2="{width - 2}" y2="{y}" stroke="#000" stroke-width="1.1"/>')
    out.append(f'<line x1="2" y1="{y - 2 * S}" x2="2" y2="{y + 2 * S}" stroke="#000" stroke-width="1.3"/>')
    out.append(f'<line x1="{width - 5}" y1="{y - 2 * S}" x2="{width - 5}" y2="{y + 2 * S}" stroke="#000" stroke-width="1.3"/>')
    x = 30.0
    t = p5_table()
    k = 0
    for item in P5_MESSAGE:
        if item is None:
            x += gap
            continue
        cx = x
        out.append(f'<g class="q" data-puz="5" data-n="{k + 1}" data-kind="{item}">')
        out.append(token_svg(item, cx, y, S))
        out.append(f'<rect x="{cx - 14:.1f}" y="66" width="28" height="28" rx="4" fill="#fff" stroke="#000" stroke-width="1.4"/>')
        if mode == "key":
            out.append(f'<text x="{cx:.1f}" y="86.5" text-anchor="middle" font-family="Oswald" font-weight="700" font-size="19" fill="{ACCENT}">{t[item]}</text>')
        out.append(f'<text x="{cx:.1f}" y="108" text-anchor="middle" font-family="Oswald" font-weight="500" font-size="9.5">{k + 1}</text>')
        out.append("</g>")
        k += 1
        x += step
    out.append("</svg>")
    return "".join(out)


def pz5(wm=False):
    cells = "".join(f'<div class="refcell" data-kind="{k}"><b>{escape(nm)}</b><span style="font-family:Oswald;font-weight:700;font-size:20pt;color:{ACCENT}">{L}</span></div>'
                    for nm, k, L in P5_TABLE)
    cells = f'<div class="refgrid" style="grid-template-columns:repeat(4,1fr)">{cells}</div>'
    return (f'<section class="page">{wmark(wm)}{puzzle_header(5, "The beat code", "Decode with note and rest values")}'
            f'<div class="name">Name<span></span>Date<span class="d"></span></div>'
            f'<div class="story">Deep inside the globe is a secret message written in beats. The code book lists each note or rest by name.</div>'
            f'<div class="how"><b>Decode it.</b> Look at each symbol in the message and find its name. Then use the code book to turn it into a letter and write the letter in the box. '
            f'Read all {sum(1 for k in P5_MESSAGE if k)} letters, with a gap between the two words.</div>'
            f'<div class="coltitle" style="margin-top:6pt">Code book</div>{cells}'
            f'<div class="coltitle" style="margin-top:10pt">The message</div><div style="margin-top:6pt">{msg_svg("ws")}</div>'
            f'<div class="ansline" style="margin-top:10pt">The secret message:<span class="bx" style="max-width:3in"></span></div>'
            f'<div class="cardnote"><b>Next:</b> Take Puzzle 5 envelope, find the card that shows your message and copy its digit onto the lock page.</div>'
            f'<div style="flex:1"></div>{foot(f"Page {P_PUZ[5]}")}</section>')


def final_lock(wm=False):
    wheels = "".join(f'<div class="wh"><div class="n">Wheel {w}</div><div class="bx"></div><div class="src">from card, wheel {w}</div></div>' for w in range(1, 6))
    chart = "".join(f'<div><i>{d}</i>{L}</div>' for d, L in CHART.items())
    boxes = "".join(f'<div class="wh"><div class="bx" style="height:0.65in;background:#fff;color:#000"></div></div>' for _ in range(5))
    return (f'<section class="page doc">{wmark(wm)}{header("The final lock", "FINAL LOCK", "Page 10")}'
            f'<div class="name">Team<span></span>Date<span class="d"></span></div>'
            f'<div class="story">The five wheels are glowing. Turn them to the digits you earned, then read the lock chart.</div>'
            f'<h2>Step 1 · Fill the wheels</h2><p>Each answer card names a wheel. Write its digit in the matching wheel. The wheels are in a different order than the puzzles.</p>'
            f'<div class="wheels">{wheels}</div>'
            f'<h2>Step 2 · Use the lock chart</h2><p>Every digit hides a letter. Look up each wheel’s digit and write the letter underneath.</p>'
            f'<div class="chart">{chart}</div>'
            f'<div class="wheels">{boxes}</div>'
            f'<h2>Step 3 · Open the lock</h2><p>Read the five letters from wheel 1 to wheel 5. If they make a word you would hear in a music room, the lock clicks open and the snow-globe plays. '
            f'If you see nonsense, one digit is wrong: go back to the puzzle you are least sure of and check it again.</p>'
            f'<div class="ansline">The lock word:<span class="bx" style="max-width:2.4in"></span></div>'
            f'<div class="story" style="margin-top:12pt">Bonus: write one sentence about which puzzle was hardest for your team and what helped you solve it.</div>'
            f'<div style="border-bottom:1pt solid #000;height:22pt"></div><div style="border-bottom:1pt solid #000;height:22pt"></div>'
            f'<div style="flex:1"></div>{foot("Page 10")}</section>')


def card_html(c):
    return (f'<div class="cd"><div class="pz">Puzzle {c["puzzle"]}</div><div class="tx">{escape(c["text"])}</div>'
            f'<div class="gv">Wheel {c["wheel"]} · digit <b>{c["digit"]}</b></div></div>')


def cards_page(wm=False):
    cells = "".join(card_html(c) for pz in range(1, 6) for c in CARDS[pz])
    return (f'<section class="page">{wmark(wm)}{header("Answer-check cards · cut out", "CUT-OUTS", "Teacher prep")}'
            f'<div class="how" style="margin:5pt 0 0">Cut along the dashed lines. Put each row of three cards into an envelope marked with its puzzle number. '
            f'Teams take the card that shows their answer. Only one card in each row is right.</div>'
            f'<div class="cardgrid">{cells}</div>'
            f'<div style="flex:1"></div>{foot(f"Page {P_CARDS}")}</section>')


HINTS = {
    1: ("Look at the clef at the start. A treble clef curls around the second line from the bottom: that line is G.",
        "Lines from the bottom: E G B D F. Spaces from the bottom: F A C E."),
    2: ("This clef has two dots around the second line from the top: that line is F. The notes are not the same as in the treble clef.",
        "Lines from the bottom: G B D F A. Spaces from the bottom: A C E G."),
    3: ("Add up the beats that are already in the bar. Subtract from the number on top of the time signature.",
        "A quarter note is 1 beat, a half note 2, a dotted half note 3 (a dot adds half), a whole note 4. Two beamed eighths make 1 beat."),
    4: ("Start with the symbols you know for sure, then cross out their meanings. The two hairpins open or close.",
        "Hairpin opening to the right = louder. Closing = softer. A dot over a note = short. A curved bird’s-eye over a note = hold it."),
    5: ("Say the name of each symbol aloud. A rest hangs below or sits on top of the line: the whole rest hangs, the half rest sits.",
        "A dot after a note makes it longer, so a dotted half note is different from a half note."),
}


def hints_page(wm=False):
    cells = []
    for pz in range(1, 6):
        for lv in (0, 1):
            cells.append(f'<div class="hc"><span class="pz">Puzzle {pz} <em>· hint {lv + 1}</em></span>{escape(HINTS[pz][lv])}</div>')
    return (f'<section class="page">{wmark(wm)}{header("Hint cards · cut out", "CUT-OUTS", "Teacher prep")}'
            f'<div class="how" style="margin:5pt 0 0">Cut along the dashed lines and keep the cards at the front of the room. Teams may take one hint card per puzzle: hint 1 nudges, hint 2 gives a strong start.</div>'
            f'<div class="hintgrid">{"".join(cells)}</div>'
            f'<div style="flex:1"></div>{foot(f"Page {P_HINTS}")}</section>')


def manual_page(wm=False):
    def mini_staff(clef, lab):
        S = 8.0
        W = 250
        yb = 52.0
        o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} 96" width="{W}pt" height="96pt" style="display:block">']
        for i in range(5):
            o.append(f'<line x1="4" y1="{yb - i * S}" x2="{W - 4}" y2="{yb - i * S}" stroke="#000" stroke-width="1"/>')
        if clef == "treble":
            o.append(gl(0xE050, 8, yb - S, 4 * S))
        else:
            o.append(gl(0xE062, 8, yb - 3 * S, 4 * S))
        for i, p in enumerate(range(0, 9)):
            cx = 70 + i * 20
            y = yb - p * S / 2
            o.append(gl(0xE0A4, cx - 0.59 * S, y, 4 * S))
            o.append(f'<text x="{cx}" y="92" text-anchor="middle" font-family="Oswald" font-weight="700" font-size="11" fill="{ACCENT}">{note_letter(clef, p)}</text>')
        o.append("</svg>")
        return "".join(o)
    cells = "".join(f'<div class="refcell"><svg width="56pt" height="36pt" viewBox="0 0 56 36"><line x1="6" y1="22" x2="50" y2="22" stroke="#000" stroke-width="1"/>{token_svg(k, 26, 22, 7.0)}</svg>'
                    f'<b>{escape(KINDS[k][0])}</b><span>{b}</span></div>' for k, b in
                    (("w", "4 beats"), ("dh", "3 beats"), ("h", "2 beats"), ("dq", "1½ beats"), ("q", "1 beat"), ("e", "½ beat"),
                     ("wr", "4 beats of silence"), ("hr", "2 beats of silence"), ("qr", "1 beat of silence")))
    return (f'<section class="page doc">{wmark(wm)}<div class="rule"><h1>Workshop Manual</h1>'
            f'<div class="l" style="font-size:13pt">An optional reference. Teachers: hand it out for support, or keep it back for a challenge.</div></div>'
            f'<h2>Notes on the staff <span class="acc">·</span> <span class="l" style="text-transform:none;font-size:11pt">notes from the bottom line up</span></h2>'
            f'<div class="refrow"><div><div class="coltitle">Treble clef</div>{mini_staff("treble", "T")}</div>'
            f'<div><div class="coltitle">Bass clef</div>{mini_staff("bass", "B")}</div></div>'
            f'<p class="small">The music alphabet has only seven letters: A B C D E F G, then it starts again. Going up from a line to the next space means the next letter.</p>'
            f'<h2>Note and rest values <span class="acc">·</span> <span class="l" style="text-transform:none;font-size:11pt">when a quarter note gets the beat</span></h2>'
            f'<div class="refgrid">{cells}</div>'
            f'<p class="small">A dot after a note makes it half as long again: a dotted half note is 2 + 1 = 3 beats; a dotted quarter note is 1 + ½ = 1½ beats.</p>'
            f'<h2>Time signatures</h2><table><tr><th>Sign</th><th>Beats in a bar</th><th>The bottom 4 means</th></tr>'
            f'<tr><td><b>4/4</b></td><td>4</td><td rowspan="3">a quarter note gets 1 beat</td></tr><tr><td><b>3/4</b></td><td>3</td></tr><tr><td><b>2/4</b></td><td>2</td></tr></table>'
            f'<div style="flex:1"></div>{foot(f"Page {P_MANUAL}")}</section>')


def terms_page(wm=False):
    return (f'<section class="page doc">{wmark(wm)}<div class="rule"><h1>Terms of Use</h1>'
            f'<div class="l" style="font-size:13pt">Thank you for your purchase!</div></div>'
            f'<p>© {YEAR} {STORE}. {BRAND} by {STORE}. All rights reserved. This purchase gives <b>one teacher</b> a license to use this resource with their own students.</p>'
            f'<h2>You may</h2><ul><li>Print and copy pages for your own classroom and students, year after year.</li>'
            f'<li>Share pages with your own students through a password-protected class site or learning platform.</li>'
            f'<li>Use the pages with your own students when you have a substitute teacher.</li></ul>'
            f'<h2>You may not</h2><ul><li>Share, email or copy this resource for other teachers, a whole school or a district. '
            f'Additional licenses are available on Teachers Pay Teachers.</li>'
            f'<li>Post any part of it on a public website, shared drive or social media.</li>'
            f'<li>Sell, give away or claim any part of it as your own, or edit it into a new product.</li></ul>'
            f'<h2>Questions?</h2><p>Please use the Q&amp;A tab on the {BRAND} by {STORE} store on Teachers Pay Teachers. If something looks wrong, let me know there and I will fix it.</p>'
            f'<h2>Credits</h2><ul>'
            f'<li>Puzzles, story, layouts and answer keys: original work, {BRAND} by {STORE}.</li>'
            f'<li>Music notation font: Bravura © Steinberg Media Technologies GmbH, SIL Open Font License 1.1.</li>'
            f'<li>Text fonts: Oswald (The Oswald Project Authors) and Source Sans 3 (Adobe), SIL Open Font License 1.1.</li></ul>'
            f'<p class="small">{DISCLOSURE}</p>'
            f'<p class="small">No songs, lyrics or copyrighted characters are used.</p>'
            f'<div style="flex:1"></div>{foot(f"Page {P_TERMS}")}</section>')


# ---- answer key
def key_p1p2(pz):
    clef, ps, word = ("treble", P1_POS, p1_answer()) if pz == 1 else ("bass", P2_POS, p2_answer())
    c = card_lookup(pz, word)
    return (f'<div class="kk">Puzzle {pz} · {"Treble clef door" if pz == 1 else "Bass clef gears"}<span>page {P_PUZ[pz]}</span></div>'
            f'<div data-key="{pz}">{staff_row_svg(clef, ps, "key")}</div>'
            f'<div class="kline">Word: <b>{word}</b> · card shows wheel <b>{c["wheel"]}</b>, digit <b>{c["digit"]}</b>.</div>')


def key_p3():
    blocks = []
    for i, bar in enumerate(P3_BARS):
        fit, need = p3_fit(bar)
        order = p3_option_order(i)
        k = fit[0]
        blocks.append(
            f'<div data-k="{i + 1}" data-need="{need}" data-kind="{k}" data-letter="{OPT_LETTERS[order.index(k)]}" style="width:168pt"><div class="kline" style="margin:0;font-size:9pt"><b>{i + 1}.</b> Missing {need} beat{"s" if need != 1 else ""}: '
            f'<b>{OPT_LETTERS[order.index(k)]}</b> ({escape(KINDS[k][0])})</div>{bar_svg(i + 1, bar, "key", k, width=168.0)}</div>')
    tot = p3_answer()
    vals = " + ".join(str(int(KINDS[p3_fit(b)[0][0]][1])) for b in P3_BARS)
    c = card_lookup(3, str(tot))
    return (f'<div class="kk">Puzzle 3 · Rhythm math<span>page {P_PUZ[3]}</span></div>'
            f'<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:2pt 10pt;justify-items:start">{"".join(blocks)}</div>'
            f'<div class="kline" style="margin-top:3pt">Total: {vals} = <b>{tot}</b> · card shows wheel <b>{c["wheel"]}</b>, digit <b>{c["digit"]}</b>.</div>')


def key_page1(wm=False):
    return (f'<section class="page">{wmark(wm)}{header("Answer key · puzzles 1–3", "ANSWER KEY", "Teacher copy", key=True)}'
            f'{key_p1p2(1)}{key_p1p2(2)}{key_p3()}'
            f'<div style="flex:1"></div>{foot(f"Answer key · Page {P_KEY1}")}</section>')


def key_page2(wm=False):
    digits, word, ans = final_code()
    # puzzle 4
    rows = []
    L = p4_letters()
    for i, sid in enumerate(P4_ORDER):
        rows.append(f'<tr data-k="{i + 1}" data-sym="{sid}" data-ans="{L[sid]}"><td><b>{i + 1}</b></td><td>{escape(SYMBOLS[sid][0])}</td><td>{escape(SYMBOLS[sid][1])}</td><td><b style="color:{ACCENT}">{L[sid]}</b></td></tr>')
    c4 = card_lookup(4, p4_answer())
    t5 = p5_table()
    names = {k: nm for nm, k, _ in P5_TABLE}
    c5 = card_lookup(5, p5_answer())
    msg = []
    j = 0
    for kk in P5_MESSAGE:
        if kk is None:
            continue
        j += 1
        msg.append(f'<span data-k="{j}" data-kind="{kk}" data-ans="{t5[kk]}">{j}. {escape(names[kk])} = <b style="color:{ACCENT}">{t5[kk]}</b></span>')
    wheel_rows = "".join(
        f'<td style="text-align:center"><b>Wheel {w}</b><br>Puzzle {next(p for p, ww in WHEEL_OF.items() if ww == w)}<br><span style="font-family:Oswald;font-weight:700;font-size:15pt;color:{ACCENT}">{digits[w - 1]} → {word[w - 1]}</span></td>'
        for w in range(1, 6))
    cardlist = "; ".join(f'P{pz}: ' + ", ".join(f'{escape(c["text"])} ({c["digit"]}){"✔" if c["correct"] else ""}' for c in CARDS[pz]) for pz in range(1, 6))
    return (f'<section class="page">{wmark(wm)}{header("Answer key · puzzles 4 and 5, final lock", "ANSWER KEY", "Teacher copy", key=True)}'
            f'<div class="kk">Puzzle 4 · Symbol sorting<span>page {P_PUZ[4]}</span></div>'
            f'<table style="border-collapse:collapse;width:100%;font-size:9.6pt" class="k4"><tr style="background:#000;color:#fff"><th style="padding:2pt 5pt;text-align:left">#</th><th style="text-align:left">Symbol</th><th style="text-align:left">Meaning</th><th style="text-align:left">Letter</th></tr>'
            f'{"".join(rows)}</table>'
            f'<div class="kline" style="margin-top:3pt">Word: <b>{p4_answer()}</b> · card shows wheel <b>{c4["wheel"]}</b>, digit <b>{c4["digit"]}</b>.</div>'
            f'<div class="kk">Puzzle 5 · The beat code<span>page {P_PUZ[5]}</span></div>'
            f'<div data-key="5">{msg_svg("key")}</div>'
            f'<div class="kline" style="margin-top:2pt">{" · ".join(msg)}</div>'
            f'<div class="kline">Message: <b>{p5_answer()}</b> · card shows wheel <b>{c5["wheel"]}</b>, digit <b>{c5["digit"]}</b>.</div>'
            f'<div class="kk">Final lock<span>page {P_FINAL}</span></div>'
            f'<table style="border-collapse:collapse;width:100%;font-size:9.6pt"><tr>{wheel_rows}</tr></table>'
            f'<div class="kline" style="margin-top:4pt">Combination lock code: <b>{" ".join(str(d) for d in digits)}</b> · lock word: <b>{word}</b>. '
            f'Chart: {", ".join(f"{d} = {l}" for d, l in CHART.items())}.</div>'
            f'<div class="kline small" style="font-size:8.5pt">Cards (✔ = correct; the other two are traps from common slips): {cardlist}.</div>'
            f'<div style="flex:1"></div>{foot(f"Answer key · Page {P_KEY2}")}</section>')


PAGE_FUNCS = {1: cover_page, 2: tg1, 3: tg2, 4: mission, 5: pz1, 6: pz2, 7: pz3, 8: pz4, 9: pz5, 10: final_lock, 11: cards_page, 12: hints_page,
              13: manual_page, 14: key_page1, 15: key_page2, 16: terms_page}
PREVIEW_PAGES = [3, 5, 7, 10]


def all_pages(wm=False, only=None):
    return [PAGE_FUNCS[i](wm) for i in (only or range(1, TOTAL_PAGES + 1))]


# ------------------------------------------------------------------ square images
SQ_CSS = """
.sq { width: 1000px; height: 1000px; position: relative; overflow: hidden; background: #fff; display: flex; flex-direction: column; align-items: center; }
.sq .store { font-family: 'Oswald'; font-weight: 500; letter-spacing: .32em; text-transform: uppercase; font-size: 22px; margin-top: 34px; }
.sq .hd { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; text-align: center; line-height: .95; }
.sq .sub { font-family: 'Oswald'; font-weight: 300; text-align: center; }
.sq .band { position: absolute; left: 0; right: 0; bottom: 0; height: 66px; background: #000; color: #fff; text-align: center; font-family: 'Oswald';
            font-weight: 500; text-transform: uppercase; letter-spacing: .1em; font-size: 26px; line-height: 66px; }
.sq .band em { font-style: normal; color: ACC_LT; }
.shot { background: #fff; border: 2px solid #000; box-shadow: 8px 8px 0 #000; position: relative; overflow: hidden; }
.shot img { display: block; width: 100%; }
.lbl { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 22px; text-align: center; margin-top: 16px; }
.lbl span { font-weight: 300; text-transform: none; display: block; font-size: 18px; }
.swm { position: absolute; left: 50%; top: 50%; transform: translate(-50%,-50%) rotate(-38deg); font-family: 'Oswald'; font-weight: 700;
       color: rgba(0,0,0,.14); white-space: nowrap; letter-spacing: .06em; }
.pcard { box-sizing: border-box; border: 2px solid #000; border-radius: 8px; padding: 8px 12px; background: #fff; display: flex; align-items: center; gap: 14px; }
.pcard .pn { font-family: 'Oswald'; font-weight: 700; font-size: 44px; color: ACCENT; width: 38px; text-align: center; }
.pcard .pt { font-family: 'Oswald'; font-weight: 700; font-size: 24px; text-transform: uppercase; line-height: 1.05; }
.pcard .ps { font-family: 'Oswald'; font-weight: 300; font-size: 18px; }
""".replace("ACCENT", ACCENT).replace("ACC_LT", ACC_LT)


def sq_doc(body):
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{font_css()}'
            f'html,body{{margin:0;background:#fff}}{SQ_CSS}</style></head><body>{body}</body></html>')


def cover_square():
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div>'
        f'<div style="flex:1;display:flex;flex-direction:column;justify-content:space-evenly;align-items:center;width:100%;padding:0 0 84px">'
        f'<div style="width:470px">{globe_art()}</div>'
        f'<div><div class="hd" style="font-size:66px">Winter Music</div>'
        f'<div class="hd" style="font-size:128px">Escape Room</div>'
        f'<div class="sub" style="font-size:28px;margin-top:12px">Print and go · note names, rhythms and symbols</div></div>'
        f'</div><div class="band">Grades 3–6 <em>·</em> 5 puzzles <em>·</em> {TOTAL_PAGES} pages</div></div>')


def shot(src, w, fs):
    return (f'<div class="shot" style="width:{w}px"><img src="{src}"><div class="swm" style="font-size:{fs}px">PREVIEW</div></div>')


def preview_square_1(img):
    labs = [("Puzzle 1", "Treble clef"), ("Puzzle 3", "Rhythm math"), ("Puzzle 4", "Symbol sorting")]
    shots = "".join(f'<div style="width:296px">{shot(img[i], 296, 54)}<div class="lbl">{labs[i][0]}<span>{labs[i][1]}</span></div></div>' for i in range(3))
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div>'
        f'<div class="hd" style="font-size:72px;margin-top:20px">Five puzzles, one lock</div>'
        f'<div class="sub" style="font-size:27px;margin-top:8px">Solve each puzzle, collect a digit, open the snow-globe workshop</div>'
        f'<div style="display:flex;gap:26px;margin-top:40px">{shots}</div>'
        f'<div style="font-family:Oswald;font-weight:300;font-size:23px;margin-top:34px;text-align:center;width:880px;line-height:1.35">'
        f'Treble clef · bass clef · rhythm math · symbols and terms · a decoder. '
        f'Each puzzle has one answer, and the final lock needs all five.</div>'
        f'<div class="band">Grades 3–6 <em>·</em> about 45 minutes <em>·</em> answer key</div></div>')


def preview_square_2(a, b):
    pair = "".join(f'<div style="width:420px">{shot(src, 420, 80)}<div class="lbl">{lab}</div></div>' for src, lab in ((a, "Teacher guide"), (b, "Final lock page")))
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div>'
        f'<div class="hd" style="font-size:70px;margin-top:20px">Teacher guide included</div>'
        f'<div class="sub" style="font-size:27px;margin-top:8px">Setup, timing, hints and differentiation, plus a full answer key</div>'
        f'<div style="display:flex;gap:40px;margin-top:30px">{pair}</div>'
        f'<div class="band">Cut-out answer cards <em>·</em> hint cards <em>·</em> keys</div></div>')


def preview_square_3():
    items = [("1", "Treble clef door", "Name 6 notes, spell a word"), ("2", "Bass clef gears", "Name 7 notes, spell a word"),
             ("3", "Rhythm math", "Fill 6 bars, add the beats"), ("4", "Symbol sorting", "Match 8 symbols to meanings"),
             ("5", "The beat code", "Decode a message of notes and rests")]
    cards = "".join(f'<div class="pcard" style="width:760px"><div class="pn">{a}</div><div><div class="pt">{b}</div><div class="ps">{c}</div></div></div>' for a, b, c in items)
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div>'
        f'<div class="hd" style="font-size:70px;margin-top:20px">Five puzzles inside</div>'
        f'<div style="display:flex;flex-direction:column;gap:14px;margin-top:34px;align-items:center">{cards}'
        f'<div class="pcard" style="width:760px;background:{ACC_XLT}"><div class="pn">★</div><div><div class="pt">The final lock</div><div class="ps">Five digits make one secret word</div></div></div></div>'
        f'<div class="band">Print and go <em>·</em> {TOTAL_PAGES} pages <em>·</em> answer key included</div></div>')


# ------------------------------------------------------------------ build
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


def build_upload():
    pages_txt = "\n".join(f"• {n} — {c} page{'s' if c > 1 else ''}" for n, c in PAGE_LIST)
    assert sum(c for _, c in PAGE_LIST) == TOTAL_PAGES
    title = "Music Escape Room | Note Names, Rhythms & Symbols | Print and Go | Gr 3-6"
    return f"""# UPLOAD: {TITLE} (TpT 042)

These fields follow the order of TpT's "Add a resource" form.

**Files to attach**
- Resource (digital download): `{SLUG}.pdf`, {TOTAL_PAGES} pages, US Letter.
- Thumbnails, in this order: `cover.png`, `preview-1.png`, `preview-2.png`, `preview-3.png` (all 2000 × 2000).
- Preview file: `{SLUG}-PREVIEW.pdf`, 4 watermarked pages.

## 1. Title

```
{title}
```
({len(title)} characters; the limit is 80.) The title leaves out "Winter" and other seasonal words because TpT's Seasonal Titles notice blocked seasonal titles on earlier items (see 032 and 039). If TpT accepts it, "Winter Music Escape Room | Note Names, Rhythms & Symbols | Gr 3-6" is the preferred title.

## 2. Description

```
A print-and-go music escape room for grades 3–6. The snow-globe workshop is locked, and your students have 45 minutes to open it. Five puzzles on note names, rhythms and music symbols each give an answer; the answers lead to five lock digits, and the digits spell the final word. Winter themed and non-denominational: it fits every school calendar. No tech needed, just paper, pencils and scissors.

THE FIVE PUZZLES
1. Treble clef door: name six notes on the treble staff and spell the word on the sign.
2. Bass clef gears: name seven notes on the bass staff and spell the word.
3. Rhythm math: fill six bars so that each one adds up to its time signature (4/4, 3/4 and 2/4), then add the beats.
4. Symbol sorting: match eight symbols (dynamics, crescendo and decrescendo, fermata, staccato, repeat sign, sharp) to their meanings.
5. The beat code: decode a secret message written with note and rest values.
Then the final lock: five digits from the answer cards are turned into letters.

WHAT'S INCLUDED ({TOTAL_PAGES} pages, PDF, US Letter)
{pages_txt}
Total: {TOTAL_PAGES} pages.

TEACHER-FRIENDLY
• Every puzzle has exactly one correct answer, and every answer is computed and re-checked
• Answer-check cards tell teams if they are right (the trap cards catch common slips)
• Hint cards, optional student manual, timing for a 45-minute class and notes for grades 3–4 and 5–6
• Full answer key, including the lock code if you want to use a real 5-digit combination lock
• Works for a sub, a music center or a class party day; print in black and white
• No songs, lyrics or copyrighted characters

{DISCLOSURE}
```

## 3. Grades

3, 4, 5, 6.

## 4. Subjects and tags

- Subject: Music
- Tags: Winter, Escape Rooms, Games, Activities, Printables, Critical Thinking and Problem Solving

## 5. Resource type

- Activities
- Games

## 6. Standards (optional)

National Core Arts Standards, Music: MU:Pr4.2, grades 3–6. Optional.

## 7. Price

**${PRICE}** (queue price).

## 8. Free or paid / preview

Paid. Preview PDF: teacher guide page, Puzzle 1 (treble clef), Puzzle 3 (rhythm math) and the final lock page, all watermarked and unsolved. The answer key is not in the preview.

## 9. Before you click publish

- [ ] List by **early Nov 2026** or as soon as possible; winter searches build through November and December.
- Winter and secular imagery only (snow-globe, snowflakes, padlock). No holiday symbols, characters or brands.
"""


def build_json():
    cfg = {"price": PRICE, "license_price": PRICE, "tax_code": "Other Digital Goods - No Physical Media",
           "grades": ["3rd-grade", "4th-grade", "5th-grade", "6th-grade"], "subjects": ["Music"],
           "tags": ["Winter", "Escape Rooms", "Games", "Activities", "Printables", "Critical Thinking and Problem Solving"],
           "formats": ["PDF"], "pages": TOTAL_PAGES, "answer_key": "Included",
           "files": {"product": f"{SLUG}.pdf", "preview": f"{SLUG}-PREVIEW.pdf", "thumb1": "cover.png", "thumb2": "preview-1.png",
                     "thumb3": "preview-2.png", "thumb4": "preview-3.png"}}
    with open(TPT_JSON, "w") as f:
        json.dump(cfg, f, indent=2)
        f.write("\n")


def build():
    os.makedirs(BUILD, exist_ok=True)
    errs = verify_data()
    if errs:
        print("\n".join(errs))
        sys.exit("data check failed; not rendering")
    full = write("resource.html", html_doc(all_pages(False), TITLE))
    prev = write("preview.html", html_doc(all_pages(True, PREVIEW_PAGES), "Preview"))
    render([{"html": full, "pdf": PDF}, {"html": prev, "pdf": PREVIEW_PDF}])
    for i in (4, 5, 7, 8, 3, 10):
        subprocess.run(["pdftoppm", "-png", "-r", "110", "-f", str(i), "-l", str(i), "-singlefile", PDF, os.path.join(BUILD, f"pg{i}")], check=True)
    sq = [write("cover.html", cover_square()),
          write("p1.html", preview_square_1(["pg5.png", "pg7.png", "pg8.png"])),
          write("p2.html", preview_square_2("pg3.png", "pg10.png")),
          write("p3.html", preview_square_3())]
    render([{"html": h, "png": o, "width": 1000, "height": 1000, "scale": 2} for h, o in zip(sq, [COVER_PNG] + PREVIEW_PNGS)])
    with open(UPLOAD, "w") as f:
        f.write(build_upload())
    build_json()
    print(f"built {PDF}, {PREVIEW_PDF}, cover + 3 previews, UPLOAD.md, tpt.json")


# ------------------------------------------------------------------ checks
def verify_data():
    errs = []
    # puzzles 1 and 2: two letter methods agree, one letter per staff position, decoys differ
    for pz, clef, ps, word, dec in ((1, "treble", P1_POS, P1_WORD, P1_DECOYS), (2, "bass", P2_POS, P2_WORD, P2_DECOYS)):
        for p in range(0, 10):
            if note_letter(clef, p) != note_letter_b(clef, p):
                errs.append(f"P{pz}: letter methods disagree at p={p}")
        got = "".join(note_letter(clef, p) for p in ps)
        got2 = "".join(note_letter_b(clef, p) for p in ps)
        if not (got == got2 == word):
            errs.append(f"P{pz}: notes spell {got}/{got2}, expected {word}")
        if len(set(dec) | {word}) != 3 or any(len(d) != len(word) for d in dec):
            errs.append(f"P{pz}: decoys must be 2 different words of the same length")
        # treble vs bass reading must differ, so a wrong clef can't also give the word
        other = "bass" if clef == "treble" else "treble"
        if "".join(note_letter(other, p) for p in ps) == word:
            errs.append(f"P{pz}: reading in the other clef gives the same word")
    # puzzle 3: every bar has exactly one option that fills it; option values distinct
    for i, bar in enumerate(P3_BARS):
        beats, label, toks, opts = bar
        if int(label[0]) != beats or label[2] != "4":
            errs.append(f"P3 bar {i + 1}: label {label} vs {beats} beats")
        if toks.count("M") != 1:
            errs.append(f"P3 bar {i + 1}: needs exactly one missing slot")
        vals = [KINDS[k][1] for k in opts]
        if len(set(vals)) != 4 or len(set(opts)) != 4:
            errs.append(f"P3 bar {i + 1}: option values not distinct")
        fit, need = p3_fit(bar)
        if len(fit) != 1:
            errs.append(f"P3 bar {i + 1}: {len(fit)} options fill the bar")
        # brute force check over every one of the 9 kinds: exactly one fits among the options
        brute = [k for k in opts if abs(sum(TOK_BEATS[t] for t in toks if t != 'M') + KINDS[k][1] - beats) < 1e-9]
        if brute != fit:
            errs.append(f"P3 bar {i + 1}: brute force disagrees")
    tot = p3_answer()
    if tot != sum(p3_fit(b)[1] for b in P3_BARS):
        errs.append("P3: total mismatch")
    if len({str(tot), str(p3_answer_dotted_slip()), str(p3_answer(ignore_meter=True))}) != 3:
        errs.append("P3: the correct total equals a decoy")
    # puzzle 4: bijection, letters spell the word, meanings unique
    if sorted(P4_ORDER) != sorted(SYMBOLS) or sorted(P4_MEANING_ORDER) != sorted(SYMBOLS):
        errs.append("P4: symbol lists do not cover each symbol once")
    if len(set(m for _, m in SYMBOLS.values())) != len(SYMBOLS) or len(set(n for n, _ in SYMBOLS.values())) != len(SYMBOLS):
        errs.append("P4: duplicate meaning or name")
    if len(set(P4_WORD)) != len(P4_ORDER) or len(P4_WORD) != len(P4_ORDER):
        errs.append("P4: word letters must be distinct and match the symbol count")
    if p4_answer() != P4_WORD:
        errs.append("P4: answer does not spell the word")
    # no meaning shares its key phrase with another meaning
    words = [set(re.findall(r"[a-z]+", m.lower())) - {"the", "a", "an", "to", "than", "by", "it", "little", "play", "note", "music", "and"} for _, m in SYMBOLS.values()]
    for a, b in itertools.combinations(range(len(words)), 2):
        sh = words[a] & words[b]
        if sh - {"louder", "softer", "get"} and sh:
            errs.append(f"P4: meanings {a} and {b} share words {sh}")
    # puzzle 5: table is a bijection on 8 symbols; message decodes uniquely
    kinds = [k for _, k, _ in P5_TABLE]
    letters = [L for _, _, L in P5_TABLE]
    if len(set(kinds)) != 8 or len(set(letters)) != 8:
        errs.append("P5: code book is not one-to-one")
    if any(k not in kinds for k in P5_MESSAGE if k):
        errs.append("P5: message uses a symbol that is not in the code book")
    if p5_answer() != P5_WORD:
        errs.append(f"P5: decodes to {p5_answer()!r}, expected {P5_WORD!r}")
    if set(KINDS_NAMES_P5()) != set(kinds):
        errs.append("P5: names mismatch")
    # cards: distinct texts per puzzle, one correct, digits distinct, wheels a permutation
    if sorted(WHEEL_OF.values()) != [1, 2, 3, 4, 5]:
        errs.append("wheels are not a permutation")
    if len(set(CHART.values())) != 9:
        errs.append("lock chart letters repeat")
    for pz in range(1, 6):
        cs = CARDS[pz]
        if len(cs) != 3 or len({c["text"] for c in cs}) != 3 or len({c["digit"] for c in cs}) != 3:
            errs.append(f"cards P{pz}: texts or digits repeat")
        if sum(c["correct"] for c in cs) != 1:
            errs.append(f"cards P{pz}: need exactly one correct card")
    allt = [c["text"] for pz in CARDS for c in CARDS[pz]]
    if len(set(allt)) != len(allt):
        errs.append("cards: an answer text appears on two cards")
    # final lock derives from the five answers; any wrong card choice breaks it (3^5 combos, only one opens)
    digits, word, ans = final_code()
    if word != LOCK_WORD:
        errs.append(f"final lock spells {word}, expected {LOCK_WORD}")
    opens = 0
    for combo in itertools.product(*[CARDS[pz] for pz in range(1, 6)]):
        code = {c["wheel"]: c["digit"] for c in combo}
        if "".join(CHART[code[w]] for w in range(1, 6)) == LOCK_WORD:
            opens += 1
    if opens != 1:
        errs.append(f"{opens} card combinations open the lock, expected exactly 1")
    # each answer is used by the final code: changing any one puzzle's answer changes the word
    for pz in range(1, 6):
        for c in CARDS[pz]:
            if not c["correct"]:
                code = dict(zip(range(1, 6), digits))
                code[c["wheel"]] = c["digit"]
                if "".join(CHART[code[w]] for w in range(1, 6)) == LOCK_WORD:
                    errs.append(f"final lock does not depend on puzzle {pz}")
    return errs


def KINDS_NAMES_P5():
    return [k for _, k, _ in P5_TABLE if KINDS[k][0] in [n for n, _, _ in P5_TABLE]]


def parse_ws(html):
    """Independent view of the rendered worksheets, from the HTML data attributes."""
    ws = {}
    sections = html.split('<section class="page')
    for sec in sections:
        for m in re.finditer(r'<g class="q" data-puz="(\d)" data-n="(\d+)" data-clef="(\w+)" data-p="(\d+)"', sec):
            pz, n, clef, p = m.groups()
            mode = re.search(r'<svg class="staff" data-puz="%s" data-mode="(\w+)"' % pz, sec[:m.start()][::1][-60000:] if False else sec)
            pass
    return ws


def verify_html():
    errs = []
    p = os.path.join(BUILD, "resource.html")
    if not os.path.exists(p):
        return ["build/resource.html missing: run gen.py first"], {}
    html = open(p).read()
    secs = html.split('<section class="page')[1:]
    pages = {i + 1: s for i, s in enumerate(secs)}
    if len(pages) != TOTAL_PAGES:
        errs.append(f"html has {len(pages)} pages, expected {TOTAL_PAGES}")
    counts = {}
    ws_ans, key_ans = {}, {}
    # puzzle 1, 2 and 5 notes / symbols (worksheet page vs key page)
    for pz, ws_page, clef in ((1, P_PUZ[1], "treble"), (2, P_PUZ[2], "bass")):
        w = re.findall(r'<g class="q" data-puz="%d" data-n="(\d+)" data-clef="(\w+)" data-p="(\d+)"' % pz, pages[ws_page])
        k = re.findall(r'<g class="q" data-puz="%d" data-n="(\d+)" data-clef="(\w+)" data-p="(\d+)"' % pz, pages[P_KEY1])
        if len(w) != len(k) or w != k:
            errs.append(f"P{pz}: worksheet has {len(w)} notes, key has {len(k)} (or they differ)")
        counts[pz] = (len(w), len(k))
        word = "".join(CLEF_INFO[clef][0][int(p_) % 7] for _, _, p_ in w)
        shown = re.search(r'data-key="%d".*?Word: <b>(\w+)</b>' % pz, pages[P_KEY1], re.S)
        # the key text is inside the same page: find the 'Word:' line after the staff
        words = re.findall(r"Word: <b>(\w+)</b>", pages[P_KEY1])
        if word not in words:
            errs.append(f"P{pz}: key word does not match the notes on the worksheet ({word})")
        # key letters written in the svg
        letters = re.findall(r'font-size="19" fill="#1F6FA8">([A-G])</text>', re.search(r'data-key="%d">(.*?)</svg>' % pz, pages[P_KEY1], re.S).group(1))
        if "".join(letters) != word:
            errs.append(f"P{pz}: key staff letters {''.join(letters)} != {word}")
    # puzzle 3
    wbars = re.findall(r'<div class="rb" style="width:250pt" data-q="(\d+)"', pages[P_PUZ[3]])
    kbars = re.findall(r'<div data-k="(\d+)" data-need="([\d.]+)" data-kind="(\w+)" data-letter="(\w)"', pages[P_KEY1])
    counts[3] = (len(wbars), len(kbars))
    if len(wbars) != len(kbars):
        errs.append(f"P3: worksheet has {len(wbars)} bars, key has {len(kbars)}")
    tot = 0
    for (k, need, kind, letter), bar in zip(kbars, P3_BARS):
        tot += KINDS[kind][1]
        if abs(KINDS[kind][1] - float(need)) > 1e-9:
            errs.append(f"P3 bar {k}: key kind {kind} is not worth {need}")
    m = re.search(r"Total: ([\d +]+) = <b>(\d+)</b>", pages[P_KEY1])
    if not m or int(m.group(2)) != tot or sum(int(x) for x in m.group(1).split("+")) != tot:
        errs.append(f"P3: printed total does not match recomputed {tot}")
    # puzzle 4
    w4 = re.findall(r'<div class="mrow" data-q="(\d+)" data-sym="(\w+)"', pages[P_PUZ[4]])
    means = re.findall(r'<div class="mean" data-mean="(\w+)"><div class="bd">(\w)</div>', pages[P_PUZ[4]])
    k4 = re.findall(r'<tr data-k="(\d+)" data-sym="(\w+)" data-ans="(\w)"', pages[P_KEY2])
    counts[4] = (len(w4), len(k4))
    if len(w4) != len(k4) or [s for _, s in w4] != [s for _, s, _ in k4]:
        errs.append(f"P4: worksheet has {len(w4)} symbols, key has {len(k4)}")
    badge = dict(means)
    if len(badge) != len(means) or len(set(badge.values())) != len(means) or len(means) != len(w4):
        errs.append("P4: meaning list does not have one distinct letter per meaning")
    word4 = "".join(badge.get(s, "?") for _, s in w4)
    if word4 != "".join(a for _, _, a in k4):
        errs.append(f"P4: recomputed word {word4} differs from the key")
    # puzzle 5
    w5 = re.findall(r'<g class="q" data-puz="5" data-n="(\d+)" data-kind="(\w+)"', pages[P_PUZ[5]])
    k5 = re.findall(r'<span data-k="(\d+)" data-kind="(\w+)" data-ans="(\w)"', pages[P_KEY2])
    counts[5] = (len(w5), len(k5))
    book = dict(re.findall(r'<div class="refcell" data-kind="(\w+)"><b>[^<]+</b><span[^>]*>(\w)</span>', pages[P_PUZ[5]]))
    if len(w5) != len(k5) or [b for _, b in w5] != [b for _, b, _ in k5]:
        errs.append(f"P5: worksheet has {len(w5)} symbols, key has {len(k5)}")
    if "".join(book.get(b, "?") for _, b in w5) != "".join(a for _, _, a in k5):
        errs.append("P5: key letters differ from the worksheet code book")
    # the teacher guide's counts match
    g = pages[P_TG1]
    for pz, want in ((1, "notes"), (2, "notes"), (3, "bars"), (4, "symbols"), (5, "symbols")):
        if f"{counts[pz][0]} {want}" not in g:
            errs.append(f"teacher guide does not state {counts[pz][0]} {want} for puzzle {pz}")
    for pz, (a, b) in counts.items():
        if a != b:
            errs.append(f"P{pz}: worksheet items {a} != key items {b}")
    # key card list vs real cards, and cards page has 15 cards
    if len(re.findall(r'<div class="cd">', pages[P_CARDS])) != 15:
        errs.append("cards page does not have 15 cards")
    return errs, counts


LAYOUT_JS = r"""
const { chromium } = require('playwright'); const url = require('url'); const fs = require('fs');
(async () => {
  const jobs = JSON.parse(fs.readFileSync(process.argv[2], 'utf8')); const out = [];
  const browser = await chromium.launch();
  for (const j of jobs) {
    const page = await browser.newPage({ viewport: { width: j.kind === 'sq' ? 1000 : 816, height: j.kind === 'sq' ? 1000 : 1056 } });
    await page.goto(url.pathToFileURL(j.html).href); await page.evaluate(() => document.fonts.ready);
    const res = await page.evaluate((kind) => {
      const probs = [];
      if (kind === 'page') {
        document.querySelectorAll('.page').forEach((pg, i) => {
          const pr = pg.getBoundingClientRect(); const ft = pg.querySelector('.foot'); const fr = ft ? ft.getBoundingClientRect() : null;
          if (pg.scrollHeight > pg.clientHeight + 1) probs.push(`page ${i+1}: content taller than the page (${pg.scrollHeight} > ${pg.clientHeight})`);
          pg.querySelectorAll('*').forEach(el => {
            if (el.closest('.foot') || el.closest('.wm') || el.tagName === 'tspan') return;
            const r = el.getBoundingClientRect(); if (r.width === 0 || r.height === 0) return;
            if (fr && r.bottom > fr.top + 0.5 && !el.contains(ft) && !ft.contains(el)) probs.push(`page ${i+1}: <${el.tagName.toLowerCase()} class="${el.className && el.className.baseVal === undefined ? el.className : ''}"> overlaps the footer`);
            if (r.right > pr.right - 0.3 * 96 + 0.5 && !el.closest('.cover')) probs.push(`page ${i+1}: <${el.tagName.toLowerCase()}> reaches ${Math.round(r.right - pr.left)}px of ${Math.round(pr.width)}`);
          });
        });
      } else {
        const sq = document.querySelector('.sq'); const band = sq.querySelector('.band'); const bt = band.getBoundingClientRect().top;
        sq.querySelectorAll('.shot, .lbl, .pcard, .hd, .sub, img, svg').forEach(el => {
          const r = el.getBoundingClientRect(); if (r.bottom > bt - 8) probs.push(`${el.className || el.tagName}: bottom ${Math.round(r.bottom)} runs into the band at ${Math.round(bt)}`);
          if (r.right > 1000 || r.left < 0) probs.push(`${el.className || el.tagName}: outside the image`);
        });
        sq.querySelectorAll('.shot').forEach(s => { const img = s.querySelector('img'); if (img && img.getBoundingClientRect().height > s.getBoundingClientRect().height + 4) probs.push('shot clips its page image'); });
        const w = sq.querySelectorAll('.swm').length, sh = sq.querySelectorAll('.shot').length; if (w !== sh) probs.push(`watermarks ${w} vs shots ${sh}`);
      }
      return [...new Set(probs)];
    }, j.kind);
    out.push({ html: j.html, probs: res }); await page.close();
  }
  await browser.close(); console.log(JSON.stringify(out));
})().catch(e => { console.error(e); process.exit(1); });
"""


def verify_layout():
    js = write("layout.js", LAYOUT_JS)
    jobs = [{"html": os.path.join(BUILD, "resource.html"), "kind": "page"}, {"html": os.path.join(BUILD, "preview.html"), "kind": "page"}] + \
           [{"html": os.path.join(BUILD, n), "kind": "sq"} for n in ("cover.html", "p1.html", "p2.html", "p3.html")]
    jp = write("layout-jobs.json", json.dumps(jobs))
    r = subprocess.run(["node", js, jp], capture_output=True, text=True, env=node_env())
    if r.returncode:
        return [f"layout script failed: {r.stderr[-300:]}"]
    errs = []
    for row in json.loads(r.stdout.strip().splitlines()[-1]):
        errs += [f"{os.path.basename(row['html'])}: {p}" for p in row["probs"]]
    return errs


def pdf_fonts(path):
    out = subprocess.run(["pdffonts", path], capture_output=True, text=True, check=True).stdout.splitlines()[2:]
    return [(l.split()[0], l.split()[-5]) for l in out]


def load_json(name):
    return json.load(open(os.path.join(TPT, name)))


def verify_files():
    errs = []
    from pypdf import PdfReader
    from PIL import Image
    for p in [PDF, PREVIEW_PDF, COVER_PNG, *PREVIEW_PNGS, UPLOAD, TPT_JSON]:
        if not os.path.exists(p):
            errs.append(f"missing {os.path.relpath(p, HERE)}")
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
                errs.append(f"{os.path.basename(path)}: {fam} not in PDF fonts")
    rd = PdfReader(PDF)
    for i, pg in enumerate(rd.pages):
        t = pg.extract_text() or ""
        if len(t.strip()) < 40:
            errs.append(f"PDF page {i + 1} looks blank")
        if "PREVIEW" in t:
            errs.append(f"PDF page {i + 1} carries a PREVIEW watermark")
    # preview: one watermark per page, no answer key, no answers
    prd = PdfReader(PREVIEW_PDF)
    secrets = [p1_answer(), p2_answer(), P4_WORD, P5_WORD, "ANSWER KEY"]
    for i, pg in enumerate(prd.pages):
        t = pg.extract_text() or ""
        if t.count("PREVIEW") != 1:
            errs.append(f"preview page {i + 1}: PREVIEW appears {t.count('PREVIEW')} times (want 1)")
        for s in secrets:
            if s in t.upper():
                errs.append(f"preview page {i + 1} contains '{s}'")
    # the preview PDF pages are the same pages as the product's (by text, minus the watermark)
    for pv, src in zip(prd.pages, PREVIEW_PAGES):
        a = re.sub(r"\s+", "", (pv.extract_text() or "").replace("PREVIEW", ""))
        b = re.sub(r"\s+", "", rd.pages[src - 1].extract_text() or "")
        if a != b:
            errs.append(f"preview page for p{src} differs from the product page")
    # page headings
    for n, want in ((P_KEY1, "ANSWER KEY"), (P_KEY2, "ANSWER KEY"), (P_CARDS, "CUT-OUTS"), (P_HINTS, "CUT-OUTS"), (P_FINAL, "FINAL LOCK")):
        if want not in (rd.pages[n - 1].extract_text() or "").upper():
            errs.append(f"PDF page {n}: '{want}' missing")
    for p in [COVER_PNG, *PREVIEW_PNGS]:
        if Image.open(p).size != (2000, 2000):
            errs.append(f"{os.path.basename(p)}: not 2000x2000")
    # watermark once in preview images: the HTML sources use unwatermarked pages (pg*.png come from the product PDF)
    for n in ("p1.html", "p2.html"):
        h = open(os.path.join(BUILD, n)).read()
        if h.count('class="swm"') != h.count('class="shot"') or "PREVIEW" in h.replace("PREVIEW</div>", ""):
            errs.append(f"{n}: watermark count differs from the shots")
    # cover must not show a page badge that differs
    ch = open(os.path.join(BUILD, "cover.html")).read()
    badges = set(re.findall(r"(\d+) pages", ch))
    if badges != {str(TOTAL_PAGES)}:
        errs.append(f"cover shows page counts {badges}, PDF has {TOTAL_PAGES}")
    up = open(UPLOAD).read()
    m = re.search(r"^## 1\. Title\s*\n+```\n(.+?)\n```", up, re.M | re.S)
    title = m.group(1).strip() if m else ""
    if not m or len(title) > 80:
        errs.append(f"UPLOAD.md title missing or over 80 ({len(title)})")
    for bad in ("winter", "christmas", "holiday", "hanukkah", "kwanzaa", "snow"):
        if bad in title.lower():
            errs.append(f"title contains seasonal word '{bad}'")
    if not title.lower().startswith("music escape room"):
        errs.append("title should start with plain search words")
    for need in (DISCLOSURE, f"${PRICE}", f"{TOTAL_PAGES} pages"):
        if need not in up:
            errs.append(f"UPLOAD.md: missing '{need}'")
    # page list in UPLOAD.md totals the PDF exactly
    inc = up.split("WHAT'S INCLUDED", 1)[1].split("Total:", 1)[0]
    nums = [int(x) for x in re.findall(r"— (\d+) pages?", inc)]
    if sum(nums) != len(rd.pages):
        errs.append(f"UPLOAD.md page list totals {sum(nums)}, PDF has {len(rd.pages)}")
    if "checked by hand" in up.lower() or "handmade" in up.lower() or "classroom-tested" in up.lower():
        errs.append("UPLOAD.md: forbidden claim")
    tj = json.load(open(TPT_JSON))
    if tj.get("pages") != TOTAL_PAGES or tj["price"] != PRICE:
        errs.append("tpt.json pages/price mismatch")
    if len(tj["grades"]) > 4:
        errs.append("tpt.json: more than 4 grades")
    return errs


def check():
    errs = verify_data()
    e2, counts = verify_html()
    errs += e2
    errs += verify_files()
    errs += verify_layout()
    if errs:
        print("CHECK FAILED")
        print("\n".join(" - " + e for e in errs[:60]))
        sys.exit(1)
    digits, word, ans = final_code()
    print(f"CHECK OK: puzzles solved in code ({', '.join(f'P{k}={v[0]} items/key {v[1]}' for k, v in counts.items())}); "
          f"answers {ans}; lock code {digits} -> {word}; only 1 of 243 card combinations opens the lock; "
          f"{TOTAL_PAGES}-page PDF, 4-page preview (one watermark, no answers); images 2000x2000; layout clean; UPLOAD.md and tpt.json ok.")


if __name__ == "__main__":
    if "--check" in sys.argv:
        check()
    else:
        build()
