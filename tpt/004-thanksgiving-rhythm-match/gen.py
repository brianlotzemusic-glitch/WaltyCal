#!/usr/bin/env python3
"""Thanksgiving Rhythm Match + Echo Cards (TpT 004): build the resource and verify it.

    python3 gen.py           build everything (PDFs, PNGs, tpt.json) into this folder
    python3 gen.py --check   verify phrases, rhythms, keys, pages, fonts and files

Grades 1-3, four rhythm values only (item 002's rhythm.py tokens):
    q  ta      quarter note        1 beat, 1 sound
    e  ti-ti   two eighth notes    1 beat, 2 sounds
    r  (shh)   quarter rest        1 beat, silent
    h  ta-a    half note           2 beats, 1 sound held

Every word phrase is written beat by beat ("|" between beats, a space between
syllables in one beat, "~" on a word held for two beats, "(shh)" for a silent
beat). Its rhythm is derived from the syllables and must equal the rhythm it is
paired with, so the match key is checked from two independent sources.

Rendering uses Playwright + Chromium (HTML/SVG -> PDF/PNG) through the shared
../tools/render.js, with the OFL fonts in ../fonts embedded as subsets.
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
sys.path.insert(0, HERE)
from art import art  # noqa: E402

TPT = os.path.dirname(HERE)
_spec = importlib.util.spec_from_file_location("rhythm002", os.path.join(TPT, "002-fall-rhythm-flashcards", "rhythm.py"))
R = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(R)

FONTS = os.path.join(TPT, "fonts")
BUILD = os.path.join(HERE, "build")
RENDER_JS = os.path.join(TPT, "tools", "render.js")

SLUG = "thanksgiving-rhythm-match"
PDF = os.path.join(HERE, f"{SLUG}.pdf")
PREVIEW_PDF = os.path.join(HERE, f"{SLUG}-PREVIEW.pdf")
COVER_PNG = os.path.join(HERE, "cover.png")
PREVIEW_PNGS = [os.path.join(HERE, f"preview-{i}.png") for i in (1, 2, 3)]
UPLOAD = os.path.join(HERE, "UPLOAD.md")
TPT_JSON = os.path.join(HERE, "tpt.json")

STORE = "Brian Lotze"      # copyright holder
BRAND = "Hudson Beat"      # store line on covers and previews (owner, 4 Oct)
YEAR = 2026
ACCENT = "#B5471E"         # this product's single accent (Thanksgiving rust, a little deeper than 002's)
TITLE = "Thanksgiving Rhythm Match"
PRICE = "3.50"
LOW_RES = "--lowres" in sys.argv   # self-check renders: scale 1 PNGs, nothing else changes

# ---------------------------------------------------------------- the content
# (phrase, rhythm, picture). Phrases are original; stressed syllables land on the beat.
SET1 = [  # ta and ti-ti only
    ("Pump- kin|pie,|pump- kin|pie", "eqeq", "pie"),
    ("Tur- key,|tur- key,|run a-|way!", "eeeq", "turkey"),
    ("Corn,|beans,|squash,|pie!", "qqqq", "corn"),
    ("Rake,|rake,|rake the|leaves", "qqeq", "maple"),
    ("Tur- key,|gra- vy,|pump- kin,|muf- fins", "eeee", "pumpkin"),
    ("Leaf,|a- corn,|leaf,|a- corn", "qeqe", "acorn"),
    ("Pop- corn,|pop,|pop,|pop!", "eqqq", "corn"),
    ("Crunch,|crunch,|crack- le,|crack- le", "qqee", "leaf"),
    ("Ap- ple|ci- der,|yum,|yum!", "eeqq", "apple"),
    ("Leaves|fall- ing,|fall- ing|down", "qeeq", "maple"),
    ("Gob- ble,|gob,|gob,|gob- ble!", "eqqe", "turkey"),
    ("Pies:|pump- kin,|ap- ple,|cher- ry", "qeee", "pie"),
]
SET2 = [  # adds the quarter rest and the half note
    ("Leaves|fall- ing|down,|(shh)", "qeqr", "leaf"),
    ("Pump- kin|pie,|(shh)|yum!", "eqrq", "pie"),
    ("Gob- ble,|gob- ble,|gob!~", "eeh", "turkey"),
    ("Rake,|rake,|leaves!~", "qqh", "maple"),
    ("Pie~|for|me!", "hqq", "pie"),
    ("Mmm,~|pump- kin|muf- fins!", "hee", "pumpkin"),
    ("Fall,~|crunch- y|leaves", "heq", "leaf"),
    ("Crunch,~|crunch,|(shh)", "hqr", "maple"),
    ("Gob,|(shh)|gob,|(shh)", "qrqr", "turkey"),
    ("Tur- key,|tur- key,|(shh)|gob!", "eerq", "turkey"),
    ("Pie,|(shh)|ap- ple|pie", "qreq", "apple"),
    ("(shh)|yum,|pump- kin|pie", "rqeq", "pumpkin"),
]
MATCH = SET1 + SET2
LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWX"
SEED = 1128                # rhythm-card letter order; checked to be a derangement within each set

# Echo cards: three levels of 8, each pattern exactly one 4/4 bar.
ECHO = [
    ("Level 1", "ta · ti-ti", "qqqq qqee eeqq qeqe qqqe qeqq eqee eeqe".split()),
    ("Level 2", "adds the rest", "qqqr qqrq qrqr eeqr eqer qreq ereq eeer".split()),
    ("Level 3", "adds the half note", "qqh hqq eeh hee qeh heq hh hqr".split()),
]
ECHO_POOL = [p for _, _, ps in ECHO for p in ps]
ECHO_ART = ["turkey", "pie", "corn", "apple", "maple", "acorn", "pumpkin", "leaf"]

# Worksheets: which match phrases (0-based) appear, and the order of the rhythms on the right.
WS = [
    ("Match It! 1", "ta and ti-ti", [1, 2, 5, 7, 9, 11]),
    ("Match It! 2", "rests and half notes", [12, 14, 16, 18, 21, 22]),
]
WRITE = [  # "write the rhythm" worksheet: new phrases, not on the cards
    ("Pass the|corn,|please!|(shh)", "eqqr", "corn"),
    ("Bake a|pie,|bake a|pie", "eqeq", "pie"),
    ("Leaves|on the|ground|(shh)", "qeqr", "leaf"),
    ("Gath- er|round the|ta- ble|(shh)", "eeer", "turkey"),
    ("Rake,|rake,|jump!~", "qqh", "maple"),
    ("Crunch~|crunch!~", "hh", "acorn"),
]
WORD_BANK = [("pie", "pie", 1), ("corn", "corn", 1), ("leaf", "leaf", 1), ("yum", "pie", 1),
             ("tur-key", "turkey", 2), ("pump-kin", "pumpkin", 2), ("ap-ple", "apple", 2), ("a-corn", "acorn", 2)]

SYL = {"q": "ta", "e": "ti-ti", "r": "shh", "h": "ta-a"}


def tokens(phrase):
    return phrase.split("|")


def derive(phrase):
    """Rhythm from the words alone: 1 syllable = ta, 2 = ti-ti, '(shh)' = rest, '~' = held 2 beats."""
    out = ""
    for t in tokens(phrase):
        if t == "(shh)":
            out += "r"
        elif t.endswith("~"):
            out += "h" if len(t[:-1].split()) == 1 else "?"
        else:
            out += {1: "q", 2: "e"}.get(len(t.split()), "?")
    return out


def beat_text(tok):
    """Display text for one beat group: 'Pump- kin' -> 'Pump-kin', 'run a-' -> 'run a-'."""
    t = tok.rstrip("~")
    return re.sub(r"- ", "-", t)


def box_text(tok):
    """Text inside a beat box: as beat_text, minus trailing commas and colons (the boxes already separate the beats)."""
    return beat_text(tok).rstrip(",:")


def sentence(phrase):
    return re.sub(r"- ", "-", " ".join(beat_text(t) for t in tokens(phrase)))


def letter_order():
    """LETTERS[k] names rhythm card k; ORDER[k] is the match phrase on it. Shuffled within each set."""
    rnd = random.Random(SEED)
    order = []
    for base in (0, 12):
        idx = list(range(base, base + 12))
        rnd.shuffle(idx)
        order += idx
    return order


ORDER = letter_order()
LETTER_OF = {pid: LETTERS[k] for k, pid in enumerate(ORDER)}


def ws_order(n):
    """Right-hand rhythm order for worksheet n: a fixed derangement of its 6 rows."""
    rnd = random.Random(SEED + 7 + n)
    rows = list(range(6))
    while True:
        rnd.shuffle(rows)
        if all(r != i for i, r in enumerate(rows)):
            return list(rows)


WS_ORDER = [ws_order(n) for n in range(len(WS))]


# ---------------------------------------------------------------- html scaffolding (from 003)
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
.how { font-size: 12pt; margin: 3pt 0 6pt; }
.how b { font-weight: 700; }
.body { flex: 1; display: flex; align-items: center; justify-content: center; }
.foot { display: flex; justify-content: space-between; font-size: 8.5pt; color: #333; border-top: .8pt solid #000; padding-top: 3pt; }
.wm { position: absolute; left: 50%; top: 50%; transform: translate(-50%, -50%) rotate(-38deg); font-family: 'Oswald'; font-weight: 700;
      font-size: 150pt; color: rgba(0,0,0,.13); letter-spacing: .06em; white-space: nowrap; pointer-events: none; z-index: 9; }
.doc h1 { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 30pt; margin: 0 0 4pt; line-height: 1; }
.doc h2 { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 14pt; margin: 11pt 0 4pt; letter-spacing: .02em; }
.doc h2 .acc { color: ACCENT; }
.doc p, .doc li { font-size: 10.8pt; line-height: 1.34; margin: 0 0 4pt; }
.doc ul, .doc ol { margin: 0 0 4pt; padding-left: 15pt; }
.doc .rule { border-bottom: 2.2pt solid #000; margin-bottom: 6pt; padding-bottom: 6pt; }
.doc table { border-collapse: collapse; width: 100%; font-size: 10.5pt; margin: 2pt 0 4pt; }
.doc td, .doc th { border: 1pt solid #000; padding: 3pt 6pt; text-align: left; vertical-align: middle; }
.doc th { font-family: 'Oswald'; font-weight: 500; text-transform: uppercase; font-size: 10pt; background: #000; color: #fff; }
.cols { display: flex; gap: 22pt; }
.cols > div { flex: 1; }
.small { font-size: 9pt !important; color: #333; }
.ref td { text-align: center; padding: 3pt 6pt; }
.ref td.n { text-align: left; }
.ref .big { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 13pt; }
.cover { align-items: center; justify-content: space-between; padding: 0.55in 0.6in 0.5in; }
.store { font-family: 'Oswald'; font-weight: 500; font-size: 13pt; letter-spacing: .32em; text-transform: uppercase; }
.ctitle { text-align: center; }
.ctitle .a { font-family: 'Oswald'; font-weight: 700; font-size: 44pt; line-height: 1; letter-spacing: .02em; }
.ctitle .b { white-space: nowrap; font-family: 'Oswald'; font-weight: 700; font-size: 72pt; line-height: .95; letter-spacing: .01em; }
.ctitle .c { font-family: 'Oswald'; font-weight: 300; font-size: 17pt; margin-top: 8pt; }
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
    family = f"'{family}'" if " " in family else family   # unquoted "Source Sans 3" is invalid CSS and falls back to Times
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{family}" font-weight="{weight}" font-size="{size}" '
            f'text-anchor="{anchor}" fill="{fill}" {extra}>{t}</text>')


def pill(x, y, label, size=11, fill="#000", anchor="start"):
    w = len(label) * size * 0.56 + 14
    x0 = x if anchor == "start" else x - w
    return (f'<rect x="{x0:.1f}" y="{y:.1f}" width="{w:.1f}" height="{size + 9:.1f}" rx="4" fill="{fill}"/>'
            + text(x0 + w / 2, y + size + 3.2, label, size, 500, extra='letter-spacing="0.06em"', fill="#fff", upper=True))


# ---------------------------------------------------------------- building blocks
# Widths in em of every beat-box label in Source Sans 3 600, measured in Chromium (the renderer) on 9 Oct 2026.
# A label missing here falls back to 0.55 em per character, which is wider than any measured one.
WIDTH_EM = {
    "Ap-ple": 2.790, "Bake a": 2.835, "Corn": 2.058, "Crunch": 3.085, "Fall": 1.532, "Gath-er": 3.249, "Gob": 1.740,
    "Gob-ble": 3.407, "Leaf": 1.817, "Leaves": 2.927, "Mmm": 2.431, "Pass the": 3.548, "Pie": 1.351, "Pies": 1.782,
    "Pop-corn": 3.919, "Pump-kin": 4.215, "Rake": 2.108, "Red leaves": 4.562, "Tur-key": 3.228, "a-corn": 2.758,
    "ap-ple": 2.748, "bake a": 2.789, "beans": 2.565, "cher-ry": 3.080, "ci-der": 2.490, "corn": 1.920, "crack-le":
    3.344, "crunch": 2.971, "crunch!": 3.286, "crunch-y": 3.788, "down": 2.415, "fall-ing": 3.019, "for": 1.229,
    "gob": 1.616, "gob!": 1.931, "gob-ble": 3.283, "gob-ble!": 3.598, "gra-vy": 2.683, "ground": 3.112, "jump!":
    2.541, "leaf": 1.599, "leaves": 2.709, "leaves!": 3.024, "me!": 1.665, "muf-fins": 3.592, "muf-fins!": 3.907,
    "on the": 2.735, "pie": 1.333, "pie!": 1.648, "please!": 3.099, "pop": 1.677, "pop!": 1.992, "pump-kin": 4.197,
    "rake": 1.869, "rake the": 3.495, "round the": 4.218, "run a-": 2.527, "squash": 3.056, "ta-ble": 2.519,
    "tur-key": 3.087, "way!": 2.064, "yum": 1.894, "yum!": 2.209
}


def width_em(label):
    return WIDTH_EM.get(label, 0.55 * len(label))


def fit(label, width, base):
    """Largest font size up to `base` at which `label` fits `width` points."""
    return round(min(base, width / max(0.5, width_em(label))), 1)


def word_boxes(phrase, x, y, bw, bh, gap=4, fs=14, writing=False, fill="#fff"):
    """The phrase in beat boxes: one box per beat, a held word spans two. writing=True draws empty boxes."""
    out, bx = [], x
    labs = [box_text(t) for t in tokens(phrase) if t != "(shh)"]
    fs = min([fs] + [fit(lab, bw - 8, fs) for lab in labs])   # one size for the whole phrase
    for t in tokens(phrase):
        held = t.endswith("~")
        w = 2 * bw + gap if held else bw
        out.append(f'<rect x="{bx:.1f}" y="{y:.1f}" width="{w:.1f}" height="{bh:.1f}" rx="5" fill="{fill}" stroke="#000" stroke-width="1.3"/>')
        if not writing:
            cy = y + bh / 2 + fs * 0.35
            if t == "(shh)":
                out.append(text(bx + w / 2, cy, "shh", fs * 0.9, 400, "Source Sans 3", fill="#777", extra='font-style="italic"'))
            elif held:
                lab = box_text(t)
                f = fs
                out.append(text(bx + 8, cy, lab, f, 600, "Source Sans 3", anchor="start"))
                lx = bx + 14 + width_em(lab) * f
                out.append(f'<path d="M{lx:.1f},{y + bh / 2:.1f} L{bx + w - 12:.1f},{y + bh / 2:.1f}" stroke="#000" stroke-width="1.6" '
                           f'stroke-linecap="round" stroke-dasharray="0.1 4.2"/>')
                out.append(f'<path d="M{bx + w - 16:.1f},{y + bh / 2 - 4:.1f} L{bx + w - 11:.1f},{y + bh / 2:.1f} L{bx + w - 16:.1f},{y + bh / 2 + 4:.1f}" '
                           f'fill="none" stroke="#000" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/>')
            else:
                lab = box_text(t)
                out.append(text(bx + w / 2, cy, lab, fs, 600, "Source Sans 3"))
        bx += w + gap
    return "".join(out)


def notes(p, x0, yl, s, W, fill="#000", timesig=True, staff=True):
    """Rhythm on a one-line staff (beat-proportional, item 002). Returns (svg, beat centres, right edge)."""
    return R.engraved_pattern(p, x0, yl, s, W, staff=staff, timesig=timesig, fill=fill)


def notes_width(s, W, beats=4):
    return 2.6 * s + beats * W + 0.6 * s + 0.6 * s + 0.5 * s


def beat_syllables(p):
    out = []
    for t in p:
        out += ["ta-", "a"] if t == "h" else [SYL[t]]
    return out


def cut_grid(cols, rows, w, h, W, H):
    out = [f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" fill="none" stroke="#666" stroke-width="0.8" stroke-dasharray="6 4"/>']
    for c in range(1, cols):
        out.append(f'<line x1="{c * w}" y1="0" x2="{c * w}" y2="{H}" stroke="#666" stroke-width="0.8" stroke-dasharray="6 4"/>')
    for r in range(1, rows):
        out.append(f'<line x1="0" y1="{r * h}" x2="{W}" y2="{r * h}" stroke="#666" stroke-width="0.8" stroke-dasharray="6 4"/>')
    return "".join(out)


# ---------------------------------------------------------------- match cards (12 per page, 2 x 6)
CARD_AREA = (540, 624)
MC_COLS, MC_ROWS = 2, 6
MC_W, MC_H = CARD_AREA[0] / MC_COLS, CARD_AREA[1] / MC_ROWS
MC_BW = 61
MC_S, MC_BEAT = 7.0, 50


MIN_CARD_PT = 12


def card_font(phrase, bw=MC_BW, base=16):
    return min([base] + [fit(box_text(t), bw - 8, base) for t in tokens(phrase) if t != "(shh)"])


def card_font_min():
    return min(card_font(ph) for ph, _, _ in MATCH)


def word_card(pid, x, y, w=MC_W, h=MC_H):
    phrase, _, pic = MATCH[pid]
    out = [f'<rect x="{x + 6}" y="{y + 6}" width="{w - 12}" height="{h - 12}" rx="10" fill="#fff" stroke="#000" stroke-width="1.8"/>']
    out.append(pill(x + 15, y + 14, str(pid + 1), 12))
    out.append(text(x + 52, y + 29, "Say it, clap it, find its rhythm", 9, 300, anchor="start"))
    out.append(art(pic, x + w - 46, y + 10, 32, 1.3))
    bx = x + (w - (4 * MC_BW + 3 * 3)) / 2
    out.append(word_boxes(phrase, bx, y + 46, MC_BW, 44, 3, 16))
    return "".join(out)


def rhythm_card(k, x, y, w=MC_W, h=MC_H):
    pid = ORDER[k]
    p = MATCH[pid][1]
    out = [f'<rect x="{x + 6}" y="{y + 6}" width="{w - 12}" height="{h - 12}" rx="10" fill="#fff" stroke="#000" stroke-width="1.8"/>']
    out.append(pill(x + 15, y + 14, LETTERS[k], 12))
    out.append(art("leaf", x + w - 40, y + 12, 24, 1.1))
    nw = notes_width(MC_S, MC_BEAT)
    body, _, _ = notes(p, x + (w - nw) / 2, y + 74, MC_S, MC_BEAT)
    out.append(body)
    return "".join(out)


def match_page(kind, set_no, page_no, watermark=False):
    base = 12 * (set_no - 1)
    body = cut_grid(MC_COLS, MC_ROWS, MC_W, MC_H, *CARD_AREA)
    for i in range(12):
        x, y = (i % MC_COLS) * MC_W, (i // MC_COLS) * MC_H
        body += word_card(base + i, x, y) if kind == "words" else rhythm_card(base + i, x, y)
    sub = {1: "Set 1 · ta and ti-ti", 2: "Set 2 · adds the rest and the half note"}[set_no]
    if kind == "words":
        tag, hint = "WORDS", (f"Word cards #{base + 1}–#{base + 12}. Each box is one beat. "
                              '<span class="small">“shh” is a silent beat; an arrow means hold the word for two beats.</span>')
    else:
        tag, hint = "RHYTHMS", (f"Rhythm cards {LETTERS[base]}–{LETTERS[base + 11]}. "
                                '<span class="small">Letters are mixed up, so a card’s letter never gives away its match.</span>')
    return (f'<section class="page">{wm(watermark)}{top(sub, tag, f"Set {set_no} · cut on the dashed lines")}'
            f'<div class="how" style="margin-top:7pt">{hint}</div>'
            f'<div class="body">{svg(*CARD_AREA, body)}</div>{foot(f"Page {page_no}")}</section>')


# ---------------------------------------------------------------- echo cards (6 per page, 2 x 3)
EC_AREA = (540, 618)
EC_COLS, EC_ROWS = 2, 3
EC_W, EC_H = EC_AREA[0] / EC_COLS, EC_AREA[1] / EC_ROWS
EC_S, EC_BEAT = 8.0, 50


def echo_level(i):
    return i // 8


def echo_card(i, x, y, w=EC_W, h=EC_H):
    p = ECHO_POOL[i]
    lv, lvsub, _ = ECHO[echo_level(i)]
    out = [f'<rect x="{x + 7}" y="{y + 7}" width="{w - 14}" height="{h - 14}" rx="12" fill="#fff" stroke="#000" stroke-width="1.8"/>']
    out.append(pill(x + 18, y + 18, f"#{i + 1}", 13))
    out.append(text(x + 68, y + 33, f"{lv} · {lvsub}", 11, 300, anchor="start"))
    out.append(art(ECHO_ART[i % len(ECHO_ART)], x + w - 62, y + 14, 44, 1.4))
    nw = notes_width(EC_S, EC_BEAT)
    body, centres, _ = notes(p, x + (w - nw) / 2, y + 122, EC_S, EC_BEAT)
    out.append(body)
    for c, syl in zip(centres, beat_syllables(p)):
        grey = syl == "shh"
        out.append(text(c, y + 160, syl, 14, 400 if grey else 600, "Source Sans 3", fill="#666" if grey else "#000",
                        extra='font-style="italic"' if grey else ""))
    out.append(text(x + w / 2, y + h - 20, "ECHO ME!  clap · pat · play · say", 9.5, 500, extra='letter-spacing="0.08em"'))
    return "".join(out)


def echo_page(k, page_no, watermark=False):
    body = cut_grid(EC_COLS, EC_ROWS, EC_W, EC_H, *EC_AREA)
    ids = list(range(k * 6, k * 6 + 6))
    for j, i in enumerate(ids):
        body += echo_card(i, (j % EC_COLS) * EC_W, (j // EC_COLS) * EC_H)
    levels = " & ".join(sorted({ECHO[echo_level(i)][0] for i in ids}))
    return (f'<section class="page">{wm(watermark)}{top(f"Echo cards #{ids[0] + 1}–#{ids[-1] + 1} · {levels}", "ECHO", f"Page {k + 1} of 4")}'
            f'<div class="how" style="margin-top:7pt">Perform the card; the class echoes it right back. '
            f'<span class="small">“shh” is a silent beat; “ta-a” is held for two beats.</span></div>'
            f'<div class="body">{svg(*EC_AREA, body)}</div>{foot(f"Page {page_no}")}</section>')


# ---------------------------------------------------------------- worksheets
WS_ROW = 98


def match_ws(n, page_no, key=False, watermark=False):
    name, sub, picks = WS[n]
    order = WS_ORDER[n]
    out = []
    bw = 54
    for i, pid in enumerate(picks):
        y = i * WS_ROW
        phrase, _, pic = MATCH[pid]
        out.append(art(pic, 0, y + 22, 36, 1.4))
        out.append(word_boxes(phrase, 40, y + 18, bw, 46, 3, 15))
        out.append(f'<circle cx="276" cy="{y + 41}" r="5" fill="#000"/>')
        rp = MATCH[picks[order[i]]][1]
        out.append(f'<circle cx="304" cy="{y + 41}" r="5" fill="#000"/>')
        body, _, _ = notes(rp, 316, y + 54, 6.2, 46)
        out.append(body)
    if key:
        for i in range(6):
            j = order.index(i)   # row on the right that shows row i's rhythm
            out.append(f'<path d="M276,{i * WS_ROW + 41} L304,{j * WS_ROW + 41}" stroke="{ACCENT}" stroke-width="3" stroke-linecap="round"/>')
    H = 6 * WS_ROW
    body = svg(540, H, "".join(out))
    tag = ("KEY", True) if key else (f"SHEET {n + 1}", False)
    how = ("Say each phrase and clap it. Each box is one beat. Draw a line to the rhythm that matches." if not key
           else f"Answer key for “{name}” (page {page_index()[('ws', n)]}).")
    return (f'<section class="page">{wm(watermark)}{top(f"{name} · {sub}", tag[0], "Answer key" if key else "Draw a line", ak=tag[1])}'
            f'{"" if key else NAME}<div class="how" style="margin-top:{8 if key else 2}pt">{how}</div>'
            f'<div class="body">{body}</div>{foot(f"Page {page_no}")}</section>')


def write_ws(page_no, key=False, watermark=False):
    out = []
    bw, gap, row = 112, 6, 94
    x0 = 52
    for i, (phrase, p, pic) in enumerate(WRITE):
        y = i * row
        out.append(art(pic, 0, y + 16, 42, 1.4))
        out.append(word_boxes(phrase, x0, y + 4, bw, 28, gap, 14))
        out.append(word_boxes(phrase, x0, y + 36, bw, 48, gap, writing=True, fill="#fafafa"))
        for t, xs in _box_spans(phrase, x0, bw, gap):
            out.append(f'<line x1="{xs[0] + 8:.1f}" y1="{y + 70}" x2="{xs[1] - 8:.1f}" y2="{y + 70}" stroke="#bbb" stroke-width="0.9"/>')
        if key:
            body, _, _ = notes(p, x0 - gap / 2, y + 70, 7.0, bw + gap, fill=ACCENT, timesig=False, staff=False)
            out.append(body)
    body = svg(540, len(WRITE) * row, "".join(out))
    how = ("Say the words and clap them. Write the rhythm under each beat: ta, ti-ti, rest or ta-a." if not key
           else f"Answer key for “Write the Rhythm” (page {page_index()['write']}). Stick notation is fine too.")
    return (f'<section class="page">{wm(watermark)}{top("Write the Rhythm · new phrases", "KEY" if key else "SHEET 3", "Answer key" if key else "Write it", ak=key)}'
            f'{"" if key else NAME}<div class="how" style="margin-top:{8 if key else 2}pt">{how}</div>'
            f'<div class="body">{body}</div>{foot(f"Page {page_no}")}</section>')


def _box_spans(phrase, x0, bw, gap):
    bx = x0
    for t in tokens(phrase):
        w = 2 * bw + gap if t.endswith("~") else bw
        yield t, (bx, bx + w)
        bx += w + gap


def compose_ws(page_no, watermark=False):
    out = []
    for i, (word, pic, n) in enumerate(WORD_BANK):
        x = (i % 4) * 135
        y = (i // 4) * 62
        out.append(f'<rect x="{x + 2}" y="{y + 2}" width="128" height="54" rx="8" fill="#fff" stroke="#000" stroke-width="1.3"/>')
        out.append(art(pic, x + 8, y + 9, 40, 1.3))
        out.append(text(x + 56, y + 27, word, 14, 600, "Source Sans 3", anchor="start"))
        out.append(text(x + 56, y + 45, "ta" if n == 1 else "ti-ti", 11, 400, "Source Sans 3", anchor="start", fill="#444"))
    y0 = 140
    bw, gap = 124, 6
    for r in range(3):
        y = y0 + r * 150
        out.append(text(0, y + 12, f"Rhythm {r + 1}", 13, 700, anchor="start"))
        out.append(text(80, y + 12, "words (one box = one beat)", 10, 300, anchor="start"))
        for b in range(4):
            out.append(f'<rect x="{10 + b * (bw + gap)}" y="{y + 20}" width="{bw}" height="38" rx="5" fill="#fff" stroke="#000" stroke-width="1.3"/>')
        out.append(text(80, y + 76, "rhythm", 10, 300, anchor="start"))
        for b in range(4):
            out.append(f'<rect x="{10 + b * (bw + gap)}" y="{y + 82}" width="{bw}" height="48" rx="5" fill="#fafafa" stroke="#000" stroke-width="1.3"/>')
            out.append(f'<line x1="{18 + b * (bw + gap)}" y1="{y + 120}" x2="{2 + bw + b * (bw + gap)}" y2="{y + 120}" stroke="#bbb" stroke-width="0.9"/>')
    body = svg(540, y0 + 3 * 150 - 10, "".join(out))
    return (f'<section class="page">{wm(watermark)}{top("Compose your own · word bank", "SHEET 4", "Create")}'
            f'{NAME}<div class="how" style="margin-top:2pt">Choose words from the bank (or your own) to fill 4 beats. '
            f'Write the rhythm under them. Then clap it for a partner and have them echo it back!</div>'
            f'<div class="body">{body}</div>{foot(f"Page {page_no}")}</section>')


def match_key_page(page_no, watermark=False):
    rows = []
    for pid, (phrase, p, _) in enumerate(MATCH):
        if pid in (0, 12):
            title = "Set 1 · ta and ti-ti" if pid == 0 else "Set 2 · rests and half notes"
            rows.append(f'<tr><th colspan="4">{title}</th></tr>')
        body, _, end = notes(p, 4, 15.5, 3.0, 24)
        rows.append(f'<tr><td style="text-align:center"><b>{pid + 1}</b></td><td>{escape(sentence(phrase))}</td>'
                    f'<td style="text-align:center;font-family:Oswald;font-weight:700;font-size:13pt;color:{ACCENT}">{LETTER_OF[pid]}</td>'
                    f'<td>{svg(int(end + 6), 21, body)}</td><td class="small">{" ".join(SYL[t] for t in p)}</td></tr>')
    return (f'<section class="page doc">{wm(watermark)}{top("Match game: word card number → rhythm card letter", "KEY", "Answer key", ak=True)}'
            f'<table style="margin-top:8pt;font-size:10pt" class="mk"><style>.mk td{{padding:1pt 6pt}}</style><tr><th>Word</th><th>Phrase</th><th>Rhythm</th><th>Notation</th><th>Syllables</th></tr>'
            f'{"".join(rows)}</table><div style="flex:1"></div>{foot(f"Page {page_no}")}</section>'
            ).replace('<th colspan="4">', '<th colspan="5" style="background:#fff;color:#000;border-left:0;border-right:0;font-size:11pt">')


# ---------------------------------------------------------------- plan and page index
def plan():
    p = [("cover",), ("teacher",), ("howto",), ("reference",)]
    p += [("words", 1), ("rhythms", 1), ("words", 2), ("rhythms", 2)]
    p += [("ws", 0), ("ws", 1), ("write",), ("compose",)]
    p += [("echo", k) for k in range(4)]
    p += [("key_match",), ("key_ws", 0), ("key_ws", 1), ("key_write",), ("terms",)]
    return p


def page_index():
    return {(item if len(item) > 1 else item[0]): i + 1 for i, item in enumerate(plan())}


def page_of(item):
    ix = page_index()
    return ix[item if len(item) > 1 else item[0]]


# ---------------------------------------------------------------- teacher pages
def teacher_page():
    ix = page_index()
    rows = [("How to use", ix["howto"], "games, echo ideas, tips"),
            ("Rhythm reference", ix["reference"], "ta, ti-ti, rest, ta-a with words"),
            ("Match cards, Set 1", f'{ix[("words", 1)]}–{ix[("rhythms", 1)]}', "12 word + 12 rhythm cards"),
            ("Match cards, Set 2", f'{ix[("words", 2)]}–{ix[("rhythms", 2)]}', "12 word + 12 rhythm cards"),
            ("Worksheets", f'{ix[("ws", 0)]}–{ix["compose"]}', "2 match, write, compose"),
            ("Echo cards (24)", f'{ix[("echo", 0)]}–{ix[("echo", 3)]}', "3 levels, 6 per page"),
            ("Answer keys", f'{ix["key_match"]}–{ix["key_write"]}', "match game and worksheets"),
            ("Terms of use", ix["terms"], "license and credits")]
    trs = "".join(f"<tr><td><b>{a}</b></td><td style='white-space:nowrap'>{b}</td><td>{c}</td></tr>" for a, b, c in rows)
    return (f'<section class="page doc"><div class="rule"><h1>Teacher Notes</h1>'
            f'<div class="l" style="font-size:13pt">{TITLE} + Echo Cards · grades 1–3 · ta, ti-ti, rest, ta-a</div></div>'
            f'<div class="cols"><div>'
            f'<h2>What it is</h2>'
            f'<p>Students say short Thanksgiving word phrases (“Pump-kin pie, pump-kin pie”), clap them, and match each one to its '
            f'rhythm in standard notation. Echo cards build the ear: you perform, the class echoes.</p>'
            f'<h2>How the words work</h2><ul>'
            f'<li>Every phrase is exactly <b>4 beats</b>, one box per beat.</li>'
            f'<li>One sound in a beat = <b>ta</b> (quarter note). Two sounds = <b>ti-ti</b> (two eighth notes).</li>'
            f'<li>“shh” = a <b>silent beat</b> (quarter rest).</li>'
            f'<li>An arrow = hold the word for <b>two beats</b> (half note, ta-a).</li>'
            f'<li>Stressed syllables fall on the beat, so the words sound natural when spoken.</li></ul>'
            f'<h2>Two levels</h2><ul>'
            f'<li><b>Set 1</b> (cards 1–12, A–L): ta and ti-ti only. Good for grade 1 and early grade 2.</li>'
            f'<li><b>Set 2</b> (cards 13–24, M–X): adds the quarter rest and half note. Grades 2–3.</li>'
            f'<li><b>Echo cards</b>: Level 1 ta/ti-ti (#1–8), Level 2 adds the rest (#9–16), Level 3 adds the half note (#17–24).</li></ul>'
            f'<h2>Getting ready</h2><ul>'
            f'<li>Print the card pages on card stock. Print each set’s word and rhythm pages on different colored paper if you like, '
            f'so the two piles stay apart.</li>'
            f'<li>Cut on the dashed lines. Laminate for years of use.</li></ul>'
            f'</div><div>'
            f'<h2>What’s inside</h2><table><tr><th>Part</th><th>Pages</th><th>Contents</th></tr>{trs}</table>'
            f'<h2>Syllables</h2>'
            f'<p>Cards use Kodály-style syllables (ta, ti-ti, ta-a) and “shh” for the rest. If your class uses another system '
            f'(Takadimi, Gordon, counting 1 &amp; 2 &amp;), say that instead; the notation is the same.</p>'
            f'<h2>Music notes</h2><p class="small">Every rhythm is one bar of 4/4 on a one-line rhythm staff, stems up, eighth notes '
            f'beamed in pairs, spaced one beat per slot. Half notes start on beat 1 or 3. Every match pattern is different, so each word card '
            f'has exactly one rhythm card.</p>'
            f'<h2>Standards</h2><p>Supports reading and performing rhythm patterns in iconic and standard notation '
            f'(National Core Arts Standards, Music, MU:Pr4.2, grades 1–3) and echoing rhythm patterns by ear.</p>'
            f'<p class="small">Harvest theme: turkey, pies, corn, apples, leaves, acorns and pumpkins. All words, rhythms and art are original. '
            f'No songs, lyrics or copyrighted characters are used.</p>'
            f'</div></div><div style="flex:1"></div>' + foot('Page ' + str(page_index()['teacher'])) + '</section>')


def howto_page():
    ix = page_index()
    deco = "".join(art(a, 20 + i * 66, 4, 50, 1.5) for i, a in enumerate(["turkey", "pie", "corn", "apple", "maple", "acorn", "pumpkin", "leaf"]))
    return (f'<section class="page doc"><div class="rule"><h1>How to Use</h1>'
            f'<div class="l" style="font-size:13pt">Say it · clap it · read it · echo it</div></div>'
            f'<div class="cols"><div>'
            f'<h2>Rhythm match games</h2><ul>'
            f'<li><b>Partner match</b>: lay out one set face up. Partners say and clap a word card, then find its rhythm card. '
            f'Check with the key (page {ix["key_match"]}).</li>'
            f'<li><b>Memory</b>: one set face down in a grid (24 cards). Turn over two; keep them if the words match the rhythm. '
            f'Students must clap the pair to keep it.</li>'
            f'<li><b>Find your partner</b>: give half the class word cards and half rhythm cards. Students walk, clap and say, '
            f'and pair up. Each pair performs for the class.</li>'
            f'<li><b>Pocket chart</b>: post the rhythm cards; draw a word card and the class decides together where it goes.</li>'
            f'<li><b>Around the room</b>: tape the rhythm cards to the walls; students carry a word card and hunt for its rhythm.</li></ul>'
            f'<h2>Worksheets</h2><ul>'
            f'<li><b>Match It! 1 and 2</b> (pages {ix[("ws", 0)]}–{ix[("ws", 1)]}): draw lines from words to rhythms.</li>'
            f'<li><b>Write the Rhythm</b> (page {ix["write"]}): six new phrases; students write the notes or stick notation.</li>'
            f'<li><b>Compose</b> (page {ix["compose"]}): open-ended; students build and perform their own 4-beat chant.</li></ul>'
            f'</div><div>'
            f'<h2>Echo cards</h2><ol>'
            f'<li>Keep a steady beat (pat, tap or a drum). Count in: “1, 2, ready, echo.”</li>'
            f'<li>Perform the card. The class echoes it right away, keeping the beat going.</li>'
            f'<li>Show the card and say the syllables together.</li></ol>'
            f'<h2>Echo ideas</h2><ul>'
            f'<li><b>Echo or not?</b> Perform the card correctly or with one beat changed; students thumbs-up or thumbs-down.</li>'
            f'<li><b>Which card?</b> Show three cards, perform one; students point to it.</li>'
            f'<li><b>Student leader</b>: a student draws a card and leads the echo.</li>'
            f'<li><b>Word swap</b>: put Thanksgiving words to the echo rhythm (ti-ti = tur-key, ta = pie).</li>'
            f'<li><b>Instruments</b>: echo on drums, rhythm sticks or one pitch on a xylophone.</li></ul>'
            f'<h2>Tips</h2><ul>'
            f'<li>Speak the words in rhythm with the beat before clapping.</li>'
            f'<li>In Set 2, show the rest as a quiet gesture (open hands) so students feel the silent beat.</li>'
            f'<li>Collect cards by set so the class sets stay together.</li></ul>'
            f'</div></div><div style="flex:1"></div>'
            f'<div style="display:flex;justify-content:center;margin-bottom:10pt">{svg(560, 58, deco)}</div>'
            + foot('Page ' + str(ix['howto'])) + '</section>')


REF = [("q", "quarter note", 1, "ta", "pie"), ("e", "two eighth notes", 1, "ti-ti", "tur- key"),
       ("r", "quarter rest", 1, "(silent)", "(shh)"), ("h", "half note", 2, "ta-a", "yum!~")]


def reference_page(watermark=False):
    rows = []
    for t, name, beats, syl, word in REF:
        s = 6.5
        W = 40
        body, _, end = notes(t, 6, 34, s, W, timesig=False, staff=False)
        std = svg(int(beats * W + 14), 46, f'<line x1="0" y1="34" x2="{beats * W + 12}" y2="34" stroke="#000" stroke-width="1.3"/>' + body,
                  'display:block;margin:0 auto')
        boxes = svg(int(beats * 64 + 4), 40, word_boxes(word, 1, 2, 60, 34, 4, 15), 'display:block;margin:0 auto')
        rows.append(f'<tr><td>{std}</td><td class="n"><span class="big">{name}</span></td>'
                    f'<td><b>{beats} beat{"s" if beats != 1 else ""}</b></td><td><b>{syl}</b></td><td>{boxes}</td></tr>')
    ex = MATCH[0]
    W = 100
    exb = word_boxes(ex[0], 46, 4, W - 6, 36, 6, 18)
    body, centres, end = notes(ex[1], 0, 108, 8, W)
    exsvg = svg(460, 124, exb + body)
    ex2 = SET2[2]
    exb2 = word_boxes(ex2[0], 46, 4, W - 6, 36, 6, 18)
    body2, _, _ = notes(ex2[1], 0, 108, 8, W)
    exsvg2 = svg(460, 124, exb2 + body2)
    return (f'<section class="page doc">{wm(watermark)}<div class="rule"><h1>Rhythm Reference</h1>'
            f'<div class="l" style="font-size:13pt">The 4 rhythm values in this set · display it or keep it on desks</div></div>'
            f'<table class="ref"><tr><th>Notation</th><th>Name</th><th>Beats</th><th>Say</th><th>Word example</th></tr>{"".join(rows)}</table>'
            f'<h2>Words into rhythm <span class="acc">·</span> one box is one beat</h2>'
            f'<div style="display:flex;justify-content:center;margin:4pt 0">{exsvg}</div>'
            f'<p style="text-align:center">“Pump-kin” has two sounds in one beat (ti-ti). “Pie” has one sound (ta). '
            f'ti-ti ta ti-ti ta = 4 beats.</p>'
            f'<div style="display:flex;justify-content:center;margin:8pt 0 4pt">{exsvg2}</div>'
            f'<p style="text-align:center">“Gob!” is held for two beats, so it is a half note (ta-a). ti-ti ti-ti ta-a = 4 beats.</p>'
            f'<ul style="margin-top:6pt"><li>Count the <b>sounds</b> in each beat box: 1 sound = ta, 2 sounds = ti-ti, no sound = rest.</li>'
            f'<li>Every card and echo pattern is <b>4 beats</b>, one bar of 4/4 time.</li></ul>'
            f'<div style="flex:1"></div>' + foot('Page ' + str(page_index()['reference'])) + '</section>')


def terms_page(page_no):
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
            f'<li>Art, word phrases, cards, layouts and rhythm patterns: original work, {BRAND} by {STORE}.</li>'
            f'<li>Music notation font: Bravura © Steinberg Media Technologies GmbH, SIL Open Font License 1.1.</li>'
            f'<li>Text fonts: Oswald (The Oswald Project Authors) and Source Sans 3 (Adobe), SIL Open Font License 1.1.</li></ul>'
            f'<p class="small">Designed with the help of digital and AI tools, and checked by hand.</p>'
            f'<div style="flex:1"></div>{foot(f"Page {page_no}")}</section>')


# ---------------------------------------------------------------- cover art
def hero_svg(width_css):
    """Cover art: a word card matched to its rhythm card, with harvest art; accent and black only."""
    A = ACCENT
    w, h = MC_W, MC_H
    wc = (f'<g transform="translate(150 26) rotate(-5 {w / 2} {h / 2}) scale(1.12)">{word_card(0, 0, 0)}</g>')
    k = ORDER.index(0)
    rc = (f'<g transform="translate(250 170) rotate(4 {w / 2} {h / 2}) scale(1.12)">{rhythm_card(k, 0, 0)}</g>')
    link = (f'<path d="M300,140 C300,160 330,170 350,190" fill="none" stroke="{A}" stroke-width="4" stroke-linecap="round" stroke-dasharray="0.1 10"/>'
            f'<circle cx="300" cy="138" r="7" fill="{A}" stroke="#000" stroke-width="1.6"/><circle cx="352" cy="192" r="7" fill="{A}" stroke="#000" stroke-width="1.6"/>')
    deco = (art("turkey", 8, 150, 150, 2.6, fill=A) + art("maple", 30, 10, 88, 2.4, fill=A, rotate=-14)
            + art("pie", 480, 12, 108, 2.4, fill=A) + art("acorn", 520, 130, 62, 2.2, rotate=12)
            + art("leaf", 470, 278, 70, 2.2, fill=A, rotate=30) + art("corn", 176, 280, 70, 2.2, rotate=-20))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 360" width="{width_css}" style="display:block">'
            f'{wc}{rc}{link}{deco}</svg>')


def cover_page():
    rg = len(plan())
    return (f'<section class="page cover"><div class="store">{BRAND}</div>'
            f'<div style="width:6.9in">{hero_svg("100%")}</div>'
            f'<div class="ctitle"><div class="a">THANKSGIVING</div><div class="b">RHYTHM MATCH</div>'
            f'<div class="c">+ Echo Cards · ta, ti-ti, rest &amp; half note · worksheets &amp; answer keys</div></div>'
            f'<div class="cband">Grades 1–3 <em>·</em> 48 match cards <em>·</em> 24 echo cards <em>·</em> {rg} pages</div></section>')


# ---------------------------------------------------------------- assemble
def render_page(item, watermark=False):
    n = page_of(item)
    k = item[0]
    if k == "cover":
        return cover_page()
    if k == "teacher":
        return teacher_page()
    if k == "howto":
        return howto_page()
    if k == "reference":
        return reference_page(watermark)
    if k in ("words", "rhythms"):
        return match_page(k, item[1], n, watermark)
    if k == "ws":
        return match_ws(item[1], n, watermark=watermark)
    if k == "write":
        return write_ws(n, watermark=watermark)
    if k == "compose":
        return compose_ws(n, watermark)
    if k == "echo":
        return echo_page(item[1], n, watermark)
    if k == "key_match":
        return match_key_page(n, watermark)
    if k == "key_ws":
        return match_ws(item[1], n, key=True, watermark=watermark)
    if k == "key_write":
        return write_ws(n, key=True, watermark=watermark)
    if k == "terms":
        return terms_page(n)
    raise KeyError(k)


PREVIEW_PICKS = [("words", 1), ("echo", 2), ("ws", 0), ("key_write",)]


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


def sq_doc(body):
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{font_css()}'
            f'html,body{{margin:0;background:#fff}}{SQ_CSS}</style></head><body>{FONT_PRIME}{body}</body></html>')


# SVG <text> alone doesn't make Chromium load a web font before the screenshot, so name every face once in HTML.
FONT_PRIME = ('<div style="position:absolute;left:-9999px;font-family:\'Source Sans 3\'">'
              '<span style="font-weight:400">a</span><span style="font-weight:600">a</span>'
              '<i style="font-weight:400">a</i><span style="font-family:Bravura">&#xE0A4;</span></div>')


def cover_square():
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div>'
        f'<div style="width:840px;margin-top:14px">{hero_svg("100%")}</div>'
        f'<div class="hd" style="font-size:66px;margin-top:6px">Thanksgiving</div>'
        f'<div class="hd" style="font-size:118px">Rhythm Match</div>'
        f'<div class="sub" style="font-size:29px;margin-top:10px">+ Echo Cards · ta, ti-ti, rest &amp; half note · answer keys</div>'
        f'<div class="band">Grades 1–3 <em>·</em> 48 match cards <em>·</em> 24 echo cards</div></div>')


def preview_square_1(img):
    items = [(img[0], "Word cards", "4 beats, one box per beat"), (img[1], "Rhythm cards", "letters mixed up"),
             (img[2], "Echo cards", "3 levels, 24 cards")]
    shots = "".join(
        f'<div style="width:300px"><div class="shot"><img src="{src}"><div class="swm" style="font-size:64px">PREVIEW</div></div>'
        f'<div class="lbl">{a}<span>{b}</span></div></div>' for src, a, b in items)
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div>'
        f'<div class="hd" style="font-size:76px;margin-top:20px">Match &amp; echo</div>'
        f'<div class="sub" style="font-size:27px;margin-top:8px">Word cards, rhythm cards, echo cards, worksheets and keys</div>'
        f'<div style="display:flex;gap:24px;margin-top:60px;align-items:flex-start">{shots}</div>'
        f'<div class="band">Say it <em>·</em> clap it <em>·</em> match it <em>·</em> echo it</div></div>')


def preview_square_2(a, b):
    pair = "".join(
        f'<div style="position:absolute;left:{x}px;top:{y}px;width:540px"><div class="shot"><img src="{src}">'
        f'<div class="swm" style="font-size:110px">PREVIEW</div></div>'
        f'<div class="lbl" style="position:absolute;{side}:-2px;top:-44px;margin:0">{lab}</div></div>'
        for src, lab, x, y, side in ((a, "Worksheet", 50, 250, "left"), (b, "Answer key", 410, 330, "right")))
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div>'
        f'<div class="hd" style="font-size:72px;margin-top:20px">Worksheets + keys</div>'
        f'<div class="sub" style="font-size:27px;margin-top:8px">Match it, write the rhythm, compose your own</div>'
        f'{pair}'
        f'<div class="band">Answer keys for every worksheet and the match game</div></div>')


def preview_square_3():
    rows = []
    picks = [0, 4, 13, 14]
    W = 76
    for pid in picks:
        phrase, p, pic = MATCH[pid]
        boxes = word_boxes(phrase, 70, 6, W - 6, 46, 6, 22)
        body, _, _ = notes(p, 450, 64, 9.2, W)
        rows.append(f'<svg viewBox="0 0 900 120" width="900" style="display:block">{art(pic, 2, 8, 60, 1.6)}{boxes}'
                    f'<path d="M392,30 L432,30 M424,22 L433,30 L424,38" fill="none" stroke="{ACCENT}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>'
                    f'{body}</svg>')
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div>'
        f'<div class="hd" style="font-size:70px;margin-top:16px">Words become rhythms</div>'
        f'<div class="sub" style="font-size:27px;margin-top:8px">Count the sounds in each beat: 1 = ta, 2 = ti-ti, shh = rest, hold = ta-a</div>'
        f'<div style="position:relative;display:flex;flex-direction:column;gap:26px;margin-top:44px">{"".join(rows)}'
        f'<div class="swm" style="font-size:150px">PREVIEW</div></div>'
        f'<div class="band">Original phrases <em>·</em> every pattern 4 beats in 4/4</div></div>')


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
        "grades": ["1st-grade", "2nd-grade", "3rd-grade"],
        "subjects": ["Music"],
        "tags": ["Thanksgiving", "Autumn"],
        "formats": ["PDF"],
        "pages": pages,
        "answer_key": "Included",
        "files": {"product": f"{SLUG}.pdf", "preview": f"{SLUG}-PREVIEW.pdf", "thumb1": "cover.png",
                  "thumb2": "preview-1.png", "thumb3": "preview-2.png", "thumb4": "preview-3.png"},
    }


def pdf_png(src, page, out, res=110):
    subprocess.run(["pdftoppm", "-png", "-r", str(res), "-f", str(page), "-l", str(page), "-singlefile", src,
                    os.path.join(BUILD, out)], check=True)


def build():
    os.makedirs(BUILD, exist_ok=True)
    problems = verify_data()
    if problems:
        print("\n".join(problems))
        sys.exit("data check failed; not rendering")
    full = write("resource.html", html_doc([render_page(p) for p in plan()], TITLE))
    prev = write("preview.html", html_doc(preview_pages(), "Preview"))
    render([{"html": full, "pdf": PDF}, {"html": prev, "pdf": PREVIEW_PDF}])
    res = 50 if LOW_RES else 110
    for name, item in (("words", ("words", 1)), ("rhythms", ("rhythms", 1)), ("echo", ("echo", 0)),
                       ("ws", ("ws", 0)), ("wskey", ("key_ws", 0))):
        pdf_png(PDF, page_of(item), name, res)
    sq = [write("cover.html", cover_square()), write("p1.html", preview_square_1(["words.png", "rhythms.png", "echo.png"])),
          write("p2.html", preview_square_2("ws.png", "wskey.png")), write("p3.html", preview_square_3())]
    render([{"html": h, "png": o, "width": 1000, "height": 1000, "scale": 1 if LOW_RES else 2}
            for h, o in zip(sq, [COVER_PNG] + PREVIEW_PNGS)])
    with open(TPT_JSON, "w") as f:
        json.dump(tpt_json(len(plan())), f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"built {PDF} ({len(plan())} pages), {PREVIEW_PDF}, cover + 3 previews, tpt.json" + (" [LOW RES]" if LOW_RES else ""))


# ---------------------------------------------------------------- checks
BEATS = {"q": 1, "e": 1, "r": 1, "h": 2}      # independent of R.TOKENS; the check compares the two
SOUNDS = {"q": 1, "e": 2, "r": 0, "h": 1}


def pattern_errors(label, p):
    errs = []
    if any(t not in BEATS for t in p):
        return [f"{label} {p}: unknown token"]
    if sum(BEATS[t] for t in p) != 4 or R.beats(p) != 4:
        errs.append(f"{label} {p}: not 4 beats")
    b = 0
    for t in p:
        if t == "h" and b not in (0, 2):
            errs.append(f"{label} {p}: half note starts on beat {b + 1} (must be 1 or 3)")
        b += BEATS[t]
    return errs


def verify_data():
    errs = []
    for t in BEATS:
        if R.TOKENS[t]["beats"] != BEATS[t] or R.TOKENS[t]["sounds"] != SOUNDS[t]:
            errs.append(f"token {t}: 002's table disagrees on beats/sounds")
    for i, (phrase, p, pic) in enumerate(MATCH, 1):
        errs += pattern_errors(f"match #{i}", p)
        if derive(phrase) != p:
            errs.append(f"match #{i} '{phrase}': words give {derive(phrase)}, card says {p}")
        sounds = sum(0 if t == "(shh)" else len(t.rstrip("~").split()) for t in tokens(phrase))
        if sounds != sum(SOUNDS[t] for t in p):
            errs.append(f"match #{i}: {sounds} syllables but {sum(SOUNDS[t] for t in p)} notes")
    pats = [p for _, p, _ in MATCH]
    if len(set(pats)) != len(pats):
        errs.append("two match cards share a rhythm (the match would be ambiguous)")
    if any(set(p) - set("qe") for _, p, _ in SET1):
        errs.append("Set 1 uses more than ta and ti-ti")
    if any(not set(p) & set("rh") for _, p, _ in SET2):
        errs.append("every Set 2 card needs a rest or half note")
    if sorted(ORDER[:12]) != list(range(12)) or sorted(ORDER[12:]) != list(range(12, 24)):
        errs.append("rhythm-card letters are not a per-set permutation")
    if any(ORDER[k] == k for k in range(24)):
        errs.append("a rhythm card's letter lines up with its word card number (A = 1 ...); reseed")
    for pid in range(24):
        k = LETTERS.index(LETTER_OF[pid])
        if MATCH[ORDER[k]][1] != MATCH[pid][1]:
            errs.append(f"key: word card {pid + 1} -> {LETTER_OF[pid]} is not its rhythm")
    for i, p in enumerate(ECHO_POOL, 1):
        errs += pattern_errors(f"echo #{i}", p)
    if len(set(ECHO_POOL)) != 24 or [len(ps) for _, _, ps in ECHO] != [8, 8, 8]:
        errs.append("echo cards: need 24 different patterns, 8 per level")
    if any(set(p) - set("qe") for p in ECHO[0][2]):
        errs.append("echo level 1 goes beyond ta/ti-ti")
    if any("r" not in p or "h" in p for p in ECHO[1][2]):
        errs.append("echo level 2: each card needs a rest and no half note")
    if any("h" not in p for p in ECHO[2][2]):
        errs.append("echo level 3: each card needs a half note")
    for n, (_, _, picks) in enumerate(WS):
        if len(picks) != 6 or len(set(picks)) != 6:
            errs.append(f"worksheet {n + 1}: needs 6 different phrases")
        if sorted(WS_ORDER[n]) != list(range(6)) or any(WS_ORDER[n][i] == i for i in range(6)):
            errs.append(f"worksheet {n + 1}: rhythm order must be a derangement")
    if any(set(MATCH[p][1]) - set("qe") for p in WS[0][2]) or any(not set(MATCH[p][1]) & set("rh") for p in WS[1][2]):
        errs.append("worksheet levels don't match their sets")
    for i, (phrase, p, _) in enumerate(WRITE, 1):
        errs += pattern_errors(f"write #{i}", p)
        if derive(phrase) != p:
            errs.append(f"write #{i} '{phrase}': words give {derive(phrase)}, key says {p}")
    for word, _, n in WORD_BANK:
        if len(word.split("-")) != n:
            errs.append(f"word bank '{word}': {n} sounds listed")
    words = " ".join(ph for ph, _, _ in MATCH + WRITE).lower()
    for bad in ("pilgrim", "indian", "native", "christmas", "santa"):
        if bad in words:
            errs.append(f"phrase mentions '{bad}'")
    # fits: every beat-box label has a measured width, and word-card text stays readable for grades 1-3
    labels = {box_text(t) for ph in [x[0] for x in MATCH + WRITE] + [r[4] for r in REF] for t in tokens(ph) if t != "(shh)"}
    if labels - set(WIDTH_EM):
        errs.append(f"labels without a measured width: {sorted(labels - set(WIDTH_EM))}")
    if card_font_min() < MIN_CARD_PT:
        errs.append(f"smallest word-card text is {card_font_min()}pt (< {MIN_CARD_PT}pt)")
    if notes_width(MC_S, MC_BEAT) > MC_W - 24:
        errs.append("rhythm card notation overflows")
    if notes_width(EC_S, EC_BEAT) > EC_W - 24:
        errs.append("echo card notation overflows")
    for name, cp in {"noteQuarterUp": 0xE1D5, "noteHalfUp": 0xE1D3, "restQuarter": 0xE4E5, "noteheadBlack": 0xE0A4,
                     "timeSig4": 0xE084}.items():
        if R.GLYPH[name][0] != cp:
            errs.append(f"{name} codepoint wrong")
    return errs


def pdf_fonts(path):
    out = subprocess.run(["pdffonts", path], capture_output=True, text=True, check=True).stdout.splitlines()[2:]
    return [(ln.split()[0], ln.split()[-5]) for ln in out]


def footer_errors(path, safe=0.35 * 72):
    out = subprocess.run(["pdftotext", "-bbox", path, "-"], capture_output=True, text=True, check=True).stdout
    errs = []
    for i, page in enumerate(re.findall(r'<page width="([\d.]+)" height="([\d.]+)">(.*?)</page>', out, re.S)):
        ph = float(page[1])
        ys = [float(m) for m in re.findall(r'yMax="([\d.]+)">Lotze', page[2])]
        if i == 0 and not ys:
            continue
        if not ys:
            errs.append(f"{os.path.basename(path)} p{i + 1}: footer not found on the page")
        elif max(ys) > ph - safe:
            errs.append(f"{os.path.basename(path)} p{i + 1}: footer ends {ph - max(ys):.1f}pt from the bottom edge (< {safe:.0f}pt)")
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
    for path, items in ((PDF, plan()), (PREVIEW_PDF, PREVIEW_PICKS)):
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
    rd = PdfReader(PDF)
    txt = [pg.extract_text().replace("\n", " ") for pg in rd.pages]
    for i, t in enumerate(txt):
        if i > 0 and "Brian Lotze · Hudson Beat" not in t:
            errs.append(f"page {i + 1}: footer missing")
    # the printed match key, read back from the PDF, must agree with the phrase-derived rhythms
    kt = txt[page_of(("key_match",)) - 1]
    pairs = {}
    for m in re.finditer(r"(?<![\w-])(\d{1,2}) ([^\d]+?) ([A-X]) ", kt):
        pairs.setdefault(int(m.group(1)), m.group(3))
    for pid in range(24):
        if pairs.get(pid + 1) != LETTER_OF[pid]:
            errs.append(f"match key page: word {pid + 1} -> {pairs.get(pid + 1)} (expected {LETTER_OF[pid]})")
            break
    for s in (1, 2):
        rt = txt[page_of(("rhythms", s)) - 1]
        for k in range(12 * (s - 1), 12 * s):
            if not re.search(rf"(?<![A-Za-z]){LETTERS[k]}(?![A-Za-z])", rt):
                errs.append(f"rhythm page set {s}: letter {LETTERS[k]} not found")
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
    m = re.search(r"^## 1\. Title\s*\n+```\n(.+?)\n```", up, re.M | re.S)
    if not m:
        errs.append("UPLOAD.md: title block not found")
    elif len(m.group(1).strip()) > 80:
        errs.append(f"UPLOAD.md: title is {len(m.group(1).strip())} chars (max 80)")
    m2 = re.search(r"^## 2\. Description\s*\n+```\n(.+?)\n```", up, re.M | re.S)
    if not m2 or "Designed with the help of digital and AI tools, and checked by hand." not in m2.group(1):
        errs.append("UPLOAD.md: description block missing the disclosure line")
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
    print(f"CHECK OK: 24 match phrases, rhythm derived from the words = card rhythm, all 4 beats, all different; "
          f"letters a per-set derangement and the printed key read back from the PDF agrees; 24 echo patterns (3 levels) 4 beats, "
          f"half notes on beat 1 or 3; worksheets 6 rows each with derangements, 6 write-it phrases checked; "
          f"PDF {len(plan())} Letter pages with footers, preview {len(PREVIEW_PICKS)} watermarked pages, fonts embedded; "
          f"images 2000x2000; tpt.json and UPLOAD.md ok.")


if __name__ == "__main__":
    if "--check" in sys.argv:
        check()
    else:
        build()
