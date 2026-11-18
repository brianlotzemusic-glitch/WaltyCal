#!/usr/bin/env python3
"""Holiday Rhythm "I Have, Who Has" (TpT 056): build the resource and verify it.

    python3 gen.py           build everything (PDFs, PNGs, UPLOAD.md, tpt.json) into this folder
    python3 gen.py --check   re-read every rhythm staff from the rendered HTML and verify the loops, layout and images

Two games of 24 cards. Every card is one bar of 4/4 on a one-line rhythm staff. Cards are stored as lists of beat patterns
(ta, shh, ti-ti, ta-a, ti-ka-ti-ka, ti-ti-ka, ti-ka-ti). `--check` does not trust that data: it parses the rendered SVG of every staff
(line, clef, time signature, noteheads, stems, beams, rests, barline), derives each note value from the head glyph and the number of
beams, adds up the bar, checks that every note sits where its time position says, and recomputes the rhythm syllables from the
notation. It then re-reads the printed "Who has" prompt of every card, proves that each prompt names exactly one card, and follows
the prompts from card 1 to prove that each game is one closed loop of 24 cards.
"""
import json
import math
import os
import random
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from fractions import Fraction
from html import escape

HERE = os.path.dirname(os.path.abspath(__file__))
TPT = os.path.dirname(HERE)
FONTS = os.path.join(TPT, "fonts")
BUILD = os.path.join(HERE, "build")
RENDER_JS = os.path.join(TPT, "tools", "render.js")
HERO = os.path.join(HERE, "art", "hero.png")

SLUG = "holiday-rhythm-i-have-who-has"
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
TINT = "#DCEEF8"
DISCLOSURE = "Created with the help of digital and AI tools. Notation and answer keys are verified before release."
TITLE = "Holiday Rhythm: I Have, Who Has"
LISTING_TITLE = "I Have Who Has Rhythm Games: Quarter, Eighth & Sixteenth Notes, 48 Cards"
PREFERRED_TITLE = "Holiday Rhythm I Have Who Has Games: Quarter, Eighth & Sixteenth Notes"
PRICE = "3.50"
TAGS = ["Winter", "Games", "Activities", "Printables", "Centers"]
SUBJECTS = ["Music"]
GRADES = ["2nd-grade", "3rd-grade", "4th-grade", "5th-grade"]

# ------------------------------------------------------------------ rhythm data
# One beat pattern = one token, named by its rhythm syllables. Each event is (kind, duration in beats): n note, r rest, h half note.
TOKDEF = {
    "ta": [("n", Fraction(1))],
    "shh": [("r", Fraction(1))],
    "ti-ti": [("n", Fraction(1, 2))] * 2,
    "ta-a": [("h", Fraction(2))],
    "ti-ka-ti-ka": [("n", Fraction(1, 4))] * 4,
    "ti-ti-ka": [("n", Fraction(1, 2)), ("n", Fraction(1, 4)), ("n", Fraction(1, 4))],
    "ti-ka-ti": [("n", Fraction(1, 4)), ("n", Fraction(1, 4)), ("n", Fraction(1, 2))],
}
# the independent table used by --check: (kind, duration) pattern of one beat -> syllables
BEAT_SYL = {
    (("n", Fraction(1)),): "ta",
    (("r", Fraction(1)),): "shh",
    (("n", Fraction(1, 2)), ("n", Fraction(1, 2))): "ti-ti",
    (("n", Fraction(1, 4)),) * 4: "ti-ka-ti-ka",
    (("n", Fraction(1, 2)), ("n", Fraction(1, 4)), ("n", Fraction(1, 4))): "ti-ti-ka",
    (("n", Fraction(1, 4)), ("n", Fraction(1, 4)), ("n", Fraction(1, 2))): "ti-ka-ti",
}
HALF_SYL = "ta-a"
SIXTEENTH_TOKENS = {"ti-ka-ti-ka", "ti-ti-ka", "ti-ka-ti"}


def parse_card(s):
    toks = s.split()
    assert all(t in TOKDEF for t in toks), s
    return toks


def token_beats(tk):
    return sum(d for _, d in TOKDEF[tk])


L1_SRC = ["ta ta ta ta", "ta ti-ti ta ta", "ta ta ta shh", "ti-ti ta ti-ti ta", "ta-a ta ta", "ta ta ta-a", "ta shh ta ta", "ti-ti ti-ti ta ta",
          "ta-a ta-a", "ta ti-ti ta shh", "ti-ti ta shh ta", "ta ta ti-ti ti-ti", "ta-a ta shh", "ta shh ti-ti ta", "ti-ti ti-ti ti-ti ta",
          "ta-a ti-ti ta", "ti-ti ta ta ta", "ta ta ti-ti shh", "ti-ti shh ta ta", "ta-a ti-ti shh", "ta ti-ti ti-ti ta", "ti-ti ta ta-a",
          "shh ta ti-ti ta", "ti-ti ti-ti ta-a"]
L2_SRC = ["ti-ka-ti-ka ta ta ta", "ta ti-ka-ti-ka ta ta", "ta ta ti-ti-ka ta", "ta ta ta ti-ka-ti", "ti-ti-ka ti-ka-ti ta ta",
          "ti-ka-ti-ka ti-ti ta ta", "ti-ka-ti ta ti-ka-ti ta", "ta shh ti-ka-ti-ka ta", "ti-ti ti-ka-ti-ka ta-a", "ta-a ti-ka-ti-ka ta",
          "ti-ti-ka ta ti-ti-ka ta", "ti-ka-ti-ka ti-ka-ti-ka ta ta", "ta ti-ti ti-ka-ti shh", "ti-ka-ti-ka ta ta-a", "ti-ti-ka ti-ti ta shh",
          "ta-a ti-ka-ti ti-ti-ka", "shh ti-ka-ti-ka ta ti-ti", "ti-ka-ti ti-ka-ti ti-ti ta", "ta ti-ti-ka shh ti-ka-ti-ka",
          "ti-ti ti-ti-ka ti-ka-ti ta", "ta-a ta ti-ka-ti-ka", "ti-ka-ti-ka ta shh ta", "ti-ti-ka ta ta-a", "ti-ka-ti-ka ti-ka-ti ta-a"]


def syl(card):
    return " ".join(card)


def make_game(level, src, seed):
    cards = [parse_card(s) for s in src]
    assert len(cards) == 24 and len({syl(c) for c in cards}) == 24, f"level {level}: cards not 24 distinct"
    for c in cards:
        assert sum(token_beats(t) for t in c) == 4, c
        pos = Fraction(0)
        for t in c:
            if t == "ta-a":
                assert pos in (0, 2), f"half note off beats 1 and 3 in {c}"
            pos += token_beats(t)
    rng = random.Random(seed)
    rest = list(range(2, 25))
    rng.shuffle(rest)
    order = [1] + rest                      # loop order: card numbers; card k points at the next one in this list
    nxt = {order[i]: order[(i + 1) % 24] for i in range(24)}
    assert sum(1 for k in range(1, 25) if nxt[k] == k + 1) <= 2, "loop too close to numeric order"
    return {"level": level, "cards": {i + 1: c for i, c in enumerate(cards)}, "order": order, "next": nxt, "end": order[-1]}


GAMES = {1: make_game(1, L1_SRC, 5601), 2: make_game(2, L2_SRC, 5602)}
for _c in GAMES[1]["cards"].values():
    assert not (set(_c) & SIXTEENTH_TOKENS)
for _c in GAMES[2]["cards"].values():
    assert set(_c) & SIXTEENTH_TOKENS, "level 2 card without a sixteenth pattern"


# ------------------------------------------------------------------ drawing helpers
HEAD_W = 1.18
REST_W = 1.08
G_HEAD, G_HALF, G_QREST, G_NEUTRAL, G_TS4 = 0xE0A4, 0xE0A3, 0xE4E5, 0xE069, 0xE084
STEM_X = 0.168
STEM_LEN = 3.5
CLEF_W, TS_W = 1.528, 1.88


def fx(v):
    return f"{v:.2f}"


def gl(cp, x, y, size, cls="", fill="#000"):
    c = f' class="{cls}"' if cls else ""
    return f'<text{c} x="{fx(x)}" y="{fx(y)}" font-family="Bravura" font-size="{fx(size)}" fill="{fill}">&#x{cp:X};</text>'


def snowflake(cx, cy, r, color="#000", sw=1.3):
    out = []
    for k in range(6):
        a = math.radians(60 * k - 90)
        ex, ey = cx + r * math.cos(a), cy + r * math.sin(a)
        out.append(f'<line x1="{cx:.2f}" y1="{cy:.2f}" x2="{ex:.2f}" y2="{ey:.2f}" stroke="{color}" stroke-width="{sw}"/>')
        bx, by = cx + 0.58 * r * math.cos(a), cy + 0.58 * r * math.sin(a)
        for da in (-50, 50):
            b = math.radians(60 * k - 90 + da)
            out.append(f'<line x1="{bx:.2f}" y1="{by:.2f}" x2="{bx + 0.34 * r * math.cos(b):.2f}" y2="{by + 0.34 * r * math.sin(b):.2f}" stroke="{color}" stroke-width="{sw}"/>')
    return f'<g stroke-linecap="round" fill="none">{"".join(out)}</g>'


def icon_svg(n):
    """Small non-denominational holiday icon for a card corner: snowflake, star, ornament, tree (28 x 28 box)."""
    k = n % 4
    sw = 1.2
    if k == 0:
        body = snowflake(14, 14, 11, "#000", 1.4)
    elif k == 1:
        pts = []
        for i in range(10):
            r = 11 if i % 2 == 0 else 4.6
            a = math.radians(-90 + 36 * i)
            pts.append(f"{14 + r * math.cos(a):.2f},{15 + r * math.sin(a):.2f}")
        body = f'<polygon points="{" ".join(pts)}" fill="{ACCENT}" stroke="#000" stroke-width="{sw}" stroke-linejoin="round"/>'
    elif k == 2:
        body = (f'<line x1="14" y1="5.5" x2="14" y2="3.6" stroke="#000" stroke-width="{sw}" stroke-linecap="round"/>'
                f'<circle cx="14" cy="16" r="9" fill="{TINT}" stroke="#000" stroke-width="{sw}"/>'
                f'<rect x="10.5" y="5.5" width="7" height="3.6" fill="#fff" stroke="#000" stroke-width="{sw}" stroke-linejoin="round"/>')
    else:
        body = (f'<polygon points="14,2.8 21,10 7,10" fill="{TINT}" stroke="#000" stroke-width="{sw}" stroke-linejoin="round"/>'
                f'<polygon points="14,7 23,16 5,16" fill="{TINT}" stroke="#000" stroke-width="{sw}" stroke-linejoin="round"/>'
                f'<polygon points="14,12 25,22 3,22" fill="{TINT}" stroke="#000" stroke-width="{sw}" stroke-linejoin="round"/>'
                f'<rect x="12.2" y="22" width="3.6" height="3.2" fill="#000" stroke="#000" stroke-width="{sw}"/>')
    return f'<svg class="ic" data-n="{k}" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 28 28" width="26pt" height="26pt" style="display:block">{body}</svg>'


