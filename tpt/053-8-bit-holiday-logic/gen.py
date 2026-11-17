#!/usr/bin/env python3
"""Logic Pro project kit: 8-Bit Holiday (TpT 053): the teacher resource, the intro deck and the listing files.

    python3 gen.py            build everything into this folder (also writes UPLOAD.md)
    python3 gen.py --lowres   same, but square images at scale 1 and small page shots (self-check only; --check rejects it)
    python3 gen.py --check    verify content, the carol (two transcriptions in two keys, a transposition check, bar sums, pitches,
                              chords, chord spellings, arpeggio sequences, noise drum patterns), the tempo and length arithmetic, the
                              worked example, drawings, files, page/slide counts, class slots, notes, fonts, fit and overlap, overflow
                              and dead space, truncated slide bullets, the edges of cover.png and the previews, banned strings,
                              tpt.json and UPLOAD.md

An ORIGINAL Hudson Beat project (dmp2.ORIGINAL = True, like 031, 036, 040 and 045). Students arrange the public-domain carol
"O Come, All Ye Faithful" (Adeste fideles; the tune is attributed to John Francis Wade, c. 1743; the earliest dated manuscript is from
1751) as an 8-bit chiptune in Logic Pro: a square-wave lead, arpeggiated chords (the Arpeggiator MIDI plug-in) on a pulse wave, a
triangle-wave bass, a noise-channel drum and a Bitcrusher. No audio ships and no lyrics are printed.

The carol is stored three times: SRC_A is the first transcription as typed (G major, from the Open Hymnal Project, which engraves
"A Hymnal", Episcopal, 1916, hymn 72); SRC_B is a second, independent transcription typed in C major; CHART is the chart the
students use (C major, every pitch five semitones above SRC_A). --check parses both transcriptions and proves SRC_A + 5 semitones == SRC_B
== CHART, note for note and length for length. Pitches and lengths only; no engraving or edition is reproduced.
The art on the cover, the previews and the deck is the owner's pre-made hero (art/hero.png), used whole. Everything else (piano
rolls, waveforms, arpeggio strips, drum grids, the arrangement map) is drawn in code. The shared builder is ../_dmp2_common/dmp2.py.
"""
import math
import os
import re
import sys
from html import escape

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "_dmp2_common"))
import dmp2 as D  # noqa: E402

ORIGINAL = True
SLUG = "8-bit-holiday"
TITLE = "8-Bit Holiday"
ACCENT = "#2F7FB8"          # this product's single accent: icy blue (a shade deeper than the art's #4FA3D9, so small labels read)
ACC_LIGHT = "#DCEBF6"
PRICE = "8.00"
CLASSES = 4
GRADES_TEXT = "9–12"
GRADE_SLUGS = ["9th-grade", "10th-grade", "11th-grade", "12th-grade"]
TAGS = ["Winter", "Christmas-Chanukah-Kwanzaa", "Project-based Learning", "Projects"]     # exact entries of tpt/TAG-OPTIONS.json, none a heading
SUBJECTS = ["Music", "Computer Science - Technology", "Music Composition"]     # all in SUBJECT-OPTIONS.json, none a heading
ANSWER_KEY = None
LISTING_TITLE = "Logic Pro Chiptune Project | 8-Bit Music Arrangement | High School Music Tech"
DESC_START = "Chiptune music making for high school music technology:"
DESC_MUST = ["8-Bit Holiday", "piano-roll", "no audio", "square", "triangle", "Arpeggiator", "Bitcrusher", "public domain", "O Come, All Ye Faithful"]
ZIP_DIR = "8-Bit Holiday - Hudson Beat"
ZIP_DATE = (2026, 11, 17, 12, 0, 0)
TYPE = "Original Project"
PROJ_LINE = "Music Technology | <i>Chiptune Arrangement Project</i> | 4 class periods"
DECK_STRAP = "A carol in 8 bits"
REFLECT_ROW = "Plan &amp; Reflection"
# split so this file never contains them (the --check scan reads every file in this folder)
BANNED_EXTRA = ["Rud" + "olph", "Fro" + "sty", "Gri" + "nch", "Santa Claus " + "Is", "Jingle Bell " + "Rock", "Feliz " + "Navidad",
                "Mari" + "ah Carey", "Spoti" + "fy", "You" + "Tube", "Home " + "Alone", "Nin" + "tendo", "Game " + "Boy", "Se" + "ga ",
                "Com" + "modore", "At" + "ari", "Super " + "Mario", "Zel" + "da", "Pac-" + "Man", "Tet" + "ris", "Mega " + "Man", "Ro" + "land"]

# ================================================================ page plan (teacher pages 2-11, student pages 12-26)
PLAN = ["cover", "howto", "overview", "setup", "pacing", "tn1", "tn2", "logicref", "tunes", "example", "example2", "chart1", "chart2",
        "chart3", "channels", "arps", "drums", "plan", "layers", "proj1", "proj2", "proj3", "rubric", "vocab", "present", "reflect", "terms"]


def pg(k):
    return PLAN.index(k) + 1


# ================================================================ numbers the text uses (all verified in --check)
TEMPO_LO, TEMPO_HI = 120, 150          # the project's tempo range
LEN_LO, LEN_HI = 45, 75                # seconds
BARS_MIN, BARS_MAX = 31, 35            # intro (2-6) + the whole carol (21) + the chorus again (8)


def bar_s(bpm):
    return 240 / bpm                    # seconds in one bar of 4/4


def length_s(bars, bpm):
    return bars * 240 / bpm


def mmss(t):
    t = int(round(t))
    return f"{t // 60}:{t % 60:02d}"


# ================================================================ the project text (original; students read these pages)
OVERVIEW = ("Rebuild a carol as an 8-bit game tune. Enter the melody of “O Come, All Ye Faithful”, a public-domain tune from the 1700s, into "
            "Logic Pro from a piano-roll note chart and play it on a square-wave lead. Then build the other three channels of a classic "
            "game-music chip: arpeggios that spell out the chords, a triangle-wave bass and a noise drum, and crush it all with a Bitcrusher "
            "so it sounds lo-fi. Your finished arrangement is 45 to 75 seconds long at 120 to 150 BPM, and your classmates should still "
            "recognize the carol.")
GOALS = ["Enter a melody into Logic Pro’s Piano Roll from a note chart, with the right pitches and lengths",
         "Build four chip channels: a square-wave lead, arpeggiated chords, a triangle-wave bass and a noise drum",
         "Spell the chords of a key and play them as arpeggios with the Arpeggiator MIDI plug-in",
         "Plan an arrangement in bars and seconds, and prove that its length is between 45 and 75 seconds"]
VOCAB = [("Chiptune", "Music made with the simple sounds of early game chips: a few channels of square, triangle and noise waves, often with fast arpeggios"),
         ("Square wave", "A wave that switches between a high and a low level, spending half of each cycle at each; it sounds bright, buzzy and hollow"),
         ("Arpeggio", "The notes of a chord played one after another instead of together; a chip channel plays one note at a time, so an arpeggio suggests a chord"),
         ("Bitcrusher", "An effect that lowers a sound’s bit depth and sample rate on purpose, so it sounds grainy and lo-fi")]
REQS = ["Enter the carol’s melody from the note chart (pages @CHART1–@CHART3) on a square-wave lead; every pitch and length matches the chart",
        "Set a tempo from 120 to 150 BPM in 4/4 and build four channels: the square lead, arpeggios, a triangle-wave bass and a noise drum (pages @CHANNELS–@DRUMS)",
        "Play the chords of the carol as arpeggios with the Arpeggiator, using at least two different patterns (page @ARPS)",
        "Put the triangle bass on the chord roots and program a noise drum pattern from page @DRUMS",
        "Use a Bitcrusher, and make the sound change from one section to the next, for example with more crush in the intro",
        "Arrange 31 to 35 bars (45 to 75 seconds): an intro, the whole carol once and the chorus again with a change, and show the length arithmetic (page @LAYERS)",
        "Reflect on how the arrangement went, in writing or out loud (page @REFLECT)"]
FILE_NAME = "“Your Name – 8-Bit Holiday”"
STEPS = ["<b>Read</b> — Read the note chart (pages @CHART1–@CHART3) and the four channels (page @CHANNELS)",
         "<b>Plan</b> — Fill in My plan: tempo, sounds, arpeggio patterns and drum pattern (page @PLAN)",
         "<b>Enter the melody</b> — Draw the chart into the Piano Roll on a square-wave lead and listen for wrong notes (Logic quick reference: page @LOGICREF)",
         "<b>Chords and bass</b> — Enter the chords, play them with the Arpeggiator (page @ARPS) and add a triangle bass on the chord roots",
         "<b>Drums and lo-fi</b> — Program a noise drum pattern (page @DRUMS) and add a Bitcrusher (page @CHANNELS)",
         "<b>Arrange and mix</b> — Plan the form on the Layer map (page @LAYERS), build 31 to 35 bars, balance with volume and Channel EQ, and bounce with the file name format",
         "<b>Present &amp; get feedback</b> — Write three questions you want classmates to answer about your arrangement. Play it, say how you built "
         "each channel, and answer at least 2 of each classmate’s questions. Then reflect (page @REFLECT)."]
TIPS = ["Chip music is about limits. Each channel plays one note at a time, so let an arpeggio suggest the chord instead of stacking notes.",
        "Keep the arpeggios quieter and lower than the lead, so the melody stays on top.",
        "Add one channel at a time and listen before you add the next.",
        "Save a new version of your project before each big experiment, so you can always go back."]
CHECK = ["Bounced .mp3 or .wav handed in where your teacher says",
         "Zipped .logicx project file handed in",
         f"Files named correctly: {FILE_NAME}",
         "My plan, Layer map and Reflection page handed in",
         "Rubric self-score done (page @RUBRIC)",
         "I can name my four channels and what each one plays"]
RUBRIC_NOTE = "Each category is scored 1–5. Score yourself first; your final grade is the average of your self-score and your teacher’s score."
LEVELS = [1, 2, 3, 4, 5]
RUBRIC = [
    ("Melody & Notes", ["The melody is missing or mostly wrong", "Several wrong pitches or lengths; the lead is not a square or pulse sound",
                        "Mostly right, with a few slips; the lead is a square-wave sound",
                        "Every pitch and length matches the chart, on a square-wave lead",
                        "Exact and clean, with crisp notes played one at a time; the carol is unmistakable"]),
    ("Chip Sounds", ["One sound only, or no chip-style sounds", "Two channels use chip waves; the bass or the drum is missing",
                     "Square lead, triangle bass and noise drum, but one is hard to hear",
                     "All four channels sound like a chip, and a Bitcrusher gives a lo-fi feel",
                     "Every channel is shaped on purpose, and the Bitcrusher changes between sections"]),
    ("Arps & Chords", ["No chords or arpeggios", "Chords are present but not played as arpeggios, or most are wrong",
                       "Arpeggios on most chords of the carol, with a few wrong notes",
                       "The right chord tones in an arpeggio for every chord, with at least two patterns",
                       "Chords spelled correctly, and arpeggios that change from section to section"]),
    ("Form & Length", ["No clear form; length not measured", "A loop with little change, or a length outside 45 to 75 seconds",
                       "Intro, verse and chorus; length in range", "Intro, the whole carol and a changed chorus in 31 to 35 bars, with the length arithmetic shown",
                       "A form that builds and resolves; channels enter and leave; the arithmetic is exact"]),
    ("Plan & Reflection", ["Plans, presentation or reflection missing", "Thin plan; little to say about choices",
                           "Plan and reflection complete, with basic detail", "Clear plan; thoughtful reflection and good answers to questions",
                           "Insightful reflection and a polished, confident presentation"]),
]
RUBRIC_TOTAL = 25
RUBRIC_SHORT = [ds[4] for _, ds in RUBRIC]
RUBRIC_SLIDE_LINE = "Scored 1–5 · final grade = average of your score and mine, out of 25"
RUBRIC_ROW_PITCH = 0.86
RUBRIC_LINE_Y = 6.3

TN_REINFORCES = ("Teaches how a few simple parts make a whole sound. Students learn that a game tune is a melody, chords turned into arpeggios, a "
                 "bass and a drum, and they practice entering notes, spelling chords and doing the arithmetic of bars, tempo and seconds in "
                 "Logic Pro’s Piano Roll.")
STRUGGLES = ["The notes go in but the tune sounds wrong: check the grid setting and the note lengths against the chart, bar by bar "
             "(Logic quick reference, page @LOGICREF). Remember that chart bar 1 is the pickup bar.",
             "The chords play but the arpeggio sounds wrong: compare the notes with the chord table on page @ARPS, and check that the Arpeggiator is in "
             "the MIDI FX slot of the arpeggio track, not of the melody track.",
             "The sound is not chip-like: use a square, pulse or triangle wave, one note at a time, with a short release and no reverb (page @CHANNELS).",
             "The length is off: use bars × 240 ÷ BPM and the length helper (page @LAYERS), then set the end of the project at the right bar."]
VAR_EASY = (f"Arrange the chorus only: enter the last beat of chart bar 13 and chart bars 14 to 21 (pages {PLAN.index('chart2') + 1}–{PLAN.index('chart3') + 1}), "
            "loop that eight-bar chorus, and use the Up pattern on every chord.")
VAR_HARD = ("Give the last chorus a key change: move it up two semitones with Transpose in the Region inspector (C major becomes D major), then "
            "rewrite the chords and arpeggios to match (page " + str(PLAN.index("arps") + 1) + " shows how a chord’s notes are built). Or add a second drum pattern for the bridge.")
RESOURCES = [("The note charts (pages @CHART1–@CHART3)",
              "Hand out all three pages. Pitch names are printed, so nobody needs to read staff notation."),
             ("Four channels and the Bitcrusher (page @CHANNELS)",
              "A card for each channel with its wave, its job and a starting setting in Logic, then a card for the Bitcrusher."),
             ("Arpeggio cards and noise drum patterns (pages @ARPS–@DRUMS)",
              "Chord spellings and four arpeggio patterns for the chords of the carol, then four one-bar patterns for the noise drum."),
             ("Worked example (pages @EXAMPLE–@EXAMPLE2)",
              "The carol as a 33-bar, 66-second chiptune, planned on paper. Use it as a model, not a template; student projects will differ.")]
TN_NOTE = ("Pairs well with a listening day: play the finished tunes without saying the title and let the class name the carol. A tune that "
           "people name quickly is an arrangement that kept the melody.")
GRADING = ["The rubric: five categories, each scored 1–5, /25 (page @RUBRIC). Students score themselves first; the final grade is the "
           "average of their score and yours.",
           "Melody & Notes (rubric row 1): open the project and compare the Piano Roll with the chart (pages @CHART1–@CHART3), bar by bar.",
           "Chip Sounds and Arps & Chords (rubric rows 2 and 3): check that the lead is a square or pulse wave, the bass a triangle and the drum "
           "noise, and that each chord’s arpeggio uses the right notes (page @ARPS).",
           "Form & Length (rubric row 4): compare the project with the Layer map (page @LAYERS) and check the arithmetic: bars × 240 ÷ tempo "
           "must be between 45 and 75 seconds.",
           "Plan & Reflection (rubric row 5): My plan (page @PLAN), the feedback questions and the Reflection page (page @REFLECT) are the evidence."]
PACING = [
    {"n": 1, "owner": "Read the chart, fill in My plan, and enter the melody.",
     "do": "Slides 1–6: the hook, what the project is, the four classes, the five moves and how to read a piano roll. Hand out the project "
           "sheet, the three chart pages and My plan. Check that every student has a tempo and has started the melody before they leave.",
     "slides": (1, 6), "pages": ["chart1", "chart2", "chart3", "plan", "proj1", "proj2", "proj3", "vocab"],
     "deck": "A carol in 8 bits · five moves · reading a piano roll"},
    {"n": 2, "owner": "Build the channels: arpeggios, bass and the chip sounds.",
     "do": "Slides 7–9: the four chip waves, arpeggios and the sound-building steps. Demonstrate a square-wave track and the Arpeggiator on the "
           "projector, then work time. Walk the room with one question: which channel is playing that note?",
     "slides": (7, 9), "pages": ["channels", "arps"], "deck": "Four channels · arpeggios · build the sound"},
    {"n": 3, "owner": "Add the noise drum and the Bitcrusher, then plan the form and arrange.",
     "do": "Slides 10–11: the noise drum patterns and the worked example on paper. Hand out the Layer map. Then work time; ask each student to "
           "play their first 20 seconds and say which carol they hear.",
     "slides": (10, 11), "pages": ["drums", "layers"], "deck": "Noise drum patterns · worked example, 66 seconds"},
    {"n": 4, "owner": "Bounce, hand in, present and reflect.",
     "do": "Slides 12–15: what to turn in, the rubric, presentation day and the close. Students bounce, name their files and write "
           "their three feedback questions, then present.",
     "slides": (12, 15), "pages": ["rubric", "present", "reflect"], "deck": "Checklist · rubric · presentations"},
]
PACING_EXTRA = (
    '<div class="cols" style="margin-top:4pt;gap:14pt"><div class="box acc-b"><span class="k">The one thing to do on Class 1</span>'
    '<p style="margin:0;font-size:9.6pt">Make sure every student leaves with a tempo from 120 to 150 BPM, a project in 4/4 and the first '
    'five bars of the melody entered. If the tempo is only a guess, tap it: tap a steady beat for ten seconds and count the taps.</p></div>'
    '<div class="box"><span class="k">If you only have three classes</span><p style="margin:0;font-size:9.6pt">Merge Classes 2 and 3: '
    'build the arpeggios, bass and drum on Class 2, then arrange and mix on Class 3 and use Class 4 for bouncing, presentations and reflection.</p></div></div>')
PACING_SIZE = 9.6


# ================================================================ the carol: stored three times, checked against each other
# Lengths are in sixteenth notes: 1 = sixteenth, 2 = eighth, 3 = dotted eighth, 4 = quarter, 6 = dotted quarter, 8 = half,
# 12 = dotted half, 16 = whole. "R" is a rest. One chart bar = one bar of 4/4 = 16 sixteenths.
LEN_NAMES = {1: "16th", 2: "eighth", 3: "dotted eighth", 4: "quarter", 6: "dotted quarter", 8: "half", 12: "dotted half", 16: "whole"}
_PC = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
BLACK_PC = {1, 3, 6, 8, 10}


def midi(p):
    acc = 0 if len(p) == 2 else (1 if p[1] == "#" else -1)
    return 12 * (int(p[-1]) + 1) + _PC[p[0]] + acc


