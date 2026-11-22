#!/usr/bin/env python3
"""Listening Journal and Listening Glyphs (TpT 071): build the resource and verify it.

    python3 gen.py           build everything (PDFs, PNGs, UPLOAD.md, tpt.json) into this folder
    python3 gen.py --check   re-read the rendered HTML and SVG, recompute the music facts (tempo order, dynamics order, hairpin
                             direction, beat staves, glyph geometry), the vocabulary counts, the cross-references, the layout
                             (footer gaps, drawing padding, blank bands) and the files

Content lives in the DATA section. Drawings are built here and `--check` reads their geometry back from the rendered HTML with
formulas typed separately in the CHECK section. The resource is repertoire-free: no recording, composer or work is named.
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

SLUG = "listening-journal-and-glyphs"
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
TITLE = "Listening Journal"
LISTING_TITLE = "Listening Journal and Listening Glyphs: 10 Music Response Pages, Gr 2-8"
PRICE = "3.50"
TAGS = ["Worksheets", "Graphic Organizers", "Printables", "Rubrics", "Activities", "Handouts"]
SUBJECTS = ["Music", "Speaking & Listening"]
GRADES = ["2nd-grade", "4th-grade", "6th-grade", "8th-grade"]

# ================================================================== DATA
# Four listening glyphs: key, name, what it stands for, when to stamp it
GLYPHS = [
    ("contour", "Contour", "Melody contour", "The melody moves: it goes up, goes down, or stays level.", "Stamp it when you notice the tune rising, falling or leaping."),
    ("pulse", "Pulse", "Rhythm and beat", "The steady beat, and the pattern of long and short sounds on top of it.", "Stamp it when you can tap the beat or hear a rhythm pattern."),
    ("dynamics", "Dynamics", "Loud and soft", "How loud or soft the music is, and when it gets louder or softer.", "Stamp it when the volume changes or stays strong."),
    ("timbre", "Timbre", "Instrument color", "The color of a sound: what makes a flute sound different from a drum.", "Stamp it when you notice an instrument or voice and how it sounds."),
]
GLYPH_NAMES = [g[1] for g in GLYPHS]

# Vocabulary bank: (group, word, say it, definition)
GROUPS = ["Beat and rhythm", "Tempo", "Melody and pitch", "Dynamics", "Instruments and sound", "Form and texture"]
V = [
    ("Beat and rhythm", "beat", "", "The steady pulse in music, like a heartbeat you can tap."),
    ("Beat and rhythm", "rhythm", "", "The pattern of long and short sounds and silences over the beat."),
    ("Beat and rhythm", "meter", "", "How the beats are grouped into strong and weak, usually in sets of 2, 3 or 4."),
    ("Beat and rhythm", "measure", "", "One group of beats between two bar lines. It is also called a bar."),
    ("Beat and rhythm", "accent", "", "A note played or sung with extra stress so it stands out."),
    ("Beat and rhythm", "rest", "", "A silence that lasts for a certain number of beats."),
    ("Tempo", "tempo", "", "The speed of the beat."),
    ("Tempo", "largo", "LAR-go", "Very slow and broad."),
    ("Tempo", "andante", "ahn-DAHN-tay", "A walking speed, easy and a little slow."),
    ("Tempo", "moderato", "mod-er-AH-toe", "A medium speed."),
    ("Tempo", "allegro", "ah-LEG-row", "Fast and lively."),
    ("Tempo", "presto", "PRESS-toe", "Very fast."),
    ("Tempo", "accelerando", "ak-sel-er-AHN-doe", "Gradually getting faster."),
    ("Tempo", "ritardando", "ree-tar-DAHN-doe", "Gradually getting slower."),
    ("Melody and pitch", "pitch", "", "How high or low a sound is."),
    ("Melody and pitch", "melody", "", "The tune: a line of pitches you could hum or sing."),
    ("Melody and pitch", "contour", "", "The shape of a melody as it moves up, down or stays level."),
    ("Melody and pitch", "step", "", "A move from one note to the very next note, up or down."),
    ("Melody and pitch", "leap", "", "A jump from one note to a note that is farther away."),
    ("Melody and pitch", "phrase", "", "A musical sentence: an idea in the melody with a beginning and an ending."),
    ("Dynamics", "dynamics", "", "How loud or soft the music is."),
    ("Dynamics", "piano", "pee-AH-no", "Soft. The symbol is p."),
    ("Dynamics", "mezzo piano", "MET-so pee-AH-no", "Medium soft. The symbol is mp."),
    ("Dynamics", "mezzo forte", "MET-so FOR-tay", "Medium loud. The symbol is mf."),
    ("Dynamics", "forte", "FOR-tay", "Loud. The symbol is f."),
    ("Dynamics", "crescendo", "kreh-SHEN-doe", "Gradually getting louder. The hairpin opens wider."),
    ("Dynamics", "decrescendo", "day-kreh-SHEN-doe", "Gradually getting softer. The hairpin closes."),
    ("Instruments and sound", "timbre", "TAM-ber", "The color or quality of a sound that tells instruments and voices apart."),
    ("Instruments and sound", "strings", "", "Instruments with strings that are bowed or plucked, such as violin, cello and harp."),
    ("Instruments and sound", "woodwinds", "", "Instruments played by blowing air across an opening or against a reed, such as flute and clarinet."),
    ("Instruments and sound", "brass", "", "Metal instruments played by buzzing the lips into a mouthpiece, such as trumpet and tuba."),
    ("Instruments and sound", "percussion", "", "Instruments played by hitting, shaking or scraping, such as drums and xylophone."),
    ("Instruments and sound", "ensemble", "ahn-SAHM-bul", "A group of musicians who play or sing together."),
    ("Instruments and sound", "solo", "", "One performer playing or singing alone."),
    ("Form and texture", "form", "", "The plan of a piece: the order of its sections."),
    ("Form and texture", "section", "", "A big part of a piece, often labeled with a letter such as A or B."),
    ("Form and texture", "repeat", "", "Music that comes back again, the same or almost the same."),
    ("Form and texture", "contrast", "", "A change that makes one part sound different from the part before it."),
    ("Form and texture", "texture", "", "How many sounds or layers are heard at once, thin or thick."),
    ("Form and texture", "accompaniment", "", "Music that supports the melody."),
]
NV = len(V)
VOCAB_GROUP_ORDER_P1 = ["Beat and rhythm", "Tempo", "Melody and pitch"]
VOCAB_GROUP_ORDER_P2 = ["Dynamics", "Instruments and sound", "Form and texture"]
DEF = {w: d for _, w, _, d in V}

# Page 3 and the vocabulary bank must agree: short meanings used on the response page
TEMPO = [("largo", "very slow and broad"), ("andante", "a walking speed"), ("moderato", "a medium speed"), ("allegro", "fast and lively"), ("presto", "very fast")]
DYN = [("p", "piano", "soft", 0xE520), ("mp", "mezzo piano", "medium soft", 0xE52C), ("mf", "mezzo forte", "medium loud", 0xE52D), ("f", "forte", "loud", 0xE522)]
DYN_MEAN = {"crescendo": "gradually louder", "decrescendo": "gradually softer"}

MOODS = ["calm", "peaceful", "gentle", "dreamy", "graceful", "hopeful", "happy", "joyful", "playful", "bouncy", "silly", "excited",
         "energetic", "bold", "proud", "powerful", "majestic", "stormy", "tense", "eerie", "mysterious", "sad", "lonely", "serious"]
TIMBRE_WORDS = ["bright", "dark", "warm", "smooth", "airy", "buzzy", "ringing", "sharp", "mellow", "scratchy"]
FAMILIES = [
    ("Strings", ["violin", "viola", "cello", "double bass", "guitar", "harp"]),
    ("Woodwinds", ["flute", "clarinet", "oboe", "bassoon", "saxophone", "recorder"]),
    ("Brass", ["trumpet", "trombone", "French horn", "tuba"]),
    ("Percussion", ["snare drum", "bass drum", "cymbals", "xylophone", "timpani", "tambourine"]),
    ("Voices", ["child voice", "adult voice", "one singer", "choir (many voices)"]),
    ("Keyboard and electronic", ["piano", "organ", "synthesizer", "other: ______"]),
]
CONTOURS = [("rise", [(8, 34), (24, 28), (40, 22), (56, 16), (72, 10)]), ("fall", [(8, 10), (24, 16), (40, 22), (56, 28), (72, 34)]),
            ("arch", [(8, 32), (24, 20), (40, 8), (56, 20), (72, 32)]), ("valley", [(8, 8), (24, 20), (40, 32), (56, 20), (72, 8)]),
            ("wave", [(8, 22), (20, 10), (34, 34), (48, 10), (62, 34), (72, 22)]), ("level", [(8, 22), (24, 22), (40, 22), (56, 22), (72, 22)])]
SECTION_WORD = ["strings", "woodwinds", "brass", "percussion"]

# The ten response pages: key, title (page name), focus, short Track A, short Track B, listens, week
RESP = [
    ("r1", "First Listen", "What do I hear and feel?", "Finish three sentence starters.", "Write 3 to 4 sentences with a detail and two vocabulary words.", "1", 1),
    ("r2", "Instruments and Families", "Which instruments and families do I hear?", "Check instruments and circle one timbre word.", "Name the melody instrument and explain its timbre.", "2", 2),
    ("r3", "Tempo and Dynamics", "How fast, and how loud or soft?", "Circle one tempo word and the starting dynamic.", "Map the dynamics at three moments and describe tempo changes.", "2", 3),
    ("r4", "Mood and Character", "What mood does the music have?", "Circle three mood words and give one reason.", "Choose the best word and support it with two details.", "1 or 2", 4),
    ("r5", "Melody Shape", "What shape does the melody draw?", "Draw one contour line and circle steps or leaps.", "Draw three phrases, star the highest point and compare phrases.", "2 or 3", 5),
    ("r6", "Beat and Meter", "How are the beats grouped?", "Circle 2, 3 or 4 for each section and tap along.", "Also find the strongest beat and how each beat splits.", "2", 6),
    ("r7", "Form Map", "How is the music organized?", "Write letters in up to 5 boxes.", "Map up to 8 sections and mark what changed.", "2 or 3", 7),
    ("r8", "Compare Two Pieces", "How are two pieces alike and different?", "Fill in the table with words.", "Complete the table and write two comparing sentences.", "2 per piece", 8),
    ("r9", "Listening Log", "What did I listen to this month?", "Write one short sentence for each piece.", "Use a vocabulary word in each response.", "1 per entry", 9),
    ("r10", "Reflection and Exit Ticket", "What did I learn about listening?", "Answer three short questions.", "Write a 3-2-1 exit ticket with evidence.", "any", 10),
]
RKEYS = [r[0] for r in RESP]
RTITLE = {r[0]: r[1] for r in RESP}

ORDER = ["cover", "teach", "guide", "gkey", "gstamp"] + RKEYS + ["vocab1", "vocab2", "rubric", "terms"]
P = {k: i + 1 for i, k in enumerate(ORDER)}
TOTAL_PAGES = len(ORDER)
PAGE_NAMES = {"cover": "Cover", "teach": "Teacher notes", "guide": "Prompt guide and pacing", "gkey": "Listening glyph key", "gstamp": "Glyph stamp sheet",
              **{r[0]: r[1] for r in RESP}, "vocab1": "Vocabulary bank 1", "vocab2": "Vocabulary bank 2", "rubric": "Self-check and rubric", "terms": "Terms of use and credits"}
RUB_CRITERIA = [("Listening detail", "Names a clear detail that can be heard in the music.", "Names one detail.", "Names a detail that is vague or not in the music.", "No detail."),
                ("Vocabulary", "Uses vocabulary bank words correctly (Track A: 1 word, Track B: 2 words).", "Uses a word but not quite correctly.", "Uses everyday words only.", "No response."),
                ("Reasons", "Gives a reason or evidence for the answer (because...).", "Gives a reason that is general.", "Gives an answer without a reason.", "No reason."),
                ("Completeness", "Finishes the page neatly and follows the directions.", "Finishes most of the page.", "Finishes some of the page.", "Little finished.")]
RUB_MAX = 3
RUB_TOTAL = len(RUB_CRITERIA) * RUB_MAX
SCALE = [("11-12", "Strong"), ("9-10", "Secure"), ("6-8", "Developing"), ("0-5", "Needs review")]
CHECKS = [("I can say what I hear and feel when I listen.", ["r1", "r9"]), ("I can name instruments and their families.", ["r2"]), ("I can describe how fast the music is with a tempo word.", ["r3"]),
          ("I can describe how loud or soft it is with a dynamics word.", ["r3"]), ("I can draw the shape of a melody.", ["r5"]),
          ("I can tell if the beat is grouped in 2, 3 or 4.", ["r6"]), ("I can map the sections of a piece with letters.", ["r7"]), ("I can compare two pieces.", ["r8"])]


def pg(k):
    return f"page {P[k]}"


def pgs(a, b):
    return f"pages {P[a]}–{P[b]}"


XREFS = []


def xref(frm, text):
    XREFS.append((P[frm], text))
    return text


def f2(v):
    return f"{v:.2f}".rstrip("0").rstrip(".")


# ================================================================== drawings (all in code)
def glyph_svg(key, cls="gl"):
    """A 100 x 100 pictogram: 4-unit frame (outer edge 4 from the viewBox edge) and 5- or 6-unit art, 11+ units clear of the frame."""
    fr = '<rect x="6" y="6" width="88" height="88" rx="16" fill="none" stroke="#000" stroke-width="4"/>'
    s = 'stroke="#000" fill="none" stroke-linecap="round" stroke-linejoin="round"'
    if key == "contour":
        body = (f'<path class="art" d="M22 68 C 30 68 32 34 44 34 C 56 34 56 60 66 60 C 72 60 75 46 78 34" {s} stroke-width="5"/>'
                f'<circle class="art" cx="22" cy="68" r="5" fill="#000" stroke="none"/><circle class="art" cx="78" cy="34" r="5" fill="#000" stroke="none"/>')
    elif key == "pulse":
        tops = [28, 48, 48, 48]
        body = "".join(f'<line class="art bar" x1="{x}" y1="{t}" x2="{x}" y2="74" {s} stroke-width="6"/>' for x, t in zip((26, 42, 58, 74), tops))
    elif key == "dynamics":
        body = (f'<line class="art hp" x1="22" y1="50" x2="78" y2="28" {s} stroke-width="6"/>'
                f'<line class="art hp" x1="22" y1="50" x2="78" y2="72" {s} stroke-width="6"/>')
    else:
        body = (f'<path class="art" d="M50 22 C 50 22 30 46 30 60 C 30 71 39 79 50 79 C 61 79 70 71 70 60 C 70 46 50 22 50 22 Z" {s} stroke-width="5"/>'
                f'<path class="art" d="M38 62 C 42 54 46 54 50 62 C 54 70 58 70 62 62" {s} stroke-width="4"/>')
    return f'<svg class="{cls}" data-glyph="{key}" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">{fr}{body}</svg>'


def hairpin_svg(opening, w=90, h=34, sw=3.2, cls="hpn"):
    pad = sw * 2
    cy = h / 2
    s = f'stroke="#000" fill="none" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"'
    if opening:
        a = (pad, cy, w - pad, pad)
        b = (pad, cy, w - pad, h - pad)
    else:
        a = (pad, pad, w - pad, cy)
        b = (pad, h - pad, w - pad, cy)
    ln = "".join(f'<line x1="{f2(x1)}" y1="{f2(y1)}" x2="{f2(x2)}" y2="{f2(y2)}" {s}/>' for x1, y1, x2, y2 in (a, b))
    return f'<svg class="{cls}" data-icon="hairpin-{"open" if opening else "close"}" viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg">{ln}</svg>'


def contour_svg(name, pts, w=80, h=42, sw=3.4):
    pl = " ".join(f"{x},{y}" for x, y in pts)
    return (f'<svg class="cs" data-contour="{name}" viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg">'
            f'<polyline points="{pl}" fill="none" stroke="#000" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"/></svg>')


# Beat staves (unpitched rhythm: all notes on the middle line, so every stem goes down on the left edge of the notehead)
CP_PERC, CP_QHEAD, TS0 = 0xE069, 0xE0A4, 0xE080
STEM_W, STEM_LEN, STEM_DOWN_NW_Y, STAFF_W = 0.13, 3.5, -0.168, 0.16


def beat_svg(n, sp=6.5, bw=40, pad=5):
    x_clef = pad + 0.5 * sp
    x_ts = x_clef + 1.528 * sp + 0.9 * sp
    x0 = x_ts + 1.88 * sp + 0.9 * sp
    x_end = x0 + n * bw + 0.3 * sp
    top = pad + 0.6 * sp
    mid = top + 2 * sp
    stem_top = mid + STEM_DOWN_NW_Y * sp
    stem_bot = stem_top + STEM_LEN * sp
    fs = 11
    num_y = stem_bot + 0.4 * sp + fs
    height = num_y + 4 + pad
    width = x_end + pad
    g = [f'<line class="sl" x1="{f2(pad)}" y1="{f2(top + i * sp)}" x2="{f2(x_end)}" y2="{f2(top + i * sp)}" stroke="#000" stroke-width="{f2(STAFF_W * sp)}"/>' for i in range(5)]
    g.append(f'<rect class="bar" x="{f2(pad)}" y="{f2(top)}" width="{f2(0.16 * sp)}" height="{f2(4 * sp)}"/>')
    g.append(f'<rect class="bar" x="{f2(x_end - 0.16 * sp)}" y="{f2(top)}" width="{f2(0.16 * sp)}" height="{f2(4 * sp)}"/>')
    ff = "font-family:Bravura"
    g.append(f'<text class="clef" x="{f2(x_clef)}" y="{f2(mid)}" style="{ff}" font-size="{f2(4 * sp)}">{chr(CP_PERC)}</text>')
    g.append(f'<text class="tsn" data-n="{n}" x="{f2(x_ts)}" y="{f2(mid - sp)}" style="{ff}" font-size="{f2(4 * sp)}">{chr(TS0 + n)}</text>')
    g.append(f'<text class="tsd" data-n="4" x="{f2(x_ts)}" y="{f2(mid + sp)}" style="{ff}" font-size="{f2(4 * sp)}">{chr(TS0 + 4)}</text>')
    for k in range(n):
        hx = x0 + k * bw + 0.55 * sp
        g.append(f'<text class="nh" x="{f2(hx)}" y="{f2(mid)}" style="{ff}" font-size="{f2(4 * sp)}">{chr(CP_QHEAD)}</text>')
        g.append(f'<rect class="stem" x="{f2(hx)}" y="{f2(stem_top)}" width="{f2(STEM_W * sp)}" height="{f2(STEM_LEN * sp)}"/>')
        cx = hx + 1.18 * sp / 2
        g.append(f'<text class="cnt" x="{f2(cx)}" y="{f2(num_y)}" text-anchor="middle" font-size="{fs}" font-weight="{700 if k == 0 else 400}" '
                 f'style="font-family:\'Source Sans 3\'">{k + 1}</text>')
    return (f'<svg class="bt" data-beats="{n}" data-sp="{sp}" data-mid="{f2(mid)}" viewBox="0 0 {f2(width)} {f2(height)}" width="{f2(width)}" height="{f2(height)}" '
            f'xmlns="http://www.w3.org/2000/svg">{"".join(g)}</svg>')


# ================================================================== CSS
def font_css():
    f = os.path.relpath(FONTS, BUILD)
    faces = [("Oswald", 300, "normal", "oswald-latin-300-normal"), ("Oswald", 500, "normal", "oswald-latin-500-normal"), ("Oswald", 700, "normal", "oswald-latin-700-normal"),
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
.doc h2 { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 13.5pt; margin: 8pt 0 3pt; letter-spacing: .02em; }
.doc p, .doc li { font-size: 10.6pt; line-height: 1.34; margin: 0 0 5pt; }
.doc ul, .doc ol { margin: 0 0 4pt; padding-left: 16pt; }
.doc .rule { border-bottom: 2.2pt solid #000; margin-bottom: 8pt; padding-bottom: 6pt; }
.doc table { border-collapse: collapse; width: 100%; table-layout: fixed; font-size: 10pt; margin: 2pt 0 4pt; }
.doc td, .doc th { border: 1pt solid #000; padding: 3pt 6pt; text-align: left; vertical-align: middle; }
.doc th { font-family: 'Oswald'; font-weight: 500; text-transform: uppercase; font-size: 9.5pt; background: #000; color: #fff; }
.small { font-size: 9pt !important; color: #333; }
.box { border: 1.3pt solid #000; border-radius: 7pt; padding: 7pt 10pt 4pt; margin: 6pt 0; }
.box h3 { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 12.5pt; margin: 0 0 3pt; letter-spacing: .02em; }
.box p, .box li { font-size: 10.4pt !important; }
.box p { margin: 0 0 4pt !important; }
.cols { display: flex; gap: 12pt; }
.cols .box { flex: 1; margin: 6pt 0; }
.nd { display: flex; align-items: flex-end; gap: 6pt; font-size: 10pt; margin: 7pt 0 0; }
.nd .ln { flex: 1; border-bottom: 1pt solid #000; height: 11pt; }
/* response pages */
.rb { flex: 1; display: flex; flex-direction: column; gap: 8pt; padding: 8pt 0 10px; min-height: 0; }
.piece { display: flex; align-items: flex-end; gap: 6pt; font-size: 10pt; }
.piece .ln { flex: 1; border-bottom: 1pt solid #000; height: 11pt; }
.cb { display: inline-block; width: 11pt; height: 11pt; border: 1.2pt solid #000; border-radius: 2pt; vertical-align: -2pt; margin-right: 4pt; }
.wbox { border: 1.3pt solid #000; border-radius: 7pt; padding: 5pt 9pt 5pt; position: relative; display: flex; flex-direction: column; min-height: 0; }
.wbox > .lab { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 11pt; letter-spacing: .04em; margin: 0 0 2pt; }
.wbox .wl { border-bottom: 1pt solid #000; height: 20pt; flex: none; }
.wbox .grow { flex: 1; }
.trk { display: flex; align-items: center; gap: 7pt; margin: 0 0 3pt; }
.trk .pill { background: #000; color: #fff; font-family: 'Oswald'; font-weight: 700; font-size: 10.5pt; letter-spacing: .06em; padding: 1pt 8pt 2pt; border-radius: 10pt; white-space: nowrap; }
.trk .pill.b { background: ACCENT; }
.trk .gr { font-family: 'Oswald'; font-weight: 300; font-size: 10.5pt; }
.pr { font-size: 10.6pt; line-height: 1.28; margin: 0 0 3pt; }
.chips { display: flex; flex-wrap: wrap; gap: 5pt 6pt; }
.chip { border: 1.2pt solid #000; border-radius: 12pt; padding: 1pt 9pt 2pt; font-size: 11pt; font-weight: 600; white-space: nowrap; }
.row { display: flex; gap: 8pt; }
.row > * { flex: 1; min-width: 0; }
.gstrip { display: flex; align-items: center; gap: 10pt; }
.gstrip .g1 { display: flex; align-items: center; gap: 5pt; font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 10.5pt; }
.gstrip svg { width: 0.42in; height: 0.42in; display: block; flex: none; }
.cmp .gstrip svg { width: 0.3in; height: 0.3in; }
.gl { display: block; }
.bv { font-family: 'Bravura'; font-weight: 400; font-style: normal; line-height: 1; display: inline-block; height: 1em; white-space: nowrap; position: relative; top: .15em; }
.hpn { width: 0.7in; height: 0.27in; display: inline-block; vertical-align: middle; }
.cs { width: 0.8in; height: 0.42in; display: block; margin: 0 auto; }
.bt { display: block; }
.fam { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 6pt; }
.fam .fb { border: 1.2pt solid #000; border-radius: 6pt; padding: 4pt 8pt 3pt; }
.fam .fb b { font-family: 'Oswald'; text-transform: uppercase; font-size: 10.5pt; letter-spacing: .04em; display: block; margin-bottom: 1pt; }
.fam .fb div { font-size: 10pt; line-height: 1.38; white-space: nowrap; }
.tempo { display: flex; gap: 0; border: 1.2pt solid #000; border-radius: 6pt; overflow: hidden; }
.tempo .tp { flex: 1; text-align: center; padding: 4pt 3pt 5pt; border-right: 1pt solid #000; }
.tempo .tp:last-child { border-right: 0; }
.tempo .tp b { font-family: 'Oswald'; text-transform: uppercase; font-size: 12pt; letter-spacing: .03em; display: block; }
.tempo .tp span { display: block; font-size: 9.4pt; line-height: 1.2; }
.tempo .tp i { display: inline-block; width: 12pt; height: 12pt; border: 1.2pt solid #000; border-radius: 50%; margin-top: 3pt; }
.arrow { display: flex; justify-content: space-between; font-family: 'Oswald'; font-weight: 300; font-size: 10pt; margin: 2pt 2pt 0; }
.dyn { width: 100%; border-collapse: collapse; }
.dyn td, .dyn th { text-align: center; }
.doc .dyn th { background: #fff; color: #000; text-transform: none; font-family: 'Source Sans 3'; }
.dyn .bv { font-size: 19pt; }
.circ { display: inline-block; width: 22pt; height: 22pt; border: 1.2pt solid #000; border-radius: 50%; }
.dline { position: relative; height: 1pt; background: repeating-linear-gradient(90deg,#000 0 3pt,transparent 3pt 6pt); }
.draw { border: 1.3pt solid #000; border-radius: 7pt; position: relative; flex: 1; min-height: 0; }
.draw .gd { position: absolute; left: 0; right: 0; height: 0; border-top: 1pt dashed #888; }
.draw .gt { position: absolute; left: 6pt; font-size: 8.5pt; color: #444; background: #fff; padding: 0 3pt; }
.fbox { border: 1.3pt solid #000; border-radius: 6pt; flex: 1; min-height: 0; position: relative; }
.fbox span { position: absolute; left: 5pt; top: 3pt; font-family: 'Oswald'; font-weight: 700; font-size: 10pt; color: #555; }
.cmp { width: 100%; border-collapse: collapse; table-layout: fixed; }
.cmp td, .cmp th { border: 1pt solid #000; padding: 2pt 6pt; vertical-align: top; font-size: 10pt; }
.cmp th { background: #000; color: #fff; font-family: 'Oswald'; font-weight: 500; text-transform: uppercase; font-size: 10pt; }
.cmp td.f { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 10pt; width: 1.3in; }
.cmp td.f small { display: block; line-height: 1.1; font-family: 'Source Sans 3'; font-weight: 400; text-transform: none; font-size: 8.5pt; color: #444; }
.log { width: 100%; border-collapse: collapse; table-layout: fixed; flex: 1; }
.log tr:not(.lh) { height: 0.5in; }
.log td, .log th { border: 1pt solid #000; padding: 0 3pt; text-align: center; }
tr.lh { height: 0.5in; }
.log th { background: #000; color: #fff; font-family: 'Oswald'; font-weight: 500; text-transform: uppercase; font-size: 9pt; padding: 3pt; }
.log th svg { width: 0.26in; height: 0.26in; display: block; margin: 0 auto; background: #fff; border-radius: 4pt; }
.log td .cb { margin: 0; }
.cut { border-top: 1.4pt dashed #000; position: relative; margin: 4pt 0; }
.cut span { position: absolute; left: 50%; top: -8pt; transform: translateX(-50%); background: #fff; padding: 0 8pt; font-size: 9pt; }
.ticket { border: 1.6pt dashed #000; border-radius: 8pt; padding: 7pt 11pt 6pt; display: flex; flex-direction: column; flex: 1; min-height: 0; }
.scale { display: flex; gap: 14pt; align-items: center; font-size: 10.5pt; }
.scale .sn { display: inline-flex; align-items: center; justify-content: center; width: 22pt; height: 22pt; border: 1.2pt solid #000; border-radius: 50%; font-family: 'Oswald'; font-weight: 700; margin-right: 4pt; }
/* glyph key and stamps */
.gk { display: flex; gap: 14pt; align-items: center; border: 1.4pt solid #000; border-radius: 9pt; padding: 8pt 12pt; flex: 1; min-height: 0; }
.gk .gb { flex: none; width: 1.45in; }
.gk .gb svg { width: 1.45in; height: 1.45in; }
.gk h3 { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 18pt; margin: 0; line-height: 1; letter-spacing: .02em; }
.gk h3 small { font-family: 'Oswald'; font-weight: 300; text-transform: none; font-size: 12pt; margin-left: 6pt; }
.gk p { margin: 3pt 0 0 !important; font-size: 11pt !important; line-height: 1.28; }
.gk .where { font-size: 9.8pt !important; color: #333; }
.gk .wl { border-bottom: 1pt solid #000; height: 17pt; margin-top: 2pt; }
.sg { display: grid; grid-template-columns: repeat(4, 1fr); grid-template-rows: repeat(6, 1fr); flex: 1; min-height: 0; margin: 8pt 0 8pt; border-top: 1pt dashed #000; border-left: 1pt dashed #000; }
.tile { border-right: 1pt dashed #000; border-bottom: 1pt dashed #000; padding: 6pt 7pt 5pt; display: flex; align-items: center; gap: 6pt; }
.tile svg { width: 0.62in; height: 0.62in; flex: none; }
.tile .tt { flex: 1; min-width: 0; }
.tile b { font-family: 'Oswald'; text-transform: uppercase; font-size: 11pt; letter-spacing: .04em; display: block; }
.tile .wl { border-bottom: 1pt solid #000; height: 17pt; }
.tile .gx { font-size: 8pt; color: #444; line-height: 1.1; }
/* vocabulary */
.vt { width: 100%; border-collapse: collapse; table-layout: fixed; }
.vt th { background: #000; color: #fff; font-family: 'Oswald'; font-weight: 500; text-transform: uppercase; font-size: 9.5pt; text-align: left; padding: 2pt 6pt; border: 1pt solid #000; }
.vt td { border: 1pt solid #000; padding: 4.8pt 6pt; font-size: 10.6pt; line-height: 1.22; vertical-align: middle; }
.vt td.w { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 11pt; letter-spacing: .02em; }
.vt td.s { color: #444; font-style: italic; font-size: 9.8pt; }
.vt .bv { font-size: 15pt; margin-left: 3pt; text-transform: none; }
.vg td { background: #DCEEF8; font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; letter-spacing: .06em; font-size: 11pt; padding: 4pt 6pt !important; }
.vg td span { font-weight: 300; text-transform: none; letter-spacing: 0; margin-left: 6pt; }
.rbt td, .rbt th { font-size: 9.8pt !important; vertical-align: top; }
.rbt td.c { width: 1.1in; font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; }
.cover { align-items: center; justify-content: space-between; padding: 0.55in 0.6in 0.5in; }
.store { font-family: 'Oswald'; font-weight: 500; font-size: 13pt; letter-spacing: .32em; text-transform: uppercase; }
.ctitle { text-align: center; }
.ctitle .a { font-family: 'Oswald'; font-weight: 700; font-size: 40pt; line-height: 1; letter-spacing: .02em; }
.ctitle .b { font-family: 'Oswald'; font-weight: 700; white-space: nowrap; font-size: 78pt; line-height: .95; letter-spacing: .01em; }
.ctitle .c { font-family: 'Oswald'; font-weight: 300; font-size: 16pt; margin-top: 8pt; }
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


def page(key, body, wm=False, tag="TEACHER", tagline="", ak=False, extra="", student=False, piece=False, sub=None):
    n = P[key]
    right = f"Page {n}" + (f" · {extra}" if extra else "")
    top = (f'<div class="top"><div class="t">{TITLE}<small>{sub or PAGE_NAMES[key]}</small></div>'
           f'<div class="tag"><div class="lv{" ak" if ak else ""}">{tag}</div><div class="ln">{tagline}</div></div></div>')
    nd = ('<div class="nd"><span>Name</span><span class="ln"></span><span>Date</span><span class="ln" style="flex:.45"></span>'
          '<span>Class</span><span class="ln" style="flex:.4"></span></div>') if student else ""
    pc = ('<div class="piece" style="margin-top:6pt"><span>Piece (title or listening number)</span><span class="ln"></span>'
          '<span>Listen</span><span><i class="cb"></i>1st</span><span><i class="cb"></i>2nd</span><span><i class="cb"></i>3rd</span></div>') if piece else ""
    return (f'<section class="page doc" data-p="{n}" data-k="{key}">{wm_div(wm)}{top}{nd}{pc}{body}'
            f'<div class="foot"><span>{COPY}</span><span>{right}</span></div></section>')


def doc_head(h1, sub):
    return f'<div class="rule" style="margin-top:8pt"><h1>{h1}</h1><div style="font-family:Oswald;font-weight:300;font-size:13pt">{sub}</div></div>'


def trk(letter, extra=""):
    gr = "Grades 2–4" if letter == "A" else "Grades 5–8"
    return f'<div class="trk"><span class="pill{" b" if letter == "B" else ""}">TRACK {letter}</span><span class="gr">{gr}{extra}</span></div>'


def wl(n):
    return '<div class="wl"></div>' * n


def cb(t):
    return f'<i class="cb"></i>{escape(t)}'


def gl_mini():
    return '<div class="gstrip" style="gap:5pt">' + ''.join(f'<span style="display:inline-flex;align-items:center;gap:2pt">{glyph_svg(g[0])}<i class="cb" style="margin:0"></i></span>' for g in GLYPHS) + '</div>'


def gl_strip(keys=None):
    keys = keys or [g[0] for g in GLYPHS]
    names = {g[0]: g[1] for g in GLYPHS}
    return '<div class="gstrip">' + "".join(f'<div class="g1">{glyph_svg(k)}<span>{names[k]}</span><i class="cb"></i></div>' for k in keys) + "</div>"


def dynglyph(k, size=None):
    d = [x for x in DYN if x[0] == k][0]
    st = f' style="font-size:{size}pt"' if size else ""
    return f'<span class="bv" data-dyn="{k}" data-g="{d[3]:X}"{st}>{chr(d[3])}</span>'


# ================================================================== pages
def cover_page():
    return (f'<section class="page cover" data-p="1" data-k="cover"><div class="store">{BRAND}</div>'
            f'<div style="height:4.6in;display:flex;align-items:center;justify-content:center"><img src="../art/hero.png" alt="" style="display:block;height:4.6in;width:auto;margin:-0.1in 0"></div>'
            f'<div class="ctitle"><div class="a">LISTENING JOURNAL</div><div class="b">&amp; GLYPHS</div>'
            f'<div class="c">10 reusable response pages, 4 listening glyphs and a {NV}-word vocabulary bank</div></div>'
            f'<div class="cband">Grades 2–8 <em>·</em> 10 response pages <em>·</em> 4 glyphs <em>·</em> {TOTAL_PAGES} pages</div></section>')


def teach_page(wm=False):
    body = (
        f'<div class="cols"><div class="box"><h3>How it works</h3><ol>'
        f'<li><b>You choose the music.</b> Any recording, live performance or class performance works. No pieces are named in this resource, so you can use it with any music you teach.</li>'
        f'<li>Set one listening focus (one response page) and say it before you press play.</li>'
        f'<li>Play the music one to three times, as the guide on {pg("guide")} suggests, and let students respond.</li>'
        f'<li>Share answers aloud, then have students stamp the glyphs they used ({pg("gkey")}).</li></ol></div>'
        f'<div class="box"><h3>What is inside ({TOTAL_PAGES} pages)</h3><ul>'
        f'<li>10 response pages, {pgs("r1", "r10")}, each with two prompt tracks.</li>'
        f'<li>4 listening glyphs: {", ".join(GLYPH_NAMES[:-1])} and {GLYPH_NAMES[-1]}. A key ({pg("gkey")}) and a stamp sheet ({pg("gstamp")}).</li>'
        f'<li>A vocabulary bank of {NV} words in {len(GROUPS)} groups ({pgs("vocab1", "vocab2")}).</li>'
        f'<li>Prompt guide and pacing ({pg("guide")}), self-check and rubric ({pg("rubric")}).</li></ul></div></div>'
        f'<h2>Two tracks, one page</h2>'
        f'<p>Every response page has <b>Track A</b> for grades 2–4 and <b>Track B</b> for grades 5–8. The page, the drawing space and the word banks are the same, so a mixed class '
        f'can listen together. Track A asks for choosing, circling and one short sentence. Track B asks for a reason, evidence from the music and vocabulary words. '
        f'Grades 4 and 5 can use either track.</p>'
        f'<h2>Make it reusable</h2><ul>'
        f'<li><b>Copy a page as often as you like for your own students.</b> The response pages are blank on purpose: write the piece name on the line at the top, not in advance.</li>'
        f'<li><b>Slide the pages into plastic sleeves</b> and use dry-erase markers, or print them on the back of scrap paper.</li>'
        f'<li><b>Glyphs are quick answers.</b> When time is short, students stamp, draw or circle a glyph instead of writing. Use the stamp sheet ({pg("gstamp")}) for cut-out stamps.</li>'
        f'<li><b>Build a journal.</b> Staple the vocabulary bank and a stack of response pages behind the listening log ({pg("r9")}).</li></ul>'
        f'<h2>Standards and notes</h2><p>The pages support the Responding processes of the National Core Arts Standards for Music (MU:Re7.1, MU:Re8.1 and MU:Re9.1). '
        f'Match them to your own curriculum. Tempo and dynamics words follow standard Italian terms. The beat examples on {pg("r6")} use unpitched notes on a one-line rhythm staff. '
        f'No songs, lyrics or copyrighted characters are used.</p>'
        f'<h2>Choosing music</h2><ul><li>Pick a piece, or a one-to-three-minute excerpt, with something clear to listen for.</li>'
        f'<li>Vary the music across the year: different styles, places, times and ensembles.</li></ul>'
        f'<h2>Supporting every listener</h2><p><b>Younger or newer listeners:</b> use Track A, read prompts aloud and let students stamp glyphs instead of writing. <b>Older or experienced listeners:</b> use Track B and have partners compare reasons.</p>'
        f'<p class="small">{DISCLOSURE}</p>')
    return page("teach", body, wm, tag="TEACHER", tagline="Read first")


def guide_page(wm=False):
    rows = "".join(f'<tr><td class="n" style="text-align:center"><b>{P[k]}</b></td><td><b>{escape(t)}</b><br><span class="small">{escape(fo)}</span></td><td>{escape(a)}</td><td>{escape(b)}</td>'
                   f'<td style="text-align:center">{ls}</td><td style="text-align:center"><b>{wk}</b></td></tr>' for k, t, fo, a, b, ls, wk in RESP)
    body = (f'<h2 style="margin-top:8pt">Prompts by page, listens and a ten-week sequence</h2>'
            f'<table class="gt"><tr><th style="width:34pt">Page</th><th style="width:132pt">Response page</th><th>Track A (grades 2–4)</th><th>Track B (grades 5–8)</th><th style="width:44pt">Listens</th><th style="width:34pt">Week</th></tr>{rows}</table>'
            f'<h2>A 10-minute routine</h2><ol>'
            f'<li><b>1 minute:</b> name the focus and read the prompt together.</li>'
            f'<li><b>2 to 4 minutes:</b> first listen. Students only listen, or stamp a glyph.</li>'
            f'<li><b>3 minutes:</b> second listen while students respond on the page.</li>'
            f'<li><b>2 minutes:</b> partner talk, then two or three students share.</li>'
            f'<li><b>1 minute:</b> stamp the glyphs that fit and pick a vocabulary word to use next time.</li></ol>'
            f'<p class="small">One page a week fits a once-a-week class. Pages {P["r1"]}–{P["r8"]} build skills in order. The log ({pg("r9")}) can run from week 1.</p>')
    return page("guide", body, wm, tag="TEACHER", tagline="Pacing")


def gkey_page(wm=False):
    where = {"contour": ("Use with", f"the melody shape page ({pg('r5')})"), "pulse": ("Use with", f"the beat and meter page ({pg('r6')})"),
             "dynamics": ("Use with", f"the tempo and dynamics page ({pg('r3')})"), "timbre": ("Use with", f"the instruments page ({pg('r2')})")}
    adds = {"contour": "Add a word: up, down, level, steps or leaps.", "pulse": "Add a word: steady, speeding up or slowing down.",
            "dynamics": "Add a letter or word: p, mp, mf, f, crescendo or decrescendo.", "timbre": "Add the instrument or a color word, such as bright or warm."}
    blocks = "".join(
        f'<div class="gk" data-glyph="{k}"><div class="gb">{glyph_svg(k)}</div><div><h3>{n}<small>{sub}</small></h3><p><b>It means:</b> {mean}</p>'
        f'<p><b>{escape(st.split(" when")[0])}</b> when{escape(st.split(" when", 1)[1])}</p><p class="where">{where[k][0]} {where[k][1]}. {adds[k]}</p></div></div>'
        for k, n, sub, mean, st in GLYPHS)
    body = (f'<p style="margin:8pt 0 0;font-size:10.8pt">A listening glyph is a quick-response picture. Draw it, stamp it or circle it to show what you noticed. '
            f'The glyphs also appear on {pg("r1")}, {pg("r2")}, {pg("r3")}, {pg("r5")}, {pg("r6")}, {pg("r8")}, {pg("r9")} and {pg("r10")}.</p>'
            f'<div style="display:flex;flex-direction:column;gap:9pt;flex:1;min-height:0;padding:8pt 0 10px">{blocks}</div>')
    return page("gkey", body, wm, tag="GLYPHS", tagline="4 listening glyphs")


def gstamp_page(wm=False):
    tiles = []
    for r in range(6):
        for k, n, sub, mean, st in GLYPHS:
            tiles.append(f'<div class="tile" data-glyph="{k}">{glyph_svg(k)}<div class="tt"><b>{n}</b><div class="wl"></div><div class="gx">What I noticed</div></div></div>')
    body = (f'<p class="cutnote" style="margin:8pt 0 0;font-size:10.2pt">Cut along the dashed lines. Glue a stamp beside an answer, or copy the picture onto the page. '
            f'There are six stamps for each of the 4 glyphs. The glyph key is on {pg("gkey")}.</p>'
            f'<div class="sg">{"".join(tiles)}</div>')
    return page("gstamp", body, wm, tag="STAMPS", tagline="24 cut-out stamps")


# ---------------- response pages
def r1(wm):
    body = (f'<div class="rb"><div class="row" style="flex:1.25;min-height:0"><div class="wbox"><div class="lab">I hear...</div><div class="grow"></div></div>'
            f'<div class="wbox"><div class="lab">I feel...</div><div class="grow"></div></div>'
            f'<div class="wbox"><div class="lab">It reminds me of...</div><div class="grow"></div></div></div>'
            f'<div class="wbox" style="padding:6pt 10pt"><div class="lab">Stamp or check the glyphs you noticed</div>{gl_strip()}</div>'
            f'<div class="wbox" style="flex:1"><div class="trk" style="margin-bottom:0">{trk("A")}</div><p class="pr">Finish the sentences. <b>I hear</b> ________________. <b>I feel</b> ________________. <b>My favorite part was</b> ________________.</p>{wl(3)}</div>'
            f'<div class="wbox" style="flex:1.3">{trk("B")}<p class="pr">Write 3 to 4 sentences about the music. Include one detail you heard and how it made you feel. Use two words from the vocabulary bank ({pgs("vocab1", "vocab2")}).</p>{wl(4)}<div class="grow"></div></div></div>')
    return page("r1", body, wm, tag="RESPONSE 1", tagline="of 10 · First listen", student=True, piece=True)


def r2(wm):
    fam = "".join(f'<div class="fb"><b>{escape(n)}</b>' + "".join(f'<div>{cb(x)}</div>' for x in items) + "</div>" for n, items in FAMILIES)
    tw = "".join(f'<span class="chip">{w}</span>' for w in TIMBRE_WORDS)
    body = (f'<div class="rb"><div style="font-size:10.4pt">Check every instrument or voice you hear. Keyboards belong to more than one family, so they have their own box.</div>'
            f'<div class="fam" data-families="{len(FAMILIES)}">{fam}</div>'
            f'<div class="wbox" style="padding:6pt 10pt"><div style="display:flex;align-items:center;gap:8pt"><div style="width:0.5in;flex:none">{glyph_svg("timbre")}</div>'
            f'<div style="flex:1"><div class="lab" style="margin:0 0 3pt">Timbre words: circle the ones that fit</div><div class="chips">{tw}</div></div></div></div>'
            f'<div class="wbox" style="flex:.8">{trk("A")}<p class="pr">Check the instruments you hear. Circle one timbre word. Write one more word that describes the sound: ______________</p>{wl(2)}</div>'
            f'<div class="wbox" style="flex:1.2">{trk("B")}<p class="pr">Which instrument played the melody? Which family is it in? Describe its timbre in your own words. Did the instruments change as the music went on? When?</p>{wl(3)}<div class="grow"></div></div></div>')
    return page("r2", body, wm, tag="RESPONSE 2", tagline="of 10 · Instruments", student=True, piece=True)


def r3(wm):
    tempo = "".join(f'<div class="tp" data-tempo="{w}"><b>{w}</b><span>{m}</span><i></i></div>' for w, m in TEMPO)
    dh = "".join(f'<th>{dynglyph(k)}<div class="small" style="font-family:Source Sans 3;text-transform:none;font-weight:600;color:#000;font-size:9pt;background:none">{n}<br>{m}</div></th>' for k, n, m, _ in DYN)
    def drow(label):
        return f'<tr><td style="text-align:left;width:70pt"><b>{label}</b></td>' + "".join('<td><span class="circ"></span></td>' for _ in DYN) + "</td></tr>"
    chg = (f'<table class="dyn" style="margin-top:4pt" data-change="1"><tr><td style="text-align:left;border:0;width:70pt"><b>It got...</b></td>'
           f'<td style="border:0">{hairpin_svg(True)}<div class="small">crescendo<br>{DYN_MEAN["crescendo"]}</div></td>'
           f'<td style="border:0">{hairpin_svg(False)}<div class="small">decrescendo<br>{DYN_MEAN["decrescendo"]}</div></td>'
           f'<td style="border:0"><span class="circ"></span><div class="small">stayed<br>the same</div></td></tr></table>')
    body = (f'<div class="rb"><div class="wbox" style="padding:6pt 10pt"><div class="lab">Tempo: how fast is the beat? Mark one.</div><div class="tempo">{tempo}</div>'
            f'<div class="arrow"><span>slow</span><span>fast</span></div></div>'
            f'<div class="wbox" style="padding:6pt 10pt"><div style="display:flex;gap:10pt;align-items:center"><div style="width:0.42in;flex:none">{glyph_svg("dynamics")}</div><div class="lab" style="margin:0">Dynamics: how loud or soft? Circle one for each moment.</div></div>'
            f'<table class="dyn" data-dyn="1"><tr><th style="width:70pt;background:none"></th>{dh}</tr>{drow("Beginning")}{drow("Middle")}{drow("End")}</table>{chg}</div>'
            f'<div class="wbox" style="flex:1">{trk("A")}<p class="pr">Mark one tempo word. Circle the dynamic at the beginning. Did the music get louder, softer or stay the same? Write one sentence about the tempo.</p>{wl(1)}</div>'
            f'<div class="wbox" style="flex:1.1">{trk("B")}<p class="pr">Fill in all three moments. Did the tempo stay steady, get faster (<i>accelerando</i>) or get slower (<i>ritardando</i>)? Why might the music change speed or volume there?</p>{wl(2)}<div class="grow"></div></div></div>')
    return page("r3", body, wm, tag="RESPONSE 3", tagline="of 10 · Tempo and dynamics", student=True, piece=True)


def r4(wm):
    ch = "".join(f'<span class="chip">{w}</span>' for w in MOODS)
    body = (f'<div class="rb"><div class="wbox" style="padding:7pt 10pt"><div class="lab">Mood and character words: circle the ones that fit</div><div class="chips" style="gap:7pt 7pt">{ch}</div></div>'
            f'<div class="wbox" style="padding:6pt 10pt"><div class="lab">Did the mood change? Write a word for each part.</div><div class="row">'
            f'<div style="display:flex;gap:5pt;align-items:flex-end">Beginning <span class="wl" style="flex:1;border-bottom:1pt solid #000;height:14pt"></span></div>'
            f'<div style="display:flex;gap:5pt;align-items:flex-end">Middle <span class="wl" style="flex:1;border-bottom:1pt solid #000;height:14pt"></span></div>'
            f'<div style="display:flex;gap:5pt;align-items:flex-end">End <span class="wl" style="flex:1;border-bottom:1pt solid #000;height:14pt"></span></div></div></div>'
            f'<div class="wbox" style="flex:1">{trk("A")}<p class="pr">Circle three mood words. Finish the sentence. <b>The music sounds</b> __________ <b>because I hear</b> ____________.</p>{wl(2)}</div>'
            f'<div class="wbox" style="flex:1.5">{trk("B")}<p class="pr">Choose the one word that fits best. Support it with two details from the music, such as tempo, dynamics, instruments or melody. If the mood changed, say where and what changed.</p>{wl(5)}<div class="grow"></div></div></div>')
    return page("r4", body, wm, tag="RESPONSE 4", tagline="of 10 · Mood", student=True, piece=True)


def r5(wm):
    shapes = "".join(f'<div style="text-align:center">{contour_svg(n, p)}<div class="small" style="font-weight:600;color:#000">{n}</div></div>' for n, p in CONTOURS)
    def dbox(lab, fl="1"):
        return (f'<div class="draw" style="flex:{fl}"><div class="gd" style="top:25%"></div><div class="gd" style="top:50%"></div><div class="gd" style="top:75%"></div>'
                f'<span class="gt" style="top:calc(25% - 7pt)">high</span><span class="gt" style="top:calc(50% - 7pt)">middle</span><span class="gt" style="top:calc(75% - 7pt)">low</span>'
                f'<span class="gt" style="right:8pt;left:auto;top:3pt;font-weight:700;font-size:9.5pt;color:#000">{lab}</span></div>')
    body = (f'<div class="rb"><div class="wbox" style="padding:6pt 10pt"><div style="display:flex;align-items:center;gap:8pt"><div style="width:0.5in;flex:none">{glyph_svg("contour")}</div>'
            f'<div style="flex:1"><div class="lab" style="margin:0">Contour shapes: the line a melody draws</div><div style="display:flex;justify-content:space-between;gap:4pt;margin-top:3pt">{shapes}</div></div></div></div>'
            f'<div style="font-size:10.4pt">Move your finger in the air along with the melody, then draw it. Start at the dot. Higher on the page means a higher pitch.</div>'
            f'{dbox("Phrase 1", "1.1")}{dbox("Phrase 2")}{dbox("Phrase 3")}'
            f'<div class="wbox">{trk("A")}<p class="pr">Draw one line in Phrase 1. Does the melody move mostly by <span class="chip" style="font-size:10pt">steps</span> or <span class="chip" style="font-size:10pt">leaps</span>? Circle one.</p></div>'
            f'<div class="wbox">{trk("B")}<p class="pr">Draw all three phrases. Star the highest point and name each shape. Is Phrase 2 the same, similar or different from Phrase 1? Write why: __________________________</p>{wl(1)}</div></div>')
    return page("r5", body, wm, tag="RESPONSE 5", tagline="of 10 · Melody shape", student=True, piece=True)


def r6(wm):
    st = "".join(f'<div style="display:flex;flex-direction:column;align-items:flex-start;gap:2pt">{beat_svg(n)}<div class="small" style="font-weight:600;color:#000">{n} beats in each measure</div></div>' for n in (2, 3, 4))
    nums = "".join(f'<span class="chip" style="min-width:26pt;text-align:center">{n}</span>' for n in (2, 3, 4))
    sect = "".join(f'<div style="display:flex;align-items:center;gap:8pt"><b style="width:62pt">Section {i}</b><span class="chips">{nums}</span></div>' for i in (1, 2, 3))
    taps = "".join('<span class="circ" style="width:20pt;height:20pt"></span>' for _ in range(12))
    body = (f'<div class="rb"><div class="wbox" style="padding:6pt 10pt"><div style="display:flex;align-items:center;gap:8pt"><div style="width:0.5in;flex:none">{glyph_svg("pulse")}</div>'
            f'<div class="lab" style="margin:0">How the beat looks: one measure of steady beats. Beat 1 is the strongest.</div></div>'
            f'<div style="display:flex;justify-content:space-between;gap:6pt;margin-top:4pt" data-beatrow="1">{st}</div></div>'
            f'<div class="wbox" style="padding:6pt 10pt"><div class="lab">Tap the beat. How many beats are in each group? Circle 2, 3 or 4.</div><div style="display:flex;flex-direction:column;gap:5pt">{sect}</div></div>'
            f'<div class="wbox" style="padding:6pt 10pt"><div class="lab">Tap and count: write the count in the circles (1, 2, 3... start over at each strong beat)</div><div style="display:flex;gap:7pt;flex-wrap:wrap">{taps}</div>'
            f'<div style="margin-top:5pt;font-size:10.4pt">The beat was: <span class="chip" style="font-size:10pt">steady</span> <span class="chip" style="font-size:10pt">speeding up</span> <span class="chip" style="font-size:10pt">slowing down</span></div></div>'
            f'<div class="wbox" style="flex:1">{trk("A")}<p class="pr">Tap along. Circle 2, 3 or 4 for each section. Write one word that tells how the beat felt, such as <i>marching</i> or <i>swaying</i>.</p>{wl(1)}</div>'
            f'<div class="wbox" style="flex:1.2">{trk("B")}<p class="pr">Which beat felt strongest? Does each beat split into 2 (like ti-ti) or into 3? How does the meter match the mood of the music?</p>{wl(3)}<div class="grow"></div></div></div>')
    return page("r6", body, wm, tag="RESPONSE 6", tagline="of 10 · Beat and meter", student=True, piece=True)


def r7(wm):
    ex = [("AB", "two different parts"), ("ABA", "the first part comes back"), ("ABACA", "part A keeps returning between new parts")]
    exr = "".join(f'<div style="display:flex;align-items:center;gap:7pt"><b style="font-family:Oswald;width:46pt;font-size:12pt">{a}</b><span style="font-size:10pt">{b}</span></div>' for a, b in ex)
    boxes = "".join(f'<div class="fbox"><span>{i}</span></div>' for i in range(1, 9))
    changes = ["melody", "tempo", "dynamics", "instruments", "mood"]
    trs = "".join(f'<tr><td style="text-align:left"><b>{c}</b></td>' + "".join('<td><i class="cb" style="margin:0"></i></td>' for _ in range(8)) + "</tr>" for c in changes)
    th = "".join(f"<th>{i}</th>" for i in range(1, 9))
    body = (f'<div class="rb"><div class="wbox" style="padding:6pt 10pt"><div class="lab">Form words: use a letter for each section</div>'
            f'<div style="display:flex;justify-content:space-between;gap:10pt"><div style="flex:1.1;display:flex;flex-direction:column;gap:3pt">{exr}</div>'
            f'<div style="flex:1.2;font-size:10pt;line-height:1.3">Write <b>A</b> in the first box. When something new starts, write <b>B</b>. If an earlier section returns, write its letter again.</div></div></div>'
            f'<div style="font-size:10.4pt"><b>Map the sections as you listen.</b> Write a letter in each box. Leave extra boxes empty.</div>'
            f'<div class="row" style="gap:4pt;flex:none;height:0.55in" data-fboxes="8">{boxes}</div>'
            f'<div class="wbox" style="padding:5pt 8pt"><div class="lab">What changed from the section before? (Track B)</div>'
            f'<table class="chg" style="width:100%;border-collapse:collapse;font-size:10pt"><tr><th style="width:80pt"></th>{th}</tr>{trs}</table></div>'
            f'<div class="wbox" style="flex:1">{trk("A")}<p class="pr">Use boxes 1 to 5. Write a letter in each. Which section was your favorite? Letter: ____ Why?</p>{wl(1)}</div>'
            f'<div class="wbox" style="flex:1.1">{trk("B")}<p class="pr">Map up to 8 sections and mark what changed above. Name the form (such as AB or ABA). What told you a new section had started?</p>{wl(2)}<div class="grow"></div></div></div>')
    return page("r7", body, wm, tag="RESPONSE 7", tagline="of 10 · Form map", student=True, piece=True)


def r8(wm):
    feats = [("Title", "and composer or performer, if you know them"), ("Tempo", "largo to presto"), ("Dynamics", "p, mp, mf or f; any changes?"), ("Instruments", "families and timbre words"),
             ("Mood", "one or two words"), ("Melody shape", "rise, fall, arch, valley, wave or level"), ("Beat", "2, 3 or 4 in a group")]
    rows = "".join(f'<tr><td class="f">{a}<small>{b}</small></td><td style="height:17pt"></td><td></td></tr>' for a, b in feats)
    gl = f'<tr><td class="f">Glyphs<small>check the ones you noticed</small></td><td style="height:26pt">{gl_mini()}</td><td>{gl_mini()}</td></tr>'
    body = (f'<div class="rb"><div style="font-size:10.4pt">Listen to two pieces. Fill in a column for each. The teacher chooses the music.</div>'
            f'<table class="cmp" data-cmp="1"><tr><th style="width:1.3in">Feature</th><th>Piece 1</th><th>Piece 2</th></tr>{rows}{gl}</table>'
            f'<div class="row"><div class="wbox"><div class="lab">Alike</div>{wl(1)}</div><div class="wbox"><div class="lab">Different</div>{wl(1)}</div></div>'
            f'<div class="wbox" style="flex:1">{trk("A")}<p class="pr">Finish: <b>Both pieces are</b> ______________. <b>One difference is</b> ______________.</p>{wl(1)}</div>'
            f'<div class="wbox" style="flex:1.1">{trk("B")}<p class="pr">Write two sentences that compare the pieces. Use <i>both</i>, <i>but</i> and <i>while</i>, and name a musical detail as evidence.</p>{wl(2)}<div class="grow"></div></div></div>')
    return page("r8", body, wm, tag="RESPONSE 8", tagline="of 10 · Compare", student=True)


def r9(wm):
    heads = "".join(f'<th style="width:0.3in">{glyph_svg(k)}</th>' for k, *_ in GLYPHS)
    rows = "".join('<tr><td></td><td></td><td></td>' + "".join('<td><i class="cb"></i></td>' for _ in GLYPHS) + '<td></td></tr>' for _ in range(12))
    body = (f'<div class="rb" style="gap:6pt"><div class="row" style="gap:10pt;align-items:flex-start"><div style="font-size:10pt;line-height:1.3"><b>{trk("A").replace("<div class=\"trk\">", "<div class=\"trk\" style=\"margin:0\">")}</b>Write one short sentence about each piece.</div>'
            f'<div style="font-size:10pt;line-height:1.3">{trk("B").replace("<div class=\"trk\">", "<div class=\"trk\" style=\"margin:0\">")}Use a vocabulary word in each response ({pgs("vocab1", "vocab2")}).</div></div>'
            f'<table class="log" data-rows="12"><tr class="lh"><th style="width:0.75in">Date</th><th style="width:1.7in">Piece</th><th style="width:1.35in">Composer or performer</th>{heads}<th>My 1-line response</th></tr>{rows}</table>'
            f'<div class="small" style="font-size:8.5pt">Check a glyph box when you noticed it: {", ".join(GLYPH_NAMES[:-1])} or {GLYPH_NAMES[-1]}. The glyph key is on {pg("gkey")}.</div></div>')
    return page("r9", body, wm, tag="RESPONSE 9", tagline="of 10 · Listening log", student=True)


def r10(wm):
    body = (f'<div class="rb"><div class="wbox" style="padding:6pt 10pt;flex:1.35"><div class="lab">Reflection</div>'
            f'<div class="scale" style="margin:2pt 0 4pt">How well did I listen? '
            + "".join(f'<span><span class="sn">{i}</span>{t}</span>' for i, t in ((1, "not yet"), (2, "a little"), (3, "mostly"), (4, "very well"))) +
            f'</div><div class="scale" style="margin:0 0 4pt;gap:8pt">Glyph I used most:'
            + "".join(f'<span style="display:inline-flex;align-items:center;gap:4pt;font-family:Oswald;font-weight:700;text-transform:uppercase;font-size:10pt"><span style="width:0.3in;display:block">{glyph_svg(k)}</span>{n}<i class="cb" style="margin:0"></i></span>' for k, n, *_ in GLYPHS) +
            f'</div>{trk("A")}<p class="pr" style="margin:0">One thing I noticed was ____________. Next time I want to listen for ____________.</p>{wl(1)}'
            f'{trk("B")}<p class="pr" style="margin:0">What did I learn about listening today? What will I listen for next time, and which vocabulary word will help me say it?</p>{wl(2)}<div class="grow"></div></div>'
            f'<div class="cut"><span>cut here</span></div>'
            f'<div class="ticket"><div class="lab" style="font-family:Oswald;font-weight:700;text-transform:uppercase;font-size:12pt">Exit ticket <span style="font-weight:300;text-transform:none;font-size:10pt">Name ________________ Piece ________________</span></div>'
            f'<div class="row" style="flex:none;margin-top:3pt"><div>{trk("A")}<p class="pr" style="margin:0">1. I heard ______________________</p>{wl(1)}<p class="pr" style="margin:0">2. I felt ______________________</p>{wl(1)}'
            f'<p class="pr" style="margin:0">3. A new word I can use: ____________</p></div>'
            f'<div>{trk("B")}<p class="pr" style="margin:0"><b>3</b> things I heard:</p>{wl(2)}<p class="pr" style="margin:0"><b>2</b> vocabulary words I used: _____________ and _____________</p>'
            f'<p class="pr" style="margin:3pt 0 0"><b>1</b> question I still have:</p>{wl(1)}</div></div></div></div>')
    return page("r10", body, wm, tag="RESPONSE 10", tagline="of 10 · Reflection", student=True, piece=True)


def vocab_page(key, groups, wm=False):
    parts = []
    for g in groups:
        rows = [v for v in V if v[0] == g]
        parts.append(f'<tr class="vg"><td colspan="3">{g}<span>{len(rows)} words</span></td></tr>')
        for _, w, say, d in rows:
            gly = ""
            d_ = [x for x in DYN if x[1] == w]
            if d_:
                gly = f'<span class="bv" data-dyn="{d_[0][0]}" data-g="{d_[0][3]:X}">{chr(d_[0][3])}</span>'
            parts.append(f'<tr data-word="{w}"><td class="w">{w}{gly}</td><td class="s">{escape(say) if say else "&nbsp;"}</td><td>{escape(d)}</td></tr>')
    n = sum(1 for v in V if v[0] in groups)
    body = (f'<table class="vt" style="margin-top:8pt" data-count="{n}"><tr><th style="width:1.6in">Word</th><th style="width:1.3in">Say it</th><th>What it means</th></tr>{"".join(parts)}</table>')
    return page(key, body, wm, tag="VOCABULARY", tagline=f"{NV} words · {1 if key == 'vocab1' else 2} of 2")


def rubric_page(wm=False):
    chk = "".join(f'<tr><td style="width:292pt">{a}</td><td style="text-align:center">{", ".join(str(P[k]) for k in ks)}</td><td style="text-align:center;width:40pt"><i class="cb" style="margin:0"></i></td>'
                  f'<td style="text-align:center;width:46pt"><i class="cb" style="margin:0"></i></td><td style="text-align:center;width:44pt"><i class="cb" style="margin:0"></i></td></tr>' for a, ks in CHECKS)
    rub = "".join(f'<tr><td class="c">{a}</td><td>{b}</td><td>{c}</td><td>{d}</td><td>{e}</td></tr>' for a, b, c, d, e in RUB_CRITERIA)
    sc = " · ".join(f"<b>{a}</b> {b}" for a, b in SCALE)
    body = (f'<h2 style="margin-top:8pt">Part 1: Self-check for students</h2><p>Mark how sure you are. The pages listed show where to practice.</p>'
            f'<table class="rbt"><tr><th>I can...</th><th style="width:44pt">Page</th><th style="width:40pt">Yes</th><th style="width:46pt">Almost</th><th style="width:44pt">Not yet</th></tr>{chk}</table>'
            f'<h2>Part 2: Teacher rubric for any response page ({RUB_TOTAL} points)</h2><p>Score each row from 0 to {RUB_MAX}. Use the same rubric for Track A and Track B. For Track A, expect one detail and a simple reason. For Track B, expect two details and a clear reason.</p>'
            f'<table class="rbt"><tr><th style="width:80pt">Row</th><th>3 points</th><th>2 points</th><th>1 point</th><th style="width:60pt">0 points</th></tr>{rub}'
            f'<tr><td colspan="5" style="text-align:right"><b>Total: ___ / {RUB_TOTAL}</b></td></tr></table>'
            f'<h2>Part 3: Score guide (out of {RUB_TOTAL})</h2><p>{sc}</p>'
            f'<h2>Conferring prompts</h2><ul><li>What did you hear that made you say that?</li><li>Which vocabulary word could say it more exactly?</li><li>Listen again: did it change?</li></ul>'
            f'')
    return page("rubric", body, wm, tag="ASSESS", tagline="Self-check and rubric")


def terms_page(wm=False):
    body = (f'{doc_head("Terms of Use", "Thank you for your purchase!")}'
            f'<p>© {YEAR} {STORE}. {BRAND} by {STORE}. All rights reserved. This purchase gives <b>one teacher</b> a license to use this resource with their own students.</p>'
            f'<h2>You may</h2><ul><li>Print and copy pages for your own classroom and students, year after year.</li>'
            f'<li>Share pages with your own students through a password-protected class site or learning platform.</li>'
            f'<li>Use the pages with your own students when you have a substitute teacher.</li></ul>'
            f'<h2>You may not</h2><ul><li>Share, email or copy this resource for other teachers, a whole school or a district. Additional licenses are available on Teachers Pay Teachers.</li>'
            f'<li>Post any part of it on a public website, shared drive or social media.</li>'
            f'<li>Sell, give away or claim any part of it as your own, or edit it into a new product.</li></ul>'
            f'<h2>Questions?</h2><p>Please use the Q&amp;A tab on the {BRAND} by {STORE} store on Teachers Pay Teachers. If something looks wrong, let me know there and I will fix it.</p>'
            f'<h2>Credits</h2><ul>'
            f'<li>The response pages, listening glyphs, vocabulary bank and rubric are original work, {BRAND} by {STORE}.</li>'
            f'<li>The cover headphones illustration is made with AI tools. The glyphs, notation, drawings and text are drawn in code.</li>'
            f'<li>Text fonts: Oswald (The Oswald Project Authors) and Source Sans 3 (Adobe), SIL Open Font License 1.1. Music font: Bravura © Steinberg Media Technologies GmbH, SIL Open Font License 1.1.</li></ul>'
            f'<h2>Printing tips</h2><ul><li>All pages print clearly in black and white. Print the stamp sheet on card stock or sticker paper if you like.</li>'
            f'<li>Keep your own copy of the rubric ({pg("rubric")}). Copy the response pages one at a time, as many as you need.</li></ul>'
            f'<h2>What is in this file ({TOTAL_PAGES} pages)</h2><p>Page 1 cover, page {P["teach"]} teacher notes, page {P["guide"]} prompt guide and pacing, page {P["gkey"]} glyph key, '
            f'page {P["gstamp"]} glyph stamps, pages {P["r1"]}–{P["r10"]} response pages, pages {P["vocab1"]}–{P["vocab2"]} vocabulary bank, page {P["rubric"]} self-check and rubric and page {P["terms"]} these terms.</p>'
            f'<p class="small">{DISCLOSURE}</p>')
    return page("terms", body, wm, tag="TERMS", tagline="Please read")


RFUNC = {"r1": r1, "r2": r2, "r3": r3, "r4": r4, "r5": r5, "r6": r6, "r7": r7, "r8": r8, "r9": r9, "r10": r10}


def make_page(key, wm=False):
    if key == "cover":
        return cover_page()
    if key in RFUNC:
        return RFUNC[key](wm)
    return {"teach": teach_page, "guide": guide_page, "gkey": gkey_page, "gstamp": gstamp_page, "vocab1": lambda w: vocab_page("vocab1", VOCAB_GROUP_ORDER_P1, w),
            "vocab2": lambda w: vocab_page("vocab2", VOCAB_GROUP_ORDER_P2, w), "rubric": rubric_page, "terms": terms_page}[key](wm)


def full_pages():
    XREFS.clear()
    out = [make_page(k) for k in ORDER]
    assert len(out) == TOTAL_PAGES
    return out


PREVIEW_KEYS = ["gkey", "r3", "r6", "vocab1"]


def preview_pages():
    return [make_page(k, True) for k in PREVIEW_KEYS]


# ================================================================== square images
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


def cover_square():
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div>'
        f'<div style="flex:1;display:flex;flex-direction:column;justify-content:space-evenly;align-items:center;width:100%;padding:0 0 76px">'
        f'<div style="height:420px;display:flex;align-items:center"><img src="../art/hero.png" alt="" style="display:block;height:440px;width:auto"></div>'
        f'<div><div class="hd" style="font-size:66px">Listening Journal</div><div class="hd" style="font-size:124px">&amp; Glyphs</div>'
        f'<div class="sub" style="font-size:28px;margin-top:12px">10 reusable response pages, 4 listening glyphs, {NV} vocabulary words</div></div>'
        f'</div><div class="band">Grades 2–8 <em>·</em> 10 response pages <em>·</em> {TOTAL_PAGES} pages</div></div>')


def preview_square_1(img):
    caps = [(PAGE_NAMES["r3"], "Tempo words and dynamics symbols"), (PAGE_NAMES["r5"], "Draw the contour of the melody"), (PAGE_NAMES["r6"], "Beats in 2, 3 and 4 on a staff")]
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div><div class="hd" style="font-size:72px;margin-top:28px">Ten pages for any piece</div>'
        f'<div class="sub" style="font-size:29px;margin-top:10px">Two prompt tracks on every page: grades 2–4 and 5–8</div>'
        f'<div style="flex:1;display:flex;flex-direction:column;align-items:center;justify-content:space-evenly;padding-bottom:70px">'
        f'<div style="display:flex;gap:22px;align-items:flex-start">{trio(img, caps)}</div>{pill_row(["10 response pages", "Track A", "Track B"])}</div>'
        f'{swm_over(230)}<div class="band">Teacher chooses the music <em>·</em> no prep</div></div>')


def preview_square_2(a, b):
    pair = "".join(f'<div style="width:380px">{shot(src, 380)}<div class="lbl">{lab}<span>{sub}</span></div></div>'
                   for src, lab, sub in ((a, PAGE_NAMES["gkey"], "Four quick-response pictures"), (b, PAGE_NAMES["vocab1"], f"{NV} words in {len(GROUPS)} groups")))
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div><div class="hd" style="font-size:72px;margin-top:24px">Glyphs and vocabulary</div>'
        f'<div class="sub" style="font-size:27px;margin-top:8px">Stamp what you hear, then say it with the right word</div>'
        f'<div style="flex:1;display:flex;align-items:center;padding-bottom:70px"><div style="display:flex;gap:44px;align-items:flex-start">{pair}</div></div>'
        f'{swm_over(230)}<div class="band">4 glyphs <em>·</em> {NV} words <em>·</em> self-check and rubric</div></div>')


def preview_square_3():
    chips = "".join(f'<div class="tc"><small>{i + 1}</small><div>{escape(t)}<span>{escape(fo)}</span></div></div>' for i, (k, t, fo, *_r) in enumerate(RESP))
    gts = "".join(f'<div class="gtl">{glyph_svg(k)}<b>{n}</b><span>{sub}</span></div>' for k, n, sub, *_ in GLYPHS)
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div><div class="hd" style="font-size:72px;margin-top:28px">Everything inside</div>'
        f'<div class="sub" style="font-size:27px;margin-top:10px">10 response pages and 4 listening glyphs</div>'
        f'<div style="flex:1;display:flex;flex-direction:column;align-items:center;justify-content:space-evenly;padding-bottom:70px"><div style="display:flex;gap:24px">{gts}</div>'
        f'<div class="tg">{chips}</div>'
        f'{pill_row(["Teacher notes", "Pacing", "Rubric"])}</div>'
        f'{swm_over(230)}<div class="band">Reflect <em>·</em> compare <em>·</em> log <em>·</em> map the form</div></div>')


# ================================================================== render / build
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


PAGE_LIST = [("Cover", 1), ("Teacher notes", 1), ("Prompt guide and pacing", 1), ("Listening glyph key", 1), ("Glyph stamp sheet, 24 cut-out stamps", 1),
             ("Response pages, 10 reusable pages", 10), (f"Vocabulary bank, {NV} words", 2), ("Self-check and rubric", 1), ("Terms of use and credits", 1)]
assert sum(c for _, c in PAGE_LIST) == TOTAL_PAGES, sum(c for _, c in PAGE_LIST)


def upload_md():
    lst = "\n".join(f"- {n}: {c}" for n, c in PAGE_LIST)
    return f"""# UPLOAD: {LISTING_TITLE} (TpT 071)

