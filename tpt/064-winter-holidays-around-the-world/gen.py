#!/usr/bin/env python3
"""Around the World, Music Edition: readings and listening response pages (TpT 064): build the resource and verify it.

    python3 gen.py           build everything (PDFs, PNGs, UPLOAD.md, tpt.json) into this folder
    python3 gen.py --check   re-read the rendered pages and verify every count, cross-reference, fact list and the layout

--check does not trust the lists in this file. It loads the rendered HTML in Chromium and reads back what is really on the pages
(every reading, question, prompt, principle, vocabulary card, rubric row, pacing step and page reference), then recomputes from that.
The facts themselves, with a source URL for each, are listed in QA.md.

Rendering uses Playwright + Chromium (HTML/SVG -> PDF/PNG) with the OFL fonts in ../fonts.
"""
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
ART = os.path.join(HERE, "art")
RENDER_JS = os.path.join(TPT, "tools", "render.js")

SLUG = "around-the-world-music-edition"
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
TINT = "#DCEBF7"
DISCLOSURE = "Created with the help of digital and AI tools. Notation and answer keys are verified before release."
TITLE = "Around the World"
LISTING_TITLE = "Music Listening Response & Readings, Around the World Music Edition, Gr 3-6"
PRICE = "5.00"
TAGS = ["Christmas-Chanukah-Kwanzaa", "Cultural Activities", "Worksheets", "Printables", "Activities"]
SUBJECTS = ["Music", "Instrumental Music", "Vocal Music"]
GRADES = ["3rd-grade", "4th-grade", "5th-grade", "6th-grade"]

# ------------------------------------------------------------------ content
# One list per celebration. Pages, notes, the answer key and the upload text all read from it. Sources: QA.md.
CELEBS = [
    dict(key="christmas", name="Christmas",
         reading=("Christmas is celebrated on December 25. For Christians, it marks the birth of Jesus. Some Orthodox churches follow the older "
                  "Julian calendar, so their Christmas falls on January 7. Christmas is observed in many countries, and families celebrate it "
                  "in many different ways. Singing carols is one long-standing tradition. A carol is a song, often sung in a group, and carols "
                  "are sung in many languages and musical styles. Some people who are not Christian also join in Christmas customs as part of "
                  "their culture, and many people do not celebrate it at all. No two families celebrate in exactly the same way."),
         when="December 25 (January 7 in some Orthodox churches)", where="Observed in many countries",
         words="carol, Julian calendar", glance="Late December",
         qs=[("On what date do most Christians celebrate Christmas?", "December 25", "December 25"),
             ("What is a carol?", "A song, often sung in a group", "carol is a song"),
             ("Why do some Orthodox churches celebrate on January 7?", "They follow the older Julian calendar", "Julian calendar")],
         bonus=("Connect to the reading", "If your example has singing, how do the voices (and the words, if there are any) add to the mood? "
                "If it has no singing, what do the instruments add instead?"), bonus_kw="singing"),
    dict(key="hanukkah", name="Hanukkah",
         reading=("Hanukkah is a Jewish holiday that lasts eight nights. It begins on the 25th day of Kislev, a month in the Hebrew calendar, so "
                  "its date on the calendar most of us use changes every year. Hanukkah remembers the rededication of the Temple in Jerusalem "
                  "long ago. A story tells how a small amount of oil lasted eight days. Many families light a menorah, which is sometimes called "
                  "a hanukkiah. It has nine branches: one for each night and a helper candle, the shamash, which is used to light the others. One "
                  "more candle is lit each night. Many people also play dreidel, a game with a spinning top."),
         when="Eight nights, starting on 25 Kislev (usually in November or December)", where="Celebrated by Jewish communities worldwide",
         words="menorah, shamash, dreidel", glance="Eight nights",
         qs=[("How many nights does Hanukkah last?", "Eight nights", "eight nights"),
             ("What is the shamash?", "The helper candle that is used to light the others", "helper candle, the shamash"),
             ("Why does the date of Hanukkah change from year to year on our usual calendar?", "It follows the Hebrew calendar (it begins on 25 Kislev)", "Hebrew calendar")],
         bonus=("Connect to the reading", "The reading says Hanukkah lasts eight nights, and one more candle is lit each night. If you wrote music for the "
                "eight nights, how would the tempo or the dynamics change from the first night to the last? Explain your thinking."), bonus_kw="eight nights"),
    dict(key="kwanzaa", name="Kwanzaa",
         reading=("Kwanzaa is a celebration of African American culture, family and community. It lasts seven days, from December 26 to "
                  "January 1. Maulana Karenga created it in 1966. The name comes from a Swahili phrase, matunda ya kwanza, which means "
                  "“first fruits.” Each day focuses on one of seven principles, called the Nguzo Saba, and their names are Swahili words. "
                  "Families and communities often light one candle each day on a candleholder called a kinara, which holds seven candles. "
                  "Many people also share a community feast called Karamu. The table below lists the seven principles in order."),
         when="Seven days, December 26 to January 1", where="Celebrated by many African American families and communities",
         words="principle, kinara, Swahili", glance="December 26 to January 1",
         qs=[("Who created Kwanzaa, and in what year?", "Maulana Karenga, in 1966", "Maulana Karenga created it in 1966"),
             ("How many principles are there, and what are they called together?", "Seven; the Nguzo Saba", "Nguzo Saba"),
             ("What does the word Kuumba mean?", "Creativity", "Creativity")],
         bonus=("Connect to the reading", "Choose one principle from the table. Which sounds in your example match its meaning? For example, Umoja means "
                "unity: do many voices or instruments play together?"), bonus_kw="principle"),
    dict(key="posadas", name="Las Posadas",
         reading=("Las Posadas is a celebration of nine nights, held from December 16 to 24. It is most closely linked with Mexico, and it is "
                  "also observed in other countries, including Guatemala, and by many families in the United States. The word posada means "
                  "lodging, or inn. Each night, people walk in a procession from house to house, remembering Mary and Joseph’s search for a "
                  "place to stay before the birth of Jesus. Groups often sing along the way, and each night ends with a gathering. Many "
                  "gatherings include songs, a piñata and food to share. Customs differ from town to town and from family to family."),
         when="Nine nights, December 16 to 24", where="Most closely linked with Mexico",
         words="posada, procession, piñata", glance="December 16 to 24",
         qs=[("How many nights does Las Posadas last?", "Nine nights", "nine nights"),
             ("What does the word posada mean?", "Lodging, or inn", "lodging, or inn"),
             ("What do people remember when they walk in the procession?", "Mary and Joseph’s search for a place to stay", "search for a place to stay")],
         bonus=("Connect to the reading", "The reading says people walk in a procession and often sing along the way. Is the beat of your example steady "
                "enough to walk to? How could you tell?"), bonus_kw="procession"),
    dict(key="lunar", name="Lunar New Year",
         reading=("Lunar New Year begins on a different date each year because it follows a calendar based on the moon. It always falls in "
                  "late January or in February, which is later than the other celebrations in this pack. Lunar New Year is celebrated in many "
                  "places and cultures, including China, Vietnam and Korea. In China, the festival lasts until the Lantern Festival on the 15th "
                  "day. In many places, a lion dance is part of the festivities, and the dancers are often accompanied by drums, gongs and "
                  "cymbals. Families have their own traditions, and they celebrate in many different ways."),
         when="A new date each year, in late January or February", where="China, Vietnam, Korea and many other places",
         words="lunar calendar, lion dance, percussion", glance="January or February",
         qs=[("Why does the date of Lunar New Year change each year?", "It follows a calendar based on the moon", "calendar based on the moon"),
             ("In which months does Lunar New Year always fall?", "Late January or February", "late January or in February"),
             ("Name one country where Lunar New Year is celebrated.", "China, Vietnam or Korea", "China, Vietnam and Korea")],
         bonus=("Connect to the reading", "The reading says lion dances are often accompanied by drums, gongs and cymbals. If your example has percussion, "
                "which sounds did you hear? Describe them with music words."), bonus_kw="drums"),
]
NC = len(CELEBS)
KEYS = [c["key"] for c in CELEBS]
NQ_EACH = 3

PRINCIPLES = [("Umoja", "Unity", "Working together for unity in the family and the community"),
              ("Kujichagulia", "Self-determination", "Defining, naming and speaking for yourself"),
              ("Ujima", "Collective work and responsibility", "Building the community and solving its problems together"),
              ("Ujamaa", "Cooperative economics", "Building and sharing in community businesses together"),
              ("Nia", "Purpose", "Having a purpose: building up the community"),
              ("Kuumba", "Creativity", "Using creativity to leave the community better than you found it"),
              ("Imani", "Faith", "Believing in your people, your leaders and the success of the community’s goals")]

PROMPTS = [  # key, heading, choice labels, line prompt
    ("instruments", "Instruments and voices", ["Voices", "Strings", "Winds", "Brass", "Percussion", "Keyboard", "Other"],
     "The instruments or voices I heard were:"),
    ("tempo", "Tempo", ["Slow", "Medium", "Fast", "It changed"], "I know the tempo because:"),
    ("dynamics", "Dynamics", ["Mostly quiet", "Medium", "Mostly loud", "It changed"], "The music got louder or softer when:"),
    ("mood", "Mood", ["Joyful", "Calm", "Festive", "Peaceful", "Lively", "Hopeful", "Serious"], "The mood was ______ because I heard:"),
    ("beat", "Beat feel", ["Steady and strong", "Gentle and flowing", "Bouncy", "No clear beat"], "I tapped the beat. It felt like groups of 2, 3, 4 or not sure because:"),
]
NPROMPT = len(PROMPTS) + 1      # five music prompts plus the connect-to-the-reading prompt

