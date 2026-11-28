#!/usr/bin/env python3
"""Color by Note Growing Bundle (TpT 093): ZIP bundle of the 6 paid color-by-note sets (001 027 029 032 035 039), with its own guide, cover, previews and listing files.

    python3 gen.py            build everything into this folder
    python3 gen.py --check    recompute sum, price, saving $ and %, chip, page totals, grades, titles from the member files; verify ZIP (SHA-256), layout, images, tpt.json, UPLOAD.md

Member data (price, pages, grades, worksheet counts, markers) is READ from each member folder (tpt.json, UPLOAD.md, the PDF itself). Member folders are only read, never written.
"""
import glob
import hashlib
import json
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
TITLE = "Color by Note Growing Bundle"
SLUG = "color-by-note-growing-bundle"
FOLDER = "Color by Note Growing Bundle - Hudson Beat"
GUIDE_NAME = "00 START HERE - Bundle Guide.pdf"
ZIP = os.path.join(HERE, f"{SLUG}.zip")
GUIDE = os.path.join(HERE, "bundle-guide.pdf")
PREVIEW_PDF = os.path.join(HERE, f"{SLUG}-PREVIEW.pdf")
COVER_PNG = os.path.join(HERE, "cover.png")
PREVIEW_PNGS = [os.path.join(HERE, f"preview-{i}.png") for i in (1, 2, 3)]
UPLOAD = os.path.join(HERE, "UPLOAD.md")
TPT_JSON = os.path.join(HERE, "tpt.json")
DISCLOSURE = "Created with the help of digital and AI tools. Notation and answer keys are verified before release."
BANNED = ["Blind Brook", "BBHS", "blindbrook", "Google Classroom"]
GUIDE_PAGES = 4

LISTING_TITLE = "Color by Note Growing Bundle | 6 Music Coloring Sets, Rhythm & Notes | Gr 1-6"
TAGS = ["Halloween", "Thanksgiving", "Christmas-Chanukah-Kwanzaa", "Winter", "Printables", "Activities"]
SUBJECTS = ["Music"]
GRADES = ["2nd-grade", "3rd-grade", "4th-grade", "5th-grade"]     # identical on all 6 members (checked)

OWNER_PRICE = 15.00          # sum 22.50 minus 35% = 14.63; $14.50 would be 35.6% off (over the 35% cap), so $15.00 = 33.3% off
EXPECT = dict(sum=22.50, price=15.00, save=7.50, ribbon=33, pages=348, worksheets=162, n=6)

# id, set name (the member's own cover title), what the set colors/reads, short folder name
MEMBERS = [("001", "Halloween Color by Note", "Halloween Color by Note", "Halloween"),
           ("027", "Fall Color by Note", "Fall Color by Note", "Thanksgiving-Fall"),
           ("029", "Winter Color by Note", "Winter Color by Note", "Winter"),
           ("032", "Christmas Color by Note", "Christmas Color by Note", "Christmas"),
           ("035", "Hanukkah Color by Note", "Hanukkah Color by Note", "Hanukkah"),
           ("039", "Winter Color by Music Symbol", "Color by Music Symbol", "Winter-Music-Symbols")]
N = len(MEMBERS)
PREVIEW_MEMBER_PAGES = [("029", 1), ("035", 3)]          # (member id, 0-based page of its own watermarked PREVIEW pdf)
SHOTS3 = [("001", 0), ("027", 0), ("029", 0), ("032", 0), ("035", 0), ("039", 0)]
MARKER_NOTE = {"001": "no release file (it predates the marker) but has uploaded"}


def member_dir(mid):
    return glob.glob(os.path.join(TPT, f"{mid}-*"))[0]


def load_members():
    out = []
    for i, (mid, name, desc_open, folder) in enumerate(MEMBERS, 1):
        d = member_dir(mid)
        tj = json.load(open(os.path.join(d, "tpt.json")))
        up = open(os.path.join(d, "UPLOAD.md")).read()
        title = re.search(r"## 1\. Title\s+```\n(.*?)\n```", up, re.S).group(1).strip()
        g = re.search(r"Grades (\d)–(\d) \(choose", up)
        ws = re.search(r"(\d+) worksheets", up)
        pdf = os.path.join(d, tj["files"]["product"])
        out.append(dict(i=i, id=mid, name=name, desc_open=desc_open, dir=d, tj=tj, up=up, title=title,
                        pdf=pdf, prev=os.path.join(d, tj["files"]["preview"]),
                        price=float(tj["price"]), pages=int(tj["pages"]), worksheets=int(ws.group(1)),
                        g1=int(g.group(1)), g2=int(g.group(2)), grades=f"{g.group(1)}–{g.group(2)}",
                        folder=f"{i:02d}-{folder}", cover=os.path.join(d, "cover.png"),
                        has_release=os.path.exists(os.path.join(d, "release")),
                        has_uploaded=os.path.exists(os.path.join(d, "uploaded"))))
    return out