These fields follow the order of TpT's "Add a resource" form. Evergreen item: no season, any month of the school year.

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
Listening Journal and Listening Glyphs gives you 10 reusable response pages that work with any piece of music you choose. There are no named recordings or copyrighted works in the pages, so you can use them with a classroom performance, a recording or a concert. Every page has two prompt tracks: Track A for grades 2-4 and Track B for grades 5-8, so one set serves a whole school.

THE 10 RESPONSE PAGES
1. First Listen: what do I hear and feel?
2. Instruments and Families: a checklist and timbre words
3. Tempo and Dynamics: largo, andante, moderato, allegro, presto; piano, mezzo piano, mezzo forte, forte, crescendo and decrescendo, with the symbols drawn correctly
4. Mood and Character: 24 mood words
5. Melody Shape: draw the contour on high, middle and low lines
6. Beat and Meter: circle 2, 3 or 4, tap the beat, with beat examples on a staff
7. Form Map: blank A, B and C boxes
8. Compare Two Pieces: a two-column table
9. Listening Log: date, piece, composer and a 1-line response, 12 rows
10. Reflection and Exit Ticket

4 LISTENING GLYPHS
Simple original picture icons for Contour (melody contour), Pulse (rhythm and beat), Dynamics and Timbre (instrument color). Students draw, stamp or circle a glyph as a quick response. The pack has a glyph key and a stamp sheet of 24 cut-out stamps.

