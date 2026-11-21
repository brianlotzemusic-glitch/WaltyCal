#!/usr/bin/env python3
"""Logic Pro project kit: New Year's Countdown (TpT 067): the teacher resource, the intro deck and the listing files.

    python3 gen.py            build everything into this folder (also writes UPLOAD.md)
    python3 gen.py --lowres   same, but square images at scale 1 and small page shots (self-check only; --check rejects it)
    python3 gen.py --check    verify content and layout: the timing arithmetic (seconds per beat = 60 / BPM, seconds per bar in 4/4 = 240 / BPM,
                              bars in 10 seconds = BPM / 24, a whole number only at BPM = 24 x bars), the tempo table (90, 96, 100, 110, 120, 128,
                              144 BPM), the section map (8 + 8 + C + 16 + 8 bars = 40 + C, 44 to 46 bars at 96, 120 and 144 BPM), every section
                              start in bars and seconds, the countdown cue sheet (the number said at second s sits at s x BPM / 60 beats; the drop is on
                              the first beat of the drop bar), the snare-roll ladder (1, 2, 4 and 8 hits per beat, 60000 / (BPM x hits) ms apart),
                              the filter-sweep and pitch-up numbers, Step N references on every page, slide and UPLOAD.md, class badges against the
                              pacing page, drawings (each rendered alone on a transparent ground: no ink within 4 px of its edge), the hero art, files,
                              page and slide counts, class slots, fonts, fit and overlap, dead space, footer gap, truncated slide bullets, the edges
                              of cover.png and the previews, banned strings, tpt.json and UPLOAD.md

An ORIGINAL Hudson Beat project (dmp2.ORIGINAL = True, like 053, 057, 061 and 063). Students arrange a 40 to 48 bar countdown track in Logic Pro: an
intro, a build-up (risers, a snare roll that speeds up from quarter notes to thirty-second notes, a filter sweep, a pitch-up), a 10-second countdown
(the numbers 10 to 1, one per second), the drop on the first beat after 1, and an outro. Ten seconds is a whole number of bars only when the tempo
is 24 x bars (96, 120 or 144 BPM give 4, 5 or 6 bars), so students choose one of those tempos. No audio ships; students make every sound. The art on the
cover, the previews and the deck is the owner's pre-made hero (art/hero.png: laptop, headphones, microphone, monitor, controller and a plain stopwatch
with no numbers), used whole. Everything else is drawn in code. The shared builder is ../_dmp2_common/dmp2.py.
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
SLUG = "new-years-countdown"
TITLE = "New Year’s Countdown"
ACCENT = "#2F7FB8"          # this product's single accent: icy blue (a shade deeper than the art's #4FA3D9, so small labels read)
ACC_LIGHT = "#DCEBF6"
PRICE = "8.00"
CLASSES = 3
GRADES_TEXT = "9–12"
GRADE_SLUGS = ["9th-grade", "10th-grade", "11th-grade", "12th-grade"]
TAGS = ["New Year", "Project-based Learning", "Projects", "Activities"]     # exact entries of tpt/TAG-OPTIONS.json, none a heading
SUBJECTS = ["Music", "Computer Science - Technology", "Music Composition"]     # all in SUBJECT-OPTIONS.json, none a heading
ANSWER_KEY = None
LISTING_TITLE = "Logic Pro Build-Up and Drop | Risers, Snare Rolls, Countdown | High School"
DESC_START = "Build-up and drop project for high school music technology:"
DESC_MUST = ["New Year’s Countdown", "10-second countdown", "seconds per bar", "tempo = 24 × bars", "120 BPM", "no audio", "Alchemy"]
ZIP_DIR = "New Years Countdown - Hudson Beat"
ZIP_DATE = (2026, 11, 21, 12, 0, 0)
TYPE = "Original Project"
PROJ_LINE = "Music Technology | <i>Build-Up and Drop Project</i> | 3 class periods"
DECK_STRAP = "Build-up and drop"
REFLECT_ROW = "Plan &amp; Reflection"
# split so this file never contains them (the --check scan reads every file in this folder)
BANNED_EXTRA = ["Rud" + "olph", "Fro" + "sty", "Gri" + "nch", "Santa Claus " + "Is", "Jingle Bell " + "Rock", "Feliz " + "Navidad",
                "Mari" + "ah Carey", "Spoti" + "fy", "You" + "Tube", "Home " + "Alone", "Nin" + "tendo", "Ro" + "land",
                "Star " + "Wars", "Hans " + "Zimmer", "John " + "Williams", "Harry " + "Potter", "Pix" + "ar", "Lord of the " + "Rings",
                "Winter " + "Wonderland", "Let It " + "Snow", "Sleigh " + "Ride", "X" + "mas", "Times " + "Square", "Auld " + "Lang",
                "cham" + "pagne", "bub" + "bly", "Isaac " + "Nathan", "Marcus " + "Hast"]

# ================================================================ page plan (teacher pages 2-10, student pages 11-22)
PLAN = ["cover", "howto", "overview", "setup", "pacing", "tn1", "tn2", "logicref", "example", "example2", "tempo", "map", "ladder", "cues", "mix",
        "proj1", "proj2", "proj3", "rubric", "vocab", "present", "reflect", "terms"]


def pg(k):
    return PLAN.index(k) + 1


# ================================================================ the arithmetic (exact fractions; all verified in --check)
SEC_NAMES = ["Intro", "Build-up", "Countdown", "Drop", "Outro"]
FIXED_BARS = {"Intro": 8, "Build-up": 8, "Drop": 16, "Outro": 8}      # the countdown has C bars, the rest are fixed
CHOICES = (96, 120, 144)                    # the tempos a student may choose: 10 seconds is 4, 5 or 6 whole bars
TEMPOS = (90, 96, 100, 110, 120, 128, 144)  # the tempo table's rows (whole and not whole)
EX_BPM = 120                                # the worked example's tempo: 5 countdown bars, 45 bars, 90 seconds
CD_SECONDS = 10


def spb(bpm):
    """Seconds per beat = 60 / BPM."""
    return Fraction(60, bpm)


def bar_len(bpm):
    """Seconds per bar of 4/4 = 240 / BPM (four beats)."""
    return Fraction(240, bpm)


def cd_bars(bpm):
    """Bars in the 10-second countdown = 10 / (240 / BPM) = BPM / 24 (a whole number only when BPM = 24 x bars)."""
    return Fraction(CD_SECONDS) / bar_len(bpm)


def is_whole(bpm):
    return cd_bars(bpm).denominator == 1


def sec_bars(bpm):
    """Bars in each of the five sections: 8, 8, C, 16, 8."""
    c = int(cd_bars(bpm))
    return [FIXED_BARS["Intro"], FIXED_BARS["Build-up"], c, FIXED_BARS["Drop"], FIXED_BARS["Outro"]]


def total_bars(bpm):
    return sum(sec_bars(bpm))


def passed(bpm, i):
    """Bars that have gone by before section i (0-based) starts."""
    return sum(sec_bars(bpm)[:i])


def start_bar(bpm, i):
    return passed(bpm, i) + 1


def start_s(bpm, i):
    """Seconds from the start of the track to the beginning of section i: bars gone by x 240 / BPM."""
    return passed(bpm, i) * bar_len(bpm)


def total_s(bpm):
    return total_bars(bpm) * bar_len(bpm)


CD_START_BAR = 17                           # the countdown always starts at bar 17: 8 + 8 bars come first


def cue_beats(bpm, s):
    """Beats from the start of the countdown to second s: s x BPM / 60."""
    return Fraction(s * bpm, 60)


def cue_pos(bpm, s):
    """(bar, beat) of second s of the countdown in the whole track: bar 17 + whole bars gone by, beat 1 + the leftover beats."""
    b = cue_beats(bpm, s)
    return CD_START_BAR + int(b // 4), 1 + (b - 4 * (b // 4))


def number_at(s):
    """The number said at second s (0 to 9): 10 at second 0 down to 1 at second 9. Second 10 is the drop."""
    return CD_SECONDS - s


# the snare-roll ladder: hits per beat for quarter, eighth, sixteenth and thirty-second notes, two bars of each across the 8 build-up bars
LADDER = [("1/4", "quarter notes", 1), ("1/8", "eighth notes", 2), ("1/16", "sixteenth notes", 4), ("1/32", "thirty-second notes", 8)]
LADDER_BARS = 2                             # bars spent on each rung


def gap_ms(bpm, hits):
    """Milliseconds between snare hits when there are `hits` in every beat: 60000 / (BPM x hits)."""
    return Fraction(60000, bpm * hits)


def ladder_bars(i):
    """First and last bar of rung i (0-based) of the ladder: the build-up starts at bar 9."""
    a = 9 + LADDER_BARS * i
    return a, a + LADDER_BARS - 1


# the example filter sweep and pitch-up over the build-up (bar numbers) at the example tempo: values are an example, not a rule
EX_SWEEP = [(9, 200), (11, 500), (13, 1500), (15, 5000), (17, 12000)]      # bar, low-pass cutoff in Hz
EX_PITCH_ST = 12                                                            # the riser rises one octave: 12 semitones, which doubles the frequency


def rnd(x, nd):
    """Round half up (a 5 rounds up) to nd decimals, on exact fractions."""
    s = Fraction(10) ** nd
    return Fraction(math.floor(Fraction(x) * s + Fraction(1, 2)), 1) / s


def dec(x, nd):
    return f"{float(rnd(x, nd)):.{nd}f}"


def num(x, nd=2):
    """A number rounded half up to nd decimals with no trailing zeros: 625, 312.5, 78.13."""
    return f"{float(rnd(x, nd)):g}"


def fmt(x):
    x = float(x)
    x = round(x + 1e-9, 3)
    return f"{x:.0f}" if x == int(x) else f"{x:g}"


def bb(bar, beat):
    """A position as printed in tables: 'bar beat'."""
    return f"{bar} {fmt(beat)}"


# ================================================================ the section map: which elements play in which section
# element -> five cells (Intro, Build-up, Countdown, Drop, Outro); "" = not playing, text = what it does there
ELEMENTS = [
    ("Pad or chords", ["soft", "soft", "soft", "full", "fades"]),
    ("Kick", ["soft", "steady", "", "full", "soft"]),
    ("Bass", ["", "", "", "full", "soft"]),
    ("Hi-hat or shaker", ["steady", "busier", "", "full", "steady"]),
    ("Riser", ["", "rises", "peaks", "", ""]),
    ("Snare roll", ["", "1/4 to 1/32", "", "", ""]),
    ("Filter sweep", ["", "opens", "open", "open", ""]),
    ("Countdown voice", ["", "", "10 to 1", "", ""]),
    ("Lead synth", ["", "", "", "melody", ""]),
    ("Impact and crash", ["", "", "", "on beat 1", ""]),
]
ELEM_PLAYING = [sum(1 for _, cells in ELEMENTS if cells[i]) for i in range(5)]      # 3, 6, 4, 7, 4


# ================================================================ the project text (original; students read these pages)
THEME = ("Many communities around the world count down the last seconds of the old year together and cheer when the new one begins. This project borrows only "
         "that idea: a count to a big moment. It is a music-technology project that suits any class. Students may choose a different countdown, such as a launch, "
         "a game start or the final seconds of a race.")
BUILD_NOTE = ("The build-up and drop is a structure found in many styles of electronic music: the energy climbs for a while, a short count or a moment of "
              "near-silence leads in, and then everything arrives at once.")
OVERVIEW = ("Arrange a countdown track in Logic Pro: 40 to 48 bars in five sections. An intro sets the mood. A build-up raises the tension with a riser, a snare roll that "
            "speeds up from quarter notes to eighth, sixteenth and thirty-second notes, a filter sweep that opens a low-pass filter, and a pitch that climbs. Then comes a "
            "10-second countdown, the numbers 10 to 1 with one number on each second, and the drop lands on the first beat after 1. A drop section and an outro finish the track. "
            "Ten seconds is a whole number of bars only at some tempos: tempo = 24 × bars, so 96, 120 and 144 BPM give 4, 5 and 6 bars. Nobody needs to read music.")
GOALS = ["Arrange a 40 to 48 bar track in five sections: intro, build-up, a 10-second countdown, drop and outro",
         "Use one bar = 240 ÷ BPM seconds and tempo = 24 × bars to choose a tempo at which 10 seconds is a whole number of bars, and to place every section",
         "Build tension in Logic Pro with a riser, a snare roll that speeds up through four note values, a filter sweep and a pitch-up, all shaped with automation",
         "Place the numbers 10 to 1 one second apart and land the drop on the first beat after 1, then mix, bounce and reflect on the choices"]
VOCAB = [("Riser", "A sound that climbs in pitch, brightness or volume to build tension, such as a rising synth or noise sweep"),
         ("Snare roll", "A fast run of snare hits that gets quicker in steps, from quarter notes (1 hit per beat) to eighths (2), sixteenths (4) and thirty-seconds (8)"),
         ("Filter sweep", "Moving the cutoff of a low-pass filter from low to high so that a muffled sound slowly opens up and brightens"),
         ("Automation", "Drawing a change over time in Logic, such as a filter cutoff, a pitch or a volume, so a control moves by itself"),
         ("Drop", "The moment after a build-up when the full beat and bass arrive together; here it lands on the first beat after the number 1")]
REQS = ["Choose 96, 120 or 144 BPM in 4/4 and show why with the tempo table (page @TEMPO)",
        "Make a track of 40 to 48 bars with five sections and a marker at the start of each (pages @MAP and @LOGICREF)",
        "Build a snare roll that speeds up through 1/4, 1/8, 1/16 and 1/32 notes, and a filter sweep and a pitch-up on the riser (page @LADDER)",
        "Say or play the numbers 10 to 1, one on each second of the countdown, at the bars and beats on your cue sheet (page @CUES)",
        "Land the drop, with an impact, on the first beat after the number 1",
        "Mix with level, filter and automation so the build-up grows, the countdown is clear and the drop feels biggest (page @MIX), then bounce",
        "Reflect on your choices (page @REFLECT)"]
FILE_NAME = "“Your Name – Countdown”"
STEP_NAMES = ["Choose tempo and map", "Plan the build", "Set up Logic", "Build intro and build-up", "Countdown and drop", "Mix and bounce", "Present &amp; get feedback"]
STEPS = ["<b>Choose tempo and map</b> — Use the tempo table (page @TEMPO) to pick 96, 120 or 144 BPM, work out how long each section lasts, and fill in the section map (page @MAP)",
         "<b>Plan the build</b> — Read the snare-roll ladder, the riser checklist and the automation checklist (page @LADDER) and choose a sound for each element on the map",
         "<b>Set up Logic</b> — Open a project at your tempo in 4/4 and put a marker at the start of each of the five sections (Logic quick reference: page @LOGICREF)",
         "<b>Build intro and build-up</b> — Make the intro, then build the riser, the snare roll that speeds up through four note values, the filter sweep and the pitch-up across bars 9 to 16",
         "<b>Countdown and drop</b> — Use your cue sheet (page @CUES) to place the numbers 10 to 1 one second apart, then land the drop and its impact on the first beat after 1; add the outro",
         "<b>Mix and bounce</b> — Set levels, filter automation and pan with the mix checklist (page @MIX), then bounce your whole track and name the file as on the checklist",
         "<b>Present &amp; get feedback</b> — Write three questions you want classmates to answer about your track. Play it, point out each part of the build as it arrives, "
         "and answer at least 2 of each classmate’s questions. Then reflect (page @REFLECT)."]
TIPS = ["Get the intro and the drop sounding good before you build the tension. The build-up needs something to lead to.",
        "Make the drop feel bigger by taking things away in the countdown: fewer sounds there make the drop seem louder.",
        "Check your countdown against the clock on your cue sheet: the numbers should be exactly one second apart, not just roughly even.",
        "Save a new version of your project at the end of each class, so you can always go back."]
CHECK = ["Bounced .mp3 or .wav of your whole track, 40 to 48 bars long",
         "Zipped .logicx project file handed in",
         f"Files named correctly: {FILE_NAME}",
         "Tempo table work, section map and cue sheet handed in",
         "Rubric self-score done (page @RUBRIC)",
         "I can say when the countdown starts and where the drop lands, in bars and in seconds"]
RUBRIC_NOTE = "Each category is scored 1–5. Score yourself first; the final grade is the average of your score and your teacher’s."
LEVELS = [1, 2, 3, 4, 5]
RUBRIC = [
    ("Build-Up & Tension", ["No build-up", "One tension tool, such as a riser, and little change over time",
                            "A riser and a snare roll, but the roll does not speed up through the note values",
                            "A riser, a snare roll through 1/4, 1/8, 1/16 and 1/32, a filter sweep and a pitch-up that all build toward the countdown",
                            "All tension tools are shaped with automation and arrive together; the build-up feels inevitable"]),
    ("Countdown & Drop", ["No countdown", "Some numbers are missing, or they are not one second apart",
                          "All ten numbers, but several are early or late, or the drop misses the beat",
                          "The numbers 10 to 1 sit one second apart at the cue sheet’s bars and beats, and the drop lands on the first beat after 1",
                          "Exact timing and a clear voice; the drop hits with an impact and is the biggest moment of the track"]),
    ("Tempo & Timing Math", ["No tempo and no arithmetic", "A tempo is chosen, but the bar length or section lengths are missing or wrong",
                            "Seconds per bar and the total length shown, with small errors",
                            "A tempo chosen on purpose (24 × bars); seconds per bar, section starts and the cue sheet are all correct",
                            "Correct math, a comparison of two tempos and a clear reason for the choice"]),
    ("Sound & Mix", ["Sounds are too loud or too quiet to tell apart", "A few parts can be heard; others are buried or clip",
                     "Most parts can be heard; some balance problems", "Every part can be heard; levels and filter automation are used; no clipping",
                     "The countdown voice is clear, the low end is tight and the drop is the loudest, widest part"]),
    ("Plan & Reflection", ["Plans, presentation or reflection missing", "Thin plan; little to say about choices",
                           "Plan and reflection complete, with basic detail", "Clear plan; thoughtful reflection and good answers to questions",
                           "Insightful reflection and a polished, confident presentation"]),
]
RUBRIC_TOTAL = 25
RUBRIC_SHORT = ["All tension tools are shaped with automation and arrive together",
                "Exact timing and a clear voice; the drop hits with an impact",
                "Correct math, two tempos compared and a clear reason",
                "Clear voice, tight low end, the drop is the biggest part",
                "Insightful reflection and a polished, confident presentation"]
RUBRIC_SLIDE_LINE = "Scored 1–5 · final grade = average of your score and mine, out of 25"
RUBRIC_ROW_PITCH = 0.86
RUBRIC_LINE_Y = 6.3

TN_REINFORCES = ("Teaches how a build-up and drop is made. Students learn what risers, snare rolls, filter sweeps and pitch-ups do to tension, how to turn a tempo into bars and "
                 "seconds with simple arithmetic, why 10 seconds is a whole number of bars only at some tempos, and how to place ten spoken cues on exact beats, all in Logic Pro.")
STRUGGLES = ["The drop does not feel big: take things away in the countdown (kick, bass and hi-hat stop) and bring everything back on the drop bar (page @MIX).",
             "The arithmetic looks hard: work one cue aloud with the formula beats = second × BPM ÷ 60, then bar = 17 + whole bars and beat = 1 + the leftover (page @CUES).",
             "The numbers drift: check that the first number starts exactly on bar 17 beat 1, and that the drop is on the first beat of bar 17 plus the countdown bars (page @TEMPO).",
             "The snare roll does not feel faster: make each rung of the ladder two full bars, and raise the velocity a little on every rung (page @LADDER)."]
VAR_EASY = ("Keep the tempo at 120 BPM, where 10 seconds is exactly 5 bars and every number lands on a beat (page " + str(pg("cues")) + "); skip the pitch-up, and use "
            "only the 1/4, 1/8 and 1/16 rungs of the snare ladder.")
VAR_HARD = ("Build two versions at two tempos, such as 96 and 144 BPM, and compare where the drop lands (page " + str(pg("tempo")) + "). Or add a false drop: "
            "a second countdown of 3, 2, 1 inside the drop section that ends in silence before the full drop.")
RESOURCES = [("Tempo table (page @TEMPO)",
              "Seconds per beat and per bar and the bars in 10 seconds at seven tempos, then the section starts in bars and seconds at 96, 120 and 144 BPM; every number is computed."),
             ("Section map and snare-roll ladder (pages @MAP and @LADDER)",
              "A map of which elements play in which section, a table of hits per beat and milliseconds between hits, and checklists for risers and automation."),
             ("Countdown cue sheet (page @CUES)",
              "The bar and beat of each number from 10 to 1 and of the drop, at 96, 120 and 144 BPM, a formula and a blank sheet for the student’s own tempo."),
             ("Worked example (pages @EXAMPLE–@EXAMPLE2)",
              "An invented plan at 120 BPM: a 45-bar track that lasts 90 seconds, a countdown of 5 bars starting at bar 17, and the drop at bar 22 (42 seconds). A model, not a template.")]
TN_NOTE = ("A good listening day: play each student’s track and ask the class to call out the moment the tension is highest, and then to count aloud with the numbers. "
           "If the drop lands a little before or after the room says it should, check the cue sheet together. This kit names no songs or artists.")
GRADING = ["The rubric: five categories, each scored 1–5, /25 (page @RUBRIC). Students score themselves first; the final grade is the "
           "average of their score and yours.",
           "Build-Up & Tension (rubric row 1): listen for the roll speeding up, the riser climbing and the filter opening; open the automation lanes (page @LADDER).",
           "Countdown & Drop (rubric row 2): play bars 17 onward and count the numbers against the cue sheet; the drop must be on the first beat after 1 (page @CUES).",
           "Tempo & Timing Math (rubric row 3): recompute one section start with the student: bars gone by × (240 ÷ BPM) (page @TEMPO).",
           "Sound & Mix (rubric row 4): listen for the voice over the riser, check the meter for clipping and compare the loudness of the countdown and the drop (page @MIX).",
           "Plan & Reflection (rubric row 5): the section map, the cue sheet, the feedback questions and the Reflection page (page @REFLECT) are the evidence."]
PACING = [
    {"n": 1, "owner": "Hear the idea, do the timing math and plan the track.",
     "do": "Slides 1–6: the think-and-share, what the project is, the three classes, the section map, the timing math and the tension tools. Hand out the tempo table, the section map, "
           "the snare-roll ladder and the cue sheet. Before they leave, students have a tempo, a filled-in section map and a plan for each tension tool.",
     "slides": (1, 6), "pages": ["tempo", "map", "ladder", "cues", "proj1", "proj2", "proj3", "vocab"],
     "deck": "Hear the build · the section map · tempo = 24 × bars"},
    {"n": 2, "owner": "Set up Logic and build the intro and the build-up.",
     "do": "Slides 7–9: the snare-roll ladder, the filter sweep and pitch-up, and building in Logic. Work one cue aloud with the formula. Students set up Logic with a marker at "
           "every section, then build the intro and the build-up. Walk the room with one question: what is rising right now?",
     "slides": (7, 9), "pages": ["ladder", "cues", "present"], "deck": "Snare ladder · filter sweep · build it in Logic"},
    {"n": 3, "owner": "Place the countdown, land the drop, mix, present and reflect.",
     "do": "Slides 10–14: the countdown timeline, what to turn in, the rubric and presentation day. Students place the ten numbers with the cue sheet, land the drop and add the outro, "
           "then mix with the checklist, bounce and present.",
     "slides": (10, 14), "pages": ["cues", "mix", "rubric", "present", "reflect"], "deck": "The 10-second countdown · checklist · rubric · presentations"},
]
PACING_EXTRA = (
    '<div class="cols" style="margin-top:4pt;gap:14pt"><div class="box acc-b"><span class="k">The one thing to do on Class 1</span>'
    '<p style="margin:0;font-size:10.6pt">Make sure every student leaves with 96, 120 or 144 BPM and a section map with the right bar numbers, so that Class 2 '
    'is all building. Check each tempo against the tempo table before they go.</p></div>'
    '<div class="box"><span class="k">With two or four periods</span><p style="margin:0;font-size:10.6pt"><b>Two classes:</b> Class 1 is the plan, the set-up and the intro; '
    'Class 2 is the build-up, the countdown, the drop, the mix and short presentations. <b>Four classes:</b> keep Classes 1 and 2, then spend Class 3 on the countdown, the drop and the outro, and '
    'Class 4 on the mix, presentations and reflection.</p></div></div>')
PACING_SIZE = 10.6
TN2_SIZE = 10.3

SONG_NOTE = ("No audio, recordings, lyrics or melodies are included, and no songs, artists or albums are named. Students make every "
             "sound themselves, from the instruments, samples and loops in Logic and from their own voices or synth beeps.")
VOICE_NOTE = ("The countdown can be students’ own voices, a classmate’s voice with permission, or beeps and tones made with a synth, so no one has to record themselves. "
              "Use only sounds students made or have the right to use.")
CREDITS = ["The tempo table, the section map, the snare-roll ladder, the cue sheet, the checklists and the worked example: original work, Hudson Beat. "
           "No melodies, lyrics, recordings or published editions are included.",
           "The cover illustration was made with digital and AI tools. No audio, video, album art, screenshots, presets, templates, links or "
           "chart data from other sources are included. No student work is included. All timing facts are arithmetic shown in the product."]
LOGIC_INTRO = ("Where to find the tools a New Year’s Countdown track is likely to use. Demonstrate what your class needs on Classes 1 and 2 and then "
               "let students work. Names are from current Logic Pro versions; labels move between versions, so check yours.")
LOGIC_REF = [("Project and tempo", "File › New…, then a Software Instrument track to start. Set the project tempo in the control bar to 96, 120 or 144 BPM and keep the time signature at "
              "4/4. The timing arithmetic only works at that tempo, so set it first. Set a cycle from bar 1 to the bar after your last outro bar to hear the whole track."),
             ("Sections with markers", "Show the Marker global track (the Global Tracks controls or the View menu). Add a marker with the plus (+) button in that track, "
              "or with a Create Marker key command if your version has one, then drag or type it to the bars on your section map. Name them Intro, Build-up, Countdown, Drop and Outro."),
             ("Risers and reverse effects", "Make a riser in Alchemy or Retro Synth, for example a noise or saw sound that rises, or record a cymbal or crash into an audio track or Quick Sampler and "
              "play it backward. Look for a Reverse option in the audio region inspector or in Quick Sampler or Sample Alchemy, if your version has it. Place the riser so it ends on the drop."),
             ("Snare roll", "Use a snare on a Drum Machine Designer pad or in Quick Sampler. In the Piano Roll, set the grid division to 1/4, then 1/8, 1/16 and 1/32 as the roll speeds up, and click the hits "
              "in, or draw them with the Step Sequencer if your version has it. Raise the velocity a little on each rung so the roll swells."),
             ("Filter sweep", "Open the filter of Alchemy or Retro Synth and automate its cutoff, or put a Channel EQ (its high cut) or an Auto Filter, if your version has it, on the riser or the whole "
              "mix. Press A to show automation, choose the cutoff or the filter frequency, and click points to draw it rising across the build-up."),
             ("Pitch-up and tension", "Automate the pitch or tuning control of the riser instrument, if it has one, so it climbs across the build-up. Twelve semitones is one octave. "
              "Also automate volume, so the riser swells, and add reverb that grows toward the countdown if you like."),
             ("Countdown voice", "Record each number into an audio track with a microphone, or make beeps with a synth. Place each one at the bar and beat on your cue sheet. Drag the region with the snap set to a fine "
              "value, or nudge it, and read its position, then play it against the clock. Leave a short rest after the number 1 so the drop hits."),
             ("Drop, impact and outro", "At the first beat after 1, bring in the kick, bass, lead and an impact or crash, and stop the riser. Fill the drop with the loop you built in the intro, only bigger. "
              "In the outro, take layers away and let the filter close if you like."),
             ("Mixer, automation and bounce", "Press X for the Mixer and set levels and pan. Keep the countdown voice above the riser, and keep the master out of the red. "
              "Then File › Bounce › Project or Section (Command-B), MP3 or WAV, for the whole track. In Finder, Control-click the .logicx and choose Compress.")]
PRESENT_CHECK = [f"Files named {FILE_NAME}; the .mp3 or .wav and the zipped .logicx handed in",
                 "Reflection page done (page @REFLECT)", "Three questions for classmates written",
                 "Rubric self-score done (page @RUBRIC)"]
VOCAB_PROMPT = "Where it shows up in my track:"
TN1_EXTRA = (
    '<div class="box acc-b" style="margin-top:4pt"><span class="k">Where this kit helps with each struggle</span><ul style="margin:0">'
    '<li style="font-size:12pt;margin-bottom:3pt">A drop that does not hit: the section map (page @MAP) shows what leaves in the countdown, and the mix checklist (page @MIX) covers the drop.</li>'
    '<li style="font-size:12pt;margin-bottom:3pt">The arithmetic: the tempo table (page @TEMPO) gives every section start at three tempos, and the worked example (pages @EXAMPLE–@EXAMPLE2) shows each step.</li>'
    '<li style="font-size:12pt;margin-bottom:3pt">Numbers that drift: the cue sheet (page @CUES) lists the bar and beat of every number at three tempos.</li>'
    '<li style="font-size:12pt;margin-bottom:0">A roll that does not speed up: the ladder (page @LADDER) lists hits per beat and the gap in milliseconds for each rung.</li></ul></div>')
TN1_SIZE = 12.0
PROJ_SIZE = 11.4
VOCAB_GAP = 8
LOGIC_SIZE = 9.0
PROJ1_EXTRA = ""
RUBRIC_EXTRA = ""

# ================================================================ the worked example: an invented track at 120 BPM
EX_KEY = "D minor"
EX_BAR_S = bar_len(EX_BPM)                  # 2 s
EX_C = int(cd_bars(EX_BPM))                 # 5 countdown bars
EX_WEAK = "I will make a build-up and then a drop, and it will be exciting."
EX_STRONG = ("My track is in D minor at 120 BPM in 4/4. One bar lasts 240 ÷ 120 = 2 seconds, so the 10-second countdown is exactly 5 bars. The track has 8 + 8 + 5 + 16 + 8 = 45 bars "
             "and lasts 90 seconds. The intro is bars 1 to 8, the build-up is bars 9 to 16, the countdown is bars 17 to 21 and the drop starts at bar 22, which is 42 seconds in. "
             "The snare roll speeds up from quarter notes to eighths, sixteenths and thirty-seconds, two bars each. The filter opens from 200 Hz to 12,000 Hz across the build-up. "
             "The number 10 is on bar 17 beat 1, and the drop is on bar 22 beat 1.")
EX_QUESTIONS = ["Where did you feel the tension was highest, and what caused it?",
                "Was the drop big enough? What would make it bigger?",
                "Did the countdown feel steady? Which number felt off, if any?"]
EX_AUTO = ("The riser fades in over bars 9 and 10 and swells to bar 17; the filter cutoff and the pitch rise together; the kick, bass and hi-hat stop at bar 17 and return on bar 22; "
           "the numbers are 3 dB above the riser")


# ================================================================ drawings (all in code, labels logged for the fit check)
def padded(body, W, H, M=10):
    """Wrap a drawing's body with M units of clear padding on all four sides (wider than the thickest outer stroke), so no edge pixel is ever inked."""
    return f'<g transform="translate({M},{M})">{body}</g>', W + 2 * M, H + 2 * M


