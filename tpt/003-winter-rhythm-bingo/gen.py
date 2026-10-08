#!/usr/bin/env python3
"""Winter Rhythm Bingo (TpT 003): build the resource and verify it.

    python3 gen.py           build everything (PDFs, PNGs, tpt.json) into this folder
    python3 gen.py --check   verify rhythms, cards, calling cards, pages, fonts and files

36 four-beat rhythm patterns (rhythm.py tokens: quarter, eighth pair, quarter
rest, half, dotted half, sixteenth groups, dotted quarter + eighth) are dealt
onto 30 unique 5x5 cards with a free centre. Every card holds 24 of the 36
patterns and every pattern sits on exactly 20 cards. Card dealing follows
bundles/010-woodland-christmas-bingo/cards.py: shuffled rounds, each round's
groups being what a card leaves out, with a fixed seed so builds repeat.

Rendering uses Playwright + Chromium (HTML/SVG -> PDF/PNG) through the shared
../tools/render.js, with the OFL fonts in ../fonts embedded as subsets.
"""
import itertools
import json
import os
import random
import re
import subprocess
import sys
from fractions import Fraction
from html import escape

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import rhythm as R  # noqa: E402
from art import art  # noqa: E402

TPT = os.path.dirname(HERE)
FONTS = os.path.join(TPT, "fonts")
BUILD = os.path.join(HERE, "build")
RENDER_JS = os.path.join(TPT, "tools", "render.js")

SLUG = "winter-rhythm-bingo"
PDF = os.path.join(HERE, f"{SLUG}.pdf")
PREVIEW_PDF = os.path.join(HERE, f"{SLUG}-PREVIEW.pdf")
COVER_PNG = os.path.join(HERE, "cover.png")
PREVIEW_PNGS = [os.path.join(HERE, f"preview-{i}.png") for i in (1, 2, 3)]
UPLOAD = os.path.join(HERE, "UPLOAD.md")
TPT_JSON = os.path.join(HERE, "tpt.json")

STORE = "Brian Lotze"      # copyright holder
BRAND = "Hudson Beat"      # store line on covers and previews (owner, 4 Oct)
YEAR = 2026
ACCENT = "#2B7BB9"         # this product's single accent (icy winter blue)
TITLE = "Winter Rhythm Bingo"
PRICE = "5.00"

# 36 calling patterns in three groups. Numbers on the calling cards are 1-36 in this order.
GROUPS = [
    ("Quarters, eighths, rests & half notes", "qeqq eeqr qqh hee eqre rqeq qrqe eeee heq hqr qeer erqq".split()),
    ("Sixteenth-note groups", "sqeq qsqr ssh hss esrq qqes aqaq bqbq abh hqa eaqr qbsr".split()),
    ("Dotted rhythms", "dqq dee qqd dd dh hd tq tr dsq erd dbq qad".split()),
]
POOL = [p for _, ps in GROUPS for p in ps]
GROUP_SHORT = ["Basics", "Sixteenths", "Dotted rhythms"]
N_PAT, N_CARDS, PER_CARD = len(POOL), 30, 24
SEED = 2027                # first seed whose deal passes every check (found by `deal_ok`)
ART = ["snowflake", "mitten", "sled", "hat", "mug", "skate"]


# ---------------------------------------------------------------- dealing (after 010's cards.py)
def deal(seed):
    """30 cards of 24 pattern indices + None (FREE) at index 12. 10 rounds; each round shuffles the
    36 patterns into 3 groups of 12, and card g of the round leaves out group g, so every pattern
    is on exactly 20 cards."""
    rnd = random.Random(seed)
    cards = []
    groups = N_PAT // (N_PAT - PER_CARD)
    while len(cards) < N_CARDS:
        pool = list(range(N_PAT))
        rnd.shuffle(pool)
        for g in range(groups):
            omit = set(pool[g * (N_PAT - PER_CARD):(g + 1) * (N_PAT - PER_CARD)])
            keep = [i for i in range(N_PAT) if i not in omit]
            rnd.shuffle(keep)
            cards.append(keep[:12] + [None] + keep[12:])
    return cards[:N_CARDS]


def lines(grid):
    rows = [grid[r * 5:(r + 1) * 5] for r in range(5)]
    cols = [grid[c::5] for c in range(5)]
    diags = [[grid[i * 6] for i in range(5)], [grid[4 + i * 4] for i in range(5)]]
    return [frozenset(x for x in ln if x is not None) for ln in rows + cols + diags]


