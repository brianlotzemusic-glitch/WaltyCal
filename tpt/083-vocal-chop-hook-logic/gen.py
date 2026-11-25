#!/usr/bin/env python3
"""Logic Pro project kit: Winter Vocal Chop (TpT 083): the teacher resource, the intro deck and the listing files.

    python3 gen.py            build everything into this folder (also writes UPLOAD.md)
    python3 gen.py --lowres   same, but square images at scale 1 and small page shots (self-check only; --check rejects it)
    python3 gen.py --check    verify content and layout: the timing arithmetic (one bar of 4/4 = 240 / BPM s, one 16th-note step = 15 / BPM s, 16 steps = one bar, 4 bars = 960 / BPM s,
                              16 bars = 3840 / BPM s; a 16th note at 120 BPM = 0.125 s; slice length = phrase length / slices, exact fractions and an independent float method), the tempo table,
                              the slice map (8 equal slices of a 3-second phrase = 0.375 s = 3 steps at 120 BPM; start, end and length of every slice; 16 slices), the model chop pattern
                              (hits per bar 6, 6, 6 and 8 counted from the data, counted again in the drawn step grid, one hit per step, every slice used, hit times in seconds), the drum groove
                              (kick 3, snare 2, hat 8), the pitch table (ratio = 2^(n/12): +12 = x2.000, +7 = x1.498, -5 = x0.749; intervals add and ratios multiply; slice length / ratio), the
                              arrangement (5 layers, 4 sections, 16 bars = 32 s at 120 BPM), Step N references on every page, slide and UPLOAD.md, class badges against the pacing page, drawings
                              (each rendered alone on a transparent ground: no ink within 4 px of its edge), the hero art, files, page and slide counts, class slots, fonts, fit and overlap, dead
                              space, footer gap (pages and deck slides), black-box padding (deck slides), the edges of cover.png and the previews, banned strings, tpt.json and UPLOAD.md

An ORIGINAL Hudson Beat project (dmp2.ORIGINAL = True, like 063, 067, 070, 076 and 080). Students record ONE short hummed phrase in their own voice (2 to 4 seconds, no words, no existing melody),
load it in Quick Sampler (if their version has it), slice it into 8 or 16 pieces, map the slices to keys, play a 4-bar chop pattern on a 16-step grid, pitch pieces by semitones, add a simple drum groove
and bass, and arrange an 8- or 16-bar hook with an intro, hook, drop and outro. No audio ships and no existing songs or recordings are used. The art on the cover, the previews and the deck is the owner's
pre-made hero (art/hero.png: a studio microphone, laptop with a waveform, monitors, headphones, interface and pad controller), used whole. Everything else is drawn in code. The shared builder is
../_dmp2_common/dmp2.py (untouched).
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
SLUG = "vocal-chop-hook"
TITLE = "Winter Vocal Chop"
ACCENT = "#2F7FB8"          # this product's single accent: icy blue (a shade deeper than the art's #4FA3D9, so small labels read)
ACC_LIGHT = "#DCEBF6"
PRICE = "8.00"
CLASSES = 3
GRADES_TEXT = "9–12"
GRADE_SLUGS = ["9th-grade", "10th-grade", "11th-grade", "12th-grade"]
TAGS = ["Winter", "Project-based Learning", "Projects", "Activities"]     # exact entries of tpt/TAG-OPTIONS.json, none a heading
SUBJECTS = ["Music", "Computer Science - Technology", "Music Composition"]     # all in SUBJECT-OPTIONS.json, none a heading
ANSWER_KEY = None
LISTING_TITLE = "Logic Pro Vocal Chop Project | Quick Sampler, Slices, Hook | High School"
DESC_START = "Vocal chop project for high school music technology:"
DESC_MUST = ["Winter Vocal Chop", "Quick Sampler", "16th-note", "15 ÷ BPM", "120 BPM", "no audio", "semitone", "2^(n/12)", "0.375"]
ZIP_DIR = "Winter Vocal Chop - Hudson Beat"
ZIP_DATE = (2026, 11, 25, 12, 0, 0)
TYPE = "Original Project"
PROJ_LINE = "Music Technology | <i>Vocal Chop Project</i> | 3 class periods"
DECK_STRAP = "Hum, slice, pattern, hook"
REFLECT_ROW = "Plan &amp; Reflection"
# split so this file never contains them (the --check scan reads every file in this folder)
BANNED_EXTRA = ["Rud" + "olph", "Fro" + "sty", "Gri" + "nch", "Santa Claus " + "Is", "Jingle Bell " + "Rock", "Feliz " + "Navidad",
                "Mari" + "ah Carey", "Spoti" + "fy", "You" + "Tube", "Home " + "Alone", "Nin" + "tendo", "Ro" + "land",
                "Star " + "Wars", "Hans " + "Zimmer", "John " + "Williams", "Harry " + "Potter", "Pix" + "ar", "Lord of the " + "Rings",
                "Winter " + "Wonderland", "Let It " + "Snow", "Sleigh " + "Ride", "X" + "mas", "Times " + "Square", "Auld " + "Lang",
                "Ak" + "ai", "Ab" + "leton", "FL " + "Studio", "Sound" + "Cloud", "Tik" + "Tok", "Spl"+"ice", "Ser" + "um"]

# ================================================================ page plan (teacher pages 2-10, student pages 11-25)
PLAN = ["cover", "howto", "overview", "setup", "pacing", "tn1", "tn2", "logicref", "example", "example2", "timing", "record", "slicemap", "pattern", "pitch",
        "drums", "arrange", "mix", "proj1", "proj2", "proj3", "rubric", "vocab", "present", "reflect", "terms"]


def pg(k):
    return PLAN.index(k) + 1


# ================================================================ the arithmetic (exact fractions; all verified in --check)
TEMPOS = (80, 90, 100, 110, 120, 128)       # the timing table's rows
EX_BPM = 120                                # the worked example's tempo
PHRASE = Fraction(3)                        # the worked example's hummed phrase: 3 seconds
PHRASES = (Fraction(2), Fraction(5, 2), Fraction(3), Fraction(7, 2), Fraction(4))     # the 2 to 4 second range
NSLICE = 8                                  # the slices in the model (8 equal slices)
NSLICE_ALT = 16
STEPS_BAR = 16                              # 16th-note steps in one bar of 4/4
BEATS_BAR = 4
PAT_BARS = 4                                # the chop pattern is 4 bars
ARR_BARS = 16                               # the arrangement
ARR_BARS_ALT = 8


def spb(bpm):
    """Seconds per beat = 60 / BPM."""
    return Fraction(60, bpm)


def bar_len(bpm):
    """Seconds per bar of 4/4 = 240 / BPM (four beats)."""
    return Fraction(240, bpm)


def step_len(bpm):
    """Seconds per 16th-note step = 15 / BPM (a quarter-note beat holds four steps)."""
    return Fraction(15, bpm)


def slice_len(L, n):
    """Seconds per equal slice of a phrase of L seconds cut into n pieces."""
    return Fraction(L) / n


def slice_steps(L, n, bpm):
    """How many steps one slice lasts at a tempo: (L / n) / (15 / BPM)."""
    return slice_len(L, n) / step_len(bpm)


def hit_time(bpm, bar, step):
    """Seconds from the start of the pattern to grid step `step` (1 to 16) of bar `bar`: ((bar - 1) x 16 + (step - 1)) x 15 / BPM."""
    return ((bar - 1) * STEPS_BAR + (step - 1)) * step_len(bpm)


def rnd(x, nd):
    """Round half up (a 5 rounds up) to nd decimals, on exact fractions."""
    s = Fraction(10) ** nd
    return Fraction(math.floor(Fraction(x) * s + Fraction(1, 2)), 1) / s


def dec(x, nd):
    return f"{float(rnd(x, nd)):.{nd}f}".replace("-", "−")


def exact(x):
    """An exact decimal (the denominator has only the factors 2 and 5), with no trailing zeros: 3/8 -> 0.375, 5/32 -> 0.15625."""
    x = Fraction(x)
    d = x.denominator
    while d % 2 == 0:
        d //= 2
    while d % 5 == 0:
        d //= 5
    assert d == 1, f"{x} is not a terminating decimal"
    s = f"{float(x):.6f}".rstrip("0").rstrip(".")
    return s


def fmt(x):
    x = float(x)
    x = round(x + 1e-9, 4)
    return f"{x:.0f}" if x == int(x) else f"{x:g}"


# ---- pitch: ratio = 2^(n / 12), n in semitones
SEMITONE = 2 ** (1 / 12)
PITCHES = (-12, -7, -5, 0, 3, 4, 5, 7, 12)
INTERVALS = {-12: "octave down", -7: "fifth down", -5: "fourth down", 0: "same pitch", 3: "minor third up", 4: "major third up", 5: "fourth up", 7: "fifth up", 12: "octave up"}
HUM_HZ = 200                                # an example number for a low hum, labeled as an example


def ratio(n):
    return 2 ** (n / 12)


def r3(x):
    return f"{math.floor(x * 1000 + 0.5) / 1000:.3f}"


def r4(x):
    return f"{math.floor(x * 10000 + 0.5) / 10000:.4f}"


def r1(x):
    return f"{math.floor(x * 10 + 0.5) / 10:.1f}"


def sgn(n):
    return "0" if n == 0 else (f"+{n}" if n > 0 else f"−{-n}")


# ---- the model chop pattern: 4 bars of 16 steps; each hit is (grid step 1-16, slice 1-8); one hit per step (one slice sounds at a time)
PATTERN = [
    [(1, 1), (4, 2), (7, 3), (9, 1), (11, 4), (15, 2)],
    [(1, 1), (4, 2), (7, 3), (9, 1), (11, 5), (13, 6)],
    [(1, 7), (4, 8), (7, 7), (9, 8), (11, 3), (15, 4)],
    [(1, 1), (3, 2), (5, 3), (7, 4), (9, 5), (11, 6), (13, 7), (15, 8)],
]
PAT_HITS = [len(b) for b in PATTERN]                    # 6, 6, 6, 8
# a simple drum groove: one bar of 16 steps, repeated
DRUMS = [("KICK", [1, 9, 11]), ("SNARE", [5, 13]), ("HAT", [1, 3, 5, 7, 9, 11, 13, 15])]
# the bass plays one low note per bar: semitones from the hum's key, bars 1-4 (root, root, fourth below, fifth below)
BASS = [0, 0, -5, -7]
# the arrangement: 16 bars; rows and the bars each layer plays
ARR_ROWS = [("CHOPS", [(1, 8), (10, 16)]), ("PITCHED", [(5, 8), (11, 12)]), ("REVERSE", [(4, 4), (8, 8), (12, 12)]), ("DRUMS", [(5, 12)]), ("BASS", [(9, 12)])]
ARR_SECTIONS = [("INTRO", 1, 4), ("HOOK", 5, 8), ("DROP", 9, 12), ("OUTRO", 13, 16)]
ARR_LAYERS = [r for r, _ in ARR_ROWS]
PITCH_USED = [(1, 12), (3, 7), (5, -5)]                 # slices pitched in the example: (slice, semitones)


def slice_hits(s):
    """Hits of slice s in the model pattern."""
    return sum(1 for b in PATTERN for _, sl in b if sl == s)


# ================================================================ the project text (original; students read these pages)
THEME = ("A vocal chop is a short piece of a recorded voice that is cut out, played from a key or pad and repeated in a pattern, so that a hum becomes a hook. "
         "This project starts from a winter morning: a hum inspired by wind at the window, boots on snow or a kettle starting to sing. "
         "Students record their own voice, so there is no existing song, melody or recording anywhere in the project.")
BUILD_NOTE = ("The skills here are the ones every sample-based track needs: record a clean source, cut it into pieces, play the pieces on a grid, change their pitch by an exact number of "
              "semitones and arrange them into sections. They carry over to beat making, remixing and sound design.")
OVERVIEW = ("Make a hook in Logic Pro from one short hummed phrase. Students record about 2 to 4 seconds of their own voice (a hum, no words, no existing melody), load it in Quick Sampler (if their version has it), "
            "and slice it into 8 or 16 pieces. They put the slices on keys, play a 4-bar chop pattern on a 16-step grid, pitch some slices by semitones, try a reversed slice, and add a simple drum groove and bass. "
            "The result is an 8- or 16-bar arrangement with an intro, a hook, a drop and an outro. Timing math drives every choice, and nobody needs to read music.")
GOALS = ["Plan a hook with timing math: one bar of 4/4 = 240 ÷ BPM seconds and one 16th-note step = 15 ÷ BPM seconds (0.125 s at 120 BPM)",
         "Record a clean hum in your own voice and cut it into 8 or 16 slices, using slice length = hum length ÷ number of slices",
         "Play slices from keys in a 4-bar, 16-step chop pattern and read it as a step grid with a count of hits per bar",
         "Pitch slices by semitones with the ratio 2^(n ÷ 12) (+12 is × 2.000, +7 is × 1.498, −5 is × 0.749) and arrange an 8- or 16-bar hook"]
VOCAB = [("Chop", "To cut a recording into short pieces and play them in a new order or pitch"),
         ("Slice", "One piece of a recording between two slice markers; each slice can be played from its own key"),
         ("Transient", "The sudden start of a sound, such as a hard consonant or a drum hit"),
         ("Sampler", "An instrument that records and plays back samples (recorded sounds) from keys or pads"),
         ("Pitch", "How high or low a sound is; here it changes by semitones, and 12 semitones make an octave"),
         ("Pattern", "A group of hits placed on steps that repeats; here it is 4 bars long"),
         ("Hook", "A short musical idea that is easy to remember and comes back during a piece"),
         ("Step", "One 16th-note slot on the grid; 16 steps make one bar of 4/4")]
REQS = ["Choose a tempo and fill in the timing page: one step = 15 ÷ BPM seconds (page @TIMING)",
        "Record one hummed phrase of 2 to 4 seconds in your own voice, with no words and no existing melody (page @RECORD)",
        "Slice the hum into 8 or 16 pieces in Quick Sampler (if your version has it) and fill in the slice map (page @SLICEMAP)",
        "Play a 4-bar chop pattern on a 16-step grid and draw its hits on the step grid (page @PATTERN)",
        "Pitch two or more of your slices by semitones and try one reversed slice (page @PITCH)",
        "Add a simple drum groove and a bass, then arrange 8 or 16 bars with an intro, hook, drop and outro (pages @DRUMS and @ARRANGE)",
        "Mix and bounce your hook, then reflect on your choices (pages @MIX and @REFLECT)"]
FILE_NAME = "“Your Name – Chop”"
STEP_NAMES = ["Plan the hook", "Record the hum", "Slice and map", "Play the chop pattern", "Pitch and flip", "Groove, arrange and mix", "Present &amp; get feedback"]
STEPS = ["<b>Plan the hook</b> — Use the timing page (page @TIMING) to pick a tempo and work out how long one step, one bar and one slice last",
         "<b>Record the hum</b> — Hum one short phrase of 2 to 4 seconds in your own voice, with no words and no existing melody, and use the recording checklist (page @RECORD)",
         "<b>Slice and map</b> — Load the hum in Quick Sampler (if your version has it), slice it into 8 or 16 pieces and give each slice its own key (page @SLICEMAP)",
         "<b>Play the chop pattern</b> — Play the slices on a 16-step grid for 4 bars and draw the hits on the step grid (page @PATTERN; quick reference: page @LOGICREF)",
         "<b>Pitch and flip</b> — Change some slices by semitones, try one reversed slice and note the ratios on the pitch table (page @PITCH)",
         "<b>Groove, arrange and mix</b> — Add a drum groove and a bass (page @DRUMS), build an 8- or 16-bar arrangement (page @ARRANGE), then mix with the checklist (page @MIX) and bounce",
         "<b>Present &amp; get feedback</b> — Write three questions you want classmates to answer about your hook. Play it, point out the slices, the pattern, the pitched chops and the sections as they arrive, "
         "and answer at least 2 of each classmate’s questions. Then reflect (page @REFLECT)."]
TIPS = ["Hum on one comfortable note or a gentle slide. A steady hum slices into pieces that sound good in any order.",
        "Record two or three takes and keep the cleanest. The recording is the only sound you have, so make it good before you cut it.",
        "Start with a simple pattern and add one change at a time. Listen after each change.",
        "Save a new version of your project at the end of each class, so you can always go back."]
CHECK = ["Bounced .mp3 or .wav of your hook, 8 or 16 bars long",
         "Zipped .logicx project file handed in",
         f"Files named correctly: {FILE_NAME}",
         "Timing page, slice map and step grid handed in",
         "Rubric self-score done (page @RUBRIC)",
         "I can say my tempo, how long one step and one slice last, and where each section starts"]
RUBRIC_NOTE = "Each category is scored 1–5. Score yourself first; the final grade is the average of your score and your teacher’s."
LEVELS = [1, 2, 3, 4, 5]
RUBRIC = [
    ("Hum & Recording", ["No hum recorded", "Too quiet, clipping or full of room noise", "Usable hum, but it has words, noise or an uneven level",
                         "Clean hum of 2 to 4 seconds in the student’s own voice, no clipping", "Clean, steady hum that slices well, with notes on the takes"]),
    ("Slices & Pattern", ["No slices or no pattern", "Slices cut mid-sound; pattern does not repeat", "Slices mapped; a 4-bar pattern with some timing slips",
                          "8 or 16 slices mapped to keys; a 4-bar, 16-step pattern that matches the step grid", "Clean slices and a pattern with a clear shape and variation"]),
    ("Pitch & Sound Design", ["No pitch changes", "Pitch changes are random or out of tune", "Two of the slices pitched, with some ratios unchecked",
                              "Two or more slices pitched by semitones, one reversed slice, ratios on the table", "Pitch and reverse choices that are deliberate and explained"]),
    ("Groove & Arrangement", ["No drums, bass or sections", "Drums or bass only, no sections", "Groove and bass, with unclear sections",
                              "8 or 16 bars with an intro, hook, drop and outro; a clear drum groove and bass", "A clear arrangement with a balanced mix that ends on time"]),
    ("Plan & Reflection", ["Plans, presentation or reflection missing", "Thin plan; little to say about choices", "Plan and reflection complete, with basic detail",
                           "Correct timing math, slice map and grid; thoughtful reflection", "Insightful reflection and a polished presentation"]),
]
RUBRIC_TOTAL = 25
RUBRIC_SHORT = ["A clean, steady hum that slices well",
                "Clean slices and a pattern with a clear shape",
                "Deliberate, explained pitch and reverse choices",
                "A clear arrangement and a balanced mix",
                "Insightful reflection and a polished presentation"]
RUBRIC_SLIDE_LINE = "Scored 1–5 · final grade = average of your score and mine, out of 25"
RUBRIC_ROW_PITCH = 0.86
RUBRIC_LINE_Y = 6.3

TN_REINFORCES = ("Teaches how a sample-based hook is made. Students learn to record a clean source, to cut it into slices of a planned length, to play the slices on a 16-step grid, "
                 "to change pitch by semitones with an exact frequency ratio, and to arrange the result into sections, all in Logic Pro.")
STRUGGLES = ["The slices click or cut off a sound: move the slice marker to the start of a sound (a transient), not into the middle of one, and listen again (page @SLICEMAP).",
             "The chops feel off the beat: check the project tempo, set the snap or grid to 16th notes and count the steps on the step grid (pages @TIMING and @PATTERN).",
             "A pitched slice sounds too short or too fast: in many samplers a higher pitch plays the recording faster, so its slice is shorter. The pitch table shows the new length (page @PITCH).",
             "The hook sounds crowded: take layers away until the chops are clear again, and bring them back one at a time (page @ARRANGE)."]
VAR_EASY = ("Keep the tempo at 120 BPM, where a step lasts 0.125 seconds and a 3-second phrase cut into 8 slices gives slices of exactly 3 steps (page " + str(pg("timing")) + "); slice into 8 pieces only, "
            "use the model pattern on page " + str(pg("pattern")) + " and an 8-bar arrangement.")
VAR_HARD = ("Slice into 16 pieces, write a different 4-bar pattern for the drop and pitch three or more slices (page " + str(pg("pitch")) + "). "
            "Or build a 16-bar arrangement with a second hum recorded at a different pitch.")
RESOURCES = [("Timing page (page @TIMING)",
              "Seconds per beat, step and bar at six tempos, the length of a 4-bar and a 16-bar section, and the length of a slice for hums of 2 to 4 seconds."),
             ("Recording checklist (page @RECORD)",
              "A checklist for a quiet room, mic distance and levels, a copyright note, and a take log."),
             ("Slice map and step grid (pages @SLICEMAP and @PATTERN)",
              "A waveform with slice lines, a keyboard map, a slice table, and a 4-bar step grid with the hits per bar."),
             ("Pitch table (page @PITCH)",
              "Semitone offsets with their frequency ratios and what each does to the length of a slice."),
             ("Groove, arrangement and worked example (pages @DRUMS, @ARRANGE and @EXAMPLE–@EXAMPLE2)",
              "A drum groove, a bass plan, a 16-bar arrangement map, and an invented hook at 120 BPM. A model, not a template.")]
TN_NOTE = ("A good listening day: play each hook and ask the class two questions. Could you tell the hook is a voice? Which slice did you hear most often? "
           "If a slice sounds wrong, find it on the slice map together. This kit names no songs or artists.")
GRADING = ["The rubric: five categories, each scored 1–5, /25 (page @RUBRIC). Students score themselves first; the final grade is the "
           "average of their score and yours.",
           "Hum & Recording (rubric row 1): listen for noise and clipping, check the take log and ask for the hum’s length in seconds (page @RECORD).",
           "Slices & Pattern (rubric row 2): check the slice map against the number of slices and compare the step grid with what plays (pages @SLICEMAP and @PATTERN).",
           "Pitch & Sound Design (rubric row 3): ask the student to read the ratio for each pitched slice from the pitch table (page @PITCH).",
           "Groove & Arrangement (rubric row 4): play the whole hook and find the intro, hook, drop and outro on the arrangement map (pages @DRUMS and @ARRANGE).",
           "Plan & Reflection (rubric row 5): the timing page, the slice map, the feedback questions and the Reflection page (page @REFLECT) are the evidence."]
PACING = [
    {"n": 1, "owner": "Hear the idea, plan the timing, record the hum and cut it into slices.",
     "do": "Slides 1–8: the think-and-share, what the project is, the three classes, the slices, the timing math, the keys and the recording checklist. Hand out the timing page, the recording page and the slice map. "
           "Before they leave, students have a tempo, a clean hum and a first slice map.",
     "slides": (1, 8), "pages": ["timing", "record", "slicemap", "proj1", "proj2", "proj3", "vocab"],
     "deck": "Hear the hook · one step = 15 ÷ BPM · record · slice"},
    {"n": 2, "owner": "Finish the slices, play a 4-bar chop pattern and pitch some slices.",
     "do": "Slides 9–11: chopping in Quick Sampler, the 4-bar step grid and pitch by semitone. Demonstrate loading the hum and playing a slice from its key, then the pattern, then one pitched slice. Students finish "
           "the slice map, play and draw a 4-bar pattern, and pitch two or more slices. Walk the room with one question: which step is this hit on?",
     "slides": (9, 11), "pages": ["slicemap", "pattern", "pitch", "present"], "deck": "Chop it in Quick Sampler · the step grid · pitch"},
    {"n": 3, "owner": "Add drums and bass, arrange the hook, mix, bounce, present and reflect.",
     "do": "Slides 12–17: the drum groove and bass, the arrangement, what to turn in, the rubric, presentation day and the wrap-up. Students add a groove and a bass, arrange 8 or 16 bars, mix with the checklist, "
           "bounce and present.",
     "slides": (12, 17), "pages": ["drums", "arrange", "mix", "rubric", "present", "reflect"], "deck": "Groove and bass · arrangement · checklist · presentations"},
]
PACING_EXTRA = (
    '<div class="cols" style="margin-top:4pt;gap:14pt"><div class="box acc-b"><span class="k">The one thing to do on Class 1</span>'
    '<p style="margin:0;font-size:10.6pt">Make sure every student leaves with a tempo, a clean hum of 2 to 4 seconds and a first set of slices that each play from a key, so that Class 2 '
    'is all pattern and pitch. Check each hum against the take log before they go.</p></div>'
    '<div class="box"><span class="k">With two or four periods</span><p style="margin:0;font-size:10.6pt"><b>Two classes:</b> Class 1 is the plan, the hum, the slices and the pattern; '
    'Class 2 is the pitch, the groove, the arrangement, the mix and short presentations. <b>Four classes:</b> keep Classes 1 and 2, then spend Class 3 on the groove, the bass and the arrangement, and '
    'Class 4 on the mix, presentations and reflection.</p></div></div>')
PACING_SIZE = 10.6
TN2_SIZE = 9.9

SONG_NOTE = ("No audio, recordings, lyrics or melodies are included, and no songs, artists or albums are named. Students make every "
             "sound themselves: their own hummed voice, and drums and a bass from the sounds in Logic.")
VOICE_NOTE = ("Students record their OWN voice. They do not sample songs, videos, games or any commercial recording, and they do not use a classmate’s voice without that classmate’s permission. "
              "A student who prefers not to be recorded can ask a willing classmate to hum, with permission.")
CREDITS = ["The timing page, the slice map, the step grids, the pitch table, the checklists and the worked example: original work, Hudson Beat. "
           "No melodies, lyrics, recordings or published editions are included.",
           "The cover illustration was made with digital and AI tools. No audio, video, album art, screenshots, presets, templates, links or "
           "chart data from other sources are included. No student work is included. The recording and level guidance is general practice, "
           "given as starting points to set by ear."]
LOGIC_INTRO = ("Where to find the tools a Winter Vocal Chop is likely to use. Demonstrate what your class needs on Classes 1 and 2 and then "
               "let students work. Names are from current Logic Pro versions; labels move between versions, so check yours.")
LOGIC_REF = [("Project and tempo", "File › New…, then an Audio track to record the hum. Set the project tempo in the control bar to the BPM on your timing page and keep the time signature at 4/4. "
              "Set the snap or grid value to 16th notes (if your version shows one) so that every hit lands on a step."),
             ("Record the hum", "On the Audio track, choose the microphone or interface as the input and click the record-enable button (R). Watch the track’s level meter while you hum your loudest moment: "
              "set the gain on the interface, not the fader, so the peaks stay well below 0 dBFS, around −12 to −6 as a starting point. Re-record a take that clips."),
             ("Load it in Quick Sampler", "Add a Software Instrument track and choose Quick Sampler (if your version has it). Drop your hum’s audio region onto the Quick Sampler window, or use Logic’s command that converts an audio "
              "region to a sampler instrument (if your version has it; the Logic Pro User Guide describes it). Trim the start and end markers to the hum."),
             ("Slice mode", "In the Quick Sampler window, look for a Slice mode (if your version has it). It can place slice markers at transients, in equal divisions or by hand (manual), and it may offer a "
              "way to set how many slices (for transients, a sensitivity control). Choose 8 or 16, then listen and move any marker that cuts a sound in half."),
             ("Slices on keys", "Slices usually play from neighboring keys in order, starting from a key you can see in the plug-in. Play each key and write down which slice it plays and where slice 1 starts. "
              "The note names and octave numbers differ between versions, so label your own start key."),
             ("Play the pattern", "Record the pattern from a keyboard or pads, or draw notes in the Piano Roll with the grid set to 16th notes, 16 steps to a bar, for 4 bars. Quantize to 16th notes if hits are late. "
              "The Step Sequencer (if your version has one) can also play a pattern on a grid."),
             ("Pitch and reverse", "Pitch a slice by playing a different key, by transposing its notes by semitones in the Piano Roll, or with a tune or pitch control in Quick Sampler (if your version has one); these use "
              "semitones. Look for a reverse option in the Quick Sampler window (if your version has it). Flex Time and similar tools (if your version has them) can stretch audio without changing its pitch."),
             ("Drums and bass", "Add a drum part with a Session Player such as the Drummer, or a Drum Machine Designer kit, or a loop from the Loop Browser (each if your version has it), and play the groove on page " + str(pg("drums")) + ". "
              "For the bass, choose a bass sound from the Software Instrument library and play one low note per bar."),
             ("Mixer and bounce", "Press X for the Mixer and set levels and pan. Keep the master peak below 0 dBFS with room to spare. Then File › Bounce › Project or Section (Command-B), MP3 or WAV, for the whole hook. "
              "In Finder, Control-click the .logicx and choose Compress.")]
PRESENT_CHECK = [f"Files named {FILE_NAME}; the .mp3 or .wav and the zipped .logicx handed in",
                 "Reflection page done (page @REFLECT)", "Three questions for classmates written",
                 "Rubric self-score done (page @RUBRIC)"]
VOCAB_PROMPT = "Where it shows up in my hook:"
TN1_EXTRA = (
    '<div class="box acc-b" style="margin-top:4pt"><span class="k">Where this kit helps with each struggle</span><ul style="margin:0">'
    '<li style="font-size:12pt;margin-bottom:3pt">Slices that click: the slice map page (page @SLICEMAP) shows the lines on a waveform and explains transient, equal and manual slices.</li>'
    '<li style="font-size:12pt;margin-bottom:3pt">Hits that feel off the beat: the timing page (page @TIMING) gives the length of a step at six tempos, and the step grid (page @PATTERN) shows every hit.</li>'
    '<li style="font-size:12pt;margin-bottom:3pt">Pitch: the pitch table (page @PITCH) gives each semitone offset with its ratio, and the worked example (pages @EXAMPLE–@EXAMPLE2) shows a full set of choices.</li>'
    '<li style="font-size:12pt;margin-bottom:0">A crowded hook: the arrangement page (page @ARRANGE) shows which of five layers plays in each bar.</li></ul></div>')
TN1_SIZE = 12.0
PROJ_SIZE = 11.2
VOCAB_GAP = 5
LOGIC_SIZE = 9.4
PROJ1_EXTRA = ""
RUBRIC_EXTRA = ""

# ================================================================ the worked example: an invented hook at 120 BPM
EX_BAR_S = bar_len(EX_BPM)                  # 2 s
EX_STEP_S = step_len(EX_BPM)                # 0.125 s
EX_SLICE_S = slice_len(PHRASE, NSLICE)      # 0.375 s
EX_WEAK = "I will hum something and chop it up and add drums, and it will sound cool."
EX_STRONG = ("My hook is at 120 BPM in 4/4. One bar lasts 240 ÷ 120 = 2 seconds and one 16th-note step lasts 15 ÷ 120 = 0.125 seconds. My hum is 3 seconds long, so 8 equal slices are 3 ÷ 8 = 0.375 seconds each, "
             "which is exactly 3 steps. My 4-bar chop pattern uses all 8 slices and has 6, 6, 6 and 8 hits, 26 in all, and lasts 4 × 2 = 8 seconds. I pitch slice 1 up 12 semitones (× 2.000), slice 3 up 7 (× 1.498) "
             "and slice 5 down 5 (× 0.749). My arrangement is 16 bars = 32 seconds: an intro in bars 1 to 4, the hook in bars 5 to 8, the drop in bars 9 to 12 and an outro in bars 13 to 16.")
EX_QUESTIONS = ["Which slice did you hear most often, and did you notice when it changed?",
                "Could you tell the pitched chops from the plain ones?",
                "Did the drop feel different from the hook, and why?"]
EX_NOTE = ("the hum is a gentle rising phrase inspired by wind at a window; the pattern repeats slice 1 on the first step of bars 1, 2 and 4; "
           "the reversed slice at the end of bars 4, 8 and 12 points into the next section")


# ================================================================ drawings (all in code, labels logged for the fit check)
def padded(body, W, H, M=10):
    """Wrap a drawing's body with M units of clear padding on all four sides (wider than the thickest outer stroke), so no edge pixel is ever inked."""
    return f'<g transform="translate({M},{M})">{body}</g>', W + 2 * M, H + 2 * M


