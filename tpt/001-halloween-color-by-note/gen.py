#!/usr/bin/env python3
"""Halloween Color by Note (TpT 001): build the resource and verify it.

    python3 gen.py           build everything (PDFs, PNGs) into this folder
    python3 gen.py --check   verify data, answer keys, pages, fonts and files

Worksheets and answer keys are rendered from the same `Sheet` objects: each
region stores the symbol printed in it, and the answer key colour is looked up
from that printed symbol through the sheet's key. `--check` confirms that the
lookup lands on the colour the picture was designed with, for every region.

Rendering uses Playwright + Chromium (HTML/SVG -> PDF/PNG) with the OFL fonts in
../fonts, embedded as subsets. Run with NODE_PATH=$(npm root -g) available, or
let this script find it.
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

import notation as N  # noqa: E402
from pictures import PICTURES, W, H  # noqa: E402
from regions import build_regions, place, n_symbols  # noqa: E402

TPT = os.path.dirname(HERE)
FONTS = os.path.join(TPT, "fonts")
BUILD = os.path.join(HERE, "build")
RENDER_JS = os.path.join(TPT, "tools", "render.js")

SLUG = "halloween-color-by-note"
PDF = os.path.join(HERE, f"{SLUG}.pdf")
PREVIEW_PDF = os.path.join(HERE, f"{SLUG}-PREVIEW.pdf")
COVER_PNG = os.path.join(HERE, "cover.png")
PREVIEW_PNGS = [os.path.join(HERE, f"preview-{i}.png") for i in (1, 2, 3)]
UPLOAD = os.path.join(HERE, "UPLOAD.md")

STORE = "Brian Lotze"      # copyright holder
BRAND = "Hudson Beat"      # store line on covers and previews (owner, 4 Oct)
YEAR = 2026
ACCENT = "#E8731A"  # this product's single accent (Halloween orange)

COLORS = {  # crayon name -> answer-key fill
    "orange": "#F39234", "black": "#2E2E2E", "green": "#5DB04C", "purple": "#9467C9",
    "yellow": "#FFD94A", "brown": "#9A6434", "gray": "#A8A8A8", "white": "#FFFFFF", "blue": "#4F88DA",
}
LEVELS = {
    "A": {"name": "Rhythm values", "kind": "rhythm", "grades": "1–2",
          "how": "Find the note or rest in each space. Match it to the key, then color the space."},
    "B": {"name": "Treble clef notes", "kind": "treble", "grades": "2–4",
          "how": "Name the note in each space. Find that letter in the key, then color the space."},
    "C": {"name": "Bass clef notes", "kind": "bass", "grades": "4–5",
          "how": "Name the note in each space. Find that letter in the key, then color the space."},
}
HELPER = {"treble": "Treble clef — lines: E G B D F · spaces: F A C E",
          "bass": "Bass clef — lines: G B D F A · spaces: A C E G"}

MARGIN = 2.0  # pt of white space kept around every symbol inside its region


# ---------------------------------------------------------------- data
@dataclass
class Sheet:
    level: str
    slug: str
    title: str
    key: dict            # colour -> symbol (rhythm id, or letter name)
    regions: list        # dicts: id, poly, color, symbols [(cx, cy, symbol_or_pitch)]
    ink: object
    number: int = 0
    key_page: int = 0
    page: int = 0
    extra: dict = field(default_factory=dict)

    def symbol_class(self, printed):
        """The key entry a printed symbol belongs to: rhythm id as is, pitch -> letter."""
        return printed if self.level == "A" else printed[0]

    def inverse(self):
        return {v: k for k, v in self.key.items()}

    def answer_color(self, region):
        """Colour for the answer key, derived from the symbols printed on the worksheet."""
        inv = self.inverse()
        cols = {inv[self.symbol_class(sym)] for _, _, sym in region["symbols"]}
        assert len(cols) == 1, f"region {region['id']} has symbols of different colours"
        return cols.pop()


def box_for(level):
    if level == "A":
        w, h = N.rhythm_box()
    else:
        w, h = N.staff_box()
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
            if level == "A":
                pool = list(N.RHYTHM)
            else:
                pool = list(N.LETTERS)
                rng.shuffle(pool)
                pool = sorted(pool[:len(colours)], key=N.LETTERS.index)
            syms = pool[:len(colours)]
            rng.shuffle(syms)
            key = dict(zip(colours, syms))
            clef = LEVELS[level]["kind"]
            octave_cycle = {}
            regs = []
            for r in regions:
                taken = unary_union([sbox(cx - bw / 2, cy - bh / 2, cx + bw / 2, cy + bh / 2) for rr in regs for cx, cy, _ in rr["symbols"]] or [sbox(-9, -9, -8, -8)])
                pts = place(r["poly"], unary_union([ink, taken]), bw, bh, n_symbols(r["poly"]))
                symbols = []
                for cx, cy in pts:
                    if level == "A":
                        symbols.append((cx, cy, key[r["color"]]))
                    else:
                        letter = key[r["color"]]
                        options = [p for p in N.CLEFS[clef]["range"] if p[0] == letter]
                        k = octave_cycle.get(letter, 0)
                        octave_cycle[letter] = k + 1
                        symbols.append((cx, cy, options[k % len(options)]))
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
    if level == "A":
        return N.rhythm_svg(sym, cx, cy)
    return N.mini_staff_svg(sym, LEVELS[level]["kind"], cx, cy)


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
    out.append(f'<path d="{geom_path(sheet.ink)}" fill="#000"/>')
    if show_symbols:
        for r in sheet.regions:
            if fills is not None and r["id"] in fills:
                continue
            for cx, cy, sym in r["symbols"]:
                out.append(symbol_svg(sheet.level, sym, cx, cy))
    if frame:
        out.append(f'<rect x="0" y="0" width="{W}" height="{H}" fill="none" stroke="#000" stroke-width="{stroke * 1.4}"/>')
    out.append("</svg>")
    return "".join(out)


def key_symbol_svg(level, sym):
    if level == "A":
        w, h = N.rhythm_box(6.0)
        return (f'<svg width="{w + 6:.0f}pt" height="{h + 6:.0f}pt" viewBox="0 0 {w + 6:.1f} {h + 6:.1f}">'
                f'{N.rhythm_svg(sym, (w + 6) / 2, (h + 6) / 2, 6.0)}</svg>')
    return f'<span class="kletter">{sym}</span>'


def key_html(sheet):
    cells = []
    for colour, sym in sheet.key.items():
        label = N.RHYTHM[sym][1] if sheet.level == "A" else f"{sym}"
        sub = f'<div class="kname">{escape(label)}</div>' if sheet.level == "A" else ""
        cells.append(f'<div class="kcell"><div class="ksym">{key_symbol_svg(sheet.level, sym)}{sub}</div>'
                     f'<div class="keq">=</div><div class="kcol"><span class="sw" style="background:{COLORS[colour]}"></span>'
                     f'<span class="cname">{colour}</span></div></div>')
    return f'<div class="key">{"".join(cells)}</div>'


# ---------------------------------------------------------------- html pages
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
.kname { font-size: 7.5pt; line-height: 1; margin-top: 1pt; white-space: nowrap; }
.kletter { font-family: 'Oswald'; font-weight: 700; font-size: 26pt; line-height: 1; }
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


def worksheet_page(sh, watermark=False):
    lv = LEVELS[sh.level]
    helper = f'<div class="helper">{HELPER[lv["kind"]]}</div>' if sh.level != "A" else '<div class="helper">Every note and rest is shown without a staff. Look at the notehead, stem and flag.</div>'
    wm = '<div class="wm">PREVIEW</div>' if watermark else ""
    return (f'<section class="page">{wm}'
            f'<div class="top"><div class="h t">Halloween Color by Note<small>{sh.number}. {escape(sh.title)}</small></div>'
            f'<div class="tag"><div class="lv">LEVEL {sh.level}</div><div class="ln">{lv["name"]}</div></div></div>'
            f'<div class="name">Name<span></span>Date<span class="d"></span></div>'
            f'<div class="how"><b>How to play:</b> {lv["how"]}</div>'
            f'{key_html(sh)}{helper}'
            f'<div class="pic">{picture_svg(sh)}</div>'
            f'{foot(COPY, f"Level {sh.level} · Answer key on page {sh.key_page} · Page {sh.page}")}</section>')


def answer_page(sh, watermark=False):
    lv = LEVELS[sh.level]
    wm = '<div class="wm">PREVIEW</div>' if watermark else ""
    return (f'<section class="page">{wm}'
            f'<div class="top"><div class="h t">Answer Key<small>{sh.number}. {escape(sh.title)} — Level {sh.level}, {lv["name"].lower()}</small></div>'
            f'<div class="tag"><div class="lv ak">ANSWER KEY</div><div class="ln">Level {sh.level} · {lv["name"]}</div></div></div>'
            f'<div class="how" style="margin-top:9pt">Every space is colored from the symbol printed in it on the worksheet (page {sh.page}).</div>'
            f'{key_html(sh)}<div class="helper">&nbsp;</div>'
            f'<div class="pic">{picture_svg(sh, answer=True)}</div>'
            f'{foot(COPY, f"Level {sh.level} answer key · Page {sh.key_page}")}</section>')


def cover_art(sheet):
    """Jack-o'-lantern half coloured in the accent + black (one-accent rule), symbols left in the rest."""
    return {r["id"]: r["color"] for r in sheet.regions if r["color"] in ("orange", "black")}