M = load_members()
SUM = round(sum(m["price"] for m in M), 2)
PRICE = OWNER_PRICE
SAVE = round(SUM - PRICE, 2)
PCT = 100 * (1 - PRICE / SUM)
RIBBON = int(PCT)                                          # "SAVE 33%": real saving rounded DOWN (33.3)
MEMBER_PAGES = sum(m["pages"] for m in M)
TOTAL_PAGES = MEMBER_PAGES + GUIDE_PAGES
WORKSHEETS = sum(m["worksheets"] for m in M)
GMIN, GMAX = min(m["g1"] for m in M), max(m["g2"] for m in M)


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
    return "".join(f'<tr><td class="n"><b>{m["i"]}</b></td><td><b>{escape(m["name"])}</b></td><td class="n">{m["grades"]}</td><td>{escape(m["folder"])}</td>'
                   f'<td class="n">{m["pages"]}</td></tr>' for m in ms)


HEAD = '<tr><th class="n">#</th><th>Set</th><th class="n">Grades</th><th>Folder in the ZIP</th><th class="n">Pages</th></tr>'


def start_page(n, watermark=False):
    inner = (f'<p style="margin-top:8pt">Welcome! This ZIP holds <b>all {N} Hudson Beat Color by Note sets</b> sold today: Halloween, Fall, Winter, Christmas, Hanukkah and Color by Music Symbol. '
             f'Every set has three levels in one file, so each student in a class can color the same picture at their own reading level, and every worksheet has a full-color answer key.</p>'
             f'<div class="hero3"><div><b>{N}</b><span>Sets</span></div><div><b>{WORKSHEETS}</b><span>Worksheets</span></div>'
             f'<div><b>{WORKSHEETS}</b><span>Answer keys</span></div><div><b>{RIBBON}%</b><span>Saved</span></div></div>'
             f'<h2>How to use this bundle</h2><ol>'
             f'<li>Unzip the download. Each set has its own numbered folder (01 to {N:02d}) holding that set&#8217;s PDF.</li>'
             f'<li>Look at the next page: the table lists every set with its grades, page count and folder name.</li>'
             f'<li>Open the PDF you need. Each one starts with a cover and a teacher page with a level guide and a page list; the answer keys are inside the same PDF.</li>'
             f'<li>Choose the level for each student: Level A reads rhythm values, Level B reads treble clef note names, Level C reads bass clef note names '
             f'(in the Color by Music Symbol set: dynamics, tempo terms and music symbols). Print the worksheets and hand out crayons.</li></ol>'
             f'<h2>What you saved</h2>'
             f'<div class="box"><p style="margin:0">The {N} sets sold separately add up to <b>{money(SUM)}</b>. This bundle is <b>{money(PRICE)}</b>: '
             f'you save <b>{money(SAVE)}</b> ({PCT:.1f}%).</p></div>'
             f'<h2>The three levels at a glance</h2>'
             f'<table class="t"><tr><th>Level</th><th>What students read</th><th>Answer key</th></tr>'
             f'<tr><td><b>Level A</b></td><td>Rhythm values: whole, half, quarter and eighth notes and the quarter rest (dynamics in the Music Symbol set)</td><td>Full color, one per worksheet</td></tr>'
             f'<tr><td><b>Level B</b></td><td>Treble clef note names, middle C to A5, with ledger lines (tempo terms in the Music Symbol set)</td><td>Full color, one per worksheet</td></tr>'
             f'<tr><td><b>Level C</b></td><td>Bass clef note names, E2 to middle C, with ledger lines (music symbols in the Music Symbol set)</td><td>Full color, one per worksheet</td></tr></table>'
             f'<h2>Good to know</h2><ul>'
             f'<li>Every picture is original, kid-friendly artwork. No songs, lyrics or copyrighted characters are used.</li>'
             f'<li>Every page prints in black and white. Colors are written as words next to each swatch.</li></ul>')
    return page("Start here", "GUIDE", "Teacher", inner, n, watermark)


def table_page(n, watermark=False):
    tot = (f'<tr><td></td><td><b>Total</b></td><td class="n">{GMIN}&#8211;{GMAX}</td><td>{N} folders</td><td class="n"><b>{MEMBER_PAGES}</b></td></tr>')
    inner = (f'<table class="t" style="margin-top:8pt">{HEAD}{rows_html(M)}{tot}</table>'
             f'<div class="box" style="margin-top:12pt"><p style="margin:0"><b>Bundle price {money(PRICE)}</b> instead of {money(SUM)}: you save {money(SAVE)} ({PCT:.1f}%). '
             f'Each set is also sold separately in the {BRAND} store.</p></div>'
             f'<p class="small" style="margin-top:8pt">Page counts are the pages of each set&#8217;s PDF. The ZIP also holds this {GUIDE_PAGES}-page guide, '
             f'so the bundle has {TOTAL_PAGES} pages in all. Each set has 9 pictures and {M[0]["worksheets"]} worksheets.</p>'
             f'<h2>Sets, pictures and levels</h2><ul>'
             + "".join(f'<li><b>{escape(m["name"])}</b> ({m["grades"]}): {LEVELS[m["id"]]}</li>' for m in M) + '</ul>')
    return page("All 6 sets", "GUIDE", "Set list", inner, n, watermark)


