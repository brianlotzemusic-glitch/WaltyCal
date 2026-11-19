#!/usr/bin/env python3
"""Logic Pro project kit: Snow Day Film Score (TpT 061): the teacher resource, the intro deck and the listing files.

    python3 gen.py            build everything into this folder (also writes UPLOAD.md)
    python3 gen.py --lowres   same, but square images at scale 1 and small page shots (self-check only; --check rejects it)
    python3 gen.py --check    verify content and layout: the hit-point arithmetic (seconds per beat = 60 / BPM, seconds per bar in 4/4 =
                              240 / BPM, bar number = 1 + t / (240 / BPM), the sixteenth-note rounding rule), every cell of the
                              hit-point calculator table (20 s at 80, 96, 100, 120 and 128 BPM), the worked example (4 hit points at
                              96 BPM, 8 bars), the three storyboards (5 frames of 4 s = 20 s), Step N references on every page,
                              slide and UPLOAD.md, class badges against the pacing page, drawings (each rendered alone on a
                              transparent ground: no ink within 4 px of its edge; each storyboard frame keeps its art inside its box),
                              the hero art, files, page and slide counts, class slots, fonts, fit and overlap, dead space, truncated
                              slide bullets, the edges of cover.png and the previews, banned strings, tpt.json and UPLOAD.md

An ORIGINAL Hudson Beat project (dmp2.ORIGINAL = True, like 045, 048, 053 and 057). Students score a 20-second winter scene they film
on a phone or take from one of three printable storyboards: they name the mood and emotional arc, mark HIT POINTS on a timeline, choose
a tempo so the hit points land on beats or bars, and build a score from four layers in Logic Pro. No melody is prescribed and no audio
ships. The art on the cover, the previews and the deck is the owner's pre-made hero (art/hero.png), used whole. Everything else
(storyboard frames, timelines, the score map) is drawn in code. The shared builder is ../_dmp2_common/dmp2.py.
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
SLUG = "snow-day-film-score"
TITLE = "Snow Day Film Score"
ACCENT = "#2F7FB8"          # this product's single accent: icy blue (a shade deeper than the art's #4FA3D9, so small labels read)
ACC_LIGHT = "#DCEBF6"
PRICE = "9.00"
CLASSES = 3
GRADES_TEXT = "9–12"
GRADE_SLUGS = ["9th-grade", "10th-grade", "11th-grade", "12th-grade"]
TAGS = ["Winter", "Project-based Learning", "Projects", "Activities"]     # exact entries of tpt/TAG-OPTIONS.json, none a heading
SUBJECTS = ["Music", "Computer Science - Technology", "Music Composition"]     # all in SUBJECT-OPTIONS.json, none a heading
ANSWER_KEY = None
LISTING_TITLE = "Logic Pro Film Scoring | Hit Points, Tempo & Mood | High School Music Tech"
DESC_START = "Film scoring for high school music technology:"
DESC_MUST = ["Snow Day Film Score", "hit point", "storyboard", "no audio", "seconds per beat", "20-second", "96 BPM", "Movie"]
ZIP_DIR = "Snow Day Film Score - Hudson Beat"
ZIP_DATE = (2026, 11, 19, 12, 0, 0)
TYPE = "Original Project"
PROJ_LINE = "Music Technology | <i>Film Scoring Project</i> | 3 class periods"
DECK_STRAP = "Film scoring"
REFLECT_ROW = "Plan &amp; Reflection"
# split so this file never contains them (the --check scan reads every file in this folder)
BANNED_EXTRA = ["Rud" + "olph", "Fro" + "sty", "Gri" + "nch", "Santa Claus " + "Is", "Jingle Bell " + "Rock", "Feliz " + "Navidad",
                "Mari" + "ah Carey", "Spoti" + "fy", "You" + "Tube", "Home " + "Alone", "Nin" + "tendo", "Ro" + "land",
                "Star " + "Wars", "Hans " + "Zimmer", "John " + "Williams", "Harry " + "Potter", "Pix" + "ar", "Lord of the " + "Rings",
                "Winter " + "Wonderland", "Let It " + "Snow", "Sleigh " + "Ride"]

# ================================================================ page plan (teacher pages 2-10, student pages 11-24)
PLAN = ["cover", "howto", "overview", "setup", "pacing", "tn1", "tn2", "logicref", "example", "example2", "board1", "board2", "board3", "mood",
        "spot", "calc", "layers", "proj1", "proj2", "proj3", "rubric", "vocab", "present", "reflect", "terms"]


def pg(k):
    return PLAN.index(k) + 1


# ================================================================ the hit-point arithmetic (exact fractions; all verified in --check)
SCENE_S = 20                                # every scene lasts 20 seconds
TEMPOS = (80, 96, 100, 120, 128)            # the calculator's tempos
TEMPO_LO, TEMPO_HI = 80, 128                # the project's tempo range
CALC_TIMES = (2, 4, 5, 6, 8, 10, 12, 14, 15, 16, 18, 20)    # hit-point times (seconds) in the calculator table
EX_BPM = 96                                 # the worked example's tempo: 20 s = 8 bars exactly


def Fx(x):
    return Fraction(str(x))


def spb(bpm):
    """Seconds per beat = 60 / BPM."""
    return Fraction(60, bpm)


def bar_len(bpm):
    """Seconds per bar of 4/4 = 240 / BPM (four beats)."""
    return Fraction(240, bpm)


def bar_pos(t, bpm):
    """Bar number of time t (seconds): 1 + t / (240 / BPM). A whole number is the downbeat of that bar; .25 is beat 2, .5 beat 3, .75 beat 4."""
    return 1 + Fx(t) / bar_len(bpm)


def beats_from(t, bpm):
    """Beats from the start of the scene: t x BPM / 60."""
    return Fx(t) * bpm / 60


def rnd(x, nd):
    """Round half up (a 5 rounds up) to nd decimals, on exact fractions."""
    s = Fraction(10) ** nd
    return Fraction(math.floor(Fraction(x) * s + Fraction(1, 2)), 1) / s


def dec(x, nd):
    return f"{float(rnd(x, nd)):.{nd}f}"


def sixteenths(t, bpm):
    """The marker rounding rule: sixteenth notes from the start = t x BPM / 60 x 4, rounded (half up) to a whole number."""
    return math.floor(beats_from(t, bpm) * 4 + Fraction(1, 2))


def bar_beat(t, bpm):
    """(bar, beat) after rounding to the nearest sixteenth note: bar = idx // 16 + 1, beat = 1 + (idx mod 16) / 4."""
    i = sixteenths(t, bpm)
    return i // 16 + 1, 1 + Fraction(i % 16, 4)


def bb_text(t, bpm):
    b, k = bar_beat(t, bpm)
    return f"{b} · {float(k):g}"


def off_ms(t, bpm):
    """How far (ms) the time is from its nearest sixteenth note."""
    i = sixteenths(t, bpm)
    return abs(Fx(t) - Fraction(i, 4) * spb(bpm)) * 1000


def grid_class(t, bpm):
    x = beats_from(t, bpm)
    if x.denominator == 1:
        return "beat"
    if (2 * x).denominator == 1:
        return "half beat"
    if (4 * x).denominator == 1:
        return "sixteenth"
    return "off"


def lands_text(t, bpm):
    c = grid_class(t, bpm)
    return c if c != "off" else f"off by {int(rnd(off_ms(t, bpm), 0))} ms"


def on_beat(t, bpm):
    return grid_class(t, bpm) == "beat"


def fmt(x):
    x = float(x)
    x = round(x + 1e-9, 3)
    return f"{x:.0f}" if x == int(x) else f"{x:g}"


# ================================================================ the three storyboards: 5 frames of 4 seconds each (20 s)
FRAME_S = 4
BOARDS = [
    dict(key="board1", num=1, name="Snow-day morning", sub="A child wakes up to a world covered in white",
         frames=["Snow falls past the window", "Boots wait by the door", "The door opens on bright white", "A first step into deep snow", "Arms wide, looking up"],
         art=["a1", "a2", "a3", "a4", "a5"]),
    dict(key="board2", num=2, name="Sledding", sub="A child rides a sled down a long, snowy hill",
         frames=["A sled waits at the top", "The push-off", "Trees blur past", "A bump: the sled leaps", "A soft landing in a snow pile"],
         art=["b1", "b2", "b3", "b4", "b5"]),
    dict(key="board3", num=3, name="Snowman building", sub="A snowman grows from one small snowball",
         frames=["An empty yard and one small snowball", "Rolling the snowball bigger", "Stacking the big balls", "A hat and a scarf go on", "Snow starts again: the finished snowman"],
         art=["c1", "c2", "c3", "c4", "c5"]),
]


def board(k):
    return next(b for b in BOARDS if b["key"] == k)


def frame_span(i):
    """Frame i (0-based) runs from i x 4 s to (i + 1) x 4 s."""
    return i * FRAME_S, (i + 1) * FRAME_S


# ================================================================ the project text (original; students read these pages)
OVERVIEW = ("Score a 20-second winter scene. Film a short scene on a phone, or choose one of the three storyboards in this kit: a snow-day "
            "morning, sledding or snowman building. Name the scene’s mood and trace how the feeling changes. Watch it with the sound off and "
            "mark the hit points, the key moments where the music must land. Choose a tempo so the hit points fall on beats or bars: a hit "
            "point at time t seconds is at bar number 1 + t ÷ (240 ÷ BPM). Then, in Logic Pro, build the score from four layers: a pad, "
            "a motif of your own, percussion hits and foley or sound-design accents. Nobody needs to read music, and no melody is given.")
GOALS = ["Name the mood of a 20-second winter scene and describe how its feeling changes from start to finish, its emotional arc",
         "Spot the scene: mark 3 to 6 hit points with their times in seconds and say what each one needs",
         "Choose a tempo so the hit points land on beats or bars, using seconds per beat = 60 ÷ BPM and seconds per bar = 240 ÷ BPM in 4/4",
         "Score the scene in Logic Pro with a pad, a motif, percussion hits and foley accents, then mix and bounce it"]
VOCAB = [("Hit point", "A key moment in a scene, such as a door opening or a sled leaping, where a sound or a change in the music lands exactly on the picture"),
         ("Spotting", "Watching a scene closely to decide where music is needed and what each moment needs; the notes you take are your spotting notes"),
         ("Motif", "A short musical idea of a few notes that you invent and bring back, changed, as the mood of the scene changes"),
         ("Foley", "Everyday sounds recorded or made by hand to match the picture, such as footsteps in snow or the creak of a door")]
REQS = ["Use a 20-second scene: film your own on a phone (with no music in it) or choose one of the three storyboards (pages @BOARD1–@BOARD3)",
        "Name the scene’s mood and draw its emotional arc on the Mood and arc page (page @MOOD)",
        "Mark 3 to 6 hit points with their times in seconds on the spotting sheet (page @SPOT)",
        "Choose a tempo from 80 to 128 BPM in 4/4 and show the arithmetic for every hit point: bar number = 1 + t ÷ (240 ÷ BPM) (pages @SPOT and @CALC)",
        "In Logic Pro, set your tempo and put a marker on every hit point; if you filmed the scene, import the movie so you can see it (page @LOGICREF)",
        "Score it with four layers: a pad, a motif of your own, percussion hits on the hit points and foley or sound-design accents (page @LAYERS)",
        "Mix with volume or filter automation, bounce your score, then reflect (page @REFLECT)"]
FILE_NAME = "“Your Name – Snow Day Film Score”"
STEP_NAMES = ["Choose the scene", "Spot it", "Pick a tempo", "Set up Logic", "Build the layers", "Mix and bounce", "Present &amp; get feedback"]
STEPS = ["<b>Choose the scene</b> — Film a 20-second winter scene or pick a storyboard (pages @BOARD1–@BOARD3), then name its mood and sketch its arc (page @MOOD)",
         "<b>Spot it</b> — Watch the scene with the sound off and mark 3 to 6 hit points with their times in seconds on the spotting sheet (page @SPOT)",
         "<b>Pick a tempo</b> — Use the calculator tables (page @CALC) to find a tempo from 80 to 128 BPM where your hit points land on beats or bars, then fill in their bar numbers (page @SPOT)",
         "<b>Set up Logic</b> — Open a project at your tempo in 4/4, import the movie if you filmed one, and put a marker on every hit point (Logic quick reference: page @LOGICREF)",
         "<b>Build the layers</b> — Plan and play a pad, a motif of your own, percussion hits and foley accents, one layer at a time (page @LAYERS)",
         "<b>Mix and bounce</b> — Draw volume or filter automation, balance the layers, then bounce your score and name the file as on the checklist",
         "<b>Present &amp; get feedback</b> — Write three questions you want classmates to answer about your score. Play it with the scene, point out each hit point, "
         "and answer at least 2 of each classmate’s questions. Then reflect (page @REFLECT)."]
TIPS = ["Watch the scene with the sound off at least three times before you mark a single hit point.",
        "Fewer, bigger hit points work better than many small ones: three to six is plenty for 20 seconds.",
        "Leave space. A quiet moment just before a hit point makes the hit feel bigger.",
        "Save a new version of your project before each big experiment, so you can always go back."]
CHECK = ["Bounced .mp3 or .wav of your score handed in, about 20 seconds long",
         "Zipped .logicx project file handed in",
         f"Files named correctly: {FILE_NAME}",
         "Mood and arc, spotting sheet and layer plan handed in",
         "Rubric self-score done (page @RUBRIC)",
         "I can name each hit point, its time and its bar number"]
RUBRIC_NOTE = "Each category is scored 1–5. Score yourself first; the final grade is the average of your score and your teacher’s."
LEVELS = [1, 2, 3, 4, 5]
RUBRIC = [
    ("Mood & Spotting", ["No clear mood and no hit points marked", "A mood is named, but fewer than 3 hit points or no times",
                         "Mood and arc described; 3 hit points marked with times",
                         "Clear mood and arc; 3 to 6 hit points with times and what each one needs",
                         "Arc and hit points tell a story; each hit point is ranked with a reason"]),
    ("Tempo & Timing Math", ["No tempo and no arithmetic", "A tempo is chosen, but bar numbers are missing or wrong",
                              "Bar numbers shown for each hit point, with small errors",
                              "A tempo chosen on purpose; bar number and bar · beat correct for every hit point",
                              "Correct math and a comparison of two tempos, with a reason"]),
    ("Layers & Sound", ["One sound only", "Fewer than 3 of the 4 layers, or layers that cannot be told apart",
                        "All four layers present; some sounds do not fit the mood",
                        "All four layers with clear jobs; the motif is the student’s own; accents land on hit points",
                        "Layers enter and leave to follow the arc; foley adds real detail"]),
    ("Sync & Mix", ["Nothing lines up with the picture", "A few hits land on the picture; most are early or late",
                    "Most hit points land; some balance problems",
                    "Every hit point lands on its moment; automation used; the layers are balanced",
                    "Hits land exactly; automation shapes the swells; the mix is clear"]),
    ("Plan & Reflection", ["Plans, presentation or reflection missing", "Thin plan; little to say about choices",
                           "Plan and reflection complete, with basic detail", "Clear plan; thoughtful reflection and good answers to questions",
                           "Insightful reflection and a polished, confident presentation"]),
]
RUBRIC_TOTAL = 25
RUBRIC_SHORT = [ds[4] for _, ds in RUBRIC]
RUBRIC_SLIDE_LINE = "Scored 1–5 · final grade = average of your score and mine, out of 25"
RUBRIC_ROW_PITCH = 0.86
RUBRIC_LINE_Y = 6.3

TN_REINFORCES = ("Teaches how film music is planned. Students learn to watch a scene for its mood and its key moments, to turn a time in seconds "
                 "into a bar and a beat with simple arithmetic, and to build a score from layers in Logic Pro, with a tempo chosen so that "
                 "the music lands on the picture.")