def map_body(W=1600, with_time=False, name="map", lf=24, lh=46):
    """The section map: 10 elements (rows) x 5 sections (columns). A cell is filled when the element plays in that section and says what it does there."""
    gx = 340
    pw = W - gx - 30
    cw = pw / 5
    hh = 106 if with_time else 80
    out = []
    for i, nm in enumerate(SEC_NAMES):
        cx = gx + (i + 0.5) * cw
        l1 = nm.upper()
        l2 = f"bars {start_bar(EX_BPM, i)}–{start_bar(EX_BPM, i) + sec_bars(EX_BPM)[i] - 1}" if with_time else ("4 to 6 bars" if i == 2 else f"{sec_bars(EX_BPM)[i]} bars")
        out.append(D.t_(cx, 32, l1, 26, 700))
        D.lab(name + " heads", l1, 26, cw - 14)
        out.append(D.t_(cx, 62, l2, 21, 500, fill_="#555"))
        D.lab(name + " bars", l2, 21, cw - 14)
        if with_time:
            l3 = f"{fmt(start_s(EX_BPM, i))}–{fmt(start_s(EX_BPM, i + 1))} s"
            out.append(D.t_(cx, 92, l3, 21, 500, fill_=ACCENT))
            D.lab(name + " times", l3, 21, cw - 14)
    y0 = hh + 8
    gap = 6
    for r, (el, cells) in enumerate(ELEMENTS):
        yy = y0 + r * (lh + gap)
        lbl = el.upper()
        out.append(D.t_(gx - 16, yy + lh / 2 + lf * .35, lbl, lf, 700, anchor="end"))
        D.lab(name + " rows", lbl, lf, gx - 30)
        for i, txt in enumerate(cells):
            x = gx + i * cw + 3
            if txt:
                out.append(f'<rect x="{x:.1f}" y="{yy}" width="{cw - 6:.1f}" height="{lh}" rx="6" fill="{ACC_LIGHT}" stroke="#000" stroke-width="2.5"/>')
                out.append(D.t_(x + (cw - 6) / 2, yy + lh / 2 + 7, txt, 21, 600))
                D.lab(name + " cells", txt, 21, cw - 24)
            else:
                out.append(f'<rect x="{x:.1f}" y="{yy}" width="{cw - 6:.1f}" height="{lh}" rx="6" fill="#fff" stroke="#bbb" stroke-width="1.5"/>')
    yb = y0 + len(ELEMENTS) * (lh + gap) + 6
    out.append(f'<line x1="{gx}" y1="{yb - 6}" x2="{gx + pw:.1f}" y2="{yb - 6}" stroke="#000" stroke-width="2.5"/>')
    lbl = "ELEMENTS PLAYING"
    out.append(D.t_(gx - 16, yb + 34, lbl, lf, 700, anchor="end", fill_=ACCENT))
    D.lab(name + " rows", lbl, lf, gx - 30)
    for i in range(5):
        out.append(D.t_(gx + (i + 0.5) * cw, yb + 36, str(ELEM_PLAYING[i]), 34, 700))
    if with_time:
        cap = f"{total_bars(EX_BPM)} bars at {EX_BPM} BPM in 4/4: {total_bars(EX_BPM)} × {fmt(EX_BAR_S)} = {fmt(total_s(EX_BPM))} seconds"
    else:
        cap = "Shaded: the element plays in that section. The countdown thins out, so the drop is the biggest section."
    out.append(D.t_(gx + pw / 2, yb + 86, cap, 24, 500))
    D.lab(name + " cap", cap, 24, pw)
    return padded("".join(out), W, yb + 100, 14)


