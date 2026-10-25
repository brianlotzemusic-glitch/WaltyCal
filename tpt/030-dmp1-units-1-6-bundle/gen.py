#!/usr/bin/env python3
"""DMP1 Units 1-6 Bundle (TpT 030): fallback ZIP bundle of kits 008-013, with its own guide, cover, previews and listing files.

    python3 gen.py            build everything into this folder
    python3 gen.py --check    verify the ZIP (all six kits' files present and byte-identical to their sources), guide, previews, images, tpt.json

tools/tpt.js cannot drive TpT's native "Bundle of Resources" type yet (the picker has no URL and its form was never recorded), so this is ONE Digital
Download ZIP. The kits' files are copied unchanged into the ZIP (one folder per unit); nothing from the six kit folders is edited or duplicated on disk.
Only new files: the bundle guide PDF, preview PDF, cover, 3 previews, ZIP, UPLOAD.md, tpt.json.
"""
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import zipfile
from html import escape

HERE = os.path.dirname(os.path.abspath(__file__))
TPT = os.path.dirname(HERE)
BUILD = os.path.join(HERE, "build")
RENDER_JS = os.path.join(TPT, "tools", "render.js")

# ---- reuse the shared Hudson Beat CSS from kit 008 (import only; nothing is written there)
_spec = importlib.util.spec_from_file_location("g8", os.path.join(TPT, "008-dmp1-beat-from-nothing", "gen.py"))
g8 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(g8)

STORE, BRAND, YEAR = "Brian Lotze", "Hudson Beat", 2026
ACCENT = "#B8860B"   # this product's single accent: dark gold (kits use red, orange, violet, teal, blue, green)
TITLE = "DMP1 Units 1-6 Bundle"
FOLDER = "DMP1 Units 1-6 Bundle - Hudson Beat"
SLUG = "dmp1-units-1-6-bundle"
GUIDE_NAME = "00 START HERE - Bundle Guide.pdf"
ZIP = os.path.join(HERE, f"{SLUG}.zip")
GUIDE = os.path.join(HERE, "bundle-guide.pdf")
PREVIEW_PDF = os.path.join(HERE, f"{SLUG}-PREVIEW.pdf")
COVER_PNG = os.path.join(HERE, "cover.png")
PREVIEW_PNGS = [os.path.join(HERE, f"preview-{i}.png") for i in (1, 2, 3)]
DISCLOSURE = "Designed with the help of digital and AI tools, and checked by hand."
BANNED = ["Blind Brook", "BBHS", "blindbrook", "Google Classroom", "Thunderstruck"]

# (unit, kit folder, file stem, unit title, price, days, pdf pages, slides, what students make)
KITS = [
    (1, "008-dmp1-beat-from-nothing", "beat-from-nothing", "Beat From Nothing", 9, 4, 21, 15,
     "an original 16-measure drum beat in AABA form, programmed from nothing in Logic Pro"),
    (2, "013-dmp1-stems-and-grooves", "stems-and-grooves", "Stems and Grooves", 10, 6, 28, 22,
     "drums over a stem: two contrasting grooves, then a full song with a transition at each section change"),
    (3, "011-dmp1-chords-by-ear", "chords-by-ear", "Chords by Ear", 12, 5, 35, 21,
     "major and minor chords labelled with Roman numerals, as a chord layer over a bassline"),
    (4, "012-dmp1-bass-melody-writing", "bass-melody-writing", "Bass and Melody Writing", 10, 4, 30, 22,
     "a short melody written from a scale, and a bassline over four chosen chords"),
    (5, "010-dmp1-song-form", "song-form", "Song Form", 10, 4, 27, 17,
     "a song arranged from chords, bass and melody, with at least four sections"),
    (6, "009-dmp1-spooky-tunes", "spooky-tunes", "Spooky Tunes", 12, 6, 31, 16,
     "a 32-measure score to a one-minute video, with reverb and delay on shared buses"),
]
SUFFIXES = [".pdf", "-intro-deck.pptx", "-intro-deck.pdf"]
PRICE_SUM = sum(k[4] for k in KITS)            # 63
PRICE = 49                                      # about 22% off
DAYS = sum(k[5] for k in KITS)                  # 29
PDF_PAGES = sum(k[6] for k in KITS)             # 172
SLIDES = sum(k[7] for k in KITS)                # 113