def cover_page(sheets):
    pump = next(s for s in sheets if s.level == "A" and s.slug == "pumpkin")
    return (f'<section class="page cover"><div class="store">{BRAND}</div>'
            f'<div style="width:6.2in">{picture_svg(pump, fills=cover_art(pump), stroke=2.2)}</div>'
            f'<div class="ctitle"><div class="a">HALLOWEEN</div><div class="b">COLOR BY NOTE</div>'
            f'<div class="c">Rhythm values · Treble clef · Bass clef — 3 levels with answer keys</div></div>'
            f'<div class="cband">Grades 1–5 <em>·</em> 27 worksheets <em>·</em> 27 answer keys</div></section>')


def teacher_page(sheets, toc):
    rows = "".join(f'<tr><td style="white-space:nowrap"><b>Level {k}</b></td><td>{v["name"]}</td><td style="white-space:nowrap">Grades {v["grades"]}</td><td>{toc[k]}</td></tr>' for k, v in LEVELS.items())
    pics = ", ".join(f"{i + 1}. {t}" for i, (_, t, _) in enumerate(PICTURES))
    return (f'<section class="page doc"><div class="rule"><h1>Teacher Notes</h1>'
            f'<div class="l" style="font-size:13pt">Halloween Color by Note · 3 levels · grades 1–5</div></div>'
            f'<div class="cols"><div>'
            f'<h2>How to use</h2><ul>'
            f'<li>Pick a level for each student or group, print the worksheets single-sided, and hand out crayons or colored pencils.</li>'
            f'<li>Students read the symbol in each space, find it in the color key, and color the space. Every space has a symbol in it.</li>'
            f'<li><b>White</b> in a key means leave the space white. <b>Gray</b> can be a gray crayon or a light pencil shade.</li>'
            f'<li>Check with the answer key that follows each level. Keys are full-color pages you can print or project.</li>'
            f'<li>All three levels use the same nine pictures, so one class can color the same picture at three different reading levels.</li></ul>'
            f'<h2>Great for</h2><ul><li>Early finishers and music centers</li><li>Sub plans (no music background needed with the answer keys)</li>'
            f'<li>A quick check of note-reading before or after Halloween lessons</li></ul>'
            f'</div><div>'
            f'<h2>Level guide</h2><table><tr><th>Level</th><th>Skill</th><th>Suggested</th><th>Pages</th></tr>{rows}</table>'
            f'<p class="small">Level A: whole, half, quarter and eighth notes and the quarter rest. Level B: treble-clef notes from middle C (C4) to A5. '
            f'Level C: bass-clef notes from E2 to middle C (C4). Ledger-line notes are included in levels B and C. '
            f'Each key uses letter names, and the same letter can appear in two octaves.</p>'
            f'<h2>Standards</h2><p>Practices reading standard notation: note and rest values, and note names on the treble and bass staff. '
            f'Supports the National Core Arts Standards for Music, Performing (reading notation, MU:Pr4.2) in grades 1–5.</p>'
            f'<h2>What’s inside</h2><p class="small">Page 3: student reference (note values and note names). {toc["all"]}. '
            f'Last page: terms of use and credits. Pictures: {pics}.</p>'
            f'<p class="small">No songs, lyrics or copyrighted characters are used. All pictures are original line art.</p>'
            f'</div></div>'
            f'{foot(COPY, "Page 2")}</section>')


