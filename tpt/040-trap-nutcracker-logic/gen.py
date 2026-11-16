#!/usr/bin/env python3
"""Logic Pro project kit: Trap Nutcracker (TpT 040): the teacher resource, the intro deck and the listing files.

    python3 gen.py            build everything into this folder (also writes UPLOAD.md)
    python3 gen.py --lowres   same, but square images at scale 1 and small page shots (self-check only; --check rejects it)
    python3 gen.py --check    verify content, melodies, drum patterns, hi-hat roll numbers, the flips, the worked example, drawings, files,
                              page/slide counts, class slots, notes, fonts, fit and overlap, overflow and dead space, banned strings,
                              tpt.json and UPLOAD.md

An ORIGINAL Hudson Beat project (dmp2.ORIGINAL = True, like 031 and 036). Students flip one of two public-domain Tchaikovsky themes
(The Nutcracker, 1892) into a trap beat: a 4-bar loop (melody and chords) over a half-time drum pattern, hi-hat rolls and an 808 sub bass.
The two themes are given as piano-roll note charts, drawn here in code from the note lists below (pitch, start and length in sixteenth
notes) and checked against them:

  Dance of the Sugar Plum Fairy: the celesta tune, score bars 5-12 (the first 8 bars of the melody), E minor. Tchaikovsky, The Nutcracker
      (Act II, Variation II of the Pas de deux; No. 3 of the Op. 71a suite), 1892. Public domain.
  Trepak (Russian Dance): the main theme, score bars 1-8, G major. Tchaikovsky, The Nutcracker (Act II divertissement; No. 4 of the Op. 71a
      suite), 1892. Public domain.

Both are 2/4 in the score. Two score bars are written as one 4/4 bar here (4 chart bars = 8 score bars), so a student can set up Logic in 4/4 at
a trap tempo. The Sugar Plum chart is the score pitches moved down an octave; the Trepak chart is at score pitch.
Transcription used (pitches only; no engraving, no edition is reproduced): Sugar Plum Fairy: Ted Muller's celesta part (tedmuller.us, a
free transcription of the score: MusicXML and MIDI), bar by bar; the top note of the celesta's two-note chords is the tune. A second free MIDI
sequence (classicalmidi.co.uk) agrees on every melody note but one (chart bar 3, second half-bar, second note: B in Muller's celesta part,
D in the other file; the chart uses B). Trepak: the melody line of the sequence on classicalmidi.co.uk (Elias Bustos Maure), checked
against the tune as published in piano reductions. NO AUDIO, no recordings, no lyrics: students make every sound in Logic Pro.
Every picture (hero, cards, piano rolls, hi-hat roll diagram, drum grids, flips, arrangement map) is drawn in code. The shared builder is
../_dmp2_common/dmp2.py (see its README).
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "_dmp2_common"))
import dmp2 as D  # noqa: E402

ORIGINAL = True
SLUG = "trap-nutcracker"
TITLE = "Trap Nutcracker"
ACCENT = "#6B3FA0"          # this product's single accent: sugar-plum purple
ACC_LIGHT = "#E8DDF4"
PRICE = "9.00"
CLASSES = 4
GRADES_TEXT = "9–12"
GRADE_SLUGS = ["9th-grade", "10th-grade", "11th-grade", "12th-grade"]
TAGS = ["Winter", "Christmas-Chanukah-Kwanzaa", "Project-based Learning", "Projects"]     # exact entries of tpt/TAG-OPTIONS.json, none a heading
SUBJECTS = ["Music", "Computer Science - Technology", "Music Composition"]     # METADATA-GUIDE (a); all in SUBJECT-OPTIONS.json, none a heading
ANSWER_KEY = None
LISTING_TITLE = "Trap Beat in Logic Pro | Tchaikovsky Flip Project | High School Music Tech"
DESC_START = "Trap beat making for high school music technology:"
DESC_MUST = ["Trap Nutcracker", "piano-roll", "no audio", "Sugar Plum Fairy", "Trepak", "public domain", "808", "hi-hat", "Tchaikovsky"]
ZIP_DIR = "Trap Nutcracker - Hudson Beat"
ZIP_DATE = (2026, 11, 14, 12, 0, 0)
TYPE = "Original Project"
PROJ_LINE = "Music Technology | <i>Beat-Making Project</i> | 4 class periods"
DECK_STRAP = "Tchaikovsky, flipped"
REFLECT_ROW = "Plan &amp; Reflection"
# split so this file never contains them (the --check scan reads every file in this folder)
BANNED_EXTRA = ["Rud" + "olph", "Fro" + "sty", "Gri" + "nch", "Santa Claus " + "Is", "Jingle Bell " + "Rock", "Feliz " + "Navidad",
                "Mari" + "ah Carey", "Pentato" + "nix", "Trans-" + "Siberian", "Home " + "Alone", "Spoti" + "fy", "You" + "Tube",
                "Metro " + "Boomin", "Travis " + "Scott", "Fantas" + "ia", "Balan" + "chine", "TR-" + "808"]

# ================================================================ the project text (original; students read these pages)
OVERVIEW = ("Flip Tchaikovsky into a trap beat. Choose one of two public-domain themes from The Nutcracker (1892), enter its four-bar "
            "melody and chords into Logic Pro from a piano-roll note chart, then build a half-time trap beat around it: a heavy snare, "
            "rolling hi-hats, a gliding 808 sub bass and a flipped, chopped version of the tune. Your finished beat is 60 to 90 seconds "
            "long at 130 to 150 BPM, and people should still be able to name the theme.")
GOALS = ["Enter a melody and chords into Logic Pro’s Piano Roll from a note chart, with the right pitches and lengths",
         "Program a half-time trap drum pattern with hi-hat rolls, and an 808 sub bass on the chord roots, at 130 to 150 BPM",
         "Flip a melody on purpose (chop it, move it up or down an octave, reverse it) and explain what each flip does",
         "Plan, build and mix a 60 to 90 second beat with an intro, beat sections, a break, a drop and an outro"]
VOCAB = [("Trap", "A style of hip-hop from the southern United States with a half-time feel, a heavy 808 sub bass, snappy snares and fast, rolling hi-hats"),
         ("808", "A deep, long, pitched bass sound that is part drum and part bass note; it plays the chord roots and can glide between notes"),
         ("Hi-hat roll", "A burst of very fast hi-hat notes, often triplets or 32nd notes, that speeds up or swells in volume"),
         ("Flip", "To remake an existing melody into something new by changing its rhythm, register or sound, while keeping it recognizable")]
REQS = ["Choose one of the two themes (or a melody your teacher approves) and enter its four-bar melody into a Software Instrument track "
        "in Logic Pro; every pitch and length matches the chart",
        "Set a tempo from 130 to 150 BPM and build a half-time drum pattern (page @DRUMS) with the snare or clap on beat 3",
        "Play the chords of the loop under the melody, and add an 808 sub bass on the chord roots",
        "Use at least four of the five trap moves: hi-hat rolls, an 808, a half-time snare, a flipped melody and a riser and drop (pages @FX1–@FX2)",
        "Build a 60 to 90 second arrangement with at least five layers, an intro, beat sections, a break and an outro",
        "Reflect on how the beat went, in writing or out loud (page @REFLECT)"]
FILE_NAME = "“Your Name – Trap Nutcracker – Theme”"
STEPS = ["<b>Choose</b> — Pick one theme and read its chords (note charts: pages @SUGAR and @TREPAK)",
         "<b>Plan</b> — Fill in your Beat plan: tempo, drum pattern, chords, and which trap moves you will use (page @PLAN)",
         "<b>Enter the melody and chords</b> — Draw the chart into the Piano Roll and listen for wrong notes (Logic quick reference: page @LOGICREF)",
         "<b>Build the beat</b> — Program a drum pattern (page @DRUMS), add hi-hat rolls and an 808 on the chord roots, and flip the melody (page @FLIPS)",
         "<b>Make it hit</b> — Shape the 808, the snare and the sounds, and add a riser and a drop (pages @FX1–@FX2)",
         "<b>Arrange and mix</b> — Plan the form on the Arrangement plan (page @ARRANGE), build 60 to 90 seconds with an intro, beat "
         "sections, a break and an outro, balance with volume, pan and EQ, and bounce with the file name format",
         "<b>Present &amp; get feedback</b> — Write three questions you want classmates to answer about your beat. Play it, say which "
         "trap moves you used, and answer at least 2 of each classmate’s questions. Then reflect (page @REFLECT)."]
TIPS = ["Trap is about space. Leave room for the 808 and the snare, and let the tune be the star.",
        "Keep the melody in a different register from the 808: if they overlap, one of them disappears.",
        "Add one layer at a time and listen before you add the next. Hi-hat rolls work best when they are rare.",
        "Save a new version of your project before each big experiment, so you can always go back."]
CHECK = ["Bounced .mp3 or .wav handed in where your teacher says",
         "Zipped .logicx project file handed in",
         f"Files named correctly: {FILE_NAME}",
         "Beat plan, Arrangement plan and Reflection page handed in",
         "Rubric self-score done (page @RUBRIC)",
         "I can name the trap moves I used and what each one does"]
RUBRIC_NOTE = "Each category is scored 1–5. Score yourself first; your final grade is the average of your self-score and your teacher’s score."
LEVELS = [1, 2, 3, 4, 5]
RUBRIC = [
    ("Melody & Chords", ["The melody is missing or mostly wrong", "Several wrong pitches or lengths; chords missing or clashing",
                         "Mostly right, with a few slips; chords fit most of the loop",
                         "Every pitch and length matches the chart; the chords fit",
                         "Exact, with chords and an 808 that support the melody; the theme is unmistakable"]),
    ("Trap Beat", ["No clear drum pattern or tempo", "A drum pattern, but not half-time, or outside 130 to 150 BPM",
                   "A steady half-time pattern in range, with a few hi-hat changes", "Half-time snare, kick and hats that fit the tempo, with at least one hi-hat roll",
                   "A heavy, moving groove: kick, snare, hats and rolls lock with the 808"]),
    ("808 & Sound", ["No 808 or sub bass", "An 808, but hard to hear or off the chord roots", "An 808 on the chord roots and at least four trap moves, each audible",
                     "A gliding, controlled 808, four or five moves, and the student can say what each does",
                     "Every move is used on purpose, with automation, and the theme is still clear"]),
    ("Arrangement & Mix", ["No clear form; layers cover each other", "A loop with little change; muddy mix",
                           "Intro, beat sections and outro; mostly balanced", "Clear form with a break and a drop; layers enter and leave; clean mix",
                           "A form that builds and resolves; every layer audible, melody on top, 808 under control"]),
    ("Plan & Reflection", ["Plans, presentation or reflection missing", "Thin plan; little to say about choices",
                           "Plan and reflection complete, with basic detail", "Clear plan; thoughtful reflection and good answers to questions",
                           "Insightful reflection and a polished, confident presentation"]),
]
RUBRIC_TOTAL = 25
RUBRIC_SHORT = [ds[4] for _, ds in RUBRIC]
RUBRIC_SLIDE_LINE = "Scored 1–5 · final grade = average of your score and mine, out of 25"
LIVE = True   # already on TpT; its release/uploaded markers are the uploader's
RUBRIC_ROW_PITCH = 0.86
RUBRIC_LINE_Y = 6.3

TN_REINFORCES = ("Teaches how a style is built from small choices. Students learn that a half-time snare, an 808, rolling hi-hats and a "
                 "flipped melody, not only the notes, make a beat sound like trap, and they practice entering notes and chords in Logic "
                 "Pro’s Piano Roll.")
STRUGGLES = ["The notes go in but the tune sounds wrong: check the grid setting and the note lengths against the chart, bar by bar "
             "(Logic quick reference, page @LOGICREF). Remember that two bars of the score are written as one 4/4 bar.",
             "The beat sounds busy, not heavy: check that the snare lands on beat 3 only and that the hi-hats are quieter than the snare (page @DRUMS).",
             "The 808 is muddy or vanishes: shorten its notes, sidechain it to the kick or add a little distortion so small speakers can hear it (page @FX1).",
             "The tune disappears: compare with the flips on page @FLIPS and the cards on pages @FX1–@FX2. A flip changes the rhythm or register, "
             "never the order of the pitches, unless it is flip 3 on purpose."]
VAR_EASY = ("Use Trepak, loop one four-bar section for the whole beat, and start from pattern A on the drum patterns page or a Drummer "
            "track in a hip-hop style, then make it half-time.")
VAR_HARD = ("Write a second four-bar section with a different chord order, play the melody twice, once chopped and once an octave up "
            "(see the flips page), and automate the filter and the 808’s distortion across the whole piece. Sugar Plum Fairy is the harder chart: "
            "it has sharps and a pick-up.")
RESOURCES = [("The two note charts (pages @SUGAR and @TREPAK)",
              "Hand out one chart each, or let students choose. Pitch names are printed, so nobody needs to read staff notation."),
             ("Trap drum patterns (page @DRUMS)",
              "Students copy a pattern into the Step Sequencer or use a Drummer track. Pattern D is the sparse one for intros and breaks."),
             ("Flips and effect cards (pages @FLIPS, @FX1–@FX2)",
              "Six versions of one bar of Trepak, then one card each for hi-hat rolls, the 808, the half-time snare, flipping the melody and the riser and drop."),
             ("Worked example (pages @EXAMPLE–@EXAMPLE2)",
              "Sugar Plum Fairy as a 64-second trap beat, planned on paper. Use it as a model, not a template; student projects will differ.")]
TN_NOTE = ("Pairs well with a listening day: play the finished beats without saying the title and let the class name the Tchaikovsky "
           "theme. A tune that people name quickly is a beat that kept the melody.")
GRADING = ["The rubric: five categories, each scored 1–5, /25 (page @RUBRIC). Students score themselves first; the final grade is the "
           "average of their score and yours.",
           "Melody & Chords (rubric row 1): open the project and compare the Piano Roll with the chart, bar by bar. Check that the chords "
           "match the plan.",
           "Trap Beat and 808 & Sound (rubric rows 2 and 3): check the tempo is 130 to 150 BPM, that the snare is half-time, that there is a hi-hat "
           "roll, and that at least four of the five trap moves can be heard and named.",
           "Arrangement and Mix (rubric row 4): compare the project with the Arrangement plan (page @ARRANGE). Is there an intro, beat "
           "sections, a break with a drop and an outro, and can you hear the melody over the 808?",
           "Plan and Reflection (rubric row 5): the Beat plan (page @PLAN), the questions on the feedback planner and the Reflection "
           "page (page @REFLECT) are the evidence."]
PACING = [
    {"n": 1, "owner": "Choose a theme, fill in the Beat plan, and enter the melody and chords.",
     "do": "Slides 1–6: the hook, what the project is, the four classes, the five moves and how to read a piano roll. Hand out the project "
           "sheet, the two charts and the Beat plan. Check that each student has a theme and a tempo before they leave.",
     "slides": (1, 6), "pages": ["sugar", "trepak", "plan", "proj1", "proj2", "proj3", "vocab"],
     "deck": "Tchaikovsky, flipped · five moves · reading a piano roll"},
    {"n": 2, "owner": "Build the beat: drums, hi-hat rolls, 808 and a flipped melody.",
     "do": "Slides 7–9: building the beat, hi-hat rolls and trap drum patterns. Demonstrate the Step Sequencer and a hat roll on the projector, "
           "then work time. Walk the room with one question: where is the snare, and is it only on beat 3?",
     "slides": (7, 9), "pages": ["flips", "drums"], "deck": "Build the beat · hi-hat rolls · trap drum patterns"},
    {"n": 3, "owner": "Make it hit, plan the form, and build the arrangement and mix.",
     "do": "Slides 10–11: the worked example on paper and flip it, drop it. Hand out the Arrangement plan. Then work time; "
           "ask each student to play their first 20 seconds and say which theme they hear.",
     "slides": (10, 11), "pages": ["fx1", "fx2", "arrange"], "deck": "Worked example, 64 seconds · flip it, drop it"},
    {"n": 4, "owner": "Bounce, hand in, present and reflect.",
     "do": "Slides 12–15: what to turn in, the rubric, presentation day and the close. Students bounce, name their files and write "
           "their three feedback questions, then present.",
     "slides": (12, 15), "pages": ["rubric", "present", "reflect"], "deck": "Checklist · rubric · presentations"},
]
PACING_EXTRA = (
    '<div class="cols" style="margin-top:4pt;gap:14pt"><div class="box acc-b"><span class="k">The one thing to do on Class 1</span>'
    '<p style="margin:0;font-size:9.6pt">Make sure every student leaves with a theme, a tempo from 130 to 150 BPM and the chords of their '
    'loop written on the Beat plan. If the tempo is only a guess, tap it: tap a steady beat for ten seconds and count the taps.</p></div>'
    '<div class="box"><span class="k">If you only have three classes</span><p style="margin:0;font-size:9.6pt">Merge Classes 2 and 3: '
    'build the beat and add the 808, rolls and riser on Class 2, then arrange and mix on Class 3 and use Class 4 for bouncing, presentations and reflection.</p></div></div>')
PACING_SIZE = 9.6

# ================================================================ the melodies: (pitch, length in sixteenth notes), chart bar by chart bar
# Lengths: 1 = sixteenth, 2 = eighth, 4 = quarter, 8 = half, 16 = whole. "R" is a rest. One chart bar = two bars of the 2/4 score.
LEN_NAMES = {1: "16th", 2: "eighth", 4: "quarter", 8: "half", 16: "whole"}
_PC = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
BLACK_PC = {1, 3, 6, 8, 10}


def midi(p):
    acc = 0 if len(p) == 2 else (1 if p[1] == "#" else -1)
    return 12 * (int(p[-1]) + 1) + _PC[p[0]] + acc


def pname(m):
    return NAMES[m % 12] + str(m // 12 - 1)


# The notes at SCORE pitch (octave numbers as the score sounds them, middle C = C4), from the transcriptions named at the top.
SRC = {
    # Sugar Plum Fairy, E minor, score bars 5-8 | 9-12 as chart bars 1-4 (each chart bar = two 2/4 bars)
    "sugar": [[("R", 2), ("G6", 1), ("E6", 1), ("G6", 2), ("F#6", 2), ("D#6", 2), ("E6", 2), ("D6", 1), ("D6", 1), ("D6", 2)],
              [("C#6", 1), ("C#6", 1), ("C#6", 2), ("C6", 1), ("C6", 1), ("C6", 2), ("B5", 1), ("E6", 1), ("C6", 1), ("E6", 1), ("B5", 4)],
              [("R", 2), ("G5", 1), ("E5", 1), ("G5", 2), ("F#5", 2), ("C6", 2), ("B5", 2), ("G6", 1), ("G6", 1), ("G6", 2)],
              [("F#6", 1), ("F#6", 1), ("F#6", 2), ("E6", 1), ("E6", 1), ("E6", 2), ("D#6", 1), ("F#6", 1), ("E6", 1), ("F#6", 1), ("D#6", 4)]],
    # Trepak, G major, score bars 1-4 | 5-8 as chart bars 1-2, 3-4 ... (two 2/4 bars per chart bar)
    "trepak": [[("G5", 2), ("G5", 1), ("F#5", 1), ("G5", 2), ("G5", 2), ("E5", 2), ("D5", 2), ("C5", 2), ("E5", 2)],
               [("D5", 2), ("D5", 1), ("C#5", 1), ("D5", 2), ("D5", 2), ("B4", 2), ("A4", 2), ("G4", 2), ("B4", 1), ("D5", 1)],
               [("A4", 2), ("A4", 1), ("D5", 1), ("G4", 2), ("G4", 1), ("D5", 1), ("F#4", 2), ("F#4", 1), ("D5", 1), ("A4", 2), ("A4", 1), ("D5", 1)],
               [("B4", 2), ("B4", 1), ("D5", 1), ("G4", 2), ("G4", 1), ("D5", 1), ("A4", 2), ("G4", 2), ("A4", 1), ("D5", 1), ("E5", 1), ("F#5", 1)]],
}
SHIFT = {"sugar": 12, "trepak": 0}      # semitones the chart is moved DOWN from score pitch


def moved(bars, semis):
    return [[(p if p == "R" else pname(midi(p) - semis), d) for p, d in bar] for bar in bars]


SUGAR = moved(SRC["sugar"], SHIFT["sugar"])
TREPAK = moved(SRC["trepak"], SHIFT["trepak"])
# chords: per chart bar, [(length in sixteenths, chord)] spanning the bar; one idea that fits, not the only one
SUGAR_CH = [[(8, "Em"), (8, "B7")], [(4, "C#dim7"), (4, "Cdim7"), (8, "Em")], [(8, "Em"), (8, "Cmaj7")], [(16, "B7")]]
TREPAK_CH = [[(8, "G"), (8, "C")], [(8, "D"), (8, "G")], [(4, "D"), (4, "G"), (8, "D")], [(4, "Em"), (4, "G"), (8, "D")]]
CHORD_TONES = {"Em": {"E", "G", "B"}, "B7": {"B", "D#", "F#", "A"}, "C#dim7": {"C#", "E", "G", "A#"}, "Cdim7": {"C", "D#", "F#", "A"},
               "Cmaj7": {"C", "E", "G", "B"}, "G": {"G", "B", "D"}, "C": {"C", "E", "G"}, "D": {"D", "F#", "A"}}
BASS_ROOT = {"Em": "E1", "B7": "B1", "C#dim7": "C#2", "Cdim7": "C2", "Cmaj7": "C2", "G": "G1", "C": "C2", "D": "D2"}
SCALE_PCS = {"sugar": {"B", "C", "C#", "D", "D#", "E", "F#", "G"}, "trepak": {"A", "B", "C", "C#", "D", "E", "F#", "G"}}

TUNES = {
    "sugar": dict(title="Dance of the Sugar Plum Fairy", part="the celesta theme, first 8 melody bars", who="Tchaikovsky, The Nutcracker", yr="1892",
                  src="The celesta tune from Act II of Tchaikovsky’s Nutcracker ballet (Variation II of the Pas de deux, No. 3 of the Op. 71a suite), "
                      "first performed in 1892. This chart is score bars 5 to 12, with the pitches moved down an octave.",
                  key="E minor", time="4/4", bar_len=16, beat=4, bars=SUGAR, chords=SUGAR_CH, lo=64, hi=79, row_h=22, systems=[(0, 4)],
                  good="The challenge: a pick-up, a chromatic step-by-step fall (D#, D, C#, C) and seventh chords. It already sounds like a trap melody, dark and bell-like.",
                  tip="Bars 1 and 3 start with an eighth rest (the celesta comes in on the “and”). The last chord, B7, leads straight back to Em, so the loop turns around."),
    "trepak": dict(title="Trepak (Russian Dance)", part="the main theme, first 8 bars", who="Tchaikovsky, The Nutcracker", yr="1892",
                   src="The main theme of the Russian Dance from Act II of Tchaikovsky’s Nutcracker ballet (No. 4 of the Op. 71a suite), first performed "
                       "in 1892. This chart is score bars 1 to 8, at score pitch.",
                   key="G major", time="4/4", bar_len=16, beat=4, bars=TREPAK, chords=TREPAK_CH, lo=65, hi=79, row_h=24, systems=[(0, 4)],
                   good="The easier chart: short, bouncy notes that already feel like hi-hats, and mostly G, C and D chords. A good first choice.",
                   tip="From bar 3 the tune bounces between low notes and a high D. Put that D on its own sound and it becomes a built-in hi-hat pattern."),
}


def tune_notes(key):
    """Flat list of (pitch, start, length) for a tune, start in sixteenths from the first bar (rests are skipped, but they take time)."""
    T, out, t = TUNES[key], [], 0
    for bar in T["bars"]:
        for p, d in bar:
            if p != "R":
                out.append((p, t, d))
            t += d
    return out


def note_count(key):
    return sum(1 for b in TUNES[key]["bars"] for p, _ in b if p != "R")


def bar_text(bar):
    return " · ".join(f"rest {LEN_NAMES[d]}" if p == "R" else f"{p} {LEN_NAMES[d]}" for p, d in bar)


def chord_text(spans):
    return " · ".join(c for _, c in spans)


# ---- the five flips of one bar of Trepak (chart bar 1, 16 steps): every flip is computed from the notes, not drawn by hand
def flip_src():
    return [(p, s, d) for p, s, d in tune_notes("trepak") if s < 16]


def flip_stretch(ns):
    return [(p, s * 2, d * 2) for p, s, d in ns]


def flip_chop(ns):
    return [(p, s, 1) for p, s, d in ns]


def flip_reverse(ns, total=16):
    return sorted([(p, total - (s + d), d) for p, s, d in ns], key=lambda x: x[1])


def flip_octave(ns):
    return [(pname(midi(p) + 12) if i % 2 else p, s, d) for i, (p, s, d) in enumerate(ns)]


def flip_drop(ns):
    return [(pname(midi(p) - 12), s, d) for p, s, d in ns]


FLIPS = [("Original", "the chart as written", lambda ns: list(ns)),
         ("1 · Stretch", "half-time: twice as long", flip_stretch),
         ("2 · Chop", "staccato: every note one step", flip_chop),
         ("3 · Reverse", "the bar played backwards", flip_reverse),
         ("4 · Octave jump", "every second note up 12", flip_octave),
         ("5 · Drop", "everything down an octave", flip_drop)]
FLIP_ROWS = [("1 · Stretch", "Every start and length doubles, so one bar becomes two. The tune is the same, but it breathes like half-time.",
              "Draw the notes again twice as long: double every start and every length in the table on page @TREPAK."),
             ("2 · Chop", "Every note is cut to one step. The pitches and starts stay, so the rhythm of the tune is still there, but it ticks like a hi-hat.",
              "Shorten the notes to one grid step, or draw them one step long, on a 1/16 grid."),
             ("3 · Reverse", "The bar played backwards: the same notes and lengths, in the opposite order. Use it for a break or a fill.",
              "Bounce the region to audio and use Reverse in Quick Sampler, or enter the notes from the end of the table up."),
             ("4 · Octave jump", "Every second note moves up an octave, so the line leaps. It sounds bright and bell-like over a heavy 808.",
              "Select every second note and drag it up 12 rows (an octave) in the Piano Roll."),
             ("5 · Drop", "The whole line moves down an octave. Use it to double the 808, or to hide the tune under the next section.",
              "Select the region and set Transpose in the Region inspector to −12.")]


def mini_lane(notes, lo, hi, x0, w, y0, h, steps, name):
    """One flip: notes as small bars on a time axis (steps wide), pitch rising up the lane."""
    cw = w / steps
    out = [f'<rect x="{x0}" y="{y0}" width="{w:.1f}" height="{h}" fill="#fff" stroke="#000" stroke-width="1.6"/>']
    for s in range(0, steps + 1, 4):
        wd = 3 if s % 16 == 0 else 1
        col = "#000" if s % 16 == 0 else "#9a9a9a"
        out.append(f'<line x1="{x0 + s * cw:.1f}" y1="{y0}" x2="{x0 + s * cw:.1f}" y2="{y0 + h}" stroke="{col}" stroke-width="{wd}"/>')
    for p, s, d in notes:
        y = y0 + 8 + (hi - midi(p)) / (hi - lo) * (h - 22)
        out.append(f'<rect x="{x0 + s * cw + 1.2:.1f}" y="{y:.1f}" width="{d * cw - 2.4:.1f}" height="9" rx="3" fill="{ACCENT}"/>')
    return "".join(out)


def flips_body(W=1100, name="flips pic"):
    src = flip_src()
    results = [(nm, sub, fn(src)) for nm, sub, fn in FLIPS]
    allm = [midi(p) for _, _, ns in results for p, _, _ in ns]
    lo, hi = min(allm), max(allm)
    gut, lh, gap = 270, 78, 8
    cw_w = W - gut - 6
    out = []
    for r, (nm, sub, ns) in enumerate(results):
        y = r * (lh + gap)
        out.append(D.t_(gut - 14, y + lh / 2 - 2, nm.upper(), 22, 700, anchor="end", fill_=ACCENT if r else "#000"))
        D.lab(name + " names", nm.upper(), 22, gut - 24)
        out.append(D.t_(gut - 14, y + lh / 2 + 22, sub, 17, 500, anchor="end"))
        D.lab(name + " subs", sub, 17, gut - 24)
        out.append(mini_lane(ns, lo, hi, gut, cw_w, y, lh, 32, name))
    cap = "Bar 1 of Trepak, six ways: two bars wide (32 steps); the first bar is the grid you know"
    out.append(D.t_(W / 2, len(results) * (lh + gap) + 22, cap, 21, 500))
    D.lab(name + " cap", cap, 21, W - 20)
    return "".join(out), W, len(results) * (lh + gap) + 34


# ---- the worked example: Sugar Plum Fairy as a trap beat at 150 BPM, 40 bars = 64 seconds
EX_BPM = 150
EX_BAR_S = 240 / EX_BPM         # 1.6 s
EX_BARS = 40
EX_SECTIONS = [("Intro", 1, 4), ("Beat A", 5, 16), ("Break", 17, 20), ("Beat B", 21, 36), ("Outro", 37, 40)]
# layer, [(first bar, last bar), ...], how it is made
EX_LAYERS = [("Pad", [(1, 40)], "a soft pad playing the chords, with a long reverb that swells in the break"),
             ("Melody", [(1, 16), (21, 36)], "the theme on a plucked bell sound; in the intro it is filtered, in Beat A it is chopped (flip 2), and it rests in the break"),
             ("808", [(5, 16), (21, 36)], "a sub bass on the chord roots (E1, B1, C#2, C2) with glide and light distortion, sidechained to the kick"),
             ("Kick", [(5, 16), (21, 36)], "pattern B: kick on beat 1, a short one on the “and” of 2 and one on the “and” of 3"),
             ("Clap", [(5, 16), (21, 36)], "half-time: one clap layered with a snare, on beat 3 only"),
             ("Hi-hats", [(5, 20), (21, 36)], "16th-note hats with a 32nd roll in the last beat of every fourth bar; they carry on, quieter, through the break"),
             ("Bells", [(21, 36)], "the melody an octave higher (flip 4, octave jump) on a bell sound, only in Beat B"),
             ("Riser", [(3, 4), (19, 20)], "a noise riser that builds into each drop, with one beat of silence just before it")]
EX_AUTO = [("Melody", "low-pass cutoff", [(1, .2), (5, .7), (17, .25), (21, .9), (36, .5)]),
           ("808", "distortion amount", [(5, .3), (13, .6), (21, .5), (29, .9), (36, .4)]),
           ("Pad", "reverb send", [(1, .8), (5, .3), (17, .9), (21, .3), (40, .9)])]
EX_WEAK = "I will make the Sugar Plum Fairy into a trap beat."
EX_STRONG = ("My theme is the Sugar Plum Fairy celesta tune, the four-bar chart in E minor. My beat is trap at 150 BPM, in half-time. The loop "
             "is 4 bars with the chords Em B7 | C#dim7 Cdim7 Em | Em Cmaj7 | B7. I use all five trap moves: hi-hat rolls in the last beat of "
             "every fourth bar, an 808 that glides on the chord roots, a clap on beat 3 only, the melody chopped and then an octave higher, "
             "and a riser before each drop. The beat is 40 bars, 64 seconds: intro, beat, break, beat with bells, outro.")
EX_MOVES = [("Hi-hat rolls", "16th-note hats, with a 32nd roll in the last beat of bars 4, 8, 12 and so on; the roll’s velocity ramps up (page @FX1)"),
            ("808", "E1, B1, C#2 and C2 on the chord roots, Glide on, a little Distortion, sidechained to the kick"),
            ("Half-time snare", "one clap layered with a snare on beat 3 only; the kick has just three hits a bar"),
            ("Flip", "chopped in Beat A (flip 2), an octave higher on bells in Beat B (flip 4); see page @FLIPS"),
            ("Riser and drop", "a noise riser in bars 3–4 and 19–20, then one beat of silence before the 808 returns")]
EX_STAYS = "Every pitch and every length of the chart before it is flipped: the theme keeps its tune, so people still know it."
EX_QUESTIONS = ["Which Tchaikovsky theme did you hear, and how fast did you know?",
                "Where did the beat drop out, and what stayed?",
                "Which trap move did you notice first?"]


def ex_density(bar):
    return sum(1 for _n, spans, _d in EX_LAYERS if any(a <= bar <= b for a, b in spans))


EX_DENS = [ex_density(b) for b in range(1, EX_BARS + 1)]


def mmss(t):
    t = int(round(t))
    return f"{t // 60}:{t % 60:02d}"


# ---- hi-hat rolls: notes per beat for each hat rate; one beat lasts 60000 / BPM ms
HATS = [("16th hats", "1/16", 4), ("Triplet hats", "1/16T", 6), ("32nd roll", "1/32", 8)]


def beat_ms(bpm):
    return 60000 / bpm


def hat_gap_ms(per_beat, bpm):
    return beat_ms(bpm) / per_beat


def length_s(bars, bpm):
    return bars * 240 / bpm


# ================================================================ drum patterns: 16 sixteenth steps (4 per beat)
LANES = ["Hi-hat", "Open hat", "Clap / snare", "Kick"]
HATS16 = "x" * 16
PATTERNS = [
    dict(key="a", name="Pattern A · Half-time basic", feel="slow and heavy, with space",
         pat={"Hi-hat": "x.x.x.x.x.x.x.x.", "Open hat": "." * 16, "Clap / snare": "........x.......", "Kick": "x.........x....."},
         drums="Kick on beat 1 and an eighth note after beat 3; clap or snare on beat 3 only; hats on every eighth note.",
         bass="one long note on each chord root, sliding at the chord change.",
         sounds="A deep kick, a layered clap and snare, tight closed hats.",
         tryit="Turn the hats down until the snare and 808 own the beat."),
    dict(key="b", name="Pattern B · Bounce", feel="rolling, a little busier",
         pat={"Hi-hat": HATS16, "Open hat": "." * 14 + "x.", "Clap / snare": "........x.......", "Kick": "x..x......x....."},
         drums="Kick on beat 1, the last sixteenth of beat 1 and the “and” of beat 3; clap or snare on beat 3 only; hats on every sixteenth; open hat on the last eighth of the bar.",
         bass="follow the kick, with short notes on the root and a long one on beat 3.",
         sounds="The same kit as A, with the hats at lower velocity and an open hat for lift.",
         tryit="Vary the hat velocities: accents on the beat, softer in between."),
    dict(key="c", name="Pattern C · Roll fill", feel="a fill, for the end of a phrase",
         pat={"Hi-hat": "x.x.x.x.x.x.xxxx", "Open hat": "." * 16, "Clap / snare": "........x.......", "Kick": "x.....x...x....."},
         drums="Kick on beat 1, the “and” of 2 and the “and” of 3; clap or snare on beat 3; hats on eighth notes, then four sixteenths in the last beat (a roll).",
         bass="long roots, with a short note before the change.",
         sounds="The same kit as A; ramp the roll’s velocity up from soft to loud.",
         tryit="Use this bar only as the fourth bar of a phrase, then go back to A or B."),
    dict(key="d", name="Pattern D · Sparse", feel="for intros, breaks and outros",
         pat={"Hi-hat": "....x.......x...", "Open hat": "." * 14 + "x.", "Clap / snare": "........x.......", "Kick": "x..............."},
         drums="Kick on beat 1 only; clap or snare on beat 3; hats only on beats 2 and 4; open hat on the last eighth.",
         bass="one long note per bar, or leave it out for a break.",
         sounds="Soft and spacious: more reverb on the clap, hats very quiet.",
         tryit="Use it for the intro and the break, then bring in pattern A or B for the drop.")]


def pattern(key):
    return next(p for p in PATTERNS if p["key"] == key)


def grid_for(p, name=None):
    """Drum grid of a pattern card as (svg body, w, h); labels logged for the fit check."""
    meas = [{ln: p["pat"][ln] for ln in LANES}]
    return D.grid_body(name or f"grid {p['key']}", meas, [p["name"].split(" · ")[1]], LANES, cw=22, ch=22, gut=140, ls=18, accent_from=0)


def blank_grid(name="grid blank"):
    return D.grid_body(name, [{}], ["Your pattern"], LANES, cw=22, ch=22, gut=140, ls=18, accent_from=0, blank=True)


def roll_body(notes, nsteps, bar_len, beat, lo, hi, W=1100, row_h=24, first_bar=1, chords=None, name="roll", hl=None, key_w=80, head=30):
    """A piano roll: rows are pitches lo..hi (MIDI numbers, black-key rows grey), columns are sixteenth notes, bars in bold, beats
    in grey. notes = [(pitch name, start, length)]; hl(p) -> True fills a note with the accent. chords = [(start, length, name)]."""
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
            out.append(D.t_(key_w - 6, y + row_h / 2 + fsz * .35, nm, fsz - 2, 500, anchor="end", fill_="#444"))
            D.lab(name + " keys", nm, fsz - 2, key_w * 0.5 - 6)
        else:
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
    for b in range(nb):
        out.append(D.t_(x0 + (b + .5) * bar_len * cw, head - 9, str(first_bar + b), 18, 700))
        D.lab(name + " bars", str(first_bar + b), 18, bar_len * cw - 6)
    fs = min(row_h - 9, 16)
    for p, s, d in notes:
        r = hi - midi(p)
        assert 0 <= r < rows, (p, lo, hi)
        x, y, w, h = x0 + s * cw + 1.2, head + r * row_h + 2.5, d * cw - 2.4, row_h - 5
        out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="4" fill="{ACCENT if hl and hl(p) else "#000"}"/>')
        txt = p[:-1]
        if w >= D.text_w(txt, fs) + 8:
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
    return "".join(out), W, H


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
    return "".join(out), W, bh + 72


def tune_roll(key, a, b, W=1100, name=None, chords=True):
    """Chart bars a..b-1 (0-based) of a tune as a roll."""
    T = TUNES[key]
    bl = T["bar_len"]
    nts = [(p, s - a * bl, d) for p, s, d in tune_notes(key) if a * bl <= s < b * bl]
    chs = []
    for i in range(a, b):
        t = (i - a) * bl
        for ln, ch in T["chords"][i]:
            chs.append((t, ln, ch))
            t += ln
    return roll_body(nts, (b - a) * bl, bl, T["beat"], T["lo"], T["hi"], W, T["row_h"], a + 1, chs if chords else None,
                     name or f"roll {key} {a}")


def hats_body(W=1100, name="hats pic", bpm=EX_BPM):
    """One bar of hi-hats three times: 16ths (4 a beat), triplet 16ths (6 a beat) and a 32nd roll (8 a beat, velocity swelling).
    The first hit of every beat is black, the others accent."""
    gut, head, rh = 250, 34, 78
    cw = (W - gut - 20) / 4
    out = []
    for b in range(4):
        out.append(D.t_(gut + (b + .5) * cw, 22, str(b + 1), 20, 700))
        D.lab(name + " beats", str(b + 1), 20, cw - 10)
    for r, (nm, rate, per) in enumerate(HATS):
        y = head + r * rh
        cy = y + rh / 2
        lbl = f"{nm.split()[0].upper()} · {rate}"
        out.append(D.t_(gut - 14, cy + 7, lbl, 20, 700, anchor="end", fill_=ACCENT if r else "#000"))
        D.lab(name + " rows", lbl, 20, gut - 24)
        out.append(f'<rect x="{gut}" y="{y + 4}" width="{4 * cw:.1f}" height="{rh - 8}" fill="#fff" stroke="#000" stroke-width="1.6"/>')
        for b in range(4):
            out.append(f'<rect x="{gut + b * cw:.1f}" y="{y + 4}" width="{cw:.1f}" height="{rh - 8}" fill="{"#ececec" if b % 2 == 0 else "#fff"}"/>')
        for b in range(5):
            out.append(f'<line x1="{gut + b * cw:.1f}" y1="{y + 4}" x2="{gut + b * cw:.1f}" y2="{y + rh - 4}" stroke="#7a7a7a" stroke-width="1.4"/>')
        total = 4 * per
        for k in range(total):
            x = gut + (k / per) * cw + cw / per / 2
            rad = (11, 9.5)[r] if r < 2 else 4 + 5 * k / (total - 1)   # last dots stay clear of the frame
            out.append(f'<circle cx="{x:.1f}" cy="{cy:.1f}" r="{rad:.1f}" fill="{"#000" if k % per == 0 else ACCENT}"/>')
    out.append(f'<rect x="{gut}" y="{head + 4}" width="{4 * cw:.1f}" height="{3 * rh - 8}" fill="none" stroke="#000" stroke-width="2.4"/>')
    g = [hat_gap_ms(per, bpm) for _, _, per in HATS]
    cap = f"At {bpm} BPM a beat lasts {beat_ms(bpm):g} ms: 16th hats every {g[0]:g} ms, triplet hats every {g[1]:.1f} ms, a 32nd roll every {g[2]:g} ms"
    out.append(D.t_(W / 2, head + 3 * rh + 28, cap, 21, 500))
    D.lab(name + " cap", cap, 21, W - 20)
    return "".join(out), W, head + 3 * rh + 44


def drums_body(name="drums pic"):
    a = grid_for(pattern("a"), name=name + " a")
    c = grid_for(pattern("c"), name=name + " c")
    cap = "Same grid, two trap feels: pattern A (half-time basic) and pattern C (with a roll in the last beat)"
    return D.stack([a, c, (D.t_(430, 22, cap, 22, 500), 860, 34)], 14)


def cycle_body(W=1600, name="cycle pic", fs=30, cs=22):
    return cards_body([("Choose", "a theme"), ("Plan", "your beat"), ("Enter", "melody + chords"), ("Beat", "snare + hats + 808"),
                       ("Flip it", "chop · roll · drop")], "Then arrange, mix, bounce, present and reflect", W, name, fs, cs)


def hero_body():
    W = 1100
    roll = tune_roll("sugar", 0, 4, 1000, "hero roll", chords=False)
    out = [f'<g transform="translate(50,0)">{roll[0]}</g>']
    y0 = roll[2] + 6
    names = ["808", "HAT ROLLS", "FLIP"]
    pw, gap, x0 = 300, 40, 60
    for i, nm in enumerate(names):
        x = x0 + i * (pw + gap)
        cx = x + pw / 2
        out.append(f'<line x1="{cx}" y1="{y0}" x2="{cx}" y2="{y0 + 46}" stroke="#000" stroke-width="5" stroke-dasharray="3 10" stroke-linecap="round"/>')
        out.append(f'<polygon points="{cx - 16},{y0 + 42} {cx + 16},{y0 + 42} {cx},{y0 + 72}" fill="#000"/>')
        out.append(f'<rect x="{x}" y="{y0 + 84}" width="{pw}" height="78" rx="39" fill="{ACCENT if i != 1 else "#000"}"/>')
        out.append(D.t_(cx, y0 + 84 + 39 + 14, nm, 40, 700, fill_="#fff"))
        D.lab("hero pills", nm, 40, pw - 50)
    return "".join(out), W, y0 + 168


def map_body(W=1600, name="map", fs=24, ts=20):
    """The worked example's whole 40-bar arrangement: sections, eight layers (some in two parts) and three automation lanes."""
    gx = 300
    pwid = W - gx - 16

    def X(bar):
        return gx + pwid * (bar - 1) / EX_BARS

    out = []
    sh = 54
    shade = {"Intro": "#4a4a4a", "Beat A": "#000", "Break": "#4a4a4a", "Beat B": ACCENT, "Outro": "#4a4a4a"}
    for nm, a, b in EX_SECTIONS:
        out.append(f'<rect x="{X(a) + 2:.1f}" y="2" width="{X(b + 1) - X(a) - 4:.1f}" height="{sh}" rx="8" fill="{shade[nm]}"/>')
        out.append(D.t_((X(a) + X(b + 1)) / 2, sh / 2 + fs * .3 + 2, nm.upper(), fs - 4, 700, fill_="#fff"))
        D.lab(name + " sections", nm.upper(), fs - 4, X(b + 1) - X(a) - 10)
    lh, lg = 28, 6
    y0 = sh + 14
    out.append(D.t_(gx - 14, y0 + 6, "LAYERS", fs - 6, 700, anchor="end", fill_=ACCENT))
    for i, (nm, spans, _d) in enumerate(EX_LAYERS):
        yy = y0 + 16 + i * (lh + lg)
        out.append(D.t_(gx - 14, yy + lh / 2 + 7, nm.upper(), 20, 700, anchor="end"))
        D.lab(name + " lanes", nm.upper(), 20, gx - 24)
        out.append(f'<rect x="{gx}" y="{yy}" width="{pwid:.1f}" height="{lh}" fill="#fff" stroke="#000" stroke-width="1.2"/>')
        for a, b in spans:
            out.append(f'<rect x="{X(a):.1f}" y="{yy + 4}" width="{X(b + 1) - X(a):.1f}" height="{lh - 8}" rx="6" fill="#bdbdbd" stroke="#000" stroke-width="2"/>')
    ay0 = y0 + 16 + len(EX_LAYERS) * (lh + lg) + 8
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
    ticks = (1, 5, 9, 13, 17, 21, 25, 29, 33, 37, 41)
    for bar in ticks:
        t = (bar - 1) * EX_BAR_S
        lbl = mmss(t)
        anc = "start" if bar == 1 else ("end" if bar == 41 else "middle")
        out.append(f'<line x1="{X(bar):.1f}" y1="{ty - 6}" x2="{X(bar):.1f}" y2="{ty + 8}" stroke="#000" stroke-width="2"/>')
        out.append(D.t_(X(bar) + (2 if bar == 1 else (-2 if bar == 41 else 0)), ty + 8 + ts, lbl, ts, 500, anchor=anc))
        D.lab(name + " ticks", lbl, ts, 70)
    cap = f"Bar 1 to bar 40 at {EX_BPM} BPM: {EX_BARS} bars × {EX_BAR_S:g} seconds = {EX_BARS * EX_BAR_S:g} seconds"
    out.append(D.t_(gx + pwid / 2, ty + 8 + ts + 34, cap, ts + 2, 500))
    D.lab(name + " cap", cap, ts + 2, pwid)
    return "".join(out), W, ty + 8 + ts + 48