def unit_dir(k):
    return f"Unit {k[0]} - {k[3]}"


def sources():
    """[(zip path inside bundle folder, absolute source path)] for every kit file."""
    out = []
    for k in KITS:
        for s in SUFFIXES:
            out.append((f"{unit_dir(k)}/{k[2]}{s}", os.path.join(TPT, k[1], f"{k[2]}{s}")))
    return out


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


# ---------------------------------------------------------------- pages
CSS = g8.CSS.replace(g8.ACCENT, ACCENT) + """
.tiles { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14pt; width: 100%; }
.tile { border: 1.8pt solid #000; border-radius: 8pt; padding: 8pt 6pt 10pt; text-align: center; background: #fff; }
.tile .n { font-family: 'Oswald'; font-weight: 700; font-size: 54pt; line-height: 1; color: ACCENT; }
.tile .u { font-family: 'Oswald'; font-weight: 500; font-size: 9pt; letter-spacing: .24em; text-transform: uppercase; }
.tile .t { font-family: 'Oswald'; font-weight: 700; font-size: 15pt; text-transform: uppercase; line-height: 1.05; margin-top: 4pt; }
.tile .d { font-family: 'Oswald'; font-weight: 300; font-size: 11pt; margin-top: 3pt; }
.tree { font-size: 10.4pt; line-height: 1.5; border: 1.4pt solid #000; border-radius: 8pt; padding: 8pt 12pt; }
.tree b { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; letter-spacing: .02em; }
.tree .f { padding-left: 18pt; color: #222; }
""".replace("ACCENT", ACCENT)
COPY = f"© {YEAR} {STORE} · {BRAND} · For single-classroom use"


def foot(n):
    return f'<div class="foot"><span>{COPY}</span><span>Page {n}</span></div>'


def wm(on):
    return '<div class="wm">PREVIEW</div>' if on else ""


def page(sub, tag, tagsub, inner, n, watermark=False):
    top = (f'<div class="top"><div class="t">{escape(TITLE)}<small>{sub}</small></div>'
           f'<div class="tag"><div class="lv">{tag}</div><div class="ln">{tagsub}</div></div></div>')
    return f'<section class="page">{wm(watermark)}{top}<div class="main">{inner}</div>{foot(n)}</section>'


def tiles(desc=True):
    cells = ""
    for k in KITS:
        d = f'<div class="d">{k[5]} days</div>' if desc else ""
        cells += f'<div class="tile"><div class="u">Unit</div><div class="n">{k[0]}</div><div class="t">{escape(k[3])}</div>{d}</div>'
    return f'<div class="tiles">{cells}</div>'


def cover_page():
    return (f'<section class="page cover"><div class="store">{BRAND}</div><div style="width:100%;margin-top:.3in">{tiles()}</div>'
            f'<div class="ctitle"><div class="a">Digital Music Production 1</div><div class="b">Units 1–6 Bundle</div>'
            f'<div class="c">Bundle guide · six units in Logic Pro · {DAYS} class periods</div></div>'
            f'<div class="cband">Grades 9–12 <em>·</em> 6 units <em>·</em> {PDF_PAGES} pages + {SLIDES} slides</div></section>')