def build_events(tokens):
    ev, groups, t = [], [], Fraction(0)
    for tk in tokens:
        idxs = []
        for kind, dur in TOKDEF[tk]:
            ev.append({"kind": kind, "dur": dur, "t": t})
            idxs.append(len(ev) - 1)
            t += dur
        if len(TOKDEF[tk]) > 1 and TOKDEF[tk][0][1] < 1:
            groups.append(idxs)
    return ev, groups, t


SYM_U = 42.0


SUBF = 0.8       # inside a beat the notes use 80% of the beat column, so the next beat starts clearly apart from a group of sixteenths


def pos(t):
    t = Fraction(t)
    b = t.numerator // t.denominator
    return b + SUBF * float(t - b)


def rhythm_svg(tokens, kind, uid, w=250.0, S=7.0, labels=False, nbeats=4):
    """One rhythm on a one-line staff. kind: card (clef, 4/4, final barline), ex (same, with counts and syllables), sym (just the line)."""
    ev, groups, total = build_events(tokens)
    assert total == nbeats, (tokens, total)
    hw = HEAD_W * S
    y0 = 4.9 * S
    sw = 0.13 * S
    withbar = kind in ("card", "ex")
    if withbar:
        xclef = 6.0
        xts = xclef + CLEF_W * S + 0.9 * S
        x0 = xts + TS_W * S + 0.9 * S
        bx = w - 3.0 - 0.18 * S
        thin = bx - 0.5 * S
        x_first = x0 + 1.0 * S + hw / 2
        u = (thin - 0.07 * S - 5.0 - hw / 2 - x_first) / pos(Fraction(15, 4))
    else:
        x0 = 2.0
        x_first = x0 + 1.2 * S + hw / 2
        u = SYM_U
        w = x_first + nbeats * u + 6.0
    H = y0 + (6.6 * S if labels else 3.5 * S if withbar else 2.3 * S)
    X = lambda t: x_first + pos(t) * u
    o = [f'<svg class="ns" data-kind="{kind}" data-id="{uid}" data-s="{fx(S)}" data-y0="{fx(y0)}" data-x0="{fx(x_first)}" data-u="{fx(u)}" '
         f'xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.2f} {H:.2f}" width="{w:.2f}pt" height="{H:.2f}pt" style="display:block">']
    o.append(f'<line class="sl" x1="2" y1="{fx(y0)}" x2="{fx(w - 2)}" y2="{fx(y0)}" stroke="#000" stroke-width="{fx(sw)}"/>')
    if withbar:
        o.append(gl(G_NEUTRAL, xclef, y0, 4 * S, "clef"))
        o.append(gl(G_TS4, xts, y0 - 1.25 * S, 4 * S, "tsd"))
        o.append(gl(G_TS4, xts, y0 + 1.25 * S, 4 * S, "tsd"))
        o.append(f'<line class="bar" x1="{fx(thin)}" y1="{fx(y0 - 2 * S)}" x2="{fx(thin)}" y2="{fx(y0 + 2 * S)}" stroke="#000" stroke-width="{fx(0.14 * S)}"/>')
        o.append(f'<rect class="fin" x="{fx(bx - 0.18 * S)}" y="{fx(y0 - 2 * S)}" width="{fx(0.36 * S)}" height="{fx(4 * S)}" fill="#000"/>')
    tip = y0 - STEM_X * S - STEM_LEN * S
    stem_x = {}
    for i, e in enumerate(ev):
        xc = X(e["t"])
        if e["kind"] == "r":
            o.append(f'<g class="ev">{gl(G_QREST, xc - REST_W * S / 2, y0, 4 * S, "rest")}</g>')
            continue
        left = xc - hw / 2
        sx = left + hw - sw / 2
        stem_x[i] = sx
        glyph = G_HALF if e["kind"] == "h" else G_HEAD
        o.append(f'<g class="ev">{gl(glyph, left, y0, 4 * S, "head")}'
                 f'<line class="stem" x1="{fx(sx)}" y1="{fx(y0 - STEM_X * S)}" x2="{fx(sx)}" y2="{fx(tip)}" stroke="#000" stroke-width="{fx(sw)}"/></g>')
    for g in groups:
        x1, x2 = stem_x[g[0]] - sw / 2, stem_x[g[-1]] + sw / 2
        o.append(f'<rect class="beam" data-lvl="1" x="{fx(x1)}" y="{fx(tip)}" width="{fx(x2 - x1)}" height="{fx(0.5 * S)}" fill="#000"/>')
        run = []
        for i in g + [None]:
            if i is not None and ev[i]["dur"] == Fraction(1, 4):
                run.append(i)
                continue
            if len(run) >= 2:
                a, b = stem_x[run[0]] - sw / 2, stem_x[run[-1]] + sw / 2
                o.append(f'<rect class="beam" data-lvl="2" x="{fx(a)}" y="{fx(tip + 0.75 * S)}" width="{fx(b - a)}" height="{fx(0.5 * S)}" fill="#000"/>')
            run = []
    if labels:
        t = Fraction(0)
        for b in range(4):
            o.append(f'<text class="cnt" x="{fx(X(b) )}" y="{fx(y0 + 3.55 * S)}" text-anchor="middle" font-family="Source Sans 3, sans-serif" font-weight="600" font-size="8.5" fill="#555">{b + 1}</text>')
        t = Fraction(0)
        for tk in tokens:
            span = token_beats(tk)
            starts = []
            tt = t
            for _k, d in TOKDEF[tk]:
                starts.append(tt)
                tt += d
            cx = X(t) + 0.5 * u if tk == "ta-a" else (X(starts[0]) + X(starts[-1])) / 2
            o.append(f'<text class="syl" x="{fx(cx)}" y="{fx(y0 + 5.7 * S)}" text-anchor="middle" font-family="Source Sans 3, sans-serif" font-weight="700" font-size="7.2">{tk}</text>')
            t += span
    o.append("</svg>")
    return "".join(o)


def card_svg(game, n):
    return rhythm_svg(GAMES[game]["cards"][n], "card", f"L{game}-{n:02d}", w=246.0)


