#!/usr/bin/env python3
"""Music Goals and Practice Tracker (TpT 094): build the resource and verify it.

    python3 gen.py           build everything (PDFs, PNGs, UPLOAD.md, tpt.json) into this folder
    python3 gen.py --check   re-read the rendered HTML and SVG and recompute: the two 30-day logs (30 numbered cells each, rows of 7, 7, 7, 7 and 2),
                             the practice-plan minute splits and the stacked bar, the totals page (day boxes per week, 30 in all), both chart grids
                             (cells counted from the drawing), the SMART letters, the cross-references, the layout (footer gaps, drawing padding,
                             blank bands, text fit) and the files

Content lives in the DATA section. The pack has no music notation. Drawings are built here and `--check` reads their geometry back from the
rendered HTML with formulas typed separately in the CHECK section.
"""
import json
import math
import os
import re
import subprocess
import sys
from html import escape

HERE = os.path.dirname(os.path.abspath(__file__))
TPT = os.path.dirname(HERE)
FONTS = os.path.join(TPT, "fonts")
BUILD = os.path.join(HERE, "build")
RENDER_JS = os.path.join(TPT, "tools", "render.js")
HERO = os.path.join(HERE, "art", "hero.png")

SLUG = "music-goals-practice-tracker"
PDF = os.path.join(HERE, f"{SLUG}.pdf")
PREVIEW_PDF = os.path.join(HERE, f"{SLUG}-PREVIEW.pdf")
COVER_PNG = os.path.join(HERE, "cover.png")
PREVIEW_PNGS = [os.path.join(HERE, f"preview-{i}.png") for i in (1, 2, 3)]
UPLOAD = os.path.join(HERE, "UPLOAD.md")
TPT_JSON = os.path.join(HERE, "tpt.json")

STORE = "Brian Lotze"
BRAND = "Hudson Beat"
YEAR = 2026
ACCENT = "#4F95D0"   # the hero's blue
DISCLOSURE = "Created with the help of digital and AI tools. Notation and answer keys are verified before release."
TITLE = "Music Goals Tracker"
LISTING_TITLE = "Music Goals and Practice Tracker, 30-Day Practice Logs, Reflection, Gr 5-8"
PRICE = "3.50"
TAGS = ["New Year", "Printables", "Worksheets", "Graphic Organizers", "Study Skills", "Homework"]
SUBJECTS = ["Music", "Instrumental Music", "Vocal Music"]
GRADES = ["5th-grade", "6th-grade", "7th-grade", "8th-grade"]

# ================================================================== DATA
DAYS = 30
WEEKS = [(1, 7), (8, 14), (15, 21), (22, 28)]      # four weekly rows of seven days
BONUS = (29, 30)                                   # days 29 and 30 fill the fifth row
FOCUS = [(1, "hard to focus"), (2, "okay"), (3, "locked in")]
WAYS = ["playing", "singing", "tapping or clapping", "listening closely", "composing or making a beat"]

PARTS = [("Warm-up", "Get your hands, breath or voice ready: long notes, easy patterns, slides, steady taps."),
         ("New material", "Learn something you cannot do yet. Go slowly and work in small pieces."),
         ("Review", "Go back to something you already know and make it smoother."),
         ("Fun", "Play, sing, tap or make up anything you enjoy.")]
PLANS = [(10, [2, 5, 2, 1]), (15, [3, 7, 3, 2]), (20, [3, 10, 4, 3]), (30, [5, 15, 6, 4])]
EXAMPLE_TOTAL = 20
NO_INSTRUMENT = [("Warm-up", "hum or sing a slow pattern, or clap a steady beat"), ("New material", "tap a new rhythm, or learn a short melody by ear"),
                 ("Review", "sing or tap something you already know"), ("Fun", "make up a beat, a melody or a rhythm, or listen to a favorite")]

SMART = [("S", "Specific", "Say exactly what you will do.", "What will I play, sing, tap, listen to or create?"),
         ("M", "Measurable", "You can count it or check it.", "How will I know when I am done? How many times, minutes or measures?"),
         ("A", "Achievable", "It is a stretch, but you can really do it.", "Can I do this in the time I have? Who could help me?"),
         ("R", "Relevant", "It matters to you and to your music.", "Why do I want this? How does it help my music?"),
         ("T", "Time-bound", "It has a finish line.", "By which day or date will I be done?")]
SMART_WORDS = [w for _, w, _, _ in SMART]
EX_FUZZY = "Get better at my music."
EX_SMART = ("By day 30, I will play or sing the first 8 measures of my class piece without stopping, at the speed my teacher chose. "
            "I will make music at least 5 days each week to get ready for our performance.")
EX_PARTS = [("S", "the first 8 measures of my class piece"), ("M", "without stopping, at my teacher's speed, 5 days each week"),
            ("A", "8 measures is a small part of the piece, not all of it"), ("R", "it helps me get ready for our performance"), ("T", "by day 30")]
EX2 = "By day 30, I will listen to 3 different kinds of music and write one sentence about each."

CATS = [("Skill", "Get better at something.", "learn a new scale or chord, read rhythms faster, sing a harmony part, play a passage smoothly"),
        ("Performance", "Share your music with others.", "play or sing in a concert, perform for family or friends, play one piece from memory"),
        ("Listening and creating", "Hear something new or make something of your own.", "listen to a new style, write a short melody, make a beat, improvise four measures")]

TIPS = [("Short and regular is a good place to start", "A little music time on most days can feel easier to keep going than one long session. Pick an amount you can really do."),
        ("Pick a time and a place", "Link music time to something you already do, such as after a snack or before dinner. A steady spot helps you remember."),
        ("Warm up first", "Begin with something easy so your hands, breath or voice are ready. It also helps you settle in."),
        ("Start slowly", "Go slowly enough that you can get it right, then speed up a little at a time."),
        ("Work in small pieces", "Choose one line, one measure or one phrase. Fix the small part, then put it back into the whole."),
        ("Fix one thing at a time", "Ask: what is the one thing I want to improve right now? Rhythm, notes, breath, or how it sounds?"),
        ("Mark the tricky spots", "Put a pencil dot or sticky note at spots that need more work. Come back to them first next time."),
        ("End with something fun", "Finish with a song you like or a sound you want to try. That gives you a reason to come back.")]

WEEK_PROMPTS = [("Starting out", "What was it like to start? What time and place worked best for music time?"),
                ("Keeping going", "Which habit is helping you? What got in the way of music time this week?"),
                ("Check your goals", "Look at your small goals again. Does one need to be smaller, bigger or have a new date?"),
                ("Looking back", "Look back at all four weeks. What are you proud of? What will you keep doing?")]

# Pages, in order
ORDER = ["cover", "teach", "start", "smart", "goal", "year", "plan", "tips", "logA", "logB", "w1", "w2", "w3", "w4", "totals", "chart", "cert", "terms"]
P = {k: i + 1 for i, k in enumerate(ORDER)}
TOTAL_PAGES = len(ORDER)
PAGE_NAMES = {"cover": "Cover", "teach": "Teacher notes", "start": "Start here", "smart": "SMART goals guide", "goal": "Big goal and small goals",
              "year": "My music year", "plan": "Practice plan", "tips": "Practice tips", "logA": "30-day log: minutes", "logB": "30-day log: what I worked on",
              "w1": "Weekly reflection 1", "w2": "Weekly reflection 2", "w3": "Weekly reflection 3", "w4": "Weekly reflection 4",
              "totals": "Practice minutes totals", "chart": "Progress chart", "cert": "Celebration certificate", "terms": "Terms of use and credits"}


def pg(k):
    return f"page {P[k]}"


def pgs(a, b):
    return f"pages {P[a]}–{P[b]}"


def f2(v):
    return f"{v:.2f}".rstrip("0").rstrip(".")


def wl(n, h=None):
    st = f' style="height:{h}pt"' if h else ""
    return f'<div class="wl"{st}></div>' * n


def fc(n):
    return f'<i class="fc">{n}</i>'


def cbx(t=""):
    return f'<i class="cb"></i>{escape(t)}'


# ================================================================== drawings (all in code)
def plan_bar_svg(total, mins, w=700, h=64, pad=6, sw=2):
    """A stacked bar whose segment widths are proportional to the minutes. Segments are labeled inside."""
    usable = w - 2 * pad
    x = pad
    out = []
    shades = ["#fff", "#CFE3F4", "#fff", "#CFE3F4"]
    for (name, _), m, sh in zip(PARTS, mins, shades):
        sw_ = usable * m / total
        out.append(f'<rect class="seg" data-part="{name}" data-min="{m}" x="{f2(x)}" y="{pad}" width="{f2(sw_)}" height="{h - 2 * pad}" fill="{sh}" stroke="#000" stroke-width="{sw}"/>')
        out.append(f'<text x="{f2(x + sw_ / 2)}" y="{pad + 22}" text-anchor="middle" font-family="Oswald" font-weight="700" font-size="15" fill="#000">{name.upper()}</text>')
        out.append(f'<text x="{f2(x + sw_ / 2)}" y="{pad + 40}" text-anchor="middle" font-family="Source Sans 3" font-weight="600" font-size="14" fill="#000">{m} min</text>')
        x += sw_
    return f'<svg class="pbar" data-total="{total}" viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg">{"".join(out)}</svg>'


def grid_svg(kind, cols, rows, cw, ch, step, label_every=1, left=46, top=8, bottom=26, pad=4, sw=1.2):
    """A colour-in bar chart: `cols` columns by `rows` rows of empty cells. Row r (from the bottom) stands for r*step minutes."""
    W = left + cols * cw + pad + 2
    H = top + rows * ch + bottom
    out = []
    for r in range(rows):                       # r = 0 is the top row
        level = rows - r
        for c in range(cols):
            out.append(f'<rect class="gc" data-col="{c + 1}" data-level="{level}" x="{f2(left + c * cw)}" y="{f2(top + r * ch)}" width="{cw}" height="{ch}" fill="none" stroke="#000" stroke-width="{sw}"/>')
        out.append(f'<text class="ylab" data-level="{level}" x="{left - 6}" y="{f2(top + r * ch + ch / 2 + 4)}" text-anchor="end" font-family="Source Sans 3" font-size="11" fill="#000">{level * step}</text>')
    for c in range(cols):
        out.append(f'<text class="xlab" data-col="{c + 1}" x="{f2(left + c * cw + cw / 2)}" y="{top + rows * ch + 16}" text-anchor="middle" font-family="Source Sans 3" font-size="11" fill="#000">{c + 1 if kind == "day" else "Week " + str(c + 1)}</text>')
    return f'<svg class="gsv" data-kind="{kind}" data-cols="{cols}" data-rows="{rows}" data-step="{step}" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">{"".join(out)}</svg>'


def badge_svg(size=120):
    """A star rosette: a ring, a star and two ribbon tails. All strokes keep 6+ units from the viewBox edge."""
    cx, cy, R, r = 60, 52, 38, 17
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rad = 24 if i % 2 == 0 else 10
        pts.append(f"{f2(cx + rad * math.cos(ang))},{f2(cy + rad * math.sin(ang))}")
    s = 'stroke="#000" stroke-linejoin="round" stroke-linecap="round"'
    return (f'<svg class="badge" viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg">'
            f'<polygon points="42,84 34,114 50,106 58,114 62,86" fill="{ACCENT}" {s} stroke-width="3"/>'
            f'<polygon points="78,84 86,114 70,106 62,114 58,86" fill="#fff" {s} stroke-width="3"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="#fff" {s} stroke-width="4"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{R - 8}" fill="none" {s} stroke-width="2"/>'
            f'<polygon points="{" ".join(pts)}" fill="{ACCENT}" {s} stroke-width="3"/></svg>')

def font_css():
    f = os.path.relpath(FONTS, BUILD)
    faces = [("Oswald", 300, "normal", "oswald-latin-300-normal"), ("Oswald", 500, "normal", "oswald-latin-500-normal"), ("Oswald", 700, "normal", "oswald-latin-700-normal"),
             ("Source Sans 3", 400, "normal", "source-sans-3-latin-400-normal"), ("Source Sans 3", 400, "italic", "source-sans-3-latin-400-italic"),
             ("Source Sans 3", 600, "normal", "source-sans-3-latin-600-normal"), ("Source Sans 3", 700, "normal", "source-sans-3-latin-700-normal"),
             ("Bravura", 400, "normal", "bravura")]
    return "".join(f"@font-face{{font-family:'{n}';font-weight:{w};font-style:{s};src:url('{f}/{file}.woff2') format('woff2');}}" for n, w, s, file in faces)




