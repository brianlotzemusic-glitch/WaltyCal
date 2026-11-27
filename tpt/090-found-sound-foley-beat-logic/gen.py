#!/usr/bin/env python3
"""Logic Pro project kit: Gift Wrap Foley Beat (TpT 090): the teacher resource, the intro deck and the listing files.

    python3 gen.py            build everything into this folder (also writes UPLOAD.md)
    python3 gen.py --lowres   same, but square images at scale 1 and small page shots (self-check only; --check rejects it)
    python3 gen.py --check    verify content and layout: the tempo math for 4/4 (one beat = 60 / BPM s, one 16th-note step = 15 / BPM s, one bar = 240 / BPM s = 16 steps; 4 bars = 960 / BPM,
                              16 bars = 3840 / BPM; exact fractions and an independent float method; length tables at 80, 100 and 120 BPM), the swing arithmetic (a pair of steps split long:short r:1 delays the
                              second step by (r - 1) / (r + 1) of a step), the 6 sounds and their roles, the 4-bar 16-step pattern (hits per bar, per lane and in all, counted again in the step-grid drawing: hit
                              rectangles, cells, per-bar labels; hits on even steps), the 16-bar arrangement (6 layers, 4 sections, bars per layer, layers sounding per bar, counted again in the drawing), the
                              sound-role table drawing (6 rows, 6 icons, dots), the signal-chain drawing (5 stages, 4 arrows), the swing drawing, Step N references on every page, slide and UPLOAD.md, class badges
                              against the pacing page, count-vs-drawing (sounds, steps, hits, bars, layers), drawings (each rendered alone on a transparent ground: no ink within 4 px of its edge), the hero art,
                              files, page and slide counts, class slots, fonts, fit and overlap, dead space, footer gap (pages and deck slides), black-box padding (pages and deck slides), the edges of cover.png
                              and the previews, banned strings, tpt.json and UPLOAD.md

An ORIGINAL Hudson Beat project (dmp2.ORIGINAL = True, like 063 to 087). Students record 6 to 8 found sounds from safe household objects (paper, tape, boxes, tubes, a small bell: their own
recordings only), trim them, give each a drum-machine role, build a 4-bar, 16-step pattern, add swing and humanize (hedged), layer the sounds into a 16-bar arrangement and mix it. No audio
ships. The art on the cover, the previews and the deck is the owner's pre-made hero (art/hero.png), used whole. Everything else is drawn in code. The shared builder is ../_dmp2_common/dmp2.py (untouched).
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
SLUG = "found-sound-foley-beat"
TITLE = "Gift Wrap Foley Beat"
ACCENT = "#2F7FB8"          # this product's single accent: icy blue (a shade deeper than the art's #4FA3D9, so small labels read)
ACC_LIGHT = "#DCEBF6"
PRICE = "8.00"
CLASSES = 3
GRADES_TEXT = "9–12"
GRADE_SLUGS = ["9th-grade", "10th-grade", "11th-grade", "12th-grade"]
TAGS = ["Winter", "Project-based Learning", "Projects", "Activities"]     # exact entries of tpt/TAG-OPTIONS.json, none a heading
SUBJECTS = ["Music", "Music Composition", "Computer Science - Technology"]     # all in SUBJECT-OPTIONS.json, none a heading
ANSWER_KEY = None
LISTING_TITLE = "Logic Pro Found Sound Beat | Foley, Samples, Step Sequencer | High School"
DESC_START = "Found sound beat project for high school music technology:"
DESC_MUST = ["Gift Wrap Foley Beat", "Foley", "Step Sequencer", "16th-note", "15 ÷ BPM", "100 BPM", "no audio", "swing", "high-pass", "0.15"]
ZIP_DIR = "Gift Wrap Foley Beat - Hudson Beat"
ZIP_DATE = (2026, 11, 27, 12, 0, 0)
TYPE = "Original Project"
PROJ_LINE = "Music Technology | <i>Found Sound Beat</i> | 3 class periods"
DECK_STRAP = "Record it, trim it, play it"
REFLECT_ROW = "Plan &amp; Reflection"
# split so this file never contains them (the --check scan reads every file in this folder)
BANNED_EXTRA = ["Rud" + "olph", "Fro" + "sty", "Gri" + "nch", "Santa Claus " + "Is", "Jingle Bell " + "Rock", "Feliz " + "Navidad",
                "Mari" + "ah Carey", "Spoti" + "fy", "You" + "Tube", "Home " + "Alone", "Nin" + "tendo", "Ro" + "land",
                "Star " + "Wars", "Hans " + "Zimmer", "John " + "Williams", "Harry " + "Potter", "Pix" + "ar", "Lord of the " + "Rings",
                "Winter " + "Wonderland", "Let It " + "Snow", "Sleigh " + "Ride", "X" + "mas", "Times " + "Square", "Auld " + "Lang",
                "Ak" + "ai", "Ab" + "leton", "FL " + "Studio", "Sound" + "Cloud", "Tik" + "Tok", "Spl" + "ice", "Ser" + "um", "Scot" + "ch", "Sell" + "otape", "Ama" + "zon",
                "Hallm" + "ark"]

# ================================================================ page plan (teacher pages 2-10, student pages 11-24)
PLAN = ["cover", "howto", "overview", "setup", "pacing", "tn1", "tn2", "logicref", "example", "example2", "timing", "sounds", "roles", "pattern", "swing",
        "arrange", "mix", "proj1", "proj2", "proj3", "rubric", "vocab", "present", "reflect", "terms"]


def pg(k):
    return PLAN.index(k) + 1


# ================================================================ the arithmetic (exact fractions; all verified in --check)
TEMPOS = (80, 90, 100, 110, 120, 128)       # the timing table's rows
EX_BPM = 100                                # the worked example's tempo
LEN_TEMPOS = (80, 100, 120)                 # the length table's three tempos
LEN_BARS = (4, 8, 16, 32)
STEPS_BAR = 16                              # 16th-note steps in one bar of 4/4
BEATS_BAR = 4
PAT_BARS = 4                                # the pattern is 4 bars
ARR_BARS = 16                               # the arrangement
SEC_BARS = 4
SWING_RATIOS = (Fraction(1), Fraction(3, 2), Fraction(2), Fraction(3))      # long : short, as r : 1


def spb(bpm):
    """Seconds per beat = 60 / BPM."""
    return Fraction(60, bpm)


def bar_len(bpm):
    """Seconds per bar of 4/4 = 240 / BPM (four beats)."""
    return Fraction(240, bpm)


def step_len(bpm):
    """Seconds per 16th-note step = 15 / BPM (a quarter-note beat holds four steps)."""
    return Fraction(15, bpm)


def hit_time(bpm, bar, step):
    """Seconds from the start of the pattern to grid step `step` (1 to 16) of bar `bar`: ((bar - 1) x 16 + (step - 1)) x 15 / BPM."""
    return ((bar - 1) * STEPS_BAR + (step - 1)) * step_len(bpm)


def swing_delay_steps(r):
    """A pair of two steps (2 step lengths) split long:short = r:1 puts the second step at 2r/(r+1) steps instead of 1: it is late by (r - 1)/(r + 1) of a step."""
    return Fraction(2) * r / (r + 1) - 1


def rnd(x, nd):
    """Round half up (a 5 rounds up) to nd decimals, on exact fractions."""
    s = Fraction(10) ** nd
    return Fraction(math.floor(Fraction(x) * s + Fraction(1, 2)), 1) / s


def dec(x, nd):
    return f"{float(rnd(x, nd)):.{nd}f}".replace("-", "−")


def exact(x):
    """An exact decimal (the denominator has only the factors 2 and 5), with no trailing zeros: 3/20 -> 0.15."""
    x = Fraction(x)
    d = x.denominator
    while d % 2 == 0:
        d //= 2
    while d % 5 == 0:
        d //= 5
    assert d == 1, f"{x} is not a terminating decimal"
    return f"{float(x):.6f}".rstrip("0").rstrip(".")


def fmt(x):
    x = float(x)
    x = round(x + 1e-9, 4)
    return f"{x:.0f}" if x == int(x) else f"{x:g}"


def fs(x):
    """A fraction as text: 4/3, or 1 for a whole number."""
    x = Fraction(x)
    return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"


def sgn(n):
    return "0" if n == 0 else (f"+{n}" if n > 0 else f"−{-n}")


# ---- the six sounds: (name, icon, role, pitch 1-3, brightness 1-3, length 1-3, what to use, how to make it)
PITCH_W = {1: "LOW", 2: "MID", 3: "HIGH"}
BRIGHT_W = {1: "DULL", 2: "MEDIUM", 3: "BRIGHT"}
LEN_W = {1: "SHORT", 2: "MEDIUM", 3: "LONG"}
SOUNDS = [("BOX TAP", "box", "KICK", 1, 1, 1, "An empty cardboard box", "Tap the side or lid gently with your fingertips or the heel of your hand."),
          ("TUBE TAP", "tube", "PERC", 2, 1, 1, "A cardboard tube from a roll of paper", "Tap one end with your palm, or tap along the tube."),
          ("TAPE PULL", "tape", "SNARE", 3, 3, 2, "A roll of tape", "Pull a length off the roll in one quick, steady pull."),
          ("PAPER CRINKLE", "paper", "HAT", 3, 3, 1, "A sheet of wrapping paper, or any paper", "Scrunch the paper once, quickly, in one hand."),
          ("SCISSOR SNIP", "scissors", "PERC", 2, 3, 1, "Ordinary scissors and a scrap of paper", "With an adult’s help, close the blades slowly on the paper, away from everyone."),
          ("BELLS", "bell", "PERC", 3, 3, 3, "A few small jingle bells", "Shake them once and let the sound ring out, or hold them still to stop it.")]
NSND = len(SOUNDS)                          # 6
ROLES = [("KICK", "A low thump on the strong beats", "the box tap"), ("SNARE", "A sharp snap, here on beats 2 and 4", "the tape pull"),
         ("HAT", "A steady tick that keeps time", "the paper crinkle"), ("PERC", "Extra accents that add color", "the tube tap, the scissor snip and the bells")]
LANES = [s[0] for s in SOUNDS]

# ---- the model pattern: 4 bars of 16 steps; for each sound (lane) the grid steps (1-16) it plays in bars 1 to 4. Different sounds may share a step (they are layered).
PATTERN = {"BOX TAP": [[1, 7, 11], [1, 7, 11, 15], [1, 7, 11], [1, 7, 11, 15]],
           "TUBE TAP": [[], [14], [10], [13, 15]],
           "TAPE PULL": [[5, 13], [5, 13], [5, 13], [5, 13]],
           "PAPER CRINKLE": [[1, 3, 5, 7, 9, 11, 13, 15], [1, 3, 5, 7, 9, 11, 13, 15], [1, 3, 5, 7, 9, 11, 13, 15], [1, 3, 5, 7, 9, 11]],
           "SCISSOR SNIP": [[], [4], [4, 12], [4, 12]],
           "BELLS": [[1], [], [9], [1, 9]]}
PAT_HITS = [sum(len(PATTERN[l][b]) for l in LANES) for b in range(PAT_BARS)]       # 14, 16, 17, 18
LANE_HITS = {l: sum(len(x) for x in PATTERN[l]) for l in LANES}                    # 14, 4, 8, 30, 5, 4
PAT_TOTAL = sum(PAT_HITS)                                                           # 65
EVEN_HITS = sum(1 for l in LANES for b in PATTERN[l] for s in b if s % 2 == 0)       # hits on even steps: the ones a 16th swing moves

# ---- the arrangement: 16 bars; rows (layers) and the bars each plays
ARR_ROWS = [("PAPER CRINKLE", [(1, 16)]), ("BELLS", [(1, 4), (9, 12), (15, 16)]), ("BOX TAP", [(5, 14)]), ("TAPE PULL", [(5, 12)]), ("TUBE TAP", [(9, 12)]), ("SCISSOR SNIP", [(9, 12)])]
ARR_SECTIONS = [("INTRO", 1, 4), ("BUILD", 5, 8), ("GROOVE", 9, 12), ("OUTRO", 13, 16)]
ARR_LAYERS = [r for r, _ in ARR_ROWS]


def spans_text(spans):
    return ", ".join(f"{a}–{b}" if a != b else str(a) for a, b in spans)


def bars_of(nm):
    return [b for r, spans in ARR_ROWS if r == nm for a, c in spans for b in range(a, c + 1)]


def layers_in_bar(b):
    return [r for r, _ in ARR_ROWS if b in bars_of(r)]


# ================================================================ the project text (original; students read these pages)
FOLEY_NOTE = ("Foley is the reproduction of everyday sound effects that are added to films, videos and other media in post-production, after the picture has been shot. "
              "It is named after sound-effects artist Jack Foley. In this project you are the Foley artist for a beat: the sounds are everyday ones, and you record them yourself.")
THEME = ("Foley artists make the sound of footsteps, rustling and door handles with everyday objects. This project borrows that idea for music: paper, tape, boxes and bells become the drum kit of a beat. "
         "Students record their own found sounds, so there is no existing song, sample or recording anywhere in the project.")
BUILD_NOTE = ("The skills here are the ones every sample-based beat needs: record a clean one-shot, trim it, give it a job, play it on a 16-step grid, move it slightly off the grid on purpose "
              "and mix the layers so each can be heard. They carry over to beat making, game and film sound, and sound design.")
INCLUSIVE_NOTE = ("Not every family wraps gifts, and that is fine. The project is about the sounds of paper, tape, boxes and bells: any paper and boxes will do, such as newspaper, a paper bag, "
                  "a cereal box, a shoebox or a cardboard tube. Nothing needs to be bought.")
SAFETY = ["Ask permission before you use an object, and tell an adult where you are recording.",
          "Use only safe household objects that cannot break: paper, tape, cardboard, small bells. No glass, no knives, no blades.",
          "Scissors: ordinary scissors on paper only, with an adult’s help, closed slowly and pointed away from everyone. Skip this sound if you are unsure; a pen click works instead.",
          "Tap gently. Do not hit, drop or throw anything, and do not make loud sounds near anyone’s ears.",
          "Keep your headphone volume low, and turn it down before you play a sound back."]
OVERVIEW = ("Build a beat in Logic Pro from sounds you record yourself. Students choose 6 to 8 household sounds (wrapping paper, tape, boxes, a tube, scissors and bells, or any paper and boxes), "
            "record each one at a safe level, trim and clean it, and give it a drum-machine job: kick, snare, hat or percussion. They play a 4-bar pattern on a 16-step grid, "
            "add swing and humanize if their version has them, layer the sounds into a 16-bar arrangement and mix it. Timing math drives every choice, and nobody needs to read music.")
GOALS = ["Plan a beat with timing math: one bar of 4/4 = 240 ÷ BPM seconds and one 16th-note step = 15 ÷ BPM seconds (0.15 s at 100 BPM)",
         "Record 6 to 8 clean found sounds of your own at a safe level, trim each to its start, and give each a role: kick, snare, hat or percussion",
         "Build a 4-bar, 16-step pattern, draw it on a step grid and count its hits per bar and in all",
         "Add swing and humanize (if your version has them), layer a 16-bar arrangement and mix it, starting with small moves"]
VOCAB = [("Foley", "Everyday sound effects recorded and added to a film or video after it is shot; named after sound-effects artist Jack Foley"),
         ("Found sound", "A sound made by an ordinary object, such as paper or a box, that is recorded and used as music"),
         ("Sample", "A recorded sound that an instrument plays back from a key, a pad or a step"),
         ("Transient", "The sudden, loud start of a sound, such as a tap, a snip or a crinkle"),
         ("One-shot", "A short sample that plays once, from its start to its end, each time it is triggered"),
         ("Velocity", "A number that says how hard a note or pad is hit; higher numbers play harder and usually louder"),
         ("Swing", "Timing that delays every second step of a pair, so the pair is long and short instead of even"),
         ("Humanize", "Tiny changes in timing and velocity that make a pattern sound less like a machine")]
REQS = ["Choose a tempo and fill in the timing page: one step = 15 ÷ BPM seconds (page @TIMING)",
        "Record 6 to 8 found sounds of your own, safely and with permission, and keep the cleanest take of each (page @SOUNDS)",
        "Trim each sound and give it a role in the role table: kick, snare, hat or percussion (page @ROLES)",
        "Build a 4-bar pattern on a 16-step grid and draw its hits on the step grid (page @PATTERN)",
        "Try swing and humanize (if your version has them) and write what you hear (page @SWING)",
        "Layer a 16-bar arrangement, mix it with the checklist and bounce (pages @ARRANGE and @MIX)",
        "Present your beat and reflect on your choices (pages @PRESENT and @REFLECT)"]
FILE_NAME = "“Your Name – Foley Beat”"
STEP_NAMES = ["Plan the beat", "Collect the sounds", "Trim and assign roles", "Build the pattern", "Swing and humanize", "Layer, arrange and mix", "Present &amp; get feedback"]
STEPS = ["<b>Plan the beat</b> — Use the timing page (page @TIMING) to pick a tempo and work out how long one step and one bar last",
         "<b>Collect the sounds</b> — Ask permission, choose 6 to 8 safe household sounds and record each one at a safe level with the recording checklist (page @SOUNDS)",
         "<b>Trim and assign roles</b> — Trim each recording to its first hit, name it and give it a role in the role table (page @ROLES)",
         "<b>Build the pattern</b> — Play the sounds on a 16-step grid for 4 bars and draw the hits on the step grid (page @PATTERN; quick reference: page @LOGICREF)",
         "<b>Swing and humanize</b> — Try swing and small timing and velocity changes, if your version has them, and write what you hear (page @SWING)",
         "<b>Layer, arrange and mix</b> — Build a 16-bar arrangement with your sounds as layers (page @ARRANGE), then mix with the checklist (page @MIX) and bounce",
         "<b>Present &amp; get feedback</b> — Write three questions you want classmates to answer about your beat. Play it, point out the sounds, the pattern and the sections as they arrive, "
         "and answer at least 2 of each classmate’s questions. Then reflect (page @REFLECT)."]
TIPS = ["Record each sound several times and keep the cleanest. A good recording makes every later step easier.",
        "Leave plenty of headroom: record quietly. You can raise a quiet sound later, but you cannot repair one that clipped.",
        "Start with a simple pattern and add one change at a time. Listen after each change.",
        "Save a new version of your project at the end of each class, so you can always go back."]
CHECK = ["Bounced .mp3 or .wav of your beat, 16 bars long",
         "Zipped .logicx project file handed in",
         f"Files named correctly: {FILE_NAME}",
         "Timing page, role table and step grid handed in",
         "Rubric self-score done (page @RUBRIC)",
         "I can say my tempo, how long one step lasts, and where each section starts"]
RUBRIC_NOTE = "Each category is scored 1–5. Score yourself first; the final grade is the average of your score and your teacher’s."
LEVELS = [1, 2, 3, 4, 5]
RUBRIC = [
    ("Sounds & Recording", ["No sounds recorded", "Too few sounds, or clipped or full of noise", "6 usable sounds, but some are noisy or uneven in level",
                            "6 to 8 clean sounds, safely recorded, trimmed to their first hit", "Clean, well-trimmed sounds with notes on the takes and a clear reason for each choice"]),
    ("Roles & Pattern", ["No roles or no pattern", "Roles unclear; the pattern does not repeat", "Roles assigned; a pattern with some timing slips",
                         "Every sound has a role; a 4-bar, 16-step pattern that matches the step grid", "Clear roles and a pattern with a steady shape and variation"]),
    ("Swing & Feel", ["No timing or velocity changes", "Changes are random", "Swing or velocity tried, with little explanation",
                      "Swing or humanize tried (if the version has them), with velocity changes and a written comparison", "Deliberate feel choices that are explained and compared"]),
    ("Arrangement & Mix", ["No arrangement or mix", "Sounds only, no sections", "Sections with an unclear mix",
                           "A 16-bar arrangement with 4 sections, rumble cleaned up in small steps and no clipping", "A clear build with a balanced mix that ends on time"]),
    ("Plan & Reflection", ["Plans, presentation or reflection missing", "Thin plan; little to say about choices", "Plan and reflection complete, with basic detail",
                           "Correct timing math, role table and step grid; thoughtful reflection", "Insightful reflection and a polished presentation"]),
]
RUBRIC_TOTAL = 25
RUBRIC_SHORT = ["Clean, safely recorded and well-trimmed sounds",
                "Clear roles and a steady, varied pattern",
                "Deliberate, explained swing and velocity choices",
                "A clear build and a balanced mix",
                "Insightful reflection and a polished presentation"]
RUBRIC_SLIDE_LINE = "Scored 1–5 · final grade = average of your score and mine, out of 25"
RUBRIC_ROW_PITCH = 0.86
RUBRIC_LINE_Y = 6.3

TN_REINFORCES = ("Teaches how a sample-based beat is made from found sounds. Students learn to record clean one-shots at a safe level, to trim them, to give each a drum role, "
                 "to play them on a 16-step grid, to move them off the grid on purpose and to arrange and mix the layers, all in Logic Pro.")
STRUGGLES = ["A recording is noisy or distorted: record again with the input turned down and the object a little farther from the microphone. A recording that clipped cannot be repaired (page @SOUNDS).",
             "A sound clicks or has a gap at the start: trim just before the first sharp part of the sound, the transient, and not after it (page @ROLES).",
             "The hits feel off the beat: check the project tempo and the grid, and count the steps on the step grid (pages @TIMING and @PATTERN).",
             "The mix sounds muddy or boomy: use a high-pass filter on the sounds that are not meant to be low, starting with a small move, and leave the kick alone (page @MIX)."]
VAR_EASY = ("Keep the tempo at 100 BPM, where a step lasts 0.15 seconds and a bar lasts 2.4 seconds (page " + str(pg("timing")) + "); record 6 sounds, use the model pattern on page " + str(pg("pattern")) +
            " and build only the first 8 bars of the arrangement.")
VAR_HARD = ("Record 8 sounds, write a different 4-bar pattern for the groove section and compare two swing settings by ear (page " + str(pg("swing")) + "). "
            "Or build a 32-bar arrangement with a second pattern.")
RESOURCES = [("Timing page (page @TIMING)",
              "Seconds per beat, step and bar at six tempos, the length of a 4-bar pattern and a 16-bar arrangement, and length tables at three tempos."),
             ("Sound sources, safety and recording (page @SOUNDS)",
              "A signal-chain drawing, a safety list, a sound-source table, a recording checklist and a take log."),
             ("Role table and trim checklist (page @ROLES)",
              "Six sounds with icons, roles and pitch, brightness and length descriptors, and a blank role table for 6 to 8 sounds."),
             ("Step grid and swing (pages @PATTERN and @SWING)",
              "A 4-bar, 16-step grid with the hits per bar and in all, and a swing drawing with a table of delays."),
             ("Arrangement, mix and worked example (pages @ARRANGE, @MIX and @EXAMPLE–@EXAMPLE2)",
              "A 16-bar arrangement map, a mix checklist with a high-pass step, and an invented beat at 100 BPM. A model, not a template.")]
TN_NOTE = ("A good listening day: play each beat and ask the class two questions. Which found sound did you recognize first? Where did the build begin? "
           "If a layer is hard to hear, find it on the arrangement map together. This kit includes no recordings and names no songs or artists.")
GRADING = ["The rubric: five categories, each scored 1–5, /25 (page @RUBRIC). Students score themselves first; the final grade is the "
           "average of their score and yours.",
           "Sounds & Recording (rubric row 1): listen for noise and clipping, check the take log and ask where each sound came from (page @SOUNDS).",
           "Roles & Pattern (rubric row 2): check the role table and compare the step grid with what plays (pages @ROLES and @PATTERN).",
           "Swing & Feel (rubric row 3): ask the student to play a straight and a swung version and say what changed (page @SWING).",
           "Arrangement & Mix (rubric row 4): play the whole beat and find the intro, build, groove and outro on the arrangement map; check the mix checklist (pages @ARRANGE and @MIX).",
           "Plan & Reflection (rubric row 5): the timing page, the role table, the feedback questions and the Reflection page (page @REFLECT) are the evidence."]
PACING = [
    {"n": 1, "owner": "Hear the idea, plan the timing and record the found sounds.",
     "do": "Slides 1–8: the think-and-share, the project, the three classes, what Foley is, the timing math, the signal chain and the safety checklist. Hand out the timing page and the sounds page. "
           "Before they leave, students have a tempo and a first set of clean recordings.",
     "slides": (1, 8), "pages": ["timing", "sounds", "proj1", "proj2", "proj3", "vocab"],
     "deck": "Hear the room · one step = 15 ÷ BPM · record safely"},
    {"n": 2, "owner": "Trim the sounds, give each a role, play a 4-bar pattern and try swing.",
     "do": "Slides 9–12: roles, trimming and loading, the 4-bar step grid and swing. Demonstrate dropping a trimmed sound onto a pad, then the pattern, then one swing setting. "
           "Walk the room with one question: which step is this hit on?",
     "slides": (9, 12), "pages": ["roles", "pattern", "swing", "present"], "deck": "Roles · trim and load · the step grid · swing"},
    {"n": 3, "owner": "Layer a 16-bar arrangement, mix, bounce, present and reflect.",
     "do": "Slides 13–18: the arrangement, the mix and the high-pass step, what to turn in, the rubric, presentation day and the wrap-up. Students arrange, mix, bounce and present.",
     "slides": (13, 18), "pages": ["arrange", "mix", "rubric", "present", "reflect"], "deck": "Arrangement · mix · checklist · presentations"},
]
PACING_EXTRA = (
    '<div class="cols" style="margin-top:4pt;gap:14pt"><div class="box acc-b"><span class="k">The one thing to do on Class 1</span>'
    '<p style="margin:0;font-size:10.6pt">Make sure every student leaves with a tempo and at least 6 clean, safely recorded sounds, so that Class 2 '
    'is all trimming, roles and pattern. Check the take logs before they go.</p></div>'
    '<div class="box"><span class="k">With two or four periods</span><p style="margin:0;font-size:10.6pt"><b>Two classes:</b> Class 1 is the plan, the recording, the trimming and the roles; '
    'Class 2 is the pattern, the swing, the arrangement, the mix and short presentations. <b>Four classes:</b> keep Classes 1 and 2, then spend Class 3 on the arrangement and the mix, and '
    'Class 4 on presentations and reflection.</p></div></div>')
PACING_SIZE = 10.6
TN2_SIZE = 9.9

SONG_NOTE = ("No audio, recordings, lyrics or melodies are included, and no songs, artists or albums are named. Students make every "
             "sound themselves, from safe household objects they record with permission.")
VOICE_NOTE = ("Students record their OWN found sounds. They do not sample songs, videos, games or any commercial recording. Every object is used with permission, and an adult helps with anything beyond "
              "paper, tape, cardboard and small bells. No glass, no knives, no blades, and the volume stays low.")
CREDITS = ["The timing page, the role table, the step grids, the swing drawing, the checklists and the worked example: original work, Hudson Beat. "
           "No melodies, lyrics, recordings or published editions are included.",
           "The cover illustration was made with digital and AI tools. No audio, video, album art, screenshots, presets, templates, links or "
           "chart data from other sources are included. No student work is included. The recording and mixing guidance is general practice, "
           "given as starting points to set by ear."]
LOGIC_INTRO = ("Where to find the tools a Gift Wrap Foley Beat is likely to use. Demonstrate what your class needs on Classes 1 and 2 and then "
               "let students work. Names are from current Logic Pro versions; labels move between versions, so check yours.")
LOGIC_REF = [("Project and tempo", "File › New…, then an Audio track to record the sounds. Set the project tempo in the control bar to the BPM on your timing page and keep the time signature at 4/4. "
              "Set the snap or grid value to 16th notes (if your version shows one) so that every hit lands on a step."),
             ("Record a sound", "On the Audio track, choose the microphone or interface as the input and click the record-enable button (R). Set the gain on the interface, not the fader, and leave plenty of headroom: "
              "record the loudest tap you plan to make and keep the meter well below the top. Leave a moment of silence before each hit and record several takes. Re-record a take that clips."),
             ("Trim a recording", "Select the region and shorten its start so that it begins just before the first sharp part of the sound, the transient, and its end after the sound has died away. "
              "Look for a fade option on the region (if your version has one) to remove a click at the end. Rename each region after its sound."),
             ("Load the sounds", "Add a Software Instrument track and choose Drum Machine Designer (if your version has it), then drop each trimmed recording onto its own pad. Quick Sampler (if your version has it) can hold "
              "one sound at a time. Name each pad after its sound and role."),
             ("Play the pattern", "Play the pads from a keyboard or pad controller, or draw notes in the Piano Roll with the grid set to 16th notes: 16 steps to a bar, for 4 bars. "
              "The Step Sequencer (if your version has it) shows one row for each sound and a column for each step, and works with Drum Machine Designer. Quantize to 16th notes if hits are late."),
             ("Velocity", "Velocity is a number that says how hard a note or pad is hit (many programs use a scale up to 127). Look for a velocity value for each step or note (if your version shows one). "
              "Change the velocities a little so that not every hit is equally loud."),
             ("Swing and humanize", "Look for a swing control in the Step Sequencer or in the region or track settings, and for a humanize or randomize option for timing and velocity (each if your version has them). "
              "The scales and names differ between versions, so listen and compare a straight and a swung version."),
             ("EQ and the high-pass filter", "Add an EQ plug-in on a track, such as Channel EQ (if your version has it), and look for a high-pass filter, which lets higher sounds through and cuts the lows. "
              "Start with a small move, listen, and stop as soon as the sound starts to feel thin."),
             ("Mixer and bounce", "Open the Mixer (the key command is X by default, if your version has it) and set levels and pan. Keep the master peak below 0 dBFS with room to spare. Then File › Bounce › Project or Section (Command-B), MP3 or WAV, for the whole beat. "
              "In Finder, Control-click the .logicx and choose Compress.")]
PRESENT_CHECK = [f"Files named {FILE_NAME}; the .mp3 or .wav and the zipped .logicx handed in",
                 "Reflection page done (page @REFLECT)", "Three questions for classmates written",
                 "Rubric self-score done (page @RUBRIC)"]
VOCAB_PROMPT = "Where it shows up in my beat:"
TN1_EXTRA = (
    '<div class="box acc-b" style="margin-top:4pt"><span class="k">Where this kit helps with each struggle</span><ul style="margin:0">'
    '<li style="font-size:12pt;margin-bottom:3pt">Noisy or clipped recordings: the sounds page (page @SOUNDS) has a signal-chain drawing, a headroom checklist and a take log.</li>'
    '<li style="font-size:12pt;margin-bottom:3pt">Clicks and gaps: the role table page (page @ROLES) has a trim checklist.</li>'
    '<li style="font-size:12pt;margin-bottom:3pt">Hits off the beat: the timing page (page @TIMING) gives the length of a step at six tempos, and the step grid (page @PATTERN) shows every hit.</li>'
    '<li style="font-size:12pt;margin-bottom:0">A muddy mix: the mix page (page @MIX) has a high-pass step, and the worked example (pages @EXAMPLE–@EXAMPLE2) shows a full set of choices.</li></ul></div>')
TN1_SIZE = 12.0
PROJ_SIZE = 10.9
VOCAB_GAP = 5
LOGIC_SIZE = 9.4
PROJ1_EXTRA = ""
RUBRIC_EXTRA = ('<div class="box acc-b" style="margin-top:8pt;padding:6pt 10pt"><span class="k">Evidence to look at for each category</span>'
                '<p style="margin:0;font-size:10.6pt;line-height:1.4">Sounds &amp; Recording: take log and sounds page (page @SOUNDS). Roles &amp; Pattern: role table and step grid (pages @ROLES and @PATTERN). '
                'Swing &amp; Feel: the comparison table (page @SWING). Arrangement &amp; Mix: arrangement map and mix checklist (pages @ARRANGE and @MIX). '
                'Plan &amp; Reflection: timing page, feedback questions and reflection (pages @TIMING, @PRESENT and @REFLECT).</p></div>')

# ================================================================ the worked example: an invented beat at 100 BPM
EX_BAR_S = bar_len(EX_BPM)                  # 2.4 s
EX_STEP_S = step_len(EX_BPM)                # 0.15 s
EX_WEAK = "I will record some paper sounds and some taps, put them in a pattern and add more sounds, and it will sound cool."
EX_STRONG = ("My beat is in 4/4 at 100 BPM. One bar lasts 240 ÷ 100 = 2.4 seconds and one 16th-note step lasts 15 ÷ 100 = 0.15 seconds. I recorded 6 sounds: a box tap as the kick, a tape pull as the snare, "
             "a paper crinkle as the hat, and a tube tap, a scissor snip and bells as percussion. My 4-bar pattern has 14, 16, 17 and 18 hits, 65 in all, and lasts 4 × 2.4 = 9.6 seconds. "
             "My arrangement is 16 bars = 38.4 seconds: an intro in bars 1 to 4, a build in bars 5 to 8, the groove in bars 9 to 12 and an outro in bars 13 to 16, with 6 layers in all.")
EX_QUESTIONS = ["Which found sound did you recognize first?",
                "Could you hear the build start in bar 5?",
                "Which sound felt like the kick, and why?"]
EX_NOTE = ("the paper crinkle never stops, so it works like a hat; the box tap and the tape pull arrive together in bar 5; "
           "all six sounds play only in the groove, and the outro strips back to the paper and the bells")


# ================================================================ drawings (all in code, labels logged for the fit check)
def padded(body, W, H, M=10):
    """Wrap a drawing's body with M units of clear padding on all four sides (wider than the thickest outer stroke), so no edge pixel is ever inked."""
    return f'<g transform="translate({M},{M})">{body}</g>', W + 2 * M, H + 2 * M


