#!/usr/bin/env python3
"""Winter Color by Music Symbol (TpT 039): build the resource and verify it.

    python3 gen.py           build everything (PDFs, PNGs) into this folder
    python3 gen.py --check   verify data, answer keys, pages, fonts, files and image layout

Same structure as 035 (Hanukkah Color by Note). Worksheets and answer keys are rendered from
the same `Sheet` objects: each region stores the symbol printed in it, and the answer-key colour
is looked up from that printed symbol through the sheet's key. `--check` confirms that the
lookup lands on the colour the picture was designed with, for every region.

Level A: dynamics (pp p mp mf f ff). Level B: Italian tempo terms. Level C: notation symbols.
The key shows the meaning (A, B) or the name (C); the space shows the marking itself.

Rendering uses Playwright + Chromium (HTML/SVG -> PDF/PNG) with the OFL fonts in ../fonts.
"""
import json
import os
import random
import re
import subprocess
import sys
from dataclasses import dataclass, field
from html import escape

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from shapely.geometry import box as sbox  # noqa: E402
from shapely.ops import unary_union  # noqa: E402

import symbols as SY  # noqa: E402
from pictures import PICTURES, W, H  # noqa: E402
from regions import build_regions, place, n_symbols  # noqa: E402

TPT = os.path.dirname(HERE)
FONTS = os.path.join(TPT, "fonts")
BUILD = os.path.join(HERE, "build")
RENDER_JS = os.path.join(TPT, "tools", "render.js")

SLUG = "winter-color-by-music-symbol"
PDF = os.path.join(HERE, f"{SLUG}.pdf")
PREVIEW_PDF = os.path.join(HERE, f"{SLUG}-PREVIEW.pdf")
COVER_PNG = os.path.join(HERE, "cover.png")
PREVIEW_PNGS = [os.path.join(HERE, f"preview-{i}.png") for i in (1, 2, 3)]
UPLOAD = os.path.join(HERE, "UPLOAD.md")
TPTJSON = os.path.join(HERE, "tpt.json")

STORE = "Brian Lotze"      # copyright holder
BRAND = "Hudson Beat"      # store line on covers and previews
YEAR = 2026
ACCENT = "#1F6FA8"  # this product's single accent (icy winter blue)
N_PAGES = 3 + 54 + 1   # cover, teacher notes, reference, 27 worksheets + 27 keys, terms
PRICE = "4.00"
DISCLOSURE = "Created with the help of digital and AI tools. Notation and answer keys are verified before release."

COLORS = {  # crayon name -> answer-key fill
    "blue": "#A5D2F2", "white": "#FFFFFF", "gray": "#B8C0C9", "red": "#D6402F", "green": "#5DB04C",
    "purple": "#9467C9", "yellow": "#FFD94A", "brown": "#9A6434", "orange": "#F39234", "black": "#2E2E2E",
    # cover-only tints of the accent (the cover stays black + one accent, per STYLE.md)
    "accent": ACCENT, "accent_lt": "#A9CBE6", "accent_xlt": "#DCEAF5", "accent_dk": "#123F63",
}
LEVELS = {
    "A": {"name": "Dynamics", "grades": "2–3", "ids": list(SY.DYNAMICS),
          "how": "Read the dynamic marking in each space. Find what it means in the key, then color the space."},
    "B": {"name": "Tempo terms", "grades": "3–5", "ids": list(SY.TEMPO),
          "how": "Read the Italian tempo term in each space. Find what it means in the key, then color the space."},
    "C": {"name": "Music symbols", "grades": "4–5", "ids": list(SY.SYMBOLS),
          "how": "Name the music symbol in each space. Find its name in the key, then color the space."},
}
HELPER = {"A": "Dynamics tell us how loudly or softly to play. p = soft, f = loud, m = medium (mezzo).",
          "B": "Tempo terms tell us how fast or slow to play. They are Italian words.",
          "C": "Look closely at each symbol, and use the reference page if you need help."}

MARGIN = 2.0  # pt of white space kept around every symbol inside its region


def key_label(level, sid):
    """(main, sub) text the key shows for an id."""
    if level == "A":
        return SY.DYNAMICS[sid][2], ""
    if level == "B":
        return SY.TEMPO[sid][1], ""
    return SY.SYMBOLS[sid][0], SY.SYMBOLS[sid][1]


# ---------------------------------------------------------------- data
@dataclass
class Sheet:
    level: str
    slug: str
    title: str
    key: dict            # colour -> symbol id
    regions: list        # dicts: id, poly, color, symbols [(cx, cy, id)]
    ink: object
    number: int = 0
    key_page: int = 0
    page: int = 0
    extra: dict = field(default_factory=dict)

    def inverse(self):
        return {v: k for k, v in self.key.items()}

    def answer_color(self, region):
        """Colour for the answer key, derived from the symbols printed on the worksheet."""
        inv = self.inverse()
        cols = {inv[sym] for _, _, sym in region["symbols"]}
        assert len(cols) == 1, f"region {region['id']} has symbols of different colours"
        return cols.pop()


def box_for(level):
    w, h = SY.box(level)
    return w + 2 * MARGIN, h + 2 * MARGIN


_GEOM = {}


def picture_regions(slug, fn):
    if slug not in _GEOM:
        layers, ink = fn()
        _GEOM[slug] = build_regions(layers, ink)
    return _GEOM[slug]