DRAWINGS = {"hero": hero_body, "cycle": lambda: cycle_body(1600), "roll": lambda: tune_roll("sugar", 0, 4, 1100, "roll deck"),
            "hats": lambda: hats_body(1100, "hats deck"), "drums": lambda: drums_body(), "map": lambda: map_body(1600, "map pic")}
DRAWING_PX = {"hero": 1900, "cycle": 2000, "roll": 2000, "hats": 2000, "drums": 2000, "map": 2000}
SIDE = {"cycle": ["Choose a theme and a tempo", "Plan your beat and trap moves", "Enter the melody and chords",
                  "Beat first, then flip it, then arrange"],
        "roll": ["Higher bar means higher pitch", "Longer bar means a longer note", "Left to right is time, bar by bar",
                 "Four bars of 4/4 = eight score bars"],
        "hats": ["Black dots start each beat", "Purple dots are the fast hits in between", "A roll swells from soft to loud",
                 "Roll only in the last beat"],
        "map": ["An invented 64-second beat", "Five sections: 4, 12, 4, 16, 4 bars", "Eight layers, three automation lanes",
                "Beat B has the most layers"]}


def label_extras():
    for k, T in TUNES.items():
        for a, b in T["systems"]:
            tune_roll(k, a, b, 1100, f"page {k} {a}")
    hats_body(1100, "page hats")
    flips_body(1100, "page flips")
    tune_roll("sugar", 0, 4, 1100, "page example roll")
    map_body(1250, "page map", 24, 20)
    cycle_body(1250, "page cycle", 28, 20)
    roll_body([], 64, 16, 4, 55, 67, 1100, 14, 1, None, "blank roll")
    for p in PATTERNS:
        grid_for(p)
    blank_grid()