# ================================================================== CSS
CSS = """
@page { size: 8.5in 11in; margin: 0; }
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; background: #fff; color: #000; }
body { font-family: 'Source Sans 3', sans-serif; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
.page { width: 8.5in; height: 11in; position: relative; overflow: hidden; page-break-after: always; break-after: page;
        padding: 0.42in 0.5in 0.38in; display: flex; flex-direction: column; }
.page:last-child { page-break-after: auto; break-after: auto; }
.top { display: flex; justify-content: space-between; align-items: flex-end; border-bottom: 2.2pt solid #000; padding-bottom: 6pt; }
.top .t { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; letter-spacing: .01em; line-height: 1; font-size: 19pt; white-space: nowrap; }
.top .t small { display: block; font-family: 'Oswald'; font-weight: 300; text-transform: none; font-size: 11pt; letter-spacing: 0; margin-top: 3pt; white-space: nowrap; }
.top .tag { flex: none; white-space: nowrap; text-align: right; }
.tag .lv { display: inline-block; background: #000; color: #fff; font-family: 'Oswald'; font-weight: 700; font-size: 15pt; padding: 3pt 9pt 4pt; border-radius: 4pt; letter-spacing: .04em; }
.tag .lv.ak { background: ACCENT; }
.tag .ln { font-family: 'Oswald'; font-weight: 300; font-size: 11pt; margin-top: 3pt; }
.foot { display: flex; justify-content: space-between; font-size: 8.5pt; color: #333; border-top: .8pt solid #000; padding-top: 3pt; margin-top: auto; }
.wm { position: absolute; left: 50%; top: 50%; transform: translate(-50%, -50%) rotate(-38deg); font-family: 'Oswald'; font-weight: 700;
      font-size: 150pt; color: rgba(0,0,0,.13); letter-spacing: .06em; white-space: nowrap; pointer-events: none; z-index: 9; }
.doc h1 { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 28pt; margin: 0 0 4pt; line-height: 1; }
.doc h2 { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 13pt; margin: 7pt 0 3pt; letter-spacing: .02em; }
.doc p, .doc li { font-size: 10.4pt; line-height: 1.32; margin: 0 0 4pt; }
.doc ul, .doc ol { margin: 0 0 3pt; padding-left: 16pt; }
.doc .rule { border-bottom: 2.2pt solid #000; margin-bottom: 8pt; padding-bottom: 6pt; }
.doc table { border-collapse: collapse; width: 100%; table-layout: fixed; font-size: 10pt; margin: 2pt 0 4pt; }
.doc td, .doc th { border: 1pt solid #000; padding: 3pt 6pt; text-align: left; vertical-align: middle; }
.doc th { font-family: 'Oswald'; font-weight: 500; text-transform: uppercase; font-size: 9.5pt; background: #000; color: #fff; }
.small { font-size: 9pt !important; color: #333; }
.box { border: 1.3pt solid #000; border-radius: 7pt; padding: 6pt 10pt 3pt; margin: 5pt 0; }
.box h3 { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 12pt; margin: 0 0 3pt; letter-spacing: .02em; }
.box p, .box li { font-size: 10pt !important; line-height: 1.3; }
.box p { margin: 0 0 3pt !important; }
.cols { display: flex; gap: 12pt; }
.cols .box { flex: 1; min-width: 0; }
.nd { display: flex; align-items: flex-end; gap: 6pt; font-size: 10pt; margin: 7pt 0 0; }
.nd .ln { flex: 1; border-bottom: 1pt solid #000; height: 11pt; }
.rb { flex: 1; display: flex; flex-direction: column; gap: 8pt; padding: 8pt 0 10px; min-height: 0; }
.cb { display: inline-block; width: 11pt; height: 11pt; border: 1.2pt solid #000; border-radius: 2pt; vertical-align: -2pt; margin-right: 4pt; }
.fc { display: inline-flex; align-items: center; justify-content: center; width: 12pt; height: 12pt; border: 1.1pt solid #000; border-radius: 50%; font-style: normal;
      font-family: 'Oswald'; font-weight: 500; font-size: 7.5pt; line-height: 1; flex: none; }
.wbox { border: 1.3pt solid #000; border-radius: 7pt; padding: 5pt 9pt 6pt; display: flex; flex-direction: column; min-height: 0; }
.wbox .lab { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 11pt; letter-spacing: .04em; margin: 0 0 1pt; }
.wbox > .hint { font-size: 9.2pt; color: #333; line-height: 1.25; margin: 0 0 2pt; }
.wbox .wl { border-bottom: 1pt solid #000; height: 20pt; flex: none; }
.wbox .grow { flex: 1; display: flex; flex-direction: column; justify-content: space-evenly; min-height: 0; }
.wbox .grow .wl { height: 18pt; }
.wl { border-bottom: 1pt solid #000; height: 20pt; }
.row { display: flex; gap: 10pt; }
.row > * { flex: 1; min-width: 0; }
.pill { display: inline-block; background: #000; color: #fff; font-family: 'Oswald'; font-weight: 700; font-size: 10.5pt; letter-spacing: .06em; padding: 1pt 8pt 2pt; border-radius: 10pt; white-space: nowrap; }
.pill.b { background: ACCENT; }
.num { display: inline-flex; align-items: center; justify-content: center; width: 20pt; height: 20pt; border-radius: 50%; background: #000; color: #fff; font-family: 'Oswald'; font-weight: 700; font-size: 11pt; flex: none; }
.num.b { background: ACCENT; }
.tt { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; letter-spacing: .03em; }
/* logs */
.leg { border: 1.2pt solid #000; border-radius: 6pt; padding: 4pt 9pt 3pt; margin: 6pt 0 0; font-size: 9.6pt; line-height: 1.28; }
.leg b { font-family: 'Oswald'; text-transform: uppercase; letter-spacing: .03em; font-weight: 700; }
.lgrid { flex: 1; display: flex; flex-direction: column; gap: 2pt; min-height: 0; padding: 6pt 0 10px; }
.wkl { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 9.5pt; letter-spacing: .05em; line-height: 1; margin-top: 3pt; }
.wkl span { font-weight: 300; text-transform: none; letter-spacing: 0; margin-left: 4pt; }
.lrow { display: flex; gap: 5pt; flex: 1; min-height: 0; }
.lrow .cell { flex: 0 0 calc((100% - 30pt) / 7); min-width: 0; border: 1.2pt solid #000; border-radius: 5pt; padding: 3pt 4pt 3pt; display: flex; flex-direction: column; }
.cell .dn { font-family: 'Oswald'; font-weight: 700; font-size: 13pt; line-height: 1; }
.cell .dn small { font-weight: 300; font-size: 7.5pt; letter-spacing: .06em; margin-right: 2pt; }
.cell .mw { display: flex; align-items: flex-end; gap: 3pt; font-family: 'Oswald'; font-weight: 500; font-size: 8.5pt; margin-top: 4pt; }
.cell .mw .ln { flex: 1; border-bottom: 1pt solid #000; height: 14pt; }
.cell .ww { flex: 1; display: flex; flex-direction: column; justify-content: flex-end; min-height: 0; padding-bottom: 3pt; }
.cell .ww small { font-size: 7.4pt; color: #444; line-height: 1; margin-bottom: 1pt; }
.cell .ww .ln { border-bottom: 1pt solid #000; height: 13pt; }
.cell .wr { flex: 1; display: flex; flex-direction: column; justify-content: space-evenly; min-height: 0; padding: 2pt 0; }
.cell .wr .ln { border-bottom: 1pt solid #000; height: 13pt; }
.cell .fo { display: flex; align-items: center; justify-content: space-between; font-size: 7.4pt; color: #333; }
.cell .fo .fcs { display: flex; gap: 2pt; }
.lrow .bnote { flex: 1; min-width: 0; border: 1.2pt dashed #000; border-radius: 5pt; padding: 4pt 8pt; font-size: 9.6pt; line-height: 1.3; display: flex; flex-direction: column; justify-content: center; }
.lrow .bnote b { font-family: 'Oswald'; text-transform: uppercase; letter-spacing: .03em; }
.lrow .bnote .ln { border-bottom: 1pt solid #000; height: 15pt; }
/* plan, charts, totals */
.pbar { display: block; width: 100%; }
.gsv { display: block; }
.pt { width: 100%; border-collapse: collapse; table-layout: fixed; }
.pt td, .pt th { text-align: center; }
.pt td.l { text-align: left; }
.trow { display: flex; align-items: stretch; gap: 5pt; }
.trow .wk { flex: 0 0 62pt; display: flex; flex-direction: column; justify-content: center; font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 11pt; line-height: 1.1; }
.trow .wk small { font-weight: 300; text-transform: none; font-size: 8.8pt; }
.trow .tb { flex: 0 0 calc((100% - 62pt - 88pt - 7 * 5pt) / 7); border: 1.2pt solid #000; border-radius: 4pt; padding: 2pt 3pt; font-size: 7.6pt; color: #333; min-height: 52pt; }
.trow .tot { flex: 1; display: flex; align-items: flex-end; gap: 4pt; font-family: 'Oswald'; font-weight: 500; font-size: 15pt; line-height: 1; }
.trow .tot .ln { flex: 1; border-bottom: 1pt solid #000; height: 18pt; }
.fml { font-size: 9.8pt; color: #222; margin: 9pt 0 3pt; }
.fml b { font-family: 'Oswald'; text-transform: uppercase; letter-spacing: .03em; }
/* certificate */
.certf { flex: 1; min-height: 0; border: 4pt double #000; border-radius: 10pt; padding: 14pt 22pt; margin: 10pt 0 10px; display: flex; flex-direction: column; align-items: center; text-align: center; }
.certf .badge { width: 1.15in; height: 1.15in; flex: none; }
.certf h1 { font-size: 34pt; margin: 2pt 0 0; letter-spacing: .02em; }
.certf .sub { font-family: 'Oswald'; font-weight: 300; font-size: 15pt; margin: 2pt 0 8pt; }
.certf .fl { width: 100%; display: flex; align-items: flex-end; gap: 7pt; font-size: 11.5pt; margin: 8pt 0 0; text-align: left; }
.certf .fl .ln { flex: 1; border-bottom: 1pt solid #000; height: 16pt; }
.certf .fl span.k { white-space: nowrap; }
.certf .three { display: flex; gap: 14pt; width: 100%; }
.certf .three > div { flex: 1; }
/* cover */
.cover { align-items: center; justify-content: space-between; padding: 0.55in 0.6in 0.5in; }
.store { font-family: 'Oswald'; font-weight: 500; font-size: 13pt; letter-spacing: .32em; text-transform: uppercase; }
.ctitle { text-align: center; }
.ctitle .a { font-family: 'Oswald'; font-weight: 700; font-size: 40pt; line-height: 1; letter-spacing: .02em; }
.ctitle .b { font-family: 'Oswald'; font-weight: 700; white-space: nowrap; font-size: 66pt; line-height: .95; letter-spacing: .01em; }
.ctitle .c { font-family: 'Oswald'; font-weight: 300; font-size: 15pt; margin-top: 8pt; }
.cband { width: 100%; background: #000; color: #fff; text-align: center; font-family: 'Oswald'; font-weight: 500; font-size: 14pt;
         letter-spacing: .08em; text-transform: uppercase; padding: 8pt 0 9pt; border-radius: 4pt; white-space: nowrap; }
.cband em { font-style: normal; color: ACCENT; }
""".replace("ACCENT", ACCENT)

def html_doc(pages, title="doc"):
    return (f'<!doctype html><html><head><meta charset="utf-8"><title>{escape(title)}</title><style>{font_css()}{CSS}</style></head>'
            f'<body>{"".join(pages)}</body></html>')


COPY = f"© {YEAR} {STORE} · {BRAND} · For single-classroom use"


def wm_div(on):
    return '<div class="wm">PREVIEW</div>' if on else ""




COPY = f"© {YEAR} {STORE} · {BRAND} · For single-classroom use"


def page(key, body, wm=False, tag="STUDENT", tagline="", ak=False, student=True, extra=""):
    n = P[key]
    right = f"Page {n}" + (f" · {extra}" if extra else "")
    top = (f'<div class="top"><div class="t">{TITLE}<small>{PAGE_NAMES[key]}</small></div>'
           f'<div class="tag"><div class="lv{" ak" if ak else ""}">{tag}</div><div class="ln">{tagline}</div></div></div>')
    nd = ('<div class="nd"><span>Name</span><span class="ln"></span><span>Date</span><span class="ln" style="flex:.45"></span>'
          '<span>Class</span><span class="ln" style="flex:.4"></span></div>') if student else ""
    return (f'<section class="page doc" data-p="{n}" data-k="{key}">{wm_div(wm)}{top}{nd}{body}'
            f'<div class="foot"><span>{COPY}</span><span>{right}</span></div></section>')


