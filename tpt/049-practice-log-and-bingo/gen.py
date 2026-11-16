#!/usr/bin/env python3
"""Practice Log and Practice Bingo (TpT 049): build the resource and verify it.

    python3 gen.py           build everything (PDFs, PNGs, UPLOAD.md, tpt.json) into this folder
    python3 gen.py --check   re-read the rendered pages and verify every number, the bingo boards and the layout

--check does not trust the lists in this file. It loads the rendered HTML in Chromium, reads back what is really on the pages
(every bingo square, every caller-sheet row, every tracker cell and total, every printed sum) and recomputes from that.

Rendering uses Playwright + Chromium (HTML/SVG -> PDF/PNG) with the OFL fonts in ../fonts.
"""
import json
import math
import os
import random
import re
import subprocess
import sys
from html import escape

HERE = os.path.dirname(os.path.abspath(__file__))
TPT = os.path.dirname(HERE)
FONTS = os.path.join(TPT, "fonts")
BUILD = os.path.join(HERE, "build")
RENDER_JS = os.path.join(TPT, "tools", "render.js")

SLUG = "practice-log-and-bingo"
PDF = os.path.join(HERE, f"{SLUG}.pdf")
PREVIEW_PDF = os.path.join(HERE, f"{SLUG}-PREVIEW.pdf")
COVER_PNG = os.path.join(HERE, "cover.png")
PREVIEW_PNGS = [os.path.join(HERE, f"preview-{i}.png") for i in (1, 2, 3)]
UPLOAD = os.path.join(HERE, "UPLOAD.md")
TPT_JSON = os.path.join(HERE, "tpt.json")

STORE = "Brian Lotze"
BRAND = "Hudson Beat"
YEAR = 2026
ACCENT = "#1E8E7E"      # teal: the one accent of this product
TINT = "#D6EEE9"        # pale tint of the accent
DISCLOSURE = "Created with the help of digital and AI tools. Notation and answer keys are verified before release."
TITLE = "Practice Log & Bingo"
LISTING_TITLE = "Music Practice Log & Practice Bingo | Band Orchestra Choir Piano Guitar Gr 4-8"
PRICE = "3.00"
TAGS = ["Games", "Activities", "Printables", "Homework", "Classroom Management", "Study Skills"]
SUBJECTS = ["Music", "Instrumental Music", "Vocal Music"]
GRADES = ["4th-grade", "5th-grade", "6th-grade", "7th-grade"]

# ------------------------------------------------------------------ content
GROUPS = {
    "A": ["Play your slowest section 3 times", "Practice with a metronome", "Warm up for 5 minutes before you start",
          "Check your tuning or starting note", "Sit or stand tall for a whole practice", "Practice in a new spot at home",
          "Practice at the same time two days in a row", "Play your piece all the way through once"],
    "B": ["Clap a tricky rhythm before you play it", "Count out loud while you play", "Circle three hard spots in your music",
          "Say the note names in one line of music", "Find every repeat sign and mark it", "Sight-read a new line of music",
          "Play a hard measure 5 times in a row", "Write the counts above one measure"],
    "C": ["Play it loud, then play it soft", "Record yourself and listen back", "Play for one minute with your best tone",
          "Play a phrase as smoothly as you can", "Take a deep breath before every phrase", "Play a scale or warm-up from memory",
          "Play a line fast, then slow", "Add a crescendo to one phrase"],
    "D": ["Teach someone a rhythm", "Play for a family member", "Play for a pet or a stuffed animal",
          "Make up a short tune of your own", "Play along with a recording you like", "Play your favorite piece twice",
          "Tap the rhythm of a song you know", "Invent a new warm-up"],
    "E": ["Write a practice goal before you start", "Practice 10 minutes without stopping", "Fix one mistake, then play it right 3 times",
          "Practice 20 minutes in one day", "Practice 3 days in a row", "Set out your music the night before",
          "Ask your teacher one question", "Take care of your instrument or voice"],
    "F": ["Write one thing you did well today", "Write one thing you want to improve", "Rate your practice from 1 to 5",
          "Listen to a performer you admire", "Practice a spot, rest, then play it again", "Play your piece for a friend",
          "Listen to a style of music that is new to you", "Play a duet or echo with a classmate"],
}
BOARD_GROUPS = [["A", "B", "C"], ["A", "D", "E"], ["B", "D", "F"], ["C", "E", "F"]]
CHALLENGES = [t for g in "ABCDEF" for t in GROUPS[g]]          # challenge number n is CHALLENGES[n - 1]
NCH = len(CHALLENGES)                                           # 48
PER_BOARD = 24
NBOARDS = len(BOARD_GROUPS)
APPEARS = NBOARDS * PER_BOARD // NCH                            # each challenge appears on this many boards (2)
SHARED = 8                                                      # challenges any two boards share


def build_boards():
    start = {g: i * 8 + 1 for i, g in enumerate("ABCDEF")}
    boards = []
    for b, groups in enumerate(BOARD_GROUPS):
        nums = [start[g] + k for g in groups for k in range(8)]
        random.Random(4900 + b).shuffle(nums)
        nums.insert(12, 0)             # 0 = FREE, centre of the 5x5 grid
        boards.append(nums)
    return boards


BOARDS = build_boards()

# ------------------------------------------------------------------ page map
P_COVER, P_TEACH, P_PARENT, P_WIN = 1, 2, 3, 4
P_LOG0 = 5
NLOGS = 4
P_TRACK = P_LOG0 + NLOGS          # 9
P_CALL = P_TRACK + 1              # 10
P_BOARD0 = P_CALL + 1             # 11
P_TERMS = P_BOARD0 + NBOARDS      # 15
TOTAL_PAGES = P_TERMS

TRACK_DAYS = 30
TRACK_COLS = 7
TRACK_WEEKS = 5
STREAKS = [5, 10, 20, 30]
GOALS = [10, 15, 20, 30]
RUBRIC = [("Weekly logs filled in and returned", 40, "4 logs, 10 points each"),
          ("Practice minutes goal met", 30, "total on the 30-day tracker"),
          ("Practice Bingo", 20, "5 points for each line, up to 20"),
          ("Goals and reflection lines completed", 10, "on the weekly logs")]


