#!/usr/bin/env python3
"""Concert Etiquette Lesson and Posters (TpT 054): build the resource and verify it.

    python3 gen.py           build everything (PDFs, PNGs, UPLOAD.md, tpt.json) into this folder
    python3 gen.py --check   re-read the rendered pages and verify every count, cross-reference, icon and the layout

--check does not trust the lists in this file. It loads the rendered HTML in Chromium and reads back what is really on the pages
(every poster, checklist item, exit ticket question, lesson step, page reference and icon box), then recomputes from that.

Rendering uses Playwright + Chromium (HTML/SVG -> PDF/PNG) with the OFL fonts in ../fonts.
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
ART = os.path.join(HERE, "art")
RENDER_JS = os.path.join(TPT, "tools", "render.js")

SLUG = "concert-etiquette-lesson-and-posters"
PDF = os.path.join(HERE, f"{SLUG}.pdf")
PREVIEW_PDF = os.path.join(HERE, f"{SLUG}-PREVIEW.pdf")
COVER_PNG = os.path.join(HERE, "cover.png")
PREVIEW_PNGS = [os.path.join(HERE, f"preview-{i}.png") for i in (1, 2, 3)]
UPLOAD = os.path.join(HERE, "UPLOAD.md")
TPT_JSON = os.path.join(HERE, "tpt.json")

STORE = "Brian Lotze"
BRAND = "Hudson Beat"
YEAR = 2026
ACCENT = "#2F7FBF"      # one accent: a deeper shade of the library art's icy blue
TINT = "#DCEBF7"        # pale tint of the accent
DISCLOSURE = "Created with the help of digital and AI tools. Notation and answer keys are verified before release."
TITLE = "Concert Etiquette"
LISTING_TITLE = "Concert Etiquette Lesson & Posters | Audience Checklist Exit Ticket Gr 3-8"
PRICE = "4.00"
TAGS = ["Posters", "Lessons", "Printables", "Classroom Management", "Social Skills", "Assessment"]
SUBJECTS = ["Music", "Instrumental Music", "Vocal Music"]
GRADES = ["4th-grade", "5th-grade", "6th-grade", "7th-grade"]

# ------------------------------------------------------------------ content
# The six poster habits. Posters, the lesson, both checklists and the notes all read from this one list.
POSTERS = [
    dict(key="early", head="Arrive early and quietly", icon="clock",
         sub="Find your seat before the music starts. Walk, do not run, and use a quiet voice.",
         rem="Quiet arrivals help everyone get ready to listen."),
    dict(key="phone", head="Silence phones", icon="phone",
         sub="Turn off the sound and the buzz, then put your phone away. Lights and noises can distract performers and the people near you.",
         rem="Phones away means eyes and ears on the music."),
    dict(key="clap", head="Clap at the right time", icon="clap",
         sub="Listen for the end of the piece, then clap when the music has stopped. Watch for cues from your director or the announcer.",
         rem="Customs differ by place, so watch for cues."),
    dict(key="seat", head="Stay seated until the music ends", icon="chair",
         sub="Stay in your seat until the performance is over. If you must leave, go quietly between pieces.",
         rem="A calm room lets the last note ring."),
    dict(key="respect", head="Be a respectful audience", icon="heart",
         sub="Listen with your eyes and ears, keep your voice low, and cheer kindly for every group.",
         rem="Every performer deserves your full attention."),
    dict(key="perf", head="Performers: ready, focused, kind", icon="star",
         sub="Ready: warm up and be on time. Focused: watch your director. Kind: support the people performing with you.",
         rem="A good performance is a team effort."),
]
NPOST = len(POSTERS)

AUDIENCE = [  # (text, poster index or None, word that poster must contain)
    ("I arrived early and found my seat quietly.", 0, "early"),
    ("I silenced my phone and put it away.", 1, "phone"),
    ("I listened quietly while the music was playing.", 4, "listen"),
    ("I waited until a piece ended before I clapped.", 2, "clap"),
    ("I cheered kindly for every group.", 4, "cheer"),
    ("I stayed seated until the music ended, or stepped out quietly between pieces.", 3, "seat"),
    ("I kept my voice low and my belongings out of the way.", 4, "voice"),
    ("I thanked a performer or my director after the concert.", None, ""),
]
PERFORMER = [  # (group, text)
    ("Ready", "I warmed up and had my music and materials ready."),
    ("Ready", "I arrived on time and dressed as my director asked."),
    ("Ready", "I knew where to enter, where to stand and when to exit."),
    ("Focused", "I watched my director and listened to my section."),
    ("Focused", "I stayed still and quiet between pieces."),
    ("Focused", "I kept going calmly when something did not go as planned."),
    ("Kind", "I encouraged a fellow performer before or after we performed."),
    ("Kind", "I smiled or bowed when the music ended and thanked the audience."),
]
NAUD, NPERF = len(AUDIENCE), len(PERFORMER)
GROUP_COUNTS = {g: sum(1 for x, _ in PERFORMER if x == g) for g in ("Ready", "Focused", "Kind")}
PERF_POSTER = NPOST - 1

STEPS = [  # (name, minutes)
    ("Hook", 3), ("The six habits", 6), ("Discuss", 4), ("Think-pair-share", 3), ("Show me", 5), ("Exit ticket", 2),
]
NSTEPS = len(STEPS)
LESSON_MIN = sum(m for _, m in STEPS)

DISCUSS = [
    "Why does a performer do their best work in a quiet room?",
    "What can happen to the music when a phone buzzes or someone whispers?",
    "How might it feel to look out and see an audience that is listening closely?",
    "In some places, people clap or cheer during the music. Why might customs be different from place to place?",
    "What can you do if you need to cough, sneeze or step out during a concert?",
]
NDISC = len(DISCUSS)

VOCAB = [("audience", "the people who watch and listen to a performance"),
         ("performer", "a person who sings, plays or speaks for an audience"),
         ("applause", "clapping or cheering to show thanks and enjoyment"),
         ("cue", "a signal, such as a nod from the director, that tells everyone what happens next"),
         ("venue", "the place where a concert happens, such as a gym, a hall or a park"),
         ("etiquette", "the customs for polite, respectful behavior in a certain situation")]

ROLES = [
    ("A", "You arrive just as the concert is starting.", "Show how to enter quietly and find a seat, or wait at the back for a pause between pieces."),
    ("B", "Your phone buzzes during a soft piece.", "Show how to silence it quickly and put it away without a fuss."),
    ("C", "A piece ends, and you are not sure whether to clap.", "Show how to watch the director and the rest of the audience for a cue."),
    ("D", "You are a performer, and the last note has just ended.", "Show how to stay focused, smile or bow, and wait for your director's cue."),
]
NROLE = len(ROLES)

EXIT_Q = [
    dict(kind="mc", text="When is it usual to clap at a school concert?",
         opts=[("A", "In a quiet moment in the middle of a piece."),
               ("B", "After a piece has ended and the music has stopped."),
               ("C", "Never. Clapping is not allowed at concerts.")], correct="B"),
    dict(kind="open", text="Name two ways an audience member can help the performers do their best."),
    dict(kind="open", text="You are performing and you make a mistake. What is one calm, kind thing you can do next?"),
]
NQ = len(EXIT_Q)

# ------------------------------------------------------------------ page map
P_COVER, P_TEACH, P_GLANCE, P_SCR1, P_SCR2, P_TPS = 1, 2, 3, 4, 5, 6
P_POST0 = 7
P_AUD = P_POST0 + NPOST           # 13
P_PERF = P_AUD + 1                # 14
P_EXIT = P_PERF + 1               # 15
P_KEY = P_EXIT + 1                # 16
P_TERMS = P_KEY + 1               # 17
TOTAL_PAGES = P_TERMS
PAGEOF = {"cover": P_COVER, "teacher": P_TEACH, "glance": P_GLANCE, "script1": P_SCR1, "script2": P_SCR2, "tps": P_TPS,
          "audience": P_AUD, "performer": P_PERF, "exit": P_EXIT, "key": P_KEY, "terms": P_TERMS}
for _i in range(NPOST):
    PAGEOF[f"poster{_i + 1}"] = P_POST0 + _i
PAGE_NAMES = {"cover": "Cover", "teacher": "Teacher Notes", "glance": "Lesson at a Glance", "script1": "Teacher Script, Steps 1 to 3",
              "script2": "Teacher Script, Steps 4 to 6", "tps": "Think-Pair-Share", "audience": "Audience Checklist",
              "performer": "Performer Checklist", "exit": "Exit Ticket", "key": "Exit Ticket Answer Key", "terms": "Terms of Use"}
for _i, _p in enumerate(POSTERS):
    PAGE_NAMES[f"poster{_i + 1}"] = f"Poster {_i + 1} of {NPOST}"
STEP_PAGE = {1: P_SCR1, 2: P_SCR1, 3: P_SCR1, 4: P_SCR2, 5: P_SCR2, 6: P_SCR2}


def R(kind, cap=False):
    """A page reference that --check reads back and compares with where that page really is."""
    return f'<span data-ref="{kind}" data-n="{PAGEOF[kind]}">{"Page" if cap else "page"} {PAGEOF[kind]}</span>'


def RR(k1, k2, cap=False):
    return (f'<span data-ref="{k1}" data-n="{PAGEOF[k1]}" data-ref2="{k2}" data-n2="{PAGEOF[k2]}">'
            f'{"Pages" if cap else "pages"} {PAGEOF[k1]}–{PAGEOF[k2]}</span>')


def stepref(n):
    return f'<span data-stepref="{n}">Step {n}</span>'


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
.tag.key .lv { background: ACCENT; }
.tag .ln { font-family: 'Oswald'; font-weight: 300; font-size: 11pt; margin-top: 3pt; }
.name { display: flex; gap: 14pt; font-size: 12pt; margin: 9pt 0 7pt; align-items: flex-end; }
.name span { flex: 1; border-bottom: 1pt solid #000; height: 15pt; }
.name span.s { flex: 0 0 1.3in; }
.foot { display: flex; justify-content: space-between; font-size: 8.5pt; color: #333; border-top: .8pt solid #000; padding-top: 3pt; }
.wm { position: absolute; left: 50%; top: 50%; transform: translate(-50%, -50%) rotate(-38deg); font-family: 'Oswald'; font-weight: 700;
      font-size: 150pt; color: rgba(0,0,0,.13); letter-spacing: .06em; white-space: nowrap; pointer-events: none; z-index: 9; }
.fill { flex: 1; }
.how { font-size: 11.5pt; margin: 2pt 0 6pt; line-height: 1.3; text-wrap: pretty; }
.row2 { display: flex; gap: 12pt; margin-top: 8pt; }
.box { border: 1.3pt solid #000; border-radius: 7pt; padding: 6pt 10pt 8pt; flex: 1; }
.box .bt { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 11.5pt; letter-spacing: .02em; margin-bottom: 2pt; }
.rl { border-bottom: 1pt solid #000; height: 21pt; }
.doc h1 { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 30pt; margin: 0 0 4pt; line-height: 1; }
.doc h2 { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 13.5pt; margin: 11pt 0 4pt; letter-spacing: .02em; }
.doc p, .doc li { font-size: 11pt; line-height: 1.36; margin: 0 0 5pt; text-wrap: pretty; }
.doc ul, .doc ol { margin: 0 0 4pt; padding-left: 16pt; }
.doc .rule { border-bottom: 2.2pt solid #000; margin-bottom: 8pt; padding-bottom: 6pt; }
.doc table.dt { border-collapse: collapse; width: 100%; table-layout: fixed; font-size: 10pt; margin: 2pt 0 4pt; }
.doc table.dt td, .doc table.dt th { border: 1pt solid #000; padding: 3pt 6pt; text-align: left; vertical-align: top; }
.doc table.dt th { font-family: 'Oswald'; font-weight: 500; text-transform: uppercase; font-size: 9.5pt; background: #000; color: #fff; }
.cols { display: flex; gap: 20pt; }
.cols > div { flex: 1; min-width: 0; }
.small { font-size: 9.5pt !important; color: #333; }
/* lesson script */
.sh { display: flex; align-items: center; gap: 9pt; margin: 9pt 0 4pt; }
.sh .n { flex: 0 0 24pt; background: ACCENT; color: #fff; font-family: 'Oswald'; font-weight: 700; font-size: 14pt; border-radius: 50%; width: 24pt; height: 24pt; line-height: 24pt; text-align: center; }
.sh .st { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 14.5pt; letter-spacing: .02em; flex: 1; }
.sh .mn { font-family: 'Oswald'; font-weight: 500; font-size: 11pt; border: 1.2pt solid #000; border-radius: 10pt; padding: 1pt 8pt 2pt; }
.say { border-left: 3pt solid ACCENT; background: #F4F8FC; padding: 4pt 10pt 4pt 10pt; margin: 0 0 5pt; font-size: 11pt; line-height: 1.36; font-style: italic; }
.do { font-size: 11pt; line-height: 1.36; margin: 0 0 5pt; }
.do b, .say b { font-style: normal; font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 9.5pt; letter-spacing: .06em; color: ACCENT; margin-right: 4pt; }
ol.dq { margin: 2pt 0 5pt; padding-left: 20pt; }
ol.dq li { font-size: 11pt; line-height: 1.34; margin: 0 0 3pt; }
.rolegrid { display: grid; grid-template-columns: 1fr 1fr; gap: 8pt; margin: 4pt 0 4pt; }
.rc { border: 1.3pt solid #000; border-radius: 7pt; padding: 5pt 9pt 6pt; display: flex; gap: 8pt; }
.rc .lt { flex: 0 0 22pt; background: #000; color: #fff; font-family: 'Oswald'; font-weight: 700; font-size: 13pt; width: 22pt; height: 22pt; line-height: 22pt; text-align: center; border-radius: 4pt; }
.rc p { margin: 0; font-size: 10.5pt; line-height: 1.3; }
.rc p b { font-weight: 700; }
.tps { display: flex; gap: 10pt; margin: 8pt 0 6pt; }
.tps .c { flex: 1; border: 1.3pt solid #000; border-radius: 7pt; padding: 6pt 10pt 8pt; }
.tps .c .bt { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 13pt; letter-spacing: .03em; }
.tps .c .bt small { font-weight: 300; text-transform: none; font-size: 11pt; margin-left: 4pt; }
.tps .c p { margin: 2pt 0 0; font-size: 10pt; line-height: 1.25; }
/* posters */
.poster { align-items: center; justify-content: space-between; text-align: center; padding: 0.42in 0.6in 0.38in; }
.poster .pk { font-family: 'Oswald'; font-weight: 500; text-transform: uppercase; letter-spacing: .26em; font-size: 12pt; }
.poster > * { flex-shrink: 0; }
.poster .pt { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 72pt; line-height: 1.02; padding: .1em 0 .3em; letter-spacing: .005em; width: 100%; margin-top: 6pt; }
.poster .pt.long { font-size: 62pt; }
.poster .pico { width: 3.5in; height: 3.5in; display: flex; align-items: center; justify-content: center; }
.poster .pico svg { width: 3.5in; height: 3.5in; display: block; }
.poster .psub { font-size: 22pt; line-height: 1.28; width: 100%; font-weight: 600; text-wrap: balance; }
.poster .prem { width: 100%; background: #000; color: #fff; font-family: 'Oswald'; font-weight: 500; font-size: 16pt; letter-spacing: .04em;
                text-transform: uppercase; padding: 9pt 14pt 10pt; border-radius: 5pt; line-height: 1.2; }
.poster .foot { width: 100%; margin-top: 10pt; }
/* checklists */
.ck { display: flex; align-items: center; gap: 12pt; border: 1.3pt solid #000; border-radius: 7pt; padding: 9pt 12pt; margin-bottom: 9pt; }
.ck .bx { flex: 0 0 22pt; width: 22pt; height: 22pt; border: 2pt solid #000; border-radius: 4pt; }
.ck .tx { flex: 1; font-size: 13pt; line-height: 1.25; font-weight: 600; }
.ck .rf { flex: 0 0 auto; font-family: 'Oswald'; font-weight: 500; text-transform: uppercase; font-size: 9pt; letter-spacing: .05em; text-align: right; color: #222; line-height: 1.25; }
.ck .gp { flex: 0 0 auto; background: ACCENT; color: #fff; font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 9.5pt; letter-spacing: .08em; border-radius: 10pt; padding: 1pt 8pt 2pt; min-width: 58pt; text-align: center; }
.ckh { display: flex; align-items: center; gap: 12pt; margin: 4pt 0 8pt; font-size: 12pt; line-height: 1.3; }
.ckh .sp { flex: 0 0 0.85in; height: 0.85in; display: flex; align-items: center; justify-content: center; padding: 0.06in; }
.ckh .sp img { max-width: 100%; max-height: 100%; display: block; }
/* exit ticket */
.tk { border: 1.6pt dashed #000; border-radius: 8pt; padding: 8pt 14pt 8pt; margin-bottom: 9pt; }
.tk .th { display: flex; justify-content: space-between; align-items: baseline; border-bottom: 1.6pt solid #000; padding-bottom: 3pt; }
.tk .th .h { font-size: 17pt; }
.tk .th .l { font-size: 10.5pt; }
.tk .q { font-size: 11.5pt; line-height: 1.3; margin: 6pt 0 2pt; font-weight: 600; }
.tk .q i { font-style: normal; font-family: 'Oswald'; font-weight: 700; color: ACCENT; margin-right: 3pt; }
.tk .op { font-size: 11pt; line-height: 1.25; margin: 1pt 0 1pt 14pt; display: flex; gap: 6pt; }
.tk .op b { flex: 0 0 14pt; font-family: 'Oswald'; font-weight: 700; }
.tk .nm { display: flex; gap: 14pt; font-size: 11pt; margin: 6pt 0 0; align-items: flex-end; }
.tk .nm span { flex: 1; border-bottom: 1pt solid #000; height: 13pt; }
.tk .nm span.s { flex: 0 0 1.1in; }
.tk .rl { height: 21pt; }
.kq { border: 1.3pt solid #000; border-radius: 7pt; padding: 7pt 12pt 8pt; margin-bottom: 9pt; }
.kq .kh { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 13pt; letter-spacing: .02em; margin-bottom: 3pt; }
.kq .kh i { font-style: normal; color: ACCENT; }
.kq p { margin: 0 0 4pt; font-size: 10.8pt; line-height: 1.34; }
.kq .ko { display: flex; gap: 6pt; font-size: 10.8pt; line-height: 1.3; margin: 1pt 0 1pt 10pt; }
.kq .ko b { flex: 0 0 14pt; font-family: 'Oswald'; font-weight: 700; }
.kq .ko.ok { background: TINT; border-radius: 4pt; padding: 1pt 4pt; margin-left: 6pt; }
.doc.big .say, .doc.big .do, .doc.big ol.dq li, .doc.big li { font-size: 12.5pt; line-height: 1.4; }
.doc.big .say, .doc.big .do { margin-bottom: 8pt; }
.doc.big .sh { margin: 14pt 0 6pt; }
.doc.big .rc p { font-size: 11.5pt; }
.cover { align-items: center; justify-content: space-between; padding: 0.55in 0.6in 0.5in; }
.store { font-family: 'Oswald'; font-weight: 500; font-size: 13pt; letter-spacing: .32em; text-transform: uppercase; }
.ctitle { text-align: center; }
.ctitle .a { font-family: 'Oswald'; font-weight: 700; font-size: 50pt; line-height: 1; letter-spacing: .02em; }
.ctitle .b { font-family: 'Oswald'; font-weight: 700; white-space: nowrap; font-size: 76pt; line-height: .95; letter-spacing: .01em; }
.ctitle .c { font-family: 'Oswald'; font-weight: 300; font-size: 17pt; margin-top: 8pt; }
.cband { width: 100%; background: #000; color: #fff; text-align: center; font-family: 'Oswald'; font-weight: 500; font-size: 14pt;
         letter-spacing: .08em; text-transform: uppercase; padding: 8pt 0 9pt; border-radius: 4pt; }
.cband em { font-style: normal; color: #8FC3EC; }
""".replace("ACCENT", ACCENT).replace("TINT", TINT)