def icon(kind, x, y, s=1.0):
    """A 64 x 64 line icon of a household object, drawn at (x, y) scaled by s. Strokes are 4 units; every shape stays at least 3 units inside the 64 x 64 box."""
    k = f'<g transform="translate({x:.1f},{y:.1f}) scale({s})" fill="#fff" stroke="#000" stroke-width="4" stroke-linejoin="round" stroke-linecap="round">'
    if kind == "box":
        k += (f'<polygon points="32,8 58,19 32,30 6,19" fill="{ACC_LIGHT}"/><polygon points="6,19 32,30 32,57 6,46"/><polygon points="32,30 58,19 58,46 32,57"/>'
              f'<line x1="19" y1="24.5" x2="45" y2="13.5" stroke-width="3"/>')
    elif kind == "tube":
        k += (f'<path d="M14 14 H46 A9 18 0 0 1 46 50 H14 Z"/><ellipse cx="14" cy="32" rx="9" ry="18" fill="{ACC_LIGHT}"/>'
              f'<ellipse cx="14" cy="32" rx="3" ry="9" fill="#fff" stroke-width="3"/>')
    elif kind == "tape":
        k += (f'<circle cx="26" cy="26" r="20"/><circle cx="26" cy="26" r="8" fill="{ACC_LIGHT}"/>'
              f'<polygon points="26,46 58,46 54,50 58,54 54,58 26,58" fill="{ACC_LIGHT}"/>')
    elif kind == "paper":
        k += ('<polygon points="8,16 24,8 40,14 56,9 58,30 50,43 56,55 36,59 21,52 8,57 13,36"/>'
              '<polyline points="24,8 28,28 21,52" fill="none" stroke-width="3"/><polyline points="40,14 36,32 50,43" fill="none" stroke-width="3"/>'
              '<polyline points="13,36 28,28" fill="none" stroke-width="3"/>')
    elif kind == "scissors":
        k += (f'<line x1="44" y1="7" x2="22" y2="40" stroke-width="5"/><line x1="20" y1="7" x2="42" y2="40" stroke-width="5"/>'
              f'<circle cx="19" cy="49" r="9" fill="{ACC_LIGHT}"/><circle cx="45" cy="49" r="9" fill="{ACC_LIGHT}"/><circle cx="32" cy="24" r="3" fill="#000"/>')
    elif kind == "bell":
        k += (f'<circle cx="32" cy="35" r="21" fill="{ACC_LIGHT}"/><line x1="12" y1="41" x2="52" y2="41" stroke-width="3"/><circle cx="32" cy="41" r="3.5" fill="#000"/>'
              f'<circle cx="32" cy="9.5" r="4.5"/>')
    elif kind == "mic":
        k += (f'<rect x="21" y="5" width="22" height="34" rx="11" fill="{ACC_LIGHT}"/><line x1="21" y1="17" x2="43" y2="17" stroke-width="3"/><line x1="21" y1="26" x2="43" y2="26" stroke-width="3"/>'
              f'<path d="M12 28 V32 A20 20 0 0 0 52 32 V28" fill="none"/><line x1="32" y1="52" x2="32" y2="59"/><line x1="20" y1="59" x2="44" y2="59"/>')
    elif kind == "interface":
        k += (f'<rect x="5" y="14" width="54" height="36" rx="5"/><circle cx="20" cy="32" r="8" fill="{ACC_LIGHT}"/><line x1="20" y1="32" x2="24" y2="27" stroke-width="3"/>'
              f'<circle cx="44" cy="32" r="5" fill="#fff"/><circle cx="44" cy="32" r="1.5" fill="#000"/>')
    elif kind == "track":
        k += ('<rect x="5" y="13" width="54" height="38" rx="5"/>'
              + "".join(f'<line x1="{x0}" y1="{32 - h}" x2="{x0}" y2="{32 + h}" stroke-width="4"/>' for x0, h in ((14, 5), (22, 11), (30, 7), (38, 14), (46, 6), (52, 3))))
    elif kind == "phones":
        k += (f'<path d="M10 40 V32 A22 22 0 0 1 54 32 V40" fill="none"/><rect x="5" y="38" width="12" height="20" rx="5" fill="{ACC_LIGHT}"/><rect x="47" y="38" width="12" height="20" rx="5" fill="{ACC_LIGHT}"/>')
    else:
        raise ValueError(kind)
    return k + "</g>"


def meter(x, cy, level, cls="dot"):
    """Three dots, `level` of them filled."""
    out = []
    for i in range(3):
        on = i < level
        out.append(f'<circle class="{cls} {"on" if on else "off"}" cx="{x + i * 40:.1f}" cy="{cy:.1f}" r="13" fill="{ACCENT if on else "#fff"}" stroke="#000" stroke-width="3.5"/>')
    return "".join(out)


def roles_body(W=1600, name="roles"):
    """The sound-role table: 6 rows, each an icon, the sound's name, its role chip and three 3-dot meters (pitch, brightness, length) with the word printed next to the dots."""
    out = []
    top = 70
    rh = 84
    cols = {"snd": 120, "role": 470, "pitch": 690, "bright": 950, "len": 1240}
    out.append(f'<rect x="0" y="6" width="{W - 40}" height="46" rx="8" fill="#000"/>')
    for key, lbl in (("snd", "SOUND"), ("role", "ROLE"), ("pitch", "PITCH"), ("bright", "BRIGHTNESS"), ("len", "LENGTH")):
        out.append(D.t_(cols[key] + (0 if key != "snd" else -60), 40, lbl, 26, 700, anchor="start", fill_="#fff"))
        D.lab(name + " heads", lbl, 26, 200)
    chip = {"KICK": ("#000", "#fff"), "SNARE": (ACCENT, "#fff"), "HAT": (ACC_LIGHT, "#000"), "PERC": ("#fff", "#000")}
    for i, (nm, ic, role, p, b, ln, _, _) in enumerate(SOUNDS):
        y = top + i * rh
        out.append(f'<rect class="row" x="0" y="{y}" width="{W - 40}" height="{rh - 8}" fill="{"#f4f4f4" if i % 2 == 0 else "#fff"}" stroke="#bbb" stroke-width="2"/>')
        out.append(f'<g class="icon">{icon(ic, 18, y + 3, 1.0)}</g>')
        out.append(D.t_(cols["snd"], y + 48, nm, 28, 700, anchor="start"))
        D.lab(name + " names", nm, 28, cols["role"] - cols["snd"] - 30)
        fl, tc = chip[role]
        out.append(f'<rect class="chip" x="{cols["role"]}" y="{y + 14}" width="150" height="42" rx="21" fill="{fl}" stroke="#000" stroke-width="3.5"/>')
        out.append(D.t_(cols["role"] + 75, y + 44, role, 26, 700, fill_=tc))
        D.lab(name + " chips", role, 26, 130)
        for key, lv, words in (("pitch", p, PITCH_W), ("bright", b, BRIGHT_W), ("len", ln, LEN_W)):
            out.append(meter(cols[key], y + 35, lv))
            out.append(D.t_(cols[key] + 124, y + 44, words[lv], 24, 700, anchor="start", fill_="#222"))
            D.lab(name + " words", "MEDIUM", 24, 110)
    bot = top + NSND * rh
    cap = f"{NSND} sounds, {len(ROLES)} roles. The dots are what to listen for in each sound, not measurements: your objects will sound a little different."
    out.append(D.t_((W - 40) / 2, bot + 28, cap, 23, 700, "Source Sans 3"))
    D.lab(name + " cap", cap, 23, W - 80)
    return padded("".join(out), W - 40, bot + 44, 16)