VOCAB = [
    ("Music words", [("tempo", "How fast or slow the beat of the music is."),
                     ("dynamics", "How loud or soft the music is, and how that changes."),
                     ("mood", "The feeling the music gives you, such as calm or joyful."),
                     ("beat feel", "How the steady beat moves: strong, flowing or bouncy, in groups of 2, 3 or 4."),
                     ("instrument", "Something that makes music, such as a drum, a flute or a violin. A voice counts too."),
                     ("percussion", "Instruments you hit, shake or scrape, such as drums, gongs and cymbals.")]),
    ("Culture words", [("tradition", "A custom passed down over time in a family or a community."),
                       ("carol", "A song, often sung in a group, that is linked to Christmas."),
                       ("menorah", "A candleholder used at Hanukkah. It has a place for eight candles and a helper candle."),
                       ("principle", "A basic belief that guides how people act."),
                       ("procession", "A group of people moving along together, often walking, as part of a celebration."),
                       ("lunar calendar", "A calendar that uses the phases of the moon to mark the months.")]),
]
NTERMS = sum(len(t) for _, t in VOCAB)

STEPS = [("Read together and answer the reading questions", 8), ("Listen once with no writing", 3),
         ("Listen again and fill in the response page", 10), ("Share and discuss", 4)]
NSTEPS = len(STEPS)
SET_MIN = sum(m for _, m in STEPS)          # one celebration
COMPARE_MIN = 25
REFLECT_MIN = 10
TOTAL_MIN = SET_MIN * NC + COMPARE_MIN + REFLECT_MIN

RUBRIC = [("Listening for music", "Describes all five music elements accurately with detail", "Describes four or five music elements, mostly accurately",
           "Describes two or three music elements", "Describes one element or needs a lot of help"),
          ("Evidence", "Gives a clear reason from the music for every choice", "Gives a reason for most choices", "Gives a reason for some choices",
           "Gives few or no reasons"),
          ("Reading and facts", "Answers every reading question correctly and links the music to the reading", "Answers most questions correctly",
           "Answers some questions correctly", "Needs support to answer"),
          ("Compare and contrast", "Names clear likenesses and differences with examples from both pieces", "Names likenesses and differences with some examples",
           "Names a likeness or a difference", "Needs support to compare"),
          ("Respectful listening", "Listens carefully and respectfully every time", "Listens respectfully almost every time",
           "Listens respectfully some of the time", "Needs reminders to listen respectfully")]
RUBRIC_MAX = 4
RUBRIC_TOTAL = RUBRIC_MAX * len(RUBRIC)

REFLECT_CHECK = ["I listened quietly and carefully while the music played.",
                 "I used music words (tempo, dynamics, mood, beat feel) to describe what I heard.",
                 "I respected that families celebrate in many different ways, or not at all.",
                 "I shared only what I wanted to share about my own family."]

NO_AUDIO = "No audio or recordings are included or named. You choose the music."

# ------------------------------------------------------------------ page map
PLAN = ["cover", "teacher1", "teacher2", "guide", "vocab"]
for _c in CELEBS:
    PLAN += [f"read_{_c['key']}", f"listen_{_c['key']}"]
PLAN += ["compare", "chart", "rubric", "reflect", "key", "terms"]
PAGEOF = {k: i + 1 for i, k in enumerate(PLAN)}
TOTAL_PAGES = len(PLAN)
PAGE_NAMES = {"cover": "Cover", "teacher1": "Teacher Notes", "teacher2": "Teacher Notes: Facts and Pacing", "guide": "How to Listen",
              "vocab": "Vocabulary", "compare": "Compare and Contrast", "chart": "Five-Celebration Chart", "rubric": "Rubric",
              "reflect": "Reflection", "key": "Reading Answer Key", "terms": "Terms of Use"}
for _i, _c in enumerate(CELEBS, 1):
    PAGE_NAMES[f"read_{_c['key']}"] = f"Reading {_i}: {_c['name']}"
    PAGE_NAMES[f"listen_{_c['key']}"] = f"Listening Response {_i}: {_c['name']}"


def R(kind, cap=False):
    """A page reference that --check reads back and compares with where that page really is."""
    return f'<span data-ref="{kind}" data-n="{PAGEOF[kind]}">{"Page" if cap else "page"} {PAGEOF[kind]}</span>'


def RR(k1, k2, cap=False):
    return (f'<span data-ref="{k1}" data-n="{PAGEOF[k1]}" data-ref2="{k2}" data-n2="{PAGEOF[k2]}">'
            f'{"Pages" if cap else "pages"} {PAGEOF[k1]}–{PAGEOF[k2]}</span>')


