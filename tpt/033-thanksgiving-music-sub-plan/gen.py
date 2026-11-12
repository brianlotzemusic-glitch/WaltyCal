#!/usr/bin/env python3
"""Thanksgiving Music Sub Plan K-5: 3 no-prep lessons (TpT 033): build the resource and verify it.

    python3 gen.py            build everything (PDFs, PNGs, tpt.json) into this folder
    python3 gen.py --lowres   same, but square images at scale 1 (self-check only; --check rejects them)
    python3 gen.py --check    verify rhythms, keys, lyric syllable counts, pages, fonts and files

Three no-tech, no-prep Thanksgiving-week music lessons for a substitute, each with a scripted
plan page and two worksheets (K-2 and 3-5): Turkey Rhythm Reading, Gratitude Lyric Writing and
Thankful Listening (a listening response sheet). Plus a sub welcome sheet, lessons at a glance
with a game bank, a turkey rhythm chart with syllables under every note, an early-finisher
page, an answer key and a sub report form. Built from tpt/007's gen.py.

Accuracy is checked end to end: every engraved rhythm is drawn to SVG, the SVG is parsed back
(glyph codepoints, beamed pairs, x position inside its beat slot, barlines) and must equal the
data; every bar holds 4 beats (except the deliberate wrong bars in Lesson 1 part B, whose
printed key is computed); the syllable counts of the example lyrics are computed from their
hyphenation, and the lyric line shape (7 syllables + a rest = 8 beats) is read back from the
drawn rhythm. No songs, lyrics or copyrighted characters: all chants, verses and games are original.
Rendering uses Playwright + Chromium through ../tools/render.js, fonts from ../fonts.
"""
import importlib.util
import json
import os
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

SLUG = "thanksgiving-music-sub-plan"
PDF = os.path.join(HERE, f"{SLUG}.pdf")
PREVIEW_PDF = os.path.join(HERE, f"{SLUG}-PREVIEW.pdf")
COVER_PNG = os.path.join(HERE, "cover.png")
PREVIEW_PNGS = [os.path.join(HERE, f"preview-{i}.png") for i in (1, 2, 3)]
UPLOAD = os.path.join(HERE, "UPLOAD.md")
TPT_JSON = os.path.join(HERE, "tpt.json")

STORE = "Brian Lotze"      # copyright holder
BRAND = "Hudson Beat"      # store line on covers and previews (owner, 4 Oct)
YEAR = 2026
ACCENT = "#B5471B"         # this product's single accent (Thanksgiving rust, as 027)
TINT1, TINT2 = "#D98B66", "#EFC5AE"   # tints of the accent, allowed on cover art
TITLE = "Thanksgiving Music Sub Plan"
PRICE = "4.00"
DISCLOSURE = "Created with the help of digital and AI tools. Notation and answer keys are verified before release."
LOW_RES = "--lowres" in sys.argv

BANNED = ("christmas", "xmas", "santa", "hanukkah", "chanukah", "kwanzaa", "nativity", "jesus", "advent",
          "reindeer", "jingle", "carol", "menorah", "elf", "elves", "youtube", "spotify", "pilgrim", "pilgrims",
          "indian", "indians", "checked by hand", "handmade", "classroom-tested")

# ---------------------------------------------------------------- rhythm data
# tokens: q ta (1 beat), e ti-ti (beamed pair, 1 beat), r shh (quarter rest, 1 beat), h ta-a (2), w ta-a-a-a (4); "|" = barline
BEATS = {"q": 1, "e": 1, "r": 1, "h": 2, "w": 4}
SOUNDS = {"q": 1, "e": 2, "r": 0, "h": 1, "w": 1}
SYL = {"q": "ta", "e": "ti-ti", "r": "shh", "h": "ta-a", "w": "ta-a-a-a"}
NAMES = {"q": "quarter note", "e": "two eighth notes", "r": "quarter rest", "h": "half note", "w": "whole note"}

CHART = ["qeqr", "qqee", "eqqr", "erqe",                   # lines 1-4: K-5 (ta, ti-ti, shh)
         "hqq|eeh", "qeqq|w", "qrh|eeqr", "eqrq|hh"]       # lines 5-8: 3-5 (adds ta-a and ta-a-a-a), two bars

# Lesson 1 Turkey Rhythm Reading
L1_COUNT = ["qqqr", "eqqq", "qrqe", "eeqq", "eeee", "qeqr"]            # K-2 part A: how many sounds?
L1_WORDS = [("pie", "q"), ("gob-ble", "e"), ("shh", "r"), ("corn", "q")]  # K-2 part B: word -> rhythm box
L1_BOXES = ["e", "r", "q"]                                              # boxes A, B, C
L1_MATH = ["qqh", "hh", "wq", "eqr", "hqe", "wh"]                       # 3-5 part A: add the beats
L1_BARS = ["hq", "qqeq", "eeqh", "eeer", "wq", "qrh"]                   # 3-5 part B: is it 4 beats?
L1_SAY = ["eqh", "qrqe"]                                                # 3-5 part C: write the syllables
L1_EX_35 = "qeh|eeqr"
COVER_STRIP = "eeqr"
FEATHERS = ["q", "e", "h", "q", "r", "e", "q"]                          # one glyph per cover feather

# Lesson 2 Gratitude Lyric Writing
L2_STEM = ["Thank", "you", "for"]                  # K-2 chant stem: 3 beats (ta ta ta) + 1 beat of your own word
L2_EX_K2 = [("pie", "q"), ("tur-key", "e")]        # example last words (1 syllable = ta, 2 = ti-ti)
L2_BANK1 = ["pie", "corn", "yam", "home", "sun", "food", "friends", "love", "dog", "cat"]
L2_BANK2 = ["tur-key", "pump-kin", "ap-ple", "to-day", "mu-sic", "teach-er", "sis-ter", "grand-ma", "kit-ten", "co-zy"]
L2_LINE_SHAPE = "qqqq|qqqr"                        # 3-5: 7 syllables on 7 beats + 1 silent beat = 8 beats (2 bars of 4/4)
L2_LINES = [("Thank-ful for the gold-en trees", "A"), ("Thank-ful for the cool fall breeze", "A"),
            ("Pie and corn and rolls to share", "B"), ("Thank-ful for good friends who care", "B")]
L2_SYLLABLES = 7


def syl_count(line):
    """Syllables in a hyphenated lyric line: words split by spaces, syllables by hyphens."""
    return sum(len(w.split("-")) for w in line.split())


def bars(p):
    return p.split("|")


def nbeats(bar):
    return sum(BEATS[t] for t in bar)


def nsounds(p):
    return sum(SOUNDS[t] for t in p if t != "|")


def syllables(p):
    return " ".join(SYL[t] for t in p if t != "|")


def word_rhythm(word):
    """1 syllable = ta, 2 syllables = ti-ti, 'shh' = a silent beat (Kodaly-style word rhythms)."""
    if word == "shh":
        return "r"
    return {1: "q", 2: "e"}.get(len(word.split("-")), "?")


# ---------------------------------------------------------------- listening (Lesson 3)
L3_MOODS = ["calm", "happy", "peaceful", "excited", "sleepy", "cozy", "proud", "thoughtful", "playful", "grand"]
L3_FAMILIES = ["Strings", "Woodwinds", "Brass", "Percussion", "Piano / keyboard", "Voices"]
L3_TEMPO = [("adagio", "slow"), ("moderato", "medium"), ("allegro", "fast")]


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


# ---------------------------------------------------------------- plan and page index
PLAN = ["cover", "teacher", "welcome", "glance", "chart",
        "l1_plan", "l1_k2", "l1_35", "l2_plan", "l2_k2", "l2_35", "l3_plan", "l3_k2", "l3_35",
        "early", "key", "report", "terms"]
IX = {k: i + 1 for i, k in enumerate(PLAN)}


def pg(k):
    return f"page {IX[k]}"