def order_page(n, watermark=False):
    rows, start = "", 1
    for k in KITS:
        end = start + k[5] - 1
        rows += (f'<tr><td><b>{k[0]}</b></td><td><b>{escape(k[3])}</b></td><td>{k[5]}</td><td>{start}–{end}</td>'
                 f'<td>{escape(k[8])}</td><td>{k[6]} pp + {k[7]} slides</td></tr>')
        start = end + 1
    inner = (f'<p>Teach the units in this order. It is the course order the units are numbered in, and each unit works as a stand-alone teaching unit.</p>'
             f'<table class="t"><tr><th>Unit</th><th>Title</th><th>Days</th><th>Periods</th><th>Students make</th><th>In the folder</th></tr>{rows}'
             f'<tr><td></td><td><b>Total</b></td><td><b>{DAYS}</b></td><td>1–{DAYS}</td><td></td><td><b>{PDF_PAGES} pp + {SLIDES} slides</b></td></tr></table>'
             f'<h2 class="s">Pacing</h2>'
             f'<ul><li>The units are planned for about 53-minute class periods, {DAYS} in all: about six school weeks if the class meets five days a week.</li>'
             f'<li>Each unit has its own minute-by-minute day plans (the pacing page near the front of its PDF). Unit 1 has a note on stretching to 5 days, '
             f'and Unit 5 has a note on running in 3 days if you are short on time.</li></ul>'
             f'<h2 class="s">Why this order</h2>'
             f'<ul><li><b>Unit 2</b> builds on Unit 1, Beat From Nothing.</li>'
             f'<li><b>Unit 4</b> picks up where Unit 3 ends: students continue in their Unit 3 project, or use a file made from the recipe on its setup page.</li>'
             f'<li><b>Unit 5</b> arranges a chord progression and bassline students already have, so it follows Units 3 and 4. If they have none, its setup page shows a quick way to make one.</li>'
             f'<li><b>Unit 6</b> needs no key, chord progression or song form (students may work in any key), so you can move it earlier, for example to October for Halloween.</li></ul>')
    return page("Unit order and pacing", "GUIDE", "Teacher", inner, n, watermark)


def folder_page(n, watermark=False):
    tree = f'<b>{FOLDER}</b><br>'
    tree += f'<span class="f">{GUIDE_NAME}</span><br>'
    for k in KITS:
        tree += f'<b>&nbsp;&nbsp;{escape(unit_dir(k))}</b><br>'
        for s in SUFFIXES:
            tree += f'<span class="f">&nbsp;&nbsp;{k[2]}{s}</span><br>'
    inner = (f'<div class="cols"><div><div class="tree">{tree}</div></div><div>'
             f'<h2 class="s">In every unit folder</h2>'
             f'<ul><li><b>The PDF</b>: how to use, unit overview and setup, pacing and day plans, teacher notes, student pages, rubric and answer key.</li>'
             f'<li><b>The intro deck (.pptx)</b>: the teacher-presented slides, with speaker notes on every slide.</li>'
             f'<li><b>The intro deck (PDF)</b>: a copy that shows the intended look. The deck uses the free Oswald and Source Sans 3 fonts.</li></ul>'
             f'<h2 class="s">How to start</h2><ol><li>Open this guide, then the folder for Unit 1.</li>'
             f'<li>Read the unit PDF\'s how-to-use and pacing pages, then the teacher notes.</li>'
             f'<li>Present the intro deck on Day 1 and print the student pages.</li></ol>'
             f'<h2 class="s">What you supply</h2>'
             f'<ul><li>Logic Pro on a Mac. The steps are written for Logic Pro; the music ideas carry over to other DAWs.</li>'
             f'<li>No audio, video, stems or Logic sessions are included. Where a unit needs a file (stems for Unit 2, a short bassline file for Units 3 and 4, a one-minute video for Unit 6), '
             f'that unit\'s setup page explains how to make or find one.</li>'
             f'<li>Songs named in a unit are named for reference only; play them from your own streaming access.</li></ul></div></div>')
    return page("What is in the ZIP", "GUIDE", "Folder map", inner, n, watermark)


def terms_page(n):
    return (f'<section class="page"><div class="top"><div class="t">Terms of Use<small>Thank you for your purchase!</small></div></div>'
            f'<div class="main"><p>© {YEAR} {STORE}. {BRAND} by {STORE}. All rights reserved. This purchase gives <b>one teacher</b> a license to use all six units '
            f'(the PDFs and the intro decks) with their own students.</p>'
            f'<h2 class="s">You may</h2><ul><li>Print and copy pages for your own classroom and students, year after year.</li>'
            f'<li>Present the intro decks to your own classes and edit them for your own teaching.</li>'
            f'<li>Share pages with your own students through a password-protected class site or learning platform.</li>'
            f'<li>Leave the pages for a substitute teacher who teaches your own students.</li></ul>'
            f'<h2 class="s">You may not</h2><ul><li>Share, email or copy this resource for other teachers, a whole school or a district. '
            f'Additional licenses are available on Teachers Pay Teachers.</li>'
            f'<li>Post any part of it on a public website, shared drive or social media.</li>'
            f'<li>Sell, give away or claim any part of it as your own, or edit it into a new product.</li></ul>'
            f'<h2 class="s">Questions?</h2><p>Please use the Q&amp;A tab on the {BRAND} by {STORE} store on Teachers Pay Teachers.</p>'
            f'<h2 class="s">Credits</h2><ul>'
            f'<li>Curriculum, project sheets, rubrics, teacher notes and intro decks: original work by {STORE}, {BRAND}. Each unit\'s own credits page applies to its files.</li>'
            f'<li>Text fonts: Oswald (The Oswald Project Authors) and Source Sans 3 (Adobe), SIL Open Font License 1.1.</li>'
            f'<li>Logic Pro is a trademark of Apple Inc., named only to describe compatibility; this resource is not affiliated with or endorsed by Apple.</li></ul>'
            f'<p class="small">{DISCLOSURE}</p><div style="flex:1"></div></div>{foot(n)}</section>')


