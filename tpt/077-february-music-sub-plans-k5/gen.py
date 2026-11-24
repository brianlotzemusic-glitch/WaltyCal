#!/usr/bin/env python3
"""February Music Sub Plans K-5 (TpT 077): monthly sub plan bundle, build the resource and verify it.

    python3 gen.py            build everything (PDFs, PNGs, tpt.json, UPLOAD.md, SOURCES.md) into this folder
    python3 gen.py --check    verify timings, keys, word search, decode, bingo, hard rules, pages, layout, files

Eight no-prep, no-tech music days for a substitute, themed to February: Black History Month musicians (short facts about Scott Joplin,
Duke Ellington, Ella Fitzgerald, Louis Armstrong and Florence Price), Valentine's Day (the heartbeat is a steady beat), Lunar New Year
(drums, cymbals and gongs of the lion dance) and Groundhog Day. Each day has a scripted plan page and two student sheets (K-2 and 3-5).
Rhythm work is speech rhythm (clap the syllables of words): the sub never reads notation, sings or plays, and no recording is needed.
Every key is computed from the data in this file and re-read from the PDF text.
All text, chants, games and drawings are original; the heart-drum scene is the pre-made art in art/hero.png.
Rendering uses Playwright + Chromium through ../tools/render.js, fonts from ../fonts.
"""
import json
import os
import random
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

SLUG = "february-music-sub-plans-k5"
PDF = os.path.join(HERE, f"{SLUG}.pdf")
PREVIEW_PDF = os.path.join(HERE, f"{SLUG}-PREVIEW.pdf")
COVER_PNG = os.path.join(HERE, "cover.png")
PREVIEW_PNGS = [os.path.join(HERE, f"preview-{i}.png") for i in (1, 2, 3)]
UPLOAD = os.path.join(HERE, "UPLOAD.md")
SOURCES = os.path.join(HERE, "SOURCES.md")
TPT_JSON = os.path.join(HERE, "tpt.json")

STORE = "Brian Lotze"
BRAND = "Hudson Beat"
YEAR = 2026
ACCENT = "#A8244B"        # February raspberry (Valentine's red-pink; white text on it passes contrast)
ACCENT_LIGHT = "#59A5DB"       # the hero art's blue, used for drawing fills
TITLE = "February Music Sub Plans"
PRICE = "15.00"
DISCLOSURE = "Created with the help of digital and AI tools. Notation and answer keys are verified before release."
LISTING_TITLE = "February Music Sub Plans K-5 | Black History Month Musicians | No Prep, No Tech"
TAGS = ["Black History Month", "Valentine's Day", "Lunar New Year", "Groundhog Day", "Presidents' Day"]
GRADES = ["kindergarten", "2nd-grade", "3rd-grade", "5th-grade"]

# ---------------------------------------------------------------- vocabulary and syllables (speech rhythm)
# a word's syllables are written with hyphens; one syllable = ta (one clap), two syllables in one beat = ti-ti
WORDS = {w.replace("-", "").lower(): w for w in [
    "drum", "gong", "heart", "beat", "love", "kind", "share", "jazz", "swing", "moon", "glow", "bright", "night", "cheer", "price",
    "jop-lin", "arm-strong", "rag-time", "trum-pet", "lan-tern", "cym-bal", "heart-beat", "ground-hog", "shad-ow", "mu-sic", "rhy-thm", "con-cert", "tu-ner",
    "pi-an-o", "val-en-tine", "el-ling-ton", "fitz-ger-ald", "or-ches-tra", "sym-pho-ny", "com-pos-er", "band-lead-er", "con-duc-tor", "ra-di-o", "syl-la-ble"]}
EXPECT = {"drum": 1, "gong": 1, "heart": 1, "beat": 1, "love": 1, "kind": 1, "share": 1, "jazz": 1, "swing": 1, "moon": 1, "glow": 1,
          "bright": 1, "night": 1, "cheer": 1, "price": 1, "joplin": 2, "armstrong": 2, "ragtime": 2, "trumpet": 2, "lantern": 2,
          "cymbal": 2, "heartbeat": 2, "groundhog": 2, "shadow": 2, "music": 2, "rhythm": 2, "concert": 2, "tuner": 2,
          "piano": 3, "valentine": 3, "ellington": 3, "fitzgerald": 3, "orchestra": 3, "symphony": 3, "composer": 3,
          "bandleader": 3, "conductor": 3, "radio": 3, "syllable": 3}
SYL = {"q": "ta", "e": "ti-ti", "r": "shh"}      # 1 syllable = ta, 2 = ti-ti, silent beat = shh


def nsyl(w):
    return len(WORDS[w.lower().replace("-", "")].split("-"))


def wd(w):
    return WORDS[w.lower().replace("-", "")]


def beat_kind(word):
    if word == "shh":
        return "r"
    return {1: "q", 2: "e"}[nsyl(word)]


MUSICIAN_FACT = "Scott Joplin, Duke Ellington, Ella Fitzgerald, Louis Armstrong and Florence Price"
D1_K2_TEXT = [
    "February is the second month of the year.",
    "Every February, the United States celebrates Black History Month.",
    "Scott Joplin wrote ragtime music for the piano, and his Maple Leaf Rag came out in 1899.",
    "Duke Ellington was a pianist and composer who led his own orchestra for about fifty years.",
    "Ella Fitzgerald was a famous jazz singer who used her voice like an instrument.",
    "Louis Armstrong was a jazz trumpeter from New Orleans.",
    "Florence Price wrote a symphony, and the Chicago Symphony Orchestra performed it in 1933.",
    "Valentine’s Day is on February 14, and your heart keeps a steady beat all day long.",
]
D1_K2_Q = [("Scott Joplin wrote ___ music for the piano.", ["opera", "ragtime", "polka"], 1),
           ("Louis Armstrong was a jazz ___.", ["drummer", "violinist", "trumpeter"], 2),
           ("Ella Fitzgerald was a famous jazz ___.", ["singer", "dancer", "painter"], 0),
           ("Florence Price wrote a ___ for an orchestra.", ["poster", "symphony", "calendar"], 1)]
D1_35_TEXT = (
    "Every February, the United States observes Black History Month. It grew from Negro History Week, which historian Carter G. Woodson started in "
    "February 1926. Music is one way to meet people who shaped American culture. Scott Joplin, a composer and pianist, became known as the King of "
    "Ragtime, and his Maple Leaf Rag was published in 1899. Duke Ellington was born in Washington, D.C., in 1899. He was a pianist, composer and "
    "bandleader who led his own orchestra from 1924 until 1974. Louis Armstrong, born in New Orleans, was a jazz trumpeter and one of the most "
    "influential artists in jazz history. Ella Fitzgerald, a jazz singer, was famous for scat, which uses the voice like an instrument. Florence Price, "
    "born in Little Rock, Arkansas, was a composer. Her Symphony No. 1 was performed by the Chicago Symphony Orchestra in 1933, and she is known as the "
    "first African American woman to have a symphony performed by a major U.S. orchestra. February also holds Valentine’s Day, when people share kind "
    "words, and Lunar New Year, a celebration based on the Moon’s calendar. Its date changes every year.")
D1_35_Q = [("What did historian Carter G. Woodson start in February 1926?", "Negro History Week"),
           ("Which Scott Joplin piece was published in 1899?", "Maple Leaf Rag"),
           ("Besides pianist and composer, what was Duke Ellington?", "A bandleader"),
           ("What is scat?", "Using the voice like an instrument"),
           ("What is Florence Price known for?", "First African American woman to have a symphony performed by a major U.S. orchestra")]
D1_K2_NEED = ("second month", "Black History Month", "ragtime", "trumpeter", "singer", "symphony", "February 14")
D1_35_NEED = ("Negro History Week", "Maple Leaf Rag", "bandleader", "voice like an instrument", "first African American woman", "1933", "1899")

# ---------------------------------------------------------------- Day 2 rhythm words
D2_K2_A = ["drum", "heart", "trum-pet", "cym-bal", "val-en-tine", "pi-an-o"]            # color one circle per clap
D2_K2_B = ["jazz", "rag-time", "or-ches-tra", "ground-hog"]                              # circle 1, 2 or 3 claps
D2_35_A = ["price", "arm-strong", "el-ling-ton", "fitz-ger-ald", "com-pos-er", "cym-bal", "heart-beat", "val-en-tine"]
D2_35_B = ["drum", "lan-tern", "pi-an-o", "jazz", "shad-ow", "sym-pho-ny", "band-lead-er", "moon", "gong"]   # sort: 1, 2, 3 claps
D2_35_BANK = ["drum", "heart", "beat", "love", "kind", "jazz", "swing", "trum-pet", "lan-tern", "rag-time", "cym-bal", "moon"]
D2_35_EX = ["drum", "heart", "lan-tern", "shh"]      # example four-beat chant (word per beat, shh = silent beat)

# ---------------------------------------------------------------- Day 4 picture cards (drawn in code)
CARDS = [("heart", "Pat your chest softly to a steady beat."), ("drum", "Tap a drum on your legs, steady and strong."),
         ("lantern", "Sway slowly from side to side, like a lantern in the breeze."), ("trumpet", "Hold a pretend trumpet and march in place."),
         ("piano", "Wiggle your fingers on pretend piano keys in the air."), ("cymbal", "Bring your hands together in a crash, then freeze with hands apart."),
         ("gong", "Reach up high, then lower your arms slowly like a ringing gong."), ("card", "Tiptoe and pretend to hand a kind card to a friend.")]

# ---------------------------------------------------------------- Day 5 puzzles
MATCH = ["heart", "drum", "lantern", "trumpet", "piano", "gong"]      # K-2: word -> picture (shuffled on the page)
MATCH_PIC_ORDER = [4, 2, 5, 0, 3, 1]                                         # right column order: index into MATCH
TRACE = ["HEART", "DRUM", "BEAT", "JAZZ"]
WS_WORDS = ["FEBRUARY", "ELLINGTON", "ARMSTRONG", "FITZGERALD", "JOPLIN", "PRICE", "TRUMPET", "LANTERN", "HEARTBEAT", "RAGTIME", "CYMBAL", "DRUM"]
WS_N = 12
WS_DIRS = [(0, 1), (1, 0), (1, 1)]
BAD_WORDS = ["SEX", "ASS", "FUK", "FUC", "DIE", "DEAD", "KILL", "POO", "PEE", "BUTT", "DAMN", "HELL", "GUN", "NAZI", "TIT", "CUM",
             "UGLY", "DUMB", "HATE", "PIS", "DICK", "COCK", "SHIT", "FART", "BOOB", "CRAP", "SUCK", "STUPID", "WAR", "GOD", "DRUG", "BOMB"]
BAD_WORDS = [b for b in BAD_WORDS if not any(b in w or b in w[::-1] for w in WS_WORDS)]   # hidden words inside our own list are not counted
ALL_DIRS = [(dr, dc) for dr in (-1, 0, 1) for dc in (-1, 0, 1) if (dr, dc) != (0, 0)]
DECODE_MSG = ["YOUR", "HEARTBEAT", "IS", "A", "STEADY", "BEAT"]


def count_word(grid, w):
    n = len(grid)
    c = 0
    for r in range(n):
        for k in range(n):
            for dr, dc in ALL_DIRS:
                if all(0 <= r + dr * i < n and 0 <= k + dc * i < n and grid[r + dr * i][k + dc * i] == w[i] for i in range(len(w))):
                    c += 1
    return c


def make_wordsearch(seed=7077):
    rnd = random.Random(seed)
    for _ in range(4000):
        g = [[None] * WS_N for _ in range(WS_N)]
        place = {}
        ok = True
        for w in sorted(WS_WORDS, key=len, reverse=True):
            for _try in range(400):
                dr, dc = rnd.choice(WS_DIRS)
                r = rnd.randrange(WS_N - (len(w) - 1) * dr)
                c = rnd.randrange(WS_N - (len(w) - 1) * dc)
                cells = [(r + dr * i, c + dc * i) for i in range(len(w))]
                if all(g[y][x] in (None, w[i]) for i, (y, x) in enumerate(cells)):
                    for i, (y, x) in enumerate(cells):
                        g[y][x] = w[i]
                    place[w] = cells
                    break
            else:
                ok = False
                break
        if not ok:
            continue
        if len({(c[1][0] - c[0][0], c[1][1] - c[0][1]) for c in place.values()}) < 3:
            continue
        for y in range(WS_N):
            for x in range(WS_N):
                if g[y][x] is None:
                    g[y][x] = rnd.choice("ABCDEFGHIKLMNOPRSTUVWY")
        if all(count_word(g, w) == 1 for w in WS_WORDS) and not any(count_word(g, b) for b in BAD_WORDS):
            return g, place
    raise SystemExit("word search: no clean grid found")


GRID, PLACE = make_wordsearch()

# ---------------------------------------------------------------- Day 6 jobs
JOBS = [("composer", "writes original music for others to perform"),
        ("conductor", "leads an orchestra or other group so the musicians stay together"),
        ("piano tuner", "adjusts a piano’s strings so it sounds in tune"),
        ("radio host", "talks with listeners and shares music, news and interviews"),
        ("music teacher", "helps students learn about music")]
D6_K2_TEXT = [
    "Many different people help music happen.",
    "A composer writes new music. Scott Joplin and Florence Price were composers.",
    "A conductor leads a group of musicians so they stay together.",
    "Duke Ellington led his own orchestra, so he was a bandleader.",
    "A piano tuner fixes a piano so that it sounds just right.",
    "A radio host talks with listeners and shares music.",
    "A music teacher helps students learn about music.",
]
D6_K2_Q = [("Who writes new music?", ["piano tuner", "composer"], 1),
           ("Who fixes a piano so it sounds right?", ["piano tuner", "radio host"], 0),
           ("Who helps students learn about music?", ["conductor", "music teacher"], 1)]
D6_35_TEXT = (
    "Every piece of music starts somewhere, and many different jobs help it reach listeners. A composer writes and arranges original music. Scott Joplin and "
    "Florence Price were both composers. A conductor, also called a music director, leads an orchestra or another group so that the musicians stay together. "
    "Duke Ellington led his own orchestra for about fifty years, so he was a bandleader as well as a composer. A piano tuner adjusts the tension of a piano’s "
    "strings so that the instrument sounds in tune. A radio host broadcasts music, news and weather, interviews guests, and often specializes in one kind of "
    "music. A music teacher helps students learn how music works and gives them chances to try it. All of these jobs need careful listening, and most of them "
    "need teamwork. Imagine that you lead a brand new orchestra. Which job from this list would you most want to add first, and why?")
D6_35_MATCH_ORDER = [3, 0, 4, 2, 1]       # description column order (indexes into JOBS)

D7_CARDS = ["heart", "drum", "gong", "love", "jazz", "swing", "trum-pet", "lan-tern", "cym-bal", "kind", "shad-ow", "shh"]

# ---------------------------------------------------------------- Day 8 bingo
BINGO = [  # (answer, clue); the first 12 are on the K-2 board bank
    ("HEART", "The muscle in your chest that makes a steady beat."),
    ("DRUM", "An instrument you tap with your hands or with sticks."),
    ("LANTERN", "A paper light that people often hang for Lunar New Year."),
    ("GONG", "A big metal disc that is struck and makes a long, ringing sound."),
    ("TRUMPET", "The shiny brass instrument that Louis Armstrong is famous for."),
    ("PIANO", "The instrument with black and white keys that Scott Joplin wrote music for."),
    ("FEBRUARY", "The month with Valentine’s Day, Groundhog Day and Black History Month."),
    ("SHADOW", "On February 2, people watch to see if a groundhog sees this dark shape."),
    ("CYMBAL", "A round metal plate that crashes when two are hit together, used in the lion dance."),
    ("BEAT", "The steady pulse in music that you can pat."),
    ("JAZZ", "The music style of Louis Armstrong, Ella Fitzgerald and Duke Ellington."),
    ("ORCHESTRA", "A big group of musicians who make music together."),
    ("RAGTIME", "The lively piano music that Scott Joplin made famous."),
    ("SYMPHONY", "A long piece of music written for an orchestra. Florence Price wrote one."),
    ("ELLINGTON", "Duke ___ was a pianist, composer and bandleader."),
    ("ARMSTRONG", "Louis ___ was a famous trumpeter from New Orleans."),
]
BINGO_K2 = 12          # the K-2 board has exactly this many squares (3 across, 4 down) and this many words in its bank
BINGO_K2_COLS = 3
BINGO_35 = 16          # the 3-5 board is 4 by 4, so it has two corner-to-corner lines
D8_3_FREE = False

# ---------------------------------------------------------------- word-rhythm chart (big chart)
CHART = [  # four beats, a word (or shh) per beat; lines 1-4 for K-2, lines 5-8 add silent beats and 2-syllable words
    ["heart", "beat", "heart", "beat"], ["drum", "drum", "drum", "gong"], ["jazz", "swing", "jazz", "shh"],
    ["love", "kind", "share", "cheer"],
    ["trum-pet", "rag-time", "drum", "shh"], ["lan-tern", "cym-bal", "gong", "shh"], ["heart-beat", "shh", "jazz", "swing"],
    ["shad-ow", "moon", "glow", "shh"],
]
WORDS.update({"shh": "shh"})
EXPECT.update({"shh": 0})
CHART_K2 = 4

# ---------------------------------------------------------------- quick games (shared game bank)
GAMES = [
    ("Heartbeat Echo", "Say a short phrase, like “heart, beat, heart, beat.” The class repeats it exactly, then once softly.", "1"),
    ("Name Clap", "Say a name or word from the month, like “El-ling-ton.” The class claps its syllables out loud, then holds up that many fingers.", "2"),
    ("Freeze Beat", "Tap a pencil on a desk. Students move while you tap and freeze when you stop.", "4"),
    ("Quiet Countdown", "Count down from 10 to 0 in a whisper. Students sit tall and silent at 0.", "any"),
    ("Pass the Pencil", "Pass a pencil around a circle while you tap a steady beat. When you stop, that student says a February word.", "8"),
    ("Clue Time", "Read a clue from the Day 8 quiz. Students call out the answer together.", "8"),
    ("Kind Word Round", "Each student says one kind word, like “friend,” while the class pats a steady beat.", "any"),
    ("Mirror Moves", "Pairs face each other. One moves slowly, the other copies like a mirror; then swap.", "4"),
]

# ---------------------------------------------------------------- plan and page index
PLAN = ["cover", "teacher", "welcome", "quick", "glance", "games", "chart", "facts", "sign",
        "d1_plan", "d1_k2", "d1_35", "d2_plan", "d2_k2", "d2_35", "d3_plan", "d3_k2", "d3_35",
        "d4_plan", "d4_k2", "d4_35", "d4_cards", "d5_plan", "d5_k2", "d5_35", "d6_plan", "d6_k2", "d6_35",
        "d7_plan", "d7_k2", "d7_35", "d7_cards", "d7_book", "d8_plan", "d8_k2", "d8_35", "d8_quiz",
        "early1", "early2", "exit", "key_a", "key_b", "key_c", "report", "labels", "cert", "terms", "thanks"]
IX = {k: i + 1 for i, k in enumerate(PLAN)}
TOTAL = len(PLAN)


def pg(k):
    return f"page&nbsp;{IX[k]}"


def fill_pages(s):
    return re.sub(r"PG:(\w+)", lambda m: pg(m.group(1)), s)


SAY = lambda s: f"<span class=say>“{s}”</span>"