# ================================================================ intro deck: (class, kind, title, body, speaker notes)
SLIDES = [
    (1, "title", "Trap Nutcracker", "Tchaikovsky, flipped.",
     "Class 1, the first minute. No audio is included in this deck. Open with the idea: you are going to flip a theme by Tchaikovsky, "
     "written in 1892, into a trap beat in Logic Pro, with an 808, rolling hi-hats and a heavy half-time snare. The two themes are public "
     "domain and arrive as note charts, so every student can enter them without reading staff notation."),
    (1, "listen", "Think: what makes a beat sound like trap?", "Think, then share|Teacher: say or hum the first line of Trepak, first "
     "bright and bouncy, then slow, heavy and low.|What changed?|What would make it hit harder?|Which sounds would you add?",
     "Ask the three questions aloud and take a few answers. Nothing is played from a speaker: you say or hum the first line of Trepak yourself, "
     "first bright and bouncy and then slow, heavy and low. Students will say slower, deeper, more bass and, if they know the style, "
     "fast hi-hats and a big snare. Write their words on the board; the project turns each one into a tool."),
    (1, "bullets", "What is Trap Nutcracker?", "Choose a public-domain Tchaikovsky theme|Enter its melody and chords in Logic Pro|Flip it: "
     "808, hi-hat rolls, half-time snare|Finish a 60 to 90 second beat",
     "The project in four lines. Students choose the Sugar Plum Fairy or the Trepak, both from The Nutcracker of 1892; both melodies are "
     "public domain, so anyone may use them. They enter the melody and chords from a piano-roll chart, then build a half-time beat and "
     "flip the tune. The finished beat is 60 to 90 seconds. If a student would rather use another public-domain melody, a blank piano "
     "roll is provided and you approve the tune."),
    (1, "days", "Four classes", "",
     "The shape of the project. Class 1: hook, choose a theme, fill in the Beat plan and enter the melody and chords. Class 2: build the "
     "beat, with drums, hi-hat rolls, an 808 and a flipped melody. Class 3: make it hit with the snare, the 808 and a riser and drop, then plan "
     "the form, arrange and mix. Class 4: bounce, hand in, present and reflect. Hand out the project sheet, the charts and the Beat plan now."),
    (1, "pic", "Five moves, then finish", "cycle",
     "Class 1. The five moves in order: choose, plan, enter, beat and flip it. After that students arrange, mix, bounce, present and "
     "reflect. Point to each box and say roughly when it happens: choosing and planning today, entering and the beat on Class 2, the "
     "snare, 808, riser and arranging on Class 3. The picture and its short labels are drawn for this kit."),
    (1, "pic", "Reading a piano roll", "roll",
     "Class 1. This is the Piano Roll view of the four-bar Sugar Plum Fairy loop, drawn the same way as the charts on students' pages. "
     "A higher bar is a higher pitch, a longer bar is a longer note, and time runs left to right. In the score the dance is in 2/4; the "
     "chart writes two score bars as one 4/4 bar. The chord boxes underneath are the loop's chords; other chords can work."),
    (2, "steps", "Build the beat", "Set the tempo, 130 to 150 BPM|Pick a drum pattern: kick, clap, hats|Enter it in the Step Sequencer, or "
     "start from a Drummer track|Snare or clap on beat 3 only: half-time|Add an 808 on the chord roots, with Glide",
     "Class 2. Demonstrate on the projector: set the tempo between 130 and 150 BPM, make a Drum Machine Designer track and open the Step "
     "Sequencer, or make a Drummer track in a hip-hop or trap style if your version has one. Click in pattern A from page 15, with the clap "
     "on beat 3 only. Then add an 808: a Software Instrument track with Alchemy or Retro Synth, playing one long note on each chord root. "
     "Menu names move between Logic versions."),
    (2, "pic", "Hi-hat rolls", "hats",
     "Class 2. One bar of hi-hats three times. The black dots start each beat; the purple dots are the fast hits in between. Sixteenth notes "
     "are four a beat, triplet sixteenths six, and a 32nd roll eight. At 150 BPM a beat lasts 400 milliseconds, so the gaps are 100, "
     "66.7 and 50 milliseconds. The third row's dots grow: that is a velocity ramp, soft to loud. In Logic, draw the roll on a fine grid in "
     "the Piano Roll, or set the Step Sequencer's rate, or use the Note Repeater MIDI plug-in."),
    (2, "pic", "Trap drum patterns", "drums",
     "Class 2. The same 16-step grid in two trap feels. Pattern A is half-time: kick on beat 1 and just after beat 3, clap on beat 3 only, "
     "hats on eighths. Pattern C adds a four-hit roll in the last beat. Students copy a pattern from page 15 into the Step Sequencer. "
     "Ask: which of your trap moves is this, drums, rolls or the 808? Pattern D is the sparse one for intros and breaks."),
    (3, "pic", "Worked example: 64 seconds", "map",
     "Class 3. An invented beat described on paper, nothing here is audio: the Sugar Plum Fairy at 150 BPM. Forty bars at 1.6 seconds a "
     "bar is 64 seconds, in five sections of 4, 12, 4, 16 and 4 bars. Eight layers join and leave, and Beat B has the most. Three automation "
     "lanes keep the sound moving. Students plan their own on the Arrangement plan."),
    (3, "bullets", "Flip it, drop it", "Chop it, jump an octave, or reverse it|808: roots only, glide, a little distortion|Riser into a "
     "drop, then one beat of silence|Keep the theme clear: the melody on top",
     "Class 3. The sound moves in one idea: each one is small, and the melody stays the star. Flip the melody with the five flips on page 14: "
     "chop it, jump an octave, reverse it. Put a little Distortion on the 808 and sidechain it to the kick with a Compressor. Build a riser "
     "from noise and leave a beat of silence before the drop. Ask each student to play their first 20 seconds and say whether a listener "
     "could name the theme."),
    (4, "check", "What you turn in", "Bounced .mp3 or .wav|Zipped .logicx project|Named: Your Name – Trap Nutcracker – Theme|Beat plan, "
     "Arrangement plan, Reflection|Rubric self-score|Three questions for classmates",
     "Class 4. The submission checklist, shortened to fit the slide. Show where students hand in. The file name is Your Name, Trap "
     "Nutcracker, then the theme, in that order. Check that every beat is between 60 and 90 seconds before students bounce."),
    (4, "rubric", "How it’s scored", "",
     "The rubric: five categories, each scored 1 to 5, for a total out of 25. Students score themselves first; the final grade is the "
     "average of their score and yours. The slide reads the 5 column of each category aloud. Hand out the rubric page so students can "
     "self-score before they present."),
    (4, "bullets", "Presentation day", "Play your beat, then name the theme|Say which trap moves you used|Your three questions "
     "for classmates|Answer at least 2 of each classmate’s questions",
     "Class 4, presentations. Each student plays their beat, says which theme it is and names the trap moves they used, then takes "
     "questions. Students write three questions they want classmates to answer, and answer at least two of each classmate's. "
     "Ask the class to name the theme before the presenter does."),
    (4, "closer", "One last thing…", "Tchaikovsky wrote it.|You flipped it.|You added the 808.|Now press play.",
     "Close with the listening day: play the finished beats without saying the title and let the class name each theme. A melody that "
     "people name quickly is a beat that kept the tune. Ask a few students which trap move changed the mood most. No audio is included "
     "in this kit; the sounds are the students' own."),
]
SHOTS1 = [("pacing", "Pacing guide", "4 class periods, slide by slide"), ("sugar", "Piano-roll chart", "Sugar Plum Fairy, bar by bar"),
          ("rubric", "Rubric / 25", "student + teacher average")]
