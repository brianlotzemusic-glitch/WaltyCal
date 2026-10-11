#!/usr/bin/env python3
"""Music Sub Plans K-5: 5 No-Prep Emergency Days (TpT 007): build the resource and verify it.

    python3 gen.py            build everything (PDFs, PNGs, tpt.json) into this folder
    python3 gen.py --lowres   same, but square images at scale 1 (self-check only; --check rejects them)
    python3 gen.py --check    verify rhythms, keys, word search, pages, fonts and files

Five no-tech, no-prep music days for a substitute, each with a scripted plan page and
two worksheets (K-2 and 3-5): listening log, rhythm reading, dynamics and tempo,
composing, and music words. Plus a sub welcome sheet, days-at-a-glance with a game
bank, a big rhythm chart the sub can read without knowing music (syllables printed
under every note), early-finisher page, answer keys and a sub report form.

Musical accuracy is checked end to end: every engraved rhythm is drawn to SVG, the
SVG is parsed back (glyph codepoints, beamed pairs, x position inside its beat slot,
barlines) and the read-back rhythm must equal the data, each bar must hold 4 beats
(except the deliberate wrong bars on Day 2, whose printed key is computed), and the
syllables, sound counts and beat sums printed on the keys come from that data.
No songs, lyrics or copyrighted characters; all chants and games are original text.
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


R = _load("rhythm002", "002-fall-rhythm-flashcards/rhythm.py")

FONTS = os.path.join(TPT, "fonts")
BUILD = os.path.join(HERE, "build")
RENDER_JS = os.path.join(TPT, "tools", "render.js")

SLUG = "music-sub-plans-k5"
PDF = os.path.join(HERE, f"{SLUG}.pdf")
PREVIEW_PDF = os.path.join(HERE, f"{SLUG}-PREVIEW.pdf")
COVER_PNG = os.path.join(HERE, "cover.png")
PREVIEW_PNGS = [os.path.join(HERE, f"preview-{i}.png") for i in (1, 2, 3)]
UPLOAD = os.path.join(HERE, "UPLOAD.md")
TPT_JSON = os.path.join(HERE, "tpt.json")

STORE = "Brian Lotze"      # copyright holder
BRAND = "Hudson Beat"      # store line on covers and previews (owner, 4 Oct)
YEAR = 2026
ACCENT = "#1F7A8C"         # this product's single accent (calm teal: year-round, not tied to a season)
TITLE = "Music Sub Plans"
PRICE = "7.00"
LOW_RES = "--lowres" in sys.argv

BANNED = ("christmas", "xmas", "santa", "hanukkah", "chanukah", "kwanzaa", "nativity", "jesus", "holiday", "advent",
          "reindeer", "jingle", "carol", "menorah", "elf", "elves", "youtube", "spotify")

# ---------------------------------------------------------------- rhythm data
# tokens: q ta (1 beat), e ti-ti (beamed pair, 1 beat), r shh (quarter rest, 1 beat), h ta-a (2), w ta-a-a-a (4); "|" = barline
BEATS = {"q": 1, "e": 1, "r": 1, "h": 2, "w": 4}
SOUNDS = {"q": 1, "e": 2, "r": 0, "h": 1, "w": 1}
SYL = {"q": "ta", "e": "ti-ti", "r": "shh", "h": "ta-a", "w": "ta-a-a-a"}
NAMES = {"q": "quarter note", "e": "two eighth notes", "r": "quarter rest", "h": "half note", "w": "whole note"}

CHART = ["qqqr", "eeqq", "qeqe", "erqq",                   # lines 1-4: K-2 (ta, ti-ti, shh)
         "hqq|eeh", "qeqe|w", "qrh|eeqr", "eqrq|hh"]       # lines 5-8: 3-5 (adds ta-a and ta-a-a-a), two bars

D2_COUNT = ["qqqq", "eqqq", "qrqr", "eeqq", "eeee", "qeqr"]          # K-2 part A: how many sounds?
D2_WORDS = [("dog", "q"), ("tur-tle", "e"), ("shh", "r"), ("sun", "q")]  # K-2 part B: word -> rhythm box
D2_BOXES = ["e", "r", "q"]                                             # boxes A, B, C
D2_MATH = ["qqh", "hh", "wq", "eqr", "hee", "whq"]                     # 3-5 part A: add the beats
D2_BARS = ["qqeq", "hq", "qrh", "eeqh", "wq", "eeer"]                  # 3-5 part B: is it 4 beats?
D2_SAY = ["qeh", "eqrq"]                                               # 3-5 part C: write the syllables

D4_BANK_K2 = [("cat", "q"), ("piz-za", "e"), ("shh", "r"), ("dog", "q"), ("ap-ple", "e")]
D4_EXAMPLE_K2 = [("cat", "q"), ("piz-za", "e"), ("dog", "q"), ("shh", "r")]
D4_EXAMPLE_35 = "qeh|eeqr"
COVER_STRIP = "qeqr"


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


# ---------------------------------------------------------------- dynamics and tempo (Day 3)
DYN = [  # (symbol id, meaning) softest to loudest, then the hairpins
    ("pp", "very soft (pianissimo)"), ("p", "soft (piano)"), ("mp", "medium soft (mezzo piano)"),
    ("mf", "medium loud (mezzo forte)"), ("f", "loud (forte)"), ("ff", "very loud (fortissimo)"),
    ("cresc", "get louder little by little (crescendo)"), ("dim", "get softer little by little (decrescendo)")]
DYN_GLYPH = {"pp": 0xE52B, "p": 0xE520, "mp": 0xE52C, "mf": 0xE52D, "f": 0xE522, "ff": 0xE52F}
TEMPO = [("largo", "very slow and broad"), ("adagio", "slow"), ("andante", "walking speed"),
         ("moderato", "medium speed"), ("allegro", "fast and lively"), ("presto", "very fast")]
D3_SOUNDS = [("a lion's roar", "f"), ("a whisper", "p"), ("a fire truck siren", "f"), ("a kitten's purr", "p"),
             ("a big bass drum", "f"), ("tiptoe footsteps", "p")]
D3_SPEED = [("a cheetah running", "FAST"), ("a turtle walking", "SLOW"), ("a race car", "FAST"), ("a snail crawling", "SLOW")]

# ---------------------------------------------------------------- music words (Day 5)
OPPOSITES = [("LOUD", "SOFT"), ("HIGH", "LOW"), ("FAST", "SLOW")]
OPP_RIGHT = ["SLOW", "SOFT", "LOW"]           # right column order on the K-2 sheet
TRACE = ["BEAT", "SING", "CLAP", "DRUM"]
WS_WORDS = ["BEAT", "RHYTHM", "TEMPO", "PIANO", "FORTE", "MELODY", "PITCH", "STAFF", "REST", "TREBLE", "DYNAMICS", "CRESCENDO"]
WS_N = 12
WS_DIRS = [(0, 1), (1, 0), (1, 1)]            # across, down, diagonal down-right (no backwards words for grade 3)
BAD_WORDS = ["SEX", "ASS", "FUK", "FUC", "DIE", "DEAD", "KILL", "POO", "PEE", "BUTT", "DAMN", "HELL", "GUN", "NAZI", "TIT", "CUM",
             "UGLY", "DUMB", "HATE", "PIS", "DICK", "COCK", "SHIT", "FART", "BOOB", "CRAP", "SUCK", "STUPID", "WAR", "GOD", "DRUG", "BOMB"]
ALL_DIRS = [(dr, dc) for dr in (-1, 0, 1) for dc in (-1, 0, 1) if (dr, dc) != (0, 0)]


def count_word(grid, w):
    n = len(grid)
    c = 0
    for r in range(n):
        for k in range(n):
            for dr, dc in ALL_DIRS:
                if all(0 <= r + dr * i < n and 0 <= k + dc * i < n and grid[r + dr * i][k + dc * i] == w[i] for i in range(len(w))):
                    c += 1
    return c


def make_wordsearch(seed=7007):
    rnd = random.Random(seed)
    for _ in range(2000):
        g = [[None] * WS_N for _ in range(WS_N)]
        place = {}
        ok = True
        for w in sorted(WS_WORDS, key=len, reverse=True):
            for _try in range(400):
                dr, dc = rnd.choice(WS_DIRS)
                r = rnd.randrange(WS_N - (len(w) - 1) * dr)
                c = rnd.randrange(WS_N - (len(w) - 1) * dc)
                cells = [(r + dr * i, c + dc * i) for i in range(len(w))]
                if all(g[y][x] in (None, w[i]) for i, (y, x) in enumerate(cells)):
                    for i, (y, x) in enumerate(cells):
                        g[y][x] = w[i]
                    place[w] = cells
                    break
            else:
                ok = False
                break
        if not ok:
            continue
        dirs = {(cells[1][0] - cells[0][0], cells[1][1] - cells[0][1]) for cells in place.values()}
        if len(dirs) < 3:
            continue
        for y in range(WS_N):
            for x in range(WS_N):
                if g[y][x] is None:
                    g[y][x] = rnd.choice("ABCDEFGHIKLMNOPRSTUVWY")
        if all(count_word(g, w) == 1 for w in WS_WORDS) and not any(count_word(g, b) for b in BAD_WORDS):
            return g, place
    raise SystemExit("word search: no clean grid found")


GRID, PLACE = make_wordsearch()

# ---------------------------------------------------------------- notation
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
        "d1_plan", "d1_k2", "d1_35", "d2_plan", "d2_k2", "d2_35", "d3_plan", "d3_k2", "d3_35",
        "d4_plan", "d4_k2", "d4_35", "d5_plan", "d5_k2", "d5_35",
        "early", "key_d2", "key_d35", "report", "terms"]
IX = {k: i + 1 for i, k in enumerate(PLAN)}


def pg(k):
    return f"page {IX[k]}"


DAYS = [
    {"n": 1, "short": "Skip step 2 and keep the worksheet.", "title": "Sound Detectives", "skill": "Listening and describing sounds",
     "goal": "Students listen closely and describe sounds as loud or soft, high or low, long or short.",
     "materials": "Pencils, the worksheets, and a few classroom objects (pencil, paper, a book, keys).",
     "steps": [
         ("5", "Echo me", "Say: <span class=say>“Good morning, musicians! I’m your guest teacher today. Let’s warm up. Echo me!”</span> "
                          "Say each line in a clear voice and let the class repeat it: <i>Ears are on. Eyes are up. Hands are still. "
                          "Let’s make music!</i> Do it again once quietly and once in a strong voice (strong, not shouting)."),
         ("5", "One-minute listen", "Everyone closes their eyes (or looks down) and stays silent for one minute. "
                                    "Say: <span class=say>“Count how many different sounds you hear.”</span> Then ask 3 or 4 students to share one sound each."),
         ("10", "Guest teacher sound show", "Students close their eyes while you make a sound; they guess what it was. Try: tap a pencil on a desk, "
                                            "crumple paper, knock on the door, clap once, rattle keys, zip a bag, flip book pages, whisper “hello”. "
                                            "For each one ask: <b>Loud or soft? High or low? Long or short?</b>"),
         ("15", "Listening log", "Hand out the worksheet: <b>K–2</b> My Listening Log (PG:d1_k2), <b>3–5</b> Listening Log (PG:d1_35). "
                                 "Read the directions aloud. Make the sounds again, one at a time, while students fill in their sheets."),
         ("5", "Copy my sound", "One student makes a short body-percussion sound (pat, clap, snap, stomp). The class copies it. "
                                "The leader picks the next leader."),
     ],
     "extra": "Play Hot and Cold Dynamics or Freeze Beat from the game bank (PG:glance)."},
    {"n": 2, "short": "Shorten step 2 to lines 1–4 and keep the worksheet.", "title": "Rhythm Readers", "skill": "Steady beat and reading rhythm",
     "goal": "Students keep a steady beat and read and clap simple rhythms with rhythm syllables.",
     "materials": "Pencils, the worksheets, the rhythm chart (PG:chart). No music reading needed: the syllables are printed under every note.",
     "steps": [
         ("5", "Copy the beat", "Pat a slow, steady beat on your legs. Say: <span class=say>“Copy me!”</span> Switch to clapping, then tapping "
                                "shoulders, at the same speed. Say: <span class=say>“This steady pulse is called the beat.”</span>"),
         ("10", "Rhythm chart echoes", "Show the rhythm chart (PG:chart) or copy one line at a time on the board. Clap and say a line; the class echoes. "
                                       "<b>ta</b> = one clap, <b>ti-ti</b> = two quick claps in one beat, <b>shh</b> = a silent beat (open hands), "
                                       "<b>ta-a</b> = one clap held for 2 beats. K–2 use lines 1–4; 3–5 use all 8."),
         ("15", "Worksheet", "<b>K–2</b> Rhythm Readers (PG:d2_k2): read Part B aloud. <b>3–5</b> Rhythm Math (PG:d2_35). "
                             "Answer keys are on PG:key_d2."),
         ("10", "Poison Rhythm", "Pick one chart line as the poison rhythm and show it. Clap other lines; the class echoes. When you clap the "
                                 "poison rhythm, everyone stays silent. Anyone who claps it becomes a judge. Change the poison line each round."),
     ],
     "extra": "Let students take turns as the leader for Poison Rhythm."},
    {"n": 3, "short": "Skip step 3 and keep the worksheet.", "title": "Loud & Soft, Fast & Slow", "skill": "Dynamics and tempo",
     "goal": "Students show and name dynamics (how loud or soft) and tempo (how fast or slow).",
     "materials": "Pencils, the worksheets, one small object to hide (an eraser).",
     "steps": [
         ("5", "Voice dynamics", "Say: <span class=say>“Dynamics means how loud or soft the music is. Piano means soft. Forte means loud.”</span> "
                                 "Say <i>Music is fun!</i>; the class echoes it in a piano voice, then a forte voice (strong, never shouting)."),
         ("10", "Hot and Cold Dynamics", "One student covers their eyes while another hides the eraser in the room. The seeker looks for it while "
                                         "the class claps a steady beat: soft when the seeker is far away, louder as they get closer. Play 3 or 4 rounds."),
         ("5", "Tempo walk", "Say: <span class=say>“Tempo means how fast or slow.”</span> Clap a beat while students walk in place (or pat their legs). "
                             "Try very slow (<i>largo</i>), walking speed (<i>andante</i>), fast (<i>allegro</i>), very fast (<i>presto</i>). "
                             "When you stop, they freeze."),
         ("15", "Worksheet", "<b>K–2</b> Loud or Soft? (PG:d3_k2): read each sound in Parts B and C aloud. <b>3–5</b> Dynamics and Tempo "
                             "(PG:d3_35). Answer keys are on PG:key_d35."),
         ("5", "Silent Conductor", "A student conducts the class’s clapping: hands far apart = loud, close together = soft, "
                                   "fast or slow moves = tempo, fists closed = stop. Take turns."),
     ],
     "extra": "Echo short lines from the rhythm chart (PG:chart) at different dynamics and tempos."},
    {"n": 4, "short": "Skip step 2 and show the example on the worksheet instead.", "title": "Rhythm Composers", "skill": "Composing and performing rhythms",
     "goal": "Students create their own 4-beat rhythms, check the beats, and perform them.",
     "materials": "Pencils, the worksheets, the rhythm chart (PG:chart).",
     "steps": [
         ("5", "Chart review", "Clap and say lines 1–4 of the rhythm chart (PG:chart); the class echoes. 3–5 classes add lines 5–8."),
         ("10", "Word rhythms", "Say a word and clap its syllables: <i>cat</i> = ta (one clap), <i>piz-za</i> = ti-ti (two quick claps), "
                                "<i>shh</i> = a silent beat. Students suggest more words: one syllable = ta, two syllables = ti-ti."),
         ("15", "Compose", "<b>K–2</b> Word Rhythm Composer (PG:d4_k2). <b>3–5</b> Rhythm Composer (PG:d4_35). "
                           "Walk around and ask: <span class=say>“Does each box (or bar) have the right number of beats?”</span>"),
         ("10", "Composer concert", "Volunteers clap and say their rhythm while the class pats a steady beat, then the class echoes it. "
                                    "Clap for every composer!"),
     ],
     "extra": "Partners trade sheets and clap each other’s rhythms."},
    {"n": 5, "short": "Skip step 2 and keep the worksheet.", "title": "Music Word Games", "skill": "Music vocabulary",
     "goal": "Students review music words: beat, rhythm, dynamics, tempo, pitch and more.",
     "materials": "Pencils and the worksheets.",
     "steps": [
         ("5", "Show me", "Call out a word; students show it. <b>High:</b> hands up and a high “ooo”. <b>Low:</b> hands down and a low “ooo”. "
                          "<b>Loud / soft:</b> big or small claps. <b>Fast / slow:</b> pat fast or slow."),
         ("10", "Rhythm Telephone", "Students sit in a circle or line. Clap a short rhythm from the chart (PG:chart) to the first student, who claps "
                                    "it to the next, and so on. Does it reach the end the same? Start a new rhythm each round."),
         ("15", "Worksheet", "<b>K–2</b> Music Opposites (PG:d5_k2). <b>3–5</b> Music Word Search (PG:d5_35). Answer keys are on PG:key_d35."),
         ("5", "Freeze Beat", "Pat a steady beat while students move in place (march, sway, tiptoe). When you stop, everyone freezes. "
                              "Anyone who moves helps you keep the beat."),
     ],
     "extra": "Early finishers: the drawing and rhythm page (PG:early)."},
]

GAMES = [
    ("Echo Me", "Say or clap a short line; the class repeats it exactly. Change the dynamics (soft, strong) and the speed.", "1"),
    ("Poison Rhythm", "Pick a chart line as the poison. Clap lines; the class echoes all but the poison rhythm.", "2"),
    ("Hot and Cold Dynamics", "Hide an eraser. The class claps softly when the seeker is far away and louder when close.", "3"),
    ("Silent Conductor", "A student conducts the class’s claps: hands far apart = loud, close = soft, fists = stop.", "3"),
    ("Rhythm Telephone", "Pass a clapped rhythm from student to student. Does it arrive the same?", "5"),
    ("Freeze Beat", "Move in place to a steady beat; freeze when the beat stops.", "5"),
    ("Copy My Sound", "A leader makes a body-percussion sound; everyone copies; the leader picks the next leader.", "1"),
]

DAY_SHEETS = {  # day: (K-2 title, 3-5 title)
    1: ("My Listening Log", "Listening Log"),
    2: ("Rhythm Readers", "Rhythm Math"),
    3: ("Loud or Soft?", "Dynamics and Tempo"),
    4: ("Word Rhythm Composer", "Rhythm Composer"),
    5: ("Music Opposites", "Music Word Search"),
}

PARTS = [  # (label, first key, last key, use)
    ("For the substitute", "welcome", "glance", "welcome sheet, days at a glance, game bank"),
    ("Rhythm chart", "chart", "chart", "8 lines with syllables, for Days 2, 4 and 5"),
    ("Day 1 · Sound Detectives", "d1_plan", "d1_35", "plan + K–2 and 3–5 sheets"),
    ("Day 2 · Rhythm Readers", "d2_plan", "d2_35", "plan + K–2 and 3–5 sheets"),
    ("Day 3 · Loud & Soft, Fast & Slow", "d3_plan", "d3_35", "plan + K–2 and 3–5 sheets"),
    ("Day 4 · Rhythm Composers", "d4_plan", "d4_35", "plan + K–2 and 3–5 sheets"),
    ("Day 5 · Music Word Games", "d5_plan", "d5_35", "plan + K–2 and 3–5 sheets"),
    ("Early finishers", "early", "early", "draw, write and clap, K–5"),
    ("Answer keys", "key_d2", "key_d35", "Days 2, 3 and 5"),
    ("Sub report", "report", "report", "notes back to you"),
    ("Terms of use", "terms", "terms", "license and credits"),
]


def prange(a, b):
    return str(IX[a]) if a == b else f"{IX[a]}–{IX[b]}"


def fill_pages(s):
    return re.sub(r"PG:(\w+)", lambda m: pg(m.group(1)), s)


# ---------------------------------------------------------------- shared art
def dyn_svg(sym, cx, base, size, fill="#000"):
    """A dynamic mark: Bravura letters, or a hairpin drawn with lines (size = height in pt)."""
    if sym in DYN_GLYPH:
        return (f'<text x="{cx:.1f}" y="{base:.1f}" font-family="Bravura" font-size="{size * 2.2:.1f}" text-anchor="middle" '
                f'fill="{fill}">&#x{DYN_GLYPH[sym]:X};</text>')
    w, h = size * 2.6, size * 0.9
    y = base - size * 0.45
    if sym == "cresc":
        d = f"M{cx + w / 2:.1f} {y - h / 2:.1f} L{cx - w / 2:.1f} {y:.1f} L{cx + w / 2:.1f} {y + h / 2:.1f}"
    else:
        d = f"M{cx - w / 2:.1f} {y - h / 2:.1f} L{cx + w / 2:.1f} {y:.1f} L{cx - w / 2:.1f} {y + h / 2:.1f}"
    return f'<path d="{d}" fill="none" stroke="{fill}" stroke-width="{max(1.2, size * 0.07):.2f}" stroke-linejoin="miter"/>'


def clipboard_svg(x, y, w, h, ticks=3, accent=ACCENT):
    """Line-art clipboard with a 5-day checklist and a rhythm strip (cover art)."""
    sw = 2.4
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="16" fill="#fff" stroke="#000" stroke-width="{sw}"/>',
           f'<rect x="{x + 18}" y="{y + 30}" width="{w - 36}" height="{h - 48}" rx="4" fill="#fff" stroke="#000" stroke-width="{sw * .8}"/>',
           f'<rect x="{x + w / 2 - 52}" y="{y - 14}" width="104" height="40" rx="9" fill="{accent}" stroke="#000" stroke-width="{sw}"/>',
           f'<circle cx="{x + w / 2}" cy="{y - 2}" r="6" fill="#fff" stroke="#000" stroke-width="{sw * .8}"/>',
           text(x + w / 2, y + 66, "SUB PLANS", 25, 700, extra='letter-spacing="2"')]
    for i in range(5):
        ry = y + 92 + i * 34
        out.append(f'<rect x="{x + 40}" y="{ry}" width="20" height="20" rx="3" fill="#fff" stroke="#000" stroke-width="2"/>')
        if i < ticks:
            out.append(f'<path d="M{x + 43} {ry + 10} L{x + 49} {ry + 17} L{x + 59} {ry + 3}" fill="none" stroke="{accent}" stroke-width="3.6" '
                       f'stroke-linecap="round" stroke-linejoin="round"/>')
        out.append(text(x + 72, ry + 16, f"DAY {i + 1}", 15, 700, anchor="start"))
        out.append(f'<line x1="{x + 128}" y1="{ry + 14}" x2="{x + w - 40}" y2="{ry + 14}" stroke="#000" stroke-width="1.3" '
                   f'stroke-dasharray="{"" if i < ticks else "3 4"}"/>')
    return "".join(out)


def pencil_svg(x, y, length, angle, accent=ACCENT):
    return (f'<g transform="translate({x} {y}) rotate({angle})">'
            f'<rect x="0" y="-11" width="{length}" height="22" rx="3" fill="#fff" stroke="#000" stroke-width="2.2"/>'
            f'<rect x="0" y="-11" width="22" height="22" rx="3" fill="{accent}" stroke="#000" stroke-width="2.2"/>'
            f'<line x1="26" y1="-11" x2="26" y2="11" stroke="#000" stroke-width="2.2"/>'
            f'<path d="M{length} -11 L{length + 30} 0 L{length} 11 Z" fill="#fff" stroke="#000" stroke-width="2.2" stroke-linejoin="round"/>'
            f'<path d="M{length + 20} -3.7 L{length + 30} 0 L{length + 20} 3.7 Z" fill="#000"/></g>')


# ---------------------------------------------------------------- substitute pages
def welcome_page(n, watermark=False):
    rows = "".join(f"<tr><td style='height:25pt'></td><td></td><td></td><td></td></tr>" for _ in range(7))
    inner = (f'<div class="how">Teacher: fill this in once and keep it on top of the sub folder. Substitute: welcome, and thank you! '
             f'Everything you need for today is in this folder.</div>'
             f'<div class="cols" style="gap:16pt"><div>{fl("Teacher")}{fl("Room")}{fl("School office ext.")}</div>'
             f'<div>{fl("Nearby teacher who can help")}{fl("Their room")}{fl("Date updated")}</div></div>'
             f'<div class="part">Today’s classes<span class="acc"> ·</span><small>Use the day number you have not used yet with that class.</small></div>'
             f'<table class="t"><tr><th style="width:18%">Time</th><th style="width:30%">Class / grade</th><th style="width:14%">Day #</th><th>Notes</th></tr>{rows}</table>'
             f'<div class="cols" style="gap:16pt;margin-top:6pt"><div>'
             f'<div class="part">How we do things<span class="acc"> ·</span></div>'
             f'{fl("Attention signal")}{fl("Entering the room")}{fl("Where students sit")}{fl("Bathroom / water")}{fl("Lining up / dismissal")}'
             f'</div><div>'
             f'<div class="part">Where things are<span class="acc"> ·</span></div>'
             f'{fl("Copies of worksheets")}{fl("Pencils")}{fl("Seating charts")}{fl("Emergency plans")}{fl("Class lists")}'
             f'</div></div>'
             f'<div class="part">Helpful students<span class="acc"> ·</span><small>Keep private student information in the office file, not here.</small></div>'
             f'<div class="cols" style="gap:16pt"><div>{fl("")}{fl("")}</div><div>{fl("")}{fl("")}</div></div>'
             f'<div class="box" style="margin-top:4pt;font-size:10.5pt"><b>No music background needed.</b> Each day has a step-by-step plan with words to say, '
             f'and every rhythm has its syllables printed under the notes. Please leave notes on the sub report ({pg("report")}).</div>')
    return page("Welcome, substitute · fill in and keep on top", "FOR THE SUB", "Welcome sheet", inner, n, watermark)


def glance_page(n, watermark=False):
    rows = ""
    for d in DAYS:
        k = d["n"]
        rows += (f"<tr><td class='ans' style='font-size:13pt;text-align:center'>{k}</td><td><b>{escape(d['title'])}</b><br>"
                 f"<span class='small'>{d['skill']}</span></td><td>{escape(DAY_SHEETS[k][0])}<br><span class='small'>{pg(f'd{k}_k2')}</span></td>"
                 f"<td>{escape(DAY_SHEETS[k][1])}<br><span class='small'>{pg(f'd{k}_35')}</span></td>"
                 f"<td style='text-align:center'>{IX[f'd{k}_plan']}</td></tr>")
    games = "".join(f"<tr><td><b>{g}</b></td><td>{t}</td><td style='text-align:center'>{dd}</td></tr>" for g, t, dd in GAMES)
    inner = (f'<div class="how">Each day is one 30–45 minute music class. Every day works for any grade K–5: use the plan page, then hand out '
             f'the <b>K–2</b> or <b>3–5</b> sheet. The days can be used in any order.</div>'
             f'<table class="t"><tr><th style="width:8%">Day</th><th style="width:31%">Lesson</th><th>K–2 sheet</th><th>3–5 sheet</th>'
             f'<th style="width:11%">Plan page</th></tr>{rows}</table>'
             f'<div class="part" style="margin-top:12pt">Game bank<span class="acc"> ·</span><small>No-prep games for extra time. No equipment, no tech.</small></div>'
             f'<table class="t"><tr><th style="width:25%">Game</th><th>How to play</th><th style="width:9%">Day</th></tr>{games}</table>'
             f'<div class="part" style="margin-top:12pt">Tips for a calm class<span class="acc"> ·</span></div>'
             f'<ul style="margin:0;padding-left:15pt;font-size:10.6pt;line-height:1.4">'
             f'<li>Use the teacher’s attention signal from the welcome sheet ({pg("welcome")}), or clap a short rhythm and have the class clap it back.</li>'
             f'<li>“Strong voice, not shouting” keeps the forte parts happy and safe.</li>'
             f'<li>If a game gets too loud, switch to a worksheet or Freeze Beat.</li></ul>')
    return page("Days at a glance and game bank", "FOR THE SUB", "5 days, any order", inner, n, watermark)


def chart_page(n, watermark=False):
    s, W = 8.6, 50
    rows = []
    for i, p in enumerate(CHART):
        st, _ = rhythm_svg(p, 14, 34, s, W if "|" not in p else 33, syl=True, syl_size=12.5)
        lab = (f'<div style="flex:0 0 34pt;text-align:center"><div class="h" style="font-size:22pt">{i + 1}</div>'
               f'<div class="l" style="font-size:9pt">{"K–5" if i < 4 else "3–5"}</div></div>')
        rows.append(f'<div style="display:flex;align-items:center;border-bottom:1pt solid #bbb;padding:0">{lab}{svg(470, 68, st)}</div>')
    key = " · ".join(f"<b>{SYL[t]}</b> = {NAMES[t]} ({BEATS[t]} beat{'s' if BEATS[t] > 1 else ''})" for t in "qerhw")
    inner = (f'<div class="how">Clap and say each line; the class echoes. Say the words under the notes; you do not need to read music. '
             f'Silent beats (<b>shh</b>): open your hands, no sound.</div>'
             f'<div style="border-top:1pt solid #bbb">{"".join(rows)}</div>'
             f'<div class="small" style="margin-top:6pt;font-size:9.5pt !important">{key}</div>')
    return page("Rhythm chart · show it or copy a line on the board", "FOR THE SUB", "Days 2, 4 and 5", inner, n, watermark)


def plan_page(d, n, watermark=False):
    k = d["n"]
    steps = "".join(
        f'<li><div class="tm"><b>{m} min</b><span>Step {i + 1}</span></div><div class="tx"><b class="hd">{escape(h)}</b><br>{fill_pages(t)}</div></li>'
        for i, (m, h, t) in enumerate(d["steps"]))
    total = sum(int(m) for m, _, _ in d["steps"])
    inner = (f'<div class="meta"><div><b class="k">Goal</b>{d["goal"]}</div><div><b class="k">You need</b>{fill_pages(d["materials"])}</div>'
             f'<div style="flex:0 0 1.55in"><b class="k">Copies</b>K–2: {pg(f"d{k}_k2")}<br>3–5: {pg(f"d{k}_35")}<br>'
             f'<span class="small">about {total} min</span></div></div>'
             f'<div class="part" style="margin-top:10pt">Step by step<span class="acc"> ·</span><small>Italic lines are words you can say.</small></div>'
             f'<ol class="steps">{steps}</ol>'
             f'<div class="box" style="margin-top:auto;font-size:10.5pt"><b>Extra time?</b> {fill_pages(d["extra"])} '
             f'<b>Short class?</b> {d["short"]}</div>')
    return page(f"Day {k} · {escape(d['skill'])} · no tech, no prep", f"DAY {k}", "Sub plan", inner, n, watermark,
                title=d["title"])


# ---------------------------------------------------------------- worksheets
def sheet(k, band, sub, inner, n, watermark=False, key_page=None):
    title = DAY_SHEETS[k][0 if band == "k2" else 1]
    right = f"Answer key on page {IX[key_page]}" if key_page else None
    return page(sub, f"DAY {k}", "Grades K–2" if band == "k2" else "Grades 3–5", inner, n, watermark, name=True, right=right, title=title)


def d1_k2(n, watermark=False):
    cells = []
    for i in range(4):
        cells.append(
            f'<div class="box" style="padding:6pt 9pt"><div class="h" style="font-size:13pt">Sound {i + 1}</div>'
            f'<div style="height:118pt;border:1pt dashed #999;border-radius:6pt;margin:5pt 0 7pt;position:relative">'
            f'<span class="small" style="position:absolute;left:6pt;top:3pt">Draw it</span></div>'
            f'<div style="display:flex;justify-content:space-around;font-size:14pt;margin-bottom:5pt">{circ("LOUD")}{circ("SOFT")}</div>'
            f'<div style="display:flex;justify-content:space-around;font-size:14pt;margin-bottom:5pt">{circ("HIGH")}{circ("LOW")}</div>'
            f'<div style="display:flex;justify-content:space-around;font-size:14pt">{circ("LONG")}{circ("SHORT")}</div></div>')
    inner = (f'<div class="how" style="font-size:12.5pt">Listen to each sound. <b>Draw</b> what made it. <b>Circle</b> one word in each row.</div>'
             f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:12pt 14pt">{"".join(cells)}</div>'
             f'<div style="margin-top:14pt;font-size:13pt;display:flex;align-items:flex-end;gap:8pt"><b>My favorite sound was</b>'
             f'<span style="flex:1;border-bottom:1pt solid #000;height:20pt"></span></div>')
    return sheet(1, "k2", "Close your eyes and listen like a detective", inner, n, watermark)


def d1_35(n, watermark=False):
    dyn = "".join(svg(22, 20, dyn_svg(sym, 11, 15, 8.5), "display:inline-block;vertical-align:middle") for sym in ("p", "mp", "mf", "f"))
    rows = "".join(
        f"<tr><td style='text-align:center;font-family:Oswald;font-weight:700'>{i + 1}</td><td></td>"
        f"<td style='white-space:nowrap;text-align:center'>{dyn}</td>"
        f"<td style='text-align:center;font-family:Oswald;font-weight:500;letter-spacing:.1em'>H &nbsp;M &nbsp;L</td>"
        f"<td style='text-align:center;font-family:Oswald;font-weight:500;font-size:9.5pt'>SHORT &nbsp;LONG</td><td></td></tr>" for i in range(8))
    bank = ["scratchy", "smooth", "bright", "dull", "crisp", "booming", "tinkly", "hollow", "squeaky", "buzzy", "sharp", "soft-edged"]
    inner = (f'<div class="how">Listen to each sound. Write what made it, then circle its <b>dynamics</b>, its <b>pitch</b> (high, medium, low) and its '
             f'<b>length</b>. Describe its <b>timbre</b> (tone color) with a word or two.</div>'
             f'<table class="t" style="font-size:10.5pt"><tr><th style="width:5%">#</th><th style="width:25%">Sound I heard</th><th style="width:21%">Dynamics</th>'
             f'<th style="width:12%">Pitch</th><th style="width:13%">Length</th><th>Timbre words</th></tr>'
             + rows.replace("<tr><td", "<tr style='height:36pt'><td") + '</table>'
             f'<div class="box" style="margin-top:8pt;font-size:10.5pt;padding:5pt 10pt"><b class="h" style="font-size:11pt">Timbre word bank</b> &nbsp; '
             f'{" · ".join(bank)}</div>'
             f'<div class="part">Think about it<span class="acc"> ·</span></div>'
             f'<div style="font-size:11pt">1. Which sound would you use to start a piece of music? Why?</div><div class="ln2"></div><div class="ln2"></div>'
             f'<div style="font-size:11pt;margin-top:6pt">2. Which two sounds had the most different timbres?</div><div class="ln2"></div>')
    return sheet(1, "35", "Listen like a composer: dynamics, pitch, length and timbre", inner, n, watermark)


def _letter_box(val, key, w=34, h=28, size=18):
    return (f'<span style="display:inline-block;width:{w}pt;height:{h}pt;border:1.3pt solid #000;border-radius:5pt;text-align:center;'
            f'line-height:{h}pt;vertical-align:middle;font-family:Oswald;font-weight:700;font-size:{size}pt;color:{ACCENT}">{val if key else ""}</span>')


def d2_k2(n, watermark=False, key=False):
    s, W = 8.6, 52
    rows = []
    for i, p in enumerate(D2_COUNT):
        st, _ = rhythm_svg(p, 8, 34, s, W, syl=key, syl_size=11)
        rows.append(f'<div style="display:flex;align-items:center;gap:14pt;border:1.3pt solid #000;border-radius:7pt;padding:1pt 14pt">'
                    f'<b class="h" style="font-size:17pt">{i + 1}</b>{svg(270, 60, st)}<span style="flex:1"></span>'
                    f'<span style="font-size:11pt">claps</span>{_letter_box(nsounds(p), key, 42, 34, 21)}</div>')
    bx = "".join(f'<div style="text-align:center"><div class="h" style="font-size:16pt">{"ABC"[i]}</div>'
                 f'{svg(70, 56, _single(t, 35, 34, 9))}</div>'
                 for i, t in enumerate(D2_BOXES))
    words = "".join(f'<div style="display:flex;align-items:center;gap:8pt;font-size:16pt;margin:3pt 0"><b style="width:70pt">{w}</b>'
                    f'{_letter_box("ABC"[D2_BOXES.index(t)], key, 34, 28, 17)}</div>' for w, t in D2_WORDS)
    inner = (f'<div class="part">A · How many sounds?<small>Clap each rhythm. Write how many claps you hear. (A rest is silent.)</small></div>'
             f'<div style="display:grid;grid-template-columns:1fr;gap:7pt">{"".join(rows)}</div>'
             f'<div class="part" style="margin-top:14pt">B · Word rhythms<small>Say and clap each word. Write the letter of its rhythm.</small></div>'
             f'<div style="display:flex;gap:24pt;align-items:center"><div class="box" style="display:flex;gap:24pt;padding:6pt 18pt">{bx}</div>'
             f'<div>{words}</div></div>')
    if key:
        return page("Day 2 · K–2 answer key", "ANSWER KEY", "Rhythm Readers", inner, n, watermark, ak=True, title="Rhythm Readers")
    return sheet(2, "k2", "Clap, count and match", inner, n, watermark, key_page="key_d2")


def _single(t, cx, yl, s):
    return tok_svg(t, cx, yl, s, 40)


def d2_35(n, watermark=False, key=False):
    s = 7
    math_cells = []
    for i, p in enumerate(D2_MATH):
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
    for i, p in enumerate(D2_BARS):
        st, _ = rhythm_svg(p, 8, 30, 6, 30, syl=False)
        ok = nbeats(p) == 4
        bar_cells.append(f'<div style="display:flex;align-items:center;gap:6pt;border:1.3pt solid #000;border-radius:7pt;padding:2pt 8pt">'
                         f'<b class="h" style="font-size:13pt">{i + 1}</b>{svg(178, 52, st)}<span style="flex:1"></span>'
                         f'<div style="text-align:center;font-size:11pt"><div style="white-space:nowrap">{circ("YES", key and ok)}{circ("NO", key and not ok)}</div>'
                         f'<div style="font-size:9.5pt;margin-top:3pt">beats: {_letter_box(nbeats(p), key, 26, 20, 13)}</div></div></div>')
    say = []
    for i, p in enumerate(D2_SAY):
        st, _ = rhythm_svg(p, 8, 30, 7.4, 52)
        say.append(f'<div style="display:flex;align-items:center;gap:10pt"><b class="h" style="font-size:13pt">{i + 1}</b>{svg(250, 50, st)}'
                   f'<span style="flex:1;border-bottom:1pt solid #000;height:22pt;font-family:Oswald;font-weight:700;color:{ACCENT};'
                   f'font-size:15pt;letter-spacing:.04em">{syllables(p) if key else ""}</span></div>')
    beat_key = " · ".join(f"{NAMES[t]} = {BEATS[t]}" for t in "qerhw")
    inner = (f'<div class="small" style="margin-top:6pt;font-size:9.5pt !important"><b>Beats:</b> {beat_key}</div>'
             f'<div class="part" style="margin-top:6pt">A · Rhythm math<small>Add up the beats.</small></div>'
             f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:7pt 12pt">{"".join(math_cells)}</div>'
             f'<div class="part" style="margin-top:12pt">B · Is it 4 beats?<small>In 4/4 time every bar needs 4 beats. Count each bar. Circle YES or NO.</small></div>'
             f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:7pt 12pt">{"".join(bar_cells)}</div>'
             f'<div class="part" style="margin-top:12pt">C · Say it<small>Write the rhythm syllables (ta, ti-ti, shh, ta-a) for each rhythm.</small></div>'
             f'{"".join(say)}')
    if key:
        return page("Day 2 · 3–5 answer key", "ANSWER KEY", "Rhythm Math", inner, n, watermark, ak=True, title="Rhythm Math")
    return sheet(2, "35", "Add the beats, check the bars, say the rhythm", inner, n, watermark, key_page="key_d2")


def _trace_word(word, size, w):
    return (f'<text x="4" y="{size * 0.92:.1f}" font-family="Oswald" font-weight="700" font-size="{size}" fill="none" stroke="#777" '
            f'stroke-width="1.2" stroke-dasharray="3 2.5" letter-spacing="2">{escape(word)}</text>')


def d3_k2(n, watermark=False, key=False):
    trace = []
    for sym, word, mean in (("f", "forte", "LOUD"), ("p", "piano", "SOFT")):
        trace.append(f'<div class="box" style="display:flex;align-items:center;gap:12pt;padding:4pt 12pt">'
                     f'{svg(56, 60, dyn_svg(sym, 28, 46, 22))}'
                     f'<div><div style="font-size:11pt">means <b>{mean}</b>. Trace:</div>{svg(150, 42, _trace_word(word, 38, 150))}</div></div>')
    snd = "".join(f'<div style="display:flex;align-items:center;gap:8pt;font-size:13pt;margin:0 0 5pt"><b class="h" style="width:16pt">{i + 1}</b>'
                  f'<span style="flex:1">{escape(w)}</span>'
                  f'<span class="circ{" on" if key and a == "f" else ""}" style="padding:0 6pt">{svg(26, 24, dyn_svg("f", 13, 18, 10, ACCENT if key and a == "f" else "#000"))}</span>'
                  f'<span class="circ{" on" if key and a == "p" else ""}" style="padding:0 6pt">{svg(26, 24, dyn_svg("p", 13, 18, 10, ACCENT if key and a == "p" else "#000"))}</span></div>'
                  for i, (w, a) in enumerate(D3_SOUNDS))
    spd = "".join(f'<div style="display:flex;align-items:center;gap:8pt;font-size:13pt;margin:0 0 5pt"><b class="h" style="width:16pt">{i + 1}</b>'
                  f'<span style="flex:1">{escape(w)}</span>{circ("FAST", key and a == "FAST")}{circ("SLOW", key and a == "SLOW")}</div>'
                  for i, (w, a) in enumerate(D3_SPEED))
    inner = (f'<div class="part">A · Music words for loud and soft</div><div class="cols" style="gap:12pt">{"".join(f"<div>{t}</div>" for t in trace)}</div>'
             f'<div class="part" style="margin-top:12pt">B · Loud or soft?<small>Listen as your teacher reads. Circle <b>f</b> for loud or <b>p</b> for soft.</small></div>'
             f'{snd}'
             f'<div class="part" style="margin-top:12pt">C · Fast or slow?<small>Circle the tempo.</small></div>{spd}'
             f'<div class="part" style="margin-top:12pt">D · Draw something loud and something soft</div>'
             f'<div class="cols" style="gap:14pt;flex:1"><div class="box" style="min-height:120pt"><b class="h">Loud</b></div>'
             f'<div class="box" style="min-height:120pt"><b class="h">Soft</b></div></div>')
    if key:
        return page("Day 3 · K–2 answer key", "ANSWER KEY", "Loud or Soft?", inner, n, watermark, ak=True, title="Loud or Soft?")
    return sheet(3, "k2", "Dynamics and tempo: loud, soft, fast, slow", inner, n, watermark, key_page="key_d35")


DYN_ORDER = [5, 2, 7, 0, 6, 1, 4, 3]     # Part A: meanings A-H are DYN in this shuffled order
TEMPO_ORDER = [4, 0, 3, 5, 1, 2]         # Part B: tempo words listed in this shuffled order


def d3_35(n, watermark=False, key=False):
    syms = []
    for i, (sym, _) in enumerate(DYN):
        letter = "ABCDEFGH"[DYN_ORDER.index(i)]
        syms.append(f'<div style="display:flex;align-items:center;gap:8pt;margin:0 0 1pt"><b class="h" style="font-size:12pt;width:14pt">{i + 1}</b>'
                    f'<span style="display:inline-block;width:62pt">{svg(60, 30, dyn_svg(sym, 30, 23, 11))}</span>'
                    f'{_letter_box(letter, key, 30, 24, 15)}</div>')
    means = "".join(f'<div style="font-size:11pt;margin:0 0 5pt"><b class="h" style="font-size:12pt">{"ABCDEFGH"[j]}</b> &nbsp;{escape(DYN[k][1])}</div>'
                    for j, k in enumerate(DYN_ORDER))
    temp = "".join(f'<div style="display:flex;align-items:center;gap:8pt;margin:0 0 3pt">{_letter_box(TEMPO_ORDER[j] + 1, key, 30, 24, 15)}'
                   f'<span style="font-size:12pt"><b><i>{TEMPO[k][0]}</i></b> · {TEMPO[k][1]}</span></div>'
                   for j, k in enumerate(TEMPO_ORDER))
    lines = ["Hear the thunder rumble,", "feel the raindrops fall,", "now the storm is passing,", "quiet, after all."]
    chant = "".join(f'<div style="display:flex;align-items:flex-end;gap:10pt;margin:0 0 3pt"><span style="flex:0 0 52pt;border-bottom:1pt solid #000;height:20pt"></span>'
                    f'<span style="font-size:12pt"><i>{l}</i></span></div>' for l in lines)
    inner = (f'<div class="part">A · Dynamics match<small>Write the letter of the meaning next to each symbol.</small></div>'
             f'<div class="cols" style="gap:16pt"><div style="flex:0 0 2.1in">{"".join(syms)}</div><div class="box" style="padding:7pt 12pt">{means}</div></div>'
             f'<div class="part" style="margin-top:10pt">B · Tempo ladder<small>Number the tempos from 1 (slowest) to 6 (fastest).</small></div>'
             f'<div class="cols" style="gap:16pt"><div>{temp}</div>'
             f'<div class="box" style="font-size:10.5pt">Tempo words are Italian. Composers write them at the start of a piece so every '
             f'musician plays at the same speed.</div></div>'
             f'<div class="part" style="margin-top:10pt">C · Be the composer<small>Write a dynamic (pp, p, mp, mf, f, ff) for each line of this chant. Then say it that way.</small></div>'
             f'{chant}')
    if key:
        return page("Day 3 · 3–5 answer key", "ANSWER KEY", "Dynamics and Tempo", inner, n, watermark, ak=True, title="Dynamics and Tempo")
    return sheet(3, "35", "Match the symbols, order the tempos, mark the dynamics", inner, n, watermark, key_page="key_d35")


def d4_k2(n, watermark=False):
    s = 9
    bank = "".join(f'<div style="text-align:center;padding:0 6pt"><div style="font-size:15pt;font-weight:700">{w}</div>'
                   f'{svg(60, 50, _single(t, 30, 36, s))}<div class="l" style="font-size:11pt;color:{ACCENT}">{SYL[t]}</div></div>'
                   for w, t in D4_BANK_K2)

    def row(items=None):
        cells = []
        for i in range(4):
            w, t = items[i] if items else ("", None)
            note = svg(70, 56, _single(t, 35, 40, s)) if t else ""
            cells.append(f'<div style="border:1.4pt solid #000;border-radius:7pt;text-align:center;overflow:hidden">'
                         f'<div style="height:52pt;font-size:17pt;font-weight:700;line-height:52pt">{w}</div>'
                         f'<div style="height:62pt;border-top:1pt dashed #999;display:flex;align-items:center;justify-content:center">{note}</div></div>')
        return f'<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:8pt">{"".join(cells)}</div>'
    inner = (f'<div class="how" style="font-size:12pt">Each box is <b>one beat</b>. Write or draw a word in the top of each box. '
             f'Then draw its rhythm underneath. Clap and say your rhythm!</div>'
             f'<div class="box" style="display:flex;justify-content:space-around;padding:4pt 6pt">{bank}</div>'
             f'<div class="part" style="margin-top:10pt">Example<small>cat · piz-za · dog · shh</small></div>{row(D4_EXAMPLE_K2)}'
             f'<div class="part" style="margin-top:12pt">My rhythm 1</div>{row()}'
             f'<div class="part" style="margin-top:12pt">My rhythm 2</div>{row()}')
    return sheet(4, "k2", "Make a 4-beat rhythm from words", inner, n, watermark)


def d4_35(n, watermark=False):
    bank = "".join(f'<div style="text-align:center">{svg(54, 46, _single(t, 27, 32, 7.4))}<div style="font-size:10pt"><b>{SYL[t]}</b><br>'
                   f'{BEATS[t]} beat{"s" if BEATS[t] > 1 else ""}</div></div>' for t in "qerhw")
    ex, _ = rhythm_svg(D4_EXAMPLE_35, 8, 30, 7.4, 40, syl=True, syl_size=10.5)
    bars_ = []
    for i in range(4):
        bars_.append(f'<div style="display:flex;align-items:center;gap:8pt;margin:0 0 6pt"><b class="h" style="font-size:13pt;width:46pt">Bar {i + 1}</b>'
                     f'<div style="flex:1;height:58pt;position:relative;border-right:2pt solid #000">'
                     f'<div style="position:absolute;left:0;right:0;top:29pt;border-top:1.4pt solid #000"></div>'
                     f'{"".join(f"<div style=\'position:absolute;bottom:0;left:{(k + .5) * 25 - 1}%;font-size:8pt;color:#999\'>{k + 1}</div>" for k in range(4))}</div>'
                     f'<div style="font-size:9.5pt;text-align:center;width:56pt">beats<br>{_letter_box("", False, 30, 22, 13)}</div></div>')
    checks = "".join(f'<div style="font-size:11pt;margin:0 0 4pt">{checkbox(12)} &nbsp;{c}</div>' for c in (
        "Every bar adds up to exactly 4 beats.", "I used at least one rest (shh).", "I used at least three different rhythms.",
        "I can clap and say my whole rhythm with a steady beat."))
    inner = (f'<div class="how">Compose 4 bars of rhythm in 4/4 time. Each bar needs exactly <b>4 beats</b>. Write the syllables under your notes, '
             f'then count the beats and write the total.</div>'
             f'<div class="box" style="display:flex;justify-content:space-around;padding:4pt 6pt">{bank}</div>'
             f'<div class="part" style="margin-top:8pt">Example<small>2 bars, 4 beats each</small></div>{svg(320, 62, ex)}'
             f'<div style="display:flex;gap:16pt;margin:4pt 0 4pt">{fl("Title", "style=flex:1")}{fl("Composer", "style=flex:1")}</div>'
             f'{"".join(bars_)}'
             f'<div class="part" style="margin-top:6pt">Composer checklist</div>{checks}')
    return sheet(4, "35", "Compose 4 bars in 4/4 and perform them", inner, n, watermark)


def d5_k2(n, watermark=False, key=False):
    h = 210
    ys = [36 + i * 66 for i in range(3)]
    left = "".join(text(30, y + 9, a, 26, 700, anchor="start") + f'<circle cx="140" cy="{y}" r="6" fill="#000"/>'
                   for (a, _), y in zip(OPPOSITES, ys))
    right = "".join(f'<circle cx="290" cy="{y}" r="6" fill="#000"/>' + text(310, y + 9, w, 26, 700, anchor="start")
                    for w, y in zip(OPP_RIGHT, ys))
    lines = ""
    if key:
        for (a, b), y in zip(OPPOSITES, ys):
            lines += (f'<line x1="146" y1="{y}" x2="284" y2="{ys[OPP_RIGHT.index(b)]}" stroke="{ACCENT}" stroke-width="3" '
                      f'stroke-linecap="round"/>')
    tr = "".join(f'<div class="box" style="padding:4pt 8pt">{svg(118, 46, _trace_word(w, 40, 118))}</div>' for w in TRACE)
    inner = (f'<div class="part">A · Opposites<small>Draw a line from each word to its opposite.</small></div>'
             f'<div style="display:flex;justify-content:center">{svg(430, h, left + right + lines)}</div>'
             f'<div class="part" style="margin-top:8pt">B · Trace the music words</div>'
             f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:8pt 14pt">{tr}</div>'
             f'<div class="part" style="margin-top:12pt">C · Draw yourself making music</div>'
             f'<div class="box" style="flex:1;min-height:150pt"></div>')
    if key:
        return page("Day 5 · K–2 answer key", "ANSWER KEY", "Music Opposites", inner, n, watermark, ak=True, title="Music Opposites")
    return sheet(5, "k2", "Opposites, music words and a drawing", inner, n, watermark, key_page="key_d35")


def ws_grid_svg(cell, key=False, size=None):
    on = {c for cells in PLACE.values() for c in cells} if key else set()
    out = []
    for y in range(WS_N):
        for x in range(WS_N):
            cx, cy = x * cell + cell / 2, y * cell + cell / 2
            if (y, x) in on:
                out.append(f'<rect x="{x * cell + 1.5:.1f}" y="{y * cell + 1.5:.1f}" width="{cell - 3:.1f}" height="{cell - 3:.1f}" rx="{cell / 3:.1f}" '
                           f'fill="{ACCENT}" fill-opacity=".22" stroke="{ACCENT}" stroke-width="1"/>')
            out.append(text(cx, cy + (size or cell * 0.55) * 0.36, GRID[y][x], size or cell * 0.55, 500))
    out.append(f'<rect x="0.7" y="0.7" width="{WS_N * cell - 1.4}" height="{WS_N * cell - 1.4}" rx="6" fill="none" stroke="#000" stroke-width="1.4"/>')
    return svg(WS_N * cell, WS_N * cell, "".join(out), "display:block;margin:0 auto")


def d5_35(n, watermark=False):
    words = "".join(f'<div style="font-size:11.5pt;margin:0 0 5pt;display:flex;align-items:center;gap:7pt">{checkbox(11)}'
                    f'<b style="font-family:Oswald;font-weight:500;letter-spacing:.06em">{w}</b></div>' for w in WS_WORDS)
    inner = (f'<div class="how">Find the 12 music words. They go across, down, or diagonally down to the right. Tick each word when you find it.</div>'
             f'<div style="display:flex;gap:18pt;align-items:flex-start"><div>{ws_grid_svg(30)}</div>'
             f'<div class="box" style="flex:1;padding:8pt 12pt">{words}</div></div>'
             f'<div class="part" style="margin-top:12pt">Word work<small>Pick 3 words from the list. Write what each one means.</small></div>'
             + "".join(f'<div style="display:flex;align-items:flex-end;gap:8pt;margin:0 0 4pt"><span style="flex:0 0 1.3in;border-bottom:1pt solid #000;height:24pt"></span>'
                       f'<span style="font-size:11pt">means</span><span style="flex:1;border-bottom:1pt solid #000;height:24pt"></span></div>' for _ in range(3)))
    return sheet(5, "35", "Find the music vocabulary, then explain it", inner, n, watermark, key_page="key_d35")


def early_page(n, watermark=False):
    inner = (f'<div class="how">Finished early? Pick one (or do them all).</div>'
             f'<div class="cols" style="gap:14pt"><div class="box" style="height:300pt"><b class="h" style="font-size:13pt">Invent an instrument</b>'
             f'<div style="font-size:10.5pt;margin-top:3pt">Draw it. How do you play it? Circle: '
             f'{circ("SHAKE")}{circ("TAP")}{circ("BLOW")}{circ("PLUCK")}</div></div>'
             f'<div class="box" style="height:300pt"><b class="h" style="font-size:13pt">Design a concert poster</b>'
             f'<div style="font-size:10.5pt;margin-top:3pt">Who is playing? Where? When? Add a picture.</div></div></div>'
             f'<div class="part" style="margin-top:12pt">My 4-beat rhythm<small>One word or note in each beat box. Clap it for a friend.</small></div>'
             f'<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:8pt">'
             + "".join(f'<div style="border:1.4pt solid #000;border-radius:7pt;height:70pt;position:relative"><span class="small" '
                       f'style="position:absolute;left:6pt;top:3pt">beat {i + 1}</span></div>' for i in range(4))
             + f'</div><div class="part" style="margin-top:12pt">My music words<small>Write 3 sentences using a music word: beat, loud, soft, fast, slow, high, low.</small></div>'
             f'<div class="ln2"></div><div class="ln2"></div><div class="ln2"></div>')
    return page("Early finishers · grades K–5", "ANY DAY", "Early finishers", inner, n, watermark, name=True, title="Early Finishers")


# ---------------------------------------------------------------- answer keys
def mini(html_page, scale):
    """Embed a filled-in worksheet page as a scaled-down copy on a key page."""
    body = re.sub(r'^<section class="page">', "", html_page)
    body = re.sub(r"</section>$", "", body)
    body = re.sub(r'<div class="foot">.*?</span></div>', "", body)
    return (f'<div style="width:{8.5 * scale}in;height:{11 * scale}in;overflow:hidden;border:1.2pt solid #000;border-radius:4pt">'
            f'<div class="page" style="transform:scale({scale});transform-origin:0 0">{body}</div></div>')


def key_d2_page(n, watermark=False):
    a = mini(d2_k2(0, key=True), 0.37)
    b = mini(d2_35(0, key=True), 0.37)
    rows = "".join(f"<tr><td>A{i + 1}</td><td>{syllables(p)}</td><td class='ans'>{nsounds(p)}</td></tr>" for i, p in enumerate(D2_COUNT))
    rows += "".join(f"<tr><td>B · {w}</td><td>{SYL[t]}</td><td class='ans'>{'ABC'[D2_BOXES.index(t)]}</td></tr>" for w, t in D2_WORDS)
    rows2 = "".join(f"<tr><td>A{i + 1}</td><td>{' + '.join(str(BEATS[t]) for t in p)}</td><td class='ans'>{nbeats(p)}</td></tr>" for i, p in enumerate(D2_MATH))
    rows2 += "".join(f"<tr><td>B{i + 1}</td><td>{syllables(p)}</td><td class='ans'>{'YES' if nbeats(p) == 4 else 'NO'} · {nbeats(p)}</td></tr>"
                     for i, p in enumerate(D2_BARS))
    rows2 += "".join(f"<tr><td>C{i + 1}</td><td colspan=2 class='ans'>{syllables(p)}</td></tr>" for i, p in enumerate(D2_SAY))
    inner = (f'<div class="how">Day 2 answers. The small pages are the filled-in worksheets; the tables list every answer.</div>'
             f'<div class="cols" style="gap:16pt"><div>{a}<table class="t" style="margin-top:8pt;font-size:9.5pt"><tr><th>K–2</th><th>Rhythm</th><th>Answer</th></tr>{rows}</table></div>'
             f'<div>{b}<table class="t" style="margin-top:8pt;font-size:9.5pt"><tr><th>3–5</th><th>Work</th><th>Answer</th></tr>{rows2}</table></div></div>')
    return page("Answer keys · Day 2 Rhythm Readers and Rhythm Math", "ANSWER KEY", "Day 2", inner, n, watermark, ak=True)


def key_d35_page(n, watermark=False):
    k2 = ", ".join(f"{i + 1} <b class=ans>{a}</b>" for i, (_, a) in enumerate(D3_SOUNDS))
    sp = ", ".join(f"{i + 1} <b class=ans>{a}</b>" for i, (_, a) in enumerate(D3_SPEED))
    dm = ", ".join(f"{i + 1} <b class=ans>{'ABCDEFGH'[DYN_ORDER.index(i)]}</b>" for i in range(len(DYN)))
    tm = ", ".join(f"<i>{TEMPO[k][0]}</i> <b class=ans>{TEMPO_ORDER[j] + 1}</b>" for j, k in enumerate(TEMPO_ORDER))
    opp = ", ".join(f"{a} <b class=ans>{b}</b>" for a, b in OPPOSITES)
    words = "".join(f"<div style='font-size:9.5pt;margin:0 0 2pt'><b>{w}</b> · row {PLACE[w][0][0] + 1}, col {PLACE[w][0][1] + 1}, "
                    f"{ {(0, 1): 'across', (1, 0): 'down', (1, 1): 'diagonal'}[(PLACE[w][1][0] - PLACE[w][0][0], PLACE[w][1][1] - PLACE[w][0][1])]}</div>"
                    for w in WS_WORDS)
    inner = (f'<div class="cols" style="gap:16pt"><div>'
             f'<div class="part" style="margin-top:4pt">Day 3 · K–2 Loud or Soft?</div>'
             f'<p style="font-size:11pt;margin:0 0 3pt">B: {k2}<br>C: {sp}<br>A and D: check tracing and drawings.</p>'
             f'<div class="part">Day 3 · 3–5 Dynamics and Tempo</div>'
             f'<p style="font-size:11pt;margin:0 0 3pt">A: {dm}</p><p style="font-size:11pt;margin:0 0 3pt">B: {tm}</p>'
             f'<p style="font-size:11pt;margin:0 0 3pt">C: answers vary. A strong answer gets louder on the thunder lines and softer at the end '
             f'(for example <b class=ans>f, mf, mp, pp</b>).</p>'
             f'<div class="part">Day 5 · K–2 Music Opposites</div><p style="font-size:11pt;margin:0 0 3pt">A: {opp}. B and C: check tracing and drawing.</p>'
             f'</div><div style="flex:0 0 3.05in">'
             f'<div class="part" style="margin-top:4pt">Day 5 · 3–5 Word Search</div>{ws_grid_svg(18, key=True, size=10.5)}'
             f'<div style="margin-top:6pt">{words}</div></div></div>'
             f'<div class="part" style="margin-top:8pt">Dynamics, softest to loudest</div>'
             f'<div style="display:flex;gap:14pt;align-items:center">'
             + "".join(f'<div style="text-align:center">{svg(46, 28, dyn_svg(s_, 23, 22, 9.5))}<div class="small">{m.split(" (")[0]}</div></div>'
                       for s_, m in DYN[:6]) + '</div>')
    return page("Answer keys · Days 3 and 5", "ANSWER KEY", "Days 3 and 5", inner, n, watermark, ak=True)


def report_page(n, watermark=False):
    rows = "".join("<tr><td style='height:27pt'></td><td></td><td></td><td></td></tr>" for _ in range(6))
    inner = (f'<div class="how">Substitute: thank you! Please fill this in and leave it on the teacher’s desk.</div>'
             f'<div class="cols" style="gap:16pt"><div>{fl("Your name")}</div><div>{fl("Date")}</div></div>'
             f'<table class="t"><tr><th style="width:24%">Class / grade</th><th style="width:12%">Day #</th><th style="width:30%">What we finished</th>'
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
            f'<div class="l" style="font-size:13pt">Music Sub Plans K–5 · 5 no-prep emergency days</div></div>'
            f'<div class="cols"><div>'
            f'<h2>What it is</h2>'
            f'<p>Five complete music lessons a substitute can teach with no tech, no instruments and no music background. Each day has '
            f'a step-by-step plan with words to say, timed steps, a closing game, and two worksheets: one for grades K–2 and one for grades 3–5.</p>'
            f'<h2>The five days</h2><ol>'
            + "".join(f"<li><b>{escape(d['title'])}</b>: {d['skill'].lower()}.</li>" for d in DAYS) +
            f'</ol><p>Use them in any order. The welcome sheet has a “Day #” column so the sub knows which day each class gets next.</p>'
            f'<h2>Set up the sub tub (about 15 minutes, once)</h2><ol>'
            f'<li>Fill in the welcome sheet (page {IX["welcome"]}).</li>'
            f'<li>Print the plans, the rhythm chart and the sub report; copy each worksheet for your largest class.</li>'
            f'<li>Put each day in its own folder with its worksheets, and add the answer keys.</li></ol>'
            f'<h2>Why subs can teach it</h2>'
            f'<p>Every rhythm has its syllables (ta, ti-ti, shh, ta-a) printed under the notes, so the sub can lead echo clapping '
            f'without reading music. Games use only voices, hands and an eraser.</p>'
            f'</div><div>'
            f'<h2>What’s inside</h2><table class="t"><tr><th>Part</th><th>Pages</th><th>Use</th></tr>{trs}</table>'
            f'<h2>About the notation</h2>'
            f'<p>Rhythms are in 4/4 and use quarter notes, paired eighth notes, quarter rests, half notes and whole notes, engraved with a '
            f'professional music font. Every rhythm was read back by computer and checked for 4 beats per bar, except the bars on Day 2 that '
            f'students must spot as wrong; every key comes from the same checked data.</p>'
            f'<h2>Standards</h2><p>Supports reading rhythm notation (MU:Pr4.2), creating rhythms (MU:Cr2.1) and describing what students hear '
            f'(MU:Re7.2), National Core Arts Standards, Music, grades K–5.</p>'
            f'<h2>Good to know</h2><ul><li>Prints well in black and white.</li><li>K–2 sheets have read-aloud parts; the plans tell the sub which ones.</li>'
            f'<li>Rhythm syllables follow the common ta / ti-ti system. If your students use counting or other syllables, add a note on the welcome sheet.</li></ul>'
            f'<p class="small">All lessons, chants, games, words and art are original. No songs, lyrics or copyrighted characters are used.</p>'
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
            f'<li>Lessons, chants, games, art and layouts: original work, {BRAND} by {STORE}.</li>'
            f'<li>Music notation font: Bravura © Steinberg Media Technologies GmbH, SIL Open Font License 1.1.</li>'
            f'<li>Text fonts: Oswald (The Oswald Project Authors) and Source Sans 3 (Adobe), SIL Open Font License 1.1.</li></ul>'
            f'<p class="small">Designed with the help of digital and AI tools, and checked by hand.</p>'
            f'<div style="flex:1"></div>{foot(f"Page {n}")}</section>')


# ---------------------------------------------------------------- cover
def hero_svg(width_css):
    st, end = rhythm_svg(COVER_STRIP, 0, 0, 9, 42, syl=True, syl_size=14)
    strip = f'<g transform="translate(330 250)">{st}</g>'
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 330" width="{width_css}" style="display:block">'
            f'{clipboard_svg(60, 26, 230, 290)}{pencil_svg(286, 70, 210, 22)}'
            f'<g transform="translate(350 132)">{dyn_svg("f", 20, 30, 20)}{dyn_svg("p", 100, 30, 20, ACCENT)}{dyn_svg("cresc", 190, 30, 18)}</g>'
            f'{strip}</svg>')


def cover_page():
    return (f'<section class="page cover"><div class="store">{BRAND}</div>'
            f'<div style="width:6.9in">{hero_svg("100%")}</div>'
            f'<div class="ctitle"><div class="a">NO-PREP EMERGENCY</div><div class="b">MUSIC SUB PLANS</div>'
            f'<div class="c">5 days · scripted plans · K–2 and 3–5 worksheets · no tech · answer keys</div></div>'
            f'<div class="cband">Grades K–5 <em>·</em> 5 days <em>·</em> 10 worksheets <em>·</em> {len(PLAN)} pages</div></section>')


# ---------------------------------------------------------------- assemble
def render_page(key, watermark=False):
    n = IX[key]
    m = re.match(r"d(\d)_plan$", key)
    if m:
        return plan_page(DAYS[int(m.group(1)) - 1], n, watermark)
    return {
        "cover": cover_page, "teacher": lambda: teacher_page(n), "welcome": lambda: welcome_page(n, watermark),
        "glance": lambda: glance_page(n, watermark), "chart": lambda: chart_page(n, watermark),
        "d1_k2": lambda: d1_k2(n, watermark), "d1_35": lambda: d1_35(n, watermark),
        "d2_k2": lambda: d2_k2(n, watermark), "d2_35": lambda: d2_35(n, watermark),
        "d3_k2": lambda: d3_k2(n, watermark), "d3_35": lambda: d3_35(n, watermark),
        "d4_k2": lambda: d4_k2(n, watermark), "d4_35": lambda: d4_35(n, watermark),
        "d5_k2": lambda: d5_k2(n, watermark), "d5_35": lambda: d5_35(n, watermark),
        "early": lambda: early_page(n, watermark), "key_d2": lambda: key_d2_page(n, watermark),
        "key_d35": lambda: key_d35_page(n, watermark), "report": lambda: report_page(n, watermark), "terms": lambda: terms_page(n),
    }[key]()


PREVIEW_PICKS = ["d2_plan", "chart", "d3_35", "key_d2"]


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
        f'<div style="width:880px;margin-top:22px;margin-left:-40px">{hero_svg("100%")}</div>'
        f'<div class="hd" style="font-size:64px;margin-top:12px">No-Prep Emergency</div>'
        f'<div class="hd" style="font-size:120px">Music Sub Plans</div>'
        f'<div class="sub" style="font-size:29px;margin-top:12px">5 days · scripted plans · K–2 and 3–5 worksheets · no tech</div>'
        f'<div class="band">Grades K–5 <em>·</em> 5 days <em>·</em> {len(PLAN)} pages</div></div>')


def preview_square_1(img):
    items = [(img[0], "Sub plan", "timed steps, words to say"), (img[1], "Rhythm chart", "syllables under every note"),
             (img[2], "Days at a glance", "plus a no-prep game bank")]
    shots = "".join(
        f'<div style="width:290px"><div class="shot"><img src="{src}"><div class="swm" style="font-size:64px">PREVIEW</div></div>'
        f'<div class="lbl">{a}<span>{b}</span></div></div>' for src, a, b in items)
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div>'
        f'<div class="hd" style="font-size:74px;margin-top:20px">Any sub can teach it</div>'
        f'<div class="sub" style="font-size:27px;margin-top:8px">No music background, no tech, no instruments needed</div>'
        f'<div style="display:flex;gap:28px;margin-top:60px;align-items:flex-start">{shots}</div>'
        f'<div class="band">Listening <em>·</em> rhythm <em>·</em> dynamics <em>·</em> composing <em>·</em> vocabulary</div></div>')


def preview_square_2(a, b):
    pair = "".join(
        f'<div style="position:absolute;left:{x}px;top:{y}px;width:470px"><div class="shot"><img src="{src}">'
        f'<div class="swm" style="font-size:100px">PREVIEW</div></div>'
        f'<div class="lbl" style="position:absolute;{side}:-2px;top:-44px;margin:0">{lab}</div></div>'
        for src, lab, x, y, side in ((a, "Grades K–2", 50, 250, "left"), (b, "Grades 3–5", 476, 300, "right")))
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div>'
        f'<div class="hd" style="font-size:72px;margin-top:20px">Two levels every day</div>'
        f'<div class="sub" style="font-size:27px;margin-top:8px">One plan, a K–2 sheet and a 3–5 sheet, with checked answer keys</div>'
        f'{pair}'
        f'<div class="band">10 worksheets <em>·</em> 2 key pages <em>·</em> sub report</div></div>')


def preview_square_3(imgs):
    cells = "".join(
        f'<div style="width:196px"><div class="shot" style="box-shadow:5px 5px 0 #000"><img src="{src}">'
        f'<div class="swm" style="font-size:44px">PREVIEW</div></div><div class="lbl" style="font-size:17px;margin-top:9px">{lab}</div></div>'
        for src, lab in imgs)
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div>'
        f'<div class="hd" style="font-size:70px;margin-top:16px">Everything inside</div>'
        f'<div class="sub" style="font-size:27px;margin-top:8px">Welcome sheet, 5 plans, 10 worksheets, keys and a sub report</div>'
        f'<div style="display:grid;grid-template-columns:repeat(4,196px);gap:20px 26px;margin-top:34px">{cells}</div>'
        f'<div class="band">{len(PLAN)} pages <em>·</em> US Letter PDF <em>·</em> prints in black &amp; white</div></div>')


SHOTS1 = ["d1_plan", "chart", "glance"]
SHOTS2 = ["d2_k2", "d2_35"]
SHOTS3 = [("welcome", "Welcome sheet"), ("d1_35", "Listening log"), ("d3_k2", "Loud or soft"), ("d4_k2", "Word rhythms"),
          ("d4_35", "Composer"), ("d5_35", "Word search"), ("key_d35", "Answer keys"), ("report", "Sub report")]


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
        "grades": ["kindergarten", "2nd-grade", "3rd-grade", "5th-grade"],
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
    for i, p in enumerate(D2_COUNT):
        errs += rhythm_check(f"Day 2 K-2 A{i + 1}", p, s=7.4, W=40)
        if set(p) - set("qer"):
            errs.append(f"Day 2 K-2 A{i + 1} uses a symbol K-2 has not met")
    for i, p in enumerate(D2_BARS):
        errs += rhythm_check(f"Day 2 3-5 B{i + 1}", p, s=6, W=30, four=False)
    if sorted(nbeats(p) == 4 for p in D2_BARS) != [False] * 3 + [True] * 3:
        errs.append("Day 2 part B should have 3 correct and 3 wrong bars")
    for i, p in enumerate(D2_SAY):
        errs += rhythm_check(f"Day 2 3-5 C{i + 1}", p, s=7.4, W=52)
    errs += rhythm_check("Day 4 3-5 example", D4_EXAMPLE_35, s=7.4, W=40)
    errs += rhythm_check("cover strip", COVER_STRIP, s=9, W=42)
    for t in "qerhw":   # single glyphs used in rhythm math, word boxes and banks
        st = tok_svg(t, 50, 40, 7, 40) + '<line class="bar" x1="80" y1="0" x2="80" y2="1"/><rect class="fin"/>'
        got, e = read_rhythm(st, 7, 40, 50 - 20, timesig=False)
        if got.replace("|", "") != t:
            errs.append(f"single glyph {t} reads back as {got}")
    # 2. word rhythms: syllables decide the rhythm, and the printed rhythm agrees
    for label, pairs in (("Day 2 K-2 B", D2_WORDS), ("Day 4 K-2 bank", D4_BANK_K2), ("Day 4 K-2 example", D4_EXAMPLE_K2)):
        for w, t in pairs:
            if word_rhythm(w) != t:
                errs.append(f"{label}: '{w}' has {len(w.split('-'))} syllable(s) but is shown as {SYL[t]}")
    if sum(BEATS[t] for _, t in D4_EXAMPLE_K2) != 4:
        errs.append("Day 4 K-2 example is not 4 beats")
    if sorted(D2_BOXES) != sorted(set(t for _, t in D2_WORDS)):
        errs.append("Day 2 K-2 part B boxes do not cover the word rhythms exactly once")
    # 3. rhythm math is 2-4 terms with sums in range, and the syllable table matches the token table
    for p in D2_MATH:
        if not 2 <= len(p) <= 3:
            errs.append(f"rhythm math item {p} length")
    if SYL != {"q": "ta", "e": "ti-ti", "r": "shh", "h": "ta-a", "w": "ta-a-a-a"} or BEATS != {"q": 1, "e": 1, "r": 1, "h": 2, "w": 4}:
        errs.append("syllable/beat table changed")
    # 4. dynamics/tempo keys: permutations, letters well mixed, order is softest->loudest and slowest->fastest
    if sorted(DYN_ORDER) != list(range(8)) or any(DYN_ORDER[j] == j for j in range(8)):
        errs.append("Day 3 dynamics order must be a derangement of 0-7")
    if sorted(TEMPO_ORDER) != list(range(6)) or any(TEMPO_ORDER[j] == j for j in range(6)):
        errs.append("Day 3 tempo order must be a derangement of 0-5")
    if [s for s, _ in DYN[:6]] != ["pp", "p", "mp", "mf", "f", "ff"]:
        errs.append("dynamics are not softest to loudest")
    if [t for t, _ in TEMPO] != ["largo", "adagio", "andante", "moderato", "allegro", "presto"]:
        errs.append("tempos are not slowest to fastest")
    for sym, cp in (("pp", 0xE52B), ("p", 0xE520), ("mp", 0xE52C), ("mf", 0xE52D), ("f", 0xE522), ("ff", 0xE52F)):
        if DYN_GLYPH[sym] != cp:
            errs.append(f"SMuFL codepoint for {sym}")
    if {a for _, a in D3_SOUNDS} != {"f", "p"} or sum(a == "f" for _, a in D3_SOUNDS) != 3:
        errs.append("Day 3 K-2 sounds should be 3 loud, 3 soft")
    # 5. Day 5: opposites, word search
    if sorted(OPP_RIGHT) != sorted(b for _, b in OPPOSITES) or any(OPP_RIGHT[i] == OPPOSITES[i][1] for i in range(3)):
        errs.append("Day 5 opposites column must be shuffled")
    for w in WS_WORDS:
        if count_word(GRID, w) != 1:
            errs.append(f"word search: {w} found {count_word(GRID, w)} times")
        cells = PLACE[w]
        if "".join(GRID[y][x] for y, x in cells) != w:
            errs.append(f"word search key: {w} cells do not spell it")
        d = (cells[1][0] - cells[0][0], cells[1][1] - cells[0][1])
        if d not in WS_DIRS:
            errs.append(f"word search: {w} runs in a direction the directions do not allow")
    for b in BAD_WORDS:
        if count_word(GRID, b):
            errs.append(f"word search: grid hides the word {b}")
    if len(WS_WORDS) != 12 or len(GRID) != WS_N or any(len(r) != WS_N for r in GRID):
        errs.append("word search size")
    # 6. plan and teacher table
    if len(PLAN) != len(set(PLAN)):
        errs.append("plan has a repeated page")
    covered = set()
    for _, a, b, _ in PARTS:
        covered |= set(PLAN[IX[a] - 1:IX[b]])
    if covered | {"cover", "teacher"} != set(PLAN):
        errs.append(f"teacher table misses pages: {sorted(set(PLAN) - covered - {'cover', 'teacher'})}")
    for d in DAYS:
        if not 30 <= sum(int(m) for m, _, _ in d["steps"]) <= 45:
            errs.append(f"Day {d['n']} steps add to {sum(int(m) for m, _, _ in d['steps'])} min, not 30-45")
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
    """The answers printed in the PDF's key pages equal the checked data."""
    errs = []
    t = re.sub(r"\s+", " ", txt[IX["key_d2"] - 1])
    for i, p in enumerate(D2_COUNT):
        if f"A{i + 1} {syllables(p)} {nsounds(p)}" not in t:
            errs.append(f"Day 2 key: K-2 A{i + 1} '{syllables(p)} {nsounds(p)}' not found")
    for i, p in enumerate(D2_MATH):
        if f"A{i + 1} {'+'.join(str(BEATS[x]) for x in p)} {nbeats(p)}" not in re.sub(r" ?\+ ?", "+", t):
            errs.append(f"Day 2 key: 3-5 A{i + 1} sum not found")
    for i, p in enumerate(D2_BARS):
        if f"B{i + 1} {syllables(p)} {'YES' if nbeats(p) == 4 else 'NO'} · {nbeats(p)}" not in t:
            errs.append(f"Day 2 key: 3-5 B{i + 1} not found")
    for i, p in enumerate(D2_SAY):
        if f"C{i + 1} {syllables(p)}" not in t:
            errs.append(f"Day 2 key: 3-5 C{i + 1} not found")
    t3 = re.sub(r"\s+", " ", txt[IX["key_d35"] - 1])
    want = ", ".join(f"{i + 1} {'ABCDEFGH'[DYN_ORDER.index(i)]}" for i in range(8))
    if want not in t3:
        errs.append("Day 3 key: dynamics letters not found")
    for w in WS_WORDS:
        if w not in t3:
            errs.append(f"Day 5 key: {w} not listed")
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
    for d in DAYS:  # each plan names its own sheets' pages
        k = d["n"]
        for s_ in ("k2", "35"):
            if f"page {IX[f'd{k}_{s_}']}" not in flat[IX[f"d{k}_plan"] - 1]:
                errs.append(f"Day {k} plan does not point to its {s_} sheet")
    for key, target in (("d2_k2", "key_d2"), ("d2_35", "key_d2"), ("d3_k2", "key_d35"), ("d3_35", "key_d35"), ("d5_k2", "key_d35"), ("d5_35", "key_d35")):
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
    nr = len(CHART) + len(D2_COUNT) + len(D2_BARS) + len(D2_SAY) + 2
    print(f"CHECK OK: {nr} engraved rhythms read back from the drawn SVG (glyphs, beamed pairs, beat slots, barlines) and match the data, "
          f"4 beats per bar except Day 2's 3 deliberate wrong bars; word rhythms match syllable counts; Day 2 and 3 key text in the PDF "
          f"matches the data; word search has each of 12 words exactly once; {len(PLAN)} Letter pages with footers and page numbers; "
          f"only Bravura/Oswald/Source Sans 3, all embedded; preview {len(PREVIEW_PICKS)} watermarked pages; images 2000x2000; "
          f"tpt.json and UPLOAD.md ok.")


if __name__ == "__main__":
    if "--check" in sys.argv:
        check()
    else:
        build()