def html_doc(pages, title):
    return (f'<!doctype html><html><head><meta charset="utf-8"><title>{escape(title)}</title>'
            f'<style>{g8.font_css(BUILD)}{CSS}</style></head><body>{"".join(pages)}</body></html>')


SQ_CSS = g8.SQ_CSS.replace(g8.ACCENT, ACCENT) + """
.tiles { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14pt; width: 100%; }
.tile { border: 1.8pt solid #000; border-radius: 8pt; padding: 8pt 6pt 10pt; text-align: center; background: #fff; }
.tile .n { font-family: 'Oswald'; font-weight: 700; font-size: 54pt; line-height: 1; color: %ACC%; }
.tile .u { font-family: 'Oswald'; font-weight: 500; font-size: 9pt; letter-spacing: .24em; text-transform: uppercase; }
.tile .t { font-family: 'Oswald'; font-weight: 700; font-size: 15pt; text-transform: uppercase; line-height: 1.05; margin-top: 4pt; }
.tile .d { font-family: 'Oswald'; font-weight: 300; font-size: 11pt; margin-top: 3pt; }
""".replace("%ACC%", ACCENT) + """
.sq .tiles { width: 880px; gap: 22px; }
.sq .tile { padding: 14px 8px 18px; border-width: 3px; }
.sq .tile .n { font-size: 100px; } .sq .tile .u { font-size: 17px; } .sq .tile .t { font-size: 27px; margin-top: 6px; } .sq .tile .d { font-size: 21px; }
"""


def sq_doc(body):
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{g8.font_css(BUILD)}'
            f'html,body{{margin:0;background:#fff}}{SQ_CSS}</style></head><body>{g8.FONT_PRIME}{body}</body></html>')


def cover_square():
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div><div style="margin-top:36px">{tiles()}</div>'
        f'<div class="hd" style="font-size:52px;margin-top:40px">Digital Music Production 1</div>'
        f'<div class="hd" style="font-size:112px">Units 1–6 Bundle</div>'
        f'<div class="sub" style="font-size:29px;margin-top:12px">Six Logic Pro units · teacher notes · rubrics · intro decks</div>'
        f'<div class="band">Grades 9–12 <em>·</em> 6 units <em>·</em> {DAYS} class periods</div></div>')


def shot(img, w, wmsize=60):
    return f'<div class="shot" style="width:{w}px"><img src="{img}"><div class="swm" style="font-size:{wmsize}px">PREVIEW</div></div>'


def preview_1(covers):
    cells = "".join(f'<div style="width:270px"><div class="shot" style="box-shadow:6px 6px 0 #000"><img src="{c}"></div>'
                    f'<div class="lbl" style="font-size:19px;margin-top:10px">Unit {k[0]}<span>{k[5]} days</span></div></div>' for c, k in zip(covers, KITS))
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div><div class="hd" style="font-size:74px;margin-top:20px">Six units in one download</div>'
        f'<div class="sub" style="font-size:27px;margin-top:8px">Each unit is a PDF plus a teacher-presented intro deck</div>'
        f'<div style="display:grid;grid-template-columns:repeat(3,270px);gap:30px 36px;margin-top:46px">{cells}</div>'
        f'<div class="band">{PDF_PAGES} pages <em>·</em> {SLIDES} slides <em>·</em> {DAYS} class periods</div></div>')