SHOTS2 = [1, 6, 8, 9, 10, 13]
SHOTS3 = [("sugar", "Sugar Plum"), ("trepak", "Trepak"), ("flips", "Five flips"), ("drums", "Drum patterns"),
          ("fx1", "Rolls and 808"), ("fx2", "Snare, flip, drop"), ("example", "Worked example"), ("arrange", "Arrangement plan")]

# ================================================================ page plan (teacher pages 2-11, student pages 12-26)
PLAN = ["cover", "howto", "overview", "setup", "pacing", "tn1", "tn2", "logicref", "tunes", "example", "example2", "sugar", "trepak", "flips",
        "drums", "fx1", "fx2", "plan", "arrange", "proj1", "proj2", "proj3", "rubric", "vocab", "present", "reflect", "terms"]
PREVIEW_PICKS = ["pacing", "sugar", "fx1", "rubric"]

COVER_A = "Flip Tchaikovsky into trap"
COVER_C = "Logic Pro · piano-roll charts · 808s, hat rolls · intro slides"
PDF_COVER = dict(a=26, b=58, c=14, art=7.3)
SQ_COVER = dict(a=40, b=150, c=27, art=740, gap=40)
SQ_B_LINES = ["Trap", "Nutcracker"]
SQ_SUB = "4 class periods · 2 themes · intro slides"
SQ_HEADS = {1: ("Ready to teach Monday", 76, "Teacher notes, pacing, charts, drum patterns and the /25 rubric in one PDF", 28),
            2: ("Intro deck included", 76, f"{len(SLIDES)} editable slides (.pptx + PDF) with speaker notes on every slide", 28),
            3: ("Everything inside", 72, "Two note charts, five flips, drum patterns, effect cards, a worked example and plans", 28)}
SQ_BANDS = {1: "Choose <em>·</em> enter <em>·</em> 808 <em>·</em> hat rolls <em>·</em> flip it",
            2: "Piano roll <em>·</em> hat rolls <em>·</em> drum patterns <em>·</em> worked example",
            3: f"{len(PLAN)} pages <em>·</em> US Letter PDF <em>·</em> no audio included"}

SONG_NOTE = ("No audio, recordings, lyrics, artists or albums are named or included. The two themes are public domain and appear "
             "only as note charts. Students make every sound in their beats themselves, from the instruments, drum kits and plug-ins in Logic.")
CREDITS = ["Piano-roll note charts of two public-domain themes by Tchaikovsky (Dance of the Sugar Plum Fairy and Trepak, from The Nutcracker, "
           "1892), the flips, the worked example, the drum patterns, the effect cards, the hero, card, hi-hat roll and "
           "arrangement drawings and all layouts: original work, Hudson Beat. No lyrics, recordings or published editions are included.",
           "No audio, video, album art, screenshots, presets, templates, links or chart data are included. No student work is included."]
LOGIC_INTRO = ("Where to find the tools a Trap Nutcracker beat is likely to use. Demonstrate what your class needs on Classes 1 and 2 and then "
               "let students work. Names are from current Logic Pro versions; labels move between versions, so check yours.")
LOGIC_REF = [("New project and tracks", "File › New…, then add a Software Instrument track with Track › New Tracks…. Use one track for the "
              "melody and more for chords, the 808 and drums."),
             ("Tempo and time signature", "Type the tempo in the control bar (130 to 150 BPM) and keep 4/4. In the score both themes are in 2/4; "
              "the charts write two score bars as one 4/4 bar, so nobody needs to change the time signature."),
             ("Make a region, open the Piano Roll", "With the Pencil tool, click on the track where bar 1 starts to make an empty MIDI "
              "region, then double-click it to open the Piano Roll editor."),
             ("Draw notes and chords", "Pick a grid value in the Piano Roll’s Snap menu (for example, 1/16 note) so notes land on the "
              "chart’s sixteenth-note grid, click with the Pencil to add a note and drag its right edge to change its length. Draw a chord as "
              "notes stacked in one column. Logic names middle C “C3” by default; the charts call it C4, so subtract one from the chart’s octave number when you read the roll."),
             ("Fix wrong notes", "Select a note and drag it up or down a row, or press delete. To play a melody an octave lower, select the "
              "region and change Transpose in the Region inspector by 12 steps."),
             ("Drums", "Make a Drum Machine Designer track and open the Step Sequencer: click the 16 steps for each drum, as on the patterns on page "
              + str(PLAN.index("drums") + 1) + ". Or make a Drummer track and, if your version has a hip-hop or trap style, start there and make it half-time."),
             ("808 sub bass", "Make a Software Instrument track with Alchemy or Retro Synth and browse the Library (Y) for a sub bass or 808 sound, "
              "or build one: a sine oscillator, mono with Glide on, a long release. Play low notes (E1 to D2). Add a little Distortion or Overdrive so small speakers can hear it."),
             ("Hi-hat rolls", "Put the closed hat on its own pad. In the Piano Roll draw the roll on a fine grid (1/16 triplet or 1/32), or in the Step Sequencer set "
              "the row’s rate to a faster value. A Note Repeater MIDI plug-in on the track will repeat a held note. Ramp the velocities up with MIDI Draw or the velocity "
              "controls so the roll swells."),
             ("Sidechain, reverb and EQ", "On the 808 track add a Compressor and set its Side Chain to the kick’s track, so the 808 ducks when the kick hits. For space use "
              "ChromaVerb or Space Designer on the clap and the pad. Use Channel EQ to cut mud and to close a low-pass filter (High Cut) in the intro."),
             ("Chop and reverse", "Select regions and press Command-T to split at the playhead, or bounce a part to audio and open it in Quick Sampler, "
              "which can play slices from the keyboard and has a Reverse button."),
             ("Automation, mixing and bounce", "Press A to show automation, pick a parameter such as a filter cutoff or distortion amount, and draw points. "
              "Press X for the Mixer. Then File › Bounce › Project or Section (Command-B), MP3 or WAV. In Finder, Control-click the .logicx "
              "and choose Compress.")]
PRESENT_CHECK = [f"Files named {FILE_NAME}; the .mp3 or .wav and zipped .logicx handed in",
                 "Reflection page done (page @REFLECT)", "Three questions for classmates written",
                 "Rubric self-score done (page @RUBRIC)"]
VOCAB_PROMPT = "Where it shows up in my beat:"
TN1_EXTRA = (
    '<div class="box acc-b" style="margin-top:4pt"><span class="k">Where this kit helps with each struggle</span><ul style="margin:0">'
    '<li style="font-size:12pt;margin-bottom:3pt">Wrong notes: the chart pages (pages @SUGAR and @TREPAK) list every note by bar, and the Logic quick reference (page @LOGICREF) shows the grid.</li>'
    '<li style="font-size:12pt;margin-bottom:3pt">A busy, weak beat: the drum patterns (page @DRUMS) and slide 8 show where the snare and the rolls go.</li>'
    '<li style="font-size:12pt;margin-bottom:3pt">A muddy 808: the 808 card (page @FX1), the mix checks on the Arrangement plan (page @ARRANGE) and slide 11.</li>'
    '<li style="font-size:12pt;margin-bottom:0">A tune that disappears: the five flips (page @FLIPS) and the worked example (pages @EXAMPLE–@EXAMPLE2).</li></ul></div>')
TN1_SIZE = 12.8
PROJ_SIZE = 12.6
VOCAB_GAP = 14
LOGIC_SIZE = 9.4
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
             ("Student pages", "sugar", "reflect", "Two note charts, five flips, trap drum patterns, effect cards (2 pages), Beat plan, Arrangement plan, "
              "project sheet (3 pages), rubric, vocabulary, feedback planner, reflection page"),
             ("Intro deck (separate file)", None, None, f"{len(SLIDES)} slides, .pptx + PDF, speaker notes on every slide")]
    trs = "".join(f"<tr><td><b>{a}</b></td><td style='white-space:nowrap'>{('pages ' + str(D.IX(f)) + '–' + str(D.IX(l))) if f else 'deck'}</td>"
                  f"<td>{u}</td></tr>" for a, f, l, u in parts)
    inner = (f'<div class="cols"><div>'
             f'{D.H2("What this is", True)}'
             f'<p style="font-size:12pt;line-height:1.45">A {CLASSES}-class-period beat-making project for high school music technology. Each '
             f'student chooses one of two public-domain themes from Tchaikovsky’s Nutcracker (1892), enters its melody and chords into Logic Pro from a '
             f'piano-roll note chart, and flips it into a trap beat: a half-time snare, rolling hi-hats, a gliding 808 sub bass and a chopped, '
             f'moved or reversed melody. The beat is 60 to 90 seconds. Students plan it, build and mix it, present it and reflect on it. It is an original Hudson Beat project.</p>'
             f'{D.H2("Quick start")}<ol>'
             f'<li style="margin-bottom:5pt">Read the pacing guide (page {D.IX("pacing")}) and the teacher notes (pages {D.IX("tn1")}–{D.IX("tn2")}).</li>'
             f'<li style="margin-bottom:5pt">Decide which themes to offer (page {D.IX("tunes")}) and check the setup (page {D.IX("setup")}).</li>'
             f'<li style="margin-bottom:5pt">Print the student pages (pages {D.IX("sugar")}–{D.IX("reflect")}), one set per student.</li>'
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
             f'<li><b>Theme choice:</b> Trepak is the easier chart, Sugar Plum Fairy the harder (page {D.IX("tunes")}). They are in related keys (G major and E minor), so strong students can combine them.</li>'
             f'<li><b>Feedback:</b> students write three questions and answer classmates’ on a class board or on paper.</li>'
             f'<li><b>Grading:</b> the rubric, /{RUBRIC_TOTAL}, the average of the student’s and your score (page {D.IX("rubric")}).</li></ul>'
             f'<div class="box" style="margin-top:6pt"><span class="k">In one sentence</span><p style="margin:0;font-size:12pt">Students learn that a '
             f'style is made of small choices: a half-time snare, an 808, rolling hats and a flipped melody turn the same tune into trap.</p></div>'
             f'<p class="small" style="margin-top:6pt">Logic Pro is a product of Apple Inc. This resource is not affiliated with Apple.</p>'
             f'</div></div>')
    return D.page("How to use this resource", "START HERE", "Teacher", inner, n, key="howto")


