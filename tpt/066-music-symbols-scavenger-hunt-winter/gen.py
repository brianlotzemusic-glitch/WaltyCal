#!/usr/bin/env python3
"""Music Symbols Scavenger Hunt (TpT 066): build the resource and verify it.

    python3 gen.py           build everything (PDFs, PNGs, UPLOAD.md, tpt.json) into this folder
    python3 gen.py --check   re-read the rendered HTML and verify every hidden symbol, count, key and layout

Six scenes are drawn in code (scenes.py). The hidden symbols are Bravura glyphs plus plain rectangles for stems (symbols.py), scattered by a
seeded placement routine. `--check` does not trust the scene data: it parses the rendered SVG of every scene, classifies every hidden
symbol from the glyph code points and rectangles it actually contains, recounts each symbol per scene, compares with the answer key,
the hunt lists, the score page and the teacher notes, tests stems (right edge going up, left edge going down), staff positions on the
symbol key, padding inside each scene box, overlaps, the tempo and dynamics review keys against a second copy of the facts, and the
rendered layout (footer gap of 8 px, blank bands, watermarks, fonts, images, cross-references, UPLOAD.md, tpt.json).
"""
import json
import math
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from html import escape

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import symbols as SY  # noqa: E402
import scenes as SC  # noqa: E402

TPT = os.path.dirname(HERE)
FONTS = os.path.join(TPT, "fonts")
BUILD = os.path.join(HERE, "build")
RENDER_JS = os.path.join(TPT, "tools", "render.js")
HERO = os.path.join(HERE, "art", "hero.png")

SLUG = "music-symbols-scavenger-hunt"
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
DISCLOSURE = "Created with the help of digital and AI tools. Notation and answer keys are verified before release."
TITLE = "Music Symbols Scavenger Hunt"
LISTING_TITLE = "Music Symbols Scavenger Hunt, Find & Color Review Pages, Gr 3-5"
PRICE = "3.50"
TAGS = ["Winter", "Activities", "Printables", "Worksheets", "Games"]
SUBJECTS = ["Music"]
GRADES = ["3rd-grade", "4th-grade", "5th-grade"]

# ------------------------------------------------------------------ data
TEMPO = [  # term, say it, meaning, BPM range as commonly taught
    ("largo", "LAR-go", "very slow", "40–60"),
    ("andante", "ahn-DAHN-tay", "a walking speed", "76–108"),
    ("moderato", "mod-er-AH-toh", "a medium speed", "108–120"),
    ("allegro", "ah-LEG-roh", "fast and lively", "120–156"),
    ("presto", "PRES-toh", "very fast", "168–200"),
]
DYN = [  # sym id, term, say it, meaning
    ("p", "piano", "pee-AH-noh", "soft"),
    ("mp", "mezzo piano", "MET-soh pee-AH-noh", "medium soft"),
    ("mf", "mezzo forte", "MET-soh FOR-tay", "medium loud"),
    ("f", "forte", "FOR-tay", "loud"),
    ("cresc", "crescendo", "kreh-SHEN-doh", "gradually getting louder"),
    ("decresc", "decrescendo", "day-kreh-SHEN-doh", "gradually getting softer"),
]
SCENE_IDS = sorted(SC.SCENES)
for _n in SCENE_IDS:
    assert len(SC.SCENES[_n]["colors"]) == len(SC.SCENES[_n]["counts"])
PLACED = {n: SY.place(SC.SCENES[n]["counts"], SC.SCENES[n]["seed"], keepout=SC.KEEPOUT.get(n, ())) for n in SCENE_IDS}


def scene_total(n):
    return sum(c for _, c in SC.SCENES[n]["counts"])


def scene_types(n):
    return len(SC.SCENES[n]["counts"])


ALL_HIDDEN = sum(scene_total(n) for n in SCENE_IDS)
HUNT_POINTS = sum(scene_types(n) for n in SCENE_IDS)

# review pages
T_MEANS = ["very slow", "a walking speed", "a medium speed", "fast and lively", "very fast"]   # in TEMPO order
T_LETTERS = {"largo": "B", "andante": "D", "moderato": "E", "allegro": "A", "presto": "C"}   # printed meaning letters
T_SHUFFLE = ["presto", "largo", "moderato", "allegro", "andante"]
T_SCENARIOS = [("Racing to catch the last sled run", ("presto", "largo"), "presto"),
               ("A calm walk through the quiet snow", ("andante", "presto"), "andante"),
               ("Snow drifting down very slowly on a still night", ("largo", "allegro"), "largo"),
               ("A lively skating song with quick steps", ("allegro", "largo"), "allegro"),
               ("A medium-speed song for sipping cocoa", ("moderato", "presto"), "moderato")]
D_ORDER_SHUFFLE = ["mf", "p", "f", "mp"]
D_HAIRPINS = ["cresc", "decresc", "decresc", "cresc"]
D_WORDS = [("loud", "f"), ("soft", "p"), ("medium loud", "mf"), ("medium soft", "mp")]
T_POINTS = 5 + 5 + len(T_SCENARIOS)
D_POINTS = 6 + 4 + len(D_HAIRPINS) + len(D_WORDS)
REVIEW_POINTS = T_POINTS + D_POINTS
TOTAL_POINTS = HUNT_POINTS + REVIEW_POINTS

# pages
P_COVER, P_TEACH, P_KEY, P_VOCAB = 1, 2, 3, 4
P_TEMPO, P_DYN, P_SCORE, P_REVKEY, P_TERMS = 11, 12, 13, 20, 21
TOTAL_PAGES = P_TERMS


def p_scene(n): return 4 + n
def p_key(n): return 13 + n


PAGE_NAMES = {P_COVER: "cover", P_TEACH: "Teacher notes", P_KEY: "Symbol key", P_VOCAB: "Vocabulary",
              P_TEMPO: "Tempo review", P_DYN: "Dynamics review", P_SCORE: "Scoring and class record", P_REVKEY: "Review answer keys", P_TERMS: "Terms of use"}
for _n in SCENE_IDS:
    PAGE_NAMES[p_scene(_n)] = f"Scene {_n}: {SC.SCENES[_n]['title']}"
    PAGE_NAMES[p_key(_n)] = f"Answer key, scene {_n}: {SC.SCENES[_n]['title']}"
assert sorted(PAGE_NAMES) == list(range(1, TOTAL_PAGES + 1))
XREFS = []


def xref(frm, to, text):
    XREFS.append((frm, to, text))
    return text