STRUGGLES = ["No hit points stand out: ask what changes on the screen, such as a door opening or a sled leaping, and what a viewer would gasp at. "
             "Mark only those (page @SPOT).",
             "The arithmetic looks hard: give students the calculator tables (page @CALC), work one hit point aloud with the formula "
             "bar number = 1 + t ÷ (240 ÷ BPM), and let them check it by moving a marker in Logic.",
             "A hit lands late or early in Logic: check that the movie starts at the very beginning of the project, that the tempo is the one on the "
             "spotting sheet and that each marker sits where the sheet says (page @LOGICREF).",
             "The score is too busy and covers the picture: take a layer away, turn the pad down and leave a little silence before each hit point."]
VAR_EASY = ("Use one of the three storyboards, choose just 3 hit points, use only the pad and the percussion hits, and work at 96 BPM, where the "
            "20 seconds are exactly 8 bars (page " + str(pg("calc")) + ").")
VAR_HARD = ("Film your own scene and plan two tempos, such as 96 and 120 BPM, then compare how the hit points land at each (page " + str(pg("calc")) + "). Or ask "
            "for a score that changes mood at a hit point, with a different motif before and after it.")
RESOURCES = [("The three storyboards (pages @BOARD1–@BOARD3)",
              "Printable scenes of five frames, 4 seconds each. Students who cannot film use one; the timeline under each board is where hit points are marked."),
             ("Mood and arc page (page @MOOD)",
              "A word bank and a blank arc, so students decide what the scene feels like before any music is made."),
             ("Spotting sheet and calculator tables (pages @SPOT–@CALC)",
              "Hit points in seconds turn into bars and beats at 80, 96, 100, 120 and 128 BPM; every number in the tables is computed, not estimated."),
             ("Worked example (pages @EXAMPLE–@EXAMPLE2)",
              "An invented 20-second ice-skating scene with 4 hit points at 96 BPM, planned on paper. Use it as a model, not a template.")]
TN_NOTE = ("A good listening day: show a few seconds of each student’s scene with no sound and let the class guess where the hit points are, then play the "
           "score and see whether the class and the student agree. This kit prints no film music and names no films.")
GRADING = ["The rubric: five categories, each scored 1–5, /25 (page @RUBRIC). Students score themselves first; the final grade is the "
           "average of their score and yours.",
           "Mood & Spotting (rubric row 1): read the Mood and arc page (page @MOOD) and the spotting sheet (page @SPOT). Are the hit points real moments, with times?",
           "Tempo & Timing Math (rubric row 2): recompute one hit point with the student: bar number = 1 + t ÷ (240 ÷ BPM) (page @CALC).",
           "Layers & Sound (rubric row 3): open the project and compare the layers with the plan (page @LAYERS). Is the motif the student’s own?",
           "Sync & Mix (rubric row 4): play the bounce against the scene and listen at each marker. Does the sound land on the moment?",
           "Plan & Reflection (rubric row 5): the layer plan, the feedback questions and the Reflection page (page @REFLECT) are the evidence."]
PACING = [
    {"n": 1, "owner": "Watch, feel and spot the scene.",
     "do": "Slides 1–6: the think-and-share, what the project is, the three classes, the scene and its mood, and spotting. Hand out the storyboards, the Mood "
           "and arc page and the spotting sheet. Before they leave, students have a scene, a mood word and at least two hit points with times.",
     "slides": (1, 6), "pages": ["board1", "board2", "board3", "mood", "spot", "proj1", "proj2", "proj3", "vocab"],
     "deck": "Silence or sound? · mood and arc · spotting"},
    {"n": 2, "owner": "Turn times into bars, pick a tempo and start building.",
     "do": "Slides 7–9: seconds to bars, the four layers and building in Logic. Work one hit point aloud with the formula. Students finish the spotting sheet, "
           "choose a tempo with the calculator tables, set up Logic with a marker on each hit point and start the pad and the motif. Walk the room with one "
           "question: which beat does this hit point land on?",
     "slides": (7, 9), "pages": ["spot", "calc", "layers", "present"], "deck": "Seconds to bars · four layers · build it in Logic"},
    {"n": 3, "owner": "Finish the layers, mix, bounce, present and reflect.",
     "do": "Slides 10–14: the worked example, what to turn in, the rubric and presentation day. Students add the percussion hits and the foley accents, draw "
           "automation, mix and bounce, then present.",
     "slides": (10, 14), "pages": ["layers", "rubric", "present", "reflect"], "deck": "20 seconds, 8 bars · checklist · rubric · presentations"},
]
PACING_EXTRA = (
    '<div class="cols" style="margin-top:4pt;gap:14pt"><div class="box acc-b"><span class="k">The one thing to do on Class 1</span>'
    '<p style="margin:0;font-size:10.6pt">Make sure every student leaves with a scene (their own clip or a storyboard), one word for its mood and at least two hit '
    'points with times in seconds. Tap the seconds on a phone timer while the scene plays, so the times are real and not guesses.</p></div>'
    '<div class="box"><span class="k">With two or four periods</span><p style="margin:0;font-size:10.6pt"><b>Two classes:</b> Class 1 is the scene, the mood and the spotting '
    'sheet; Class 2 is the tempo, the layers, the mix and short presentations. <b>Four classes:</b> keep Classes 1 and 2, then spend Class 3 on the percussion hits, the '
    'foley accents and the mix, and Class 4 on bouncing, presentations and reflection.</p></div></div>')
PACING_SIZE = 10.6

SONG_NOTE = ("No audio, recordings, lyrics, artists, albums or films are named or included, and no melody is notated. Students make every "
             "sound themselves, from the instruments, samples and recordings in Logic.")
CREDITS = ["The storyboards, the hit-point calculator, the timeline and arc drawings, the worked example and the spotting sheet: original work, Hudson Beat. "
           "No melodies, lyrics, recordings, films or published editions are included.",
           "The cover illustration was made with digital and AI tools. No audio, video, album art, screenshots, presets, templates, links or "
           "chart data from other sources are included. No student work is included."]
LOGIC_INTRO = ("Where to find the tools a Snow Day Film Score is likely to use. Demonstrate what your class needs on Classes 1 and 2 and then "
               "let students work. Names are from current Logic Pro versions; labels move between versions, so check yours.")
LOGIC_REF = [("Project and tempo", "File › New…, then a Software Instrument track to start. Set the project tempo in the control bar to the number on your "
              "spotting sheet and keep the time signature at 4/4. The hit-point arithmetic only works at that tempo, so set it first."),
             ("Import the movie", "If you filmed the scene, choose File › Open Movie… (look for it in the File menu; the wording can differ by version) and pick the video "
              "file. Logic shows the picture in a Movie window and, if you switch it on, in the Movie global track above the tracks. Check that the first frame sits at the very "
              "start of the project. With a storyboard there is no movie: use the frame times printed on the board."),
             ("Seconds as well as bars", "While you place markers, switch the control bar display to time, if your version offers it. Time may show as timecode (hours, minutes, "
              "seconds, frames): the last number counts frames, not hundredths of a second, so 6.25 seconds is not 6:25."),
             ("Markers on the hit points", "Show the Marker global track (the Global Tracks controls or the View menu). Add a marker with the plus (+) button in "
              "that track, or with a Create Marker key command if your version has one, then drag or type it to the bar and beat on your spotting sheet. Name it for its moment, "
              "such as Door opens."),
             ("Pad", "Make a Software Instrument track and open Alchemy or Retro Synth, then look in the Library for a soft pad sound with a slow attack, so each note fades in. "
              "Play long, slow notes or chords that fit the mood. A pad is a background color, not a tune."),
             ("Motif", "Add another Software Instrument track and invent a motif of 3 to 5 notes. Click it in, or play it, and bring it back changed (slower, higher, softer) as the mood "
              "changes. To stay in key, use only the white keys, or switch on Scale Quantize if your version has it. This kit gives no melody: the motif must be yours."),
             ("Percussion hits", "Make a Drum Machine Designer track (click the instrument slot and choose it), or use Quick Sampler. Give a pad a big, short sound such as a soft drum, a "
              "cymbal swell or a low boom, and place one hit exactly on each marker. Zoom in until the hit starts on the line of its bar and beat."),
             ("Foley and sound-design accents", "Open Quick Sampler (a pad in Drum Machine Designer has one) to import a sound or, if your version offers it, record your own with "
              "the Mac’s microphone: a crunch of snow, a door, a zip. Squeezing a bag of cornstarch is a classic stand-in for steps in snow. If your version has it, reverse or "
              "pitch the sound to make a whoosh."),
             ("Automation, mix and bounce", "Press A to show automation, choose a parameter such as track volume (or the filter cutoff in Alchemy or Retro Synth) and click points to draw "
              "it: fade the pad up before a hit point and let it fall after. Press X for the Mixer. Then File › Bounce › Project or Section (Command-B), MP3 or WAV, for the 20 seconds of "
              "the scene. In Finder, Control-click the .logicx and choose Compress.")]
PRESENT_CHECK = [f"Files named {FILE_NAME}; the .mp3 or .wav and the zipped .logicx handed in",
                 "Reflection page done (page @REFLECT)", "Three questions for classmates written",
                 "Rubric self-score done (page @RUBRIC)"]
VOCAB_PROMPT = "Where it shows up in my score:"
TN1_EXTRA = (
    '<div class="box acc-b" style="margin-top:4pt"><span class="k">Where this kit helps with each struggle</span><ul style="margin:0">'
    '<li style="font-size:12pt;margin-bottom:3pt">Hit points that do not stand out: the storyboards (pages @BOARD1–@BOARD3) show five clear moments each, and the spotting sheet (page @SPOT) asks for a size for every hit point.</li>'
    '<li style="font-size:12pt;margin-bottom:3pt">The arithmetic: the calculator tables (page @CALC) give the bar and beat for 12 times at 5 tempos, and the worked example (pages @EXAMPLE–@EXAMPLE2) shows every step.</li>'
    '<li style="font-size:12pt;margin-bottom:3pt">Late or early hits: the Logic quick reference (page @LOGICREF) covers the movie, the markers and the time display.</li>'
    '<li style="font-size:12pt;margin-bottom:0">A busy score: the layer plan (page @LAYERS) shows when each layer enters, and the Mood and arc page (page @MOOD) matches the sound to the feeling.</li></ul></div>')
TN1_SIZE = 12.0
PROJ_SIZE = 11.8
VOCAB_GAP = 22
LOGIC_SIZE = 9.3
PROJ1_EXTRA = ""
RUBRIC_EXTRA = ""

# ================================================================ the worked example: an invented 20-second ice-skating scene at 96 BPM
EX_BARS = 8
EX_BAR_S = bar_len(EX_BPM)                  # 2.5 s
EX_HITS = [(2.5, "The skater steps onto the ice", "small", "a soft hit and a blade scrape"),
           (6.25, "The first spin begins", "medium", "a cymbal swell into a drum hit"),
           (12.5, "A wobble", "big", "a low boom and a creak"),
           (17.5, "The skater stops and bows", "medium", "a soft hit and a snow-crunch stop")]
EX_MOODS = [("Calm", 0, 2.5), ("Joy", 2.5, 12.5), ("Tension", 12.5, 17.5), ("Relief", 17.5, 20)]
EX_LAYERS = [("Pad", [(1, 8)], "one soft pad all the way through"),
             ("Motif", [(2, 5), (8, 8)], "enters at hit point 1; a quiet echo in bar 8"),
             ("Percussion hits", None, "one hit on every marker"),
             ("Foley accents", None, "a sound on every marker")]
EX_AUTO = "Pad filter opens in bars 2–5, closes in bars 6–7 for the tension, opens again at hit point 4 for the relief"
EX_WEAK = "I will make sad winter music for my skating video."
EX_STRONG = ("My scene is 20 seconds of ice skating. The mood starts calm, turns joyful, becomes tense during a wobble and ends in relief. I marked four hit points: "
             "2.5 s (the skater steps onto the ice), 6.25 s (the first spin), 12.5 s (the wobble) and 17.5 s (the bow). I chose 96 BPM in 4/4, so one beat lasts "
             "60 ÷ 96 = 0.625 seconds and one bar lasts 240 ÷ 96 = 2.5 seconds. That puts the hit points at bar 2 beat 1, bar 3 beat 3, bar 6 beat 1 and bar 8 beat 1, "
             "and the scene is exactly 8 bars long. A soft pad plays throughout, my motif enters at the first hit point, and a drum hit and a foley sound land on each marker.")
EX_QUESTIONS = ["Which hit point felt biggest, and what sound made it big?",
                "Did the mood change when you expected it to? What told you?",
                "Which layer would you take away first, and why?"]
EX_TIMES = [h[0] for h in EX_HITS]


# ================================================================ drawings (all in code, labels logged for the fit check)
def padded(body, W, H, M=10):
    """Wrap a drawing's body with M units of clear padding on all four sides (wider than the thickest outer stroke), so no edge pixel is ever inked."""
    return f'<g transform="translate({M},{M})">{body}</g>', W + 2 * M, H + 2 * M


SK = 'stroke="#000" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"'


def flake(x, y, r):
    out = []
    for a in (0, 60, 120):
        dx, dy = r * math.cos(math.radians(a)), r * math.sin(math.radians(a))
        out.append(f'<line x1="{x - dx:.1f}" y1="{y - dy:.1f}" x2="{x + dx:.1f}" y2="{y + dy:.1f}" stroke="{ACCENT}" stroke-width="3" stroke-linecap="round"/>')
    return "".join(out)


def ball(cx, cy, r, fillc="#fff"):
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fillc}" {SK}/>'


def poly(pts, fillc="#fff"):
    return f'<polygon points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}" fill="{fillc}" {SK}/>'


def line(x1, y1, x2, y2, col="#000"):
    return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{col}" stroke-width="3" stroke-linecap="round"/>'


def boot(bx, by, stripe=True):
    pts = [(0, 0), (26, 0), (26, 38), (54, 44), (62, 58), (62, 74), (0, 74)]
    out = poly([(bx + x, by + y) for x, y in pts])
    if stripe:
        out += f'<rect x="{bx + 2}" y="{by + 2}" width="22" height="10" fill="{ACCENT}"/>'
    return out


def ground(y, dy=8, fillc="#fff"):
    return f'<path d="M14 {y} Q 90 {y - dy} 160 {y} T 306 {y - 2} V 166 H 14 Z" fill="{fillc}" {SK}/>'


def tree(cx, base, k):
    """A snowy pine: two triangles and a trunk, base at y = base, k scales the size (stroke stays 3)."""
    a = [(0, -84), (-24, -48), (24, -48)]
    b = [(0, -62), (-30, -20), (30, -20)]
    f = lambda pts: [(cx + x * k, base + y * k) for x, y in pts]
    return line(cx, base - 20 * k, cx, base) + poly(f(b)) + poly(f(a))


def sled(cx, cy, rot, person=False):
    g = [f'<rect x="-28" y="-12" width="56" height="8" rx="3" fill="{ACCENT}" {SK}/>',
         f'<path d="M-34 -5 Q-34 3 -27 3 L30 3" fill="none" {SK}/>', line(-18, -4, -18, 3), line(18, -4, 18, 3)]
    if person:
        g += [ball(-2, -33, 8), line(-2, -25, 5, -12), line(-1, -21, 16, -17)]
    return f'<g transform="translate({cx},{cy}) rotate({rot})">{"".join(g)}</g>'


def snowman(hat=True, scarf=True):
    out = [ball(160, 136, 28), ball(160, 92, 22), ball(160, 52, 15)]
    out += [line(138, 90, 106, 72), line(182, 90, 214, 72), f'<circle cx="154" cy="49" r="2.5" fill="#000"/>', f'<circle cx="166" cy="49" r="2.5" fill="#000"/>',
            f'<circle cx="160" cy="55" r="2.5" fill="#000"/>', f'<circle cx="160" cy="88" r="2.5" fill="#000"/>', f'<circle cx="160" cy="100" r="2.5" fill="#000"/>']
    if scarf:
        out.append(f'<rect x="138" y="64" width="44" height="9" rx="4" fill="{ACCENT}" {SK}/>')
    if hat:
        out += [f'<rect x="147" y="16" width="26" height="22" fill="#fff" {SK}/>', line(140, 38, 180, 38)]
    return "".join(out)