LEVELS = {"001": "Level A rhythm values (1&#8211;2), Level B treble clef (2&#8211;4), Level C bass clef (4&#8211;5)",
          "027": "Level A rhythm values (1&#8211;2), Level B treble clef (2&#8211;4), Level C bass clef (4&#8211;5)",
          "029": "Level A rhythm values (1&#8211;2), Level B treble clef (2&#8211;4), Level C bass clef (4&#8211;5)",
          "032": "Level A rhythm values (2&#8211;3), Level B treble clef (3&#8211;5), Level C bass clef (4&#8211;6)",
          "035": "Level A rhythm values (2&#8211;3), Level B treble clef (3&#8211;5), Level C bass clef (4&#8211;6)",
          "039": "Level A dynamics (2&#8211;3), Level B tempo terms (3&#8211;5), Level C music symbols (4&#8211;5)"}


def growing_page(n, watermark=False):
    inner = (f'<div class="box" style="margin-top:8pt"><p style="margin:0 0 3pt"><b>This is a growing bundle.</b></p>'
             f'<p style="margin:0">Today it holds <b>{N} sets</b>. We plan to add more color-by-note sets over time, but no set or date is promised. '
             f'If a set is added, the bundle&#8217;s price goes up by a share of the new set&#8217;s price. Today&#8217;s price is the lowest the bundle will be: '
             f'the price rises as sets are added.</p></div>'
             f'<div class="hero3"><div><b>{N}</b><span>Sets today</span></div><div><b>{money(PRICE)}</b><span>Price today</span></div>'
             f'<div><b>{money(PRICE / N)}</b><span>Per set today</span></div><div><b>{money(SAVE)}</b><span>You save</span></div></div>'
             f'<h2>How you get new sets</h2><ul>'
             f'<li>If a set is added, we upload a revised ZIP and can use TpT&#8217;s &#8220;Notify Buyers&#8221; option, which shows past buyers a notice on their My Purchases page.</li>'
             f'<li>To get it, open My Purchases on Teachers Pay Teachers, find this bundle and download the updated file. The new set arrives as one more numbered folder, and this guide is refreshed.</li>'
             f'<li>No set or date is promised here: the list above is everything in the ZIP today.</li></ul>'
             f'<h2>Each set is also sold separately</h2>'
             f'<p>Every set in this ZIP is also sold on its own in the {BRAND} store on Teachers Pay Teachers, and the files are the same. '
             f'If you already own some sets, you have them twice: use the folders you need.</p>'
             f'<h2>Which set to open</h2><ul>'
             f'<li>Match the set to the season or the skill: Halloween and Fall in autumn; Winter, Christmas and Hanukkah in the winter months; Color by Music Symbol any time you teach dynamics, tempo terms and music symbols.</li>'
             f'<li>Every set works with a mixed-grade class, because each has three levels in the same file.</li>'
             f'<li>Winter and secular options sit beside the Christmas and Hanukkah sets, so you can choose what fits your school.</li></ul>'
             f'<h2>Please rate</h2><div class="box"><p style="margin:0">Please leave a rating on Teachers Pay Teachers: you earn TpT credits for feedback, and it helps other teachers find this bundle. '
             f'Follow the {BRAND} store for new music resources every week.</p></div>')
    return page("About this growing bundle", "GUIDE", "Growing", inner, n, watermark)


def terms_page(n):
    return (f'<section class="page doc terms"><div class="top"><div class="t">Terms of Use<small>Thank you for your purchase!</small></div></div>'
            f'<div class="main"><p style="margin-top:8pt">© {YEAR} {STORE}. {BRAND} by {STORE}. All rights reserved. This purchase gives <b>one teacher</b> a license to use all {N} sets '
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
            f'<li>Original work by {STORE}, {BRAND}. Each set&#8217;s own terms and credits page applies to its PDF.</li>'
            f'<li>Music notation font: Bravura (&#169; Steinberg Media Technologies GmbH), SIL Open Font License 1.1. Text fonts: Oswald (The Oswald Project Authors) and Source Sans 3 (Adobe), SIL Open Font License 1.1.</li>'
            f'<li>No songs with copyrighted lyrics, film or pop songs, or copyrighted characters are used.</li></ul>'
            f'<h2>Please rate</h2><p>Please leave a rating: you earn TpT credits for feedback, and it helps other teachers find this bundle. '
            f'Follow the {BRAND} store for new music resources every week.</p>'
            f'<p class="small">{DISCLOSURE}</p><div style="flex:1"></div></div>{foot(n)}</section>')


EXTRA_CSS = ""
CSS += EXTRA_CSS


def guide_pages(watermark=False):
    return [start_page(1, watermark), table_page(2, watermark), growing_page(3, watermark), terms_page(4)]


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