def card_errors(cards):
    errs = []
    if len(cards) != N_CARDS:
        errs.append(f"{len(cards)} cards, expected {N_CARDS}")
    sets = [frozenset(x for x in c if x is not None) for c in cards]
    for i, (c, s) in enumerate(zip(cards, sets)):
        if len(c) != 25 or c[12] is not None or len(s) != PER_CARD or None in c[:12] + c[13:]:
            errs.append(f"card {i + 1}: not 24 distinct patterns around a FREE centre")
    if len(set(sets)) != len(cards):
        errs.append("two cards hold the same set of patterns")
    if len({tuple(c) for c in cards}) != len(cards):
        errs.append("two cards have the same layout")
    seen = {}
    for i, c in enumerate(cards):
        for ln in lines(c):
            if ln in seen and seen[ln] != i:
                errs.append(f"cards {seen[ln] + 1} and {i + 1} share a winning line")
            seen[ln] = i
    use = [sum(p in s for s in sets) for p in range(N_PAT)]
    if set(use) != {N_CARDS * PER_CARD // N_PAT}:
        errs.append(f"patterns are not used evenly: {use}")
    return errs


def deal_ok(start=SEED):
    seed = start
    while card_errors(deal(seed)):
        seed += 1
    return seed


CARDS = deal(SEED)


# ---------------------------------------------------------------- html scaffolding (from 002)
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
@page land { size: 11in 8.5in; margin: 0; }
.page.land { page: land; width: 11in; height: 8.5in; }
.top .art { align-self: center; }
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
/* text pages */
.doc h1 { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 30pt; margin: 0 0 4pt; line-height: 1; }
.doc h2 { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 14pt; margin: 11pt 0 4pt; letter-spacing: .02em; }
.doc h2 .acc { color: ACCENT; }
.doc p, .doc li { font-size: 10.6pt; line-height: 1.34; margin: 0 0 4pt; }
.doc ul, .doc ol { margin: 0 0 4pt; padding-left: 15pt; }
.doc .rule { border-bottom: 2.2pt solid #000; margin-bottom: 6pt; padding-bottom: 6pt; }
.doc table { border-collapse: collapse; width: 100%; font-size: 10.5pt; margin: 2pt 0 4pt; }
.doc td, .doc th { border: 1pt solid #000; padding: 3pt 6pt; text-align: left; vertical-align: middle; }
.doc th { font-family: 'Oswald'; font-weight: 500; text-transform: uppercase; font-size: 10pt; background: #000; color: #fff; }
.cols { display: flex; gap: 22pt; }
.cols > div { flex: 1; }
.small { font-size: 9pt !important; color: #333; }
.ref td { text-align: center; padding: 1.5pt 6pt; }
.ref td.n { text-align: left; }
.ref .big { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 12pt; }
.cnt { font-family: 'Source Sans 3'; font-weight: 600; white-space: pre; }
/* cover page (letter) */
.cover { align-items: center; justify-content: space-between; padding: 0.55in 0.6in 0.5in; }
.store { font-family: 'Oswald'; font-weight: 500; font-size: 13pt; letter-spacing: .32em; text-transform: uppercase; }
.ctitle { text-align: center; }
.ctitle .a { font-family: 'Oswald'; font-weight: 700; font-size: 44pt; line-height: 1; letter-spacing: .02em; }
.ctitle .b { font-family: 'Oswald'; font-weight: 700; font-size: 92pt; line-height: .95; letter-spacing: .01em; }
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
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{family}" font-weight="{weight}" font-size="{size}" '
            f'text-anchor="{anchor}" fill="{fill}" {extra}>{t}</text>')


def pill(x, y, label, size=11, fill="#000", anchor="start"):
    w = len(label) * size * 0.56 + 14
    x0 = x if anchor == "start" else x - w
    return (f'<rect x="{x0:.1f}" y="{y:.1f}" width="{w:.1f}" height="{size + 9:.1f}" rx="4" fill="{fill}"/>'
            + text(x0 + w / 2, y + size + 3.2, label, size, 500, extra='letter-spacing="0.06em"', fill="#fff", upper=True))


def nb(t):
    """Keep the spacing of counts and syllables inside SVG text (spaces would collapse)."""
    return t.replace(" ", "\u00a0")


def centred(p, cx, yl, s, fill="#000", bar=False):
    """A pattern centred on cx: notes only (bar=False) or a full 4/4 measure (bar=True)."""
    w = (R.measure_width(p) if bar else R.width(p)) * s
    x0 = cx - w / 2
    body, end = (R.measure(p, x0, yl, s, fill) if bar else R.pattern(p, x0, yl, s, fill=fill))
    return body, x0, end


MAX_W = max(R.width(p) for p in POOL)
MAX_MW = max(R.measure_width(p) for p in POOL)


# ---------------------------------------------------------------- bingo cards
# Cards are landscape (11 x 8.5 in) so the notation can be printed large for grade 3 (QA round 1).
GRID_W, CELL_W, CELL_H, HEAD_H = 720, 144, 82, 32
SQ_S = round(min(6.4, (CELL_W - 18) / MAX_W), 2)   # one staff-space size for every square
MIN_SQ_S = 6.0                                     # QA: at least ~6 pt staff space for grade 3


def free_square(x, y, w, h):
    k = h / 104
    return (art("snowflake", x + w / 2 - 30 * k, y + 8 * k, 60 * k, 2.2 * k, fill=ACCENT, line=ACCENT)
            + text(x + w / 2, y + h - 14 * k, "FREE", 20 * k, 700, extra='letter-spacing="0.12em"'))


def card_grid(card, w=CELL_W, h=CELL_H, head=HEAD_H, s=SQ_S, sw=1.8, letters=True):
    out = []
    y0 = 0
    if letters:
        for c, L in enumerate("BINGO"):
            out.append(f'<rect x="{c * w + 3}" y="2" width="{w - 6}" height="{head - 6}" rx="6" fill="#000"/>')
            out.append(text(c * w + w / 2, head * 0.73, L, head * 0.66, 700, fill="#fff"))
        y0 = head
    for i, pid in enumerate(card):
        r, c = divmod(i, 5)
        x, y = c * w, y0 + r * h
        if pid is None:
            out.append(free_square(x, y, w, h))
            continue
        yl = y + h / 2 + 1.1 * s
        body, _, _ = centred(POOL[pid], x + w / 2, yl, s)
        out.append(body)
    # grid lines on top
    H = 5 * h
    out.append(f'<rect x="{sw / 2}" y="{y0 + sw / 2}" width="{5 * w - sw}" height="{H - sw}" fill="none" stroke="#000" stroke-width="{sw * 1.4}"/>')
    for k in range(1, 5):
        out.append(f'<line x1="{k * w}" y1="{y0}" x2="{k * w}" y2="{y0 + H}" stroke="#000" stroke-width="{sw}"/>')
        out.append(f'<line x1="0" y1="{y0 + k * h}" x2="{5 * w}" y2="{y0 + k * h}" stroke="#000" stroke-width="{sw}"/>')
    return "".join(out), y0 + H


def card_page(n, page_no, watermark=False):
    grid, H = card_grid(CARDS[n - 1])
    body = svg(GRID_W, int(H + 2), grid)
    icons = svg(250, 36, "".join(art(a, 4 + i * 42, 2, 32, 1.4) for i, a in enumerate(ART)), "display:block")
    hdr = top("Listen, find the rhythm, cover the square", f"CARD {n}", f"Card {n} of {N_CARDS}")
    hdr = hdr.replace('<div class="tag">', f'<div class="art">{icons}</div><div class="tag">', 1)
    return (f'<section class="page land">{wm(watermark)}{hdr}'
            f'{NAME}<div class="body">{body}</div>{foot(f"Page {page_no}")}</section>')


# ---------------------------------------------------------------- calling cards
CARD_AREA = (540, 612)
CALL_COLS, CALL_ROWS = 3, 4
CALLS_PER_PAGE = CALL_COLS * CALL_ROWS
CALL_W, CALL_H = CARD_AREA[0] / CALL_COLS, CARD_AREA[1] / CALL_ROWS
CALL_S = round((CALL_W - 30) / MAX_MW, 2)


def cut_grid(cols, rows, w, h):
    W, H = CARD_AREA
    out = [f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" fill="none" stroke="#666" stroke-width="0.8" stroke-dasharray="6 4"/>']
    for c in range(1, cols):
        out.append(f'<line x1="{c * w}" y1="0" x2="{c * w}" y2="{H}" stroke="#666" stroke-width="0.8" stroke-dasharray="6 4"/>')
    for r in range(1, rows):
        out.append(f'<line x1="0" y1="{r * h}" x2="{W}" y2="{r * h}" stroke="#666" stroke-width="0.8" stroke-dasharray="6 4"/>')
    return "".join(out)


def group_of(pid):
    return next(i for i, (_, ps) in enumerate(GROUPS) if POOL[pid] in ps)


def calling_card(pid, x, y, w, h):
    p = POOL[pid]
    out = [f'<rect x="{x + 7}" y="{y + 7}" width="{w - 14}" height="{h - 14}" rx="12" fill="#fff" stroke="#000" stroke-width="1.8"/>']
    out.append(pill(x + 17, y + 17, f"#{pid + 1}", 12))
    out.append(art(ART[pid % len(ART)], x + w - 47, y + 14, 30, 1.3))
    out.append(text(x + 17, y + 54, GROUP_SHORT[group_of(pid)], 9, 300, anchor="start"))
    yl = y + 88
    body, _, end = centred(p, x + w / 2, yl, CALL_S, bar=True)
    out.append(body)
    out.append(text(x + w / 2, y + h - 30, nb(R.counts(p)), 11.5, 600, "Source Sans 3"))
    out.append(text(x + w / 2, y + h - 16, nb(R.syllables(p)), 8.5, 400, "Source Sans 3", fill="#444"))
    return "".join(out)


def calls_page(k, page_no, watermark=False):
    ids = list(range(N_PAT))[k * CALLS_PER_PAGE:(k + 1) * CALLS_PER_PAGE]
    body = cut_grid(CALL_COLS, CALL_ROWS, CALL_W, CALL_H)
    for i, pid in enumerate(ids):
        body += calling_card(pid, (i % CALL_COLS) * CALL_W, (i // CALL_COLS) * CALL_H, CALL_W, CALL_H)
    npages = -(-N_PAT // CALLS_PER_PAGE)
    return (f'<section class="page">{wm(watermark)}{top(f"Calling cards #{ids[0] + 1}–#{ids[-1] + 1}", "CALLER", f"Page {k + 1} of {npages}")}'
            f'<div class="how" style="margin-top:7pt">Print on cardstock and cut on the dashed lines. '
            f'<span class="small">Held or silent beats are in (parentheses); syllables are optional.</span></div>'
            f'<div class="body">{svg(*CARD_AREA, body)}</div>{foot(f"Page {page_no}")}</section>')


# ---------------------------------------------------------------- caller's checklist
def checklist_page(page_no, watermark=False):
    rows_per_col = N_PAT // 2
    rh = 33.5
    s = 3.9
    out = []
    for pid, p in enumerate(POOL):
        col, r = divmod(pid, rows_per_col)
        x, y = col * 276, r * rh
        if r % 2 == 0:
            out.append(f'<rect x="{x}" y="{y}" width="264" height="{rh}" fill="#f1f1f1"/>')
        out.append(f'<rect x="{x + 6}" y="{y + 9}" width="15" height="15" rx="2" fill="#fff" stroke="#000" stroke-width="1.2"/>')
        out.append(text(x + 44, y + 22, f"#{pid + 1}", 12, 700))
        body, _, _ = centred(p, x + 116, y + rh / 2 + 1.6 * s + 3, s)
        out.append(body)
        out.append(text(x + 166, y + 21, nb(R.counts(p)), 8.6, 600, "Source Sans 3", anchor="start"))
    body = svg(540, int(rows_per_col * rh + 2), "".join(out))
    legend = " · ".join(f"<b>#{1 + 12 * g}–#{12 + 12 * g}</b> {escape(name.lower())}" for g, (name, _) in enumerate(GROUPS))
    return (f'<section class="page">{wm(watermark)}{top("Caller’s checklist · tick each pattern as you call it", "CALLER", "Keep this page")}'
            f'<div class="how" style="margin-top:8pt">Shuffle the calling cards and call them in any order. Tick each one here, '
            f'then use this list to check a winner’s card. <span class="small">{legend}.</span></div>'
            f'<div class="body">{body}</div>{foot(f"Page {page_no}")}</section>')


# ---------------------------------------------------------------- markers
def markers_page(page_no, watermark=False):
    out = []
    cols, rows, w, h = 6, 8, 90, 73
    for i in range(cols * rows):
        r, c = divmod(i, cols)
        cx, cy = c * w + w / 2, r * h + h / 2
        out.append(f'<circle cx="{cx}" cy="{cy}" r="33" fill="none" stroke="#666" stroke-width="0.9" stroke-dasharray="5 3.5"/>')
        name = "snowflake" if (r + c) % 2 == 0 else ART[1 + (i // 2) % (len(ART) - 1)]
        out.append(art(name, cx - 22, cy - 22, 44, 1.4))
    body = svg(cols * w, rows * h, "".join(out))
    return (f'<section class="page">{wm(watermark)}{top("Bingo markers · optional", "MARKERS", "48 per page")}'
            f'<div class="how" style="margin-top:8pt">Print on cardstock and cut out, or use counters, buttons or erasable markers on laminated cards. '
            f'Students can color the markers while they wait for the game to start.</div>'
            f'<div class="body">{body}</div>{foot(f"Page {page_no}")}</section>')


# ---------------------------------------------------------------- plan and page index
def plan():
    p = [("cover",), ("teacher",), ("howto",), ("reference",), ("checklist",)]
    p += [("card", n) for n in range(1, N_CARDS + 1)]
    p += [("calls", k) for k in range(-(-N_PAT // CALLS_PER_PAGE))]
    p += [("markers",), ("terms",)]
    return p


def page_index():
    return {(item if len(item) > 1 else item[0]): i + 1 for i, item in enumerate(plan())}


def ranges():
    ix = page_index()
    nc = -(-N_PAT // CALLS_PER_PAGE)
    return {"cards": f'{ix[("card", 1)]}–{ix[("card", N_CARDS)]}', "calls": f'{ix[("calls", 0)]}–{ix[("calls", nc - 1)]}',
            "howto": ix["howto"], "reference": ix["reference"], "checklist": ix["checklist"], "markers": ix["markers"],
            "terms": ix["terms"], "total": len(plan())}


# ---------------------------------------------------------------- teacher pages
def teacher_page():
    rg = ranges()
    rows = [("How to play", rg["howto"], "rules, calling options, game variations"),
            ("Rhythm reference", rg["reference"], "all 9 rhythm values with counts"),
            ("Caller’s checklist", rg["checklist"], "all 36 patterns, tick as you call"),
            ("Bingo cards (30)", rg["cards"], "1 per page, every card different"),
            ("Calling cards (36)", rg["calls"], "12 per page, counts on each"),
            ("Markers", rg["markers"], "48 snowflake and winter markers"),
            ("Terms of use", rg["terms"], "license and credits")]
    trs = "".join(f"<tr><td><b>{a}</b></td><td style='white-space:nowrap'>{b}</td><td>{c}</td></tr>" for a, b, c in rows)
    return (f'<section class="page doc"><div class="rule"><h1>Teacher Notes</h1>'
            f'<div class="l" style="font-size:13pt">{TITLE} · grades 3–6 · {N_CARDS} unique cards · {N_PAT} rhythm patterns</div></div>'
            f'<div class="cols"><div>'
            f'<h2>What it is</h2>'
            f'<p>A listening and reading game. You perform a 4-beat rhythm; students find it on their card and cover it. '
            f'Each square is one 4/4 measure written in standard notation on a one-line rhythm staff.</p>'
            f'<h2>Getting ready</h2><ul>'
            f'<li>Print the {N_CARDS} bingo cards (pages {rg["cards"]}) single-sided; they are landscape pages with large notation. Card stock and lamination make them last for years.</li>'
            f'<li>Print the calling cards (pages {rg["calls"]}) on card stock and cut them apart, or keep the caller’s checklist (page {rg["checklist"]}) in your hand and call from it.</li>'
            f'<li>Markers: page {rg["markers"]}, counters, or dry-erase markers on laminated cards.</li>'
            f'<li>Review the rhythm reference (page {rg["reference"]}) first, especially sixteenth notes and dotted rhythms.</li></ul>'
            f'<h2>Fair, unique cards</h2>'
            f'<p>Every card holds 24 of the 36 patterns around a FREE centre, and each pattern appears on exactly 20 cards. '
            f'No two cards are the same, and no two cards share a winning row, column or diagonal, so two students can’t win on the very same line.</p>'
            f'<h2>Pattern groups</h2><ul>'
            + "".join(f"<li><b>#{1 + 12 * g}–#{12 + 12 * g}</b> {escape(name.lower())}</li>" for g, (name, _) in enumerate(GROUPS))
            + f'</ul><p class="small">Every card mixes all three groups, so teach all 9 rhythm values before playing.</p>'
            f'</div><div>'
            f'<h2>What’s inside</h2><table><tr><th>Part</th><th>Pages</th><th>Contents</th></tr>{trs}</table>'
            f'<h2>Counting &amp; syllables</h2>'
            f'<p>Calling cards print counts (1 e &amp; a) with held or silent beats in parentheses, plus Kodály-style syllables in small print '
            f'(ta, ti-ti, ti-ka-ti-ka, ti-tika, tika-ti, tam-ti, ta-a). Many teachers use Takadimi, Gordon or other systems instead; '
            f'say whatever your students know.</p>'
            f'<h2>Music notes</h2><p class="small">Every pattern is exactly 4 beats in 4/4 time. Stems go up on the one-line staff. '
            f'Sixteenth groups and eighth pairs are beamed by the beat. Half notes and dotted quarters start on beat 1 or 3, '
            f'and the dotted half starts on beat 1, so beat 3 is always easy to see.</p>'
            f'<h2>Standards</h2><p>Supports reading and performing rhythm patterns in standard notation '
            f'(National Core Arts Standards, Music, MU:Pr4.2, grades 3–6) and listening skills.</p>'
            f'<p class="small">Winter theme with snowflakes, mittens, sleds, hats, cocoa and skates: no holiday or religious images, '
            f'so it works from December through February. No songs, lyrics or copyrighted characters are used. All art is original.</p>'
            f'</div></div><div style="flex:1"></div>' + foot('Page ' + str(page_index()['teacher'])) + '</section>')


def howto_page():
    rg = ranges()
    return (f'<section class="page doc"><div class="rule"><h1>How to Play</h1>'
            f'<div class="l" style="font-size:13pt">Call by sound, never by number</div></div>'
            f'<div class="cols"><div>'
            f'<h2>The basic game</h2><ol>'
            f'<li>Give each student a card and markers. Everyone covers the <b>FREE</b> snowflake.</li>'
            f'<li>Shuffle the calling cards. Draw one and set a steady beat: “1, 2, ready, go.”</li>'
            f'<li><b>Perform</b> the rhythm. Keep the number to yourself so students have to read and listen.</li>'
            f'<li>Students who find the pattern cover it. Tick it on the caller’s checklist and set the card aside.</li>'
            f'<li>Five in a row (across, down or diagonal) wins. The winner claps or chants their line back to you, '
            f'and you check it against the checklist.</li></ol>'
            f'<h2>Ways to call</h2><ul>'
            f'<li><b>Clap</b> or tap it on a drum.</li>'
            f'<li><b>Play</b> it on one pitch on a recorder, keyboard, xylophone or Boomwhacker.</li>'
            f'<li><b>Speak</b> it with counts or rhythm syllables (easier).</li>'
            f'<li><b>Echo first:</b> you perform, the class echoes, then everyone looks.</li>'
            f'<li><b>Student caller:</b> a student draws and performs the card.</li></ul>'
            f'</div><div>'
            f'<h2>Game variations</h2><ul>'
            f'<li><b>Four corners</b>: cover all four corner squares.</li>'
            f'<li><b>X marks the spot</b>: both diagonals.</li>'
            f'<li><b>Snowflake frame</b>: every square around the edge.</li>'
            f'<li><b>Two lines</b> for a longer game, or <b>blackout</b> for a whole lesson.</li>'
            f'<li><b>Mystery count</b>: say only the counts (“1 e &amp; a, 2, 3 &amp;, 4”) and students find the notation.</li>'
            f'<li><b>Compose</b>: students choose a square, write the counts under it, and perform it for a partner.</li></ul>'
            f'<h2>Tips</h2><ul>'
            f'<li>Perform each rhythm twice at a moderate tempo with a steady beat underneath (pat or metronome).</li>'
            f'<li>Patterns #1–#12 use the simplest values. To warm up, call a few of those first and then shuffle the rest in.</li>'
            f'<li>Several patterns differ by only one beat (for example #6 and #13, or #31 and #32). That is on purpose: it trains careful listening.</li>'
            f'<li>Collect cards in number order so the class set stays together.</li></ul>'
            f'</div></div><div style="flex:1"></div>'
            f'<div style="display:flex;justify-content:center;margin-bottom:10pt">{svg(540, 56, "".join(art(a, 30 + i * 88, 4, 48, 1.5) for i, a in enumerate(ART)))}</div>'
            + foot('Page ' + str(rg['howto'])) + '</section>')


REF_ORDER = ["q", "e", "r", "h", "t", "s", "a", "b", "d"]


def reference_page(watermark=False):
    rows = []
    for t in REF_ORDER:
        info = R.TOKENS[t]
        s = 5.5
        w = (R.INK_W[t] + 2 * R.PAD) * s
        body, _ = R.pattern(t, 4, 28, s, line=True, extend=0.3)
        std = svg(int(w + 10), 37, body, 'display:block;margin:0 auto')
        b = info["beats"]
        rows.append(f'<tr><td>{std}</td><td class="n"><span class="big">{info["name"]}</span></td>'
                    f'<td><b>{b} beat{"s" if b != 1 else ""}</b></td><td class="cnt">{escape(R.counts(t))}</td><td>{info["kodaly"]}</td></tr>')
    s = 7
    ex = "sqd"
    body, _, end = centred(ex, 220, 46, s, bar=True)
    exsvg = svg(440, 66, body)
    return (f'<section class="page doc">{wm(watermark)}<div class="rule"><h1>Rhythm Reference</h1>'
            f'<div class="l" style="font-size:13pt">The 9 rhythm values in this game · display it or keep it on desks</div></div>'
            f'<table class="ref"><tr><th>Notation</th><th>Name</th><th>Beats</th><th>Counts (starting on beat 1)</th><th>Syllables<br>(optional)</th></tr>'
            f'{"".join(rows)}</table>'
            f'<h2>Reading a pattern <span class="acc">·</span> every square is one 4-beat measure</h2>'
            f'<div style="display:flex;justify-content:center;margin:2pt 0">{exsvg}</div>'
            f'<p style="text-align:center"><span class="cnt" style="font-size:14pt">{escape(R.counts(ex))}</span></p>'
            f'<p class="small" style="text-align:center">Four sixteenths (1 beat) + a quarter note (1 beat) + a dotted quarter and an eighth (2 beats) = 4 beats.</p>'
            f'<ul><li>Count with the beat number, then <b>e &amp; a</b> for sixteenths and <b>&amp;</b> for eighths.</li>'
            f'<li>Numbers in (parentheses) are beats you <b>hold</b> or <b>rest</b>: keep counting in your head.</li>'
            f'<li>A <b>dot</b> adds half the note’s value: a dotted half is 2 + 1 = 3 beats; a dotted quarter is 1 + ½ = 1½ beats.</li>'
            f'<li>One beam means eighth notes; two beams mean sixteenth notes.</li></ul>'
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
            f'<li>Art, cards, layouts and rhythm patterns: original work, {BRAND} by {STORE}.</li>'
            f'<li>Music notation font: Bravura © Steinberg Media Technologies GmbH, SIL Open Font License 1.1.</li>'
            f'<li>Text fonts: Oswald (The Oswald Project Authors) and Source Sans 3 (Adobe), SIL Open Font License 1.1.</li></ul>'
            f'<p class="small">Designed with the help of digital and AI tools, and checked by hand.</p>'
            f'<div style="flex:1"></div>{foot(f"Page {page_no}")}</section>')


# ---------------------------------------------------------------- cover art
def hero_svg(width_css):
    """Cover art: a tilted bingo card with markers, winter art around it; accent and black only."""
    A = ACCENT
    w, h, head = 52, 50, 22
    grid, H = card_grid(CARDS[0], w, h, head, s=2.35, sw=1.4)
    marks = "".join(f'<rect x="{c * w + 1.5}" y="{head + r * h + 1.5}" width="{w - 3}" height="{h - 3}" fill="#fff"/>'
                    f'<circle cx="{c * w + w / 2}" cy="{head + r * h + h / 2}" r="19" fill="{A}" stroke="#000" stroke-width="1.4"/>'
                    + art("snowflake", c * w + w / 2 - 13, head + r * h + h / 2 - 13, 26, 1.1, fill="#fff", line="#fff")
                    for r, c in ((0, 0), (1, 1), (3, 3), (4, 4)))
    card = (f'<g transform="translate(168 22) rotate(-4 130 140)"><rect x="-10" y="-10" width="{5 * w + 20}" height="{H + 20}" rx="12" '
            f'fill="#fff" stroke="#000" stroke-width="3"/>{grid}{marks}</g>')
    deco = (art("snowflake", 18, 14, 92, 2.6, fill=A, line=A, rotate=10) + art("mitten", 40, 150, 104, 2.6, fill=A, rotate=-14)
            + art("snowflake", 492, 10, 70, 2.4, rotate=-8) + art("sled", 456, 210, 136, 2.6, fill=A)
            + art("hat", 476, 92, 96, 2.4, fill="#fff", rotate=12) + art("snowflake", 120, 280, 54, 2.0, fill=A, line=A)
            + art("mug", 16, 262, 84, 2.2))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 360" width="{width_css}" style="display:block">'
            f'{card}{deco}</svg>')


def cover_page():
    rg = ranges()
    return (f'<section class="page cover"><div class="store">{BRAND}</div>'
            f'<div style="width:6.9in">{hero_svg("100%")}</div>'
            f'<div class="ctitle"><div class="a">WINTER RHYTHM</div><div class="b">BINGO</div>'
            f'<div class="c">30 unique cards · rhythm calling cards · sixteenths &amp; dotted rhythms</div></div>'
            f'<div class="cband">Grades 3–6 <em>·</em> 30 cards <em>·</em> 36 patterns <em>·</em> {rg["total"]} pages</div></section>')


# ---------------------------------------------------------------- assemble
def render_page(item, watermark=False):
    ix = page_index()
    k = item[0]
    if k == "cover":
        return cover_page()
    if k == "teacher":
        return teacher_page()
    if k == "howto":
        return howto_page()
    if k == "reference":
        return reference_page(watermark)
    if k == "checklist":
        return checklist_page(ix["checklist"], watermark)
    if k == "card":
        return card_page(item[1], ix[item], watermark)
    if k == "calls":
        return calls_page(item[1], ix[item], watermark)
    if k == "markers":
        return markers_page(ix["markers"], watermark)
    if k == "terms":
        return terms_page(ix["terms"])
    raise KeyError(k)


PREVIEW_PICKS = [("card", 1), ("calls", 1), ("reference",), ("checklist",)]


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
            f'html,body{{margin:0;background:#fff}}{SQ_CSS}</style></head><body>{body}</body></html>')


def cover_square():
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div>'
        f'<div style="width:840px;margin-top:14px">{hero_svg("100%")}</div>'
        f'<div class="hd" style="font-size:66px;margin-top:8px">Winter Rhythm</div>'
        f'<div class="hd" style="font-size:132px">Bingo</div>'
        f'<div class="sub" style="font-size:29px;margin-top:10px">30 unique cards · calling cards · sixteenths &amp; dotted rhythms</div>'
        f'<div class="band">Grades 3–6 <em>·</em> 30 cards <em>·</em> 36 rhythm patterns</div></div>')


def preview_square_1(img):
    items = [(img[0], "Bingo cards", "30, all different"), (img[1], "Calling cards", "counts on every card"),
             (img[2], "Rhythm reference", "9 rhythm values")]
    # these shots come from the preview PDF, which already carries the PREVIEW watermark
    shots = "".join(
        f'<div style="width:{wd}px"><div class="shot"><img src="{src}"></div>'
        f'<div class="lbl">{a}<span>{b}</span></div></div>' for (src, a, b), wd in zip(items, (410, 245, 245)))
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div>'
        f'<div class="hd" style="font-size:76px;margin-top:20px">Ready to play</div>'
        f'<div class="sub" style="font-size:27px;margin-top:8px">Cards, calling cards, checklist, markers and teacher notes</div>'
        f'<div style="display:flex;gap:22px;margin-top:90px;align-items:flex-start">{shots}</div>'
        f'<div class="band">Print <em>·</em> cut <em>·</em> clap a rhythm <em>·</em> play</div></div>')


def preview_square_2(a, b):
    # both shots come from the unwatermarked resource PDF, so each gets exactly one overlay watermark
    pair = "".join(
        f'<div style="position:absolute;left:{x}px;top:{y}px;width:600px"><div class="shot"><img src="{src}">'
        f'<div class="swm" style="font-size:110px">PREVIEW</div></div>'
        f'<div class="lbl" style="position:absolute;{side}:-2px;top:-44px;margin:0">{lab}</div></div>'
        for src, lab, x, y, side in ((a, "Card 1", 40, 250, "left"), (b, "Card 2", 360, 420, "right")))
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div>'
        f'<div class="hd" style="font-size:72px;margin-top:20px">30 unique cards</div>'
        f'<div class="sub" style="font-size:27px;margin-top:8px">No two cards alike, and no two share a winning line</div>'
        f'{pair}'
        f'<div class="band">Every pattern exactly 4 beats in 4/4</div></div>')


def preview_square_3():
    cells = []
    s = 6.3
    for pid, p in enumerate(POOL):
        body, _, end = centred(p, 75, 66, s)
        assert end < 146, f"preview-3 pattern {pid + 1} crowds its box"
        cells.append(f'<div style="width:150px"><svg viewBox="0 0 150 96" width="150" style="display:block">'
                     f'<rect x="1.5" y="1.5" width="147" height="93" rx="8" fill="#fff" stroke="#000" stroke-width="2"/>'
                     f'{text(10, 20, str(pid + 1), 13, 700, anchor="start")}{body}</svg></div>')
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div>'
        f'<div class="hd" style="font-size:70px;margin-top:16px">36 rhythm patterns</div>'
        f'<div class="sub" style="font-size:27px;margin-top:8px">Quarters, eighths, rests, half notes, sixteenths and dotted rhythms</div>'
        f'<div style="position:relative;display:flex;flex-wrap:wrap;gap:14px 12px;width:960px;margin-top:30px;justify-content:center">{"".join(cells)}'
        f'<div class="swm" style="font-size:150px">PREVIEW</div></div>'
        f'<div class="band">#1–12 basics <em>·</em> #13–24 sixteenths <em>·</em> #25–36 dotted</div></div>')


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
        "grades": ["3rd-grade", "4th-grade", "5th-grade", "6th-grade"],
        "subjects": ["Music"],
        "tags": ["Winter"],
        "formats": ["PDF"],
        "pages": pages,
        "files": {"product": f"{SLUG}.pdf", "preview": f"{SLUG}-PREVIEW.pdf", "thumb1": "cover.png",
                  "thumb2": "preview-1.png", "thumb3": "preview-2.png", "thumb4": "preview-3.png"},
    }


def pdf_png(src, page, out):
    subprocess.run(["pdftoppm", "-png", "-r", "110", "-f", str(page), "-l", str(page), "-singlefile", src,
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
    for i in range(1, 5):
        pdf_png(PREVIEW_PDF, i, f"pv{i}")
    pdf_png(PDF, page_index()[("card", 1)], "card1")
    pdf_png(PDF, page_index()[("card", 2)], "card2")
    sq = [write("cover.html", cover_square()), write("p1.html", preview_square_1(["pv1.png", "pv2.png", "pv3.png"])),
          write("p2.html", preview_square_2("card1.png", "card2.png")), write("p3.html", preview_square_3())]
    render([{"html": h, "png": o, "width": 1000, "height": 1000, "scale": 2} for h, o in zip(sq, [COVER_PNG] + PREVIEW_PNGS)])
    with open(TPT_JSON, "w") as f:
        json.dump(tpt_json(len(plan())), f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"built {PDF} ({len(plan())} pages), {PREVIEW_PDF}, cover + 3 previews, tpt.json")


# ---------------------------------------------------------------- checks
def verify_data():
    errs = []
    # token facts, checked against an independent hand-written table: (beats, number of sounds)
    want = {"q": (1, 1), "e": (1, 2), "r": (1, 0), "h": (2, 1), "t": (3, 1), "s": (1, 4), "a": (1, 3), "b": (1, 3), "d": (2, 2)}
    if set(want) != set(R.TOKENS):
        errs.append("token table differs from the expected 9 rhythm values")
    for t, (b, n) in want.items():
        info = R.TOKENS[t]
        if info["beats"] != b or sum(abs(x) for x in info["dur"]) != b or sum(1 for x in info["dur"] if x > 0) != n:
            errs.append(f"token {t}: beats/durations/sounds disagree")
        sounding = [c for c in info["count"] if not c.startswith("(")]
        if len(sounding) != n:
            errs.append(f"token {t}: counting syllables don't match its {n} sounds")
    for i, p in enumerate(POOL, 1):
        total = sum((abs(x) for t in p for x in R.TOKENS[t]["dur"]), Fraction(0))
        if total != 4 or R.beats(p) != 4:
            errs.append(f"pattern #{i} {p}: {total} beats, not 4")
        for t, on in zip(p, R.onsets(p)):
            if t in "hd" and on not in (0, 2):
                errs.append(f"pattern #{i} {p}: {R.TOKENS[t]['name']} starts on beat {on + 1} (hides beat 3)")
            if t == "t" and on != 0:
                errs.append(f"pattern #{i} {p}: dotted half must start on beat 1")
        if sum(t in R.SIXTEENTHS for t in p) > 2:
            errs.append(f"pattern #{i} {p}: more than two sixteenth groups")
    if len(set(POOL)) != len(POOL):
        errs.append("duplicate patterns in the calling pool")
    if [len(ps) for _, ps in GROUPS] != [12, 12, 12]:
        errs.append("groups must be 12 + 12 + 12")
    if any(not set(p) <= set("qerh") for p in GROUPS[0][1]):
        errs.append("group 1 uses values beyond quarter/eighth/rest/half")
    if any(not set(p) & R.SIXTEENTHS for p in GROUPS[1][1]):
        errs.append("every group 2 pattern needs a sixteenth group")
    if any(not set(p) & set("dt") for p in GROUPS[2][1]):
        errs.append("every group 3 pattern needs a dotted rhythm")
    # cards
    errs += card_errors(CARDS)
    called = set(range(N_PAT))                     # one calling card is drawn for every pool index
    drawn = {pid for k in range(-(-N_PAT // CALLS_PER_PAGE)) for pid in range(N_PAT)[k * CALLS_PER_PAGE:(k + 1) * CALLS_PER_PAGE]}
    on_cards = {x for c in CARDS for x in c if x is not None}
    if drawn != called:
        errs.append("calling-card pages don't cover every pattern")
    if not on_cards <= drawn:
        errs.append(f"patterns on cards without a calling card: {sorted(on_cards - drawn)}")
    if on_cards != drawn:
        errs.append(f"calling cards for patterns on no bingo card: {sorted(drawn - on_cards)}")
    # layout fits and is big enough for grade 3 (QA round 1)
    if SQ_S < MIN_SQ_S:
        errs.append(f"bingo-square staff space {SQ_S}pt is below {MIN_SQ_S}pt")
    if R.BEAM_GAP * SQ_S < 1.6:
        errs.append("gap between sixteenth beams on the cards is under 1.6pt")
    if R.width(max(POOL, key=R.width)) * SQ_S > CELL_W - 12:
        errs.append("widest pattern overflows a bingo square")
    if R.measure_width(max(POOL, key=R.measure_width)) * CALL_S > CALL_W - 24:
        errs.append("widest measure overflows a calling card")
    for name, cp in {"noteQuarterUp": 0xE1D5, "noteHalfUp": 0xE1D3, "restQuarter": 0xE4E5, "noteheadBlack": 0xE0A4,
                     "note8thUp": 0xE1D7, "augmentationDot": 0xE1E7, "timeSig4": 0xE084}.items():
        if R.GLYPH[name][0] != cp:
            errs.append(f"{name} codepoint wrong")
    return errs


def pdf_fonts(path):
    out = subprocess.run(["pdffonts", path], capture_output=True, text=True, check=True).stdout.splitlines()[2:]
    return [(ln.split()[0], ln.split()[-5]) for ln in out]


def footer_errors(path, safe=0.35 * 72):
    """Every page after the cover must show its footer inside the page, clear of the 0.35 in safe zone."""
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
        for i, (pg, item) in enumerate(zip(rd.pages, items)):
            w, h = float(pg.mediabox.width), float(pg.mediabox.height)
            want = (792, 612) if item[0] == "card" else (612, 792)   # bingo cards are landscape Letter
            if abs(w - want[0]) > 1 or abs(h - want[1]) > 1:
                errs.append(f"{os.path.basename(path)} p{i + 1}: {w:.0f}x{h:.0f}pt, expected {want[0]}x{want[1]} (US Letter)")
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
    ix = page_index()
    for i, t in enumerate(txt):
        if i > 0 and "Brian Lotze · Hudson Beat" not in t:
            errs.append(f"page {i + 1}: footer missing")
    for n in range(1, N_CARDS + 1):
        t = txt[ix[("card", n)] - 1]
        if f"Card {n} of {N_CARDS}" not in t or "FREE" not in t.replace(" ", ""):
            errs.append(f"card {n}: page {ix[('card', n)]} lacks its card label or FREE square")
    calls_txt = " ".join(txt[ix[("calls", k)] - 1] for k in range(-(-N_PAT // CALLS_PER_PAGE)))
    found = {int(m) for m in re.findall(r"#(\d+)", calls_txt)}
    if not set(range(1, N_PAT + 1)) <= found:
        errs.append(f"calling-card pages missing #{sorted(set(range(1, N_PAT + 1)) - found)}")
    ptxt = [PdfReader(PREVIEW_PDF).pages[i].extract_text() for i in range(len(PREVIEW_PICKS))]
    if sum("PREVIEW" in t for t in ptxt) != len(PREVIEW_PICKS):
        errs.append("preview PDF: watermark missing on some pages")
    for p in [COVER_PNG, *PREVIEW_PNGS]:
        if Image.open(p).size != (2000, 2000):
            errs.append(f"{os.path.basename(p)}: not 2000x2000")
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
    for word in ("christmas", "hanukkah", "santa", "nativity", "kwanzaa"):
        if word in " ".join(txt).lower():
            errs.append(f"resource text mentions '{word}' (must be non-denominational)")
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
    sets = [frozenset(x for x in c if x is not None) for c in CARDS]
    overlap = max(len(a & b) for a, b in itertools.combinations(sets, 2))
    print(f"CHECK OK: {N_PAT} patterns, each exactly 4 beats (two independent tables); {N_CARDS} cards unique "
          f"(sets, layouts, no shared winning line; max overlap {overlap}/24; each pattern on {N_CARDS * PER_CARD // N_PAT} cards); "
          f"every card pattern has a calling card (#1–#{N_PAT} found in the PDF); "
          f"PDF {len(plan())} Letter pages with footers, preview {len(PREVIEW_PICKS)} watermarked pages, fonts embedded; "
          f"images 2000x2000; tpt.json and UPLOAD.md ok.")


if __name__ == "__main__":
    if "--find-seed" in sys.argv:
        print(deal_ok())
    elif "--check" in sys.argv:
        check()
    else:
        build()