def reference_page():
    cells = []
    for sym, (g, name, beats) in N.RHYTHM.items():
        w, h = N.rhythm_box(8.0)
        svg = (f'<svg width="{w + 10:.0f}pt" height="{h + 8:.0f}pt" viewBox="0 0 {w + 10:.1f} {h + 8:.1f}">'
               f'{N.rhythm_svg(sym, (w + 10) / 2, (h + 8) / 2, 8.0)}</svg>')
        cells.append(f'<div class="refcell">{svg}<b>{name}</b><span>{beats}</span></div>')
    s = 7.0
    staffs = []
    for clef in ("treble", "bass"):
        svg_body, length = N.reference_staff_svg(clef, 6, 9 * s, s)
        staffs.append(f'<svg width="100%" viewBox="0 0 {length + 12:.1f} {14.2 * s:.1f}">{svg_body}</svg>')
    return (f'<section class="page doc"><div class="rule"><h1>Student Reference</h1>'
            f'<div class="l" style="font-size:13pt">Keep this page nearby while you color.</div></div>'
            f'<h2>Level A <span class="acc">·</span> Note and rest values <span class="l" style="text-transform:none;font-size:11pt">(beats in 4/4 time)</span></h2>'
            f'<div class="refrow">{"".join(cells)}</div>'
            f'<h2>Level B <span class="acc">·</span> Treble clef note names</h2>{staffs[0]}'
            f'<p class="small" style="text-align:center">Lines (bottom to top): E G B D F · Spaces: F A C E · The first note, C, is middle C on a ledger line.</p>'
            f'<h2>Level C <span class="acc">·</span> Bass clef note names</h2>{staffs[1]}'
            f'<p class="small" style="text-align:center">Lines (bottom to top): G B D F A · Spaces: A C E G · The last note, C, is middle C on a ledger line.</p>'
            f'<h2>Stems</h2><p>Notes below the middle line have stems going <b>up</b> on the right. Notes on or above the middle line have stems going <b>down</b> on the left. '
            f'The stem never changes the note name: only where the notehead sits does.</p>'
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
            f'<li>Music notation font: Bravura © Steinberg Media Technologies GmbH, SIL Open Font License 1.1.</li>'
            f'<li>Text fonts: Oswald (The Oswald Project Authors) and Source Sans 3 (Adobe), SIL Open Font License 1.1.</li></ul>'
            f'<p class="small">Designed with the help of digital and AI tools, and checked by hand.</p>'
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


PREVIEW_PICKS = [("A", "pumpkin", "ws"), ("B", "bat", "ws"), ("C", "ghost", "ws"), ("C", "ghost", "key")]


def preview_pages(sheets):
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


def cover_square(sheets):
    pump = next(s for s in sheets if s.level == "A" and s.slug == "pumpkin")
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div>'
        f'<div style="width:610px;margin-top:22px">{picture_svg(pump, fills=cover_art(pump), stroke=2.4)}</div>'
        f'<div class="hd" style="font-size:66px;margin-top:20px">Halloween</div>'
        f'<div class="hd" style="font-size:112px">Color by Note</div>'
        f'<div class="sub" style="font-size:29px;margin-top:12px">Rhythm values · Treble clef · Bass clef — with answer keys</div>'
        f'<div class="band">Grades 1–5 <em>·</em> 3 levels <em>·</em> 27 worksheets</div></div>')


