#!/usr/bin/env python3
"""Band and Orchestra Emergency Sub Plans: 5 no-instrument lessons for grades 6-12 (TpT 041): build the resource and verify it.

    python3 gen.py            build everything (PDFs, PNGs, tpt.json) into this folder
    python3 gen.py --lowres   same, but square images at scale 1 (self-check only; --check rejects them)
    python3 gen.py --check    verify every answer key, rhythms, puzzles, pages, fonts and files

Five lessons a non-music substitute can run with no instruments and no audio, for band or orchestra
(grades 6-12): instrument families and care (reading + sort), rhythm and note-value math (engraved
rhythms), composers and music history (reading + comprehension), practice journal and rehearsal
reflection, and a seating and terminology puzzle (seating charts, matching, word search). Each has a
plan page (timing, script, materials), student pages and answer keys; plus a welcome sheet, lessons at a
glance, early finishers, a sub report, teacher notes and terms. Built from tpt/033's gen.py.

Accuracy is checked end to end: every engraved rhythm is drawn to SVG and read back (glyphs, beamed pairs,
beat slots, barlines) and must equal the data; every number in the rhythm-math keys is computed from the
data; the history timeline arithmetic is computed from the dates; the word search is placed by code and
solved by code (every word found exactly once); scrambles and sorts are computed; and the key text printed
in the PDF is compared with the data. Rendering uses Playwright + Chromium through ../tools/render.js.
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


R = _load("rhythm002", "002-fall-rhythm-flashcards/rhythm.py")

FONTS = os.path.join(TPT, "fonts")
BUILD = os.path.join(HERE, "build")
RENDER_JS = os.path.join(TPT, "tools", "render.js")

SLUG = "band-orchestra-emergency-sub-plans"
PDF = os.path.join(HERE, f"{SLUG}.pdf")
PREVIEW_PDF = os.path.join(HERE, f"{SLUG}-PREVIEW.pdf")
COVER_PNG = os.path.join(HERE, "cover.png")
PREVIEW_PNGS = [os.path.join(HERE, f"preview-{i}.png") for i in (1, 2, 3)]
UPLOAD = os.path.join(HERE, "UPLOAD.md")
TPT_JSON = os.path.join(HERE, "tpt.json")

STORE = "Brian Lotze"      # copyright holder
BRAND = "Hudson Beat"      # store line on covers and previews
YEAR = 2026
ACCENT = "#1F6F8B"         # this product's single accent (deep teal-blue)
TINT1, TINT2 = "#7DB0C4", "#C4DDE8"   # tints of the accent, allowed on cover art
TITLE = "Band & Orchestra Sub Plans"
PRICE = "7.00"
DISCLOSURE = "Created with the help of digital and AI tools. Notation and answer keys are verified before release."
LOW_RES = "--lowres" in sys.argv

BANNED = ("christmas", "xmas", "santa", "hanukkah", "chanukah", "kwanzaa", "halloween", "thanksgiving", "easter", "valentine",
          "youtube", "spotify", "checked by hand", "handmade", "classroom-tested", "classroom tested", "hand-checked")

BEATS = {"q": 1, "e": 1, "r": 1, "h": 2, "w": 4}
SOUNDS = {"q": 1, "e": 2, "r": 0, "h": 1, "w": 1}
SYL = {"q": "ta", "e": "ti-ti", "r": "shh", "h": "ta-a", "w": "ta-a-a-a"}
NAMES = {"q": "quarter note", "e": "two eighth notes", "r": "quarter rest", "h": "half note", "w": "whole note"}


def bars(p):
    return p.split("|")


def nbeats(bar):
    return sum(BEATS[t] for t in bar if t != "|")


# ---------------------------------------------------------------- notation drawing
BAR_W = 0.16          # thin barline, spaces


def glyph(cp, x, y, s, fill="#000"):
    return f'<text x="{x:.2f}" y="{y:.2f}" font-family="Bravura" font-size="{4 * s:.2f}" fill="{fill}">&#x{cp:X};</text>'


def tok_svg(t, cx, yl, s, W, fill="#000"):
    if t == "w":
        (x0, _), (x1, _) = R.GLYPH["noteWhole"][1], R.GLYPH["noteWhole"][2]
        return R.glyph("noteWhole", cx - (x0 + x1) / 2 * s, yl, s, fill)
    return R.engraved(t, cx, yl, s, pair_gap=min(2.4, W / s / 2), fill=fill)


def rhythm_svg(p, x0, yl, s, W, timesig=True, fill="#000", syl=False, syl_size=None, syl_fill=None, staff=True):
    """A rhythm (bars split by '|') on a one-line staff, beat-proportional. Returns (svg, right edge).
    Each token sits in its own beat slot (width W); the bar line follows each bar; the last one is a final barline."""
    out = []
    x = x0
    if timesig:
        out.append(R.glyph("timeSig4", x, yl - s, s, fill))
        out.append(R.glyph("timeSig4", x, yl + s, s, fill))
        x += 2.6 * s
    for bi, bar in enumerate(bars(p)):
        b = 0
        for t in bar:
            cx = x + (b + 0.5) * W
            out.append(tok_svg(t, cx, yl, s, W, fill))
            if syl:
                out.append(f'<text x="{cx:.2f}" y="{yl + 3.6 * s:.2f}" font-family="Oswald" font-weight="500" '
                           f'font-size="{syl_size or 1.9 * s:.2f}" text-anchor="middle" fill="{syl_fill or ACCENT}">{SYL[t]}</text>')
            b += BEATS[t]
        x += b * W + 0.6 * s
        last = bi == len(bars(p)) - 1
        out.append(f'<line class="bar" x1="{x:.2f}" y1="{yl - 2 * s:.2f}" x2="{x:.2f}" y2="{yl + 2 * s:.2f}" stroke="{fill}" '
                   f'stroke-width="{BAR_W * s:.2f}"/>')
        if last:
            out.append(f'<rect class="fin" x="{x + 0.6 * s:.2f}" y="{yl - 2 * s:.2f}" width="{0.5 * s:.2f}" height="{4 * s:.2f}" fill="{fill}"/>')
            x += 1.1 * s
        else:
            x += 0.6 * s
    if staff:
        out.insert(0, f'<line x1="{x0 - 0.4 * s:.2f}" y1="{yl:.2f}" x2="{x:.2f}" y2="{yl:.2f}" stroke="{fill}" '
                      f'stroke-width="{R.STAFF_W * s * 1.3:.2f}"/>')
    return "".join(out), x


def rhythm_width(p, s, W, timesig=True):
    return (2.6 * s if timesig else 0) + sum(nbeats(b) * W + 1.2 * s for b in bars(p)) + 0.5 * s


# ---------------------------------------------------------------- the accuracy check (reads the drawn SVG back)
CP = {0xE1D5: "q", 0xE1D3: "h", 0xE1D2: "w", 0xE4E5: "r"}


def read_rhythm(svgtxt, s, W, x0, timesig=True):
    """Parse a rhythm drawn by rhythm_svg back into a token string, using only the drawn glyphs and lines."""
    errs = []
    items = []
    for x, y, cp in re.findall(r'<text x="([-\d.]+)" y="([-\d.]+)" font-family="Bravura" font-size="[\d.]+" fill="[^"]+">&#x([0-9A-F]+);</text>', svgtxt):
        items.append((float(x), int(cp, 16)))
    ts = [i for i in items if i[1] == 0xE084]
    if timesig and len(ts) != 2:
        errs.append(f"time signature: {len(ts)} '4' glyphs")
    heads = sorted(x for x, cp in items if cp == 0xE0A4)
    beams = [(float(a), float(w)) for a, w in re.findall(r'<rect x="([-\d.]+)" y="[-\d.]+" width="([\d.]+)" height="' + f"{R.BEAM_T * s:.2f}" + r'"', svgtxt)]
    toks = []
    for x, cp in items:
        if cp in CP:
            (bx0, _), (bx1, _) = R.GLYPH[{"q": "noteQuarterUp", "h": "noteHalfUp", "w": "noteWhole", "r": "restQuarter"}[CP[cp]]][1:]
            cx = x + (bx1 + bx0) / 2 * s if CP[cp] in "wr" else x + R.HEAD_W / 2 * s
            toks.append((cx, CP[cp]))
        elif cp not in (0xE084, 0xE0A4):
            errs.append(f"unexpected glyph U+{cp:X}")
    if len(heads) % 2:
        errs.append("an unpaired eighth notehead")
    for i in range(0, len(heads) - 1, 2):
        a, b = heads[i], heads[i + 1]
        if not any(bx <= a + R.HEAD_W * s and bx + bw >= b for bx, bw in beams):
            errs.append("eighth pair without a beam")
        toks.append(((a + b) / 2 + R.HEAD_W / 2 * s, "e"))
    bl = sorted(float(x) for x in re.findall(r'<line class="bar" x1="([-\d.]+)"', svgtxt))
    if len(re.findall(r'class="fin"', svgtxt)) != 1:
        errs.append("final barline missing")
    toks.sort()
    out, start, bar_i = "", x0 + (2.6 * s if timesig else 0), 0
    beat = 0
    for cx, t in toks:
        while bar_i < len(bl) and cx > bl[bar_i]:
            out += "|"
            start = bl[bar_i] + 0.6 * s
            bar_i += 1
            beat = 0
        pos = (cx - start) / W - 0.5
        if abs(pos - beat) > 0.02:
            errs.append(f"{t} drawn at beat {pos + 1:.2f} of its bar, should be beat {beat + 1}")
        beat += BEATS[t]
        out += t
    if bar_i != len(bl) - 1:
        errs.append(f"{len(bl)} barlines for {out.count('|') + 1} bars")
    return out, errs


def rhythm_check(label, p, s=6, W=24, timesig=True, four=True):
    st, _ = rhythm_svg(p, 10, 40, s, W, timesig=timesig)
    got, errs = read_rhythm(st, s, W, 10, timesig)
    errs = [f"{label}: {e}" for e in errs]
    if got != p:
        errs.append(f"{label}: drawn rhythm reads back as {got}, data says {p}")
    if four:
        for b in bars(p):
            if nbeats(b) != 4:
                errs.append(f"{label}: bar {b} has {nbeats(b)} beats, not 4")
    return errs


# ---------------------------------------------------------------- html scaffolding (from 006)
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
.how { font-size: 11.5pt; margin: 7pt 0 6pt; }
.main { flex: 1; display: flex; flex-direction: column; min-height: 0; }
.foot { display: flex; justify-content: space-between; font-size: 8.5pt; color: #333; border-top: .8pt solid #000; padding-top: 3pt; }
.wm { position: absolute; left: 50%; top: 50%; transform: translate(-50%, -50%) rotate(-38deg); font-family: 'Oswald'; font-weight: 700;
      font-size: 150pt; color: rgba(0,0,0,.13); letter-spacing: .06em; white-space: nowrap; pointer-events: none; z-index: 9; }
.doc h1 { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 30pt; margin: 0 0 4pt; line-height: 1; }
.doc h2, .sec { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 13.5pt; margin: 10pt 0 4pt; letter-spacing: .02em; }
.doc h2 .acc, .sec .acc { color: ACCENT; }
.doc p, .doc li { font-size: 10.6pt; line-height: 1.32; margin: 0 0 4pt; }
.doc ul, .doc ol { margin: 0 0 4pt; padding-left: 15pt; }
.tn p, .tn li { font-size: 10pt !important; line-height: 1.28 !important; margin-bottom: 3pt !important; }
.tn h2 { margin: 8pt 0 3pt !important; font-size: 12.5pt !important; }
.tn table.t { font-size: 9pt; }
.tn table.t td { padding: 2pt 4pt; }
.doc .rule { border-bottom: 2.2pt solid #000; margin-bottom: 6pt; padding-bottom: 6pt; }
table.t { border-collapse: collapse; width: 100%; font-size: 10pt; margin: 2pt 0 4pt; }
table.t td, table.t th { border: 1pt solid #000; padding: 2.6pt 5pt; text-align: left; vertical-align: middle; }
table.t th { font-family: 'Oswald'; font-weight: 500; text-transform: uppercase; font-size: 9.5pt; background: #000; color: #fff; letter-spacing: .04em; }
.cols { display: flex; gap: 22pt; }
.cols > div { flex: 1; min-width: 0; }
.small { font-size: 9pt !important; color: #333; }
.box { border: 1.4pt solid #000; border-radius: 8pt; padding: 7pt 10pt; }
.part { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 13pt; letter-spacing: .03em; margin: 9pt 0 4pt; }
.part .acc { color: ACCENT; }
.part small { font-family: 'Source Sans 3'; font-weight: 400; text-transform: none; font-size: 11pt; letter-spacing: 0; margin-left: 6pt; }
.fl { display: flex; align-items: flex-end; gap: 6pt; font-size: 10.5pt; margin: 0 0 7pt; }
.fl b { font-weight: 600; white-space: nowrap; }
.fl span { flex: 1; border-bottom: 1pt solid #000; height: 14pt; }
.ln2 { border-bottom: 1pt solid #000; height: 22pt; }
.ans { font-family: 'Oswald'; font-weight: 700; color: ACCENT; }
.circ { display: inline-block; font-family: 'Oswald'; font-weight: 500; letter-spacing: .05em; padding: 0 7pt; border: 1.3pt solid transparent; border-radius: 10pt; }
.circ.on { border-color: ACCENT; color: ACCENT; font-weight: 700; }
.steps { list-style: none; padding: 0; margin: 4pt 0 0; }
.steps li { display: flex; gap: 10pt; margin: 0 0 11pt; font-size: 12pt; line-height: 1.36; }
.steps .tm { flex: 0 0 46pt; text-align: center; }
.steps .tm b { display: block; background: #000; color: #fff; font-family: 'Oswald'; font-weight: 700; font-size: 11pt; border-radius: 4pt; padding: 2pt 0 3pt; }
.steps .tm span { display: block; font-family: 'Oswald'; font-weight: 300; font-size: 9.5pt; margin-top: 2pt; }
.steps .tx b.hd { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 13pt; letter-spacing: .02em; }
.say { font-style: italic; }
.meta { display: flex; gap: 10pt; margin: 8pt 0 2pt; }
.meta > div { flex: 1; border: 1.3pt solid #000; border-radius: 7pt; padding: 6pt 9pt; font-size: 11pt; line-height: 1.3; }
.meta b.k { display: block; font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 10pt; letter-spacing: .05em; color: ACCENT; }
.cover { align-items: center; justify-content: space-between; padding: 0.55in 0.6in 0.5in; }
.store { font-family: 'Oswald'; font-weight: 500; font-size: 13pt; letter-spacing: .32em; text-transform: uppercase; }
.ctitle { text-align: center; }
.ctitle .a { font-family: 'Oswald'; font-weight: 700; font-size: 44pt; line-height: 1; letter-spacing: .02em; }
.ctitle .b { white-space: nowrap; font-family: 'Oswald'; font-weight: 700; font-size: 64pt; line-height: .95; letter-spacing: .01em; }
.ctitle .c { font-family: 'Oswald'; font-weight: 300; font-size: 16pt; margin-top: 8pt; }
.cband { width: 100%; background: #000; color: #fff; text-align: center; font-family: 'Oswald'; font-weight: 500; font-size: 14pt;
         letter-spacing: .08em; text-transform: uppercase; padding: 8pt 0 9pt; border-radius: 4pt; }
.cband em { font-style: normal; color: ACCENT; }
.kg { display: grid; gap: 2pt 10pt; font-size: 10.5pt; }
.kc { white-space: nowrap; border-bottom: .6pt solid #ccc; padding: 1pt 0; }
.kl { font-family: 'Oswald'; font-weight: 500; letter-spacing: .03em; }
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


def text(x, y, s, size, weight=700, family="Oswald", anchor="middle", fill="#000", extra=""):
    family = f"'{family}'" if " " in family else family
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{family}" font-weight="{weight}" font-size="{size}" '
            f'text-anchor="{anchor}" fill="{fill}" {extra}>{escape(s)}</text>')


def page(sub, tag, tagsub, inner, n, watermark=False, name=False, ak=False, right=None, title=TITLE):
    r = f"Page {n}" if right is None else f"{right} · Page {n}"
    return (f'<section class="page">{wm(watermark)}{top(sub, tag, tagsub, ak=ak, title=title)}{NAME if name else ""}'
            f'<div class="main">{inner}</div>{foot(r)}</section>')


def fl(label, extra=""):
    return f'<div class="fl" {extra}><b>{label}</b><span></span></div>'


def circ(word, on=False):
    return f'<span class="circ{" on" if on else ""}">{word}</span>'


def checkbox(size=11, ticked=False):
    tick = (f'<path d="M{size * .2:.1f} {size * .52:.1f} L{size * .42:.1f} {size * .75:.1f} L{size * .82:.1f} {size * .25:.1f}" '
            f'fill="none" stroke="{ACCENT}" stroke-width="{size * .14:.1f}" stroke-linecap="round" stroke-linejoin="round"/>' if ticked else "")
    return (f'<svg width="{size}pt" height="{size}pt" viewBox="0 0 {size} {size}" style="display:inline-block;vertical-align:-2pt">'
            f'<rect x=".7" y=".7" width="{size - 1.4}" height="{size - 1.4}" rx="2" fill="#fff" stroke="#000" stroke-width="1.2"/>{tick}</svg>')




# ================================================================ CONTENT DATA (every answer below is computed or checked by --check)
def lbl(i):
    return "ABCDEFGHIJKLMNOP"[i]


# ---- Lesson 1: instrument families and care
FAMILIES = {
    "Woodwinds": ["flute", "clarinet", "oboe", "bassoon", "saxophone"],
    "Brass": ["trumpet", "trombone", "French horn", "tuba"],
    "Percussion": ["snare drum", "timpani", "xylophone", "cymbals"],
    "Strings": ["violin", "viola", "cello", "double bass"],
}
SORT_BANK = ["cello", "trumpet", "snare drum", "clarinet", "French horn", "violin", "flute", "timpani", "trombone", "oboe",
             "double bass", "xylophone", "tuba", "saxophone", "viola", "cymbals", "bassoon"]
FAMILY_OF = {inst: fam for fam, lst in FAMILIES.items() for inst in lst}

SOUND_MATCH = [  # (instrument, how its sound starts)
    ("flute", "Air is blown across an edge (no reed)"),
    ("clarinet", "A single reed vibrates"),
    ("oboe", "Two reeds vibrate against each other"),
    ("trumpet", "The player’s lips buzz in a cup-shaped mouthpiece"),
    ("violin", "A bow or a finger sets the strings vibrating"),
    ("snare drum", "A stick strikes the drumhead"),
]
SOUND_ORDER = [3, 0, 5, 1, 4, 2]     # shuffled order in which the statements are printed (index into SOUND_MATCH)

CARE_TF = [
    ("When you are not playing, your instrument belongs in its case, with the latches closed.", True),
    ("It is fine to share a mouthpiece with a friend for a minute.", False),
    ("Rosin goes on the bow hair, not on the strings.", True),
    ("Touching the bow hair with your fingers is a good way to keep it clean.", False),
    ("A hot car is a safe place to leave an instrument for an afternoon.", False),
    ("After playing a woodwind, you should swab out the moisture with a cleaning cloth or swab.", True),
]

N_L1_MC = 2  # reading-check questions on the page 7 worksheet; the key prints exactly this many
L1_MC = [  # (question, options, correct index)
    ("Instruments are grouped into families by...", ["their color", "how they make sound", "how much they cost", "who invented them"], 1),
    ("A saxophone is a woodwind, even though it is made of brass, because it...", ["is very quiet", "uses a reed", "has a slide", "is played with sticks"], 1),
    ("Brass players start the sound by...", ["blowing across an edge", "buzzing their lips", "bowing a string", "striking a bar"], 1),
    ("Which family has the largest section in an orchestra?", ["Strings", "Brass", "Percussion", "Woodwinds"], 0),
    ("Timpani are different from a snare drum because timpani...", ["are made of brass", "use reeds", "can be tuned to different pitches", "are played with a bow"], 2),
]

# ---- Lesson 2: rhythm and note-value math
L2_ADD = ["hqq", "wr", "eeh", "qre", "hhq", "wqh"]
L2_SHORT = ["qq", "hq", "qeq", "h", "q", "qrq"]
L2_CMP = [("hh", "w"), ("qqq", "h"), ("eq", "h"), ("w", "qqq"), ("qr", "w"), ("hq", "qqq")]
L2_CIRCLE = ["hqq", "hq", "qeeq", "qqq", "wq", "eqrq", "ehq", "hrq"]
L2_SIGS = [(3, 4), (2, 4), (2, 2), (4, 4)]


def sig_note(bottom):
    return {1: "whole note", 2: "half note", 4: "quarter note", 8: "eighth note"}[bottom]


def sig_beats_value(bottom):
    return {1: 4, 2: 2, 4: 1}[bottom]


def cmp_sym(a, b):
    x, y = nbeats(a), nbeats(b)
    return "=" if x == y else (">" if x > y else "<")


def secs_per_beat(bpm):
    return 60 / bpm


L2_WORDS = [  # (question, answer text)  all computed
    ("A piece in 4/4 has 32 measures. How many beats is that?", str(32 * 4)),
    ("At 60 beats per minute, how many seconds does one beat last?", f"{secs_per_beat(60):g}"),
    ("At 60 beats per minute, how many seconds does a whole note (4 beats) last?", f"{4 * secs_per_beat(60):g}"),
    ("At 120 beats per minute, how many beats happen in 30 seconds?", str(int(120 * 30 / 60))),
    ("A march has 48 measures in 4/4 at 120 beats per minute. How many seconds does it last?", str(int(48 * 4 / 120 * 60))),
]

# ---- Lesson 3: composers
COMP = {  # name: (born, died)
    "Bach": (1685, 1750), "Mozart": (1756, 1791), "Beethoven": (1770, 1827), "Sousa": (1854, 1932),
}
SYM9 = 1824          # first performance of Beethoven's Symphony No. 9, Vienna
STARS = 1896         # "The Stars and Stripes Forever"
L3_MC = [
    ("Which composer is called “The March King”?", ["Bach", "Mozart", "Beethoven", "Sousa"], 3),
    ("Which composer wrote music as a child and toured Europe as a young performer?", ["Bach", "Mozart", "Sousa", "Beethoven"], 1),
    ("Which composer kept writing music as his hearing got worse?", ["Beethoven", "Sousa", "Bach", "Mozart"], 0),
    ("Bach’s music comes from which era?", ["Romantic", "Baroque", "Classical", "Modern"], 1),
    ("The sousaphone is named after...", ["a town in Germany", "an Italian word", "John Philip Sousa", "Mozart’s father"], 2),
]
L3_MATCH = [  # clue, composer
    ("Wrote six Brandenburg Concertos", "Bach"),
    ("Wrote more than 600 works and died at age 35", "Mozart"),
    ("Wrote nine symphonies; the last ends with a chorus", "Beethoven"),
    ("Led the U.S. Marine Band from 1880 to 1892", "Sousa"),
]
L3_MATCH_ORDER = [2, 0, 3, 1]
L3_MATH = [  # (question, answer int)
    ("How many years after Bach was born was Mozart born?", COMP["Mozart"][0] - COMP["Bach"][0]),
    ("How many years after Bach died was Mozart born?", COMP["Mozart"][0] - COMP["Bach"][1]),
    ("How many years after Mozart was born was Beethoven born?", COMP["Beethoven"][0] - COMP["Mozart"][0]),
    ("How many years passed from Beethoven’s Ninth Symphony (1824) to “The Stars and Stripes Forever” (1896)?", STARS - SYM9),
    ("Mozart died in 1791 at age 35. In what year was he born?", 1791 - 35),
]
L3_ORDER = ["Mozart", "Sousa", "Bach", "Beethoven"]     # scrambled; students order by birth year
L3_ORDER_ANS = sorted(L3_ORDER, key=lambda n: COMP[n][0])

# ---- Lesson 4: practice and rehearsal
STRAT = [  # (problem, strategy)
    ("The same hard spot goes wrong every time I play.", "Pull out the hard spot and repeat it slowly until it is right"),
    ("I speed up whenever the notes get fast.", "Practice with a metronome or a steady foot tap"),
    ("I can play the first line, but I fall apart when I try the full page.", "Break the piece into short chunks and work one at a time"),
    ("I forget where I made mistakes.", "Circle trouble spots in pencil so you can find them next time"),
    ("My practice time feels random and goes nowhere.", "Set one clear goal before you start"),
]
STRAT_ORDER = [3, 0, 4, 2, 1]
JOURNAL = [("Mon", 15, "long tones, scales"), ("Tue", 20, "new etude"), ("Wed", 0, "—"), ("Thu", 20, "hard measures, slow"),
           ("Fri", 15, "etude with metronome"), ("Sat", 25, "all my music"), ("Sun", 10, "just for fun")]
JOURNAL_GOAL = 100
RATING_ITEMS = ["I arrived with my instrument, music and a pencil.", "I counted my rests and came in on time.",
                "I watched the conductor.", "I listened to the players around me.",
                "I marked my music when the director gave a correction.", "I stayed focused for the whole rehearsal."]

# ---- Lesson 5: seating and terms
BAND_ZONES = [("1", "Woodwinds", "front rows"), ("2", "Brass", "behind the woodwinds"), ("3", "Percussion", "at the back")]
ORCH_ZONES = [("1", "First violins"), ("2", "Second violins"), ("3", "Violas"), ("4", "Cellos"),
              ("5", "Double basses"), ("6", "Woodwinds"), ("7", "Brass"), ("8", "Percussion")]
ZONE_BANK_BAND = ["Brass", "Percussion", "Woodwinds"]
ZONE_BANK_ORCH = ["Violas", "Percussion", "Cellos", "First violins", "Brass", "Double basses", "Woodwinds", "Second violins"]
CLOZE = [  # sentence with a blank, answer
    ("The ______ keeps the beat, gives cues and shapes the music.", "conductor"),
    ("A group of the same kind of instrument, such as all the clarinets, is a ______.", "section"),
    ("The leader of the first violins in an orchestra is the ______.", "concertmaster"),
    ("The player in the leader’s seat of a section sits in ______ chair.", "first"),
]
CLOZE_BANK = ["section", "first", "conductor", "concertmaster"]
TERMS = [  # (term, meaning)
    ("allegro", "fast and lively"), ("adagio", "slow"), ("forte", "loud"), ("piano", "soft"),
    ("crescendo", "gradually getting louder"), ("diminuendo", "gradually getting softer"),
    ("staccato", "short and separated"), ("legato", "smooth and connected"),
    ("fermata", "hold the note longer than its written value"), ("ritardando", "gradually slow down"),
]
TERM_ORDER = [5, 2, 8, 0, 9, 3, 6, 1, 7, 4]
DYNAMICS = [("pp", "pianissimo", "very soft"), ("p", "piano", "soft"), ("mp", "mezzo piano", "medium soft"),
            ("mf", "mezzo forte", "medium loud"), ("f", "forte", "loud"), ("ff", "fortissimo", "very loud")]
DYN_SCRAMBLED = ["mf", "pp", "ff", "p", "f", "mp"]
SEARCH_WORDS = ["ALLEGRO", "ADAGIO", "FORTE", "LEGATO", "STACCATO", "FERMATA", "CRESCENDO", "TEMPO", "CONDUCTOR", "SECTION",
                "UNISON", "RITARDANDO"]
GRID_N = 14

# ---- Early finishers
SCRAMBLE_WORDS = ["CLARINET", "TRUMPET", "TIMPANI", "TROMBONE", "BASSOON", "VIOLA"]
RIDDLES = [
    ("I am the largest and lowest-sounding of the string instruments in an orchestra.", "double bass"),
    ("I am a brass instrument with a slide instead of valves.", "trombone"),
    ("I am a drum that can be tuned to different pitches.", "timpani"),
    ("I am the smallest, highest-sounding string instrument in an orchestra.", "violin"),
    ("I am a woodwind with a single reed and I am made of brass.", "saxophone"),
]


def scramble(word, seed):
    rnd = random.Random(seed)
    letters = list(word)
    for _ in range(50):
        rnd.shuffle(letters)
        if "".join(letters) != word:
            break
    return "".join(letters)


SCRAMBLES = [(scramble(w, 100 + i), w) for i, w in enumerate(SCRAMBLE_WORDS)]


# ---- word search (placed by code; solved by code in --check)
DIRS = [(0, 1), (1, 0), (1, 1), (0, -1), (-1, 0), (-1, -1), (1, -1), (-1, 1)]


def find_all(grid, word):
    n = len(grid)
    hits = []
    for r in range(n):
        for c in range(n):
            for dr, dc in DIRS:
                cells = [(r + dr * k, c + dc * k) for k in range(len(word))]
                if all(0 <= rr < n and 0 <= cc < n for rr, cc in cells) and all(grid[rr][cc] == ch for (rr, cc), ch in zip(cells, word)):
                    hits.append(cells)
    return hits


def make_search():
    for seed in range(1, 400):
        rnd = random.Random(seed)
        g = [[""] * GRID_N for _ in range(GRID_N)]
        ok = True
        allowed = [(0, 1), (1, 0), (1, 1), (0, -1), (-1, 0), (1, -1)]
        for w in sorted(SEARCH_WORDS, key=len, reverse=True):
            for _ in range(500):
                dr, dc = rnd.choice(allowed)
                r, c = rnd.randrange(GRID_N), rnd.randrange(GRID_N)
                cells = [(r + dr * k, c + dc * k) for k in range(len(w))]
                if all(0 <= rr < GRID_N and 0 <= cc < GRID_N and g[rr][cc] in ("", ch) for (rr, cc), ch in zip(cells, w)):
                    for (rr, cc), ch in zip(cells, w):
                        g[rr][cc] = ch
                    break
            else:
                ok = False
                break
        if not ok:
            continue
        for r in range(GRID_N):
            for c in range(GRID_N):
                if not g[r][c]:
                    g[r][c] = rnd.choice("ABCDEFGHIKLMNOPRSTUVWY")
        if all(len(find_all(g, w)) == 1 for w in SEARCH_WORDS):
            return g
    raise SystemExit("could not build a word search")


SEARCH = make_search()
SEARCH_SOL = {w: find_all(SEARCH, w)[0] for w in SEARCH_WORDS}


# ================================================================ PLAN AND PAGE INDEX
PLAN = ["cover", "teacher", "welcome", "glance",
        "l1_plan", "l1_read", "l1_work", "l2_plan", "l2_a", "l2_b", "l2_c", "l3_plan", "l3_read", "l3_work",
        "l4_plan", "l4_read", "l4_journal", "l4_reflect", "l5_plan", "l5_seat", "l5_terms", "l5_search",
        "early", "key1", "key2", "key3", "key4", "report", "terms"]
IX = {k: i + 1 for i, k in enumerate(PLAN)}


def pg(k):
    return f"page {IX[k]}"


def fill_pages(s):
    return re.sub(r"PG:(\w+)", lambda m: pg(m.group(1)), s)


SAY_OPEN = ("Good morning, musicians! I’m your guest teacher today. Your director left a plan, and today is a no-instruments day, "
            "so please leave your instruments in their cases or in storage.")

LESSONS = [
    {"n": 1, "title": "Instrument Families and Care", "skill": "Instrument families, how sound is made, and caring for your instrument",
     "goal": "Students read about the four instrument families, sort instruments into them and learn the basic rules for caring for an instrument.",
     "materials": "Pencils and the reading and worksheet (PG:l1_read, PG:l1_work). No instruments, no audio, no screens.",
     "short": "Do steps 1, 3 and 4, and send the worksheet home to finish.",
     "extra": "Play Name That Family (PG:glance) or hand out the early finishers page (PG:early).",
     "steps": [
         ("5", "Welcome", f"Say: <span class=say>“{SAY_OPEN}”</span> Take attendance the way the welcome sheet (PG:welcome) says. Hand out pencils."),
         ("5", "Warm-up question", "Write on the board: <b>Which instrument do you play, and is it a woodwind, brass, percussion or string instrument?</b> "
                                   "Take four or five answers. It is fine if they are not sure; that is what today is for."),
         ("15", "Read together", "Hand out the reading (PG:l1_read). Students read one family at a time, one volunteer per paragraph. "
                                 "After each family ask: <i>What do players of this family do to start the sound?</i> The care rules at the bottom are read by the whole class."),
         ("12", "Worksheet", "Hand out the worksheet (PG:l1_work). Students work alone; they may look back at the reading. Walk around and point students to the reading, not to the answer. "
                             "The answers are on PG:key1."),
         ("5", "Check and share", "Read the answers aloud from PG:key1 and have students check their own work in a different color. "
                                  "Last, ask pairs to share one care rule they will follow this week.")]},
    {"n": 2, "title": "Rhythm and Note-Value Math", "skill": "Note values, time signatures and beats as math",
     "goal": "Students add note values, find missing beats and compare rhythms in 4/4, and use beats per minute to work out time.",
     "materials": "Pencils and the three worksheets (PG:l2_a, PG:l2_b, PG:l2_c). Students may clap on their desks or knees; no instruments.",
     "short": "Do steps 1 to 3 with the first worksheet only.",
     "extra": "Students write their own 4-beat rhythms in part G of the last worksheet, or use the early finishers page (PG:early).",
     "steps": [
         ("5", "Clap a steady beat", "Say: <span class=say>“Music is math you can hear. Pat your knees in a slow, steady beat with me: 1, 2, 3, 4.”</span> "
                                    "Count four steady beats aloud, then ask the class to clap on 1 only and rest on 2, 3 and 4. Repeat twice."),
         ("8", "Learn the note values", "Hand out the first worksheet (PG:l2_a) and read the box at the top aloud. Say: <span class=say>“A whole note lasts four beats. A half note lasts two. "
                                        "A quarter note lasts one. Two eighth notes joined by a beam together last one beat.”</span> Clap each one: a whole note is one clap, then wait four beats."),
         ("15", "Worksheet A", "Students complete the first worksheet alone. Remind them: in 4/4 every full measure adds up to 4 beats. Rests count too, even though they are silent."),
         ("10", "Worksheets B and C", "Hand out the next two worksheets (PG:l2_b, PG:l2_c). Part C on the first looks like a puzzle: compare what is on each side, just as in math. Parts F and G on the last are a good stretch for fast finishers."),
         ("5", "Check", "Read the answers from PG:key2. Students check each other’s papers. Ask: <i>Which question was the trickiest?</i>")]},
    {"n": 3, "title": "Composers and Music History", "skill": "A reading about four composers, with comprehension questions",
     "goal": "Students read about Bach, Mozart, Beethoven and Sousa, answer comprehension questions and use the dates to do timeline math.",
     "materials": "Pencils and the reading and questions (PG:l3_read, PG:l3_work). No audio needed.",
     "short": "Do steps 1 to 3 and skip the timeline math.",
     "extra": "Students write three sentences about the composer they would most like to meet, or use the early finishers page (PG:early).",
     "steps": [
         ("5", "Welcome and hook", f"Say: <span class=say>“{SAY_OPEN}”</span> Then ask: <b>Name a composer. What do you know about them?</b> Write answers on the board."),
         ("15", "Read together", "Hand out the reading (PG:l3_read). Four volunteers each read one composer. After each one, ask the class for one thing they learned. "
                                 "Draw a line on the board from 1685 to 1932 and mark each composer’s birth year as it is read."),
         ("15", "Questions", "Hand out the questions (PG:l3_work). Students may use the reading. Parts A and B are multiple choice and matching; part C is timeline math."),
         ("5", "Check", "Read the answers from PG:key3 and have students check their own papers."),
         ("5", "Discuss", "Ask: <i>Why might a composer from 300 years ago still matter to a band or orchestra today?</i> Take two or three answers.")]},
    {"n": 4, "title": "Practice Journal & Reflection", "skill": "Practice strategies, goal setting and honest reflection",
     "goal": "Students learn five practice strategies, track a week of practice and reflect on how they act in rehearsal.",
     "materials": "Pencils and the four pages for this lesson (PG:l4_read, PG:l4_journal, PG:l4_reflect). Students need no instruments; they think about their own recent practice.",
     "short": "Do steps 1, 2 and 4.",
     "extra": "Students finish the weekly goal on the journal page, or use the early finishers page (PG:early).",
     "steps": [
         ("5", "Welcome and thumbs", f"Say: <span class=say>“{SAY_OPEN}”</span> Then ask: <b>Thumbs up if you practiced at least once last week.</b> Do not comment on the count; just notice."),
         ("12", "Read and match", "Hand out the reading (PG:l4_read). Read the five strategies aloud together. Then students match each practice problem to its best strategy. Answers: PG:key3."),
         ("10", "Study a sample week", "Hand out the practice journal (PG:l4_journal). Part A shows one student’s week; students answer the questions. Check the sums with the key (PG:key3)."),
         ("10", "Plan your own week", "On the same page students fill in part B for the coming week. Remind them that a good goal is small and specific (for example, 15 minutes, 5 days)."),
         ("6", "Rehearsal reflection", "Hand out the reflection (PG:l4_reflect). Students rate themselves honestly on a scale of 1 to 4 and write one goal. These stay private; collect them only if the teacher asked you to.")]},
    {"n": 5, "title": "Seating and Terminology Puzzle", "skill": "Where the sections sit, and the Italian terms in your music",
     "goal": "Students label band and orchestra seating charts, match music terms to meanings and solve a word search.",
     "materials": "Pencils and the pages for this lesson (PG:l5_seat, PG:l5_terms, PG:l5_search). No instruments.",
     "short": "Do steps 1 to 3 and send the word search home.",
     "extra": "Play Silent Conductor (PG:glance) or hand out the early finishers page (PG:early).",
     "steps": [
         ("5", "Welcome and seats", f"Say: <span class=say>“{SAY_OPEN}”</span> Then ask: <b>Who sits in front of you in your ensemble, and who sits behind you?</b> Take a few answers."),
         ("12", "Seating charts", "Hand out the seating page (PG:l5_seat). Read the first paragraph aloud. Students label each numbered zone from the word bank. "
                                  "Say that ensembles differ, so their own director’s seating may be a little different."),
         ("10", "Music words", "Hand out the terms page (PG:l5_terms). Read the terms aloud together. Students match each term and put the loudness symbols in order."),
         ("10", "Word search", "Hand out the word search (PG:l5_search). Students find all 12 words. Ask the early finishers to write the meaning of three of them."),
         ("5", "Silent conductor", "Choose a student conductor. They show <b>loud</b>, <b>soft</b>, <b>fast</b>, <b>slow</b>, <b>crescendo</b> and <b>stop</b> with their hands only, and the class answers by patting their knees: big pats for loud, tiny pats for soft, hands still for stop.")]},
]


GAMES = [
    ("Name That Family", "The sub says an instrument. Woodwinds raise both hands, brass tap their shoulders, strings pat their knees, percussion tap the desk. Use the sort list (PG:l1_work).", "1"),
    ("Beat Clap-Back", "Clap a short rhythm from the note-value box (PG:l2_a); the class claps it back. Change the speed.", "2"),
    ("Composer Trivia", "Ask the class a question from the reading (PG:l3_read), such as where a composer was born. First hand up answers.", "3"),
    ("Practice Pledge", "Each student says one practice goal for the week in one sentence. Anyone may pass.", "4"),
    ("Silent Conductor", "A student conducts with hands only: wide arms are loud, small hands are soft, a fist is stop. The class pats knees to match.", "5"),
    ("Term Charades", "A student silently acts out a music term from PG:l5_terms (such as legato or staccato) with their arms; the class guesses.", "5"),
]

def welcome_page(n, watermark=False):
    rows = "".join("<tr><td style='height:24pt'></td><td></td><td></td><td></td></tr>" for _ in range(6))
    inner = (f'<div class="how">Teacher: fill this in once and keep it on top of the sub folder. Substitute: welcome, and thank you! '
             f'You do not need to know music. Everything for today is in this folder, and no lesson uses an instrument, a recording or a screen.</div>'
             f'<div style="font-size:11.5pt;margin:2pt 0 6pt"><b>Our ensemble:</b> &nbsp;{checkbox(12)} Concert band &nbsp;&nbsp;{checkbox(12)} Orchestra &nbsp;&nbsp;{checkbox(12)} Jazz band &nbsp;&nbsp;{checkbox(12)} Other: ________</div>'
             f'<div class="cols" style="gap:16pt"><div>{fl("Teacher")}{fl("Room")}{fl("School office ext.")}</div>'
             f'<div>{fl("Nearby teacher who can help")}{fl("Their room")}{fl("Date updated")}</div></div>'
             f'<div class="part">Today’s classes<span class="acc"> ·</span><small>Give each class the next lesson number it has not had.</small></div>'
             f'<table class="t"><tr><th style="width:18%">Time</th><th style="width:30%">Class / grade</th><th style="width:14%">Lesson #</th><th>Notes</th></tr>{rows}</table>'
             f'<div class="cols" style="gap:16pt;margin-top:2pt"><div>'
             f'<div class="part">How we do things<span class="acc"> ·</span></div>'
             f'{fl("Attention signal")}{fl("Entering the room")}{fl("Where students sit")}{fl("Bathroom / water")}{fl("Dismissal")}'
             f'</div><div>'
             f'<div class="part">Where things are<span class="acc"> ·</span></div>'
             f'{fl("Copies of worksheets")}{fl("Pencils")}{fl("Seating charts")}{fl("Emergency plans")}{fl("Class lists")}'
             f'</div></div>'
             f'<div class="box" style="margin-top:6pt;font-size:10.5pt"><b>Please keep instruments in their cases or in storage.</b> Each lesson has a plan page with timed steps and words to say. '
             f'Please leave notes on the sub report ({pg("report")}).</div>')
    return page("Welcome, substitute · fill in and keep on top", "FOR THE SUB", "Welcome sheet", inner, n, watermark)


def glance_page(n, watermark=False):
    rows = ""
    for d in LESSONS:
        k = d["n"]
        total = sum(int(m) for m, _, _ in d["steps"])
        a, b = {1: ("l1_read", "l1_work"), 2: ("l2_a", "l2_c"), 3: ("l3_read", "l3_work"), 4: ("l4_read", "l4_reflect"), 5: ("l5_seat", "l5_search")}[k]
        rows += (f"<tr><td class='ans' style='font-size:13pt;text-align:center'>{k}</td><td><b>{escape(d['title'])}</b><br>"
                 f"<span class='small'>{d['skill']}</span></td><td style='text-align:center'>{total} min</td>"
                 f"<td style='text-align:center'>{IX[f'l{k}_plan']}</td><td style='text-align:center'>{IX[a]}–{IX[b]}</td>"
                 f"<td style='text-align:center'>{IX['key1'] if k == 1 else IX['key2'] if k == 2 else IX['key3'] if k in (3, 4) else IX['key4']}</td></tr>")
    games = "".join(f"<tr><td><b>{g}</b></td><td>{fill_pages(t)}</td><td style='text-align:center'>{dd}</td></tr>" for g, t, dd in GAMES)
    inner = (f'<div class="how">Each lesson fills one 40–45 minute class. Every lesson works for <b>band or orchestra</b>, grades 6–12, and for a mixed class. '
             f'The lessons work in any order, and each one stands alone. Instruments stay in their cases.</div>'
             f'<table class="t"><tr><th style="width:8%">#</th><th>Lesson</th><th style="width:11%">Time</th><th style="width:10%">Plan</th>'
             f'<th style="width:14%">Student pages</th><th style="width:9%">Key</th></tr>{rows}</table>'
             f'<div class="small" style="margin:-1pt 0 4pt;font-size:9pt !important">The numbers in the last three columns are page numbers in this packet.</div>'
             f'<div class="part" style="margin-top:8pt">Game bank<span class="acc"> ·</span><small>No-prep, silent-instrument games for extra time. No equipment, no audio.</small></div>'
             f'<table class="t"><tr><th style="width:23%">Game</th><th>How to play</th><th style="width:9%">Lesson</th></tr>{games}</table>'
             f'<div class="part" style="margin-top:8pt">Tips for a calm class<span class="acc"> ·</span></div>'
             f'<ul style="margin:0;padding-left:15pt;font-size:10.6pt;line-height:1.38">'
             f'<li>Use the teacher’s attention signal from the welcome sheet ({pg("welcome")}). If there is none, raise one hand and wait.</li>'
             f'<li>Students sit in their normal ensemble seats or the seats the welcome sheet lists. Instruments stay put.</li>'
             f'<li>If a student asks to play, say: <i>“Your director wants us to learn about music today. You can play tomorrow.”</i></li>'
             f'<li>Name one student who is helping, and write the names of any students who are not on the sub report.</li></ul>')
    return page("Lessons at a glance and game bank", "FOR THE SUB", "5 lessons, any order", inner, n, watermark)


def plan_page(d, n, watermark=False):
    k = d["n"]
    steps = "".join(
        f'<li><div class="tm"><b>{m} min</b><span>Step {i + 1}</span></div><div class="tx"><b class="hd">{escape(h)}</b><br>{fill_pages(t)}</div></li>'
        for i, (m, h, t) in enumerate(d["steps"]))
    total = sum(int(m) for m, _, _ in d["steps"])
    inner = (f'<div class="meta"><div><b class="k">Goal</b>{d["goal"]}</div><div><b class="k">You need</b>{fill_pages(d["materials"])}</div>'
             f'<div style="flex:0 0 1.25in"><b class="k">Time</b>about {total} min<br><span class="small">for band or orchestra</span></div></div>'
             f'<div class="part" style="margin-top:8pt">Step by step<span class="acc"> ·</span><small>Italic lines are words you can say.</small></div>'
             f'<ol class="steps">{steps}</ol>'
             f'<div class="box" style="margin-top:auto;font-size:10.5pt"><b>Extra time?</b> {fill_pages(d["extra"])} '
             f'<b>Short class?</b> {d["short"]}</div>')
    return page(f"Lesson {k} · {escape(d['skill'])}", f"LESSON {k}", "Sub plan · no instruments", inner, n, watermark, title=d["title"])


def sheet(k, title, sub, inner, n, watermark=False, key_page=None, tagsub=None):
    right = f"Answer key on page {IX[key_page]}" if key_page else None
    return page(sub, f"LESSON {k}", tagsub or "Student page", inner, n, watermark, name=True, right=right, title=title)


def box_ans(val, key, w=34, h=24, size=14):
    return (f'<span style="display:inline-block;min-width:{w}pt;height:{h}pt;border:1.3pt solid #000;border-radius:5pt;text-align:center;padding:0 4pt;'
            f'line-height:{h - 2.6}pt;vertical-align:middle;font-family:Oswald;font-weight:700;font-size:{size}pt;color:{ACCENT}">{val if key else ""}</span>')


def tf_choice(ans, key):
    return circ("TRUE", key and ans) + circ("FALSE", key and not ans)


def mc_block(i, q, opts, correct, key, small=False):
    o = "".join(f'<span style="white-space:nowrap;margin-right:8pt">{circ(lbl(j), key and j == correct)} {escape(t)}</span>' for j, t in enumerate(opts))
    return f'<div style="margin-bottom:5pt;font-size:{10.5 if small else 11}pt;line-height:1.5"><b>{i}.</b> {escape(q)}<br>{o}</div>'


# ================================================================ LESSON 1 PAGES
L1_READ = [
    ("Woodwinds", "A flute player blows air across an edge. A clarinet or saxophone player makes a single reed vibrate. An oboe or bassoon player uses a double reed, "
                  "two reeds tied together that vibrate against each other. Many woodwinds were once made of wood, but not all are today. "
                  "A saxophone is made of brass, yet it is a woodwind because it uses a reed."),
    ("Brass", "Brass players buzz their lips inside a cup-shaped mouthpiece, and the tubing makes the buzz louder and gives it a color. "
              "A trumpet, French horn or tuba player changes notes by pressing valves; a trombone player moves a slide. "
              "A tuba is the largest and lowest of the common brass instruments."),
    ("Percussion", "Percussion instruments are struck, shaken or scraped. Some play a definite pitch, such as the timpani (kettledrums, which can be tuned) and the xylophone. "
                   "Others, such as the snare drum and cymbals, make sounds with no clear pitch."),
    ("Strings", "Violins, violas, cellos and double basses make sound when a bow is drawn across the strings or when the strings are plucked. "
                "They are built in the same shape but in different sizes: the smaller the instrument, the higher it sounds. The violin is the smallest and highest; "
                "the double bass is the largest and lowest."),
]
L1_CARE = ["Keep your instrument in its case, latched, when you are not playing. Never leave it on a chair or on the floor.",
           "Swab or wipe out a woodwind after you play, to remove moisture.",
           "Keep reeds in a reed case or holder. Use your own mouthpiece and do not share it.",
           "Put rosin on the bow hair, not on the strings, and loosen the bow hair when you put the bow away. Do not touch the bow hair with your fingers.",
           "Use valve oil or slide grease only as your director shows you, and never force a stuck valve or slide.",
           "Keep instruments away from heat and cold. A parked car can get far too hot or too cold."]


def l1_read(n, watermark=False):
    fam = "".join(f'<div style="margin-bottom:8pt"><div class="h" style="font-size:14pt;margin-bottom:2pt">{escape(f)} <span style="color:{ACCENT}">·</span></div>'
                  f'<p style="margin:0;font-size:11pt;line-height:1.36">{escape(t)}</p></div>' for f, t in L1_READ)
    care = "".join(f"<li>{escape(c)}</li>" for c in L1_CARE)
    inner = (f'<div class="how" style="font-size:12pt">Instruments are grouped into <b>families</b> by how they make sound. A concert band is mostly woodwinds, brass and percussion. '
             f'An orchestra has all four families, and its string section is the largest.</div>'
             f'<div class="cols" style="gap:20pt"><div>{fam}</div><div>'
             f'<div class="box" style="margin-bottom:8pt"><div class="h" style="font-size:14pt;margin-bottom:3pt">How to look after your instrument</div>'
             f'<ol style="margin:0;padding-left:16pt;font-size:11pt;line-height:1.36">{care}</ol></div>'
             f'<div class="box" style="font-size:10.5pt"><b>Did you know?</b> Most bands and orchestras tune to a single note. Instruments in different families sound different because their sound starts differently: a buzz, a reed, an edge, a string or a strike.</div>'
             f'</div></div>')
    return page("Reading · The four instrument families", "LESSON 1", "Reading page", inner, n, watermark, name=True, title="Instrument Families")


def l1_work(n, watermark=False, key=False):
    fam_names = list(FAMILIES)
    sort_boxes = ""
    for f in fam_names:
        items = ", ".join(FAMILIES[f]) if key else ""
        sort_boxes += (f'<div style="border:1.3pt solid #000;border-radius:7pt;padding:3pt 7pt;min-height:48pt"><div class="h" style="font-size:11.5pt">{f}</div>'
                       f'<div style="font-size:10pt;color:{ACCENT};font-weight:700;line-height:1.25">{escape(items)}</div></div>')
    bank = " · ".join(f"<b>{escape(w)}</b>" for w in SORT_BANK)
    match = ""
    for i, (inst, _) in enumerate(SOUND_MATCH):
        match += f'<div style="display:flex;align-items:center;gap:6pt;margin:2pt 0;font-size:11pt"><b style="width:12pt">{i + 1}</b><span style="width:70pt">{inst}</span>{box_ans(lbl(SOUND_ORDER.index(i)), key, 26, 20, 12)}</div>'
    stm = "".join(f'<div style="margin:2pt 0;font-size:10.5pt"><b>{lbl(j)}.</b> {escape(SOUND_MATCH[i][1])}</div>' for j, i in enumerate(SOUND_ORDER))
    tf = "".join(f'<div style="display:flex;gap:6pt;margin:2pt 0;font-size:10.3pt;align-items:center"><b>{i + 1}.</b><span style="flex:1">{escape(t)}</span>'
                 f'<span style="white-space:nowrap">{tf_choice(a, key)}</span></div>' for i, (t, a) in enumerate(CARE_TF))
    mcs = "".join(mc_block(i + 1, q, o, c, key, True) for i, (q, o, c) in enumerate(L1_MC[:N_L1_MC]))
    inner = (f'<div class="part" style="margin-top:2pt">A · Sort the instruments<small>Write each instrument from the word bank in its family box.</small></div>'
             f'<div class="small" style="font-size:9.5pt !important;margin-bottom:4pt">{bank}</div>'
             f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:6pt">{sort_boxes}</div>'
             f'<div class="part" style="margin-top:8pt">B · How does the sound start?<small>Write the letter of the best statement next to each instrument.</small></div>'
             f'<div class="cols" style="gap:10pt"><div style="flex:0 0 138pt">{match}</div><div>{stm}</div></div>'
             f'<div class="part" style="margin-top:6pt">C · True or false: caring for your instrument<small>Circle TRUE or FALSE.</small></div>{tf}'
             f'<div class="part" style="margin-top:6pt">D · Reading check</div>{mcs}')
    if key:
        return inner
    return sheet(1, "Sort and Match", "Sort, match and think", inner, n, watermark, key_page="key1")


# ================================================================ LESSON 2 PAGES (engraved rhythm math)
def _single(t, cx, yl, s):
    return tok_svg(t, cx, yl, s, 40)


def expr_svg(p, s=7, yl=38, plus=True):
    """Note values in a row with + between them; returns (svg body, width in pt)."""
    parts, x = [], 6
    for j, t in enumerate(p):
        if j:
            parts.append(text(x + 5, yl + 3, "+" if plus else "", 15, 500))
            x += 16
        w = 30 if t == "e" else (28 if t != "w" else 32)
        parts.append(_single(t, x + w / 2, yl, s))
        x += w
    return "".join(parts), x + 4


def l2_a(n, watermark=False):
    ref = ""
    for t, nm, bt in (("w", "whole note", "4 beats"), ("h", "half note", "2 beats"), ("q", "quarter note", "1 beat"),
                      ("e", "two eighth notes", "1 beat together"), ("r", "quarter rest", "1 beat of silence")):
        ref += (f'<div style="text-align:center;flex:1">{svg(60, 46, _single(t, 30, 30, 7))}<div class="h" style="font-size:10pt;line-height:1.1">{nm}</div>'
                f'<div style="font-size:10pt;color:{ACCENT};font-weight:700">{bt}</div></div>')
    sigs = ("<b>Time signature:</b> the top number tells how many beats are in each measure; the bottom number tells which note gets one beat. "
            "In <b>4/4</b> there are 4 beats in every measure and the quarter note gets one beat.")
    cells = []
    for i, p in enumerate(L2_ADD):
        body, w = expr_svg(p)
        body += text(w + 6, 41, "=", 15, 500)
        cells.append(f'<div style="display:flex;align-items:center;gap:6pt;border:1.3pt solid #000;border-radius:7pt;padding:1pt 8pt"><b class="h" style="font-size:13pt">{i + 1}</b>'
                     f'{svg(w + 16, 54, body)}{box_ans("", False, 34, 24)}<span style="font-size:10pt">beats</span></div>')
    miss = []
    for i, p in enumerate(L2_SHORT):
        st, xe = rhythm_svg(p, 8, 30, 6, 28, syl=False)
        miss.append(f'<div style="display:flex;align-items:center;gap:6pt;border:1.3pt solid #000;border-radius:7pt;padding:1pt 8pt;min-width:0"><b class="h" style="font-size:13pt">{i + 1}</b>'
                    f'{svg(int(xe) + 6, 52, st)}<span style="flex:1"></span><span style="font-size:10pt;text-align:right">beats<br>missing</span>{box_ans("", False, 30, 24)}</div>')
    inner = (f'<div class="box" style="padding:5pt 8pt;margin-top:4pt"><div style="display:flex;gap:2pt">{ref}</div>'
             f'<div style="font-size:10.2pt;margin-top:3pt;line-height:1.3">{sigs}</div></div>'
             f'<div class="part" style="margin-top:8pt">A · Add the beats<small>Write the total number of beats. A rest counts as a beat too.</small></div>'
             f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:6pt 12pt">{"".join(cells)}</div>'
             f'<div class="part" style="margin-top:10pt">B · How many beats are missing?<small>Each measure should have 4 beats in 4/4. Write how many beats it is short.</small></div>'
             f'<div style="display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:6pt 12pt">{"".join(miss)}</div>')
    return sheet(2, "Rhythm Math A", "Note values, add and find the missing beats", inner, n, watermark, key_page="key2")


def l2_b(n, watermark=False):
    cmp = []
    for i, (a, b) in enumerate(L2_CMP):
        ba, wa = expr_svg(a, 6.2, 36)
        bb, wb = expr_svg(b, 6.2, 36)
        cmp.append(f'<div style="display:flex;align-items:center;gap:5pt;border:1.3pt solid #000;border-radius:7pt;padding:1pt 8pt"><b class="h" style="font-size:12pt">{i + 1}</b>'
                   f'{svg(wa + 2, 50, ba)}<span style="white-space:nowrap;font-size:11pt">{circ("&lt;")}{circ("=")}{circ("&gt;")}</span>{svg(wb + 2, 50, bb)}</div>')
    circ_items = []
    for i, p in enumerate(L2_CIRCLE):
        st, xe = rhythm_svg(p, 6, 28, 5.6, 22, timesig=False)
        circ_items.append(f'<div style="display:flex;align-items:center;gap:4pt;border:1.3pt solid #000;border-radius:7pt;padding:1pt 7pt;min-width:0"><b class="h" style="font-size:12pt">{i + 1}</b>'
                          f'{svg(int(xe) + 4, 46, st)}<span style="flex:1"></span><span style="white-space:nowrap;font-size:10.5pt">{circ("YES")}{circ("NO")}</span></div>')
    inner = (f'<div class="part" style="margin-top:2pt">C · Greater, equal or smaller?<small>Add each side. Circle &lt;, = or &gt;.</small></div>'
             f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:6pt 12pt">{"".join(cmp)}</div>'
             f'<div class="part" style="margin-top:8pt">D · Is it 4 beats?<small>Circle YES if the measure adds up to exactly 4 beats in 4/4.</small></div>'
             f'<div style="display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:6pt 12pt">{"".join(circ_items)}</div>'
             )
    return sheet(2, "Rhythm Math B", "Compare and check measures", inner, n, watermark, key_page="key2")


def l2_c(n, watermark=False):
    sig_rows = ""
    for top_, bot in L2_SIGS:
        big = svg(26, 40, text(13, 17, str(top_), 18, 700) + text(13, 37, str(bot), 18, 700))
        sig_rows += (f'<tr><td style="text-align:center;width:44pt">{big}</td><td>{box_ans("", False, 28, 22)} beats in each measure</td>'
                     f'<td>The {box_ans("", False, 120, 22)} gets one beat</td></tr>')
    words = "".join(f'<div style="display:flex;gap:8pt;align-items:flex-end;margin:0 0 9pt;font-size:10.8pt"><b>{i + 1}.</b><span style="flex:1;line-height:1.2">{escape(q)}</span>'
                    f'<span style="width:84pt;border-bottom:1pt solid #000;height:15pt"></span></div>' for i, (q, a) in enumerate(L2_WORDS))
    blank = ""
    for _ in range(3):
        st, xe = rhythm_svg("qqqq", 6, 26, 6.4, 34)
        st = re.sub(r'<text [^>]*font-family="Bravura"[^>]*>&#x(?!E084)[0-9A-F]+;</text>', "", st)
        blank += f'<div style="border:1.3pt solid #000;border-radius:7pt;padding:0 6pt;margin-bottom:6pt">{svg(int(xe) + 6, 48, st)}</div>'
    inner = (f'<div class="part" style="margin-top:2pt">E · Time signatures<small>Fill in what each time signature tells you.</small></div>'
             f'<table class="t" style="font-size:10.8pt">{sig_rows}</table>'
             f'<div class="part" style="margin-top:12pt">F · Beats per minute<small>A minute has 60 seconds. Show your work in the margin.</small></div>{words}'
             f'<div class="part" style="margin-top:12pt">G · Write your own<small>Draw three different measures of 4/4 using whole, half and quarter notes, eighth pairs and rests. Each must add up to 4 beats.</small></div>{blank}')
    return sheet(2, "Rhythm Math C", "Time signatures, tempo and your own rhythms", inner, n, watermark, key_page="key2")


# ================================================================ LESSON 3 PAGES (composers)
L3_READ = [
    ("Johann Sebastian Bach", "Bach", "1685–1750", "Baroque era (roughly 1600–1750)",
     "Bach was born in Eisenach, Germany, into a family of musicians. He worked as an organist and a music director, and from 1723 until he died he led the music at St. Thomas Church in Leipzig. "
     "He wrote six Brandenburg Concertos, which he sent to a nobleman in 1721, and a huge amount of music for organ, keyboard, voices and orchestra."),
    ("Wolfgang Amadeus Mozart", "Mozart", "1756–1791", "Classical era (roughly 1750–1820)",
     "Mozart was born in Salzburg, in today’s Austria. As a child he played and wrote music, and he toured Europe as a young performer. "
     "He lived in Vienna as an adult, wrote more than 600 works, including symphonies, concertos and operas, and died there at age 35."),
    ("Ludwig van Beethoven", "Beethoven", "1770–1827", "Between the Classical and Romantic eras",
     "Beethoven was born in Bonn, Germany, and spent most of his adult life in Vienna. In his late twenties he began to lose his hearing, "
     "but he kept composing. He wrote nine symphonies; his Symphony No. 9, first performed in Vienna in 1824, ends with a chorus and four solo singers."),
    ("John Philip Sousa", "Sousa", "1854–1932", "Wind-band composer",
     "Sousa was born in Washington, D.C. He led the U.S. Marine Band from 1880 to 1892, then formed his own Sousa Band. He wrote more than 100 marches and is called “The March King.” "
     "His march “The Stars and Stripes Forever” (1896) became the national march of the United States by act of Congress in 1987. The sousaphone, a tuba that wraps around the player, is named for him."),
]


def l3_read(n, watermark=False):
    blocks = ""
    for full, short, yrs, era, txt in L3_READ:
        blocks += (f'<div style="border:1.4pt solid #000;border-radius:8pt;padding:6pt 10pt;margin-bottom:8pt"><div style="display:flex;justify-content:space-between;align-items:baseline">'
                   f'<div class="h" style="font-size:15pt">{full}</div><div class="h" style="font-size:12pt;color:{ACCENT}">{yrs}</div></div>'
                   f'<div class="l" style="font-size:10.5pt;margin-bottom:2pt">{era}</div><p style="margin:0;font-size:11pt;line-height:1.36">{escape(txt)}</p></div>')
    inner = (f'<div class="how" style="font-size:12pt">Bands and orchestras play music from many centuries. Here are four composers whose work you may meet. '
             f'The years are the years each composer lived.</div>{blocks}'
             f'<div class="small" style="font-size:9.5pt !important">Era dates are rough: historians draw the lines in slightly different places.</div>')
    return page("Reading · Four composers", "LESSON 3", "Reading page", inner, n, watermark, name=True, title="Composers")


def l3_work(n, watermark=False):
    mcs = "".join(mc_block(i + 1, q, o, c, False, True) for i, (q, o, c) in enumerate(L3_MC))
    mrows = ""
    for i, k in enumerate(L3_MATCH_ORDER):
        clue = L3_MATCH[k][0]
        mrows += f'<div style="display:flex;gap:6pt;align-items:center;margin:3pt 0;font-size:10.8pt"><span style="flex:1"><b>{i + 1}.</b> {escape(clue)}</span>{box_ans("", False, 80, 20, 12)}</div>'
    maths = "".join(f'<div style="display:flex;gap:8pt;align-items:flex-end;margin:0 0 6pt;font-size:10.8pt"><b>{i + 1}.</b><span style="flex:1;line-height:1.2">{escape(q)}</span>'
                    f'<span style="width:60pt;border-bottom:1pt solid #000;height:15pt"></span></div>' for i, (q, a) in enumerate(L3_MATH))
    order = "".join(f'<span style="display:inline-flex;align-items:center;gap:4pt;margin-right:14pt;font-size:11pt"><b>{nm}</b>{box_ans("", False, 24, 20, 12)}</span>' for nm in L3_ORDER)
    inner = (f'<div class="part" style="margin-top:2pt">A · Multiple choice<small>Circle the best answer. Use the reading.</small></div>{mcs}'
             f'<div class="part" style="margin-top:2pt">B · Who am I?<small>Write BACH, MOZART, BEETHOVEN or SOUSA.</small></div>{mrows}'
             f'<div class="part" style="margin-top:8pt">C · Timeline math<small>Use the years in the reading.</small></div>{maths}'
             f'<div style="margin-top:2pt;font-size:10.8pt"><b>6. Put the composers in order by birth year, writing 1 for the earliest and 4 for the latest.</b><div style="margin-top:4pt">{order}</div></div>'
             f'<div class="part" style="margin-top:8pt">D · Your thoughts</div><div class="small" style="margin-bottom:2pt">Which composer would you most like to hear about next, and why?</div><div class="ln2"></div><div class="ln2"></div>')
    return sheet(3, "Composer Questions", "Read, answer and work out the years", inner, n, watermark, key_page="key3")


# ================================================================ LESSON 4 PAGES (practice and rehearsal)
L4_STRATS = [
    ("Isolate the hard spot", "Do not play the whole piece again and again. Find the one or two measures that go wrong and repeat just those, slowly."),
    ("Use a steady beat", "A metronome or a steady foot tap shows you when you rush or drag. Start slow and speed up a little at a time."),
    ("Work in small chunks", "Break a piece into short sections of one to four measures. Make one chunk right, then join it to the next."),
    ("Mark your music", "Circle trouble spots in pencil, and write in counts or reminders, so you know where to start tomorrow."),
    ("Set one goal", "Before you start, decide what you will fix today. A clear goal keeps your practice from drifting."),
]


def l4_read(n, watermark=False):
    strat = "".join(f'<li style="margin-bottom:5pt"><b>{escape(h)}.</b> {escape(t)}</li>' for h, t in L4_STRATS)
    pairs = ""
    for i, k in enumerate(STRAT_ORDER):
        pairs += (f'<div style="display:flex;gap:6pt;align-items:center;margin:4pt 0;font-size:10.8pt"><span style="flex:1"><b>{i + 1}.</b> {escape(STRAT[k][0])}</span>'
                  f'{box_ans("", False, 28, 20, 12)}</div>')
    opts = "".join(f'<div style="margin:3pt 0;font-size:10.5pt"><b>{lbl(j)}.</b> {escape(STRAT[k][1])}</div>' for j, k in enumerate(range(len(STRAT))))
    inner = (f'<div class="how" style="font-size:12pt">Practice is not the same as playing through your music. Good practice is short, focused and has a plan. '
             f'Here are five strategies that many band and orchestra directors teach.</div>'
             f'<div class="box" style="margin-bottom:6pt"><ol style="margin:0;padding-left:16pt;font-size:11pt;line-height:1.34">{strat}</ol></div>'
             f'<div class="part" style="margin-top:6pt">Match the problem to the best strategy<small>Write the letter of the strategy.</small></div>'
             f'<div class="cols" style="gap:12pt"><div>{pairs}</div><div>{opts}</div></div>')
    return page("Reading · Five practice strategies", "LESSON 4", "Reading + match", inner, n, watermark, name=True, title="Practice Smarter", right=f"Answer key on page {IX['key3']}")


def journal_totals():
    mins = [m for _, m, _ in JOURNAL]
    total = sum(mins)
    days = sum(1 for m in mins if m > 0)
    avg = total / days
    longest = max(JOURNAL, key=lambda r: r[1])[0]
    return total, days, avg, longest, total >= JOURNAL_GOAL


def l4_journal(n, watermark=False):
    rows = "".join(f"<tr><td><b>{d}</b></td><td style='text-align:center'>{m}</td><td>{w}</td></tr>" for d, m, w in JOURNAL)
    qs = ["Total minutes practiced this week", "Number of days practiced", "Average minutes on the days practiced (round to one decimal)",
          "Day with the longest practice", f"Did the student reach the goal of {JOURNAL_GOAL} minutes? Circle one:  YES  /  NO"]
    qh = "".join(f'<div style="display:flex;gap:6pt;align-items:flex-end;margin:0 0 5pt;font-size:10.6pt"><b>{i + 1}.</b><span style="flex:1;line-height:1.2">{escape(q)}</span>'
                 f'<span style="width:64pt;border-bottom:1pt solid #000;height:15pt"></span></div>' for i, q in enumerate(qs))
    blank = "".join("<tr><td style='height:21pt;width:44pt'></td><td style='width:52pt'></td><td></td><td style='width:60pt'></td></tr>" for _ in range(7))
    inner = (f'<div class="part" style="margin-top:2pt">A · A sample week<small>Read one student’s journal and answer the questions.</small></div>'
             f'<div class="cols" style="gap:14pt"><div style="flex:0 0 45%"><table class="t" style="font-size:10pt"><tr><th>Day</th><th>Minutes</th><th>What I worked on</th></tr>{rows}</table></div>'
             f'<div style="padding-top:3pt">{qh}</div></div>'
             f'<div class="part" style="margin-top:8pt">B · My practice plan<small>Fill this in for the coming week. Then fill in the minutes after each practice.</small></div>'
             f'<div style="display:flex;gap:18pt;font-size:11pt;margin-bottom:4pt"><span><b>My goal:</b> ______ minutes on ______ days</span><span><b>Starting with:</b> ____________________</span></div>'
             f'<table class="t"><tr><th>Day</th><th>Minutes</th><th>What I worked on</th><th>How it went (1–4)</th></tr>{blank}</table>'
             f'<div class="small" style="margin-top:3pt;font-size:9.5pt !important">How it went: 1 = hard day, 2 = ok, 3 = good, 4 = great. Total minutes: ________</div>')
    return sheet(4, "Practice Journal", "Study a sample week and plan your own", inner, n, watermark, key_page="key3")


def l4_reflect(n, watermark=False):
    head = "".join(f'<th style="width:34pt;text-align:center">{k}</th>' for k in "1234")
    rows = "".join(f'<tr><td style="font-size:10.8pt">{escape(t)}</td>' + "".join(f'<td style="text-align:center">{circ(str(k))}</td>' for k in range(1, 5)) + "</tr>"
                   for t in RATING_ITEMS)
    inner = (f'<div class="how" style="font-size:12pt">Think about your most recent rehearsal. Be honest: this is for you, not a grade. '
             f'<b>1</b> = not yet, <b>2</b> = sometimes, <b>3</b> = usually, <b>4</b> = always.</div>'
             f'<table class="t"><tr><th>In my last rehearsal...</th>{head}</tr>{rows}</table>'
             f'<div class="part" style="margin-top:10pt">One thing our group did well</div><div class="ln2"></div><div class="ln2"></div>'
             f'<div class="part" style="margin-top:6pt">One thing our group should fix</div><div class="ln2"></div><div class="ln2"></div>'
             f'<div class="part" style="margin-top:6pt">My goal for the next rehearsal<small>Make it small and specific.</small></div><div class="ln2"></div><div class="ln2"></div>'
             f'<div class="part" style="margin-top:6pt">Something I can do this week to help my section</div><div class="ln2"></div><div class="ln2"></div>')
    return sheet(4, "Rehearsal Reflection", "Rate yourself and set a goal", inner, n, watermark, tagsub="Student page")


# ================================================================ LESSON 5 PAGES (seating and terms)
import math


def sector(cx, cy, r1, r2, a1, a2):
    """Annular sector; angles in degrees from the left (0) over the top (90) to the right (180)."""
    def pt(r, a):
        return cx - r * math.cos(math.radians(a)), cy - r * math.sin(math.radians(a))
    x1, y1 = pt(r2, a1)
    x2, y2 = pt(r2, a2)
    x3, y3 = pt(r1, a2)
    x4, y4 = pt(r1, a1)
    return (f"M{x1:.1f} {y1:.1f} A{r2} {r2} 0 0 1 {x2:.1f} {y2:.1f} L{x3:.1f} {y3:.1f} A{r1} {r1} 0 0 0 {x4:.1f} {y4:.1f} Z",
            pt((r1 + r2) / 2, (a1 + a2) / 2))


BAND_GEOM = {"1": (50, 100, 8, 172), "2": (104, 140, 14, 166), "3": (144, 172, 22, 158)}
ORCH_GEOM = {"1": (46, 92, 10, 58), "2": (46, 92, 58, 92), "3": (46, 92, 92, 124), "4": (46, 92, 124, 168),
             "5": (96, 132, 128, 170), "6": (96, 132, 40, 120), "7": (136, 172, 45, 135), "8": (176, 206, 25, 155)}


def seating_svg(geom, w, h, cx, cy, key_names=None, fills=None):
    out = []
    for num, (r1, r2, a1, a2) in geom.items():
        d, (px, py) = sector(cx, cy, r1, r2, a1, a2)
        fill = (fills or {}).get(num, "#fff")
        out.append(f'<path d="{d}" fill="{fill}" stroke="#000" stroke-width="1.8" stroke-linejoin="round"/>')
        out.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="10" fill="#fff" stroke="#000" stroke-width="1.5"/>')
        out.append(text(px, py + 5, num, 14, 700))
    out.append(f'<circle cx="{cx}" cy="{cy - 8}" r="8" fill="{ACCENT}" stroke="#000" stroke-width="1.5"/>')
    out.append(text(cx, cy + 16, "CONDUCTOR", 9, 500))
    out.append(text(cx, cy + 30, "AUDIENCE", 9, 300, extra='letter-spacing="2"'))
    return svg(w, h, "".join(out), "display:block;margin:0 auto;width:100%;height:auto")


def l5_seat(n, watermark=False):
    band = seating_svg(BAND_GEOM, 320, 216, 160, 186, fills={"1": TINT2, "2": "#fff", "3": TINT1})
    orch = seating_svg(ORCH_GEOM, 420, 262, 210, 224, fills={"1": TINT2, "2": TINT2, "3": TINT2, "4": TINT2, "5": TINT2, "6": "#fff", "7": "#fff", "8": TINT1})
    bank_b = " · ".join(f"<b>{w}</b>" for w in ZONE_BANK_BAND)
    bank_o = " · ".join(f"<b>{w}</b>" for w in ZONE_BANK_ORCH)
    rb = "".join(f'<div style="display:flex;align-items:flex-end;gap:5pt;margin:5pt 0;font-size:11pt"><b style="width:12pt">{a}</b><span style="flex:1;border-bottom:1pt solid #000;height:16pt"></span></div>' for a, _, _ in BAND_ZONES)
    ro = "".join(f'<div style="display:flex;align-items:flex-end;gap:5pt;margin:3pt 0;font-size:11pt"><b style="width:12pt">{a}</b><span style="flex:1;border-bottom:1pt solid #000;height:15pt"></span></div>' for a, _ in ORCH_ZONES)
    inner = (f'<div class="how" style="font-size:11.3pt">Seen from above, with the audience at the bottom. Loud instruments usually sit behind softer ones so that everyone can be heard. '
             f'Most groups seat like this, but your director’s plan may be a little different.</div>'
             f'<div class="part" style="margin:4pt 0 2pt">A · Concert band<small>Write the name of each zone from the bank: {bank_b}</small></div>'
             f'<div class="cols" style="gap:10pt;align-items:center"><div style="flex:0 0 60%">{band}</div><div>{rb}</div></div>'
             f'<div class="part" style="margin:6pt 0 2pt">B · Orchestra<small>Bank: {bank_o}</small></div>'
             f'<div class="cols" style="gap:10pt;align-items:center"><div style="flex:0 0 66%">{orch}</div><div>{ro}</div></div>')
    return sheet(5, "Seating Charts", "Label where each section sits", inner, n, watermark, key_page="key4")


def l5_terms(n, watermark=False):
    left = "".join(f'<div style="display:flex;gap:6pt;align-items:center;margin:2.5pt 0;font-size:11pt"><b style="width:14pt">{i + 1}</b><span style="width:80pt"><b>{TERMS[k][0]}</b></span>{box_ans("", False, 24, 18, 12)}</div>'
                   for i, k in enumerate(range(len(TERMS))))
    right = "".join(f'<div style="margin:2.5pt 0;font-size:10.5pt"><b>{lbl(j)}.</b> {escape(TERMS[k][1])}</div>' for j, k in enumerate(TERM_ORDER))
    dyn = "".join(f"<tr><td style='text-align:center'><b>{s_}</b></td><td>{nm}</td><td>{mn}</td></tr>" for s_, nm, mn in DYNAMICS)
    order = " &nbsp; ".join(f'<span style="display:inline-block;border:1.3pt solid #000;border-radius:5pt;padding:1pt 8pt;font-family:Oswald;font-weight:700;font-size:13pt">{d}</span>' for d in DYN_SCRAMBLED)
    blank = '<span style="display:inline-block;width:90pt;border-bottom:1pt solid #000">&nbsp;</span>'
    cl = "".join(f'<div style="margin:3pt 0;font-size:10.8pt"><b>{i + 1}.</b> {escape(s_).replace("______", blank)}</div>' for i, (s_, a) in enumerate(CLOZE))
    bank = " · ".join(f"<b>{w}</b>" for w in CLOZE_BANK)
    inner = (f'<div class="cols" style="gap:14pt"><div style="flex:0 0 40%"><div class="part" style="margin-top:2pt">Loudness symbols</div>'
             f'<table class="t" style="font-size:10pt"><tr><th>Symbol</th><th>Word</th><th>Meaning</th></tr>{dyn}</table></div>'
             f'<div><div class="part" style="margin-top:2pt">A · Put them in order<small>Write 1 to 6 over each symbol, softest (1) to loudest (6).</small></div>'
             f'<div style="margin-top:6pt">{order}</div><div class="small" style="margin-top:4pt">Tip: “piano” means soft and “forte” means loud.</div></div></div>'
             f'<div class="part" style="margin-top:8pt">B · Match each term to its meaning<small>Write the letter.</small></div>'
             f'<div class="cols" style="gap:12pt"><div style="flex:0 0 150pt">{left}</div><div>{right}</div></div>'
             f'<div class="part" style="margin-top:6pt">C · Who is who?<small>Fill in each blank from the bank: {bank}</small></div>{cl}')
    return sheet(5, "Music Words", "Match the terms, order the loudness", inner, n, watermark, key_page="key4")


def search_svg(highlight=False, cell=25):
    cell = cell
    out = []
    hl = set()
    if highlight:
        for cells in SEARCH_SOL.values():
            hl |= set(cells)
    for r, row in enumerate(SEARCH):
        for c, ch in enumerate(row):
            if (r, c) in hl:
                out.append(f'<rect x="{c * cell + 1}" y="{r * cell + 1}" width="{cell - 2}" height="{cell - 2}" rx="4" fill="{TINT2}"/>')
            out.append(text(c * cell + cell / 2, r * cell + cell * 0.72, ch, cell * 0.6, 500 if (r, c) not in hl else 700, "Oswald"))
    w = GRID_N * cell
    out.insert(0, f'<rect x="0" y="0" width="{w}" height="{w}" fill="#fff" stroke="#000" stroke-width="1.6" rx="4"/>')
    return svg(w, w, "".join(out), "display:block")


def l5_search(n, watermark=False):
    words = "".join(f'<div style="font-family:Oswald;font-weight:500;font-size:13pt;letter-spacing:.06em;margin:3pt 0">{checkbox(10)} {w}</div>' for w in SEARCH_WORDS)
    inner = (f'<div class="how" style="font-size:12pt">Find the 12 music words. Words run across, down and diagonally, forwards or backwards. Circle each one and tick it off the list.</div>'
             f'<div class="cols" style="gap:16pt;align-items:flex-start"><div style="flex:0 0 {GRID_N * 25}pt">{search_svg()}</div>'
             f'<div>{words}</div></div>'
             f'<div class="part" style="margin-top:12pt">Bonus<small>Write what three of the words mean (use the music words page if you need help).</small></div>'
             f'<div class="ln2"></div><div class="ln2"></div><div class="ln2"></div>')
    return sheet(5, "Music Word Search", "Find the hidden terms", inner, n, watermark, key_page="key4")


# ================================================================ EARLY FINISHERS, KEYS, REPORT
def early_page(n, watermark=False):
    sc = "".join(f'<div style="display:flex;align-items:center;gap:8pt;margin:3pt 0;font-size:11pt"><b>{i + 1}.</b><span style="width:96pt;font-family:Oswald;font-weight:700;letter-spacing:.12em;font-size:13pt">{w}</span>'
                 f'<span style="flex:1;border-bottom:1pt solid #000;height:15pt"></span></div>' for i, (w, a) in enumerate(SCRAMBLES))
    rd = "".join(f'<div style="display:flex;gap:8pt;align-items:flex-end;margin:0 0 6pt;font-size:10.8pt"><b>{i + 1}.</b><span style="flex:1;line-height:1.22">{escape(q)}</span>'
                 f'<span style="width:100pt;border-bottom:1pt solid #000;height:15pt"></span></div>' for i, (q, a) in enumerate(RIDDLES))
    inner = (f'<div class="how">Finished early? Pick one (or do them all).</div>'
             f'<div class="part" style="margin-top:0">Instrument scramble<small>Unscramble each instrument name.</small></div>{sc}'
             f'<div class="part" style="margin-top:8pt">Instrument riddles<small>Which instrument am I?</small></div>{rd}'
             f'<div class="part" style="margin-top:8pt">Design a concert program<small>Invent a concert for your band or orchestra. List four pieces, with a composer or “original” for each.</small></div>'
             f'<div class="ln2"></div><div class="ln2"></div><div class="ln2"></div><div class="ln2"></div>'
             f'<div class="part" style="margin-top:8pt">Write a rehearsal tip<small>Write one tip that would help a new player in your section.</small></div><div class="ln2"></div><div class="ln2"></div>')
    return page("Early finishers · grades 6–12", "ANY LESSON", "Early finishers", inner, n, watermark, name=True, title="Early Finishers", right=f"Scramble and riddle answers on page {IX['key4']}")


def rank_of(names):
    return {nm: 1 + sorted(COMP[x][0] for x in names).index(COMP[nm][0]) for nm in names}


def key_items():
    """All printed answers: {page: [(heading, [items])]}; each item is one string that must appear in the PDF."""
    k = {}
    # Lesson 1
    sec = [("A · Sort", [f"{f}: {', '.join(FAMILIES[f])}" for f in FAMILIES]),
           ("B · How does the sound start?", [f"B{i + 1}: {lbl(SOUND_ORDER.index(i))}" for i in range(len(SOUND_MATCH))]),
           ("C · True or false", [f"C{i + 1}: {'TRUE' if a else 'FALSE'}" for i, (_, a) in enumerate(CARE_TF)]),
           ("D · Reading check", [f"D{i + 1}: {lbl(c)}" for i, (_, _, c) in enumerate(L1_MC[:N_L1_MC])])]
    k["key1"] = sec
    # Lesson 2
    k["key2"] = [("A · Add the beats", [f"A{i + 1}: {nbeats(p)}" for i, p in enumerate(L2_ADD)]),
                 ("B · Beats missing", [f"B{i + 1}: {4 - nbeats(p)}" for i, p in enumerate(L2_SHORT)]),
                 ("C · Compare", [f"C{i + 1}: {cmp_sym(a, b)}" for i, (a, b) in enumerate(L2_CMP)]),
                 ("D · Is it 4 beats?", [f"D{i + 1}: {'YES' if nbeats(p) == 4 else 'NO'}" for i, p in enumerate(L2_CIRCLE)]),
                 ("E · Time signatures", [f"E{top_}/{bot}: {top_} beats, {sig_note(bot)}" for top_, bot in L2_SIGS]),
                 ("F · Beats per minute", [f"F{i + 1}: {a}" for i, (_, a) in enumerate(L2_WORDS)])]
    # Lessons 3 and 4
    rk = rank_of(L3_ORDER)
    tot, days, avg, longest, hit = journal_totals()
    k["key3"] = [("Lesson 3 · A · Multiple choice", [f"A{i + 1}: {lbl(c)}" for i, (_, _, c) in enumerate(L3_MC)]),
                 ("B · Who am I?", [f"B{i + 1}: {L3_MATCH[j][1].upper()}" for i, j in enumerate(L3_MATCH_ORDER)]),
                 ("C · Timeline math", [f"C{i + 1}: {a}" for i, (_, a) in enumerate(L3_MATH)]),
                 ("C6 · Order by birth year", [f"{nm}: {rk[nm]}" for nm in L3_ORDER]),
                 ("Lesson 4 · Match the strategy", [f"M{i + 1}: {lbl(k_)}" for i, k_ in enumerate(STRAT_ORDER)]),
                 ("Lesson 4 · Sample week", [f"J1: {tot}", f"J2: {days}", f"J3: {avg:.1f}", f"J4: {longest}", f"J5: {'YES' if hit else 'NO'}"])]
    # Lesson 5 and early finishers
    k["key4"] = [("Band zones", [f"Band {a}: {b}" for a, b, _ in BAND_ZONES]),
                 ("Orchestra zones", [f"Orch {a}: {b}" for a, b in ORCH_ZONES]),
                 ("A · Loudness order", [f"Symbol {d}: {1 + [x[0] for x in DYNAMICS].index(d)}" for d in DYN_SCRAMBLED]),
                 ("B · Terms", [f"T{i + 1}: {lbl(TERM_ORDER.index(i))}" for i in range(len(TERMS))]),
                 ("C · Who is who?", [f"W{i + 1}: {a}" for i, (_, a) in enumerate(CLOZE)]),
                 ("Early finishers", [f"S{i + 1}: {a}" for i, (_, a) in enumerate(SCRAMBLES)] + [f"R{i + 1}: {a}" for i, (_, a) in enumerate(RIDDLES)])]
    return k


KEY_TITLES = {"key1": ("Lesson 1 · Instrument Families and Care", "Lesson 1", "Sort and Match worksheet"),
              "key2": ("Lesson 2 · Rhythm and Note-Value Math", "Lesson 2", "Rhythm Math A, B and C"),
              "key3": ("Lessons 3 and 4 · Composers, Practice", "Lessons 3, 4", "Composers and Practice"),
              "key4": ("Lesson 5 and Early Finishers", "Lesson 5", "Seating, words, search")}
KEY_COLS = {"key1": [1, 3, 4, 3], "key2": [6, 6, 6, 4, 1, 5], "key3": [5, 4, 5, 4, 5, 5], "key4": [3, 4, 6, 5, 4, 4]}


def key_page(k, n, watermark=False):
    parts = ""
    for (head, items), cols in zip(key_items()[k], KEY_COLS[k]):
        cells = "".join(f'<div class="kc">{key_cell(it)}</div>' for it in items)
        parts += f'<div class="part" style="margin:8pt 0 3pt">{head}</div><div class="kg" style="grid-template-columns:repeat({cols},1fr)">{cells}</div>'
    extra = ""
    if k == "key4":
        extra = (f'<div class="cols" style="gap:14pt;margin-top:8pt;align-items:flex-start"><div style="flex:0 0 174pt">'
                 f'<div class="part" style="margin:0 0 3pt">Word search solution</div>{search_svg(True, 12)}</div>'
                 f'<div class="small" style="font-size:9pt !important;line-height:1.35">' +
                 "<br>".join(f"<b>{w}</b>: row {c[0][0] + 1}, column {c[0][1] + 1} to row {c[-1][0] + 1}, column {c[-1][1] + 1}" for w, c in SEARCH_SOL.items()) + "</div></div>")
    if k == "key3":
        extra = (f'<div class="small" style="margin-top:8pt;font-size:9.5pt !important">Lesson 4 reflection pages and the practice plan are the student’s own: accept any honest answer. '
                 f'Lesson 3 part D is open: accept any reason tied to the reading.</div>')
    if k == "key2":
        extra = (f'<div class="small" style="margin-top:8pt;font-size:9.5pt !important">Part F: 1 minute = 60 seconds. At 60 beats per minute each beat is 1 second; at 120 each beat is half a second. '
                 f'Beats = measures × 4. Accept 1 minute 36 seconds for F5.</div>')
    head, tagsub, _ = KEY_TITLES[k]
    return page(head, "ANSWER KEY", tagsub, f'<div class="how">Answers are printed in the accent color. Students may check their own work with a different color pen.</div>{parts}{extra}', n, watermark, ak=True, title="Answer Key")


def key_cell(it):
    lab, _, ans = it.partition(": ")
    return f'<span class="kl">{escape(lab)}</span> <span class="ans">{escape(ans)}</span>' if ans else escape(it)


def report_page(n, watermark=False):
    rows = "".join("<tr><td style='height:27pt'></td><td></td><td></td><td></td></tr>" for _ in range(6))
    inner = (f'<div class="how">Substitute: thank you! Please fill this in and leave it on the teacher’s desk.</div>'
             f'<div class="cols" style="gap:16pt"><div>{fl("Your name")}</div><div>{fl("Date")}</div></div>'
             f'<table class="t"><tr><th style="width:24%">Class / period</th><th style="width:12%">Lesson #</th><th style="width:30%">What we finished</th>'
             f'<th>Notes</th></tr>{rows}</table>'
             f'<div class="part">Students who were a big help<span class="acc"> ·</span></div><div class="ln2"></div><div class="ln2"></div>'
             f'<div class="part">Anything I should know?<span class="acc"> ·</span></div><div class="ln2"></div><div class="ln2"></div><div class="ln2"></div>'
             f'<div class="part">Games we played<span class="acc"> ·</span></div>'
             f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:4pt 14pt;font-size:11pt">'
             + "".join(f'<div>{checkbox(12)} &nbsp;{g}</div>' for g, _, _ in GAMES)
             + f'</div><div class="part">Copies left over<span class="acc"> ·</span></div><div class="ln2"></div>')
    return page("Sub report · notes for the director", "FOR THE SUB", "Leave on the desk", inner, n, watermark)


# ================================================================ TEACHER NOTES AND TERMS
PARTS = [  # (label, first key, last key, use)
    ("Cover and teacher notes", "cover", "teacher", "this page and how to use the packet"),
    ("For the substitute", "welcome", "glance", "welcome sheet, lessons at a glance, game bank"),
    ("Lesson 1 · Instrument Families and Care", "l1_plan", "l1_work", "plan, reading, sort and match"),
    ("Lesson 2 · Rhythm and Note-Value Math", "l2_plan", "l2_c", "plan and three engraved-rhythm worksheets"),
    ("Lesson 3 · Composers and Music History", "l3_plan", "l3_work", "plan, reading, questions and timeline math"),
    ("Lesson 4 · Practice Journal & Reflection", "l4_plan", "l4_reflect", "plan, strategies, journal, reflection"),
    ("Lesson 5 · Seating and Terminology Puzzle", "l5_plan", "l5_search", "plan, seating charts, terms, word search"),
    ("Early finishers", "early", "early", "scramble, riddles, concert program"),
    ("Answer keys", "key1", "key4", "every lesson, with the word search solution"),
    ("Sub report", "report", "report", "notes back to you"),
    ("Terms of use", "terms", "terms", "license and credits"),
]


def prange(a, b):
    return str(IX[a]) if a == b else f"{IX[a]}–{IX[b]}"


def part_pages(a, b):
    return IX[b] - IX[a] + 1


def teacher_page(n):
    trs = "".join(f"<tr><td><b>{a}</b></td><td style='white-space:nowrap'>{prange(f, l)}</td><td>{u}</td></tr>" for a, f, l, u in PARTS)
    return (f'<section class="page doc tn"><div class="rule"><h1>Teacher Notes</h1>'
            f'<div class="l" style="font-size:13pt">Band and Orchestra Emergency Sub Plans · 5 no-instrument lessons · grades 6–12</div></div>'
            f'<div class="cols"><div>'
            f'<h2>What it is</h2>'
            f'<p>Five complete lessons for the day you cannot be there. A substitute with no music background can run each one: every plan page has timed steps, words to say and a list of materials, '
            f'and every lesson ends with a printed answer key. No lesson needs an instrument, a recording or a screen, so the plans work in a band room, an orchestra room, a mixed class or a regular classroom.</p>'
            f'<h2>The five lessons</h2><ol>'
            + "".join(f"<li><b>{escape(d['title'])}</b>: {d['skill'][0].lower() + d['skill'][1:]}.</li>" for d in LESSONS) +
            f'</ol><p>Each lesson fills one 40–45 minute class. Use them in any order; each stands alone. If you will be out several days, use the welcome sheet’s “Lesson #” column so the sub gives each class a new lesson.</p>'
            f'<h2>Set up the sub folder (about 15 minutes, once)</h2><ol>'
            f'<li>Fill in the welcome sheet (page {IX["welcome"]}).</li>'
            f'<li>Print the plan and student pages for the lessons you want, one copy of each plan for the sub and a class set of each student page.</li>'
            f'<li>Keep the answer keys and the sub report in the folder.</li></ol>'
            f'<h2>Levels</h2><p>Grades 6–8: read aloud together. Grades 9–12: students can read silently and work alone.</p>'
            f'</div><div>'
            f'<h2>What’s inside ({len(PLAN)} pages)</h2><table class="t"><tr><th>Part</th><th>Pages</th><th>Use</th></tr>{trs}</table>'
            f'<h2>About the music content</h2>'
            f'<p>Rhythms are in 4/4 and use whole, half and quarter notes, paired eighth notes and quarter rests, engraved with a professional music font. '
            f'Every engraved rhythm was read back from its drawing and checked against the data, and every answer in the keys was computed from the same data.</p>'
            f'<p>The history reading uses only well-documented facts, and the seating charts show the common layout (your ensemble may differ).</p>'
            f'<h2>Standards</h2><p>Supports reading and counting rhythm (MU:Pr4.2), evaluating and refining personal and ensemble performance (MU:Pr5.1) and connecting music to history and culture (MU:Cn11.0), '
            f'National Core Arts Standards, Music (ensemble strand), grades 6–12.</p>'
            f'<p>Prints well in black and white. Nothing is dated or seasonal.</p>'
            f'<p class="small">All lessons, readings, games, puzzles and art are original. No songs, lyrics or copyrighted characters are used.</p>'
            f'</div></div><div style="flex:1"></div>{foot(f"Page {n}")}</section>')


def terms_page(n):
    return (f'<section class="page doc"><div class="rule"><h1>Terms of Use</h1>'
            f'<div class="l" style="font-size:13pt">Thank you for your purchase!</div></div>'
            f'<p>© {YEAR} {STORE}. {BRAND} by {STORE}. All rights reserved. This purchase gives <b>one teacher</b> a license to use this resource with their own students.</p>'
            f'<h2>You may</h2><ul><li>Print and copy pages for your own classroom and students, year after year.</li>'
            f'<li>Share pages with your own students through a password-protected class site or learning platform.</li>'
            f'<li>Leave the pages for a substitute teacher who teaches your own students.</li></ul>'
            f'<h2>You may not</h2><ul><li>Share, email or copy this resource for other teachers, a whole school or a district. '
            f'Additional licenses are available on Teachers Pay Teachers.</li>'
            f'<li>Post any part of it on a public website, shared drive or social media.</li>'
            f'<li>Sell, give away or claim any part of it as your own, or edit it into a new product.</li></ul>'
            f'<h2>Questions?</h2><p>Please use the Q&amp;A tab on the {BRAND} by {STORE} store on Teachers Pay Teachers. '
            f'If something looks wrong, let me know there and I will fix it.</p>'
            f'<h2>Credits</h2><ul>'
            f'<li>Lessons, readings, puzzles, games, art and layouts: original work, {BRAND} by {STORE}.</li>'
            f'<li>Music notation font: Bravura © Steinberg Media Technologies GmbH, SIL Open Font License 1.1.</li>'
            f'<li>Text fonts: Oswald (The Oswald Project Authors) and Source Sans 3 (Adobe), SIL Open Font License 1.1.</li></ul>'
            f'<p class="small">{DISCLOSURE}</p>'
            f'<div style="flex:1"></div>{foot(f"Page {n}")}</section>')


# ================================================================ COVER ART (accent + black only)
def violin_svg(cx, cy, rot):
    body = ("M0 -34 C34 -34 40 -12 24 -2 C13 6 15 12 30 22 C52 44 42 78 0 78 C-42 78 -52 44 -30 22 C-15 12 -13 6 -24 -2 C-40 -12 -34 -34 0 -34 Z")
    return (f'<g transform="translate({cx} {cy}) rotate({rot})">'
            f'<rect x="-5" y="-100" width="10" height="68" fill="#000"/>'
            f'<path d="M-6 -100 C-12 -108 -4 -118 2 -112 C6 -108 4 -102 0 -102" fill="none" stroke="#000" stroke-width="3.4" stroke-linecap="round"/>'
            f'<path d="{body}" fill="{ACCENT}" stroke="#000" stroke-width="3.4" stroke-linejoin="round"/>'
            f'<path d="M-24 8 C-18 -2 -14 6 -18 14 M24 8 C18 -2 14 6 18 14" fill="none" stroke="#000" stroke-width="2.4" stroke-linecap="round" transform="translate(0 6)"/>'
            f'<path d="M-15 12 q-2 12 5 22 M15 12 q2 12 -5 22" fill="none" stroke="#000" stroke-width="3" stroke-linecap="round"/>'
            f'<line x1="-12" y1="40" x2="12" y2="40" stroke="#fff" stroke-width="3.4" stroke-linecap="round"/>'
            f'<path d="M-6 56 L6 56 L4 74 L-4 74 Z" fill="#000"/>'
            f'<line x1="-2" y1="-98" x2="-2" y2="56" stroke="#fff" stroke-width="1.2"/><line x1="2" y1="-98" x2="2" y2="56" stroke="#fff" stroke-width="1.2"/>'
            f'<line x1="-72" y1="-20" x2="80" y2="100" stroke="#000" stroke-width="3.4" stroke-linecap="round"/>'
            f'<rect x="-86" y="-30" width="22" height="9" rx="2" fill="#fff" stroke="#000" stroke-width="2.6" transform="rotate(39 -75 -25)"/></g>')


def snare_svg(cx, cy):
    out = [f'<path d="M{cx - 66} {cy} L{cx - 66} {cy + 62} A66 18 0 0 0 {cx + 66} {cy + 62} L{cx + 66} {cy} Z" fill="#fff" stroke="#000" stroke-width="3.4" stroke-linejoin="round"/>',
           f'<path d="M{cx - 66} {cy + 14} L{cx - 66} {cy + 24} A66 18 0 0 0 {cx + 66} {cy + 24} L{cx + 66} {cy + 14} A66 18 0 0 1 {cx - 66} {cy + 14} Z" fill="{ACCENT}"/>',
           f'<path d="M{cx - 66} {cy + 36} L{cx - 66} {cy + 46} A66 18 0 0 0 {cx + 66} {cy + 46} L{cx + 66} {cy + 36} A66 18 0 0 1 {cx - 66} {cy + 36} Z" fill="{ACCENT}"/>']
    for i in range(-5, 6):
        x = cx + i * 11
        out.append(f'<path d="M{x} {cy + 2} L{x + 5} {cy + 30} L{x + 10} {cy + 56}" fill="none" stroke="#000" stroke-width="1.3" opacity=".5"/>')
    out.append(f'<ellipse cx="{cx}" cy="{cy}" rx="66" ry="18" fill="#fff" stroke="#000" stroke-width="3.4"/>')
    out.append(f'<line x1="{cx - 44}" y1="{cy - 78}" x2="{cx + 8}" y2="{cy - 2}" stroke="#000" stroke-width="5" stroke-linecap="round"/>')
    out.append(f'<line x1="{cx + 48}" y1="{cy - 78}" x2="{cx - 4}" y2="{cy - 2}" stroke="#000" stroke-width="5" stroke-linecap="round"/>')
    out.append(f'<circle cx="{cx - 44}" cy="{cy - 78}" r="6.5" fill="{ACCENT}" stroke="#000" stroke-width="2.6"/>')
    out.append(f'<circle cx="{cx + 48}" cy="{cy - 78}" r="6.5" fill="{ACCENT}" stroke="#000" stroke-width="2.6"/>')
    return "".join(out)


COVER_STRIP = "qeqr"


def hero_svg(width_css):
    st, end = rhythm_svg("eeqr", 0, 0, 6, 27, syl=True, syl_size=10)
    strip = f'<g transform="translate({300 - end / 2:.1f} 118)">{st}</g>'
    stand = (f'<rect x="190" y="22" width="220" height="250" rx="6" fill="#fff" stroke="#000" stroke-width="3.4"/>'
             f'<rect x="212" y="42" width="176" height="12" rx="2" fill="#000"/>'
             f'<rect x="212" y="62" width="120" height="6" rx="2" fill="{TINT1}"/>'
             + "".join(f'<rect x="212" y="{y}" width="{w}" height="6" rx="2" fill="#000" opacity=".28"/>' for y, w in ((176, 170), (192, 150), (208, 176), (224, 120), (240, 160))) +
             f'<path d="M168 272 L432 272 L420 292 L180 292 Z" fill="{ACCENT}" stroke="#000" stroke-width="3.4" stroke-linejoin="round"/>'
             f'<line x1="300" y1="292" x2="300" y2="380" stroke="#000" stroke-width="5"/>'
             f'<path d="M300 380 L252 420 M300 380 L348 420 M300 380 L300 422" fill="none" stroke="#000" stroke-width="5" stroke-linecap="round"/>')
    baton = (f'<line x1="430" y1="402" x2="578" y2="356" stroke="#000" stroke-width="3.2" stroke-linecap="round"/>'
             f'<circle cx="426" cy="403" r="8" fill="{ACCENT}" stroke="#000" stroke-width="2.4"/>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 430" width="{width_css}" style="display:block">'
            f'{stand}{strip}{violin_svg(92, 240, -10)}{snare_svg(506, 250)}{baton}</svg>')


def cover_page():
    return (f'<section class="page cover"><div class="store">{BRAND}</div>'
            f'<div style="width:6.9in">{hero_svg("100%")}</div>'
            f'<div class="ctitle"><div class="a">BAND &amp; ORCHESTRA</div><div class="b">SUB PLANS</div>'
            f'<div class="c">5 no-instrument lessons · readings · worksheets · answer keys</div></div>'
            f'<div class="cband">Grades 6–12 <em>·</em> 5 lessons <em>·</em> {len(PLAN)} pages</div></section>')


# ================================================================ ASSEMBLE
def render_page(key, watermark=False):
    n = IX[key]
    m = re.match(r"l(\d)_plan$", key)
    if m:
        return plan_page(LESSONS[int(m.group(1)) - 1], n, watermark)
    if key.startswith("key"):
        return key_page(key, n, watermark)
    return {
        "cover": cover_page, "teacher": lambda: teacher_page(n), "welcome": lambda: welcome_page(n, watermark),
        "glance": lambda: glance_page(n, watermark),
        "l1_read": lambda: l1_read(n, watermark), "l1_work": lambda: l1_work(n, watermark),
        "l2_a": lambda: l2_a(n, watermark), "l2_b": lambda: l2_b(n, watermark), "l2_c": lambda: l2_c(n, watermark),
        "l3_read": lambda: l3_read(n, watermark), "l3_work": lambda: l3_work(n, watermark),
        "l4_read": lambda: l4_read(n, watermark), "l4_journal": lambda: l4_journal(n, watermark), "l4_reflect": lambda: l4_reflect(n, watermark),
        "l5_seat": lambda: l5_seat(n, watermark), "l5_terms": lambda: l5_terms(n, watermark), "l5_search": lambda: l5_search(n, watermark),
        "early": lambda: early_page(n, watermark), "report": lambda: report_page(n, watermark), "terms": lambda: terms_page(n),
    }[key]()


PREVIEW_PICKS = ["l1_plan", "l2_a", "l5_seat", "key2"]


def preview_pages():
    return [render_page(p, watermark=True) for p in PREVIEW_PICKS]


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


def pdf_png(src, page_no, out, res=110):
    subprocess.run(["pdftoppm", "-png", "-r", str(res), "-f", str(page_no), "-l", str(page_no), "-singlefile", src,
                    os.path.join(BUILD, out)], check=True)




# ================================================================ SQUARE IMAGES (2000 x 2000)
PAGE_RATIO = 11 / 8.5
BAND_TOP = 1000 - 62          # the black band is ~62px tall; nothing may reach it (shot + border + shadow + label)
# (top of shots, shot width, label height, extra for shadow/border) per preview image: asserted in verify_data
SQ_LAYOUT = {"p1": (253, 290, 64), "p2": (300, 450, 0), "p3": (205, 196, 28)}


def sq_bottom(key, rows=1):
    top, w, lab = SQ_LAYOUT[key]
    return top + rows * (w * PAGE_RATIO + 4 + 8 + lab) + (rows - 1) * 22


def cover_square():
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div>'
        f'<div style="width:690px;margin-top:14px">{hero_svg("100%")}</div>'
        f'<div class="hd" style="font-size:70px;margin-top:6px">Band &amp; Orchestra</div>'
        f'<div class="hd" style="font-size:150px">Sub Plans</div>'
        f'<div class="sub" style="font-size:29px;margin-top:10px">5 no-instrument lessons · readings · worksheets · answer keys</div>'
        f'<div class="band">Grades 6–12 <em>·</em> 5 lessons <em>·</em> {len(PLAN)} pages</div></div>')


def preview_square_1(img):
    items = [(img[0], "Lesson plan", "timed steps, words to say"), (img[1], "Rhythm math", "engraved notes, key included"),
             (img[2], "Seating charts", "band and orchestra")]
    shots = "".join(
        f'<div style="width:{SQ_LAYOUT["p1"][1]}px"><div class="shot"><img src="{src}"><div class="swm" style="font-size:64px">PREVIEW</div></div>'
        f'<div class="lbl">{a}<span>{b}</span></div></div>' for src, a, b in items)
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div>'
        f'<div class="hd" style="font-size:74px;margin-top:20px">Any sub can run it</div>'
        f'<div class="sub" style="font-size:27px;margin-top:8px">No music background, no instruments, no audio, no screens</div>'
        f'<div style="display:flex;gap:28px;margin-top:{SQ_LAYOUT["p1"][0] - 193}px;align-items:flex-start">{shots}</div>'
        f'<div class="band">Band <em>·</em> orchestra <em>·</em> mixed classes <em>·</em> grades 6–12</div></div>')


def preview_square_2(a, b):
    w = SQ_LAYOUT["p2"][1]
    pair = "".join(
        f'<div style="position:absolute;left:{x}px;top:{y}px;width:{w}px"><div class="shot"><img src="{src}">'
        f'<div class="swm" style="font-size:96px">PREVIEW</div></div>'
        f'<div class="lbl" style="position:absolute;{side}:-2px;top:-40px;margin:0">{lab}</div></div>'
        for src, lab, x, y, side in ((a, "Reading page", 60, SQ_LAYOUT["p2"][0] - 20, "left"), (b, "Questions", 490, SQ_LAYOUT["p2"][0] + 20, "right")))
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div>'
        f'<div class="hd" style="font-size:72px;margin-top:20px">Readings with questions</div>'
        f'<div class="sub" style="font-size:27px;margin-top:8px">Composer facts, timeline math and a printed key</div>'
        f'{pair}'
        f'<div class="band">Reading <em>·</em> comprehension <em>·</em> timeline math <em>·</em> answer key</div></div>')


def preview_square_3(imgs):
    w = SQ_LAYOUT["p3"][1]
    cells = "".join(
        f'<div style="width:{w}px"><div class="shot" style="box-shadow:5px 5px 0 #000"><img src="{src}">'
        f'<div class="swm" style="font-size:44px">PREVIEW</div></div><div class="lbl" style="font-size:17px;margin-top:9px">{lab}</div></div>'
        for src, lab in imgs)
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div>'
        f'<div class="hd" style="font-size:70px;margin-top:16px">Everything inside</div>'
        f'<div class="sub" style="font-size:27px;margin-top:8px">5 plans, readings, worksheets, puzzles, keys and a sub report</div>'
        f'<div style="display:grid;grid-template-columns:repeat(4,{w}px);gap:22px 26px;margin-top:{SQ_LAYOUT["p3"][0] - 168}px">{cells}</div>'
        f'<div class="band">{len(PLAN)} pages <em>·</em> US Letter PDF <em>·</em> prints in black &amp; white</div></div>')


SHOTS1 = ["l1_plan", "l2_a", "l5_seat"]
SHOTS2 = ["l3_read", "l3_work"]
SHOTS3 = [("welcome", "Welcome sheet"), ("l1_work", "Sort and match"), ("l2_b", "Rhythm math B"), ("l4_journal", "Practice journal"),
          ("l5_search", "Word search"), ("early", "Early finishers"), ("key3", "Answer key"), ("report", "Sub report")]


def tpt_json(pages):
    return {
        "price": PRICE, "license_price": PRICE,
        "tax_code": "Other Digital Goods - No Physical Media",
        "grades": ["6th-grade", "8th-grade", "10th-grade", "12th-grade"],
        "subjects": ["Music", "Instrumental Music"],
        "tags": ["Worksheets", "Lessons", "Printables", "Activities", "Handouts", "Classroom Management"],
        "formats": ["PDF"],
        "pages": pages,
        "answer_key": "Included",
        "files": {"product": f"{SLUG}.pdf", "preview": f"{SLUG}-PREVIEW.pdf", "thumb1": "cover.png",
                  "thumb2": "preview-1.png", "thumb3": "preview-2.png", "thumb4": "preview-3.png"},
    }


UPLOAD_TITLE = "Band and Orchestra Sub Plans | 5 No-Prep Lessons, Worksheets & Keys, Gr 6-12"


def upload_md(pages):
    plist = "\n".join(f"• {a}: {part_pages(f, l)} page{'s' if part_pages(f, l) > 1 else ''} ({use})" for a, f, l, use in PARTS)
    total = sum(part_pages(f, l) for _, f, l, _ in PARTS)
    lessons = "\n".join(f"• Lesson {d['n']}, {d['title']}: {d['skill'][0].lower() + d['skill'][1:]}" for d in LESSONS)
    desc = f"""Emergency sub plans for band and orchestra, grades 6–12, that a substitute with no music background can run. Five complete lessons, each with a plan page (timed steps, words the sub can read aloud, materials), a reading or worksheet, and a printed answer key. No instruments, no audio and no screens are needed, so the plans work in a band room, an orchestra room, a mixed class or any classroom.