LESSONS = [
    {"n": 1, "short": "Do steps 1 to 3 and send the worksheet home to finish.", "title": "Turkey Rhythm Reading",
     "skill": "Reading and clapping rhythms", "band": "TURKEY RHYTHMS",
     "goal": "Students clap, say and read rhythms with ta, ti-ti and shh (grades 3–5 add ta-a and ta-a-a-a).",
     "materials": "Pencils, the rhythm chart (PG:chart) shown or copied on the board, and the worksheets.",
     "steps": [
         ("5", "Turkey trot echo", "Say: <span class=say>“Happy November, musicians! I’m your guest teacher today. Let’s warm up. Echo me!”</span> "
                                  "Say each line and let the class repeat it: <i>Ears are on. Eyes are up. Hands are still. Let’s make music!</i> "
                                  "Then pat a slow, steady beat on your knees and have the class pat along."),
         ("10", "Learn the rhythm words", "Show the rhythm chart (PG:chart). Point to the key at the bottom: <b>ta</b> is one clap, <b>ti-ti</b> is two quick claps, "
                                          "<b>shh</b> is a silent beat (open hands, no sound). Say line 1 aloud, then clap it. The class echoes. Do lines 1 to 4 "
                                          "with every class. Grades 3–5 also try lines 5 to 8, which add <b>ta-a</b> (a long sound, 2 beats) and <b>ta-a-a-a</b> (4 beats)."),
         ("10", "Gobble and freeze", "Pick one chart line as the <b>gobble line</b>. Clap lines in any order. The class echoes every line, but when "
                                     "the gobble line comes they stay silent and gobble quietly with their hands over their mouths. Let a student leader "
                                     "choose the lines for the last round."),
         ("15", "Worksheets", "Hand out the worksheet: <b>K–2</b> Feather Rhythms (PG:l1_k2), <b>3–5</b> Turkey Rhythm Math (PG:l1_35). "
                              "Read the directions aloud. Clap each rhythm out loud with the class first if students ask. Answers are on PG:key."),
         ("5", "Pass the pie", "Sit in a circle or stay in rows. Clap a short rhythm to the first student, who claps it to the next, and so on. "
                               "Does it arrive the same? Ask: <i>Which rhythm was the hardest to pass?</i>")],
     "extra": "Students make up a 4-beat rhythm of their own with pie, corn, tur-key and shh, then clap it for a neighbor. Or use the early finishers page (PG:early)."},
    {"n": 2, "short": "Do steps 1 and 2, then let students start the worksheet.", "title": "Gratitude Lyrics",
     "skill": "Writing a gratitude chant or verse", "band": "GRATITUDE LYRICS",
     "goal": "Students write original thankful lyrics to a steady beat: a one-beat word chant (K–2) or a four-line rhyming verse (3–5).",
     "materials": "Pencils, the worksheets, and the board for the class chant. No instruments needed.",
     "steps": [
         ("5", "Thankful circle", "Everyone pats a slow, steady beat. Go around the room: each student says one thing they are thankful for in a "
                                  "single beat, such as <i>pie</i>, <i>pup</i> or <i>sun</i>. Anyone can pass. <b>Tip:</b> thankful can be anything small, "
                                  "a pet, a sunny day, a good book or a hot meal. Not every family celebrates Thanksgiving, and that is fine; this lesson is about noticing good things."),
         ("10", "Write a class chant", "On the board, write <b>Thank you for ______.</b> Say it on a steady beat (<i>Thank</i>, <i>you</i>, <i>for</i> and then a word of your own on beat 4). "
                                       "Take word ideas from the class and chant each line together. A one-syllable word is one clap (<b>ta</b>); a two-syllable word, "
                                       "like <i>turkey</i>, is two quick claps (<b>ti-ti</b>)."),
         ("15", "Worksheets", "Hand out the worksheet: <b>K–2</b> My Thankful Chant (PG:l2_k2), <b>3–5</b> Gratitude Verse (PG:l2_35). "
                              "Grades 3–5: read the example verse aloud on a steady beat, and show students how to count syllables on their fingers. "
                              "A line should have exactly 7 syllables and then a silent beat. This lesson has no answer key because every answer is the student’s own."),
         ("10", "Share and chant", "Invite volunteers to read or chant their lines while the class pats the beat. Praise one specific thing: "
                                   "a funny word, a great rhyme or a line that fits the beat perfectly. Finish with the whole class chanting <i>Thank you for ______</i>, "
                                   "each student adding their own word.")],
     "extra": "Add a second verse, or turn a favorite line into a poster with a drawing. Or use the early finishers page (PG:early)."},
    {"n": 3, "short": "Do steps 1, 3 and 4 only.", "title": "Thankful Listening",
     "skill": "Listening and responding to music", "band": "THANKFUL LISTENING",
     "goal": "Students listen carefully to one piece of music and describe its speed, loudness, instruments and mood.",
     "materials": "The listening music your teacher chose (see the welcome sheet, PG:welcome), a way to play it, pencils and the worksheets. "
                  "No audio is included in this resource.",
     "steps": [
         ("5", "Listening ears", "Say: <span class=say>“A good listener has quiet hands, a quiet voice and open ears. Today we listen the way a musician does.”</span> "
                                 "Ask: <b>What sounds can you hear in the room right now?</b> Take 3 or 4 answers."),
         ("5", "Music words", "Read the words on the student sheet aloud. K–2: <b>loud, soft, fast, slow, happy, calm</b>. 3–5: <b>tempo, dynamics, "
                              "instrument families, mood</b>. Act them out: clap loud and soft, walk fast and slow."),
         ("10", "First listen: just listen", "Play the music your teacher chose (about 2 to 3 minutes). Students close their eyes or look down and "
                                             "<b>only listen</b>. No audio today? Do the sound show instead: clap, stomp and whisper in a pattern of soft, loud, soft, "
                                             "fast, slow, and let students describe what changed."),
         ("15", "Second listen: fill in the sheet", "Hand out the worksheet: <b>K–2</b> My Listening Page (PG:l3_k2), <b>3–5</b> Listening Response (PG:l3_35). "
                                                    "Play the music again and let students fill in the sheet as it plays. Play it a third time if there is time. "
                                                    "There are no wrong answers, because each student describes what they heard."),
         ("5", "Turn and talk", "Partners share one thing they heard and one thing they imagined. Then ask: <i>Who heard something different from their partner?</i>")],
     "extra": "Students draw a second picture for a different scene, or write 3 sentences about the music. Or use the early finishers page (PG:early)."},
]

GAMES = [
    ("Turkey Trot Echo", "Clap a short line from the chart; the class echoes it exactly. Change the speed and the loudness.", "1"),
    ("Gobble and Freeze", "Clap chart lines in any order. Everyone echoes except for the chosen gobble line: silence.", "1"),
    ("Pass the Pie", "Pass a clapped rhythm from student to student. Does it arrive the same?", "1"),
    ("Thankful Circle", "Pat a steady beat. Each student says one thing they are thankful for in one beat. Passing is allowed.", "2"),
    ("Silent Conductor", "A student conducts the class’s claps: hands far apart = loud, close together = soft, fists = stop.", "3"),
    ("Feast Freeze", "March in place to a steady beat; freeze when the beat stops. Name a food to act out when you freeze.", "3"),
]

SHEET_TITLES = {  # lesson: (K-2 title, 3-5 title)
    1: ("Feather Rhythms", "Turkey Rhythm Math"),
    2: ("My Thankful Chant", "Gratitude Verse"),
    3: ("My Listening Page", "Listening Response"),
}

PARTS = [  # (label, first key, last key, use)
    ("For the substitute", "welcome", "glance", "welcome sheet, lessons at a glance, game bank"),
    ("Rhythm chart", "chart", "chart", "8 lines with syllables, for Lessons 1 and 3 games"),
    ("Lesson 1 · Turkey Rhythm Reading", "l1_plan", "l1_35", "plan + K–2 and 3–5 sheets"),
    ("Lesson 2 · Gratitude Lyrics", "l2_plan", "l2_35", "plan + K–2 and 3–5 sheets"),
    ("Lesson 3 · Thankful Listening", "l3_plan", "l3_35", "plan + K–2 and 3–5 response sheets"),
    ("Early finishers", "early", "early", "draw, write and clap, K–5"),
    ("Answer key", "key", "key", "Lesson 1 answers and Lesson 2 syllable counts"),
    ("Sub report", "report", "report", "notes back to you"),
    ("Terms of use", "terms", "terms", "license and credits"),
]


def prange(a, b):
    return str(IX[a]) if a == b else f"{IX[a]}–{IX[b]}"


def fill_pages(s):
    return re.sub(r"PG:(\w+)", lambda m: pg(m.group(1)), s)


