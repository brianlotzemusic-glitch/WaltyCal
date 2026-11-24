#!/usr/bin/env python3
"""Logic Pro project kit: Holiday Radio Ident (TpT 080): the teacher resource, the intro deck and the listing files.

    python3 gen.py            build everything into this folder (also writes UPLOAD.md)
    python3 gen.py --lowres   same, but square images at scale 1 and small page shots (self-check only; --check rejects it)
    python3 gen.py --check    verify content and layout: the timing arithmetic (seconds per beat = 60 / BPM, seconds per bar in 4/4 = 240 / BPM, bars in a 20-second ident =
                              BPM / 12, a whole number only at BPM = 12 x bars; the same for 15 and 30 seconds), the tempo table, the cue sheet (voice in, duck start and end,
                              final hit, in seconds and in bar and beat at 96, 120 and 144 BPM, exact fractions and an independent float method), the script templates (word
                              counts, read time at 150 words per minute = 2.5 words per second, fit in the 12-second voice window), the dB ladder (amplitude = 10^(dB/20),
                              20 log10(0.5) = -6.02), the duck depths, the compression arithmetic (gain reduction = dB over threshold x (1 - 1/ratio)), the EQ and compressor
                              drawings' curves, Step N references on every page, slide and UPLOAD.md, class badges against the pacing page (the "three classes" slide carries
                              Classes 1-3), drawings (each rendered alone on a transparent ground: no ink within 4 px of its edge), the hero art, files, page and slide counts,
                              class slots, fonts, fit and overlap, dead space, footer gap (pages and deck slides), truncated slide bullets, the edges of cover.png and the
                              previews, banned strings, tpt.json and UPLOAD.md

An ORIGINAL Hudson Beat project (dmp2.ORIGINAL = True, like 063, 067, 070 and 076). Students make a 15 to 30 second radio station ident (a short sound logo and spot) for an invented
winter station: a voice read of an original script, an original music bed built from Logic's own loops, Session Players or a simple MIDI pattern, and sound effects. They plan the length
with timing math (tempo = 12 x bars for 20 seconds), record the voice with good microphone technique and levels, clean it up with EQ and compression, and duck the music under the voice
with sidechain compression or automation. No audio ships and no existing songs, jingles, stations or brands are used. The art on the cover, the previews and the deck is the owner's
pre-made hero (art/hero.png: a microphone with headphones and a small radio), used whole. Everything else is drawn in code. The shared builder is ../_dmp2_common/dmp2.py (untouched).
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
SLUG = "holiday-radio-ident"
TITLE = "Holiday Radio Ident"
ACCENT = "#2F7FB8"          # this product's single accent: icy blue (a shade deeper than the art's #4FA3D9, so small labels read)
ACC_LIGHT = "#DCEBF6"
PRICE = "8.00"
CLASSES = 3
GRADES_TEXT = "9–12"
GRADE_SLUGS = ["9th-grade", "10th-grade", "11th-grade", "12th-grade"]
TAGS = ["Winter", "Project-based Learning", "Projects", "Activities"]     # exact entries of tpt/TAG-OPTIONS.json, none a heading
SUBJECTS = ["Music", "Computer Science - Technology", "Music Composition"]     # all in SUBJECT-OPTIONS.json, none a heading
ANSWER_KEY = None
LISTING_TITLE = "Logic Pro Radio Ident Project | Voice, Music Bed, Ducking, EQ | High School"
DESC_START = "Radio ident project for high school music technology:"
DESC_MUST = ["Holiday Radio Ident", "20-second", "seconds per bar", "tempo = 12 × bars", "120 BPM", "no audio", "ducking", "sidechain", "150 words per minute", "high-pass"]
ZIP_DIR = "Holiday Radio Ident - Hudson Beat"
ZIP_DATE = (2026, 11, 24, 12, 0, 0)
TYPE = "Original Project"
PROJ_LINE = "Music Technology | <i>Radio Ident Project</i> | 3 class periods"
DECK_STRAP = "Voice, music bed, effects"
REFLECT_ROW = "Plan &amp; Reflection"
# split so this file never contains them (the --check scan reads every file in this folder)
BANNED_EXTRA = ["Rud" + "olph", "Fro" + "sty", "Gri" + "nch", "Santa Claus " + "Is", "Jingle Bell " + "Rock", "Feliz " + "Navidad",
                "Mari" + "ah Carey", "Spoti" + "fy", "You" + "Tube", "Home " + "Alone", "Nin" + "tendo", "Ro" + "land",
                "Star " + "Wars", "Hans " + "Zimmer", "John " + "Williams", "Harry " + "Potter", "Pix" + "ar", "Lord of the " + "Rings",
                "Winter " + "Wonderland", "Let It " + "Snow", "Sleigh " + "Ride", "X" + "mas", "Times " + "Square", "Auld " + "Lang",
                "cham" + "pagne", "bub" + "bly", "Neu" + "mann", "iHeart" + "Radio", "Clear " + "Channel", "Sir" + "ius", "Pand" + "ora"]

# ================================================================ page plan (teacher pages 2-10, student pages 11-26)
PLAN = ["cover", "howto", "overview", "setup", "pacing", "tn1", "tn2", "logicref", "example", "example2", "tempo", "script", "chain", "ladder", "bed", "eqcomp", "duck", "cues",
        "mix", "proj1", "proj2", "proj3", "rubric", "vocab", "present", "reflect", "terms"]


def pg(k):
    return PLAN.index(k) + 1


# ================================================================ the arithmetic (exact fractions; all verified in --check)
CHOICES = (96, 120, 144)                    # the tempos a student may choose: 20 seconds is 8, 10 or 12 whole bars
TEMPOS = (90, 96, 100, 110, 120, 128, 144)  # the tempo table's rows (whole and not whole)
EX_BPM = 120                                # the worked example's tempo: 10 bars of 2 seconds
ID_SECONDS = 20
LENGTHS = (15, 20, 30)                      # ident lengths in seconds that the second table compares
LEN_TEMPOS = (96, 120, 128, 144)


def spb(bpm):
    """Seconds per beat = 60 / BPM."""
    return Fraction(60, bpm)


def bar_len(bpm):
    """Seconds per bar of 4/4 = 240 / BPM (four beats)."""
    return Fraction(240, bpm)


def id_bars(bpm, secs=ID_SECONDS):
    """Bars in an ident of `secs` seconds = secs / (240 / BPM) = secs x BPM / 240 (20 seconds: BPM / 12)."""
    return Fraction(secs) / bar_len(bpm)


def is_whole(bpm, secs=ID_SECONDS):
    return id_bars(bpm, secs).denominator == 1


# the cue sheet: events in seconds from the start of the ident (the voice window is 12 seconds: 4 s to 16 s)
VOICE_IN, VOICE_OUT = Fraction(4), Fraction(16)
DUCK_RAMP = Fraction(1, 2)                  # the music falls (and returns) over half a second
DUCK_DB = 8                                 # the example duck depth in dB
CUES = [("Music bed starts at full level; wind fades in", Fraction(0)),
        ("Duck starts: the music begins to fall", VOICE_IN - DUCK_RAMP),
        ("Voice comes in; the music has reached its ducked level", VOICE_IN),
        ("Voice ends; the music starts to rise", VOICE_OUT),
        ("Music is back at full level", VOICE_OUT + DUCK_RAMP),
        ("Chime and final hit; the bed stops", Fraction(18)),
        ("End of the ident, after the tail rings out", Fraction(ID_SECONDS))]


def cue_beats(bpm, s):
    """Beats from the start of the ident to second s: s x BPM / 60."""
    return Fraction(s) * bpm / 60


def cue_pos(bpm, s):
    """(bar, beat) of second s: bar 1 + the whole bars gone by, beat 1 + the beats left over."""
    b = cue_beats(bpm, s)
    return 1 + int(b // 4), 1 + (b - 4 * (b // 4))


def pos_s(bpm, bar, beat=1):
    """Seconds at a position (bar, beat): ((bar - 1) x 4 + (beat - 1)) x 60 / BPM."""
    return ((bar - 1) * 4 + (Fraction(beat) - 1)) * Fraction(60, bpm)


# speaking rate: about 150 words per minute = 2.5 words per second
WPM = 150
WPS = Fraction(WPM, 60)


def read_s(words):
    """Seconds to read `words` words at 150 words per minute."""
    return Fraction(words) / WPS


def words_for(secs):
    """Words that fit `secs` seconds at 150 words per minute."""
    return Fraction(secs) * WPS


# the three script templates (original, no brands, invented stations; none uses call letters)
SCRIPTS = [("A", "Snowline Radio", "A morning station",
            "This is Snowline Radio. Frost on the windows, snow on the roof, warm music inside. Stay cozy with us all winter long. Snowline Radio."),
           ("B", "Northlight Radio", "A long-nights station",
            "The nights are long, so we brought the light. Northlight Radio plays your favorite winter sounds. Turn it up, and let it glow. Northlight Radio."),
           ("C", "Hollow Pine Radio", "A hometown station",
            "Hollow Pine Radio, the sound of our town in winter. Snow day or school day, we’re on the air. Tell a friend, and tune in. Hollow Pine Radio.")]
SCRIPT_WORDS = [len(t.split()) for _, _, _, t in SCRIPTS]       # 24, 25, 28


def n_words(t):
    return len(t.split())


# ---- decibels: amplitude ratio = 10^(dB / 20); dB = 20 log10(ratio)
def amp(db):
    return 10 ** (float(db) / 20)


def to_db(ratio):
    return 20 * math.log10(ratio)


def r3(x):
    """Round half up to 3 decimals (floats from exact-enough math; the printed values have no ties)."""
    return f"{math.floor(x * 1000 + 0.5) / 1000:.3f}".replace("-", "−")


def r1(x):
    return f"{math.floor(x * 10 + 0.5) / 10:.1f}".replace("-", "−")


def r2(x):
    return f"{math.floor(x * 100 + 0.5) / 100:.2f}".replace("-", "−")


LADDER = [(0, "Full scale: the highest level a digital recording can hold. Above it the sound clips."),
          (-3, "The ceiling for the whole mix in this kit’s worked example."),
          (-6, "Half the amplitude of full scale. The loudest words of a voice may touch this level."),
          (-9, "The middle of the voice target (the worked example’s voice peaks)."),
          (-12, "The low end of the voice target, and the music bed’s peaks in the worked example."),
          (-18, "An average level that some guides suggest for the body of a recording."),
          (-20, "The ducked music in the worked example: a bed at -12 dBFS lowered by 8 dB.")]
HALVES = [Fraction(1, 2), Fraction(1, 4), Fraction(1, 8)]          # amplitude halved once, twice, three times
DUCK_DEPTHS = (6, 8, 10, 12)                # dB of music reduction in the duck table
BED_PEAK = -12                              # the worked example's music bed peaks (dBFS)
VOICE_PEAK = -9                             # the worked example's voice peaks (dBFS)
MIX_CEILING = -3                            # the worked example's mix ceiling (dBFS)

# compression: gain reduction = (dB over threshold) x (1 - 1/ratio)
RATIOS = (2, 3, 4)
OVERS = (3, 6, 9, 12)
EX_THRESH = -17                             # the worked example's threshold (dB)
EX_RATIO = 4
EX_OVER = VOICE_PEAK - EX_THRESH            # 8 dB over


def gain_red(over, ratio):
    return Fraction(over) * (1 - Fraction(1, ratio))


def out_level(inp, thresh, ratio):
    """Output level of a hard-knee compressor: unchanged below the threshold, thresh + (in - thresh) / ratio above it."""
    return Fraction(inp) if inp <= thresh else Fraction(thresh) + (Fraction(inp) - thresh) / ratio


# EQ: a 2nd-order high-pass at 80 Hz and a small example boost near 3 kHz
HPF_HZ = 80
PRES_HZ, PRES_DB = 3000, 2


def hpf_gain_db(f, fc=HPF_HZ):
    """Response of a 2nd-order Butterworth high-pass: -10 log10(1 + (fc / f)^4); -3.01 dB at fc."""
    return -10 * math.log10(1 + (fc / f) ** 4)


def eq_gain_db(f):
    bump = PRES_DB * math.exp(-(math.log2(f / PRES_HZ) ** 2) / (2 * 0.8 ** 2))
    return hpf_gain_db(f) + bump


def rnd(x, nd):
    """Round half up (a 5 rounds up) to nd decimals, on exact fractions."""
    s = Fraction(10) ** nd
    return Fraction(math.floor(Fraction(x) * s + Fraction(1, 2)), 1) / s


def dec(x, nd):
    return f"{float(rnd(x, nd)):.{nd}f}"


def num(x, nd=2):
    """A number rounded half up to nd decimals with no trailing zeros."""
    return f"{float(rnd(x, nd)):g}"


def fmt(x):
    x = float(x)
    x = round(x + 1e-9, 3)
    return f"{x:.0f}" if x == int(x) else f"{x:g}"


def bb(bar, beat):
    return f"{bar} {fmt(beat)}"


# ================================================================ the project text (original; students read these pages)
THEME = ("A radio ident is the short sound logo and spot that a station plays between songs: a voice says the station’s name and a promise, a music bed carries it, "
         "and a few sound effects set the scene. This project is a winter-season station, but it suits any class: students may invent a station for any season. "
         "Every station name in this kit is invented, and none uses call letters.")
BUILD_NOTE = ("The skills here are the ones every voice track needs: record cleanly, shape the voice with EQ and compression, and lower the music under the words. "
              "They carry over to podcasts, announcements, video and school broadcasts.")
OVERVIEW = ("Make a radio ident in Logic Pro, 15 to 30 seconds long, for an invented winter station. It is built from a voice that reads a short original script, a music bed that is an "
            "original loop or pattern built from Logic’s own sounds, and sound effects such as sleigh-bell-like shakers, wind or a door chime. Students plan the length with timing math "
            "(tempo = 12 × bars for a 20-second ident, so 96, 120 and 144 BPM give 8, 10 and 12 bars), record the voice with good microphone technique and safe levels, clean it up with EQ and compression, "
            "and duck the music under the voice, either with sidechain compression or with automation. Nobody needs to read music, and no song is used.")
GOALS = ["Plan a 20-second ident: use one bar = 240 ÷ BPM seconds and tempo = 12 × bars to choose a tempo, and place the voice, music and effects on a cue sheet",
         "Write a script that fits its time: about 150 words per minute is 2.5 words per second, so a 12-second read is about 30 words",
         "Record a clean voice: microphone distance, a pop filter and levels that peak around −12 to −6 dBFS, and read the dB ladder",
         "Process the voice with a high-pass filter and gentle compression, then duck the music under it by about 6 to 12 dB, with sidechain compression or automation"]
VOCAB = [("Ident", "A short sound logo or spot, usually 5 to 30 seconds, that tells listeners which station they are hearing"),
         ("Music bed", "The music that plays under a voice. Here it is an original loop or pattern that is ducked while the voice speaks"),
         ("dBFS", "Decibels relative to full scale. 0 dBFS is the highest level a digital recording can hold, so every real level is a negative number"),
         ("Ducking", "Lowering the music while the voice speaks and letting it rise again afterward, by sidechain compression or by volume automation"),
         ("Sidechain", "A way to let one track control an effect on another: here the voice track tells the music track’s compressor when to turn the music down")]
REQS = ["Choose 96, 120 or 144 BPM in 4/4 and show why with the tempo table (page @TEMPO)",
        "Write or choose a script of about 24 to 30 words that fits the 12-second voice window, and record or use a read of it (page @SCRIPT)",
        "Record the voice with the microphone 10 to 20 cm away and a pop filter, with peaks around −12 to −6 dBFS and no clipping (pages @CHAIN and @LADDER)",
        "Build an original music bed and at least two sound effects, all on the beats of your cue sheet (pages @BED and @CUES)",
        "Clean up the voice with a high-pass filter and gentle compression, using small moves (page @EQCOMP)",
        "Duck the music under the voice by sidechain compression or automation, and mix so the voice is always clear (pages @DUCK and @MIX)",
        "Bounce the finished ident and reflect on your choices (page @REFLECT)"]
FILE_NAME = "“Your Name – Ident”"
STEP_NAMES = ["Plan the ident", "Write and record the voice", "Build the bed and effects", "Clean up the voice", "Duck the music", "Mix and bounce", "Present &amp; get feedback"]
STEPS = ["<b>Plan the ident</b> — Use the tempo table (page @TEMPO) to pick 96, 120 or 144 BPM and work out how long each bar lasts, then list your cues in seconds, bars and beats on the cue sheet (page @CUES)",
         "<b>Write and record the voice</b> — Choose one of the three script templates or write your own (page @SCRIPT), set up the microphone and the signal chain (page @CHAIN), set your level with the dB ladder (page @LADDER) and record",
         "<b>Build the bed and effects</b> — Build an original music bed from Logic’s own loops, Session Players or a simple MIDI pattern, and add sound effects, on the plan on page @BED (quick reference: page @LOGICREF)",
         "<b>Clean up the voice</b> — Put a high-pass filter and a gentle compressor on the voice track, with small moves and your ears as the judge (page @EQCOMP)",
         "<b>Duck the music</b> — Lower the music under the voice with sidechain compression or automation, and place the duck on your cue sheet (pages @DUCK and @CUES)",
         "<b>Mix and bounce</b> — Set levels with the mix checklist (page @MIX), then bounce the whole ident and name the file as on the checklist",
         "<b>Present &amp; get feedback</b> — Write three questions you want classmates to answer about your ident. Play it, point out the voice, the bed, the effects and the duck as they arrive, "
         "and answer at least 2 of each classmate’s questions. Then reflect (page @REFLECT)."]
TIPS = ["Record the voice first and build the music around it. The bed has to leave room for the words.",
        "Say the script out loud twice before you record. Time yourself: the read should be shorter than the voice window, so there is room to breathe.",
        "Start with small moves on the EQ, the compressor and the duck. Change one thing at a time and listen after each change.",
        "Save a new version of your project at the end of each class, so you can always go back."]
CHECK = ["Bounced .mp3 or .wav of your whole ident, 15 to 30 seconds long",
         "Zipped .logicx project file handed in",
         f"Files named correctly: {FILE_NAME}",
         "Tempo table work, script and cue sheet handed in",
         "Rubric self-score done (page @RUBRIC)",
         "I can say where the voice comes in, where the duck starts and ends, and where the ident finishes, in seconds and in bars"]
RUBRIC_NOTE = "Each category is scored 1–5. Score yourself first; the final grade is the average of your score and your teacher’s."
LEVELS = [1, 2, 3, 4, 5]
RUBRIC = [
    ("Voice & Recording", ["No voice recorded", "Too quiet, clipping or loud pops", "Clear voice, but uneven distance, pops or a hot level",
                           "Clean read, peaks around −12 to −6 dBFS, no clipping, script fits", "Clean, steady, expressive read with controlled peaks"]),
    ("Music Bed & Effects", ["No music bed", "A loop that is not original or does not fit", "Original bed and one effect, some timing slips",
                             "Original bed fits the bars; two or more effects on beats", "A bed with a clear shape and scene-setting effects"]),
    ("EQ & Compression", ["No processing", "Plug-ins on, but not checked by ear", "High-pass and compressor, with extreme settings",
                          "High-pass near 80 Hz, gentle compression of about 3 to 6 dB, by ear", "Small, deliberate moves, each one explained"]),
    ("Ducking & Mix", ["The music covers the voice", "Music lowered, but words still hard to hear", "Music ducks, with a late or abrupt start or release",
                       "Smooth duck of about 6 to 12 dB, clear voice, no clipping", "Smooth, well-timed duck, balanced mix, ends on time"]),
    ("Plan & Reflection", ["Plans, presentation or reflection missing", "Thin plan; little to say about choices", "Plan and reflection complete, with basic detail",
                           "Correct tempo math, word count and cue sheet; thoughtful reflection", "Insightful reflection and a polished presentation"]),
]
RUBRIC_TOTAL = 25
RUBRIC_SHORT = ["A clean, expressive read with controlled peaks",
                "A bed with a clear shape and scene-setting effects",
                "Small, deliberate moves, each one explained",
                "A smooth, well-timed duck and a balanced mix",
                "Insightful reflection and a polished presentation"]
RUBRIC_SLIDE_LINE = "Scored 1–5 · final grade = average of your score and mine, out of 25"
RUBRIC_ROW_PITCH = 0.86
RUBRIC_LINE_Y = 6.3

TN_REINFORCES = ("Teaches how a voice spot is made. Students learn to plan a short piece with timing arithmetic, to fit a script to a time, to record a voice with sensible levels, "
                 "to shape it with a high-pass filter and a compressor, and to lower music under words with sidechain compression or automation, all in Logic Pro.")
STRUGGLES = ["The voice sounds boomy or hissy: check the distance (10 to 20 cm), keep it steady and look at the high-pass filter before anything else (page @EQCOMP).",
             "The recording clips or is very quiet: lower or raise the input gain at the interface, not the track fader, and read the peak against the dB ladder (page @LADDER).",
             "The music still covers the words: deepen the duck by a few dB, check that the ramp starts half a second early, and listen again (page @DUCK).",
             "The ident runs long: count the words (about 2.5 per second), then check the bars and the cue sheet (pages @SCRIPT and @CUES)."]
VAR_EASY = ("Keep the tempo at 120 BPM, where 20 seconds is exactly 10 bars and every cue lands on a beat (page " + str(pg("cues")) + "); use one of the three script templates, and "
            "duck the music with volume automation only.")
VAR_HARD = ("Build a 15-second and a 30-second version of the same ident (page " + str(pg("tempo")) + "), or duck with sidechain compression and then compare it with an automated duck. "
            "Or add a second voice, a tagline that comes back at the end.")
RESOURCES = [("Tempo table (page @TEMPO)",
              "Seconds per beat and per bar, and the bars in 20 seconds at seven tempos, then in 15, 20 and 30 seconds."),
             ("Script templates (page @SCRIPT)",
              "Three original scripts with word counts and read times, a words-per-second rule and a blank script sheet."),
             ("Recording and levels (pages @CHAIN and @LADDER)",
              "A signal-chain diagram, a microphone checklist, and a dB ladder with the −6 dB rule."),
             ("EQ, compression and ducking (pages @EQCOMP and @DUCK)",
              "Starting points for a high-pass filter and a compressor, the gain-reduction arithmetic, and two ways to duck."),
             ("Cue sheet and worked example (page @CUES and pages @EXAMPLE–@EXAMPLE2)",
              "Every cue at three tempos, and an invented 20-second ident at 120 BPM. A model, not a template.")]
TN_NOTE = ("A good listening day: play each ident and ask the class two questions. Could you hear every word? When did you notice the music move? "
           "If a word is lost, find it on the cue sheet together. This kit names no songs or artists.")
GRADING = ["The rubric: five categories, each scored 1–5, /25 (page @RUBRIC). Students score themselves first; the final grade is the "
           "average of their score and yours.",
           "Voice & Recording (rubric row 1): listen for pops and hiss, check the peak on the meter against the dB ladder and count the script words (pages @LADDER and @SCRIPT).",
           "Music Bed & Effects (rubric row 2): check that the bed is original, that its length matches the bars and that each effect sits on a cue (page @BED).",
           "EQ & Compression (rubric row 3): open the plug-ins, find the high-pass filter, and ask the student to say what each change did (page @EQCOMP).",
           "Ducking & Mix (rubric row 4): play the ident with the voice solo and with it mixed, and look at the duck depth and ramp (pages @DUCK and @MIX).",
           "Plan & Reflection (rubric row 5): the tempo table work, the cue sheet, the feedback questions and the Reflection page (page @REFLECT) are the evidence."]
PACING = [
    {"n": 1, "owner": "Hear the idea, plan the timing, write the script and record the voice.",
     "do": "Slides 1–8: the think-and-share, what the project is, the three classes, the 20-second timeline, the timing math, the signal chain and the dB ladder. Hand out the tempo table, "
           "the script page and the cue sheet. Before they leave, students have a tempo, a script that fits 12 seconds and a first recording.",
     "slides": (1, 8), "pages": ["tempo", "script", "chain", "ladder", "cues", "proj1", "proj2", "proj3", "vocab"],
     "deck": "Hear the ident · the 20-second timeline · tempo = 12 × bars · record"},
    {"n": 2, "owner": "Build the music bed and effects, and clean up the voice.",
     "do": "Slides 9–11: building in Logic, EQ for voice and compression. Demonstrate the loop browser or a simple pattern, then the high-pass filter and the compressor. Students build the bed and "
           "the effects and process the voice. Walk the room with one question: what does this setting change?",
     "slides": (9, 11), "pages": ["ladder", "bed", "eqcomp", "cues", "present"], "deck": "Build it in Logic · EQ · compression"},
    {"n": 3, "owner": "Duck the music, mix, bounce, present and reflect.",
     "do": "Slides 12–16: ducking, what to turn in, the rubric, presentation day and the wrap-up. Students duck the music with sidechain compression or automation, mix with the checklist, bounce "
           "and present.",
     "slides": (12, 16), "pages": ["duck", "cues", "mix", "rubric", "present", "reflect"], "deck": "Ducking · checklist · rubric · presentations"},
]
PACING_EXTRA = (
    '<div class="cols" style="margin-top:4pt;gap:14pt"><div class="box acc-b"><span class="k">The one thing to do on Class 1</span>'
    '<p style="margin:0;font-size:10.6pt">Make sure every student leaves with 96, 120 or 144 BPM, a script of about 24 to 30 words and a voice recording with no clipping, so that Class 2 '
    'is all building and processing. Check each tempo against the tempo table before they go.</p></div>'
    '<div class="box"><span class="k">With two or four periods</span><p style="margin:0;font-size:10.6pt"><b>Two classes:</b> Class 1 is the plan, the script, the recording and the music bed; '
    'Class 2 is the effects, the EQ and compression, the duck, the mix and short presentations. <b>Four classes:</b> keep Classes 1 and 2, then spend Class 3 on the duck and the mix, and '
    'Class 4 on presentations and reflection.</p></div></div>')
PACING_SIZE = 10.6
TN2_SIZE = 9.9

SONG_NOTE = ("No audio, recordings, lyrics or melodies are included, and no songs, jingles, stations, artists or albums are named. Students make every "
             "sound themselves, from the loops, instruments and effects in Logic and from their own voices.")
VOICE_NOTE = ("The voice can be the student’s own, a classmate’s with permission, or a read of the script recorded by anyone who agrees. Nobody has to record themselves. "
              "Use only sounds students made or have the right to use.")
CREDITS = ["The tempo table, the script templates, the dB ladder, the cue sheet, the checklists and the worked example: original work, Hudson Beat. "
           "The three station names are invented and are not call letters. No melodies, lyrics, recordings or published editions are included.",
           "The cover illustration was made with digital and AI tools. No audio, video, album art, screenshots, presets, templates, links or "
           "chart data from other sources are included. No student work is included. The audio guidance (levels, high-pass filter, compression, ducking and speaking rate) is general practice, "
           "given as starting points to set by ear."]
LOGIC_INTRO = ("Where to find the tools a Holiday Radio Ident is likely to use. Demonstrate what your class needs on Classes 1 and 2 and then "
               "let students work. Names are from current Logic Pro versions; labels move between versions, so check yours.")
LOGIC_REF = [("Project and tempo", "File › New…, then an Audio track to record the voice and a Software Instrument track for the bed. Set the project tempo in the control bar to 96, 120 or 144 BPM and keep the time signature at "
              "4/4. The timing arithmetic only works at that tempo, so set it first. Set a cycle from bar 1 to the bar after your last bar to hear the whole ident."),
             ("Record the voice", "On the Audio track, choose the microphone or interface as the input and click the record-enable button (R). Watch the track’s level meter while you read the loudest line: "
              "set the gain on the interface, not the fader, so the peaks land around −12 to −6 dBFS. Keep a pop filter in front of the microphone, and re-record a take that clips."),
             ("Music bed", "Open the Loop Browser (the loop icon in the toolbar) and search for drums, bass, keys or pads in a winter mood. Loops follow the project tempo. Or add a Session Player such as the Drummer, "
              "if your version has them, or draw a simple pattern in the Piano Roll on an Alchemy or Retro Synth patch. Make the bed as long as your bars: 8, 10 or 12."),
             ("Sound effects", "Search the Loop Browser or the patch browser for shaker, jingle, bell, wind or chime sounds, if your version has them, or build a wind sound from a noise patch. Place each effect on a beat of your cue sheet and "
              "keep it short. Sleigh-bell-like shakers sit well on the beat; a chime works as the final hit."),
             ("EQ for the voice", "Open Channel EQ on the voice track. Switch on its lowest band as a high-pass (low cut) filter if your version offers one and set it near 80 Hz. For presence, make a small boost with one band "
              "and listen; start with small moves, and remove the boost if the voice sounds harsh."),
             ("Compression for the voice", "Insert Compressor on the voice track. Set a ratio of about 3:1 or 4:1, then lower the threshold until the gain reduction meter shows about 3 to 6 dB on the loudest words. "
              "Use the make-up gain, if your version has it, to bring the level back. Choose settings by ear; this kit names no presets."),
             ("Ducking with sidechain", "Insert Compressor on the music track. In the plug-in header, open the Side Chain menu (if your version has it) and choose the voice track. Lower the threshold until the music drops about 6 to 12 dB "
              "while the voice speaks, and set the release so it rises smoothly."),
             ("Ducking with automation", "Press A to show automation on the music track and choose Volume. Click points to draw the music down about half a second before the voice and back up half a second after it. "
              "Draw ramps, not steps, so the move is not heard."),
             ("Mixer and bounce", "Press X for the Mixer and set levels and pan. Keep the master peak below your ceiling. Then File › Bounce › Project or Section (Command-B), MP3 or WAV, for the whole ident. "
              "In Finder, Control-click the .logicx and choose Compress.")]
PRESENT_CHECK = [f"Files named {FILE_NAME}; the .mp3 or .wav and the zipped .logicx handed in",
                 "Reflection page done (page @REFLECT)", "Three questions for classmates written",
                 "Rubric self-score done (page @RUBRIC)"]
VOCAB_PROMPT = "Where it shows up in my ident:"
TN1_EXTRA = (
    '<div class="box acc-b" style="margin-top:4pt"><span class="k">Where this kit helps with each struggle</span><ul style="margin:0">'
    '<li style="font-size:12pt;margin-bottom:3pt">A voice that sounds boomy or hissy: the EQ and compression page (page @EQCOMP) lists the starting points, and the signal chain (page @CHAIN) covers distance and the pop filter.</li>'
    '<li style="font-size:12pt;margin-bottom:3pt">Levels: the dB ladder (page @LADDER) gives the amplitude at each level, and the worked example (pages @EXAMPLE–@EXAMPLE2) shows a full set of levels.</li>'
    '<li style="font-size:12pt;margin-bottom:3pt">Music that covers the words: the ducking page (page @DUCK) shows both methods with depth and ramp numbers.</li>'
    '<li style="font-size:12pt;margin-bottom:0">An ident that runs long: the script page (page @SCRIPT) gives word counts and read times, and the cue sheet (page @CUES) the seconds, bars and beats.</li></ul></div>')
TN1_SIZE = 12.0
PROJ_SIZE = 11.4
VOCAB_GAP = 8
LOGIC_SIZE = 9.6
PROJ1_EXTRA = ""
RUBRIC_EXTRA = ""

# ================================================================ the worked example: an invented ident at 120 BPM
EX_BAR_S = bar_len(EX_BPM)                  # 2 s
EX_BARS = int(id_bars(EX_BPM))              # 10 bars
EX_SCRIPT = SCRIPTS[0]
EX_WEAK = "I will make a radio ident with a voice and music, and it will sound good."
EX_STRONG = ("My ident is for Snowline Radio at 120 BPM in 4/4. One bar lasts 240 ÷ 120 = 2 seconds, so 20 seconds is exactly 10 bars. The music bed starts on bar 1. "
             "The voice reads a 24-word script in about 9.6 seconds, from 4 seconds (bar 3 beat 1) to 16 seconds (bar 9 beat 1), so 12 seconds are available. "
             "The music starts to fall at 3.5 seconds (bar 2 beat 4), is 8 dB lower when the voice comes in, and is back at full level at 16.5 seconds (bar 9 beat 2). "
             "A chime and the final hit land at 18 seconds (bar 10 beat 1), and the ident ends at 20 seconds.")
EX_QUESTIONS = ["Could you hear every word? Which word was hardest to hear, if any?",
                "When did you first notice the music move, and did it feel smooth?",
                "Does the final chime feel like an ending?"]
EX_AUTO = ("the shaker plays on every beat of bars 1 and 2 and again on bar 9; the wind fades in over bars 1 and 2 and out under the voice; the music falls 8 dB over half a second before the voice; "
           "the chime is 3 dB under the final hit")


EX_LEVELS = [("Voice", VOICE_PEAK), ("Music bed, open", BED_PEAK), ("Music bed, ducked", BED_PEAK - DUCK_DB), ("Shaker", -18), ("Wind", -24), ("Chime", -15)]


def worst_sum_db(levels):
    """If every listed peak lined up at the same instant, the combined peak in dBFS: 20 log10(sum of amplitudes)."""
    return to_db(sum(amp(db) for db in levels))


# ================================================================ drawings (all in code, labels logged for the fit check)
def padded(body, W, H, M=10):
    """Wrap a drawing's body with M units of clear padding on all four sides (wider than the thickest outer stroke), so no edge pixel is ever inked."""
    return f'<g transform="translate({M},{M})">{body}</g>', W + 2 * M, H + 2 * M