def overview_page(n, wm=False):
    inner = (f'<div class="cols"><div>'
             f'<div class="box inv" style="margin-bottom:6pt"><span class="k">The project in one line</span><p style="margin:0;font-size:12pt">'
             f'<b>{TITLE}</b> · Beat making · Logic Pro<br>Flip a Tchaikovsky theme into a trap beat.</p></div>'
             f'{D.H2("What students make")}'
             f'<p style="font-size:13pt;line-height:1.5">One original beat, 60 to 90 seconds long, built on a public-domain theme. The melody is '
             f'entered from a piano-roll chart and stays recognizable; the tempo is 130 to 150 BPM, the snare is half-time, the hats roll, and an 808 '
             f'plays the chord roots. It has at least five layers and an intro, beat sections, a break and an outro, is '
             f'mixed with volume, pan and EQ, and uses at least four of the five trap moves. Students hand in a bounced .mp3 or .wav and the zipped '
             f'.logicx project, plus their plans and a reflection, then play the beat and take questions.</p>'
             f'{D.H2("What this project reinforces")}<p style="font-size:12.6pt;line-height:1.5">{TN_REINFORCES}</p>'
             f'{D.H2("Standards")}<p style="font-size:11.6pt">Supports the National Core Arts Standards for Music (Music Technology, high school): generating '
             f'and developing ideas (MU:Cr1.1, MU:Cr2.1), presenting work (MU:Pr6.1) and responding to it (MU:Re7.2).</p>'
             f'</div><div>'
             f'{D.H2("Goals", True)}<ul>' + "".join(f"<li style='font-size:12.6pt;line-height:1.5'>{g}</li>" for g in GOALS) + '</ul>'
             f'{D.H2("At a glance")}<table class="t" style="font-size:11.4pt">'
             f'<tr><td><b>Grades</b></td><td>{GRADES_TEXT}, music technology or music production</td></tr>'
             f'<tr><td><b>Length</b></td><td>{CLASSES} class periods: choose and enter, build the beat, make it hit and arrange, present and reflect</td></tr>'
             f'<tr><td><b>Software</b></td><td>Logic Pro: Piano Roll, instruments, Step Sequencer or Drummer, hi-hat rolls, 808, effects, bounce</td></tr>'
             f'<tr><td><b>You supply</b></td><td>Macs with Logic Pro, headphones, a place to hand in files and a class board or paper for feedback</td></tr>'
             f'<tr><td><b>Assessment</b></td><td>Rubric, 5 categories scored 1–5, /{RUBRIC_TOTAL}; final grade = average of the student’s and the '
             f'teacher’s score (page {D.IX("rubric")})</td></tr></table>'
             f'<div class="box" style="margin-top:6pt"><span class="k">Before they start</span><p style="margin:0;font-size:11.6pt">Students should know how '
             f'to open a project, add a software instrument and use the mixer in Logic. Nobody needs to read music: the charts name every '
             f'pitch and length.</p></div>'
             f'</div></div>')
    return D.page("Project overview", "OVERVIEW", "Beat-making project", inner, n, key="overview")


def setup_page(n, wm=False):
    inner = (f'<style>.sb p, .sb li {{ font-size: 11.8pt; line-height: 1.44; margin-bottom: 5pt; }}</style><div class="cols"><div class="big sb">'
             f'{D.H2("You need", True)}<ul>'
             f'<li><b>A Mac with Logic Pro</b> for each student, and <b>headphones</b>. Speakers help for the final listen, because an 808 needs good low end.</li>'
             f'<li><b>A place to hand in</b> the .mp3 or .wav, the zipped .logicx and the reflection.</li>'
             f'<li><b>The two charts</b>, printed (pages {D.IX("sugar")} and {D.IX("trepak")}), or shown on the projector.</li>'
             f'<li><b>The flips, drum patterns and effect cards</b>, printed (pages {D.IX("flips")}–{D.IX("fx2")}).</li>'
             f'<li><b>Printed student pages</b>, one set each (pages {D.IX("sugar")}–{D.IX("reflect")}).</li>'
             f'<li><b>A MIDI keyboard</b> is optional: every melody can be drawn with the mouse.</li></ul>'
             f'{D.H2("Before Class 1")}'
             + "".join(D.chk(c, 13, "font-size:11.8pt;margin-bottom:7pt") for c in [
                 "Decide which themes you will offer (page @TUNES).".replace("@TUNES", str(D.IX("tunes"))),
                 "Open Logic Pro on a student computer: can you make a track, open the Piano Roll and hear playback through headphones?",
                 "Check that the tools on page @FX1 and page @FX2 are there (Alchemy or Retro Synth, Compressor, a Distortion or Overdrive plug-in, ChromaVerb or Space Designer) and that you know where your Library keeps sub bass sounds.".replace("@FX1", str(D.IX("fx1"))).replace("@FX2", str(D.IX("fx2"))),
                 "Read the worked example (pages @A–@B).".replace("@A", str(D.IX("example"))).replace("@B", str(D.IX("example2")))]) +
             f'</div><div class="big sb">'
             f'{D.H2("What to watch", True)}'
             f'<p style="font-size:11.6pt">Students enter the notes but get a wrong one, the beat is busy instead of heavy, the 808 turns to mud, '
             f'or the tune disappears. {TN_NOTE}</p>'
             f'<div class="box acc-b" style="margin-top:2pt"><span class="k">Ideas for the room</span><ul style="margin:0">'
             f'<li style="font-size:11.4pt">Ask while students work: where is the snare? Can you hear the theme? Which trap move is this?</li>'
             f'<li style="font-size:11.4pt">On Class 1, tap 130, 140 and 150 BPM on the desk, then clap only on every second backbeat, so students feel half-time.</li>'
             f'<li style="font-size:11.4pt">A student who is stuck on drums can start from a Drummer track in a hip-hop style and move the snare to beat 3.</li></ul></div>'
             f'{D.H2("Choosing themes")}'
             f'<div class="box"><span class="k">A respectful choice</span><p style="margin:0;font-size:11.2pt;line-height:1.4">'
             f'Both themes come from a Christmas-season ballet, but neither is a carol and neither has words. Trepak is a lively Russian dance and the '
             f'Sugar Plum Fairy is a dance for a fairy; students of any background can use them. If a student prefers another '
             f'melody, a public-domain one you approve (first published in the United States in 1930 or earlier) works with the same plan, and '
             f'the blank piano roll on page {D.IX("plan")} is there for their own chart.</p></div>'
             f'<div class="box" style="margin-top:6pt"><span class="k">Keep the volume moderate</span><p style="margin:0;font-size:11.2pt;line-height:1.4">'
             f'Bass-heavy beats and loud peaks are tiring in headphones. Tell students to start low and check the final mix at a normal level.</p></div>'
             f'</div></div>')
    return D.page("Setup and what to watch", "SETUP", "Teacher", inner, n, key="setup")


def tunes_page(n, wm=False):
    rows = ""
    for k in ("sugar", "trepak"):
        T = TUNES[k]
        rows += (f"<tr><td><b>{T['title']}</b><br>{T['part']}</td><td>{T['who']}<br>{T['yr']}</td><td>{T['key']}, {T['time']}<br>"
                 f"{len(T['bars'])} bars, {note_count(k)} notes</td><td>{T['good']}</td></tr>")
    srcs = "".join(f"<li><b>{TUNES[k]['title']}:</b> {TUNES[k]['src']}</li>" for k in ("sugar", "trepak"))
    inner = (f'<p style="margin:0 0 4pt;font-size:11.6pt;line-height:1.42">Both themes are in the public domain, and each is printed '
             f'here as a note chart only: no lyrics, no recordings and no published edition. Pitches and lengths are checked against the notes in code.</p>'
             f'<table class="t" style="font-size:10.4pt"><tr><th style="width:21%">Theme</th><th style="width:22%">Source · year</th><th style="width:19%">In this kit</th>'
             f'<th>Good for</th></tr>{rows}</table>'
             f'{D.H2("Where the themes come from")}<ul style="font-size:11pt">{srcs}'
             f'<li><b>The transcription:</b> the notes were taken from free transcriptions of the score, checked against each other, and written here in the '
             f'kit’s own layout. Both dances are in 2/4 in the score; this kit writes two score bars as one 4/4 bar. If you want to check a note, the score of '
             f'Op. 71 (and the suite, Op. 71a) is free on IMSLP.</li></ul>'
             f'{D.H2("The public-domain rule")}<p style="font-size:11.4pt;line-height:1.42">In 2026 a melody is in the public domain in the United '
             f'States when it was first published in 1930 or earlier (1931 from 1 January 2027). Tchaikovsky’s Nutcracker was first performed and published in 1892. '
             f'Recordings, film and pop versions, and their arrangements are separate works, so students must not use them. If a student suggests another '
             f'tune, check its first publication date before you approve it.</p>'
             f'{D.H2("Picking a theme for a student")}<ul style="font-size:11pt"><li><b>First time in the Piano Roll:</b> Trepak. Short notes, mostly G, C and D, and a loop that repeats cleanly.</li>'
             f'<li><b>Wants a dark, bell-like sound:</b> Sugar Plum Fairy. E minor, with sharps and seventh chords.</li>'
             f'<li><b>Wants a challenge:</b> use both: Trepak (G major) for Beat A and Sugar Plum Fairy (E minor, the relative minor) for Beat B.</li></ul>'
             f'<div class="cols" style="gap:12pt;margin-top:4pt"><div class="box acc-b"><span class="k">Reading the charts</span><p style="margin:0;font-size:10.6pt;line-height:1.38">'
             f'Pitch names run down the left; middle C is C4 (Logic’s piano roll calls it C3). Bold lines are bars, grey lines are beats. A note’s length is the name beside it: '
             f'16th, eighth, quarter or half. Black-key notes are marked with a sharp (F#). Chords are one idea that fits, not the only one.</p></div>'
             f'<div class="box"><span class="k">Why a four-bar loop</span><p style="margin:0;font-size:10.6pt;line-height:1.38">'
             f'Trap beats are built on a short loop that repeats. Each chart ends so that it leads back into bar 1: the Sugar Plum loop ends on B7 and returns '
             f'to Em, and the Trepak loop ends on D and returns to G.</p></div></div>')
    return D.page("Tune sources and the public-domain rule", "TEACHER", "Tunes", inner, n, key="tunes")


def bass_roll(key, name="808 roll"):
    T = TUNES[key]
    nb = len(T["bars"])
    return roll_body([], nb * T["bar_len"], T["bar_len"], T["beat"], 28, 40, 1100, 17, 1, None, name)


def chart_page(key):
    def build(n, wm=False):
        T = TUNES[key]
        glance = (f'<p style="margin:0 0 3pt;font-size:10.4pt"><b>{T["title"]}</b>, {T["part"]} · {T["who"]}, {T["yr"]} · {T["key"]}, {T["time"]} · '
                  f'{len(T["bars"])} chart bars · {note_count(key)} notes</p>')
        systems = "".join(f'<div style="margin:0 0 2pt">{D.body_svg(tune_roll(key, a, b, 1100, f"page {key} {a}"))}</div>' for a, b in T["systems"])
        nb = len(T["bars"])
        rr = "".join(f"<tr><td style='width:9%'><b>{i + 1}</b></td><td>{bar_text(T['bars'][i])}</td><td style='width:20%'>{chord_text(T['chords'][i])}</td></tr>"
                     for i in range(nb))
        tab = (f'<table class="t" style="font-size:9.4pt;line-height:1.2;margin:2pt 0 3pt"><tr><th>Bar</th><th>Notes (pitch, length)</th><th>Chords</th></tr>{rr}</table>')
        about = (f'{T["src"]} {T["tip"]} Chords shown are one idea that fits; try others by ear. Drums: pattern A, B or C (page {D.IX("drums")}).')
        bass = D.body_svg(bass_roll(key, f"page {key} bass"))
        inner = (f'{glance}{systems}{tab}'
                 f'<div class="box acc-b" style="margin-top:4pt;padding:4pt 10pt"><span class="k">About this chart</span><p style="margin:0;font-size:9.2pt;line-height:1.3">'
                 f'{about}</p></div>'
                 f'<span class="k" style="margin-top:5pt">Your turn: write an 808 line on the chord roots (pencil), one long note per chord</span>'
                 f'<div style="margin-top:2pt">{bass}</div>')
        return D.page(f"Note chart · {T['title']}", "STUDENT", "Class 1", inner, n, wm, name=True, key=key)
    return build


def flips_page(n, wm=False):
    rows = "".join(f"<tr><td style='width:15%'><b>{a}</b></td><td>{b}</td><td style='width:33%'>{D.fill(c)}</td></tr>" for a, b, c in FLIP_ROWS)
    inner = (f'<p style="margin:0 0 4pt;font-size:10.8pt;line-height:1.38">A <b>flip</b> remakes a melody without losing it. Here is bar 1 of Trepak (page {D.IX("trepak")}) '
             f'in five flips. Every picture is computed from the same nine notes: nothing is drawn by hand. Try one flip per section of your beat, and keep the original '
             f'for the part where people should name the tune.</p>'
             f'<div style="margin:2pt 0 4pt">{D.body_svg(flips_body(1100, "page flips"))}</div>'
             f'<table class="t" style="font-size:9.6pt;line-height:1.25"><tr><th>Flip</th><th>What changes</th><th>In Logic</th></tr>{rows}</table>'
             f'<div class="box acc-b" style="margin-top:4pt;padding:4pt 10pt"><span class="k">The rule of the flip</span><p style="margin:0;font-size:9.8pt;line-height:1.3">'
             f'Change the rhythm, the register or the sound, but keep the pitches in order (except flip 3, on purpose). Play your flip next to the original: if a listener '
             f'cannot name the theme, bring back more of the original.</p></div>')
    return D.page("Five flips", "STUDENT", "Class 2", inner, n, wm, name=False, key="flips")


def pattern_card(p):
    body, w, h = grid_for(p)
    txt = (f'<p style="margin:0 0 2pt;font-size:9.6pt;line-height:1.28"><b>Drums.</b> {p["drums"]}</p>'
           f'<p style="margin:0 0 2pt;font-size:9.6pt;line-height:1.28"><b>808.</b> {p["bass"]}</p>'
           f'<p style="margin:0 0 2pt;font-size:9.6pt;line-height:1.28"><b>Sounds.</b> {p["sounds"]}</p>'
           f'<p style="margin:0;font-size:9.6pt;line-height:1.28"><b>Try.</b> {p["tryit"]}</p>')
    head = f'<span class="k" style="font-size:13pt;margin:0">{p["name"]} · {p["feel"]}</span>'
    return (f'<div class="box" style="margin-bottom:6pt;padding:6pt 10pt">{head}<div style="display:flex;gap:12pt;margin-top:3pt;align-items:flex-start">'
            f'<div style="flex:1">{txt}</div><div style="width:3.55in;flex:0 0 3.55in">{D.body_svg((body, w, h))}</div></div></div>')


def drums_page(n, wm=False):
    inner = (f'<p style="margin:0 0 4pt;font-size:10.8pt;line-height:1.38">Trap drums are simple and heavy. Each card gives a one-bar pattern '
             f'(16 steps, 4 to a beat; shaded steps are the beats), an 808 idea and sounds to try. Every pattern is <b>half-time</b>: the clap or snare lands on beat 3 only. Pick one for your '
             f'beat at 130 to 150 BPM and copy it into the Step Sequencer, or use a Drummer track, then add rolls (page {D.IX("fx1")}). Use pattern C only as the last bar of a phrase and pattern D for intros and breaks.</p>'
             + "".join(pattern_card(p) for p in PATTERNS))
    return D.page("Trap drum patterns", "STUDENT", "Class 2", inner, n, wm, name=False, key="drums")