# ---------------------------------------------------------------- shared art
def turkey_svg(cx, cy, tokens=None, tints=True, s=6.5):
    """A front-facing turkey whose tail fan has 7 feathers (cover art: accent, its tints, black and white only).
    The pivot (cx, cy) is the top of the body; tokens, if given, are drawn upright near each feather tip."""
    out = []
    fills = [TINT2, "#fff", TINT1] if tints else ["#fff"]
    angles = [-72, -48, -24, 0, 24, 48, 72]
    for i, a in enumerate(angles):
        out.append(f'<g transform="translate({cx} {cy}) rotate({a}) translate(0 -88)">'
                   f'<ellipse cx="0" cy="0" rx="29" ry="68" fill="{fills[i % len(fills)]}" stroke="#000" stroke-width="2.6"/>'
                   f'<path d="M0 -50 L0 52 M0 -22 L-15 -38 M0 -22 L15 -38 M0 6 L-17 -12 M0 6 L17 -12" fill="none" stroke="#000" '
                   f'stroke-width="1.5" opacity=".45" stroke-linecap="round"/></g>')
    if tokens:
        import math
        for a, t in zip(angles, tokens):
            px = cx + math.sin(math.radians(a)) * 108
            py = cy - math.cos(math.radians(a)) * 108
            out.append(tok_svg(t, px, py + 8, s, 40))
    out.append(f'<ellipse cx="{cx}" cy="{cy + 40}" rx="58" ry="48" fill="{ACCENT}" stroke="#000" stroke-width="2.8"/>')
    out.append(f'<path d="M{cx - 30} {cy + 52} Q{cx} {cy + 82} {cx + 30} {cy + 52}" fill="none" stroke="#fff" stroke-width="3" stroke-linecap="round"/>')
    out.append(f'<path d="M{cx - 20} {cy + 88} L{cx - 24} {cy + 112} M{cx + 20} {cy + 88} L{cx + 24} {cy + 112} '
               f'M{cx - 24} {cy + 112} L{cx - 36} {cy + 118} M{cx - 24} {cy + 112} L{cx - 24} {cy + 120} M{cx - 24} {cy + 112} L{cx - 12} {cy + 118} '
               f'M{cx + 24} {cy + 112} L{cx + 36} {cy + 118} M{cx + 24} {cy + 112} L{cx + 24} {cy + 120} M{cx + 24} {cy + 112} L{cx + 12} {cy + 118}" '
               f'fill="none" stroke="#000" stroke-width="3" stroke-linecap="round"/>')
    out.append(f'<circle cx="{cx}" cy="{cy + 2}" r="24" fill="#fff" stroke="#000" stroke-width="2.8"/>')
    out.append(f'<circle cx="{cx - 9}" cy="{cy - 3}" r="3.6" fill="#000"/><circle cx="{cx + 9}" cy="{cy - 3}" r="3.6" fill="#000"/>')
    out.append(f'<path d="M{cx - 6} {cy + 6} L{cx + 6} {cy + 6} L{cx} {cy + 16} Z" fill="{ACCENT}" stroke="#000" stroke-width="2" stroke-linejoin="round"/>')
    out.append(f'<path d="M{cx - 2} {cy + 16} Q{cx - 3} {cy + 28} {cx + 3} {cy + 24} Q{cx + 5} {cy + 18} {cx + 2} {cy + 16} Z" fill="{ACCENT}" stroke="#000" stroke-width="1.6"/>')
    return "".join(out)


def pencil_svg(x, y, length, angle, accent=ACCENT):
    return (f'<g transform="translate({x} {y}) rotate({angle})">'
            f'<rect x="0" y="-11" width="{length}" height="22" rx="3" fill="#fff" stroke="#000" stroke-width="2.2"/>'
            f'<rect x="0" y="-11" width="22" height="22" rx="3" fill="{accent}" stroke="#000" stroke-width="2.2"/>'
            f'<line x1="26" y1="-11" x2="26" y2="11" stroke="#000" stroke-width="2.2"/>'
            f'<path d="M{length} -11 L{length + 30} 0 L{length} 11 Z" fill="#fff" stroke="#000" stroke-width="2.2" stroke-linejoin="round"/>'
            f'<path d="M{length + 20} -3.7 L{length + 30} 0 L{length + 20} 3.7 Z" fill="#000"/></g>')


def mini_turkey(w=64):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 250" width="{w}pt" style="display:block">'
            f'{turkey_svg(150, 118, None, True)}</svg>')


# ---------------------------------------------------------------- substitute pages
def welcome_page(n, watermark=False):
    rows = "".join(f"<tr><td style='height:25pt'></td><td></td><td></td><td></td></tr>" for _ in range(6))
    inner = (f'<div class="how">Teacher: fill this in once and keep it on top of the sub folder. Substitute: welcome, and thank you! '
             f'Everything you need for today is in this folder.</div>'
             f'<div class="cols" style="gap:16pt"><div>{fl("Teacher")}{fl("Room")}{fl("School office ext.")}</div>'
             f'<div>{fl("Nearby teacher who can help")}{fl("Their room")}{fl("Date updated")}</div></div>'
             f'<div class="part">Today’s classes<span class="acc"> ·</span><small>Use the lesson number you have not used yet with that class.</small></div>'
             f'<table class="t"><tr><th style="width:18%">Time</th><th style="width:30%">Class / grade</th><th style="width:14%">Lesson #</th><th>Notes</th></tr>{rows}</table>'
             f'<div class="part" style="margin-top:6pt">Listening music for Lesson 3<span class="acc"> ·</span><small>Teacher: choose a calm instrumental piece or two that you may play in class.</small></div>'
             f'<div class="cols" style="gap:16pt"><div>{fl("Title / composer")}</div><div>{fl("Where to find it / how to play it")}</div></div>'
             f'<div class="cols" style="gap:16pt;margin-top:2pt"><div>'
             f'<div class="part">How we do things<span class="acc"> ·</span></div>'
             f'{fl("Attention signal")}{fl("Entering the room")}{fl("Where students sit")}{fl("Bathroom / water")}{fl("Lining up / dismissal")}'
             f'</div><div>'
             f'<div class="part">Where things are<span class="acc"> ·</span></div>'
             f'{fl("Copies of worksheets")}{fl("Pencils")}{fl("Seating charts")}{fl("Emergency plans")}{fl("Class lists")}'
             f'</div></div>'
             f'<div class="box" style="margin-top:6pt;font-size:10.5pt"><b>No music background needed.</b> Each lesson has a step-by-step plan with words to say, '
             f'and every rhythm has its syllables printed under the notes. Please leave notes on the sub report ({pg("report")}).</div>')
    return page("Welcome, substitute · fill in and keep on top", "FOR THE SUB", "Welcome sheet", inner, n, watermark)


def glance_page(n, watermark=False):
    rows = ""
    for d in LESSONS:
        k = d["n"]
        total = sum(int(m) for m, _, _ in d["steps"])
        rows += (f"<tr><td class='ans' style='font-size:13pt;text-align:center'>{k}</td><td><b>{escape(d['title'])}</b><br>"
                 f"<span class='small'>{d['skill']} · about {total} min</span></td><td>{escape(SHEET_TITLES[k][0])}<br><span class='small'>{pg(f'l{k}_k2')}</span></td>"
                 f"<td>{escape(SHEET_TITLES[k][1])}<br><span class='small'>{pg(f'l{k}_35')}</span></td>"
                 f"<td style='text-align:center'>{IX[f'l{k}_plan']}</td></tr>")
    games = "".join(f"<tr><td><b>{g}</b></td><td>{t}</td><td style='text-align:center'>{dd}</td></tr>" for g, t, dd in GAMES)
    inner = (f'<div class="how">Each lesson is one 30–45 minute music class. Every lesson works for any grade K–5: use the plan page, then hand out '
             f'the <b>K–2</b> or <b>3–5</b> sheet. The lessons can be used in any order, and each one works on its own.</div>'
             f'<table class="t"><tr><th style="width:9%">Lesson</th><th style="width:33%">Lesson</th><th>K–2 sheet</th><th>3–5 sheet</th>'
             f'<th style="width:11%">Plan page</th></tr>{rows}</table>'
             f'<div class="part" style="margin-top:12pt">Game bank<span class="acc"> ·</span><small>No-prep games for extra time. No equipment, no tech.</small></div>'
             f'<table class="t"><tr><th style="width:26%">Game</th><th>How to play</th><th style="width:9%">Lesson</th></tr>{games}</table>'
             f'<div class="part" style="margin-top:12pt">Tips for a calm class<span class="acc"> ·</span></div>'
             f'<ul style="margin:0;padding-left:15pt;font-size:10.6pt;line-height:1.4">'
             f'<li>Use the teacher’s attention signal from the welcome sheet ({pg("welcome")}), or clap a short rhythm and have the class clap it back.</li>'
             f'<li>“Strong voice, not shouting” keeps the loud parts happy and safe.</li>'
             f'<li>If a game gets too loud, switch to a worksheet or Feast Freeze.</li>'
             f'<li>Students may have very different holiday plans. Keep the talk on gratitude, food and music, and let anyone pass.</li></ul>')
    return page("Lessons at a glance and game bank", "FOR THE SUB", "3 lessons, any order", inner, n, watermark)


def chart_page(n, watermark=False):
    s, W = 8.6, 50
    rows = []
    for i, p in enumerate(CHART):
        st, _ = rhythm_svg(p, 14, 34, s, W if "|" not in p else 33, syl=True, syl_size=12.5)
        lab = (f'<div style="flex:0 0 34pt;text-align:center"><div class="h" style="font-size:22pt">{i + 1}</div>'
               f'<div class="l" style="font-size:9pt">{"K–5" if i < 4 else "3–5"}</div></div>')
        rows.append(f'<div style="display:flex;align-items:center;border-bottom:1pt solid #bbb;padding:0">{lab}{svg(470, 68, st)}</div>')
    key = " · ".join(f"<b>{SYL[t]}</b> = {NAMES[t]} ({BEATS[t]} beat{'s' if BEATS[t] > 1 else ''})" for t in "qerhw")
    inner = (f'<div style="display:flex;align-items:center;gap:12pt"><div class="how" style="flex:1">Clap and say each line; the class echoes. '
             f'Say the words under the notes; you do not need to read music. Silent beats (<b>shh</b>): open your hands, no sound.</div>{mini_turkey(62)}</div>'
             f'<div style="border-top:1pt solid #bbb">{"".join(rows)}</div>'
             f'<div class="small" style="margin-top:6pt;font-size:9.5pt !important">{key}</div>')
    return page("Turkey rhythm chart · show it or copy a line on the board", "FOR THE SUB", "Lesson 1 and games", inner, n, watermark)