def arrow(x1, y1, x2, y2, dash=False, w=4):
    """A line with a filled triangular head at (x2, y2); axis-aligned arrows only."""
    dx = (x2 > x1) - (x2 < x1)
    dy = (y2 > y1) - (y2 < y1)
    hl, hw = 16, 10
    bx, by = x2 - dx * hl, y2 - dy * hl
    px, py = -dy, dx
    pts = f"{x2},{y2} {bx + px * hw},{by + py * hw} {bx - px * hw},{by - py * hw}"
    da = ' stroke-dasharray="12 8"' if dash else ""
    return (f'<line x1="{x1}" y1="{y1}" x2="{bx}" y2="{by}" stroke="#000" stroke-width="{w}"{da}/>'
            f'<polygon points="{pts}" fill="#000"/>')


def chain_body(W=1600, name="chain"):
    """The signal chain: mic -> interface (preamp) -> audio track -> Channel EQ -> Compressor -> mix bus, with the music track and its side chain below."""
    bw, bh = 236, 112
    gap = (W - 60 - 6 * bw) / 5
    xs = [30 + i * (bw + gap) for i in range(6)]
    out = []

    def box(x, y, title, sub, fill_="#fff", tsz=26, ssz=21, name_=name, bold=False):
        o = (f'<rect x="{x:.1f}" y="{y}" width="{bw}" height="{bh}" rx="12" fill="{fill_}" stroke="#000" stroke-width="{4 if bold else 3}"/>'
             + D.t_(x + bw / 2, y + 48, title, tsz, 700) + D.t_(x + bw / 2, y + 84, sub, ssz, 500, "Source Sans 3", fill_="#222"))
        D.lab(name + " box titles", title, tsz, bw - 20)
        D.lab(name + " box subs", sub, ssz, bw - 20)
        return o
    y1, y2, y3 = 40, 250, 420
    row1 = [("MICROPHONE", "10–20 cm, pop filter"), ("INTERFACE", "preamp: input gain"), ("AUDIO TRACK", "record the voice"),
            ("CHANNEL EQ", "high-pass near 80 Hz"), ("COMPRESSOR", "ratio 3:1 or 4:1"), ("MIX BUS", "stereo output")]
    fills = ["#fff", "#fff", "#fff", ACC_LIGHT, ACC_LIGHT, "#fff"]
    for i, ((a, b), f) in enumerate(zip(row1, fills)):
        out.append(box(xs[i], y1, a, b, f, bold=(i == 5)))
        if i < 5:
            out.append(arrow(xs[i] + bw + 6, y1 + bh / 2, xs[i + 1] - 6, y1 + bh / 2))
    out.append(D.t_(30, 24, "VOICE", 22, 700, anchor="start", fill_=ACCENT))
    D.lab(name + " row tags", "VOICE", 22, 120)
    # music track under the audio track, its compressor under the voice compressor
    out.append(box(xs[3], y2, "MUSIC TRACK", "loops or pattern"))
    out.append(box(xs[4], y2, "COMPRESSOR", "side chain: voice", ACC_LIGHT))
    out.append(arrow(xs[3] + bw + 6, y2 + bh / 2, xs[4] - 6, y2 + bh / 2))
    out.append(D.t_(30, y2 - 16, "MUSIC", 22, 700, anchor="start", fill_=ACCENT))
    D.lab(name + " row tags", "MUSIC", 22, 120)
    # dashed side-chain arrow from the voice compressor down to the music compressor
    out.append(arrow(xs[4] + bw / 2, y1 + bh + 4, xs[4] + bw / 2, y2 - 6, dash=True))
    sc = "the voice controls the music"
    out.append(D.t_(xs[4] + bw / 2 - 18, (y1 + bh + y2) / 2 + 8, sc, 22, 600, "Source Sans 3", anchor="end", fill_=ACCENT))
    D.lab(name + " sc", sc, 22, xs[4] + bw / 2 - 18 - 30)
    # music compressor -> up into the bus
    bx_music = xs[5] + bw / 2 - 40
    out.append(f'<polyline points="{xs[4] + bw + 6},{y2 + bh / 2} {bx_music},{y2 + bh / 2}" fill="none" stroke="#000" stroke-width="4"/>')
    out.append(arrow(bx_music, y2 + bh / 2, bx_music, y1 + bh + 6))
    # effects track straight to the bus
    out.append(box(xs[3], y3, "EFFECTS TRACK", "shaker, wind, chime"))
    out.append(D.t_(30, y3 - 16, "EFFECTS", 22, 700, anchor="start", fill_=ACCENT))
    D.lab(name + " row tags", "EFFECTS", 22, 120)
    bx_fx = xs[5] + bw / 2 + 40
    out.append(f'<polyline points="{xs[3] + bw + 6},{y3 + bh / 2} {bx_fx},{y3 + bh / 2}" fill="none" stroke="#000" stroke-width="4"/>')
    out.append(arrow(bx_fx, y3 + bh / 2, bx_fx, y1 + bh + 6))
    cap = "Solid arrows carry audio. The dashed arrow is the side chain: the voice tells the music’s compressor when to turn the music down."
    out.append(D.t_(W / 2, y3 + bh + 56, cap, 23, 500, "Source Sans 3"))
    D.lab(name + " cap", cap, 23, W - 40)
    return padded("".join(out), W, y3 + bh + 76, 14)


METER_TICKS = [0, -3, -6, -9, -12, -18, -24, -30]


def ladder_body(W=1500, name="ladder"):
    """A dBFS meter from -30 to 0: the voice-peak target band (-12 to -6), the clip edge at 0, and the amplitude at each tick (10^(dB/20))."""
    gx, pw = 150, W - 300

    def x(db):
        return gx + (db + 30) / 30 * pw
    top, bot = 130, 230
    out = []
    out.append(f'<rect x="{gx}" y="{top}" width="{pw}" height="{bot - top}" fill="#fff" stroke="#000" stroke-width="4"/>')
    out.append(f'<rect x="{x(-30)}" y="{top}" width="{x(-12) - x(-30):.1f}" height="{bot - top}" fill="#eeeeee" stroke="none"/>')
    out.append(f'<rect x="{x(-12):.1f}" y="{top}" width="{x(-6) - x(-12):.1f}" height="{bot - top}" fill="{ACC_LIGHT}" stroke="{ACCENT}" stroke-width="6"/>')
    out.append(f'<rect x="{x(-1.2):.1f}" y="{top}" width="{x(0) - x(-1.2):.1f}" height="{bot - top}" fill="#000"/>')
    out.append(f'<rect x="{gx}" y="{top}" width="{pw}" height="{bot - top}" fill="none" stroke="#000" stroke-width="4"/>')
    for z0, z1, txt, fl in ((-30, -12, "ROOM TO SPARE", "#000"), (-12, -6, "VOICE PEAK TARGET", ACCENT), (-6, -1.2, "LITTLE HEADROOM", "#000")):
        cx = (x(z0) + x(z1)) / 2
        out.append(D.t_(cx, top - 18, txt, 22, 700, fill_=fl))
        D.lab(name + " zones", txt, 22, x(z1) - x(z0) - 14)
        D.span(name, "zones", txt, 22, cx, lo=gx - 40, hi=gx + pw + 40)
    out.append(D.t_(x(0), bot + 74, "CLIPS", 22, 700, anchor="middle", fill_="#000"))
    for db in METER_TICKS:
        xx = x(db)
        out.append(f'<line x1="{xx:.1f}" y1="{bot}" x2="{xx:.1f}" y2="{bot + 16}" stroke="#000" stroke-width="3"/>')
        lbl = "0" if db == 0 else f"−{-db}"
        out.append(D.t_(xx, bot + 44, lbl, 28, 700))
        D.lab(name + " ticks", lbl, 28, 90)
        am = f"{amp(db):.2f}"
        out.append(D.t_(xx, bot + 138, am, 26, 500, "Source Sans 3", fill_="#222"))
        D.lab(name + " amps", am, 26, 90)
    out.append(D.t_(gx - 50, bot + 44, "dBFS", 22, 700, anchor="end", fill_=ACCENT))
    out.append(D.t_(gx - 50, bot + 138, "× FULL", 22, 700, anchor="end", fill_=ACCENT))
    D.lab(name + " row tags", "× FULL", 22, gx - 60)
    # the half-amplitude bracket from 0 to -6 dBFS
    yb = bot + 94
    out.append(f'<polyline points="{x(0):.1f},{yb - 8} {x(0):.1f},{yb} {x(-6):.1f},{yb} {x(-6):.1f},{yb - 8}" fill="none" stroke="{ACCENT}" stroke-width="4"/>')
    cap = "Every 6 dB down is about half the amplitude: 20 × log10(0.5) = −6.02 dB."
    out.append(D.t_(W / 2, bot + 200, cap, 25, 500, "Source Sans 3"))
    D.lab(name + " cap", cap, 25, W - 30)
    return padded("".join(out), W, bot + 216, 14)