def doc_head(h1, sub):
    return f'<div class="rule" style="margin-top:8pt"><h1>{h1}</h1><div style="font-family:Oswald;font-weight:300;font-size:13pt">{sub}</div></div>'


def ways_text():
    return ", ".join(WAYS[:-1]) + " or " + WAYS[-1]


# ================================================================== pages
def cover_page():
    return (f'<section class="page cover" data-p="1" data-k="cover"><div class="store">{BRAND}</div>'
            f'<div style="height:4.6in;display:flex;align-items:center;justify-content:center"><img src="../art/hero.png" alt="" style="display:block;height:4.6in;width:auto;margin:-0.1in 0"></div>'
            f'<div class="ctitle"><div class="a">MUSIC GOALS AND</div><div class="b">PRACTICE TRACKER</div>'
            f'<div class="c">30-day practice logs, goal setting and reflection for any instrument or voice</div></div>'
            f'<div class="cband">Grades 5–8 <em>·</em> 2 thirty-day logs <em>·</em> {TOTAL_PAGES} pages</div></section>')


def teach_page(wm=False):
    body = (
        f'<div class="cols"><div class="box"><h3>How to use it in class</h3><ol>'
        f'<li><b>Launch (one class period).</b> Read {pg("start")} together and teach the SMART words on {pg("smart")}. Students write goals on {pgs("goal", "year")} and a plan on {pg("plan")}.</li>'
        f'<li><b>Four weeks.</b> Students fill in one log, {pg("logA")} (minutes) or {pg("logB")} (what I worked on), a little each day. Two minutes at the start or end of class works for a quick check-in.</li>'
        f'<li><b>Weekly reflection.</b> After days 7, 14, 21 and 28, students complete one page from {pgs("w1", "w4")}. Five to eight minutes is enough.</li>'
        f'<li><b>Finish.</b> On days 29 and 30 students add up their minutes on {pg("totals")}, color the chart on {pg("chart")} and may take the certificate on {pg("cert")}.</li></ol></div>'
        f'<div class="box"><h3>A log is a reflection tool, not a grade</h3>'
        f'<p>These pages help students notice what they do and what helps them. They are not scored. Please do not turn minutes into points: that rewards students who have more time, more space or an instrument at home.</p>'
        f'<p>If you need a record, note that a student completed a reflection, and compare each student only with their own goals.</p>'
        f'<p>Praise effort and choices, such as "You picked a smaller goal and kept going," and not the minute total.</p></div></div>'
        f'<div class="cols"><div class="box"><h3>Every student can take part</h3>'
        f'<p>Not every student practices at home or owns an instrument. Students may log <b>any way I made music</b>: {ways_text()}, whether at school, at home or at a relative\'s house. '
        f'Time in your own class counts too. A student with no music time one day writes a zero or leaves the cell empty, and that is fine.</p>'
        f'<p>Goals can be for any kind of music-making. See the non-instrument example on {pg("smart")}.</p></div>'
        f'<div class="box"><h3>Sharing with families</h3>'
        f'<p>Send home {pg("start")} and the log your class uses. A sentence you can paste into a note: "This tracker helps your child set a music goal and notice what helps. '
        f'Please ask what they worked on this week. There are no grades and no signatures."</p>'
        f'<p>Suggest the question "What did you work on?" instead of "Did you practice?"</p></div></div>'
        f'<h2>Adapting it for your room</h2>'
        f'<table><tr><th style="width:80pt">Group</th><th>Ideas for goals and log entries</th></tr>'
        f'<tr><td><b>Band</b></td><td>A passage, a scale or a rhythm from the music you are rehearsing; steady tone; a part for the concert.</td></tr>'
        f'<tr><td><b>Orchestra</b></td><td>Shifting, bow control, intonation on one string, a section of a piece; use the plan on {pg("plan")} for warm-ups.</td></tr>'
        f'<tr><td><b>Choir</b></td><td>Learn a part, memorize words, breath phrases, match pitch with a partner. Count singing and humming.</td></tr>'
        f'<tr><td><b>Piano, guitar, ukulele</b></td><td>Chords, left hand, a short piece from memory, a clean change between two chords.</td></tr>'
        f'<tr><td><b>General music</b></td><td>Rhythm patterns, listening journals, composing a short melody or beat, learning a song.</td></tr></table>'
        f'<p>The pages support the Performing process of preparing and refining music (MU:Pr5.1 in the National Core Arts Standards for Music). Match them to your own curriculum. '
        f'No songs, lyrics or copyrighted characters are used, and there are no answer keys.</p>'
        f'<p class="small">{DISCLOSURE}</p>')
    return page("teach", body, wm, tag="TEACHER", tagline="Read first", student=False)


def start_page(wm=False):
    steps = [("Choose", f"Pick a log: minutes ({pg('logA')}) or what I worked on ({pg('logB')}). You can use both."),
             ("Set goals", f"Write a big goal and three small goals ({pg('goal')}), then your music year goals ({pg('year')})."),
             ("Plan", f"Make a practice plan ({pg('plan')}). Read the tips on {pg('tips')}."),
             ("Log it", "Each day, write the minutes, what you worked on and circle how focused you felt."),
             ("Reflect", f"After days 7, 14, 21 and 28, fill in a weekly reflection ({pgs('w1', 'w4')}).")]
    st = "".join(f'<div style="display:flex;align-items:center;gap:8pt;margin:0 0 5pt"><span class="num b">{i + 1}</span><span style="font-size:10.8pt;line-height:1.28"><b>{a}.</b> {b}</span></div>' for i, (a, b) in enumerate(steps))
    plan_rows = [("Week 1", "Days 1–7", "Set goals and a plan. Start the log. Reflect on day 7.", f"{pgs('smart', 'plan')}, {pg('logA')} or {pg('logB')}, {pg('w1')}"),
                 ("Week 2", "Days 8–14", "Keep logging. Try one tip. Reflect on day 14.", f"{pg('tips')}, {pg('w2')}"),
                 ("Week 3", "Days 15–21", "Check your small goals. Make one smaller or bigger if needed. Reflect on day 21.", f"{pg('goal')}, {pg('w3')}"),
                 ("Week 4", "Days 22–28", "Finish strong. Reflect on day 28.", pg("w4")),
                 ("Bonus days", "Days 29–30", "Add up your minutes, color the chart and celebrate.", f"{pgs('totals', 'cert')}")]
    rows = "".join(f'<tr><td><b>{w}</b></td><td>{d}</td><td>{t}</td><td>{p_}</td></tr>' for w, d, t, p_ in plan_rows)
    body = (f'<div class="rb" style="gap:6pt">'
            f'<h2 style="margin:0">How to use this tracker</h2>{st}'
            f'<h2 style="margin-top:4pt">Your 4-week plan (30 days)</h2>'
            f'<table><tr><th style="width:62pt">Week</th><th style="width:62pt">Days</th><th>What to do</th><th style="width:128pt">Pages</th></tr>{rows}</table>'
            f'<div class="row" style="flex:none">'
            f'<div class="box" style="margin:0"><h3>Any way I made music counts</h3><p>You do not need an instrument or a quiet room. Count {ways_text()}. '
            f'Time you made music at school counts too.</p></div>'
            f'<div class="box" style="margin:0"><h3>This is not a grade</h3><p>A log helps you notice what you do and what helps you. Nobody scores it. '
            f'Be honest, and write a zero if you had no music time that day. That is useful information.</p></div></div>'
            f'<div class="wbox" style="flex:1"><div class="lab">My set-up</div><div class="grow">'
            f'<div style="font-size:10.6pt"><b>My log:</b> &nbsp;<i class="cb"></i>minutes ({pg("logA")}) &nbsp; <i class="cb"></i>what I worked on ({pg("logB")}) &nbsp; <i class="cb"></i>both</div>'
            f'<div style="display:flex;align-items:flex-end;gap:6pt;font-size:10.6pt"><span>My start date</span><span class="wl" style="flex:1;height:18pt"></span><span>My day 30 date</span><span class="wl" style="flex:1;height:18pt"></span></div>'
            f'<div style="display:flex;align-items:flex-end;gap:6pt;font-size:10.6pt"><span>My music time will be (when and where)</span><span class="wl" style="flex:1;height:18pt"></span></div></div></div></div>')
    return page("start", body, wm, tag="START HERE", tagline="How to use it")


def smart_page(wm=False):
    rows = "".join(
        f'<div data-smart="{l}" style="display:flex;gap:10pt;align-items:center;border:1.3pt solid #000;border-radius:7pt;padding:4pt 10pt;flex:1;min-height:0">'
        f'<span class="num" style="width:30pt;height:30pt;font-size:18pt">{l}</span><div style="flex:1"><div class="tt" style="font-size:13pt">{w}</div>'
        f'<div style="font-size:10.4pt;line-height:1.25"><b>{m}</b> Ask: {q}</div></div></div>' for l, w, m, q in SMART)
    ex = "".join(f'<tr><td style="width:24pt;text-align:center"><b>{l}</b></td><td>{t}</td></tr>' for l, t in EX_PARTS)
    body = (f'<div class="rb" style="gap:5pt"><p style="margin:0;font-size:10.6pt">A SMART goal is a goal with five parts. Use the five letters as a checklist for every goal you write.</p>{rows}'
            f'<div class="row" style="gap:10pt;flex:none">'
            f'<div class="box" style="margin:0"><h3>A fuzzy goal</h3><p><i>"{EX_FUZZY}"</i></p><p class="small">You cannot tell what to do or when you are done.</p>'
            f'<h3 style="margin-top:4pt">Another SMART goal</h3><p>{EX2}</p></div>'
            f'<div class="box" style="margin:0"><h3>A SMART goal</h3><p><i>"{EX_SMART}"</i></p></div></div>'
            f'<table class="ex" style="margin:0"><tr><th colspan="2">Find the five parts in the SMART goal above</th></tr>{ex}</table></div>')
    return page("smart", body, wm, tag="GOALS", tagline="SMART in five letters")


def goal_page(wm=False):
    small = "".join(
        f'<div class="wbox" data-small="{i}" style="flex:1"><div style="display:flex;align-items:center;gap:7pt"><span class="num b">{i}</span><span class="lab" style="margin:0">Small goal {i}</span>'
        f'<span style="margin-left:auto;font-size:9.2pt;color:#333">Tick each letter your goal has:&nbsp; '
        + "&nbsp; ".join(f'<b>{l}</b> <i class="cb" style="margin:0 0 0 1pt"></i>' for l, *_ in SMART) + '</span></div>'
        f'<div class="grow"><div class="wl"></div><div class="wl"></div>'
        f'<div style="display:flex;align-items:flex-end;gap:6pt;font-size:10pt"><span>How I will know (what I can count or check)</span><span class="wl" style="flex:1;height:18pt"></span></div>'
        f'<div style="display:flex;align-items:flex-end;gap:6pt;font-size:10pt"><span>I will be done by</span><span class="wl" style="flex:1;height:18pt"></span></div></div></div>' for i in (1, 2, 3))
    body = (f'<div class="rb" style="gap:6pt">'
            f'<div class="wbox" data-big="1" style="flex:none"><div class="lab">My big goal</div><div class="hint">Something I want to do in music by the end of this tracker or later in the year.</div>'
            f'{wl(2)}<div style="display:flex;align-items:flex-end;gap:6pt;font-size:10pt"><span>Why it matters to me</span><span class="wl" style="flex:1;height:18pt"></span></div>{wl(1, 18)}</div>'
            f'<div style="text-align:center;font-family:Oswald;font-weight:500;letter-spacing:.06em;font-size:11pt;text-transform:uppercase">Break it into three small steps. Each small goal should be SMART.</div>'
            f'{small}'
            f'<div style="display:flex;align-items:flex-end;gap:6pt;font-size:10pt"><span>People who can help me (teacher, family, friend)</span><span class="wl" style="flex:1;height:18pt"></span></div></div>')
    return page("goal", body, wm, tag="GOALS", tagline="One big goal, three small ones")