def plan_page(d, n, watermark=False):
    k = d["n"]
    steps = "".join(
        f'<li><div class="tm"><b>{m} min</b><span>Step {i + 1}</span></div><div class="tx"><b class="hd">{escape(h)}</b><br>{fill_pages(t)}</div></li>'
        for i, (m, h, t) in enumerate(d["steps"]))
    total = sum(int(m) for m, _, _ in d["steps"])
    inner = (f'<div class="meta"><div><b class="k">Goal</b>{d["goal"]}</div><div><b class="k">You need</b>{fill_pages(d["materials"])}</div>'
             f'<div style="flex:0 0 1.55in"><b class="k">Copies</b>K–2: {pg(f"l{k}_k2")}<br>3–5: {pg(f"l{k}_35")}<br>'
             f'<span class="small">about {total} min</span></div></div>'
             f'<div class="part" style="margin-top:10pt">Step by step<span class="acc"> ·</span><small>Italic lines are words you can say.</small></div>'
             f'<ol class="steps">{steps}</ol>'
             f'<div class="box" style="margin-top:auto;font-size:10.5pt"><b>Extra time?</b> {fill_pages(d["extra"])} '
             f'<b>Short class?</b> {d["short"]}</div>')
    return page(f"Lesson {k} · {escape(d['skill'])} · no tech, no prep", f"LESSON {k}", "Sub plan", inner, n, watermark,
                title=d["title"])


# ---------------------------------------------------------------- worksheets
def sheet(k, band, sub, inner, n, watermark=False, key_page=None):
    title = SHEET_TITLES[k][0 if band == "k2" else 1]
    right = f"Answer key on page {IX[key_page]}" if key_page else None
    return page(sub, f"LESSON {k}", "Grades K–2" if band == "k2" else "Grades 3–5", inner, n, watermark, name=True, right=right, title=title)


def _single(t, cx, yl, s):
    return tok_svg(t, cx, yl, s, 40)


def _letter_box(val, key, w=34, h=28, size=18):
    return (f'<span style="display:inline-block;width:{w}pt;height:{h}pt;border:1.3pt solid #000;border-radius:5pt;text-align:center;'
            f'line-height:{h}pt;vertical-align:middle;font-family:Oswald;font-weight:700;font-size:{size}pt;color:{ACCENT}">{val if key else ""}</span>')


def l1_k2(n, watermark=False, key=False):
    s, W = 8.6, 52
    rows = []
    for i, p in enumerate(L1_COUNT):
        st, _ = rhythm_svg(p, 8, 34, s, W, syl=key, syl_size=11)
        rows.append(f'<div style="display:flex;align-items:center;gap:14pt;border:1.3pt solid #000;border-radius:7pt;padding:1pt 14pt">'
                    f'<b class="h" style="font-size:17pt">{i + 1}</b>{svg(270, 60, st)}<span style="flex:1"></span>'
                    f'<span style="font-size:11pt">claps</span>{_letter_box(nsounds(p), key, 42, 34, 21)}</div>')
    bx = "".join(f'<div style="text-align:center"><div class="h" style="font-size:16pt">{"ABC"[i]}</div>'
                 f'{svg(70, 56, _single(t, 35, 34, 9))}</div>'
                 for i, t in enumerate(L1_BOXES))
    words = "".join(f'<div style="display:flex;align-items:center;gap:8pt;font-size:16pt;margin:3pt 0"><b style="width:78pt">{w}</b>'
                    f'{_letter_box("ABC"[L1_BOXES.index(t)], key, 34, 28, 17)}</div>' for w, t in L1_WORDS)
    inner = (f'<div class="part">A · How many sounds?<small>Clap each feather rhythm. Write how many claps you hear. (A rest is silent.)</small></div>'
             f'<div style="display:grid;grid-template-columns:1fr;gap:7pt">{"".join(rows)}</div>'
             f'<div class="part" style="margin-top:14pt">B · Word rhythms<small>Say and clap each word. Write the letter of its rhythm.</small></div>'
             f'<div style="display:flex;gap:24pt;align-items:center"><div class="box" style="display:flex;gap:24pt;padding:6pt 18pt">{bx}</div>'
             f'<div>{words}</div></div>')
    if key:
        return page("Lesson 1 · K–2 answer key", "ANSWER KEY", "Feather Rhythms", inner, n, watermark, ak=True, title="Feather Rhythms")
    return sheet(1, "k2", "Clap, count and match", inner, n, watermark, key_page="key")


def l1_35(n, watermark=False, key=False):
    s = 7
    math_cells = []
    for i, p in enumerate(L1_MATH):
        parts = []
        x = 8
        for j, t in enumerate(p):
            if j:
                parts.append(text(x + 6, 40, "+", 16, 500))
                x += 18
            parts.append(_single(t, x + 12, 38, s))
            x += 26 if t != "e" else 30
        parts.append(text(x + 6, 40, "=", 16, 500))
        math_cells.append(f'<div style="display:flex;align-items:center;gap:6pt;border:1.3pt solid #000;border-radius:7pt;padding:2pt 8pt">'
                          f'<b class="h" style="font-size:13pt">{i + 1}</b>{svg(x + 14, 54, "".join(parts))}'
                          f'{_letter_box(nbeats(p), key, 34, 26, 16)}<span style="font-size:10pt">beats</span></div>')
    bar_cells = []
    for i, p in enumerate(L1_BARS):
        st, xe = rhythm_svg(p, 8, 30, 6, 26, syl=False)
        ok = nbeats(p) == 4
        bar_cells.append(f'<div style="display:flex;align-items:center;gap:6pt;border:1.3pt solid #000;border-radius:7pt;padding:2pt 8pt;min-width:0">'
                         f'<b class="h" style="font-size:13pt">{i + 1}</b>{svg(int(xe) + 6, 52, st)}<span style="flex:1"></span>'
                         f'<div style="text-align:center;font-size:11pt"><div style="white-space:nowrap">{circ("YES", key and ok)}{circ("NO", key and not ok)}</div>'
                         f'<div style="font-size:9.5pt;margin-top:3pt">beats: {_letter_box(nbeats(p), key, 26, 20, 13)}</div></div></div>')
    say = []
    for i, p in enumerate(L1_SAY):
        st, _ = rhythm_svg(p, 8, 30, 7.4, 52)
        say.append(f'<div style="display:flex;align-items:center;gap:10pt"><b class="h" style="font-size:13pt">{i + 1}</b>{svg(250, 50, st)}'
                   f'<span style="flex:1;border-bottom:1pt solid #000;height:22pt;font-family:Oswald;font-weight:700;color:{ACCENT};'
                   f'font-size:15pt;letter-spacing:.04em">{syllables(p) if key else ""}</span></div>')
    beat_key = " · ".join(f"{NAMES[t]} = {BEATS[t]}" for t in "qerhw")
    inner = (f'<div class="small" style="margin-top:6pt;font-size:9.5pt !important"><b>Beats:</b> {beat_key}</div>'
             f'<div class="part" style="margin-top:6pt">A · Rhythm math<small>Add up the beats.</small></div>'
             f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:7pt 12pt">{"".join(math_cells)}</div>'
             f'<div class="part" style="margin-top:12pt">B · Is it 4 beats?<small>In 4/4 time every bar needs 4 beats. Count each bar. Circle YES or NO.</small></div>'
             f'<div style="display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:7pt 12pt">{"".join(bar_cells)}</div>'
             f'<div class="part" style="margin-top:12pt">C · Say it<small>Write the rhythm syllables (ta, ti-ti, shh, ta-a) for each rhythm.</small></div>'
             f'{"".join(say)}')
    if key:
        return page("Lesson 1 · 3–5 answer key", "ANSWER KEY", "Turkey Rhythm Math", inner, n, watermark, ak=True, title="Turkey Rhythm Math")
    return sheet(1, "35", "Add the beats, check the bars, say the rhythm", inner, n, watermark, key_page="key")


def l2_k2(n, watermark=False):
    s = 9
    bank1 = " · ".join(f"<b>{w}</b>" for w in L2_BANK1)
    bank2 = " · ".join(f"<b>{w}</b>" for w in L2_BANK2)

    def row(last=None, label=""):
        cells = []
        for i in range(4):
            if i < 3:
                w, t = L2_STEM[i], "q"
            else:
                w, t = last if last else ("", None)
            note = svg(70, 48, _single(t, 35, 34, s)) if t else ""
            cells.append(f'<div style="border:1.4pt solid #000;border-radius:7pt;text-align:center;overflow:hidden">'
                         f'<div style="height:36pt;font-size:17pt;font-weight:700;line-height:36pt{";color:" + ACCENT if i == 3 else ""}">{w}</div>'
                         f'<div style="height:48pt;border-top:1pt dashed #999;display:flex;align-items:center;justify-content:center">{note}</div></div>')
        return f'<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:8pt;margin-bottom:6pt">{"".join(cells)}</div>'
    inner = (f'<div class="how" style="font-size:12pt">Each box is <b>one beat</b>. The first three beats say <b>Thank you for</b>. '
             f'In the last box, write or draw something you are thankful for. One-syllable word = <b>ta</b> (one note). '
             f'Two-syllable word = <b>ti-ti</b> (two notes joined). Draw its note, then chant your line on a steady beat!</div>'
             f'<div class="box" style="font-size:11pt;line-height:1.35;padding:5pt 10pt"><b>One syllable (ta):</b> {bank1}<br>'
             f'<b>Two syllables (ti-ti):</b> {bank2}<br><span class="small">Your own words are welcome too.</span></div>'
             f'<div class="part" style="margin-top:8pt">Examples<small>Thank you for pie (one syllable, ta). Thank you for tur-key would use ti-ti.</small></div>'
             f'{row(L2_EX_K2[0])}'
             f'<div class="part" style="margin-top:6pt">My chant<small>Write 3 lines of your own.</small></div>'
             f'{row()}{row()}{row()}')
    return sheet(2, "k2", "Chant something you are thankful for", inner, n, watermark)