def preview_square_1(img):
    shots = "".join(
        f'<div style="width:296px"><div class="shot"><img src="{img[k]}"><div class="swm" style="font-size:54px">PREVIEW</div></div>'
        f'<div class="lbl">Level {k}<span>{LEVELS[k]["name"]} · gr. {LEVELS[k]["grades"]}</span></div></div>' for k in "ABC")
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div>'
        f'<div class="hd" style="font-size:78px;margin-top:20px">3 levels, same pictures</div>'
        f'<div class="sub" style="font-size:27px;margin-top:8px">Differentiate in one lesson: everyone colors the same picture at their own level</div>'
        f'<div style="display:flex;gap:26px;margin-top:60px">{shots}</div>'
        f'<div class="band">9 Halloween pictures <em>·</em> 27 worksheets</div></div>')


def preview_square_2(ws, key):
    pair = "".join(
        f'<div style="width:420px"><div class="shot"><img src="{src}"><div class="swm" style="font-size:80px">PREVIEW</div></div>'
        f'<div class="lbl">{lab}</div></div>' for src, lab in ((ws, "Worksheet"), (key, "Answer key")))
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div>'
        f'<div class="hd" style="font-size:70px;margin-top:20px">An answer key for every page</div>'
        f'<div class="sub" style="font-size:27px;margin-top:8px">Keys are built from the same data as the worksheets, then checked by hand</div>'
        f'<div style="display:flex;gap:40px;margin-top:30px">{pair}</div>'
        f'<div class="band">27 full-color answer keys</div></div>')