def eq_body(W=700, name="eq"):
    """EQ for voice: a 2nd-order high-pass at 80 Hz plus a small example boost near 3 kHz, on a log frequency axis."""
    gx, gx2 = 104, W - 36
    top, bot = 130, 360
    f0, f1 = 20, 20000
    g0, g1 = -27, 6

    def X(f):
        return gx + (gx2 - gx) * math.log(f / f0) / math.log(f1 / f0)

    def Y(g):
        return bot - (bot - top) * (g - g0) / (g1 - g0)
    out = [f'<rect x="{gx}" y="{top}" width="{gx2 - gx}" height="{bot - top}" fill="#fff" stroke="#000" stroke-width="3"/>']
    out.append(f'<rect x="{gx}" y="{top}" width="{X(HPF_HZ) - gx:.1f}" height="{bot - top}" fill="#eeeeee"/>')
    for f, lbl in ((100, "100 Hz"), (1000, "1 kHz"), (10000, "10 kHz")):
        out.append(f'<line x1="{X(f):.1f}" y1="{top}" x2="{X(f):.1f}" y2="{bot}" stroke="#bbb" stroke-width="2"/>')
        out.append(D.t_(X(f), bot + 34, lbl, 22, 700))
        D.lab(name + " freq", lbl, 22, 100)
    out.append(D.t_(X(20) + 4, bot + 34, "20 Hz", 22, 700, anchor="start"))
    for g in (0, -12, -24):
        out.append(f'<line x1="{gx}" y1="{Y(g):.1f}" x2="{gx2}" y2="{Y(g):.1f}" stroke="{"#000" if g == 0 else "#bbb"}" stroke-width="{3 if g == 0 else 2}" stroke-dasharray="{"" if g == 0 else "6 6"}"/>')
        lbl = "0 dB" if g == 0 else f"−{-g} dB"
        out.append(D.t_(gx - 12, Y(g) + 8, lbl, 22, 700, anchor="end"))
        D.lab(name + " gain", lbl, 22, gx - 14)
    pts = []
    n = 160
    for i in range(n + 1):
        f = f0 * (f1 / f0) ** (i / n)
        pts.append((X(f), Y(max(g0 + 0.3, eq_gain_db(f)))))
    out.append(f'<polyline points="{" ".join(f"{a:.1f},{b:.1f}" for a, b in pts)}" fill="none" stroke="{ACCENT}" stroke-width="7" stroke-linejoin="round" stroke-linecap="round"/>')
    px, py = X(HPF_HZ), Y(hpf_gain_db(HPF_HZ))
    out.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="10" fill="#fff" stroke="#000" stroke-width="4"/>')
    l1 = "high-pass at 80 Hz"
    out.append(D.t_(px + 22, py + 40, l1, 22, 700, anchor="start"))
    D.lab(name + " notes", l1, 22, 260)
    l1b = "(−3 dB at the corner)"
    out.append(D.t_(px + 22, py + 66, l1b, 20, 500, "Source Sans 3", anchor="start", fill_="#222"))
    D.lab(name + " notes", l1b, 20, 260)
    bx, by = X(PRES_HZ), Y(eq_gain_db(PRES_HZ))
    out.append(f'<circle cx="{bx:.1f}" cy="{by:.1f}" r="10" fill="#fff" stroke="#000" stroke-width="4"/>')
    l2 = "small presence boost"
    out.append(D.t_(bx, by - 60, l2, 22, 700, anchor="middle"))
    D.lab(name + " notes", l2, 22, 300)
    l2b = "(example: +2 dB)"
    out.append(D.t_(bx, by - 34, l2b, 20, 500, "Source Sans 3", anchor="middle", fill_="#222"))
    D.lab(name + " notes", l2b, 20, 300)
    l3 = "RUMBLE"
    out.append(D.t_((gx + X(HPF_HZ)) / 2, top + 32, l3, 20, 700, fill_="#555"))
    D.lab(name + " notes", l3, 20, X(HPF_HZ) - gx - 6)
    cap = "Start with small moves. Set the real numbers by ear."
    out.append(D.t_((gx + gx2) / 2, bot + 76, cap, 22, 500, "Source Sans 3"))
    D.lab(name + " cap", cap, 22, gx2 - gx)
    return padded("".join(out), W, bot + 92, 14)


def comp_body(W=1000, name="comp"):
    """A compressor's transfer curve at 4:1 with the threshold at -17 dB: 1:1 below it, 1 dB out for 4 dB in above it."""
    gx, top = 120, 40
    S = 7.0                                   # units per dB
    lo, hi = -40, 0
    side = (hi - lo) * S

    def X(db):
        return gx + (db - lo) * S

    def Y(db):
        return top + side - (db - lo) * S
    out = [f'<rect x="{gx}" y="{top}" width="{side}" height="{side}" fill="#fff" stroke="#000" stroke-width="3"/>']
    for db in (-30, -20, -10):
        out.append(f'<line x1="{X(db):.1f}" y1="{top}" x2="{X(db):.1f}" y2="{top + side}" stroke="#ddd" stroke-width="2"/>')
        out.append(f'<line x1="{gx}" y1="{Y(db):.1f}" x2="{gx + side}" y2="{Y(db):.1f}" stroke="#ddd" stroke-width="2"/>')
    for db in (-40, -30, -20, -10, 0):
        lbl = "0" if db == 0 else f"−{-db}"
        out.append(D.t_(X(db), top + side + 34, lbl, 22, 700))
        out.append(D.t_(gx - 12, Y(db) + 8, lbl, 22, 700, anchor="end"))
        D.lab(name + " ticks", lbl, 22, 60)
    out.append(f'<line x1="{X(lo)}" y1="{Y(lo)}" x2="{X(hi)}" y2="{Y(hi)}" stroke="#999" stroke-width="4" stroke-dasharray="12 9"/>')
    o_hi = out_level(0, EX_THRESH, EX_RATIO)
    out.append(f'<polyline points="{X(lo):.1f},{Y(lo):.1f} {X(EX_THRESH):.1f},{Y(EX_THRESH):.1f} {X(hi):.1f},{Y(float(o_hi)):.1f}" fill="none" stroke="{ACCENT}" stroke-width="8" stroke-linejoin="round"/>')
    out.append(f'<circle cx="{X(EX_THRESH):.1f}" cy="{Y(EX_THRESH):.1f}" r="11" fill="#fff" stroke="#000" stroke-width="4"/>')
    l1 = f"−{-EX_THRESH} dB"
    out.append(D.t_(X(EX_THRESH) + 18, Y(EX_THRESH) + 48, l1, 20, 700, anchor="start"))
    D.lab(name + " notes", l1, 20, gx + side - X(EX_THRESH) - 24)
    out.append(D.t_(X(EX_THRESH) + 18, Y(EX_THRESH) + 74, "threshold", 20, 700, anchor="start"))
    D.lab(name + " notes", "threshold", 20, gx + side - X(EX_THRESH) - 24)
    vi = VOICE_PEAK
    vo = float(out_level(vi, EX_THRESH, EX_RATIO))
    out.append(f'<line x1="{X(vi):.1f}" y1="{Y(vi):.1f}" x2="{X(vi):.1f}" y2="{Y(vo):.1f}" stroke="#000" stroke-width="5"/>')
    out.append(f'<circle cx="{X(vi):.1f}" cy="{Y(vi):.1f}" r="9" fill="#999" stroke="#000" stroke-width="3"/>')
    out.append(f'<circle cx="{X(vi):.1f}" cy="{Y(vo):.1f}" r="11" fill="{ACCENT}" stroke="#000" stroke-width="4"/>')
    l2 = f"{int(vi - vo)} dB less"
    out.append(D.t_(X(vi) - 18, Y(vi) - 16, l2, 22, 700, anchor="end"))
    D.lab(name + " notes", l2, 22, X(vi) - 18 - gx)
    out.append(D.t_(gx + side - 14, Y(-33), "4:1 above", 20, 700, anchor="end", fill_=ACCENT))
    out.append(D.t_(gx + side - 14, Y(-33) + 26, "the threshold", 20, 700, anchor="end", fill_=ACCENT))
    D.lab(name + " notes", "the threshold", 20, 200)
    out.append(D.t_(gx + side / 2, top + side + 74, "INPUT LEVEL (dB)", 22, 700, fill_=ACCENT))
    out.append(D.t_(34, top + side / 2, "OUTPUT (dB)", 22, 700, fill_=ACCENT, extra=f'transform="rotate(-90 34 {top + side / 2})"'))
    cap = "Dashed: no compression"
    out.append(D.t_(gx + side / 2, top + side + 112, cap, 23, 500, "Source Sans 3"))
    D.lab(name + " cap", cap, 23, side)
    return padded("".join(out), gx + side + 30, top + side + 126, 14)


DUCK_ROWS = ["VOICE", "MUSIC BED", "SHAKER", "WIND", "CHIME"]


def duck_body(W=1600, name="duck"):
    """The 20-second timeline at 120 BPM: ten bars of 2 s; the voice from 4 to 16 s; the music bed ducked 8 dB over half a second before the voice and back after it;
    shaker, wind and a chime at the end."""
    gx = 262
    pw = W - gx - 50
    S = pw / ID_SECONDS
    out = []

    def X(s):
        return gx + float(s) * S
    # bars and seconds
    out.append(D.t_(gx - 20, 38, "BAR", 22, 700, anchor="end", fill_=ACCENT))
    out.append(D.t_(gx - 20, 92, "SECONDS", 22, 700, anchor="end", fill_=ACCENT))
    D.lab(name + " rows", "SECONDS", 22, gx - 30)
    for b in range(EX_BARS):
        x0 = X(b * float(EX_BAR_S))
        out.append(f'<rect x="{x0 + 2:.1f}" y="14" width="{float(EX_BAR_S) * S - 4:.1f}" height="36" rx="6" fill="{ACC_LIGHT if b % 2 == 0 else "#fff"}" stroke="#000" stroke-width="2.5"/>')
        out.append(D.t_(x0 + float(EX_BAR_S) * S / 2, 41, str(b + 1), 26, 700))
    for s in range(0, ID_SECONDS + 1, 2):
        out.append(D.t_(X(s), 92, str(s), 24, 500, fill_="#444"))
    rows_y = [120 + i * 92 for i in range(5)]
    rh = 80
    for i, (nm, y) in enumerate(zip(DUCK_ROWS, rows_y)):
        out.append(f'<rect x="{gx}" y="{y}" width="{pw}" height="{rh}" fill="{"#fff"}" stroke="#bbb" stroke-width="2"/>')
        out.append(D.t_(gx - 20, y + rh / 2 + 9, nm, 26, 700, anchor="end"))
        D.lab(name + " rows", nm, 26, gx - 30)
    # voice waveform
    y, cy = rows_y[0], rows_y[0] + rh / 2
    i = 0
    s = float(VOICE_IN)
    while s < float(VOICE_OUT) - 0.1:
        word_gap = (i % 11) in (9, 10)
        h = 5 if word_gap else 10 + 26 * abs(math.sin(i * 0.93)) * (0.55 + 0.45 * abs(math.sin(i * 0.27 + 1)))
        out.append(f'<rect x="{X(s) + 1:.1f}" y="{cy - h:.1f}" width="{0.2 * S - 4:.1f}" height="{2 * h:.1f}" rx="3" fill="#000"/>')
        s += 0.2
        i += 1
    # music bed: height proportional to amplitude; the duck is DUCK_DB dB lower
    y = rows_y[1]
    bot = y + rh - 8
    hf = rh - 22
    hd = hf * amp(-DUCK_DB)
    pts = [(X(0), bot), (X(0), bot - hf), (X(VOICE_IN - DUCK_RAMP), bot - hf), (X(VOICE_IN), bot - hd), (X(VOICE_OUT), bot - hd), (X(VOICE_OUT + DUCK_RAMP), bot - hf),
           (X(18), bot - hf), (X(18), bot)]
    out.append(f'<polygon points="{" ".join(f"{a:.1f},{b:.1f}" for a, b in pts)}" fill="{ACC_LIGHT}" stroke="#000" stroke-width="4" stroke-linejoin="round"/>')
    mx = X(10)
    out.append(f'<line x1="{mx:.1f}" y1="{bot - hf:.1f}" x2="{mx:.1f}" y2="{bot - hd:.1f}" stroke="{ACCENT}" stroke-width="4" stroke-dasharray="7 5"/>')
    out.append(f'<line x1="{X(5):.1f}" y1="{bot - hf:.1f}" x2="{mx:.1f}" y2="{bot - hf:.1f}" stroke="{ACCENT}" stroke-width="3" stroke-dasharray="7 5"/>')
    lbl = f"ducked {DUCK_DB} dB"
    out.append(D.t_(mx + 14, bot - (hf + hd) / 2 + 8, lbl, 22, 700, anchor="start", fill_=ACCENT))
    D.lab(name + " notes", lbl, 22, 180)
    # shaker: a dot on every beat of bars 1-2 and bar 9
    y = rows_y[2]
    for k in range(0, 8):
        out.append(f'<circle cx="{X(k * 0.5):.1f}" cy="{y + rh / 2:.1f}" r="9" fill="{ACCENT}" stroke="#000" stroke-width="3"/>')
    for k in range(0, 4):
        out.append(f'<circle cx="{X(16 + k * 0.5):.1f}" cy="{y + rh / 2:.1f}" r="9" fill="{ACCENT}" stroke="#000" stroke-width="3"/>')
    # wind: a swell that fades in over bars 1-2 and out under the voice
    y = rows_y[3]
    cy = y + rh / 2
    out.append(f'<path d="M {X(0):.1f} {cy:.1f} Q {X(2.4):.1f} {cy - 36:.1f} {X(6):.1f} {cy:.1f} Q {X(2.4):.1f} {cy + 36:.1f} {X(0):.1f} {cy:.1f} Z" fill="#dddddd" stroke="#000" stroke-width="3"/>')
    # chime at 18 s with rings and a short tail
    y = rows_y[4]
    cy = y + rh / 2
    cx = X(18)
    out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="11" fill="{ACCENT}" stroke="#000" stroke-width="3"/>')
    out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="23" fill="none" stroke="#000" stroke-width="3"/>')
    for k, hh in enumerate((26, 20, 14, 9, 5)):
        out.append(f'<line x1="{X(18.7 + k * 0.4):.1f}" y1="{cy - hh:.1f}" x2="{X(18.7 + k * 0.4):.1f}" y2="{cy + hh:.1f}" stroke="#000" stroke-width="5" stroke-linecap="round"/>')
    # cue lines and their labels
    yb = rows_y[4] + rh
    for s, (l1, row, anc, dx) in ((float(VOICE_IN), ("voice in · bar 3 beat 1 · 4 s", 0, "middle", 0)), (float(VOICE_OUT), ("voice out · bar 9 beat 1 · 16 s", 0, "end", 8)),
                                  (18.0, ("chime and hit · bar 10 beat 1 · 18 s", 1, "middle", 0))):
        out.append(f'<line x1="{X(s):.1f}" y1="{rows_y[0] - 6}" x2="{X(s):.1f}" y2="{yb + 14 + row * 38}" stroke="#000" stroke-width="3" stroke-dasharray="9 7"/>')
        ty = yb + 38 + row * 38
        out.append(D.t_(X(s) + dx, ty, l1, 23, 700, "Source Sans 3", anchor=anc))
        D.lab(name + " cues", l1, 23, 420)
        D.span(name, f"cues{row}", l1, 23, X(s) + dx, anchor=anc, lo=2, hi=W - 2)
    cap = "Example at 120 BPM: 10 bars of 2 seconds. The music falls half a second before the voice and rises half a second after it."
    out.append(D.t_(W / 2, yb + 120, cap, 23, 500, "Source Sans 3"))
    D.lab(name + " cap", cap, 23, W - 40)
    return padded("".join(out), W, yb + 136, 14)


def hero_body():
    """The owner's pre-made art (art/hero.png, used whole). The viewBox only trims fully transparent margin: the art's own pixels
    (x 121-1279, y 162-1311 of 1400) stay at least 40 units inside it, which --check proves from the file."""
    return (f'<image href="../art/hero.png" x="{-HX}" y="{-HY}" width="1400" height="1400"/>', HW, HH)


HX, HY, HW, HH = 60, 100, 1280, 1270

DRAWINGS = {"hero": hero_body, "duck": lambda: duck_body(1600, "duck deck"), "chain": lambda: chain_body(1600, "chain deck"),
            "ladder": lambda: ladder_body(1500, "ladder deck"), "eq": lambda: eq_body(700, "eq deck"), "comp": lambda: comp_body(1000, "comp deck")}
DRAWING_PX = {"hero": 1340, "duck": 2000, "chain": 2000, "ladder": 2000, "eq": 1100, "comp": 1300}
SIDE = {"duck": ["Voice in at 4 s, out at 16 s", "Music dips 8 dB while the voice speaks"],
        "chain": ["Mic, interface, track, EQ, compressor, bus", "The music joins the same bus"],
        "ladder": ["−6 dB is about half the amplitude", "Voice peaks: about −12 to −6 dBFS"],
        "eq": ["High-pass near 80 Hz removes rumble", "Start with small moves"],
        "comp": ["Ratio 3:1 or 4:1 as a starting point", "Loudest words down about 3 to 6 dB"]}
# extra drawings used on pages only, rendered alone on a transparent ground by --check as well
PAGE_DRAWINGS = {"duck-page": lambda: duck_body(1600, "duck page"), "chain-page": lambda: chain_body(1600, "chain page"),
                 "ladder-page": lambda: ladder_body(1500, "ladder page"), "eq-page": lambda: eq_body(700, "eq page"), "comp-page": lambda: comp_body(1000, "comp page")}


def label_extras():
    duck_body(1600, "duck page")
    chain_body(1600, "chain page")
    ladder_body(1500, "ladder page")
    eq_body(700, "eq page")
    comp_body(1000, "comp page")