def l2_35(n, watermark=False):
    s = 6.4
    st, _ = rhythm_svg(L2_LINE_SHAPE, 8, 30, s, 30, syl=False)
    shape = svg(300, 52, st)
    ex_lines = []
    for ln, g in L2_LINES:
        last = ln.split()[-1]
        body = " ".join(f'<b style="color:{ACCENT}">{w}</b>' if w == last else w for w in ln.split())
        ex_lines.append(f'<div style="display:flex;gap:8pt;font-size:13pt;line-height:1.5"><b class="h" style="width:16pt;color:{ACCENT}">{g}</b>'
                        f'<span style="flex:1">{body}</span><span class="small" style="width:70pt;text-align:right">{syl_count(ln)} syllables</span></div>')
    lines_html = []
    for i in range(4):
        boxes = "".join(f'<span style="flex:1;height:26pt;border:1.2pt solid #000;border-radius:3pt"></span>' for _ in range(L2_SYLLABLES))
        lines_html.append(f'<div style="display:flex;align-items:center;gap:6pt;margin:0 0 5pt"><b class="h" style="width:16pt;color:{ACCENT}">{"AABB"[i]}</b>'
                          f'<div style="display:flex;gap:3pt;flex:1">{boxes}</div>'
                          f'<span style="width:36pt;text-align:center;border-bottom:1pt solid #000;font-size:10pt;height:20pt">&nbsp;</span>'
                          f'<span class="small" style="width:2pt"></span></div>')
    inner = (f'<div class="how">Write a 4-line thankful verse. Every line has <b>7 syllables</b> (one in each box) and then one silent beat, so it fits 8 beats of music. '
             f'Lines 1 and 2 rhyme (A), and lines 3 and 4 rhyme (B).</div>'
             f'<div class="part" style="margin-top:2pt">A · Read the example<small>Syllables are counted for you. Rhyme words are in color.</small></div>'
             f'<div class="box" style="padding:5pt 10pt">{"".join(ex_lines)}</div>'
             f'<div class="part" style="margin-top:10pt">B · The beat<small>7 syllables on 7 beats, then <b>shh</b> (a silent beat).</small></div>'
             f'<div style="display:flex;align-items:center;gap:14pt">{shape}<div class="small" style="font-size:10pt !important">Tap the beat on your desk and '
             f'say one syllable on each tap. Rest on the last tap.</div></div>'
             f'<div class="part" style="margin-top:8pt">C · Write your verse<small>One syllable per box. Write the number of syllables you wrote at the end of each line.</small></div>'
             f'{"".join(lines_html)}'
             f'<div style="display:flex;gap:16pt;margin-top:8pt">{fl("Verse title", "style=flex:1")}</div>'
             f'<div class="part" style="margin-top:6pt">D · Check it<small>Tick each box when it is true.</small></div>'
             + "".join(f'<div style="font-size:11pt;margin:0 0 4pt">{checkbox(12)} &nbsp;{c}</div>' for c in (
                 "Every line has exactly 7 syllables.", "Lines 1 and 2 rhyme, and lines 3 and 4 rhyme.",
                 "I can chant my whole verse on a steady beat, with a rest at the end of each line.")))
    return sheet(2, "35", "Write a four-line gratitude verse to a steady beat", inner, n, watermark)


# ---------------------------------------------------------------- answer-key helper
def mini(html_page, scale):
    """Embed a filled-in worksheet page as a scaled-down copy on a key page."""
    body = re.sub(r'^<section class="page">', "", html_page)
    body = re.sub(r"</section>$", "", body)
    body = re.sub(r'<div class="foot">.*?</span></div>', "", body)
    return (f'<div style="width:{8.5 * scale}in;height:{11 * scale}in;overflow:hidden;border:1.2pt solid #000;border-radius:4pt">'
            f'<div class="page" style="transform:scale({scale});transform-origin:0 0">{body}</div></div>')


def l3_k2(n, watermark=False):
    def pair(a, b, c=None):
        items = "".join(circ(x) for x in (a, b, c) if x)
        return f'<div style="display:flex;justify-content:space-around;font-size:15pt;margin:0 0 9pt">{items}</div>'
    inner = (f'<div class="how" style="font-size:12.5pt">Listen to the music. <b>Draw</b> what you picture. <b>Circle</b> one word in each row.</div>'
             f'<div class="box" style="height:250pt;position:relative"><span class="small" style="position:absolute;left:8pt;top:4pt">Draw what you see in your mind.</span></div>'
             f'<div class="part" style="margin-top:12pt">The music was<span class="acc"> ·</span></div>'
             f'{pair("LOUD", "SOFT")}{pair("FAST", "SLOW")}{pair("HAPPY", "CALM", "SLEEPY")}'
             f'<div class="part" style="margin-top:6pt">I heard<span class="acc"> ·</span><small>Circle all you heard.</small></div>'
             f'{pair("DRUMS", "PIANO", "VOICES")}{pair("STRINGS", "HORNS", "FLUTES")}'
             f'<div style="margin-top:8pt;font-size:13pt;display:flex;align-items:flex-end;gap:8pt"><b>This music made me feel</b>'
             f'<span style="flex:1;border-bottom:1pt solid #000;height:20pt"></span></div>'
             f'<div style="margin-top:12pt;font-size:13pt">I liked it: &nbsp;{circ("A LOT")}{circ("A LITTLE")}{circ("NOT YET")}</div>')
    return sheet(3, "k2", "Close your eyes and listen like a musician", inner, n, watermark)


def l3_35(n, watermark=False):
    tempo = "".join(f'<div style="text-align:center">{circ(w.upper())}<div class="small">{m}</div></div>' for w, m in L3_TEMPO)
    fams = "".join(f'<div style="font-size:11pt">{checkbox(12)} &nbsp;{f}</div>' for f in L3_FAMILIES)
    moods = " ".join(circ(m.upper()) for m in L3_MOODS)
    # dynamics graph: 6 time slots, loud/medium/soft rows
    gw, gh, left = 330, 92, 56
    g = [f'<rect x="{left}" y="4" width="{gw - left}" height="{gh - 8}" fill="#fff" stroke="#000" stroke-width="1.4"/>']
    for i, lab in enumerate(("LOUD", "MEDIUM", "SOFT")):
        y = 4 + (gh - 8) * (i + .5) / 3
        g.append(text(left - 6, y + 4, lab, 11, 500, anchor="end"))
        g.append(f'<line x1="{left}" y1="{y:.1f}" x2="{gw}" y2="{y:.1f}" stroke="#999" stroke-width="1" stroke-dasharray="3 4"/>')
    for j in range(1, 6):
        x = left + (gw - left) * j / 6
        g.append(f'<line x1="{x:.1f}" y1="4" x2="{x:.1f}" y2="{gh - 4}" stroke="#bbb" stroke-width="1"/>')
    g.append(text(left, gh + 14, "start", 10, 300, anchor="start") + text(gw, gh + 14, "end", 10, 300, anchor="end"))
    graph = svg(gw, gh + 18, "".join(g))
    inner = (f'<div style="display:flex;gap:14pt">{fl("Music title", "style=flex:1")}{fl("Composer (if known)", "style=flex:1")}</div>'
             f'<div class="part" style="margin-top:0">A · Tempo<small>Circle the speed of the music.</small></div>'
             f'<div style="display:flex;gap:26pt;font-size:13pt">{tempo}</div>'
             f'<div class="part" style="margin-top:8pt">B · Dynamics<small>Draw a line to show how loud or soft the music gets from start to end.</small></div>{graph}'
             f'<div class="part" style="margin-top:8pt">C · Instruments<small>Tick every group you hear.</small></div>'
             f'<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:4pt 10pt">{fams}</div>'
             f'<div class="part" style="margin-top:8pt">D · Mood<small>Circle up to three words.</small></div>'
             f'<div style="font-size:11.5pt;line-height:1.9">{moods}</div>'
             f'<div class="part" style="margin-top:8pt">E · Explain<small>Finish the sentences.</small></div>'
             f'<div style="font-size:11.5pt">This music would fit a scene about <span style="display:inline-block;width:240pt;border-bottom:1pt solid #000">&nbsp;</span> because</div>'
             f'<div class="ln2"></div><div style="font-size:11.5pt;margin-top:2pt">One thing I heard that I want to remember is</div><div class="ln2"></div>'
             f'<div style="font-size:11.5pt;margin-top:2pt">If I could add one instrument or sound, it would be</div><div class="ln2"></div>')
    return sheet(3, "35", "Listen, describe and explain what you hear", inner, n, watermark)