def time_body(W=1600, name="time"):
    """The 10-second countdown on one time axis: the numbers 10 to 1 and the drop, then the bars at 96, 120 and 144 BPM (4, 5 and 6 whole bars)."""
    gx = 270
    pw = W - gx - 70
    sc = pw / CD_SECONDS
    out = []
    out.append(D.t_(gx - 44, 52, "SECOND", 22, 700, anchor="end", fill_=ACCENT))
    D.lab(name + " rows", "SECOND", 22, gx - 60)
    out.append(D.t_(gx - 44, 112, "YOU SAY", 22, 700, anchor="end", fill_=ACCENT))
    D.lab(name + " rows", "YOU SAY", 22, gx - 60)
    for s in range(CD_SECONDS + 1):
        x = gx + s * sc
        out.append(D.t_(x, 52, str(s), 26, 500, fill_="#555"))
        word = "DROP" if s == CD_SECONDS else str(number_at(s))
        out.append(D.t_(x, 112, word, 38 if s < CD_SECONDS else 34, 700, fill_="#000" if s < CD_SECONDS else ACCENT))
        D.lab(name + " says", word, 38, sc - 20)
        out.append(f'<line x1="{x:.1f}" y1="124" x2="{x:.1f}" y2="{(386 if s in (0, 10) else 140)}" stroke="#000" stroke-width="{2.5 if s in (0, 10) else 1.5}" '
                   f'stroke-dasharray="{"" if s in (0, 10) else "5 6"}"/>')
    ys = [150, 232, 314]
    for bpm, y in zip(CHOICES, ys):
        c = int(cd_bars(bpm))
        lb = f"{bpm} BPM"
        out.append(D.t_(gx - 20, y + 38, lb, 32, 700, anchor="end"))
        D.lab(name + " rows", lb, 32, gx - 40)
        l2 = f"{c} bars of {num(bar_len(bpm), 3)} s"
        out.append(D.t_(gx - 20, y + 66, l2, 20, 500, anchor="end", fill_=ACCENT))
        D.lab(name + " rows", l2, 20, gx - 22)
        bl = float(bar_len(bpm))
        for k in range(c):
            x0 = gx + k * bl * sc
            out.append(f'<rect x="{x0 + 3:.1f}" y="{y}" width="{bl * sc - 6:.1f}" height="70" rx="8" fill="{ACC_LIGHT if k % 2 == 0 else "#fff"}" stroke="#000" stroke-width="2.5"/>')
            lbl = str(CD_START_BAR + k)
            out.append(D.t_(x0 + bl * sc / 2, y + 47, lbl, 30, 700))
            D.lab(name + " barnums", lbl, 30, bl * sc - 20)
    cap = "Blocks are bars (bar numbers inside). The 10 seconds end exactly on a bar line, where the drop begins."
    out.append(D.t_(gx + pw / 2, 438, cap, 24, 500))
    D.lab(name + " cap", cap, 24, W - 60)
    return padded("".join(out), W, 456, 14)


def ladder_body(W=1500, name="ladder"):
    """The snare-roll ladder: one beat at 120 BPM (500 ms) split into 1, 2, 4 and 8 equal parts; a dot marks each hit."""
    gx, gx2 = 330, 1130
    out = []
    out.append(D.t_(gx - 20, 40, "NOTE VALUE", 22, 700, anchor="end", fill_=ACCENT))
    D.lab(name + " rows", "NOTE VALUE", 22, gx - 40)
    out.append(D.t_((gx + gx2) / 2, 40, f"ONE BEAT AT {EX_BPM} BPM = {num(spb(EX_BPM) * 1000)} ms", 24, 700))
    D.lab(name + " head", f"ONE BEAT AT {EX_BPM} BPM = {num(spb(EX_BPM) * 1000)} ms", 24, gx2 - gx)
    out.append(D.t_(W - 20, 40, "GAP BETWEEN HITS", 22, 700, anchor="end", fill_=ACCENT))
    D.lab(name + " rows", "GAP BETWEEN HITS", 22, W - gx2 - 40)
    y0 = 70
    for r, (nv, nm, h) in enumerate(LADDER):
        y = y0 + r * 108
        out.append(D.t_(gx - 20, y + 36, nv, 38, 700, anchor="end"))
        out.append(D.t_(gx - 20, y + 66, f"{h} hit{'s' if h > 1 else ''} per beat", 21, 500, anchor="end", fill_="#555"))
        D.lab(name + " rows", f"{h} hits per beat", 21, gx - 40)
        out.append(f'<line x1="{gx}" y1="{y + 44}" x2="{gx2}" y2="{y + 44}" stroke="#000" stroke-width="2.5"/>')
        for t in (0, 1):
            x = gx + t * (gx2 - gx)
            out.append(f'<line x1="{x}" y1="{y + 12}" x2="{x}" y2="{y + 76}" stroke="#000" stroke-width="4"/>')
        for k in range(h):
            cx = gx + (gx2 - gx) * k / h
            out.append(f'<circle cx="{cx:.1f}" cy="{y + 44}" r="13" fill="{ACCENT}" stroke="#000" stroke-width="2.5"/>')
        ms_txt = f"{num(gap_ms(EX_BPM, h))} ms"
        out.append(D.t_(W - 20, y + 54, ms_txt, 36, 700, anchor="end"))
        D.lab(name + " ms", ms_txt, 36, W - gx2 - 40)
    cap = "Each rung doubles the hits and halves the gap: 60000 ÷ (BPM × hits per beat) milliseconds."
    out.append(D.t_(W / 2, y0 + 4 * 108 + 14, cap, 24, 500))
    D.lab(name + " cap", cap, 24, W - 40)
    return padded("".join(out), W, y0 + 4 * 108 + 30, 14)


def sweep_body(W=1200, name="sweep"):
    """The filter sweep and the pitch-up over the build-up: cutoff in Hz on a log scale and pitch in semitones, bars 9 to 17."""
    gx, gx2 = 50, W - 60
    b0, b1 = EX_SWEEP[0][0], EX_SWEEP[-1][0]
    out = []

    def bx(b):
        return gx + (gx2 - gx) * (b - b0) / (b1 - b0)
    top, bot = 60, 300
    t1 = "LOW-PASS CUTOFF (Hz, log scale)"
    out.append(D.t_(gx, 40, t1, 26, 700, anchor="start", fill_=ACCENT))
    D.lab(name + " titles", t1, 26, gx2 - gx)
    out.append(f'<rect x="{gx}" y="{top}" width="{gx2 - gx}" height="{bot - top}" fill="#fff" stroke="#000" stroke-width="2.5"/>')
    pts = []
    for b, hz in EX_SWEEP:
        yv = bot - 24 - (bot - top - 70) * (math.log(hz / 100) / math.log(20000 / 100))
        pts.append((bx(b), yv, b, hz))
    out.append(f'<polyline points="{" ".join(f"{x:.1f},{y:.1f}" for x, y, _, _ in pts)}" fill="none" stroke="{ACCENT}" stroke-width="7" stroke-linejoin="round" stroke-linecap="round"/>')
    for x, y, b, hz in pts:
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="11" fill="#fff" stroke="#000" stroke-width="3"/>')
        lbl = f"{hz:,} Hz"
        anc = "start" if b == b0 else ("end" if b == b1 else "middle")
        lx = x + (4 if b == b0 else (-4 if b == b1 else 0))
        out.append(D.t_(lx, y - 20, lbl, 24, 700, anchor=anc))
        D.lab(name + " hz", lbl, 24, 150)
    top2, bot2 = 370, 560
    t2 = "RISER PITCH (semitones)"
    out.append(D.t_(gx, 350, t2, 26, 700, anchor="start", fill_=ACCENT))
    D.lab(name + " titles", t2, 26, gx2 - gx)
    out.append(f'<rect x="{gx}" y="{top2}" width="{gx2 - gx}" height="{bot2 - top2}" fill="#fff" stroke="#000" stroke-width="2.5"/>')
    p2 = []
    for b, _ in EX_SWEEP:
        st = EX_PITCH_ST * (b - b0) / (b1 - b0)
        yv = bot2 - 28 - (bot2 - top2 - 78) * st / EX_PITCH_ST
        p2.append((bx(b), yv, b, st))
    out.append(f'<polyline points="{" ".join(f"{x:.1f},{y:.1f}" for x, y, _, _ in p2)}" fill="none" stroke="#000" stroke-width="5" stroke-dasharray="14 9" stroke-linecap="round"/>')
    for x, y, b, st in p2:
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="10" fill="{ACCENT}" stroke="#000" stroke-width="3"/>')
        lbl = f"+{fmt(st)}" if st else "0"
        anc = "start" if b == b0 else ("end" if b == b1 else "middle")
        lx = x + (4 if b == b0 else (-4 if b == b1 else 0))
        out.append(D.t_(lx, y - 20, lbl, 24, 700, anchor=anc))
        D.lab(name + " st", lbl, 24, 100)
    for b, _ in EX_SWEEP:
        lbl = f"bar {b}"
        out.append(D.t_(bx(b), 600, lbl, 24, 500, anchor="middle" if b not in (b0, b1) else ("start" if b == b0 else "end")))
        D.lab(name + " bars", lbl, 24, 110)
    cap = "Example values: 200 Hz to 12,000 Hz, and 12 semitones (one octave), both by bar 17."
    out.append(D.t_((gx + gx2) / 2, 646, cap, 23, 500))
    D.lab(name + " cap", cap, 23, gx2 - gx)
    return padded("".join(out), W, 662, 14)


def hero_body():
    """The owner's pre-made art (art/hero.png, used whole). The viewBox only trims fully transparent margin: the art's own pixels
    (x 44-1357, y 131-1317 of 1400) stay at least 40 units inside it, which --check proves from the file."""
    return (f'<image href="../art/hero.png" x="{-HX}" y="{-HY}" width="1400" height="1400"/>', HW, HH)


HX, HY, HW, HH = 0, 90, 1400, 1270

DRAWINGS = {"hero": hero_body, "map": lambda: map_body(1600, False, "map deck"), "time": lambda: time_body(1600, "time deck"),
            "ladder": lambda: ladder_body(1500, "ladder deck"), "sweep": lambda: sweep_body(1200, "sweep deck"), "exmap": lambda: map_body(1600, True, "exmap deck")}
DRAWING_PX = {"hero": 1340, "map": 2000, "time": 2000, "ladder": 2000, "sweep": 2000, "exmap": 2000}
SIDE = {"map": ["Five sections, one track", "The drop is the biggest section", "The countdown thins the sound out", "Every element has a job"],
        "time": ["One bar = 240 ÷ BPM seconds", "Bars in 10 seconds = BPM ÷ 24", "96, 120, 144 BPM: 4, 5, 6 bars", "The drop is on the first beat after 1"],
        "ladder": ["1, 2, 4 and 8 hits per beat", "Gap = 60000 ÷ (BPM × hits)", "At 120 BPM: 500, 250, 125, 62.5 ms", "Two bars on each rung"],
        "sweep": ["Open the filter across the build-up", "Climb the pitch one octave", "Both reach their top at bar 17", "Draw both with automation"],
        "exmap": ["An invented plan at 120 BPM", "Countdown: bars 17 to 21", "The drop lands on bar 22", "The whole track lasts 90 seconds"]}
# extra drawings used on pages only, rendered alone on a transparent ground by --check as well
PAGE_DRAWINGS = {"map-page": lambda: map_body(1500, False, "map page", 23, 38), "exmap-page": lambda: map_body(1500, True, "exmap page", 23, 38),
                 "time-page": lambda: time_body(1500, "time page"), "ladder-page": lambda: ladder_body(1400, "ladder page"),
                 "sweep-page": lambda: sweep_body(1200, "sweep page")}


def label_extras():
    map_body(1500, False, "map page", 23, 38)
    map_body(1500, True, "exmap page", 23, 38)
    time_body(1500, "time page")
    ladder_body(1400, "ladder page")
    sweep_body(1200, "sweep page")


