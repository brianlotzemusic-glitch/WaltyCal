#!/usr/bin/env python3
"""Winter Concert Planner + Program Kit (TpT 005): build the resource and verify it.

    python3 gen.py            build everything (PDFs, PNGs, tpt.json) into this folder
    python3 gen.py --lowres   same, but square images at scale 1 (self-check only; --check rejects them)
    python3 gen.py --check    verify plan, cross-references, notation, wording, pages, fonts and files

A printable teacher resource for any K-8 winter concert: planning timeline, concert
at a glance, repertoire planner, rehearsal tracker and plans, two seating charts,
stage/tech checklist with volunteer sign-up, run of show, parent letter with return
slip, reminder notes, 3 program layouts, 8 thank-you notes and a student reflection.

Non-denominational: no holiday names, trees, stars, gifts or religious images. Piece
titles are left blank, so no songs, lyrics or copyrighted works appear anywhere.
The only notation is a decorative one-bar 4/4 rhythm strip on the cover and programs,
engraved with item 002's rhythm.py (Bravura) and checked here.

Rendering uses Playwright + Chromium (HTML/SVG -> PDF/PNG) through the shared
../tools/render.js, with the OFL fonts in ../fonts embedded as subsets.
"""
import importlib.util
import json
import math
import os
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

SLUG = "winter-concert-planner"
PDF = os.path.join(HERE, f"{SLUG}.pdf")
PREVIEW_PDF = os.path.join(HERE, f"{SLUG}-PREVIEW.pdf")
COVER_PNG = os.path.join(HERE, "cover.png")
PREVIEW_PNGS = [os.path.join(HERE, f"preview-{i}.png") for i in (1, 2, 3)]
UPLOAD = os.path.join(HERE, "UPLOAD.md")
TPT_JSON = os.path.join(HERE, "tpt.json")

STORE = "Brian Lotze"      # copyright holder
BRAND = "Hudson Beat"      # store line on covers and previews (owner, 4 Oct)
YEAR = 2026
ACCENT = "#2E6FA7"         # this product's single accent (winter blue, a little deeper than 003's icy blue)
TITLE = "Winter Concert Planner"
PRICE = "4.50"
LOW_RES = "--lowres" in sys.argv

# Decorative rhythm strips (one bar of 4/4 each, item 002 tokens: q ta, e ti-ti, r rest, h half note)
STRIPS = {"cover": "qeh", "prog_a": "eeh", "prog_b": "qqeq", "prog_c": "hqe"}

# Words that must not appear anywhere in the resource (it is a non-denominational winter concert kit)
BANNED = ("christmas", "xmas", "santa", "hanukkah", "chanukah", "kwanzaa", "nativity", "jesus", "holiday", "advent",
          "reindeer", "jingle", "carol", "menorah", "elf", "elves")

SYL = {"q": "ta", "e": "ti-ti", "r": "shh", "h": "ta-a"}