WHAT'S INCLUDED ({pages} pages, PDF, US Letter)
{plist}
Total: {total} pages

THE FIVE LESSONS (each about 40–45 minutes)
{lessons}

WHY IT WORKS FOR SUBS
• Every plan has timed steps and “say this” scripts, so a sub can run it cold
• Instruments stay in their cases: no playing, no equipment, no recordings
• Lessons work in any order and each stands alone, so a multi-day absence is covered
• Welcome sheet to fill in once, a game bank of 6 no-prep games, and a sub report for notes back to you
• Each lesson has a short-class option and an extra-time option

ACCURATE BY DESIGN
• Rhythms are engraved with a professional music font in 4/4; every rhythm was read back by computer and every answer in the keys was computed from the same data
• The composer reading uses only well-documented facts, and era dates are marked as rough
• The word search is solved by computer: every word is in the grid exactly once
• Seating charts show the common layout, and the page tells students their own ensemble may differ

• Grades 6–12; works for band, orchestra, jazz band or mixed ensemble classes
• Prints well in black and white
• Nothing seasonal, so it works any week of the year
• All lessons, readings, puzzles and art are original. No songs, lyrics or copyrighted characters

{DISCLOSURE}"""
    return f"""# UPLOAD: Band and Orchestra Emergency Sub Plans, 5 No-Instrument Lessons, Grades 6–12 (TpT 041)