def preview_2(a, b):
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div><div class="hd" style="font-size:74px;margin-top:20px">A plan from Day 1 to Day {DAYS}</div>'
        f'<div class="sub" style="font-size:27px;margin-top:8px">Unit order, pacing and a clean folder for each unit</div>'
        f'<div style="display:flex;gap:40px;margin-top:50px;align-items:flex-start">'
        f'{shot(a, 400, 54)}{shot(b, 400, 54)}</div>'
        f'<div class="band">Start-here guide <em>·</em> one folder per unit</div></div>')


def preview_3(imgs):
    cells = "".join(f'<div style="width:270px">{shot(i, 270, 44)}<div class="lbl" style="font-size:19px;margin-top:10px">{lab}</div></div>' for i, lab in imgs)
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div><div class="hd" style="font-size:70px;margin-top:20px">What is inside each unit</div>'
        f'<div class="sub" style="font-size:27px;margin-top:8px">Day plans, student pages, rubrics and answer keys from the six units</div>'
        f'<div style="display:grid;grid-template-columns:repeat(3,270px);gap:26px 36px;margin-top:44px">{cells}</div>'
        f'<div class="band">Teacher notes <em>·</em> student pages <em>·</em> rubrics <em>·</em> keys</div></div>')


# ---------------------------------------------------------------- build
def node_env():
    env = dict(os.environ)
    if not env.get("NODE_PATH"):
        env["NODE_PATH"] = subprocess.run(["npm", "root", "-g"], capture_output=True, text=True).stdout.strip()
    return env


def render(jobs):
    p = os.path.join(BUILD, "jobs.json")
    with open(p, "w") as f:
        json.dump(jobs, f)
    subprocess.run(["node", RENDER_JS, p], check=True, env=node_env())


def write(name, txt):
    p = os.path.join(BUILD, name)
    with open(p, "w") as f:
        f.write(txt)
    return p


def pdf_png(src, n, out, res):
    subprocess.run(["pdftoppm", "-png", "-r", str(res), "-f", str(n), "-l", str(n), "-singlefile", src, os.path.join(BUILD, out)], check=True)


def tpt_json():
    return {
        "price": f"{PRICE}.00", "license_price": f"{PRICE}.00",
        "tax_code": "Other Digital Goods - No Physical Media",
        "grades": ["9th-grade", "10th-grade", "11th-grade", "12th-grade"],
        "subjects": ["Music", "Computer Science - Technology", "Music Composition"],
        "tags": ["High School", "Project Based Learning", "Technology", "Back to School"],
        "formats": ["PDF"],
        "pages": PDF_PAGES + SLIDES + 4,
        "answer_key": "Included",
        "zip_contents": [GUIDE_NAME] + [p for p, _ in sources()],
        "files": {"product": os.path.basename(ZIP), "preview": os.path.basename(PREVIEW_PDF), "thumb1": "cover.png",
                  "thumb2": "preview-1.png", "thumb3": "preview-2.png", "thumb4": "preview-3.png"},
    }


def make_zip():
    if os.path.exists(ZIP):
        os.remove(ZIP)
    with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED) as z:
        items = [(GUIDE_NAME, GUIDE)] + sources()
        for name, src in items:
            zi = zipfile.ZipInfo(f"{FOLDER}/{name}", date_time=(2026, 10, 23, 12, 0, 0))
            zi.compress_type = zipfile.ZIP_DEFLATED
            with open(src, "rb") as fh:
                z.writestr(zi, fh.read())


def kit_preview(unit):
    k = KITS[unit - 1]
    return os.path.join(TPT, k[1], f"{k[2]}-PREVIEW.pdf")


