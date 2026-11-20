#!/usr/bin/env python3
"""Logic Pro project kit: Eight Nights, Eight Layers (TpT 063): the teacher resource, the intro deck and the listing files.

    python3 gen.py            build everything into this folder (also writes UPLOAD.md)
    python3 gen.py --lowres   same, but square images at scale 1 and small page shots (self-check only; --check rejects it)
    python3 gen.py --check    verify content and layout: the tempo arithmetic (seconds per beat = 60 / BPM, seconds per bar in 4/4 =
                              240 / BPM, 4 bars per section, 8 sections = 32 bars, total seconds = 32 x 240 / BPM), every cell of the
                              tempo table and the section-start table (80, 90, 100, 110, 120 and 128 BPM), the worked example (100 BPM,
                              32 bars = 76.8 s), the layer map staircase (8 layers x 8 sections, layer r plays from section r on, so
                              section s has s layers), Step N references on every page, slide and UPLOAD.md, class badges against the
                              pacing page, drawings (each rendered alone on a transparent ground: no ink within 4 px of its edge),
                              the hero art, files, page and slide counts, class slots, fonts, fit and overlap, dead space, footer gap,
                              truncated slide bullets, the edges of cover.png and the previews, banned strings, tpt.json and UPLOAD.md

An ORIGINAL Hudson Beat project (dmp2.ORIGINAL = True, like 053, 057 and 061). Students build a layered arrangement in Logic Pro across
EIGHT sections of 4 bars (32 bars); each section adds one new track, so the arrangement grows from one layer to eight. The structure
is inspired by the eight nights of Hanukkah (one more candle each night); it is a music-technology project, not a religious activity.
No melody is printed or notated (the Maoz Tzur melody was NOT included: no two public-domain transcriptions could be checked from
this build environment), and no audio ships. The art on the cover, the previews and the deck is the owner's pre-made hero (art/hero.png:
a nine-candle menorah with studio gear), used whole. Everything else is drawn in code. The shared builder is ../_dmp2_common/dmp2.py.
"""
import json
import math
import os
import re
import subprocess
import sys
from fractions import Fraction
from html import escape

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "_dmp2_common"))
import dmp2 as D  # noqa: E402

ORIGINAL = True
SLUG = "eight-nights-eight-layers"
TITLE = "Eight Nights, Eight Layers"
ACCENT = "#2F7FB8"          # this product's single accent: icy blue (a shade deeper than the art's #4FA3D9, so small labels read)
ACC_LIGHT = "#DCEBF6"
PRICE = "8.00"
CLASSES = 3
GRADES_TEXT = "9–12"
GRADE_SLUGS = ["9th-grade", "10th-grade", "11th-grade", "12th-grade"]
TAGS = ["Christmas-Chanukah-Kwanzaa", "Project-based Learning", "Projects", "Activities"]     # exact entries of tpt/TAG-OPTIONS.json, none a heading
SUBJECTS = ["Music", "Computer Science - Technology", "Music Composition"]     # all in SUBJECT-OPTIONS.json, none a heading
ANSWER_KEY = None
LISTING_TITLE = "Logic Pro Layered Arrangement | 8 Sections, 8 Tracks | High School Music Tech"
DESC_START = "Layered arrangement project for high school music technology:"
DESC_MUST = ["Eight Nights, Eight Layers", "32 bars", "no audio", "seconds per bar", "76.8 seconds", "100 BPM", "Alchemy"]
ZIP_DIR = "Eight Nights, Eight Layers - Hudson Beat"
ZIP_DATE = (2026, 11, 20, 12, 0, 0)
TYPE = "Original Project"
PROJ_LINE = "Music Technology | <i>Layered Arrangement Project</i> | 3 class periods"
DECK_STRAP = "Layered arrangement"
REFLECT_ROW = "Plan &amp; Reflection"
# split so this file never contains them (the --check scan reads every file in this folder)
BANNED_EXTRA = ["Rud" + "olph", "Fro" + "sty", "Gri" + "nch", "Santa Claus " + "Is", "Jingle Bell " + "Rock", "Feliz " + "Navidad",
                "Mari" + "ah Carey", "Spoti" + "fy", "You" + "Tube", "Home " + "Alone", "Nin" + "tendo", "Ro" + "land",
                "Star " + "Wars", "Hans " + "Zimmer", "John " + "Williams", "Harry " + "Potter", "Pix" + "ar", "Lord of the " + "Rings",
                "Winter " + "Wonderland", "Let It " + "Snow", "Sleigh " + "Ride", "X" + "mas",
                "Isaac " + "Nathan", "Marcus " + "Hast"]

# ================================================================ page plan (teacher pages 2-10, student pages 11-22)
PLAN = ["cover", "howto", "overview", "setup", "pacing", "tn1", "tn2", "logicref", "example", "example2", "stair", "cards", "tempo", "plan", "mix",
        "proj1", "proj2", "proj3", "rubric", "vocab", "present", "reflect", "terms"]


def pg(k):
    return PLAN.index(k) + 1


# ================================================================ the arithmetic (exact fractions; all verified in --check)
SECTIONS = 8                                # one per night
BARS_PER = 4                                # bars in every section
TOTAL_BARS = SECTIONS * BARS_PER            # 32
TEMPOS = (80, 90, 100, 110, 120, 128)       # the tempo table's tempos
EX_BPM = 100                                # the worked example's tempo: 32 bars = 76.8 s


def spb(bpm):
    """Seconds per beat = 60 / BPM."""
    return Fraction(60, bpm)


def bar_len(bpm):
    """Seconds per bar of 4/4 = 240 / BPM (four beats)."""
    return Fraction(240, bpm)


def sec_len(bpm):
    """Seconds per section = 4 bars x 240 / BPM."""
    return BARS_PER * bar_len(bpm)


def total_s(bpm):
    """Seconds in the whole arrangement = 32 bars x 240 / BPM."""
    return TOTAL_BARS * bar_len(bpm)


def start_bar(s):
    """First bar of section s (1-based): 4 (s - 1) + 1."""
    return BARS_PER * (s - 1) + 1


def start_s(s, bpm):
    """Seconds from the start of the arrangement to the beginning of section s: (s - 1) x 4 x 240 / BPM."""
    return (s - 1) * sec_len(bpm)


def rnd(x, nd):
    """Round half up (a 5 rounds up) to nd decimals, on exact fractions."""
    s = Fraction(10) ** nd
    return Fraction(math.floor(Fraction(x) * s + Fraction(1, 2)), 1) / s


def dec(x, nd):
    return f"{float(rnd(x, nd)):.{nd}f}"


def fmt(x):
    x = float(x)
    x = round(x + 1e-9, 3)
    return f"{x:.0f}" if x == int(x) else f"{x:g}"


def playing(r, s):
    """Layer r (1 = pad ... 8 = lead) plays in section s from its own night on: the staircase."""
    return s >= r


# ================================================================ the eight layers: night, name, role, tools to try, idea
LAYERS = [
    dict(n=1, name="Pad or drone", short="Pad or drone", role="A long, soft sound that fills the background and sets the mood",
         tools="Alchemy or Retro Synth: look in the Library for a pad patch with a slow attack",
         idea="Hold one chord, or one or two notes, for a whole bar or longer; follow your four chords"),
    dict(n=2, name="Bass", short="Bass", role="The low line under everything; it usually follows the root of each chord",
         tools="Retro Synth or Alchemy bass patch; the Bass Player Session Player if your version has it",
         idea="Play one long note per bar on each chord’s root, then try a simple repeating pattern"),
    dict(n=3, name="Kick and clap", short="Kick and clap", role="The steady backbone: a low kick and a sharp clap mark the beat",
         tools="Drum Machine Designer, Quick Sampler, or the Drummer Session Player if your version has it",
         idea="Kick on beats 1 and 3, clap on beats 2 and 4"),
    dict(n=4, name="Hi-hat or shaker", short="Hi-hat or shaker", role="Small, quick sounds that keep the pulse moving",
         tools="Drum Machine Designer or Quick Sampler; the Step Sequencer if your version has it",
         idea="Eighth notes: two hits in every beat, counted 1 and 2 and 3 and 4 and"),
    dict(n=5, name="Chord stabs", short="Chord stabs", role="Short, punchy chords that add harmony and rhythm",
         tools="Any keyboard or synth Software Instrument with a short, quick release",
         idea="Play each chord on an off-beat, the “and” of a beat, and let it stop quickly"),
    dict(n=6, name="Arpeggio", short="Arpeggio", role="The notes of a chord played one after another as a flowing pattern",
         tools="The Arpeggiator MIDI plug-in on a Software Instrument track if your version has it, or click the notes in",
         idea="Take the notes of the chord that is playing and run them up and down in eighth notes"),
    dict(n=7, name="Counter-melody", short="Counter-melody", role="A second melody that moves in the spaces and weaves around the main one",
         tools="Alchemy or Retro Synth, or any Software Instrument whose sound stands out from the pad",
         idea="Write a short pattern of 4 to 8 notes, long and short, with rests where the lead will play"),
    dict(n=8, name="Lead", short="Lead", role="The main melody, clear and bright, at the top of the arrangement: the climax",
         tools="An Alchemy or Retro Synth lead patch; a melody you write, or any melody you have the right to use",
         idea="Play it in the last section only; make it the loudest and brightest layer in the mix"),
]
LAYER_NAMES = [l["name"] for l in LAYERS]

# ================================================================ the project text (original; students read these pages)
CULTURE = ("Hanukkah (also spelled Chanukah) is an eight-night Jewish festival of lights. It remembers the rededication of the Second Temple in Jerusalem in the "
           "2nd century BCE, and it begins on the 25th day of the Hebrew month of Kislev, which falls in late November or December. A hanukkiah, or menorah, "
           "has nine branches: eight for the nights and one more for the shamash, the “helper” candle that lights the others. One new candle is added each night.")
INSPIRE = ("This project borrows only that pattern as inspiration: one new layer for every section, so the music grows from one layer to eight. It is a "
           "music-technology project, not a religious activity, and it suits any class. Students may choose a different theme with eight steps, such as eight "
           "colors of a sunrise or eight stops on a journey. Families celebrate in many ways, and this kit does not say how anyone should.")
OVERVIEW = ("Build an arrangement that grows. In Logic Pro, make 32 bars of music in eight sections of 4 bars each. Section 1 has one layer, a pad or drone. "
            "Every new section adds one more track: bass, kick and clap, hi-hat or shaker, chord stabs, an arpeggio, a counter-melody and finally a lead, so "
            "section 8 plays all eight at once. Choose a tempo with the tempo table: one bar of 4/4 lasts 240 ÷ BPM seconds, so the whole piece lasts "
            "32 × 240 ÷ BPM seconds. Then mix it so each new layer is heard when it enters. Nobody needs to read music, and no melody is given.")
GOALS = ["Plan an arrangement of eight 4-bar sections in which each section adds exactly one new layer to the ones already playing",
         "Use seconds per beat = 60 ÷ BPM and seconds per bar = 240 ÷ BPM in 4/4 to find how long the piece is and when each layer enters",
         "Build eight layers in Logic Pro, each with its own sound and its own job: pad, bass, kick and clap, hi-hat, chord stabs, arpeggio, counter-melody and lead",
         "Mix the arrangement so every layer can be heard when it joins, then bounce it and reflect on the choices"]
VOCAB = [("Layer", "One track in an arrangement with its own sound and its own job, such as a bass line or a hi-hat pattern"),
         ("Section", "A block of bars, here 4, in which the music repeats; in this project a new layer joins at the start of each section"),
         ("Arrangement", "The way layers and sections are put together over time so that a piece builds, thins out or changes"),
         ("Arpeggio", "The notes of a chord played one after another instead of all together, usually as a repeating pattern")]
REQS = ["Choose a key and a tempo from 80 to 128 BPM in 4/4, and show the arithmetic with the tempo table (page @TEMPO)",
        "Plan eight layers, one for each section, on the arrangement plan (pages @CARDS and @PLAN)",
        "Make 32 bars in eight sections of 4 bars, with a marker at the start of every section (page @LOGICREF)",
        "Add exactly one new layer at the start of each section, so section 1 has one layer and section 8 has all eight (page @STAIR)",
        "Give every layer its own sound and its own job: no two layers may do the same thing",
        "Mix with level, pan and automation so each new layer can be heard when it enters (page @MIX), then bounce",
        "Reflect on your choices (page @REFLECT)"]
FILE_NAME = "“Your Name – Eight Layers”"
STEP_NAMES = ["Choose key and tempo", "Plan the layers", "Set up Logic", "Build nights 1 to 4", "Build nights 5 to 8", "Mix and bounce", "Present &amp; get feedback"]
STEPS = ["<b>Choose key and tempo</b> — Pick a key and four chords, then use the tempo table (page @TEMPO) to choose a tempo from 80 to 128 BPM and work out how long your 32 bars last",
         "<b>Plan the layers</b> — Read the eight layer cards (page @CARDS) and fill in the arrangement plan (page @PLAN): which sound and which pattern for each night",
         "<b>Set up Logic</b> — Open a project at your tempo in 4/4, make a 4-bar region of your four chords, and put a marker at the start of each of the eight sections (Logic quick reference: page @LOGICREF)",
         "<b>Build nights 1 to 4</b> — Build the pad, the bass, the kick and clap and the hi-hat or shaker, one at the start of each of sections 1 to 4",
         "<b>Build nights 5 to 8</b> — Add the chord stabs, the arpeggio, the counter-melody and the lead, one at the start of each of sections 5 to 8, until all eight play together",
         "<b>Mix and bounce</b> — Set levels, pan and automation with the mix checklist (page @MIX), then bounce your 32 bars and name the file as on the checklist",
         "<b>Present &amp; get feedback</b> — Write three questions you want classmates to answer about your arrangement. Play it, point out each new layer as it enters, "
         "and answer at least 2 of each classmate’s questions. Then reflect (page @REFLECT)."]
TIPS = ["Get the first four bars sounding good before you add anything. Every later layer sits on top of them.",
        "Leave space. A layer that plays all the time is harder to hear than one that rests now and then.",
        "Give the new layer the spotlight: turn it up a little in its first section, then settle it back into the mix.",
        "Save a new version of your project at the end of each night’s work, so you can always go back."]
CHECK = ["Bounced .mp3 or .wav of your arrangement handed in, 32 bars long",
         "Zipped .logicx project file handed in",
         f"Files named correctly: {FILE_NAME}",
         "Arrangement plan and tempo table work handed in",
         "Rubric self-score done (page @RUBRIC)",
         "I can name each layer and say when it enters, in bars and in seconds"]