These fields follow the order of TpT's "Add a resource" form. `tools/tpt.js publish` reads the title and description from the code blocks under 1 and 2, and everything else from `tpt.json`. This file is written by `gen.py`.

**Files to attach**
- Resource (digital download): `{SLUG}.pdf`, {pages} pages, US Letter portrait.
- Thumbnails, in this order: `cover.png`, `preview-1.png`, `preview-2.png`, `preview-3.png` (all 2000 × 2000).
- Preview file: `{SLUG}-PREVIEW.pdf`, 4 watermarked pages.

## 1. Title

```
{UPLOAD_TITLE}
```
({len(UPLOAD_TITLE)} characters; the limit is 80.)

## 2. Description

```
{desc}
```

## 3. Grades

6th, 8th, 10th and 12th (`6th-grade`, `8th-grade`, `10th-grade`, `12th-grade` in tpt.json): TpT allows 4 grades, so these four mark both ends of 6–12 and the middle-school / high-school split.

## 4. Subjects

Music, Instrumental Music. (Both are real entries, not headings.)

## 5. Tags

Worksheets, Lessons, Printables, Activities, Handouts, Classroom Management. (None is a heading in `tpt/TAG-OPTIONS.json`.)

## 6. Price

${PRICE} (single license; multiple-license price the same in tpt.json).

