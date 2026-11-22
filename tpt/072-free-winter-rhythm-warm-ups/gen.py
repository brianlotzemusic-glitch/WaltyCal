#!/usr/bin/env python3
"""FREE Rhythm Warm-Ups, Clap and Say Rhythm Reading, Gr 2-5 (TpT 072): build the resource and verify it.

    python3 gen.py           build everything (PDFs, PNGs, UPLOAD.md, tpt.json) into this folder
    python3 gen.py --check   re-read the rendered HTML and verify every rhythm line, key line, page number, layout and file

Four warm-up pages (ta and ti-ti, quarter rests, half and whole notes, an echo chain), each line of 4/4 drawn in code (rhythm.py).
`--check` does not trust the data: it parses the rendered SVG of every rhythm line, finds the noteheads, stems, beams and rests from
their real geometry, derives each bar's beats (must be 4), tests stem side and direction, beams, the syllable and winter-word rows
(syllable count of every word must match its note), recomputes the teacher key from the parsed notation and compares it with the key
page text, measures notation padding on rendered pixels, and checks the layout (8 px footer gap, blank bands, watermarks),
page numbers, cross-references, UPLOAD.md and tpt.json.
"""
import json
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from html import escape

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rhythm as RH  # noqa: E402

TPT = os.path.dirname(HERE)
FONTS = os.path.join(TPT, "fonts")
BUILD = os.path.join(HERE, "build")
RENDER_JS = os.path.join(TPT, "tools", "render.js")
HERO = os.path.join(HERE, "art", "hero.png")

SLUG = "free-rhythm-warm-ups"
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
TITLE = "Rhythm Warm-Ups"
LISTING_TITLE = "FREE Rhythm Warm-Ups, Clap and Say Rhythm Reading, Gr 2-5"
PRICE = "0.00"
TAGS = ["Winter", "Bell Ringers", "Activities", "Worksheets", "Printables"]
SUBJECTS = ["Music"]
GRADES = ["2nd-grade", "3rd-grade", "4th-grade", "5th-grade"]

# ------------------------------------------------------------------ the rhythm data
# A line is a list of bars; a bar is a string of "SYMBOL:word" tokens. Symbols: Q ta, E ti-ti, R shh (rest), H ta-a, W ta-a-a-a.
# Words are winter cue words with one part (syllable) per spoken part; held words are stretched (sno-ow = 2 beats).
REST_WORD = "(rest)"
NOWORDS = "Say the syllables"
WARMUPS = [
    {"n": 1, "name": "Warm-up 1: ta and ti-ti", "tag": "WARM-UP 1", "tagline": "Clap and say",
     "direction": "Teacher: lead the class to say the words, then clap and say ta and ti-ti.",
     "bank": "<b>Ta</b> is one beat (a quarter note): snow, sled, hat, boot, ice, cold, frost. <b>Ti-ti</b> is two sounds in one beat "
             "(two eighth notes joined by a beam): sled-ding, co-coa, mit-tens, pen-guin, snow-man.",
     "lines": [["Q:snow Q:sled Q:hat Q:boot", "Q:ice Q:cold Q:frost Q:snow"],
               ["Q:snow E:sled-ding Q:ice Q:cold", "E:co-coa E:mit-tens Q:hat Q:boot"],
               ["E:pen-guin E:snow-man Q:snow Q:sled", "Q:hat E:co-coa E:sled-ding Q:frost"]]},
    {"n": 2, "name": "Warm-up 2: quarter rests", "tag": "WARM-UP 2", "tagline": "Clap, say and shh",
     "direction": "Teacher: on a rest, say shh, keep your hands apart and tap the beat on your knees.",
     "bank": "A <b>quarter rest</b> is one beat of silence. Say <b>shh</b> and do not clap. Every bar still has four beats, so count them all: "
             "1 2 3 4.",
     "lines": [["Q:snow Q:sled R:(rest) Q:boot", "Q:ice R:(rest) Q:cold R:(rest)"],
               ["E:co-coa R:(rest) Q:hat Q:snow", "Q:sled Q:ice E:mit-tens R:(rest)"],
               ["E:pen-guin E:snow-man R:(rest) Q:cold", "Q:frost E:sled-ding R:(rest) Q:snow"]]},
    {"n": 3, "name": "Warm-up 3: half and whole notes", "tag": "WARM-UP 3", "tagline": "Clap and hold",
     "direction": "Teacher: clap once on a half or whole note, then hold the sound and count the beats.",
     "bank": "A <b>half note</b> lasts two beats: say ta-a. A <b>whole note</b> lasts four beats: say ta-a-a-a. Stretch the word to fill the "
             "beats: <span style='white-space:nowrap'>sno-ow</span>, <span style='white-space:nowrap'>sno-o-o-ow</span>.",
     "lines": [["H:sno-ow H:co-old", "W:sno-o-o-ow"],
               ["Q:snow Q:sled H:sle-ed", "H:i-ice Q:hat Q:boot"],
               ["H:sno-ow E:sled-ding Q:ice", "W:co-o-o-old"]]},
    {"n": 4, "name": "Warm-up 4: rhythm echo chain", "tag": "WARM-UP 4", "tagline": "Clap and echo",
     "direction": "Teacher: clap one bar, let the class echo it, then clap the whole line together.",
     "bank": "Each chain mixes ta, ti-ti, shh, ta-a and ta-a-a-a. Say the syllables as you clap.",
     "lines": [["Q Q E Q", "Q R Q Q", "E E Q Q", "H Q Q"],
               ["E Q Q E", "H R Q", "Q E E Q", "W"],
               ["Q Q Q R", "E Q R Q", "H E Q", "Q Q H"],
               ["Q E Q R", "E E E E", "H H", "W"]]},
]
SYLLABLES = {  # real English syllable counts for every cue word (base word)
    "snow": 1, "sled": 1, "hat": 1, "boot": 1, "ice": 1, "cold": 1, "frost": 1,
    "sled-ding": 2, "co-coa": 2, "mit-tens": 2, "pen-guin": 2, "snow-man": 2,
}
HELD = {"sno-ow": "snow", "sno-o-o-ow": "snow", "co-old": "cold", "co-o-o-old": "cold", "sle-ed": "sled", "i-ice": "ice"}
PARTS = RH.PARTS
BEATS = RH.BEATS


def parse_bar(s):
    out = []
    for tok in s.split():
        sym, _, word = tok.partition(":")
        out.append((sym, word or None))
    return out


def line_bars(line):
    return [parse_bar(b) for b in line]


def bar_beats(bar):
    return sum(BEATS[s] for s, _ in bar)


def has_words(w):
    return w["n"] != 4


for _w in WARMUPS:   # data sanity at import: the build refuses an off-meter bar
    for _ln in _w["lines"]:
        for _b in line_bars(_ln):
            assert bar_beats(_b) == 4, (_w["n"], _b)

# ------------------------------------------------------------------ page map
P_COVER, P_W1, P_W2, P_W3, P_W4, P_KEY, P_FULL, P_TERMS = 1, 2, 3, 4, 5, 6, 7, 8
TOTAL_PAGES = P_TERMS
PAGE_NAMES = {P_COVER: "cover", P_W1: WARMUPS[0]["name"], P_W2: WARMUPS[1]["name"], P_W3: WARMUPS[2]["name"], P_W4: WARMUPS[3]["name"],
              P_KEY: "Teacher answer key", P_FULL: "See the full sets", P_TERMS: "Terms of use and credits"}
XREFS = []   # (page it is printed on, page it points to, text)


def xref(frm, to, text):
    XREFS.append((frm, to, text))
    return text