def fx_card(head, rows, extra="", fs=11.2):
    body = "".join(f'<p style="margin:0 0 3.5pt;font-size:{fs}pt;line-height:1.34"><b>{a}.</b> {b}</p>' for a, b in rows)
    return (f'<div class="box" style="margin-bottom:6pt;padding:6pt 10pt"><span class="k" style="font-size:13pt;margin:0">{head}</span>'
            f'{extra}<div style="margin-top:3pt">{body}</div></div>')


FX_HATS = ("Hi-hat rolls · the trap signature", [
    ("What it does", "A roll is a burst of very fast hi-hat notes. Trap hats are steady eighths or sixteenths, with a roll of triplets or 32nd notes at the end of a bar or a phrase."),
    ("In Logic", "Put the closed hat on its own pad. In the Piano Roll draw the hats on a fine grid (1/16, 1/16 triplet or 1/32), or in the Step Sequencer set the hat row’s rate to a faster value. "
                 "A Note Repeater MIDI plug-in will repeat a held note. Ramp the velocities up (MIDI Draw or the velocity controls) so the roll swells."),
    ("Try", "Roll only in the last beat of the bar, and only every fourth bar. Keep the hats much quieter than the snare."),
    ("Listen for", "The hats speed up and lean into the next bar. If the whole beat is rolling, nothing stands out.")])
FX_808 = ("808 · the sub bass that is also a drum", [
    ("What it does", "A long, deep bass note that plays the chord roots and can glide from one to the next. It is felt more than heard."),
    ("In Logic", "Make a Software Instrument track with Alchemy or Retro Synth and look in the Library (Y) for a sub bass or 808 sound, or build one: a sine oscillator, "
                 "mono with Glide on, a long release. Play low notes (E1 to D2). Add a little Distortion or Overdrive so small speakers can hear it, "
                 "and put a Compressor on it with its Side Chain set to the kick."),
    ("Try", "One long root per chord. Cut each note a hair before the next kick. Glide only on the notes that change chord."),
    ("Listen for", "Weight under everything. If it vanishes on a laptop, add distortion; if it is muddy, make the notes shorter.")])
FX_SNARE = ("Half-time snare · the heavy backbeat", [
    ("What it does", "In half-time the clap or snare lands on beat 3 only, not on 2 and 4, so the beat feels half as fast even though the hats are busy."),
    ("In Logic", "Put a clap and a snare on their own pads (Drum Machine Designer) and click both on step 9 of the Step Sequencer, which is beat 3. "
                 "Layer them, and put a long reverb on the clap. A Drummer track can do the same if you move its snare to beat 3."),
    ("Try", "Add a very quiet ghost hit before beat 3, or leave a bar with no snare before a drop. Keep the kick to three hits a bar or fewer."),
    ("Listen for", "The beat feels slow and heavy while the hats still move. If it sounds like a march, check that the snare is only on beat 3.")])
FX_FLIP = ("Flip the melody · same tune, new job", [
    ("What it does", "A flip changes a melody’s rhythm, register or sound while keeping its notes. See the five flips on page @FLIPS."),
    ("In Logic", "In the Piano Roll shorten the notes to chop them, drag notes up 12 rows to jump an octave, or set Transpose in the Region inspector. "
                 "To play slices from the keyboard, bounce the melody to audio and drop it into Quick Sampler. For a new sound, try a bell, a pluck or a mallet instrument from the Library."),
    ("Try", "Play the original in the intro, a chopped version in Beat A and an octave higher in Beat B. Move the flipped tune away from the 808’s register."),
    ("Listen for", "A listener should still name the theme. If they cannot, bring back more of the original rhythm.")])
FX_RISER = ("Riser and drop · tension and release", [
    ("What it does", "A riser is a sound that climbs before a drop. The drop is the moment the 808 and the kick come back. A beat of silence just before it makes it hit harder."),
    ("In Logic", "Use a synthesizer’s noise oscillator and automate its filter cutoff or pitch upward (press A for automation), or search the Loop Browser (O) for a riser or sweep. "
                 "To reverse a cymbal or a hit, bounce it to audio and use Reverse in Quick Sampler. Put a ChromaVerb or Space Designer on the last note."),
    ("Try", "One riser of two bars before each drop. Cut every sound for one beat, then bring the 808 back on beat 1."),
    ("Listen for", "The room fills up, then empties, then the bass lands. If the drop does not hit, make the silence longer.")])


def fx1_page(n, wm=False):
    hats = D.body_svg(hats_body(1100, "page hats"))
    inner = (f'<p style="margin:0 0 4pt;font-size:10.8pt;line-height:1.38">Five moves make a beat sound like trap: hi-hat rolls, an 808, a half-time snare, a flipped melody and a '
             f'riser and drop. Use at least four. This page has the rolls and the 808; page {D.IX("fx2")} has the other three. Every move should leave room for the theme.</p>'
             + fx_card(FX_HATS[0], FX_HATS[1], f'<div style="margin-top:3pt">{hats}</div>')
             + fx_card(FX_808[0], FX_808[1]))
    return D.page("Trap effect cards · 1 of 2", "STUDENT", "Class 3", inner, n, wm, name=False, key="fx1")


def fx2_page(n, wm=False):
    cheat_rows = [("Hi-hat rolls", "Last beat of every fourth bar; triplets or 32nds; velocity ramps up"), ("808", "Roots E1 to D2, Glide on, light distortion, sidechain to the kick"),
                  ("Half-time snare", "Clap and snare on beat 3 only; reverb on the clap"), ("Flip", "Chop, octave jump or reverse; one flip per section"),
                  ("Riser and drop", "Two-bar riser, one beat of silence, then the 808 returns")]
    cheat = "".join(f"<tr><td style='width:22%'><b>{a}</b></td><td>{b}</td></tr>" for a, b in cheat_rows)
    inner = (fx_card(*FX_SNARE, fs=10.4) + fx_card(FX_FLIP[0], [(a, D.fill(b)) for a, b in FX_FLIP[1]], fs=10.4) + fx_card(*FX_RISER, fs=10.4)
             + f'<div class="box" style="padding:5pt 10pt;margin-bottom:6pt"><span class="k">Starting settings, all five moves</span>'
               f'<table class="t" style="font-size:10.4pt;margin-top:3pt">{cheat}</table></div>')
    return D.page("Trap effect cards · 2 of 2", "STUDENT", "Class 3", inner, n, wm, name=False, key="fx2")


TRAP_MENU = ["Hi-hat rolls", "808 sub bass with glide", "Half-time snare or clap", "Flip: chop, octave jump or reverse", "Riser and drop",
             "Open hat or ghost hits", "Sidechain the 808 to the kick", "Automation (filter, distortion or reverb)"]


def plan_page(n, wm=False):
    half = (len(TRAP_MENU) + 1) // 2
    items = [D.chk(f"<b>{m}</b> — where: <span style='display:inline-block;width:1.0in;border-bottom:1pt solid #000'>&nbsp;</span>", 11,
                   "font-size:10.2pt;margin-bottom:4pt") for m in TRAP_MENU]
    rows = "".join("<tr><td style='height:21pt'></td><td></td><td></td></tr>" for _ in range(5))
    chords = "".join(f"<td style='height:24pt;text-align:center'><b>Bar {i}</b></td>" for i in range(1, 5))
    roll = D.body_svg(roll_body([], 64, 16, 4, 55, 67, 1100, 14, 1, None, "blank roll"))
    inner = (f'<p style="margin:0 0 4pt;font-size:10.6pt;line-height:1.36">Step 2: plan. Pick one theme, a tempo from 130 to 150 BPM and a drum pattern, '
             f'then decide which trap moves you will use. You need at least four of the five (requirement 4), and the theme must still be recognizable.</p>'
             f'<div class="box acc-b" style="margin:0 0 5pt"><span class="k">My choices</span>'
             f'<div class="fl" style="margin:3pt 0 0"><b>My theme:</b><span></span><b>Key:</b><span></span></div>'
             f'<div class="fl" style="margin:0"><b>Tempo (BPM):</b><span style="flex:0 0 0.9in"></span><b>Drum pattern (A, B, C or D):</b><span style="flex:0 0 0.9in"></span>'
             f'<b>Why this tempo:</b><span></span></div></div>'
             f'<span class="k">The chords of my loop (from my chart, or my own)</span>'
             f'<table class="map" style="margin-bottom:4pt"><tr>{chords}</tr><tr>' + "".join("<td style='height:24pt'></td>" for _ in range(4)) + '</tr></table>'
             f'<span class="k">My trap moves (check at least four)</span>'
             f'<div class="cols" style="gap:12pt"><div>{"".join(items[:half])}</div><div>{"".join(items[half:])}</div></div>'
             f'<div class="fl" style="margin-top:3pt"><b>What stays the same, so people still know the tune:</b><span></span></div>'
             f'<span class="k">My layers</span>'
             f'<table class="map" style="margin-bottom:4pt"><tr><th style="width:18%">Layer</th><th style="width:38%">Sound or instrument in Logic</th>'
             f'<th>What it plays</th></tr>{rows}</table>'
             f'<span class="k">Sketch: a counter-melody or a flipped rhythm for the first four bars (pencil, optional)</span>'
             f'<div style="margin-top:2pt">{roll}</div>')
    return D.page("Beat plan", "STUDENT", "Class 1", inner, n, wm, name=True, key="plan")


ARR_COLS = 24         # each column is two bars: 48 bars
LEN_BARS = (40, 44, 48)
LEN_BPMS = (130, 135, 140, 145, 150)


def arrange_page(n, wm=False):
    head = "<tr><th style='width:1.1in'>Layer</th>" + "".join(f"<th>{2 * i + 1}</th>" for i in range(ARR_COLS)) + "</tr>"
    body = "".join("<tr><td class='l' style='height:25pt'></td>" + "".join(f"<td class='{'b' if i % 2 == 0 else ''}'></td>" for i in range(ARR_COLS))
                   + "</tr>" for _ in range(8))
    hr = "".join(f"<tr><td><b>{b}</b></td><td>{240 / b:.2f} s</td>" + "".join(f"<td>{length_s(bars, b):.1f} s</td>" for bars in LEN_BARS) + "</tr>"
                 for b in LEN_BPMS)
    inner = (f'{CSS_SG}<style>table.sg th {{ font-size: 6.4pt; }} table.sg td.l {{ width: 1.1in; }}</style>'
             f'<p style="margin:0 0 4pt;font-size:10.4pt">Step 6: arrange. Give your beat a form: an intro, beat sections with a break and a drop, and an outro. Each column is 2 bars '
             f'(the number is its first bar). Shade the columns where each layer plays, write the layer’s name at the left, and mark where each section starts (every thick line is 4 bars). 60 to 90 seconds only.</p>'
             f'<table class="sg">{head}{body}</table>'
             f'<div class="cols" style="gap:10pt;margin-top:6pt"><div class="box acc-b"><span class="k">My sections</span>'
             f'<div class="fl" style="margin:3pt 0 0"><b>Intro:</b><span></span><b>bars</b><span style="flex:0 0 0.6in"></span></div>'
             f'<div class="fl"><b>Beat:</b><span></span><b>bars</b><span style="flex:0 0 0.6in"></span></div>'
             f'<div class="fl"><b>Break:</b><span></span><b>bars</b><span style="flex:0 0 0.6in"></span></div>'
             f'<div class="fl" style="margin-bottom:0"><b>Outro:</b><span></span><b>bars</b><span style="flex:0 0 0.6in"></span></div></div>'
             f'<div><span class="k">Length helper (4/4)</span><table class="t" style="font-size:9.4pt;margin-top:2pt"><tr><th>BPM</th><th>One bar</th>'
             f'<th>{LEN_BARS[0]} bars</th><th>{LEN_BARS[1]} bars</th><th>{LEN_BARS[2]} bars</th></tr>{hr}</table><p class="small" style="margin:1pt 0 0">Aim for 60 to 90 seconds. '
             f'Seconds = bars × 240 ÷ BPM.</p></div></div>'
             f'<div class="fl" style="margin-top:6pt"><b>My tempo:</b><span style="flex:0 0 0.8in"></span><b>Bars:</b><span style="flex:0 0 0.8in"></span>'
             f'<b>Length: bars × 240 ÷ tempo =</b><span style="flex:0 0 0.8in"></span><b>seconds</b></div>'
             f'<div class="box" style="margin-top:4pt"><span class="k">Checks before I bounce</span>'
             + "".join(D.chk(c, 11, "font-size:10pt;margin-bottom:2pt") for c in [
                 "I can name the theme in the first ten seconds, and the melody is louder than the hats.",
                 "Every pitch and length matches the chart, or a flip I planned.",
                 "The 808 is clear and not muddy, and the snare is only on beat 3.",
                 "At least four trap moves are on, each audible, and EQ is in use.",
                 "The beat is between 60 and 90 seconds."]) + '</div>')
    return D.page("Arrangement plan", "STUDENT", "Classes 3–4", inner, n, wm, name=True, key="arrange")


def example_page(n, wm=False):
    moves = "".join(f"<tr><td style='width:16%'><b>{a}</b></td><td>{D.fill(b)}</td></tr>" for a, b in EX_MOVES)
    inner = (f'<p style="margin:0 0 4pt;font-size:10.2pt">An <b>invented plan on paper</b>: the Sugar Plum Fairy, the four-bar loop, as a trap beat at '
             f'{EX_BPM} BPM. No audio is included. Student projects will differ. Page 1 of 2: the plan and the trap moves.</p>'
             f'<div class="cols" style="gap:10pt"><div class="box"><span class="k">1 · A weak plan</span><p style="margin:0;font-size:10.2pt">{EX_WEAK}</p>'
             f'<p style="margin:3pt 0 0;font-size:9.2pt">It names no tempo, no moves and nothing that would sound like trap.</p></div>'
             f'<div class="box acc-b"><span class="k">2 · A clear plan</span><p style="margin:0;font-size:8.6pt;line-height:1.28">{EX_STRONG}</p></div></div>'
             f'{D.H2("3 · Five trap moves, and what stays")}'
             f'<table class="t" style="font-size:9.2pt;line-height:1.22">{moves}<tr><td><b>Stays</b></td><td>{EX_STAYS}</td></tr></table>'
             f'{D.H2("4 · The loop on the piano roll, with its chords (bars 1–4)")}'
             f'<div style="width:6.6in;margin:2pt auto 0">{D.body_svg(tune_roll("sugar", 0, 4, 1100, "page example roll"))}</div>')
    return D.page("Worked example · an invented beat", "EXAMPLE", "Teacher", inner, n, wm, ak=True, key="example")


def example2_page(n, wm=False):
    secs = "".join(f"<tr><td style='width:22%'><b>{nm}</b></td><td style='white-space:nowrap'>bars {a}–{b}</td><td>{mmss((a - 1) * EX_BAR_S)}–{mmss(b * EX_BAR_S)}</td></tr>"
                   for nm, a, b in EX_SECTIONS)
    lay = "".join(f"<tr><td style='width:15%'><b>{nm}</b></td><td>{d}</td></tr>" for nm, _s, d in EX_LAYERS)
    chs = "".join(f"<td><b>Bar {i + 1}</b><br>{chord_text(c)}<br><span style='font-size:7.4pt'>808 {' · '.join(dict.fromkeys(BASS_ROOT[x] for _, x in c))}</span></td>"
                  for i, c in enumerate(SUGAR_CH))
    qs = " ".join(f"{i + 1}. {q}" for i, q in enumerate(EX_QUESTIONS))
    inner = (f'<p style="margin:0 0 3pt;font-size:10pt">The same beat, page 2 of 2: the map of the whole piece, then the numbers.</p>'
             f'{D.H2("5 · The map: 1:04, five sections, eight layers, three lanes")}'
             f'<div style="width:6.5in;margin:1pt auto 3pt">{D.body_svg(map_body(1250, "page map", 24, 20))}</div>'
             f'<div class="cols" style="gap:10pt"><div><span class="k" style="font-size:9.4pt">6 · Sections</span>'
             f'<table class="t" style="font-size:8.6pt;line-height:1.2;margin-top:2pt">{secs}</table></div>'
             f'<div><span class="k" style="font-size:9.4pt">7 · Layers (in to out)</span>'
             f'<table class="t" style="font-size:7.8pt;line-height:1.14;margin-top:2pt">{lay}</table></div></div>'
             f'<span class="k" style="font-size:9.4pt;display:block;margin-top:3pt">8 · The chords of the 4-bar loop, with the 808 root (the melody’s first and longest notes are chord tones)</span>'
             f'<table class="t" style="font-size:8.8pt;line-height:1.15;margin-top:2pt;text-align:center"><tr>{chs}</tr></table>'
             f'<div class="box acc-b" style="margin-top:4pt"><span class="k">9 · Checking the numbers</span><p style="margin:0;font-size:8.6pt;line-height:1.28">'
             f'One bar of 4/4 at {EX_BPM} BPM lasts 240 ÷ {EX_BPM} = {EX_BAR_S:g} seconds, so {EX_BARS} bars = {EX_BARS * EX_BAR_S:g} seconds, inside 60 to 90. '
             f'The sections are {" + ".join(str(b - a + 1) for _, a, b in EX_SECTIONS)} bars = {EX_BARS}. Beat B has the most layers ({max(EX_DENS)}). '
             f'<b>Three feedback questions (invented):</b> {qs}</p></div>')
    return D.page("Worked example · the map", "EXAMPLE", "Teacher", inner, n, wm, ak=True, key="example2")