def early_page(n, watermark=False):
    import math
    feathers = []
    for i, off in enumerate((36, 12, 0, 12, 36)):
        feathers.append(f'<div style="position:absolute;left:{i * 101 + 4}pt;top:{off}pt;width:96pt;height:140pt;border:1.6pt solid #000;'
                        f'border-radius:48pt 48pt 40pt 40pt / 64pt 64pt 36pt 36pt;background:#fff;text-align:center;padding-top:30pt">'
                        f'<span class="small">I’m thankful<br>for…</span></div>')
    big_turkey = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 -45 300 295" width="150pt" style="display:block;overflow:visible">'
                  f'{turkey_svg(150, 118, None, True)}</svg>')
    inner = (f'<div class="how">Finished early? Pick one (or do them all).</div>'
             f'<div class="part" style="margin-top:0">Thankful turkey<small>Write or draw one thing you are thankful for on each feather. Color the turkey.</small></div>'
             f'<div style="position:relative;height:300pt;width:505pt;margin:0 auto">{"".join(feathers)}'
             f'<div style="position:absolute;left:calc(50% - 75pt);top:152pt;width:150pt">{big_turkey}</div></div>'
             f'<div class="part" style="margin-top:8pt">My 4-beat thankful rhythm<small>One word or note in each beat box. Clap it for a friend.</small></div>'
             f'<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:8pt">'
             + "".join(f'<div style="border:1.4pt solid #000;border-radius:7pt;height:64pt;position:relative"><span class="small" '
                       f'style="position:absolute;left:6pt;top:3pt">beat {i + 1}</span></div>' for i in range(4))
             + f'</div><div class="part" style="margin-top:10pt">My music words<small>Write 3 sentences using a music word: beat, loud, soft, fast, slow, high, low.</small></div>'
             f'<div class="ln2"></div><div class="ln2"></div><div class="ln2"></div>')
    return page("Early finishers · grades K–5", "ANY LESSON", "Early finishers", inner, n, watermark, name=True, title="Early Finishers")


# ---------------------------------------------------------------- answer key
EXAMPLE_CLAPS = "Lesson 2 example verse"


def key_page(n, watermark=False):
    a = mini(l1_k2(0, key=True), 0.22)
    b = mini(l1_35(0, key=True), 0.22)
    rows = "".join(f"<tr><td>A{i + 1}</td><td>{syllables(p)}</td><td class='ans'>{nsounds(p)}</td></tr>" for i, p in enumerate(L1_COUNT))
    rows += "".join(f"<tr><td>B · {w}</td><td>{SYL[t]}</td><td class='ans'>{'ABC'[L1_BOXES.index(t)]}</td></tr>" for w, t in L1_WORDS)
    rows2 = "".join(f"<tr><td>A{i + 1}</td><td>{' + '.join(str(BEATS[t]) for t in p)}</td><td class='ans'>{nbeats(p)}</td></tr>" for i, p in enumerate(L1_MATH))
    rows2 += "".join(f"<tr><td>B{i + 1}</td><td>{syllables(p)}</td><td class='ans'>{'YES' if nbeats(p) == 4 else 'NO'} · {nbeats(p)}</td></tr>"
                     for i, p in enumerate(L1_BARS))
    rows2 += "".join(f"<tr><td>C{i + 1}</td><td colspan=2 class='ans'>{syllables(p)}</td></tr>" for i, p in enumerate(L1_SAY))
    lyr = "".join(f"<tr><td>{g}</td><td>{ln}</td><td class='ans'>{syl_count(ln)}</td></tr>" for ln, g in L2_LINES)
    inner = (f'<div class="how">Lesson 1 answers. The small pages are the filled-in worksheets; the tables list every answer.</div>'
             f'<div class="cols" style="gap:16pt"><div>{a}<table class="t" style="margin-top:6pt;font-size:9pt"><tr><th>K–2</th><th>Rhythm</th><th>Answer</th></tr>{rows}</table></div>'
             f'<div>{b}<table class="t" style="margin-top:6pt;font-size:9pt"><tr><th>3–5</th><th>Work</th><th>Answer</th></tr>{rows2}</table></div></div>'
             f'<div class="cols" style="gap:16pt;margin-top:4pt"><div>'
             f'<div class="part" style="margin-top:2pt">Lesson 2 · example verse<small>(page {IX["l2_35"]})</small></div>'
             f'<table class="t" style="font-size:9.5pt"><tr><th>Rhyme</th><th>Line</th><th>Syllables</th></tr>{lyr}</table></div>'
             f'<div><div class="part" style="margin-top:2pt">Lessons 2 and 3</div>'
             f'<p style="font-size:10.5pt;margin:0 0 3pt">Answers are the students’ own. For the K–2 chant, check that each last word fits its note: a one-syllable word on '
             f'<b>ta</b> and a two-syllable word on <b>ti-ti</b>. For the 3–5 verse, check 7 syllables a line and the AABB rhymes. For the listening sheets, accept any answer a student '
             f'can explain.</p></div></div>')
    return page("Answer key · Lesson 1 and Lesson 2 example", "ANSWER KEY", "Lessons 1 and 2", inner, n, watermark, ak=True)


def report_page(n, watermark=False):
    rows = "".join("<tr><td style='height:27pt'></td><td></td><td></td><td></td></tr>" for _ in range(6))
    inner = (f'<div class="how">Substitute: thank you! Please fill this in and leave it on the teacher’s desk.</div>'
             f'<div class="cols" style="gap:16pt"><div>{fl("Your name")}</div><div>{fl("Date")}</div></div>'
             f'<table class="t"><tr><th style="width:24%">Class / grade</th><th style="width:12%">Lesson #</th><th style="width:30%">What we finished</th>'
             f'<th>Notes</th></tr>{rows}</table>'
             f'<div class="part">Students who were a big help<span class="acc"> ·</span></div><div class="ln2"></div><div class="ln2"></div>'
             f'<div class="part">Anything I should know?<span class="acc"> ·</span></div><div class="ln2"></div><div class="ln2"></div><div class="ln2"></div>'
             f'<div class="part">Games we played<span class="acc"> ·</span></div>'
             f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:4pt 14pt;font-size:11pt">'
             + "".join(f'<div>{checkbox(12)} &nbsp;{g}</div>' for g, _, _ in GAMES)
             + f'</div><div class="part">Copies left over<span class="acc"> ·</span></div><div class="ln2"></div>')
    return page("Sub report · notes for the music teacher", "FOR THE SUB", "Leave on the desk", inner, n, watermark)


# ---------------------------------------------------------------- teacher notes and terms
def teacher_page(n):
    trs = "".join(f"<tr><td><b>{a}</b></td><td style='white-space:nowrap'>{prange(f, l)}</td><td>{u}</td></tr>" for a, f, l, u in PARTS)
    return (f'<section class="page doc tn"><div class="rule"><h1>Teacher Notes</h1>'
            f'<div class="l" style="font-size:13pt">Thanksgiving Music Sub Plan K–5 · 3 no-prep lessons</div></div>'
            f'<div class="cols"><div>'
            f'<h2>What it is</h2>'
            f'<p>Three complete music lessons for Thanksgiving week that a substitute can teach with no tech, no instruments and no music background '
            f'(Lesson 3 needs a way to play one piece of music you choose). Each has a step-by-step plan with words to say, timed steps, and two worksheets: one for grades K–2 and one for grades 3–5.</p>'
            f'<h2>The three lessons</h2><ol>'
            + "".join(f"<li><b>{escape(d['title'])}</b>: {d['skill'].lower()}.</li>" for d in LESSONS) +
            f'</ol><p>Use them in any order; each lesson takes 30 to 45 minutes. The welcome sheet has a “Lesson #” column so the sub knows which one each class gets next.</p>'
            f'<h2>Set up the sub tub (about 15 minutes, once)</h2><ol>'
            f'<li>Fill in the welcome sheet (page {IX["welcome"]}), including the listening music for Lesson 3.</li>'
            f'<li>Print the plans, the rhythm chart and the sub report; copy each worksheet for your largest class.</li>'
            f'<li>Put each lesson in its own folder with its worksheets, and add the answer key.</li></ol>'
            f'<h2>Lesson 3 listening music</h2>'
            f'<p>No audio is included. Choose a calm instrumental piece you already have the right to play in class, about 2 to 3 minutes long, and write how to start it on the welcome sheet. '
            f'If your sub has no audio, the plan gives a no-tech sound show instead.</p>'
            f'</div><div>'
            f'<h2>What’s inside</h2><table class="t"><tr><th>Part</th><th>Pages</th><th>Use</th></tr>{trs}</table>'
            f'<h2>About the notation</h2>'
            f'<p>Rhythms are in 4/4 and use quarter notes, paired eighth notes, quarter rests, half notes and whole notes, engraved with a '
            f'professional music font. Every rhythm is read back by computer and checked for 4 beats per bar, except the bars in Lesson 1 part B that '
            f'students must spot as wrong; the key comes from the same checked data. Each example lyric line is counted by computer too.</p>'
            f'<h2>Standards</h2><p>Supports reading rhythm notation (MU:Pr4.2), creating original lyrics and rhythms (MU:Cr2.1) and describing what students hear '
            f'(MU:Re7.2), National Core Arts Standards, Music, grades K–5.</p>'
            f'<h2>Good to know</h2><ul><li>Prints well in black and white.</li><li>Not every family celebrates Thanksgiving. The lessons are about food, '
            f'gratitude and music, with no history lesson and no required beliefs, and every student can pass or choose their own thankful word.</li>'
            f'<li>Rhythm syllables follow the common ta / ti-ti system.</li></ul>'
            f'<p class="small">All lessons, chants, verses, games, words and art are original. No songs, lyrics or copyrighted characters are used.</p>'
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
            f'<li>Lessons, chants, verses, games, art and layouts: original work, {BRAND} by {STORE}.</li>'
            f'<li>Music notation font: Bravura © Steinberg Media Technologies GmbH, SIL Open Font License 1.1.</li>'
            f'<li>Text fonts: Oswald (The Oswald Project Authors) and Source Sans 3 (Adobe), SIL Open Font License 1.1.</li></ul>'
            f'<p class="small">{DISCLOSURE}</p>'
            f'<div style="flex:1"></div>{foot(f"Page {n}")}</section>')