def word_count(t):
    return len(re.findall(r"[A-Za-zñ’'-]+", t))


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
.foot { display: flex; justify-content: space-between; font-size: 8.5pt; color: #333; border-top: .8pt solid #000; padding-top: 3pt; margin-top: 12pt; }
.wm { position: absolute; left: 50%; top: 50%; transform: translate(-50%, -50%) rotate(-38deg); font-family: 'Oswald'; font-weight: 700;
      font-size: 150pt; color: rgba(0,0,0,.13); letter-spacing: .06em; white-space: nowrap; pointer-events: none; z-index: 9; }
.fill { flex: 1; min-height: 0; }
.doc h1 { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 30pt; margin: 0 0 4pt; line-height: 1; }
.doc h2 { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 13.5pt; margin: 11pt 0 4pt; letter-spacing: .02em; }
.doc p, .doc li { font-size: 11pt; line-height: 1.36; margin: 0 0 5pt; text-wrap: pretty; }
.doc ul, .doc ol { margin: 0 0 4pt; padding-left: 16pt; }
.doc.big p, .doc.big li { font-size: 11.6pt; line-height: 1.4; margin-bottom: 5pt; }
.doc.big .small { font-size: 10.5pt !important; }
.doc.big h2 { margin-top: 12pt; }
.doc .rule { border-bottom: 2.2pt solid #000; margin-bottom: 8pt; padding-bottom: 6pt; }
.doc table.dt { border-collapse: collapse; width: 100%; table-layout: fixed; font-size: 10pt; margin: 2pt 0 4pt; }
.doc table.dt td, .doc table.dt th { border: 1pt solid #000; padding: 3pt 6pt; text-align: left; vertical-align: top; }
.doc table.dt th { font-family: 'Oswald'; font-weight: 500; text-transform: uppercase; font-size: 9.5pt; background: #000; color: #fff; }
.small { font-size: 9.5pt !important; color: #333; }
.cols { display: flex; gap: 18pt; }
.cols > div { flex: 1; min-width: 0; }
.rl { border-bottom: 1pt solid #000; height: 21pt; }
.hd2 { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 13pt; letter-spacing: .02em; margin: 10pt 0 4pt; }
/* readings */
.read { font-size: 13.5pt; line-height: 1.5; margin: 8pt 0 8pt; text-wrap: pretty; }
.fact { border: 1.3pt solid #000; border-radius: 7pt; padding: 6pt 12pt 7pt; margin: 2pt 0 4pt; }
.fact div { display: flex; gap: 10pt; font-size: 11pt; line-height: 1.3; padding: 1.5pt 0; }
.fact b { flex: 0 0 0.95in; font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 10pt; letter-spacing: .06em; color: ACCENT; padding-top: 1pt; }
table.pr { border-collapse: collapse; width: 100%; table-layout: fixed; font-size: 10.5pt; margin: 4pt 0 2pt; }
table.pr td, table.pr th { border: 1pt solid #000; padding: 3pt 6pt; text-align: left; vertical-align: middle; line-height: 1.25; }
table.pr th { font-family: 'Oswald'; font-weight: 500; text-transform: uppercase; font-size: 9.5pt; background: #000; color: #fff; letter-spacing: .04em; }
table.pr td.d { font-family: 'Oswald'; font-weight: 700; text-align: center; }
table.pr td.sw { font-family: 'Oswald'; font-weight: 700; font-size: 12pt; }
ol.rq { margin: 2pt 0 4pt; padding-left: 20pt; }
ol.rq li { font-size: 11.5pt; line-height: 1.3; margin: 0 0 3pt; font-weight: 600; }
ol.rq li .rl { margin-top: 0; font-weight: 400; }
.notes { flex: 1; min-height: 60pt; border: 1.3pt solid #000; border-radius: 7pt; padding: 5pt 12pt 6pt; margin-top: 8pt; display: flex; flex-direction: column; overflow: hidden; }
.notes .bt { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 11pt; letter-spacing: .03em; }
.notes .ln { flex: 1; background-image: repeating-linear-gradient(to bottom, transparent 0, transparent 20pt, #000 20pt, #000 21pt); background-size: 100% 21pt; background-position: 0 0; }
/* listening response */
.ex { border: 1.3pt dashed #000; border-radius: 7pt; padding: 6pt 12pt 7pt; margin: 2pt 0 6pt; }
.ex .bt { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 11pt; letter-spacing: .03em; }
.ex .bt small { font-family: 'Source Sans 3'; font-weight: 400; text-transform: none; font-size: 10pt; letter-spacing: 0; margin-left: 6pt; }
.ex .rl { height: 18pt; }
.cards { flex: 1; display: flex; flex-direction: column; gap: 6pt; min-height: 0; }
.pc { flex: 1; border: 1.3pt solid #000; border-radius: 7pt; padding: 5pt 11pt 5pt; display: flex; flex-direction: column; min-height: 0; }
.pc .ph { display: flex; align-items: center; gap: 8pt; }
.pc .ph i { flex: 0 0 20pt; width: 20pt; height: 20pt; line-height: 20pt; border-radius: 50%; background: ACCENT; color: #fff; font-style: normal; font-family: 'Oswald'; font-weight: 700; font-size: 11.5pt; text-align: center; }
.pc .ph b { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 12pt; letter-spacing: .03em; }
.pc .opts { display: flex; flex-wrap: wrap; gap: 3pt 12pt; margin: 4pt 0 2pt 28pt; }
.pc .opts span { display: inline-flex; align-items: center; gap: 4pt; font-size: 10.5pt; line-height: 1.1; font-weight: 600; }
.pc .opts span::before { content: ""; width: 10.5pt; height: 10.5pt; border: 1.5pt solid #000; border-radius: 50%; flex: 0 0 10.5pt; }
.pc .lp { font-size: 10.5pt; line-height: 1.25; margin: 2pt 0 0 28pt; }
.pc .lp.bonus { font-size: 11pt; font-weight: 600; }
.pc .ln { flex: 1; min-height: 16pt; margin-left: 28pt; background-image: repeating-linear-gradient(to bottom, transparent 0, transparent 19pt, #000 19pt, #000 20pt); background-size: 100% 20pt; }
/* listening guide, vocabulary, compare */
table.gd { border-collapse: collapse; width: 100%; table-layout: fixed; font-size: 11.8pt; margin: 4pt 0; }
table.gd td, table.gd th { border: 1pt solid #000; padding: 8pt 9pt; vertical-align: top; line-height: 1.3; }
table.gd th { font-family: 'Oswald'; font-weight: 500; text-transform: uppercase; font-size: 10pt; background: #000; color: #fff; }
table.gd td.e { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 12pt; letter-spacing: .02em; }
.ckh { display: flex; align-items: center; gap: 14pt; margin: 8pt 0 8pt; font-size: 12.5pt; line-height: 1.35; }
.ckh .sp { flex: 0 0 1.15in; height: 1.15in; display: flex; align-items: center; justify-content: center; padding: 0.06in; }
.ckh .sp img { max-width: 100%; max-height: 100%; display: block; }
.vgrid { display: grid; grid-template-columns: 1fr 1fr; gap: 6pt 16pt; margin-top: 2pt; }
.vc { border: 1.3pt solid #000; border-radius: 7pt; padding: 5pt 10pt 4pt; }
.vc b { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 13pt; letter-spacing: .03em; }
.vc p { font-size: 10.5pt; line-height: 1.28; margin: 1pt 0 0; }
.vc .rl { height: 23pt; }
table.cmp { border-collapse: collapse; width: 100%; table-layout: fixed; font-size: 11pt; margin: 4pt 0; }
table.cmp td, table.cmp th { border: 1.2pt solid #000; padding: 4pt 7pt; vertical-align: middle; }
table.cmp th { font-family: 'Oswald'; font-weight: 500; text-transform: uppercase; font-size: 10pt; background: #000; color: #fff; }
table.cmp td.e { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 11pt; letter-spacing: .02em; }
table.cmp tr.r td { height: 33pt; }
table.cmp tr.r5 td { height: 74pt; }
.venn { display: flex; justify-content: center; margin: 4pt 0 2pt; }
.venn svg { width: 6.1in; height: 2.65in; display: block; }
.pick { display: flex; gap: 14pt; margin: 4pt 0 2pt; }
.pick div { flex: 1; font-size: 11.5pt; font-weight: 600; }
.pick .rl { height: 19pt; }
.rub { border-collapse: collapse; width: 100%; table-layout: fixed; font-size: 10.2pt; margin: 6pt 0; }
.rub td, .rub th { border: 1.2pt solid #000; padding: 9pt 6pt; vertical-align: top; line-height: 1.28; }
.rub th { font-family: 'Oswald'; font-weight: 500; text-transform: uppercase; font-size: 10pt; background: #000; color: #fff; text-align: center; }
.rub td.c { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 11pt; letter-spacing: .02em; vertical-align: middle; }
.rub td.s { text-align: center; vertical-align: middle; }
.rub tr.tot td { font-family: 'Oswald'; font-weight: 700; font-size: 12pt; text-align: right; height: 32pt; vertical-align: middle; }
.ck { display: flex; align-items: center; gap: 12pt; border: 1.3pt solid #000; border-radius: 7pt; padding: 8pt 12pt; margin-bottom: 8pt; }
.ck .bx { flex: 0 0 20pt; width: 20pt; height: 20pt; border: 2pt solid #000; border-radius: 4pt; }
.ck .tx { flex: 1; font-size: 12pt; line-height: 1.25; font-weight: 600; }
.kq { border: 1.3pt solid #000; border-radius: 7pt; padding: 9pt 14pt 8pt; margin-bottom: 11pt; }
.kq .kh { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 14pt; letter-spacing: .02em; margin-bottom: 3pt; }
.kq .kh i { font-style: normal; color: ACCENT; }
.kq li { font-size: 11.8pt; line-height: 1.34; margin: 0 0 3pt; }
.kq ol { margin: 0; padding-left: 18pt; }
.steps { width: 100%; border-collapse: collapse; margin: 3pt 0 4pt; font-size: 10.8pt; }
.steps td { border: 1pt solid #000; padding: 3pt 7pt; }
.steps td.m { width: 0.9in; text-align: right; font-family: 'Oswald'; font-weight: 700; }
.steps tr.t td { background: #EAF2F9; font-family: 'Oswald'; font-weight: 700; }
.cover { align-items: center; justify-content: space-between; padding: 0.55in 0.6in 0.5in; }
.store { font-family: 'Oswald'; font-weight: 500; font-size: 13pt; letter-spacing: .32em; text-transform: uppercase; }
.ctitle { text-align: center; }
.ctitle .a { font-family: 'Oswald'; font-weight: 700; font-size: 44pt; line-height: 1; letter-spacing: .02em; }
.ctitle .b { font-family: 'Oswald'; font-weight: 700; white-space: nowrap; font-size: 60pt; line-height: .95; letter-spacing: .01em; }
.ctitle .c { font-family: 'Oswald'; font-weight: 300; font-size: 17pt; margin-top: 8pt; }
.cband { width: 100%; background: #000; color: #fff; text-align: center; font-family: 'Oswald'; font-weight: 500; font-size: 14pt;
         letter-spacing: .08em; text-transform: uppercase; padding: 8pt 0 9pt; border-radius: 4pt; }
.cband em { font-style: normal; color: #8FC3EC; }
""".replace("ACCENT", ACCENT)


def html_doc(pages, title="doc"):
    return (f'<!doctype html><html><head><meta charset="utf-8"><title>{escape(title)}</title>'
            f'<style>{font_css()}{CSS}</style></head><body>{"".join(pages)}</body></html>')


COPY = f"© {YEAR} {STORE} · {BRAND} · For single-classroom use"


def foot(right):
    return f'<div class="foot"><span>{COPY}</span><span>{right}</span></div>'


def page(kind, inner, wm=False, cls="", right=None, fill=True):
    n = PAGEOF[kind]
    w = '<div class="wm">PREVIEW</div>' if wm else ""
    f = '<div class="fill"></div>' if fill else ""
    return (f'<section class="page {cls}" data-page="{n}" data-kind="{kind}" data-name="{escape(PAGE_NAMES[kind])}">{w}{inner}{f}'
            f'{foot(right or f"Page {n}")}</section>')


def top(title, sub, tag, tagline, cls=""):
    return (f'<div class="top"><div class="h t">{title}<small>{sub}</small></div>'
            f'<div class="tag {cls}"><div class="lv">{tag}</div><div class="ln">{tagline}</div></div></div>')


NAME_ROW = '<div class="name">Name <span></span> Date <span class="s"></span></div>'


def rls(n):
    return '<div class="rl"></div>' * n


# ------------------------------------------------------------------ pages
def teacher1_page(wm=False):
    inner = (f'<div class="rule"><h1>Teacher Notes</h1><div class="l" style="font-size:13pt">Around the World, Music Edition · Grades 3–6</div></div>'
             f'<p>Students read a short passage about each of five celebrations, listen to music that you choose from that tradition, and describe what they hear '
             f'with five music elements: instruments, tempo, dynamics, mood and beat feel. Then they compare and contrast, build vocabulary and reflect. '
             f'{NO_AUDIO}</p>'
             f'<h2>Learning about cultures</h2>'
             f'<ul><li>These pages are for learning about cultures and traditions through music. They are not for practicing any religion. Students are never asked '
             f'to take part in a ritual, to say what they believe or to say what their family does.</li>'
             f'<li>Invite student voices without requiring them. Some students celebrate one of these, some celebrate several, some celebrate other things and '
             f'some celebrate none. Make no assumptions about any family, and avoid saying “we” or “everyone.”</li>'
             f'<li>Each reading keeps to basic facts. Customs differ from place to place and from family to family, and each reading says so. Invite students to ask '
             f'family or community members what they would like to add.</li></ul>'
             f'<h2>Choosing the music</h2>'
             f'<ul><li>Use any music from the tradition that you have the right to use: public domain or traditional music with a source you have checked, a recording '
             f'licensed to your school or covered by a service your district allows, a live performance by you, a colleague or a guest, or a recording shared with permission.</li>'
             f'<li>Write the title or a short description in the “teacher-chosen example” box on each response page. One to two minutes is enough; students listen twice.</li>'
             f'<li>No tradition has one sound. If you can, choose examples that differ in style, and tell students the example is one of many.</li></ul>'
             f'<h2>The calendar</h2>'
             f'<ul><li>Dates are listed on each reading. Hanukkah begins on 25 Kislev, so it moves around on the usual calendar. Kwanzaa runs December 26 to January 1.</li>'
             f'<li><b>Lunar New Year is not a December celebration.</b> It falls in late January or February, so it works well as a January or February lesson, and the whole pack can be taught in any month.</li></ul>'
             f'<h2>What is inside ({TOTAL_PAGES} pages)</h2>'
             f'<p>{R("teacher1", True)} and {R("teacher2")} teacher notes, {R("guide")} how to listen, {R("vocab")} vocabulary, '
             f'{RR(f"read_{KEYS[0]}", f"listen_{KEYS[-1]}")} the {NC} readings, each followed by its listening response page, '
             f'{R("compare")} compare and contrast, {R("chart")} five-celebration chart, {R("rubric")} rubric, {R("reflect")} reflection, '
             f'{R("key")} reading answer key and {R("terms")} terms of use.</p>'
             f'<p class="small">Standards: the activities connect to the Responding and Connecting processes of the National Core Arts Standards in music. '
             f'Please match them to your own curriculum.</p>')
    return page("teacher1", inner, wm, "doc")


def teacher2_page(wm=False):
    rows = "".join(f'<tr data-fact="{c["key"]}"><td><b>{c["name"]}</b></td><td>{escape(c["when"])}</td><td>{escape(c["where"])}</td></tr>' for c in CELEBS)
    steps = "".join(f'<tr data-step="{i}" data-min="{m}"><td>{i}. {n}</td><td class="m">{m} min</td></tr>' for i, (n, m) in enumerate(STEPS, 1))
    inner = (f'<div class="rule"><h1>Facts, Pacing and Support</h1><div class="l" style="font-size:13pt">A quick reference for teachers</div></div>'
             f'<h2>Facts at a glance</h2>'
             f'<table class="dt"><tr><th style="width:1.35in">Celebration</th><th>When</th><th style="width:2.5in">Where</th></tr>{rows}</table>'
             f'<p class="small">The facts are limited to basics that are widely documented. Lunar New Year is called by other names in different cultures; this pack uses the general name.</p>'
             f'<h2>Pacing for each celebration ({SET_MIN} minutes)</h2>'
             f'<table class="steps">{steps}<tr class="t" data-mintotal="{SET_MIN}"><td>One celebration (reading page and response page)</td><td class="m">{SET_MIN} min</td></tr></table>'
             f'<p>Teach the {NC} sets in any order. All {NC} sets take {SET_MIN * NC} minutes. Add {COMPARE_MIN} minutes for the compare and contrast pages '
             f'({R("compare")} and {R("chart")}) and {REFLECT_MIN} minutes for the reflection ({R("reflect")}): {TOTAL_MIN} minutes in all.</p>'
             f'<h2>Differentiation and support</h2>'
             f'<ul><li><b>Grades 3–4:</b> read each passage aloud, listen once together and fill in the first response page as a class. Students circle choices and add a few words.</li>'
             f'<li><b>Grades 5–6:</b> students read silently, write full sentences for their reasons and use the vocabulary words ({R("vocab")}).</li>'
             f'<li><b>Support:</b> {R("guide")} gives word choices for every music element. Students can point to a choice and say one reason.</li></ul>'
             f'<h2>Scoring</h2>'
             f'<p>The rubric ({R("rubric")}) has {len(RUBRIC)} categories scored 1–{RUBRIC_MAX}, {RUBRIC_TOTAL} points in all. The response pages have no single correct answer: accept any answer that matches what the student heard and gives a reason. '
             f'Reading questions have answers on {R("key")}.</p>')
    return page("teacher2", inner, wm, "doc")


def guide_page(wm=False):
    rows = [("Instruments", "What is making the sounds?", "voices, strings, winds, brass, percussion, keyboard"),
            ("Tempo", "How fast is the steady beat?", "slow, medium, fast, speeding up, slowing down"),
            ("Dynamics", "How loud or soft is it, and does it change?", "quiet, medium, loud, getting louder, getting softer"),
            ("Mood", "What feeling does it give you?", "joyful, calm, festive, peaceful, lively, hopeful, serious"),
            ("Beat feel", "Can you tap along? How does the beat move?", "steady and strong, gentle and flowing, bouncy, groups of 2, 3 or 4, no clear beat")]
    tr = "".join(f'<tr data-elem="{e}"><td class="e">{e}</td><td>{q}</td><td>{w}</td></tr>' for e, q, w in rows)
    inner = (top("How to Listen", "Five things to listen for", "GUIDE", "student reference")
             + NAME_ROW
             + f'<div class="ckh"><div class="sp"><img src="../art/hero.png" alt=""></div>'
               f'<div>You are going to listen to music from five celebrations. Music from every tradition has instruments or voices, a tempo, dynamics, a mood and a beat feel. '
               f'Use these words to describe what <b>you</b> hear. There are no wrong answers if you can give a reason from the music.</div></div>'
             + f'<table class="gd"><tr><th style="width:1.2in">Element</th><th style="width:2.5in">Ask yourself</th><th>Words you can use</th></tr>{tr}</table>'
             + '<h2 class="hd2">Listening routine</h2>'
               '<ol style="margin:0 0 4pt;padding-left:18pt;font-size:12.5pt;line-height:1.45">'
               '<li><b>Listen once.</b> Close your eyes or look at the floor. Just listen.</li>'
               '<li><b>Listen again.</b> Tap the steady beat very quietly on your leg.</li>'
               '<li><b>Respond.</b> Circle choices and write a reason for each.</li>'
               '<li><b>Share.</b> Tell a partner one thing you heard. Say it with a music word.</li></ol>'
               '<h2 class="hd2">Respectful listening</h2>'
               '<ul style="margin:0;padding-left:18pt;font-size:12.5pt;line-height:1.45">'
               '<li>We are learning about cultures and traditions. We do not have to celebrate any of them.</li>'
               '<li>Keep your voice off while the music plays, and keep your comments kind.</li>'
               '<li>Share about your own family only if you want to. Everyone celebrates differently, and that is fine.</li></ul>')
    return page("guide", inner, wm, "doc")


def vocab_page(wm=False):
    parts = []
    for grp, terms in VOCAB:
        cards = "".join(f'<div class="vc" data-term="{t}"><b>{t}</b><p>{d}</p><div class="rl"></div></div>' for t, d in terms)
        parts.append(f'<h2 class="hd2" style="margin-top:8pt">{grp}</h2><div class="vgrid">{cards}</div>')
    inner = (top("Vocabulary", f"{NTERMS} words for listening and reading", "WORDS", "student reference") + NAME_ROW
             + '<p style="font-size:11.5pt;margin:0 0 2pt">Read each meaning. On the line, write a sentence or a note that uses the word in your own way.</p>'
             + "".join(parts))
    return page("vocab", inner, wm, "doc")


def reading_page(i, wm=False):
    c = CELEBS[i - 1]
    k = c["key"]
    fact = (f'<div class="fact"><div><b>When</b><span>{escape(c["when"])}</span></div><div><b>Where</b><span>{escape(c["where"])}</span></div>'
            f'<div><b>Key words</b><span>{escape(c["words"])}</span></div></div>')
    table = ""
    nlines = 2
    if k == "kwanzaa":
        trs = "".join(f'<tr data-principle="{n}"><td class="d">{j}</td><td class="sw">{n}</td><td><b>{m}</b></td><td>{g}</td></tr>'
                      for j, (n, m, g) in enumerate(PRINCIPLES, 1))
        table = (f'<table class="pr"><tr><th style="width:0.5in">Day</th><th style="width:1.3in">Swahili name</th><th style="width:2.1in">Meaning</th><th>In other words</th></tr>{trs}</table>')
        nlines = 1
    qs = "".join(f'<li data-rq="{k}" data-n="{j}">{escape(q)}{rls(nlines)}</li>' for j, (q, _, _) in enumerate(c["qs"], 1))
    notes = ('<div class="notes"><div class="bt">Ideas I want to remember</div><div class="ln"></div></div>' if k != "kwanzaa" else "")
    inner = (top(c["name"], "Reading and questions", f"READING {i}", f"of {NC}") + NAME_ROW
             + f'<p class="read" data-reading="{k}">{escape(c["reading"])}</p>' + fact + table
             + f'<div class="hd2">Check your reading</div><ol class="rq">{qs}</ol>' + notes)
    return page(f"read_{k}", inner, wm, "", right=f"Page {PAGEOF[f'read_{k}']} · Listening response on {R(f'listen_{k}')}", fill=(k == "kwanzaa"))


def listen_page(i, wm=False):
    c = CELEBS[i - 1]
    k = c["key"]
    cards = ""
    for j, (pk, head, opts, lp) in enumerate(PROMPTS, 1):
        o = "".join(f"<span>{x}</span>" for x in opts)
        cards += (f'<div class="pc" data-prompt="{pk}" data-celeb="{k}" data-n="{j}"><div class="ph"><i>{j}</i><b>{head}</b></div>'
                  f'<div class="opts">{o}</div><div class="lp">{lp}</div><div class="ln"></div></div>')
    bh, bt = c["bonus"]
    cards += (f'<div class="pc" data-prompt="connect" data-celeb="{k}" data-n="{NPROMPT}"><div class="ph"><i>{NPROMPT}</i><b>{bh}</b></div>'
              f'<div class="lp bonus" data-bonus="{k}">{escape(bt)}</div><div class="ln"></div></div>')
    inner = (top(c["name"], "Listening response", f"LISTEN {i}", f"of {NC}") + NAME_ROW
             + '<div class="ex"><div class="bt">Teacher-chosen example <small>Your teacher writes the title or a short description. Listen twice.</small></div><div class="rl"></div></div>'
             + f'<div class="cards">{cards}</div>')
    return page(f"listen_{k}", inner, wm, "", right=f"Page {PAGEOF[f'listen_{k}']} · Reading on {R(f'read_{k}')}", fill=False)


def venn_svg():
    sw = 4
    return (f'<svg class="art" data-svg="venn" data-sw="{sw}" viewBox="0 0 760 330" role="img" aria-label="Two overlapping circles">'
            f'<g class="art" fill="none" stroke="#000" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round">'
            f'<circle cx="290" cy="165" r="140"/><circle cx="470" cy="165" r="140"/></g>'
            f'<g font-family="Oswald" font-weight="700" font-size="18" letter-spacing="1" text-anchor="middle" fill="#000">'
            f'<text x="225" y="172">ONLY A</text><text x="380" y="172">BOTH</text><text x="535" y="172">ONLY B</text></g></svg>')


def compare_page(wm=False):
    rows = "".join(f'<tr class="r" data-cmp="{pk}"><td class="e">{head}</td><td></td><td></td><td></td></tr>' for pk, head, _, _ in PROMPTS)
    inner = (top("Compare and Contrast", "Choose two examples and compare them", "COMPARE", "two examples") + NAME_ROW
             + '<div class="pick"><div>Example A (celebration and piece):' + '<div class="rl"></div></div><div>Example B (celebration and piece):<div class="rl"></div></div></div>'
             + f'<table class="cmp"><tr><th style="width:1.35in">Element</th><th>Example A</th><th>Example B</th><th style="width:1.2in">Same or different?</th></tr>{rows}</table>'
             + f'<div class="venn">{venn_svg()}</div>'
             + '<div class="hd2" style="margin-top:2pt">Write about it</div>'
               '<div style="font-size:11.5pt;font-weight:600">One way the two examples were alike:</div>' + rls(2)
             + '<div style="font-size:11.5pt;font-weight:600;margin-top:2pt">One way they were different:</div>' + rls(2))
    return page("compare", inner, wm, "")


def chart_page(wm=False):
    rows = "".join(f'<tr class="r5" data-chart="{c["key"]}"><td class="e">{c["name"]}</td><td></td><td></td><td></td><td></td><td></td></tr>' for c in CELEBS)
    inner = (top("Five-Celebration Chart", "Keep track as you listen", "CHART", "all five") + NAME_ROW
             + '<p style="font-size:11.5pt;margin:0 0 4pt">Use your response pages. Write a few words in each box.</p>'
             + f'<table class="cmp"><tr><th style="width:1.15in">Celebration</th><th>Instruments</th><th>Tempo</th><th>Dynamics</th><th>Mood</th><th>Beat feel</th></tr>{rows}</table>'
             + '<div class="hd2">Think about it</div>'
               '<div style="font-size:11.5pt;font-weight:600">Which two examples sounded the most alike? How?</div>' + rls(2)
             + '<div style="font-size:11.5pt;font-weight:600;margin-top:2pt">Which two sounded the most different? How?</div>' + rls(2))
    return page("chart", inner, wm, "")


def rubric_page(wm=False):
    hdr = ''.join(f'<th>{RUBRIC_MAX - j}</th>' for j in range(RUBRIC_MAX))
    rows = "".join(f'<tr data-rubric="{j}"><td class="c">{n}</td>' + "".join(f'<td>{d}</td>' for d in ds) + '<td class="s"></td><td class="s"></td></tr>'
                   for j, (n, *ds) in enumerate(RUBRIC, 1))
    inner = (top("Rubric", f"{len(RUBRIC)} categories, scored 1–{RUBRIC_MAX}", "RUBRIC", f"{RUBRIC_TOTAL} points") + NAME_ROW
             + '<p style="font-size:11.5pt;margin:0 0 2pt">Score yourself first, and then your teacher scores. Look at your response pages, the compare and contrast pages and your reflection.</p>'
             + f'<table class="rub"><tr><th style="width:1.15in">Category</th>{hdr}<th style="width:0.55in">Me</th><th style="width:0.65in">Teacher</th></tr>{rows}'
             + f'<tr class="tot" data-total="{RUBRIC_TOTAL}"><td colspan="5">Total, out of {RUBRIC_TOTAL}</td><td></td><td></td></tr></table>'
             + '<div class="hd2">Teacher comments</div>' + rls(4))
    return page("rubric", inner, wm, "")


def reflect_page(wm=False):
    ck = "".join(f'<div class="ck" data-reflect><div class="bx"></div><div class="tx">{t}</div></div>' for t in REFLECT_CHECK)
    inner = (top("Reflection", "Think back on what you heard and read", "REFLECT", "my thoughts") + NAME_ROW
             + '<div class="hd2">Finish the sentences</div>'
               '<div style="font-size:11.5pt;font-weight:600">One celebration I learned about, and one fact I learned:</div>' + rls(3)
             + '<div style="font-size:11.5pt;font-weight:600;margin-top:3pt">The music element that was easiest for me to hear was ______ because:</div>' + rls(3)
             + '<div style="font-size:11.5pt;font-weight:600;margin-top:3pt">Something in the music that surprised me:</div>' + rls(3)
             + '<div style="font-size:11.5pt;font-weight:600;margin-top:3pt">A question I still have, and who I could ask:</div>' + rls(3)
             + '<div class="hd2">My listening</div>' + ck
             + '<p class="small" style="margin-top:2pt">Teachers: invite students to share, and never require it. Share only what you want to share.</p>')
    return page("reflect", inner, wm, "")


def key_page(wm=False):
    cards = ""
    for c in CELEBS:
        li = "".join(f'<li data-ak="{c["key"]}" data-n="{j}"><b>{escape(q)}</b> {escape(a)}</li>' for j, (q, a, _) in enumerate(c["qs"], 1))
        cards += f'<div class="kq"><div class="kh"><i>{c["name"]}</i> · {R("read_" + c["key"])}</div><ol>{li}</ol></div>'
    inner = (top("Reading Answer Key", "For teachers", "ANSWER KEY", f"{NC * NQ_EACH} answers", "key") + '<div style="height:6pt"></div>' + cards
             + '<p class="small">The listening response pages have no single correct answer. Accept answers that match what the student heard and give a reason from the music.</p>')
    return page("key", inner, wm, "doc")


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
             f'<li>Readings, response pages, charts, rubric and answer key: original work, {BRAND} by {STORE}.</li>'
             f'<li>Cover and spot illustration: house-style line art made with digital tools by {BRAND}.</li>'
             f'<li>Text fonts: Oswald (The Oswald Project Authors) and Source Sans 3 (Adobe), SIL Open Font License 1.1.</li></ul>'
             f'<h2>About the music</h2><p>{NO_AUDIO} You are responsible for choosing music you have the right to use.</p>'
             f'<h2>What is in this file</h2><p>{TOTAL_PAGES} pages in all: cover, teacher notes, how to listen, vocabulary, {NC} readings with {NC} listening response pages, compare and contrast, '
             f'a five-celebration chart, a rubric, a reflection, a reading answer key and these terms.</p>'
             f'<p class="small">{DISCLOSURE}</p>')
    return page("terms", inner, wm, "doc big")


def cover_page():
    return (f'<section class="page cover" data-page="1" data-kind="cover" data-name="Cover"><div class="store">{BRAND}</div>'
            f'<div style="height:4.5in;display:flex;align-items:center;justify-content:center"><img src="../art/hero.png" style="height:4.4in;display:block" alt=""></div>'
            f'<div class="ctitle"><div class="a">READINGS &amp; LISTENING PAGES</div><div class="b">AROUND THE WORLD</div>'
            f'<div class="c">Music Edition: {NC} celebrations, each with a short reading and a listening response page</div></div>'
            f'<div class="cband">Grades 3–6 <em>·</em> {NC} celebrations <em>·</em> {TOTAL_PAGES} pages</div></section>')


def all_pages(wm=False):
    p = [cover_page(), teacher1_page(wm), teacher2_page(wm), guide_page(wm), vocab_page(wm)]
    for i in range(1, NC + 1):
        p += [reading_page(i, wm), listen_page(i, wm)]
    p += [compare_page(wm), chart_page(wm), rubric_page(wm), reflect_page(wm), key_page(wm), terms_page(wm)]
    return p


SHOT_KINDS = ["teacher1", *[f"read_{k}" for k in KEYS], "listen_kwanzaa", "listen_hanukkah", "compare", "rubric"]
SHOT_PAGES = {k: PAGEOF[k] for k in SHOT_KINDS}
PREVIEW_ORDER = ["teacher1", "read_kwanzaa", "listen_hanukkah", "compare"]

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
        f'<div><div class="hd" style="font-size:54px">Readings &amp; Listening Pages</div>'
        f'<div class="hd" style="font-size:104px">Around the World</div>'
        f'<div class="sub" style="font-size:28px;margin-top:12px">Music Edition: {NC} celebrations, each with a reading and a listening page</div></div>'
        f'</div><div class="band">Grades 3–6 <em>·</em> {NC} celebrations <em>·</em> {TOTAL_PAGES} pages</div></div>')


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
        shots_row("A reading and a listening page", "Every celebration has both",
                  [("shot-read_kwanzaa.png", label("read_kwanzaa", "80–120 words and 3 questions")),
                   ("shot-listen_hanukkah.png", label("listen_hanukkah", f"{NPROMPT} prompts, teacher-chosen music"))],
                  f"{NC} readings <em>·</em> {NC} listening pages <em>·</em> no audio needed", 420),
        shots_grid(f"{NC} celebrations", "One reading for each, written for grades 3–6",
                   [(f"shot-read_{c['key']}.png", f'{c["name"]}<span>{escape(c["glance"])}</span>') for c in CELEBS],
                   f"{NC} readings <em>·</em> facts kept simple <em>·</em> grades 3–6", 190),
        shots_row("Compare, then assess", "Compare and contrast, plus a rubric and a reflection page",
                  [("shot-compare.png", label("compare", "Venn diagram and table")),
                   ("shot-rubric.png", label("rubric", f"{len(RUBRIC)} categories, {RUBRIC_TOTAL} points"))],
                  f"Vocabulary <em>·</em> reflection <em>·</em> {TOTAL_PAGES} pages", 420),
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


SECTIONS = [  # (label, pages)
    ("Cover", 1), ("Teacher notes", 2), ("How to listen", 1), ("Vocabulary", 1), ("Readings", NC), ("Listening response pages", NC),
    ("Compare and contrast", 1), ("Five-celebration chart", 1), ("Rubric", 1), ("Reflection", 1), ("Reading answer key", 1), ("Terms of use and credits", 1)]


def upload_md():
    sec = "\n".join(f"- {n}: {p}" for n, p in SECTIONS)
    return f"""# UPLOAD: {LISTING_TITLE} (TpT 064)

These fields follow the order of TpT's "Add a resource" form. Written for December (most of the pack is December celebrations), but Lunar New Year is a January or February celebration, so it sells through February.

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
Bring music and culture together with {NC} short readings and {NC} listening response pages for grades 3-6. Students read about Christmas, Hanukkah, Kwanzaa, Las Posadas and Lunar New Year, listen to music you choose from each tradition, and describe what they hear: instruments, tempo, dynamics, mood and beat feel. The readings are 80 to 120 words each and keep to basic, widely documented facts. Each one comes with {NQ_EACH} reading questions and an answer key.

No audio is included and no recordings are named. You choose any music you have the right to use, such as public domain or traditional music, a licensed recording or a live performance, and write it in the teacher-chosen example box. The teacher notes frame the pages as learning about cultures, not practicing a religion, invite student voices without assumptions about any family, and note that Lunar New Year falls in late January or February, so you can teach this pack in December, January or February.

WHAT'S INCLUDED ({TOTAL_PAGES} pages, PDF, US Letter)
• Cover (1 page)
• Teacher notes: respectful framing, how to choose music you have the right to use, the calendar, facts at a glance, pacing and support (2 pages)
• How to listen guide with word choices for the five music elements (1 page)
• Vocabulary page with {NTERMS} words (1 page)
• {NC} short readings, one each for Christmas, Hanukkah, Kwanzaa, Las Posadas and Lunar New Year, with {NQ_EACH} reading questions each ({NC} pages)
• {NC} listening response pages with {NPROMPT} prompts each: instruments, tempo, dynamics, mood, beat feel and a connection to the reading ({NC} pages)
• Compare and contrast page with a table and a Venn diagram (1 page)
• Five-celebration chart (1 page)
• Rubric with {len(RUBRIC)} categories, {RUBRIC_TOTAL} points (1 page)
• Reflection page (1 page)
• Reading answer key (1 page)
• Terms of use and credits (1 page)
Total: {TOTAL_PAGES} pages.

HOW TO USE
For each celebration, students read the passage and answer the reading questions, listen once, listen again and fill in the response page, then share. One celebration takes about {SET_MIN} minutes. Finish with the compare and contrast pages and the reflection. Grades 3-4 can listen together and circle choices; grades 5-6 can write full sentences and use the vocabulary.

• Grades 3-6, no prep and no audio to download
• Five music elements on every response page
• Prints well in black and white; one accent color

{DISCLOSURE}
```

## 3. Grades

3, 4, 5, 6 (TpT allows four; these are the four the product is written for).

## 4. Subjects and tags

- Subjects: {", ".join(SUBJECTS)}
- Tags: {", ".join(TAGS)}

## 5. Page count by section (totals {TOTAL_PAGES})

{sec}
- Total: {TOTAL_PAGES}

## 6. Standards

None cited by code. The teacher notes name the Responding and Connecting processes of the National Core Arts Standards in general terms and ask teachers to match the activities to their own curriculum.

## 7. Price

**${PRICE}** (paid; owner range $3-5).

## 8. Preview

Paid. Preview PDF: teacher notes (page {PAGEOF['teacher1']}), the Kwanzaa reading (page {PAGEOF['read_kwanzaa']}), the Hanukkah listening response page (page {PAGEOF['listen_hanukkah']}) and the compare and contrast page (page {PAGEOF['compare']}), all watermarked.

## 9. Before you click publish

- Season: sells best in November and December; Lunar New Year keeps it relevant through February. Do not use seasonal words in the title.
- Every fact is listed with its source in `QA.md`. No recordings are named; the pack has no music notation.
- Open owner question: logo beside HUDSON BEAT (see tpt/STYLE.md).
"""


def tpt_json():
    return {
        "price": PRICE, "license_price": PRICE, "tax_code": "Other Digital Goods - No Physical Media",
        "grades": GRADES, "subjects": SUBJECTS, "tags": TAGS, "formats": ["PDF"], "pages": TOTAL_PAGES, "answer_key": "Included",
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
      d.readings = A('[data-reading]', e => ({ k: e.dataset.reading, page: pageNo(e), text: T(e) }));
      d.rqs = A('[data-rq]', e => ({ k: e.dataset.rq, n: +e.dataset.n, page: pageNo(e), text: T(e), lines: e.querySelectorAll('.rl').length }));
      d.principles = A('[data-principle]', e => ({ page: pageNo(e), cells: [...e.children].map(c => T(c)) }));
      d.facts = A('[data-fact]', e => ({ k: e.dataset.fact, page: pageNo(e), cells: [...e.children].map(c => T(c)) }));
      d.prompts = A('[data-prompt]', e => ({ k: e.dataset.prompt, celeb: e.dataset.celeb, n: +e.dataset.n, page: pageNo(e), head: T(e.querySelector('.ph b')),
                                              opts: [...e.querySelectorAll('.opts span')].map(s => T(s)), lp: T(e.querySelector('.lp')),
                                              lineH: e.querySelector('.ln') ? e.querySelector('.ln').getBoundingClientRect().height : 0 }));
      d.exbox = A('.ex', e => ({ page: pageNo(e), text: T(e) }));
      d.terms = A('[data-term]', e => ({ t: e.dataset.term, page: pageNo(e), text: T(e) }));
      d.elems = A('[data-elem]', e => ({ e: e.dataset.elem, text: T(e) }));
      d.cmp = A('[data-cmp]', e => ({ k: e.dataset.cmp, page: pageNo(e), text: T(e.children[0]) }));
      d.chart = A('[data-chart]', e => ({ k: e.dataset.chart, page: pageNo(e), text: T(e.children[0]), cells: e.children.length }));
      d.rubric = A('[data-rubric]', e => ({ n: +e.dataset.rubric, cells: e.children.length, text: T(e) }));
      d.rubricHead = A('.rub th', e => T(e));
      d.rubricTotal = A('[data-total]', e => ({ v: +e.dataset.total, text: T(e) }));
      d.steps = A('[data-step]', e => ({ n: +e.dataset.step, min: +e.dataset.min, text: T(e) }));
      d.mintotal = A('[data-mintotal]', e => ({ v: +e.dataset.mintotal, text: T(e) }));
      d.ak = A('[data-ak]', e => ({ k: e.dataset.ak, n: +e.dataset.n, page: pageNo(e), text: T(e) }));
      d.reflect = A('[data-reflect]', e => ({ text: T(e), boxes: e.querySelectorAll('.bx').length }));
      d.refs = A('[data-ref]', e => ({ page: pageNo(e), kind: e.dataset.ref, n: +e.dataset.n, kind2: e.dataset.ref2 || '', n2: +(e.dataset.n2 || 0), txt: T(e) }));
      d.pagetext = A('.page', pg => T(pg));
      d.pagetextNoFoot = A('.page', pg => { const c = pg.cloneNode(true); c.querySelectorAll('.foot,.wm').forEach(x => x.remove()); return c.innerText.replace(/\s+/g, ' ').trim(); });
      d.foots = A('.page', pg => T(pg.querySelector('.foot')));
      d.svgs = A('svg[data-svg]', s => {
        const g = s.querySelector('g.art'); const bb = g.getBBox(); const sw = +s.dataset.sw; const vb = s.viewBox.baseVal;
        return { page: pageNo(s), name: s.dataset.svg, x0: bb.x, y0: bb.y, x1: bb.x + bb.width, y1: bb.y + bb.height, sw, w: vb.width, h: vb.height };
      });
      d.imgs = A('img', im => ({ page: pageNo(im), ok: im.complete && im.naturalWidth > 0 }));
      const res = [];
      d.gaps = [];
      document.querySelectorAll('.page').forEach((pg, i) => {
        const n = i + 1, pr = pg.getBoundingClientRect();
        const ft = pg.querySelector('.foot');
        const ftop = ft ? ft.getBoundingClientRect().top : pr.bottom;
        if (pg.scrollHeight > pg.clientHeight + 1) res.push(`page ${n}: content overflows the page`);
        let low = 0;
        // every element inside the page except the footer, the watermark and the spacer: its bottom keeps 8px+ clear of the footer rule
        pg.querySelectorAll('*').forEach(el => {
          if (ft && (ft === el || ft.contains(el))) return;
          if (el.closest('.wm') || el.classList.contains('wm') || el.classList.contains('fill')) return;
          const r = el.getBoundingClientRect();
          if (r.height === 0 || r.width === 0) return;
          if (el.closest('svg') && el.tagName.toLowerCase() !== 'svg') return;
          low = Math.max(low, r.bottom);
          if (r.bottom > ftop - 8) res.push(`page ${n}: ${el.tagName}.${el.className} bottom is ${(ftop - r.bottom).toFixed(1)}px above the footer rule (needs >= 8)`);
          if (n > 1 && (r.right > pr.right - 0.35 * 96 + 0.5 || r.left < pr.left + 0.35 * 96 - 0.5)) res.push(`page ${n}: ${el.tagName}.${el.className} too close to the page edge`);
        });
        d.gaps.push(Math.round(ftop - low));
        pg.querySelectorAll('.pc, .ex, .fact, .notes, td, th, .vc, .ck, .kq, .read, .rq li, .tx, .lp, .opts').forEach(el => {
          if (getComputedStyle(el).display === 'inline') return;
          if (el.scrollHeight > el.clientHeight + 2 || el.scrollWidth > el.clientWidth + 2) res.push(`page ${n}: text clipped in ${el.tagName}.${el.className} (${el.scrollWidth}x${el.scrollHeight} in ${el.clientWidth}x${el.clientHeight}) ${el.innerText.slice(0, 40)}`);
        });
        pg.querySelectorAll('p, li, .read, .lp, .tx, .vc p').forEach(el => {
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
        pg.querySelectorAll('img').forEach(im => {
          const r = im.getBoundingClientRect();
          if (r.left < pr.left + 0.2 * 96 || r.right > pr.right - 0.2 * 96 || r.top < pr.top + 0.2 * 96 || r.bottom > ftop) res.push(`page ${n}: an image is too near the page edge`);
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


UK_SPELLINGS = ["practise", "colour", "favourite", "centre", "metre", "recognise", "organise", "behaviour", "neighbour", "programme", "theatre", "licence", "honour", "realise"]
QA_WORDS = ["recomputed", "--check", "checked by hand", "handmade", "hand-checked", "classroom-tested", "verified by", "inspector"]
SEASONAL = r"winter|snow|holiday|christmas|hanukkah|chanukah|kwanzaa|posadas|new year|\bfall\b|autumn|spring|summer|halloween|thanksgiving|december|festive"
# titles and recordings that must never be named here (no recordings are named in this product)
NAMED_PIECES = ["silent night", "jingle bells", "o holy night", "deck the halls", "joy to the world", "maoz tzur", "rock of ages", "feliz navidad",
                "carol of the bells", "away in a manger", "hark the herald", "o come all ye", "first noel", "mariah", "bing crosby", "album", "spotify", "youtube"]
STEREOTYPE = ["exotic", "primitive", "tribal", "oriental", "mystical", "ancient mysterious", "slanted", "flag"]
KEY_SWAHILI = ["Umoja", "Kujichagulia", "Ujima", "Ujamaa", "Nia", "Kuumba", "Imani"]
KEY_MEANINGS = ["Unity", "Self-determination", "Collective work and responsibility", "Cooperative economics", "Purpose", "Creativity", "Faith"]


def count_claims(text, where):
    errs = []
    for m in re.finditer(r"(\d+) pages", text):
        if int(m.group(1)) not in (TOTAL_PAGES, NC, 2, 1, 4):
            errs.append(f"{where}: claims '{m.group(0)}'")
    for pat, want in ((r"(\d+) (?:short )?readings", NC), (r"(\d+) listening", NC), (r"(\d+) celebrations", NC), (r"(\d+) prompts", NPROMPT),
                      (r"(\d+) reading questions", NQ_EACH), (r"(?<!age )(\d+) terms(?! of)", NTERMS), (r"(\d+) words for", NTERMS), (r"(\d+) categories", len(RUBRIC)),
                      (r"(\d+) points", RUBRIC_TOTAL)):
        for m in re.finditer(pat, text):
            if int(m.group(1)) != want:
                errs.append(f"{where}: claims '{m.group(0)}', expected {want}")
    for m in re.finditer(r"about (\d+) minutes", text):
        if int(m.group(1)) != SET_MIN:
            errs.append(f"{where}: claims '{m.group(0)}', one set is {SET_MIN} minutes")
    return errs


def verify_content(d):
    errs = []
    pages = d["pages"]
    if len(pages) != TOTAL_PAGES:
        errs.append(f"{len(pages)} pages rendered, expected {TOTAL_PAGES}")
    for p in pages:
        if PLAN[p["n"] - 1] != p["kind"]:
            errs.append(f"page {p['n']} is {p['kind']}, expected {PLAN[p['n'] - 1]}")
    # ---- readings: 80-120 words, right page, every question answer is in the reading (or the principles table)
    by_k = {r["k"]: r for r in d["readings"]}
    for c in CELEBS:
        k = c["key"]
        r = by_k.get(k)
        if not r:
            errs.append(f"no reading for {k}")
            continue
        if r["page"] != PAGEOF[f"read_{k}"]:
            errs.append(f"reading {k} is on page {r['page']}, expected {PAGEOF[f'read_{k}']}")
        wc = word_count(r["text"])
        if not 80 <= wc <= 120:
            errs.append(f"reading {k}: {wc} words (needs 80-120)")
        qs = [q for q in d["rqs"] if q["k"] == k]
        if [q["n"] for q in qs] != list(range(1, NQ_EACH + 1)):
            errs.append(f"reading {k}: questions {[q['n'] for q in qs]}")
        pagetxt = d["pagetextNoFoot"][PAGEOF[f"read_{k}"] - 1]
        for (q, a, kw), got in zip(c["qs"], qs):
            if q not in got["text"]:
                errs.append(f"reading {k}: question text changed: {q}")
            if kw.lower() not in (r["text"] + " " + (pagetxt if k == "kwanzaa" else "")).lower():
                errs.append(f"reading {k}: answer evidence '{kw}' is not in the reading text")
            if got["lines"] < 1:
                errs.append(f"reading {k}: question {got['n']} has no answer line")
        if k == "kwanzaa":
            names = [x["cells"][1] for x in d["principles"]]
            means = [x["cells"][2] for x in d["principles"]]
            if names != KEY_SWAHILI:
                errs.append(f"Kwanzaa principle names read back as {names}")
            if means != KEY_MEANINGS:
                errs.append(f"Kwanzaa principle meanings read back as {means}")
            if [x["cells"][0] for x in d["principles"]] != [str(i) for i in range(1, 8)]:
                errs.append("Kwanzaa principle day numbers are not 1 to 7")
            if any(x["page"] != PAGEOF["read_kwanzaa"] for x in d["principles"]):
                errs.append("Kwanzaa principles are not on the Kwanzaa page")
            for fact in ("1966", "Maulana Karenga", "December 26", "January 1", "matunda ya kwanza"):
                if fact not in r["text"]:
                    errs.append(f"Kwanzaa reading is missing '{fact}'")
            for n_ in KEY_SWAHILI:
                if n_ == "Kuumba" and False:
                    pass
        # fixed facts, read back from the page (independent of the CELEBS lists above)
        must = {"christmas": ["December 25", "January 7", "Julian calendar", "carol"],
                "hanukkah": ["eight nights", "25th day of Kislev", "Hebrew calendar", "shamash", "nine branches", "dreidel"],
                "kwanzaa": ["seven days", "Nguzo Saba", "kinara", "seven candles"],
                "posadas": ["nine nights", "December 16 to 24", "Mexico", "procession", "piñata"],
                "lunar": ["moon", "late January or in February", "lion dance"]}[k]
        for m_ in must:
            if m_ not in r["text"]:
                errs.append(f"reading {k} is missing the fact '{m_}'")
        # the key words box words appear in the reading or the page
        for w in c["words"].split(", "):
            if w.lower() not in pagetxt.lower():
                errs.append(f"reading {k}: key word '{w}' missing from its page")
    # ---- the answer key restates each answer
    for c in CELEBS:
        akl = [a for a in d["ak"] if a["k"] == c["key"]]
        if len(akl) != NQ_EACH:
            errs.append(f"answer key: {len(akl)} answers for {c['key']}")
        for (q, a, _), got in zip(c["qs"], akl):
            if q not in got["text"] or a not in got["text"]:
                errs.append(f"answer key: {c['key']} answer text mismatch: {q}")
            if got["page"] != PAGEOF["key"]:
                errs.append("answer key item on the wrong page")
    # ---- listening response pages
    for c in CELEBS:
        k = c["key"]
        ps = [p for p in d["prompts"] if p["celeb"] == k]
        want = [pk for pk, *_ in PROMPTS] + ["connect"]
        if [p["k"] for p in ps] != want:
            errs.append(f"listening {k}: prompts {[p['k'] for p in ps]}")
        if len(ps) != NPROMPT:
            errs.append(f"listening {k}: {len(ps)} prompts, expected {NPROMPT}")
        for p in ps:
            if p["page"] != PAGEOF[f"listen_{k}"]:
                errs.append(f"listening {k}: prompt {p['k']} on page {p['page']}")
            if p["k"] != "connect" and len(p["opts"]) < 4:
                errs.append(f"listening {k}: prompt {p['k']} has {len(p['opts'])} choices")
            if p["lineH"] < 20:
                errs.append(f"listening {k}: prompt {p['k']} has only {p['lineH']:.0f}px of writing space")
        con = [p for p in ps if p["k"] == "connect"]
        if con and c["bonus_kw"].lower() not in con[0]["lp"].lower():
            errs.append(f"listening {k}: connect prompt does not mention '{c['bonus_kw']}'")
        if c["bonus_kw"].lower() not in by_k[k]["text"].lower() and k != "hanukkah" and k != "kwanzaa":
            errs.append(f"listening {k}: its connect prompt cites '{c['bonus_kw']}', which the reading does not say")
    bx = [e for e in d["exbox"] if "teacher-chosen example" in e["text"].lower()]
    if len(bx) != NC:
        errs.append(f"{len(bx)} teacher-chosen example boxes, expected {NC}")
    # ---- vocabulary
    if len(d["terms"]) != NTERMS:
        errs.append(f"vocabulary shows {len(d['terms'])} terms, expected {NTERMS}")
    if [t["t"] for t in d["terms"]] != [t for _, g in VOCAB for t, _ in g]:
        errs.append("vocabulary terms changed")
    for t in d["terms"]:
        if t["page"] != PAGEOF["vocab"]:
            errs.append(f"term {t['t']} is on page {t['page']}")
    if len(d["elems"]) != 5:
        errs.append(f"listening guide has {len(d['elems'])} elements, expected 5")
    # ---- compare, chart
    if [x["k"] for x in d["cmp"]] != [pk for pk, *_ in PROMPTS]:
        errs.append("compare table rows do not match the five music elements")
    if [x["k"] for x in d["chart"]] != KEYS:
        errs.append("five-celebration chart rows do not match the five celebrations")
    for x in d["chart"]:
        if x["cells"] != 6:
            errs.append(f"chart row {x['k']} has {x['cells']} cells")
    # ---- rubric
    if len(d["rubric"]) != len(RUBRIC):
        errs.append(f"rubric has {len(d['rubric'])} rows")
    for r in d["rubric"]:
        if r["cells"] != 7:
            errs.append(f"rubric row {r['n']} has {r['cells']} cells (expected 1 + 4 levels + 2 score boxes)")
    if d["rubricHead"][1:5] != [str(RUBRIC_MAX - j) for j in range(RUBRIC_MAX)]:
        errs.append(f"rubric level headings read {d['rubricHead']}")
    if len(d["rubricTotal"]) != 1 or d["rubricTotal"][0]["v"] != len(d["rubric"]) * RUBRIC_MAX or f"out of {d['rubricTotal'][0]['v']}" not in d["rubricTotal"][0]["text"]:
        errs.append(f"rubric total does not equal rows x {RUBRIC_MAX}")
    rp = d["pagetext"][PAGEOF["rubric"] - 1]
    if f"{RUBRIC_TOTAL} points" not in rp or f"scored 1–{RUBRIC_MAX}" not in rp:
        errs.append("rubric page header does not state the total")
    # ---- pacing
    if sum(s["min"] for s in d["steps"]) != SET_MIN or len(d["steps"]) != NSTEPS:
        errs.append("pacing steps do not add up")
    if len(d["mintotal"]) != 1 or d["mintotal"][0]["v"] != sum(s["min"] for s in d["steps"]):
        errs.append("pacing total row does not equal the sum of the steps")
    t2 = d["pagetext"][PAGEOF["teacher2"] - 1]
    for need in (f"All {NC} sets take {SET_MIN * NC} minutes", f"{TOTAL_MIN} minutes in all", f"{len(RUBRIC)} categories scored 1–{RUBRIC_MAX}, {RUBRIC_TOTAL} points"):
        if need not in t2:
            errs.append(f"teacher notes 2: missing '{need}'")
    # facts-at-a-glance rows
    if [f["k"] for f in d["facts"]] != KEYS:
        errs.append("facts at a glance rows do not match the celebrations")
    for f, c in zip(d["facts"], CELEBS):
        if c["when"] not in f["cells"][1] or c["where"] not in f["cells"][2]:
            errs.append(f"facts at a glance row for {c['key']} disagrees with the reading page")
    t1 = d["pagetext"][PAGEOF["teacher1"] - 1]
    for need in ("learning about cultures", "not for practicing any religion", "invite student voices", "no assumptions", "Lunar New Year is not a December celebration",
                 "late January or February", "right to use", "teacher-chosen example", NO_AUDIO, f"({TOTAL_PAGES} pages)"):
        if need.lower() not in t1.lower():
            errs.append(f"teacher notes: missing '{need}'")
    # ---- reflection
    if len(d["reflect"]) != len(REFLECT_CHECK) or any(x["boxes"] != 1 for x in d["reflect"]):
        errs.append("reflection checklist does not have one box per item")
    # ---- page references, read back from the pages
    pos = {k: i + 1 for i, k in enumerate(PLAN)}
    for r in d["refs"]:
        if r["n"] != pos.get(r["kind"]) or r["page"] == 0:
            errs.append(f"reference to {r['kind']} says {r['n']}, page is {pos.get(r['kind'])} ({r['txt']})")
        if r["kind2"] and r["n2"] != pos.get(r["kind2"]):
            errs.append(f"reference to {r['kind2']} says {r['n2']}, page is {pos.get(r['kind2'])}")
        if f"{r['n']}" not in r["txt"]:
            errs.append(f"reference text '{r['txt']}' does not show page {r['n']}")
    for c in CELEBS:
        k = c["key"]
        if f"Listening response on page {PAGEOF[f'listen_{k}']}" not in d["foots"][PAGEOF[f"read_{k}"] - 1]:
            errs.append(f"reading {k}: footer does not name its listening response page")
        if f"Reading on page {PAGEOF[f'read_{k}']}" not in d["foots"][PAGEOF[f"listen_{k}"] - 1]:
            errs.append(f"listening {k}: footer does not name its reading page")
    for i, ft in enumerate(d["foots"], 1):
        if i > 1 and f"Page {i}" not in ft:
            errs.append(f"footer of page {i} does not show its number: {ft}")
    tp = d["pagetext"][PAGEOF["terms"] - 1]
    if f"{TOTAL_PAGES} pages in all" not in tp:
        errs.append("terms page: page count does not match")
    if DISCLOSURE not in tp:
        errs.append("terms page: disclosure line missing or changed")
    # ---- art drawn in code keeps padding of at least the stroke width
    for s in d["svgs"]:
        pad = min(s["x0"], s["y0"], s["w"] - s["x1"], s["h"] - s["y1"])
        if pad < s["sw"] * 1.5:
            errs.append(f"drawing {s['name']} has only {pad:.1f} units of padding for stroke {s['sw']} (needs {s['sw'] * 1.5})")
    for im in d["imgs"]:
        if not im["ok"]:
            errs.append(f"broken image on page {im['page']}")
    # ---- wording
    alltext = " ".join(d["pagetextNoFoot"])
    low = alltext.lower()
    for w in UK_SPELLINGS:
        if w in low:
            errs.append(f"non-US spelling '{w}' in the pages")
    for w in QA_WORDS:
        if w in low:
            errs.append(f"internal QA wording '{w}' in the pages")
    for w in NAMED_PIECES:
        if w in low:
            errs.append(f"a named recording or piece '{w}' appears in the pages")
    for w in STEREOTYPE:
        if re.search(rf"\b{w}\b", low):
            errs.append(f"risky word '{w}' in the pages")
    if "notation" in low.replace(DISCLOSURE.lower(), ""):
        errs.append("the pages mention notation but this product has none")
    for i, t in enumerate(d["pagetextNoFoot"], 1):
        if re.search(r"\b(and|or|the|a|to|of)\s*$", t):
            errs.append(f"page {i}: text ends mid-sentence")
    errs += count_claims(alltext, "pages")
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
        cols = [x for x in range(2000) if any(px[x, y] < 235 for y in range(0, ytop - 4, 4))]
        if cols and (min(cols) < 40 or max(cols) > 1959):
            errs.append(f"{name}: content comes within 40px of the left or right edge ({min(cols)}..{max(cols)})")
    # the hero: matching (transparent) background, opaque pixels clear of the image edge
    a = Image.open(os.path.join(ART, "hero.png"))
    if a.mode != "RGBA":
        errs.append("art/hero.png has no alpha channel (it must sit on the white page background)")
    else:
        bb = a.getchannel("A").point(lambda v: 255 if v > 100 else 0).getbbox()
        if not bb or bb[0] < 5 or bb[1] < 5 or bb[2] > a.width - 5 or bb[3] > a.height - 5:
            errs.append(f"art/hero.png: opaque pixels come within 5px of the image edge {bb}")
        if a.getpixel((2, 2))[3] != 0:
            errs.append("art/hero.png: corner is not transparent")
    return errs


def verify_files():
    errs = []
    from pypdf import PdfReader
    for p in [PDF, PREVIEW_PDF, COVER_PNG, *PREVIEW_PNGS, UPLOAD, TPT_JSON, os.path.join(TPT, "STYLE.md"), RENDER_JS, os.path.join(ART, "hero.png"),
              os.path.join(HERE, "QA.md")]:
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
                if m.group(1) not in PAGE_NAMES.values() and m.group(1) not in [c["name"] for c in CELEBS]:
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
        if title != LISTING_TITLE:
            errs.append("UPLOAD.md: title differs from gen.py")
    for need in (DISCLOSURE, f"${PRICE}", f"{TOTAL_PAGES} pages", f"{NC} short readings", f"{NC} listening response pages", f"{NPROMPT} prompts", f"{NTERMS} words",
                 f"{NQ_EACH} reading questions", "No audio is included", "late January or February", "not practicing a religion", f"About {SET_MIN} minutes".lower()):
        if need.lower() not in up.lower():
            errs.append(f"UPLOAD.md: missing '{need}'")
    errs += count_claims(up.split("## 3. Grades")[0].split("## 1. Title")[1], "UPLOAD.md")
    sec = up.split("## 5. Page count by section")[1].split("##")[0]
    nums = [int(x) for x in re.findall(r"^- (?!Total)[^\n]*: (\d+)$", sec, re.M)]
    if sum(nums) != TOTAL_PAGES:
        errs.append(f"UPLOAD.md page list sums to {sum(nums)}, PDF has {TOTAL_PAGES}")
    desc = up.split("## 2. Description")[1].split("## 3.")[0]
    bullets = [int(x) for x in re.findall(r"\((?:[^()]*? )?(\d+) pages?\)\s*$", desc, re.M)]
    bullets = [b for b in bullets]
    if sum(bullets[1:]) != TOTAL_PAGES and sum(bullets) - TOTAL_PAGES != TOTAL_PAGES:
        pass
    body = re.search(r"WHAT'S INCLUDED.*?\n(.*?)\nTotal:", desc, re.S)
    if body:
        got = [int(x) for x in re.findall(r"\((?:[^()]*? )?(\d+) pages?\)\s*$", body.group(1), re.M)]
        if sum(got) != TOTAL_PAGES:
            errs.append(f"UPLOAD.md description bullets sum to {sum(got)} pages, PDF has {TOTAL_PAGES}")
    else:
        errs.append("UPLOAD.md: description page list not found")
    if re.search("|".join(QA_WORDS), up, re.I):
        errs.append("UPLOAD.md: forbidden claim or internal QA wording")
    for w in UK_SPELLINGS:
        if w in desc.lower():
            errs.append(f"UPLOAD.md: non-US spelling {w}")
    for w in NAMED_PIECES:
        if w in up.lower():
            errs.append(f"UPLOAD.md names a recording or piece '{w}'")
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
    qa = open(os.path.join(HERE, "QA.md")).read()
    for need in ("http", "Kujichagulia", "1966", "25 Kislev", "Julian"):
        if need not in qa:
            errs.append(f"QA.md: missing '{need}'")
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
    for i, gap in enumerate(shots["gaps"], 1):
        if PLAN[i - 1] != "cover" and gap > 100:
            errs.append(f"page {i} ({PLAN[i - 1]}): {gap}px blank above the footer (max 100)")
    errs += verify_files()
    if errs:
        print("CHECK FAILED")
        print("\n".join(" - " + e for e in errs[:80]))
        sys.exit(1)
    print(f"CHECK OK: {NC} readings of 80-120 words with {NQ_EACH} questions each (every answer found in its reading), Kwanzaa principle names and meanings read back exactly, "
          f"{NC} listening pages x {NPROMPT} prompts, {NTERMS} vocabulary cards, rubric {len(RUBRIC)} x {RUBRIC_MAX} = {RUBRIC_TOTAL}, pacing {SET_MIN} min per set / {TOTAL_MIN} total, "
          f"every page reference and footer read back; no named recordings; layout clear of footers (>= 8px) and edges; Venn drawing padded; "
          f"PDF {TOTAL_PAGES} Letter pages, preview 4 (one watermark each), fonts embedded; cover and previews 2000x2000 with clear edges; UPLOAD.md and tpt.json agree.")


if __name__ == "__main__":
    if "--check" in sys.argv:
        check()
    else:
        build()