PAGES = {"howto": howto_page, "overview": overview_page, "setup": setup_page, "tunes": tunes_page, "example": example_page,
         "example2": example2_page, "sugar": chart_page("sugar"), "trepak": chart_page("trepak"), "flips": flips_page,
         "drums": drums_page, "fx1": fx1_page, "fx2": fx2_page, "plan": plan_page, "arrange": arrange_page}


# ================================================================ content checks (melodies, chords, flips, drums, hat numbers, the worked example, no audio)
def seg_ok(notes, a, b, chord):
    """The first note and the longest note that start in [a, b) are tones of the chord."""
    ins = [(p, s, d) for p, s, d in notes if a <= s < b]
    if not ins:      # a note held through the whole segment
        held = [p for p, s, d in notes if s < a and s + d >= b]
        return bool(held) and held[0].rstrip("0123456789") in CHORD_TONES[chord]
    first = ins[0][0]
    longest = max(ins, key=lambda x: x[2])[0]
    tones = CHORD_TONES[chord]
    return first.rstrip("0123456789") in tones and longest.rstrip("0123456789") in tones


def chord_root(ch):
    return ch[:2] if len(ch) > 1 and ch[1] == "#" else ch[0]


# What two transcriptions agree on, score bar by score bar (a 2/4 bar is 8 sixteenths): (pitch names at score pitch, onsets in sixteenths)
EXPECT = {
    "sugar": [(["G6", "E6", "G6", "F#6"], [2, 3, 4, 6]), (["D#6", "E6", "D6", "D6", "D6"], [0, 2, 4, 5, 6]),
              (["C#6", "C#6", "C#6", "C6", "C6", "C6"], [0, 1, 2, 4, 5, 6]), (["B5", "E6", "C6", "E6", "B5"], [0, 1, 2, 3, 4]),
              (["G5", "E5", "G5", "F#5"], [2, 3, 4, 6]), (["C6", "B5", "G6", "G6", "G6"], [0, 2, 4, 5, 6]),
              (["F#6", "F#6", "F#6", "E6", "E6", "E6"], [0, 1, 2, 4, 5, 6]), (["D#6", "F#6", "E6", "F#6", "D#6"], [0, 1, 2, 3, 4])],
    "trepak": [(["G5", "G5", "F#5", "G5", "G5"], [0, 2, 3, 4, 6]), (["E5", "D5", "C5", "E5"], [0, 2, 4, 6]),
               (["D5", "D5", "C#5", "D5", "D5"], [0, 2, 3, 4, 6]), (["B4", "A4", "G4", "B4", "D5"], [0, 2, 4, 6, 7]),
               (["A4", "A4", "D5", "G4", "G4", "D5"], [0, 2, 3, 4, 6, 7]), (["F#4", "F#4", "D5", "A4", "A4", "D5"], [0, 2, 3, 4, 6, 7]),
               (["B4", "B4", "D5", "G4", "G4", "D5"], [0, 2, 3, 4, 6, 7]), (["A4", "G4", "A4", "D5", "E5", "F#5"], [0, 2, 4, 5, 6, 7])]}