def make_sheets():
    sheets = []
    for level in LEVELS:
        bw, bh = box_for(level)
        for i, (slug, title, fn) in enumerate(PICTURES):
            regions, ink = picture_regions(slug, fn)
            colours = sorted({r["color"] for r in regions}, key=list(COLORS).index)
            rng = random.Random(f"{level}-{slug}-v1")
            pool = list(LEVELS[level]["ids"])
            rng.shuffle(pool)
            key = dict(zip(colours, pool[:len(colours)]))
            counts = {}
            regs = []
            for r in regions:
                taken = unary_union([sbox(cx - bw / 2, cy - bh / 2, cx + bw / 2, cy + bh / 2) for rr in regs for cx, cy, _ in rr["symbols"]] or [sbox(-9, -9, -8, -8)])
                pts = place(r["poly"], unary_union([ink, taken]), bw, bh, n_symbols(r["poly"]))
                symbols = [(cx, cy, key[r["color"]]) for cx, cy in pts]
                regs.append({"id": r["id"], "poly": r["poly"], "color": r["color"], "symbols": symbols})
            sheets.append(Sheet(level, slug, title, key, regs, ink, number=i + 1))
    return sheets


# ---------------------------------------------------------------- svg
def poly_path(p):
    def ring(c):
        return "M" + "L".join(f"{x:.1f},{y:.1f}" for x, y in c.coords) + "Z"
    return ring(p.exterior) + "".join(ring(i) for i in p.interiors)


def geom_path(g):
    if g.is_empty:
        return ""
    return "".join(poly_path(p) for p in (g.geoms if hasattr(g, "geoms") else [g]))


def symbol_svg(level, sym, cx, cy):
    return SY.symbol_svg(level, sym, cx, cy)


def picture_svg(sheet, answer=False, fills=None, show_symbols=None, width="100%", stroke=1.6, frame=True):
    """fills: optional {region_id: colour name} override (cover art)."""
    show_symbols = (not answer) if show_symbols is None else show_symbols
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-2 -2 {W + 4} {H + 4}" width="{width}" style="display:block">']
    for r in sheet.regions:
        if fills is not None:
            col = COLORS[fills[r["id"]]] if r["id"] in fills else "#fff"
        else:
            col = COLORS[sheet.answer_color(r)] if answer else "#fff"
        out.append(f'<path d="{poly_path(r["poly"])}" fill="{col}" fill-rule="evenodd" stroke="#000" stroke-width="{stroke}" stroke-linejoin="round"/>')
    out.append(f'<path d="{geom_path(sheet.ink)}" fill="#000" fill-rule="evenodd"/>')
    if show_symbols:
        for r in sheet.regions:
            if fills is not None and r["id"] in fills:
                continue
            for cx, cy, sym in r["symbols"]:
                out.append(symbol_svg(sheet.level, sym, cx, cy))
    if frame:
        out.append(f'<rect x="0" y="0" width="{W}" height="{H}" rx="28" ry="28" fill="none" stroke="#000" stroke-width="{stroke * 1.4}"/>')
    out.append("</svg>")
    return "".join(out)