def year_page(wm=False):
    boxes = "".join(
        f'<div class="wbox" data-cat="{n}" style="flex:1"><div style="display:flex;align-items:baseline;gap:8pt"><span class="pill{" b" if i == 1 else ""}">{i + 1}</span><span class="lab" style="margin:0">{n}</span>'
        f'<span style="font-size:10pt;font-weight:600">{d}</span></div><div class="hint" style="margin-top:2pt"><i>Ideas: {ex}.</i></div>'
        f'<div class="grow"><div style="display:flex;align-items:flex-end;gap:6pt;font-size:10pt"><span>My goal</span><span class="wl" style="flex:1;height:18pt"></span></div><div class="wl"></div>'
        f'<div style="display:flex;align-items:flex-end;gap:6pt;font-size:10pt"><span>My first step</span><span class="wl" style="flex:1;height:18pt"></span></div>'
        f'<div style="display:flex;align-items:flex-end;gap:6pt;font-size:10pt"><span>I will check in on</span><span class="wl" style="flex:1;height:18pt"></span></div></div></div>'
        for i, (n, d, ex) in enumerate(CATS))
    body = (f'<div class="rb" style="gap:7pt"><p style="margin:0;font-size:10.6pt">Think about the whole school year. Write one goal for each kind of music goal. '
            f'You do not have to work on all three at once: use the 4-week tracker for one small goal at a time ({pg("goal")}).</p>{boxes}'
            f'<div style="display:flex;align-items:flex-end;gap:6pt;font-size:10pt"><span>My word for this music year</span><span class="wl" style="flex:1;height:18pt"></span></div></div>')
    return page("year", body, wm, tag="GOALS", tagline="Three kinds of goals")


def plan_page(wm=False):
    mins = dict(PLANS)[EXAMPLE_TOTAL]
    ex_eq = " + ".join(str(m) for m in mins) + f" = {EXAMPLE_TOTAL}"
    trs = "".join(
        f'<tr data-total="{t}"><td><b>{t} minutes</b></td>' + "".join(f"<td>{m}</td>" for m in ms) + f'<td class="eq">{" + ".join(str(m) for m in ms)} = {t}</td></tr>' for t, ms in PLANS)
    desc = "".join(f'<tr><td style="width:84pt"><b>{n}</b></td><td>{d}</td></tr>' for n, d in PARTS)
    mine = "".join(f'<tr data-part="{n}"><td style="width:84pt"><b>{n}</b></td><td style="width:54pt"></td><td style="height:25pt"></td></tr>' for n, _ in PARTS)
    noi = "".join(f'<li><b>{n}:</b> {t}.</li>' for n, t in NO_INSTRUMENT)
    body = (f'<div class="rb" style="gap:5pt">'
            f'<h2 style="margin:0">A {EXAMPLE_TOTAL}-minute plan: {ex_eq}</h2>{plan_bar_svg(EXAMPLE_TOTAL, mins)}'
            f'<table style="margin:0">{desc}</table>'
            f'<h2 style="margin:2pt 0 0">Pick a total and split it</h2>'
            f'<table class="pt" style="margin:0"><tr><th>Total</th>' + "".join(f"<th>{n}</th>" for n, _ in PARTS) + f'<th style="width:112pt">Adds up to</th></tr>{trs}</table>'
            f'<p class="small" style="margin:0">Each plan puts about half the time on new material. Change the split to fit your goals.</p>'
            f'<h2 style="margin:2pt 0 0">My plan</h2>'
            f'<table style="margin:0" data-myplan="1"><tr><th>Part</th><th style="width:54pt">Minutes</th><th>What I will work on</th></tr>{mine}'
            f'<tr><td colspan="3" style="text-align:right;height:22pt"><b>My total: ___ + ___ + ___ + ___ = ___ minutes</b></td></tr></table>'
            f'<div class="box" style="margin:0"><h3>No instrument at home? Make a music plan anyway</h3><ul style="columns:2;column-gap:14pt;margin:0">{noi}</ul></div></div>')
    return page("plan", body, wm, tag="PLAN", tagline="Warm-up, new, review, fun")


def tips_page(wm=False):
    cards = "".join(
        f'<div class="wbox" data-tip="{i + 1}" style="flex:1"><div style="display:flex;gap:6pt;align-items:flex-start"><span class="num">{i + 1}</span><div class="tt" style="font-size:11.5pt;line-height:1.12;padding-top:1pt">{t}</div></div>'
        f'<p style="font-size:9.8pt;line-height:1.28;margin:3pt 0 2pt">{d}</p><div style="margin-top:auto;font-size:9.6pt"><i class="cb"></i>I will try this</div></div>'
        for i, (t, d) in enumerate(TIPS))
    pairs = "".join(f'<div class="row" style="flex:1;min-height:0">{cards_}</div>' for cards_ in [""]) if False else ""
    grid = "".join(f'<div class="row" style="flex:1;min-height:0">' + "".join(
        f'<div class="wbox" data-tip="{j + 1}" style="flex:1"><div style="display:flex;gap:6pt;align-items:flex-start"><span class="num">{j + 1}</span><div class="tt" style="font-size:11.5pt;line-height:1.12;padding-top:1pt">{TIPS[j][0]}</div></div>'
        f'<p style="font-size:9.8pt;line-height:1.28;margin:3pt 0 2pt">{TIPS[j][1]}</p><div style="margin-top:auto;font-size:9.6pt"><div style="display:flex;align-items:flex-end;gap:5pt;margin-bottom:6pt"><span>I tried it when</span><span class="wl" style="flex:1;height:16pt"></span></div><i class="cb"></i>I will try this</div></div>' for j in (r * 2, r * 2 + 1))
        + '</div>' for r in range(4))
    body = (f'<div class="rb" style="gap:6pt"><p style="margin:0;font-size:10.4pt">These are ideas, not rules. Different tips work for different people. Try one or two, and use your weekly reflection to see what helps.</p>{grid}'
            f'<div class="box" style="margin:0"><h3>Music time can look many ways</h3><p>If you cannot play today, you can still sing or hum, tap a rhythm on a table, listen closely to a piece and notice one thing, or write a few measures of your own music.</p></div></div>')
    return page("tips", body, wm, tag="TIPS", tagline="8 ideas to try")


def cell_html(d, version):
    fo = f'<div class="fo"><span>focus</span><span class="fcs">{"".join(fc(n) for n, _ in FOCUS)}</span></div>'
    head = f'<div class="dn"><small>DAY</small>{d}</div>'
    if version == "A":
        mid = ('<div class="mw"><span class="ln"></span>min</div>'
               '<div class="ww"><small>what I practiced</small><span class="ln"></span></div>')
    else:
        mid = ('<div class="wr"><small style="font-size:7.4pt;color:#444;line-height:1">what I worked on</small><span class="ln"></span><span class="ln"></span><span class="ln"></span></div>'
               '<div class="mw" style="margin:0 0 3pt"><span style="font-size:8pt">min</span><span class="ln" style="height:12pt"></span></div>')
    return f'<div class="cell" data-day="{d}">{head}{mid}{fo}</div>'


def log_page(key, wm=False):
    v = "A" if key == "logA" else "B"
    rows = []
    for i, (a, b) in enumerate(WEEKS):
        rows.append(f'<div class="wkl">Week {i + 1}<span>days {a}–{b}</span></div><div class="lrow" data-week="{i + 1}">{"".join(cell_html(d, v) for d in range(a, b + 1))}</div>')
    if v == "A":
        note = (f'<div class="bnote"><div><b>Month total:</b> add up the minutes on {pg("totals")}.</div>'
                f'<div style="margin-top:3pt">Total minutes for the month: <span class="ln" style="display:inline-block;width:80pt"></span></div></div>')
    else:
        note = (f'<div class="bnote"><div><b>My favorite thing I worked on this month:</b></div><div class="ln"></div><div class="ln"></div></div>')
    rows.append(f'<div class="wkl">Bonus days<span>days {BONUS[0]}–{BONUS[1]}</span></div><div class="lrow" data-week="5">{"".join(cell_html(d, v) for d in range(BONUS[0], BONUS[1] + 1))}{note}</div>')
    focus = "; ".join(f"{n} = {t}" for n, t in FOCUS)
    if v == "A":
        leg = (f'<div class="leg"><b>How to fill it in:</b> each day write the minutes you made music and a few words about what you practiced. Circle a focus number: {focus}. '
               f'Count <b>any way I made music</b>: {ways_text()}. A zero is okay. This log is not a grade.</div>')
    else:
        leg = (f'<div class="leg"><b>How to fill it in:</b> each day write what you worked on (a passage, a skill, a song, a listening idea), then the minutes. Circle a focus number: {focus}. '
               f'Count <b>any way I made music</b>: {ways_text()}. A zero is okay. This log is not a grade.</div>')
    body = leg + f'<div class="lgrid">{"".join(rows)}</div>'
    return page(key, body, wm, tag="30-DAY LOG", tagline="Minutes" if v == "A" else "What I worked on")


def wk_page(n, wm=False):
    a, b = WEEKS[n - 1]
    name, prompt = WEEK_PROMPTS[n - 1]
    stat = (f'<div class="row" style="flex:none;gap:10pt;font-size:10.4pt">'
            f'<div class="wbox" style="flex:1;padding:4pt 9pt;flex-direction:row;align-items:flex-end;gap:6pt"><span>Days I made music</span><span class="wl" style="flex:1;height:17pt"></span><span>of 7</span></div>'
            f'<div class="wbox" style="flex:1.25;padding:4pt 9pt;flex-direction:row;align-items:flex-end;gap:6pt"><span>My minutes this week ({pg("totals")})</span><span class="wl" style="flex:1;height:17pt"></span></div></div>')
    boxes = "".join(
        f'<div class="wbox" data-box="{k}" style="flex:1"><div class="lab">{t}</div><div class="hint">{h}</div><div class="grow">{wl(4)}</div></div>'
        for k, t, h in (("well", "What went well", "A moment, a skill or a habit I feel good about."),
                        ("hard", "What was hard", "What got in the way, or what felt tricky?"),
                        ("next", "My next step", "One small thing I will do next week.")))
    goals = "".join(f'<tr><td style="width:72pt"><b>Small goal {i}</b></td><td></td><td style="width:200pt;font-size:9.4pt;white-space:nowrap"><i class="cb"></i>not yet &nbsp;<i class="cb"></i>getting there &nbsp;<i class="cb"></i>got it</td></tr>' for i in (1, 2, 3))
    body = (f'<div class="rb" style="gap:6pt">'
            f'<div style="font-family:Oswald;font-size:12pt;letter-spacing:.03em" data-week-days="{a}-{b}"><b>WEEK {n}</b> <span style="font-weight:300">· days {a}–{b} · {name}</span></div>{stat}'
            f'<div class="box" style="margin:0"><h3>Think about it</h3><p>{prompt}</p></div>{boxes}'
            f'<table class="gt" style="margin:0"><tr><th colspan="3">How are my small goals ({pg("goal")})?</th></tr>{goals}</table></div>')
    return page(f"w{n}", body, wm, tag=f"WEEK {n}", tagline=f"Days {a}–{b}")


def totals_page(wm=False):
    rows = []
    for i, (a, b) in enumerate(WEEKS):
        boxes = "".join(f'<div class="tb" data-day="{d}">{d}</div>' for d in range(a, b + 1))
        rows.append(f'<div class="fml">Week {i + 1} total = Day {a} + Day {a + 1} + … + Day {b}</div>'
                    f'<div class="trow" data-week="{i + 1}"><div class="wk">Week {i + 1}<small>days {a}–{b}</small></div>{boxes}<div class="tot">= <span class="ln"></span></div></div>')
    a, b = BONUS
    boxes = "".join(f'<div class="tb" data-day="{d}">{d}</div>' for d in range(a, b + 1))
    rows.append(f'<div class="fml">Days {a}–{b} total = Day {a} + Day {b}</div>'
                f'<div class="trow" data-week="5"><div class="wk">Bonus<small>days {a}–{b}</small></div>{boxes}<div style="flex:1"></div><div class="tot" style="flex:0 0 88pt">= <span class="ln"></span></div></div>')
    body = (f'<p style="margin:7pt 0 0;font-size:10.2pt">Copy the minutes from your log ({pg("logA")} or {pg("logB")}) into the day boxes. Add each row. Then add the rows to find your month total.</p>'
            f'<div class="rb" style="gap:0;padding-top:2pt">{"".join(rows)}'
            f'<div class="box" style="margin:8pt 0 0"><h3>Month total</h3>'
            f'<p style="font-size:11pt !important"><b>Month total = Week 1 + Week 2 + Week 3 + Week 4 + Days 29–30</b></p>'
            f'<p style="font-size:11pt !important">___ + ___ + ___ + ___ + ___ = <b>_______ minutes</b></p></div>'
            f'<div class="row" style="gap:10pt;margin-top:6pt"><div class="box" style="margin:0"><h3>Days I made music</h3><p>I made music on ____ of 30 days.</p></div>'
            f'<div class="box" style="margin:0"><h3>Average on my music days</h3><p>Month total ÷ days I made music = ____ minutes. Round to the nearest whole minute. Skip this if you made music on 0 days.</p></div></div></div>')
    return page("totals", body, wm, tag="TOTALS", tagline="Add it up")


