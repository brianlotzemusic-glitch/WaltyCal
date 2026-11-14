#!/usr/bin/env python3
"""Nutcracker Listening Unit (TpT 034): build the resource and verify it.

    python3 gen.py            build everything (PDFs, PNGs, tpt.json) into this folder
    python3 gen.py --lowres   same, but square images at scale 1 (self-check only; --check rejects them)
    python3 gen.py --check    verify keys, quiz, spotting chart, pages, layout, fonts and files

A grades 2-6 listening unit for Tchaikovsky's ballet The Nutcracker (premiered 1892): the story in
six scenes, six movement listening maps with response pages (March, Waltz of the Snowflakes, Trepak,
Dance of the Reed Flutes, Waltz of the Flowers, Dance of the Sugar Plum Fairy), an instrument gallery
and spotting chart, a 16-point quiz and a computed answer key. No audio ships: the teacher plays a
recording of their choice. Structure copied from tpt/033's gen.py (no notation, so no Bravura).

Accuracy checks: every quiz question has exactly one correct option and the key text printed in the
PDF equals the data; the instrument spotting key is derived from the movement data and every
instrument has an icon and a family; story order and match keys are computed from the shuffled
cards; page cross-references exist; every page is scanned for text overflowing the page box.
Rendering uses Playwright + Chromium through ../tools/render.js, fonts from ../fonts.
"""
import importlib.util  # noqa: F401
import json
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

SLUG = "nutcracker-listening-unit"
PDF = os.path.join(HERE, f"{SLUG}.pdf")
PREVIEW_PDF = os.path.join(HERE, f"{SLUG}-PREVIEW.pdf")
COVER_PNG = os.path.join(HERE, "cover.png")
PREVIEW_PNGS = [os.path.join(HERE, f"preview-{i}.png") for i in (1, 2, 3)]
UPLOAD = os.path.join(HERE, "UPLOAD.md")
TPT_JSON = os.path.join(HERE, "tpt.json")

STORE = "Brian Lotze"
BRAND = "Hudson Beat"
YEAR = 2026
ACCENT = "#B3262E"            # Nutcracker red (single accent)
TINT1, TINT2 = "#D8767C", "#F0C4C7"
TITLE = "Nutcracker Listening Unit"
PRICE = "6.00"
DISCLOSURE = "Created with the help of digital and AI tools. Notation and answer keys are verified before release."
LOW_RES = "--lowres" in sys.argv

BANNED = ("rudolph", "frosty", "grinch", "santa", "jingle bell rock", "feliz navidad", "disney", "fantasia", "barbie",
          "youtube", "spotify", "checked by hand", "handmade", "classroom-tested", "hand-checked")

# ---------------------------------------------------------------- data
INSTR = {  # id: (name, family)
    "violin": ("Violin", "Strings"), "harp": ("Harp", "Strings"), "flute": ("Flute", "Woodwinds"),
    "bassclar": ("Bass clarinet", "Woodwinds"), "trumpet": ("Trumpet", "Brass"), "horn": ("French horn", "Brass"),
    "celesta": ("Celesta", "Keyboard percussion"), "voices": ("Children's voices", "Voices"),
}
INSTR_ORDER = ["violin", "harp", "flute", "bassclar", "trumpet", "horn", "celesta", "voices"]
INSTR_BLURB = {
    "violin": "Bowed strings. The violin section is the heart of the orchestra.",
    "harp": "Plucked strings. Sweeping glides are called glissandos.",
    "flute": "A high woodwind you blow across. Light and bird-like.",
    "bassclar": "A very low woodwind with a curved metal bell.",
    "trumpet": "Bright, bold brass. Often plays calls and fanfares.",
    "horn": "A round, warm brass sound from a coiled tube.",
    "celesta": "A keyboard that strikes metal bars. Sounds like tiny bells.",
    "voices": "Singers. In the ballet, children sing without words.",
}

MOVES = [  # in story order
    dict(k="march", n=1, title="March", sub="Act I · the party arrives", scene="Guests arrive at the party",
         facts=["Tchaikovsky wrote it for the guests arriving at the holiday party.",
                "It has a steady beat in groups of 4 (4/4), so you can march to it.",
                "Listen for bright trumpets and the string section."],
         inst=["trumpet", "violin"], meter="4/4", clue="Guests arrive at the party; bright trumpets and a steady 4-beat march",
         moods=["proud", "excited", "happy", "grand", "playful", "calm"]),
    dict(k="snow", n=2, title="Waltz of the Snowflakes", sub="End of Act I · the snowy forest", scene="Snowflakes dance in the forest",
         facts=["Clara and the Nutcracker Prince travel through a snowy forest where snowflakes dance.",
                "In the ballet, a chorus of children sings with no words, joining the orchestra.",
                "The music swirls and whirls like falling snow."],
         inst=["voices", "violin"], meter="", clue="Dancing snowflakes; children's voices (with no words) join the orchestra",
         moods=["peaceful", "magical", "icy", "excited", "sleepy", "thoughtful"]),
    dict(k="trepak", n=3, title="Trepak (Russian Dance)", sub="Act II · treats dance for Clara", scene="Treats from around the world dance",
         facts=["A trepak is a fast folk dance from Russia. Dancers leap and kick.",
                "It is in groups of 2 beats (2/4), like a gallop: ONE-two, ONE-two.",
                "It starts fast and keeps speeding up to a big finish."],
         inst=["violin"], meter="2/4", clue="A very fast Russian folk dance that keeps speeding up",
         moods=["excited", "playful", "wild", "proud", "happy", "calm"]),
    dict(k="reeds", n=4, title="Dance of the Reed Flutes", sub="Act II · treats dance for Clara", scene="Treats from around the world dance",
         facts=["Another dance for Clara in the Kingdom of Sweets. Its French name is Mirlitons.",
                "Three flutes play the light, sweet tune together.",
                "The short, light notes make it sound tiny and dainty."],
         inst=["flute"], meter="", clue="Three flutes play a light, dainty tune together",
         moods=["playful", "dainty", "happy", "calm", "cozy", "sleepy"]),
    dict(k="flowers", n=5, title="Waltz of the Flowers", sub="Act II · the flowers dance", scene="Flowers waltz in the Kingdom of Sweets",
         facts=["The flowers dance a grand waltz for Clara and the Prince.",
                "A harp plays a long, sweeping flourish before the waltz begins.",
                "A waltz has 3 beats in each group (3/4): ONE-two-three."],
         inst=["harp", "horn", "violin"], meter="3/4", clue="A waltz that opens with a harp flourish and feels like ONE-two-three",
         moods=["grand", "graceful", "happy", "excited", "peaceful", "proud"]),
    dict(k="sugar", n=6, title="Dance of the Sugar Plum Fairy", sub="Act II · the Fairy dances", scene="The Sugar Plum Fairy dances",
         facts=["The Sugar Plum Fairy rules the Kingdom of Sweets.",
                "Tchaikovsky heard a new instrument, the celesta, in Paris and wanted it for this dance.",
                "The celesta sparkles on top while a bass clarinet plays low and strings pluck."],
         inst=["celesta", "bassclar", "violin"], meter="", clue="The sparkling celesta plays the tune, like a music box",
         moods=["magical", "dainty", "peaceful", "sleepy", "thoughtful", "cozy"]),
]
MK = {m["k"]: m for m in MOVES}

# story events in correct order (sequencing page); shuffle order given as a fixed permutation (letters A-F)
EVENTS = [
    "At the Christmas Eve party, Clara's godfather Drosselmeyer gives her a nutcracker doll.",
    "At midnight the tree grows tall, and the Nutcracker leads the toy soldiers against the Mouse King and his mice.",
    "The Nutcracker becomes a prince and takes Clara through a snowy forest where snowflakes dance.",
    "They reach the Kingdom of Sweets, where the Sugar Plum Fairy welcomes them.",
    "Dances from around the world are performed for Clara, such as the Russian dance and the Reed Flutes.",
    "The flowers waltz, and the Sugar Plum Fairy and the Prince dance. Clara says goodbye.",
]
EVENT_PERM = [3, 0, 5, 2, 4, 1]       # card letter A-F shows EVENTS[EVENT_PERM[i]]
WHO = [  # (character, description), shuffled for display by WHO_PERM
    ("Clara", "The girl who receives the nutcracker and travels with it."),
    ("Drosselmeyer", "The godfather who makes and brings the nutcracker."),
    ("Mouse King", "The leader of the mice who attack at midnight."),
    ("Sugar Plum Fairy", "The ruler of the Kingdom of Sweets."),
]
WHO_PERM = [2, 0, 3, 1]

QUIZ_A = [(m["k"], m["clue"]) for m in MOVES]       # match movement number to clue
QUIZ_A_PERM = [4, 2, 0, 5, 1, 3]                    # row i shows clue of movement QUIZ_A_PERM[i]
QUIZ_B = [  # (question, [A, B, C], correct index)
    ("Who composed The Nutcracker?", ["Mozart", "Tchaikovsky", "Beethoven"], 1),
    ("The ballet was first performed in the year", ["1792", "1992", "1892"], 2),
    ("Which instrument plays the tune in the Dance of the Sugar Plum Fairy?", ["Celesta", "Trumpet", "Trombone"], 0),
    ("How many beats are in each group of a waltz?", ["2", "4", "3"], 2),
    ("Which dance speeds up as it goes on?", ["Waltz of the Flowers", "Trepak", "Dance of the Sugar Plum Fairy"], 1),
    ("The flute belongs to which instrument family?", ["Brass", "Strings", "Woodwinds"], 2),
]
QUIZ_C = [  # (statement, True/False)
    ("The Nutcracker is a ballet that tells its story with music and dance.", True),
    ("The harp is a brass instrument.", False),
    ("The Trepak is a slow, quiet dance.", False),
    ("Tchaikovsky was a composer from Russia.", True),
]
QUIZ_TOTAL = len(QUIZ_A) + len(QUIZ_B) + len(QUIZ_C)

TEMPOS = [("SLOW", "adagio"), ("MEDIUM", "moderato"), ("FAST", "allegro")]

# ---------------------------------------------------------------- pages
PLAN = ["cover", "teacher", "story", "story_q", "toolkit",
        "m_march", "m_snow", "m_trepak", "m_reeds", "m_flowers", "m_sugar",
        "gallery", "spot", "quiz", "key", "review", "terms"]
IX = {k: i + 1 for i, k in enumerate(PLAN)}


def pg(k):
    return f"page {IX[k]}"


# ---------------------------------------------------------------- derived keys
def spot_key():
    return {m["k"]: sorted(m["inst"], key=INSTR_ORDER.index) for m in MOVES}


def event_cards():
    return [("ABCDEF"[i], EVENTS[j]) for i, j in enumerate(EVENT_PERM)]


def event_key():
    """Card letters in story order: the answer to 'put the cards in order 1-6'."""
    out = []
    for story_pos in range(len(EVENTS)):
        out.append("ABCDEF"[EVENT_PERM.index(story_pos)])
    return out