# ================================================================ intro deck: (class, kind, title, body, speaker notes)
SLIDES = [
    (1, "title", "Holiday Radio Ident", "Record it. Build it. Duck it.",
     "Class 1, the first minute. No audio is included in this deck. Open with the idea: you will make a 20-second radio ident for an invented winter station in Logic Pro, with a voice, a music bed "
     "and sound effects. Students plan the timing, record the voice, clean it up with EQ and compression, and lower the music under the words. Nobody needs to read music, and no song is used."),
    (1, "listen", "Hear the ident", "Think, then share|Teacher: read aloud, no audio plays. Wind blows and bells shake on a steady beat. A warm voice names a station while the music dips. "
     "Then the music swells and a chime ends it.|What do you hear first?|What happens to the music when the voice starts?|"
     "What is the last sound, and why is it there?",
     "Read the scene aloud slowly and ask the three questions. Take a few answers. Nothing is played from a speaker. Students will name the wind, the shaker, the voice and the chime, and some will notice "
     "the music move. Write their words on the board. The project turns each idea into a tool with a number attached: a timeline, a recording level, a filter, a compressor and a duck."),
    (1, "bullets", "What is the Holiday Radio Ident project?", "Make a 20-second ident for an invented station|Record a voice and build a music bed with sound effects|"
     "Clean up the voice with EQ and compression|Duck the music under the voice, then mix",
     "The project in four lines. Every student makes a radio ident of 15 to 30 seconds, with 20 seconds as the worked example, in Logic Pro. It has a voice that reads a short original script, an original music bed "
     "and sound effects. The voice is cleaned up with a high-pass filter and a compressor, and the music is ducked under it. There is no melody to learn and no audio ships: students make every sound."),
    (1, "days", "Three classes", "",
     "The shape of the project. Class 1: hook, the timing math, the script and the first recording. Class 2: build the music bed and effects, then EQ and compression. Class 3: ducking, mix, bounce, present "
     "and reflect. The badge on this slide reads Classes 1 to 3 because it covers all three. With two classes, do the plan, script, recording and bed in Class 1 and the rest in Class 2; with four, add a day "
     "for presentations. Hand out the tempo table, the script page and the cue sheet now."),
    (1, "pic", "Twenty seconds, five layers", "duck",
     f"Class 1. This is the timeline of the worked example at 120 BPM: ten bars of 2 seconds, with the bar numbers along the top. The voice runs from 4 to 16 seconds. The music bed falls 8 dB over half a second "
     f"before the voice and rises again after it. A shaker plays on the beat, wind fades in, and a chime lands on the final hit at 18 seconds. Ask which layer they would add or remove. "
     f"The full cue sheet is on page {pg('cues')} and the duck on page {pg('duck')}."),
    (1, "bullets", "The math: tempo = 12 × bars", "One bar of 4/4 lasts 240 ÷ BPM seconds|20 seconds should be a whole number of bars|Tempo = 12 × bars|96, 120 or 144 BPM: 8, 10 or 12 bars",
     f"Class 1, the key idea. In 4/4 there are four beats in a bar, so one bar lasts 240 divided by the tempo, in seconds. Twenty seconds is 20 divided by that, which is the tempo divided by 12 bars. "
     f"That is a whole number only when the tempo is 12 times a whole number: 96 BPM gives 8 bars, 120 gives 10 and 144 gives 12. At 100 BPM it is 8.3333 bars, so the ident would end in the middle of a bar. "
     f"The tempo table is on page {pg('tempo')}, and the script page (page {pg('script')}) shows how many words fit: about 150 words per minute is 2.5 words per second."),
    (1, "pic", "From mouth to mix", "chain",
     f"Class 1. The signal chain: the microphone, the interface with its preamp, the audio track, Channel EQ, a compressor and the mix bus. The music track and the effects track join the same bus, and the "
     f"dashed arrow is the side chain, which the duck uses later. Talk about distance: 10 to 20 cm from the microphone, with a pop filter in front, and a steady position. The setup checklist is on page {pg('chain')}."),
    (1, "pic", "Levels: the dB ladder", "ladder",
     f"Class 1. A digital recording cannot go above 0 dBFS, so every real level is a negative number. Aim for the loudest words of the voice to peak around −12 to −6 dBFS, which leaves room for a surprise. "
     f"Every 6 dB down is about half the amplitude: 20 × log10(0.5) = −6.02 dB. Students set the gain at the interface while reading the loudest line. The ladder and a place to record the peak are on page {pg('ladder')}."),
    (2, "steps", "Build it in Logic", "Set the tempo; keep 4/4|Build the bed from Logic’s own loops or a pattern|Add a shaker, wind and a chime on the beats|Put EQ and a compressor on the voice|Save the project and check the levels",
     f"Class 2. Demonstrate on the projector. Set the tempo to 96, 120 or 144 BPM and keep 4/4. Open the Loop Browser, find a drum, bass or pad loop and add a shaker. Place a wind sound at the start and a chime for the "
     f"final hit. Menu names and button places move between Logic versions; the quick reference on page {pg('logicref')} hedges where they do, and says which tools to use only if your version has them. "
     f"The bed plan is on page {pg('bed')}. Ducking and the mix wait for Class 3."),
    (2, "pic", "EQ for the voice", "eq",
     f"Class 2. A high-pass filter lets high frequencies pass and removes the low ones, where rumble and breath thumps live. Start near 80 Hz. Then a small boost for presence, here an example of 2 dB near 3 kHz, "
     f"and the advice is to start with small moves and listen. These are example values, not rules. The EQ and compression page is page {pg('eqcomp')}."),
    (2, "pic", "Compression for the voice", "comp",
     f"Class 2. A compressor turns down the loudest parts so that the voice is more even. At a ratio of 4:1, every 4 dB above the threshold becomes 1 dB. If the loudest words are 8 dB over the threshold, "
     f"the compressor lowers them by 8 × (1 − 1/4) = 6 dB. A ratio of about 3:1 or 4:1 and about 3 to 6 dB of reduction on the loudest words are starting points, not rules; the gain reduction meter shows the amount. "
     f"The arithmetic table is on page {pg('eqcomp')}."),
    (3, "bullets", "Ducking: two ways", "Sidechain compression: the voice turns the music down|Automation: draw the music down and up yourself|Start with 6 to 12 dB and a half-second ramp|Check that every word is clear",
     f"Class 3. Ducking is lowering the music while the voice speaks. With sidechain compression, a compressor on the music track listens to the voice track and turns the music down by itself. With automation, "
     f"students draw the music volume down about half a second before the voice and back up after it. Both work; the automated duck is easy to see and edit. A depth of 6 to 12 dB is a starting point. "
     f"The ducking page is page {pg('duck')}, and the cue sheet is on page {pg('cues')}."),
    (3, "check", "What you turn in", "Bounced .mp3 or .wav, 15 to 30 seconds long|Zipped .logicx project|Named: Your Name – Ident|Tempo table work, script and cue sheet|"
     "Reflection page|Rubric self-score and three questions",
     "Class 3. The submission checklist, shortened to fit the slide. Show where students hand in. The file name is Your Name, then Ident. Check the length before students bounce: "
     "the bounce should run the whole ident, which is 20 seconds at 96, 120 and 144 BPM when the plan uses 8, 10 or 12 bars."),
    (3, "rubric", "How it’s scored", "",
     "The rubric: five categories, each scored 1 to 5, for a total out of 25. Students score themselves first; the final grade is the average of their score and yours. "
     "The slide reads the 5 column of each category aloud. Hand out the rubric page so students can self-score before they present."),
    (3, "bullets", "Presentation day", "Play your ident from the top|Point out the voice, the bed, the effects and the duck|Your three questions for classmates|Answer at least 2 of each classmate’s questions",
     "Class 3, presentations. Each student plays the ident and points out the voice, the music bed, the effects and the duck as they arrive, with their bar numbers. Students write three "
     "questions they want classmates to answer, and answer at least two of each classmate's. Ask the class whether every word was clear and when they noticed the music move."),
    (3, "closer", "One last thing…", "Plan the time.|Record it clean.|Shape it gently.|Then let the voice lead.",
     "Close with the listening day: play an ident and ask the class whether they could hear every word. A duck that nobody notices is a duck that was well planned and well timed. "
     "Ask a few students which tool did the most for the voice. No audio is included in this resource; the sounds are the students' own."),
]
SHOTS1 = [("pacing", "Pacing guide", "3 class periods, slide by slide"), ("duck", "Ducking page", "Two ways, with depth numbers"),
          ("tempo", "Tempo table", "Seconds, bars and words")]
SHOTS2 = [1, 5, 7, 11, 12, 6]
SHOTS3 = [("tempo", "Tempo table"), ("script", "Scripts"), ("chain", "Signal chain"), ("ladder", "dB ladder"), ("eqcomp", "EQ and compression"), ("cues", "Cue sheet"),
          ("example", "Worked example"), ("rubric", "Rubric")]
PREVIEW_PICKS = ["pacing", "chain", "duck", "rubric"]

COVER_A = "Record it, build it, duck it"
COVER_C = "Logic Pro · EQ · Compression · Ducking"
PDF_COVER = dict(a=26, b=42, c=15, art=5.0)
SQ_COVER = dict(a=36, b=140, c=27, art=420, gap=20)
SQ_B_LINES = ["Holiday Radio", "Ident"]
SQ_SUB = "3 class periods · voice, music bed, effects · timing math"
SQ_HEADS = {1: ("Ready to teach Monday", 76, "Pacing, tempo table, ducking page and the /25 rubric in one PDF", 28),
            2: ("Intro deck included", 76, f"{len(SLIDES)} editable slides (.pptx + PDF) with speaker notes on every slide", 28),
            3: ("Everything inside", 72, "Scripts, signal chain, dB ladder, cue sheet and worked example", 28)}
SQ_BANDS = {1: "Voice <em>·</em> music bed <em>·</em> effects <em>·</em> ducking",
            2: "Signal chain <em>·</em> dB ladder <em>·</em> EQ",
            3: f"{len(PLAN)} pages <em>·</em> US Letter PDF <em>·</em> no audio included"}


# ================================================================ small page helpers
CSS_CC = ("<style>table.cc td { text-align: center; padding: 2pt 3pt; font-size: 9.4pt; line-height: 1.15; } table.cc th { text-align: center; font-size: 9pt; } "
          "table.cc td.l { text-align: left; } table.cc tr.hi td { background: #eef5fb; }</style>")


def howto_page(n, wm=False):
    parts = [("Teacher pages", "howto", "example2", "How to use, overview, setup, pacing, teacher notes, Logic quick reference, worked example (2 pages)"),
             ("Student pages", "tempo", "reflect", "Tempo table, scripts, signal chain, dB ladder, bed plan, EQ and compression, ducking, cue sheet, mix checklist, "
              "project sheet (3 pages), rubric, vocabulary, feedback planner, reflection page"),
             ("Intro deck (separate file)", None, None, f"{len(SLIDES)} slides, .pptx + PDF, speaker notes on every slide")]
    trs = "".join(f"<tr><td><b>{a}</b></td><td style='white-space:nowrap'>{('pages ' + str(D.IX(f)) + '–' + str(D.IX(l))) if f else 'deck'}</td>"
                  f"<td>{u}</td></tr>" for a, f, l, u in parts)
    inner = (f'<div class="cols"><div>'
             f'{D.H2("What this is", True)}'
             f'<p style="font-size:12pt;line-height:1.45">A {CLASSES}-class-period radio ident project for high school music technology. Every '
             f'student makes a short ident of 15 to 30 seconds for an invented station: a voice, an original music bed and sound effects, recorded, cleaned up with EQ and compression, and mixed with the music ducked under the words. '
             f'Students plan the timing with simple arithmetic, present the result and reflect on it. It is an original Hudson Beat project.</p>'
             f'{D.H2("Quick start")}<ol>'
             f'<li style="margin-bottom:5pt">Read the pacing guide (page {D.IX("pacing")}) and the teacher notes (pages {D.IX("tn1")}–{D.IX("tn2")}).</li>'
             f'<li style="margin-bottom:5pt">Look at the tempo table, scripts, signal chain and dB ladder (pages {D.IX("tempo")}–{D.IX("ladder")}) and the setup (page {D.IX("setup")}).</li>'
             f'<li style="margin-bottom:5pt">Print the student pages (pages {D.IX("tempo")}–{D.IX("reflect")}), one set per student.</li>'
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
             f'<li><b>Pace:</b> Class 1 plan, script and recording; Class 2 bed, EQ and compression; Class 3 duck, mix and presentations (page {D.IX("pacing")}, which also shows two and four periods).</li>'
             f'<li><b>Grading:</b> the rubric, /{RUBRIC_TOTAL}, the average of the student’s and your score (page {D.IX("rubric")}).</li></ul>'
             f'<div class="box" style="margin-top:6pt"><span class="k">In one sentence</span><p style="margin:0;font-size:12pt">Students learn that '
             f'a clear voice spot is planned: a tempo that fits the time into whole bars, a script that fits its seconds, a clean recording, gentle processing and music that steps aside for the words.</p></div>'
             f'<p class="small" style="margin-top:6pt">Logic Pro is a product of Apple Inc. This resource is not affiliated with Apple.</p>'
             f'</div></div>')
    return D.page("How to use this resource", "START HERE", "Teacher", inner, n, key="howto")


def overview_page(n, wm=False):
    inner = (f'<div class="cols"><div>'
             f'<div class="box inv" style="margin-bottom:6pt"><span class="k">The project in one line</span><p style="margin:0;font-size:12pt">'
             f'<b>{TITLE}</b> · Voice, music bed and effects · Logic Pro<br>One invented station, twenty seconds, a voice that is always clear.</p></div>'
             f'{D.H2("What students make")}'
             f'<p style="font-size:12.2pt;line-height:1.48">An ident of 15 to 30 seconds, built in Logic Pro: a voice that reads a script of about 24 to 30 words, an original music bed that fills 8, 10 or 12 bars, '
             f'and at least two sound effects such as a sleigh-bell-like shaker, wind or a door chime. The voice is recorded with a pop filter and levels that peak around −12 to −6 dBFS, cleaned up with a high-pass filter and '
             f'a gentle compressor, and the music is ducked under it. Students hand in a bounced file and the zipped .logicx project, plus their plans and a reflection, '
             f'then play the ident and take questions.</p>'
             f'{D.H2("What this project reinforces")}<p style="font-size:12pt;line-height:1.5">{TN_REINFORCES}</p>'
             f'{D.H2("Standards")}<p style="font-size:11.4pt">Supports the National Core Arts Standards for Music (Music Technology, high school): generating '
             f'and developing ideas (MU:Cr1.1, MU:Cr2.1), presenting work (MU:Pr6.1) and responding to it (MU:Re7.2).</p>'
             f'</div><div>'
             f'{D.H2("Goals", True)}<ul>' + "".join(f"<li style='font-size:12pt;line-height:1.45'>{g}</li>" for g in GOALS) + '</ul>'
             f'{D.H2("About the theme")}<div class="box acc-b" style="padding:5pt 9pt"><p style="margin:0 0 3pt;font-size:10.2pt;line-height:1.36">{THEME}</p>'
             f'<p style="margin:0;font-size:10.2pt;line-height:1.36">{BUILD_NOTE}</p></div>'
             f'<div class="box" style="margin-top:6pt;padding:5pt 9pt"><span class="k">At a glance</span><p style="margin:0;font-size:10.2pt;line-height:1.38"><b>Grades</b> {GRADES_TEXT}, music technology or music production · '
             f'<b>Length</b> {CLASSES} class periods (two and four also shown) · <b>Software</b> Logic Pro · <b>You supply</b> Macs with Logic Pro, headphones, a microphone and pop filter (or a quiet corner and a shared one) and a place to hand in files · '
             f'<b>Assessment</b> rubric, 5 categories scored 1–5, /{RUBRIC_TOTAL} (page {D.IX("rubric")})</p></div>'
             f'</div></div>')
    return D.page("Project overview", "OVERVIEW", "Radio ident project", inner, n, key="overview")


def setup_page(n, wm=False):
    inner = (f'<style>.sb p, .sb li {{ font-size: 11.6pt; line-height: 1.44; margin-bottom: 5pt; }}</style><div class="cols"><div class="big sb">'
             f'{D.H2("You need", True)}<ul>'
             f'<li><b>A Mac with Logic Pro</b> for each student, and <b>headphones</b>.</li>'
             f'<li><b>A microphone and a pop filter</b>, shared if you must. A quiet corner with soft surfaces beats a loud room. A laptop’s built-in microphone will do for practice.</li>'
             f'<li><b>A place to hand in</b> the .mp3 or .wav files, the zipped .logicx and the reflection.</li>'
             f'<li><b>The tempo table, scripts, dB ladder and cue sheet</b>, printed (pages {D.IX("tempo")}–{D.IX("ladder")} and {D.IX("cues")}), or shown on the projector.</li>'
             f'<li><b>Printed student pages</b>, one set each (pages {D.IX("tempo")}–{D.IX("reflect")}).</li></ul>'
             f'{D.H2("Before Class 1")}'
             + "".join(D.chk(c, 13, "font-size:11.6pt;margin-bottom:7pt") for c in [
                 f"Read the tempo table (page {D.IX('tempo')}) so you can answer ‘how many bars is 20 seconds?’ at 96, 120 and 144 BPM.",
                 f"Test a microphone in Logic Pro on one computer, and read a line while watching the meter (page {D.IX('ladder')}).",
                 f"Open Logic Pro on a student computer and check which tools your version has: the Loop Browser, Session Players, Channel EQ, Compressor with a Side Chain menu (see page {D.IX('logicref')}).",
                 f"Read the worked example (pages {D.IX('example')}–{D.IX('example2')})."]) +
             f'</div><div class="big sb">'
             f'{D.H2("What to watch", True)}'
             f'<p style="font-size:11.4pt">Watch for a voice that clips or is much too quiet, a microphone that moves between takes, a bed that is already loud under the words, and a duck that starts late or snaps back. {TN_NOTE}</p>'
             f'<div class="box acc-b" style="margin-top:2pt"><span class="k">Ideas for the room</span><ul style="margin:0">'
             f'<li style="font-size:11.2pt">Ask while students work: what does this setting change? Could you hear every word?</li>'
             f'<li style="font-size:11.2pt">Use only loops and sounds that come with Logic, and no existing songs, jingles or station names. Students invent a station and do not use real call letters.</li>'
             f'<li style="font-size:11.2pt">A student who is stuck can build the voice, a short bed and the final chime only: those three already make an ident.</li></ul></div>'
             f'{D.H2("The voice")}'
             f'<div class="box"><p style="margin:0;font-size:10.8pt;line-height:1.4">{VOICE_NOTE}</p></div>'
             f'<div class="box" style="margin-top:6pt"><span class="k">Keep the volume moderate</span><p style="margin:0;font-size:11pt;line-height:1.4">'
             f'Students listen to their own voice over and over in headphones. Tell them to start low and check the final mix at a normal level.</p></div>'
             f'</div></div>')
    return D.page("Setup and what to watch", "SETUP", "Teacher", inner, n, key="setup")


# ================================================================ the student pages
def tempo_a_rows():
    rows = []
    for bpm in TEMPOS:
        w = is_whole(bpm)
        b, e = ("<b>", "</b>") if w else ("", "")
        c = id_bars(bpm)
        cs = fmt(c) if w else dec(c, 4)
        hi = ' class="hi"' if w else ''
        rows.append(f"<tr{hi}><td>{b}{bpm}{e}</td><td>{dec(spb(bpm), 3)}</td><td>{dec(bar_len(bpm), 3)}</td><td>{b}{cs}{e}</td>"
                    f"<td>{b}{'Yes' if w else 'No'}{e}</td></tr>")
    return "".join(rows)


def len_cell(bpm, secs):
    c = id_bars(bpm, secs)
    return f"<td><b>{fmt(c)}</b></td>" if c.denominator == 1 else f"<td>{dec(c, 2)}</td>"


def len_rows():
    return "".join(f"<tr><td><b>{L} s</b></td><td>{240 // L if 240 % L == 0 else fmt(Fraction(240, L))} × bars</td>" + "".join(len_cell(b, L) for b in LEN_TEMPOS) + "</tr>" for L in LENGTHS)


def tempo_page(n, wm=False):
    inner = (CSS_CC +
             f'<p style="margin:0 0 4pt;font-size:10.2pt;line-height:1.36">Step 1: plan the ident. In 4/4 there are 4 beats in a bar. These formulas turn a tempo into seconds and bars. '
             f'Every number below is computed, so you can check your own arithmetic against it.</p>'
             f'<div class="cols" style="gap:10pt;align-items:flex-start"><div class="box acc-b" style="padding:5pt 9pt;flex:1.15"><span class="k">The formulas (4/4)</span>'
             f'<p style="margin:0 0 2pt;font-size:9.8pt"><b>Seconds per beat</b> = 60 ÷ BPM</p><p style="margin:0 0 2pt;font-size:9.8pt"><b>Seconds per bar</b> = 240 ÷ BPM</p>'
             f'<p style="margin:0 0 2pt;font-size:9.8pt"><b>Bars in 20 seconds</b> = 20 ÷ (240 ÷ BPM) = BPM ÷ 12</p>'
             f'<p style="margin:0 0 2pt;font-size:9.8pt"><b>Tempo = 12 × bars</b>, when 20 seconds is a whole number of bars</p>'
             f'<p style="margin:0 0 2pt;font-size:9.8pt"><b>A position is at</b> ((bar − 1) × 4 + (beat − 1)) × 60 ÷ BPM seconds</p>'
             f'<p style="margin:0;font-size:9.8pt"><b>Example:</b> 120 BPM: 240 ÷ 120 = 2 s per bar, 20 ÷ 2 = 10 bars, and 120 ÷ 12 = 10 too.</p></div>'
             f'<div class="box" style="padding:5pt 9pt;flex:1"><span class="k">Rounding rules</span><p style="margin:0;font-size:9.2pt;line-height:1.32">Seconds per beat and per bar to 3 decimals, '
             f'bars to 4 decimals in the first table and to 2 in the second; a 5 rounds up. So 240 ÷ 144 = 1.667 seconds per bar (the exact value is 5/3), and 20 ÷ (5/3) is exactly 12 bars.</p></div></div>'
             f'<span class="k" style="margin-top:5pt">Is 20 seconds a whole number of bars?</span>'
             f'<table class="t cc" style="margin-top:1pt"><tr><th>BPM</th><th>Seconds per beat</th><th>Seconds per bar</th><th>Bars in 20 seconds</th><th>Whole bars?</th></tr>{tempo_a_rows()}</table>'
             f'<p class="small" style="margin:0 0 2pt;font-size:8.6pt">Shaded rows are whole numbers of bars. Choose one of them: 96, 120 or 144 BPM. At 100 BPM the ident would be 8.3333 bars, so it would end in the middle of a bar.</p>'
             f'<span class="k" style="margin-top:3pt">Other lengths: bars in 15, 20 and 30 seconds (bold = a whole number)</span>'
             f'<table class="t cc" style="margin-top:1pt"><tr><th>Length</th><th>Tempo rule</th>' + "".join(f"<th>{b} BPM</th>" for b in LEN_TEMPOS) + f'</tr>{len_rows()}</table>'
             f'<p class="small" style="margin:0 0 3pt;font-size:8.6pt">For any length in seconds, bars = seconds × BPM ÷ 240, so tempo = (240 ÷ seconds) × bars. At 120 BPM a 15-second ident is 7.5 bars; use 96 or 128 BPM instead.</p>'
             f'<div class="box acc-b" style="padding:5pt 9pt"><span class="k">My tempo</span>'
             f'<div class="fl" style="margin:3pt 0 3pt;font-size:10pt"><b>Length (15 to 30 s):</b><span></span><b>Tempo:</b><span></span><b>BPM</b></div>'
             f'<div class="fl" style="margin:0;font-size:10pt"><b>One bar = 240 ÷ BPM =</b><span></span><b>s</b><b style="margin-left:8pt">Bars = seconds ÷ one bar =</b><span></span><b>bars</b></div></div>')
    return D.page("Tempo table", "STUDENT", "Class 1", inner, n, wm, name=True, key="tempo")