def grid_body(W=1600, name="grid", blank=False):
    """The 4-bar pattern on a step grid: one lane for each of the 6 sounds by 64 steps (4 bars of 16). Hit cells carry class="hit", every cell class="cell"."""
    gx = 215
    pw = W - gx - 34
    cw = pw / (PAT_BARS * STEPS_BAR)
    ch = 40
    top = 92
    bot = top + NSND * ch
    out = []
    for b in range(PAT_BARS):
        for s in range(STEPS_BAR):
            for ln in range(NSND):
                out.append(f'<rect class="cell" x="{gx + (b * STEPS_BAR + s) * cw:.1f}" y="{top + ln * ch}" width="{cw:.1f}" height="{ch}" fill="{"#f4f4f4" if (s // 4) % 2 == 0 else "#fff"}" '
                           f'stroke="#bbb" stroke-width="1.5"/>')
    for ln, nm in enumerate(LANES):
        out.append(D.t_(gx - 14, top + ln * ch + 28, nm, 22, 700, anchor="end"))
        D.lab(name + " lanes", "PAPER CRINKLE", 22, gx - 22)
    if not blank:
        for ln, nm in enumerate(LANES):
            for b in range(PAT_BARS):
                for st in PATTERN[nm][b]:
                    x = gx + (b * STEPS_BAR + st - 1) * cw
                    out.append(f'<rect class="hit" x="{x + 2.5:.1f}" y="{top + ln * ch + 5}" width="{cw - 5:.1f}" height="{ch - 10}" rx="4" fill="{ACCENT}" stroke="#000" stroke-width="2.5"/>')
    for k in range(PAT_BARS * 4 + 1):
        x = gx + k * 4 * cw
        out.append(f'<line x1="{x:.1f}" y1="{top}" x2="{x:.1f}" y2="{bot}" stroke="{"#000" if k % 4 == 0 else "#777"}" stroke-width="{4 if k % 4 == 0 else 2}"/>')
    out.append(f'<rect x="{gx}" y="{top}" width="{pw}" height="{bot - top}" fill="none" stroke="#000" stroke-width="4"/>')
    for b in range(PAT_BARS):
        x0 = gx + b * STEPS_BAR * cw
        out.append(D.t_(x0 + 10, 36, f"BAR {b + 1}", 24, 700, anchor="start", fill_=ACCENT))
        for beat in range(BEATS_BAR):
            out.append(D.t_(x0 + (beat * 4 + 2) * cw, 74, str(beat + 1), 20, 500, "Source Sans 3", fill_="#222"))
        lbl = "hits: ______" if blank else f"{PAT_HITS[b]} hits"
        out.append(D.t_(x0 + STEPS_BAR * cw / 2, bot + 38, lbl, 24, 700))
        D.lab(name + " hits", lbl, 24, STEPS_BAR * cw - 20)
    out.append(D.t_(gx - 14, 74, "BEAT", 20, 700, anchor="end", fill_=ACCENT))
    cap = (f"{PAT_BARS} bars of {STEPS_BAR} steps = {PAT_BARS * STEPS_BAR} steps. Each beat is 4 steps. " + ("Draw a hit in the lane of each sound you play." if blank else f"{PAT_TOTAL} hits in all."))
    out.append(D.t_(gx + pw / 2, bot + 82, cap, 23, 500, "Source Sans 3"))
    D.lab(name + " cap", cap, 23, pw)
    return padded("".join(out), W, bot + 98, 16)