def frame_art(k):
    """The art of one storyboard frame in a 320 x 180 box. All ink stays inside x 14-306 and y 14-166 (--check proves it from the render)."""
    hill = f'<path d="M14 56 L306 146 V166 H14 Z" fill="#fff" {SK}/>'
    if k == "a1":
        return (f'<rect x="95" y="26" width="130" height="100" rx="4" fill="{ACC_LIGHT}" {SK}/>' + line(160, 26, 160, 126) + line(95, 76, 225, 76)
                + flake(127, 51, 12) + flake(192, 51, 12) + flake(127, 101, 12) + flake(192, 101, 12)
                + f'<rect x="80" y="126" width="160" height="14" rx="3" fill="#fff" {SK}/>')
    if k == "a2":
        return (f'<rect x="50" y="128" width="220" height="18" rx="4" fill="{ACC_LIGHT}" {SK}/>' + boot(80, 52) + boot(176, 52))
    if k == "a3":
        return (f'<rect x="110" y="32" width="100" height="114" fill="{ACC_LIGHT}" {SK}/>' + poly([(110, 32), (80, 44), (80, 134), (110, 146)])
                + '<circle cx="90" cy="92" r="4" fill="#000"/>' + flake(160, 70, 11) + flake(186, 112, 11) + line(40, 148, 280, 148))
    if k == "a4":
        return (boot(150, 46) + ground(110, 12) + f'<ellipse cx="70" cy="138" rx="22" ry="9" fill="{ACC_LIGHT}" {SK}/>'
                + f'<ellipse cx="250" cy="140" rx="22" ry="9" fill="{ACC_LIGHT}" {SK}/>' + flake(60, 50, 10) + flake(262, 60, 10) + flake(100, 84, 10))
    if k == "a5":
        return (ball(160, 52, 16) + line(160, 68, 160, 116) + line(160, 82, 116, 60) + line(160, 82, 204, 60) + line(160, 116, 138, 152) + line(160, 116, 182, 152)
                + line(60, 154, 260, 154) + flake(62, 50, 11) + flake(260, 46, 11) + flake(72, 120, 11) + flake(252, 112, 11) + flake(110, 28, 11))
    if k == "b1":
        return hill + tree(262, 133, 1.0) + sled(70, 69, 17.1, False) + flake(40, 30, 10) + flake(130, 34, 10) + flake(200, 56, 10)
    if k == "b2":
        return (hill + tree(262, 133, 1.0) + sled(140, 91, 17.1, True) + line(70, 44, 112, 44, ACCENT) + line(60, 56, 104, 56, ACCENT) + line(66, 68, 98, 68, ACCENT))
    if k == "b3":
        return (line(24, 140, 296, 140) + tree(70, 138, 1.0) + tree(160, 130, 0.8) + tree(250, 138, 1.1) + line(24, 40, 84, 40, ACCENT)
                + line(214, 30, 284, 30, ACCENT) + line(24, 62, 48, 62, ACCENT))
    if k == "b4":
        return (f'<path d="M14 120 L100 120 Q150 70 200 120 L306 120 V166 H14 Z" fill="#fff" {SK}/>'
                + f'<path d="M150 92 Q190 24 236 74" fill="none" stroke="{ACCENT}" stroke-width="3" stroke-dasharray="3 9" stroke-linecap="round"/>'
                + sled(232, 76, -12, True))
    if k == "b5":
        return (f'<path d="M40 152 Q60 78 160 74 Q260 78 280 152 Z" fill="#fff" {SK}/>' + sled(78, 130, -10, False)
                + flake(60, 40, 10) + flake(112, 32, 10) + flake(206, 38, 10) + flake(252, 52, 10) + flake(290, 100, 10))
    if k == "c1":
        return (ground(120, 8) + ball(170, 114, 13) + flake(70, 46, 10) + flake(140, 60, 10) + flake(232, 40, 10) + flake(270, 80, 10) + flake(98, 90, 10))
    if k == "c2":
        return (f'<rect x="26" y="118" width="130" height="18" fill="{ACC_LIGHT}"/>' + ground(122, 4) + ball(190, 104, 30) + flake(60, 50, 10) + flake(250, 52, 10))
    if k == "c3":
        return ball(160, 126, 38) + ball(160, 66, 28) + line(40, 164, 280, 164) + flake(60, 60, 11) + flake(260, 70, 11) + flake(72, 122, 11)
    if k == "c4":
        return (snowman(hat=False, scarf=True) + f'<g transform="rotate(24 224 40)"><rect x="211" y="24" width="26" height="22" fill="#fff" {SK}/>'
                + line(204, 46, 244, 46) + '</g>' + f'<path d="M210 66 Q190 60 176 54" fill="none" stroke="{ACCENT}" stroke-width="3" stroke-dasharray="3 8" stroke-linecap="round"/>')
    if k == "c5":
        return snowman() + flake(62, 40, 10) + flake(86, 104, 10) + flake(256, 48, 10) + flake(268, 112, 10) + flake(70, 150, 10) + flake(250, 150, 10)
    raise KeyError(k)


FRAME_KEYS = [k for b in BOARDS for k in b["art"]]


def frame_body(k):
    """One storyboard frame: a rounded border 4 units inside the 320 x 180 box (stroke 3), then the art."""
    return (f'<rect x="4" y="4" width="312" height="172" rx="8" fill="#fff" stroke="#000" stroke-width="3"/>' + frame_art(k), 320, 180)


def board_timeline_body(W=1500, name="board timeline"):
    """A blank 0-20 s timeline under a storyboard: the five 4-second frames, then an empty strip for the student's hit-point flags."""
    gx, x1 = 200, W - 30
    pw = x1 - gx
    sx = lambda s: gx + pw * s / SCENE_S
    out = []
    for s in range(0, SCENE_S + 1):
        out.append(f'<line x1="{sx(s):.1f}" y1="50" x2="{sx(s):.1f}" y2="{58 if s % 2 else 64}" stroke="#000" stroke-width="2"/>')
        if s % 2 == 0:
            lbl = f"{s} s" if s in (0, SCENE_S) else str(s)
            out.append(D.t_(sx(s), 38, lbl, 24, 500))
            D.lab(name + " ruler", lbl, 24, 60)
    y0 = 74
    out.append(D.t_(gx - 16, y0 + 36, "FRAMES", 24, 700, anchor="end"))
    D.lab(name + " lane", "FRAMES", 24, gx - 30)
    for i in range(5):
        a, b = frame_span(i)
        out.append(f'<rect x="{sx(a) + 3:.1f}" y="{y0}" width="{sx(b) - sx(a) - 6:.1f}" height="54" rx="8" fill="{ACC_LIGHT}" stroke="#000" stroke-width="2.5"/>')
        t = f"Frame {i + 1} · {a}–{b} s"
        out.append(D.t_((sx(a) + sx(b)) / 2, y0 + 35, t, 24, 700))
        D.lab(name + " frames", t, 24, sx(b) - sx(a) - 20)
    y1 = y0 + 54 + 20
    out.append(D.t_(gx - 16, y1 + 56, "HIT POINTS", 24, 700, anchor="end"))
    D.lab(name + " lane", "HIT POINTS", 24, gx - 30)
    out.append(f'<rect x="{gx}" y="{y1}" width="{pw}" height="112" fill="#fff" stroke="#000" stroke-width="2.5"/>')
    for s in range(1, SCENE_S):
        out.append(f'<line x1="{sx(s):.1f}" y1="{y1 + 4}" x2="{sx(s):.1f}" y2="{y1 + 108}" stroke="#bbb" stroke-width="1.5" stroke-dasharray="3 6"/>')
    cap = "Draw a flag at each hit point and write its time in seconds"
    out.append(D.t_(gx + pw / 2, y1 + 112 + 34, cap, 24, 500))
    D.lab(name + " cap", cap, 24, pw)
    return padded("".join(out), W, y1 + 112 + 48, 12)


def arc_body(W=1500, H=470, name="arc"):
    """A blank emotional-arc chart: time 0-20 s across, energy low to high up. The student draws the line."""
    gx, x1 = 170, W - 30
    pw = x1 - gx
    top, bot = 30, H - 70
    out = []
    for i, lbl in enumerate(["HIGH", "MEDIUM", "LOW"]):
        y = top + (bot - top) * i / 2
        out.append(f'<line x1="{gx}" y1="{y:.1f}" x2="{x1}" y2="{y:.1f}" stroke="#bbb" stroke-width="1.5" stroke-dasharray="3 6"/>')
        out.append(D.t_(gx - 16, y + 8, lbl, 24, 700, anchor="end"))
        D.lab(name + " levels", lbl, 24, gx - 30)
    for s in range(0, SCENE_S + 1, 5):
        x = gx + pw * s / SCENE_S
        out.append(f'<line x1="{x:.1f}" y1="{top - 8}" x2="{x:.1f}" y2="{bot + 8}" stroke="#bbb" stroke-width="1.5" stroke-dasharray="3 6"/>')
        lbl = f"{s} s"
        out.append(D.t_(x, bot + 40, lbl, 24, 500))
        D.lab(name + " times", lbl, 24, 90)
    out.append(f'<rect x="{gx}" y="{top - 8}" width="{pw}" height="{bot - top + 16}" fill="none" stroke="#000" stroke-width="2.5"/>')
    cap = "Energy of the scene over time"
    out.append(D.t_(gx + pw / 2, H - 6, cap, 24, 500))
    D.lab(name + " cap", cap, 24, pw)
    return padded("".join(out), W, H, 12)


def calc_body(W=1600, name="calc pic"):
    """The same 20 seconds counted in bars at 96 BPM (8 bars of 2.5 s) and at 120 BPM (10 bars of 2 s), with one hit point at 12.5 s."""
    gx = 250
    pw = W - gx - 30
    sx = lambda s: gx + pw * s / SCENE_S
    hp = 12.5
    out = []
    for s in (0, 5, 10, 15, 20):
        lbl = f"{s} s"
        out.append(D.t_(sx(s), 30, lbl, 24, 500, anchor="start" if s == 0 else ("end" if s == 20 else "middle")))
        D.lab(name + " ruler", lbl, 24, 90)
    rows = [(96, 90, 8), (120, 230, 10)]
    for bpm, y, n in rows:
        lbl = f"{bpm} BPM"
        out.append(D.t_(gx - 20, y + 38, lbl, 34, 700, anchor="end"))
        D.lab(name + " rows", lbl, 34, gx - 40)
        bl = float(bar_len(bpm))
        for i in range(n):
            fillc = ACC_LIGHT if i % 2 == 0 else "#fff"
            out.append(f'<rect x="{sx(i * bl):.1f}" y="{y}" width="{sx((i + 1) * bl) - sx(i * bl):.1f}" height="56" fill="{fillc}" stroke="#000" stroke-width="2.5"/>')
            out.append(D.t_((sx(i * bl) + sx((i + 1) * bl)) / 2, y + 38, str(i + 1), 30, 700))
    for bpm, y, n in rows:
        bp = bar_pos(hp, bpm)
        b, k = bar_beat(hp, bpm)
        t1 = f"bar {dec(bp, 2)} = bar {b}, beat {float(k):g}"
        yy = y + 56 + 36
        out.append(D.t_(sx(hp) + 12, yy, t1, 26, 700, anchor="start", fill_=ACCENT))
        D.lab(name + " flags", t1, 26, W - sx(hp) - 40)
    out.append(f'<line x1="{sx(hp):.1f}" y1="76" x2="{sx(hp):.1f}" y2="324" stroke="{ACCENT}" stroke-width="5" stroke-linecap="round"/>')
    out.append(f'<circle cx="{sx(hp):.1f}" cy="66" r="9" fill="{ACCENT}"/>')
    t = "hit point at 12.5 s"
    out.append(D.t_(sx(hp) - 22, 74, t, 26, 700, anchor="end"))
    D.lab(name + " flag", t, 26, 300)
    cap = "The same 20 seconds, counted in bars: bar number = 1 + 12.5 ÷ (240 ÷ BPM)"
    out.append(D.t_(gx + pw / 2, 372, cap, 26, 500))
    D.lab(name + " cap", cap, 26, pw)
    return padded("".join(out), W, 388, 14)


def layers_body(W=1700, name="layers pic"):
    """Four cards: the four layers of the score."""
    cw, gap, ch = 390, 40, 330
    cards = [("PAD", "A soft background", "color that sets the mood"), ("MOTIF", "A short idea of 3 to 5", "notes that you invent"),
             ("PERCUSSION HITS", "Big short sounds that", "land on the hit points"), ("FOLEY ACCENTS", "Crunches, doors and whooshes", "that match the picture")]
    out = []
    for i, (nm, d1, d2) in enumerate(cards):
        x = i * (cw + gap)
        g = [f'<rect x="0" y="0" width="{cw}" height="{ch}" rx="16" fill="#fff" stroke="#000" stroke-width="3"/>']
        if i == 0:
            g.append(f'<rect x="60" y="56" width="270" height="70" rx="35" fill="{ACC_LIGHT}" stroke="#000" stroke-width="3"/>')
            g.append(f'<path d="M95 91 Q135 62 175 91 T255 91 T300 84" fill="none" stroke="{ACCENT}" stroke-width="5" stroke-linecap="round"/>')
        elif i == 1:
            pts = [(80, 112), (150, 80), (220, 100), (300, 58)]
            g.append(f'<polyline points="{" ".join(f"{a},{b}" for a, b in pts)}" fill="none" stroke="#000" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>')
            g += [f'<circle cx="{a}" cy="{b}" r="13" fill="{ACCENT}" stroke="#000" stroke-width="3"/>' for a, b in pts]
        elif i == 2:
            cx, cy = 195, 92
            g.append(f'<polygon points="{cx},{cy - 38} {cx + 38},{cy} {cx},{cy + 38} {cx - 38},{cy}" fill="{ACCENT}" stroke="#000" stroke-width="3" stroke-linejoin="round"/>')
            for a in range(0, 360, 45):
                r1, r2 = 56, 74
                g.append(f'<line x1="{cx + r1 * math.cos(math.radians(a)):.1f}" y1="{cy + r1 * math.sin(math.radians(a)):.1f}" '
                         f'x2="{cx + r2 * math.cos(math.radians(a)):.1f}" y2="{cy + r2 * math.sin(math.radians(a)):.1f}" stroke="#000" stroke-width="3" stroke-linecap="round"/>')
        else:
            hs = [20, 44, 70, 36, 82, 52, 26, 60, 30]
            for j, h in enumerate(hs):
                xx = 88 + j * 26.5
                g.append(f'<line x1="{xx:.1f}" y1="{92 - h / 2:.1f}" x2="{xx:.1f}" y2="{92 + h / 2:.1f}" stroke="{ACCENT if j % 2 == 0 else "#000"}" stroke-width="8" stroke-linecap="round"/>')
        g.append(D.t_(cw / 2, 206, nm, 36, 700))
        D.lab(name + " names", nm, 36, cw - 30)
        g.append(D.t_(cw / 2, 252, d1, 24, 500))
        g.append(D.t_(cw / 2, 284, d2, 24, 500))
        D.lab(name + " text", d1, 24, cw - 30)
        D.lab(name + " text", d2, 24, cw - 30)
        out.append(f'<g transform="translate({x},0)">{"".join(g)}</g>')
    return padded("".join(out), 4 * cw + 3 * gap, ch, 12)


