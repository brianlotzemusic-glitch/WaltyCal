#!/usr/bin/env python3
"""Winter Music Mega Bundle (TpT 074): ZIP bundle of 23 released elementary winter/holiday kits, with its own guide, cover, previews and listing files.

    python3 gen.py            build everything into this folder
    python3 gen.py --check    verify ZIP (SHA-256 vs member PDFs), prices/percent/ribbon, page counts, titles, layout, images, tpt.json, UPLOAD.md

Member data (price, pages, title, grades) is READ from each member folder (tpt.json, UPLOAD.md, the PDF itself); nothing is typed from memory except
the short display names and grade ranges, which --check verifies against the members' UPLOAD.md text. Member folders are only read, never written.
"""
import hashlib
import json
import math
import os
import re
import subprocess
import sys
import zipfile
from html import escape

HERE = os.path.dirname(os.path.abspath(__file__))
TPT = os.path.dirname(HERE)
ROOT = os.path.dirname(TPT)
FONTS = os.path.join(TPT, "fonts")
BUILD = os.path.join(HERE, "build")
RENDER_JS = os.path.join(TPT, "tools", "render.js")

STORE, BRAND, YEAR = "Brian Lotze", "Hudson Beat", 2026
ACCENT = "#1F6C9C"
ACCENT_LIGHT = "#59A5DB"
TITLE = "Winter Music Mega Bundle"
SLUG = "winter-music-mega-bundle"
FOLDER = "Winter Music Mega Bundle - Hudson Beat"
GUIDE_NAME = "00 START HERE - Bundle Guide.pdf"
ZIP = os.path.join(HERE, f"{SLUG}.zip")
GUIDE = os.path.join(HERE, "bundle-guide.pdf")
PREVIEW_PDF = os.path.join(HERE, f"{SLUG}-PREVIEW.pdf")
COVER_PNG = os.path.join(HERE, "cover.png")
PREVIEW_PNGS = [os.path.join(HERE, f"preview-{i}.png") for i in (1, 2, 3)]
UPLOAD = os.path.join(HERE, "UPLOAD.md")
TPT_JSON = os.path.join(HERE, "tpt.json")
DISCLOSURE = "Created with the help of digital and AI tools. Notation and answer keys are verified before release."
BANNED = ["Blind Brook", "BBHS", "blindbrook", "Google Classroom", "Rudolph", "Frosty"]
GUIDE_PAGES = 4

LISTING_TITLE = "Music Mega Bundle | 23 Resources: Rhythm, Color by Note, Games | Gr K-6"
TAGS = ["Winter", "Christmas-Chanukah-Kwanzaa", "Printables", "Activities", "Worksheets", "Games"]
SUBJECTS = ["Music", "Instrumental Music", "Music Composition"]
GRADES = ["kindergarten", "2nd-grade", "4th-grade", "6th-grade"]

# id, short display name, grade range (as each member's own listing states it)
MEMBERS = [
    ("003", "Winter Rhythm Bingo", "3-6"),
    ("005", "Winter Concert Planner", "K-8"),
    ("006", "Winter Treble Clef Task Cards", "2-5"),
    ("029", "Winter Color by Note", "1-5"),
    ("032", "Christmas Color by Note", "2-6"),
    ("034", "Nutcracker Listening Unit", "2-6"),
    ("035", "Hanukkah Color by Note", "2-6"),
    ("038", "December Music Bell Ringers", "3-6"),
    ("039", "Winter Color by Music Symbol", "2-5"),
    ("042", "Winter Music Escape Room", "3-6"),
    ("044", "Color-Coded Carol Play-Alongs", "1-5"),
    ("046", "Winter Concert Reflection", "4-12"),
    ("047", "Winter Rhythm Math", "2-5"),
    ("050", "Solfege Snowball Melody Cards", "2-4"),
    ("051", "Roll and Compose Winter", "2-5"),
    ("052", "Holiday Music Word Puzzles", "3-6"),
    ("055", "Winter Recorder Songbook (B-A-G)", "3-5"),
    ("056", "Holiday Rhythm I Have Who Has", "2-5"),
    ("059", "Winter Bucket Drumming", "3-8"),
    ("060", "Winter Note Speller", "3-6"),
    ("064", "Winter Holidays Around the World", "3-6"),
    ("066", "Music Symbols Scavenger Hunt", "3-5"),
    ("069", "Beat vs Rhythm Movement Cards", "K-2"),
]
N = len(MEMBERS)
PREVIEW_MEMBER_PAGES = [("003", 1), ("038", 1)]          # (member id, 0-based page of its own watermarked PREVIEW pdf)
SHOTS3 = [("003", 1), ("029", 1), ("038", 1), ("042", 1), ("005", 1), ("064", 1), ("069", 1), ("055", 1)]


def member_dir(mid):
    import glob
    return glob.glob(os.path.join(TPT, f"{mid}-*"))[0]


def load_members():
    out = []
    for i, (mid, short, grades) in enumerate(MEMBERS, 1):
        d = member_dir(mid)
        tj = json.load(open(os.path.join(d, "tpt.json")))
        up = open(os.path.join(d, "UPLOAD.md")).read()
        title = re.search(r"## 1\. Title\s+```\n(.*?)\n```", up, re.S).group(1).strip()
        pdf = os.path.join(d, tj["files"]["product"])
        prev = os.path.join(d, tj["files"]["preview"])
        out.append(dict(i=i, id=mid, short=short, grades=grades, dir=d, tj=tj, up=up, title=title, pdf=pdf, prev=prev,
                        price=float(tj["price"]), pages=int(tj["pages"]),
                        folder=f"{i:02d} {short.replace('&', 'and')}", cover=os.path.join(d, "cover.png"),
                        has_release=os.path.exists(os.path.join(d, "release"))))
    return out


M = load_members()
SUM = round(sum(m["price"] for m in M), 2)
TARGET = SUM * 0.65
PRICE = math.floor(TARGET * 2 + 0.5) / 2.0                 # nearest .00 or .50
SAVE = round(SUM - PRICE, 2)
PCT = 100 * (1 - PRICE / SUM)
RIBBON = int(math.floor(PCT))                              # "SAVE 34%": real saving rounded DOWN
MEMBER_PAGES = sum(m["pages"] for m in M)
TOTAL_PAGES = MEMBER_PAGES + GUIDE_PAGES