# ---------------------------------------------------------------- html scaffolding (from 004)
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
.how { font-size: 11pt; margin: 7pt 0 6pt; }
.main { flex: 1; display: flex; flex-direction: column; }
.foot { display: flex; justify-content: space-between; font-size: 8.5pt; color: #333; border-top: .8pt solid #000; padding-top: 3pt; }
.wm { position: absolute; left: 50%; top: 50%; transform: translate(-50%, -50%) rotate(-38deg); font-family: 'Oswald'; font-weight: 700;
      font-size: 150pt; color: rgba(0,0,0,.13); letter-spacing: .06em; white-space: nowrap; pointer-events: none; z-index: 9; }
.doc h1 { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 30pt; margin: 0 0 4pt; line-height: 1; }
.doc h2, .sec { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 13.5pt; margin: 10pt 0 4pt; letter-spacing: .02em; }
.doc h2 .acc, .sec .acc { color: ACCENT; }
.doc p, .doc li { font-size: 10.6pt; line-height: 1.32; margin: 0 0 4pt; }
.doc ul, .doc ol { margin: 0 0 4pt; padding-left: 15pt; }
.doc .rule { border-bottom: 2.2pt solid #000; margin-bottom: 6pt; padding-bottom: 6pt; }
.doc table { border-collapse: collapse; width: 100%; font-size: 10pt; margin: 2pt 0 4pt; }
.doc td, .doc th { border: 1pt solid #000; padding: 2.4pt 5pt; text-align: left; vertical-align: middle; }
.doc th, .tb th { font-family: 'Oswald'; font-weight: 500; text-transform: uppercase; font-size: 9.5pt; background: #000; color: #fff;
                  letter-spacing: .04em; }
.cols { display: flex; gap: 22pt; }
.cols > div { flex: 1; min-width: 0; }
.small { font-size: 9pt !important; color: #333; }
/* forms */
.fl { display: flex; align-items: flex-end; gap: 6pt; margin: 0 0 9pt; }
.fl b { white-space: nowrap; font-family: 'Oswald'; font-weight: 500; text-transform: uppercase; font-size: 10pt; letter-spacing: .05em; }
.fl span { flex: 1; border-bottom: 1pt solid #000; height: 15pt; }
.rl { border-bottom: .9pt solid #999; height: 21pt; }
.u { display: inline-block; border-bottom: 1pt solid #000; height: 13pt; vertical-align: -2pt; }
.ck { list-style: none; padding: 0; margin: 0 0 4pt; }
.ck li { display: flex; gap: 7pt; font-size: 10.5pt; line-height: 1.25; margin: 0 0 4pt; }
.ck li:before { content: ""; flex: 0 0 9pt; height: 9pt; border: 1.2pt solid #000; border-radius: 2pt; margin-top: 2pt; }
.box { border: 1.4pt solid #000; border-radius: 8pt; padding: 8pt 11pt; }
.when { display: flex; justify-content: space-between; align-items: flex-end; border-bottom: 1.6pt solid #000; margin: 9pt 0 5pt; padding-bottom: 2pt; }
.when .h { font-size: 13pt; }
.when .h i { font-style: normal; color: ACCENT; }
.when small { font-size: 9pt; color: #333; }
.tb { border-collapse: collapse; width: 100%; table-layout: fixed; }
.tb th { padding: 3pt 4pt; text-align: left; }
.tb td { border: 1pt solid #000; padding: 1pt 5pt; font-size: 10pt; }
.tb td.pre { font-size: 10pt; color: #222; }
.tb td.num { text-align: center; font-family: 'Oswald'; font-weight: 500; font-size: 10.5pt; }
/* handouts (programs, letters, notes) */
.ho { align-items: stretch; }
.big { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; text-align: center; line-height: 1; letter-spacing: .02em; }
.lite { font-family: 'Oswald'; font-weight: 300; text-align: center; }
.pr { display: flex; align-items: flex-end; gap: 8pt; height: 37pt; }
.pr .n { flex: 0 0 18pt; height: 18pt; border-radius: 50%; background: #000; color: #fff; font-family: 'Oswald'; font-weight: 500;
         font-size: 10pt; text-align: center; line-height: 18pt; margin-bottom: 1pt; }
.pr .t { flex: 1.25; border-bottom: 1pt dotted #000; height: 22pt; position: relative; }
.pr .p { flex: 1; border-bottom: 1pt dotted #000; height: 22pt; position: relative; }
.pr .t i, .pr .p i { position: absolute; left: 0; bottom: -10pt; font-style: normal; font-size: 7pt; color: #777; letter-spacing: .04em;
                     text-transform: uppercase; font-family: 'Oswald'; font-weight: 300; }
.phead { display: flex; align-items: center; gap: 10pt; margin: 10pt 0 2pt; }
.phead:before, .phead:after { content: ""; flex: 1; border-top: 1.4pt solid #000; }
.phead span { font-family: 'Oswald'; font-weight: 700; font-size: 16pt; letter-spacing: .28em; text-transform: uppercase; }
.cut { border-top: 1pt dashed #666; position: relative; margin: 0 -0.2in; }
.cut span { position: absolute; left: 50%; top: -7pt; transform: translateX(-50%); background: #fff; padding: 0 6pt; font-size: 8pt;
            color: #666; font-family: 'Oswald'; font-weight: 300; letter-spacing: .1em; text-transform: uppercase; }
.letter p { font-size: 12pt; line-height: 1.5; margin: 0 0 13pt; }
.cover { align-items: center; justify-content: space-between; padding: 0.55in 0.6in 0.5in; }
.store { font-family: 'Oswald'; font-weight: 500; font-size: 13pt; letter-spacing: .32em; text-transform: uppercase; }
.ctitle { text-align: center; }
.ctitle .a { font-family: 'Oswald'; font-weight: 700; font-size: 44pt; line-height: 1; letter-spacing: .02em; }
.ctitle .b { white-space: nowrap; font-family: 'Oswald'; font-weight: 700; font-size: 72pt; line-height: .95; letter-spacing: .01em; }
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


def text(x, y, s, size, weight=700, family="Oswald", anchor="middle", fill="#000", upper=False, extra=""):
    t = escape(s.upper() if upper else s)
    family = f"'{family}'" if " " in family else family
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{family}" font-weight="{weight}" font-size="{size}" '
            f'text-anchor="{anchor}" fill="{fill}" {extra}>{t}</text>')


def fl(label, extra=""):
    return f'<div class="fl" {extra}><b>{label}</b><span></span></div>'


def flrow(*labels, style=""):
    return f'<div style="display:flex;gap:16pt;{style}">' + "".join(f'<div style="flex:1">{fl(lab)}</div>' for lab in labels) + '</div>'


def rules(n, h=21):
    return "".join(f'<div class="rl" style="height:{h}pt"></div>' for _ in range(n))


def ck(items):
    return '<ul class="ck">' + "".join(f"<li><span>{it}</span></li>" for it in items) + "</ul>"


def blank(w_in):
    return f'<span class="u" style="width:{w_in}in"></span>'


def page(sub, tag, tagsub, inner, n, watermark=False, name=False, ak=False):
    return (f'<section class="page">{wm(watermark)}{top(sub, tag, tagsub, ak=ak)}{NAME if name else ""}'
            f'<div class="main">{inner}</div>{foot(f"Page {n}")}</section>')


def handout(inner, n, watermark=False, cls=""):
    return f'<section class="page ho {cls}">{wm(watermark)}<div class="main">{inner}</div>{foot(f"Page {n}")}</section>'


def notes_width(s, W, beats=4):
    return 2.6 * s + beats * W + 0.6 * s + 0.6 * s + 0.5 * s


def strip(key, s, W, fill="#000"):
    """The decorative 4/4 rhythm strip for `key`, as an inline SVG sized to fit."""
    p = STRIPS[key]
    w = notes_width(s, W) + 2 * s
    body, _, _ = R.engraved_pattern(p, s, 4.2 * s, s, W, fill=fill)
    return svg(round(w, 1), round(6.4 * s, 1), body, "display:block;margin:0 auto")


def snowrow(n, size, gap, fill="#fff", accent_every=2):
    """A row of snowflakes, alternate ones in the accent (outline only) so it still prints in black and white."""
    out = []
    for i in range(n):
        acc = i % accent_every == 0
        out.append(art("snowflake", i * (size + gap), 0, size, 1.5, fill=fill, line=ACCENT if acc else "#000"))
    return svg(n * (size + gap) - gap, size, "".join(out), "display:block;margin:0 auto")


# ---------------------------------------------------------------- plan and page index
PLAN = ["cover", "teacher", "timeline", "glance", "repertoire", "tracker", "rehearsal", "risers", "stage", "tech", "runshow",
        "letter", "reminder", "prog_a", "prog_b", "prog_c", "thanks_a", "thanks_b", "reflect", "terms"]
IX = {k: i + 1 for i, k in enumerate(PLAN)}

PARTS = [  # (label, first page key, last page key, use) for the teacher-notes table
    ("Planning timeline", "timeline", "timeline", "8 weeks out to the day after"),
    ("Concert at a glance", "glance", "glance", "all the key facts on one page"),
    ("Repertoire planner", "repertoire", "repertoire", "order, length, featured students"),
    ("Rehearsal tracker", "tracker", "tracker", "every piece, 12 rehearsals"),
    ("Rehearsal plans", "rehearsal", "rehearsal", "two plans per page"),
    ("Riser chart (choir)", "risers", "risers", "27 spots, 3 rows"),
    ("Stage setup (chairs)", "stage", "stage", "27 chairs in 3 arcs"),
    ("Stage & tech + volunteers", "tech", "tech", "checklist and sign-up"),
    ("Run of show", "runshow", "runshow", "concert-day schedule"),
    ("Parent letter", "letter", "letter", "with a return slip"),
    ("Reminder notes", "reminder", "reminder", "2 per page"),
    ("Programs A, B, C", "prog_a", "prog_c", "full page, half page (2 up), with names"),
    ("Thank-you notes", "thanks_a", "thanks_b", "8 designs, 4 per page"),
    ("Student reflection", "reflect", "reflect", "after the concert"),
    ("Terms of use", "terms", "terms", "license and credits"),
]


def prange(a, b):
    return str(IX[a]) if a == b else f"{IX[a]}–{IX[b]}"


# ---------------------------------------------------------------- teacher notes
def teacher_page(n):
    trs = "".join(f"<tr><td><b>{a}</b></td><td style='white-space:nowrap'>{prange(f, l)}</td><td>{u}</td></tr>" for a, f, l, u in PARTS)
    return (f'<section class="page doc"><div class="rule"><h1>Teacher Notes</h1>'
            f'<div class="l" style="font-size:13pt">{TITLE} + Program Kit · for any K–8 winter concert</div></div>'
            f'<div class="cols"><div>'
            f'<h2>What it is</h2>'
            f'<p>Everything you need to plan and run a winter concert, in one printable file: a planning timeline, '
            f'repertoire and rehearsal trackers, seating charts, a stage and tech checklist, a run of show, a parent letter, '
            f'reminder notes, three program layouts, thank-you notes and a student reflection.</p>'
            f'<h2>How to use it</h2><ol>'
            f'<li>Print the planner pages (pages {IX["timeline"]}–{IX["runshow"]}) and keep them in a concert binder or folder.</li>'
            f'<li>Start with <b>Concert at a Glance</b> (page {IX["glance"]}) and the <b>timeline</b> (page {IX["timeline"]}). '
            f'Write a target date next to each stage.</li>'
            f'<li>Send the <b>parent letter</b> about six weeks out and the <b>reminder notes</b> a few days before.</li>'
            f'<li>Fill in a <b>program</b>, proofread the names, then copy it for families.</li>'
            f'<li>After the concert, send <b>thank-you notes</b> and have students complete the <b>reflection</b>.</li></ol>'
            f'<h2>Filling it in</h2>'
            f'<p>Every page is designed to be written on by hand. You can also type onto any page with the “add text” '
            f'tool in most PDF readers before you print.</p>'
            f'<h2>Printing tips</h2><ul>'
            f'<li>All pages are US Letter and print well in black and white.</li>'
            f'<li>Program B and the reminder notes are two per page: cut on the dashed line. The thank-you notes are four per page.</li>'
            f'<li>Programs look great on light blue or gray paper; thank-you notes on card stock.</li></ul>'
            f'</div><div>'
            f'<h2>What’s inside</h2><table><tr><th>Part</th><th>Pages</th><th>Use</th></tr>{trs}</table>'
            f'<h2>For every school</h2>'
            f'<p>The kit is non-denominational: snowflakes, mittens, cocoa, music stands and drums, and nothing tied to a '
            f'particular celebration. Piece titles are left blank for you, so it works for choir, band, orchestra, general music '
            f'and whole-school concerts.</p>'
            f'<h2>Standards</h2><p>The rehearsal pages and student reflection support refining and presenting work for an '
            f'audience (National Core Arts Standards, Music, MU:Pr5.1 and MU:Pr6.1).</p>'
            f'<p class="small">All layouts, art and wording are original. No songs, lyrics or copyrighted characters are used.</p>'
            f'</div></div><div style="flex:1"></div>{foot(f"Page {n}")}</section>')


# ---------------------------------------------------------------- planner pages
TIMELINE = [
    ("8 weeks out", ["Confirm the date, time and room with the office", "Choose a snow date",
                     "Choose the music and check you have enough copies", "Put the concert on the school calendar"]),
    ("6 weeks out", [f"Send the parent letter (page {IX['letter']})", f"Start the rehearsal tracker (page {IX['tracker']})",
                     "Decide on concert attire", f"Ask for volunteers (page {IX['tech']})"]),
    ("4 weeks out", [f"Make the seating or riser chart (pages {IX['risers']}–{IX['stage']})",
                     "Book sound, lights and a piano tuning", f"Draft the program order (page {IX['repertoire']})",
                     "Confirm an accompanist if you need one"]),
    ("2 weeks out", ["Send reminder notes home", "Finish the program and proofread every name",
                     "Confirm volunteers, custodians and staff helpers", f"Plan the run of show (page {IX['runshow']})"]),
    ("Concert week", ["Dress rehearsal in the performance space", "Print and fold the programs",
                      "Set up risers, chairs and stands; do a sound check", "Pack folders, water and a spare-supplies box"]),
    ("Concert day", ["Post the run of show backstage", "Greet students at call time and warm up",
                     "Welcome families and thank your helpers", "Enjoy the music!"]),
    ("After the concert", [f"Send thank-you notes (pages {IX['thanks_a']}–{IX['thanks_b']})", "Return borrowed equipment",
                           f"Student reflection (page {IX['reflect']})", "Write notes for next year below"]),
]


def timeline_page(n, watermark=False):
    blocks = []
    for name, items in TIMELINE:
        blocks.append(f'<div class="when"><span class="h">{name}<i> ·</i></span><small>Target date {blank(1.05)}</small></div>{ck(items)}')
    left = "".join(blocks[:4])
    right = "".join(blocks[4:]) + f'<div class="sec" style="margin-top:8pt">Notes for next year<span class="acc"> ·</span></div>{rules(3, 20)}'
    inner = (f'<div class="how">Write a target date for each stage, then tick each box as you go.</div>'
             f'<div class="cols" style="gap:24pt">' f'<div>{left}</div><div>{right}</div></div>')
    return page("Planning timeline · 8 weeks to concert day", "TIMELINE", "Check it off", inner, n, watermark)


def glance_page(n):
    inner = (f'<div class="how">Keep this page at the front of your concert folder. Copy it for the office and your helpers.</div>'
             + fl("Concert name") + flrow("Date", "Start time") + flrow("Snow date", "End time (about)")
             + flrow("Place / room", "Dress rehearsal")
             + flrow("Student call time", "Call room")
             + fl("Classes / ensembles performing") + rules(2, 20)
             + fl("Concert attire") + rules(1, 20)
             + flrow("Accompanist", "Sound / tech")
             + flrow("Custodian / setup", "Office contact")
             + flrow("Programs needed", "Seats / chairs needed")
             + fl("Photo and video policy") + rules(1, 20)
             + f'<div class="sec">Notes<span class="acc"> ·</span></div>' + rules(8, 22))
    return page("Concert at a glance · the key facts", "OVERVIEW", "Fill in first", inner, n)


def repertoire_page(n):
    rows = "".join(f'<tr style="height:33pt"><td class="num">{i}</td><td></td><td></td><td></td><td></td><td></td></tr>' for i in range(1, 13))
    inner = (f'<div class="how">List the pieces in concert order. Add the minutes to check the concert length.</div>'
             f'<table class="tb"><colgroup><col style="width:24pt"><col style="width:150pt"><col style="width:100pt"><col style="width:84pt">'
             f'<col style="width:94pt"><col style="width:40pt"><col></colgroup>'
             f'<tr><th>#</th><th>Piece title</th><th>Composer / arranger</th><th>Class / group</th><th>Soloists / featured</th><th>Min.</th></tr>'
             f'{rows}<tr style="height:26pt"><td colspan="5" style="text-align:right;font-family:Oswald;font-weight:700;text-transform:uppercase">'
             f'Total music time</td><td></td></tr></table>'
             f'<div class="cols" style="margin-top:10pt;gap:20pt"><div class="doc">'
             f'<div class="sec" style="margin-top:0">Order tips<span class="acc"> ·</span></div><ul style="margin:0;padding-left:14pt">'
             f'<li style="font-size:10pt">Open with something confident and familiar.</li>'
             f'<li style="font-size:10pt">Alternate fast and slow, loud and quiet pieces.</li>'
             f'<li style="font-size:10pt">Plan stage changes between classes so there is no long wait.</li>'
             f'<li style="font-size:10pt">Finish with everyone together.</li></ul></div>'
             f'<div><div class="sec" style="margin-top:0">Music and rights<span class="acc"> ·</span></div>'
             f'<p style="font-size:10pt;margin:0 0 4pt">Note where each piece comes from (purchased, school library, public domain). '
             f'Keep any licence or receipt with this page.</p>{rules(2, 18)}</div></div>')
    return page("Repertoire planner · concert order", "MUSIC", "Plan the order", inner, n)


TRACK_COLS = 12


def tracker_page(n, watermark=False):
    head = "".join('<th style="padding:2pt 0"></th>' for _ in range(TRACK_COLS))
    dates = "".join('<td style="height:30pt"></td>' for _ in range(TRACK_COLS))
    rows = "".join(f'<tr style="height:33pt"><td class="num" style="text-align:left">{i}.</td>' + "".join("<td></td>" for _ in range(TRACK_COLS)) + "</tr>"
                   for i in range(1, 11))
    legend = (f'<div class="box" style="margin-top:10pt;display:flex;gap:16pt;font-size:10.5pt;justify-content:space-between">'
              + "".join(f'<span><b style="font-family:Oswald;font-size:13pt;color:{ACCENT}">{k}</b> {v}</span>'
                        for k, v in (("R", "read-through"), ("L", "learning notes &amp; rhythms"), ("P", "polishing: dynamics, blend"),
                                     ("S", "stage-ready")))
              + '</div>')
    inner = (f'<div class="how">Write the piece names down the side and the rehearsal dates across the top. '
             f'After each rehearsal, mark each piece R, L, P or S.</div>'
             f'<table class="tb"><colgroup><col style="width:150pt">' + "".join("<col>" for _ in range(TRACK_COLS)) + '</colgroup>'
             f'<tr><th>Piece</th>{head}</tr>'
             f'<tr><td style="font-family:Oswald;font-weight:500;text-transform:uppercase;font-size:9pt">Rehearsal dates</td>{dates}</tr>'
             f'{rows}</table>{legend}'
             f'<div class="sec">Next rehearsal, start with<span class="acc"> ·</span></div>{rules(3, 20)}')
    return page("Rehearsal tracker · 10 pieces × 12 rehearsals", "TRACKER", "Mark R · L · P · S", inner, n, watermark)


def rehearsal_block(k):
    return (f'<div class="box" style="flex:1;display:flex;flex-direction:column;justify-content:space-between;margin-bottom:{10 if k == 0 else 0}pt">'
            f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6pt">'
            f'<span class="h" style="font-size:15pt">Rehearsal plan</span>'
            f'<span style="font-family:Oswald;font-weight:500;font-size:11pt">REHEARSAL # {blank(0.5)}</span></div>'
            + flrow("Date", "Class / group", "Minutes")
            + '<div class="cols" style="gap:16pt"><div>'
            + fl("Warm-up") + rules(1, 18) + fl("Goal for today") + rules(1, 18)
            + '</div><div>'
            + '<div class="fl" style="margin-bottom:2pt"><b>Pieces &amp; sections</b><span style="border:0"></span><b>min</b></div>'
            + "".join(f'<div style="display:flex;gap:8pt"><div class="rl" style="flex:1;height:20pt"></div>'
                      f'<div class="rl" style="flex:0 0 30pt;height:20pt"></div></div>' for _ in range(5))
            + '</div></div>'
            + '<div>' + fl("Notes for next time") + rules(3, 20) + '</div></div>')


def rehearsal_page(n):
    inner = (f'<div class="how">Plan one rehearsal per box. Copy this page as many times as you need.</div>'
             f'<div style="flex:1;display:flex;flex-direction:column">{rehearsal_block(0)}{rehearsal_block(1)}</div>')
    return page("Rehearsal plans · 2 per page", "PLAN", "Rehearsals", inner, n)


# ---------------------------------------------------------------- seating charts
RISER_ROWS = [("Back row · step 3", 10), ("Middle row · step 2", 9), ("Front row · step 1", 8)]


def risers_svg():
    W, bw, bh, gap, step = 540, 46, 34, 6, 70
    out = []
    num = sum(c for _, c in RISER_ROWS)       # numbered front to back, left to right
    starts, k = {}, 1
    for r in range(len(RISER_ROWS) - 1, -1, -1):
        starts[r] = k
        k += RISER_ROWS[r][1]
    for r, (label, cnt) in enumerate(RISER_ROWS):
        y = r * step
        inset = r * 14
        out.append(f'<path d="M{inset},{y + step} L{inset + 6},{y} L{W - inset - 6},{y} L{W - inset},{y + step} Z" '
                   f'fill="{"#f1f4f8" if r % 2 == 0 else "#fff"}" stroke="#000" stroke-width="1.2" stroke-linejoin="round"/>')
        out.append(text(inset + 14, y + 13, label, 8.5, 500, anchor="start", upper=True, extra='letter-spacing="0.08em"'))
        row_w = cnt * bw + (cnt - 1) * gap
        x0 = (W - row_w) / 2
        for i in range(cnt):
            x = x0 + i * (bw + gap)
            out.append(f'<rect x="{x:.1f}" y="{y + 25}" width="{bw}" height="{bh}" rx="5" fill="#fff" stroke="#000" stroke-width="1.3"/>')
            out.append(text(x + 6, y + 34, str(starts[r] + i), 7, 500, anchor="start", fill="#666"))
    yb = len(RISER_ROWS) * step
    out.append(f'<rect x="{W / 2 - 46}" y="{yb + 26}" width="92" height="28" rx="14" fill="{ACCENT}" stroke="#000" stroke-width="1.3"/>')
    out.append(text(W / 2, yb + 44, "Director", 11, 500, fill="#fff", upper=True, extra='letter-spacing="0.08em"'))
    out.append(f'<rect x="{W - 112}" y="{yb + 18}" width="104" height="44" rx="4" fill="#fff" stroke="#000" stroke-width="1.3"/>')
    out.append(text(W - 60, yb + 36, "Piano", 11, 500, upper=True, extra='letter-spacing="0.08em"'))
    out.append(text(W - 60, yb + 52, "or accompaniment", 8, 300))
    out.append(f'<path d="M30,{yb + 84} L{W - 30},{yb + 84}" stroke="#000" stroke-width="1" stroke-dasharray="3 4"/>')
    out.append(text(W / 2, yb + 102, "Audience", 12, 700, upper=True, extra='letter-spacing="0.3em"'))
    return svg(W, yb + 108, "".join(out)), num


def risers_page(n, watermark=False):
    chart, num = risers_svg()
    inner = (f'<div style="margin-top:9pt">' + flrow("Class / group", "Concert date") + '</div>'
             f'<div class="how" style="margin-top:0">Write a singer’s name in each spot ({num} spots, numbered front to back). '
             f'Rows are staggered so every face shows between the two singers in front.</div>'
             f'<div style="display:flex;justify-content:center;margin:4pt 0 6pt">{chart}</div>'
             f'<div class="cols" style="gap:20pt"><div class="doc"><div class="sec" style="margin-top:2pt">Placement tips<span class="acc"> ·</span></div>'
             f'<ul style="margin:0;padding-left:14pt"><li style="font-size:10pt">Tallest singers on the back step, shortest in front.</li>'
             f'<li style="font-size:10pt">Strong singers in the middle of each section help the others.</li>'
             f'<li style="font-size:10pt">Leave an end spot free for a student who may need to step out.</li></ul></div>'
             f'<div><div class="sec" style="margin-top:2pt">Notes<span class="acc"> ·</span></div>{rules(3, 18)}</div></div>')
    return page("Riser chart · choir and singing classes", "SEATING", "Risers", inner, n, watermark)


STAGE_ROWS = [(115, 6), (180, 9), (245, 12)]   # (radius, chairs): inner to outer arc


def stage_svg():
    W, cx, cy, bw, bh, span = 540, 270, 300, 46, 26, 150
    out = [f'<rect x="2" y="2" width="112" height="58" rx="6" fill="#fff" stroke="#000" stroke-width="1.2" stroke-dasharray="5 4"/>',
           text(58, 26, "Percussion", 10, 500, upper=True, extra='letter-spacing="0.06em"'), text(58, 42, "or extra players", 8, 300),
           f'<rect x="{W - 114}" y="2" width="112" height="58" rx="6" fill="#fff" stroke="#000" stroke-width="1.2" stroke-dasharray="5 4"/>',
           text(W - 58, 26, "Piano", 10, 500, upper=True, extra='letter-spacing="0.06em"'), text(W - 58, 42, "or keyboard", 8, 300)]
    k = 1
    total = 0
    for r, cnt in STAGE_ROWS:
        total += cnt
        for i in range(cnt):
            a = 90 + span / 2 - (i + 0.5) * span / cnt          # left to right, as the conductor sees it from the front
            x = cx + r * math.cos(math.radians(a))
            y = cy - r * math.sin(math.radians(a))
            out.append(f'<g transform="translate({x:.1f} {y:.1f}) rotate({90 - a:.1f})">'
                       f'<rect x="{-bw / 2}" y="{-bh / 2}" width="{bw}" height="{bh}" rx="5" fill="#fff" stroke="#000" stroke-width="1.3"/>'
                       + text(-bw / 2 + 5, -bh / 2 + 8.5, str(k), 7, 500, anchor="start", fill="#666") + '</g>')
            k += 1
    out.append(f'<rect x="{cx - 50}" y="{cy + 10}" width="100" height="28" rx="14" fill="{ACCENT}" stroke="#000" stroke-width="1.3"/>')
    out.append(text(cx, cy + 28, "Conductor", 11, 500, fill="#fff", upper=True, extra='letter-spacing="0.08em"'))
    out.append(f'<path d="M30,{cy + 56} L{W - 30},{cy + 56}" stroke="#000" stroke-width="1" stroke-dasharray="3 4"/>')
    out.append(text(cx, cy + 74, "Audience", 12, 700, upper=True, extra='letter-spacing="0.3em"'))
    return svg(W, cy + 80, "".join(out)), total


def stage_page(n):
    chart, total = stage_svg()
    inner = (f'<div style="margin-top:9pt">' + flrow("Class / group", "Concert date") + '</div>'
             f'<div class="how" style="margin-top:0">For band, orchestra, recorders, Orff or a seated class: write a name and an instrument '
             f'in each chair ({total} chairs, numbered inner arc to outer arc).</div>'
             f'<div style="display:flex;justify-content:center;margin:2pt 0 6pt">{chart}</div>'
             f'<div class="cols" style="gap:20pt"><div>' + fl("Stands needed") + fl("Chairs needed") + '</div><div>'
             + fl("Mics / amps") + fl("Other setup") + '</div></div>'
             f'<div class="sec" style="margin-top:2pt">Notes<span class="acc"> ·</span></div>{rules(2, 18)}')
    return page("Stage setup · seated ensembles", "SEATING", "Chairs", inner, n)


# ---------------------------------------------------------------- stage, tech, volunteers, run of show
TECH = ["Risers set up, locked and checked", f"Chairs and stands placed (page {IX['stage']})", "Piano tuned and in place",
        "Microphones and sound check", "Stage lights and house lights checked", "Programs printed and at the door",
        "Greeters and ushers know their jobs", "Water for performers backstage", "Signs: restrooms, exits, seating",
        "Photo and video announcement ready", "Snow-day plan shared with families", "Spare-supplies box (tape, pencils, safety pins)"]
JOBS = ["Greeters / ushers", "Program handout", "Backstage helper", "Backstage helper", "Stage setup", "Clean-up",
        "Photos (school use)", "Refreshments (optional)", "", ""]


def tech_page(n):
    rows = "".join(f'<tr style="height:27pt"><td class="pre">{escape(j)}</td><td></td><td></td><td></td></tr>' for j in JOBS)
    inner = (f'<div class="sec">Stage &amp; tech checklist<span class="acc"> ·</span></div>'
             f'<div class="cols" style="gap:20pt"><div>{ck(TECH[:6])}</div><div>{ck(TECH[6:])}</div></div>'
             f'<div class="sec" style="margin-top:12pt">Volunteer sign-up<span class="acc"> ·</span></div>'
             f'<div class="how" style="margin-top:0">Helpers write their name next to a job. Check school rules for volunteers before the day.</div>'
             f'<table class="tb"><colgroup><col style="width:150pt"><col style="width:90pt"><col><col style="width:130pt"></colgroup>'
             f'<tr><th>Job</th><th>Time</th><th>Name</th><th>Contact</th></tr>{rows}</table>'
             f'<div class="sec" style="margin-top:12pt">Borrowed equipment to return<span class="acc"> ·</span></div>{rules(5, 20)}')
    return page("Stage & tech checklist · volunteer sign-up", "SETUP", "Before the day", inner, n)


RUN = ["Students arrive (call time)", "Warm-up", "Restroom break and line up", "Doors open for families", "Welcome and announcements",
       "", "", "", "", "", "", "", "", "Thank-yous", "Final piece (everyone)", "Students meet families", "Clean-up and lost & found"]


def runshow_page(n):
    rows = "".join(f'<tr style="height:34pt"><td></td><td class="pre">{escape(r)}</td><td></td><td></td></tr>' for r in RUN)
    inner = (f'<div style="margin-top:9pt">' + flrow("Concert", "Date") + '</div>'
             f'<div class="how" style="margin-top:0">Fill in the times and the pieces, then post a copy backstage and give one to each helper.</div>'
             f'<table class="tb"><colgroup><col style="width:62pt"><col style="width:200pt"><col style="width:120pt"><col></colgroup>'
             f'<tr><th>Time</th><th>What happens</th><th>Who</th><th>Notes</th></tr>{rows}</table>')
    return page("Run of show · concert-day schedule", "DAY OF", "Post backstage", inner, n)


# ---------------------------------------------------------------- handouts: letter, reminders
def letter_page(n, watermark=False):
    deco = svg(540, 46, art("mitten", 0, 0, 44, 1.5, fill=ACCENT) + art("snowflake", 60, 6, 32, 1.4, line=ACCENT)
               + art("stand", 248, 0, 44, 1.5) + art("snowflake", 448, 6, 32, 1.4, line=ACCENT) + art("drum", 496, 0, 44, 1.5),
               "display:block;margin:0 auto")
    slip = (f'<div class="cut" style="margin-top:22pt"><span>cut and return</span></div>'
            f'<div style="margin-top:12pt"><div class="h" style="font-size:14pt;margin-bottom:8pt">Winter concert return slip</div>'
            + flrow("Student", "Class") +
            f'<ul class="ck" style="font-size:11pt"><li><span>My child will perform in the concert.</span></li>'
            f'<li><span>My child cannot attend. Please tell me what to do instead.</span></li>'
            f'<li><span>I can help as a volunteer. Job: {blank(2.3)} Contact: {blank(1.9)}</span></li></ul>'
            + flrow("Parent / guardian signature", "Date", style="margin-top:8pt") + '</div>')
    inner = (f'{deco}<div class="big" style="font-size:30pt;margin-top:6pt">You’re invited to our winter concert!</div>'
             f'<div class="letter" style="margin-top:14pt">'
             f'<p>Dear Families,</p>'
             f'<p>Our students have been working hard on their music, and we would love for you to come and hear them!</p>'
             f'<p><b>Date:</b> {blank(2.2)} &nbsp; <b>Time:</b> {blank(1.4)} &nbsp; <b>Place:</b> {blank(1.6)}</p>'
             f'<p><b>Students arrive by:</b> {blank(1.3)} &nbsp; <b>Meet in:</b> {blank(2.6)}</p>'
             f'<p><b>What to wear:</b> {blank(5.5)}</p>'
             f'<p><b>Please bring:</b> {blank(5.6)}</p>'
             f'<p><b>Pick-up:</b> {blank(6.1)}</p>'
             f'<p>If school is closed for weather, the concert moves to {blank(2.6)}.</p>'
             f'<p>Thank you for supporting music at our school. Please return the slip below by {blank(1.6)}.</p>'
             f'<p style="margin:0">With thanks,</p><p style="margin-top:14pt">{blank(2.8)}<br><span class="small">Music teacher</span></p>'
             f'</div>{slip}')
    return handout(inner, n, watermark)


def reminder_half():
    return (f'<div style="flex:1;display:flex;gap:18pt;align-items:center;padding:6pt 4pt">'
            f'<div style="flex:0 0 1.55in">{svg(110, 150, art("snowflake", 30, 0, 52, 1.6, line=ACCENT) + art("mitten", 0, 50, 70, 1.6, fill=ACCENT) + art("hat", 56, 78, 54, 1.5))}</div>'
            f'<div style="flex:1"><div class="big" style="font-size:30pt;text-align:left">Concert reminder!</div>'
            f'<div class="lite" style="text-align:left;font-size:13pt;margin:3pt 0 12pt">Our winter concert is almost here. We can’t wait to see you!</div>'
            + flrow("Date", "Time") + fl("Place") + flrow("Arrive by", "Meet in") + fl("Wear") + fl("Bring")
            + '</div></div>')


def reminder_page(n):
    inner = (f'<div style="flex:1;display:flex;flex-direction:column">{reminder_half()}'
             f'<div class="cut"><span>cut here</span></div>{reminder_half()}</div>')
    return handout(inner, n)


# ---------------------------------------------------------------- programs
def prow(i, compact=False):
    return (f'<div class="pr" style="{"height:27pt" if compact else ""}"><div class="n">{i}</div>'
            f'<div class="t">{"<i>piece</i>" if i == 1 else ""}</div><div class="p">{"<i>performed by</i>" if i == 1 else ""}</div></div>')


def program_a(n, watermark=False):
    rows = "".join(prow(i) for i in range(1, 11))
    inner = (f'<div style="margin-top:6pt">{snowrow(9, 34, 30)}</div>'
             f'<div style="text-align:center;margin-top:12pt">{blank(4.2)}<div class="small" style="margin-top:2pt">school or ensemble</div></div>'
             f'<div class="big" style="font-size:50pt;margin-top:6pt">Winter Concert</div>'
             f'<div style="margin-top:6pt">{strip("prog_a", 5, 40)}</div>'
             f'<div style="display:flex;gap:14pt;margin-top:10pt">' + "".join(f'<div style="flex:1">{fl(lab)}</div>' for lab in ("Date", "Time", "Place"))
             + '</div>'
             f'<div class="phead"><span>Program</span></div>{rows}'
             f'<div style="display:flex;gap:16pt;margin-top:30pt">'
             f'<div class="box" style="flex:1"><div class="h" style="font-size:12pt;margin-bottom:4pt">Concert manners</div>'
             f'<div style="font-size:10pt;line-height:1.35">Please silence phones · Stay seated while the music plays · '
             f'Clap at the end of each piece · Enjoy!</div></div>'
             f'<div style="flex:1.2"><div class="h" style="font-size:12pt;margin-bottom:2pt">Special thanks</div>{rules(2, 19)}</div></div>')
    return handout(inner, n, watermark)


def program_b_half():
    rows = "".join(prow(i, compact=True) for i in range(1, 9))
    return (f'<div style="flex:1;display:flex;gap:20pt;padding:8pt 0 6pt">'
            f'<div style="flex:0 0 2.45in;display:flex;flex-direction:column;align-items:center;text-align:center">'
            f'{svg(150, 52, art("snowflake", 0, 10, 36, 1.4, line=ACCENT) + art("stand", 48, 0, 52, 1.5) + art("snowflake", 112, 10, 36, 1.4, line=ACCENT))}'
            f'<div class="big" style="font-size:30pt;margin-top:6pt">Winter<br>Concert</div>'
            f'<div style="margin-top:4pt">{strip("prog_b", 3.4, 28)}</div>'
            f'<div style="width:100%;margin-top:8pt">{fl("School")}{fl("Date")}{fl("Time")}</div>'
            f'<div class="small" style="line-height:1.3">Please silence phones and clap at the end of each piece.</div></div>'
            f'<div style="flex:1;display:flex;flex-direction:column;justify-content:center"><div class="phead" style="margin-top:0"><span>Program</span></div>{rows}</div></div>')


def program_b(n, watermark=False):
    inner = (f'<div style="flex:1;display:flex;flex-direction:column">{program_b_half()}'
             f'<div class="cut"><span>cut here · 2 programs per page</span></div>{program_b_half()}</div>')
    return handout(inner, n, watermark)


def program_c(n):
    rows = "".join(prow(i, compact=True) for i in range(1, 9))
    names = "".join(f'<div style="flex:1">{rules(12, 19)}</div>' for _ in range(4))
    inner = (f'<div style="display:flex;align-items:center;gap:14pt;margin-top:4pt">'
             f'<div>{svg(92, 80, art("snowflake", 0, 0, 44, 1.5, line=ACCENT) + art("mug", 36, 26, 54, 1.5, fill=ACCENT))}</div>'
             f'<div style="flex:1"><div class="big" style="font-size:40pt;text-align:left">Winter Concert</div>'
             f'<div style="display:flex;gap:12pt;margin-top:8pt">' + "".join(f'<div style="flex:1">{fl(lab)}</div>' for lab in ("School", "Date", "Time"))
             + f'</div></div><div>{strip("prog_c", 3.6, 26)}</div></div>'
             f'<div class="phead"><span>Program</span></div>{rows}'
             f'<div class="phead" style="margin-top:14pt"><span>Our performers</span></div>'
             f'<div style="display:flex;gap:16pt">{names}</div>'
             f'<div style="display:flex;gap:16pt;margin-top:12pt"><div style="flex:1">{fl("Director")}</div><div style="flex:1">{fl("Accompanist")}</div></div>')
    return handout(inner, n)


# ---------------------------------------------------------------- thank-you notes
THANKS = [
    ("snowflake", "for helping with our winter concert!"),
    ("stand", "for helping our music shine!"),
    ("mitten", "for setting up our stage!"),
    ("drum", "for cheering us on!"),
    ("mug", "for coming to our concert!"),
    ("hat", "for all your help backstage!"),
    ("stand", "for making music with us!"),
    ("snowflake", "for keeping our school ready for the big night!"),
]


def thank_card(pic, msg):
    a = (art(pic, 0, 0, 58, 1.6, fill=ACCENT) if pic != "snowflake" else art(pic, 0, 0, 58, 1.6, line=ACCENT))
    return (f'<div style="flex:1;display:flex;flex-direction:column;align-items:center;padding:14pt 18pt 10pt;text-align:center">'
            f'{svg(58, 58, a)}<div class="big" style="font-size:36pt;margin-top:8pt">Thank you</div>'
            f'<div class="lite" style="font-size:14pt;margin-top:3pt;min-height:36pt">{escape(msg)}</div>'
            f'<div style="width:100%;margin-top:6pt">{fl("To")}{rules(3, 20)}<div style="margin-top:8pt">{fl("From")}</div></div></div>')


def thanks_page(k, n, watermark=False):
    cards = [thank_card(*THANKS[k * 4 + i]) for i in range(4)]
    vline = '<div style="border-left:1pt dashed #666"></div>'
    inner = (f'<div style="flex:1;display:flex;flex-direction:column">'
             f'<div style="flex:1;display:flex">{cards[0]}{vline}{cards[1]}</div>'
             f'<div class="cut"><span>cut on the dashed lines</span></div>'
             f'<div style="flex:1;display:flex">{cards[2]}{vline}{cards[3]}</div></div>')
    return handout(inner, n, watermark)


# ---------------------------------------------------------------- reflection
def reflect_page(n):
    flakes = svg(5 * 44 - 10, 34, "".join(art("snowflake", i * 44, 0, 34, 1.5) for i in range(5)))
    inner = (f'<div class="how">Think back to the concert and answer in words or pictures.</div>'
             f'<div class="box" style="height:3.3in;position:relative"><div class="h" style="font-size:12pt">Draw yourself performing</div></div>'
             f'<div style="margin-top:12pt">' + fl("My favorite piece was") + fl("because") + rules(1, 20) + '</div>'
             f'<div style="margin-top:6pt">' + fl("Something I did well") + rules(1, 20) + '</div>'
             f'<div style="margin-top:6pt">' + fl("Something I want to get better at") + rules(1, 20) + '</div>'
             f'<div style="margin-top:6pt">' + fl("When the audience clapped, I felt") + '</div>'
             f'<div style="display:flex;align-items:center;gap:14pt;margin-top:10pt"><b style="font-family:Oswald;font-weight:500;'
             f'text-transform:uppercase;font-size:10pt;letter-spacing:.05em">My effort · color the snowflakes</b>{flakes}</div>')
    return page("Concert reflection · for students", "REFLECT", "After the concert", inner, n, name=True)


# ---------------------------------------------------------------- terms
def terms_page(n):
    return (f'<section class="page doc"><div class="rule"><h1>Terms of Use</h1>'
            f'<div class="l" style="font-size:13pt">Thank you for your purchase!</div></div>'
            f'<p>© {YEAR} {STORE}. {BRAND} by {STORE}. All rights reserved. This purchase gives <b>one teacher</b> a license to use this resource with their own students.</p>'
            f'<h2>You may</h2><ul><li>Print and copy pages for your own classroom and students, year after year.</li>'
            f'<li>Send copies of the programs, parent letter, reminder notes and thank-you notes to your own students’ families and helpers.</li>'
            f'<li>Share pages with your own students through a password-protected class site or learning platform.</li>'
            f'<li>Use the pages with your own students when you have a substitute teacher.</li></ul>'
            f'<h2>You may not</h2><ul><li>Share, email or copy this resource for other teachers, a whole school or a district. '
            f'Additional licenses are available on Teachers Pay Teachers.</li>'
            f'<li>Post any part of it on a public website, shared drive or social media.</li>'
            f'<li>Sell, give away or claim any part of it as your own, or edit it into a new product.</li></ul>'
            f'<h2>Questions?</h2><p>Please use the Q&amp;A tab on the {BRAND} by {STORE} store on Teachers Pay Teachers. '
            f'If something looks wrong, let me know there and I will fix it.</p>'
            f'<h2>Credits</h2><ul>'
            f'<li>Art, layouts, wording and rhythm patterns: original work, {BRAND} by {STORE}.</li>'
            f'<li>Music notation font: Bravura © Steinberg Media Technologies GmbH, SIL Open Font License 1.1.</li>'
            f'<li>Text fonts: Oswald (The Oswald Project Authors) and Source Sans 3 (Adobe), SIL Open Font License 1.1.</li></ul>'
            f'<p class="small">Designed with the help of digital and AI tools, and checked by hand.</p>'
            f'<div style="flex:1"></div>{foot(f"Page {n}")}</section>')


# ---------------------------------------------------------------- cover art
def mock_program():
    """A small drawn program (accent and black only), 220 x 320, for the cover."""
    A = ACCENT
    s, W = 4.0, 30
    nw = notes_width(s, W)
    body, _, _ = R.engraved_pattern(STRIPS["cover"], 110 - nw / 2, 104, s, W)
    rows = []
    for i in range(7):
        y = 160 + i * 22
        rows.append(f'<circle cx="34" cy="{y - 4}" r="7" fill="#000"/>' + text(34, y - 0.6, str(i + 1), 9, 500, fill="#fff")
                    + f'<line x1="48" y1="{y}" x2="196" y2="{y}" stroke="#000" stroke-width="1.2" stroke-dasharray="1 3.2" stroke-linecap="round"/>')
    return (f'<rect x="0" y="0" width="220" height="320" rx="6" fill="#fff" stroke="#000" stroke-width="3"/>'
            + art("snowflake", 94, 12, 32, 1.4, line=A)
            + text(110, 74, "WINTER CONCERT", 23, 700, extra='letter-spacing="0.02em"') + body
            + f'<line x1="22" y1="133" x2="76" y2="133" stroke="#000" stroke-width="1.4"/><line x1="144" y1="133" x2="198" y2="133" stroke="#000" stroke-width="1.4"/>'
            + text(110, 137.5, "PROGRAM", 12, 700, extra='letter-spacing="0.24em"') + "".join(rows))


def mock_clipboard():
    A = ACCENT
    out = [f'<rect x="0" y="0" width="150" height="214" rx="10" fill="#fff" stroke="#000" stroke-width="3"/>',
           f'<rect x="45" y="-12" width="60" height="26" rx="6" fill="{A}" stroke="#000" stroke-width="2.4"/>',
           text(75, 40, "CONCERT", 13, 700, extra='letter-spacing="0.12em"'), text(75, 55, "CHECKLIST", 9, 500, extra='letter-spacing="0.2em"')]
    for i in range(6):
        y = 72 + i * 22
        out.append(f'<rect x="16" y="{y}" width="13" height="13" rx="2" fill="#fff" stroke="#000" stroke-width="1.8"/>')
        out.append(f'<line x1="38" y1="{y + 10}" x2="{132 - (i % 3) * 14}" y2="{y + 10}" stroke="#000" stroke-width="1.6" stroke-linecap="round"/>')
        if i < 3:
            out.append(f'<path d="M18,{y + 6} L23,{y + 12} L33,{y - 3}" fill="none" stroke="{A}" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"/>')
    return "".join(out)


def hero_svg(width_css):
    A = ACCENT
    prog = f'<g transform="translate(196 22) rotate(-4 110 160)">{mock_program()}</g>'
    clip = f'<g transform="translate(410 70) rotate(6 75 107)">{mock_clipboard()}</g>'
    deco = (art("stand", 36, 96, 150, 2.6, fill=A) + art("snowflake", 26, 8, 80, 2.4, line=A, rotate=8)
            + art("snowflake", 140, 22, 40, 1.8, rotate=-10) + art("snowflake", 494, 4, 58, 2.0, rotate=12)
            + art("mug", 14, 270, 78, 2.2) + art("drum", 120, 268, 80, 2.2, fill=A)
            + art("mitten", 520, 282, 72, 2.2, fill=A, rotate=14) + art("snowflake", 448, 300, 44, 1.8, line=A))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 360" width="{width_css}" style="display:block">'
            f'{prog}{clip}{deco}</svg>')


def cover_page():
    return (f'<section class="page cover"><div class="store">{BRAND}</div>'
            f'<div style="width:6.9in">{hero_svg("100%")}</div>'
            f'<div class="ctitle"><div class="a">WINTER CONCERT</div><div class="b">PLANNER KIT</div>'
            f'<div class="c">Programs · seating charts · rehearsal tracker · parent letter · thank-you notes</div></div>'
            f'<div class="cband">Grades K–8 <em>·</em> 3 program layouts <em>·</em> {len(PLAN)} pages <em>·</em> print &amp; go</div></section>')


# ---------------------------------------------------------------- assemble
def render_page(key, watermark=False):
    n = IX[key]
    return {
        "cover": cover_page, "teacher": lambda: teacher_page(n), "timeline": lambda: timeline_page(n, watermark),
        "glance": lambda: glance_page(n), "repertoire": lambda: repertoire_page(n), "tracker": lambda: tracker_page(n, watermark),
        "rehearsal": lambda: rehearsal_page(n), "risers": lambda: risers_page(n, watermark), "stage": lambda: stage_page(n),
        "tech": lambda: tech_page(n), "runshow": lambda: runshow_page(n), "letter": lambda: letter_page(n, watermark),
        "reminder": lambda: reminder_page(n), "prog_a": lambda: program_a(n, watermark), "prog_b": lambda: program_b(n, watermark),
        "prog_c": lambda: program_c(n), "thanks_a": lambda: thanks_page(0, n, watermark), "thanks_b": lambda: thanks_page(1, n),
        "reflect": lambda: reflect_page(n), "terms": lambda: terms_page(n),
    }[key]()


PREVIEW_PICKS = ["prog_a", "timeline", "risers", "thanks_a"]


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
        f'<div style="width:840px;margin-top:14px">{hero_svg("100%")}</div>'
        f'<div class="hd" style="font-size:66px;margin-top:6px">Winter Concert</div>'
        f'<div class="hd" style="font-size:122px">Planner Kit</div>'
        f'<div class="sub" style="font-size:28px;margin-top:10px">Programs · seating charts · rehearsal tracker · parent letter · thank-yous</div>'
        f'<div class="band">Grades K–8 <em>·</em> 3 program layouts <em>·</em> {len(PLAN)} pages</div></div>')


def preview_square_1(img):
    items = [(img[0], "Programs", "3 layouts, ready to copy"), (img[1], "Rehearsal tracker", "10 pieces × 12 rehearsals"),
             (img[2], "Seating charts", "risers and chairs")]
    shots = "".join(
        f'<div style="width:290px"><div class="shot"><img src="{src}"><div class="swm" style="font-size:64px">PREVIEW</div></div>'
        f'<div class="lbl">{a}<span>{b}</span></div></div>' for src, a, b in items)
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div>'
        f'<div class="hd" style="font-size:76px;margin-top:20px">Plan it · run it</div>'
        f'<div class="sub" style="font-size:27px;margin-top:8px">From the first rehearsal to the last bow, on paper</div>'
        f'<div style="display:flex;gap:28px;margin-top:100px;align-items:flex-start">{shots}</div>'
        f'<div class="band">Print &amp; go <em>·</em> fill in by hand <em>·</em> black-and-white friendly</div></div>')


def preview_square_2(a, b):
    pair = "".join(
        f'<div style="position:absolute;left:{x}px;top:{y}px;width:520px"><div class="shot"><img src="{src}">'
        f'<div class="swm" style="font-size:110px">PREVIEW</div></div>'
        f'<div class="lbl" style="position:absolute;{side}:-2px;top:-44px;margin:0">{lab}</div></div>'
        for src, lab, x, y, side in ((a, "Parent letter", 56, 250, "left"), (b, "Thank-you notes", 424, 330, "right")))
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div>'
        f'<div class="hd" style="font-size:72px;margin-top:20px">Families &amp; helpers</div>'
        f'<div class="sub" style="font-size:27px;margin-top:8px">Parent letter with return slip, reminder notes, 8 thank-you designs</div>'
        f'{pair}'
        f'<div class="band">Non-denominational <em>·</em> works for any school</div></div>')


def preview_square_3(imgs):
    cells = "".join(
        f'<div style="width:196px"><div class="shot" style="box-shadow:5px 5px 0 #000"><img src="{src}">'
        f'<div class="swm" style="font-size:44px">PREVIEW</div></div><div class="lbl" style="font-size:17px;margin-top:9px">{lab}</div></div>'
        for src, lab in imgs)
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div>'
        f'<div class="hd" style="font-size:70px;margin-top:16px">Every planning page</div>'
        f'<div class="sub" style="font-size:27px;margin-top:8px">Timeline, concert facts, repertoire, rehearsals, setup and the day itself</div>'
        f'<div style="display:grid;grid-template-columns:repeat(4,196px);gap:20px 26px;margin-top:34px">{cells}</div>'
        f'<div class="band">{len(PLAN)} pages <em>·</em> US Letter PDF</div></div>')


SHOTS1 = ["prog_a", "tracker", "risers"]
SHOTS2 = ["letter", "thanks_a"]
SHOTS3 = [("timeline", "Timeline"), ("glance", "At a glance"), ("repertoire", "Repertoire"), ("rehearsal", "Rehearsal plans"),
          ("stage", "Stage setup"), ("tech", "Tech + volunteers"), ("runshow", "Run of show"), ("reflect", "Reflection")]


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
        "grades": ["not-grade-specific"],
        "subjects": ["Music"],
        "tags": ["Winter"],
        "formats": ["PDF"],
        "pages": pages,
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
BEATS = {"q": 1, "e": 1, "r": 1, "h": 2}      # independent of R.TOKENS; the check compares the two


def pattern_errors(label, p):
    errs = []
    if any(t not in BEATS for t in p):
        return [f"{label} {p}: unknown token"]
    if sum(BEATS[t] for t in p) != 4 or R.beats(p) != 4:
        errs.append(f"{label} {p}: not one bar of 4/4")
    b = 0
    for t in p:
        if t == "h" and b not in (0, 2):
            errs.append(f"{label} {p}: half note starts on beat {b + 1} (must be 1 or 3)")
        b += BEATS[t]
    return errs


def verify_data():
    errs = []
    for t in BEATS:
        if R.TOKENS[t]["beats"] != BEATS[t]:
            errs.append(f"token {t}: 002's table disagrees on beats")
    for k, p in STRIPS.items():
        errs += pattern_errors(f"strip {k}", p)
    if len(PLAN) != len(set(PLAN)):
        errs.append("plan has a repeated page")
    for _, a, b, _ in PARTS:
        if a not in IX or b not in IX or IX[a] > IX[b]:
            errs.append(f"teacher table range {a}-{b} is wrong")
    covered = set()
    for _, a, b, _ in PARTS:
        covered |= set(PLAN[IX[a] - 1:IX[b]])
    if covered | {"cover", "teacher"} != set(PLAN):
        errs.append(f"teacher table misses pages: {sorted(set(PLAN) - covered - {'cover', 'teacher'})}")
    if len(THANKS) != 8 or len({m for _, m in THANKS}) != 8:
        errs.append("need 8 different thank-you messages")
    if sum(c for _, c in RISER_ROWS) != 27 or sum(c for _, c in STAGE_ROWS) != 27:
        errs.append("seating counts changed: update the teacher table and UPLOAD.md (27 spots / 27 chairs)")
    for name, cp in {"noteQuarterUp": 0xE1D5, "noteHalfUp": 0xE1D3, "noteheadBlack": 0xE0A4, "timeSig4": 0xE084}.items():
        if R.GLYPH[name][0] != cp:
            errs.append(f"{name} codepoint wrong")
    return errs


def pdf_fonts(path):
    out = subprocess.run(["pdffonts", path], capture_output=True, text=True, check=True).stdout.splitlines()[2:]
    return [(ln.split()[0], ln.split()[-5]) for ln in out]


def footer_errors(path, safe=0.35 * 72):
    """Every page but the cover has its footer, and it sits inside the safe margin (content that overflows pushes it off the page)."""
    out = subprocess.run(["pdftotext", "-bbox", path, "-"], capture_output=True, text=True, check=True).stdout
    errs = []
    for i, pg in enumerate(re.findall(r'<page width="([\d.]+)" height="([\d.]+)">(.*?)</page>', out, re.S)):
        ph = float(pg[1])
        ys = [float(m) for m in re.findall(r'yMax="([\d.]+)">Lotze', pg[2])]
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
    for path, items in ((PDF, PLAN), (PREVIEW_PDF, PREVIEW_PICKS)):
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
        for name, _ in fonts:
            if not re.search(r"bravura|oswald|sourcesans", name.lower()):
                errs.append(f"{os.path.basename(path)}: unexpected font {name} (a glyph fell back to a system font)")
    rd = PdfReader(PDF)
    txt = [pg.extract_text().replace("\n", " ") for pg in rd.pages]
    for i, t in enumerate(txt):
        if i > 0 and "Brian Lotze · Hudson Beat" not in t:
            errs.append(f"page {i + 1}: footer missing")
        if i > 0 and f"Page {i + 1}" not in t:
            errs.append(f"page {i + 1}: page number in the footer is wrong")
    alltext = " ".join(txt).lower()
    for bad in BANNED:
        if re.search(rf"\b{bad.strip()}", alltext):
            errs.append(f"resource text mentions '{bad.strip()}' (must stay non-denominational)")
    # every "page N" / "pages N–M" cross-reference points at a page that exists
    for m in re.finditer(r"pages? (\d+)(?:–(\d+))?", " ".join(txt[1:])):
        for g in m.groups():
            if g and not 1 <= int(g) <= len(PLAN):
                errs.append(f"cross-reference to page {g} does not exist")
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
    elif any(b in m2.group(1).lower() for b in BANNED):
        errs.append("UPLOAD.md: description uses a holiday word")
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
    print(f"CHECK OK: {len(PLAN)} Letter pages with footers and correct page numbers, teacher table covers every page, "
          f"cross-references in range; rhythm strips {', '.join(STRIPS.values())} each one bar of 4/4 (half notes on beat 1 or 3); "
          f"no holiday words; only Bravura/Oswald/Source Sans 3, all embedded; preview {len(PREVIEW_PICKS)} watermarked pages; "
          f"images 2000x2000; tpt.json and UPLOAD.md ok (title length matches its stated count).")


if __name__ == "__main__":
    if "--check" in sys.argv:
        check()
    else:
        build()