def map_body(W=1600, name="map", fs=22, ts=20, lf=22, lh=44):
    """The worked example's score map: 20 s at 96 BPM = 8 bars of 2.5 s; mood bands, four hit points and the layers."""
    gx = 250
    pwid = W - gx - 30
    Xt = lambda t: gx + pwid * t / SCENE_S
    Xb = lambda bar: gx + pwid * (bar - 1) / EX_BARS
    out = []
    for i, (nm, a, b) in enumerate(EX_MOODS):
        fillc = ACCENT if nm == "Tension" else (ACC_LIGHT if nm == "Joy" else "#ececec")
        lbl = nm.upper()
        out.append(f'<rect x="{Xt(a) + 2:.1f}" y="2" width="{Xt(b) - Xt(a) - 4:.1f}" height="50" rx="8" fill="{fillc}" stroke="#000" stroke-width="3"/>')
        out.append(D.t_((Xt(a) + Xt(b)) / 2, 36, lbl, fs, 700, fill_="#fff" if nm == "Tension" else "#000"))
        D.lab(name + " moods", lbl, fs, Xt(b) - Xt(a) - 24)
    out.append(D.t_(gx - 14, 36, "MOOD", lf - 2, 700, anchor="end", fill_=ACCENT))
    y0 = 128
    rows = [(nm, sp) for nm, sp, _d in EX_LAYERS] + [("Automation", "auto")]
    lg = 8
    ybot = y0 + len(rows) * (lh + lg) - lg
    for i, (nm, sp) in enumerate(rows):
        yy = y0 + i * (lh + lg)
        lbl = nm.upper()
        out.append(D.t_(gx - 14, yy + lh / 2 + lf * .35, lbl, lf, 700, anchor="end"))
        D.lab(name + " lanes", lbl, lf, gx - 24)
        out.append(f'<rect x="{gx}" y="{yy}" width="{pwid:.1f}" height="{lh}" fill="#fff" stroke="#000" stroke-width="1.5"/>')
    for bar in range(2, EX_BARS + 1):
        out.append(f'<line x1="{Xb(bar):.1f}" y1="{y0}" x2="{Xb(bar):.1f}" y2="{ybot}" stroke="#aaa" stroke-width="1.5"/>')
    for i, (nm, sp) in enumerate(rows):
        yy = y0 + i * (lh + lg)
        cy = yy + lh / 2
        if sp == "auto":
            pts = [(1, .15), (2, .25), (5, .95), (6, .85), (7, .15), (8, .15), (8.7, .9), (9, .9)]
            d = " ".join(f"{Xb(b):.1f},{yy + lh - 8 - v * (lh - 16):.1f}" for b, v in pts)
            out.append(f'<polyline points="{d}" fill="none" stroke="{ACCENT}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>')
        elif sp is None:
            for t in EX_TIMES:
                x = Xt(t)
                if nm == "Percussion hits":
                    out.append(f'<polygon points="{x:.1f},{cy - 16:.1f} {x + 16:.1f},{cy:.1f} {x:.1f},{cy + 16:.1f} {x - 16:.1f},{cy:.1f}" fill="{ACCENT}" stroke="#000" stroke-width="3" stroke-linejoin="round"/>')
                else:
                    out.append(f'<rect x="{x - 12:.1f}" y="{cy - 12:.1f}" width="24" height="24" rx="4" fill="#fff" stroke="#000" stroke-width="3"/>')
        else:
            for a, b in sp:
                out.append(f'<rect x="{Xb(a) + 3:.1f}" y="{yy + 5}" width="{Xb(b + 1) - Xb(a) - 6:.1f}" height="{lh - 10}" rx="8" fill="#c9c9c9" stroke="#000" stroke-width="2.5"/>')
    for n, t in enumerate(EX_TIMES, start=1):
        x = Xt(t)
        pt = y0 + 2 * (lh + lg)                     # the percussion and foley lanes keep their marks clear of the flag line
        fb = y0 + 3 * (lh + lg) + lh
        out.append(f'<line x1="{x:.1f}" y1="92" x2="{x:.1f}" y2="{pt - 3}" stroke="#000" stroke-width="2.5" stroke-dasharray="2 7" stroke-linecap="round"/>')
        out.append(f'<line x1="{x:.1f}" y1="{fb + 3}" x2="{x:.1f}" y2="{ybot + 6}" stroke="#000" stroke-width="2.5" stroke-dasharray="2 7" stroke-linecap="round"/>')
        out.append(f'<circle cx="{x:.1f}" cy="92" r="9" fill="#000"/>')
        lbl = f"HP{n} · {fmt(t)} s"
        out.append(D.t_(x, 80, lbl, lf - 2, 700))
        D.span(name + " flags", 0, lbl, lf - 2, x, lo=gx, hi=gx + pwid + 20)
    ty = ybot + 20
    for i in range(EX_BARS + 1):
        t = i * float(EX_BAR_S)
        lbl = f"{fmt(t)} s"
        anc = "start" if i == 0 else ("end" if i == EX_BARS else "middle")
        xx = Xb(i + 1)
        out.append(f'<line x1="{xx:.1f}" y1="{ty - 8}" x2="{xx:.1f}" y2="{ty + 4}" stroke="#000" stroke-width="2"/>')
        out.append(D.t_(xx + (3 if i == 0 else (-3 if i == EX_BARS else 0)), ty + 4 + ts, lbl, ts, 500, anchor=anc))
        D.lab(name + " ticks", lbl, ts, 100)
        if i < EX_BARS:
            bl = f"bar {i + 1}"
            out.append(D.t_((Xb(i + 1) + Xb(i + 2)) / 2, ty + 4 + ts * 2 + 8, bl, ts - 2, 500, fill_="#555"))
            D.lab(name + " bars", bl, ts - 2, pwid / EX_BARS - 16)
    cap = f"{SCENE_S} seconds at {EX_BPM} BPM in 4/4: {EX_BARS} bars × {fmt(EX_BAR_S)} seconds = {SCENE_S} seconds"
    out.append(D.t_(gx + pwid / 2, ty + 4 + ts * 2 + 48, cap, ts + 4, 500))
    D.lab(name + " cap", cap, ts + 4, pwid)
    return padded("".join(out), W, ty + 4 + ts * 2 + 64, 14)


def storyboard_strip_body(bk="board1", name="board strip"):
    """Deck picture: the five frames of a storyboard in a row, with their seconds and captions."""
    b = board(bk)
    fw, gap = 320, 26
    out = []
    for i in range(5):
        x = i * (fw + gap)
        a, e = frame_span(i)
        fb, _, _ = frame_body(b["art"][i])
        out.append(f'<g transform="translate({x},0)">{fb}</g>')
        t = f"{a}–{e} s"
        out.append(D.t_(x + fw / 2, 180 + 40, t, 34, 700))
        cap = b["frames"][i]
        words = cap.split()
        lines_, cur = [], ""
        for w in words:
            if D.text_w(cur + " " + w, 22, "oswald") > fw - 10 and cur:
                lines_.append(cur)
                cur = w
            else:
                cur = (cur + " " + w).strip()
        lines_.append(cur)
        for j, ln in enumerate(lines_):
            out.append(D.t_(x + fw / 2, 180 + 76 + j * 28, ln, 22, 500))
            D.lab(name + " captions", ln, 22, fw - 10)
    return padded("".join(out), 5 * fw + 4 * gap, 180 + 76 + 28, 12)


def hero_body():
    """The owner's pre-made art (art/hero.png, used whole). The viewBox only trims fully transparent margin: the art's own pixels
    (x 73-1323, y 79-1373 of 1400) stay at least 40 units inside it, which --check proves from the file."""
    return (f'<image href="../art/hero.png" x="{-HX}" y="{-HY}" width="1400" height="1400"/>', HW, HH)


HX, HY, HW, HH = 30, 35, 1340, 1380

DRAWINGS = {"hero": hero_body, "board": lambda: storyboard_strip_body("board1", "board deck"), "calc": lambda: calc_body(1600, "calc deck"),
            "layers": lambda: layers_body(1700, "layers deck"), "map": lambda: map_body(1600, "map deck")}
DRAWING_PX = {"hero": 1340, "board": 2000, "calc": 2000, "layers": 2000, "map": 2000}
SIDE = {"board": ["Five frames of 4 seconds make 20", "Name the mood of the scene", "Find the moments that matter", "Each one is a hit point"],
        "calc": ["Seconds per beat = 60 ÷ BPM", "Seconds per bar = 240 ÷ BPM", "Bar number = 1 + t ÷ seconds per bar", "At 96 BPM, 20 seconds is 8 bars"],
        "layers": ["Four layers make a score", "Each one has its own job", "The motif is yours alone", "Percussion lands on hit points"],
        "map": ["An invented 20-second scene", "Four hit points on four markers", "Mood changes at the hit points", "Every bar lasts 2.5 seconds"]}
# extra drawings used on pages only, rendered alone on a transparent ground by --check as well
PAGE_DRAWINGS = {"timeline": lambda: board_timeline_body(1500, "board timeline"), "arc": lambda: arc_body(1500, 470, "arc page"),
                 "map-page": lambda: map_body(1500, "map page", 24, 22, 24, 46), "layers-page": lambda: layers_body(1700, "layers page"),
                 **{f"frame-{k}": (lambda k=k: padded(*frame_body(k), 10)) for k in FRAME_KEYS}}


def label_extras():
    board_timeline_body(1500, "board timeline")
    arc_body(1500, 470, "arc page")
    map_body(1500, "map page", 24, 22, 24, 46)
    storyboard_strip_body("board1")
    for b in BOARDS:
        storyboard_strip_body(b["key"], "board strip " + b["key"])


# ================================================================ intro deck: (class, kind, title, body, speaker notes)
SLIDES = [
    (1, "title", "Snow Day Film Score", "Score a 20-second scene. Land the hits.",
     "Class 1, the first minute. No audio is included in this deck. Open with the idea: you will score a 20-second winter scene, the way a film composer "
     "does. You will film it on a phone or use a storyboard, name its mood, mark its hit points, choose a tempo so the hits land on beats, and build the score "
     "in Logic Pro from four layers. Nobody needs to play an instrument or read music, and no melody is given."),
    (1, "listen", "Silence or sound?", "Think, then share|Teacher: read this aloud, no audio plays. A street is covered in snow and the morning is very quiet.|Which mood did you picture?|"
     "What would one big sound feel like here?|Where in the scene would you put it?",
     "Read the scene aloud slowly and ask the three questions. Take a few answers. Nothing is played from a speaker. Students will say peaceful, lonely, cozy or "
     "magical for the mood, and many will want a sound when something moves. Write their words on the board. The project turns that gut feeling into a plan: the mood "
     "becomes the sound of the score, and the moment of the big sound becomes a hit point with a time."),
    (1, "bullets", "What is Snow Day Film Score?", "Score a 20-second winter scene|Film it, or use a storyboard|Spot the hit points; pick a tempo|Four layers in Logic Pro",
     "The project in four lines. Every student scores one 20-second winter scene, filmed on a phone or taken from one of the three storyboards. They name the mood, spot "
     "the hit points, and choose a tempo so the hit points land on beats or bars. Then they build the score from a pad, a motif, percussion hits and foley accents. "
     "There is no melody to learn and no audio ships: students make every sound."),
    (1, "days", "Three classes", "",
     "The shape of the project. Class 1: hook, the scene, its mood and the spotting sheet. Class 2: turn times into bars, pick a tempo, set up Logic and start the layers. "
     "Class 3: finish the layers, mix, bounce, present and reflect. With two classes, merge Classes 2 and 3 and keep the presentations short; with four, add a day for "
     "the percussion hits, the foley and the mix. Hand out the storyboards and the spotting sheet now."),
    (1, "pic", "A scene, a mood, an arc", "board",
     f"Class 1. This is the first storyboard, a snow-day morning: five frames of 4 seconds each make 20 seconds. Ask what the mood of the whole scene is, and how the feeling "
     f"changes from the first frame to the last. That change is the emotional arc. Students who film their own scene do the same with their clip. The three boards are on pages "
     f"{pg('board1')} to {pg('board3')}, and the Mood and arc page is page {pg('mood')}."),
    (1, "steps", "Spot the scene", "Watch it with the sound off|Name the mood in one word|Pause at each key moment|Write its time in seconds|Keep 3 to 6 hit points",
     f"Class 1. Spotting means watching a scene closely to decide where music is needed. Students watch with the sound off, pause at each key moment, and write its time on the "
     f"spotting sheet, page {pg('spot')}. A hit point is a moment where the music or a sound accent must land exactly on the picture: a door opens, a sled leaps. Three to six is "
     f"plenty for 20 seconds, and a quiet moment before a big one makes it feel bigger."),
    (2, "pic", "Seconds to bars", "calc",
     f"Class 2. Pick a tempo and the clock becomes a grid. Seconds per beat is 60 divided by the tempo, and seconds per bar in 4/4 is 240 divided by the tempo. A hit point at time "
     f"t is at bar number 1 plus t divided by the seconds per bar. At 96 BPM a bar lasts 2.5 seconds, so 12.5 seconds is bar 6, beat 1. At 120 BPM a bar lasts 2 seconds, so the "
     f"same moment is bar 7.25, which is bar 7, beat 2. The calculator tables are on page {pg('calc')}."),
    (2, "pic", "Four layers", "layers",
     "Class 2. A score is built in layers. The pad is a soft background that sets the mood. The motif is a short idea of 3 to 5 notes that the student invents; this kit gives "
     "no melody. The percussion hits land on the hit points. The foley and sound-design accents are sounds that match the picture, like a crunch of snow. Ask which layer "
     "the class would add first, and which one they could remove without losing the mood."),
    (2, "steps", "Build it in Logic", "Set the tempo; keep 4/4|Open Movie if you filmed it|Add a marker on each hit point|Pad, motif, hits and foley|Automate, mix and bounce",
     f"Class 2. Demonstrate on the projector. Set the tempo from the spotting sheet and keep 4/4. If a student filmed the scene, choose File, then Open Movie, to bring the clip in; "
     f"the wording can differ by version. Put a marker on each hit point, then add the pad, the motif, the percussion hits and the foley, and draw automation for swells. Menu names "
     f"and button places move between Logic versions; the quick reference on page {pg('logicref')} hedges where they do."),
    (3, "pic", "20 seconds, 8 bars", "map",
     f"Class 3. An invented skating scene described on paper; nothing here is audio. At 96 BPM one bar is 240 divided by 96, which is 2.5 seconds, so 20 seconds are exactly 8 bars. "
     f"The four hit points, 2.5, 6.25, 12.5 and 17.5 seconds, land at bar 2 beat 1, bar 3 beat 3, bar 6 beat 1 and bar 8 beat 1. The mood runs calm, joy, tension, relief. "
     f"Students plan their own on the layer plan, page {pg('layers')}; the full example is on pages {pg('example')} and {pg('example2')}."),
    (3, "check", "What you turn in", "Bounced .mp3 or .wav, about 20 seconds|Zipped .logicx project|Named: Your Name – Snow Day Film Score|Mood and arc, spotting sheet, layer plan|"
     "Reflection page|Rubric self-score and three questions",
     "Class 3. The submission checklist, shortened to fit the slide. Show where students hand in. The file name is Your Name, then Snow Day Film Score. Check the length before "
     "students bounce: the score should run about 20 seconds, which is 8 bars at 96 BPM or 10 bars at 120 BPM."),
    (3, "rubric", "How it’s scored", "",
     "The rubric: five categories, each scored 1 to 5, for a total out of 25. Students score themselves first; the final grade is the average of their score and yours. "
     "The slide reads the 5 column of each category aloud. Hand out the rubric page so students can self-score before they present."),
    (3, "bullets", "Presentation day", "Play the scene with your score|Point out each hit point as it lands|Your three questions for classmates|Answer at least 2 of each classmate’s questions",
     "Class 3, presentations. Each student plays the scene with the score, names the mood and points out each hit point as it lands, with its time and bar number. Students write three "
     "questions they want classmates to answer, and answer at least two of each classmate's. Ask the class to say where the hit points are before the presenter does."),
    (3, "closer", "One last thing…", "Watch before you write.|Hit points need space.|Tempo makes them land.|Now press play.",
     "Close with the listening day: show a scene with no sound and ask the class where the hits should go, then play the score. A hit that people expected is a hit that was well "
     "spotted. Ask a few students which layer did the most for the mood. No audio is included in this resource; the sounds are the students' own."),
]
SHOTS1 = [("pacing", "Pacing guide", "3 class periods, slide by slide"), ("board1", "Storyboards", "Three ready-made scenes"),
          ("calc", "Calculator", "Seconds to bars and beats")]
SHOTS2 = [1, 5, 7, 8, 10, 12]
SHOTS3 = [("board1", "Storyboard 1"), ("mood", "Mood and arc"), ("spot", "Spotting sheet"), ("calc", "Calculator"), ("layers", "Layer plan"),
          ("example", "Worked example"), ("example2", "Worked example 2"), ("rubric", "Rubric")]