def preview_square_3(sheets):
    cells = "".join(
        f'<div style="width:236px"><div style="border:2px solid #000">{picture_svg(s, answer=True, stroke=2.0, frame=False)}</div>'
        f'<div class="lbl" style="font-size:15px;margin-top:4px">{s.number}. {escape(s.title)}</div></div>'
        for s in sheets if s.level == "B")
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div>'
        f'<div class="hd" style="font-size:60px;margin-top:12px">9 original pictures</div>'
        f'<div style="position:relative;display:flex;flex-wrap:wrap;gap:8px 22px;width:800px;margin-top:12px;justify-content:center">{cells}'
        f'<div class="swm" style="font-size:150px">PREVIEW</div></div>'
        f'<div class="band">Kid-friendly <em>·</em> not scary <em>·</em> grades 1–5</div></div>')


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


def build():
    os.makedirs(BUILD, exist_ok=True)
    sheets = make_sheets()
    problems = verify_data(sheets)
    if problems:
        print("\n".join(problems))
        sys.exit("data check failed; not rendering")
    pages, _ = full_pages(sheets)
    full = write("resource.html", html_doc(pages, "Halloween Color by Note"))
    prev = write("preview.html", html_doc(preview_pages(sheets), "Preview"))
    render([{"html": full, "pdf": PDF}, {"html": prev, "pdf": PREVIEW_PDF}])
    # page images for the square previews (from the watermarked preview PDF)
    for i in range(1, 5):
        subprocess.run(["pdftoppm", "-png", "-r", "110", "-f", str(i), "-l", str(i), "-singlefile", PREVIEW_PDF,
                        os.path.join(BUILD, f"pv{i}")], check=True)
    img = {"A": "pv1.png", "B": "pv2.png", "C": "pv3.png"}
    sq = [write("cover.html", cover_square(sheets)), write("p1.html", preview_square_1(img)),
          write("p2.html", preview_square_2("pv3.png", "pv4.png")), write("p3.html", preview_square_3(sheets))]
    outs = [COVER_PNG] + PREVIEW_PNGS
    render([{"html": h, "png": o, "width": 1000, "height": 1000, "scale": 2} for h, o in zip(sq, outs)])
    print(f"built {PDF}, {PREVIEW_PDF}, cover + 3 previews")


# ---------------------------------------------------------------- checks
EXPECTED_LEDGERS = {("treble", "C4"): 1, ("treble", "A5"): 1, ("bass", "E2"): 1, ("bass", "C4"): 1}