def hum_amp(t, L=3.0):
    """The look of a hummed phrase: a soft rise, a slight breath dip near the middle and a fade, with a gentle wobble. A drawing, not data."""
    env = (0.22 + 0.78 * math.sin(math.pi * t / L) ** 1.3)
    dip = 1 - 0.55 * math.exp(-((t - 1.52) / 0.07) ** 2)
    wob = 0.82 + 0.18 * math.sin(2 * math.pi * t * 3.4)
    return max(0.06, env * dip * wob)


def slices_body(W=1600, name="slices"):
    """A 3-second hum drawn as a waveform with 7 slice lines between the start and the end: 8 equal slices of 0.375 s, numbered, with their start times."""
    gx, pw = 30, W - 60
    sw = pw / NSLICE
    top, bot = 66, 290
    cy = (top + bot) / 2
    out = []
    for i in range(NSLICE):
        out.append(f'<rect x="{gx + i * sw:.1f}" y="{top}" width="{sw:.1f}" height="{bot - top}" fill="{ACC_LIGHT if i % 2 == 0 else "#fff"}" stroke="none"/>')
    n = 150
    for k in range(n):
        t = (k + 0.5) / n * float(PHRASE)
        h = hum_amp(t) * (bot - top) / 2 * 0.92
        x = gx + (k + 0.5) / n * pw
        out.append(f'<rect x="{x - 3.2:.1f}" y="{cy - h:.1f}" width="6.4" height="{2 * h:.1f}" rx="3" fill="#000"/>')
    out.append(f'<line x1="{gx}" y1="{cy}" x2="{gx + pw}" y2="{cy}" stroke="#000" stroke-width="1.5" opacity="0.45"/>')
    out.append(f'<rect x="{gx}" y="{top}" width="{pw}" height="{bot - top}" fill="none" stroke="#000" stroke-width="4"/>')
    for i in range(1, NSLICE):
        out.append(f'<line class="marker" x1="{gx + i * sw:.1f}" y1="{top - 14}" x2="{gx + i * sw:.1f}" y2="{bot + 14}" stroke="{ACCENT}" stroke-width="5" stroke-dasharray="14 8"/>')
    for i in range(NSLICE):
        cx = gx + (i + 0.5) * sw
        out.append(f'<circle cx="{cx:.1f}" cy="32" r="21" fill="#000"/>')
        out.append(D.t_(cx, 41, str(i + 1), 28, 700, fill_="#fff"))
        lbl = exact(i * slice_len(PHRASE, NSLICE))
        x0 = gx + i * sw
        out.append(D.t_(x0, bot + 54, lbl, 24, 700, anchor="start" if i == 0 else "middle"))
        D.lab(name + " times", lbl, 24, sw - 20)
    out.append(D.t_(gx + pw, bot + 54, exact(PHRASE), 24, 700, anchor="end"))
    out.append(D.t_(gx + pw / 2, bot + 98, "seconds from the start of the hum", 22, 500, "Source Sans 3", fill_="#222"))
    D.lab(name + " cap", "seconds from the start of the hum", 22, pw)
    cap = f"A {exact(PHRASE)}-second hum cut into {NSLICE} equal slices: {exact(PHRASE)} ÷ {NSLICE} = {exact(EX_SLICE_S)} seconds each."
    out.append(D.t_(gx + pw / 2, bot + 140, cap, 25, 700, "Source Sans 3"))
    D.lab(name + " cap", cap, 25, pw)
    return padded("".join(out), W, bot + 156, 16)


WHITE_PCS = (0, 2, 4, 5, 7, 9, 11)
NOTE_NAMES = {0: "C", 2: "D", 4: "E", 5: "F", 7: "G", 9: "A", 11: "B"}


def key_geom(semi, ww, x0):
    """(is_black, centre x, width) of the key `semi` semitones above a C, on a keyboard whose white keys are ww wide and start at x0."""
    o, r = divmod(semi, 12)
    if r in WHITE_PCS:
        return False, x0 + (o * 7 + WHITE_PCS.index(r) + 0.5) * ww, ww
    left = o * 7 + WHITE_PCS.index(r - 1) + 1
    return True, x0 + left * ww, ww * 0.62


def keys_body(W=1500, name="keys"):
    """One octave of keys (C to the next C, 13 keys): slices 1 to 8 on the first 8 neighboring keys, with the note letters of the white keys."""
    nkeys = 13
    ww = (W - 60) / 8
    x0 = 30
    top, wh, bh = 92, 250, 156
    out = []
    # white keys first, then black keys on top
    for s in range(nkeys):
        blk, cx, w = key_geom(s, ww, x0)
        if not blk:
            used = s < NSLICE
            out.append(f'<rect x="{cx - w / 2:.1f}" y="{top}" width="{w:.1f}" height="{wh}" fill="{ACC_LIGHT if used else "#fff"}" stroke="#000" stroke-width="4"/>')
    for s in range(nkeys):
        blk, cx, w = key_geom(s, ww, x0)
        if blk:
            used = s < NSLICE
            out.append(f'<rect x="{cx - w / 2:.1f}" y="{top}" width="{w:.1f}" height="{bh}" rx="5" fill="{ACCENT if used else "#222"}" stroke="#000" stroke-width="4"/>')
    for s in range(NSLICE):
        blk, cx, w = key_geom(s, ww, x0)
        if blk:
            out.append(f'<circle class="slicekey" cx="{cx:.1f}" cy="{top + bh - 36}" r="21" fill="#fff" stroke="#000" stroke-width="3"/>')
            out.append(D.t_(cx, top + bh - 27, str(s + 1), 26, 700))
        else:
            out.append(f'<circle class="slicekey" cx="{cx:.1f}" cy="{top + wh - 40}" r="23" fill="#000"/>')
            out.append(D.t_(cx, top + wh - 30, str(s + 1), 28, 700, fill_="#fff"))
    for s in range(nkeys):
        blk, cx, w = key_geom(s, ww, x0)
        if not blk:
            out.append(D.t_(cx, top + wh + 42, NOTE_NAMES[s % 12], 32, 700))
    # a bracket over the first 8 keys
    xa = key_geom(0, ww, x0)[1] - ww / 2 + 6
    xb = key_geom(NSLICE - 1, ww, x0)[1] + key_geom(NSLICE - 1, ww, x0)[2] / 2 - 6
    out.append(f'<polyline points="{xa:.1f},{top - 12} {xa:.1f},{top - 28} {xb:.1f},{top - 28} {xb:.1f},{top - 12}" fill="none" stroke="{ACCENT}" stroke-width="5" stroke-linejoin="round"/>')
    lab1 = f"slices 1 to {NSLICE}, one per neighboring key"
    out.append(D.t_((xa + xb) / 2, top - 40, lab1, 30, 700, fill_=ACCENT))
    D.lab(name + " top", lab1, 30, xb - xa)
    cap = "Your start key may be different. Play each key and write down which slice it plays."
    out.append(D.t_(W / 2, top + wh + 92, cap, 26, 500, "Source Sans 3"))
    D.lab(name + " cap", cap, 26, W - 40)
    return padded("".join(out), W, top + wh + 108, 16)


def grid_body(W=1600, name="grid", pattern=PATTERN, blank=False):
    """The 4-bar chop pattern on a step grid: 8 slice lanes by 64 steps (4 bars of 16 steps). Hit cells carry class="hit", every cell class="cell"."""
    bars = len(pattern)
    gx = 150
    pw = W - gx - 34
    cw = pw / (bars * STEPS_BAR)
    ch = 34
    top = 92
    lanes = NSLICE
    bot = top + lanes * ch
    out = []
    for b in range(bars):
        for s in range(STEPS_BAR):
            for ln in range(lanes):
                out.append(f'<rect class="cell" x="{gx + (b * STEPS_BAR + s) * cw:.1f}" y="{top + ln * ch}" width="{cw:.1f}" height="{ch}" fill="{"#f4f4f4" if (s // 4) % 2 == 0 else "#fff"}" '
                           f'stroke="#bbb" stroke-width="1.5"/>')
    for ln in range(lanes):
        out.append(D.t_(gx - 14, top + ln * ch + 25, f"SLICE {ln + 1}", 21, 700, anchor="end"))
    D.lab(name + " lanes", "SLICE 8", 21, gx - 20)
    for b in range(bars):
        for s in range(STEPS_BAR):
            if blank:
                continue
        if not blank:
            for st, sl in pattern[b]:
                x = gx + (b * STEPS_BAR + st - 1) * cw
                out.append(f'<rect class="hit" x="{x + 3:.1f}" y="{top + (sl - 1) * ch + 4}" width="{cw - 6:.1f}" height="{ch - 8}" rx="4" fill="{ACCENT}" stroke="#000" stroke-width="2.5"/>')
    for k in range(bars * 4 + 1):
        x = gx + k * 4 * cw
        out.append(f'<line x1="{x:.1f}" y1="{top}" x2="{x:.1f}" y2="{bot}" stroke="{"#000" if k % 4 == 0 else "#777"}" stroke-width="{4 if k % 4 == 0 else 2}"/>')
    out.append(f'<rect x="{gx}" y="{top}" width="{pw}" height="{bot - top}" fill="none" stroke="#000" stroke-width="4"/>')
    for b in range(bars):
        x0 = gx + b * STEPS_BAR * cw
        out.append(D.t_(x0 + 10, 36, f"BAR {b + 1}", 24, 700, anchor="start", fill_=ACCENT))
        for beat in range(BEATS_BAR):
            out.append(D.t_(x0 + (beat * 4 + 2) * cw, 74, str(beat + 1), 20, 500, "Source Sans 3", fill_="#222"))
        lbl = "hits: ______" if blank else f"{PAT_HITS[b]} hits"
        out.append(D.t_(x0 + STEPS_BAR * cw / 2, bot + 38, lbl, 24, 700))
        D.lab(name + " hits", lbl, 24, STEPS_BAR * cw - 20)
    out.append(D.t_(gx - 14, 74, "BEAT", 20, 700, anchor="end", fill_=ACCENT))
    cap = (f"{bars} bars of {STEPS_BAR} steps = {bars * STEPS_BAR} steps. Each beat is 4 steps. " + ("Draw a hit in the lane of the slice you play." if blank else f"{sum(PAT_HITS)} hits in all."))
    out.append(D.t_(gx + pw / 2, bot + 82, cap, 23, 500, "Source Sans 3"))
    D.lab(name + " cap", cap, 23, pw)
    return padded("".join(out), W, bot + 98, 16)


def drum_body(W=1400, name="drums", blank=False):
    """One bar of drum groove on 16 steps: kick, snare and hat lanes, each lane labelled with its number of hits."""
    gx = 230
    pw = W - gx - 34
    cw = pw / STEPS_BAR
    ch = 56
    top = 92
    bot = top + len(DRUMS) * ch
    out = []
    for ln, (nm, hits) in enumerate(DRUMS):
        for s in range(STEPS_BAR):
            out.append(f'<rect class="cell" x="{gx + s * cw:.1f}" y="{top + ln * ch}" width="{cw:.1f}" height="{ch}" fill="{"#f4f4f4" if (s // 4) % 2 == 0 else "#fff"}" stroke="#bbb" stroke-width="1.5"/>')
        for st in ([] if blank else hits):
            cx, cy = gx + (st - 0.5) * cw, top + ln * ch + ch / 2
            out.append(f'<circle class="dhit" cx="{cx:.1f}" cy="{cy:.1f}" r="{(ch - 20) / 2:.1f}" fill="{ACCENT}" stroke="#000" stroke-width="3"/>')
        lbl = nm if blank else f"{nm} · {len(hits)}"
        out.append(D.t_(gx - 14, top + ln * ch + ch / 2 + 9, lbl, 26, 700, anchor="end"))
        D.lab(name + " lanes", lbl, 26, gx - 24)
    for k in range(5):
        x = gx + k * 4 * cw
        out.append(f'<line x1="{x:.1f}" y1="{top}" x2="{x:.1f}" y2="{bot}" stroke="{"#000" if k in (0, 4) else "#777"}" stroke-width="{4 if k in (0, 4) else 2}"/>')
    out.append(f'<rect x="{gx}" y="{top}" width="{pw}" height="{bot - top}" fill="none" stroke="#000" stroke-width="4"/>')
    for s in range(STEPS_BAR):
        out.append(D.t_(gx + (s + 0.5) * cw, 74, str(s + 1), 20, 500, "Source Sans 3", fill_="#222"))
    out.append(D.t_(gx - 14, 74, "GRID STEP", 20, 700, anchor="end", fill_=ACCENT))
    total = sum(len(h) for _, h in DRUMS)
    cap = ("One bar of 16 steps. Draw a dot where each drum plays." if blank else f"One bar of 16 steps. The number after each name is its hits per bar: {total} hits in all.")
    out.append(D.t_(gx + pw / 2, bot + 44, cap, 23, 500, "Source Sans 3"))
    D.lab(name + " cap", cap, 23, pw)
    return padded("".join(out), W, bot + 60, 16)