def cover_square():
    tw, gap, x0, y0 = 280, 10, 70, 66
    tiles = ""
    for k, m in enumerate(M):
        x, y = x0 + (k % 3) * (tw + gap), y0 + (k // 3) * (tw + gap)
        tiles += f'<div class="tile" style="left:{x}px;top:{y}px;width:{tw}px;height:{tw}px"><img src="{os.path.relpath(m["cover"], BUILD)}"></div>'
    cy = y0 + 2 * tw + gap + 12
    cnt = (f'<div class="cnt" style="left:70px;top:{cy}px;width:200px;height:46px;line-height:42px;font-size:30px;letter-spacing:.05em">{N} SETS</div>'
           f'<div class="cnt" style="left:290px;top:{cy}px;width:400px;height:46px;line-height:42px;font-size:30px;letter-spacing:.08em;background:#000">GROWING BUNDLE</div>'
           f'<div class="cnt" style="left:710px;top:{cy}px;width:220px;height:46px;line-height:42px;font-size:30px;letter-spacing:.05em">SAVE {RIBBON}%</div>')
    by = cy + 46 + 12
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div>{tiles}{cnt}'
        f'<div class="cv-block" style="position:absolute;left:0;right:0;top:{by}px;height:158px;background:{ACCENT};text-align:center;color:#fff">'
        f'<div class="hd" style="position:static;font-size:100px;line-height:1.05;padding-top:4px;letter-spacing:.01em">Color by Note</div>'
        f'<div class="hd" style="position:static;font-size:30px;line-height:1.1;margin-top:2px;letter-spacing:.04em">Rhythm &#183; Treble &#183; Bass &#183; Music symbols</div></div>'
        f'<div class="cv-series" style="position:absolute;left:0;right:0;top:{by + 158}px;height:50px;background:#fff;border-top:3px solid #000;text-align:center;'
        f'font-family:Oswald;font-weight:700;font-size:28px;letter-spacing:.14em;line-height:46px;white-space:nowrap">HUDSON BEAT &#183; COLOR BY NOTE SERIES</div>'
        f'<div class="band">Grades {GMIN}&#8211;{GMAX} <em>&#183;</em> {N} sets <em>&#183;</em> {MEMBER_PAGES} pages <em>&#183;</em> {money(SAVE)} off</div></div>')


def preview_1():
    rows = ""
    for k, m in enumerate(M):
        col, r = k % 2, k // 2
        x, y = 30 + col * 475, 200 + r * 164
        rows += (f'<div class="row" style="left:{x}px;top:{y}px;height:130px;width:465px"><div class="n" style="height:44px;line-height:44px;flex-basis:44px">{m["i"]}</div>'
                 f'<div class="t" style="line-height:1.2"><span style="font-family:Oswald;font-size:27px;text-transform:uppercase;white-space:normal">{escape(m["name"])}</span><br>'
                 f'<span style="font-size:18px;font-weight:600">{m["worksheets"]} worksheets + keys</span></div>'
                 f'<div class="g">Gr {m["grades"]}<br>{m["pages"]} pp</div></div>')
    box = (f'<div class="cnt" style="left:30px;top:706px;width:940px;height:150px;background:#000;line-height:1.15;font-size:52px;letter-spacing:.06em;padding-top:22px">'
           f'GROWING BUNDLE<div style="font-weight:500;font-size:27px;letter-spacing:.03em;margin-top:8px">More sets may follow. Price rises as sets are added.</div></div>')
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div>{hd(f"{N} sets, one download", 70, 78)}'
        f'{sub("Halloween, Fall, Winter, Christmas, Hanukkah and Music Symbols", 27, 160)}{rows}{box}'
        f'<div class="band">{N} sets <em>&#183;</em> save {money(SAVE)} <em>&#183;</em> each set also sold separately</div></div>')


def preview_2(a, b):
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div>{hd("A guide and 6 folders", 70, 78)}'
        f'{sub("How to use it, every set, every grade range, every page count", 27, 160)}'
        f'{shot(a, 70, 214, 400)}{shot(b, 530, 214, 400)}'
        f'<div class="lbl" style="left:70px;top:756px;width:400px;font-size:22px">Start here</div>'
        f'<div class="lbl" style="left:530px;top:756px;width:400px;font-size:22px">All 6 sets</div>'
        f'<div class="band">Numbered folders <em>&#183;</em> {N} PDFs <em>&#183;</em> teacher guide</div></div>')


def preview_3(items):
    cells = ""
    pw = 232
    for i, (src, lab) in enumerate(items):
        x = 104 + (i % 3) * (pw + 48)
        y = 196 + (i // 3) * 372
        cells += shot(src, x, y, pw) + f'<div class="lbl" style="left:{x - 8}px;top:{y + 300 + 12}px;width:{pw + 16}px;font-size:17px;line-height:1.1">{escape(lab)}</div>'
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div>{hd("Real pages from the bundle", 70, 78)}'
        f'{sub("A Level A worksheet from each of the 6 sets", 27, 154)}{cells}'
        f'<div class="band">Three levels <em>&#183;</em> answer keys <em>&#183;</em> print and go</div></div>')