# ================================================================ intro deck: (class, kind, title, body, speaker notes)
SLIDES = [
    (1, "title", "New Year’s Countdown", "Build the tension. Count down. Drop.",
     "Class 1, the first minute. No audio is included in this deck. Open with the idea: you will arrange a track of 40 to 48 bars in Logic Pro that builds tension with risers, a snare roll "
     "and a filter sweep, counts down ten seconds, and then drops. Students choose a tempo, do the timing math, build the parts and mix them. Nobody needs to play an instrument or read "
     "music, and no melody is given."),
    (1, "listen", "Hear the build", "Think, then share|Teacher: read aloud, no audio plays. A low hum begins and slowly rises. A drum taps, then taps faster and faster. A voice counts down from ten. "
     "Then there is a pause, and everything lands at once.|What makes you feel that something is about to happen?|What gets faster, higher or brighter as the tension rises?|"
     "What does the pause before the drop do?",
     "Read the scene aloud slowly and ask the three questions. Take a few answers. Nothing is played from a speaker. Students will name the rising pitch, the faster drum hits, the counting and the "
     "silence. Write their words on the board. The project turns each of those ideas into a tool with a number attached: a riser, a snare roll that speeds up, a filter sweep, a countdown and a drop."),
    (1, "bullets", "What is the New Year’s Countdown project?", "Arrange 40 to 48 bars in five sections|Build tension with risers, a snare roll and a filter sweep|"
     "Count down 10 seconds, one number per second|Land the drop on the first beat after 1",
     "The project in four lines. Every student arranges a track of 40 to 48 bars in Logic Pro: an intro, a build-up, a 10-second countdown, the drop and an outro. The build-up uses a riser, a snare roll "
     "that speeds up through four note values, a filter sweep and a pitch-up. The numbers 10 to 1 sit one second apart, and the drop lands on the first beat after 1. There is no melody to learn and no "
     "audio ships: students make every sound."),
    (1, "days", "Three classes", "",
     "The shape of the project. Class 1: hook, the section map, the timing math and the plan. Class 2: set up Logic, build the intro and the build-up. Class 3: place the countdown, land the drop, "
     "mix, bounce, present and reflect. With two classes, plan and set up in Class 1 and build everything in Class 2; with four, add a day for the mix and the presentations. "
     "Hand out the tempo table, the section map, the snare-roll ladder and the cue sheet now."),
    (1, "pic", "Five sections, one track", "map",
     f"Class 1. This is the section map: ten elements down the side and five sections across. A shaded cell means the element plays in that section, and the words say what it does. Ask the class to count the "
     f"elements in each section: 3, 6, 4, 7 and 4. The countdown has fewer elements than the build-up, so the drop feels bigger when everything returns. The map is on page {pg('map')}, "
     f"and the Logic setup is on page {pg('logicref')}."),
    (1, "bullets", "The math: tempo = 24 × bars", "One bar of 4/4 lasts 240 ÷ BPM seconds|10 seconds should be a whole number of bars|Tempo = 24 × bars of countdown|96, 120 or 144 BPM: 4, 5 or 6 bars",
     f"Class 1, the key idea. In 4/4 there are four beats in a bar, so one bar lasts 240 divided by the tempo, in seconds. Ten seconds is 10 divided by that, which is the tempo divided by 24 bars. "
     f"That is a whole number only when the tempo is 24 times a whole number: 96 BPM gives 4 bars, 120 gives 5 and 144 gives 6. At 100 BPM it is 4.1667 bars, so the number 1 would not end on a bar line. "
     f"The tempo table is on page {pg('tempo')}."),
    (2, "pic", "The snare-roll ladder", "ladder",
     f"Class 2. A snare roll gets faster in steps. One hit per beat is quarter notes, two are eighth notes, four are sixteenth notes and eight are thirty-second notes. At 120 BPM a beat lasts 500 "
     f"milliseconds, so the gaps are 500, 250, 125 and 62.5 milliseconds. Each step doubles the hits and halves the gap. Students spend two bars on each step across the eight bars of the build-up. "
     f"The ladder is on page {pg('ladder')}."),
    (2, "pic", "Filter sweep and pitch-up", "sweep",
     f"Class 2. Two more tools raise the tension. A filter sweep opens a low-pass filter, so a muffled sound slowly brightens; here the cutoff rises from 200 Hz to 12,000 Hz across the build-up. "
     f"A pitch-up climbs the riser by 12 semitones, one octave. Both are drawn with automation and reach their top at bar 17. These are example values, not rules. The automation checklist is on "
     f"page {pg('ladder')}."),
    (2, "steps", "Build it in Logic", "Set the tempo; keep 4/4|A marker at the start of each section|Build the intro, then the riser|Draw the roll, the sweep and the pitch-up|Mix and bounce",
     f"Class 2. Demonstrate on the projector. Set the tempo to 96, 120 or 144 BPM and keep 4/4. Put a marker at the start of each of the five sections. Build the intro, then the riser, the snare roll, the "
     f"filter sweep and the pitch-up across bars 9 to 16. Menu names and button places move between Logic versions; the quick reference on page {pg('logicref')} hedges where they do, and says which "
     f"tools to use only if your version has them."),
    (3, "pic", "The 10-second countdown", "time",
     f"Class 3. At 120 BPM one bar is 2 seconds, so the 10-second countdown is exactly 5 bars: the number 10 on bar 17 beat 1, the number 1 on bar 21 beat 3, and the drop on bar 22 beat 1. At 96 BPM it is 4 bars "
     f"of 2.5 seconds and at 144 BPM it is 6 bars of about 1.67 seconds. Students place their numbers with the cue sheet on page {pg('cues')}; the full example is on pages {pg('example')} and {pg('example2')}."),
    (3, "check", "What you turn in", "Bounced .mp3 or .wav, 40 to 48 bars long|Zipped .logicx project|Named: Your Name – Countdown|Tempo table work, section map and cue sheet|"
     "Reflection page|Rubric self-score and three questions",
     "Class 3. The submission checklist, shortened to fit the slide. Show where students hand in. The file name is Your Name, then Countdown. Check the length before students bounce: "
     "the bounce should run the whole track, which is 90 seconds at 120 BPM, 110 seconds at 96 BPM and about 76.7 seconds at 144 BPM."),
    (3, "rubric", "How it’s scored", "",
     "The rubric: five categories, each scored 1 to 5, for a total out of 25. Students score themselves first; the final grade is the average of their score and yours. "
     "The slide reads the 5 column of each category aloud. Hand out the rubric page so students can self-score before they present."),
    (3, "bullets", "Presentation day", "Play your track from the top|Point out each part of the build as it arrives|Your three questions for classmates|Answer at least 2 of each classmate’s questions",
     "Class 3, presentations. Each student plays the track from the top and points out the riser, the roll, the sweep, the countdown and the drop as they arrive, with their bar numbers. Students write three "
     "questions they want classmates to answer, and answer at least two of each classmate's. Ask the class to say the numbers along with the track and see whether the drop lands where they expect."),
    (3, "closer", "One last thing…", "Build it slowly.|Count it exactly.|Take things away.|Then let it drop.",
     "Close with the listening day: play a track and ask the class to call out the moment the tension is highest, then count along with the numbers. A drop that people can predict to the beat "
     "is a drop that was well planned and well timed. Ask a few students which tool did the most for the tension. No audio is included in this resource; the sounds are the students' own."),
]
SHOTS1 = [("pacing", "Pacing guide", "3 class periods, slide by slide"), ("map", "Section map", "Five sections, ten elements"),
          ("tempo", "Tempo table", "Seconds, bars and section starts")]
SHOTS2 = [1, 5, 6, 7, 8, 10]
SHOTS3 = [("tempo", "Tempo table"), ("map", "Section map"), ("ladder", "Snare ladder"), ("cues", "Cue sheet"), ("mix", "Mix checklist"),
          ("example", "Worked example"), ("example2", "Worked example 2"), ("rubric", "Rubric")]
PREVIEW_PICKS = ["pacing", "ladder", "tempo", "rubric"]

COVER_A = "Build the tension, count down, drop"
COVER_C = "Logic Pro · Risers · Snare rolls · Timing math"
PDF_COVER = dict(a=26, b=42, c=15, art=5.0)
SQ_COVER = dict(a=36, b=140, c=27, art=420, gap=20)
SQ_B_LINES = ["New Year’s", "Countdown"]
SQ_SUB = "3 class periods · build-up and drop · timing math · intro slides"
SQ_HEADS = {1: ("Ready to teach Monday", 76, "Pacing, tempo table, snare ladder and the /25 rubric in one PDF", 28),
            2: ("Intro deck included", 76, f"{len(SLIDES)} editable slides (.pptx + PDF) with speaker notes on every slide", 28),
            3: ("Everything inside", 72, "Tempo table, section map, cue sheet, worked example and worksheets", 28)}
SQ_BANDS = {1: "Risers <em>·</em> snare rolls <em>·</em> filter sweep <em>·</em> drop",
            2: "Section map <em>·</em> snare ladder <em>·</em> cue sheet",
            3: f"{len(PLAN)} pages <em>·</em> US Letter PDF <em>·</em> no audio included"}


# ================================================================ small page helpers
CSS_SG = ("<style>table.sg { border-collapse: collapse; width: 100%; table-layout: fixed; } table.sg td, table.sg th { border: 1pt solid #000; text-align: center; "
          "padding: 0; font-size: 8.6pt; } table.sg th { background: #000; color: #fff; font-family: Oswald; font-weight: 500; height: 14pt; } "
          "table.sg td.l { text-align: left; padding: 0 4pt; font-weight: 700; width: 1.45in; font-size: 8.8pt; } "
          "table.sg td.g { background: #e4e4e4; } </style>")
CSS_CC = ("<style>table.cc td { text-align: center; padding: 2pt 3pt; font-size: 9.4pt; line-height: 1.15; } table.cc th { text-align: center; font-size: 9pt; } "
          "table.cc td.l { text-align: left; } table.cc tr.hi td { background: #eef5fb; }</style>")


def howto_page(n, wm=False):
    parts = [("Teacher pages", "howto", "example2", "How to use, overview, setup, pacing, teacher notes, Logic quick reference, worked example (2 pages)"),
             ("Student pages", "tempo", "reflect", "Tempo table, section map, snare ladder and checklists, cue sheet, mix checklist, "
              "project sheet (3 pages), rubric, vocabulary, feedback planner, reflection page"),
             ("Intro deck (separate file)", None, None, f"{len(SLIDES)} slides, .pptx + PDF, speaker notes on every slide")]
    trs = "".join(f"<tr><td><b>{a}</b></td><td style='white-space:nowrap'>{('pages ' + str(D.IX(f)) + '–' + str(D.IX(l))) if f else 'deck'}</td>"
                  f"<td>{u}</td></tr>" for a, f, l, u in parts)
    inner = (f'<div class="cols"><div>'
             f'{D.H2("What this is", True)}'
             f'<p style="font-size:12pt;line-height:1.45">A {CLASSES}-class-period build-up and drop project for high school music technology. Every '
             f'student arranges a track of 40 to 48 bars in Logic Pro: an intro, a build-up with risers, a snare roll and a filter sweep, a 10-second countdown, the drop and an outro. '
             f'Students choose a tempo, do the timing math, build and mix the parts, present the result and reflect on it. It is an original Hudson Beat project.</p>'
             f'{D.H2("Quick start")}<ol>'
             f'<li style="margin-bottom:5pt">Read the pacing guide (page {D.IX("pacing")}) and the teacher notes (pages {D.IX("tn1")}–{D.IX("tn2")}).</li>'
             f'<li style="margin-bottom:5pt">Look at the tempo table, the section map, the snare ladder and the cue sheet (pages {D.IX("tempo")}–{D.IX("cues")}) and the setup (page {D.IX("setup")}).</li>'
             f'<li style="margin-bottom:5pt">Print the student pages (pages {D.IX("tempo")}–{D.IX("reflect")}), one set per student.</li>'
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
             f'<li><b>Pace:</b> Class 1 is the timing math and the plan, Class 2 the intro and the build-up, Class 3 the countdown, the drop, the mix and the presentations (page {D.IX("pacing")}); the pacing page also shows two and four periods.</li>'
             f'<li><b>Another countdown?</b> The build-up and drop works for any class; students may count down to a launch, a game start or a finish line (page {D.IX("overview")}).</li>'
             f'<li><b>Grading:</b> the rubric, /{RUBRIC_TOTAL}, the average of the student’s and your score (page {D.IX("rubric")}).</li></ul>'
             f'<div class="box" style="margin-top:6pt"><span class="k">In one sentence</span><p style="margin:0;font-size:12pt">Students learn that '
             f'a drop is planned: a tempo that fits ten seconds into whole bars, tension tools that speed up and open, and ten numbers placed on exact beats.</p></div>'
             f'<p class="small" style="margin-top:6pt">Logic Pro is a product of Apple Inc. This resource is not affiliated with Apple.</p>'
             f'</div></div>')
    return D.page("How to use this resource", "START HERE", "Teacher", inner, n, key="howto")


def overview_page(n, wm=False):
    inner = (f'<div class="cols"><div>'
             f'<div class="box inv" style="margin-bottom:6pt"><span class="k">The project in one line</span><p style="margin:0;font-size:12pt">'
             f'<b>{TITLE}</b> · Build-up and drop · Logic Pro<br>Five sections, ten seconds of numbers, one big drop.</p></div>'
             f'{D.H2("What students make")}'
             f'<p style="font-size:12.2pt;line-height:1.48">A track of 40 to 48 bars in five sections, built in Logic Pro: an 8-bar intro, an 8-bar build-up, a countdown of 4, 5 or 6 bars, a 16-bar drop and an 8-bar outro. '
             f'The build-up has a riser, a snare roll that speeds up from quarter to eighth, sixteenth and thirty-second notes, a filter sweep and a pitch-up. The countdown is the numbers 10 to 1, one on each second, '
             f'and the drop lands on the first beat after 1. Students hand in a bounced file and the zipped .logicx project, plus their plans and a reflection, '
             f'then play the track and take questions.</p>'
             f'{D.H2("What this project reinforces")}<p style="font-size:12pt;line-height:1.5">{TN_REINFORCES}</p>'
             f'{D.H2("Standards")}<p style="font-size:11.4pt">Supports the National Core Arts Standards for Music (Music Technology, high school): generating '
             f'and developing ideas (MU:Cr1.1, MU:Cr2.1), presenting work (MU:Pr6.1) and responding to it (MU:Re7.2).</p>'
             f'</div><div>'
             f'{D.H2("Goals", True)}<ul>' + "".join(f"<li style='font-size:12pt;line-height:1.45'>{g}</li>" for g in GOALS) + '</ul>'
             f'{D.H2("About the theme")}<div class="box acc-b" style="padding:5pt 9pt"><p style="margin:0 0 3pt;font-size:10.2pt;line-height:1.36">{THEME}</p>'
             f'<p style="margin:0;font-size:10.2pt;line-height:1.36">{BUILD_NOTE}</p></div>'
             f'<div class="box" style="margin-top:6pt;padding:5pt 9pt"><span class="k">At a glance</span><p style="margin:0;font-size:10.2pt;line-height:1.38"><b>Grades</b> {GRADES_TEXT}, music technology or music production · '
             f'<b>Length</b> {CLASSES} class periods (two and four also shown) · <b>Software</b> Logic Pro · <b>You supply</b> Macs with Logic Pro, headphones and a place to hand in files · '
             f'<b>Assessment</b> rubric, 5 categories scored 1–5, /{RUBRIC_TOTAL} (page {D.IX("rubric")})</p></div>'
             f'</div></div>')
    return D.page("Project overview", "OVERVIEW", "Build-up and drop project", inner, n, key="overview")


def setup_page(n, wm=False):
    inner = (f'<style>.sb p, .sb li {{ font-size: 11.6pt; line-height: 1.44; margin-bottom: 5pt; }}</style><div class="cols"><div class="big sb">'
             f'{D.H2("You need", True)}<ul>'
             f'<li><b>A Mac with Logic Pro</b> for each student, and <b>headphones</b>.</li>'
             f'<li><b>A place to hand in</b> the .mp3 or .wav files, the zipped .logicx and the reflection.</li>'
             f'<li><b>The tempo table, section map, snare ladder and cue sheet</b>, printed (pages {D.IX("tempo")}–{D.IX("cues")}), or shown on the projector.</li>'
             f'<li><b>Printed student pages</b>, one set each (pages {D.IX("tempo")}–{D.IX("reflect")}).</li>'
             f'<li><b>A microphone</b> is optional: the countdown can be beeps made with a synth. A MIDI keyboard is optional too.</li></ul>'
             f'{D.H2("Before Class 1")}'
             + "".join(D.chk(c, 13, "font-size:11.6pt;margin-bottom:7pt") for c in [
                 f"Read the tempo table (page {D.IX('tempo')}) so you can answer ‘where does the drop land?’ at 96, 120 and 144 BPM.",
                 f"Open Logic Pro on a student computer and check which tools your version has: Alchemy, Quick Sampler, Drum Machine Designer, Step Sequencer, Channel EQ (see page {D.IX('logicref')}).",
                 f"Check that you can add a marker and draw filter automation.",
                 f"Read the worked example (pages {D.IX('example')}–{D.IX('example2')})."]) +
             f'</div><div class="big sb">'
             f'{D.H2("What to watch", True)}'
             f'<p style="font-size:11.4pt">Watch for numbers that drift off the second, a roll that does not speed up, a build-up that is already loud before it starts, and a drop that is not louder than the countdown. {TN_NOTE}</p>'
             f'<div class="box acc-b" style="margin-top:2pt"><span class="k">Ideas for the room</span><ul style="margin:0">'
             f'<li style="font-size:11.2pt">Ask while students work: what is rising right now? What could you take away before the drop?</li>'
             f'<li style="font-size:11.2pt">Say the theme plainly: the countdown is an inspiration for the structure, and students may count down to anything.</li>'
             f'<li style="font-size:11.2pt">A student who is stuck can build the riser, the countdown and the drop only: those three already sound like a build-up.</li></ul></div>'
             f'{D.H2("The voice (optional)")}'
             f'<div class="box"><p style="margin:0;font-size:10.8pt;line-height:1.4">{VOICE_NOTE}</p></div>'
             f'<div class="box" style="margin-top:6pt"><span class="k">Keep the volume moderate</span><p style="margin:0;font-size:11pt;line-height:1.4">'
             f'Rising sounds, fast drum rolls and a big drop can be tiring in headphones. Tell students to start low and check the final mix at a normal level.</p></div>'
             f'</div></div>')
    return D.page("Setup and what to watch", "SETUP", "Teacher", inner, n, key="setup")