# ------------------------------------------------------------------ CSS / frame
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
.top { display: flex; justify-content: space-between; align-items: flex-end; border-bottom: 2.2pt solid #000; padding-bottom: 6pt; }
.top .t { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; letter-spacing: .01em; line-height: 1; font-size: 18pt; white-space: nowrap; }
.top .t small { display: block; font-family: 'Oswald'; font-weight: 300; text-transform: none; font-size: 11pt; letter-spacing: 0; margin-top: 3pt; }
.top .tag { flex: none; white-space: nowrap; text-align: right; }
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
.doc td, .doc th { border: 1pt solid #000; padding: 3pt 6pt; text-align: left; vertical-align: middle; }
.doc th { font-family: 'Oswald'; font-weight: 500; text-transform: uppercase; font-size: 9.5pt; background: #000; color: #fff; }
.terms p, .terms li { font-size: 11.8pt !important; }
.small { font-size: 9pt !important; color: #333; }
.box { border: 1.3pt solid #000; border-radius: 7pt; padding: 7pt 10pt 4pt; margin: 6pt 0; }
.box h3 { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 12.5pt; margin: 0 0 3pt; letter-spacing: .02em; }
.box p { margin: 0 0 4pt !important; font-size: 10.4pt !important; }
.cols { display: flex; gap: 12pt; }
.cols .box { flex: 1; margin: 6pt 0; }
.nd { display: flex; align-items: flex-end; gap: 6pt; font-size: 10pt; margin: 7pt 0 0; }
.nd .ln { flex: 1; border-bottom: 1pt solid #000; height: 11pt; }
.stack { flex: 1; display: flex; flex-direction: column; justify-content: space-between; gap: 7pt; padding: 7pt 0 9pt; }
.inst { font-size: 10.4pt; line-height: 1.3; margin: 0; }
.scn { border: 0; line-height: 0; }
.scn svg { display: block; margin: 0 auto; }
.hunt { display: grid; grid-template-columns: 1fr 1fr; gap: 5pt 12pt; }
.hc { display: flex; align-items: center; gap: 7pt; border: 1.2pt solid #000; border-radius: 6pt; padding: 3pt 7pt; min-height: 40pt; }
.hc .sy { flex: none; width: 66pt; }
.hc .nm { flex: 1; font-weight: 700; font-size: 10.4pt; line-height: 1.12; }
.hc .co { flex: none; display: flex; align-items: center; gap: 4pt; font-family: 'Oswald'; font-weight: 500; font-size: 9.5pt; text-transform: uppercase; letter-spacing: .04em; width: 62pt; }
.sw { flex: none; display: inline-block; width: 15pt; height: 15pt; border-radius: 50%; border: 1.3pt solid #000; background: #fff; }
.hc .bx { flex: none; width: 30pt; height: 26pt; border: 1.3pt solid #000; border-radius: 4pt; text-align: center; font-family: 'Oswald'; font-weight: 700; font-size: 16pt; line-height: 23pt; }
.kgrid { display: grid; grid-template-columns: 1fr 1fr; gap: 0 14pt; flex: 1; align-content: space-between; padding: 4pt 0 6pt; }
.kc { display: flex; align-items: center; gap: 8pt; border-bottom: .8pt solid #999; padding: 0; }
.kc .ks { flex: none; width: 118pt; }
.kc .kt { font-size: 9.8pt; line-height: 1.18; }
.kc .kt b { display: block; font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 11pt; letter-spacing: .02em; margin-bottom: 1pt; }
.vsym svg { display: block; margin: 0 auto; }
.vt td.mid, .vt th.mid { text-align: center; }
.vt td { padding: 2pt 6pt !important; font-size: 9.6pt; }
.part { flex: 1; display: flex; flex-direction: column; justify-content: space-evenly; }
.mt.big li { font-size: 12pt; margin: 0 0 9pt; }
.chips.big .chip { font-size: 12pt; padding: 4pt 8pt; }
.part { border: 1.3pt solid #000; border-radius: 7pt; padding: 6pt 10pt 5pt; }
.part h3 { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 12.5pt; margin: 0 0 3pt; letter-spacing: .02em; }
.part h3 span { display: inline-block; background: ACCENT; color: #fff; border-radius: 3pt; padding: 0 6pt 1pt; margin-right: 6pt; font-size: 11pt; }
.part p { margin: 0 0 4pt; font-size: 10.2pt; line-height: 1.28; }
.two { display: flex; gap: 22pt; }
.two > div { flex: 1; }
.ln2 { display: inline-block; width: 34pt; border-bottom: 1pt solid #000; height: 13pt; vertical-align: bottom; text-align: center; font-family: 'Oswald'; font-weight: 700; color: ACCENT; }
.ln3 { display: inline-block; width: 100pt; border-bottom: 1pt solid #000; height: 13pt; vertical-align: bottom; font-weight: 700; color: ACCENT; text-align: center; }
.mt { margin: 0; padding: 0; list-style: none; }
.mt li { font-size: 10.6pt; line-height: 1.2; margin: 0 0 6pt; }
.mt li .lt { display: inline-block; width: 14pt; font-family: 'Oswald'; font-weight: 700; }
.chips { display: flex; flex-wrap: wrap; gap: 6pt 8pt; }
.chip { display: flex; align-items: center; gap: 5pt; border: 1.2pt solid #000; border-radius: 5pt; padding: 2pt 6pt; font-size: 10.4pt; }
.chip .nb { width: 20pt; height: 20pt; border: 1.2pt solid #000; border-radius: 4pt; text-align: center; font-family: 'Oswald'; font-weight: 700; line-height: 18pt; color: ACCENT; }
.opt { display: inline-block; border: 1.2pt solid #000; border-radius: 12pt; padding: 0 9pt 1pt; margin-left: 6pt; font-size: 10.2pt; }
.opt.on { background: ACCENT; border-color: ACCENT; color: #fff; font-weight: 700; }
.wb { border: 1.2pt dashed #000; border-radius: 6pt; padding: 3pt 8pt; font-size: 10pt; margin: 2pt 0 5pt; }
.cover { align-items: center; justify-content: space-between; padding: 0.55in 0.6in 0.5in; }
.store { font-family: 'Oswald'; font-weight: 500; font-size: 13pt; letter-spacing: .32em; text-transform: uppercase; }
.ctitle { text-align: center; }
.ctitle .a { font-family: 'Oswald'; font-weight: 700; font-size: 46pt; line-height: 1; letter-spacing: .02em; }
.ctitle .b { font-family: 'Oswald'; font-weight: 700; white-space: nowrap; font-size: 64pt; line-height: .95; letter-spacing: .01em; }
.ctitle .c { font-family: 'Oswald'; font-weight: 300; font-size: 17pt; margin-top: 8pt; }
.cband { width: 100%; background: #000; color: #fff; text-align: center; font-family: 'Oswald'; font-weight: 500; font-size: 14pt;
         letter-spacing: .08em; text-transform: uppercase; padding: 8pt 0 9pt; border-radius: 4pt; white-space: nowrap; }
.cband em { font-style: normal; color: ACCENT; }
""".replace("ACCENT", ACCENT)


def html_doc(pages, title="doc"):
    return (f'<!doctype html><html><head><meta charset="utf-8"><title>{escape(title)}</title><style>{font_css()}{CSS}</style></head>'
            f'<body>{"".join(pages)}</body></html>')


COPY = f"© {YEAR} {STORE} · {BRAND} · For single-classroom use"


def foot(left, right):
    return f'<div class="foot"><span>{left}</span><span>{right}</span></div>'


def wm_div(on):
    return '<div class="wm">PREVIEW</div>' if on else ""


def top_block(sub, tag, tagline, ak=False):
    return (f'<div class="top"><div class="t">{TITLE}<small>{sub}</small></div>'
            f'<div class="tag"><div class="lv{" ak" if ak else ""}">{tag}</div><div class="ln">{tagline}</div></div></div>')


def doc_head(h1, sub):
    return f'<div class="rule"><h1>{h1}</h1><div style="font-family:Oswald;font-weight:300;font-size:13pt">{sub}</div></div>'


NAME_DATE = '<div class="nd">Name <span class="ln"></span> Date <span class="ln" style="max-width:130pt;flex:none;width:130pt"></span></div>'


# ------------------------------------------------------------------ scene drawing
def scene_svg(n, key=False):
    sc = SC.SCENES[n]
    cid = f"clip{n}{'k' if key else ''}"
    hs = "".join(SY.sym_group(s, cx, cy, rot, S, down)[0] for s, cx, cy, rot, down, S, _ in PLACED[n])
    rings = ""
    if key:
        hexmap = {s: SC.COLOR_HEX[c] for (s, _), c in zip(sc["counts"], sc["colors"])}
        for s, cx, cy, rot, down, S, bb in PLACED[n]:
            ink = SY.aabb(s, cx, cy, rot, S, down, grow=0)
            rings += (f'<rect class="ring" data-sym="{s}" x="{ink[0] - 7:.2f}" y="{ink[1] - 7:.2f}" width="{ink[2] - ink[0] + 14:.2f}" height="{ink[3] - ink[1] + 14:.2f}" '
                      f'rx="9" fill="none" stroke="{hexmap[s]}" stroke-width="3.2"/>')
    return (f'<svg class="scene" data-scene="{n}" data-key="{1 if key else 0}" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {SC.W} {SC.H}" width="540pt" height="{540 * SC.H / SC.W:.2f}pt">'
            f'<defs><clipPath id="{cid}"><rect x="3.2" y="3.2" width="{SC.W - 6.4}" height="{SC.H - 6.4}" rx="12"/></clipPath></defs>'
            f'<g clip-path="url(#{cid})" {SC.BASE}>{sc["art"]()}</g>'
            f'<rect class="frame" x="2" y="2" width="{SC.W - 4}" height="{SC.H - 4}" rx="14" fill="none" stroke="#000" stroke-width="2.4"/>'
            f'<g class="hidden">{hs}</g>{rings}</svg>')


def hunt_cells(n, key=False):
    sc = SC.SCENES[n]
    out = ""
    for (s, cnt), col in zip(sc["counts"], sc["colors"]):
        sw = f'<span class="sw" style="background:{SC.COLOR_HEX[col]}"></span>' if key else '<span class="sw"></span>'
        box = f'<div class="bx" style="color:{ACCENT}">{cnt}</div>' if key else '<div class="bx"></div>'
        out += (f'<div class="hc" data-scene="{n}" data-sym="{s}" data-color="{col}"{f" data-count={chr(34)}{cnt}{chr(34)}" if key else ""}>'
                f'<div class="sy">{SY.sample_svg(s, 66, 34)}</div><div class="nm">{SY.SYMS[s][0]}</div>'
                f'<div class="co">{sw}{col}</div>{box}</div>')
    return f'<div class="hunt">{out}</div>'


def scene_page(n, wm=False):
    sc = SC.SCENES[n]
    inst = ("<b>Find and color.</b> Color the circle beside each symbol with its crayon. Hunt through the scene and circle every one you find in that color. "
            "Then count them and write the number in the box. Color the scene when you are done!")
    return (f'<section class="page doc" data-page="{p_scene(n)}">{wm_div(wm)}{top_block(f"Scene {n}: {sc["title"]}", f"SCENE {n}", f"{scene_types(n)} kinds of symbols")}{NAME_DATE}'
            f'<div class="stack"><p class="inst">{inst}</p><div class="scn">{scene_svg(n)}</div>{hunt_cells(n)}</div>'
            f'{foot(COPY, f"Page {p_scene(n)} · " + xref(p_scene(n), p_key(n), f"Answer key on page {p_key(n)}"))}</section>')


def key_page(n, wm=False):
    sc = SC.SCENES[n]
    tot = scene_total(n)
    note = (f"<b>Answer key.</b> Every hidden symbol is circled in its color. The numbers show how many of each symbol are hidden. "
            f"<b data-total=\"{n}\">Total hidden symbols: {tot}</b>. Each correct count is worth 1 point ({scene_types(n)} points for this scene).")
    return (f'<section class="page doc" data-page="{p_key(n)}">{wm_div(wm)}{top_block(f"Answer key, scene {n}: {sc["title"]}", "ANSWER KEY", f"{scene_types(n)} kinds of symbols", ak=True)}'
            f'<div class="stack"><p class="inst">{note}</p><div class="scn">{scene_svg(n, True)}</div>{hunt_cells(n, True)}</div>'
            f'{foot(COPY, f"Page {p_key(n)} · " + xref(p_key(n), p_scene(n), f"Student page {p_scene(n)}"))}</section>')


# ------------------------------------------------------------------ the symbol key (symbols on a staff)
KS_W, KS_H, KS_S, KS_MID = 118.0, 56.0, 6.5, 28.0


def ln_y(i):  # i = 0 bottom line ... 4 top line
    return KS_MID + (2 - i) * KS_S


def key_staff(sym):
    """A symbol on a five-line staff at the correct position. Returns an svg string."""
    S = KS_S
    sl = "".join(f'<line class="sl" x1="3" y1="{ln_y(i):.2f}" x2="{KS_W - 3}" y2="{ln_y(i):.2f}" stroke="#000" stroke-width="0.9"/>' for i in range(5))

    def g(s, x, y, down=False):
        pts = SY.parts(s, down)
        return (f'<g class="smp" data-sym="{s}" data-s="{S}" data-down="{1 if down else 0}" transform="translate({x:.2f} {y:.2f})">'
                f'<g class="ink">{SY.svg_parts(pts, S, "fill=" + chr(34) + "#000" + chr(34))}</g></g>')
    body = ""
    if sym == "treble": body = g("treble", 8, ln_y(1))
    elif sym == "bass": body = g("bass", 8, ln_y(3))
    elif sym in ("quarter", "half"):
        body = g(sym, 38, ln_y(1)) + g(sym, 74, ln_y(3), True)       # below the middle line: stem up; above it: stem down
    elif sym == "whole": body = g("whole", 46, (ln_y(2) + ln_y(3)) / 2)
    elif sym == "qrest": body = g("qrest", 52, KS_MID)
    elif sym == "hrest": body = g("hrest", 50, KS_MID)
    elif sym == "repeat": body = g("repeat", 90, ln_y(0))
    elif sym == "fermata": body = g("whole", 46, (ln_y(2) + ln_y(3)) / 2) + g("fermata", 46 + (1.688 - 2.42) / 2 * S, ln_y(4) - 0.5 * S)
    elif sym in ("sharp", "flat", "natural"): body = g(sym, 38, KS_MID) + g("quarter", 52, KS_MID, True)
    elif sym == "ts44": body = g("ts44", 52, KS_MID)
    elif sym == "dbl": body = g("dbl", 90, ln_y(0))
    return (f'<svg class="ks" data-cell="{sym}" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {KS_W} {KS_H}" width="{KS_W}pt" height="{KS_H}pt" style="display:block">{sl}{body}</svg>')


KEY_ON_STAFF = {"treble", "bass", "quarter", "half", "whole", "qrest", "hrest", "repeat", "fermata", "sharp", "flat", "natural", "ts44", "dbl"}


def key_cell_svg(sym):
    return key_staff(sym) if sym in KEY_ON_STAFF else SY.sample_svg(sym, KS_W, KS_H)


def key_cells():
    out = ""
    for s in SY.ORDER:
        name, meaning, _ = SY.SYMS[s]
        out += f'<div class="kc" data-sym="{s}"><div class="ks">{key_cell_svg(s)}</div><div class="kt"><b>{name}</b>{meaning}</div></div>'
    return out


def symbol_key_page(wm=False):
    return (f'<section class="page doc" data-page="{P_KEY}">{wm_div(wm)}{top_block("Symbol key", "REFERENCE", "20 symbols")}'
            f'<div class="kgrid">{key_cells()}</div>'
            f'<p class="small" style="margin:0 0 9pt">In the scenes the symbols hide without a staff. Stems go up on the right of the head below the middle line, and down on the left on or above it.</p>'
            f'{foot(COPY, f"Page {P_KEY}")}</section>')


# ------------------------------------------------------------------ vocabulary
WORDS = [("Tempo", "How fast or slow the music goes."), ("Dynamics", "How loud or soft the music is."),
         ("Clef", "A symbol at the start of the staff that tells you the names of the lines and spaces."),
         ("Rest", "A symbol for silence. It has a length, just like a note."), ("Accidental", "A sharp, flat or natural sign written before a note."),
         ("Time signature", "Two numbers at the start of the music. In 4/4 there are four beats in a bar, and a quarter note gets one beat."),
         ("Barline", "A vertical line that divides the music into bars. A double barline marks the end of a section."),
]


def vocab_page(wm=False):
    trows = "".join(f'<tr data-term="{t}" data-meaning="{m}" data-bpm="{b}"><td><b>{t}</b></td><td>{say}</td><td>{m}</td><td class="mid">about {b}</td></tr>' for t, say, m, b in TEMPO)
    drows = "".join(f'<tr data-term="{t}" data-meaning="{m}"><td class="vsym">{SY.sample_svg(s, 70, 26)}</td><td><b>{t}</b></td><td>{say}</td><td>{m}</td></tr>' for s, t, say, m in DYN)
    wrows = "".join(f'<tr><td><b>{w}</b></td><td colspan="3">{d}</td></tr>' for w, d in WORDS)
    return (f'<section class="page doc" data-page="{P_VOCAB}">{wm_div(wm)}{top_block("Vocabulary", "REFERENCE", "Italian terms and music words")}'
            f'<div class="stack" style="justify-content:flex-start;gap:3pt">'
            f'<h2 style="margin-top:2pt">Tempo terms</h2>'
            f'<table class="vt"><tr><th style="width:22%">Term</th><th style="width:27%">Say it</th><th style="width:27%">Meaning</th><th class="mid">Speed</th></tr>{trows}</table>'
            f'<p class="small" style="margin:0">BPM means beats per minute. These are common ranges. Books, teachers and conductors use slightly different numbers.</p>'
            f'<h2>Dynamics</h2>'
            f'<table class="vt"><tr><th style="width:22%">Symbol</th><th style="width:27%">Term</th><th style="width:27%">Say it</th><th>Meaning</th></tr>{drows}</table>'
            f'<p class="small" style="margin:0">The letter <i>m</i> in mp and mf stands for <i>mezzo</i>, which means &ldquo;medium.&rdquo; The words are Italian.</p>'
            f'<h2>Music words</h2><table class="vt"><tr><th style="width:22%">Word</th><th colspan="3">What it means</th></tr>{wrows}</table></div>'
            f'{foot(COPY, f"Page {P_VOCAB}")}</section>')


# ------------------------------------------------------------------ review pages
def tempo_data():
    items = []
    for i, (t, say, m, b) in enumerate(TEMPO):
        items.append((t, T_LETTERS[t], m, b))
    return items


def tempo_order_answer():
    low = {t: int(b.split("–")[0]) for t, _, _, b in TEMPO}
    ranked = sorted(low, key=low.get)
    return {t: ranked.index(t) + 1 for t in low}


D_RANK = {"p": 1, "mp": 2, "mf": 3, "f": 4}
D_TERM = {s: t for s, t, _, _ in DYN}
D_MEAN = {s: m for s, _, _, m in DYN}


def tempo_review(key=False, wm=False):
    ans = tempo_order_answer()
    letters = sorted(T_LETTERS.values())
    meaning_of = {T_LETTERS[t]: m for t, _, m, _ in TEMPO}
    left = "".join(f'<li data-term="{t}" data-ans="{T_LETTERS[t]}"><span class="lt">{i + 1}.</span> <b>{t}</b> <span class="ln2">{T_LETTERS[t] if key else ""}</span></li>' for i, (t, _, _, _) in enumerate(TEMPO))
    right = "".join(f'<li data-letter="{L}" data-meaning="{meaning_of[L]}"><span class="lt">{L}.</span> {meaning_of[L]}</li>' for L in letters)
    chips = "".join(f'<div class="chip" data-term="{t}" data-bpm="{dict((a, d) for a, _, _, d in TEMPO)[t]}" data-ans="{ans[t]}"><span class="nb">{ans[t] if key else ""}</span><b>{t}</b> (about {dict((a, d) for a, _, _, d in TEMPO)[t]} BPM)</div>' for t in T_SHUFFLE)
    sc = ""
    for i, (txt, opts, correct) in enumerate(T_SCENARIOS):
        o = "".join(f'<span class="opt{" on" if key and x == correct else ""}">{x}</span>' for x in opts)
        sc += f'<li data-scn="{i + 1}" data-ans="{correct}"><span class="lt">{i + 1}.</span> {txt}.{o}</li>'
    head = ("Answer key" if key else "Tempo review")
    return (f'<section class="page doc" data-page="{P_TEMPO}">{wm_div(wm)}{top_block("Tempo review", "REVIEW", f"{T_POINTS} points")}{NAME_DATE}'
            f'<div class="stack" style="padding-top:9pt">'
            f'<div class="part"><h3><span>A</span>Match each tempo word to its meaning</h3><p>Write the letter of the meaning on the line.</p>'
            f'<div class="two"><ul class="mt big">{left}</ul><ul class="mt big">{right}</ul></div></div>'
            f'<div class="part"><h3><span>B</span>Order the tempo words</h3><p>Use the BPM clues. Write 1 for the slowest and 5 for the fastest.</p><div class="chips big">{chips}</div></div>'
            f'<div class="part"><h3><span>C</span>Which tempo fits?</h3><p>Circle the better tempo word.</p><ul class="mt big" style="margin-top:3pt">{sc}</ul></div>'
            f'</div>{foot(COPY, f"Page {P_TEMPO} · " + xref(P_TEMPO, P_REVKEY, f"Answer key on page {P_REVKEY}"))}</section>')


def dyn_review(wm=False):
    rows = "".join(f'<tr data-sym="{s}"><td class="vsym" style="width:90pt">{SY.sample_svg(s, 70, 22)}</td><td><span class="ln3"></span></td></tr>' for s in ["f", "cresc", "p", "decresc", "mp", "mf"])
    bank = " &nbsp;·&nbsp; ".join(f"<b>{t}</b>" for t in ["piano", "mezzo piano", "mezzo forte", "forte", "crescendo", "decrescendo"])
    chips = "".join(f'<div class="chip"><span class="nb"></span>{SY.sample_svg(s, 52, 22, inline=True)}</div>' for s in D_ORDER_SHUFFLE)
    hp = "".join(f'<li><span class="lt">{i + 1}.</span> {SY.sample_svg(s, 56, 18, inline=True)} <span class="opt">gets louder</span><span class="opt">gets softer</span></li>' for i, s in enumerate(D_HAIRPINS))
    ws = "".join(f'<li><span class="lt">{i + 1}.</span> <b>{w}</b> <span class="ln2"></span></li>' for i, (w, s) in enumerate(D_WORDS))
    return (f'<section class="page doc" data-page="{P_DYN}">{wm_div(wm)}{top_block("Dynamics review", "REVIEW", f"{D_POINTS} points")}{NAME_DATE}'
            f'<div class="stack" style="padding-top:9pt">'
            f'<div class="part"><h3><span>A</span>Name the dynamic</h3><p>Write the Italian word for each symbol.</p><div class="wb">Word bank: {bank}</div>'
            f'<table style="width:100%;border-collapse:collapse;table-layout:fixed"><tr><td style="width:50%;vertical-align:top;border:0;padding:0"><table class="d2" style="width:100%">{"".join(rows.split("</tr>")[i] + "</tr>" for i in (0, 1, 2))}</table></td>'
            f'<td style="vertical-align:top;border:0;padding:0 0 0 14pt"><table class="d2" style="width:100%">{"".join(rows.split("</tr>")[i] + "</tr>" for i in (3, 4, 5))}</table></td></tr></table></div>'
            f'<div class="part"><h3><span>B</span>Quiet to loud</h3><p>Write 1 in the box by the quietest symbol and 4 in the box by the loudest.</p><div class="chips">{chips}</div></div>'
            f'<div class="part"><h3><span>C</span>Louder or softer?</h3><p>Circle what each hairpin tells you to do.</p><ul class="mt" style="margin-top:3pt">{hp}</ul></div>'
            f'<div class="part"><h3><span>D</span>Write the letters</h3><p>Write p, mp, mf or f to match each word.</p><ul class="mt" style="margin-top:3pt">{ws}</ul></div>'
            f'</div>{foot(COPY, f"Page {P_DYN} · " + xref(P_DYN, P_REVKEY, f"Answer key on page {P_REVKEY}"))}</section>')


def review_key_page(wm=False):
    ans = tempo_order_answer()
    meaning_of = {T_LETTERS[t]: m for t, _, m, _ in TEMPO}
    ta = "".join(f'<tr data-term="{t}" data-ans="{T_LETTERS[t]}"><td><b>{i + 1}. {t}</b></td><td class="mid">{T_LETTERS[t]}</td><td>{meaning_of[T_LETTERS[t]]}</td></tr>' for i, (t, _, _, _) in enumerate(TEMPO))
    tb = "".join(f'<tr data-term="{t}" data-rank="{ans[t]}"><td>{t}</td><td class="mid">{ans[t]}</td></tr>' for t in T_SHUFFLE)
    tc = "".join(f'<tr data-scn="{i + 1}" data-ans="{c}"><td>{i + 1}. {txt}</td><td><b>{c}</b></td></tr>' for i, (txt, _, c) in enumerate(T_SCENARIOS))
    da = "".join(f'<tr data-sym="{s}"><td class="vsym" style="width:60pt">{SY.sample_svg(s, 52, 20)}</td><td><b>{D_TERM[s]}</b></td></tr>' for s in ["f", "cresc", "p", "decresc", "mp", "mf"])
    db = "".join(f'<tr data-sym="{s}" data-rank="{D_RANK[s]}"><td class="vsym" style="width:60pt">{SY.sample_svg(s, 52, 20)}</td><td class="mid">{D_RANK[s]}</td></tr>' for s in D_ORDER_SHUFFLE)
    dc = "".join(f'<tr data-sym="{s}" data-ans="{"louder" if s == "cresc" else "softer"}"><td>{i + 1}.</td><td class="vsym" style="width:60pt">{SY.sample_svg(s, 52, 20)}</td><td><b>gets {"louder" if s == "cresc" else "softer"}</b></td></tr>' for i, s in enumerate(D_HAIRPINS))
    dd = "".join(f'<tr data-word="{w}" data-ans="{s}"><td>{i + 1}. {w}</td><td class="mid"><b>{s}</b></td></tr>' for i, (w, s) in enumerate(D_WORDS))
    return (f'<section class="page doc" data-page="{P_REVKEY}">{wm_div(wm)}{top_block("Review answer keys", "ANSWER KEY", f"{REVIEW_POINTS} points", ak=True)}'
            f'<div class="stack" style="justify-content:flex-start;gap:2pt">'
            f'<h2 style="margin-top:3pt">Tempo review (page {P_TEMPO}): {T_POINTS} points</h2>'
            f'<div class="two"><div><p class="small" style="margin:0"><b>A.</b> Letters</p><table class="vt"><tr><th>Word</th><th class="mid" style="width:30pt">Ans.</th><th>Meaning</th></tr>{ta}</table></div>'
            f'<div><p class="small" style="margin:0"><b>B.</b> Order, 1 = slowest</p><table class="vt"><tr><th>Word</th><th class="mid" style="width:40pt">Number</th></tr>{tb}</table>'
            f'<p class="small" style="margin:3pt 0 0"><b>C.</b> Which tempo fits?</p></div></div>'
            f'<table class="vt">{tc}</table>'
            f'<h2>Dynamics review (page {P_DYN}): {D_POINTS} points</h2>'
            f'<div class="two"><div><p class="small" style="margin:0"><b>A.</b> Names</p><table class="vt">{da}</table></div>'
            f'<div><p class="small" style="margin:0"><b>B.</b> Quiet to loud</p><table class="vt">{db}</table>'
            f'<p class="small" style="margin:3pt 0 0"><b>D.</b> Letters</p><table class="vt">{dd}</table></div></div>'
            f'<p class="small" style="margin:0"><b>C.</b> Louder or softer</p><table class="vt">{dc}</table></div>'
            f'{foot(COPY, f"Page {P_REVKEY}")}</section>')


# ------------------------------------------------------------------ teacher notes, score page, terms
def pct_bands():
    hi = math.ceil(0.9 * TOTAL_POINTS)
    mid = math.ceil(0.7 * TOTAL_POINTS)
    return hi, mid


def teacher_page(wm=False):
    hi, mid = pct_bands()
    kinds = ", ".join(f"scene {n} ({scene_total(n)})" for n in SCENE_IDS)
    pacing = [("Lesson 1 (15 min)", f"Study the symbol key (page {P_KEY}) and the vocabulary (page {P_VOCAB}). Students say each symbol name and its meaning aloud.", f"{P_KEY}–{P_VOCAB}"),
              ("Lesson 2 (20 min)", "Scenes 1 and 2: notes, clefs and rests, then rests, repeat signs and fermatas.", f"{p_scene(1)}–{p_scene(2)}"),
              ("Lesson 3 (20 min)", "Scenes 3 and 4: accidentals and time signatures, then dynamics and hairpins.", f"{p_scene(3)}–{p_scene(4)}"),
              ("Lesson 4 (20 min)", "Scenes 5 and 6, the challenge scenes with ten kinds of symbols each.", f"{p_scene(5)}–{p_scene(6)}"),
              ("Lesson 5 (20 min)", f"Tempo and dynamics review, then scoring (page {P_SCORE}).", f"{P_TEMPO}–{P_SCORE}")]
    prow = "".join(f'<tr><td><b>{a}</b></td><td>{b}</td><td class="mid">{c}</td></tr>' for a, b, c in pacing)
    return (f'<section class="page doc" data-page="{P_TEACH}">{wm_div(wm)}{doc_head("Teacher Notes", "How to use this scavenger hunt")}'
            f'<p>Students hunt through six scenes for hidden music symbols. They find each symbol, circle it in a color, count it and write the number. '
            f'Then they review tempo terms and dynamics. Every scene has an answer key that circles each symbol, and every review has a key too.</p>'
            f'<div class="cols"><div class="box"><h3>Quick start</h3>'
            f'<p>1. Copy the symbol key (page {P_KEY}) and vocabulary (page {P_VOCAB}) for each student.</p>'
            f'<p>2. Hand out a scene page and crayons in several colors.</p>'
            f'<p>3. Students color a circle beside each symbol, then circle the symbols in the scene with that crayon.</p>'
            f'<p>4. They count and write the numbers, then check with the key.</p></div>'
            f'<div class="box"><h3>What is inside ({TOTAL_PAGES} pages)</h3>'
            f'<p>{xref(P_TEACH, P_KEY, f"Page {P_KEY}")}: symbol key. {xref(P_TEACH, P_VOCAB, f"Page {P_VOCAB}")}: vocabulary.</p>'
            f'<p>Pages {p_scene(1)}–{p_scene(6)}: six scenes with {ALL_HIDDEN} hidden symbols ({kinds}).</p>'
            f'<p>Pages {P_TEMPO}–{P_DYN}: tempo and dynamics review. Page {P_SCORE}: scoring.</p>'
            f'<p>Pages {p_key(1)}–{p_key(6)}: scene answer keys. Page {P_REVKEY}: review keys. Page {P_TERMS}: terms of use.</p></div></div>'
            f'<h2>Pacing</h2><table class="vt"><tr><th style="width:24%">Lesson</th><th>Plan</th><th class="mid" style="width:60pt">Pages</th></tr>{prow}</table>'
            f'<h2>Tips</h2><ul><li>The scenes get harder. Scenes 1 and 2 have seven kinds of symbols each and scenes 5 and 6 have ten, so you can match the scene to the student.</li>'
            f'<li>The hidden symbols are printed in black and are drawn without a staff. Some notes have stems down and some have stems up. The symbol key shows each symbol on a staff.</li>'
            f'<li>Black-and-white printing works: every color is also written as a word. Students can circle with a pencil and write the color name instead.</li>'
            f'<li>If a count is off by one, ask the student to look again near the edges of the picture and behind the line art.</li></ul>'
            f'<h2>Standards and ideas</h2><p>The hunt supports reading and naming notation, tempo terms and dynamics, as described in the National Core Arts Standards for Music. '
            f'Match the wording to your own curriculum. For extra practice, students can clap or play a short pattern in the tempo or dynamic that a symbol shows. '
            f'No songs, lyrics or copyrighted characters are used.</p>'
            f'<div style="flex:1"></div>{foot(COPY, f"Page {P_TEACH}")}</section>')


def score_page(wm=False):
    hi, mid = pct_bands()
    rows = "".join(f'<tr data-pts="{scene_types(n)}"><td>Scene {n}: {SC.SCENES[n]["title"]}</td><td class="mid">{scene_types(n)}</td><td class="mid">page {p_scene(n)}</td><td class="mid">key {p_key(n)}</td><td class="mid">____ / {scene_types(n)}</td></tr>' for n in SCENE_IDS)
    return (f'<section class="page doc" data-page="{P_SCORE}">{wm_div(wm)}{top_block("Scoring and class record", "SCORING", f"{TOTAL_POINTS} points")}{NAME_DATE}'
            f'<div class="stack" style="justify-content:flex-start;gap:5pt;padding-top:9pt">'
            f'<h2 style="margin-top:0">How to score</h2>'
            f'<p>On each scene, a student earns <b>1 point for every kind of symbol that is counted correctly</b>. The score for a scene is the number of kinds of symbols on its hunt list. '
            f'The tempo review is worth {T_POINTS} points and the dynamics review is worth {D_POINTS} points. Use the answer keys on pages {p_key(1)}–{P_REVKEY}.</p>'
            f'<table class="vt" data-total="{TOTAL_POINTS}"><tr><th>Part</th><th class="mid" style="width:48pt">Points</th><th class="mid" style="width:56pt">Student</th><th class="mid" style="width:56pt">Key</th><th class="mid" style="width:80pt">My score</th></tr>{rows}'
            f'<tr data-pts="{T_POINTS}"><td>Tempo review</td><td class="mid">{T_POINTS}</td><td class="mid">page {P_TEMPO}</td><td class="mid">key {P_REVKEY}</td><td class="mid">____ / {T_POINTS}</td></tr>'
            f'<tr data-pts="{D_POINTS}"><td>Dynamics review</td><td class="mid">{D_POINTS}</td><td class="mid">page {P_DYN}</td><td class="mid">key {P_REVKEY}</td><td class="mid">____ / {D_POINTS}</td></tr>'
            f'<tr><td><b>Total</b></td><td class="mid"><b>{TOTAL_POINTS}</b></td><td></td><td></td><td class="mid"><b>____ / {TOTAL_POINTS}</b></td></tr></table>'
            f'<h2>Rubric</h2><table class="vt"><tr><th style="width:26%">Level</th><th style="width:22%">Points</th><th>What it looks like</th></tr>'
            f'<tr><td><b>Symbol Expert</b></td><td>{hi}–{TOTAL_POINTS}</td><td>Names symbols quickly, counts accurately and knows the tempo and dynamics words.</td></tr>'
            f'<tr><td><b>Symbol Finder</b></td><td>{mid}–{hi - 1}</td><td>Finds most symbols and knows most of the words. Needs another look at a few.</td></tr>'
            f'<tr><td><b>Still Hunting</b></td><td>0–{mid - 1}</td><td>Needs more time with the symbol key and vocabulary before trying again.</td></tr></table>'
            f'<h2>I can...</h2><ul style="list-style:none;padding:0;margin:0 0 4pt">'
            + "".join(f'<li style="margin:0 0 5pt">&#9744; {t}</li>' for t in ["name the clefs, notes and rests", "find sharps, flats and naturals", "recognize a repeat sign, a fermata and a double barline",
                                                                          "read a 4/4 time signature", "tell the dynamics from soft to loud", "put tempo words in order from slow to fast"]) +
            f'</ul><p class="small" style="margin:0">Teacher check: ____________________ &nbsp; Date: ____________</p></div>'
            f'{foot(COPY, f"Page {P_SCORE}")}</section>')


def terms_page(wm=False):
    return (f'<section class="page doc terms" data-page="{P_TERMS}">{wm_div(wm)}{doc_head("Terms of Use", "Thank you for your purchase!")}'
            f'<p>© {YEAR} {STORE}. {BRAND} by {STORE}. All rights reserved. This purchase gives <b>one teacher</b> a license to use this resource with their own students.</p>'
            f'<h2>You may</h2><ul><li>Print and copy pages for your own classroom and students, year after year.</li>'
            f'<li>Share pages with your own students through a password-protected class site or learning platform.</li>'
            f'<li>Use the pages with your own students when you have a substitute teacher.</li></ul>'
            f'<h2>You may not</h2><ul><li>Share, email or copy this resource for other teachers, a whole school or a district. Additional licenses are available on Teachers Pay Teachers.</li>'
            f'<li>Post any part of it on a public website, shared drive or social media.</li>'
            f'<li>Sell, give away or claim any part of it as your own, or edit it into a new product.</li></ul>'
            f'<h2>Questions?</h2><p>Please use the Q&amp;A tab on the {BRAND} by {STORE} store on Teachers Pay Teachers. If something looks wrong, let me know there and I will fix it.</p>'
            f'<h2>Credits</h2><ul>'
            f'<li>The scenes, hidden symbols, hunt lists, reviews and answer keys are original work, {BRAND} by {STORE}.</li>'
            f'<li>The cover illustration is made with AI tools. The scenes, notation, tables and text are drawn in code.</li>'
            f'<li>Music notation font: Bravura © Steinberg Media Technologies GmbH, SIL Open Font License 1.1.</li>'
            f'<li>Text fonts: Oswald (The Oswald Project Authors) and Source Sans 3 (Adobe), SIL Open Font License 1.1.</li></ul>'
            f'<h2>Printing tips</h2><ul><li>Print the scene pages and review pages single-sided. Color or black and white both work.</li>'
            f'<li>Keep the answer keys for yourself. Copy only the student pages, so students never see the answers.</li></ul>'
            f'<h2>What is in this file ({TOTAL_PAGES} pages)</h2><p>Page 1 cover, page {P_TEACH} teacher notes, page {P_KEY} symbol key, page {P_VOCAB} vocabulary, pages {p_scene(1)}–{p_scene(6)} the six scenes, '
            f'pages {P_TEMPO}–{P_DYN} the reviews, page {P_SCORE} scoring, pages {p_key(1)}–{P_REVKEY} the answer keys and page {P_TERMS} these terms.</p>'
            f'<p class="small">{DISCLOSURE}</p><div style="flex:1"></div>{foot(COPY, f"Page {P_TERMS}")}</section>')


def cover_art_img(height):
    return f'<img src="../art/hero.png" alt="" style="display:block;height:{height};width:auto">'


def cover_page():
    return (f'<section class="page cover"><div class="store">{BRAND}</div>'
            f'<div style="height:4.5in;display:flex;align-items:center;justify-content:center">{cover_art_img("4.5in")}</div>'
            f'<div class="ctitle"><div class="a">MUSIC SYMBOLS</div><div class="b">SCAVENGER HUNT</div>'
            f'<div class="c">Find, circle and color · tempo and dynamics review · answer keys</div></div>'
            f'<div class="cband">Grades 3–5 <em>·</em> 6 scenes <em>·</em> {TOTAL_PAGES} pages</div></section>')


def full_pages():
    XREFS.clear()
    pages = [cover_page(), teacher_page(), symbol_key_page(), vocab_page()]
    pages += [scene_page(n) for n in SCENE_IDS]
    pages += [tempo_review(), dyn_review(), score_page()]
    pages += [key_page(n) for n in SCENE_IDS]
    pages += [review_key_page(), terms_page()]
    assert len(pages) == TOTAL_PAGES, len(pages)
    return pages


PREVIEW_PAGES = [p_scene(1), P_KEY, P_TEMPO, p_key(3)]


def preview_pages():
    return [scene_page(1, True), symbol_key_page(True), tempo_review(wm=True), key_page(3, True)]


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
.pill { border: 2px solid #000; border-radius: 30px; padding: 6px 22px; font-family: Oswald; font-weight: 500; font-size: 24px; letter-spacing: .06em; text-transform: uppercase; white-space: nowrap; }
""".replace("ACCENT", ACCENT)


def sq_doc(body):
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{font_css()}html,body{{margin:0;background:#fff;font-family:"Source Sans 3",sans-serif}}{SQ_CSS}</style></head><body>'
            f'{body}</body></html>')


def cover_square():
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div>'
        f'<div style="flex:1;display:flex;flex-direction:column;justify-content:space-evenly;align-items:center;width:100%;padding:0 0 76px">'
        f'<div style="height:520px;display:flex;align-items:center;margin:-10px 0 -20px">{cover_art_img("640px")}</div>'
        f'<div><div class="hd" style="font-size:74px">Music Symbols</div><div class="hd" style="font-size:112px">Scavenger Hunt</div>'
        f'<div class="sub" style="font-size:28px;margin-top:12px">Find, circle and color · tempo and dynamics review · answer keys</div></div>'
        f'</div><div class="band">Grades 3–5 <em>·</em> 6 scenes <em>·</em> {TOTAL_PAGES} pages</div></div>')


def swm_over(size=230):
    return f'<div class="swm" style="font-size:{size}px">PREVIEW</div>'


def shot(src, w):
    return f'<div class="shot" style="width:{w}px"><img src="{src}"></div>'


def pill_row(items):
    return '<div style="display:flex;gap:18px">' + "".join(f'<div class="pill">{t}</div>' for t in items) + "</div>"


def trio(img, caps, head, sub, pills, bandtxt):
    shots = "".join(
        f'<div style="width:290px;display:flex;flex-direction:column;align-items:center">{shot(img[i], 290)}'
        f'<div class="lbl" style="font-size:22px;margin-top:20px">{caps[i][0]}</div>'
        f'<div style="font-family:Oswald;font-weight:300;font-size:20px;line-height:1.25;text-align:center;margin-top:8px;width:270px">{caps[i][1]}</div></div>' for i in range(3))
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div><div class="hd" style="font-size:72px;margin-top:28px">{head}</div>'
        f'<div class="sub" style="font-size:28px;margin-top:10px">{sub}</div>'
        f'<div style="flex:1;display:flex;flex-direction:column;align-items:center;justify-content:space-evenly;padding-bottom:70px">'
        f'<div style="display:flex;gap:22px;align-items:flex-start">{shots}</div>{pill_row(pills)}</div>'
        f'{swm_over(230)}<div class="band">{bandtxt}</div></div>')


def preview_square_1(img):
    caps = [(PAGE_NAMES[p_scene(1)], "Find, circle and count"), (PAGE_NAMES[P_KEY], "Twenty symbols with meanings"), (PAGE_NAMES[P_TEMPO], "Italian tempo terms")]
    return trio(img, caps, "What is inside", "Six scenes, two reviews and answer keys", ["6 scenes", f"{ALL_HIDDEN} hidden symbols", "Answer keys"],
                "Find <em>·</em> Circle <em>·</em> Count <em>·</em> Review")


def preview_square_2(a, b):
    pair = "".join(f'<div style="width:380px">{shot(src, 380)}<div class="lbl">{lab}<span>{sub}</span></div></div>'
                   for src, lab, sub in ((a, PAGE_NAMES[p_scene(3)], "Hidden symbols, hunt list and count boxes"), (b, PAGE_NAMES[p_key(3)], "Every symbol circled in its color")))
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div><div class="hd" style="font-size:72px;margin-top:24px">Hunt page and key</div>'
        f'<div class="sub" style="font-size:27px;margin-top:8px">Every scene has a matching answer key</div>'
        f'<div style="flex:1;display:flex;align-items:center;padding-bottom:70px"><div style="display:flex;gap:44px;align-items:flex-start">{pair}</div></div>'
        f'{swm_over(230)}<div class="band">6 scenes <em>·</em> {ALL_HIDDEN} hidden symbols <em>·</em> 6 answer keys</div></div>')


def preview_square_3(img):
    caps = [(PAGE_NAMES[P_DYN], "Dynamics from soft to loud"), (PAGE_NAMES[P_REVKEY], "Both reviews answered"), (PAGE_NAMES[P_SCORE], "Points, rubric and class record")]
    return trio(img, caps, "Reviews and scoring", "Grades 3–5", [f"{REVIEW_POINTS} review points", f"{TOTAL_POINTS} points in all"],
                "Tempo <em>·</em> Dynamics <em>·</em> Scoring")


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


PAGE_LIST = [("Cover", 1), ("Teacher notes", 1), ("Symbol key", 1), ("Vocabulary", 1), ("Six scene pages with hunt lists", 6), ("Tempo review", 1),
             ("Dynamics review", 1), ("Scoring and class record", 1), ("Six scene answer keys", 6), ("Review answer keys", 1), ("Terms of use and credits", 1)]
assert sum(c for _, c in PAGE_LIST) == TOTAL_PAGES


def upload_md():
    lst = "\n".join(f"- {n}: {c}" for n, c in PAGE_LIST)
    scenes_txt = ", ".join(f"{SC.SCENES[n]['title']}" for n in SCENE_IDS)
    return f"""# UPLOAD: {LISTING_TITLE} (TpT 066)

These fields follow the order of TpT's "Add a resource" form. Winter-themed content, non-religious; the title leaves out seasonal words.

**Files to attach**
- Resource (digital download): `{SLUG}.pdf`, {TOTAL_PAGES} pages, US Letter.
- Thumbnails, in this order: `cover.png`, `preview-1.png`, `preview-2.png`, `preview-3.png` (all 2000 × 2000).
- Preview file: `{SLUG}-PREVIEW.pdf`, 4 watermarked pages.

## 1. Title

```
{LISTING_TITLE}
```
({len(LISTING_TITLE)} characters; the limit is 80.) Plain search words first, no seasonal words in the title.

## 2. Description

```
Music Symbols Scavenger Hunt gives your students six snowy, kid-friendly scenes with music symbols hidden all over them. Students find each symbol, circle it in a color, count how many there are and write the number. Then they review tempo terms and dynamics on two review pages. Every scene and every review has an answer key, so checking takes minutes. The scenes are winter themed and non-religious (snow, skates, cocoa and mittens), so they fit every school calendar.

SIX SCENES: {scenes_txt}. Scenes 1 and 2 have seven kinds of symbols each, scenes 3 and 4 have seven or eight, and scenes 5 and 6 are challenge scenes with ten kinds each. There are {ALL_HIDDEN} hidden symbols in all.

SYMBOLS: treble clef, bass clef, quarter note, half note, whole note, quarter rest, half rest, repeat sign, fermata, sharp, flat, natural, forte (f), piano (p), mezzo forte (mf), mezzo piano (mp), crescendo, decrescendo, 4/4 time signature and double barline. The symbols are drawn in notation style, and a symbol key page shows each one on a staff with its meaning.

TEMPO AND DYNAMICS REVIEW: largo, andante, moderato, allegro and presto with common BPM ranges; piano, mezzo piano, mezzo forte, forte, crescendo and decrescendo with their meanings. Students match, order and choose, and a vocabulary page lists every term with a pronunciation guide.

WHAT'S INCLUDED ({TOTAL_PAGES} pages, PDF, US Letter)
• Cover (1 page)
• Teacher notes with pacing, tips and standards (1 page)
• Symbol key (1 page)
• Vocabulary (1 page)
• Six scene pages with hunt lists and count boxes (6 pages)
• Tempo review (1 page)
• Dynamics review (1 page)
• Scoring and class record with a rubric (1 page)
• Six scene answer keys with every symbol circled and counted (6 pages)
• Review answer keys (1 page)
• Terms of use and credits (1 page)
Total: {TOTAL_PAGES} pages.

HOW TO USE
Hand out the symbol key and a scene page. Students color the circle beside each symbol on the hunt list, circle each one they find in that color, count and write the numbers. Use the keys to check. It works as a center, an early-finisher activity, a sub plan or a review before a concert.

• Grades 3-5
• Prints well in black and white: every color is also written as a word
• No songs, lyrics or copyrighted characters

{DISCLOSURE}
```

## 3. Grades

3rd, 4th and 5th.

## 4. Subjects and tags

- Subjects: {", ".join(SUBJECTS)}
- Tags: {", ".join(TAGS)}

## 5. Page count by section (totals {TOTAL_PAGES})

{lst}
- Total: {TOTAL_PAGES}

## 6. Standards

None cited by code. The teacher notes refer to the National Core Arts Standards for Music in general terms and ask teachers to match them to their own curriculum.

## 7. Price

**${PRICE}** (paid; owner range $3-5).

## 8. Preview

Paid. Preview PDF: scene 1 (page {p_scene(1)}), the symbol key (page {P_KEY}), the tempo review (page {P_TEMPO}) and the scene 3 answer key (page {p_key(3)}), all watermarked.

## 9. Before you click publish

- Season: winter, non-religious. Build window: December and January.
- Art: the cover illustration (magnifying glass, snowflake, mitten and tree) is made with AI tools (the disclosure line covers it); scenes, notation, tables and keys are drawn in code.
- Open owner question: logo beside HUDSON BEAT (see tpt/STYLE.md).
"""


def tpt_json():
    return {"price": PRICE, "license_price": PRICE, "tax_code": "Other Digital Goods - No Physical Media", "grades": GRADES, "subjects": SUBJECTS, "tags": TAGS,
            "formats": ["PDF"], "pages": TOTAL_PAGES, "answer_key": "Included",
            "files": {"product": f"{SLUG}.pdf", "preview": f"{SLUG}-PREVIEW.pdf", "thumb1": "cover.png", "thumb2": "preview-1.png", "thumb3": "preview-2.png", "thumb4": "preview-3.png"}}


SHOT_PAGES = [p_scene(1), P_KEY, P_TEMPO, p_scene(3), p_key(3), P_DYN, P_REVKEY, P_SCORE]


def build():
    os.makedirs(BUILD, exist_ok=True)
    full = write("resource.html", html_doc(full_pages(), TITLE))
    prev = write("preview.html", html_doc(preview_pages(), "Preview"))
    render([{"html": full, "pdf": PDF}, {"html": prev, "pdf": PREVIEW_PDF}])
    for i in SHOT_PAGES:
        subprocess.run(["pdftoppm", "-png", "-r", "150", "-f", str(i), "-l", str(i), "-singlefile", PDF, os.path.join(BUILD, f"pg{i}")], check=True)
    sq = [write("cover.html", cover_square()),
          write("p1.html", preview_square_1([f"pg{p_scene(1)}.png", f"pg{P_KEY}.png", f"pg{P_TEMPO}.png"])),
          write("p2.html", preview_square_2(f"pg{p_scene(3)}.png", f"pg{p_key(3)}.png")),
          write("p3.html", preview_square_3([f"pg{P_DYN}.png", f"pg{P_REVKEY}.png", f"pg{P_SCORE}.png"]))]
    render([{"html": h, "png": o, "width": 1000, "height": 1000, "scale": 2} for h, o in zip(sq, [COVER_PNG] + PREVIEW_PNGS)])
    with open(UPLOAD, "w") as fh:
        fh.write(upload_md())
    with open(TPT_JSON, "w") as fh:
        json.dump(tpt_json(), fh, indent=2)
        fh.write("\n")
    print(f"built {PDF}, {PREVIEW_PDF}, cover + 3 previews, UPLOAD.md, tpt.json")


if __name__ == "__main__" and "--check" not in sys.argv:
    build()


# ------------------------------------------------------------------ checks (independent of the generator's data where it matters)
NS = "{http://www.w3.org/2000/svg}"
SVG_RE = re.compile(r'<svg class="(?:scene|ks|sm)".*?</svg>', re.S)

# second copy of the classification: code points -> symbol id (does not use symbols.CP)
CP_CLASS = {(0xE050,): "treble", (0xE062,): "bass", (0xE0A4,): "quarter", (0xE0A3,): "half", (0xE0A2,): "whole", (0xE4E5,): "qrest", (0xE4E4,): "hrest",
            (0xE041,): "repeat", (0xE4C0,): "fermata", (0xE262,): "sharp", (0xE260,): "flat", (0xE261,): "natural", (0xE522,): "f", (0xE520,): "p",
            (0xE52D,): "mf", (0xE52C,): "mp", (0xE53E,): "cresc", (0xE53F,): "decresc", (0xE084, 0xE084): "ts44", (0xE031,): "dbl"}
RECTS_NEEDED = {"quarter": 1, "half": 1, "hrest": 1}
_GB = {}


def gbox(cp):
    if not _GB:
        from fontTools.ttLib import TTFont
        from fontTools.pens.boundsPen import BoundsPen
        f = TTFont(os.path.join(FONTS, "bravura.woff2"))
        gs, cm, upm = f.getGlyphSet(), f.getBestCmap(), f["head"].unitsPerEm
        for c in {k for key in CP_CLASS for k in key}:
            bp = BoundsPen(gs)
            gs[cm[c]].draw(bp)
            _GB[c] = tuple(v / upm * 4 for v in bp.bounds)
    return _GB[cp]


def fl(v):
    return float(v)


def read_group(g):
    """Parse one symbol group: returns dict(sym, S, texts [(cp,x,y,fs)], rects [(x,y,w,h)], ink box in local px, matrix)."""
    ink = [c for c in g if c.get("class") == "ink"]
    if len(ink) != 1:
        return None
    texts = [(ord(t.text), fl(t.get("x")), fl(t.get("y")), fl(t.get("font-size"))) for t in ink[0].iter(NS + "text")]
    rects = [(fl(r.get("x")), fl(r.get("y")), fl(r.get("width")), fl(r.get("height"))) for r in ink[0].iter(NS + "rect")]
    xs, ys = [], []
    for cp, x, y, fs in texts:
        b = gbox(cp)
        S = fs / 4
        xs += [x + b[0] * S, x + b[2] * S]
        ys += [y - b[3] * S, y - b[1] * S]
    for x, y, w, h in rects:
        xs += [x, x + w]
        ys += [y, y + h]
    tr = g.get("transform", "")
    nums = [[float(v) for v in re.findall(r"-?\d+\.?\d*", part)] for part in re.findall(r"\w+\([^)]*\)", tr)]
    return dict(texts=texts, rects=rects, box=(min(xs), min(ys), max(xs), max(ys)), tr=nums, s=fl(g.get("data-s")), down=g.get("data-down") == "1", sym=g.get("data-sym"))


def classify(info, errs, label):
    key = tuple(sorted(t[0] for t in info["texts"]))
    sym = CP_CLASS.get(key)
    if sym is None:
        errs.append(f"{label}: glyphs {[hex(k) for k in key]} are not a known symbol")
        return None
    if len(info["rects"]) != RECTS_NEEDED.get(sym, 0):
        errs.append(f"{label}: {sym} has {len(info['rects'])} rectangles, expected {RECTS_NEEDED.get(sym, 0)}")
    S = info["s"]
    for cp, x, y, fs in info["texts"]:
        if abs(fs - 4 * S) > 0.05:
            errs.append(f"{label}: font size {fs} is not 4 staff spaces of {S}")
    if sym in ("quarter", "half"):
        cp, hx, hy, fs = info["texts"][0]
        rx, ry, rw, rh = info["rects"][0]
        hw = 1.18 * S
        if info["down"]:
            if abs(rx - hx) > 0.06 or abs(ry - (hy + 0.168 * S)) > 0.06 or abs((ry + rh) - (hy + 3.668 * S)) > 0.06:
                errs.append(f"{label}: down stem not on the left edge of the head going down")
        else:
            if abs((rx + rw) - (hx + hw)) > 0.06 or abs((ry + rh) - (hy - 0.168 * S)) > 0.06 or abs(ry - (hy - 3.668 * S)) > 0.06:
                errs.append(f"{label}: up stem not on the right edge of the head going up")
        if abs(rw - 0.12 * S) > 0.05 or rh < 3 * S:
            errs.append(f"{label}: stem thickness or length wrong")
    if sym == "ts44":
        ys = sorted(t[2] for t in info["texts"])
        if abs((ys[1] - ys[0]) - 2 * S) > 0.05:
            errs.append(f"{label}: time signature digits not one above the other at the right spacing")
    if sym == "hrest":
        cp, hx, hy, fs = info["texts"][0]
        rx, ry, rw, rh = info["rects"][0]
        if not (abs(ry - hy) < 0.06 and rx < hx and rx + rw > hx + 1.13 * S):
            errs.append(f"{label}: half rest is not sitting on its line")
    if sym != info["sym"]:
        errs.append(f"{label}: group is labelled {info['sym']} but is drawn as {sym}")
    return sym


def aabb_of(info, grow=0.0):
    m = info["tr"]  # translate(cx cy) rotate(r) translate(-mx -my)
    (cx, cy), (rot,), (mx, my) = m[0], m[1], m[2]
    a = math.radians(rot)
    x0, y0, x1, y1 = info["box"]
    xs, ys = [], []
    for px, py in ((x0, y0), (x1, y0), (x1, y1), (x0, y1)):
        dx, dy = px + mx, py + my
        xs.append(cx + dx * math.cos(a) - dy * math.sin(a))
        ys.append(cy + dx * math.sin(a) + dy * math.cos(a))
    return min(xs) - grow, min(ys) - grow, max(xs) + grow, max(ys) + grow, rot


def verify_html():
    errs = []
    html = open(os.path.join(BUILD, "resource.html")).read()
    svgs = SVG_RE.findall(html)
    scene_counts = {}
    key_scenes = {}
    for sv in svgs:
        root = ET.fromstring(sv)
        cls = root.get("class")
        if cls == "scene":
            n, key = int(root.get("data-scene")), root.get("data-key") == "1"
            groups = [g for g in root.iter(NS + "g") if g.get("class") == "hs"]
            cnt, boxes = {}, []
            for i, g in enumerate(groups):
                info = read_group(g)
                label = f"scene {n} symbol {i + 1}"
                if info is None:
                    errs.append(f"{label}: no ink group")
                    continue
                sym = classify(info, errs, label)
                if sym is None:
                    continue
                cnt[sym] = cnt.get(sym, 0) + 1
                x0, y0, x1, y1, rot = aabb_of(info)
                if abs(rot) > 10.01:
                    errs.append(f"{label}: tilted {rot} degrees")
                boxes.append((sym, x0, y0, x1, y1))
                for kx0, ky0, kx1, ky1 in SC.KEEPOUT.get(n, ()):
                    # knock-out (ink + halo 3) must stay at least a stroke width (1.6) clear of decorative outlines (moons, clouds)
                    m = 3 + 1.6
                    if x0 - m < kx1 and kx0 < x1 + m and y0 - m < ky1 and ky0 < y1 + m:
                        errs.append(f"{label} ({sym}): knock-out box cuts or crowds a decorative outline (moon or cloud)")
                # padding: ink + halo (3) + ring (7 + 1.6) stays inside the frame by at least the stroke width
                pad = 7 + 1.6 + 2.4
                if x0 - pad < 2 or y0 - pad < 2 or x1 + pad > SC.W - 2 or y1 + pad > SC.H - 2:
                    errs.append(f"{label} ({sym}): too close to the scene box edge (needs padding of at least its stroke)")
            for a in range(len(boxes)):
                for b in range(a + 1, len(boxes)):
                    A, B = boxes[a], boxes[b]
                    gap = max(A[1], B[1]) - min(A[3], B[3]), max(A[2], B[2]) - min(A[4], B[4])
                    if gap[0] < 18 and gap[1] < 18:
                        errs.append(f"scene {n}: {A[0]} and {B[0]} overlap or crowd each other")
            (key_scenes if key else scene_counts)[n] = cnt
            if key:
                rings = [r for r in root.iter(NS + "rect") if r.get("class") == "ring"]
                if len(rings) != len(groups):
                    errs.append(f"scene {n} key: {len(rings)} rings for {len(groups)} symbols")
                for r in rings:  # each ring colour must be the colour of its symbol's row
                    pass
        elif cls == "ks":
            check_staff(root, errs)
        else:
            groups = [g for g in root.iter(NS + "g") if g.get("data-sym")]
            for g in groups:
                info = read_group(g)
                if info:
                    classify(info, errs, "sample")
    for n in SCENE_IDS:
        if sorted(scene_counts.get(n, {}).items()) != sorted(dict(SC.SCENES[n]["counts"]).items()):
            errs.append(f"scene {n}: recounted {scene_counts.get(n)} differs from the data {SC.SCENES[n]['counts']}")
        if key_scenes.get(n) != scene_counts.get(n):
            errs.append(f"scene {n}: the key drawing does not hold the same symbols as the student page")
    # hunt lists and keys: counts printed in the answer key equal the recount
    for m in re.finditer(r'<div class="hc" data-scene="(\d+)" data-sym="(\w+)" data-color="(\w+)" data-count="(\d+)"', html):
        n, s, col, c = int(m.group(1)), m.group(2), m.group(3), int(m.group(4))
        if scene_counts.get(n, {}).get(s) != c:
            errs.append(f"scene {n}: key says {c} {s}, the drawing has {scene_counts.get(n, {}).get(s)}")
    for n in SCENE_IDS:
        rows = re.findall(rf'<div class="hc" data-scene="{n}" data-sym="(\w+)"', html)
        if sorted(rows) != sorted(list(scene_counts.get(n, {})) * 2):
            errs.append(f"scene {n}: hunt list and key list do not name exactly the symbols drawn in the scene")
        m = re.search(rf'data-total="{n}">Total hidden symbols: (\d+)', html)
        if not m or int(m.group(1)) != sum(scene_counts.get(n, {}).values()):
            errs.append(f"scene {n}: printed total differs from the recount")
        colors = re.findall(rf'<div class="hc" data-scene="{n}" data-sym="\w+" data-color="(\w+)"', html)
        if len(set(colors)) != len(colors) // 2:
            errs.append(f"scene {n}: two kinds of symbol share a color")
        # ring colours equal swatch colours, in drawing order of the row list
        ring = {m2.group(1): m2.group(2) for m2 in re.finditer(r'<rect class="ring" data-sym="(\w+)"[^>]*stroke="(#\w+)"', html.split(f'data-scene="{n}" data-key="1"')[1].split("</svg>")[0])}
        for (s, _), col in zip(SC.SCENES[n]["counts"], SC.SCENES[n]["colors"]):
            if ring.get(s) != SC.COLOR_HEX[col]:
                errs.append(f"scene {n}: ring color of {s} is {ring.get(s)}, expected {SC.COLOR_HEX[col]} ({col})")
    if ALL_HIDDEN != sum(sum(c.values()) for c in scene_counts.values()):
        errs.append("total hidden symbols differs from the recount")
    # points
    pts = sum(len(c) for c in scene_counts.values())
    if pts != HUNT_POINTS or TOTAL_POINTS != HUNT_POINTS + 33:
        errs.append(f"points: hunt {pts} vs {HUNT_POINTS}, total {TOTAL_POINTS}")
    errs += verify_reviews(html)
    return errs


def check_staff(root, errs):
    sym = root.get("data-cell")
    lines = sorted(fl(l.get("y1")) for l in root.iter(NS + "line") if l.get("class") == "sl")
    if len(lines) != 5 or any(abs((lines[i + 1] - lines[i]) - (lines[1] - lines[0])) > 0.01 for i in range(4)):
        errs.append(f"key staff {sym}: not five evenly spaced lines")
        return
    sp = lines[1] - lines[0]
    mid = lines[2]
    bottom, top = lines[4], lines[0]
    found = []
    for g in root.iter(NS + "g"):
        if g.get("class") != "smp":
            continue
        info = read_group(g)
        label = f"key staff {sym}"
        s = classify(info, errs, label)
        if s is None:
            continue
        found.append(s)
        tx, ty = [float(v) for v in re.findall(r"-?\d+\.?\d*", g.get("transform"))]
        if abs(info["s"] - sp) > 0.01:
            errs.append(f"{label}: symbol scale differs from the staff space")
        if s in ("quarter", "half"):
            below = ty > mid + 0.01
            if below and info["down"]:
                errs.append(f"{label}: a note below the middle line has its stem down")
            if not below and not info["down"]:
                errs.append(f"{label}: a note on or above the middle line has its stem up")
            if not (top - 0.01 <= ty <= bottom + 0.01):
                errs.append(f"{label}: note head off the staff")
        elif s == "treble" and abs(ty - lines[3]) > 0.01:
            errs.append(f"{label}: treble clef not on the G line")
        elif s == "bass" and abs(ty - lines[1]) > 0.01:
            errs.append(f"{label}: bass clef not on the F line")
        elif s in ("qrest", "hrest", "ts44") and abs(ty - mid) > 0.01:
            errs.append(f"{label}: {s} not on the middle line")
        elif s in ("repeat", "dbl") and abs(ty - bottom) > 0.01:
            errs.append(f"{label}: {s} does not start at the bottom line")
        elif s == "whole" and not (top < ty < bottom):
            errs.append(f"{label}: whole note off the staff")
        elif s == "fermata" and not ty < top:
            errs.append(f"{label}: fermata not above the staff")
        elif s in ("sharp", "flat", "natural"):
            if abs(ty - mid) > 0.01:
                errs.append(f"{label}: accidental not centred on its note")
        vb = [float(v) for v in root.get("viewBox").split()]
        a = info["box"]
        if tx + a[0] < 1 or ty + a[1] < 1 or tx + a[2] > vb[2] - 1 or ty + a[3] > vb[3] - 1:
            errs.append(f"{label}: {s} is clipped by its drawing box")
    want = {"quarter": ["quarter", "quarter"], "half": ["half", "half"], "fermata": ["fermata", "whole"], "sharp": ["sharp", "quarter"],
            "flat": ["flat", "quarter"], "natural": ["natural", "quarter"]}.get(sym, [sym])
    if sorted(found) != sorted(want):
        errs.append(f"key staff {sym}: shows {found}")
    if sym in ("sharp", "flat", "natural") and len(found) == 2:
        pass


def verify_reviews(html):
    errs = []
    # facts typed again here, apart from the data in the generator
    MEANING = {"largo": "very slow", "andante": "a walking speed", "moderato": "a medium speed", "allegro": "fast and lively", "presto": "very fast"}
    BPM = {"largo": (40, 60), "andante": (76, 108), "moderato": (108, 120), "allegro": (120, 156), "presto": (168, 200)}
    DYNM = {"piano": "soft", "mezzo piano": "medium soft", "mezzo forte": "medium loud", "forte": "loud",
            "crescendo": "gradually getting louder", "decrescendo": "gradually getting softer"}
    for t, m, b in re.findall(r'<tr data-term="(\w+)" data-meaning="([^"]+)" data-bpm="([^"]+)"', html):
        if MEANING.get(t) != m:
            errs.append(f"vocabulary: {t} means '{MEANING.get(t)}', page says '{m}'")
        lo, hi = (int(x) for x in b.split("–"))
        if BPM[t] != (lo, hi):
            errs.append(f"vocabulary: {t} BPM {b}")
    for t, m in re.findall(r'<tr data-term="([a-z ]+)" data-meaning="([^"]+)"><td class="vsym"', html):
        if DYNM.get(t) != m:
            errs.append(f"vocabulary: {t} means '{DYNM.get(t)}', page says '{m}'")
    seen_t = set(re.findall(r'<tr data-term="(\w+)" data-meaning="[^"]+" data-bpm', html))
    if seen_t != set(MEANING):
        errs.append("vocabulary: tempo terms missing")
    # tempo review (student page): letters
    letter_meaning = dict(re.findall(r'<li data-letter="(\w)" data-meaning="([^"]+)"', html))
    for t, L in re.findall(r'<li data-term="(\w+)" data-ans="(\w)"><span class="lt">', html):
        if letter_meaning.get(L) != MEANING[t]:
            errs.append(f"tempo review A: {t} is keyed {L} = '{letter_meaning.get(L)}', should be '{MEANING[t]}'")
    # printed key: letter, meaning
    for t, L, m in re.findall(r'<tr data-term="(\w+)" data-ans="(\w)"><td><b>\d\. \w+</b></td><td class="mid">\w</td><td>([^<]+)</td>', html):
        if m != MEANING[t] or letter_meaning.get(L) != MEANING[t]:
            errs.append(f"review key A: {t}")
    order = sorted(BPM, key=lambda t: BPM[t][0])
    for t, r in re.findall(r'<tr data-term="(\w+)" data-rank="(\d)"', html):
        if order.index(t) + 1 != int(r):
            errs.append(f"review key B: {t} ranked {r}, correct {order.index(t) + 1}")
    for t, bpm, ans in re.findall(r'<div class="chip" data-term="(\w+)" data-bpm="([^"]+)" data-ans="(\d)"', html):
        if order.index(t) + 1 != int(ans) or bpm != f"{BPM[t][0]}–{BPM[t][1]}":
            errs.append(f"tempo review B chip {t}")
    SCN = {1: "presto", 2: "andante", 3: "largo", 4: "allegro", 5: "moderato"}
    for i, a in re.findall(r'<li data-scn="(\d)" data-ans="(\w+)"', html):
        if SCN[int(i)] != a:
            errs.append(f"tempo review C item {i}: keyed {a}, expected {SCN[int(i)]}")
    for i, a in re.findall(r'<tr data-scn="(\d)" data-ans="(\w+)">', html):
        if SCN[int(i)] != a:
            errs.append(f"review key C item {i}")
    SIGN = {"p": "piano", "mp": "mezzo piano", "mf": "mezzo forte", "f": "forte", "cresc": "crescendo", "decresc": "decrescendo"}
    RANK = {"p": 1, "mp": 2, "mf": 3, "f": 4}
    # the dynamics key rows hold a sample whose glyph we read back
    def row_sym(chunk):
        m = re.search(r'<g class="smp" data-sym="(\w+)"', chunk)
        return m.group(1) if m else None
    dk = html.split('data-page="20"')[1]
    for m in re.finditer(r'<tr data-sym="(\w+)"><td class="vsym" style="width:60pt">(.*?)</td><td><b>([a-z ]+)</b></td></tr>', dk, re.S):
        s = m.group(1)
        if row_sym(m.group(2)) != s or SIGN[s] != m.group(3):
            errs.append(f"dynamics key A: {s} -> {m.group(3)}")
    for m in re.finditer(r'<tr data-sym="(\w+)" data-rank="(\d)"><td class="vsym" style="width:60pt">(.*?)</td>', dk, re.S):
        if RANK[m.group(1)] != int(m.group(2)) or row_sym(m.group(3)) != m.group(1):
            errs.append(f"dynamics key B: {m.group(1)}")
    for m in re.finditer(r'<tr data-sym="(\w+)" data-ans="(\w+)"><td>\d\.</td><td class="vsym" style="width:60pt">(.*?)</td>', dk, re.S):
        want = {"cresc": "louder", "decresc": "softer"}[m.group(1)]
        if want != m.group(2) or row_sym(m.group(3)) != m.group(1):
            errs.append(f"dynamics key C: {m.group(1)}")
    WORDS_ = {"loud": "f", "soft": "p", "medium loud": "mf", "medium soft": "mp"}
    got = re.findall(r'<tr data-word="([a-z ]+)" data-ans="(\w+)">', dk)
    if sorted(got) != sorted(WORDS_.items()):
        errs.append(f"dynamics key D: {got}")
    if len(re.findall(r'<tr data-sym="\w+"><td class="vsym" style="width:90pt">', html)) != 6:
        errs.append("dynamics review A should have 6 symbols")
    # the student review A symbols are the same six as the key
    sa = html.split('data-page="12"')[1].split('data-page="13"')[0]
    if sorted(re.findall(r'<g class="smp" data-sym="(\w+)"', sa.split("Quiet to loud")[0])) != sorted(SIGN):
        errs.append("dynamics review A does not show the six dynamic symbols once each")
    return errs


LAYOUT_JS = r"""
const { chromium } = require('playwright');
const url = require('url');
(async () => {
  const b = await chromium.launch();
  const out = [];
  for (const f of process.argv.slice(2)) {
    const p = await b.newPage({ viewport: { width: 1000, height: 1056 }, deviceScaleFactor: 1 });
    await p.goto(url.pathToFileURL(f).href, { waitUntil: 'load' });
    await p.evaluate(() => document.fonts.ready);
    const r = await p.evaluate(() => {
      const res = [];
      const BOX = '.hc, .box, .part, .top, .nd, .doc table, .hunt, .kc, .doc p, .doc ul, .scn, .chip';
      document.querySelectorAll('.page').forEach((pg, i) => {
        const pr = pg.getBoundingClientRect();
        const ft = pg.querySelector('.foot');
        if (pg.scrollHeight > pg.clientHeight + 1) res.push(`page ${i + 1}: content overflows the page`);
        if (!ft) return;
        const ftop = ft.getBoundingClientRect().top;
        const skip = el => ft.contains(el) || el.closest('.wm');
        pg.querySelectorAll(BOX + ', svg, img').forEach(el => {
          if (skip(el)) return;
          const r = el.getBoundingClientRect();
          if (r.height === 0) return;
          if (r.bottom > ftop - 8) res.push(`page ${i + 1}: ${el.tagName}.${el.getAttribute('class')} bottom ${(r.bottom - ftop).toFixed(1)}px vs footer rule (needs <= -8)`);
          if (r.right > pr.right - 0.35 * 96 + 0.5 || r.left < pr.left + 0.35 * 96 - 0.5) res.push(`page ${i + 1}: ${el.tagName}.${el.getAttribute('class')} too close to the page edge`);
        });
        pg.querySelectorAll('*').forEach(el => {
          if (skip(el) || el.children.length || !(el.textContent || '').trim() || el.closest('svg')) return;
          const r = el.getBoundingClientRect();
          if (r.height && r.bottom > ftop - 8) res.push(`page ${i + 1}: text "${el.textContent.trim().slice(0, 30)}" ends ${(r.bottom - ftop).toFixed(1)}px from the footer rule`);
        });
        pg.querySelectorAll('.hc, .part, .box').forEach(bx => {
          if (bx.scrollWidth > bx.clientWidth + 1 || bx.scrollHeight > bx.clientHeight + 1) res.push(`page ${i + 1}: content overflows a ${bx.className} box`);
          const br = bx.getBoundingClientRect();
          bx.querySelectorAll('svg').forEach(sv => {
            const s = sv.getBoundingClientRect();
            if (s.left < br.left + 2 || s.right > br.right - 2 || s.top < br.top + 1 || s.bottom > br.bottom - 1) res.push(`page ${i + 1}: a drawing is too close to its box edge`);
          });
        });
        const boxes = [...pg.querySelectorAll('.hc, .part')].map(e => e.getBoundingClientRect());
        for (let a = 0; a < boxes.length; a++) for (let c = a + 1; c < boxes.length; c++) {
          const A = boxes[a], C = boxes[c];
          const gx = Math.max(A.left, C.left) - Math.min(A.right, C.right);
          const gy = Math.max(A.top, C.top) - Math.min(A.bottom, C.bottom);
          if (gx < 4 && gy < 4) res.push(`page ${i + 1}: two boxes lack a gutter`);
        }
        pg.querySelectorAll('.kc').forEach(kc => {
          const br = kc.getBoundingClientRect();
          kc.querySelectorAll('svg').forEach(sv => {
            const s = sv.getBoundingClientRect();
            if (s.left < br.left - 0.5 || s.top < br.top - 0.5 || s.bottom > br.bottom + 0.5) res.push(`page ${i + 1}: key sample outside its cell`);
          });
        });
        pg.querySelectorAll('.top .t').forEach(t => { if (t.getBoundingClientRect().right > pg.querySelector('.top .tag').getBoundingClientRect().left - 8) res.push(`page ${i + 1}: title crowds the tag`); });
        let maxb = 0;
        pg.querySelectorAll('*').forEach(el => { if (skip(el)) return; const r = el.getBoundingClientRect(); if (r.height > 0 && r.width > 0 && ((el.children.length === 0 && ((el.textContent || '').trim() || el.matches('svg, img'))) || el.matches('.hc, .part, .box, table'))) maxb = Math.max(maxb, r.bottom); });
        if (i > 0 && ftop - maxb > 105) res.push(`page ${i + 1}: blank band of ${(ftop - maxb).toFixed(0)}px above the footer (over 10% of the page)`);
        // blank band between blocks: any gap between consecutive top-level children above 10% of the page
        const kids = [...pg.querySelectorAll(':scope > *, :scope > .stack > *')].filter(e => !skip(e) && e.getBoundingClientRect().height > 0 && !e.classList.contains('stack')).map(e => e.getBoundingClientRect()).sort((a, b) => a.top - b.top);
        for (let k = 0; k < kids.length - 1; k++) if (kids[k + 1].top - kids[k].bottom > 105) res.push(`page ${i + 1}: blank band of ${(kids[k + 1].top - kids[k].bottom).toFixed(0)}px between blocks`);
      });
      document.querySelectorAll('.sq').forEach((sq, i) => {
        const sr = sq.getBoundingClientRect();
        const btop = sq.querySelector('.band').getBoundingClientRect().top;
        const shots = [];
        sq.querySelectorAll('.shot').forEach(sh => {
          const r = sh.getBoundingClientRect(); shots.push(r);
          if (r.left < sr.left + 24 || r.right + 8 > sr.right - 24) res.push(`square ${i + 1}: a page shot is too close to the side edge`);
          if (r.bottom + 8 > btop - 8) res.push(`square ${i + 1}: a page shot shadow is within 8px of the band`);
        });
        for (let a = 0; a < shots.length; a++) for (let c = a + 1; c < shots.length; c++) if (shots[a].right + 16 > shots[c].left && shots[a].left < shots[c].left && shots[a].bottom > shots[c].top) res.push(`square ${i + 1}: page shots lack a gutter`);
        sq.querySelectorAll('.lbl, .lbl span, .pill, .sub, .hd').forEach(el => {
          const r = el.getBoundingClientRect();
          if (r.bottom > btop - 8) res.push(`square ${i + 1}: text "${el.textContent.trim().slice(0, 24)}" within 8px of the band`);
          if (r.left < sr.left + 24 || r.right > sr.right - 24) res.push(`square ${i + 1}: text "${el.textContent.trim().slice(0, 24)}" too close to the side edge`);
        });
        sq.querySelectorAll('.shot img').forEach(im => { if (!im.complete || im.naturalWidth === 0) res.push(`square ${i + 1}: an image did not load`); });
      });
      document.querySelectorAll('.cover').forEach(pg => {
        const pr = pg.getBoundingClientRect();
        pg.querySelectorAll('.ctitle .b, .cband, .ctitle .c, img').forEach(el => {
          const r = el.getBoundingClientRect();
          if (r.left < pr.left + 0.45 * 96 || r.right > pr.right - 0.45 * 96) res.push(`cover: ${el.className || el.tagName} too close to the side edge`);
        });
        const kids = [...pg.children].map(c => c.getBoundingClientRect());
        for (let a = 0; a < kids.length - 1; a++) if (kids[a].bottom + 8 > kids[a + 1].top) res.push('cover: blocks lack a gutter');
      });
      return res;
    });
    out.push(...r.map(x => f.split('/').pop() + ': ' + x));
    await p.close();
  }
  await b.close();
  console.log(JSON.stringify(out));
})().catch(e => { console.error(e); process.exit(1); });
"""

PIX_JS = r"""
const { chromium } = require('playwright');
const url = require('url');
(async () => {
  // each scene rendered with only its hidden symbols and rings on a transparent ground, at 2x: report the ink box in scene units
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 760, height: 500 }, deviceScaleFactor: 2 });
  await p.goto(url.pathToFileURL(process.argv[2]).href, { waitUntil: 'load' });
  await p.evaluate(() => document.fonts.ready);
  const hs = await p.$$('svg.scene');
  let n = 0;
  for (const h of hs) {
    await h.evaluate(sv => { sv.querySelectorAll('g[clip-path], .frame').forEach(e => e.style.display = 'none'); sv.setAttribute('width', '720'); sv.setAttribute('height', '450'); document.body.style.background = 'transparent'; });
    await h.screenshot({ path: process.argv[3] + '/s' + String(n++).padStart(2, '0') + '.png', omitBackground: true });
  }
  await b.close();
  console.log(n);
})().catch(e => { console.error(e); process.exit(1); });
"""


def verify_layout():
    js = os.path.join(BUILD, "layout.js")
    with open(js, "w") as fh:
        fh.write(LAYOUT_JS)
    files = [os.path.join(BUILD, x) for x in ("resource.html", "preview.html", "cover.html", "p1.html", "p2.html", "p3.html")]
    if not all(os.path.exists(x) for x in files):
        return ["build html missing: run gen.py first"]
    r = subprocess.run(["node", js, *files], capture_output=True, text=True, env=node_env())
    if r.returncode != 0:
        return [f"layout script failed: {r.stderr[-300:]}"]
    errs = json.loads(r.stdout.strip().splitlines()[-1])
    # rendered pixels: the hidden symbols alone on a transparent ground must stay inside the scene box with padding
    from PIL import Image
    html = open(os.path.join(BUILD, "resource.html")).read()
    scn = re.findall(r'<svg class="scene" data-scene="\d" data-key="0".*?</svg>', html, re.S)
    page = (f'<!doctype html><html><head><meta charset="utf-8"><style>{font_css()}html,body{{margin:0;background:transparent}}svg{{display:block;margin:20px}}</style></head>'
            f'<body>{"".join(scn)}</body></html>')
    write("pix.html", page)
    shots = os.path.join(BUILD, "pixshots")
    os.makedirs(shots, exist_ok=True)
    for x in os.listdir(shots):
        os.remove(os.path.join(shots, x))
    jsp = os.path.join(BUILD, "pix.js")
    with open(jsp, "w") as fh:
        fh.write(PIX_JS)
    r = subprocess.run(["node", jsp, os.path.join(BUILD, "pix.html"), shots], capture_output=True, text=True, env=node_env())
    if r.returncode != 0:
        return errs + [f"pixel script failed: {r.stderr[-300:]}"]
    names = sorted(os.listdir(shots))
    if len(names) != 6:
        errs.append(f"pixel check rendered {len(names)} scenes")
    for nm in names:
        im = Image.open(os.path.join(shots, nm)).convert("RGBA")
        bb = im.getchannel("A").point(lambda v: 255 if v > 8 else 0).getbbox()
        w, h = im.size
        if bb is None:
            errs.append(f"rendered pixels: {nm} is blank")
            continue
        # scene is 720x450 units at 2x; the 2.4 stroke plus at least 2.4 padding = 5 units each side
        m = 12
        if bb[0] < m or bb[1] < m or bb[2] > w - m or bb[3] > h - m:
            errs.append(f"rendered pixels: hidden symbols of {nm} come within {min(bb[0], bb[1], w - bb[2], h - bb[3])}px of the scene box edge")
    return errs


def verify_images():
    errs = []
    from PIL import Image
    h = Image.open(HERO)
    a = h.getchannel("A").point(lambda v: 255 if v > 24 else 0)
    bb = a.getbbox()
    if bb is None or bb[0] < 10 or bb[1] < 10 or h.width - bb[2] < 10 or h.height - bb[3] < 10:
        errs.append(f"hero.png touches its image edge: {bb}")
    if h.size != (1400, 1400):
        errs.append("hero.png is not the pre-made 1400x1400 file")
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
    names = set(PAGE_NAMES.values())
    for hn in ("p1.html", "p2.html", "p3.html"):
        t = open(os.path.join(BUILD, hn)).read()
        for cap in re.findall(r'<div class="lbl"[^>]*>([^<]+)(?:<span>[^<]*</span>)?</div>', t):
            if cap not in names:
                errs.append(f"{hn}: label '{cap}' is not a page name")
        if t.count('class="swm"') != 1:
            errs.append(f"{hn}: expected exactly one PREVIEW watermark")
    return errs


def pdf_fonts(path):
    out = subprocess.run(["pdffonts", path], capture_output=True, text=True, check=True).stdout.splitlines()[2:]
    return [(p.split()[0], p.split()[-5]) for p in out]


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
        if i + 1 != 1 and f"Page {i + 1}" not in t:
            errs.append(f"PDF page {i + 1} does not print its own page number")
    for pg, name in PAGE_NAMES.items():
        if pg != P_COVER and name.lower() not in texts[pg - 1].lower():
            errs.append(f"page {pg} does not show its name '{name}'")
    full_pages()
    for frm, to, text in XREFS:
        if text not in texts[frm - 1]:
            errs.append(f"page {frm}: cross-reference text '{text}' not found")
        m = re.search(r"page (\d+)", text)
        if m and int(m.group(1)) != to:
            errs.append(f"cross-reference '{text}' on page {frm} should point to {to}")
    # every scene page names its key, every key names its scene page, and the targets really are those pages
    for n in SCENE_IDS:
        if f"Answer key on page {p_key(n)}" not in texts[p_scene(n) - 1] or f"scene {n}:" not in texts[p_key(n) - 1].lower() or f"Student page {p_scene(n)}" not in texts[p_key(n) - 1]:
            errs.append(f"scene {n}: page references between the student page and its key are wrong")
        if f"Total hidden symbols: {scene_total(n)}" not in texts[p_key(n) - 1]:
            errs.append(f"scene {n}: key page lacks its total")
    for i, t in enumerate(texts):
        for m in re.finditer(r"(?i)\bpages? (\d+)(?:–(\d+))?", t):
            a, b = int(m.group(1)), int(m.group(2) or m.group(1))
            if a < 1 or b > TOTAL_PAGES or b < a:
                errs.append(f"page {i + 1}: reference '{m.group(0)}' is outside the {TOTAL_PAGES}-page file")
    teach, terms, score = texts[P_TEACH - 1], texts[P_TERMS - 1], texts[P_SCORE - 1]
    for need in (f"Page {P_KEY}", f"Page {P_VOCAB}", f"Pages {p_scene(1)}–{p_scene(6)}", f"{ALL_HIDDEN} hidden symbols", f"Pages {p_key(1)}–{p_key(6)}", f"Page {P_REVKEY}", f"({TOTAL_PAGES} pages)"):
        if need.lower() not in teach.lower():
            errs.append(f"teacher notes lack '{need}'")
    for n in SCENE_IDS:
        if f"scene {n} ({scene_total(n)})" not in teach:
            errs.append(f"teacher notes: scene {n} total missing")
    if f"pages {p_scene(1)}–{p_scene(6)}" not in terms or f"pages {p_key(1)}–{P_REVKEY}" not in terms or f"({TOTAL_PAGES} pages)" not in terms.lower().replace("pages)", "pages)") and f"({TOTAL_PAGES} pages)" not in terms:
        errs.append("terms page 'what is in this file' does not match the page numbers")
    if f"{TOTAL_POINTS}" not in score or f"{pct_bands()[0]}–{TOTAL_POINTS}" not in score:
        errs.append("scoring page totals or bands missing")
    # score table equals the recount
    html = open(os.path.join(BUILD, "resource.html")).read()
    pts = [int(x) for x in re.findall(r'<tr data-pts="(\d+)">', html)]
    if sum(pts) != TOTAL_POINTS or pts[:6] != [scene_types(n) for n in SCENE_IDS]:
        errs.append(f"score table rows {pts} do not add to {TOTAL_POINTS}")
    prd = PdfReader(PREVIEW_PDF)
    for i in range(4):
        t = prd.pages[i].extract_text() or ""
        if t.count("PREVIEW") != 1:
            errs.append(f"preview PDF page {i + 1}: expected exactly one PREVIEW watermark")
        if PAGE_NAMES[PREVIEW_PAGES[i]].lower() not in t.lower():
            errs.append(f"preview PDF page {i + 1} is not '{PAGE_NAMES[PREVIEW_PAGES[i]]}'")
    errs += verify_images()
    up = open(UPLOAD).read()
    m = re.search(r"^## 1\. Title\s*\n+```\n(.+?)\n```", up, re.M | re.S)
    if not m:
        errs.append("UPLOAD.md: title block not found")
    else:
        title = m.group(1).strip()
        if len(title) > 80 or title != LISTING_TITLE:
            errs.append("UPLOAD.md: title is over 80 chars or differs from the generator")
        if re.search(r"winter|snow|holiday|christmas|december|halloween|thanksgiving|season", title, re.I):
            errs.append("UPLOAD.md: seasonal word in the title")
    if re.search(r"winter|snow|holiday", TITLE + " " + texts[0], re.I):
        errs.append("cover or title carries a seasonal word")
    for need in (DISCLOSURE, f"${PRICE}", f"{TOTAL_PAGES} pages", f"{ALL_HIDDEN} hidden symbols", "Grades 3-5", "3rd, 4th and 5th"):
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
    for n in SCENE_IDS:
        if SC.SCENES[n]["title"] not in desc:
            errs.append(f"UPLOAD.md lacks scene '{SC.SCENES[n]['title']}'")
    low = up.lower()
    for bad in ("checked by hand", "handmade", "recomputed", "classroom-tested", "classroom tested", "hand-checked"):
        if bad in low:
            errs.append(f"UPLOAD.md says '{bad}'")
    tj = json.load(open(TPT_JSON))
    tags = set(json.load(open(os.path.join(TPT, "TAG-OPTIONS.json")))["options"])
    subs = set(json.load(open(os.path.join(TPT, "SUBJECT-OPTIONS.json"))))
    if any(t not in tags for t in tj["tags"]) or any(s not in subs for s in tj["subjects"]):
        errs.append("tpt.json tags or subjects invalid")
    if tj.get("pages") != TOTAL_PAGES or tj["price"] != PRICE or not 1 <= len(tj["grades"]) <= 4:
        errs.append("tpt.json pages, price or grades mismatch")
    first = texts[0].lower()
    if f"{TOTAL_PAGES} pages" not in first or "6 scenes" not in first or "grades 3–5" not in first:
        errs.append("cover text does not state the page count, scenes and grades")
    if DISCLOSURE not in terms:
        errs.append("terms page lacks the disclosure line")
    allt = " ".join(texts).lower()
    for bad in ("colour", "favourite", "metre", "crotchet", "quaver", "minim", "semibreve", "analyse", "recomputed", "checker"):
        if bad in allt:
            errs.append(f"unwanted wording '{bad}'")
    for bad in ("christmas", "santa", "holiday", "hanukkah", "kwanzaa", "easter"):
        if bad in allt:
            errs.append(f"holiday word '{bad}' in the product")
    return errs


def check():
    errs = verify_html()
    errs += verify_layout()
    errs += verify_files()
    if errs:
        print("CHECK FAILED")
        print("\n".join(" - " + e for e in errs[:80]))
        if len(errs) > 80:
            print(f" ... and {len(errs) - 80} more")
        sys.exit(1)
    print(f"CHECK OK: {ALL_HIDDEN} hidden symbols in 6 scenes re-read from the rendered SVG and classified from their glyphs; counts per scene equal the answer keys, hunt lists, totals and "
          f"score page ({TOTAL_POINTS} points); stems attach to the right edge going up and the left edge going down; key staff positions correct; symbols keep padding inside their scene boxes and do not "
          f"overlap (also tested on rendered pixels); tempo and dynamics review keys match a second copy of the facts; layout and footer gaps clear; PDF {TOTAL_PAGES} Letter pages, preview 4 "
          f"(one watermark each); images 2000x2000 with clean edges; cross-references, UPLOAD.md and tpt.json agree.")


if __name__ == "__main__" and "--check" in sys.argv:
    check()