# ------------------------------------------------------------------ CSS / frame
def font_css():
    f = os.path.relpath(FONTS, BUILD)
    faces = [("Oswald", 300, "normal", "oswald-latin-300-normal"), ("Oswald", 500, "normal", "oswald-latin-500-normal"),
             ("Oswald", 700, "normal", "oswald-latin-700-normal"), ("Oswald", 400, "normal", "oswald-latin-500-normal"),
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
.top .t { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; letter-spacing: .01em; line-height: 1; font-size: 20pt; white-space: nowrap; }
.top .t small { display: block; font-family: 'Oswald'; font-weight: 300; text-transform: none; font-size: 12pt; letter-spacing: 0; margin-top: 3pt; }
.top .tag { flex: none; white-space: nowrap; text-align: right; }
.tag .lv { display: inline-block; background: #000; color: #fff; font-family: 'Oswald'; font-weight: 700; font-size: 15pt; padding: 3pt 9pt 4pt; border-radius: 4pt; letter-spacing: .04em; }
.tag .lv.ak { background: ACCENT; }
.tag .ln { font-family: 'Oswald'; font-weight: 300; font-size: 11pt; margin-top: 3pt; }
.foot { display: flex; justify-content: space-between; font-size: 8.5pt; color: #333; border-top: .8pt solid #000; padding-top: 3pt; }
.wm { position: absolute; left: 50%; top: 50%; transform: translate(-50%, -50%) rotate(-38deg); font-family: 'Oswald'; font-weight: 700;
      font-size: 150pt; color: rgba(0,0,0,.13); letter-spacing: .06em; white-space: nowrap; pointer-events: none; z-index: 9; }
.doc h1 { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 30pt; margin: 0 0 4pt; line-height: 1; }
.doc h2 { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 14pt; margin: 9pt 0 3pt; letter-spacing: .02em; }
.doc p, .doc li { font-size: 10.8pt; line-height: 1.34; margin: 0 0 5pt; }
.doc ul { margin: 0 0 4pt; padding-left: 16pt; }
.doc .rule { border-bottom: 2.2pt solid #000; margin-bottom: 8pt; padding-bottom: 6pt; }
.doc table { border-collapse: collapse; width: 100%; table-layout: fixed; font-size: 10.4pt; margin: 2pt 0 4pt; }
.doc td, .doc th { border: 1pt solid #000; padding: 3pt 6pt; text-align: left; vertical-align: middle; }
.doc th { font-family: 'Oswald'; font-weight: 500; text-transform: uppercase; font-size: 9.5pt; background: #000; color: #fff; }
.terms p, .terms li { font-size: 12.4pt !important; }
.terms h2 { font-size: 15pt !important; margin-top: 12pt !important; }
.small { font-size: 9pt !important; color: #333; }
.box { border: 1.3pt solid #000; border-radius: 7pt; padding: 7pt 10pt 4pt; margin: 6pt 0; }
.box h3 { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 12.5pt; margin: 0 0 3pt; letter-spacing: .02em; }
.box p { margin: 0 0 4pt !important; font-size: 10.6pt !important; }
.nd { display: flex; align-items: flex-end; gap: 6pt; font-size: 10.5pt; margin: 7pt 0 0; }
.nd .ln { flex: 1; border-bottom: 1pt solid #000; height: 11pt; }
.inst { font-size: 11.6pt; line-height: 1.3; margin: 8pt 0 0; font-weight: 600; }
.stack { flex: 1; display: flex; flex-direction: column; justify-content: space-between; gap: 5pt; padding: 6pt 0 12px; }
.part { border: 1.3pt solid #000; border-radius: 7pt; padding: 4pt 11pt 4pt; }
.part .lab { display: flex; align-items: center; gap: 8pt; font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 12pt; letter-spacing: .05em; margin-bottom: 1pt; }
.part .lab i { font-style: normal; background: ACCENT; color: #fff; padding: 1pt 8pt 2pt; border-radius: 3pt; }
.part .lab span { font-family: 'Oswald'; font-weight: 300; text-transform: none; letter-spacing: 0; font-size: 10.5pt; }
.part svg { display: block; margin: 2pt 0; }
.part .turn { border-top: 1pt dashed #777; margin-top: 3pt; padding-top: 3pt; }
.cover { align-items: center; justify-content: space-between; padding: 0.55in 0.6in 0.5in; }
.store { font-family: 'Oswald'; font-weight: 500; font-size: 13pt; letter-spacing: .32em; text-transform: uppercase; }
.ctitle { text-align: center; }
.ctitle .a { font-family: 'Oswald'; font-weight: 700; font-size: 46pt; line-height: 1; letter-spacing: .02em; }
.ctitle .b { font-family: 'Oswald'; font-weight: 700; white-space: nowrap; font-size: 58pt; line-height: .95; letter-spacing: .01em; }
.ctitle .c { font-family: 'Oswald'; font-weight: 300; font-size: 17pt; margin-top: 8pt; }
.cband { width: 100%; background: #000; color: #fff; text-align: center; font-family: 'Oswald'; font-weight: 500; font-size: 14pt;
         letter-spacing: .08em; text-transform: uppercase; padding: 8pt 0 9pt; border-radius: 4pt; white-space: nowrap; }
.cband em { font-style: normal; color: ACCENT; }
.prod { border: 1.3pt solid #000; border-radius: 7pt; padding: 10pt 14pt 7pt; margin: 9pt 0; }
.prod .pt { font-family: 'Source Sans 3'; font-weight: 700; font-size: 12.4pt; line-height: 1.22; margin: 0 0 2pt; }
.prod .pm { font-family: 'Oswald'; font-weight: 500; text-transform: uppercase; letter-spacing: .06em; font-size: 9.6pt; color: ACCENT; margin: 0 0 2pt; }
.prod p { font-size: 11.4pt; line-height: 1.28; margin: 0 0 3pt; }
.key td.k { font-family: 'Oswald'; font-weight: 500; width: 17%; font-size: 10pt; letter-spacing: .04em; }
.key td.w { width: 43%; }
.key td.s { width: 40%; color: #222; }
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


def pg_foot(page, extra=""):
    return foot(COPY + (f" · {extra}" if extra else ""), f"Page {page}")


# ------------------------------------------------------------------ drawings
LINE_W = 672.0   # svg width in px inside a .part box (box inner width is about 687 px)


def rh_svg(bars, rows, words=None, sp=8, label=None):
    n = len(bars)
    bw = RH.fit_bw(LINE_W, n, sp)
    return RH.rhythm_svg(bars, sp=sp, bw=bw, rows=rows, words=words, label=label)[0]


def line_svgs(w, li, line):
    """The rhythm svg and the blank 'my turn' svg for one line."""
    bars = line_bars(line) if w["n"] != 4 else [[(s, None) for s in b.split()] for b in line]
    pats = ["".join(s for s, _ in b) for b in bars]
    words = [[(wd if wd != "(rest)" else REST_WORD) for _, wd in b] for b in bars] if has_words(w) else None
    rows = ("num", "word", "syl") if has_words(w) else ("num", "syl")
    sp = 7.6 if has_words(w) else 5.6
    svg = rh_svg(pats, rows, words, sp=sp, label=f"w{w['n']}l{li + 1}")
    blank = rh_svg([None] * len(pats), rows, None, sp=sp, label=f"w{w['n']}l{li + 1}turn")
    return svg, blank


def warm_page(w, wm=False):
    page = P_W1 + w["n"] - 1
    parts = []
    for li, line in enumerate(w["lines"]):
        svg, blank = line_svgs(w, li, line)
        parts.append(
            f'<div class="part"><div class="lab"><i>Line {li + 1}</i><span>Clap and say it</span></div>{svg}'
            f'<div class="turn"><div class="lab"><i style="background:#000">My turn</i><span>Write {len(line)} bars of 4 beats, then clap them for a partner.</span></div>{blank}</div></div>')
    return (f'<section class="page doc" data-page="{page}">{wm_div(wm)}{top_block(w["name"], w["tag"], w["tagline"])}{NAME_DATE}'
            f'<p class="inst">{w["direction"]}</p><div class="box" style="margin-bottom:0"><p>{w["bank"]}</p></div>'
            f'<div class="stack">{"".join(parts)}</div>{pg_foot(page, xref(page, P_KEY, f"Teacher key on page {P_KEY}"))}</section>')


def key_rows():
    rows = []
    for w in WARMUPS:
        page = P_W1 + w["n"] - 1
        for li, line in enumerate(w["lines"]):
            bars = line_bars(line)
            words = " | ".join(" ".join(wd for _, wd in b) for b in bars) if has_words(w) else NOWORDS
            syl = " | ".join(" ".join(RH.SYL[s] for s, _ in b) for b in bars)
            rows.append((f"Page {page}, line {li + 1}", words, syl))
    return rows


def key_page(wm=False):
    rows = "".join(f'<tr><td class="k">{a}</td><td class="w">{b}</td><td class="s">{c}</td></tr>' for a, b, c in key_rows())
    return (f'<section class="page doc key" data-page="{P_KEY}">{wm_div(wm)}{top_block(PAGE_NAMES[P_KEY], "KEY", "Rhythms in words", ak=True)}'
            f'<p class="inst" style="font-weight:400;margin-top:8pt">How each line sounds when clapped, in words. A bar line is shown as |. '
            f'Every bar is four beats; <b>shh</b> is a silent beat and a held note is one clap and a long sound.</p>'
            f'<table><thead><tr><th>Line</th><th>Winter words</th><th>Syllables</th></tr></thead><tbody>{rows}</tbody></table>'
            f'<div class="box"><h3>How to use the warm-ups</h3>'
            f'<p>Use one page a day as a five-minute warm-up, or all four in one lesson. Say the words first, then the syllables, then clap. '
            f'On the My turn staves, children draw their own two or four bars on the middle line, then clap them for a partner. '
            f'These warm-ups do not cite standards; match them to your own music goals.</p></div>'
            f'<div style="flex:1"></div>{pg_foot(P_KEY)}</section>')


PRODUCTS = [
    ("Winter Rhythm Bingo | 30 Unique Cards, Sixteenths & Dotted Rhythms | Grades 3-6", "40 pages · Grades 3-6",
     "Clap a four-beat rhythm and students find it on their card. 30 unique bingo cards, 36 rhythm calling cards with counts and a caller's checklist."),
    ("Beat vs Rhythm Movement Cards and Echo Strips, Music Games, K-2", "15 pages · Grades K-2",
     "24 movement cards and 12 rhythm echo strips for your younger students, with a clap-and-echo game."),
    ("Music Symbols Scavenger Hunt, Find & Color Review Pages, Gr 3-5", "21 pages · Grades 3-5",
     "Six snowy scenes with 130 hidden music symbols to find, circle and count, plus two review pages and answer keys."),
    ("Winter Color by Note | Rhythm, Treble & Bass Clef Worksheets, Answer Keys", "58 pages · Grades 1-5",
     "9 pictures at three levels: 27 worksheets and 27 full-color answer keys."),
    ("Music Listening Response & Readings, Around the World Music Edition, Gr 3-6", "21 pages · Grades 3-6",
     "Five short readings about celebrations around the world and five listening response pages."),
]


def full_page(wm=False):
    prods = "".join(f'<div class="prod"><div class="pt">{escape(t)}</div><div class="pm">{m}</div><p>{d}</p></div>' for t, m, d in PRODUCTS)
    return (f'<section class="page doc" data-page="{P_FULL}">{wm_div(wm)}{doc_head("See the Full Sets", "Thank you for trying these free rhythm warm-ups!")}'
            f'<p>If your students enjoyed these four warm-ups, there is more in the {BRAND} store. Find us on Teachers Pay Teachers and search for any title below, '
            f'or follow the store to hear about new sets.</p>{prods}'
            f'<div class="box"><h3>Follow the store</h3><p>Following {BRAND} on Teachers Pay Teachers tells you when new sets arrive.</p></div><p class="small">Titles, grades and page counts are as listed in the store.</p>'
            f'<div style="flex:1"></div>{pg_foot(P_FULL)}</section>')


def terms_page(wm=False):
    return (f'<section class="page doc terms" data-page="{P_TERMS}">{wm_div(wm)}{doc_head("Terms of Use and Credits", "Thank you for downloading this free resource!")}'
            f'<p>© {YEAR} {STORE}. {BRAND} by {STORE}. All rights reserved. This free download is for <b>one teacher</b> to use with their own students.</p>'
            f'<h2>You may</h2><ul><li>Print and copy pages for your own classroom and students.</li>'
            f'<li>Share pages with your own students through a password-protected class site or learning platform.</li>'
            f'<li>Use the pages with your own students when you have a substitute teacher.</li></ul>'
            f'<h2>You may not</h2><ul><li>Share, email or copy this resource for other teachers, a whole school or a district. Colleagues can download their own free copy on Teachers Pay Teachers.</li>'
            f'<li>Post any part of it on a public website, shared drive or social media.</li>'
            f'<li>Sell, give away or claim any part of it as your own, or edit it into a new product.</li></ul>'
            f'<h2>Questions?</h2><p>Please use the Q&amp;A tab on the {BRAND} by {STORE} store on Teachers Pay Teachers. If something looks wrong, let me know there and I will fix it.</p>'
            f'<h2>Credits</h2><ul>'
            f'<li>The warm-ups, rhythms, key and pages are original work, {BRAND} by {STORE}.</li>'
            f'<li>The cover illustration is made with AI tools. The notation, tables and text are drawn in code.</li>'
            f'<li>Music notation font: Bravura © Steinberg Media Technologies GmbH, SIL Open Font License 1.1.</li>'
            f'<li>Text fonts: Oswald (The Oswald Project Authors) and Source Sans 3 (Adobe), SIL Open Font License 1.1.</li>'
            f'<li>No songs, lyrics or copyrighted characters are used.</li></ul>'
            f'<h2>What is in this file ({TOTAL_PAGES} pages)</h2><p>Page 1 cover, pages {P_W1}–{P_W4} the four warm-ups, page {P_KEY} teacher answer key, page {P_FULL} see the full sets and page {P_TERMS} these terms.</p>'
            f'<p class="small">{DISCLOSURE}</p><div style="flex:1"></div>{pg_foot(P_TERMS)}</section>')


def cover_art_img(height):
    return f'<img src="../art/hero.png" alt="" style="display:block;height:{height};width:auto">'


def cover_page():
    return (f'<section class="page cover"><div class="store">{BRAND}</div>'
            f'<div style="height:5in;display:flex;align-items:center;justify-content:center">{cover_art_img("5in")}</div>'
            f'<div class="ctitle"><div class="a">FREE</div><div class="b">RHYTHM WARM-UPS</div>'
            f'<div class="c">Clap and say rhythm reading · teacher led</div></div>'
            f'<div class="cband">Grades 2–5 <em>·</em> 4 warm-ups <em>·</em> {TOTAL_PAGES} pages</div></section>')


def full_pages():
    XREFS.clear()
    pages = [cover_page()] + [warm_page(w) for w in WARMUPS] + [key_page(), full_page(), terms_page()]
    assert len(pages) == TOTAL_PAGES, len(pages)
    return pages


PREVIEW_PAGES = [P_W1, P_W3, P_W4, P_KEY]


def preview_pages():
    return [warm_page(WARMUPS[0], True), warm_page(WARMUPS[2], True), warm_page(WARMUPS[3], True), key_page(True)]


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
        f'<img src="../art/hero.png" alt="" style="display:block;height:640px;width:auto;margin-top:-70px">'
        f'<div><div class="hd" style="font-size:60px">FREE</div><div class="hd" style="font-size:106px">Rhythm Warm-Ups</div>'
        f'<div class="sub" style="font-size:28px;margin-top:8px">Clap and say rhythm reading · teacher led</div></div>'
        f'</div><div class="band">Grades 2–5 <em>·</em> 4 warm-ups <em>·</em> {TOTAL_PAGES} pages</div></div>')


def swm_over(size=230):
    return f'<div class="swm" style="font-size:{size}px">PREVIEW</div>'


def shot(src, w):
    return f'<div class="shot" style="width:{w}px"><img src="{src}"></div>'


def pill_row(items):
    return '<div style="display:flex;gap:18px">' + "".join(f'<div class="pill">{t}</div>' for t in items) + "</div>"


def trio(img, caps, head, sub, pills, bandtxt):
    shots = "".join(
        f'<div style="width:290px;display:flex;flex-direction:column;align-items:center">{shot(img[i], 290)}'
        f'<div class="lbl" style="font-size:20px;margin-top:20px">{caps[i][0]}</div>'
        f'<div style="font-family:Oswald;font-weight:300;font-size:20px;line-height:1.25;text-align:center;margin-top:8px;width:270px">{caps[i][1]}</div></div>' for i in range(3))
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div><div class="hd" style="font-size:72px;margin-top:28px">{head}</div>'
        f'<div class="sub" style="font-size:28px;margin-top:10px">{sub}</div>'
        f'<div style="flex:1;display:flex;flex-direction:column;align-items:center;justify-content:space-evenly;padding-bottom:70px">'
        f'<div style="display:flex;gap:22px;align-items:flex-start">{shots}</div>{pill_row(pills)}</div>'
        f'{swm_over(230)}<div class="band">{bandtxt}</div></div>')


def pair(a, b, head, sub, band):
    cells = "".join(f'<div style="width:380px">{shot(src, 380)}<div class="lbl">{lab}<span>{sb}</span></div></div>' for src, lab, sb in (a, b))
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div><div class="hd" style="font-size:72px;margin-top:24px">{head}</div>'
        f'<div class="sub" style="font-size:27px;margin-top:8px">{sub}</div>'
        f'<div style="flex:1;display:flex;align-items:center;padding-bottom:70px"><div style="display:flex;gap:44px;align-items:flex-start">{cells}</div></div>'
        f'{swm_over(230)}<div class="band">{band}</div></div>')


def preview_square_1(img):
    caps = [(PAGE_NAMES[P_W1], "Quarter notes and paired eighths, with winter words"), (PAGE_NAMES[P_W2], "A silent beat: say shh"),
            (PAGE_NAMES[P_W3], "Hold the sound for 2 and 4 beats")]
    return trio(img, caps, "What is inside", "Four warm-ups for grades 2–5", ["Clap", "Say", "Hold"], "Free <em>·</em> Teacher led <em>·</em> 4/4 rhythms")


def preview_square_2(a, b):
    return pair((a, PAGE_NAMES[P_W4], "Clap a bar, the class echoes it"), (b, PAGE_NAMES[P_KEY], "Every line, in words"),
                "Echo chain and key", "Mix every rhythm, then check it", "Echo chain <em>·</em> Teacher key <em>·</em> My turn lines")


def preview_square_3(a, b):
    return pair((a, PAGE_NAMES[P_FULL], "More from the store"), (b, PAGE_NAMES[P_TERMS], "Printing, sharing and credits"),
                "See the full sets", "Follow the store for new sets", "Free download <em>·</em> {0} pages".format(TOTAL_PAGES))


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


PAGE_LIST = [("Cover", 1), ("Warm-up pages: ta and ti-ti, quarter rests, half and whole notes, and a rhythm echo chain", 4),
             ("Teacher answer key (every line in words)", 1), ("See the full sets", 1), ("Terms of use and credits", 1)]
assert sum(c for _, c in PAGE_LIST) == TOTAL_PAGES


def upload_md():
    lst = "\n".join(f"- {n}: {c}" for n, c in PAGE_LIST)
    prod = "\n".join(f"- {t} ({m})" for t, m, _ in PRODUCTS)
    return f"""# UPLOAD: {LISTING_TITLE} (TpT 072)

Free follower magnet (queue, December). These fields follow the order of TpT's "Add a resource" form. Winter-themed content, non-religious; the title leaves out seasonal words.

**Files to attach**
- Resource (digital download): `{SLUG}.pdf`, {TOTAL_PAGES} pages, US Letter (4 warm-up pages, 1 "see the full sets" page, plus cover, teacher answer key and terms).
- Thumbnails, in this order: `cover.png`, `preview-1.png`, `preview-2.png`, `preview-3.png` (all 2000 × 2000).
- Preview file: `{SLUG}-PREVIEW.pdf`, 4 watermarked pages.

## 1. Title

```
{LISTING_TITLE}
```
({len(LISTING_TITLE)} characters; the limit is 80.) Plain search words first, no seasonal words in the title.

## 2. Description

```
A FREE set of four teacher-led rhythm warm-ups for grades 2-5. Students clap and say rhythms in 4/4 while they read real notation: ta and ti-ti, quarter rests, half and whole notes, and a rhythm echo chain that mixes them all. Winter cue words (snow, sled, cocoa, mittens, penguin) match the notes syllable for syllable, so children can say the words first and then switch to ta and ti-ti. Everything is non-religious and winter themed, so it fits any school calendar.

HOW IT WORKS
Every warm-up page has a one-line teaching direction, three rhythm lines to clap and say (the echo chain page has four) and a "My turn" staff under each line where students write their own bars and clap them for a partner. Every bar adds up to four beats, and the teacher key gives each line in words.

WHAT'S INCLUDED ({TOTAL_PAGES} pages, PDF, US Letter)
• Cover (1 page)
• 4 warm-up pages: ta and ti-ti, quarter rests, half and whole notes, and a rhythm echo chain (4 pages)
• Teacher answer key: every line in words and syllables (1 page)
• A "See the full sets" page about more {BRAND} winter resources (1 page)
• Terms of use and credits (1 page)
Total: {TOTAL_PAGES} pages. That is 5 pages for students (the 4 warm-ups and the "see the full sets" page) plus the cover, the teacher key and the terms.

PERFECT FOR
Bell ringers, music centers, sub plans and a quick rhythm reading check. Find the {BRAND} store on Teachers Pay Teachers for the full winter sets.

• Grades 2-5
• Prints well in black and white
• No songs, lyrics or copyrighted characters
• No standards cited: match the activities to your own music goals

{DISCLOSURE}
```

## 3. Grades

2nd, 3rd, 4th and 5th (TpT allows four; the description says grades 2-5).

## 4. Subjects and tags

- Subjects: {", ".join(SUBJECTS)}
- Tags: {", ".join(TAGS)} (all are exact, pickable entries in tpt/TAG-OPTIONS.json; there is no "Freebies" tag in that list, so none is used)

## 5. Page count by section (totals {TOTAL_PAGES})

{lst}
- Total: {TOTAL_PAGES}

## 6. Standards

None cited. The key page says so and asks teachers to match the activities to their own music goals.

## 7. Price

**$0 (Free Resource).** Tick the "Free Resource" checkbox (`#item-free`) as for 028. `tpt.json` has `price`/`license_price` "0.00" and `"free": true`. Note: tools/tpt.js only fills the price boxes and does not know the Free checkbox (see the 028 notes); I did not touch it.

## 8. Preview

Free. Preview PDF: warm-up 1 (page {P_W1}), warm-up 3 (page {P_W3}), the echo chain (page {P_W4}) and the teacher answer key (page {P_KEY}), all watermarked.

## 9. The "see the full sets" page

It names these released {BRAND} products by their exact titles, with grades and page counts as in their UPLOAD.md files, and no web addresses:
{prod}
Buyers are told to search the title on Teachers Pay Teachers or follow the store.

## 10. Before you click publish

- Season: winter, non-religious. Build window: December.
- Art: the cover illustration (cards fanned behind crossed drumsticks and a snowflake) is made with AI tools (the disclosure line covers it); notation, key and pages are drawn in code.
- Open owner questions: (1) Free checkbox in tools/tpt.js (above). (2) Logo beside HUDSON BEAT (see tpt/STYLE.md).
"""


def tpt_json():
    return {"price": PRICE, "license_price": PRICE, "free": True, "tax_code": "Other Digital Goods - No Physical Media", "grades": GRADES, "subjects": SUBJECTS,
            "tags": TAGS, "formats": ["PDF"], "pages": TOTAL_PAGES, "answer_key": "Included",
            "files": {"product": f"{SLUG}.pdf", "preview": f"{SLUG}-PREVIEW.pdf", "thumb1": "cover.png", "thumb2": "preview-1.png", "thumb3": "preview-2.png", "thumb4": "preview-3.png"}}


SHOT_PAGES = [P_W1, P_W2, P_W3, P_W4, P_KEY, P_FULL, P_TERMS]


def build():
    os.makedirs(BUILD, exist_ok=True)
    full = write("resource.html", html_doc(full_pages(), TITLE))
    prev = write("preview.html", html_doc(preview_pages(), "Preview"))
    render([{"html": full, "pdf": PDF}, {"html": prev, "pdf": PREVIEW_PDF}])
    for i in SHOT_PAGES:
        subprocess.run(["pdftoppm", "-png", "-r", "150", "-f", str(i), "-l", str(i), "-singlefile", PDF, os.path.join(BUILD, f"pg{i}")], check=True)
    sq = [write("cover.html", cover_square()),
          write("p1.html", preview_square_1([f"pg{P_W1}.png", f"pg{P_W2}.png", f"pg{P_W3}.png"])),
          write("p2.html", preview_square_2(f"pg{P_W4}.png", f"pg{P_KEY}.png")),
          write("p3.html", preview_square_3(f"pg{P_FULL}.png", f"pg{P_TERMS}.png"))]
    render([{"html": h, "png": o, "width": 1000, "height": 1000, "scale": 2} for h, o in zip(sq, [COVER_PNG] + PREVIEW_PNGS)])
    with open(UPLOAD, "w") as fh:
        fh.write(upload_md())
    with open(TPT_JSON, "w") as fh:
        json.dump(tpt_json(), fh, indent=2)
        fh.write("\n")
    print(f"built {PDF}, {PREVIEW_PDF}, cover + 3 previews, UPLOAD.md, tpt.json")


if __name__ == "__main__" and "--check" not in sys.argv:
    build()


# ------------------------------------------------------------------ checks
# Everything below re-reads the rendered HTML/SVG/PDF. It does not trust the pattern data except to compare against it.
SVG_RE = re.compile(r'<svg class="rh".*?</svg>', re.S)


def local(tag):
    return tag.split("}")[-1]


def num(v):
    return float(v)


def collapse(s):
    return re.sub(r"(.)\1+", r"\1", s.replace("-", ""))


def parse_rh(svg):
    """Return (list of bars, list of errors) from the geometry of one rendered rhythm SVG. Each bar is a list of (kind, word, syl)."""
    errs = []
    root = ET.fromstring(svg)
    sp, bw, pad = num(root.get("data-sp")), num(root.get("data-bw")), num(root.get("data-pad"))
    label = root.get("data-label") or "?"
    lines = sorted(num(e.get("y1")) for e in root.iter() if local(e.tag) == "line" and e.get("class") == "sl")
    if len(lines) != 5 or any(abs((lines[i + 1] - lines[i]) - sp) > 0.05 for i in range(4)):
        return [], [f"{label}: staff is not five lines one space apart"]
    top, mid = lines[0], lines[2]
    heads, stems, beams, rests, txt, ts, clef, bars = [], [], [], [], {"syl": [], "word": [], "num": []}, [], [], []
    for e in root.iter():
        t, c = local(e.tag), e.get("class")
        if t == "text":
            d = {"x": num(e.get("x")), "y": num(e.get("y")), "t": (e.text or "").strip()}
            if c == "nh":
                heads.append(d)
            elif c == "rest":
                rests.append(d)
            elif c in txt:
                txt[c].append(d)
            elif c == "ts":
                ts.append(d)
            elif c == "clef":
                clef.append(d)
        elif t == "rect":
            d = {"x": num(e.get("x")), "y": num(e.get("y")), "w": num(e.get("width")), "h": num(e.get("height"))}
            (stems if c == "stem" else beams if c == "beam" else bars if c == "bar" else []).append(d)
    if len(clef) != 1 or clef[0]["t"] != chr(0xE069) or abs(clef[0]["y"] - mid) > 0.05 * sp:
        errs.append(f"{label}: unpitched percussion clef missing or misplaced")
    if len(ts) != 2 or any(d["t"] != chr(0xE084) for d in ts) or sorted(round(d["y"] - mid, 2) for d in ts) != [round(-sp, 2), round(sp, 2)]:
        errs.append(f"{label}: time signature is not 4 over 4")
    thin = sorted([b for b in bars if abs(b["w"] - 0.16 * sp) < 0.02 * sp], key=lambda b: b["x"])
    thick = [b for b in bars if abs(b["w"] - 0.5 * sp) < 0.02 * sp]
    if len(thick) != 1 or len(thin) < 2 or any(abs(b["h"] - 4 * sp) > 0.05 or abs(b["y"] - top) > 0.05 for b in bars):
        return [], errs + [f"{label}: barlines are wrong (need a start line, a final thin and thick line, and a line between bars)"]
    nb = len(thin) - 1
    x_end = thin[-1]["x"]
    if abs(thick[0]["x"] - (x_end + 0.4 * sp)) > 0.05:
        errs.append(f"{label}: final barline is not thin + thick")
    left = [x_end - (nb - k) * 4 * bw for k in range(nb + 1)]   # bar k's left edge (bar line centre)
    for k in range(1, nb):
        if abs(thin[k]["x"] + 0.08 * sp - left[k]) > 0.1:
            errs.append(f"{label}: barline {k} is not one bar width from the next")
    items = []   # (bar, start beat, kind, cx, value)
    beamed = {}
    for bm in beams:
        under = [h for h in heads if bm["x"] - 0.01 <= h["x"] <= bm["x"] + bm["w"]]
        if len(under) != 2:
            errs.append(f"{label}: a beam does not join exactly two noteheads")
            continue
        under.sort(key=lambda h: h["x"])
        sx = [s for s in stems if abs(s["x"] - under[0]["x"]) < 0.02 or abs(s["x"] - under[1]["x"]) < 0.02]
        if abs(bm["x"] - under[0]["x"]) > 0.02 or abs(bm["x"] + bm["w"] - (under[1]["x"] + RH.STEM_W * sp)) > 0.02:
            errs.append(f"{label}: a beam does not run from the first stem to the end of the second")
        if len(sx) != 2 or any(abs(s["y"] + s["h"] - (bm["y"] + bm["h"])) > 0.02 for s in sx):
            errs.append(f"{label}: a beam is not flush with the stem ends")
        if abs((under[1]["x"] - under[0]["x"]) - bw / 2) > 0.05:
            errs.append(f"{label}: beamed eighths are not half a beat apart")
        for h in under:
            beamed[id(h)] = under
    used_stems = 0
    seen = set()
    for h in heads:
        if abs(h["y"] - mid) > 0.05 * sp:
            errs.append(f"{label}: a notehead is not on the middle line")
        code = ord(h["t"]) if h["t"] else 0
        bar = max(k for k in range(nb) if h["x"] >= left[k] - 0.1)
        beat = (h["x"] - left[bar] - RH.LEAD * sp) / bw
        if code == RH.CP_WHOLE:
            if any(abs(s["x"] - h["x"]) < 0.5 * sp for s in stems):
                errs.append(f"{label}: a whole note has a stem")
            items.append((bar, beat, "W", h["x"] + RH.HEAD_W["W"] * sp / 2, 4.0))
            continue
        if code not in (RH.CP_HEAD, RH.CP_HALF):
            errs.append(f"{label}: unknown notehead glyph")
            continue
        mine = [s for s in stems if abs(s["x"] - h["x"]) < 0.02]
        if len(mine) != 1:
            errs.append(f"{label}: notehead at x={h['x']:.1f} has {len(mine)} stems on its left edge")
            continue
        used_stems += 1
        s = mine[0]
        step = round((lines[4] - h["y"]) / (sp / 2))
        if step < 4:
            errs.append(f"{label}: a notehead below the middle line would need an up stem")
        if not (abs(s["w"] - RH.STEM_W * sp) < 0.02 and abs(s["y"] - (h["y"] + RH.STEM_DOWN_NW_Y * sp)) < 0.02 and s["h"] > 3 * sp):
            errs.append(f"{label}: a down stem must start at the notehead's left edge and go down at least 3 spaces")
        if code == RH.CP_HALF:
            items.append((bar, beat, "H", h["x"] + RH.HEAD_W["H"] * sp / 2, 2.0))
        elif id(h) in beamed:
            pair = beamed[id(h)]
            if h is pair[0] and id(pair[0]) not in seen:
                seen.add(id(pair[0]))
                items.append((bar, beat, "E", (pair[0]["x"] + pair[1]["x"] + RH.HEAD_W["E"] * sp) / 2, 1.0))
        else:
            items.append((bar, beat, "Q", h["x"] + RH.HEAD_W["Q"] * sp / 2, 1.0))
    if used_stems != len(stems):
        errs.append(f"{label}: {len(stems)} stems but {used_stems} belong to a notehead")
    for r in rests:
        if r["t"] != chr(RH.CP_QREST) or abs(r["y"] - mid) > 0.05 * sp:
            errs.append(f"{label}: a quarter rest is not the quarter rest glyph on the middle line")
        bar = max(k for k in range(nb) if r["x"] >= left[k] - 0.1)
        items.append((bar, (r["x"] - left[bar] - RH.LEAD * sp) / bw, "R", r["x"] + 0.54 * sp, 1.0))
    out = []
    for k in range(nb):
        run = 0.0
        row = []
        for _, beat, kind, cx, val in sorted(i for i in items if i[0] == k):
            if abs(beat - run) > 0.02:
                errs.append(f"{label}: bar {k + 1} has a symbol at beat {beat + 1:.2f} but the beats so far end at {run + 1:.2f}")
            run += val
            row.append((kind, cx))
        if items and abs(run - 4.0) > 1e-6:
            errs.append(f"{label}: bar {k + 1} adds up to {run} beats, not 4")
        out.append(row)
    if not items:   # a blank staff carries no notes, rests or text rows
        if heads or rests or stems or beams or any(txt.values()):
            errs.append(f"{label}: blank staff is not empty")
        return [[] for _ in range(nb)], errs
    # text rows: every symbol has its syllable (and winter word when a word row is present); numbers 1-4 once per bar
    res = []
    has_word = bool(txt["word"])
    for k, row in enumerate(out):
        bar = []
        for kind, cx in row:
            sy = [d["t"] for d in txt["syl"] if abs(d["x"] - cx) < 1.0]
            wd = [d["t"] for d in txt["word"] if abs(d["x"] - cx) < 1.0]
            if len(sy) != 1 or sy[0] != RH.SYL[kind]:
                errs.append(f"{label}: bar {k + 1} {kind}: syllable text {sy} should be {RH.SYL[kind]}")
            if has_word:
                if len(wd) != 1:
                    errs.append(f"{label}: bar {k + 1} {kind}: needs exactly one cue word")
                else:
                    w = wd[0]
                    base = HELD.get(w, w)
                    if kind == "R":
                        if w != REST_WORD:
                            errs.append(f"{label}: a rest's word row should read {REST_WORD}")
                    elif kind in "QE":
                        if SYLLABLES.get(w) != RH.PARTS[kind]:
                            errs.append(f"{label}: word '{w}' has {SYLLABLES.get(w)} syllables but sits under a {kind} ({RH.PARTS[kind]})")
                    else:
                        if w not in HELD or len(w.split("-")) != RH.PARTS[kind] or SYLLABLES.get(base) != 1 or collapse(w) != collapse(base):
                            errs.append(f"{label}: held word '{w}' does not stretch a one-syllable word over {RH.PARTS[kind]} parts")
            bar.append((kind, wd[0] if wd else "", sy[0] if sy else ""))
        res.append(bar)
    if len(txt["syl"]) != sum(len(b) for b in res) or (has_word and len(txt["word"]) != sum(len(b) for b in res)):
        errs.append(f"{label}: extra or missing text under the notes")
    if txt["num"]:
        for k in range(nb):
            got = sorted(d["t"] for d in txt["num"] if left[k] <= d["x"] < left[k] + 4 * bw)
            if got != ["1", "2", "3", "4"]:
                errs.append(f"{label}: bar {k + 1} counting numbers are {got}")
    return res, errs


def key_from_parsed(bars, has_word):
    words = " | ".join(" ".join(w for _, w, _ in b) for b in bars) if has_word else NOWORDS
    syl = " | ".join(" ".join(s for _, _, s in b) for b in bars)
    return words, syl


def verify_html():
    errs = []
    html = open(os.path.join(BUILD, "resource.html")).read()
    secs = re.split(r'<section class="page', html)[1:]
    if len(secs) != TOTAL_PAGES:
        errs.append(f"resource.html has {len(secs)} pages, expected {TOTAL_PAGES}")
        return errs
    parsed = {}
    for w in WARMUPS:
        page = P_W1 + w["n"] - 1
        sec = secs[page - 1]
        svgs = SVG_RE.findall(sec)
        want = len(w["lines"]) * 2
        if len(svgs) != want:
            errs.append(f"warm-up {w['n']}: {len(svgs)} drawings, expected {want}")
            continue
        parsed[w["n"]] = []
        kinds_seen = set()
        for li, line in enumerate(w["lines"]):
            bars, e = parse_rh(svgs[2 * li])
            errs += e
            blank, e2 = parse_rh(svgs[2 * li + 1])
            errs += e2
            if len(bars) != len(line) or len(blank) != len(line) or any(blank):
                errs.append(f"warm-up {w['n']} line {li + 1}: rhythm has {len(bars)} bars and the My turn staff {len(blank)}; both should have {len(line)} and the staff must be empty")
            if len(bars) > 4:
                errs.append(f"warm-up {w['n']} line {li + 1}: more than 4 bars")
            for b in bars:
                kinds_seen |= {k for k, _, _ in b}
            # compare with the data: symbols and words
            exp = [[(s, wd or "") for s, wd in (tok.partition(":")[0:3:2] for tok in b.split())] for b in line]
            got = [[(k, wd) for k, wd, _ in b] for b in bars]
            if has_words(w):
                if exp != got:
                    errs.append(f"warm-up {w['n']} line {li + 1}: rendered notation differs from the data")
            elif [[k for k, _ in b] for b in exp] != [[k for k, _ in b] for b in got]:
                errs.append(f"warm-up {w['n']} line {li + 1}: rendered notation differs from the data")
            parsed[w["n"]].append(bars)
        need = {1: {"Q", "E"}, 2: {"Q", "E", "R"}, 3: {"Q", "E", "H", "W"}, 4: {"Q", "E", "R", "H", "W"}}[w["n"]]
        if not need <= kinds_seen:
            errs.append(f"warm-up {w['n']}: missing symbol kinds {sorted(need - kinds_seen)}")
        extra = {1: {"R", "H", "W"}, 2: {"H", "W"}}.get(w["n"], set())
        if extra & kinds_seen:
            errs.append(f"warm-up {w['n']}: uses symbols not taught yet {sorted(extra & kinds_seen)}")
        if f"Teacher key on page {P_KEY}" not in sec:
            errs.append(f"warm-up {w['n']}: key cross-reference missing")
    # the key page: recompute every row from the parsed (rendered) notation and find it in the key page text
    key_sec = re.sub(r"\s+", "", re.sub(r"<[^>]+>", " ", secs[P_KEY - 1])).replace("&amp;", "&")
    n_rows = 0
    for w in WARMUPS:
        for li, bars in enumerate(parsed.get(w["n"], [])):
            words, syl = key_from_parsed(bars, has_words(w))
            lab = f"Page{P_W1 + w['n'] - 1},line{li + 1}"
            row = re.sub(r"\s+", "", lab + words + syl)
            if row not in key_sec:
                errs.append(f"key row for warm-up {w['n']} line {li + 1} does not match the notation: {words} / {syl}")
            n_rows += 1
    if n_rows != sum(len(w["lines"]) for w in WARMUPS):
        errs.append("key does not cover every line")
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
      const BOX = '.part, .prod, .top, .nd, .doc table, .doc p, .doc ul, .box, .inst';
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
        pg.querySelectorAll('.part, .prod').forEach(bx => {
          if (bx.scrollWidth > bx.clientWidth + 1 || bx.scrollHeight > bx.clientHeight + 1) res.push(`page ${i + 1}: content overflows a ${bx.className} box`);
          const br = bx.getBoundingClientRect();
          bx.querySelectorAll('svg').forEach(sv => {
            const s = sv.getBoundingClientRect();
            if (s.left < br.left + 3 || s.right > br.right - 3 || s.top < br.top + 3 || s.bottom > br.bottom - 3) res.push(`page ${i + 1}: a drawing is too close to its ${bx.className} box edge`);
          });
        });
        pg.querySelectorAll('.top .t').forEach(t => { if (t.getBoundingClientRect().right > pg.querySelector('.top .tag').getBoundingClientRect().left - 8) res.push(`page ${i + 1}: title crowds the tag`); });
        pg.querySelectorAll('.inst').forEach(t => { const lh = parseFloat(getComputedStyle(t).lineHeight); if (t.getBoundingClientRect().height > lh * 1.5 && pg.querySelector('.stack')) res.push(`page ${i + 1}: the one-line teaching direction wraps`); });
        let maxb = 0;
        pg.querySelectorAll('*').forEach(el => { if (skip(el)) return; const r = el.getBoundingClientRect(); if (r.height > 0 && r.width > 0 && ((el.children.length === 0 && ((el.textContent || '').trim() || el.matches('svg, img'))) || el.matches('.part, .box, table, .prod'))) maxb = Math.max(maxb, r.bottom); });
        if (i > 0 && ftop - maxb > 105) res.push(`page ${i + 1}: blank band of ${(ftop - maxb).toFixed(0)}px above the footer (over 10% of the page)`);
        const kids = [...pg.querySelectorAll(':scope > *, :scope > .stack > *')].filter(e => !skip(e) && e.getBoundingClientRect().height > 0 && !e.classList.contains('stack')).map(e => e.getBoundingClientRect()).sort((a, b) => a.top - b.top);
        for (let k = 0; k < kids.length - 1; k++) if (kids[k + 1].top - kids[k].bottom > 105) res.push(`page ${i + 1}: blank band of ${(kids[k + 1].top - kids[k].bottom).toFixed(0)}px between blocks`);
        pg.querySelectorAll('.stack').forEach(st => {
          const k2 = [...st.children].filter(e => e.getBoundingClientRect().height > 0).map(e => e.getBoundingClientRect());
          for (let k = 0; k < k2.length - 1; k++) if (k2[k + 1].top - k2[k].bottom > 105) res.push(`page ${i + 1}: blank band of ${(k2[k + 1].top - k2[k].bottom).toFixed(0)}px inside the page body`);
        });
      });
      document.querySelectorAll('.sq').forEach((sq, i) => {
        const sr = sq.getBoundingClientRect();
        const bandEl = sq.querySelector('.band');
        const btop = bandEl.getBoundingClientRect().top;
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
        sq.querySelectorAll('img').forEach(im => {
          if (!im.complete || im.naturalWidth === 0) res.push(`square ${i + 1}: an image did not load`);
          const r = im.getBoundingClientRect();
          if (!im.closest('.shot') && (r.bottom + 8 > btop || r.left < sr.left + 40 || r.right > sr.right - 40)) res.push(`square ${i + 1}: hero art too close to the band or the edge`);
        });
        const kids = [...sq.children].filter(c => !c.classList.contains('band') && !c.classList.contains('swm'));
        const hs = [...sq.querySelectorAll('.store, .hd, .sub')].map(e => e.getBoundingClientRect()).sort((a, b) => a.top - b.top);
        for (let k = 0; k < hs.length - 1; k++) if (hs[k].bottom > hs[k + 1].top + 1 && hs[k].top < hs[k + 1].top && hs[k].left < hs[k + 1].right && hs[k + 1].left < hs[k].right) res.push(`square ${i + 1}: overlapping blocks`);
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
  // every notation drawing alone on a transparent ground at 4x
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 700, height: 500 }, deviceScaleFactor: 4 });
  await p.goto(url.pathToFileURL(process.argv[2]).href, { waitUntil: 'load' });
  await p.evaluate(() => document.fonts.ready);
  const hs = await p.$$('svg');
  let n = 0;
  for (const h of hs) await h.screenshot({ path: process.argv[3] + '/s' + String(n++).padStart(3, '0') + '.png', omitBackground: true });
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
    from PIL import Image
    html = open(os.path.join(BUILD, "resource.html")).read()
    seen, items = set(), []
    for m in SVG_RE.finditer(html):
        s = m.group(0)
        key = re.sub(r'data-label="[^"]*"', "", s)
        if key in seen:
            continue
        seen.add(key)
        items.append(s)
    page = (f'<!doctype html><html><head><meta charset="utf-8"><style>{font_css()}html,body{{margin:0;background:transparent}}svg{{display:block;margin:20px}}</style></head>'
            f'<body>{"".join(items)}</body></html>')
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
    if len(names) != len(items):
        errs.append(f"pixel check rendered {len(names)} drawings, expected {len(items)}")
    for nm, s in zip(names, items):
        im = Image.open(os.path.join(shots, nm)).convert("RGBA")
        bb = im.getchannel("A").point(lambda v: 255 if v > 8 else 0).getbbox()
        w, h = im.size
        lab = re.search(r'data-label="([^"]*)"', s).group(1)
        if bb is None:
            errs.append(f"rendered pixels: {lab} is blank")
            continue
        edge = min(bb[0], bb[1], w - bb[2], h - bb[3])
        need = 4 * 2          # stroke is about 1 CSS px at this size: padding of 2 CSS px (8 px at 4x) is more than the stroke width
        if edge < need:
            errs.append(f"rendered pixels: {lab} ink comes within {edge}px of its box edge (needs {need}px)")
    return errs


def verify_images():
    errs = []
    from PIL import Image
    h = Image.open(HERO)
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
    if 'class="swm"' in open(os.path.join(BUILD, "cover.html")).read():
        errs.append("cover.png carries a watermark")
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
    for i, t in enumerate(texts):
        for m in re.finditer(r"(?i)\bpages? (\d+)(?:–(\d+))?", t):
            a, b = int(m.group(1)), int(m.group(2) or m.group(1))
            if a < 1 or b > TOTAL_PAGES or b < a:
                errs.append(f"page {i + 1}: reference '{m.group(0)}' is outside the {TOTAL_PAGES}-page file")
    for w in WARMUPS:
        t = texts[P_W1 + w["n"] - 2]
        if re.sub(r"<[^>]+>", "", w["direction"]) not in t:
            errs.append(f"warm-up {w['n']}: teaching direction missing")
        if t.lower().count("my turn") != len(w["lines"]):
            errs.append(f"warm-up {w['n']}: expected {len(w['lines'])} My turn lines")
    terms = texts[P_TERMS - 1]
    for need in (f"Page 1 cover, pages {P_W1}–{P_W4} the four warm-ups", f"page {P_KEY} teacher answer key", f"page {P_FULL} see the full sets", f"({TOTAL_PAGES} pages)"):
        if need.lower() not in terms.lower():
            errs.append(f"terms page 'what is in this file' lacks '{need}'")
    if DISCLOSURE not in terms:
        errs.append("terms page lacks the disclosure line")
    full = texts[P_FULL - 1]
    for t, m, _ in PRODUCTS:
        if t not in full or m.lower() not in full.lower():
            errs.append(f"see-the-full-sets page lacks '{t[:40]}' with '{m}'")
    if re.search(r"https?://|www\.|\.com", " ".join(texts)):
        errs.append("a web address appears in the PDF")
    if "Teachers Pay Teachers" not in full or BRAND not in full:
        errs.append("see-the-full-sets page should name the store and Teachers Pay Teachers")
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
    for need in (DISCLOSURE, "$0", f"{TOTAL_PAGES} pages", "Grades 2-5", "2nd, 3rd, 4th and 5th", "Free Resource"):
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
    if "5 pages for students" not in desc:
        errs.append("UPLOAD.md should say honestly what the 5 pages are")
    if re.search(r"https?://|www\.", up):
        errs.append("UPLOAD.md carries a web address")
    for pt, pm, _ in PRODUCTS:
        if pt not in up:
            errs.append(f"UPLOAD.md lacks product '{pt[:40]}'")
        # the title, grades and page count must match the product's own UPLOAD.md
        found = None
        for d in sorted(os.listdir(TPT)):
            u = os.path.join(TPT, d, "UPLOAD.md")
            if os.path.exists(u) and f"```\n{pt}\n```" in open(u).read():
                found = u
        if not found:
            errs.append(f"no released product has the exact title '{pt[:40]}'")
            continue
        body = open(found).read()
        pages = re.search(r"(\d+) pages", pm).group(1)
        if f"{pages} pages" not in body:
            errs.append(f"'{pt[:30]}': page count {pages} not found in its UPLOAD.md")
        g = re.search(r"Grades? ([\dK]+-\d)", pm).group(1)
        if g.replace("-", "–") not in body and g not in body:
            errs.append(f"'{pt[:30]}': grades {g} not found in its UPLOAD.md")
    low = up.lower()
    for bad in ("checked by hand", "handmade", "recomputed", "classroom-tested", "classroom tested", "hand-checked"):
        if bad in low:
            errs.append(f"UPLOAD.md says '{bad}'")
    tj = json.load(open(TPT_JSON))
    topts = json.load(open(os.path.join(TPT, "TAG-OPTIONS.json")))["options"]
    headings = {"Audience", "Language", "Programs & Methods", "Resource Type", "Instruction", "Student Assessment", "Student Practice", "Teacher Tools", "Supports", "Specialty", "Speech Therapy",
                "Theme", "Holiday", "Seasonal", "Hands-on Activities", "Forms", "Classroom Decor", "Special Education"}
    subs = json.load(open(os.path.join(TPT, "SUBJECT-OPTIONS.json")))
    sub_headings = {"Arts", "Art", "English Language Arts", "Math", "Performing Arts", "Science", "Social Studies", "World Languages", "Social Emotional", "For All Subjects"}
    if any(t not in topts or t in headings for t in tj["tags"]) or any(s not in subs or s in sub_headings for s in tj["subjects"]):
        errs.append("tpt.json tags or subjects invalid, or a heading")
    if not 1 <= len(tj["tags"]) <= 6 or not 1 <= len(tj["subjects"]) <= 3:
        errs.append("tpt.json tag or subject count out of range")
    if tj.get("pages") != TOTAL_PAGES or tj["price"] != "0.00" or tj["license_price"] != "0.00" or tj.get("free") is not True or not 1 <= len(tj["grades"]) <= 4:
        errs.append("tpt.json pages, price, free flag or grades mismatch")
    first = texts[0].lower()
    if f"{TOTAL_PAGES} pages" not in first or "4 warm-ups" not in first or "grades 2–5" not in first or "free" not in first:
        errs.append("cover text does not state free, the page count, warm-ups and grades")
    pt_all = " ".join(texts).lower()
    for bad in ("colour", "favourite", "metre", "crotchet", "quaver", "minim", "semibreve", "analyse", "recomputed", "checker", "grey"):
        if bad in pt_all:
            errs.append(f"unwanted wording '{bad}'")
    for bad in ("christmas", "santa", "hanukkah", "kwanzaa", "easter", "church", "pray", "nativity"):
        if bad in pt_all:
            errs.append(f"religious word '{bad}' in the product")
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
    n_lines = sum(len(w["lines"]) for w in WARMUPS)
    n_bars = sum(len(l) for w in WARMUPS for l in w["lines"])
    print(f"CHECK OK: {n_lines} rhythm lines ({n_bars} bars) and {n_lines} My turn staves re-read from the rendered SVG; every bar adds up to 4 beats; stems on the left edge going down from noteheads on the middle line; "
          f"beams join exactly two eighths flush with the stem ends; half and whole heads open, no stem on whole notes; rests, clef and 4/4 placed correctly; every cue word's syllable count matches its note; "
          f"the teacher key was recomputed from the rendered notation and matches the key page; notation keeps padding on rendered pixels; layout and footer gaps clear; PDF {TOTAL_PAGES} Letter pages, preview 4 "
          f"(one watermark each); images 2000x2000 with clean edges; full-sets titles, grades and page counts agree with their UPLOAD.md files; UPLOAD.md and tpt.json agree.")


if __name__ == "__main__" and "--check" in sys.argv:
    check()