def arr_body(W=1600, name="arrange"):
    """The 16-bar arrangement at 120 BPM: four sections of 4 bars, five layers, bars along the top and seconds along the bottom."""
    gx = 190
    pw = W - gx - 34
    bw = pw / ARR_BARS
    rh, gap = 54, 10
    top = 126
    out = []
    for nm, a, b in ARR_SECTIONS:
        x0 = gx + (a - 1) * bw
        out.append(f'<rect x="{x0 + 2:.1f}" y="12" width="{(b - a + 1) * bw - 4:.1f}" height="44" rx="8" fill="{ACCENT if nm in ("HOOK", "DROP") else "#000"}"/>')
        lbl = f"{nm} · bars {a}–{b}"
        out.append(D.t_(x0 + (b - a + 1) * bw / 2, 44, lbl, 24, 700, fill_="#fff"))
        D.lab(name + " sections", lbl, 24, (b - a + 1) * bw - 16)
    for b in range(ARR_BARS):
        out.append(D.t_(gx + (b + 0.5) * bw, 94, str(b + 1), 24, 700))
    out.append(D.t_(gx - 14, 94, "BAR", 22, 700, anchor="end", fill_=ACCENT))
    for r, (nm, spans) in enumerate(ARR_ROWS):
        y = top + r * (rh + gap)
        out.append(f'<rect x="{gx}" y="{y}" width="{pw}" height="{rh}" fill="#fff" stroke="#bbb" stroke-width="2"/>')
        out.append(D.t_(gx - 14, y + rh / 2 + 9, nm, 24, 700, anchor="end"))
        D.lab(name + " rows", nm, 24, gx - 24)
        for a, b in spans:
            fillc = {"CHOPS": ACCENT, "PITCHED": ACC_LIGHT, "REVERSE": "#fff", "DRUMS": "#d9d9d9", "BASS": "#555"}[nm]
            out.append(f'<rect class="block" x="{gx + (a - 1) * bw + 3:.1f}" y="{y + 5}" width="{(b - a + 1) * bw - 6:.1f}" height="{rh - 10}" rx="7" fill="{fillc}" stroke="#000" stroke-width="3"/>')
    bot = top + len(ARR_ROWS) * (rh + gap) - gap
    for k in range(ARR_BARS // 4 + 1):
        x = gx + k * 4 * bw
        out.append(f'<line x1="{x:.1f}" y1="{top - 8}" x2="{x:.1f}" y2="{bot + 12}" stroke="#000" stroke-width="3" stroke-dasharray="9 7"/>')
        s = hit_time(EX_BPM, 4 * k + 1, 1)
        out.append(D.t_(x, bot + 44, fmt(s), 24, 700, anchor="start" if k == 0 else ("end" if k == ARR_BARS // 4 else "middle")))
    out.append(D.t_(gx - 14, bot + 44, "SECONDS", 22, 700, anchor="end", fill_=ACCENT))
    D.lab(name + " rows", "SECONDS", 22, gx - 24)
    cap = f"{ARR_BARS} bars at {EX_BPM} BPM = {fmt(ARR_BARS * EX_BAR_S)} seconds, with {len(ARR_ROWS)} layers. A reversed chop ends each section."
    out.append(D.t_(gx + pw / 2, bot + 92, cap, 24, 700, "Source Sans 3"))
    D.lab(name + " cap", cap, 24, pw)
    return padded("".join(out), W, bot + 110, 16)


def pitch_body(W=1560, name="pitch"):
    """Two octaves of keys, 25 keys from -12 to +12 semitones around a root C, with the semitone count on every key and the ratio 2^(n/12) at the keys the table uses most."""
    ww = (W - 80) / 15
    x0 = 40
    top, wh, bh = 120, 230, 140
    out = []
    marks = {0: -12, 7: -5, 12: 0, 19: 7, 24: 12}                # key index -> semitone offset
    for s in range(25):
        blk, cx, w = key_geom(s, ww, x0)
        if not blk:
            fl = ACCENT if s == 12 else (ACC_LIGHT if s in marks else "#fff")
            out.append(f'<rect x="{cx - w / 2:.1f}" y="{top}" width="{w:.1f}" height="{wh}" fill="{fl}" stroke="#000" stroke-width="3.5"/>')
    for s in range(25):
        blk, cx, w = key_geom(s, ww, x0)
        if blk:
            fl = ACCENT if s == 12 else ("#777" if s in marks else "#222")
            out.append(f'<rect x="{cx - w / 2:.1f}" y="{top}" width="{w:.1f}" height="{bh}" rx="5" fill="{fl}" stroke="#000" stroke-width="3.5"/>')
    for s in range(25):
        blk, cx, w = key_geom(s, ww, x0)
        n = s - 12
        lbl = sgn(n)
        if blk:
            out.append(D.t_(cx, top + bh - 14, lbl, 17, 700, fill_="#fff"))
        else:
            out.append(D.t_(cx, top + wh - 16, lbl, 20, 700, fill_="#fff" if s == 12 else "#000"))
    D.lab(name + " keynums", "−12", 20, ww - 4)
    for s, n in marks.items():
        blk, cx, w = key_geom(s, ww, x0)
        lbl = ("ROOT · × 1" if n == 0 else f"{sgn(n)} · × {r3(ratio(n))}")
        D.lab(name + " marks", lbl, 24, 250)
        if n > 0:
            ty, y1, y2 = 62, 74, top - 4
        else:
            ty, y1, y2 = top + wh + 56, top + wh + 6, top + wh + 24
        out.append(f'<line x1="{cx:.1f}" y1="{y1}" x2="{cx:.1f}" y2="{y2}" stroke="#000" stroke-width="3"/>')
        wtxt = D.text_w(lbl, 24)
        anc, tx = "middle", cx
        if cx + wtxt / 2 > W - 14:
            anc, tx = "end", W - 14
        if cx - wtxt / 2 < 14:
            anc, tx = "start", 14
        out.append(D.t_(tx, ty, lbl, 24, 700, anchor=anc, fill_=ACCENT if n == 0 else "#000"))
        D.span(name, "bottom" if n <= 0 else "top", lbl, 24, tx, anchor=anc, lo=0, hi=W)
    cap = "Every key is one semitone. 12 semitones = an octave = × 2.000. Ratio = 2^(n ÷ 12)."
    out.append(D.t_(W / 2, top + wh + 112, cap, 24, 700, "Source Sans 3"))
    D.lab(name + " cap", cap, 24, W - 40)
    return padded("".join(out), W, top + wh + 128, 16)


def hero_body():
    """The owner's pre-made art (art/hero.png, used whole). The viewBox only trims fully transparent margin: the art's own pixels
    (x 95-1310, y 134-1252 of 1400) stay at least 40 units inside it, which --check proves from the file."""
    return (f'<image href="../art/hero.png" x="{-HX}" y="{-HY}" width="1400" height="1400"/>', HW, HH)


HX, HY, HW, HH = 50, 90, 1310, 1220

DRAWINGS = {"hero": hero_body, "slices": lambda: slices_body(1600, "slices deck"), "keys": lambda: keys_body(1500, "keys deck"),
            "grid": lambda: grid_body(1600, "grid deck"), "pitch": lambda: pitch_body(1560, "pitch deck"), "arrange": lambda: arr_body(1600, "arrange deck")}
DRAWING_PX = {"hero": 1340, "slices": 2000, "keys": 1800, "grid": 2000, "pitch": 2000, "arrange": 2000}
SIDE = {"slices": ["8 equal slices of 0.375 s", "Equal slices: lines the same distance apart"],
        "keys": ["One slice on each neighboring key", "Label your own start key"],
        "grid": ["16 steps in a bar, 4 beats of 4 steps", "Hits per bar: 6, 6, 6 and 8"],
        "pitch": ["+12 is an octave up: × 2.000", "+7 is a fifth up: × 1.498"],
        "arrange": ["Intro, hook, drop and outro", "16 bars at 120 BPM are 32 seconds"]}
# extra drawings used on pages only, rendered alone on a transparent ground by --check as well
PAGE_DRAWINGS = {"slices-page": lambda: slices_body(1600, "slices page"), "keys-page": lambda: keys_body(1500, "keys page"), "grid-page": lambda: grid_body(1600, "grid page"),
                 "grid-blank-page": lambda: grid_body(1600, "grid blank page", blank=True), "drums-page": lambda: drum_body(1400, "drums page"), "drums-blank-page": lambda: drum_body(1400, "drums blank page", blank=True),
                 "pitch-page": lambda: pitch_body(1560, "pitch page"), "arrange-page": lambda: arr_body(1600, "arrange page")}


def label_extras():
    for k, fn in PAGE_DRAWINGS.items():
        fn()


# ================================================================ intro deck: (class, kind, title, body, speaker notes)
SLIDES = [
    (1, "title", "Winter Vocal Chop", "Hum it. Slice it. Play it.",
     "Class 1, the first minute. No audio is included in this deck. Open with the idea: you will record one short hum of your own voice, cut it into slices in Quick Sampler (if your version has it), "
     "play the slices in a pattern, change some pitches and build a hook with drums and a bass. Nobody needs to read music, and no existing song or recording is used."),
    (1, "listen", "Hear the hook", "Think, then share|Teacher: read aloud, no audio plays. Wind at the window, boots on snow, a kettle starting to sing. "
     "Hum one phrase to match, then imagine it cut into eight pieces.|What winter sound would you hum?|What happens if the pieces play in a different order?|"
     "Which piece would you play the most?",
     "Read the scene aloud slowly and ask the three questions. Take a few answers. Nothing is played from a speaker. Students will name a wind sound, a footstep sound or a kettle, and some will hum a rising or falling "
     "line. Write their words on the board. The project turns each idea into a tool with a number attached: a tempo, a slice length, a step on a grid, a semitone and a section."),
    (1, "bullets", "What is the Winter Vocal Chop project?", "Hum one short phrase in your own voice|Slice it into 8 pieces and put them on keys|Play the pieces in a 4-bar chop pattern|"
     "Pitch, reverse, add drums and bass, then build a hook",
     "The project in four lines. Every student records one hum of 2 to 4 seconds, with no words and no existing melody, and builds a hook in Logic Pro. The hum is sliced into 8 or 16 pieces, the pieces are played "
     "on a 16-step grid for 4 bars, some are pitched by semitones, and a drum groove and bass turn the pattern into an 8- or 16-bar arrangement. No audio ships: students make every sound."),
    (1, "days", "Three classes", "",
     "The shape of the project. Class 1: hook, the timing math, the recording and the slices. Class 2: finish the slices, play the 4-bar pattern and pitch some slices. Class 3: groove, bass, arrangement, mix, "
     "bounce, present and reflect. The badge on this slide reads Classes 1 to 3 because it covers all three. With two classes, do the plan, hum, slices and pattern in Class 1 and the rest in Class 2; with four, "
     "add a day for the mix and presentations. Hand out the timing page, the recording page and the slice map now."),
    (1, "pic", "One hum, eight slices", "slices",
     f"Class 1. This is a 3-second hum drawn as a waveform with 7 slice lines between its start and end, which makes 8 equal slices. Each slice is 3 ÷ 8 = 0.375 seconds long, so the lines are at 0.375, 0.75, 1.125 and so on. "
     f"Equal slices are the easiest to plan; transient slicing would put the lines at the start of each sound instead. Ask students where they would put a line in their own hum. The slice map is on page {pg('slicemap')} "
     f"and the recording page is page {pg('record')}."),
    (1, "bullets", "The math: one step = 15 ÷ BPM", "One bar of 4/4 lasts 240 ÷ BPM seconds|One 16th-note step lasts 15 ÷ BPM seconds|At 120 BPM, one step is 0.125 seconds|Slice length = hum length ÷ slices",
     f"Class 1, the key idea. In 4/4 there are four beats in a bar and each beat holds four 16th-note steps, so a bar has 16 steps. One bar lasts 240 divided by the tempo, and one step lasts 15 divided by the tempo: at 120 BPM that is "
     f"0.125 seconds. A hum of L seconds cut into 8 equal slices gives slices of L divided by 8, so a 3-second hum gives 0.375 seconds, which is exactly 3 steps at 120 BPM. The slice length does not depend on the tempo; "
     f"the tempo only decides how many steps a slice covers. The timing page is page {pg('timing')}."),
    (1, "pic", "Slices on the keys", "keys",
     f"Class 1. In Quick Sampler's slice mode (if your version has it) the slices are usually played from neighboring keys in order. Here slices 1 to 8 sit on the first 8 keys of an octave, white and black. "
     f"Your version may start on a different key, so students play each key, listen and write down which slice it plays. A slice that plays on the wrong key is a labeling problem, not a mistake in the hum. "
     f"The slice map with the key column is on page {pg('slicemap')}, and the quick reference is page {pg('logicref')}."),
    (1, "check", "Record the hum", "Quiet room with soft surfaces|The same distance from the mic every take|Peaks around −12 to −6 dBFS|One phrase of 2 to 4 seconds|"
     "No words and no existing melody|Your own voice only",
     f"Class 1. The recording checklist, shortened to fit the slide. Every student records their own voice: no samples of songs, videos or games. Peaks around −12 to −6 dBFS are a common beginner range and a starting point; "
     f"a quieter recording is safe and a clipped one has to be recorded again. Students should try two distances from the microphone and listen. The full checklist, the copyright note and a take log are on page {pg('record')}."),
    (2, "steps", "Chop it in Quick Sampler", "Load your hum in the Quick Sampler window|Look for the slice mode, if your version has it|Choose 8 slices: transient, equal or manual|Play each key and check its slice|Save the project",
     f"Class 2. Demonstrate on the projector. Add a Software Instrument track with Quick Sampler (if your version has it), drop the hum onto the Quick Sampler window and look for a slice mode. Describe the controls generically: "
     f"there is a way to choose how the markers are placed (at transients, in equal divisions or by hand) and, where offered, a way to set how many slices (for transients, a sensitivity control). Menu names and button places move between Logic versions; the quick reference on "
     f"page {pg('logicref')} hedges where they do. Students finish the slice map on page {pg('slicemap')}. The groove, the bass and the arrangement wait for Class 3."),
    (2, "pic", "The 4-bar chop pattern", "grid",
     f"Class 2. The model pattern on a step grid: 8 lanes, one for each slice, and 64 steps, which is 4 bars of 16. Each beat is 4 steps. The hits per bar are 6, 6, 6 and 8, 26 in all, and every slice is used. "
     f"At 120 BPM a step lasts 0.125 seconds, so bar 2, grid step 4 is slice 2 at (16 + 3) × 0.125 = 2.375 seconds. Students play their own pattern and draw it on the blank grid on page {pg('pattern')}. "
     f"Ask which hit they would move, and which step it would move to."),
    (2, "pic", "Pitch by semitone", "pitch",
     f"Class 2. Each key is one semitone, and 12 semitones make an octave. The frequency ratio for n semitones is 2^(n ÷ 12): +12 is × 2.000, +7 is × 1.498 and −5 is × 0.749. Intervals add and ratios multiply, "
     f"so +7 and then +5 makes +12: 1.4983 × 1.3348 = 2.0000. In many samplers a higher pitch also plays the recording faster, so a 0.375-second slice at +12 lasts 0.1875 seconds; some versions have tools that keep the "
     f"length (if your version has them). Reverse is also worth trying. The pitch table is on page {pg('pitch')}."),
    (3, "bullets", "Groove and bass", "Drums: kick, snare and hat on the grid|One low bass note per bar|Add layers as the hook builds|Keep every chop clear",
     f"Class 3. A simple drum groove on 16 steps: the kick on grid steps 1, 9 and 11, the snare on grid steps 5 and 13 and the hat on every other step, which is 3, 2 and 8 hits per bar. The bass plays one low note per bar, here the root, the root, "
     f"a fourth below and a fifth below. Use a Session Player or a drum kit or a loop for the drums, each if your version has it. The groove and bass page is page {pg('drums')}. The test is simple: can you still hear the chops?"),
    (3, "pic", "Arrange the hook", "arrange",
     f"Class 3. A 16-bar arrangement at 120 BPM: an intro in bars 1 to 4, the hook in bars 5 to 8, the drop in bars 9 to 12 and the outro in bars 13 to 16. There are 5 layers: chops, pitched chops, reversed chops, drums and bass. "
     f"16 bars of 2 seconds are 32 seconds. A reversed chop ends each section and points into the next one. An 8-bar version halves every section. The arrangement page is page {pg('arrange')}."),
    (3, "check", "What you turn in", "Bounced .mp3 or .wav, 8 or 16 bars long|Zipped .logicx project|Named: Your Name – Chop|Timing page, slice map and step grid|Reflection page|Rubric self-score and three questions",
     "Class 3. The submission checklist, shortened to fit the slide. Show where students hand in. The file name is Your Name, then Chop. Check the length before students bounce: "
     "the bounce should run the whole arrangement, which is 8 or 16 bars at the student's own tempo, and the timing page shows how many seconds that is."),
    (3, "rubric", "How it’s scored", "",
     "The rubric: five categories, each scored 1 to 5, for a total out of 25. Students score themselves first; the final grade is the average of their score and yours. "
     "The slide reads the 5 column of each category aloud. Hand out the rubric page so students can self-score before they present."),
    (3, "bullets", "Presentation day", "Play your hook from the top|Point out the slices, the pitched chops and the sections|Your three questions for classmates|Answer at least 2 of each classmate’s questions",
     "Class 3, presentations. Each student plays the hook and points out the slices, the pitched chops, the reversed chop and the sections as they arrive, with their bar numbers. Students write three "
     "questions they want classmates to answer, and answer at least two of each classmate's. Ask the class which slice they heard most often and when they noticed the drop."),
    (3, "closer", "One last thing…", "Hum it clean.|Slice it with care.|Count the steps.|Then let the hook land.",
     "Close with the listening day: play a hook and ask the class whether they could tell it began as a hum. A chop pattern that nobody can place is a pattern that was well planned and well timed. "
     "Ask a few students which choice did the most for their hook. No audio is included in this resource; the sounds are the students' own."),
]
SHOTS1 = [("pacing", "Pacing guide", "3 class periods, slide by slide"), ("pattern", "Step grid", "4 bars, 16 steps, 8 slices"),
          ("pitch", "Pitch table", "Semitones and ratios")]
SHOTS2 = [1, 5, 7, 10, 11, 13]
SHOTS3 = [("timing", "Timing math"), ("record", "Recording"), ("slicemap", "Slice map"), ("pattern", "Step grid"), ("pitch", "Pitch table"), ("drums", "Groove and bass"),
          ("arrange", "Arrangement"), ("example", "Worked example")]
PREVIEW_PICKS = ["pacing", "slicemap", "pattern", "pitch"]

COVER_A = "Hum it, slice it, play it"
COVER_C = "Logic Pro · Quick Sampler · Slices · Pitch"
PDF_COVER = dict(a=26, b=42, c=15, art=5.0)
SQ_COVER = dict(a=36, b=140, c=27, art=420, gap=20)
SQ_B_LINES = ["Winter Vocal", "Chop"]
SQ_SUB = "3 class periods · one hum, 8 slices, a 4-bar pattern"
SQ_HEADS = {1: ("Ready to teach Monday", 76, "Pacing, step grid, pitch table and the /25 rubric in one PDF", 28),
            2: ("Intro deck included", 76, f"{len(SLIDES)} editable slides (.pptx + PDF) with speaker notes on every slide", 28),
            3: ("Everything inside", 72, "Timing math, slice map, step grids, pitch table and worked example", 28)}
SQ_BANDS = {1: "Hum <em>·</em> slices <em>·</em> step grid <em>·</em> pitch",
            2: "Slice map <em>·</em> pitch table <em>·</em> arrangement",
            3: f"{len(PLAN)} pages <em>·</em> US Letter PDF <em>·</em> no audio included"}


# ================================================================ small page helpers
CSS_CC = ("<style>table.cc td { text-align: center; padding: 2pt 3pt; font-size: 9.4pt; line-height: 1.15; } table.cc th { text-align: center; font-size: 9pt; } "
          "table.cc td.l { text-align: left; } table.cc tr.hi td { background: #eef5fb; }</style>")


def howto_page(n, wm=False):
    parts = [("Teacher pages", "howto", "example2", "How to use, overview, setup, pacing, teacher notes, Logic quick reference, worked example (2 pages)"),
             ("Student pages", "timing", "reflect", "Timing page, recording checklist, slice map, step grid, pitch table, groove and bass, arrangement, mix checklist, "
              "project sheet (3 pages), rubric, vocabulary, feedback planner, reflection page"),
             ("Intro deck (separate file)", None, None, f"{len(SLIDES)} slides, .pptx + PDF, speaker notes on every slide")]
    trs = "".join(f"<tr><td><b>{a}</b></td><td style='white-space:nowrap'>{('pages ' + str(D.IX(f)) + '–' + str(D.IX(l))) if f else 'deck'}</td>"
                  f"<td>{u}</td></tr>" for a, f, l, u in parts)
    inner = (f'<div class="cols"><div>'
             f'{D.H2("What this is", True)}'
             f'<p style="font-size:12pt;line-height:1.45">A {CLASSES}-class-period vocal chop project for high school music technology. Every '
             f'student records one short hum of their own voice, slices it into 8 or 16 pieces in Quick Sampler (if their version has it), plays the pieces in a 4-bar pattern on a 16-step grid, '
             f'pitches some by semitones and arranges a hook with drums and a bass. Students plan the timing with simple arithmetic, present the result and reflect on it. It is an original Hudson Beat project.</p>'
             f'{D.H2("Quick start")}<ol>'
             f'<li style="margin-bottom:5pt">Read the pacing guide (page {D.IX("pacing")}) and the teacher notes (pages {D.IX("tn1")}–{D.IX("tn2")}).</li>'
             f'<li style="margin-bottom:5pt">Look at the timing page, the slice map, the step grid and the pitch table (pages {D.IX("timing")}–{D.IX("pitch")}) and the setup (page {D.IX("setup")}).</li>'
             f'<li style="margin-bottom:5pt">Print the student pages (pages {D.IX("timing")}–{D.IX("reflect")}), one set per student.</li>'
             f'<li>Open the intro deck and read the speaker notes for Class 1.</li></ol>'
             f'{D.H2("The intro deck")}'
             f'<p>Every slide has a class: {D.deck_class_line()}. The slide about the three classes carries the badge for all three. Every slide has speaker notes.</p>'
             f'<p class="small">Fonts: the deck uses Oswald and Source Sans 3 (free on Google Fonts, built into Google Slides). If PowerPoint or '
             f'Keynote shows a different font, install the two fonts or present the PDF copy, which shows the intended look.</p>'
             f'</div><div>'
             f'{D.H2("What’s inside", True)}<table class="t"><tr><th>Part</th><th>Pages</th><th>Use</th></tr>{trs}</table>'
             f'<div class="box acc-b" style="margin-top:6pt"><span class="k">No audio included</span><p style="margin:0">{D.fill(SONG_NOTE)}</p></div>'
             f'{D.H2("Make it fit your class")}<ul>'
             f'<li><b>Easier or harder:</b> see the variations on page {D.IX("tn1")}.</li>'
             f'<li><b>Pace:</b> Class 1 plan, hum and slices; Class 2 pattern and pitch; Class 3 groove, arrangement and presentations (page {D.IX("pacing")}, which also shows two and four periods).</li>'
             f'<li><b>Grading:</b> the rubric, /{RUBRIC_TOTAL}, the average of the student’s and your score (page {D.IX("rubric")}).</li></ul>'
             f'<div class="box" style="margin-top:6pt"><span class="k">In one sentence</span><p style="margin:0;font-size:12pt">Students learn that '
             f'a hook made from a voice is planned: a tempo that sets the length of a step, slices of a known length, hits placed on a grid, pitches changed by exact semitones and sections that build.</p></div>'
             f'<p class="small" style="margin-top:6pt">Logic Pro is a product of Apple Inc. This resource is not affiliated with Apple.</p>'
             f'</div></div>')
    return D.page("How to use this resource", "START HERE", "Teacher", inner, n, key="howto")


def overview_page(n, wm=False):
    inner = (f'<div class="cols"><div>'
             f'<div class="box inv" style="margin-bottom:6pt"><span class="k">The project in one line</span><p style="margin:0;font-size:12pt">'
             f'<b>{TITLE}</b> · Hum, slices, pattern and hook · Logic Pro<br>One hum of your own voice, eight slices, a hook that comes from them.</p></div>'
             f'{D.H2("What students make")}'
             f'<p style="font-size:12.2pt;line-height:1.48">A hook of 8 or 16 bars, built in Logic Pro from one hummed phrase of 2 to 4 seconds. The hum is sliced into 8 or 16 pieces, each slice is put on a key, '
             f'and a 4-bar chop pattern plays them on a 16-step grid. Some slices are pitched by semitones and one is reversed, and a simple drum groove and bass turn the pattern into an arrangement with an intro, a hook, '
             f'a drop and an outro. Students hand in a bounced file and the zipped .logicx project, plus their plans and a reflection, '
             f'then play the hook and take questions.</p>'
             f'{D.H2("What this project reinforces")}<p style="font-size:12pt;line-height:1.5">{TN_REINFORCES}</p>'
             f'{D.H2("Standards")}<p style="font-size:11.4pt">Supports the National Core Arts Standards for Music (Music Technology, high school): generating '
             f'and developing ideas (MU:Cr1.1, MU:Cr2.1), presenting work (MU:Pr6.1) and responding to it (MU:Re7.2).</p>'
             f'</div><div>'
             f'{D.H2("Goals", True)}<ul>' + "".join(f"<li style='font-size:12pt;line-height:1.45'>{g}</li>" for g in GOALS) + '</ul>'
             f'{D.H2("About the theme")}<div class="box acc-b" style="padding:5pt 9pt"><p style="margin:0 0 3pt;font-size:10.2pt;line-height:1.36">{THEME}</p>'
             f'<p style="margin:0;font-size:10.2pt;line-height:1.36">{BUILD_NOTE}</p></div>'
             f'<div class="box" style="margin-top:6pt;padding:5pt 9pt"><span class="k">At a glance</span><p style="margin:0;font-size:10.2pt;line-height:1.38"><b>Grades</b> {GRADES_TEXT}, music technology or music production · '
             f'<b>Length</b> {CLASSES} class periods (two and four also shown) · <b>Software</b> Logic Pro · <b>You supply</b> Macs with Logic Pro, headphones, a microphone (or a quiet corner and a shared one) and a place to hand in files · '
             f'<b>Assessment</b> rubric, 5 categories scored 1–5, /{RUBRIC_TOTAL} (page {D.IX("rubric")})</p></div>'
             f'</div></div>')
    return D.page("Project overview", "OVERVIEW", "Vocal chop project", inner, n, key="overview")


def setup_page(n, wm=False):
    inner = (f'<style>.sb p, .sb li {{ font-size: 11.6pt; line-height: 1.44; margin-bottom: 5pt; }}</style><div class="cols"><div class="big sb">'
             f'{D.H2("You need", True)}<ul>'
             f'<li><b>A Mac with Logic Pro</b> for each student, and <b>headphones</b>.</li>'
             f'<li><b>A microphone</b>, shared if you must, and a pop filter if you have one. A quiet corner with soft surfaces beats a loud room. A laptop’s built-in microphone will do for practice.</li>'
             f'<li><b>A place to hand in</b> the .mp3 or .wav files, the zipped .logicx and the reflection.</li>'
             f'<li><b>The timing page, slice map, step grid and pitch table</b>, printed (pages {D.IX("timing")}–{D.IX("pitch")}), or shown on the projector.</li>'
             f'<li><b>Printed student pages</b>, one set each (pages {D.IX("timing")}–{D.IX("reflect")}).</li></ul>'
             f'{D.H2("Before Class 1")}'
             + "".join(D.chk(c, 13, "font-size:11.6pt;margin-bottom:7pt") for c in [
                 f"Read the timing page (page {D.IX('timing')}) so you can answer ‘how long is one step at 100 BPM?’ and ‘how long is a slice of a 3-second hum?’",
                 f"Test a microphone in Logic Pro on one computer, and hum into it while watching the meter (page {D.IX('record')}).",
                 f"Open Logic Pro on a student computer and check which tools your version has: Quick Sampler and its slice mode, the Piano Roll, a Drummer or drum kit (see page {D.IX('logicref')}).",
                 f"Read the worked example (pages {D.IX('example')}–{D.IX('example2')})."]) +
             f'</div><div class="big sb">'
             f'{D.H2("What to watch", True)}'
             f'<p style="font-size:11.4pt">Watch for a hum that clips or is much too quiet, a slice marker in the middle of a sound, hits that sit off the grid, and a hook so crowded that the chops disappear. {TN_NOTE}</p>'
             f'<div class="box acc-b" style="margin-top:2pt"><span class="k">Ideas for the room</span><ul style="margin:0">'
             f'<li style="font-size:11.2pt">Ask while students work: which step is this hit on? Which slice is this key?</li>'
             f'<li style="font-size:11.2pt">Use only the student’s own hum, plus the drums and bass sounds that come with Logic. No existing songs, videos or recordings.</li>'
             f'<li style="font-size:11.2pt">A student who is stuck can build one slice, one pitched copy of it and a drum groove: those already make a hook.</li></ul></div>'
             f'{D.H2("The voice and copyright")}'
             f'<div class="box"><p style="margin:0;font-size:10.8pt;line-height:1.4">{VOICE_NOTE}</p></div>'
             f'<div class="box" style="margin-top:6pt"><span class="k">Keep the volume moderate</span><p style="margin:0;font-size:11pt;line-height:1.4">'
             f'Students listen to a short sound over and over in headphones. Tell them to start low and check the final mix at a normal level.</p></div>'
             f'</div></div>')
    return D.page("Setup and what to watch", "SETUP", "Teacher", inner, n, key="setup")


# ================================================================ the student pages
def tempo_rows():
    rows = []
    for bpm in TEMPOS:
        hi = ' class="hi"' if bpm == EX_BPM else ''
        b, e = ("<b>", "</b>") if bpm == EX_BPM else ("", "")
        rows.append(f"<tr{hi}><td>{b}{bpm}{e}</td><td>{dec(spb(bpm), 3)}</td><td>{b}{dec(step_len(bpm), 4)}{e}</td><td>{dec(bar_len(bpm), 3)}</td>"
                    f"<td>{dec(PAT_BARS * bar_len(bpm), 3)}</td><td>{dec(ARR_BARS * bar_len(bpm), 3)}</td><td>{dec(slice_steps(PHRASE, NSLICE, bpm), 2)}</td></tr>")
    return "".join(rows)


def hum_rows():
    rows = []
    for L in PHRASES:
        rows.append(f"<tr><td><b>{exact(L)} s</b></td><td>{exact(slice_len(L, NSLICE))}</td><td>{exact(slice_len(L, NSLICE_ALT))}</td>"
                    f"<td>{dec(slice_steps(L, NSLICE, EX_BPM), 2)}</td><td>{dec(slice_steps(L, NSLICE_ALT, EX_BPM), 2)}</td></tr>")
    return "".join(rows)


def timing_page(n, wm=False):
    inner = (CSS_CC +
             f'<p style="margin:0 0 4pt;font-size:10.2pt;line-height:1.36">Step 1: plan the hook. In 4/4 there are 4 beats in a bar, and each beat holds four 16th-note steps, so a bar has 16 steps. '
             f'These formulas turn a tempo into seconds. Every number below is computed, so you can check your own arithmetic against it.</p>'
             f'<div class="cols" style="gap:10pt;align-items:flex-start"><div class="box acc-b" style="padding:5pt 9pt;flex:1.15"><span class="k">The formulas (4/4)</span>'
             f'<p style="margin:0 0 2pt;font-size:9.8pt"><b>Seconds per beat</b> = 60 ÷ BPM</p><p style="margin:0 0 2pt;font-size:9.8pt"><b>Seconds per 16th-note step</b> = 15 ÷ BPM</p>'
             f'<p style="margin:0 0 2pt;font-size:9.8pt"><b>Seconds per bar</b> = 240 ÷ BPM = 16 steps</p>'
             f'<p style="margin:0 0 2pt;font-size:9.8pt"><b>A hit on grid step s of bar b</b> is at ((b − 1) × 16 + (s − 1)) × 15 ÷ BPM seconds</p>'
             f'<p style="margin:0 0 2pt;font-size:9.8pt"><b>Slice length</b> = hum length ÷ number of slices</p>'
             f'<p style="margin:0;font-size:9.8pt"><b>Example:</b> 120 BPM: 15 ÷ 120 = 0.125 s per step, and 240 ÷ 120 = 2 s per bar.</p></div>'
             f'<div class="box" style="padding:5pt 9pt;flex:1"><span class="k">Rounding rules</span><p style="margin:0;font-size:9.2pt;line-height:1.32">Seconds per beat, bar and section to 3 decimals and seconds per step to 4; '
             f'a 5 rounds up. So 15 ÷ 128 = 0.1172 seconds (the exact value is 0.1171875). Slice lengths in the second table are exact.</p></div></div>'
             f'<span class="k" style="margin-top:5pt">How long is a step, a bar and a section?</span>'
             f'<table class="t cc" style="margin-top:1pt"><tr><th>BPM</th><th>Seconds per beat</th><th>Seconds per step</th><th>Seconds per bar</th><th>4-bar pattern (s)</th><th>16-bar hook (s)</th>'
             f'<th>Steps in a 0.375 s slice</th></tr>{tempo_rows()}</table>'
             f'<p class="small" style="margin:0 0 2pt;font-size:8.6pt">The shaded row is the worked example. The last column is (3 ÷ 8) ÷ (15 ÷ BPM): a slice of a 3-second hum cut into 8 pieces. At 120 BPM it is exactly 3 steps.</p>'
             f'<span class="k" style="margin-top:3pt">How long is a slice? (hums of 2 to 4 seconds)</span>'
             f'<table class="t cc" style="margin-top:1pt"><tr><th>Hum length</th><th>8 slices (s each)</th><th>16 slices (s each)</th><th>Steps per slice, 8 slices, 120 BPM</th><th>Steps per slice, 16 slices, 120 BPM</th></tr>{hum_rows()}</table>'
             f'<p class="small" style="margin:0 0 3pt;font-size:8.6pt">The slice length depends only on the hum: 3 ÷ 8 = 0.375 s at any tempo. The tempo only changes how many steps a slice covers: 0.375 ÷ 0.125 = 3 steps at 120 BPM.</p>'
             f'<div class="box acc-b" style="padding:5pt 9pt"><span class="k">My plan</span>'
             f'<div class="fl" style="margin:3pt 0 3pt;font-size:10pt"><b>Tempo:</b><span></span><b>BPM</b><b style="margin-left:8pt">One step = 15 ÷ BPM =</b><span></span><b>s</b></div>'
             f'<div class="fl" style="margin:0 0 3pt;font-size:10pt"><b>One bar = 240 ÷ BPM =</b><span></span><b>s</b><b style="margin-left:8pt">Hum length (2 to 4 s):</b><span></span><b>s</b></div>'
             f'<div class="fl" style="margin:0;font-size:10pt"><b>Slices (8 or 16):</b><span style="flex:0 0 0.8in"></span><b>One slice = length ÷ slices =</b><span></span><b>s</b><b style="margin-left:8pt">Steps per slice:</b><span style="flex:0 0 0.8in"></span></div></div>')
    return D.page("Timing page", "STUDENT", "Class 1", inner, n, wm, name=True, key="timing")


def record_page(n, wm=False):
    def box(title, items, acc=False):
        return (f'<div class="box{" acc-b" if acc else ""}" style="padding:4pt 9pt"><span class="k">{title}</span>'
                + "".join(D.chk(c, 11, "font-size:9.8pt;line-height:1.28;margin-bottom:2.5pt") for c in items) + '</div>')
    inner = (f'<p style="margin:0 0 4pt;font-size:10.2pt;line-height:1.36">Step 2: record the hum. You need one short phrase, 2 to 4 seconds long, hummed in your own voice. Think of a winter morning and hum what you hear in your head: '
             f'wind at the window, boots on snow, a kettle starting to sing. No words, and no tune from a song you know. The hum is the only sound the project starts with, so a clean take makes every later step easier.</p>'
             f'<div class="cols" style="gap:9pt;align-items:flex-start"><div>'
             + box("The room and the microphone", ["I am in a quiet room with soft surfaces, and the heating, fans and phones are off or far away.",
                                                   "I use headphones, so nothing leaks back into the microphone.",
                                                   "I keep the same distance from the microphone for every take. About 10 to 30 cm is this kit’s starting range: I try two distances and listen.",
                                                   "If there is a pop filter, it sits between my mouth and the microphone."], True)
             + '</div><div>'
             + box("Levels", ["I set the input gain on the interface while I hum my loudest moment.",
                              "The loudest part peaks around −12 to −6 dBFS on the track meter and never reaches 0 dBFS, the top of the scale.",
                              "A take that clips is deleted and recorded again; turning it down later does not fix it.",
                              "A quieter recording is safe: I can raise it later."])
             + '</div></div>'
             f'<div class="cols" style="gap:9pt;align-items:flex-start;margin-top:4pt"><div>'
             + box("The hum", ["It is one phrase of 2 to 4 seconds. I time it on the take log below.", "It has no words and no existing melody. It is my own idea.",
                               "It has a clear start and a few clear changes in loudness or pitch, so it slices well.", "I hum it more than once and keep the cleanest take."], True)
             + '</div><div class="box" style="padding:4pt 9pt"><span class="k">Copyright note: your own voice only</span>'
             f'<p style="margin:0 0 2pt;font-size:9.6pt;line-height:1.32">Record your OWN voice. Do not sample or chop a commercial recording: no songs, no clips from videos or games, no audio from the internet. '
             f'Chopping someone else’s recording is not the same as making your own. A classmate’s voice is fine only if they say yes.</p>'
             f'<p style="margin:0;font-size:9.6pt;line-height:1.32">If you would rather not record yourself, ask a willing classmate to hum, with permission, and credit them on your reflection page.</p></div></div>'
             f'<span class="k" style="margin-top:5pt">Take log</span>'
             f'<table class="t cc" style="margin-top:1pt"><tr><th>Take</th><th>Length (s)</th><th>Loudest peak (dBFS)</th><th>Noise or clipping?</th><th>Keep?</th></tr>'
             + "".join(f"<tr><td style='height:19pt'>{i}</td><td></td><td></td><td></td><td></td></tr>" for i in (1, 2, 3, 4)) + '</table>'
             f'<div class="box" style="margin-top:5pt;padding:4pt 9pt"><span class="k">My setup</span>'
             f'<div class="fl" style="margin:2pt 0 2pt;font-size:10pt"><b>Microphone:</b><span></span><b>Distance (cm):</b><span style="flex:0 0 0.9in"></span><b>Pop filter?</b><span style="flex:0 0 0.8in"></span></div>'
             f'<div class="fl" style="margin:0 0 2pt;font-size:10pt"><b>Interface gain setting:</b><span></span><b>The winter sound I hummed:</b><span></span></div></div>')
    return D.page("Recording checklist", "STUDENT", "Class 1", inner, n, wm, name=True, key="record")


def mode_rows():
    return ("<tr><td><b>Transient</b></td><td class='l'>Markers go at the start of each sound, found by the software. A sensitivity control sets how many markers appear.</td>"
            "<td class='l'>A hum with clear changes, such as a note change or a breath</td></tr>"
            f"<tr><td><b>Equal</b></td><td class='l'>The recording is cut into equal pieces. Aim for {NSLICE} or {NSLICE_ALT}; set the number with whatever control your version offers.</td>"
            f"<td class='l'>A steady hum, and planning: every slice is hum length ÷ {NSLICE} seconds</td></tr>"
            "<tr><td><b>Manual</b></td><td class='l'>You place each marker yourself.</td><td class='l'>Fixing a marker that cuts a sound in half</td></tr>")


def smap_rows():
    rows = []
    for i in range(NSLICE):
        a = i * EX_SLICE_S
        rows.append(f"<tr><td><b>{i + 1}</b></td><td>start key + {i}</td><td>{exact(a)}</td><td>{exact(a + EX_SLICE_S)}</td><td>{exact(EX_SLICE_S)}</td>"
                    f"<td style='width:1.0in'></td><td style='width:1.6in'></td></tr>")
    return "".join(rows)


def slicemap_page(n, wm=False):
    inner = (CSS_CC +
             f'<p style="margin:0 0 3pt;font-size:10.2pt;line-height:1.36">Step 3: slice and map. Load the hum in Quick Sampler (if your version has it), look for its slice mode and cut the hum into {NSLICE} or {NSLICE_ALT} slices. '
             f'Each slice plays from its own key, so you can play the pieces like notes. The picture shows a 3-second hum cut into {NSLICE} equal slices.</p>'
             f'<div style="margin:0 0 2pt">{D.body_svg(slices_body(1600, "slices page"))}</div>'
             f'<span class="k" style="margin-top:2pt">Three ways to place slice markers (if your version has them)</span>'
             f'<table class="t cc" style="margin-top:1pt"><tr><th style="width:12%">Mode</th><th>What it does</th><th style="width:34%">Good for</th></tr>{mode_rows()}</table>'
             f'<div style="width:58%;margin:2pt auto 0">{D.body_svg(keys_body(1500, "keys page"))}</div>'
             f'<span class="k" style="margin-top:4pt">The slice map for a 3-second hum (8 equal slices)</span>'
             f'<table class="t cc" style="margin-top:1pt"><tr><th>Slice</th><th>Key</th><th>Start (s)</th><th>End (s)</th><th>Length (s)</th><th>My start (s)</th><th>What I hear</th></tr>{smap_rows()}</table>'
             f'<p class="small" style="margin:1pt 0 2pt;font-size:8.6pt">Start of slice k = (k − 1) × hum length ÷ {NSLICE}. With {NSLICE_ALT} slices a 3-second hum gives {exact(slice_len(PHRASE, NSLICE_ALT))} s each. '
             f'Transient slices will not all be the same length: write your own start and end times from the markers.</p>')
    return D.page("Slice map", "STUDENT", "Classes 1–2", inner, n, wm, name=True, key="slicemap")


def pat_rows():
    rows = []
    for b, hits in enumerate(PATTERN, start=1):
        used = sorted({sl for _, sl in hits})
        rows.append(f"<tr><td><b>{b}</b></td><td>{len(hits)}</td><td class='l'>{', '.join(str(u) for u in used)}</td><td>{exact(hit_time(EX_BPM, b, 1))}</td></tr>")
    return "".join(rows)


def pattern_page(n, wm=False):
    inner = (CSS_CC +
             f'<p style="margin:0 0 3pt;font-size:10.2pt;line-height:1.36">Step 4: play the chop pattern. A chop pattern is a set of hits that repeats. Each lane is one slice and each column is one 16th-note step, so a bar has 16 steps '
             f'and the 4-bar pattern has {PAT_BARS * STEPS_BAR}. The model pattern below uses all {NSLICE} slices. Play your own, then draw it on the blank grid.</p>'
             f'<div style="margin:0 0 2pt">{D.body_svg(grid_body(1600, "grid page"))}</div>'
             f'<div class="cols" style="gap:10pt;align-items:flex-start"><div style="flex:1"><span class="k" style="margin-top:2pt">The model pattern, bar by bar</span>'
             f'<table class="t cc" style="margin-top:1pt"><tr><th>Bar</th><th>Hits</th><th>Slices used</th><th>Bar starts at (s, 120 BPM)</th></tr>{pat_rows()}</table>'
             f'<p class="small" style="margin:1pt 0 0;font-size:8.6pt">Hits per bar: {PAT_HITS[0]}, {PAT_HITS[1]}, {PAT_HITS[2]} and {PAT_HITS[3]}, {sum(PAT_HITS)} in all. One slice sounds at a time, so no step holds two hits.</p></div>'
             f'<div class="box acc-b" style="padding:4pt 9pt;flex:1"><span class="k">Reading the grid</span>'
             f'<p style="margin:0 0 2pt;font-size:9.4pt;line-height:1.32">A hit on grid step s of bar b starts at ((b − 1) × 16 + (s − 1)) × 15 ÷ BPM seconds. At 120 BPM, bar 2, grid step 4 is slice 2: (16 + 3) × 0.125 = 2.375 s.</p>'
             f'<p style="margin:0;font-size:9.4pt;line-height:1.32">At 120 BPM a slice lasts 3 steps. Slice 1 on grid step 1 and the next hit on grid step 4 gives it all 3 steps. A hit only 2 steps later cuts it short, if your '
             f'sampler plays one slice at a time.</p></div></div>'
             f'<span class="k" style="margin-top:4pt">My pattern: draw a hit in the lane of each slice you play</span>'
             f'<div style="margin:1pt 0 2pt">{D.body_svg(grid_body(1600, "grid blank page", blank=True))}</div>'
             f'<div class="fl" style="margin:2pt 0 0;font-size:10pt"><b>My hits per bar:</b><span></span><b>Total:</b><span style="flex:0 0 0.8in"></span><b>Bar 1 starts at 0 s; bar 2 starts at</b><span style="flex:0 0 0.8in"></span><b>s</b></div>')
    return D.page("The 4-bar chop pattern", "STUDENT", "Class 2", inner, n, wm, name=True, key="pattern")


def pitch_rows():
    rows = []
    for nn in PITCHES:
        r = ratio(nn)
        hi = ' class="hi"' if nn in (12, 7, -5) else ""
        rows.append(f"<tr{hi}><td><b>{sgn(nn)}</b></td><td class='l'>{INTERVALS[nn]}</td><td>{r3(r)}</td><td>{r1(HUM_HZ * r)}</td><td>{r4(float(EX_SLICE_S) / r)}</td></tr>")
    return "".join(rows)


def pitch_page(n, wm=False):
    inner = (CSS_CC +
             f'<p style="margin:0 0 3pt;font-size:10.2pt;line-height:1.36">Step 5: pitch and flip. Every key on a keyboard is one semitone, and 12 semitones make an octave. Raising a slice by n semitones multiplies its frequency by 2^(n ÷ 12), '
             f'so +12 doubles it (× 2.000), +7 gives × 1.498 and −5 gives × 0.749. Try a few and listen.</p>'
             f'<div style="margin:0 0 2pt">{D.body_svg(pitch_body(1560, "pitch page"))}</div>'
             f'<span class="k" style="margin-top:2pt">The pitch table</span>'
             f'<table class="t cc" style="margin-top:1pt"><tr><th>Semitones (n)</th><th>Interval</th><th>Ratio 2^(n ÷ 12)</th><th>A {HUM_HZ} Hz hum becomes (Hz)</th><th>A {exact(EX_SLICE_S)} s slice lasts (s) if played faster or slower</th></tr>{pitch_rows()}</table>'
             f'<p class="small" style="margin:1pt 0 3pt;font-size:8.6pt">{HUM_HZ} Hz is an example number for a low hum, not a measurement of your voice. Duration = {exact(EX_SLICE_S)} ÷ ratio. Intervals add and ratios multiply: '
             f'+7 then +5 is +12, and {r4(ratio(7))} × {r4(ratio(5))} = {r4(ratio(7) * ratio(5))}. To find n from a ratio, n = 12 × log2(ratio): 12 × log2(2) = 12.</p>'
             f'<div class="cols" style="gap:9pt;align-items:flex-start"><div class="box acc-b" style="padding:4pt 9pt"><span class="k">Reverse and stretch (if your version has them)</span>'
             f'<p style="margin:0 0 2pt;font-size:9.4pt;line-height:1.32"><b>Reverse:</b> look for a reverse option in the Quick Sampler window. A reversed slice makes a good lead-in to the next section.</p>'
             f'<p style="margin:0;font-size:9.4pt;line-height:1.32"><b>Time-stretch:</b> many samplers play a recording faster when you raise its pitch, so the slice gets shorter. Some tools (Flex Time, for example) can change the length '
             f'without changing the pitch, and the other way round. Try one and listen for a watery or rough sound.</p></div>'
             f'<div class="box" style="padding:4pt 9pt"><span class="k">My pitch plan</span>'
             f'<table class="t cc" style="margin-top:1pt"><tr><th>Slice</th><th>Semitones</th><th>Ratio</th><th>I hear</th></tr>'
             + "".join("<tr><td style='height:19pt'></td><td></td><td></td><td></td></tr>" for _ in range(3)) + '</table>'
             f'<div class="fl" style="margin:3pt 0 0;font-size:9.8pt"><b>Reversed slice:</b><span style="flex:0 0 0.7in"></span><b>Where it goes (bar):</b><span></span></div></div></div>')
    return D.page("Pitch table", "STUDENT", "Class 2", inner, n, wm, name=True, key="pitch")


def bass_rows():
    names = {0: "the root", -5: "a fourth below the root", -7: "a fifth below the root"}
    return "".join(f"<tr><td><b>{b}</b></td><td>{sgn(s)}</td><td>{r3(ratio(s))}</td><td class='l'>{names[s]}</td></tr>" for b, s in enumerate(BASS, start=1))


def drums_page(n, wm=False):
    kick, snare, hat = (len(h) for _, h in DRUMS)
    inner = (CSS_CC +
             f'<p style="margin:0 0 3pt;font-size:10.2pt;line-height:1.36">Step 6: groove, arrange and mix. First a simple drum groove and a bass under your chops. The groove is one bar of 16 steps that repeats: '
             f'the kick on grid steps {", ".join(str(s) for s in DRUMS[0][1][:-1])} and {DRUMS[0][1][-1]}, the snare on {DRUMS[1][1][0]} and {DRUMS[1][1][1]} (beats 2 and 4) and the hat on every other step. '
             f'Build it from a Session Player or a drum kit or a loop (each if your version has it), or play the pads yourself.</p>'
             f'<div style="margin:0 0 3pt">{D.body_svg(drum_body(1400, "drums page"))}</div>'
             f'<div class="cols" style="gap:10pt;align-items:flex-start"><div style="flex:1"><span class="k" style="margin-top:2pt">The bass: one low note per bar</span>'
             f'<table class="t cc" style="margin-top:1pt"><tr><th>Bar</th><th>Semitones from the root</th><th>Ratio</th><th>Note</th></tr>{bass_rows()}</table>'
             f'<p class="small" style="margin:1pt 0 0;font-size:8.6pt">The bass plays in a low octave, so only the offsets matter here. Bars 1 to 4 repeat for the whole hook. Choose the root from the key of your hum.</p></div>'
             f'<div class="box acc-b" style="padding:4pt 9pt;flex:1"><span class="k">Counting the groove</span>'
             f'<p style="margin:0 0 2pt;font-size:9.6pt;line-height:1.32">Kick {kick}, snare {snare} and hat {hat}: {kick + snare + hat} drum hits in each bar. The kick and the hat both play on the first step of the bar, and the snare and the hat both play on the first step of beat 2, '
             f'but they are different sounds, so both play.</p>'
             f'<p style="margin:0;font-size:9.6pt;line-height:1.32">One step lasts 15 ÷ BPM seconds, so at 120 BPM the snare lands at (5 − 1) × 0.125 = 0.5 s and (13 − 1) × 0.125 = 1.5 s into each bar.</p></div></div>'
             f'<div class="box" style="margin-top:4pt;padding:4pt 9pt"><span class="k">Keep the chops clear</span>'
             + "".join(D.chk(c, 11, "font-size:9.8pt;line-height:1.28;margin-bottom:2pt") for c in [
                 "The drums and the bass use only sounds that come with Logic, or sounds I made myself.",
                 "The bass is quieter than the kick and does not hide the chops.",
                 "When I mute the drums and the bass, the chops still sound like a hook."]) + '</div>'
             f'<span class="k" style="margin-top:4pt">My groove: draw the hits</span><div style="margin:2pt auto 3pt;width:88%">{D.body_svg(drum_body(1400, "drums blank page", blank=True))}</div>'
             f'<span class="k" style="margin-top:3pt">My groove and bass</span>'
             f'<div class="fl" style="margin:2pt 0 2pt;font-size:10pt"><b>Drum sound source:</b><span></span><b>Bass sound:</b><span></span></div>'
             f'<div class="fl" style="margin:0;font-size:10pt"><b>Bass notes for bars 1 to 4 (semitones):</b><span></span></div>')
    return D.page("Drum groove and bass", "STUDENT", "Class 3", inner, n, wm, name=True, key="drums")


def sec_rows():
    rows = []
    for nm, a, b in ARR_SECTIONS:
        layers = [r for r, spans in ARR_ROWS if any(x <= b and a <= y for x, y in spans)]
        rows.append(f"<tr><td><b>{nm.title()}</b></td><td>{a}–{b}</td><td>{exact(hit_time(EX_BPM, a, 1))}</td><td>{exact(hit_time(EX_BPM, b + 1, 1))}</td>"
                    f"<td class='l'>{', '.join(x.lower() for x in layers)}</td></tr>")
    return "".join(rows)


def len_rows():
    return "".join(f"<tr><td>{t}</td><td>{dec(ARR_BARS_ALT * bar_len(t), 3)}</td><td>{dec(ARR_BARS * bar_len(t), 3)}</td></tr>" for t in TEMPOS)


def arrange_page(n, wm=False):
    mine = "".join("<tr><td style='height:19pt'></td><td></td><td></td><td></td></tr>" for _ in range(4))
    inner = (CSS_CC +
             f'<p style="margin:0 0 3pt;font-size:10.2pt;line-height:1.36">Step 6: groove, arrange and mix, continued. An arrangement puts your layers into sections. This one is {ARR_BARS} bars, four sections of 4 bars: an intro, '
             f'the hook, the drop and an outro. It has {len(ARR_ROWS)} layers. An {ARR_BARS_ALT}-bar version halves every section: 2 bars each.</p>'
             f'<div style="margin:0 0 3pt">{D.body_svg(arr_body(1600, "arrange page"))}</div>'
             f'<div class="cols" style="gap:10pt;align-items:flex-start"><div style="flex:1.6"><span class="k" style="margin-top:2pt">The sections at {EX_BPM} BPM</span>'
             f'<table class="t cc" style="margin-top:1pt"><tr><th>Section</th><th>Bars</th><th>Starts (s)</th><th>Ends (s)</th><th>Layers that play</th></tr>{sec_rows()}</table></div>'
             f'<div style="flex:1"><span class="k" style="margin-top:2pt">How long is my arrangement?</span>'
             f'<table class="t cc" style="margin-top:1pt"><tr><th>BPM</th><th>{ARR_BARS_ALT} bars (s)</th><th>{ARR_BARS} bars (s)</th></tr>{len_rows()}</table></div></div>'
             f'<p class="small" style="margin:1pt 0 2pt;font-size:8.6pt">Length = bars × 240 ÷ BPM. At {EX_BPM} BPM, {ARR_BARS} bars × 2 s = {fmt(ARR_BARS * EX_BAR_S)} s. Section start = (first bar − 1) × 240 ÷ BPM.</p>'
             f'<span class="k" style="margin-top:3pt">My arrangement (my tempo: ________ BPM)</span>'
             f'<table class="t cc" style="margin-top:1pt"><tr><th>Section</th><th>Bars</th><th>Starts at (s)</th><th>Layers that play</th></tr>{mine}</table>'
             f'<div class="box acc-b" style="margin-top:4pt;padding:4pt 9pt"><span class="k">Check my arrangement</span>'
             + "".join(D.chk(c, 11, "font-size:9.8pt;line-height:1.28;margin-bottom:2pt") for c in [
                 "Each section is the same number of bars, and the sections add up to 8 or 16 bars.",
                 "The layers build: the hook has more layers than the intro, and the drop has the bass.",
                 "A reversed chop leads into the next section, and the outro ends on the first step of its last bar or a clean stop."]) + '</div>')
    return D.page("Arrangement map", "STUDENT", "Class 3", inner, n, wm, name=True, key="arrange")


def mix_page(n, wm=False):
    def box(title, items, acc=False):
        return (f'<div class="box{" acc-b" if acc else ""}" style="padding:5pt 9pt"><span class="k">{title}</span>'
                + "".join(D.chk(c, 11, "font-size:10pt;line-height:1.3;margin-bottom:3pt") for c in items) + '</div>')
    inner = (f'<p style="margin:0 0 5pt;font-size:10.2pt;line-height:1.36">Step 6: groove, arrange and mix, finished. A mix makes the chops clear, the drums and bass supportive and the ending clean. Work through the boxes with headphones, '
             f'then check each one off.</p>'
             f'<div class="cols" style="gap:10pt;align-items:flex-start"><div>'
             + box("Chops", ["I can hear every slice that matters, and none of them clicks.", "The chops are not clipped and the hum is not noisy.",
                             "The pitched chops are in tune with each other, or out of tune on purpose."], True)
             + '<div style="height:6pt"></div>'
             + box("Drums and bass", ["The kick and the bass do not fight: the bass is a little quieter.", "The snare and the hat sit behind the chops.",
                                      "I can mute the drums and still hear a hook."])
             + '</div><div>'
             + box("Sections", ["The intro, hook, drop and outro are the lengths on my arrangement map.", "A reversed chop leads into the next section.",
                                "The hook ends when it should, on the last bar I planned."], True)
             + '<div style="height:6pt"></div>'
             + box("Levels", ["The master meter never reaches 0 dBFS; I leave room to spare.", "The loudest section is the drop or the hook, not by accident.",
                              "I listened at a normal volume, not only loud."])
             + '</div></div>'
             f'<div class="box" style="margin-top:6pt;padding:5pt 9pt"><span class="k">The listening test</span><p style="margin:0 0 3pt;font-size:10pt;line-height:1.36">Play the whole hook with your eyes closed and '
             f'rate each part from 1 (weak) to 5 (very strong). Does the hum still sound like a voice? Does the pattern feel steady? Does the hook come back? Write what you hear:</p>'
             f'<div class="fl" style="margin:2pt 0;font-size:10pt"><b>Voice:</b><span></span><b>Pattern:</b><span></span><b>Hook:</b><span></span></div></div>'
             f'<div class="box acc-b" style="margin-top:6pt;padding:5pt 9pt"><span class="k">Bounce</span>'
             + "".join(D.chk(c, 11, "font-size:10pt;margin-bottom:3pt") for c in [
                 "The bounce starts at bar 1 and ends at the planned length (8 or 16 bars; check the seconds for my tempo on page " + str(pg("timing")) + ").",
                 "MP3 or WAV bounced, and the .logicx project zipped.", f"Both files named {FILE_NAME}."]) + '</div>'
             f'<span class="k" style="margin-top:6pt">What I changed after the listening test</span>' + D.lines(7, 24))
    return D.page("Mix checklist", "STUDENT", "Class 3", inner, n, wm, name=True, key="mix")


# ================================================================ worked example (2 pages)
def ex_slice_rows():
    rows = []
    for i in range(NSLICE):
        a = i * EX_SLICE_S
        rows.append(f"<tr><td><b>{i + 1}</b></td><td>{exact(a)}</td><td>{exact(a + EX_SLICE_S)}</td><td>{exact(EX_SLICE_S)}</td><td>{fmt(slice_steps(PHRASE, NSLICE, EX_BPM))}</td><td>{slice_hits(i + 1)}</td></tr>")
    return "".join(rows)


def ex_bar_rows():
    rows = []
    for b, hits in enumerate(PATTERN, start=1):
        rows.append(f"<tr><td><b>{b}</b></td><td>{len(hits)}</td><td>{exact(hit_time(EX_BPM, b, 1))}</td><td>{exact(hit_time(EX_BPM, b + 1, 1))}</td></tr>")
    return "".join(rows)


def ex_pitch_rows():
    return "".join(f"<tr><td><b>{sl}</b></td><td>{sgn(nn)}</td><td>{r3(ratio(nn))}</td><td>{r4(float(EX_SLICE_S) / ratio(nn))}</td></tr>" for sl, nn in PITCH_USED)


def example_page(n, wm=False):
    inner = (f'<style>table.ec td {{ text-align: center; }}</style>'
             f'<p style="margin:0 0 4pt;font-size:10pt">An <b>invented plan on paper</b>: a hook at {EX_BPM} BPM from a 3-second hum. No audio is included. '
             f'Student projects will differ. Page 1 of 2: the plan, the slices and the pattern.</p>'
             f'<div class="cols" style="gap:10pt;align-items:flex-start"><div class="box"><span class="k">1 · A weak plan</span><p style="margin:0;font-size:10.2pt">{EX_WEAK}</p>'
             f'<p style="margin:3pt 0 0;font-size:9.2pt">It names no tempo, no hum length, no slices, no pattern and no sections.</p></div>'
             f'<div class="box acc-b"><span class="k">2 · A clear plan</span><p style="margin:0;font-size:8.6pt;line-height:1.28">{EX_STRONG}</p></div></div>'
             f'{D.H2("3 · The slice map: 3 seconds in 8 equal slices")}'
             f'<table class="t ec" style="font-size:8.8pt;line-height:1.14"><tr><th>Slice</th><th>Start (s)</th><th>End (s)</th><th>Length (s)</th><th>Steps at {EX_BPM} BPM</th><th>Hits in the pattern</th></tr>{ex_slice_rows()}</table>'
             f'<p style="margin:2pt 0 0;font-size:8.8pt;line-height:1.3">Each slice is {exact(PHRASE)} ÷ {NSLICE} = {exact(EX_SLICE_S)} s, and one step is 15 ÷ {EX_BPM} = {exact(EX_STEP_S)} s, so a slice is {exact(EX_SLICE_S)} ÷ {exact(EX_STEP_S)} = '
             f'{fmt(slice_steps(PHRASE, NSLICE, EX_BPM))} steps. The seven slice lines sit at {", ".join(exact(i * EX_SLICE_S) for i in range(1, NSLICE))} seconds. With 16 slices each would be {exact(slice_len(PHRASE, NSLICE_ALT))} s. '
             f'The hits in the last column add up to {sum(PAT_HITS)}.</p>'
             f'{D.H2("4 · The 4-bar chop pattern at 120 BPM")}'
             f'<div class="cols" style="gap:10pt;align-items:flex-start"><div style="flex:0 0 3.4in"><table class="t ec" style="font-size:8.8pt;line-height:1.14"><tr><th>Bar</th><th>Hits</th><th>Starts (s)</th><th>Ends (s)</th></tr>{ex_bar_rows()}</table></div>'
             f'<p style="margin:0;font-size:8.8pt;line-height:1.3">The pattern has {PAT_HITS[0]}, {PAT_HITS[1]}, {PAT_HITS[2]} and {PAT_HITS[3]} hits, {sum(PAT_HITS)} in all, on a grid of {PAT_BARS} × {STEPS_BAR} = {PAT_BARS * STEPS_BAR} steps. '
             f'It lasts {PAT_BARS} × {fmt(EX_BAR_S)} = {fmt(PAT_BARS * EX_BAR_S)} seconds. A hit on bar 2, grid step 4 (slice 2) starts at (16 + 3) × {exact(EX_STEP_S)} = {exact(hit_time(EX_BPM, 2, 4))} s. '
             f'Slice 1 plays on grid step 1 and the next hit comes on grid step 4, so it gets all 3 of its steps.</p></div>'
             f'<div class="box" style="margin-top:4pt;padding:4pt 9pt"><span class="k">What to notice</span><p style="margin:0;font-size:9.2pt;line-height:1.3">{EX_NOTE[0].upper() + EX_NOTE[1:]}.</p></div>')
    return D.page("Worked example · the plan, the slices and the pattern", "EXAMPLE", "Teacher", inner, n, wm, ak=True, key="example")


def example2_page(n, wm=False):
    qs = " ".join(f"{i + 1}. {q}" for i, q in enumerate(EX_QUESTIONS))
    inner = (f'<p style="margin:0 0 3pt;font-size:10pt">The same hook, page 2 of 2: the pitch choices, the groove and the arrangement, then the moments to point out.</p>'
             f'{D.H2("5 · Three pitch choices")}'
             f'<div class="cols" style="gap:10pt;align-items:flex-start"><div style="flex:0 0 3.5in"><table class="t ec" style="font-size:8.8pt;line-height:1.14"><tr><th>Slice</th><th>Semitones</th><th>Ratio</th><th>Length now (s)</th></tr>{ex_pitch_rows()}</table></div>'
             f'<p style="margin:0;font-size:8.8pt;line-height:1.3">Ratio = 2^(n ÷ 12): +12 gives {r3(ratio(12))}, +7 gives {r3(ratio(7))} and −5 gives {r3(ratio(-5))}. If the sampler plays a pitched slice faster or slower, its length becomes '
             f'{exact(EX_SLICE_S)} ÷ ratio: {r4(float(EX_SLICE_S) / ratio(12))} s at +12 and {r4(float(EX_SLICE_S) / ratio(-5))} s at −5. One slice is also reversed, at the end of bar 4.</p></div>'
             f'{D.H2("6 · The groove and the bass")}'
             f'<p style="margin:0;font-size:9.6pt;line-height:1.34">One bar of drums has the kick on grid steps {", ".join(str(s) for s in DRUMS[0][1])} ({len(DRUMS[0][1])} hits), the snare on {" and ".join(str(s) for s in DRUMS[1][1])} ({len(DRUMS[1][1])} hits) '
             f'and the hat on every other step ({len(DRUMS[2][1])} hits): {sum(len(h) for _, h in DRUMS)} hits. The bass plays one note per bar at {", ".join(sgn(s) for s in BASS)} semitones from the root.</p>'
             f'{D.H2("7 · The 16-bar arrangement")}'
             f'<div style="margin:1pt 0 3pt">{D.body_svg(arr_body(1600, "arrange page"))}</div>'
             f'<p style="margin:0;font-size:9.6pt;line-height:1.34">{ARR_BARS} bars × {fmt(EX_BAR_S)} s = {fmt(ARR_BARS * EX_BAR_S)} s. The intro starts at {exact(hit_time(EX_BPM, 1, 1))} s, the hook at {exact(hit_time(EX_BPM, 5, 1))} s, '
             f'the drop at {exact(hit_time(EX_BPM, 9, 1))} s and the outro at {exact(hit_time(EX_BPM, 13, 1))} s.</p>'
             f'<div class="box" style="margin-top:5pt"><span class="k">8 · Three feedback questions (invented)</span><p style="margin:0;font-size:10pt;line-height:1.36">{qs}</p></div>'
             f'<div class="box acc-b" style="margin-top:5pt"><span class="k">9 · Moments to point out in class</span><ul style="margin:0">'
             f'<li style="font-size:10pt;margin-bottom:2pt">The same 3 seconds of hum make every sound in the hook, so the slice map explains everything the listener hears.</li>'
             f'<li style="font-size:10pt;margin-bottom:0">At 120 BPM a step is exactly 0.125 s and a slice exactly 3 steps, so the class can clap the grid and hear each hit land.</li></ul></div>')
    return D.page("Worked example · the pitch, the groove and the arrangement", "EXAMPLE", "Teacher", inner, n, wm, ak=True, key="example2")


PAGES = {"howto": howto_page, "overview": overview_page, "setup": setup_page, "example": example_page, "example2": example2_page,
         "timing": timing_page, "record": record_page, "slicemap": slicemap_page, "pattern": pattern_page, "pitch": pitch_page, "drums": drums_page,
         "arrange": arrange_page, "mix": mix_page}


def vocab8_page(n, wm=False):
    cells = "".join(
        f'<div class="box" style="padding:6pt 8pt 4pt"><p style="margin:0 0 2pt;font-size:10.8pt;line-height:1.3"><b style="font-family:Oswald;font-size:12.5pt;'
        f'text-transform:uppercase;letter-spacing:.02em">{a}</b> — {b}</p>'
        f'<div class="fl" style="margin:17pt 0 15pt"><b>In my own words:</b><span></span></div>'
        f'<div class="fl" style="margin:0 0 8pt"><b>{VOCAB_PROMPT}</b><span></span></div></div>' for a, b in VOCAB)
    inner = (f'<p style="font-size:11.4pt;margin:0 0 7pt">The eight words from your project sheet, with definitions. Rewrite each in your '
             f'own words, then show where it happens in your own project.</p><div style="display:grid;grid-template-columns:1fr 1fr;gap:8pt">{cells}</div>')
    return D.page("Key vocabulary", "STUDENT", "Vocabulary", inner, n, wm, name=True, key="vocab")


PAGES["vocab"] = vocab8_page
# ================================================================ content-check helpers (shared with 067/076)
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
    text = re.sub(r"\s+", " ", text)
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




BADGE = {"timing": "Class 1", "record": "Class 1", "slicemap": "Classes 1–2", "pattern": "Class 2", "pitch": "Class 2", "drums": "Class 3", "arrange": "Class 3",
         "mix": "Class 3", "present": f"Classes {CLASSES - 1}–{CLASSES}"}


FORBIDDEN_WORDS = ("cham" + "pagne", "toast", "cheers", "wine", "beer", "cocktail", "alcohol", "bub" + "bly", "church", "prayer", "pray ", "blessing", "holy", "sacred",
                   "religio", "god ", "santa", "christmas", "hanukkah", "chanukah", "kwanzaa", "holiday", "sleigh", "reindeer", "ornament", "carol", "elf ", "elves")
EXPECT_STEP = {"timing": {1}, "record": {2}, "slicemap": {3}, "pattern": {4}, "pitch": {5}, "drums": {6}, "arrange": {6}, "mix": {6}}


def float_slice(L, n, i):
    """An independent float check of slice i (0-based): start and end seconds of equal slices of a phrase of L seconds."""
    w = float(L) / n
    return i * w, (i + 1) * w


def svg_count(svg, cls):
    return len(re.findall(rf'class="{cls}"', svg))


def verify_content():
    errs = []
    counts = dict(goals=(GOALS, 4), vocab=(VOCAB, 8), reqs=(REQS, 7), steps=(STEPS, 7), tips=(TIPS, 4), check=(CHECK, 6),
                  rubric=(RUBRIC, 5), struggles=(STRUGGLES, 4), resources=(RESOURCES, 5), slides=(SLIDES, 17), plan=(PLAN, 26),
                  logic=(LOGIC_REF, 9), pattern=(PATTERN, 4), drums=(DRUMS, 3), arrange=(ARR_ROWS, 5), sections=(ARR_SECTIONS, 4))
    for nm, (lst, nexp) in counts.items():
        if len(lst) != nexp:
            errs.append(f"{nm}: {len(lst)} items, expected {nexp}")
    if RUBRIC_TOTAL != 25 or LEVELS != [1, 2, 3, 4, 5] or len(RUBRIC_SHORT) != 5:
        errs.append("rubric is /25, levels 1-5")
    if FILE_NAME not in CHECK[2]:
        errs.append("file name format must be on the checklist")
    if [w for w, _ in VOCAB] != ["Chop", "Slice", "Transient", "Sampler", "Pitch", "Pattern", "Hook", "Step"]:
        errs.append("vocabulary: chop, slice, transient, sampler, pitch, pattern, hook, step")
    if set(TAGS) & {"Holiday", "Student Practice", "Theme", "Seasonal"} or "Performing Arts" in SUBJECTS:
        errs.append("tags and subjects must not be headings")
    if len(LISTING_TITLE) > 80 or "Logic Pro" not in LISTING_TITLE[:30]:
        errs.append("listing title: at most 80 characters, 'Logic Pro' in the first 30")
    for w in ("new year", "winter", "holiday", "christmas", "hanukkah", "chanukah", "sleigh", "carol", "snow", "eve "):
        if w in LISTING_TITLE.lower():
            errs.append(f"the listing title must not hold the seasonal word {w}")
    if len(STEP_NAMES) != len(STEPS) or any(not s.startswith(f"<b>{nm}</b>") for s, nm in zip(STEPS, STEP_NAMES)):
        errs.append("STEPS must start with the bold names in STEP_NAMES (the pages cite them)")
    # ---- the timing arithmetic, by hand first
    if [spb(b) for b in (120, 90, 100, 80)] != [Fraction(1, 2), Fraction(2, 3), Fraction(3, 5), Fraction(3, 4)]:
        errs.append("seconds per beat = 60 / BPM: 0.5 at 120, 0.6667 at 90, 0.6 at 100, 0.75 at 80")
    if [step_len(b) for b in TEMPOS] != [Fraction(3, 16), Fraction(1, 6), Fraction(3, 20), Fraction(3, 22), Fraction(1, 8), Fraction(15, 128)]:
        errs.append("seconds per 16th-note step = 15 / BPM: 3/16, 1/6, 3/20, 3/22, 1/8, 15/128")
    if step_len(120) != Fraction(125, 1000) or step_len(120) != spb(120) / 4:
        errs.append("a 16th note at 120 BPM lasts 0.125 s, a quarter of a beat")
    if [bar_len(b) for b in TEMPOS] != [Fraction(3), Fraction(8, 3), Fraction(12, 5), Fraction(24, 11), Fraction(2), Fraction(15, 8)]:
        errs.append("seconds per bar = 240 / BPM")
    for b in TEMPOS:
        if bar_len(b) != 4 * spb(b) or bar_len(b) != STEPS_BAR * step_len(b) or abs(float(step_len(b)) - 15.0 / b) > 1e-12 or abs(float(bar_len(b)) - 240.0 / b) > 1e-12:
            errs.append(f"a bar is 4 beats and 16 steps at {b} BPM")
        if PAT_BARS * bar_len(b) != Fraction(960, b) or ARR_BARS * bar_len(b) != Fraction(3840, b) or ARR_BARS_ALT * bar_len(b) != Fraction(1920, b):
            errs.append(f"4 bars = 960 / BPM, 8 bars = 1920 / BPM and 16 bars = 3840 / BPM at {b} BPM")
    if [dec(spb(b), 3) for b in TEMPOS] != ["0.750", "0.667", "0.600", "0.545", "0.500", "0.469"] or \
       [dec(step_len(b), 4) for b in TEMPOS] != ["0.1875", "0.1667", "0.1500", "0.1364", "0.1250", "0.1172"] or \
       [dec(bar_len(b), 3) for b in TEMPOS] != ["3.000", "2.667", "2.400", "2.182", "2.000", "1.875"]:
        errs.append("seconds per beat, step and bar, rounded half up")
    if [dec(PAT_BARS * bar_len(b), 3) for b in TEMPOS] != ["12.000", "10.667", "9.600", "8.727", "8.000", "7.500"] or \
       [dec(ARR_BARS * bar_len(b), 3) for b in TEMPOS] != ["48.000", "42.667", "38.400", "34.909", "32.000", "30.000"] or \
       [dec(ARR_BARS_ALT * bar_len(b), 3) for b in TEMPOS] != ["24.000", "21.333", "19.200", "17.455", "16.000", "15.000"]:
        errs.append("4-bar, 8-bar and 16-bar lengths at the six tempos")
    if [slice_steps(PHRASE, NSLICE, b) for b in TEMPOS] != [2, Fraction(9, 4), Fraction(5, 2), Fraction(11, 4), 3, Fraction(16, 5)] or \
       [dec(slice_steps(PHRASE, NSLICE, b), 2) for b in TEMPOS] != ["2.00", "2.25", "2.50", "2.75", "3.00", "3.20"]:
        errs.append("steps in a 0.375 s slice: 2, 2.25, 2.5, 2.75, 3, 3.2 at 80, 90, 100, 110, 120, 128 BPM")
    if rnd(Fraction(5, 2), 0) != 3 or dec(Fraction(15, 128), 4) != "0.1172" or dec(Fraction(15, 8), 3) != "1.875":
        errs.append("round half up")
    # ---- slices
    if slice_len(PHRASE, NSLICE) != Fraction(3, 8) or exact(slice_len(PHRASE, NSLICE)) != "0.375" or exact(slice_len(PHRASE, NSLICE_ALT)) != "0.1875":
        errs.append("3 s in 8 slices = 0.375 s; in 16 slices = 0.1875 s")
    if slice_len(PHRASE, NSLICE) != 3 * step_len(120) or slice_steps(PHRASE, NSLICE, 120) != 3:
        errs.append("a 0.375 s slice is exactly 3 steps at 120 BPM")
    if [exact(slice_len(L, NSLICE)) for L in PHRASES] != ["0.25", "0.3125", "0.375", "0.4375", "0.5"] or \
       [exact(slice_len(L, NSLICE_ALT)) for L in PHRASES] != ["0.125", "0.15625", "0.1875", "0.21875", "0.25"]:
        errs.append("slice lengths for hums of 2, 2.5, 3, 3.5 and 4 seconds")
    for L in PHRASES:
        for nn in (NSLICE, NSLICE_ALT):
            if slice_len(L, nn) * nn != L:
                errs.append(f"{nn} slices of {L} s must add up to the hum")
            for i in range(nn):
                a, b = slice_len(L, nn) * i, slice_len(L, nn) * (i + 1)
                fa, fb = float_slice(L, nn, i)
                if abs(float(a) - fa) > 1e-12 or abs(float(b) - fb) > 1e-12:
                    errs.append(f"slice {i + 1} of {nn} for {L} s: exact and float disagree")
    if [exact(i * EX_SLICE_S) for i in range(NSLICE)] != ["0", "0.375", "0.75", "1.125", "1.5", "1.875", "2.25", "2.625"]:
        errs.append("slice starts of the 3-second example: 0, 0.375, 0.75, 1.125, 1.5, 1.875, 2.25, 2.625")
    # ---- hit times
    if hit_time(120, 1, 1) != 0 or hit_time(120, 2, 1) != 2 or hit_time(120, 2, 4) != Fraction(19, 8) or hit_time(120, 5, 1) != 8 or hit_time(120, 4, 15) != Fraction(31, 4) or \
       hit_time(120, 9, 1) != 16 or hit_time(120, 13, 1) != 24 or hit_time(120, 17, 1) != 32:
        errs.append("hit times at 120 BPM: bar 2 grid step 4 = 2.375 s, bar 4 grid step 15 = 7.75 s, bar 5 = 8 s, bar 9 = 16 s, bar 13 = 24 s, bar 17 = 32 s")
    for b in TEMPOS:
        for bar in range(1, 5):
            for st in range(1, 17):
                t = hit_time(b, bar, st)
                k = t / step_len(b)
                if k != (bar - 1) * 16 + (st - 1) or abs(float(t) - ((bar - 1) * 16 + st - 1) * 15.0 / b) > 1e-9:
                    errs.append(f"hit time at {b} BPM bar {bar} grid step {st}")
    # ---- the model pattern
    if PAT_HITS != [6, 6, 6, 8] or sum(PAT_HITS) != 26 or sum(slice_hits(s) for s in range(1, NSLICE + 1)) != 26 or [slice_hits(s) for s in range(1, 9)] != [5, 4, 4, 3, 2, 2, 3, 3]:
        errs.append("model pattern: 6, 6, 6 and 8 hits (26); hits per slice 5, 4, 4, 3, 2, 2, 3, 3")
    used = set()
    for b, hits in enumerate(PATTERN, start=1):
        steps = [s for s, _ in hits]
        if steps != sorted(steps) or len(set(steps)) != len(steps) or not all(1 <= s <= STEPS_BAR for s in steps):
            errs.append(f"pattern bar {b}: one hit per grid step, in order, steps 1 to 16")
        if not all(1 <= sl <= NSLICE for _, sl in hits):
            errs.append(f"pattern bar {b}: slices 1 to {NSLICE}")
        used |= {sl for _, sl in hits}
    if used != set(range(1, NSLICE + 1)):
        errs.append("the model pattern uses every slice")
    g_svg = grid_body(1600, "grid check")[0]
    gb_svg = grid_body(1600, "grid check blank", blank=True)[0]
    if svg_count(g_svg, "hit") != sum(PAT_HITS) or svg_count(g_svg, "cell") != PAT_BARS * STEPS_BAR * NSLICE or svg_count(gb_svg, "hit") != 0 or svg_count(gb_svg, "cell") != PAT_BARS * STEPS_BAR * NSLICE:
        errs.append(f"the step grid drawing must hold {sum(PAT_HITS)} hits in {PAT_BARS * STEPS_BAR * NSLICE} cells ({PAT_BARS} bars x {STEPS_BAR} steps x {NSLICE} lanes); the blank grid has no hits")
    for b in range(PAT_BARS):      # hits per bar counted again from the drawing's x positions
        gx, pw = 150, 1600 - 150 - 34
        cw = pw / (PAT_BARS * STEPS_BAR)
        xs = [float(m) for m in re.findall(r'<rect class="hit" x="([\d.]+)"', g_svg)]
        n_in = sum(1 for x in xs if gx + b * STEPS_BAR * cw <= x < gx + (b + 1) * STEPS_BAR * cw)
        if n_in != PAT_HITS[b]:
            errs.append(f"the drawn grid has {n_in} hits in bar {b + 1}, the data {PAT_HITS[b]}")
    if svg_count(slices_body(1600, "s check")[0], "marker") != NSLICE - 1:
        errs.append(f"the waveform must show {NSLICE - 1} slice lines (for {NSLICE} slices)")
    if svg_count(keys_body(1500, "k check")[0], "slicekey") != NSLICE:
        errs.append(f"the keyboard map must mark {NSLICE} keys")
    if [len(h) for _, h in DRUMS] != [3, 2, 8] or svg_count(drum_body(1400, "d check")[0], "dhit") != 13:
        errs.append("drum groove: kick 3, snare 2 and hat 8 hits (13), drawn the same")
    if BASS != [0, 0, -5, -7] or [r3(ratio(s)) for s in BASS] != ["1.000", "1.000", "0.749", "0.667"]:
        errs.append("bass plan: 0, 0, -5, -7 semitones (x1.000, x1.000, x0.749, x0.667)")
    # ---- the arrangement
    if [(n_, a, b) for n_, a, b in ARR_SECTIONS] != [("INTRO", 1, 4), ("HOOK", 5, 8), ("DROP", 9, 12), ("OUTRO", 13, 16)] or ARR_BARS != 16:
        errs.append("arrangement: intro 1-4, hook 5-8, drop 9-12, outro 13-16")
    for nm, spans in ARR_ROWS:
        for a, b in spans:
            if not 1 <= a <= b <= ARR_BARS:
                errs.append(f"layer {nm}: bars {a}-{b} outside 1-{ARR_BARS}")
    if len(ARR_LAYERS) != 5 or svg_count(arr_body(1600, "a check")[0], "block") != sum(len(s) for _, s in ARR_ROWS):
        errs.append("arrangement: 5 layers, every block drawn")
    if ARR_BARS * EX_BAR_S != 32 or ARR_BARS_ALT * EX_BAR_S != 16 or [exact(hit_time(EX_BPM, a, 1)) for _, a, _ in ARR_SECTIONS] != ["0", "8", "16", "24"]:
        errs.append("16 bars at 120 BPM = 32 s (8 bars = 16 s); sections start at 0, 8, 16 and 24 s")
    # ---- pitch
    if abs(SEMITONE - 1.0594630943592953) > 1e-12 or abs(ratio(12) - 2) > 1e-12:
        errs.append("a semitone is 2^(1/12) = 1.05946; 12 semitones double the frequency")
    if [r3(ratio(n_)) for n_ in PITCHES] != ["0.500", "0.667", "0.749", "1.000", "1.189", "1.260", "1.335", "1.498", "2.000"]:
        errs.append("pitch ratios: -12 0.500, -7 0.667, -5 0.749, 0 1.000, +3 1.189, +4 1.260, +5 1.335, +7 1.498, +12 2.000")
    for n_ in PITCHES:
        rr = 1.0
        for _ in range(abs(n_)):
            rr *= SEMITONE if n_ > 0 else 1 / SEMITONE
        if abs(rr - ratio(n_)) > 1e-12 or abs(12 * math.log2(ratio(n_)) - n_) > 1e-9:
            errs.append(f"ratio at {n_} semitones: repeated multiplication and 12 x log2 disagree")
        if abs(float(EX_SLICE_S) / ratio(n_) * ratio(n_) - float(EX_SLICE_S)) > 1e-12:
            errs.append("duration x ratio must return the slice length")
    if abs(ratio(7) * ratio(5) - ratio(12)) > 1e-12 or abs(ratio(-5) * ratio(5) - 1) > 1e-12 or abs(ratio(7) * ratio(-12) - ratio(-5)) > 1e-12 or r4(ratio(7) * ratio(5)) != "2.0000":
        errs.append("intervals add and ratios multiply: +7 then +5 = +12 (1.4983 x 1.3348 = 2.0000); +12 then -12 = 1")
    if [r1(HUM_HZ * ratio(n_)) for n_ in PITCHES] != ["100.0", "133.5", "149.8", "200.0", "237.8", "252.0", "267.0", "299.7", "400.0"]:
        errs.append("a 200 Hz example hum at each offset")
    if [r4(float(EX_SLICE_S) / ratio(n_)) for n_ in PITCHES] != ["0.7500", "0.5619", "0.5006", "0.3750", "0.3153", "0.2976", "0.2809", "0.2503", "0.1875"]:
        errs.append("a 0.375 s slice played at each ratio: 0.7500, 0.5619, 0.5006, 0.3750, 0.3153, 0.2976, 0.2809, 0.2503, 0.1875 s")
    if [INTERVALS[12], INTERVALS[7], INTERVALS[-5]] != ["octave up", "fifth up", "fourth down"]:
        errs.append("interval names: 12 = octave, 7 = fifth, -5 = fourth down")
    # ---- Logic wording: newer tools are hedged
    for nm, txt in LOGIC_REF:
        if any(w in txt for w in ("Session Player", "Quick Sampler", "Slice mode", "Flex Time", "Step Sequencer", "Drum Machine Designer", "reverse option")) and "if your version" not in txt.lower():
            errs.append(f"Logic reference '{nm}' must hedge a newer tool with 'if your version'")
    joined = " ".join(t for _, t in LOGIC_REF)
    for w in ("Quick Sampler", "Slice", "transient", "equal", "manual", "Piano Roll", "Flex Time", "Drummer", "Loop Browser", "Bounce", "Mixer", "record-enable", "semitone", "reverse"):
        if w.lower() not in joined.lower():
            errs.append(f"the Logic quick reference must name {w}")
    # ---- the worked example
    if EX_BPM != 120 or EX_BAR_S != 2 or EX_STEP_S != Fraction(1, 8) or PHRASE != 3 or EX_SLICE_S != Fraction(3, 8):
        errs.append("the example: 120 BPM, 2 s per bar, 0.125 s per step, a 3-second hum, 0.375 s slices")
    for need in ("120 BPM", "240 ÷ 120 = 2 seconds", "15 ÷ 120 = 0.125 seconds", "3 seconds long", "3 ÷ 8 = 0.375 seconds", "exactly 3 steps", "6, 6, 6 and 8 hits, 26 in all", "4 × 2 = 8 seconds",
                 "slice 1 up 12 semitones (× 2.000)", "slice 3 up 7 (× 1.498)", "slice 5 down 5 (× 0.749)", "16 bars = 32 seconds", "bars 1 to 4", "bars 5 to 8", "bars 9 to 12", "bars 13 to 16"):
        if need not in EX_STRONG:
            errs.append(f"the clear plan must say '{need}'")
    if PITCH_USED != [(1, 12), (3, 7), (5, -5)]:
        errs.append("pitch choices of the example: slice 1 +12, slice 3 +7, slice 5 -5")
    # ---- no forbidden themes in any text a buyer reads
    allt = " ".join([THEME, BUILD_NOTE, OVERVIEW, " ".join(GOALS), " ".join(f"{a} {b}" for a, b in VOCAB), " ".join(REQS), " ".join(STEPS), " ".join(TIPS), " ".join(CHECK),
                     " ".join(d for _, ds in RUBRIC for d in ds), TN_REINFORCES, " ".join(STRUGGLES), VAR_EASY, VAR_HARD, " ".join(f"{a} {b}" for a, b in RESOURCES), TN_NOTE,
                     " ".join(GRADING), " ".join(d["do"] for d in PACING), SONG_NOTE, VOICE_NOTE, " ".join(t for _, t in LOGIC_REF), EX_STRONG, EX_NOTE, " ".join(EX_QUESTIONS),
                     " ".join(" ".join((s[2], s[3], s[4])) for s in SLIDES)]).lower()
    for w in FORBIDDEN_WORDS:
        if re.search(rf"\b{re.escape(w.strip())}\b", allt):
            errs.append(f"no alcohol, religious or holiday wording in a secular kit: '{w.strip()}'")
    for w in ("colour", "favour", "centre", "licence", "grey", "metre ", "organis", "recognis", "practise", "analyse", "whilst", "milli-second", "equalis", "normalis", "behaviour", "sulph"):
        if w in allt:
            errs.append(f"US spelling: '{w}'")
    for w in ("qa ", "inspector", "verified by", "--check", "gen.py"):
        if w in allt.replace("verified before", ""):
            errs.append(f"internal wording in buyer-facing text: '{w}'")
    # ---- slides: no truncated bullets, side lines or notes; page numbers in notes are pages that exist and fit
    for i, s in enumerate(SLIDES, start=1):
        for b in [x.strip() for x in s[3].split("|") if x.strip()] if s[1] != "pic" else []:
            if truncated(b):
                errs.append(f"slide {i} bullet looks truncated: '{b}'")
        if s[1] == "listen" and len([x for x in s[3].split("|") if x]) != 5:
            errs.append(f"slide {i} (listen): head, teacher line and three questions")
    for k, lines in SIDE.items():
        for b in lines:
            if truncated(b) or b.endswith(".") or len(b) > 46:
                errs.append(f"side line for '{k}' looks truncated or has a stop or is too long: '{b}'")
    for i, s in enumerate(SLIDES, start=1):
        for m in re.finditer(r"\bpages? (\d+)\b", s[4]):
            if int(m.group(1)) not in {pg(k) for k in PLAN}:
                errs.append(f"slide {i} notes name page {m.group(1)}, which does not exist")
    for need, key in ((f"page {pg('slicemap')}", 4), (f"page {pg('record')}", 4), (f"page {pg('timing')}", 5), (f"page {pg('slicemap')}", 6), (f"page {pg('logicref')}", 6),
                      (f"page {pg('record')}", 7), (f"page {pg('logicref')}", 8), (f"page {pg('slicemap')}", 8), (f"page {pg('pattern')}", 9), (f"page {pg('pitch')}", 10),
                      (f"page {pg('drums')}", 11), (f"page {pg('arrange')}", 12)):
        if need not in SLIDES[key][4]:
            errs.append(f"slide {key + 1} notes must name {need}")
    for i, s in enumerate(SLIDES, start=1):
        errs += step_ref_errors(" ".join((s[2], s[3], s[4])), f"slide {i}")
    if [s[0] for s in SLIDES] != [1] * 8 + [2] * 3 + [3] * 6 or SLIDES[3][1] != "days":
        errs.append("deck classes: slides 1-8 Class 1, 9-11 Class 2, 12-17 Class 3; slide 4 is the 'days' slide (it gets the Classes 1-3 badge)")
    if [d["slides"] for d in PACING] != [(1, 8), (9, 11), (12, 17)]:
        errs.append("pacing slide slots 1-8, 9-11, 12-17")
    # ---- the hero art, used whole: its pixels sit inside the viewBox with room to spare, and on all four edges of the file
    hp = os.path.join(HERE, "art", "hero.png")
    if not os.path.exists(hp):
        errs.append("art/hero.png is missing")
    else:
        x0, y0, x1, y1 = alpha_bbox(hp)
        if min(x0 - HX, y0 - HY, HX + HW - 1 - x1, HY + HH - 1 - y1) < 40:
            errs.append(f"hero art {x0, y0, x1, y1} is closer than 40 units to the viewBox {HX, HY, HX + HW, HY + HH}")
        if min(x0, y0, 1399 - x1, 1399 - y1) < 70:
            errs.append(f"hero art {x0, y0, x1, y1} comes within 5% of an edge of its file")
    if "--check" in sys.argv:
        errs += drawing_edge_errors() + footer_gap_errors()
    return errs


DECK_BOX_PAD_IN = 16 / 96        # --check: least padding below the last text line in any black box on a deck slide (16 px at the 1280 px slide scale)
NUM_WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7}


def layer_count_errors(flat, stext, notes):
    """Every stated layer count (PDF, deck, notes, UPLOAD.md, source strings) equals the number of rows in the arrangement drawing."""
    errs = []
    n = len(ARR_LAYERS)
    texts = [("PDF", " ".join(flat)), ("deck", " ".join(stext)), ("deck notes", " ".join(notes)), ("source", OVERVIEW + " " + " ".join(s[2] for s in SLIDES))]
    up = os.path.join(HERE, "UPLOAD.md")
    if os.path.exists(up):
        texts.append(("UPLOAD.md", open(up, encoding="utf8").read()))
    for label, t in texts:
        for m in re.finditer(r"\b(\d+|one|two|three|four|five|six|seven)\s+layers\b", t, re.I):
            w = m.group(1).lower()
            if (int(w) if w.isdigit() else NUM_WORDS[w]) != n:
                errs.append(f"{label}: '{m.group(0)}' but the arrangement drawing has {n} layers ({', '.join(ARR_LAYERS)})")
    if not any(re.search(rf"\b{n}\s+layers\b", t, re.I) for _, t in texts[:2]):
        errs.append(f"the layer count ({n}) is not stated in the PDF or the deck")
    return errs


COUNT_WORDS = {"eight": 8, "sixteen": 16}


def count_claim_errors(texts):
    """Every stated number of slices, steps, bars of a pattern or hits equals the drawing: 'N slices' is 8 or 16 (the two options), 'N steps' is 16, 64, or a slice's 3, 'N hits' matches a bar or the total."""
    errs = []
    allowed_hits = {*PAT_HITS, sum(PAT_HITS), 3, 2, 8, 13, 1, 12}
    for label, t in texts:
        for m in re.finditer(r"(?<!Page )(?<!p\. )\b(\d+|eight|sixteen)[ -]slices\b", t, ):
            w = m.group(1).lower()
            v = int(w) if w.isdigit() else COUNT_WORDS[w]
            if v not in (NSLICE, NSLICE_ALT, 7, 1):
                errs.append(f"{label}: '{m.group(0)}' but the kit has {NSLICE} (or {NSLICE_ALT}) slices")
        for m in re.finditer(r"(?<![\d.])(\d+) steps\b", t):
            v = int(m.group(1))
            if v not in (STEPS_BAR, PAT_BARS * STEPS_BAR, 3, 4, 2):
                errs.append(f"{label}: '{m.group(0)}' is not a count from the grid (16 a bar, 64 in 4 bars, 4 a beat, 3 a slice)")
        for m in re.finditer(r"\b(\d+) hits\b", t):
            if int(m.group(1)) not in allowed_hits:
                errs.append(f"{label}: '{m.group(0)}' is not a hit count from the patterns")
    return errs


def class_step_errors():
    """A deck slide badged Class 2 does not name the groove, the bass or the arrangement (the pacing table puts them in Class 3), and a Class 1 slide does not teach the chop pattern or pitch."""
    errs = []
    for i, s in enumerate(SLIDES, start=1):
        shown = " ".join((s[2], s[3] if s[1] != "pic" else ""))
        if s[0] == 2 and re.search(r"\bdrums?\b|\bbass\b|\barrang|\bmix\b|\bintro\b|\bdrop\b|\boutro\b|\bgroove\b", shown, re.I):
            errs.append(f"deck slide {i} is badged Class 2 but names groove, bass or arrangement content, which the pacing page assigns to Class 3")
        if s[0] == 1 and re.search(r"\bsemitone|\bchop pattern\b|\bstep grid\b|\bdrums?\b|\barrang", shown, re.I) and s[1] not in ("title", "bullets", "days"):
            errs.append(f"deck slide {i} is badged Class 1 but teaches Class 2 or 3 content")
    return errs


def dark_box_errors():
    """Rendered check on the deck PDF: for every black box (filled rectangle taller than 0.5 in) on every slide, the lowest text line inside it ends at least
    DECK_BOX_PAD_IN above the box's bottom edge (and no line crosses the edge)."""
    errs = []
    from pptx import Presentation
    from pptx.dml.color import RGBColor
    from pptx.enum.shapes import MSO_SHAPE
    prs = Presentation(D.P(f"{SLUG}-intro-deck.pptx"))
    pdf = D.P(f"{SLUG}-intro-deck.pdf")
    xml = subprocess.run(["pdftotext", "-bbox", pdf, "-"], capture_output=True, text=True, check=True).stdout
    pages = xml.split("<page ")[1:]
    if len(pages) != len(prs.slides):
        return [f"deck PDF has {len(pages)} pages but the deck has {len(prs.slides)} slides"]
    for i, (sl, pg_xml) in enumerate(zip(prs.slides, pages), start=1):
        words = [(float(a) / 72, float(b) / 72, float(c) / 72, float(d) / 72) for a, b, c, d in re.findall(r'xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)"', pg_xml)]
        for sh in sl.shapes:
            try:
                dark = sh.fill.type == 1 and sh.fill.fore_color.rgb == RGBColor(0, 0, 0)
            except Exception:
                continue
            x0, y0, w, h = (sh.left / 914400, sh.top / 914400, sh.width / 914400, sh.height / 914400)
            if not dark or h < 0.5 or sh.auto_shape_type not in (MSO_SHAPE.RECTANGLE, MSO_SHAPE.ROUNDED_RECTANGLE):    # step-number circles are not boxes
                continue
            bottom = y0 + h
            ins = [wd for wd in words if x0 <= (wd[0] + wd[2]) / 2 <= x0 + w and wd[3] > y0 and wd[1] < bottom]
            if ins and max(wd[3] for wd in ins) > bottom - DECK_BOX_PAD_IN:
                errs.append(f"deck slide {i}: text in the black box at y {y0:.2f} in ends {max(wd[3] for wd in ins):.2f} in, within {DECK_BOX_PAD_IN * 96:.0f} px of the box bottom {bottom:.2f} in")
    return errs


def dark_box_page_errors():
    """Rendered-DOM check on the product and preview PDFs: text inside a dark (black or very dark) box on a page stays at least 8 px above the box's bottom edge."""
    errs = []
    js = D.write("dark.js", r"""
const { chromium } = require('playwright');
const url = require('url');
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto(url.pathToFileURL(process.argv[2]).href, { waitUntil: 'load' });
  await page.evaluate(() => document.fonts.ready);
  await page.emulateMedia({ media: 'print' });
  const res = await page.evaluate(() => {
    const out = [];
    document.querySelectorAll('section.page').forEach((s, i) => {
      s.querySelectorAll('*').forEach(el => {
        const cs = getComputedStyle(el);
        const m = cs.backgroundColor.match(/rgba?\((\d+), (\d+), (\d+)(?:, ([\d.]+))?\)/);
        if (!m || (m[4] !== undefined && parseFloat(m[4]) < 0.5)) return;
        if (['TH', 'TD', 'TR', 'TABLE'].includes(el.tagName) || /\blv\b/.test(el.className)) return;
        if (+m[1] > 60 || +m[2] > 60 || +m[3] > 60) return;
        const r = el.getBoundingClientRect();
        if (r.height < 20 || r.width < 60) return;
        let low = -1e9;
        const w = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
        let n;
        while ((n = w.nextNode())) {
          if (!n.textContent.trim()) continue;
          const rg = document.createRange(); rg.selectNodeContents(n);
          Array.from(rg.getClientRects()).forEach(q => { if (q.bottom > low) low = q.bottom; });
        }
        if (low > -1e8) out.push({ page: i + 1, key: s.dataset.key, gap: r.bottom - low, cls: el.className });
      });
    });
    return out;
  });
  require('fs').writeFileSync(process.argv[3], JSON.stringify(res));
  await browser.close();
})().catch(e => { console.error(e); process.exit(1); });
""")
    for name, label in (("resource.html", "PDF"), ("preview.html", "PREVIEW")):
        html = os.path.join(D.build_dir(), name)
        if not os.path.exists(html):
            continue
        out = os.path.join(D.build_dir(), "dark-" + name + ".json")
        subprocess.run(["node", js, html, out], check=True, env=D.node_env())
        for o in json.load(open(out)):
            if o["gap"] < FOOT_GAP:
                errs.append(f"{label} page {o['page']} ({o['key']}): text in a dark box ({o['cls']}) ends {o['gap']:.1f}px above the box bottom (< {FOOT_GAP}px)")
    return errs


def verify_outputs(flat, stext, notes):
    errs = []
    alldeck = " ".join(stext + notes)
    txt = " ".join(flat)
    if "No audio" not in notes[0]:
        errs.append("deck slide 1 notes must say 'No audio'")
    for need in ("No audio, recordings, lyrics or melodies", "invented plan on paper", "Quick Sampler", "if your version", "slice", "transient", "semitone", "16th-note", "15 ÷ BPM",
                 "2^(n ÷ 12)", "× 2.000", "× 1.498", "× 0.749", "−12 to −6 dBFS", "your own voice", "copyright", "pattern", "hook", "intro", "drop", "outro", "reverse",
                 "Created with the help of digital and AI tools. Notation and answer keys are verified before release."):
        if need.lower() not in txt.lower():
            errs.append(f"PDF must say: '{need}'")
    if "What changed" in txt or "Kept as I wrote it" in txt or "my project menu" in txt or "my Digital Music Production" in txt:
        errs.append("ORIGINAL kit: no wording about changes to an owner's sheet")
    if "checked by hand" in txt or "handmade" in txt.lower() or "classroom-tested" in txt.lower() or "hand-checked" in txt.lower():
        errs.append("never claim hand checks or classroom testing for a new product")
    if GRADES_TEXT != "9–12" or "Grades 9–12" not in txt:
        errs.append("PDF: 'Grades 9–12'")
    for w in FORBIDDEN_WORDS:
        if re.search(rf"\b{re.escape(w.strip())}\b", (txt + " " + alldeck).lower()):
            errs.append(f"no alcohol, religious or holiday-specific wording in this product ({w.strip()})")
    for w in ("colour", "favour", "centre", "licence", "grey", "metre", "organis", "recognis", "practise", "analyse", "whilst", "milli-second", "colourful", "equalis"):
        if w in txt.lower().replace("greyscale", ""):
            errs.append(f"US spelling: '{w}' in the PDF")
    if re.search(r"\b(QA|inspector|gen\.py|--check)\b", txt + " " + alldeck):
        errs.append("internal QA wording in buyer-facing text")
    # ---- Step N on every page, in the deck PDF text, the deck notes and UPLOAD.md agrees with the project sheet
    for k in PLAN:
        t = flat[D.IX(k) - 1]
        errs += step_ref_errors(t, f"page {D.IX(k)} ({k})")
        found = {int(m.group(1)) for m in re.finditer(r"\bStep (\d+)\b", t)}
        if k in EXPECT_STEP and found != EXPECT_STEP[k]:
            errs.append(f"page {D.IX(k)} ({k}) should cite Step {sorted(EXPECT_STEP[k])}, cites {sorted(found)}")
        if k not in EXPECT_STEP and found:
            errs.append(f"page {D.IX(k)} ({k}) cites Step {sorted(found)} unexpectedly")
    errs += step_ref_errors(" ".join(stext), "deck slides")
    errs += layer_count_errors(flat, stext, notes)
    errs += count_claim_errors([("PDF", txt), ("deck", " ".join(stext)), ("deck notes", " ".join(notes))])
    errs += class_step_errors()
    errs += dark_box_errors()
    errs += dark_box_page_errors()
    errs += badge_errors(flat)
    import subprocess as sp

    def raw(key):
        return re.sub(r"\s+", " ", sp.run(["pdftotext", "-raw", "-f", str(D.IX(key)), "-l", str(D.IX(key)), D.files()["pdf"], "-"],
                                          capture_output=True, text=True, check=True).stdout).replace("- ", "-")
    # ---- the timing page prints every number
    rc = raw("timing")
    for bpm in TEMPOS:
        row = (f"{bpm} {dec(spb(bpm), 3)} {dec(step_len(bpm), 4)} {dec(bar_len(bpm), 3)} {dec(PAT_BARS * bar_len(bpm), 3)} {dec(ARR_BARS * bar_len(bpm), 3)} "
               f"{dec(slice_steps(PHRASE, NSLICE, bpm), 2)}")
        if row not in rc:
            errs.append(f"timing page: row '{row}' is not printed")
    for L in PHRASES:
        row = f"{exact(L)} s {exact(slice_len(L, NSLICE))} {exact(slice_len(L, NSLICE_ALT))} {dec(slice_steps(L, NSLICE, EX_BPM), 2)} {dec(slice_steps(L, NSLICE_ALT, EX_BPM), 2)}"
        if row not in rc:
            errs.append(f"timing page: hum row '{row}' is not printed")
    for need in ("Seconds per beat = 60 ÷ BPM", "Seconds per 16th-note step = 15 ÷ BPM", "Seconds per bar = 240 ÷ BPM = 16 steps", "15 ÷ 120 = 0.125 s per step", "240 ÷ 120 = 2 s per bar",
                 "Step 1: plan the hook", "5 rounds up", "0.1172", "3 ÷ 8 = 0.375 s at any tempo", "0.375 ÷ 0.125 = 3 steps at 120 BPM"):
        if need.lower() not in rc.lower():
            errs.append(f"timing page must say '{need}'")
    # ---- the recording page
    rr = raw("record")
    for need in ("Step 2: record the hum", "2 to 4 seconds", "no existing melody", "your OWN voice", "commercial recording", "−12 to −6 dBFS", "10 to 30 cm", "winter morning", "Take log"):
        if need.lower() not in rr.lower():
            errs.append(f"recording page must say '{need}'")
    # ---- the slice map page
    rs = raw("slicemap")
    for i in range(NSLICE):
        a = i * EX_SLICE_S
        row = f"{i + 1} start key + {i} {exact(a)} {exact(a + EX_SLICE_S)} {exact(EX_SLICE_S)}"
        if row not in rs:
            errs.append(f"slice map page: row '{row}' is not printed")
    for need in ("Step 3: slice and map", "if your version has it", "Transient", "Equal", "Manual", "3 ÷ 8 = 0.375", "0.1875 s each", "slices 1 to 8"):
        if need.lower() not in rs.lower():
            errs.append(f"slice map page must say '{need}'")
    # ---- the step grid page
    rp = raw("pattern")
    for b, hits in enumerate(PATTERN, start=1):
        used = ", ".join(str(u) for u in sorted({sl for _, sl in hits}))
        row = f"{b} {len(hits)} {used} {exact(hit_time(EX_BPM, b, 1))}"
        if row not in rp:
            errs.append(f"step grid page: row '{row}' is not printed")
    for need in ("Step 4: play the chop pattern", "64", "Hits per bar: 6, 6, 6 and 8, 26 in all", "(16 + 3) × 0.125 = 2.375 s", "BAR 1", "BAR 4", "6 hits", "8 hits", "SLICE 8", "My pattern"):
        if need.lower() not in rp.lower():
            errs.append(f"step grid page must say '{need}'")
    # ---- the pitch page
    rt = raw("pitch")
    for nn in PITCHES:
        r = ratio(nn)
        row = f"{sgn(nn)} {INTERVALS[nn]} {r3(r)} {r1(HUM_HZ * r)} {r4(float(EX_SLICE_S) / r)}"
        if row not in rt:
            errs.append(f"pitch page: row '{row}' is not printed")
    for need in ("Step 5: pitch and flip", "2^(n ÷ 12)", "× 2.000", "× 1.498", "× 0.749", "1.4983 × 1.3348 = 2.0000", "12 × log2(2) = 12", "Reverse", "Time-stretch", "if your version has them", "ROOT"):
        if need.lower() not in rt.lower():
            errs.append(f"pitch page must say '{need}'")
    # ---- groove and bass, arrangement
    rd = raw("drums")
    for b, s in enumerate(BASS, start=1):
        row = f"{b} {sgn(s)} {r3(ratio(s))}"
        if row not in rd:
            errs.append(f"groove page: bass row '{row}' is not printed")
    for need in ("Step 6: groove, arrange and mix", "KICK · 3", "SNARE · 2", "HAT · 8", "13 drum hits", "(5 − 1) × 0.125 = 0.5 s", "(13 − 1) × 0.125 = 1.5 s"):
        if need.lower() not in rd.lower():
            errs.append(f"groove page must say '{need}'")
    ra = raw("arrange")
    for nm, a, b in ARR_SECTIONS:
        layers = [r for r, spans in ARR_ROWS if any(x <= b and a <= y for x, y in spans)]
        row = f"{nm.title()} {a}–{b} {exact(hit_time(EX_BPM, a, 1))} {exact(hit_time(EX_BPM, b + 1, 1))} {', '.join(x.lower() for x in layers)}"
        if row not in ra:
            errs.append(f"arrangement page: row '{row}' is not printed")
    for t in TEMPOS:
        row = f"{t} {dec(ARR_BARS_ALT * bar_len(t), 3)} {dec(ARR_BARS * bar_len(t), 3)}"
        if row not in ra:
            errs.append(f"arrangement page: length row '{row}' is not printed")
    for need in ("Step 6: groove, arrange and mix, continued", "5 layers", "four sections of 4 bars", "16 bars × 2 s = 32 s", "SECONDS", "INTRO · bars 1–4", "DROP · bars 9–12"):
        if need.lower() not in ra.lower():
            errs.append(f"arrangement page must say '{need}'")
    rm = raw("mix")
    if "Step 6: groove, arrange and mix, finished" not in rm or "0 dBFS" not in rm:
        errs.append("mix page: Step 6 and the 0 dBFS line")
    # ---- the worked example prints its numbers
    re1 = raw("example") + " " + raw("example2")
    for i in range(NSLICE):
        a = i * EX_SLICE_S
        row = f"{i + 1} {exact(a)} {exact(a + EX_SLICE_S)} {exact(EX_SLICE_S)} {fmt(slice_steps(PHRASE, NSLICE, EX_BPM))} {slice_hits(i + 1)}"
        if row not in re1:
            errs.append(f"worked example: slice row '{row}' is not printed")
    for b, hits in enumerate(PATTERN, start=1):
        row = f"{b} {len(hits)} {exact(hit_time(EX_BPM, b, 1))} {exact(hit_time(EX_BPM, b + 1, 1))}"
        if row not in re1:
            errs.append(f"worked example: bar row '{row}' is not printed")
    for sl, nn in PITCH_USED:
        row = f"{sl} {sgn(nn)} {r3(ratio(nn))} {r4(float(EX_SLICE_S) / ratio(nn))}"
        if row not in re1:
            errs.append(f"worked example: pitch row '{row}' is not printed")
    for need in ("15 ÷ 120 = 0.125 s", "3 ÷ 8 = 0.375 s", "0.375 ÷ 0.125 = 3 steps", "0.375, 0.75, 1.125, 1.5, 1.875, 2.25, 2.625 seconds", "6, 6, 6 and 8 hits, 26 in all", "4 × 2 = 8 seconds", "(16 + 3) × 0.125 = 2.375 s",
                 "0.1875 s at +12", "0.5006 s at −5", "16 bars × 2 s = 32 s", "outro at 24 s", "The hits in the last column add up to 26"):
        if need.lower() not in re1.lower():
            errs.append(f"worked example must say '{need}'")
    up = open(os.path.join(HERE, "UPLOAD.md"), encoding="utf8").read()
    errs += step_ref_errors(up, "UPLOAD.md")
    errs += count_claim_errors([("UPLOAD.md", up)])
    if "Grades 9-12" not in up or "`9th-grade`, `10th-grade`, `11th-grade`, `12th-grade`" not in up:
        errs.append("UPLOAD.md: grades 9-12 in the description and section 3")
    if "no audio" not in up.lower() or "Open question" not in up or "Timing numbers" not in up or "Sources and credits" not in up:
        errs.append("UPLOAD.md: must say no audio is included, record the timing numbers checked, the sources and the open questions")
    for need in ("Semitone", "Sixteenth note", "Sampler (musical instrument)", "Quick Sampler Slice mode", "could not", "musicstudioinsights", "musosoup", "10 to 30 cm", "not from any source"):
        if need not in up:
            errs.append(f"UPLOAD.md sources and credits must name: {need}")
    m = re.search(r"= 1 cover \+ (\d+) teacher \+ (\d+) student \+ 1 terms page", up)
    if not m or 2 + int(m.group(1)) + int(m.group(2)) != len(PLAN):
        errs.append("UPLOAD.md: the page-count list (1 cover + teacher + student + 1 terms) must total the PDF's pages")
    if m and (int(m.group(1)) != D.IX("example2") - 1 or int(m.group(2)) != D.IX("reflect") - D.IX("timing") + 1):
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
    for banned in ["Billie", "Beatles", "Daft", "Skrillex", "Disney", "Radiohead", "Billboard", "Ro" + "land", "Bensound", "Able" + "ton "]:
        if banned in alldeck or banned in txt:
            errs.append(f"must not name artists, albums, songs, sites, services or other brands ({banned})")
    for brand in ("Shure", "Sound on Sound", "MusicRadar", "Wikipedia", "musicstudioinsights", "musosoup", "Apple Support"):
        if brand in alldeck or brand in txt:
            errs.append(f"buyer-facing pages and slides must not name a source site or brand ({brand}); sources are listed in UPLOAD.md")
    # deck: no truncated bullet reaches the slides; every class badge is true
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
    for i, s in enumerate(prs.slides, start=1):
        badges = [sh.text_frame.text.strip() for sh in s.shapes if sh.has_text_frame and abs(sh.left / 914400 - 11.18) < 0.01 and abs(sh.top / 914400 - 0.3) < 0.01 and sh.text_frame.text.strip()]
        want = f"CLASSES 1–{CLASSES}" if SLIDES[i - 1][1] == "days" else f"CLASS {SLIDES[i - 1][0]}"
        if SLIDES[i - 1][1] == "title":
            continue
        if badges != [want]:
            errs.append(f"deck slide {i}: class badge {badges}, expected {want}")
    # deck slides: nothing above the footer rule ends within FOOT_GAP px (96 per inch) of it
    for i, s in enumerate(prs.slides, start=1):
        rule = min((sh.top for sh in s.shapes if sh.top / 914400 > 6.9 and sh.height / 914400 < 0.05), default=None)
        if rule is None:
            continue
        for sh in s.shapes:
            if sh.top < rule and (rule - (sh.top + sh.height)) / 914400 * 96 < FOOT_GAP and sh.top / 914400 < 6.9:
                errs.append(f"deck slide {i}: a shape ends {(rule - (sh.top + sh.height)) / 914400 * 96:.1f}px above the footer rule (< {FOOT_GAP}px)")
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
    return ("seconds per beat = 60 / BPM, per 16th-note step = 15 / BPM (0.125 s at 120 BPM) and per bar = 240 / BPM (16 steps) recomputed exactly (fractions) and by an independent float method at six tempos; "
            "4-bar, 8-bar and 16-bar lengths (960, 1920 and 3840 / BPM); slice length = hum length / slices (3 s in 8 slices = 0.375 s = 3 steps at 120 BPM; 16 slices = 0.1875 s; hums of 2 to 4 s), every slice start and end "
            "exact and float; hit times ((bar - 1) x 16 + (step - 1)) x 15 / BPM; the model chop pattern (6, 6, 6 and 8 hits = 26, one hit per step, every slice used) counted from the data and again in the drawn step grid "
            "(512 cells, 26 hits, hits per bar from the x positions), the waveform's 7 slice lines, the keyboard's 8 marked keys, the drum groove (kick 3, snare 2, hat 8 = 13, drawn the same), the bass plan, the 16-bar "
            "arrangement (5 layers, 4 sections, 32 s at 120 BPM); the pitch table (ratio = 2^(n/12): +12 = 2.000, +7 = 1.498, -5 = 0.749; repeated multiplication and 12 x log2 agree; intervals add and ratios multiply; "
            "slice length / ratio); every 'Step N' agrees with the project sheet on pages, slides, notes and UPLOAD.md; class badges agree with the pacing page, and the deck's 'three classes' slide carries Classes 1-3; "
            "Class 2 slides teach no Class 3 content; every stated slice, step, hit and layer count equals the drawing; every drawing renders alone on a transparent ground with no ink at its edges; hero art inside its viewBox "
            "and 5% from the file's edges; rendered-DOM footer gap on every page and deck slide, and clear space under text in dark boxes on pages and slides; no truncated slide bullets; edges of cover.png and previews clear; "
            "no audio, lyrics, melodies, alcohol, religious or holiday wording or student work; no source site named on a buyer page; grades 9-12; tags and subjects are not headings; no 'what changed' page (ORIGINAL).")


# ================================================================ UPLOAD.md (written by gen.py so every number matches the build)
def write_upload():
    np_, ns = len(PLAN), len(SLIDES)
    n_teacher = (PLAN.index("example2") + 1) - 1
    n_student = (PLAN.index("reflect") + 1) - (PLAN.index("timing") + 1) + 1
    assert 2 + n_teacher + n_student == np_, "page-count list must total the PDF"
    nt = len(LISTING_TITLE)
    desc = (f"{DESC_START} students record ONE short hummed phrase of their own voice (2 to 4 seconds, no words, no existing melody) and chop it into a hook in Quick Sampler (if their version has it). "
            f"They slice the hum into 8 or 16 pieces, assign the slices to keys, play a 4-bar chop pattern on a 16-step grid, pitch pieces by semitone, try a reversed slice, add a simple drum groove and bass, "
            f"and build an 8- or 16-bar arrangement with an intro, a hook, a drop and an outro. Timing math runs through every step: one bar of 4/4 = 240 ÷ BPM seconds, one 16th-note step = 15 ÷ BPM seconds "
            f"(0.125 seconds at 120 BPM), and a 3-second hum cut into 8 equal slices gives slices of 0.375 seconds. Pitch is arithmetic too: the ratio for n semitones is 2^(n/12), so +12 is × 2.000, +7 is × 1.498 and −5 is × 0.749. "
            f"The theme is a winter morning (wind at the window, boots on snow, a kettle starting to sing) as the hum's inspiration. This Winter Vocal Chop project takes {CLASSES} class periods "
            f"(the pacing guide also shows two and four) and is an original Hudson Beat project; the steps are written for Logic Pro, while the ideas (slices, step grids, semitones, arrangement) carry over to GarageBand and other music software.\n\n"
            f"WHAT'S INCLUDED (ZIP: {np_}-page PDF = 1 cover + {n_teacher} teacher + {n_student} student + 1 terms page, plus {ns}-slide intro deck as .pptx and PDF)\n"
            f"• Teacher pages: how to use, project overview, setup, a {CLASSES}-class pacing guide with the deck slides for each class, "
            f"two pages of teacher notes (struggles, variations, resources, grading), a Logic quick reference and a two-page worked example (an invented hook at 120 BPM: "
            f"a 3-second hum, 8 slices of 0.375 seconds, a 4-bar pattern with 26 hits, three pitch choices and a 16-bar arrangement of 32 seconds) ({n_teacher} pages)\n"
            f"• Student pages: a timing page (seconds per beat, step and bar at six tempos, 4-bar and 16-bar lengths, and slice lengths for hums of 2 to 4 seconds), a recording checklist with a copyright note and take log, "
            f"a slice map (a waveform with slice lines, a keyboard map and a slice table), a 4-bar chop pattern step grid with a blank grid to fill in, a pitch table (semitone offsets with ratios), a drum groove and bass page, "
            f"an arrangement map with 5 layers, a mix checklist, the 3-page project sheet (overview, goals, vocabulary, requirements, steps, tips, submission checklist), the /{RUBRIC_TOTAL} rubric, a vocabulary page, a feedback planner and a reflection page ({n_student} pages)\n"
            f"• Teacher-presented intro deck, {ns} slides with speaker notes on every slide: a think-and-share hook, what the project is, the slices, the timing math, the keyboard map, the recording checklist, "
            f"chopping in Quick Sampler, the step grid, pitch by semitone, groove and bass, the arrangement, what to turn in and the rubric\n\n"
            f"THE THREE CLASS PERIODS\n"
            f"• Class 1: hook; the timing math and a tempo; recording the hum; slicing it and mapping the slices\n"
            f"• Class 2: finish the slices; play a 4-bar chop pattern on the step grid; pitch slices by semitone and try a reversed slice\n"
            f"• Class 3: add a drum groove and bass, arrange 8 or 16 bars, mix, bounce, present and reflect\n\n"
            f"WHAT STUDENTS LEARN\n"
            f"• Timing math: seconds per bar in 4/4 = 240 ÷ BPM; seconds per step = 15 ÷ BPM; 16 steps make a bar; slice length = hum length ÷ number of slices\n"
            f"• Sampling: recording a clean source in their own voice, cutting it into slices (transient, equal or manual, if your version has them), playing slices from keys and reading a pattern as a step grid\n"
            f"• Pitch: 12 semitones make an octave; ratio = 2^(n/12); intervals add and ratios multiply\n"
            f"• Arranging: intro, hook, drop and outro, layers that build, and a mix that keeps the chops clear\n\n"
            f"GOOD TO KNOW\n"
            f"• There is no audio in this resource and no student work. No melody, song or lyrics are printed. Students record their OWN voice; the kit tells them not to sample commercial recordings. They make every sound themselves in Logic Pro\n"
            f"• Requires Logic Pro on a Mac with Quick Sampler. A microphone is recommended, and a classmate can hum with permission; nobody has to read music. Where a control may differ between versions, the pages say \"if your version has it\" and describe controls generically\n"
            f"• All recording levels and mixing numbers are starting points to set by ear, not rules\n"
            f"• Rubric: 5 categories scored 1-5, /{RUBRIC_TOTAL}; the final grade is the average of the student's and the teacher's score\n"
            f"• Grades 9-12; music technology or music production classes\n"
            f"• The deck uses the free Oswald and Source Sans 3 fonts (built into Google Slides); install them for PowerPoint or Keynote, or present "
            f"the PDF copy, which shows the intended look\n"
            f"• Every student page prints well in black and white\n\n"
            f"Logic Pro and Quick Sampler are products of Apple Inc., named only to describe compatibility. This resource is not affiliated with Apple.\n\n"
            f"Part of the Hudson Beat Logic Pro project series\n"
            f"Please leave a rating: you earn TpT credits for feedback, and it helps other teachers find this\n"
            f"Follow the Hudson Beat store for new music resources every week\n\n"
            f"{D.DISCLOSURE_NEW}")
    tbl = "; ".join(f"{b} BPM: {dec(step_len(b), 4)} s per step, {dec(bar_len(b), 3)} s per bar, 16 bars = {dec(ARR_BARS * bar_len(b), 3)} s" for b in TEMPOS)
    pit = "; ".join(f"{sgn(n_)} = x{r3(ratio(n_))}" for n_ in PITCHES)
    md = f"""# UPLOAD: Winter Vocal Chop, original Logic Pro project (TpT 083)

These fields follow the order of TpT's "Add a resource" form. `tools/tpt.js publish` reads the title and description from the code blocks under 1 and 2, and everything else from `tpt.json`. This file is written by `gen.py`; edit the text there.

**Files to attach**
- Resource (digital download): `{SLUG}.zip`. It holds three files in a folder "{ZIP_DIR}":
  - `{SLUG}.pdf`: the teacher and student resource, {np_} pages, US Letter portrait.
  - `{SLUG}-intro-deck.pptx`: the teacher-presented intro deck, {ns} slides (16:9), speaker notes and a Class badge on every slide (the three-classes slide carries "Classes 1-3").
  - `{SLUG}-intro-deck.pdf`: a PDF copy of the deck, {ns} pages.
- Thumbnails, in this order: `cover.png`, `preview-1.png`, `preview-2.png`, `preview-3.png` (all 2000 × 2000).
- Preview file: `{SLUG}-PREVIEW.pdf`, 4 watermarked pages.

TpT takes one product file, so the PDF, the .pptx and the deck PDF go up together as the ZIP (`files.product` in tpt.json; `zip_contents` lists what is inside). **No audio, video, lyrics, recordings, presets, screenshots, student work or Logic sessions are in the ZIP.**

**Page count, adding up to the PDF:** 1 cover + {n_teacher} teacher + {n_student} student + 1 terms page = {np_} pages; plus {ns} slides = {np_ + ns} for TpT's "Number of pages or slides".

## 1. Title

```
{LISTING_TITLE}
```
({nt} characters; the limit is 80.) The title leaves out Winter, Holiday and Christmas because TpT's Seasonal Titles notice blocked a holiday-named title on 027 (see 067, 070, 076 and 080 for the working format); "Vocal Chop Project" and "Quick Sampler, Slices, Hook" are the plain search phrases. "Logic Pro" is in the first 30 characters as a compatibility word.

## 2. Description

```
{desc}
```

## 3. Grades

9th, 10th, 11th, 12th (`9th-grade`, `10th-grade`, `11th-grade`, `12th-grade` in tpt.json), as tpt/METADATA-GUIDE.md prescribes for every music-production item.

## 4. Subjects and tags

- Subjects in tpt.json: Music; Computer Science - Technology; Music Composition (all three are in `tpt/SUBJECT-OPTIONS.json` and none is a heading)
- Tags in tpt.json: {", ".join(TAGS)} (four exact entries of `tpt/TAG-OPTIONS.json`, checked with `tools/tpt-validate.py`; the limit is 6). "Holiday" and "Student Practice" are headings and are not used; "Winter" is a real entry.
- Formats: PDF (add PowerPoint or ZIP if TpT offers it)
- Answer key: left out of tpt.json (there is none; the worked example is a model)

## 5. Resource type

- Projects
- Unit Plans
- PowerPoint Presentations

## 6. Standards (optional)

National Core Arts Standards, Music (Music Technology, high school): MU:Cr1.1, MU:Cr2.1, MU:Pr6.1, MU:Re7.2. Tag only if it matches how the teacher uses it.

## 7. Price

**${PRICE}** (paid), multiple-license price ${PRICE}. The price the queue set, at the low end of the $8-12 holiday Logic kit range, for a kit with {np_} pages + {ns} slides, a timing page, a recording checklist, a slice map, a 4-bar step grid with a blank grid, a pitch table, a groove and bass page, an arrangement map and a two-page worked example, listed in December.

## 8. Free or paid / free preview pages

Paid. Preview PDF (4 watermarked pages): the {CLASSES}-class pacing guide, the slice map, the 4-bar step grid and the pitch table. "Number of pages or slides" is {np_ + ns} ({np_} pages + {ns} slides).

## 9. Sources and credits

All sources were fetched on 25 Nov 2026 unless a line says "could not". Recording and mixing numbers are starting points, and the product says so.

- **Semitone, octave and the ratio 2^(1/12).** English Wikipedia, "Semitone" (page read): the equal-tempered semitone is 2^(1/12), about 1.05946 (100 cents), "one twelfth of an octave"; 12 semitones per octave; an octave is a 2:1 ratio. The page does not give the fifth's decimal: 2^(7/12) = 1.49831 and every other ratio in the table are arithmetic, computed in `gen.py --check` by repeated multiplication of 2^(1/12) and again with 12 x log2(ratio) = n. Pitch table: {pit}. The interval names (octave, fifth, fourth, thirds) are standard music-theory vocabulary, not sourced here.
- **A 16th note and steps per bar.** English Wikipedia, "Sixteenth note" (page read): a sixteenth note is 1/16 of a whole note, half an eighth note. The page does not state the counts per beat or per bar; 4 per quarter-note beat and 16 per bar of 4/4 follow from the definition. Seconds per beat = 60 / BPM, per step = 15 / BPM and per bar = 240 / BPM, and every table, are arithmetic computed in `gen.py --check`, exactly with fractions and with an independent float method. At 120 BPM a step is 0.125 s.
- **Sampler, slicing and keys.** English Wikipedia, "Sampler (musical instrument)" (page read): a sampler is an electronic musical instrument that records and plays back samples; samples can include speech and other sounds; keyboard tracking shifts a sample's pitch in semitones relative to its center pitch. The page does not describe slicing by name.
- **Quick Sampler's Slice mode (transient, equal divisions, beat divisions, manual).** Apple, "Quick Sampler Slice mode in Logic Pro for Mac" (support.apple.com/guide/logicpro/slice-mode-lgcp18515788/mac): **could not read the page body** (the fetch returned only the User Guide's navigation); the three marker modes and the sensitivity and slice-count controls were seen only in a search summary. Apple's "Quick Sampler" overview page could not be read either. The kit therefore says "if your version has it", names the modes generically (transient, equal, manual), invents no menu paths and promises no key layout, and tells students to play each key and write down which slice it plays. Logic's command that converts an audio region to a sampler instrument was seen only as a table-of-contents entry in the User Guide; the kit hedges it too.
- **Voice peaks around −12 to −6 dBFS.** musicstudioinsights.com, "Best dB Level for Recording Vocals: Peaks & Headroom" (page read): loud vocal peaks between −12 and −6 dBFS when recording at 24-bit, as "a practical starting point, not a strict limit"; a take peaking at −12 dBFS can be raised later; a clipped take cannot be repaired by turning it down; 0 dBFS is the digital ceiling. musosoup.com, "How to Record Vocals at Home" (page read): average around −18 dBFS with peaks near −10 dBFS, so the sources differ; the kit calls −12 to −6 a starting point and says a quieter recording is safe.
- **Mic distance, pop filter, quiet room.** musosoup.com (page read): the microphone 10 to 30 cm from your mouth, a pop filter about 2 to 3 inches (5 to 8 cm) in front of the microphone, soft furnishings in a larger room. The kit says "about 10 to 30 cm is this kit\u2019s starting range" and "try two distances and listen", mentions a pop filter only as "if there is one", and gives no pop filter distance. A "hand's width" rule of thumb is not used because no page read states it. The Shure "vocal miking tips" page was fetched and returned no content about distance, so Shure is not cited.
- **Example values (not from any source).** The 3-second hum, the 120 BPM tempo, the model chop pattern (6, 6, 6 and 8 hits), which slices are pitched and by how much, the 200 Hz example hum, the drum groove (kick 3, snare 2, hat 8), the bass offsets (0, 0, −5, −7), the arrangement and every invented time are example values chosen for this kit and labeled as examples. The claim that a higher pitch plays a sample faster and so shortens it is how many samplers work, stated as "many samplers" and "if the sampler plays it faster", not as a fact about Quick Sampler.
- **No existing music.** Nothing is notated or printed. No songs, artists or recordings are named. Students record their own voice and are told not to sample commercial recordings.
- **Art:** the cover, previews and deck use the owner's pre-made art (`art/hero.png`: a studio microphone, a laptop showing an abstract waveform, monitors, headphones, an audio interface and a pad controller, no screen text), copied whole from `tpt/_art/next/winter-vocal-chop/`; logged in `tpt/_art/USAGE.md`. Everything else, including every number, table, grid, waveform and keyboard, is drawn or printed in code.
- **Fonts:** Oswald and Source Sans 3 (SIL OFL 1.1). Logic Pro and Quick Sampler are named only to describe compatibility.

## 10. Before you click publish

- [ ] **Needs QA approval first.** This is a new kit (not yet on TpT); the Manager releases it only after a QA `**Verdict: APPROVED**`. Season rule: listing no sooner than the 2-8 week window before winter allows.
- [ ] Cover and previews show "HUDSON BEAT" in type; PDF footers read "© 2026 Brian Lotze · Hudson Beat · For single-classroom use".
- [ ] No school name, logo, student names or work, audio, video, lyrics, melody, song title or Logic session anywhere (`gen.py --check` scans every output and every file in this folder).
- [ ] **Secular.** The theme is a winter morning as the hum's inspiration: no holiday imagery, no religious content, no alcohol imagery, no brands other than Logic Pro and Quick Sampler, no existing songs or recordings. `gen.py --check` fails on alcohol, religious and holiday words.
- [ ] **Timing numbers (all recomputed in `gen.py --check`, exactly with fractions and again with an independent float method).** Seconds per beat = 60 / BPM; per 16th-note step = 15 / BPM; per bar of 4/4 = 240 / BPM = 16 steps; 4 bars = 960 / BPM; 16 bars = 3840 / BPM. Six tempos: {tbl}. Slice length = hum length / slices: 3 s / 8 = 0.375 s = 3 steps at 120 BPM (2.25 steps at 90 BPM, 3.2 at 128 BPM); 3 s / 16 = 0.1875 s; hums of 2, 2.5, 3, 3.5 and 4 s give 0.25, 0.3125, 0.375, 0.4375 and 0.5 s in 8 slices. Hit time = ((bar − 1) × 16 + (step − 1)) × 15 / BPM: bar 2, grid step 4 at 120 BPM = 2.375 s. Rounding: seconds per beat, bar and section to 3 decimals, per step to 4, half up.
- [ ] **Pattern numbers (recomputed from the data and from the drawn grid).** The model pattern has 6, 6, 6 and 8 hits (26) on a grid of 4 × 16 = 64 steps and 8 lanes (512 cells), one hit per step, every slice used; hits per slice 5, 4, 4, 3, 2, 2, 3 and 3. The drum bar has kick 3, snare 2 and hat 8 hits (13). The arrangement has 5 layers and 4 sections of 4 bars; 16 bars at 120 BPM = 32 s (8 bars = 16 s).
- [ ] **Pitch numbers (recomputed).** Ratio = 2^(n/12): +12 = x2.000, +7 = x1.498, −5 = x0.749 (also −12 0.500, −7 0.667, +3 1.189, +4 1.260, +5 1.335); +7 then +5 is +12: 1.4983 × 1.3348 = 2.0000; a 0.375 s slice played at these ratios lasts 0.7500, 0.5619, 0.5006, 0.3750, 0.3153, 0.2976, 0.2809, 0.2503 and 0.1875 s (0.375 / ratio); a 200 Hz example hum becomes 100.0 to 400.0 Hz.
- [ ] **Original project.** Built with `ORIGINAL = True` in `tpt/_dmp2_common/dmp2.py` (like 031, 036, 053, 057, 061, 063, 067, 070, 076 and 080): no "what changed" page and the new disclosure line. The reflection page is the shared Reflection element, scored in the rubric's "Plan & Reflection" row. `dmp2.py` is unchanged; the deck's three-classes badge and the terms-page thank-you note are applied inside `gen.py`.
- [ ] **Logic Pro names to confirm on a Mac with a current Logic.** Quick Sampler and its slice mode (hedged; transient, equal, manual), converting an audio region to a sampler instrument (hedged), the Piano Roll with a 16th-note grid, Quantize, the Step Sequencer, Flex Time, the Drummer and Drum Machine Designer (all hedged), the Loop Browser, record-enable (R), the Mixer (X), Bounce (Command-B) and Compress in Finder. Whether Quick Sampler plays slices from neighboring keys in order, and where slice 1 starts, differs by version and is left for students to check.
- [ ] **Open questions for the owner:** (1) **Title.** No Winter, Holiday or Christmas in the title because of TpT's seasonal-title notice (see 1). (2) **Price.** ${PRICE}, as queued, the low end of the $8-12 range. (3) **Quick Sampler details.** Apple's Slice mode page could not be read in full, so the kit stays generic; say if you want a Mac check before release. (4) **Levels.** −12 to −6 dBFS rests on one read page, and a second read page gives a different target (peaks near −10 dBFS), so it is worded as a starting point. (5) **Drum and bass sounds.** The kit tells students to use only sounds that come with Logic or that they made; it makes no licensing statement (see the Apple royalty-free-content note in 080's QA.md). (6) **Classes.** Three periods; Class 1 holds the recording and the slicing, so the pacing page shows how to use two or four.
"""
    with open(os.path.join(HERE, "UPLOAD.md"), "w", encoding="utf8") as f:
        f.write(md)

def thank_you_terms(n, wm=False):
    """The shared terms page plus a thank-you and rating note above the disclosure line (the shared builder stays untouched)."""
    html = D.terms_page(n, wm)
    note = ('<div class="box acc-b" style="margin:4pt 0 6pt;padding:6pt 10pt"><span class="k">Thank you, and please rate this resource</span>'
            '<p style="margin:0;font-size:10.4pt;line-height:1.38">Thank you for choosing this project for your students. If you leave a rating on Teachers Pay Teachers you earn TpT credits for feedback, '
            'and it helps other teachers find the resource. Follow the Hudson Beat store for new music resources every week.</p></div>')
    marker = f'<p class="small">{D.DISCLOSURE}</p>'
    assert marker in html, "terms page marker not found"
    return html.replace(marker, note + marker)


PAGES["terms"] = thank_you_terms


# the deck's "three classes" slide covers all classes, so its badge reads Classes 1-3 (applied after the shared deck builder runs; the shared builder stays untouched)
_orig_build_deck = D.build_deck


def _build_deck_with_true_badges(img):
    _orig_build_deck(img)
    from pptx import Presentation
    path = D.P(f"{SLUG}-intro-deck.pptx")
    prs = Presentation(path)
    for i, s in enumerate(prs.slides, start=1):
        if SLIDES[i - 1][1] != "days":
            continue
        done = 0
        for sh in s.shapes:
            if sh.has_text_frame and abs(sh.left / 914400 - 11.18) < 0.01 and abs(sh.top / 914400 - 0.3) < 0.01 and sh.text_frame.text.strip().upper().startswith("CLASS"):
                sh.text_frame.paragraphs[0].runs[0].text = f"CLASSES 1–{CLASSES}"
                done += 1
        assert done == 1, f"slide {i}: class badge not found"
    prs.save(path)


D.build_deck = _build_deck_with_true_badges

# the "listen" slide's black box: the shared builder leaves an empty subtitle line between the heading and the teacher line and sets the teacher line on the box's bottom edge.
# Re-lay it out here (the shared builder stays untouched): heading, a tight gap, the body, then DECK_BOX_PAD_IN of padding below the last line.
_build_deck_shared = D.build_deck


def _build_deck_with_listen_box(img):
    _build_deck_shared(img)
    from pptx import Presentation
    from pptx.util import Inches
    path = D.P(f"{SLUG}-intro-deck.pptx")
    prs = Presentation(path)
    for i, s in enumerate(prs.slides, start=1):
        if SLIDES[i - 1][1] != "listen":
            continue
        shapes = list(s.shapes)
        box = [sh for sh in shapes if abs(sh.left / 914400 - 0.6) < 0.01 and abs(sh.top / 914400 - 2.0) < 0.01 and abs(sh.height / 914400 - 2.0) < 0.01]
        sub = [sh for sh in shapes if sh.has_text_frame and abs(sh.top / 914400 - 2.82) < 0.01 and not sh.text_frame.text.strip()]
        body = [sh for sh in shapes if sh.has_text_frame and abs(sh.top / 914400 - 3.38) < 0.01 and sh.text_frame.text.strip()]
        assert len(box) == 1 and len(sub) == 1 and len(body) == 1, f"slide {i}: listen box shapes not found"
        sub[0]._element.getparent().remove(sub[0]._element)
        body[0].top, body[0].height = Inches(2.78), Inches(0.62)       # two 18 pt lines, straight under the heading
        box[0].height = Inches(1.75)                                   # box bottom 3.75 in; last line ends near 3.4 in
    prs.save(path)


D.build_deck = _build_deck_with_listen_box


if __name__ == "__main__":
    if "--check" not in sys.argv:
        write_upload()
        D.deck_art = deck_art_transparent
    D.main(sys.modules[__name__])
