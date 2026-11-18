#!/usr/bin/env python3
"""Logic Pro project kit: Sleigh Bell Groove (TpT 057): the teacher resource, the intro deck and the listing files.

    python3 gen.py            build everything into this folder (also writes UPLOAD.md)
    python3 gen.py --lowres   same, but square images at scale 1 and small page shots (self-check only; --check rejects it)
    python3 gen.py --check    verify content and layout: the 16-step grid (4 beats of 4 sixteenths, counts 1 e & a), every step-grid
                              pattern card (hits, counts, which hits 16th-note and 8th-note swing move), the straight versus swung timing
                              table (swing percent to milliseconds at 120 BPM, all 16 steps), the tempo and groove-length arithmetic, the
                              worked example (8 bars at 100 BPM = 19.2 s), Step N references on every page, slide and UPLOAD.md, drawings
                              (each one rendered alone on a transparent ground: no ink within 3 px of its edge), the hero art, files,
                              page and slide counts, class slots, fonts, fit and overlap, dead space, truncated slide bullets, the
                              edges of cover.png and the previews, banned strings, tpt.json and UPLOAD.md

An ORIGINAL Hudson Beat project (dmp2.ORIGINAL = True, like 045, 048 and 053). Students program a holiday percussion groove with no
melody: sleigh bells, shaker, tambourine, wood block, kick, snare and hi-hat, in Logic Pro's Drum Machine Designer and Step Sequencer,
a 4-bar groove and then an 8-bar groove, and compare STRAIGHT with SWING feel. No audio ships, no song or melody is notated.
The art on the cover, the previews and the deck is the owner's pre-made hero (art/hero.png), used whole. Everything else (step grids,
pair diagrams, the arrangement map) is drawn in code. The shared builder is ../_dmp2_common/dmp2.py.
"""
import math
import os
import re
import subprocess
import sys
from html import escape

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "_dmp2_common"))
import dmp2 as D  # noqa: E402

ORIGINAL = True
SLUG = "sleigh-bell-groove"
TITLE = "Sleigh Bell Groove"
ACCENT = "#2F7FB8"          # this product's single accent: icy blue (a shade deeper than the art's #4FA3D9, so small labels read)
ACC_LIGHT = "#DCEBF6"
PRICE = "7.00"
CLASSES = 3
GRADES_TEXT = "9–12"
GRADE_SLUGS = ["9th-grade", "10th-grade", "11th-grade", "12th-grade"]
TAGS = ["Winter", "Project-based Learning", "Projects", "Activities"]     # exact entries of tpt/TAG-OPTIONS.json, none a heading
SUBJECTS = ["Music", "Computer Science - Technology", "Music Composition"]     # all in SUBJECT-OPTIONS.json, none a heading
ANSWER_KEY = None
LISTING_TITLE = "Logic Pro Drum Programming | Straight vs Swing Groove | High School Music Tech"
DESC_START = "Drum programming for high school music technology:"
DESC_MUST = ["Sleigh Bell Groove", "Step Sequencer", "Drum Machine Designer", "no audio", "swing", "16-step", "milliseconds", "19.2 seconds"]
ZIP_DIR = "Sleigh Bell Groove - Hudson Beat"
ZIP_DATE = (2026, 11, 18, 12, 0, 0)
TYPE = "Original Project"
PROJ_LINE = "Music Technology | <i>Percussion Programming Project</i> | 3 class periods"
DECK_STRAP = "Holiday percussion"
REFLECT_ROW = "Plan &amp; Reflection"
# split so this file never contains them (the --check scan reads every file in this folder)
BANNED_EXTRA = ["Rud" + "olph", "Fro" + "sty", "Gri" + "nch", "Santa Claus " + "Is", "Jingle Bell " + "Rock", "Feliz " + "Navidad",
                "Mari" + "ah Carey", "Spoti" + "fy", "You" + "Tube", "Home " + "Alone", "Nin" + "tendo", "Ro" + "land",
                "Sleigh " + "Ride", "Winter " + "Wonderland", "Let It " + "Snow", "Silver " + "Bells"]

# ================================================================ page plan (teacher pages 2-10, student pages 11-23)
PLAN = ["cover", "howto", "overview", "setup", "pacing", "tn1", "tn2", "logicref", "example", "example2", "grid1", "grid2", "swing", "plan",
        "layers", "listen", "proj1", "proj2", "proj3", "rubric", "vocab", "present", "reflect", "terms"]


def pg(k):
    return PLAN.index(k) + 1


# ================================================================ the music arithmetic (all verified in --check)
STEP_LABELS = ["1", "e", "&", "a"]          # the count inside one beat: four sixteenth notes
STEPS_PER_BEAT, BEATS = 4, 4
NSTEPS = STEPS_PER_BEAT * BEATS             # 16 steps = one bar of 4/4 in sixteenth notes
TEMPO_LO, TEMPO_HI = 90, 120                # the project's tempo range
SW_PCTS = (50, 55, 60, 66, 75)              # swing percents in the table; 50 is straight
SW_NAMES = {50: "straight", 55: "a touch of swing", 60: "light swing", 66: "close to a triplet feel", 75: "hard swing"}
TABLE_BPM = 120                             # the timing table's tempo: a 16th lasts 125 ms
EX_BPM = 100                                # the worked example's tempo
EX_BARS = 8
LEN_BPMS = (90, 100, 110, 120)
LEN_BARS = (4, 8, 16)
LEN_EXPECT = [10.7, 21.3, 42.7, 9.6, 19.2, 38.4, 8.7, 17.5, 34.9, 8.0, 16.0, 32.0]      # row by row: 90, 100, 110, 120 BPM