def chart_page(wm=False):
    day = grid_svg("day", 30, 12, 22, 19, 5)
    wkc = grid_svg("week", 4, 14, 62, 17, 30, left=40)
    body = (f'<div class="rb" style="gap:4pt;padding-top:6pt">'
            f'<h2 style="margin:0">My 30 days</h2>'
            f'<p style="margin:0;font-size:10pt">For each day, color the cells from the bottom up. <b>One cell is 5 minutes.</b> Round to the nearest 5 minutes. If you did more than 60 minutes, color the whole column.</p>'
            f'<div data-chart="day" style="width:100%">{day}</div>'
            f'<div style="text-align:center;font-family:Oswald;font-size:9.5pt;letter-spacing:.06em;text-transform:uppercase;margin-top:-2pt">Day of the tracker</div>'
            f'<h2 style="margin:2pt 0 0">My 4 weeks</h2>'
            f'<div class="row" style="align-items:center;gap:14pt"><div data-chart="week" style="flex:0 0 3.9in">{wkc}</div>'
            f'<div class="box" style="margin:0;flex:1"><h3>Color the weekly bars</h3><p>Use your week totals from {pg("totals")}. <b>One cell is 30 minutes.</b> Color the cells from the bottom up to the nearest 30 minutes.</p>'
            f'<p>Week 1 minutes: ____<br>Week 2 minutes: ____<br>Week 3 minutes: ____<br>Week 4 minutes: ____</p></div></div></div>')
    return page("chart", body, wm, tag="PROGRESS", tagline="Color it in")


def cert_page(wm=False):
    body = (f'<div class="certf" data-cert="1">{badge_svg()}<h1>Music Goals Certificate</h1><div class="sub">for setting a goal, making music and reflecting</div>'
            f'<div style="font-size:12pt">This certificate is proudly given to</div>'
            f'<div style="flex:1;width:100%;display:flex;flex-direction:column;justify-content:space-evenly;min-height:0">'
            f'<div class="fl"><span class="ln" style="height:24pt"></span></div>'
            f'<div style="font-size:11.5pt;text-align:center">for making music on <b>____</b> of 30 days and keeping a music tracker for 4 weeks.</div>'
            f'<div class="fl"><span class="k">My big goal was</span><span class="ln"></span></div><div class="fl"><span class="ln"></span></div>'
            f'<div class="fl"><span class="k">What I learned about how I make music best</span><span class="ln"></span></div><div class="fl"><span class="ln"></span></div>'
            f'<div class="fl"><span class="k">Total minutes</span><span class="ln" style="max-width:110pt"></span><span class="k">The thing I am proudest of</span><span class="ln"></span></div>'
            f'<div class="fl"><span class="ln"></span></div></div>'
            f'<div class="three"><div class="fl"><span class="ln"></span></div><div class="fl"><span class="ln"></span></div></div>'
            f'<div class="three" style="font-size:9.4pt;color:#333"><div style="text-align:center">Teacher or family signature</div><div style="text-align:center">Date</div></div></div>')
    return page("cert", body, wm, tag="CELEBRATE", tagline="Hand it out", student=False)


def terms_page(wm=False):
    body = (f'{doc_head("Terms of Use", "Thank you for your purchase!")}'
            f'<p>© {YEAR} {STORE}. {BRAND} by {STORE}. All rights reserved. This purchase gives <b>one teacher</b> a license to use this resource with their own students.</p>'
            f'<h2>You may</h2><ul><li>Print and copy pages for your own classroom and students.</li>'
            f'<li>Share pages with your own students through a password-protected class site or learning platform.</li>'
            f'<li>Use the pages with your own students when you have a substitute teacher.</li></ul>'
            f'<h2>You may not</h2><ul><li>Share, email or copy this resource for other teachers, a whole school or a district. Additional licenses are available on Teachers Pay Teachers.</li>'
            f'<li>Post any part of it on a public website, shared drive or social media.</li>'
            f'<li>Sell, give away or claim any part of it as your own, or edit it into a new product.</li></ul>'
            f'<h2>Questions?</h2><p>Please use the Q&amp;A tab on the {BRAND} by {STORE} store on Teachers Pay Teachers. If something looks wrong, let me know there and I will fix it.</p>'
            f'<h2>Credits</h2><ul>'
            f'<li>The goal pages, logs, reflections, plans, charts and certificate are original work, {BRAND} by {STORE}.</li>'
            f'<li>The cover illustration is made with AI tools. The pages, grids, charts and text are drawn in code.</li>'
            f'<li>Text fonts: Oswald (The Oswald Project Authors) and Source Sans 3 (Adobe), SIL Open Font License 1.1.</li></ul>'
            f'<h2>Printing tips</h2><ul><li>All pages print clearly in black and white. Print the logs and the chart single-sided so students can see every day at once.</li>'
            f'<li>Copy the log students will use ({pg("logA")} or {pg("logB")}) and one weekly reflection for each of the 4 weeks ({pgs("w1", "w4")}).</li></ul>'
            f'<h2>What is in this file ({TOTAL_PAGES} pages)</h2><p>Page 1 cover, page {P["teach"]} teacher notes, page {P["start"]} start here, page {P["smart"]} SMART goals guide, '
            f'page {P["goal"]} big goal, page {P["year"]} my music year, page {P["plan"]} practice plan, page {P["tips"]} practice tips, '
            f'pages {P["logA"]}–{P["logB"]} 30-day logs, pages {P["w1"]}–{P["w4"]} weekly reflections, page {P["totals"]} totals, page {P["chart"]} progress chart, '
            f'page {P["cert"]} certificate and page {P["terms"]} these terms.</p>'
            f'<h2>Thank you and please rate this resource</h2><p>If this tracker helped your students, please leave a rating on TpT. It helps other teachers find it, and you earn TpT credits for feedback. '
            f'Follow the {BRAND} store for new music resources every week.</p>'
            f'<p class="small">{DISCLOSURE}</p>')
    return page("terms", body, wm, tag="TERMS", tagline="Please read", student=False)


FUNCS = {"teach": teach_page, "start": start_page, "smart": smart_page, "goal": goal_page, "year": year_page, "plan": plan_page, "tips": tips_page,
         "logA": lambda w: log_page("logA", w), "logB": lambda w: log_page("logB", w), "w1": lambda w: wk_page(1, w), "w2": lambda w: wk_page(2, w),
         "w3": lambda w: wk_page(3, w), "w4": lambda w: wk_page(4, w), "totals": totals_page, "chart": chart_page, "cert": cert_page, "terms": terms_page}


def make_page(key, wm=False):
    return cover_page() if key == "cover" else FUNCS[key](wm)


def full_pages():
    out = [make_page(k) for k in ORDER]
    assert len(out) == TOTAL_PAGES
    return out


PREVIEW_KEYS = ["goal", "logA", "w1", "chart"]