def numbered_list():
    return "\n".join(f"{m['i']}. {m['name']} (grades {m['grades']}, {m['pages']} pages): {m['worksheets']} worksheets + {m['worksheets']} answer keys, {SETDESC[m['id']]}" for m in M)


SETDESC = {"001": "9 Halloween pictures", "027": "9 fall pictures", "029": "9 winter pictures", "032": "9 Christmas pictures",
           "035": "9 Hanukkah pictures", "039": "9 winter pictures, dynamics, tempo terms and symbols"}


def description():
    return f"""Want a color-by-note set ready for every season, without hunting for and buying each one separately? This bundle gives you all {N} Hudson Beat Color by Note sets for grades {GMIN}-{GMAX} in one download. Each set has three levels in one file, so every student can color the same picture at their own reading level: rhythm values, treble clef and bass clef (or dynamics, tempo terms and music symbols in the Music Symbol set). {WORKSHEETS} worksheets and {WORKSHEETS} full-color answer keys, print and go.

GROWING BUNDLE: BUY NOW AT TODAY'S PRICE
This bundle currently holds {N} sets. We plan to add more color-by-note sets over time, but no set or date is promised. If a set is added, the bundle's price goes up by a share of the new set's price. Today's price is the lowest the bundle will be: the price rises as sets are added. If the file is updated, you can download the updated ZIP from your My Purchases page (TpT's "Notify Buyers" option shows past buyers a notice there). 

THE {N} SETS IN THE ZIP (grades and page counts)
{numbered_list()}

WHAT'S INCLUDED (one ZIP, {N} folders)
• {N} product PDFs, {MEMBER_PAGES} pages in all, in numbered folders (01 to {N:02d})
• {WORKSHEETS} worksheets and {WORKSHEETS} answer keys ({N} sets x 27 of each), 9 original pictures per set
• Teacher notes, a student reference page and terms of use inside every set
• A {GUIDE_PAGES}-page start-here guide: how to use the bundle, a table of all {N} sets with grades, page counts and folder names, the growing-bundle note, and terms of use
• Total: {TOTAL_PAGES} pages ({MEMBER_PAGES} + {GUIDE_PAGES})

YOUR SAVING
• The {N} sets sold separately add up to {money(SUM)}. This bundle is {money(PRICE)} today: you save {money(SAVE)}, which is {PCT:.1f}% off.
• Each set is also sold separately in the Hudson Beat store. If you already own some sets, you have them twice: use the folders you need.

GOOD TO KNOW
• This is a ZIP of PDFs. Your computer unzips it; nothing else is needed.
• Files are the same as the individual Hudson Beat listings. Every page prints in black and white; colors are written as words next to each swatch.
• Winter and secular options sit beside the Christmas and Hanukkah sets, and no songs, lyrics or copyrighted characters are used.

Please leave a rating: you earn TpT credits for feedback, and it helps other teachers find this bundle.
Follow the Hudson Beat store for new music resources every week.

{DISCLOSURE}"""


def page_list():
    return ("\n".join(f"- {m['name']}: {m['pages']}" for m in M)
            + f"\n- Start-here guide: {GUIDE_PAGES}\n- Total: {MEMBER_PAGES} + {GUIDE_PAGES} = {TOTAL_PAGES}")