def html_doc(pages, title="doc"):
    return (f'<!doctype html><html><head><meta charset="utf-8"><title>{escape(title)}</title>'
            f'<style>{font_css()}{CSS}</style></head><body>{"".join(pages)}</body></html>')


COPY = f"© {YEAR} {STORE} · {BRAND} · For single-classroom use"


def foot(right):
    return f'<div class="foot"><span>{COPY}</span><span>{right}</span></div>'


def page(kind, inner, wm=False, cls="", right=None):
    n = PAGEOF[kind]
    w = '<div class="wm">PREVIEW</div>' if wm else ""
    return (f'<section class="page {cls}" data-page="{n}" data-kind="{kind}" data-name="{escape(PAGE_NAMES[kind])}">{w}{inner}'
            f'{foot(right or f"Page {n}")}</section>')


def top(title, sub, tag, tagline, cls=""):
    return (f'<div class="top"><div class="h t">{title}<small>{sub}</small></div>'
            f'<div class="tag {cls}"><div class="lv">{tag}</div><div class="ln">{tagline}</div></div></div>')


# ------------------------------------------------------------------ icons (drawn in code; stroke 8 in a 200 x 200 box)
SW = 8


def icon(kind):
    s = f'stroke="#000" stroke-width="{SW}" stroke-linecap="round" stroke-linejoin="round"'
    if kind == "clock":
        body = (f'<circle cx="100" cy="100" r="72" fill="{TINT}"/><path d="M100 54 V100 L130 118" fill="none"/>'
                f'<circle cx="100" cy="100" r="6" fill="#000"/>')
    elif kind == "phone":
        body = (f'<rect x="60" y="24" width="80" height="152" rx="14" fill="#fff"/><path d="M60 54 H140 M60 146 H140" fill="none"/>'
                f'<line x1="38" y1="38" x2="162" y2="162" stroke="#fff" stroke-width="22"/>'
                f'<line x1="38" y1="38" x2="162" y2="162" stroke="{ACCENT}" stroke-width="{SW}"/>')
    elif kind == "clap":
        def hand(fill):
            fl = "".join(f'<rect x="{x}" y="{y}" width="15" height="{h}" rx="7.5" fill="{fill}"/>'
                         for x, y, h in ((18, 70, 60), (33, 56, 74), (48, 52, 78), (63, 60, 70)))
            th = f'<rect x="70" y="108" width="15" height="42" rx="7.5" transform="rotate(-38 77 150)" fill="{fill}"/>'
            palm = f'<rect x="18" y="104" width="60" height="56" rx="20" fill="{fill}"/>'
            return fl + palm
        body = (f'<g transform="translate(8 6) rotate(16 48 160)">{hand(TINT)}</g>'
                f'<g transform="translate(192 6) scale(-1 1) rotate(16 48 160)">{hand("#fff")}</g>'
                f'<path d="M100 14 V32 M62 22 L70 38 M138 22 L130 38" fill="none" stroke="{ACCENT}"/>')
    elif kind == "chair":
        body = (f'<rect x="54" y="28" width="24" height="106" rx="11" fill="{TINT}"/>'
                f'<rect x="54" y="108" width="100" height="24" rx="11" fill="{TINT}"/>'
                f'<path d="M66 132 V172 M142 132 V172" fill="none"/>')
    elif kind == "heart":
        body = (f'<path d="M100 168 C28 112 26 48 68 46 C86 45 98 56 100 68 C102 56 114 45 132 46 C174 48 172 112 100 168 Z" fill="{TINT}"/>')
    else:  # star
        pts = []
        for i in range(10):
            r = 78 if i % 2 == 0 else 33
            a = -math.pi / 2 + i * math.pi / 5
            pts.append(f"{100 + r * math.cos(a):.1f},{108 + r * math.sin(a):.1f}")
        body = f'<polygon points="{" ".join(pts)}" fill="{TINT}"/>'
    return (f'<svg class="icon" viewBox="0 0 200 200" data-sw="{SW}" data-icon="{kind}" xmlns="http://www.w3.org/2000/svg">'
            f'<g class="art" {s}>{body}</g></svg>')