RUBRIC_NOTE = "Each category is scored 1–5. Score yourself first; the final grade is the average of your score and your teacher’s."
LEVELS = [1, 2, 3, 4, 5]
RUBRIC = [
    ("Layer Build", ["Two or fewer layers", "Fewer than 6 layers, or layers that do not join one at a time",
                     "Eight layers, but some join in the wrong section or two join at once",
                     "Eight layers; exactly one new layer joins at the start of each section, so section 8 plays all eight",
                     "Eight layers join in the right order and each entrance is marked, shaped and easy to hear"]),
    ("Tempo & Timing Math", ["No tempo and no arithmetic", "A tempo is chosen, but the lengths are missing or wrong",
                             "Seconds per bar and the total length shown, with small errors",
                             "A tempo chosen on purpose; seconds per bar, per section and in total all correct",
                             "Correct math, entrance times for every layer and a comparison of two tempos, with a reason"]),
    ("Sound & Roles", ["One sound only", "Some layers sound alike or do the same job",
                       "Every layer has a sound; a few jobs overlap",
                       "Every layer has its own sound and its own job; the pad, bass and drums fit the chords",
                       "Sounds are chosen with care; each layer’s pattern leaves room for the others"]),
    ("Arrangement & Mix", ["Layers are too loud or too quiet to tell apart", "A few layers can be heard; others are buried or clip",
                           "Most layers can be heard; some balance problems",
                           "Every layer can be heard when it enters; levels, pan and automation are used; no clipping",
                           "The build feels shaped; the low end is clear and the lead stands out in section 8"]),
    ("Plan & Reflection", ["Plans, presentation or reflection missing", "Thin plan; little to say about choices",
                           "Plan and reflection complete, with basic detail", "Clear plan; thoughtful reflection and good answers to questions",
                           "Insightful reflection and a polished, confident presentation"]),
]
RUBRIC_TOTAL = 25
RUBRIC_SHORT = [ds[4] for _, ds in RUBRIC]
RUBRIC_SLIDE_LINE = "Scored 1–5 · final grade = average of your score and mine, out of 25"
RUBRIC_ROW_PITCH = 0.86
RUBRIC_LINE_Y = 6.3

TN_REINFORCES = ("Teaches how a piece is built up in layers. Students learn what each layer in an arrangement is for, how to turn a tempo into bars and seconds with "
                 "simple arithmetic, and how to mix so a new layer can be heard, all in Logic Pro, with a plan that grows one layer at a time.")
STRUGGLES = ["The layers blur together: take a layer away, turn the pad down, and give each layer its own range, with the bass low and the lead high (page @MIX).",
             "The arithmetic looks hard: work one entrance aloud with the formula start time = (section − 1) × 4 × (240 ÷ BPM), and let students check it by "
             "reading the time of a marker in Logic (page @TEMPO).",
             "A new layer starts late or early: check that the region begins exactly on the first bar of its section, and that the markers are at bars 1, 5, 9, 13, 17, 21, 25 and 29 (page @LOGICREF).",
             "A student cannot find a pattern for a layer: use the idea on its layer card (page @CARDS), or start with one note per bar and add one more idea only after it sounds right."]
VAR_EASY = ("Use a pad, a bass, a kick and clap and a lead only, four layers over four 8-bar sections, with a tempo of 100 BPM, where the 32 bars last exactly "
            "76.8 seconds (page " + str(pg("tempo")) + ").")
VAR_HARD = ("Plan two tempos, such as 100 and 120 BPM, and compare when each layer enters (page " + str(pg("tempo")) + "). Or take layers away again from section 9 on, "
            "so the arrangement builds to eight and then thins back to one, for a 64-bar piece.")
RESOURCES = [("The layer map and layer cards (pages @STAIR–@CARDS)",
              "A staircase grid that shows which layers play in which sections, and eight cards that give each layer a role, tools to try and a pattern idea."),
             ("Tempo table (page @TEMPO)",
              "Seconds per beat, per bar and per section, the length of 32 bars and the time every section begins, at 80, 90, 100, 110, 120 and 128 BPM; every number is computed."),
             ("Arrangement plan and mix checklist (pages @PLAN and @MIX)",
              "A plan sheet for the eight layers, a grid to shade, and a checklist for levels, pan, low end, entrances and the bounce."),
             ("Worked example (pages @EXAMPLE–@EXAMPLE2)",
              "An invented plan at 100 BPM: 32 bars last 76.8 seconds, and the eight layers enter at 0, 9.6, 19.2, 28.8, 38.4, 48, 57.6 and 67.2 seconds. A model, not a template.")]
TN_NOTE = ("A good listening day: play each student’s arrangement and ask the class to hold up fingers for how many layers they hear at the start of each section. "
           "The count should be 1, 2, 3 and so on up to 8. This kit prints no melody and names no songs or artists.")
GRADING = ["The rubric: five categories, each scored 1–5, /25 (page @RUBRIC). Students score themselves first; the final grade is the "
           "average of their score and yours.",
           "Layer Build (rubric row 1): play the bounce and count the layers at the start of each section: 1, 2, 3 up to 8 (page @STAIR).",
           "Tempo & Timing Math (rubric row 2): recompute one entrance time with the student: (section − 1) × 4 × (240 ÷ BPM) (page @TEMPO).",
           "Sound & Roles (rubric row 3): open the project and compare the layers with the plan (page @PLAN). Does every layer have its own job?",
           "Arrangement & Mix (rubric row 4): listen for each entrance, check the meter for clipping and listen to the low end (page @MIX).",
           "Plan & Reflection (rubric row 5): the arrangement plan, the feedback questions and the Reflection page (page @REFLECT) are the evidence."]
PACING = [
    {"n": 1, "owner": "Hear the idea, plan the eight layers and pick a tempo.",
     "do": "Slides 1–6: the think-and-share, what the project is, the three classes, the layer map, the eight layers and the inspiration. Hand out the layer map, "
           "the layer cards, the tempo table and the arrangement plan. Before they leave, students have a key, four chords, a tempo and a plan for all eight layers.",
     "slides": (1, 6), "pages": ["stair", "cards", "tempo", "plan", "proj1", "proj2", "proj3", "vocab"],
     "deck": "Count the layers · the layer map · the inspiration"},
    {"n": 2, "owner": "Set up Logic and build the first six layers.",
     "do": "Slides 7–9: seconds and bars, the eight layers and building in Logic. Work one entrance time aloud with the formula. Students set up Logic with a marker at "
           "every section, then build nights 1 to 6, one layer per section. Walk the room with one question: which layer is new in this section?",
     "slides": (7, 9), "pages": ["cards", "plan", "present"], "deck": "Seconds to bars · eight layers · build it in Logic"},
    {"n": 3, "owner": "Finish the layers, mix, bounce, present and reflect.",
     "do": "Slides 10–14: the worked example, what to turn in, the rubric and presentation day. Students add the counter-melody and the lead, mix with the checklist, "
           "bounce, then present.",
     "slides": (10, 14), "pages": ["plan", "mix", "rubric", "present", "reflect"], "deck": "32 bars, 76.8 seconds · checklist · rubric · presentations"},
]
PACING_EXTRA = (
    '<div class="cols" style="margin-top:4pt;gap:14pt"><div class="box acc-b"><span class="k">The one thing to do on Class 1</span>'
    '<p style="margin:0;font-size:10.6pt">Make sure every student leaves with a key, four chords, a tempo and the plan for all eight layers, so that Class 2 '
    'is all building. Check each tempo against the tempo table before they go.</p></div>'
    '<div class="box"><span class="k">With two or four periods</span><p style="margin:0;font-size:10.6pt"><b>Two classes:</b> Class 1 is the plan and the first four layers; '
    'Class 2 is the last four layers, the mix and short presentations. <b>Four classes:</b> keep Classes 1 and 2, then spend Class 3 on nights 7 and 8 and the mix, and '
    'Class 4 on bouncing, presentations and reflection.</p></div></div>')
PACING_SIZE = 10.6

SONG_NOTE = ("No audio, recordings, lyrics or melodies are included or notated, and no songs, artists or albums are named. Students make every "
             "sound themselves, from the instruments, samples and loops in Logic.")
MELODY_NOTE = ("The lead in section 8 can be a melody the student writes, or any melody the student has the right to use. A class that would like a traditional "
               "Hanukkah song, such as Ma’oz Tzur, can bring a notated copy from a school or library collection and check that it is in the public domain. "
               "This kit does not print a melody chart.")
CREDITS = ["The layer map, the layer cards, the tempo tables, the arrangement plan, the mix checklist and the worked example: original work, Hudson Beat. "
           "No melodies, lyrics, recordings or published editions are included.",
           "The cover illustration was made with digital and AI tools. No audio, video, album art, screenshots, presets, templates, links or "
           "chart data from other sources are included. No student work is included. Facts about the festival: Encyclopaedia Britannica and the Jewish "
           "Virtual Library entries on Hanukkah."]
LOGIC_INTRO = ("Where to find the tools an Eight Nights, Eight Layers arrangement is likely to use. Demonstrate what your class needs on Classes 1 and 2 and then "
               "let students work. Names are from current Logic Pro versions; labels move between versions, so check yours.")
LOGIC_REF = [("Project and tempo", "File › New…, then a Software Instrument track to start. Set the project tempo in the control bar to the number on your "
              "tempo table and keep the time signature at 4/4. The timing arithmetic only works at that tempo, so set it first. Set a cycle from bar 1 to bar 33 to hear all 32 bars."),
             ("Sections with markers", "Show the Marker global track (the Global Tracks controls or the View menu). Add a marker with the plus (+) button in that track, "
              "or with a Create Marker key command if your version has one, then drag or type it to bars 1, 5, 9, 13, 17, 21, 25 and 29. Name them Night 1 to Night 8."),
             ("Repeat a 4-bar idea", "Record or click in your four chords for 4 bars, then repeat the region to bar 33: use the Loop option for a selected region (look in the region "
              "inspector or press L), or drag the upper right corner of the region. Delete or mute the regions of layers that have not joined yet."),
             ("Session Players", "If your version has Session Players, add a Drummer or a Bass Player track and let it follow your chords; choose a style, then check that it "
              "starts in the right bar. If your version does not have them, build the same parts with the instruments below."),
             ("Pad and lead", "Make a Software Instrument track and open Alchemy or Retro Synth, then look in the Library for a soft pad with a slow attack, or a bright lead. "
              "Play long chords for the pad. Stay in key with the white keys only, or switch on Scale Quantize if your version has it."),
             ("Kick, clap and hi-hat", "Make a Drum Machine Designer track (click the instrument slot and choose it), or use Quick Sampler pads. Click the hits in on the "
              "beats you planned. If your version has the Step Sequencer, it is a quick way to draw a pattern of hits."),
             ("Arpeggio", "Put the Arpeggiator MIDI plug-in in the MIDI FX slot of a Software Instrument channel strip, if your version has it, and hold a chord. Otherwise click "
              "the notes of the chord in one after another, in eighth notes."),
             ("Bass, stabs and counter-melody", "Use Retro Synth or Alchemy patches (a bass patch low, a stab patch short). Keep the bass below the other layers, play the stabs "
              "on the off-beats and leave rests in the counter-melody."),
             ("Mixer, automation and bounce", "Press X for the Mixer and set levels and pan. Press A to show automation, choose a parameter such as track volume and click points "
              "to draw it: fade a new layer in, or push it up a little in its first section. Then File › Bounce › Project or Section (Command-B), MP3 or WAV, for the 32 bars. "
              "In Finder, Control-click the .logicx and choose Compress.")]
PRESENT_CHECK = [f"Files named {FILE_NAME}; the .mp3 or .wav and the zipped .logicx handed in",
                 "Reflection page done (page @REFLECT)", "Three questions for classmates written",
                 "Rubric self-score done (page @RUBRIC)"]
VOCAB_PROMPT = "Where it shows up in my arrangement:"
TN1_EXTRA = (
    '<div class="box acc-b" style="margin-top:4pt"><span class="k">Where this kit helps with each struggle</span><ul style="margin:0">'
    '<li style="font-size:12pt;margin-bottom:3pt">Layers that blur: the layer cards (page @CARDS) give each layer a range and a job, and the mix checklist (page @MIX) covers pan and the low end.</li>'
    '<li style="font-size:12pt;margin-bottom:3pt">The arithmetic: the tempo table (page @TEMPO) gives every section start time at 6 tempos, and the worked example (pages @EXAMPLE–@EXAMPLE2) shows each step.</li>'
    '<li style="font-size:12pt;margin-bottom:3pt">Late or early entrances: the Logic quick reference (page @LOGICREF) covers markers and repeating a region.</li>'
    '<li style="font-size:12pt;margin-bottom:0">Not sure what to play: every card has a pattern idea, and the layer map (page @STAIR) shows what is already playing.</li></ul></div>')
TN1_SIZE = 12.0
PROJ_SIZE = 11.8
VOCAB_GAP = 22
LOGIC_SIZE = 9.3
PROJ1_EXTRA = ""
RUBRIC_EXTRA = ""

# ================================================================ the worked example: an invented arrangement at 100 BPM
EX_KEY = "A minor"
EX_CHORDS = ["Am", "F", "C", "G"]
EX_BAR_S = bar_len(EX_BPM)                  # 2.4 s
EX_SEC_S = sec_len(EX_BPM)                  # 9.6 s
EX_LAYER_PATTERNS = ["One long chord per bar, following Am, F, C, G", "The root of each chord, one note per bar: A, F, C, G",
                     "Kick on beats 1 and 3, clap on beats 2 and 4", "Closed hi-hat in eighth notes: 8 hits in every bar, 32 in a section",
                     "Each chord struck once on the “and” of beat 2", "The three notes of each chord, up and down in eighth notes",
                     "A 6-note answer pattern with rests in bars 3 and 4", "A 4-bar tune in A minor, the loudest layer"]
EX_WEAK = "I will add some sounds to a beat, and it will get bigger."
EX_STRONG = ("My arrangement is in A minor at 100 BPM in 4/4, with the chords Am, F, C and G, one chord per bar, repeated in every section. One bar lasts 240 ÷ 100 = 2.4 seconds, "
             "so a 4-bar section lasts 9.6 seconds and all 32 bars last 76.8 seconds. Night 1 is a pad. Each new section adds one layer: bass, kick and clap, hi-hat, chord stabs, "
             "an arpeggio, a counter-melody and, in section 8, the lead. The layers enter at 0, 9.6, 19.2, 28.8, 38.4, 48, 57.6 and 67.2 seconds, and section 8 plays all eight layers.")