# ================================================================ the tempo table, section map, ladder, cue sheet and mix pages
def tempo_a_rows():
    rows = []
    for bpm in TEMPOS:
        w = is_whole(bpm)
        b, e = ("<b>", "</b>") if w else ("", "")
        c = cd_bars(bpm)
        cs = fmt(c) if w else dec(c, 4)
        hi = ' class="hi"' if w else ''
        rows.append(f"<tr{hi}><td>{b}{bpm}{e}</td><td>{dec(spb(bpm), 3)}</td><td>{dec(bar_len(bpm), 3)}</td><td>{b}{cs}{e}</td>"
                    f"<td>{b}{'Yes' if w else 'No'}{e}</td></tr>")
    return "".join(rows)


def tempo_b_rows():
    rows = []
    for bpm in CHOICES:
        sb = sec_bars(bpm)
        rows.append(f"<tr><td><b>{bpm}</b></td><td>{sb[2]}</td><td>{start_bar(bpm, 3)}</td><td>{start_bar(bpm, 4)}</td><td><b>{total_bars(bpm)}</b></td><td><b>{dec(total_s(bpm), 2)}</b></td>"
                    + "".join(f"<td>{dec(start_s(bpm, i), 2)}</td>" for i in (1, 2, 3, 4)) + "</tr>")
    return "".join(rows)


def tempo_page(n, wm=False):
    inner = (CSS_CC +
             f'<p style="margin:0 0 4pt;font-size:10.2pt;line-height:1.36">Step 1: choose tempo and map. In 4/4 there are 4 beats in a bar. These formulas turn a tempo into seconds and bars. '
             f'Every number below is computed, so you can check your own arithmetic against it.</p>'
             f'<div class="cols" style="gap:10pt;align-items:flex-start"><div class="box acc-b" style="padding:5pt 9pt;flex:1.15"><span class="k">The formulas (4/4)</span>'
             f'<p style="margin:0 0 2pt;font-size:9.8pt"><b>Seconds per beat</b> = 60 ÷ BPM</p><p style="margin:0 0 2pt;font-size:9.8pt"><b>Seconds per bar</b> = 240 ÷ BPM</p>'
             f'<p style="margin:0 0 2pt;font-size:9.8pt"><b>Bars in 10 seconds</b> = 10 ÷ (240 ÷ BPM) = BPM ÷ 24</p>'
             f'<p style="margin:0 0 2pt;font-size:9.8pt"><b>Tempo = 24 × bars</b>, when 10 seconds is a whole number of bars</p>'
             f'<p style="margin:0 0 2pt;font-size:9.8pt"><b>A section starts at</b> (bars gone by) × 240 ÷ BPM seconds</p>'
             f'<p style="margin:0;font-size:9.8pt"><b>Example:</b> 120 BPM: 240 ÷ 120 = 2 s per bar, 10 ÷ 2 = 5 bars, and 120 ÷ 24 = 5 too.</p></div>'
             f'<div class="box" style="padding:5pt 9pt;flex:1"><span class="k">Rounding rules</span><p style="margin:0;font-size:9.2pt;line-height:1.32">Seconds per beat and per bar to 3 decimals, '
             f'bars in 10 seconds to 4, and seconds for sections and totals to 2; a 5 rounds up. So 240 ÷ 144 = 1.667 seconds per bar, and the 16 bars before the countdown at 144 BPM last '
             f'26.67 seconds (26.666… rounds up). Every start time is rounded from its exact value.</p></div></div>'
             f'<span class="k" style="margin-top:5pt">Is 10 seconds a whole number of bars?</span>'
             f'<table class="t cc" style="margin-top:1pt"><tr><th>BPM</th><th>Seconds per beat</th><th>Seconds per bar</th><th>Bars in 10 seconds</th><th>Whole bars?</th></tr>{tempo_a_rows()}</table>'
             f'<p class="small" style="margin:0 0 2pt;font-size:8.6pt">Shaded rows are whole numbers of bars. Choose one of them: 96, 120 or 144 BPM. At 100 BPM the countdown would be 4.1667 bars, so the number 1 and the drop would fall in the middle of a bar.</p>'
             f'<span class="k" style="margin-top:3pt">Where does each section start? The three tempos you may choose</span>'
             f'<table class="t cc" style="margin-top:1pt"><tr><th rowspan="2">BPM</th><th rowspan="2">Countdown bars</th><th colspan="2">Starts at bar</th><th rowspan="2">Total bars</th><th rowspan="2">Total seconds</th><th colspan="4">Section starts at (seconds)</th></tr>'
             f'<tr><th>Drop</th><th>Outro</th><th>Build-up</th><th>Countdown</th><th>Drop</th><th>Outro</th></tr>{tempo_b_rows()}</table>'
             f'<p class="small" style="margin:0 0 3pt;font-size:8.6pt">The intro starts at bar 1 (0 seconds), the build-up at bar 9 and the countdown at bar 17 at every tempo, because the intro and the build-up are 8 bars each. '
             f'The drop starts exactly 10 seconds after the countdown does.</p>'
             f'<div class="box acc-b" style="padding:5pt 9pt"><span class="k">My tempo</span>'
             f'<div class="fl" style="margin:3pt 0 3pt;font-size:10pt"><b>Tempo (96, 120 or 144 BPM):</b><span></span><b>One bar = 240 ÷ BPM =</b><span></span><b>s</b></div>'
             f'<div class="fl" style="margin:0;font-size:10pt"><b>Countdown = 10 ÷ one bar =</b><span></span><b>bars</b><b style="margin-left:8pt">Total bars = 40 + countdown =</b><span></span><b>bars</b></div></div>')
    return D.page("Tempo table", "STUDENT", "Class 1", inner, n, wm, name=True, key="tempo")


def map_page(n, wm=False):
    sb = {b: sec_bars(b) for b in CHOICES}
    rows = ""
    for i, nm in enumerate(SEC_NAMES):
        if i == 2:
            bars = "4, 5 or 6"
        else:
            bars = str(sb[96][i])
        rows += (f"<tr><td class='l'>{nm}</td><td>{bars}</td>" + "".join(f"<td>{start_bar(b, i)}</td>" for b in CHOICES) + "</tr>")
    rows += "<tr><td class='l'>Total</td><td>40 + countdown</td>" + "".join(f"<td><b>{total_bars(b)}</b></td>" for b in CHOICES) + "</tr>"
    mine = "".join(f"<tr><td class='l' style='height:22pt'>{nm}</td><td></td><td></td><td></td><td></td><td></td></tr>" for nm in SEC_NAMES)
    inner = (CSS_SG +
             f'<p style="margin:0 0 4pt;font-size:10.2pt;line-height:1.36">Step 1: choose tempo and map. Your track has five sections: an intro (8 bars), a build-up (8 bars), the countdown (4, 5 or 6 bars), '
             f'a drop (16 bars) and an outro (8 bars), which is 44, 45 or 46 bars in all. The map shows which elements play in each section.</p>'
             f'<div style="margin:0 0 3pt">{D.body_svg(map_body(1500, False, "map page", 23, 38))}</div>'
             f'<table class="sg" style="margin-top:3pt"><tr><th style="width:1.45in">Section</th><th>Bars</th><th>Starts at bar, 96 BPM</th><th>120 BPM</th><th>144 BPM</th></tr>{rows}</table>'
             f'<p class="small" style="margin:2pt 0 3pt;font-size:8.6pt">The elements playing in the five sections are {", ".join(str(c) for c in ELEM_PLAYING)}, which add up to {sum(ELEM_PLAYING)}. '
             f'The countdown has fewer elements than the build-up, so the drop feels bigger when the kick, bass and hi-hat return.</p>'
             f'<span class="k" style="margin-top:3pt">My map: my tempo and the numbers for each section</span>'
             f'<table class="sg" style="margin-top:2pt"><tr><th style="width:1.45in">Section</th><th>Bars</th><th>Starts at bar</th><th>Ends at bar</th><th>Starts at (s)</th><th>Lasts (s)</th></tr>{mine}</table>'
             f'<div class="fl" style="margin:4pt 0 3pt;font-size:10pt"><b>My tempo:</b><span></span><b>Countdown bars:</b><span></span><b>Total bars:</b><span></span></div>'
             f'<p class="small" style="margin:0;font-size:8.6pt">Check: your sections add up to between 44 and 46 bars, and the drop starts 10 seconds after the countdown does.</p>')
    return D.page("Section map", "STUDENT", "Class 1", inner, n, wm, name=True, key="map")


def ladder_rows():
    rows = []
    for k, (nv, nm, h) in enumerate(LADDER):
        a, b = ladder_bars(k)
        rows.append(f"<tr><td><b>{nv}</b></td><td>{nm}</td><td>{h}</td><td>{h * 4}</td>" + "".join(f"<td>{num(gap_ms(bpm, h))}</td>" for bpm in CHOICES)
                    + f"<td>{a}–{b}</td><td>{h * 4 * LADDER_BARS}</td></tr>")
    return "".join(rows)


def ladder_page(n, wm=False):
    def box(title, items, acc=False):
        return (f'<div class="box{" acc-b" if acc else ""}" style="padding:4pt 9pt"><span class="k">{title}</span>'
                + "".join(D.chk(c, 11, "font-size:9.6pt;line-height:1.28;margin-bottom:2pt") for c in items) + '</div>')
    inner = (CSS_CC +
             f'<p style="margin:0 0 3pt;font-size:10.2pt;line-height:1.36">Step 2: plan the build. A snare roll speeds up in steps. The time between hits is 60000 ÷ (BPM × hits per beat) milliseconds, so each rung '
             f'doubles the hits and halves the gap. Spend two bars on each rung across the 8 bars of the build-up, bars 9 to 16.</p>'
             f'<div style="width:6.1in;margin:0 auto 2pt">{D.body_svg(ladder_body(1400, "ladder page"))}</div>'
             f'<table class="t cc" style="margin-top:2pt"><tr><th>Note</th><th>Name</th><th>Hits per beat</th><th>Hits per bar</th><th>Gap at 96 BPM (ms)</th><th>120 BPM</th><th>144 BPM</th><th>Bars (build-up)</th><th>Hits in 2 bars</th></tr>{ladder_rows()}</table>'
             f'<p class="small" style="margin:1pt 0 3pt;font-size:8.6pt">Gaps are in milliseconds, rounded half up to 2 decimals. Across the four rungs the roll has {sum(h * 4 * LADDER_BARS for _, _, h in LADDER)} hits.</p>'
             f'<div class="cols" style="gap:9pt;align-items:flex-start"><div>'
             + box("Riser checklist", ["I made a riser from a rising synth or noise sound (Alchemy or Retro Synth), or a reversed cymbal (a Reverse effect, if my version has it).",
                                       "It starts quiet at bar 9 and gets louder and brighter.", "It reaches its top by bar 17, holds through the countdown and stops on the drop."], True)
             + '</div><div>'
             + box("Automation checklist", ["The low-pass cutoff rises from low to open across bars 9 to 17 (instrument filter, Channel EQ or Auto Filter, if my version has it).",
                                            "The riser’s pitch climbs, for example 12 semitones, by bar 17, if its instrument has a pitch control.",
                                            "Volume swells, and the filter stays open on the drop."])
             + '</div></div>'
             f'<span class="k" style="margin-top:4pt">My plan: a sound for each element</span>'
             f'<table class="map" style="margin-bottom:0"><tr><th style="width:24%">Element</th><th style="width:34%">Instrument or sound source</th><th>My idea</th></tr>'
             + "".join(f"<tr><td style='height:17pt;font-size:9.6pt'><b>{el}</b></td><td></td><td></td></tr>" for el in ("Riser", "Snare roll", "Filter sweep", "Countdown voice", "Drop and impact"))
             + '</table>')
    return D.page("Snare-roll ladder, risers and automation", "STUDENT", "Classes 1–2", inner, n, wm, name=True, key="ladder")


def cue_rows():
    rows = []
    for s in range(CD_SECONDS + 1):
        word = "DROP" if s == CD_SECONDS else str(number_at(s))
        cells = ""
        for bpm in CHOICES:
            bar, beat = cue_pos(bpm, s)
            cells += f"<td>{bar}</td><td>{fmt(beat)}</td>"
        cls = ' class="hi"' if s in (0, CD_SECONDS) else ""
        rows.append(f"<tr{cls}><td>{s}</td><td><b>{word}</b></td>{cells}</tr>")
    return "".join(rows)


def cues_page(n, wm=False):
    mine = "".join(f"<tr><td>{s}</td><td><b>{'DROP' if s == CD_SECONDS else number_at(s)}</b></td><td style='height:17pt'></td><td></td><td></td></tr>" for s in range(CD_SECONDS + 1))
    inner = (CSS_CC +
             f'<p style="margin:0 0 3pt;font-size:10.2pt;line-height:1.36">Step 5: countdown and drop. The number 10 is said on second 0 of the countdown, which starts on bar 17 beat 1, and the number 1 on second 9. '
             f'The drop is on second 10, the first beat of the drop section. The table gives the bar and beat of every cue.</p>'
             f'<div class="box acc-b" style="padding:4pt 9pt"><span class="k">How to find a cue at your tempo</span>'
             f'<p style="margin:0 0 1pt;font-size:9.6pt"><b>Beats from the start of the countdown</b> = second × BPM ÷ 60. <b>Bar</b> = 17 + the whole bars in (beats ÷ 4). <b>Beat</b> = 1 + the beats left over.</p>'
             f'<p style="margin:0;font-size:9.6pt"><b>Example:</b> 96 BPM, second 3: 3 × 96 ÷ 60 = 4.8 beats, which is 1 whole bar and 0.8 beat, so bar 18, beat 1.8. A beat of 1.8 is 80% of the way from beat 1 to beat 2.</p></div>'
             f'<span class="k" style="margin-top:4pt">The cue sheet at the three tempos</span>'
             f'<table class="t cc" style="margin-top:1pt"><tr><th rowspan="2">Second</th><th rowspan="2">You say</th><th colspan="2">96 BPM</th><th colspan="2">120 BPM</th><th colspan="2">144 BPM</th></tr>'
             f'<tr><th>Bar</th><th>Beat</th><th>Bar</th><th>Beat</th><th>Bar</th><th>Beat</th></tr>{cue_rows()}</table>'
             f'<p class="small" style="margin:1pt 0 3pt;font-size:8.6pt">At 120 BPM every number lands exactly on a beat. At 96 and 144 BPM most numbers fall between beats, so drag the region with the snap set to a small value and check its position. '
             f'The drop is on bar {start_bar(96, 3)} at 96 BPM, bar {start_bar(120, 3)} at 120 BPM and bar {start_bar(144, 3)} at 144 BPM, always on beat 1.</p>'
             f'<span class="k" style="margin-top:3pt">My cue sheet (my tempo: ________ BPM)</span>'
             f'<table class="t cc" style="margin-top:1pt"><tr><th>Second</th><th>You say</th><th>Beats = second × BPM ÷ 60</th><th>My bar</th><th>My beat</th></tr>{mine}</table>')
    return D.page("Countdown cue sheet", "STUDENT", "Classes 1–3", inner, n, wm, name=True, key="cues")