# ------------------------------------------------------------------ pages
def teacher_page(wm=False):
    tl = [("A week or so before", f"Teach the {LESSON_MIN}-minute mini-lesson ({R('glance')}). It ends with the exit ticket."),
          ("Before the day", f"Post the {NPOST} posters ({RR('poster1', f'poster{NPOST}')}) in the rehearsal room and near the entrance."),
          ("The day of the concert", f"Hand out the audience checklist ({R('audience')}) to students who will be listening and the performer checklist ({R('performer')}) to students who will be performing."),
          ("After the concert", "Students tick the boxes and write one thing that went well. Talk about it together the next time you meet.")]
    trow = "".join(f"<tr><td><b>{a}</b></td><td>{b}</td></tr>" for a, b in tl)
    inner = (f'<div class="rule"><h1>Teacher Notes</h1><div class="l" style="font-size:13pt">{TITLE} · a mini-lesson, {NPOST} posters, 2 checklists and an exit ticket · grades 3–8</div></div>'
             f'<div class="cols"><div>'
             f'<h2>What is inside ({TOTAL_PAGES} pages)</h2><ul>'
             f'<li>{R("glance", True)}: lesson at a glance ({NSTEPS} steps, {LESSON_MIN} minutes)</li>'
             f'<li>{RR("script1", "script2", True)}: teacher script with {NDISC} discussion questions and {NROLE} role-play scenarios</li>'
             f'<li>{R("tps", True)}: think-pair-share sheet</li>'
             f'<li>{RR("poster1", f"poster{NPOST}", True)}: {NPOST} posters</li>'
             f'<li>{R("audience", True)}: audience checklist ({NAUD} audience items)</li>'
             f'<li>{R("performer", True)}: performer checklist ({NPERF} performer items)</li>'
             f'<li>{R("exit", True)}: exit ticket ({NQ} exit ticket questions, 2 tickets per page)</li>'
             f'<li>{R("key", True)}: exit ticket answer key</li>'
             f'<li>{R("terms", True)}: terms of use</li></ul>'
             f'<h2>Before a concert</h2><table class="dt"><colgroup><col style="width:34%"><col style="width:66%"></colgroup>{trow}</table>'
             f'<h2>Good to know</h2>'
             f'<p>Concert customs vary by venue, style and culture. At many school concerts the audience claps when a piece has ended. At a jazz club, a drum circle or a pop show, people may clap or cheer during the music. '
             f'Teach students to watch and listen for cues, and tell them what your own concert expects.</p>'
             f'</div><div>'
             f'<h2>Differentiation</h2>'
             f'<p><b>Grades 3–5:</b> read each poster aloud and have students repeat the habit. Do the role-plays as a whole class with volunteers, use two or three discussion questions, and have students tick the checklist with a partner.</p>'
             f'<p><b>Grades 6–8:</b> let students lead the discussion and the role-plays, and use all {NDISC} discussion questions. Ask them to explain why each habit helps performers, and to compare customs at different kinds of events.</p>'
             f'<h2>Including everyone</h2>'
             f'<p>Some students need to move, use a quiet fidget, wear ear protection or step out for a moment. Treat these as part of respectful listening, and plan a quiet way to do each. Applause can also be silent, such as waving open hands.</p>'
             f'<h2>Extension ideas</h2><ul>'
             f'<li>Students write a short note for the concert program that welcomes the audience and explains one habit.</li>'
             f'<li>Students design their own poster for a habit that is not covered here.</li>'
             f'<li>Students ask a family member where they have been in an audience and what the customs were there, then share what they learned.</li></ul>'
             f'<p class="small">No songs, lyrics or copyrighted characters are used. Standards: none cited. Match the activities to your own curriculum.</p>'
             f'</div></div><div class="fill"></div>')
    return page("teacher", inner, wm, "doc")


def glance_page(wm=False):
    desc = {1: f"Ask a short question about being in an audience (script on {R('script1')}).",
            2: f"Introduce the {NPOST} habits one at a time with the posters ({RR('poster1', f'poster{NPOST}')}).",
            3: f"Discuss {NDISC} discussion questions as a class.",
            4: f"Students think, pair and share on {R('tps')}.",
            5: f"Volunteers act out {NROLE} role-play scenarios with no instruments.",
            6: f"Students answer {NQ} exit ticket questions ({R('exit')}). Key on {R('key')}."}
    rows = "".join(f'<tr data-step="{i}" data-min="{m}"><td><b>{i}</b></td><td>{escape(n)}</td><td data-minutes="{m}">{m} min</td><td>{desc[i]}</td></tr>'
                   for i, (n, m) in enumerate(STEPS, 1))
    inner = (f'<div class="rule"><h1>Lesson at a Glance</h1><div class="l" style="font-size:13pt">A {LESSON_MIN}-minute mini-lesson for grades 3–8. No instruments needed.</div></div>'
             f'<div class="doc">'
             f'<h2>The lesson in {NSTEPS} steps</h2>'
             f'<table class="dt blk"><colgroup><col style="width:7%"><col style="width:19%"><col style="width:11%"><col style="width:63%"></colgroup>'
             f'<tr><th>Step</th><th>Name</th><th>Time</th><th>What happens</th></tr>{rows}'
             f'<tr><td></td><td><b>Total</b></td><td data-mintotal="{LESSON_MIN}"><b>{LESSON_MIN} min</b></td><td>Short on time? Use fewer questions in Step 3.</td></tr></table>'
             f'<div class="cols"><div>'
             f'<h2>Students will</h2><ul>'
             f'<li>name the {NPOST} habits of a respectful audience and of focused, kind performers;</li>'
             f'<li>explain why each habit helps the performers and the people around them;</li>'
             f'<li>show how to handle a tricky moment at a concert without instruments.</li></ul>'
             f'<h2>Get ready</h2><ul>'
             f'<li>Print the {NPOST} posters ({RR("poster1", f"poster{NPOST}")}) and tape them up or show them on a screen.</li>'
             f'<li>Print the think-pair-share sheet ({R("tps")}) and the exit ticket ({R("exit")}), 2 tickets to a page.</li>'
             f'</ul>'
             f'</div><div>'
             f'<h2>The {NPOST} habits</h2><ol>{"".join(f"<li>{escape(p["head"])}</li>" for p in POSTERS)}</ol>'
             f'<h2>A note on customs</h2>'
             f'<p>Concert customs differ from venue to venue and culture to culture. This lesson teaches the usual habits for a school concert and invites students to notice where customs change.</p>'
             f'</div></div>'
             f'<h2>Words to know</h2><table class="dt blk"><colgroup><col style="width:20%"><col style="width:80%"></colgroup>'
             f'{"".join(f"<tr><td><b>{a}</b></td><td>{b}</td></tr>" for a, b in VOCAB)}</table>'
             f'</div><div class="fill"></div>')
    return page("glance", inner, wm, "doc")


def sh(n):
    name, m = STEPS[n - 1]
    return (f'<div class="sh blk" data-stephead="{n}" data-min="{m}"><div class="n">{n}</div><div class="st">Step {n}: {escape(name)}</div>'
            f'<div class="mn">{m} min</div></div>')


def script1_page(wm=False):
    habits = "".join(f'<li data-habit="{i}"><b>{escape(p["head"])}.</b> {escape(p["sub"].split(". ")[0].rstrip("."))}. (Poster {i}, {R(f"poster{i}")})</li>'
                     for i, p in enumerate(POSTERS, 1))
    dq = "".join(f'<li data-disc="{i}">{escape(q)}</li>' for i, q in enumerate(DISCUSS, 1))
    inner = (f'<div class="rule"><h1>Teacher Script</h1><div class="l" style="font-size:13pt">Steps 1 to 3 · say the shaded lines in your own words</div></div>'
             f'<div class="doc big">'
             f'{sh(1)}'
             f'<div class="say blk"><b>Say</b>Think about a time you watched someone perform, in person or at school. Raise your hand if you have ever been in an audience. Now keep your hand up if you have ever been a performer.</div>'
             f'<div class="say blk"><b>Say</b>Performers practice for weeks. Today we will learn what the audience can do to help them shine, and what performers can do to be their best on stage.</div>'
             f'{sh(2)}'
             f'<div class="do blk"><b>Do</b>Show the {NPOST} posters one at a time, about a minute each. Read each heading aloud and have students repeat it. Then ask why the habit matters.</div>'
             f'<ol class="blk" style="margin:2pt 0 4pt;padding-left:18pt">{habits}</ol>'
             f'{sh(3)}'
             f'<div class="do blk"><b>Ask</b>Take as many of these {NDISC} discussion questions as time allows. Call on a few students for each one.</div>'
             f'<ol class="dq blk">{dq}</ol>'
             f'<div class="do blk"><b>Note</b>Listen for answers about focus, safety, respect and kindness. If students say that customs differ, agree: different places have different customs, so we watch and listen for cues.</div>'
             f'</div><div class="fill"></div>')
    return page("script1", inner, wm, "doc")