# ---------------------------------------------------------------- cover
def hero_svg(width_css):
    st, end = rhythm_svg(COVER_STRIP, 0, 0, 9, 42, syl=True, syl_size=14)
    w = end
    strip = f'<g transform="translate({300 - w / 2:.1f} 378)">{st}</g>'
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 430" width="{width_css}" style="display:block">'
            f'{turkey_svg(300, 208, FEATHERS)}{strip}</svg>')


def cover_page():
    return (f'<section class="page cover"><div class="store">{BRAND}</div>'
            f'<div style="width:6.9in">{hero_svg("100%")}</div>'
            f'<div class="ctitle"><div class="a">THANKSGIVING MUSIC</div><div class="b">SUB PLAN</div>'
            f'<div class="c">3 no-prep lessons · turkey rhythm reading · gratitude lyrics · listening response</div></div>'
            f'<div class="cband">Grades K–5 <em>·</em> 3 lessons <em>·</em> 6 worksheets <em>·</em> {len(PLAN)} pages</div></section>')


# ---------------------------------------------------------------- assemble
def render_page(key, watermark=False):
    n = IX[key]
    m = re.match(r"l(\d)_plan$", key)
    if m:
        return plan_page(LESSONS[int(m.group(1)) - 1], n, watermark)
    return {
        "cover": cover_page, "teacher": lambda: teacher_page(n), "welcome": lambda: welcome_page(n, watermark),
        "glance": lambda: glance_page(n, watermark), "chart": lambda: chart_page(n, watermark),
        "l1_k2": lambda: l1_k2(n, watermark), "l1_35": lambda: l1_35(n, watermark),
        "l2_k2": lambda: l2_k2(n, watermark), "l2_35": lambda: l2_35(n, watermark),
        "l3_k2": lambda: l3_k2(n, watermark), "l3_35": lambda: l3_35(n, watermark),
        "early": lambda: early_page(n, watermark), "key": lambda: key_page(n, watermark),
        "report": lambda: report_page(n, watermark), "terms": lambda: terms_page(n),
    }[key]()


PREVIEW_PICKS = ["l1_plan", "chart", "l2_35", "key"]


def preview_pages():
    return [render_page(p, watermark=True) for p in PREVIEW_PICKS]

# ---------------------------------------------------------------- square images (2000 x 2000)

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
        f'<div style="width:700px;margin-top:20px">{hero_svg("100%")}</div>'
        f'<div class="hd" style="font-size:66px;margin-top:6px">Thanksgiving Music</div>'
        f'<div class="hd" style="font-size:150px">Sub Plan</div>'
        f'<div class="sub" style="font-size:29px;margin-top:10px">3 no-prep lessons · rhythm reading · gratitude lyrics · listening</div>'
        f'<div class="band">Grades K–5 <em>·</em> 3 lessons <em>·</em> {len(PLAN)} pages</div></div>')


def preview_square_1(img):
    items = [(img[0], "Lesson plan", "timed steps, words to say"), (img[1], "Turkey rhythm chart", "syllables under every note"),
             (img[2], "Lessons at a glance", "plus a no-prep game bank")]
    shots = "".join(
        f'<div style="width:290px"><div class="shot"><img src="{src}"><div class="swm" style="font-size:64px">PREVIEW</div></div>'
        f'<div class="lbl">{a}<span>{b}</span></div></div>' for src, a, b in items)
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div>'
        f'<div class="hd" style="font-size:74px;margin-top:20px">Any sub can teach it</div>'
        f'<div class="sub" style="font-size:27px;margin-top:8px">No music background, no tech, no instruments needed</div>'
        f'<div style="display:flex;gap:28px;margin-top:60px;align-items:flex-start">{shots}</div>'
        f'<div class="band">Rhythm <em>·</em> lyric writing <em>·</em> listening <em>·</em> games</div></div>')


def preview_square_2(a, b):
    pair = "".join(
        f'<div style="position:absolute;left:{x}px;top:{y}px;width:470px"><div class="shot"><img src="{src}">'
        f'<div class="swm" style="font-size:100px">PREVIEW</div></div>'
        f'<div class="lbl" style="position:absolute;{side}:-2px;top:-44px;margin:0">{lab}</div></div>'
        for src, lab, x, y, side in ((a, "Grades K–2", 50, 250, "left"), (b, "Grades 3–5", 476, 300, "right")))
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div>'
        f'<div class="hd" style="font-size:72px;margin-top:20px">Write a gratitude chant</div>'
        f'<div class="sub" style="font-size:27px;margin-top:8px">A K–2 word chant and a 3–5 rhyming verse that fits the beat</div>'
        f'{pair}'
        f'<div class="band">Lyric writing <em>·</em> syllables <em>·</em> rhythm <em>·</em> rhyme</div></div>')


def preview_square_3(imgs):
    cells = "".join(
        f'<div style="width:196px"><div class="shot" style="box-shadow:5px 5px 0 #000"><img src="{src}">'
        f'<div class="swm" style="font-size:44px">PREVIEW</div></div><div class="lbl" style="font-size:17px;margin-top:9px">{lab}</div></div>'
        for src, lab in imgs)
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div>'
        f'<div class="hd" style="font-size:70px;margin-top:16px">Everything inside</div>'
        f'<div class="sub" style="font-size:27px;margin-top:8px">Welcome sheet, 3 plans, 6 worksheets, key and a sub report</div>'
        f'<div style="display:grid;grid-template-columns:repeat(4,196px);gap:20px 26px;margin-top:34px">{cells}</div>'
        f'<div class="band">{len(PLAN)} pages <em>·</em> US Letter PDF <em>·</em> prints in black &amp; white</div></div>')


SHOTS1 = ["l1_plan", "chart", "glance"]
SHOTS2 = ["l2_k2", "l2_35"]
SHOTS3 = [("welcome", "Welcome sheet"), ("l1_k2", "Feather rhythms"), ("l1_35", "Rhythm math"), ("l3_k2", "Listening page"),
          ("l3_35", "Listening response"), ("early", "Early finishers"), ("key", "Answer key"), ("report", "Sub report")]


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


def pdf_png(src, page_no, out, res=110):
    subprocess.run(["pdftoppm", "-png", "-r", str(res), "-f", str(page_no), "-l", str(page_no), "-singlefile", src,
                    os.path.join(BUILD, out)], check=True)