PREVIEW_PICKS = ["pacing", "board1", "calc", "rubric"]

COVER_A = "Score a 20-second scene"
COVER_C = "Logic Pro · Hit points · Tempo · Mood"
PDF_COVER = dict(a=26, b=52, c=15, art=5.0)
SQ_COVER = dict(a=38, b=140, c=27, art=420, gap=20)
SQ_B_LINES = ["Snow Day", "Film Score"]
SQ_SUB = "3 class periods · hit points and tempo math · intro slides"
SQ_HEADS = {1: ("Ready to teach Monday", 76, "Pacing, storyboards, calculator tables and the /25 rubric in one PDF", 28),
            2: ("Intro deck included", 76, f"{len(SLIDES)} editable slides (.pptx + PDF) with speaker notes on every slide", 28),
            3: ("Everything inside", 72, "Storyboards, calculator tables, worked example, plans and worksheets", 28)}
SQ_BANDS = {1: "Mood <em>·</em> hit points <em>·</em> tempo <em>·</em> layers",
            2: "Storyboards <em>·</em> hit points <em>·</em> tempo math",
            3: f"{len(PLAN)} pages <em>·</em> US Letter PDF <em>·</em> no audio included"}


# ================================================================ small page helpers
CSS_SG = ("<style>table.sg { border-collapse: collapse; width: 100%; table-layout: fixed; } table.sg td, table.sg th { border: 1pt solid #000; text-align: center; "
          "padding: 0; font-size: 8pt; } table.sg th { background: #000; color: #fff; font-family: Oswald; font-weight: 500; height: 14pt; } "
          "table.sg td.l { text-align: left; padding: 0 4pt; font-weight: 700; width: 1.35in; font-size: 8.6pt; } "
          "table.sg td.g { background: #e4e4e4; } </style>")


def howto_page(n, wm=False):
    parts = [("Teacher pages", "howto", "example2", "How to use, overview, setup, pacing, teacher notes, Logic quick reference, worked example (2 pages)"),
             ("Student pages", "board1", "reflect", "Three storyboards, mood and arc, spotting sheet, hit-point calculator, layer plan, "
              "project sheet (3 pages), rubric, vocabulary, feedback planner, reflection page"),
             ("Intro deck (separate file)", None, None, f"{len(SLIDES)} slides, .pptx + PDF, speaker notes on every slide")]
    trs = "".join(f"<tr><td><b>{a}</b></td><td style='white-space:nowrap'>{('pages ' + str(D.IX(f)) + '–' + str(D.IX(l))) if f else 'deck'}</td>"
                  f"<td>{u}</td></tr>" for a, f, l, u in parts)
    inner = (f'<div class="cols"><div>'
             f'{D.H2("What this is", True)}'
             f'<p style="font-size:12pt;line-height:1.45">A {CLASSES}-class-period film-scoring project for high school music technology. Every '
             f'student scores a 20-second winter scene that they film on a phone or take from one of three ready-made storyboards. They name its mood, mark its hit points on '
             f'a timeline, choose a tempo so the hits land on beats or bars, and build the score in Logic Pro from four layers. Students plan it, build and mix it, present it and '
             f'reflect on it. It is an original Hudson Beat project.</p>'
             f'{D.H2("Quick start")}<ol>'
             f'<li style="margin-bottom:5pt">Read the pacing guide (page {D.IX("pacing")}) and the teacher notes (pages {D.IX("tn1")}–{D.IX("tn2")}).</li>'
             f'<li style="margin-bottom:5pt">Look at the storyboards, the spotting sheet and the calculator (pages {D.IX("board1")}–{D.IX("calc")}) and the setup (page {D.IX("setup")}).</li>'
             f'<li style="margin-bottom:5pt">Print the student pages (pages {D.IX("board1")}–{D.IX("reflect")}), one set per student.</li>'
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
             f'<li><b>Pace:</b> Class 1 is the scene, the mood and the spotting, Class 2 the tempo and the layers, Class 3 the mix and the presentations (page {D.IX("pacing")}); the pacing page also shows two and four periods.</li>'
             f'<li><b>No phone?</b> Students use one of the three storyboards; every step works without a movie.</li>'
             f'<li><b>Grading:</b> the rubric, /{RUBRIC_TOTAL}, the average of the student’s and your score (page {D.IX("rubric")}).</li></ul>'
             f'<div class="box" style="margin-top:6pt"><span class="k">In one sentence</span><p style="margin:0;font-size:12pt">Students learn that '
             f'a film score is planned: a mood, a few hit points, and a tempo chosen so that the music lands on the picture.</p></div>'
             f'<p class="small" style="margin-top:6pt">Logic Pro is a product of Apple Inc. This resource is not affiliated with Apple.</p>'
             f'</div></div>')
    return D.page("How to use this resource", "START HERE", "Teacher", inner, n, key="howto")


def overview_page(n, wm=False):
    inner = (f'<div class="cols"><div>'
             f'<div class="box inv" style="margin-bottom:6pt"><span class="k">The project in one line</span><p style="margin:0;font-size:12pt">'
             f'<b>{TITLE}</b> · Film scoring · Logic Pro<br>Spot the hit points, pick the tempo, score the scene.</p></div>'
             f'{D.H2("What students make")}'
             f'<p style="font-size:13pt;line-height:1.5">A score for one 20-second winter scene, filmed by the student or taken from a storyboard. It has a named mood and an emotional arc, '
             f'3 to 6 hit points with their times and bar numbers, and four layers in Logic Pro: a pad, a motif the student invents, percussion hits on the hit points and foley or '
             f'sound-design accents. The tempo is chosen from 80 to 128 BPM so that hit points land on beats or bars. Students hand in a bounced file and the zipped .logicx project, '
             f'plus their plans and a reflection, then play the scene with the score and take questions.</p>'
             f'{D.H2("What this project reinforces")}<p style="font-size:12.2pt;line-height:1.5">{TN_REINFORCES}</p>'
             f'{D.H2("Standards")}<p style="font-size:11.4pt">Supports the National Core Arts Standards for Music (Music Technology, high school): generating '
             f'and developing ideas (MU:Cr1.1, MU:Cr2.1), presenting work (MU:Pr6.1) and responding to it (MU:Re7.2).</p>'
             f'</div><div>'
             f'{D.H2("Goals", True)}<ul>' + "".join(f"<li style='font-size:12.4pt;line-height:1.5'>{g}</li>" for g in GOALS) + '</ul>'
             f'{D.H2("At a glance")}<table class="t" style="font-size:11.2pt">'
             f'<tr><td><b>Grades</b></td><td>{GRADES_TEXT}, music technology or music production</td></tr>'
             f'<tr><td><b>Length</b></td><td>{CLASSES} class periods (the pacing page also shows two and four): scene and spotting, tempo and layers, mix and presentations</td></tr>'
             f'<tr><td><b>Software</b></td><td>Logic Pro: Movie track, markers, Alchemy or Retro Synth, Quick Sampler, Drum Machine Designer, automation, bounce</td></tr>'
             f'<tr><td><b>You supply</b></td><td>Macs with Logic Pro, headphones, a place to hand in files and, for students who film, a phone</td></tr>'
             f'<tr><td><b>Assessment</b></td><td>Rubric, 5 categories scored 1–5, /{RUBRIC_TOTAL}; final grade = average of the student’s and the '
             f'teacher’s score (page {D.IX("rubric")})</td></tr></table>'
             f'<div class="box" style="margin-top:6pt"><span class="k">Before they start</span><p style="margin:0;font-size:11.4pt">Students should know how '
             f'to open a project, add a software instrument and use the mixer in Logic. Nobody needs to read music: the project works with sounds, timing and a few '
             f'simple formulas.</p></div>'
             f'</div></div>')
    return D.page("Project overview", "OVERVIEW", "Film scoring project", inner, n, key="overview")


def setup_page(n, wm=False):
    inner = (f'<style>.sb p, .sb li {{ font-size: 11.6pt; line-height: 1.44; margin-bottom: 5pt; }}</style><div class="cols"><div class="big sb">'
             f'{D.H2("You need", True)}<ul>'
             f'<li><b>A Mac with Logic Pro</b> for each student, and <b>headphones</b>.</li>'
             f'<li><b>A place to hand in</b> the .mp3 or .wav files, the zipped .logicx and the reflection.</li>'
             f'<li><b>The storyboards and the calculator tables</b>, printed (pages {D.IX("board1")}–{D.IX("calc")}), or shown on the projector.</li>'
             f'<li><b>Scenes:</b> a phone clip of 20 seconds for each student who films, or a storyboard for everyone else. Common formats such as .mov and .mp4 usually import; '
             f'if one does not, convert it in a video app first.</li>'
             f'<li><b>Printed student pages</b>, one set each (pages {D.IX("board1")}–{D.IX("reflect")}).</li>'
             f'<li><b>A MIDI keyboard</b> is optional: every note can be clicked in with the mouse.</li></ul>'
             f'{D.H2("Before Class 1")}'
             + "".join(D.chk(c, 13, "font-size:11.6pt;margin-bottom:7pt") for c in [
                 f"Read the calculator page (page {D.IX('calc')}) so you can answer ‘which beat is that?’ for any time.",
                 "Open Logic Pro on a student computer and try File › Open Movie… with a phone clip. Note what your version calls it and where the Movie track appears.",
                 f"Check that you can add a marker and set the tempo (see page {D.IX('logicref')}).",
                 f"Read the worked example (pages {D.IX('example')}–{D.IX('example2')})."]) +
             f'</div><div class="big sb">'
             f'{D.H2("What to watch", True)}'
             f'<p style="font-size:11.4pt">Watch for hit points that are not real moments, arithmetic slips, a movie that does not start at the beginning of the project, or a score so busy it '
             f'covers the picture. {TN_NOTE}</p>'
             f'<div class="box acc-b" style="margin-top:2pt"><span class="k">Ideas for the room</span><ul style="margin:0">'
             f'<li style="font-size:11.2pt">Ask while students work: what is the mood right now? Which beat does this hit point land on? What does the pad do here?</li>'
             f'<li style="font-size:11.2pt">On Class 1, play a scene with the sound off on the projector and let the class call out the moments that need a sound.</li>'
             f'<li style="font-size:11.2pt">A student who is stuck can start with the percussion hits only: one hit on every marker already sounds like a score.</li></ul></div>'
             f'{D.H2("Filming rules")}'
             f'<div class="box"><span class="k">Share these with students</span><p style="margin:0;font-size:11pt;line-height:1.4">'
             f'Film an original scene with no music, no copyrighted characters and no logos in it. Ask permission before you film anyone, and follow your school’s rules about '
             f'filming people. Scenes with no faces in them, such as boots, snow, hands or a sled, work well.</p></div>'
             f'<div class="box" style="margin-top:6pt"><span class="k">Keep the volume moderate</span><p style="margin:0;font-size:11pt;line-height:1.4">'
             f'Bright, high sounds and big hits can be tiring in headphones. Tell students to start low and check the final mix at a normal level.</p></div>'
             f'</div></div>')
    return D.page("Setup and what to watch", "SETUP", "Teacher", inner, n, key="setup")


# ================================================================ the storyboard pages
def board_page_fn(k):
    def fn(n, wm=False):
        b = board(k)
        cells = []
        for i in range(5):
            a, e = frame_span(i)
            cells.append(f'<div><div>{D.body_svg(frame_body(b["art"][i]))}</div>'
                         f'<p style="margin:2pt 0 0;font-size:9.6pt;line-height:1.2"><b>Frame {i + 1} · {a}–{e} s</b><br>{b["frames"][i]}</p>'
                         f'<div class="fl" style="margin:3pt 0 0;font-size:9pt"><b>Sound idea:</b><span style="height:12pt"></span></div></div>')
        cells.append('<div class="box acc-b" style="padding:5pt 8pt"><span class="k">My first impressions</span>'
                     '<div class="fl" style="margin:3pt 0 0;font-size:9.4pt"><b>Mood:</b><span></span></div>'
                     '<div class="fl" style="margin:3pt 0 0;font-size:9.4pt"><b>Starts:</b><span></span></div>'
                     '<div class="fl" style="margin:3pt 0 0;font-size:9.4pt"><b>Ends:</b><span></span></div>'
                     '<div class="fl" style="margin:3pt 0 0;font-size:9.4pt"><b>Biggest moment:</b><span></span></div></div>')
        grid = f'<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:7pt 10pt">{"".join(cells)}</div>'
        inner = (f'<p style="margin:0 0 5pt;font-size:10.4pt;line-height:1.38">Step 1: choose the scene. Use this board if you do not film your own. It lasts 20 seconds: five frames of '
                 f'{FRAME_S} seconds each. The scene: {b["sub"].lower().replace("a child", "a child")}. Look at each frame and imagine its sound, then name the mood. Mark the moments you would hit on the timeline below; '
                 f'you will list their times on the spotting sheet (page {pg("spot")}).</p>'
                 + grid +
                 f'<span class="k" style="margin-top:6pt">Timeline: mark my hit points</span>'
                 f'<div style="margin-top:2pt">{D.body_svg(board_timeline_body(1500, "board timeline"))}</div>'
                 f'<span class="k" style="margin-top:6pt">My hit points: time in seconds and what happens</span>'
                 + "".join('<div class="fl" style="margin:2pt 0 3pt"><b>HP</b><span style="flex:0 0 0.4in"></span><b>t =</b><span style="flex:0 0 0.9in"></span><b>s</b>'
                           '<span></span></div>' for _ in range(4)))
        return D.page(f"Storyboard {b['num']}: {b['name']}", "STUDENT", "Class 1", inner, n, wm, name=True, key=k)
    return fn


# ================================================================ mood and arc
MOODS = {"Low energy": ["calm", "cozy", "quiet", "sleepy", "lonely", "peaceful"],
         "Medium energy": ["curious", "hopeful", "wistful", "warm", "dreamy", "thoughtful"],
         "High energy": ["joyful", "playful", "excited", "tense", "nervous", "triumphant"]}
FEEL_ROWS = [("Calm, cozy", "Slow, about 80 BPM, or no strong pulse", "A soft pad with a slow attack; a few notes with space between them", "Very quiet hits; soft snow sounds"),
             ("Wonder, dreamy", "Slow to medium", "A pad that swells; bright, high notes in the motif", "Light, shimmering sounds; a gentle swell before a hit"),
             ("Playful", "Medium to fast, 100 to 128 BPM", "Short, light notes that skip around", "Small percussion; quick crunches and whooshes"),
             ("Tense, nervous", "A steady, quiet pulse; gaps of silence", "A low held note; a motif that stops before it ends", "A low boom on the big moment; creaks"),
             ("Joy, triumph", "Medium to fast", "Fuller layers; a motif that climbs", "Hits that stand out; a bright swell"),
             ("Relief, peace", "Settle back to slower layers", "The motif returns softly; the pad stays", "One soft hit; a long, quiet tail")]