def pname(m):
    return NAMES[m % 12] + str(m // 12 - 1)


# Transcription A (as typed, G major, ABC notation with a default length of a quarter note): the melody of the Open Hymnal Project's
# setting of "A Hymnal" (Episcopal, 1916), hymn 72. The first bar is the one-beat pickup; the last is a three-beat bar.
SRC_A = {"key": "G", "sharps": {"F"}, "unit": 4,
         "text": "G | G2 D G | A2 D2 | B A B c | B2 A G | G2 F E | F G A B | F2 E3/2 D/ | D3 z | d2 c B | c2 B2 | A B G A | F3/2 E/ D G | "
                 "G F G A | G2 D B | B A B c | B2 A B | c B A G | F2 G c | B2 A3/2 G/ | G3"}
# Transcription B (as typed, C major, ABC notation with a default length of a sixteenth): a second, independent transcription of the same tune.
SRC_B = {"key": "C", "sharps": set(), "unit": 1,
         "text": "c4 | c8 G4 c4 | d8 G8 | e4 d4 e4 f4 | e8 d4 c4 | c8 B4 A4 | B4 c4 d4 e4 | B8 A6 G2 | G12 z4 | g8 f4 e4 | f8 e8 | "
                 "d4 e4 c4 d4 | B6 A2 G4 c4 | c4 B4 c4 d4 | c8 G4 e4 | e4 d4 e4 f4 | e8 d4 e4 | f4 e4 d4 c4 | B8 c4 f4 | e8 d6 c2 | c12"}
SHIFT = 5       # the chart is the transcription in G moved UP five semitones (a perfect fourth): G major becomes C major


def parse_abc(src):
    """ABC bars -> [[(pitch name or 'R', sixteenths)]]; upper case letters are octave 4, lower case octave 5; the key's sharps apply."""
    bars = []
    for bar in src["text"].split("|"):
        notes = []
        for tok in bar.split():
            m = re.fullmatch(r"([A-Ga-gz])(\d*)(/?)(\d*)", tok)
            if not m:
                raise ValueError(f"cannot read ABC token {tok!r}")
            ltr, num, slash, den = m.groups()
            mult = (int(num or 1) / int(den or 2)) if slash else int(num or 1)
            length = src["unit"] * mult
            if length != int(length):
                raise ValueError(f"fractional length in {tok!r}")
            if ltr == "z":
                notes.append(("R", int(length)))
                continue
            oct_ = 5 if ltr.islower() else 4
            L = ltr.upper()
            notes.append((L + ("#" if L in src["sharps"] else "") + str(oct_), int(length)))
        bars.append(notes)
    return bars


def moved(bars, semis):
    return [[(p if p == "R" else pname(midi(p) + semis), d) for p, d in bar] for bar in bars]


# The chart the students use (C major). Chart bar 1 is the pickup bar; chart bar n is bar n-1 of a hymn book.
CHART = [
    [("R", 12), ("C5", 4)],
    [("C5", 8), ("G4", 4), ("C5", 4)],
    [("D5", 8), ("G4", 8)],
    [("E5", 4), ("D5", 4), ("E5", 4), ("F5", 4)],
    [("E5", 8), ("D5", 4), ("C5", 4)],
    [("C5", 8), ("B4", 4), ("A4", 4)],
    [("B4", 4), ("C5", 4), ("D5", 4), ("E5", 4)],
    [("B4", 8), ("A4", 6), ("G4", 2)],
    [("G4", 12), ("R", 4)],
    [("G5", 8), ("F5", 4), ("E5", 4)],
    [("F5", 8), ("E5", 8)],
    [("D5", 4), ("E5", 4), ("C5", 4), ("D5", 4)],
    [("B4", 6), ("A4", 2), ("G4", 4), ("C5", 4)],
    [("C5", 4), ("B4", 4), ("C5", 4), ("D5", 4)],
    [("C5", 8), ("G4", 4), ("E5", 4)],
    [("E5", 4), ("D5", 4), ("E5", 4), ("F5", 4)],
    [("E5", 8), ("D5", 4), ("E5", 4)],
    [("F5", 4), ("E5", 4), ("D5", 4), ("C5", 4)],
    [("B4", 8), ("C5", 4), ("F5", 4)],
    [("E5", 8), ("D5", 6), ("C5", 2)],
    [("C5", 12), ("R", 4)],
]
NBARS = len(CHART)
SECTIONS = [("Verse", 1, 9), ("Bridge", 10, 13), ("Chorus", 14, 21)]       # chart bars; the verse starts with the pickup bar
SYSTEMS = [(0, 5), (5, 9), (9, 13), (13, 17), (17, 21)]                     # chart bars 1-5, 6-9, 10-13, 14-17, 18-21 (0-based, end open)

# Chords: per chart bar, [(length in sixteenths, chord)] spanning the bar. One idea that fits, not the only one.
CH = [[(16, "C")], [(16, "C")], [(16, "G")], [(8, "C"), (8, "Am")], [(8, "C"), (8, "G")], [(8, "C"), (4, "G"), (4, "Am")],
      [(8, "Em"), (8, "G")], [(16, "G")], [(16, "G7")], [(8, "C"), (4, "G7"), (4, "C")], [(8, "F"), (8, "C")], [(8, "Dm"), (8, "Am")],
      [(12, "G7"), (4, "C")], [(12, "C"), (4, "G")], [(16, "C")], [(8, "C"), (8, "Am")], [(8, "C"), (4, "G"), (4, "C")],
      [(4, "F"), (4, "C"), (4, "G"), (4, "C")], [(8, "G"), (4, "C"), (4, "F")], [(8, "C"), (8, "G7")], [(16, "C")]]

# ---- chords of C major, spelled by stacking thirds in the scale (computed, then compared with the printed names)
C_SCALE = ["C", "D", "E", "F", "G", "A", "B"]
C_SEMI = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
CHORDS = {   # name: (scale degree of the root, number of notes, Roman numeral, quality)
    "C": (0, 3, "I", "major"), "Dm": (1, 3, "ii", "minor"), "Em": (2, 3, "iii", "minor"), "F": (3, 3, "IV", "major"),
    "G": (4, 3, "V", "major"), "Am": (5, 3, "vi", "minor"), "G7": (4, 4, "V7", "dominant seventh")}
CHORD_ORDER = ["C", "Dm", "Em", "F", "G", "G7", "Am"]


def chord_letters(name):
    r, n, _, _ = CHORDS[name]
    return [C_SCALE[(r + 2 * i) % 7] for i in range(n)]


def chord_midi(name, oct_=3):
    """The chord's notes rising from the root in octave oct_ (C3 = 48, the octave below the lead)."""
    out, prev = [], None
    for L in chord_letters(name):
        m = 12 * (oct_ + 1) + C_SEMI[L]
        if prev is not None and m <= prev:
            m += 12
        out.append(m)
        prev = m
    return out


def chord_semis(name):
    ms = chord_midi(name)
    return [m - ms[0] for m in ms]


CHORD_TONES = {k: set(chord_letters(k)) for k in CHORDS}
BASS_ROOT = {k: pname(12 * 3 + C_SEMI[chord_letters(k)[0]]) for k in CHORDS}     # triangle bass: roots in octave 2 (C2 = 36)

# ---- arpeggio patterns: Arpeggiator note orders at a 1/16 rate, one bar = 16 steps
ARPS = [("up", "Up", "Note Order: Up · Rate 1/16", "Climbs through the chord and starts again. The classic, driving game sound."),
        ("down", "Down", "Note Order: Down · Rate 1/16", "Falls through the chord. It feels calmer and sounds good under a held lead note."),
        ("updown", "Up & Down", "Note Order: Up & Down · Rate 1/16", "Climbs, then falls, so the top and bottom notes are played once per turn. It bounces."),
        ("up2", "Up, two octaves", "Note Order: Up · Octave Range 2 · Rate 1/16", "Climbs through the chord, then through the same notes an octave higher, then repeats. It sparkles.")]


def arp_seq(name, kind, steps=16):
    t = chord_midi(name)
    n = len(t)
    if kind == "up":
        cyc = t
    elif kind == "down":
        cyc = t[::-1]
    elif kind == "updown":
        cyc = t + t[-2:0:-1]
    elif kind == "up2":
        cyc = t + [x + 12 for x in t]
    else:
        raise ValueError(kind)
    return [cyc[i % len(cyc)] for i in range(steps)]


# ---- noise drum patterns: 16 sixteenth steps (4 per beat)
LANES = ["Hat", "Snare", "Kick"]
PATTERNS = [
    dict(key="a", name="Pattern A · March", feel="steady, like a game level",
         pat={"Hat": "x.x.x.x.x.x.x.x.", "Snare": "....x.......x...", "Kick": "x.......x......."},
         drums="Kick on beats 1 and 3; snare on beats 2 and 4; hat on every eighth note.",
         noise="A very short burst for the hat, a longer burst for the snare and a short, very low burst for the kick.",
         tryit="Turn the hat down until the snare and the lead are clear."),
    dict(key="b", name="Pattern B · Run", feel="busy, for a chorus",
         pat={"Hat": "xxxxxxxxxxxxxxxx", "Snare": "....x.......x...", "Kick": "x.....x.x......."},
         drums="Kick on beat 1, the “and” of 2 and beat 3; snare on beats 2 and 4; hat on every sixteenth note.",
         noise="The same three sounds as A; make the hat very quiet or it will cover the arpeggio.",
         tryit="Draw the hats with softer velocities between the beats."),
    dict(key="c", name="Pattern C · Fill", feel="the last bar of a phrase",
         pat={"Hat": "x.x.x.x.x.x.....", "Snare": "....x.......xxxx", "Kick": "x.......x......."},
         drums="Kick on beats 1 and 3; snare on beat 2, then four sixteenth notes in beat 4 (a roll); hat on eighths until beat 3 ends.",
         noise="Ramp the snare roll’s velocity up from soft to loud.",
         tryit="Use this bar only as the last bar of a section, then go back to A or B."),
    dict(key="d", name="Pattern D · Sparse", feel="for intros and the bridge",
         pat={"Hat": "x...x...x...x...", "Snare": "........x.......", "Kick": "x..............."},
         drums="Kick on beat 1 only; snare on beat 3; hat on every quarter note.",
         noise="Soft and spacious: the shortest hat, a quiet snare.",
         tryit="Use it for the intro and the bridge, then bring in A for the chorus.")]


def pattern(key):
    return next(p for p in PATTERNS if p["key"] == key)


def hits(p, ln):
    return [i for i, c in enumerate(p["pat"][ln]) if c == "x"]


# ---- tempo and length
LEN_BPMS = (120, 130, 140, 150)
LEN_BARS = (31, 33, 35)
LEN_EXPECT = [62.0, 57.2, 53.1, 49.6, 66.0, 60.9, 56.6, 52.8, 70.0, 64.6, 60.0, 56.0]

# ---- the worked example: the carol as a 33-bar chiptune at 120 BPM (2 seconds a bar) = 66 seconds
EX_BPM = 120
EX_BAR_S = bar_s(EX_BPM)
EX_SECTIONS = [("Intro", 1, 4), ("Verse", 5, 13), ("Bridge", 14, 17), ("Chorus", 18, 25), ("Chorus again", 26, 33)]
EX_BARS = EX_SECTIONS[-1][2]
EX_INTRO = ["C", "Am", "F", "G"]            # the intro's chords, one a bar (I vi IV V), arriving on the C of the pickup bar
EX_CH = [("1", "Lead", "Square wave, one note at a time", [(5, 33)],
          "the carol from the pickup bar (bar 5); the last chorus is the same notes an octave higher"),
         ("2", "Arps", "Pulse wave, Arpeggiator", [(1, 33)],
          "the chords as arpeggios: Up at 1/16 in the intro and chorus, Up & Down at 1/16 in the verse and bridge"),
         ("3", "Bass", "Triangle wave", [(3, 33)], "the chord roots, one long note per chord, from bar 3"),
         ("4", "Noise drum", "Noise, short bursts", [(14, 33)],
          "pattern D in the bridge, pattern A in the chorus, pattern C as the last bar of each chorus")]
EX_AUTO = [("Bitcrusher", "mix", [(1, .9), (5, .5), (14, .4), (18, .3), (26, .6), (33, .8)]),
           ("Arps", "volume", [(1, .8), (5, .35), (14, .3), (18, .45), (26, .7), (33, .5)])]
EX_WEAK = "I will make O Come All Ye Faithful sound like a video game."
EX_STRONG = ("My arrangement is the carol on a square-wave lead at 120 BPM in 4/4, 33 bars = 66 seconds. The arps play the chords as arpeggios on a "
             "pulse wave, the triangle bass plays the roots, and a noise drum comes in at the bridge. The intro is C | Am | F | G. The "
             "Bitcrusher is strongest in the intro and the last chorus, and the last chorus is an octave higher. The sections are 4 + 9 + 4 + 8 + 8 bars.")
EX_QUESTIONS = ["Which channel did you hear first, and what did it play?",
                "When did you know which carol it was?",
                "Where did the Bitcrusher change the sound most?"]
EX_MOMENTS = [(5, "the pickup bar: the square lead enters on beat 4"), (14, "the bridge: the noise drum enters, pattern D"),
              (18, "the chorus: pattern A and the full four channels"), (26, "the last chorus: the lead an octave higher")]


def ex_density(bar):
    return sum(1 for *_x, spans, _d in EX_CH if any(a <= bar <= b for a, b in spans))


EX_DENS = [ex_density(b) for b in range(1, EX_BARS + 1)]


def tune_notes():
    """Flat list of (pitch, start, length) in sixteenths from the first chart bar (rests are skipped, but they take time)."""
    out, t = [], 0
    for bar in CHART:
        for p, d in bar:
            if p != "R":
                out.append((p, t, d))
            t += d
    return out


def note_count():
    return sum(1 for b in CHART for p, _ in b if p != "R")


def bar_text(bar):
    return " · ".join(f"rest {LEN_NAMES[d]}" if p == "R" else f"{p} {LEN_NAMES[d]}" for p, d in bar)


def chord_text(spans):
    return " · ".join(c for _, c in spans)


# ================================================================ drawings (all in code, labels logged for the fit check)
def padded(body, W, H, M=6):
    """Wrap a drawing's body with M units of clear padding on all four sides (wider than the thickest outer stroke), so no edge pixel is ever inked."""
    return f'<g transform="translate({M},{M})">{body}</g>', W + 2 * M, H + 2 * M


def roll_body(notes, nsteps, bar_len, beat, lo, hi, W=1100, row_h=24, first_bar=1, chords=None, name="roll", hl=None, key_w=80, head=30,
              labels=True, fs_note=None, bar_nums=True):
    """A piano roll: rows are pitches lo..hi (MIDI numbers, black-key rows grey), columns are sixteenth notes, bars in bold, beats in
    grey. notes = [(pitch name, start, length)]; chords = [(start, length, name)]. Returns (svg body, w, h)."""
    cw = (W - key_w - 4) / nsteps
    rows = hi - lo + 1
    gh = rows * row_h
    x0 = key_w
    out = []
    for r in range(rows):
        m = hi - r
        y = head + r * row_h
        black = m % 12 in BLACK_PC
        out.append(f'<rect x="{x0}" y="{y}" width="{nsteps * cw:.1f}" height="{row_h}" fill="{"#e3e3e3" if black else "#fff"}" stroke="#bdbdbd" stroke-width="0.6"/>')
        out.append(f'<rect x="0" y="{y}" width="{key_w}" height="{row_h}" fill="#fff" stroke="#000" stroke-width="1"/>')
        nm = pname(m)
        fsz = min(15, row_h - 5)
        if black:
            out.append(f'<rect x="0" y="{y + 1}" width="{key_w * 0.5:.1f}" height="{row_h - 2}" fill="#000"/>')
            if labels and row_h >= 16:
                out.append(D.t_(key_w - 6, y + row_h / 2 + fsz * .35, nm, fsz - 2, 500, anchor="end", fill_="#444"))
                D.lab(name + " keys", nm, fsz - 2, key_w * 0.5 - 6)
        elif row_h >= 14 and (labels or m % 12 == 0):
            out.append(D.t_(key_w - 8, y + row_h / 2 + fsz * .35, nm, fsz, 500, anchor="end", fill_=ACCENT if m % 12 == 0 else "#000"))
            D.lab(name + " keys", nm, fsz, key_w - 14)
    for s in range(nsteps + 1):
        x = x0 + s * cw
        if s % bar_len == 0:
            out.append(f'<line x1="{x:.1f}" y1="{head - 4}" x2="{x:.1f}" y2="{head + gh}" stroke="#000" stroke-width="3"/>')
        elif s % beat == 0:
            out.append(f'<line x1="{x:.1f}" y1="{head}" x2="{x:.1f}" y2="{head + gh}" stroke="#7a7a7a" stroke-width="1.1"/>')
        elif s % 2 == 0:
            out.append(f'<line x1="{x:.1f}" y1="{head}" x2="{x:.1f}" y2="{head + gh}" stroke="#d6d6d6" stroke-width=".6"/>')
    nb = nsteps // bar_len
    if bar_len and bar_nums:
        for b in range(nb):
            out.append(D.t_(x0 + (b + .5) * bar_len * cw, head - 9, str(first_bar + b), 18, 700))
            D.lab(name + " bars", str(first_bar + b), 18, bar_len * cw - 6)
    fs = fs_note or min(row_h - 9, 16)
    for p, s, d in notes:
        r = hi - midi(p)
        assert 0 <= r < rows, (p, lo, hi)
        x, y, w, h = x0 + s * cw + 1.2, head + r * row_h + 2.5, d * cw - 2.4, row_h - 5
        out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="4" fill="{ACCENT if hl and hl(p) else "#000"}"/>')
        txt = p[:-1]
        if labels and fs >= 9 and w >= D.text_w(txt, fs) + 8:
            out.append(D.t_(x + w / 2, y + h / 2 + fs * .35, txt, fs, 700, fill_="#fff"))
            D.lab(name + " notes", txt, fs, w - 6)
    out.append(f'<rect x="{x0}" y="{head}" width="{nsteps * cw:.1f}" height="{gh}" fill="none" stroke="#000" stroke-width="2"/>')
    H = head + gh + 8
    if chords:
        yc = head + gh + 10
        out.append(D.t_(key_w - 8, yc + 24, "CHORDS", 14, 700, anchor="end", fill_=ACCENT))
        D.lab(name + " keys", "CHORDS", 14, key_w - 14)
        for s, d, ch in chords:
            out.append(f'<rect x="{x0 + s * cw + 2:.1f}" y="{yc}" width="{d * cw - 4:.1f}" height="34" rx="6" fill="{ACC_LIGHT}" stroke="{ACCENT}" stroke-width="2"/>')
            fz = 20 if D.text_w(ch, 20) <= d * cw - 14 else 16
            out.append(D.t_(x0 + (s + d / 2) * cw, yc + 24, ch, fz, 700))
            D.lab(name + " chords", ch, fz, d * cw - 8)
        H = yc + 44
    return padded("".join(out), W, H, 3)


LO, HI = 67, 79           # the carol's rows: G4 to G5


def tune_roll(a, b, W=1100, name=None, chords=True, row_h=20):
    """Chart bars a..b-1 (0-based) as a roll, with the chords."""
    nts = [(p, s - a * 16, d) for p, s, d in tune_notes() if a * 16 <= s < b * 16]
    chs, t = [], 0
    for i in range(a, b):
        for ln, ch in CH[i]:
            chs.append((t, ln, ch))
            t += ln
    return roll_body(nts, (b - a) * 16, 16, 4, LO, HI, W, row_h, a + 1, chs if chords else None, name or f"roll {a}-{b}")


def cards_body(items, cap, W=1600, name="cards", fs=30, cs=22):
    n = len(items)
    gap = 74
    pw = (W - (n - 1) * gap) / n
    bh = 190
    out = []
    for k, (h, s) in enumerate(items):
        x0 = k * (pw + gap)
        out.append(f'<rect x="{x0:.1f}" y="4" width="{pw:.1f}" height="{bh}" rx="12" fill="{"#000" if k % 2 == 0 else ACCENT}"/>')
        out.append(D.t_(x0 + pw / 2, 4 + bh / 2 - 6, h.upper(), fs, 700, fill_="#fff"))
        D.lab(name + " heads", h.upper(), fs, pw - 30)
        out.append(D.t_(x0 + pw / 2, 4 + bh / 2 + 38, s, cs, 500, fill_="#fff"))
        D.lab(name + " subs", s, cs, pw - 30)
        out.append(D.t_(x0 + 24, 4 + 40, str(k + 1), 28, 700, anchor="start", fill_="#fff"))
        if k < n - 1:
            ax, ay = x0 + pw + 10, 4 + bh / 2
            out.append(f'<line x1="{ax:.1f}" y1="{ay:.1f}" x2="{ax + gap - 36:.1f}" y2="{ay:.1f}" stroke="#000" stroke-width="6" stroke-linecap="round"/>')
            out.append(f'<polygon points="{ax + gap - 16:.1f},{ay:.1f} {ax + gap - 40:.1f},{ay - 15:.1f} {ax + gap - 40:.1f},{ay + 15:.1f}" fill="#000"/>')
    out.append(D.t_(W / 2, bh + 56, cap, cs + 2, 500))
    D.lab(name + " cap", cap, cs + 2, W - 20)
    return padded("".join(out), W, bh + 72)


def cycle_body(W=1600, name="cycle pic", fs=30, cs=22):
    return cards_body([("Read", "the chart"), ("Plan", "four channels"), ("Enter", "the melody"), ("Layer", "arps, bass, drum"),
                       ("Crush", "lo-fi + arrange")], "Then mix, bounce, present and reflect", W, name, fs, cs)


def wave_pts(kind, x0, y0, w, h, cycles=2, pad=28):
    """Points of a waveform inside the box (x0, y0, w, h): at least `pad` clear of every edge (the stroke is 6)."""
    X0, X1, Yt, Yb = x0 + pad, x0 + w - pad, y0 + pad, y0 + h - pad
    ym = (Yt + Yb) / 2
    cw = (X1 - X0) / cycles
    pts = []
    if kind in ("square", "pulse"):
        duty = .5 if kind == "square" else .25
        for c in range(cycles):
            xa = X0 + c * cw
            pts += [(xa, Yb), (xa, Yt), (xa + cw * duty, Yt), (xa + cw * duty, Yb)]
        pts.append((X1, Yb))
    elif kind == "triangle":
        for c in range(cycles):
            xa = X0 + c * cw
            pts += [(xa, ym), (xa + cw / 4, Yt), (xa + 3 * cw / 4, Yb)]
        pts.append((X1, ym))
    else:       # noise: the same pseudo-random points every build
        seed, n = 12345, 34
        for i in range(n + 1):
            seed = (seed * 1103515245 + 12345) % (2 ** 31)
            pts.append((X0 + (X1 - X0) * i / n, Yt + (Yb - Yt) * (seed % 1000) / 1000))
    return pts


WAVES = [("square", "Square", "Channel 1 · lead"), ("pulse", "Pulse 25%", "Channel 2 · arps"), ("triangle", "Triangle", "Channel 3 · bass"),
         ("noise", "Noise", "Channel 4 · drum")]


def waves_body(W=1600, name="waves pic", fs=34, cs=24, gap=36):
    n = len(WAVES)
    pw = (W - (n - 1) * gap) / n
    bh = 250
    out = []
    for k, (kind, head, sub) in enumerate(WAVES):
        x0 = k * (pw + gap)
        out.append(f'<rect x="{x0:.1f}" y="4" width="{pw:.1f}" height="{bh}" rx="12" fill="#fff" stroke="#000" stroke-width="4"/>')
        ym = 4 + bh / 2
        out.append(f'<line x1="{x0 + 28:.1f}" y1="{ym:.1f}" x2="{x0 + pw - 28:.1f}" y2="{ym:.1f}" stroke="#b5b5b5" stroke-width="2" stroke-dasharray="6 8"/>')
        pts = wave_pts(kind, x0, 4, pw, bh)
        out.append(f'<polyline points="{" ".join(f"{a:.1f},{b:.1f}" for a, b in pts)}" fill="none" stroke="{ACCENT if k % 2 else "#000"}" '
                   f'stroke-width="6" stroke-linejoin="round" stroke-linecap="round"/>')
        out.append(D.t_(x0 + pw / 2, 4 + bh + 46, head.upper(), fs, 700))
        D.lab(name + " heads", head.upper(), fs, pw - 20)
        out.append(D.t_(x0 + pw / 2, 4 + bh + 46 + 38, sub, cs, 500))
        D.lab(name + " subs", sub, cs, pw - 20)
    M = 14      # padding on all four sides: wider than the 4-unit tile stroke (2 units spill outside each tile) and the 6-unit wave stroke
    return f'<g transform="translate({M},{M})">{"".join(out)}</g>', W + 2 * M, bh + 4 + 46 + 38 + 10 + 2 * M


def arps_roll(name="C", kind="up", W=1100, nm="arp roll", row_h=30, steps=16, labels=True):
    seq = arp_seq(name, kind, steps)
    lo, hi = min(seq), max(seq)
    notes = [(pname(m), i, 1) for i, m in enumerate(seq)]
    return roll_body(notes, steps, 16, 4, lo, hi, W, row_h, 1, [(0, 16, name)], nm, labels=labels, key_w=70, head=8, bar_nums=False)


def arps_body(W=1100, name="arps pic"):
    return arps_roll("C", "up", W, name, 34)


def grid_for(p, name=None):
    meas = [{ln: p["pat"][ln] for ln in LANES}]
    return D.grid_body(name or f"grid {p['key']}", meas, [p["name"].split(" · ")[1]], LANES, cw=26, ch=26, gut=100, ls=20, accent_from=0)


def blank_grid(name="grid blank"):
    return D.grid_body(name, [{}], ["My pattern"], LANES, cw=26, ch=26, gut=100, ls=20, accent_from=0, blank=True)


def drums_body(name="drums pic"):
    a = grid_for(pattern("a"), name=name + " a")
    c = grid_for(pattern("c"), name=name + " c")
    cap = "Pattern A (march), then pattern C (fill)"
    D.lab(name + " cap", cap, 20, 500)
    return D.stack([a, c, (D.t_(260, 22, cap, 20, 500), 520, 34)], 14)


def hero_body():
    """The owner's pre-made art (art/hero.png, used whole). The viewBox only trims fully transparent margin: the art's own pixels
    (x 244-1155, y 93-1325 of 1400) stay at least 50 units inside it, which --check proves from the file."""
    return (f'<image href="../art/hero.png" x="{-HX}" y="{-HY}" width="1400" height="1400"/>', HW, HH)


HX, HY, HW, HH = 190, 40, 1020, 1340


def map_body(W=1600, name="map", fs=24, ts=20):
    """The worked example's whole 33-bar arrangement: sections, four channels and two automation lanes."""
    gx = 300
    pwid = W - gx - 16

    def X(bar):
        return gx + pwid * (bar - 1) / EX_BARS

    out = []
    sh = 54
    shade = {"Intro": "#4a4a4a", "Verse": "#000", "Bridge": "#4a4a4a", "Chorus": ACCENT, "Chorus again": ACCENT}
    for nm, a, b in EX_SECTIONS:
        out.append(f'<rect x="{X(a) + 2:.1f}" y="2" width="{X(b + 1) - X(a) - 4:.1f}" height="{sh}" rx="8" fill="{shade[nm]}"/>')
        sz = fs - 4
        while D.text_w(nm.upper(), sz) > X(b + 1) - X(a) - 14 and sz > 12:
            sz -= 1
        out.append(D.t_((X(a) + X(b + 1)) / 2, sh / 2 + sz * .3 + 2, nm.upper(), sz, 700, fill_="#fff"))
        D.lab(name + " sections", nm.upper(), sz, X(b + 1) - X(a) - 10)
    lh, lg = 34, 8
    y0 = sh + 14
    out.append(D.t_(gx - 14, y0 + 6, "CHANNELS", fs - 6, 700, anchor="end", fill_=ACCENT))
    for i, (num, nm, _w, spans, _d) in enumerate(EX_CH):
        yy = y0 + 16 + i * (lh + lg)
        lbl = f"{num} {nm}".upper()
        out.append(D.t_(gx - 14, yy + lh / 2 + 7, lbl, 20, 700, anchor="end"))
        D.lab(name + " lanes", lbl, 20, gx - 24)
        out.append(f'<rect x="{gx}" y="{yy}" width="{pwid:.1f}" height="{lh}" fill="#fff" stroke="#000" stroke-width="1.2"/>')
        for a, b in spans:
            out.append(f'<rect x="{X(a):.1f}" y="{yy + 4}" width="{X(b + 1) - X(a):.1f}" height="{lh - 8}" rx="6" fill="#bdbdbd" stroke="#000" stroke-width="2"/>')
    ay0 = y0 + 16 + len(EX_CH) * (lh + lg) + 8
    out.append(D.t_(gx - 14, ay0 + 6, "AUTOMATION", fs - 6, 700, anchor="end", fill_=ACCENT))
    D.lab(name + " lanes", "AUTOMATION", fs - 6, gx - 24)
    for i, (ly, par, pts) in enumerate(EX_AUTO):
        yy = ay0 + 16 + i * (lh + lg + 6)
        lbl = f"{ly} · {par}".upper()
        out.append(D.t_(gx - 14, yy + lh / 2 + 7, lbl, 18, 700, anchor="end"))
        D.lab(name + " lanes", lbl, 18, gx - 24)
        out.append(f'<rect x="{gx}" y="{yy}" width="{pwid:.1f}" height="{lh + 6}" fill="#fff" stroke="#000" stroke-width="1.2"/>')
        xy = [(X(t), yy + lh + 2 - v * (lh - 2)) for t, v in pts]
        out.append(f'<polyline points="{" ".join(f"{a:.1f},{b:.1f}" for a, b in xy)}" fill="none" stroke="{ACCENT}" stroke-width="4" stroke-linejoin="round"/>')
        for a, b in xy:
            out.append(f'<circle cx="{a:.1f}" cy="{b:.1f}" r="4.5" fill="#000"/>')
    ty = ay0 + 16 + len(EX_AUTO) * (lh + lg + 6) + 4
    ticks = (1, 5, 9, 13, 17, 21, 25, 29, EX_BARS + 1)
    for bar in ticks:
        t = (bar - 1) * EX_BAR_S
        lbl = mmss(t)
        anc = "start" if bar == 1 else ("end" if bar == EX_BARS + 1 else "middle")
        xx = X(bar)
        out.append(f'<line x1="{xx:.1f}" y1="{ty - 6}" x2="{xx:.1f}" y2="{ty + 8}" stroke="#000" stroke-width="2"/>')
        out.append(D.t_(xx + (2 if bar == 1 else (-2 if bar == EX_BARS + 1 else 0)), ty + 8 + ts, lbl, ts, 500, anchor=anc))
        D.lab(name + " ticks", lbl, ts, 70)
    cap = f"Bar 1 to bar {EX_BARS} at {EX_BPM} BPM: {EX_BARS} bars × {EX_BAR_S:g} seconds = {EX_BARS * EX_BAR_S:g} seconds"
    out.append(D.t_(gx + pwid / 2, ty + 8 + ts + 34, cap, ts + 2, 500))
    D.lab(name + " cap", cap, ts + 2, pwid)
    return padded("".join(out), W, ty + 8 + ts + 48)


DRAWINGS = {"hero": hero_body, "cycle": lambda: cycle_body(1600), "roll": lambda: tune_roll(0, 5, 1100, "roll deck"),
            "waves": lambda: waves_body(1600, "waves deck"), "arps": lambda: arps_body(1100, "arps deck"),
            "drums": lambda: drums_body(), "map": lambda: map_body(1600, "map pic")}
DRAWING_PX = {"hero": 1020, "cycle": 2000, "roll": 2000, "waves": 2000, "arps": 2000, "drums": 2000, "map": 2000}
SIDE = {"cycle": ["Read the chart and plan your tempo", "Enter the melody on a square wave", "Layer arps, bass and a noise drum",
                  "Crush it, arrange it, then bounce"],
        "roll": ["Higher bar means higher pitch", "Longer bar means a longer note", "Left to right is time, bar by bar",
                 "Bar 1 is the pickup bar"],
        "waves": ["Each channel plays one note at a time", "Square and pulse are bright and buzzy", "Triangle is soft and round",
                  "Noise has no pitch: it is the drum"],
        "arps": ["A chord’s notes, one after another", "Up climbs through C, E and G", "One bar at 1/16 is 16 notes",
                 "The Arpeggiator plug-in does it for you"],
        "drums": ["Hat, snare and kick are all noise", "Shaded columns are the beats", "Pattern C ends with a snare roll",
                  "Draw one bar, then loop it"],
        "map": ["An invented 66-second arrangement", "Five sections: 4, 9, 4, 8 and 8 bars", "Four channels, two automation lanes",
                "Every channel is on in the last 20 bars"]}


def label_extras():
    for a, b in SYSTEMS:
        tune_roll(a, b, 1100, f"page roll {a}")
    waves_body(1100, "page waves", 26, 19, 24)
    for kind, *_ in ARPS:
        arps_roll("C", kind, 560, "page arp card", 25, labels=kind != "up2")
    map_body(1250, "page map", 24, 20)
    cycle_body(1250, "page cycle", 28, 20)
    roll_body([], 64, 16, 4, 36, 45, 1100, 14, 1, None, "blank bass roll", labels=False)
    roll_body([], 64, 16, 4, 48, 59, 1100, 14, 1, None, "blank arp roll", labels=False)
    for p in PATTERNS:
        grid_for(p)
    blank_grid()


# ================================================================ intro deck: (class, kind, title, body, speaker notes)
SLIDES = [
    (1, "title", "8-Bit Holiday", "A carol, rebuilt as a game tune.",
     "Class 1, the first minute. No audio is included in this deck. Open with the idea: you are going to rebuild a carol, “O Come, All Ye "
     "Faithful”, as an 8-bit game tune in Logic Pro, with a square-wave lead, arpeggios, a triangle bass and a noise drum. The carol is in the "
     "public domain and arrives as a piano-roll note chart, so every student can enter it without reading staff notation."),
    (1, "listen", "What makes music sound 8-bit?", "Think, then share|Teacher: hum the first line of the carol, then again in short, flat, "
     "bleepy notes like a game.|What changed?|Why does it sound like a game?|Which sounds would you use?",
     "Ask the three questions aloud and take a few answers. Nothing is played from a speaker: you hum the first line of the carol yourself, "
     "first smoothly and then in short, flat, bleepy notes. Students will say shorter, simpler, robotic, higher, and maybe “like a "
     "video game”. Write their words on the board; the project turns each one into a tool: a square wave, a fast arpeggio, a bass and a drum."),
    (1, "bullets", "What is 8-Bit Holiday?", "Enter a public-domain carol in Logic Pro|Play it on a square-wave lead|Add arpeggios, a triangle "
     "bass and a noise drum|Crush it into a 45 to 75 second tune",
     "The project in four lines. Every student arranges the same carol, “O Come, All Ye Faithful”; the tune is attributed to John Francis Wade "
     "and is far older than 1930, so anyone may use it. They enter the melody from a piano-roll chart, then build the other three channels of "
     "a classic game-music chip and add a Bitcrusher. The finished tune is 45 to 75 seconds. If a student would rather use another "
     "public-domain tune, a blank piano roll is provided and you approve the tune."),
    (1, "days", "Four classes", "",
     "The shape of the project. Class 1: hook, read the chart, fill in My plan and enter the melody. Class 2: build the channels, with "
     "arpeggios, a triangle bass and the chip sounds. Class 3: add the noise drum and the Bitcrusher, then plan the form and arrange. Class 4: "
     "bounce, hand in, present and reflect. Hand out the project sheet, the chart pages and My plan now."),
    (1, "pic", "Five moves, then finish", "cycle",
     "Class 1. The five moves in order: read, plan, enter, layer and crush. After that students arrange, mix, bounce, present and reflect. "
     f"Point to each box and say roughly when it happens: reading and planning today, entering the melody today and tomorrow, the layers on "
     f"Class 2 and the lo-fi and the arrangement on Class 3. The picture and its short labels are drawn for this resource. My plan is page {pg('plan')}."),
    (1, "pic", "Reading a piano roll", "roll",
     "Class 1. This is the Piano Roll view of the first five bars of the carol, drawn the same way as the chart on students’ pages "
     f"(page {pg('chart1')}). A higher bar is a higher pitch, a longer bar is a longer note, and time runs left to right. Chart bar 1 is the "
     "pickup bar: three beats of rest, then one note. The chord boxes underneath are the chords of the arrangement; other chords can work."),
    (2, "pic", "Four channels, four waves", "waves",
     "Class 2. A classic game chip had only a few channels, and each plays one note at a time: two pulse (square) waves, a triangle and "
     "noise. The square is bright and buzzy, the narrower pulse is thinner, the triangle is soft and round, and noise has no pitch at "
     f"all, so it plays the drum. Because a channel plays one note at a time, a chord has to be spelled out as an arpeggio. Students read "
     f"the cards on page {pg('channels')}."),
    (2, "pic", "Arpeggios: a chord in motion", "arps",
     "Class 2. An arpeggio plays the notes of a chord one after another. This is a C chord, C, E and G, played with the Up order at a 1/16 "
     "rate: one bar is 16 notes. In Logic, put the Arpeggiator plug-in in the MIDI FX slot of the track and hold or draw the chord. "
     f"Students use the chord table and the four patterns on page {pg('arps')}, and a different chord in every bar of the carol."),
    (2, "steps", "Build the sound", "Make a Software Instrument track for each channel|Lead: square wave, one note at a time|Arps: pulse wave "
     "plus the Arpeggiator|Bass: triangle wave on the chord roots|Drum: noise, short for the hat, longer for the snare",
     "Class 2. Demonstrate on the projector: make a Software Instrument track with Retro Synth or Alchemy and pick the square wave, set a "
     "short release, and play the first notes of the chart. Then a second track with a pulse wave and the Arpeggiator in its MIDI FX slot, "
     "and a third with a triangle wave for the bass. The drum comes on Class 3. Menu names move between Logic versions."),
    (3, "pic", "Noise drum patterns", "drums",
     "Class 3. The same 16-step grid in two feels. Pattern A is a march: kick on beats 1 and 3, snare on beats 2 and 4, hat on eighths. "
     f"Pattern C is a fill: the last beat is four snare hits, a roll. Students copy a pattern from page {pg('drums')} into the Step Sequencer "
     "of a Drum Machine Designer track. On a chip all three sounds are noise: a short burst is the hat, a longer one the snare and a short, "
     "very low one the kick."),
    (3, "pic", "A 33-bar arrangement", "map",
     "Class 3. An invented arrangement described on paper; nothing here is audio. Thirty-three bars at 2 seconds a bar is 66 seconds, in five "
     "sections of 4, 9, 4, 8 and 8 bars. The arps play the whole time, the bass joins at bar 3, the lead at bar 5 and the noise drum at the "
     f"bridge. Two automation lanes keep the sound moving. Students plan their own on the Layer map, page {pg('layers')}."),
    (4, "check", "What you turn in", "Bounced .mp3 or .wav|Zipped .logicx project|Named: Your Name – 8-Bit Holiday|My plan, Layer map, "
     "Reflection|Rubric self-score|Three questions for classmates",
     "Class 4. The submission checklist, shortened to fit the slide. Show where students hand in. The file name is Your Name, then "
     "8-Bit Holiday. Check that every arrangement is between 45 and 75 seconds before students bounce: bars times 240 divided by the tempo."),
    (4, "rubric", "How it’s scored", "",
     "The rubric: five categories, each scored 1 to 5, for a total out of 25. Students score themselves first; the final grade is the "
     "average of their score and yours. The slide reads the 5 column of each category aloud. Hand out the rubric page so students can "
     "self-score before they present."),
    (4, "bullets", "Presentation day", "Play your arrangement, then name the carol|Say what each of the four channels plays|Your three "
     "questions for classmates|Answer at least 2 of each classmate’s questions",
     "Class 4, presentations. Each student plays their arrangement, names the carol and says what each of the four channels plays, then takes "
     "questions. Students write three questions they want classmates to answer, and answer at least two of each classmate's. "
     "Ask the class to name the carol before the presenter does."),
    (4, "closer", "One last thing…", "An old tune, rebuilt.|Four channels, all yours.|Lo-fi on purpose.|Now press play.",
     "Close with the listening day: play the finished tunes without saying the title and let the class name the carol. A melody that "
     "people name quickly is an arrangement that kept the tune. Ask a few students which channel changed the mood most. No audio is "
     "included in this resource; the sounds are the students' own."),
]
SHOTS1 = [("pacing", "Pacing guide", "4 class periods, slide by slide"), ("chart1", "Piano-roll chart", "The carol, bar by bar"),
          ("rubric", "Rubric / 25", "student + teacher average")]
SHOTS2 = [1, 6, 7, 8, 10, 11]
SHOTS3 = [("chart1", "Note chart"), ("arps", "Arpeggio cards"), ("channels", "Four channels"), ("drums", "Noise drums"),
          ("chart3", "Chords and bass"), ("example", "Worked example"), ("plan", "My plan"), ("layers", "Layer map")]
PREVIEW_PICKS = ["pacing", "chart1", "arps", "rubric"]

COVER_A = "Rebuild a carol as a game tune"
COVER_C = "Logic Pro · square and triangle waves · arpeggios · intro slides"
PDF_COVER = dict(a=26, b=62, c=14, art=4.3)
SQ_COVER = dict(a=40, b=150, c=27, art=440, gap=26)
SQ_B_LINES = ["8-Bit Holiday"]
SQ_SUB = "4 class periods · a public-domain carol · intro slides"
SQ_HEADS = {1: ("Ready to teach Monday", 76, "Pacing, note charts, arpeggio cards and the /25 rubric in one PDF", 28),
            2: ("Intro deck included", 76, f"{len(SLIDES)} editable slides (.pptx + PDF) with speaker notes on every slide", 28),
            3: ("Everything inside", 72, "Note charts, channels, arpeggio cards, noise drums, a worked example and plans", 28)}
SQ_BANDS = {1: "Read <em>·</em> enter <em>·</em> arpeggios <em>·</em> bass <em>·</em> noise drum",
            2: "Piano roll <em>·</em> four channels <em>·</em> arpeggios <em>·</em> worked example",
            3: f"{len(PLAN)} pages <em>·</em> US Letter PDF <em>·</em> no audio included"}

SONG_NOTE = ("No audio, recordings, lyrics, artists or albums are named or included. The carol is public domain and appears only as a note "
             "chart. Students make every sound in their arrangements themselves, from the instruments, drum kits and plug-ins in Logic.")
CREDITS = ["Piano-roll note charts and chord ideas for the public-domain tune “O Come, All Ye Faithful” (attributed to John Francis Wade, c. 1743), the "
           "arpeggio and noise-drum patterns, the channel cards, the worked example, the waveform, piano-roll, drum and arrangement drawings "
           "and all layouts: original work, Hudson Beat. No lyrics, recordings or published editions are included.",
           "The cover illustration was made with digital and AI tools. No audio, video, album art, screenshots, presets, templates, links or "
           "chart data from other sources are included. No student work is included."]
LOGIC_INTRO = ("Where to find the tools an 8-Bit Holiday arrangement is likely to use. Demonstrate what your class needs on Classes 1 to 3 and then "
               "let students work. Names are from current Logic Pro versions; labels move between versions, so check yours.")
LOGIC_REF = [("New project and tracks", "File › New…, then add a Software Instrument track for each channel with Track › New Tracks…. Name them Lead, Arps, "
              "Bass and Drum so that your Layer map matches (page " + str(pg("layers")) + ")."),
             ("Tempo and time signature", "Type the tempo in the control bar (120 to 150 BPM) and keep 4/4. The chart is in 4/4 too, so nothing "
              "needs to change."),
             ("Make a region, open the Piano Roll", "With the Pencil tool, click on the track where bar 1 starts to make an empty MIDI "
              "region, then double-click it to open the Piano Roll editor."),
             ("Draw notes and chords", "Pick a grid value in the Piano Roll’s Snap menu (for example, 1/16 note) so notes land on the "
              "chart’s sixteenth-note grid, click with the Pencil to add a note and drag its right edge to change its length. Draw a chord as "
              "notes stacked in one column. Logic names middle C “C3” by default; the chart calls it C4, so subtract one from the chart’s octave number when you read the roll."),
             ("Fix wrong notes, move a region", "Select a note and drag it up or down a row, or press delete. To move a whole region, change "
              "Transpose in the Region inspector by a number of semitones (12 is one octave)."),
             ("Square, pulse and triangle sounds", "On a Software Instrument track choose Retro Synth or Alchemy. In Retro Synth, use the Analog "
              "engine and pick a square, pulse or triangle wave for the oscillator (a pulse wave has a pulse width control); Alchemy can do the "
              "same from a basic square or triangle source if your version offers one. If a menu names the waves differently, pick the shape that "
              "matches the picture on page " + str(pg("channels")) + ". Set a short release, no reverb, and Mono if the instrument has that setting."),
             ("Arpeggiator", "Click a MIDI FX slot at the top of the arpeggio track’s channel strip and choose Arpeggiator. Set the Note Order "
              "(Up, Down, Up & Down), the Rate (1/16) and the Octave Range, then play or draw a chord: the plug-in plays its notes one at a time. "
              "Draw the chord as notes stacked in one column of the region (page " + str(pg("arps")) + "). If a setting has a different name in your version, use the closest one."),
             ("Triangle bass", "Another Retro Synth or Alchemy track with a triangle wave, Mono if available and a short release. Play the chord roots, "
              "C2 to A2 (page " + str(pg("chart3")) + ")."),
             ("Noise drum", "Make a Drum Machine Designer track and open its Step Sequencer: click the 16 steps for each sound, as on the patterns on page "
              + str(pg("drums")) + ". Give each pad a very short noise sound; a synthesizer’s noise source with a quick envelope works too, if your instrument has one."),
             ("Bitcrusher and Channel EQ", "Click an Audio FX slot on the channel strip and choose Bitcrusher (look in the Distortion group of the plug-in "
              "menu). Lower Resolution and Downsampling for a grainier sound and set Mix to taste. Put it on one channel, or on the Stereo Out to crush "
              "everything. Add Channel EQ to the lead and the arps and cut the low end they do not need, so the bass owns it."),
             ("Automation, mixing and bounce", "Press A to show automation, pick a parameter such as the Bitcrusher’s Mix or a channel’s Volume, and draw points. "
              "Press X for the Mixer. Then File › Bounce › Project or Section (Command-B), MP3 or WAV. In Finder, Control-click the .logicx "
              "and choose Compress.")]
PRESENT_CHECK = [f"Files named {FILE_NAME}; the .mp3 or .wav and zipped .logicx handed in",
                 "Reflection page done (page @REFLECT)", "Three questions for classmates written",
                 "Rubric self-score done (page @RUBRIC)"]
VOCAB_PROMPT = "Where it shows up in my arrangement:"
TN1_EXTRA = (
    '<div class="box acc-b" style="margin-top:4pt"><span class="k">Where this kit helps with each struggle</span><ul style="margin:0">'
    '<li style="font-size:12pt;margin-bottom:3pt">Wrong notes: the chart pages (pages @CHART1–@CHART3) list every note by bar, and the Logic quick reference (page @LOGICREF) shows the grid.</li>'
    '<li style="font-size:12pt;margin-bottom:3pt">A wrong arpeggio: the chord table and the four patterns (page @ARPS) spell every chord.</li>'
    '<li style="font-size:12pt;margin-bottom:3pt">A sound that is not chip-like: the four channel cards (page @CHANNELS) and the noise drum patterns (page @DRUMS).</li>'
    '<li style="font-size:12pt;margin-bottom:0">A length that is off: the length helper and the Layer map (page @LAYERS) and the worked example (pages @EXAMPLE–@EXAMPLE2).</li></ul></div>')
TN1_SIZE = 12.4
PROJ_SIZE = 12.2
VOCAB_GAP = 14
LOGIC_SIZE = 8.6
PROJ1_EXTRA = ""
RUBRIC_EXTRA = ""


# ================================================================ small page helpers
CSS_SG = ("<style>table.sg { border-collapse: collapse; width: 100%; } table.sg td, table.sg th { border: 1pt solid #000; text-align: center; "
          "padding: 0; font-size: 8pt; } table.sg th { background: #000; color: #fff; font-family: Oswald; font-weight: 500; height: 14pt; } "
          "table.sg td.l { text-align: left; padding: 0 4pt; font-weight: 700; width: 1.2in; font-size: 9pt; } "
          "table.sg td.b { border-left: 2.2pt solid #000; } </style>")


def howto_page(n, wm=False):
    parts = [("Teacher pages", "howto", "example2", "How to use, overview, setup, pacing, teacher notes, Logic quick reference, tune sources, "
              "worked example (2 pages)"),
             ("Student pages", "chart1", "reflect", "Three note-chart pages, four channels, arpeggio cards, noise drum patterns, My plan, Layer map, "
              "project sheet (3 pages), rubric, vocabulary, feedback planner, reflection page"),
             ("Intro deck (separate file)", None, None, f"{len(SLIDES)} slides, .pptx + PDF, speaker notes on every slide")]
    trs = "".join(f"<tr><td><b>{a}</b></td><td style='white-space:nowrap'>{('pages ' + str(D.IX(f)) + '–' + str(D.IX(l))) if f else 'deck'}</td>"
                  f"<td>{u}</td></tr>" for a, f, l, u in parts)
    inner = (f'<div class="cols"><div>'
             f'{D.H2("What this is", True)}'
             f'<p style="font-size:12pt;line-height:1.45">A {CLASSES}-class-period chiptune project for high school music technology. Every '
             f'student arranges the public-domain carol “O Come, All Ye Faithful” as an 8-bit game tune in Logic Pro: they enter its melody '
             f'from a piano-roll note chart on a square-wave lead, then build the other three channels of a classic game-music chip (arpeggiated chords, a '
             f'triangle-wave bass and a noise drum) and crush it with a Bitcrusher. The arrangement is 45 to 75 seconds. Students plan it, build and mix it, '
             f'present it and reflect on it. It is an original Hudson Beat project.</p>'
             f'{D.H2("Quick start")}<ol>'
             f'<li style="margin-bottom:5pt">Read the pacing guide (page {D.IX("pacing")}) and the teacher notes (pages {D.IX("tn1")}–{D.IX("tn2")}).</li>'
             f'<li style="margin-bottom:5pt">Check the tune and its sources (page {D.IX("tunes")}) and the setup (page {D.IX("setup")}).</li>'
             f'<li style="margin-bottom:5pt">Print the student pages (pages {D.IX("chart1")}–{D.IX("reflect")}), one set per student.</li>'
             f'<li>Open the intro deck and read the speaker notes for Class 1.</li></ol>'
             f'{D.H2("The intro deck")}'
             f'<p>Every slide has a class: {D.deck_class_line()}. Every slide has speaker notes.</p>'
             f'<p class="small">Fonts: the deck uses Oswald and Source Sans 3 (free on Google Fonts, built into Google Slides). If PowerPoint or '
             f'Keynote shows a different font, install the two fonts or present the PDF copy, which shows the intended look.</p>'
             f'</div><div>'
             f'{D.H2("What’s inside", True)}<table class="t"><tr><th>Part</th><th>Pages</th><th>Use</th></tr>{trs}</table>'
             f'<div class="box acc-b" style="margin-top:6pt"><span class="k">No audio included</span><p style="margin:0">{D.fill(SONG_NOTE)}</p></div>'
             f'{D.H2("Make it fit your class")}<ul>'
             f'<li><b>Easier or harder:</b> see the variations on page {D.IX("tn1")}.</li>'
             f'<li><b>Pace:</b> Class 1 is the melody, Class 2 the channels, Class 3 the drum and the arrangement, Class 4 the presentations (page {D.IX("pacing")}).</li>'
             f'<li><b>Feedback:</b> students write three questions and answer classmates’ on a class board or on paper.</li>'
             f'<li><b>Grading:</b> the rubric, /{RUBRIC_TOTAL}, the average of the student’s and your score (page {D.IX("rubric")}).</li></ul>'
             f'<div class="box" style="margin-top:6pt"><span class="k">In one sentence</span><p style="margin:0;font-size:12pt">Students learn that '
             f'a few simple parts make a whole sound: a melody, chords spelled out as arpeggios, a bass and a drum, with the limits of a game chip.</p></div>'
             f'<p class="small" style="margin-top:6pt">Logic Pro is a product of Apple Inc. This resource is not affiliated with Apple.</p>'
             f'</div></div>')
    return D.page("How to use this resource", "START HERE", "Teacher", inner, n, key="howto")


def overview_page(n, wm=False):
    inner = (f'<div class="cols"><div>'
             f'<div class="box inv" style="margin-bottom:6pt"><span class="k">The project in one line</span><p style="margin:0;font-size:12pt">'
             f'<b>{TITLE}</b> · Chiptune · Logic Pro<br>Rebuild a carol as an 8-bit game tune.</p></div>'
             f'{D.H2("What students make")}'
             f'<p style="font-size:13pt;line-height:1.5">One original arrangement, 45 to 75 seconds long, of a public-domain carol. The melody is '
             f'entered from a piano-roll chart on a square-wave lead and stays recognizable; the tempo is 120 to 150 BPM; arpeggios play the chords on a pulse wave; a '
             f'triangle bass plays the chord roots; a noise drum keeps the beat; and a Bitcrusher makes it lo-fi. It has an intro, the whole carol and the '
             f'chorus again with a change, and it is mixed with volume and EQ. Students hand in a bounced .mp3 or .wav and the zipped '
             f'.logicx project, plus their plans and a reflection, then play the tune and take questions.</p>'
             f'{D.H2("What this project reinforces")}<p style="font-size:12.2pt;line-height:1.5">{TN_REINFORCES}</p>'
             f'{D.H2("Standards")}<p style="font-size:11.4pt">Supports the National Core Arts Standards for Music (Music Technology, high school): generating '
             f'and developing ideas (MU:Cr1.1, MU:Cr2.1), presenting work (MU:Pr6.1) and responding to it (MU:Re7.2).</p>'
             f'</div><div>'
             f'{D.H2("Goals", True)}<ul>' + "".join(f"<li style='font-size:12.4pt;line-height:1.5'>{g}</li>" for g in GOALS) + '</ul>'
             f'{D.H2("At a glance")}<table class="t" style="font-size:11.2pt">'
             f'<tr><td><b>Grades</b></td><td>{GRADES_TEXT}, music technology or music production</td></tr>'
             f'<tr><td><b>Length</b></td><td>{CLASSES} class periods: read and enter the melody, build the channels, drum and arrange, present and reflect</td></tr>'
             f'<tr><td><b>Software</b></td><td>Logic Pro: Piano Roll, Retro Synth or Alchemy, Arpeggiator, Drum Machine Designer, Bitcrusher, Channel EQ, bounce</td></tr>'
             f'<tr><td><b>You supply</b></td><td>Macs with Logic Pro, headphones, a place to hand in files and a class board or paper for feedback</td></tr>'
             f'<tr><td><b>Assessment</b></td><td>Rubric, 5 categories scored 1–5, /{RUBRIC_TOTAL}; final grade = average of the student’s and the '
             f'teacher’s score (page {D.IX("rubric")})</td></tr></table>'
             f'<div class="box" style="margin-top:6pt"><span class="k">Before they start</span><p style="margin:0;font-size:11.4pt">Students should know how '
             f'to open a project, add a software instrument and use the mixer in Logic. Nobody needs to read music: the charts name every '
             f'pitch and length.</p></div>'
             f'</div></div>')
    return D.page("Project overview", "OVERVIEW", "Chiptune project", inner, n, key="overview")


def setup_page(n, wm=False):
    inner = (f'<style>.sb p, .sb li {{ font-size: 11.6pt; line-height: 1.44; margin-bottom: 5pt; }}</style><div class="cols"><div class="big sb">'
             f'{D.H2("You need", True)}<ul>'
             f'<li><b>A Mac with Logic Pro</b> for each student, and <b>headphones</b>.</li>'
             f'<li><b>A place to hand in</b> the .mp3 or .wav, the zipped .logicx and the reflection.</li>'
             f'<li><b>The three chart pages</b>, printed (pages {D.IX("chart1")}–{D.IX("chart3")}), or shown on the projector.</li>'
             f'<li><b>The channel cards, arpeggio cards and drum patterns</b>, printed (pages {D.IX("channels")}–{D.IX("drums")}).</li>'
             f'<li><b>Printed student pages</b>, one set each (pages {D.IX("chart1")}–{D.IX("reflect")}).</li>'
             f'<li><b>A MIDI keyboard</b> is optional: every melody can be drawn with the mouse.</li></ul>'
             f'{D.H2("Before Class 1")}'
             + "".join(D.chk(c, 13, "font-size:11.6pt;margin-bottom:7pt") for c in [
                 f"Read the tune page (page {D.IX('tunes')}) and decide whether the carol suits your class.",
                 "Open Logic Pro on a student computer: can you make a Software Instrument track, open the Piano Roll, put an Arpeggiator in a MIDI FX slot and a Bitcrusher in an audio effects slot?",
                 f"Check that the tools on page {D.IX('channels')} are there (Retro Synth or Alchemy, Arpeggiator, Drum Machine Designer, Bitcrusher, Channel EQ).",
                 f"Read the worked example (pages {D.IX('example')}–{D.IX('example2')})."]) +
             f'</div><div class="big sb">'
             f'{D.H2("What to watch", True)}'
             f'<p style="font-size:11.4pt">Students enter the notes but get a wrong one, the arpeggio plays the wrong chord, the sound is smooth instead of '
             f'chip-like, or the arrangement is the wrong length. {TN_NOTE}</p>'
             f'<div class="box acc-b" style="margin-top:2pt"><span class="k">Ideas for the room</span><ul style="margin:0">'
             f'<li style="font-size:11.2pt">Ask while students work: which channel is that? Which chord is the arpeggio spelling? Can you hear the carol?</li>'
             f'<li style="font-size:11.2pt">On Class 1, tap 120, 135 and 150 BPM on the desk and have students pick the tempo that feels like a game level.</li>'
             f'<li style="font-size:11.2pt">A student who is stuck on arpeggios can start from the Up pattern and one chord, then change the chord every bar.</li></ul></div>'
             f'{D.H2("Choosing the carol")}'
             f'<div class="box"><span class="k">A respectful choice</span><p style="margin:0;font-size:11pt;line-height:1.4">'
             f'“O Come, All Ye Faithful” is a Christian Christmas carol. Offer it where carols are part of your winter concert or classroom. For a secular '
             f'winter program, or for a student who prefers another melody, any public-domain tune you approve (first published in the United States in '
             f'1930 or earlier) works with the same plan, and the blank piano roll on page {D.IX("plan")} is there for their own chart.</p></div>'
             f'<div class="box" style="margin-top:6pt"><span class="k">Keep the volume moderate</span><p style="margin:0;font-size:11pt;line-height:1.4">'
             f'Square waves and crushed sounds are bright and can be tiring in headphones. Tell students to start low and check the final mix at a normal level.</p></div>'
             f'</div></div>')
    return D.page("Setup and what to watch", "SETUP", "Teacher", inner, n, key="setup")


def tunes_page(n, wm=False):
    facts = [("Tune", "“O Come, All Ye Faithful” (Latin: Adeste fideles), the whole melody: 21 chart bars, {nn} notes"),
             ("Composer, date", "Attributed to John Francis Wade (about 1711–1786). Many hymn books date the tune to about 1743; the earliest dated "
                                "manuscript is from 1751. Either way it is far older than the 1930 cutoff, so it is in the public domain."),
             ("In this kit", "C major, 4/4, a one-beat pickup, 21 chart bars, range G4 to G5 (eight different notes, all white keys)"),
             ("Not included", "No lyrics, no recordings and no published edition. The words are not printed; students make every sound themselves.")]
    rows = "".join(f"<tr><td style='width:20%'><b>{a}</b></td><td>{b.replace('{nn}', str(note_count()))}</td></tr>" for a, b in facts)
    inner = (f'<p style="margin:0 0 4pt;font-size:11.4pt;line-height:1.42">The carol is in the public domain and is printed here as a note chart only. '
             f'Pitches and lengths are checked against two independent transcriptions in code.</p>'
             f'<table class="t" style="font-size:10.4pt">{rows}</table>'
             f'{D.H2("Where the notes come from")}<ul style="font-size:10.8pt">'
             f'<li><b>Transcription 1 (G major):</b> the melody of the Open Hymnal Project’s setting of “A Hymnal” (Episcopal, 1916), hymn 72, a free score '
             f'of the public-domain tune.</li>'
             f'<li><b>Transcription 2 (C major):</b> a second, independent transcription of the same tune, typed in C major.</li>'
             f'<li><b>The chart:</b> transcription 1 moved up five semitones (a perfect fourth), so G major becomes C major. All three agree note for note and '
             f'length for length. In some other editions the F# in hymn-book bar 12 (chart bar 13) is held for two beats; the chart uses the version that passes through E, as the 1916 hymnal does.</li></ul>'
             f'{D.H2("The public-domain rule")}<p style="font-size:11.2pt;line-height:1.42">In 2026 a melody is in the public domain in the United '
             f'States when it was first published in 1930 or earlier (1931 from 1 January 2027). Recordings, film and pop versions, and their arrangements are '
             f'separate works, so students must not use them. If a student suggests another tune, check its first publication date before you approve it.</p>'
             f'{D.H2("Why C major")}<p style="font-size:11.2pt;line-height:1.42">The carol is usually printed in G major. Moving every note up five semitones '
             f'puts it in C major: every note is a white key, and the lead sits in a bright range, G4 to G5. A strong student can move the project back to G '
             f'major with Transpose in the Region inspector (down five semitones) and rewrite the chords.</p>'
             f'<div class="cols" style="gap:12pt;margin-top:4pt"><div class="box acc-b"><span class="k">Reading the chart</span><p style="margin:0;font-size:10.4pt;line-height:1.38">'
             f'Pitch names run down the left; middle C is C4 (Logic’s piano roll calls it C3). Bold lines are bars, gray lines are beats. A note’s length is the name beside it: '
             f'16th, eighth, quarter, half, or dotted (a dotted quarter is one and a half beats). Chords are one idea that fits, not the only one.</p></div>'
             f'<div class="box"><span class="k">The pickup bar</span><p style="margin:0;font-size:10.4pt;line-height:1.38">'
             f'The carol starts on beat 4: one note before the first full bar. Chart bar 1 holds that note after three beats of rest, so chart bar 2 is the first '
             f'bar of a hymn book. The last chart bar holds three beats and a rest, so the pickup and the last bar add up to one bar.</p></div></div>')
    return D.page("Tune sources and the public-domain rule", "TEACHER", "Tune", inner, n, key="tunes")


def tune_table(a, b, size=9.4):
    rows = "".join(f"<tr><td style='width:7%'><b>{i + 1}</b></td><td>{bar_text(CHART[i])}</td><td style='width:19%'>{chord_text(CH[i])}</td></tr>"
                   for i in range(a, b))
    return f'<style>table.tt td, table.tt th {{ padding: 1.5pt 5pt; }}</style><table class="t tt" style="font-size:{size}pt;line-height:1.2;margin:3pt 0 3pt"><tr><th>Bar</th><th>Notes (pitch, length)</th><th>Chords</th></tr>{rows}</table>'


def systems_html(idx):
    return "".join(f'<div style="margin:0 0 3pt">{D.body_svg(tune_roll(a, b, 1100, f"page roll {a}"))}</div>' for a, b in (SYSTEMS[i] for i in idx))


def chart1_page(n, wm=False):
    inner = (f'<p style="margin:0 0 3pt;font-size:10.4pt"><b>O Come, All Ye Faithful</b>, part 1 of 3: the verse, chart bars 1–9 · John Francis Wade, '
             f'c. 1743 (public domain) · C major, 4/4 · {note_count()} notes in all, {NBARS} chart bars</p>'
             + systems_html([0, 1]) + tune_table(0, 9) +
             f'<div class="box acc-b" style="margin-top:4pt;padding:4pt 10pt"><span class="k">About this chart</span><p style="margin:0;font-size:9.6pt;line-height:1.32">'
             f'Chart bar 1 is the <b>pickup bar</b>: three beats of rest, then one note on beat 4. Chart bar 2 is the first full bar of the tune, and the verse ends on a long G in chart bar 9. '
             f'Logic calls middle C “C3”, so subtract one from the octave numbers here when you read your Piano Roll. Chords are one idea that fits; try others by ear. '
             f'Step 3 of the project sheet: enter the melody on your square-wave lead.</p></div>')
    return D.page("Note chart · the carol, 1 of 3", "STUDENT", "Class 1", inner, n, wm, name=True, key="chart1")


def chart2_page(n, wm=False):
    inner = (f'<p style="margin:0 0 3pt;font-size:10.4pt"><b>O Come, All Ye Faithful</b>, part 2 of 3: the bridge and the first half of the chorus, chart bars 10–17</p>'
             + systems_html([2, 3]) + tune_table(9, 17) +
             f'<div class="box acc-b" style="margin-top:4pt;padding:4pt 10pt"><span class="k">About this chart</span><p style="margin:0;font-size:9.6pt;line-height:1.32">'
             f'The bridge (chart bars 10–13) starts on the highest note, G5, and walks down. Chart bar 13 ends with a lead-in note, C5, on beat 4 that starts the '
             f'chorus. The chorus (chart bars 14–21) is the part people know best: “O come, let us adore Him”. Chart bars 14 and 16 start alike, so you can copy a region '
             f'and edit it instead of drawing every note again.</p></div>'
             f'<div class="box" style="margin-top:4pt;padding:4pt 10pt"><span class="k">Check your entry</span>'
             + "".join(D.chk(c, 11, "font-size:9.6pt;margin-bottom:2pt") for c in [
                 "Mark the start of the bridge and the start of the chorus with a marker or a region color: you will need them for the Layer map."]) + '</div>')
    return D.page("Note chart · the carol, 2 of 3", "STUDENT", "Class 1", inner, n, wm, name=True, key="chart2")


def bass_table(a=0, b=NBARS):
    def one(i):
        parts, t = [], 0
        for ln, ch in CH[i]:
            parts.append(f"{BASS_ROOT[ch]} {LEN_NAMES[ln]}")
            t += ln
        return " · ".join(parts)
    half = (b - a + 1) // 2

    def tbl(lo, hi):
        rows = "".join(f"<tr><td style='width:11%'><b>{i + 1}</b></td><td>{one(i)}</td></tr>" for i in range(lo, hi))
        return f'<table class="t" style="font-size:8.8pt;line-height:1.18;margin:2pt 0 0"><tr><th>Bar</th><th>Triangle bass (root, length)</th></tr>{rows}</table>'
    return f'<div class="cols" style="gap:10pt"><div>{tbl(a, a + half)}</div><div>{tbl(a + half, b)}</div></div>'


def chart3_page(n, wm=False):
    inner = (f'<p style="margin:0 0 3pt;font-size:10.4pt"><b>O Come, All Ye Faithful</b>, part 3 of 3: the second half of the chorus, chart bars 18–21, and the bass line for the whole carol</p>'
             + systems_html([4]) + tune_table(17, 21) +
             f'<div class="box acc-b" style="margin:4pt 0;padding:4pt 10pt"><span class="k">The triangle bass</span><p style="margin:0;font-size:9.6pt;line-height:1.32">'
             f'The bass plays the root of each chord, one long note per chord, in the octave below the arpeggios (C2 to A2). The roots come from the chords printed '
             f'on the three chart pages. Chord changes inside a bar get a shorter note. The last chart bar ends on a long C and a rest.</p></div>'
             + bass_table())
    return D.page("Note chart · chords and bass, 3 of 3", "STUDENT", "Classes 1–2", inner, n, wm, name=True, key="chart3")


def chan_rows():
    rows = [("1 · LEAD", "Square wave", "Plays the melody. A square wave switches between high and low, half of each cycle at each level: bright, buzzy and hollow. Keep it the loudest channel.",
             "Retro Synth (Analog engine) or Alchemy: pick the square wave, Mono if there is a Mono setting, a short attack and release, no reverb."),
            ("2 · ARPS", "Pulse wave, 25%", "Plays the chords as arpeggios. A narrower pulse, high for a quarter of each cycle, is thinner and more nasal than a square, so it sits behind the lead.",
             f"A second Retro Synth or Alchemy track with a pulse wave (pulse width about 25%). Put the Arpeggiator in its MIDI FX slot (page {pg('arps')}). Keep it lower and quieter than the lead."),
            ("3 · BASS", "Triangle wave", f"Plays the chord roots (page {pg('chart3')}). A triangle wave is soft and round, with weaker high harmonics than a square, so it makes a good bass.",
             "Retro Synth or Alchemy with a triangle wave, Mono if available and a short release. Play the roots from C2 to A2."),
            ("4 · DRUM", "Noise", "Plays the drum. Noise has no pitch: a short burst is a hat, a longer burst a snare and a short, very low one a kick.",
             f"Drum Machine Designer and its Step Sequencer (page {pg('drums')}), one pad per sound, or a synthesizer’s noise source with a quick envelope.")]
    return "".join(f"<tr><td style='width:15%'><b style='font-family:Oswald;color:{ACCENT}'>{a}</b><br><b>{b}</b></td><td style='width:41%'>{c}</td><td>{d}</td></tr>"
                   for a, b, c, d in rows)


def channels_page(n, wm=False):
    inner = (f'<p style="margin:0 0 3pt;font-size:10.6pt;line-height:1.38">A classic game chip had only a few channels, and each channel plays <b>one note at a time</b>. '
             f'This project uses four: two pulse-type waves, a triangle and noise. Because a channel cannot play a chord, the arps channel spells chords out one note after another (page {pg("arps")}).</p>'
             f'<div style="margin:2pt auto 4pt;width:6.4in">{D.body_svg(waves_body(1100, "page waves", 26, 19, 24))}</div>'
             f'<table class="t" style="font-size:9.4pt;line-height:1.28"><tr><th>Channel</th><th>What it does</th><th>In Logic (starting settings)</th></tr>{chan_rows()}</table>'
             f'<div class="box acc-b" style="margin-top:5pt;padding:5pt 10pt"><span class="k">Bitcrusher · the lo-fi switch</span><p style="margin:0 0 2pt;font-size:9.8pt;line-height:1.32">'
             f'<b>What it does.</b> It lowers the sound’s bit depth (Resolution) and its sample rate (Downsampling) on purpose, so the sound turns grainy and a little metallic. The lower the numbers, the more crushed it sounds.</p>'
             f'<p style="margin:0 0 2pt;font-size:9.8pt;line-height:1.32"><b>In Logic.</b> Click an Audio FX slot on a channel strip and choose Bitcrusher (look in the Distortion group of the plug-in menu). Put it on one channel, or on the Stereo Out to crush everything. Start with Mix at about half, then lower Resolution and Downsampling until it sounds like a game.</p>'
             f'<p style="margin:0;font-size:9.8pt;line-height:1.32"><b>Try.</b> Crush the intro more than the chorus, and automate Mix (press A) so the sound changes from section to section. Keep the arps and the bass clear: too much crush hides a chord.</p></div>'
             f'<div class="box" style="margin-top:5pt;padding:5pt 10pt"><span class="k">Four checks for every channel</span>'
             + "".join(D.chk(c, 11, "font-size:9.8pt;margin-bottom:2pt") for c in [
                 "It plays one note at a time, with a short release.",
                 "It has its own register: bass lowest, then the arps, then the lead on top.",
                 "No reverb on the chip channels: a chip is dry.",
                 "I can say which channel plays any note I point to."]) + '</div>')
    return D.page("Four channels and the Bitcrusher", "STUDENT", "Class 2", inner, n, wm, name=True, key="channels")


def chord_rows():
    out = []
    for nm in CHORD_ORDER:
        r, k, num, q = CHORDS[nm]
        letters = chord_letters(nm)
        seq = arp_seq(nm, "up", 8)
        out.append(f"<tr><td><b>{nm}</b></td><td>{num}</td><td>{' – '.join(letters)}</td><td>{' '.join(pname(m) for m in seq)}</td><td>{BASS_ROOT[nm]}</td></tr>")
    return "".join(out)


def arp_card(kind, head, setting, feel):
    cheight = 11 if kind == "up2" else 21
    body = arps_roll("C", kind, 560, "page arp card", cheight, labels=kind != "up2")
    seq = " ".join(pname(m)[:-1] for m in arp_seq("C", kind))
    head, setting, feel = escape(head), escape(setting), escape(feel)
    return (f'<div class="box" style="padding:4pt 8pt"><span class="k" style="font-size:11.5pt;margin:0">{head}</span>'
            f'<p style="margin:0 0 2pt;font-size:8.8pt"><b>Arpeggiator:</b> {setting}</p>'
            f'<div style="margin:2pt 0">{D.body_svg(body)}</div>'
            f'<p style="margin:0 0 1pt;font-size:8.8pt;line-height:1.25"><b>C chord, one bar (16 steps):</b> {seq}</p>'
            f'<p style="margin:0;font-size:8.8pt;line-height:1.25"><b>Sounds like:</b> {feel}</p></div>')


def arps_page(n, wm=False):
    cards = [arp_card(a[0], a[1], a[2], a[3]) for a in ARPS]
    inner = (f'<p style="margin:0 0 3pt;font-size:10.4pt;line-height:1.36">A <b>chord</b> is three or four notes stacked in thirds. An <b>arpeggio</b> plays them one after another. '
             f'The table spells every chord of the carol in C major and gives the first eight steps of its Up arpeggio at a 1/16 rate; the cards below show four patterns for the C chord. '
             f'Put the chord in the arpeggio track as notes stacked in one column, with the Arpeggiator in the MIDI FX slot (page {pg("logicref")}).</p>'
             f'<style>table.ct td, table.ct th {{ padding: 1.8pt 5pt; }}</style><table class="t ct" style="font-size:9.4pt;line-height:1.22;text-align:left"><tr><th>Chord</th><th>Numeral</th><th>Notes: root – third – fifth (– seventh)</th>'
             f'<th>Up, first 8 steps</th><th>Bass root</th></tr>{chord_rows()}</table>'
             f'<div class="cols" style="gap:8pt;margin-top:5pt"><div>{cards[0]}<div style="height:5pt"></div>{cards[2]}</div><div>{cards[1]}<div style="height:5pt"></div>{cards[3]}</div></div>'
             f'<p style="margin:5pt 0 0;font-size:9.2pt;line-height:1.3"><b>Try:</b> Up in the chorus and Up &amp; Down in the verse. Some versions of the Arpeggiator repeat the top and bottom '
             f'note in Up &amp; Down; if yours does, the idea is the same. The numerals show each chord’s place in the key: I, IV and V are major, ii, iii and vi are minor, and V7 adds a seventh to V.</p>')
    return D.page("Arpeggio cards", "STUDENT", "Class 2", inner, n, wm, name=True, key="arps")


def pattern_card(p):
    body, w, h = grid_for(p)
    txt = (f'<p style="margin:0 0 2pt;font-size:9.6pt;line-height:1.28"><b>Drums.</b> {p["drums"]}</p>'
           f'<p style="margin:0 0 2pt;font-size:9.6pt;line-height:1.28"><b>Noise sounds.</b> {p["noise"]}</p>'
           f'<p style="margin:0;font-size:9.6pt;line-height:1.28"><b>Try.</b> {p["tryit"]}</p>')
    head = f'<span class="k" style="font-size:13pt;margin:0">{p["name"]} · {p["feel"]}</span>'
    return (f'<div class="box" style="margin-bottom:5pt;padding:5pt 10pt">{head}<div style="display:flex;gap:12pt;margin-top:2pt;align-items:flex-start">'
            f'<div style="flex:1">{txt}</div><div style="width:3.15in;flex:0 0 3.15in">{D.body_svg((body, w, h))}</div></div></div>')


def drums_page(n, wm=False):
    inner = (f'<p style="margin:0 0 4pt;font-size:10.8pt;line-height:1.38">On a game chip the whole drum kit is one <b>noise</b> channel: a very short burst is a hat, a longer burst is a snare and a short, '
             f'very low burst is a kick. Each card gives a one-bar pattern (16 steps, 4 to a beat; shaded steps are the beats). Pick one for your arrangement and copy it into the Step Sequencer of a '
             f'Drum Machine Designer track, with a very short noise sound on each pad (page {pg("logicref")}).</p>'
             + "".join(pattern_card(p) for p in PATTERNS)
             + f'<div class="cols" style="gap:12pt"><div class="box acc-b" style="padding:6pt 10pt"><span class="k" style="font-size:13pt;margin:0">Pattern E · my own</span>'
               f'<p style="margin:2pt 0 3pt;font-size:9.6pt;line-height:1.28">Fill in a one-bar pattern of your own. Keep the snare on a beat.</p>'
               f'<div style="width:3.3in">{D.body_svg(blank_grid("page blank grid"))}</div></div>'
               f'<div class="box" style="padding:6pt 10pt"><span class="k" style="font-size:13pt;margin:0">Where I will use each pattern</span>'
               f'<table class="t" style="font-size:9.8pt;margin-top:3pt"><tr><th>Section</th><th>Pattern (A to E)</th></tr>'
               + "".join(f"<tr><td style='height:16pt'>{x}</td><td></td></tr>" for x in ("Intro", "Verse", "Bridge", "Chorus", "Chorus again"))
               + '</table></div></div>')
    return D.page("Noise drum patterns", "STUDENT", "Class 3", inner, n, wm, name=False, key="drums")


PLAN_MENU = ["Arpeggios: Up in one section, Up & Down in another", "Triangle bass on the chord roots", "Noise drum with pattern A, B or D",
             "A fill (pattern C) at the end of a section", "Bitcrusher on at least one channel", "Bitcrusher Mix or crush changes between sections",
             "Last chorus an octave higher", "Channel EQ on the lead and the arps"]


def plan_page(n, wm=False):
    half = (len(PLAN_MENU) + 1) // 2
    items = [D.chk(f"<b>{m}</b>", 11, "font-size:10.2pt;margin-bottom:4pt") for m in PLAN_MENU]
    rows = "".join(f"<tr><td style='height:21pt'><b>{a}</b></td><td></td><td></td></tr>" for a in ("1 · Lead", "2 · Arps", "3 · Bass", "4 · Drum"))
    chords = "".join(f"<td style='height:24pt;text-align:center'><b>Intro bar {i}</b></td>" for i in range(1, 5))
    roll = D.body_svg(roll_body([], 64, 16, 4, 48, 59, 1100, 14, 1, None, "blank arp roll", labels=False))
    inner = (f'<p style="margin:0 0 4pt;font-size:10.6pt;line-height:1.36">Step 2: plan. Pick a tempo from 120 to 150 BPM, a drum pattern and the arpeggio patterns, '
             f'then decide which moves you will use. The carol and its chords are on the chart pages (pages {pg("chart1")}–{pg("chart3")}).</p>'
             f'<div class="box acc-b" style="margin:0 0 5pt"><span class="k">My choices</span>'
             f'<div class="fl" style="margin:3pt 0 0"><b>Tempo (BPM):</b><span style="flex:0 0 0.9in"></span><b>Why this tempo:</b><span></span></div>'
             f'<div class="fl" style="margin:0"><b>Drum pattern (A, B, C or D):</b><span style="flex:0 0 0.9in"></span>'
             f'<b>Arpeggio patterns (Up, Down, Up &amp; Down):</b><span></span></div></div>'
             f'<span class="k">The chords of my intro (four bars, one chord a bar, ending so that it leads to a C chord)</span>'
             f'<table class="map" style="margin-bottom:4pt"><tr>{chords}</tr><tr>' + "".join("<td style='height:24pt'></td>" for _ in range(4)) + '</tr></table>'
             f'<span class="k">My moves (check the ones I will use)</span>'
             f'<div class="cols" style="gap:12pt"><div>{"".join(items[:half])}</div><div>{"".join(items[half:])}</div></div>'
             f'<div class="fl" style="margin-top:3pt"><b>What stays the same, so people still know the carol:</b><span></span></div>'
             f'<span class="k">My four channels</span>'
             f'<table class="map" style="margin-bottom:4pt"><tr><th style="width:16%">Channel</th><th style="width:40%">Wave and sound in Logic</th>'
             f'<th>What it plays</th></tr>{rows}</table>'
             f'<span class="k">Sketch: the arpeggio of my first intro chord, one bar, or my own tune (pencil, optional)</span>'
             f'<div style="margin-top:2pt">{roll}</div>')
    return D.page("My plan", "STUDENT", "Class 1", inner, n, wm, name=True, key="plan")


ARR_COLS = 18         # each column is two bars: 36 bars


def layers_page(n, wm=False):
    head = "<tr><th style='width:1.1in'>Channel</th>" + "".join(f"<th>{2 * i + 1}</th>" for i in range(ARR_COLS)) + "</tr>"
    names = ["1 · Lead", "2 · Arps", "3 · Bass", "4 · Drum", "Effect"]
    body = "".join(f"<tr><td class='l' style='height:27pt'>{nm}</td>" + "".join(f"<td class='{'b' if i % 2 == 0 else ''}'></td>" for i in range(ARR_COLS))
                   + "</tr>" for nm in names)
    hr = "".join(f"<tr><td><b>{b}</b></td><td>{bar_s(b):.2f} s</td>" + "".join(f"<td>{length_s(bars, b):.1f} s</td>" for bars in LEN_BARS) + "</tr>"
                 for b in LEN_BPMS)
    inner = (f'{CSS_SG}<style>table.sg th {{ font-size: 7pt; }} table.sg td.l {{ width: 1.1in; }}</style>'
             f'<p style="margin:0 0 4pt;font-size:10.4pt">Step 6: arrange. Give your arrangement a form: an intro of 2 to 6 bars, the whole carol (21 bars, chart bars 1–21), and the chorus again '
             f'(8 bars) with a change. Each column is 2 bars (the number is its first bar). Shade the columns where each channel plays, and write what the effect row does '
             f'(for example, Bitcrusher Mix). Mark where each section starts: every thick line is 4 bars. 31 to 35 bars, 45 to 75 seconds only.</p>'
             f'<table class="sg">{head}{body}</table>'
             f'<div class="cols" style="gap:10pt;margin-top:6pt"><div class="box acc-b"><span class="k">My sections (bars)</span>'
             f'<div class="fl" style="margin:3pt 0 0"><b>Intro:</b><span></span><b>bars</b><span style="flex:0 0 0.6in"></span></div>'
             f'<div class="fl"><b>Verse + pickup (9):</b><span></span><b>starts bar</b><span style="flex:0 0 0.6in"></span></div>'
             f'<div class="fl"><b>Bridge (4):</b><span></span><b>starts bar</b><span style="flex:0 0 0.6in"></span></div>'
             f'<div class="fl"><b>Chorus (8):</b><span></span><b>starts bar</b><span style="flex:0 0 0.6in"></span></div>'
             f'<div class="fl" style="margin-bottom:0"><b>Chorus again (8):</b><span></span><b>starts bar</b><span style="flex:0 0 0.6in"></span></div></div>'
             f'<div><span class="k">Length helper (4/4)</span><table class="t" style="font-size:9.4pt;margin-top:2pt"><tr><th>BPM</th><th>One bar</th>'
             f'<th>{LEN_BARS[0]} bars</th><th>{LEN_BARS[1]} bars</th><th>{LEN_BARS[2]} bars</th></tr>{hr}</table><p class="small" style="margin:1pt 0 0">Aim for 45 to 75 seconds. '
             f'Seconds = bars × 240 ÷ BPM.</p></div></div>'
             f'<div class="fl" style="margin-top:6pt"><b>My tempo:</b><span style="flex:0 0 0.8in"></span><b>Bars:</b><span style="flex:0 0 0.8in"></span>'
             f'<b>Length: bars × 240 ÷ tempo =</b><span style="flex:0 0 0.8in"></span><b>seconds</b></div>'
             f'<div class="box" style="margin-top:4pt"><span class="k">Checks before I bounce</span>'
             + "".join(D.chk(c, 11, "font-size:10pt;margin-bottom:2pt") for c in [
                 "I can name the carol in the first ten seconds, and the lead is louder than the arps.",
                 "Every pitch and length matches the chart, and every arpeggio matches its chord.",
                 "The bass is clear and not muddy, and the drum does not cover the lead.",
                 "The Bitcrusher is on and the sound changes between sections.",
                 "The arrangement is between 45 and 75 seconds."]) + '</div>')
    return D.page("Layer map", "STUDENT", "Classes 3–4", inner, n, wm, name=True, key="layers")


def example_page(n, wm=False):
    chs = "".join(f"<tr><td style='width:17%'><b>{num} · {nm}</b><br>{w}</td><td>{d}</td></tr>" for num, nm, w, _s, d in EX_CH)
    intro = "".join(f"<td><b>Bar {i + 1}</b><br>{c}<br><span style='font-size:8.6pt;letter-spacing:.06em'>{' '.join(pname(m)[:-1] for m in arp_seq(c, 'up', 8))}</span></td>"
                    for i, c in enumerate(EX_INTRO))
    inner = (f'<p style="margin:0 0 4pt;font-size:10pt">An <b>invented plan on paper</b>: the carol as an 8-bit tune at {EX_BPM} BPM. No audio is included. '
             f'Student projects will differ. Page 1 of 2: the plan, the four channels and the intro.</p>'
             f'<div class="cols" style="gap:10pt"><div class="box"><span class="k">1 · A weak plan</span><p style="margin:0;font-size:10.2pt">{EX_WEAK}</p>'
             f'<p style="margin:3pt 0 0;font-size:9.2pt">It names no tempo, no channels and nothing that would sound like a game chip.</p></div>'
             f'<div class="box acc-b"><span class="k">2 · A clear plan</span><p style="margin:0;font-size:8.6pt;line-height:1.28">{EX_STRONG}</p></div></div>'
             f'{D.H2("3 · The four channels")}'
             f'<table class="t" style="font-size:9pt;line-height:1.22">{chs}</table>'
             f'{D.H2("4 · The intro: four chords, one a bar, with their Up arpeggios")}'
             f'<table class="t" style="font-size:8.8pt;line-height:1.2;text-align:center"><tr>{intro}</tr></table>'
             f'<p style="margin:2pt 0 3pt;font-size:8.8pt">The intro ends on G, which leads to the C chord of the pickup bar (bar 5). The line under each chord is its first eight arpeggio steps.</p>'
             f'{D.H2("5 · The first five bars of the carol, with their chords (chart bars 1–5)")}'
             f'<div style="width:6.6in;margin:2pt auto 0">{D.body_svg(tune_roll(0, 5, 1100, "page example roll"))}</div>')
    return D.page("Worked example · an invented arrangement", "EXAMPLE", "Teacher", inner, n, wm, ak=True, key="example")


EX_OFFSET = {"Verse": 4, "Bridge": 4, "Chorus": 4, "Chorus again": 12}     # arrangement bar minus chart bar
EX_DRUM = {"Intro": "none", "Verse": "none", "Bridge": "pattern D", "Chorus": "pattern A, then C in the last bar",
           "Chorus again": "pattern A, then C in the last bar"}


def ex_chart_bars(nm, a, b):
    return (a - EX_OFFSET[nm], b - EX_OFFSET[nm]) if nm in EX_OFFSET else None


def ex_rows():
    out = []
    for nm, a, b in EX_SECTIONS:
        cb = ex_chart_bars(nm, a, b)
        if cb:
            chords = " | ".join(chord_text(CH[i - 1]).replace(" · ", " ") for i in range(cb[0], cb[1] + 1))
            cbt = f"{cb[0]}–{cb[1]}"
        else:
            chords, cbt = " | ".join(EX_INTRO), "none"
        out.append(f"<tr><td><b>{nm}</b></td><td style='white-space:nowrap'>{a}–{b}</td><td style='white-space:nowrap'>{cbt}</td><td>{chords}</td><td>{EX_DRUM[nm]}</td></tr>")
    return "".join(out)


def example2_page(n, wm=False):
    secs = "".join(f"<tr><td style='width:30%'><b>{nm}</b></td><td style='white-space:nowrap'>bars {a}–{b}</td><td>{mmss((a - 1) * EX_BAR_S)}–{mmss(b * EX_BAR_S)}</td></tr>"
                   for nm, a, b in EX_SECTIONS)
    moms = "".join(f"<tr><td style='width:14%'><b>bar {b}</b></td><td style='width:14%'>{mmss((b - 1) * EX_BAR_S)}</td><td>{d}</td></tr>" for b, d in EX_MOMENTS)
    qs = " ".join(f"{i + 1}. {q}" for i, q in enumerate(EX_QUESTIONS))
    inner = (f'<p style="margin:0 0 3pt;font-size:10pt">The same arrangement, page 2 of 2: the map of the whole piece, then the numbers.</p>'
             f'{D.H2("6 · The map: 1:06, five sections, four channels, two lanes")}'
             f'<div style="width:7.4in;margin:1pt auto 3pt">{D.body_svg(map_body(1250, "page map", 24, 20))}</div>'
             f'<div class="cols" style="gap:10pt"><div><span class="k" style="font-size:9.4pt">7 · Sections</span>'
             f'<table class="t" style="font-size:8.8pt;line-height:1.2;margin-top:2pt">{secs}</table></div>'
             f'<div><span class="k" style="font-size:9.4pt">8 · Moments to point out</span>'
             f'<table class="t" style="font-size:8.8pt;line-height:1.2;margin-top:2pt">{moms}</table></div></div>'
             f'{D.H2("9 · Section by section")}<table class="t" style="font-size:8.8pt;line-height:1.22"><tr><th>Section</th><th>Bars</th><th>Chart bars</th>'
             f'<th>Chords the arps spell</th><th>Noise drum</th></tr>{ex_rows()}</table>'
             f'<div class="box acc-b" style="margin-top:5pt"><span class="k">10 · Checking the numbers</span><p style="margin:0;font-size:9pt;line-height:1.3">'
             f'One bar of 4/4 at {EX_BPM} BPM lasts 240 ÷ {EX_BPM} = {EX_BAR_S:g} seconds, so {EX_BARS} bars = {EX_BARS * EX_BAR_S:g} seconds, inside 45 to 75. '
             f'The sections are {" + ".join(str(b - a + 1) for _, a, b in EX_SECTIONS)} bars = {EX_BARS}. A moment in bar b happens at (b minus 1) × {EX_BAR_S:g} seconds: bar 18 is 17 × 2 = 34 seconds, 0:34. '
             f'All four channels play from bar {EX_DENS.index(4) + 1} to the end. '
             f'<b>Three feedback questions (invented):</b> {qs}</p></div>')
    return D.page("Worked example · the map", "EXAMPLE", "Teacher", inner, n, wm, ak=True, key="example2")


PAGES = {"howto": howto_page, "overview": overview_page, "setup": setup_page, "tunes": tunes_page, "example": example_page,
         "example2": example2_page, "chart1": chart1_page, "chart2": chart2_page, "chart3": chart3_page, "channels": channels_page,
         "arps": arps_page, "drums": drums_page, "plan": plan_page, "layers": layers_page}


# ================================================================ content checks
def seg_ok(notes, a, b, chord):
    """The first note and the longest note that start in [a, b) are tones of the chord."""
    ins = [(p, s, d) for p, s, d in notes if a <= s < b]
    tones = CHORD_TONES[chord]
    if not ins:
        held = [p for p, s, d in notes if s < a and s + d >= b]
        return bool(held) and held[0].rstrip("0123456789") in tones
    first = ins[0][0]
    longest = max(ins, key=lambda x: x[2])[0]
    return first.rstrip("0123456789") in tones and longest.rstrip("0123456789") in tones


def alpha_bbox(path):
    from PIL import Image
    import numpy as np
    a = np.array(Image.open(path).convert("RGBA"))[..., 3]
    ys, xs = np.where(a > 10)
    return xs.min(), ys.min(), xs.max(), ys.max()


def verify_content():
    errs = []
    counts = dict(goals=(GOALS, 4), vocab=(VOCAB, 4), reqs=(REQS, 7), steps=(STEPS, 7), tips=(TIPS, 4), check=(CHECK, 6),
                  rubric=(RUBRIC, 5), struggles=(STRUGGLES, 4), resources=(RESOURCES, 4))
    for nm, (lst, nexp) in counts.items():
        if len(lst) != nexp:
            errs.append(f"{nm}: {len(lst)} items, expected {nexp}")
    if RUBRIC_TOTAL != 25 or LEVELS != [1, 2, 3, 4, 5]:
        errs.append("rubric is /25, levels 1-5")
    if FILE_NAME not in CHECK[2]:
        errs.append("file name format must be on the checklist")
    if set(TAGS) & {"Holiday", "Student Practice", "Theme", "Seasonal"} or "Performing Arts" in SUBJECTS:
        errs.append("tags and subjects must not be headings")
    for w in ("Winter", "Holiday", "Christmas"):
        if w.lower() in LISTING_TITLE.lower():
            errs.append(f"the listing title must not hold the seasonal word {w}")
    # steps named on the pages are the project sheet's steps
    if not STEPS[1].startswith("<b>Plan</b>") or not STEPS[2].startswith("<b>Enter the melody</b>") or not STEPS[5].startswith("<b>Arrange"):
        errs.append("steps 2, 3 and 6 must be Plan, Enter the melody and Arrange (the pages name them)")
    # ---- the carol, three ways
    A, B = parse_abc(SRC_A), parse_abc(SRC_B)
    if len(A) != 21 or len(B) != 21:
        errs.append(f"transcriptions have {len(A)} and {len(B)} bars, expected 21 each")
    for nm, T in (("A", A), ("B", B)):
        lens = [sum(d for _, d in bar) for bar in T]
        if lens != [4] + [16] * 19 + [12]:
            errs.append(f"transcription {nm}: bar lengths {lens} (pickup 4, then 19 full bars, then a 3-beat bar)")
    if moved(A, SHIFT) != B:
        errs.append("transposition check: transcription A moved up 5 semitones must equal transcription B, note for note and length for length")
    exp_chart = [[("R", 12)] + moved(A, SHIFT)[0]] + moved(A, SHIFT)[1:20] + [moved(A, SHIFT)[20] + [("R", 4)]]
    if CHART != exp_chart:
        errs.append("the chart must be transcription A moved up 5 semitones, with the pickup and last bar filled with rests")
    if len(CHART) != NBARS or len(CH) != NBARS:
        errs.append("21 chart bars and a chord list for each")
    for i, bar in enumerate(CHART):
        if sum(d for _, d in bar) != 16:
            errs.append(f"chart bar {i + 1} adds to {sum(d for _, d in bar)} sixteenths, not 16")
        if sum(ln for ln, _ in CH[i]) != 16:
            errs.append(f"the chords of chart bar {i + 1} do not fill the bar")
        for p, d in bar:
            if d not in LEN_NAMES:
                errs.append(f"chart bar {i + 1} has a length ({d}) with no name")
            if p != "R" and (len(p) != 2 or p[0] not in "CDEFGAB"):
                errs.append(f"chart bar {i + 1}: {p} is not a white key (C major has no sharps)")
    if note_count() != 62:
        errs.append(f"{note_count()} notes, expected 62")
    ms = [midi(p) for p, _, _ in tune_notes()]
    if min(ms) != midi("G4") or max(ms) != midi("G5") or not LO <= min(ms) or not max(ms) <= HI:
        errs.append(f"range {pname(min(ms))}-{pname(max(ms))}, expected G4-G5 and inside the roll's rows")
    if CHART[0][-1] != ("C5", 4) or CHART[-1][0] != ("C5", 12) or len({p for p, _, _ in tune_notes()}) != 8:
        errs.append("the carol starts on a C5 pickup, ends on a dotted-half C5 and uses eight different notes")
    if A[0][0][1] + A[-1][0][1] != 16:
        errs.append("the pickup and the last bar must add up to one bar")
    # sections and phrases tile the 21 bars
    if [(a, b) for _, a, b in SECTIONS] != [(1, 9), (10, 13), (14, 21)] or [(a + 1, b) for a, b in SYSTEMS] != [(1, 5), (6, 9), (10, 13), (14, 17), (18, 21)]:
        errs.append("sections and systems must tile chart bars 1-21")
    # chords: spelled by stacking thirds in the scale, checked against the written names, qualities and numerals
    want = {"C": ["C", "E", "G"], "Dm": ["D", "F", "A"], "Em": ["E", "G", "B"], "F": ["F", "A", "C"], "G": ["G", "B", "D"],
            "G7": ["G", "B", "D", "F"], "Am": ["A", "C", "E"]}
    for nm, (r, k, num, q) in CHORDS.items():
        if chord_letters(nm) != want[nm]:
            errs.append(f"chord {nm} is spelled {chord_letters(nm)}, expected {want[nm]}")
        semis = chord_semis(nm)
        wq = {"major": [0, 4, 7], "minor": [0, 3, 7], "dominant seventh": [0, 4, 7, 10]}[q]
        if semis != wq:
            errs.append(f"chord {nm}: intervals {semis} do not make a {q} chord")
        if (q == "minor") != nm.endswith("m") or (q == "dominant seventh") != nm.endswith("7") or (num.isupper() == (q == "minor")):
            errs.append(f"chord {nm}: name, quality and Roman numeral {num} disagree")
        if nm not in CHORD_TONES or CHORD_TONES[nm] != set(want[nm]):
            errs.append(f"chord tones of {nm}")
        root = BASS_ROOT[nm]
        if root[:-1] != want[nm][0] or not 36 <= midi(root) <= 45:
            errs.append(f"bass root of {nm}: {root}")
    if sorted(CHORD_ORDER) != sorted(CHORDS) or {c for bar in CH for _, c in bar} != set(CHORDS):
        errs.append("every chord of the table is used in the carol, and every chord used is in the table")
    for i, spans in enumerate(CH):
        t = i * 16
        for ln, ch in spans:
            if ch not in CHORDS:
                errs.append(f"unknown chord {ch}")
                continue
            if not seg_ok(tune_notes(), t, t + ln, ch):
                errs.append(f"chord {ch} in chart bar {i + 1} (steps {t}-{t + ln}) does not hold the first and longest notes")
            t += ln
    if CH[0][0][1] != "C" or CH[-1][-1][1] != "C" or CH[8] != [(16, "G7")] or CH[7] != [(16, "G")] or CH[19][-1][1] != "G7":
        errs.append("the harmony must start and end on C, and the phrase ends must lead home through G / G7")
    # ---- arpeggios: 16 steps, every note a chord tone, and the cards' sequences
    for nm in CHORDS:
        for kind, *_ in ARPS:
            seq = arp_seq(nm, kind)
            if len(seq) != 16 or any(NAMES[m % 12].rstrip("#") not in CHORD_TONES[nm] or "#" in NAMES[m % 12] for m in seq):
                errs.append(f"arpeggio {kind} on {nm}: a note outside the chord")
    names = lambda nm, kind, n=16: " ".join(pname(m) for m in arp_seq(nm, kind)[:n])
    if names("C", "up") != "C3 E3 G3 C3 E3 G3 C3 E3 G3 C3 E3 G3 C3 E3 G3 C3" or names("C", "down") != "G3 E3 C3 G3 E3 C3 G3 E3 C3 G3 E3 C3 G3 E3 C3 G3" \
            or names("C", "updown") != "C3 E3 G3 E3 C3 E3 G3 E3 C3 E3 G3 E3 C3 E3 G3 E3" \
            or names("C", "up2") != "C3 E3 G3 C4 E4 G4 C3 E3 G3 C4 E4 G4 C3 E3 G3 C4":
        errs.append("the C chord arpeggio sequences")
    if names("G7", "up", 8) != "G3 B3 D4 F4 G3 B3 D4 F4" or names("G7", "updown", 12) != "G3 B3 D4 F4 D4 B3 G3 B3 D4 F4 D4 B3" \
            or names("Am", "up", 6) != "A3 C4 E4 A3 C4 E4" or names("F", "up", 6) != "F3 A3 C4 F3 A3 C4":
        errs.append("arpeggio sequences for G7, Am and F")
    # ---- noise drum patterns: 16 steps and the facts the cards claim
    for p in PATTERNS:
        if any(len(p["pat"][ln]) != 16 or set(p["pat"][ln]) - {"x", "."} for ln in LANES):
            errs.append(f"pattern {p['key']}: each lane is 16 steps of x and .")
    a, b, c, d = (pattern(k) for k in "abcd")
    if hits(a, "Kick") != [0, 8] or hits(a, "Snare") != [4, 12] or hits(a, "Hat") != list(range(0, 16, 2)):
        errs.append("pattern A: kick on beats 1 and 3, snare on 2 and 4, hat on every eighth")
    if hits(b, "Kick") != [0, 6, 8] or hits(b, "Snare") != [4, 12] or hits(b, "Hat") != list(range(16)):
        errs.append("pattern B: kick on beat 1, the 'and' of 2 and beat 3; snare on 2 and 4; hat on every sixteenth")
    if hits(c, "Kick") != [0, 8] or hits(c, "Snare") != [4, 12, 13, 14, 15] or hits(c, "Hat") != [0, 2, 4, 6, 8, 10]:
        errs.append("pattern C: kick on 1 and 3, snare on 2 then four sixteenths in beat 4, hat on eighths until beat 3 ends")
    if hits(d, "Kick") != [0] or hits(d, "Snare") != [8] or hits(d, "Hat") != [0, 4, 8, 12]:
        errs.append("pattern D: kick on beat 1, snare on beat 3, hat on every quarter")
    # ---- tempo and length arithmetic
    if bar_s(120) != 2 or bar_s(150) != 1.6 or length_s(33, 120) != 66:
        errs.append("one bar at 120 BPM is 2 s, at 150 BPM 1.6 s; 33 bars at 120 BPM = 66 s")
    got = [round(length_s(bars, bpm), 1) for bars in LEN_BARS for bpm in LEN_BPMS]
    if got != LEN_EXPECT:
        errs.append(f"length helper numbers {got}")
    if any(not LEN_LO <= length_s(bars, bpm) <= LEN_HI for bars in LEN_BARS for bpm in LEN_BPMS):
        errs.append("every length-helper cell must sit inside 45 to 75 seconds")
    if (BARS_MIN, BARS_MAX) != (2 + 21 + 8, 6 + 21 + 8) or (LEN_BARS[0], LEN_BARS[-1]) != (BARS_MIN, BARS_MAX) \
            or length_s(BARS_MAX, TEMPO_LO) > LEN_HI or length_s(BARS_MIN, TEMPO_HI) < LEN_LO:
        errs.append("31 to 35 bars at 120 to 150 BPM must give 45 to 75 seconds (intro 2-6 + carol 21 + chorus 8)")
    # ---- the worked example adds up
    if EX_BPM not in range(TEMPO_LO, TEMPO_HI + 1) or EX_BAR_S != 2 or EX_BARS != 33 or EX_BARS * EX_BAR_S != 66 or not BARS_MIN <= EX_BARS <= BARS_MAX:
        errs.append("the example: 33 bars x 2 s = 66 s at 120 BPM, inside the project's limits")
    if EX_SECTIONS[0][1] != 1 or EX_SECTIONS[-1][2] != EX_BARS or any(b_ + 1 != c_ for (_, _, b_), (_, c_, _) in zip(EX_SECTIONS, EX_SECTIONS[1:])):
        errs.append("sections must tile bars 1-33")
    sizes = {nm: b_ - a_ + 1 for nm, a_, b_ in EX_SECTIONS}
    if [sizes[k] for k in ("Intro", "Verse", "Bridge", "Chorus", "Chorus again")] != [4, 9, 4, 8, 8] or not 2 <= sizes["Intro"] <= 6 \
            or sizes["Intro"] + 21 + sizes["Chorus again"] != EX_BARS:
        errs.append("example sections 4 + 9 + 4 + 8 + 8: intro 2-6, the carol's 9 + 4 + 8, then the chorus again")
    if (sizes["Verse"], sizes["Bridge"], sizes["Chorus"]) != tuple(b_ - a_ + 1 for _, a_, b_ in SECTIONS):
        errs.append("the example's verse, bridge and chorus must be the chart's 9, 4 and 8 bars")
    if [m[0] for m in EX_MOMENTS] != [a_ for nm, a_, _ in EX_SECTIONS if nm != "Intro"]:
        errs.append("the example's moments are the starts of the verse, bridge, chorus and last chorus")
    if len(EX_CH) != 4 or len(EX_AUTO) != 2 or len(EX_QUESTIONS) != 3:
        errs.append("four channels, two automation lanes, three feedback questions")
    for _n, nm, _w, spans, _d in EX_CH:
        for a_, b_ in spans:
            if not 1 <= a_ <= b_ <= EX_BARS:
                errs.append(f"channel {nm}: span {a_}-{b_} outside the piece")
    spans_by = {nm: (min(a_ for a_, _ in sp), max(b_ for _, b_ in sp)) for _n, nm, _w, sp, _d in EX_CH}
    for ly, par, pts in EX_AUTO:
        key = "Arps" if ly == "Arps" else None
        a_, b_ = spans_by.get(ly, (1, EX_BARS))
        ts_ = [t_ for t_, _ in pts]
        vs = [v for _, v in pts]
        if ts_ != sorted(ts_) or len(pts) < 3 or ts_[0] < a_ or ts_[-1] > b_:
            errs.append(f"lane {ly}/{par}: points in order, 3+, inside its range")
        if max(vs) - min(vs) < .5:
            errs.append(f"lane {ly}/{par}: a lane that barely moves")
    if EX_DENS[:2] != [1, 1] or EX_DENS[2:4] != [2, 2] or set(EX_DENS[4:13]) != {3} or set(EX_DENS[13:]) != {4}:
        errs.append(f"channels playing per bar: 1 in the first two bars, 2 in the next two, 3 in the verse, 4 from the bridge on; got {EX_DENS}")
    if EX_INTRO != ["C", "Am", "F", "G"] or any(c not in CHORDS for c in EX_INTRO) or EX_INTRO[-1] != "G" or CH[0] != [(16, "C")]:
        errs.append("the intro is C | Am | F | G and leads to the C of the pickup bar")
    for need in ("120 BPM", "33 bars = 66 seconds", "C | Am | F | G", "4 + 9 + 4 + 8 + 8 bars", "octave higher"):
        if need not in EX_STRONG:
            errs.append(f"the clear plan must say '{need}'")
    # ---- the hero art, used whole: its pixels sit inside the viewBox with room to spare
    hp = os.path.join(HERE, "art", "hero.png")
    if not os.path.exists(hp):
        errs.append("art/hero.png is missing")
    else:
        x0, y0, x1, y1 = alpha_bbox(hp)
        if min(x0 - HX, y0 - HY, HX + HW - 1 - x1, HY + HH - 1 - y1) < 40:
            errs.append(f"hero art {x0, y0, x1, y1} is closer than 40 units to the viewBox {HX, HY, HX + HW, HY + HH}")
    # no slide bullet may end mid-sentence (apostrophe-s, or a dangling article/preposition/possessive)
    dangling = {"a", "an", "the", "of", "to", "at", "in", "on", "for", "and", "or", "with", "your", "each", "every", "their", "its", "from", "by",
                "as", "is", "are", "that", "than", "but", "my"}
    for i, s in enumerate(SLIDES, start=1):
        for b in [x.strip() for x in s[3].split("|") if x.strip()]:
            last = re.sub(r"[^\w’']", "", b.split()[-1]).lower()
            if b.endswith(("’s", "'s")) or last in dangling:
                errs.append(f"slide {i} bullet looks truncated: '{b}'")
    # slide notes that name a page number name a page that exists and is the right one
    ok_pages = {pg(k) for k in ("plan", "chart1", "channels", "arps", "drums", "layers")}
    for i, s in enumerate(SLIDES, start=1):
        for m in re.finditer(r"\bpage (\d+)\b", s[4]):
            if int(m.group(1)) not in ok_pages:
                errs.append(f"slide {i} notes name page {m.group(1)}, which is not a page the notes mean to cite")
    # rendered-pixel check: no drawing's non-background pixel touches the edge of its render box
    from PIL import Image
    import numpy as np
    for k in (DRAWINGS if "--check" in sys.argv else ()):   # needs the rendered PNGs, so only on --check (the build renders them)
        if k == "hero":
            continue
        p = os.path.join(HERE, "build", f"deck-{k}.png")
        if not os.path.exists(p):
            errs.append(f"build/deck-{k}.png is missing: run python3 gen.py first")
            continue
        g = np.array(Image.open(p).convert("L"))
        e = 3
        for side, strip in (("top", g[:e, :]), ("bottom", g[-e - 2:-2, :]), ("left", g[:, :e]), ("right", g[:, -e:])):
            if strip.min() < 250:
                errs.append(f"drawing '{k}' touches the {side} edge of its render box (clipped art)")
    return errs


def edge_errors(path, label):
    """Rendered-pixel check: no art touching the image edges. The top rows and the left and right columns above the black band are
    white; the black band, if any, runs to the bottom edge; the blank strip above the band is no taller than 10% of the image."""
    from PIL import Image
    import numpy as np
    errs = []
    g = np.array(Image.open(path).convert("L"))
    h, w = g.shape
    dark = (g < 60).mean(axis=1)
    top = h
    while top > 0 and dark[top - 1] > 0.6:
        top -= 1
    if top == h:
        errs.append(f"{label}: no black band along the bottom edge")
        top = h - 1
    edge = max(6, w // 250)
    if g[:edge, :].min() < 215:
        errs.append(f"{label}: something touches the top edge")
    if g[:top - 4, :edge].min() < 215 or g[:top - 4, w - edge:].min() < 215:
        errs.append(f"{label}: something touches the left or right edge")
    rows = (g[:top, edge:w - edge].min(axis=1) > 225)
    run = 0
    y = top - 1
    while y >= 0 and rows[y]:
        run += 1
        y -= 1
    if run > 0.1 * h:
        errs.append(f"{label}: a blank band of {run}px sits above the black band (more than 10% of the image)")
    return errs


def verify_outputs(flat, stext, notes):
    errs = []
    alldeck = " ".join(stext + notes)
    txt = " ".join(flat)
    if "No audio" not in notes[0]:
        errs.append("deck slide 1 notes must say 'No audio'")
    for need in ("No audio, recordings, lyrics, artists or albums", "invented plan on paper", "public domain", "John Francis Wade", "1751", "1930 or earlier",
                 "No student work is included", "Arpeggiator", "Bitcrusher", "Resolution", "Downsampling", "one note at a time", "MIDI FX",
                 "Created with the help of digital and AI tools. Notation and answer keys are verified before release."):
        if need not in txt:
            errs.append(f"PDF must say: '{need}'")
    if "What changed" in txt or "Kept as I wrote it" in txt or "my project menu" in txt or "my Digital Music Production" in txt:
        errs.append("ORIGINAL kit: no wording about changes to an owner's sheet")
    if "checked by hand" in txt or "handmade" in txt.lower() or "classroom-tested" in txt.lower() or "hand-checked" in txt.lower():
        errs.append("never claim hand checks or classroom testing for a new product")
    if GRADES_TEXT != "9–12" or "Grades 9–12" not in txt:
        errs.append("PDF: 'Grades 9–12'")
    for w in ("colour", "favour", "centre", "licence", "grey", "metre", "organis", "recognis", "practise", "analyse"):
        if w in txt.lower().replace("greyscale", ""):
            if w == "grey" and "grey lines" in txt.lower():
                continue
            errs.append(f"US spelling: '{w}' in the PDF")
    import subprocess

    def raw(key):
        return re.sub(r"\s+", " ", subprocess.run(["pdftotext", "-raw", "-f", str(D.IX(key)), "-l", str(D.IX(key)), D.files()["pdf"], "-"],
                                                   capture_output=True, text=True, check=True).stdout)
    for key, (lo, hi) in (("chart1", (0, 9)), ("chart2", (9, 17)), ("chart3", (17, 21))):
        r = raw(key)
        for i in range(lo, hi):
            if bar_text(CHART[i]) not in r:
                errs.append(f"{key} page: bar {i + 1} '{bar_text(CHART[i])}' is not printed")
            if chord_text(CH[i]) not in r:
                errs.append(f"{key} page: the chords of bar {i + 1} are not printed")
    r3 = raw("chart3")
    for i, spans in enumerate(CH):
        want = " · ".join(f"{BASS_ROOT[ch]} {LEN_NAMES[ln]}" for ln, ch in spans)
        if want not in r3:
            errs.append(f"chart3 page: the bass line of bar {i + 1} '{want}' is not printed")
    ra = raw("arps")
    for nm in CHORD_ORDER:
        if " – ".join(chord_letters(nm)) not in ra or " ".join(pname(m) for m in arp_seq(nm, "up", 8)) not in ra:
            errs.append(f"arps page: chord {nm} (spelling and Up arpeggio) is not printed")
    for kind, head, *_ in ARPS:
        if head.lower() not in ra.lower() or " ".join(pname(m)[:-1] for m in arp_seq("C", kind)) not in ra:
            errs.append(f"arps page: card {head} or its C-chord sequence is not printed")
    pat_pages = " ".join(flat[D.IX("drums") - 1:D.IX("drums")])
    for p in PATTERNS:
        if p["name"].lower() not in pat_pages.lower():
            errs.append(f"noise drum card {p['name']} missing")
    ch = " ".join(flat[D.IX("channels") - 1:D.IX("channels")]).lower()
    for need in ("square wave", "pulse wave", "triangle wave", "noise", "bitcrusher", "one note at a time", "lead", "arps", "bass", "drum"):
        if need not in ch:
            errs.append(f"channels page must say '{need}'")
    ex = " ".join(flat[D.IX("example") - 1:D.IX("example2")])
    for need in ("240 ÷ 120 = 2", "33 bars = 66 seconds", "4 + 9 + 4 + 8 + 8 bars = 33"):
        if need not in ex:
            errs.append(f"worked example must say '{need}'")
    lay = flat[D.IX("layers") - 1]
    for need in ("Step 6: arrange", "bars × 240 ÷ BPM", "45 to 75"):
        if need not in lay:
            errs.append(f"layer map page must say '{need}'")
    if "Step 2: plan" not in flat[D.IX("plan") - 1] or "Step 3 of the project sheet" not in flat[D.IX("chart1") - 1]:
        errs.append("My plan page must say 'Step 2: plan' and the first chart page 'Step 3 of the project sheet'")
    up = open(os.path.join(HERE, "UPLOAD.md"), encoding="utf8").read()
    if "Grades 9-12" not in up or "`9th-grade`, `10th-grade`, `11th-grade`, `12th-grade`" not in up:
        errs.append("UPLOAD.md: grades 9-12 in the description and section 3")
    if "no audio" not in up.lower() or "Open question" not in up or "public domain" not in up or "Transcriptions used" not in up:
        errs.append("UPLOAD.md: must say no audio is included, say public domain, name the transcriptions used and record the open questions")
    m = re.search(r"= 1 cover \+ (\d+) teacher \+ (\d+) student \+ 1 terms page", up)
    if not m or 2 + int(m.group(1)) + int(m.group(2)) != len(PLAN):
        errs.append("UPLOAD.md: the page-count list (1 cover + teacher + student + 1 terms) must total the PDF's pages")
    if m and (int(m.group(1)) != D.IX("example2") - 1 or int(m.group(2)) != D.IX("reflect") - D.IX("chart1") + 1):
        errs.append("UPLOAD.md: teacher and student page counts must match the plan")
    for t in TAGS:
        if t not in up:
            errs.append(f"UPLOAD.md: tag {t} missing")
    for banned in ["Billie", "Beatles", "Daft", "Skrillex", "Disney", "Radiohead", "Billboard", "Ro" + "land", "Bensound", "Ableton "]:
        if banned in alldeck or banned in txt:
            errs.append(f"must not name artists, albums, songs, sites, services or other brands ({banned})")
    # the cover and previews: nothing touches an edge; no big blank band
    F = D.files()
    for p in [F["cover"], *F["pv"]]:
        errs += edge_errors(p, os.path.basename(p))
    return errs


def check_summary():
    return (f"O Come, All Ye Faithful ({NBARS} chart bars, {note_count()} notes): transcription A (G major) moved up 5 semitones equals transcription B "
            f"(C major) and the chart, note for note and length for length; every bar adds to 16 sixteenths; every chord is spelled by thirds in C major "
            f"and holds each span's first and longest note; arpeggio sequences, bass roots and {len(PATTERNS)} noise drum patterns match their cards; "
            f"length helper correct ({BARS_MIN}-{BARS_MAX} bars at {TEMPO_LO}-{TEMPO_HI} BPM = {LEN_LO}-{LEN_HI} s); the worked example is {EX_BARS} bars at "
            f"{EX_BPM} BPM = {EX_BARS * EX_BAR_S:g} s (sections {'+'.join(str(b - a + 1) for _, a, b in EX_SECTIONS)}, {len(EX_CH)} channels, "
            f"{len(EX_AUTO)} moving lanes); hero art inside its viewBox; edges of cover.png and previews clear; no audio, lyrics, artist names or student "
            f"work; grades 9-12; tags and subjects are not headings; no 'what changed' page (ORIGINAL).")


# ================================================================ UPLOAD.md (written by gen.py so every number matches the build)
def write_upload():
    from html import unescape
    np_, ns = len(PLAN), len(SLIDES)
    n_teacher = (PLAN.index("example2") + 1) - 1
    n_student = (PLAN.index("reflect") + 1) - (PLAN.index("chart1") + 1) + 1
    assert 2 + n_teacher + n_student == np_, "page-count list must total the PDF"
    nt = len(LISTING_TITLE)
    desc = (f"{DESC_START} students arrange the public-domain carol “O Come, All Ye Faithful” as an 8-bit game tune in Logic Pro. They enter the melody from a "
            f"piano-roll note chart on a square-wave lead, play the chords as arpeggios with the Arpeggiator, add a triangle-wave bass and a noise drum, "
            f"and crush it with a Bitcrusher. This 8-Bit Holiday project takes {CLASSES} class periods and is an original Hudson Beat project; the steps are written for Logic Pro, "
            f"while the ideas (square, triangle and noise channels, arpeggios and a lo-fi crush make a chiptune) carry over to GarageBand, Ableton Live and BandLab.\n\n"
            f"WHAT'S INCLUDED (ZIP: {np_}-page PDF = 1 cover + {n_teacher} teacher + {n_student} student + 1 terms page, plus {ns}-slide intro deck as .pptx and PDF)\n"
            f"• Teacher pages: how to use, project overview, setup, a {CLASSES}-class pacing guide with the deck slides for each class, two pages of teacher notes "
            f"(struggles, variations, resources, grading), a Logic quick reference, the tune's sources and the public-domain rule, and a two-page worked "
            f"example (an invented plan on paper: the carol as a 66-second tune at 120 BPM, with its four channels, an intro, a 33-bar map and two automation lanes) ({n_teacher} pages)\n"
            f"• Student pages: three piano-roll note-chart pages with every note listed bar by bar, the chords and a bass line for all 21 bars, a page on the four channels "
            f"(square, pulse, triangle and noise) and the Bitcrusher, arpeggio cards (every chord of the carol spelled out, four arpeggio patterns), four noise drum "
            f"patterns with grids, My plan, a Layer map with a length helper, the 3-page project sheet (overview, goals, vocabulary, requirements, steps, tips, "
            f"submission checklist), the /25 rubric, a vocabulary page, a feedback planner and a reflection page ({n_student} pages)\n"
            f"• Teacher-presented intro deck, {ns} slides with speaker notes on every slide: a think-and-share hook, what the project is, how to read a "
            f"piano roll, the four chip channels, arpeggios, building the sound, noise drum patterns, a worked-example map, what to turn in and the rubric\n\n"
            f"THE FOUR CLASS PERIODS\n"
            f"• Class 1: hook; read the chart; fill in My plan; enter the melody on a square-wave lead\n"
            f"• Class 2: build the channels: arpeggios with the Arpeggiator, a triangle bass and the chip sounds\n"
            f"• Class 3: add the noise drum and the Bitcrusher; plan the form and arrange 31 to 35 bars\n"
            f"• Class 4: bounce and hand in; presentations with feedback questions; reflection\n\n"
            f"WHAT STUDENTS LEARN\n"
            f"• Entering and editing notes in Logic Pro's Piano Roll from a note chart\n"
            f"• Spelling the chords of a key and playing them as arpeggios\n"
            f"• Why a game chip has square, triangle and noise channels that play one note at a time, and how to build them with a synthesizer\n"
            f"• Using a Bitcrusher and automation to make a lo-fi sound that changes from section to section\n"
            f"• Planning a 45 to 75 second arrangement in bars and seconds (bars × 240 ÷ BPM), then explaining their choices in a reflection\n\n"
            f"GOOD TO KNOW\n"
            f"• There is no audio in this resource and no student work. The carol is in the public domain (attributed to John Francis Wade, c. 1743; first published 1751) "
            f"and appears only as a note chart, with no lyrics; students make every sound themselves in Logic Pro\n"
            f"• “O Come, All Ye Faithful” is a Christian Christmas carol; offer it where carols suit your school, or let students bring a public-domain tune you approve\n"
            f"• Requires Logic Pro on a Mac. A MIDI keyboard is not needed; nobody has to read staff notation\n"
            f"• Rubric: 5 categories scored 1-5, /{RUBRIC_TOTAL}; the final grade is the average of the student's and the teacher's score\n"
            f"• Grades 9-12; music technology or music production classes\n"
            f"• The deck uses the free Oswald and Source Sans 3 fonts (built into Google Slides); install them for PowerPoint or Keynote, or present "
            f"the PDF copy, which shows the intended look\n"
            f"• Every student page prints well in black and white\n\n"
            f"Logic Pro is a product of Apple Inc., named only to describe compatibility. This resource is not affiliated with Apple.\n\n"
            f"{D.DISCLOSURE_NEW}")
    md = f"""# UPLOAD: 8-Bit Holiday, original Logic Pro project (TpT 053)

These fields follow the order of TpT's "Add a resource" form. `tools/tpt.js publish` reads the title and description from the code blocks under 1 and 2, and everything else from `tpt.json`. This file is written by `gen.py`; edit the text there.

**Files to attach**
- Resource (digital download): `{SLUG}.zip`. It holds three files in a folder "{ZIP_DIR}":
  - `{SLUG}.pdf`: the teacher and student resource, {np_} pages, US Letter portrait.
  - `{SLUG}-intro-deck.pptx`: the teacher-presented intro deck, {ns} slides (16:9), speaker notes and a Class badge on every slide.
  - `{SLUG}-intro-deck.pdf`: a PDF copy of the deck, {ns} pages.
- Thumbnails, in this order: `cover.png`, `preview-1.png`, `preview-2.png`, `preview-3.png` (all 2000 × 2000).
- Preview file: `{SLUG}-PREVIEW.pdf`, 4 watermarked pages.

TpT takes one product file, so the PDF, the .pptx and the deck PDF go up together as the ZIP (`files.product` in tpt.json; `zip_contents` lists what is inside). **No audio, video, lyrics, recordings, presets, screenshots, student work or Logic sessions are in the ZIP.**

**Page count, adding up to the PDF:** 1 cover + {n_teacher} teacher + {n_student} student + 1 terms = {np_} pages; plus {ns} slides = {np_ + ns} for TpT's "Number of pages or slides".

## 1. Title

```
{LISTING_TITLE}
```
({nt} characters; the limit is 80.) The title leaves out Holiday, Winter, Christmas and carol because TpT's Seasonal Titles notice blocked a holiday-named title on 027 (see 032, 033 and 034). "Logic Pro" sits in the first 30 characters.

## 2. Description

```
{desc}
```

## 3. Grades

9th, 10th, 11th, 12th (`9th-grade`, `10th-grade`, `11th-grade`, `12th-grade` in tpt.json), as tpt/METADATA-GUIDE.md prescribes for every music-production item.

## 4. Subjects and tags

- Subjects in tpt.json: Music; Computer Science - Technology; Music Composition (all three are in `tpt/SUBJECT-OPTIONS.json` and none is a heading)
- Tags in tpt.json: {", ".join(TAGS)} (four exact entries of `tpt/TAG-OPTIONS.json`; the limit is 6). "Holiday" and "Student Practice" are headings and are not used.
- Formats: PDF (add PowerPoint or ZIP if TpT offers it)
- Answer key: left out of tpt.json (there is none; the worked example is a model)

## 5. Resource type

- Projects
- Unit Plans
- PowerPoint Presentations

## 6. Standards (optional)

National Core Arts Standards, Music (Music Technology, high school): MU:Cr1.1, MU:Cr2.1, MU:Pr6.1, MU:Re7.2. Tag only if it matches how the teacher uses it.

## 7. Price

**${PRICE}** (paid), multiple-license price ${PRICE}. The $8 set in the queue, inside the $7-9 holiday-kit range, for a kit with {np_} pages + {ns} slides, three note-chart pages with a bass line, four channel cards, arpeggio cards, four noise drum patterns and a two-page worked example, listed in November and December.

## 8. Free or paid / free preview pages

Paid. Preview PDF (4 watermarked pages): the {CLASSES}-class pacing guide, the first note-chart page, the arpeggio cards and the /25 rubric. "Number of pages or slides" is {np_ + ns} ({np_} pages + {ns} slides).

## 9. Before you click publish

- [ ] **Needs QA approval first.** This is a new kit (not yet on TpT); the Manager releases it only after a QA `**Verdict: APPROVED**`.
- [ ] Cover and previews show "HUDSON BEAT" in type; PDF footers read "© 2026 Brian Lotze · Hudson Beat · For single-classroom use".
- [ ] No school name, logo, student names or work, audio, video, lyrics or Logic session anywhere (`gen.py --check` scans every output and every file in this folder).
- [ ] **Tune is public domain (year and source for QA.md).** "O Come, All Ye Faithful" (Adeste fideles), the tune attributed to John Francis Wade (about 1711-1786). Hymn books date it to about 1743 (the Open Hymnal score says "1743"); the earliest dated Wade manuscript (Stonyhurst College) and the first printed publication are of 1751 (Wikipedia, "O Come, All Ye Faithful"). All of these are far before the 1930 cutoff. No lyrics are printed (the English words, Oakeley 1841, are also old but are not used); no recordings and no editions are used.
- [ ] **Transcriptions used (two independent, in two keys, plus a third check).** (A) the Open Hymnal Project ABC file "O_Come_All_Ye_Faithful-Adeste_Fideles-Portugese_Hymn.abc" (public domain, setting from "A Hymnal", Episcopal, 1916, hymn 72; G major), melody voice only. (B) an independent ABC file typed in C major from a public hymn-tune repository (SBurrell23/Sheets, songs/hymns/o-come-all-ye-faithful.abc), which agrees with A bar for bar once A is moved up five semitones. (C) a third G-major ABC file (avnerdorman/abc-solfege-tool, songs/O_Come_All_Ye_Faithful_G.abc) agrees with A on every note. `gen.py --check` parses A and B, proves A + 5 semitones = B = the chart, and proves every bar adds to 16 sixteenths. Pitches and lengths only; no engraving or edition is reproduced.
- [ ] **Original project.** Built with `ORIGINAL = True` in `tpt/_dmp2_common/dmp2.py` (like 031, 036 and 040): no "what changed" page and the new disclosure line. The reflection page is the shared Reflection element, scored in the rubric's "Plan & Reflection" row. `dmp2.py` is unchanged.
- [ ] **Art.** The cover, previews and deck use the owner's pre-made art (`art/hero.png`, the pixel snowman on a handheld console, no text), copied whole from `tpt/_art/next/8-bit-holiday/`; the file is logged in `tpt/_art/USAGE.md`. Everything else is drawn in code. Needs art: none.
- [ ] **Logic Pro names to confirm on a Mac with a current Logic.** Retro Synth (Analog engine: square, pulse and triangle waves, pulse width, Mono) and Alchemy (hedged: "if your version offers one"), the Arpeggiator MIDI plug-in in a MIDI FX slot (Note Order Up, Down, Up & Down; Rate 1/16; Octave Range; the pages say that some versions repeat the end notes in Up & Down), Drum Machine Designer and its Step Sequencer, a noise source in Retro Synth or Alchemy (hedged), Bitcrusher (Distortion group; Resolution, Downsampling, Mix), Channel EQ, automation (A), the Mixer (X), Region inspector Transpose, Command-B bounce. Logic names middle C "C3" by default, so the kit says to subtract one from the chart's octave number. Nothing says a loop or preset of a given name exists.
"""
    md += f"""- [ ] **Open questions for the owner:** (1) **One variant bar.** In chart bar 13 (hymn-book bar 12) the chart passes through E (F# dotted quarter, E eighth, D, G), as the 1916 hymnal and two other transcriptions do; the Wikipedia LilyPond score and one four-voice ABC file hold the F# for two beats instead. Both are heard in practice; the teacher page says so. (2) **Title.** No Holiday, Winter, Christmas or carol in the title because of TpT's seasonal-title notice (see 1). (3) **Price.** $8, as in the queue. (4) **Religious content.** The carol is a Christian hymn; the teacher setup page offers a secular alternative (any public-domain tune the teacher approves, with a blank piano roll on My plan).
"""
    with open(os.path.join(HERE, "UPLOAD.md"), "w", encoding="utf8") as f:
        f.write(md)


if __name__ == "__main__":
    if "--check" not in sys.argv:
        write_upload()
    D.main(sys.modules[__name__])