# ------------------------------------------------------------------ CSS and page frame
def font_css():
    f = os.path.relpath(FONTS, BUILD)
    faces = [("Oswald", 300, "normal", "oswald-latin-300-normal"), ("Oswald", 500, "normal", "oswald-latin-500-normal"),
             ("Oswald", 700, "normal", "oswald-latin-700-normal"),
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
.h { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; letter-spacing: .01em; line-height: 1; }
.l { font-family: 'Oswald'; font-weight: 300; }
.top { display: flex; justify-content: space-between; align-items: flex-end; border-bottom: 2.2pt solid #000; padding-bottom: 6pt; }
.top .t { font-size: 22pt; white-space: nowrap; }
.top .tag { flex: none; white-space: nowrap; }
.top .t small { display: block; font-family: 'Oswald'; font-weight: 300; text-transform: none; font-size: 12pt; letter-spacing: 0; margin-top: 4pt; }
.top.slim .t { font-size: 18pt; }
.top.slim .t small { font-size: 11pt; margin-top: 3pt; }
.tag { text-align: right; }
.tag .lv { display: inline-block; background: #000; color: #fff; font-family: 'Oswald'; font-weight: 700; font-size: 15pt; padding: 3pt 9pt 4pt; border-radius: 4pt; letter-spacing: .04em; }
.tag .lv.ak { background: ACCENT; }
.tag .ln { font-family: 'Oswald'; font-weight: 300; font-size: 11pt; margin-top: 3pt; }
.foot { display: flex; justify-content: space-between; font-size: 8.5pt; color: #333; border-top: .8pt solid #000; padding-top: 3pt; }
.wm { position: absolute; left: 50%; top: 50%; transform: translate(-50%, -50%) rotate(-38deg); font-family: 'Oswald'; font-weight: 700;
      font-size: 150pt; color: rgba(0,0,0,.13); letter-spacing: .06em; white-space: nowrap; pointer-events: none; z-index: 9; }
.doc h1 { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 30pt; margin: 0 0 4pt; line-height: 1; }
.doc h2 { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 14pt; margin: 9pt 0 3pt; letter-spacing: .02em; }
.doc p, .doc li { font-size: 10.6pt; line-height: 1.34; margin: 0 0 5pt; }
.doc ul { margin: 0 0 4pt; padding-left: 16pt; }
.doc .rule { border-bottom: 2.2pt solid #000; margin-bottom: 8pt; padding-bottom: 6pt; }
.doc table { border-collapse: collapse; width: 100%; table-layout: fixed; font-size: 10pt; margin: 2pt 0 4pt; }
.doc td, .doc th { border: 1pt solid #000; padding: 3.5pt 6pt; text-align: left; vertical-align: middle; }
.doc th { font-family: 'Oswald'; font-weight: 500; text-transform: uppercase; font-size: 9.5pt; background: #000; color: #fff; }
.small { font-size: 9pt !important; color: #333; }
.box { border: 1.3pt solid #000; border-radius: 7pt; padding: 7pt 10pt 4pt; margin: 6pt 0; }
.box h3 { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 12.5pt; margin: 0 0 3pt; letter-spacing: .02em; }
.box p { margin: 0 0 4pt !important; font-size: 10.4pt !important; }
.cols { display: flex; gap: 12pt; }
.cols .box { flex: 1; margin: 6pt 0; }
.steps { display: flex; flex-direction: column; gap: 6pt; margin: 4pt 0 2pt; }
.step { display: flex; gap: 9pt; align-items: flex-start; border: 1.3pt solid #000; border-radius: 7pt; padding: 6pt 10pt 3pt 8pt; }
.step .n { flex: none; background: ACCENT; color: #fff; font-family: 'Oswald'; font-weight: 700; font-size: 13pt; border-radius: 50%; width: 22pt; height: 22pt; line-height: 22pt; text-align: center; }
.step p { margin: 0 0 3pt !important; font-size: 10.6pt !important; line-height: 1.3 !important; }
.pt { white-space: nowrap; }
.cinstr { font-size: 10pt; margin: 6pt 0 6pt; line-height: 1.3; }
.cgrid { flex: 1; display: grid; grid-template-columns: 3.68in 3.68in; grid-template-rows: repeat(4, 1fr); gap: 0.15in 0.14in; justify-content: center; padding-bottom: 0.1in; }
.card { border: 1.1pt dashed #000; border-radius: 8pt; padding: 6pt 9pt 5pt; display: flex; flex-direction: column; overflow: hidden; background: #fff; }
.card .ch { display: flex; align-items: center; gap: 7pt; }
.card .cn { background: #000; color: #fff; font-family: 'Oswald'; font-weight: 700; font-size: 15pt; line-height: 1; border-radius: 5pt; padding: 3pt 8pt 3.5pt; min-width: 26pt; text-align: center; }
.card .lvt { font-family: 'Oswald'; font-weight: 300; font-size: 9.5pt; letter-spacing: .06em; text-transform: uppercase; }
.card .mk { font-family: 'Oswald'; font-weight: 500; font-size: 7pt; letter-spacing: .1em; padding: 1pt 5pt; border-radius: 8pt; color: #fff; background: ACCENT; }
.card .mk.end { background: #000; }
.card .ic { margin-left: auto; }
.card .lab { font-family: 'Oswald'; font-weight: 500; font-size: 9pt; letter-spacing: .12em; text-transform: uppercase; margin: 1pt 0 0; }
.card svg.ns { margin: 0 auto; }
.card .wh { font-size: 12.5pt; font-weight: 700; line-height: 1.22; margin-top: auto; padding-bottom: 1pt; }
.card .wh .w { color: ACCENT; }
.card .wh .tk { white-space: nowrap; }
.krow td { padding: 2pt 6pt !important; font-size: 10pt; height: 19pt; }
.krow td.c { text-align: center; }
.krow .mkc { font-family: 'Oswald'; font-weight: 500; font-size: 8pt; letter-spacing: .08em; color: ACCENT; }
.loop { font-size: 10.6pt; line-height: 1.5; font-weight: 600; margin: 3pt 0 4pt; }
.syt td.sy { text-align: center; }
.syt td.sy svg { margin: 1pt auto; }
.syt td { padding: 1.5pt 6pt !important; }
.syt td.sd { font-family: 'Oswald'; font-weight: 700; font-size: 15pt; letter-spacing: .02em; text-align: center; }
.exbox { border: 1.3pt solid #000; border-radius: 7pt; padding: 4pt 8pt 2pt; flex: 1; }
.exbox svg { margin: 0 auto; }
.cover { align-items: center; justify-content: space-between; padding: 0.55in 0.6in 0.5in; }
.store { font-family: 'Oswald'; font-weight: 500; font-size: 13pt; letter-spacing: .32em; text-transform: uppercase; }
.ctitle { text-align: center; }
.ctitle .a { font-family: 'Oswald'; font-weight: 700; font-size: 40pt; line-height: 1; letter-spacing: .02em; }
.ctitle .b { font-family: 'Oswald'; font-weight: 700; white-space: nowrap; font-size: 70pt; line-height: .95; letter-spacing: .01em; }
.ctitle .c { font-family: 'Oswald'; font-weight: 300; font-size: 17pt; margin-top: 8pt; }
.cband { width: 100%; background: #000; color: #fff; text-align: center; font-family: 'Oswald'; font-weight: 500; font-size: 14pt;
         letter-spacing: .08em; text-transform: uppercase; padding: 8pt 0 9pt; border-radius: 4pt; }
.cband em { font-style: normal; color: ACCENT; }
""".replace("ACCENT", ACCENT)


def html_doc(pages, title="doc"):
    return (f'<!doctype html><html><head><meta charset="utf-8"><title>{escape(title)}</title><style>{font_css()}{CSS}</style></head>'
            f'<body>{"".join(pages)}</body></html>')


def foot(left, right):
    return f'<div class="foot"><span>{left}</span><span>{right}</span></div>'


COPY = f"© {YEAR} {STORE} · {BRAND} · For single-classroom use"

# ------------------------------------------------------------------ page numbers (single source of truth)
P_COVER, P_TEACH, P_HOW, P_SYL = 1, 2, 3, 4
P_C1, P_K1, P_C2, P_K2, P_TERMS = 5, 8, 9, 12, 13       # level 1 cards 5-7, key 8, level 2 cards 9-11, key 12
TOTAL_PAGES = P_TERMS
RANGES = ["1–8", "9–16", "17–24"]
PAGE_NAMES = {P_COVER: "cover", P_TEACH: "Teacher notes", P_HOW: "How to play", P_SYL: "Rhythm syllables guide",
              P_K1: "Level 1 teacher key", P_K2: "Level 2 teacher key", P_TERMS: "Terms of use"}
for _i in range(3):
    PAGE_NAMES[P_C1 + _i] = f"Level 1 cards {RANGES[_i]}"
    PAGE_NAMES[P_C2 + _i] = f"Level 2 cards {RANGES[_i]}"
XREFS = []


def xref(frm, to, text):
    XREFS.append((frm, to, text))
    return text


def wm_div(on):
    return '<div class="wm">PREVIEW</div>' if on else ""


def top_block(sub, tag, tagline, ak=False, slim=False):
    return (f'<div class="top{" slim" if slim else ""}"><div class="h t">{TITLE}<small>{sub}</small></div>'
            f'<div class="tag"><div class="lv{" ak" if ak else ""}">{tag}</div><div class="ln">{tagline}</div></div></div>')


# ------------------------------------------------------------------ pages
def cover_art_img(height):
    return f'<img src="../art/hero.png" alt="" style="display:block;height:{height};width:auto">'


def cover_page():
    return (f'<section class="page cover"><div class="store">{BRAND}</div>'
            f'<div style="height:4.9in;display:flex;align-items:center;justify-content:center">{cover_art_img("4.9in")}</div>'
            f'<div class="ctitle"><div class="a">HOLIDAY RHYTHM</div><div class="b">I HAVE, WHO HAS</div>'
            f'<div class="c">Two 24-card loop games · quarter, eighth and sixteenth notes</div></div>'
            f'<div class="cband">Grades 2–5 <em>·</em> 48 cards <em>·</em> {TOTAL_PAGES} pages</div></section>')


def teacher_page(wm=False):
    pace = [("Lesson 1", "Teach ta, shh, ti-ti and ta-a with the guide (page %d), then try the rhythm echo." % P_SYL, "Level 1"),
            ("Lesson 2", "Play Level 1 as a whole class (page %d) with a slow, steady beat." % P_HOW, "Level 1"),
            ("Lesson 3", "Play Level 1 in small groups or with partners. Swap cards between rounds.", "Level 1"),
            ("Lesson 4", "Teach sixteenth notes: ti-ka-ti-ka first, then ti-ti-ka and ti-ka-ti.", "Level 2"),
            ("Lesson 5", "Play Level 2 as a whole class, then in groups, and assess.", "Level 2")]
    prow = "".join(f"<tr><td><b>{a}</b></td><td>{b}</td><td>{c}</td></tr>" for a, b, c in pace)
    return (f'<section class="page doc">{wm_div(wm)}<div class="rule"><h1>Teacher Notes</h1>'
            f'<div class="l" style="font-size:13pt">{TITLE} · two games of 24 cards · grades 2–5</div></div>'
            f'<p><b>What this is.</b> Two complete "I have, who has" loop games for the music room. Each card shows a one-bar rhythm in 4/4 and asks for another card\'s rhythm by its rhythm syllables. '
            f'Students read notation, say the syllables and clap. Level 1 uses quarter notes, quarter rests, pairs of eighth notes and half notes. '
            f'Level 2 adds sixteenth-note patterns. The holiday art is non-denominational: snowflakes, stars, ornaments and trees.</p>'
            f'<p><b>Getting ready.</b> Print the cards on card stock and cut on the dashed lines. Level 1 cards are on pages {P_C1}–{P_C1 + 2} and Level 2 cards are on pages {P_C2}–{P_C2 + 2}. '
            f'Each level has its own teacher key with the loop order: page {P_K1} for Level 1 and page {P_K2} for Level 2. '
            f'The card numbers are only for sorting. Card 1 is marked START and the card that closes the loop is marked END. The rules of play are on page {P_HOW}.</p>'
                        f'<h2>Suggested pacing</h2><table><tr><th style="width:52pt">When</th><th>Focus</th><th style="width:52pt">Cards</th></tr>{prow}</table>'
            f'<h2>Differentiation</h2><ul>'
            f'<li><b>Grades 2–3.</b> Start with Level 1. Do the rhythm echo first, keep the beat for the class, and let students keep the syllables guide (page {P_SYL}) beside them. '
            f'Give a student a partner or a second look at the card before they answer.</li>'
            f'<li><b>Grades 4–5.</b> Play Level 1 quickly as a warm-up, then move to Level 2. Remove the teacher beat so the class keeps its own, '
            f'and challenge groups to close the loop with no mistakes. Ask students to explain how ti-ti-ka differs from ti-ka-ti when they are written and when they are clapped.</li></ul>'
            f'<h2>Assessment idea</h2><p>While a loop is played, listen to each student clap and say their own "I have" rhythm. Mark a class list with a check for a steady beat, '
            f'a check for syllables that match the notation, and a check for reading the "Who has" prompt correctly. For a quick written follow-up, say one prompt aloud and ask students to draw the rhythm in one bar of 4/4.</p>'
            f'<h2>Standards</h2><p>The games support the Performing and Responding processes of the National Core Arts Standards. Please match them to your own curriculum.</p>'
            f'<h2>What is inside ({TOTAL_PAGES} pages)</h2><p>Page 1 cover, page 2 these notes, page {P_HOW} how to play, page {P_SYL} rhythm syllables guide, pages {P_C1}–{P_C1 + 2} Level 1 cards, '
            f'page {P_K1} Level 1 teacher key, pages {P_C2}–{P_C2 + 2} Level 2 cards, page {P_K2} Level 2 teacher key and page {P_TERMS} terms of use.</p>'
            f'<p class="small">No songs, lyrics or copyrighted characters are used.</p>'
            f'<div style="flex:1"></div>{foot(COPY, "Page 2")}</section>')


def how_page(wm=False):
    steps = [("Deal.", f"Give each student one card from the same level. With fewer than 24 students, give some students two or three cards and have them answer for each. With more than 24, let students share a card as partners."),
             ("Start.", "The student holding card 1, the START card, reads the Who has prompt aloud in rhythm syllables, keeping a steady beat."),
             ("Answer.", "Everyone checks the I have rhythm on their own card. The student whose rhythm matches stands, claps it while saying the syllables, and then reads their own Who has prompt."),
             ("Finish.", "Play continues until the END card reads its prompt, which names the START card. The START student then claps their own I have rhythm, and the loop is closed after all 24 cards.")]
    srows = "".join(f'<div class="step"><span class="n">{i + 1}</span><div><p><b>{a}</b> {b}</p></div></div>' for i, (a, b) in enumerate(steps))
    return (f'<section class="page doc">{wm_div(wm)}<div class="rule"><h1>How to Play</h1>'
            f'<div class="l" style="font-size:13pt">Whole class, small groups, partners and the rhythm echo</div></div>'
            f'<p>Every card has an <b>I have</b> rhythm and a <b>Who has</b> prompt. The prompt spells out another card\'s rhythm in rhythm syllables, such as "ta ti-ti ta shh", so exactly one card matches it. '
            f'Because the prompts form one loop, the class visits all 24 cards once and comes back to the start.</p>'
            f'<div class="box"><h3>Before you play</h3><p>Print the cards, cut on the dashed lines and keep each level in its own envelope. Level 1 cards are on pages {xref(P_HOW, P_C1, f"{P_C1}–{P_C1 + 2}")} '
            f'and Level 2 cards are on pages {P_C2}–{P_C2 + 2}. Review the syllables on page {xref(P_HOW, P_SYL, str(P_SYL))} first. '
            f'The loop order for each level is on the teacher keys, page {xref(P_HOW, P_K1, str(P_K1))} and page {xref(P_HOW, P_K2, str(P_K2))}.</p></div>'
            f'<h2>Whole class</h2><div class="steps">{srows}</div>'
            f'<div class="cols"><div class="box"><h3>Small groups</h3><p>Use groups of 4 to 6 students and one set of 24 cards per group. Deal every card, so each student holds several. '
            f'Play exactly like the whole class game. Groups can race to close their loop with no mistakes, or try for the steadiest beat.</p></div>'
            f'<div class="box"><h3>Partner version</h3><p>Partners share one set. Spread all 24 cards face up in any order. Partner A reads the Who has prompt on the START card. '
            f'Partner B finds the card with that I have rhythm, claps and says it, and lays it next in the row, then reads its prompt. Switch roles after each card. '
            f'The chain is done when the END card is placed, and the partners check their row against the teacher key.</p></div></div>'
            f'<div class="box"><h3>Rhythm echo variation</h3><p>Before a student reads their Who has prompt, they clap their I have rhythm one time without speaking. The whole class echoes it by clapping the same rhythm, '
            f'and then everyone says the syllables together. Then the student reads the prompt and play moves on. The echo works well with body percussion too: pat, snap or stamp instead of clapping. A slow steady beat of about 60 beats per minute works well at first.</p></div>'
            f'<div style="flex:1"></div>{foot(COPY, f"Page {P_HOW}")}</section>')


SYM_ROWS = [  # (tokens, name, beats shown, say, level)
    (["ta"], "Quarter note", "1 beat", "ta", "Level 1"),
    (["shh"], "Quarter rest (silence)", "1 beat", "shh", "Level 1"),
    (["ti-ti"], "Two eighth notes, joined by a beam", "1 beat together", "ti-ti", "Level 1"),
    (["ta-a"], "Half note", "2 beats", "ta-a", "Level 1"),
    (["ti-ka-ti-ka"], "Four sixteenth notes, joined by two beams", "1 beat together", "ti-ka-ti-ka", "Level 2"),
    (["ti-ti-ka"], "Eighth note then two sixteenth notes", "1 beat together", "ti-ti-ka", "Level 2"),
    (["ti-ka-ti"], "Two sixteenth notes then an eighth note", "1 beat together", "ti-ka-ti", "Level 2"),
]
EXAMPLES = [("ex1", ["ta", "ti-ti", "ta", "shh"]), ("ex2", ["ti-ka-ti-ka", "ta", "ti-ti-ka", "shh"])]


def syl_page(wm=False):
    rows = ""
    for toks, name, beats, say, lvl in SYM_ROWS:
        nb = int(sum(token_beats(t) for t in toks))
        svg = rhythm_svg(toks, "sym", f"sym-{say}", nbeats=nb, S=5.6)
        rows += f'<tr><td class="sy">{svg}</td><td><b>{name}</b></td><td>{beats}</td><td class="sd">{say}</td><td>{lvl}</td></tr>'
    exs = "".join(f'<div class="exbox">{rhythm_svg(t, "ex", uid, w=246.0, labels=True, S=6.8)}</div>' for uid, t in EXAMPLES)
    return (f'<section class="page doc">{wm_div(wm)}<div class="rule"><h1>Rhythm Syllables Guide</h1>'
            f'<div class="l" style="font-size:13pt">How to say and clap every rhythm in the games</div></div>'
            f'<table class="syt"><tr><th style="width:130pt">Notation</th><th>Name</th><th style="width:70pt">Length</th><th style="width:92pt">Say</th><th style="width:46pt">Level</th></tr>{rows}</table>'
            f'<h2>Clapping and speaking</h2><ul>'
            f'<li><b>Steady beat first.</b> In 4/4 each bar has four beats and a quarter note gets one beat. Count "1 2 3 4" or pat the beat while you say the syllables.</li>'
            f'<li><b>Clap every note.</b> Clap when a note starts. A rest is silence: say "shh" with your hands apart. Clap a half note once and hold your hands together for two beats while you say "ta-a".</li>'
            f'<li><b>Beams.</b> Eighth notes joined by a beam share one beat, so each is half a beat. Sixteenth notes have two beams and four of them share one beat, so each is a quarter of a beat.</li>'
            f'<li><b>Reading the card.</b> The notes sit on a one-line rhythm staff and every stem points up. The mark at the start is the neutral clef, used for rhythm without pitches, and 4/4 means four quarter-note beats in each bar.</li></ul>'
            f'<h2>Try it</h2><div class="cols">{exs}</div>'
            f'<div style="flex:1"></div>{foot(COPY, f"Page {P_SYL}")}</section>')


def card_html(game, n):
    g = GAMES[game]
    nxt = g["next"][n]
    mk = ""
    if n == 1:
        mk = '<span class="mk" data-mk="start">START</span>'
    elif n == g["end"]:
        mk = '<span class="mk end" data-mk="end">END</span>'
    prompt = " ".join(f'<span class="tk">{t}</span>' for t in g["cards"][nxt])
    return (f'<div class="card" data-game="{game}" data-n="{n}"><div class="ch"><span class="cn">{n}</span><span class="lvt">Level {game}</span>{mk}{icon_svg(n)}</div>'
            f'<div class="lab">I have</div>{card_svg(game, n)}'
            f'<div class="wh"><span class="w">Who has</span> {prompt}?</div></div><!--/card-->')


def cards_page(game, k, wm=False):
    page = (P_C1 if game == 1 else P_C2) + k
    cards = "".join(card_html(game, n) for n in range(k * 8 + 1, k * 8 + 9))
    return (f'<section class="page">{wm_div(wm)}{top_block(PAGE_NAMES[page], f"LEVEL {game}", "Game cards", slim=True)}'
            f'<div class="cinstr">Cut on the dashed lines. Card numbers are for sorting; they are not the order of play.</div>'
            f'<div class="cgrid">{cards}</div>{foot(COPY, f"Page {page}")}</section>')


def key_page(game, wm=False):
    g = GAMES[game]
    page = P_K1 if game == 1 else P_K2
    rows = ""
    for i, n in enumerate(g["order"]):
        mk = "START" if n == 1 else ("END" if n == g["end"] else "")
        rows += (f'<tr class="krow" data-step="{i + 1}" data-game="{game}"><td class="c">{i + 1}</td><td class="c kc">{n}</td><td class="c mkc">{mk}</td>'
                 f'<td class="ks">{syl(g["cards"][n])}</td><td class="c kn">{g["next"][n]}</td></tr>')
    loop = " → ".join(str(n) for n in g["order"] + [1])
    return (f'<section class="page doc">{wm_div(wm)}{top_block(PAGE_NAMES[page], "ANSWER KEY", f"Level {game} loop order", ak=True, slim=True)}'
            f'<p style="margin-top:8pt"><b>How to read this key.</b> Each row is one step of the game. The card in the Card column says its I have rhythm; its Who has prompt names the card in the last column. '
            f'Step 1 is the START card and step 24 is the END card. After step 24 the START card answers once more and the loop is closed.</p>'
            f'<table><tr><th style="width:44pt">Step</th><th style="width:44pt">Card</th><th style="width:52pt"></th><th>I have (rhythm syllables)</th><th style="width:78pt">Who has: card</th></tr>{rows}</table>'
            f'<div class="loop" data-loop="{game}">Loop: {loop}</div>'
            f'<div style="flex:1"></div>{foot(COPY, f"Page {page}")}</section>')


def terms_page(wm=False):
    return (f'<section class="page doc">{wm_div(wm)}<div class="rule"><h1>Terms of Use</h1><div class="l" style="font-size:13pt">Thank you for your purchase!</div></div>'
            f'<p>© {YEAR} {STORE}. {BRAND} by {STORE}. All rights reserved. This purchase gives <b>one teacher</b> a license to use this resource with their own students.</p>'
            f'<h2>You may</h2><ul><li>Print and copy pages for your own classroom and students, year after year.</li>'
            f'<li>Share pages with your own students through a password-protected class site or learning platform.</li>'
            f'<li>Use the pages with your own students when you have a substitute teacher.</li></ul>'
            f'<h2>You may not</h2><ul><li>Share, email or copy this resource for other teachers, a whole school or a district. Additional licenses are available on Teachers Pay Teachers.</li>'
            f'<li>Post any part of it on a public website, shared drive or social media.</li>'
            f'<li>Sell, give away or claim any part of it as your own, or edit it into a new product.</li></ul>'
            f'<h2>Questions?</h2><p>Please use the Q&amp;A tab on the {BRAND} by {STORE} store on Teachers Pay Teachers. If something looks wrong, let me know there and I will fix it.</p>'
            f'<h2>Credits</h2><ul>'
            f'<li>The rhythms, cards, teacher keys and corner icons are original work, {BRAND} by {STORE}.</li>'
            f'<li>Cover artwork: an illustration made with AI tools. The notation, cards and text are drawn in code.</li>'
            f'<li>Music notation font: Bravura © Steinberg Media Technologies GmbH, SIL Open Font License 1.1.</li>'
            f'<li>Text fonts: Oswald (The Oswald Project Authors) and Source Sans 3 (Adobe), SIL Open Font License 1.1.</li></ul>'
            f'<h2>What is in this file</h2><p>Page 1 cover, page 2 teacher notes, page {P_HOW} how to play, page {P_SYL} rhythm syllables guide, pages {P_C1}–{P_C1 + 2} Level 1 cards, '
            f'page {P_K1} Level 1 teacher key, pages {P_C2}–{P_C2 + 2} Level 2 cards, page {P_K2} Level 2 teacher key and page {P_TERMS} these terms.</p>'
            f'<p class="small">{DISCLOSURE}</p><div style="flex:1"></div>{foot(COPY, f"Page {P_TERMS}")}</section>')


def full_pages():
    XREFS.clear()
    pages = ([cover_page(), teacher_page(), how_page(), syl_page()] + [cards_page(1, k) for k in range(3)] + [key_page(1)]
             + [cards_page(2, k) for k in range(3)] + [key_page(2), terms_page()])
    assert len(pages) == TOTAL_PAGES, len(pages)
    return pages


PREVIEW_PAGES = [P_C1, P_C2, P_HOW, P_K1]


def preview_pages():
    fn = {P_C1: lambda wm: cards_page(1, 0, wm), P_C2: lambda wm: cards_page(2, 0, wm), P_HOW: how_page, P_K1: lambda wm: key_page(1, wm)}
    return [fn[p](True) for p in PREVIEW_PAGES]


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
""".replace("ACCENT", ACCENT)


def sq_doc(body):
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{font_css()}html,body{{margin:0;background:#fff;font-family:"Source Sans 3",sans-serif}}{SQ_CSS}</style></head><body>'
            f'{body}</body></html>')


def cover_square():
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div>'
        f'<div style="flex:1;display:flex;flex-direction:column;justify-content:space-evenly;align-items:center;width:100%;padding:0 0 76px">'
        f'<div style="height:500px;display:flex;align-items:center">{cover_art_img("500px")}</div>'
        f'<div><div class="hd" style="font-size:64px">Holiday Rhythm</div><div class="hd" style="font-size:112px">I Have, Who Has</div>'
        f'<div class="sub" style="font-size:28px;margin-top:12px">Two 24-card loop games · quarter, eighth and sixteenth notes</div></div>'
        f'</div><div class="band">Grades 2–5 <em>·</em> 48 cards <em>·</em> {TOTAL_PAGES} pages</div></div>')


def swm_over(size=230):
    return f'<div class="swm" style="font-size:{size}px">PREVIEW</div>'


def shot(src, w):
    return f'<div class="shot" style="width:{w}px"><img src="{src}"></div>'


def preview_square_1(img):
    caps = [(PAGE_NAMES[P_C1], "Eight cards a page, cut lines, START marker"), (PAGE_NAMES[P_HOW], "Whole class, groups, partners and echo"),
            (PAGE_NAMES[P_SYL], "Every syllable with its notation")]
    shots = "".join(
        f'<div style="width:290px;display:flex;flex-direction:column;align-items:center">{shot(img[i], 290)}'
        f'<div class="lbl" style="font-size:24px;margin-top:20px">{caps[i][0]}</div>'
        f'<div style="font-family:Oswald;font-weight:300;font-size:20px;line-height:1.25;text-align:center;margin-top:8px;width:270px">{caps[i][1]}</div></div>' for i in range(3))
    pills = "".join(f'<div style="border:2px solid #000;border-radius:30px;padding:6px 22px;font-family:Oswald;font-weight:500;font-size:24px;letter-spacing:.06em;text-transform:uppercase">{t}</div>'
                    for t in ("2 games", "48 cards", "2 teacher keys"))
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div><div class="hd" style="font-size:72px;margin-top:28px">What is inside</div>'
        f'<div class="sub" style="font-size:29px;margin-top:10px">Everything for two rhythm loop games</div>'
        f'<div style="flex:1;display:flex;flex-direction:column;align-items:center;justify-content:space-evenly;padding-bottom:70px">'
        f'<div style="display:flex;gap:22px;align-items:flex-start">{shots}</div><div style="display:flex;gap:18px">{pills}</div></div>'
        f'{swm_over(230)}<div class="band">Read it <em>·</em> Say it <em>·</em> Clap it <em>·</em> {TOTAL_PAGES} pages</div></div>')


def preview_square_2(a, b):
    pair = "".join(f'<div style="width:380px">{shot(src, 380)}<div class="lbl">{lab}<span>{sub}</span></div></div>'
                   for src, lab, sub in ((a, PAGE_NAMES[P_C1], "Quarter notes, rests, eighths, halves"), (b, PAGE_NAMES[P_C2], "Adds sixteenth notes")))
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div><div class="hd" style="font-size:72px;margin-top:24px">Two levels of cards</div>'
        f'<div class="sub" style="font-size:27px;margin-top:8px">24 cards each, every rhythm different</div>'
        f'<div style="flex:1;display:flex;align-items:center;padding-bottom:70px"><div style="display:flex;gap:44px;align-items:flex-start">{pair}</div></div>'
        f'{swm_over(230)}<div class="band">Level 1 <em>·</em> Level 2 <em>·</em> one closed loop each</div></div>')


def preview_square_3(a, b):
    pair = "".join(f'<div style="width:380px">{shot(src, 380)}<div class="lbl">{lab}</div></div>' for src, lab in ((a, PAGE_NAMES[P_K1]), (b, PAGE_NAMES[P_K2])))
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div><div class="hd" style="font-size:72px;margin-top:24px">Loop keys included</div>'
        f'<div class="sub" style="font-size:27px;margin-top:8px">Check the order of play at a glance</div>'
        f'<div style="flex:1;display:flex;align-items:center;padding-bottom:70px"><div style="display:flex;gap:44px;align-items:flex-start">{pair}</div></div>'
        f'{swm_over(230)}<div class="band">Card to card <em>·</em> start to end <em>·</em> 24 steps</div></div>')


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


PAGE_LIST = [("Cover", 1), ("Teacher notes", 1), ("How to play", 1), ("Rhythm syllables guide", 1), ("Level 1 cards (8 per page)", 3),
             ("Level 1 teacher key", 1), ("Level 2 cards (8 per page)", 3), ("Level 2 teacher key", 1), ("Terms of use and credits", 1)]


def upload_md():
    lst = "\n".join(f"- {n}: {c}" for n, c in PAGE_LIST)
    return f"""# UPLOAD: {LISTING_TITLE} (TpT 056)

These fields follow the order of TpT's "Add a resource" form. Winter and holiday theme: build window is December. Never put Winter, Holiday or Christmas in the title field (TpT's Seasonal Titles notice).

**Files to attach**
- Resource (digital download): `{SLUG}.pdf`, {TOTAL_PAGES} pages, US Letter.
- Thumbnails, in this order: `cover.png`, `preview-1.png`, `preview-2.png`, `preview-3.png` (all 2000 × 2000).
- Preview file: `{SLUG}-PREVIEW.pdf`, 4 watermarked pages.

## 1. Title

```
{LISTING_TITLE}
```
({len(LISTING_TITLE)} characters; the limit is 80.) Plain search words first, no seasonal words. If TpT accepts it, the preferred title is "{PREFERRED_TITLE}" ({len(PREFERRED_TITLE)} characters).

## 2. Description

```
Holiday Rhythm: I Have, Who Has is two complete loop games for the music room, 24 cards each. Every card shows a one-bar rhythm in 4/4 and asks "Who has ...?" by naming another card's rhythm in rhythm syllables, so students read notation, say the syllables and clap while the class listens. Follow the prompts and the class visits every card once and returns to the start. Level 1 uses quarter notes, quarter rests, pairs of eighth notes and half notes (ta, shh, ti-ti, ta-a). Level 2 adds sixteenth notes (ti-ka-ti-ka, ti-ti-ka, ti-ka-ti) in mixed patterns. The holiday art is non-denominational: snowflakes, stars, ornaments and trees. For music classes in grades 2 to 5.

WHAT'S INCLUDED ({TOTAL_PAGES} pages, PDF, US Letter)
• Cover (1 page)
• Teacher notes with pacing, grade 2-3 and grade 4-5 differentiation and an assessment idea (1 page)
• How to play: whole class, small groups, partner version and a rhythm echo variation (1 page)
• Rhythm syllables guide with notation, clapping and speaking tips and two examples (1 page)
• Level 1: 24 cards, 8 per page with cut lines (3 pages)
• Level 1 teacher key with the loop order (1 page)
• Level 2: 24 cards, 8 per page with cut lines (3 pages)
• Level 2 teacher key with the loop order (1 page)
• Terms of use and credits (1 page)
Total: {TOTAL_PAGES} pages, 48 cards.

HOW TO USE
Print the cards on card stock and cut on the dashed lines. Deal one card to each student, start with the card marked START, and play until the card marked END brings the class back to the start. The card numbers are only for sorting. Use the teacher keys to check the loop order. Every rhythm in a level is different, and each "Who has" prompt matches exactly one card.

• Grades 2–5
• 2 games, 48 cards, one-bar rhythms in 4/4 on a one-line rhythm staff
• Whole class, small group and partner versions, plus a rhythm echo
• Prints well in black and white

{DISCLOSURE}
```

## 3. Grades

2, 3, 4, 5.

## 4. Subjects and tags

- Subjects: {", ".join(SUBJECTS)}
- Tags: {", ".join(TAGS)}

## 5. Page count by section (totals {TOTAL_PAGES})

{lst}
- Total: {TOTAL_PAGES}

## 6. Standards

None cited by code. The teacher notes name the Performing and Responding processes of the National Core Arts Standards in general terms and ask teachers to match them to their own curriculum.

## 7. Price

**${PRICE}** (paid; owner range $3-5).

## 8. Preview

Paid. Preview PDF: Level 1 cards 1–8 (page {P_C1}), Level 2 cards 1–8 (page {P_C2}), how to play (page {P_HOW}) and the Level 1 teacher key (page {P_K1}), all watermarked.

## 9. Before you click publish

- [ ] Season: December (build window 2 to 8 weeks ahead).
- Art: cover illustration made with AI tools (disclosure line covers it); cards, notation and corner icons are drawn in code.
- Open owner question: logo beside HUDSON BEAT (see tpt/STYLE.md).
"""


def tpt_json():
    return {"price": PRICE, "license_price": PRICE, "tax_code": "Other Digital Goods - No Physical Media", "grades": GRADES, "subjects": SUBJECTS, "tags": TAGS,
            "formats": ["PDF"], "pages": TOTAL_PAGES, "answer_key": "Included",
            "files": {"product": f"{SLUG}.pdf", "preview": f"{SLUG}-PREVIEW.pdf", "thumb1": "cover.png", "thumb2": "preview-1.png", "thumb3": "preview-2.png", "thumb4": "preview-3.png"}}


def build():
    os.makedirs(BUILD, exist_ok=True)
    full = write("resource.html", html_doc(full_pages(), TITLE))
    prev = write("preview.html", html_doc(preview_pages(), "Preview"))
    render([{"html": full, "pdf": PDF}, {"html": prev, "pdf": PREVIEW_PDF}])
    for i in (P_C1, P_C2, P_HOW, P_SYL, P_K1, P_K2):      # clean (unwatermarked) page shots from the product PDF
        subprocess.run(["pdftoppm", "-png", "-r", "150", "-f", str(i), "-l", str(i), "-singlefile", PDF, os.path.join(BUILD, f"pg{i}")], check=True)
    sq = [write("cover.html", cover_square()),
          write("p1.html", preview_square_1([f"pg{P_C1}.png", f"pg{P_HOW}.png", f"pg{P_SYL}.png"])),
          write("p2.html", preview_square_2(f"pg{P_C1}.png", f"pg{P_C2}.png")),
          write("p3.html", preview_square_3(f"pg{P_K1}.png", f"pg{P_K2}.png"))]
    render([{"html": h, "png": o, "width": 1000, "height": 1000, "scale": 2} for h, o in zip(sq, [COVER_PNG] + PREVIEW_PNGS)])
    with open(UPLOAD, "w") as fh:
        fh.write(upload_md())
    with open(TPT_JSON, "w") as fh:
        json.dump(tpt_json(), fh, indent=2)
        fh.write("\n")
    print(f"built {PDF}, {PREVIEW_PDF}, cover + 3 previews, UPLOAD.md, tpt.json")


# ------------------------------------------------------------------ checks
NS = "{http://www.w3.org/2000/svg}"
SVG_RE = re.compile(r'<svg class="(?:ns|ic)".*?</svg>', re.S)


def parse_svg(txt):
    return ET.fromstring(txt)


def f(el, k, d=0.0):
    return float(el.get(k, d))


def cp_of(el):
    return ord((el.text or "?")[0])


_GLYPH = {}


def glyph_box(cp):
    """Ink box of a Bravura glyph in staff spaces: (xmin, ymin, xmax, ymax), y up, origin at the glyph origin."""
    if not _GLYPH:
        from fontTools.ttLib import TTFont
        from fontTools.pens.boundsPen import BoundsPen
        font = TTFont(os.path.join(FONTS, "bravura.woff2"))
        gs, cm, upm = font.getGlyphSet(), font.getBestCmap(), font["head"].unitsPerEm
        for c in (G_HEAD, G_HALF, G_QREST, G_NEUTRAL, G_TS4):
            bp = BoundsPen(gs)
            gs[cm[c]].draw(bp)
            _GLYPH[c] = tuple(v / upm * 4 for v in bp.bounds)
    return _GLYPH[cp]


def check_extent(root, label, errs):
    """Every drawn shape and glyph sits inside the viewBox with padding at least its stroke width (and at least 1 unit)."""
    vb = [float(x) for x in root.get("viewBox").split()]
    W, H = vb[2], vb[3]
    for el in root.iter():
        tag = el.tag.replace(NS, "")
        sw = f(el, "stroke-width", 0.0) if el.get("stroke") not in (None, "none") else 0.0
        xs, ys = [], []
        if tag == "line":
            xs, ys = [f(el, "x1"), f(el, "x2")], [f(el, "y1"), f(el, "y2")]
        elif tag == "rect":
            xs, ys = [f(el, "x"), f(el, "x") + f(el, "width")], [f(el, "y"), f(el, "y") + f(el, "height")]
        elif tag == "circle":
            r = f(el, "r")
            xs, ys = [f(el, "cx") - r, f(el, "cx") + r], [f(el, "cy") - r, f(el, "cy") + r]
        elif tag == "polygon":
            nums = [float(x) for x in re.findall(r"-?\d+(?:\.\d+)?", el.get("points", ""))]
            xs, ys = nums[0::2], nums[1::2]
        elif tag == "text":
            if el.get("font-family") == "Bravura":
                S = f(el, "font-size") / 4
                x0, y0b, x1, y1b = glyph_box(cp_of(el))
                xs = [f(el, "x") + x0 * S, f(el, "x") + x1 * S]
                ys = [f(el, "y") - y1b * S, f(el, "y") - y0b * S]
            else:
                fs = f(el, "font-size")
                wd = len((el.text or "").strip()) * 0.56 * fs
                cx = f(el, "x")
                xs = [cx - wd / 2, cx + wd / 2]
                ys = [f(el, "y") - 0.75 * fs, f(el, "y") + 0.25 * fs]
        else:
            continue
        pad = max(sw, 1.0)
        if min(xs) - sw / 2 < pad - 1e-6 or min(ys) - sw / 2 < pad - 1e-6 or max(xs) + sw / 2 > W - pad + 1e-6 or max(ys) + sw / 2 > H - pad + 1e-6:
            errs.append(f"{label}: a {tag} (stroke {sw}) is closer to the viewBox edge than max(stroke, 1)")


def read_rhythm(root, errs, expect_beats):
    """Re-read one rhythm svg from its geometry. Returns the list of beat syllables, or None."""
    label = f'{root.get("data-kind")} {root.get("data-id")}'
    kind = root.get("data-kind")
    S, y0, xf, u = f(root, "data-s"), f(root, "data-y0"), f(root, "data-x0"), f(root, "data-u")
    hw = HEAD_W * S
    sls = [el for el in root.iter(NS + "line") if el.get("class") == "sl"]
    if len(sls) != 1 or abs(f(sls[0], "y1") - y0) > 0.02 or abs(f(sls[0], "y2") - y0) > 0.02:
        errs.append(f"{label}: expected exactly one horizontal staff line")
        return None
    if f(sls[0], "stroke-width") < 0.08 * S:
        errs.append(f"{label}: staff line too thin")
    clefs = [t for t in root.iter(NS + "text") if t.get("class") == "clef"]
    tsd = sorted((f(t, "y"), cp_of(t)) for t in root.iter(NS + "text") if t.get("class") == "tsd")
    bars = [l for l in root.iter(NS + "line") if l.get("class") == "bar"]
    fins = [r for r in root.iter(NS + "rect") if r.get("class") == "fin"]
    if kind in ("card", "ex"):
        if len(clefs) != 1 or cp_of(clefs[0]) != G_NEUTRAL or abs(f(clefs[0], "y") - y0) > 0.02:
            errs.append(f"{label}: neutral clef missing or off the line")
        if [c for _, c in tsd] != [G_TS4, G_TS4] or abs(tsd[0][0] - (y0 - 1.25 * S)) > 0.02 or abs(tsd[1][0] - (y0 + 1.25 * S)) > 0.02:
            errs.append(f"{label}: time signature is not 4 over 4 around the line")
        if len(bars) != 1 or len(fins) != 1:
            errs.append(f"{label}: expected one barline and one thick final barline")
    elif clefs or tsd or bars or fins:
        errs.append(f"{label}: symbol example should have no clef, time signature or barline")
    stems_by_x, evs = [], []
    beams = [(f(r, "x"), f(r, "x") + f(r, "width"), f(r, "y"), f(r, "height")) for r in root.iter(NS + "rect") if r.get("class") == "beam"]
    for g in root.iter(NS + "g"):
        if g.get("class") != "ev":
            continue
        head = next((t for t in g.iter(NS + "text") if t.get("class") == "head"), None)
        rest = next((t for t in g.iter(NS + "text") if t.get("class") == "rest"), None)
        stems = [l for l in g.iter(NS + "line") if l.get("class") == "stem"]
        if rest is not None:
            if head is not None or stems or cp_of(rest) != G_QREST or abs(f(rest, "y") - y0) > 0.02:
                errs.append(f"{label}: rest is not a quarter rest on the line")
            evs.append({"kind": "r", "x": f(rest, "x") + REST_W * S / 2, "dur": Fraction(1)})
            continue
        if head is None or len(stems) != 1:
            errs.append(f"{label}: note without exactly one head and one stem")
            continue
        gp = cp_of(head)
        if gp not in (G_HEAD, G_HALF) or abs(f(head, "y") - y0) > 0.02:
            errs.append(f"{label}: notehead glyph or position wrong")
            continue
        left = f(head, "x")
        sm = stems[0]
        sx, y1, y2, swd = f(sm, "x1"), f(sm, "y1"), f(sm, "y2"), f(sm, "stroke-width")
        if abs(sx - (left + hw - swd / 2)) > 0.03 * S or abs(y1 - (y0 - STEM_X * S)) > 0.03 * S or y2 >= y1:
            errs.append(f"{label}: stem is not on the RIGHT edge of its head going up")
        if y1 - y2 < 3.0 * S - 0.01:
            errs.append(f"{label}: stem shorter than 3 staff spaces")
        evs.append({"kind": "n", "x": left + hw / 2, "open": gp == G_HALF, "sx": sx, "swd": swd, "tip": y2})
    evs.sort(key=lambda e: e["x"])
    # beams: level by distance below the stem tip; each joins >= 2 stems from first stem's left edge to last stem's right edge
    for e in evs:
        e["lv"] = 0
    lvl_sets = {1: [], 2: []}
    for bx1, bx2, by, bh in beams:
        cov = [e for e in evs if e["kind"] == "n" and bx1 - 0.02 <= e["sx"] - e["swd"] / 2 and e["sx"] + e["swd"] / 2 <= bx2 + 0.02]
        if len(cov) < 2:
            errs.append(f"{label}: a beam joins fewer than two stems")
            continue
        top = min(e["tip"] for e in cov)
        lvl = 1 if abs(by - top) < 0.03 else 2 if abs(by - (top + 0.75 * S)) < 0.03 else 0
        if lvl == 0 or abs(bh - 0.5 * S) > 0.03:
            errs.append(f"{label}: beam at an unexpected height")
            continue
        if abs(bx1 - (cov[0]["sx"] - cov[0]["swd"] / 2)) > 0.03 or abs(bx2 - (cov[-1]["sx"] + cov[-1]["swd"] / 2)) > 0.03:
            errs.append(f"{label}: beam does not end exactly at its outer stems")
        if any(abs(e["tip"] - by) > 0.03 for e in cov) and lvl == 1:
            errs.append(f"{label}: a stem does not end at its beam")
        for e in cov:
            e["lv"] += 1
        lvl_sets[lvl].append(frozenset(id(e) for e in cov))
    for s2 in lvl_sets[2]:
        if not any(s2 <= s1 for s1 in lvl_sets[1]):
            errs.append(f"{label}: a second beam is not inside a first beam")
    for e in evs:
        if e["kind"] == "n":
            if e["open"]:
                e["dur"] = Fraction(2)
                if e["lv"]:
                    errs.append(f"{label}: half note with a beam")
            else:
                e["dur"] = {0: Fraction(1), 1: Fraction(1, 2), 2: Fraction(1, 4)}.get(e["lv"])
                if e["dur"] is None:
                    errs.append(f"{label}: more than two beams on a stem")
                    e["dur"] = Fraction(1)
            e["beam_ids"] = e["lv"]
    # time positions: each event's x must equal where its start time says it should be
    t = Fraction(0)
    for e in evs:
        e["t"] = t
        if abs(e["x"] - (xf + pos(t) * u)) > 0.3:
            errs.append(f"{label}: an event is not where its time position puts it")
        t += e["dur"]
    if t != expect_beats:
        errs.append(f"{label}: bar adds up to {t} beats, expected {expect_beats}")
    if len(evs) > 1 and min(b["x"] - a["x"] for a, b in zip(evs, evs[1:])) < hw + 1.0:
        errs.append(f"{label}: neighbouring noteheads crowd or overlap")
    # syllables, beat by beat
    syls, b, i = [], 0, 0
    while b < int(expect_beats) and i < len(evs):
        e = evs[i]
        if e["t"] != b:
            errs.append(f"{label}: an event starts off the beat or a beat is empty ({e['t']} vs {b})")
            return None
        if e["kind"] == "n" and e["dur"] == 2:
            if b % 2:
                errs.append(f"{label}: half note starts on beat {b + 1}")
            syls.append(HALF_SYL)
            i += 1
            b += 2
            continue
        grp = []
        while i < len(evs) and evs[i]["t"] < b + 1:
            grp.append((evs[i]["kind"], evs[i]["dur"]))
            i += 1
        s = BEAT_SYL.get(tuple(grp))
        if s is None:
            errs.append(f"{label}: beat {b + 1} holds a pattern with no syllable {grp}")
            return None
        syls.append(s)
        b += 1
    if i != len(evs):
        errs.append(f"{label}: events left over after the last beat")
    # a beam must not cross a beat: beamed events of one beam all lie within one beat
    for bx1, bx2, by, bh in beams:
        cov = [e for e in evs if e["kind"] == "n" and bx1 - 0.02 <= e["sx"] - e["swd"] / 2 and e["sx"] + e["swd"] / 2 <= bx2 + 0.02]
        if cov and len({int(e["t"]) for e in cov}) != 1:
            errs.append(f"{label}: a beam crosses a beat")
    # labels on the example staves
    cnt = [(f(t, "x"), (t.text or "").strip()) for t in root.iter(NS + "text") if t.get("class") == "cnt"]
    sy = [(f(t, "x"), (t.text or "").strip()) for t in root.iter(NS + "text") if t.get("class") == "syl"]
    if kind == "ex":
        if [c for _, c in cnt] != ["1", "2", "3", "4"] or any(abs(x - (xf + pos(k) * u)) > 0.3 for k, (x, _) in enumerate(cnt)):
            errs.append(f"{label}: counts 1 2 3 4 are not under the beats")
        if [s for _, s in sy] != syls:
            errs.append(f"{label}: printed syllables differ from the notation ({[s for _, s in sy]} vs {syls})")
        xs = [x for x, _ in sy]
        ws = [len(s_) * 0.56 * 7.2 for _, s_ in sy]
        if any((b2 - a2) < (w1 + w2) / 2 + 2 for a2, b2, w1, w2 in zip(xs, xs[1:], ws, ws[1:])):
            errs.append(f"{label}: syllable labels crowd each other")
    elif cnt or sy:
        errs.append(f"{label}: unexpected labels")
    check_extent(root, label, errs)
    return syls


def card_blocks(html):
    out = {}
    for m in re.finditer(r'<div class="card" data-game="(\d)" data-n="(\d+)">(.*?)<!--/card-->', html, re.S):
        out[(int(m.group(1)), int(m.group(2)))] = m.group(3)
    return out


def verify_html():
    errs = []
    html = open(os.path.join(BUILD, "resource.html")).read()
    # ---- every svg on every page
    svgs = SVG_RE.findall(html)
    n_ns = n_ic = 0
    for s in svgs:
        root = parse_svg(s)
        if root.get("class") == "ic":
            n_ic += 1
            check_extent(root, f"icon {root.get('data-n')}", errs)
            continue
        n_ns += 1
        kind = root.get("data-kind")
        if kind in ("card", "ex"):
            exp = Fraction(4)
        else:
            sid = root.get("data-id")
            row = next((r for r in SYM_ROWS if f"sym-{r[3]}" == sid), None)
            exp = Fraction(int(sum(token_beats(t) for t in row[0]))) if row else Fraction(1)
        read_rhythm(root, errs, exp)
    # ---- the games
    blocks = card_blocks(html)
    if set(blocks) != {(g, n) for g in (1, 2) for n in range(1, 25)}:
        errs.append(f"card blocks found: {len(blocks)}, expected 48 (two games of cards 1-24)")
        return errs
    deck = {}
    for g in (1, 2):
        gm = GAMES[g]
        read = {}
        prompts = {}
        marks = {}
        for n in range(1, 25):
            b = blocks[(g, n)]
            sv = SVG_RE.findall(b)
            roots = [parse_svg(x) for x in sv if x.startswith('<svg class="ns"')]
            if len(roots) != 1:
                errs.append(f"game {g} card {n}: {len(roots)} notation staves")
                continue
            e2 = []
            syls = read_rhythm(roots[0], e2, Fraction(4))
            errs += e2
            if syls is None:
                continue
            read[n] = " ".join(syls)
            if read[n] != syl(gm["cards"][n]):
                errs.append(f"game {g} card {n}: notation says '{read[n]}' but the card data says '{syl(gm['cards'][n])}'")
            if roots[0].get("data-id") != f"L{g}-{n:02d}":
                errs.append(f"game {g} card {n}: staff id mismatch")
            if not re.search(rf'<span class="cn">{n}</span>', b):
                errs.append(f"game {g} card {n}: printed number missing")
            if f"Level {g}</span>" not in b:
                errs.append(f"game {g} card {n}: level label missing")
            toks = re.findall(r'<span class="tk">([^<]+)</span>', b.split('class="wh"')[1])
            prompts[n] = " ".join(toks)
            if "Who has" not in b or not b.split('class="wh"')[1].rstrip().rstrip("</div>").rstrip().endswith("?"):
                errs.append(f"game {g} card {n}: prompt does not read 'Who has ...?'")
            marks[n] = re.findall(r'data-mk="(\w+)"', b)
        if len(read) != 24:
            continue
        # distinct, level content
        if len(set(read.values())) != 24:
            errs.append(f"game {g}: the 24 I have rhythms are not all distinct")
        for n, s in read.items():
            toks = s.split()
            if g == 1 and set(toks) & SIXTEENTH_TOKENS:
                errs.append(f"game 1 card {n}: sixteenth notes in Level 1")
            if g == 2 and not set(toks) & SIXTEENTH_TOKENS:
                errs.append(f"game 2 card {n}: Level 2 card without sixteenth notes")
        # each prompt names exactly one card
        by_syl = {}
        for n, s in read.items():
            by_syl.setdefault(s, []).append(n)
        ptr = {}
        for n, p in prompts.items():
            hits = by_syl.get(p, [])
            if len(hits) != 1:
                errs.append(f"game {g} card {n}: prompt '{p}' matches {len(hits)} cards")
                continue
            if hits[0] == n:
                errs.append(f"game {g} card {n}: prompt names its own rhythm")
            ptr[n] = hits[0]
        if len(ptr) != 24:
            continue
        if sorted(ptr.values()) != list(range(1, 25)):
            errs.append(f"game {g}: every card must be named by exactly one prompt")
        cur, seen = 1, []
        for step in range(24):
            seen.append(cur)
            cur = ptr[cur]
            if cur == 1 and step < 23:
                errs.append(f"game {g}: loop returns to card 1 after only {step + 1} steps")
                break
        else:
            if cur != 1 or sorted(seen) != list(range(1, 25)):
                errs.append(f"game {g}: following the prompts from card 1 is not one closed loop of 24")
        end = [n for n in ptr if ptr[n] == 1]
        if len(end) != 1:
            errs.append(f"game {g}: {len(end)} cards point back at card 1")
        for n in range(1, 25):
            want = ["start"] if n == 1 else ["end"] if end and n == end[0] else []
            if marks[n] != want:
                errs.append(f"game {g} card {n}: start/end markers {marks[n]}, expected {want}")
        if seen != gm["order"] or end != [gm["end"]]:
            errs.append(f"game {g}: loop read from the printed prompts differs from the key data")
        if sum(1 for k in range(1, 25) if ptr[k] == k + 1) > 2:
            errs.append(f"game {g}: the loop follows card-number order too often")
        deck[g] = (read, ptr, seen)
        # ---- teacher key page
        kp = [p for p in re.split(r'<section class="page', html) if f"data-game=\"{g}\"" in p and 'class="krow"' in p]
        if len(kp) != 1:
            errs.append(f"game {g}: key page not found")
            continue
        rows = re.findall(r'<tr class="krow" data-step="(\d+)" data-game="\d"><td class="c">\d+</td><td class="c kc">(\d+)</td><td class="c mkc">(\w*)</td><td class="ks">([^<]+)</td><td class="c kn">(\d+)</td></tr>', kp[0])
        if len(rows) != 24 or [int(r[0]) for r in rows] != list(range(1, 25)):
            errs.append(f"game {g} key: {len(rows)} rows")
            continue
        if [int(r[1]) for r in rows] != seen:
            errs.append(f"game {g} key: card order differs from the loop read from the cards")
        for r in rows:
            n, nx = int(r[1]), int(r[4])
            if r[3] != read[n] or ptr[n] != nx:
                errs.append(f"game {g} key step {r[0]}: row disagrees with card {n}")
        if [r[2] for r in rows if r[2]] != ["START", "END"] or rows[0][2] != "START" or rows[-1][2] != "END":
            errs.append(f"game {g} key: START/END marks wrong")
        m = re.search(r'data-loop="\d">Loop: ([^<]+)</div>', kp[0])
        if not m or [int(x) for x in m.group(1).split(" → ")] != seen + [1]:
            errs.append(f"game {g} key: loop line differs from the loop")
    if len(deck) == 2 and set(deck[1][0].values()) & set(deck[2][0].values()):
        errs.append("a rhythm appears in both games")
    # ---- symbol and example counts
    if n_ns != 48 + len(SYM_ROWS) + len(EXAMPLES):
        errs.append(f"rhythm staves: {n_ns}, expected {48 + len(SYM_ROWS) + len(EXAMPLES)}")
    if n_ic != 48:
        errs.append(f"corner icons: {n_ic}, expected 48")
    # the symbol table: syllables re-read from the notation equal the printed 'Say' words, example bars sum
    for toks, name, beats, say, lvl in SYM_ROWS:
        r = [parse_svg(s) for s in svgs if f'data-id="sym-{say}"' in s]
        got = read_rhythm(r[0], [], Fraction(int(sum(token_beats(t) for t in toks)))) if r else None
        if got != [say]:
            errs.append(f"syllable guide row '{name}': notation reads {got}, printed '{say}'")
        if say not in html:
            errs.append(f"syllable guide row '{name}' missing")
    # theory statements on the pages
    text = " ".join(re.sub(r"<[^>]+>", " ", html).split())
    for need in ("a quarter note gets one beat", "each is half a beat", "each is a quarter of a beat", "hold your hands together for two beats",
                 "Sixteenth notes have two beams", "four quarter-note beats in each bar", "neutral clef"):
        if need not in text:
            errs.append(f"missing theory sentence: {need}")
    return errs


def pdf_fonts(path):
    out = subprocess.run(["pdffonts", path], capture_output=True, text=True, check=True).stdout.splitlines()[2:]
    return [(p.split()[0], p.split()[-5]) for p in out]


def load_json(name):
    return json.load(open(os.path.join(TPT, name)))


LAYOUT_JS = r"""
const { chromium } = require('playwright');
const url = require('url');
const fs = require('fs');
(async () => {
  const b = await chromium.launch();
  const out = [];
  const shotDir = process.argv[2];
  fs.mkdirSync(shotDir, { recursive: true });
  let shotN = 0;
  for (const f of process.argv.slice(3)) {
    const p = await b.newPage({ viewport: { width: 816, height: 1056 }, deviceScaleFactor: 4 });
    await p.goto(url.pathToFileURL(f).href, { waitUntil: 'load' });
    await p.evaluate(() => document.fonts.ready);
    const r = await p.evaluate(() => {
      const res = [];
      document.querySelectorAll('.page').forEach((pg, i) => {
        const pr = pg.getBoundingClientRect();
        const ft = pg.querySelector('.foot');
        const ftop = ft ? ft.getBoundingClientRect().top : pr.bottom;
        if (pg.scrollHeight > pg.clientHeight + 1) res.push(`page ${i + 1}: content overflows the page`);
        const boxes = [];
        pg.querySelectorAll('svg.ns, .card, .box, .step, .doc table, .doc p, .doc ul, .top, .cinstr, .exbox, .loop').forEach(el => {
          if (ft && ft.contains(el)) return;
          const r = el.getBoundingClientRect();
          if (r.height === 0) return;
          if (r.bottom > ftop - 6) res.push(`page ${i + 1}: ${el.tagName}.${el.getAttribute('class')} bottom ${(r.bottom - ftop).toFixed(1)}px vs footer rule (needs <= -6)`);
          if (r.right > pr.right - 0.35 * 96 + 0.5 || r.left < pr.left + 0.35 * 96 - 0.5) res.push(`page ${i + 1}: element ${el.tagName}.${el.getAttribute('class')} too close to the page edge`);
          if (el.matches('.card, .box, .step')) boxes.push([el, r]);
        });
        for (let a = 0; a < boxes.length; a++) for (let c = a + 1; c < boxes.length; c++) {
          const A = boxes[a][1], C = boxes[c][1];
          if (boxes[a][0].contains(boxes[c][0]) || boxes[c][0].contains(boxes[a][0])) continue;
          const gx = Math.max(A.left, C.left) - Math.min(A.right, C.right);
          const gy = Math.max(A.top, C.top) - Math.min(A.bottom, C.bottom);
          if (gx < 8 && gy < 8) res.push(`page ${i + 1}: two boxes lack a gutter`);
        }
        // cards: everything inside a card keeps padding from the dashed cut line
        pg.querySelectorAll('.card').forEach(cd => {
          const box = cd.getBoundingClientRect();
          if (cd.scrollHeight > cd.clientHeight + 1 || cd.scrollWidth > cd.clientWidth + 1) res.push(`page ${i + 1}: card ${cd.dataset.n} content overflows its card`);
          cd.querySelectorAll('svg, .cn, .mk, .wh, .lab, .lvt').forEach(ch => {
            const s = ch.getBoundingClientRect();
            if (s.left < box.left + 6 || s.right > box.right - 6 || s.top < box.top + 4 || s.bottom > box.bottom - 3) res.push(`page ${i + 1}: card ${cd.dataset.n} ${ch.tagName}.${ch.getAttribute('class')} too close to the cut line`);
          });
          const kids = [...cd.querySelectorAll('.ch, .lab, svg.ns, .wh')].map(e => e.getBoundingClientRect());
          for (let a = 0; a < kids.length - 1; a++) if (kids[a].bottom > kids[a + 1].top + 0.5) res.push(`page ${i + 1}: card ${cd.dataset.n} parts overlap`);
        });
        pg.querySelectorAll('.box svg, .exbox svg, .syt svg').forEach(sv => {
          const box = sv.closest('.box, .exbox, td').getBoundingClientRect();
          const s = sv.getBoundingClientRect();
          if (s.left < box.left + 4 || s.right > box.right - 4 || s.top < box.top + 2 || s.bottom > box.bottom - 2) res.push(`page ${i + 1}: a drawing is too close to its box edge`);
        });
        pg.querySelectorAll('.doc p, .doc li').forEach(el => {
          const range = document.createRange(); range.selectNodeContents(el);
          const rects = [...range.getClientRects()].filter(q => q.width > 1);
          const lines = {};
          rects.forEach(q => { const k = Math.round(q.top / 3); lines[k] = lines[k] ? [Math.min(lines[k][0], q.left), Math.max(lines[k][1], q.right)] : [q.left, q.right]; });
          const ks = Object.keys(lines).map(Number).sort((a, b) => a - b);
          if (ks.length >= 2) {
            const last = lines[ks[ks.length - 1]];
            const w = el.getBoundingClientRect().width;
            const txt = el.innerText.trim().split(/\s+/);
            if (last[1] - last[0] < 0.12 * w && txt.length > 6) res.push(`page ${i + 1}: short last line in "${el.innerText.trim().slice(0, 40)}..."`);
          }
        });
        let maxb = 0;
        pg.querySelectorAll('*').forEach(el => { if (ft && ft.contains(el)) return; if (el.closest('.wm')) return; const r = el.getBoundingClientRect(); if (r.height > 0 && r.width > 0 && el.children.length === 0) maxb = Math.max(maxb, r.bottom); });
        if (i > 0 && ftop - maxb > 90) res.push(`page ${i + 1}: blank band of ${(ftop - maxb).toFixed(0)}px above the footer`);
      });
      return res;
    });
    out.push(...r.map(x => f.split('/').pop() + ': ' + x));
    // rendered-pixel check input: screenshot every notation staff and corner icon on its own
    if (f.endsWith('resource.html')) {
      const handles = await p.$$('svg.ns, svg.ic');
      for (const h of handles) {
        const name = shotDir + '/s' + String(shotN++).padStart(4, '0') + '.png';
        await h.screenshot({ path: name });
      }
    }
    await p.close();
  }
  await b.close();
  console.log(JSON.stringify(out));
})().catch(e => { console.error(e); process.exit(1); });
"""


def verify_layout():
    js = os.path.join(BUILD, "layout.js")
    with open(js, "w") as fh:
        fh.write(LAYOUT_JS)
    files = [os.path.join(BUILD, "resource.html"), os.path.join(BUILD, "preview.html")]
    if not all(os.path.exists(x) for x in files):
        return ["build html missing: run gen.py first"]
    shots = os.path.join(BUILD, "svgshots")
    if os.path.isdir(shots):
        for x in os.listdir(shots):
            os.remove(os.path.join(shots, x))
    r = subprocess.run(["node", js, shots, *files], capture_output=True, text=True, env=node_env())
    if r.returncode != 0:
        return [f"layout script failed: {r.stderr[-300:]}"]
    errs = json.loads(r.stdout.strip().splitlines()[-1])
    # rendered-pixel check: the outer ring of every staff and icon screenshot must be clean white (nothing clipped by its svg box)
    from PIL import Image
    names = sorted(os.listdir(shots))
    want = 48 + len(SYM_ROWS) + len(EXAMPLES) + 48
    if len(names) != want:
        errs.append(f"svg screenshots: {len(names)}, expected {want}")
    for nme in names:
        im = Image.open(os.path.join(shots, nme)).convert("L")
        px = im.load()
        w, h = im.size
        ring = 4          # device pixels (1 CSS px at 4x)
        bad = any(px[x, y] < 235 for x in range(w) for y in list(range(0, ring)) + list(range(h - ring, h))) or \
            any(px[x, y] < 235 for y in range(h) for x in list(range(0, ring)) + list(range(w - ring, w)))
        if bad:
            errs.append(f"rendered pixels: ink touches the edge of {nme}")
    return errs


def verify_images():
    errs = []
    from PIL import Image
    h = Image.open(HERO)
    a = h.getchannel("A").point(lambda v: 255 if v > 24 else 0)
    bb = a.getbbox()
    if bb is None or bb[0] < 10 or bb[1] < 10 or h.width - bb[2] < 10 or h.height - bb[3] < 4:
        errs.append(f"hero art touches its image edge: {bb}")
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
        elif any(px[x, y] > 40 for x in list(range(0, 6)) + list(range(1994, 2000)) for y in range(ytop + 40, 2000)):
            errs.append(f"{name}: bottom band is not solid black to the edge")
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
    return errs


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
        if i + 1 != 1 and f"Page {i + 1}" not in t and f"Page {i + 1}".upper() not in t.upper():
            errs.append(f"PDF page {i + 1} does not print its own page number")
    for pg, name in PAGE_NAMES.items():
        if pg == P_COVER:
            continue
        if name.lower() not in texts[pg - 1].lower():
            errs.append(f"page {pg} does not show its name '{name}'")
    full_pages()
    for frm, to, text in XREFS:
        if text not in texts[frm - 1]:
            errs.append(f"page {frm}: cross-reference text '{text}' not found")
    # every "page N" / "pages N–M" mention names a real page and the thing it points at
    expect = {"syllables guide": [P_SYL], "teacher key": [P_K1, P_K2], "teacher keys": [P_K1, P_K2]}
    for i, t in enumerate(texts):
        for m in re.finditer(r"(?i)\bpages? (\d+)(?:–(\d+))?", t):
            a, b = int(m.group(1)), int(m.group(2) or m.group(1))
            if a < 1 or b > TOTAL_PAGES or b < a:
                errs.append(f"page {i + 1}: reference '{m.group(0)}' is outside the {TOTAL_PAGES}-page file")
        for m in re.finditer(r"(?i)(syllables guide) \(page (\d+)\)", t):
            if int(m.group(2)) != P_SYL:
                errs.append(f"page {i + 1}: '{m.group(0)[:50]}' points at the wrong page")
    teach, terms, how = texts[P_TEACH - 1], texts[P_TERMS - 1], texts[P_HOW - 1]
    for need in (f"pages {P_C1}–{P_C1 + 2}", f"pages {P_C2}–{P_C2 + 2}", f"page {P_K1}", f"page {P_K2}", f"page {P_HOW}", f"page {P_SYL}"):
        for nm, tx in (("teacher notes", teach), ("terms", terms)):
            if need not in tx and not (nm == "terms" and need in (f"page {P_HOW}",) and False):
                errs.append(f"{nm} page lacks the reference '{need}'")
    for need in (f"pages {P_C1}–{P_C1 + 2}", f"pages {P_C2}–{P_C2 + 2}", f"page {P_SYL}", f"page {P_K1}", f"page {P_K2}"):
        if need not in how:
            errs.append(f"how-to-play page lacks the reference '{need}'")
    # the numbered steps on the how-to page are 1..4 in order
    if not all(re.search(rf"(?<!\d){n}(?!\d)", how) for n in range(1, 5)):
        errs.append("how-to-play steps 1-4 not all present")
    prd = PdfReader(PREVIEW_PDF)
    for i in range(4):
        t = prd.pages[i].extract_text() or ""
        if t.count("PREVIEW") != 1:
            errs.append(f"preview PDF page {i + 1}: expected exactly one PREVIEW watermark")
        want = PAGE_NAMES[PREVIEW_PAGES[i]]
        if want.lower() not in t.lower():
            errs.append(f"preview PDF page {i + 1} is not '{want}'")
    errs += verify_images()
    up = open(UPLOAD).read()
    m = re.search(r"^## 1\. Title\s*\n+```\n(.+?)\n```", up, re.M | re.S)
    if not m:
        errs.append("UPLOAD.md: title block not found")
    else:
        title = m.group(1).strip()
        if len(title) > 80:
            errs.append(f"UPLOAD.md: title is {len(title)} chars")
        if re.search(r"winter|snow|holiday|christmas|december", title, re.I):
            errs.append("UPLOAD.md: seasonal word in the title")
    for need in (DISCLOSURE, f"${PRICE}", f"{TOTAL_PAGES} pages", "48 cards"):
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
    tags, subs = set(load_json("TAG-OPTIONS.json")["options"]), set(load_json("SUBJECT-OPTIONS.json"))
    if any(t not in tags for t in tj["tags"]) or any(s not in subs for s in tj["subjects"]):
        errs.append("tpt.json tags or subjects invalid")
    if tj.get("pages") != TOTAL_PAGES or tj["price"] != PRICE or not 1 <= len(tj["grades"]) <= 4:
        errs.append("tpt.json pages, price or grades mismatch")
    first = texts[0].lower()
    if f"{TOTAL_PAGES} pages" not in first or "48 cards" not in first:
        errs.append("cover text does not state the page and card counts")
    if DISCLOSURE not in terms:
        errs.append("terms page lacks the disclosure line")
    allt = " ".join(texts).lower()
    for bad in ("qa ", "checker", "recomputed", "verified by code"):
        if bad in allt.replace("answer keys are verified", ""):
            errs.append(f"buyer-facing text contains internal wording '{bad}'")
    for bad in ("colour", "favourite", "rhythmn"):
        if bad in allt:
            errs.append(f"non-US spelling '{bad}'")
    return errs


def check():
    errs = verify_html()
    errs += verify_layout()
    errs += verify_files()
    if errs:
        print("CHECK FAILED")
        print("\n".join(" - " + e for e in errs[:80]))
        sys.exit(1)
    print(f"CHECK OK: {48} cards and {len(SYM_ROWS) + len(EXAMPLES)} guide staves re-read from the rendered SVG (one-line staff, neutral clef, 4/4, stems up on the right of the heads, "
          f"beams single for eighths and double for sixteenths, quarter rests on the line); every bar adds to 4 beats and every note sits at its time position; "
          f"syllables recomputed from the notation match the card data and the printed Who has prompts; each prompt names exactly one card; both games are one closed loop of 24 "
          f"(card 1 back to card 1 after 24 steps); all rhythms distinct; keys, START/END markers and loop lines agree; no ink on svg edges; layout clear; "
          f"PDF {TOTAL_PAGES} Letter pages, preview 4 (one watermark each); images 2000x2000 with clean edges; cross-references, UPLOAD.md and tpt.json ok.")


if __name__ == "__main__":
    if "--check" in sys.argv:
        check()
    else:
        build()