def verify_content():
    import re
    errs = []
    counts = dict(goals=(GOALS, 4), vocab=(VOCAB, 4), reqs=(REQS, 6), steps=(STEPS, 7), tips=(TIPS, 4), check=(CHECK, 6),
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
    # ---- the two melodies
    expect = {"sugar": (4, 40, "E4", "G5", "D#5"), "trepak": (4, 43, "F#4", "G5", "F#5")}
    for k, T in TUNES.items():
        nb, nn, lo, hi, last = expect[k]
        if len(T["bars"]) != nb or len(T["chords"]) != nb or len(SRC[k]) != nb:
            errs.append(f"{k}: {nb} chart bars and a chord list for each expected")
        if T["bar_len"] != 16 or T["time"] != "4/4":
            errs.append(f"{k}: chart bars are 16 sixteenths of 4/4")
        for i, bar in enumerate(T["bars"]):
            if sum(d for _, d in bar) != 16:
                errs.append(f"{k}: bar {i + 1} adds to {sum(d for _, d in bar)} sixteenths, not 16")
            if sum(ln for ln, _ in T["chords"][i]) != 16:
                errs.append(f"{k}: the chords of bar {i + 1} do not fill the bar")
            for p, d in bar:
                if d not in LEN_NAMES:
                    errs.append(f"{k}: bar {i + 1} has a length ({d}) with no name")
                if p != "R" and p[:-1].rstrip("#") + ("#" if "#" in p[:-1] else "") not in SCALE_PCS[k]:
                    errs.append(f"{k}: {p} is not in the scale of the piece (fewer than expected accidentals)")
        if note_count(k) != nn:
            errs.append(f"{k}: {note_count(k)} notes, expected {nn}")
        ms = [midi(p) for p, _, _ in tune_notes(k)]
        if min(ms) != midi(lo) or max(ms) != midi(hi):
            errs.append(f"{k}: range {pname(min(ms))}-{pname(max(ms))}, expected {lo}-{hi}")
        if not T["lo"] <= min(ms) or not max(ms) <= T["hi"]:
            errs.append(f"{k}: the roll's rows do not cover the notes")
        if T["bars"][-1][-1][0] != last:
            errs.append(f"{k}: last note {T['bars'][-1][-1][0]}, expected {last}")
        # the chart is the score pitch moved down SHIFT semitones, note for note and length for length
        for bs, bc in zip(SRC[k], T["bars"]):
            if [(p if p == "R" else midi(p) - SHIFT[k], d) for p, d in bs] != [(p if p == "R" else midi(p), d) for p, d in bc]:
                errs.append(f"{k}: the chart is not the score moved down {SHIFT[k]} semitones")
        # pitches and onsets against the two transcriptions' agreement, score bar by score bar
        flat = [(p, s) for p, s, _ in tune_notes_src(k)]
        pos = 0
        for pitches, onsets in EXPECT[k]:
            got = flat[pos:pos + len(pitches)]
            pos += len(pitches)
            if [p for p, _ in got] != pitches:
                errs.append(f"{k}: pitches {[p for p, _ in got]} differ from the transcription {pitches}")
            base = (got[0][1] // 8) * 8 if got else 0
            if [s - base for _, s in got] != onsets:
                errs.append(f"{k}: onsets {[s - base for _, s in got]} differ from the transcription {onsets}")
        if pos != len(flat):
            errs.append(f"{k}: the chart has {len(flat) - pos} notes the transcription does not")
        for i, spans in enumerate(T["chords"]):
            t = i * 16
            for ln, ch in spans:
                if ch not in CHORD_TONES:
                    errs.append(f"{k}: unknown chord {ch}")
                    continue
                if not seg_ok(tune_notes(k), t, t + ln, ch):
                    errs.append(f"{k}: chord {ch} in bar {i + 1} (steps {t}-{t + ln}) does not hold the first and longest notes")
                r = BASS_ROOT[ch]
                if r.rstrip("0123456789") != chord_root(ch) or not 28 <= midi(r) <= 40:
                    errs.append(f"808 root for {ch}: {r}")
                t += ln
    if SUGAR_CH[-1] != [(16, "B7")] or SUGAR_CH[0][0][1] != "Em" or TREPAK_CH[-1][-1][1] != "D" or TREPAK_CH[0][0][1] != "G":
        errs.append("the loops must turn around: Sugar Plum B7 -> Em, Trepak D -> G")
    # ---- drum patterns: 16 steps and the facts the cards claim
    hit = lambda p, ln: [i for i, c in enumerate(p["pat"][ln]) if c == "x"]
    for p in PATTERNS:
        if any(len(p["pat"][ln]) != 16 or set(p["pat"][ln]) - {"x", "."} for ln in LANES):
            errs.append(f"pattern {p['key']}: each drum lane is 16 steps of x and .")
        if hit(p, "Clap / snare") != [8]:
            errs.append(f"pattern {p['key']}: half-time means the clap or snare is on beat 3 only (step 8)")
    a, b, c, d = (pattern(k) for k in "abcd")
    if hit(a, "Kick") != [0, 10] or hit(a, "Hi-hat") != list(range(0, 16, 2)) or hit(a, "Open hat"):
        errs.append("pattern A: kick on beat 1 and an eighth after beat 3, hats on eighths, no open hat")
    if hit(b, "Kick") != [0, 3, 10] or hit(b, "Hi-hat") != list(range(16)) or hit(b, "Open hat") != [14]:
        errs.append("pattern B: kick on 1, the last 16th of beat 1 and the 'and' of 3; hats on every 16th; open hat on step 14")
    if hit(c, "Kick") != [0, 6, 10] or hit(c, "Hi-hat") != [0, 2, 4, 6, 8, 10, 12, 13, 14, 15]:
        errs.append("pattern C: kick on 1, the 'and' of 2 and the 'and' of 3; eighth hats then four 16ths (the roll) in the last beat")
    if hit(d, "Kick") != [0] or hit(d, "Hi-hat") != [4, 12] or hit(d, "Open hat") != [14]:
        errs.append("pattern D: kick on 1; hats on beats 2 and 4; open hat on step 14")
    # ---- hi-hat roll numbers
    if [per for _, _, per in HATS] != [4, 6, 8] or [r for _, r, _ in HATS] != ["1/16", "1/16T", "1/32"]:
        errs.append("hat rates: 1/16 (4 a beat), 1/16T (6), 1/32 (8)")
    if beat_ms(150) != 400 or hat_gap_ms(4, 150) != 100 or abs(hat_gap_ms(6, 150) - 66.6667) > 1e-3 or hat_gap_ms(8, 150) != 50:
        errs.append("at 150 BPM a beat is 400 ms: 100, 66.7 and 50 ms")
    # ---- the flips are computed from the same nine notes
    src = flip_src()
    if [p for p, _, _ in src] != ["G5", "G5", "F#5", "G5", "G5", "E5", "D5", "C5", "E5"] or sum(d for _, _, d in src) != 16:
        errs.append("flip source: the nine notes of Trepak chart bar 1")
    f = {nm: fn(src) for nm, _, fn in FLIPS}
    st, ch, rv, oc, dr = (f[k] for k in ("1 · Stretch", "2 · Chop", "3 · Reverse", "4 · Octave jump", "5 · Drop"))
    if st != [(p, 2 * s, 2 * d) for p, s, d in src] or max(s + d for _, s, d in st) != 32:
        errs.append("flip 1 must double every start and length (two bars)")
    if [(p, s) for p, s, _ in ch] != [(p, s) for p, s, _ in src] or any(d != 1 for _, _, d in ch):
        errs.append("flip 2 keeps pitches and starts and makes every length 1")
    if [p for p, _, _ in rv] != [p for p, _, _ in reversed(src)] or [d for _, _, d in rv] != [d for _, _, d in reversed(src)] \
            or any(x[1] + x[2] > y[1] for x, y in zip(rv, rv[1:])) or max(s + d for _, s, d in rv) != 16:
        errs.append("flip 3 must be the bar backwards, without overlaps")
    if [(midi(q) - midi(p)) for (p, _, _), (q, _, _) in zip(src, oc)] != [12 * (i % 2) for i in range(len(src))] or [s for _, s, _ in oc] != [s for _, s, _ in src]:
        errs.append("flip 4 moves every second note up an octave")
    if [(midi(q) - midi(p)) for (p, _, _), (q, _, _) in zip(src, dr)] != [-12] * len(src):
        errs.append("flip 5 moves every note down an octave")
    if len(FLIP_ROWS) != 5 or len(FLIPS) != 6:
        errs.append("five flips and the original")
    # ---- the worked example adds up
    if EX_BAR_S != 1.6 or EX_BARS * EX_BAR_S != 64 or not 60 <= EX_BARS * EX_BAR_S <= 90:
        errs.append("40 bars x 1.6 s = 64 s, inside 60 to 90")
    if not 130 <= EX_BPM <= 150:
        errs.append("the example tempo must sit in 130 to 150 BPM")
    if EX_SECTIONS[0][1] != 1 or EX_SECTIONS[-1][2] != EX_BARS or any(b_ + 1 != c_ for (_, _, b_), (_, c_, _) in zip(EX_SECTIONS, EX_SECTIONS[1:])):
        errs.append("sections must tile bars 1-40")
    if [b_ - a_ + 1 for _, a_, b_ in EX_SECTIONS] != [4, 12, 4, 16, 4] or sum(b_ - a_ + 1 for _, a_, b_ in EX_SECTIONS) != EX_BARS:
        errs.append("sections 4 + 12 + 4 + 16 + 4 = 40")
    if len(EX_LAYERS) != 8 or len(EX_AUTO) != 3 or len(EX_MOVES) != 5:
        errs.append("eight layers, three automation lanes, five trap moves")
    for nm, spans, _d in EX_LAYERS:
        for a_, b_ in spans:
            if not 1 <= a_ <= b_ <= EX_BARS:
                errs.append(f"layer {nm}: span {a_}-{b_} outside the piece")
    spans = {nm: (min(a_ for a_, _ in sp), max(b_ for _, b_ in sp)) for nm, sp, _ in EX_LAYERS}
    for ly, par, pts in EX_AUTO:
        a_, b_ = spans[ly]
        ts_ = [t_ for t_, _ in pts]
        vs = [v for _, v in pts]
        if ts_ != sorted(ts_) or len(pts) < 3 or ts_[0] < a_ or ts_[-1] > b_:
            errs.append(f"lane {ly}/{par}: points in order, 3+, inside its layer")
        if max(vs) - min(vs) < .5:
            errs.append(f"lane {ly}/{par}: a lane that barely moves")
    top = max(EX_DENS)
    mb = next((a_, b_) for nm, a_, b_ in EX_SECTIONS if nm == "Beat B")
    if [i + 1 for i, dd in enumerate(EX_DENS) if dd == top] != list(range(mb[0], mb[1] + 1)):
        errs.append("the most layers must play in exactly Beat B")
    brk = next((a_, b_) for nm, a_, b_ in EX_SECTIONS if nm == "Break")
    ba = next((a_, b_) for nm, a_, b_ in EX_SECTIONS if nm == "Beat A")
    if EX_DENS[0] >= top or EX_DENS[-1] >= top or min(EX_DENS[brk[0] - 1:brk[1]]) >= min(EX_DENS[ba[0] - 1:ba[1]]):
        errs.append("the piece starts smaller than its peak, drops in the Break and resolves down")
    if [round(length_s(bars, bpm), 1) for bpm in LEN_BPMS for bars in LEN_BARS] != \
            [73.8, 81.2, 88.6, 71.1, 78.2, 85.3, 68.6, 75.4, 82.3, 66.2, 72.8, 79.4, 64.0, 70.4, 76.8]:
        errs.append("length helper numbers")
    if any(not 60 <= length_s(bars, bpm) <= 90 for bpm in LEN_BPMS for bars in LEN_BARS):
        errs.append("every length-helper cell must sit inside 60 to 90 seconds")
    if len(EX_QUESTIONS) != 3:
        errs.append("three feedback questions")
    for need in ("150 BPM", "40 bars, 64 seconds", "Em B7 | C#dim7 Cdim7 Em | Em Cmaj7 | B7"):
        if need not in EX_STRONG:
            errs.append(f"the clear plan must say '{need}'")
    expect_chords = " | ".join(" ".join(c for _, c in bar) for bar in SUGAR_CH)
    if expect_chords not in EX_STRONG:
        errs.append("the clear plan's chords must be the chart's chords")
    if "♭" in EX_STRONG:
        errs.append("plain text only (no flat sign) in the clear plan")
    # no slide bullet may end mid-sentence (apostrophe-s, or a dangling article/preposition/possessive)
    dangling = {"a", "an", "the", "of", "to", "at", "in", "on", "for", "and", "or", "with", "your", "each", "every", "their", "its", "from", "by"}
    for i, s in enumerate(SLIDES, start=1):
        for b in [x.strip() for x in s[3].split("|") if x.strip()]:
            last = re.sub(r"[^\w’']", "", b.split()[-1]).lower()
            if b.endswith(("’s", "'s")) or last in dangling:
                errs.append(f"slide {i} bullet looks truncated: '{b}'")
    # slide notes that name a page number name a page that exists and is the right one
    ok_pages = {D.IX("drums"), D.IX("flips")}
    for i, s in enumerate(SLIDES, start=1):
        for m in re.finditer(r"\bpage (\d+)\b", s[4]):
            if int(m.group(1)) not in ok_pages:
                errs.append(f"slide {i} notes name page {m.group(1)}, which is neither the drum patterns nor the flips page")
        if "flips on page" in s[4] and f"page {D.IX('flips')}" not in s[4]:
            errs.append(f"slide {i}: flips page number")
        if "from page" in s[4] and f"page {D.IX('drums')}" not in s[4]:
            errs.append(f"slide {i}: drum pattern page number")
    return errs


def tune_notes_src(key):
    """(pitch, start, length) at SCORE pitch, from SRC, rests skipped (for the transcription check)."""
    out, t = [], 0
    for bar in SRC[key]:
        for p, d in bar:
            if p != "R":
                out.append((p, t, d))
            t += d
    return out


def verify_outputs(flat, stext, notes):
    errs = []
    alldeck = " ".join(stext + notes)
    txt = " ".join(flat)
    if "No audio" not in notes[0]:
        errs.append("deck slide 1 notes must say 'No audio'")
    for need in ("No audio, recordings, lyrics, artists or albums", "invented plan on paper", "public domain", "Tchaikovsky", "1892",
                 "1930 or earlier", "No student work is included", "IMSLP", "Note Repeater", "Side Chain",
                 "Created with the help of digital and AI tools. Notation and answer keys are verified before release."):
        if need not in txt:
            errs.append(f"PDF must say: '{need}'")
    if "What changed" in txt or "Kept as I wrote it" in txt or "my project menu" in txt or "my Digital Music Production" in txt:
        errs.append("ORIGINAL kit: no wording about changes to an owner's sheet")
    if "checked by hand" in txt or "handmade" in txt.lower() or "classroom-tested" in txt.lower() or "hand-checked" in txt.lower():
        errs.append("never claim hand checks or classroom testing for a new product")
    if GRADES_TEXT != "9–12" or "Grades 9–12" not in txt:
        errs.append("PDF: 'Grades 9–12'")
    import re
    import subprocess
    for k in ("sugar", "trepak"):
        raw = re.sub(r"\s+", " ", subprocess.run(["pdftotext", "-raw", "-f", str(D.IX(k)), "-l", str(D.IX(k)), D.files()["pdf"], "-"],
                                                 capture_output=True, text=True, check=True).stdout)
        for i, bar in enumerate(TUNES[k]["bars"]):
            if bar_text(bar) not in raw:
                errs.append(f"{k} chart page: bar {i + 1} '{bar_text(bar)}' is not printed")
    pat_pages = " ".join(flat[D.IX("drums") - 1:D.IX("drums")])
    for p in PATTERNS:
        if p["name"].lower() not in pat_pages.lower():
            errs.append(f"drum pattern card {p['name']} missing")
    fx = " ".join(flat[D.IX("fx1") - 1:D.IX("fx2")])
    for need in ("Hi-hat rolls", "808", "Half-time snare", "Flip", "Riser and drop", "every 100 ms", "every 66.7 ms", "every 50 ms"):
        if need.lower() not in fx.lower():
            errs.append(f"effect cards must say '{need}'")
    fl = " ".join(flat[D.IX("flips") - 1:D.IX("flips")])
    for need in ("Stretch", "Chop", "Reverse", "Octave jump", "Drop", "nine notes"):
        if need.lower() not in fl.lower():
            errs.append(f"flips page must say '{need}'")
    ex = " ".join(flat[D.IX("example") - 1:D.IX("example2")])
    for need in ("240 ÷ 150 = 1.6", "40 bars = 64 seconds", "4 + 12 + 4 + 16 + 4 bars = 40"):
        if need not in ex:
            errs.append(f"worked example must say '{need}'")
    up = open(os.path.join(HERE, "UPLOAD.md"), encoding="utf8").read()
    if "Grades 9-12" not in up or "`9th-grade`, `10th-grade`, `11th-grade`, `12th-grade`" not in up:
        errs.append("UPLOAD.md: grades 9-12 in the description and section 3")
    if "no audio" not in up.lower() or "Open question" not in up or "public domain" not in up or "Transcription used" not in up:
        errs.append("UPLOAD.md: must say no audio is included, say public domain, name the transcription used and record the open questions")
    m = re.search(r"= 1 cover \+ (\d+) teacher \+ (\d+) student \+ 1 terms page", up)
    if not m or 2 + int(m.group(1)) + int(m.group(2)) != len(PLAN):
        errs.append("UPLOAD.md: the page-count list (1 cover + teacher + student + 1 terms) must total the PDF's pages")
    if m and (int(m.group(1)) != D.IX("example2") - 1 or int(m.group(2)) != D.IX("reflect") - D.IX("sugar") + 1):
        errs.append("UPLOAD.md: teacher and student page counts must match the plan")
    for t in TAGS:
        if t not in up:
            errs.append(f"UPLOAD.md: tag {t} missing")
    for banned in ["Billie", "Beatles", "Daft", "Skrillex", "Disney", "Radiohead", "Billboard", "Roland", "TR-" + "808", "Bensound", "Ableton"]:
        if banned in alldeck or banned in txt:
            errs.append(f"must not name artists, albums, songs, sites, services or other brands ({banned})")
    return errs


def check_summary():
    return (f"Dance of the Sugar Plum Fairy (4 chart bars = score bars 5-12, {note_count('sugar')} notes) and Trepak (4 chart bars = score bars 1-8, "
            f"{note_count('trepak')} notes) match the transcription note for note and onset for onset, add up bar by bar, and every chord holds each "
            f"span's first and longest note; {len(PATTERNS)} half-time drum patterns match what their cards say; hat gaps are 100/66.7/50 ms at "
            f"{EX_BPM} BPM; the five flips are computed from the nine source notes; the worked example is {EX_BARS} bars at {EX_BPM} BPM = "
            f"{EX_BARS * EX_BAR_S:g} s (sections {'+'.join(str(b - a + 1) for _, a, b in EX_SECTIONS)}, {len(EX_LAYERS)} layers, peak "
            f"{max(EX_DENS)} layers only in Beat B, {len(EX_AUTO)} moving lanes); length helper correct; no audio, lyrics, artist names or student "
            f"work; grades 9-12; tags and subjects are not headings; no 'what changed' page (ORIGINAL).")


# ================================================================ UPLOAD.md (written by gen.py so every number matches the build)
def write_upload():
    np_, ns = len(PLAN), len(SLIDES)
    n_teacher = (PLAN.index("example2") + 1) - 1
    n_student = (PLAN.index("reflect") + 1) - (PLAN.index("sugar") + 1) + 1
    assert 2 + n_teacher + n_student == np_, "page-count list must total the PDF"
    nt = len(LISTING_TITLE)
    desc = (f"{DESC_START} students flip a public-domain Tchaikovsky theme into a trap beat in Logic Pro. They enter the melody and chords from a "
            f"piano-roll note chart, build a half-time drum pattern with hi-hat rolls and an 808 sub bass, and flip the tune by chopping it, jumping an octave or "
            f"reversing it. This Trap Nutcracker project takes {CLASSES} class periods and is an original Hudson Beat project; the steps are written for Logic Pro, "
            f"while the ideas (a half-time snare, an 808, rolling hats and a flipped melody make trap) carry over to GarageBand, Ableton Live and BandLab.\n\n"
            f"WHAT'S INCLUDED (ZIP: {np_}-page PDF = 1 cover + {n_teacher} teacher + {n_student} student + 1 terms page, plus {ns}-slide intro deck as .pptx and PDF)\n"
            f"• Teacher pages: how to use, project overview, setup, a {CLASSES}-class pacing guide with the deck slides for each class, two pages of teacher notes "
            f"(struggles, variations, resources, grading), a Logic quick reference, tune sources and the public-domain rule, and a two-page worked "
            f"example (an invented plan on paper: the Sugar Plum Fairy as a 64-second beat at 150 BPM, with its five trap moves, a 40-bar map, "
            f"eight layers, chords and three automation lanes) ({n_teacher} pages)\n"
            f"• Student pages: two piano-roll note charts (Dance of the Sugar Plum Fairy and Trepak) with every note listed bar by bar and a blank 808 roll, "
            f"five flips drawn from one bar of Trepak, four half-time drum patterns with grids, two pages of effect cards (hi-hat rolls with a diagram, 808, "
            f"half-time snare, flipping the melody, riser and drop), a Beat plan, an Arrangement plan with a length helper, the 3-page project sheet "
            f"(overview, goals, vocabulary, requirements, steps, tips, submission checklist), the /25 rubric, a vocabulary page, a feedback "
            f"planner and a reflection page ({n_student} pages)\n"
            f"• Teacher-presented intro deck, {ns} slides with speaker notes on every slide: a think-and-share hook, what the project is, how to read a "
            f"piano roll, building the beat, hi-hat rolls, trap drum patterns, a worked-example map, flipping the tune, what to turn in and the rubric\n\n"
            f"THE FOUR CLASS PERIODS\n"
            f"• Class 1: hook; choose a theme; fill in the Beat plan; enter the melody and chords\n"
            f"• Class 2: build the beat: half-time drums, hi-hat rolls, an 808 and a flipped melody\n"
            f"• Class 3: make it hit with the snare, the 808, a riser and a drop; plan the form; arrange and mix\n"
            f"• Class 4: bounce and hand in; presentations with feedback questions; reflection\n\n"
            f"WHAT STUDENTS LEARN\n"
            f"• Entering and editing notes and chords in Logic Pro's Piano Roll from a note chart\n"
            f"• Programming a half-time trap drum pattern, with hi-hat rolls and a velocity ramp\n"
            f"• Building an 808 sub bass on the chord roots, with glide and a little distortion\n"
            f"• Flipping a melody (chop, stretch, reverse, octave jump) so it stays recognizable\n"
            f"• Planning a 60 to 90 second arrangement with an intro, beat sections, a break, a drop and an outro, then explaining their choices in a reflection\n\n"
            f"GOOD TO KNOW\n"
            f"• There is no audio in this resource and no student work. Both themes are in the public domain (Tchaikovsky, 1892) and appear only as note charts, "
            f"with no lyrics; students make every sound themselves in Logic Pro\n"
            f"• The themes come from the Nutcracker ballet, but neither is a carol and neither has words; offer the ones that suit your school\n"
            f"• Requires Logic Pro on a Mac. A MIDI keyboard is not needed; nobody has to read staff notation\n"
            f"• Rubric: 5 categories scored 1-5, /{RUBRIC_TOTAL}; the final grade is the average of the student's and the teacher's score\n"
            f"• Grades 9-12; music technology or music production classes\n"
            f"• The deck uses the free Oswald and Source Sans 3 fonts (built into Google Slides); install them for PowerPoint or Keynote, or present "
            f"the PDF copy, which shows the intended look\n"
            f"• Every student page prints well in black and white\n\n"
            f"Logic Pro is a product of Apple Inc., named only to describe compatibility. This resource is not affiliated with Apple.\n\n"
            f"{D.DISCLOSURE_NEW}")
    md = f"""# UPLOAD: Trap Nutcracker, original Logic Pro project (TpT 040)

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
({nt} characters; the limit is 80.) The title leaves out Nutcracker, December and holiday words because TpT's Seasonal Titles notice blocked a holiday-named title on 027 (see 032, 033 and 034). If TpT accepts it, "Trap Nutcracker Logic Pro Project ..." is a strong December search term; "Logic Pro" would still sit in the first 30 characters.

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

**${PRICE}** (paid), multiple-license price ${PRICE}. The $9 set in the queue, the top of the $7-9 holiday-kit range, for a kit with {np_} pages + {ns} slides, two note charts, five flips, four drum patterns, five effect cards and a two-page worked example, listed in November and December.

## 8. Free or paid / free preview pages

Paid. Preview PDF (4 watermarked pages): the {CLASSES}-class pacing guide, the Sugar Plum Fairy note chart, the first effect-card page (hi-hat rolls and 808) and the /25 rubric. "Number of pages or slides" is {np_ + ns} ({np_} pages + {ns} slides).

## 9. Before you click publish

- [ ] **Needs QA approval first.** This is a new kit (not yet on TpT); the Manager releases it only after a QA `**Verdict: APPROVED**`.
- [ ] Cover and previews show "HUDSON BEAT" in type; PDF footers read "© 2026 Brian Lotze · Hudson Beat · For single-classroom use".
- [ ] No school name, logo, student names or work, audio, video, lyrics or Logic session anywhere (`gen.py --check` scans every output and every file in this folder).
- [ ] **Tunes are public domain (year and source for QA.md).** Tchaikovsky, The Nutcracker (ballet, first performed in St Petersburg in December 1892; the Op. 71a suite was first performed earlier in 1892; score published in the early 1890s; Tchaikovsky died in 1893). Dance of the Sugar Plum Fairy: the celesta tune, score bars 5-12 (Act II, Variation II of the Pas de deux; No. 3 of the suite). Trepak (Russian Dance): the main theme, score bars 1-8 (Act II divertissement; No. 4 of the suite). No recordings, no editions and no lyrics are used.
- [ ] **Transcription used.** Transcription used for the Sugar Plum Fairy: Ted Muller's free celesta part (tedmuller.us, MusicXML and MIDI of the score; the tune is the top note of the celesta's two-note chords), cross-checked with a second free MIDI sequence (classicalmidi.co.uk), which agrees on every melody note but one. Trepak: the melody line of the classicalmidi.co.uk sequence (Elias Bustos Maure), compared with the tune as printed in piano reductions. Pitches and onsets only; no engraving or edition is reproduced. `gen.py --check` compares every pitch and onset with the transcription's notes, bar by bar.
- [ ] **Original project.** Built with `ORIGINAL = True` in `tpt/_dmp2_common/dmp2.py` (like 031 and 036): no "what changed" page and the new disclosure line. The reflection page is the shared Reflection element, scored in the rubric's "Plan & Reflection" row.
- [ ] **Logic Pro names to confirm on a Mac with a current Logic.** Drum Machine Designer and its Step Sequencer (pattern rate), Drummer hip-hop or trap styles (stated as "if your version has one"), Alchemy and Retro Synth (sine oscillator, mono, Glide), Compressor Side Chain, Distortion and Overdrive, ChromaVerb and Space Designer, the Note Repeater MIDI plug-in, MIDI Draw and velocity controls in the Piano Roll, Quick Sampler (slices and Reverse), Region inspector Transpose, Command-T to split, the Loop Browser (O). Logic names middle C "C3" by default, so the kit says to subtract one from the chart's octave number. Nothing says a loop or preset of a given name exists.
"""
    md += f"""- [ ] **Open questions for the owner:** (1) **Black keys.** The note charts are not all white keys: the Sugar Plum Fairy melody is chromatic (E minor with F#, D# and C#; kept at that key, moved down one octave) and Trepak is in G major with F# and one C#. They are marked with sharps on the rolls and in the note lists. (2) **One uncertain note.** Chart bar 3, the second note of the second half-bar (score bar 10): the celesta part says B, the other sequence says D; the chart uses B. Please glance at a published score (IMSLP, Op. 71) if you want it certain. (3) **Title.** No "Nutcracker" in the title because of TpT's seasonal-title notice (see 1). (4) **Price.** $9, as in the queue.
"""
    with open(os.path.join(HERE, "UPLOAD.md"), "w", encoding="utf8") as f:
        f.write(md)


if __name__ == "__main__":
    if "--check" not in sys.argv:
        write_upload()
    D.main(sys.modules[__name__])