def arr_body(W=1600, name="arrange"):
    """The 16-bar arrangement at 100 BPM: four sections of 4 bars, six layers (one for each sound), bars along the top and seconds along the bottom."""
    gx = 230
    pw = W - gx - 34
    bw = pw / ARR_BARS
    rh, gap = 46, 8
    top = 126
    out = []
    for nm, a, b in ARR_SECTIONS:
        x0 = gx + (a - 1) * bw
        out.append(f'<rect class="sec" x="{x0 + 2:.1f}" y="12" width="{(b - a + 1) * bw - 4:.1f}" height="44" rx="8" fill="{ACCENT if nm == "GROOVE" else "#000"}"/>')
        lbl = f"{nm} · bars {a}–{b}"
        out.append(D.t_(x0 + (b - a + 1) * bw / 2, 44, lbl, 24, 700, fill_="#fff"))
        D.lab(name + " sections", lbl, 24, (b - a + 1) * bw - 16)
    for b in range(ARR_BARS):
        out.append(D.t_(gx + (b + 0.5) * bw, 94, str(b + 1), 24, 700))
    out.append(D.t_(gx - 14, 94, "BAR", 22, 700, anchor="end", fill_=ACCENT))
    fills = {"PAPER CRINKLE": "#d9d9d9", "BELLS": "#fff", "BOX TAP": "#555", "TAPE PULL": ACCENT, "TUBE TAP": ACC_LIGHT, "SCISSOR SNIP": "#999"}
    for r, (nm, spans) in enumerate(ARR_ROWS):
        y = top + r * (rh + gap)
        out.append(f'<rect class="lane" x="{gx}" y="{y}" width="{pw}" height="{rh}" fill="#fff" stroke="#bbb" stroke-width="2"/>')
        out.append(D.t_(gx - 14, y + rh / 2 + 8, nm, 22, 700, anchor="end"))
        D.lab(name + " rows", "PAPER CRINKLE", 22, gx - 24)
        for a, b in spans:
            out.append(f'<rect class="block" x="{gx + (a - 1) * bw + 3:.1f}" y="{y + 5}" width="{(b - a + 1) * bw - 6:.1f}" height="{rh - 10}" rx="7" fill="{fills[nm]}" stroke="#000" stroke-width="3"/>')
    bot = top + len(ARR_ROWS) * (rh + gap) - gap
    cy = bot + 30
    out.append(D.t_(gx - 14, cy + 36, "LAYERS", 22, 700, anchor="end", fill_=ACCENT))
    for b in range(1, ARR_BARS + 1):
        out.append(D.t_(gx + (b - 0.5) * bw, cy + 36, str(len(layers_in_bar(b))), 26, 700, extra='class="cnt"'))
    for k in range(ARR_BARS // SEC_BARS + 1):
        x = gx + k * SEC_BARS * bw
        out.append(f'<line x1="{x:.1f}" y1="{top - 8}" x2="{x:.1f}" y2="{bot + 12}" stroke="#000" stroke-width="3" stroke-dasharray="9 7"/>')
        s = hit_time(EX_BPM, SEC_BARS * k + 1, 1)
        out.append(D.t_(x, cy + 86, fmt(s), 24, 700, anchor="start" if k == 0 else ("end" if k == ARR_BARS // SEC_BARS else "middle")))
    out.append(D.t_(gx - 14, cy + 86, "SECONDS", 22, 700, anchor="end", fill_=ACCENT))
    D.lab(name + " rows", "SECONDS", 22, gx - 24)
    cap = f"{ARR_BARS} bars at {EX_BPM} BPM = {fmt(ARR_BARS * EX_BAR_S)} seconds, with {len(ARR_ROWS)} layers. The number row shows how many layers sound in each bar."
    out.append(D.t_(gx + pw / 2, cy + 134, cap, 23, 700, "Source Sans 3"))
    D.lab(name + " cap", cap, 23, pw)
    return padded("".join(out), W, cy + 150, 16)


def chain_body(W=1620, name="chain"):
    """The signal chain from a found sound to the student's ears: five stages (class "stage") joined by four arrows (class "arrow")."""
    stages = [("OBJECT", "box", "ask first"), ("MICROPHONE", "mic", "same distance"), ("INPUT", "interface", "gain low"), ("TRACK", "track", "watch the meter"), ("HEADPHONES", "phones", "volume low")]
    sw, sh, gap = 240, 214, 90
    out = []
    for i, (lbl, ic, sub) in enumerate(stages):
        x = 10 + i * (sw + gap)
        out.append(f'<rect class="stage" x="{x}" y="14" width="{sw}" height="{sh}" rx="14" fill="#fff" stroke="#000" stroke-width="4"/>')
        out.append(f'<circle cx="{x + 26}" cy="40" r="19" fill="#000"/>')
        out.append(D.t_(x + 26, 49, str(i + 1), 26, 700, fill_="#fff"))
        out.append(icon(ic, x + sw / 2 - 40, 46, 1.25))
        out.append(D.t_(x + sw / 2, 164, lbl, 28, 700))
        D.lab(name + " stages", lbl, 28, sw - 20)
        out.append(D.t_(x + sw / 2, 202, sub, 23, 500, "Source Sans 3", fill_=ACCENT))
        D.lab(name + " subs", sub, 23, sw - 20)
        if i < len(stages) - 1:
            ax = x + sw + 12
            out.append(f'<g class="arrow"><line x1="{ax}" y1="{14 + sh / 2}" x2="{ax + gap - 34}" y2="{14 + sh / 2}" stroke="#000" stroke-width="5" stroke-linecap="round"/>'
                       f'<polyline points="{ax + gap - 50},{14 + sh / 2 - 14} {ax + gap - 30},{14 + sh / 2} {ax + gap - 50},{14 + sh / 2 + 14}" fill="none" stroke="#000" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/></g>')
    wtot = 10 + len(stages) * sw + (len(stages) - 1) * gap + 10
    cap = f"From object to track in {len(stages)} stages. Leave plenty of headroom at the input."
    out.append(D.t_(wtot / 2, 14 + sh + 48, cap, 25, 700, "Source Sans 3"))
    D.lab(name + " cap", cap, 25, wtot - 40)
    return padded("".join(out), wtot, 14 + sh + 66, 16)


def swing_body(W=1500, name="swing"):
    """One beat (4 steps) twice: straight, and swung 2:1 (steps 2 and 4 late by 1/3 of a step). Every hit is a circle of class "sw"."""
    gx = 200
    pw = W - gx - 50
    u = pw / 4
    r = Fraction(2)
    out = []
    rows = [("STRAIGHT", 0, [Fraction(i) for i in range(4)], "#fff"), ("SWUNG 2:1", 1, [Fraction(0), 1 + swing_delay_steps(r), Fraction(2), 3 + swing_delay_steps(r)], ACCENT)]
    top = 96
    rh = 120
    for k in range(5):
        out.append(f'<line x1="{gx + k * u:.1f}" y1="{top - 12}" x2="{gx + k * u:.1f}" y2="{top + 2 * rh}" stroke="{"#000" if k in (0, 4) else "#999"}" stroke-width="{4 if k in (0, 4) else 2.5}" stroke-dasharray="{"0" if k in (0, 4) else "8 6"}"/>')
    for i in range(4):
        out.append(D.t_(gx + (i + 0.5) * u, 70, f"grid step {i + 1}", 24, 700, fill_=ACCENT))
        D.lab(name + " steps", "grid step 4", 24, u - 20)
    for nm, ri, pos, fl in rows:
        cy = top + ri * rh + rh / 2
        out.append(f'<line x1="{gx}" y1="{cy}" x2="{gx + pw}" y2="{cy}" stroke="#bbb" stroke-width="3"/>')
        out.append(D.t_(gx - 40, cy + 9, nm, 26, 700, anchor="end"))
        D.lab(name + " rows", "SWUNG 2:1", 26, gx - 50)
        for p in pos:
            out.append(f'<circle class="sw" cx="{gx + float(p) * u:.1f}" cy="{cy}" r="19" fill="{fl}" stroke="#000" stroke-width="4"/>')
    cy1 = top + rh + rh / 2
    for i in (1, 3):
        x0, x1 = gx + i * u, gx + (i + float(swing_delay_steps(r))) * u
        out.append(f'<line x1="{x0:.1f}" y1="{cy1 - 36}" x2="{x1:.1f}" y2="{cy1 - 36}" stroke="#000" stroke-width="4"/>')
        out.append(f'<polyline points="{x1 - 12:.1f},{cy1 - 46} {x1:.1f},{cy1 - 36} {x1 - 12:.1f},{cy1 - 26}" fill="none" stroke="#000" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>')
    late = f"late by 1/3 step = {exact(swing_delay_steps(r) * step_len(EX_BPM))} s at {EX_BPM} BPM"
    out.append(D.t_(gx + 2 * u + 30, top + 2 * rh + 46, late, 25, 700, "Source Sans 3"))
    D.lab(name + " late", late, 25, pw - 40)
    cap = "One beat is 4 steps. In the swung row, grid steps 2 and 4 play late."
    out.append(D.t_(gx + pw / 2, top + 2 * rh + 92, cap, 24, 700, "Source Sans 3"))
    D.lab(name + " cap", cap, 24, pw)
    return padded("".join(out), W, top + 2 * rh + 108, 16)


def hero_body():
    """The owner's pre-made art (art/hero.png, used whole and unchanged). The viewBox is the whole 1400 x 1400 file plus 24 units of clear padding on every side (art pixels x 62-1329, y 74-1363, so at least 60 units inside it), which --check proves from the file."""
    return (f'<image href="../art/hero.png" x="{-HX}" y="{-HY}" width="1400" height="1400"/>', HW, HH)


HX, HY, HW, HH = -24, -24, 1448, 1448

DRAWINGS = {"hero": hero_body, "chain": lambda: chain_body(1620, "chain deck"), "roles": lambda: roles_body(1600, "roles deck"), "grid": lambda: grid_body(1600, "grid deck"),
            "swing": lambda: swing_body(1500, "swing deck"), "arrange": lambda: arr_body(1600, "arrange deck")}
DRAWING_PX = {"hero": 1340, "chain": 2000, "roles": 2000, "grid": 2000, "swing": 1800, "arrange": 2000}
SIDE = {"chain": ["Ask first, record quietly", "Keep the meter well below the top"],
        "roles": ["6 sounds, 4 roles", "Dots show pitch, brightness, length"],
        "grid": ["16 steps in a bar, 4 beats of 4 steps", "Hits per bar: 14, 16, 17 and 18"],
        "swing": ["The 2nd and 4th steps play a little late", "A 2:1 swing delays them by 1/3 step"],
        "arrange": ["Intro, build, groove and outro", "16 bars at 100 BPM are 38.4 seconds"]}
# extra drawings used on pages only, rendered alone on a transparent ground by --check as well
PAGE_DRAWINGS = {"chain-page": lambda: chain_body(1620, "chain page"), "roles-page": lambda: roles_body(1600, "roles page"), "grid-page": lambda: grid_body(1600, "grid page"),
                 "grid-blank-page": lambda: grid_body(1600, "grid blank page", blank=True), "swing-page": lambda: swing_body(1500, "swing page"), "arrange-page": lambda: arr_body(1600, "arrange page")}


def label_extras():
    for k, fn in PAGE_DRAWINGS.items():
        fn()


# ================================================================ intro deck: (class, kind, title, body, speaker notes)
SLIDES = [
    (1, "title", "Gift Wrap Foley Beat", "Record it. Trim it. Play it.",
     "Class 1, the first minute. No audio is included in this deck. Open with the idea: you will record found sounds of your own from safe household objects, trim them, give each one a job in a beat, "
     "play them in a pattern, add a little swing and arrange and mix a short piece. Nobody needs to read music, and no existing song or recording is used. If a student's family does not wrap gifts, any paper and boxes will do."),
    (1, "listen", "Hear the room", "Think, then share|Teacher: read aloud, no audio plays. Paper crinkles, tape pulls off its roll, a box lid taps, a small bell shakes and then goes still. "
     "Imagine every one of those sounds as a drum.|Which everyday sound would make the best kick?|Which would make the best hat?|"
     "What would you need to record it cleanly?",
     "Read the scene aloud slowly and ask the three questions. Take a few answers. Nothing is played from a speaker. Students will say a box or a book for a kick, and paper or tape for a hat. Write their words on the board. "
     "The project turns each idea into a tool with a number attached: a tempo, a step length, a role and a grid."),
    (1, "bullets", "What is the Gift Wrap Foley Beat?", "Record 6 to 8 found sounds of your own|Trim each one and give it a job|Play them in a 4-bar pattern|"
     "Add swing, then arrange and mix 16 bars",
     "The project in four lines. Every student records 6 to 8 sounds from safe household objects, with permission, and builds a beat in Logic Pro. Each sound is trimmed and given a role such as kick, snare, hat or percussion, "
     "the sounds are played on a 16-step grid for 4 bars, swing and humanize are tried if the version has them, and the result is a 16-bar arrangement that is mixed and bounced. No audio ships: students make every sound."),
    (1, "days", "Three classes", "",
     "The shape of the project. Class 1: hook, what Foley is, the timing math and recording safely. Class 2: trim the sounds, give each a role, play the 4-bar pattern and try swing. Class 3: arrangement, mix, "
     "bounce, present and reflect. The badge on this slide reads Classes 1 to 3 because it covers all three. With two classes, do the plan, recording, trimming and roles in Class 1 and the rest in Class 2; "
     "with four, add a day for presentations. Hand out the timing page and the sounds page now."),
    (1, "bullets", "What is Foley?", "Everyday sound effects added to a film or video|Recorded and added in post-production|Named after sound-effects artist Jack Foley|Today you are the Foley artist for a beat",
     "Class 1. Foley is the reproduction of everyday sound effects that are added to films, videos and other media in post-production, after the picture has been shot; it is named after sound-effects artist Jack Foley. "
     "Footsteps, rustling cloth and door handles are classic examples. We borrow the idea: paper, tape, boxes and bells become the drums of a beat. This is a description of the idea, not a history lesson, so keep it short."),
    (1, "bullets", "The math: one step = 15 ÷ BPM", "One bar of 4/4 lasts 240 ÷ BPM seconds|One 16th-note step lasts 15 ÷ BPM seconds|At 100 BPM, one step is 0.15 seconds|16 bars at 100 BPM last 38.4 seconds",
     f"Class 1, the key idea. In 4/4 there are four beats in a bar and each beat holds four 16th-note steps, so a bar has 16 steps. One bar lasts 240 divided by the tempo, and one step lasts 15 divided by the tempo: at 100 BPM that is "
     f"0.15 seconds, and a bar is 2.4 seconds. A 4-bar pattern lasts 9.6 seconds and 16 bars last 38.4 seconds. At 80 BPM a bar is 3 seconds and at 120 BPM it is 2 seconds. The timing page is page {pg('timing')}."),
    (1, "pic", "From object to track", "chain",
     f"Class 1. The signal chain in five stages. 1: the object, used with permission and with an adult's help for anything beyond paper, tape, cardboard and small bells. 2: the microphone, at the same distance for every take. "
     f"3: the input, where you set the gain low; leave plenty of headroom and re-record a take that clips. 4: the track, where you watch the meter. 5: headphones, with the volume low. A quiet recording can be raised later; "
     f"a clipped one cannot be repaired. The recording checklist and take log are on page {pg('sounds')}, and the quick reference is page {pg('logicref')}."),
    (1, "check", "Collect sounds safely", "Ask permission before you use an object|Safe objects only; an adult for scissors|No glass, knives or blades|Tap gently and keep the volume low|"
     "Your own recordings, 6 to 8 sounds",
     f"Class 1. The safety checklist, shortened to fit the slide. Every object is used with permission. Use safe household objects that cannot break; no glass, no knives, no blades. Ordinary scissors on paper only, "
     f"with an adult's help and closed slowly away from everyone, or skip that sound and use a pen click. Not every family wraps gifts: any paper and boxes work, such as newspaper, a paper bag or a cereal box. "
     f"Students record their own sounds; no existing recordings. The full safety list and the sound-source table are on page {pg('sounds')}."),
    (2, "pic", "Give each sound a job", "roles",
     f"Class 2. The role table: 6 sounds, each with an icon, a role and three sets of dots. The box tap is the kick, the tape pull is the snare, the paper crinkle is the hat and the tube tap, the scissor snip and the bells are percussion. "
     f"The dots say how low or high, how dull or bright and how short or long each sound is, as a guide to listen for: they are descriptions, not measurements, and students' objects will differ. "
     f"Students fill in their own table for 6 to 8 sounds on page {pg('roles')}."),
    (2, "steps", "Trim and load the sounds", "Select the region and trim its start just before the hit|Trim the end after the sound dies away|Name the region after its sound|"
     "Drop it onto a pad in Drum Machine Designer, if your version has it|Play the pad and check it",
     f"Class 2. Demonstrate on the projector. Trim the start of the region just before the transient, the sharp start of the sound, and not after it, or the hit will sound soft. Trim the end after the sound has died away, "
     f"and look for a short fade (if your version has one) to remove a click. Then add a Software Instrument track with Drum Machine Designer (if your version has it) and drop each sound onto its own pad. Menu names and button places move between versions; "
     f"the quick reference on page {pg('logicref')} hedges where they do. The trim checklist is on page {pg('roles')}."),
    (2, "pic", "The 4-bar step grid", "grid",
     f"Class 2. The model pattern on a step grid: 6 lanes, one for each sound, and 64 steps, which is 4 bars of 16. Each beat is 4 steps. The hits per bar are 14, 16, 17 and 18, 65 in all. "
     f"Different sounds can share a step, so they sound together. At 100 BPM a step lasts 0.15 seconds, so bar 2, grid step 14 (the tube tap) is at (16 + 13) × 0.15 = 4.35 seconds. "
     f"Students play their own pattern and draw it on the blank grid on page {pg('pattern')}. The Step Sequencer (if your version has it) shows the same grid."),
    (2, "pic", "Swing", "swing",
     f"Class 2. One beat is 4 steps. Swing delays every second step: in a 2:1 swing, a pair of steps is split into a long part and a short part, so grid steps 2 and 4 play 1/3 of a step late, which is 0.05 seconds at 100 BPM. "
     f"A common description of swing says the first note of each pair is often about twice as long as the second, and that the ratio can range from nearly even to about three to one. Software swing controls use their own scales, "
     f"so students listen and compare. Humanize adds tiny random timing and velocity changes, if your version has it. The swing page is page {pg('swing')}."),
    (3, "pic", "Arrange 16 bars", "arrange",
     f"Class 3. A 16-bar arrangement at 100 BPM: an intro in bars 1 to 4, a build in bars 5 to 8, the groove in bars 9 to 12 and an outro in bars 13 to 16. There are 6 layers, one for each sound. "
     f"The number row shows how many layers sound in each bar: 2, 3, 6 and 2. 16 bars of 2.4 seconds are 38.4 seconds, and the sections start at 0, 9.6, 19.2 and 28.8 seconds. "
     f"The arrangement page is page {pg('arrange')}."),
    (3, "bullets", "Mix: start with small moves", "Set the levels so every layer can be heard|High-pass the sounds that are not meant to be low|Start with a small move, then listen|Leave the kick alone: its job is low",
     f"Class 3. A high-pass filter lets higher sounds through and cuts the lows (a rumble filter is a high-pass filter used to remove unwanted low-frequency sounds). On the paper crinkle, the tape pull, the scissor snip and the bells, "
     f"low rumble from handling the object is not part of the sound, so try the high-pass filter in an EQ (such as Channel EQ, if your version has it) and move it a little at a time, listening after each move. Stop as soon as the sound feels thin. "
     f"The kick keeps its low end. The mix checklist is on page {pg('mix')}, and the quick reference is page {pg('logicref')}."),
    (3, "check", "What you turn in", "Bounced .mp3 or .wav, 16 bars long|Zipped .logicx project|Named: Your Name – Foley Beat|Timing page, role table and step grid|Reflection page|Rubric self-score and three questions",
     "Class 3. The submission checklist, shortened to fit the slide. Show where students hand in. The file name is Your Name, then Foley Beat. Check the length before students bounce: "
     "the bounce should run all 16 bars, which is 38.4 seconds at 100 BPM; the timing page shows how many seconds that is at other tempos."),
    (3, "rubric", "How it’s scored", "",
     "The rubric: five categories, each scored 1 to 5, for a total out of 25. Students score themselves first; the final grade is the average of their score and yours. "
     "The slide reads the 5 column of each category aloud. Hand out the rubric page so students can self-score before they present."),
    (3, "bullets", "Presentation day", "Play your beat from the top|Point out the sounds, the pattern and the sections|Your three questions for classmates|Answer at least 2 of each classmate’s questions",
     "Class 3, presentations. Each student plays the beat and points out the sounds, the pattern, the swing and the sections as they arrive, with their bar numbers. Students write three "
     "questions they want classmates to answer, and answer at least two of each classmate's. Ask the class which found sound they recognized first and when they noticed the build."),
    (3, "closer", "One last thing…", "Record it clean.|Trim it close.|Count the steps.|Then let the beat land.",
     "Close with the listening day: play a beat and ask the class whether they could tell what each sound was made from. A beat that nobody can place is a beat that was well planned and well timed. "
     "Ask a few students which choice did the most for their beat. No audio is included in this resource; the sounds are the students' own."),
]
SHOTS1 = [("pacing", "Pacing guide", "3 class periods, slide by slide"), ("roles", "Role table", "6 sounds, 4 roles"),
          ("pattern", "Step grid", "4 bars, 16 steps, 6 sounds")]
SHOTS2 = [1, 7, 9, 11, 12, 13]
SHOTS3 = [("timing", "Timing math"), ("sounds", "Sounds and safety"), ("roles", "Role table"), ("pattern", "Step grid"), ("swing", "Swing"), ("arrange", "Arrangement"),
          ("mix", "Mix"), ("example", "Worked example")]
PREVIEW_PICKS = ["pacing", "roles", "pattern", "arrange"]

COVER_A = "Record it, trim it, play it"
COVER_C = "Logic Pro · Found Sounds · Step Grid · Swing"
PDF_COVER = dict(a=26, b=42, c=15, art=5.0)
SQ_COVER = dict(a=36, b=140, c=27, art=470, gap=20)
SQ_B_LINES = ["Gift Wrap", "Foley Beat"]
SQ_SUB = "3 class periods · 6 to 8 found sounds, a 16-step beat"
SQ_HEADS = {1: ("Ready to teach Monday", 76, "Pacing, role table, step grid and the /25 rubric in one PDF", 28),
            2: ("Intro deck included", 76, f"{len(SLIDES)} editable slides (.pptx + PDF) with speaker notes on every slide", 28),
            3: ("Everything inside", 72, "Timing math, safety, role table, step grids, swing and worked example", 28)}
SQ_BANDS = {1: "Found sounds <em>·</em> roles <em>·</em> step grid <em>·</em> swing",
            2: "Role table <em>·</em> step grid <em>·</em> arrangement",
            3: f"{len(PLAN)} pages <em>·</em> US Letter PDF <em>·</em> no audio included"}



# ================================================================ small page helpers
CSS_CC = ("<style>table.cc td { text-align: center; padding: 2pt 3pt; font-size: 9.4pt; line-height: 1.15; } table.cc th { text-align: center; font-size: 9pt; } "
          "table.cc td.l { text-align: left; } table.cc tr.hi td { background: #eef5fb; }</style>")


def howto_page(n, wm=False):
    parts = [("Teacher pages", "howto", "example2", "How to use, overview, setup, pacing, teacher notes, Logic quick reference, worked example (2 pages)"),
             ("Student pages", "timing", "reflect", "Timing page, sounds and safety, role table, step grid, swing page, arrangement, mix checklist, "
              "project sheet (3 pages), rubric, vocabulary, feedback planner, reflection page"),
             ("Intro deck (separate file)", None, None, f"{len(SLIDES)} slides, .pptx + PDF, speaker notes on every slide")]
    trs = "".join(f"<tr><td><b>{a}</b></td><td style='white-space:nowrap'>{('pages ' + str(D.IX(f)) + '–' + str(D.IX(l))) if f else 'deck'}</td>"
                  f"<td>{u}</td></tr>" for a, f, l, u in parts)
    inner = (f'<div class="cols"><div>'
             f'{D.H2("What this is", True)}'
             f'<p style="font-size:12pt;line-height:1.45">A {CLASSES}-class-period found sound project for high school music technology. Every '
             f'student records 6 to 8 sounds from safe household objects (wrapping paper, tape, boxes, a tube, a small bell, or any paper and boxes), trims each one, gives it a drum role, '
             f'plays a 4-bar pattern on a 16-step grid, tries swing and humanize (if their version has them) and arranges and mixes 16 bars. Students plan the timing with simple arithmetic, present the result and reflect on it. It is an original Hudson Beat project.</p>'
             f'{D.H2("Quick start")}<ol>'
             f'<li style="margin-bottom:5pt">Read the pacing guide (page {D.IX("pacing")}) and the teacher notes (pages {D.IX("tn1")}–{D.IX("tn2")}).</li>'
             f'<li style="margin-bottom:5pt">Look at the timing page, the sounds page, the role table, the step grid and the swing page (pages {D.IX("timing")}–{D.IX("swing")}) and the setup (page {D.IX("setup")}).</li>'
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
             f'<li><b>Pace:</b> Class 1 plan and record; Class 2 trim, roles, pattern and swing; Class 3 arrangement, mix and presentations (page {D.IX("pacing")}, which also shows two and four periods).</li>'
             f'<li><b>Grading:</b> the rubric, /{RUBRIC_TOTAL}, the average of the student’s and your score (page {D.IX("rubric")}).</li></ul>'
             f'<div class="box" style="margin-top:6pt"><span class="k">In one sentence</span><p style="margin:0;font-size:12pt">Students learn that '
             f'a beat made from everyday sounds is planned: a tempo that sets the length of a step, clean recordings, a role for each sound, hits placed on a grid and layers that build.</p></div>'
             f'<p class="small" style="margin-top:6pt">Logic Pro is a product of Apple Inc. This resource is not affiliated with Apple.</p>'
             f'</div></div>')
    return D.page("How to use this resource", "START HERE", "Teacher", inner, n, key="howto")


def overview_page(n, wm=False):
    inner = (f'<div class="cols"><div>'
             f'<div class="box inv" style="margin-bottom:6pt"><span class="k">The project in one line</span><p style="margin:0;font-size:12pt">'
             f'<b>{TITLE}</b> · Found sounds, roles, step grid and mix · Logic Pro<br>Six to eight sounds you record yourself, one beat built from them.</p></div>'
             f'{D.H2("What students make")}'
             f'<p style="font-size:12.2pt;line-height:1.48">A beat of 16 bars, built in Logic Pro from 6 to 8 found sounds that students record themselves: wrapping paper, tape, a box, a tube, scissors on paper and a small bell, '
             f'or any paper and boxes. Each sound is trimmed and given a role: kick, snare, hat or percussion. A 4-bar pattern plays them on a 16-step grid, swing and humanize are tried (if the version has them), '
             f'and the sounds become the layers of an arrangement with an intro, a build, a groove and an outro. Students hand in a bounced file and the zipped .logicx project, plus their plans and a reflection, '
             f'then play the beat and take questions.</p>'
             f'{D.H2("What this project reinforces")}<p style="font-size:12pt;line-height:1.5">{TN_REINFORCES}</p>'
             f'{D.H2("Standards")}<p style="font-size:11.4pt">Supports the National Core Arts Standards for Music (Music Technology, high school): generating '
             f'and developing ideas (MU:Cr1.1, MU:Cr2.1), presenting work (MU:Pr6.1) and responding to it (MU:Re7.2).</p>'
             f'</div><div>'
             f'{D.H2("Goals", True)}<ul>' + "".join(f"<li style='font-size:12pt;line-height:1.45'>{g}</li>" for g in GOALS) + '</ul>'
             f'{D.H2("About Foley and the theme")}<div class="box acc-b" style="padding:5pt 9pt"><p style="margin:0 0 3pt;font-size:10.2pt;line-height:1.36">{FOLEY_NOTE}</p>'
             f'<p style="margin:0 0 3pt;font-size:10.2pt;line-height:1.36">{THEME}</p>'
             f'<p style="margin:0;font-size:10.2pt;line-height:1.36">{INCLUSIVE_NOTE}</p></div>'
             f'<div class="box" style="margin-top:6pt;padding:5pt 9pt"><span class="k">At a glance</span><p style="margin:0;font-size:10.2pt;line-height:1.38"><b>Grades</b> {GRADES_TEXT}, music technology or music production · '
             f'<b>Length</b> {CLASSES} class periods (two and four also shown) · <b>Software</b> Logic Pro · <b>You supply</b> Macs with Logic Pro, headphones, a microphone and a place to hand in files · '
             f'<b>Assessment</b> rubric, 5 categories scored 1–5, /{RUBRIC_TOTAL} (page {D.IX("rubric")})</p></div>'
             f'</div></div>')
    return D.page("Project overview", "OVERVIEW", "Found sound project", inner, n, key="overview")


def setup_page(n, wm=False):
    inner = (f'<style>.sb p, .sb li {{ font-size: 11.6pt; line-height: 1.44; margin-bottom: 5pt; }}</style><div class="cols"><div class="big sb">'
             f'{D.H2("You need", True)}<ul>'
             f'<li><b>A Mac with Logic Pro</b> for each student, and <b>headphones</b>.</li>'
             f'<li><b>A microphone</b>, shared if you must. A quiet corner with soft surfaces beats a loud room. A laptop’s built-in microphone will do for practice.</li>'
             f'<li><b>Safe household objects</b>: paper, tape, cardboard boxes and tubes, small bells. Students may bring their own with permission; keep a small box of spares in the room.</li>'
             f'<li><b>A place to hand in</b> the .mp3 or .wav files, the zipped .logicx and the reflection.</li>'
             f'<li><b>Printed student pages</b>, one set each (pages {D.IX("timing")}–{D.IX("reflect")}).</li></ul>'
             f'{D.H2("Before Class 1")}'
             + "".join(D.chk(c, 13, "font-size:11.6pt;margin-bottom:7pt") for c in [
                 f"Read the timing page (page {D.IX('timing')}) so you can answer ‘how long is one step at 100 BPM?’ and ‘how long are 16 bars?’",
                 f"Test a microphone in Logic Pro on one computer, and tap a box near it while watching the meter (page {D.IX('sounds')}).",
                 f"Open Logic Pro on a student computer and check which tools your version has: Drum Machine Designer, Quick Sampler, the Step Sequencer, an EQ with a high-pass filter (see page {D.IX('logicref')}).",
                 f"Read the worked example (pages {D.IX('example')}–{D.IX('example2')})."]) +
             f'</div><div class="big sb">'
             f'{D.H2("What to watch", True)}'
             f'<p style="font-size:11.4pt">Watch for a recording that clips or is full of room noise, a sound trimmed too late so that its start is cut off, hits that sit off the grid, and a mix so crowded that the sounds disappear. {TN_NOTE}</p>'
             f'<div class="box acc-b" style="margin-top:2pt"><span class="k">Safety and permission</span><ul style="margin:0">'
             f'<li style="font-size:11pt">Students ask permission before using an object, and an adult helps with anything beyond paper, tape, cardboard and small bells.</li>'
             f'<li style="font-size:11pt">No glass, no knives, no blades. Ordinary scissors only on paper, closed slowly, or use a pen click instead.</li>'
             f'<li style="font-size:11pt">Tap gently, and keep headphone volume low.</li></ul></div>'
             f'{D.H2("Not every family wraps gifts")}'
             f'<div class="box"><p style="margin:0;font-size:10.6pt;line-height:1.4">{INCLUSIVE_NOTE}</p></div>'
             f'<div class="box" style="margin-top:6pt"><span class="k">Their own recordings only</span><p style="margin:0;font-size:10.6pt;line-height:1.4">{VOICE_NOTE}</p></div>'
             f'</div></div>')
    return D.page("Setup and what to watch", "SETUP", "Teacher", inner, n, key="setup")


# ================================================================ the student pages
def tempo_rows():
    rows = []
    for bpm in TEMPOS:
        hi = ' class="hi"' if bpm == EX_BPM else ''
        b, e = ("<b>", "</b>") if bpm == EX_BPM else ("", "")
        rows.append(f"<tr{hi}><td>{b}{bpm}{e}</td><td>{dec(spb(bpm), 3)}</td><td>{b}{dec(step_len(bpm), 4)}{e}</td><td>{dec(bar_len(bpm), 3)}</td>"
                    f"<td>{dec(PAT_BARS * bar_len(bpm), 3)}</td><td>{dec(ARR_BARS * bar_len(bpm), 3)}</td></tr>")
    return "".join(rows)


def len_rows():
    return "".join(f"<tr><td><b>{t}</b></td>" + "".join(f"<td>{dec(nb * bar_len(t), 3)}</td>" for nb in LEN_BARS) + "</tr>" for t in LEN_TEMPOS)


def timing_page(n, wm=False):
    inner = (CSS_CC +
             f'<p style="margin:0 0 4pt;font-size:10.2pt;line-height:1.36">Step 1: plan the beat. In 4/4 there are 4 beats in a bar, and each beat holds four 16th-note steps, so a bar has 16 steps. '
             f'These formulas turn a tempo into seconds. Every number below is computed, so you can check your own arithmetic against it.</p>'
             f'<div class="cols" style="gap:10pt;align-items:flex-start"><div class="box acc-b" style="padding:5pt 9pt;flex:1.15"><span class="k">The formulas (4/4)</span>'
             f'<p style="margin:0 0 2pt;font-size:9.8pt"><b>Seconds per beat</b> = 60 ÷ BPM</p><p style="margin:0 0 2pt;font-size:9.8pt"><b>Seconds per 16th-note step</b> = 15 ÷ BPM</p>'
             f'<p style="margin:0 0 2pt;font-size:9.8pt"><b>Seconds per bar</b> = 240 ÷ BPM (16 steps, 4 beats)</p>'
             f'<p style="margin:0 0 2pt;font-size:9.8pt"><b>A hit on grid step s of bar b</b> is at ((b − 1) × 16 + (s − 1)) × 15 ÷ BPM seconds</p>'
             f'<p style="margin:0 0 2pt;font-size:9.8pt"><b>A piece of b bars</b> lasts b × 240 ÷ BPM seconds</p>'
             f'<p style="margin:0;font-size:9.8pt"><b>Example:</b> 100 BPM: 15 ÷ 100 = 0.15 s per step, and 240 ÷ 100 = 2.4 s per bar.</p></div>'
             f'<div class="box" style="padding:5pt 9pt;flex:1"><span class="k">Rounding rules</span><p style="margin:0;font-size:9.2pt;line-height:1.32">Seconds per beat, bar and section to 3 decimals and seconds per step to 4; '
             f'a 5 rounds up. So 15 ÷ 128 = 0.1172 seconds (the exact value is 0.1171875). The tables for 80, 100 and 120 BPM are exact.</p></div></div>'
             f'<span class="k" style="margin-top:5pt">How long is a step, a bar and a section?</span>'
             f'<table class="t cc" style="margin-top:1pt"><tr><th>BPM</th><th>Seconds per beat</th><th>Seconds per step</th><th>Seconds per bar</th><th>4-bar pattern (s)</th><th>16-bar arrangement (s)</th></tr>{tempo_rows()}</table>'
             f'<p class="small" style="margin:0 0 2pt;font-size:8.6pt">The shaded row is the worked example. The 16-bar arrangement lasts 16 × 240 ÷ BPM = 3840 ÷ BPM seconds, which is 38.4 seconds at 100 BPM.</p>'
             f'<span class="k" style="margin-top:3pt">How long is my piece? (lengths in seconds at three tempos)</span>'
             f'<table class="t cc" style="margin-top:1pt"><tr><th>BPM</th>' + "".join(f"<th>{nb} bars</th>" for nb in LEN_BARS) + f'</tr>{len_rows()}</table>'
             f'<p class="small" style="margin:0 0 3pt;font-size:8.6pt">At 80 BPM a bar is 3 s, at 100 BPM it is 2.4 s and at 120 BPM it is 2 s. A slower tempo makes the same 16 bars last longer.</p>'
             f'<div class="box" style="padding:5pt 9pt"><span class="k">Going the other way: how many bars fit in a time?</span>'
             f'<p style="margin:0 0 2pt;font-size:9.8pt;line-height:1.32">Bars = seconds × BPM ÷ 240. Check: 38.4 seconds at 100 BPM is 38.4 × 100 ÷ 240 = 16 bars. '
             f'Try it: 24 seconds at 120 BPM = 24 × 120 ÷ 240 = 12 bars, and 19.2 seconds at 100 BPM = 19.2 × 100 ÷ 240 = 8 bars.</p>'
             f'<div class="fl" style="margin:3pt 0 0;font-size:10pt"><b>My time:</b><span style="flex:0 0 0.8in"></span><b>s at</b><span style="flex:0 0 0.8in"></span><b>BPM = time × BPM ÷ 240 =</b><span></span><b>bars</b></div></div>'
             f'<div class="box acc-b" style="margin-top:5pt;padding:5pt 9pt"><span class="k">My plan</span>'
             f'<div class="fl" style="margin:3pt 0 3pt;font-size:10pt"><b>Tempo:</b><span></span><b>BPM</b><b style="margin-left:8pt">One step = 15 ÷ BPM =</b><span></span><b>s</b></div>'
             f'<div class="fl" style="margin:0 0 3pt;font-size:10pt"><b>One bar = 240 ÷ BPM =</b><span></span><b>s</b><b style="margin-left:8pt">One beat = 60 ÷ BPM =</b><span></span><b>s</b></div>'
             f'<div class="fl" style="margin:0;font-size:10pt"><b>My 4-bar pattern lasts</b><span style="flex:0 0 0.8in"></span><b>s</b><b style="margin-left:8pt">My 16 bars last</b><span style="flex:0 0 0.8in"></span><b>s</b></div></div>')
    return D.page("Timing page", "STUDENT", "Class 1", inner, n, wm, name=True, key="timing")


def source_rows():
    return "".join(f"<tr><td><b>{nm}</b></td><td class='l'>{use}</td><td class='l'>{how}</td><td>{PITCH_W[p].lower()}</td><td>{BRIGHT_W[b].lower()}</td><td>{LEN_W[ln].lower()}</td></tr>"
                   for nm, _, _, p, b, ln, use, how in SOUNDS)


def sounds_page(n, wm=False):
    def box(title, items, acc=False):
        return (f'<div class="box{" acc-b" if acc else ""}" style="padding:4pt 9pt"><span class="k">{title}</span>'
                + "".join(D.chk(c, 11, "font-size:9.6pt;line-height:1.26;margin-bottom:2pt") for c in items) + '</div>')
    inner = (CSS_CC +
             f'<p style="margin:0 0 3pt;font-size:10pt;line-height:1.34">Step 2: collect the sounds. Choose 6 to 8 sounds from safe household objects and record each one yourself, as a one-shot: one clean hit with a little silence before it. '
             f'Think like a Foley artist, who records everyday sounds to add to a film. Your recordings are the only sounds in your beat.</p>'
             f'<div style="margin:0 auto 2pt;width:80%">{D.body_svg(chain_body(1620, "chain page"))}</div>'
             f'<div class="cols" style="gap:9pt;align-items:flex-start"><div>' + box("Safety and permission", SAFETY[:3], True) + '</div><div>' + box("Safety, continued", SAFETY[3:]) +
             f'<div class="box acc-b" style="margin-top:3pt;padding:4pt 9pt"><p style="margin:0;font-size:9.2pt;line-height:1.28"><b>No wrapping paper?</b> {INCLUSIVE_NOTE}</p></div></div></div>'
             f'<span class="k" style="margin-top:3pt">Sound-source table: what to listen for</span>'
             f'<table class="t cc" style="margin-top:1pt;font-size:8.8pt"><tr><th>Sound</th><th>What to use</th><th>How to make it</th><th>Pitch</th><th>Brightness</th><th>Length</th></tr>{source_rows()}</table>'
             f'<p class="small" style="margin:1pt 0 2pt;font-size:8.4pt">Low, mid and high, dull and bright, and short and long are descriptions to listen for, not measurements. Your objects will sound different from this table.</p>'
             f'<div class="cols" style="gap:9pt;align-items:flex-start"><div>' +
             box("Record at a safe level", ["I set the input gain on the interface while I make my loudest hit, and I leave plenty of headroom.",
                                            "The track meter stays well below the top, and a take that clips is deleted and recorded again.",
                                            "Every take has a moment of silence before the hit and a clean end.",
                                            "I record each sound several times and keep the cleanest."], True) +
             '</div><div>'
             f'<span class="k">Take log (6 to 8 sounds)</span>'
             f'<table class="t cc" style="margin-top:1pt"><tr><th>Sound</th><th>Object</th><th>Takes</th><th>Best take</th></tr>'
             + "".join("<tr><td style='height:15pt'></td><td></td><td></td><td></td></tr>" for _ in range(4)) + '</table></div></div>')
    return D.page("Sounds, safety and recording", "STUDENT", "Class 1", inner, n, wm, name=True, key="sounds")


def role_rows():
    return "".join(f"<tr><td><b>{r}</b></td><td class='l'>{job}</td><td class='l'>{ex}</td></tr>" for r, job, ex in ROLES)


def roles_page(n, wm=False):
    def box(title, items, acc=False):
        return (f'<div class="box{" acc-b" if acc else ""}" style="padding:4pt 9pt"><span class="k">{title}</span>'
                + "".join(D.chk(c, 11, "font-size:9.8pt;line-height:1.28;margin-bottom:2.5pt") for c in items) + '</div>')
    blank = "".join("<tr><td style='height:17pt'></td><td></td><td></td><td></td><td></td><td></td></tr>" for _ in range(8))
    inner = (CSS_CC +
             f'<p style="margin:0 0 3pt;font-size:10.2pt;line-height:1.36">Step 3: trim and assign roles. Trim each recording to its first hit, then give it a job in the beat, the way a drum kit has a kick, a snare and a hat. '
             f'The model below has {NSND} sounds and {len(ROLES)} roles. Fill in your own table for your 6 to 8 sounds.</p>'
             f'<div style="margin:0 0 3pt">{D.body_svg(roles_body(1600, "roles page"))}</div>'
             f'<div class="cols" style="gap:10pt;align-items:flex-start"><div style="flex:1.25"><span class="k" style="margin-top:2pt">The four roles</span>'
             f'<table class="t cc" style="margin-top:1pt"><tr><th>Role</th><th>Its job</th><th>In the model</th></tr>{role_rows()}</table></div>'
             f'<div style="flex:1">' + box("Trim checklist", ["The region starts just before the transient, the sharp start of the sound.", "The end comes after the sound has died away, with no click.",
                                                              "The region is named after its sound and its role.", "I play it on its pad and it sounds the same every time."], True) + '</div></div>'
             f'<span class="k" style="margin-top:4pt">My role table (6 to 8 sounds)</span>'
             f'<table class="t cc" style="margin-top:1pt"><tr><th>Sound</th><th>Object</th><th>Role</th><th>Pitch</th><th>Brightness</th><th>Length</th></tr>{blank}</table>')
    return D.page("Role table and trimming", "STUDENT", "Class 2", inner, n, wm, name=True, key="roles")


def pat_rows():
    rows = []
    for nm in LANES:
        rows.append(f"<tr><td class='l'><b>{nm.title()}</b></td>" + "".join(f"<td>{len(PATTERN[nm][b])}</td>" for b in range(PAT_BARS)) + f"<td><b>{LANE_HITS[nm]}</b></td></tr>")
    rows.append("<tr class='hi'><td class='l'><b>All sounds</b></td>" + "".join(f"<td><b>{h}</b></td>" for h in PAT_HITS) + f"<td><b>{PAT_TOTAL}</b></td></tr>")
    return "".join(rows)


def pattern_page(n, wm=False):
    inner = (CSS_CC +
             f'<p style="margin:0 0 3pt;font-size:10.2pt;line-height:1.36">Step 4: build the pattern. A pattern is a set of hits that repeats. Each lane is one of your sounds and each column is one 16th-note step, so a bar has 16 steps '
             f'and the 4-bar pattern has {PAT_BARS * STEPS_BAR}. Different sounds can share a step, so they play together. Play your own pattern, then draw it on the blank grid.</p>'
             f'<div style="margin:0 0 2pt">{D.body_svg(grid_body(1600, "grid page"))}</div>'
             f'<div class="cols" style="gap:10pt;align-items:flex-start"><div style="flex:1.2"><span class="k" style="margin-top:2pt">Hits in the model pattern</span>'
             f'<table class="t cc" style="margin-top:1pt"><tr><th>Sound</th><th>Bar 1</th><th>Bar 2</th><th>Bar 3</th><th>Bar 4</th><th>All bars</th></tr>{pat_rows()}</table>'
             f'<p class="small" style="margin:1pt 0 0;font-size:8.6pt">Hits per bar: {PAT_HITS[0]}, {PAT_HITS[1]}, {PAT_HITS[2]} and {PAT_HITS[3]}, {PAT_TOTAL} in all. The lanes add up to the same {sum(LANE_HITS.values())}.</p></div>'
             f'<div class="box acc-b" style="padding:4pt 9pt;flex:1"><span class="k">Reading the grid</span>'
             f'<p style="margin:0 0 2pt;font-size:9.4pt;line-height:1.32">A hit on grid step s of bar b starts at ((b − 1) × 16 + (s − 1)) × 15 ÷ BPM seconds. At 100 BPM, bar 2, grid step 14 (the tube tap) is at (16 + 13) × 0.15 = 4.35 s.</p>'
             f'<p style="margin:0;font-size:9.4pt;line-height:1.32">The box tap plays on grid steps 1, 7 and 11 and the tape pull on 5 and 13, which are beats 2 and 4. Velocity sets how hard each hit is, if your version shows one for each step.</p></div></div>'
             f'<span class="k" style="margin-top:4pt">My pattern: draw a hit in the lane of each sound you play</span>'
             f'<div style="margin:1pt 0 2pt">{D.body_svg(grid_body(1600, "grid blank page", blank=True))}</div>'
             f'<div class="fl" style="margin:2pt 0 0;font-size:10pt"><b>My hits per bar:</b><span></span><b>Total:</b><span style="flex:0 0 0.8in"></span><b>Bar 2 starts at (s):</b><span style="flex:0 0 0.8in"></span></div>')
    return D.page("The 4-bar step grid", "STUDENT", "Class 2", inner, n, wm, name=True, key="pattern")


def swing_rows():
    rows = []
    for r in SWING_RATIOS:
        d = swing_delay_steps(r)
        nm = "straight" if r == 1 else f"{exact(r)}:1"
        rows.append(f"<tr><td><b>{nm}</b></td><td>{fs(Fraction(2) * r / (r + 1))}</td><td>{fs(d)}</td><td>{exact(d * step_len(EX_BPM))}</td></tr>")
    return "".join(rows)


def swing_page(n, wm=False):
    inner = (CSS_CC +
             f'<p style="margin:0 0 3pt;font-size:10.2pt;line-height:1.36">Step 5: swing and humanize. Swing delays every second step of a pair, so the pair is long and short instead of even. Humanize makes tiny random changes to timing and velocity, '
             f'so a pattern sounds less like a machine. Look for a swing control and a humanize option (each if your version has them); their scales differ, so listen and compare.</p>'
             f'<div style="margin:0 auto 3pt;width:90%">{D.body_svg(swing_body(1500, "swing page"))}</div>'
             f'<div class="cols" style="gap:10pt;align-items:flex-start"><div style="flex:1.2"><span class="k" style="margin-top:2pt">The idea in numbers (an example, not a Logic setting)</span>'
             f'<table class="t cc" style="margin-top:1pt"><tr><th>Long : short</th><th>2nd step starts at (steps)</th><th>Late by (steps)</th><th>Late by at {EX_BPM} BPM (s)</th></tr>{swing_rows()}</table>'
             f'<p class="small" style="margin:1pt 0 0;font-size:8.6pt">Two steps make a pair. Split long : short = r : 1, the second step starts at 2r ÷ (r + 1) steps instead of 1, so it is late by (r − 1) ÷ (r + 1) of a step. '
             f'For 2 : 1 that is 1/3 of a step: 0.15 ÷ 3 = 0.05 s at 100 BPM.</p></div>'
             f'<div class="box acc-b" style="padding:4pt 9pt;flex:1"><span class="k">Which hits does swing move?</span>'
             f'<p style="margin:0 0 2pt;font-size:9.4pt;line-height:1.32">A 16th-note swing moves the hits on even steps (2, 4, 6 and so on). In the model, {EVEN_HITS} of the {PAT_TOTAL} hits are on even steps: the scissor snips and two tube taps. '
             f'The crinkles are on odd steps, so they stay put.</p>'
             f'<p style="margin:0;font-size:9.4pt;line-height:1.32">One common description of swing says the first note of a pair is often about twice as long as the second. Try a little first.</p></div></div>'
             f'<span class="k" style="margin-top:4pt">Velocity and humanize: small changes</span>'
             + "".join(D.chk(c, 11, "font-size:9.8pt;line-height:1.28;margin-bottom:2pt") for c in [
                 "I make the hits on the beat a little louder and the others a little softer, with velocity (if my version shows it).",
                 "I try a humanize option for timing and velocity (if my version has one) and keep the changes small.",
                 "I play the pattern straight, then swung, then humanized, and listen to all three."]) +
             f'<span class="k" style="margin-top:4pt">My comparison</span>'
             f'<table class="t cc" style="margin-top:1pt"><tr><th>Version</th><th>Setting I used</th><th>What I heard</th></tr>'
             + "".join(f"<tr><td style='height:26pt'><b>{v}</b></td><td></td><td></td></tr>" for v in ("Straight", "Swung", "Humanized")) + '</table>'
             f'<div class="fl" style="margin:3pt 0 0;font-size:10pt"><b>I chose:</b><span></span><b>because</b><span></span></div>')
    return D.page("Swing and humanize", "STUDENT", "Class 2", inner, n, wm, name=True, key="swing")


def sec_rows():
    rows = []
    for nm, a, b in ARR_SECTIONS:
        layers = [r for r, spans in ARR_ROWS if any(x <= b and a <= y for x, y in spans)]
        rows.append(f"<tr><td><b>{nm.title()}</b></td><td>{a}–{b}</td><td>{exact(hit_time(EX_BPM, a, 1))}</td><td>{exact(hit_time(EX_BPM, b + 1, 1))}</td>"
                    f"<td class='l'>{', '.join(x.lower() for x in layers)}</td></tr>")
    return "".join(rows)


def arrange_page(n, wm=False):
    mine = "".join("<tr><td style='height:19pt'></td><td></td><td></td><td></td></tr>" for _ in range(4))
    inner = (CSS_CC +
             f'<p style="margin:0 0 3pt;font-size:10.2pt;line-height:1.36">Step 6: layer, arrange and mix. An arrangement puts your sounds into sections. This one is {ARR_BARS} bars, four sections of {SEC_BARS}: an intro, a build, '
             f'the groove and an outro. Each of your sounds is a layer, and this model has {len(ARR_ROWS)} layers. Sounds join and leave so the listener hears the beat grow and then settle.</p>'
             f'<div style="margin:0 0 3pt">{D.body_svg(arr_body(1600, "arrange page"))}</div>'
             f'<div class="cols" style="gap:10pt;align-items:flex-start"><div style="flex:1.6"><span class="k" style="margin-top:2pt">The sections at {EX_BPM} BPM</span>'
             f'<table class="t cc" style="margin-top:1pt"><tr><th>Section</th><th>Bars</th><th>Starts (s)</th><th>Ends (s)</th><th>Layers that play</th></tr>{sec_rows()}</table></div>'
             f'<div style="flex:1"><span class="k" style="margin-top:2pt">Layer-bars in the model</span>'
             f'<table class="t cc" style="margin-top:1pt"><tr><th>Layer</th><th>Bars</th></tr>'
             + "".join(f"<tr><td class='l'>{r.title()}</td><td>{len(bars_of(r))}</td></tr>" for r in ARR_LAYERS) + '</table></div></div>'
             f'<p class="small" style="margin:1pt 0 2pt;font-size:8.6pt">The layers play {sum(len(bars_of(r)) for r in ARR_LAYERS)} bars in all: {" + ".join(str(len(bars_of(r))) for r in ARR_LAYERS)}. The number row on the map adds to the same {sum(len(layers_in_bar(b)) for b in range(1, ARR_BARS + 1))}. '
             f'Length = bars × 240 ÷ BPM: at {EX_BPM} BPM, {ARR_BARS} bars × 2.4 s = {fmt(ARR_BARS * EX_BAR_S)} s.</p>'
             f'<span class="k" style="margin-top:3pt">My arrangement (my tempo: ________ BPM)</span>'
             f'<table class="t cc" style="margin-top:1pt"><tr><th>Section</th><th>Bars</th><th>Starts at (s)</th><th>Layers that play</th></tr>{mine}</table>'
             f'<div class="box acc-b" style="margin-top:4pt;padding:4pt 9pt"><span class="k">Check my arrangement</span>'
             + "".join(D.chk(c, 11, "font-size:9.8pt;line-height:1.28;margin-bottom:2pt") for c in [
                 "My sections are the same number of bars, and together they make 16 bars.",
                 "The beat builds: the groove has more layers than the intro.",
                 "I can say which layer joins in which bar, and the number of layers in each bar matches my map."]) + '</div>')
    return D.page("Arrangement map", "STUDENT", "Class 3", inner, n, wm, name=True, key="arrange")


def mix_page(n, wm=False):
    def box(title, items, acc=False):
        return (f'<div class="box{" acc-b" if acc else ""}" style="padding:5pt 9pt"><span class="k">{title}</span>'
                + "".join(D.chk(c, 11, "font-size:10pt;line-height:1.3;margin-bottom:3pt") for c in items) + '</div>')
    inner = (f'<p style="margin:0 0 5pt;font-size:10.2pt;line-height:1.36">Step 6: layer, arrange and mix, continued. A mix makes every layer clear. Work through the boxes with headphones at a low volume, '
             f'then check each one off. Make small moves and listen after each one.</p>'
             f'<div class="cols" style="gap:10pt;align-items:flex-start"><div>'
             + box("Clean up the rumble (EQ high-pass)", ["I add an EQ with a high-pass filter on the paper, tape, snip and bell tracks, if my version has one.",
                                                       "I start with a small move, listen, and stop when the sound starts to feel thin.",
                                                       "I leave the box tap alone: its job is low."], True)
             + '<div style="height:6pt"></div>'
             + box("Levels", ["I can hear every layer, and I make a loud layer quieter before I make a quiet layer louder.",
                              "The master meter stays below 0 dBFS with plenty of room to spare.",
                              "I listened at a normal volume, not only loud."])
             + '</div><div>'
             + box("Layers and sections", ["I can find every layer on my arrangement map by listening.", "The intro, build, groove and outro are the lengths on my map.",
                                           "The groove is the fullest part, and the outro strips back."], True)
             + '<div style="height:6pt"></div>'
             + box("Feel", ["The swing or humanize setting I chose sounds natural, not sloppy.", "No hit clicks or starts late because of the trim.",
                            "When I mute the quietest layer, I can tell it is gone."])
             + '</div></div>'
             f'<div class="box" style="margin-top:6pt;padding:5pt 9pt"><span class="k">The listening test</span><p style="margin:0 0 3pt;font-size:10pt;line-height:1.36">Play the whole beat with your eyes closed and '
             f'rate each part from 1 (weak) to 5 (very strong). Can you tell what each sound is? Does the pattern feel steady? Does the build land? Write what you hear:</p>'
             f'<div class="fl" style="margin:2pt 0;font-size:10pt"><b>Sounds:</b><span></span><b>Pattern:</b><span></span><b>Build:</b><span></span></div></div>'
             f'<div class="box acc-b" style="margin-top:6pt;padding:5pt 9pt"><span class="k">Bounce</span>'
             + "".join(D.chk(c, 11, "font-size:10pt;margin-bottom:3pt") for c in [
                 "The bounce starts at bar 1 and ends at the planned length (16 bars; check the seconds for my tempo on page " + str(pg("timing")) + ").",
                 "MP3 or WAV bounced, and the .logicx project zipped.", f"Both files named {FILE_NAME}."]) + '</div>'
             f'<span class="k" style="margin-top:6pt">What I changed after the listening test</span>' + D.lines(7, 24))
    return D.page("Mix checklist", "STUDENT", "Class 3", inner, n, wm, name=True, key="mix")


# ================================================================ worked example (2 pages)
def ex_snd_rows():
    return "".join(f"<tr><td><b>{nm.title()}</b></td><td>{role.title()}</td><td>{PITCH_W[p].lower()}</td><td>{BRIGHT_W[b].lower()}</td><td>{LEN_W[ln].lower()}</td><td>{LANE_HITS[nm]}</td></tr>"
                   for nm, _, role, p, b, ln, _, _ in SOUNDS)


def ex_bar_rows():
    return "".join(f"<tr><td><b>{b + 1}</b></td><td>{PAT_HITS[b]}</td><td>{exact(hit_time(EX_BPM, b + 1, 1))}</td><td>{exact(hit_time(EX_BPM, b + 2, 1))}</td></tr>" for b in range(PAT_BARS))


def ex_layer_rows():
    return "".join(f"<tr><td><b>{nm.title()}</b></td><td>{spans_text(spans)}</td><td>{len(bars_of(nm))}</td></tr>" for nm, spans in ARR_ROWS)


def ex_len_rows():
    return "".join(f"<tr><td><b>{t}</b></td><td>{dec(bar_len(t), 3)}</td><td>{dec(PAT_BARS * bar_len(t), 3)}</td><td>{dec(ARR_BARS * bar_len(t), 3)}</td></tr>" for t in LEN_TEMPOS)


def example_page(n, wm=False):
    inner = (f'<style>table.ec td {{ text-align: center; }}</style>'
             f'<p style="margin:0 0 4pt;font-size:10pt">An <b>invented plan on paper</b>: a beat at {EX_BPM} BPM from {NSND} found sounds. No audio is included. '
             f'Student projects will differ. Page 1 of 2: the plan, the sounds and the pattern.</p>'
             f'<div class="cols" style="gap:10pt;align-items:flex-start"><div class="box"><span class="k">1 · A weak plan</span><p style="margin:0;font-size:10.2pt">{EX_WEAK}</p>'
             f'<p style="margin:3pt 0 0;font-size:9.2pt">It names no tempo, no sounds, no roles, no pattern and no sections.</p></div>'
             f'<div class="box acc-b"><span class="k">2 · A clear plan</span><p style="margin:0;font-size:8.6pt;line-height:1.28">{EX_STRONG}</p></div></div>'
             f'{D.H2("3 · The sounds, their roles and their hits")}'
             f'<table class="t ec" style="font-size:8.8pt;line-height:1.14"><tr><th>Sound</th><th>Role</th><th>Pitch</th><th>Brightness</th><th>Length</th><th>Hits in the pattern</th></tr>{ex_snd_rows()}</table>'
             f'<p style="margin:2pt 0 0;font-size:8.8pt;line-height:1.3">The {NSND} sounds play {PAT_TOTAL} hits in all ({" + ".join(str(LANE_HITS[l]) for l in LANES)}). At {EX_BPM} BPM one step is 15 ÷ {EX_BPM} = {exact(EX_STEP_S)} s and one bar is {fmt(EX_BAR_S)} s. '
             f'The words in the table are listening descriptions, not measurements.</p>'
             f'{D.H2("4 · The 4-bar step grid at 100 BPM")}'
             f'<div class="cols" style="gap:10pt;align-items:flex-start"><div style="flex:0 0 3.4in"><table class="t ec" style="font-size:8.8pt;line-height:1.14"><tr><th>Bar</th><th>Hits</th><th>Starts (s)</th><th>Ends (s)</th></tr>{ex_bar_rows()}</table></div>'
             f'<p style="margin:0;font-size:8.8pt;line-height:1.3">The pattern has {PAT_HITS[0]}, {PAT_HITS[1]}, {PAT_HITS[2]} and {PAT_HITS[3]} hits, {PAT_TOTAL} in all, on a grid of {PAT_BARS} bars of {STEPS_BAR} steps = {PAT_BARS * STEPS_BAR} steps. '
             f'It lasts {PAT_BARS} × {fmt(EX_BAR_S)} = {fmt(PAT_BARS * EX_BAR_S)} seconds. The tube tap on bar 2, grid step 14 starts at (16 + 13) × {exact(EX_STEP_S)} = {exact(hit_time(EX_BPM, 2, 14))} s. '
             f'The box tap and the tape pull never share a step: they play on grid steps 1, 7, 11 and 5, 13.</p></div>'
             f'<div style="margin:3pt auto 3pt;width:80%">{D.body_svg(grid_body(1600, "grid page"))}</div>'
             f'<div class="box" style="margin-top:4pt;padding:4pt 9pt"><span class="k">What to notice</span><p style="margin:0;font-size:9.2pt;line-height:1.3">{EX_NOTE[0].upper() + EX_NOTE[1:]}.</p></div>')
    return D.page("Worked example · the plan, the sounds and the pattern", "EXAMPLE", "Teacher", inner, n, wm, ak=True, key="example")


def example2_page(n, wm=False):
    qs = " ".join(f"{i + 1}. {q}" for i, q in enumerate(EX_QUESTIONS))
    inner = (f'<p style="margin:0 0 3pt;font-size:10pt">The same beat, page 2 of 2: the swing, the timing and the arrangement, then the moments to point out.</p>'
             f'{D.H2("5 · The swing choice")}'
             f'<p style="margin:0;font-size:9.6pt;line-height:1.34">The student plays the pattern straight, then swung 2 : 1, where grid steps 2 and 4 of each beat play 1/3 of a step late, which is {exact(swing_delay_steps(Fraction(2)) * EX_STEP_S)} s at {EX_BPM} BPM. '
             f'Only the {EVEN_HITS} hits on even steps move; the crinkles stay put. They keep it small.</p>'
             f'{D.H2("6 · The timing at three tempos")}'
             f'<table class="t ec" style="font-size:8.8pt;line-height:1.14"><tr><th>BPM</th><th>One bar (s)</th><th>4-bar pattern (s)</th><th>16-bar arrangement (s)</th></tr>{ex_len_rows()}</table>'
             f'{D.H2("7 · The 16-bar arrangement")}'
             f'<div style="margin:1pt auto 3pt;width:72%">{D.body_svg(arr_body(1600, "arrange page"))}</div>'
             f'<div class="cols" style="gap:10pt;align-items:flex-start"><div style="flex:0 0 3.3in"><table class="t ec" style="font-size:8.8pt;line-height:1.14"><tr><th>Layer</th><th>Bars it plays</th><th>Bars</th></tr>{ex_layer_rows()}</table></div>'
             f'<p style="margin:0;font-size:9pt;line-height:1.32">{ARR_BARS} bars × {fmt(EX_BAR_S)} s = {fmt(ARR_BARS * EX_BAR_S)} s. The intro starts at {exact(hit_time(EX_BPM, 1, 1))} s, the build at {exact(hit_time(EX_BPM, 5, 1))} s, '
             f'the groove at {exact(hit_time(EX_BPM, 9, 1))} s and the outro at {exact(hit_time(EX_BPM, 13, 1))} s. The layers play {sum(len(bars_of(r)) for r in ARR_LAYERS)} bars in all. '
             f'In the mix, the paper, tape, snip and bell tracks get a small high-pass move; the box tap does not.</p></div>'
             f'<div class="box" style="margin-top:5pt"><span class="k">8 · Three feedback questions (invented)</span><p style="margin:0;font-size:10pt;line-height:1.36">{qs}</p></div>'
             f'<div class="box acc-b" style="margin-top:5pt"><span class="k">9 · Moments to point out in class</span><ul style="margin:0">'
             f'<li style="font-size:10pt;margin-bottom:2pt">Every sound in the beat started as an everyday object, so the role table explains everything the listener hears.</li>'
             f'<li style="font-size:10pt;margin-bottom:0">At {EX_BPM} BPM a step is exactly 0.15 s and a bar exactly 2.4 s, so the class can count bars and hear each layer arrive.</li></ul></div>')
    return D.page("Worked example · the swing, the timing and the arrangement", "EXAMPLE", "Teacher", inner, n, wm, ak=True, key="example2")


PAGES = {"howto": howto_page, "overview": overview_page, "setup": setup_page, "example": example_page, "example2": example2_page,
         "timing": timing_page, "sounds": sounds_page, "roles": roles_page, "pattern": pattern_page, "swing": swing_page, "arrange": arrange_page, "mix": mix_page}


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


def proj2_roomy(n, wm=False):
    """The shared requirements-and-steps page at a larger size, so the page does not end with a wide blank band (the shared builder stays untouched)."""
    global PROJ_SIZE
    old = PROJ_SIZE
    PROJ_SIZE = 12.2
    try:
        return D.proj2_page(n, wm)
    finally:
        PROJ_SIZE = old


PAGES["proj2"] = proj2_roomy

# ================================================================ content-check helpers (shared with 067/076/083/087)

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






BADGE = {"timing": "Class 1", "sounds": "Class 1", "roles": "Class 2", "pattern": "Class 2", "swing": "Class 2", "arrange": "Class 3", "mix": "Class 3",
         "present": f"Classes {CLASSES - 1}–{CLASSES}"}


FORBIDDEN_WORDS = ("cham" + "pagne", "toast", "cheers", "wine", "beer", "cocktail", "alcohol", "bub" + "bly", "church", "prayer", "pray ", "blessing", "holy", "sacred",
                   "religio", "god ", "santa", "christmas", "hanukkah", "chanukah", "kwanzaa", "holiday", "sleigh", "reindeer", "ornament", "carol", "elf ", "elves", "sale", "shopping", "buy ")
EXPECT_STEP = {"timing": {1}, "sounds": {2}, "roles": {3}, "pattern": {4}, "swing": {5}, "arrange": {6}, "mix": {6}}


def svg_count(svg, cls):
    return len(re.findall(rf'class="{cls}"', svg))


def verify_content():
    errs = []
    counts = dict(goals=(GOALS, 4), vocab=(VOCAB, 8), reqs=(REQS, 7), steps=(STEPS, 7), tips=(TIPS, 4), check=(CHECK, 6),
                  rubric=(RUBRIC, 5), struggles=(STRUGGLES, 4), resources=(RESOURCES, 5), slides=(SLIDES, 18), plan=(PLAN, 25),
                  logic=(LOGIC_REF, 9), sounds=(SOUNDS, 6), roles=(ROLES, 4), arrange=(ARR_ROWS, 6), sections=(ARR_SECTIONS, 4), safety=(SAFETY, 5))
    for nm, (lst, nexp) in counts.items():
        if len(lst) != nexp:
            errs.append(f"{nm}: {len(lst)} items, expected {nexp}")
    if RUBRIC_TOTAL != 25 or LEVELS != [1, 2, 3, 4, 5] or len(RUBRIC_SHORT) != 5:
        errs.append("rubric is /25, levels 1-5")
    if FILE_NAME not in CHECK[2]:
        errs.append("file name format must be on the checklist")
    if [w for w, _ in VOCAB] != ["Foley", "Found sound", "Sample", "Transient", "One-shot", "Velocity", "Swing", "Humanize"]:
        errs.append("vocabulary: foley, found sound, sample, transient, one-shot, velocity, swing, humanize")
    if set(TAGS) & {"Holiday", "Student Practice", "Theme", "Seasonal"} or "Performing Arts" in SUBJECTS:
        errs.append("tags and subjects must not be headings")
    if len(LISTING_TITLE) > 80 or "Logic Pro" not in LISTING_TITLE[:30]:
        errs.append("listing title: at most 80 characters, 'Logic Pro' in the first 30")
    for w in ("new year", "winter", "holiday", "christmas", "hanukkah", "chanukah", "sleigh", "carol", "snow", "eve ", "bells", "gift", "wrap"):
        if w in LISTING_TITLE.lower():
            errs.append(f"the listing title must not hold the seasonal word {w}")
    if len(STEP_NAMES) != len(STEPS) or any(not s.startswith(f"<b>{nm}</b>") for s, nm in zip(STEPS, STEP_NAMES)):
        errs.append("STEPS must start with the bold names in STEP_NAMES (the pages cite them)")
    # ---- the tempo arithmetic for 4/4, by hand first
    if [spb(b) for b in (120, 90, 100, 80, 110, 128)] != [Fraction(1, 2), Fraction(2, 3), Fraction(3, 5), Fraction(3, 4), Fraction(6, 11), Fraction(15, 32)]:
        errs.append("seconds per beat = 60 / BPM: 0.5 at 120, 0.6667 at 90, 0.6 at 100, 0.75 at 80, 0.5455 at 110, 0.46875 at 128")
    if [step_len(b) for b in (80, 100, 120)] != [Fraction(3, 16), Fraction(3, 20), Fraction(1, 8)] or [bar_len(b) for b in (80, 100, 120)] != [Fraction(3), Fraction(12, 5), Fraction(2)]:
        errs.append("a step = 15 / BPM (0.1875, 0.15, 0.125 s at 80, 100, 120 BPM) and a bar = 240 / BPM (3, 2.4, 2 s)")
    for b in TEMPOS:
        if bar_len(b) != BEATS_BAR * spb(b) or bar_len(b) != STEPS_BAR * step_len(b) or abs(float(bar_len(b)) - 240.0 / b) > 1e-12 or abs(float(step_len(b)) - 15.0 / b) > 1e-12 or \
           abs(float(spb(b)) - 60.0 / b) > 1e-12:
            errs.append(f"a bar of 4/4 is 4 beats and 16 steps at {b} BPM")
        if PAT_BARS * bar_len(b) != Fraction(960, b) or ARR_BARS * bar_len(b) != Fraction(3840, b):
            errs.append(f"4 bars = 960 / BPM and 16 bars = 3840 / BPM at {b} BPM")
    if [dec(spb(b), 3) for b in TEMPOS] != ["0.750", "0.667", "0.600", "0.545", "0.500", "0.469"] or \
       [dec(step_len(b), 4) for b in TEMPOS] != ["0.1875", "0.1667", "0.1500", "0.1364", "0.1250", "0.1172"] or \
       [dec(bar_len(b), 3) for b in TEMPOS] != ["3.000", "2.667", "2.400", "2.182", "2.000", "1.875"]:
        errs.append("seconds per beat, step and bar, rounded half up")
    if [dec(PAT_BARS * bar_len(b), 3) for b in TEMPOS] != ["12.000", "10.667", "9.600", "8.727", "8.000", "7.500"] or \
       [dec(ARR_BARS * bar_len(b), 3) for b in TEMPOS] != ["48.000", "42.667", "38.400", "34.909", "32.000", "30.000"]:
        errs.append("4-bar and 16-bar lengths at the six tempos")
    want = {80: ["12.000", "24.000", "48.000", "96.000"], 100: ["9.600", "19.200", "38.400", "76.800"], 120: ["8.000", "16.000", "32.000", "64.000"]}
    for t in LEN_TEMPOS:
        if [dec(nb * bar_len(t), 3) for nb in LEN_BARS] != want[t] or [float(nb * bar_len(t)) for nb in LEN_BARS] != [nb * 240.0 / t for nb in LEN_BARS] and \
           any(abs(float(nb * bar_len(t)) - nb * 240.0 / t) > 1e-9 for nb in LEN_BARS):
            errs.append(f"lengths of 4, 8, 16 and 32 bars at {t} BPM")
    if rnd(Fraction(5, 2), 0) != 3 or dec(Fraction(15, 128), 4) != "0.1172":
        errs.append("round half up")
    if [exact(hit_time(EX_BPM, a, 1)) for _, a, _ in ARR_SECTIONS] != ["0", "9.6", "19.2", "28.8"] or hit_time(EX_BPM, 17, 1) != Fraction(192, 5) or ARR_BARS * EX_BAR_S != Fraction(192, 5) or \
       EX_BAR_S != Fraction(12, 5) or EX_STEP_S != Fraction(3, 20) or hit_time(EX_BPM, 2, 14) != Fraction(87, 20):
        errs.append("100 BPM: a step is 0.15 s, a bar 2.4 s, sections start at 0, 9.6, 19.2 and 28.8 s, 16 bars = 38.4 s, bar 2 step 14 = 4.35 s")
    if abs(float(hit_time(EX_BPM, 2, 14)) - ((2 - 1) * 16 + (14 - 1)) * 15.0 / 100) > 1e-12:
        errs.append("hit time formula, float method")
    # ---- swing arithmetic: r:1 split of a pair of two steps
    if [swing_delay_steps(r) for r in SWING_RATIOS] != [Fraction(0), Fraction(1, 5), Fraction(1, 3), Fraction(1, 2)] or \
       [exact(swing_delay_steps(r) * step_len(EX_BPM)) for r in SWING_RATIOS] != ["0", "0.03", "0.05", "0.075"]:
        errs.append("swing delays: 0, 1/5, 1/3 and 1/2 of a step = 0, 0.03, 0.05 and 0.075 s at 100 BPM")
    for r in SWING_RATIOS:
        first = 2 * r / (r + 1)
        if first / (2 - first) != r:
            errs.append(f"a pair split {r}:1 has a long part {r} times the short part")
    # ---- the sounds and roles
    if [s[0] for s in SOUNDS] != ["BOX TAP", "TUBE TAP", "TAPE PULL", "PAPER CRINKLE", "SCISSOR SNIP", "BELLS"] or [s[2] for s in SOUNDS] != ["KICK", "PERC", "SNARE", "HAT", "PERC", "PERC"]:
        errs.append("the six sounds and their roles: box tap kick, tube tap perc, tape pull snare, paper crinkle hat, scissor snip perc, bells perc")
    if {s[2] for s in SOUNDS} != {r for r, _, _ in ROLES} or any(not (1 <= v <= 3) for s in SOUNDS for v in s[3:6]):
        errs.append("every role is used by a sound, and pitch, brightness and length are 1 to 3")
    if LANES != [s[0] for s in SOUNDS] or set(PATTERN) != set(LANES) or set(ARR_LAYERS) != set(LANES):
        errs.append("pattern lanes and arrangement layers are the six sounds")
    # ---- the pattern
    for nm in LANES:
        if len(PATTERN[nm]) != PAT_BARS:
            errs.append(f"{nm}: {PAT_BARS} bars of steps")
        for bar in PATTERN[nm]:
            if bar != sorted(set(bar)) or any(not 1 <= s <= STEPS_BAR for s in bar):
                errs.append(f"{nm}: grid steps must be distinct, rising and in 1-16: {bar}")
    if PAT_HITS != [14, 16, 17, 18] or PAT_TOTAL != 65 or [LANE_HITS[l] for l in LANES] != [14, 4, 8, 30, 5, 4] or sum(LANE_HITS.values()) != PAT_TOTAL or EVEN_HITS != 7:
        errs.append("pattern hits per bar 14, 16, 17, 18 = 65; per sound 14, 4, 8, 30, 5, 4 = 65; 7 hits on even steps")
    flat_even = [(l, b, s) for l in LANES for b in range(PAT_BARS) for s in PATTERN[l][b] if s % 2 == 0]
    if sorted({l for l, _, _ in flat_even}) != ["SCISSOR SNIP", "TUBE TAP"] or sum(1 for l, _, _ in flat_even if l == "SCISSOR SNIP") != 5 or sum(1 for l, _, _ in flat_even if l == "TUBE TAP") != 2:
        errs.append("even-step hits are 5 scissor snips and 2 tube taps")
    if any(s % 2 == 0 for bar in PATTERN["PAPER CRINKLE"] for s in bar):
        errs.append("the crinkles sit on odd steps")
    if any(set(PATTERN["BOX TAP"][b]) & set(PATTERN["TAPE PULL"][b]) for b in range(PAT_BARS)) or any(PATTERN["TAPE PULL"][b] != [5, 13] for b in range(PAT_BARS)) or \
       any({1, 7, 11} - set(PATTERN["BOX TAP"][b]) for b in range(PAT_BARS)):
        errs.append("box tap on steps 1, 7, 11 (and 15 in bars 2 and 4); tape pull on 5 and 13 (beats 2 and 4), never sharing a step")
    if (5 - 1) // 4 + 1 != 2 or (13 - 1) // 4 + 1 != 4:
        errs.append("grid steps 5 and 13 are beats 2 and 4")
    gp, gb = grid_body(1600, "g check")[0], grid_body(1600, "gb check", blank=True)[0]
    if svg_count(gp, "hit") != PAT_TOTAL or svg_count(gp, "cell") != NSND * PAT_BARS * STEPS_BAR or svg_count(gb, "hit") != 0 or svg_count(gb, "cell") != NSND * PAT_BARS * STEPS_BAR:
        errs.append(f"the step grid drawing must hold {PAT_TOTAL} hits and {NSND * PAT_BARS * STEPS_BAR} cells; the blank grid holds no hits")
    labels = [int(x) for x in re.findall(r">(\d+) hits<", gp)]
    if labels != PAT_HITS:
        errs.append(f"the drawn hits per bar {labels} do not match the data {PAT_HITS}")
    for ln, nm in enumerate(LANES):          # each lane's hit rectangles, counted again by row
        ys = [round(float(y)) for y in re.findall(r'class="hit" x="[\d.]+" y="([\d.]+)"', gp)]
        if len([y for y in ys if round(92 + ln * 40 + 5) == y]) != LANE_HITS[nm]:
            errs.append(f"lane {nm}: the drawing holds a different number of hits than the data ({LANE_HITS[nm]})")
    # ---- the arrangement
    for nm, spans in ARR_ROWS:
        last = 0
        for a, b in spans:
            if not (1 <= a <= b <= ARR_BARS) or a <= last:
                errs.append(f"layer {nm}: bars {a}-{b} outside 1-{ARR_BARS} or out of order")
            last = b
    if [(n_, a, b) for n_, a, b in ARR_SECTIONS] != [("INTRO", 1, 4), ("BUILD", 5, 8), ("GROOVE", 9, 12), ("OUTRO", 13, 16)]:
        errs.append("sections of the map")
    per_bar = [len(layers_in_bar(b)) for b in range(1, ARR_BARS + 1)]
    if per_bar != [2] * 4 + [3] * 4 + [6] * 4 + [2] * 4 or sum(per_bar) != 52 or [len(bars_of(r)) for r in ARR_LAYERS] != [16, 10, 10, 8, 4, 4] or sum(len(bars_of(r)) for r in ARR_LAYERS) != 52:
        errs.append("layers sounding per bar 2,2,2,2,3,3,3,3,6,6,6,6,2,2,2,2 = 52 layer-bars = 16 + 10 + 10 + 8 + 4 + 4")
    if len(ARR_LAYERS) != 6:
        errs.append("the arrangement has 6 layers")
    am = arr_body(1600, "a check")[0]
    if svg_count(am, "block") != sum(len(s) for _, s in ARR_ROWS) or svg_count(am, "cnt") != ARR_BARS or svg_count(am, "sec") != 4 or svg_count(am, "lane") != 6:
        errs.append(f"the arrangement drawing must hold {sum(len(s) for _, s in ARR_ROWS)} blocks, {ARR_BARS} layer counts, 4 section bars and 6 lanes")
    drawn = [int(x) for x in re.findall(r'class="cnt"[^>]*>(\d+)<', am)]
    if drawn != per_bar:
        errs.append(f"the drawn layer counts {drawn} do not match the data {per_bar}")
    if len(re.findall(r">(?:PAPER CRINKLE|BELLS|BOX TAP|TAPE PULL|TUBE TAP|SCISSOR SNIP)<", am)) != 6:
        errs.append("the arrangement drawing must name 6 layers")
    # ---- the role table, signal chain and swing drawings
    rb, cb, sb = roles_body(1600, "r check")[0], chain_body(1620, "c check")[0], swing_body(1500, "s check")[0]
    if svg_count(rb, "row") != NSND or svg_count(rb, "icon") != NSND or svg_count(rb, "chip") != NSND or svg_count(rb, "dot on") + svg_count(rb, "dot off") != NSND * 9 or \
       svg_count(rb, "dot on") != sum(s[3] + s[4] + s[5] for s in SOUNDS):
        errs.append("the role table drawing must hold 6 rows, 6 icons, 6 role chips and 54 dots, with as many filled dots as the levels add up to")
    for nm, _, role, p, b, ln, _, _ in SOUNDS:
        if f">{nm}<" not in rb or f">{role}<" not in rb or f">{PITCH_W[p]}<" not in rb or f">{BRIGHT_W[b]}<" not in rb or f">{LEN_W[ln]}<" not in rb:
            errs.append(f"the role table drawing must print {nm}, {role}, {PITCH_W[p]}, {BRIGHT_W[b]} and {LEN_W[ln]}")
    if svg_count(cb, "stage") != 5 or svg_count(cb, "arrow") != 4 or [x for x in re.findall(r">(OBJECT|MICROPHONE|INPUT|TRACK|HEADPHONES)<", cb)] != ["OBJECT", "MICROPHONE", "INPUT", "TRACK", "HEADPHONES"]:
        errs.append("the signal chain drawing must hold 5 stages (object, microphone, input, track, headphones) and 4 arrows")
    if svg_count(sb, "sw") != 8 or "late by 1/3 step = 0.05 s at 100 BPM" not in sb:
        errs.append("the swing drawing must hold 8 hits (4 straight, 4 swung) and say 'late by 1/3 step = 0.05 s at 100 BPM'")
    for k in ("box", "tube", "tape", "paper", "scissors", "bell", "mic", "interface", "track", "phones"):
        if len(icon(k, 0, 0)) < 80:
            errs.append(f"icon {k} is empty")
    # ---- Logic wording: newer tools are hedged
    for nm, txt in LOGIC_REF:
        if any(w in txt for w in ("Drum Machine Designer", "Quick Sampler", "Step Sequencer", "Channel EQ", "swing control", "humanize", "fade option", "velocity value", "key command")) and \
           "if your version" not in txt.lower() and "look for" not in txt.lower():
            errs.append(f"Logic reference '{nm}' must hedge a newer or version-specific tool with 'if your version'")
    joined = " ".join(t for _, t in LOGIC_REF)
    for w in ("Drum Machine Designer", "Quick Sampler", "Step Sequencer", "Piano Roll", "velocity", "swing", "humanize", "high-pass", "Mixer", "Bounce", "headroom", "transient", "4/4"):
        if w.lower() not in joined.lower():
            errs.append(f"the Logic quick reference must name {w}")
    # ---- the worked example
    if EX_BPM != 100:
        errs.append("the example is at 100 BPM")
    for need in ("4/4 at 100 BPM", "240 ÷ 100 = 2.4 seconds", "15 ÷ 100 = 0.15 seconds", "6 sounds", "14, 16, 17 and 18 hits, 65 in all", "4 × 2.4 = 9.6 seconds", "16 bars = 38.4 seconds",
                 "bars 1 to 4", "bars 5 to 8", "bars 9 to 12", "bars 13 to 16", "6 layers"):
        if need not in EX_STRONG:
            errs.append(f"the clear plan must say '{need}'")
    # ---- no forbidden themes in any text a buyer reads
    allt = " ".join([FOLEY_NOTE, THEME, BUILD_NOTE, INCLUSIVE_NOTE, " ".join(SAFETY), OVERVIEW, " ".join(GOALS), " ".join(f"{a} {b}" for a, b in VOCAB), " ".join(REQS), " ".join(STEPS), " ".join(TIPS), " ".join(CHECK),
                     " ".join(d for _, ds in RUBRIC for d in ds), TN_REINFORCES, " ".join(STRUGGLES), VAR_EASY, VAR_HARD, " ".join(f"{a} {b}" for a, b in RESOURCES), TN_NOTE,
                     " ".join(GRADING), " ".join(d["do"] for d in PACING), SONG_NOTE, VOICE_NOTE, " ".join(t for _, t in LOGIC_REF), EX_STRONG, EX_NOTE, " ".join(EX_QUESTIONS),
                     " ".join(f"{s[1]} {s[6]} {s[7]}" for s in SOUNDS), " ".join(" ".join((s[2], s[3], s[4])) for s in SLIDES)]).lower()
    for w in FORBIDDEN_WORDS:
        if re.search(rf"\b{re.escape(w.strip())}\b", allt):
            errs.append(f"no alcohol, religious, shopping or holiday wording in a secular kit: '{w.strip()}'")
    for w in ("colour", "favour", "centre", "licence", "grey", "metre ", "organis", "recognis", "practise", "analyse", "whilst", "milli-second", "equalis", "normalis", "behaviour", "sulph", "crotchet", "quaver", "sceptic", "tyre"):
        if w in allt:
            errs.append(f"US spelling: '{w}'")
    for w in ("qa ", "inspector", "verified by", "--check", "gen.py"):
        if w in allt.replace("verified before", ""):
            errs.append(f"internal wording in buyer-facing text: '{w}'")
    for w in ("wikipedia", "imslp", "wikimedia", "apple support", "commons"):
        if w in allt:
            errs.append(f"buyer-facing text must not name a source ({w})")
    for w in (" hz", "khz", "−12", "−6 dbfs", "-12"):
        if w in allt:
            errs.append(f"no frequency or level numbers in a kit that has no source for them: '{w}'")
    if "No glass, no knives, no blades" not in SAFETY[1] or "ordinary scissors on paper only" not in SAFETY[2].lower() or "adult" not in SAFETY[0] + SAFETY[2]:
        errs.append("safety list: permission, no glass, knives or blades, ordinary scissors on paper only with an adult")
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
    for need, key in ((f"page {pg('timing')}", 5), (f"page {pg('sounds')}", 6), (f"page {pg('logicref')}", 6), (f"page {pg('sounds')}", 7), (f"page {pg('roles')}", 8), (f"page {pg('roles')}", 9),
                      (f"page {pg('logicref')}", 9), (f"page {pg('pattern')}", 10), (f"page {pg('swing')}", 11), (f"page {pg('arrange')}", 12), (f"page {pg('mix')}", 13)):
        if need not in SLIDES[key][4]:
            errs.append(f"slide {key + 1} notes must name {need}")
    for i, s in enumerate(SLIDES, start=1):
        errs += step_ref_errors(" ".join((s[2], s[3], s[4])), f"slide {i}")
    if [s[0] for s in SLIDES] != [1] * 8 + [2] * 4 + [3] * 6 or SLIDES[3][1] != "days":
        errs.append("deck classes: slides 1-8 Class 1, 9-12 Class 2, 13-18 Class 3; slide 4 is the 'days' slide (it gets the Classes 1-3 badge)")
    if [d["slides"] for d in PACING] != [(1, 8), (9, 12), (13, 18)]:
        errs.append("pacing slide slots 1-8, 9-12, 13-18")
    # ---- the hero art, used whole: the viewBox is the 1400 px file; the art's own pixels keep at least 40 px (it is not cropped, redrawn or recolored)
    hp = os.path.join(HERE, "art", "hero.png")
    if not os.path.exists(hp):
        errs.append("art/hero.png is missing")
    else:
        x0, y0, x1, y1 = alpha_bbox(hp)
        if min(x0 - HX, y0 - HY, HX + HW - 1 - x1, HY + HH - 1 - y1) < 40 or (HX, HY, HW, HH) != (-24, -24, 1448, 1448):
            errs.append(f"hero art {x0, y0, x1, y1} is closer than 40 units to the viewBox {HX, HY, HX + HW, HY + HH}")
    if "--check" in sys.argv:
        errs += drawing_edge_errors() + footer_gap_errors()
    return errs


COUNT_WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "twelve": 12, "sixteen": 16}


def count_claim_errors(texts):
    """Every stated number of sounds, steps, hits, bars, roles, stages or layers equals the drawings and the data."""
    errs = []
    allowed_bars = {0, 1, 2, 3, 4, 5, 8, 12, 16, 32, 52}     # 0: a table cell next to the word 'bars' in the flattened page text
    allowed_steps = {2, 4, 16, 64}
    allowed_hits = {7, 14, 16, 17, 18, 65}
    for label, t in texts:
        for m in re.finditer(r"(?<![\d.–])\b(\d+) sounds\b", t):
            if int(m.group(1)) not in (NSND, 8):
                errs.append(f"{label}: '{m.group(0)}' but the model has {NSND} sounds (students record 6 to 8)")
        for m in re.finditer(r"(?<![\d.–])\b(\d+) bars\b", t):
            if int(m.group(1)) not in allowed_bars:
                errs.append(f"{label}: {t[max(0, m.start() - 30):m.end()]!r} is not a bar count from the plan")
        for m in re.finditer(r"\b(\d+)-bar\b", t):
            if int(m.group(1)) not in allowed_bars:
                errs.append(f"{label}: '{m.group(0)}' is not a bar count from the plan")
        for m in re.finditer(r"(?<![\d.–])\b(\d+) steps\b", t):
            if int(m.group(1)) not in allowed_steps:
                errs.append(f"{label}: '{m.group(0)}' is not a step count from the grid (4 per beat, 16 per bar, 64 in 4 bars)")
        for m in re.finditer(r"(?<![\d.–])\b(\d+) hits\b", t):
            if int(m.group(1)) not in allowed_hits:
                errs.append(f"{label}: '{m.group(0)}' is not a hit count from the model pattern (14, 16, 17, 18; 65 in all)")
        for m in re.finditer(r"\b(\d+) sections\b", t):
            if int(m.group(1)) != len(ARR_SECTIONS):
                errs.append(f"{label}: '{m.group(0)}' but the form has {len(ARR_SECTIONS)} sections")
        for m in re.finditer(r"\b(\d+) roles\b", t):
            if int(m.group(1)) != len(ROLES):
                errs.append(f"{label}: '{m.group(0)}' but there are {len(ROLES)} roles")
        for m in re.finditer(r"\b(\d+) stages\b", t):
            if int(m.group(1)) != 5:
                errs.append(f"{label}: '{m.group(0)}' but the signal chain has 5 stages")
        for m in re.finditer(r"\b(\d+) lanes\b", t):
            if int(m.group(1)) != NSND:
                errs.append(f"{label}: '{m.group(0)}' but the step grid has {NSND} lanes")
    return errs


C1_BANNED = r"\bswing\b|\bhumanize\b|\barrange(ment|d)?\b|\bmix\b|\bhigh-pass\b|\bstep grid\b|\broles?\b|\bpattern\b|\blayers?\b|\bvelocity\b|\bkick\b"
C2_BANNED = r"\barrange(ment|d)?\b|\bmix(ing)?\b|\bhigh-pass\b|\bEQ\b|\bbounce\b|\blayers?\b|\bintro\b|\bgroove\b|\boutro\b"


def class_step_errors():
    """A deck slide badged Class 2 does not name the arrangement, mix, high-pass or layers (the pacing table puts them in Class 3), and a Class 1 slide does not teach roles, patterns,
    swing or the arrangement. Title, bullet and 'days' slides may preview the whole project."""
    errs = []
    for i, s in enumerate(SLIDES, start=1):
        shown = " ".join((s[2], s[3] if s[1] != "pic" else ""))
        if s[0] == 2 and re.search(C2_BANNED, shown, re.I):
            errs.append(f"deck slide {i} is badged Class 2 but names arrangement, mix or layer content, which the pacing page assigns to Class 3")
        if s[0] == 1 and re.search(C1_BANNED, shown, re.I) and s[1] not in ("title", "bullets", "days", "listen"):
            errs.append(f"deck slide {i} is badged Class 1 but teaches Class 2 or 3 content")
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
    for need in ("No audio, recordings, lyrics or melodies", "invented plan on paper", "Foley", "Jack Foley", "production, after the picture has been shot", "found sound", "one-shot", "transient", "velocity", "swing", "humanize",
                 "high-pass", "headroom", "Step Sequencer", "Drum Machine Designer", "if your version", "any paper and boxes", "permission", "No glass", "adult", "16th-note", "15 ÷ BPM", "240 ÷ BPM",
                 "kick", "snare", "hat", "percussion", "role table", "step grid", "arrangement", "intro", "build", "groove", "outro", "0 dBFS", "start with a small move", "listening descriptions",
                 "Not every family wraps gifts",
                 "Created with the help of digital and AI tools. Notation and answer keys are verified before release."):
        if need.lower() not in txt.lower().replace("- ", "-").replace("postproduction", "post-production"):
            errs.append(f"PDF must say: '{need}'")
    if "What changed" in txt or "Kept as I wrote it" in txt or "my project menu" in txt or "my Digital Music Production" in txt:
        errs.append("ORIGINAL kit: no wording about changes to an owner's sheet")
    if "checked by hand" in txt or "handmade" in txt.lower() or "classroom-tested" in txt.lower() or "hand-checked" in txt.lower():
        errs.append("never claim hand checks or classroom testing for a new product")
    if GRADES_TEXT != "9–12" or "Grades 9–12" not in txt:
        errs.append("PDF: 'Grades 9–12'")
    for w in FORBIDDEN_WORDS:
        if re.search(rf"\b{re.escape(w.strip())}\b", (txt + " " + alldeck).lower()):
            errs.append(f"no alcohol, religious, shopping or holiday-specific wording in this product ({w.strip()})")
    for w in ("colour", "favour", "centre", "licence", "grey", "metre", "organis", "recognis", "practise", "analyse", "whilst", "milli-second", "colourful", "equalis", "crotchet"):
        if w in txt.lower().replace("greyscale", ""):
            errs.append(f"US spelling: '{w}' in the PDF")
    if re.search(r"\b(QA|inspector|gen\.py|--check)\b", txt + " " + alldeck):
        errs.append("internal QA wording in buyer-facing text")
    for w in (" Hz", "kHz", "−12", "−6 dBFS"):
        if w in txt or w in alldeck:
            errs.append(f"no frequency or level numbers without a source: '{w}'")
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
        row = f"{bpm} {dec(spb(bpm), 3)} {dec(step_len(bpm), 4)} {dec(bar_len(bpm), 3)} {dec(PAT_BARS * bar_len(bpm), 3)} {dec(ARR_BARS * bar_len(bpm), 3)}"
        if row not in rc:
            errs.append(f"timing page: row '{row}' is not printed")
    for t in LEN_TEMPOS:
        row = f"{t} " + " ".join(dec(nb * bar_len(t), 3) for nb in LEN_BARS)
        if row not in rc:
            errs.append(f"timing page: length row '{row}' is not printed")
    for need in ("Seconds per beat = 60 ÷ BPM", "Seconds per 16th-note step = 15 ÷ BPM", "Seconds per bar = 240 ÷ BPM (16 steps, 4 beats)", "15 ÷ 100 = 0.15 s per step", "240 ÷ 100 = 2.4 s per bar",
                 "Step 1: plan the beat", "5 rounds up", "0.1172", "3840 ÷ BPM", "38.4 seconds at 100 BPM", "38.4 × 100 ÷ 240 = 16 bars"):
        if need.lower() not in rc.lower():
            errs.append(f"timing page must say '{need}'")
    # ---- the sounds page
    rs = raw("sounds")
    for nm, _, _, p, b, ln, use, how in SOUNDS:
        if f"{nm} {use}" not in rs or f"{PITCH_W[p].lower()} {BRIGHT_W[b].lower()} {LEN_W[ln].lower()}" not in rs:
            errs.append(f"sounds page: the sound-source row for {nm} is not printed")
    for need in ("Step 2: collect the sounds", "Sound-source table", "Take log", "No wrapping paper?", "Safety and permission", "From object to track in 5 stages", "plenty of headroom", "not measurements",
                 "OBJECT", "MICROPHONE", "INPUT", "TRACK", "HEADPHONES", "6 to 8 sounds"):
        if need.lower() not in rs.lower():
            errs.append(f"sounds page must say '{need}'")
    # ---- the role table page
    rr = raw("roles")
    for nm, _, role, p, b, ln, _, _ in SOUNDS:
        if nm not in rr or role not in rr:
            errs.append(f"roles page: {nm} and {role} must be printed in the drawing")
    for r, job, ex in ROLES:
        if f"{r} {job} {ex}" not in rr:
            errs.append(f"roles page: role row '{r}' is not printed")
    for need in ("Step 3: trim and assign roles", "Trim checklist", "My role table", "6 sounds, 4 roles", "transient", "SOUND", "ROLE", "PITCH", "BRIGHTNESS", "LENGTH"):
        if need.lower() not in rr.lower():
            errs.append(f"roles page must say '{need}'")
    # ---- the pattern page
    rp = raw("pattern")
    for nm in LANES:
        row = f"{nm.title()} " + " ".join(str(len(PATTERN[nm][b])) for b in range(PAT_BARS)) + f" {LANE_HITS[nm]}"
        if row not in rp:
            errs.append(f"pattern page: hit row '{row}' is not printed")
    row = "All sounds " + " ".join(str(h) for h in PAT_HITS) + f" {PAT_TOTAL}"
    if row not in rp:
        errs.append(f"pattern page: total row '{row}' is not printed")
    for need in ("Step 4: build the pattern", "64", "14 hits", "16 hits", "17 hits", "18 hits", "65 hits in all", "(16 + 13) × 0.15 = 4.35 s", "grid steps 1, 7 and 11", "5 and 13", "beats 2 and 4",
                 "BAR 1", "BAR 4", "My pattern", "hits: ______"):
        if need.lower() not in rp.lower():
            errs.append(f"pattern page must say '{need}'")
    # ---- the swing page
    rw = raw("swing")
    for r in SWING_RATIOS:
        d = swing_delay_steps(r)
        nm = "straight" if r == 1 else f"{exact(r)}:1"
        row = f"{nm} {fs(Fraction(2) * r / (r + 1))} {fs(d)} {exact(d * step_len(EX_BPM))}"
        if row not in rw:
            errs.append(f"swing page: row '{row}' is not printed")
    for need in ("Step 5: swing and humanize", f"{EVEN_HITS} of the {PAT_TOTAL} hits are on even steps", "late by 1/3 step = 0.05 s at 100 BPM", "(r − 1) ÷ (r + 1)", "0.15 ÷ 3 = 0.05 s", "not a Logic setting",
                 "STRAIGHT", "SWUNG 2:1", "My comparison", "Humanized"):
        if need.lower() not in rw.lower():
            errs.append(f"swing page must say '{need}'")
    # ---- the arrangement and mix pages
    ra = raw("arrange")
    for nm, a, b in ARR_SECTIONS:
        layers = [r for r, spans in ARR_ROWS if any(x <= b and a <= y for x, y in spans)]
        row = f"{nm.title()} {a}–{b} {exact(hit_time(EX_BPM, a, 1))} {exact(hit_time(EX_BPM, b + 1, 1))} {', '.join(x.lower() for x in layers)}"
        if row not in ra:
            errs.append(f"arrangement page: section row '{row}' is not printed")
    for need in ("Step 6: layer, arrange and mix", "6 layers", "four sections of 4", "52 bars in all: 16 + 10 + 10 + 8 + 4 + 4", "16 bars × 2.4 s = 38.4 s", "INTRO · bars 1–4", "OUTRO · bars 13–16", "SECONDS", "LAYERS", "My arrangement"):
        if need.lower() not in ra.lower():
            errs.append(f"arrangement page must say '{need}'")
    rx = raw("mix")
    for need in ("Step 6: layer, arrange and mix, continued", "0 dBFS", "high-pass", "small move", "leave the box tap alone", "plenty of room to spare"):
        if need.lower() not in rx.lower():
            errs.append(f"mix page must say '{need}'")
    # ---- the worked example prints its numbers
    re1 = raw("example") + " " + raw("example2")
    for t in LEN_TEMPOS:
        row = f"{t} {dec(bar_len(t), 3)} {dec(PAT_BARS * bar_len(t), 3)} {dec(ARR_BARS * bar_len(t), 3)}"
        if row not in re1:
            errs.append(f"worked example: timing row '{row}' is not printed")
    for b in range(PAT_BARS):
        row = f"{b + 1} {PAT_HITS[b]} {exact(hit_time(EX_BPM, b + 1, 1))} {exact(hit_time(EX_BPM, b + 2, 1))}"
        if row not in re1:
            errs.append(f"worked example: bar row '{row}' is not printed")
    for nm, spans in ARR_ROWS:
        row = f"{nm.title()} {spans_text(spans)} {len(bars_of(nm))}"
        if row not in re1:
            errs.append(f"worked example: layer row '{row}' is not printed")
    for nm, _, role, p, b, ln, _, _ in SOUNDS:
        row = f"{nm.title()} {role.title()} {PITCH_W[p].lower()} {BRIGHT_W[b].lower()} {LEN_W[ln].lower()} {LANE_HITS[nm]}"
        if row not in re1:
            errs.append(f"worked example: sound row '{row}' is not printed")
    for need in ("15 ÷ 100 = 0.15 s", "240 ÷ 100 = 2.4", "65 in all", "14 + 4 + 8 + 30 + 5 + 4", "4 × 2.4 = 9.6 seconds", "(16 + 13) × 0.15 = 4.35 s", "16 bars × 2.4 s = 38.4 s", "the build at 9.6 s",
                 "0.05 s at 100 BPM", "7 hits on even steps", "52 bars in all"):
        if need.lower() not in re1.lower().replace("hits on even steps", "hits on even steps"):
            errs.append(f"worked example must say '{need}'")
    up = open(os.path.join(HERE, "UPLOAD.md"), encoding="utf8").read()
    errs += step_ref_errors(up, "UPLOAD.md")
    errs += count_claim_errors([("UPLOAD.md", up)])
    if "Grades 9-12" not in up or "`9th-grade`, `10th-grade`, `11th-grade`, `12th-grade`" not in up:
        errs.append("UPLOAD.md: grades 9-12 in the description and section 3")
    if "no audio" not in up.lower() or "Open questions" not in up or "Timing numbers" not in up or "Sources and credits" not in up:
        errs.append("UPLOAD.md: must say no audio is included, record the timing numbers checked, the sources and the open questions")
    for need in ("Foley (filmmaking)", "Jack Foley", "named after sound-effects artist Jack Foley", "Swing (jazz performance style)", "Sampling (music)", "one-shot", "High-pass filter", "Transient (acoustics)",
                 "DBFS", "Time signature", "Step Sequencer", "could not", "not from any source", "MIDI", "Quantization (music)"):
        if need not in up:
            errs.append(f"UPLOAD.md sources and credits must name: {need}")
    m = re.search(r"= 1 cover \+ (\d+) teacher \+ (\d+) student \+ 1 terms page", up)
    if not m or 2 + int(m.group(1)) + int(m.group(2)) != len(PLAN):
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
    for brand in ("Wikipedia", "Wikimedia", "Apple Support", "Jack Foley's"):
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
    return ("seconds per beat = 60 / BPM, per 16th-note step = 15 / BPM and per bar of 4/4 = 240 / BPM (4 beats, 16 steps) recomputed exactly (fractions) and by an independent float method at six tempos; "
            "4-bar and 16-bar lengths (960 and 3840 / BPM; 16 bars = 38.4 s at 100 BPM) and the length table for 4, 8, 16 and 32 bars at 80, 100 and 120 BPM; the swing arithmetic (a pair split r:1 delays "
            "the second step by (r - 1) / (r + 1) of a step: 0, 1/5, 1/3, 1/2 = 0, 0.03, 0.05, 0.075 s at 100 BPM); the 6 sounds and 4 roles; the 4-bar, 16-step pattern (hits per bar 14, 16, 17, 18 = 65, per sound 14, 4, 8, 30, 5, 4 = 65, "
            "7 hits on even steps) counted again in the step-grid drawing (hit rectangles, cells, per-bar labels, hits in each lane); the 16-bar arrangement (6 layers, 4 sections, bars per layer 16 + 10 + 10 + 8 + 4 + 4 = 52, "
            "layers per bar) counted again in the drawing; the role-table drawing (6 rows, icons, role chips, 54 dots), the signal chain (5 stages, 4 arrows) and the swing drawing (8 hits); every 'Step N' agrees with the project sheet "
            "on pages, slides, notes and UPLOAD.md; class badges agree with the pacing page, and the deck's 'three classes' slide carries Classes 1-3; Class 1 and 2 slides teach no later-class content; every stated sound, step, hit, "
            "bar, role, stage and layer count equals the drawing or the data; every drawing renders alone on a transparent ground with no ink at its edges; hero art used whole inside its viewBox; rendered-DOM footer gap on every page and deck "
            "slide, and clear space under text in dark boxes on pages and slides; no truncated slide bullets; edges of cover.png and previews clear; no audio, lyrics, existing recordings, alcohol, religious or holiday wording, "
            "frequency numbers or student work; safety wording (no glass, knives or blades); no source site named on a buyer page; grades 9-12; tags and subjects are not headings; no 'what changed' page (ORIGINAL).")


# ================================================================ UPLOAD.md (written by gen.py so every number matches the build)
def write_upload():
    np_, ns = len(PLAN), len(SLIDES)
    n_teacher = (PLAN.index("example2") + 1) - 1
    n_student = (PLAN.index("reflect") + 1) - (PLAN.index("timing") + 1) + 1
    assert 2 + n_teacher + n_student == np_, "page-count list must total the PDF"
    nt = len(LISTING_TITLE)
    desc = (f"{DESC_START} students record 6 to 8 found sounds of their own (wrapping paper, tape, a box, a tube, scissors on paper and a small bell, or any paper and boxes), trim each one, give it a drum role, "
            f"and build a beat from them in Logic Pro. Foley is the craft of recording everyday sound effects for film and video; here the sounds become a kick, a snare, a hat and percussion. "
            f"Students play a 4-bar, 16-step pattern (use the Step Sequencer or Drum Machine Designer, if your version has them), add swing and humanize, layer a 16-bar arrangement and mix it, "
            f"starting with small moves such as an EQ high-pass filter to clean up low rumble. Math runs through every step: one bar of 4/4 = 240 ÷ BPM seconds, one 16th-note step = 15 ÷ BPM seconds "
            f"(0.15 seconds at 100 BPM, so 16 bars last 38.4 seconds), and a swing of 2:1 delays every second step by 1/3 of a step (0.05 seconds at 100 BPM). "
            f"Safety comes first: only safe household objects, used with permission and an adult's help, no glass, knives or blades, and the volume kept low. "
            f"Not every family wraps gifts, so any paper and boxes work. This Gift Wrap Foley Beat takes {CLASSES} class periods (the pacing guide also shows two and four) and is an original Hudson Beat project; "
            f"the steps are written for Logic Pro, while the ideas (found sound, sampling, step patterns, swing, mixing) carry over to GarageBand and other music software.\n\n"
            f"WHAT'S INCLUDED (ZIP: {np_}-page PDF = 1 cover + {n_teacher} teacher + {n_student} student + 1 terms page, plus {ns}-slide intro deck as .pptx and PDF)\n"
            f"• Teacher pages: how to use, project overview, setup, a {CLASSES}-class pacing guide with the deck slides for each class, "
            f"two pages of teacher notes (struggles, variations, resources, grading), a Logic quick reference and a two-page worked example (an invented beat at 100 BPM: "
            f"6 sounds and their roles, a 4-bar pattern of 65 hits, swing, timing at three tempos and a 16-bar arrangement of 6 layers = 38.4 seconds) ({n_teacher} pages)\n"
            f"• Student pages: a timing page (seconds per beat, step and bar at six tempos, 4-bar and 16-bar lengths, and a length table at three tempos), a sounds page (a signal-chain drawing, a safety list, a sound-source table with "
            f"pitch, brightness and length descriptors, a headroom checklist and a take log), a role table with icons and a trim checklist, a 4-bar step grid with the hits per bar and a blank grid, a swing page with a table of delays, "
            f"an arrangement map with a blank table, a mix checklist with an EQ high-pass step, the 3-page project sheet (overview, goals, vocabulary, requirements, steps, tips, submission checklist), "
            f"the /{RUBRIC_TOTAL} rubric, a vocabulary page (foley, found sound, sample, transient, one-shot, velocity, swing, humanize), a feedback planner and a reflection page ({n_student} pages)\n"
            f"• Teacher-presented intro deck, {ns} slides with speaker notes on every slide: a think-and-share hook, what the project is, what Foley is, the timing math, the signal chain, safe collecting, roles, trimming, the step grid, "
            f"swing, the arrangement, the mix, what to turn in and the rubric\n\n"
            f"THE THREE CLASS PERIODS\n"
            f"• Class 1: hook; what Foley is; the timing math and a tempo; the signal chain, safety and recording the found sounds\n"
            f"• Class 2: trim the sounds and give each a role; build the 4-bar pattern; try swing and humanize\n"
            f"• Class 3: layer a 16-bar arrangement, mix (with a high-pass step), bounce, present and reflect\n\n"
            f"WHAT STUDENTS LEARN\n"
            f"• Timing math: seconds per bar in 4/4 = 240 ÷ BPM; seconds per step = 15 ÷ BPM; 16 bars = 3840 ÷ BPM seconds; the delay of a swung step\n"
            f"• Sound: recording at a safe level with plenty of headroom, trimming to the transient, roles (kick, snare, hat, percussion) and describing a sound as low, mid or high, dull or bright, short or long\n"
            f"• Beats: a 16-step grid, hits per bar, velocity, swing and humanize, layers and sections\n"
            f"• Mixing: small moves, an EQ high-pass filter to remove rumble, and leaving the kick alone\n\n"
            f"GOOD TO KNOW\n"
            f"• There is no audio in this resource and no student work. Students record their own found sounds; no existing recordings are used\n"
            f"• Requires Logic Pro on a Mac and a microphone; nobody has to read notation. Where a control may differ between versions, the pages say \"if your version has it\" and describe controls generically\n"
            f"• Rubric: 5 categories scored 1-5, /{RUBRIC_TOTAL}; the final grade is the average of the student's and the teacher's score\n"
            f"• Grades 9-12; music technology or music production classes\n"
            f"• The deck uses the free Oswald and Source Sans 3 fonts (built into Google Slides); install them for PowerPoint or Keynote, or present "
            f"the PDF copy, which shows the intended look\n"
            f"• Every student page prints well in black and white\n\n"
            f"Logic Pro is a product of Apple Inc., named only to describe compatibility. This resource is not affiliated with Apple.\n\n"
            f"Part of the Hudson Beat Logic Pro project series\n"
            f"Please leave a rating: you earn TpT credits for feedback, and it helps other teachers find this\n"
            f"Follow the Hudson Beat store for new music resources every week\n\n"
            f"{D.DISCLOSURE_NEW}")
    md = f"""# UPLOAD: Gift Wrap Foley Beat, original Logic Pro project (TpT 090)

These fields follow the order of TpT's "Add a resource" form. `tools/tpt.js publish` reads the title and description from the code blocks under 1 and 2, and everything else from `tpt.json`. This file is written by `gen.py`; edit the text there.

**Files to attach**
- Resource (digital download): `{SLUG}.zip`. It holds three files in a folder "{ZIP_DIR}":
  - `{SLUG}.pdf`: the teacher and student resource, {np_} pages, US Letter portrait.
  - `{SLUG}-intro-deck.pptx`: the teacher-presented intro deck, {ns} slides (16:9), speaker notes and a Class badge on every slide (the three-classes slide carries "Classes 1-3").
  - `{SLUG}-intro-deck.pdf`: a PDF copy of the deck, {ns} pages.
- Thumbnails, in this order: `cover.png`, `preview-1.png`, `preview-2.png`, `preview-3.png` (all 2000 × 2000).
- Preview file: `{SLUG}-PREVIEW.pdf`, 4 watermarked pages.

TpT takes one product file, so the PDF, the .pptx and the deck PDF go up together as the ZIP (`files.product` in tpt.json; `zip_contents` lists what is inside). **No audio, video, lyrics, recordings, presets, screenshots, student work or Logic sessions are in the ZIP.** Students record their own found sounds; the kit prints no melody and no words.

**Page count, adding up to the PDF:** 1 cover + {n_teacher} teacher + {n_student} student + 1 terms page = {np_} pages; plus {ns} slides = {np_ + ns} for TpT's "Number of pages or slides".

## 1. Title

```
{LISTING_TITLE}
```
({nt} characters; the limit is 80.) The title leaves out Winter, Holiday, Christmas and Gift because TpT's Seasonal Titles notice blocked a holiday-named title on 027 (see 080, 083 and 087 for the working format); "Found Sound Beat" and "Foley, Samples, Step Sequencer" are the plain search phrases. "Logic Pro" is in the first 30 characters as a compatibility word.

## 2. Description

```
{desc}
```

## 3. Grades

9th, 10th, 11th, 12th (`9th-grade`, `10th-grade`, `11th-grade`, `12th-grade` in tpt.json), as tpt/METADATA-GUIDE.md prescribes for every music-production item.

## 4. Subjects and tags

- Subjects in tpt.json: {"; ".join(SUBJECTS)} (all are in `tpt/SUBJECT-OPTIONS.json` and none is a heading)
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

**${PRICE}** (paid), multiple-license price ${PRICE}. The price the queue set, at the low end of the $8-12 holiday Logic kit range, for a kit with {np_} pages + {ns} slides, a timing page, a sounds and safety page, a role table with icons, a 4-bar step grid with a blank grid, a swing page, a 16-bar arrangement map, a mix checklist and a two-page worked example, listed for winter.

## 8. Free or paid / free preview pages

Paid. Preview PDF (4 watermarked pages): the {CLASSES}-class pacing guide, the role table, the step grid and the arrangement map. "Number of pages or slides" is {np_ + ns} ({np_} pages + {ns} slides).

## 9. Sources and credits

Fetched on 27 Nov 2026 (English Wikipedia and Apple's Logic Pro User Guide) unless a line says "could not". Each fact below says which source it came from; anything marked "not from any source" is an example value chosen for this kit.

- **What Foley is, and the name.** English Wikipedia, "Foley (filmmaking)": Foley is "the reproduction of everyday sound effects that are added to films, videos, and other media" to improve their audio; "Foley sounds are added to the film in post-production after the film has been shot"; the practice is "named after sound-effects artist Jack Foley". The kit says exactly this (sound effects recorded and added in post-production, named after sound-effects artist Jack Foley) and adds no history of Jack Foley.
- **Found sound, one-shot and sample.** English Wikipedia, "Sampling (music)": "sampling is the reuse of a portion (or sample) of a sound recording in another recording"; "sampling a short, isolated sound such as a drum hit or vocal snippet is known as one-shot sampling". The kit's definitions of sample and one-shot follow this. The term "found sound" is defined in the kit's own words (a sound made by an ordinary object that is recorded and used as music); **could not** source a dedicated page for it in this build.
- **Transient.** English Wikipedia, "Transient (acoustics)": "a high amplitude, short-duration sound at the beginning of a waveform". The kit defines a transient as the sudden, loud start of a sound.
- **High-pass filter and rumble.** English Wikipedia, "High-pass filter": "an electronic filter that passes signals with a frequency higher than a certain cutoff frequency"; "Rumble filters are high-pass filters applied to the removal of unwanted sounds" near or below the lower end of human hearing. The kit gives no cutoff frequency: it says only to start with a small move and stop when the sound feels thin, which is general mixing practice, not from any source.
- **Swing.** English Wikipedia, "Swing (jazz performance style)": swung notes involve "alternately lengthening and shortening the first and second consecutive notes in the two part pulse-divisions in a beat"; in traditional jazz this is usually applied to eighth notes, the first note of each pair is often about twice as long as the second, and the ratio can range from nearly even to about three to one. The kit applies the same long:short idea to pairs of 16th-note steps as an illustration: the delay (r - 1) / (r + 1) of a step for a long:short ratio of r:1 (1/5, 1/3 and 1/2 of a step for 3:2, 2:1 and 3:1; seconds at 100 BPM from 15 / BPM) is arithmetic computed in `gen.py --check`, labeled "an example, not a Logic setting". Logic's swing control and its scale: **could not** read (see Logic Pro below).
- **Humanize and quantization.** English Wikipedia, "Quantization (music)": quantization is "the studio-software process of transforming performed musical notes, which may be imprecise, to a strict rhythm". The page does not use the word "humanize", so the kit defines humanize in its own words (tiny changes in timing and velocity so a pattern sounds less like a machine) and hedges every control with "if your version has it".
- **Meter and the length of a bar.** English Wikipedia, "Time signature": the upper numeral "indicates how many such note values constitute a bar" and the lower numeral the note value being counted, so 4/4 is four quarter-note beats per bar. One beat = 60 / BPM s is the definition of beats per minute; the 16th-note step = 15 / BPM s (four steps to a beat), the bar = 240 / BPM s = 16 steps, and every table are arithmetic computed in `gen.py --check` exactly with fractions and with an independent float method. Six tempos: 80 BPM: 3.000 s per bar, 16 bars = 48.000 s; 90 BPM: 2.667 s, 42.667 s; 100 BPM: 2.400 s, 38.400 s; 110 BPM: 2.182 s, 34.909 s; 120 BPM: 2.000 s, 32.000 s; 128 BPM: 1.875 s, 30.000 s.
- **Level: 0 dBFS and headroom.** English Wikipedia, "DBFS": "The level of 0 dBFS is assigned to the maximum possible digital level", and all peaks below it are negative levels. The kit says "leave plenty of headroom" and "keep the meter well below the top" and prints no target peak level, because **no source for a target (such as -12 to -6 dBFS) was fetched**.
- **Velocity.** English Wikipedia, "MIDI": note-on messages carry "a velocity value that indicates how forcefully the note was played". The page text I read did not give the value range, so the kit says only that many programs use a scale up to 127 (the range comes from the Wikipedia "Dynamics (music)" table of default velocities read for kit 087, not re-read here) and that higher numbers play harder and usually louder.
- **Logic Pro.** Apple, Logic Pro User Guide, "Use Step Sequencer" section: the page's table of contents lists "Step Sequencer overview", "Create patterns" and "Use Step Sequencer with Drum Machine Designer" (the Step Sequencer works with Drum Machine Designer; **could not** read the overview text itself, only the contents list; the fetch returned the section's navigation). **Could not** read: the Quick Sampler page, the Drum Machine Designer overview page, the Channel EQ page, the Step Sequencer's swing controls, the region fade options and the Mixer page. The kit therefore names the tools, says "if your version has it", and invents no menu paths or key commands, except File › Bounce › Project or Section (Command-B), the Mixer key command (X) and "Compress in Finder", carried over from kits 083 and 087 (kit 087 notes the Bounce path and Command-B were confirmed on Apple Support search results; I did not re-fetch them).
- **Example values (not from any source).** The 100 BPM tempo, the six sounds and their roles, the pitch, brightness and length descriptors (qualitative: low, mid, high, dull, bright, short, long; listening guides, not measurements and with no frequency numbers), the pattern's steps and hits, the arrangement's layers and bars, the section names and every invented time are example values chosen for this kit and labeled as examples. The safety rules (ask permission, safe household objects, no glass, knives or blades, ordinary scissors on paper only with an adult's help, low volume) are general common-sense precautions written for this kit, not from any source; the teacher should adapt them to the school's own rules.
- **No recordings, no brands.** No recordings, artists or albums are named, and no tape or paper brand. The kit uses no film, game or pop-music reference.
- **Art:** the cover, previews and deck use the owner's pre-made art (`art/hero.png`: a roll of wrapping paper with snowflakes, a tape dispenser, a gift box with a bow, three jingle bells, a studio microphone, headphones and a pad controller, no text), copied whole and unchanged from `tpt/_art/next/gift-wrap-foley-beat/`; logged in `tpt/_art/USAGE.md`. Everything else, including every number, table, icon, step grid, role table, signal chain, swing drawing and arrangement map, is drawn or printed in code.
- **Fonts:** Oswald and Source Sans 3 (SIL OFL 1.1). Logic Pro is named only to describe compatibility.

## 10. Before you click publish

- [ ] **Needs QA approval first.** This is a new kit (not yet on TpT); the Manager releases it only after a QA `**Verdict: APPROVED**`. Season rule: listing no sooner than the 2-8 week window before winter allows.
- [ ] Cover and previews show "HUDSON BEAT" in type; PDF footers read "© 2026 Brian Lotze · Hudson Beat · For single-classroom use".
- [ ] No school name, logo, student names or work, audio, video, lyrics, recording name or Logic session anywhere (`gen.py --check` scans every output and every file in this folder).
- [ ] **Secular and inclusive.** The theme is winter-gift materials (paper, tape, boxes, bells) as sound sources: no religious content, no alcohol imagery, no brands other than Logic Pro, no shopping or gift-giving emphasis. The page says not every family wraps gifts and offers "any paper and boxes". `gen.py --check` fails on alcohol, religious, shopping and holiday words.
- [ ] **Safety wording.** Safe household objects only, with permission and an adult's help; no glass, knives or blades; ordinary scissors only on paper (with a pen click as the alternative); low volume. Please confirm this matches your school's rules.
- [ ] **Timing numbers (all recomputed in `gen.py --check`, exactly with fractions and again with an independent float method).** Seconds per beat = 60 / BPM; per 16th-note step = 15 / BPM; per bar of 4/4 = 240 / BPM = 4 beats = 16 steps; 4 bars = 960 / BPM; 16 bars = 3840 / BPM. Lengths of 4 / 8 / 16 / 32 bars = 12 / 24 / 48 / 96 s at 80 BPM, 9.6 / 19.2 / 38.4 / 76.8 s at 100 BPM and 8 / 16 / 32 / 64 s at 120 BPM. Rounding: seconds per beat, bar and section to 3 decimals, per step to 4, half up. Section starts at 100 BPM: 0, 9.6, 19.2, 28.8 s; the arrangement ends at 38.4 s. Swing: a pair split r:1 puts the second step at 2r / (r + 1) steps, late by (r - 1) / (r + 1): 0, 1/5, 1/3, 1/2 of a step = 0, 0.03, 0.05, 0.075 s at 100 BPM.
- [ ] **Pattern and arrangement numbers (recomputed from the data and from the drawings).** 6 sounds on 6 lanes; 4 bars of 16 steps = 64 steps; hits per bar 14, 16, 17, 18 = 65; hits per sound 14, 4, 8, 30, 5, 4 = 65; 7 hits on even steps (5 snips, 2 tube taps), 58 on odd steps; tape pull on grid steps 5 and 13 (beats 2 and 4) in every bar; bar 2 grid step 14 = (16 + 13) x 0.15 = 4.35 s. Arrangement: 16 bars, 4 sections of 4 bars, 6 layers; bars per layer 16, 10, 10, 8, 4, 4 = 52; layers sounding per bar 2 (bars 1-4), 3 (5-8), 6 (9-12), 2 (13-16) = 52. Role table drawing: 6 rows, 6 icons, 6 role chips, 54 dots; signal chain: 5 stages, 4 arrows; swing drawing: 4 straight and 4 swung circles.
- [ ] **Original project.** Built with `ORIGINAL = True` in `tpt/_dmp2_common/dmp2.py` (like 031, 036, 053, 057, 061, 063, 067, 070, 076, 080, 083 and 087): no "what changed" page and the new disclosure line. The reflection page is the shared Reflection element, scored in the rubric's "Plan & Reflection" row. `dmp2.py` is unchanged; the deck's three-classes badge and the terms-page thank-you note are applied inside `gen.py`.
- [ ] **Logic Pro names to confirm on a Mac with a current Logic.** Audio track input and record-enable, trimming a region, Drum Machine Designer (hedged), Quick Sampler (hedged), the Step Sequencer and its swing control (hedged), velocity per step (hedged), humanize or randomize (hedged), Channel EQ and its high-pass filter (hedged), the Mixer (X), Bounce (Command-B) and Compress in Finder.
- [ ] **Open questions for the owner:** (1) **Naming Jack Foley.** The name is in the vocabulary, the overview and slide 5, sourced from Wikipedia's "Foley (filmmaking)"; say if you want it removed. (2) **Safety.** Scissors on paper with an adult's help is the only edged item; say if you want it removed from the model sounds. (3) **Headroom.** No numeric target level is printed because none could be sourced. (4) **Title.** No Winter, Holiday, Christmas or Gift in the title because of TpT's seasonal-title notice (see 1). (5) **Price.** $8.00, as queued. (6) **Logic details.** Apple's pages for Quick Sampler, Drum Machine Designer, Channel EQ and swing could not be read, so the kit stays generic; say if you want a Mac check before release. (7) **Classes.** Three periods; Class 2 holds trimming, roles, the pattern and swing, so the pacing page shows how to use two or four.
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