def script_boxes():
    out = ""
    for (k, st, kind, txt), w in zip(SCRIPTS, SCRIPT_WORDS):
        rs = read_s(w)
        out += (f'<div class="box" style="padding:5pt 9pt;margin-bottom:5pt"><span class="k">Script {k} · {st} · {kind}</span>'
                f'<p style="margin:0 0 2pt;font-size:10.4pt;line-height:1.36">{escape(txt)}</p>'
                f'<p class="small" style="margin:0;font-size:8.8pt">{w} words ÷ 2.5 = {fmt(rs)} seconds at 150 words per minute; the voice window is 12 seconds, so {fmt(12 - rs)} seconds are left for pauses.</p></div>')
    return out


def script_page(n, wm=False):
    rows = "".join(f"<tr><td><b>{s} s</b></td><td>{fmt(words_for(s))}</td><td>{fmt(words_for(s) * 60 / s)}</td></tr>" for s in (10, 12, 15, 20, 30))
    inner = (CSS_CC +
             f'<p style="margin:0 0 4pt;font-size:10.2pt;line-height:1.36">Step 2: write and record the voice. A relaxed radio read is about 150 words per minute, which is 2.5 words per second. '
             f'In a 20-second ident the voice speaks from 4 s to 16 s, a 12-second window, so the script has about 30 words at most. Aim for 24 to 28 so you can breathe. Use a template or write your own; '
             f'all three stations are invented, and none uses call letters.</p>'
             f'{script_boxes()}'
             f'<div class="cols" style="gap:10pt;align-items:flex-start"><div style="flex:0 0 2.6in"><span class="k" style="margin-top:2pt">Words that fit a read time</span>'
             f'<table class="t cc" style="margin-top:1pt"><tr><th>Read time</th><th>Words at 2.5 per second</th><th>Words per minute</th></tr>{rows}</table></div>'
             f'<div style="flex:1"><span class="k" style="margin-top:2pt">My script (invent a station name; no call letters, no real station)</span>'
             f'<div class="ln2" style="height:21pt"></div><div class="ln2" style="height:21pt"></div><div class="ln2" style="height:21pt"></div><div class="ln2" style="height:21pt"></div>'
             f'<div class="fl" style="margin:6pt 0 0;font-size:10pt"><b>Words:</b><span></span><b>÷ 2.5 =</b><span></span><b>s</b><b style="margin-left:6pt">Pause room (12 − read time):</b><span></span><b>s</b></div></div></div>'
             f'<p class="small" style="margin:4pt 0 4pt;font-size:8.6pt">Read the script out loud with a timer before you record. If the real read is longer than the arithmetic says, cut words; do not rush.</p>'
             f'<div class="cols" style="gap:10pt;align-items:flex-start"><div class="box acc-b" style="padding:5pt 9pt"><span class="k">Delivery checklist</span>'
             + "".join(D.chk(c, 11, "font-size:9.8pt;line-height:1.28;margin-bottom:3pt") for c in [
                 "I read the whole script out loud twice, with a timer.", "I say the station name clearly, at an easy pace.",
                 "My voice sounds friendly and relaxed, not rushed.", "I leave a short pause between sentences."]) + '</div>'
             f'<div style="flex:1.2"><span class="k" style="margin-top:0">Take log</span>'
             f'<table class="t cc" style="margin-top:1pt"><tr><th>Take</th><th>Read time (s)</th><th>Loudest peak (dBFS)</th><th>Clipped?</th><th>Keep?</th></tr>'
             + "".join(f"<tr><td style='height:19pt'>{i}</td><td></td><td></td><td></td><td></td></tr>" for i in (1, 2, 3, 4)) + '</table></div></div>')
    return D.page("Script templates and read times", "STUDENT", "Class 1", inner, n, wm, name=True, key="script")


def chain_page(n, wm=False):
    def box(title, items, acc=False):
        return (f'<div class="box{" acc-b" if acc else ""}" style="padding:4pt 9pt"><span class="k">{title}</span>'
                + "".join(D.chk(c, 11, "font-size:9.8pt;line-height:1.28;margin-bottom:2pt") for c in items) + '</div>')
    inner = (f'<p style="margin:0 0 3pt;font-size:10.2pt;line-height:1.36">Step 2: write and record the voice, continued. Follow the sound from your mouth to the mix. '
             f'Each box is one place where you can make the sound better or worse, and the order matters: the high-pass filter and the compressor come after the recording.</p>'
             f'<div style="margin:0 0 3pt">{D.body_svg(chain_body(1600, "chain page"))}</div>'
             f'<div class="cols" style="gap:9pt;align-items:flex-start"><div>'
             + box("Microphone technique", ["I sit 10 to 20 cm from the microphone, about the width of my hand, and stay at that distance for every take.",
                                            "A pop filter sits between my mouth and the microphone, so the P and B sounds do not pop.",
                                            "I speak across the front of the microphone, not into a corner, in a quiet room with soft surfaces.",
                                            "I wear headphones so the music and my voice do not leak back into the microphone."], True)
             + '</div><div>'
             + box("Gain staging", ["I set the input gain on the interface while I read the loudest line of the script.",
                                    "The loudest words peak around −12 to −6 dBFS on the track meter, and never reach 0 dBFS.",
                                    "A take that clips is deleted and recorded again; turning it down later does not fix it.",
                                    "A quieter recording is safe: the next page explains why."])
             + '</div></div>'
             f'<div class="box" style="margin-top:4pt;padding:4pt 9pt"><span class="k">Why 10 to 20 cm</span><p style="margin:0;font-size:9.6pt;line-height:1.32">Close to the microphone the voice gets '
             f'boomy, a change called the proximity effect with many microphones; far away the room gets in. A steady distance keeps the tone and the level the same from word to word. Nobody has measured your room, so try '
             f'two distances and listen.</p></div>'
             f'<span class="k" style="margin-top:4pt">My setup</span>'
             f'<div class="fl" style="margin:2pt 0 2pt;font-size:10pt"><b>Microphone:</b><span></span><b>Distance (cm):</b><span style="flex:0 0 0.9in"></span><b>Pop filter?</b><span style="flex:0 0 0.8in"></span></div>'
             f'<div class="fl" style="margin:0;font-size:10pt"><b>Interface gain setting:</b><span></span><b>Loudest peak seen (dBFS):</b><span style="flex:0 0 1in"></span></div>')
    return D.page("Signal chain and recording technique", "STUDENT", "Class 1", inner, n, wm, name=True, key="chain")


def ladder_rows():
    out = []
    for db, meaning in LADDER:
        a = amp(db)
        lbl = "0" if db == 0 else f"−{-db}"
        out.append(f"<tr><td><b>{lbl}</b></td><td>{r3(a)}</td><td>{r1(a * 100)}%</td><td style='text-align:left'>{meaning}</td></tr>")
    return "".join(out)


def halves_rows():
    return "".join(f"<tr><td>{fmt(h)}</td><td>20 × log10({fmt(h)}) = {r2(to_db(float(h)))} dB</td></tr>" for h in HALVES)


def ladder_page(n, wm=False):
    inner = (CSS_CC +
             f'<p style="margin:0 0 3pt;font-size:10.2pt;line-height:1.36">Step 2: write and record the voice, continued. In a digital recording 0 dBFS is the highest level there is, so every real level is a negative number. '
             f'The amplitude (how far the wave swings, as a share of full scale) is 10 raised to the power of dB ÷ 20. Aim for the loudest words to peak around −12 to −6 dBFS.</p>'
             f'<div style="margin:0 0 2pt">{D.body_svg(ladder_body(1500, "ladder page"))}</div>'
             f'<span class="k" style="margin-top:3pt">The dB ladder</span>'
             f'<table class="t cc" style="margin-top:1pt"><tr><th>dBFS</th><th>Amplitude (× full scale)</th><th>Share of full scale</th><th>What it means here</th></tr>{ladder_rows()}</table>'
             f'<div class="cols" style="gap:10pt;align-items:flex-start;margin-top:2pt"><div class="box acc-b" style="padding:4pt 9pt;flex:1"><span class="k">Half the amplitude is −6 dB</span>'
             f'<table class="t cc" style="margin:1pt 0 2pt"><tr><th>Amplitude</th><th>In decibels</th></tr>{halves_rows()}</table>'
             f'<p style="margin:0;font-size:9pt;line-height:1.3">Each halving is about 6 dB, so −6 is about half, −12 about a quarter and −18 about an eighth. The exact value of −6 dB is 0.501, close to one half.</p></div>'
             f'<div class="box" style="padding:4pt 9pt;flex:1"><span class="k">Set my level</span>'
             f'<p style="margin:0 0 3pt;font-size:9.4pt;line-height:1.3">Read the loudest line. Then work out the amplitude of the peak.</p>'
             f'<div class="fl" style="margin:0 0 3pt;font-size:9.8pt"><b>Loudest peak:</b><span></span><b>dBFS</b></div>'
             f'<div class="fl" style="margin:0 0 3pt;font-size:9.8pt"><b>Amplitude = 10^(dB ÷ 20) =</b><span></span></div>'
             f'<div class="fl" style="margin:0;font-size:9.8pt"><b>Inside −12 to −6?</b><span style="flex:0 0 0.6in"></span><b>If not, change the gain by</b><span></span><b>dB</b></div></div></div>')
    return D.page("The dB ladder and recording levels", "STUDENT", "Classes 1–2", inner, n, wm, name=True, key="ladder")


def bed_page(n, wm=False):
    layers = [("Drums or shaker loop", "Loop Browser, or a Session Player (Drummer) if your version has it"), ("Bass", "A loop or a Software Instrument pattern in the Piano Roll"),
              ("Chords or pad", "A loop, or Alchemy or Retro Synth playing a simple chord pattern"), ("Melody (optional)", "A short original motif; no existing song")]
    fx = [("Sleigh-bell-like shaker", "shaker, jingle or bell loop or sound, if your version has one"), ("Wind", "a wind or noise sound, if your version has one"),
          ("Door chime", "a chime or bell sound, if your version has one")]
    lrows = "".join(f"<tr><td><b>{a}</b></td><td>{b}</td><td style='height:19pt'></td></tr>" for a, b in layers)
    frows = "".join(f"<tr><td><b>{a}</b></td><td>{b}</td><td></td><td></td></tr>" for a, b in fx) + "<tr><td style='height:19pt'></td><td></td><td></td><td></td></tr>"
    tb = "".join(f"<tr><td><b>{b}</b></td><td>{fmt(id_bars(b))}</td><td>{dec(bar_len(b), 3)}</td><td>{fmt(id_bars(b) * bar_len(b))}</td></tr>" for b in CHOICES)
    inner = (CSS_CC +
             f'<p style="margin:0 0 4pt;font-size:10.2pt;line-height:1.36">Step 3: build the bed and effects. The music bed is the music that plays under the voice. Build it from the loops, instruments and effects that come with Logic, '
             f'or play a simple original pattern. Do not use an existing song, and keep it simple: the bed must leave room for the words.</p>'
             f'<div class="cols" style="gap:10pt;align-items:flex-start"><div style="flex:1"><span class="k">How long is my bed?</span>'
             f'<table class="t cc" style="margin-top:1pt"><tr><th>BPM</th><th>Bars</th><th>Seconds per bar</th><th>Seconds in all</th></tr>{tb}</table>'
             f'<p class="small" style="margin:0;font-size:8.6pt">The bed fills every bar of the ident. A loop of 2 or 4 bars repeats to fill 8, 10 or 12.</p></div>'
             f'<div class="box acc-b" style="padding:5pt 9pt;flex:1"><span class="k">A bed with a shape</span>'
             f'<p style="margin:0;font-size:9.6pt;line-height:1.34"><b>Open</b> (first 4 seconds): the bed at full level, so listeners hear the station. <b>Under the voice</b> (4 to 16 seconds): ducked and simpler. '
             f'<b>Out</b> (16 to 20 seconds): back to full for the final hit and chime. Fewer layers under the voice leave room for the words.</p></div></div>'
             f'<span class="k" style="margin-top:5pt">My music bed: layers</span>'
             f'<table class="t" style="margin-top:1pt"><tr><th style="width:24%">Layer</th><th style="width:44%">Where it can come from</th><th>My choice</th></tr>{lrows}</table>'
             f'<span class="k" style="margin-top:5pt">My sound effects: where each one goes</span>'
             f'<table class="t" style="margin-top:1pt"><tr><th style="width:23%">Effect</th><th style="width:37%">Where it can come from</th><th>My choice</th><th style="width:19%">Bar and beat</th></tr>{frows}</table>'
             f'<div class="box" style="margin-top:5pt;padding:5pt 9pt"><span class="k">Bed and effects checklist</span>'
             + "".join(D.chk(c, 11, "font-size:9.8pt;line-height:1.3;margin-bottom:2pt") for c in [
                 "Every loop, instrument and effect comes with Logic, or I made it myself. I used no existing song, jingle or sample.",
                 "The bed is exactly the number of bars on my tempo plan, and it ends on the final hit.",
                 "At least two effects sit on beats of my cue sheet (page @CUES), and each one is short.",
                 "Under the voice the bed has fewer layers, and nothing plays in the same range as the words."]).replace("@CUES", str(pg("cues"))) + '</div>')
    return D.page("Music bed and sound effects plan", "STUDENT", "Class 2", inner, n, wm, name=True, key="bed")


def gr_rows():
    return "".join(f"<tr><td><b>{r}:1</b></td>" + "".join(f"<td>{fmt(gain_red(o, r))}</td>" for o in OVERS) + "</tr>" for r in RATIOS)


def eqcomp_page(n, wm=False):
    inner = (CSS_CC +
             f'<p style="margin:0 0 3pt;font-size:10.2pt;line-height:1.36">Step 4: clean up the voice. Put Channel EQ and then a compressor on the voice track. The numbers on this page are <b>starting points</b>, not rules. '
             f'Change one thing at a time, start with small moves, and let your ears decide.</p>'
             f'<div class="cols" style="gap:10pt;align-items:flex-start"><div style="flex:1.75">{D.H2("EQ: remove rumble first", True)}<div>{D.body_svg(eq_body(700, "eq page"))}</div></div>'
             f'<div style="flex:1">{D.H2("Compression: even it out", True)}<div>{D.body_svg(comp_body(1000, "comp page"))}</div></div></div>'
             f'<div class="cols" style="gap:9pt;align-items:flex-start;margin-top:3pt"><div class="box acc-b" style="padding:4pt 9pt"><span class="k">Starting points for voice</span><ul style="margin:0;padding-left:12pt">'
             f'<li style="font-size:9.6pt;line-height:1.28;margin:0 0 2pt"><b>High-pass:</b> switch it on near 80 Hz. It removes rumble and breath thumps below the voice. Raise it a little only if the voice still sounds full.</li>'
             f'<li style="font-size:9.6pt;line-height:1.28;margin:0 0 2pt"><b>Presence:</b> if the words are hard to follow, try one small boost, such as 1 to 2 dB, and listen. Take it back if the voice gets harsh.</li>'
             f'<li style="font-size:9.6pt;line-height:1.28;margin:0 0 2pt"><b>Ratio:</b> about 3:1 or 4:1. Guides give anything from 2:1 to 5:1.</li>'
             f'<li style="font-size:9.6pt;line-height:1.28;margin:0"><b>Threshold:</b> lower it until the loudest words show about 3 to 6 dB of gain reduction. About 4 dB or less is gentle.</li></ul></div>'
             f'<div style="flex:1"><span class="k" style="margin-top:0">Gain reduction in dB</span>'
             f'<table class="t cc" style="margin-top:1pt"><tr><th>Ratio</th>' + "".join(f"<th>{o} dB over</th>" for o in OVERS) + f'</tr>{gr_rows()}</table>'
             f'<p class="small" style="margin:0;font-size:8.6pt">Gain reduction = dB over the threshold × (1 − 1 ÷ ratio). Example: the loudest words are {EX_OVER} dB over the threshold at {EX_RATIO}:1, so the gain reduction is {EX_OVER} × (1 − 1/{EX_RATIO}) = {fmt(gain_red(EX_OVER, EX_RATIO))} dB. Real compressors soften the bend near the threshold, so the meter may read a little less.</p></div></div>'
             f'<div class="box" style="margin-top:4pt;padding:4pt 9pt"><span class="k">My settings</span>'
             f'<div class="fl" style="margin:2pt 0 3pt;font-size:9.8pt"><b>High-pass (Hz):</b><span style="flex:0 0 0.8in"></span><b>Presence boost (dB, or none):</b><span style="flex:0 0 0.8in"></span><b>Ratio:</b><span></span></div>'
             f'<div class="fl" style="margin:0 0 3pt;font-size:9.8pt"><b>Threshold (dB):</b><span style="flex:0 0 0.8in"></span><b>Most gain reduction seen (dB):</b><span style="flex:0 0 0.8in"></span><b>What I heard change:</b><span></span></div></div>')
    return D.page("EQ and compression for the voice", "STUDENT", "Class 2", inner, n, wm, name=True, key="eqcomp")


def depth_rows():
    out = []
    for d in DUCK_DEPTHS:
        duck = BED_PEAK - d
        out.append(f"<tr><td><b>−{d} dB</b></td><td>{r3(amp(-d))}</td><td>{duck}</td><td>{VOICE_PEAK - duck} dB</td></tr>".replace(f"<td>{duck}</td>", f"<td>−{-duck}</td>"))
    return "".join(out)


def duck_page(n, wm=False):
    inner = (CSS_CC +
             f'<p style="margin:0 0 3pt;font-size:10.2pt;line-height:1.36">Step 5: duck the music. Ducking lowers the music while the voice speaks and lets it rise again afterward, so every word stays clear. '
             f'Start with 6 to 12 dB of reduction and a ramp of about half a second, then adjust by ear. Two ways to do it are below.</p>'
             f'<div style="margin:0 0 3pt">{D.body_svg(duck_body(1600, "duck page"))}</div>'
             f'<div class="cols" style="gap:9pt;align-items:flex-start"><div class="box acc-b" style="padding:4pt 9pt"><span class="k">Way 1 · Sidechain compression</span>'
             + "".join(D.chk(c, 11, "font-size:9.4pt;line-height:1.27;margin-bottom:2pt") for c in [
                 "Put a Compressor on the music track.", "In the plug-in header, open the Side Chain menu (if your version has it) and choose the voice track.",
                 "Lower the threshold until the music drops about 6 to 12 dB while the voice speaks.", "Set the release so the music rises smoothly after the last word."]) +
             f'<p class="small" style="margin:2pt 0 0;font-size:8.6pt">It reacts by itself if you change the voice, but its settings need careful listening.</p></div>'
             f'<div class="box" style="padding:4pt 9pt"><span class="k">Way 2 · Volume automation</span>'
             + "".join(D.chk(c, 11, "font-size:9.4pt;line-height:1.27;margin-bottom:2pt") for c in [
                 "Show automation on the music track and choose Volume.", "Click a point half a second before the voice, and another where the music is 8 dB lower.",
                 "Click a point where the voice ends, and one half a second later back at full level.", "Check the ramps: a straight, gentle slope, never a step."]) +
             f'<p class="small" style="margin:2pt 0 0;font-size:8.6pt">You see and control the exact timing, but you redraw it if the voice moves.</p></div></div>'
             f'<div class="cols" style="gap:9pt;align-items:flex-start;margin-top:3pt"><div><span class="k" style="margin-top:0">Duck depths</span>'
             f'<table class="t cc" style="margin-top:1pt"><tr><th>Reduction</th><th>Music amplitude (× open)</th><th>Ducked peak (dBFS)</th><th>Voice above music</th></tr>{depth_rows()}</table><p class="small" style="margin:0;font-size:8.6pt">Example: the bed peaks at −12 dBFS and the voice at −9 dBFS.</p></div>'
             f'<div class="box" style="padding:4pt 9pt"><span class="k">My duck</span>'
             f'<div class="fl" style="margin:2pt 0 3pt;font-size:9.8pt"><b>Method:</b><span></span><b>Depth (dB):</b><span style="flex:0 0 0.7in"></span></div>'
             f'<div class="fl" style="margin:0 0 3pt;font-size:9.8pt"><b>Ramp (s):</b><span style="flex:0 0 0.7in"></span><b>Starts at (s):</b><span style="flex:0 0 0.7in"></span><b>Ends at (s):</b><span></span></div>'
             f'<div class="fl" style="margin:0;font-size:9.8pt"><b>Could I hear every word?</b><span></span></div></div></div>')
    return D.page("Ducking: the music steps aside", "STUDENT", "Class 3", inner, n, wm, name=True, key="duck")