VOCABULARY BANK
{NV} kid-friendly words in {len(GROUPS)} groups: beat and rhythm, tempo, melody and pitch, dynamics, instruments and sound, and form and texture, with pronunciations for the Italian terms.

WHAT'S INCLUDED ({TOTAL_PAGES} pages, PDF, US Letter)
• Cover (1 page)
• Teacher notes (1 page)
• Prompt guide and pacing, with a 10-week sequence (1 page)
• Listening glyph key (1 page)
• Glyph stamp sheet (1 page)
• Response pages (10 pages)
• Vocabulary bank (2 pages)
• Self-check and rubric (1 page)
• Terms of use and credits (1 page)
Total: {TOTAL_PAGES} pages.

HOW TO USE
Choose any music, set one listening focus, play it one to three times and have students respond on the matching page. A 10-minute routine is in the teacher notes. Copy the pages as often as you like for your own students, slide them into sleeves for dry-erase markers, or staple them into a journal.

• Grades 2-8 (Track A for grades 2-4, Track B for grades 5-8)
• Works with any music: no answer keys are needed
• Prints well in black and white

{DISCLOSURE}
```

## 3. Grades

Four entries: 2nd, 4th, 6th and 8th grade. The product is for grades 2-8 (Track A for grades 2-4, Track B for grades 5-8), but TpT allows only four grade entries, so they are spread across the range. The listing title says Gr 2-8.

## 4. Subjects and tags

- Subjects: {", ".join(SUBJECTS)}
- Tags: {", ".join(TAGS)}

## 5. Page count by section (totals {TOTAL_PAGES})

{lst}
- Total: {TOTAL_PAGES}

## 6. Standards

None cited by code. The teacher notes name the Responding processes of the National Core Arts Standards for Music (MU:Re7.1, MU:Re8.1 and MU:Re9.1) in general terms and ask teachers to match them to their own curriculum.

## 7. Price

**${PRICE}** (paid; owner range $3-5).

## 8. Preview

Paid. Preview PDF: the listening glyph key (page {P["gkey"]}), response page 3, tempo and dynamics (page {P["r3"]}), response page 6, beat and meter (page {P["r6"]}) and vocabulary bank 1 (page {P["vocab1"]}), all watermarked.

## 9. Before you click publish

- Evergreen: no season check needed.
- Repertoire-free: no recording, composer or copyrighted work is named; the teacher picks the music.
- Art: the cover headphones are made with AI tools (the disclosure line covers it); the glyphs, notation, tables and drawing spaces are drawn in code.
- No answer keys: every page is a response page. There is no matching activity.
- Open owner question: logo beside HUDSON BEAT (see tpt/STYLE.md).
"""


def tpt_json():
    return {"price": PRICE, "license_price": PRICE, "tax_code": "Other Digital Goods - No Physical Media", "grades": GRADES, "subjects": SUBJECTS, "tags": TAGS,
            "formats": ["PDF"], "pages": TOTAL_PAGES, "answer_key": "Not Included",
            "files": {"product": f"{SLUG}.pdf", "preview": f"{SLUG}-PREVIEW.pdf", "thumb1": "cover.png", "thumb2": "preview-1.png", "thumb3": "preview-2.png", "thumb4": "preview-3.png"}}


SHOT_KEYS = ["r3", "r5", "r6", "gkey", "vocab1"]


def build():
    os.makedirs(BUILD, exist_ok=True)
    full = write("resource.html", html_doc(full_pages(), TITLE))
    prev = write("preview.html", html_doc(preview_pages(), "Preview"))
    render([{"html": full, "pdf": PDF}, {"html": prev, "pdf": PREVIEW_PDF}])
    for k in SHOT_KEYS:
        subprocess.run(["pdftoppm", "-png", "-r", "150", "-f", str(P[k]), "-l", str(P[k]), "-singlefile", PDF, os.path.join(BUILD, f"pg-{k}")], check=True)
    sq = [write("cover.html", cover_square()),
          write("p1.html", preview_square_1(["pg-r3.png", "pg-r5.png", "pg-r6.png"])),
          write("p2.html", preview_square_2("pg-gkey.png", "pg-vocab1.png")),
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

# Independent truth tables (typed again, not imported from the DATA section)
T_TEMPO = ["largo", "andante", "moderato", "allegro", "presto"]                       # slowest to fastest
T_TEMPO_WORDS = {"largo": "slow", "andante": "walk", "moderato": "medium", "allegro": "fast", "presto": "very fast"}
T_DYN = [("p", 0xE520, "soft"), ("mp", 0xE52C, "medium soft"), ("mf", 0xE52D, "medium loud"), ("f", 0xE522, "loud")]   # softest to loudest (SMuFL code points)
T_PAGES = {"melody shape": 10, "beat and meter": 11, "tempo and dynamics": 8, "instruments": 7}
T_GLYPHS = ["Contour", "Pulse", "Dynamics", "Timbre"]
T_FAMILY_OF = {"violin": "Strings", "viola": "Strings", "cello": "Strings", "double bass": "Strings", "guitar": "Strings", "harp": "Strings",
               "flute": "Woodwinds", "clarinet": "Woodwinds", "oboe": "Woodwinds", "bassoon": "Woodwinds", "saxophone": "Woodwinds", "recorder": "Woodwinds",
               "trumpet": "Brass", "trombone": "Brass", "French horn": "Brass", "tuba": "Brass",
               "snare drum": "Percussion", "bass drum": "Percussion", "cymbals": "Percussion", "xylophone": "Percussion", "timpani": "Percussion", "tambourine": "Percussion"}


def fl(el, k, d=0.0):
    return float(el.get(k, d))


def nums(d):
    v = [float(x) for x in re.findall(r"-?\d+(?:\.\d+)?", d)]
    return list(zip(v[0::2], v[1::2]))


def check_svg_extent(sv, label, errs):
    vb = [float(x) for x in sv.get("viewbox").split()]
    W_, H_ = vb[2], vb[3]
    for el in sv.iter():
        sw = fl(el, "stroke-width") if el.get("stroke") not in (None, "none") else 0.0
        tag = el.tag
        if tag == "line":
            xs, ys = [fl(el, "x1"), fl(el, "x2")], [fl(el, "y1"), fl(el, "y2")]
        elif tag == "rect":
            xs, ys = [fl(el, "x"), fl(el, "x") + fl(el, "width")], [fl(el, "y"), fl(el, "y") + fl(el, "height")]
        elif tag == "circle":
            r = fl(el, "r")
            xs, ys = [fl(el, "cx") - r, fl(el, "cx") + r], [fl(el, "cy") - r, fl(el, "cy") + r]
        elif tag == "polyline":
            p = nums(el.get("points"))
            xs, ys = [q[0] for q in p], [q[1] for q in p]
        elif tag == "path":
            p = nums(el.get("d"))
            xs, ys = [q[0] for q in p], [q[1] for q in p]
        else:
            continue
        pad = max(sw, 3.0)
        if min(xs) - sw / 2 < pad - 1e-6 or min(ys) - sw / 2 < pad - 1e-6 or max(xs) + sw / 2 > W_ - pad + 1e-6 or max(ys) + sw / 2 > H_ - pad + 1e-6:
            errs.append(f"{label}: a {tag} (stroke {sw}) is closer than max(stroke, 3) to the viewBox edge")


def bez_pts(d):
    """Sample a path made of M, C and Z with absolute coordinates."""
    toks = re.findall(r"[MCZ]|-?\d+(?:\.\d+)?", d)
    pts, i, cur = [], 0, None
    while i < len(toks):
        t = toks[i]
        if t == "M":
            cur = (float(toks[i + 1]), float(toks[i + 2]))
            pts.append(cur)
            i += 3
        elif t == "C":
            i += 1
            while i < len(toks) and toks[i] not in "MCZ":
                p1, p2, p3 = [(float(toks[i + j]), float(toks[i + j + 1])) for j in (0, 2, 4)]
                for k in range(1, 21):
                    u = k / 20
                    x = (1 - u) ** 3 * cur[0] + 3 * (1 - u) ** 2 * u * p1[0] + 3 * (1 - u) * u * u * p2[0] + u ** 3 * p3[0]
                    y = (1 - u) ** 3 * cur[1] + 3 * (1 - u) ** 2 * u * p1[1] + 3 * (1 - u) * u * u * p2[1] + u ** 3 * p3[1]
                    pts.append((x, y))
                cur = p3
                i += 6
        else:
            i += 1
    return pts


def check_glyph(sv, errs):
    k = sv.get("data-glyph")
    art = [e for e in sv.iter() if "art" in (e.get("class") or "").split()]
    if k == "contour":
        path = [e for e in art if e.tag == "path"][0]
        pts = bez_pts(path.get("d"))
        ys = [p[1] for p in pts]
        i_top = ys.index(min(ys))
        if not (pts[0][1] > 60 and pts[-1][1] < 40):
            errs.append("contour glyph: should start low and end high")
        if not (pts[0][0] < pts[-1][0] and all(pts[i][0] <= pts[i + 1][0] + 1e-9 for i in range(len(pts) - 1))):
            errs.append("contour glyph: the line must run left to right")
        if i_top in (0, len(pts) - 1) or not any(pts[j][1] > pts[j + 1][1] + 0.5 for j in range(len(pts) - 1)):
            pass
        circ = [e for e in art if e.tag == "circle"]
        if len(circ) != 2:
            errs.append("contour glyph: expected two end dots")
    elif k == "pulse":
        bars = [e for e in art if e.tag == "line"]
        if len(bars) != 4:
            errs.append("pulse glyph: expected 4 bars")
        else:
            xs = [fl(b, "x1") for b in bars]
            tops = [min(fl(b, "y1"), fl(b, "y2")) for b in bars]
            bots = {max(fl(b, "y1"), fl(b, "y2")) for b in bars}
            gaps = {round(xs[i + 1] - xs[i], 3) for i in range(3)}
            if len(gaps) != 1 or len(bots) != 1 or not (tops[0] < tops[1] == tops[2] == tops[3]):
                errs.append("pulse glyph: bars must be evenly spaced, share a bottom and have a taller first bar")
    elif k == "dynamics":
        ln = [e for e in art if e.tag == "line"]
        if len(ln) != 2:
            errs.append("dynamics glyph: expected 2 hairpin lines")
        else:
            a, b = ln
            left = {(fl(a, "x1"), fl(a, "y1")), (fl(b, "x1"), fl(b, "y1"))}
            if len(left) != 1 or fl(a, "x2") != fl(b, "x2") or abs(fl(a, "y2") - fl(b, "y2")) < 30 or fl(a, "x2") <= fl(a, "x1"):
                errs.append("dynamics glyph: must be a crescendo hairpin that opens to the right")
    elif k == "timbre":
        paths = [e for e in art if e.tag == "path"]
        if len(paths) != 2 or not paths[0].get("d").strip().endswith("Z"):
            errs.append("timbre glyph: expected a closed drop and a wave")
    else:
        errs.append(f"unknown glyph {k}")


def verify_html():
    errs = []
    doc = LH.fromstring(open(os.path.join(BUILD, "resource.html"), encoding="utf-8").read())
    pages = {p.get("data-k"): p for p in doc.xpath('//section[contains(@class,"page")]')}
    if list(pages) != ORDER:
        errs.append("page order in the HTML differs from ORDER")
    # ---- every svg: padding
    for key, p in pages.items():
        for n, sv in enumerate(p.iter("svg")):
            check_svg_extent(sv, f"page {P[key]} svg {n + 1}", errs)
    # ---- glyphs
    for key, p in pages.items():
        for sv in p.xpath('.//svg[@data-glyph]'):
            check_glyph(sv, errs)
    gk = pages["gkey"]
    names = [b.xpath('.//h3')[0].text.strip() for b in gk.xpath('.//div[contains(@class,"gk")]')]
    if names != T_GLYPHS:
        errs.append(f"glyph key lists {names}")
    stamp = pages["gstamp"]
    tiles = stamp.xpath('.//div[contains(@class,"tile")]')
    cnt = {}
    for t in tiles:
        cnt[t.get("data-glyph")] = cnt.get(t.get("data-glyph"), 0) + 1
        nm = t.xpath('.//b')[0].text_content()
        if nm.lower() != t.get("data-glyph").lower() and not (t.get("data-glyph"), nm) in (("contour", "Contour"),):
            errs.append(f"stamp tile name {nm} does not match its glyph {t.get('data-glyph')}")
    if len(tiles) != 24 or sorted(cnt.values()) != [6, 6, 6, 6]:
        errs.append(f"stamp sheet has {len(tiles)} tiles {cnt}")
    for key in ("teach", "gkey", "r10"):
        t = pages[key].text_content()
        for g in T_GLYPHS:
            if g.lower() not in t.lower():
                errs.append(f"page {P[key]} does not name the glyph {g}")
    for key in ("r1", "r8", "r9", "r10"):
        if not pages[key].xpath('.//svg[@data-glyph="contour"]'):
            errs.append(f"page {P[key]} has no glyphs")
    # ---- hairpins: crescendo opens right, decrescendo closes right
    hp = [sv for p in pages.values() for sv in p.xpath('.//svg[@data-icon]')]
    if len(hp) != 2:
        errs.append(f"expected 2 hairpins, found {len(hp)}")
    for sv in hp:
        ln = sv.xpath('.//line')
        a, b = ln
        kind = sv.get("data-icon")
        L = [(fl(x, "x1"), fl(x, "y1")) for x in ln]
        R = [(fl(x, "x2"), fl(x, "y2")) for x in ln]
        if kind == "hairpin-open" and not (L[0] == L[1] and R[0][0] == R[1][0] and abs(R[0][1] - R[1][1]) > 10 and R[0][0] > L[0][0]):
            errs.append("crescendo hairpin does not open to the right")
        if kind == "hairpin-close" and not (R[0] == R[1] and L[0][0] == L[1][0] and abs(L[0][1] - L[1][1]) > 10 and R[0][0] > L[0][0]):
            errs.append("decrescendo hairpin does not close to the right")
    r3p = pages["r3"]
    ch = r3p.xpath('.//table[@data-change]')[0]
    cells = ch.xpath('.//td[svg]')
    if [c.xpath('.//svg')[0].get("data-icon") for c in cells] != ["hairpin-open", "hairpin-close"] or "crescendo" not in cells[0].text_content() or "decrescendo" not in cells[1].text_content() \
            or "louder" not in cells[0].text_content() or "softer" not in cells[1].text_content():
        errs.append("hairpin labels on page 8 do not match their drawings")
    # ---- tempo order and meanings
    tp = r3p.xpath('.//div[@data-tempo]')
    if [t.get("data-tempo") for t in tp] != T_TEMPO:
        errs.append("tempo scale is not ordered slowest to fastest")
    for t in tp:
        if T_TEMPO_WORDS[t.get("data-tempo")] not in t.text_content().lower():
            errs.append(f"tempo {t.get('data-tempo')} has a wrong meaning: {t.text_content()}")
    # ---- dynamics order, symbols and meanings
    dy = r3p.xpath('.//table[@data-dyn]')[0].xpath('.//th[span]')
    if len(dy) != 4:
        errs.append("dynamics header does not have 4 symbols")
    for th, (sym, cp, mean) in zip(dy, T_DYN):
        sp = th.xpath('.//span[@data-dyn]')[0]
        if sp.get("data-dyn") != sym or ord(sp.text) != cp or f"{mean}" not in th.text_content():
            errs.append(f"dynamics header for {sym} is wrong")
    names_ = ["piano", "mezzo piano", "mezzo forte", "forte"]
    for th, n in zip(dy, names_):
        if n not in th.text_content():
            errs.append(f"dynamics header lacks {n}")
    for key in ("vocab1", "vocab2"):
        for sp in pages[key].xpath('.//span[@data-dyn]'):
            want = {s: c for s, c, _ in T_DYN}[sp.get("data-dyn")]
            if ord(sp.text) != want:
                errs.append("vocabulary dynamics symbol has the wrong code point")
            row = sp.xpath('ancestor::tr')[0]
            w = row.get("data-word")
            if {"piano": "p", "mezzo piano": "mp", "mezzo forte": "mf", "forte": "f"}[w] != sp.get("data-dyn"):
                errs.append(f"vocabulary: {w} shows the symbol {sp.get('data-dyn')}")
            if f"The symbol is {sp.get('data-dyn')}." not in row.text_content():
                errs.append(f"vocabulary: {w} definition does not state its symbol")
    # ---- beat staves
    bts = pages["r6"].xpath('.//svg[@data-beats]')
    if [int(b.get("data-beats")) for b in bts] != [2, 3, 4]:
        errs.append("beat page must show 2, 3 and 4 beats")
    for b in bts:
        n, sp, mid = int(b.get("data-beats")), float(b.get("data-sp")), float(b.get("data-mid"))
        lines = sorted(fl(l, "y1") for l in b.xpath('.//line[@class="sl"]'))
        if len(lines) != 5 or abs(lines[2] - mid) > 0.02 or any(abs(lines[i + 1] - lines[i] - sp) > 0.02 for i in range(4)):
            errs.append(f"{n}-beat staff: staff lines are not 5 evenly spaced lines")
        heads = b.xpath('.//text[@class="nh"]')
        stems = b.xpath('.//rect[@class="stem"]')
        if len(heads) != n or len(stems) != n:
            errs.append(f"{n}-beat staff has {len(heads)} heads and {len(stems)} stems")
        for h, s_ in zip(heads, stems):
            if abs(fl(h, "y") - mid) > 0.02:
                errs.append("notehead is not on the middle line")
            if abs(fl(s_, "x") - fl(h, "x")) > 0.02:
                errs.append("stem is not on the left edge of its notehead")
            top = fl(s_, "y")
            if not (mid - 0.3 * sp <= top <= mid + 0.1 * sp) or fl(s_, "height") < 3 * sp:
                errs.append("stem must start at the notehead and go down at least 3 spaces")
        for t in b.xpath('.//text[@class="tsn"]'):
            if ord(t.text) != 0xE080 + n or int(t.get("data-n")) != n:
                errs.append(f"{n}-beat staff: wrong time signature top number")
        if ord(b.xpath('.//text[@class="tsd"]')[0].text) != 0xE084:
            errs.append("time signature bottom number is not 4")
        if [t.text for t in b.xpath('.//text[@class="cnt"]')] != [str(i + 1) for i in range(n)]:
            errs.append(f"{n}-beat staff: counting numbers are wrong")
        c0 = b.xpath('.//text[@class="cnt"]')
        if c0 and c0[0].get("font-weight") != "700":
            errs.append("beat 1 is not emphasized")
    # ---- contour shapes
    seen = {}
    for sv in pages["r5"].xpath('.//svg[@data-contour]'):
        nm = sv.get("data-contour")
        pts = nums(sv.xpath('.//polyline')[0].get("points"))
        ys = [p[1] for p in pts]
        xs = [p[0] for p in pts]
        if xs != sorted(xs):
            errs.append(f"contour {nm}: x must increase")
        up = [ys[i + 1] < ys[i] for i in range(len(ys) - 1)]    # svg y goes down the page: smaller y is higher
        dn = [ys[i + 1] > ys[i] for i in range(len(ys) - 1)]
        ok = {"rise": all(up), "fall": all(dn), "level": len(set(ys)) == 1,
              "arch": ys.index(min(ys)) not in (0, len(ys) - 1) and all(up[:ys.index(min(ys))]) and all(dn[ys.index(min(ys)):]),
              "valley": ys.index(max(ys)) not in (0, len(ys) - 1) and all(dn[:ys.index(max(ys))]) and all(up[ys.index(max(ys)):]),
              "wave": sum(1 for i in range(len(up) - 1) if up[i] != up[i + 1]) >= 3}[nm]
        if not ok:
            errs.append(f"contour shape {nm} does not draw its name")
        seen[nm] = 1
    if sorted(seen) != sorted(["rise", "fall", "arch", "valley", "wave", "level"]):
        errs.append("contour shapes missing")
    # ---- instrument families
    fam = pages["r2"].xpath('.//div[contains(@class,"fb")]')
    for fb in fam:
        fname = fb.xpath('.//b')[0].text
        for d in fb.xpath('./div'):
            item = d.text_content().strip()
            if item in T_FAMILY_OF and T_FAMILY_OF[item] != fname:
                errs.append(f"{item} is listed under {fname}, but it is a {T_FAMILY_OF[item]} instrument")
    listed = {d.text_content().strip() for fb in fam for d in fb.xpath('./div')}
    for item in T_FAMILY_OF:
        if item not in listed:
            errs.append(f"{item} is missing from the instrument checklist")
    # ---- other structure
    if len(pages["r4"].xpath('.//span[@class="chip"]')) != 24 or len(set(c.text for c in pages["r4"].xpath('.//span[@class="chip"]'))) != 24:
        errs.append("mood page must have 24 different words")
    if len(pages["r9"].xpath('.//table[@class="log"]//tr')) != 13:
        errs.append("listening log needs a header and 12 rows")
    if len(pages["r7"].xpath('.//div[@data-fboxes]/div')) != 8:
        errs.append("form map needs 8 boxes")
    cmpt = pages["r8"].xpath('.//table[@data-cmp]')[0]
    if len(cmpt.xpath('.//th')) != 3:
        errs.append("compare page needs 3 columns")
    # ---- vocabulary
    words = [v[1] for v in V]
    if NV != 40 or len(set(words)) != NV or len(words) != 40:
        errs.append("vocabulary bank must have 40 different words")
    sizes = {g: sum(1 for v in V if v[0] == g) for g in GROUPS}
    if sorted(sizes.values()) != [6, 6, 6, 7, 7, 8]:
        errs.append(f"vocabulary group sizes {sizes}")
    shown = [r.get("data-word") for key in ("vocab1", "vocab2") for r in pages[key].xpath('.//tr[@data-word]')]
    if sorted(shown) != sorted(words):
        errs.append("vocabulary pages do not show every word exactly once")
    for key in ("vocab1", "vocab2"):
        t = pages[key].xpath('.//table[@data-count]')[0]
        if int(t.get("data-count")) != len(t.xpath('.//tr[@data-word]')):
            errs.append(f"{key}: word count label differs from the rows")
    for w, m in TEMPO:
        if not DEF[w].lower().startswith(m.lower()):
            errs.append(f"tempo meaning on page 8 for {w} differs from the vocabulary bank")
    for k, n, m, cp in DYN:
        if not DEF[n].lower().startswith(m.lower()):
            errs.append(f"dynamics meaning on page 8 for {n} differs from the vocabulary bank")
    for w, m in DYN_MEAN.items():
        if not any(x in DEF[w].lower() for x in (("louder",) if w == "crescendo" else ("softer",))):
            errs.append(f"{w} meaning differs from the vocabulary bank")
    t_def = {w: DEF[w].lower() for w in T_TEMPO}
    for w in T_TEMPO:
        if T_TEMPO_WORDS[w] not in t_def[w]:
            errs.append(f"vocabulary definition of {w} is wrong")
    # ---- brand or repertoire names
    low = " ".join(p.text_content() for p in pages.values()).lower()
    for bad in ("beethoven", "mozart", "bach", "tchaikovsky", "vivaldi", "symphony no", "twinkle", "logic pro", "garageband", "spotify", "youtube"):
        if bad in low:
            errs.append(f"named work, composer or brand '{bad}' appears")
    # ---- cross-reference sentences use the true page numbers
    full = " ".join(p.text_content() for p in pages.values())
    for phrase, n in T_PAGES.items():
        for m in re.finditer(rf"{phrase} page \(page (\d+)\)", full):
            if int(m.group(1)) != n:
                errs.append(f"'{phrase} page' points to page {m.group(1)}, expected {n}")
    if P["r5"] != 10 or P["r6"] != 11 or P["r3"] != 8 or P["r2"] != 7:
        errs.append("response page numbers differ from the typed expectation")
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
      const BOX = '.wbox, .fb, .gk, .tile, .box, .top, .doc table, .doc p, .doc ul, .doc ol, .fbox, .draw, .ticket, .tempo, .chips, .scale';
      const FILL = '.wbox, .fb, .gk, .tile, .box, .fbox, .draw, .ticket, .tempo, table, .wl, .chips, .scale, .fam';
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
        pg.querySelectorAll('.wbox, .fb, .gk, .tile, .box, .ticket, .tempo, .fbox').forEach(bx => {
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
        pg.querySelectorAll('.rb > *, .doc > table, .doc > h2, .doc > p, .doc > ul, .doc > ol, .doc > .cols, .sg').forEach(e => { const r = e.getBoundingClientRect(); if (r.height) ys.push([r.top, r.bottom]); });
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
            if not re.search(r"oswald|sourcesans3|bravura", name.lower()):
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
    for i, t in enumerate(texts):
        for m in re.finditer(r"(?i)\bpages? (\d+)(?:[–-](\d+))?", t):
            a, b = int(m.group(1)), int(m.group(2) or m.group(1))
            if a < 1 or b > TOTAL_PAGES or b < a:
                errs.append(f"page {i + 1}: reference '{m.group(0)}' is outside the {TOTAL_PAGES}-page file")
    teach, terms, guide = texts[1], texts[TOTAL_PAGES - 1], texts[2]
    for need in ("pages 6–15", "page 3", "page 4", "page 5", "pages 16–17", "page 18", "page 14", "page 11"):
        if need not in teach:
            errs.append(f"teacher notes lack the reference '{need}'")
    if ("page 3 prompt guide" not in terms or "page 4 glyph key" not in terms or "page 5 glyph stamps" not in terms or "pages 6–15 response pages" not in terms
            or "pages 16–17 vocabulary bank" not in terms or "page 18 self-check and rubric" not in terms or "page 19 these terms" not in terms or "(19 pages)" not in terms.lower()):
        errs.append("terms page 'what is in this file' does not match the page numbers")
    # guide table: page numbers 6..15 in order with the right titles
    for k in RKEYS:
        if f"{P[k]} {RTITLE[k]}" not in guide:
            errs.append(f"prompt guide row for {RTITLE[k]} does not show page {P[k]}")
    for k, ks in zip(range(8), CHECKS):
        pass
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
    if re.search(r"winter|snow|holiday|christmas|december|halloween|thanksgiving|spring|summer|autumn|fall\b|new year|back to school", title, re.I):
        errs.append("UPLOAD.md: seasonal word in the title")
    for need in (DISCLOSURE, f"${PRICE}", f"{TOTAL_PAGES} pages", "Gr 2-8", "2nd, 4th, 6th and 8th", f"{NV} kid-friendly words"):
        if need not in up:
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
    if any(t not in tags or t in heads for t in tj["tags"]) or any(s_ not in subs or s_ in heads for s_ in tj["subjects"]):
        errs.append("tpt.json tags or subjects invalid")
    if tj.get("pages") != TOTAL_PAGES or tj["price"] != PRICE or not 1 <= len(tj["grades"]) <= 4:
        errs.append("tpt.json pages, price or grades mismatch")
    c = texts[0].lower()
    if f"{TOTAL_PAGES} pages" not in c or f"{NV}-word" not in c or "grades 2–8" not in c or "10 response pages" not in c or "4 glyphs" not in c:
        errs.append("cover text does not state the page count, word count, glyphs and grades")
    if DISCLOSURE not in terms or DISCLOSURE not in teach:
        errs.append("teacher notes or terms page lacks the disclosure line")
    allt = " ".join(texts).lower()
    for bad in ("colour", "favourite", "metre ", "analyse", "centre", "behaviour", "colour"):
        if bad in allt:
            errs.append(f"non-US spelling '{bad}'")
    for bad in ("qa ", "checker", "recomputed", "verified by code"):
        if bad in allt.replace("answer keys are verified", ""):
            errs.append(f"buyer-facing text contains internal wording '{bad}'")
    if "answer key" in allt.replace("answer keys are verified", ""):
        errs.append("an answer key is mentioned but this item has none")
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
    print("CHECK OK: tempo order largo to presto with meanings; dynamics p, mp, mf, f in order with SMuFL code points; crescendo hairpin opens right and decrescendo closes right; "
          "beat staves 2/4, 3/4, 4/4 (right number of notes, stems on the left edge going down from the middle line, counts); contour shapes; 4 glyph geometries; "
          "instrument families; 40 vocabulary words (unique, 6 groups) agree with page 8; cross-references, UPLOAD.md and tpt.json agree; drawing padding, footer gaps and blank bands clear; "
          f"PDF {TOTAL_PAGES} Letter pages, preview 4 (one watermark each); images 2000x2000 with clean edges.")


if __name__ == "__main__" and "--check" in sys.argv:
    check()