def step_count(i):
    """The count of grid step i (0-based): 1 e & a for beat 1, then 2 e & a, and so on, as printed on every card."""
    return str(i // 4 + 1) if i % 4 == 0 else STEP_LABELS[i % 4]


def step_count_long(n):
    """Count of grid step n (1-based) written for a sentence: '1', '2 e', '3 &', '4 a'."""
    i = n - 1
    return str(i // 4 + 1) if i % 4 == 0 else f"{i // 4 + 1} {STEP_LABELS[i % 4]}"


def sixteenth_ms(bpm):
    return 15000 / bpm                      # 60000 ms per minute / bpm = one beat; a sixteenth is a quarter of it


def beat_ms(bpm):
    return 60000 / bpm


def bar_s(bpm):
    return 240 / bpm                        # seconds in one bar of 4/4


def length_s(bars, bpm):
    return bars * 240 / bpm


def swung_start_ms(i, bpm, pct, kind=16):
    """Start (ms from the start of the bar) of grid step i (0-based). Swing delays the second note of each PAIR so that it begins pct percent
    of the way through the pair: kind 16 = pairs of sixteenths (steps 2, 4, 6 ... 16 move), kind 8 = pairs of eighths (steps 3, 7, 11, 15 move)."""
    s = sixteenth_ms(bpm)
    if kind == 16:
        return (i - 1) * s + pct / 100 * 2 * s if i % 2 == 1 else i * s
    return (i - 2) * s + pct / 100 * 4 * s if i % 4 == 2 else i * s


def moves16(n):
    return n % 2 == 0                       # 1-based grid steps 2, 4, 6 ... 16 (the "e" and the "a")


def moves8(n):
    return n % 4 == 3                       # 1-based grid steps 3, 7, 11, 15 (the "&")


def fmt(x):
    x = round(x + 1e-9, 1)
    return f"{x:.0f}" if x == int(x) else f"{x:.1f}"


def mmss(t):
    t = int(round(t))
    return f"{t // 60}:{t % 60:02d}"


# ================================================================ the step-grid pattern cards (grid steps are 1-based, 1 to 16)
CARDS = [
    dict(key="bells_q", part="Sleigh bells", name="Quarter jingle", steps=[1, 5, 9, 13],
         feel="One jingle on every beat. It keeps time and leaves room for everything else.",),
    dict(key="bells_g", part="Sleigh bells", name="Gallop", steps=[1, 3, 4, 5, 7, 8, 9, 11, 12, 13, 15, 16],
         feel="A long-short-short rhythm in every beat: an eighth note, then two sixteenths. It sounds like a trotting horse.",),
    dict(key="shaker", part="Shaker", name="Sixteenth shake", steps=list(range(1, 17)),
         feel="A shake on every grid step, so a 16th-note swing moves half of them. It makes swing easy to hear.",),
    dict(key="tamb", part="Tambourine", name="Backbeat shake", steps=[5, 8, 13, 16],
         feel="A shake on beats 2 and 4, each followed by the “a” just before the next beat.",),
    dict(key="wood", part="Wood block", name="Offbeat tick", steps=[3, 7, 11, 15],
         feel="A dry tick on the “&” of every beat. A 16th-note swing leaves it alone, but an 8th-note swing moves it.",),
    dict(key="kick", part="Kick", name="Push", steps=[1, 6, 9, 14],
         feel="The kick lands on beats 1 and 3, then pushes on the “e” of 2 and the “e” of 4.",),
    dict(key="snare", part="Snare", name="Backbeat", steps=[5, 13],
         feel="The snare answers the kick on beats 2 and 4. Many grooves are built around this one pattern.",),
    dict(key="hat", part="Hi-hat", name="Steady eighths", steps=[1, 3, 5, 7, 9, 11, 13, 15],
         feel="A hat on every eighth note: the beat and the “&”. An 8th-note swing moves every second hit.",),
]
CARD_PAGES = {"grid1": ["bells_q", "bells_g", "shaker", "tamb"], "grid2": ["wood", "kick", "snare", "hat"]}


def card(key):
    return next(c for c in CARDS if c["key"] == key)


def card_moves(c, kind):
    return [n for n in c["steps"] if (moves16(n) if kind == 16 else moves8(n))]


def list_text(ns):
    if list(ns) == list(range(1, 17)):
        return "all 16"
    return ", ".join(str(n) for n in ns) if ns else "none"


def counts_text(c):
    if c["steps"] == list(range(1, 17)):
        return "every step, 1 e & a in each beat"
    return " · ".join(step_count_long(n) for n in c["steps"])


# the example groove (groove B of the worked example): one pattern per layer, in the order the drawings use
LAYER_ORDER = [("Sleigh bells", "bells_g"), ("Shaker", "shaker"), ("Tambourine", "tamb"), ("Wood block", "wood"), ("Kick", "kick"),
               ("Snare", "snare"), ("Hi-hat", "hat")]

# ================================================================ the project text (original; students read these pages)
OVERVIEW = ("Program a holiday percussion groove with no melody. In Logic Pro, build a Drum Machine Designer kit of sleigh bells, shaker, "
            "tambourine, wood block, kick, snare and hi-hat. Use the Step Sequencer to program a 4-bar groove on a 16-step grid, one layer "
            "at a time. Then copy it, add swing and compare the straight feel with the swung feel by ear and by the numbers: at 120 BPM "
            "a 16th note lasts 125 milliseconds, and a swung one lands later. Grow it into an 8-bar groove with a variation and a fill. "
            "Your groove runs at 90 to 120 BPM, and nobody needs to play an instrument or read music.")
GOALS = ["Build a Drum Machine Designer kit with at least five percussion layers, such as sleigh bells, shaker, tambourine, wood block, kick, snare and hi-hat",
         "Program a 4-bar groove in the Step Sequencer on a 16-step grid, with four steps to each beat",
         "Compare straight and swing feel, and explain swing in percent and in milliseconds",
         "Plan an 8-bar groove in bars and seconds, and prove its length with bars × 240 ÷ BPM"]
VOCAB = [("16-step grid", "One bar of 4/4 split into sixteen equal steps, four to each beat, counted 1 e & a 2 e & a 3 e & a 4 e & a"),
         ("Swing", "A feel in which the second note of each pair is played late, so the pair is long then short instead of even; its amount is given in percent"),
         ("Layer", "One percussion part of a groove, such as the shaker or the kick, programmed on its own pad and its own row of the grid"),
         ("Groove", "The pattern and feel of a rhythm that makes people want to move, built from layers that fit together")]
REQS = ["Build a Drum Machine Designer kit with at least 5 of the 7 layers (sleigh bells, shaker, tambourine, wood block, kick, snare, hi-hat) and name every pad (page @PLAN)",
        "Program a 4-bar straight groove on the 16-step grid, using at least 3 of the pattern cards or patterns of your own (pages @GRID1–@GRID2)",
        "Set a tempo from 90 to 120 BPM in 4/4 and write it on My groove plan (page @PLAN)",
        "Make a swung copy of your groove, try 50, 60 and 66 percent, and compare the feels on the listening worksheet (pages @SWING and @LISTEN)",
        "Grow the groove into 8 bars: bars 1 to 4 are your groove, bars 5 to 8 a variation with a fill in bar 8",
        "Balance the layers with volume, Channel EQ and a Compressor, so the bells and shaker do not cover the kick and snare",
        "Show the length arithmetic for your 8 bars on the Layer map (page @LAYERS), then reflect (page @REFLECT)"]
FILE_NAME = "“Your Name – Sleigh Bell Groove”"
STEP_NAMES = ["Plan", "Build the kit", "Program it straight", "Swing it", "Grow to 8 bars", "Mix and bounce", "Present &amp; get feedback"]
STEPS = ["<b>Plan</b> — Choose a tempo from 90 to 120 BPM and at least five layers, and fill in My groove plan (page @PLAN)",
         "<b>Build the kit</b> — Make a Drum Machine Designer track, give each pad a sound and name the pads (Logic quick reference: page @LOGICREF)",
         "<b>Program it straight</b> — Open the Step Sequencer and program a 4-bar groove from the cards (pages @GRID1–@GRID2), one layer at a time",
         "<b>Swing it</b> — Copy the groove, turn on swing and try 50, 60 and 66 percent (page @SWING), then fill in the listening worksheet (page @LISTEN)",
         "<b>Grow to 8 bars</b> — Make bars 5 to 8 a variation with a fill in bar 8, then fill in the Layer map and the length arithmetic (page @LAYERS)",
         "<b>Mix and bounce</b> — Balance with volume, Channel EQ and a Compressor, then bounce the 4-bar straight groove and the final 8-bar groove, named as on the checklist",
         "<b>Present &amp; get feedback</b> — Write three questions you want classmates to answer about your groove. Play the straight and the swung "
         "version, say which hits swing moved, and answer at least 2 of each classmate’s questions. Then reflect (page @REFLECT)."]
TIPS = ["Program one layer at a time and listen to it with the kick before you add the next one.",
        "Bells and shakers are bright and carry far: turn them down until the kick and snare are clear.",
        "Small amounts of swing, about 55 to 66 percent, are the most useful. Much more than that starts to sound like a different rhythm.",
        "Save a new version of your project before each big experiment, so you can always go back."]
CHECK = ["Bounced .mp3 or .wav files handed in: the 4-bar straight groove and the final 8-bar groove",
         "Zipped .logicx project file handed in",
         f"Files named correctly: {FILE_NAME}",
         "My groove plan, Layer map and listening worksheet handed in",
         "Rubric self-score done (page @RUBRIC)",
         "I can point to the grid steps that swing moves"]
RUBRIC_NOTE = "Each category is scored 1–5. Score yourself first; the final grade is the average of your score and your teacher’s."
LEVELS = [1, 2, 3, 4, 5]
RUBRIC = [
    ("Grid & Patterns", ["Few or no patterns are programmed; the grid is not used", "Fewer than 3 layers, or hits that do not sit on the beat",
                         "At least 3 layers programmed on the 16-step grid, mostly on the beat",
                         "At least 5 layers with clear jobs: a steady pulse, a backbeat and offbeat hits",
                         "Layers that interlock: each part has its own steps and the groove sounds finished"]),
    ("Sounds & Mix", ["One sound only, or the layers cannot be told apart", "Sounds chosen, but the bells or shaker cover the kick and snare",
                      "Every layer can be heard, with some balance problems",
                      "Balanced with volume and Channel EQ; the kick and snare stay clear",
                      "Balanced and shaped on purpose, with a Compressor and velocities that add life"]),
    ("Straight vs Swing", ["No swung version", "A swung version, but no comparison or an incorrect one",
                           "Swung copy made; the listening worksheet describes both feels",
                           "Swing tried at 50, 60 and 66 percent; says which grid steps move and why",
                           "Explains swing in percent and milliseconds at the project tempo, and chooses a feel with reasons"]),
    ("Form & Length", ["No clear length; the groove is not 4 or 8 bars", "4 bars only, with little change, or the length is not measured",
                       "4 bars plus a variation; length measured", "8 bars: groove, variation and a fill in bar 8, with the arithmetic shown",
                       "A form that builds: layers enter and leave; the arithmetic is exact"]),
    ("Plan & Reflection", ["Plans, presentation or reflection missing", "Thin plan; little to say about choices",
                           "Plan and reflection complete, with basic detail", "Clear plan; thoughtful reflection and good answers to questions",
                           "Insightful reflection and a polished, confident presentation"]),
]
RUBRIC_TOTAL = 25
RUBRIC_SHORT = [ds[4] for _, ds in RUBRIC]
RUBRIC_SLIDE_LINE = "Scored 1–5 · final grade = average of your score and mine, out of 25"
RUBRIC_ROW_PITCH = 0.86
RUBRIC_LINE_Y = 6.3

TN_REINFORCES = ("Teaches how a groove is built from simple parts. Students learn that a rhythm is a stack of layers on a grid, that feel "
                 "comes from tiny timing differences measured in milliseconds, and they practice programming a 16-step pattern, comparing straight "
                 "with swing, and doing the arithmetic of bars, tempo and seconds in Logic Pro’s Step Sequencer.")
STRUGGLES = ["The hits are in the wrong place: check which row is which pad and count the steps against the card, 1 e & a for each beat "
             "(pages @GRID1–@GRID2). Remember that four steps make one beat and sixteen make one bar.",
             "Swing seems to do nothing: the layers on the beat do not move. A 16th-note swing moves only the “e” and “a” hits, so use the "
             "shaker or a 16th-note hat to hear it (page @SWING).",
             "The groove sounds crowded: turn the bells and shaker down, give each layer its own steps and use the Channel EQ to cut the low "
             "end the high layers do not need (page @LOGICREF).",
             "The length is off: use bars × 240 ÷ BPM and the length helper (page @LAYERS), then set the end of the project at the right bar."]
VAR_EASY = ("Use three layers only (sleigh bells, kick and snare), keep one 4-bar groove for all 8 bars, and compare straight with one swing "
            "setting, 60 percent.")
VAR_HARD = ("Program a second groove with 8th-note swing instead of 16th-note swing (set the Step Sequencer’s step rate to 1/8 if your version "
            "allows it) and work out in milliseconds how far the “&” moves. Or add velocity changes and a second fill in bar 4.")
RESOURCES = [("The step-grid cards (pages @GRID1–@GRID2)",
              "Hand out both pages. Every card lists its hits, their counts and the hits that swing moves, so no one needs to read notation."),
             ("Straight vs swing: the timing table (page @SWING)",
              "Percent to milliseconds at 120 BPM, a pair diagram and all 16 steps straight and swung. Students check what they hear against it."),
             ("Listening and compare worksheet (page @LISTEN)",
              "Students describe straight and swung feel in their own words. Nothing is played from this kit: they listen to their own bounces."),
             ("Worked example (pages @EXAMPLE–@EXAMPLE2)",
              "An invented 8-bar groove at 100 BPM, 19.2 seconds, planned on paper. Use it as a model, not a template.")]
TN_NOTE = ("A listening day pairs well with this project: play the finished grooves without naming the tempo and let the class say which are straight and "
           "which are swung. If you want a feel reference, name a carol your students know and tap its tempo; the kit prints none.")
GRADING = ["The rubric: five categories, each scored 1–5, /25 (page @RUBRIC). Students score themselves first; the final grade is the "
           "average of their score and yours.",
           "Grid & Patterns (rubric row 1): open the Step Sequencer and compare the hits with the cards or with the student’s My groove plan (pages @GRID1–@GRID2).",
           "Sounds & Mix (rubric row 2): listen to the bounce. Can you hear the kick and snare under the bells and shaker?",
           "Straight vs Swing (rubric row 3): read the listening worksheet (page @LISTEN) and ask which grid steps swing moves; the answer is on page @SWING.",
           "Form & Length (rubric row 4): compare the project with the Layer map (page @LAYERS) and check the arithmetic: bars × 240 ÷ tempo.",
           "Plan & Reflection (rubric row 5): My groove plan (page @PLAN), the feedback questions and the Reflection page (page @REFLECT) are the evidence."]
PACING = [
    {"n": 1, "owner": "Hear the difference, build the kit and program the straight groove.",
     "do": "Slides 1–6: the think-and-share, what the project is, the three classes, the 16-step grid and building the kit. Hand out the project sheet, the cards "
           "and My groove plan. Check that every student has a tempo and a Drum Machine Designer track with at least three pads before they leave.",
     "slides": (1, 6), "pages": ["grid1", "grid2", "plan", "proj1", "proj2", "proj3", "vocab"],
     "deck": "Straight or swung? · the 16-step grid · build the kit"},
    {"n": 2, "owner": "Finish the straight groove, then swing it and compare.",
     "do": "Slides 7–9: the seven layers, the pair diagram and where swing lives in Logic. Finish the straight groove, adding the remaining layers. Demonstrate swing at 50, 60 and 66 "
           "percent on the projector, then work time. Walk the room with one question: which hits did swing move?",
     "slides": (7, 9), "pages": ["swing", "listen"], "deck": "Seven layers · swing in milliseconds · swing in Logic"},
    {"n": 3, "owner": "Grow to 8 bars, mix, bounce, present and reflect.",
     "do": "Slides 10–14: the worked example, what to turn in, the rubric and presentation day. Hand out the Layer map. Students extend to 8 bars, "
           "mix, bounce, name their files and write three feedback questions, then present.",
     "slides": (10, 14), "pages": ["layers", "rubric", "present", "reflect"], "deck": "8 bars, 19.2 seconds · checklist · rubric · presentations"},
]
PACING_EXTRA = (
    '<div class="cols" style="margin-top:4pt;gap:14pt"><div class="box acc-b"><span class="k">The one thing to do on Class 1</span>'
    '<p style="margin:0;font-size:10.6pt">Make sure every student leaves with a tempo from 90 to 120 BPM, a Drum Machine Designer track with '
    'sounds on at least three pads and a first layer programmed in the Step Sequencer. If the tempo is only a guess, tap a steady beat for ten seconds and count the taps.</p></div>'
    '<div class="box"><span class="k">With two or four periods</span><p style="margin:0;font-size:10.6pt"><b>Two classes:</b> Class 1 is the kit and the straight '
    'groove; Class 2 is swing, 8 bars, mixing, bounce and short presentations. <b>Four classes:</b> keep Class 1 and Class 2, then spend Class 3 on 8 bars and the mix '
    'and Class 4 on bouncing, presentations and reflection.</p></div></div>')
PACING_SIZE = 10.8


SONG_NOTE = ("No audio, recordings, lyrics, artists or albums are named or included, and no melody or song is notated. Students make every "
             "sound themselves, from the drum kits, samples and plug-ins in Logic.")
CREDITS = ["The step-grid pattern cards, the swing timing table, the pair diagram, the worked example, the listening worksheet and all "
           "step-grid, pair and arrangement drawings: original work, Hudson Beat. No melodies, lyrics, recordings or published editions are included.",
           "The cover illustration was made with digital and AI tools. No audio, video, album art, screenshots, presets, templates, links or "
           "chart data from other sources are included. No student work is included."]
LOGIC_INTRO = ("Where to find the tools a Sleigh Bell Groove is likely to use. Demonstrate what your class needs on Classes 1 and 2 and then "
               "let students work. Names are from current Logic Pro versions; labels move between versions, so check yours.")
LOGIC_REF = [("New project and kit track", "File › New…, then make a Software Instrument track. Click its instrument slot and choose Drum Machine Designer, "
              "or load a drum kit from the Library (a library kit is a Drum Machine Designer with a sound on each pad). Name the track Sleigh Kit. "
              "Set the tempo in the control bar (90 to 120 BPM) and keep 4/4."),
             ("Give each pad a sound", "Each pad in Drum Machine Designer holds its own sound. Drag an audio file onto a pad, or open a pad’s Quick Sampler "
              "to import a sound or record your own, for example a ring of jingle bells, keys or a shaker close to the Mac’s microphone. A library kit can supply the "
              "kick, snare and hat. Name the pads Bells, Shaker, Tambourine, Wood Block, Kick, Snare and Hat so your Layer map matches (page " + str(pg("layers")) + ")."),
             ("Open the Step Sequencer", "With the Drum Machine Designer track selected, open the Step Sequencer (look in the editors area at the bottom of the "
              "window; the exact button differs by version). Each row is one pad. Click a step to switch it on and click it again to switch it off."),
             ("Pattern length and rate", "Set the pattern to 16 steps and the step rate to 1/16, so every step is a sixteenth note: four steps make one beat and "
              "sixteen make one bar of 4/4, as on the cards (pages " + str(pg("grid1")) + "–" + str(pg("grid2")) + "). If your version offers a different rate, "
              "such as 1/8, one step is an eighth note and the grid changes with it."),
             ("Velocity and accents", "If your Step Sequencer shows a velocity lane under the steps, draw softer hits for the in-between steps and louder ones on the "
              "beats. Bells and shakers sound best when the hits are not all the same strength."),
             ("Swing", "Look for a Swing control in the Step Sequencer’s pattern settings, if your version shows one. Other places, if your version has them: the "
              "Q-Swing setting in a MIDI region’s Quantize settings, and a swing or feel control on a Drummer or percussion player. Scales differ: on most "
              "tools 50 percent is straight, but some start at 0. Find the setting that sounds even first, call it straight, and use the table on page "
              + str(pg("swing")) + " to check what you hear."),
             ("Loop, copy and extend", "Press C to turn Cycle on, so the 4 or 8 bars repeat while you work. Copy the 4-bar region to bar 5 (for example, "
              "Option-drag it), then edit the copy to make the variation and the fill in bar 8."),
             ("Mix: volume, EQ and Compressor", "Press X for the Mixer. Put a Channel EQ on the track and cut the low end the bells and shaker do not need; "
              "Drum Machine Designer can also show a separate mixer channel for each pad if your version offers it. Add a Compressor to the kick and snare "
              "or to the whole kit and lower its threshold until it just tames the loudest hits."),
             ("Automation, mixing and bounce", "Press A to show automation, pick a parameter such as volume, and draw points. Then File › Bounce › Project or "
              "Section (Command-B), MP3 or WAV. In Finder, Control-click the .logicx and choose Compress.")]
PRESENT_CHECK = [f"Files named {FILE_NAME}; the .mp3 or .wav files and the zipped .logicx handed in",
                 "Reflection page done (page @REFLECT)", "Three questions for classmates written",
                 "Rubric self-score done (page @RUBRIC)"]
VOCAB_PROMPT = "Where it shows up in my groove:"
TN1_EXTRA = (
    '<div class="box acc-b" style="margin-top:4pt"><span class="k">Where this kit helps with each struggle</span><ul style="margin:0">'
    '<li style="font-size:12pt;margin-bottom:3pt">Hits in the wrong place: the pattern cards list every hit with its count (pages @GRID1–@GRID2), and the Logic quick reference (page @LOGICREF) shows the grid.</li>'
    '<li style="font-size:12pt;margin-bottom:3pt">Swing that seems to do nothing: the timing table and the pair diagram (page @SWING) show which steps move and by how many milliseconds.</li>'
    '<li style="font-size:12pt;margin-bottom:3pt">A crowded mix: the Layer map (page @LAYERS) shows when each layer enters, and My groove plan (page @PLAN) gives each one a job.</li>'
    '<li style="font-size:12pt;margin-bottom:0">A length that is off: the length helper (page @LAYERS) and the worked example (pages @EXAMPLE–@EXAMPLE2).</li></ul></div>')
TN1_SIZE = 12.4
PROJ_SIZE = 12.0
VOCAB_GAP = 22
LOGIC_SIZE = 9.9
PROJ1_EXTRA = ""
RUBRIC_EXTRA = ""

# ================================================================ the worked example: an invented 8-bar groove at 100 BPM
EX_BAR_S = bar_s(EX_BPM)                    # 2.4 s
EX_SECTIONS = [("Groove A", 1, 4), ("Groove B", 5, 8)]
EX_LAYERS = [("Sleigh bells", [(1, 8)], "gallop from bar 5 (quarter jingle before it)"), ("Shaker", [(2, 8)], "sixteenth shake from bar 2"),
             ("Tambourine", [(5, 8)], "backbeat shake in groove B"), ("Wood block", [(5, 8)], "offbeat tick in groove B"),
             ("Kick", [(1, 8)], "the push pattern all the way through"), ("Snare", [(3, 8)], "backbeat from bar 3"),
             ("Hi-hat", [(1, 8)], "steady eighths all the way through")]
EX_FILL_BAR = 8
EX_SWING = 60
EX_WEAK = "I will make a holiday drum beat with bells and swing."
EX_STRONG = ("My groove is 8 bars at 100 BPM in 4/4 = 19.2 seconds. Bars 1 to 4 are groove A: bells, a kick that pushes on the “e” of 2 and 4, a "
             "backbeat snare from bar 3 and steady hi-hat eighths, with the shaker joining in bar 2. Bars 5 to 8 are groove B: the bells gallop and "
             "the tambourine and wood block join, with a snare fill in bar 8. The whole groove has 60 percent swing, so each swung 16th lands "
             "180 ms into its pair instead of 150 ms.")
EX_QUESTIONS = ["Which layer did you hear first, and what did it play?",
                "Could you hear the swing? Which layers made it clear?",
                "Where did the groove change, and what caused the change?"]
EX_MOMENTS = [(2, "the shaker joins: the first sixteenth-note layer"), (3, "the snare enters on the backbeat"),
              (5, "groove B: the tambourine and wood block join and the bells gallop"), (8, "the snare fill: grid steps 13 to 16 of the last bar")]
EX_FILL_STEPS = [13, 14, 15, 16]


def ex_density(bar):
    return sum(1 for _n, spans, _d in EX_LAYERS if any(a <= bar <= b for a, b in spans))


EX_DENS = [ex_density(b) for b in range(1, EX_BARS + 1)]


# ================================================================ drawings (all in code, labels logged for the fit check)
def padded(body, W, H, M=10):
    """Wrap a drawing's body with M units of clear padding on all four sides (wider than the thickest outer stroke), so no edge pixel is ever inked."""
    return f'<g transform="translate({M},{M})">{body}</g>', W + 2 * M, H + 2 * M


def grid16_body(name, lanes, cw=44, ch=44, gut=0, ls=22, blank=False, nums=True, counts=True, legend=False, hl=True, fs_n=18, fs_c=26):
    """A 16-step grid for one bar: step numbers 1-16, the count 1 e & a 2 e & a 3 e & a 4 e & a, then one row per layer.
    lanes = [(label, [1-based steps])]. A hit on a step that a 16th-note swing moves (2, 4, 6 ... 16) is a blue circle; every other hit
    is a black square, so the difference survives black-and-white printing. Beat columns are shaded."""
    out = []
    W = gut + NSTEPS * cw
    y = 0
    if nums:
        for i in range(NSTEPS):
            out.append(D.t_(gut + (i + .5) * cw, y + 20, str(i + 1), fs_n, 500, fill_="#555"))
            D.lab(f"{name} numbers", str(i + 1), fs_n, cw - 8)
        y += 28
    if counts:
        for i in range(NSTEPS):
            beat = i % 4 == 0
            lbl = step_count(i)
            out.append(D.t_(gut + (i + .5) * cw, y + 28, lbl, fs_c if beat else fs_c - 4, 700 if beat else 500, fill_="#000" if beat else ACCENT))
            D.lab(f"{name} counts", lbl, fs_c, cw - 8)
        y += 38
    y0 = y + 4
    gh = len(lanes) * ch
    pad = 8
    for r, (label, steps) in enumerate(lanes):
        yy = y0 + r * ch
        if gut:
            out.append(D.t_(gut - 12, yy + ch / 2 + ls * .35, label, ls, 500, anchor="end"))
            D.lab(f"{name} lanes", label, ls, gut - 20)
        for i in range(NSTEPS):
            x = gut + i * cw
            out.append(f'<rect x="{x:.1f}" y="{yy:.1f}" width="{cw}" height="{ch}" fill="{"#e4e4e4" if i % 4 == 0 else "#fff"}" stroke="#000" '
                       f'stroke-width="{1.3 if i % 4 == 0 else .6}"/>')
        if blank:
            continue
        for n in steps:
            i = n - 1
            x = gut + i * cw
            if hl and moves16(n):
                out.append(f'<circle cx="{x + cw / 2:.1f}" cy="{yy + ch / 2:.1f}" r="{min(cw, ch) / 2 - pad:.1f}" fill="{ACCENT}"/>')
            else:
                out.append(f'<rect x="{x + pad:.1f}" y="{yy + pad:.1f}" width="{cw - 2 * pad:.1f}" height="{ch - 2 * pad:.1f}" rx="3" fill="#000"/>')
    for b in range(BEATS + 1):
        x = gut + b * 4 * cw
        out.append(f'<line x1="{x:.1f}" y1="{y0 - 2}" x2="{x:.1f}" y2="{y0 + gh + 2}" stroke="#000" stroke-width="2.6"/>')
    out.append(f'<rect x="{gut}" y="{y0}" width="{NSTEPS * cw}" height="{gh}" fill="none" stroke="#000" stroke-width="2.4"/>')
    H = y0 + gh + 4
    if legend:
        sz = 24
        ly = H + 30
        out.append(f'<rect x="{gut + 2}" y="{ly - sz + 4}" width="{sz}" height="{sz}" rx="3" fill="#000"/>')
        t1 = "black square: stays put under a 16th-note swing"
        out.append(D.t_(gut + sz + 16, ly, t1, 22, 500, anchor="start"))
        D.lab(f"{name} legend", t1, 22, NSTEPS * cw - sz - 24)
        ly += 36
        out.append(f'<circle cx="{gut + 2 + sz / 2}" cy="{ly - sz / 2 + 4}" r="{sz / 2}" fill="{ACCENT}"/>')
        t2 = "blue circle: moves later under a 16th-note swing"
        out.append(D.t_(gut + sz + 16, ly, t2, 22, 500, anchor="start"))
        D.lab(f"{name} legend", t2, 22, NSTEPS * cw - sz - 24)
        H = ly + 8
    return "".join(out), W, H


def padded_grid(name, lanes, **kw):
    b, W, H = grid16_body(name, lanes, **kw)
    return padded(b, W, H, 10)


def card_body(c, name=None):
    return padded_grid(name or f"card {c['key']}", [(c["part"], c["steps"])], cw=44, ch=44)


def blank_body(nlanes=2, name="blank grid"):
    return padded_grid(name, [(f"Layer {i + 1}", []) for i in range(nlanes)], cw=44, ch=44, gut=110, ls=20, blank=True)


def layers_body(name="layers pic", cw=44, ch=44, gut=190, legend=True):
    lanes = [(label, card(k)["steps"]) for label, k in LAYER_ORDER]
    return padded_grid(name, lanes, cw=cw, ch=ch, gut=gut, ls=22, legend=legend)


def swing_body(W=1500, name="swing pic", bpm=TABLE_BPM):
    """The pair diagram: one pair of sixteenth notes (250 ms at 120 BPM) split at the swing percent. The second note starts where the split is."""
    pair = 2 * sixteenth_ms(bpm)
    lx, bw = 330, 760
    x0 = lx
    sc = bw / pair
    out = []
    out.append(D.t_(x0, 30, "0 ms", 24, 500, anchor="start"))
    D.lab(name + " ruler", "0 ms", 24, 120)
    t_end = f"{fmt(pair)} ms: the next pair starts"
    out.append(D.t_(x0 + bw, 30, t_end, 24, 500, anchor="end"))
    D.lab(name + " ruler", t_end, 24, 420)
    rowh = 80
    top = 52
    for r, pct in enumerate(SW_PCTS):
        y = top + r * rowh
        off = pct / 100 * pair
        late = off - pair / 2
        out.append(D.t_(lx - 24, y + 36, f"{pct}%", 40, 700, anchor="end", fill_=ACCENT if pct != 50 else "#000"))
        D.lab(name + " pct", f"{pct}%", 40, 130)
        sub = SW_NAMES[pct]
        out.append(D.t_(lx - 24, y + 60, sub, 21, 500, anchor="end"))
        D.lab(name + " names", sub, 21, lx - 40)
        g = 3
        out.append(f'<rect x="{x0}" y="{y}" width="{off * sc - g:.1f}" height="56" rx="8" fill="#ececec" stroke="#000" stroke-width="3"/>')
        out.append(f'<rect x="{x0 + off * sc + g:.1f}" y="{y}" width="{bw - off * sc - g:.1f}" height="56" rx="8" fill="{ACCENT}" stroke="#000" stroke-width="3"/>')
        t1 = f"1st: {fmt(off)} ms"
        t2 = f"2nd: {fmt(pair - off)} ms"
        out.append(D.t_(x0 + (off * sc - g) / 2, y + 37, t1, 26, 700))
        D.lab(name + " first", t1, 26, off * sc - 16)
        out.append(D.t_(x0 + off * sc + g + (bw - off * sc - g) / 2, y + 37, t2, 26, 700, fill_="#fff"))
        D.lab(name + " second", t2, 26, bw - off * sc - g - 14)
        t3 = f"2nd note starts at {fmt(off)} ms"
        out.append(D.t_(x0 + bw + 30, y + 24, t3, 26, 700, anchor="start"))
        D.lab(name + " start", t3, 26, W - (x0 + bw + 30) - 8)
        t4 = "even, no delay" if pct == 50 else f"{fmt(late)} ms later than straight"
        out.append(D.t_(x0 + bw + 30, y + 50, t4, 22, 500, anchor="start"))
        D.lab(name + " late", t4, 22, W - (x0 + bw + 30) - 8)
    cap = f"One pair of sixteenth notes at {bpm} BPM: the swing percent is where the second note starts inside the pair"
    out.append(D.t_(W / 2, top + len(SW_PCTS) * rowh + 22, cap, 24, 500))
    D.lab(name + " cap", cap, 24, W - 20)
    return padded("".join(out), W, top + len(SW_PCTS) * rowh + 36, 12)


def map_body(W=1600, name="map", fs=24, ts=20, lf=20, lh=32):
    """The worked example's whole 8-bar groove: two grooves, seven layers, a fill and the swing setting, with the seconds under it."""
    gx = 300
    pwid = W - gx - 16

    def X(bar):
        return gx + pwid * (bar - 1) / EX_BARS

    out = []
    sh = 54
    for nm, a, b in EX_SECTIONS:
        lbl = f"{nm.upper()} · BARS {a}–{b}"
        out.append(f'<rect x="{X(a) + 3:.1f}" y="2" width="{X(b + 1) - X(a) - 6:.1f}" height="{sh}" rx="8" fill="{"#000" if a == 1 else ACCENT}"/>')
        out.append(D.t_((X(a) + X(b + 1)) / 2, sh / 2 + fs * .3 - 1, lbl, fs - 2, 700, fill_="#fff"))
        D.lab(name + " sections", lbl, fs - 2, X(b + 1) - X(a) - 16)
    lg = 7
    y0 = sh + 14
    out.append(D.t_(gx - 14, y0 + 6, "LAYERS", fs - 6, 700, anchor="end", fill_=ACCENT))
    rows = [(nm, spans, "") for nm, spans, _d in EX_LAYERS] + [("Fill", [(EX_FILL_BAR, EX_FILL_BAR)], "FILL"), ("Swing", [(1, EX_BARS)], f"{EX_SWING}% SWING")]
    for i, (nm, spans, txt) in enumerate(rows):
        yy = y0 + 16 + i * (lh + lg)
        lbl = nm.upper()
        out.append(D.t_(gx - 14, yy + lh / 2 + lf * .35, lbl, lf, 700, anchor="end"))
        D.lab(name + " lanes", lbl, lf, gx - 24)
        out.append(f'<rect x="{gx}" y="{yy}" width="{pwid:.1f}" height="{lh}" fill="#fff" stroke="#000" stroke-width="1.2"/>')
        for a, b in spans:
            fillc = ACC_LIGHT if txt else "#bdbdbd"
            out.append(f'<rect x="{X(a) + 2:.1f}" y="{yy + 4}" width="{X(b + 1) - X(a) - 4:.1f}" height="{lh - 8}" rx="6" fill="{fillc}" stroke="#000" stroke-width="2"/>')
            if txt:
                out.append(D.t_((X(a) + X(b + 1)) / 2, yy + lh / 2 + lf * .33, txt, lf - 2, 700))
                D.lab(name + " lane text", txt, lf - 2, X(b + 1) - X(a) - 16)
    ty = y0 + 16 + len(rows) * (lh + lg) + 10
    for bar in range(1, EX_BARS + 2):
        t = (bar - 1) * EX_BAR_S
        lbl = f"{t:.1f} s"
        anc = "start" if bar == 1 else ("end" if bar == EX_BARS + 1 else "middle")
        xx = X(bar)
        out.append(f'<line x1="{xx:.1f}" y1="{ty - 6}" x2="{xx:.1f}" y2="{ty + 8}" stroke="#000" stroke-width="2"/>')
        out.append(D.t_(xx + (3 if bar == 1 else (-3 if bar == EX_BARS + 1 else 0)), ty + 8 + ts, lbl, ts, 500, anchor=anc))
        D.lab(name + " ticks", lbl, ts, 100)
        if bar <= EX_BARS:
            bl = f"bar {bar}"
            out.append(D.t_((X(bar) + X(bar + 1)) / 2, ty + 8 + ts * 2 + 8, bl, ts - 2, 500, fill_="#555"))
            D.lab(name + " bars", bl, ts - 2, pwid / EX_BARS - 16)
    cap = f"Bar 1 to bar {EX_BARS} at {EX_BPM} BPM: {EX_BARS} bars × {EX_BAR_S:g} seconds = {EX_BARS * EX_BAR_S:g} seconds"
    out.append(D.t_(gx + pwid / 2, ty + 8 + ts * 2 + 46, cap, ts + 4, 500))
    D.lab(name + " cap", cap, ts + 4, pwid)
    return padded("".join(out), W, ty + 8 + ts * 2 + 62, 14)


def hero_body():
    """The owner's pre-made art (art/hero.png, used whole). The viewBox only trims fully transparent margin: the art's own pixels
    (x 89-1326, y 265-1228 of 1400) stay at least 40 units inside it, which --check proves from the file."""
    return (f'<image href="../art/hero.png" x="{-HX}" y="{-HY}" width="1400" height="1400"/>', HW, HH)


HX, HY, HW, HH = 40, 215, 1330, 1060


DRAWINGS = {"hero": hero_body, "grid": lambda: padded_grid("grid pic", [("Kick", card("kick")["steps"]), ("Snare", card("snare")["steps"]),
                                                                       ("Hi-hat", card("hat")["steps"])], cw=48, ch=48, gut=130, ls=24, legend=True),
            "layers": lambda: layers_body("layers deck"), "swing": lambda: swing_body(1500, "swing deck"), "map": lambda: map_body(1600, "map pic")}
DRAWING_PX = {"hero": 1330, "grid": 2000, "layers": 2000, "swing": 2000, "map": 2000}
SIDE = {"grid": ["16 steps make one bar of 4/4", "Four steps make one beat", "Count each beat 1 e & a", "Blue circles are the hits a 16th swing moves"],
        "layers": ["Seven layers, one bar", "Each row is one pad", "Every hit sits on a step", "Which hits would an 8th swing move?"],
        "swing": ["50 percent is straight", "A higher percent means a later second note", "At 66 percent the pair is long then short", "Swing moves the second note only"],
        "map": ["An invented 8-bar groove", "Groove A, then groove B with a fill", "Three layers start, four more join", "Every bar lasts 2.4 seconds"]}
# extra drawings used on pages only, rendered alone on a transparent ground by --check as well
PAGE_DRAWINGS = {"card": lambda: card_body(card("kick"), "card kick"), "card-gallop": lambda: card_body(card("bells_g"), "card gallop"),
                 "blank": lambda: blank_body(2, "blank grid"), "swing-page": lambda: swing_body(1500, "swing page")}


def label_extras():
    for c in CARDS:
        card_body(c)
    blank_body(2, "blank grid")
    blank_body(3, "blank grid plan")
    layers_body("page layers", 40, 40, 170)
    swing_body(1500, "swing page")
    map_body(1500, "page map", 27, 23, 25, 40)


# ================================================================ intro deck: (class, kind, title, body, speaker notes)
SLIDES = [
    (1, "title", "Sleigh Bell Groove", "Straight or swung? Program the difference.",
     "Class 1, the first minute. No audio is included in this deck. Open with the idea: you will build a holiday percussion groove with no melody, "
     "in Logic Pro, from sleigh bells, a shaker, a tambourine, a wood block, a kick, a snare and a hi-hat. You will program it on a 16-step grid in the "
     "Step Sequencer, then add swing and compare the two feels by ear and by the numbers. Nobody needs to play an instrument or read music."),
    (1, "listen", "Can you hear the swing?", "Think, then share|Teacher: tap four even beats on the desk, then tap them long-short. No audio plays.|Which tapping was straight?|What changed between the two?|Which suits a ride through the snow, and which a march?",
     "Ask the three questions aloud and take a few answers. Nothing is played from a speaker: you tap on the desk, first evenly, then with a long-short "
     "lilt. Students will say bouncy, skippy, lazy, rolling or shuffly for the second. Write their words on the board; the project gives each word "
     "a number, because swing is just the second note of a pair arriving a little later. A familiar carol may be named as a tempo or feel reference; "
     "nothing is notated in this kit."),
    (1, "bullets", "What is Sleigh Bell Groove?", "Program percussion with no melody|Build a kit: bells, shaker, kick, snare, hat|Program 4 bars in the "
     "Step Sequencer|Swing it, compare, then grow to 8 bars",
     "The project in four lines. Every student builds a Drum Machine Designer kit of at least five layers and programs a 4-bar groove in the Step "
     "Sequencer on a 16-step grid. Then they copy it, add swing, and compare the two feels. Last, the groove grows to 8 bars with a variation and a "
     "fill. The groove runs at 90 to 120 BPM. There is no melody, so no one needs to read notation, and no audio ships: students make every sound."),
    (1, "days", "Three classes", "",
     "The shape of the project. Class 1: hook, the 16-step grid, the kit and the straight groove. Class 2: finish the straight groove, then swing it "
     "and compare the feels on the listening worksheet. Class 3: grow to 8 bars, mix, bounce, present and reflect. With two classes, merge Class 2 "
     "and 3; with four, add a day for the 8 bars and the mix. Hand out the project sheet, the cards and My groove plan now."),
    (1, "pic", "The 16-step grid", "grid",
     "Class 1. One bar of 4/4 is sixteen steps: four beats, four sixteenth notes in each. Count each beat 1 e & a, so the steps read 1 e & a 2 e & a 3 e & a "
     f"4 e & a. This is a kick, snare and hi-hat pattern. The black squares stay put when a 16th-note swing is on; the blue circles sit on the “e” and the "
     f"“a” and move later. At 120 BPM each step lasts 125 milliseconds. Students find the cards on pages {pg('grid1')} and {pg('grid2')} and fill in My "
     f"groove plan, page {pg('plan')}."),
    (1, "steps", "Build it in Logic", "Add a Drum Machine Designer track|Give each pad a sound; name the pads|Open the Step Sequencer: 16 steps, "
     "rate 1/16|Click in the hits for one layer at a time|Listen with the kick, then add the next layer",
     "Class 1. Demonstrate on the projector: make a Software Instrument track and choose Drum Machine Designer, drop or record a sound on each pad "
     "(Quick Sampler can import or record one), open the Step Sequencer, set 16 steps at a 1/16 rate, and click in the kick. Then add a layer at a time "
     f"and listen. Menu names and button places move between Logic versions; the quick reference on page {pg('logicref')} hedges where they do."),
    (2, "pic", "Seven layers, one bar", "layers",
     "Class 2. The same grid with seven layers: sleigh bells, shaker, tambourine, wood block, kick, snare and hi-hat. Each row is one pad in the Drum "
     "Machine Designer kit and each filled step is one hit. Ask the class which hits a 16th-note swing would move: the blue circles. Then ask which "
     "an 8th-note swing would move, the “&” hits on grid steps 3, 7, 11 and 15, which are the wood block, the bells, the shaker and the hat."),
    (2, "pic", "Swing: where the second note lands", "swing",
     "Class 2. Take one pair of sixteenth notes at 120 BPM: together they last 250 milliseconds. Straight, the second note starts at 125 ms. At 60 percent it "
     "starts at 150 ms, at 66 percent at 165 ms and at 75 percent at 187.5 ms. The first note gets longer and the second shorter, which is the long-short "
     f"lilt. Students check the full 16-step table on page {pg('swing')} against what they hear."),
    (2, "bullets", "Where swing lives in Logic", "Step Sequencer: look for its Swing control|Region Quantize: Q-Swing, if your version has it|"
     "Straight is the setting that sounds even|Test with 50, 60 and 66 percent",
     "Class 2. Swing can live in more than one place. The Step Sequencer has a Swing control in its pattern settings, if your version shows one. A MIDI "
     "region's Quantize settings can include Q-Swing, and Drummer or percussion players may have a swing or feel control, if your version has them. "
     "Scales differ between tools, so have students find the setting that sounds even, call it straight, and test 50, 60 and 66 percent."),
    (3, "pic", "An 8-bar groove in 19.2 seconds", "map",
     "Class 3. An invented groove described on paper; nothing here is audio. Eight bars at 100 BPM: one bar is 240 divided by 100, which is 2.4 seconds, so eight "
     "bars last 19.2 seconds. Groove A is bars 1 to 4, groove B is bars 5 to 8 with a fill in bar 8, and the whole groove has 60 percent swing. Three layers play from bar 1 and "
     f"four more join over the eight bars. Students plan their own on the Layer map, page {pg('layers')}, and show the arithmetic."),
    (3, "check", "What you turn in", "Bounced .mp3 or .wav: 4 bars straight, 8 bars final|Zipped .logicx project|Named: Your Name – Sleigh Bell Groove|"
     "My groove plan, Layer map, listening worksheet|Reflection page|Rubric self-score and three questions",
     "Class 3. The submission checklist, shortened to fit the slide. Show where students hand in. The file name is Your Name, then Sleigh Bell "
     "Groove. Check the length before students bounce: bars times 240 divided by the tempo, so 4 bars at 100 BPM is 9.6 seconds and 8 bars is 19.2."),
    (3, "rubric", "How it’s scored", "",
     "The rubric: five categories, each scored 1 to 5, for a total out of 25. Students score themselves first; the final grade is the average of their "
     "score and yours. The slide reads the 5 column of each category aloud. Hand out the rubric page so students can self-score before they present."),
    (3, "bullets", "Presentation day", "Play the straight groove, then the swung one|Say which hits swing moved and by how many ms|Your three "
     "questions for classmates|Answer at least 2 of each classmate’s questions",
     "Class 3, presentations. Each student plays the straight groove, then the swung one, and says which grid steps swing moved and about how many "
     "milliseconds later they land at their tempo. Students write three questions they want classmates to answer, and answer at least two of each "
     "classmate's. Ask the class to say which version is which before the presenter does."),
    (3, "closer", "One last thing…", "Layers on a grid.|Swing is a number.|Feel is timing.|Now press play.",
     "Close with the listening day: play the finished grooves without saying which is straight and let the class say. A feel that people name "
     "quickly is a swing that was clear. Ask a few students which layer made the swing easiest to hear. No audio is included in this resource; "
     "the sounds are the students' own."),
]
SHOTS1 = [("pacing", "Pacing guide", "3 class periods, slide by slide"), ("grid1", "Step-grid cards", "Bells, shaker, tambourine"),
          ("swing", "Straight vs swing", "Percent to milliseconds")]
SHOTS2 = [1, 3, 5, 7, 8, 10]
SHOTS3 = [("grid1", "Step-grid cards 1"), ("grid2", "Step-grid cards 2"), ("swing", "Straight vs swing"), ("listen", "Listening worksheet"),
          ("example", "Worked example"), ("plan", "My groove plan"), ("layers", "Layer map"), ("rubric", "Rubric")]
PREVIEW_PICKS = ["pacing", "grid1", "swing", "rubric"]

COVER_A = "Straight vs swing"
COVER_C = "Logic Pro · Drum Machine Designer · Step Sequencer"
PDF_COVER = dict(a=26, b=56, c=15, art=6.2)
SQ_COVER = dict(a=40, b=150, c=27, art=500, gap=22)
SQ_B_LINES = ["Sleigh Bell", "Groove"]
SQ_SUB = "3 class periods · percussion programming · intro slides"
SQ_HEADS = {1: ("Ready to teach Monday", 76, "Pacing, step-grid cards, swing table and the /25 rubric in one PDF", 28),
            2: ("Intro deck included", 76, f"{len(SLIDES)} editable slides (.pptx + PDF) with speaker notes on every slide", 28),
            3: ("Everything inside", 72, "Step-grid cards, swing table, worked example, plans and worksheets", 28)}
SQ_BANDS = {1: "Grid <em>·</em> layers <em>·</em> straight <em>·</em> swing <em>·</em> 8 bars",
            2: "Step grids <em>·</em> seven layers <em>·</em> swing in ms <em>·</em> example",
            3: f"{len(PLAN)} pages <em>·</em> US Letter PDF <em>·</em> no audio included"}


# ================================================================ small page helpers
CSS_SG = ("<style>table.sg { border-collapse: collapse; width: 100%; } table.sg td, table.sg th { border: 1pt solid #000; text-align: center; "
          "padding: 0; font-size: 8pt; } table.sg th { background: #000; color: #fff; font-family: Oswald; font-weight: 500; height: 14pt; } "
          "table.sg td.l { text-align: left; padding: 0 4pt; font-weight: 700; width: 1.2in; font-size: 9pt; } "
          "table.sg td.b { border-left: 2.2pt solid #000; } </style>")


def howto_page(n, wm=False):
    parts = [("Teacher pages", "howto", "example2", "How to use, overview, setup, pacing, teacher notes, Logic quick reference, worked example (2 pages)"),
             ("Student pages", "grid1", "reflect", "Step-grid cards (2 pages), the swing timing table, My groove plan, Layer map, listening worksheet, "
              "project sheet (3 pages), rubric, vocabulary, feedback planner, reflection page"),
             ("Intro deck (separate file)", None, None, f"{len(SLIDES)} slides, .pptx + PDF, speaker notes on every slide")]
    trs = "".join(f"<tr><td><b>{a}</b></td><td style='white-space:nowrap'>{('pages ' + str(D.IX(f)) + '–' + str(D.IX(l))) if f else 'deck'}</td>"
                  f"<td>{u}</td></tr>" for a, f, l, u in parts)
    inner = (f'<div class="cols"><div>'
             f'{D.H2("What this is", True)}'
             f'<p style="font-size:12pt;line-height:1.45">A {CLASSES}-class-period percussion project for high school music technology. Every '
             f'student builds a holiday percussion groove with no melody in Logic Pro: a Drum Machine Designer kit of sleigh bells, shaker, tambourine, wood block, kick, snare and hi-hat, '
             f'programmed in the Step Sequencer on a 16-step grid. They program 4 bars straight, add swing and compare the two feels by ear and by the '
             f'numbers, then grow the groove to 8 bars. Students plan it, build and mix it, present it and reflect on it. It is an original Hudson Beat project.</p>'
             f'{D.H2("Quick start")}<ol>'
             f'<li style="margin-bottom:5pt">Read the pacing guide (page {D.IX("pacing")}) and the teacher notes (pages {D.IX("tn1")}–{D.IX("tn2")}).</li>'
             f'<li style="margin-bottom:5pt">Look at the cards and the swing table (pages {D.IX("grid1")}–{D.IX("swing")}) and the setup (page {D.IX("setup")}).</li>'
             f'<li style="margin-bottom:5pt">Print the student pages (pages {D.IX("grid1")}–{D.IX("reflect")}), one set per student.</li>'
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
             f'<li><b>Pace:</b> Class 1 is the kit and the straight groove, Class 2 swing, Class 3 the 8 bars and the presentations (page {D.IX("pacing")}); the pacing page also shows two and four periods.</li>'
             f'<li><b>Feedback:</b> students write three questions and answer classmates’ on a class board or on paper.</li>'
             f'<li><b>Grading:</b> the rubric, /{RUBRIC_TOTAL}, the average of the student’s and your score (page {D.IX("rubric")}).</li></ul>'
             f'<div class="box" style="margin-top:6pt"><span class="k">In one sentence</span><p style="margin:0;font-size:12pt">Students learn that '
             f'a groove is layers on a 16-step grid, and that swing is the second note of each pair arriving a measurable moment late.</p></div>'
             f'<p class="small" style="margin-top:6pt">Logic Pro is a product of Apple Inc. This resource is not affiliated with Apple.</p>'
             f'</div></div>')
    return D.page("How to use this resource", "START HERE", "Teacher", inner, n, key="howto")


def overview_page(n, wm=False):
    inner = (f'<div class="cols"><div>'
             f'<div class="box inv" style="margin-bottom:6pt"><span class="k">The project in one line</span><p style="margin:0;font-size:12pt">'
             f'<b>{TITLE}</b> · Percussion · Logic Pro<br>Program a groove, then hear it straight and swung.</p></div>'
             f'{D.H2("What students make")}'
             f'<p style="font-size:13pt;line-height:1.5">One original percussion groove with no melody: 4 bars programmed straight, a swung copy, and a final 8-bar groove '
             f'with a variation and a fill. It uses at least five of seven layers (sleigh bells, shaker, tambourine, wood block, kick, snare and hi-hat) in a '
             f'Drum Machine Designer kit, programmed on a 16-step grid in the Step Sequencer at 90 to 120 BPM, and it is mixed with volume, Channel EQ and a Compressor. '
             f'Students hand in two bounced files and the zipped .logicx project, plus their plans and a reflection, then play both feels and take questions.</p>'
             f'{D.H2("What this project reinforces")}<p style="font-size:12.2pt;line-height:1.5">{TN_REINFORCES}</p>'
             f'{D.H2("Standards")}<p style="font-size:11.4pt">Supports the National Core Arts Standards for Music (Music Technology, high school): generating '
             f'and developing ideas (MU:Cr1.1, MU:Cr2.1), presenting work (MU:Pr6.1) and responding to it (MU:Re7.2).</p>'
             f'</div><div>'
             f'{D.H2("Goals", True)}<ul>' + "".join(f"<li style='font-size:12.4pt;line-height:1.5'>{g}</li>" for g in GOALS) + '</ul>'
             f'{D.H2("At a glance")}<table class="t" style="font-size:11.2pt">'
             f'<tr><td><b>Grades</b></td><td>{GRADES_TEXT}, music technology or music production</td></tr>'
             f'<tr><td><b>Length</b></td><td>{CLASSES} class periods (the pacing page also shows two and four): kit and straight groove, swing, 8 bars and presentations</td></tr>'
             f'<tr><td><b>Software</b></td><td>Logic Pro: Drum Machine Designer, Quick Sampler, Step Sequencer, Channel EQ, Compressor, bounce</td></tr>'
             f'<tr><td><b>You supply</b></td><td>Macs with Logic Pro, headphones, a place to hand in files and a class board or paper for feedback</td></tr>'
             f'<tr><td><b>Assessment</b></td><td>Rubric, 5 categories scored 1–5, /{RUBRIC_TOTAL}; final grade = average of the student’s and the '
             f'teacher’s score (page {D.IX("rubric")})</td></tr></table>'
             f'<div class="box" style="margin-top:6pt"><span class="k">Before they start</span><p style="margin:0;font-size:11.4pt">Students should know how '
             f'to open a project, add a software instrument and use the mixer in Logic. Nobody needs to read music: the cards name every '
             f'hit by its step and its count.</p></div>'
             f'</div></div>')
    return D.page("Project overview", "OVERVIEW", "Percussion project", inner, n, key="overview")


def setup_page(n, wm=False):
    inner = (f'<style>.sb p, .sb li {{ font-size: 11.6pt; line-height: 1.44; margin-bottom: 5pt; }}</style><div class="cols"><div class="big sb">'
             f'{D.H2("You need", True)}<ul>'
             f'<li><b>A Mac with Logic Pro</b> for each student, and <b>headphones</b>.</li>'
             f'<li><b>A place to hand in</b> the .mp3 or .wav files, the zipped .logicx and the reflection.</li>'
             f'<li><b>The step-grid cards and the swing table</b>, printed (pages {D.IX("grid1")}–{D.IX("swing")}), or shown on the projector.</li>'
             f'<li><b>Sounds for the pads:</b> a Logic drum kit from the Library, or sounds the students record themselves (jingle bells, keys, a shaker).</li>'
             f'<li><b>Printed student pages</b>, one set each (pages {D.IX("grid1")}–{D.IX("reflect")}).</li>'
             f'<li><b>A MIDI keyboard or pad controller</b> is optional: every hit can be clicked in with the mouse.</li></ul>'
             f'{D.H2("Before Class 1")}'
             + "".join(D.chk(c, 13, "font-size:11.6pt;margin-bottom:7pt") for c in [
                 f"Read the swing page (page {D.IX('swing')}) so you can answer ‘how late is late?’ in milliseconds.",
                 "Open Logic Pro on a student computer: can you make a Drum Machine Designer track, open its Step Sequencer and set 16 steps at a 1/16 rate?",
                 f"Find the swing setting in your version (see page {D.IX('logicref')}) and note which scale it uses.",
                 f"Read the worked example (pages {D.IX('example')}–{D.IX('example2')})."]) +
             f'</div><div class="big sb">'
             f'{D.H2("What to watch", True)}'
             f'<p style="font-size:11.4pt">Hits land on the wrong step, swing seems to do nothing, the bells and shaker cover the kick and snare, or the '
             f'groove is the wrong length. {TN_NOTE}</p>'
             f'<div class="box acc-b" style="margin-top:2pt"><span class="k">Ideas for the room</span><ul style="margin:0">'
             f'<li style="font-size:11.2pt">Ask while students work: which layer is that? Which grid steps are you using? Can you hear the swing yet?</li>'
             f'<li style="font-size:11.2pt">On Class 1, tap 90, 105 and 120 BPM on the desk and have students pick the tempo that feels right for a sleigh-bell groove.</li>'
             f'<li style="font-size:11.2pt">A student who is stuck can start from the shaker card, which has a hit on every step, then add the kick and snare.</li></ul></div>'
             f'{D.H2("Finding swing in your version")}'
             f'<div class="box"><span class="k">Check before Class 2</span><p style="margin:0;font-size:11pt;line-height:1.4">'
             f'Logic’s controls move between versions. Look for a Swing control in the Step Sequencer’s pattern settings, and for Q-Swing in a MIDI region’s '
             f'Quantize settings, if your version shows them. If a scale starts at 0 for straight, tell students to find the even setting and call it 50 percent.</p></div>'
             f'<div class="box" style="margin-top:6pt"><span class="k">Keep the volume moderate</span><p style="margin:0;font-size:11pt;line-height:1.4">'
             f'Bells, shakers and hats are bright and can be tiring in headphones. Tell students to start low and check the final mix at a normal level.</p></div>'
             f'</div></div>')
    return D.page("Setup and what to watch", "SETUP", "Teacher", inner, n, key="setup")


# ================================================================ the pattern-card pages
ICON_SQ = f'<svg width="11pt" height="11pt" viewBox="0 0 11 11" style="vertical-align:-1.5pt"><rect x="1" y="1" width="9" height="9" rx="1.5" fill="#000"/></svg>'
ICON_CI = f'<svg width="11pt" height="11pt" viewBox="0 0 11 11" style="vertical-align:-1.5pt"><circle cx="5.5" cy="5.5" r="4.6" fill="{ACCENT}"/></svg>'


def card_html(c, w="4.7in", mb=8, pad=6):
    m16, m8 = card_moves(c, 16), card_moves(c, 8)
    txt = (f'<p style="margin:0 0 2pt;font-size:9.2pt;line-height:1.26">{c["feel"]}</p>'
           f'<p style="margin:0 0 1pt;font-size:8.8pt;line-height:1.22"><b>Counts:</b> {counts_text(c)}</p>'
           f'<p style="margin:0 0 1pt;font-size:8.8pt;line-height:1.22"><b>Grid steps:</b> {list_text(c["steps"])}</p>'
           f'<p style="margin:0 0 1pt;font-size:8.8pt;line-height:1.22"><b>16th swing moves:</b> {list_text(m16)}</p>'
           f'<p style="margin:0;font-size:8.8pt;line-height:1.22"><b>8th swing moves:</b> {list_text(m8)}</p>')
    return (f'<div class="box" style="margin-bottom:{mb}pt;padding:{pad}pt 9pt"><span class="k" style="font-size:11.5pt;margin:0 0 3pt">{c["part"]} · {c["name"]}</span>'
            f'<div style="display:flex;gap:10pt;align-items:flex-start"><div style="flex:0 0 {w}">{D.body_svg(card_body(c))}</div>'
            f'<div style="flex:1">{txt}</div></div></div>')


def grid1_page(n, wm=False):
    cards = "".join(card_html(card(k)) for k in CARD_PAGES["grid1"])
    inner = (f'<p style="margin:0 0 4pt;font-size:10pt;line-height:1.34">A bar of 4/4 has 4 beats, and each beat holds 4 sixteenth notes, so one bar is '
             f'<b>16 grid steps</b>. Count every beat 1 e &amp; a. Each card shows one layer’s hits on that grid: the numbers 1 to 16 are the grid steps, the counts '
             f'sit under them, and the shaded steps are the beats. {ICON_SQ} A black square is a hit that stays put when a 16th-note swing is on; '
             f'{ICON_CI} a blue circle is a hit on an “e” or an “a”, and it moves later. Each card also lists its hits in words, so it works in black and white. '
             f'Step 3 of the project sheet: program a straight groove from these cards.</p>'
             + cards)
    return D.page("Step-grid cards 1: bells, shaker, tambourine", "STUDENT", "Classes 1–2", inner, n, wm, name=True, key="grid1")


def grid2_page(n, wm=False):
    cards = "".join(card_html(card(k), mb=5, pad=4) for k in CARD_PAGES["grid2"])
    inner = (f'<p style="margin:0 0 4pt;font-size:10.2pt;line-height:1.36">Four more cards: the wood block, kick, snare and hi-hat. A groove sounds finished '
             f'when each layer has its own steps. Step 3: program it straight, one layer at a time, and listen with the kick on before you add the next.</p>'
             + cards +
             f'<div class="box acc-b" style="padding:4pt 9pt"><span class="k" style="font-size:11.5pt;margin:0 0 2pt">My own pattern</span>'
             f'<div style="display:flex;gap:10pt;align-items:flex-start"><div style="flex:0 0 4.7in">{D.body_svg(blank_body(3, "blank grid plan"))}</div>'
             f'<div style="flex:1"><p style="margin:0 0 2pt;font-size:9.2pt;line-height:1.3">Fill in up to three layers of your own. Mark the hits, '
             f'then write the grid steps and counts below.</p><div class="fl" style="margin:4pt 0 0"><b>Steps:</b><span></span></div>'
             f'<div class="fl" style="margin:3pt 0 0"><b>Counts:</b><span></span></div></div></div></div>')
    return D.page("Step-grid cards 2: wood block, kick, snare, hi-hat", "STUDENT", "Classes 1–2", inner, n, wm, name=True, key="grid2")


# ================================================================ the swing page
def pct_rows():
    s16, pair16, pair8 = sixteenth_ms(TABLE_BPM), 2 * sixteenth_ms(TABLE_BPM), 4 * sixteenth_ms(TABLE_BPM)
    rows = []
    for p in SW_PCTS:
        o16, o8 = p / 100 * pair16, p / 100 * pair8
        rows.append(f"<tr><td><b>{p}%</b></td><td>{SW_NAMES[p]}</td><td>{fmt(o16)} ms</td><td>{fmt(o16 - s16)} ms</td><td>{fmt(o8)} ms</td><td>{fmt(o8 - 2 * s16)} ms</td></tr>")
    return "".join(rows)


def step_table(lo, hi):
    rows = []
    for i in range(lo, hi):
        st, a, b = swung_start_ms(i, TABLE_BPM, 50), swung_start_ms(i, TABLE_BPM, 60), swung_start_ms(i, TABLE_BPM, 66)
        mv = moves16(i + 1)
        rows.append(f"<tr><td><b>{i + 1}</b></td><td>{step_count_long(i + 1)}</td><td>{fmt(st)}</td><td>{'<b>' if mv else ''}{fmt(a)}{'</b>' if mv else ''}</td>"
                    f"<td>{'<b>' if mv else ''}{fmt(b)}{'</b>' if mv else ''}</td></tr>")
    return (f'<table class="t sw" style="font-size:9pt;line-height:1.1;margin:0"><tr><th>Grid step</th><th>Count</th><th>Straight</th><th>60%</th><th>66%</th></tr>'
            f'{"".join(rows)}</table>')


def swing_page(n, wm=False):
    inner = (f'<style>table.sw td, table.sw th {{ padding: 1.2pt 4pt; }} table.sw th {{ font-size: 8.6pt; }}</style>'
             f'<p style="margin:0 0 3pt;font-size:10pt;line-height:1.34">Step 4: swing it. One bar is 16 grid steps, so at {TABLE_BPM} BPM a 16th note lasts '
             f'60000 ÷ {TABLE_BPM} ÷ 4 = <b>{fmt(sixteenth_ms(TABLE_BPM))} ms</b>. Swing takes each <b>pair</b> of notes and moves the second one later: the swing percent is how far through the pair the '
             f'second note starts. 50% is straight. Bold numbers below are the steps a 16th-note swing moves.</p>'
             f'<div style="width:6.6in;margin:0 auto 3pt">{D.body_svg(swing_body(1500, "swing page"))}</div>'
             f'<div class="cols" style="gap:10pt;align-items:flex-start"><div style="flex:1.15"><span class="k" style="font-size:9.4pt">Percent to milliseconds at {TABLE_BPM} BPM</span>'
             f'<table class="t sw" style="font-size:8.8pt;line-height:1.12;margin:1pt 0 0"><tr><th rowspan="2">Swing</th><th rowspan="2">Feel</th><th colspan="2">16th pairs (250 ms)</th><th colspan="2">8th pairs (500 ms)</th></tr>'
             f'<tr><th>2nd starts</th><th>Late by</th><th>2nd starts</th><th>Late by</th></tr>{pct_rows()}</table>'
             f'<p class="small" style="margin:2pt 0 0;font-size:8.4pt">A true triplet feel is 2⁄3 of the pair: 166.7 ms and 333.3 ms. 66% is the nearest whole number.</p></div></div>'
             f'<span class="k" style="font-size:9.4pt;margin-top:3pt">Every grid step in one bar at {TABLE_BPM} BPM (ms from the start of the bar; 16th-note swing)</span>'
             f'<div class="cols" style="gap:10pt"><div>{step_table(0, 8)}</div><div>{step_table(8, 16)}</div></div>'
             f'<div class="cols" style="gap:10pt;margin-top:5pt"><div class="box acc-b" style="padding:4pt 9pt"><span class="k">At my tempo</span>'
             f'<div class="fl" style="margin:2pt 0 3pt;font-size:9.6pt"><b>My tempo (BPM):</b><span></span><b>One 16th = 15000 ÷ BPM =</b><span></span><b>ms</b></div>'
             f'<div class="fl" style="margin:0 0 3pt;font-size:9.6pt"><b>Pair of 16ths =</b><span></span><b>ms · 60% =</b><span></span><b>ms · 66% =</b><span></span><b>ms</b></div>'
             f'<p style="margin:0;font-size:8.8pt;line-height:1.28">Check: at {EX_BPM} BPM a 16th lasts {fmt(sixteenth_ms(EX_BPM))} ms, a pair {fmt(2 * sixteenth_ms(EX_BPM))} ms; 60% starts the 2nd note at '
             f'{fmt(.6 * 2 * sixteenth_ms(EX_BPM))} ms and 66% at {fmt(.66 * 2 * sixteenth_ms(EX_BPM))} ms.</p></div>'
             f'<div class="box" style="padding:4pt 9pt"><span class="k">Where swing lives in Logic</span><p style="margin:0;font-size:8.8pt;line-height:1.28">'
             f'Look for a Swing control in the Step Sequencer, and for Q-Swing in a MIDI region’s Quantize settings, if your version has them (page {pg("logicref")}). '
             f'Scales differ: find the setting that sounds even first and call it straight, then test 60 and 66.</p></div></div>')
    return D.page("Straight vs swing: the timing table", "STUDENT", "Class 2", inner, n, wm, name=True, key="swing")


# ================================================================ plan, layer map, listening worksheet
PLAN_MENU = ["Sleigh bells: quarter jingle or gallop", "A sixteenth-note shaker", "Tambourine or wood block on the offbeats",
             "Kick: plain or with the push", "A fill in bar 8",
             "Channel EQ on the bells and shaker", "A Compressor on the kick and snare", "Velocity changes on the in-between hits"]


def plan_page(n, wm=False):
    half = (len(PLAN_MENU) + 1) // 2
    items = [D.chk(f"<b>{m}</b>", 11, "font-size:9.8pt;margin-bottom:3pt") for m in PLAN_MENU]
    rows = "".join(f"<tr><td style='height:18pt'><b>{a}</b></td><td></td><td></td><td></td></tr>"
                   for a in [x for x, _ in LAYER_ORDER])
    inner = (f'<p style="margin:0 0 4pt;font-size:10.4pt;line-height:1.36">Step 1: plan. Pick a tempo from 90 to 120 BPM, choose at least five layers and decide on a feel. '
             f'The patterns are on the cards (pages {pg("grid1")}–{pg("grid2")}).</p>'
             f'<div class="box acc-b" style="margin:0 0 5pt"><span class="k">My choices</span>'
             f'<div class="fl" style="margin:3pt 0 0"><b>Tempo (BPM):</b><span style="flex:0 0 0.9in"></span><b>Why this tempo:</b><span></span></div>'
             f'<div class="fl" style="margin:0"><b>One 16th lasts (15000 ÷ BPM):</b><span style="flex:0 0 0.9in"></span>'
             f'<b>The feel I want my groove to have:</b><span></span></div></div>'
             f'<span class="k">My layers (at least five)</span>'
             f'<table class="map" style="margin-bottom:4pt"><tr><th style="width:17%">Layer</th><th style="width:25%">Sound for the pad (where from)</th>'
             f'<th style="width:25%">Pattern (card or my own)</th><th>Its job in the groove</th></tr>{rows}</table>'
             f'<span class="k">My moves (check the ones I will use)</span>'
             f'<div class="cols" style="gap:12pt"><div>{"".join(items[:half])}</div><div>{"".join(items[half:])}</div></div>'
             f'<span class="k">My 8 bars</span>'
             f'<div class="fl" style="margin-top:2pt"><b>Bars 1–4 (groove A):</b><span></span></div>'
             f'<div class="fl" style="margin-top:0"><b>Bars 5–8 (the variation) and my fill in bar 8:</b><span></span></div>'
             f'<div class="fl" style="margin-top:0"><b>What stays the same, so it still sounds like one groove:</b><span></span></div>'
             f'<span class="k">Sketch: one bar of my own groove (pencil, optional)</span>'
             f'<div style="margin-top:2pt;width:4.9in">{D.body_svg(blank_body(2, "blank grid"))}</div>')
    return D.page("My groove plan", "STUDENT", "Class 1", inner, n, wm, name=True, key="plan")


def layers_page(n, wm=False):
    head = "<tr><th style='width:1.3in'>Layer</th>" + "".join(f"<th>Bar {i + 1}</th>" for i in range(EX_BARS)) + "</tr>"
    names = [x for x, _ in LAYER_ORDER] + ["Fill (bar 8)", "Swing %", "Effects"]
    body = "".join(f"<tr><td class='l' style='height:25pt'>{nm}</td>" + "".join(f"<td class='{'b' if i % 4 == 0 else ''}'></td>" for i in range(EX_BARS))
                   + "</tr>" for nm in names)
    hr = "".join(f"<tr><td><b>{b}</b></td><td>{bar_s(b):.2f} s</td>" + "".join(f"<td>{length_s(bars, b):.1f} s</td>" for bars in LEN_BARS) + "</tr>"
                 for b in LEN_BPMS)
    inner = (f'{CSS_SG}<style>table.sg th {{ font-size: 7.4pt; }} table.sg td.l {{ width: 1.3in; }}</style>'
             f'<p style="margin:0 0 4pt;font-size:10.4pt">Step 5: grow to 8 bars. Bars 1 to 4 are your groove; bars 5 to 8 are a variation with a fill in bar 8. Each column is one bar. '
             f'Shade the bars where each layer plays, write the swing percent you used and note any effect (for example, Channel EQ on the bells). The thick line marks bar 5, where your variation starts.</p>'
             f'<table class="sg">{head}{body}</table>'
             f'<div class="cols" style="gap:10pt;margin-top:6pt"><div class="box acc-b"><span class="k">My arithmetic</span>'
             f'<div class="fl" style="margin:3pt 0 0"><b>My tempo (BPM):</b><span></span></div>'
             f'<div class="fl"><b>One bar = 240 ÷ BPM =</b><span></span><b>seconds</b></div>'
             f'<div class="fl"><b>4 bars = 4 × one bar =</b><span></span><b>seconds</b></div>'
             f'<div class="fl" style="margin-bottom:0"><b>8 bars = 8 × one bar =</b><span></span><b>seconds</b></div></div>'
             f'<div><span class="k">Groove-length helper (4/4)</span><table class="t" style="font-size:9.4pt;margin-top:2pt"><tr><th>BPM</th><th>One bar</th>'
             f'<th>{LEN_BARS[0]} bars</th><th>{LEN_BARS[1]} bars</th><th>{LEN_BARS[2]} bars</th></tr>{hr}</table><p class="small" style="margin:1pt 0 0">'
             f'Seconds = bars × 240 ÷ BPM. 16 bars is the 8 bars played twice.</p></div></div>'
             f'<div class="box" style="margin-top:6pt"><span class="k">Checks before I bounce</span>'
             + "".join(D.chk(c, 11, "font-size:10pt;margin-bottom:2pt") for c in [
                 "At least five layers play, and every layer has its own steps.",
                 "Bars 5 to 8 change something, and bar 8 has a fill.",
                 "The kick and snare are clear; the bells and shaker are quieter.",
                 "I know which grid steps my swing moves, and I tested 50, 60 and 66 percent.",
                 "My arithmetic is done: 4 bars and 8 bars in seconds."]) + '</div>')
    return D.page("Layer map", "STUDENT", "Class 3", inner, n, wm, name=True, key="layers")


WORD_BANK = ["stiff", "steady", "marching", "bouncy", "rolling", "skipping", "lazy", "driving", "laid-back", "shuffling", "tight", "loose"]


def listen_page(n, wm=False):
    cols = ["Straight (50%)", "Swing at 60%", "Swing at 66%"]
    qs = ["How it feels, in my words (use the word bank)", "Where I can tap my foot easily", "The layer that sounds most different",
          "The hits that moved (grid steps)", "How late the 2nd note of a pair lands (ms at my tempo)"]
    rows = "".join(f"<tr><td style='width:24%'><b>{q}</b></td>" + "".join("<td style='height:34pt'></td>" for _ in cols) + "</tr>" for q in qs)
    inner = (f'<p style="margin:0 0 4pt;font-size:10.4pt;line-height:1.36">Step 4: swing it. Play your 4-bar groove straight, then the swung copy at 60% and at 66%. '
             f'Nothing is played from this kit: you listen to your own work. Fill in one column for each version, then answer the questions below. '
             f'The timing numbers are on page {pg("swing")}.</p>'
             f'<table class="map" style="margin-bottom:5pt"><tr><th style="width:24%">I listened to</th>' + "".join(f"<th>{c}</th>" for c in cols) + f'</tr>{rows}</table>'
             f'<div class="box acc-b" style="padding:4pt 10pt;margin-bottom:5pt"><span class="k">Word bank</span><p style="margin:0;font-size:10.4pt">'
             + " · ".join(WORD_BANK) + '. Add your own words.</p></div>'
             f'<div class="cols" style="gap:12pt"><div class="box" style="padding:4pt 10pt"><span class="k">Which feel fits which job?</span>'
             f'<div class="fl" style="margin:3pt 0"><b>A march:</b><span></span></div><div class="fl" style="margin:0 0 3pt"><b>A ride through the snow:</b><span></span></div>'
             f'<div class="fl" style="margin:0 0 3pt"><b>A lullaby:</b><span></span></div></div>'
             f'<div class="box" style="padding:4pt 10pt"><span class="k">Tap along</span><p style="margin:0;font-size:10pt;line-height:1.32">Tap the beat with one hand and the “e” '
             f'and “a” hits with the other. In the straight version the two hands are evenly spaced. In the swung versions the second tap is late. Which layer makes that easiest to hear?</p></div></div>'
             f'<span class="k" style="margin-top:6pt">My verdict</span>'
             f'<div class="fl" style="margin:2pt 0 4pt"><b>The feel I chose for my final 8 bars is</b><span></span></div>'
             f'<div class="fl" style="margin:0 0 4pt"><b>Because</b><span></span></div><div class="ln2" style="margin-bottom:2pt"></div>'
             f'<div class="fl" style="margin:4pt 0 0"><b>One thing a listener should notice:</b><span></span></div>')
    return D.page("Listening and compare worksheet", "STUDENT", "Class 2", inner, n, wm, name=True, key="listen")


# ================================================================ worked example (2 pages)
def ex_move_rows():
    rows = []
    for label, k in LAYER_ORDER:
        c = card(k)
        rows.append(f"<tr><td><b>{label}</b></td><td>{c['name']}</td><td>{list_text(c['steps'])}</td><td>{list_text(card_moves(c, 16))}</td><td>{list_text(card_moves(c, 8))}</td></tr>")
    return "".join(rows)


def example_page(n, wm=False):
    inner = (f'<p style="margin:0 0 4pt;font-size:10pt">An <b>invented plan on paper</b>: an 8-bar groove at {EX_BPM} BPM. No audio is included. '
             f'Student projects will differ. Page 1 of 2: the plan and groove B.</p>'
             f'<div class="cols" style="gap:10pt"><div class="box"><span class="k">1 · A weak plan</span><p style="margin:0;font-size:10.2pt">{EX_WEAK}</p>'
             f'<p style="margin:3pt 0 0;font-size:9.2pt">It names no tempo, no layers, no length and no swing amount.</p></div>'
             f'<div class="box acc-b"><span class="k">2 · A clear plan</span><p style="margin:0;font-size:8.6pt;line-height:1.28">{EX_STRONG}</p></div></div>'
             f'{D.H2("3 · Groove B, bars 5 to 8: seven layers on the 16-step grid")}'
             f'<div style="width:6.9in;margin:2pt auto 0">{D.body_svg(layers_body("page layers", 40, 34, 170))}</div>'
             f'{D.H2("4 · Which hits does swing move?")}'
             f'<table class="t" style="font-size:8.8pt;line-height:1.2"><tr><th>Layer</th><th>Card</th><th>Grid steps hit</th><th>16th swing moves</th><th>8th swing moves</th></tr>{ex_move_rows()}</table>'
             f'<p style="margin:3pt 0 0;font-size:8.8pt">The plan uses 16th-note swing, so the shaker, the bells, the tambourine and the kick change feel while the hat, wood block and snare stay put. '
             f'An 8th-note swing would move the “&amp;” hits instead: grid steps 3, 7, 11 and 15.</p>')
    return D.page("Worked example · the plan and groove B", "EXAMPLE", "Teacher", inner, n, wm, ak=True, key="example")


def ex_rows():
    out = []
    for nm, a, b in EX_SECTIONS:
        extra = "gallop, tambourine and wood block join; snare fill in bar 8" if nm == "Groove B" else "bells (quarter jingle), kick, hat; shaker bar 2, snare bar 3"
        out.append(f"<tr><td><b>{nm}</b></td><td style='white-space:nowrap'>{a}–{b}</td><td style='white-space:nowrap'>{(a - 1) * EX_BAR_S:.1f}–{b * EX_BAR_S:.1f} s</td>"
                   f"<td>up to {max(EX_DENS[a - 1:b])} layers: {extra}</td></tr>")
    return "".join(out)


def example2_page(n, wm=False):
    moms = "".join(f"<tr><td style='width:12%'><b>bar {b}</b></td><td style='width:14%'>{(b - 1) * EX_BAR_S:.1f} s</td><td>{d}</td></tr>" for b, d in EX_MOMENTS)
    qs = " ".join(f"{i + 1}. {q}" for i, q in enumerate(EX_QUESTIONS))
    s16, pr = sixteenth_ms(EX_BPM), 2 * sixteenth_ms(EX_BPM)
    inner = (f'<p style="margin:0 0 3pt;font-size:10pt">The same groove, page 2 of 2: the map of the whole piece, then the numbers.</p>'
             f'{D.H2("5 · The map: 8 bars, seven layers, 19.2 seconds")}'
             f'<div style="width:7.4in;margin:1pt auto 3pt">{D.body_svg(map_body(1500, "page map", 27, 23, 25, 40))}</div>'
             f'<div class="cols" style="gap:10pt"><div><span class="k" style="font-size:9.4pt">6 · Sections</span>'
             f'<table class="t" style="font-size:9.6pt;line-height:1.22;margin-top:2pt"><tr><th>Section</th><th>Bars</th><th>Time</th><th>What plays</th></tr>{ex_rows()}</table></div>'
             f'<div><span class="k" style="font-size:9.4pt">7 · Moments to point out</span>'
             f'<table class="t" style="font-size:9.6pt;line-height:1.22;margin-top:2pt">{moms}</table></div></div>'
             f'<div class="box acc-b" style="margin-top:6pt"><span class="k">8 · Checking the numbers</span><p style="margin:0;font-size:10.2pt;line-height:1.38">'
             f'One bar of 4/4 at {EX_BPM} BPM lasts 240 ÷ {EX_BPM} = {EX_BAR_S:g} seconds, so {EX_BARS} bars = {EX_BARS} × {EX_BAR_S:g} = {EX_BARS * EX_BAR_S:g} seconds '
             f'and 4 bars = {4 * EX_BAR_S:g} seconds. A 16th lasts 15000 ÷ {EX_BPM} = {fmt(s16)} ms, so a pair of 16ths lasts {fmt(pr)} ms. At {EX_SWING}% swing the second note of a pair starts at '
             f'{EX_SWING / 100:.2f} × {fmt(pr)} = {fmt(EX_SWING / 100 * pr)} ms instead of {fmt(s16)} ms, which is {fmt(EX_SWING / 100 * pr - s16)} ms late; at 66% it starts at {fmt(.66 * pr)} ms, {fmt(.66 * pr - s16)} ms late. '
             f'A moment in bar b happens at (b − 1) × {EX_BAR_S:g} seconds: bar 5 is 4 × {EX_BAR_S:g} = {4 * EX_BAR_S:g} seconds. '
             f'The layers playing in bars 1 to 8 are {", ".join(str(x) for x in EX_DENS)}.</p></div>'
             f'<div class="box" style="margin-top:5pt"><span class="k">9 · Three feedback questions (invented)</span><p style="margin:0;font-size:10.2pt;line-height:1.38">{qs}</p></div>')
    return D.page("Worked example · the map and the numbers", "EXAMPLE", "Teacher", inner, n, wm, ak=True, key="example2")


PAGES = {"howto": howto_page, "overview": overview_page, "setup": setup_page, "example": example_page, "example2": example2_page,
         "grid1": grid1_page, "grid2": grid2_page, "swing": swing_page, "plan": plan_page, "layers": layers_page, "listen": listen_page}


# ================================================================ content checks
def alpha_bbox(path):
    from PIL import Image
    import numpy as np
    a = np.array(Image.open(path).convert("RGBA"))[..., 3]
    ys, xs = np.where(a > 10)
    return xs.min(), ys.min(), xs.max(), ys.max()


DANGLING = {"a", "an", "the", "of", "to", "at", "in", "on", "for", "and", "or", "with", "your", "each", "every", "their", "its", "from", "by",
            "as", "is", "are", "that", "than", "but", "my", "then", "this", "these", "those", "into", "than", "so"}


def truncated(b):
    """A bullet that ends mid-sentence: ends in a possessive 's, a dangling article, preposition or conjunction, or a comma or colon."""
    last = re.sub(r"[^\w’']", "", b.split()[-1]).lower()
    if b.endswith("& a"):          # the count 1 e & a ends in the letter a
        return False
    return b.endswith(("’s", "'s", ",", ":", "…")) or last in DANGLING


TRANSPARENT_JS = r"""
const { chromium } = require('playwright');
const url = require('url');
const fs = require('fs');
(async () => {
  const jobs = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
  const browser = await chromium.launch();
  for (const j of jobs) {
    const page = await browser.newPage({ viewport: { width: j.width, height: j.height } });
    await page.goto(url.pathToFileURL(j.html).href, { waitUntil: 'load' });
    await page.evaluate(() => document.fonts.ready);
    await page.screenshot({ path: j.png, omitBackground: true, clip: { x: 0, y: 0, width: j.width, height: j.height } });
    await page.close();
  }
  await browser.close();
})().catch(e => { console.error(e); process.exit(1); });
"""


def drawing_edge_errors():
    """Rendered-pixel check: every reusable drawing, rendered alone on a TRANSPARENT ground at the size it is used, has no inked pixel
    (alpha above 8) within 4 px of any of its four edges, and is not empty."""
    from PIL import Image
    import numpy as np
    import json
    errs = []
    bd = D.build_dir()
    jobs = []
    allk = {**{k: v for k, v in DRAWINGS.items() if k != "hero"}, **PAGE_DRAWINGS}
    for k, fn in allk.items():
        svg = D.body_svg(fn())
        vw, vh = map(float, re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', svg).groups())
        w = 1400
        h = int(round(w * vh / vw)) + 2
        html = (f'<!doctype html><html><head><meta charset="utf-8"><style>{D.font_css()}html,body{{margin:0;background:transparent}}</style></head>'
                f'<body><div style="width:{w}px;height:{h}px;overflow:hidden;background:transparent">{svg}</div></body></html>')
        hp = D.write(f"tr-{k}.html", html)
        jobs.append({"html": hp, "png": os.path.join(bd, f"tr-{k}.png"), "width": w, "height": h})
    jp = D.write("tr-jobs.json", json.dumps(jobs))
    js = D.write("tr.js", TRANSPARENT_JS)
    subprocess.run(["node", js, jp], check=True, env=D.node_env())
    for j in jobs:
        k = os.path.basename(j["png"])[3:-4]
        a = np.array(Image.open(j["png"]).convert("RGBA"))[..., 3]
        if (a > 8).sum() == 0:
            errs.append(f"drawing '{k}' rendered empty on a transparent ground")
            continue
        e = 4
        for side, strip in (("top", a[:e, :]), ("bottom", a[-e - 2:-2, :]), ("left", a[:, :e]), ("right", a[:, -e:])):
            if strip.max() > 8:
                errs.append(f"drawing '{k}' has ink within {e}px of its {side} edge when rendered alone on a transparent ground (clipped art)")
    return errs


def verify_content():
    errs = []
    counts = dict(goals=(GOALS, 4), vocab=(VOCAB, 4), reqs=(REQS, 7), steps=(STEPS, 7), tips=(TIPS, 4), check=(CHECK, 6),
                  rubric=(RUBRIC, 5), struggles=(STRUGGLES, 4), resources=(RESOURCES, 4), cards=(CARDS, 8), slides=(SLIDES, 14), plan=(PLAN, 24))
    for nm, (lst, nexp) in counts.items():
        if len(lst) != nexp:
            errs.append(f"{nm}: {len(lst)} items, expected {nexp}")
    if RUBRIC_TOTAL != 25 or LEVELS != [1, 2, 3, 4, 5]:
        errs.append("rubric is /25, levels 1-5")
    if FILE_NAME not in CHECK[2]:
        errs.append("file name format must be on the checklist")
    if set(TAGS) & {"Holiday", "Student Practice", "Theme", "Seasonal"} or "Performing Arts" in SUBJECTS:
        errs.append("tags and subjects must not be headings")
    for w in ("winter", "holiday", "christmas", "sleigh", "carol", "snow"):
        if w in LISTING_TITLE.lower():
            errs.append(f"the listing title must not hold the seasonal word {w}")
    if len(STEP_NAMES) != len(STEPS) or any(not s.startswith(f"<b>{nm}</b>") for s, nm in zip(STEPS, STEP_NAMES)):
        errs.append("STEPS must start with the bold names in STEP_NAMES (the pages cite them)")
    # ---- the 16-step grid: 16 steps = 4 beats of 4 sixteenths, counted 1 e & a
    if NSTEPS != 16 or STEPS_PER_BEAT * BEATS != 16 or len(STEP_LABELS) != STEPS_PER_BEAT:
        errs.append("16 steps = 4 beats x 4 sixteenths")
    if " ".join(step_count(i) for i in range(16)) != "1 e & a 2 e & a 3 e & a 4 e & a":
        errs.append("the count of the 16 steps must read 1 e & a 2 e & a 3 e & a 4 e & a")
    if [step_count_long(n) for n in (1, 2, 3, 4, 5, 6, 7, 8, 14, 16)] != ["1", "1 e", "1 &", "1 a", "2", "2 e", "2 &", "2 a", "4 e", "4 a"]:
        errs.append("step_count_long")
    # ---- pattern cards
    parts = {c["part"] for c in CARDS}
    if parts != {"Sleigh bells", "Shaker", "Tambourine", "Wood block", "Kick", "Snare", "Hi-hat"}:
        errs.append(f"card parts {sorted(parts)}")
    if sorted(k for ks in CARD_PAGES.values() for k in ks) != sorted(c["key"] for c in CARDS):
        errs.append("every card is on exactly one page")
    if [k for k, _ in [(k, 0) for _, k in LAYER_ORDER]] != ["bells_g", "shaker", "tamb", "wood", "kick", "snare", "hat"]:
        errs.append("layer order of the example groove")
    for c in CARDS:
        s = c["steps"]
        if s != sorted(set(s)) or not all(1 <= x <= 16 for x in s):
            errs.append(f"card {c['key']}: grid steps must be 1-16, ascending, no repeats")
    want = {"bells_q": ([1, 5, 9, 13], [], [], "1 · 2 · 3 · 4"),
            "bells_g": ([1, 3, 4, 5, 7, 8, 9, 11, 12, 13, 15, 16], [4, 8, 12, 16], [3, 7, 11, 15],
                        None),
            "shaker": (list(range(1, 17)), list(range(2, 17, 2)), [3, 7, 11, 15], None),
            "tamb": ([5, 8, 13, 16], [8, 16], [], "2 · 2 a · 4 · 4 a"),
            "wood": ([3, 7, 11, 15], [], [3, 7, 11, 15], "1 & · 2 & · 3 & · 4 &"),
            "kick": ([1, 6, 9, 14], [6, 14], [], "1 · 2 e · 3 · 4 e"),
            "snare": ([5, 13], [], [], "2 · 4"),
            "hat": ([1, 3, 5, 7, 9, 11, 13, 15], [], [3, 7, 11, 15], "1 · 1 & · 2 · 2 & · 3 · 3 & · 4 · 4 &")}
    for k, (st, m16, m8, _ct) in want.items():
        c = card(k)
        if c["steps"] != st or card_moves(c, 16) != m16 or card_moves(c, 8) != m8:
            errs.append(f"card {k}: hits {c['steps']} or the hits swing moves ({card_moves(c, 16)}, {card_moves(c, 8)}) are wrong")
    if counts_text(card("kick")) != "1 · 2 e · 3 · 4 e" or counts_text(card("tamb")) != "2 · 2 a · 4 · 4 a" or counts_text(card("wood")) != "1 & · 2 & · 3 & · 4 &" \
            or counts_text(card("snare")) != "2 · 4" or counts_text(card("bells_q")) != "1 · 2 · 3 · 4":
        errs.append("card counts: kick 1 2e 3 4e, tambourine 2 2a 4 4a, wood block 1& 2& 3& 4&, snare 2 4, bells 1 2 3 4")
    if counts_text(card("bells_g")).split(" · ")[:6] != ["1", "1 &", "1 a", "2", "2 &", "2 a"]:
        errs.append("gallop counts")
    # step n is beat (n-1)//4+1: grid steps 1, 5, 9, 13 are the beats
    if [n for n in range(1, 17) if (n - 1) % 4 == 0] != [1, 5, 9, 13]:
        errs.append("beats fall on grid steps 1, 5, 9 and 13")
    # ---- straight vs swung timing
    if sixteenth_ms(120) != 125 or beat_ms(120) != 500 or 16 * sixteenth_ms(120) != 2000 or sixteenth_ms(100) != 150 or sixteenth_ms(90) * 6 != 1000:
        errs.append("a 16th at 120 BPM is 125 ms (beat 500, bar 2000); at 100 BPM 150 ms; at 90 BPM 166.67 ms")
    if round(sixteenth_ms(110), 2) != 136.36 or round(sixteenth_ms(90), 2) != 166.67:
        errs.append("16th at 110 and 90 BPM")
    straight = [swung_start_ms(i, 120, 50) for i in range(16)]
    if straight != [125 * i for i in range(16)] or [swung_start_ms(i, 120, 50, 8) for i in range(16)] != straight:
        errs.append("50% swing must equal straight, step by step (125 ms apart at 120 BPM)")
    t60 = [swung_start_ms(i, 120, 60) for i in range(16)]
    t66 = [swung_start_ms(i, 120, 66) for i in range(16)]
    if t60 != [0, 150, 250, 400, 500, 650, 750, 900, 1000, 1150, 1250, 1400, 1500, 1650, 1750, 1900]:
        errs.append(f"swung 16ths at 60%: {t60}")
    if [round(x, 6) for x in t66] != [0, 165, 250, 415, 500, 665, 750, 915, 1000, 1165, 1250, 1415, 1500, 1665, 1750, 1915]:
        errs.append(f"swung 16ths at 66%: {t66}")
    for i in range(16):
        if (t60[i] != straight[i]) != moves16(i + 1) or (t66[i] != straight[i]) != moves16(i + 1):
            errs.append(f"only grid steps 2, 4, ... 16 move under a 16th swing (step {i + 1})")
    if any(not (straight[i] <= t66[i] < (i // 2 + 1) * 250) for i in range(16)):
        errs.append("a swung note must stay inside its pair")
    e8 = [swung_start_ms(i, 120, 66, 8) for i in range(16)]
    if [i + 1 for i in range(16) if e8[i] != straight[i]] != [3, 7, 11, 15] or e8[2] != 330 or round(swung_start_ms(2, 120, 75, 8), 6) != 375:
        errs.append("an 8th-note swing moves grid steps 3, 7, 11 and 15 (330 ms at 66% instead of 250)")
    pair16, pair8 = 2 * sixteenth_ms(120), 4 * sixteenth_ms(120)
    rows16 = [p / 100 * pair16 for p in SW_PCTS]
    rows8 = [p / 100 * pair8 for p in SW_PCTS]
    if rows16 != [125, 137.5, 150, 165, 187.5] or rows8 != [250, 275, 300, 330, 375] or [r - 125 for r in rows16] != [0, 12.5, 25, 40, 62.5] \
            or [r - 250 for r in rows8] != [0, 25, 50, 80, 125]:
        errs.append("swing percent table at 120 BPM (16th pairs 250 ms, 8th pairs 500 ms)")
    if round(2 / 3 * pair16, 1) != 166.7 or round(2 / 3 * pair8, 1) != 333.3:
        errs.append("a triplet feel is 166.7 ms and 333.3 ms at 120 BPM")
    if fmt(137.5) != "137.5" or fmt(125) != "125" or fmt(62.5) != "62.5" or fmt(sixteenth_ms(90)) != "166.7":
        errs.append("number formatting")
    # ---- groove length helper and the worked example
    if bar_s(120) != 2 or bar_s(100) != 2.4 or bar_s(90) * 3 != 8 or length_s(8, 100) != 19.2 and round(length_s(8, 100), 6) != 19.2:
        errs.append("one bar at 120 BPM is 2 s, at 100 BPM 2.4 s; 8 bars at 100 BPM = 19.2 s")
    got = [round(length_s(bars, bpm), 1) for bpm in LEN_BPMS for bars in LEN_BARS]
    if got != LEN_EXPECT:
        errs.append(f"groove-length helper numbers {got}")
    if round(length_s(4, 100), 6) != 9.6 or round(length_s(8, 100), 6) != 19.2 or round(length_s(8, 120), 6) != 16 or round(length_s(8, 90), 6) != 21.333333:
        errs.append("4 and 8 bars at 100, 120 and 90 BPM")
    if (TEMPO_LO, TEMPO_HI) != (90, 120) or EX_BPM not in range(TEMPO_LO, TEMPO_HI + 1) or EX_BARS != 8 or round(EX_BARS * EX_BAR_S, 6) != 19.2:
        errs.append("the example: 8 bars x 2.4 s = 19.2 s at 100 BPM, inside the project's tempo range")
    if EX_SECTIONS != [("Groove A", 1, 4), ("Groove B", 5, 8)] or EX_FILL_BAR != 8 or EX_FILL_STEPS != [13, 14, 15, 16]:
        errs.append("the example's sections tile bars 1-8: groove A bars 1-4, groove B bars 5-8, a fill in bar 8 on grid steps 13-16")
    if EX_DENS != [3, 4, 5, 5, 7, 7, 7, 7] or len(EX_LAYERS) != 7 or len(EX_QUESTIONS) != 3:
        errs.append(f"layers playing per bar: expected [3, 4, 5, 5, 7, 7, 7, 7], got {EX_DENS}; seven layers; three questions")
    for nm, spans, _d in EX_LAYERS:
        for a_, b_ in spans:
            if not 1 <= a_ <= b_ <= EX_BARS:
                errs.append(f"layer {nm}: span {a_}-{b_} outside the piece")
    if [nm for nm, _s, _d in EX_LAYERS] != [lab for lab, _ in LAYER_ORDER]:
        errs.append("the map's layers must be in the same order as the layers drawing")
    for need in ("100 BPM", "19.2 seconds", "60 percent", "180 ms", "150 ms", "8 bars"):
        if need not in EX_STRONG:
            errs.append(f"the clear plan must say '{need}'")
    if round(.6 * 2 * sixteenth_ms(100), 6) != 180 or round(.66 * 2 * sixteenth_ms(100), 6) != 198:
        errs.append("at 100 BPM, swing 60% = 180 ms and 66% = 198 ms")
    if [m[0] for m in EX_MOMENTS] != [2, 3, 5, 8] or [round((b - 1) * EX_BAR_S, 1) for b, _ in EX_MOMENTS] != [2.4, 4.8, 9.6, 16.8]:
        errs.append("moments: bars 2, 3, 5, 8 at 2.4, 4.8, 9.6 and 16.8 seconds")
    # ---- slides: no truncated bullets, side lines or notes; page numbers in notes are pages that exist and fit
    for i, s in enumerate(SLIDES, start=1):
        for b in [x.strip() for x in s[3].split("|") if x.strip()] if s[1] != "pic" else []:
            if truncated(b):
                errs.append(f"slide {i} bullet looks truncated: '{b}'")
        if s[1] == "listen":
            if len([x for x in s[3].split("|") if x]) != 5:
                errs.append(f"slide {i} (listen): head, teacher line and three questions")
    for k, lines in SIDE.items():
        for b in lines:
            if truncated(b) or b.endswith(".") or len(b) > 44:
                errs.append(f"side line for '{k}' looks truncated or has a stop: '{b}'")
    for i, s in enumerate(SLIDES, start=1):
        for m in re.finditer(r"\bpages? (\d+)\b", s[4]):
            if int(m.group(1)) not in {pg(k) for k in PLAN}:
                errs.append(f"slide {i} notes name page {m.group(1)}, which does not exist")
    for need, key in ((f"pages {pg('grid1')} and {pg('grid2')}", 4), (f"page {pg('logicref')}", 5), (f"page {pg('swing')}", 7), (f"page {pg('layers')}", 9)):
        if need not in SLIDES[key][4]:
            errs.append(f"slide {key + 1} notes must name {need}")
    # ---- Step N: only the project sheet's seven steps, with their names, on every deck slide and note
    for i, s in enumerate(SLIDES, start=1):
        errs += step_ref_errors(" ".join((s[2], s[3], s[4])), f"slide {i}")
    # ---- the hero art, used whole: its pixels sit inside the viewBox with room to spare
    hp = os.path.join(HERE, "art", "hero.png")
    if not os.path.exists(hp):
        errs.append("art/hero.png is missing")
    else:
        x0, y0, x1, y1 = alpha_bbox(hp)
        if min(x0 - HX, y0 - HY, HX + HW - 1 - x1, HY + HH - 1 - y1) < 40:
            errs.append(f"hero art {x0, y0, x1, y1} is closer than 40 units to the viewBox {HX, HY, HX + HW, HY + HH}")
    if "--check" in sys.argv:
        errs += drawing_edge_errors()
    return errs


STEP_REF = re.compile(r"\bStep (\d+)\b(?:: ([A-Za-z][A-Za-z &;]*))?")


def step_ref_errors(text, where):
    """Every capital 'Step N' is one of the project sheet's steps (1..7); when it is followed by a name ('Step 4: swing it') the name is that step's.
    A lower-case 'step N' that is not a grid step ('grid step 6') can only be the last step (the feedback planner says 'step 7')."""
    errs = []
    names = [re.sub(r"&amp;", "&", n).lower() for n in STEP_NAMES]
    for m in STEP_REF.finditer(text):
        n = int(m.group(1))
        if not 1 <= n <= len(STEPS):
            errs.append(f"{where}: 'Step {n}' is not a step on the project sheet (1 to {len(STEPS)})")
            continue
        nm = (m.group(2) or "").strip().lower().replace("&amp;", "&")
        if nm and not names[n - 1].startswith(nm.rstrip(".")) and not nm.startswith(names[n - 1]):
            errs.append(f"{where}: 'Step {n}: {nm}' does not match the project sheet's Step {n} ({names[n - 1]})")
    for m in re.finditer(r"(?<!grid )(?<![A-Za-z-])steps? (\d+)\b(?! of )", text):
        if int(m.group(1)) != len(STEPS) and "Step Sequencer" not in m.group(0):
            errs.append(f"{where}: '{m.group(0)}' is not a grid step (needs 'grid') and not the last project step")
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
    # art must keep clear of the band too: the last inked row above the band sits at least 8 px above it
    inked = np.where(g[:top - 2, edge:w - edge].min(axis=1) < 200)[0]
    if len(inked) and top - 1 - inked.max() < 8 and top != h - 1:
        errs.append(f"{label}: art touches the black band")
    return errs


def verify_outputs(flat, stext, notes):
    errs = []
    alldeck = " ".join(stext + notes)
    txt = " ".join(flat)
    if "No audio" not in notes[0]:
        errs.append("deck slide 1 notes must say 'No audio'")
    for need in ("No audio, recordings, lyrics, artists or albums", "invented plan on paper", "no melody", "Step Sequencer", "Drum Machine Designer", "Quick Sampler",
                 "Compressor", "Channel EQ", "16 grid steps", "1 e & a", "125 ms", "19.2 seconds", "if your version",
                 "Created with the help of digital and AI tools. Notation and answer keys are verified before release."):
        if need not in txt.replace("1 e &amp; a", "1 e & a"):
            errs.append(f"PDF must say: '{need}'")
    if "What changed" in txt or "Kept as I wrote it" in txt or "my project menu" in txt or "my Digital Music Production" in txt:
        errs.append("ORIGINAL kit: no wording about changes to an owner's sheet")
    if "checked by hand" in txt or "handmade" in txt.lower() or "classroom-tested" in txt.lower() or "hand-checked" in txt.lower():
        errs.append("never claim hand checks or classroom testing for a new product")
    if GRADES_TEXT != "9–12" or "Grades 9–12" not in txt:
        errs.append("PDF: 'Grades 9–12'")
    for w in ("colour", "favour", "centre", "licence", "grey", "metre", "organis", "recognis", "practise", "analyse", "rhythmic ", "whilst", "milli-second"):
        if w in txt.lower().replace("greyscale", "") and w != "rhythmic ":
            errs.append(f"US spelling: '{w}' in the PDF")
    # ---- Step N on every page, in the deck PDF text, the deck notes and UPLOAD.md agrees with the project sheet
    expect = {"grid1": {3}, "grid2": {3}, "swing": {4}, "plan": {1}, "layers": {5}, "listen": {4}}
    for k in PLAN:
        t = flat[D.IX(k) - 1]
        errs += step_ref_errors(t, f"page {D.IX(k)} ({k})")
        found = {int(m.group(1)) for m in re.finditer(r"\bStep (\d+)\b", t)}
        if k in expect and found != expect[k]:
            errs.append(f"page {D.IX(k)} ({k}) should cite Step {sorted(expect[k])}, cites {sorted(found)}")
        if k not in expect and found:
            errs.append(f"page {D.IX(k)} ({k}) cites Step {sorted(found)} unexpectedly")
    errs += step_ref_errors(" ".join(stext), "deck slides")
    import subprocess as sp

    def raw(key):
        return re.sub(r"\s+", " ", sp.run(["pdftotext", "-raw", "-f", str(D.IX(key)), "-l", str(D.IX(key)), D.files()["pdf"], "-"],
                                          capture_output=True, text=True, check=True).stdout)
    for pk in ("grid1", "grid2"):
        r = raw(pk)
        for k in CARD_PAGES[pk]:
            c = card(k)
            for need in (c["part"], c["name"], "Counts: " + counts_text(c), "Grid steps: " + list_text(c["steps"]),
                         "16th swing moves: " + list_text(card_moves(c, 16)), "8th swing moves: " + list_text(card_moves(c, 8))):
                if need.lower() not in r.lower():
                    errs.append(f"{pk} page: card text '{need}' is not printed")
    rs = raw("swing")
    for p, v16, l16, v8, l8 in ((50, 125, 0, 250, 0), (55, 137.5, 12.5, 275, 25), (60, 150, 25, 300, 50), (66, 165, 40, 330, 80), (75, 187.5, 62.5, 375, 125)):
        row = f"{p}% {SW_NAMES[p]} {fmt(v16)} ms {fmt(l16)} ms {fmt(v8)} ms {fmt(l8)} ms"
        if row not in rs:
            errs.append(f"swing page: table row '{row}' is not printed")
    for i in range(16):
        mv = moves16(i + 1)
        row = f"{i + 1} {step_count_long(i + 1)} {fmt(swung_start_ms(i, 120, 50))} {fmt(swung_start_ms(i, 120, 60))} {fmt(swung_start_ms(i, 120, 66))}"
        if row not in rs:
            errs.append(f"swing page: step row '{row}' is not printed")
    for need in ("60000 ÷ 120 ÷ 4 = 125 ms", "166.7 ms and 333.3 ms", "Step 4: swing it"):
        if need not in rs:
            errs.append(f"swing page must say '{need}'")
    rl = raw("layers")
    for need in ("Step 5: grow to 8 bars", "bars × 240 ÷ BPM"):
        if need not in rl:
            errs.append(f"layer map page must say '{need}'")
    for bpm in LEN_BPMS:
        row = f"{bpm} {bar_s(bpm):.2f} s " + " ".join(f"{length_s(b, bpm):.1f} s" for b in LEN_BARS)
        if row not in rl:
            errs.append(f"layer map page: length helper row '{row}' is not printed")
    re1 = raw("example") + " " + raw("example2")
    for need in ("240 ÷ 100 = 2.4", "8 bars = 8 × 2.4 = 19.2 seconds", "15000 ÷ 100 = 150 ms", "0.60 × 300 = 180 ms", "30 ms late", "198 ms", "48 ms late", "bar 5 is 4 × 2.4 = 9.6 seconds"):
        if need not in re1:
            errs.append(f"worked example must say '{need}'")
    for label, k in LAYER_ORDER:
        c = card(k)
        if f"{label} {c['name']} {list_text(c['steps'])} {list_text(card_moves(c, 16))} {list_text(card_moves(c, 8))}" not in raw("example"):
            errs.append(f"worked example: the swing row for {label} is not printed")
    up = open(os.path.join(HERE, "UPLOAD.md"), encoding="utf8").read()
    errs += step_ref_errors(up, "UPLOAD.md")
    if "Grades 9-12" not in up or "`9th-grade`, `10th-grade`, `11th-grade`, `12th-grade`" not in up:
        errs.append("UPLOAD.md: grades 9-12 in the description and section 3")
    if "no audio" not in up.lower() or "Open question" not in up or "Timing numbers" not in up:
        errs.append("UPLOAD.md: must say no audio is included, record the timing numbers checked and the open questions")
    m = re.search(r"= 1 cover \+ (\d+) teacher \+ (\d+) student \+ 1 terms page", up)
    if not m or 2 + int(m.group(1)) + int(m.group(2)) != len(PLAN):
        errs.append("UPLOAD.md: the page-count list (1 cover + teacher + student + 1 terms) must total the PDF's pages")
    if m and (int(m.group(1)) != D.IX("example2") - 1 or int(m.group(2)) != D.IX("reflect") - D.IX("grid1") + 1):
        errs.append("UPLOAD.md: teacher and student page counts must match the plan")
    m3 = re.search(r"plus (\d+) slides = (\d+) for TpT", up)
    if not m3 or int(m3.group(1)) != len(SLIDES) or int(m3.group(2)) != len(PLAN) + len(SLIDES):
        errs.append("UPLOAD.md: slides and the total for TpT must match the deck and the PDF")
    for t in TAGS:
        if t not in up:
            errs.append(f"UPLOAD.md: tag {t} missing")
    for banned in ["Billie", "Beatles", "Daft", "Skrillex", "Disney", "Radiohead", "Billboard", "Ro" + "land", "Bensound", "Ableton "]:
        if banned in alldeck or banned in txt:
            errs.append(f"must not name artists, albums, songs, sites, services or other brands ({banned})")
    # deck: every paragraph of the .pptx text, and every drawing label already checked; no truncated bullet reaches the slides
    from pptx import Presentation
    prs = Presentation(D.files()["deck"])
    for i, s in enumerate(prs.slides, start=1):
        for sh in s.shapes:
            if sh.has_text_frame and sh.shape_type == 17:
                r = sh.text_frame.paragraphs[0].runs
                if r and r[0].font.name == "Source Sans 3" and r[0].font.size and r[0].font.size.pt >= 22:
                    for p in sh.text_frame.paragraphs:
                        if p.text.strip() and truncated(p.text.strip().rstrip(".")) and not p.text.strip().endswith((".", "?")):
                            errs.append(f"deck slide {i}: text '{p.text.strip()}' looks truncated (dangling last word)")
    # deck art sits on the slide itself: transparent PNGs, never a white or off-white box
    from PIL import Image
    for k in DRAWINGS:
        im = Image.open(os.path.join(D.build_dir(), f"deck-{k}.png"))
        if im.mode != "RGBA" or im.getpixel((1, 1))[3] != 0 or im.getpixel((im.width - 2, im.height - 2))[3] != 0:
            errs.append(f"deck art '{k}' must be a PNG with a transparent background (no box on the slide)")
    # the cover and previews: nothing touches an edge; no big blank band
    F = D.files()
    for p in [F["cover"], *F["pv"]]:
        errs += edge_errors(p, os.path.basename(p))
    return errs


def check_summary():
    return (f"16 steps = 4 beats x 4 sixteenths, counted 1 e & a; {len(CARDS)} step-grid cards match their hits, counts and the hits a 16th or 8th swing moves; "
            f"straight vs swung table (all 16 steps at 120 BPM: 125 ms a 16th; 60% and 66% offsets 150 and 165 ms; percent table for 16th and 8th pairs) "
            f"recomputed; groove-length helper correct ({LEN_BPMS[0]}-{LEN_BPMS[-1]} BPM); the worked example is {EX_BARS} bars at {EX_BPM} BPM = "
            f"{EX_BARS * EX_BAR_S:g} s (layers per bar {EX_DENS}); every 'Step N' agrees with the project sheet on pages, slides, notes and UPLOAD.md; "
            f"every drawing renders alone on a transparent ground with no ink at its edges; hero art inside its viewBox; no truncated slide bullets; "
            f"edges of cover.png and previews clear; no audio, lyrics, melodies, artist names or student work; grades 9-12; tags and subjects are not headings; "
            f"no 'what changed' page (ORIGINAL).")


# ================================================================ UPLOAD.md (written by gen.py so every number matches the build)
def write_upload():
    np_, ns = len(PLAN), len(SLIDES)
    n_teacher = (PLAN.index("example2") + 1) - 1
    n_student = (PLAN.index("reflect") + 1) - (PLAN.index("grid1") + 1) + 1
    assert 2 + n_teacher + n_student == np_, "page-count list must total the PDF"
    nt = len(LISTING_TITLE)
    desc = (f"{DESC_START} students program a holiday percussion groove with no melody in Logic Pro. They build a Drum Machine Designer kit of sleigh bells, shaker, "
            f"tambourine, wood block, kick, snare and hi-hat, program a 4-bar groove in the Step Sequencer on a 16-step grid, then add swing and compare straight "
            f"with swung feel in words and in milliseconds. This Sleigh Bell Groove project takes {CLASSES} class periods (the pacing guide also shows two and four) and is an "
            f"original Hudson Beat project; the steps are written for Logic Pro, while the ideas (a 16-step grid, layers, swing percent) carry over to GarageBand, Ableton Live and BandLab.\n\n"
            f"WHAT'S INCLUDED (ZIP: {np_}-page PDF = 1 cover + {n_teacher} teacher + {n_student} student + 1 terms page, plus {ns}-slide intro deck as .pptx and PDF)\n"
            f"• Teacher pages: how to use, project overview, setup, a {CLASSES}-class pacing guide with the deck slides for each class, two pages of teacher notes "
            f"(struggles, variations, resources, grading), a Logic quick reference and a two-page worked example (an invented plan on paper: an 8-bar groove at 100 BPM = "
            f"19.2 seconds, with seven layers, a map and the swing numbers) ({n_teacher} pages)\n"
            f"• Student pages: eight step-grid pattern cards on two pages (sleigh bells, shaker, tambourine, wood block, kick, snare, hi-hat; each shows its hits on the 16 "
            f"grid steps with the count 1 e & a and the hits swing moves), the straight vs swing timing table (swing percent to milliseconds, all 16 steps), My groove plan, a Layer map with a "
            f"groove-length helper, a listening and compare worksheet, the 3-page project sheet (overview, goals, vocabulary, requirements, steps, tips, submission checklist), "
            f"the /{RUBRIC_TOTAL} rubric, a vocabulary page, a feedback planner and a reflection page ({n_student} pages)\n"
            f"• Teacher-presented intro deck, {ns} slides with speaker notes on every slide: a think-and-share hook, what the project is, the 16-step grid, "
            f"building the kit in Logic, the seven layers, how swing moves the second note, where swing lives in Logic, a worked-example map, what to turn in and the rubric\n\n"
            f"THE THREE CLASS PERIODS\n"
            f"• Class 1: hook; the 16-step grid; build the kit; program the straight groove\n"
            f"• Class 2: finish the straight groove; swing it at 50, 60 and 66 percent; the listening worksheet\n"
            f"• Class 3: grow to 8 bars with a variation and a fill; mix, bounce, present and reflect\n\n"
            f"WHAT STUDENTS LEARN\n"
            f"• Building a Drum Machine Designer kit and programming patterns in Logic Pro's Step Sequencer\n"
            f"• Reading a 16-step grid: four beats, four sixteenth notes in each, counted 1 e & a\n"
            f"• Straight versus swing feel, and swing as a percent and as milliseconds (at 120 BPM a 16th note lasts 125 ms)\n"
            f"• Balancing layers with volume, Channel EQ and a Compressor\n"
            f"• Planning a groove in bars and seconds (bars × 240 ÷ BPM), then explaining their choices in a reflection\n\n"
            f"GOOD TO KNOW\n"
            f"• There is no audio in this resource and no student work. No melody or song is printed or notated; students make every sound themselves in Logic Pro\n"
            f"• Requires Logic Pro on a Mac. A MIDI keyboard is not needed; nobody has to read music. Where a control may differ between versions, the pages say \"if your version has it\"\n"
            f"• Rubric: 5 categories scored 1-5, /{RUBRIC_TOTAL}; the final grade is the average of the student's and the teacher's score\n"
            f"• Grades 9-12; music technology or music production classes\n"
            f"• The deck uses the free Oswald and Source Sans 3 fonts (built into Google Slides); install them for PowerPoint or Keynote, or present "
            f"the PDF copy, which shows the intended look\n"
            f"• Every student page prints well in black and white\n\n"
            f"Logic Pro is a product of Apple Inc., named only to describe compatibility. This resource is not affiliated with Apple.\n\n"
            f"{D.DISCLOSURE_NEW}")
    md = f"""# UPLOAD: Sleigh Bell Groove, original Logic Pro project (TpT 057)

These fields follow the order of TpT's "Add a resource" form. `tools/tpt.js publish` reads the title and description from the code blocks under 1 and 2, and everything else from `tpt.json`. This file is written by `gen.py`; edit the text there.

**Files to attach**
- Resource (digital download): `{SLUG}.zip`. It holds three files in a folder "{ZIP_DIR}":
  - `{SLUG}.pdf`: the teacher and student resource, {np_} pages, US Letter portrait.
  - `{SLUG}-intro-deck.pptx`: the teacher-presented intro deck, {ns} slides (16:9), speaker notes and a Class badge on every slide.
  - `{SLUG}-intro-deck.pdf`: a PDF copy of the deck, {ns} pages.
- Thumbnails, in this order: `cover.png`, `preview-1.png`, `preview-2.png`, `preview-3.png` (all 2000 × 2000).
- Preview file: `{SLUG}-PREVIEW.pdf`, 4 watermarked pages.

TpT takes one product file, so the PDF, the .pptx and the deck PDF go up together as the ZIP (`files.product` in tpt.json; `zip_contents` lists what is inside). **No audio, video, lyrics, recordings, presets, screenshots, student work or Logic sessions are in the ZIP.**

**Page count, adding up to the PDF:** 1 cover + {n_teacher} teacher + {n_student} student + 1 terms page = {np_} pages; plus {ns} slides = {np_ + ns} for TpT's "Number of pages or slides".

## 1. Title

```
{LISTING_TITLE}
```
({nt} characters; the limit is 80.) The title leaves out Winter, Holiday, Christmas and Sleigh because TpT's Seasonal Titles notice blocked a holiday-named title on 027 (see 032, 033 and 034). "Logic Pro" sits in the first 30 characters.

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

**${PRICE}** (paid), multiple-license price ${PRICE}. The $7 in the queue, at the low end of the $7-9 holiday-kit range, for a kit with {np_} pages + {ns} slides, eight step-grid pattern cards, a swing timing table, a listening worksheet and a two-page worked example, listed in November and December.

## 8. Free or paid / free preview pages

Paid. Preview PDF (4 watermarked pages): the {CLASSES}-class pacing guide, the first step-grid card page, the straight vs swing timing table and the /{RUBRIC_TOTAL} rubric. "Number of pages or slides" is {np_ + ns} ({np_} pages + {ns} slides).

## 9. Before you click publish

- [ ] **Needs QA approval first.** This is a new kit (not yet on TpT); the Manager releases it only after a QA `**Verdict: APPROVED**`.
- [ ] Cover and previews show "HUDSON BEAT" in type; PDF footers read "© 2026 Brian Lotze · Hudson Beat · For single-classroom use".
- [ ] No school name, logo, student names or work, audio, video, lyrics, melody or Logic session anywhere (`gen.py --check` scans every output and every file in this folder).
- [ ] **No tune, no melody.** The kit holds no song, carol or notation; the teacher notes only say a teacher may name a familiar carol as a tempo or feel reference in class. Nothing to date or source.
- [ ] **Timing numbers (all recomputed in `gen.py --check`).** 16 grid steps = 4 beats x 4 sixteenths, counted 1 e & a. At 120 BPM a 16th lasts 60000 / 120 / 4 = 125 ms, a pair of 16ths 250 ms, a pair of 8ths 500 ms. Swing percent = where the second note of a pair starts: 50% = 125 ms (straight), 60% = 150 ms (25 ms late), 66% = 165 ms (40 ms late; a true triplet is 166.7 ms), 75% = 187.5 ms; for 8th pairs 60% = 300 ms and 66% = 330 ms. A 16th-note swing moves grid steps 2, 4, ... 16; an 8th-note swing moves 3, 7, 11 and 15. Worked example: 8 bars at 100 BPM = 8 x 2.4 = 19.2 s; a 16th is 150 ms; 60% swing starts the 2nd note at 180 ms (30 ms late), 66% at 198 ms (48 ms late). Groove-length helper: bars x 240 / BPM at 90 to 120 BPM.
- [ ] **Original project.** Built with `ORIGINAL = True` in `tpt/_dmp2_common/dmp2.py` (like 031, 036 and 053): no "what changed" page and the new disclosure line. The reflection page is the shared Reflection element, scored in the rubric's "Plan & Reflection" row. `dmp2.py` is unchanged.
- [ ] **Art.** The cover, previews and deck use the owner's pre-made art (`art/hero.png`, a sleigh-bell strap beside a drum-machine pad controller, no text), copied whole from `tpt/_art/next/sleigh-bell-groove/`; the file is logged in `tpt/_art/USAGE.md`. Everything else is drawn in code. Needs art: none.
- [ ] **Logic Pro names to confirm on a Mac with a current Logic.** Drum Machine Designer (instrument slot or a Library kit, pads, Quick Sampler on a pad to import or record a sound), the Step Sequencer (16 steps, rate 1/16, a velocity lane, a Swing control: all hedged "if your version has it"), Q-Swing in a region's Quantize settings (hedged), a swing or feel control on Drummer or percussion players (hedged), Cycle (C), Channel EQ, Compressor, the Mixer (X), automation (A), Command-B bounce, Option-drag to copy a region. The pages say that some swing scales start at 0 and tell students to find the even setting first. Nothing says a loop or preset of a given name exists.
- [ ] **Open questions for the owner:** (1) **Swing scale in Logic.** The kit defines swing as the percent of the pair at which the second note starts (50 = straight) and tells students how to calibrate if their control differs; please confirm on a Mac which scale the Step Sequencer's Swing uses. (2) **Title.** No Winter, Holiday, Christmas or Sleigh in the title because of TpT's seasonal-title notice (see 1). (3) **Price.** $7, as in the queue. (4) **Classes.** Three periods; the pacing page shows how to run it in two or four.
"""
    with open(os.path.join(HERE, "UPLOAD.md"), "w", encoding="utf8") as f:
        f.write(md)


def deck_art_transparent():
    """Deck art as PNGs with a transparent background (the slides are white, and a JPEG-recompressed white box would show as an off-white
    rectangle): every drawing in DRAWINGS rendered with the brand fonts at its own aspect ratio, nothing behind it."""
    import json
    bd = D.build_dir()
    jobs, out = [], {}
    for k, fn in DRAWINGS.items():
        w = DRAWING_PX.get(k, 2000)
        svg = D.body_svg(fn())
        vw, vh = map(float, re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', svg).groups())
        h = int(round(w * vh / vw)) + 2
        html = (f'<!doctype html><html><head><meta charset="utf-8"><style>{D.font_css()}html,body{{margin:0;background:transparent}}</style></head>'
                f'<body><div style="width:{w}px;height:{h}px;overflow:hidden;background:transparent">{svg}</div></body></html>')
        hp = D.write(f"deck-{k}.html", html)
        p = os.path.join(bd, f"deck-{k}.png")
        jobs.append({"html": hp, "png": p, "width": w, "height": h})
        out[k] = (p, (w, h))
    jp = D.write("deck-jobs.json", json.dumps(jobs))
    js = D.write("tr.js", TRANSPARENT_JS)
    subprocess.run(["node", js, jp], check=True, env=D.node_env())
    return [], out


if __name__ == "__main__":
    if "--check" not in sys.argv:
        write_upload()
        D.deck_art = deck_art_transparent
    D.main(sys.modules[__name__])