DAYS = [
    {"n": 1, "title": "Musician Spotlight Reader", "skill": "Reading about February musicians", "sk": "reading",
     "goal": "Students hear or read short facts about Black History Month and five musicians, and answer questions about them.",
     "materials": "Pencils, crayons and the worksheets. Nothing else.",
     "steps": [
         ("5", "Welcome and echo", f"Say: {SAY('Good morning, musicians! I am your guest teacher today. Echo me!')} Say each line and let the class repeat it: "
                                   "<i>Ears are on. Eyes are up. Hands are still. Let’s start!</i> Then say it once in a whisper."),
         ("5", "Opening question", f"Say: {SAY('February is the second month of the year. Every February, people in the United States celebrate Black History Month and learn about people who shaped our country.')} "
                                   "Ask: <b>Which musicians do you already know?</b> Take five answers. Any answer is fine."),
         ("10", "Read aloud", "<b>K–2:</b> read the short reading on PG:d1_k2 aloud, slowly, once. Read it a second time and let students point to the words. "
                              "<b>3–5:</b> students read PG:d1_35 silently, then you ask: <b>What was one new fact?</b>"),
         ("15", "Questions and drawing", "Hand out the worksheet: <b>K–2</b> PG:d1_k2, <b>3–5</b> PG:d1_35. Read the directions aloud. "
                                         "Walk around and help students find answers in the reading. Answers are on PG:key_a."),
         ("5", "Share a picture", "Ask 3 or 4 volunteers to hold up their drawing and say one sentence about it. Clap for each artist."),
     ],
     "extra": "Try Quiet Countdown or Heartbeat Echo from the quick games (PG:games).", "short": "Skip step 2; keep the reading and the questions."},
    {"n": 2, "title": "Name Beats", "skill": "Speech rhythm: clap the syllables", "sk": "syllables",
     "goal": "Students clap the syllables of musicians’ names and February words and use them to build a four-beat chant.",
     "materials": "Pencils, crayons, the worksheets and the word-rhythm chart (PG:chart). No music reading needed: every word shows its claps.",
     "steps": [
         ("5", "Steady pat", f"Pat your legs slowly and evenly, like a heartbeat. Say: {SAY('Copy me!')} Students pat with you. Say: {SAY('This steady pulse is called the beat.')}"),
         ("10", "Clap the words", "Say a word, then say it again while clapping once for each syllable: <b>Price</b> (1 clap), <b>Jop-lin</b> (2 claps), "
                                  "<b>El-ling-ton</b> (3 claps). Students echo. Try five or six words from PG:chart."),
         ("5", "Chart echoes", "Show PG:chart. Read a line out loud, one box per beat, while clapping the dots. <b>One dot</b> = ta, <b>two dots in one box</b> = ti-ti, "
                               "<b>shh</b> = a silent beat (open hands). Students echo. K–2 use lines 1–4; 3–5 use all 8."),
         ("15", "Worksheet", "<b>K–2</b> PG:d2_k2, <b>3–5</b> PG:d2_35. Read Part A aloud and clap each word with the class before they color or write. "
                             "Answers are on PG:key_a."),
         ("5", "Chant parade", "Volunteers read their chant aloud while the class pats a steady beat. Everyone claps at the end."),
     ],
     "extra": "Name Clap from the quick games (PG:games), with the names of students.", "short": "Do only Part A and Part B."},
    {"n": 3, "title": "Heart Drum Design Lab", "skill": "Design a heart drum", "sk": "design",
     "goal": "Students design a decorated drum, label its parts, and connect it to a steady beat.",
     "materials": "Pencils, crayons and the worksheets. Nothing else.",
     "steps": [
         ("5", "What is a drum?", f"Say: {SAY('A drum makes sound when something taps it. Drums are used in many kinds of music, and a big drum helps keep the beat in the Lunar New Year lion dance.')} "
                                  "Ask: <b>What patterns or colors could decorate a drum?</b> Take three answers."),
         ("5", "Find your heartbeat", "Say: <b>Put a hand on your chest and find your heartbeat.</b> Then say: "
                                      f"{SAY('Your heart keeps a steady beat all day. Pat the same beat on your leg.')} Pat slowly together for ten seconds."),
         ("20", "Design the drum", "Hand out the worksheet: <b>K–2</b> PG:d3_k2, <b>3–5</b> PG:d3_35. Say: "
                                   f"{SAY('Design a heart drum. Make it bright and clear, and give your drum a name.')} Read the directions aloud."),
         ("5", "Gallery walk", "Students stand beside their desks with their drums. Walk the room and ask three students: <b>What is your drum called?</b>"),
         ("5", "Put it away", "Collect the sheets for the teacher. Ask: <b>Whose drum would you like to tap?</b>"),
     ],
     "extra": "Kind Word Round or Quiet Countdown from the quick games (PG:games).", "short": "Skip the gallery walk."},
    {"n": 4, "title": "Heartbeat Freeze", "skill": "Move to a tapped beat and freeze", "sk": "movement",
     "goal": "Students move to a steady tap, change speed with the tap, and freeze when it stops.",
     "materials": "Pencils, the worksheets, a clear space to move, and the picture cards on PG:d4_cards (point at them or cut them out).",
     "steps": [
         ("5", "Rules of the freeze", f"Say: {SAY('When I tap, you move. When I stop, you freeze like a statue. Keep your hands to yourself.')} "
                                      "Practice once: tap a pencil on a desk for five seconds, stop, and wait for stillness."),
         ("10", "Heartbeat walk", f"Say: {SAY('Your heartbeat is a steady beat. It is faster when you run and slower when you rest.')} Show the heart card on PG:d4_cards. Tap <b>slowly</b>: students walk slowly. "
                                  "Tap <b>fast</b>: they jog in place. Stop: freeze. Repeat with three different speeds."),
         ("10", "Picture cards", "Hold up (or point at) one card at a time. Students move as the card says while you tap. Use at least six cards. "
                                 "The words under each card tell you what to say."),
         ("10", "Reflection sheet", "Hand out the worksheet: <b>K–2</b> PG:d4_k2, <b>3–5</b> PG:d4_35. Students sit and fill it in. Read the directions aloud."),
         ("5", "Statue gallery", "Tap a few beats, stop, and let the class freeze in a favorite pose. Walk around and name two poses you notice."),
     ],
     "extra": "Mirror Moves from the quick games (PG:games).", "short": "Use only four cards."},
    {"n": 5, "title": "Lantern Word Puzzles", "skill": "February vocabulary puzzles", "sk": "words",
     "goal": "Students find, match and decode February words about musicians, instruments and holidays.",
     "materials": "Pencils and the worksheets. Colored pencils or crayons are optional.",
     "steps": [
         ("5", "Show me", "Say a word and let students show it with their bodies: <b>heart</b> (hands on chest), <b>drum</b> (tap your legs), "
                          "<b>lantern</b> (hands make a round glow), <b>trumpet</b> (hold a pretend trumpet), <b>piano</b> (wiggle fingers in the air)."),
         ("5", "Syllable clap", "Say five words from PG:chart and clap their syllables together. Ask how many claps each word has."),
         ("20", "Word puzzles", "<b>K–2</b> PG:d5_k2 (match and trace). <b>3–5</b> PG:d5_35 (word search, then the decode puzzle). Read the directions "
                                "aloud. Answers are on PG:key_b."),
         ("5", "Show what you found", "Ask volunteers to read one word they found. The class claps its syllables."),
         ("5", "Quiet game", "Do Quiet Countdown from the quick games (PG:games) to end calmly."),
     ],
     "extra": "Early finishers: PG:early1.", "short": "Skip step 2; do the first puzzle only."},
    {"n": 6, "title": "Music Job Spotlight", "skill": "Music jobs", "sk": "jobs",
     "goal": "Students learn five jobs in music, what each person does, and write or draw about one of them.",
     "materials": "Pencils, crayons and the worksheets.",
     "steps": [
         ("5", "Who makes music happen?", f"Ask: {SAY('Who do you see at a concert?')} Take answers. Then ask: {SAY('Who do you not see?')}"),
         ("10", "Read about the jobs", "<b>K–2:</b> read the reading on PG:d6_k2 aloud. <b>3–5:</b> students read PG:d6_35 silently. "
                                       "Then ask: <b>Which job sounds most interesting? Why?</b>"),
         ("20", "Worksheet", "<b>K–2</b> PG:d6_k2 (draw a music job). <b>3–5</b> PG:d6_35 (match the jobs, then write a job ad or interview questions). "
                             "Answers are on PG:key_b."),
         ("5", "Act it out", "Students act out one job in silence while the class guesses it: composer (write in the air), conductor (arms in the air), "
                             "piano tuner (turn a pretend tuning key), radio host (talk into a pretend microphone), music teacher (point to the board)."),
     ],
     "extra": "Name Clap: clap the syllables of each job name (PG:games).", "short": "Skip the act-it-out step."},
    {"n": 7, "title": "Lantern Chant Book", "skill": "Compose a four-beat chant", "sk": "chant",
     "goal": "Students build four-beat chants from heart, drum and lantern words, say them with a steady beat, and keep them in a chant book.",
     "materials": "Pencils (crayons are optional for the picture), the worksheets, the word cards on PG:d7_cards and the chant book page (PG:d7_book).",
     "steps": [
         ("5", "Remember the chart", "Say a line from PG:chart with the class, one box per beat. Tap or clap the beat. Say it once softly and once with a strong voice."),
         ("5", "Make a class chant", "Pick four words from the word cards on PG:d7_cards. Write them on the board (or read them aloud). Say the chant together twice."),
         ("20", "Write chants", "<b>K–2</b> PG:d7_k2 (pick words). <b>3–5</b> PG:d7_35 (two chants with syllables). Walk around and ask: "
                               "<b>Does every beat have a word (or a shh)?</b> Answers are on PG:key_c."),
         ("5", "Partner share", "Partners trade sheets and say each other’s chants while one pats the beat."),
         ("5", "Chant book", "Hand out PG:d7_book. Students copy their favorite chant onto it and draw a picture to match."),
     ],
     "extra": "Heartbeat Echo with the best chants (PG:games).", "short": "Do one chant instead of two."},
    {"n": 8, "title": "February Bingo Showdown", "skill": "Review game day", "sk": "review",
     "goal": "Students review the month’s vocabulary with a bingo game, a read-aloud quiz and Pass the Pencil.",
     "materials": "Pencils, the worksheets, the read-aloud quiz on PG:d8_quiz, and scrap paper to cover squares (or students may draw a circle).",
     "steps": [
         ("5", "Make your board", "Hand out the bingo boards: <b>K–2</b> PG:d8_k2 (12 squares), <b>3–5</b> PG:d8_35 (16 squares). Students write the words from the word bank in any order in the squares. "
                                  "Read the bank aloud."),
         ("15", "Bingo", "Read one clue from PG:d8_quiz. Students find the answer on their board and cover or circle it. Use the first 12 clues with grades K–2; "
                          "use all 16 with grades 3–5. <b>K–2:</b> the first student to cover three squares across in one row says <b>Bingo!</b> "
                          "<b>3–5:</b> a full row, a full column, or a corner-to-corner line on the 4 by 4 board wins."),
         ("10", "Pass the Pencil", "Sit in a circle or line. Tap a beat on a desk while students pass a pencil. When you stop, the student holding it says a February word "
                                   "and claps its syllables."),
         ("5", "Reflection", "Students finish the reflection on their sheet. Ask: <b>What was your favorite day this week?</b>"),
     ],
     "extra": "Clue Time from the quick games (PG:games).", "short": "Do one bingo round only."},
]
for d in DAYS:
    d["steps"] = [(m, h, t) for m, h, t in d["steps"]]

# crayon lists come from the day data, so the Quick start page and the plans cannot disagree
CRAYON_DAYS = [d["n"] for d in DAYS if "crayons" in d["materials"] and "optional" not in d["materials"]]
CRAYON_OPT = [d["n"] for d in DAYS if "crayons" in d["materials"] and "optional" in d["materials"]]


def days_txt(ns):
    ns = [str(n) for n in ns]
    return "Days " + ", ".join(ns[:-1]) + " and " + ns[-1] if len(ns) > 1 else "Day " + ns[0]


DAY_SHEETS = {1: ("Musician Spotlight", "Read, Answer and Draw"), 2: ("Clap the Name Beats", "Name Beat Chants"),
              3: ("My Heart Drum", "Heart Drum Design Lab"), 4: ("Heartbeat Freeze", "Freeze Reflection"),
              5: ("Match and Trace", "Word Search and Decode"), 6: ("Music Job Spotlight", "Jobs and What They Do"),
              7: ("Pick a Chant", "Write Two Chants"), 8: ("February Bingo (K–2)", "February Bingo")}

PARTS = [  # (label, first key, last key, use)
    ("Cover and teacher notes", "cover", "teacher", "month note, setup steps, page guide"),
    ("For the substitute", "welcome", "sign", "welcome sheet, quick start, glance, games, chart, facts, class sign"),
    ("Day 1 · Musician Spotlight Reader", "d1_plan", "d1_35", "plan + K–2 and 3–5 sheets"),
    ("Day 2 · Name Beats", "d2_plan", "d2_35", "plan + K–2 and 3–5 sheets"),
    ("Day 3 · Heart Drum Design Lab", "d3_plan", "d3_35", "plan + K–2 and 3–5 sheets"),
    ("Day 4 · Heartbeat Freeze", "d4_plan", "d4_cards", "plan, 2 sheets, picture cards"),
    ("Day 5 · Lantern Word Puzzles", "d5_plan", "d5_35", "plan + K–2 and 3–5 sheets"),
    ("Day 6 · Music Job Spotlight", "d6_plan", "d6_35", "plan + K–2 and 3–5 sheets"),
    ("Day 7 · Lantern Chant Book", "d7_plan", "d7_book", "plan, 2 sheets, word cards, chant book"),
    ("Day 8 · February Bingo Showdown", "d8_plan", "d8_quiz", "plan, 2 boards, read-aloud quiz"),
    ("Extras", "early1", "exit", "early finishers, exit tickets"),
    ("Answer keys", "key_a", "key_c", "Days 1, 2, 5, 6, 7 and 8"),
    ("Sub tools and credits", "report", "thanks", "report, labels, awards, terms, thank you"),
]


def prange(a, b):
    return str(IX[a]) if a == b else f"{IX[a]}–{IX[b]}"