def preview_pages():
    return [make_page(k, True) for k in PREVIEW_KEYS]

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
.gtl { display: flex; flex-direction: column; align-items: center; width: 190px; }
.gtl svg { width: 150px; height: 150px; display: block; }
.gtl b { font-family: Oswald; font-weight: 700; text-transform: uppercase; font-size: 26px; margin-top: 8px; }
.gtl span { font-family: Oswald; font-weight: 300; font-size: 19px; text-align: center; }
.tg { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px 16px; width: 880px; }
.tg .tc { border: 2px solid #000; border-radius: 10px; padding: 8px 14px 9px; font-family: Oswald; font-weight: 700; font-size: 26px; text-transform: uppercase; line-height: 1.1; display: flex; align-items: center; gap: 12px; }
.tg .tc small { font-weight: 500; font-size: 17px; letter-spacing: .1em; color: ACCENT; width: 40px; flex: none; }
.tg .tc span { font-weight: 300; text-transform: none; font-size: 17px; display: block; letter-spacing: 0; }
""".replace("ACCENT", ACCENT)


def sq_doc(body):
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{font_css()}html,body{{margin:0;background:#fff;font-family:"Source Sans 3",sans-serif}}{SQ_CSS}</style></head><body>'
            f'{body}</body></html>')


def swm_over(size=230):
    return f'<div class="swm" style="font-size:{size}px">PREVIEW</div>'


def shot(src, w):
    return f'<div class="shot" style="width:{w}px"><img src="{src}"></div>'


def pill_row(items):
    return '<div style="display:flex;gap:18px">' + "".join(f'<div class="pill">{t}</div>' for t in items) + "</div>"


def trio(imgs, caps, w=290):
    return "".join(
        f'<div style="width:{w}px;display:flex;flex-direction:column;align-items:center">{shot(imgs[i], w)}'
        f'<div class="lbl" style="font-size:22px;margin-top:20px">{caps[i][0]}</div>'
        f'<div style="font-family:Oswald;font-weight:300;font-size:20px;line-height:1.25;text-align:center;margin-top:8px;width:{w - 20}px">{caps[i][1]}</div></div>'
        for i in range(len(imgs)))


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



SQ_EXTRA = """
.tg { grid-template-columns: repeat(2, 1fr); }
.tg .tc { padding: 26px 16px 27px !important; font-size: 31px !important; gap: 8px !important; }
.tg .tc small { width: 104px !important; font-size: 26px !important; }
"""


def sq_doc(body):
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{font_css()}html,body{{margin:0;background:#fff;font-family:"Source Sans 3",sans-serif}}{SQ_CSS}{SQ_EXTRA}</style></head><body>'
            f'{body}</body></html>')


def swm_over(size=230):
    return f'<div class="swm" style="font-size:{size}px">PREVIEW</div>'


def shot(src, w):
    return f'<div class="shot" style="width:{w}px"><img src="{src}"></div>'


def pill_row(items):
    return '<div style="display:flex;gap:18px">' + "".join(f'<div class="pill">{t}</div>' for t in items) + "</div>"


def cover_square():
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div>'
        f'<div style="flex:1;display:flex;flex-direction:column;justify-content:space-evenly;align-items:center;width:100%;padding:0 0 76px">'
        f'<div style="height:440px;display:flex;align-items:center"><img src="../art/hero.png" alt="" style="display:block;height:460px;width:auto"></div>'
        f'<div><div class="hd" style="font-size:66px">Music Goals and</div><div class="hd" style="font-size:112px">Practice Tracker</div>'
        f'<div class="sub" style="font-size:27px;margin-top:12px">30-day practice logs, goal setting and reflection pages</div></div>'
        f'</div><div class="band">Grades 5–8 <em>·</em> 2 thirty-day logs <em>·</em> {TOTAL_PAGES} pages</div></div>')


def preview_square_1(img):
    caps = [(PAGE_NAMES["goal"], "One big goal, three SMART small goals"), (PAGE_NAMES["logA"], "30 numbered days with minutes and focus"), (PAGE_NAMES["w1"], "What went well, what was hard, next step")]
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div><div class="hd" style="font-size:70px;margin-top:28px">Set it, log it, reflect</div>'
        f'<div class="sub" style="font-size:28px;margin-top:10px">For any instrument or voice, grades 5–8</div>'
        f'<div style="flex:1;display:flex;flex-direction:column;align-items:center;justify-content:space-evenly;padding-bottom:70px">'
        f'<div style="display:flex;gap:22px;align-items:flex-start">{trio(img, caps)}</div>{pill_row(["Goals", "30-day logs", "Reflection"])}</div>'
        f'{swm_over(230)}<div class="band">Not a grade <em>·</em> any way I made music counts</div></div>')


def preview_square_2(a, b):
    pair = "".join(f'<div style="width:380px">{shot(src, 380)}<div class="lbl">{lab}<span>{sub}</span></div></div>'
                   for src, lab, sub in ((a, PAGE_NAMES["plan"], "Warm-up, new, review and fun, with minutes that add up"),
                                         (b, PAGE_NAMES["chart"], "Color a 30-day bar chart and 4 weekly bars")))
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div><div class="hd" style="font-size:70px;margin-top:24px">Plan it, then chart it</div>'
        f'<div class="sub" style="font-size:27px;margin-top:8px">Plans that add up and charts you color in</div>'
        f'<div style="flex:1;display:flex;align-items:center;padding-bottom:70px"><div style="display:flex;gap:44px;align-items:flex-start">{pair}</div></div>'
        f'{swm_over(230)}<div class="band">Practice plan <em>·</em> totals <em>·</em> progress chart</div></div>')


CONTENTS = [(f"{P['start']}", "Start here and pacing plan"), (f"{P['smart']}", "SMART goals guide"), (f"{P['goal']}–{P['year']}", "Big goal and music year goals"),
            (f"{P['plan']}–{P['tips']}", "Practice plan and tips"), (f"{P['logA']}–{P['logB']}", "Two 30-day logs"), (f"{P['w1']}–{P['w4']}", "4 weekly reflections"),
            (f"{P['totals']}–{P['chart']}", "Totals and progress chart"), (f"{P['cert']}", "Celebration certificate")]


def preview_square_3():
    chips = "".join(f'<div class="tc"><small>{n}</small><div>{escape(t)}</div></div>' for n, t in CONTENTS)
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div><div class="hd" style="font-size:72px;margin-top:28px">Everything inside</div>'
        f'<div class="sub" style="font-size:27px;margin-top:10px">{TOTAL_PAGES} printable pages with teacher notes</div>'
        f'<div style="flex:1;display:flex;flex-direction:column;align-items:center;justify-content:space-evenly;padding-bottom:70px">'
        f'<div class="tg" style="gap:22px 16px">{chips}</div>'
        f'{pill_row(["Teacher notes", "No prep", "Print and go"])}</div>'
        f'{swm_over(230)}<div class="band">Goals <em>·</em> logs <em>·</em> reflection <em>·</em> certificate</div></div>')


# ================================================================== render / build
PAGE_LIST = [("Cover", 1), ("Teacher notes", 1), ("Start here with the 4-week plan", 1), ("SMART goals guide", 1), ("Goal pages: big goal and my music year", 2),
             ("Practice plan and practice tips", 2), ("30-day logs: minutes and what I worked on", 2), ("Weekly reflections, 4 weeks", 4),
             ("Practice minutes totals and progress chart", 2), ("Celebration certificate", 1), ("Terms of use and credits", 1)]
assert sum(c for _, c in PAGE_LIST) == TOTAL_PAGES, sum(c for _, c in PAGE_LIST)


def upload_md():
    lst = "\n".join(f"- {n}: {c}" for n, c in PAGE_LIST)
    return f"""# UPLOAD: {LISTING_TITLE} (TpT 094)

These fields follow the order of TpT's "Add a resource" form. Strongest in January (goal setting) but works all year: the title has no seasonal word.

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
Ready to help students set a music goal and keep track of it? This printable goal-setting and practice-tracking pack gives grades 5-8 a clear way to pick a goal, break it into small steps, log 30 days of music-making and reflect each week. It works for band, orchestra, choir, piano, guitar and general music because the wording is the same for every instrument and for voice. It is a great fresh start for January, a new semester or any time of year.

WHAT'S INCLUDED ({TOTAL_PAGES} pages, PDF, US Letter)
• Cover (1 page)
• Teacher notes: how to use it in class, grading-free use, sharing with families and ideas for band, orchestra, choir, piano, guitar and general music (1 page)
• Start here with a 4-week pacing plan (1 page)
• SMART goals guide in kid-friendly language: Specific, Measurable, Achievable, Relevant, Time-bound, with an example and a non-instrument example (1 page)
• Goal pages: a big goal broken into three small goals, and a my music year page with skill, performance, and listening and creating goals (2 pages)
• Practice plan template with warm-up, new material, review and fun, with minute splits that add up (10, 15, 20 and 30 minutes), plus practice tips (2 pages)
• 30-day practice logs, two versions: a minutes log and a what I worked on log, each with 30 numbered days, minutes, what I practiced and a focus circle (2 pages)
• Weekly reflections for weeks 1 to 4: what went well, what was hard, my next step (4 pages)
• Practice minutes totals with the formulas shown, and a progress chart to color in with a 30-day bar chart and 4 weekly bars (2 pages)
• Celebration certificate (1 page)
• Terms of use and credits (1 page)
Total: {TOTAL_PAGES} pages.

INCLUSIVE BY DESIGN
Not every student practices at home or owns an instrument. Students can count any way they made music: playing, singing, tapping or clapping, listening closely or composing. The pages say clearly that a log is a reflection tool, not a grade, and the teacher notes suggest ways to use it without grading.

HOW TO USE
Launch the goal pages in one class period, then students fill in a 30-day log a little each day and complete a weekly reflection after days 7, 14, 21 and 28. On days 29 and 30 they add up their minutes, color the chart and celebrate with the certificate. Copy only the pages you need.

• Grades 5-8
• No prep: print and go, black and white friendly
• No songs, lyrics or copyrighted characters

{DISCLOSURE}

Please leave a rating: you earn TpT credits for feedback, and it helps other teachers find this.
Follow the Hudson Beat store for new music resources every week.
```

## 3. Grades

5th, 6th, 7th and 8th grade.

## 4. Subjects and tags

- Subjects: {", ".join(SUBJECTS)}
- Tags: {", ".join(TAGS)}

(January and "New Year" appear only in the description's first paragraph and in the tag list, never in the title or on the cover.)

## 5. Page count by section (totals {TOTAL_PAGES})

{lst}
- Total: {TOTAL_PAGES}

## 6. Standards

The teacher notes name the Performing process of preparing and refining music (MU:Pr5.1, National Core Arts Standards for Music) in general terms and ask teachers to match it to their own curriculum.

## 7. Price

**${PRICE}** (paid; queue price).

## 8. Preview

Paid. Preview PDF: big goal and small goals (page {P["goal"]}), 30-day log: minutes (page {P["logA"]}), weekly reflection 1 (page {P["w1"]}) and progress chart (page {P["chart"]}), all watermarked.

## 9. Before you click publish

- Title has no seasonal words; "New Year" is only a tag, and January is only in the description.
- No answer keys: every page is a student page or a teacher page. There is no music notation.
- Art: the cover illustration is made with AI tools (the disclosure line covers it); the grids, charts, certificate badge and text are drawn in code.
- Not repeated from the Practice Log and Practice Bingo pack (TpT 049): this pack is about goals, reflection, plans and charts, with 30-day logs in two new layouts.
- Open owner question: logo beside HUDSON BEAT (see tpt/STYLE.md).
"""


def tpt_json():
    return {"price": PRICE, "license_price": PRICE, "tax_code": "Other Digital Goods - No Physical Media", "grades": GRADES, "subjects": SUBJECTS, "tags": TAGS,
            "formats": ["PDF"], "pages": TOTAL_PAGES, "answer_key": "Not Included",
            "files": {"product": f"{SLUG}.pdf", "preview": f"{SLUG}-PREVIEW.pdf", "thumb1": "cover.png", "thumb2": "preview-1.png", "thumb3": "preview-2.png", "thumb4": "preview-3.png"}}


SHOT_KEYS = ["goal", "logA", "w1", "plan", "chart"]


def build():
    os.makedirs(BUILD, exist_ok=True)
    full = write("resource.html", html_doc(full_pages(), TITLE))
    prev = write("preview.html", html_doc(preview_pages(), "Preview"))
    render([{"html": full, "pdf": PDF}, {"html": prev, "pdf": PREVIEW_PDF}])
    for k in SHOT_KEYS:
        subprocess.run(["pdftoppm", "-png", "-r", "150", "-f", str(P[k]), "-l", str(P[k]), "-singlefile", PDF, os.path.join(BUILD, f"pg-{k}")], check=True)
    sq = [write("cover.html", cover_square()),
          write("p1.html", preview_square_1(["pg-goal.png", "pg-logA.png", "pg-w1.png"])),
          write("p2.html", preview_square_2("pg-plan.png", "pg-chart.png")),
          write("p3.html", preview_square_3())]
    render([{"html": h, "png": o, "width": 1000, "height": 1000, "scale": 2} for h, o in zip(sq, [COVER_PNG] + PREVIEW_PNGS)])
    with open(UPLOAD, "w") as fh:
        fh.write(upload_md())
    with open(TPT_JSON, "w") as fh:
        json.dump(tpt_json(), fh, indent=2)
        fh.write("\n")
    print(f"built {PDF}, {PREVIEW_PDF}, cover + 3 previews, UPLOAD.md, tpt.json")


if __name__ == "__main__" and "--check" not in sys.argv:
    build()



# ================================================================== checks
# Everything below is typed separately from the drawing code above: it reads the rendered HTML/SVG back and recomputes.
import lxml.html as LH  # noqa: E402

T_WEEKS = [(1, 7), (8, 14), (15, 21), (22, 28)]
T_PLAN_PARTS = ["Warm-up", "New material", "Review", "Fun"]
T_PLANS = {10: [2, 5, 2, 1], 15: [3, 7, 3, 2], 20: [3, 10, 4, 3], 30: [5, 15, 6, 4]}
T_SMART = [("S", "Specific"), ("M", "Measurable"), ("A", "Achievable"), ("R", "Relevant"), ("T", "Time-bound")]
T_CATS = ["Skill", "Performance", "Listening and creating"]
T_REFS = {"minutes": 9, "what I worked on": 10}   # phrase -> expected page, checked below with typed numbers
T_PAGE = {"teach": 2, "start": 3, "smart": 4, "goal": 5, "year": 6, "plan": 7, "tips": 8, "logA": 9, "logB": 10, "w1": 11, "w2": 12, "w3": 13, "w4": 14,
          "totals": 15, "chart": 16, "cert": 17, "terms": 18}


def fl(el, k, d=0.0):
    return float(el.get(k, d))


def check_svg_extent(sv, label, errs):
    vb = [float(x) for x in sv.get("viewbox").split()]
    W_, H_ = vb[2], vb[3]
    for el in sv.iter():
        sw = fl(el, "stroke-width") if el.get("stroke") not in (None, "none") else 0.0
        tag = el.tag
        if tag == "rect":
            xs, ys = [fl(el, "x"), fl(el, "x") + fl(el, "width")], [fl(el, "y"), fl(el, "y") + fl(el, "height")]
        elif tag == "circle":
            r = fl(el, "r")
            xs, ys = [fl(el, "cx") - r, fl(el, "cx") + r], [fl(el, "cy") - r, fl(el, "cy") + r]
        elif tag == "polygon":
            v = [float(x) for x in re.findall(r"-?\d+(?:\.\d+)?", el.get("points"))]
            xs, ys = v[0::2], v[1::2]
        elif tag == "text":
            x, y, fs = fl(el, "x"), fl(el, "y"), fl(el, "font-size")
            if x < 0 or x > W_ or y - fs < 0 or y + fs * 0.25 > H_:
                errs.append(f"{label}: a text label is outside the viewBox")
            continue
        else:
            continue
        pad = max(sw, 2.0)
        if min(xs) - sw / 2 < pad - 1e-6 or min(ys) - sw / 2 < pad - 1e-6 or max(xs) + sw / 2 > W_ - pad + 1e-6 or max(ys) + sw / 2 > H_ - pad + 1e-6:
            errs.append(f"{label}: a {tag} (stroke {sw}) is closer than max(stroke, 2) to the viewBox edge")


def verify_html():
    errs = []
    doc = LH.fromstring(open(os.path.join(BUILD, "resource.html"), encoding="utf-8").read())
    pages = {p.get("data-k"): p for p in doc.xpath('//section[contains(@class,"page")]')}
    if list(pages) != ORDER:
        errs.append("page order in the HTML differs from ORDER")
    for key, expect in T_PAGE.items():
        if P[key] != expect:
            errs.append(f"page number of {key} is {P[key]}, typed expectation {expect}")
    for key, p in pages.items():
        for n, sv in enumerate(p.iter("svg")):
            check_svg_extent(sv, f"page {P[key]} svg {n + 1}", errs)
    # ---- the two 30-day logs: 30 numbered cells, rows of 7, 7, 7, 7 and 2
    for key, mode in (("logA", "A"), ("logB", "B")):
        p = pages[key]
        cells = p.xpath('.//div[contains(@class,"cell")]')
        days = [int(c.get("data-day")) for c in cells]
        if days != list(range(1, 31)):
            errs.append(f"{key}: cells are {days[:3]}... ({len(cells)} cells), expected exactly 1..30 in order")
        shown = [int(re.sub(r"\D", "", c.xpath('.//div[contains(@class,"dn")]')[0].text_content())) for c in cells]
        if shown != days:
            errs.append(f"{key}: printed day numbers differ from the cell numbers")
        rows = p.xpath('.//div[contains(@class,"lrow")]')
        counts = [len(r.xpath('./div[contains(@class,"cell")]')) for r in rows]
        if counts != [7, 7, 7, 7, 2]:
            errs.append(f"{key}: row sizes {counts}, expected [7, 7, 7, 7, 2]")
        for r, (a, b) in zip(rows[:4], T_WEEKS):
            got = [int(c.get("data-day")) for c in r.xpath('./div[contains(@class,"cell")]')]
            if got != list(range(a, b + 1)):
                errs.append(f"{key}: week row {a}-{b} holds {got}")
        for c in cells:
            if len(c.xpath('.//i[contains(@class,"fc")]')) != 3 or [x.text for x in c.xpath('.//i[contains(@class,"fc")]')] != ["1", "2", "3"]:
                errs.append(f"{key}: day {c.get('data-day')} lacks the 1-2-3 focus circles")
            if not c.xpath('.//div[contains(@class,"mw")]'):
                errs.append(f"{key}: day {c.get('data-day')} lacks a minutes line")
            if mode == "A" and not c.xpath('.//div[contains(@class,"ww")]'):
                errs.append(f"{key}: day {c.get('data-day')} lacks a 'what I practiced' line")
            if mode == "B" and len(c.xpath('.//div[contains(@class,"wr")]/span')) != 3:
                errs.append(f"{key}: day {c.get('data-day')} lacks three 'what I worked on' lines")
        txt = p.text_content().lower()
        if "any way i made music" not in txt or "not a grade" not in txt:
            errs.append(f"{key}: lacks the 'any way I made music' or 'not a grade' wording")
    # ---- practice plan
    pp = pages["plan"]
    bar = pp.xpath('.//svg[contains(@class,"pbar")]')[0]
    segs = bar.xpath('.//rect[contains(@class,"seg")]')
    total = int(bar.get("data-total"))
    mins = [int(s.get("data-min")) for s in segs]
    if [s.get("data-part") for s in segs] != T_PLAN_PARTS or mins != T_PLANS[20] or total != 20 or sum(mins) != total or mins != [3, 10, 4, 3]:
        errs.append(f"plan bar: parts/minutes {mins} total {total}")
    wsum = sum(float(s.get("width")) for s in segs)
    for s, m in zip(segs, mins):
        if abs(float(s.get("width")) / wsum - m / 20) > 0.002:
            errs.append(f"plan bar: segment {s.get('data-part')} width is not proportional to {m} of 20 minutes")
    if "3 + 10 + 4 + 3 = 20" not in pp.text_content() or 3 + 10 + 4 + 3 != 20:
        errs.append("plan page does not show 3 + 10 + 4 + 3 = 20")
    trs = pp.xpath('.//tr[@data-total]')
    if sorted(int(t.get("data-total")) for t in trs) != sorted(T_PLANS):
        errs.append("plan table totals differ from 10, 15, 20, 30")
    for t in trs:
        tot = int(t.get("data-total"))
        cells = [int(td.text_content()) for td in t.xpath('./td')[1:5]]
        eq = t.xpath('./td[contains(@class,"eq")]')[0].text_content()
        if cells != T_PLANS[tot] or sum(cells) != tot:
            errs.append(f"plan table row {tot}: {cells} sums to {sum(cells)}")
        if eq != " + ".join(map(str, cells)) + f" = {tot}":
            errs.append(f"plan table row {tot}: equation text '{eq}'")
        if not 0.45 <= cells[1] / tot <= 0.55:
            errs.append(f"plan table row {tot}: new material is not about half")
    if len(pp.xpath('.//table[@data-myplan]//tr[@data-part]')) != 4:
        errs.append("plan page: the blank plan needs four part rows")
    # ---- SMART
    sm = pages["smart"]
    got = [(d.get("data-smart"), d.xpath('.//div[contains(@class,"tt")]')[0].text_content()) for d in sm.xpath('.//div[@data-smart]')]
    if got != T_SMART or "".join(l for l, _ in got) != "SMART":
        errs.append(f"SMART letters/words {got}")
    exrows = [td.text_content().strip() for td in sm.xpath('.//table[contains(@class,"ex")]//td[1]')]
    if exrows != list("SMART"):
        errs.append("SMART example table rows are not S M A R T")
    # ---- goal pages
    gp = pages["goal"]
    if len(gp.xpath('.//div[@data-small]')) != 3 or len(gp.xpath('.//div[@data-big]')) != 1:
        errs.append("goal page needs one big goal and three small goals")
    for sg in gp.xpath('.//div[@data-small]'):
        if [b.text for b in sg.xpath('.//b')] != list("SMART") or len(sg.xpath('.//i[contains(@class,"cb")]')) != 5:
            errs.append("a small goal lacks the S M A R T tick row")
    yp = pages["year"]
    if [c.get("data-cat") for c in yp.xpath('.//div[@data-cat]')] != T_CATS:
        errs.append("music year page categories differ")
    # ---- weekly reflections
    for n in range(1, 5):
        p = pages[f"w{n}"]
        a, b = T_WEEKS[n - 1]
        if p.xpath('.//div[@data-week-days]')[0].get("data-week-days") != f"{a}-{b}" or f"days {a}–{b}" not in p.text_content():
            errs.append(f"reflection {n}: day range is not {a}-{b}")
        if [x.get("data-box") for x in p.xpath('.//div[@data-box]')] != ["well", "hard", "next"]:
            errs.append(f"reflection {n}: needs what went well, what was hard and my next step")
        if f"WEEK {n}" not in p.text_content().upper():
            errs.append(f"reflection {n}: week number missing")
    # ---- totals page
    tp = pages["totals"]
    rows = tp.xpath('.//div[contains(@class,"trow")]')
    allboxes = []
    for r, (a, b) in zip(rows[:4], T_WEEKS):
        ds = [int(x.get("data-day")) for x in r.xpath('./div[contains(@class,"tb")]')]
        if ds != list(range(a, b + 1)):
            errs.append(f"totals: week row {a}-{b} has day boxes {ds}")
        allboxes += ds
    bd = [int(x.get("data-day")) for x in rows[4].xpath('./div[contains(@class,"tb")]')]
    allboxes += bd
    if bd != [29, 30] or allboxes != list(range(1, 31)) or len(rows) != 5:
        errs.append(f"totals: boxes {len(allboxes)} (bonus {bd}), expected 30 day boxes in 5 rows")
    for i, (a, b) in enumerate(T_WEEKS):
        if f"Week {i + 1} total = Day {a} + Day {a + 1} + … + Day {b}" not in tp.text_content():
            errs.append(f"totals: formula text for week {i + 1}")
    if "Month total = Week 1 + Week 2 + Week 3 + Week 4 + Days 29–30" not in tp.text_content() or "Days 29–30 total = Day 29 + Day 30" not in tp.text_content():
        errs.append("totals: month formula missing")
    # ---- chart grids, counted from the drawing
    ch = pages["chart"]
    for kind, cols, rws, step in (("day", 30, 12, 5), ("week", 4, 14, 30)):
        sv = ch.xpath(f'.//svg[@data-kind="{kind}"]')[0]
        cells = sv.xpath('.//rect[contains(@class,"gc")]')
        if len(cells) != cols * rws:
            errs.append(f"chart {kind}: {len(cells)} cells, expected {cols * rws}")
        xs = sorted({round(float(c.get("x")), 2) for c in cells})
        ys = sorted({round(float(c.get("y")), 2) for c in cells})
        if len(xs) != cols or len(ys) != rws:
            errs.append(f"chart {kind}: {len(xs)} columns by {len(ys)} rows drawn, expected {cols} by {rws}")
        xl = [t.text for t in sv.xpath('.//text[contains(@class,"xlab")]')]
        want = [str(i) for i in range(1, 31)] if kind == "day" else [f"Week {i}" for i in range(1, 5)]
        if xl != want:
            errs.append(f"chart {kind}: column labels {xl[:4]}...")
        yl = sorted(int(t.text) for t in sv.xpath('.//text[contains(@class,"ylab")]'))
        if yl != [step * i for i in range(1, rws + 1)]:
            errs.append(f"chart {kind}: row labels {yl}")
    if 12 * 5 != 60 or 14 * 30 != 7 * 60:
        errs.append("chart scales do not match (60 minutes a day, 420 a week)")
    # ---- cross-references: phrase (page N) pairs must point at the true page
    full = " ".join(" ".join(p.text_content().split()) for p in pages.values())
    for phrase, n in (("minutes", 9), ("what I worked on", 10), ("totals", 15), ("practice plan", 7), ("tips", 8), ("SMART", 4)):
        pass
    for m in re.finditer(r"(?i)\bpages? (\d+)(?:–(\d+))?", full):
        a, b = int(m.group(1)), int(m.group(2) or m.group(1))
        if a < 1 or b > TOTAL_PAGES or b < a:
            errs.append(f"reference '{m.group(0)}' is outside the {TOTAL_PAGES}-page file")
    for pat, want in ((r"minutes \(page (\d+)\)", 9), (r"what I worked on \(page (\d+)\)", 10), (r"my minutes this week \(page (\d+)\)", 15), (r"practice plan \(page (\d+)\)", 7),
                      (r"small goals \(page (\d+)\)", 5), (r"weekly reflection \(pages (\d+)", 11), (r"certificate \(page (\d+)\)", 17), (r"chart \(page (\d+)\)", 16),
                      (r"minutes totals \(page (\d+)\)", 15)):
        for m in re.finditer(pat, full, re.I):
            if int(m.group(1)) != want:
                errs.append(f"'{m.group(0)}' should point to page {want}")
    t = pages["teach"].text_content()
    for need in ("page 3", "page 4", "pages 5–6", "page 7", "page 9", "page 10", "pages 11–14", "page 15", "page 16", "page 17"):
        if need not in t:
            errs.append(f"teacher notes lack the reference '{need}'")
    s = pages["start"].text_content()
    for need in ("pages 4–7", "page 9", "page 10", "page 11", "page 12", "page 13", "page 14", "pages 15–17", "page 8", "pages 11–14", "pages 5–6" if False else "page 5", "page 6"):
        if need not in s:
            errs.append(f"start page lacks the reference '{need}'")
    for k in ("start", "teach", "logA", "logB"):
        low = pages[k].text_content().lower()
        if "any way i made music" not in low and k in ("start", "logA", "logB"):
            errs.append(f"{k}: lacks the any-way-I-made-music option")
    # ---- brand and repertoire words
    low = " ".join(p.text_content() for p in pages.values()).lower()
    for bad in ("beethoven", "mozart", "bach", "garageband", "spotify", "youtube", "research shows", "studies show", "scientists", "proven"):
        if bad in low:
            errs.append(f"unwanted word '{bad}' appears")
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
      const BOX = '.wbox, .fb, .gk, .tile, .box, .top, .doc table, .doc p, .doc ul, .doc ol, .fbox, .draw, .ticket, .tempo, .chips, .scale, .cell, .tb, .bnote, .leg, .certf, .gsv, .pbar';
      const FILL = '.wbox, .fb, .gk, .tile, .box, .fbox, .draw, .ticket, .tempo, table, .wl, .chips, .scale, .fam, .cell, .tb, .bnote, .leg, .certf, .gsv, .pbar, .lgrid, .trow';
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
        pg.querySelectorAll('.wbox, .fb, .gk, .tile, .box, .ticket, .tempo, .fbox, .cell, .bnote, .certf, .tb').forEach(bx => {
          if (bx.scrollWidth > bx.clientWidth + 1 || bx.scrollHeight > bx.clientHeight + 1) res.push(`page ${i + 1}: content overflows a ${bx.className} box`);
          const br = bx.getBoundingClientRect();
          bx.querySelectorAll(':scope > *').forEach(ch => { const r = ch.getBoundingClientRect(); if (r.height && r.bottom > br.bottom + 0.5) res.push(`page ${i + 1}: a child spills out of a ${bx.className} box`); });
        });
        pg.querySelectorAll('.tile').forEach(c => {
          const cr = c.getBoundingClientRect();
          c.querySelectorAll('.tt, svg').forEach(e => { const r = e.getBoundingClientRect(); if (r.bottom > cr.bottom - 4 || r.right > cr.right - 4) res.push(`page ${i + 1}: stamp content too close to the cut line`); });
        });
        pg.querySelectorAll('.gk').forEach(g => { const s = g.querySelector('svg').getBoundingClientRect(), gr = g.getBoundingClientRect(); if (s.top < gr.top + 6 || s.bottom > gr.bottom - 6) res.push(`page ${i + 1}: glyph too close to its box edge`); });
        let maxb = 0;
        pg.querySelectorAll('*').forEach(el => { if (skip(el)) return; const r = el.getBoundingClientRect(); if (r.height > 0 && r.width > 0 && ((el.children.length === 0 && ((el.textContent || '').trim() || el.matches('svg, img'))) || el.matches(FILL))) maxb = Math.max(maxb, r.bottom); });
        if (i > 0 && ftop - maxb > 105) res.push(`page ${i + 1}: blank band of ${(ftop - maxb).toFixed(0)}px above the footer (over 10% of the page)`);
        const ys = [];
        pg.querySelectorAll('.rb > *, .lgrid > *, .doc > table, .doc > h2, .doc > p, .doc > ul, .doc > ol, .doc > .cols, .sg').forEach(e => { const r = e.getBoundingClientRect(); if (r.height) ys.push([r.top, r.bottom]); });
        ys.sort((a, c) => a[0] - c[0]);
        for (let k = 1; k < ys.length; k++) if (ys[k][0] - ys[k - 1][1] > 105) res.push(`page ${i + 1}: blank band of ${(ys[k][0] - ys[k - 1][1]).toFixed(0)}px between blocks`);
      });
      document.querySelectorAll('.sq').forEach((sq, i) => {
        const sr = sq.getBoundingClientRect();
        const band = sq.querySelector('.band');
        const btop = band.getBoundingClientRect().top;
        const shots = [];
        sq.querySelectorAll('.shot').forEach(sh => {
          const r = sh.getBoundingClientRect();
          shots.push(r);
          if (r.left < sr.left + 24 || r.right + 8 > sr.right - 24) res.push(`square ${i + 1}: a page shot is too close to the side edge`);
          if (r.bottom + 8 > btop - 8) res.push(`square ${i + 1}: a page shot shadow is within 8px of the band`);
        });
        for (let a = 0; a < shots.length; a++) for (let c = a + 1; c < shots.length; c++) if (shots[a].right + 8 + 8 > shots[c].left && shots[a].left < shots[c].left && shots[a].bottom > shots[c].top) res.push(`square ${i + 1}: page shots lack a gutter`);
        sq.querySelectorAll('.lbl, .lbl span, .pill, .sub, .hd, .tg, .gtl').forEach(el => {
          const r = el.getBoundingClientRect();
          if (r.bottom > btop - 8) res.push(`square ${i + 1}: ${el.className} "${el.textContent.trim().slice(0, 24)}" within 8px of the band`);
          if (r.left < sr.left + 24 || r.right > sr.right - 24) res.push(`square ${i + 1}: text "${el.textContent.trim().slice(0, 24)}" too close to the side edge`);
        });
        sq.querySelectorAll('.tc').forEach(el => { if (el.scrollWidth > el.clientWidth + 1) res.push(`square ${i + 1}: a chip overflows`); });
        sq.querySelectorAll('img').forEach(im => { if (!im.complete || im.naturalWidth === 0) res.push(`square ${i + 1}: an image did not load`); });
        sq.querySelectorAll('svg').forEach(sv => { const r = sv.getBoundingClientRect(); if (r.left < sr.left + 24 || r.right > sr.right - 24) res.push(`square ${i + 1}: a glyph is too close to the side edge`); });
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


def pdf_fonts(path):
    out = subprocess.run(["pdffonts", path], capture_output=True, text=True, check=True).stdout.splitlines()[2:]
    return [(p.split()[0], p.split()[-5]) for p in out]


def verify_layout():
    js = write("layout.js", LAYOUT_JS)
    files = [os.path.join(BUILD, x) for x in ("resource.html", "preview.html", "cover.html", "p1.html", "p2.html", "p3.html")]
    if not all(os.path.exists(x) for x in files):
        return ["build html missing: run gen.py first"]
    r = subprocess.run(["node", js, *files], capture_output=True, text=True, env=node_env())
    if r.returncode != 0:
        return [f"layout script failed: {r.stderr[-300:]}"]
    return json.loads(r.stdout.strip().splitlines()[-1])


def verify_images():
    errs = []
    from PIL import Image
    h = Image.open(HERO)
    a = h.getchannel("A").point(lambda v: 255 if v > 24 else 0)
    bb = a.getbbox()
    if bb is None or bb[0] < 10 or bb[1] < 10 or h.width - bb[2] < 10 or h.height - bb[3] < 10:
        errs.append(f"hero.png touches its image edge: {bb}")
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
            continue
        run = best = 0
        for y in range(120, ytop, 2):
            if rows[y // 2] == 0:
                run += 2
                best = max(best, run)
            else:
                run = 0
        if best > 200:
            errs.append(f"{name}: blank band of {best}px")
        cols = [x for x in range(0, 2000, 2) if any(px[x, y] < 200 for y in range(120, ytop - 4, 4))]
        if cols and (min(cols) < 40 or max(cols) > 1960):
            errs.append(f"{name}: content within 40px of the left or right edge")
    for hn in ("p1.html", "p2.html", "p3.html"):
        t = open(os.path.join(BUILD, hn)).read()
        for cap in re.findall(r'<div class="lbl"[^>]*>([^<]+)(?:<span>[^<]*</span>)?</div>', t):
            if cap not in set(PAGE_NAMES.values()):
                errs.append(f"{hn}: label '{cap}' is not a page name")
        if t.count('class="swm"') != 1:
            errs.append(f"{hn}: expected exactly one PREVIEW watermark")
    return errs




def verify_files():
    errs = []
    from pypdf import PdfReader
    for p in [PDF, PREVIEW_PDF, COVER_PNG, *PREVIEW_PNGS, UPLOAD, TPT_JSON, HERO]:
        if not os.path.exists(p):
            errs.append(f"missing {os.path.relpath(p, TPT)}")
    if errs:
        return errs
    for path, want in ((PDF, TOTAL_PAGES), (PREVIEW_PDF, 4)):
        rd = PdfReader(path)
        if len(rd.pages) != want:
            errs.append(f"{os.path.basename(path)}: {len(rd.pages)} pages, expected {want}")
        for i, pg_ in enumerate(rd.pages):
            if abs(float(pg_.mediabox.width) - 612) > 1 or abs(float(pg_.mediabox.height) - 792) > 1:
                errs.append(f"{os.path.basename(path)} p{i + 1}: not US Letter")
        for name, emb in pdf_fonts(path):
            if emb != "yes":
                errs.append(f"{os.path.basename(path)}: font {name} not embedded")
            if not re.search(r"oswald|sourcesans3", name.lower()):
                errs.append(f"{os.path.basename(path)}: unexpected font {name}")
    rd = PdfReader(PDF)
    texts = [" ".join((pg_.extract_text() or "").split()) for pg_ in rd.pages]
    for i, t in enumerate(texts):
        if len(t) < 40:
            errs.append(f"PDF page {i + 1} looks blank")
        if "PREVIEW" in t.upper():
            errs.append(f"product PDF page {i + 1} carries a PREVIEW watermark")
        if i + 1 != 1 and f"Page {i + 1}" not in t:
            errs.append(f"PDF page {i + 1} does not print its own page number")
    for k, name in PAGE_NAMES.items():
        if k != "cover" and name.lower() not in texts[P[k] - 1].lower():
            errs.append(f"page {P[k]} does not show its name '{name}'")
    # the 30 day numbers are really printed on each log page (read from the PDF text)
    for k in ("logA", "logB"):
        t = texts[P[k] - 1]
        found = [int(x) for x in re.findall(r"DAY (\d+)", t)]
        if sorted(found) != list(range(1, 31)):
            errs.append(f"PDF {k}: printed day labels {len(found)}, expected DAY 1..DAY 30")
    terms = texts[TOTAL_PAGES - 1]
    exp = ("page 2 teacher notes", "page 3 start here", "page 4 SMART goals guide", "page 5 big goal", "page 6 my music year", "page 7 practice plan", "page 8 practice tips",
           "pages 9–10 30-day logs", "pages 11–14 weekly reflections", "page 15 totals", "page 16 progress chart", "page 17 certificate", "page 18 these terms", "(18 pages)")
    for e in exp:
        if e.lower() not in terms.lower():
            errs.append(f"terms page 'what is in this file' lacks '{e}'")
    for e in ("Thank you and please rate", DISCLOSURE):
        if e.lower() not in terms.lower():
            errs.append(f"terms page lacks '{e}'")
    if DISCLOSURE not in texts[1]:
        errs.append("teacher notes lack the disclosure line")
    prd = PdfReader(PREVIEW_PDF)
    for i in range(4):
        t = prd.pages[i].extract_text() or ""
        if t.count("PREVIEW") != 1:
            errs.append(f"preview PDF page {i + 1}: expected exactly one PREVIEW watermark")
        if PAGE_NAMES[PREVIEW_KEYS[i]].lower() not in " ".join(t.split()).lower():
            errs.append(f"preview PDF page {i + 1} is not '{PAGE_NAMES[PREVIEW_KEYS[i]]}'")
    errs += verify_images()
    up = open(UPLOAD).read()
    m = re.search(r"^## 1\. Title\s*\n+```\n(.+?)\n```", up, re.M | re.S)
    title = m.group(1).strip() if m else ""
    if len(title) > 80 or title != LISTING_TITLE:
        errs.append(f"UPLOAD.md: title is {len(title)} chars or differs from the generator")
    if re.search(r"winter|snow|holiday|christmas|december|january|halloween|thanksgiving|spring|summer|autumn|fall\b|new year|back to school", title, re.I):
        errs.append("UPLOAD.md: seasonal word in the title")
    for need in (DISCLOSURE, f"${PRICE}", f"{TOTAL_PAGES} pages", "January", "leave a rating", "Follow the Hudson Beat store", "SMART", "any way"):
        if need.lower() not in up.lower():
            errs.append(f"UPLOAD.md: missing '{need}'")
    sec = up.split("## 5. Page count by section")[1].split("##")[0]
    n_ = [int(x) for x in re.findall(r"^- (?!Total)[^\n]*: (\d+)$", sec, re.M)]
    if sum(n_) != TOTAL_PAGES:
        errs.append(f"UPLOAD.md page list sums to {sum(n_)}, PDF has {TOTAL_PAGES}")
    desc = up.split("## 2. Description")[1].split("## 3.")[0]
    dn = [int(x) for x in re.findall(r"^• [^\n]*\((?:[^()]*? )?(\d+) pages?\)", desc, re.M)]
    if sum(dn) != TOTAL_PAGES:
        errs.append(f"UPLOAD.md description page list sums to {sum(dn)}, PDF has {TOTAL_PAGES}")
    for bad in ("checked by hand", "handmade", "hand-checked", "classroom-tested", "classroom tested"):
        if bad in up.lower():
            errs.append(f"UPLOAD.md says '{bad}'")
    tj = json.load(open(TPT_JSON))
    tags, subs = set(json.load(open(os.path.join(TPT, "TAG-OPTIONS.json")))["options"]), set(json.load(open(os.path.join(TPT, "SUBJECT-OPTIONS.json"))))
    heads = {"Performing Arts", "Holiday", "Student Practice", "Classroom Decor"}
    if any(t not in tags or t in heads for t in tj["tags"]) or any(s_ not in subs or s_ in heads for s_ in tj["subjects"]) or not 1 <= len(tj["tags"]) <= 6:
        errs.append("tpt.json tags or subjects invalid")
    if tj.get("pages") != TOTAL_PAGES or tj["price"] != PRICE or not 1 <= len(tj["grades"]) <= 4:
        errs.append("tpt.json pages, price or grades mismatch")
    c = texts[0].lower()
    if "grades 5–8" not in c or f"{TOTAL_PAGES} pages" not in c or "practice tracker" not in c or "30-day" not in c:
        errs.append("cover text does not state the grades, page count and 30-day logs")
    allt = " ".join(texts).lower()
    for bad in ("colour", "favourite", "metre ", "analyse", "centre", "behaviour", "organis", "practise"):
        if bad in allt:
            errs.append(f"non-US spelling '{bad}'")
    for bad in ("qa ", "checker", "recomputed", "verified by code"):
        if bad in allt.replace("answer keys are verified", ""):
            errs.append(f"buyer-facing text contains internal wording '{bad}'")
    if "new year" in allt:
        errs.append("'new year' appears in the product pages (tag and description only)")
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
    print("CHECK OK: both 30-day logs have 30 numbered cells (rows 7+7+7+7+2) with minutes, what-I-worked-on and 1-2-3 focus circles, and PDF text shows DAY 1..30; "
          "plan splits 2+5+2+1=10, 3+7+3+2=15, 3+10+4+3=20, 5+15+6+4=30 and the 20-minute bar is proportional; totals page 30 day boxes in 4 weeks plus days 29-30 with formulas; "
          "charts 30x12=360 and 4x14=56 cells counted from the drawing with labels; SMART letters; reflections 1-4 day ranges; cross-references, UPLOAD.md and tpt.json agree; "
          f"drawing padding, footer gaps and blank bands clear; PDF {TOTAL_PAGES} Letter pages, preview 4 (one watermark each); images 2000x2000 with clean edges.")


if __name__ == "__main__" and "--check" in sys.argv:
    check()
