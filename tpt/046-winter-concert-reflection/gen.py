#!/usr/bin/env python3
"""Concert Reflection and Self-Assessment (TpT 046): build the resource and verify it.

    python3 gen.py           build everything (PDFs, PNGs, UPLOAD.md, tpt.json) into this folder
    python3 gen.py --check   verify scores, counts, page totals, layout, fonts, previews and listing files

Student reflection pages for band, choir and orchestra (grades 4-12): self-assessment checklists in six skill areas
(18 tick statements per ensemble), a 4-level rubric (6 areas, total 6-24, four score bands), a goal sheet, an etiquette
reflection, two "looking back" pages, a teacher guide and a class tally sheet. No notation is drawn anywhere.
Everything (statements, levels, bands, page numbers, minutes) comes from the data below; `--check` re-derives each number
from the rendered HTML and PDF instead of trusting the data.
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

SLUG = "winter-concert-reflection"
PDF = os.path.join(HERE, f"{SLUG}.pdf")
PREVIEW_PDF = os.path.join(HERE, f"{SLUG}-PREVIEW.pdf")
COVER_PNG = os.path.join(HERE, "cover.png")
PREVIEW_PNGS = [os.path.join(HERE, f"preview-{i}.png") for i in (1, 2, 3)]
UPLOAD = os.path.join(HERE, "UPLOAD.md")
TPT_JSON = os.path.join(HERE, "tpt.json")

STORE = "Brian Lotze"
BRAND = "Hudson Beat"
YEAR = 2026
ACCENT = "#2B7FB8"   # icy blue
DISCLOSURE = "Created with the help of digital and AI tools. Notation and answer keys are verified before release."
LISTING_TITLE = "Music Performance Reflection and Self-Assessment Rubric | Band Choir Orchestra"
PRICE = "3.50"
TAGS = ["Rubrics", "Assessment", "Reflective Journals for Teachers", "Winter", "Worksheets", "Printables"]
SUBJECTS = ["Music", "Instrumental Music", "Vocal Music"]
GRADES = ["4th-grade", "6th-grade", "8th-grade", "10th-grade"]
COPY = f"© {YEAR} {STORE} · {BRAND} · For single-classroom use"

# ------------------------------------------------------------------ data
AREAS = ["Tone", "Rhythm", "Pitch and Intonation", "Dynamics", "Teamwork", "Concert Etiquette"]
LEVELS = ["Beginning", "Developing", "Proficient", "Excelling"]            # level 1..4
BANDS = [(6, 10, "Beginning"), (11, 15, "Developing"), (16, 20, "Proficient"), (21, 24, "Excelling")]
STMT_PER_AREA = 3

STATEMENTS = {   # ensemble -> six areas -> three "I" statements, each one thing only
    "Band": [
        ["I sat tall and used steady, supported air.",
         "My sound stayed full and clear, not airy, pinched or harsh.",
         "My sound stayed steady in both loud and soft parts."],
        ["I counted my rests and came in on time.",
         "I played my rhythms in the right place with the beat.",
         "I kept a steady tempo by watching the conductor."],
        ["I played the right notes and fingerings or slide positions.",
         "I listened and adjusted my pitch to match my section.",
         "I tuned with the group before we played."],
        ["I played the loud and soft markings as written.",
         "I changed volume smoothly in crescendos and decrescendos.",
         "I balanced my sound so the melody could be heard."],
        ["I listened to the other sections while I played.",
         "I stayed with the group after a mistake.",
         "I was ready on time with my instrument, music and pencil."],
        ["I entered and left the stage quietly, in order.",
         "I kept my instrument still and quiet between pieces.",
         "I watched the conductor from the first note to the final bow."],
    ],
    "Choir": [
        ["I stood tall with relaxed shoulders and breathed low.",
         "My voice sounded clear and open, with tall vowels.",
         "My voice stayed steady in both loud and soft parts."],
        ["I counted my rests and came in on time.",
         "I sang my rhythms in the right place with the beat.",
         "I kept a steady tempo by watching the conductor."],
        ["I sang the right notes for my voice part.",
         "I listened and adjusted my pitch to match my section.",
         "I stayed on pitch when other parts sang different notes."],
        ["I sang the loud and soft markings as written.",
         "I changed volume smoothly in crescendos and decrescendos.",
         "I blended my voice so no one voice stuck out."],
        ["I listened to the other voice parts while I sang.",
         "I stayed with the group after a mistake.",
         "I was ready on time with my music and pencil."],
        ["I entered and left the stage quietly, in order.",
         "I stood still and quiet between pieces.",
         "I watched the conductor from the first note to the final bow."],
    ],
    "Orchestra": [
        ["I held my instrument and bow with a relaxed, balanced hold.",
         "My sound stayed full and clear, not scratchy or squeaky.",
         "My bow speed stayed steady in both loud and soft parts."],
        ["I counted my rests and came in on time.",
         "I played my rhythms in the right place with the beat.",
         "I kept a steady tempo by watching the conductor."],
        ["I played the right notes and finger placements.",
         "I listened and adjusted my pitch to match my section.",
         "I tuned with the group before we played."],
        ["I played the loud and soft markings as written.",
         "I changed volume smoothly in crescendos and decrescendos.",
         "I balanced my sound so the melody could be heard."],
        ["I listened to the other sections while I played.",
         "I stayed with the group after a mistake.",
         "I was ready on time with my instrument, music and pencil."],
        ["I entered and left the stage quietly, in order.",
         "I kept my instrument still and quiet between pieces.",
         "I watched the conductor from the first note to the final bow."],
    ],
}
ENSEMBLES = list(STATEMENTS)
ENS_NOTE = {
    "Band": "Wind, brass and percussion players.",
    "Choir": "Singers in any voice part.",
    "Orchestra": "String players. Wind, brass and percussion players in orchestra use the Band page.",
}

RUBRIC = [   # one row per area, four descriptors (level 1 to level 4)
    ["Sound is often airy, harsh, strained or unsteady. Posture and breath or bow support need frequent reminders.",
     "Sound is clear some of the time. Posture and support are steady in easy parts.",
     "Sound is usually clear, full and steady. Posture and support are good.",
     "Sound is full, clear and steady throughout, including loud, soft, high and low parts."],
    ["Often loses the beat. Entrances and rests are frequently wrong.",
     "Keeps the beat in easy parts. Some entrances and rhythms are early or late.",
     "Keeps a steady beat. Most rhythms and entrances are accurate.",
     "Steady beat, accurate rhythms and confident entrances. Follows tempo changes and cutoffs."],
    ["Many wrong notes. Rarely hears or fixes pitch problems.",
     "Mostly correct notes. Hears pitch problems but cannot always fix them.",
     "Correct notes and in tune most of the time. Adjusts to match the group.",
     "Correct notes and in tune throughout. Adjusts quickly to blend with the section."],
    ["Plays or sings at one volume. Markings are missed.",
     "Shows the loud and soft markings in some places.",
     "Shows most markings. Changes in volume are clear and controlled.",
     "Shows every marking with smooth changes and good balance with other parts."],
    ["Often distracted. Needs reminders to be ready or to listen.",
     "Ready most days. Listens to own part more than to the group.",
     "Ready and attentive. Listens and stays with the group.",
     "Leads by example. Listens across the ensemble, supports others and recovers quickly from mistakes."],
    ["Needs reminders to stay quiet, still and on task on stage and in the audience.",
     "Follows stage and audience rules some of the time.",
     "Follows stage and audience rules. Calm and respectful.",
     "Models stage and audience rules for others. Calm and respectful throughout the concert."],
]
PERFORMER_ETIQ = ["I waited quietly before walking on stage.",
                  "I walked on in order and found my spot without talking.",
                  "I kept my body still and quiet between pieces.",
                  "I stayed focused on the conductor during the music.",
                  "I bowed or stood with the group and waited for the cue to leave."]
AUDIENCE_ETIQ = ["I turned off my phone or put it away before the concert.",
                 "I stayed quiet while music was playing.",
                 "I waited until the end of each piece to clap.",
                 "I stayed in my seat until the performance ended.",
                 "I showed respect to every group, including the ones I was not in."]
FEEL_OPTS = ["Very ready", "Mostly ready", "A little ready", "Not ready"]
WENT_OPTS = ["Great", "Good", "Okay", "Rough"]
LOOK46 = ["The best part of our concert was",
          "I am most proud of",
          "Something that was hard for me was",
          "I got better at this by",
          "One thing our group did well together was",
          "Next time I will"]
LOOK712 = ["Choose your highest-scoring skill area. Give two pieces of evidence from the concert, such as a section, a phrase or a moment, that show it.",
           "Choose your lowest-scoring skill area. What caused it, and what did you do in rehearsal that did or did not help?",
           "Compare your self-assessment total with the teacher rubric total, if you have both. Where do they differ, and why might that be?",
           "How did your part fit with the other parts or sections? Describe one moment when listening to others changed how you played or sang.",
           "What would you change about how we prepared for this concert, and what would you keep?"]
SMART = [("S", "Specific", "What exactly will I work on? Name the skill area and the exact skill."),
         ("M", "Measurable", "How will I know I improved? Write a number, a level or a test."),
         ("A", "Achievable", "What help or tools will I use? Examples: a recording, a practice tool, a partner."),
         ("R", "Relevant", "Why does this goal matter for my ensemble?"),
         ("T", "Time-bound", "What is my deadline? Write a date.")]
PRACTICE_DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
NEXT_STEPS = 3
TALLY_ROWS = 20

# page map: (key, title, number of pages, minutes of student time)
SECTIONS = [("cover", "Cover", 1, 0), ("guide", "Teacher Guide", 2, 0), ("concert", "My Concert", 1, 8),
            ("self", "Self-Assessment Checklists: Band, Choir, Orchestra", 3, 10), ("rubric", "4-Level Rubric", 1, 0),
            ("etiq", "Concert Etiquette Reflection", 1, 7), ("look", "Looking Back: grades 4-6 and grades 7-12", 2, 10),
            ("goal", "Goal-Setting Sheet", 1, 10), ("tally", "Class Summary and Tally Sheet", 1, 0),
            ("terms", "Terms of Use and Credits", 1, 0)]
TOTAL_PAGES = sum(s[2] for s in SECTIONS)
PAGE_OF = {}
_p = 1
for _k, _t, _n, _m in SECTIONS:
    PAGE_OF[_k] = _p
    _p += _n
STUDENT_MINUTES = sum(s[3] for s in SECTIONS)


def pg(key, i=0):
    return PAGE_OF[key] + i


def pgs(key):
    n = [s[2] for s in SECTIONS if s[0] == key][0]
    return f"{pg(key)}" if n == 1 else f"{pg(key)}-{pg(key) + n - 1}"


def level_from_ticks(t):
    return t + 1


def band_of(total):
    hits = [b[2] for b in BANDS if b[0] <= total <= b[1]]
    assert len(hits) == 1, total
    return hits[0]


MIN_TOTAL = len(AREAS) * 1
MAX_TOTAL = len(AREAS) * len(LEVELS)
EX_TICKS = [3, 2, 2, 3, 1, 2]
EX_LEVELS = [level_from_ticks(t) for t in EX_TICKS]
EX_TOTAL = sum(EX_LEVELS)
EX_BAND = band_of(EX_TOTAL)
N_TICKS_ENS = len(AREAS) * STMT_PER_AREA
N_TICKS_ALL = N_TICKS_ENS * len(ENSEMBLES)
N_ETIQ = len(PERFORMER_ETIQ) + len(AUDIENCE_ETIQ)

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
.top { display: flex; justify-content: space-between; align-items: flex-end; border-bottom: 2.2pt solid #000; padding-bottom: 6pt; }
.top .t { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 25pt; line-height: 1; letter-spacing: .01em; }
.top .t small { display: block; font-weight: 300; text-transform: none; font-size: 12pt; letter-spacing: 0; margin-top: 4pt; }
.tag { text-align: right; }
.tag .lv { display: inline-block; background: #000; color: #fff; font-family: 'Oswald'; font-weight: 700; font-size: 15pt; padding: 3pt 9pt 4pt; border-radius: 4pt; letter-spacing: .04em; text-transform: uppercase; }
.tag .lv.ak { background: ACCENT; }
.tag .ln { font-family: 'Oswald'; font-weight: 300; font-size: 11pt; margin-top: 3pt; }
.name { display: flex; gap: 18pt; font-size: 12pt; margin: 9pt 0 6pt; align-items: flex-end; }
.name span { flex: 1; border-bottom: 1pt solid #000; height: 16pt; padding-bottom: 1pt; }
.name span.d { flex: 0 0 1.6in; }
.how { font-size: 12pt; margin: 4pt 0 8pt; line-height: 1.3; }
.foot { display: flex; justify-content: space-between; font-size: 8.5pt; color: #333; border-top: .8pt solid #000; padding-top: 3pt; margin-top: 8pt; }
.wm { position: absolute; left: 50%; top: 50%; transform: translate(-50%, -50%) rotate(-38deg); font-family: 'Oswald'; font-weight: 700;
      font-size: 150pt; color: rgba(0,0,0,.13); letter-spacing: .06em; white-space: nowrap; pointer-events: none; z-index: 9; }
.h2 { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 13pt; margin: 11pt 0 4pt; letter-spacing: .02em; line-height: 1.1; }
.h2 .acc { color: ACCENT; }
.doc p, .doc li { font-size: 10.5pt; line-height: 1.34; margin: 0 0 4pt; }
.doc ul, .doc ol { margin: 0 0 4pt; padding-left: 16pt; }
.small { font-size: 9pt !important; color: #333; }
.cb { display: inline-block; width: 11pt; height: 11pt; border: 1.3pt solid #000; border-radius: 2pt; vertical-align: -2pt; margin-right: 5pt; flex: none; }
.cbr { display: inline-flex; align-items: center; margin-right: 12pt; font-size: 10.5pt; }
.cbr .cb { vertical-align: 0; }
table.g { border-collapse: collapse; width: 100%; table-layout: fixed; }
table.g td, table.g th { border: 1pt solid #000; padding: 3pt 5pt; text-align: left; vertical-align: top; font-size: 9.5pt; line-height: 1.25; }
table.g th { font-family: 'Oswald'; font-weight: 500; text-transform: uppercase; font-size: 9.5pt; background: #000; color: #fff; letter-spacing: .03em; }
table.g td.c, table.g th.c { text-align: center; }
table.g td.k { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 10.5pt; line-height: 1.1; }
.box { border: 1.3pt solid #000; border-radius: 6pt; padding: 6pt 8pt; }
.ln { border-bottom: .9pt solid #000; height: 23pt; }
.stmt { display: flex; align-items: flex-start; font-size: 11.5pt; line-height: 1.25; margin: 0 0 6pt; }
.big td { padding: 8pt 7pt !important; font-size: 11pt !important; }
.big td.k { font-size: 12pt !important; }
.rub td { padding: 5pt 6pt !important; font-size: 10.5pt !important; }
.big td .stmt:last-child { margin-bottom: 0; }
.lvbox { display: inline-block; width: 26pt; height: 22pt; border: 1.3pt solid #000; border-radius: 4pt; }
.cover { align-items: center; padding: 0; }
.cvr { width: 1000px; position: relative; display: flex; flex-direction: column; align-items: center; background: #fff; overflow: hidden; }
.cvr .store { font-family: 'Oswald'; font-weight: 500; letter-spacing: .32em; text-transform: uppercase; font-size: 22px; margin-top: 34px; }
.cvr .hd { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; text-align: center; line-height: .95; }
.cvr .sub { font-family: 'Oswald'; font-weight: 300; text-align: center; }
.cvr .band { width: 100%; background: #000; color: #fff; text-align: center; font-family: 'Oswald'; font-weight: 500; text-transform: uppercase; letter-spacing: .1em; font-size: 26px; padding: 16px 0 18px; }
.cvr .band em { font-style: normal; color: ACCENT; }
""".replace("ACCENT", ACCENT)

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
.lbl { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 22px; text-align: center; margin-top: 18px; }
.lbl span { font-weight: 300; text-transform: none; display: block; font-size: 18px; }
.dc { box-sizing: border-box; border: 2px solid #000; border-radius: 8px; padding: 9px 10px; background: #fff; text-align: left; width: 205px; height: 205px; }
.dc .dn { font-family: 'Oswald'; font-weight: 700; font-size: 15px; color: ACCENT; letter-spacing: .06em; }
.dc .dt { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 21px; line-height: 1.05; margin-top: 2px; }
.dc .df { font-family: 'Oswald'; font-weight: 300; font-size: 19px; line-height: 1.2; margin-top: 8px; }
""".replace("ACCENT", ACCENT)


def html_doc(pages, title="doc"):
    return (f'<!doctype html><html><head><meta charset="utf-8"><title>{escape(title)}</title>'
            f'<style>{font_css()}{CSS}</style></head><body>{"".join(pages)}</body></html>')


# ------------------------------------------------------------------ page parts
def cb(extra=""):
    return f'<span class="cb" {extra}></span>'


def foot(right):
    return f'<div class="foot"><span>{COPY}</span><span>{right}</span></div>'


def header(title, sub, tag, tag_sub, ak=False):
    return (f'<div class="top"><div class="t">{title}<small>{sub}</small></div>'
            f'<div class="tag"><div class="lv{" ak" if ak else ""}">{tag}</div><div class="ln">{tag_sub}</div></div></div>')


def name_line():
    return '<div class="name">Name <span></span> Date <span class="d"></span></div>'


def page(key, i, inner, right=None, extra_cls="", wm=False):
    n = pg(key, i)
    return (f'<section class="page {extra_cls}" data-pg="{n}" data-key="{key}">{"<div class=wm>PREVIEW</div>" if wm else ""}'
            f'{inner}<div style="flex:1"></div>{foot(right or f"Page {n}")}</section>')


def snowflake(cx, cy, r, color, sw=2.2):
    out = []
    for k in range(6):
        a = math.radians(60 * k - 90)
        ex, ey = cx + r * math.cos(a), cy + r * math.sin(a)
        out.append(f'<line x1="{cx:.1f}" y1="{cy:.1f}" x2="{ex:.1f}" y2="{ey:.1f}"/>')
        for f_, bl in ((0.55, 0.32), (0.8, 0.2)):
            bx, by = cx + r * f_ * math.cos(a), cy + r * f_ * math.sin(a)
            for da in (-55, 55):
                b = a + math.radians(da)
                out.append(f'<line x1="{bx:.1f}" y1="{by:.1f}" x2="{bx + r * bl * math.cos(b):.1f}" y2="{by + r * bl * math.sin(b):.1f}"/>')
    return f'<g stroke="{color}" stroke-width="{sw}" stroke-linecap="round" fill="none">{"".join(out)}</g>'


def check_mark(x, y, s, color=ACCENT):
    return (f'<path d="M{x + s * .12:.1f} {y + s * .55:.1f} L{x + s * .42:.1f} {y + s * .85:.1f} L{x + s * .95:.1f} {y + s * .1:.1f}" '
            f'stroke="{color}" stroke-width="{s * .16:.1f}" fill="none" stroke-linecap="round" stroke-linejoin="round"/>')


# ------------------------------------------------------------------ cover art
def stage_art():
    W, H = 880, 470
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" style="display:block">']
    # curtains: left and right drapes with fold lines
    for side in (0, 1):
        x0, x1 = (6, 176) if side == 0 else (W - 176, W - 6)
        o.append(f'<path d="M{x0} 30 H{x1} V{H - 70} Q{(x0 + x1) / 2} {H - 54} {x0} {H - 70} Z" fill="#fff" stroke="#000" stroke-width="3.2" stroke-linejoin="round"/>')
        for k in range(1, 5):
            fx = x0 + (x1 - x0) * k / 5
            o.append(f'<path d="M{fx:.0f} 34 Q{fx + (8 if side == 0 else -8):.0f} {H / 2:.0f} {fx:.0f} {H - 62}" fill="none" stroke="#000" stroke-width="2"/>')
    o.append(f'<rect x="6" y="14" width="{W - 12}" height="30" rx="6" fill="#000"/>')
    # string of lights along the valance
    pts = []
    for k in range(17):
        x = 22 + k * (W - 44) / 16
        y = 44 + 26 * math.sin(math.pi * k / 16)
        pts.append((x, y))
    o.append('<path d="M' + " L".join(f"{x:.1f} {y - 0:.1f}" for x, y in pts) + '" fill="none" stroke="#000" stroke-width="2.4"/>')
    for k, (x, y) in enumerate(pts):
        fill = ACCENT if k % 2 == 0 else "#fff"
        o.append(f'<ellipse cx="{x:.1f}" cy="{y + 10:.1f}" rx="7.5" ry="10" fill="{fill}" stroke="#000" stroke-width="2.4"/>')
        o.append(f'<rect x="{x - 3.5:.1f}" y="{y - 1:.1f}" width="7" height="5" fill="#000"/>')
    # stage floor with risers
    o.append(f'<path d="M150 {H - 70} H{W - 150} L{W - 100} {H - 12} H100 Z" fill="#fff" stroke="#000" stroke-width="3.2" stroke-linejoin="round"/>')
    o.append(f'<line x1="124" y1="{H - 41}" x2="{W - 124}" y2="{H - 41}" stroke="#000" stroke-width="2"/>')
    # checklist card on stage
    cx, cy, cw, ch = 300, 108, 280, 298
    o.append(f'<rect x="{cx + 7}" y="{cy + 7}" width="{cw}" height="{ch}" rx="12" fill="#000"/>')
    o.append(f'<rect x="{cx}" y="{cy}" width="{cw}" height="{ch}" rx="12" fill="#fff" stroke="#000" stroke-width="3.2"/>')
    o.append(f'<rect x="{cx + 90}" y="{cy - 12}" width="100" height="26" rx="8" fill="#000"/>')
    o.append(f'<circle cx="{cx + 140}" cy="{cy + 1}" r="5" fill="#fff"/>')
    for k in range(4):
        y = cy + 44 + k * 60
        o.append(f'<rect x="{cx + 22}" y="{y}" width="34" height="34" rx="5" fill="#fff" stroke="#000" stroke-width="3"/>')
        if k < 3:
            o.append(check_mark(cx + 24, y + 1, 32))
        o.append(f'<line x1="{cx + 72}" y1="{y + 24}" x2="{cx + cw - 24}" y2="{y + 24}" stroke="#000" stroke-width="3" stroke-linecap="round"/>')
        o.append(f'<line x1="{cx + 72}" y1="{y + 6}" x2="{cx + cw - 70 - (k % 2) * 30}" y2="{y + 6}" stroke="#000" stroke-width="3" stroke-linecap="round" opacity=".45"/>')
    # snowflakes beside the card
    o.append(snowflake(236, 190, 38, ACCENT, 3))
    o.append(snowflake(660, 150, 46, "#000", 2.8))
    o.append(snowflake(212, 330, 24, "#000", 2.4))
    o.append(snowflake(690, 316, 30, ACCENT, 2.8))
    o.append("</svg>")
    return "".join(o)


def cover_inner(h):
    return (f'<div class="cvr" style="height:{h}px"><div class="store">{BRAND}</div>'
            f'<div style="flex:1;display:flex;flex-direction:column;justify-content:space-evenly;align-items:center;width:100%;padding-bottom:78px;position:relative">'
            f'<div style="width:880px">{stage_art()}</div>'
            f'<div><div class="hd" style="font-size:66px">Winter Concert</div>'
            f'<div class="hd" style="font-size:128px">Reflection</div>'
            f'<div class="hd" style="font-size:54px;margin-top:4px">&amp; Self-Assessment</div>'
            f'<div class="sub" style="font-size:28px;margin-top:12px">Band · Choir · Orchestra · rubric · goal sheet</div></div></div>'
            f'<div class="band" style="position:absolute;left:0;bottom:0">Grades 4–12 <em>·</em> {TOTAL_PAGES} pages <em>·</em> 3 ensemble versions</div></div>')


def cover_page():
    return (f'<section class="page cover" data-pg="1" data-key="cover" style="padding:0"><div style="zoom:.816;width:1000px">{cover_inner(1294)}</div></section>')


# ------------------------------------------------------------------ teacher guide
def guide_pages():
    pagemap = "".join(
        f'<tr><td>{pgs(k)}</td><td>{escape(t)}</td><td class="c">{n}</td></tr>' for k, t, n, _ in SECTIONS)
    band_rows = "".join(f'<tr><td class="c">{a}–{b}</td><td>{n}</td></tr>' for a, b, n in BANDS)
    ex = "".join(f'<tr><td>{AREAS[i]}</td><td class="c">{EX_TICKS[i]}</td><td class="c">{EX_LEVELS[i]}</td></tr>' for i in range(len(AREAS)))
    p1 = (f'{header("Teacher Guide", "How to use, what is inside and how scoring works", "Teacher", "Page 1 of 2", True)}'
          f'<div class="doc"><div class="cols" style="display:flex;gap:20pt"><div style="flex:1">'
          f'<div class="h2">How to use</div><ol>'
          f'<li>Choose the concert pages that match your ensemble: {pg("self")} for band, {pg("self", 1)} for choir, {pg("self", 2)} for orchestra. Print one copy of the pages you need for each student.</li>'
          f'<li>Students fill in <b>My Concert</b> (page {pg("concert")}) first, then the checklist, the etiquette page and one Looking Back page.</li>'
          f'<li>On the checklist, a student ticks every statement that is true of their own concert, counts the ticks in each area and turns the count into a level.</li>'
          f'<li>Optional: score the same six areas yourself with the rubric (page {pg("rubric")}) and compare.</li>'
          f'<li>Finish with the Goal-Setting Sheet (page {pg("goal")}). Record scores on the Class Summary (page {pg("tally")}).</li></ol>'
          f'<div class="h2">Student time</div>'
          f'<p>About {STUDENT_MINUTES} minutes in all: My Concert {SECTIONS[2][3]}, checklist {SECTIONS[3][3]}, etiquette {SECTIONS[5][3]}, Looking Back {SECTIONS[6][3]} and goal sheet {SECTIONS[7][3]}. '
          f'Use one long period, or split it over two.</p>'
          f'<div class="h2">What is inside ({TOTAL_PAGES} pages)</div>'
          f'<table class="g"><colgroup><col style="width:22%"><col><col style="width:16%"></colgroup><tr><th>Pages</th><th>Item</th><th class="c">Count</th></tr>{pagemap}</table>'
          f'</div><div style="flex:1">'
          f'<div class="h2">Scoring the checklist</div>'
          f'<p>Each ensemble page has {len(AREAS)} skill areas with {STMT_PER_AREA} statements each, so {N_TICKS_ENS} tick boxes per page. '
          f'Students turn the ticks in an area into a level:</p>'
          f'<table class="g"><tr><th class="c">Ticks</th>{"".join(f"<th class=c>{t}</th>" for t in range(STMT_PER_AREA + 1))}</tr>'
          f'<tr><td class="c"><b>Level</b></td>{"".join(f"<td class=c>{level_from_ticks(t)}</td>" for t in range(STMT_PER_AREA + 1))}</tr></table>'
          f'<p>Level = ticks + 1, so every area scores from 1 to {len(LEVELS)}. The {len(AREAS)} levels add up to a total from {MIN_TOTAL} to {MAX_TOTAL}.</p>'
          f'<div class="h2">Worked example</div>'
          f'<table class="g"><colgroup><col style="width:56%"><col><col></colgroup><tr><th>Area</th><th class="c">Ticks</th><th class="c">Level</th></tr>{ex}'
          f'<tr><td><b>Total</b></td><td class="c">{sum(EX_TICKS)}</td><td class="c"><b>{EX_TOTAL}</b></td></tr></table>'
          f'<p>{" + ".join(str(x) for x in EX_LEVELS)} = {EX_TOTAL} out of {MAX_TOTAL}, which is in the {EX_BAND} band.</p>'
          f'<div class="h2">Score bands</div>'
          f'<table class="g"><colgroup><col style="width:34%"><col></colgroup><tr><th class="c">Total</th><th>Band</th></tr>{band_rows}</table>'
          f'<p class="small">The bands cover every total from {MIN_TOTAL} to {MAX_TOTAL} with no gaps. Use them to start a conversation, not as a grade.</p>'
          f'</div></div></div>')
    diff_rows = [
        ("Reading support", "Read each statement aloud once. Use the checklist for one area at a time.", "Students read and tick on their own."),
        ("Which Looking Back page", f"Page {pg('look')}: six sentence starters.", f"Page {pg('look', 1)}: five prompts that ask for evidence."),
        ("Scoring", "Student ticks and levels only. You add the rubric score for a few students or none.", "Student scores first, then the teacher rubric. Compare the two totals."),
        ("Goal sheet", "Choose one area. Teacher or partner helps with the date and the measure.", "Write a full SMART goal with a practice plan and check-ins."),
        ("Etiquette page", "Talk through each item before students tick.", "Students tick, then write about one habit to change."),
        ("Discussion", "Pair share: one proud moment.", "Small groups: compare evidence for the highest and lowest areas."),
    ]
    dr = "".join(f'<tr><td class="k">{a}</td><td>{b}</td><td>{c}</td></tr>' for a, b, c in diff_rows)
    p2 = (f'{header("Teacher Guide", "Differentiation, conferencing and standards", "Teacher", "Page 2 of 2", True)}'
          f'<div class="doc"><div class="h2">Differentiation: grades 4–6 and grades 7–12</div>'
          f'<table class="g"><colgroup><col style="width:20%"><col><col></colgroup><tr><th>Item</th><th>Grades 4–6</th><th>Grades 7–12</th></tr>{dr}</table>'
          f'<div class="h2">Ensemble versions</div><ul>'
          f'<li><b>Band</b> (page {pg("self")}): wind, brass and percussion.</li>'
          f'<li><b>Choir</b> (page {pg("self", 1)}): singers in any voice part.</li>'
          f'<li><b>Orchestra</b> (page {pg("self", 2)}): string players. Wind, brass and percussion players in orchestra use the Band page.</li></ul>'
          f'<p>The six skill areas, the levels and the rubric are the same for every ensemble, so a class summary can mix all three.</p>'
          f'<div class="h2">Conferencing and feedback</div><ul>'
          f'<li>Start with what the student is proud of (page {pg("concert")}), then look at their highest area.</li>'
          f'<li>If your rubric level and the student\'s level are 2 or more apart in an area, ask the student for evidence from the concert.</li>'
          f'<li>Connect the lowest area to the goal sheet. One small goal is better than three large ones.</li>'
          f'<li>Keep the wording neutral. These pages say "concert", "performance" and "winter"; they use no holiday or religious references, so they fit any school.</li></ul>'
          f'<div class="h2">Standards</div>'
          f'<p>Supports the National Core Arts Standards for Music: MU:Pr5.1 (rehearse, evaluate and refine) and MU:Re9.1 (evaluate performances). '
          f'Modest claim: a structured reflection routine, not a full assessment program.</p>'
          f'<div class="h2">Printing</div>'
          f'<p>US Letter. The student pages print in black and white; print them single-sided.</p>'
          f'<p class="small">No songs, lyrics, notation or copyrighted characters are used.</p></div>')
    return [page("guide", 0, p1, "Teacher Guide · Page 2"), page("guide", 1, p2, "Teacher Guide · Page 3")]


# ------------------------------------------------------------------ student pages
def concert_page():
    ens = "".join(f'<span class="cbr">{cb()}{e}</span>' for e in ENSEMBLES)
    feel = "".join(f'<span class="cbr">{cb()}{o}</span>' for o in FEEL_OPTS)
    went = "".join(f'<span class="cbr">{cb()}{o}</span>' for o in WENT_OPTS)
    inner = (header("My Concert", "Tell about your concert before you score it.", "Student", f"Page {pg('concert')}") + name_line() +
             f'<div class="doc"><div class="h2">My ensemble <span class="acc">·</span> <span style="font-weight:300;text-transform:none;font-size:11pt">tick one</span></div>'
             f'<div>{ens}</div>'
             f'<div class="name" style="margin-top:9pt">My instrument or voice part <span></span> Concert date <span class="d"></span></div>'
             f'<div class="h2">Pieces we performed</div>'
             f'<div class="ln"></div><div class="ln"></div><div class="ln"></div>'
             f'<div class="h2">How ready did I feel before the concert? <span style="font-weight:300;text-transform:none;font-size:11pt">tick one</span></div><div data-grp="feel">{feel}</div>'
             f'<div class="h2">How did the concert go for me? <span style="font-weight:300;text-transform:none;font-size:11pt">tick one</span></div><div data-grp="went">{went}</div>'
             f'<div class="h2">What I am proud of</div>'
             f'<div class="box" style="height:3.7in"><div style="font-size:10pt;color:#333">Write about one thing you did well, or one way you helped your group. Start with: "I am proud that I..."</div></div>'
             f'</div>')
    return page("concert", 0, inner)


def self_page(ei):
    ens = ENSEMBLES[ei]
    rows = []
    for ai, area in enumerate(AREAS):
        st = "".join(f'<div class="stmt" data-self="{ens}">{cb()}<span>{escape(s)}</span></div>' for s in STATEMENTS[ens][ai])
        rows.append(f'<tr data-area="{ai}"><td class="k">{area}</td><td>{st}</td><td class="c"><span class="lvbox" style="width:34pt;height:30pt"></span></td><td class="c"><span class="lvbox" style="width:34pt;height:30pt"></span></td></tr>')
    conv = "  ·  ".join(f"{t} {'tick' if t == 1 else 'ticks'} = level {level_from_ticks(t)}" for t in range(STMT_PER_AREA + 1))
    inner = (header(f"Self-Assessment: {ens}", ENS_NOTE[ens], ens, f"Page {pg('self', ei)}") + name_line() +
             f'<div class="how"><b>Directions:</b> Tick every statement that is true about your concert. Count the ticks in each row and write the number. '
             f'Then write your level.</div>'
             f'<div style="margin:0 0 7pt;font-size:10.5pt"><b>{conv}</b></div>'
             f'<table class="g big" data-ens="{ens}"><colgroup><col style="width:17%"><col><col style="width:12%"><col style="width:12%"></colgroup>'
             f'<tr><th>Skill</th><th>I can say...</th><th class="c">Ticks (0–{STMT_PER_AREA})</th><th class="c">Level (1–{len(LEVELS)})</th></tr>{"".join(rows)}</table>'
             f'<div style="display:flex;align-items:center;gap:10pt;margin-top:10pt;border:1.3pt solid #000;border-radius:6pt;padding:6pt 10pt">'
             f'<div style="font-family:Oswald;font-weight:700;text-transform:uppercase;font-size:14pt;white-space:nowrap">My total</div>'
             f'<span class="lvbox" style="width:44pt;height:32pt"></span><div style="font-size:11.5pt;white-space:nowrap">out of {MAX_TOTAL} (add the {len(AREAS)} levels)</div></div>'
             f'<div class="small" style="margin-top:6pt">Bands: ' + " · ".join(f"{a}–{b} {n}" for a, b, n in BANDS) + '</div>')
    return page("self", ei, inner)


def rubric_page():
    rows = "".join(
        f'<tr data-area="{ai}"><td class="k">{AREAS[ai]}</td>{"".join(f"<td>{escape(d)}</td>" for d in RUBRIC[ai])}</tr>' for ai in range(len(AREAS)))
    head = "".join(f'<th class="c">{i + 1} · {n}</th>' for i, n in enumerate(LEVELS))
    inner = (header("4-Level Rubric", "For teachers and students: band, choir and orchestra", "Rubric", f"Page {pg('rubric')}", True) +
             f'<div class="how" style="margin-top:8pt">Score each area from 1 to {len(LEVELS)}. Add the {len(AREAS)} levels for a total from {MIN_TOTAL} to {MAX_TOTAL}.</div>'
             f'<table class="g big rub" data-rubric="1"><colgroup><col style="width:14%"><col style="width:21.5%"><col style="width:21.5%"><col style="width:21.5%"><col style="width:21.5%"></colgroup>'
             f'<tr><th>Skill</th>{head}</tr>{rows}</table>'
             f'<div class="h2" style="margin-top:16pt">Total score</div>'
             f'<table class="g" data-bands="1"><tr><th class="c">Total</th>{"".join(f"<th class=c>{a}–{b}</th>" for a, b, _ in BANDS)}</tr>'
             f'<tr><td class="c"><b>Band</b></td>{"".join(f"<td class=c>{n}</td>" for _, _, n in BANDS)}</tr></table>'
             f'<div class="small" style="margin-top:6pt">Level 1 in all {len(AREAS)} areas = {MIN_TOTAL}. Level {len(LEVELS)} in all {len(AREAS)} areas = {MAX_TOTAL}.</div>'
             f'<div style="display:flex;gap:12pt;margin-top:14pt;align-items:center;font-size:12pt"><div class="box" style="flex:1;padding:10pt"><b>Teacher total:</b> ______ / {MAX_TOTAL}</div>'
             f'<div class="box" style="flex:1;padding:10pt"><b>Student total:</b> ______ / {MAX_TOTAL}</div></div>')
    return page("rubric", 0, inner)


def etiq_page():
    def col(title, items, grp):
        li = "".join(f'<div class="stmt" data-etiq="{grp}" style="margin-bottom:7pt">{cb()}<span>{escape(s)}</span></div>' for s in items)
        return f'<div style="flex:1"><div class="h2" style="margin-top:4pt">{title}</div>{li}</div>'
    inner = (header("Concert Etiquette", "How did I act on stage and in the audience?", "Student", f"Page {pg('etiq')}") + name_line() +
             f'<div class="how"><b>Directions:</b> Tick each statement that is true. There are {N_ETIQ} statements: {len(PERFORMER_ETIQ)} for performers and {len(AUDIENCE_ETIQ)} for audience members. '
             f'Leave a box empty if it was not true this time.</div>'
             f'<div style="display:flex;gap:22pt">{col("As a performer", PERFORMER_ETIQ, "performer")}{col("As an audience member", AUDIENCE_ETIQ, "audience")}</div>'
             f'<div class="h2">Ticks: performer ____ / {len(PERFORMER_ETIQ)} &nbsp; audience ____ / {len(AUDIENCE_ETIQ)}</div>'
             f'<div class="h2">Think about it</div>'
             f'<div class="how" style="margin:0 0 2pt">1. One thing the audience did that helped our group perform well:</div><div class="ln"></div><div class="ln"></div>'
             f'<div class="how" style="margin:8pt 0 2pt">2. One etiquette habit I want to practice before the next concert:</div><div class="ln"></div><div class="ln"></div>'
             f'<div class="how" style="margin:8pt 0 2pt">3. Why does good etiquette matter to the performers and to the audience?</div><div class="ln"></div><div class="ln"></div>')
    return page("etiq", 0, inner)


def look_pages():
    lines = "".join(f'<div class="how" style="margin:9pt 0 2pt" data-look="46"><b>{i + 1}.</b> {escape(s)}...</div><div class="ln"></div><div class="ln"></div>' for i, s in enumerate(LOOK46))
    a = page("look", 0, header("Looking Back", "Grades 4–6: finish each sentence.", "Grades 4–6", f"Page {pg('look')}") + name_line() +
             f'<div class="how"><b>Directions:</b> Finish each sentence with at least one full sentence of your own.</div>{lines}')
    lines2 = "".join(f'<div class="how" style="margin:8pt 0 2pt" data-look="712"><b>{i + 1}.</b> {escape(s)}</div><div class="ln"></div><div class="ln"></div><div class="ln"></div>' for i, s in enumerate(LOOK712))
    b = page("look", 1, header("Looking Back", "Grades 7–12: use evidence from the concert.", "Grades 7–12", f"Page {pg('look', 1)}") + name_line() +
             f'<div class="how"><b>Directions:</b> Answer each prompt in a short paragraph. Use your checklist and rubric scores as evidence.</div>{lines2}')
    return [a, b]


def goal_page():
    smart = "".join(
        f'<div style="display:flex;gap:8pt;margin-bottom:9pt" data-smart="{l}"><div style="flex:none;width:26pt;height:26pt;background:#000;color:#fff;font-family:Oswald;font-weight:700;font-size:16pt;text-align:center;line-height:26pt;border-radius:4pt">{l}</div>'
        f'<div style="flex:1"><div style="font-family:Oswald;font-weight:700;text-transform:uppercase;font-size:10.5pt">{n} <span style="font-family:\'Source Sans 3\';font-weight:400;text-transform:none;font-size:9.5pt">· {escape(q)}</span></div>'
        f'<div class="ln" style="height:25pt"></div></div></div>' for l, n, q in SMART)
    areas = "".join(f'<span class="cbr" data-goalarea="1">{cb()}{a}</span>' for a in AREAS)
    steps = "".join(f'<tr><td class="c">{i + 1}</td><td style="height:34pt"></td><td></td><td class="c"><span class="cb" style="margin:0"></span></td></tr>' for i in range(NEXT_STEPS))
    days = "".join(f'<div style="flex:1;text-align:center;border:1.2pt solid #000;border-radius:4pt;padding:2pt 0 8pt;font-family:Oswald;font-size:10pt;text-transform:uppercase">{d}<div style="height:34pt"></div></div>' for d in PRACTICE_DAYS)
    inner = (header("My Goal Sheet", "Pick one skill and make a plan.", "Student", f"Page {pg('goal')}") + name_line() +
             f'<div class="h2" style="margin-top:4pt">1. My goal area <span style="font-weight:300;text-transform:none;font-size:11pt">tick one, ideally my lowest level</span></div><div>{areas}</div>'
             f'<div class="h2">2. My SMART goal</div>{smart}'
             f'<div class="h2" style="margin-top:6pt">3. My next steps ({NEXT_STEPS})</div>'
             f'<table class="g"><colgroup><col style="width:7%"><col><col style="width:22%"><col style="width:10%"></colgroup><tr><th class="c">#</th><th>What I will do</th><th>By when</th><th class="c">Done</th></tr>{steps}</table>'
             f'<div class="h2" style="margin-top:8pt">4. My practice plan <span style="font-weight:300;text-transform:none;font-size:11pt">write the minutes for each day</span></div>'
             f'<div style="display:flex;gap:4pt">{days}</div>'
             f'<div style="display:flex;gap:16pt;margin-top:22pt;font-size:11.5pt"><div style="flex:1">Student signature <span style="display:inline-block;border-bottom:1pt solid #000;width:55%">&nbsp;</span></div>'
             f'<div style="flex:1">Check-in date <span style="display:inline-block;border-bottom:1pt solid #000;width:45%">&nbsp;</span></div></div>')
    return page("goal", 0, inner)


def tally_page():
    heads = "".join(f'<th class="c" style="font-size:8pt;padding:3pt 1pt">{a.split(" ")[0] if a != "Concert Etiquette" else "Etiquette"}</th>' for a in AREAS)
    rows = "".join(f'<tr data-row="1"><td class="c" style="height:16.5pt">{i + 1}</td><td></td>{"<td></td>" * len(AREAS)}<td></td><td></td></tr>' for i in range(TALLY_ROWS))
    tot = f'<tr><td colspan="2"><b>Class total per area</b></td>{"<td></td>" * len(AREAS)}<td></td><td></td></tr>'
    avg = f'<tr><td colspan="2"><b>Average level per area (total ÷ students)</b></td>{"<td></td>" * len(AREAS)}<td></td><td></td></tr>'
    cols = ('<col style="width:5%"><col style="width:23%">' + f'<col style="width:9.2%">' * len(AREAS) + '<col style="width:9%"><col style="width:7.8%">')
    brows = "".join(f'<tr data-band="1"><td class="c">{a}–{b}</td><td>{n}</td><td></td><td></td></tr>' for a, b, n in BANDS)
    inner = (header("Class Summary", f"Record each student's level (1–{len(LEVELS)}) in the six areas.", "Teacher", f"Page {pg('tally')}", True) +
             f'<div class="how" style="margin-top:6pt">Class: ____________ &nbsp; Ensemble: ____________ &nbsp; Date: ____________ &nbsp; Total = add the {len(AREAS)} levels (from {MIN_TOTAL} to {MAX_TOTAL}).</div>'
             f'<table class="g" data-tally="1"><colgroup>{cols}</colgroup><tr><th class="c">#</th><th>Student</th>{heads}<th class="c" style="font-size:8pt;padding:3pt 1pt">Total /{MAX_TOTAL}</th><th class="c" style="font-size:8pt;padding:3pt 1pt">Band</th></tr>{rows}{tot}{avg}</table>'
             f'<div style="display:flex;gap:14pt;align-items:flex-start;margin-top:9pt"><div style="flex:1.2"><table class="g" data-bandtally="1"><colgroup><col style="width:20%"><col><col style="width:22%"><col style="width:18%"></colgroup>'
             f'<tr><th class="c">Total</th><th>Band</th><th>Tally</th><th class="c">Count</th></tr>{brows}</table></div>'
             f'<div style="flex:1" class="small">Count the students in each band. The four counts should add up to the number of students in the class.<br><br><b>Students: ______ &nbsp; Sum of counts: ______</b></div></div>')
    return page("tally", 0, inner)


def terms_page():
    inner = (f'<div class="top"><div class="t">Terms of Use<small>Thank you for your purchase!</small></div></div><div class="doc">'
             f'<p style="margin-top:10pt">© {YEAR} {STORE}. {BRAND} by {STORE}. All rights reserved. This purchase gives <b>one teacher</b> a license to use this resource with their own students.</p>'
             f'<div class="h2">You may</div><ul><li>Print and copy pages for your own classroom and students.</li>'
             f'<li>Share pages with your own students through a password-protected class site or learning platform.</li>'
             f'<li>Use the pages with your own students when you have a substitute teacher.</li></ul>'
             f'<div class="h2">You may not</div><ul><li>Share, email or copy this resource for other teachers, a whole school or a district. Additional licenses are available on Teachers Pay Teachers.</li>'
             f'<li>Post any part of it on a public website, shared drive or social media.</li>'
             f'<li>Sell, give away or claim any part of it as your own, or edit it into a new product.</li></ul>'
             f'<div class="h2">Questions?</div><p>Please use the Q&amp;A tab on the {BRAND} by {STORE} store on Teachers Pay Teachers. If something looks wrong, let me know there and I will fix it.</p>'
             f'<div class="h2">Credits</div><ul><li>Pages, layouts, art and scoring tables: original work, {BRAND} by {STORE}.</li>'
             f'<li>Text fonts: Oswald (The Oswald Project Authors) and Source Sans 3 (Adobe), SIL Open Font License 1.1.</li></ul>'
             f'<p class="small">{DISCLOSURE}</p></div>')
    return page("terms", 0, inner)


def full_pages(wm=False):
    return ([cover_page()] + guide_pages() + [concert_page()] + [self_page(i) for i in range(3)] + [rubric_page(), etiq_page()]
            + look_pages() + [goal_page(), tally_page(), terms_page()])


PREVIEW_PICK = [4, 5, 8, 13]   # PDF page numbers (1-based): My Concert, band checklist, rubric, goal sheet


def preview_pages():
    allp = full_pages()
    picks = [pg("concert"), pg("self"), pg("rubric"), pg("goal")]
    out = []
    for n in picks:
        s = allp[n - 1]
        s = s.replace('<section class="page ', '<section class="page ', 1)
        s = re.sub(r'(<section [^>]*>)', r'\1<div class="wm">PREVIEW</div>', s, count=1)
        out.append(s)
    return out


# ------------------------------------------------------------------ square images
def sq_doc(body):
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{font_css()}{CSS}html,body{{margin:0;background:#fff}}{SQ_CSS}</style></head><body>{body}</body></html>')


def shots(imgs, labels, w):
    return "".join(f'<div style="width:{w}px"><div class="shot"><img src="{i}"></div><div class="lbl">{l}</div></div>' for i, l in zip(imgs, labels))


def preview_square_1():
    pills = ''.join(f'<div style="border:2.5px solid #000;border-radius:40px;padding:22px 10px;text-align:center;font-family:Oswald;font-weight:700;text-transform:uppercase;font-size:28px;line-height:1">{a}</div>' for a in AREAS)
    # three ensemble checklists side by side (band, choir, orchestra), rendered from the full PDF pages
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div>'
        f'<div class="hd" style="font-size:72px;margin-top:18px">One checklist per ensemble</div>'
        f'<div class="sub" style="font-size:27px;margin-top:8px">Band, choir and orchestra versions of the same six skills</div>'
        f'<div style="display:flex;gap:26px;margin-top:34px">{shots(["f6.png", "f7.png", "f8.png"], ["Band", "Choir", "Orchestra"], 296)}</div>'
        f'<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:18px;width:900px;margin-top:56px">{pills}</div>'
        f'<div class="band">{N_TICKS_ENS} tick boxes each <em>·</em> six skills <em>·</em> totals out of {MAX_TOTAL}</div></div>')


def preview_square_2():
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div>'
        f'<div class="hd" style="font-size:70px;margin-top:20px">Rubric and goal sheet</div>'
        f'<div class="sub" style="font-size:27px;margin-top:8px">Four levels, scores out of {MAX_TOTAL}, then a SMART goal</div>'
        f'<div style="display:flex;gap:36px;margin-top:40px">{shots(["pv3.png", "pv4.png"], ["4-level rubric", "Goal sheet"], 455)}</div>'
        f'<div class="band">Score bands <em>·</em> next steps <em>·</em> practice plan</div></div>')


def preview_square_3():
    cards = [("Cover", "1", "Stage, lights and snowflakes."), ("Teacher Guide", pgs("guide"), "How to use, scoring, differentiation."),
             ("My Concert", pgs("concert"), "Ensemble, pieces, feelings, proud moment."), ("Band", pgs("self"), f"{N_TICKS_ENS} tick statements in 6 skills."),
             ("Choir", str(pg("self", 1)), f"{N_TICKS_ENS} tick statements in 6 skills."), ("Orchestra", str(pg("self", 2)), f"{N_TICKS_ENS} tick statements in 6 skills."),
             ("Rubric", pgs("rubric"), f"4 levels, {len(AREAS)} areas, total {MIN_TOTAL}–{MAX_TOTAL}."), ("Etiquette", pgs("etiq"), f"{N_ETIQ} items: performer and audience."),
             ("Looking Back", pgs("look"), "Grades 4–6 and grades 7–12 pages."), ("Goal Sheet", pgs("goal"), "SMART goal, steps, practice plan."),
             ("Class Tally", pgs("tally"), f"{TALLY_ROWS} students, bands and counts."), ("Terms", pgs("terms"), "License and credits.")]
    cs = "".join(f'<div class="dc"><div class="dn">PAGE {p}</div><div class="dt">{escape(t)}</div><div class="df">{escape(d)}</div></div>' for t, p, d in cards)
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div>'
        f'<div class="hd" style="font-size:66px;margin-top:16px">What is inside</div>'
        f'<div class="sub" style="font-size:27px;margin-top:8px">{TOTAL_PAGES} printable pages, US Letter</div>'
        f'<div style="display:flex;flex-wrap:wrap;gap:18px;width:900px;margin-top:34px;justify-content:center">{cs}</div>'
        f'<div class="band">Grades 4–12 <em>·</em> band <em>·</em> choir <em>·</em> orchestra</div></div>')


def cover_square():
    return sq_doc(cover_inner(1000))


# ------------------------------------------------------------------ listing files
def upload_md():
    inside = "\n".join(f"• {t} ({n} page{'s' if n > 1 else ''})" for _, t, n, _ in SECTIONS)
    return f"""# UPLOAD: Winter Concert Reflection and Self-Assessment (TpT 046)

These fields follow the order of TpT's "Add a resource" form. Non-denominational: list in November or early December (queue: December).

**Files to attach**
- Resource (digital download): `{SLUG}.pdf`, {TOTAL_PAGES} pages, US Letter.
- Thumbnails, in this order: `cover.png`, `preview-1.png`, `preview-2.png`, `preview-3.png` (all 2000 × 2000).
- Preview file: `{SLUG}-PREVIEW.pdf`, 4 watermarked pages.

## 1. Title

```
{LISTING_TITLE}
```
({len(LISTING_TITLE)} characters; the limit is 80.) The title leaves out winter, holiday and concert-season words because TpT's Seasonal Titles notice blocked a seasonal title on 027. If TpT accepts it, "Winter Concert Reflection and Self-Assessment | Band Choir Orchestra Rubric Gr 4-12" is the preferred title.

## 2. Description

```
Winter Concert Reflection and Self-Assessment: {TOTAL_PAGES} printable pages for grades 4-12 that help band, choir and orchestra students look back on a concert, score their own work with a 4-level rubric and set a goal for next time. The wording is non-denominational, so it fits any school's winter or December concert.

WHAT'S INCLUDED ({TOTAL_PAGES} pages, PDF, US Letter)
{inside}

HOW IT WORKS
Students fill in a My Concert page, tick statements on a checklist for their ensemble, and turn the ticks in each of six skill areas (tone, rhythm, pitch and intonation, dynamics, teamwork, concert etiquette) into a level from 1 to 4. The six levels add up to a total from {MIN_TOTAL} to {MAX_TOTAL}, with four score bands. Each ensemble checklist has {N_TICKS_ENS} tick statements ({N_TICKS_ALL} across the three versions). The etiquette page has {N_ETIQ} statements. Students then finish a Looking Back page, a goal sheet with a SMART goal, next steps and a practice plan.

FOR TEACHERS
The teacher guide explains scoring with a worked example, differentiation for grades 4-6 and grades 7-12, and conferencing tips. Use the rubric to score the same six areas yourself and compare. The class summary sheet has rows for {TALLY_ROWS} students, class averages and band counts. About {STUDENT_MINUTES} minutes of student time in all.

• Grades 4-12
• Print in black and white
• No songs, lyrics or copyrighted characters
• Answer Key: Not Included (the rubric and worked example cover scoring)

{DISCLOSURE}
```

## 3. Grades

{", ".join(g.split("-")[0] for g in GRADES)} (also useful for the grades in between)

## 4. Subjects and tags

- Subjects: {", ".join(SUBJECTS)}
- Tags: {", ".join(TAGS)}

## 5. Price

${PRICE}
"""


def tpt_json():
    return {"price": PRICE, "license_price": PRICE, "tax_code": "Other Digital Goods - No Physical Media", "grades": GRADES,
            "subjects": SUBJECTS, "tags": TAGS, "formats": ["PDF"], "pages": TOTAL_PAGES, "answer_key": "Not Included",
            "files": {"product": f"{SLUG}.pdf", "preview": f"{SLUG}-PREVIEW.pdf", "thumb1": "cover.png", "thumb2": "preview-1.png",
                      "thumb3": "preview-2.png", "thumb4": "preview-3.png"}}


# ------------------------------------------------------------------ build
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


def write(name, text, folder=None):
    p = os.path.join(folder or BUILD, name)
    with open(p, "w") as f:
        f.write(text)
    return p


def build():
    os.makedirs(BUILD, exist_ok=True)
    full = write("resource.html", html_doc(full_pages(), "Concert Reflection"))
    prev = write("preview.html", html_doc(preview_pages(), "Preview"))
    render([{"html": full, "pdf": PDF}, {"html": prev, "pdf": PREVIEW_PDF}])
    for i in range(1, 5):
        subprocess.run(["pdftoppm", "-png", "-r", "110", "-f", str(i), "-l", str(i), "-singlefile", PREVIEW_PDF, os.path.join(BUILD, f"pv{i}")], check=True)
    for n in (pg("self"), pg("self", 1), pg("self", 2)):   # un-watermarked pages of the full PDF are never used as shots: use watermarked ones
        pass
    # shots of the three checklists come from the full PDF but get the preview watermark through a dedicated preview html
    allp = full_pages()
    wmpages = [re.sub(r'(<section [^>]*>)', r'\1<div class="wm">PREVIEW</div>', allp[pg("self", i) - 1], count=1) for i in range(3)]
    ws = write("shots.html", html_doc(wmpages, "Shots"))
    shots_pdf = os.path.join(BUILD, "shots.pdf")
    render([{"html": ws, "pdf": shots_pdf}])
    for i in range(3):
        subprocess.run(["pdftoppm", "-png", "-r", "110", "-f", str(i + 1), "-l", str(i + 1), "-singlefile", shots_pdf, os.path.join(BUILD, f"f{6 + i}")], check=True)
    sq = [write("cover.html", cover_square()), write("p1.html", preview_square_1()), write("p2.html", preview_square_2()), write("p3.html", preview_square_3())]
    render([{"html": h, "png": o, "width": 1000, "height": 1000, "scale": 2} for h, o in zip(sq, [COVER_PNG] + PREVIEW_PNGS)])
    write("UPLOAD.md", upload_md(), HERE)
    write("tpt.json", json.dumps(tpt_json(), indent=2) + "\n", HERE)
    print(f"built {PDF} ({TOTAL_PAGES} pages), preview PDF, cover + 3 previews, UPLOAD.md, tpt.json")


# ------------------------------------------------------------------ checks
OVERFLOW_JS = """
const { chromium } = require('playwright'); const url = require('url');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage();
  await p.goto(url.pathToFileURL(process.argv[2]).href, { waitUntil: 'load' });
  await p.evaluate(() => document.fonts.ready);
  const res = await p.evaluate(() => [...document.querySelectorAll('section.page')].map((s, i) => {
    const r = s.getBoundingClientRect(); let worst = 0, wide = 0, clear = 1e9;
    const ft = s.querySelector('.foot'); const fy = ft ? ft.getBoundingClientRect().top : null;
    for (const c of s.querySelectorAll('*')) {
      if (c.closest('.wm') || c.closest('.foot') || c.closest('.cvr') || (c.getAttribute('style')||'').startsWith('flex:1')) continue;
      const q = c.getBoundingClientRect(); if (q.width === 0 && q.height === 0) continue;
      worst = Math.max(worst, q.bottom - r.bottom); wide = Math.max(wide, q.right - r.right, r.left - q.left);
      if (fy !== null && c.children.length === 0 && c.textContent.trim().length + 0 >= 0 && q.height > 0) clear = Math.min(clear, fy - q.bottom);
    }
    const tbls = [...s.querySelectorAll('table')].map(t => { const w = t.getBoundingClientRect(); return [w.left - r.left, r.right - w.right]; });
    return [i + 1, worst, wide, clear, fy === null ? -1 : 0];
  }));
  console.log(JSON.stringify(res)); await b.close();
})();
"""


def overflow_check():
    js = os.path.join(BUILD, "overflow.js")
    open(js, "w").write(OVERFLOW_JS)
    out = subprocess.run(["node", js, os.path.join(BUILD, "resource.html")], capture_output=True, text=True, env=node_env())
    if out.returncode:
        return [f"overflow check failed to run: {out.stderr[-300:]}"], 0
    res = json.loads(out.stdout.strip().splitlines()[-1])
    errs = []
    for n, worst, wide, clear, hasfoot in res:
        if n > 1 and (worst > 0.5 or wide > 0.5):
            errs.append(f"PDF page {n}: content runs {worst:.1f}px past the bottom / {wide:.1f}px past a side")
        if n > 1 and hasfoot == 0 and clear < 6:
            errs.append(f"PDF page {n}: content comes within {clear:.1f}px of the footer rule (needs 6px clearance)")
    return errs, len(res)


def pdf_fonts(path):
    out = subprocess.run(["pdffonts", path], capture_output=True, text=True, check=True).stdout.splitlines()[2:]
    return [(l.split()[0], l.split()[-5]) for l in out]


def sections(html):
    return {int(m.group(1)): (m.group(2), m.group(0)) for m in re.finditer(r'<section class="page[^"]*" data-pg="(\d+)" data-key="(\w+)".*?</section>', html, re.S)}


def verify_data():
    errs = []
    if set(STATEMENTS) != {"Band", "Choir", "Orchestra"}:
        errs.append("ensembles wrong")
    for e, rows in STATEMENTS.items():
        if len(rows) != len(AREAS):
            errs.append(f"{e}: {len(rows)} areas")
        for ai, r in enumerate(rows):
            if len(r) != STMT_PER_AREA or len(set(r)) != STMT_PER_AREA:
                errs.append(f"{e} {AREAS[ai]}: statements wrong")
            for s in r:
                if " and " in s.lower() and s.count(" and ") > 1:
                    errs.append(f"{e}: statement may hold two ideas: {s}")
                if not s.endswith("."):
                    errs.append(f"{e}: statement without a full stop: {s}")
    if len(RUBRIC) != len(AREAS) or any(len(r) != len(LEVELS) for r in RUBRIC):
        errs.append("rubric is not 6 areas x 4 levels")
    # bands: contiguous, start at the minimum, end at the maximum, every total in exactly one band
    if BANDS[0][0] != MIN_TOTAL or BANDS[-1][1] != MAX_TOTAL or any(BANDS[i][1] + 1 != BANDS[i + 1][0] for i in range(len(BANDS) - 1)):
        errs.append("bands are not contiguous over the total range")
    for t in range(MIN_TOTAL, MAX_TOTAL + 1):
        if sum(1 for a, b, _ in BANDS if a <= t <= b) != 1:
            errs.append(f"total {t} is in {sum(1 for a, b, _ in BANDS if a <= t <= b)} bands")
    # a student who ticks everything / nothing reaches the extremes
    if sum(level_from_ticks(0) for _ in AREAS) != MIN_TOTAL or sum(level_from_ticks(STMT_PER_AREA) for _ in AREAS) != MAX_TOTAL:
        errs.append("tick-to-level mapping does not reach the minimum and maximum totals")
    if STMT_PER_AREA + 1 != len(LEVELS):
        errs.append("tick counts and levels do not line up")
    if EX_TOTAL != sum(t + 1 for t in EX_TICKS) or EX_TOTAL != 19 or EX_BAND != "Proficient":
        errs.append(f"worked example total {EX_TOTAL} / {EX_BAND} wrong")
    if STUDENT_MINUTES != 8 + 10 + 7 + 10 + 10:
        errs.append("minutes do not add up")
    if sum(s[2] for s in SECTIONS) != TOTAL_PAGES or TOTAL_PAGES != 14:
        errs.append(f"page total {TOTAL_PAGES}")
    return errs


def verify_html():
    errs = []
    p = os.path.join(BUILD, "resource.html")
    if not os.path.exists(p):
        return ["build/resource.html missing: run gen.py first"], ""
    html = open(p).read()
    secs = sections(html)
    if sorted(secs) != list(range(1, TOTAL_PAGES + 1)):
        errs.append(f"page numbers in html: {sorted(secs)}")
    for k, _, n, _ in SECTIONS:
        have = [i for i, (kk, _) in secs.items() if kk == k]
        if len(have) != n or (have and sorted(have) != list(range(pg(k), pg(k) + n))):
            errs.append(f"section {k}: pages {sorted(have)}, expected {n} from {pg(k)}")
    # self-assessment pages: tick boxes counted from the html, mapped to the data
    for ei, e in enumerate(ENSEMBLES):
        body = secs[pg("self", ei)][1]
        stmts = re.findall(r'<div class="stmt" data-self="(\w+)"><span class="cb" ></span><span>([^<]+)</span>', body)
        if len(stmts) != N_TICKS_ENS or {s[0] for s in stmts} != {e}:
            errs.append(f"{e} page: {len(stmts)} tick statements, expected {N_TICKS_ENS}")
        want = [escape(s) for r in STATEMENTS[e] for s in r]
        if [s[1] for s in stmts] != want:
            errs.append(f"{e} page: statements differ from the data")
        if body.count('class="cb"') != N_TICKS_ENS:
            errs.append(f"{e} page: {body.count('class=\"cb\"')} checkboxes, expected {N_TICKS_ENS}")
        rows = re.findall(r'<tr data-area="(\d)">', body)
        if rows != [str(i) for i in range(len(AREAS))]:
            errs.append(f"{e} page: area rows {rows}")
        for ai, area in enumerate(AREAS):
            m = re.search(rf'<tr data-area="{ai}"><td class="k">([^<]+)</td>(.*?)</tr>', body, re.S)
            if not m or m.group(1) != area or m.group(2).count('class="stmt"') != STMT_PER_AREA:
                errs.append(f"{e} page: area {area} does not have {STMT_PER_AREA} statements")
        for t in range(STMT_PER_AREA + 1):   # the printed conversion line
            if f"{t} {'tick' if t == 1 else 'ticks'} = level {t + 1}" not in body:
                errs.append(f"{e} page: conversion for {t} ticks missing or wrong")
        if f"out of {MAX_TOTAL} (add the {len(AREAS)} levels)" not in body:
            errs.append(f"{e} page: total line wrong")
        for a, b, n in BANDS:
            if f"{a}–{b} {n}" not in body:
                errs.append(f"{e} page: band {n} missing")
    # rubric
    rb = secs[pg("rubric")][1]
    rrows = re.findall(r'<tr data-area="(\d)"><td class="k">([^<]+)</td>((?:<td>[^<]+</td>){4})</tr>', rb)
    if len(rrows) != len(AREAS) or [r[1] for r in rrows] != AREAS:
        errs.append(f"rubric rows: {[r[1] for r in rrows]}")
    for r in rrows:
        if r[2].count("<td>") != len(LEVELS):
            errs.append(f"rubric row {r[1]}: {r[2].count('<td>')} descriptors")
    cols = re.search(r"<colgroup>(.*?)</colgroup>", rb, re.S).group(1)
    widths = [float(w) for w in re.findall(r"width:([\d.]+)%", cols)]
    if len(widths) != 5 or len(set(widths[1:])) != 1 or abs(sum(widths) - 100) > 0.01:
        errs.append(f"rubric columns not equal / not 100%: {widths}")
    if f"total from {MIN_TOTAL} to {MAX_TOTAL}" not in rb:
        errs.append("rubric: total range text missing")
    bt = re.search(r'data-bands="1">(.*?)</table>', rb, re.S).group(1)
    for a, b, n in BANDS:
        if f"{a}–{b}</th>" not in bt or f"<td class=c>{n}</td>" not in bt:
            errs.append(f"rubric band {n} {a}-{b} missing")
    # etiquette
    et = secs[pg("etiq")][1]
    if et.count('data-etiq="performer"') != len(PERFORMER_ETIQ) or et.count('data-etiq="audience"') != len(AUDIENCE_ETIQ):
        errs.append("etiquette item counts differ from the data")
    if f"There are {N_ETIQ} statements: {len(PERFORMER_ETIQ)} for performers and {len(AUDIENCE_ETIQ)} for audience members" not in et or N_ETIQ != 10:
        errs.append("etiquette count claim wrong")
    # looking back
    if secs[pg("look")][1].count('data-look="46"') != len(LOOK46) or secs[pg("look", 1)][1].count('data-look="712"') != len(LOOK712):
        errs.append("looking back item counts differ from the data")
    # goal sheet
    gl = secs[pg("goal")][1]
    if gl.count('data-goalarea="1"') != len(AREAS) or len(re.findall(r'data-smart="(\w)"', gl)) != 5 or "".join(re.findall(r'data-smart="(\w)"', gl)) != "SMART":
        errs.append("goal sheet: areas or SMART letters wrong")
    if gl.count('<td style="height:34pt"></td>') != NEXT_STEPS or f"My next steps ({NEXT_STEPS})" not in gl:
        errs.append("goal sheet: next-step rows differ from the claim")
    # tally
    tl = secs[pg("tally")][1]
    tbl = re.search(r'data-tally="1">(.*?)</table>', tl, re.S).group(1)
    if tl.count('data-row="1"') != TALLY_ROWS:
        errs.append(f"tally: {tl.count('data-row=\"1\"')} student rows, expected {TALLY_ROWS}")
    ncols = len(re.findall(r"<col ", tbl))
    first_row = re.search(r'<tr data-row="1">(.*?)</tr>', tbl, re.S).group(1)
    if ncols != 2 + len(AREAS) + 2 or first_row.count("<td") != ncols:
        errs.append(f"tally: {ncols} columns defined, {first_row.count('<td')} cells per row")
    ws = [float(w) for w in re.findall(r"width:([\d.]+)%", tbl)]
    area_w = ws[2:2 + len(AREAS)]
    if len(set(area_w)) != 1 or abs(sum(ws) - 100) > 0.01:
        errs.append(f"tally: area columns not equal or widths sum {sum(ws)}: {ws}")
    if tl.count('data-band="1"') != len(BANDS):
        errs.append("tally: band rows wrong")
    # teacher guide claims
    g = secs[pg("guide")][1] + secs[pg("guide", 1)][1]
    for need in (f"{N_TICKS_ENS} tick boxes per page", f"= {EX_TOTAL} out of {MAX_TOTAL}", f"About {STUDENT_MINUTES} minutes",
                 f"total from {MIN_TOTAL} to {MAX_TOTAL}", f"What is inside ({TOTAL_PAGES} pages)", "Level = ticks + 1"):
        if need not in g:
            errs.append(f"teacher guide: missing '{need}'")
    ex = re.findall(r'<td>(Tone|Rhythm|Pitch and Intonation|Dynamics|Teamwork|Concert Etiquette)</td><td class="c">(\d)</td><td class="c">(\d)</td>', g)
    if len(ex) != 6 or sum(int(t) + 1 for _, t, _ in ex) != EX_TOTAL or any(int(t) + 1 != int(l) for _, t, l in ex):
        errs.append("worked example rows wrong")
    if f"<td class=\"c\"><b>{EX_TOTAL}</b></td>" not in g:
        errs.append("worked example total cell wrong")
    pm = re.findall(r'<tr><td>([\d-]+)</td><td>([^<]+)</td><td class="c">(\d+)</td></tr>', g)
    if sum(int(x[2]) for x in pm) != TOTAL_PAGES:
        errs.append(f"page map in the guide adds to {sum(int(x[2]) for x in pm)}, expected {TOTAL_PAGES}")
    for rng, _, n in pm:
        a, _, b = rng.partition("-")
        if int(b or a) - int(a) + 1 != int(n):
            errs.append(f"page map row {rng}: count {n} does not match the range")
    return errs, html


def verify_files():
    errs = []
    from pypdf import PdfReader
    from PIL import Image
    for p in [PDF, PREVIEW_PDF, COVER_PNG, *PREVIEW_PNGS, UPLOAD, TPT_JSON]:
        if not os.path.exists(p):
            errs.append(f"missing {os.path.basename(p)}")
    if errs:
        return errs
    for path, want in ((PDF, TOTAL_PAGES), (PREVIEW_PDF, 4)):
        rd = PdfReader(path)
        if len(rd.pages) != want:
            errs.append(f"{os.path.basename(path)}: {len(rd.pages)} pages, expected {want}")
        for i, pgx in enumerate(rd.pages):
            if abs(float(pgx.mediabox.width) - 612) > 1 or abs(float(pgx.mediabox.height) - 792) > 1:
                errs.append(f"{os.path.basename(path)} p{i + 1}: not US Letter")
        fonts = pdf_fonts(path)
        for name, emb in fonts:
            if emb != "yes":
                errs.append(f"{os.path.basename(path)}: font {name} not embedded")
        names = " ".join(n for n, _ in fonts).lower().replace(" ", "")
        for fam in ("oswald", "sourcesans3"):
            if fam not in names:
                errs.append(f"{os.path.basename(path)}: {fam} missing")
    rd = PdfReader(PDF)
    texts = [(pgx.extract_text() or "") for pgx in rd.pages]
    for i, t in enumerate(texts):
        if len(t.strip()) < 40:
            errs.append(f"PDF page {i + 1} looks blank")
        if "PREVIEW" in t:
            errs.append(f"PDF page {i + 1} carries a watermark")
    for i, pgx in enumerate(PdfReader(PREVIEW_PDF).pages):
        t = pgx.extract_text() or ""
        if t.count("PREVIEW") != 1:
            errs.append(f"preview PDF page {i + 1}: PREVIEW appears {t.count('PREVIEW')} times")
    prev_html = open(os.path.join(BUILD, "preview.html")).read()
    if prev_html.count('class="wm"') != 4:
        errs.append("preview.html: expected 4 watermarks")
    for h in ("p1.html", "p2.html", "p3.html", "cover.html"):
        if "swm" in open(os.path.join(BUILD, h)).read() or open(os.path.join(BUILD, h)).read().count('class="wm"') != 0:
            errs.append(f"{h}: a second watermark layer")
    for p in [COVER_PNG, *PREVIEW_PNGS]:
        if Image.open(p).size != (2000, 2000):
            errs.append(f"{os.path.basename(p)}: not 2000x2000")
        im = Image.open(p).convert("L")
        # blank-band scan: no horizontal band of 90 px that is pure white inside the central 80 percent, below the store line
        px = im.load()
        run = 0
        for y in range(150, 1860):
            white = all(px[x, y] > 250 for x in range(200, 1800, 4))
            run = run + 1 if white else 0
            if run > 190:
                errs.append(f"{os.path.basename(p)}: blank band near y={y}")
                break
    cover_text = open(os.path.join(BUILD, "cover.html")).read()
    if f"{TOTAL_PAGES} pages" not in cover_text:
        errs.append("cover badge page count differs from the PDF")
    up = open(UPLOAD).read()
    m = re.search(r"^## 1\. Title\s*\n+```\n(.+?)\n```", up, re.M | re.S)
    title = m.group(1).strip() if m else ""
    if not title or len(title) > 80 or title != LISTING_TITLE:
        errs.append(f"UPLOAD.md title problem ({len(title)} chars)")
    for bad in ("december", "winter", "holiday", "christmas", "hanukkah", "kwanzaa", "seasonal", "concert"):
        if bad in title.lower():
            errs.append(f"title contains {bad!r}")
    inc = re.findall(r"^• (.+) \((\d+) pages?\)$", up, re.M)
    if sum(int(n) for _, n in inc) != TOTAL_PAGES or len(inc) != len(SECTIONS):
        errs.append(f"UPLOAD.md page list adds to {sum(int(n) for _, n in inc)}, PDF has {TOTAL_PAGES}")
    for need in (DISCLOSURE, f"${PRICE}", f"{TOTAL_PAGES} pages", f"{N_TICKS_ENS} tick", f"total from {MIN_TOTAL} to {MAX_TOTAL}", f"{N_ETIQ} statements", "Answer Key: Not Included"):
        if need not in up:
            errs.append(f"UPLOAD.md missing '{need}'")
    if re.search(r"hand-checked|handmade|classroom-tested|checked by hand", up.lower()):
        errs.append("UPLOAD.md hand-checked claim")
    tj = json.load(open(TPT_JSON))
    tags, subs = load("TAG-OPTIONS.json")["options"], load("SUBJECT-OPTIONS.json")
    heads = {"Performing Arts", "Holiday", "Student Practice", "Theme", "Seasonal", "Audience", "Language", "Resource Type", "Instruction", "Student Assessment", "Teacher Tools"}
    if not 1 <= len(tj["tags"]) <= 6 or any(t not in tags or t in heads for t in tj["tags"]):
        errs.append(f"tags invalid: {tj['tags']}")
    if not 1 <= len(tj["subjects"]) <= 3 or any(s not in subs or s in heads for s in tj["subjects"]):
        errs.append("subjects invalid")
    if not 1 <= len(tj["grades"]) <= 4:
        errs.append("grades must be 1-4 entries")
    if tj["pages"] != TOTAL_PAGES or tj["price"] != PRICE or tj["license_price"] != PRICE:
        errs.append("tpt.json pages or price wrong")
    for fn in tj["files"].values():
        if not os.path.exists(os.path.join(HERE, fn)):
            errs.append(f"tpt.json file {fn} missing")
    alltext = " ".join(texts).lower()
    for bad in ("christmas", "hanukkah", "kwanzaa", "santa", "menorah", "nativity", "church", "manger", "carol", "jesus", "prayer"):
        if re.search(r"\b" + bad + r"\b", alltext):
            errs.append(f"product text contains '{bad}'")
    if not re.search(r"\bwinter\b", alltext):
        errs.append("no winter wording in the product")
    return errs


def load(name):
    return json.load(open(os.path.join(TPT, name)))


def check():
    errs = verify_data()
    e2, _ = verify_html()
    errs += e2
    errs += verify_files()
    oe, npg = overflow_check()
    errs += oe
    if errs:
        print("CHECK FAILED")
        print("\n".join(" - " + e for e in errs[:60]))
        sys.exit(1)
    print(f"CHECK OK: {TOTAL_PAGES} pages; {N_TICKS_ALL} checklist statements ({N_TICKS_ENS} per ensemble, counted in the html); "
          f"levels 1-{len(LEVELS)}, totals {MIN_TOTAL}-{MAX_TOTAL}, {len(BANDS)} bands cover every total once; worked example {EX_TOTAL} ({EX_BAND}); "
          f"rubric {len(AREAS)}x{len(LEVELS)} with equal columns; tally {TALLY_ROWS} rows with equal area columns; page map and UPLOAD list total {TOTAL_PAGES}; "
          f"no page overflows or touches the footer ({npg} pages); preview 4 pages one watermark each; fonts embedded; images 2000x2000; tpt.json ok.")


if __name__ == "__main__":
    if "--check" in sys.argv:
        check()
    else:
        build()