def script2_page(wm=False):
    roles = "".join(f'<div class="rc blk" data-role="{l}"><div class="lt">{l}</div><p><b>{escape(t)}</b> {escape(d)}</p></div>' for l, t, d in ROLES)
    inner = (f'<div class="rule"><h1>Teacher Script</h1><div class="l" style="font-size:13pt">Steps 4 to 6 · say the shaded lines in your own words</div></div>'
             f'<div class="doc big">'
             f'{sh(4)}'
             f'<div class="say blk"><b>Say</b>Your friend&rsquo;s group is playing a soft, slow piece. In the audience, your phone buzzes in your pocket. What do you do, and why does it matter to the performers?</div>'
             f'<div class="do blk"><b>Do</b>Hand out the think-pair-share sheet ({R("tps")}). Students think on their own for 1 minute, talk with a partner for 1 minute, then share with the class for 1 minute.</div>'
             f'<div class="do blk"><b>Listen for</b>Silence it quickly, put it away, and wait until after the piece. Accept any calm, considerate answer that keeps the performers in mind.</div>'
             f'{sh(5)}'
             f'<div class="say blk"><b>Say</b>Now you will show me. We will use no instruments, only our bodies and our manners. I need volunteers to act out {NROLE} role-play scenarios.</div>'
             f'<div class="rolegrid">{roles}</div>'
             f'<div class="do blk"><b>Do</b>Ask 1 or 2 volunteers to act out each scenario in silence, then replay it. After each one, ask the class: &ldquo;What did you see that helped the performers?&rdquo; Give a thumbs-up for each habit spotted.</div>'
             f'{sh(6)}'
             f'<div class="say blk"><b>Say</b>Last, answer {NQ} short questions on the exit ticket. Do it on your own. This tells me what stuck.</div>'
             f'<div class="do blk"><b>Do</b>Hand out the exit tickets ({R("exit")}), 2 to a page, cut apart. Collect them at the door. The answer key is on {R("key")}. Question 1 has one right answer. Questions 2 and 3 have many good answers.</div>'
             f'</div><div class="fill"></div>')
    return page("script2", inner, wm, "doc")


def tps_page(wm=False):
    inner = (top("Think-Pair-Share", f'<span data-stepref="4">Step 4</span> of the mini-lesson · 3 minutes', "STEP 4", f"of {NSTEPS}") +
             '<div class="name">Name<span></span>Partner<span class="s"></span>Date<span class="s"></span></div>'
             '<div class="how blk"><b>The question:</b> Your friend&rsquo;s group is playing a soft, slow piece. In the audience, your phone buzzes in your pocket. What do you do, and why does it matter to the performers?</div>'
             '<div class="tps blk">'
             '<div class="c"><div class="bt">1. Think <small>1 minute</small></div><p>Work alone and write your own answer below.</p></div>'
             '<div class="c"><div class="bt">2. Pair <small>1 minute</small></div><p>Tell your partner. Listen to their answer too.</p></div>'
             '<div class="c"><div class="bt">3. Share <small>1 minute</small></div><p>Be ready to share your idea or your partner&rsquo;s idea.</p></div></div>'
             '<div class="box blk"><div class="bt">My answer</div><div class="rl"></div><div class="rl"></div><div class="rl"></div></div>'
             '<div class="row2"><div class="box blk"><div class="bt">My partner&rsquo;s idea</div><div class="rl"></div><div class="rl"></div></div></div>'
             '<div class="row2"><div class="box blk"><div class="bt">One new idea from the class</div><div class="rl"></div><div class="rl"></div></div></div>'
             '<div class="row2"><div class="box blk"><div class="bt">Sentence starters</div>'
             '<div style="font-size:11pt;line-height:1.5">I would&hellip; &nbsp;·&nbsp; This helps the performers because&hellip; &nbsp;·&nbsp; My partner said&hellip; &nbsp;·&nbsp; Another way to handle it is&hellip;</div></div></div>'
             '<div class="fill"></div>')
    return page("tps", inner, wm)


def poster_page(i, wm=False):
    p = POSTERS[i - 1]
    long = " long" if len(p["head"]) > 26 else ""
    inner = (f'<div class="pk blk">{TITLE} · Poster {i} of {NPOST}</div>'
             f'<div class="pt blk{long}" data-poster="{i}">{escape(p["head"])}</div>'
             f'<div class="pico blk">{icon(p["icon"])}</div>'
             f'<div class="psub blk">{escape(p["sub"])}</div>'
             f'<div class="prem blk">{escape(p["rem"])}</div>')
    return page(f"poster{i}", inner, wm, "poster")


def checklist_head(sub):
    return f'<div class="ckh blk"><div>{sub}</div></div>'


def audience_page(wm=False):
    rows = "".join(
        f'<div class="ck blk" data-aud="{i}"><div class="bx"></div><div class="tx">{escape(t)}</div>'
        + (f'<div class="rf" data-pref="{pi + 1}" data-ppage="{P_POST0 + pi}">Poster {pi + 1}<br>page {P_POST0 + pi}</div></div>' if pi is not None else '<div class="rf"></div></div>')
        for i, (t, pi, _w) in enumerate(AUDIENCE, 1))
    inner = (top("Audience Checklist", f"{NAUD} audience items · tick each box you did", "AUDIENCE", "I was part of the music") +
             '<div class="name">Name<span></span>Concert<span class="s"></span>Date<span class="s"></span></div>'
             f'<div class="how blk">Tick each box that is true for you. The poster on the right shows where each habit is taught. Tick what you did, not what you wish you had done.</div>'
             f'{rows}'
             '<div class="row2"><div class="box blk"><div class="bt">One thing I did well as an audience member</div><div class="rl"></div></div></div>'
             '<div class="row2"><div class="box blk"><div class="bt">One thing I will try next time</div><div class="rl"></div></div></div>'
             '<div class="fill"></div>')
    return page("audience", inner, wm)


def performer_page(wm=False):
    rows = "".join(
        f'<div class="ck blk" data-perf="{i}"><div class="bx"></div><div class="gp" data-group="{g}">{g}</div><div class="tx">{escape(t)}</div></div>'
        for i, (g, t) in enumerate(PERFORMER, 1))
    gc = " · ".join(f"{g} {n}" for g, n in GROUP_COUNTS.items())
    inner = (top("Performer Checklist", f"{NPERF} performer items · ready, focused, kind", "PERFORMER", "I helped the show") +
             '<div class="name">Name<span></span>Concert<span class="s"></span>Date<span class="s"></span></div>'
             f'<div class="ckh blk"><div class="sp"><img src="../art/spot-music-stand.png" alt=""></div>'
             f'<div>Tick each box that is true for you. These items match <span data-pref="{NPOST}" data-ppage="{P_POST0 + PERF_POSTER}">Poster {NPOST}, page {P_POST0 + PERF_POSTER}</span>. '
             f'<span data-groups="{gc}">{gc}</span> = {NPERF} performer items.</div></div>'
             f'{rows}'
             '<div class="row2"><div class="box blk"><div class="bt">One thing I did well as a performer</div><div class="rl"></div></div></div>'
             '<div class="row2"><div class="box blk"><div class="bt">One thing I will try next time</div><div class="rl"></div></div></div>'
             '<div class="fill"></div>')
    return page("performer", inner, wm)


def ticket(t):
    q1 = EXIT_Q[0]
    opts = "".join(f'<div class="op" data-opt="{l}"><b>{l}.</b><span>{escape(x)}</span></div>' for l, x in q1["opts"])
    return (f'<div class="tk blk" data-ticket="{t}"><div class="th"><div class="h">Exit Ticket</div><div class="l">{TITLE} · {NQ} questions</div></div>'
            f'<div class="nm">Name<span></span>Date<span class="s"></span></div>'
            f'<div class="q" data-q="1"><i>1.</i>{escape(q1["text"])} Circle one.</div>{opts}'
            f'<div class="q" data-q="2"><i>2.</i>{escape(EXIT_Q[1]["text"])}</div><div class="rl"></div><div class="rl"></div><div class="rl"></div>'
            f'<div class="q" data-q="3"><i>3.</i>{escape(EXIT_Q[2]["text"])}</div><div class="rl"></div><div class="rl"></div><div class="rl"></div></div>')


def exit_page(wm=False):
    inner = (f'<div class="how blk" style="margin-top:0">Cut along the middle. This is {stepref(6)} of the mini-lesson. Answer key on {R("key")}.</div>'
             f'{ticket(1)}{ticket(2)}<div class="fill"></div>')
    return page("exit", inner, wm, right=f"Page {P_EXIT} · Answer key on page {P_KEY}")


def key_page(wm=False):
    q1 = EXIT_Q[0]
    opts = {
        "A": "Wrong. A quiet moment in the middle of a piece is when the audience listens most closely, so clapping there can cover the music.",
        "B": "Correct. At most school concerts the audience claps after a piece has ended and the music has stopped. Some pieces have several parts, so watch your director or the program for cues.",
        "C": "Wrong. Clapping is welcome at concerts. The habit is to clap at the right time, which is after a piece ends.",
    }
    ko = "".join(f'<div class="ko{" ok" if l == q1["correct"] else ""}" data-keyopt="{l}"><b>{l}.</b><span>{escape(opts[l])}</span></div>' for l, _ in q1["opts"])
    inner = (top("Exit Ticket Answer Key", f"{NQ} exit ticket questions · only Question 1 has one right answer", "ANSWER KEY", f"for {R('exit')}", "key") +
             '<div class="doc" style="margin-top:9pt">'
             f'<div class="kq blk" data-keyq="1" data-correct="{q1["correct"]}"><div class="kh">Question 1 · <i>Answer: {q1["correct"]}</i></div>'
             f'<p>{escape(q1["text"])}</p>{ko}'
             f'<p style="margin-top:5pt" class="small">Customs vary. At a jazz club, a pop show or a drum circle, people may clap during the music. If a student chooses A for that reason, ask where they have seen that, then explain that at most school concerts we wait for the end of a piece.</p></div>'
             f'<div class="kq blk" data-keyq="2"><div class="kh">Question 2 · <i>Many answers are right</i></div><p>{escape(EXIT_Q[1]["text"])}</p>'
             f'<p><b>Look for any two of these:</b> arrive early and quietly; silence and put away a phone; listen quietly; clap at the end of a piece; stay seated until the music ends; cheer kindly for every group; keep voices low; thank the performers.</p></div>'
             f'<div class="kq blk" data-keyq="3"><div class="kh">Question 3 · <i>Many answers are right</i></div><p>{escape(EXIT_Q[2]["text"])}</p>'
             f'<p><b>Look for one calm, kind action, such as:</b> take a breath and keep going with the group; watch the director for the next cue; stay still and quiet until the piece ends; smile and move on; encourage a fellow performer afterward. Be careful with answers that blame someone else.</p></div>'
             f'<p class="small">Scoring idea: give 1 point for Question 1, and 1 point each for Questions 2 and 3 when the answer is on topic and respectful. That makes {NQ} points in all.</p>'
             '</div><div class="fill"></div>')
    return page("key", inner, wm)


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
             f'<li>Lesson, posters, checklists, exit ticket and icons: original work, {BRAND} by {STORE}.</li>'
             f'<li>Cover and spot illustrations: house-style line art made with digital tools by {BRAND}.</li>'
             f'<li>Text fonts: Oswald (The Oswald Project Authors) and Source Sans 3 (Adobe), SIL Open Font License 1.1.</li></ul>'
             f'<h2>What is in this file</h2><p>{R("cover", True)} cover, {R("teacher")} teacher notes, {R("glance")} lesson at a glance, '
             f'{RR("script1", "script2")} teacher script, {R("tps")} think-pair-share sheet, {RR("poster1", f"poster{NPOST}")} the posters, '
             f'{R("audience")} audience checklist, {R("performer")} performer checklist, {R("exit")} exit ticket, {R("key")} answer key and {R("terms")} these terms: '
             f'{TOTAL_PAGES} pages in all.</p>'
             f'<p class="small">{DISCLOSURE}</p><div class="fill"></div>')
    return page("terms", inner, wm, "doc")