def tpt_json(pages):
    return {
        "price": PRICE, "license_price": PRICE,
        "tax_code": "Other Digital Goods - No Physical Media",
        "grades": ["kindergarten", "2nd-grade", "3rd-grade", "5th-grade"],
        "subjects": ["Music"],
        "tags": ["Thanksgiving", "Autumn"],
        "formats": ["PDF"],
        "pages": pages,
        "answer_key": "Included",
        "files": {"product": f"{SLUG}.pdf", "preview": f"{SLUG}-PREVIEW.pdf", "thumb1": "cover.png",
                  "thumb2": "preview-1.png", "thumb3": "preview-2.png", "thumb4": "preview-3.png"},
    }


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
def verify_data():
    errs = []
    # 1. every engraved rhythm reads back from its drawn SVG, beat-aligned, with 4 beats per bar
    for i, p in enumerate(CHART):
        errs += rhythm_check(f"chart line {i + 1}", p, s=8.6, W=50 if "|" not in p else 33)
    for i, p in enumerate(CHART[:4]):
        if set(p) - set("qer"):
            errs.append(f"chart line {i + 1} is for K-2 but uses {set(p) - set('qer')}")
    if not {"h", "w"} <= set("".join(CHART[4:])):
        errs.append("chart lines 5-8 should introduce ta-a and ta-a-a-a")
    for i, p in enumerate(L1_COUNT):
        errs += rhythm_check(f"Lesson 1 K-2 A{i + 1}", p, s=7.4, W=40)
        if set(p) - set("qer"):
            errs.append(f"Lesson 1 K-2 A{i + 1} uses a symbol K-2 has not met")
    for i, p in enumerate(L1_BARS):
        errs += rhythm_check(f"Lesson 1 3-5 B{i + 1}", p, s=6, W=30, four=False)
    if sorted(nbeats(p) == 4 for p in L1_BARS) != [False] * 3 + [True] * 3:
        errs.append("Lesson 1 part B should have 3 correct and 3 wrong bars")
    for i, p in enumerate(L1_SAY):
        errs += rhythm_check(f"Lesson 1 3-5 C{i + 1}", p, s=7.4, W=52)
    errs += rhythm_check("Lesson 1 3-5 example", L1_EX_35, s=7.4, W=40)
    errs += rhythm_check("Lesson 2 line shape", L2_LINE_SHAPE, s=6.4, W=30)
    errs += rhythm_check("cover strip", COVER_STRIP, s=9, W=42)
    for t in "qerhw":   # single glyphs used in rhythm math, word boxes, feathers
        st = tok_svg(t, 50, 40, 7, 40) + '<line class="bar" x1="80" y1="0" x2="80" y2="1"/><rect class="fin"/>'
        got, e = read_rhythm(st, 7, 40, 50 - 20, timesig=False)
        if got.replace("|", "") != t:
            errs.append(f"single glyph {t} reads back as {got}")
    if len(FEATHERS) != 7 or set(FEATHERS) - set("qerhw"):
        errs.append("cover feathers: need 7 valid rhythm tokens")
    # 2. word rhythms: syllables decide the rhythm, and the printed rhythm agrees
    for label, pairs in (("Lesson 1 K-2 B", L1_WORDS), ("Lesson 2 K-2 examples", L2_EX_K2)):
        for w, t in pairs:
            if word_rhythm(w) != t:
                errs.append(f"{label}: '{w}' has {len(w.split('-'))} syllable(s) but is shown as {SYL[t]}")
    if sorted(L1_BOXES) != sorted(set(t for _, t in L1_WORDS)):
        errs.append("Lesson 1 K-2 part B boxes do not cover the word rhythms exactly once")
    if len(L2_STEM) != 3 or any(len(w.split("-")) != 1 for w in L2_STEM):
        errs.append("Lesson 2 K-2 stem must be 3 one-syllable words (3 beats)")
    for w in L2_BANK1:
        if len(w.split("-")) != 1:
            errs.append(f"Lesson 2 bank (1 syllable): '{w}'")
    for w in L2_BANK2:
        if len(w.split("-")) != 2:
            errs.append(f"Lesson 2 bank (2 syllables): '{w}'")
    # 3. Lesson 2 lyrics: 7 syllables a line + one rest = 8 beats; AABB
    if nbeats(L2_LINE_SHAPE.split("|")[0]) != 4 or nbeats(L2_LINE_SHAPE.split("|")[1]) != 4:
        errs.append("Lesson 2 line shape bars are not 4 beats")
    if nsounds(L2_LINE_SHAPE) != L2_SYLLABLES or L2_LINE_SHAPE.count("r") != 1:
        errs.append("Lesson 2 line shape: needs 7 sounded beats and one rest")
    for ln, g in L2_LINES:
        if syl_count(ln) != L2_SYLLABLES:
            errs.append(f"Lesson 2 example line '{ln}' has {syl_count(ln)} syllables, not {L2_SYLLABLES}")
    if [g for _, g in L2_LINES] != list("AABB"):
        errs.append("Lesson 2 example verse must rhyme AABB")
    # 4. rhythm math is 2-3 terms, syllable table matches the token table
    for p in L1_MATH:
        if not 2 <= len(p) <= 3:
            errs.append(f"rhythm math item {p} length")
    if SYL != {"q": "ta", "e": "ti-ti", "r": "shh", "h": "ta-a", "w": "ta-a-a-a"} or BEATS != {"q": 1, "e": 1, "r": 1, "h": 2, "w": 4}:
        errs.append("syllable/beat table changed")
    # 5. plan and teacher table
    if len(PLAN) != len(set(PLAN)):
        errs.append("plan has a repeated page")
    covered = set()
    for _, a, b, _ in PARTS:
        covered |= set(PLAN[IX[a] - 1:IX[b]])
    if covered | {"cover", "teacher"} != set(PLAN):
        errs.append(f"teacher table misses pages: {sorted(set(PLAN) - covered - {'cover', 'teacher'})}")
    for d in LESSONS:
        if not 30 <= sum(int(m) for m, _, _ in d["steps"]) <= 45:
            errs.append(f"Lesson {d['n']} steps add to {sum(int(m) for m, _, _ in d['steps'])} min, not 30-45")
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




def key_text_errors(txt):
    """The answers printed in the PDF's key page equal the checked data."""
    errs = []
    t = re.sub(r"\s+", " ", txt[IX["key"] - 1])
    for i, p in enumerate(L1_COUNT):
        if f"A{i + 1} {syllables(p)} {nsounds(p)}" not in t:
            errs.append(f"Key: K-2 A{i + 1} '{syllables(p)} {nsounds(p)}' not found")
    for w, tk in L1_WORDS:
        if f"B · {w} {SYL[tk]} {'ABC'[L1_BOXES.index(tk)]}" not in t:
            errs.append(f"Key: K-2 B '{w}' not found")
    for i, p in enumerate(L1_MATH):
        if f"A{i + 1} {'+'.join(str(BEATS[x]) for x in p)} {nbeats(p)}" not in re.sub(r" ?\+ ?", "+", t):
            errs.append(f"Key: 3-5 A{i + 1} sum not found")
    for i, p in enumerate(L1_BARS):
        if f"B{i + 1} {syllables(p)} {'YES' if nbeats(p) == 4 else 'NO'} · {nbeats(p)}" not in t:
            errs.append(f"Key: 3-5 B{i + 1} not found")
    for i, p in enumerate(L1_SAY):
        if f"C{i + 1} {syllables(p)}" not in t:
            errs.append(f"Key: 3-5 C{i + 1} not found")
    for ln, g in L2_LINES:
        if f"{g} {ln} {syl_count(ln)}" not in t:
            errs.append(f"Key: lyric line '{ln}' not found with its syllable count")
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
    errs += key_text_errors(txt)
    alltext = " ".join(flat).lower()
    for bad in BANNED:
        if re.search(rf"\b{bad}\b", alltext):
            errs.append(f"resource text mentions '{bad}'")
    for m in re.finditer(r"[Pp]ages? (\d+)(?:–(\d+))?", " ".join(flat[1:])):
        for g in m.groups():
            if g and not 1 <= int(g) <= len(PLAN):
                errs.append(f"cross-reference to page {g} does not exist")
    for d in LESSONS:  # each plan names its own sheets' pages
        k = d["n"]
        for s_ in ("k2", "35"):
            if f"page {IX[f'l{k}_{s_}']}" not in flat[IX[f"l{k}_plan"] - 1]:
                errs.append(f"Lesson {k} plan does not point to its {s_} sheet")
    for key in ("l1_k2", "l1_35"):
        if f"Answer key on page {IX['key']}" not in flat[IX[key] - 1]:
            errs.append(f"{key}: answer-key cross-reference missing")
    if "page " + str(IX["chart"]) not in flat[IX["l1_plan"] - 1]:
        errs.append("Lesson 1 plan does not point to the rhythm chart")
    if "page " + str(IX["welcome"]) not in flat[IX["l3_plan"] - 1]:
        errs.append("Lesson 3 plan does not point to the welcome sheet (listening music)")
    for ln, g in L2_LINES:
        if ln not in flat[IX["l2_35"] - 1]:
            errs.append(f"Lesson 2 3-5 sheet does not show example line '{ln}'")
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
    if not m2 or DISCLOSURE not in m2.group(1):
        errs.append("UPLOAD.md: description block missing the disclosure line")
    elif any(re.search(rf"\b{b}\b", m2.group(1).lower()) for b in BANNED):
        errs.append("UPLOAD.md: description uses a banned word")
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
    nr = len(CHART) + len(L1_COUNT) + len(L1_BARS) + len(L1_SAY) + 4
    print(f"CHECK OK: {nr} engraved rhythms read back from the drawn SVG (glyphs, beamed pairs, beat slots, barlines) and match the data, "
          f"4 beats per bar except Lesson 1's 3 deliberate wrong bars; word rhythms match syllable counts; Lesson 2 lyric lines are 7 syllables each (AABB) and fit 7 beats + a rest; Lesson 1 key text in the PDF "
          f"matches the data; {len(PLAN)} Letter pages with footers and page numbers; "
          f"only Bravura/Oswald/Source Sans 3, all embedded; preview {len(PREVIEW_PICKS)} watermarked pages; images 2000x2000; "
          f"tpt.json and UPLOAD.md ok.")


if __name__ == "__main__":
    if "--check" in sys.argv:
        check()
    else:
        build()