def cue_rows():
    rows = []
    for k, (txt, s) in enumerate(CUES):
        cells = ""
        for bpm in CHOICES:
            bar, beat = cue_pos(bpm, s)
            cells += f"<td>{bar}</td><td>{fmt(beat)}</td>"
        cls = ' class="hi"' if k in (2, 3) else ""
        rows.append(f"<tr{cls}><td>{fmt(s)}</td><td class='l'>{txt}</td>{cells}</tr>")
    return "".join(rows)


def cues_page(n, wm=False):
    mine = "".join(f"<tr><td>{fmt(s)}</td><td class='l' style='height:17pt'>{txt}</td><td></td><td></td><td></td></tr>" for txt, s in CUES)
    inner = (CSS_CC +
             f'<p style="margin:0 0 3pt;font-size:10.2pt;line-height:1.36">Step 5: duck the music. The cue sheet puts every event on the clock and on the grid. The voice window is 12 seconds, from 4 s to 16 s. '
             f'The duck starts half a second before the voice. The table gives the bar and beat of every cue at the three tempos.</p>'
             f'<div class="box acc-b" style="padding:4pt 9pt"><span class="k">How to find a cue at your tempo</span>'
             f'<p style="margin:0 0 1pt;font-size:9.6pt"><b>Beats from the start</b> = second × BPM ÷ 60. <b>Bar</b> = 1 + the whole bars in (beats ÷ 4). <b>Beat</b> = 1 + the beats left over.</p>'
             f'<p style="margin:0;font-size:9.6pt"><b>Example:</b> 96 BPM, second 4: 4 × 96 ÷ 60 = 6.4 beats, which is 1 whole bar and 2.4 beats, so bar 2, beat 3.4. A beat of 3.4 is 40% of the way from beat 3 to beat 4.</p></div>'
             f'<span class="k" style="margin-top:4pt">The cue sheet at the three tempos</span>'
             f'<table class="t cc" style="margin-top:1pt"><tr><th rowspan="2">Second</th><th rowspan="2">What happens</th><th colspan="2">96 BPM</th><th colspan="2">120 BPM</th><th colspan="2">144 BPM</th></tr>'
             f'<tr><th>Bar</th><th>Beat</th><th>Bar</th><th>Beat</th><th>Bar</th><th>Beat</th></tr>{cue_rows()}</table>'
             f'<p class="small" style="margin:1pt 0 3pt;font-size:8.6pt">At 120 BPM every cue lands exactly on a beat, because a beat lasts half a second. At 96 and 144 BPM some cues fall between beats, so draw the automation points '
             f'with the snap set to a small value and check their positions. The ident ends at bar {cue_pos(96, 20)[0]} beat 1 at 96 BPM, bar {cue_pos(120, 20)[0]} at 120 BPM and bar {cue_pos(144, 20)[0]} at 144 BPM, which is the line after its last bar.</p>'
             f'<span class="k" style="margin-top:3pt">My cue sheet (my tempo: ________ BPM)</span>'
             f'<table class="t cc" style="margin-top:1pt"><tr><th>Second</th><th>What happens</th><th>Beats = second × BPM ÷ 60</th><th>My bar</th><th>My beat</th></tr>{mine}</table>'
             f'<div class="box acc-b" style="margin-top:5pt;padding:4pt 9pt"><span class="k">Check my cues</span>'
             + "".join(D.chk(c, 11, "font-size:9.8pt;line-height:1.28;margin-bottom:2pt") for c in [
                 "The voice comes in on my cue and goes out on my cue.", "The duck starts half a second before the voice and ends half a second after it.",
                 "My last cue is the end of the ident at my tempo, and the bounce ends there."]) + '</div>')
    return D.page("Cue sheet", "STUDENT", "Classes 1–3", inner, n, wm, name=True, key="cues")


def mix_page(n, wm=False):
    def box(title, items, acc=False):
        return (f'<div class="box{" acc-b" if acc else ""}" style="padding:5pt 9pt"><span class="k">{title}</span>'
                + "".join(D.chk(c, 11, "font-size:10pt;line-height:1.3;margin-bottom:3pt") for c in items) + '</div>')
    inner = (f'<p style="margin:0 0 5pt;font-size:10.2pt;line-height:1.36">Step 6: mix and bounce. A mix makes the voice clear, the music supportive and the ending clean. Work through the boxes with headphones, '
             f'then check each one off.</p>'
             f'<div class="cols" style="gap:10pt;align-items:flex-start"><div>'
             + box("Voice", ["I can understand every word with the music playing.", "The high-pass filter is on and there is no rumble, and no loud pops.",
                             "The compressor’s gain reduction meter shows about 3 to 6 dB on the loudest words."], True)
             + '<div style="height:6pt"></div>'
             + box("Music and duck", ["The music falls before the first word and rises after the last, with smooth ramps.", "The music is about 6 to 12 dB lower under the voice.",
                                      "I did not duck so far that the music disappears."])
             + '</div><div>'
             + box("Effects and ending", ["The shaker, wind and chime are on the beats of my cue sheet.", "The chime and the final hit land on the planned bar, and the ident ends when it should.",
                                          "No effect covers a word."], True)
             + '<div style="height:6pt"></div>'
             + box("Levels", ["The voice peaks around −12 to −6 dBFS before processing.", f"The master stays below my ceiling (in the example, −{-MIX_CEILING} dBFS) and never reaches 0 dBFS.",
                              "I listened at a normal volume, not only loud."])
             + '</div></div>'
             f'<div class="box" style="margin-top:6pt;padding:5pt 9pt"><span class="k">The listening test</span><p style="margin:0 0 3pt;font-size:10pt;line-height:1.36">Play the whole ident with your eyes closed and '
             f'rate each part from 1 (weak) to 5 (very strong). Is the voice clear? Does the music feel natural? Does it feel finished at the end? Write what you hear:</p>'
             f'<div class="fl" style="margin:2pt 0;font-size:10pt"><b>Voice:</b><span></span><b>Music:</b><span></span><b>Ending:</b><span></span></div></div>'
             f'<div class="box acc-b" style="margin-top:6pt;padding:5pt 9pt"><span class="k">Bounce</span>'
             + "".join(D.chk(c, 11, "font-size:10pt;margin-bottom:3pt") for c in [
                 "The bounce starts at bar 1 and ends at the planned length (20 seconds for a 20-second plan; check your own tempo on page " + str(pg("tempo")) + ").",
                 "MP3 or WAV bounced, and the .logicx project zipped.", f"Both files named {FILE_NAME}."]) + '</div>'
             f'<span class="k" style="margin-top:6pt">What I changed after the listening test</span>' + D.lines(7, 24))
    return D.page("Mix checklist", "STUDENT", "Class 3", inner, n, wm, name=True, key="mix")


# ================================================================ worked example (2 pages)
def ex_cue_rows():
    out = []
    for txt, s in CUES:
        bar, beat = cue_pos(EX_BPM, s)
        out.append(f"<tr><td>{fmt(s)}</td><td style='text-align:left'>{txt}</td><td>{fmt(cue_beats(EX_BPM, s))}</td><td>{bar}</td><td>{fmt(beat)}</td></tr>")
    return "".join(out)


def ex_level_rows():
    out = []
    for nm, db in EX_LEVELS:
        out.append(f"<tr><td style='text-align:left'><b>{nm}</b></td><td>−{-db}</td><td>{r3(amp(db))}</td></tr>")
    return "".join(out)


def example_page(n, wm=False):
    k, st, kind, txt = EX_SCRIPT
    w = SCRIPT_WORDS[0]
    inner = (f'<style>table.ec td {{ text-align: center; }}</style>'
             f'<p style="margin:0 0 4pt;font-size:10pt">An <b>invented plan on paper</b>: a 20-second ident for {st} at {EX_BPM} BPM. No audio is included. '
             f'Student projects will differ. Page 1 of 2: the plan, the script and the cue sheet.</p>'
             f'<div class="cols" style="gap:10pt;align-items:flex-start"><div class="box"><span class="k">1 · A weak plan</span><p style="margin:0;font-size:10.2pt">{EX_WEAK}</p>'
             f'<p style="margin:3pt 0 0;font-size:9.2pt">It names no tempo, no length in bars, no script and no times.</p></div>'
             f'<div class="box acc-b"><span class="k">2 · A clear plan</span><p style="margin:0;font-size:8.6pt;line-height:1.28">{EX_STRONG}</p></div></div>'
             f'{D.H2("3 · The script (template A)")}'
             f'<div class="box" style="padding:5pt 9pt"><p style="margin:0 0 2pt;font-size:10pt;line-height:1.34">{escape(txt)}</p>'
             f'<p style="margin:0;font-size:8.8pt">{w} words ÷ 2.5 words per second = {fmt(read_s(w))} seconds; the window is 16 − 4 = 12 seconds, so there are {fmt(12 - read_s(w))} seconds for pauses.</p></div>'
             f'{D.H2("4 · The cue sheet at 120 BPM")}'
             f'<table class="t ec" style="font-size:8.8pt;line-height:1.14"><tr><th>Second</th><th>What happens</th><th>Beats from the start</th><th>Bar</th><th>Beat</th></tr>{ex_cue_rows()}</table>'
             f'<p style="margin:2pt 0 0;font-size:8.8pt;line-height:1.3">One beat lasts 60 ÷ {EX_BPM} = {dec(spb(EX_BPM), 3)} s and one bar lasts 240 ÷ {EX_BPM} = {fmt(EX_BAR_S)} s. The ident is 20 ÷ {fmt(EX_BAR_S)} = {EX_BARS} bars, and {EX_BPM} ÷ 12 = {EX_BARS} too. '
             f'Every cue is on a beat because there are {fmt(cue_beats(EX_BPM, 1))} beats in each second.</p>'
             f'{D.H2("5 · The levels in the example")}'
             f'<div class="cols" style="gap:10pt;align-items:flex-start"><div style="flex:0 0 3.3in"><table class="t ec" style="font-size:8.6pt;line-height:1.1;white-space:nowrap"><tr><th>Track</th><th>Peak (dBFS)</th><th>Amplitude</th></tr>{ex_level_rows()}</table></div>'
             f'<p style="margin:0;font-size:8.8pt;line-height:1.3">The music bed peaks at −12 dBFS and is ducked by {DUCK_DB} dB to −{-(BED_PEAK - DUCK_DB)} dBFS, which is {VOICE_PEAK - (BED_PEAK - DUCK_DB)} dB under the voice at −{-VOICE_PEAK}. '
             f'If every peak lined up at one instant, the open bed with the shaker and the wind would reach {r1(worst_sum_db([BED_PEAK, -18, -24]))} dBFS, the voice with the ducked bed {r1(worst_sum_db([VOICE_PEAK, BED_PEAK - DUCK_DB]))} dBFS, '
             f'and the final hit with the chime {r1(worst_sum_db([BED_PEAK, -15]))} dBFS: all below the −{-MIX_CEILING} dBFS ceiling.</p></div>')
    return D.page("Worked example · the plan, the script and the cues", "EXAMPLE", "Teacher", inner, n, wm, ak=True, key="example")


def example2_page(n, wm=False):
    qs = " ".join(f"{i + 1}. {q}" for i, q in enumerate(EX_QUESTIONS))
    inner = (f'<p style="margin:0 0 3pt;font-size:10pt">The same ident, page 2 of 2: the timeline, the voice processing, then the moments to point out.</p>'
             f'{D.H2("6 · The timeline: 10 bars, 5 layers")}'
             f'<div style="margin:1pt 0 3pt">{D.body_svg(duck_body(1600, "duck page"))}</div>'
             f'<div class="cols" style="gap:10pt;align-items:flex-start"><div class="box acc-b" style="margin-top:4pt;flex:1.1"><span class="k">7 · The voice processing</span><p style="margin:0;font-size:9.6pt;line-height:1.34">'
             f'High-pass at {HPF_HZ} Hz (−3 dB at the corner). A small example boost of +{PRES_DB} dB near 3 kHz, added by ear and kept because the consonants were clearer. Compressor at {EX_RATIO}:1 with the threshold at −{-EX_THRESH} dB. '
             f'The loudest words peak at −{-VOICE_PEAK} dBFS, which is {EX_OVER} dB over the threshold, so the gain reduction is {EX_OVER} × (1 − 1/{EX_RATIO}) = {fmt(gain_red(EX_OVER, EX_RATIO))} dB and the peak leaves the compressor at '
             f'−{-int(out_level(VOICE_PEAK, EX_THRESH, EX_RATIO))} dBFS before make-up gain.</p></div>'
             f'<div class="box" style="margin-top:4pt;flex:1"><span class="k">8 · The duck</span><p style="margin:0;font-size:9.6pt;line-height:1.34">Method: volume automation on the music track. The music starts to fall at 3.5 s (bar 2 beat 4), '
             f'is {DUCK_DB} dB lower at 4 s, and rises from 16 s (bar 9 beat 1) to full level at 16.5 s (bar 9 beat 2). The ramps last {fmt(DUCK_RAMP)} second. The same duck with sidechain compression would be set '
             f'by the threshold until the music drops about {DUCK_DB} dB under the voice.</p></div></div>'
             f'<div class="box" style="margin-top:5pt"><span class="k">9 · The effects</span><p style="margin:0;font-size:10pt;line-height:1.36">{EX_AUTO[0].upper() + EX_AUTO[1:]}.</p></div>'
             f'<div class="box" style="margin-top:5pt"><span class="k">10 · Three feedback questions (invented)</span><p style="margin:0;font-size:10pt;line-height:1.36">{qs}</p></div>'
             f'<div class="box acc-b" style="margin-top:5pt"><span class="k">11 · Moments to point out in class</span><ul style="margin:0">'
             f'<li style="font-size:10pt;margin-bottom:2pt">The music is the loudest at the start and the end and quietest under the voice, so the voice always leads.</li>'
             f'<li style="font-size:10pt;margin-bottom:0">At 120 BPM every cue falls on a beat, so the class can clap along with the duck and hear exactly when it begins.</li></ul></div>')
    return D.page("Worked example · the timeline, the processing and the numbers", "EXAMPLE", "Teacher", inner, n, wm, ak=True, key="example2")


PAGES = {"howto": howto_page, "overview": overview_page, "setup": setup_page, "example": example_page, "example2": example2_page,
         "tempo": tempo_page, "script": script_page, "chain": chain_page, "ladder": ladder_page, "bed": bed_page, "eqcomp": eqcomp_page,
         "duck": duck_page, "cues": cues_page, "mix": mix_page}

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


BADGE = {"tempo": "Class 1", "script": "Class 1", "chain": "Class 1", "ladder": "Classes 1–2", "bed": "Class 2", "eqcomp": "Class 2", "duck": "Class 3",
         "cues": "Classes 1–3", "mix": "Class 3", "present": f"Classes {CLASSES - 1}–{CLASSES}"}


def float_cue(bpm, s):
    """An independent float check of one cue: (bar, beat) of second s, from beats = s x BPM / 60."""
    beats = float(s) * bpm / 60
    whole = math.floor(beats / 4 + 1e-9)
    return 1 + whole, 1 + beats - 4 * whole


FORBIDDEN_WORDS = ("cham" + "pagne", "toast", "cheers", "wine", "beer", "cocktail", "drink", "alcohol", "bub" + "bly", "church", "prayer", "pray ", "blessing", "holy", "sacred",
                   "religio", "god ", "santa", "christmas", "hanukkah", "chanukah", "kwanzaa")
CALL_LETTERS = re.compile(r"\b[KW][A-Z]{2,3}\b")