def mix_page(n, wm=False):
    def box(title, items, acc=False):
        return (f'<div class="box{" acc-b" if acc else ""}" style="padding:5pt 9pt"><span class="k">{title}</span>'
                + "".join(D.chk(c, 11, "font-size:10pt;line-height:1.3;margin-bottom:3pt") for c in items) + '</div>')
    inner = (f'<p style="margin:0 0 5pt;font-size:10.2pt;line-height:1.36">Step 6: mix and bounce. A mix makes the build-up grow, the countdown clear and the drop big. Work through the boxes with headphones, '
             f'then check each one off.</p>'
             f'<div class="cols" style="gap:10pt;align-items:flex-start"><div>'
             + box("Build-up (bars 9 to 16)", ["The riser starts quiet and swells; it is never louder than the drums.", "The snare roll grows louder as it speeds up.",
                                               "The filter opens and the pitch climbs without a sudden jump."], True)
             + '<div style="height:6pt"></div>'
             + box("Countdown (bars 17 on)", ["I can hear every number clearly over the riser.", "The kick, bass and hi-hat have stopped, so the sound feels empty.",
                                              "The numbers sit on the cue sheet’s bars and beats."])
             + '</div><div>'
             + box("Drop and outro", ["The drop is on the first beat after 1, with an impact or crash.", "The drop is the loudest, widest part of the track.",
                                      "The riser and the countdown stop before the drop starts."], True)
             + '<div style="height:6pt"></div>'
             + box("Low end and levels", ["The kick and the bass do not cover each other.", "I cut the low notes from the riser and the voice (Channel EQ, if I like).",
                                          "The master level never reaches red (no clipping)."])
             + '</div></div>'
             f'<div class="box" style="margin-top:6pt;padding:5pt 9pt"><span class="k">The listening test</span><p style="margin:0 0 3pt;font-size:10pt;line-height:1.36">Play from bar 9 with your eyes closed and '
             f'rate each part from 1 (flat) to 5 (very strong). Is the tension rising? Is the countdown steady? Does the drop feel bigger than anything before it? Write what you hear:</p>'
             f'<div class="fl" style="margin:2pt 0;font-size:10pt"><b>Build-up:</b><span></span><b>Countdown:</b><span></span><b>Drop:</b><span></span></div></div>'
             f'<div class="box acc-b" style="margin-top:6pt;padding:5pt 9pt"><span class="k">Bounce</span>'
             + "".join(D.chk(c, 11, "font-size:10pt;margin-bottom:3pt") for c in [
                 "The bounce starts at bar 1 and ends after the last bar of the outro (about " + dec(total_s(EX_BPM), 0) + " seconds at 120 BPM; check your own tempo on page " + str(pg("tempo")) + ").",
                 "MP3 or WAV bounced, and the .logicx project zipped.", f"Both files named {FILE_NAME}."]) + '</div>'
             f'<span class="k" style="margin-top:6pt">What I changed after the listening test</span>' + D.lines(7, 24))
    return D.page("Mix checklist", "STUDENT", "Class 3", inner, n, wm, name=True, key="mix")


# ================================================================ worked example (2 pages)
def ex_rows():
    out = []
    for i, nm in enumerate(SEC_NAMES):
        sb = sec_bars(EX_BPM)[i]
        a = start_bar(EX_BPM, i)
        out.append(f"<tr><td style='text-align:left'><b>{nm}</b></td><td>{a}–{a + sb - 1}</td><td>{sb}</td><td>{fmt(start_s(EX_BPM, i))}</td><td>{fmt(start_s(EX_BPM, i + 1))}</td>"
                   f"<td style='text-align:left'>{EX_SEC_NOTES[i]}</td></tr>")
    return "".join(out)


EX_SEC_NOTES = ["Pad and a soft kick and hi-hat set the D minor mood", "Riser, snare roll, filter sweep and pitch-up; the hi-hat gets busier",
                "Only the riser, the pad and the voice; the numbers 10 to 1", "Full beat, bass, lead and impact on bar 22", "Layers drop away and the pad fades"]


def ex_cue_rows():
    out = []
    for s in range(CD_SECONDS + 1):
        bar, beat = cue_pos(EX_BPM, s)
        word = "DROP" if s == CD_SECONDS else str(number_at(s))
        out.append(f"<tr><td>{s}</td><td><b>{word}</b></td><td>{cue_beats(EX_BPM, s)}</td><td>{bar}</td><td>{fmt(beat)}</td><td>{fmt(start_s(EX_BPM, 2) + s)}</td></tr>")
    return "".join(out)


def ex_compare_rows():
    out = []
    for bpm in CHOICES:
        b, e = ("<b>", "</b>") if bpm == EX_BPM else ("", "")
        bar, beat = cue_pos(bpm, 5)
        out.append(f"<tr><td>{b}{bpm}{e}</td><td>{dec(bar_len(bpm), 3)}</td><td>{sec_bars(bpm)[2]}</td><td>{total_bars(bpm)}</td><td>{dec(total_s(bpm), 2)}</td><td>{start_bar(bpm, 3)}</td><td>{dec(start_s(bpm, 3), 2)}</td></tr>")
    return "".join(out)


def example_page(n, wm=False):
    inner = (f'<style>table.ec td {{ text-align: center; }}</style>'
             f'<p style="margin:0 0 4pt;font-size:10pt">An <b>invented plan on paper</b>: a track in {EX_KEY} at {EX_BPM} BPM. No audio is included. '
             f'Student projects will differ. Page 1 of 2: the plan, the sections and the countdown cues.</p>'
             f'<div class="cols" style="gap:10pt;align-items:flex-start"><div class="box"><span class="k">1 · A weak plan</span><p style="margin:0;font-size:10.2pt">{EX_WEAK}</p>'
             f'<p style="margin:3pt 0 0;font-size:9.2pt">It names no tempo, no sections, no countdown length and no times.</p></div>'
             f'<div class="box acc-b"><span class="k">2 · A clear plan</span><p style="margin:0;font-size:8.6pt;line-height:1.28">{EX_STRONG}</p></div></div>'
             f'{D.H2("3 · The five sections at 120 BPM")}'
             f'<table class="t ec" style="font-size:9pt;line-height:1.2"><tr><th>Section</th><th>Bars</th><th>Length (bars)</th><th>Starts (s)</th><th>Ends (s)</th><th>What happens</th></tr>{ex_rows()}</table>'
             f'<p style="margin:2pt 0 0;font-size:9pt">One beat lasts 60 ÷ {EX_BPM} = {dec(spb(EX_BPM), 3)} s and one bar lasts 240 ÷ {EX_BPM} = {fmt(EX_BAR_S)} s. The countdown lasts 10 ÷ {fmt(EX_BAR_S)} = {EX_C} bars, '
             f'and {EX_BPM} ÷ 24 = {EX_C} too. The track has 8 + 8 + {EX_C} + 16 + 8 = {total_bars(EX_BPM)} bars, which last {total_bars(EX_BPM)} × {fmt(EX_BAR_S)} = {fmt(total_s(EX_BPM))} seconds.</p>'
             f'{D.H2("4 · The countdown cue sheet at 120 BPM")}'
             f'<table class="t ec" style="font-size:8.8pt;line-height:1.12"><tr><th>Second</th><th>You say</th><th>Beats from countdown start</th><th>Bar</th><th>Beat</th><th>Seconds from track start</th></tr>{ex_cue_rows()}</table>'
             f'<p style="margin:2pt 0 0;font-size:8.8pt;line-height:1.3">Every cue is on a beat because there are {fmt(cue_beats(EX_BPM, 1))} beats in each second at {EX_BPM} BPM. The number 10 is on bar 17 beat 1 and the number 1 is on bar 21 beat 3. '
             f'The drop is on bar 22 beat 1, which is 32 + 10 = 42 seconds into the track.</p>')
    return D.page("Worked example · the plan, the sections and the cues", "EXAMPLE", "Teacher", inner, n, wm, ak=True, key="example")


def example2_page(n, wm=False):
    qs = " ".join(f"{i + 1}. {q}" for i, q in enumerate(EX_QUESTIONS))
    ladder_txt = "; ".join(f"{nv} on bars {ladder_bars(k)[0]}–{ladder_bars(k)[1]} ({num(gap_ms(EX_BPM, h))} ms apart)" for k, (nv, _, h) in enumerate(LADDER))
    sw = ", ".join(f"{hz:,} Hz at bar {b}" for b, hz in EX_SWEEP)
    inner = (f'<p style="margin:0 0 3pt;font-size:10pt">The same track, page 2 of 2: the map of the whole track, the tension tools, then the numbers.</p>'
             f'{D.H2("5 · The map: 45 bars, 5 sections, 10 elements")}'
             f'<div style="width:5.4in;margin:1pt auto 3pt">{D.body_svg(map_body(1500, True, "exmap page", 23, 38))}</div>'
             f'<div class="cols" style="gap:10pt;align-items:flex-start"><div style="width:4.1in;flex:0 0 4.1in">{D.H2("6 · The filter sweep and pitch-up")}'
             f'<div style="margin:1pt 0 0">{D.body_svg(sweep_body(1200, "sweep page"))}</div></div>'
             f'<div class="box acc-b" style="margin-top:6pt;flex:1"><span class="k">7 · Checking the numbers</span><p style="margin:0;font-size:9.6pt;line-height:1.34">'
             f'The snare ladder: {ladder_txt}; that is {sum(h * 4 * LADDER_BARS for _, _, h in LADDER)} hits in 8 bars. The sweep: {sw}. The pitch climbs {EX_PITCH_ST} semitones, one octave, so its frequency doubles. '
             f'At {EX_BPM} BPM one bar is {fmt(EX_BAR_S)} s, so {total_bars(EX_BPM)} bars = {fmt(total_s(EX_BPM))} s, and 8 + 8 + {EX_C} + 16 bars = {8 + 8 + EX_C + 16} bars gone by before the outro, which starts at {fmt(start_s(EX_BPM, 4))} s.</p></div></div>'
             f'<div class="box" style="margin-top:5pt"><span class="k">8 · The automation</span><p style="margin:0;font-size:10pt;line-height:1.36">{EX_AUTO}.</p></div>'
             f'<div class="box" style="margin-top:5pt"><span class="k">9 · Three feedback questions (invented)</span><p style="margin:0;font-size:10pt;line-height:1.36">{qs}</p></div>'
             f'<div class="box acc-b" style="margin-top:5pt"><span class="k">10 · Moments to point out in class</span><ul style="margin:0">'
             f'<li style="font-size:10pt;margin-bottom:2pt">The kick, bass and hi-hat stop at bar 17, so the countdown is the emptiest moment, and that makes the drop on bar 22 feel biggest.</li>'
             f'<li style="font-size:10pt;margin-bottom:0">Both the cutoff and the pitch reach their top at bar 17 and hold there; at 120 BPM the numbers fall on beats 1 and 3, so the class can count along.</li></ul></div>')
    return D.page("Worked example · the map, the tools and the numbers", "EXAMPLE", "Teacher", inner, n, wm, ak=True, key="example2")


PAGES = {"howto": howto_page, "overview": overview_page, "setup": setup_page, "example": example_page, "example2": example2_page,
         "tempo": tempo_page, "map": map_page, "ladder": ladder_page, "cues": cues_page, "mix": mix_page}


# ================================================================ content checks
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


BADGE = {"tempo": "Class 1", "map": "Class 1", "ladder": "Classes 1–2", "cues": "Classes 1–3", "mix": "Class 3", "present": f"Classes {CLASSES - 1}–{CLASSES}"}
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



def float_cue(bpm, s):
    """An independent float check of one cue: (bar, beat) of second s of the countdown, from beats = s x BPM / 60."""
    beats = s * bpm / 60
    whole = math.floor(beats / 4 + 1e-9)
    return CD_START_BAR + whole, 1 + beats - 4 * whole


FORBIDDEN_WORDS = ("cham" + "pagne", "toast", "cheers", "wine", "beer", "cocktail", "drink", "alcohol", "bub" + "bly", "church", "prayer", "pray ", "blessing", "holy", "sacred",
                   "religio", "god ", "santa", "christmas", "hanukkah", "chanukah", "kwanzaa", "resolution")