def upload_md():
    ids = ", ".join(m["id"] for m in M)
    return f"""# UPLOAD: {TITLE} (TpT 093)

Fields follow the order of TpT's "Add a resource" form. This is a **ZIP bundle** sold as an ordinary Digital Download (template: tpt/091-year-long-music-sub-plans-bundle, tpt/074-winter-holiday-music-mega-bundle). The {N} member listings (tpt/{ids.replace(", ", ", tpt/")}) are not touched, re-uploaded or changed; the free sampler 028 is not in the bundle. A native TpT Bundle is a later upgrade (TPT-FACTORY.md "Bundles"). No hero art: the collage of the {N} member covers is the art.

**GROWING bundle.** Price today {money(PRICE)}; the price rises by the new set's share each time a set is added (owner policy, queue 093). When the ZIP is updated: replace the file on TpT and tick "Notify Buyers" (TpT Help Center, "How do I notify Buyers when I update or revise a resource?": past buyers then see a notification on their My Purchases page).

**Files to attach**
- Resource (digital download): `{SLUG}.zip` (__ZIPMB__ MB, {N + 1} files, folder "{FOLDER}"): `{GUIDE_NAME}` ({GUIDE_PAGES} pages, built here) plus one numbered folder per set (01 to {N:02d}) holding that set's product PDF, copied unchanged from tpt/{ids.replace(", ", ", tpt/")} (`gen.py --check` proves each byte-identical by SHA-256). Previews, gen.py, QA.md and work files are not included.
- Thumbnails, in order: `cover.png`, `preview-1.png`, `preview-2.png`, `preview-3.png` (all 2000 x 2000).
- Preview file: `{SLUG}-PREVIEW.pdf`, 4 watermarked pages (guide start page, set list, two real member pages: Winter Level B and Hanukkah answer key).

## 1. Title

```
{LISTING_TITLE}
```
({len(LISTING_TITLE)} characters; the limit is 80.) No holiday or season word, per TPT-FACTORY.md "Bundles".

## 2. Description

```
{description()}
```

## 3. Grades

2nd, 3rd, 4th, 5th (the same four boxes as the {N} members; the description says grades {GMIN}-{GMAX}, the span of the levels).

## 4. Subjects, tags, formats

Subjects: {", ".join(SUBJECTS)}. Tags: {", ".join(TAGS)} (exact entries of tpt/TAG-OPTIONS.json, none a heading; the season stays in the tags, not the title). Formats PDF (ZIP).

## 5. Price (arithmetic)

Sum of the {N} member prices: **{money(SUM)}** ({" + ".join(f"{m['price']:.2f}" for m in M)}). 35% under is {SUM * 0.65:.2f}; $14.50 would be {100 * (1 - 14.5 / SUM):.1f}% off (over the 35% cap), so the bundle price is **{money(PRICE)}**: saving {money(SAVE)} = {PCT:.1f}% (the cover chip says SAVE {RIBBON}%, the real saving rounded down). Multiple-license price {money(PRICE)}.

## 6. Free preview and pages

Paid. Preview PDF 4 pages. "Number of pages or slides": {TOTAL_PAGES}.
Page list (totals the guide PDF exactly; the ZIP holds {N} product PDFs and the guide):
{page_list()}

## 7. Sources and credits

No new facts or tunes: each set's own terms page applies. Fonts: Bravura, Oswald and Source Sans 3 (OFL 1.1). No hero art; cover is a collage of the members' own covers.

## 8. Before you click publish

- [ ] `python3 tools/tpt-validate.py tpt/093-color-by-note-growing-bundle` and `node tools/tpt.js publish tpt/093-color-by-note-growing-bundle --dry-run` on the Mac.
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


def make_zip():
    if os.path.exists(ZIP):
        os.remove(ZIP)
    with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED) as z:
        for name, src in [(GUIDE_NAME, GUIDE)] + sources():
            zi = zipfile.ZipInfo(f"{FOLDER}/{name}", date_time=(2026, 11, 28, 12, 0, 0))
            zi.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(zi, open(src, "rb").read())


def build():
    from pypdf import PdfReader, PdfWriter
    os.makedirs(BUILD, exist_ok=True)
    guide = write("guide.html", html_doc(guide_pages(), TITLE + " Guide"))
    prev = write("guide-prev.html", html_doc([start_page(1, True), table_page(2, True)], "Preview"))
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
        items.append((f"m{mid}.png", byid[mid]["name"]))
    sq = [write("cover.html", cover_square()), write("p1.html", preview_1()), write("p2.html", preview_2("g1.png", "g2.png")),
          write("p3.html", preview_3(items))]
    render([{"html": h, "png": o, "width": 1000, "height": 1000, "scale": 2} for h, o in zip(sq, [COVER_PNG] + PREVIEW_PNGS)])
    json.dump(tpt_json(), open(TPT_JSON, "w"), indent=2, ensure_ascii=False)
    open(TPT_JSON, "a").write("\n")
    mb = os.path.getsize(ZIP) / 1048576
    open(UPLOAD, "w").write(upload_md().replace("__ZIPMB__", f"{mb:.1f}"))
    print(f"built guide ({GUIDE_PAGES} pp), preview PDF, ZIP ({mb:.1f} MB), cover, 3 previews, tpt.json, UPLOAD.md")


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


def check():
    from pypdf import PdfReader
    from PIL import Image
    errs = []
    notes = []
    for m in M:
        if not m["has_uploaded"]:
            errs.append(f"{m['id']}: no uploaded marker (not live on TpT)")
        if not m["has_release"]:
            if m["id"] in MARKER_NOTE:
                notes.append(f"{m['id']}: {MARKER_NOTE[m['id']]}")
            else:
                errs.append(f"{m['id']}: no release file")
        n = len(PdfReader(m["pdf"]).pages)
        if n != m["pages"]:
            errs.append(f"{m['id']}: PDF has {n} pages, tpt.json says {m['pages']}")
        if not re.search(rf"\b{m['pages']} pages\b", m["up"]):
            errs.append(f"{m['id']}: UPLOAD.md does not state {m['pages']} pages")
        if m["worksheets"] != 27:
            errs.append(f"{m['id']}: {m['worksheets']} worksheets (expected 27)")
        if m["id"] == "028" or "sampler" in m["dir"]:
            errs.append("free sampler in members")
        if m["tj"]["grades"] != GRADES:
            errs.append(f"{m['id']}: grades differ from the bundle")
        if m["price"] <= 0:
            errs.append(f"{m['id']}: price {m['price']} not paid")
        if m["desc_open"] not in m["up"].split("## 2. Description")[1][:200]:
            errs.append(f"{m['id']}: description does not open with {m['desc_open']!r}")
        pf = subprocess.run(["pdfinfo", m["pdf"]], capture_output=True, text=True).stdout
        if f"Pages:           {m['pages']}" not in pf:
            errs.append(f"{m['id']}: pdfinfo page count differs")
    if [m["id"] for m in M] != ["001", "027", "029", "032", "035", "039"] or N != EXPECT["n"]:
        errs.append("members are not 001 027 029 032 035 039")
    for k, v in (("sum", SUM), ("price", PRICE), ("save", SAVE), ("ribbon", RIBBON), ("pages", MEMBER_PAGES), ("worksheets", WORKSHEETS)):
        if v != EXPECT[k]:
            errs.append(f"{k} is {v}, expected {EXPECT[k]}")
    if not (30 <= PCT <= 35) or RIBBON > PCT or RIBBON != int(PCT) or (PRICE * 2) != int(PRICE * 2):
        errs.append(f"saving {PCT:.3f}% / chip {RIBBON} wrong (must be 30-35% and rounded down; price .00 or .50)")
    if abs(SUM - sum(float(json.load(open(os.path.join(m['dir'], 'tpt.json')))["price"]) for m in M)) > 1e-9:
        errs.append("sum mismatch")
    cover_html = open(os.path.join(BUILD, "cover.html")).read()
    for needle in (f"SAVE {RIBBON}%", f"{N} SETS", "GROWING BUNDLE", "COLOR BY NOTE SERIES", f"{MEMBER_PAGES} pages", f"{money(SAVE)} off"):
        if needle not in cover_html:
            errs.append(f"cover lacks {needle!r}")
    for m in M:
        if os.path.relpath(m["cover"], BUILD) not in cover_html:
            errs.append(f"cover lacks tile of {m['id']}")
        if Image.open(m["cover"]).size != (2000, 2000):
            errs.append(f"{m['id']} cover not 2000x2000")
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
            if ln.split() and ln.split()[-5] != "yes":
                errs.append(f"{os.path.basename(p)}: font not embedded: {ln.strip()}")
    gtxt = " ".join(pdf_text(GUIDE).split())
    for m in M:
        if not re.search(rf"{m['i']}\s+{re.escape(m['name'])}\s+{m['grades']}\s+{re.escape(m['folder'])}\s+{m['pages']}\b", gtxt):
            errs.append(f"guide row for {m['name']} does not read grades {m['grades']}, folder {m['folder']}, {m['pages']} pages")
    for needle in (money(SUM), money(PRICE), money(SAVE), f"{PCT:.1f}%", "also sold separately", "TERMS OF USE", "YOU MAY NOT", "growing bundle", "no set or date is promised", "My Purchases", "Welcome", DISCLOSURE):
        if needle.lower() not in gtxt.lower():
            errs.append(f"guide text lacks {needle!r}")
    for i in range(1, 5):
        if "PREVIEW" not in subprocess.run(["pdftotext", "-raw", "-f", str(i), "-l", str(i), PREVIEW_PDF, "-"], capture_output=True, text=True).stdout:
            errs.append(f"preview PDF page {i} has no PREVIEW watermark")
    boxes = subprocess.run(["pdftotext", "-bbox", GUIDE, "-"], capture_output=True, text=True).stdout
    for i, pgx in enumerate(re.findall(r'<page width="([\d.]+)" height="([\d.]+)">(.*?)</page>', boxes, re.S)):
        ys = [float(v) for v in re.findall(r'yMax="([\d.]+)">Lotze', pgx[2])]
        if not ys or max(ys) > float(pgx[1]) - 0.35 * 72:
            errs.append(f"guide p{i + 1}: footer missing or too near the bottom edge")
    for b in BANNED:
        for p in (GUIDE, PREVIEW_PDF, UPLOAD, TPT_JSON):
            if os.path.exists(p) and b.lower() in (pdf_text(p) if p.endswith(".pdf") else open(p).read()).lower():
                errs.append(f"banned string {b!r} in {os.path.basename(p)}")
    for p in [COVER_PNG] + PREVIEW_PNGS:
        im = Image.open(p)
        name = os.path.basename(p)
        if im.size != (2000, 2000):
            errs.append(f"{name} is {im.size}")
            continue
        if os.path.getsize(p) > 4 * 1024 * 1024:
            errs.append(f"{name} over 4 MB")
        px = im.convert("L").load()
        ytop = 2000
        for y in range(1999, 0, -1):
            if px[2, y] < 60 and px[1997, y] < 60:
                ytop = y
            else:
                break
        if ytop > 1990 or ytop < 1700:
            errs.append(f"{name}: bottom band not found")
        limit = ytop - 4 if name != "cover.png" else 1300
        for edge, pts in (("top", [(x, y) for x in range(0, 2000, 2) for y in range(0, 14)]),
                          ("left", [(x, y) for x in range(0, 14) for y in range(0, limit, 2)]),
                          ("right", [(x, y) for x in range(1986, 2000) for y in range(0, limit, 2)])):
            if any(px[x, y] < 235 for x, y in pts):
                errs.append(f"{name}: art or ink touches the {edge} edge")
    tj = json.load(open(TPT_JSON))
    up = open(UPLOAD).read()
    opts = json.load(open(os.path.join(TPT, "TAG-OPTIONS.json")))["options"]
    if tj["price"] != f"{PRICE:.2f}" or tj["license_price"] != tj["price"] or tj["pages"] != TOTAL_PAGES or len(tj["grades"]) > 4 or tj["grades"] != GRADES:
        errs.append("tpt.json price/pages/grades wrong")
    if tj["subjects"] != ["Music"] or not 1 <= len(tj["tags"]) <= 6 or any(t not in opts for t in tj["tags"]) or tj["tags"] != TAGS:
        errs.append("tpt.json tags/subjects wrong")
    ut = re.search(r"## 1\. Title\s+```\n(.*?)\n```", up, re.S).group(1).strip()
    if ut != LISTING_TITLE or len(ut) > 80 or not ut.startswith("Color by Note Growing Bundle") or re.search(
            r"(?i)winter|holiday|christmas|hanukkah|halloween|thanksgiving|fall\b|autumn|seasonal|december|valentine", ut):
        errs.append("UPLOAD.md title wrong, over 80 characters or seasonal")
    desc = up.split("## 2. Description")[1].split("## 3.")[0]
    for m in M:
        if f"{m['i']}. {m['name']} (grades {m['grades']}, {m['pages']} pages):" not in desc:
            errs.append(f"description lacks list line for {m['name']}")
    for needle in (money(SAVE), money(SUM), money(PRICE), f"{PCT:.1f}%", "also sold separately", "GROWING BUNDLE", "currently holds 6 sets", "no set or date is promised", "My Purchases", DISCLOSURE,
                   f"{WORKSHEETS} worksheets", f"{TOTAL_PAGES} pages"):
        if needle not in desc:
            errs.append(f"description lacks {needle!r}")
    if re.search(r"(?i)valentine|st\. patrick|keep every future set", desc):
        errs.append("description promises specific sets or an unsourced mechanism")
    if not desc.strip().strip("`").strip().startswith("Want a color-by-note set"):
        errs.append("description does not open with the buyer's problem")
    pl = up.split("Page list")[1]
    nums = [int(x) for x in re.findall(r": (\d+)\n", pl.split("- Total")[0])]
    if sum(nums) != TOTAL_PAGES or nums[-1] != GUIDE_PAGES or len(nums) != N + 1 or f"= {TOTAL_PAGES}" not in pl:
        errs.append("page list does not total the bundle")
    if tj["zip_contents"][0] != GUIDE_NAME or len(tj["zip_contents"]) != N + 1:
        errs.append("tpt.json zip_contents wrong")
    for f in tj["files"].values():
        if not os.path.exists(os.path.join(HERE, f)):
            errs.append(f"tpt.json file missing: {f}")
    js = os.path.join(BUILD, "layout.js")
    open(js, "w").write(LAYOUT_JS)
    r = subprocess.run(["node", js] + [os.path.join(BUILD, x) for x in ("guide.html", "cover.html", "p1.html", "p2.html", "p3.html")],
                       capture_output=True, text=True, env=node_env())
    if r.returncode != 0:
        errs.append("layout script failed: " + r.stderr[-300:])
    else:
        errs += json.loads(r.stdout.strip().splitlines()[-1])
    st = subprocess.run(["git", "status", "--porcelain", "--"] + [m["dir"] for m in M], capture_output=True, text=True, cwd=ROOT).stdout
    if st.strip():
        errs.append("member folders have uncommitted changes:\n" + st)
    if errs:
        print("CHECK FAILED")
        print("\n".join(" - " + e for e in errs[:60]))
        sys.exit(1)
    print(f"CHECK OK: {N} members (uploaded markers present; {'; '.join(notes) or 'all have release'}), 3.50+3.75+3.75+4.00+3.50+4.00; {WORKSHEETS} worksheets; ZIP {N + 1} files byte-identical to sources, {zmb:.1f} MB; "
          f"sum {money(SUM)}, bundle {money(PRICE)}, saving {money(SAVE)} = {PCT:.1f}% (SAVE {RIBBON}%); {MEMBER_PAGES}+{GUIDE_PAGES}={TOTAL_PAGES} pages; "
          f"title {len(LISTING_TITLE)} chars; guide/preview Letter, fonts embedded, watermark; cover + 3 previews 2000x2000 clean edges; description/title/tpt.json agree; members untouched.")


if __name__ == "__main__":
    if "--check" in sys.argv:
        check()
    else:
        build()