# ------------------------------------------------------------------ css
def font_css():
    f = os.path.relpath(FONTS, BUILD)
    faces = [("Oswald", 300, "normal", "oswald-latin-300-normal"), ("Oswald", 500, "normal", "oswald-latin-500-normal"),
             ("Oswald", 700, "normal", "oswald-latin-700-normal"),
             ("Source Sans 3", 400, "normal", "source-sans-3-latin-400-normal"),
             ("Source Sans 3", 400, "italic", "source-sans-3-latin-400-italic"),
             ("Source Sans 3", 600, "normal", "source-sans-3-latin-600-normal"),
             ("Source Sans 3", 700, "normal", "source-sans-3-latin-700-normal")]
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
.tag { text-align: right; flex: 0 0 auto; margin-left: 12pt; }
.tag .lv { display: inline-block; background: #000; color: #fff; font-family: 'Oswald'; font-weight: 700; font-size: 15pt; padding: 3pt 9pt 4pt; border-radius: 4pt; letter-spacing: .04em; }
.tag .ln { font-family: 'Oswald'; font-weight: 300; font-size: 11pt; margin-top: 3pt; }
.name { display: flex; gap: 14pt; font-size: 12pt; margin: 9pt 0 7pt; align-items: flex-end; }
.name span { flex: 1; border-bottom: 1pt solid #000; height: 15pt; }
.name span.s { flex: 0 0 1.3in; }
.foot { display: flex; justify-content: space-between; font-size: 8.5pt; color: #333; border-top: .8pt solid #000; padding-top: 3pt; }
.wm { position: absolute; left: 50%; top: 50%; transform: translate(-50%, -50%) rotate(-38deg); font-family: 'Oswald'; font-weight: 700;
      font-size: 150pt; color: rgba(0,0,0,.13); letter-spacing: .06em; white-space: nowrap; pointer-events: none; z-index: 9; }
.fill { flex: 1; }
.how { font-size: 11.5pt; margin: 2pt 0 6pt; line-height: 1.3; text-wrap: pretty; }
/* weekly log */
table.log { border-collapse: collapse; width: 100%; table-layout: fixed; margin-top: 2pt; }
table.log th { font-family: 'Oswald'; font-weight: 500; text-transform: uppercase; font-size: 9.5pt; background: #000; color: #fff;
               border: 1pt solid #000; padding: 4pt 4pt; line-height: 1.15; }
table.log td { border: 1pt solid #000; height: 47pt; padding: 3pt 6pt; vertical-align: middle; }
table.log td.day { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 11pt; letter-spacing: .02em; }
table.log td.rate { text-align: center; padding: 0 2pt; }
.dots { display: flex; justify-content: center; gap: 3pt; }
.dots i { font-style: normal; width: 17pt; height: 17pt; border: 1pt solid #000; border-radius: 50%; font-family: 'Oswald'; font-weight: 500;
          font-size: 9.5pt; line-height: 15pt; text-align: center; }
.key { font-size: 9.5pt; margin: 4pt 0 2pt; color: #222; line-height: 1.25; }
.row2 { display: flex; gap: 12pt; margin-top: 8pt; }
.box { border: 1.3pt solid #000; border-radius: 7pt; padding: 6pt 10pt 8pt; flex: 1; }
.box .bt { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 11.5pt; letter-spacing: .02em; margin-bottom: 2pt; }
.rl { border-bottom: 1pt solid #000; height: 19pt; }
.big { font-family: 'Oswald'; font-weight: 500; font-size: 12pt; display: flex; align-items: flex-end; gap: 6pt; text-transform: uppercase; letter-spacing: .02em; }
.big span.u { flex: 1; border-bottom: 1pt solid #000; height: 17pt; }
/* tracker */
table.trk { border-collapse: collapse; width: 100%; table-layout: fixed; margin-top: 2pt; }
table.trk th { font-family: 'Oswald'; font-weight: 500; text-transform: uppercase; font-size: 8.5pt; background: #000; color: #fff; border: 1pt solid #000; padding: 3pt 2pt; height: 24pt; }
table.trk th.wd { background: #fff; color: #555; font-weight: 300; text-transform: none; font-size: 8pt; text-align: left; vertical-align: top; padding: 2pt 4pt; height: 28pt; }
table.trk td { border: 1pt solid #000; height: 71pt; padding: 3pt 5pt; vertical-align: top; position: relative; }
table.trk td.wk { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 11pt; background: #EFEFEF; line-height: 1.15; }
table.trk td.wk small { display: block; font-weight: 300; text-transform: none; font-size: 9pt; margin-top: 2pt; }
table.trk td.dy .n { font-family: 'Oswald'; font-weight: 700; font-size: 13pt; }
table.trk td.dy .m, table.trk td.tot .m { position: absolute; right: 5pt; bottom: 3pt; font-size: 8pt; color: #444; }
table.trk td.off { background: repeating-linear-gradient(135deg, #fff 0 5px, #E6E6E6 5px 6px); }
.sumrow { display: flex; align-items: center; gap: 5pt; margin-top: 9pt; font-family: 'Oswald'; font-weight: 500; text-transform: uppercase; font-size: 9.5pt; line-height: 1.15; }
.sumrow .sb { border: 1.3pt solid #000; border-radius: 6pt; width: 62pt; height: 40pt; padding: 3pt 2pt; text-align: center; flex: 0 0 auto; }
.sumrow .sb.g { width: 104pt; background: TINT; }
.sumrow .op { font-size: 17pt; font-weight: 700; flex: 0 0 auto; }
.two { display: flex; gap: 16pt; margin-top: 10pt; }
.two > div { flex: 1; }
table.gt { border-collapse: collapse; width: 100%; table-layout: fixed; font-size: 10pt; }
table.gt td { border: 1pt solid #000; padding: 3.5pt 6pt; }
.srow { display: flex; align-items: flex-end; gap: 5pt; margin-top: 7pt; font-family: 'Oswald'; font-weight: 500; text-transform: uppercase; font-size: 10.5pt; }
.srow .u { flex: 1; border-bottom: 1pt solid #000; height: 15pt; }
.doc h1 { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 30pt; margin: 0 0 4pt; line-height: 1; }
.doc h2 { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 13.5pt; margin: 11pt 0 4pt; letter-spacing: .02em; }
.doc p, .doc li { font-size: 11pt; line-height: 1.36; margin: 0 0 5pt; text-wrap: pretty; }
.doc ul { margin: 0 0 4pt; padding-left: 16pt; }
.doc .rule { border-bottom: 2.2pt solid #000; margin-bottom: 8pt; padding-bottom: 6pt; }
.doc table.dt { border-collapse: collapse; width: 100%; table-layout: fixed; font-size: 10pt; margin: 2pt 0 4pt; }
.doc table.dt td, .doc table.dt th { border: 1pt solid #000; padding: 3.5pt 6pt; text-align: left; vertical-align: top; }
.doc table.dt th { font-family: 'Oswald'; font-weight: 500; text-transform: uppercase; font-size: 9.5pt; background: #000; color: #fff; }
.parent p, .parent li { font-size: 12.5pt; line-height: 1.5; margin-bottom: 7pt; }
.cols { display: flex; gap: 20pt; }
.cols > div { flex: 1; min-width: 0; }
.small { font-size: 9.5pt !important; color: #333; }
.steps { display: flex; flex-direction: column; gap: 5pt; margin: 4pt 0 2pt; }
.step { display: flex; gap: 8pt; align-items: center; border: 1.3pt solid #000; border-radius: 7pt; padding: 5pt 9pt; }
.step .n { flex: 0 0 20pt; background: ACCENT; color: #fff; font-family: 'Oswald'; font-weight: 700; font-size: 12pt; border-radius: 50%; width: 20pt; height: 20pt; line-height: 20pt; text-align: center; }
.step p { margin: 0 !important; font-size: 10.5pt !important; }
.diags { display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 9pt; margin-top: 4pt; }
.dg { border: 1.3pt solid #000; border-radius: 7pt; padding: 6pt 4pt 6pt; text-align: center; }
.dg svg { display: block; margin: 0 auto; }
.dg b { display: block; font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 11pt; margin-top: 3pt; }
.dg span { display: block; font-size: 9.5pt; line-height: 1.2; margin-top: 1pt; padding: 0 3pt; }
/* caller sheet */
.callgrid { display: grid; grid-template-columns: 1fr 1fr; gap: 0 16pt; margin-top: 3pt; }
.crow { display: flex; align-items: center; gap: 5pt; border-bottom: .8pt solid #888; height: 23.6pt; font-size: 9.6pt; line-height: 1.12; }
.crow .cn { flex: 0 0 18pt; font-family: 'Oswald'; font-weight: 700; font-size: 10.5pt; text-align: right; }
.crow .ct { flex: 1; }
.crow .cb { flex: 0 0 50pt; font-family: 'Oswald'; font-weight: 500; font-size: 8pt; text-transform: uppercase; text-align: right; color: #222; white-space: nowrap; }
.crow.first { border-top: 1pt solid #000; }
/* bingo board */
.bl { display: grid; grid-template-columns: repeat(5, 1fr); gap: 0; margin-top: 4pt; }
.bl div { background: #000; color: #fff; text-align: center; font-family: 'Oswald'; font-weight: 700; font-size: 17pt; letter-spacing: .1em; padding: 2pt 0 3pt; border: 1pt solid #000; }
.bg { display: grid; grid-template-columns: repeat(5, 1fr); grid-auto-rows: 104pt; border-left: 1.4pt solid #000; border-top: 1.4pt solid #000; }
.cell { border-right: 1.4pt solid #000; border-bottom: 1.4pt solid #000; padding: 4pt 6pt 4pt; position: relative; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; }
.cell .num { position: absolute; left: 4pt; top: 3pt; font-family: 'Oswald'; font-weight: 500; font-size: 8pt; color: #333; }
.cell .ct { font-size: 10.6pt; line-height: 1.17; font-weight: 600; text-wrap: balance; padding-top: 7pt; }
.cell.free { background: TINT; }
.cell.free .ct { font-family: 'Oswald'; font-weight: 700; font-size: 16pt; letter-spacing: .08em; padding-top: 2pt; line-height: 1.4; }
.chk { display: flex; gap: 14pt; align-items: center; font-family: 'Oswald'; font-weight: 500; text-transform: uppercase; font-size: 11pt; margin-top: 8pt; letter-spacing: .03em; }
.chk i { display: inline-block; width: 13pt; height: 13pt; border: 1.3pt solid #000; border-radius: 3pt; vertical-align: -2pt; margin-right: 4pt; }
.cover { align-items: center; justify-content: space-between; padding: 0.55in 0.6in 0.5in; }
.store { font-family: 'Oswald'; font-weight: 500; font-size: 13pt; letter-spacing: .32em; text-transform: uppercase; }
.ctitle { text-align: center; }
.ctitle .a { font-family: 'Oswald'; font-weight: 700; font-size: 46pt; line-height: 1; letter-spacing: .02em; }
.ctitle .b { font-family: 'Oswald'; font-weight: 700; white-space: nowrap; font-size: 78pt; line-height: .95; letter-spacing: .01em; }
.ctitle .c { font-family: 'Oswald'; font-weight: 300; font-size: 17pt; margin-top: 8pt; }
.cband { width: 100%; background: #000; color: #fff; text-align: center; font-family: 'Oswald'; font-weight: 500; font-size: 14pt;
         letter-spacing: .08em; text-transform: uppercase; padding: 8pt 0 9pt; border-radius: 4pt; }
.cband em { font-style: normal; color: ACCENT; }
""".replace("ACCENT", ACCENT).replace("TINT", TINT)


def html_doc(pages, title="doc"):
    return (f'<!doctype html><html><head><meta charset="utf-8"><title>{escape(title)}</title>'
            f'<style>{font_css()}{CSS}</style></head><body>{"".join(pages)}</body></html>')


COPY = f"© {YEAR} {STORE} · {BRAND} · For single-classroom use"


def foot(right):
    return f'<div class="foot"><span>{COPY}</span><span>{right}</span></div>'


def page(n, kind, inner, wm=False, cls=""):
    w = '<div class="wm">PREVIEW</div>' if wm else ""
    return f'<section class="page {cls}" data-page="{n}" data-kind="{kind}">{w}{inner}{foot(f"Page {n}")}</section>'


def top(title, sub, tag, tagline):
    return (f'<div class="top"><div class="h t">{title}<small>{sub}</small></div>'
            f'<div class="tag"><div class="lv">{tag}</div><div class="ln">{tagline}</div></div></div>')


def mul(a, b):
    """A printed product; --check recomputes a*b from the attributes."""
    return f'<span data-mul="{a},{b},{a * b}">{a * b}</span>'


def star_pts(ro, ri):
    pts = []
    for i in range(10):
        r = ro if i % 2 == 0 else ri
        a = -math.pi / 2 + i * math.pi / 5
        pts.append(f"{r * math.cos(a):.2f},{r * math.sin(a):.2f}")
    return " ".join(pts)


def star(size=15, fill=ACCENT):
    return (f'<svg width="{size}pt" height="{size}pt" viewBox="-10 -10 20 20" style="flex:0 0 auto"><polygon fill="{fill}" stroke="#000" stroke-width="1.2" '
            f'points="{star_pts(9, 3.9)}"/></svg>')


# ------------------------------------------------------------------ weekly logs
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def log_page(w, wm=False):
    rows = "".join(
        f'<tr data-logrow="{w}-{i}"><td class="day">{d}</td><td></td><td></td><td></td>'
        f'<td class="rate"><div class="dots">{"".join(f"<i>{k}</i>" for k in range(1, 6))}</div></td><td></td></tr>'
        for i, d in enumerate(DAYS, 1))
    cols = [("Day", 12.5), ("Date", 9), ("Minutes", 10.5), ("What I practiced", 31), ("Rating (circle one)", 21), ("Parent or guardian initials", 16)]
    cg = "".join(f'<col style="width:{p}%">' for _, p in cols)
    th = "".join(f"<th>{c}</th>" for c, _ in cols)
    inner = (top("Practice Log", f"Week {w} · minutes, music and rating", f"WEEK {w}", f"of {NLOGS}") +
             '<div class="name">Name<span></span>Instrument or voice<span class="s"></span>Week of<span class="s"></span></div>'
             f'<table class="log blk"><colgroup>{cg}</colgroup><tr>{th}</tr>{rows}</table>'
             '<div class="key blk">Rating: 1 = I need more practice, 2 = a little better, 3 = okay, 4 = good, 5 = great today. '
             'Write your minutes after each practice. A parent or guardian initials each row.</div>'
             '<div class="row2">'
             '<div class="box blk"><div class="bt">My goal this week</div><div class="rl"></div><div class="rl"></div></div>'
             '<div class="box blk" style="flex:0 0 2.55in"><div class="big">Total minutes<span class="u"></span></div>'
             '<div class="big" style="margin-top:9pt">My goal<span class="u"></span>min</div></div></div>'
             '<div class="row2">'
             '<div class="box blk"><div class="bt">One thing I did well</div><div class="rl"></div><div class="rl"></div></div>'
             '<div class="box blk"><div class="bt">One thing to fix next week</div><div class="rl"></div><div class="rl"></div></div></div>'
             '<div class="row2"><div class="box blk"><div class="big">Bingo squares I finished this week<span class="u"></span></div></div></div>'
             '<div class="fill"></div>')
    return page(P_LOG0 + w - 1, "log", inner, wm)


# ------------------------------------------------------------------ 30-day tracker
def week_range(r):
    return r * TRACK_COLS + 1, min((r + 1) * TRACK_COLS, TRACK_DAYS)


def tracker_page(wm=False):
    rows = []
    for r in range(TRACK_WEEKS):
        a, b = week_range(r)
        cells = []
        for c in range(TRACK_COLS):
            d = r * TRACK_COLS + c + 1
            if d <= TRACK_DAYS:
                cells.append(f'<td class="dy" data-day="{d}"><span class="n">{d}</span><span class="m">min</span></td>')
            else:
                cells.append('<td class="off"></td>')
        lab = f'Week {r + 1}<small>days {a}–{b}</small>'
        rows.append(f'<tr data-weekrow="{r + 1}"><td class="wk" data-weeklabel="{r + 1}">{lab}</td>{"".join(cells)}'
                    f'<td class="tot" data-weektot="{r + 1}"><span class="m">min</span></td></tr>')
    head = '<tr><th>Week</th>' + "".join('<th class="wd">weekday</th>' for _ in range(TRACK_COLS)) + '<th>Week total</th></tr>'
    cg = '<col style="width:11%">' + '<col style="width:11.2%">' * 7 + '<col style="width:10.6%">'
    sums = []
    for r in range(TRACK_WEEKS):
        a, b = week_range(r)
        sums.append(f'<div class="sb" data-sumbox="{r + 1}">Week {r + 1}<br>{"" if b - a + 1 == TRACK_COLS else f"({b - a + 1} days)"}</div>')
    sumrow = '<div class="op">+</div>'.join(sums) + '<div class="op">=</div><div class="sb g" data-grand="1">30-day total minutes</div>'
    goals = "".join(f'<tr data-goal="{g}"><td>{g} minutes a day</td><td>{g} × {TRACK_DAYS} days = {mul(g, TRACK_DAYS)} minutes</td></tr>' for g in GOALS)
    streak = "".join(f'<div class="srow" data-streak="{s}">{star()}<span style="white-space:nowrap">{s} days in a row</span><span class="u"></span></div>' for s in STREAKS)
    inner = (top("30-Day Tracker", f"{TRACK_DAYS} days in {TRACK_WEEKS} week rows (4 full weeks and 2 more days)", f"{TRACK_DAYS} DAYS", "minutes, totals and streaks") +
             '<div class="name">Name<span></span>Instrument or voice<span class="s"></span>Start date<span class="s"></span></div>'
             f'<table class="trk blk"><colgroup>{cg}</colgroup>{head}{"".join(rows)}</table>'
             f'<div class="sumrow blk">{sumrow}</div>'
             '<div class="two">'
             f'<div class="blk"><div class="h" style="font-size:12pt;margin-bottom:5pt">Pick a daily goal</div>'
             f'<table class="gt"><colgroup><col style="width:38%"><col style="width:62%"></colgroup>{goals}</table>'
             f'<div class="big" style="margin-top:9pt;font-size:10.5pt">Days I practiced<span class="u"></span>of {TRACK_DAYS}</div></div>'
             f'<div class="blk"><div class="h" style="font-size:12pt">Streak rewards</div>'
             f'<div style="font-size:9.5pt;margin-top:3pt;line-height:1.25">A streak is days in a row with practice. Write the reward you earn.</div>{streak}</div>'
             '</div><div class="fill"></div>')
    return page(P_TRACK, "tracker", inner, wm)


# ------------------------------------------------------------------ bingo boards, caller sheet, how to win
def board_page(b, wm=False):
    cells = []
    for idx, n in enumerate(BOARDS[b]):
        r, c = divmod(idx, 5)
        if n == 0:
            cells.append(f'<div class="cell free" data-board="{b + 1}" data-r="{r}" data-c="{c}" data-num="0">{star(20)}<span class="ct">FREE</span></div>')
        else:
            cells.append(f'<div class="cell" data-board="{b + 1}" data-r="{r}" data-c="{c}" data-num="{n}"><span class="num">{n}</span><span class="ct">{escape(CHALLENGES[n - 1])}</span></div>')
    letters = "".join(f"<div>{x}</div>" for x in "BINGO")
    inner = (top("Practice Bingo", f"Board {b + 1} of {NBOARDS} · finish a challenge, then mark its square", f"BOARD {b + 1}", f"{PER_BOARD} challenges + FREE") +
             '<div class="name">Name<span></span>Instrument or voice<span class="s"></span>Week of<span class="s"></span></div>'
             f'<div class="blk"><div class="bl">{letters}</div><div class="bg">{"".join(cells)}</div></div>'
             '<div class="chk blk">My bingos: <span><i></i>Row</span><span><i></i>Column</span><span><i></i>Diagonal</span><span><i></i>Blackout</span></div>'
             '<div class="fill"></div>')
    return page(P_BOARD0 + b, "board", inner, wm)


def boards_of(n):
    return [b + 1 for b in range(NBOARDS) if n in BOARDS[b]]


def caller_page(wm=False):
    half = NCH // 2
    cols = []
    for part in (range(1, half + 1), range(half + 1, NCH + 1)):
        rows = []
        for n in part:
            bs = ", ".join(str(x) for x in boards_of(n))
            rows.append(f'<div class="crow{" first" if n in (1, half + 1) else ""}" data-call="{n}"><span class="cn">{n}</span>'
                        f'<span class="ct">{escape(CHALLENGES[n - 1])}</span><span class="cb">Boards {bs}</span></div>')
        cols.append(f'<div class="blk">{"".join(rows)}</div>')
    inner = (top("Challenge List", f"Caller sheet · all {NCH} challenges, numbered", "CALLER", "for the teacher") +
             f'<div class="how">Each board uses {PER_BOARD} of these {NCH} challenges. Every challenge is on exactly {APPEARS} of the {NBOARDS} boards, and any two boards share {SHARED} challenges. '
             f'The small number in a bingo square matches the number here. Call a number for a class game, or pick a Challenge of the Day.</div>'
             f'<div class="callgrid">{"".join(cols)}</div><div class="fill"></div>')
    return page(P_CALL, "caller", inner, wm)


def mini_grid(lit, size=92):
    s = size / 5
    cells = []
    for r in range(5):
        for c in range(5):
            on = (r, c) in lit
            cells.append(f'<rect x="{c * s + 1:.1f}" y="{r * s + 1:.1f}" width="{s:.1f}" height="{s:.1f}" fill="{ACCENT if on else "#fff"}" stroke="#000" stroke-width="1.3"/>')
    free = f'<g transform="translate({2.5 * s + 1:.1f},{2.5 * s + 1:.1f})"><polygon fill="#fff" stroke="#000" stroke-width="1" points="{star_pts(5.6, 2.4)}"/></g>'
    cl = ";".join(f"{r},{c}" for r, c in sorted(lit))
    return f'<svg width="{size + 3}pt" height="{size + 3}pt" viewBox="0 0 {size + 2} {size + 2}" data-cells="{cl}">{"".join(cells)}{free}</svg>'


DIAGS = [("row", "Row", "5 squares in a line across.", {(2, c) for c in range(5)}),
         ("col", "Column", "5 squares in a line down.", {(r, 0) for r in range(5)}),
         ("diag", "Diagonal", "5 squares corner to corner.", {(i, i) for i in range(5)}),
         ("black", "Blackout", "All 25 squares marked.", {(r, c) for r in range(5) for c in range(5)})]


def win_page(wm=False):
    steps = [f"Pick a bingo board from pages {P_BOARD0}–{P_BOARD0 + NBOARDS - 1}. Write your name on it.",
             f"Do a challenge during your practice. Write your minutes and what you practiced on your weekly log (pages {P_LOG0}–{P_LOG0 + NLOGS - 1}).",
             "Mark the square with a check, a date or a color. Each square counts once.",
             "Ask a parent, guardian or teacher to initial the squares you finished.",
             "Make a line, then try for a blackout. The FREE square is already marked."]
    sh = "".join(f'<div class="step"><div class="n">{i}</div><p>{escape(s)}</p></div>' for i, s in enumerate(steps, 1))
    dg = "".join(f'<div class="dg" data-diag="{k}">{mini_grid(lit)}<b>{t}</b><span>{d}</span></div>' for k, t, d, lit in DIAGS)
    inner = (top("How to Win", "Practice Bingo rules for students", "RULES", "4 ways to win") +
             '<div class="how" style="margin-top:8pt">Practice Bingo turns practice into a game. Your goal is to mark squares in a line, and every square is a real practice challenge.</div>'
             f'<div class="doc"><h2>How to play in {len(steps)} steps</h2></div><div class="steps blk">{sh}</div>'
             f'<div class="doc"><h2>Four ways to win</h2></div><div class="diags blk">{dg}</div>'
             f'<div class="doc"><p style="margin-top:9pt" data-lines="1">A board has 5 rows + 5 columns + 2 diagonals = 12 possible lines. The FREE square in the center counts for the row, the column and the diagonals that cross it. '
             f'A blackout needs all 25 squares: 24 challenges and the FREE square.</p>'
             f'<h2>Keep going</h2><p>Finish a line, then finish another one. Then try the next board. A square earned with care is worth more than a quick check mark, '
             f'because every challenge is a way to practice smarter.</p></div><div class="fill"></div>')
    return page(P_WIN, "win", inner, wm, "doc")


# ------------------------------------------------------------------ teacher notes, parent note, terms, cover
def teacher_page(wm=False):
    plan = [("Week 1", "Launch", f"Send home the parent note (page {P_PARENT}). Hand out log 1 (page {P_LOG0}) and Board 1 (page {P_BOARD0}). Students start the 30-day tracker on day 1."),
            ("Week 2", "Build the habit", "Log 2 and Board 2. Check the logs and ask who has a line."),
            ("Week 3", "Stretch", "Log 3 and Board 3. Raise the daily goal by 5 minutes if students are ready."),
            ("Week 4", "Finish strong", "Log 4 and Board 4. Days 29 and 30 on the tracker are bonus days. Share totals and celebrate streaks.")]
    prow = "".join(f"<tr><td><b>{a}</b></td><td>{b}</td><td>{c}</td></tr>" for a, b, c in plan)
    rub = "".join(f'<tr><td>{a}</td><td data-pts="{p}">{p}</td><td>{c}</td></tr>' for a, p, c in RUBRIC)
    gl = "".join(f'<tr><td>{g} minutes</td><td>{g} × 7 = {mul(g, 7)}</td><td>{mul(g * 7, 4)} ({mul(g, 7)} × 4)</td></tr>' for g in GOALS)
    total_pts = sum(p for _, p, _ in RUBRIC)
    inner = (f'<div class="rule"><h1>Teacher Notes</h1><div class="l" style="font-size:13pt">{TITLE} · weekly logs, a 30-day tracker and {NBOARDS} bingo boards · grades 4–8</div></div>'
             f'<div class="cols"><div>'
             f'<h2>What is inside ({TOTAL_PAGES} pages)</h2><ul>'
             f'<li>Page {P_PARENT}: parent note with blanks</li>'
             f'<li>Page {P_WIN}: how to win (rows, columns, diagonals, blackout)</li>'
             f'<li>Pages {P_LOG0}–{P_LOG0 + NLOGS - 1}: {NLOGS} weekly practice logs</li>'
             f'<li>Page {P_TRACK}: 30-day tracker</li>'
             f'<li>Page {P_CALL}: challenge list and caller sheet</li>'
             f'<li>Pages {P_BOARD0}–{P_BOARD0 + NBOARDS - 1}: {NBOARDS} bingo boards</li>'
             f'<li>Page {P_TERMS}: terms of use</li></ul>'
             f'<p class="small">Every square is something students can do on any instrument or with their voice. "Play" means play or sing. Each board has {PER_BOARD} different challenges and a FREE center. '
             f'Each of the {NCH} challenges is on {APPEARS} boards.</p>'
             f'<h2>Differentiation</h2>'
             f'<p><b>Grades 4–5:</b> aim for 10 to 15 minutes a day. Start with Boards 1 and 2. Read the challenges aloud, let students use the log as a checklist, and count a single line as a win.</p>'
             f'<p><b>Grades 6–8:</b> aim for 20 to 30 minutes a day. Use all {NBOARDS} boards, ask for the goal and reflection lines every week, let a student run the caller sheet, and set a blackout as the stretch goal.</p>'
             f'<h2>Minutes at a glance</h2><table class="dt"><colgroup><col style="width:30%"><col style="width:30%"><col style="width:40%"></colgroup>'
             f'<tr><th>Daily goal</th><th>Per week</th><th>4 weeks</th></tr>{gl}</table>'
             f'</div><div>'
             f'<h2>Four-week plan</h2><table class="dt"><colgroup><col style="width:17%"><col style="width:24%"><col style="width:59%"></colgroup>'
             f'<tr><th>Week</th><th>Focus</th><th>What to do</th></tr>{prow}</table>'
             f'<h2>Grading ideas ({total_pts} points)</h2><table class="dt"><colgroup><col style="width:44%"><col style="width:14%"><col style="width:42%"></colgroup>'
             f'<tr><th>Part</th><th>Points</th><th>Notes</th></tr>{rub}'
             f'<tr><td><b>Total</b></td><td data-ptstotal="{total_pts}"><b>{total_pts}</b></td><td></td></tr></table>'
             f'<p class="small">Or skip points: mark each log Complete, Almost there or Not yet.</p>'
             f'</div></div><div class="fill"></div>')
    return page(P_TEACH, "teacher", inner, wm, "doc")


def parent_page(wm=False):
    def bl(w):
        return f'<span style="display:inline-block;border-bottom:1pt solid #000;width:{w}pt;height:11pt"></span>'
    inner = (f'<div class="rule"><h1>Parent Note</h1><div class="l" style="font-size:13pt">A letter template: fill in the blanks, then copy it to send home.</div></div>'
             f'<div class="doc parent" style="margin-top:6pt">'
             f'<p style="text-align:right">Date: {bl(120)}</p>'
             f'<p>Dear parent or guardian of {bl(150)},</p>'
             f'<p>Our class is starting a four-week practice challenge. Your child will bring home a weekly practice log, a 30-day tracker and a Practice Bingo board. '
             f'The bingo squares are small, fun challenges, such as playing a slow section three times, teaching someone a rhythm or practicing with a metronome.</p>'
             f'<p>Our goal is about {bl(36)} minutes a day, on {bl(30)} days each week, starting on {bl(90)}. '
             f'Short, regular practice helps more than one long session, and a few minutes of focus can make a big difference.</p>'
             f'<p><b>How you can help</b></p>'
             f'<ul><li>Help your child find a quiet place to practice.</li>'
             f'<li>Ask to hear one thing from this week, or ask your child to teach you a rhythm.</li>'
             f'<li>Initial the practice log after each practice.</li>'
             f'<li>Cheer for effort and progress. Mistakes are a normal part of learning.</li></ul>'
             f'<p>Please send the log back to school each {bl(90)}. If you have questions, you can reach me at:</p><p>{bl(250)}</p>'
             f'<p>Thank you for helping your child grow as a musician!</p>'
             f'<p style="margin-top:12pt">Sincerely,<br><br>{bl(200)}<br><span class="small">Teacher name and class or ensemble</span></p>'
             f'<div style="border-top:1.3pt dashed #000;margin-top:14pt;padding-top:7pt" class="blk">'
             f'<div class="h" style="font-size:12pt;margin-bottom:5pt">Reply slip (cut here and return)</div>'
             f'<p>I have seen my child\'s practice log and bingo board.</p>'
             f'<p style="margin:12pt 0 0">Child: {bl(130)} &nbsp; Parent or guardian: {bl(130)} &nbsp; Date: {bl(60)}</p></div>'
             f'</div><div class="fill"></div>')
    return page(P_PARENT, "parent", inner, wm, "doc")


def terms_page(wm=False):
    inner = (f'<div class="rule"><h1>Terms of Use</h1><div class="l" style="font-size:13pt">Thank you for your purchase!</div></div>'
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
             f'<li>Logs, tracker, bingo boards and art: original work, {BRAND} by {STORE}.</li>'
             f'<li>Text fonts: Oswald (The Oswald Project Authors) and Source Sans 3 (Adobe), SIL Open Font License 1.1.</li></ul>'
             f'<h2>What is in this file</h2><p>Page {P_COVER} cover, page {P_TEACH} teacher notes, page {P_PARENT} parent note, page {P_WIN} how to win, '
             f'pages {P_LOG0}–{P_LOG0 + NLOGS - 1} weekly logs, page {P_TRACK} 30-day tracker, page {P_CALL} challenge list, '
             f'pages {P_BOARD0}–{P_BOARD0 + NBOARDS - 1} bingo boards and page {P_TERMS} these terms: {TOTAL_PAGES} pages in all.</p>'
             f'<p class="small">{DISCLOSURE}</p><div class="fill"></div>')
    return page(P_TERMS, "terms", inner, wm, "doc")


def cover_art(width=900, height=470):
    s = 52
    gx, gy = 70, 100
    lit = {(0, 0), (1, 1), (3, 3), (4, 4), (0, 3), (2, 0), (4, 1)}
    cells, checks = [], []
    for r in range(5):
        for c in range(5):
            on = (r, c) in lit
            x, y = gx + c * s, gy + r * s
            cells.append(f'<rect x="{x}" y="{y}" width="{s}" height="{s}" fill="{TINT if on else "#fff"}" stroke="#000" stroke-width="3"/>')
            if on:
                checks.append(f'<polyline points="{x + 13},{y + 28} {x + 23},{y + 39} {x + 40},{y + 14}" fill="none" stroke="{ACCENT}" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>')
    letters = "".join(f'<rect x="{gx + i * s}" y="{gy - 40}" width="{s}" height="40" fill="#000"/>'
                      f'<text x="{gx + i * s + s / 2}" y="{gy - 10}" fill="#fff" font-family="Oswald" font-weight="700" font-size="28" text-anchor="middle">{ch}</text>'
                      for i, ch in enumerate("BINGO"))
    cx, cy = gx + 2 * s + s / 2, gy + 2 * s + s / 2
    free = (f'<rect x="{gx + 2 * s}" y="{gy + 2 * s}" width="{s}" height="{s}" fill="{ACCENT}" stroke="#000" stroke-width="3"/>'
            f'<polygon transform="translate({cx},{cy - 5})" fill="#fff" stroke="#000" stroke-width="2" points="{star_pts(16, 6.8)}"/>'
            f'<text x="{cx}" y="{cy + 20}" fill="#fff" font-family="Oswald" font-weight="700" font-size="12" text-anchor="middle">FREE</text>')
    lx, ly, lw, lh = 500, 62, 290, 364
    rows = []
    for i in range(7):
        y = ly + 122 + i * 34
        rows.append(f'<line x1="{lx + 16}" y1="{y}" x2="{lx + lw - 16}" y2="{y}" stroke="#000" stroke-width="2.4"/>')
        rows.append(f'<circle cx="{lx + 30}" cy="{y - 14}" r="9" fill="{ACCENT if i < 5 else "#fff"}" stroke="#000" stroke-width="2.4"/>')
        rows.append(f'<line x1="{lx + 52}" y1="{y - 14}" x2="{lx + 52 + 70 + (i * 23) % 40}" y2="{y - 14}" stroke="#000" stroke-width="3" stroke-linecap="round"/>')
        for k in range(5):
            rows.append(f'<circle cx="{lx + 190 + k * 18}" cy="{y - 14}" r="6" fill="{"#000" if k < (i % 4) + 2 else "#fff"}" stroke="#000" stroke-width="1.8"/>')
    sheet = (f'<g transform="rotate(3 {lx + lw / 2} {ly + lh / 2})"><rect x="{lx}" y="{ly}" width="{lw}" height="{lh}" rx="10" fill="#fff" stroke="#000" stroke-width="4"/>'
             f'<path d="M{lx},{ly + 52} V{ly + 10} Q{lx},{ly} {lx + 10},{ly} H{lx + lw - 10} Q{lx + lw},{ly} {lx + lw},{ly + 10} V{ly + 52} Z" fill="#000"/>'
             f'<text x="{lx + 18}" y="{ly + 36}" fill="#fff" font-family="Oswald" font-weight="700" font-size="24" letter-spacing="1.5">PRACTICE LOG</text>'
             f'<text x="{lx + 18}" y="{ly + 78}" font-family="Oswald" font-weight="500" font-size="14" letter-spacing="1">DAY · MINUTES · RATING</text>'
             f'{"".join(rows)}</g>')
    stars = "".join(f'<g transform="translate({x},{y}) scale({k})"><polygon fill="{ACCENT}" stroke="#000" stroke-width="1.5" points="{star_pts(9, 3.9)}"/></g>'
                    for x, y, k in ((440, 80, 2.0), (452, 412, 1.5), (36, 58, 1.6)))
    return (f'<svg viewBox="10 30 {width - 70} {height - 60}" width="100%" xmlns="http://www.w3.org/2000/svg">{letters}{"".join(cells)}{free}{"".join(checks)}{sheet}{stars}</svg>')


def cover_page():
    return (f'<section class="page cover" data-page="1" data-kind="cover"><div class="store">{BRAND}</div>'
            f'<div style="width:6.9in">{cover_art()}</div>'
            f'<div class="ctitle"><div class="a">PRACTICE LOG</div><div class="b">&amp; BINGO</div>'
            f'<div class="c">Weekly logs, a 30-day tracker and {NBOARDS} bingo boards for any instrument or voice</div></div>'
            f'<div class="cband">Grades 4–8 <em>·</em> {NBOARDS} bingo boards <em>·</em> {TOTAL_PAGES} pages</div></section>')


def all_pages(wm=False):
    """Every page in order, optionally watermarked (preview use)."""
    p = [cover_page(), teacher_page(wm), parent_page(wm), win_page(wm)]
    p += [log_page(w, wm) for w in range(1, NLOGS + 1)]
    p += [tracker_page(wm), caller_page(wm)]
    p += [board_page(b, wm) for b in range(NBOARDS)]
    p.append(terms_page(wm))
    return p


SHOT_PAGES = {"log1": P_LOG0, "tracker": P_TRACK, "board1": P_BOARD0, "board3": P_BOARD0 + 2, "caller": P_CALL,
              "parent": P_PARENT, "win": P_WIN, "teacher": P_TEACH}
PREVIEW_ORDER = ["log1", "tracker", "board1", "caller"]

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
.lbl { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 24px; text-align: center; margin-top: 18px; }
.lbl span { font-weight: 300; text-transform: none; display: block; font-size: 20px; margin-top: 2px; }
""".replace("ACCENT", ACCENT)


def sq_doc(body):
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{font_css()}'
            f'html,body{{margin:0;background:#fff}}{SQ_CSS}</style></head><body>{body}</body></html>')


def cover_square():
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div>'
        f'<div style="flex:1;display:flex;flex-direction:column;justify-content:space-evenly;align-items:center;width:100%;padding:0 0 76px">'
        f'<div style="width:880px">{cover_art()}</div>'
        f'<div><div class="hd" style="font-size:78px">Practice Log</div>'
        f'<div class="hd" style="font-size:132px">&amp; Bingo</div>'
        f'<div class="sub" style="font-size:28px;margin-top:12px">Weekly logs, a 30-day tracker and {NBOARDS} bingo boards for any instrument or voice</div></div>'
        f'</div><div class="band">Grades 4–8 <em>·</em> {NBOARDS} bingo boards <em>·</em> {TOTAL_PAGES} pages</div></div>')


def pair_shots(headline, sub, items, band, w):
    shots = "".join(f'<div style="width:{w}px"><div class="shot"><img src="{src}"></div><div class="lbl">{lab}</div></div>' for src, lab in items)
    gap = 40 if len(items) < 3 else 26
    return sq_doc(f'<div class="sq"><div class="store">{BRAND}</div>'
                  f'<div class="hd" style="font-size:66px;margin-top:24px">{headline}</div>'
                  f'<div class="sub" style="font-size:27px;margin-top:8px">{sub}</div>'
                  f'<div style="flex:1;display:flex;align-items:center;padding-bottom:74px"><div style="display:flex;gap:{gap}px;align-items:flex-start">{shots}</div></div>'
                  f'<div class="band">{band}</div></div>')


def square_pages():
    return [
        pair_shots("Logs and a 30-day tracker", "Minutes, ratings, parent initials and streaks",
                   [("shot-log1.png", "Weekly practice log<span>4 weeks, 7 days each</span>"),
                    ("shot-tracker.png", "30-day tracker<span>totals and streak rewards</span>")],
                   f"{NLOGS} weekly logs <em>·</em> 30-day tracker <em>·</em> streak rewards", 420),
        pair_shots(f"{NBOARDS} different bingo boards", f"{PER_BOARD} challenges and a FREE center on each board",
                   [("shot-board1.png", "Board 1<span>5 × 5, FREE center</span>"),
                    ("shot-board3.png", "Board 3<span>a different mix of challenges</span>")],
                   "Band <em>·</em> orchestra <em>·</em> voice <em>·</em> piano <em>·</em> guitar", 420),
        pair_shots("Everything to run it", "A numbered caller sheet and the rules",
                   [("shot-caller.png", f"Challenge list<span>all {NCH} numbered</span>"),
                    ("shot-win.png", "How to win<span>rows, columns, diagonals</span>")],
                   f"Parent note <em>·</em> teacher notes <em>·</em> {TOTAL_PAGES} pages", 430),
    ]


# ------------------------------------------------------------------ render / build
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


def upload_md():
    return f"""# UPLOAD: {LISTING_TITLE} (TpT 049)

These fields follow the order of TpT's "Add a resource" form. Evergreen: no season, sell all year (strongest in August to October and January).

**Files to attach**
- Resource (digital download): `{SLUG}.pdf`, {TOTAL_PAGES} pages, US Letter.
- Thumbnails, in this order: `cover.png`, `preview-1.png`, `preview-2.png`, `preview-3.png` (all 2000 × 2000).
- Preview file: `{SLUG}-PREVIEW.pdf`, 4 watermarked pages.

## 1. Title

```
{LISTING_TITLE}
```
({len(LISTING_TITLE)} characters; the limit is 80.) Plain search words first, no seasonal words.

## 2. Description

```
Get students practicing at home with a music practice log and a Practice Bingo game. This printable pack has {NLOGS} weekly practice logs, a 30-day practice tracker, {NBOARDS} different bingo boards, a challenge list, a parent note and teacher notes. It works for band, orchestra, choir, piano and guitar students in grades 4 to 8, and the wording is the same for every instrument and for voice.

WHAT'S INCLUDED ({TOTAL_PAGES} pages, PDF, US Letter)
• Cover (1 page)
• Teacher notes: a four-week plan, grading ideas and differentiation for grades 4-5 and grades 6-8 (1 page)
• Parent note: a friendly letter template with blanks and a reply slip (1 page)
• How to win: rows, columns, diagonals and blackout, with pictures (1 page)
• Weekly practice logs: minutes for each day, what I practiced, a 1 to 5 self-rating, a parent or guardian initials column, a goals line and a reflection ({NLOGS} pages, one for each of 4 weeks)
• 30-day practice tracker: a calendar-style grid with weekly totals, a 30-day total and streak rewards (1 page)
• Challenge list and caller sheet: all {NCH} challenges, numbered (1 page)
• Practice Bingo boards: {NBOARDS} different 5 x 5 boards, each with {PER_BOARD} challenges and a FREE center ({NBOARDS} pages)
• Terms of use and credits (1 page)
Total: {TOTAL_PAGES} pages.

HOW TO USE
Hand out one log and one bingo board each week for four weeks, and start the 30-day tracker on day 1. Students write down their minutes, mark the bingo squares they finish and ask a parent or guardian to initial the log. Challenges include "play your slowest section 3 times", "practice with a metronome" and "teach someone a rhythm". Each of the {NCH} challenges appears on {APPEARS} of the {NBOARDS} boards. Good for homework, practice charts, a class bingo game and parent communication.

• Grades 4–8 (suggested goals for each grade band in the teacher notes)
• Prints well in black and white; one accent color
• No songs, lyrics or copyrighted characters

{DISCLOSURE}
```

## 3. Grades

4, 5, 6, 7 (TpT allows four; the product is written for grades 4 to 8).

## 4. Subjects and tags

- Subjects: {", ".join(SUBJECTS)}
- Tags: {", ".join(TAGS)}

## 5. Page count by section (totals {TOTAL_PAGES})

- Cover: 1
- Teacher notes: 1
- Parent note: 1
- How to win: 1
- Weekly practice logs: {NLOGS}
- 30-day tracker: 1
- Challenge list and caller sheet: 1
- Bingo boards: {NBOARDS}
- Terms of use and credits: 1
- Total: {TOTAL_PAGES}

## 6. Standards

None cited. The teacher notes ask teachers to match the activities to their own curriculum.

## 7. Price

**${PRICE}** (paid; owner range $3–5).

## 8. Preview

Paid. Preview PDF: weekly log 1, the 30-day tracker, bingo board 1 and the challenge list, all watermarked.

## 9. Before you click publish

- [ ] Evergreen: no season, no holiday words.
- Open owner question: logo beside HUDSON BEAT (see tpt/STYLE.md).
"""


def tpt_json():
    return {
        "price": PRICE, "license_price": PRICE, "tax_code": "Other Digital Goods - No Physical Media",
        "grades": GRADES, "subjects": SUBJECTS, "tags": TAGS, "formats": ["PDF"], "pages": TOTAL_PAGES,
        "files": {"product": f"{SLUG}.pdf", "preview": f"{SLUG}-PREVIEW.pdf", "thumb1": "cover.png", "thumb2": "preview-1.png",
                  "thumb3": "preview-2.png", "thumb4": "preview-3.png"},
    }


def build():
    os.makedirs(BUILD, exist_ok=True)
    full = write("resource.html", html_doc(all_pages(False), TITLE))
    shots = write("shots.html", html_doc(all_pages(True), "Preview shots"))
    sq = [write("cover.html", cover_square())]
    render([{"html": full, "pdf": PDF}, {"html": shots, "pdf": os.path.join(BUILD, "shots.pdf")}])
    from pypdf import PdfReader, PdfWriter
    rd = PdfReader(os.path.join(BUILD, "shots.pdf"))
    wr = PdfWriter()
    for k in PREVIEW_ORDER:
        wr.add_page(rd.pages[SHOT_PAGES[k] - 1])
    with open(PREVIEW_PDF, "wb") as f:
        wr.write(f)
    for k, n in SHOT_PAGES.items():
        subprocess.run(["pdftoppm", "-png", "-r", "150", "-f", str(n), "-l", str(n), "-singlefile",
                        os.path.join(BUILD, "shots.pdf"), os.path.join(BUILD, f"shot-{k}")], check=True)
    for i, h in enumerate(square_pages(), 1):
        sq.append(write(f"p{i}.html", h))
    render([{"html": h, "png": o, "width": 1000, "height": 1000, "scale": 2} for h, o in zip(sq, [COVER_PNG] + PREVIEW_PNGS)])
    with open(UPLOAD, "w") as f:
        f.write(upload_md())
    with open(TPT_JSON, "w") as f:
        json.dump(tpt_json(), f, indent=2)
        f.write("\n")
    print(f"built {PDF}, {PREVIEW_PDF}, cover + 3 previews, UPLOAD.md, tpt.json")


# ------------------------------------------------------------------ checks
INSPECT_JS = r"""
const { chromium } = require('playwright');
const url = require('url');
(async () => {
  const b = await chromium.launch();
  const out = {};
  for (const f of process.argv.slice(2)) {
    const p = await b.newPage({ viewport: { width: 816, height: 1056 } });
    await p.goto(url.pathToFileURL(f).href, { waitUntil: 'load' });
    await p.evaluate(() => document.fonts.ready);
    out[f.split('/').pop()] = await p.evaluate(() => {
      const T = el => el ? el.innerText.replace(/\s+/g, ' ').trim() : '';
      const A = (sel, fn) => [...document.querySelectorAll(sel)].map(fn);
      const pageNo = el => { const pg = el.closest('.page'); return pg ? +pg.dataset.page : 0; };
      const d = {};
      d.pages = A('.page', pg => ({ n: +pg.dataset.page, kind: pg.dataset.kind }));
      d.cells = A('[data-board]', e => ({ page: pageNo(e), board: +e.dataset.board, r: +e.dataset.r, c: +e.dataset.c, num: +e.dataset.num,
                                          numTxt: T(e.querySelector('.num')), text: T(e.querySelector('.ct')) }));
      d.calls = A('[data-call]', e => ({ page: pageNo(e), num: +e.dataset.call, numTxt: T(e.querySelector('.cn')), text: T(e.querySelector('.ct')), boards: T(e.querySelector('.cb')) }));
      d.days = A('[data-day]', e => ({ day: +e.dataset.day, txt: T(e.querySelector('.n')), row: +e.closest('[data-weekrow]').dataset.weekrow }));
      d.weeks = A('[data-weekrow]', e => ({ week: +e.dataset.weekrow, label: T(e.querySelector('[data-weeklabel]')), ndays: e.querySelectorAll('[data-day]').length,
                                            hasTot: !!e.querySelector('[data-weektot]'), offs: e.querySelectorAll('td.off').length, cols: e.children.length }));
      d.sumboxes = A('[data-sumbox]', e => ({ week: +e.dataset.sumbox, txt: T(e) }));
      d.grand = A('[data-grand]', e => T(e));
      d.muls = A('[data-mul]', e => ({ a: e.dataset.mul, txt: T(e) }));
      d.pts = A('[data-pts]', e => ({ v: +e.dataset.pts, txt: T(e) }));
      d.ptstotal = A('[data-ptstotal]', e => ({ v: +e.dataset.ptstotal, txt: T(e) }));
      d.logrows = A('[data-logrow]', e => ({ id: e.dataset.logrow, page: pageNo(e), nrate: e.querySelectorAll('.dots i').length, day: T(e.querySelector('.day')),
                                              ncells: e.children.length }));
      d.diags = A('[data-diag]', e => ({ k: e.dataset.diag, cells: e.querySelector('svg').dataset.cells, title: T(e.querySelector('b')) }));
      d.lines = A('[data-lines]', e => T(e));
      d.streaks = A('[data-streak]', e => ({ s: +e.dataset.streak, txt: T(e) }));
      d.goals = A('[data-goal]', e => ({ g: +e.dataset.goal, txt: T(e) }));
      d.steps = A('.step', e => ({ page: pageNo(e), n: T(e.querySelector('.n')) }));
      d.pagetext = A('.page', pg => T(pg));
      const res = [];
      d.gaps = [];
      document.querySelectorAll('.page').forEach((pg, i) => {
        const n = i + 1, pr = pg.getBoundingClientRect();
        const ft = pg.querySelector('.foot');
        const ftop = ft ? ft.getBoundingClientRect().top : pr.bottom;
        if (pg.scrollHeight > pg.clientHeight + 1) res.push(`page ${n}: content overflows the page`);
        let low = 0; const boxes = [];
        pg.querySelectorAll('.blk, .rl, .top, .name, .how, .doc p, .doc li, .doc table, .doc h2, .step, .dg, .crow, .cell').forEach(el => {
          if (ft && ft.contains(el)) return;
          const r = el.getBoundingClientRect();
          if (r.height === 0) return;
          low = Math.max(low, r.bottom);
          if (r.bottom > ftop - 9) res.push(`page ${n}: ${el.tagName}.${el.className} bottom ${(r.bottom - ftop).toFixed(1)}px vs footer rule (needs <= -9)`);
          if (r.right > pr.right - 0.35 * 96 + 0.5 || r.left < pr.left + 0.35 * 96 - 0.5) res.push(`page ${n}: ${el.tagName}.${el.className} too close to the page edge`);
          if (el.matches('.blk')) boxes.push([el, r]);
        });
        for (let a = 0; a < boxes.length; a++) for (let c = a + 1; c < boxes.length; c++) {
          const A = boxes[a][1], C = boxes[c][1];
          if (boxes[a][0].contains(boxes[c][0]) || boxes[c][0].contains(boxes[a][0])) continue;
          const gx = Math.max(A.left, C.left) - Math.min(A.right, C.right);
          const gy = Math.max(A.top, C.top) - Math.min(A.bottom, C.bottom);
          if (gx < 3 && gy < 3) res.push(`page ${n}: ${boxes[a][0].className} and ${boxes[c][0].className} touch or overlap`);
        }
        d.gaps.push(Math.round(ftop - low));
        pg.querySelectorAll('.cell, .crow, .ct, .box, .dg span, .step p, td, .sb, .how, .key').forEach(el => {
          if (getComputedStyle(el).display === 'inline') return;
          if (el.scrollHeight > el.clientHeight + 2 || el.scrollWidth > el.clientWidth + 2) res.push(`page ${n}: text clipped in ${el.tagName}.${el.className} (${el.scrollWidth}x${el.scrollHeight} in ${el.clientWidth}x${el.clientHeight}) ${el.innerText.slice(0,30)}`);
        });
        pg.querySelectorAll('p, li, .how, .key, .step p, .dg span').forEach(el => {
          const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
          const lines = {}; let node;
          while ((node = walker.nextNode())) {
            const re = /\S+/g; let m;
            while ((m = re.exec(node.textContent))) {
              const rg = document.createRange(); rg.setStart(node, m.index); rg.setEnd(node, m.index + m[0].length);
              const rc = rg.getClientRects()[0]; if (!rc) continue;
              const k = Math.round(rc.top / 4); (lines[k] = lines[k] || []).push(m[0]);
            }
          }
          const ks = Object.keys(lines).map(Number).sort((a, b) => a - b);
          if (ks.length > 1 && lines[ks[ks.length - 1]].length === 1)
            res.push(`page ${n}: one-word last line "${lines[ks[ks.length - 1]][0]}" in ${el.tagName}.${el.className}`);
        });
      });
      d.layout = res;
      return d;
    });
    await p.close();
  }
  await b.close();
  console.log(JSON.stringify(out));
})().catch(e => { console.error(e); process.exit(1); });
"""


def inspect_html(files):
    js = os.path.join(BUILD, "inspect.js")
    with open(js, "w") as f:
        f.write(INSPECT_JS)
    r = subprocess.run(["node", js, *files], capture_output=True, text=True, env=node_env())
    if r.returncode != 0:
        sys.exit(f"inspect failed: {r.stderr[-500:]}")
    return json.loads(r.stdout.strip().splitlines()[-1])


BANNED = ["yamaha", "apple", "youtube", "spotify", "amazon", "google", "tiktok", "disney", "nintendo", "fortnite", "minecraft",
          "trumpet", "flute", "violin", "clarinet", "saxophone", "trombone", "drumstick", "drum", "mallet", "reed", "bow", "fingering",
          "embouchure", "bridge", "rosin", "valve"]
UK_SPELLINGS = ["practise", "colour", "favourite", "centre", "metre", "recognise", "organise", "behaviour", "neighbour"]


def verify_content(d):
    errs = []
    cells = d["cells"]
    by_board = {}
    for c in cells:
        by_board.setdefault(c["board"], []).append(c)
    if sorted(by_board) != list(range(1, NBOARDS + 1)):
        errs.append(f"boards found {sorted(by_board)}, expected 1..{NBOARDS}")
    sets, layouts, master = {}, {}, {}
    for cl in d["calls"]:
        if cl["num"] in master:
            errs.append(f"caller sheet: challenge {cl['num']} listed twice")
        if str(cl["num"]) != cl["numTxt"]:
            errs.append(f"caller sheet: row number {cl['numTxt']} vs {cl['num']}")
        master[cl["num"]] = cl["text"]
    if sorted(master) != list(range(1, NCH + 1)):
        errs.append(f"caller sheet lists {len(master)} challenges, expected numbers 1..{NCH}")
    if len(set(master.values())) != len(master):
        errs.append("caller sheet has two identical challenge texts")
    for bnum, cs in sorted(by_board.items()):
        if len(cs) != 25:
            errs.append(f"board {bnum}: {len(cs)} squares, expected 25")
            continue
        pos = {(c["r"], c["c"]): c for c in cs}
        if sorted(pos) != [(r, c) for r in range(5) for c in range(5)]:
            errs.append(f"board {bnum}: squares do not fill a 5x5 grid")
            continue
        centre = pos[(2, 2)]
        if centre["num"] != 0 or centre["text"] != "FREE":
            errs.append(f"board {bnum}: centre is not FREE ({centre['text']})")
        if len([c for c in cs if c["text"] == "FREE" or c["num"] == 0]) != 1:
            errs.append(f"board {bnum}: not exactly one FREE square")
        others = [c for c in cs if (c["r"], c["c"]) != (2, 2)]
        if len(others) != PER_BOARD:
            errs.append(f"board {bnum}: {len(others)} challenge squares, expected {PER_BOARD}")
        texts = [c["text"] for c in others]
        if len(set(texts)) != PER_BOARD or "" in texts:
            errs.append(f"board {bnum}: challenges are not {PER_BOARD} distinct non-empty texts")
        for c in others:
            if str(c["num"]) != c["numTxt"]:
                errs.append(f"board {bnum}: corner number {c['numTxt']} vs data {c['num']}")
            if master.get(c["num"]) != c["text"]:
                errs.append(f"board {bnum}: square '{c['text']}' does not match caller sheet #{c['num']} '{master.get(c['num'])}'")
        sets[bnum] = frozenset(c["num"] for c in others)
        layouts[bnum] = tuple(pos[(r, c)]["num"] for r in range(5) for c in range(5))
    bl = sorted(sets)
    for i in bl:
        for j in bl:
            if i < j:
                if sets[i] == sets[j]:
                    errs.append(f"boards {i} and {j} have the same challenges")
                if layouts[i] == layouts[j]:
                    errs.append(f"boards {i} and {j} are identical")
                if len(sets[i] & sets[j]) != SHARED:
                    errs.append(f"boards {i} and {j} share {len(sets[i] & sets[j])} challenges, text says {SHARED}")
    for n in range(1, NCH + 1):
        on = [b for b in bl if n in sets[b]]
        if len(on) != APPEARS:
            errs.append(f"challenge {n} is on {len(on)} boards, text says {APPEARS}")
        call = next((c for c in d["calls"] if c["num"] == n), None)
        if call:
            listed = [int(x) for x in re.findall(r"\d+", call["boards"])]
            if listed != on:
                errs.append(f"caller sheet #{n} says boards {listed}, boards have it on {on}")
    allnums = set().union(*sets.values()) if sets else set()
    if allnums != set(range(1, NCH + 1)):
        errs.append(f"boards use {len(allnums)} distinct challenges, caller sheet has {NCH}")
    if NBOARDS * PER_BOARD != NCH * APPEARS:
        errs.append("board arithmetic: boards x squares != challenges x appearances")
    for t in master.values():
        for w in BANNED:
            if re.search(r"\b" + re.escape(w) + r"\b", t.lower()):
                errs.append(f"challenge '{t}' contains instrument-specific or brand word '{w}'")
        if len(t) > 60:
            errs.append(f"challenge too long for a square: {t}")
    # tracker
    days = d["days"]
    if sorted(x["day"] for x in days) != list(range(1, TRACK_DAYS + 1)):
        errs.append(f"tracker day cells are not 1..{TRACK_DAYS}")
    for x in days:
        if str(x["day"]) != x["txt"]:
            errs.append(f"tracker cell data-day {x['day']} prints {x['txt']}")
        if x["row"] != (x["day"] - 1) // TRACK_COLS + 1:
            errs.append(f"tracker day {x['day']} sits in week row {x['row']}")
    weeks = d["weeks"]
    if len(weeks) != TRACK_WEEKS:
        errs.append(f"tracker has {len(weeks)} week rows, expected {TRACK_WEEKS}")
    covered = 0
    spans = {}
    for w in weeks:
        m = re.search(r"days (\d+)–(\d+)", w["label"])
        if not m:
            errs.append(f"week row {w['week']}: label '{w['label']}' unreadable")
            continue
        a, b = int(m.group(1)), int(m.group(2))
        spans[w["week"]] = b - a + 1
        mine = sorted(x["day"] for x in days if x["row"] == w["week"])
        if mine != list(range(a, b + 1)):
            errs.append(f"week {w['week']}: label says days {a}-{b}, cells are {mine}")
        if w["ndays"] + w["offs"] != TRACK_COLS or w["cols"] != TRACK_COLS + 2:
            errs.append(f"week {w['week']}: row has {w['ndays']} day cells + {w['offs']} blank, {w['cols']} columns")
        if not w["hasTot"]:
            errs.append(f"week {w['week']}: no week total cell")
        covered += b - a + 1
    if covered != TRACK_DAYS:
        errs.append(f"week labels cover {covered} days, not {TRACK_DAYS}")
    if len(d["sumboxes"]) != TRACK_WEEKS or len(d["grand"]) != 1 or "30-day total" not in d["grand"][0].lower():
        errs.append("tracker total row: expected one box per week plus the 30-day total")
    for sbx in d["sumboxes"]:
        nd = spans.get(sbx["week"], 0)
        if nd != TRACK_COLS and f"({nd} days)" not in sbx["txt"].lower():
            errs.append(f"total box week {sbx['week']} should say ({nd} days)")
        if nd == TRACK_COLS and "days)" in sbx["txt"].lower():
            errs.append(f"total box week {sbx['week']} wrongly says a short week")
    if "4 full weeks and 2 more days" in " ".join(d["pagetext"]):
        full = sum(1 for v in spans.values() if v == TRACK_COLS)
        rest = TRACK_DAYS - full * TRACK_COLS
        if (full, rest) != (4, 2):
            errs.append(f"tracker subtitle says 4 full weeks and 2 more days, rows give {full} and {rest}")
    ss = [x["s"] for x in d["streaks"]]
    if ss != sorted(set(ss)) or not ss or ss[-1] > TRACK_DAYS:
        errs.append(f"streak rewards {ss} must rise and stay within {TRACK_DAYS}")
    for x in d["streaks"]:
        if f"{x['s']} days in a row" not in x["txt"].lower():
            errs.append(f"streak line {x['s']} label mismatch")
    for g in d["goals"]:
        m = re.search(rf"{g['g']} × {TRACK_DAYS} days = (\d+) minutes", g["txt"])
        if not m or int(m.group(1)) != g["g"] * TRACK_DAYS:
            errs.append(f"goal row {g['g']}: '{g['txt']}' is not {g['g']} x {TRACK_DAYS}")
    if [g["g"] for g in d["goals"]] != GOALS:
        errs.append("goal rows differ from GOALS")
    # printed products and points
    if not d["muls"]:
        errs.append("no printed products found")
    for m in d["muls"]:
        a, b, c = (int(x) for x in m["a"].split(","))
        if a * b != c or m["txt"] != str(c):
            errs.append(f"printed product {a} x {b} = {m['txt']} (attribute {c}) is wrong")
    if sum(p["v"] for p in d["pts"]) != 100 or any(p["txt"] != str(p["v"]) for p in d["pts"]):
        errs.append(f"grading points add to {sum(p['v'] for p in d['pts'])}, not 100")
    for p in d["ptstotal"]:
        if p["v"] != sum(x["v"] for x in d["pts"]) or p["txt"] != str(p["v"]):
            errs.append("grading total does not match its parts")
    # weekly logs
    for w in range(1, NLOGS + 1):
        rows = [x for x in d["logrows"] if x["id"].startswith(f"{w}-")]
        if [x["day"].title() for x in rows] != DAYS:
            errs.append(f"log {w}: day rows {[x['day'] for x in rows]}")
        if any(x["nrate"] != 5 or x["page"] != P_LOG0 + w - 1 or x["ncells"] != 6 for x in rows):
            errs.append(f"log {w}: a row lacks 5 rating circles / 6 columns / is on the wrong page")
    # how to win diagrams
    want = {"row": 5, "col": 5, "diag": 5, "black": 25}
    for g in d["diags"]:
        cs = {tuple(int(v) for v in s.split(",")) for s in g["cells"].split(";")}
        if len(cs) != want[g["k"]]:
            errs.append(f"diagram {g['k']} lights {len(cs)} squares, expected {want[g['k']]}")
        rs, cc = {r for r, _ in cs}, {c for _, c in cs}
        ok = {"row": len(rs) == 1 and len(cc) == 5, "col": len(cc) == 1 and len(rs) == 5,
              "diag": all(r == c for r, c in cs) or all(r + c == 4 for r, c in cs), "black": len(cs) == 25}[g["k"]]
        if not ok:
            errs.append(f"diagram {g['k']} is not a {g['k']}")
    if sorted(g["k"] for g in d["diags"]) != sorted(want):
        errs.append("how-to-win diagrams missing")
    if not d["lines"] or "5 rows + 5 columns + 2 diagonals = 12 possible lines" not in d["lines"][0] or 5 + 5 + 2 != 12:
        errs.append("how-to-win line count statement wrong")
    ws = [s["n"] for s in d["steps"] if s["page"] == P_WIN]
    if ws != [str(i) for i in range(1, len(ws) + 1)] or not ws:
        errs.append("how-to-win step numbers are not 1..n")
    if f"how to play in {len(ws)} steps" not in d["pagetext"][P_WIN - 1].lower():
        errs.append(f"how-to-win heading does not say {len(ws)} steps")
    # page kinds and cross references
    kinds = [p["kind"] for p in d["pages"]]
    exp = ["cover", "teacher", "parent", "win"] + ["log"] * NLOGS + ["tracker", "caller"] + ["board"] * NBOARDS + ["terms"]
    if kinds != exp or len(kinds) != TOTAL_PAGES:
        errs.append(f"page kinds {kinds} differ from the page map ({TOTAL_PAGES} pages)")
    tt = d["pagetext"][P_TEACH - 1].lower()
    for need in (f"Pages {P_BOARD0}–{P_BOARD0 + NBOARDS - 1}: {NBOARDS} bingo boards", f"Pages {P_LOG0}–{P_LOG0 + NLOGS - 1}: {NLOGS} weekly practice logs",
                 f"Page {P_TRACK}: 30-day tracker", f"Page {P_CALL}: challenge list", f"Page {P_PARENT}: parent note", f"Page {P_WIN}: how to win",
                 f"Page {P_TERMS}: terms", f"({TOTAL_PAGES} pages)"):
        if need.lower() not in tt:
            errs.append(f"teacher notes: missing '{need}'")
    for p in d["pages"]:
        txt = d["pagetext"][p["n"] - 1]
        if p["kind"] == "board" and f"Board {p['n'] - P_BOARD0 + 1} of {NBOARDS}" not in txt:
            errs.append(f"page {p['n']}: board heading does not match its position")
        if p["kind"] == "log" and f"Week {p['n'] - P_LOG0 + 1}" not in txt:
            errs.append(f"page {p['n']}: log heading does not match its position")
    tp = d["pagetext"][P_TERMS - 1]
    if f"{TOTAL_PAGES} pages in all" not in tp or f"page {P_TERMS} these terms" not in tp:
        errs.append("terms page: page list does not match")
    alltext = " ".join(d["pagetext"]).lower()
    for w in UK_SPELLINGS:
        if w in alltext:
            errs.append(f"non-US spelling '{w}' in the pages")
    if re.search(r"\$|dollar|money|pay for|cost|buy", d["pagetext"][P_PARENT - 1].lower()):
        errs.append("parent note mentions money")
    return errs


def pdf_fonts(path):
    out = subprocess.run(["pdffonts", path], capture_output=True, text=True, check=True).stdout.splitlines()[2:]
    return [(line.split()[0], line.split()[-5]) for line in out]


def load_json(name):
    return json.load(open(os.path.join(TPT, name)))


def verify_images():
    errs = []
    from PIL import Image
    for p in [COVER_PNG, *PREVIEW_PNGS]:
        im = Image.open(p).convert("L")
        if im.size != (2000, 2000):
            errs.append(f"{os.path.basename(p)}: not 2000x2000")
            continue
        px = im.load()
        rows = [sum(1 for x in range(0, 2000, 8) if px[x, y] < 200) for y in range(0, 2000, 2)]
        ytop = 2000
        for y in range(1998, 0, -2):
            if rows[y // 2] > 0.9 * 250:
                ytop = y
            else:
                break
        run = best = 0
        for y in range(120, ytop, 2):
            if rows[y // 2] == 0:
                run += 2
                best = max(best, run)
            else:
                run = 0
        if best > 200:
            errs.append(f"{os.path.basename(p)}: blank band of {best}px (more than 10% of the image)")
        last = max((y for y in range(0, ytop, 2) if rows[y // 2] > 0), default=0)
        if ytop - last > 200:
            errs.append(f"{os.path.basename(p)}: {ytop - last}px blank above the bottom band")
    return errs


def verify_files():
    errs = []
    from pypdf import PdfReader
    for p in [PDF, PREVIEW_PDF, COVER_PNG, *PREVIEW_PNGS, UPLOAD, TPT_JSON, os.path.join(TPT, "STYLE.md"), RENDER_JS]:
        if not os.path.exists(p):
            errs.append(f"missing {os.path.relpath(p, TPT)}")
    if errs:
        return errs
    for path, want in ((PDF, TOTAL_PAGES), (PREVIEW_PDF, 4)):
        rd = PdfReader(path)
        if len(rd.pages) != want:
            errs.append(f"{os.path.basename(path)}: {len(rd.pages)} pages, expected {want}")
        for i, pg in enumerate(rd.pages):
            w, h = float(pg.mediabox.width), float(pg.mediabox.height)
            if abs(w - 612) > 1 or abs(h - 792) > 1:
                errs.append(f"{os.path.basename(path)} p{i + 1}: {w:.0f}x{h:.0f}pt, not US Letter")
        fonts = pdf_fonts(path)
        for name, emb in fonts:
            if emb != "yes":
                errs.append(f"{os.path.basename(path)}: font {name} not embedded")
        names = " ".join(n for n, _ in fonts).lower().replace(" ", "")
        for fam in ("oswald", "sourcesans3"):
            if fam not in names:
                errs.append(f"{os.path.basename(path)}: {fam} not found in PDF fonts")
    rd = PdfReader(PDF)
    for i, pg in enumerate(rd.pages):
        t = pg.extract_text() or ""
        if len(t.strip()) < 40:
            errs.append(f"PDF page {i + 1} looks blank")
        if "PREVIEW" in t.upper():
            errs.append(f"product PDF page {i + 1} carries a PREVIEW watermark")
    allpdf = " ".join((pg.extract_text() or "") for pg in rd.pages).replace("\n", " ")
    for m in re.finditer(r"(\d+) pages", allpdf):
        if int(m.group(1)) != TOTAL_PAGES:
            errs.append(f"PDF text claims '{m.group(0)}', PDF has {TOTAL_PAGES}")
    if f"{TOTAL_PAGES} pages" not in allpdf:
        errs.append("PDF never states its page count")
    prd = PdfReader(PREVIEW_PDF)
    for i in range(4):
        if (prd.pages[i].extract_text() or "").count("PREVIEW") != 1:
            errs.append(f"preview PDF page {i + 1}: expected exactly one PREVIEW watermark")
    errs += verify_images()
    for h in ("cover.html", "p1.html", "p2.html", "p3.html"):
        p = os.path.join(BUILD, h)
        if os.path.exists(p):
            s = open(p).read()
            for m in re.finditer(r"(\d+) pages", re.sub(r"<[^>]+>", " ", s)):
                if int(m.group(1)) != TOTAL_PAGES:
                    errs.append(f"{h}: claims {m.group(0)}")
            if "swm" in s or "PREVIEW" in s:
                errs.append(f"{h}: has its own watermark layer (the page shots already carry one)")
    up = open(UPLOAD).read()
    m = re.search(r"^## 1\. Title\s*\n+```\n(.+?)\n```", up, re.M | re.S)
    if not m:
        errs.append("UPLOAD.md: title block not found")
    else:
        title = m.group(1).strip()
        if len(title) > 80:
            errs.append(f"UPLOAD.md: title is {len(title)} chars (max 80)")
        if re.search(r"winter|snow|holiday|christmas|\bfall\b|autumn|spring|summer|halloween|new year", title, re.I):
            errs.append("UPLOAD.md: seasonal word in the title")
    for need in (DISCLOSURE, f"${PRICE}", f"{TOTAL_PAGES} pages", f"{NBOARDS} different", f"{NCH} challenges"):
        if need not in up:
            errs.append(f"UPLOAD.md: missing '{need}'")
    for m in re.finditer(r"(\d+) pages", up):
        if int(m.group(1)) not in (TOTAL_PAGES, NLOGS, NBOARDS):
            errs.append(f"UPLOAD.md: claims '{m.group(0)}'")
    sec = up.split("## 5. Page count by section")[1].split("##")[0]
    nums = [int(x) for x in re.findall(r"^- (?!Total)[^\n]*: (\d+)$", sec, re.M)]
    if sum(nums) != TOTAL_PAGES:
        errs.append(f"UPLOAD.md page list sums to {sum(nums)}, PDF has {TOTAL_PAGES}")
    if re.search(r"checked by hand|handmade|hand-checked|classroom-tested|recomputed|--check", up, re.I):
        errs.append("UPLOAD.md: forbidden claim or internal QA wording")
    desc = up.split("## 2. Description")[1].split("## 3.")[0].lower()
    for w in UK_SPELLINGS:
        if w in desc:
            errs.append(f"UPLOAD.md: non-US spelling {w}")
    tj = json.load(open(TPT_JSON))
    tags, subs = set(load_json("TAG-OPTIONS.json")["options"]), set(load_json("SUBJECT-OPTIONS.json"))
    if not 1 <= len(tj["tags"]) <= 6 or any(t not in tags for t in tj["tags"]):
        errs.append(f"tpt.json tags invalid: {tj['tags']}")
    if not 1 <= len(tj["subjects"]) <= 3 or any(s not in subs for s in tj["subjects"]):
        errs.append(f"tpt.json subjects invalid: {tj['subjects']}")
    if not 1 <= len(tj["grades"]) <= 4:
        errs.append("tpt.json grades must be 1-4")
    if tj.get("pages") != TOTAL_PAGES:
        errs.append(f"tpt.json pages {tj.get('pages')} != {TOTAL_PAGES}")
    if tj["price"] != PRICE:
        errs.append("tpt.json price mismatch")
    return errs


def check():
    files = [os.path.join(BUILD, "resource.html"), os.path.join(BUILD, "shots.html")]
    if not all(os.path.exists(x) for x in files):
        sys.exit("build html missing: run gen.py first")
    data = inspect_html(files)
    res, shots = data["resource.html"], data["shots.html"]
    errs = verify_content(res)
    errs += ["resource: " + e for e in res["layout"]] + ["shots: " + e for e in shots["layout"]]
    for k in PREVIEW_ORDER:
        n = SHOT_PAGES[k]
        gap = shots["gaps"][n - 1]
        if gap > 105:
            errs.append(f"preview page {k} (page {n}): {gap}px blank above the footer (max 105)")
    errs += verify_files()
    if errs:
        print("CHECK FAILED")
        print("\n".join(" - " + e for e in errs[:80]))
        sys.exit(1)
    print(f"CHECK OK: {NBOARDS} boards of {PER_BOARD} distinct challenges + FREE centre read back from the render; {NCH} challenges each on {APPEARS} boards, "
          f"any two boards share {SHARED}; caller sheet matches the squares; tracker {TRACK_DAYS} days in {TRACK_WEEKS} week rows, totals and goal products recomputed; "
          f"grading points = 100; layout clear of footers and boxes; PDF {TOTAL_PAGES} Letter pages, preview 4 (one watermark each), fonts embedded; "
          f"images 2000x2000; UPLOAD.md and tpt.json ok.")


if __name__ == "__main__":
    if "--check" in sys.argv:
        check()
    else:
        build()