def mood_page(n, wm=False):
    bank = "".join(f'<div class="box" style="padding:4pt 8pt"><span class="k" style="font-size:9.6pt">{g}</span><p style="margin:0;font-size:10.4pt;line-height:1.35">'
                   + " · ".join(ws) + '</p></div>' for g, ws in MOODS.items())
    rows = "".join(f"<tr><td><b>{a}</b></td><td>{b}</td><td>{c}</td><td>{d}</td></tr>" for a, b, c, d in FEEL_ROWS)
    inner = (f'<p style="margin:0 0 4pt;font-size:10.4pt;line-height:1.36">Step 1: choose the scene, then name its mood. A <b>mood</b> is the feeling of a scene. The <b>emotional arc</b> is how that feeling '
             f'changes from the start of the scene to the end. Pick words from the bank, or use your own, then draw your scene’s arc on the chart.</p>'
             f'<span class="k">Mood word bank</span><div style="display:grid;grid-template-columns:repeat(3,1fr);gap:8pt">{bank}</div>'
             f'<span class="k" style="margin-top:6pt">From feeling to sound (suggestions, not rules)</span>'
             f'<table class="t" style="font-size:9pt;line-height:1.2"><tr><th style="width:15%">Feeling</th><th style="width:22%">Tempo and pulse</th><th style="width:34%">Pad and motif</th><th>Percussion and foley</th></tr>{rows}</table>'
             f'<span class="k" style="margin-top:4pt">My emotional arc: draw a line for the energy of the scene</span>'
             f'<div style="margin-top:2pt">{D.body_svg(arc_body(1500, 470, "arc page"))}</div>'
             f'<div class="cols" style="gap:12pt;margin-top:2pt"><div><div class="fl" style="margin:2pt 0"><b>My scene:</b><span></span></div>'
             f'<div class="fl" style="margin:0 0 2pt"><b>Mood at the start:</b><span></span></div><div class="fl" style="margin:0"><b>Mood at the end:</b><span></span></div></div>'
             f'<div><div class="fl" style="margin:2pt 0"><b>Turning point (seconds):</b><span></span></div>'
             f'<div class="fl" style="margin:0 0 2pt"><b>What makes the mood change:</b><span></span></div><div class="fl" style="margin:0"><b>Pad or motif idea:</b><span></span></div></div></div>')
    return D.page("Mood and arc", "STUDENT", "Class 1", inner, n, wm, name=True, key="mood")


# ================================================================ spotting sheet and calculator
def spot_page(n, wm=False):
    rows = "".join("<tr>" + f"<td style='height:30pt;text-align:center'><b>{i}</b></td>" + "<td></td>" * 6 + "</tr>" for i in range(1, 7))
    inner = (f'<p style="margin:0 0 4pt;font-size:10.2pt;line-height:1.36">Step 2: spot it. Watch the scene with the sound off. Pause at each key moment and write its time in seconds, what happens, '
             f'and how big it is: S (small), M (medium) or BIG. Keep 3 to 6 hit points. Step 3: pick a tempo. Fill in the tempo box below, then for every hit point work out its bar number and its '
             f'bar · beat with the tables on page {pg("calc")}.</p>'
             f'<table class="map" style="margin-bottom:4pt"><tr><th style="width:5%">HP</th><th style="width:10%">Seconds (t)</th><th style="width:26%">The moment (what happens)</th>'
             f'<th style="width:8%">Size</th><th style="width:21%">What it needs (sound idea)</th><th style="width:16%">Bar number = 1 + t ÷ one bar</th><th>Bar · beat</th></tr>{rows}</table>'
             f'<div class="cols" style="gap:10pt"><div class="box acc-b" style="padding:5pt 9pt"><span class="k">My tempo</span>'
             f'<div class="fl" style="margin:3pt 0 3pt;font-size:10pt"><b>Tempo (BPM, 80 to 128):</b><span></span></div>'
             f'<div class="fl" style="margin:0 0 3pt;font-size:10pt"><b>One beat = 60 ÷ BPM =</b><span></span><b>s</b></div>'
             f'<div class="fl" style="margin:0 0 3pt;font-size:10pt"><b>One bar = 240 ÷ BPM =</b><span></span><b>s</b></div>'
             f'<div class="fl" style="margin:0;font-size:10pt"><b>Bars in my scene = 20 ÷ one bar =</b><span></span></div></div>'
             f'<div class="box" style="padding:5pt 9pt"><span class="k">Does it land?</span><p style="margin:0;font-size:9.6pt;line-height:1.34">A hit point lands exactly on a beat when '
             f't × BPM ÷ 60 is a whole number. If none of yours do, look at another tempo in the tables, or move a hit point a little. Rounding: bar numbers to 2 decimals; '
             f'for a marker, round to the nearest sixteenth note (a quarter of a beat).</p></div></div>'
             f'<span class="k" style="margin-top:6pt">Check one hit point by hand</span>'
             f'<div class="fl" style="margin:2pt 0 4pt"><b>HP</b><span style="flex:0 0 0.5in"></span><b>t =</b><span style="flex:0 0 0.7in"></span><b>seconds per bar =</b>'
             f'<span style="flex:0 0 0.8in"></span><b>bar number = 1 + t ÷</b><span style="flex:0 0 0.8in"></span><b>=</b><span></span></div>'
             f'<span class="k" style="margin-top:4pt">Spotting notes</span>' + D.lines(6, 22))
    return D.page("Spotting sheet", "STUDENT", "Classes 1–2", inner, n, wm, name=True, key="spot")


def calc_tempo_rows():
    rows = []
    for bpm in TEMPOS:
        beats20 = Fx(SCENE_S) * bpm / 60
        bars20 = Fx(SCENE_S) / bar_len(bpm)
        whole = bars20.denominator == 1
        b = "<b>" if whole else ""
        e = "</b>" if whole else ""
        rows.append(f"<tr><td>{b}{bpm}{e}</td><td>{dec(spb(bpm), 3)}</td><td>{dec(bar_len(bpm), 3)}</td><td>{dec(beats20, 2)}</td><td>{b}{dec(bars20, 2)}{e}</td></tr>")
    return "".join(rows)


def calc_cells(t, bpm):
    bp = dec(bar_pos(t, bpm), 2)
    bb = bb_text(t, bpm)
    if on_beat(t, bpm):
        return f"<td><b>{bp}</b><br><b>{bb}</b></td>"
    return f"<td>{bp}<br>{bb}</td>"


def calc_page(n, wm=False):
    head = "<tr><th>Seconds (t)</th>" + "".join(f"<th>{b} BPM</th>" for b in TEMPOS) + "</tr>"
    body = "".join(f"<tr><td><b>{fmt(t)}</b></td>" + "".join(calc_cells(t, b) for b in TEMPOS) + "</tr>" for t in CALC_TIMES)
    inner = (f'<style>table.cc td {{ text-align: center; padding: 1pt 3pt; font-size: 8.4pt; line-height: 1.12; }} table.cc th {{ text-align: center; }}</style>'
             f'<p style="margin:0 0 4pt;font-size:10.2pt;line-height:1.36">Step 3: pick a tempo. In 4/4 there are 4 beats in a bar. These formulas turn a time in seconds into a bar and a beat. '
             f'Every number below is computed, so you can check your own arithmetic against it.</p>'
             f'<div class="cols" style="gap:10pt;align-items:flex-start"><div class="box acc-b" style="padding:5pt 9pt;flex:1.1"><span class="k">The formulas (4/4)</span>'
             f'<p style="margin:0 0 2pt;font-size:9.8pt"><b>Seconds per beat</b> = 60 ÷ BPM</p><p style="margin:0 0 2pt;font-size:9.8pt"><b>Seconds per bar</b> = 240 ÷ BPM</p>'
             f'<p style="margin:0 0 2pt;font-size:9.8pt"><b>Bar number</b> = 1 + t ÷ (240 ÷ BPM)</p><p style="margin:0 0 2pt;font-size:9.8pt"><b>Beats from the start</b> = t × BPM ÷ 60</p>'
             f'<p style="margin:0;font-size:9.8pt"><b>Example:</b> t = 12.5 s at 96 BPM: 1 + 12.5 ÷ 2.5 = 6.00, so bar 6, beat 1.</p></div>'
             f'<div class="box" style="padding:5pt 9pt;flex:1"><span class="k">Rounding rules</span><p style="margin:0;font-size:9.2pt;line-height:1.32">Seconds to 3 decimals, bar numbers to 2, a 5 rounds up. '
             f'For a marker, round to the nearest sixteenth note: sixteenths = t × BPM ÷ 60 × 4, rounded to a whole number. Then bar = sixteenths ÷ 16 (whole part) + 1, and '
             f'beat = 1 + (sixteenths left over after the bars) ÷ 4. A bar number of 6.25 is bar 6 and a quarter, which is beat 2.</p></div></div>'
             f'<span class="k" style="margin-top:5pt">Seconds, beats and bars in a 20-second scene</span>'
             f'<table class="t cc" style="margin-top:1pt"><tr><th>BPM</th><th>Seconds per beat</th><th>Seconds per bar</th><th>Beats in 20 s</th><th>Bars in 20 s</th></tr>{calc_tempo_rows()}</table>'
             f'<p class="small" style="margin:0 0 2pt;font-size:8.6pt">Bold = the scene is a whole number of bars: 8 bars at 96 BPM, 10 bars at 120 BPM.</p>'
             f'<span class="k" style="margin-top:3pt">Hit-point calculator: bar number, then bar · beat</span>'
             f'<table class="t cc" style="margin-top:1pt">{head}{body}</table>'
             f'<p class="small" style="margin:0;font-size:8.4pt;line-height:1.2">Each cell: bar number (top), then bar · beat rounded to the nearest sixteenth (bottom). '
             f'<b>Bold</b> = lands exactly on a beat. Beat 1.5 is half a beat after beat 1.</p>')
    return D.page("Hit-point calculator", "STUDENT", "Class 2", inner, n, wm, name=True, key="calc")


# ================================================================ layer plan
PLAN_ROWS = [("Pad", "Alchemy or Retro Synth: a soft pad with a slow attack"), ("Motif", "A Software Instrument you choose; 3 to 5 notes of your own"),
             ("Percussion hits", "Drum Machine Designer or Quick Sampler"), ("Foley accents", "Quick Sampler: sounds you record or import")]
MAX_BARS = 11                                # 20 s at 128 BPM is 10.67 bars


def layers_page(n, wm=False):
    rows = "".join(f"<tr><td style='height:25pt'><b>{a}</b></td><td style='font-size:8.8pt'>{h}</td><td></td><td></td></tr>" for a, h in PLAN_ROWS)
    head = "<tr><th style='width:1.45in'>Bar</th>" + "".join(f"<th>{i + 1}</th>" for i in range(MAX_BARS)) + "</tr>"
    names = ["Hit point number", "Pad", "Motif", "Percussion hits", "Foley accents", "Automation: what moves"]
    body = "".join(f"<tr><td class='l' style='height:25pt'>{nm}</td>" + "".join("<td></td>" for _ in range(MAX_BARS)) + "</tr>" for nm in names)
    inner = (f'{CSS_SG}<p style="margin:0 0 4pt;font-size:10.2pt;line-height:1.36">Step 5: build the layers. A score is built from layers, each with a job. Plan yours here, then play them in '
             f'one at a time. Your scene has {fmt(Fx(SCENE_S))} seconds, so the number of bars depends on your tempo (page {pg("calc")}).</p>'
             f'<div class="box acc-b" style="padding:4pt 9pt;margin-bottom:5pt"><div class="fl" style="margin:0;font-size:10pt"><b>My tempo (BPM):</b><span style="flex:0 0 0.9in"></span>'
             f'<b>My scene is 20 × BPM ÷ 240 =</b><span style="flex:0 0 0.9in"></span><b>bars long</b></div></div>'
             f'<span class="k">My four layers</span>'
             f'<table class="map" style="margin-bottom:5pt"><tr><th style="width:15%">Layer</th><th style="width:30%">Instrument or sound source</th><th style="width:25%">The sound I chose</th><th>Its job in my scene</th></tr>{rows}</table>'
             f'<span class="k">When does each layer play? Shade its bars; write each hit point’s number in its bar</span>'
             f'<table class="sg" style="margin-top:2pt">{head}{body}</table>'
             f'<p class="small" style="margin:2pt 0 4pt">Use only the bars your scene has: at 96 BPM that is 8 bars, at 120 BPM 10 bars. Leave the rest blank.</p>'
             f'<div class="box" style="padding:4pt 10pt"><span class="k">Checks before I bounce</span>'
             + "".join(D.chk(c, 11, "font-size:10pt;margin-bottom:2pt") for c in [
                 "All four layers play, and each has its own job.",
                 "Every hit point has a marker, a percussion hit and a foley accent on it (or a reason why not).",
                 "The motif is my own, and it changes as the mood changes.",
                 "A quiet moment comes just before the biggest hit point.",
                 "I drew automation for at least one swell, and the score is about 20 seconds long."]) + '</div>')
    return D.page("Layer plan", "STUDENT", "Classes 2–3", inner, n, wm, name=True, key="layers")


# ================================================================ worked example (2 pages)
def ex_rows():
    out = []
    for i, (t, what, size, sound) in enumerate(EX_HITS, start=1):
        b, k = bar_beat(t, EX_BPM)
        out.append(f"<tr><td><b>{i}</b></td><td>{fmt(t)}</td><td>{what}</td><td>{size}</td><td>1 + {fmt(t)} ÷ {fmt(EX_BAR_S)} = {dec(bar_pos(t, EX_BPM), 2)}</td><td><b>{b} · {float(k):g}</b></td></tr>")
    return "".join(out)


def ex_compare_rows():
    out = []
    for bpm in TEMPOS:
        cells = "".join(f"<td>{bb_text(t, bpm)}<br><span style='font-size:7.8pt'>{lands_text(t, bpm)}</span></td>" for t in EX_TIMES)
        b = "<b>" if bpm == EX_BPM else ""
        e = "</b>" if bpm == EX_BPM else ""
        out.append(f"<tr><td>{b}{bpm}{e}</td><td>{dec(spb(bpm), 3)}</td><td>{dec(bar_len(bpm), 3)}</td>{cells}</tr>")
    return "".join(out)


def example_page(n, wm=False):
    inner = (f'<style>table.ec td {{ text-align: center; }} table.ec td.l {{ text-align: left; }}</style>'
             f'<p style="margin:0 0 4pt;font-size:10pt">An <b>invented plan on paper</b>: a 20-second ice-skating scene scored at {EX_BPM} BPM. No audio is included. '
             f'Student projects will differ. Page 1 of 2: the plan, the hit points and the tempo choice.</p>'
             f'<div class="cols" style="gap:10pt;align-items:flex-start"><div class="box"><span class="k">1 · A weak plan</span><p style="margin:0;font-size:10.2pt">{EX_WEAK}</p>'
             f'<p style="margin:3pt 0 0;font-size:9.2pt">It names no mood, no hit points, no tempo and no layers.</p></div>'
             f'<div class="box acc-b"><span class="k">2 · A clear plan</span><p style="margin:0;font-size:8.8pt;line-height:1.28">{EX_STRONG}</p></div></div>'
             f'{D.H2("3 · Four hit points, and where they land at 96 BPM")}'
             f'<table class="t ec" style="font-size:9.2pt;line-height:1.2"><tr><th>HP</th><th>Seconds</th><th>The moment</th><th>Size</th><th>Bar number = 1 + t ÷ 2.5</th><th>Bar · beat</th></tr>{ex_rows()}</table>'
             f'<p style="margin:2pt 0 0;font-size:9pt">One beat lasts 60 ÷ {EX_BPM} = {dec(spb(EX_BPM), 3)} s and one bar lasts 240 ÷ {EX_BPM} = {fmt(EX_BAR_S)} s. The scene lasts {SCENE_S} ÷ {fmt(EX_BAR_S)} = {int(Fx(SCENE_S) / EX_BAR_S)} bars, '
             f'so it ends on bar 9, beat 1. Bar 3.50 is bar 3 and a half: the half bar is 2 beats, so beat 3.</p>'
             f'{D.H2("4 · Why 96 BPM? The same hit points at five tempos")}'
             f'<table class="t ec" style="font-size:9pt;line-height:1.18"><tr><th>BPM</th><th>Sec per beat</th><th>Sec per bar</th><th>HP1 (2.5 s)</th><th>HP2 (6.25 s)</th><th>HP3 (12.5 s)</th><th>HP4 (17.5 s)</th></tr>{ex_compare_rows()}</table>'
             f'<p style="margin:3pt 0 0;font-size:9pt;line-height:1.3">Each cell is bar · beat after rounding to the nearest sixteenth, with how it lands. At 96 BPM all four hit points land on a beat, and '
             f'three of them on the first beat of a bar. At 120 BPM all four land on a beat or a half beat, but the scene is 10 bars long. At 80, 100 and 128 BPM none land on a beat. '
             f'The choice is the musician’s: 96 BPM is calm enough for the opening and has the cleanest numbers.</p>')
    return D.page("Worked example · the plan and the hit points", "EXAMPLE", "Teacher", inner, n, wm, ak=True, key="example")