## 7. Page count and contents ({pages} pages, adds up to the PDF)

{plist}

Total: {total} pages

## 8. Preview PDF

`{SLUG}-PREVIEW.pdf`: 4 watermarked pages (Lesson 1 plan, Rhythm Math A, Seating Charts, Lesson 2 answer key).
"""


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
    with open(UPLOAD, "w") as f:
        f.write(upload_md(len(PLAN)))
    print(f"built {PDF} ({len(PLAN)} pages), {PREVIEW_PDF}, cover + 3 previews, tpt.json, UPLOAD.md" + (" [LOW RES]" if LOW_RES else ""))


# ================================================================ CHECKS
from fractions import Fraction

DUR = {"w": Fraction(1), "h": Fraction(1, 2), "q": Fraction(1, 4), "e": Fraction(2, 8), "r": Fraction(1, 4)}   # fractions of a whole note (independent of BEATS)


def beats_by_fraction(p):
    return sum(DUR[t] for t in p if t != "|") * 4


def perm(lst, n):
    return sorted(lst) == list(range(n))


def zones_overlap(a, b):
    return not (a[1] <= b[0] or b[1] <= a[0]) and not (a[3] <= b[2] or b[3] <= a[2])


def verify_data():
    errs = []
    # 1. every engraved rhythm reads back from its drawn SVG; beats agree with an independent fraction calculation
    for i, p in enumerate(L2_SHORT):
        errs += rhythm_check(f"L2 B{i + 1}", p, s=6, W=28, four=False)
    for i, p in enumerate(L2_CIRCLE):
        errs += rhythm_check(f"L2 D{i + 1}", p, s=5.6, W=22, timesig=False, four=False)
    errs += rhythm_check("cover strip", "eeqr", s=6, W=27)
    errs += rhythm_check("cover fan", "eeqr", s=6, W=27)
    for t in "qerhw":
        st = tok_svg(t, 50, 40, 7, 40) + '<line class="bar" x1="80" y1="0" x2="80" y2="1"/><rect class="fin"/>'
        got, e = read_rhythm(st, 7, 40, 50 - 20, timesig=False)
        if got.replace("|", "") != t:
            errs.append(f"single glyph {t} reads back as {got}")
    for p in L2_ADD + L2_SHORT + L2_CIRCLE + [x for pr in L2_CMP for x in pr]:
        if beats_by_fraction(p) != nbeats(p):
            errs.append(f"beats of {p}: table says {nbeats(p)}, note-value fractions say {beats_by_fraction(p)}")
    for p in L2_ADD:
        if not 2 <= len(p) <= 3:
            errs.append(f"L2 add item {p} length")
    for p in L2_SHORT:
        if not 1 <= nbeats(p) <= 3:
            errs.append(f"L2 short bar {p} has {nbeats(p)} beats; must be 1-3")
    yes = sum(nbeats(p) == 4 for p in L2_CIRCLE)
    if yes < 3 or len(L2_CIRCLE) - yes < 3:
        errs.append("L2 part D should have at least 3 YES and 3 NO bars")
    if sorted(cmp_sym(a, b) for a, b in L2_CMP).count("=") < 2 or {cmp_sym(a, b) for a, b in L2_CMP} != {"<", "=", ">"}:
        errs.append("L2 part C should use <, = and >")
    if [a for _, a in L2_WORDS] != ["128", "1", "4", "60", "96"]:
        errs.append(f"L2 word problem answers changed: {[a for _, a in L2_WORDS]}")
    if [(t, b, sig_note(b), sig_beats_value(b)) for t, b in L2_SIGS] != [(3, 4, "quarter note", 1), (2, 4, "quarter note", 1), (2, 2, "half note", 2), (4, 4, "quarter note", 1)]:
        errs.append("time-signature table changed")
    # 2. Lesson 1: sort, match, true/false, multiple choice
    if sorted(SORT_BANK) != sorted(i for lst in FAMILIES.values() for i in lst) or len(set(SORT_BANK)) != len(SORT_BANK):
        errs.append("L1 sort bank is not exactly the instruments in the family lists")
    if FAMILY_OF.get("saxophone") != "Woodwinds" or FAMILY_OF.get("timpani") != "Percussion" or FAMILY_OF.get("double bass") != "Strings":
        errs.append("L1 family facts wrong")
    if not perm(SOUND_ORDER, len(SOUND_MATCH)):
        errs.append("L1 match order is not a permutation")
    if sum(a for _, a in CARE_TF) != 3 or len(CARE_TF) != 6:
        errs.append("L1 care true/false should be 4 true, 4 false")
    for label, mcs in (("L1", L1_MC), ("L3", L3_MC)):
        for i, (q, o, c) in enumerate(mcs):
            if len(o) != 4 or len(set(o)) != 4 or not 0 <= c < 4:
                errs.append(f"{label} MC {i + 1}: options/answer invalid")
    for i, (q, o, c) in enumerate(L3_MC):
        want = ["Sousa", "Mozart", "Beethoven", "Baroque", "John Philip Sousa"][i]
        if o[c] != want:
            errs.append(f"L3 MC {i + 1}: answer is {o[c]}, expected {want}")
    if [o[c] for _, o, c in L1_MC] != ["how they make sound", "uses a reed", "buzzing their lips", "Strings", "can be tuned to different pitches"]:
        errs.append("L1 MC answers changed")
    # key item counts must equal worksheet question counts, every lesson
    ws = {"key1": [len(FAMILIES), len(SOUND_MATCH), len(CARE_TF), N_L1_MC],
          "key2": [len(L2_ADD), len(L2_SHORT), len(L2_CMP), len(L2_CIRCLE), len(L2_SIGS), len(L2_WORDS)],
          "key3": [len(L3_MC), len(L3_MATCH_ORDER), len(L3_MATH), len(L3_ORDER), len(STRAT), 5],
          "key4": [len(BAND_ZONES), len(ORCH_ZONES), len(DYN_SCRAMBLED), len(TERMS), len(CLOZE), len(SCRAMBLES) + len(RIDDLES)]}
    for kk, secs in key_items().items():
        for j, (head, items) in enumerate(secs):
            want = ws.get(kk, [])[j] if j < len(ws.get(kk, [])) else None
            if want is not None and len(items) != want:
                errs.append(f"{kk} '{head}': key has {len(items)} items but worksheet has {want} questions")
    # 3. Lesson 3: dates and arithmetic against literal facts
    if COMP != {"Bach": (1685, 1750), "Mozart": (1756, 1791), "Beethoven": (1770, 1827), "Sousa": (1854, 1932)}:
        errs.append("composer dates changed")
    if SYM9 != 1824 or STARS != 1896:
        errs.append("Symphony 9 / Stars and Stripes dates changed")
    if [a for _, a in L3_MATH] != [71, 6, 14, 72, 1756]:
        errs.append(f"L3 math answers: {[a for _, a in L3_MATH]}")
    if 1791 - 1756 != 35:
        errs.append("Mozart age")
    if L3_ORDER_ANS != ["Bach", "Mozart", "Beethoven", "Sousa"] or set(L3_ORDER) != set(COMP):
        errs.append("L3 order answer")
    if not perm(L3_MATCH_ORDER, 4) or sorted(c for _, c in L3_MATCH) != sorted(COMP):
        errs.append("L3 match")
    txt = " ".join(t for *_, t in L3_READ)
    for needle in ("1721", "1723", "35", "1824", "1880", "1892", "1896", "1987", "600"):
        if needle not in txt:
            errs.append(f"L3 reading lacks fact '{needle}'")
    for full, short, yrs, era, t in L3_READ:
        b, d = COMP[short]
        if yrs != f"{b}–{d}":
            errs.append(f"L3 reading header years for {short}: {yrs}")
    # 4. Lesson 4
    if journal_totals() != (105, 6, 17.5, "Sat", True):
        errs.append(f"journal totals: {journal_totals()}")
    if not perm(STRAT_ORDER, len(STRAT)) or len(STRAT) != len(L4_STRATS):
        errs.append("L4 strategy match")
    want_l4 = {"The same hard spot goes wrong every time I play.": "Isolate the hard spot",
               "I speed up whenever the notes get fast.": "Use a steady beat",
               "I can play the first line, but I fall apart when I try the full page.": "Work in small chunks",
               "I forget where I made mistakes.": "Mark your music",
               "My practice time feels random and goes nowhere.": "Set one goal"}
    if {p: L4_STRATS[i][0] for i, (p, _) in enumerate(STRAT)} != want_l4:
        errs.append("L4 problem-to-strategy mapping changed")
    # the key must print, for each printed item, the letter of its intended strategy (letters follow L4_STRATS order)
    l4_key = [x for h, xs in key_items()["key3"] if h == "Lesson 4 · Match the strategy" for x in xs]
    l4_want = [f"M{i + 1}: {lbl([h for h, _ in L4_STRATS].index(want_l4[STRAT[k][0]]))}" for i, k in enumerate(STRAT_ORDER)]
    if l4_key != l4_want or l4_want != ["M1: D", "M2: A", "M3: E", "M4: C", "M5: B"]:
        errs.append(f"L4 key {l4_key} != worksheet mapping {l4_want}")
    # no item may echo another strategy's wording
    import re as _re
    for p, _ in STRAT:
        for h, t in L4_STRATS:
            if h != want_l4[p] and any(w in p.lower() for w in ("chunk", "metronome", "goal", "circle", "pencil", "whole piece", "measure")):
                errs.append(f"L4 item echoes strategy wording: {p}")
    # 5. Lesson 5
    if {z for z in BAND_GEOM} != {a for a, _, _ in BAND_ZONES} or {z for z in ORCH_GEOM} != {a for a, _ in ORCH_ZONES}:
        errs.append("seating zones do not match geometry")
    if sorted(ZONE_BANK_BAND) != sorted(b for _, b, _ in BAND_ZONES) or sorted(ZONE_BANK_ORCH) != sorted(b for _, b in ORCH_ZONES):
        errs.append("seating word banks do not match the zone names")
    for nm, geom in (("band", BAND_GEOM), ("orchestra", ORCH_GEOM)):
        keys = list(geom)
        for i in range(len(keys)):
            for j in range(i + 1, len(keys)):
                if zones_overlap(geom[keys[i]], geom[keys[j]]):
                    errs.append(f"{nm} seating zones {keys[i]} and {keys[j]} overlap")
    if not (perm(TERM_ORDER, len(TERMS)) and sorted(DYN_SCRAMBLED) == sorted(d for d, _, _ in DYNAMICS) and DYN_SCRAMBLED != [d for d, _, _ in DYNAMICS]):
        errs.append("L5 term/dynamics orders")
    if [d for d, _, _ in DYNAMICS] != ["pp", "p", "mp", "mf", "f", "ff"] or [n_ for _, n_, _ in DYNAMICS] != ["pianissimo", "piano", "mezzo piano", "mezzo forte", "forte", "fortissimo"]:
        errs.append("dynamics table")
    if sorted(CLOZE_BANK) != sorted(a for _, a in CLOZE):
        errs.append("cloze bank")
    for w in SEARCH_WORDS:
        hits = find_all(SEARCH, w)
        if len(hits) != 1:
            errs.append(f"word search: {w} appears {len(hits)} times")
    if len(set(SEARCH_WORDS)) != len(SEARCH_WORDS) or any(len(r) != GRID_N for r in SEARCH) or len(SEARCH) != GRID_N:
        errs.append("word search shape")
    # 6. early finishers
    for sc, w in SCRAMBLES:
        if sorted(sc) != sorted(w) or sc == w:
            errs.append(f"scramble {sc} is not a scramble of {w}")
    ans = {a for _, a in RIDDLES}
    if ans != {"double bass", "trombone", "timpani", "violin", "saxophone"} or any(FAMILY_OF[a] == "" for a in ans):
        errs.append("riddles")
    # 7. layout and plan
    if len(PLAN) != len(set(PLAN)):
        errs.append("plan has a repeated page")
    covered = []
    for _, a, b, _ in PARTS:
        covered += PLAN[IX[a] - 1:IX[b]]
    if sorted(covered) != sorted(PLAN):
        errs.append(f"PARTS pages do not cover the plan exactly once: {sorted(set(PLAN) ^ set(covered))}")
    for d in LESSONS:
        t = sum(int(m) for m, _, _ in d["steps"])
        if not 30 <= t <= 45:
            errs.append(f"Lesson {d['n']} steps add to {t} min, not 30-45")
    if len(UPLOAD_TITLE) > 80:
        errs.append(f"title is {len(UPLOAD_TITLE)} chars")
    if sq_bottom("p1") > BAND_TOP - 10 or sq_bottom("p3", 2) > BAND_TOP - 10 or SQ_LAYOUT["p2"][0] + 20 + SQ_LAYOUT["p2"][1] * PAGE_RATIO + 12 > BAND_TOP - 10:
        errs.append("preview PNG layout: page shots would reach the black band")
    return errs


def pdf_fonts(path):
    out = subprocess.run(["pdffonts", path], capture_output=True, text=True, check=True).stdout.splitlines()[2:]
    return [(ln.split()[0], ln.split()[-5]) for ln in out]


def footer_errors(path, safe=0.35 * 72):
    out = subprocess.run(["pdftotext", "-bbox", path, "-"], capture_output=True, text=True, check=True).stdout
    errs = []
    for i, pg_ in enumerate(re.findall(r'<page width="([\d.]+)" height="([\d.]+)">(.*?)</page>', out, re.S)):
        ph = float(pg_[1])
        ys = [float(m) for m in re.findall(r'yMax="([\d.]+)">Lotze', pg_[2])]
        if i == 0 and not ys:
            continue
        if not ys:
            errs.append(f"{os.path.basename(path)} p{i + 1}: footer not found on the page")
        elif max(ys) > ph - safe:
            errs.append(f"{os.path.basename(path)} p{i + 1}: footer ends {ph - max(ys):.1f}pt from the bottom edge (< {safe:.0f}pt)")
    return errs


def overflow_errors(path):
    """No text on a page may sit below the footer rule: any word whose yMax passes the footer's yMin (other than the footer itself) is a collision."""
    out = subprocess.run(["pdftotext", "-bbox", path, "-"], capture_output=True, text=True, check=True).stdout
    errs = []
    for i, pg_ in enumerate(re.findall(r'<page width="([\d.]+)" height="([\d.]+)">(.*?)</page>', out, re.S)):
        words = re.findall(r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">(.*?)</word>', pg_[2])
        foot_y = [float(w[1]) for w in words if w[4] in ("©",) or w[4] == "Lotze"]
        if not foot_y:
            continue
        fy = min(foot_y)
        for x0, y0, x1, y1, t in words:
            if float(y1) > fy + 0.5 and float(y0) < fy - 1 and t not in ("©",):
                errs.append(f"{os.path.basename(path)} p{i + 1}: text '{t}' runs into the footer")
                break
    return errs


def key_text_errors(flat):
    errs = []
    for k, secs in key_items().items():
        t = flat[IX[k] - 1]
        for head, items in secs:
            for it in items:
                if re.sub(r"\s+", " ", it.replace(": ", " ")) not in t:
                    errs.append(f"{k}: key item '{it}' not found in the PDF text")
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
        for i, pg_ in enumerate(rd.pages):
            w, h = float(pg_.mediabox.width), float(pg_.mediabox.height)
            if abs(w - 612) > 1 or abs(h - 792) > 1:
                errs.append(f"{os.path.basename(path)} p{i + 1}: {w:.0f}x{h:.0f}pt, not US Letter")
        errs += footer_errors(path)
        errs += overflow_errors(path)
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
        if i > 0 and not re.search(rf"Page {i + 1}\s*$", t.strip()):
            errs.append(f"page {i + 1}: page number in the footer is wrong")
    errs += key_text_errors(flat)
    alltext = " ".join(flat).lower()
    for bad in BANNED:
        if re.search(rf"\b{bad}\b", alltext):
            errs.append(f"resource text mentions '{bad}'")
    if str(len(PLAN)) + " pages" not in flat[0].lower():
        errs.append("cover band page count differs from the PDF")
    for m in re.finditer(r"[Pp]ages? (\d+)(?:–(\d+))?", " ".join(flat[1:])):
        for g in m.groups():
            if g and not 1 <= int(g) <= len(PLAN):
                errs.append(f"cross-reference to page {g} does not exist")
    for d in LESSONS:   # each plan names its student pages and the right key
        k = d["n"]
        pl = flat[IX[f"l{k}_plan"] - 1]
        need = {1: ["l1_read", "l1_work", "key1"], 2: ["l2_a", "l2_b", "l2_c", "key2"], 3: ["l3_read", "l3_work", "key3"],
                4: ["l4_read", "l4_journal", "l4_reflect", "key3"], 5: ["l5_seat", "l5_terms", "l5_search"]}[k]
        for key in need:
            if f"page {IX[key]}" not in pl:
                errs.append(f"Lesson {k} plan does not point to {key} (page {IX[key]})")
    for key, kp in (("l1_work", "key1"), ("l2_a", "key2"), ("l2_b", "key2"), ("l2_c", "key2"), ("l3_work", "key3"), ("l4_journal", "key3"), ("l5_seat", "key4"),
                    ("l5_terms", "key4"), ("l5_search", "key4")):
        if f"Answer key on page {IX[kp]}" not in flat[IX[key] - 1]:
            errs.append(f"{key}: answer-key cross-reference missing")
    ptxt = [PdfReader(PREVIEW_PDF).pages[i].extract_text() for i in range(len(PREVIEW_PICKS))]
    for i, t in enumerate(ptxt):
        c = len(re.findall(r"PREVIEW", t))
        if c != 1:
            errs.append(f"preview PDF page {i + 1}: watermark appears {c} times (want exactly 1)")
    for p in [COVER_PNG, *PREVIEW_PNGS]:
        if Image.open(p).size != (2000, 2000):
            errs.append(f"{os.path.basename(p)}: not 2000x2000 (low-res build?)")
    tj = json.load(open(TPT_JSON))
    if tj != tpt_json(len(rd.pages)):
        errs.append("tpt.json differs from gen.py's data")
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
    if not m2 or DISCLOSURE not in m2.group(1):
        errs.append("UPLOAD.md: description missing the disclosure line")
    elif any(re.search(rf"\b{b}\b", m2.group(1).lower()) for b in BANNED):
        errs.append("UPLOAD.md: description uses a banned word")
    if m2:
        counts = [int(x) for x in re.findall(r"^• .+?: (\d+) pages?\b", m2.group(1), re.M)]
        tot = re.search(r"^Total: (\d+) pages", m2.group(1), re.M)
        if sum(counts) != len(rd.pages) or not tot or int(tot.group(1)) != len(rd.pages):
            errs.append(f"UPLOAD.md: page-count list adds to {sum(counts)}, PDF has {len(rd.pages)}")
        if f"({len(rd.pages)} pages, PDF" not in m2.group(1):
            errs.append("UPLOAD.md: description does not state the PDF page count")
    for need in (f"${PRICE}", f"{len(rd.pages)} pages"):
        if need not in up:
            errs.append(f"UPLOAD.md: missing '{need}'")
    if up != upload_md(len(rd.pages)):
        errs.append("UPLOAD.md is out of date: rebuild with gen.py")
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
    nitems = sum(len(i) for s in key_items().values() for _, i in s)
    print(f"CHECK OK: rhythms read back from the drawn SVG and match the data (beats also recomputed from note fractions); "
          f"{nitems} answer-key items match the data and are printed in the PDF; history dates and timeline math, journal totals, scrambles, sorts and orders verified; "
          f"word search solved by code (all {len(SEARCH_WORDS)} words found exactly once); seating zones do not overlap; "
          f"{len(PLAN)} Letter pages with footers, no text into the footer, fonts embedded (Bravura/Oswald/Source Sans 3 only); "
          f"preview {len(PREVIEW_PICKS)} pages with one watermark each; images 2000x2000 and clear of the band; tpt.json and UPLOAD.md (page list totals {len(PLAN)}) ok.")


if __name__ == "__main__":
    if "--check" in sys.argv:
        check()
    else:
        build()