def build():
    from pypdf import PdfReader, PdfWriter
    os.makedirs(BUILD, exist_ok=True)
    guide = write("guide.html", html_doc([cover_page(), order_page(2), folder_page(3), terms_page(4)], TITLE + " Guide"))
    prev = write("guide-prev.html", html_doc([order_page(2, True), folder_page(3, True)], "Preview"))
    gp = os.path.join(BUILD, "guide-prev.pdf")
    render([{"html": guide, "pdf": GUIDE}, {"html": prev, "pdf": gp}])
    # 4-page preview PDF: 2 guide pages + 2 real, already-watermarked kit pages (Unit 2 p2, Unit 3 p3)
    w = PdfWriter()
    for p in PdfReader(gp).pages:
        w.add_page(p)
    for unit, pg in ((2, 1), (3, 2)):
        w.add_page(PdfReader(kit_preview(unit)).pages[pg])
    with open(PREVIEW_PDF, "wb") as f:
        w.write(f)
    make_zip()
    # images
    for k in KITS:
        pass
    pdf_png(GUIDE, 2, "g2", 100)
    pdf_png(GUIDE, 3, "g3", 100)
    shots = [(2, 1, "Unit 2 · Transitions"), (6, 1, "Unit 6 · Bus guide"), (3, 2, "Unit 3 · Reference card"),
             (1, 0, "Unit 1 · Pacing"), (4, 3, "Unit 4 · Rubric"), (5, 1, "Unit 5 · Song sheet")]
    imgs = []
    for u, pg, lab in shots:
        name = f"u{u}p{pg}"
        pdf_png(kit_preview(u), pg + 1, name, 70)
        imgs.append((f"{name}.png", lab))
    sq = [write("cover.html", cover_square()),
          write("p1.html", preview_1([os.path.join(TPT, k[1], "cover.png") for k in KITS])),
          write("p2.html", preview_2("g2.png", "g3.png")),
          write("p3.html", preview_3(imgs))]
    render([{"html": h, "png": o, "width": 1000, "height": 1000, "scale": 2} for h, o in zip(sq, [COVER_PNG] + PREVIEW_PNGS)])
    with open(os.path.join(HERE, "tpt.json"), "w") as f:
        json.dump(tpt_json(), f, indent=2, ensure_ascii=False)
        f.write("\n")
    print("built guide, preview PDF, ZIP, cover, 3 previews, tpt.json")


# ---------------------------------------------------------------- check
def pdf_text(p):
    return subprocess.run(["pdftotext", "-layout", p, "-"], capture_output=True, text=True).stdout