def verify_content():
    errs = []
    counts = dict(goals=(GOALS, 4), vocab=(VOCAB, 5), reqs=(REQS, 7), steps=(STEPS, 7), tips=(TIPS, 4), check=(CHECK, 6),
                  rubric=(RUBRIC, 5), struggles=(STRUGGLES, 4), resources=(RESOURCES, 5), slides=(SLIDES, 16), plan=(PLAN, 27),
                  logic=(LOGIC_REF, 9), ladder=(LADDER, 7), cues=(CUES, 7), scripts=(SCRIPTS, 3))
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
    if [id_bars(b) for b in CHOICES] != [8, 10, 12] or [id_bars(b) for b in (90, 100, 110, 128)] != [Fraction(15, 2), Fraction(25, 3), Fraction(55, 6), Fraction(32, 3)]:
        errs.append("bars in 20 seconds = BPM / 12: 8, 10, 12 at 96, 120, 144; 7.5 at 90, 8.3333 at 100, 9.1667 at 110, 10.6667 at 128")
    for b in TEMPOS:
        if abs(float(id_bars(b)) - 20 / (240 / b)) > 1e-9 or id_bars(b) != Fraction(b, 12):
            errs.append(f"bars in 20 seconds at {b} BPM")
    if [b for b in TEMPOS if is_whole(b)] != [96, 120, 144]:
        errs.append("20 seconds is a whole number of bars only at 96, 120 and 144 BPM in the table")
    for bars in range(1, 15):
        if id_bars(12 * bars) != bars or not is_whole(12 * bars) or is_whole(12 * bars + 1):
            errs.append(f"tempo = 12 x bars fails for {bars} bars")
    if [dec(spb(b), 3) for b in TEMPOS] != ["0.667", "0.625", "0.600", "0.545", "0.500", "0.469", "0.417"] or \
       [dec(bar_len(b), 3) for b in TEMPOS] != ["2.667", "2.500", "2.400", "2.182", "2.000", "1.875", "1.667"]:
        errs.append("seconds per beat and per bar to 3 decimals")
    if [dec(id_bars(b), 4) for b in TEMPOS] != ["7.5000", "8.0000", "8.3333", "9.1667", "10.0000", "10.6667", "12.0000"]:
        errs.append("bars in 20 seconds to 4 decimals")
    for L in LENGTHS:
        for b in LEN_TEMPOS:
            if id_bars(b, L) != Fraction(L * b, 240) or abs(float(id_bars(b, L)) - L * b / 240) > 1e-9:
                errs.append(f"bars in {L} seconds at {b} BPM")
            if is_whole(b, L) != (b % (240 // L) == 0 if 240 % L == 0 else False):
                errs.append(f"whole-bar rule for {L} seconds at {b} BPM")
    if [[id_bars(b, L) for b in LEN_TEMPOS] for L in LENGTHS] != [[6, Fraction(15, 2), 8, 9], [8, 10, Fraction(32, 3), 12], [12, 15, 16, 18]] or [240 // L for L in LENGTHS] != [16, 12, 8]:
        errs.append("bars in 15, 20 and 30 seconds at 96, 120, 128, 144 BPM; tempo rules 16, 12 and 8 x bars")
    if rnd(Fraction(5, 2), 0) != 3 or dec(Fraction(125, 1600), 3) != "0.078" or dec(Fraction(15, 8), 3) != "1.875" or dec(Fraction(80, 3), 2) != "26.67":
        errs.append("round half up")
    # ---- the cue sheet
    secs = [s for _, s in CUES]
    if secs != [0, Fraction(7, 2), 4, 16, Fraction(33, 2), 18, 20] or VOICE_OUT - VOICE_IN != 12 or secs != sorted(secs):
        errs.append("cues: 0, 3.5, 4, 16, 16.5, 18, 20 seconds; the voice window is 12 seconds")
    for b in CHOICES:
        for s in secs:
            bar, beat = cue_pos(b, s)
            fb, fe = float_cue(b, s)
            if bar != fb or abs(float(beat) - fe) > 1e-9:
                errs.append(f"cue at {b} BPM second {s}: exact {bar, beat}, float {fb, fe}")
            if not 1 <= beat < 5:
                errs.append(f"cue beat out of the bar at {b} BPM second {s}")
            if pos_s(b, bar, beat) != s:
                errs.append(f"cue at {b} BPM second {s} does not round-trip through bar {bar} beat {beat}")
        if cue_pos(b, ID_SECONDS) != (int(id_bars(b)) + 1, 1):
            errs.append(f"the end of the ident must be beat 1 of the bar after the last bar at {b} BPM")
    if [cue_pos(120, s) for s in secs] != [(1, 1), (2, 4), (3, 1), (9, 1), (9, 2), (10, 1), (11, 1)]:
        errs.append("at 120 BPM every cue is on a beat: 1.1, 2.4, 3.1, 9.1, 9.2, 10.1, end 11.1")
    if cue_pos(96, 4) != (2, Fraction(17, 5)) or cue_pos(144, 4) != (3, Fraction(13, 5)) or cue_pos(96, Fraction(7, 2)) != (2, Fraction(13, 5)):
        errs.append("cue examples: 96 BPM second 4 = bar 2 beat 3.4; 144 BPM second 4 = bar 3 beat 2.6; 96 BPM second 3.5 = bar 2 beat 2.6")
    if [cue_pos(b, ID_SECONDS)[0] for b in CHOICES] != [9, 11, 13]:
        errs.append("the ident ends on bar 9, 11 and 13 beat 1 at 96, 120 and 144 BPM")
    if DUCK_RAMP != Fraction(1, 2) or VOICE_IN - DUCK_RAMP != Fraction(7, 2) or VOICE_OUT + DUCK_RAMP != Fraction(33, 2):
        errs.append("the duck ramp is half a second before the voice and after it")
    # ---- speaking rate and the scripts
    if WPS != Fraction(5, 2) or [words_for(s) for s in (10, 12, 15, 20, 30)] != [25, 30, Fraction(75, 2), 50, 75] or read_s(30) != 12:
        errs.append("150 words per minute = 2.5 per second: 25, 30, 37.5, 50, 75 words in 10, 12, 15, 20, 30 seconds")
    if SCRIPT_WORDS != [24, 25, 28] or [read_s(w) for w in SCRIPT_WORDS] != [Fraction(48, 5), 10, Fraction(56, 5)]:
        errs.append("script word counts 24, 25, 28 (read times 9.6, 10, 11.2 seconds)")
    for k, st, kind, t in SCRIPTS:
        if n_words(t) > words_for(VOICE_OUT - VOICE_IN) or read_s(n_words(t)) >= VOICE_OUT - VOICE_IN:
            errs.append(f"script {k} does not fit the 12-second voice window with room to breathe")
        if CALL_LETTERS.search(t) or CALL_LETTERS.search(st):
            errs.append(f"script {k} must not use call letters")
        if st not in t:
            errs.append(f"script {k} must name its station")
        for w in FORBIDDEN_WORDS:
            if w in t.lower():
                errs.append(f"script {k} holds a forbidden word: {w}")
        if len(re.findall(r"[A-Za-z’']+", t)) != n_words(t):
            errs.append(f"script {k}: a word count by whitespace must equal the count by letters (no stray tokens)")
    if len({s[1] for s in SCRIPTS}) != 3:
        errs.append("three different invented stations")
    # ---- decibels
    for db, want in zip((0, -3, -6, -9, -12, -18, -20), ("1.000", "0.708", "0.501", "0.355", "0.251", "0.126", "0.100")):
        if r3(amp(db)) != want:
            errs.append(f"amplitude at {db} dBFS must print {want}, not {r3(amp(db))}")
        if abs(to_db(amp(db)) - db) > 1e-9:
            errs.append(f"20 log10(10^(dB/20)) must return {db}")
    if [r2(to_db(float(h))) for h in HALVES] != ["−6.02", "−12.04", "−18.06"] or abs(to_db(0.5) + 6.0206) > 1e-4:
        errs.append("20 log10(0.5) = -6.02; halving twice -12.04; three times -18.06")
    if [r1(amp(d) * 100) for d in (0, -3, -6, -9, -12, -18, -20)] != ["100.0", "70.8", "50.1", "35.5", "25.1", "12.6", "10.0"]:
        errs.append("shares of full scale")
    if [r3(amp(-d)) for d in DUCK_DEPTHS] != ["0.501", "0.398", "0.316", "0.251"]:
        errs.append("duck depth amplitudes at -6, -8, -10, -12 dB")
    if BED_PEAK - DUCK_DB != -20 or VOICE_PEAK - (BED_PEAK - DUCK_DB) != 11 or [VOICE_PEAK - (BED_PEAK - d) for d in DUCK_DEPTHS] != [9, 11, 13, 15]:
        errs.append("duck: bed -12 dBFS lowered 8 dB is -20; the voice at -9 sits 11 dB above it; 9, 11, 13, 15 dB for the four depths")
    if not -12 <= VOICE_PEAK <= -6:
        errs.append("the example voice peak is in the -12 to -6 dBFS target")
    if worst_sum_db([BED_PEAK, -18, -24]) > MIX_CEILING or worst_sum_db([VOICE_PEAK, BED_PEAK - DUCK_DB]) > MIX_CEILING or worst_sum_db([BED_PEAK, -15]) > MIX_CEILING:
        errs.append("the worked example's worst-case combined peaks must stay below the mix ceiling")
    if [r1(worst_sum_db(x)) for x in ([BED_PEAK, -18, -24], [VOICE_PEAK, BED_PEAK - DUCK_DB], [BED_PEAK, -15])] != ["−7.1", "−6.8", "−7.4"]:
        errs.append("worst-case combined peaks -7.1, -6.8 and -7.4 dBFS")
    # ---- compression
    if [[gain_red(o, r) for o in OVERS] for r in RATIOS] != [[Fraction(3, 2), 3, Fraction(9, 2), 6], [2, 4, 6, 8], [Fraction(9, 4), Fraction(9, 2), Fraction(27, 4), 9]]:
        errs.append("gain reduction = over x (1 - 1/ratio): 2:1 1.5, 3, 4.5, 6; 3:1 2, 4, 6, 8; 4:1 2.25, 4.5, 6.75, 9")
    for r in RATIOS:
        for o in OVERS:
            inp = EX_THRESH + o
            if inp - out_level(inp, EX_THRESH, r) != gain_red(o, r) or out_level(EX_THRESH - 5, EX_THRESH, r) != EX_THRESH - 5:
                errs.append(f"compressor transfer at {r}:1, {o} dB over")
    if EX_OVER != 8 or gain_red(EX_OVER, EX_RATIO) != 6 or out_level(VOICE_PEAK, EX_THRESH, EX_RATIO) != -15 or out_level(0, EX_THRESH, EX_RATIO) != Fraction(-51, 4):
        errs.append("example: voice at -9, threshold -17, 4:1 -> 8 dB over, 6 dB of gain reduction, -15 dBFS out; 0 dB in gives -12.75")
    # ---- EQ curves
    if abs(hpf_gain_db(80) + 3.0103) > 1e-3 or hpf_gain_db(20) > -24 or abs(hpf_gain_db(1000)) > 0.01 or abs(hpf_gain_db(400) + 0.0) > 0.07 or hpf_gain_db(40) > -11.5 or hpf_gain_db(40) < -12.5:
        errs.append("2nd-order high-pass: -3.01 dB at 80 Hz, about -12 dB at 40 Hz, below -24 dB at 20 Hz, flat by 1 kHz")
    if not 1.9 < eq_gain_db(3000) < 2.01 or eq_gain_db(3000) < max(eq_gain_db(f) for f in (1000, 6000, 12000)):
        errs.append("the example presence boost peaks near 3 kHz at about +2 dB")
    # ---- Logic wording: newer tools are hedged
    for nm, txt in LOGIC_REF:
        if any(w in txt for w in ("Session Player", "Side Chain", "make-up", "high-pass (low cut)", "sleigh")) and "if your version" not in txt.lower():
            errs.append(f"Logic reference '{nm}' must hedge a newer tool with 'if your version'")
    joined = " ".join(t for _, t in LOGIC_REF)
    for w in ("Loop Browser", "Session Player", "Alchemy", "Retro Synth", "Channel EQ", "Compressor", "Side Chain", "automation", "Piano Roll", "Bounce", "Mixer", "record-enable"):
        if w not in joined:
            errs.append(f"the Logic quick reference must name {w}")
    # ---- the worked example
    if EX_BPM != 120 or EX_BAR_S != 2 or EX_BARS != 10 or id_bars(EX_BPM) != 10:
        errs.append("the example: 120 BPM, 2 s per bar, 10 bars")
    for need in ("120 BPM", "240 ÷ 120 = 2 seconds", "exactly 10 bars", "24-word script", "9.6 seconds", "4 seconds (bar 3 beat 1)", "16 seconds (bar 9 beat 1)", "3.5 seconds (bar 2 beat 4)",
                 "8 dB lower", "16.5 seconds (bar 9 beat 2)", "18 seconds (bar 10 beat 1)", "20 seconds"):
        if need not in EX_STRONG:
            errs.append(f"the clear plan must say '{need}'")
    # ---- no forbidden themes in any text a buyer reads
    allt = " ".join([THEME, BUILD_NOTE, OVERVIEW, " ".join(GOALS), " ".join(f"{a} {b}" for a, b in VOCAB), " ".join(REQS), " ".join(STEPS), " ".join(TIPS), " ".join(CHECK),
                     " ".join(d for _, ds in RUBRIC for d in ds), TN_REINFORCES, " ".join(STRUGGLES), VAR_EASY, VAR_HARD, " ".join(f"{a} {b}" for a, b in RESOURCES), TN_NOTE,
                     " ".join(GRADING), " ".join(d["do"] for d in PACING), SONG_NOTE, VOICE_NOTE, " ".join(t for _, t in LOGIC_REF), EX_STRONG, EX_AUTO, " ".join(EX_QUESTIONS),
                     " ".join(t for *_, t in SCRIPTS), " ".join(" ".join((s[2], s[3], s[4])) for s in SLIDES), " ".join(t for t, _ in CUES), " ".join(m for _, m in LADDER)]).lower()
    for w in FORBIDDEN_WORDS:
        if re.search(rf"\b{re.escape(w.strip())}\b", allt):
            errs.append(f"no alcohol, religious or seasonal-holiday wording in a neutral kit: '{w.strip()}'")
    for w in ("colour", "favour", "centre", "licence", "grey", "metre ", "organis", "recognis", "practise", "analyse", "whilst", "milli-second", "equalis", "normalis", "behaviour", "sulph"):
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
    for need, key in ((f"page {pg('cues')}", 4), (f"page {pg('duck')}", 4), (f"page {pg('tempo')}", 5), (f"page {pg('script')}", 5), (f"page {pg('chain')}", 6),
                      (f"page {pg('ladder')}", 7), (f"page {pg('logicref')}", 8), (f"page {pg('bed')}", 8), (f"page {pg('eqcomp')}", 9), (f"page {pg('eqcomp')}", 10),
                      (f"page {pg('duck')}", 11), (f"page {pg('cues')}", 11)):
        if need not in SLIDES[key][4]:
            errs.append(f"slide {key + 1} notes must name {need}")
    for i, s in enumerate(SLIDES, start=1):
        errs += step_ref_errors(" ".join((s[2], s[3], s[4])), f"slide {i}")
    if [s[0] for s in SLIDES] != [1] * 8 + [2] * 3 + [3] * 5 or SLIDES[3][1] != "days":
        errs.append("deck classes: slides 1-8 Class 1, 9-11 Class 2, 12-16 Class 3; slide 4 is the 'days' slide (it gets the Classes 1-3 badge)")
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


DECK_BOX_PAD_IN = 16 / 96        # --check: least padding below the last text line in any black box on a deck slide (16 px at the 1280 px slide scale)
NUM_WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7}


def layer_count_errors(flat, stext, notes):
    """Every stated layer count (PDF, deck, notes, UPLOAD.md, source strings) equals the number of rows in the timeline drawing."""
    errs = []
    n = len(DUCK_ROWS)
    texts = [("PDF", " ".join(flat)), ("deck", " ".join(stext)), ("deck notes", " ".join(notes)), ("source", OVERVIEW + " " + " ".join(s[2] for s in SLIDES))]
    up = os.path.join(HERE, "UPLOAD.md")
    if os.path.exists(up):
        texts.append(("UPLOAD.md", open(up, encoding="utf8").read()))
    for label, t in texts:
        for m in re.finditer(r"\b(\d+|one|two|three|four|five|six|seven)\s+layers\b", t, re.I):
            w = m.group(1).lower()
            if (int(w) if w.isdigit() else NUM_WORDS[w]) != n:
                errs.append(f"{label}: '{m.group(0)}' but the timeline drawing has {n} layers ({', '.join(DUCK_ROWS)})")
    if not any(re.search(rf"\b{n}\s+layers\b", t, re.I) for _, t in texts[:2]):
        errs.append(f"the layer count ({n}) is not stated in the PDF or the deck")
    return errs


def class_step_errors():
    """A deck slide badged Class 2 does not name ducking or the mix (the pacing table puts both in Class 3)."""
    errs = []
    for i, s in enumerate(SLIDES, start=1):
        if s[0] == 2 and s[1] == "steps" and re.search(r"\bduck|\bmix", s[3], re.I):
            errs.append(f"deck slide {i} is badged Class 2 but its steps name ducking or the mix, which the pacing page assigns to Class 3")
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


def verify_outputs(flat, stext, notes):
    errs = []
    alldeck = " ".join(stext + notes)
    txt = " ".join(flat)
    if "No audio" not in notes[0]:
        errs.append("deck slide 1 notes must say 'No audio'")
    for need in ("No audio, recordings, lyrics or melodies", "invented plan on paper", "Loop Browser", "Session Player", "Alchemy", "Channel EQ", "Compressor", "Side Chain",
                 "60 ÷ BPM", "240 ÷ BPM", "BPM ÷ 12", "Tempo = 12 × bars", "if your version", "150 words per minute", "2.5 words per second", "high-pass", "sidechain", "ducking",
                 "−12 to −6 dBFS", "−6.02", "pop filter", "starting points", "start with small moves", "20-second",
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
    # ---- Step N on every page, in the deck PDF text, the deck notes and UPLOAD.md agrees with the project sheet
    expect = {"tempo": {1}, "script": {2}, "chain": {2}, "ladder": {2}, "bed": {3}, "eqcomp": {4}, "duck": {5}, "cues": {5}, "mix": {6}}
    for k in PLAN:
        t = flat[D.IX(k) - 1]
        errs += step_ref_errors(t, f"page {D.IX(k)} ({k})")
        found = {int(m.group(1)) for m in re.finditer(r"\bStep (\d+)\b", t)}
        if k in expect and found != expect[k]:
            errs.append(f"page {D.IX(k)} ({k}) should cite Step {sorted(expect[k])}, cites {sorted(found)}")
        if k not in expect and found:
            errs.append(f"page {D.IX(k)} ({k}) cites Step {sorted(found)} unexpectedly")
    errs += step_ref_errors(" ".join(stext), "deck slides")
    errs += layer_count_errors(flat, stext, notes)
    errs += class_step_errors()
    errs += dark_box_errors()
    errs += badge_errors(flat)
    import subprocess as sp

    def raw(key):
        return re.sub(r"\s+", " ", sp.run(["pdftotext", "-raw", "-f", str(D.IX(key)), "-l", str(D.IX(key)), D.files()["pdf"], "-"],
                                          capture_output=True, text=True, check=True).stdout)
    # ---- the tempo page prints every number
    rc = raw("tempo")
    for bpm in TEMPOS:
        w = is_whole(bpm)
        row = f"{bpm} {dec(spb(bpm), 3)} {dec(bar_len(bpm), 3)} {fmt(id_bars(bpm)) if w else dec(id_bars(bpm), 4)} {'Yes' if w else 'No'}"
        if row not in rc:
            errs.append(f"tempo page: row '{row}' is not printed")
    for L in LENGTHS:
        row = f"{L} s {fmt(Fraction(240, L))} × bars " + " ".join(fmt(id_bars(b, L)) if id_bars(b, L).denominator == 1 else dec(id_bars(b, L), 2) for b in LEN_TEMPOS)
        if row not in rc:
            errs.append(f"tempo page: length row '{row}' is not printed")
    for need in ("Seconds per beat = 60 ÷ BPM", "Seconds per bar = 240 ÷ BPM", "Bars in 20 seconds = 20 ÷ (240 ÷ BPM) = BPM ÷ 12", "Tempo = 12 × bars", "240 ÷ 120 = 2 s per bar",
                 "20 ÷ 2 = 10 bars", "120 ÷ 12 = 10 too", "Step 1: plan the ident", "5 rounds up", "8.3333", "7.5 bars"):
        if need not in rc:
            errs.append(f"tempo page must say '{need}'")
    # ---- the script page
    rs = raw("script")
    for (k, st, kind, t), w in zip(SCRIPTS, SCRIPT_WORDS):
        if t not in rs:
            errs.append(f"script page: script {k} is not printed whole")
        line = f"{w} words ÷ 2.5 = {fmt(read_s(w))} seconds at 150 words per minute; the voice window is 12 seconds, so {fmt(12 - read_s(w))} seconds are left for pauses"
        if line not in rs:
            errs.append(f"script page: '{line}' is not printed")
    for s in (10, 12, 15, 20, 30):
        row = f"{s} s {fmt(words_for(s))} 150"
        if row not in rs:
            errs.append(f"script page: row '{row}' is not printed")
    for need in ("Step 2: write and record the voice", "150 words per minute, which is 2.5 words per second", "call letters", "30 words at most"):
        if need not in rs:
            errs.append(f"script page must say '{need}'")
    # ---- the chain and ladder pages
    rch = raw("chain")
    for need in ("Step 2: write and record the voice", "10 to 20 cm", "pop filter", "−12 to −6 dBFS", "proximity effect", "MICROPHONE", "INTERFACE", "AUDIO TRACK", "CHANNEL EQ", "COMPRESSOR", "MIX BUS", "side chain"):
        if need.lower() not in rch.lower():
            errs.append(f"chain page must say '{need}'")
    rl = raw("ladder").replace("- ", "-")
    for db, _ in LADDER:
        a = amp(db)
        lbl = "0" if db == 0 else f"−{-db}"
        row = f"{lbl} {r3(a)} {r1(a * 100)}%"
        if row not in rl:
            errs.append(f"ladder page: row '{row}' is not printed")
    for h in HALVES:
        row = f"{fmt(h)} 20 × log10({fmt(h)}) = {r2(to_db(float(h)))} dB"
        if row not in rl:
            errs.append(f"ladder page: row '{row}' is not printed")
    for need in ("Step 2: write and record the voice", "0.501", "−6.02", "10 raised to the power of dB ÷ 20", "Classes 1–2"):
        if need not in rl:
            errs.append(f"ladder page must say '{need}'")
    # ---- bed, EQ and compression, ducking
    rb = raw("bed")
    for b in CHOICES:
        row = f"{b} {fmt(id_bars(b))} {dec(bar_len(b), 3)} {fmt(id_bars(b) * bar_len(b))}"
        if row not in rb:
            errs.append(f"bed page: row '{row}' is not printed")
    if "Step 3: build the bed and effects" not in rb or "existing song" not in rb:
        errs.append("bed page: Step 3 and the no-existing-song rule")
    re_ = raw("eqcomp")
    for r in RATIOS:
        row = f"{r}:1 " + " ".join(fmt(gain_red(o, r)) for o in OVERS)
        if row not in re_:
            errs.append(f"EQ and compression page: row '{row}' is not printed")
    for need in ("Step 4: clean up the voice", "starting points", "near 80 Hz", "about 3:1 or 4:1", "3 to 6 dB", "8 × (1 − 1/4) = 6 dB", "1 to 2 dB", "start with small moves"):
        if need not in re_:
            errs.append(f"EQ and compression page must say '{need}'")
    rd = raw("duck")
    for d in DUCK_DEPTHS:
        duck = BED_PEAK - d
        row = f"−{d} dB {r3(amp(-d))} −{-duck} {VOICE_PEAK - duck} dB"
        if row not in rd:
            errs.append(f"duck page: row '{row}' is not printed")
    for need in ("Step 5: duck the music", "SIDECHAIN COMPRESSION", "VOLUME AUTOMATION", "6 to 12 dB", "half a second", "Side Chain menu"):
        if need not in rd:
            errs.append(f"duck page must say '{need}'")
    # ---- the cue sheet page
    rq = raw("cues")
    for txt_, s in CUES:
        row = f"{fmt(s)} {txt_} " + " ".join(f"{cue_pos(b, s)[0]} {fmt(cue_pos(b, s)[1])}" for b in CHOICES)
        if row not in rq:
            errs.append(f"cue page: row '{row}' is not printed")
    for need in ("Step 5: duck the music", "second × BPM ÷ 60", "4 × 96 ÷ 60 = 6.4 beats", "bar 2, beat 3.4", "ends at bar 9 beat 1 at 96 BPM, bar 11 at 120 BPM and bar 13 at 144 BPM"):
        if need not in rq:
            errs.append(f"cue page must say '{need}'")
    # ---- the worked example prints its numbers
    re1 = (raw("example") + " " + raw("example2")).replace("- ", "-")
    for txt_, s in CUES:
        bar, beat = cue_pos(EX_BPM, s)
        row = f"{fmt(s)} {txt_} {fmt(cue_beats(EX_BPM, s))} {bar} {fmt(beat)}"
        if row not in re1:
            errs.append(f"worked example: cue row '{row}' is not printed")
    for nm, db in EX_LEVELS:
        row = f"{nm} −{-db} {r3(amp(db))}"
        if row not in re1:
            errs.append(f"worked example: level row '{row}' is not printed")
    for need in ("60 ÷ 120 = 0.500 s", "240 ÷ 120 = 2 s", "20 ÷ 2 = 10 bars", "120 ÷ 12 = 10 too", "24 words ÷ 2.5 words per second = 9.6 seconds", "16 − 4 = 12 seconds", "2.4 seconds",
                 "−7.1 dBFS", "−6.8 dBFS", "−7.4 dBFS", "8 × (1 − 1/4) = 6 dB", "−15 dBFS", "threshold at −17 dB", "3.5 s (bar 2 beat 4)", "16.5 s (bar 9 beat 2)"):
        if need not in re1:
            errs.append(f"worked example must say '{need}'")
    up = open(os.path.join(HERE, "UPLOAD.md"), encoding="utf8").read()
    errs += step_ref_errors(up, "UPLOAD.md")
    if "Grades 9-12" not in up or "`9th-grade`, `10th-grade`, `11th-grade`, `12th-grade`" not in up:
        errs.append("UPLOAD.md: grades 9-12 in the description and section 3")
    if "no audio" not in up.lower() or "Open question" not in up or "Timing numbers" not in up or "Sources and credits" not in up:
        errs.append("UPLOAD.md: must say no audio is included, record the timing numbers checked, the sources and the open questions")
    for need in ("Words per minute", "DBFS", "Decibel", "MusicRadar", "Sound on Sound", "Sage Audio", "Audacity", "Apple", "Shure", "ask.audio", "invented"):
        if need not in up:
            errs.append(f"UPLOAD.md sources and credits must name: {need}")
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
    for brand in ("Shure", "Sound on Sound", "MusicRadar", "Sage Audio", "Audacity", "Wikipedia", "ask.audio"):
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
    return ("seconds per beat = 60 / BPM, per bar = 240 / BPM and bars in 20 seconds = BPM / 12 recomputed exactly (fractions) and by an independent float method; "
            "20 seconds is a whole number of bars only at tempo = 12 x bars (96, 120 and 144 BPM give 8, 10 and 12; 90, 100, 110 and 128 do not), and the 15 and 30 second tables (tempo = 16 x bars and 8 x bars); "
            "every cell of the tempo table (7 tempos); the cue sheet at all three tempos (7 cues each, exact and float, each cue round-tripping to its second; every cue on a beat at 120 BPM); "
            "the three scripts (24, 25 and 28 words; read times 9.6, 10 and 11.2 s at 2.5 words per second; all inside the 12-second voice window; no call letters); the dB ladder (amplitude = 10^(dB/20), "
            "20 log10(0.5) = -6.02, shares of full scale), the duck depths, the worked example's worst-case peaks; the compression table and transfer curve (gain reduction = over x (1 - 1/ratio); 8 dB over at 4:1 = 6 dB; -9 in gives -15 out); "
            "the EQ curve (2nd-order high-pass -3.01 dB at 80 Hz); every 'Step N' agrees with the project sheet on pages, slides, notes and UPLOAD.md; class badges agree with the pacing page, and the deck's "
            "'three classes' slide carries Classes 1-3; every drawing renders alone on a transparent ground with no ink at its edges; hero art inside its viewBox; rendered-DOM footer gap on every page and deck slide; "
            "no truncated slide bullets; edges of cover.png and previews clear; no audio, lyrics, melodies, alcohol, religious or brand wording or student work; no source site named on a buyer page; "
            "grades 9-12; tags and subjects are not headings; no 'what changed' page (ORIGINAL).")


# ================================================================ UPLOAD.md (written by gen.py so every number matches the build)
def write_upload():
    np_, ns = len(PLAN), len(SLIDES)
    n_teacher = (PLAN.index("example2") + 1) - 1
    n_student = (PLAN.index("reflect") + 1) - (PLAN.index("tempo") + 1) + 1
    assert 2 + n_teacher + n_student == np_, "page-count list must total the PDF"
    nt = len(LISTING_TITLE)
    desc = (f"{DESC_START} students make a 20-second radio station ident (a short sound logo and spot) for an invented winter station in Logic Pro, with a voice, an original music bed and sound effects. "
            f"They plan the length with timing math (one bar of 4/4 = 240 ÷ BPM seconds, so tempo = 12 × bars: 96, 120 and 144 BPM give 8, 10 and 12 bars), write a script that fits its time (about 150 words per minute, "
            f"which is 2.5 words per second, so a 12-second read is about 30 words), record the voice with good microphone technique and levels, clean it up with a high-pass filter and a gentle compressor, "
            f"and duck the music under the voice with sidechain compression or with automation. The theme is a winter-season station and the project suits any class. This Holiday Radio Ident project takes {CLASSES} class periods "
            f"(the pacing guide also shows two and four) and is an original Hudson Beat project; the steps are written for Logic Pro, while the ideas (gain staging, EQ, compression, ducking) carry over to GarageBand.\n\n"
            f"WHAT'S INCLUDED (ZIP: {np_}-page PDF = 1 cover + {n_teacher} teacher + {n_student} student + 1 terms page, plus {ns}-slide intro deck as .pptx and PDF)\n"
            f"• Teacher pages: how to use, project overview, setup, a {CLASSES}-class pacing guide with the deck slides for each class, "
            f"two pages of teacher notes (struggles, variations, resources, grading), a Logic quick reference and a two-page worked example (an invented ident at 120 BPM: "
            f"10 bars = 20 seconds, a 24-word script, the voice from 4 to 16 seconds, the duck, the levels and the processing) ({n_teacher} pages)\n"
            f"• Student pages: a tempo table (seconds per beat and per bar, bars in 20 seconds at seven tempos, and the bars in 15, 20 and 30 seconds), three original scripts for invented stations with word counts and read times, "
            f"a signal-chain diagram (microphone, interface, track, EQ, compressor, mix bus) with a recording checklist, a dB ladder (levels in dBFS, amplitudes and the −6 dB rule), a music bed and effects plan, "
            f"an EQ and compression page with starting points and the gain-reduction arithmetic, a ducking page with both methods and a depth table, a cue sheet (the bar and beat of every cue at three tempos plus a blank sheet), "
            f"a mix checklist, the 3-page project sheet (overview, goals, vocabulary, requirements, steps, tips, submission checklist), the /{RUBRIC_TOTAL} rubric, a vocabulary page, a feedback planner and a reflection page ({n_student} pages)\n"
            f"• Teacher-presented intro deck, {ns} slides with speaker notes on every slide: a think-and-share hook, what the project is, the 20-second timeline, the timing math, the signal chain, the dB ladder, "
            f"building it in Logic, EQ, compression, ducking, what to turn in and the rubric\n\n"
            f"THE THREE CLASS PERIODS\n"
            f"• Class 1: hook; the timing math and a tempo; the script; microphone technique, levels and the first recording\n"
            f"• Class 2: build the music bed and sound effects; EQ and compression for the voice\n"
            f"• Class 3: duck the music, mix, bounce, present and reflect\n\n"
            f"WHAT STUDENTS LEARN\n"
            f"• Timing math: seconds per bar in 4/4 = 240 ÷ BPM; bars in 20 seconds = BPM ÷ 12; tempo = 12 × bars gives a whole number of bars; the same for 15 and 30 seconds; words = seconds × 2.5\n"
            f"• Recording: microphone distance, a pop filter, gain at the interface, and levels that peak around −12 to −6 dBFS; −6 dB is about half the amplitude (20 × log10(0.5) = −6.02)\n"
            f"• Processing: a high-pass filter near 80 Hz, small moves, a compressor at about 3:1 or 4:1 with about 3 to 6 dB of gain reduction on the loudest words, and ducking the music by about 6 to 12 dB with a half-second ramp\n"
            f"• Building in Logic Pro: the Loop Browser, Session Players and a simple Piano Roll pattern if your version has them, Channel EQ, Compressor and its Side Chain menu, volume automation, the Mixer and bounce\n\n"
            f"GOOD TO KNOW\n"
            f"• There is no audio in this resource and no student work. No melody, song, jingle or lyrics are printed; the three station names are invented. Students make every sound themselves in Logic Pro, from Logic's own loops, instruments and effects and their own voices\n"
            f"• Requires Logic Pro on a Mac. A microphone and a pop filter are recommended, and the voice can be a classmate's read; nobody has to read music. Where a control may differ between versions, the pages say \"if your version has it\"\n"
            f"• All audio numbers are starting points to set by ear, not rules\n"
            f"• Rubric: 5 categories scored 1-5, /{RUBRIC_TOTAL}; the final grade is the average of the student's and the teacher's score\n"
            f"• Grades 9-12; music technology or music production classes\n"
            f"• The deck uses the free Oswald and Source Sans 3 fonts (built into Google Slides); install them for PowerPoint or Keynote, or present "
            f"the PDF copy, which shows the intended look\n"
            f"• Every student page prints well in black and white\n\n"
            f"Logic Pro is a product of Apple Inc., named only to describe compatibility. This resource is not affiliated with Apple.\n\n"
            f"Please leave a rating: you earn TpT credits for feedback, and it helps other teachers find this\n"
            f"Follow the Hudson Beat store for new music resources every week\n\n"
            f"{D.DISCLOSURE_NEW}")
    tbl = "; ".join(f"{b} BPM: {dec(bar_len(b), 3)} s per bar, {fmt(id_bars(b))} bars = 20 s" for b in CHOICES)
    nonw = "; ".join(f"{b} BPM = {dec(id_bars(b), 4)} bars" for b in (90, 100, 110, 128))
    cues = ", ".join(f"{t.split(';')[0].split(':')[0].lower()} at {fmt(s)} s = bar {cue_pos(EX_BPM, s)[0]} beat {fmt(cue_pos(EX_BPM, s)[1])}" for t, s in CUES)
    md = f"""# UPLOAD: Holiday Radio Ident, original Logic Pro project (TpT 080)

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
({nt} characters; the limit is 80.) The title leaves out Holiday, Winter and Christmas because TpT's Seasonal Titles notice blocked a holiday-named title on 027 (see 032, 033 and 034); "Radio Ident Project" and "Voice, Music Bed, Ducking, EQ" are the plain search phrases. "Logic Pro" is in the first 30 characters as a compatibility word.

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

**${PRICE}** (paid), multiple-license price ${PRICE}. The price the queue set, at the low end of the $8-12 holiday Logic kit range, for a kit with {np_} pages + {ns} slides, a tempo table, three scripts, a signal chain, a dB ladder, an EQ and compression page, a ducking page, a cue sheet and a two-page worked example, listed in late December.

## 8. Free or paid / free preview pages

Paid. Preview PDF (4 watermarked pages): the {CLASSES}-class pacing guide, the signal chain and recording page, the ducking page and the /{RUBRIC_TOTAL} rubric. "Number of pages or slides" is {np_ + ns} ({np_} pages + {ns} slides).

## 9. Sources and credits

Every audio number in the product is a starting point, and the product says so. What each one rests on (all fetched on 24 Nov 2026):

- **About 150 words per minute (2.5 words per second).** English Wikipedia, "Words per minute": 150-160 words per minute is the recommended range for audiobooks; 100-125 for slide presentations. The kit uses 150, the low end of the audiobook range, as a relaxed radio read; the page gives no figure for radio itself, so the kit does not claim one. Words = seconds × 150 ÷ 60 is arithmetic.
- **Decibels and dBFS.** English Wikipedia, "Decibel": amplitude ratios use 20 log10; a halving is about −6 dB (table value 0.501 ≈ 1/2). English Wikipedia, "DBFS": 0 dBFS is the maximum digital level, so a signal at 50% of maximum sits at about −6 dBFS, and digital audio clips there. 20 log10(0.5) = −6.02 is computed in `gen.py --check`, with every amplitude on the dB ladder (10^(dB/20)).
- **Voice peaks around −12 to −6 dBFS.** A common beginner target, not a standard. MusicRadar, "Back to basics: the beginner's guide to headroom and levels": peaks no higher than −6 dBFS, average around −18 dBFS. Sound on Sound, "Gain staging in Logic Pro": −18 dBFS peaks as a working reference, −12 dBFS as an analog-style reference line, no headroom above 0 dBFS, final mix peaks several dB below 0. Sound on Sound, "How should I set my compressor when recording vocals?": at 24-bit, leave 10-15 dB of headroom and compress at the mix. An Adorama guide to audio levels (page read) calls the −12 to −6 dB meter zone the "sweet spot" and "ideal for dialogue" (it does not say peaks). The exact phrase "−12 and −6 dBFS" for a vocal peak was found in a search summary of an ask.audio article, whose page was not read; the kit therefore calls the range a starting point and says a quieter recording is safe.
- **Microphone distance 10 to 20 cm, pop filter, steady distance, proximity effect.** Shure's "vocal miking tips" page (read in full): the proximity effect is the boomy, bass-heavy sound of a source very close to the microphone; studio vocals are typically captured from 6 to 12 inches (about 15 to 30 cm); distances run from an inch to arm's length depending on the performance. That page does not mention pop filters and gives no 10 to 20 cm figure. So **10 to 20 cm (about 4 to 8 inches; 10 ÷ 2.54 = 3.94, 20 ÷ 2.54 = 7.87) is this kit's choice for a classroom speaking voice, not a Shure figure**, and a pop filter and a steady distance are ordinary recording practice, not sourced here. The pages tell students to try two distances and listen.
- **High-pass filter near 80 Hz.** Sage Audio, "Mastering Voice-Over Dialogue for Video": a high-pass filter covering 0-80 Hz removes plosives and microphone rumble. The kit says "near 80 Hz" and "raise it a little only if the voice still sounds full" (the second half is general practice, not sourced).
- **Compression: ratio about 3:1 or 4:1, about 3 to 6 dB of gain reduction.** Sound on Sound (vocal compressor Q&A, seen as a search summary): ratios from roughly 2:1 to 5:1. Sage Audio (page read): compressors typically use ratios such as 2:1 or 4:1, and it is generally wise not to add more than about 6 dB of compression. A voice-over mixing blog (search summary) suggests trying 2:1 or 3:1. No page read says "3 to 6 dB"; the **3:1 or 4:1 picks and the "about 3 to 6 dB" window are the teacher's choice, inside those ranges and under Sage Audio's 6 dB ceiling**. Gain reduction = dB over threshold × (1 − 1 ÷ ratio) is the standard hard-knee formula, computed in `gen.py --check`; real compressors soften the knee, which the page says.
- **Ducking by about 6 to 12 dB with a half-second ramp.** Audacity manual, "Auto Duck": the defaults are a duck amount of −12 dB and outer fade lengths of 0.5 seconds. 12 dB is therefore a documented default; 6 dB as the lower end is this kit's choice (it halves the amplitude) and is not a published standard. A search for typical depths found no single standard, so the kit calls 6 to 12 dB a starting point to adjust by ear. Sidechain compression and the Side Chain menu: Apple's Logic Pro documentation (Compressor side chain parameters) and a Sound on Sound Logic Pro article (the side chain menu chooses any track as the source). The menu location is hedged with "if your version has it" and no menu path is invented.
- **Example values (not from any source).** The worked example's levels (voice −9, bed −12, shaker −18, wind −24, chime −15 dBFS), the −8 dB duck, the −17 dB compressor threshold, the +2 dB presence boost near 3 kHz, the −3 dBFS mix ceiling and all invented cue times are example values chosen for this kit and labeled as examples.
- **Station names.** Snowline Radio, Northlight Radio and Hollow Pine Radio are invented. None is a call-letter name. Searches on 24 Nov 2026 found no station by these names, but a search is not a trademark clearance (see the open questions).
- **Art:** the cover, previews and deck use the owner's pre-made art (`art/hero.png`: a microphone with headphones and a small radio with a blank dial), copied whole from `tpt/_art/next/holiday-radio-ident/`; logged in `tpt/_art/USAGE.md`. Everything else, including every number, table, curve and drawing, is drawn or printed in code.
- **Music:** nothing is notated or printed. No songs, jingles, artists or recordings are named. Students make every sound.
- **Fonts:** Oswald and Source Sans 3 (SIL OFL 1.1). Logic Pro is named only to describe compatibility.

## 10. Before you click publish

- [ ] **Needs QA approval first.** This is a new kit (not yet on TpT); the Manager releases it only after a QA `**Verdict: APPROVED**`. Season rule: build for late December; listing no sooner than the 2-8 week window allows.
- [ ] Cover and previews show "HUDSON BEAT" in type; PDF footers read "© 2026 Brian Lotze · Hudson Beat · For single-classroom use".
- [ ] No school name, logo, student names or work, audio, video, lyrics, melody, song title or Logic session anywhere (`gen.py --check` scans every output and every file in this folder).
- [ ] **Neutral and secular.** The theme is a winter-season radio station; no religious content, no alcohol imagery, no brands, no real stations, no existing jingles. `gen.py --check` fails on alcohol, religious and holiday-specific words and on call-letter names in the scripts.
- [ ] **Timing numbers (all recomputed in `gen.py --check`, exactly with fractions and again with an independent float method).** Seconds per beat = 60 / BPM; seconds per bar in 4/4 = 240 / BPM; bars in 20 seconds = BPM / 12, a whole number only when tempo = 12 x bars (15 seconds: 16 x bars; 30 seconds: 8 x bars). Not whole: {nonw}. Choices: {tbl}. Cues at 120 BPM: {cues}. Scripts: 24, 25 and 28 words = 9.6, 10 and 11.2 seconds at 2.5 words per second, all inside the 12-second window. Rounding: seconds per beat and per bar to 3 decimals, bars to 4 (2 in the length table), half up.
- [ ] **Level numbers (recomputed).** Amplitude = 10^(dB/20): 1.000, 0.708, 0.501, 0.355, 0.251, 0.126, 0.100 at 0, −3, −6, −9, −12, −18, −20 dBFS; halving = −6.02, −12.04, −18.06 dB; the example's worst-case combined peaks −7.1, −6.8 and −7.4 dBFS, all below its −3 dBFS ceiling; compression table (2:1, 3:1, 4:1 at 3, 6, 9, 12 dB over); the 4:1 example: 8 dB over, 6 dB of reduction, −9 in gives −15 out.
- [ ] **Original project.** Built with `ORIGINAL = True` in `tpt/_dmp2_common/dmp2.py` (like 031, 036, 053, 057, 061, 063, 067, 070 and 076): no "what changed" page and the new disclosure line. The reflection page is the shared Reflection element, scored in the rubric's "Plan & Reflection" row. `dmp2.py` is unchanged; the deck's three-classes badge and the terms-page thank-you note are applied inside `gen.py`.
- [ ] **Logic Pro names to confirm on a Mac with a current Logic.** The Loop Browser (the loop icon in the toolbar), Session Players such as the Drummer (hedged), Alchemy and Retro Synth, the Piano Roll, Channel EQ's lowest band as a high-pass or low-cut filter (hedged), Compressor with its gain reduction meter and make-up gain (hedged) and Side Chain menu (hedged), record-enable (R), automation (A), the Mixer (X), Bounce (Command-B) and Compress in Finder. Nothing says a loop or preset of a given name exists; the shaker, wind and chime sounds are "if your version has one".
- [ ] **Open questions for the owner:** (1) **Title.** No Holiday, Winter or Christmas in the title because of TpT's seasonal-title notice (see 1). (2) **Price.** ${PRICE}, as queued, the low end of the $8-12 range. (3) **Ranges.** −12 to −6 dBFS for voice peaks and 6 to 12 dB for the duck are starting points drawn from the sources above; 6 dB for the duck is the kit's own lower end, and the −12 to −6 range rests on a source that was only read as a search summary. Say if you want them rephrased. (4) **Loops.** The kit tells students to use only the loops and sounds that come with Logic. Apple's support page "Use the royalty-free content included with Logic Pro for Mac and MainStage in commercial works" says the sample content may be used royalty-free to create original soundtracks, and that individual assets may not be distributed standalone; the kit promises nothing beyond that, and does not say your school's license covers anything in particular. (5) **Station names.** Confirm you are comfortable with the three invented names. (6) **Classes.** Three periods; the pacing page shows two and four.
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