def key_html(sheet):
    cells = []
    for colour, sym in sheet.key.items():
        main, sub = key_label(sheet.level, sym)
        subh = f'<div class="ksub">{escape(sub)}</div>' if sub else ""
        cells.append(f'<div class="kcell"><div class="ksym"><div class="kmain">{escape(main)}</div>{subh}</div>'
                     f'<div class="keq">=</div><div class="kcol"><span class="sw" style="background:{COLORS[colour]}"></span>'
                     f'<span class="cname">{colour}</span></div></div>')
    return f'<div class="key">{"".join(cells)}</div>'


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
.how { font-size: 11.5pt; margin: 2pt 0 7pt; }
.how b { font-weight: 700; }
.key { display: flex; gap: 6pt; justify-content: center; margin-bottom: 4pt; }
.kcell { flex: 1; border: 1.3pt solid #000; border-radius: 6pt; display: flex; align-items: center; justify-content: center; gap: 5pt; padding: 3pt 5pt; min-height: 56pt; }
.ksym { display: flex; flex-direction: column; align-items: center; }
.kmain { font-family: 'Oswald'; font-weight: 500; font-size: 12.5pt; line-height: 1.05; text-align: center; text-transform: uppercase; letter-spacing: .02em; }
.ksub { font-size: 7.5pt; line-height: 1.05; margin-top: 2pt; text-align: center; max-width: 62pt; }
.keq { font-family: 'Oswald'; font-weight: 300; font-size: 16pt; }
.kcol { display: flex; flex-direction: column; align-items: center; gap: 2pt; }
.sw { display: inline-block; width: 20pt; height: 20pt; border-radius: 50%; border: 1.2pt solid #000; }
.cname { font-family: 'Oswald'; font-weight: 500; font-size: 10pt; text-transform: uppercase; letter-spacing: .03em; }
.helper { text-align: center; font-size: 9.5pt; margin: 1pt 0 5pt; font-style: italic; }
.pic { margin-top: 4pt; flex: 1; display: flex; align-items: flex-start; justify-content: center; }
.pic svg { width: 7.5in; }
.foot { display: flex; justify-content: space-between; font-size: 8.5pt; color: #333; border-top: .8pt solid #000; padding-top: 3pt; }
.wm { position: absolute; left: 50%; top: 50%; transform: translate(-50%, -50%) rotate(-38deg); font-family: 'Oswald'; font-weight: 700;
      font-size: 150pt; color: rgba(0,0,0,.13); letter-spacing: .06em; white-space: nowrap; pointer-events: none; z-index: 9; }
/* text pages */
.doc h1 { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 30pt; margin: 0 0 4pt; line-height: 1; }
.doc h2 { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 14pt; margin: 14pt 0 4pt; letter-spacing: .02em; }
.doc h2 .acc { color: ACCENT; }
.doc p, .doc li { font-size: 11pt; line-height: 1.38; margin: 0 0 5pt; }
.doc ul { margin: 0 0 4pt; padding-left: 16pt; }
.doc .rule { border-bottom: 2.2pt solid #000; margin-bottom: 8pt; padding-bottom: 6pt; }
.doc table { border-collapse: collapse; width: 100%; font-size: 10.5pt; margin: 2pt 0 4pt; }
.doc td, .doc th { border: 1pt solid #000; padding: 4pt 6pt; text-align: left; vertical-align: top; }
.doc th { font-family: 'Oswald'; font-weight: 500; text-transform: uppercase; font-size: 10pt; background: #000; color: #fff; }
.cols { display: flex; gap: 22pt; }
.cols > div { flex: 1; }
.small { font-size: 9pt !important; color: #333; }
.refrow { display: flex; justify-content: space-between; gap: 8pt; margin: 4pt 0 6pt; }
.refcell { flex: 1; border: 1.3pt solid #000; border-radius: 6pt; text-align: center; padding: 6pt 2pt 5pt; }
.refcell b { display: block; font-family: 'Oswald'; font-weight: 500; text-transform: uppercase; font-size: 10pt; }
.refcell span { font-size: 9.5pt; }
.rt { margin: 2pt 0 4pt !important; }
.rt td { padding: 3pt 5pt !important; vertical-align: middle !important; font-size: 10pt; }
/* cover page (letter) */
.cover { align-items: center; justify-content: space-between; padding: 0.55in 0.6in 0.5in; }
.store { font-family: 'Oswald'; font-weight: 500; font-size: 13pt; letter-spacing: .32em; text-transform: uppercase; }
.ctitle { text-align: center; }
.ctitle .a { font-family: 'Oswald'; font-weight: 700; font-size: 44pt; line-height: 1; letter-spacing: .02em; }
.ctitle .b { font-family: 'Oswald'; font-weight: 700; font-size: 74pt; line-height: .95; letter-spacing: .01em; }
.ctitle .c { font-family: 'Oswald'; font-weight: 300; font-size: 17pt; margin-top: 8pt; }
.cband { width: 100%; background: #000; color: #fff; text-align: center; font-family: 'Oswald'; font-weight: 500; font-size: 14pt;
         letter-spacing: .08em; text-transform: uppercase; padding: 8pt 0 9pt; border-radius: 4pt; }
.cband em { font-style: normal; color: ACCENT; }
""".replace("ACCENT", ACCENT)


def html_doc(pages, title="doc"):
    return (f'<!doctype html><html><head><meta charset="utf-8"><title>{escape(title)}</title>'
            f'<style>{font_css()}{CSS}</style></head><body>{"".join(pages)}</body></html>')


def foot(left, right):
    return f'<div class="foot"><span>{left}</span><span>{right}</span></div>'


COPY = f"© {YEAR} {STORE} · {BRAND} · For single-classroom use"
TITLE = "Winter Color by Music Symbol"


def worksheet_page(sh, watermark=False):
    lv = LEVELS[sh.level]
    wm = '<div class="wm">PREVIEW</div>' if watermark else ""
    return (f'<section class="page">{wm}'
            f'<div class="top"><div class="h t">{TITLE}<small>{sh.number}. {escape(sh.title)}</small></div>'
            f'<div class="tag"><div class="lv">LEVEL {sh.level}</div><div class="ln">{lv["name"]}</div></div></div>'
            f'<div class="name">Name<span></span>Date<span class="d"></span></div>'
            f'<div class="how"><b>How to play:</b> {lv["how"]}</div>'
            f'{key_html(sh)}<div class="helper">{HELPER[sh.level]}</div>'
            f'<div class="pic">{picture_svg(sh)}</div>'
            f'{foot(COPY, f"Level {sh.level} · Answer key on page {sh.key_page} · Page {sh.page}")}</section>')


def answer_page(sh, watermark=False):
    lv = LEVELS[sh.level]
    wm = '<div class="wm">PREVIEW</div>' if watermark else ""
    return (f'<section class="page">{wm}'
            f'<div class="top"><div class="h t">Answer Key<small>{sh.number}. {escape(sh.title)} — Level {sh.level}, {lv["name"].lower()}</small></div>'
            f'<div class="tag"><div class="lv ak">ANSWER KEY</div><div class="ln">Level {sh.level} · {lv["name"]}</div></div></div>'
            f'<div class="how" style="margin-top:9pt">Every space is colored from the marking printed in it on the worksheet (page {sh.page}).</div>'
            f'{key_html(sh)}<div class="helper">&nbsp;</div>'
            f'<div class="pic">{picture_svg(sh, answer=True)}</div>'
            f'{foot(COPY, f"Level {sh.level} answer key · Page {sh.key_page}")}</section>')


def cover_art(sheet):
    """The snowman's hat and scarf filled in the accent and its tints (one-accent rule); the rest
    stays line art with its markings, so the cover still shows the activity."""
    tone = {"purple": "accent_dk", "red": "accent"}
    return {r["id"]: tone[r["color"]] for r in sheet.regions if r["color"] in tone}


def cover_sheet(sheets):
    return next(s for s in sheets if s.level == "A" and s.slug == "snowman")


def cover_page(sheets):
    s = cover_sheet(sheets)
    return (f'<section class="page cover"><div class="store">{BRAND}</div>'
            f'<div style="width:5.6in">{picture_svg(s, fills=cover_art(s), stroke=2.2)}</div>'
            f'<div class="ctitle"><div class="a">WINTER COLOR BY</div><div class="b">MUSIC SYMBOL</div>'
            f'<div class="c">Dynamics · Tempo terms · Music symbols — 3 levels with answer keys</div></div>'
            f'<div class="cband">Grades 2–5 <em>·</em> 27 worksheets <em>·</em> 27 answer keys</div></section>')


def teacher_page(sheets, toc):
    rows = "".join(f'<tr><td style="white-space:nowrap"><b>Level {k}</b></td><td>{v["name"]}</td><td style="white-space:nowrap">Grades {v["grades"]}</td><td>{toc[k]}</td></tr>' for k, v in LEVELS.items())
    pics = ", ".join(f"{i + 1}. {t}" for i, (_, t, _) in enumerate(PICTURES))
    return (f'<section class="page doc"><div class="rule"><h1>Teacher Notes</h1>'
            f'<div class="l" style="font-size:13pt">{TITLE} · 3 levels · grades 2–5</div></div>'
            f'<div class="cols"><div>'
            f'<h2>How to use</h2><ul>'
            f'<li>Pick a level for each student or group, print the worksheets single-sided, and hand out crayons or colored pencils.</li>'
            f'<li>Students read the marking in each space, find what it means in the color key, and color the space. Every space has a marking in it.</li>'
            f'<li><b>White</b> in a key means leave the space white. <b>Gray</b> can be a gray crayon or a light pencil shade.</li>'
            f'<li>Check with the answer key that follows each level. Keys are full-color pages you can print or project.</li>'
            f'<li>All three levels use the same nine winter pictures, so one class can color the same picture at three different reading levels.</li></ul>'
            f'<h2>Great for</h2><ul><li>Early finishers and music centers</li><li>Sub plans (the answer keys and reference page make it no-prep)</li>'
            f'<li>A quick check of dynamics, tempo and symbols before a winter concert</li></ul>'
            f'</div><div>'
            f'<h2>Level guide</h2><table><tr><th>Level</th><th>Skill</th><th>Suggested</th><th>Pages</th></tr>{rows}</table>'
            f'<p class="small">Level A: pp, p, mp, mf, f, ff (the key gives the meaning, such as very soft or medium loud). '
            f'Level B: largo, adagio, andante, moderato, allegro, presto (the key gives the meaning, such as slow or fast). '
            f'Level C: fermata, repeat sign, crescendo, decrescendo, staccato, accent, slur (the key gives the name). '
            f'Each picture uses up to five colors, so each key shows up to five of the markings.</p>'
            f'<h2>Standards</h2><p>Practices music vocabulary and reading notation: dynamics, tempo and expressive symbols. '
            f'Supports the National Core Arts Standards for Music, Responding (MU:Re7.2) and Performing (MU:Pr4.3), grades 2–5. Keep claims modest: this is a practice activity.</p>'
            f'<h2>What’s inside</h2><p class="small">Page 3: student reference (every marking and its meaning). {toc["all"]}. '
            f'Last page: terms of use and credits. Pictures: {pics}.</p>'
            f'<p class="small">No songs, lyrics or copyrighted characters are used. All pictures are original line art.</p>'
            f'</div></div>'
            f'{foot(COPY, "Page 2")}</section>')


def reference_page():
    def row(svg, name, mean):
        return f'<tr><td style="width:84pt;text-align:center">{svg}</td><td><b>{escape(name)}</b></td><td>{escape(mean)}</td></tr>'
    dyn = "".join(row(f'<svg width="66pt" height="26pt" viewBox="0 0 66 26">{SY.dynamic_svg(k, 33, 13, 30)}</svg>', f'{k}  ·  {v[1]}', v[2]) for k, v in SY.DYNAMICS.items())
    tmp = "".join(row(f'<svg width="76pt" height="20pt" viewBox="0 0 76 20">{SY.term_svg(k, 38, 10, 16.5)}</svg>', v[0], v[2]) for k, v in SY.TEMPO.items())
    sym = "".join(row(f'<svg width="66pt" height="34pt" viewBox="-33 -17 66 34">{SY.symbol_art_svg(k, 0, 0)}</svg>', v[0], v[1]) for k, v in SY.SYMBOLS.items())
    t = lambda body, h: f'<table class="rt"><tr><th>{h[0]}</th><th>{h[1]}</th><th>{h[2]}</th></tr>{body}</table>'
    return (f'<section class="page doc"><div class="rule"><h1>Student Reference</h1>'
            f'<div class="l" style="font-size:13pt">Keep this page nearby while you color.</div></div>'
            f'<div class="cols" style="gap:16pt"><div style="flex:1.05">'
            f'<h2>Level A <span class="acc">·</span> Dynamics</h2>{t(dyn, ("Marking", "Name", "Means"))}'
            f'<h2>Level B <span class="acc">·</span> Tempo terms</h2>{t(tmp, ("Term", "Name", "Means"))}'
            f'</div><div style="flex:1">'
            f'<h2>Level C <span class="acc">·</span> Music symbols</h2>{t(sym, ("Symbol", "Name", "Means"))}'
            f'<p class="small" style="margin-top:6pt">Dynamics: <b>m</b> stands for mezzo (medium). A crescendo and a decrescendo change the dynamic gradually; '
            f'a staccato dot goes on the notehead side, an accent goes over or under the note, and a slur joins notes of different pitches.</p>'
            f'</div></div>'
            f'<div style="flex:1"></div>{foot(COPY, "Page 3")}</section>')


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
            f'<li>Pictures, layouts and answer keys: original work, {BRAND} by {STORE}.</li>'
            f'<li>Dynamics font: Bravura © Steinberg Media Technologies GmbH, SIL Open Font License 1.1.</li>'
            f'<li>Text fonts: Oswald (The Oswald Project Authors) and Source Sans 3 (Adobe), SIL Open Font License 1.1.</li></ul>'
            f'<p class="small">{DISCLOSURE}</p>'
            f'<div style="flex:1"></div>{foot(COPY, f"Page {page_no}")}</section>')


# ---------------------------------------------------------------- layout
def paginate(sheets):
    page = 4
    toc = {}
    for level in LEVELS:
        ls = [s for s in sheets if s.level == level]
        first = page
        for s in ls:
            s.page = page
            page += 1
        for s in ls:
            s.key_page = page
            page += 1
        toc[level] = f"{first}–{first + 8} worksheets, {first + 9}–{page - 1} keys"
    toc["all"] = "; ".join(f"Level {k}: pages {toc[k]}" for k in LEVELS)
    return page, toc  # page = terms page number


def full_pages(sheets):
    terms_no, toc = paginate(sheets)
    pages = [cover_page(sheets), teacher_page(sheets, toc), reference_page()]
    for level in LEVELS:
        ls = [s for s in sheets if s.level == level]
        pages += [worksheet_page(s) for s in ls]
        pages += [answer_page(s) for s in ls]
    pages.append(terms_page(terms_no))
    return pages, terms_no


PREVIEW_PICKS = [("A", "snowman", "ws"), ("B", "penguin", "ws"), ("C", "igloo", "ws"), ("C", "igloo", "key")]


def preview_pages(sheets):
    paginate(sheets)
    out = []
    for level, slug, kind in PREVIEW_PICKS:
        s = next(x for x in sheets if x.level == level and x.slug == slug)
        out.append(worksheet_page(s, watermark=True) if kind == "ws" else answer_page(s, watermark=True))
    return out


# ---------------------------------------------------------------- square images (2000 x 2000)
SQ_CSS = """
.sq { width: 1000px; height: 1000px; position: relative; overflow: hidden; background: #fff; display: flex; flex-direction: column; align-items: center; }
.sq .store { font-family: 'Oswald'; font-weight: 500; letter-spacing: .32em; text-transform: uppercase; font-size: 22px; margin-top: 34px; }
.sq .hd { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; text-align: center; line-height: .95; }
.sq .sub { font-family: 'Oswald'; font-weight: 300; text-align: center; }
.sq .band { position: absolute; left: 0; right: 0; bottom: 0; background: #000; color: #fff; text-align: center; font-family: 'Oswald';
            font-weight: 500; text-transform: uppercase; letter-spacing: .1em; font-size: 26px; padding: 16px 0 18px; }
.sq .band em { font-style: normal; color: ACCENT_LT; }
.shot { background: #fff; border: 2px solid #000; box-shadow: 8px 8px 0 #000; position: relative; overflow: hidden; }
.shot img { display: block; width: 100%; }
.lbl { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 22px; text-align: center; margin-top: 16px; }
.lbl span { font-weight: 300; text-transform: none; display: block; font-size: 18px; }
.swm { position: absolute; left: 50%; top: 50%; transform: translate(-50%,-50%) rotate(-38deg); font-family: 'Oswald'; font-weight: 700;
       color: rgba(0,0,0,.14); white-space: nowrap; letter-spacing: .06em; }
""".replace("ACCENT_LT", COLORS["accent_lt"])


def sq_doc(body):
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{font_css()}'
            f'html,body{{margin:0;background:#fff}}{SQ_CSS}</style></head><body>{body}</body></html>')


def cover_square(sheets):
    s = cover_sheet(sheets)
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div>'
        f'<div style="width:560px;margin-top:22px">{picture_svg(s, fills=cover_art(s), stroke=2.4)}</div>'
        f'<div class="hd" style="font-size:62px;margin-top:18px">Winter Color by</div>'
        f'<div class="hd" style="font-size:118px">Music Symbol</div>'
        f'<div class="sub" style="font-size:29px;margin-top:12px">Dynamics · Tempo terms · Symbols — with answer keys</div>'
        f'<div class="band">Grades 2–5 <em>·</em> 3 levels <em>·</em> 27 worksheets</div></div>')


# The preview PDF pages are already watermarked, so the page shots below get no second watermark.
def preview_square_1(img):
    shots = "".join(
        f'<div style="width:296px"><div class="shot"><img src="{img[k]}"></div>'
        f'<div class="lbl">Level {k}<span>{LEVELS[k]["name"]} · gr. {LEVELS[k]["grades"]}</span></div></div>' for k in "ABC")
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div>'
        f'<div class="hd" style="font-size:78px;margin-top:20px">3 levels, same pictures</div>'
        f'<div class="sub" style="font-size:27px;margin-top:8px">Differentiate in one lesson: everyone colors the same picture at their own level</div>'
        f'<div style="display:flex;gap:26px;margin-top:60px">{shots}</div>'
        f'<div class="band">9 winter pictures <em>·</em> 27 worksheets</div></div>')


def preview_square_2(ws, key):
    pair = "".join(
        f'<div style="width:420px"><div class="shot"><img src="{src}"></div>'
        f'<div class="lbl">{lab}</div></div>' for src, lab in ((ws, "Worksheet"), (key, "Answer key")))
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div>'
        f'<div class="hd" style="font-size:70px;margin-top:20px">An answer key for every page</div>'
        f'<div class="sub" style="font-size:27px;margin-top:8px">Every key is built from the same data as its worksheet, then verified</div>'
        f'<div style="display:flex;gap:40px;margin-top:30px">{pair}</div>'
        f'<div class="band">27 full-color answer keys</div></div>')


def preview_square_3(sheets):
    cells = "".join(
        f'<div style="width:236px"><div style="border:2px solid #000">{picture_svg(s, answer=True, stroke=2.0, frame=False)}</div>'
        f'<div class="lbl" style="font-size:15px;margin-top:4px">{s.number}. {escape(s.title)}</div></div>'
        for s in sheets if s.level == "A")
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div>'
        f'<div class="hd" style="font-size:60px;margin-top:12px">9 original winter pictures</div>'
        f'<div style="position:relative;display:flex;flex-wrap:wrap;gap:6px 22px;width:800px;margin-top:10px;justify-content:center">{cells}'
        f'<div class="swm" style="font-size:150px">PREVIEW</div></div>'
        f'<div class="band">Original winter art <em>·</em> kid-friendly <em>·</em> grades 2–5</div></div>')


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


def write(name, text):
    p = os.path.join(BUILD, name)
    with open(p, "w") as f:
        f.write(text)
    return p


MEASURE_JS = """
const { chromium } = require('playwright'); const url = require('url');
(async () => { const b = await chromium.launch(); const out = {};
  for (const f of process.argv.slice(2)) { const p = await b.newPage({ viewport: { width: 1000, height: 1000 } });
    await p.goto(url.pathToFileURL(f).href, { waitUntil: 'load' }); await p.evaluate(() => document.fonts.ready);
    out[f] = await p.evaluate(() => { const band = document.querySelector('.band').getBoundingClientRect().top; let low = 0;
      for (const e of document.querySelectorAll('.sq *')) { if (e.closest('.band') || e.classList.contains('swm')) continue;
        const r = e.getBoundingClientRect(); if (r.width && r.height) low = Math.max(low, r.bottom); }
      const wide = [...document.querySelectorAll('.sq *')].some(e => { const r = e.getBoundingClientRect(); return r.right > 1000.5 || r.left < -0.5; });
      return { band, low, wide }; });
    await p.close(); }
  await b.close(); console.log(JSON.stringify(out)); })();
"""


def measure_squares(files):
    js = write("measure.js", MEASURE_JS)
    out = subprocess.run(["node", js, *files], capture_output=True, text=True, env=node_env())
    if out.returncode:
        raise RuntimeError(out.stderr)
    return json.loads(out.stdout.strip().splitlines()[-1])


def build():
    os.makedirs(BUILD, exist_ok=True)
    sheets = make_sheets()
    problems = verify_data(sheets)
    if problems:
        print("\n".join(problems))
        sys.exit("data check failed; not rendering")
    pages, _ = full_pages(sheets)
    full = write("resource.html", html_doc(pages, TITLE))
    prev = write("preview.html", html_doc(preview_pages(sheets), "Preview"))
    render([{"html": full, "pdf": PDF}, {"html": prev, "pdf": PREVIEW_PDF}])
    for i in range(1, 5):
        subprocess.run(["pdftoppm", "-png", "-r", "110", "-f", str(i), "-l", str(i), "-singlefile", PREVIEW_PDF,
                        os.path.join(BUILD, f"pv{i}")], check=True)
    img = {"A": "pv1.png", "B": "pv2.png", "C": "pv3.png"}
    sq = [write("cover.html", cover_square(sheets)), write("p1.html", preview_square_1(img)),
          write("p2.html", preview_square_2("pv3.png", "pv4.png")), write("p3.html", preview_square_3(sheets))]
    outs = [COVER_PNG] + PREVIEW_PNGS
    render([{"html": h, "png": o, "width": 1000, "height": 1000, "scale": 2} for h, o in zip(sq, outs)])
    write_listing()
    print(f"built {PDF}, {PREVIEW_PDF}, cover + 3 previews, UPLOAD.md, tpt.json")


# ---------------------------------------------------------------- listing files
TITLE_LISTING = "Color by Music Symbol Worksheets | Dynamics, Tempo Terms, Symbols | Gr 2-5"
INCLUDED = [  # (text, pages): the page list must total the PDF
    ("Cover", 1),
    ("Teacher notes with a level guide and page list", 1),
    ("Student reference page: every dynamic, tempo term and music symbol with its meaning", 1),
    ("Level A: Dynamics (pp, p, mp, mf, f, ff), 9 worksheets + 9 answer keys (grades 2–3)", 18),
    ("Level B: Tempo terms (largo, adagio, andante, moderato, allegro, presto), 9 worksheets + 9 answer keys (grades 3–5)", 18),
    ("Level C: Music symbols (fermata, repeat sign, crescendo, decrescendo, staccato, accent, slur), 9 worksheets + 9 answer keys (grades 4–5)", 18),
    ("Terms of use and credits", 1),
]


def write_listing():
    inc = "\n".join(f"• {t} — {n} page{'s' if n != 1 else ''}" for t, n in INCLUDED)
    assert sum(n for _, n in INCLUDED) == N_PAGES
    pics = ", ".join(t for _, t, _ in PICTURES)
    desc = f"""Color by Music Symbol with three levels in one set, so every student in your class can color the same winter picture at their own level. 9 original, kid-friendly winter pictures, 27 worksheets and 27 full-color answer keys. Students read a dynamic marking, a tempo term or a music symbol in each space, find its meaning in the key, and color. Winter themed and non-denominational: it fits every school calendar.

WHAT'S INCLUDED ({N_PAGES} pages, PDF, US Letter)
{inc}
Total: {N_PAGES} pages.

PICTURES: {pics}.

HOW TO USE
Print, hand out crayons and let students work at their own level. Levels A and B show the marking in each space and the key gives its meaning (for example, "very soft" or "fast"); Level C shows the symbol and the key gives its name. Each worksheet has a matching full-color answer key, and every key is generated from the same data as its worksheet and verified in code. Great for early finishers, music centers, sub plans and winter concert season.

• Grades 2–5 (choose the level that fits)
• Print in black and white: every color in the key is also written as a word
• No songs, lyrics or copyrighted characters

{DISCLOSURE}"""
    up = f"""# UPLOAD: Winter Color by Music Symbol (TpT 039)

These fields follow the order of TpT's "Add a resource" form. Same format as 035 Hanukkah Color by Note and 032 Christmas Color by Note, with music vocabulary (dynamics, tempo terms, symbols) instead of note reading.

**Files to attach**
- Resource (digital download): `{SLUG}.pdf`, {N_PAGES} pages, US Letter.
- Thumbnails, in this order: `cover.png`, `preview-1.png`, `preview-2.png`, `preview-3.png` (all 2000 × 2000).
- Preview file: `{SLUG}-PREVIEW.pdf`, 4 watermarked pages.

## 1. Title

```
{TITLE_LISTING}
```
({len(TITLE_LISTING)} characters; the limit is 80.) The title leaves out "Winter" and other seasonal words because TpT's Seasonal Titles notice blocked a seasonal title on 027 (see 032 and 035). If TpT accepts it, "Winter Color by Music Symbol | Dynamics, Tempo Terms & Symbols, Gr 2-5" is the preferred title.

## 2. Description

```
{desc}
```

## 3. Grades

2, 3, 4, 5.

## 4. Subjects and tags

- Subject: Music
- Tags: Winter, Worksheets, Printables, Activities

## 5. Resource type

- Worksheets
- Activities

## 6. Standards (optional)

National Core Arts Standards, Music: MU:Re7.2 and MU:Pr4.3, grades 2–5. Optional.

## 7. Price

**${PRICE}** (queue price).

## 8. Free or paid / preview

Paid. Preview PDF: Level A snowman worksheet, Level B penguin worksheet, Level C igloo worksheet and the Level C igloo answer key, all watermarked.

## 9. Before you click publish

- [ ] List by **early Nov 2026** or as soon as possible; winter searches build through November and December.
- Winter and secular imagery only: snowman, mittens, penguin, cocoa mug, igloo, snowflake, pine tree, hat and ice skate. No holiday symbols, characters or brands.
"""
    with open(UPLOAD, "w") as f:
        f.write(up)
    tj = {"price": PRICE, "license_price": PRICE, "tax_code": "Other Digital Goods - No Physical Media",
          "grades": ["2nd-grade", "3rd-grade", "4th-grade", "5th-grade"], "subjects": ["Music"],
          "tags": ["Winter", "Worksheets", "Printables", "Activities"], "formats": ["PDF"], "pages": N_PAGES,
          "answer_key": "Included",
          "files": {"product": f"{SLUG}.pdf", "preview": f"{SLUG}-PREVIEW.pdf", "thumb1": "cover.png",
                    "thumb2": "preview-1.png", "thumb3": "preview-2.png", "thumb4": "preview-3.png"}}
    with open(TPTJSON, "w") as f:
        json.dump(tj, f, indent=2, ensure_ascii=False)
        f.write("\n")


# ---------------------------------------------------------------- checks
def verify_data(sheets):
    errs = []
    for sh in sheets:
        tag = f"{sh.level}/{sh.slug}"
        ids = LEVELS[sh.level]["ids"]
        cols = {r["color"] for r in sh.regions}
        if len(cols) > 5:
            errs.append(f"{tag}: {len(cols)} colours (max 5)")
        if set(sh.key) != cols:
            errs.append(f"{tag}: key colours {sorted(sh.key)} != picture colours {sorted(cols)}")
        if len(set(sh.key.values())) != len(sh.key):
            errs.append(f"{tag}: key is not one-to-one")
        for c, sid in sh.key.items():
            if c not in COLORS:
                errs.append(f"{tag}: unknown colour {c}")
            if sid not in ids:
                errs.append(f"{tag}: key entry {sid} is not a level {sh.level} symbol")
        used = set()
        bw, bh = box_for(sh.level)
        boxes = []
        for r in sh.regions:
            if not r["symbols"]:
                errs.append(f"{tag}: region {r['id']} ({r['color']}, {r['poly'].area:.0f}pt2) has no room for a symbol")
                continue
            for cx, cy, sym in r["symbols"]:
                used.add(sym)
                if sym not in sh.inverse():
                    errs.append(f"{tag}: region {r['id']} symbol {sym} is not in the key")
                elif sh.inverse()[sym] != r["color"]:
                    errs.append(f"{tag}: region {r['id']} symbol {sym} maps to {sh.inverse()[sym]}, picture says {r['color']}")
                b = sbox(cx - bw / 2, cy - bh / 2, cx + bw / 2, cy + bh / 2)
                if not b.within(r["poly"]):
                    errs.append(f"{tag}: region {r['id']} symbol box spills outside its region")
                if b.intersects(sh.ink):
                    errs.append(f"{tag}: region {r['id']} symbol overlaps printed detail")
                if any(b.intersects(o) for o in boxes):
                    errs.append(f"{tag}: region {r['id']} symbol overlaps another symbol")
                boxes.append(b)
            if sh.answer_color(r) != r["color"]:
                errs.append(f"{tag}: answer key colour for region {r['id']} disagrees with the picture")
        if used != set(sh.key.values()):
            errs.append(f"{tag}: key entries never used: {set(sh.key.values()) - used}")
    for slug, _, _ in PICTURES:
        ids = {tuple(r["id"] for r in s.regions) for s in sheets if s.slug == slug}
        if len(ids) != 1:
            errs.append(f"{slug}: levels disagree on regions")
    # music facts
    want_dyn = {"pp": "very soft", "p": "soft", "mp": "medium soft", "mf": "medium loud", "f": "loud", "ff": "very loud"}
    if {k: v[2] for k, v in SY.DYNAMICS.items()} != want_dyn:
        errs.append("dynamics meanings wrong")
    order = ["pp", "p", "mp", "mf", "f", "ff"]
    if list(SY.DYNAMICS) != order:
        errs.append("dynamics not in soft-to-loud order")
    tempo = {"largo": "very slow", "adagio": "slow", "andante": "walking speed", "moderato": "medium", "allegro": "fast", "presto": "very fast"}
    if {k: v[1] for k, v in SY.TEMPO.items()} != tempo:
        errs.append("tempo meanings wrong")
    for lv in LEVELS.values():
        keys = [key_label(next(k for k, v in LEVELS.items() if v is lv), i) for i in lv["ids"]]
        if len({m for m, _ in keys}) != len(keys):
            errs.append(f"duplicate key text in level {lv['name']}")
    for sid in SY.SYMBOLS:
        SY.symbol_art_svg(sid, 0, 0)
    return errs


def pdf_fonts(path):
    out = subprocess.run(["pdffonts", path], capture_output=True, text=True, check=True).stdout.splitlines()[2:]
    return [(p.split()[0], p.split()[-5]) for p in out if p.strip()]


def verify_files():
    errs = []
    from pypdf import PdfReader
    from PIL import Image
    for p in [PDF, PREVIEW_PDF, COVER_PNG, *PREVIEW_PNGS, UPLOAD, TPTJSON, os.path.join(TPT, "STYLE.md"), RENDER_JS]:
        if not os.path.exists(p):
            errs.append(f"missing {os.path.relpath(p, TPT)}")
    if errs:
        return errs
    for path, want_pages in ((PDF, N_PAGES), (PREVIEW_PDF, 4)):
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
        names = " ".join(n for n, _ in fonts)
        for fam in ("Bravura", "Oswald", "SourceSans3"):
            if fam.lower() not in names.lower().replace(" ", ""):
                errs.append(f"{os.path.basename(path)}: {fam} not found in PDF fonts")
    full = PdfReader(PDF)
    ftxt = [pg.extract_text() for pg in full.pages]
    for i, t in enumerate(ftxt):
        if "PREVIEW" in t:
            errs.append(f"{os.path.basename(PDF)} p{i + 1}: contains a PREVIEW watermark")
        if i >= 3 and i < N_PAGES - 1 and f"Page {i + 1}" not in t.replace("\n", " "):
            errs.append(f"{os.path.basename(PDF)} p{i + 1}: footer page number missing/wrong")
    prd = PdfReader(PREVIEW_PDF)
    for i, pg in enumerate(prd.pages):
        c = pg.extract_text().count("PREVIEW")
        if c != 1:
            errs.append(f"preview PDF p{i + 1}: watermark text appears {c} times (want exactly 1)")
    for p in [COVER_PNG, *PREVIEW_PNGS]:
        if Image.open(p).size != (2000, 2000):
            errs.append(f"{os.path.basename(p)}: not 2000x2000")
    # square-image layout: nothing sits under the band, nothing leaves the frame
    sq_files = [os.path.join(BUILD, n) for n in ("cover.html", "p1.html", "p2.html", "p3.html")]
    if all(os.path.exists(f) for f in sq_files):
        for f, m in measure_squares(sq_files).items():
            if m["low"] > m["band"] - 6:
                errs.append(f"{os.path.basename(f)}: content reaches y={m['low']:.0f}, band starts at {m['band']:.0f} (clipped)")
            if m["wide"]:
                errs.append(f"{os.path.basename(f)}: content leaves the frame sideways")
    cov = open(os.path.join(BUILD, "cover.html")).read() if os.path.exists(os.path.join(BUILD, "cover.html")) else ""
    for n in re.findall(r"(\d+)\s*(?:pages|pgs)", cov, re.I):
        if int(n) != N_PAGES:
            errs.append(f"cover claims {n} pages, PDF has {N_PAGES}")
    # UPLOAD.md and tpt.json
    up = open(UPLOAD).read()
    m = re.search(r"^## 1\. Title\s*\n+```\n(.+?)\n```", up, re.M | re.S)
    if not m:
        errs.append("UPLOAD.md: title block not found")
    else:
        t = m.group(1).strip()
        if len(t) > 80:
            errs.append(f"UPLOAD.md: title is {len(t)} chars (max 80)")
        if re.search(r"winter|christmas|holiday|hanukkah|december|seasonal", t, re.I):
            errs.append("UPLOAD.md: title contains a seasonal word")
    d = re.search(r"WHAT'S INCLUDED.*?\n(.*?)\nTotal: (\d+) pages", up, re.S)
    if not d:
        errs.append("UPLOAD.md: page list not found")
    else:
        nums = [int(x) for x in re.findall(r"— (\d+) pages?$", d.group(1), re.M)]
        if sum(nums) != len(full.pages) or int(d.group(2)) != len(full.pages):
            errs.append(f"UPLOAD.md: page list totals {sum(nums)} (stated {d.group(2)}), PDF has {len(full.pages)}")
    for n in re.findall(r"(\d+) pages, PDF", up) + re.findall(r"`[^`]*\.pdf`, (\d+) pages", up):
        if int(n) != len(full.pages):
            errs.append(f"UPLOAD.md: says {n} pages, PDF has {len(full.pages)}")
    for p_, _, _ in PICTURES:
        pass
    for _, title, _ in PICTURES:
        if title.lower() not in up.lower():
            errs.append(f"UPLOAD.md: picture '{title}' missing")
    for need in (DISCLOSURE, f"${PRICE}"):
        if need not in up:
            errs.append(f"UPLOAD.md: missing '{need}'")
    tj = json.load(open(TPTJSON))
    tags = set(json.load(open(os.path.join(TPT, "TAG-OPTIONS.json")))["options"])
    _s = json.load(open(os.path.join(TPT, "SUBJECT-OPTIONS.json")))
    subs = set(_s["options"] if isinstance(_s, dict) else _s)
    if not 1 <= len(tj["tags"]) <= 6 or any(t not in tags for t in tj["tags"]):
        errs.append("tpt.json: tags not exact TAG-OPTIONS entries (1-6)")
    if not 1 <= len(tj["subjects"]) <= 3 or any(s not in subs for s in tj["subjects"]):
        errs.append("tpt.json: subjects not exact SUBJECT-OPTIONS entries")
    if not 1 <= len(tj["grades"]) <= 4:
        errs.append("tpt.json: grades must be 1-4")
    if tj["pages"] != len(full.pages):
        errs.append(f"tpt.json: pages {tj['pages']} != PDF {len(full.pages)}")
    if tj["price"] != PRICE or tj["license_price"] != PRICE:
        errs.append("tpt.json: price mismatch")
    for k, v in tj["files"].items():
        if not os.path.exists(os.path.join(HERE, v)):
            errs.append(f"tpt.json: {k} file {v} missing")
    return errs


def check():
    sheets = make_sheets()
    errs = verify_data(sheets)
    n_regions = sum(len(s.regions) for s in sheets)
    n_syms = sum(len(r["symbols"]) for s in sheets for r in s.regions)
    errs += verify_files()
    if errs:
        print("CHECK FAILED")
        print("\n".join(" - " + e for e in errs))
        sys.exit(1)
    print(f"CHECK OK: {len(sheets)} worksheets + {len(sheets)} answer keys, {n_regions} regions, {n_syms} symbols; "
          f"every symbol maps to its region's key colour; answer keys derived from printed symbols; "
          f"PDF {N_PAGES} Letter pages, preview 4 pages (one watermark each), fonts embedded; images 2000x2000, no clipping; listing ok.")


if __name__ == "__main__":
    if "--check" in sys.argv:
        check()
    else:
        build()