def money(x):
    return f"${x:.2f}"


def sources():
    return [(f"{m['folder']}/{os.path.basename(m['pdf'])}", m["pdf"]) for m in M]


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


# ---------------------------------------------------------------- css
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
.top .t { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; letter-spacing: .01em; line-height: 1; font-size: 25pt; }
.top .t small { display: block; font-family: 'Oswald'; font-weight: 300; text-transform: none; font-size: 12pt; letter-spacing: 0; margin-top: 4pt; }
.tag { text-align: right; }
.tag .lv { display: inline-block; background: #000; color: #fff; font-family: 'Oswald'; font-weight: 700; font-size: 15pt; padding: 3pt 9pt 4pt; border-radius: 4pt; letter-spacing: .04em; }
.tag .ln { font-family: 'Oswald'; font-weight: 300; font-size: 11pt; margin-top: 3pt; }
.main { flex: 1; display: flex; flex-direction: column; min-height: 0; padding-bottom: 12px; }
.main > * { flex-shrink: 0; }
.foot { display: flex; justify-content: space-between; font-size: 8.5pt; color: #333; border-top: .8pt solid #000; padding-top: 3pt; }
.wm { position: absolute; left: 50%; top: 50%; transform: translate(-50%, -50%) rotate(-38deg); font-family: 'Oswald'; font-weight: 700;
      font-size: 150pt; color: rgba(0,0,0,.13); letter-spacing: .06em; white-space: nowrap; pointer-events: none; z-index: 9; }
.doc h2 { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 13.5pt; margin: 10pt 0 4pt; letter-spacing: .02em; }
.doc p, .doc li { font-size: 10.6pt; line-height: 1.32; margin: 0 0 4pt; }
.doc ul, .doc ol { margin: 0 0 4pt; padding-left: 15pt; }
table.t { border-collapse: collapse; width: 100%; font-size: 10.6pt; margin: 2pt 0 4pt; }
table.t td, table.t th { border: 1pt solid #000; padding: 9.5pt 6pt; text-align: left; vertical-align: middle; }
table.t th { font-family: 'Oswald'; font-weight: 500; text-transform: uppercase; font-size: 9.5pt; background: #000; color: #fff; letter-spacing: .04em; }
table.t td.n, table.t th.n { text-align: center; }
.small { font-size: 9pt !important; color: #333; }
.box { border: 1.4pt solid #000; border-radius: 8pt; padding: 8pt 12pt; }
.hero3 { display: flex; gap: 12pt; margin: 10pt 0 4pt; }
.hero3 > div { flex: 1; border: 1.8pt solid #000; border-radius: 8pt; text-align: center; padding: 8pt 4pt 9pt; }
.hero3 b { display: block; font-family: 'Oswald'; font-weight: 700; font-size: 38pt; line-height: 1; color: ACCENT; }
.hero3 span { font-family: 'Oswald'; font-weight: 500; font-size: 10pt; letter-spacing: .12em; text-transform: uppercase; }
""".replace("ACCENT", ACCENT)
COPY = f"© {YEAR} {STORE} · {BRAND} · For single-classroom use"


def foot(n):
    return f'<div class="foot"><span>{COPY}</span><span>Page {n}</span></div>'


def page(sub, tag, tagsub, inner, n, watermark=False):
    wm = '<div class="wm">PREVIEW</div>' if watermark else ""
    top = (f'<div class="top"><div class="t">{escape(TITLE)}<small>{sub}</small></div>'
           f'<div class="tag"><div class="lv">{tag}</div><div class="ln">{tagsub}</div></div></div>')
    return f'<section class="page doc">{wm}{top}<div class="main">{inner}</div>{foot(n)}</section>'


def html_doc(pages, title):
    return (f'<!doctype html><html><head><meta charset="utf-8"><title>{escape(title)}</title>'
            f'<style>{font_css()}{CSS}</style></head><body>{"".join(pages)}</body></html>')


def rows_html(ms):
    return "".join(f'<tr><td class="n"><b>{m["i"]}</b></td><td><b>{escape(m["short"])}</b></td><td>{escape(m["folder"])}</td>'
                   f'<td class="n">{m["grades"]}</td><td class="n">{m["pages"]}</td><td class="n">{money(m["price"])}</td></tr>' for m in ms)


HEAD = '<tr><th class="n">#</th><th>Resource</th><th>Folder in the ZIP</th><th class="n">Grades</th><th class="n">Pages</th><th class="n">Price alone</th></tr>'


def start_page(n, watermark=False):
    inner = (f'<p style="margin-top:8pt">Welcome! This ZIP holds <b>{N} winter and holiday music resources</b>, mostly for elementary music: rhythm and note-name practice, '
             f'games, color-by-note pages, listening, recorder and drumming play-alongs, and concert-season helpers. Each resource is a ready-to-print PDF in its own numbered folder.</p>'
             f'<div class="hero3"><div><b>{N}</b><span>Resources</span></div><div><b>{MEMBER_PAGES}</b><span>Pages</span></div>'
             f'<div><b>{RIBBON}%</b><span>Saved</span></div></div>'
             f'<h2>How to use this bundle</h2><ol>'
             f'<li>Unzip the download. Each resource has its own numbered folder (01 to {N:02d}) holding its PDF.</li>'
             f'<li>Open the next page: it lists every resource with its grades and page count, so you can pick what fits your classes.</li>'
             f'<li>Open a PDF and read its teacher page first. Print the student pages you need; answer keys are inside the PDFs that have them.</li>'
             f'<li>Plan your winter weeks: use the concert planner and reflection for concert season, the games and color-by-note pages for Fun Fridays, '
             f'and the listening unit and holidays-around-the-world pages for a holiday lesson.</li></ol>'
             f'<h2>What you saved</h2>'
             f'<div class="box"><p style="margin:0">The {N} resources sold separately add up to <b>{money(SUM)}</b>. The bundle price is <b>{money(PRICE)}</b>: '
             f'you save <b>{money(SAVE)}</b> ({PCT:.1f}%).</p></div>'
             f'<h2>Also sold separately</h2>'
             f'<p>Every resource in this bundle is also sold on its own in the {BRAND} store on Teachers Pay Teachers, and the files are the same. '
             f'If you already own some of them, you have them twice: use the folders you need.</p>'
             f'<h2>Good to know</h2><ul>'
             f'<li>Grade ranges differ by resource: most are for grades 2 to 6, some reach kindergarten or grade 1, and three go beyond elementary: the concert planner (K-8), bucket drumming (3-8) and the concert reflection (4-12, for band, choir and orchestra) (see the table).</li>'
             f'<li>Holiday resources include Christmas, Hanukkah and winter-general options; use the ones that fit your community.</li>'
             f'<li>Every page prints well in black and white unless it says otherwise.</li></ul>')
    return page("Start here", "GUIDE", "Teacher", inner, n, watermark)


def _n(*ids):
    return ", ".join(str(m["i"]) for m in M if m["id"] in ids)


PICKS = ('<div class="box" style="margin-top:12pt"><p style="margin:0 0 3pt"><b>Quick picks</b> (resource numbers)</p>'
         f'<p style="margin:0 0 2pt">Games and Fun Friday: {_n("003", "042", "051", "052", "056")}. Color-by-note pages: {_n("029", "032", "035", "039")}. '
         f'Concert season: {_n("005", "046")}.</p>'
         f'<p style="margin:0">Listening and culture: {_n("034", "064")}. Play-along and recorder: {_n("044", "055", "059")}.</p></div>')


def table_page(n, ms, sub, extra="", watermark=False):
    inner = f'<table class="t" style="margin-top:8pt">{HEAD}{rows_html(ms)}</table>{PICKS}'
    return page(sub, "GUIDE", "Resource list", inner, n, watermark)


def table_page_2(n, watermark=False):
    tot = (f'<tr><td></td><td><b>Total</b></td><td>{N} folders</td><td></td><td class="n"><b>{MEMBER_PAGES}</b></td><td class="n"><b>{money(SUM)}</b></td></tr>')
    inner = (f'<table class="t" style="margin-top:8pt">{HEAD}{rows_html(M[12:])}{tot}</table>'
             f'<div class="box" style="margin-top:12pt"><p style="margin:0"><b>Bundle price {money(PRICE)}</b> instead of {money(SUM)}: you save {money(SAVE)} ({PCT:.1f}%). '
             f'Each resource is also sold separately in the {BRAND} store.</p></div>'
             f'<p class="small" style="margin-top:10pt">Page counts are the pages of each resource&#8217;s PDF. The ZIP also holds this {GUIDE_PAGES}-page guide, '
             f'so the bundle has {TOTAL_PAGES} pages in all.</p>')
    return page(f"Resources {M[12]['i']} to {N}", "GUIDE", "Resource list", inner, n, watermark)


def terms_page(n):
    return (f'<section class="page doc terms"><div class="top"><div class="t">Terms of Use<small>Thank you for your purchase!</small></div></div>'
            f'<div class="main"><p style="margin-top:8pt">© {YEAR} {STORE}. {BRAND} by {STORE}. All rights reserved. This purchase gives <b>one teacher</b> a license to use all {N} resources '
            f'with their own students.</p>'
            f'<h2>You may</h2><ul><li>Print and copy pages for your own classroom and students, year after year.</li>'
            f'<li>Share pages with your own students through a password-protected class site or learning platform.</li>'
            f'<li>Leave the pages for a substitute teacher who teaches your own students.</li></ul>'
            f'<h2>You may not</h2><ul><li>Share, email or copy this resource for other teachers, a whole school or a district. '
            f'Additional licenses are available on Teachers Pay Teachers.</li>'
            f'<li>Post any part of it on a public website, shared drive or social media.</li>'
            f'<li>Sell, give away or claim any part of it as your own, or edit it into a new product.</li></ul>'
            f'<h2>Questions?</h2><p>Please use the Q&amp;A tab on the {BRAND} by {STORE} store on Teachers Pay Teachers.</p>'
            f'<h2>Credits</h2><ul>'
            f'<li>Original work by {STORE}, {BRAND}. Each resource&#8217;s own terms and credits page applies to its PDF.</li>'
            f'<li>Text fonts: Oswald (The Oswald Project Authors) and Source Sans 3 (Adobe), SIL Open Font License 1.1. Music notation font: Bravura (Steinberg Media Technologies GmbH), SIL Open Font License 1.1, where notation appears.</li>'
            f'<li>No songs with copyrighted lyrics, film or pop songs, or copyrighted characters are used.</li></ul>'
            f'<h2>Please rate</h2><p>Please leave a rating: you earn TpT credits for feedback, and it helps other teachers find this bundle. '
            f'Follow the {BRAND} store for new music resources every week.</p>'
            f'<p class="small">{DISCLOSURE}</p><div style="flex:1"></div></div>{foot(n)}</section>')


# ---------------------------------------------------------------- square images
SQ_CSS = """
.sq { width: 1000px; height: 1000px; position: relative; overflow: hidden; background: #fff; }
.sq .store { position: absolute; left: 24px; right: 24px; top: 30px; text-align: center; font-family: 'Oswald'; font-weight: 500; letter-spacing: .32em; text-transform: uppercase; font-size: 22px; }
.sq .hd { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; text-align: center; line-height: .95; position: absolute; left: 24px; right: 24px; }
.sq .sub { font-family: 'Oswald'; font-weight: 300; text-align: center; position: absolute; left: 24px; right: 24px; }
.sq .band { position: absolute; left: 0; right: 0; bottom: 0; background: #000; color: #fff; text-align: center; font-family: 'Oswald';
            font-weight: 500; text-transform: uppercase; letter-spacing: .1em; font-size: 26px; padding: 16px 0 18px; }
.sq .band em { font-style: normal; color: ACCENT_LIGHT; }
.shot { background: #fff; border: 2px solid #000; box-shadow: 8px 8px 0 #000; position: absolute; overflow: hidden; }
.shot img { display: block; width: 100%; }
.lbl { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 20px; text-align: center; position: absolute; }
.tile { position: absolute; border: 2px solid #000; background: #fff; overflow: hidden; }
.tile img { display: block; width: 100%; height: 100%; }
.cnt { position: absolute; border: 3px solid #000; background: ACCENT; color: #fff; text-align: center; font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; }
.row { position: absolute; display: flex; align-items: center; gap: 10px; height: 44px; width: 465px; border-bottom: 2px solid #000; }
.row .n { flex: 0 0 38px; height: 34px; background: ACCENT; color: #fff; font-family: 'Oswald'; font-weight: 700; font-size: 22px; text-align: center; line-height: 34px; border-radius: 4px; }
.row .t { flex: 1; font-family: 'Source Sans 3'; font-weight: 700; font-size: 20px; white-space: nowrap; overflow: hidden; }
.row .g { flex: 0 0 100px; text-align: right; font-family: 'Oswald'; font-weight: 500; font-size: 17px; white-space: nowrap; }
""".replace("ACCENT_LIGHT", ACCENT_LIGHT).replace("ACCENT", ACCENT)
FONT_PRIME = ('<div style="position:absolute;left:-9999px;font-family:\'Source Sans 3\'">'
              '<span style="font-weight:400">a</span><span style="font-weight:600">a</span><i style="font-weight:400">a</i></div>')


def sq_doc(body):
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{font_css()}'
            f'html,body{{margin:0;background:#fff}}{SQ_CSS}</style></head><body>{FONT_PRIME}{body}</body></html>')


def hd(txt, size, top):
    return f'<div class="hd" style="font-size:{size}px;top:{top}px">{txt}</div>'


def sub(txt, size, top):
    return f'<div class="sub" style="font-size:{size}px;top:{top}px">{txt}</div>'


def shot(src, left, top, width, extra=""):
    return f'<div class="shot" style="left:{left}px;top:{top}px;width:{width}px;height:{width * 11 / 8.5:.0f}px{extra}"><img src="{src}"></div>'


COLS, TILE, GAP, X0, Y0 = 6, 144, 12, 38, 66


def cover_square():
    tiles = ""
    for k, m in enumerate(M):
        x, y = X0 + (k % COLS) * (TILE + GAP), Y0 + (k // COLS) * (TILE + GAP)
        tiles += f'<div class="tile" style="left:{x}px;top:{y}px;width:{TILE}px;height:{TILE}px"><img src="{os.path.relpath(m["cover"], BUILD)}"></div>'
    k = N
    x, y = X0 + (k % COLS) * (TILE + GAP), Y0 + (k // COLS) * (TILE + GAP)
    tiles += (f'<div class="cnt" style="left:{x}px;top:{y}px;width:{TILE}px;height:{TILE}px">'
              f'<div style="font-size:88px;line-height:1;margin-top:12px">{N}</div><div style="font-size:23px;letter-spacing:.03em;margin-top:4px">Resources</div>'
              f'<div style="font-size:18px;font-weight:500;letter-spacing:.04em;margin-top:8px">{MEMBER_PAGES} pages</div></div>')
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div>{tiles}'
        f'<div class="cv-block" style="position:absolute;left:0;right:0;top:686px;height:188px;background:{ACCENT};text-align:center;color:#fff">'
        f'<div class="hd" style="position:static;font-size:124px;line-height:1;padding-top:6px;letter-spacing:.01em">Winter Music</div>'
        f'<div class="hd" style="position:static;font-size:54px;margin-top:0;letter-spacing:.02em">Mega Bundle · Grades K–6</div></div>'
        f'<div class="cv-series" style="position:absolute;left:0;right:0;top:874px;height:52px;background:#fff;border-top:3px solid #000;text-align:center;'
        f'font-family:Oswald;font-weight:700;font-size:30px;letter-spacing:.06em;line-height:50px;white-space:nowrap">'
        f'<span style="background:#000;color:#fff;padding:0 14px;border-radius:5px;margin-right:12px;display:inline-block;line-height:38px;vertical-align:middle">SAVE {RIBBON}%</span>'
        f'<span style="color:{ACCENT}">{money(SAVE)} OFF BUYING THEM ALONE</span></div>'
        f'<div class="band">Grades K–6 <em>·</em> {N} resources <em>·</em> {MEMBER_PAGES} pages</div></div>')


def preview_1():
    rows = ""
    for k, m in enumerate(M):
        col, r = (0, k) if k < 12 else (1, k - 12)
        x, y = 30 + col * 475, 212 + r * 54
        rows += (f'<div class="row" style="left:{x}px;top:{y}px"><div class="n">{m["i"]}</div><div class="t">{escape(m["short"])}</div>'
                 f'<div class="g">Gr {m["grades"]} · {m["pages"]} pp</div></div>')
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div>{hd(f"{N} resources, one download", 70, 78)}'
        f'{sub("Every title, grade range and page count", 27, 160)}{rows}'
        f'<div class="band">{MEMBER_PAGES} pages <em>·</em> save {money(SAVE)} <em>·</em> each also sold separately</div></div>')


def preview_2(a, b):
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div>{hd("A guide and 23 folders", 70, 78)}'
        f'{sub("A resource list with grades, pages and folder names", 27, 160)}'
        f'{shot(a, 70, 214, 400)}{shot(b, 530, 214, 400)}'
        f'<div class="lbl" style="left:70px;top:756px;width:400px;font-size:22px">Start here</div>'
        f'<div class="lbl" style="left:530px;top:756px;width:400px;font-size:22px">Resource list</div>'
        f'<div class="band">Numbered folders <em>·</em> {N} PDFs <em>·</em> teacher guide</div></div>')


def preview_3(items):
    cells = ""
    for i, (src, lab) in enumerate(items):
        x = 70 + (i % 4) * 224
        y = 200 + (i // 4) * 352
        cells += shot(src, x, y, 196) + f'<div class="lbl" style="left:{x - 8}px;top:{y + 255 + 14}px;width:212px;font-size:17px;line-height:1.1">{escape(lab)}</div>'
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div>{hd("Real pages from the bundle", 70, 78)}'
        f'{sub("A sample from eight of the 23 resources", 27, 154)}{cells}'
        f'<div class="band">Games <em>·</em> worksheets <em>·</em> listening <em>·</em> concert helpers</div></div>')


# ---------------------------------------------------------------- listing text
def numbered_list():
    return "\n".join(f"{m['i']}. {m['short']} (grades {m['grades']}, {m['pages']} pages)" for m in M)


def description():
    return f"""Looking for winter and holiday music lessons you can print and teach, without building each one yourself? This bundle gives you {N} complete music resources, mostly for elementary grades, for December and the whole winter season: games, rhythm and note-name practice, color-by-note pages, listening, recorder and drumming play-alongs and concert-season planning pages. Each one is a ready-to-print PDF in its own numbered folder.

THE {N} RESOURCES IN THE BUNDLE (grades and page counts)
{numbered_list()}

WHAT'S INCLUDED (one ZIP, {N} folders)
• {N} resource PDFs, {MEMBER_PAGES} pages in all, in numbered folders (01 to {N:02d})
• A {GUIDE_PAGES}-page start-here guide: a resource list with grades, pages and folder names, how to use the bundle, and terms of use
• Total: {TOTAL_PAGES} pages ({MEMBER_PAGES} + {GUIDE_PAGES})

YOUR SAVING
• The {N} resources sold separately add up to {money(SUM)}. The bundle is {money(PRICE)}: you save {money(SAVE)}, which is {PCT:.1f}% off.
• Each resource is also sold separately in the Hudson Beat store. If you already own some, you have them twice: use the folders you need.

GOOD TO KNOW
• Grade ranges differ by resource: most are for grades 2 to 6, some reach kindergarten or grade 1, and three go beyond elementary: the concert planner (grades K-8), bucket drumming (grades 3-8) and the concert reflection (grades 4-12, for band, choir and orchestra students).
• Holiday options include Christmas, Hanukkah and winter-general resources, so you can choose what fits your community.
• Every PDF has its own teacher page and, where it has answers, an answer key. Student pages print well in black and white unless a page says otherwise.
• This is a ZIP of PDFs. Your computer unzips it; nothing else is needed.
• Files are the same as the individual Hudson Beat listings.

Please leave a rating: you earn TpT credits for feedback, and it helps other teachers find this bundle.
Follow the Hudson Beat store for new music resources every week.

{DISCLOSURE}"""


def page_list():
    return ("\n".join(f"- {m['short']}: {m['pages']}" for m in M)
            + f"\n- Start-here guide: {GUIDE_PAGES}\n- Total: {MEMBER_PAGES} + {GUIDE_PAGES} = {TOTAL_PAGES}")


def upload_md():
    return f"""# UPLOAD: {TITLE} (TpT 074)

Fields follow the order of TpT's "Add a resource" form. This is a **ZIP bundle** sold as an ordinary Digital Download (template: tpt/030-dmp1-units-1-6-bundle). The {N} member listings are not touched, re-uploaded or changed. A native TpT Bundle is a later upgrade (TPT-FACTORY.md "Bundles"). **Live by 1 Dec 2026.**

**Files to attach**
- Resource (digital download): `{SLUG}.zip` (__ZIPMB__ MB, {N + 1} files, folder "{FOLDER}"): `{GUIDE_NAME}` ({GUIDE_PAGES} pages, built here) plus one numbered folder per resource (01 to {N:02d}) holding that resource's product PDF, copied unchanged from tpt/{M[0]['id']} ... tpt/{M[-1]['id']} (`gen.py --check` proves each byte-identical by SHA-256). Previews, gen.py, QA.md and work files are not included.
- Thumbnails, in order: `cover.png`, `preview-1.png`, `preview-2.png`, `preview-3.png` (all 2000 x 2000).
- Preview file: `{SLUG}-PREVIEW.pdf`, 4 watermarked pages (guide start page, resource list, two real resource pages).

## 1. Title

```
{LISTING_TITLE}
```
({len(LISTING_TITLE)} characters; the limit is 80.) The title is deliberately not seasonal: TpT's Seasonal Titles notice blocked listing 027, so winter appears only in the tags, the description and the art on the cover (the ZIP and guide carry the Winter Music Mega Bundle name).

## 2. Description

```
{description()}
```

## 3. Grades

Kindergarten, 2nd, 4th, 6th (TpT allows four boxes). Most members cover grades 2-6 and the set spans kindergarten to grade 6; three members reach beyond elementary (005 concert planner K-8, 059 bucket drumming 3-8, 046 concert reflection 4-12), and the description says so.

## 4. Subjects, tags, formats

Subjects: {", ".join(SUBJECTS)}. Tags: {", ".join(TAGS)} (exact entries of tpt/TAG-OPTIONS.json, none a heading). Formats PDF (ZIP).

## 5. Price (arithmetic)

Sum of the {N} member prices: **{money(SUM)}**. 35% under is {money(TARGET)}; rounded to the nearest .00 or .50 the bundle price is **{money(PRICE)}**: saving {money(SAVE)} = {PCT:.1f}% (the cover ribbon says SAVE {RIBBON}%, the real saving rounded down). Multiple-license price {money(PRICE)}.

## 6. Free preview and pages

Paid. Preview PDF 4 pages. "Number of pages or slides": {TOTAL_PAGES}.
Page list (totals the guide PDF exactly; the ZIP holds {N} resource PDFs and the guide):
{page_list()}

## 7. Before you click publish

- [ ] `python3 tools/tpt-validate.py tpt/074-winter-holiday-music-mega-bundle` and `node tools/tpt.js publish tpt/074-winter-holiday-music-mega-bundle --dry-run` on the Mac.
- [ ] The {N} member listings should be live first (the bundle is only useful when buyers can compare); this bundle does not change them.
- [ ] Release: no `release` file was written; the Manager releases after QA.
"""


def tpt_json():
    return {
        "price": f"{PRICE:.2f}", "license_price": f"{PRICE:.2f}", "tax_code": "Other Digital Goods - No Physical Media",
        "grades": GRADES, "subjects": SUBJECTS, "tags": TAGS, "formats": ["PDF"], "pages": TOTAL_PAGES, "answer_key": "Included",
        "zip_contents": [GUIDE_NAME] + [p for p, _ in sources()],
        "files": {"product": os.path.basename(ZIP), "preview": os.path.basename(PREVIEW_PDF), "thumb1": "cover.png",
                  "thumb2": "preview-1.png", "thumb3": "preview-2.png", "thumb4": "preview-3.png"},
    }


# ---------------------------------------------------------------- build
def node_env():
    env = dict(os.environ)
    if not env.get("NODE_PATH"):
        env["NODE_PATH"] = subprocess.run(["npm", "root", "-g"], capture_output=True, text=True).stdout.strip()
    return env


def render(jobs):
    p = os.path.join(BUILD, "jobs.json")
    json.dump(jobs, open(p, "w"))
    subprocess.run(["node", RENDER_JS, p], check=True, env=node_env(), stdout=subprocess.DEVNULL)


def write(name, txt):
    p = os.path.join(BUILD, name)
    open(p, "w").write(txt)
    return p


def pdf_png(src, n, out, res):
    subprocess.run(["pdftoppm", "-png", "-r", str(res), "-f", str(n), "-l", str(n), "-singlefile", src, os.path.join(BUILD, out)], check=True)


def guide_pages(watermark=False):
    return [start_page(1, watermark), table_page(2, M[:12], f"Resources 1 to 12", watermark=watermark), table_page_2(3, watermark), terms_page(4)]


def make_zip():
    if os.path.exists(ZIP):
        os.remove(ZIP)
    with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED) as z:
        for name, src in [(GUIDE_NAME, GUIDE)] + sources():
            zi = zipfile.ZipInfo(f"{FOLDER}/{name}", date_time=(2026, 11, 23, 12, 0, 0))
            zi.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(zi, open(src, "rb").read())


def build():
    from pypdf import PdfReader, PdfWriter
    os.makedirs(BUILD, exist_ok=True)
    guide = write("guide.html", html_doc(guide_pages(), TITLE + " Guide"))
    prev = write("guide-prev.html", html_doc([start_page(1, True), table_page(2, M[:12], "Resources 1 to 12", watermark=True)], "Preview"))
    gp = os.path.join(BUILD, "guide-prev.pdf")
    render([{"html": guide, "pdf": GUIDE}, {"html": prev, "pdf": gp}])
    w = PdfWriter()
    for p in PdfReader(gp).pages:
        w.add_page(p)
    byid = {m["id"]: m for m in M}
    for mid, pg in PREVIEW_MEMBER_PAGES:
        w.add_page(PdfReader(byid[mid]["prev"]).pages[pg])
    w.write(open(PREVIEW_PDF, "wb"))
    make_zip()
    pdf_png(PREVIEW_PDF, 1, "g1", 100)
    pdf_png(PREVIEW_PDF, 2, "g2", 100)
    items = []
    for mid, pg in SHOTS3:
        pdf_png(byid[mid]["prev"], pg + 1, f"m{mid}", 70)
        items.append((f"m{mid}.png", byid[mid]["short"]))
    sq = [write("cover.html", cover_square()), write("p1.html", preview_1()), write("p2.html", preview_2("g1.png", "g2.png")),
          write("p3.html", preview_3(items))]
    render([{"html": h, "png": o, "width": 1000, "height": 1000, "scale": 2} for h, o in zip(sq, [COVER_PNG] + PREVIEW_PNGS)])
    json.dump(tpt_json(), open(TPT_JSON, "w"), indent=2, ensure_ascii=False)
    open(TPT_JSON, "a").write("\n")
    mb = os.path.getsize(ZIP) / 1048576
    open(UPLOAD, "w").write(upload_md().replace("__ZIPMB__", f"{mb:.1f}"))
    print(f"built guide ({GUIDE_PAGES} pp), preview PDF, ZIP ({mb:.1f} MB), cover, 3 previews, tpt.json, UPLOAD.md")


# ---------------------------------------------------------------- check
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
      document.querySelectorAll('.page').forEach((pg, i) => {
        const pr = pg.getBoundingClientRect();
        const ft = pg.querySelector('.foot');
        if (pg.scrollHeight > pg.clientHeight + 1) res.push(`page ${i + 1}: content overflows the page`);
        if (!ft) { res.push(`page ${i + 1}: no footer`); return; }
        const ftop = ft.getBoundingClientRect().top;
        const skip = el => ft.contains(el) || el.closest('.wm');
        let maxb = 0;
        pg.querySelectorAll('*').forEach(el => {
          if (skip(el)) return;
          const r = el.getBoundingClientRect();
          if (!r.height || !r.width) return;
          if (!el.matches('.main') && r.bottom > ftop - 8) res.push(`page ${i + 1}: ${el.tagName}.${el.className} bottom ${(r.bottom - ftop).toFixed(1)}px vs footer rule (needs <= -8)`);
          if (r.right > pr.right - 0.35 * 96 + 0.5 || r.left < pr.left + 0.35 * 96 - 0.5) res.push(`page ${i + 1}: ${el.tagName}.${el.className} too close to the page edge`);
          if (el.matches('table, .box, p, ul, ol, .hero3')) maxb = Math.max(maxb, r.bottom);
        });
        if (!pg.classList.contains('terms') && ftop - maxb > 230) res.push(`page ${i + 1}: blank band of ${(ftop - maxb).toFixed(0)}px above the footer`);
        pg.querySelectorAll('td, th').forEach(td => { if (td.scrollWidth > td.clientWidth + 1) res.push(`page ${i + 1}: a table cell overflows`); });
      });
      document.querySelectorAll('.sq').forEach((sq, i) => {
        const sr = sq.getBoundingClientRect();
        const btop = sq.querySelector('.band').getBoundingClientRect().top;
        sq.querySelectorAll('.shot, .tile, .cnt, .row, .lbl, .sub, .hd, .store').forEach(el => {
          if (el.closest('.cv-block')) return;
          const r = el.getBoundingClientRect();
          const w = el.classList.contains('shot') ? 8 : 0;
          if (r.left < sr.left + 24 || r.right + w > sr.right - 24) res.push(`square ${i + 1}: ${el.className} within 24px of a side edge`);
          if (r.top < sr.top + 16) res.push(`square ${i + 1}: ${el.className} within 16px of the top`);
          if (r.bottom + w > btop - 8 && !el.matches('.cv-block *')) res.push(`square ${i + 1}: ${el.className} within 8px of the band`);
        });
        sq.querySelectorAll('.row .t').forEach(t => { if (t.scrollWidth > t.clientWidth + 1) res.push(`square ${i + 1}: row title clipped: ${t.textContent}`); });
        sq.querySelectorAll('.cnt > div').forEach(t => { const g = document.createRange(); g.selectNodeContents(t); if (g.getBoundingClientRect().width > t.parentElement.clientWidth - 12) res.push(`square ${i + 1}: count card text too wide`); });
        sq.querySelectorAll('img').forEach(im => { if (!im.complete || im.naturalWidth === 0) res.push(`square ${i + 1}: an image did not load`); });
        const els = [...sq.querySelectorAll('.store, .hd, .sub, .lbl, .shot, .tile, .cnt, .row')].filter(e => !e.closest('.cv-block')).map(e => ({ e, r: e.getBoundingClientRect() }));
        for (let a = 0; a < els.length; a++) for (let c = a + 1; c < els.length; c++) {
          const A = els[a].r, B = els[c].r;
          const sa = els[a].e.matches('.shot') ? 8 : 0, sb = els[c].e.matches('.shot') ? 8 : 0;
          if (A.left < B.right + sb && B.left < A.right + sa && A.top < B.bottom + sb && B.top < A.bottom + sa) res.push(`square ${i + 1}: ${els[a].e.className} overlaps ${els[c].e.className}`);
        }
        const blk = sq.querySelector('.cv-block');
        if (blk) {
          blk.querySelectorAll('.hd').forEach(h => { if ((() => { const g = document.createRange(); g.selectNodeContents(h); const q = g.getBoundingClientRect(); return q.right > sr.right - 24 || q.left < sr.left + 24; })()) res.push('cover title line too wide for the block'); });
        }
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


def pdf_text(p, n=None):
    return subprocess.run(["pdftotext", "-layout", p, "-"], capture_output=True, text=True).stdout


def words(s):
    return set(re.findall(r"[a-z0-9]+", s.lower())) - {"and", "the", "a", "of", "vs", "i", "b"}


def check():
    from pypdf import PdfReader
    from PIL import Image
    errs = []
    # 1. members: release file, price/pages/title/grades read from files
    for m in M:
        if not m["has_release"]:
            errs.append(f"{m['id']}: no release file")
        n = len(PdfReader(m["pdf"]).pages)
        if n != m["pages"]:
            errs.append(f"{m['id']}: PDF has {n} pages, tpt.json says {m['pages']}")
        if not re.search(rf"\b{m['pages']} pages\b", m["up"]):
            errs.append(f"{m['id']}: UPLOAD.md does not state {m['pages']} pages")
        if not words(m["short"]) <= words(m["title"]) | words(os.path.basename(m["dir"])) | words(m["tj"]["files"]["product"]):
            errs.append(f"{m['id']}: short name {m['short']!r} not found in its UPLOAD title / folder: {m['title']}")
        g = m["grades"].replace("-", "[-–]|").split("|")
        a, b = re.split(r"-", m["grades"])
        pat = rf"(?i)grades? {a}\s*(?:[-–]|to)\s*{b}\b|Gr(?:ades?)? {a}[-–]{b}\b|\b{a}[-–]{b}\b|K[-–]8 concert|K[–-]8"
        low = m["up"]
        if m["id"] == "005":
            ok = "K–8" in low or "K-8" in low
        elif m["id"] == "046":
            ok = "grades 4-12" in low or "grades 4–12" in low
        else:
            ok = re.search(pat, low) is not None
        if not ok:
            errs.append(f"{m['id']}: grade range {m['grades']} not stated in its UPLOAD.md")
        if "Logic" in m["title"] or float(m["tj"]["price"]) == 0:
            errs.append(f"{m['id']}: Logic kit or free: not allowed")
    if len({m["id"] for m in M}) != N or N != 23:
        errs.append("member count is not 23")
    # 2. prices
    if abs(SUM - sum(float(m["tj"]["price"]) for m in M)) > 1e-9:
        errs.append("price sum mismatch")
    if PRICE * 2 != int(PRICE * 2):
        errs.append("price not .00/.50")
    if not 0.30 <= 1 - PRICE / SUM <= 0.35:
        errs.append(f"saving {PCT:.1f}% outside 30-35%")
    if RIBBON != int(PCT) or RIBBON > PCT:
        errs.append("ribbon percent is not the saving rounded down")
    cover_html = open(os.path.join(BUILD, "cover.html")).read()
    if f"SAVE {RIBBON}%" not in cover_html or f"{money(SAVE)} OFF" not in cover_html or f">{N}</div>" not in cover_html:
        errs.append("cover ribbon / count callout do not match the computed numbers")
    # 3. zip
    with zipfile.ZipFile(ZIP) as z:
        names = z.namelist()
        want = {f"{FOLDER}/{GUIDE_NAME}": sha(GUIDE)}
        for name, src in sources():
            want[f"{FOLDER}/{name}"] = sha(src)
        for nme, h in want.items():
            if nme not in names:
                errs.append(f"missing in ZIP: {nme}")
            elif hashlib.sha256(z.read(nme)).hexdigest() != h:
                errs.append(f"ZIP copy differs: {nme}")
        if set(names) - set(want) or len(names) != N + 1:
            errs.append(f"unexpected ZIP entries ({len(names)})")
    zmb = os.path.getsize(ZIP) / 1048576
    if zmb > 100:
        errs.append(f"ZIP is {zmb:.1f} MB (over 100 MB)")
    # 4. guide + preview
    gr, pr = PdfReader(GUIDE), PdfReader(PREVIEW_PDF)
    if len(gr.pages) != GUIDE_PAGES:
        errs.append(f"guide must be {GUIDE_PAGES} pages")
    if len(pr.pages) != 4:
        errs.append("preview PDF must be 4 pages")
    for p in (GUIDE, PREVIEW_PDF):
        for pg in PdfReader(p).pages:
            if abs(float(pg.mediabox.width) - 612) > 2 or abs(float(pg.mediabox.height) - 792) > 2:
                errs.append(f"{os.path.basename(p)}: page not US Letter")
        for ln in subprocess.run(["pdffonts", p], capture_output=True, text=True).stdout.splitlines()[2:]:
            if ln.split() and not re.search(r"oswald|sourcesans|source", ln.lower().replace(" ", "")):
                pass
            if ln.split() and ln.split()[-5] != "yes":
                errs.append(f"{os.path.basename(p)}: font not embedded: {ln.strip()}")
    gtxt = " ".join(pdf_text(GUIDE).split())
    for m in M:
        if m["short"] not in gtxt.replace("&amp;", "&") or m["folder"] not in gtxt:
            errs.append(f"guide lacks {m['short']} / {m['folder']}")
    for needle in (f"{money(SUM)}", f"{money(PRICE)}", f"{money(SAVE)}", f"{PCT:.1f}%", "also sold separately", "TERMS OF USE", "YOU MAY NOT"):
        if needle not in gtxt:
            errs.append(f"guide text lacks {needle!r}")
    # guide table rows: pages per row equal the member data
    for m in M:
        if not re.search(rf"{re.escape(m['short'])}.*?{re.escape(m['folder'])}\s+{re.escape(m['grades'])}\s+{m['pages']}\s+{re.escape(money(m['price']))}", gtxt):
            errs.append(f"guide row for {m['short']} does not read grades {m['grades']}, {m['pages']} pages, {money(m['price'])}")
    ptxt = [subprocess.run(["pdftotext", "-f", str(i), "-l", str(i), PREVIEW_PDF, "-"], capture_output=True, text=True).stdout for i in range(1, 5)]
    for i, t in enumerate(ptxt, 1):
        if "PREVIEW" not in subprocess.run(["pdftotext", "-raw", "-f", str(i), "-l", str(i), PREVIEW_PDF, "-"], capture_output=True, text=True).stdout and "PREVIEW" not in t:
            errs.append(f"preview PDF page {i} has no PREVIEW watermark")
    # footers: not clipped (bbox), guide pages numbered
    boxes = subprocess.run(["pdftotext", "-bbox", GUIDE, "-"], capture_output=True, text=True).stdout
    for i, pgx in enumerate(re.findall(r'<page width="([\d.]+)" height="([\d.]+)">(.*?)</page>', boxes, re.S)):
        ys = [float(v) for v in re.findall(r'yMax="([\d.]+)">Lotze', pgx[2])]
        if not ys or max(ys) > float(pgx[1]) - 0.35 * 72:
            errs.append(f"guide p{i + 1}: footer missing or too near the bottom edge")
    # 5. banned strings
    for b in BANNED:
        for p in (GUIDE, PREVIEW_PDF, UPLOAD, TPT_JSON):
            if os.path.exists(p) and b.lower() in (pdf_text(p) if p.endswith(".pdf") else open(p).read()).lower():
                errs.append(f"banned string {b!r} in {os.path.basename(p)}")
    # 6. images
    for p in [COVER_PNG] + PREVIEW_PNGS:
        im = Image.open(p)
        name = os.path.basename(p)
        if im.size != (2000, 2000):
            errs.append(f"{name} is {im.size}")
            continue
        if os.path.getsize(p) > 4 * 1024 * 1024:
            errs.append(f"{name} over 4 MB")
        g = im.convert("L")
        px = g.load()
        ytop = 2000
        for y in range(1999, 0, -1):
            if px[2, y] < 60 and px[1997, y] < 60:
                ytop = y
            else:
                break
        if ytop > 1990 or ytop < 1700:
            errs.append(f"{name}: bottom band not found")
        limit = ytop - 4 if name != "cover.png" else 1370
        for edge, pts in (("top", [(x, y) for x in range(0, 2000, 2) for y in range(0, 14)]),
                          ("left", [(x, y) for x in range(0, 14) for y in range(0, limit, 2)]),
                          ("right", [(x, y) for x in range(1986, 2000) for y in range(0, limit, 2)])):
            if any(px[x, y] < 235 for x, y in pts):
                errs.append(f"{name}: art or ink touches the {edge} edge")
        if "swm" in re.sub(r"<style>.*?</style>", "", cover_html, flags=re.S):
            errs.append("cover carries a watermark")
    # 7. tpt.json / UPLOAD.md
    tj = json.load(open(TPT_JSON))
    up = open(UPLOAD).read()
    if tj["price"] != f"{PRICE:.2f}" or tj["pages"] != TOTAL_PAGES or len(tj["grades"]) > 4:
        errs.append("tpt.json price/pages/grades wrong")
    ut = re.search(r"## 1\. Title\s+```\n(.*?)\n```", up, re.S).group(1).strip()
    if ut != LISTING_TITLE or len(ut) > 80 or re.search(r"(?i)winter|holiday|christmas|hanukkah|december|seasonal", ut):
        errs.append("UPLOAD.md title wrong or over 80 characters")
    desc = up.split("## 2. Description")[1].split("## 3.")[0]
    for m in M:
        if f"{m['i']}. {m['short']} (grades {m['grades']}, {m['pages']} pages)" not in desc:
            errs.append(f"description lacks list line for {m['short']}")
    for needle in (money(SAVE), money(SUM), money(PRICE), "also sold separately", DISCLOSURE):
        if needle not in desc:
            errs.append(f"description lacks {needle!r}")
    pl = up.split("Page list")[1]
    nums = [int(x) for x in re.findall(r": (\d+)\n", pl.split("- Total")[0])]
    if sum(nums) != TOTAL_PAGES or nums[-1] != GUIDE_PAGES or len(nums) != N + 1:
        errs.append("page list does not total the bundle")
    if f"= {TOTAL_PAGES}" not in pl:
        errs.append("page list total line missing")
    if tj["zip_contents"][0] != GUIDE_NAME or len(tj["zip_contents"]) != N + 1:
        errs.append("tpt.json zip_contents wrong")
    for f in tj["files"].values():
        if not os.path.exists(os.path.join(HERE, f)):
            errs.append(f"tpt.json file missing: {f}")
    # 8. layout on rendered output
    js = os.path.join(BUILD, "layout.js")
    open(js, "w").write(LAYOUT_JS)
    r = subprocess.run(["node", js] + [os.path.join(BUILD, x) for x in ("guide.html", "cover.html", "p1.html", "p2.html", "p3.html")],
                       capture_output=True, text=True, env=node_env())
    if r.returncode != 0:
        errs.append("layout script failed: " + r.stderr[-300:])
    else:
        errs += json.loads(r.stdout.strip().splitlines()[-1])
    # 9. members untouched
    st = subprocess.run(["git", "status", "--porcelain", "--"] + [m["dir"] for m in M], capture_output=True, text=True, cwd=ROOT).stdout
    if st.strip():
        errs.append("member folders have uncommitted changes:\n" + st)
    if errs:
        print("CHECK FAILED")
        print("\n".join(" - " + e for e in errs[:60]))
        sys.exit(1)
    print(f"CHECK OK: {N} members, all with release; each PDF page count equals its tpt.json and UPLOAD.md; ZIP {N + 1} files byte-identical to sources, {zmb:.1f} MB; "
          f"sum {money(SUM)}, bundle {money(PRICE)}, saving {money(SAVE)} = {PCT:.1f}% (ribbon SAVE {RIBBON}%); {TOTAL_PAGES} pages ({MEMBER_PAGES}+{GUIDE_PAGES}); "
          f"guide/preview Letter with embedded fonts and watermark; cover + 3 previews 2000x2000 with clean edges and layout checks; description/title/tpt.json agree; members untouched.")


if __name__ == "__main__":
    if "--check" in sys.argv:
        check()
    else:
        build()