def cover_page():
    return (f'<section class="page cover" data-page="1" data-kind="cover" data-name="Cover"><div class="store">{BRAND}</div>'
            f'<div style="height:4.5in;display:flex;align-items:center;justify-content:center"><img src="../art/hero.png" style="height:4.4in;display:block" alt=""></div>'
            f'<div class="ctitle"><div class="a">CONCERT ETIQUETTE</div><div class="b">LESSON &amp; POSTERS</div>'
            f'<div class="c">A {LESSON_MIN}-minute mini-lesson, {NPOST} posters, checklists and an exit ticket</div></div>'
            f'<div class="cband">Grades 3–8 <em>·</em> {NPOST} posters <em>·</em> {TOTAL_PAGES} pages</div></section>')


def all_pages(wm=False):
    p = [cover_page(), teacher_page(wm), glance_page(wm), script1_page(wm), script2_page(wm), tps_page(wm)]
    p += [poster_page(i, wm) for i in range(1, NPOST + 1)]
    p += [audience_page(wm), performer_page(wm), exit_page(wm), key_page(wm), terms_page(wm)]
    return p


SHOT_PAGES = {"glance": P_GLANCE, **{f"poster{i}": P_POST0 + i - 1 for i in range(1, NPOST + 1)}, "audience": P_AUD,
              "performer": P_PERF, "exit": P_EXIT, "key": P_KEY}
PREVIEW_ORDER = ["glance", "poster1", "audience", "exit"]
KIND_OF_SHOT = {"glance": "glance", "poster1": "poster1", "poster3": "poster3", "poster6": "poster6", "audience": "audience",
                "performer": "performer", "exit": "exit", "key": "key"}

# ------------------------------------------------------------------ square images
SQ_CSS = """
.sq { width: 1000px; height: 1000px; position: relative; overflow: hidden; background: #fff; display: flex; flex-direction: column; align-items: center; }
.sq .store { font-family: 'Oswald'; font-weight: 500; letter-spacing: .32em; text-transform: uppercase; font-size: 22px; margin-top: 34px; }
.sq .hd { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; text-align: center; line-height: .95; }
.sq .sub { font-family: 'Oswald'; font-weight: 300; text-align: center; }
.sq .band { position: absolute; left: 0; right: 0; bottom: 0; background: #000; color: #fff; text-align: center; font-family: 'Oswald';
            font-weight: 500; text-transform: uppercase; letter-spacing: .1em; font-size: 26px; padding: 16px 0 18px; }
.sq .band em { font-style: normal; color: #8FC3EC; }
.shot { background: #fff; border: 2px solid #000; box-shadow: 8px 8px 0 #000; position: relative; overflow: hidden; }
.shot img { display: block; width: 100%; }
.lbl { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 22px; text-align: center; margin-top: 18px; }
.lbl span { font-weight: 300; text-transform: none; display: block; font-size: 19px; margin-top: 2px; }
"""


def sq_doc(body):
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{font_css()}'
            f'html,body{{margin:0;background:#fff}}{SQ_CSS}</style></head><body>{body}</body></html>')


def cover_square():
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div>'
        f'<div style="flex:1;display:flex;flex-direction:column;justify-content:space-evenly;align-items:center;width:100%;padding:0 0 76px">'
        f'<div style="height:540px;display:flex;align-items:center;justify-content:center"><img src="../art/hero.png" style="height:540px;display:block" alt=""></div>'
        f'<div><div class="hd" style="font-size:70px">Concert Etiquette</div>'
        f'<div class="hd" style="font-size:112px">Lesson &amp; Posters</div>'
        f'<div class="sub" style="font-size:28px;margin-top:12px">A {LESSON_MIN}-minute mini-lesson, {NPOST} posters, checklists and an exit ticket</div></div>'
        f'</div><div class="band">Grades 3–8 <em>·</em> {NPOST} posters <em>·</em> {TOTAL_PAGES} pages</div></div>')


def shots_row(headline, sub, items, band, w):
    shots = "".join(f'<div style="width:{w}px"><div class="shot"><img src="{src}"></div><div class="lbl">{lab}</div></div>' for src, lab in items)
    gap = 40 if len(items) < 3 else 26
    return sq_doc(f'<div class="sq"><div class="store">{BRAND}</div>'
                  f'<div class="hd" style="font-size:66px;margin-top:24px">{headline}</div>'
                  f'<div class="sub" style="font-size:27px;margin-top:8px">{sub}</div>'
                  f'<div style="flex:1;display:flex;align-items:center;padding-bottom:74px"><div style="display:flex;gap:{gap}px;align-items:flex-start">{shots}</div></div>'
                  f'<div class="band">{band}</div></div>')


def shots_grid(headline, sub, items, band, w):
    shots = "".join(f'<div style="width:{w}px"><div class="shot"><img src="{src}"></div><div class="lbl" style="font-size:18px;margin-top:12px">{lab}</div></div>' for src, lab in items)
    return sq_doc(f'<div class="sq"><div class="store">{BRAND}</div>'
                  f'<div class="hd" style="font-size:66px;margin-top:24px">{headline}</div>'
                  f'<div class="sub" style="font-size:27px;margin-top:8px">{sub}</div>'
                  f'<div style="flex:1;display:flex;align-items:center;padding-bottom:74px"><div style="display:flex;flex-wrap:wrap;justify-content:center;gap:22px 26px;width:860px">{shots}</div></div>'
                  f'<div class="band">{band}</div></div>')


def label(kind, extra):
    return f'{PAGE_NAMES[kind]}<span>{extra}</span>'