def who_cards():
    return [(WHO[j][1], "ABCD"[i]) for i, j in enumerate(WHO_PERM)]   # shown description with letter


def who_key():
    # for each character in listed order (not shuffled), the letter of its description
    return [(c, "ABCD"[WHO_PERM.index(i)]) for i, (c, _) in enumerate(WHO)]


def quiz_a_rows():
    return [(i + 1, MOVES[j]["clue"], j + 1) for i, j in enumerate(QUIZ_A_PERM)]   # row no, clue, movement number


def quiz_key():
    return {"A": [(r, mv) for r, _, mv in quiz_a_rows()],
            "B": ["ABC"[c] for _, _, c in QUIZ_B],
            "C": ["TRUE" if t else "FALSE" for _, t in QUIZ_C]}


# ---------------------------------------------------------------- fonts and css
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
.top .t { font-size: 23pt; }
.top .t small { display: block; font-family: 'Oswald'; font-weight: 300; text-transform: none; font-size: 12pt; letter-spacing: 0; margin-top: 4pt; }
.tag { text-align: right; flex: 0 0 auto; margin-left: 10pt; }
.tag .lv { display: inline-block; background: #000; color: #fff; font-family: 'Oswald'; font-weight: 700; font-size: 15pt; padding: 3pt 9pt 4pt; border-radius: 4pt; letter-spacing: .04em; }
.tag .lv.ak { background: ACCENT; }
.tag .ln { font-family: 'Oswald'; font-weight: 300; font-size: 11pt; margin-top: 3pt; }
.name { display: flex; gap: 18pt; font-size: 12pt; margin: 9pt 0 5pt; }
.name span { flex: 1; border-bottom: 1pt solid #000; height: 15pt; }
.name span.d { flex: 0 0 1.6in; }
.how { font-size: 11.5pt; margin: 7pt 0 6pt; }
.main { flex: 1; display: flex; flex-direction: column; min-height: 0; }
.foot { display: flex; justify-content: space-between; font-size: 8.5pt; color: #333; border-top: .8pt solid #000; padding-top: 3pt; }
.wm { position: absolute; left: 50%; top: 50%; transform: translate(-50%, -50%) rotate(-38deg); font-family: 'Oswald'; font-weight: 700;
      font-size: 150pt; color: rgba(0,0,0,.13); letter-spacing: .06em; white-space: nowrap; pointer-events: none; z-index: 9; }
.doc h1 { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 30pt; margin: 0 0 4pt; line-height: 1; }
.doc h2, .sec { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 13.5pt; margin: 10pt 0 4pt; letter-spacing: .02em; }
.doc p, .doc li { font-size: 10.6pt; line-height: 1.32; margin: 0 0 4pt; }
.doc ul, .doc ol { margin: 0 0 4pt; padding-left: 15pt; }
.tn p, .tn li { font-size: 10pt !important; line-height: 1.28 !important; margin-bottom: 3pt !important; }
.tn h2 { margin: 8pt 0 3pt !important; font-size: 12.5pt !important; }
.tn table.t { font-size: 9pt; }
.kp table.t { font-size: 10.6pt; }
.kp .small { font-size: 10pt !important; }
.tn table.t td { padding: 2pt 4pt; }
.doc .rule { border-bottom: 2.2pt solid #000; margin-bottom: 6pt; padding-bottom: 6pt; }
table.t { border-collapse: collapse; width: 100%; font-size: 10pt; margin: 2pt 0 4pt; }
table.t td, table.t th { border: 1pt solid #000; padding: 2.6pt 5pt; text-align: left; vertical-align: middle; }
table.t th { font-family: 'Oswald'; font-weight: 500; text-transform: uppercase; font-size: 9.5pt; background: #000; color: #fff; letter-spacing: .04em; }
.cols { display: flex; gap: 22pt; }
.cols > div { flex: 1; min-width: 0; }
.small { font-size: 9pt !important; color: #333; }
.box { border: 1.4pt solid #000; border-radius: 8pt; padding: 7pt 10pt; }
.part { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 13pt; letter-spacing: .03em; margin: 9pt 0 4pt; }
.part .acc { color: ACCENT; }
.part small { font-family: 'Source Sans 3'; font-weight: 400; text-transform: none; font-size: 10.5pt; letter-spacing: 0; margin-left: 6pt; }
.ln2 { border-bottom: 1pt solid #000; height: 21pt; }
.lines { flex: 1; min-height: 40pt; background-image: repeating-linear-gradient(to bottom, transparent 0, transparent 25pt, #000 25pt, #000 26pt); }
.ans { font-family: 'Oswald'; font-weight: 700; color: ACCENT; }
.circ { display: inline-block; font-family: 'Oswald'; font-weight: 500; letter-spacing: .05em; padding: 0 7pt; border: 1.3pt solid #000; border-radius: 10pt; margin: 0 3pt 3pt 0; font-size: 10.5pt; line-height: 1.5; }
.circ.on { border-color: ACCENT; color: ACCENT; font-weight: 700; }
.bul { margin: 0; padding-left: 14pt; }
.bul li { font-size: 11.5pt; line-height: 1.3; margin: 0 0 3pt; }
.cover { align-items: center; justify-content: space-between; padding: 0.55in 0.6in 0.5in; }
.store { font-family: 'Oswald'; font-weight: 500; font-size: 13pt; letter-spacing: .32em; text-transform: uppercase; }
.ctitle { text-align: center; }
.ctitle .a { font-family: 'Oswald'; font-weight: 700; font-size: 44pt; line-height: 1; letter-spacing: .02em; }
.ctitle .b { white-space: nowrap; font-family: 'Oswald'; font-weight: 700; font-size: 64pt; line-height: .95; letter-spacing: .01em; }
.ctitle .c { font-family: 'Oswald'; font-weight: 300; font-size: 16pt; margin-top: 8pt; }
.cband { width: 100%; background: #000; color: #fff; text-align: center; font-family: 'Oswald'; font-weight: 500; font-size: 14pt;
         letter-spacing: .08em; text-transform: uppercase; padding: 8pt 0 9pt; border-radius: 4pt; }
.cband em { font-style: normal; color: ACCENT; }
.card { border: 1.4pt solid #000; border-radius: 8pt; padding: 6pt 9pt; font-size: 11pt; line-height: 1.3; }
.card b.k { font-family: 'Oswald'; font-weight: 700; color: ACCENT; margin-right: 4pt; }
.wl { display: inline-block; width: 40pt; border-bottom: 1pt solid #000; height: 13pt; vertical-align: bottom; margin: 0 3pt; }
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


def text(x, y, s, size, weight=700, family="Oswald", anchor="middle", fill="#000", extra=""):
    family = f"'{family}'" if " " in family else family
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{family}" font-weight="{weight}" font-size="{size}" '
            f'text-anchor="{anchor}" fill="{fill}" {extra}>{escape(s)}</text>')


def page(sub, tag, tagsub, inner, n, watermark=False, name=False, ak=False, right=None, title=TITLE):
    r = f"Page {n}" if right is None else f"{right} · Page {n}"
    return (f'<section class="page">{wm(watermark)}{top(sub, tag, tagsub, ak=ak, title=title)}{NAME if name else ""}'
            f'<div class="main">{inner}</div>{foot(r)}</section>')


def circ(word, on=False):
    return f'<span class="circ{" on" if on else ""}">{word}</span>'


def fill_pages(s):
    return re.sub(r"PG:(\w+)", lambda m: pg(m.group(1)), s)


# ---------------------------------------------------------------- instrument icons (100 x 100 viewBox, line art)
S = 'fill="none" stroke="#000" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"'


def icon_body(i):
    A = ACCENT
    if i == "violin":
        return (f'<path d="M50 34 C36 34 34 44 42 50 C32 54 30 70 40 78 C46 84 54 84 60 78 C70 70 68 54 58 50 C66 44 64 34 50 34 Z" fill="{TINT2}" stroke="#000" stroke-width="2.6" stroke-linejoin="round"/>'
                f'<path d="M50 34 L50 12" {S}/><circle cx="50" cy="9" r="4.5" fill="#fff" stroke="#000" stroke-width="2.4"/>'
                f'<path d="M44 64 Q50 60 56 64 M46 72 L54 72" {S}/><path d="M50 40 L50 76" stroke="{A}" stroke-width="1.6" fill="none"/>'
                f'<path d="M20 90 L84 22" {S} stroke-width="2"/>')
    if i == "harp":
        return (f'<path d="M30 88 L30 30 C30 14 56 10 70 22 C76 28 76 36 70 42 L44 86 Z" fill="{TINT2}" stroke="#000" stroke-width="2.6" stroke-linejoin="round"/>'
                f'<path d="M30 88 L50 88 M30 80 L46 80" {S}/>'
                + "".join(f'<path d="M{34 + k * 5} {88 - k * 7} L{34 + k * 5} {26 + k * 4}" stroke="{A}" stroke-width="1.5"/>' for k in range(1, 8)))
    if i == "flute":
        return (f'<path d="M10 76 L90 24" stroke="#000" stroke-width="9" stroke-linecap="round" fill="none"/>'
                f'<path d="M10 76 L90 24" stroke="#fff" stroke-width="5" stroke-linecap="round" fill="none"/>'
                + "".join(f'<circle cx="{30 + k * 13}" cy="{63 - k * 8.1}" r="3.4" fill="{A}" stroke="#000" stroke-width="1.6"/>' for k in range(4))
                + f'<circle cx="19" cy="70" r="2.4" fill="#000"/>')
    if i == "bassclar":
        return (f'<path d="M62 8 Q74 8 74 18 L50 22" {S}/><path d="M50 22 L50 78" stroke="#000" stroke-width="11" stroke-linecap="round" fill="none"/>'
                f'<path d="M50 22 L50 78" stroke="#fff" stroke-width="6.5" stroke-linecap="round" fill="none"/>'
                f'<path d="M45 80 C40 92 62 96 66 82 L68 74" {S} stroke-width="3"/>'
                + "".join(f'<circle cx="50" cy="{30 + k * 10}" r="2.8" fill="{A}" stroke="#000" stroke-width="1.5"/>' for k in range(5)))
    if i == "trumpet":
        return (f'<path d="M10 52 L56 52 C74 52 74 70 56 70 L26 70 C14 70 14 52 26 52 M56 52 L82 40 L88 40 L88 82 L82 82 L56 70" fill="#fff" stroke="#000" stroke-width="2.6" stroke-linejoin="round"/>'
                f'<path d="M88 40 C95 52 95 70 88 82" fill="{TINT2}" stroke="#000" stroke-width="2.6"/>'
                f'<path d="M34 52 L34 40 M42 52 L42 38 M50 52 L50 40" {S}/><circle cx="34" cy="37" r="3.4" fill="{A}" stroke="#000" stroke-width="1.6"/>'
                f'<circle cx="42" cy="35" r="3.4" fill="{A}" stroke="#000" stroke-width="1.6"/><circle cx="50" cy="37" r="3.4" fill="{A}" stroke="#000" stroke-width="1.6"/>')
    if i == "horn":
        return (f'<circle cx="46" cy="52" r="32" fill="#fff" stroke="#000" stroke-width="2.6"/><circle cx="46" cy="52" r="21" {S}/>'
                f'<circle cx="46" cy="52" r="10" {S}/>'
                f'<path d="M72 36 C84 20 94 18 96 6 C86 4 80 12 70 28 M18 40 L8 30 L20 24" fill="{TINT2}" stroke="#000" stroke-width="2.6" stroke-linejoin="round"/>'
                f'<circle cx="46" cy="52" r="4" fill="{A}"/>')
    if i == "celesta":
        keys = "".join(f'<rect x="{18 + k * 9}" y="50" width="9" height="24" fill="#fff" stroke="#000" stroke-width="1.6"/>' for k in range(8))
        blk = "".join(f'<rect x="{18 + k * 9 + 6.5}" y="50" width="5" height="14" fill="#000"/>' for k in (0, 1, 3, 4, 5))
        return (f'<rect x="12" y="24" width="76" height="26" rx="3" fill="{TINT2}" stroke="#000" stroke-width="2.6"/>'
                f'<rect x="12" y="50" width="76" height="26" rx="2" fill="#fff" stroke="#000" stroke-width="2.6"/>{keys}{blk}'
                f'<path d="M20 30 L80 30 M20 37 L80 37 M20 44 L80 44" stroke="{A}" stroke-width="1.6"/>'
                f'<path d="M18 76 L18 92 M82 76 L82 92" {S}/>')
    if i == "voices":
        return (f'<circle cx="38" cy="50" r="26" fill="#fff" stroke="#000" stroke-width="2.6"/>'
                f'<circle cx="28" cy="42" r="3.2" fill="#000"/><circle cx="48" cy="42" r="3.2" fill="#000"/>'
                f'<ellipse cx="38" cy="62" rx="8" ry="9" fill="{A}" stroke="#000" stroke-width="2.2"/>'
                f'<path d="M72 28 L72 56" {S}/><ellipse cx="66" cy="58" rx="7" ry="5" fill="#000"/>'
                f'<path d="M72 28 Q82 30 82 40" {S}/><path d="M82 70 L82 84" {S}/><ellipse cx="77" cy="86" rx="6" ry="4.4" fill="#000"/>')
    raise KeyError(i)


def icon(i, w=64):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="{w}pt" height="{w}pt" style="display:block">{icon_body(i)}</svg>'


# ---------------------------------------------------------------- listening maps (505pt wide)
MW = 505


def bx(x, y, w, h, fill="#fff", sw=1.6, rx=6):
    return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{fill}" stroke="#000" stroke-width="{sw}"/>'


def map_march():
    o = [f'<path d="M20 62 Q130 20 250 62 T485 62" fill="none" stroke="{ACCENT}" stroke-width="2" stroke-dasharray="3 6" stroke-linecap="round"/>']
    for k in range(8):
        x = 12 + k * 61
        y = 38 if k % 2 == 0 else 52
        o.append(f'<ellipse cx="{x + 24}" cy="{y}" rx="6.5" ry="9" fill="#000" transform="rotate(-10 {x + 24} {y})"/>')
        o.append(f'<ellipse cx="{x + 38}" cy="{y + 10}" rx="6.5" ry="9" fill="#000" transform="rotate(-10 {x + 38} {y + 10})"/>')
        o.append(bx(x, 80, 54, 80))
        o.append(text(x + 27, 97, str(k + 1), 13))
        o.append(text(x + 27, 124, "LOUD", 9.5, 500))
        o.append(f'<ellipse cx="{x + 27}" cy="121" rx="21" ry="9.5" fill="none" stroke="#000" stroke-width="1.2"/>')
        o.append(f'<ellipse cx="{x + 27}" cy="145" rx="21" ry="9.5" fill="none" stroke="#000" stroke-width="1.2"/>')
        o.append(text(x + 27, 148.5, "SOFT", 9.5, 500))
    return svg(MW, 170, "".join(o))


def snowflake(cx, cy, r, sw=2):
    o = []
    import math
    for a in range(0, 180, 60):
        dx, dy = math.cos(math.radians(a)) * r, math.sin(math.radians(a)) * r
        o.append(f'<path d="M{cx - dx:.1f} {cy - dy:.1f} L{cx + dx:.1f} {cy + dy:.1f}" stroke="#000" stroke-width="{sw}" stroke-linecap="round"/>')
    for a in range(0, 360, 60):
        ex, ey = cx + math.cos(math.radians(a)) * r * .62, cy + math.sin(math.radians(a)) * r * .62
        for da in (-45, 45):
            bx_, by_ = ex + math.cos(math.radians(a + da)) * r * .3, ey + math.sin(math.radians(a + da)) * r * .3
            o.append(f'<path d="M{ex:.1f} {ey:.1f} L{bx_:.1f} {by_:.1f}" stroke="#000" stroke-width="{sw * .8:.1f}" stroke-linecap="round"/>')
    return "".join(o)


def map_snow():
    import math
    o = [f'<path d="M14 40 C90 -10 150 100 250 50 S420 0 492 60" fill="none" stroke="{TINT1}" stroke-width="2.2" stroke-dasharray="2 7" stroke-linecap="round"/>']
    for k in range(8):
        cx = 36 + k * 62
        cy = 52 + 22 * math.sin(k * 0.9)
        o.append(snowflake(cx, cy, 20))
        o.append(f'<circle cx="{cx}" cy="{cy}" r="4.5" fill="{ACCENT}" stroke="#000" stroke-width="1.2"/>')
        o.append(text(cx, 106, str(k + 1), 12))
        o.append(bx(cx - 22, 112, 44, 40))
        o.append(text(cx, 146, "voices?", 8.5, 500, fill="#555"))
    return svg(MW, 160, "".join(o))


def gauge(cx, cy, label):
    import math
    o = [f'<path d="M{cx - 62} {cy} A62 62 0 0 1 {cx + 62} {cy}" fill="none" stroke="#000" stroke-width="2.4"/>',
         f'<path d="M{cx - 62} {cy} L{cx + 62} {cy}" stroke="#000" stroke-width="2.4"/>']
    for k in range(9):
        a = math.radians(180 - k * 22.5)
        x1, y1 = cx + math.cos(a) * 54, cy - math.sin(a) * 54
        x2, y2 = cx + math.cos(a) * 62, cy - math.sin(a) * 62
        o.append(f'<path d="M{x1:.1f} {y1:.1f} L{x2:.1f} {y2:.1f}" stroke="#000" stroke-width="2"/>')
    o.append(f'<circle cx="{cx}" cy="{cy}" r="5" fill="{ACCENT}" stroke="#000" stroke-width="1.5"/>')
    o.append(text(cx - 56, cy + 15, "SLOW", 10, 500))
    o.append(text(cx + 56, cy + 15, "FAST", 10, 500))
    o.append(text(cx, cy + 36, label, 13))
    return "".join(o)


def map_trepak():
    return svg(MW, 118, gauge(86, 70, "START") + gauge(252, 70, "MIDDLE") + gauge(418, 70, "END"))


def map_reeds():
    o = []
    for k in range(8):
        x = 12 + k * 61
        o.append(bx(x, 6, 54, 112))
        o.append(text(x + 27, 24, str(k + 1), 13))
        o.append(f'<circle cx="{x + 15}" cy="48" r="4.6" fill="#000"/>')
        o.append(text(x + 38, 52, "short", 10, 500))
        o.append(f'<ellipse cx="{x + 27}" cy="48" rx="25" ry="12" fill="none" stroke="#000" stroke-width="1.2"/>')
        o.append(f'<path d="M{x + 7} 88 Q{x + 17} 76 {x + 27} 88 T{x + 47} 88" fill="none" stroke="#000" stroke-width="2.2" stroke-linecap="round"/>')
        o.append(text(x + 27, 108, "smooth", 10, 500))
        o.append(f'<ellipse cx="{x + 27}" cy="89" rx="25" ry="15" fill="none" stroke="#000" stroke-width="1.2"/>')
    return svg(MW, 124, "".join(o))


def map_flowers():
    o = []
    for r in range(2):
        for k in range(4):
            x0 = 14 + k * 121
            y0 = 8 + r * 80
            o.append(bx(x0, y0, 112, 70, rx=10))
            o.append(f'<circle cx="{x0 + 26}" cy="{y0 + 35}" r="17" fill="{TINT2}" stroke="#000" stroke-width="1.8"/>')
            o.append(f'<circle cx="{x0 + 62}" cy="{y0 + 40}" r="10" fill="#fff" stroke="#000" stroke-width="1.8"/>')
            o.append(f'<circle cx="{x0 + 90}" cy="{y0 + 40}" r="10" fill="#fff" stroke="#000" stroke-width="1.8"/>')
            o.append(text(x0 + 26, y0 + 40, "1", 14, fill=ACCENT))
            o.append(text(x0 + 62, y0 + 44, "2", 11, 500))
            o.append(text(x0 + 90, y0 + 44, "3", 11, 500))
            o.append(text(x0 + 9, y0 + 14, str(r * 4 + k + 1), 10, 500, anchor="start", fill="#555"))
    return svg(MW, 164, "".join(o))


def map_sugar():
    o = [text(14, 24, "HIGH", 10.5, 500, anchor="start"), text(14, 140, "LOW", 10.5, 500, anchor="start")]
    x0, x1, y0, y1 = 56, 495, 10, 148
    for r in range(5):
        y = y0 + r * (y1 - y0) / 4
        o.append(f'<path d="M{x0} {y:.1f} L{x1} {y:.1f}" stroke="#000" stroke-width="1" stroke-dasharray="1 4"/>')
    for k in range(9):
        x = x0 + k * (x1 - x0) / 8
        o.append(f'<path d="M{x:.1f} {y0} L{x:.1f} {y1}" stroke="#bbb" stroke-width="1"/>')
    o.append(f'<path d="M{x0} {y1} L{x1} {y1} M{x0} {y0} L{x0} {y1}" stroke="#000" stroke-width="2"/>')
    for k in range(8):
        o.append(text(x0 + (k + .5) * (x1 - x0) / 8, 162, str(k + 1), 10, 500, fill="#555"))
    for sx, sy in ((90, 22), (440, 28)):
        o.append(f'<path d="M{sx} {sy - 8} L{sx + 2.4} {sy - 2.4} L{sx + 8} {sy} L{sx + 2.4} {sy + 2.4} L{sx} {sy + 8} L{sx - 2.4} {sy + 2.4} L{sx - 8} {sy} L{sx - 2.4} {sy - 2.4} Z" fill="{ACCENT}"/>')
    return svg(MW, 168, "".join(o))


MAPS = {"march": map_march, "snow": map_snow, "trepak": map_trepak, "reeds": map_reeds, "flowers": map_flowers, "sugar": map_sugar}
MAP_TASK = {
    "march": ("March map", "Step along the path. In each box circle <b>LOUD</b> or <b>SOFT</b> for what you hear in that part."),
    "snow": ("Snowflake path", "Follow the dotted path from flake to flake. Write a <b>V</b> in the box when you hear voices."),
    "trepak": ("Speed gauges", "Draw the needle where the speed is at the <b>start</b>, the <b>middle</b> and the <b>end</b>."),
    "reeds": ("Short or smooth?", "In each box circle <b>short</b> (dots) or <b>smooth</b> (a wavy line). How many flutes? <span class='wl'></span>"),
    "flowers": ("Waltz groups", "First, wiggle a line up when the <b>harp</b> plays. Then tap <b>1</b>-2-3 in each flower group. Put a star where the tune begins."),
    "sugar": ("Tune shape", "Draw the tune as a line: up when the notes go higher, down when lower. Put an <b>S</b> by the sparkly sound and an <b>L</b> by a low sound."),
}
MAP_CUE = "Teacher: say “next” about every 15 seconds (stop at box 8, or start over if the music is longer)."


def mood_row(words):
    return " ".join(circ(w.upper()) for w in words)


def move_page(k, n, watermark=False):
    m = MK[k]
    mt, mtask = MAP_TASK[k]
    facts = "".join(f"<li>{escape(f)}</li>" for f in m["facts"])
    icons = "".join(f'<div style="text-align:center;width:56pt">{icon(i, 44)}<div class="small" style="font-size:8pt!important;margin-top:1pt">{INSTR[i][0]}</div></div>' for i in m["inst"])
    tempo = "".join(circ(f"{a} · {b}") for a, b in TEMPOS)
    dyn = "".join(circ(x) for x in ("LOUD", "SOFT", "GETS LOUDER", "GETS SOFTER", "BOTH"))
    inst_row = "".join(circ(INSTR[i][0].upper()) for i in INSTR_ORDER)
    inner = (f'<div class="box" style="display:flex;gap:10pt;align-items:center;margin-top:8pt">'
             f'<div style="flex:1"><div class="part" style="margin:0 0 3pt;font-size:11.5pt">About this music</div><ul class="bul">{facts}</ul></div>'
             f'<div style="display:flex;gap:2pt">{icons}</div></div>'
             f'<div class="part">Listening map<span class="acc"> ·</span><small>{mtask}</small></div>'
             f'<div style="margin:0 auto">{MAPS[k]()}</div>'
             f'<div class="small" style="margin:2pt 0 0;text-align:center">{MAP_CUE}</div>'
             f'<div class="part" style="margin-top:7pt">Circle what you hear</div>'
             f'<div style="font-size:11.5pt;margin-bottom:3pt"><b>Tempo</b> &nbsp;{tempo}</div>'
             f'<div style="font-size:11.5pt;margin-bottom:3pt"><b>Dynamics</b> &nbsp;{dyn}</div>'
             f'<div style="font-size:11.5pt;margin-bottom:3pt"><b>Mood</b> &nbsp;{mood_row(m["moods"])}</div>'
             f'<div style="font-size:11.5pt"><b>Sounds</b> &nbsp;{inst_row}</div>'
             f'<div class="part" style="margin-top:6pt">Tell about it<span class="acc"> ·</span></div>'
             f'<div style="font-size:10.5pt;margin-bottom:1pt"><b>Grades 2–3:</b> “This music sounds like ______ because ______.”  &nbsp;<b>Grades 4–6:</b> write 3 sentences using music words '
             f'(tempo, dynamics, instruments, mood).</div>'
             f'<div class="lines"></div>')
    return page(f"{m['sub']} · movement {m['n']} of 6", f"MOVEMENT {m['n']}", "Listening map", inner, n, watermark,
                name=True, title=m["title"])


# ---------------------------------------------------------------- other student/teacher pages
def story_page(n, watermark=False):
    scenes = [
        ("Act I", "The party", "On Christmas Eve, Clara and her brother Fritz welcome guests. Her godfather Drosselmeyer, a toymaker, brings gifts, including a nutcracker doll shaped like a soldier. <b>(Movement 1, March)</b>"),
        ("Act I", "Midnight", "Fritz breaks the nutcracker, and Clara tucks it in. At midnight the Christmas tree grows tall and mice creep in. The Nutcracker leads the toy soldiers against the Mouse King. Clara throws her slipper, and the Nutcracker wins and turns into a prince."),
        ("Act I", "The snowy forest", "The Prince takes Clara through a forest where snowflakes dance. <b>(Movement 2, Waltz of the Snowflakes)</b>"),
        ("Act II", "The Kingdom of Sweets", "They arrive in a land of sweets ruled by the Sugar Plum Fairy. She welcomes them and orders dances to be shown for Clara. <b>(Movement 3, Trepak; Movement 4, Reed Flutes)</b>"),
        ("Act II", "The flowers and the Fairy", "The flowers dance a waltz. The Sugar Plum Fairy and the Prince dance. <b>(Movement 5, Waltz of the Flowers; Movement 6, Dance of the Sugar Plum Fairy)</b>"),
        ("Act II", "Goodbye", "Clara says goodbye to her new friends. In many versions she wakes up at home, wondering if it was a dream."),
    ]
    rows = "".join(
        f'<div style="display:flex;gap:9pt;margin:0 0 11pt"><div style="flex:0 0 22pt;height:22pt;border-radius:50%;background:#000;color:#fff;font-family:Oswald;'
        f'font-weight:700;font-size:12pt;text-align:center;line-height:22pt">{i + 1}</div>'
        f'<div style="font-size:11.8pt;line-height:1.34"><b style="font-family:Oswald;text-transform:uppercase;letter-spacing:.02em;color:{ACCENT}">{a} · {t}</b><br>{d}</div></div>'
        for i, (a, t, d) in enumerate(scenes))
    inner = (f'<div class="cols" style="gap:14pt;margin-top:8pt"><div style="flex:0 0 190pt">'
             f'<div class="card" style="font-size:11.8pt"><b class="k">The composer</b>Pyotr Ilyich Tchaikovsky (1840–1893) was a Russian composer. He also wrote the ballets <i>Swan Lake</i> and <i>The Sleeping Beauty</i>.</div>'
             f'<div class="card" style="margin-top:8pt;font-size:11.8pt"><b class="k">The ballet</b>The Nutcracker was first performed on December 18, 1892, at the Mariinsky Theatre in St. Petersburg, Russia. '
             f'The choreography was by Lev Ivanov, from plans by Marius Petipa.</div>'
             f'<div class="card" style="margin-top:8pt;font-size:11.8pt"><b class="k">The story</b>It comes from a tale by E. T. A. Hoffmann (1816), retold by Alexandre Dumas in 1844.</div>'
             f'<div class="card" style="margin-top:8pt;font-size:11.8pt"><b class="k">A ballet</b>A ballet tells a story with dance and music, but no talking. The orchestra plays all the music. '
             f'Tchaikovsky also made a concert suite of eight pieces from it that is played without dancers.</div>'
             f'<div class="card" style="margin-top:8pt;font-size:11.8pt"><b class="k">Hearing it</b>You will hear six pieces (movements). Each one matches a part of the story.</div>'
             f'</div><div style="flex:1;min-width:0">{rows}'
             f'<div class="small" style="margin-top:4pt">Every company tells the story a little differently: names, scenes and endings change from one production to the next. This is one common version.</div>'
             f'</div></div>')
    return page("Meet the ballet · the story in six scenes", "READ", "Story summary", inner, n, watermark, title="The Nutcracker Story")


def storyq_page(n, watermark=False):
    cards = "".join(f'<div class="card" style="display:flex;gap:8pt;margin:0 0 5pt;align-items:center"><b class="k" style="font-size:15pt;flex:0 0 14pt">{l}</b>'
                    f'<span style="flex:1">{escape(t)}</span><span style="flex:0 0 26pt;height:22pt;border:1.4pt solid #000;border-radius:5pt"></span></div>'
                    for l, t in event_cards())
    wc = "".join(f'<div class="card" style="margin:0 0 5pt"><b class="k">{l}</b>{escape(d)}</div>' for d, l in who_cards())
    chars = "".join(f'<div style="display:flex;gap:6pt;align-items:flex-end;margin:0 0 7pt;font-size:11.5pt"><b style="white-space:nowrap">{c}</b>'
                    f'<span style="flex:0 0 40pt;border-bottom:1pt solid #000;height:15pt"></span></div>' for c, _ in WHO)
    inner = (f'<div class="how">Use the story on {pg("story")} to help you.</div>'
             f'<div class="part" style="margin-top:2pt">A · Put the story in order<small>Write 1 to 6 in the box (1 is first).</small></div>{cards}'
             f'<div class="part">B · Who is who?<small>Write the letter of the matching description.</small></div>'
             f'<div class="cols" style="gap:16pt"><div>{chars}</div><div>{wc}</div></div>'
             f'<div class="part" style="margin-top:2pt">C · Draw and tell<small>Draw your favorite scene and write one sentence about it.</small></div>'
             f'<div class="box" style="height:118pt"></div><div class="ln2"></div>')
    return page("Story check", "STORY", "Show what you know", inner, n, watermark, name=True, right=f"Answer key on page {IX['key']}", title="Nutcracker Story Check")


def toolkit_page(n, watermark=False):
    inner = (f'<div class="how">These are the words you will use to describe music. Keep this page next to you while you listen.</div>'
             f'<table class="t"><tr><th style="width:20%">Word</th><th>What it means</th><th style="width:30%">Try saying it</th></tr>'
             f'<tr><td><b>Tempo</b></td><td>How fast or slow the beat is. <i>adagio</i> = slow, <i>moderato</i> = medium, <i>allegro</i> = fast.</td><td>“The tempo is fast.”</td></tr>'
             f'<tr><td><b>Dynamics</b></td><td>How loud or soft. <i>piano</i> (p) = soft, <i>forte</i> (f) = loud. <i>Crescendo</i> = gets louder, <i>decrescendo</i> = gets softer.</td><td>“It starts soft and gets louder.”</td></tr>'
             f'<tr><td><b>Beat</b></td><td>The steady pulse you can tap.</td><td>“I can tap the beat.”</td></tr>'
             f'<tr><td><b>Meter</b></td><td>How the beats group: in 2s (march or gallop), in 3s (waltz) or in 4s.</td><td>“It feels like ONE-two-three.”</td></tr>'
             f'<tr><td><b>Pitch</b></td><td>How high or low a sound is.</td><td>“The tune goes up high.”</td></tr>'
             f'<tr><td><b>Timbre</b></td><td>The color of a sound: which instrument or voice you hear.</td><td>“It sounds like tiny bells.”</td></tr>'
             f'<tr><td><b>Mood</b></td><td>The feeling the music gives you.</td><td>“It sounds magical.”</td></tr></table>'
             f'<div class="part">The four families of the orchestra</div>'
             f'<table class="t"><tr><th>Family</th><th>How the sound is made</th><th>Examples in this unit</th></tr>'
             f'<tr><td><b>Strings</b></td><td>Bowed or plucked strings</td><td>violin, harp</td></tr>'
             f'<tr><td><b>Woodwinds</b></td><td>Blowing air across or through a pipe or reed</td><td>flute, bass clarinet</td></tr>'
             f'<tr><td><b>Brass</b></td><td>Buzzing lips into a metal tube</td><td>trumpet, French horn</td></tr>'
             f'<tr><td><b>Percussion</b></td><td>Hitting, shaking or scraping. A celesta has keys that strike metal bars.</td><td>celesta</td></tr></table>'
             f'<div class="part">How to listen: three times</div>'
             f'<div class="cols" style="gap:10pt">'
             f'<div class="card"><b class="k">1</b>Just listen. Close your eyes. Do not write yet.</div>'
             f'<div class="card"><b class="k">2</b>Listen with your listening map. Mark as you go.</div>'
             f'<div class="card"><b class="k">3</b>Circle what you heard and tell about it.</div></div>'
             f'<div class="part">Be a polite audience</div>'
             f'<ul class="bul"><li>Quiet voices and bodies so everyone can hear.</li><li>There are no wrong feelings about music. Say why you feel that way.</li></ul>')
    return page("Words for describing music", "LEARN", "Listening toolkit", inner, n, watermark, title="Listening Toolkit")


def gallery_page(n, watermark=False):
    cells = "".join(
        f'<div class="card" style="text-align:center;padding:8pt 6pt"><div style="display:flex;justify-content:center">{icon(i, 74)}</div>'
        f'<div class="h" style="font-size:13pt;margin-top:3pt">{INSTR[i][0]}</div>'
        f'<div style="font-family:Oswald;font-weight:500;font-size:9.5pt;color:{ACCENT};text-transform:uppercase;letter-spacing:.06em">{INSTR[i][1]}</div>'
        f'<div style="font-size:9.8pt;line-height:1.25;margin-top:3pt">{INSTR_BLURB[i]}</div></div>' for i in INSTR_ORDER)
    inner = (f'<div class="how">Meet the eight sounds you will hunt for. Next, use the spotting chart on {pg("spot")}.</div>'
             f'<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:9pt">{cells}</div>'
             f'<div class="box" style="margin-top:10pt;font-size:10.5pt"><b>Did you know?</b> Tchaikovsky heard the celesta in Paris and brought one to Russia for The Nutcracker. '
             f'Most listeners had never heard it before 1892. It is played with a keyboard, but a hammer strikes a metal bar inside, so it sounds like a tiny bell.</div>'
             f'<div class="part">Draw it</div><div class="small" style="margin-bottom:4pt">Pick your favorite instrument above. Draw it in the box and write one word that describes its sound.</div>'
             f'<div class="box" style="flex:1;min-height:110pt"></div>')
    return page("The orchestra instruments you will hear", "LOOK", "Instrument gallery", inner, n, watermark, title="Instrument Gallery")


def spot_page(n, watermark=False, key=False):
    sk = spot_key()
    head = "".join(f'<th style="text-align:center;font-size:7.8pt;padding:3pt 1pt">{INSTR[i][0].replace(" ", "<br>", 1) if " " in INSTR[i][0] else INSTR[i][0]}</th>' for i in INSTR_ORDER)
    rows = ""
    for m in MOVES:
        cells = "".join(
            f'<td style="text-align:center;height:34pt;width:45pt">'
            + (f'<span class="ans" style="font-size:16pt">X</span>' if key and i in sk[m["k"]] else "") + "</td>" for i in INSTR_ORDER)
        rows += f'<tr><td><b>{m["n"]}</b> · {escape(m["title"])}</td>{cells}</tr>'
    inner = (f'<div class="how">Listen to each movement again. Put an <b>X</b> under every instrument you can hear <b>clearly</b>. Many instruments play, so look for the ones that stand out.</div>'
             f'<table class="t" style="font-size:10pt"><tr><th style="width:150pt">Movement</th>{head}</tr>{rows}</table>'
             f'<div class="part">Which was easiest to hear? Why?</div><div class="ln2"></div><div class="ln2"></div><div class="ln2"></div>'
             f'<div class="part">Instrument families<small>Write each instrument under its family.</small></div>'
             f'<div class="cols" style="gap:10pt">'
             + "".join(f'<div class="card" style="height:150pt"><b class="k" style="font-family:Oswald">{f}</b></div>' for f in ("Strings", "Woodwinds", "Brass", "Percussion"))
             + f'</div><div class="small" style="margin-top:4pt">Children’s voices are not in an instrument family. Write them in the margin.</div>')
    return page("Which instruments do you hear?", "SPOT", "Spotting chart", inner, n, watermark, name=True, right=f"Answer key on page {IX['key']}", title="Instrument Spotting")


def quiz_page(n, watermark=False):
    qa = "".join(f'<div style="display:flex;gap:7pt;align-items:center;margin:0 0 4pt;font-size:10.4pt;line-height:1.25">'
                 f'<b style="flex:0 0 14pt">{r}.</b><span style="flex:0 0 24pt;border-bottom:1pt solid #000;height:14pt"></span><span>{escape(c)}</span></div>'
                 for r, c, _ in quiz_a_rows())
    bank = " · ".join(f'<b>{m["n"]}</b> {escape(m["title"])}' for m in MOVES)
    qb = "".join(f'<div style="margin:0 0 6pt;font-size:10.6pt;line-height:1.25"><b>{i + 7}.</b> {escape(q)}<br>'
                 + "&nbsp;&nbsp; ".join(f'<b>{"ABC"[j]}</b> {escape(o)}' for j, o in enumerate(opts)) + '</div>'
                 for i, (q, opts, _) in enumerate(QUIZ_B))
    qc = "".join(f'<div style="display:flex;gap:7pt;margin:0 0 5pt;font-size:10.6pt;line-height:1.25"><b style="flex:0 0 20pt">{i + 13}.</b>'
                 f'<span style="flex:0 0 118pt;white-space:nowrap">{circ("TRUE")}{circ("FALSE")}</span><span>{escape(s)}</span></div>' for i, (s, _) in enumerate(QUIZ_C))
    inner = (f'<div class="part" style="margin-top:2pt">A · Match each clue to a movement<small>Write the movement number in the blank.</small></div>'
             f'<div class="box" style="font-size:9.8pt;margin-bottom:5pt;padding:4pt 8pt">{bank}</div>{qa}'
             f'<div class="part">B · Circle the best answer</div>{qb}'
             f'<div class="part" style="margin-top:2pt">C · True or false<small>Circle one.</small></div>{qc}'
             f'<div style="margin-top:auto;display:flex;justify-content:flex-end;font-family:Oswald;font-weight:700;font-size:15pt">Score: <span class="wl" style="width:44pt"></span> / {QUIZ_TOTAL}</div>')
    return page(f"{QUIZ_TOTAL} questions · 20 minutes", "QUIZ", f"{QUIZ_TOTAL} points", inner, n, watermark, name=True,
                right=f"Answer key on page {IX['key']}", title="Nutcracker Quiz")


def key_page(n, watermark=False):
    sk = spot_key()
    spot_rows = "".join(f"<tr><td><b>{m['n']}</b> · {escape(m['title'])}</td><td class='ans'>"
                        + ", ".join(INSTR[i][0] for i in sk[m['k']]) + "</td></tr>" for m in MOVES)
    ev = " ".join(event_key())
    wk = " · ".join(f"{c}: <span class='ans'>{l}</span>" for c, l in who_key())
    qk = quiz_key()
    qa = " · ".join(f"{r}: <span class='ans'>{mv}</span>" for r, mv in qk["A"])
    qb = " · ".join(f"{i + 7}: <span class='ans'>{l}</span>" for i, l in enumerate(qk["B"]))
    qc = " · ".join(f"{i + 13}: <span class='ans'>{l}</span>" for i, l in enumerate(qk["C"]))
    meter = "".join(f"<tr><td><b>{m['n']}</b> · {escape(m['title'])}</td><td class='ans'>{m['meter'] or 'not asked'}</td></tr>" for m in MOVES)
    inner = (f'<div class="cols" style="gap:16pt"><div>'
             f'<div class="part" style="margin-top:4pt">Story check ({pg("story_q")})</div>'
             f'<table class="t"><tr><td>A · Story order, first to last</td><td class="ans">Cards {ev}</td></tr>'
             f'<tr><td>B · Who is who</td><td>{wk}</td></tr></table>'
             f'<div class="small">Part A: card letters in story order, so card {event_key()[0]} is 1 and card {event_key()[-1]} is 6. '
             f'Part C is open: accept any scene with one sentence.</div>'
             f'<div class="part">Instrument spotting ({pg("spot")})</div>'
             f'<table class="t"><tr><th>Movement</th><th>Instruments that stand out</th></tr>{spot_rows}</table>'
             f'<div class="small">Other instruments also play. Accept any you can truly hear, and listen once yourself first. Families: Strings = violin, harp · Woodwinds = flute, bass clarinet · Brass = trumpet, French horn · Percussion = celesta.</div>'
             f'</div><div>'
             f'<div class="part" style="margin-top:4pt">Quiz ({pg("quiz")}) · {QUIZ_TOTAL} points</div>'
             f'<table class="t"><tr><td>A · Clue number: movement</td><td>{qa}</td></tr>'
             f'<tr><td>B · Multiple choice</td><td>{qb}</td></tr>'
             f'<tr><td>C · True / false</td><td>{qc}</td></tr></table>'
             f'<div class="small">Scoring: 1 point each. 14–16 = excellent listener, 11–13 = good, 8–10 = keep listening, 0–7 = review the story and the toolkit.</div>'
             f'<div class="part">Movement facts</div>'
             f'<table class="t"><tr><th>Movement</th><th>Meter in the music</th></tr>{meter}</table>'
             f'<div class="part">Listening maps (answers vary)</div>'
             f'<div class="small" style="font-size:9.6pt!important;line-height:1.3"><b>Trepak:</b> the needle moves toward FAST by the end. '
             f'<b>Reed Flutes:</b> three flutes. <b>Sugar Plum Fairy:</b> the celesta is the sparkly high sound, the bass clarinet the low one. '
             f'<b>Flowers:</b> the harp plays first; the tune begins after it. <b>March:</b> mark loud and soft as you hear them, and accept anything the class can support. '
             f'<b>Snowflakes:</b> voices join the orchestra partway through. Maps and responses are about careful listening, so give credit for reasons.</div>'
             f'</div></div>')
    return page("Answer key · story check, spotting chart and quiz", "ANSWER KEY", "Teacher copy", f'<div class="kp">{inner}</div>', n, watermark, ak=True, title="Answer Key")


def review_page(n, watermark=False):
    inner = (f'<div class="how">You have heard six pieces from the ballet. Now be the critic.</div>'
             f'<div class="part" style="margin-top:2pt">My favorite movement<small>Circle one.</small></div>'
             f'<div>' + "".join(circ(f"{m['n']} · {m['title'].upper()}") for m in MOVES) + '</div>'
             f'<div class="part">Why I chose it</div><div class="ln2"></div><div class="ln2"></div><div class="ln2"></div>'
             f'<div class="part">Draw the music<small>Use shapes, lines and colors for the tempo, dynamics and mood.</small></div>'
             f'<div class="box" style="height:210pt"></div>'
             f'<div class="part">Write to a friend<small>Tell a friend about this ballet. Use at least 3 words from the listening toolkit ({pg("toolkit")}).</small></div>'
             f'<div class="lines" style="min-height:90pt"></div>'
             f'<div style="margin-top:8pt;font-size:11.5pt;display:flex;gap:6pt;align-items:center"><b>Stars for my listening:</b> '
             + "".join(f'<svg width="17pt" height="17pt" viewBox="0 0 20 20"><path d="M10 1 L12.5 7.3 L19 7.7 L14 12 L15.7 18.5 L10 15 L4.3 18.5 L6 12 L1 7.7 L7.5 7.3 Z" fill="#fff" stroke="#000" stroke-width="1.3" stroke-linejoin="round"/></svg>' for _ in range(5))
             + '</div>')
    return page("Your turn to be the critic", "REVIEW", "My Nutcracker review", inner, n, watermark, name=True, title="My Nutcracker Review")


def teacher_page(n):
    rows = [("Story and toolkit", "story", "toolkit", "read the story, check it, learn the music words"),
            ("Listening maps", "m_march", "m_sugar", "6 movements: map, circle, describe"),
            ("Instrument spotting", "gallery", "spot", "gallery and chart"),
            ("Quiz and key", "quiz", "key", f"{QUIZ_TOTAL}-point quiz and all answers"),
            ("Review", "review", "review", "favorite movement, drawing and letter"),
            ("Terms of use", "terms", "terms", "license and credits")]
    trs = "".join(f"<tr><td><b>{a}</b></td><td style='white-space:nowrap'>{IX[f] if f == l else str(IX[f]) + '–' + str(IX[l])}</td><td>{u}</td></tr>" for a, f, l, u in rows)
    pace = [("1", "Read the story, then the story check", "story, story_q", "25–30 min"),
            ("2", "Toolkit, then Movements 1 and 2", "toolkit, march, snow", "35–40 min"),
            ("3", "Movements 3 and 4", "trepak, reeds", "30 min"),
            ("4", "Movements 5 and 6", "flowers, sugar", "30 min"),
            ("5", "Instrument gallery and spotting chart", "gallery, spot", "30 min"),
            ("6", "Quiz, then review", "quiz, review", "35 min")]
    pt = "".join(f"<tr><td>{a}</td><td>{b}</td><td>{c}</td></tr>" for a, b, _, c in pace)
    inner = (f'<section class="page doc tn"><div class="rule"><h1>Teacher Notes</h1>'
             f'<div class="l" style="font-size:13pt">Nutcracker Listening Unit · Tchaikovsky, 1892 · grades 2–6</div></div>'
             f'<div class="cols"><div>'
             f'<h2>What it is</h2><p>A short unit that takes students through Tchaikovsky’s ballet <i>The Nutcracker</i> by listening. They read the story, then listen to six famous pieces with a listening map and response page for each, spot instruments, take a quiz and write a review. Every answer comes with a key.</p>'
             f'<h2>Before you start: choose a recording</h2>'
             f'<p><b>No audio is included.</b> Use any recording you have the right to play in class: a school or library music service, your own collection, or an orchestral recording in the public domain. '
             f'The music is by Tchaikovsky (1840–1893) and is long out of copyright, but many recordings are not, so check the recording you use. Listen to it yourself first, and find the movements by title.</p>'
             f'<h2>How each listening page works</h2><ol>'
             f'<li>Read the “About this music” box together.</li><li>Play the movement once while students just listen.</li>'
             f'<li>Play it again while they mark the map. Say “next” about every 15 seconds so the boxes keep pace with the music.</li>'
             f'<li>Play it a third time if you like. Students circle what they heard and write: grades 2–3 finish a sentence, grades 4–6 write three.</li></ol>'
             f'<h2>Grade levels</h2><p>Grades 2–3 use the sentence starters; grades 4–6 write full sentences with the toolkit words. Read the quiz aloud to grade 2.</p>'
             f'<h2>Good to know</h2><ul><li>The story is set at a Christmas Eve party, as in the original. The unit is about music and ballet, with no religious teaching, and works in any winter program.</li>'
             f'<li>Productions differ; the story here is one common version. Prints well in black and white.</li></ul>'
             f'</div><div>'
             f'<h2>What’s inside</h2><table class="t"><tr><th>Part</th><th>Pages</th><th>Use</th></tr>{trs}</table>'
             f'<h2>The six movements</h2><table class="t"><tr><th>#</th><th>Title</th><th>In the story</th></tr>'
             + "".join(f"<tr><td>{m['n']}</td><td>{escape(m['title'])}</td><td>{escape(m['scene'])}</td></tr>" for m in MOVES) + '</table>'
             f'<h2>Pacing</h2><table class="t"><tr><th>Day</th><th>Plan</th><th>Time</th></tr>{pt}</table>'
             f'<h2>Standards</h2><p>Supports responding to music: selecting and describing what students hear (MU:Re7.1, MU:Re7.2) and connecting music to its history and culture (MU:Cn11.0), National Core Arts Standards, Music.</p>'
             f'</div></div><div style="flex:1"></div>{foot(f"Page {n}")}</section>')
    return inner


def terms_page(n):
    return (f'<section class="page doc"><div class="rule"><h1>Terms of Use</h1>'
            f'<div class="l" style="font-size:13pt">Thank you for your purchase!</div></div>'
            f'<p>© {YEAR} {STORE}. {BRAND} by {STORE}. All rights reserved. This purchase gives <b>one teacher</b> a license to use this resource with their own students.</p>'
            f'<h2>You may</h2><ul><li>Print and copy pages for your own classroom and students, year after year.</li>'
            f'<li>Share pages with your own students through a password-protected class site or learning platform.</li>'
            f'<li>Leave the pages for a substitute teacher who teaches your own students.</li></ul>'
            f'<h2>You may not</h2><ul><li>Share, email or copy this resource for other teachers, a whole school or a district. '
            f'Additional licenses are available on Teachers Pay Teachers.</li>'
            f'<li>Post any part of it on a public website, shared drive or social media.</li>'
            f'<li>Sell, give away or claim any part of it as your own, or edit it into a new product.</li></ul>'
            f'<h2>Questions?</h2><p>Please use the Q&amp;A tab on the {BRAND} by {STORE} store on Teachers Pay Teachers. '
            f'If something looks wrong, let me know there and I will fix it.</p>'
            f'<h2>Credits</h2><ul>'
            f'<li>Pages, listening maps, instrument drawings and wording: original work, {BRAND} by {STORE}.</li>'
            f'<li>The Nutcracker, Op. 71, by Pyotr Ilyich Tchaikovsky (1892), is in the public domain. No recording is included.</li>'
            f'<li>Text fonts: Oswald (The Oswald Project Authors) and Source Sans 3 (Adobe), SIL Open Font License 1.1.</li></ul>'
            f'<p class="small">{DISCLOSURE}</p>'
            f'<div style="flex:1"></div>{foot(f"Page {n}")}</section>')


# ---------------------------------------------------------------- cover art: a nutcracker soldier (accent, tints, black, white)
def nutcracker_svg(cx=300, base=400, sc=1.0):
    A = ACCENT
    o = [f'<g transform="translate({cx} {base}) scale({sc})">']
    # base
    o.append('<rect x="-62" y="-14" width="124" height="14" rx="4" fill="#fff" stroke="#000" stroke-width="3"/>')
    # legs
    o.append(f'<rect x="-40" y="-92" width="30" height="80" fill="#fff" stroke="#000" stroke-width="3"/><rect x="10" y="-92" width="30" height="80" fill="#fff" stroke="#000" stroke-width="3"/>')
    o.append('<rect x="-44" y="-40" width="38" height="28" rx="3" fill="#000"/><rect x="6" y="-40" width="38" height="28" rx="3" fill="#000"/>')
    # coat
    o.append(f'<path d="M-62 -92 L-50 -230 L50 -230 L62 -92 Z" fill="{A}" stroke="#000" stroke-width="3.4" stroke-linejoin="round"/>')
    o.append('<rect x="-62" y="-122" width="124" height="16" fill="#000"/><rect x="-9" y="-124" width="18" height="20" fill="#fff" stroke="#000" stroke-width="2.4"/>')
    o.append(f'<path d="M-50 -230 L-86 -214 L-78 -190 L-50 -200 M50 -230 L86 -214 L78 -190 L50 -200" fill="{TINT1}" stroke="#000" stroke-width="3" stroke-linejoin="round"/>')
    o.append('<path d="M0 -230 L0 -126" stroke="#fff" stroke-width="3"/>')
    for k in range(4):
        o.append(f'<circle cx="0" cy="{-215 + k * 22}" r="4.6" fill="#fff" stroke="#000" stroke-width="2"/>')
    o.append('<path d="M-30 -230 L-30 -150 M30 -230 L30 -150" stroke="#fff" stroke-width="2.4" stroke-dasharray="2 6" stroke-linecap="round"/>')
    # arm and sword
    o.append(f'<rect x="-98" y="-210" width="22" height="82" rx="10" fill="{A}" stroke="#000" stroke-width="3" transform="rotate(8 -87 -210)"/>')
    o.append('<path d="M-100 -300 L-100 -118" stroke="#000" stroke-width="5" stroke-linecap="round"/><path d="M-112 -180 L-88 -180" stroke="#000" stroke-width="5" stroke-linecap="round"/>')
    o.append('<path d="M-100 -300 L-96 -312 L-104 -312 Z" fill="#000"/>')
    # head with big jaw
    o.append('<rect x="-40" y="-296" width="80" height="68" rx="20" fill="#fff" stroke="#000" stroke-width="3.4"/>')
    o.append('<path d="M-27 -244 Q0 -226 27 -244 L27 -228 L-27 -228 Z" fill="#fff" stroke="#000" stroke-width="2.4"/><path d="M-12 -243 L-12 -228 M0 -241 L0 -228 M12 -243 L12 -228" stroke="#000" stroke-width="2"/>')
    o.append('<circle cx="-16" cy="-274" r="6" fill="#000"/><circle cx="16" cy="-274" r="6" fill="#000"/>')
    o.append(f'<circle cx="-26" cy="-258" r="6" fill="{TINT1}" opacity=".8"/><circle cx="26" cy="-258" r="6" fill="{TINT1}" opacity=".8"/>')
    o.append('<path d="M-22 -254 Q0 -242 22 -254" fill="none" stroke="#000" stroke-width="3" stroke-linecap="round"/>')
    # beard
    o.append('<path d="M-36 -250 Q-38 -216 -20 -206 Q0 -196 20 -206 Q38 -216 36 -250 Q30 -226 0 -222 Q-30 -226 -36 -250 Z" fill="#fff" stroke="#000" stroke-width="2.6" stroke-linejoin="round"/>')
    # tall hat
    o.append(f'<path d="M-44 -296 L-38 -372 L38 -372 L44 -296 Z" fill="{A}" stroke="#000" stroke-width="3.4" stroke-linejoin="round"/>')
    o.append('<rect x="-47" y="-310" width="94" height="14" rx="3" fill="#000"/><rect x="-36" y="-352" width="72" height="8" fill="#fff"/>')
    o.append(f'<circle cx="0" cy="-326" r="11" fill="#fff" stroke="#000" stroke-width="2.6"/><circle cx="0" cy="-326" r="4.4" fill="{A}"/>')
    o.append('<rect x="-5" y="-392" width="10" height="20" rx="3" fill="#000"/>')
    o.append('</g>')
    return "".join(o)


def note_shapes(x, y, s=1.0, fill="#000"):
    return (f'<g transform="translate({x} {y}) scale({s})"><ellipse cx="0" cy="0" rx="9" ry="6.5" transform="rotate(-20)" fill="{fill}"/>'
            f'<path d="M8 -2 L8 -34" stroke="{fill}" stroke-width="3"/></g>')


def hero_svg(width_css):
    o = [nutcracker_svg(300, 420, 0.98)]
    for x, y, s, f in ((92, 150, 1.5, ACCENT), (130, 250, 1.1, "#000"), (505, 120, 1.4, "#000"), (470, 230, 1.7, ACCENT), (532, 300, 1.1, "#000")):
        o.append(note_shapes(x, y, s, f))
    o.append(f'<path d="M60 428 L540 428" stroke="#000" stroke-width="2.4" stroke-linecap="round"/>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 440" width="{width_css}" style="display:block">{"".join(o)}</svg>')


def cover_page():
    return (f'<section class="page cover"><div class="store">{BRAND}</div>'
            f'<div style="width:5.6in">{hero_svg("100%")}</div>'
            f'<div class="ctitle"><div class="a">NUTCRACKER</div><div class="b">LISTENING UNIT</div>'
            f'<div class="c">Tchaikovsky 1892 · story · 6 listening maps · instrument spotting · quiz with key</div></div>'
            f'<div class="cband">Grades 2–6 <em>·</em> 6 movements <em>·</em> {len(PLAN)} pages</div></section>')


# ---------------------------------------------------------------- assemble
def render_page(key, watermark=False):
    n = IX[key]
    if key.startswith("m_"):
        return move_page(key[2:], n, watermark)
    return {
        "cover": cover_page, "teacher": lambda: teacher_page(n), "story": lambda: story_page(n, watermark),
        "story_q": lambda: storyq_page(n, watermark), "toolkit": lambda: toolkit_page(n, watermark),
        "gallery": lambda: gallery_page(n, watermark), "spot": lambda: spot_page(n, watermark),
        "quiz": lambda: quiz_page(n, watermark), "key": lambda: key_page(n, watermark),
        "review": lambda: review_page(n, watermark), "terms": lambda: terms_page(n),
    }[key]()


PREVIEW_PICKS = ["story", "m_sugar", "spot", "key"]


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
              '<span style="font-weight:400">a</span><span style="font-weight:600">a</span><i style="font-weight:400">a</i></div>')


def sq_doc(body):
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{font_css()}'
            f'html,body{{margin:0;background:#fff}}{SQ_CSS}</style></head><body>{FONT_PRIME}{body}</body></html>')


def cover_square():
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div>'
        f'<div style="width:560px;margin-top:14px">{hero_svg("100%")}</div>'
        f'<div class="hd" style="font-size:66px;margin-top:8px">Nutcracker</div>'
        f'<div class="hd" style="font-size:128px;white-space:nowrap">Listening Unit</div>'
        f'<div class="sub" style="font-size:29px;margin-top:10px">Tchaikovsky 1892 · listening maps · instruments · quiz with key</div>'
        f'<div class="band">Grades 2–6 <em>·</em> 6 movements <em>·</em> {len(PLAN)} pages</div></div>')


def shot(src, w, wmsize, shadow=8):
    return (f'<div class="shot" style="width:{w}px;box-shadow:{shadow}px {shadow}px 0 #000"><img src="{src}">'
            f'<div class="swm" style="font-size:{wmsize}px">PREVIEW</div></div>')


def preview_square_1(img):
    items = [(img[0], "The story", "six scenes, easy to read"), (img[1], "Listening map", "one for each movement"),
             (img[2], "Instrument gallery", "eight sounds to find")]
    shots = "".join(f'<div style="width:290px">{shot(src, 290, 64)}<div class="lbl">{a}<span>{b}</span></div></div>' for src, a, b in items)
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div>'
        f'<div class="hd" style="font-size:74px;margin-top:20px">Listen to the ballet</div>'
        f'<div class="sub" style="font-size:27px;margin-top:8px">Story, maps and instrument spotting for six famous pieces</div>'
        f'<div style="display:flex;gap:28px;margin-top:60px;align-items:flex-start">{shots}</div>'
        f'<div class="band">Story <em>·</em> listening maps <em>·</em> instruments <em>·</em> quiz</div></div>')


def preview_square_2(a, b):
    pair = "".join(
        f'<div style="position:absolute;left:{x}px;top:{y}px;width:470px">{shot(src, 470, 100)}'
        f'<div class="lbl" style="position:absolute;{side}:-2px;top:-44px;margin:0">{lab}</div></div>'
        for src, lab, x, y, side in ((a, "Listening page", 50, 250, "left"), (b, "Answer key", 476, 300, "right")))
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div>'
        f'<div class="hd" style="font-size:72px;margin-top:20px">Map it, hear it, check it</div>'
        f'<div class="sub" style="font-size:27px;margin-top:8px">Every listening page and the full quiz have an answer key</div>'
        f'{pair}'
        f'<div class="band">Listening maps <em>·</em> quiz <em>·</em> answer key</div></div>')


def preview_square_3(imgs):
    cells = "".join(
        f'<div style="width:196px">{shot(src, 196, 44, 5)}<div class="lbl" style="font-size:17px;margin-top:9px">{lab}</div></div>'
        for src, lab in imgs)
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div>'
        f'<div class="hd" style="font-size:70px;margin-top:16px">Everything inside</div>'
        f'<div class="sub" style="font-size:27px;margin-top:8px">Story, toolkit, 6 listening pages, instruments, quiz, key and review</div>'
        f'<div style="display:grid;grid-template-columns:repeat(4,196px);gap:20px 26px;margin-top:34px">{cells}</div>'
        f'<div class="band">{len(PLAN)} pages <em>·</em> US Letter PDF <em>·</em> prints in black &amp; white</div></div>')


SHOTS1 = ["story", "m_sugar", "gallery"]
SHOTS2 = ["m_trepak", "key"]
SHOTS3 = [("story_q", "Story check"), ("toolkit", "Toolkit"), ("m_march", "March"), ("m_snow", "Snowflakes"),
          ("m_flowers", "Flowers"), ("spot", "Spotting"), ("quiz", "Quiz"), ("review", "Review")]


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


def pdf_png(src, page_no, out, res=110):
    subprocess.run(["pdftoppm", "-png", "-r", str(res), "-f", str(page_no), "-l", str(page_no), "-singlefile", src,
                    os.path.join(BUILD, out)], check=True)


TAGS = ["Christmas-Chanukah-Kwanzaa", "Winter", "Unit Plans", "Worksheets"]  # entries only, never headings (tools/tpt-validate.py)
SUBJECTS = ["Music"]  # "Performing Arts" is a heading TpT cannot select
GRADES = ["2nd-grade", "3rd-grade", "5th-grade", "6th-grade"]


def tpt_json(pages):
    return {
        "price": PRICE, "license_price": PRICE,
        "tax_code": "Other Digital Goods - No Physical Media",
        "grades": GRADES, "subjects": SUBJECTS, "tags": TAGS,
        "formats": ["PDF"], "pages": pages, "answer_key": "Included",
        "files": {"product": f"{SLUG}.pdf", "preview": f"{SLUG}-PREVIEW.pdf", "thumb1": "cover.png",
                  "thumb2": "preview-1.png", "thumb3": "preview-2.png", "thumb4": "preview-3.png"},
    }


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
def verify_data():
    errs = []
    opts = json.load(open(os.path.join(TPT, "TAG-OPTIONS.json")))["options"]
    subj = json.load(open(os.path.join(TPT, "SUBJECT-OPTIONS.json")))
    subj = subj["options"] if isinstance(subj, dict) else subj
    for t in TAGS:
        if t not in opts:
            errs.append(f"tag not in TAG-OPTIONS: {t}")
    for s in SUBJECTS:
        if s not in subj:
            errs.append(f"subject not in SUBJECT-OPTIONS: {s}")
    if not (1 <= len(TAGS) <= 6 and 1 <= len(SUBJECTS) <= 3 and 1 <= len(GRADES) <= 4):
        errs.append("tag/subject/grade counts")
    # instruments: every instrument has an icon and a family; movement data refers only to known ones
    for i in INSTR_ORDER:
        try:
            icon_body(i)
        except KeyError:
            errs.append(f"no icon for {i}")
        if i not in INSTR or i not in INSTR_BLURB:
            errs.append(f"instrument {i} missing data")
    if sorted(INSTR_ORDER) != sorted(INSTR):
        errs.append("INSTR_ORDER does not list every instrument once")
    for m in MOVES:
        if not m["inst"] or set(m["inst"]) - set(INSTR):
            errs.append(f"{m['k']}: bad instrument list")
        if len(m["facts"]) != 3 or len(m["moods"]) != 6:
            errs.append(f"{m['k']}: needs 3 facts and 6 mood words")
        if m["k"] not in MAPS or m["k"] not in MAP_TASK:
            errs.append(f"{m['k']}: no map")
    if [m["n"] for m in MOVES] != list(range(1, 7)) or len(MOVES) != 6:
        errs.append("movements must be numbered 1-6")
    if {i for m in MOVES for i in m["inst"]} != set(INSTR):
        errs.append("every instrument card should be a key answer somewhere (a card nobody can find is a dead end)")
    for fam in ("Strings", "Woodwinds", "Brass"):
        if not any(v[1] == fam for v in INSTR.values()):
            errs.append(f"no {fam} instrument")
    for m in MOVES:   # meter facts printed in the music facts must agree with the data
        if m["meter"] and m["meter"] not in " ".join(m["facts"]):
            errs.append(f"{m['k']}: meter {m['meter']} not stated in its facts")
    # story cards: permutations, and the computed order reads back to the original order
    if sorted(EVENT_PERM) != list(range(len(EVENTS))):
        errs.append("EVENT_PERM is not a permutation")
    if EVENT_PERM == sorted(EVENT_PERM):
        errs.append("event cards are not shuffled")
    cards = dict(event_cards())
    if [cards[l] for l in event_key()] != EVENTS:
        errs.append("event key does not reproduce the story order")
    if sorted(WHO_PERM) != list(range(len(WHO))) or WHO_PERM == sorted(WHO_PERM):
        errs.append("WHO_PERM must be a shuffled permutation")
    wc = {l: d for d, l in who_cards()}
    for (c, d), (c2, l) in zip(WHO, who_key()):
        if c != c2 or wc[l] != d:
            errs.append(f"who key wrong for {c}")
    # quiz
    if sorted(QUIZ_A_PERM) != list(range(len(MOVES))) or QUIZ_A_PERM == sorted(QUIZ_A_PERM):
        errs.append("QUIZ_A_PERM must be a shuffled permutation of the movements")
    for r, clue, mv in quiz_a_rows():
        if MOVES[mv - 1]["clue"] != clue:
            errs.append(f"quiz A row {r} key wrong")
    if len({c for _, _, mv in quiz_a_rows() for c in [mv]}) != 6 or len({c for _, c, _ in quiz_a_rows()}) != 6:
        errs.append("quiz A clues/answers must be 6 distinct")
    for q, o, c in QUIZ_B:
        if len(o) != 3 or len(set(o)) != 3 or not 0 <= c < 3:
            errs.append(f"quiz B '{q}': need 3 distinct options and one correct index")
    if len({c for _, _, c in QUIZ_B}) < 3:
        errs.append("quiz B answers are not spread across A, B and C")
    if len({t for _, t in QUIZ_C}) != 2:
        errs.append("quiz C needs both true and false answers")
    # facts that the quiz asserts, tied to the data
    qb = {q: (o, c) for q, o, c in QUIZ_B}
    o, c = qb["Which instrument plays the tune in the Dance of the Sugar Plum Fairy?"]
    if o[c].lower() != "celesta" or "celesta" not in MK["sugar"]["inst"]:
        errs.append("quiz: Sugar Plum answer must be the celesta")
    o, c = qb["How many beats are in each group of a waltz?"]
    if o[c] != "3" or MK["flowers"]["meter"] != "3/4":
        errs.append("quiz: waltz is 3 beats")
    o, c = qb["The flute belongs to which instrument family?"]
    if o[c] != INSTR["flute"][1]:
        errs.append("quiz: flute family")
    o, c = qb["The ballet was first performed in the year"]
    if o[c] != "1892":
        errs.append("quiz: premiere year")
    o, c = qb["Which dance speeds up as it goes on?"]
    if o[c] != "Trepak":
        errs.append("quiz: Trepak speeds up")
    harp = dict(QUIZ_C)["The harp is a brass instrument."]
    if harp != (INSTR["harp"][1] == "Brass"):
        errs.append("quiz C: harp statement")
    if QUIZ_TOTAL != 16:
        errs.append("quiz total changed")
    if len(PLAN) != len(set(PLAN)):
        errs.append("plan has a repeated page")
    return errs


def pdf_fonts(path):
    out = subprocess.run(["pdffonts", path], capture_output=True, text=True, check=True).stdout.splitlines()[2:]
    return [(ln.split()[0], ln.split()[-5]) for ln in out]


def footer_errors(path, safe=0.35 * 72):
    out = subprocess.run(["pdftotext", "-bbox", path, "-"], capture_output=True, text=True, check=True).stdout
    errs = []
    for i, pg_ in enumerate(re.findall(r'<page width="([\d.]+)" height="([\d.]+)">(.*?)</page>', out, re.S)):
        ph = float(pg_[1])
        ys = [float(m) for m in re.findall(r'yMax="([\d.]+)">Lotze', pg_[2])]
        if i == 0 and not ys:
            continue
        if not ys:
            errs.append(f"{os.path.basename(path)} p{i + 1}: footer not found on the page")
        elif max(ys) > ph - safe:
            errs.append(f"{os.path.basename(path)} p{i + 1}: footer ends {ph - max(ys):.1f}pt from the bottom edge (< {safe:.0f}pt)")
    return errs


OVERFLOW_JS = r"""
const { chromium } = require('playwright'); const url = require('url');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage();
  await p.goto(url.pathToFileURL(process.argv[2]).href, { waitUntil: 'load' });
  await p.evaluate(() => document.fonts.ready);
  const r = await p.evaluate(() => [...document.querySelectorAll('.page')].map((pg, i) => {
    const box = pg.getBoundingClientRect(); const foot = pg.querySelector('.foot'); const fy = foot ? foot.getBoundingClientRect().top : box.bottom;
    const bad = [];
    pg.querySelectorAll('.main *').forEach(e => { const q = e.getBoundingClientRect();
      if (q.width && q.height && (q.bottom > fy + 0.5 || q.right > box.right - 0.4 * 96 + 0.5 || q.left < box.left + 0.4 * 96 - 0.5)) bad.push(e.tagName + ':' + (e.textContent || '').slice(0, 30)); });
    pg.querySelectorAll('*').forEach(e => { if (e.scrollWidth > e.clientWidth + 2 && getComputedStyle(e).overflow !== 'visible') bad.push('clip:' + e.tagName); });
    return [i + 1, bad.slice(0, 3)]; }));
  console.log(JSON.stringify(r)); await b.close();
})();
"""


def overflow_errors():
    html = os.path.join(BUILD, "resource.html")
    js = os.path.join(BUILD, "overflow.js")
    with open(js, "w") as f:
        f.write(OVERFLOW_JS)
    out = subprocess.run(["node", js, html], capture_output=True, text=True, env=node_env())
    if out.returncode:
        return [f"overflow scan failed: {out.stderr[-200:]}"]
    return [f"page {i} ({PLAN[i - 1]}): content past the page body/margin: {bad}" for i, bad in json.loads(out.stdout.strip().splitlines()[-1]) if bad and i > 1]


def key_text_errors(txt):
    errs = []
    t = re.sub(r"\s+", " ", txt[IX["key"] - 1])
    if f"Cards {' '.join(event_key())}" not in t:
        errs.append("Key: story order not found")
    for c, l in who_key():
        if f"{c}: {l}" not in t:
            errs.append(f"Key: who is {c} not found")
    for m in MOVES:
        names = ", ".join(INSTR[i][0] for i in spot_key()[m["k"]])
        if f"{m['n']} · {m['title']} {names}" not in t:
            errs.append(f"Key: spotting row {m['n']} not found")
    qk = quiz_key()
    for r, mv in qk["A"]:
        if f" {r}: {mv}" not in t:
            errs.append(f"Key: quiz A{r} not found")
    for i, l in enumerate(qk["B"]):
        if f" {i + 7}: {l}" not in t:
            errs.append(f"Key: quiz Q{i + 7} not found")
    for i, l in enumerate(qk["C"]):
        if f" {i + 13}: {l}" not in t:
            errs.append(f"Key: quiz Q{i + 13} not found")
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
        for i, pg_ in enumerate(rd.pages):
            w, h = float(pg_.mediabox.width), float(pg_.mediabox.height)
            if abs(w - 612) > 1 or abs(h - 792) > 1:
                errs.append(f"{os.path.basename(path)} p{i + 1}: {w:.0f}x{h:.0f}pt, not US Letter")
        errs += footer_errors(path)
        fonts = pdf_fonts(path)
        for name, emb in fonts:
            if emb != "yes":
                errs.append(f"{os.path.basename(path)}: font {name} not embedded")
            if not re.search(r"oswald|sourcesans", name.lower()):
                errs.append(f"{os.path.basename(path)}: unexpected font {name} (a glyph fell back to a system font)")
        names = " ".join(n for n, _ in fonts).lower().replace(" ", "")
        for fam in ("oswald", "sourcesans3"):
            if fam not in names:
                errs.append(f"{os.path.basename(path)}: {fam} not found in PDF fonts")
    errs += overflow_errors()
    rd = PdfReader(PDF)
    txt = [subprocess.run(["pdftotext", "-f", str(i + 1), "-l", str(i + 1), PDF, "-"], capture_output=True, text=True,
                          check=True).stdout for i in range(len(rd.pages))]
    flat = [re.sub(r"\s+", " ", t) for t in txt]
    for i, t in enumerate(flat):
        if i > 0 and "Brian Lotze · Hudson Beat" not in t:
            errs.append(f"page {i + 1}: footer missing")
        if i > 0 and not re.search(rf"Page {i + 1}\s*$", t.strip()):
            errs.append(f"page {i + 1}: page number in the footer is wrong")
    errs += key_text_errors(txt)
    alltext = " ".join(flat).lower()
    for bad in BANNED:
        if re.search(rf"\b{bad}\b", alltext):
            errs.append(f"resource text mentions '{bad}'")
    if DISCLOSURE not in " ".join(flat):
        errs.append("terms page lacks the disclosure line")
    for m in re.finditer(r"[Pp]ages? (\d+)(?:–(\d+))?", " ".join(flat[1:])):
        for g in m.groups():
            if g and not 1 <= int(g) <= len(PLAN):
                errs.append(f"cross-reference to page {g} does not exist")
    for key in ("story_q", "quiz", "spot"):
        if f"Answer key on page {IX['key']}" not in flat[IX[key] - 1]:
            errs.append(f"{key}: answer-key cross-reference missing")
    for m in MOVES:   # each movement page shows its title and facts
        t = flat[IX["m_" + m["k"]] - 1]
        if m["title"].lower() not in t.lower():
            errs.append(f"movement page {m['k']}: title missing")
        for f in m["facts"]:
            if re.sub(r"\s+", " ", f) not in t:
                errs.append(f"movement page {m['k']}: fact missing: {f[:30]}")
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
    if tj["tags"] != TAGS or tj["subjects"] != SUBJECTS or tj["grades"] != GRADES:
        errs.append("tpt.json out of sync with gen.py (rebuild)")
    for k, f in tj["files"].items():
        if not os.path.exists(os.path.join(HERE, f)):
            errs.append(f"tpt.json file {k} missing: {f}")
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
    if not m2 or DISCLOSURE not in m2.group(1):
        errs.append("UPLOAD.md: description block missing the disclosure line")
    elif any(re.search(rf"\b{b}\b", m2.group(1).lower()) for b in BANNED):
        errs.append("UPLOAD.md: description uses a banned word")
    elif f"{len(rd.pages)} pages" not in m2.group(1):
        errs.append("UPLOAD.md: description page count wrong")
    for need in (f"${PRICE}",):
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
    print(f"CHECK OK: quiz ({QUIZ_TOTAL} points, one correct option each, answers spread) and story/who/spotting keys computed from the data and found "
          f"in the PDF key page; every instrument has an icon and a family; {len(PLAN)} Letter pages with footers, page numbers, no overflow; "
          f"only Oswald/Source Sans 3, all embedded; preview {len(PREVIEW_PICKS)} watermarked pages; images 2000x2000; tpt.json tags/subjects valid and UPLOAD.md ok.")


if __name__ == "__main__":
    if "--check" in sys.argv:
        check()
    else:
        build()