def verify_content():
    errs = []
    counts = dict(goals=(GOALS, 4), vocab=(VOCAB, 5), reqs=(REQS, 7), steps=(STEPS, 7), tips=(TIPS, 4), check=(CHECK, 6),
                  rubric=(RUBRIC, 5), struggles=(STRUGGLES, 4), resources=(RESOURCES, 4), slides=(SLIDES, 14), plan=(PLAN, 23),
                  logic=(LOGIC_REF, 9), elements=(ELEMENTS, 10), ladder=(LADDER, 4))
    for nm, (lst, nexp) in counts.items():
        if len(lst) != nexp:
            errs.append(f"{nm}: {len(lst)} items, expected {nexp}")
    if RUBRIC_TOTAL != 25 or LEVELS != [1, 2, 3, 4, 5] or len(RUBRIC_SHORT) != 5:
        errs.append("rubric is /25, levels 1-5")
    if FILE_NAME not in CHECK[2]:
        errs.append("file name format must be on the checklist")
    if set(TAGS) & {"Holiday", "Student Practice", "Theme", "Seasonal"} or "Performing Arts" in SUBJECTS:
        errs.append("tags and subjects must not be headings")
    if len(LISTING_TITLE) > 80 or "Logic Pro" not in LISTING_TITLE[:30]:
        errs.append("listing title: at most 80 characters, 'Logic Pro' in the first 30")
    for w in ("new year", "winter", "holiday", "christmas", "hanukkah", "chanukah", "sleigh", "carol", "snow", "eve "):
        if w in LISTING_TITLE.lower():
            errs.append(f"the listing title must not hold the seasonal word {w}")
    if len(STEP_NAMES) != len(STEPS) or any(not s.startswith(f"<b>{nm}</b>") for s, nm in zip(STEPS, STEP_NAMES)):
        errs.append("STEPS must start with the bold names in STEP_NAMES (the pages cite them)")
    # ---- the arithmetic, by hand first
    if [spb(b) for b in (120, 96, 100, 144)] != [Fraction(1, 2), Fraction(5, 8), Fraction(3, 5), Fraction(5, 12)]:
        errs.append("seconds per beat = 60 / BPM: 0.5 at 120, 0.625 at 96, 0.6 at 100, 0.4167 at 144")
    if [bar_len(b) for b in (96, 120, 144, 100)] != [Fraction(5, 2), 2, Fraction(5, 3), Fraction(12, 5)]:
        errs.append("seconds per bar = 240 / BPM: 2.5 at 96, 2 at 120, 1.6667 at 144, 2.4 at 100")
    if any(bar_len(b) != 4 * spb(b) for b in TEMPOS):
        errs.append("a bar of 4/4 is four beats")
    if [cd_bars(b) for b in CHOICES] != [4, 5, 6] or [cd_bars(b) for b in (100, 110, 128, 90)] != [Fraction(25, 6), Fraction(55, 12), Fraction(16, 3), Fraction(15, 4)]:
        errs.append("bars in 10 seconds = BPM / 24: 4, 5, 6 at 96, 120, 144; 4.1667 at 100, 4.5833 at 110, 5.3333 at 128, 3.75 at 90")
    for b in TEMPOS:
        if abs(float(cd_bars(b)) - 10 / (240 / b)) > 1e-9 or cd_bars(b) != Fraction(b, 24):
            errs.append(f"bars in 10 seconds at {b} BPM")
    if [b for b in TEMPOS if is_whole(b)] != [96, 120, 144]:
        errs.append("10 seconds is a whole number of bars only at 96, 120 and 144 BPM in the table")
    for bars in range(1, 12):
        if cd_bars(24 * bars) != bars or not is_whole(24 * bars) or is_whole(24 * bars + 1):
            errs.append(f"tempo = 24 x bars fails for {bars} bars")
    if [dec(spb(b), 3) for b in TEMPOS] != ["0.667", "0.625", "0.600", "0.545", "0.500", "0.469", "0.417"] or \
       [dec(bar_len(b), 3) for b in TEMPOS] != ["2.667", "2.500", "2.400", "2.182", "2.000", "1.875", "1.667"]:
        errs.append("seconds per beat and per bar to 3 decimals")
    if [dec(cd_bars(b), 4) for b in TEMPOS] != ["3.7500", "4.0000", "4.1667", "4.5833", "5.0000", "5.3333", "6.0000"]:
        errs.append("bars in 10 seconds to 4 decimals")
    # ---- the section map
    for b in CHOICES:
        sb = sec_bars(b)
        if sb != [8, 8, int(cd_bars(b)), 16, 8] or total_bars(b) != 40 + int(cd_bars(b)) or not 40 <= total_bars(b) <= 48:
            errs.append(f"sections at {b} BPM must be 8 + 8 + C + 16 + 8 = 40 + C bars, between 40 and 48")
        if [start_bar(b, i) for i in range(3)] != [1, 9, 17]:
            errs.append("the intro, build-up and countdown start at bars 1, 9 and 17 at every tempo")
        if start_bar(b, 3) != 17 + int(cd_bars(b)) or start_bar(b, 4) != 33 + int(cd_bars(b)):
            errs.append(f"drop and outro start bars at {b} BPM")
        if start_s(b, 3) - start_s(b, 2) != CD_SECONDS:
            errs.append(f"the drop must start exactly 10 seconds after the countdown at {b} BPM")
        for i in range(6):
            if abs(float(start_s(b, i)) - sum(sec_bars(b)[:i]) * 240 / b) > 1e-9:
                errs.append(f"section {i} start at {b} BPM: float check fails")
        if start_s(b, 5) != total_s(b) or total_s(b) != Fraction(total_bars(b) * 240, b):
            errs.append(f"total seconds at {b} BPM")
    if [total_bars(b) for b in CHOICES] != [44, 45, 46] or [dec(total_s(b), 2) for b in CHOICES] != ["110.00", "90.00", "76.67"]:
        errs.append("totals: 44, 45, 46 bars; 110, 90, 76.67 seconds at 96, 120, 144 BPM")
    if [dec(start_s(144, i), 2) for i in range(1, 5)] != ["13.33", "26.67", "36.67", "63.33"] or [dec(start_s(96, i), 2) for i in range(1, 5)] != ["20.00", "40.00", "50.00", "90.00"] \
            or [dec(start_s(120, i), 2) for i in range(1, 5)] != ["16.00", "32.00", "42.00", "74.00"]:
        errs.append("section starts in seconds at 96, 120 and 144 BPM")
    if rnd(Fraction(5, 2), 0) != 3 or dec(Fraction(125, 1600), 3) != "0.078" or dec(Fraction(15, 8), 3) != "1.875" or dec(Fraction(80, 3), 2) != "26.67":
        errs.append("round half up")
    # ---- the cue sheet
    for b in CHOICES:
        for s in range(CD_SECONDS + 1):
            bar, beat = cue_pos(b, s)
            fb, fe = float_cue(b, s)
            if bar != fb or abs(float(beat) - fe) > 1e-9:
                errs.append(f"cue at {b} BPM second {s}: exact {bar, beat}, float {fb, fe}")
            if not 1 <= beat < 5:
                errs.append(f"cue beat out of the bar at {b} BPM second {s}")
            # the clock time of the cue: ((bar - 1) x 4 + (beat - 1)) x 60 / BPM = start of the countdown + s
            if ((bar - 1) * 4 + (beat - 1)) * Fraction(60, b) != start_s(b, 2) + s:
                errs.append(f"cue at {b} BPM second {s} is not {s} seconds after the countdown starts")
        if cue_pos(b, CD_SECONDS) != (start_bar(b, 3), 1):
            errs.append(f"the drop (second 10) must be bar {start_bar(b, 3)} beat 1 at {b} BPM")
        if cue_pos(b, 0) != (17, 1):
            errs.append("the number 10 must be on bar 17 beat 1")
    if [number_at(s) for s in range(10)] != [10, 9, 8, 7, 6, 5, 4, 3, 2, 1]:
        errs.append("the numbers are 10 down to 1, one per second")
    if [cue_pos(120, s) for s in range(11)] != [(17, 1), (17, 3), (18, 1), (18, 3), (19, 1), (19, 3), (20, 1), (20, 3), (21, 1), (21, 3), (22, 1)]:
        errs.append("at 120 BPM every cue is on a beat: 17.1, 17.3, 18.1 ... 21.3, drop 22.1")
    if [(b, fmt(x)) for b, x in (cue_pos(96, 3), cue_pos(144, 1), cue_pos(96, 1))] != [(18, "1.8"), (17, "3.4"), (17, "2.6")]:
        errs.append("cue examples: 96 BPM second 3 = bar 18 beat 1.8; 144 BPM second 1 = bar 17 beat 3.4; 96 BPM second 1 = bar 17 beat 2.6")
    # ---- the snare-roll ladder
    if [h for _, _, h in LADDER] != [1, 2, 4, 8] or [nv for nv, _, _ in LADDER] != ["1/4", "1/8", "1/16", "1/32"]:
        errs.append("the ladder: 1/4, 1/8, 1/16, 1/32 with 1, 2, 4, 8 hits per beat")
    if [num(gap_ms(120, h)) for _, _, h in LADDER] != ["500", "250", "125", "62.5"]:
        errs.append("gaps at 120 BPM: 500, 250, 125, 62.5 ms")
    if [num(gap_ms(96, h)) for _, _, h in LADDER] != ["625", "312.5", "156.25", "78.13"] or [num(gap_ms(144, h)) for _, _, h in LADDER] != ["416.67", "208.33", "104.17", "52.08"]:
        errs.append("gaps at 96 and 144 BPM")
    for b in CHOICES:
        for _, _, h in LADDER:
            if gap_ms(b, h) * h * b != 60000 or abs(float(gap_ms(b, h)) - 60000 / (b * h)) > 1e-9 or gap_ms(b, h) * h != spb(b) * 1000:
                errs.append(f"gap at {b} BPM with {h} hits per beat")
    if [ladder_bars(i) for i in range(4)] != [(9, 10), (11, 12), (13, 14), (15, 16)] or ladder_bars(3)[1] != start_bar(120, 2) - 1:
        errs.append("the ladder fills bars 9 to 16, two bars a rung")
    if sum(h * 4 * LADDER_BARS for _, _, h in LADDER) != 120:
        errs.append("hits in the ladder: 8 + 16 + 32 + 64 = 120")
    # ---- the sweep and the pitch-up
    hz = [h for _, h in EX_SWEEP]
    bars = [b for b, _ in EX_SWEEP]
    if hz != sorted(hz) or len(set(hz)) != len(hz) or bars != sorted(bars) or bars[0] != 9 or bars[-1] != CD_START_BAR or hz[0] != 200 or hz[-1] != 12000:
        errs.append("the example sweep rises from 200 Hz at bar 9 to 12,000 Hz at bar 17")
    if abs(2 ** (EX_PITCH_ST / 12) - 2) > 1e-12:
        errs.append("12 semitones is one octave: the frequency doubles")
    # ---- the map: which elements play where
    if len(ELEMENTS) != 10 or any(len(c) != 5 for _, c in ELEMENTS) or ELEM_PLAYING != [3, 6, 4, 7, 4] or sum(ELEM_PLAYING) != 24:
        errs.append("the map: 10 elements x 5 sections; 3, 6, 4, 7 and 4 playing (24 in all)")
    if ELEM_PLAYING[3] != max(ELEM_PLAYING) or ELEM_PLAYING[2] >= ELEM_PLAYING[1]:
        errs.append("the drop has the most elements and the countdown fewer than the build-up")
    cells = dict(ELEMENTS)
    if [bool(c) for c in cells["Countdown voice"]] != [False, False, True, False, False] or [bool(c) for c in cells["Snare roll"]] != [False, True, False, False, False] \
            or [bool(c) for c in cells["Impact and crash"]] != [False, False, False, True, False] or [bool(c) for c in cells["Riser"]] != [False, True, True, False, False]:
        errs.append("the voice plays only in the countdown, the roll only in the build-up, the impact only on the drop, the riser in the build-up and the countdown")
    if any(cells[e][2] for e in ("Kick", "Bass", "Hi-hat or shaker")):
        errs.append("kick, bass and hi-hat stop in the countdown")
    # ---- Logic wording: newer tools are hedged
    for nm, txt in LOGIC_REF:
        if any(w in txt for w in ("Step Sequencer", "Auto Filter", "Reverse", "Channel EQ", "Scale Quantize")) and "if your version" not in txt.lower():
            errs.append(f"Logic reference '{nm}' must hedge a newer tool with 'if your version'")
    for w in ("Alchemy", "Retro Synth", "Quick Sampler", "Drum Machine Designer", "Channel EQ", "Reverse", "Step Sequencer", "Auto Filter", "Marker"):
        if w not in " ".join(t for _, t in LOGIC_REF):
            errs.append(f"the Logic quick reference must name {w}")
    # ---- the worked example
    if EX_BPM != 120 or EX_BAR_S != 2 or EX_C != 5 or total_bars(EX_BPM) != 45 or total_s(EX_BPM) != 90 or start_s(EX_BPM, 3) != 42:
        errs.append("the example: 120 BPM, 2 s per bar, 5 countdown bars, 45 bars, 90 s, drop at 42 s")
    for need in ("120 BPM", "240 ÷ 120 = 2 seconds", "exactly 5 bars", "8 + 8 + 5 + 16 + 8 = 45 bars", "90 seconds", "bar 22", "42 seconds", "bar 17 beat 1", "bar 22 beat 1", "200 Hz to 12,000 Hz"):
        if need not in EX_STRONG:
            errs.append(f"the clear plan must say '{need}'")
    # ---- no forbidden themes in any text a buyer reads
    allt = " ".join([THEME, BUILD_NOTE, OVERVIEW, " ".join(GOALS), " ".join(f"{a} {b}" for a, b in VOCAB), " ".join(REQS), " ".join(STEPS), " ".join(TIPS), " ".join(CHECK),
                     " ".join(d for _, ds in RUBRIC for d in ds), TN_REINFORCES, " ".join(STRUGGLES), VAR_EASY, VAR_HARD, " ".join(f"{a} {b}" for a, b in RESOURCES), TN_NOTE,
                     " ".join(GRADING), " ".join(d["do"] for d in PACING), SONG_NOTE, VOICE_NOTE, " ".join(t for _, t in LOGIC_REF), EX_STRONG, EX_AUTO, " ".join(EX_QUESTIONS),
                     " ".join(" ".join((s[2], s[3], s[4])) for s in SLIDES), " ".join(" ".join(c) for _, c in ELEMENTS)]).lower()
    for w in FORBIDDEN_WORDS:
        if re.search(rf"\b{re.escape(w.strip())}\b", allt):
            errs.append(f"no alcohol, religious or seasonal-holiday wording in a neutral kit: '{w.strip()}'")
    for w in ("colour", "favour", "centre", "licence", "grey", "metre ", "organis", "recognis", "practise", "analyse", "whilst", "milli-second"):
        if w in allt:
            errs.append(f"US spelling: '{w}'")
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
    for need, key in ((f"page {pg('map')}", 4), (f"page {pg('logicref')}", 4), (f"page {pg('tempo')}", 5), (f"page {pg('ladder')}", 6), (f"page {pg('ladder')}", 7),
                      (f"page {pg('logicref')}", 8), (f"page {pg('cues')}", 9), (f"pages {pg('example')} and {pg('example2')}", 9)):
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
    for need in ("No audio, recordings, lyrics or melodies", "invented plan on paper", "Drum Machine Designer", "Quick Sampler", "Alchemy", "Retro Synth", "Channel EQ", "Reverse",
                 "Marker", "60 ÷ BPM", "240 ÷ BPM", "BPM ÷ 24", "Tempo = 24 × bars", "if your version", "snare roll", "filter sweep", "riser", "10-second",
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
    for w in ("colour", "favour", "centre", "licence", "grey", "metre", "organis", "recognis", "practise", "analyse", "whilst", "milli-second", "colourful"):
        if w in txt.lower().replace("greyscale", ""):
            errs.append(f"US spelling: '{w}' in the PDF")
    # ---- Step N on every page, in the deck PDF text, the deck notes and UPLOAD.md agrees with the project sheet
    expect = {"tempo": {1}, "map": {1}, "ladder": {2}, "cues": {5}, "mix": {6}}
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
        w = is_whole(bpm)
        row = f"{bpm} {dec(spb(bpm), 3)} {dec(bar_len(bpm), 3)} {fmt(cd_bars(bpm)) if w else dec(cd_bars(bpm), 4)} {'Yes' if w else 'No'}"
        if row not in rc:
            errs.append(f"tempo page: row '{row}' is not printed")
    for bpm in CHOICES:
        row = (f"{bpm} {sec_bars(bpm)[2]} {start_bar(bpm, 3)} {start_bar(bpm, 4)} {total_bars(bpm)} {dec(total_s(bpm), 2)} "
               + " ".join(dec(start_s(bpm, i), 2) for i in (1, 2, 3, 4)))
        if row not in rc:
            errs.append(f"tempo page: section row '{row}' is not printed")
    for need in ("Seconds per beat = 60 ÷ BPM", "Seconds per bar = 240 ÷ BPM", "Bars in 10 seconds = 10 ÷ (240 ÷ BPM) = BPM ÷ 24", "Tempo = 24 × bars", "240 ÷ 120 = 2 s per bar",
                 "10 ÷ 2 = 5 bars", "120 ÷ 24 = 5 too", "Step 1: choose tempo and map", "5 rounds up", "26.67", "4.1667"):
        if need not in rc:
            errs.append(f"tempo page must say '{need}'")
    # ---- the section map page
    rm = raw("map")
    for need in ("Step 1: choose tempo and map", "3, 6, 4, 7, 4", "add up to 24", "44, 45 or 46 bars"):
        if need not in rm:
            errs.append(f"section map page must say '{need}'")
    for i, nm in enumerate(SEC_NAMES):
        row = f"{nm} " + ("4, 5 or 6" if i == 2 else str(sec_bars(96)[i])) + " " + " ".join(str(start_bar(b, i)) for b in CHOICES)
        if row not in rm:
            errs.append(f"section map page: row '{row}' is not printed")
    # ---- the ladder page
    rl = raw("ladder").replace("- ", "-")
    for k, (nv, nm, h) in enumerate(LADDER):
        a, b = ladder_bars(k)
        row = f"{nv} {nm} {h} {h * 4} " + " ".join(num(gap_ms(bpm, h)) for bpm in CHOICES) + f" {a}–{b} {h * 4 * LADDER_BARS}"
        if row not in rl:
            errs.append(f"ladder page: row '{row}' is not printed")
    for need in ("Step 2: plan the build", "60000 ÷ (BPM × hits per beat)", "the roll has 120 hits", "Riser checklist", "Automation checklist"):
        if need.lower() not in rl.lower():
            errs.append(f"ladder page must say '{need}'")
    # ---- the cue sheet page
    rq = raw("cues")
    for s in range(CD_SECONDS + 1):
        word = "DROP" if s == CD_SECONDS else str(number_at(s))
        row = f"{s} {word} " + " ".join(f"{cue_pos(b, s)[0]} {fmt(cue_pos(b, s)[1])}" for b in CHOICES)
        if row not in rq:
            errs.append(f"cue page: row '{row}' is not printed")
    for need in ("Step 5: countdown and drop", "second × BPM ÷ 60", "3 × 96 ÷ 60 = 4.8 beats", "bar 18, beat 1.8", "drop is on bar 21 at 96 BPM, bar 22 at 120 BPM and bar 23 at 144 BPM"):
        if need not in rq:
            errs.append(f"cue page must say '{need}'")
    # ---- the worked example prints its numbers
    re1 = (raw("example") + " " + raw("example2")).replace("- ", "-")
    for i, nm in enumerate(SEC_NAMES):
        sb = sec_bars(EX_BPM)[i]
        a = start_bar(EX_BPM, i)
        row = f"{nm} {a}–{a + sb - 1} {sb} {fmt(start_s(EX_BPM, i))} {fmt(start_s(EX_BPM, i + 1))} {EX_SEC_NOTES[i]}"
        if row not in re1:
            errs.append(f"worked example: section row '{row}' is not printed")
    for s in range(CD_SECONDS + 1):
        bar, beat = cue_pos(EX_BPM, s)
        word = "DROP" if s == CD_SECONDS else str(number_at(s))
        row = f"{s} {word} {cue_beats(EX_BPM, s)} {bar} {fmt(beat)} {fmt(start_s(EX_BPM, 2) + s)}"
        if row not in re1:
            errs.append(f"worked example: cue row '{row}' is not printed")
    for need in ("60 ÷ 120 = 0.500 s", "240 ÷ 120 = 2 s", "10 ÷ 2 = 5 bars", "8 + 8 + 5 + 16 + 8 = 45 bars", "45 × 2 = 90 seconds", "32 + 10 = 42 seconds",
                 "1/4 on bars 9–10 (500 ms apart); 1/8 on bars 11–12 (250 ms apart); 1/16 on bars 13–14 (125 ms apart); 1/32 on bars 15–16 (62.5 ms apart)", "120 hits in 8 bars",
                 "200 Hz at bar 9, 500 Hz at bar 11, 1,500 Hz at bar 13, 5,000 Hz at bar 15, 12,000 Hz at bar 17", "12 semitones, one octave, so its frequency doubles"):
        if need not in re1:
            errs.append(f"worked example must say '{need}'")
    for k, need in (("ladder", "Step 2: plan the build"), ("cues", "Step 5: countdown and drop"), ("mix", "Step 6: mix and bounce")):
        if need not in raw(k):
            errs.append(f"{k} page must say '{need}'")
    up = open(os.path.join(HERE, "UPLOAD.md"), encoding="utf8").read()
    errs += step_ref_errors(up, "UPLOAD.md")
    if "Grades 9-12" not in up or "`9th-grade`, `10th-grade`, `11th-grade`, `12th-grade`" not in up:
        errs.append("UPLOAD.md: grades 9-12 in the description and section 3")
    if "no audio" not in up.lower() or "Open question" not in up or "Timing numbers" not in up or "Sources and credits" not in up:
        errs.append("UPLOAD.md: must say no audio is included, record the timing numbers checked, the sources and the open questions")
    m = re.search(r"= 1 cover \+ (\d+) teacher \+ (\d+) student \+ 1 terms page", up)
    if not m or 2 + int(m.group(1)) + int(m.group(2)) != len(PLAN):
        errs.append("UPLOAD.md: the page-count list (1 cover + teacher + student + 1 terms) must total the PDF's pages")
    if m and (int(m.group(1)) != D.IX("example2") - 1 or int(m.group(2)) != D.IX("reflect") - D.IX("tempo") + 1):
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
    return (f"seconds per beat = 60 / BPM, per bar = 240 / BPM and bars in 10 seconds = BPM / 24 recomputed exactly (fractions) and by an independent float method; "
            f"10 seconds is a whole number of bars only at tempo = 24 x bars (96, 120 and 144 BPM give 4, 5 and 6; 90, 100, 110 and 128 do not); every cell of the tempo table "
            f"(7 tempos) and of the section-start table (96, 120, 144 BPM: 44, 45 and 46 bars, 110, 90 and 76.67 s); the countdown cue sheet at all three tempos (number 10 at bar 17 beat 1, "
            f"each cue on the clock second it names, the drop on beat 1 of bar 21, 22 or 23); the snare-roll ladder (1, 2, 4, 8 hits per beat; 500, 250, 125, 62.5 ms at 120 BPM; 120 hits in "
            f"bars 9 to 16); the example sweep and pitch-up (200 to 12,000 Hz, 12 semitones = one octave); the section map (10 elements x 5 sections, 3, 6, 4, 7, 4 playing); "
            f"every 'Step N' agrees with the project sheet on pages, slides, notes and UPLOAD.md; class badges agree with the pacing page; every drawing renders alone on a transparent "
            f"ground with no ink at its edges; hero art inside its viewBox; rendered-DOM footer gap on every page; no truncated slide bullets; edges of cover.png and previews clear; "
            f"no audio, lyrics, melodies, alcohol, religious or brand wording or student work; grades 9-12; tags and subjects are not headings; no 'what changed' page (ORIGINAL).")


# ================================================================ UPLOAD.md (written by gen.py so every number matches the build)
def write_upload():
    np_, ns = len(PLAN), len(SLIDES)
    n_teacher = (PLAN.index("example2") + 1) - 1
    n_student = (PLAN.index("reflect") + 1) - (PLAN.index("tempo") + 1) + 1
    assert 2 + n_teacher + n_student == np_, "page-count list must total the PDF"
    nt = len(LISTING_TITLE)
    desc = (f"{DESC_START} students arrange a track of 40 to 48 bars in Logic Pro in five sections: an intro, a build-up with risers, a snare roll that speeds up from quarter notes to "
            f"eighth, sixteenth and thirty-second notes, a filter sweep that opens a low-pass filter and a pitch-up, a 10-second countdown with the numbers 10 to 1 one second apart, "
            f"the drop on the first beat after 1, and an outro. The theme is a New Year countdown, but it is a music-technology project that suits any class (students may count down to a launch, "
            f"a game start or a finish line). This New Year’s Countdown project takes {CLASSES} class periods (the pacing guide also shows two and four) and is an original Hudson Beat project; "
            f"the steps are written for Logic Pro, while the ideas (sections, tempo math, automation) carry over to GarageBand.\n\n"
            f"WHAT'S INCLUDED (ZIP: {np_}-page PDF = 1 cover + {n_teacher} teacher + {n_student} student + 1 terms page, plus {ns}-slide intro deck as .pptx and PDF)\n"
            f"• Teacher pages: how to use, project overview, setup, a {CLASSES}-class pacing guide with the deck slides for each class, "
            f"two pages of teacher notes (struggles, variations, resources, grading), a Logic quick reference and a two-page worked example (an invented track at 120 BPM: "
            f"45 bars = 90 seconds, a countdown of 5 bars from bar 17, the drop at bar 22, the cue sheet, the snare ladder and the filter sweep) ({n_teacher} pages)\n"
            f"• Student pages: a tempo table (seconds per beat and per bar, bars in 10 seconds at seven tempos, and the start of every section at 96, 120 and 144 BPM), a section map of ten elements by five sections, "
            f"a snare-roll ladder with riser and automation checklists, a countdown cue sheet (the bar and beat of every number at three tempos plus a blank sheet), a mix checklist, the 3-page project sheet "
            f"(overview, goals, vocabulary, requirements, steps, tips, submission checklist), the /{RUBRIC_TOTAL} rubric, a vocabulary page, a feedback planner and a reflection page ({n_student} pages)\n"
            f"• Teacher-presented intro deck, {ns} slides with speaker notes on every slide: a think-and-share hook, what the project is, the section map, the timing math, the snare ladder, "
            f"the filter sweep and pitch-up, building it in Logic, the countdown timeline, what to turn in and the rubric\n\n"
            f"THE THREE CLASS PERIODS\n"
            f"• Class 1: hook; the section map; the timing math and a tempo; plan the build\n"
            f"• Class 2: set up Logic with a marker at every section; build the intro and the build-up\n"
            f"• Class 3: place the countdown, land the drop, add the outro; mix, bounce, present and reflect\n\n"
            f"WHAT STUDENTS LEARN\n"
            f"• Tension: what a riser, a snare roll that speeds up, a filter sweep and a pitch-up each do, and why a countdown makes a drop feel bigger\n"
            f"• Timing math: seconds per bar in 4/4 = 240 ÷ BPM; bars in 10 seconds = BPM ÷ 24; tempo = 24 × bars gives a whole number of bars (96, 120 or 144 BPM = 4, 5 or 6 bars); at 120 BPM a snare roll has 500, 250, 125 and 62.5 milliseconds between hits\n"
            f"• Building in Logic Pro: markers for sections, risers in Alchemy or Retro Synth, Quick Sampler or Sample Alchemy, Drum Machine Designer, Channel EQ or filter automation, reverse effects and the Step Sequencer if your version has them; automation, mixing and bounce\n"
            f"• Mixing so the build-up grows, the countdown is clear and the drop is the biggest part, and explaining their choices in a reflection\n\n"
            f"GOOD TO KNOW\n"
            f"• There is no audio in this resource and no student work. No melody, song or lyrics are printed or notated; students make every sound themselves in Logic Pro, from instruments, their own voices or synth beeps\n"
            f"• Requires Logic Pro on a Mac. A MIDI keyboard and a microphone are optional; nobody has to read music. Where a control may differ between versions, the pages say \"if your version has it\"\n"
            f"• Rubric: 5 categories scored 1-5, /{RUBRIC_TOTAL}; the final grade is the average of the student's and the teacher's score\n"
            f"• Grades 9-12; music technology or music production classes\n"
            f"• The deck uses the free Oswald and Source Sans 3 fonts (built into Google Slides); install them for PowerPoint or Keynote, or present "
            f"the PDF copy, which shows the intended look\n"
            f"• Every student page prints well in black and white\n\n"
            f"Logic Pro is a product of Apple Inc., named only to describe compatibility. This resource is not affiliated with Apple.\n\n"
            f"{D.DISCLOSURE_NEW}")
    tbl = "; ".join(f"{b} BPM: {dec(bar_len(b), 3)} s per bar, {sec_bars(b)[2]} countdown bars, {total_bars(b)} bars, {dec(total_s(b), 2)} s, drop at bar {start_bar(b, 3)} ({dec(start_s(b, 3), 2)} s)" for b in CHOICES)
    nonw = "; ".join(f"{b} BPM = {dec(cd_bars(b), 4)} bars" for b in (90, 100, 110, 128))
    cues = ", ".join(f"{'drop' if s == 10 else 'number ' + str(number_at(s))} at bar {cue_pos(EX_BPM, s)[0]} beat {fmt(cue_pos(EX_BPM, s)[1])}" for s in range(11))
    lad = "; ".join(f"{nv}: {h} per beat, {num(gap_ms(120, h))} ms at 120 BPM" for nv, _, h in LADDER)
    md = f"""# UPLOAD: New Year's Countdown, original Logic Pro project (TpT 067)

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
({nt} characters; the limit is 80.) The title leaves out New Year, Winter and Holiday because TpT's Seasonal Titles notice blocked a holiday-named title on 027 (see 032, 033 and 034); "Countdown" alone is a plain search word. "Logic Pro" sits in the first 30 characters.

## 2. Description

```
{desc}
```

## 3. Grades

9th, 10th, 11th, 12th (`9th-grade`, `10th-grade`, `11th-grade`, `12th-grade` in tpt.json), as tpt/METADATA-GUIDE.md prescribes for every music-production item.

## 4. Subjects and tags

- Subjects in tpt.json: Music; Computer Science - Technology; Music Composition (all three are in `tpt/SUBJECT-OPTIONS.json` and none is a heading)
- Tags in tpt.json: {", ".join(TAGS)} (four exact entries of `tpt/TAG-OPTIONS.json`; the limit is 6). "Holiday" and "Student Practice" are headings and are not used; "New Year" is a real entry under the Holiday heading.
- Formats: PDF (add PowerPoint or ZIP if TpT offers it)
- Answer key: left out of tpt.json (there is none; the worked example is a model)

## 5. Resource type

- Projects
- Unit Plans
- PowerPoint Presentations

## 6. Standards (optional)

National Core Arts Standards, Music (Music Technology, high school): MU:Cr1.1, MU:Cr2.1, MU:Pr6.1, MU:Re7.2. Tag only if it matches how the teacher uses it.

## 7. Price

**${PRICE}** (paid), multiple-license price ${PRICE}. Inside the $7-9 holiday-kit range, for a kit with {np_} pages + {ns} slides, a tempo table, a section map, a snare-roll ladder, a countdown cue sheet, a mix checklist and a two-page worked example, listed in late December.

## 8. Free or paid / free preview pages

Paid. Preview PDF (4 watermarked pages): the {CLASSES}-class pacing guide, the snare-roll ladder, the tempo table and the /{RUBRIC_TOTAL} rubric. "Number of pages or slides" is {np_ + ns} ({np_} pages + {ns} slides).

## 9. Sources and credits

- Art: the cover, previews and deck use the owner's pre-made art (`art/hero.png`: a laptop with a rising waveform, headphones, microphone, monitor, controller and a plain stopwatch dial with no numbers, and confetti), copied whole from `tpt/_art/next/new-years-countdown/`; the file is logged in `tpt/_art/USAGE.md`. Everything else, including every number on the cover and pages, is drawn or printed in code.
- Facts: none beyond arithmetic. Every timing number comes from the formulas printed in the product (seconds per bar = 240 ÷ BPM; bars in 10 seconds = BPM ÷ 24; hits-per-beat gaps = 60000 ÷ (BPM × hits)). The theme text says only that many communities count down the last seconds of the year together; it names no date, place, custom or recording.
- Music: nothing is notated or printed. No songs, artists or recordings are named. Students make every sound, including the countdown voice or beeps.
- Fonts: Oswald and Source Sans 3 (SIL OFL 1.1). Logic Pro is named only to describe compatibility.

## 10. Before you click publish

- [ ] **Needs QA approval first.** This is a new kit (not yet on TpT); the Manager releases it only after a QA `**Verdict: APPROVED**`. Season rule: build for late December; listing no sooner than the 2-8 week window allows.
- [ ] Cover and previews show "HUDSON BEAT" in type; PDF footers read "© 2026 Brian Lotze · Hudson Beat · For single-classroom use".
- [ ] No school name, logo, student names or work, audio, video, lyrics, melody, song title or Logic session anywhere (`gen.py --check` scans every output and every file in this folder).
- [ ] **Neutral and secular.** The theme is a count to a big moment; no religious content, no alcohol imagery, no brands, no real recordings. `gen.py --check` fails on alcohol, religious and holiday-specific words. The stopwatch on the art has a plain dial with no numbers; the numbers on the cover are printed text.
- [ ] **Timing numbers (all recomputed in `gen.py --check`, exactly with fractions and again with an independent float method).** Seconds per beat = 60 / BPM; seconds per bar in 4/4 = 240 / BPM; bars in 10 seconds = BPM / 24, a whole number only when tempo = 24 x bars. Not whole: {nonw}. Choices: {tbl}. Sections are 8 + 8 + countdown + 16 + 8 bars (44 to 46 bars); the intro, build-up and countdown start at bars 1, 9 and 17. Cue = second x BPM / 60 beats after bar 17 beat 1. At 120 BPM: {cues}. Snare ladder: {lad}; 120 hits across bars 9 to 16. Rounding: seconds per beat and per bar to 3 decimals, bars in 10 seconds to 4, sections and totals to 2, half up.
- [ ] **Original project.** Built with `ORIGINAL = True` in `tpt/_dmp2_common/dmp2.py` (like 031, 036, 053, 057, 061 and 063): no "what changed" page and the new disclosure line. The reflection page is the shared Reflection element, scored in the rubric's "Plan & Reflection" row. `dmp2.py` is unchanged.
- [ ] **Logic Pro names to confirm on a Mac with a current Logic.** The Marker global track with a plus (+) button and a Create Marker key command (hedged), Alchemy and Retro Synth patches, Quick Sampler and Sample Alchemy (Reverse, hedged), Drum Machine Designer, the Step Sequencer, Channel EQ high cut and Auto Filter ("if your version has it"), automation (A), Mixer (X), Command-B bounce. Nothing says a loop or preset of a given name exists.
- [ ] **Open questions for the owner:** (1) **Title.** No New Year, Winter or Holiday in the title because of TpT's seasonal-title notice (see 1). (2) **Price.** ${PRICE}, inside the $7-9 range. (3) **Classes.** Three periods; the pacing page shows how to run it in two or four. (4) **Tempos.** Students choose 96, 120 or 144 BPM so 10 seconds is 4, 5 or 6 whole bars; say if you would also allow 72 or 168 BPM (3 or 7 bars, 43 or 47 bars in all).
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