EX_QUESTIONS = ["Which new layer was easiest to hear when it entered, and why?",
                "Did the arrangement feel like it was building? Where did it feel biggest?",
                "Which layer would you take away first, and why?"]
EX_AUTO = "Each new layer fades up over its first bar; the pad filter opens a little in every section; the lead is 2 dB above the counter-melody"


# ================================================================ drawings (all in code, labels logged for the fit check)
def padded(body, W, H, M=10):
    """Wrap a drawing's body with M units of clear padding on all four sides (wider than the thickest outer stroke), so no edge pixel is ever inked."""
    return f'<g transform="translate({M},{M})">{body}</g>', W + 2 * M, H + 2 * M


def stair_body(W=1600, with_time=False, name="stair", lf=24, lh=54):
    """The layer map: 8 layers (rows) x 8 sections (columns). Layer r plays from section r on, so each section adds exactly one row.
    Dark blue = the layer that joins in this section, light blue = layers already playing, white = not yet."""
    gx = 370
    pw = W - gx - 30
    cw = pw / SECTIONS
    hh = 98 if with_time else 70
    out = []
    for s in range(1, SECTIONS + 1):
        cx = gx + (s - 0.5) * cw
        l1 = f"NIGHT {s}"
        l2 = f"bars {start_bar(s)}–{start_bar(s) + BARS_PER - 1}"
        out.append(D.t_(cx, 30, l1, 26, 700))
        D.lab(name + " heads", l1, 26, cw - 14)
        out.append(D.t_(cx, 58, l2, 20, 500, fill_="#555"))
        D.lab(name + " bars", l2, 20, cw - 14)
        if with_time:
            l3 = f"{fmt(start_s(s, EX_BPM))}–{fmt(start_s(s + 1, EX_BPM))} s"
            out.append(D.t_(cx, 86, l3, 20, 500, fill_=ACCENT))
            D.lab(name + " times", l3, 20, cw - 14)
    out.append(D.t_(gx - 16, hh - 12, "LAYER", lf - 2, 700, anchor="end", fill_=ACCENT))
    y0 = hh + 14
    gap = 6
    for r, L in enumerate(LAYERS, start=1):
        yy = y0 + (r - 1) * (lh + gap)
        lbl = f"{r} {L['name']}".upper()
        out.append(D.t_(gx - 16, yy + lh / 2 + lf * .35, lbl, lf, 700, anchor="end"))
        D.lab(name + " rows", lbl, lf, gx - 30)
        for s in range(1, SECTIONS + 1):
            x = gx + (s - 1) * cw + 3
            if playing(r, s):
                new = s == r
                out.append(f'<rect x="{x:.1f}" y="{yy}" width="{cw - 6:.1f}" height="{lh}" rx="6" fill="{ACCENT if new else ACC_LIGHT}" stroke="#000" stroke-width="2.5"/>')
                if new:
                    out.append(D.t_(x + (cw - 6) / 2, yy + lh / 2 + 8, "NEW", 24, 700, fill_="#fff"))
                    D.lab(name + " new", "NEW", 24, cw - 24)
            else:
                out.append(f'<rect x="{x:.1f}" y="{yy}" width="{cw - 6:.1f}" height="{lh}" rx="6" fill="#fff" stroke="#bbb" stroke-width="1.5"/>')
    yb = y0 + SECTIONS * (lh + gap) + 6
    out.append(f'<line x1="{gx}" y1="{yb - 6}" x2="{gx + pw:.1f}" y2="{yb - 6}" stroke="#000" stroke-width="2.5"/>')
    lbl = "LAYERS PLAYING"
    out.append(D.t_(gx - 16, yb + 34, lbl, lf, 700, anchor="end", fill_=ACCENT))
    D.lab(name + " rows", lbl, lf, gx - 30)
    for s in range(1, SECTIONS + 1):
        n = sum(1 for r in range(1, SECTIONS + 1) if playing(r, s))
        out.append(D.t_(gx + (s - 0.5) * cw, yb + 36, str(n), 34, 700))
    if with_time:
        cap = f"{TOTAL_BARS} bars at {EX_BPM} BPM in 4/4: {TOTAL_BARS} × {fmt(EX_BAR_S)} = {fmt(total_s(EX_BPM))} seconds"
    else:
        cap = "Dark blue: the layer that joins. Light blue: layers already playing. The bottom row counts the layers."
    out.append(D.t_(gx + pw / 2, yb + 86, cap, 24, 500))
    D.lab(name + " cap", cap, 24, pw)
    return padded("".join(out), W, yb + 100, 14)


def time_body(W=1600, name="time"):
    """The same eight sections at 100 BPM (76.8 s) and at 120 BPM (64 s), drawn to one time scale."""
    gx = 270
    pw = W - gx - 30
    scale = pw / float(total_s(100))
    out = []
    rows = [(100, 20), (120, 175)]
    for bpm, y in rows:
        lb = f"{bpm} BPM"
        out.append(D.t_(gx - 20, y + 36, lb, 34, 700, anchor="end"))
        D.lab(name + " rows", lb, 34, gx - 40)
        l2 = f"{fmt(total_s(bpm))} s in all"
        out.append(D.t_(gx - 20, y + 66, l2, 22, 500, anchor="end", fill_=ACCENT))
        D.lab(name + " totals", l2, 22, gx - 40)
        sl = float(sec_len(bpm))
        for s in range(1, SECTIONS + 1):
            x0 = gx + float(start_s(s, bpm)) * scale
            out.append(f'<rect x="{x0 + 2:.1f}" y="{y}" width="{sl * scale - 4:.1f}" height="70" rx="8" fill="{ACC_LIGHT if s % 2 else "#fff"}" stroke="#000" stroke-width="2.5"/>')
            out.append(D.t_(x0 + sl * scale / 2, y + 48, str(s), 32, 700))
        for s in range(1, SECTIONS + 2):
            x = gx + float(start_s(s, bpm)) * scale
            out.append(f'<line x1="{x:.1f}" y1="{y + 76}" x2="{x:.1f}" y2="{y + 86}" stroke="#000" stroke-width="2"/>')
            lbl = fmt(start_s(s, bpm))
            anc = "start" if s == 1 else ("end" if s == SECTIONS + 1 else "middle")
            out.append(D.t_(x + (2 if s == 1 else (-2 if s == SECTIONS + 1 else 0)), y + 110, lbl, 22, 500, anchor=anc))
            D.lab(name + " ticks", lbl, 22, 80)
    cap = "Each block is one section of 4 bars. Numbers under the blocks are seconds. One bar = 240 ÷ BPM seconds."
    out.append(D.t_(gx + pw / 2, 335, cap, 24, 500))
    D.lab(name + " cap", cap, 24, pw)
    return padded("".join(out), W, 350, 14)


CARD_LINES = [("Long and soft,", "it sets the mood"), ("The low line that", "anchors the chords"), ("The backbone:", "low kick, sharp clap"),
              ("Small, quick sounds", "that keep it moving"), ("Short, punchy chords", "on the off-beats"), ("A chord played", "one note at a time"),
              ("A second melody that", "weaves in the spaces"), ("The main tune:", "the climax")]