def example2_page(n, wm=False):
    rows = "".join(f"<tr><td><b>HP{i}</b></td><td>{fmt(t)} s</td><td>{snd}</td></tr>" for i, (t, _w, _s, snd) in enumerate(EX_HITS, start=1))
    qs = " ".join(f"{i + 1}. {q}" for i, q in enumerate(EX_QUESTIONS))
    inner = (f'<p style="margin:0 0 3pt;font-size:10pt">The same score, page 2 of 2: the map of the whole scene, then the sounds and the numbers.</p>'
             f'{D.H2("5 · The map: 20 seconds, 8 bars, four layers")}'
             f'<div style="width:7.4in;margin:1pt auto 3pt">{D.body_svg(map_body(1500, "map page", 24, 22, 24, 46))}</div>'
             f'<div class="cols" style="gap:10pt"><div><span class="k" style="font-size:9.4pt">6 · The sound on each hit point</span>'
             f'<table class="t" style="font-size:9.6pt;line-height:1.22;margin-top:2pt"><tr><th>Hit point</th><th>Time</th><th>Percussion hit and foley accent</th></tr>{rows}</table></div>'
             f'<div><span class="k" style="font-size:9.4pt">7 · The layers</span><table class="t" style="font-size:9.6pt;line-height:1.22;margin-top:2pt">'
             + "".join(f"<tr><td style='width:34%'><b>{a}</b></td><td>{c}</td></tr>" for a, _s, c in EX_LAYERS)
             + f"<tr><td><b>Automation</b></td><td>{EX_AUTO}</td></tr></table></div></div>"
             f'<div class="box acc-b" style="margin-top:6pt"><span class="k">8 · Checking the numbers</span><p style="margin:0;font-size:10pt;line-height:1.38">'
             f'One bar of 4/4 at {EX_BPM} BPM lasts 240 ÷ {EX_BPM} = {fmt(EX_BAR_S)} seconds, so {EX_BARS} bars = {EX_BARS} × {fmt(EX_BAR_S)} = {SCENE_S} seconds. '
             f'A hit point at t seconds is at bar 1 + t ÷ {fmt(EX_BAR_S)}: 2.5 s gives bar {dec(bar_pos(2.5, EX_BPM), 2)}, 6.25 s gives bar {dec(bar_pos(6.25, EX_BPM), 2)}, '
             f'12.5 s gives bar {dec(bar_pos(12.5, EX_BPM), 2)} and 17.5 s gives bar {dec(bar_pos(17.5, EX_BPM), 2)}. '
             f'In beats from the start: 2.5 × 96 ÷ 60 = {fmt(beats_from(2.5, EX_BPM))}, 6.25 × 96 ÷ 60 = {fmt(beats_from(6.25, EX_BPM))}, 12.5 × 96 ÷ 60 = {fmt(beats_from(12.5, EX_BPM))} and '
             f'17.5 × 96 ÷ 60 = {fmt(beats_from(17.5, EX_BPM))}; whole numbers, so every hit point lands on a beat. The mood sections last 2.5, 10, 5 and 2.5 seconds, which is 1, 4, 2 and 1 bars.</p></div>'
             f'<div class="box" style="margin-top:5pt"><span class="k">9 · Three feedback questions (invented)</span><p style="margin:0;font-size:10.2pt;line-height:1.38">{qs}</p></div>'
             f'<div class="box acc-b" style="margin-top:5pt"><span class="k">10 · Moments to point out in class</span><ul style="margin:0">'
             f'<li style="font-size:10.2pt;margin-bottom:2pt">The mood changes at hit points 1, 3 and 4 but not at hit point 2: the first spin happens inside the joyful section.</li>'
             f'<li style="font-size:10.2pt;margin-bottom:2pt">The motif stops at hit point 3, so the wobble arrives with only the pad, the low boom and the creak. That thinner sound is the tension.</li>'
             f'<li style="font-size:10.2pt;margin-bottom:0">The pad’s filter closes during the tension, bars 6 and 7, and opens again at hit point 4, so the relief sounds brighter.</li></ul></div>')
    return D.page("Worked example · the map and the numbers", "EXAMPLE", "Teacher", inner, n, wm, ak=True, key="example2")


PAGES = {"howto": howto_page, "overview": overview_page, "setup": setup_page, "example": example_page, "example2": example2_page,
         "board1": board_page_fn("board1"), "board2": board_page_fn("board2"), "board3": board_page_fn("board3"), "mood": mood_page, "spot": spot_page,
         "calc": calc_page, "layers": layers_page}


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


def frame_art_errors():
    """Each storyboard frame's art, rendered alone on a transparent ground at 1400 px for the 320 x 180 box: all ink (strokes included) sits at least 10 units
    inside the box, so nothing touches or is cut by the frame's border or the image edge."""
    from PIL import Image
    import numpy as np
    import json
    errs = []
    bd = D.build_dir()
    jobs = []
    w, h = 1400, int(round(1400 * 180 / 320))
    for k in FRAME_KEYS:
        svg = D.svgwrap(320, 180, frame_art(k))
        html = (f'<!doctype html><html><head><meta charset="utf-8"><style>html,body{{margin:0;background:transparent}}</style></head>'
                f'<body><div style="width:{w}px;height:{h}px;overflow:hidden;background:transparent">{svg}</div></body></html>')
        hp = D.write(f"fa-{k}.html", html)
        jobs.append({"html": hp, "png": os.path.join(bd, f"fa-{k}.png"), "width": w, "height": h})
    jp = D.write("fa-jobs.json", json.dumps(jobs))
    js = D.write("tr.js", TRANSPARENT_JS)
    subprocess.run(["node", js, jp], check=True, env=D.node_env())
    s = w / 320
    for j, k in zip(jobs, FRAME_KEYS):
        a = np.array(Image.open(j["png"]).convert("RGBA"))[..., 3]
        ys, xs = np.where(a > 8)
        if len(xs) == 0:
            errs.append(f"frame art {k} rendered empty")
            continue
        if xs.min() < 10 * s or xs.max() > 310 * s or ys.min() < 10 * s or ys.max() > 170 * s:
            errs.append(f"frame art {k}: ink at x {xs.min() / s:.1f}-{xs.max() / s:.1f}, y {ys.min() / s:.1f}-{ys.max() / s:.1f} is closer than 10 units to the frame edge")
        if (a > 8).sum() < 2500:
            errs.append(f"frame art {k} looks nearly empty")
    return errs


def class_set(badge):
    m = re.fullmatch(r"Class(?:es)? (\d)(?:–(\d))?", badge)
    if not m:
        return None
    return set(range(int(m.group(1)), int(m.group(2) or m.group(1)) + 1))


BADGE = {"board1": "Class 1", "board2": "Class 1", "board3": "Class 1", "mood": "Class 1", "spot": "Classes 1–2", "calc": "Class 2", "layers": "Classes 2–3",
         "present": f"Classes {CLASSES - 1}–{CLASSES}"}


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


def float_cell(t, bpm):
    """An independent float check of one calculator cell (bar number, bar, beat) using sixteenths = floor(t x BPM / 15 + 0.5)."""
    bp = 1 + t * bpm / 240
    i = int(math.floor(t * bpm / 15 + 0.5 + 1e-9))
    return f"{bp + 1e-9:.2f}", i // 16 + 1, 1 + (i % 16) / 4


def verify_content():
    errs = []
    counts = dict(goals=(GOALS, 4), vocab=(VOCAB, 4), reqs=(REQS, 7), steps=(STEPS, 7), tips=(TIPS, 4), check=(CHECK, 6),
                  rubric=(RUBRIC, 5), struggles=(STRUGGLES, 4), resources=(RESOURCES, 4), boards=(BOARDS, 3), slides=(SLIDES, 14), plan=(PLAN, 25),
                  logic=(LOGIC_REF, 9), hits=(EX_HITS, 4))
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
    # ---- the arithmetic, by hand first
    if (spb(120), spb(96), spb(100), spb(80)) != (Fraction(1, 2), Fraction(5, 8), Fraction(3, 5), Fraction(3, 4)):
        errs.append("seconds per beat = 60 / BPM: 0.5 at 120, 0.625 at 96, 0.6 at 100, 0.75 at 80")
    if (bar_len(120), bar_len(96), bar_len(100), bar_len(80), bar_len(128)) != (2, Fraction(5, 2), Fraction(12, 5), 3, Fraction(15, 8)):
        errs.append("seconds per bar = 240 / BPM: 2 at 120, 2.5 at 96, 2.4 at 100, 3 at 80, 1.875 at 128")
    if any(bar_len(b) != 4 * spb(b) for b in TEMPOS):
        errs.append("a bar of 4/4 is four beats")
    if Fx(SCENE_S) / bar_len(96) != 8 or Fx(SCENE_S) / bar_len(120) != 10 or [dec(Fx(SCENE_S) / bar_len(b), 2) for b in TEMPOS] != ["6.67", "8.00", "8.33", "10.00", "10.67"]:
        errs.append("bars in 20 s: 6.67, 8, 8.33, 10, 10.67 at 80, 96, 100, 120, 128")
    if [dec(Fx(SCENE_S) * b / 60, 2) for b in TEMPOS] != ["26.67", "32.00", "33.33", "40.00", "42.67"]:
        errs.append("beats in 20 s at the five tempos")
    if [dec(spb(b), 3) for b in TEMPOS] != ["0.750", "0.625", "0.600", "0.500", "0.469"] or [dec(bar_len(b), 3) for b in TEMPOS] != ["3.000", "2.500", "2.400", "2.000", "1.875"]:
        errs.append("seconds per beat and per bar to 3 decimals")
    hand = {(12.5, 96): ("6.00", "6 · 1"), (12.5, 120): ("7.25", "7 · 2"), (6.25, 96): ("3.50", "3 · 3"), (2.5, 96): ("2.00", "2 · 1"), (17.5, 96): ("8.00", "8 · 1"),
            (20, 96): ("9.00", "9 · 1"), (20, 120): ("11.00", "11 · 1"), (2, 128): ("2.07", "2 · 1.25"), (20, 128): ("11.67", "11 · 3.75"), (5, 100): ("3.08", "3 · 1.25"),
            (10, 80): ("4.33", "4 · 2.25"), (15, 120): ("8.50", "8 · 3")}
    for (t, b), (bp, bb) in hand.items():
        if dec(bar_pos(t, b), 2) != bp or bb_text(t, b) != bb:
            errs.append(f"hit point {t} s at {b} BPM should be bar {bp} = {bb}, got {dec(bar_pos(t, b), 2)} = {bb_text(t, b)}")
    for t in CALC_TIMES:
        for b in TEMPOS:
            fb = float_cell(t, b)
            bb = bar_beat(t, b)
            if dec(bar_pos(t, b), 2) != fb[0] or bb[0] != fb[1] or abs(float(bb[1]) - fb[2]) > 1e-9:
                errs.append(f"calculator cell {t} s at {b} BPM: exact {dec(bar_pos(t, b), 2)} {bb} but float check {fb}")
            if on_beat(t, b) != (abs(t * b / 60 - round(t * b / 60)) < 1e-9):
                errs.append(f"calculator cell {t} s at {b} BPM: on-beat flag wrong")
            if on_beat(t, b) and (bar_beat(t, b)[1] != int(bar_beat(t, b)[1]) or off_ms(t, b) != 0):
                errs.append(f"calculator cell {t} s at {b} BPM: a beat must have a whole beat number")
    if sixteenths(0, 96) != 0 or sixteenths(2.5, 96) != 16 or sixteenths(6.25, 96) != 40 or bar_beat(0, 96) != (1, 1) or bar_beat(Fraction(5, 16), 96) != (1, Fraction(3, 2)):
        errs.append("sixteenth-note rounding: 2.5 s at 96 BPM is sixteenth 16 (bar 2, beat 1); 6.25 s is sixteenth 40 (bar 3, beat 3)")
    if rnd(Fraction(5, 2), 0) != 3 or rnd(Fraction(1, 2), 0) != 1 or rnd(Fraction(13, 8), 2) != Fraction(163, 100) or dec(Fraction(15, 8), 3) != "1.875":
        errs.append("round half up")
    # ---- the worked example
    if EX_BPM != 96 or EX_BAR_S != Fraction(5, 2) or EX_BARS * EX_BAR_S != SCENE_S:
        errs.append("the example: 8 bars x 2.5 s = 20 s at 96 BPM")
    if [dec(bar_pos(t, EX_BPM), 2) for t in EX_TIMES] != ["2.00", "3.50", "6.00", "8.00"] or [bb_text(t, EX_BPM) for t in EX_TIMES] != ["2 · 1", "3 · 3", "6 · 1", "8 · 1"]:
        errs.append("example hit points at 96 BPM: bars 2.00, 3.50, 6.00, 8.00 = bar 2 beat 1, bar 3 beat 3, bar 6 beat 1, bar 8 beat 1")
    if [beats_from(t, EX_BPM) for t in EX_TIMES] != [4, 10, 20, 28] or any(not on_beat(t, EX_BPM) for t in EX_TIMES):
        errs.append("example hit points are 4, 10, 20 and 28 beats from the start, all on a beat")
    if [grid_class(t, 120) for t in EX_TIMES] != ["beat", "half beat", "beat", "beat"]:
        errs.append("example at 120 BPM: beat, half beat, beat, beat")
    for b in (80, 100, 128):
        if any(grid_class(t, b) == "beat" for t in EX_TIMES):
            errs.append(f"example at {b} BPM: none of the hit points lands on a beat")
    if sum(1 for t in EX_TIMES if bar_beat(t, EX_BPM)[1] == 1) != 3:
        errs.append("example: three of the four hit points land on the first beat of a bar")
    if [round(float(b - a), 6) for _n, a, b in EX_MOODS] != [2.5, 10, 5, 2.5] or EX_MOODS[0][1] != 0 or EX_MOODS[-1][2] != SCENE_S or any(EX_MOODS[i][2] != EX_MOODS[i + 1][1] for i in range(3)):
        errs.append("mood sections tile 0-20 s: 2.5, 10, 5 and 2.5 seconds (1, 4, 2 and 1 bars)")
    for need in ("96 BPM", "60 ÷ 96 = 0.625", "240 ÷ 96 = 2.5", "bar 2 beat 1, bar 3 beat 3, bar 6 beat 1 and bar 8 beat 1", "exactly 8 bars", "2.5 s", "6.25 s", "12.5 s", "17.5 s"):
        if need not in EX_STRONG:
            errs.append(f"the clear plan must say '{need}'")
    if [h[0] for h in EX_HITS] != [2.5, 6.25, 12.5, 17.5] or [h[2] for h in EX_HITS] != ["small", "medium", "big", "medium"]:
        errs.append("example hit points")
    for nm, sp, _d in EX_LAYERS:
        for a_, b_ in (sp or []):
            if not 1 <= a_ <= b_ <= EX_BARS:
                errs.append(f"layer {nm}: span {a_}-{b_} outside the piece")
    # ---- storyboards: five frames of 4 s tile 0-20 s; every frame has art, a caption and a unique key
    for b in BOARDS:
        if len(b["frames"]) != 5 or len(b["art"]) != 5 or [frame_span(i) for i in range(5)] != [(0, 4), (4, 8), (8, 12), (12, 16), (16, 20)]:
            errs.append(f"{b['key']}: five frames of 4 seconds must tile 0-20 s")
    if len(set(FRAME_KEYS)) != 15:
        errs.append("15 distinct frame drawings")
    for k in FRAME_KEYS:
        frame_art(k)
    if FRAME_S * 5 != SCENE_S:
        errs.append("5 frames x 4 s = 20 s")
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
    for need, key in ((f"{pg('board1')} to {pg('board3')}", 4), (f"page {pg('spot')}", 5), (f"page {pg('calc')}", 6), (f"page {pg('logicref')}", 8),
                      (f"page {pg('layers')}", 9), (f"pages {pg('example')} and {pg('example2')}", 9)):
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
        errs += drawing_edge_errors() + frame_art_errors() + footer_gap_errors()
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
    ntxt = txt.replace("1 e &amp; a", "1 e & a")
    if "No audio" not in notes[0]:
        errs.append("deck slide 1 notes must say 'No audio'")
    for need in ("No audio, recordings, lyrics, artists, albums or films", "invented plan on paper", "Drum Machine Designer", "Quick Sampler", "Alchemy", "Open Movie",
                 "Marker", "60 ÷ BPM", "240 ÷ BPM", "1 + t ÷ (240 ÷ BPM)", "if your version", "hit point", "foley",
                 "Created with the help of digital and AI tools. Notation and answer keys are verified before release."):
        if need.lower() not in ntxt.lower():
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
    # ---- Step N on every page, in the deck PDF text, the deck notes and UPLOAD.md agrees with the project sheet
    expect = {"board1": {1}, "board2": {1}, "board3": {1}, "mood": {1}, "spot": {2, 3}, "calc": {3}, "layers": {5}}
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
    # ---- the calculator page prints every number
    rc = raw("calc")
    for bpm in TEMPOS:
        beats20, bars20 = Fx(SCENE_S) * bpm / 60, Fx(SCENE_S) / bar_len(bpm)
        row = f"{bpm} {dec(spb(bpm), 3)} {dec(bar_len(bpm), 3)} {dec(beats20, 2)} {dec(bars20, 2)}"
        if row not in rc:
            errs.append(f"calculator page: tempo row '{row}' is not printed")
    for t in CALC_TIMES:
        row = f"{fmt(t)} " + " ".join(f"{dec(bar_pos(t, b), 2)} {bb_text(t, b)}" for b in TEMPOS)
        if row not in rc:
            errs.append(f"calculator page: row '{row}' is not printed")
    for need in ("Seconds per beat = 60 ÷ BPM", "Seconds per bar = 240 ÷ BPM", "Bar number = 1 + t ÷ (240 ÷ BPM)", "1 + 12.5 ÷ 2.5 = 6.00", "Step 3: pick a tempo", "nearest sixteenth", "5 rounds up"):
        if need not in rc:
            errs.append(f"calculator page must say '{need}'")
    # ---- the worked example prints its numbers
    re1 = raw("example") + " " + raw("example2")
    for i, (t, what, size, _s) in enumerate(EX_HITS, start=1):
        b, k = bar_beat(t, EX_BPM)
        row = f"{i} {fmt(t)} {what} {size} 1 + {fmt(t)} ÷ 2.5 = {dec(bar_pos(t, EX_BPM), 2)} {b} · {float(k):g}"
        if row not in re1:
            errs.append(f"worked example: hit-point row '{row}' is not printed")
    for bpm in TEMPOS:
        row = f"{bpm} {dec(spb(bpm), 3)} {dec(bar_len(bpm), 3)} " + " ".join(f"{bb_text(t, bpm)} {lands_text(t, bpm)}" for t in EX_TIMES)
        if row not in re1:
            errs.append(f"worked example: tempo row '{row}' is not printed")
    for need in ("60 ÷ 96 = 0.625 s", "240 ÷ 96 = 2.5 s", "8 bars = 8 × 2.5 = 20 seconds", "20 ÷ 2.5 = 8 bars", "ends on bar 9, beat 1", "2.5 × 96 ÷ 60 = 4", "6.25 × 96 ÷ 60 = 10",
                 "12.5 × 96 ÷ 60 = 20", "17.5 × 96 ÷ 60 = 28", "1, 4, 2 and 1 bars"):
        if need not in re1:
            errs.append(f"worked example must say '{need}'")
    for t in (2.5, 6.25, 12.5, 17.5):
        if f"{fmt(t)} s gives bar {dec(bar_pos(t, EX_BPM), 2)}" not in re1 and f"{fmt(t)} s gives bar {dec(bar_pos(t, EX_BPM), 2)}".replace("17.5 s gives", "and 17.5 s gives") not in re1:
            errs.append(f"worked example: '{fmt(t)} s gives bar {dec(bar_pos(t, EX_BPM), 2)}' is not printed")
    # ---- storyboards, spotting sheet, layer plan
    for b in BOARDS:
        r = raw(b["key"])
        for i in range(5):
            a, e = frame_span(i)
            for need in (f"Frame {i + 1} · {a}–{e} s", b["frames"][i]):
                if need not in r:
                    errs.append(f"{b['key']} page: '{need}' is not printed")
        for need in ("Step 1: choose the scene", "five frames of 4 seconds"):
            if need not in r:
                errs.append(f"{b['key']} page must say '{need}'")
    rs = raw("spot")
    for need in ("Step 2: spot it", "Step 3: pick a tempo", "One beat = 60 ÷ BPM", "One bar = 240 ÷ BPM", "t × BPM ÷ 60 is a whole number", "Bars in my scene = 20 ÷ one bar"):
        if need not in rs:
            errs.append(f"spotting sheet must say '{need}'")
    rl = raw("layers")
    for need in ("Step 5: build the layers", "20 × BPM ÷ 240"):
        if need not in rl:
            errs.append(f"layer plan page must say '{need}'")
    up = open(os.path.join(HERE, "UPLOAD.md"), encoding="utf8").read()
    errs += step_ref_errors(up, "UPLOAD.md")
    if "Grades 9-12" not in up or "`9th-grade`, `10th-grade`, `11th-grade`, `12th-grade`" not in up:
        errs.append("UPLOAD.md: grades 9-12 in the description and section 3")
    if "no audio" not in up.lower() or "Open question" not in up or "Timing numbers" not in up:
        errs.append("UPLOAD.md: must say no audio is included, record the timing numbers checked and the open questions")
    m = re.search(r"= 1 cover \+ (\d+) teacher \+ (\d+) student \+ 1 terms page", up)
    if not m or 2 + int(m.group(1)) + int(m.group(2)) != len(PLAN):
        errs.append("UPLOAD.md: the page-count list (1 cover + teacher + student + 1 terms) must total the PDF's pages")
    if m and (int(m.group(1)) != D.IX("example2") - 1 or int(m.group(2)) != D.IX("reflect") - D.IX("board1") + 1):
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
    return (f"seconds per beat = 60 / BPM and per bar = 240 / BPM recomputed exactly (fractions) and by an independent float method for every cell of the hit-point "
            f"calculator ({len(CALC_TIMES)} times x {len(TEMPOS)} tempos: bar number, bar · beat after the sixteenth-note rounding rule, beat flag); the worked example is "
            f"{SCENE_S} s at {EX_BPM} BPM = {EX_BARS} bars with hit points at bars 2.00, 3.50, 6.00, 8.00 (all on a beat) and its five-tempo comparison; 3 storyboards of 5 frames x "
            f"{FRAME_S} s = 20 s, each frame's art inside its box; every 'Step N' agrees with the project sheet on pages, slides, notes and UPLOAD.md; class badges agree with the "
            f"pacing page; every drawing renders alone on a transparent ground with no ink at its edges; hero art inside its viewBox; no truncated slide bullets; "
            f"edges of cover.png and previews clear; no audio, lyrics, melodies, film or artist names or student work; grades 9-12; tags and subjects are not headings; "
            f"no 'what changed' page (ORIGINAL).")