def check():
    from pypdf import PdfReader
    errs = []
    # 1. every kit file present in the ZIP and identical (hash) to its source; nothing else but the guide
    with zipfile.ZipFile(ZIP) as z:
        names = z.namelist()
        want = {f"{FOLDER}/{GUIDE_NAME}": sha(GUIDE)}
        for name, src in sources():
            want[f"{FOLDER}/{name}"] = sha(src)
        for n, h in want.items():
            if n not in names:
                errs.append(f"missing in ZIP: {n}")
            elif hashlib.sha256(z.read(n)).hexdigest() != h:
                errs.append(f"ZIP copy differs from source: {n}")
        extra = set(names) - set(want)
        if extra:
            errs.append(f"unexpected ZIP entries: {sorted(extra)}")
        if len(names) != 19:
            errs.append(f"ZIP has {len(names)} entries, expected 19 (guide + 6 x 3)")
    # 2. kit page and slide counts match this bundle's numbers (so the guide table is true)
    for k in KITS:
        base = os.path.join(TPT, k[1])
        n = len(PdfReader(os.path.join(base, f"{k[2]}.pdf")).pages)
        s = len(PdfReader(os.path.join(base, f"{k[2]}-intro-deck.pdf")).pages)
        if (n, s) != (k[6], k[7]):
            errs.append(f"{k[1]}: {n} pages / {s} slides, guide says {k[6]} / {k[7]}")
        kj = json.load(open(os.path.join(base, "tpt.json")))
        if int(float(kj["price"])) != k[4]:
            errs.append(f"{k[1]}: kit price {kj['price']} != {k[4]}")
    # 3. price arithmetic
    if PRICE_SUM != 63 or not (0.20 <= 1 - PRICE / PRICE_SUM <= 0.25):
        errs.append(f"bundle price {PRICE} is not 20-25% under {PRICE_SUM}")
    # 4. guide + preview
    gr = PdfReader(GUIDE)
    if len(gr.pages) != 4:
        errs.append("guide must be 4 pages")
    if len(PdfReader(PREVIEW_PDF).pages) != 4:
        errs.append("preview PDF must be 4 pages")
    for p in (GUIDE, PREVIEW_PDF):
        for pg in PdfReader(p).pages:
            if abs(float(pg.mediabox.width) - 612) > 2 or abs(float(pg.mediabox.height) - 792) > 2:
                errs.append(f"{os.path.basename(p)}: page not US Letter")
        fonts = subprocess.run(["pdffonts", p], capture_output=True, text=True).stdout.splitlines()[2:]
        for ln in fonts:
            if ln.split() and ("Oswald" not in ln and "SourceSans" not in ln.replace(" ", "") and "Source" not in ln):
                errs.append(f"{os.path.basename(p)}: unexpected font: {ln.strip()}")
            if ln.split() and " yes " not in ln.replace("  ", " ") and "yes" not in ln:
                errs.append(f"{os.path.basename(p)}: font not embedded: {ln.strip()}")
    txt = pdf_text(GUIDE)
    for k in KITS:
        if f"UNIT {k[0]} - {k[3]}".upper() not in " ".join(txt.split()).upper():
            errs.append(f"guide text lacks unit title {k[3]}")
    for b in BANNED:
        for p in (GUIDE, PREVIEW_PDF, os.path.join(HERE, "UPLOAD.md"), os.path.join(HERE, "tpt.json")):
            if os.path.exists(p) and b.lower() in (pdf_text(p) if p.endswith(".pdf") else open(p).read()).lower():
                errs.append(f"banned string {b!r} in {os.path.basename(p)}")
    # 5. images
    from PIL import Image
    for p in [COVER_PNG] + PREVIEW_PNGS:
        im = Image.open(p)
        if im.size != (2000, 2000):
            errs.append(f"{os.path.basename(p)} is {im.size}")
        if os.path.getsize(p) > 4 * 1024 * 1024:
            errs.append(f"{os.path.basename(p)} over TpT's 4 MB thumbnail limit")
    if os.path.getsize(PREVIEW_PDF) > 30 * 1024 * 1024:
        errs.append("preview PDF over 30 MB")
    # 6. tpt.json
    tj = json.load(open(os.path.join(HERE, "tpt.json")))
    for key in ("price", "license_price", "tax_code", "grades", "subjects", "tags", "files"):
        if key not in tj:
            errs.append(f"tpt.json lacks {key}")
    for f in tj["files"].values():
        if not os.path.exists(os.path.join(HERE, f)):
            errs.append(f"tpt.json file missing: {f}")
    # Subject Area is a closed list of 133 options (tpt/SUBJECT-OPTIONS.json); "Career and Technical Education" is NOT one of them
    try:
        opts = json.load(open(os.path.join(TPT, "SUBJECT-OPTIONS.json")))
        for s in tj.get("subjects", []):
            if s not in opts:
                errs.append(f"tpt.json subject {s!r} is not an option in tpt/SUBJECT-OPTIONS.json")
    except FileNotFoundError:
        pass
    if tj.get("subjects", [None])[0] != "Music":
        errs.append("tpt.json subjects must start with Music")
    if tj["price"] != f"{PRICE}.00":
        errs.append("tpt.json price differs from PRICE")
    # 7. the six kit folders are untouched in git
    st = subprocess.run(["git", "status", "--porcelain", "--"] + [os.path.join(TPT, k[1]) for k in KITS], capture_output=True, text=True, cwd=TPT).stdout
    if st.strip():
        errs.append("kit folders have uncommitted changes:\n" + st)
    if errs:
        print("CHECK FAILED")
        print("\n".join(" - " + e for e in errs))
        sys.exit(1)
    mb = os.path.getsize(ZIP) / 1048576
    print(f"CHECK OK: ZIP has 19 entries (guide + 6 units x PDF, deck .pptx, deck PDF), every kit file identical to its source by SHA-256; "
          f"kit page/slide counts and prices match the guide; ${PRICE} is {100 * (1 - PRICE / PRICE_SUM):.1f}% under the ${PRICE_SUM} sum; "
          f"guide 4 pages and preview 4 pages, Letter, fonts embedded; cover + 3 previews 2000x2000 under 4 MB; ZIP {mb:.1f} MB (TpT limit 4 GB); "
          f"no banned strings; tpt.json ok; kit folders unchanged.")


if __name__ == "__main__":
    if "--check" in sys.argv:
        check()
    else:
        build()