def square_pages():
    return [
        shots_grid(f"{NPOST} printable posters", "Large headings and simple icons, one habit on each",
                   [(f"shot-poster{i}.png", f'{PAGE_NAMES[f"poster{i}"]}<span>{escape(POSTERS[i - 1]["head"])}</span>') for i in range(1, NPOST + 1)],
                   f"{NPOST} posters <em>·</em> grades 3–8 <em>·</em> no prep", 212),
        shots_row("Audience and performer checklists", f"{NAUD} audience items and {NPERF} performer items with tick boxes",
                  [("shot-audience.png", label("audience", f"{NAUD} audience items")),
                   ("shot-performer.png", label("performer", f"{NPERF} performer items"))],
                  "Tick boxes <em>·</em> poster page numbers <em>·</em> reflection lines", 420),
        shots_row(f"A {LESSON_MIN}-minute mini-lesson", f"Teacher script, role-play and a {NQ}-question exit ticket",
                  [("shot-glance.png", label("glance", f"{NSTEPS} steps, {LESSON_MIN} minutes")),
                   ("shot-exit.png", label("exit", f"{NQ} questions, answer key included"))],
                  f"Think-pair-share <em>·</em> role-play <em>·</em> {TOTAL_PAGES} pages", 420),
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
    return f"""# UPLOAD: {LISTING_TITLE} (TpT 054)

These fields follow the order of TpT's "Add a resource" form. Evergreen: no season, sell all year (strongest before any concert and at the start of the school year).

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
Get your students ready to be a great audience, and a great ensemble, with a {LESSON_MIN}-minute concert etiquette mini-lesson. This printable pack has a teacher script, {NDISC} discussion questions, a think-pair-share, a "show me" role-play with no instruments, {NPOST} classroom posters, an audience checklist, a performer checklist and a {NQ}-question exit ticket with an answer key. It works for band, orchestra, choir and general music in grades 3 to 8, and nothing in it is tied to a season or a holiday.

WHAT'S INCLUDED ({TOTAL_PAGES} pages, PDF, US Letter)
• Cover (1 page)
• Teacher notes: how to use the pack before a concert, differentiation for grades 3-5 and grades 6-8, and extension ideas (1 page)
• Lesson at a glance: {NSTEPS} steps that add up to {LESSON_MIN} minutes (1 page)
• Teacher script: what to say and do for each step, {NDISC} discussion questions and {NROLE} role-play scenarios (2 pages)
• Think-pair-share sheet (1 page)
• {NPOST} printable posters, one per page: "Arrive early and quietly", "Silence phones", "Clap at the right time", "Stay seated until the music ends", "Be a respectful audience" and "Performers: ready, focused, kind" ({NPOST} pages)
• Audience checklist with {NAUD} audience items and tick boxes (1 page)
• Performer checklist with {NPERF} performer items and tick boxes (1 page)
• Exit ticket with {NQ} exit ticket questions, 2 tickets to a page (1 page)
• Exit ticket answer key (1 page)
• Terms of use and credits (1 page)
Total: {TOTAL_PAGES} pages.

HOW TO USE
Teach the mini-lesson a week or so before a concert, post the {NPOST} posters, and hand out the checklists on the day. After the concert, students tick the boxes and write one thing that went well. The pack states plainly that concert customs vary by venue, style and culture, and it invites students to watch and listen for cues. It also includes ideas for including every student.

• Grades 3–8 (differentiation for grades 3-5 and grades 6-8 in the teacher notes)
• Prints well in black and white; one accent color
• No songs, lyrics or copyrighted characters

{DISCLOSURE}
```

## 3. Grades

4, 5, 6, 7 (TpT allows four; the product is written for grades 3 to 8).

## 4. Subjects and tags

- Subjects: {", ".join(SUBJECTS)}
- Tags: {", ".join(TAGS)}

## 5. Page count by section (totals {TOTAL_PAGES})

- Cover: 1
- Teacher notes: 1
- Lesson at a glance: 1
- Teacher script: 2
- Think-pair-share sheet: 1
- Posters: {NPOST}
- Audience checklist: 1
- Performer checklist: 1
- Exit ticket: 1
- Exit ticket answer key: 1
- Terms of use and credits: 1
- Total: {TOTAL_PAGES}

## 6. Standards

None cited. The teacher notes ask teachers to match the activities to their own curriculum.

## 7. Price

**${PRICE}** (paid; owner range $3–5).

## 8. Preview

Paid. Preview PDF: lesson at a glance, poster 1, the audience checklist and the exit ticket, all watermarked.

## 9. Before you click publish

- [ ] Evergreen: no season, no holiday words.
- This is a printable poster and lesson pack: it has no music notation.
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
      d.pages = A('.page', pg => ({ n: +pg.dataset.page, kind: pg.dataset.kind, name: pg.dataset.name, wms: pg.querySelectorAll('.wm').length }));
      d.posters = A('[data-poster]', e => ({ i: +e.dataset.poster, page: pageNo(e), text: T(e), sw: e.scrollWidth, cw: e.clientWidth, sh: e.scrollHeight, ch: e.clientHeight,
                                              lines: Math.round(e.getBoundingClientRect().height / parseFloat(getComputedStyle(e).lineHeight)),
                                              icon: (e.closest('.page').querySelector('svg.icon') || {dataset: {}}).dataset.icon || '' }));
      d.icons = A('svg.icon', s => {
        const g = s.querySelector('g.art'); const bb = g.getBBox(); const sw = +s.dataset.sw; const vb = s.viewBox.baseVal;
        return { page: pageNo(s), icon: s.dataset.icon, x0: bb.x, y0: bb.y, x1: bb.x + bb.width, y1: bb.y + bb.height, sw, w: vb.width, h: vb.height };
      });
      d.aud = A('[data-aud]', e => ({ i: +e.dataset.aud, page: pageNo(e), text: T(e.querySelector('.tx')), boxes: e.querySelectorAll('.bx').length,
                                       pref: e.querySelector('[data-pref]') ? +e.querySelector('[data-pref]').dataset.pref : 0, ppage: e.querySelector('[data-pref]') ? +e.querySelector('[data-pref]').dataset.ppage : 0, rftxt: T(e.querySelector('.rf')) }));
      d.perf = A('[data-perf]', e => ({ i: +e.dataset.perf, page: pageNo(e), text: T(e.querySelector('.tx')), boxes: e.querySelectorAll('.bx').length, group: e.querySelector('.gp').dataset.group }));
      d.perfhead = A('[data-groups]', e => ({ g: e.dataset.groups, txt: T(e.closest('.ckh')) }));
      d.prefs = A('[data-pref]', e => ({ page: pageNo(e), pref: +e.dataset.pref, ppage: +e.dataset.ppage, txt: T(e) }));
      d.tickets = A('[data-ticket]', e => ({ t: +e.dataset.ticket, page: pageNo(e), qs: [...e.querySelectorAll('[data-q]')].map(q => ({ n: q.dataset.q, text: T(q) })),
                                              opts: [...e.querySelectorAll('[data-opt]')].map(o => ({ l: o.dataset.opt, text: T(o.querySelector('span')) })), lines: e.querySelectorAll('.rl').length,
                                              hasKey: /answer:/i.test(T(e)) }));
      d.keyqs = A('[data-keyq]', e => ({ n: e.dataset.keyq, correct: e.dataset.correct || '', text: T(e.querySelector('.kh')), q: T(e.querySelector('p')),
                                         opts: [...e.querySelectorAll('[data-keyopt]')].map(o => ({ l: o.dataset.keyopt, ok: o.classList.contains('ok'), text: T(o.querySelector('span')) })) }));
      d.stepsRows = A('[data-step]', e => ({ n: +e.dataset.step, min: +e.dataset.min, txt: T(e.children[2]), name: T(e.children[1]) }));
      d.mintotal = A('[data-mintotal]', e => ({ v: +e.dataset.mintotal, txt: T(e) }));
      d.stepheads = A('[data-stephead]', e => ({ n: +e.dataset.stephead, min: +e.dataset.min, page: pageNo(e), txt: T(e) }));
      d.stepRefs = A('[data-stepref]', e => ({ n: +e.dataset.stepref, page: pageNo(e), txt: T(e) }));
      d.disc = A('[data-disc]', e => ({ i: +e.dataset.disc, page: pageNo(e), text: T(e) }));
      d.roles = A('[data-role]', e => ({ l: e.dataset.role, page: pageNo(e), text: T(e) }));
      d.habits = A('[data-habit]', e => ({ i: +e.dataset.habit, text: T(e), page: pageNo(e) }));
      d.refs = A('[data-ref]', e => ({ page: pageNo(e), kind: e.dataset.ref, n: +e.dataset.n, kind2: e.dataset.ref2 || '', n2: +(e.dataset.n2 || 0), txt: T(e) }));
      d.pagetext = A('.page', pg => T(pg));
      d.pagetextNoFoot = A('.page', pg => { const c = pg.cloneNode(true); c.querySelectorAll('.foot,.wm').forEach(x => x.remove()); return c.innerText.replace(/\s+/g, ' ').trim(); });
      d.foots = A('.page', pg => T(pg.querySelector('.foot')));
      const res = [];
      d.gaps = [];
      document.querySelectorAll('.page').forEach((pg, i) => {
        const n = i + 1, pr = pg.getBoundingClientRect();
        const ft = pg.querySelector('.foot');
        const ftop = ft ? ft.getBoundingClientRect().top : pr.bottom;
        if (pg.scrollHeight > pg.clientHeight + 1) res.push(`page ${n}: content overflows the page`);
        let low = 0; const boxes = [];
        pg.querySelectorAll('.blk, .rl, .top, .name, .how, .doc p, .doc li, .doc table, .doc h2, .ck, .tk, .sh, .say, .do, .rc').forEach(el => {
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
        pg.querySelectorAll('.ck, .tk, .box, td, .rc, .say, .do, .how, .pt, .psub, .prem, .pk, .sh, .tx').forEach(el => {
          if (getComputedStyle(el).display === 'inline') return;
          if (el.scrollHeight > el.clientHeight + 2 || el.scrollWidth > el.clientWidth + 2) res.push(`page ${n}: text clipped in ${el.tagName}.${el.className} (${el.scrollWidth}x${el.scrollHeight} in ${el.clientWidth}x${el.clientHeight}) ${el.innerText.slice(0,30)}`);
        });
        pg.querySelectorAll('p, li, .how, .psub, .prem, .tx, .say, .do').forEach(el => {
          const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
          const lines = {}; let node;
          while ((node = walker.nextNode())) {
            const re = /\S+/g; let m;
            while ((m = re.exec(node.textContent))) {
              const rg = document.createRange(); rg.setStart(node, m.index); rg.setEnd(node, m.index + m[0].length);
              const rc = rg.getClientRects()[0]; if (!rc) continue;
              const k = Math.round((rc.top + rc.bottom) / 8); (lines[k] = lines[k] || []).push(m[0]);
            }
          }
          const ks = Object.keys(lines).map(Number).sort((a, b) => a - b);
          if (ks.length > 1 && lines[ks[ks.length - 1]].length === 1)
            res.push(`page ${n}: one-word last line "${lines[ks[ks.length - 1]][0]}" in ${el.tagName}.${el.className}`);
        });
        // poster text must lie inside the page margins
        pg.querySelectorAll('.pt, .psub, .prem, .pk').forEach(el => {
          const range = document.createRange(); range.selectNodeContents(el);
          for (const rc of range.getClientRects()) if (rc.left < pr.left + 0.35 * 96 || rc.right > pr.right - 0.35 * 96) res.push(`page ${n}: poster text reaches the page edge in ${el.className}`);
        });
        pg.querySelectorAll('img').forEach(im => {
          const r = im.getBoundingClientRect();
          if (r.left < pr.left + 0.2 * 96 || r.right > pr.right - 0.2 * 96 || r.top < pr.top + 0.2 * 96 || r.bottom > ftop) res.push(`page ${n}: an image is too near the page edge`);
          const par = im.parentElement.getBoundingClientRect();
          if (!im.complete || im.naturalWidth === 0) res.push(`page ${n}: broken image`);
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


UK_SPELLINGS = ["practise", "colour", "favourite", "centre", "metre", "recognise", "organise", "behaviour", "neighbour", "programme", "theatre", "licence"]
QA_WORDS = ["recomputed", "--check", "checked by hand", "handmade", "hand-checked", "classroom-tested", "verified by", "inspector"]
SEASONAL = r"winter|snow|holiday|christmas|\bfall\b|autumn|spring|summer|halloween|new year|thanksgiving|december"
NUMWORDS = {"posters?": NPOST, "audience (?:checklist )?items": NAUD, "performer (?:checklist )?items": NPERF, "discussion questions": NDISC,
            "exit ticket questions": NQ, "role-play scenarios": NROLE, "steps": NSTEPS}


def count_claims(text, where):
    errs = []
    for pat, want in NUMWORDS.items():
        for m in re.finditer(rf"(\d+)[ -]({pat})\b", text):
            if int(m.group(1)) != want:
                errs.append(f"{where}: claims '{m.group(0)}', expected {want}")
    for m in re.finditer(r"(\d+)-minute", text):
        if int(m.group(1)) != LESSON_MIN:
            errs.append(f"{where}: claims '{m.group(0)}', lesson is {LESSON_MIN} minutes")
    for m in re.finditer(r"(\d+) minutes", text):
        if int(m.group(1)) not in {LESSON_MIN, *[x for _, x in STEPS]}:
            errs.append(f"{where}: claims '{m.group(0)}'")
    for m in re.finditer(r"(\d+)-question", text):
        if int(m.group(1)) != NQ:
            errs.append(f"{where}: claims '{m.group(0)}', expected {NQ}")
    for m in re.finditer(r"(\d+) pages", text):
        if int(m.group(1)) not in (TOTAL_PAGES, NPOST, 2, 1, 4):
            errs.append(f"{where}: claims '{m.group(0)}'")
    return errs


def verify_content(d):
    errs = []
    kinds = [p["kind"] for p in d["pages"]]
    exp = ["cover", "teacher", "glance", "script1", "script2", "tps"] + [f"poster{i}" for i in range(1, NPOST + 1)] + \
          ["audience", "performer", "exit", "key", "terms"]
    if kinds != exp or len(kinds) != TOTAL_PAGES:
        errs.append(f"page kinds {kinds} differ from the page map ({TOTAL_PAGES} pages)")
    for p in d["pages"]:
        if PAGEOF.get(p["kind"]) != p["n"]:
            errs.append(f"page {p['n']} is kind {p['kind']}, expected page {PAGEOF.get(p['kind'])}")
        if PAGE_NAMES.get(p["kind"]) != p["name"]:
            errs.append(f"page {p['n']}: name {p['name']}")
    # footers
    for i, ft in enumerate(d["foots"], 1):
        if i == 1:
            continue
        if f"Page {i}" not in ft or "Brian Lotze" not in ft:
            errs.append(f"page {i}: footer '{ft}'")
    # posters
    if [x["i"] for x in d["posters"]] != list(range(1, NPOST + 1)):
        errs.append(f"posters found {[x['i'] for x in d['posters']]}, expected 1..{NPOST}")
    for x in d["posters"]:
        want = POSTERS[x["i"] - 1]
        if x["text"].lower() != want["head"].lower() or x["page"] != P_POST0 + x["i"] - 1:
            errs.append(f"poster {x['i']}: heading '{x['text']}' on page {x['page']}")
        if x["sw"] > x["cw"] + 1 or x["sh"] > x["ch"] + 1:
            errs.append(f"poster {x['i']}: heading clipped ({x['sw']}x{x['sh']} in {x['cw']}x{x['ch']})")
        if x["lines"] > 3:
            errs.append(f"poster {x['i']}: heading wraps to {x['lines']} lines")
        if x["icon"] != want["icon"]:
            errs.append(f"poster {x['i']}: icon {x['icon']}")
    poster_icons = [ic for ic in d["icons"] if ic["page"] >= P_POST0]
    if len(poster_icons) != NPOST:
        errs.append(f"{len(poster_icons)} icons drawn, expected {NPOST}")
    for ic in d["icons"]:
        pad = ic["sw"] * 1.5          # half the stroke sticks out of the geometry, and the padding beyond that is a full stroke
        for k, (lo, hi, lim) in {"x": (ic["x0"], ic["x1"], ic["w"]), "y": (ic["y0"], ic["y1"], ic["h"])}.items():
            if lo < pad - 0.01 or hi > lim - pad + 0.01:
                errs.append(f"icon {ic['icon']}: {k} range {lo:.1f}-{hi:.1f} leaves less than one stroke of padding in its {lim:.0f} box")
    heads = [p["head"] for p in POSTERS]
    if len(set(heads)) != NPOST:
        errs.append("two posters share a heading")
    # lesson habit list agrees with the posters
    glance = d["pagetext"][P_GLANCE - 1]
    for h in heads:
        if h not in glance:
            errs.append(f"lesson at a glance does not list the habit '{h}'")
    hb = d["habits"]
    if [x["i"] for x in hb] != list(range(1, NPOST + 1)):
        errs.append(f"script lists habits {[x['i'] for x in hb]}")
    for x in hb:
        if heads[x["i"] - 1] not in x["text"] or f"Poster {x['i']}, page {P_POST0 + x['i'] - 1}" not in x["text"]:
            errs.append(f"script habit {x['i']} does not match its poster or page: {x['text'][:60]}")
    # checklists
    if [x["i"] for x in d["aud"]] != list(range(1, NAUD + 1)) or len(d["aud"]) != NAUD:
        errs.append(f"audience checklist has {len(d['aud'])} items, expected {NAUD}")
    for x in d["aud"]:
        if x["page"] != P_AUD or x["boxes"] != 1:
            errs.append(f"audience item {x['i']}: page {x['page']}, {x['boxes']} boxes")
        w = AUDIENCE[x["i"] - 1]
        if w[1] is None:
            if x["pref"] or x["rftxt"]:
                errs.append(f"audience item {x['i']} has a poster reference but no poster covers it")
            continue
        p = POSTERS[x["pref"] - 1] if 1 <= x["pref"] <= NPOST else None
        if p is None or x["pref"] != w[1] + 1 or x["ppage"] != P_POST0 + x["pref"] - 1 or f"poster {x['pref']} page {x['ppage']}" not in x["rftxt"].lower():
            errs.append(f"audience item {x['i']}: poster reference '{x['rftxt']}' disagrees with its poster page")
        elif w[2].lower() not in (p["head"] + " " + p["sub"] + " " + p["rem"]).lower():
            errs.append(f"audience item {x['i']} cites Poster {x['pref']} but that poster never mentions '{w[2]}'")
    if [x["i"] for x in d["perf"]] != list(range(1, NPERF + 1)) or len(d["perf"]) != NPERF:
        errs.append(f"performer checklist has {len(d['perf'])} items, expected {NPERF}")
    for x in d["perf"]:
        if x["page"] != P_PERF or x["boxes"] != 1:
            errs.append(f"performer item {x['i']}: page {x['page']}, {x['boxes']} boxes")
    gcount = {}
    for x in d["perf"]:
        gcount[x["group"]] = gcount.get(x["group"], 0) + 1
    if len(d["perfhead"]) != 1 or d["perfhead"][0]["g"] != " · ".join(f"{g} {n}" for g, n in gcount.items()) or sum(gcount.values()) != NPERF:
        errs.append(f"performer header group counts {d['perfhead']} vs items {gcount}")
    for x in d["prefs"]:
        if x["ppage"] != P_POST0 + x["pref"] - 1:
            errs.append(f"poster reference {x['pref']} says page {x['ppage']}")
    texts = [x["text"] for x in d["aud"]] + [x["text"] for x in d["perf"]]
    if len(set(texts)) != len(texts) or "" in texts:
        errs.append("checklist items are not distinct and non-empty")
    pph = [x for x in d["prefs"] if x["page"] == P_PERF]
    if not pph or any(x["pref"] != NPOST for x in pph):
        errs.append("performer checklist must point to the performers poster")
    # exit ticket and key
    tk = d["tickets"]
    if len(tk) != 2 or any(t["page"] != P_EXIT for t in tk):
        errs.append(f"exit ticket page holds {len(tk)} tickets, expected 2")
    for t in tk:
        if [q["n"] for q in t["qs"]] != [str(i) for i in range(1, NQ + 1)]:
            errs.append(f"ticket {t['t']} has questions {[q['n'] for q in t['qs']]}, expected 1..{NQ}")
        if t["hasKey"]:
            errs.append("a ticket shows the answer")
        if t["lines"] != 6:
            errs.append(f"ticket {t['t']} has {t['lines']} answer lines, expected 6")
        for i, q in enumerate(t["qs"]):
            if EXIT_Q[i]["text"] not in q["text"]:
                errs.append(f"ticket {t['t']} question {i + 1} text differs")
    if len(tk) == 2 and tk[0]["qs"] != tk[1]["qs"]:
        errs.append("the two tickets differ")
    key = d["keyqs"]
    if [k["n"] for k in key] != [str(i) for i in range(1, NQ + 1)]:
        errs.append(f"answer key has questions {[k['n'] for k in key]}, expected 1..{NQ}")
    else:
        for i, k in enumerate(key):
            if EXIT_Q[i]["text"] not in k["q"]:
                errs.append(f"answer key question {i + 1} text differs from the ticket")
        k1 = key[0]
        ticket_opts = tk[0]["opts"] if tk else []
        if [(o["l"], o["text"]) for o in k1["opts"]] != [(o["l"], o["text"]) for o in ticket_opts]:
            pass
        okeys = [o for o in k1["opts"] if o["ok"]]
        if len(okeys) != 1 or okeys[0]["l"] != k1["correct"] or f"answer: {k1['correct']}".lower() not in k1["text"].lower():
            errs.append("answer key question 1: exactly one marked correct option that matches the printed answer is required")
        for o in k1["opts"]:
            want = o["l"] == k1["correct"]
            first = o["text"].split(".")[0]
            if first != ("Correct" if want else "Wrong"):
                errs.append(f"answer key option {o['l']} is described as '{first}'")
        if [o["l"] for o in k1["opts"]] != [o["l"] for o in ticket_opts]:
            errs.append("answer key options do not match the ticket's options")
        for o, e in zip(k1["opts"], EXIT_Q[0]["opts"]):
            pass
        for k in key[1:]:
            if k["correct"]:
                errs.append(f"key question {k['n']} claims one right answer but it is open")
    if EXIT_Q[0]["correct"] not in [l for l, _ in EXIT_Q[0]["opts"]]:
        errs.append("correct option is not one of the options")
    # lesson steps
    sr = d["stepsRows"]
    if [s["n"] for s in sr] != list(range(1, NSTEPS + 1)):
        errs.append(f"glance table steps {[s['n'] for s in sr]}")
    for s in sr:
        if s["txt"] != f"{s['min']} min" or STEPS[s["n"] - 1][1] != s["min"] or STEPS[s["n"] - 1][0] != s["name"]:
            errs.append(f"glance step {s['n']}: {s['name']} / {s['txt']}")
    tot = sum(s["min"] for s in sr)
    if len(d["mintotal"]) != 1 or d["mintotal"][0]["v"] != tot or d["mintotal"][0]["txt"] != f"{tot} min":
        errs.append(f"glance total {d['mintotal']} vs sum {tot}")
    if not 20 <= tot <= 25:
        errs.append(f"lesson length {tot} minutes is outside 20-25")
    sh = d["stepheads"]
    if [s["n"] for s in sh] != list(range(1, NSTEPS + 1)):
        errs.append(f"script step headings {[s['n'] for s in sh]}")
    for s in sh:
        if s["min"] != sr[s["n"] - 1]["min"] or f"step {s['n']}: {STEPS[s['n'] - 1][0]}".lower() not in s["txt"].lower() or f"{s['min']} min" not in s["txt"]:
            errs.append(f"script heading {s['n']} '{s['txt']}' disagrees with the glance table")
        if s["page"] != STEP_PAGE[s["n"]]:
            errs.append(f"script step {s['n']} is on page {s['page']}, expected {STEP_PAGE[s['n']]}")
    for s in d["stepRefs"]:
        if not 1 <= s["n"] <= NSTEPS or s["txt"] != f"Step {s['n']}":
            errs.append(f"step reference '{s['txt']}' invalid")
    for s in d["stepRefs"]:
        if s["page"] == P_TPS and s["n"] != 4:
            errs.append("think-pair-share page must reference step 4")
        if s["page"] == P_EXIT and s["n"] != 6:
            errs.append("exit ticket page must reference step 6")
    names = [x["name"].lower() for x in sr]
    if names[3] != "think-pair-share" or names[4] != "show me" or names[5] != "exit ticket":
        errs.append("step names for 4-6 changed; the think-pair-share, role-play and exit ticket page references must follow")
    if len(d["disc"]) != NDISC or [x["i"] for x in d["disc"]] != list(range(1, NDISC + 1)):
        errs.append(f"{len(d['disc'])} discussion questions found, expected {NDISC}")
    if any(not x["text"].endswith("?") and not x["text"].endswith(".") for x in d["disc"]):
        errs.append("a discussion question is not a complete sentence")
    if [r["l"] for r in d["roles"]] != [r[0] for r in ROLES] or len(d["roles"]) != NROLE:
        errs.append(f"{len(d['roles'])} role-play scenarios found, expected {NROLE}")
    # page references: every "page N" / "pages N-M" printed in the body is a data-ref span whose number matches the real page
    for r in d["refs"]:
        if PAGEOF[r["kind"]] != r["n"]:
            errs.append(f"reference on page {r['page']} says {r['n']} for {r['kind']}")
        want = f"{'Pages' if r['kind2'] else 'Page'} {r['n']}" if r["txt"][0] == "P" else f"{'pages' if r['kind2'] else 'page'} {r['n']}"
        if r["kind2"]:
            want += f"–{r['n2']}"
            if PAGEOF[r["kind2"]] != r["n2"]:
                errs.append(f"range reference on page {r['page']} ends at {r['n2']}, but {r['kind2']} is page {PAGEOF[r['kind2']]}")
        if r["txt"] != want:
            errs.append(f"reference text '{r['txt']}' vs '{want}'")
    refs_by_page = {}
    for r in d["refs"]:
        refs_by_page[r["page"]] = refs_by_page.get(r["page"], 0) + 1
    manual = 0
    for i, t in enumerate(d["pagetextNoFoot"], 1):
        found = len(re.findall(r"[Pp]ages? \d+", t))
        # poster references on checklists are checked through data-pref
        found -= len(re.findall(r"page \d+", " ".join(x["txt"] for x in d["prefs"] if x["page"] == i)))
        found -= len(re.findall(r"(?i)\bpage \d+", " ".join(x["rftxt"] for x in d["aud"] if x["page"] == i)))
        if found != refs_by_page.get(i, 0):
            errs.append(f"page {i}: {found} 'page N' mentions in text but {refs_by_page.get(i, 0)} checked references")
        manual += found
    # the footer on the exit ticket page names the key page
    if f"Answer key on page {P_KEY}" not in d["foots"][P_EXIT - 1]:
        errs.append("exit ticket footer does not name the answer key page")
    # teacher notes list
    tn = d["pagetext"][P_TEACH - 1]
    for need in (f"({TOTAL_PAGES} pages)", f"{NSTEPS} steps, {LESSON_MIN} minutes", f"{NDISC} discussion questions", f"{NROLE} role-play scenarios",
                 f"{NPOST} posters", f"{NAUD} audience items", f"{NPERF} performer items", f"{NQ} exit ticket questions", "Grades 3–5", "Grades 6–8", "vary by venue, style and culture"):
        if need.lower() not in tn.lower():
            errs.append(f"teacher notes: missing '{need}'")
    gt = d["pagetext"][P_GLANCE - 1]
    for need in (f"{NSTEPS} steps", f"{LESSON_MIN}-minute", "differ from venue to venue and culture to culture"):
        if need.lower() not in gt.lower():
            errs.append(f"lesson at a glance: missing '{need}'")
    tp = d["pagetext"][P_TERMS - 1]
    if f"{TOTAL_PAGES} pages in all" not in tp:
        errs.append("terms page: page list does not match")
    if DISCLOSURE not in tp:
        errs.append("terms page: disclosure line missing or changed")
    alltext = " ".join(d["pagetextNoFoot"])
    low = alltext.lower()
    for w in UK_SPELLINGS:
        if w in low:
            errs.append(f"non-US spelling '{w}' in the pages")
    for w in QA_WORDS:
        if w in low:
            errs.append(f"internal QA wording '{w}' in the pages")
    if re.search(SEASONAL, low):
        errs.append("seasonal word in the pages")
    if "notation" in low.replace(DISCLOSURE.lower(), ""):
        errs.append("the pages claim notation but this product has none")
    errs += count_claims(alltext, "pages")
    # sentence checks: no list item or paragraph that ends without punctuation
    for i, t in enumerate(d["pagetextNoFoot"], 1):
        if re.search(r"\b(and|or|the|a|to|of)\s*$", t):
            errs.append(f"page {i}: text ends mid-sentence")
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
        name = os.path.basename(p)
        if im.size != (2000, 2000):
            errs.append(f"{name}: not 2000x2000")
            continue
        px = im.load()
        rows = [sum(1 for x in range(0, 2000, 8) if px[x, y] < 200) for y in range(0, 2000, 2)]
        ytop = 2000
        while ytop > 1000 and px[2, ytop - 1] < 40:
            ytop -= 1
        run = best = 0
        for y in range(120, ytop, 2):
            if rows[y // 2] == 0:
                run += 2
                best = max(best, run)
            else:
                run = 0
        if best > 200:
            errs.append(f"{name}: blank band of {best}px (more than 10% of the image)")
        last = max((y for y in range(0, ytop, 2) if rows[y // 2] > 0), default=0)
        if ytop - last > 200:
            errs.append(f"{name}: {ytop - last}px blank above the bottom band")
        # rendered-pixel edge check: nothing but white may touch the top, left or right edge above the black band;
        # the band itself must fill the bottom edge completely (no art or shadow poking through it)
        e = 4
        dark = 0
        for y in range(0, ytop - 4):
            for x in list(range(0, e)) + list(range(2000 - e, 2000)):
                if px[x, y] < 235:
                    dark += 1
        for y in range(0, e):
            for x in range(2000):
                if px[x, y] < 235:
                    dark += 1
        if dark:
            errs.append(f"{name}: {dark} non-white pixels touch the top, left or right edge (art or text is clipped or too close)")
        for y in range(1996, 2000):
            if any(px[x, y] > 40 for x in range(2000)):
                errs.append(f"{name}: bottom edge row {y} is not solid black")
                break
        if name != "cover.png":
            gapdark = sum(1 for y in range(ytop - 14, ytop - 2) for x in range(0, 2000, 4) if px[x, y] < 200)
            if gapdark > 20:
                errs.append(f"{name}: page shots or art run into the black band (no clear gap above it)")
        # art padding: first and last non-white column/row of the content area (above the band) keep a margin of at least 40 px
        cols = [x for x in range(2000) if any(px[x, y] < 235 for y in range(0, ytop - 4, 4))]
        if cols and (min(cols) < 40 or max(cols) > 1959):
            errs.append(f"{name}: content comes within 40px of the left or right edge ({min(cols)}..{max(cols)})")
    # the library art: its opaque pixels keep clear of the image edge, so scaling it never clips it
    for f in ("hero.png", "spot-music-stand.png"):
        a = Image.open(os.path.join(ART, f)).getchannel("A").point(lambda v: 255 if v > 100 else 0)
        bb = a.getbbox()
        if not bb or bb[0] < 5 or bb[1] < 5 or bb[2] > a.width - 5 or bb[3] > a.height - 5:
            errs.append(f"art/{f}: opaque pixels come within 5px of the image edge {bb}")
    return errs


def verify_files():
    errs = []
    from pypdf import PdfReader
    for p in [PDF, PREVIEW_PDF, COVER_PNG, *PREVIEW_PNGS, UPLOAD, TPT_JSON, os.path.join(TPT, "STYLE.md"), RENDER_JS,
              os.path.join(ART, "hero.png"), os.path.join(ART, "spot-music-stand.png")]:
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
        if int(m.group(1)) not in (TOTAL_PAGES, NPOST, 2):
            errs.append(f"PDF text claims '{m.group(0)}', PDF has {TOTAL_PAGES}")
    if f"{TOTAL_PAGES} pages" not in allpdf:
        errs.append("PDF never states its page count")
    prd = PdfReader(PREVIEW_PDF)
    want_pages = [SHOT_PAGES[k] for k in PREVIEW_ORDER]
    for i in range(4):
        t = prd.pages[i].extract_text() or ""
        if t.count("PREVIEW") != 1:
            errs.append(f"preview PDF page {i + 1}: expected exactly one PREVIEW watermark")
        if f"Page {want_pages[i]}" not in t.replace("\n", " "):
            errs.append(f"preview PDF page {i + 1} is not page {want_pages[i]} of the product")
    errs += verify_images()
    for h in ("cover.html", "p1.html", "p2.html", "p3.html"):
        p = os.path.join(BUILD, h)
        if os.path.exists(p):
            s = open(p).read()
            txt = re.sub(r"<[^>]+>", " ", re.sub(r"<style>.*?</style>", "", s, flags=re.S))
            errs += count_claims(txt, h)
            if "swm" in s or "PREVIEW" in s:
                errs.append(f"{h}: has its own watermark layer (the page shots already carry one)")
            if "_art" in s:
                errs.append(f"{h}: references tpt/_art")
            for m in re.finditer(r'<div class="lbl">([^<]*)<span>', s):
                if m.group(1) not in PAGE_NAMES.values():
                    errs.append(f"{h}: label '{m.group(1)}' is not a real page name")
    up = open(UPLOAD).read()
    m = re.search(r"^## 1\. Title\s*\n+```\n(.+?)\n```", up, re.M | re.S)
    if not m:
        errs.append("UPLOAD.md: title block not found")
    else:
        title = m.group(1).strip()
        if len(title) > 80:
            errs.append(f"UPLOAD.md: title is {len(title)} chars (max 80)")
        if re.search(SEASONAL, title, re.I):
            errs.append("UPLOAD.md: seasonal word in the title")
    for need in (DISCLOSURE, f"${PRICE}", f"{TOTAL_PAGES} pages", f"{NPOST} printable posters", f"{NAUD} audience items", f"{NPERF} performer items",
                 f"{NQ} exit ticket questions", f"{NDISC} discussion questions", f"{NROLE} role-play scenarios", f"{NSTEPS} steps that add up to {LESSON_MIN} minutes"):
        if need not in up:
            errs.append(f"UPLOAD.md: missing '{need}'")
    errs += count_claims(up.split("## 3. Grades")[0].split("## 1. Title")[1], "UPLOAD.md")
    sec = up.split("## 5. Page count by section")[1].split("##")[0]
    nums = [int(x) for x in re.findall(r"^- (?!Total)[^\n]*: (\d+)$", sec, re.M)]
    if sum(nums) != TOTAL_PAGES:
        errs.append(f"UPLOAD.md page list sums to {sum(nums)}, PDF has {TOTAL_PAGES}")
    for m in re.finditer(r"^• .*?\((\d+) pages?\)", up, re.M):
        pass
    desc = up.split("## 2. Description")[1].split("## 3.")[0]
    bullets = [int(x) for x in re.findall(r"\((?:[^()]*? )?(\d+) pages?\)\s*$", desc, re.M)]
    if sum(bullets) != TOTAL_PAGES:
        errs.append(f"UPLOAD.md description bullets sum to {sum(bullets)} pages, PDF has {TOTAL_PAGES}")
    if re.search("|".join(QA_WORDS), up, re.I):
        errs.append("UPLOAD.md: forbidden claim or internal QA wording")
    for w in UK_SPELLINGS:
        if w in desc.lower():
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
    for p in shots["pages"]:
        if p["kind"] != "cover" and p["wms"] != 1:
            errs.append(f"shots: page {p['n']} has {p['wms']} watermarks, expected 1")
    for p in res["pages"]:
        if p["wms"] != 0:
            errs.append(f"resource: page {p['n']} has a watermark")
    for k in PREVIEW_ORDER + [f"poster{i}" for i in range(2, NPOST + 1)] + ["performer"]:
        n = SHOT_PAGES[k]
        gap = shots["gaps"][n - 1]
        if gap > 105:
            errs.append(f"preview page {k} (page {n}): {gap}px blank above the footer (max 105)")
    errs += verify_files()
    if errs:
        print("CHECK FAILED")
        print("\n".join(" - " + e for e in errs[:80]))
        sys.exit(1)
    print(f"CHECK OK: {NPOST} posters (headings, icons inside their boxes, no clipped text), {NAUD} audience + {NPERF} performer checklist items with tick boxes, "
          f"{NQ} exit ticket questions x 2 tickets and a matching key, {NSTEPS} lesson steps = {LESSON_MIN} minutes, every page reference and step reference read back; "
          f"layout clear of footers and edges; PDF {TOTAL_PAGES} Letter pages, preview 4 (one watermark each), fonts embedded; "
          f"cover and previews 2000x2000 with clear edges; UPLOAD.md and tpt.json agree.")


if __name__ == "__main__":
    if "--check" in sys.argv:
        check()
    else:
        build()