# ================================================================ UPLOAD.md (written by gen.py so every number matches the build)
def write_upload():
    np_, ns = len(PLAN), len(SLIDES)
    n_teacher = (PLAN.index("example2") + 1) - 1
    n_student = (PLAN.index("reflect") + 1) - (PLAN.index("board1") + 1) + 1
    assert 2 + n_teacher + n_student == np_, "page-count list must total the PDF"
    nt = len(LISTING_TITLE)
    desc = (f"{DESC_START} students score a 20-second winter scene in Logic Pro, filmed on a phone or taken from one of three printable storyboards. They name the mood and the "
            f"emotional arc, mark hit points on a timeline, choose a tempo so the hits land on beats or bars, and build the score from a pad, a motif of their own, percussion hits "
            f"and foley accents. This Snow Day Film Score project takes {CLASSES} class periods (the pacing guide also shows two and four) and is an original Hudson Beat project; "
            f"the steps are written for Logic Pro, while the ideas (hit points, tempo math, layers) carry over to GarageBand.\n\n"
            f"WHAT'S INCLUDED (ZIP: {np_}-page PDF = 1 cover + {n_teacher} teacher + {n_student} student + 1 terms page, plus {ns}-slide intro deck as .pptx and PDF)\n"
            f"• Teacher pages: how to use, project overview, setup, a {CLASSES}-class pacing guide with the deck slides for each class, two pages of teacher notes "
            f"(struggles, variations, resources, grading), a Logic quick reference and a two-page worked example (an invented 20-second ice-skating scene with 4 hit points at 96 BPM = 8 bars, "
            f"a score map and every number worked out) ({n_teacher} pages)\n"
            f"• Student pages: three ready-made storyboards to print (a snow-day morning, sledding and snowman building, five 4-second frames each, with a timeline for marking hit points), "
            f"a mood and emotional-arc page with a word bank, a spotting sheet, the hit-point calculator (bar numbers and bar · beat for 12 times at 80, 96, 100, 120 and 128 BPM), "
            f"a layer plan, the 3-page project sheet (overview, goals, vocabulary, requirements, steps, tips, submission checklist), the /{RUBRIC_TOTAL} rubric, a vocabulary page, "
            f"a feedback planner and a reflection page ({n_student} pages)\n"
            f"• Teacher-presented intro deck, {ns} slides with speaker notes on every slide: a think-and-share hook, what the project is, mood and arc, spotting, seconds to bars, "
            f"the four layers, building it in Logic, a worked-example map, what to turn in and the rubric\n\n"
            f"THE THREE CLASS PERIODS\n"
            f"• Class 1: hook; choose the scene; name its mood and arc; spot the hit points\n"
            f"• Class 2: turn times into bars and pick a tempo; set up Logic with markers; start the pad and the motif\n"
            f"• Class 3: percussion hits and foley accents; automation, mix and bounce; present and reflect\n\n"
            f"WHAT STUDENTS LEARN\n"
            f"• Spotting a scene: finding its mood, its emotional arc and its hit points\n"
            f"• Timing math: seconds per beat = 60 ÷ BPM, seconds per bar in 4/4 = 240 ÷ BPM, and bar number = 1 + t ÷ (240 ÷ BPM) (at 96 BPM a 20-second scene is exactly 8 bars)\n"
            f"• Scoring to picture in Logic Pro: importing a movie with File > Open Movie, markers on hit points, a pad in Alchemy or Retro Synth, Quick Sampler, "
            f"Drum Machine Designer, automation and bounce\n"
            f"• Layering a pad, a motif they invent, percussion hits and foley, and explaining their choices in a reflection\n\n"
            f"GOOD TO KNOW\n"
            f"• There is no audio in this resource and no student work. No melody, film music or song is printed or notated; students make every sound themselves in Logic Pro\n"
            f"• Requires Logic Pro on a Mac. A MIDI keyboard is not needed; nobody has to read music. Students who cannot film use a storyboard. Where a control may differ between versions, the pages say \"if your version has it\"\n"
            f"• Rubric: 5 categories scored 1-5, /{RUBRIC_TOTAL}; the final grade is the average of the student's and the teacher's score\n"
            f"• Grades 9-12; music technology or music production classes\n"
            f"• The deck uses the free Oswald and Source Sans 3 fonts (built into Google Slides); install them for PowerPoint or Keynote, or present "
            f"the PDF copy, which shows the intended look\n"
            f"• Every student page prints well in black and white\n\n"
            f"Logic Pro is a product of Apple Inc., named only to describe compatibility. This resource is not affiliated with Apple.\n\n"
            f"{D.DISCLOSURE_NEW}")
    ex = ", ".join(f"{fmt(t)} s = bar {dec(bar_pos(t, EX_BPM), 2)} (bar {bar_beat(t, EX_BPM)[0]} beat {float(bar_beat(t, EX_BPM)[1]):g})" for t in EX_TIMES)
    md = f"""# UPLOAD: Snow Day Film Score, original Logic Pro project (TpT 061)

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
({nt} characters; the limit is 80.) The title leaves out Winter, Holiday, Christmas and Snow because TpT's Seasonal Titles notice blocked a holiday-named title on 027 (see 032, 033 and 034). "Logic Pro" sits in the first 30 characters.

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

**${PRICE}** (paid), multiple-license price ${PRICE}. The $9 in the queue, at the top of the $7-9 holiday-kit range, for a kit with {np_} pages + {ns} slides, three printable storyboards, a hit-point calculator, a spotting sheet and a two-page worked example, listed in November and December.

## 8. Free or paid / free preview pages

Paid. Preview PDF (4 watermarked pages): the {CLASSES}-class pacing guide, the first storyboard, the hit-point calculator and the /{RUBRIC_TOTAL} rubric. "Number of pages or slides" is {np_ + ns} ({np_} pages + {ns} slides).

## 9. Before you click publish

- [ ] **Needs QA approval first.** This is a new kit (not yet on TpT); the Manager releases it only after a QA `**Verdict: APPROVED**`.
- [ ] Cover and previews show "HUDSON BEAT" in type; PDF footers read "© 2026 Brian Lotze · Hudson Beat · For single-classroom use".
- [ ] No school name, logo, student names or work, audio, video, lyrics, melody, film title or Logic session anywhere (`gen.py --check` scans every output and every file in this folder).
- [ ] **No tune, no melody, no film music.** The kit holds no song, carol, film music or notation; students invent every motif. Nothing to date or source.
- [ ] **Timing numbers (all recomputed in `gen.py --check`, exactly with fractions and again with an independent float method).** Seconds per beat = 60 / BPM; seconds per bar in 4/4 = 240 / BPM; a hit point at t seconds is at bar number 1 + t / (240 / BPM). At 96 BPM a beat is 0.625 s and a bar 2.5 s, so 20 s = 8 bars; at 120 BPM a bar is 2 s, so 20 s = 10 bars; at 80, 100 and 128 BPM the scene is 6.67, 8.33 and 10.67 bars. Rounding: seconds to 3 decimals, bar numbers to 2 (half up); a marker is rounded to the nearest sixteenth note (sixteenths = t x BPM / 60 x 4), then bar = sixteenths // 16 + 1 and beat = 1 + (sixteenths mod 16) / 4. Calculator table: 12 times (2 to 20 s) at 80, 96, 100, 120 and 128 BPM. Worked example at 96 BPM: {ex}; the four hit points are 4, 10, 20 and 28 beats from the start, so each lands on a beat; at 120 BPM they land on beat, half beat, beat, beat; at 80, 100 and 128 BPM none lands on a beat.
- [ ] **Original project.** Built with `ORIGINAL = True` in `tpt/_dmp2_common/dmp2.py` (like 031, 036, 053 and 057): no "what changed" page and the new disclosure line. The reflection page is the shared Reflection element, scored in the rubric's "Plan & Reflection" row. `dmp2.py` is unchanged.
- [ ] **Art.** The cover, previews and deck use the owner's pre-made art (`art/hero.png`, a clapperboard, studio headphones, a snowy pine and a snowflake, no text), copied whole from `tpt/_art/next/snow-day-film-score/`; the file is logged in `tpt/_art/USAGE.md`. The storyboard frames, timelines and score map are drawn in code. Needs art: none.
- [ ] **Logic Pro names to confirm on a Mac with a current Logic.** File > Open Movie... (hedged: "look for it in the File menu; the wording can differ by version"), the Movie global track and Movie window, the Marker global track with a plus (+) button and a Create Marker key command (hedged), the time display and timecode (hedged), Alchemy and Retro Synth pad patches, Scale Quantize (hedged), Drum Machine Designer, Quick Sampler (import, record, reverse: hedged), automation (A), Mixer (X), Command-B bounce. Whether a bounce can include the movie is not claimed. Nothing says a loop or preset of a given name exists.
- [ ] **Open questions for the owner:** (1) **Open Movie.** Please confirm on a Mac that File > Open Movie... exists in the current Logic Pro and that a phone .mov or .mp4 imports; the pages hedge the wording. (2) **Title.** No Winter, Holiday, Christmas or Snow in the title because of TpT's seasonal-title notice (see 1). (3) **Price.** $9, as in the queue. (4) **Classes.** Three periods; the pacing page shows how to run it in two or four.
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