def cards_body(W=1640, name="cards"):
    """Eight small cards, four to a row: night number, layer name and a two-line role."""
    cw, ch, gap = 380, 236, 40
    out = []
    for i, L in enumerate(LAYERS):
        x = (i % 4) * (cw + gap)
        y = (i // 4) * (ch + 30)
        g = [f'<rect x="0" y="0" width="{cw}" height="{ch}" rx="16" fill="#fff" stroke="#000" stroke-width="3"/>',
             f'<circle cx="{cw / 2}" cy="52" r="32" fill="{ACCENT}" stroke="#000" stroke-width="3"/>', D.t_(cw / 2, 64, str(L["n"]), 36, 700, fill_="#fff")]
        nm = L["name"].upper()
        g.append(D.t_(cw / 2, 128, nm, 32, 700))
        D.lab(name + " names", nm, 32, cw - 30)
        for j, ln in enumerate(CARD_LINES[i]):
            g.append(D.t_(cw / 2, 170 + j * 30, ln, 22, 500))
            D.lab(name + " text", ln, 22, cw - 30)
        out.append(f'<g transform="translate({x},{y})">{"".join(g)}</g>')
    return padded("".join(out), 4 * cw + 3 * gap, 2 * ch + 30, 12)


def hero_body():
    """The owner's pre-made art (art/hero.png, used whole). The viewBox only trims fully transparent margin: the art's own pixels
    (x 63-1337, y 67-1366 of 1400) stay at least 40 units inside it, which --check proves from the file."""
    return (f'<image href="../art/hero.png" x="{-HX}" y="{-HY}" width="1400" height="1400"/>', HW, HH)


HX, HY, HW, HH = 20, 25, 1360, 1390

DRAWINGS = {"hero": hero_body, "stair": lambda: stair_body(1600, False, "stair deck"), "time": lambda: time_body(1600, "time deck"),
            "cards": lambda: cards_body(1640, "cards deck"), "map": lambda: stair_body(1600, True, "map deck")}
DRAWING_PX = {"hero": 1340, "stair": 2000, "time": 2000, "cards": 2000, "map": 2000}
SIDE = {"stair": ["Eight sections of 4 bars", "Section 1 has one layer", "Every section adds one more", "Section 8 plays all eight"],
        "time": ["Seconds per bar = 240 ÷ BPM", "A section is 4 bars", "32 bars = 32 × 240 ÷ BPM seconds", "At 100 BPM: 76.8 seconds"],
        "cards": ["Every layer has its own job", "Low layers anchor the beat", "High layers carry the tune", "Leave rests for the others"],
        "map": ["An invented plan at 100 BPM", "Each section lasts 9.6 seconds", "Section 8 plays all eight layers", "The whole piece lasts 76.8 seconds"]}
# extra drawings used on pages only, rendered alone on a transparent ground by --check as well
PAGE_DRAWINGS = {"stair-page": lambda: stair_body(1500, False, "stair page", 24, 46), "map-page": lambda: stair_body(1500, True, "map page", 24, 46),
                 "time-page": lambda: time_body(1500, "time page")}


def label_extras():
    stair_body(1500, False, "stair page", 24, 46)
    stair_body(1500, True, "map page", 24, 46)
    time_body(1500, "time page")


# ================================================================ intro deck: (class, kind, title, body, speaker notes)
SLIDES = [
    (1, "title", "Eight Nights, Eight Layers", "One new layer in every section.",
     "Class 1, the first minute. No audio is included in this deck. Open with the idea: you will build 32 bars of music in Logic Pro in eight sections, and every section adds one "
     "new layer, so the arrangement grows from one layer to eight. Students choose a tempo, plan the layers, build them and mix them. Nobody needs to play an instrument or read "
     "music, and no melody is given."),
    (1, "listen", "Count the layers", "Think, then share|Teacher: read aloud, no audio plays. One quiet, steady sound begins. Every few seconds, one more joins.|"
     "What changes in the feeling with each new sound?|Which sound would you add first, and which last?|When does it feel biggest?",
     "Read the scene aloud slowly and ask the three questions. Take a few answers. Nothing is played from a speaker. Students will say that the music feels fuller, "
     "more exciting or more crowded as sounds are added. Write their words on the board. The project turns that feeling into a plan: eight layers, each with a job, each "
     "entering at a planned moment, so that the build can be heard."),
    (1, "bullets", "What is Eight Nights, Eight Layers?", "Build 32 bars in eight sections|One new layer in each section|Choose a tempo and do the timing math|Mix it so every layer is heard",
     "The project in four lines. Every student builds 32 bars of music in Logic Pro: eight sections of 4 bars. Section 1 has one layer and each new section adds exactly one more, so "
     "section 8 plays all eight. Students choose a tempo, work out when each layer enters, and mix so that every layer can be heard. There is no melody to learn and no audio ships: "
     "students make every sound."),
    (1, "days", "Three classes", "",
     "The shape of the project. Class 1: hook, the layer map, the eight layers, the tempo and the plan. Class 2: set up Logic and build the first six layers. Class 3: finish "
     "the layers, mix, bounce, present and reflect. With two classes, plan and build four layers in Class 1 and finish in Class 2; with four, add a day for the mix and the "
     "presentations. Hand out the layer map, the layer cards, the tempo table and the plan now."),
    (1, "pic", "Eight sections, eight layers", "stair",
     f"Class 1. This is the layer map: eight rows for the layers and eight columns for the sections. Dark blue marks the layer that joins in a section, light blue the layers that "
     f"are already playing. Ask the class to count the layers in each section: 1, 2, 3, up to 8. Each section adds exactly one layer, so the map is a staircase. The layer map is "
     f"on page {pg('stair')}, and the eight layer cards are on page {pg('cards')}."),
    (1, "bullets", "Where the idea comes from", "Hanukkah is an eight-night festival of lights|A hanukkiah has nine branches: eight plus the shamash|One new candle is added each night|"
     "We borrow only the pattern: one new layer per section|Any theme with eight steps works too",
     "Class 1, one minute, said plainly. Hanukkah, also spelled Chanukah, is an eight-night Jewish festival of lights that remembers the rededication of the Second Temple in "
     "Jerusalem in the 2nd century BCE. A hanukkiah, or menorah, has nine branches: eight for the nights and one for the shamash, the helper candle. One new candle is added each "
     "night. This project borrows only that pattern as inspiration. It is a music-technology project, not a religious activity, and students may pick another eight-step theme."),
    (2, "pic", "Seconds and bars", "time",
     f"Class 2. Pick a tempo and the clock becomes a grid. Seconds per beat is 60 divided by the tempo, and seconds per bar in 4/4 is 240 divided by the tempo. A section is 4 bars, "
     f"so at 100 BPM it lasts 9.6 seconds and all 32 bars last 76.8 seconds. At 120 BPM a bar lasts 2 seconds and the whole piece lasts 64 seconds. The tempo table is on "
     f"page {pg('tempo')}."),
    (2, "pic", "Eight layers", "cards",
     f"Class 2. Each layer has its own job. The pad or drone sets the mood, the bass anchors the chords, the kick and clap mark the beat, the hi-hat or shaker keeps the pulse "
     f"moving, the chord stabs add rhythm, the arpeggio flows, the counter-melody weaves in the spaces and the lead is the main melody. Ask which layer the class would "
     f"remove first. The full cards, with tools to try and a pattern idea for each, are on page {pg('cards')}."),
    (2, "steps", "Build it in Logic", "Set the tempo; keep 4/4|A marker at the start of each section|Repeat your 4 bars to bar 33|Add one new layer per section|Automate, mix and bounce",
     f"Class 2. Demonstrate on the projector. Set the tempo from the tempo table and keep 4/4. Put a marker at bars 1, 5, 9, 13, 17, 21, 25 and 29, then make the first 4 bars and "
     f"repeat them to bar 33. Add one new layer at the start of each section. Menu names and button places move between Logic versions; the quick reference on page "
     f"{pg('logicref')} hedges where they do, and says which tools to use only if your version has them."),
    (3, "pic", "32 bars, 76.8 seconds", "map",
     f"Class 3. An invented plan described on paper; nothing here is audio. At 100 BPM one bar is 240 divided by 100, which is 2.4 seconds, so a section is 9.6 seconds and 32 bars "
     f"are 76.8 seconds. The layers enter at 0, 9.6, 19.2, 28.8, 38.4, 48, 57.6 and 67.2 seconds, and section 8 plays all eight. Students plan their own on the arrangement plan, "
     f"page {pg('plan')}; the full example is on pages {pg('example')} and {pg('example2')}."),
    (3, "check", "What you turn in", "Bounced .mp3 or .wav, 32 bars long|Zipped .logicx project|Named: Your Name – Eight Layers|Arrangement plan and tempo table work|"
     "Reflection page|Rubric self-score and three questions",
     "Class 3. The submission checklist, shortened to fit the slide. Show where students hand in. The file name is Your Name, then Eight Layers. Check the length before "
     "students bounce: the bounce should run 32 bars, which is 76.8 seconds at 100 BPM or 64 seconds at 120 BPM."),
    (3, "rubric", "How it’s scored", "",
     "The rubric: five categories, each scored 1 to 5, for a total out of 25. Students score themselves first; the final grade is the average of their score and yours. "
     "The slide reads the 5 column of each category aloud. Hand out the rubric page so students can self-score before they present."),
    (3, "bullets", "Presentation day", "Play your 32 bars from the top|Point out each layer as it enters|Your three questions for classmates|Answer at least 2 of each classmate’s questions",
     "Class 3, presentations. Each student plays the arrangement from the top and points out each new layer as it enters, with its time and bar number. Students write three "
     "questions they want classmates to answer, and answer at least two of each classmate's. Ask the class to count the layers at the start of every section before the presenter does."),
    (3, "closer", "One last thing…", "One layer at a time.|Give each one a job.|Leave room for the next.|Now press play.",
     "Close with the listening day: play an arrangement and ask the class to hold up fingers for the number of layers they hear in each section. A build that people can count is "
     "a build that was well planned and well mixed. Ask a few students which layer did the most for the energy. No audio is included in this resource; the sounds are the students' own."),
]
SHOTS1 = [("pacing", "Pacing guide", "3 class periods, slide by slide"), ("stair", "Layer map", "Eight layers, eight sections"),
          ("tempo", "Tempo table", "Seconds, bars and entrances")]
SHOTS2 = [1, 5, 7, 8, 10, 12]
SHOTS3 = [("stair", "Layer map"), ("cards", "Layer cards"), ("tempo", "Tempo table"), ("plan", "Arrangement plan"), ("mix", "Mix checklist"),
          ("example", "Worked example"), ("example2", "Worked example 2"), ("rubric", "Rubric")]
PREVIEW_PICKS = ["pacing", "stair", "tempo", "rubric"]

COVER_A = "Add one layer in every section"
COVER_C = "Logic Pro · Layers · Tempo math · Mix"
PDF_COVER = dict(a=26, b=42, c=15, art=5.0)
SQ_COVER = dict(a=38, b=140, c=27, art=420, gap=20)
SQ_B_LINES = ["Eight Nights,", "Eight Layers"]
SQ_SUB = "3 class periods · 32 bars of tempo math · intro slides"
SQ_HEADS = {1: ("Ready to teach Monday", 76, "Pacing, layer map, tempo tables and the /25 rubric in one PDF", 28),
            2: ("Intro deck included", 76, f"{len(SLIDES)} editable slides (.pptx + PDF) with speaker notes on every slide", 28),
            3: ("Everything inside", 72, "Layer cards, tempo tables, worked example, plans and worksheets", 28)}
SQ_BANDS = {1: "Eight layers <em>·</em> 32 bars <em>·</em> tempo <em>·</em> mix",
            2: "Layer map <em>·</em> tempo table <em>·</em> mix checklist",
            3: f"{len(PLAN)} pages <em>·</em> US Letter PDF <em>·</em> no audio included"}


# ================================================================ small page helpers
CSS_SG = ("<style>table.sg { border-collapse: collapse; width: 100%; table-layout: fixed; } table.sg td, table.sg th { border: 1pt solid #000; text-align: center; "
          "padding: 0; font-size: 8pt; } table.sg th { background: #000; color: #fff; font-family: Oswald; font-weight: 500; height: 14pt; } "
          "table.sg td.l { text-align: left; padding: 0 4pt; font-weight: 700; width: 1.45in; font-size: 8.6pt; } "
          "table.sg td.g { background: #e4e4e4; } </style>")


def howto_page(n, wm=False):
    parts = [("Teacher pages", "howto", "example2", "How to use, overview, setup, pacing, teacher notes, Logic quick reference, worked example (2 pages)"),
             ("Student pages", "stair", "reflect", "Layer map, layer cards, tempo table, arrangement plan, mix checklist, "
              "project sheet (3 pages), rubric, vocabulary, feedback planner, reflection page"),
             ("Intro deck (separate file)", None, None, f"{len(SLIDES)} slides, .pptx + PDF, speaker notes on every slide")]
    trs = "".join(f"<tr><td><b>{a}</b></td><td style='white-space:nowrap'>{('pages ' + str(D.IX(f)) + '–' + str(D.IX(l))) if f else 'deck'}</td>"
                  f"<td>{u}</td></tr>" for a, f, l, u in parts)
    inner = (f'<div class="cols"><div>'
             f'{D.H2("What this is", True)}'
             f'<p style="font-size:12pt;line-height:1.45">A {CLASSES}-class-period arrangement project for high school music technology. Every '
             f'student builds 32 bars of music in Logic Pro, in eight sections of 4 bars, and each section adds one new layer, so the music grows from one layer '
             f'to eight. Students choose a tempo, plan the layers, build and mix them, present the result and reflect on it. It is an original Hudson Beat project.</p>'
             f'{D.H2("Quick start")}<ol>'
             f'<li style="margin-bottom:5pt">Read the pacing guide (page {D.IX("pacing")}) and the teacher notes (pages {D.IX("tn1")}–{D.IX("tn2")}).</li>'
             f'<li style="margin-bottom:5pt">Look at the layer map, the layer cards and the tempo table (pages {D.IX("stair")}–{D.IX("tempo")}) and the setup (page {D.IX("setup")}).</li>'
             f'<li style="margin-bottom:5pt">Print the student pages (pages {D.IX("stair")}–{D.IX("reflect")}), one set per student.</li>'
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
             f'<li><b>Pace:</b> Class 1 is the plan and the tempo, Class 2 the first six layers, Class 3 the last two layers, the mix and the presentations (page {D.IX("pacing")}); the pacing page also shows two and four periods.</li>'
             f'<li><b>Another theme?</b> The eight-layer build works for any class; students may pick a different theme with eight steps (page {D.IX("overview")}).</li>'
             f'<li><b>Grading:</b> the rubric, /{RUBRIC_TOTAL}, the average of the student’s and your score (page {D.IX("rubric")}).</li></ul>'
             f'<div class="box" style="margin-top:6pt"><span class="k">In one sentence</span><p style="margin:0;font-size:12pt">Students learn that '
             f'an arrangement is planned: a tempo, eight layers with their own jobs, and one new layer at the start of each section.</p></div>'
             f'<p class="small" style="margin-top:6pt">Logic Pro is a product of Apple Inc. This resource is not affiliated with Apple.</p>'
             f'</div></div>')
    return D.page("How to use this resource", "START HERE", "Teacher", inner, n, key="howto")


def overview_page(n, wm=False):
    inner = (f'<div class="cols"><div>'
             f'<div class="box inv" style="margin-bottom:6pt"><span class="k">The project in one line</span><p style="margin:0;font-size:12pt">'
             f'<b>{TITLE}</b> · Layered arrangement · Logic Pro<br>Eight sections, eight layers, one new layer each time.</p></div>'
             f'{D.H2("What students make")}'
             f'<p style="font-size:12.6pt;line-height:1.5">An arrangement of 32 bars in eight sections of 4 bars, built in Logic Pro. It has a key, four chords, a tempo from 80 to 128 BPM '
             f'and eight layers: a pad or drone, bass, kick and clap, hi-hat or shaker, chord stabs, an arpeggio, a counter-melody and a lead. One new layer joins at the start of each '
             f'section, so section 1 has one layer and section 8 has all eight. Students hand in a bounced file and the zipped .logicx project, plus their plans and a reflection, '
             f'then play the arrangement and take questions.</p>'
             f'{D.H2("What this project reinforces")}<p style="font-size:12pt;line-height:1.5">{TN_REINFORCES}</p>'
             f'{D.H2("Standards")}<p style="font-size:11.4pt">Supports the National Core Arts Standards for Music (Music Technology, high school): generating '
             f'and developing ideas (MU:Cr1.1, MU:Cr2.1), presenting work (MU:Pr6.1) and responding to it (MU:Re7.2).</p>'
             f'</div><div>'
             f'{D.H2("Goals", True)}<ul>' + "".join(f"<li style='font-size:12pt;line-height:1.45'>{g}</li>" for g in GOALS) + '</ul>'
             f'{D.H2("About the theme")}<div class="box acc-b" style="padding:5pt 9pt"><p style="margin:0 0 3pt;font-size:10.2pt;line-height:1.36">{CULTURE}</p>'
             f'<p style="margin:0;font-size:10.2pt;line-height:1.36">{INSPIRE}</p></div>'
             f'<div class="box" style="margin-top:6pt;padding:5pt 9pt"><span class="k">At a glance</span><p style="margin:0;font-size:10.2pt;line-height:1.38"><b>Grades</b> {GRADES_TEXT}, music technology or music production · '
             f'<b>Length</b> {CLASSES} class periods (two and four also shown) · <b>Software</b> Logic Pro · <b>You supply</b> Macs with Logic Pro, headphones and a place to hand in files · '
             f'<b>Assessment</b> rubric, 5 categories scored 1–5, /{RUBRIC_TOTAL} (page {D.IX("rubric")})</p></div>'
             f'</div></div>')
    return D.page("Project overview", "OVERVIEW", "Layered arrangement project", inner, n, key="overview")


def setup_page(n, wm=False):
    inner = (f'<style>.sb p, .sb li {{ font-size: 11.6pt; line-height: 1.44; margin-bottom: 5pt; }}</style><div class="cols"><div class="big sb">'
             f'{D.H2("You need", True)}<ul>'
             f'<li><b>A Mac with Logic Pro</b> for each student, and <b>headphones</b>.</li>'
             f'<li><b>A place to hand in</b> the .mp3 or .wav files, the zipped .logicx and the reflection.</li>'
             f'<li><b>The layer map, layer cards and tempo table</b>, printed (pages {D.IX("stair")}–{D.IX("tempo")}), or shown on the projector.</li>'
             f'<li><b>Printed student pages</b>, one set each (pages {D.IX("stair")}–{D.IX("reflect")}).</li>'
             f'<li><b>A MIDI keyboard</b> is optional: every note can be clicked in with the mouse.</li></ul>'
             f'{D.H2("Before Class 1")}'
             + "".join(D.chk(c, 13, "font-size:11.6pt;margin-bottom:7pt") for c in [
                 f"Read the tempo table (page {D.IX('tempo')}) so you can answer ‘when does the lead enter?’ for any tempo.",
                 f"Open Logic Pro on a student computer and check which tools your version has: Session Players, Step Sequencer, Arpeggiator (see page {D.IX('logicref')}).",
                 f"Check that you can add a marker and repeat a 4-bar region to bar 33.",
                 f"Read the worked example (pages {D.IX('example')}–{D.IX('example2')})."]) +
             f'</div><div class="big sb">'
             f'{D.H2("What to watch", True)}'
             f'<p style="font-size:11.4pt">Watch for layers that start in the wrong section, arithmetic slips, layers that do the same job, and a mix so busy that new layers cannot be heard. {TN_NOTE}</p>'
             f'<div class="box acc-b" style="margin-top:2pt"><span class="k">Ideas for the room</span><ul style="margin:0">'
             f'<li style="font-size:11.2pt">Ask while students work: which layer is new in this section? What is its job? What could you take away?</li>'
             f'<li style="font-size:11.2pt">Say the theme plainly: the eight-night pattern is an inspiration for the structure, and students may choose another theme.</li>'
             f'<li style="font-size:11.2pt">A student who is stuck can build the pad and the lead only: two layers already sound like an arrangement.</li></ul></div>'
             f'{D.H2("Melody (optional)")}'
             f'<div class="box"><p style="margin:0;font-size:10.8pt;line-height:1.4">{MELODY_NOTE}</p></div>'
             f'<div class="box" style="margin-top:6pt"><span class="k">Keep the volume moderate</span><p style="margin:0;font-size:11pt;line-height:1.4">'
             f'Bright, high sounds and big drums can be tiring in headphones. Tell students to start low and check the final mix at a normal level.</p></div>'
             f'</div></div>')
    return D.page("Setup and what to watch", "SETUP", "Teacher", inner, n, key="setup")


# ================================================================ the layer map, layer cards, tempo table, plan and mix pages
def stair_page(n, wm=False):
    head = "<tr><th style='width:1.45in'>Section</th>" + "".join(f"<th>{s}</th>" for s in range(1, SECTIONS + 1)) + "<th>Total</th></tr>"
    cnt = [sum(1 for r in range(1, SECTIONS + 1) if playing(r, s)) for s in range(1, SECTIONS + 1)]
    r1 = "<tr><td class='l'>Starts at bar</td>" + "".join(f"<td>{start_bar(s)}</td>" for s in range(1, SECTIONS + 1)) + "<td>–</td></tr>"
    r2 = "<tr><td class='l'>Layers playing</td>" + "".join(f"<td><b>{c}</b></td>" for c in cnt) + f"<td><b>{sum(cnt)}</b></td></tr>"
    r3 = "<tr><td class='l'>Layer-bars (layers × 4)</td>" + "".join(f"<td>{c * BARS_PER}</td>" for c in cnt) + f"<td><b>{sum(cnt) * BARS_PER}</b></td></tr>"
    mine = "".join(f"<tr><td class='l' style='height:21pt'>{r}</td>" + "".join("<td></td>" for _ in range(SECTIONS)) + "</tr>" for r in range(1, SECTIONS + 1))
    mhead = "<tr><th style='width:1.45in'>My layer</th>" + "".join(f"<th>{s}</th>" for s in range(1, SECTIONS + 1)) + "</tr>"
    inner = (f'{CSS_SG}<p style="margin:0 0 4pt;font-size:10.2pt;line-height:1.36">Step 2: plan the layers. Your arrangement has eight sections of {BARS_PER} bars, {TOTAL_BARS} bars in all. '
             f'Section 1 has one layer. Every new section adds exactly one more layer and keeps all the earlier ones, so section 8 plays all eight. The map below shows the plan '
             f'as a staircase: each night adds one row.</p>'
             f'<div style="margin:0 0 3pt">{D.body_svg(stair_body(1500, False, "stair page", 24, 46))}</div>'
             f'<table class="sg" style="margin-top:2pt">{head}{r1}{r2}{r3}</table>'
             f'<p class="small" style="margin:2pt 0 3pt;font-size:8.6pt">Layer-bars count how many bars of layers play: in section 3 there are 3 layers × 4 bars = 12. Across all eight sections the layers add up to {sum(cnt)} layer-sections, or {sum(cnt) * BARS_PER} layer-bars.</p>'
             f'<span class="k" style="margin-top:3pt">My staircase: write my layer on each row, then shade the sections where it plays</span>'
             f'<table class="sg" style="margin-top:2pt">{mhead}{mine}</table>'
             f'<p class="small" style="margin:2pt 0 0;font-size:8.6pt">Check: the shaded squares in column 1 should number 1, in column 2 should number 2, and so on up to 8 in column 8. Total shaded squares: {sum(cnt)}.</p>')
    return D.page("Layer map", "STUDENT", "Class 1", inner, n, wm, name=True, key="stair")


def cards_page(n, wm=False):
    cells = []
    for L in LAYERS:
        cells.append(f'<div class="box" style="padding:4pt 8pt"><span class="k" style="font-size:10.4pt">Night {L["n"]} · {L["name"]}</span>'
                     f'<p style="margin:0 0 2pt;font-size:9.4pt;line-height:1.3"><b>Its job:</b> {L["role"]}.</p>'
                     f'<p style="margin:0 0 2pt;font-size:9.4pt;line-height:1.3"><b>Try:</b> {L["tools"]}.</p>'
                     f'<p style="margin:0 0 2pt;font-size:9.4pt;line-height:1.3"><b>Idea:</b> {L["idea"]}.</p>'
                     f'<div class="fl" style="margin:3pt 0 0;font-size:9.2pt"><b>My sound:</b><span></span></div></div>')
    inner = (f'<p style="margin:0 0 5pt;font-size:10.2pt;line-height:1.36">Step 2: plan the layers. Each night adds one card. Read the card, try its tools if your version has them, '
             f'and write down the sound you chose. Ideas are suggestions, not rules; every pattern should be your own.</p>'
             f'<div style="display:grid;grid-template-columns:repeat(2,1fr);gap:6pt 10pt">{"".join(cells)}</div>')
    return D.page("Layer cards", "STUDENT", "Classes 1–2", inner, n, wm, name=True, key="cards")


def tempo_rows():
    rows = []
    for bpm in TEMPOS:
        whole = total_s(bpm).denominator == 1
        b, e = ("<b>", "</b>") if whole else ("", "")
        rows.append(f"<tr><td>{b}{bpm}{e}</td><td>{dec(spb(bpm), 3)}</td><td>{dec(bar_len(bpm), 3)}</td><td>{dec(sec_len(bpm), 2)}</td><td>{b}{dec(total_s(bpm), 2)}{e}</td></tr>")
    return "".join(rows)


def start_rows():
    rows = []
    for bpm in TEMPOS:
        rows.append(f"<tr><td><b>{bpm}</b></td>" + "".join(f"<td>{dec(start_s(s, bpm), 2)}</td>" for s in range(1, SECTIONS + 1)) + "</tr>")
    return "".join(rows)


def tempo_page(n, wm=False):
    head = "<tr><th>BPM</th>" + "".join(f"<th>Night {s}</th>" for s in range(1, SECTIONS + 1)) + "</tr>"
    barrow = "<tr><td><b>Starts at bar</b></td>" + "".join(f"<td><b>{start_bar(s)}</b></td>" for s in range(1, SECTIONS + 1)) + "</tr>"
    inner = (f'<style>table.cc td {{ text-align: center; padding: 2pt 3pt; font-size: 9.4pt; line-height: 1.15; }} table.cc th {{ text-align: center; }}</style>'
             f'<p style="margin:0 0 4pt;font-size:10.2pt;line-height:1.36">Step 1: choose key and tempo. In 4/4 there are 4 beats in a bar, and each section has {BARS_PER} bars. '
             f'These formulas turn a tempo into seconds. Every number below is computed, so you can check your own arithmetic against it.</p>'
             f'<div class="cols" style="gap:10pt;align-items:flex-start"><div class="box acc-b" style="padding:5pt 9pt;flex:1.1"><span class="k">The formulas (4/4)</span>'
             f'<p style="margin:0 0 2pt;font-size:9.8pt"><b>Seconds per beat</b> = 60 ÷ BPM</p><p style="margin:0 0 2pt;font-size:9.8pt"><b>Seconds per bar</b> = 240 ÷ BPM</p>'
             f'<p style="margin:0 0 2pt;font-size:9.8pt"><b>Seconds per section</b> = 4 × 240 ÷ BPM</p><p style="margin:0 0 2pt;font-size:9.8pt"><b>32 bars</b> = 32 × 240 ÷ BPM seconds</p>'
             f'<p style="margin:0 0 2pt;font-size:9.8pt"><b>A section starts at</b> (night − 1) × 4 × 240 ÷ BPM seconds</p>'
             f'<p style="margin:0;font-size:9.8pt"><b>Example:</b> 100 BPM: 240 ÷ 100 = 2.4 s per bar, 4 × 2.4 = 9.6 s per section, 32 × 2.4 = 76.8 s in all.</p></div>'
             f'<div class="box" style="padding:5pt 9pt;flex:1"><span class="k">Rounding rules</span><p style="margin:0;font-size:9.2pt;line-height:1.32">Seconds per beat and per bar to 3 decimals, '
             f'seconds per section and totals to 2, and a 5 rounds up. So 240 ÷ 90 = 2.667 seconds per bar, and 4 × 240 ÷ 90 = 10.67 seconds per section (10.666… rounds up). '
             f'In the start table, every time is rounded to 2 decimals from its exact value.</p></div></div>'
             f'<span class="k" style="margin-top:5pt">How long is the arrangement?</span>'
             f'<table class="t cc" style="margin-top:1pt"><tr><th>BPM</th><th>Seconds per beat</th><th>Seconds per bar</th><th>Seconds per section</th><th>Seconds in 32 bars</th></tr>{tempo_rows()}</table>'
             f'<p class="small" style="margin:0 0 2pt;font-size:8.6pt">Bold = the whole piece is a whole number of seconds: 64 seconds at 120 BPM and 60 seconds at 128 BPM.</p>'
             f'<span class="k" style="margin-top:3pt">When does each layer enter? Seconds from the start</span>'
             f'<table class="t cc" style="margin-top:1pt">{head}{barrow}{start_rows()}</table>'
             f'<p class="small" style="margin:0 0 3pt;font-size:8.6pt">Night 1 begins at 0 seconds. Section 8, the lead’s section, ends when the 32 bars end, at the total in the table above.</p>'
             f'<div class="box acc-b" style="padding:5pt 9pt"><span class="k">My tempo</span>'
             f'<div class="fl" style="margin:3pt 0 3pt;font-size:10pt"><b>Tempo (BPM, 80 to 128):</b><span></span><b>One bar = 240 ÷ BPM =</b><span></span><b>s</b></div>'
             f'<div class="fl" style="margin:0;font-size:10pt"><b>One section = 4 bars =</b><span></span><b>s</b><b style="margin-left:8pt">32 bars =</b><span></span><b>s</b></div></div>')
    return D.page("Tempo table", "STUDENT", "Class 1", inner, n, wm, name=True, key="tempo")


def plan_page(n, wm=False):
    rows = "".join(f"<tr><td style='height:27pt;text-align:center'><b>{L['n']}</b></td><td><b>{L['name']}</b></td><td style='text-align:center'>{start_bar(L['n'])}</td><td></td><td></td><td></td></tr>"
                   for L in LAYERS)
    inner = (f'<p style="margin:0 0 4pt;font-size:10.2pt;line-height:1.36">Step 2: plan the layers. Choose your key and four chords first. Then plan all eight layers: the sound source, '
             f'the pattern and the second at which each layer enters, using the tempo table (page {pg("tempo")}).</p>'
             f'<div class="cols" style="gap:10pt"><div class="box acc-b" style="padding:5pt 9pt"><span class="k">My key and chords</span>'
             f'<div class="fl" style="margin:3pt 0 3pt;font-size:10pt"><b>Key:</b><span></span></div>'
             f'<div class="fl" style="margin:0 0 3pt;font-size:10pt"><b>Chord 1 · 2 · 3 · 4 (one bar each):</b><span></span></div>'
             f'<div class="fl" style="margin:0;font-size:10pt"><b>Mood of my arrangement:</b><span></span></div></div>'
             f'<div class="box" style="padding:5pt 9pt"><span class="k">My tempo</span>'
             f'<div class="fl" style="margin:3pt 0 3pt;font-size:10pt"><b>Tempo (BPM):</b><span></span><b>Bar =</b><span></span><b>s</b></div>'
             f'<div class="fl" style="margin:0 0 3pt;font-size:10pt"><b>Section = 4 × one bar =</b><span></span><b>s</b></div>'
             f'<div class="fl" style="margin:0;font-size:10pt"><b>32 bars =</b><span></span><b>s</b></div></div></div>'
             f'<span class="k" style="margin-top:6pt">My eight layers</span>'
             f'<table class="map" style="margin-bottom:5pt"><tr><th style="width:6%">Night</th><th style="width:17%">Layer</th><th style="width:9%">Enters at bar</th>'
             f'<th style="width:14%">Enters at (seconds) = (night − 1) × section</th><th style="width:24%">Instrument or sound source</th><th>My pattern or idea</th></tr>{rows}</table>'
             f'<div class="box" style="padding:4pt 10pt"><span class="k">Checks before I build</span>'
             + "".join(D.chk(c, 11, "font-size:10pt;margin-bottom:2pt") for c in [
                 "Every layer has its own sound and its own job; no two do the same thing.",
                 "Each layer enters at the start of its section, at the bar printed in the table.",
                 "My entrance times match the tempo table (page " + str(pg("tempo")) + ").",
                 "The bass is the lowest layer and the lead stands out.",
                 "I left rests so the layers do not all play every beat."]) + '</div>'
             f'<span class="k" style="margin-top:5pt">Notes</span>' + D.lines(3, 20))
    return D.page("Arrangement plan", "STUDENT", "Classes 1–3", inner, n, wm, name=True, key="plan")


def mix_page(n, wm=False):
    def box(title, items, acc=False):
        return (f'<div class="box{" acc-b" if acc else ""}" style="padding:5pt 9pt"><span class="k">{title}</span>'
                + "".join(D.chk(c, 11, "font-size:10pt;line-height:1.3;margin-bottom:3pt") for c in items) + '</div>')
    inner = (f'<p style="margin:0 0 5pt;font-size:10.2pt;line-height:1.36">Step 6: mix and bounce. A mix lets every layer be heard. Work through the boxes with headphones, '
             f'then check each one off. A new layer should be easy to hear when it enters.</p>'
             f'<div class="cols" style="gap:10pt;align-items:flex-start"><div>'
             + box("Levels", ["I can hear every layer when it joins.", "The newest layer is a little louder in its first section.",
                              "The master level never reaches red (no clipping).", "The lead is the clearest layer in section 8."], True)
             + '<div style="height:6pt"></div>'
             + box("Space (pan)", ["The hi-hat or shaker is panned a little to one side.", "The arpeggio and the counter-melody sit on different sides.",
                                   "The bass, kick and lead stay near the middle."])
             + '</div><div>'
             + box("Low end", ["The kick and the bass do not cover each other.", "I cut the low notes from layers that do not need them (Channel EQ, if I like).",
                               "The pad is not muddy under the bass."])
             + '<div style="height:6pt"></div>'
             + box("Entrances", ["Markers are at bars 1, 5, 9, 13, 17, 21, 25 and 29.", "Each layer’s region starts exactly on its marker.",
                                 "I drew a fade or a filter sweep on at least one new layer."], True)
             + '</div></div>'
             f'<div class="box" style="margin-top:6pt;padding:5pt 9pt"><span class="k">The listening test</span><p style="margin:0 0 3pt;font-size:10pt;line-height:1.36">Play the piece from bar 1 with your eyes closed. '
             f'Hold up fingers for the number of layers you hear at the start of each section. Section 1 should be 1, section 2 should be 2, and section 8 should be 8. '
             f'Write what you hear:</p><div class="fl" style="margin:2pt 0;font-size:10pt"><b>Sections:</b>'
             + "".join(f'<b style="margin-left:5pt">{s}</b><span style="flex:0 0 0.5in"></span>' for s in range(1, SECTIONS + 1)) + '</div></div>'
             f'<div class="box acc-b" style="margin-top:6pt;padding:5pt 9pt"><span class="k">Bounce</span>'
             + "".join(D.chk(c, 11, "font-size:10pt;margin-bottom:3pt") for c in [
                 "The bounce starts at bar 1 and ends after bar 32 (about " + dec(total_s(100), 1) + " seconds at 100 BPM; check your own tempo on page " + str(pg("tempo")) + ").",
                 "MP3 or WAV bounced, and the .logicx project zipped.", f"Both files named {FILE_NAME}."]) + '</div>'
             f'<span class="k" style="margin-top:6pt">What I changed after the listening test</span>' + D.lines(7, 24))
    return D.page("Mix checklist", "STUDENT", "Class 3", inner, n, wm, name=True, key="mix")


# ================================================================ worked example (2 pages)
def ex_rows():
    out = []
    for L, pat in zip(LAYERS, EX_LAYER_PATTERNS):
        i = L["n"]
        out.append(f"<tr><td><b>{i}</b></td><td>{L['name']}</td><td>{start_bar(i)}</td><td>{fmt(start_s(i, EX_BPM))}</td><td>{i}</td><td style='text-align:left'>{pat}</td></tr>")
    return "".join(out)


def ex_compare_rows():
    out = []
    for bpm in TEMPOS:
        b, e = ("<b>", "</b>") if bpm == EX_BPM else ("", "")
        out.append(f"<tr><td>{b}{bpm}{e}</td><td>{dec(bar_len(bpm), 3)}</td><td>{dec(sec_len(bpm), 2)}</td><td>{dec(total_s(bpm), 2)}</td><td>{dec(start_s(5, bpm), 2)}</td></tr>")
    return "".join(out)


def example_page(n, wm=False):
    inner = (f'<style>table.ec td {{ text-align: center; }}</style>'
             f'<p style="margin:0 0 4pt;font-size:10pt">An <b>invented plan on paper</b>: an arrangement in {EX_KEY} at {EX_BPM} BPM. No audio is included. '
             f'Student projects will differ. Page 1 of 2: the plan, the entrances and the tempo choice.</p>'
             f'<div class="cols" style="gap:10pt;align-items:flex-start"><div class="box"><span class="k">1 · A weak plan</span><p style="margin:0;font-size:10.2pt">{EX_WEAK}</p>'
             f'<p style="margin:3pt 0 0;font-size:9.2pt">It names no tempo, no layers, no sections and no times.</p></div>'
             f'<div class="box acc-b"><span class="k">2 · A clear plan</span><p style="margin:0;font-size:8.6pt;line-height:1.28">{EX_STRONG}</p></div></div>'
             f'{D.H2("3 · The eight entrances at 100 BPM")}'
             f'<table class="t ec" style="font-size:9pt;line-height:1.2"><tr><th>Night</th><th>Layer</th><th>Enters at bar</th><th>Enters at (seconds)</th><th>Layers playing</th><th>Its pattern</th></tr>{ex_rows()}</table>'
             f'<p style="margin:2pt 0 0;font-size:9pt">One beat lasts 60 ÷ {EX_BPM} = {dec(spb(EX_BPM), 3)} s and one bar lasts 240 ÷ {EX_BPM} = {fmt(EX_BAR_S)} s. A section lasts 4 × {fmt(EX_BAR_S)} = {fmt(EX_SEC_S)} s. '
             f'The arrangement lasts {TOTAL_BARS} × {fmt(EX_BAR_S)} = {fmt(total_s(EX_BPM))} seconds. Night 5 enters at bar 17, which is (5 − 1) × {fmt(EX_SEC_S)} = {fmt(start_s(5, EX_BPM))} s.</p>'
             f'{D.H2("4 · Why 100 BPM? The same plan at six tempos")}'
             f'<table class="t ec" style="font-size:9pt;line-height:1.18"><tr><th>BPM</th><th>Sec per bar</th><th>Sec per section</th><th>32 bars (s)</th><th>Night 5 enters (s)</th></tr>{ex_compare_rows()}</table>'
             f'<p style="margin:3pt 0 0;font-size:9pt;line-height:1.3">At 100 BPM the piece is {fmt(total_s(EX_BPM))} seconds and every entrance time has one decimal, which keeps the arithmetic short. '
             f'At 120 BPM it is {fmt(total_s(120))} seconds, and at 128 BPM exactly {fmt(total_s(128))} seconds, one minute. At 90 and 110 BPM the times are repeating decimals, so they are rounded to 2 decimals. '
             f'The choice is the musician’s: 100 BPM is relaxed enough to hear each new layer arrive.</p>')
    return D.page("Worked example · the plan and the entrances", "EXAMPLE", "Teacher", inner, n, wm, ak=True, key="example")


def example2_page(n, wm=False):
    qs = " ".join(f"{i + 1}. {q}" for i, q in enumerate(EX_QUESTIONS))
    cnt = [sum(1 for r in range(1, SECTIONS + 1) if playing(r, s)) for s in range(1, SECTIONS + 1)]
    inner = (f'<p style="margin:0 0 3pt;font-size:10pt">The same arrangement, page 2 of 2: the map of the whole piece, then the numbers.</p>'
             f'{D.H2("5 · The map: 32 bars, 8 sections, 8 layers")}'
             f'<div style="width:7.4in;margin:1pt auto 3pt">{D.body_svg(stair_body(1500, True, "map page", 24, 46))}</div>'
             f'<div class="box acc-b" style="margin-top:4pt"><span class="k">6 · Checking the numbers</span><p style="margin:0;font-size:10pt;line-height:1.38">'
             f'One bar of 4/4 at {EX_BPM} BPM lasts 240 ÷ {EX_BPM} = {fmt(EX_BAR_S)} seconds, so {TOTAL_BARS} bars = {TOTAL_BARS} × {fmt(EX_BAR_S)} = {fmt(total_s(EX_BPM))} seconds, and '
             f'{SECTIONS} sections × {fmt(EX_SEC_S)} = {fmt(total_s(EX_BPM))} seconds too. A section starts at (night − 1) × {fmt(EX_SEC_S)} seconds: '
             + ", ".join(f"night {s} at {fmt(start_s(s, EX_BPM))}" for s in range(1, SECTIONS + 1)) +
             f'. The layers playing in sections 1 to 8 are {", ".join(str(c) for c in cnt)}, which add up to {sum(cnt)}; at 4 bars each that is {sum(cnt) * BARS_PER} layer-bars. '
             f'The hi-hat plays 8 hits in each bar, so {8 * BARS_PER} hits in a section.</p></div>'
             f'<div class="box" style="margin-top:5pt"><span class="k">7 · The automation</span><p style="margin:0;font-size:10.2pt;line-height:1.38">{EX_AUTO}.</p></div>'
             f'<div class="box" style="margin-top:5pt"><span class="k">8 · Three feedback questions (invented)</span><p style="margin:0;font-size:10.2pt;line-height:1.38">{qs}</p></div>'
             f'<div class="box acc-b" style="margin-top:5pt"><span class="k">9 · Moments to point out in class</span><ul style="margin:0">'
             f'<li style="font-size:10.2pt;margin-bottom:2pt">Each entrance is on the first beat of bar 1, 5, 9, 13, 17, 21, 25 or 29, so every new layer starts exactly on a marker.</li>'
             f'<li style="font-size:10.2pt;margin-bottom:2pt">The kick and clap arrive in night 3. Before that, the pad and the bass have no beat, so the build starts as a slow wash and gets a pulse.</li>'
             f'<li style="font-size:10.2pt;margin-bottom:0">The lead arrives alone in section 8, after seven layers have set the key and the beat, so it is the climax.</li></ul></div>')
    return D.page("Worked example · the map and the numbers", "EXAMPLE", "Teacher", inner, n, wm, ak=True, key="example2")


PAGES = {"howto": howto_page, "overview": overview_page, "setup": setup_page, "example": example_page, "example2": example2_page,
         "stair": stair_page, "cards": cards_page, "tempo": tempo_page, "plan": plan_page, "mix": mix_page}


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
def class_set(badge):
    m = re.fullmatch(r"Class(?:es)? (\d)(?:–(\d))?", badge)
    if not m:
        return None
    return set(range(int(m.group(1)), int(m.group(2) or m.group(1)) + 1))


BADGE = {"stair": "Class 1", "cards": "Classes 1–2", "tempo": "Class 1", "plan": "Classes 1–3", "mix": "Class 3", "present": f"Classes {CLASSES - 1}–{CLASSES}"}
def badge_errors(flat):
    """Every page badge that names classes agrees with the pacing page's student-page lists, and is printed on the page."""
    errs = []
    for k, bd in BADGE.items():
        want = class_set(bd)
        have = {d["n"] for d in PACING if k in d["pages"]}
        if want != have:
            errs.append(f"class badge of page {pg(k)} ({k}) says '{bd}' but the pacing page lists it in classes {sorted(have)}")
        if bd not in flat[D.IX(k) - 1]:
            errs.append(f"page {pg(k)} ({k}): badge '{bd}' is not printed on it")
    for d in PACING:
        for k in d["pages"]:
            if k not in BADGE and k not in ("proj1", "proj2", "proj3", "vocab", "rubric", "reflect"):
                errs.append(f"class {d['n']} lists page '{k}', which has no class badge")
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


def float_start(s, bpm):
    """An independent float check of one section-start time: (s - 1) x 4 x 240 / BPM, rounded half up to 2 decimals."""
    x = (s - 1) * 4 * 240 / bpm
    return f"{math.floor(x * 100 + 0.5 + 1e-7) / 100:.2f}"


def verify_content():
    errs = []
    counts = dict(goals=(GOALS, 4), vocab=(VOCAB, 4), reqs=(REQS, 7), steps=(STEPS, 7), tips=(TIPS, 4), check=(CHECK, 6),
                  rubric=(RUBRIC, 5), struggles=(STRUGGLES, 4), resources=(RESOURCES, 4), slides=(SLIDES, 14), plan=(PLAN, 23),
                  logic=(LOGIC_REF, 9), layers=(LAYERS, 8), patterns=(EX_LAYER_PATTERNS, 8))
    for nm, (lst, nexp) in counts.items():
        if len(lst) != nexp:
            errs.append(f"{nm}: {len(lst)} items, expected {nexp}")
    if RUBRIC_TOTAL != 25 or LEVELS != [1, 2, 3, 4, 5]:
        errs.append("rubric is /25, levels 1-5")
    if FILE_NAME not in CHECK[2]:
        errs.append("file name format must be on the checklist")
    if set(TAGS) & {"Holiday", "Student Practice", "Theme", "Seasonal"} or "Performing Arts" in SUBJECTS:
        errs.append("tags and subjects must not be headings")
    for w in ("winter", "holiday", "christmas", "hanukkah", "chanukah", "sleigh", "carol", "snow", "night", "menorah"):
        if w in LISTING_TITLE.lower():
            errs.append(f"the listing title must not hold the seasonal word {w}")
    if len(STEP_NAMES) != len(STEPS) or any(not s.startswith(f"<b>{nm}</b>") for s, nm in zip(STEPS, STEP_NAMES)):
        errs.append("STEPS must start with the bold names in STEP_NAMES (the pages cite them)")
    # ---- the arithmetic, by hand first
    if [spb(b) for b in (120, 96, 100, 80)] != [Fraction(1, 2), Fraction(5, 8), Fraction(3, 5), Fraction(3, 4)]:
        errs.append("seconds per beat = 60 / BPM: 0.5 at 120, 0.625 at 96, 0.6 at 100, 0.75 at 80")
    if [bar_len(b) for b in (120, 100, 80, 128)] != [2, Fraction(12, 5), 3, Fraction(15, 8)]:
        errs.append("seconds per bar = 240 / BPM: 2 at 120, 2.4 at 100, 3 at 80, 1.875 at 128")
    if any(bar_len(b) != 4 * spb(b) for b in TEMPOS):
        errs.append("a bar of 4/4 is four beats")
    if SECTIONS != 8 or BARS_PER != 4 or TOTAL_BARS != 32:
        errs.append("8 sections x 4 bars = 32 bars")
    if [dec(spb(b), 3) for b in TEMPOS] != ["0.750", "0.667", "0.600", "0.545", "0.500", "0.469"] or \
       [dec(bar_len(b), 3) for b in TEMPOS] != ["3.000", "2.667", "2.400", "2.182", "2.000", "1.875"]:
        errs.append("seconds per beat and per bar to 3 decimals")
    if [dec(sec_len(b), 2) for b in TEMPOS] != ["12.00", "10.67", "9.60", "8.73", "8.00", "7.50"]:
        errs.append("seconds per section to 2 decimals: 12, 10.67, 9.6, 8.73, 8, 7.5")
    if [dec(total_s(b), 2) for b in TEMPOS] != ["96.00", "85.33", "76.80", "69.82", "64.00", "60.00"]:
        errs.append("seconds in 32 bars: 96, 85.33, 76.8, 69.82, 64, 60")
    for b in TEMPOS:
        if total_s(b) != Fraction(7680, b) or total_s(b) != SECTIONS * sec_len(b) or abs(float(total_s(b)) - 32 * 240 / b) > 1e-9:
            errs.append(f"total length at {b} BPM")
        for s in range(1, SECTIONS + 1):
            if dec(start_s(s, b), 2) != float_start(s, b):
                errs.append(f"section {s} start at {b} BPM: exact {dec(start_s(s, b), 2)} but float check {float_start(s, b)}")
        if start_s(SECTIONS + 1, b) != total_s(b):
            errs.append(f"the end of section 8 is the end of the piece at {b} BPM")
    if rnd(Fraction(5, 2), 0) != 3 or rnd(Fraction(1, 2), 0) != 1 or dec(Fraction(15, 8), 3) != "1.875" or dec(Fraction(32, 3), 2) != "10.67":
        errs.append("round half up")
    if [start_bar(s) for s in range(1, 9)] != [1, 5, 9, 13, 17, 21, 25, 29]:
        errs.append("sections start at bars 1, 5, 9, 13, 17, 21, 25, 29")
    # ---- the staircase: layer r plays in section s exactly when s >= r
    grid = [[playing(r, s) for s in range(1, SECTIONS + 1)] for r in range(1, SECTIONS + 1)]
    if len(grid) != 8 or any(len(row) != 8 for row in grid):
        errs.append("the layer map is 8 rows x 8 columns")
    for s in range(1, SECTIONS + 1):
        col = [grid[r - 1][s - 1] for r in range(1, SECTIONS + 1)]
        if sum(col) != s:
            errs.append(f"section {s} must play {s} layers, plays {sum(col)}")
        new = [r for r in range(1, SECTIONS + 1) if grid[r - 1][s - 1] and (s == 1 or not grid[r - 1][s - 2])]
        if new != [s]:
            errs.append(f"section {s} must add exactly layer {s}, adds {new}")
        if s > 1 and any(grid[r - 1][s - 2] and not grid[r - 1][s - 1] for r in range(1, SECTIONS + 1)):
            errs.append(f"a layer stops in section {s}: the arrangement only adds")
    if sum(sum(row) for row in grid) != 36 or sum(range(1, 9)) != 36:
        errs.append("the staircase has 1 + 2 + ... + 8 = 36 filled cells")
    for r, L in enumerate(LAYERS, start=1):
        if L["n"] != r:
            errs.append(f"layer {r} has the wrong night number")
    if [L["name"] for L in LAYERS] != ["Pad or drone", "Bass", "Kick and clap", "Hi-hat or shaker", "Chord stabs", "Arpeggio", "Counter-melody", "Lead"] or len(set(LAYER_NAMES)) != 8:
        errs.append("the eight layers in order: pad or drone, bass, kick and clap, hi-hat or shaker, chord stabs, arpeggio, counter-melody, lead")
    for L in LAYERS:
        if any(w in L["tools"] for w in ("Session Player", "Step Sequencer", "Arpeggiator")) and "if your version has it" not in L["tools"]:
            errs.append(f"layer {L['name']}: a newer Logic tool must be hedged with 'if your version has it'")
    for nm, txt in LOGIC_REF:
        if any(w in txt for w in ("Session Players", "Step Sequencer", "Arpeggiator", "Scale Quantize")) and "if your version" not in txt.lower():
            errs.append(f"Logic reference '{nm}' must hedge a newer tool with 'if your version'")
    # ---- the worked example
    if EX_BPM != 100 or EX_BAR_S != Fraction(12, 5) or EX_SEC_S != Fraction(48, 5) or total_s(EX_BPM) != Fraction(384, 5) or dec(total_s(EX_BPM), 1) != "76.8":
        errs.append("the example: 32 bars x 2.4 s = 76.8 s at 100 BPM; a section is 9.6 s")
    if [fmt(start_s(s, EX_BPM)) for s in range(1, 9)] != ["0", "9.6", "19.2", "28.8", "38.4", "48", "57.6", "67.2"]:
        errs.append("example entrances at 100 BPM: 0, 9.6, 19.2, 28.8, 38.4, 48, 57.6, 67.2")
    if dec(total_s(120), 0) != "64" or dec(total_s(128), 0) != "60":
        errs.append("32 bars last 64 s at 120 BPM and 60 s at 128 BPM")
    for need in ("100 BPM", "240 ÷ 100 = 2.4", "9.6 seconds", "76.8 seconds", "0, 9.6, 19.2, 28.8, 38.4, 48, 57.6 and 67.2 seconds", "section 8 plays all eight"):
        if need not in EX_STRONG:
            errs.append(f"the clear plan must say '{need}'")
    # ---- cultural and factual statements (kept minimal; QA checks each against sources)
    for need in ("eight-night", "festival of lights", "Second Temple in Jerusalem", "2nd century BCE", "25th day of the Hebrew month of Kislev", "late November or December",
                 "nine branches", "eight for the nights", "shamash", "One new candle is added each night"):
        if need not in CULTURE:
            errs.append(f"culture text must say '{need}'")
    for need in ("inspiration", "not a religious activity", "any class", "different theme", "does not say how anyone should"):
        if need not in INSPIRE:
            errs.append(f"inspiration text must say '{need}'")
    if re.search(r"\b20\d\d\b", CULTURE + INSPIRE + MELODY_NOTE):
        errs.append("no dates or years in the festival text (only 'late November or December')")
    for w in ("melody chart", "public domain"):
        if w not in MELODY_NOTE:
            errs.append(f"melody note must say '{w}'")
    # ---- slides: no truncated bullets, side lines or notes; page numbers in notes are pages that exist and fit
    for i, s in enumerate(SLIDES, start=1):
        for b in [x.strip() for x in s[3].split("|") if x.strip()] if s[1] != "pic" else []:
            if truncated(b):
                errs.append(f"slide {i} bullet looks truncated: '{b}'")
        if s[1] == "listen" and len([x for x in s[3].split("|") if x]) != 5:
            errs.append(f"slide {i} (listen): head, teacher line and three questions")
    for k, lines in SIDE.items():
        for b in lines:
            if truncated(b) or b.endswith(".") or len(b) > 44:
                errs.append(f"side line for '{k}' looks truncated or has a stop: '{b}'")
    for i, s in enumerate(SLIDES, start=1):
        for m in re.finditer(r"\bpages? (\d+)\b", s[4]):
            if int(m.group(1)) not in {pg(k) for k in PLAN}:
                errs.append(f"slide {i} notes name page {m.group(1)}, which does not exist")
    for need, key in ((f"page {pg('stair')}", 4), (f"page {pg('cards')}", 4), (f"page {pg('tempo')}", 6), (f"page {pg('cards')}", 7), (f"page {pg('logicref')}", 8),
                      (f"page {pg('plan')}", 9), (f"pages {pg('example')} and {pg('example2')}", 9)):
        if need not in SLIDES[key][4]:
            errs.append(f"slide {key + 1} notes must name {need}")
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
        errs += drawing_edge_errors() + footer_gap_errors()
    return errs


def verify_outputs(flat, stext, notes):
    errs = []
    alldeck = " ".join(stext + notes)
    txt = " ".join(flat)
    if "No audio" not in notes[0]:
        errs.append("deck slide 1 notes must say 'No audio'")
    for need in ("No audio, recordings, lyrics or melodies", "invented plan on paper", "Drum Machine Designer", "Quick Sampler", "Alchemy", "Session Players", "Arpeggiator",
                 "Marker", "60 ÷ BPM", "240 ÷ BPM", "if your version", "layer", "does not print a melody chart", "not a religious activity", "different theme",
                 "late November or December", "nine branches", "shamash",
                 "Created with the help of digital and AI tools. Notation and answer keys are verified before release."):
        if need.lower() not in txt.lower():
            errs.append(f"PDF must say: '{need}'")
    if "What changed" in txt or "Kept as I wrote it" in txt or "my project menu" in txt or "my Digital Music Production" in txt:
        errs.append("ORIGINAL kit: no wording about changes to an owner's sheet")
    if "checked by hand" in txt or "handmade" in txt.lower() or "classroom-tested" in txt.lower() or "hand-checked" in txt.lower():
        errs.append("never claim hand checks or classroom testing for a new product")
    if GRADES_TEXT != "9–12" or "Grades 9–12" not in txt:
        errs.append("PDF: 'Grades 9–12'")
    for w in ("colour", "favour", "centre", "licence", "grey", "metre", "organis", "recognis", "practise", "analyse", "whilst", "milli-second", "colourful"):
        if w in txt.lower().replace("greyscale", ""):
            errs.append(f"US spelling: '{w}' in the PDF")
    if re.search(r"[֐-׿]", txt + alldeck):
        errs.append("no Hebrew letters anywhere (none are drawn or printed)")
    for w in ("christmas", "santa", "tree", "reindeer", "snowman", "sleigh"):
        if re.search(rf"\b{w}\b", (txt + " " + alldeck).lower()):
            errs.append(f"no Christmas imagery or words in this product ({w})")
    # ---- Step N on every page, in the deck PDF text, the deck notes and UPLOAD.md agrees with the project sheet
    expect = {"stair": {2}, "cards": {2}, "tempo": {1}, "plan": {2}, "mix": {6}}
    for k in PLAN:
        t = flat[D.IX(k) - 1]
        errs += step_ref_errors(t, f"page {D.IX(k)} ({k})")
        found = {int(m.group(1)) for m in re.finditer(r"\bStep (\d+)\b", t)}
        if k in expect and found != expect[k]:
            errs.append(f"page {D.IX(k)} ({k}) should cite Step {sorted(expect[k])}, cites {sorted(found)}")
        if k not in expect and found:
            errs.append(f"page {D.IX(k)} ({k}) cites Step {sorted(found)} unexpectedly")
    errs += step_ref_errors(" ".join(stext), "deck slides")
    errs += badge_errors(flat)
    import subprocess as sp

    def raw(key):
        return re.sub(r"\s+", " ", sp.run(["pdftotext", "-raw", "-f", str(D.IX(key)), "-l", str(D.IX(key)), D.files()["pdf"], "-"],
                                          capture_output=True, text=True, check=True).stdout)
    # ---- the tempo page prints every number
    rc = raw("tempo")
    for bpm in TEMPOS:
        row = f"{bpm} {dec(spb(bpm), 3)} {dec(bar_len(bpm), 3)} {dec(sec_len(bpm), 2)} {dec(total_s(bpm), 2)}"
        if row not in rc:
            errs.append(f"tempo page: row '{row}' is not printed")
        row2 = f"{bpm} " + " ".join(dec(start_s(s, bpm), 2) for s in range(1, SECTIONS + 1))
        if row2 not in rc:
            errs.append(f"tempo page: section-start row '{row2}' is not printed")
    for need in ("Starts at bar 1 5 9 13 17 21 25 29", "Seconds per beat = 60 ÷ BPM", "Seconds per bar = 240 ÷ BPM", "32 bars = 32 × 240 ÷ BPM seconds", "240 ÷ 100 = 2.4 s per bar",
                 "4 × 2.4 = 9.6 s per section", "32 × 2.4 = 76.8 s in all", "Step 1: choose key and tempo", "5 rounds up", "10.67"):
        if need not in rc:
            errs.append(f"tempo page must say '{need}'")
    # ---- the layer map page and the worked example print their numbers
    rs = raw("stair")
    for need in ("Step 2: plan the layers", "Layers playing 1 2 3 4 5 6 7 8 36", "Layer-bars (layers × 4) 4 8 12 16 20 24 28 32 144", "Starts at bar 1 5 9 13 17 21 25 29", "Total shaded squares: 36"):
        if need not in rs:
            errs.append(f"layer map page must say '{need}'")
    re1 = (raw("example") + " " + raw("example2")).replace("- ", "-")
    for L, pat in zip(LAYERS, EX_LAYER_PATTERNS):
        i = L["n"]
        row = f"{i} {L['name']} {start_bar(i)} {fmt(start_s(i, EX_BPM))} {i} {pat}"
        if row not in re1:
            errs.append(f"worked example: entrance row '{row}' is not printed")
    for bpm in TEMPOS:
        row = f"{bpm} {dec(bar_len(bpm), 3)} {dec(sec_len(bpm), 2)} {dec(total_s(bpm), 2)} {dec(start_s(5, bpm), 2)}"
        if row not in re1:
            errs.append(f"worked example: tempo row '{row}' is not printed")
    for need in ("60 ÷ 100 = 0.600 s", "240 ÷ 100 = 2.4 s", "4 × 2.4 = 9.6 s", "32 × 2.4 = 76.8 seconds", "8 sections × 9.6 = 76.8 seconds", "(5 − 1) × 9.6 = 38.4 s",
                 "night 1 at 0, night 2 at 9.6, night 3 at 19.2, night 4 at 28.8, night 5 at 38.4, night 6 at 48, night 7 at 57.6, night 8 at 67.2",
                 "1, 2, 3, 4, 5, 6, 7, 8, which add up to 36", "144 layer-bars", "32 hits in a section", "64 seconds", "exactly 60 seconds"):
        if need not in re1:
            errs.append(f"worked example must say '{need}'")
    for k, need in (("cards", "Step 2: plan the layers"), ("plan", "Step 2: plan the layers"), ("mix", "Step 6: mix and bounce")):
        if need not in raw(k):
            errs.append(f"{k} page must say '{need}'")
    rcards = raw("cards").replace("- ", "-")
    for L in LAYERS:
        for need in (f"Night {L['n']} · {L['name']}", L["role"], L["idea"]):
            if need.lower() not in rcards.lower():
                errs.append(f"layer cards page: '{need}' is not printed")
    up = open(os.path.join(HERE, "UPLOAD.md"), encoding="utf8").read()
    errs += step_ref_errors(up, "UPLOAD.md")
    if "Grades 9-12" not in up or "`9th-grade`, `10th-grade`, `11th-grade`, `12th-grade`" not in up:
        errs.append("UPLOAD.md: grades 9-12 in the description and section 3")
    if "no audio" not in up.lower() or "Open question" not in up or "Timing numbers" not in up or "Sources and credits" not in up:
        errs.append("UPLOAD.md: must say no audio is included, record the timing numbers checked, the sources and the open questions")
    if "Ma'oz Tzur" not in up or "NO melody chart" not in up:
        errs.append("UPLOAD.md: must state that the melody chart was not included")
    m = re.search(r"= 1 cover \+ (\d+) teacher \+ (\d+) student \+ 1 terms page", up)
    if not m or 2 + int(m.group(1)) + int(m.group(2)) != len(PLAN):
        errs.append("UPLOAD.md: the page-count list (1 cover + teacher + student + 1 terms) must total the PDF's pages")
    if m and (int(m.group(1)) != D.IX("example2") - 1 or int(m.group(2)) != D.IX("reflect") - D.IX("stair") + 1):
        errs.append("UPLOAD.md: teacher and student page counts must match the plan")
    m3 = re.search(r"plus (\d+) slides = (\d+) for TpT", up)
    if not m3 or int(m3.group(1)) != len(SLIDES) or int(m3.group(2)) != len(PLAN) + len(SLIDES):
        errs.append("UPLOAD.md: slides and the total for TpT must match the deck and the PDF")
    for t in TAGS:
        if t not in up:
            errs.append(f"UPLOAD.md: tag {t} missing")
    for c in range(1, CLASSES + 1):
        if f"Class {c}:" not in up:
            errs.append(f"UPLOAD.md: the class list must name Class {c}")
    for banned in ["Billie", "Beatles", "Daft", "Skrillex", "Disney", "Radiohead", "Billboard", "Ro" + "land", "Bensound", "Ableton "]:
        if banned in alldeck or banned in txt:
            errs.append(f"must not name artists, albums, songs, sites, services or other brands ({banned})")
    # deck: no truncated bullet reaches the slides
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
    return (f"seconds per beat = 60 / BPM, per bar = 240 / BPM, per section = 4 bars and 32 bars = 32 x 240 / BPM recomputed exactly (fractions) and by an independent float "
            f"method for all {len(TEMPOS)} tempos (80, 90, 100, 110, 120, 128 BPM): every cell of the tempo table and of the section-start table, rounded half up to 3 decimals "
            f"(per beat and per bar) and 2 decimals (per section, totals, starts); the layer map is a staircase of 8 layers x 8 sections (section s plays s layers, adds exactly layer s, "
            f"no layer stops, 36 filled cells); the worked example is 32 bars at {EX_BPM} BPM = {fmt(total_s(EX_BPM))} s with entrances at 0, 9.6, 19.2, 28.8, 38.4, 48, 57.6, 67.2 s; every "
            f"'Step N' agrees with the project sheet on pages, slides, notes and UPLOAD.md; class badges agree with the pacing page; every drawing renders alone on a transparent "
            f"ground with no ink at its edges; hero art inside its viewBox; rendered-DOM footer gap on every page; no truncated slide bullets; edges of cover.png and previews clear; "
            f"no audio, lyrics, melodies, Hebrew letters, Christmas words or student work; festival text limited to checked facts; grades 9-12; tags and subjects are not headings; "
            f"no 'what changed' page (ORIGINAL).")


# ================================================================ UPLOAD.md (written by gen.py so every number matches the build)
def write_upload():
    np_, ns = len(PLAN), len(SLIDES)
    n_teacher = (PLAN.index("example2") + 1) - 1
    n_student = (PLAN.index("reflect") + 1) - (PLAN.index("stair") + 1) + 1
    assert 2 + n_teacher + n_student == np_, "page-count list must total the PDF"
    nt = len(LISTING_TITLE)
    desc = (f"{DESC_START} students build 32 bars of music in Logic Pro in eight sections of 4 bars, and every section adds one new track, so the arrangement grows from one layer to eight: "
            f"pad or drone, bass, kick and clap, hi-hat or shaker, chord stabs, arpeggio, counter-melody and lead. The structure is inspired by the eight nights of Hanukkah (Chanukah), "
            f"when one more candle is added each night; it is a music-technology project, not a religious activity, and it suits any class (students may choose a different eight-step theme). "
            f"This Eight Nights, Eight Layers project takes {CLASSES} class periods (the pacing guide also shows two and four) and is an original Hudson Beat project; "
            f"the steps are written for Logic Pro, while the ideas (layers, sections, tempo math) carry over to GarageBand.\n\n"
            f"WHAT'S INCLUDED (ZIP: {np_}-page PDF = 1 cover + {n_teacher} teacher + {n_student} student + 1 terms page, plus {ns}-slide intro deck as .pptx and PDF)\n"
            f"• Teacher pages: how to use, project overview with a short, respectful note on the festival that inspired the structure, setup, a {CLASSES}-class pacing guide with the deck slides for each class, "
            f"two pages of teacher notes (struggles, variations, resources, grading), a Logic quick reference and a two-page worked example (an invented arrangement at 100 BPM: "
            f"32 bars = 76.8 seconds, with the eight entrance times and a map) ({n_teacher} pages)\n"
            f"• Student pages: the layer map (a staircase of 8 layers by 8 sections), eight layer cards with a role, tools to try and a pattern idea, a tempo table (seconds per beat, bar and section, "
            f"the length of 32 bars and the start time of every section at 80, 90, 100, 110, 120 and 128 BPM), an arrangement plan, a mix checklist, the 3-page project sheet "
            f"(overview, goals, vocabulary, requirements, steps, tips, submission checklist), the /{RUBRIC_TOTAL} rubric, a vocabulary page, a feedback planner and a reflection page ({n_student} pages)\n"
            f"• Teacher-presented intro deck, {ns} slides with speaker notes on every slide: a think-and-share hook, what the project is, the layer map, the inspiration, seconds and bars, "
            f"the eight layers, building it in Logic, a worked-example map, what to turn in and the rubric\n\n"
            f"THE THREE CLASS PERIODS\n"
            f"• Class 1: hook; the layer map and the eight layers; choose a key, chords and a tempo; plan the layers\n"
            f"• Class 2: set up Logic with a marker at every section; build the first six layers, one per section\n"
            f"• Class 3: the counter-melody and the lead; mix, bounce, present and reflect\n\n"
            f"WHAT STUDENTS LEARN\n"
            f"• Layering: what a pad, a bass, drums, stabs, an arpeggio, a counter-melody and a lead are each for\n"
            f"• Timing math: seconds per beat = 60 ÷ BPM, seconds per bar in 4/4 = 240 ÷ BPM, and the length of 32 bars = 32 × 240 ÷ BPM (at 100 BPM, 76.8 seconds)\n"
            f"• Building in Logic Pro: markers for sections, repeating a region, a pad or lead in Alchemy or Retro Synth, Drum Machine Designer, Quick Sampler, and Session Players, "
            f"Step Sequencer or Arpeggiator if your version has them; automation, mixing and bounce\n"
            f"• Mixing so that every new layer can be heard, and explaining their choices in a reflection\n\n"
            f"GOOD TO KNOW\n"
            f"• There is no audio in this resource and no student work. No melody, song or lyrics are printed or notated; students make every sound themselves in Logic Pro. "
            f"The lead can be a melody the student writes or any melody they have the right to use\n"
            f"• Requires Logic Pro on a Mac. A MIDI keyboard is not needed; nobody has to read music. Where a control may differ between versions, the pages say \"if your version has it\"\n"
            f"• Rubric: 5 categories scored 1-5, /{RUBRIC_TOTAL}; the final grade is the average of the student's and the teacher's score\n"
            f"• Grades 9-12; music technology or music production classes\n"
            f"• The deck uses the free Oswald and Source Sans 3 fonts (built into Google Slides); install them for PowerPoint or Keynote, or present "
            f"the PDF copy, which shows the intended look\n"
            f"• Every student page prints well in black and white\n\n"
            f"Logic Pro is a product of Apple Inc., named only to describe compatibility. This resource is not affiliated with Apple.\n\n"
            f"{D.DISCLOSURE_NEW}")
    ex = ", ".join(f"night {s} at {fmt(start_s(s, EX_BPM))} s (bar {start_bar(s)})" for s in range(1, SECTIONS + 1))
    tbl = "; ".join(f"{b} BPM: {dec(bar_len(b), 3)} s per bar, {dec(sec_len(b), 2)} s per section, {dec(total_s(b), 2)} s in all" for b in TEMPOS)
    md = f"""# UPLOAD: Eight Nights, Eight Layers, original Logic Pro project (TpT 063)

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
({nt} characters; the limit is 80.) The title leaves out Hanukkah, Chanukah, Winter, Holiday and Christmas because TpT's Seasonal Titles notice blocked a holiday-named title on 027 (see 032, 033 and 034). "Logic Pro" sits in the first 30 characters.

## 2. Description

```
{desc}
```

## 3. Grades

9th, 10th, 11th, 12th (`9th-grade`, `10th-grade`, `11th-grade`, `12th-grade` in tpt.json), as tpt/METADATA-GUIDE.md prescribes for every music-production item.

## 4. Subjects and tags

- Subjects in tpt.json: Music; Computer Science - Technology; Music Composition (all three are in `tpt/SUBJECT-OPTIONS.json` and none is a heading)
- Tags in tpt.json: {", ".join(TAGS)} (four exact entries of `tpt/TAG-OPTIONS.json`; the limit is 6). "Holiday" and "Student Practice" are headings and are not used; "Christmas-Chanukah-Kwanzaa" is a real tag entry and fits the Hanukkah inspiration.
- Formats: PDF (add PowerPoint or ZIP if TpT offers it)
- Answer key: left out of tpt.json (there is none; the worked example is a model)

## 5. Resource type

- Projects
- Unit Plans
- PowerPoint Presentations

## 6. Standards (optional)

National Core Arts Standards, Music (Music Technology, high school): MU:Cr1.1, MU:Cr2.1, MU:Pr6.1, MU:Re7.2. Tag only if it matches how the teacher uses it.

## 7. Price

**${PRICE}** (paid), multiple-license price ${PRICE}. Inside the $7-9 holiday-kit range, for a kit with {np_} pages + {ns} slides, a layer map, eight layer cards, tempo tables, an arrangement plan, a mix checklist and a two-page worked example, listed in November and December.

## 8. Free or paid / free preview pages

Paid. Preview PDF (4 watermarked pages): the {CLASSES}-class pacing guide, the layer map, the tempo table and the /{RUBRIC_TOTAL} rubric. "Number of pages or slides" is {np_ + ns} ({np_} pages + {ns} slides).

## 9. Sources and credits

- Art: the cover, previews and deck use the owner's pre-made art (`art/hero.png`, a nine-candle menorah with studio gear, no text), copied whole from `tpt/_art/next/eight-nights-eight-layers/`; the file is logged in `tpt/_art/USAGE.md`. It shows a menorah with nine lights (eight plus the helper) and no letters. Everything else is drawn in code.
- Festival facts (each is one plain sentence in the product): Hanukkah (also Chanukah) is an eight-night Jewish festival of lights that remembers the rededication of the Second Temple in Jerusalem in the 2nd century BCE; it begins on 25 Kislev, which falls in late November or December (no year or date is printed); a hanukkiah (menorah) has nine branches, eight plus the shamash (helper); one new candle is added each night. Sources: Encyclopaedia Britannica, "Hanukkah"; Jewish Virtual Library, "Hanukkah"; My Jewish Learning, "Hanukkah".
- Music: nothing is notated or printed. **Ma'oz Tzur (Rock of Ages) melody: NO melody chart is included.** It is a traditional Hanukkah song, but two independent public-domain transcriptions could not be checked note by note in this build, so the kit says only that a class may bring a notated copy it has the right to use. The lead layer is the student's own melody.
- Fonts: Oswald and Source Sans 3 (SIL OFL 1.1). Logic Pro is named only to describe compatibility.

## 10. Before you click publish

- [ ] **Needs QA approval first.** This is a new kit (not yet on TpT); the Manager releases it only after a QA `**Verdict: APPROVED**`.
- [ ] Cover and previews show "HUDSON BEAT" in type; PDF footers read "© 2026 Brian Lotze · Hudson Beat · For single-classroom use".
- [ ] No school name, logo, student names or work, audio, video, lyrics, melody, song title or Logic session anywhere (`gen.py --check` scans every output and every file in this folder).
- [ ] **Cultural accuracy.** The festival is described in two short, neutral paragraphs (overview page and slide 6) and called an inspiration for the structure; no claim about how families celebrate; no Hebrew letters, no dreidel, no Christmas imagery; the menorah art has nine lights (4 + shamash + 4). `gen.py --check` fails on Hebrew letters, Christmas words and any year in the festival text.
- [ ] **Timing numbers (all recomputed in `gen.py --check`, exactly with fractions and again with an independent float method).** Seconds per beat = 60 / BPM; seconds per bar in 4/4 = 240 / BPM; a section is 4 bars; the arrangement is 8 sections = 32 bars = 32 x 240 / BPM seconds; section s starts at (s - 1) x 4 x 240 / BPM seconds and at bar 4 (s - 1) + 1. Rounding: seconds per beat and per bar to 3 decimals, per section, totals and start times to 2 decimals, half up. Table: {tbl}. Worked example at 100 BPM: {ex}; the layers playing in sections 1 to 8 are 1 to 8 (36 layer-sections, 144 layer-bars); the layer map is a staircase of 8 rows by 8 columns, verified in code (section s plays s layers and adds exactly layer s).
- [ ] **Original project.** Built with `ORIGINAL = True` in `tpt/_dmp2_common/dmp2.py` (like 031, 036, 053, 057 and 061): no "what changed" page and the new disclosure line. The reflection page is the shared Reflection element, scored in the rubric's "Plan & Reflection" row. `dmp2.py` is unchanged.
- [ ] **Logic Pro names to confirm on a Mac with a current Logic.** The Marker global track with a plus (+) button and a Create Marker key command (hedged), repeating a region (Loop option or dragging the corner; hedged), Session Players (Drummer, Bass Player; "if your version has it"), Alchemy and Retro Synth patches, Drum Machine Designer, Quick Sampler, Step Sequencer and the Arpeggiator MIDI plug-in ("if your version has it"), Channel EQ, Scale Quantize (hedged), automation (A), Mixer (X), Command-B bounce. Nothing says a loop or preset of a given name exists.
- [ ] **Open questions for the owner:** (1) **Melody.** No Ma'oz Tzur chart; if you want one, supply two public-domain scores to check. (2) **Title.** No Hanukkah, Chanukah, Winter, Holiday or Christmas in the title because of TpT's seasonal-title notice (see 1). (3) **Price.** ${PRICE}, inside the $7-9 range. (4) **Classes.** Three periods; the pacing page shows how to run it in two or four.
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


# ---- footer clearance: nothing in a page's content area may sit on the footer rule (shared dmp2.py stays untouched; patched here only)
FOOT_GAP = 8        # --check: smallest allowed gap (CSS px at the render scale, 96 per inch) between any content box and the footer rule
D.CSS += ".main { padding-bottom: 10px; }\n"       # reserves 10 px above the footer rule on every page; ruled lines and boxes end before it
GAP_JS = r"""
const { chromium } = require('playwright');
const url = require('url');
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto(url.pathToFileURL(process.argv[2]).href, { waitUntil: 'load' });
  await page.evaluate(() => document.fonts.ready);
  await page.emulateMedia({ media: 'print' });
  const res = await page.evaluate(() => [...document.querySelectorAll('section.page')].map((s, i) => {
    const f = s.querySelector('.foot'), m = s.querySelector('.main');
    let gap = null, who = '';
    if (f && m) {
      const rule = f.getBoundingClientRect().top;
      let maxb = -1e9;
      m.querySelectorAll('*').forEach(el => {
        if (el.closest('svg') && el.tagName.toLowerCase() !== 'svg') return;
        const r = el.getBoundingClientRect();
        if (r.width && r.height && r.bottom > maxb) { maxb = r.bottom; who = el.tagName + '.' + el.className; }
      });
      gap = rule - maxb;
    }
    return { page: i + 1, key: s.dataset.key, gap: gap, who: who };
  }));
  require('fs').writeFileSync(process.argv[3], JSON.stringify(res));
  await browser.close();
})().catch(e => { console.error(e); process.exit(1); });
"""


def footer_gap_errors():
    """Rendered-DOM check: on every page of the product PDF and of the preview PDF, the lowest content box, ruled line or text block is at
    least FOOT_GAP px above the footer rule (the cover has no footer and is skipped)."""
    errs = []
    js = D.write("gap.js", GAP_JS)
    for name, label in (("resource.html", "PDF"), ("preview.html", "PREVIEW")):
        html = os.path.join(D.build_dir(), name)
        if not os.path.exists(html):
            errs.append(f"{name} missing: run python3 gen.py before --check")
            continue
        out = os.path.join(D.build_dir(), "gap-" + name + ".json")
        subprocess.run(["node", js, html, out], check=True, env=D.node_env())
        for o in json.load(open(out)):
            if o["gap"] is not None and o["gap"] < FOOT_GAP:
                errs.append(f"{label} page {o['page']} ({o['key']}): content ({o['who']}) ends {o['gap']:.1f}px above the footer rule (< {FOOT_GAP}px)")
    return errs


if __name__ == "__main__":
    if "--check" not in sys.argv:
        write_upload()
        D.deck_art = deck_art_transparent
    D.main(sys.modules[__name__])