def verify_data(sheets):
    errs = []
    for sh in sheets:
        tag = f"{sh.level}/{sh.slug}"
        cols = {r["color"] for r in sh.regions}
        if len(cols) > 5:
            errs.append(f"{tag}: {len(cols)} colours (max 5)")
        if set(sh.key) != cols:
            errs.append(f"{tag}: key colours {sorted(sh.key)} != picture colours {sorted(cols)}")
        if len(set(sh.key.values())) != len(sh.key):
            errs.append(f"{tag}: key is not one-to-one")
        for c in sh.key:
            if c not in COLORS:
                errs.append(f"{tag}: unknown colour {c}")
        used = set()
        bw, bh = box_for(sh.level)
        boxes = []
        for r in sh.regions:
            if not r["symbols"]:
                errs.append(f"{tag}: region {r['id']} ({r['color']}, {r['poly'].area:.0f}pt2) has no room for a symbol")
                continue
            for cx, cy, sym in r["symbols"]:
                cls = sh.symbol_class(sym)
                used.add(cls)
                if cls not in sh.inverse():
                    errs.append(f"{tag}: region {r['id']} symbol {sym} is not in the key")
                elif sh.inverse()[cls] != r["color"]:
                    errs.append(f"{tag}: region {r['id']} symbol {sym} maps to {sh.inverse()[cls]}, picture says {r['color']}")
                b = sbox(cx - bw / 2, cy - bh / 2, cx + bw / 2, cy + bh / 2)
                if not b.within(r["poly"]):
                    errs.append(f"{tag}: region {r['id']} symbol box spills outside its region")
                if b.intersects(sh.ink):
                    errs.append(f"{tag}: region {r['id']} symbol overlaps printed detail")
                if any(b.intersects(o) for o in boxes):
                    errs.append(f"{tag}: region {r['id']} symbol overlaps another symbol")
                boxes.append(b)
                if sh.level == "A":
                    if sym not in N.RHYTHM:
                        errs.append(f"{tag}: unknown rhythm {sym}")
                else:
                    clef = LEVELS[sh.level]["kind"]
                    if sym not in N.CLEFS[clef]["range"]:
                        errs.append(f"{tag}: {sym} outside {clef} range")
                    st = N.step(sym, clef)
                    mid = N.step({"treble": "B4", "bass": "D3"}[clef], clef)
                    if N.stem_up(st) != (st < mid):
                        errs.append(f"{tag}: stem direction wrong for {sym}")
                    if len(N.ledger_steps(st)) != EXPECTED_LEDGERS.get((clef, sym), 0):
                        errs.append(f"{tag}: ledger lines wrong for {sym}")
            if r["symbols"] and sh.answer_color(r) != r["color"]:
                errs.append(f"{tag}: answer key colour for region {r['id']} disagrees with the picture")
        if used != set(sh.key.values()):
            errs.append(f"{tag}: key entries never used: {set(sh.key.values()) - used}")
    # same pictures and region sets across levels
    for slug, _, _ in PICTURES:
        ids = {tuple(r["id"] for r in s.regions) for s in sheets if s.slug == slug}
        if len(ids) != 1:
            errs.append(f"{slug}: levels disagree on regions")
    # clef sanity: staff positions of reference pitches
    for clef, pitch, want in [("treble", "E4", 0), ("treble", "B4", 4), ("treble", "F5", 8), ("treble", "G4", 2),
                              ("bass", "G2", 0), ("bass", "D3", 4), ("bass", "A3", 8), ("bass", "F3", 6)]:
        if N.step(pitch, clef) != want:
            errs.append(f"{clef}: {pitch} at step {N.step(pitch, clef)}, expected {want}")
    return errs


def pdf_fonts(path):
    out = subprocess.run(["pdffonts", path], capture_output=True, text=True, check=True).stdout.splitlines()[2:]
    rows = []
    for line in out:
        parts = line.split()
        # name type... emb sub uni object ID: emb is the 5th from the end
        rows.append((parts[0], parts[-5]))
    return rows


def verify_files():
    errs = []
    from pypdf import PdfReader
    from PIL import Image
    for p in [PDF, PREVIEW_PDF, COVER_PNG, *PREVIEW_PNGS, UPLOAD, os.path.join(TPT, "STYLE.md"), RENDER_JS]:
        if not os.path.exists(p):
            errs.append(f"missing {os.path.relpath(p, TPT)}")
    if errs:
        return errs
    for path, want_pages in ((PDF, 3 + 54 + 1), (PREVIEW_PDF, 4)):
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
    txt = " ".join(PdfReader(PREVIEW_PDF).pages[i].extract_text() for i in range(4))
    if txt.count("PREVIEW") < 4:
        errs.append("preview PDF: watermark missing on some pages")
    for p in [COVER_PNG, *PREVIEW_PNGS]:
        if Image.open(p).size != (2000, 2000):
            errs.append(f"{os.path.basename(p)}: not 2000x2000")
    up = open(UPLOAD).read()
    m = re.search(r"^## 1\. Title\s*\n+```\n(.+?)\n```", up, re.M | re.S)
    if not m:
        errs.append("UPLOAD.md: title block not found")
    elif len(m.group(1).strip()) > 80:
        errs.append(f"UPLOAD.md: title is {len(m.group(1).strip())} chars (max 80)")
    for need in ("Designed with the help of digital and AI tools, and checked by hand.", "$3.50", "Holidays/Seasonal", "Halloween"):
        if need not in up:
            errs.append(f"UPLOAD.md: missing '{need}'")
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
          f"PDF {3 + 54 + 1} Letter pages, preview 4 pages, fonts embedded; images 2000x2000; UPLOAD.md ok.")


if __name__ == "__main__":
    if "--check" in sys.argv:
        check()
    else:
        build()