# ---------------------------------------------------------------- html scaffolding (from 007)
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
.tag { text-align: right; }
.tag .lv { display: inline-block; background: #000; color: #fff; font-family: 'Oswald'; font-weight: 700; font-size: 15pt; padding: 3pt 9pt 4pt; border-radius: 4pt; letter-spacing: .04em; }
.tag .lv.ak { background: ACCENT; }
.tag .ln { font-family: 'Oswald'; font-weight: 300; font-size: 11pt; margin-top: 3pt; }
.name { display: flex; gap: 18pt; font-size: 12pt; margin: 9pt 0 5pt; }
.name span { flex: 1; border-bottom: 1pt solid #000; height: 15pt; }
.name span.d { flex: 0 0 1.6in; }
.how { font-size: 11.5pt; margin: 7pt 0 6pt; }
.main { flex: 1; display: flex; flex-direction: column; min-height: 0; padding-bottom: 12px; }
.foot { display: flex; justify-content: space-between; font-size: 8.5pt; color: #333; border-top: .8pt solid #000; padding-top: 3pt; }
.wm { position: absolute; left: 50%; top: 50%; transform: translate(-50%, -50%) rotate(-38deg); font-family: 'Oswald'; font-weight: 700;
      font-size: 150pt; color: rgba(0,0,0,.13); letter-spacing: .06em; white-space: nowrap; pointer-events: none; z-index: 9; }
.doc h1 { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 30pt; margin: 0 0 4pt; line-height: 1; }
.doc h2 { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 13.5pt; margin: 10pt 0 4pt; letter-spacing: .02em; }
.doc p, .doc li { font-size: 10.6pt; line-height: 1.32; margin: 0 0 4pt; }
.doc ul, .doc ol { margin: 0 0 4pt; padding-left: 15pt; }
.tn p, .tn li { font-size: 9.2pt !important; line-height: 1.22 !important; margin-bottom: 2pt !important; }
.tn h2 { margin: 6pt 0 2pt !important; font-size: 12pt !important; }
.tn table.t { font-size: 9pt; }
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
.part small { font-family: 'Source Sans 3'; font-weight: 400; text-transform: none; font-size: 11pt; letter-spacing: 0; margin-left: 6pt; }
.fl { display: flex; align-items: flex-end; gap: 6pt; font-size: 10.5pt; margin: 0 0 7pt; }
.fl b { font-weight: 600; white-space: nowrap; }
.fl span { flex: 1; border-bottom: 1pt solid #000; height: 14pt; }
.ln2 { border-bottom: 1pt solid #000; height: 22pt; }
.ans { font-family: 'Oswald'; font-weight: 700; color: ACCENT; }
.circ { display: inline-block; font-family: 'Oswald'; font-weight: 500; letter-spacing: .05em; padding: 0 7pt; border: 1.3pt solid transparent; border-radius: 10pt; }
.circ.on { border-color: ACCENT; color: ACCENT; font-weight: 700; }
.steps { list-style: none; padding: 0; margin: 4pt 0 0; }
.steps li { display: flex; gap: 10pt; margin: 0 0 17pt; font-size: 13pt; line-height: 1.38; }
.steps .tm { flex: 0 0 46pt; text-align: center; }
.steps .tm b { display: block; background: #000; color: #fff; font-family: 'Oswald'; font-weight: 700; font-size: 11pt; border-radius: 4pt; padding: 2pt 0 3pt; }
.steps .tm span { display: block; font-family: 'Oswald'; font-weight: 300; font-size: 9.5pt; margin-top: 2pt; }
.steps .tx b.hd { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 13pt; letter-spacing: .02em; }
.say { font-style: italic; }
.meta { display: flex; gap: 10pt; margin: 8pt 0 2pt; }
.meta > div { flex: 1; border: 1.3pt solid #000; border-radius: 7pt; padding: 6pt 9pt; font-size: 11pt; line-height: 1.3; }
.meta b.k { display: block; font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 10pt; letter-spacing: .05em; color: ACCENT; }
.cover { align-items: center; justify-content: space-between; padding: 0.55in 0.6in 0.5in; }
.store { font-family: 'Oswald'; font-weight: 500; font-size: 13pt; letter-spacing: .32em; text-transform: uppercase; }
.ctitle { text-align: center; }
.ctitle .a { font-family: 'Oswald'; font-weight: 700; font-size: 84pt; line-height: 1; letter-spacing: .02em; color: ACCENT; }
.ctitle .b { white-space: nowrap; font-family: 'Oswald'; font-weight: 700; font-size: 44pt; line-height: .95; letter-spacing: .01em; }
.ctitle .c { font-family: 'Oswald'; font-weight: 300; font-size: 16pt; margin-top: 8pt; }
.cband { width: 100%; background: #000; color: #fff; text-align: center; font-family: 'Oswald'; font-weight: 500; font-size: 14pt;
         letter-spacing: .08em; text-transform: uppercase; padding: 8pt 0 9pt; border-radius: 4pt; }
.cband em { font-style: normal; color: ACCENT_LIGHT; }
.bx { border: 1.4pt solid #000; border-radius: 7pt; text-align: center; overflow: hidden; background: #fff; }
.bx .w { font-family: 'Oswald'; font-weight: 700; font-size: 17pt; line-height: 1; padding-top: 8pt; min-height: 31pt; }
.bx .d { height: 20pt; display: flex; align-items: center; justify-content: center; gap: 5pt; }
.bx .s { font-family: 'Oswald'; font-weight: 500; font-size: 10.5pt; color: ACCENT; border-top: 1pt dashed #999; padding: 2pt 0 3pt; letter-spacing: .04em; min-height: 17pt; }
.dot { display: inline-block; width: 9pt; height: 9pt; border-radius: 50%; background: ACCENT; }
.dot.sm { width: 6.5pt; height: 6.5pt; }
.dot.o { background: #fff; border: 1.3pt solid #000; width: 15pt; height: 15pt; }
.dot.f { background: ACCENT; border: 1.3pt solid #000; width: 15pt; height: 15pt; }
.main > * { flex-shrink: 0; }
.main > .box[style*='flex:1'], .main > div[style*='flex:1'] { flex-shrink: 1; }
.bx.c .w { padding-top: 4pt; min-height: 22pt; }
.bx.c .d { height: 13pt; }
.bx.c .s { font-size: 9pt; min-height: 12pt; padding: 1pt 0 2pt; }
.roomy td, .roomy th { padding: 6pt 6pt; }
.grid4 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8pt; }
.cut { border: 1.2pt dashed #777; border-radius: 8pt; }
""".replace("ACCENT_LIGHT", ACCENT_LIGHT).replace("ACCENT", ACCENT)


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


def fl(label, extra=""):
    return f'<div class="fl" {extra}><b>{label}</b><span></span></div>'


def circ(word, on=False):
    return f'<span class="circ{" on" if on else ""}">{word}</span>'


def checkbox(size=11, ticked=False):
    tick = (f'<path d="M{size * .2:.1f} {size * .52:.1f} L{size * .42:.1f} {size * .75:.1f} L{size * .82:.1f} {size * .25:.1f}" '
            f'fill="none" stroke="{ACCENT}" stroke-width="{size * .14:.1f}" stroke-linecap="round" stroke-linejoin="round"/>' if ticked else "")
    return (f'<svg width="{size}pt" height="{size}pt" viewBox="0 0 {size} {size}" style="display:inline-block;vertical-align:-2pt">'
            f'<rect x=".7" y=".7" width="{size - 1.4}" height="{size - 1.4}" rx="2" fill="#fff" stroke="#000" stroke-width="1.2"/>{tick}</svg>')


def lines(n, h=22):
    return "".join(f'<div class="ln2" style="height:{h}pt"></div>' for _ in range(n))


# ---------------------------------------------------------------- drawings (all drawn in code)
def pic(name, size=70, accent=ACCENT_LIGHT):
    """Simple line-art picture in a 100x100 box; every stroke sits at least 3 units inside the box."""
    S = 'stroke="#000" stroke-width="3" stroke-linejoin="round" stroke-linecap="round"'
    o = []
    if name == "snowflake":
        import math
        for a in range(0, 180, 60):
            r = math.radians(a - 90)
            o.append(f'<line x1="{50 + 40 * math.cos(r):.1f}" y1="{50 + 40 * math.sin(r):.1f}" x2="{50 - 40 * math.cos(r):.1f}" y2="{50 - 40 * math.sin(r):.1f}" {S}/>')
        for a in range(0, 360, 60):
            r = math.radians(a - 90)
            bx, by = 50 + 25 * math.cos(r), 50 + 25 * math.sin(r)
            for d in (-45, 45):
                q = math.radians(a - 90 + d)
                o.append(f'<line x1="{bx:.1f}" y1="{by:.1f}" x2="{bx + 11 * math.cos(q):.1f}" y2="{by + 11 * math.sin(q):.1f}" {S}/>')
        o.append(f'<circle cx="50" cy="50" r="6" fill="{accent}" {S}/>')
    elif name == "star":
        import math
        pts = []
        for i in range(10):
            r = 42 if i % 2 == 0 else 18
            a = math.radians(-90 + i * 36)
            pts.append(f"{50 + r * math.cos(a):.1f},{54 + r * math.sin(a):.1f}")
        o.append(f'<polygon points="{" ".join(pts)}" fill="{accent}" {S}/>')
    elif name == "heart":
        o.append(f'<path d="M50 86 C 14 60, 10 26, 30 20 C 42 17, 50 26, 50 33 C 50 26, 58 17, 70 20 C 90 26, 86 60, 50 86 Z" fill="{accent}" {S}/>')
    elif name == "lantern":
        o.append(f'<path d="M38 24 Q50 5 62 24" fill="none" {S}/>')
        o.append(f'<polygon points="32,34 68,34 60,24 40,24" fill="#fff" {S}/>')
        o.append(f'<rect x="34" y="34" width="32" height="44" fill="#fff" {S}/>')
        o.append(f'<rect x="41" y="42" width="18" height="28" fill="{accent}" {S}/>')
        o.append(f'<rect x="30" y="78" width="40" height="9" rx="2" fill="#fff" {S}/>')
    elif name == "drum":
        o.append(f'<path d="M18 42 L18 74 A32 10 0 0 0 82 74 L82 42" fill="#fff" {S}/>')
        o.append(f'<ellipse cx="50" cy="42" rx="32" ry="10" fill="{accent}" {S}/>')
        o.append(f'<line x1="28" y1="10" x2="46" y2="34" {S}/><line x1="72" y1="10" x2="54" y2="34" {S}/>')
    elif name == "trumpet":
        o.append(f'<path d="M58 41 C70 41 80 34 90 22 L90 74 C80 62 70 55 58 55 Z" fill="{accent}" {S}/>')
        o.append(f'<path d="M26 55 L26 69 Q26 76 33 76 L58 76 Q65 76 65 69 L65 55" fill="none" {S}/>')
        o.append(f'<rect x="8" y="44" width="9" height="8" rx="2" fill="#fff" {S}/>')
        o.append(f'<path d="M17 41 L58 41 M17 55 L58 55 M17 41 L17 55" fill="none" {S}/>')
        for xx in (32, 41, 50):
            o.append(f'<rect x="{xx - 3}" y="30" width="6" height="11" fill="#fff" {S}/><line x1="{xx}" y1="30" x2="{xx}" y2="24" {S}/><rect x="{xx - 4}" y="19" width="8" height="5" rx="1.5" fill="#000"/>')
    elif name == "piano":
        o.append(f'<rect x="10" y="30" width="80" height="44" rx="4" fill="#fff" {S}/>')
        o.append(f'<rect x="10" y="18" width="80" height="12" rx="3" fill="{accent}" {S}/>')
        for i in range(1, 7):
            o.append(f'<line x1="{10 + 80 / 7 * i:.1f}" y1="30" x2="{10 + 80 / 7 * i:.1f}" y2="74" {S}/>')
        for i in (1, 2, 4, 5, 6):
            o.append(f'<rect x="{10 + 80 / 7 * i - 3.5:.1f}" y="30" width="7" height="26" fill="#000"/>')
    elif name == "gong":
        o.append(f'<path d="M14 88 L14 14 L86 14 L86 88" fill="none" {S}/>')
        o.append(f'<line x1="50" y1="14" x2="50" y2="28" {S}/>')
        o.append(f'<circle cx="50" cy="54" r="26" fill="{accent}" {S}/>')
        o.append(f'<circle cx="50" cy="54" r="10" fill="#fff" {S}/>')
    elif name == "cymbal":
        o.append(f'<ellipse cx="50" cy="32" rx="36" ry="9" transform="rotate(-12 50 32)" fill="{accent}" {S}/>')
        o.append(f'<ellipse cx="50" cy="66" rx="36" ry="9" transform="rotate(12 50 66)" fill="#fff" {S}/>')
        o.append(f'<circle cx="50" cy="32" r="4" fill="#fff" {S}/><circle cx="50" cy="66" r="4" fill="{accent}" {S}/>')
    elif name == "card":
        o.append(f'<rect x="14" y="22" width="72" height="56" rx="4" fill="#fff" {S}/>')
        o.append(f'<path d="M14 24 L50 52 L86 24" fill="none" {S}/>')
        o.append(f'<path d="M50 74 C 42 68, 40 62, 45 60 C 48 59, 50 61, 50 63 C 50 61, 52 59, 55 60 C 60 62, 58 68, 50 74 Z" fill="{accent}" {S}/>')
    else:
        raise ValueError(name)
    return svg(size, size, f'<g>{"".join(o)}</g>').replace(f'width="{size}pt" height="{size}pt" viewBox="0 0 {size} {size}"',
                                                            f'width="{size}pt" height="{size}pt" viewBox="0 0 100 100"')


def sun_art(size=60):
    import math
    o = [f'<circle cx="50" cy="50" r="18" fill="{ACCENT_LIGHT}" stroke="#000" stroke-width="3"/>']
    for a in range(0, 360, 45):
        r = math.radians(a)
        o.append(f'<line x1="{50 + 28 * math.cos(r):.1f}" y1="{50 + 28 * math.sin(r):.1f}" x2="{50 + 40 * math.cos(r):.1f}" y2="{50 + 40 * math.sin(r):.1f}" '
                 f'stroke="#000" stroke-width="3" stroke-linecap="round"/>')
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}pt" height="{size}pt" viewBox="0 0 100 100" style="display:block">{"".join(o)}</svg>'


def dots_html(word):
    k = beat_kind(word)
    if k == "q":
        return '<span class="dot"></span>'
    if k == "e":
        return '<span class="dot sm"></span><span class="dot sm"></span>'
    return '<span style="font-family:Oswald;font-size:10pt;color:#555">open hands</span>'


def beat_row(words, show=True, size=17, key_syl=True, hgt=None, compact=False):
    """Four beat boxes. Each box holds one word (or shh), its claps as dots, and its rhythm syllable."""
    cells = []
    for i in range(4):
        w = words[i] if words else None
        if w is not None and show:
            lab = SYL[beat_kind(w)] if key_syl else ""
            cells.append(f'<div class="bx{" c" if compact else ""}"><div class="w" style="font-size:{size}pt">{escape(wd(w))}</div>'
                         f'<div class="d">{dots_html(w)}</div><div class="s">{lab}</div></div>')
        else:
            cells.append(f'<div class="bx"><div class="w" style="font-size:{size}pt;min-height:{hgt or 31}pt"></div>'
                         f'<div class="d"></div><div class="s" style="color:#999">beat {i + 1}</div></div>')
    return f'<div class="grid4">{"".join(cells)}</div>'


def letter_box(val, show, w=34, h=28, size=18):
    return (f'<span style="display:inline-block;width:{w}pt;height:{h}pt;border:1.3pt solid #000;border-radius:5pt;text-align:center;'
            f'line-height:{h}pt;vertical-align:middle;font-family:Oswald;font-weight:700;font-size:{size}pt;color:{ACCENT}">{val if show else ""}</span>')


def dotted(word, size, w):
    return (f'<text x="4" y="{size * 0.92:.1f}" font-family="Oswald" font-weight="700" font-size="{size}" fill="none" stroke="#777" '
            f'stroke-width="1.2" stroke-dasharray="3 2.5" letter-spacing="2">{escape(word)}</text>')


# ---------------------------------------------------------------- substitute pages
def welcome_page(n, watermark=False):
    rows = "".join("<tr><td style='height:25pt'></td><td></td><td></td><td></td></tr>" for _ in range(7))
    inner = (f'<div class="how">Teacher: fill this in once and keep it on top of the sub folder. Substitute: welcome, and thank you! '
             f'Everything you need for today is in this folder.</div>'
             f'<div class="cols" style="gap:16pt"><div>{fl("Teacher")}{fl("Room")}{fl("School office ext.")}</div>'
             f'<div>{fl("Nearby teacher who can help")}{fl("Their room")}{fl("Date updated")}</div></div>'
             f'<div class="part">Today’s classes<span class="acc"> ·</span><small>Use a day number you have not used yet with that class.</small></div>'
             f'<table class="t"><tr><th style="width:18%">Time</th><th style="width:30%">Class / grade</th><th style="width:14%">Day #</th><th>Notes</th></tr>{rows}</table>'
             f'<div class="cols" style="gap:16pt;margin-top:6pt"><div>'
             f'<div class="part">How we do things<span class="acc"> ·</span></div>'
             f'{fl("Attention signal")}{fl("Entering the room")}{fl("Where students sit")}{fl("Bathroom / water")}{fl("Lining up / dismissal")}'
             f'</div><div>'
             f'<div class="part">Where things are<span class="acc"> ·</span></div>'
             f'{fl("Copies of worksheets")}{fl("Pencils and crayons")}{fl("Seating charts")}{fl("Emergency plans")}{fl("Class lists")}'
             f'</div></div>'
             f'<div class="part">Helpful students<span class="acc"> ·</span><small>Keep private student information in the office file, not here.</small></div>'
             f'<div class="cols" style="gap:16pt"><div>{fl("")}{fl("")}</div><div>{fl("")}{fl("")}</div></div>'
             f'<div class="box" style="margin-top:4pt;font-size:10.5pt"><b>No music background needed.</b> Each day has a step-by-step plan with words to say. '
             f'Please leave notes on the sub report ({pg("report")}).</div>')
    return page("Welcome, substitute · fill in and keep on top", "FOR THE SUB", "Welcome sheet", inner, n, watermark)


def quick_page(n, watermark=False):
    items = [("1", "Pick the day", f"Look at the welcome sheet ({pg('welcome')}) for the day number for this class. Turn to that day’s plan page "
                                   f"(they are listed on {pg('glance')}). Each class gets a day it has not had yet."),
             ("2", "Set up the room", f"Write the day’s title on the board. Hold up the class sign ({pg('sign')}) if you like. "
                                      f"Have pencils ready, and crayons for {days_txt(CRAYON_DAYS)} (optional on {days_txt(CRAYON_OPT)}). Count out one worksheet per student: K–2 or 3–5 as the plan says."),
             ("3", "Say the first words", "Stand where everyone can see you. Use the attention signal from the welcome sheet. Then say the first line of step 1 "
                                         "exactly as printed. Every step has words you can read aloud.")]
    rows = "".join(f'<div class="box" style="display:flex;gap:14pt;align-items:center;margin:0 0 18pt;padding:16pt 14pt">'
                   f'<div class="h" style="font-size:44pt;color:{ACCENT};flex:0 0 40pt;text-align:center">{a}</div>'
                   f'<div><div class="h" style="font-size:17pt;margin-bottom:5pt">{b}</div><div style="font-size:12.5pt;line-height:1.38">{c}</div></div></div>'
                   for a, b, c in items)
    inner = (f'<div class="how">Short on time? These three things get you started in the first 5 minutes. Everything else is in the plan.</div>{rows}'
             f'<div class="part">You do not need to<span class="acc"> ·</span></div>'
             f'<ul style="margin:0;padding-left:15pt;font-size:12pt;line-height:1.5"><li>use any technology or electronics</li>'
             f'<li>know anything about music: you will clap, pat and say words</li>'
             f'<li>bring anything: pencils and crayons are all the days need</li></ul>'
             f'<div class="box" style="margin-top:auto;font-size:11pt"><b>If something goes wrong:</b> skip to the worksheet. Every day still works with only the worksheet and the '
             f'words in step 1. Use “Short class?” at the bottom of each plan.</div>')
    return page("The first 5 minutes", "FOR THE SUB", "Quick start", inner, n, watermark)


def glance_page(n, watermark=False):
    rows = ""
    for d in DAYS:
        k = d["n"]
        rows += (f"<tr><td class='ans' style='font-size:13pt;text-align:center'>{k}</td><td><b>{escape(d['title'])}</b><br>"
                 f"<span class='small'>{d['skill']}</span></td><td>{escape(DAY_SHEETS[k][0])}<br><span class='small'>{pg(f'd{k}_k2')}</span></td>"
                 f"<td>{escape(DAY_SHEETS[k][1])}<br><span class='small'>{pg(f'd{k}_35')}</span></td>"
                 f"<td style='text-align:center'>{IX[f'd{k}_plan']}</td></tr>")
    inner = (f'<div class="how">Each day is one 30–45 minute music class. Every day works for any grade K–5: use the plan page, then hand out '
             f'the <b>K–2</b> or <b>3–5</b> sheet. The days can be used in any order. The themes are Black History Month musicians, Valentine’s Day, Lunar New Year and Groundhog Day.</div>'
             f'<table class="t roomy" style="font-size:12pt"><tr><th style="width:8%">Day</th><th style="width:31%">Lesson</th><th>K–2 sheet</th><th>3–5 sheet</th>'
             f'<th style="width:11%">Plan page</th></tr>{rows}</table>'
             f'<div class="part" style="margin-top:12pt">Also in this folder<span class="acc"> ·</span></div>'
             f'<table class="t roomy" style="font-size:11.5pt"><tr><th style="width:30%">Page</th><th>What it is for</th></tr>'
             f'<tr><td>Quick games ({pg("games")})</td><td>8 no-prep games for extra time. No equipment, no tech.</td></tr>'
             f'<tr><td>Word-rhythm chart ({pg("chart")})</td><td>Big chart of four-beat chants. Words, claps and silent beats are printed. Used on Days 2, 5 and 7.</td></tr>'
             f'<tr><td>February facts ({pg("facts")})</td><td>The dates and facts used in this bundle, in plain words, for answering questions.</td></tr>'
             f'<tr><td>Early finishers ({pg("early1")}, {pg("early2")})</td><td>Drawing, writing and word games for fast workers.</td></tr>'
             f'<tr><td>Answer keys ({prange("key_a", "key_c")})</td><td>Days 1, 2, 5, 6, 7 and 8. Days 3 and 4 are open-ended.</td></tr></table>')
    return page("Days at a glance", "FOR THE SUB", "8 days, any order", inner, n, watermark)


def games_page(n, watermark=False):
    g = "".join(f"<tr><td><b>{a}</b></td><td>{t}</td><td style='text-align:center'>{dd}</td></tr>" for a, t, dd in GAMES)
    inner = (f'<div class="how">No-prep games for the last five minutes of a class (or any gap). They need only voices, hands and a pencil.</div>'
             f'<table class="t roomy" style="font-size:13pt"><tr><th style="width:24%">Game</th><th>How to do it</th><th style="width:9%">Day</th></tr>{g}</table>'
             f'<div class="part" style="margin-top:10pt">Tips for a calm class<span class="acc"> ·</span></div>'
             f'<ul style="margin:0;padding-left:15pt;font-size:13pt;line-height:1.7">'
             f'<li>Use the teacher’s attention signal from the welcome sheet ({pg("welcome")}), or clap two times and have the class clap back two.</li>'
             f'<li>“Strong voice, not shouting” keeps every game safe and happy.</li>'
             f'<li>If a game gets too loud, switch to a worksheet or to Quiet Countdown.</li>'
             f'<li>Let students take turns as the leader. Keep turns short.</li>'
             f'<li>Students may know other musicians or celebrate other traditions. Thank them and move on.</li></ul>'
             f'<div class="box" style="margin-top:12pt;font-size:12pt"><b>Not sure which game to pick?</b> Use <b>Quiet Countdown</b> to settle a class, '
             f'<b>Name Clap</b> to wake it up, and <b>Kind Word Round</b> to finish with something positive.</div>')
    return page("Quick games", "FOR THE SUB", "No prep, no tech", inner, n, watermark)


def chart_page(n, watermark=False):
    rows = []
    for i, line in enumerate(CHART):
        lab = (f'<div style="flex:0 0 34pt;text-align:center"><div class="h" style="font-size:22pt">{i + 1}</div>'
               f'<div class="l" style="font-size:9pt">{"K–5" if i < CHART_K2 else "3–5"}</div></div>')
        rows.append(f'<div style="display:flex;align-items:center;gap:8pt;border-bottom:1pt solid #bbb;padding:7pt 0">{lab}'
                    f'<div style="flex:1">{beat_row(line, size=15, compact=True)}</div></div>')
    inner = (f'<div class="how">Read each line aloud, one box per beat, and clap the dots. The class echoes. You do not need to read music.</div>'
             f'<div style="border-top:1pt solid #bbb">{"".join(rows)}</div>'
             f'<div class="small" style="margin-top:6pt;font-size:9.5pt !important"><b>One dot</b> = <b>ta</b> (one clap). <b>Two small dots</b> = <b>ti-ti</b> '
             f'(two quick claps in one beat). <b>shh</b> = a silent beat: open your hands, no sound. Four boxes make one four-beat chant.</div>')
    return page("Word-rhythm chart · show it or copy a line on the board", "FOR THE SUB", "Days 2, 5 and 7", inner, n, watermark)


FACTS_ROWS = [
    ("Black History Month", "Every February", "Observed in the United States each February. It grew from Negro History Week, which historian Carter G. Woodson started in February 1926. In 1976 President Gerald Ford asked Americans to honor it."),
    ("Scott Joplin", "About 1868–1917", "Composer and pianist, called the “King of Ragtime.” His Maple Leaf Rag was published in 1899. Sources differ on his exact birth date, so the pages say “about 1868.”"),
    ("Duke Ellington", "April 29, 1899 – May 24, 1974", "Born in Washington, D.C. Pianist, composer and bandleader who led his own orchestra from 1924 until his death, about fifty years."),
    ("Ella Fitzgerald", "April 25, 1917 – June 15, 1996", "Jazz singer famous for scat, using the voice like an instrument. Her nickname was “Lady Ella.”"),
    ("Louis Armstrong", "1901 – July 6, 1971", "Born in New Orleans, Louisiana. Jazz trumpeter and singer, nicknamed “Satchmo.” He often said he was born in 1900, but records point to 1901."),
    ("Florence Price", "1887 – June 3, 1953", "Born in Little Rock, Arkansas (a few sources say 1888). Composer, pianist and organist. In 1933 the Chicago Symphony Orchestra performed her Symphony No. 1. She is known as the first African American woman to have a symphony performed by a major U.S. orchestra."),
    ("Valentine’s Day", "February 14", "A day when many people share cards and kind words. In this bundle, the heart is a steady beat: it speeds up when you run and slows down when you rest."),
    ("Lunar New Year", "Between January 21 and February 20", "A celebration based on the Moon’s calendar, so its date changes every year. Many families in China, other Asian countries and communities around the world celebrate it. Lanterns are a common decoration, and the lion dance uses drums, cymbals and a gong."),
    ("Groundhog Day", "February 2", "A tradition in which people watch to see whether a groundhog sees its shadow. The best-known event is in Punxsutawney, Pennsylvania, where official celebrations date back to 1887."),
    ("Presidents’ Day", "Third Monday of February", "The federal holiday officially named Washington’s Birthday, often called Presidents’ Day. It always falls between February 15 and 21."),
]


def facts_page(n, watermark=False):
    rows = "".join(f"<tr><td><b>{a}</b></td><td>{b}</td><td style='font-size:10.5pt;line-height:1.28'>{d}</td></tr>"
                   for a, b, d in FACTS_ROWS)
    inner = (f'<div class="how">Plain facts for answering questions. Students may know more, and may celebrate other traditions. Thank them for sharing.</div>'
             f'<table class="t" style="font-size:10pt"><tr><th style="width:17%">Topic</th><th style="width:21%">When</th><th>A few facts</th></tr>{rows}</table>'
             f'<div class="box" style="margin-top:8pt;font-size:10.5pt"><b>If a student asks something you do not know:</b> say “That is a good question. '
             f'Let’s ask your classroom teacher.” You never need to explain more than what is on the page. The days share these facts and never ask students to take part in a religious practice.</div>'
             f'<ul style="margin:6pt 0 0;padding-left:15pt;font-size:10.5pt;line-height:1.4"><li>Stay with the facts on this page and in the readings. The days do not quote speeches or lyrics.</li>'
             f'<li>Treat every question kindly. If a student wants to say more, thank them and return to the plan.</li></ul>')
    return page("February facts at a glance", "FOR THE SUB", "Facts and dates", inner, n, watermark)


def sign_page(n, watermark=False):
    inner = (f'<div class="keepblank" style="flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center">'
             f'<div style="display:flex;gap:30pt;margin-bottom:16pt">{pic("heart", 80)}{pic("drum", 80)}{pic("lantern", 80)}</div>'
             f'<div class="h" style="font-size:54pt;line-height:1.05">Today we have a<br>guest teacher</div>'
             f'<div style="display:flex;align-items:flex-end;gap:10pt;font-size:20pt;margin-top:22pt;width:80%"><b>Name</b><span style="flex:1;border-bottom:2pt solid #000;height:28pt"></span></div>'
             f'<div class="h" style="font-size:20pt;margin-top:26pt;letter-spacing:.06em">Ears on · Eyes up · Hands still · Voices ready</div></div>')
    return page("Class sign · hold it up or tape it to the board", "FOR THE SUB", "Class sign", inner, n, watermark)


def plan_page(d, n, watermark=False):
    k = d["n"]
    steps = "".join(
        f'<li><div class="tm"><b>{m} min</b><span>Step {i + 1}</span></div><div class="tx"><b class="hd">{escape(h)}</b><br>{fill_pages(t)}</div></li>'
        for i, (m, h, t) in enumerate(d["steps"]))
    total = sum(int(m) for m, _, _ in d["steps"])
    inner = (f'<div class="meta"><div><b class="k">Goal</b>{d["goal"]}</div><div><b class="k">You need</b>{fill_pages(d["materials"])}</div>'
             f'<div style="flex:0 0 1.55in"><b class="k">Copies</b>K–2: {pg(f"d{k}_k2")}<br>3–5: {pg(f"d{k}_35")}<br>'
             f'<span class="small">about {total} min</span></div></div>'
             f'<div class="part" style="margin-top:10pt">Step by step<span class="acc"> ·</span><small>Italic lines are words you can say.</small></div>'
             f'<ol class="steps">{steps}</ol>'
             f'<div class="box" style="margin-top:auto;font-size:10.5pt"><b>Extra time?</b> {fill_pages(d["extra"])} '
             f'<b>Short class?</b> {d["short"]}</div>')
    return page(f"Day {k} · {escape(d['skill'])} · no tech, no prep", f"DAY {k}", "Sub plan", inner, n, watermark, title=d["title"])


# ---------------------------------------------------------------- worksheets
def sheet(k, band, sub, inner, n, watermark=False, key_page=None):
    title = DAY_SHEETS[k][0 if band == "k2" else 1]
    right = f"Answer key on page {IX[key_page]}" if key_page else None
    return page(sub, f"DAY {k}", "Grades K–2" if band == "k2" else "Grades 3–5", inner, n, watermark, name=True, right=right, title=title)


def keypage(sub, tagsub, inner, n, watermark, title=TITLE):
    return page(sub, "ANSWER KEY", tagsub, inner, n, watermark, ak=True, title=title)


def d1_k2(n, watermark=False):
    qs = ""
    for i, (q, opts, a) in enumerate(D1_K2_Q):
        qs += (f'<div style="display:flex;align-items:center;gap:8pt;font-size:13.5pt;margin:0 0 9pt"><b class="h" style="width:16pt">{i + 1}</b>'
               f'<span style="flex:1">{q}</span>{"".join(circ(o) for o in opts)}</div>')
    inner = (f'<div class="how" style="font-size:12.5pt">Your teacher reads the reading. Follow along with your finger. Then answer the questions.</div>'
             f'<div class="box" style="font-size:12.5pt;line-height:1.42;padding:8pt 12pt">{" ".join(D1_K2_TEXT)}</div>'
             f'<div class="part">Questions<small>Circle the answer.</small></div>{qs}'
             f'<div class="part" style="margin-top:4pt">Draw it<small>Draw one musician from the reading with an instrument.</small></div>'
             f'<div class="box" style="flex:1;min-height:110pt"></div>')
    return sheet(1, "k2", "A short reading about February", inner, n, watermark, key_page="key_a")


def d1_35(n, watermark=False):
    qs = "".join(f'<div style="font-size:11pt;margin:0 0 1pt"><b>{i + 1}.</b> {q}</div><div class="ln2" style="height:20pt"></div>' for i, (q, _) in enumerate(D1_35_Q))
    inner = (f'<div class="how">Read the passage. Underline one fact that was new to you. Then answer the questions in complete sentences.</div>'
             f'<div class="box" style="font-size:10.8pt;line-height:1.38;padding:7pt 11pt">{D1_35_TEXT}</div>'
             f'<div class="part">Questions<span class="acc"> ·</span></div>{qs}'
             f'<div class="part" style="margin-top:6pt">Draw it<small>Draw one musician from the reading. Add a caption that says what the person did.</small></div>'
             f'<div class="box" style="flex:1;min-height:90pt"></div>')
    return sheet(1, "35", "Read, answer and draw", inner, n, watermark, key_page="key_a")


def d2_k2(n, watermark=False, key=False):
    rows = []
    for i, w in enumerate(D2_K2_A):
        circles = "".join(f'<span class="dot {"f" if (key and j < nsyl(w)) else "o"}"></span>' for j in range(4))
        rows.append(f'<div style="display:flex;align-items:center;gap:12pt;border:1.3pt solid #000;border-radius:7pt;padding:5pt 14pt">'
                    f'<b class="h" style="font-size:16pt;width:14pt">{i + 1}</b><b style="font-size:23pt;width:150pt;font-family:Oswald">{escape(wd(w).replace("-", " · "))}</b>'
                    f'<span style="display:flex;gap:9pt">{circles}</span></div>')
    b = ""
    for i, w in enumerate(D2_K2_B):
        b += (f'<div style="display:flex;align-items:center;gap:10pt;font-size:20pt;margin:0 0 10pt"><b class="h" style="width:16pt;font-size:14pt">{i + 1}</b>'
              f'<b style="flex:1;font-family:Oswald">{escape(wd(w))}</b>{"".join(circ(str(c), key and nsyl(w) == c) for c in (1, 2, 3))}</div>')
    inner = (f'<div class="part">A · Clap and color<small>Clap the word. Color one circle for each clap.</small></div>'
             f'<div style="display:grid;gap:6pt">{"".join(rows)}</div>'
             f'<div class="part" style="margin-top:12pt">B · How many claps?<small>Clap the word. Circle the number.</small></div>{b}'
             f'<div class="part" style="margin-top:6pt">C · My own word<small>Write a February word. Clap it. Color the circles.</small></div>'
             f'<div style="display:flex;align-items:center;gap:12pt;border:1.3pt solid #000;border-radius:7pt;padding:9pt 14pt"><span style="flex:1;border-bottom:1pt solid #000;height:30pt"></span>'
             f'<span style="display:flex;gap:9pt">{"".join(chr(60) + "span class=" + chr(34) + "dot o" + chr(34) + ">" + chr(60) + "/span>" for _ in range(4))}</span></div>')
    if key:
        return keypage("Day 2 · K–2 answer key", "Clap the Syllables", inner, n, watermark, "Clap the Syllables")
    return sheet(2, "k2", "Clap the syllables of February words", inner, n, watermark, key_page="key_a")


D2_35_SORT = {1: [], 2: [], 3: []}
for _w in D2_35_B:
    D2_35_SORT[nsyl(_w)].append(_w)


def d2_35(n, watermark=False, key=False):
    cells = []
    for i, w in enumerate(D2_35_A):
        cells.append(f'<div style="display:flex;align-items:center;gap:8pt;border:1.3pt solid #000;border-radius:7pt;padding:3pt 10pt">'
                     f'<b class="h" style="font-size:13pt;width:14pt">{i + 1}</b><b style="font-family:Oswald;font-size:15pt;flex:1">{escape(wd(w).replace("-", ""))}</b>'
                     f'{letter_box(nsyl(w), key, 32, 24, 15)}</div>')
    sortbank = " &nbsp;·&nbsp; ".join(f"<b>{escape(wd(w).replace('-', ''))}</b>" for w in D2_35_B)
    cols = ""
    for c in (1, 2, 3):
        body = (f'<div class="ans" style="font-size:12pt;line-height:1.5">{"<br>".join(escape(wd(w).replace("-", "")) for w in D2_35_SORT[c])}</div>' if key else "")
        cols += (f'<div class="box" style="min-height:76pt;padding:4pt 8pt"><b class="h" style="font-size:11.5pt">{c} clap{"s" if c > 1 else ""}</b>{body}</div>')
    ex = beat_row(D2_35_EX, size=15)
    bank = " · ".join(escape(wd(w)) for w in D2_35_BANK)
    mine = beat_row(D2_35_EX if key else None, size=15)
    inner = (f'<div class="part">A · Count the claps<small>Clap each word. Write how many syllables it has.</small></div>'
             f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:6pt 12pt">{"".join(cells)}</div>'
             f'<div class="part" style="margin-top:14pt">B · Sort the words<small>Write each word in the box with its number of claps.</small></div>'
             f'<div style="font-size:11pt;margin-bottom:5pt">{sortbank}</div><div style="display:grid;grid-template-columns:repeat(3,1fr);gap:8pt">{cols}</div>'
             f'<div class="part" style="margin-top:14pt">C · Build a four-beat chant<small>Put one word in each beat. A word with 2 syllables is ti-ti; with 1 it is ta. Write the rhythm syllable under it.</small></div>'
             f'<div style="font-size:10pt;margin-bottom:4pt"><b>Word bank:</b> {bank} · or shh (silent beat)</div>'
             f'<div style="font-size:10pt;margin-bottom:3pt"><b>Example:</b> {" · ".join(wd(w) for w in D2_35_EX)}</div>{ex}'
             f'<div style="font-size:10pt;margin:6pt 0 3pt"><b>Your chant:</b></div>{mine if not key else ex}')
    if key:
        return keypage("Day 2 · 3–5 answer key", "Syllable Chants", inner, n, watermark, "Syllable Chants")
    return sheet(2, "35", "Count, sort and build a chant", inner, n, watermark, key_page="key_a")


def d3_k2(n, watermark=False):
    inner = (f'<div class="how" style="font-size:12.5pt">Design a <b>heart drum</b>. Decorate it with colors and patterns, and draw the sticks. Give your drum a name.</div>'
             f'<div class="box" style="flex:1;min-height:200pt;position:relative"><span class="small" style="position:absolute;left:10pt;top:6pt">Draw your drum here</span></div>'
             f'<div class="part" style="margin-top:10pt">My drum<span class="acc"> ·</span></div>{fl("My drum is called")}'
             f'<div class="part">I would tap it for<span class="acc"> ·</span></div>{fl("I would tap it when")}'
             f'<div class="part">My drum sounds<small>Circle one.</small></div>'
             f'<div style="display:flex;justify-content:space-around;font-size:16pt;margin-bottom:8pt;flex-wrap:nowrap">{circ("SOFT")}{circ("LOUD")}{circ("SLOW")}{circ("FAST")}</div>'
             f'{fl("I would share it with")}')
    return sheet(3, "k2", "Design a heart drum", inner, n, watermark)


def d3_35(n, watermark=False):
    steps = "".join(f'<div style="display:flex;align-items:flex-end;gap:6pt;margin:0 0 6pt;font-size:11pt"><b class="h" style="width:16pt;font-size:13pt">{i}</b><span style="flex:1;border-bottom:1pt solid #000;height:18pt"></span></div>'
                    for i in (1, 2, 3))
    inner = (f'<div class="how">Design a heart drum. Draw it, label three parts, name it, then explain how it keeps a steady beat.</div>'
             f'<div class="box" style="flex:1;min-height:170pt;position:relative"><span class="small" style="position:absolute;left:10pt;top:6pt">Draw your heart drum here · add a pattern and the sticks</span></div>'
             f'<div class="cols" style="gap:14pt;margin-top:8pt"><div>{fl("Drum name")}</div>'
             f'<div><div style="font-size:11pt;margin-bottom:4pt"><b>My drum sounds</b> (circle one)</div>'
             f'<div style="display:flex;justify-content:space-between;font-size:11.5pt;flex-wrap:nowrap">{circ("SOFT")}{circ("LOUD")}{circ("SLOW")}{circ("FAST")}</div></div></div>'
             f'<div class="part">Label three parts<span class="acc"> ·</span><small>Examples: drumhead, rim, sticks, pattern, strap.</small></div>{steps}'
             f'<div class="part">Write two sentences<span class="acc"> ·</span></div>'
             f'<div style="font-size:11pt">1. Explain who would use your drum and when.</div>{lines(2, 20)}'
             f'<div style="font-size:11pt;margin-top:4pt">2. Describe how a steady beat is like a heartbeat.</div>{lines(2, 20)}')
    return sheet(3, "35", "Design, label and explain a heart drum", inner, n, watermark)


def card_html(name, move, size=62):
    return (f'<div class="cut" style="padding:8pt 8pt 8pt;text-align:center;display:flex;flex-direction:column;align-items:center">{pic(name, size)}'
            f'<div class="h" style="font-size:15pt;margin:5pt 0 3pt">{name}</div><div style="font-size:10.5pt;line-height:1.25">{move}</div></div>')


def d4_cards(n, watermark=False):
    cards = "".join(card_html(a, b, 74).replace("font-size:10.5pt", "font-size:12pt") for a, b in CARDS)
    inner = (f'<div class="how">Cut out the cards, or just point at them. Tap a pencil while students move; stop tapping and they freeze.</div>'
             f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:10pt;flex:1;min-height:0;grid-auto-rows:minmax(0,1fr)">{cards}</div>')
    return page("Picture cards · cut out or point", "DAY 4", "Move cards", inner, n, watermark, title="Heartbeat Freeze")


def d4_k2(n, watermark=False, key=False):
    rows = ""
    items = [("Slow taps: I moved", ["SLOWLY", "QUICKLY"], 0), ("Fast taps: I moved", ["SLOWLY", "QUICKLY"], 1),
             ("When the tapping stopped, I", ["FROZE", "KEPT MOVING"], 0)]
    for q, opts, a in items:
        rows += (f'<div style="display:flex;align-items:center;gap:10pt;font-size:14pt;margin:0 0 9pt"><span style="flex:1">{q}</span>'
                 f'{"".join(circ(o, key and i == a) for i, o in enumerate(opts))}</div>')
    mini = "".join(f'<div style="text-align:center">{pic(a, 46)}<div style="font-size:10pt">{a}</div></div>' for a, _ in CARDS)
    inner = (f'<div class="how" style="font-size:12.5pt">Think about how you moved. Circle your answers.</div>{rows}'
             f'<div class="part">My favorite card<small>Circle one.</small></div>'
             f'<div class="box" style="display:flex;justify-content:space-around;padding:6pt 4pt">{mini}</div>'
             f'<div class="part" style="margin-top:10pt">My freeze pose<small>Draw yourself frozen like a statue.</small></div>'
             f'<div class="box" style="flex:1;min-height:150pt"></div>')
    if key:
        return keypage("Day 4 · K–2 answer key", DAY_SHEETS[4][0], inner, n, watermark, DAY_SHEETS[4][0])
    return sheet(4, "k2", "How did you move?", inner, n, watermark, key_page="key_c")


def d4_35(n, watermark=False):
    rows = "".join(f"<tr style='height:40pt'><td style='text-align:center;font-family:Oswald;font-weight:700'>{a}</td><td></td>"
                   f"<td style='text-align:center;font-family:Oswald;font-weight:500;font-size:9.5pt'>SLOW &nbsp; MEDIUM &nbsp; FAST</td></tr>" for a, _ in CARDS[:6])
    inner = (f'<div class="how">Think about the cards you moved to. For each card, describe how you moved, and circle the speed of the tap that fit it best.</div>'
             f'<table class="t" style="font-size:10.5pt"><tr><th style="width:18%">Card</th><th>How I moved</th><th style="width:30%">Tap speed</th></tr>{rows}</table>'
             f'<div class="part">Design a freeze game<span class="acc"> ·</span></div>'
             f'<div style="font-size:11pt">Invent a new freeze game for the class. Write the rules in three steps.</div>'
             f'{lines(1, 26)}{lines(1, 26)}{lines(1, 26)}'
             f'<div class="part">Think about it<span class="acc"> ·</span></div>'
             f'<div style="font-size:11pt">How does a steady tap help a group move together? Write two sentences.</div>{lines(4, 26)}')
    return sheet(4, "35", "Reflect on moving and freezing", inner, n, watermark)


def match_svg(key=False, scale=1.0):
    w, h = 460, 300
    ys = [32 + i * 48 for i in range(6)]
    left = "".join(text(30, y + 7, MATCH[i].upper(), 20, 700, anchor="start") + f'<circle cx="150" cy="{y}" r="5" fill="#000"/>' for i, y in enumerate(ys))
    right = ""
    for j, y in enumerate(ys):
        right += f'<circle cx="310" cy="{y}" r="5" fill="#000"/><g transform="translate(325 {y - 22}) scale(.44)">{PIC_INNER[MATCH[MATCH_PIC_ORDER[j]]]}</g>'
    ln = ""
    if key:
        for i, y in enumerate(ys):
            j = MATCH_PIC_ORDER.index(i)
            ln += f'<line x1="155" y1="{y}" x2="305" y2="{ys[j]}" stroke="{ACCENT}" stroke-width="3" stroke-linecap="round"/>'
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w * scale}pt" height="{h * scale}pt" viewBox="0 0 {w} {h}" style="display:block;margin:0 auto">{left}{right}{ln}</svg>'


PIC_INNER = {nm: re.sub(r'^<svg[^>]*><g>|</g></svg>$', "", pic(nm, 100)) for nm in ["heart", "drum", "lantern", "trumpet", "piano", "gong", "cymbal", "card", "star", "snowflake"]}


def d5_k2(n, watermark=False, key=False):
    tr = "".join(f'<div class="box" style="padding:4pt 8pt">{svg(118, 46, dotted(w, 40, 118))}</div>' for w in TRACE)
    inner = (f'<div class="part">A · Match<small>Draw a line from each word to its picture.</small></div>{match_svg(key)}'
             f'<div class="part" style="margin-top:10pt">B · Trace the February words</div>'
             f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:8pt 14pt">{tr}</div>'
             f'<div class="part" style="margin-top:12pt">C · Draw a lantern night</div>'
             f'<div class="box" style="flex:1;min-height:80pt"></div>')
    if key:
        return keypage("Day 5 · K–2 answer key", "Match and Trace", inner, n, watermark, "Match and Trace")
    return sheet(5, "k2", "Match, trace and draw", inner, n, watermark, key_page="key_b")


def ws_grid_svg(cell, key=False, size=None):
    on = {c for cells in PLACE.values() for c in cells} if key else set()
    out = []
    for y in range(WS_N):
        for x in range(WS_N):
            cx, cy = x * cell + cell / 2, y * cell + cell / 2
            if (y, x) in on:
                out.append(f'<rect x="{x * cell + 1.5:.1f}" y="{y * cell + 1.5:.1f}" width="{cell - 3:.1f}" height="{cell - 3:.1f}" rx="{cell / 3:.1f}" '
                           f'fill="{ACCENT}" fill-opacity=".22" stroke="{ACCENT}" stroke-width="1"/>')
            out.append(text(cx, cy + (size or cell * 0.55) * 0.36, GRID[y][x], size or cell * 0.55, 500))
    out.append(f'<rect x="0.7" y="0.7" width="{WS_N * cell - 1.4}" height="{WS_N * cell - 1.4}" rx="6" fill="none" stroke="#000" stroke-width="1.4"/>')
    return svg(WS_N * cell, WS_N * cell, "".join(out), "display:block")


def code_of(ch):
    return ord(ch) - 64


def decode_html(key=False):
    def word(w):
        return "".join(f'<span style="display:inline-block;text-align:center;margin:0 2pt"><span style="display:block;font-size:10pt;font-family:Oswald;font-weight:500">{code_of(c)}</span>'
                       f'{letter_box(c, key, 25, 30, 16)}</span>' for c in w)
    r1 = "".join(f'<span style="margin-right:14pt;white-space:nowrap">{word(w)}</span>' for w in DECODE_MSG[:3])
    r2 = "".join(f'<span style="margin-right:14pt;white-space:nowrap">{word(w)}</span>' for w in DECODE_MSG[3:])
    codes = " ".join(f"{chr(65 + i)}={i + 1}" for i in range(26))
    return (f'<div class="box" style="font-size:9.5pt;padding:4pt 8pt;letter-spacing:.03em;margin-bottom:5pt"><b>Code:</b> {codes}</div>'
            f'<div style="margin-bottom:8pt">{r1}</div><div>{r2}</div>')


def d5_35(n, watermark=False):
    words = "".join(f'<div style="font-size:10.5pt;margin:0 0 3pt;display:flex;align-items:center;gap:6pt">{checkbox(10)}'
                    f'<b style="font-family:Oswald;font-weight:500;letter-spacing:.05em">{w}</b></div>' for w in WS_WORDS)
    inner = (f'<div class="how">Find the 12 February words. They go across, down, or diagonally down to the right. Tick each word when you find it.</div>'
             f'<div style="display:flex;gap:16pt;align-items:flex-start"><div>{ws_grid_svg(28)}</div>'
             f'<div class="box" style="flex:1;padding:6pt 10pt">{words}</div></div>'
             f'<div class="part" style="margin-top:10pt">Decode the message<small>Write the letter for each number.</small></div>{decode_html()}'
             f'<div class="part" style="margin-top:10pt">Word work<small>Pick 2 words from the list. Write a sentence with each.</small></div>{lines(2, 17)}')
    return sheet(5, "35", "Find the words, then crack the code", inner, n, watermark, key_page="key_b")


def d6_k2(n, watermark=False, key=False):
    qs = ""
    for i, (q, opts, a) in enumerate(D6_K2_Q):
        qs += (f'<div style="display:flex;align-items:center;gap:8pt;font-size:13pt;margin:0 0 8pt"><b class="h" style="width:16pt">{i + 1}</b>'
               f'<span style="flex:1">{q}</span>{"".join(circ(o, key and j == a) for j, o in enumerate(opts))}</div>')
    inner = (f'<div class="box" style="font-size:12.5pt;line-height:1.42;padding:8pt 12pt">{" ".join(D6_K2_TEXT)}</div>'
             f'<div class="part">Questions<small>Circle the answer.</small></div>{qs}'
             f'<div class="part">Draw a music job<small>Pick one job. Draw the person at work.</small></div>'
             f'<div class="box" style="flex:1;min-height:150pt"></div>'
             f'<div style="margin-top:8pt;display:flex;gap:10pt;font-size:13pt;align-items:flex-end"><b>This person</b><span style="flex:1;border-bottom:1pt solid #000;height:20pt"></span></div>')
    if key:
        return keypage("Day 6 · K–2 answer key", DAY_SHEETS[6][0], inner, n, watermark, DAY_SHEETS[6][0])
    return sheet(6, "k2", "Listen, circle and draw", inner, n, watermark, key_page="key_b")


def d6_35(n, watermark=False, key=False):
    left = "".join(f'<div style="display:flex;align-items:center;gap:8pt;font-size:12pt;margin:0 0 7pt"><b class="h" style="width:14pt">{i + 1}</b><b>{escape(JOBS[i][0])}</b></div>'
                   for i in range(5))
    right = "".join(f'<div style="display:flex;align-items:center;gap:8pt;font-size:11pt;margin:0 0 7pt">{letter_box("ABCDE"[j] if False else "", False, 24, 18, 12)}'
                    f'<b class="h" style="width:12pt;font-size:11pt">{"ABCDE"[j]}</b><span>{JOBS[k][1]}</span></div>' for j, k in enumerate(D6_35_MATCH_ORDER))
    if key:
        right = "".join(f'<div style="display:flex;align-items:center;gap:8pt;font-size:10.5pt;margin:0 0 5pt"><b class="h" style="width:12pt;font-size:11pt">{"ABCDE"[j]}</b>'
                        f'<span>{JOBS[k][1]}</span><b class="ans">{k + 1}</b></div>' for j, k in enumerate(D6_35_MATCH_ORDER))
    inner = (f'<div class="box" style="font-size:11.8pt;line-height:1.46;padding:8pt 12pt">{D6_35_TEXT}</div>'
             f'<div class="part">A · Who does what?<small>Write the number of the job in the box next to its description.</small></div>'
             f'<div class="cols" style="gap:10pt"><div style="flex:0 0 1.8in">{left}</div><div>{right}</div></div>'
             f'<div class="part" style="margin-top:4pt">B · Choose one<small>Write a job ad OR five interview questions.</small></div>'
             f'<div class="cols" style="gap:12pt"><div class="box" style="padding:5pt 9pt"><b class="h" style="font-size:11.5pt">Job ad</b>{fl("Job", "style=margin:8pt 0 12pt")}'
             f'{fl("Duties", "style=margin:0 0 12pt")}{fl("Skills", "style=margin:0 0 12pt")}{fl("Why apply", "style=margin:0 0 6pt")}</div>'
             f'<div class="box" style="padding:5pt 9pt"><b class="h" style="font-size:11.5pt">Five interview questions</b>'
             f'{"".join(f"<div class=ln2 style=height:30pt></div>" for _ in range(5))}</div></div>'
             f'<div class="part" style="margin-top:8pt">C · Think about it<small>Which job would you most like to try, and why?</small></div>{lines(2, 26)}')
    if key:
        return keypage("Day 6 · 3–5 answer key", DAY_SHEETS[6][1], inner, n, watermark, DAY_SHEETS[6][1])
    return sheet(6, "35", "Read, match and write", inner, n, watermark, key_page="key_b")


def d7_k2(n, watermark=False):
    cards = "".join(f'<div class="bx" style="padding:0"><div class="w" style="font-size:15pt;min-height:26pt;padding-top:6pt">{escape(wd(w))}</div>'
                    f'<div class="d" style="height:16pt">{dots_html(w)}</div></div>' for w in D7_CARDS)
    inner = (f'<div class="how" style="font-size:12pt">Pick four words from the word bank. Write one word in each beat box. Clap your chant and say it. '
             f'One dot is one clap; two dots in a box are two quick claps; <b>shh</b> is a silent beat.</div>'
             f'<div class="part">Word bank</div><div style="display:grid;grid-template-columns:repeat(6,1fr);gap:6pt">{cards}</div>'
             f'<div class="part" style="margin-top:12pt">My chant 1</div>{beat_row(None, hgt=60)}'
             f'<div class="part" style="margin-top:12pt">My chant 2</div>{beat_row(None, hgt=60)}'
             f'<div class="part" style="margin-top:12pt">Check<span class="acc"> ·</span></div>'
             + "".join(f'<div style="font-size:12pt;margin:0 0 4pt">{checkbox(12)} &nbsp;{c}</div>' for c in
                       ("I wrote one word in every beat box.", "I clapped my chant with a steady beat.", "I said my chant for a friend."))
             + f'<div class="part" style="margin-top:8pt">Draw a picture for my chant</div><div class="box" style="flex:1;min-height:40pt"></div>')
    return sheet(7, "k2", "Build a chant from word cards", inner, n, watermark, key_page="key_c")


def d7_35(n, watermark=False):
    bank = " · ".join(f"<b>{escape(wd(w))}</b> ({SYL[beat_kind(w)]})" for w in D7_CARDS)
    chants = ""
    for c in (1, 2):
        chants += (f'<div class="part" style="margin-top:8pt">Chant {c}</div>{beat_row(None, hgt=52)}'
                   f'<div style="font-size:10pt;margin:4pt 0 0"><b>Write the syllables under each box:</b> ta · ti-ti · shh &nbsp;&nbsp; <b>Beats counted:</b> {letter_box("", False, 26, 20, 12)}</div>')
    inner = (f'<div class="how">Compose two four-beat chants. Each box holds one word or a shh. A one-syllable word is <b>ta</b>; a two-syllable word is <b>ti-ti</b>. '
             f'Use the word bank or your own February words (one or two syllables).</div>'
             f'<div class="box" style="font-size:10.5pt;padding:5pt 10pt"><b>Word bank:</b> {bank}</div>'
             f'{chants}'
             f'<div class="part" style="margin-top:12pt">Share it<span class="acc"> ·</span></div>'
             f'<div style="font-size:11pt">{checkbox(12)} &nbsp;My partner said my chant while I patted the beat.<br>{checkbox(12)} &nbsp;I said my partner’s chant.</div>'
             f'<div style="font-size:11pt;margin-top:8pt"><b>Which words made your chant smooth to say?</b></div>{lines(2, 22)}'
             f'<div class="part" style="margin-top:8pt">Draw a picture for your best chant</div><div class="box" style="flex:1;min-height:40pt"></div>')
    return sheet(7, "35", "Compose and mark two chants", inner, n, watermark, key_page="key_c")


def d7_cards(n, watermark=False):
    cards = []
    for w in D7_CARDS:
        cards.append(f'<div class="cut" style="text-align:center;padding:14pt 4pt;display:flex;flex-direction:column;align-items:center;justify-content:center">'
                     f'<div class="h" style="font-size:25pt">{escape(wd(w))}</div><div style="margin-top:8pt;height:16pt;display:flex;gap:6pt;align-items:center">{dots_html(w)}</div>'
                     f'<div class="l" style="font-size:12pt;margin-top:6pt">{SYL[beat_kind(w)]}</div></div>')
    inner = (f'<div class="how">Cut out the word cards, or hold up this page. Each card is one beat of a chant. Four cards in a row make a four-beat chant.</div>'
             f'<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:10pt;flex:1;margin-bottom:6pt;grid-auto-rows:1fr">{"".join(cards)}</div>')
    return page("Word cards · cut out or point", "DAY 7", "Chant cards", inner, n, watermark, title="Lantern Chant Book")


def d7_book(n, watermark=False):
    chant = lambda t: (f'<div class="part" style="margin-top:8pt">{t}</div>{beat_row(None, hgt=40)}')
    inner = (f'<div class="how">Copy your best chants here and keep this page. Draw a picture that goes with each one.</div>'
             f'<div style="display:flex;gap:16pt">{fl("Chant book of", "style=flex:1")}{fl("Class", "style=flex:0 0 1.8in")}</div>'
             f'{chant("Chant 1")}<div style="display:flex;gap:12pt;margin-top:8pt"><div class="box" style="flex:1;height:148pt"><span class="small">My picture</span></div>'
             f'<div style="flex:1">{fl("Title")}<div style="font-size:11pt;margin:4pt 0">I said it:</div>'
             f'<div style="font-size:12pt;line-height:1.7">{checkbox(12)} slowly &nbsp; {checkbox(12)} quickly &nbsp; {checkbox(12)} softly<br>{checkbox(12)} with a partner &nbsp; {checkbox(12)} with the class</div></div></div>'
             f'{chant("Chant 2")}<div style="display:flex;gap:12pt;margin-top:8pt"><div class="box" style="flex:1;height:148pt"><span class="small">My picture</span></div>'
             f'<div style="flex:1">{fl("Title")}<div style="font-size:11pt;margin:4pt 0">I said it:</div>'
             f'<div style="font-size:12pt;line-height:1.7">{checkbox(12)} slowly &nbsp; {checkbox(12)} quickly &nbsp; {checkbox(12)} softly<br>{checkbox(12)} with a partner &nbsp; {checkbox(12)} with the class</div></div></div>')
    return page("Chant book page · keep it", "DAY 7", "Keepsake", inner, n, watermark, name=True, title="My Lantern Chant Book")


BANK_ORDER_K2 = [6, 2, 9, 0, 11, 4, 8, 1, 10, 3, 7, 5]    # K-2 bank order (shuffled indexes into BINGO[:12])
BANK_ORDER_35 = [10, 3, 14, 7, 0, 12, 5, 9, 1, 15, 4, 8, 13, 2, 6, 11]


def board(cells, size, h):
    return (f'<div style="display:grid;grid-template-columns:repeat({size},1fr);gap:0;border:2pt solid #000;border-radius:6pt;overflow:hidden">'
            + "".join(f'<div style="height:{h}pt;border:1pt solid #000"></div>' for _ in range(cells)) + '</div>')


def d8_k2(n, watermark=False):
    bank = "".join(f'<div style="font-size:12.5pt;margin:0 0 5pt;display:flex;align-items:center;gap:6pt">{checkbox(11)}<b style="font-family:Oswald;font-weight:500;letter-spacing:.04em">{BINGO[i][0]}</b></div>'
                   for i in BANK_ORDER_K2)
    inner = (f'<div class="how" style="font-size:12pt">Write all {BINGO_K2} words from the word bank in the squares, one word in each square, in any order. Listen to the clues. Cover the answer when you hear it. '
             f'Three squares across in one row is <b>BINGO</b>.</div>'
             f'<div class="part" style="margin:6pt 0 4pt">My bingo board<span class="acc"> ·</span></div>'
             f'<div style="display:flex;gap:16pt;align-items:flex-start"><div style="flex:0 0 3.8in">{board(BINGO_K2, BINGO_K2_COLS, 70)}</div>'
             f'<div class="box" style="flex:1;padding:6pt 10pt"><b class="h" style="font-size:12pt">Word bank</b><div style="margin-top:4pt;column-count:1">{bank}</div></div></div>'
             f'<div class="part" style="margin-top:10pt">My favorite day this week<span class="acc"> ·</span></div>'
             f'<div class="box" style="flex:1;min-height:70pt"></div>')
    return sheet(8, "k2", "February bingo for grades K–2", inner, n, watermark, key_page="key_c")


def d8_35(n, watermark=False):
    bank = "".join(f'<div style="font-size:11pt;margin:0 0 3pt;display:flex;align-items:center;gap:6pt">{checkbox(10)}<b style="font-family:Oswald;font-weight:500;letter-spacing:.04em">{BINGO[i][0]}</b></div>'
                   for i in BANK_ORDER_35)
    inner = (f'<div class="how">Write all {BINGO_35} words from the word bank in the squares, one word in each square, in any order. Cover each answer as the clues are read. '
             f'A full row, a full column or a corner-to-corner line is <b>BINGO</b>.</div>'
             f'<div style="display:flex;gap:14pt;align-items:flex-start"><div style="flex:0 0 5.1in">{board(BINGO_35, 4, 86)}</div>'
             f'<div class="box" style="flex:1;padding:5pt 8pt"><b class="h" style="font-size:12pt">Word bank</b><div style="margin-top:4pt">{bank}</div></div></div>'
             f'<div class="part" style="margin-top:10pt">Reflection<span class="acc"> ·</span></div>'
             f'<div style="font-size:11pt">1. Which word was hardest to remember? How did you remember it?</div>{lines(3, 26)}'
             f'<div style="font-size:11pt;margin-top:4pt">2. Which day of this week did you enjoy most, and why?</div>{lines(3, 26)}')
    return sheet(8, "35", "February bingo and reflection", inner, n, watermark, key_page="key_c")


def d8_quiz(n, watermark=False):
    rows = "".join(f"<tr style='height:31pt'><td class='ans' style='text-align:center'>{i + 1}</td><td style='font-size:10.5pt'>{c}</td>"
                   f"<td><b>{a}</b></td><td style='text-align:center'>{'K–5' if i < BINGO_K2 else '3–5'}</td><td style='text-align:center'>{checkbox(10)}</td></tr>"
                   for i, (a, c) in enumerate(BINGO))
    inner = (f'<div class="how"><b>Sub: read the clue aloud, not the answer.</b> Students find the answer on their board. Use clues 1–12 for grades K–2 and all 16 for grades 3–5. K–2 wins with three squares across in one row; 3–5 wins with a row, a column or a corner-to-corner line. '
             f'Tick the box when you have read a clue. Read in any order.</div>'
             f'<table class="t"><tr><th style="width:6%">#</th><th>Clue (read this)</th><th style="width:17%">Answer</th><th style="width:9%">Grades</th><th style="width:7%">Read</th></tr>{rows}</table>'
             f'<div class="box" style="margin-top:auto;font-size:10.5pt"><b>To check a bingo:</b> ask the student to read their covered words. Each one must match a clue you read. '
             f'Say “Great job!” even if it is not a bingo yet.</div>')
    return page("Read-aloud quiz · clues and answers for the sub", "DAY 8", "For the sub", inner, n, watermark, title="February Bingo Showdown")


def early1(n, watermark=False):
    inner = (f'<div class="how">Finished early? Pick one (or do them all).</div>'
             f'<div class="cols" style="gap:14pt"><div class="box" style="height:340pt"><b class="h" style="font-size:13pt">Invent a new drum</b>'
             f'<div style="font-size:10.5pt;margin-top:3pt">Draw it. How does it make sound? Circle one:</div>'
             f'<div style="display:flex;gap:4pt;flex-wrap:nowrap;font-size:11pt">{circ("SHAKE")}{circ("TAP")}{circ("BLOW")}{circ("PLUCK")}</div></div>'
             f'<div class="box" style="height:340pt"><b class="h" style="font-size:13pt">Design a valentine card</b>'
             f'<div style="font-size:10.5pt;margin-top:3pt">Who is it for? Write a kind word inside. Add a picture.</div></div></div>'
             f'<div class="part" style="margin-top:12pt">My four-beat chant<small>One word in each beat. Clap it for a friend.</small></div>{beat_row(None, hgt=40)}'
             f'<div class="part" style="margin-top:12pt">My music words<small>Write 3 sentences with February words: heart, drum, lantern, jazz, beat.</small></div>{lines(3, 26)}')
    return page("Early finishers · grades K–5", "ANY DAY", "Early finishers", inner, n, watermark, name=True, title="Early Finishers")


def early2(n, watermark=False):
    inner = (f'<div class="how">More for fast workers. Choose any box.</div>'
             f'<div class="cols" style="gap:14pt"><div class="box" style="height:170pt"><b class="h" style="font-size:13pt">Syllable hunt</b>'
             f'<div style="font-size:10.5pt;margin-top:3pt">Find 5 words in the room. Clap each one. Write the word and its claps.</div>'
             + "".join(f'<div style="display:flex;gap:6pt;align-items:flex-end;margin-top:5pt"><span style="flex:1;border-bottom:1pt solid #000;height:14pt"></span><span style="width:28pt;border-bottom:1pt solid #000;height:14pt"></span></div>' for _ in range(5))
             + f'</div><div class="box" style="height:170pt"><b class="h" style="font-size:13pt">February word art</b>'
             f'<div style="font-size:10.5pt;margin-top:3pt">Write a February word in big letters. Fill the letters with patterns.</div></div></div>'
             f'<div class="part" style="margin-top:12pt">Write a chant<small>Write 4 words that fit a steady beat, like “heart, beat, heart, beat.”</small></div>{lines(2)}'
             f'<div class="part" style="margin-top:8pt">What would you tell a friend?<small>Write 2 sentences about a musician from this month, or one thing you learned.</small></div>{lines(3)}'
             f'<div class="part" style="margin-top:8pt">Draw a lantern night<small>Include a lantern, a drum and something that makes a sound.</small></div><div class="box" style="flex:1;min-height:110pt"></div>')
    return page("More early finishers · grades K–5", "ANY DAY", "Early finishers", inner, n, watermark, name=True, title="Early Finishers 2")


def exit_page(n, watermark=False):
    t = ('<div class="cut" style="padding:8pt 10pt;height:100%"><b class="h" style="font-size:12pt">Exit ticket</b>'
         '<div style="font-size:10.5pt;margin-top:4pt">Name ________________</div><div style="font-size:10.5pt;margin-top:6pt">Today I learned:</div>'
         '<div class="ln2" style="height:18pt"></div><div class="ln2" style="height:18pt"></div>'
         '<div style="font-size:10.5pt;margin-top:6pt">I felt: &nbsp; ' + circ("GOT IT") + circ("ALMOST") + circ("NOT YET") + '</div></div>')
    inner = (f'<div class="how">Cut apart. Hand one to each student at the end of any day.</div>'
             f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:10pt;flex:1;grid-auto-rows:1fr;margin-bottom:6pt">{t * 8}</div>')
    return page("Exit tickets · any day", "ANY DAY", "Exit tickets", inner, n, watermark)


def labels_page(n, watermark=False):
    labs = "".join(f'<div class="cut" style="text-align:center;padding:14pt 6pt"><div class="h" style="font-size:22pt;color:{ACCENT}">Day {d["n"]}</div>'
                   f'<div class="h" style="font-size:13pt;margin-top:4pt">{escape(d["title"])}</div></div>' for d in DAYS)
    inner = (f'<div class="how">Cut out and tape to folders for the sub tub. Put each day’s plan, K–2 sheets and 3–5 sheets in its folder.</div>'
             f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:10pt">{labs}</div>'
             f'<div class="cut" style="margin-top:12pt;text-align:center;padding:30pt 10pt;flex:1;display:flex;flex-direction:column;justify-content:center">'
             f'<div class="h" style="font-size:40pt">February Music Sub Tub</div><div class="l" style="font-size:16pt;margin-top:8pt">Open me first · start with the welcome sheet</div></div>')
    return page("Folder labels · cut out", "FOR THE TEACHER", "Sub tub labels", inner, n, watermark)


def cert_page(n, watermark=False):
    one = (f'<div class="box" style="flex:1;margin:14pt 0 12pt;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;border-width:2.4pt">'
           f'<div style="display:flex;gap:14pt;margin-bottom:6pt">{pic("star", 34)}{pic("heart", 34)}{pic("drum", 34)}</div>'
           f'<div class="h" style="font-size:30pt">Music Class Star</div><div style="font-size:13pt;margin-top:6pt">presented to</div>'
           f'<div style="width:70%;border-bottom:1.5pt solid #000;height:24pt"></div>'
           f'<div style="font-size:13pt;margin-top:10pt">for being a great musician today</div>'
           f'<div style="display:flex;gap:30pt;width:80%;margin-top:14pt;font-size:11pt"><div style="flex:1;border-top:1pt solid #000;padding-top:2pt">Guest teacher</div>'
           f'<div style="flex:0 0 1.3in;border-top:1pt solid #000;padding-top:2pt">Date</div></div></div>')
    return page("Awards · cut apart", "FOR THE SUB", "Class star awards", f'{one}{one}', n, watermark)


def report_page(n, watermark=False):
    rows = "".join("<tr><td style='height:32pt'></td><td></td><td></td><td></td></tr>" for _ in range(6))
    inner = (f'<div class="how">Substitute: thank you! Please fill this in and leave it on the teacher’s desk.</div>'
             f'<div class="cols" style="gap:16pt"><div>{fl("Your name")}</div><div>{fl("Date")}</div></div>'
             f'<table class="t"><tr><th style="width:24%">Class / grade</th><th style="width:12%">Day #</th><th style="width:30%">What we finished</th>'
             f'<th>Notes</th></tr>{rows}</table>'
             f'<div class="part">Students who were a big help<span class="acc"> ·</span></div>{lines(2, 28)}'
             f'<div class="part">Anything I should know?<span class="acc"> ·</span></div>{lines(3, 28)}'
             f'<div class="part">Games we did<span class="acc"> ·</span></div>'
             f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:4pt 14pt;font-size:11pt">'
             + "".join(f'<div>{checkbox(12)} &nbsp;{g}</div>' for g, _, _ in GAMES)
             + f'</div><div class="part">Copies left over<span class="acc"> ·</span></div>{lines(1)}')
    return page("Sub report · notes for the music teacher", "FOR THE SUB", "Leave on the desk", inner, n, watermark)


# ---------------------------------------------------------------- answer keys (all computed from the data)
def key_a_page(n, watermark=False):
    k1 = "".join(f"<tr><td>{i + 1}</td><td>{q.replace('___', '____')}</td><td class='ans'>{o[a]}</td></tr>" for i, (q, o, a) in enumerate(D1_K2_Q))
    k2 = "".join(f"<tr><td>{i + 1}</td><td>{q}</td><td class='ans'>{a}</td></tr>" for i, (q, a) in enumerate(D1_35_Q))
    a1 = "".join(f"<tr><td>A{i + 1}</td><td>{wd(w).replace('-', ' · ')}</td><td class='ans'>{nsyl(w)}</td></tr>" for i, w in enumerate(D2_K2_A))
    a1 += "".join(f"<tr><td>B{i + 1}</td><td>{wd(w).replace('-', ' · ')}</td><td class='ans'>{nsyl(w)}</td></tr>" for i, w in enumerate(D2_K2_B))
    a2 = "".join(f"<tr><td>A{i + 1}</td><td>{wd(w).replace('-', ' · ')}</td><td class='ans'>{nsyl(w)}</td></tr>" for i, w in enumerate(D2_35_A))
    srt = "".join(f"<tr><td>B · {c}</td><td colspan=2 class='ans'>{', '.join(wd(w).replace('-', '') for w in D2_35_SORT[c])}</td></tr>" for c in (1, 2, 3))
    ex = " ".join(f"{wd(w)} {SYL[beat_kind(w)]}" for w in D2_35_EX)
    inner = (f'<div class="cols" style="gap:16pt"><div>'
             f'<div class="part" style="margin-top:2pt">Day 1 · K–2 {DAY_SHEETS[1][0]}</div><table class="t" style="font-size:9.5pt">{k1}</table>'
             f'<div class="part">Day 1 · 3–5 {DAY_SHEETS[1][1]}</div><table class="t" style="font-size:9.5pt">{k2}</table>'
             f'<p class="small">Draw-it tasks: accept any picture that matches the reading. For 3–5, the caption should say what the person did.</p>'
             f'</div><div>'
             f'<div class="part" style="margin-top:2pt">Day 2 · K–2 Clap the Name Beats</div><table class="t" style="font-size:9.5pt"><tr><th>Item</th><th>Word</th><th>Claps</th></tr>{a1}</table>'
             f'<p class="small">Part A: the first circles up to the count are colored. Part C: any word and matching circles.</p>'
             f'<div class="part">Day 2 · 3–5 Name Beat Chants</div><table class="t" style="font-size:9.5pt"><tr><th>Item</th><th>Word</th><th>Claps</th></tr>{a2}{srt}</table>'
             f'<p style="font-size:10pt"><b>C · Example chant:</b> <span class="ans">{ex}</span>. Any four words work if each beat has one word (ta for 1 syllable, ti-ti for 2) or shh.</p>'
             f'</div></div>')
    return keypage("Answer keys · Days 1 and 2", "Days 1 and 2", inner, n, watermark)


def key_b_page(n, watermark=False):
    loc = {(0, 1): "across", (1, 0): "down", (1, 1): "diagonal"}
    words = "".join(f"<div style='font-size:9.5pt;margin:0 0 2pt'><b>{w}</b> · row {PLACE[w][0][0] + 1}, col {PLACE[w][0][1] + 1}, "
                    f"{loc[(PLACE[w][1][0] - PLACE[w][0][0], PLACE[w][1][1] - PLACE[w][0][1])]}</div>" for w in WS_WORDS)
    j = "".join(f"<tr><td>{i + 1}</td><td>{JOBS[i][0]}</td><td class='ans'>{'ABCDE'[D6_35_MATCH_ORDER.index(i)]}</td></tr>" for i in range(5))
    k6 = "".join(f"<tr><td>{i + 1}</td><td>{q}</td><td class='ans'>{o[a]}</td></tr>" for i, (q, o, a) in enumerate(D6_K2_Q))
    msg = " ".join(DECODE_MSG)
    pairs = " ".join(f"{c}={code_of(c)}" for c in dict.fromkeys("".join(DECODE_MSG)))
    inner = (f'<div class="cols" style="gap:16pt"><div style="flex:0 0 3.3in">'
             f'<div class="part" style="margin-top:2pt">Day 5 · 3–5 Word Search</div>{ws_grid_svg(19, key=True, size=11)}<div style="margin-top:6pt">{words}</div></div>'
             f'<div><div class="part" style="margin-top:2pt">Day 5 · 3–5 Decode</div>'
             f'<p style="font-size:12pt"><b class="ans">{msg}</b></p><p class="small">{pairs}</p>'
             f'<div class="part">Day 5 · K–2 Match and Trace</div><div style="margin-bottom:4pt">{match_svg(True, 0.6)}</div>'
             f'<p class="small">Part B and C: check tracing and drawings.</p></div></div>'
             f'<div class="cols" style="gap:16pt"><div><div class="part">Day 6 · K–2 {DAY_SHEETS[6][0]}</div><table class="t" style="font-size:9.5pt">{k6}</table>'
             f'<p class="small">Draw a job: accept any of the five jobs. The sentence should say what the person does.</p></div>'
             f'<div><div class="part">Day 6 · 3–5 Who does what?</div><table class="t" style="font-size:9.5pt"><tr><th>#</th><th>Job</th><th>Letter</th></tr>{j}</table>'
             f'<p class="small">Part B: a job ad names a job, duties and skills, or five questions ask about the job.</p></div></div>')
    return keypage("Answer keys · Days 5 and 6", "Days 5 and 6", inner, n, watermark)


def key_c_page(n, watermark=False):
    bingo = "".join(f"<tr><td>{i + 1}</td><td class='ans'>{a}</td><td>{'K–5' if i < BINGO_K2 else '3–5'}</td></tr>" for i, (a, _) in enumerate(BINGO))
    inner = (f'<div class="cols" style="gap:16pt"><div>'
             f'<div class="part" style="margin-top:2pt">Day 3 · Heart Drum Design Lab (K–2 and 3–5)</div>'
             f'<p style="font-size:12pt">Open-ended. Look for a drum drawing, a name, when it would be tapped and one circled word (K–2), or a drum drawing, a name, three labeled parts, one circled word and two sentences (3–5).</p>'
             f'<div class="part">Day 4 · Heartbeat Freeze</div>'
             f'<p style="font-size:12pt"><b>K–2 circles:</b> slow taps <b class="ans">SLOWLY</b>, fast taps <b class="ans">QUICKLY</b>, tapping stopped <b class="ans">FROZE</b>. The pose and favorite card are personal. '
             f'<b>3–5:</b> answers vary; a good answer links the tap speed to the way the body moved.</p>'
             f'<div class="part">Day 7 · Lantern Chant Book</div>'
             f'<p style="font-size:12pt">Check that every chant has four beat boxes with one word (or shh) each. For 3–5, ta must be written under one-syllable words and ti-ti under two-syllable words. '
             f'Example: <span class="ans">{" ".join(f"{wd(w)} {SYL[beat_kind(w)]}" for w in D2_35_EX)}</span>.</p>'
             f'<div class="part">Day 8 · Reflection</div><p style="font-size:12pt">Personal answers.</p>'
             f'</div><div style="flex:0 0 3.1in"><div class="part" style="margin-top:2pt">Day 8 · Bingo answers</div>'
             f'<table class="t roomy" style="font-size:11pt"><tr><th>#</th><th>Answer</th><th>Grades</th></tr>{bingo}</table>'
             f'<p class="small">The K–2 board (12 squares) uses the first 12 words; the 3–5 board (16 squares) uses all 16. The clues are on {pg("d8_quiz")}.</p></div></div>'
             f'<div class="part" style="margin-top:6pt">Where the other answers are</div>'
             f'<p style="font-size:12pt">Days 1 and 2: {pg("key_a")}. Days 5 and 6: {pg("key_b")}. Days 3, 4, 7 and 8: this page. Early finishers have no key; praise effort and ideas.</p>'
             f'<div class="part">Marking tips for a sub</div>'
             f'<ul style="font-size:12pt;line-height:1.5;margin:0;padding-left:15pt"><li>Accept any reasonable answer on drawing and writing tasks.</li>'
             f'<li>Count a chant correct when it has exactly four beat boxes with one word (or shh) in each.</li>'
             f'<li>If a student is stuck, read the instruction aloud and show the example on the sheet.</li>'
             f'<li>Leave the marked sheets for the teacher; do not give grades.</li></ul>')
    return keypage("Answer keys · Days 3, 4, 7 and 8", "Days 3, 4, 7 and 8", inner, n, watermark)


# ---------------------------------------------------------------- teacher notes, terms, thanks
MONTH_NOTE = ("February is a short month with a lot to remember. Every February the United States observes Black History Month, which grew from Negro History Week, "
              "started by historian Carter G. Woodson in February 1926. This bundle shares short facts about five musicians: Scott Joplin, Duke Ellington, Ella Fitzgerald, "
              "Louis Armstrong and Florence Price. February also brings Valentine’s Day on February 14, which the bundle uses to talk about the heartbeat as a steady beat; "
              "Lunar New Year, a celebration based on the Moon’s calendar that falls between January 21 and February 20, with the drums, cymbals and gong of the lion dance; "
              "and Groundhog Day on February 2. The music stays simple: clapping, patting and saying words. Nothing asks a student to take part in a religious practice.")


def teacher_page(n):
    trs = "".join(f"<tr><td><b>{a}</b></td><td style='white-space:nowrap'>{prange(f, l)}</td><td>{u}</td></tr>" for a, f, l, u in PARTS)
    return (f'<section class="page doc tn"><div class="rule"><h1>Teacher Notes</h1>'
            f'<div class="l" style="font-size:13pt">February Music Sub Plans K–5 · 8 no-prep, no-tech days · Black History Month musicians, Valentine’s Day, Lunar New Year</div></div>'
            f'<div class="cols"><div>'
            f'<h2>Why February matters</h2><p>{MONTH_NOTE}</p>'
            f'<h2>What it is</h2>'
            f'<p>Eight complete music lessons a substitute can teach with no tech, no instruments and no music background. Each day has a step-by-step plan with words to say and '
            f'timed steps, and two worksheets: one for grades K–2 and one for grades 3–5.</p>'
            f'<h2>The eight days</h2><ol>'
            + "".join(f"<li><b>{escape(d['title'])}</b>: {(d['skill'] if d['skill'].startswith('February') else d['skill'][0].lower() + d['skill'][1:])}.</li>" for d in DAYS) +
            f'</ol><p>Use them in any order. The welcome sheet has a “Day #” column so the sub knows which day each class gets next.</p>'
            f'<h2>Set up the sub tub (about 15 minutes, once)</h2><ol>'
            f'<li>Fill in the welcome sheet (page {IX["welcome"]}).</li>'
            f'<li>Print the plans, the quick start, the word-rhythm chart, the facts page and the sub report; copy each worksheet for your largest class.</li>'
            f'<li>Cut out the folder labels (page {IX["labels"]}), put each day in its own folder, and add the answer keys.</li></ol>'
            f'</div><div>'
            f'<h2>What’s inside</h2><table class="t"><tr><th>Part</th><th>Pages</th><th>Use</th></tr>{trs}</table>'
            f'<h2>Why subs can teach it</h2>'
            f'<p>Rhythm work is speech rhythm: clap the syllables of words, with the claps printed as dots. Nobody has to read music or make music with an instrument. Games use only voices, hands and a pencil.</p>'
            f'<h2>Standards</h2><p>Supports relating music to varied contexts (MU:Cn11.0) and generating musical ideas (MU:Cr1.1), National Core Arts Standards, Music, grades K–5.</p>'
            f'<h2>Good to know</h2><ul><li>Prints well in black and white.</li>'
            f'<li>The facts used in the bundle are on page {IX["facts"]}.</li></ul>'
            f'<p class="small">All lessons, chants, games, words and art are original. No lyrics or copyrighted characters are used.</p>'
            f'</div></div><div style="flex:1"></div>{foot(f"Page {n}")}</section>')


def terms_page(n):
    return (f'<section class="page doc"><div class="rule"><h1>Terms of Use</h1>'
            f'<div class="l" style="font-size:13pt">Thank you for your purchase!</div></div>'
            f'<p>© {YEAR} {STORE}. {BRAND} by {STORE}. All rights reserved. This purchase gives <b>one teacher</b> a license to use this resource with their own students.</p>'
            f'<h2>You may</h2><ul><li>Print and copy pages for your own classroom and students, year after year.</li>'
            f'<li>Share pages with your own students through a password-protected class site or learning platform.</li>'
            f'<li>Leave the pages for a substitute teacher who teaches your own students.</li></ul>'
            f'<h2>You may not</h2><ul><li>Share, email or copy this resource for other teachers, a whole school or a district. '
            f'Additional licenses are available on Teachers Pay Teachers.</li>'
            f'<li>Post any part of it publicly, or on a shared drive or social media.</li>'
            f'<li>Sell, give away or claim any part of it as your own, or edit it into a new product.</li></ul>'
            f'<h2>Questions?</h2><p>Please use the Q&amp;A tab on the {BRAND} by {STORE} store on Teachers Pay Teachers. '
            f'If something looks wrong, let me know there and I will fix it.</p>'
            f'<h2>Credits</h2><ul>'
            f'<li>Lessons, chants, games, drawings and layouts: original work, {BRAND} by {STORE}. The heart-drum scene on the cover is original {BRAND} art.</li>'
            f'<li>Facts about February, the musicians and the holidays are drawn from the sources listed in the seller’s notes for this product and are kept short and general.</li>'
            f'<li>Text fonts: Oswald (The Oswald Project Authors) and Source Sans 3 (Adobe), SIL Open Font License 1.1.</li></ul>'
            f'<p class="small">{DISCLOSURE}</p>'
            f'<div style="flex:1"></div>{foot(f"Page {n}")}</section>')


def thanks_page(n):
    return (f'<section class="page doc"><div style="flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center">'
            f'<div style="display:flex;gap:26pt;margin-bottom:18pt">{pic("heart", 70)}{pic("drum", 70)}{pic("lantern", 70)}</div>'
            f'<div class="h" style="font-size:44pt;line-height:1.05">Thank you!</div>'
            f'<div class="l" style="font-size:18pt;margin-top:10pt">Please rate this resource</div>'
            f'<p style="font-size:13pt;max-width:4.8in;margin-top:14pt;line-height:1.45">You earn TpT credits for leaving feedback, and your rating helps other teachers find this resource. '
            f'Follow the {BRAND} store on Teachers Pay Teachers for new music resources every week. This is one of the monthly music sub plan bundles: '
            f'look for the Year-Long Music Sub Plans Bundle (all 12 months, 96 days).</p>'
            f'<div class="h" style="font-size:16pt;margin-top:14pt;color:{ACCENT}">{BRAND} by {STORE}</div></div>{foot(f"Page {n}")}</section>')


# ---------------------------------------------------------------- cover (PDF page 1)
def hero_img(height_css):
    return f'<img src="../art/hero.png" alt="" style="display:block;height:{height_css};width:auto">'


def cover_page():
    return (f'<section class="page cover"><div class="store">{BRAND}</div>'
            f'<div style="display:flex;align-items:center;gap:0.3in">'
            f'<div style="display:flex;flex-direction:column;gap:9pt">'
            + "".join(f'<div style="background:#000;color:#fff;font-family:Oswald;font-weight:700;font-size:15pt;letter-spacing:.06em;padding:4pt 12pt 5pt;border-radius:4pt;text-align:center">{t}</div>'
                      for t in ("NO PREP", "NO TECH", "8 DAYS")) +
            f'</div>{hero_img("4.6in")}</div>'
            f'<div class="ctitle"><div class="a">FEBRUARY</div><div class="b">MUSIC SUB PLANS K–5</div>'
            f'<div class="c">Black History Month musicians · Valentine’s Day · Lunar New Year · K–2 and 3–5 sheets</div></div>'
            f'<div class="cband">Grades K–5 <em>·</em> 8 days <em>·</em> 16 worksheets <em>·</em> {TOTAL} pages</div></section>')


# ---------------------------------------------------------------- assemble
RENDER = {
    "cover": lambda n, w: cover_page(), "teacher": lambda n, w: teacher_page(n), "welcome": welcome_page, "quick": quick_page, "glance": glance_page,
    "games": games_page, "chart": chart_page, "facts": facts_page, "sign": sign_page,
    "d1_k2": d1_k2, "d1_35": d1_35, "d2_k2": d2_k2, "d2_35": d2_35, "d3_k2": d3_k2, "d3_35": d3_35,
    "d4_k2": d4_k2, "d4_35": d4_35, "d4_cards": d4_cards, "d5_k2": d5_k2, "d5_35": d5_35, "d6_k2": d6_k2, "d6_35": d6_35,
    "d7_k2": d7_k2, "d7_35": d7_35, "d7_cards": d7_cards, "d7_book": d7_book, "d8_k2": d8_k2, "d8_35": d8_35, "d8_quiz": d8_quiz,
    "early1": early1, "early2": early2, "exit": exit_page, "key_a": key_a_page, "key_b": key_b_page, "key_c": key_c_page,
    "report": report_page, "labels": labels_page, "cert": cert_page, "terms": lambda n, w: terms_page(n), "thanks": lambda n, w: thanks_page(n),
}


def render_page(key, watermark=False):
    n = IX[key]
    m = re.match(r"d(\d)_plan$", key)
    if m:
        return plan_page(DAYS[int(m.group(1)) - 1], n, watermark)
    return RENDER[key](n, watermark)


PREVIEW_PICKS = ["d2_plan", "d2_k2", "d2_35", "key_a"]


def preview_pages():
    return [render_page(p, watermark=True) for p in PREVIEW_PICKS]


# ---------------------------------------------------------------- square images (2000 x 2000)
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
.swm { position: absolute; left: 50%; top: 50%; transform: translate(-50%,-50%) rotate(-38deg); font-family: 'Oswald'; font-weight: 700;
       color: rgba(0,0,0,.14); white-space: nowrap; letter-spacing: .06em; }
.rib { position: absolute; font-family: 'Oswald'; font-weight: 700; color: #fff; text-align: center; border-radius: 6px; letter-spacing: .05em; }
.card { position: absolute; border: 2px solid #000; box-shadow: 8px 8px 0 #000; background: #fff; text-align: center; }
.card b { display: block; font-family: 'Oswald'; font-weight: 700; color: ACCENT; line-height: 1; }
.card span { display: block; font-family: 'Oswald'; font-weight: 500; text-transform: uppercase; letter-spacing: .06em; }
.num { position: absolute; width: 56px; height: 56px; border-radius: 50%; background: ACCENT; color: #fff; font-family: 'Oswald'; font-weight: 700; font-size: 34px; text-align: center; line-height: 56px; }
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


def shot(src, left, top, width, wmsize=90, wm_on=True, cls="shot"):
    h = width * 11 / 8.5
    return (f'<div class="{cls}" style="left:{left}px;top:{top}px;width:{width}px;height:{h:.0f}px"><img src="{src}">'
            f'{f"<div class=swm style=font-size:{wmsize}px>PREVIEW</div>" if False else ""}</div>')


def cover_square():
    rib = "".join(f'<div class="rib" style="left:36px;top:{y}px;width:172px;height:60px;line-height:62px;font-size:38px;background:{c}">{t}</div>'
                  for t, y, c in (("NO PREP", 200, ACCENT), ("NO TECH", 274, ACCENT), ("8 DAYS", 348, "#000")))
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div>'
        f'<img class="cv-hero" src="../art/hero.png" style="position:absolute;left:210px;top:62px;height:578px;width:578px">'
        f'{rib}'
        f'<div class="shot cv-mock" style="left:762px;top:372px;width:190px;height:246px;transform:rotate(5deg);box-shadow:4px 4px 0 #000">'
        f'<img src="mock.png" style="width:100%;height:100%;object-fit:fill"></div>'
        f'<div class="cv-block" style="position:absolute;left:0;right:0;top:652px;height:210px;background:{ACCENT};text-align:center;color:#fff">'
        f'<div class="hd" style="position:static;font-size:136px;line-height:1;padding-top:4px;letter-spacing:.02em">February</div>'
        f'<div class="hd" style="position:static;font-size:54px;margin-top:0">Music Sub Plans K–5</div></div>'
        f'<div class="cv-series" style="position:absolute;left:0;right:0;top:862px;height:74px;background:#fff;border-top:3px solid #000;text-align:center;'
        f'font-family:Oswald;font-weight:700;font-size:34px;letter-spacing:.22em;line-height:70px">MONTHLY MUSIC SUB PLANS</div>'
        f'<div class="band">Grades K–5 <em>·</em> 8 days <em>·</em> 16 worksheets <em>·</em> {TOTAL} pages</div></div>')


def preview_square_1():
    cards = "".join(f'<div class="card" style="left:650px;top:{y}px;width:300px;height:150px;padding-top:16px"><b style="font-size:76px">{a}</b>'
                    f'<span style="font-size:24px;margin-top:6px">{b}</span></div>'
                    for a, b, y in (("8", "days, any order", 232), ("30–45", "minutes each day", 412), ("16", "student sheets", 592)))
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div>{hd("Any sub can teach it", 74, 78)}'
        f'{sub("Timed steps and words to say on every plan page", 27, 160)}'
        f'{shot("s_d2_plan.png", 80, 222, 520)}{cards}'
        f'<div class="lbl" style="left:650px;top:784px;width:300px;font-size:20px">No music skills needed</div>'
        f'<div class="band">No prep <em>·</em> No tech <em>·</em> Words to say <em>·</em> K–2 and 3–5</div></div>')


def preview_square_2():
    cols = [("1", "Pick a day", "s_glance.png", "Any day, any order"), ("2", "Follow the plan", "s_d1_plan.png", "Read the words in italics"),
            ("3", "Hand out the sheet", "s_d1_k2.png", "K–2 or 3–5, your choice")]
    out = ""
    for i, (nn, h1, src, cap) in enumerate(cols):
        x = 62 + i * 300
        out += (f'<div class="num" style="left:{x}px;top:196px">{nn}</div>'
                f'<div class="lbl" style="left:{x + 66}px;top:200px;width:204px;text-align:left;font-size:25px;line-height:1.05">{h1}</div>'
                f'{shot(src, x, 276, 266)}'
                f'<div class="lbl" style="left:{x}px;top:652px;width:266px;font-weight:300;text-transform:none;font-size:21px">{cap}</div>')
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div>{hd("How it works", 74, 78)}{sub("Three steps for any substitute", 27, 160)}{out}'
        f'<div style="position:absolute;left:62px;right:62px;top:742px;height:120px;border:2px solid #000;box-shadow:8px 8px 0 #000;text-align:center;'
        f'font-family:Oswald;font-weight:700;font-size:38px;line-height:1.15;text-transform:uppercase;padding-top:16px">That is all.<br>'
        f'<span style="color:{ACCENT}">No tech · no prep · no music skills</span></div>'
        f'<div class="band">8 days <em>·</em> 16 worksheets <em>·</em> answer keys <em>·</em> sub report</div></div>')


SHOTS3 = [("welcome", "Welcome sheet"), ("quick", "Quick start"), ("chart", "Rhythm chart"), ("d4_cards", "Move cards"),
          ("d5_35", "Word search"), ("d7_book", "Chant book"), ("key_b", "Answer keys"), ("report", "Sub report")]
SHOT_KEYS = ["d2_plan", "glance", "d1_plan", "d1_k2"] + [k for k, _ in SHOTS3]


def preview_square_3():
    cells = ""
    for i, (k, lab) in enumerate(SHOTS3):
        x = 70 + (i % 4) * 224
        y = 232 + (i // 4) * 332
        cells += shot(f"s_{k}.png", x, y, 196) + f'<div class="lbl" style="left:{x}px;top:{y + 255 + 14}px;width:196px;font-size:17px">{lab}</div>'
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div>{hd("Everything inside", 70, 78)}'
        f'{sub("Welcome sheet, 8 plans, 16 worksheets, cards, keys and a sub report", 27, 156)}{cells}'
        f'<div class="band">{TOTAL} pages <em>·</em> US Letter PDF <em>·</em> prints in black &amp; white</div></div>')


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
    subprocess.run(["node", RENDER_JS, path], check=True, env=node_env(), stdout=subprocess.DEVNULL)


def write(name, txt):
    p = os.path.join(BUILD, name)
    with open(p, "w") as f:
        f.write(txt)
    return p


def pdf_png(src, page_no, out, res=110):
    subprocess.run(["pdftoppm", "-png", "-r", str(res), "-f", str(page_no), "-l", str(page_no), "-singlefile", src,
                    os.path.join(BUILD, out)], check=True)


def tpt_json(pages):
    return {
        "price": PRICE, "license_price": PRICE, "tax_code": "Other Digital Goods - No Physical Media",
        "grades": GRADES, "subjects": ["Music"], "tags": TAGS, "formats": ["PDF"], "pages": pages, "answer_key": "Included",
        "files": {"product": f"{SLUG}.pdf", "preview": f"{SLUG}-PREVIEW.pdf", "thumb1": "cover.png",
                  "thumb2": "preview-1.png", "thumb3": "preview-2.png", "thumb4": "preview-3.png"},
    }


# ---------------------------------------------------------------- UPLOAD.md and SOURCES.md (generated so counts always agree)
def section_counts():
    out = []
    for label, a, b, use in PARTS:
        out.append((label, IX[b] - IX[a] + 1))
    return out


def upload_md():
    sc = section_counts()
    assert sum(c for _, c in sc) == TOTAL
    pagelist = "\n".join(f"- {l}: {c}" for l, c in sc)
    days = "\n".join(f"• Day {d['n']}, {d['title']}: {x}" for d, x in zip(DAYS, [
        "K–2 hear a short reading about five Black musicians and circle answers; 3–5 read a passage of about 200 words and answer five questions",
        "clap the syllables of musicians’ names and February words; K–2 color a circle for each clap, 3–5 sort words by syllables and build a four-beat chant",
        "design a heart drum; K–2 draw it, name it and finish two sentence starters, 3–5 label three parts and write two sentences",
        "move to a tapped beat and freeze, with 8 picture cards; K–2 circle how they moved, 3–5 reflect and design a freeze game",
        "February word puzzles; K–2 match words to pictures and trace, 3–5 word search plus a decode-the-message puzzle",
        "five music jobs, from composer to piano tuner; K–2 draw a job, 3–5 match jobs and write a job ad or interview questions",
        "build four-beat chants from heart, drum and lantern word cards, mark the syllables, share with a partner, and keep a chant book page",
        "bingo (12 squares for K–2, 16 for 3–5), a read-aloud quiz and Pass the Pencil, with a reflection"]))
    desc = f"""Need sub plans a substitute can teach without any music background, any technology, or any prep from you? These eight February music days are ready to print and hand over. Each day has a step-by-step plan with timed steps and words to say, plus two student sheets: one for grades K–2 and one for grades 3–5. The theme is February: short, respectful facts about five Black musicians for Black History Month (Scott Joplin, Duke Ellington, Ella Fitzgerald, Louis Armstrong and Florence Price), the heartbeat as a steady beat for Valentine's Day, the drums, cymbals and gong of the Lunar New Year lion dance, and a little Groundhog Day fun.

WHAT'S INCLUDED ({TOTAL} pages, PDF, US Letter)
• Cover and teacher notes with the February note, setup steps and a page guide (2 pages)
• Sub quick start, welcome sheet, days at a glance, quick games, word-rhythm chart, February facts and a class sign (7 pages)
• 8 sub plans, one per day, each 30–45 minutes (8 pages)
• 16 student sheets: a K–2 and a 3–5 sheet for each day (16 pages)
• Day extras: movement picture cards, chant word cards, a chant book page and a read-aloud quiz (4 pages)
• Early finishers (2 pages)
• Exit tickets (1 page)
• Answer keys for Days 1, 2, 5, 6, 7 and 8 (3 pages)
• Sub report form, folder labels, class star awards, terms of use and a thank-you page (5 pages)

THE EIGHT DAYS
{days}

WHY IT WORKS FOR SUBS
• No tech: nothing needs a computer, projector, speaker or video. Paper, pencils, crayons, hands and voices only
• No music skills: rhythm is taught through speech rhythm, clapping the syllables of words, with the claps printed as dots. The sub never reads music or sings
• No prep: print, put each day in a folder, and go. Each day works in any order for a mixed K–5 class
• Facts are short, sourced and secular, so the days work in public schools and for students of every background

Part of the Monthly Music Sub Plans series: save with the Year-Long Music Sub Plans Bundle (all 12 months, 96 days).
Please leave a rating: you earn TpT credits for feedback, and it helps other teachers find this.
Follow the Hudson Beat store for new music resources every week.

{DISCLOSURE}"""
    return f"""# UPLOAD: February Music Sub Plans K–5, Black History Month Musicians (TpT 077)

These fields follow the order of TpT's "Add a resource" form. `tools/tpt.js publish` reads the title and description from the code blocks under 1 and 2, and everything else from `tpt.json`.

**Files to attach**
- Resource (digital download): `{SLUG}.pdf`, {TOTAL} pages, US Letter portrait.
- Thumbnails, in this order: `cover.png`, `preview-1.png`, `preview-2.png`, `preview-3.png` (all 2000 × 2000).
- Preview file: `{SLUG}-PREVIEW.pdf`, 4 watermarked pages.

## 1. Title

```
{LISTING_TITLE}
```
({len(LISTING_TITLE)} characters; the limit is 80.)

## 2. Description

```
{desc}
```

## 3. Grades

Kindergarten, 2nd, 3rd, 5th (`kindergarten`, `2nd-grade`, `3rd-grade`, `5th-grade` in tpt.json): both ends of K–5 and the K–2 / 3–5 split, as on item 007.

## 4. Subjects and tags

- Subject: Music
- Tags: {", ".join(TAGS)}

## 5. Page count by section

{pagelist}
- Total: {TOTAL}

## 6. Price

**${PRICE}** (owner, 23 Nov 2026); multiple-license price ${PRICE}. The Year-Long Bundle is $149.

## 7. Preview

Paid. Preview PDF (4 pages, watermarked "PREVIEW"): the Day 2 sub plan, its K–2 sheet, its 3–5 sheet, and the Day 1 and 2 answer key.

## 8. Before you click publish

- [ ] Cover and previews show "HUDSON BEAT" in type; footers read "© 2026 Brian Lotze · Hudson Beat · For single-classroom use".
- [ ] Run `node tools/tpt.js publish tpt/077-february-music-sub-plans-k5 --dry-run` first to confirm the tags, the "Included" answer-key option and the tax code.
- [ ] List by **15 Jan 2027**.
"""


FACTS = [  # (fact, source)
    ("Black History Month is observed in the United States every February; it grew from Negro History Week, which historian Carter G. Woodson started in February 1926; in 1976 President Gerald Ford asked Americans to honor it (Day 1, facts page, teacher notes, bingo clue February)",
     "https://www.nationalgeographic.com/history/article/courageous-historian-fought-make-black-history-month, https://www.britannica.com/biography/Carter-G-Woodson and https://news.uchicago.edu/story/century-black-history-month (web search 24 Nov 2026: Woodson launched Negro History Week in February 1926 through the Association for the Study of Negro Life and History; the observance grew into Black History Month, and 1976 is the year President Ford called on Americans to recognize it; sources differ on who made the formal change, so the product says only that Ford asked Americans to honor it)."),
    ("Scott Joplin: composer and pianist, called the King of Ragtime; born about 1868 (sources differ; the product says \"about 1868\"), died April 1, 1917; Maple Leaf Rag published in 1899 (Day 1, Day 6, facts page, bingo clues Ragtime and Piano). Maple Leaf Rag is public domain (published 1899); no music from it is reproduced, played or needed.",
     "https://en.wikipedia.org/wiki/Scott_Joplin (fetched 24 Nov 2026: born November 24, 1868 per early biographers but later research suggests 1867-68, birthplace disputed; died April 1, 1917, New York City; known as the King of Ragtime; Maple Leaf Rag published 1899 by John Stillwell Stark); https://www.britannica.com/biography/Scott-Joplin (web search 24 Nov 2026: born 1867/68, died April 1, 1917; composer and pianist known as the king of ragtime); https://www.kennedy-center.org/education/resources-for-educators/classroom-resources/media-and-interactives/artists/joplin-scott/ (Maple Leaf Rag published in 1899)."),
    ("Duke Ellington: born April 29, 1899, Washington, D.C.; died May 24, 1974; pianist, composer and bandleader; led his own orchestra from 1924 until his death, about fifty years (Day 1, Day 6, facts page, bingo clue Ellington)",
     "https://en.wikipedia.org/wiki/Duke_Ellington (fetched 24 Nov 2026: Edward Kennedy \"Duke\" Ellington, born April 29, 1899, Washington, D.C.; died May 24, 1974, New York City; pianist, composer, songwriter, bandleader, arranger; led his own orchestra from 1924 until his death, about 50 years)."),
    ("Ella Fitzgerald: jazz singer, April 25, 1917 - June 15, 1996; known for scat (using the voice like an instrument); nicknamed Lady Ella on the facts page (Day 1, facts page, bingo clue Jazz)",
     "https://en.wikipedia.org/wiki/Ella_Fitzgerald (fetched 24 Nov 2026: born April 25, 1917, died June 15, 1996; nicknames include Lady Ella; noted for scat singing, a vocal improvisation style with a horn-like quality); https://www.britannica.com/biography/Ella-Fitzgerald and https://kids.britannica.com/students/article/Ella-Fitzgerald/311263 (web search 24 Nov 2026: died June 15, 1996; scat uses the voice as an instrument with improvised nonsense syllables). Birthplace and Grammy counts are not printed because sources give differing numbers."),
    ("Louis Armstrong: jazz trumpeter and singer, born in New Orleans, Louisiana, in 1901 (he often claimed 1900; records point to 1901), died July 6, 1971; nickname Satchmo; one of the most influential artists in jazz history (Day 1, Day 8 bingo clues Trumpet, Armstrong, Jazz)",
     "https://en.wikipedia.org/wiki/Louis_Armstrong (fetched 24 Nov 2026: birth believed August 4, 1901, Armstrong claimed July 4, 1900; died July 6, 1971; New Orleans; trumpet and cornet; nickname Satchmo); https://www.britannica.com/summary/Louis-Armstrong (web search 24 Nov 2026: born August 4, 1901, New Orleans; died July 6, 1971, New York; jazz trumpeter and singer; leading trumpeter and one of the most influential artists in jazz history; baptismal record points to 1901)."),
    ("Florence Price: composer, pianist and organist; born in Little Rock, Arkansas, in 1887 (a few sources say 1888), died June 3, 1953, Chicago; her Symphony No. 1 in E minor was performed by the Chicago Symphony Orchestra, conducted by Frederick Stock, in 1933; known as the first African American woman to have a symphony performed by a major U.S. orchestra (Day 1, Day 6, facts page, bingo clue Symphony). The product uses the narrower wording \"a symphony performed by a major U.S. orchestra\" because some sources phrase the milestone more broadly.",
     "https://en.wikipedia.org/wiki/Florence_Price (fetched 24 Nov 2026: born April 9, 1887 or 1888, Little Rock; died June 3, 1953, Chicago; pianist and organist; Symphony No. 1 performed by the Chicago Symphony Orchestra under Frederick Stock in 1933; first African-American woman to have her music played by a major U.S. orchestra); https://www.britannica.com/biography/Florence-Price (web search 24 Nov 2026: first African American woman composer to have a symphony performed by a major American orchestra); https://www.classical-music.com/features/composers/how-florence-prices-1933-chicago-performance-made-history (June 15, 1933, Chicago World's Fair; the exact day is not printed)."),
    ("Valentine's Day is February 14 (a day when many people share cards and kind words; secular framing only). A heart keeps a steady beat that speeds up with activity and slows at rest (Day 3, Day 4, decode message, bingo clue Heart). No heart-rate numbers are printed.",
     "General knowledge for the date; heart rate rises with activity and settles at rest per https://health.clevelandclinic.org/pediatric-vital-signs/ and https://www.childrens.com/health-wellness/is-your-childs-heart-rate-healthy (web search 24 Nov 2026)."),
    ("Lunar New Year: a celebration based on the lunar calendar; begins with the first new moon of the lunar calendar, between January 21 and February 20, so the date changes every year; celebrated by many families in China, other Asian countries and communities around the world; red lanterns are a common decoration; the lion dance uses drums, cymbals and a gong and is believed to bring good luck (Day 3, Day 4, Day 5, facts page, bingo clues Lantern, Gong, Cymbal, Drum)",
     "https://www.britannica.com/topic/Lunar-New-Year and https://brandeis.edu/spiritual-life/resources/guide-to-observances/lunar-new-year.html (web search 24 Nov 2026: between January 21 and February 20; time and date gives a slightly wider window, so the product prints \"between January 21 and February 20\"); https://hub.yamaha.com/pianos/p-history/celebrating-lunar-new-year-around-the-world/ (drums, gongs and cymbals played loudly in lion dances to keep away bad luck); https://junior.scholastic.com/issues/2021-22/020122/time-to-celebrate.html (the lion dance is believed to bring good luck); https://www.nationalgeographic.com/travel/article/celebrate-chinese-new-year (red lanterns a staple decoration). The product does not claim any one origin or call the holiday only Chinese."),
    ("Groundhog Day is February 2; the best-known celebration is in Punxsutawney, Pennsylvania, with official celebrations dating to 1887 (facts page, bingo clue Shadow)",
     "https://www.history.com/this-day-in-history/february-2/first-groundhog-day and https://www.hagley.org/research/news/hagley-vault/first-observance-groundhog-day-punxsatawney-pennsylvania (web search 24 Nov 2026: first official Groundhog Day on February 2, 1887, at Gobbler's Knob near Punxsutawney; some sources mention 1886 for earlier notices, so the product says \"dating back to 1887\" on the facts page only and treats it as a tradition, not science)."),
    ("Presidents' Day is the common name of the federal holiday officially called Washington's Birthday, on the third Monday of February (always February 15 to 21) (facts page)",
     "https://www.opm.gov/frequently-asked-questions/pay-and-leave-faq/leave-policy/what-is-the-official-name-for-the-holiday-on-the-third-monday-in-february/ (web search 24 Nov 2026: official name Washington's Birthday under 5 U.S.C. 6103; third Monday in February since the Uniform Monday Holiday Act of 1968); https://www.govinfo.gov/features/presidents-day."),
    ("Composer: writes and arranges original music. Conductor (music director): leads orchestras and other musical groups and makes sure the musicians have one coherent sound (Day 6, bingo clue Orchestra)",
     "https://www.bls.gov/ooh/entertainment-and-sports/music-directors-and-composers.htm (fetched 24 Nov 2026: composers write and arrange original music; music directors lead orchestras and other musical groups during performances and recording sessions, and ensure that musicians have one coherent sound)."),
    ("Piano tuner: adjusts the tension of a piano's strings so the instrument sounds in tune (Day 6)",
     "https://en.wikipedia.org/wiki/Piano_tuning (fetched 24 Nov 2026: adjusting a piano's pitch accuracy, mainly by changing string tension with the tuning pins)."),
    ("Radio host broadcasts music, news and weather, interviews guests, often specializes in one kind of music (Day 6)",
     "https://www.bls.gov/ooh/media-and-communication/announcers.htm (fetched 23 Nov 2026 for tpt/073: announcers and hosts deliver news, sports, traffic and weather and may interview guests; radio DJs usually focus on one music genre)"),
    ("Music teacher helps students learn about music; most music jobs need listening and teamwork",
     "General statements with no dates, names or numbers; no external source needed."),
    ("Drum: an instrument you tap; cymbal: round metal plates crashed together; gong: a large metal disc that is struck; trumpet: a brass instrument; piano: the instrument with black and white keys; orchestra: a large group of musicians; beat = steady pulse; syllable = one part of a word; chant = words said in rhythm; ragtime = lively piano music; symphony = a long piece for an orchestra; jazz = the music style of Armstrong, Ellington and Fitzgerald",
     "Basic music-class vocabulary, no external source needed."),
    ("Teacher page standards: MU:Cn11.0 (Connecting, Anchor Standard 11: relate musical ideas and works to varied contexts and daily life) and MU:Cr1.1 (Creating, Imagine: generate musical ideas)",
     "https://www.nationalartsstandards.org/node/376 (Connect #11 wording, fetched 23 Nov 2026 for tpt/073) and https://www.commonplanner.com/standards/national-core-arts-standards-4f837f24/music/grade-2-b4babb68 (Cr1.1.2a, Cn11.0.2a)"),
    ("Counts quoted on the pages (12 squares and 12 clues on the K-2 board, 16 on the 3-5 board; 1899; 1933; 1926; 1887) match the data",
     "Checked by gen.py --check against the same data that prints the pages and the answer keys."),
]


def sources_md():
    rows = "\n".join(f"### {i + 1}. {f}\nSource: {s}\n" for i, (f, s) in enumerate(FACTS))
    return f"""# SOURCES: 077 February Music Sub Plans K-5

Every date, name and fact printed in the product, with where it was checked (WebFetch or WebSearch, 24 Nov 2026, unless a line says otherwise). Pages {IX['d1_plan']}-{IX['d1_35']} are Day 1 (the reading), pages {IX['d6_plan']}-{IX['d6_35']} are Day 6 (jobs),
page {IX['facts']} is the February facts page, page {IX['d8_quiz']} is the bingo clue list. Wording is kept to the basics the sources agree on, in our own words.
No lyrics, recordings, speeches or sheet music are used and none is needed: the sub never plays or sings anything. The only named piece is Joplin's Maple Leaf Rag (published 1899, public domain), named as a fact and never reproduced. No copyrighted characters.

Where sources disagree (Joplin's birth date, Price's birth year, Armstrong's birth year, the Lunar New Year window, the start of Groundhog Day) the product prints the safer wording described in the item.

{rows}
## Names on the pages
- Scott Joplin, Duke Ellington, Ella Fitzgerald, Louis Armstrong, Florence Price (items 2 to 6); Carter G. Woodson and President Gerald Ford (item 1); Frederick Stock is not named in the product.
- Dates: February 14, February 2, January 21 to February 20, the third Monday of February, 1926, 1976, 1899, 1924, 1974, 1933, 1887, 1917, 1996, 1901, 1971, 1953.
- Places: Washington, D.C.; New Orleans, Louisiana; Little Rock, Arkansas; Chicago; Punxsutawney, Pennsylvania.

## Rules followed
Respectful, secular and inclusive wording; short facts only; no speech quotes, no lyrics and no named songs; nothing asks a student to take part in a religious practice; no stereotypes; no technology, singing, playing or music reading by the sub.
"""


# ---------------------------------------------------------------- build
def build():
    os.makedirs(BUILD, exist_ok=True)
    problems = verify_data()
    if problems:
        print("\n".join(problems))
        sys.exit("data check failed; not rendering")
    full = write("resource.html", html_doc([render_page(p) for p in PLAN], TITLE))
    prev = write("preview.html", html_doc(preview_pages(), "Preview"))
    shots = write("shots.html", html_doc([render_page(k, True) for k in SHOT_KEYS], "Shots"))
    render([{"html": full, "pdf": PDF}, {"html": prev, "pdf": PREVIEW_PDF}, {"html": shots, "pdf": os.path.join(BUILD, "shots.pdf")}])
    spdf = os.path.join(BUILD, "shots.pdf")
    for i, k in enumerate(SHOT_KEYS):
        pdf_png(spdf, i + 1, f"s_{k}", 110)
    pdf_png(PREVIEW_PDF, 1, "mock", 110)
    sq = [write("cover.html", cover_square()), write("p1.html", preview_square_1()), write("p2.html", preview_square_2()),
          write("p3.html", preview_square_3())]
    render([{"html": h, "png": o, "width": 1000, "height": 1000, "scale": 2} for h, o in zip(sq, [COVER_PNG] + PREVIEW_PNGS)])
    with open(TPT_JSON, "w") as f:
        json.dump(tpt_json(TOTAL), f, indent=2, ensure_ascii=False)
        f.write("\n")
    with open(UPLOAD, "w") as f:
        f.write(upload_md())
    with open(SOURCES, "w") as f:
        f.write(sources_md())
    print(f"built {PDF} ({TOTAL} pages), {PREVIEW_PDF}, cover + 3 previews, tpt.json, UPLOAD.md, SOURCES.md")


# ---------------------------------------------------------------- checks
DEVICE_RE = re.compile(
    r"\b(computers?|laptops?|tablets?|chromebooks?|ipads?|projectors?|smart ?boards?|speakers?|recordings?|recorded|videos?|youtube|spotify|qr|"
    r"websites?|web ?sites?|internet|online|apps?|sing|sings|singing|sang|sung|songs?|play|plays|played|playing|"
    r"notation|staff|clef|treble|bass|sheet music|quarter notes?|eighth notes?|half notes?|whole notes?|sharps?|flats?|solfege|"
    r"key signature|time signature|pitch|pitches|melody|chords?)\b", re.I)


ALLOWED_MUSIC_FACT = re.compile(r"songs and singing", re.I)       # the one sourced music connection (SOURCES.md item 5)


def verify_data():
    errs = []
    # crayon lists, bingo boards and the plans' wording agree
    if not CRAYON_DAYS or "crayons" in " ".join(d["materials"] for d in DAYS if d["n"] not in CRAYON_DAYS + CRAYON_OPT):
        errs.append("crayon day lists do not match the materials")
    if BINGO_K2 != 12 or BINGO_K2 % BINGO_K2_COLS or len(BANK_ORDER_K2) != BINGO_K2 or BINGO_35 != 16 or len(BANK_ORDER_35) != BINGO_35:
        errs.append("bingo boards: squares must equal the word bank sizes (12 for K-2, 16 for 3-5)")
    if len(BINGO) != BINGO_35:
        errs.append("bingo clue count differs from the 3-5 board")
    # 1. syllable table: the hyphenated data must agree with an independently typed expected count
    for key, w in WORDS.items():
        if key not in EXPECT:
            errs.append(f"word '{w}' has no expected syllable count")
        elif key != "shh" and len(w.split("-")) != EXPECT[key]:
            errs.append(f"word '{w}': hyphenated into {len(w.split('-'))} syllables, expected {EXPECT[key]}")
    for lst, label, lo, hi in ((D2_K2_A, "Day 2 K-2 A", 1, 3), (D2_K2_B, "Day 2 K-2 B", 1, 3), (D2_35_A, "Day 2 3-5 A", 1, 3), (D2_35_B, "Day 2 3-5 B", 1, 3)):
        for w in lst:
            if w.lower().replace("-", "") not in WORDS or not lo <= nsyl(w) <= hi:
                errs.append(f"{label}: '{w}' unknown or out of range")
    if sorted(set(nsyl(w) for w in D2_K2_A)) != [1, 2, 3] or sorted(set(nsyl(w) for w in D2_K2_B)) != [1, 2, 3]:
        errs.append("Day 2 K-2 should show 1, 2 and 3 claps in both parts")
    if any(len(v) < 2 for v in D2_35_SORT.values()):
        errs.append("Day 2 3-5 part B: each box needs at least 2 words")
    for w in D2_35_BANK + D2_35_EX + D7_CARDS:
        if beat_kind(w) not in "qer":
            errs.append(f"chant word '{w}' is not 1 or 2 syllables")
    if len(D2_35_EX) != 4 or len(CHART) != 8 or any(len(l) != 4 for l in CHART):
        errs.append("a chant must be 4 beats (one word or shh per beat)")
    for l in CHART:
        for w in l:
            if beat_kind(w) not in "qer":
                errs.append(f"chart word {w} is not 1-2 syllables")
    if len(CARDS) != 8 or len(D7_CARDS) != 12:
        errs.append("card counts")
    # 2. readings
    n35 = len(D1_35_TEXT.split())
    if not 180 <= n35 <= 230:
        errs.append(f"Day 1 3-5 reading is {n35} words (about 200 wanted)")
    if not 6 <= len(D1_K2_TEXT) <= 8:
        errs.append("Day 1 K-2 reading must be 6-8 sentences")
    if not 5 <= len(D6_K2_TEXT) <= 8:
        errs.append("Day 6 K-2 reading sentence count")
    n6 = len(D6_35_TEXT.split())
    if not 125 <= n6 <= 200:
        errs.append(f"Day 6 3-5 reading is {n6} words")
    for q, opts, a in D1_K2_Q + D6_K2_Q:
        if not 0 <= a < len(opts):
            errs.append(f"K-2 question '{q}': answer index out of range")
    # K-2 reading answers follow from the text
    t = " ".join(D1_K2_TEXT)
    for need in D1_K2_NEED:
        if need not in t:
            errs.append(f"Day 1 K-2 reading lacks '{need}' that the key relies on")
    t35 = D1_35_TEXT
    for need in D1_35_NEED:
        if need not in t35:
            errs.append(f"Day 1 3-5 reading lacks '{need}' that the key relies on")
    # 3. word search: every word exactly once, placements spell it, directions allowed, no hidden bad words
    for w in WS_WORDS:
        if count_word(GRID, w) != 1:
            errs.append(f"word search: {w} found {count_word(GRID, w)} times")
        cells = PLACE[w]
        if "".join(GRID[y][x] for y, x in cells) != w:
            errs.append(f"word search key: {w} cells do not spell it")
        if (cells[1][0] - cells[0][0], cells[1][1] - cells[0][1]) not in WS_DIRS:
            errs.append(f"word search: {w} runs in a direction the directions do not allow")
    for b in BAD_WORDS:
        if count_word(GRID, b):
            errs.append(f"word search: grid hides the word {b}")
    if len(WS_WORDS) != 12 or len(GRID) != WS_N or any(len(r) != WS_N for r in GRID):
        errs.append("word search size")
    # 4. decode: letters -> numbers -> letters round trip, A1Z26
    for w in DECODE_MSG:
        nums = [code_of(c) for c in w]
        if "".join(chr(64 + x) for x in nums) != w or not all(1 <= x <= 26 for x in nums):
            errs.append(f"decode: {w} does not round-trip")
    # 5. matching and bingo
    if sorted(MATCH_PIC_ORDER) != list(range(6)) or any(MATCH_PIC_ORDER[j] == j for j in range(6)):
        errs.append("Day 5 K-2 match: right column must be a shuffled permutation")
    if sorted(D6_35_MATCH_ORDER) != list(range(5)):
        errs.append("Day 6 match order is not a permutation")
    if len(BINGO) != 16 or len({a for a, _ in BINGO}) != 16:
        errs.append("bingo needs 16 distinct answers")
    for a, c in BINGO:
        if a.lower() in c.lower():
            errs.append(f"bingo clue for {a} contains its answer")
    if sorted(BANK_ORDER_K2) != list(range(12)) or sorted(BANK_ORDER_35) != list(range(16)):
        errs.append("bingo bank orders are not permutations")
    # 6. plan, pairs, timings
    if len(PLAN) != len(set(PLAN)):
        errs.append("plan has a repeated page")
    for d in DAYS:
        k = d["n"]
        tot = sum(int(m) for m, _, _ in d["steps"])
        if not 30 <= tot <= 45:
            errs.append(f"Day {k} steps add to {tot} min, not 30-45")
        for need in (f"d{k}_plan", f"d{k}_k2", f"d{k}_35"):
            if need not in PLAN:
                errs.append(f"Day {k}: missing {need}")
    if [d["n"] for d in DAYS] != list(range(1, 9)):
        errs.append("days must be 1-8")
    covered = set()
    for _, a, b, _ in PARTS:
        covered |= set(PLAN[IX[a] - 1:IX[b]])
    if covered != set(PLAN):
        errs.append(f"teacher table misses pages: {sorted(set(PLAN) - covered)}")
    if not 48 <= TOTAL <= 58:
        errs.append(f"{TOTAL} pages, expected 48-58")
    return errs


def pdf_fonts(path):
    out = subprocess.run(["pdffonts", path], capture_output=True, text=True, check=True).stdout.splitlines()[2:]
    return [(ln.split()[0], ln.split()[-5]) for ln in out]


def pdf_text(path, n):
    return [subprocess.run(["pdftotext", "-raw", "-f", str(i + 1), "-l", str(i + 1), path, "-"], capture_output=True, text=True, check=True).stdout
            for i in range(n)]


def flat(s):
    return re.sub(r"\s+", " ", s)


def key_text_errors(txt):
    """The answers printed in the PDF's key pages equal the checked data."""
    errs = []
    a = flat(txt[IX["key_a"] - 1])
    b = flat(txt[IX["key_b"] - 1])
    c = flat(txt[IX["key_c"] - 1])
    for i, (q, o, ans) in enumerate(D1_K2_Q):
        if o[ans] not in a:
            errs.append(f"key A: Day 1 K-2 answer {o[ans]} missing")
    for q, ans in D1_35_Q:
        if ans not in a:
            errs.append(f"key A: Day 1 3-5 answer '{ans}' missing")
    for i, w in enumerate(D2_K2_A):
        if f"A{i + 1} {wd(w).replace('-', ' · ')} {nsyl(w)}" not in a:
            errs.append(f"key A: Day 2 K-2 A{i + 1} not found")
    for i, w in enumerate(D2_K2_B):
        if f"B{i + 1} {wd(w).replace('-', ' · ')} {nsyl(w)}" not in a:
            errs.append(f"key A: Day 2 K-2 B{i + 1} not found")
    for i, w in enumerate(D2_35_A):
        if f"A{i + 1} {wd(w).replace('-', ' · ')} {nsyl(w)}" not in a:
            errs.append(f"key A: Day 2 3-5 A{i + 1} not found")
    for cl in (1, 2, 3):
        if f"B · {cl} " + ", ".join(wd(w).replace("-", "") for w in D2_35_SORT[cl]) not in a:
            errs.append(f"key A: Day 2 3-5 sort for {cl} claps not found")
    ex = " ".join(f"{wd(w)} {SYL[beat_kind(w)]}" for w in D2_35_EX)
    if ex not in a:
        errs.append("key A: example chant not found")
    if " ".join(DECODE_MSG) not in b:
        errs.append("key B: decode message not found")
    for w in WS_WORDS:
        if w not in b:
            errs.append(f"key B: {w} not listed")
    for i in range(5):
        if f"{i + 1} {JOBS[i][0]} {'ABCDE'[D6_35_MATCH_ORDER.index(i)]}" not in b:
            errs.append(f"key B: Day 6 match row {i + 1} not found")
    for q, o, ans in D6_K2_Q:
        if o[ans] not in b:
            errs.append(f"key B: Day 6 K-2 answer {o[ans]} missing")
    for i, (ans, _) in enumerate(BINGO):
        if f"{i + 1} {ans}" not in c:
            errs.append(f"key C: bingo answer {i + 1} {ans} not found")
    for need in ("SLOWLY", "QUICKLY", "FROZE"):
        if need not in c:
            errs.append(f"key C: Day 4 answer {need} missing")
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
      const BOX = '.part, .top, .name, .box, .bx, .cut, .doc table, table.t, .grid4, .meta, .steps li, .doc p, .doc ul';
      document.querySelectorAll('.page').forEach((pg, i) => {
        if (pg.classList.contains('cover')) return;
        const pr = pg.getBoundingClientRect();
        const ft = pg.querySelector('.foot');
        if (pg.scrollHeight > pg.clientHeight + 1) res.push(`page ${i + 1}: content overflows the page`);
        if (!ft) { res.push(`page ${i + 1}: no footer`); return; }
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
          if (r.height && (r.right > pr.right - 0.35 * 96 + 0.5 || r.left < pr.left + 0.35 * 96 - 0.5)) res.push(`page ${i + 1}: text "${el.textContent.trim().slice(0, 30)}" too close to the page edge`);
        });
        pg.querySelectorAll('.main *').forEach(el => {
          if (skip(el) || el.closest('svg') || el.tagName === 'tspan') return;
          const r = el.getBoundingClientRect();
          if (r.height > 0 && r.width > 0 && r.bottom > ftop - 8) res.push(`page ${i + 1}: element ${el.tagName}.${el.getAttribute('class') || ''} bottom ${(r.bottom - ftop).toFixed(1)}px vs footer rule (needs <= -8)`);
        });
        pg.querySelectorAll('.box, .cut, .bx, .part').forEach(bx => {
          if (bx.scrollWidth > bx.clientWidth + 1 || bx.scrollHeight > bx.clientHeight + 1) res.push(`page ${i + 1}: content overflows a ${bx.className} box`);
          const br = bx.getBoundingClientRect();
          bx.querySelectorAll('svg, img').forEach(sv => {
            const s = sv.getBoundingClientRect();
            if (s.left < br.left + 3 || s.right > br.right - 3 || s.top < br.top + 3 || s.bottom > br.bottom - 3) res.push(`page ${i + 1}: a drawing is too close to its ${bx.className} box edge`);
          });
        });
        pg.querySelectorAll('.top .t').forEach(t => { if (t.getBoundingClientRect().right > pg.querySelector('.top .tag').getBoundingClientRect().left - 8) res.push(`page ${i + 1}: title crowds the tag`); });
        let maxb = 0;
        pg.querySelectorAll('*').forEach(el => { if (skip(el)) return; const r = el.getBoundingClientRect(); if (r.height > 0 && r.width > 0 && ((el.children.length === 0 && ((el.textContent || '').trim() || el.matches('svg, img'))) || el.matches('.part, .box, table, .cut, .ln2, .fl'))) maxb = Math.max(maxb, r.bottom); });
        if (!pg.classList.contains('doc') && !pg.querySelector('.keepblank') && ftop - maxb > 105) res.push(`page ${i + 1}: blank band of ${(ftop - maxb).toFixed(0)}px above the footer (over 10% of the page)`);
      });
      document.querySelectorAll('.sq').forEach((sq, i) => {
        const sr = sq.getBoundingClientRect();
        const bandEl = sq.querySelector('.band');
        const btop = bandEl.getBoundingClientRect().top;
        const full = el => el.matches('.cv-block, .cv-series, .band');
        sq.querySelectorAll('.shot, .card, .rib, .num, .lbl, .sub, .hd, .store, img').forEach(el => {
          if (full(el) || el.closest('.cv-block')) return;
          const r = el.getBoundingClientRect();
          const w = el.classList.contains('shot') || el.classList.contains('card') ? 8 : 0;
          if (r.left < sr.left + 24 || r.right + w > sr.right - 24) res.push(`square ${i + 1}: ${el.className || el.tagName} within 24px of a side edge`);
          if (r.top < sr.top + 16) res.push(`square ${i + 1}: ${el.className || el.tagName} within 16px of the top`);
          if (!el.closest('.cv-block') && el.className !== 'cv-series' && r.bottom + w > btop - 8 && !el.matches('.cv-block *')) res.push(`square ${i + 1}: ${el.className || el.tagName} within 8px of the band`);
        });
        sq.querySelectorAll('img').forEach(im => { if (!im.complete || im.naturalWidth === 0) res.push(`square ${i + 1}: an image did not load`); });
        const els = [...sq.querySelectorAll('.store, .hd, .sub, .lbl, .shot, .card, .rib, .cv-hero')].filter(e => !e.closest('.cv-block'))
          .map(e => ({ e, r: e.getBoundingClientRect() }));
        for (let a = 0; a < els.length; a++) for (let c = a + 1; c < els.length; c++) {
          const A = els[a].r, B = els[c].r;
          const pad = 6;
          const ov = A.left < B.right + (els[c].e.matches('.shot, .card') ? 8 : 0) - 0 && B.left < A.right + (els[a].e.matches('.shot, .card') ? 8 : 0) && A.top < B.bottom && B.top < A.bottom;
          if (ov) {
            const allowed = (els[a].e.matches('.cv-mock') && els[c].e.matches('.cv-hero')) || (els[c].e.matches('.cv-mock') && els[a].e.matches('.cv-hero'));
            const inside = (els[a].e.matches('.lbl, .num') || els[c].e.matches('.lbl, .num')) && false;
            if (!allowed && !inside) res.push(`square ${i + 1}: ${els[a].e.className || els[a].e.tagName} overlaps ${els[c].e.className || els[c].e.tagName}`);
          }
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

PIX_JS = r"""
const { chromium } = require('playwright');
const url = require('url');
(async () => {
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
    # drawings: ink must stay inside its box with padding (rendered pixels, each picture alone at 4x)
    from PIL import Image
    names = ["heart", "drum", "lantern", "trumpet", "piano", "gong", "cymbal", "card", "star", "snowflake"]
    items = [pic(nm, 100) for nm in names] + [sun_art(100)]
    page_ = (f'<!doctype html><html><head><meta charset="utf-8"></head><body style="margin:0">'
             + "".join(f'<div style="margin:20px">{s}</div>' for s in items) + '</body></html>')
    write("pix.html", page_)
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
    for nm, label in zip(sorted(os.listdir(shots)), names + ["sun"]):
        im = Image.open(os.path.join(shots, nm)).convert("RGBA")
        bb = im.getchannel("A").point(lambda v: 255 if v > 8 else 0).getbbox()
        w, h = im.size
        if bb is None:
            errs.append(f"rendered pixels: picture {label} is blank")
            continue
        edge = min(bb[0], bb[1], w - bb[2], h - bb[3])
        need = round(w * 0.03)          # at least as wide as the 3-unit stroke (3% of the 100-unit box)
        if edge < need:
            errs.append(f"rendered pixels: picture {label} ink comes within {edge}px of its box edge (needs {need}px)")
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
        ytop = 2000
        for y in range(1999, 0, -1):
            if px[2, y] < 60 and px[1997, y] < 60:
                ytop = y
            else:
                break
        if ytop > 1990 or ytop < 1700:
            errs.append(f"{name}: bottom band not found (starts at {ytop})")
        limit = ytop - 4 if name != "cover.png" else 1290      # the cover's colour block and series bar run edge to edge below y=1300
        for edge, pts in (("top", [(x, y) for x in range(0, 2000, 2) for y in range(0, 14)]),
                          ("left", [(x, y) for x in range(0, 14) for y in range(0, limit, 2)]),
                          ("right", [(x, y) for x in range(1986, 2000) for y in range(0, limit, 2)])):
            if any(px[x, y] < 235 for x, y in pts):
                errs.append(f"{name}: art or ink touches the {edge} edge")
        rows = [sum(1 for x in range(0, 2000, 8) if px[x, y] < 200) for y in range(0, 2000, 2)]
        run = best = 0
        for y in range(120, ytop, 2):
            if rows[y // 2] == 0:
                run += 2
                best = max(best, run)
            else:
                run = 0
        if best > 200:
            errs.append(f"{name}: blank band of {best}px")
        cols = [x for x in range(0, 2000, 2) if any(px[x, y] < 200 for y in range(120, limit, 4))]
        if cols and (min(cols) < 40 or max(cols) > 1960):
            errs.append(f"{name}: content within 40px of the left or right edge")
    cover = open(os.path.join(BUILD, "cover.html")).read()
    if "swm" in re.sub(r"<style>.*?</style>", "", cover, flags=re.S):
        errs.append("cover.png carries a watermark")
    for t in ("NO PREP", "NO TECH", "8 DAYS", "MONTHLY MUSIC SUB PLANS", "February"):
        if t not in cover:
            errs.append(f"cover.png lacks '{t}'")
    return errs


def verify_files():
    errs = []
    from pypdf import PdfReader
    for p in [PDF, PREVIEW_PDF, COVER_PNG, *PREVIEW_PNGS, UPLOAD, TPT_JSON, SOURCES, HERO]:
        if not os.path.exists(p):
            errs.append(f"missing {os.path.relpath(p, HERE)}")
    if errs:
        return errs
    for path, want in ((PDF, TOTAL), (PREVIEW_PDF, 4)):
        rd = PdfReader(path)
        if len(rd.pages) != want:
            errs.append(f"{os.path.basename(path)}: {len(rd.pages)} pages, expected {want}")
        for i, pg_ in enumerate(rd.pages):
            if abs(float(pg_.mediabox.width) - 612) > 1 or abs(float(pg_.mediabox.height) - 792) > 1:
                errs.append(f"{os.path.basename(path)} p{i + 1}: not US Letter")
        fonts = pdf_fonts(path)
        for name, emb in fonts:
            if emb != "yes":
                errs.append(f"{os.path.basename(path)}: font {name} not embedded")
            if not re.search(r"oswald|sourcesans", name.lower()):
                errs.append(f"{os.path.basename(path)}: unexpected font {name} (a glyph fell back to a system font)")
    rd = PdfReader(PDF)
    txt = pdf_text(PDF, len(rd.pages))
    fl_ = [flat(t) for t in txt]
    txt_lines_all = [ln.strip() for t in txt for ln in t.splitlines()]
    # footer rendered position, page numbers, watermark
    boxes = subprocess.run(["pdftotext", "-bbox", PDF, "-"], capture_output=True, text=True, check=True).stdout
    for i, pgx in enumerate(re.findall(r'<page width="([\d.]+)" height="([\d.]+)">(.*?)</page>', boxes, re.S)):
        if i == 0:
            continue
        ys = [float(m) for m in re.findall(r'yMax="([\d.]+)">Lotze', pgx[2])]
        if not ys:
            errs.append(f"p{i + 1}: footer not found")
        elif max(ys) > float(pgx[1]) - 0.35 * 72:
            errs.append(f"p{i + 1}: footer ends {float(pgx[1]) - max(ys):.1f}pt from the bottom edge (< 25pt)")
    for i, t in enumerate(fl_):
        if len(t) < 40:
            errs.append(f"PDF page {i + 1} looks blank")
        if "PREVIEW" in t:
            errs.append(f"product PDF page {i + 1} carries a PREVIEW watermark")
        if i > 0 and "Brian Lotze · Hudson Beat" not in t:
            errs.append(f"page {i + 1}: footer missing")
        if i > 0 and not re.search(rf"Page {i + 1}\b", t):
            errs.append(f"page {i + 1}: page number in the footer is wrong")
    errs += key_text_errors(txt)
    # the hard rules: scan every page of the PDF, the preview, and the listing text for device / notation / play words
    scan_src = [("PDF page %d" % (i + 1), t) for i, t in enumerate(fl_)]
    ptxt = pdf_text(PREVIEW_PDF, 4)
    scan_src += [("preview page %d" % (i + 1), flat(t)) for i, t in enumerate(ptxt)]
    for lab, t in scan_src:
        t2 = ALLOWED_MUSIC_FACT.sub("", t.replace(DISCLOSURE, ""))
        for m in DEVICE_RE.finditer(t2):
            errs.append(f"{lab}: hard-rule word '{m.group(0)}' ...{t2[max(0, m.start() - 30):m.end() + 20]}...")
    up = open(UPLOAD).read()
    desc = up.split("## 2. Description")[1].split("## 3.")[0].replace(DISCLOSURE, "")
    # the description may say what the product avoids ("no computer, projector, speaker or video"), so only the verbs are scanned there
    for m in re.finditer(r"\b(sing|sings|singing|play|plays|playing|played)\b", ALLOWED_MUSIC_FACT.sub("", desc), re.I):
        if not re.search(r"never reads music or sings", desc[max(0, m.start() - 40):m.end() + 5]):
            errs.append(f"UPLOAD.md description uses '{m.group(0)}'")
    # page references
    for i, t in enumerate(fl_):
        for m in re.finditer(r"(?i)\bpages? (\d+)(?:–(\d+))?", t):
            a, b = int(m.group(1)), int(m.group(2) or m.group(1))
            if a < 1 or b > TOTAL or b < a:
                errs.append(f"page {i + 1}: reference '{m.group(0)}' is outside the {TOTAL}-page file")
    for d in DAYS:
        k = d["n"]
        for s_ in ("k2", "35"):
            if f"page {IX[f'd{k}_{s_}']}" not in fl_[IX[f"d{k}_plan"] - 1]:
                errs.append(f"Day {k} plan does not point to its {s_} sheet")
        for key_ in (f"d{k}_k2", f"d{k}_35"):
            t = fl_[IX[key_] - 1]
            if DAY_SHEETS[k][0 if key_.endswith("k2") else 1].lower() not in t.lower():
                errs.append(f"{key_}: sheet title missing")
            if ("Grades K–2" if key_.endswith("k2") else "Grades 3–5") not in t:
                errs.append(f"{key_}: grade tag missing")
    for key_, target in (("d1_k2", "key_a"), ("d1_35", "key_a"), ("d2_k2", "key_a"), ("d2_35", "key_a"), ("d4_k2", "key_c"), ("d5_k2", "key_b"),
                         ("d5_35", "key_b"), ("d6_k2", "key_b"), ("d6_35", "key_b"), ("d7_k2", "key_c"), ("d7_35", "key_c"), ("d8_k2", "key_c"), ("d8_35", "key_c")):
        if f"Answer key on page {IX[target]}" not in fl_[IX[key_] - 1]:
            errs.append(f"{key_}: answer-key cross-reference missing")
    # glance table lists each plan page number; teacher table ranges
    for d in DAYS:
        if f"page {IX[f'd{d['n']}_k2']}" not in fl_[IX["glance"] - 1]:
            errs.append(f"glance page lacks Day {d['n']} K-2 page")
    for a_, b_, c_, _ in PARTS:
        if prange(b_, c_) not in fl_[IX["teacher"] - 1]:
            errs.append(f"teacher notes lack range {prange(b_, c_)}")
    # bingo: the plan's wording is true of the boards shown; crayon list on the quick page matches the plans
    k2t, t35, plant, quick = fl_[IX["d8_k2"] - 1], fl_[IX["d8_35"] - 1], fl_[IX["d8_plan"] - 1], fl_[IX["quick"] - 1]
    if "corner-to-corner" in k2t or "diagonal" in k2t or "across in one row" not in k2t:
        errs.append("K-2 bingo sheet wording does not match its 3 x 4 board")
    if "corner-to-corner" not in t35 or "corner-to-corner" not in plant or "three squares across in one row" not in plant:
        errs.append("bingo plan or 3-5 sheet wording missing")
    if f"{BINGO_K2} squares" not in plant or f"{BINGO_35} squares" not in plant:
        errs.append("bingo plan does not state the square counts")
    if days_txt(CRAYON_DAYS) not in quick:
        errs.append("quick start crayon list differs from the plans")
    for d in DAYS:
        has = "crayons" in re.split(r"(?i)you need", fl_[IX[f"d{d['n']}_plan"] - 1])[1].lower().split("copies")[0]
        if has != (d["n"] in CRAYON_DAYS + CRAYON_OPT):
            errs.append(f"Day {d['n']} plan crayon list")
    if any(re.search(r"\bpages?$", x) and re.match(r"\d", y) for x, y in zip(txt_lines_all, txt_lines_all[1:])):
        errs.append("a page reference wraps across a line")
    # preview watermarks
    if sum(1 for t in ptxt if t.count("PREVIEW") == 1) != 4:
        errs.append("preview PDF: each of the 4 pages needs exactly one PREVIEW watermark")
    st = pdf_text(os.path.join(BUILD, "shots.pdf"), len(SHOT_KEYS))
    if sum(1 for t in st if t.count("PREVIEW") == 1) != len(SHOT_KEYS):
        errs.append("page shots used on the cover and previews are not all watermarked")
    errs += verify_images()
    # metadata
    tj = json.load(open(TPT_JSON))
    topts = json.load(open(os.path.join(TPT, "TAG-OPTIONS.json")))["options"]
    if tj["tags"] != ["Black History Month", "Valentine's Day", "Lunar New Year", "Groundhog Day", "Presidents' Day"] or any(t not in topts for t in tj["tags"]):
        errs.append("tpt.json tags must be exactly the five tags of the February calendar row")
    if tj["subjects"] != ["Music"] or tj["grades"] != ["kindergarten", "2nd-grade", "3rd-grade", "5th-grade"]:
        errs.append("tpt.json subjects or grades differ from item 007")
    if tj["price"] != "15.00" or tj["license_price"] != "15.00" or not tj.get("tax_code") or tj["pages"] != len(rd.pages):
        errs.append("tpt.json price, tax code or pages")
    for k, f in tj["files"].items():
        if not os.path.exists(os.path.join(HERE, f)):
            errs.append(f"tpt.json file {k} missing: {f}")
    m = re.search(r"^## 1\. Title\s*\n+```\n(.+?)\n```\n\((\d+) characters", up, re.M | re.S)
    if not m:
        errs.append("UPLOAD.md: title block or its character count not found")
    else:
        title = m.group(1).strip()
        if len(title) > 80 or int(m.group(2)) != len(title):
            errs.append("UPLOAD.md: title over 80 characters or the stated count is wrong")
        if re.search(r"(?i)winter|holiday|new year|season|snow|valentine|lunar", title):
            errs.append("UPLOAD.md title carries a seasonal or holiday word")
        if not re.fullmatch(r"February Music Sub Plans K-5 \| .+ \| No Prep, No Tech", title):
            errs.append("UPLOAD.md: title is not in the format 'February Music Sub Plans K-5 | <theme words> | No Prep, No Tech'")
    if DISCLOSURE not in up or DISCLOSURE not in fl_[IX["terms"] - 1]:
        errs.append("disclosure line missing from UPLOAD.md or the terms page")
    for need in ("$15.00", f"{TOTAL} pages", "Year-Long Music Sub Plans Bundle", "leave a rating", "Follow the Hudson Beat store"):
        if need not in up:
            errs.append(f"UPLOAD.md: missing '{need}'")
    for bad in ("checked by hand", "handmade", "hand-checked", "classroom-tested", "classroom tested"):
        if bad in up.lower():
            errs.append(f"UPLOAD.md says '{bad}'")
    sec = up.split("## 5. Page count by section")[1].split("##")[0]
    nums = [int(x) for x in re.findall(r"^- (?!Total)[^\n]*: (\d+)$", sec, re.M)]
    if sum(nums) != TOTAL:
        errs.append(f"UPLOAD.md page list sums to {sum(nums)}, PDF has {TOTAL}")
    dn = [int(x) for x in re.findall(r"^• [^\n]*\((\d+) pages?\)", desc, re.M)]
    if sum(dn) != TOTAL:
        errs.append(f"UPLOAD.md description page list sums to {sum(dn)}, PDF has {TOTAL}")
    if f"({TOTAL} pages" not in desc:
        errs.append("UPLOAD.md description page total")
    if up != upload_md():
        errs.append("UPLOAD.md is out of date: run gen.py")
    # sources: every fact family printed in the product is listed
    src = open(SOURCES).read()
    for need in ("Scott_Joplin", "Florence_Price", "Duke_Ellington", "Ella_Fitzgerald", "Louis_Armstrong", "Woodson", "Lunar", "groundhog", "opm.gov", "bls.gov", "Piano_tuning", "1933", "1899", "1887"):
        if need not in src:
            errs.append(f"SOURCES.md lacks '{need}'")
    if src != sources_md():
        errs.append("SOURCES.md is out of date: run gen.py")
    for f in ("release", "uploaded"):
        if os.path.exists(os.path.join(HERE, f)):
            errs.append(f"{f} exists: only the Manager / uploader writes it")
    # art bookkeeping
    usage = open(os.path.join(TPT, "_art", "USAGE.md")).read()
    if not re.search(r"^\d{4}-\d{2}-\d{2} \| 077 \| hero\.png", usage, re.M):
        errs.append("tpt/_art/USAGE.md lacks the 077 line")
    if os.path.exists(os.path.join(TPT, "_art", "next", "february-music-sub-plans-k-5")):
        errs.append("art/next folder for this item still exists")
    return errs


def check():
    errs = verify_data() + verify_layout() + verify_files()
    if errs:
        print("CHECK FAILED")
        print("\n".join(" - " + e for e in errs[:80]))
        if len(errs) > 80:
            print(f" ... and {len(errs) - 80} more")
        sys.exit(1)
    print(f"CHECK OK: {len(WORDS)} words' syllable counts match an independent table; every chant is 4 beats of 1-2 syllable words or shh; "
          f"8 days each 30-45 min; K-2 and 3-5 sheet pair for all 8 days; Day 1 and 6 readings support their keys; word search has each of 12 words exactly once; "
          f"decode round-trips; bingo has 16 clues whose answers are on the boards; key text in the PDF equals the data; page references, footers ({TOTAL} Letter pages, "
          f"footer gap >= 8px, 0.35in edges) and drawing padding verified on rendered output; hard-rule scan of every PDF, preview and listing text found no device, "
          f"singing, playing or notation words; preview 4 pages with one PREVIEW each; images 2000x2000 with clean edges; tpt.json, UPLOAD.md and SOURCES.md agree.")


if __name__ == "__main__":
    if "--check" in sys.argv:
        check()
    else:
        build()
