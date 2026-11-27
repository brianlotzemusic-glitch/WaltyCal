#!/usr/bin/env python3
"""Logic Pro project kit: House Remix (TpT 092): the teacher resource, the intro deck and the listing files.

    python3 gen.py            build everything into this folder (also writes UPLOAD.md)
    python3 gen.py --lowres   same, but square images at scale 1 and small page shots (self-check only; --check rejects it)
    python3 gen.py --check    verify content and layout: the tempo math for 4/4 at 128 BPM (one beat = 60 / BPM s = 468.75 ms, one 16th-note step = 15 / BPM s = 117.1875 ms, one bar = 240 / BPM s
                              = 1.875 s = 16 steps; exact fractions and an independent float method; length tables), the tune's tempo ratio and percent change against four class-choice tempos, the
                              four-on-the-floor pattern (kick on steps 1, 5, 9, 13; clap on 5 and 13; open hat and bass on the off-beats 3, 7, 11, 15; hits per bar, per lane and in all, counted again in the
                              step-grid drawing), the chord table (I, IV, V, vi built by stacking thirds in three major keys, bass roots, no chord shares a step with the kick), the sidechain numbers
                              (gain reduction from the stated threshold and ratio, plotted in the gain-curve drawing; release times as fractions of a beat; four dips a bar counted in the ducking drawing),
                              the 64-bar arrangement (6 layers, 6 sections, section starts in bars and seconds, bars per layer, layers sounding per bar, counted again in the drawing), the layer-table and
                              signal-chain drawings, Step N references on every page, slide and UPLOAD.md, class badges against the pacing page, count-vs-drawing (lanes, steps, hits, bars, layers),
                              drawings (each rendered alone on a transparent ground: no ink within 4 px of its edge), the hero art, files, page and slide counts, class slots, fonts, fit and overlap, dead
                              space, footer gap (pages and deck slides), black-box padding (pages and deck slides), the edges of cover.png and the previews, banned strings, tpt.json and UPLOAD.md

An ORIGINAL Hudson Beat project (dmp2.ORIGINAL = True, like 063 to 090). Students remix ONE traditional winter song (Deck the Halls, a Welsh melody) as a 128 BPM four-on-the-floor house track:
tempo math, a 4-bar 16-step drum and bass pattern, a four-chord loop, a sidechain duck on the bass, pad and tune, and a 64-bar arrangement. No audio, no lyrics and no melody chart ship (the melody could not be
checked against two fetched sources, so students enter the tune from a public-domain score or by ear). The art is a library piece (art/hero.png), used whole. Everything else is drawn in code. The shared
builder is ../_dmp2_common/dmp2.py (untouched).
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
SLUG = "house-remix-sidechain"
TITLE = "House Remix"
ACCENT = "#2F7FB8"          # this product's single accent: icy blue (a shade deeper than the art's #4FA3D9, so small labels read)
ACC_LIGHT = "#DCEBF6"
PRICE = "8.00"
CLASSES = 3
GRADES_TEXT = "9–12"
GRADE_SLUGS = ["9th-grade", "10th-grade", "11th-grade", "12th-grade"]
TAGS = ["Winter", "Project-based Learning", "Projects", "Activities"]     # exact entries of tpt/TAG-OPTIONS.json, none a heading
SUBJECTS = ["Music", "Music Composition", "Computer Science - Technology"]     # all in SUBJECT-OPTIONS.json, none a heading
ANSWER_KEY = None
LISTING_TITLE = "Logic Pro House Remix | 128 BPM, Sidechain, Four on the Floor | High School"
DESC_START = "House remix project for high school music technology:"
DESC_MUST = ["House Remix", "four-on-the-floor", "sidechain", "128 BPM", "468.75", "1.875", "117.19", "no audio", "off-beat", "drop"]
ZIP_DIR = "House Remix - Hudson Beat"
ZIP_DATE = (2026, 11, 27, 12, 0, 0)
TYPE = "Original Project"
PROJ_LINE = "Music Technology | <i>House Remix at 128 BPM</i> | 3 class periods"
DECK_STRAP = "Four on the floor, ducked"
REFLECT_ROW = "Plan &amp; Reflection"
# split so this file never contains them (the --check scan reads every file in this folder)
BANNED_EXTRA = ["Rud" + "olph", "Fro" + "sty", "Gri" + "nch", "Santa Claus " + "Is", "Jingle Bell " + "Rock", "Feliz " + "Navidad",
                "Mari" + "ah Carey", "Spoti" + "fy", "You" + "Tube", "Home " + "Alone", "Nin" + "tendo", "Ro" + "land",
                "Star " + "Wars", "Hans " + "Zimmer", "John " + "Williams", "Harry " + "Potter", "Pix" + "ar", "Lord of the " + "Rings",
                "Winter " + "Wonderland", "Let It " + "Snow", "Sleigh " + "Ride", "X" + "mas", "Times " + "Square", "Auld " + "Lang",
                "Ak" + "ai", "Ab" + "leton", "FL " + "Studio", "Sound" + "Cloud", "Tik" + "Tok", "Spl" + "ice", "Ser" + "um", "Ama" + "zon",
                "Hallm" + "ark", "Day" + "tona", "Dav" + "id Guetta", "Dead" + "mau5", "Daft " + "Punk", "Calvin " + "Harris", "Avi" + "cii", "Tom" + "orrowland", "Ult" + "ra Music"]

# ================================================================ page plan (teacher pages 2-10, student pages 11-26)
PLAN = ["cover", "howto", "overview", "setup", "pacing", "tn1", "tn2", "logicref", "example", "example2", "timing", "tune", "pattern", "chords", "sidechain", "roles",
        "arrange", "mix", "proj1", "proj2", "proj3", "rubric", "vocab", "present", "reflect", "terms"]


def pg(k):
    return PLAN.index(k) + 1


# ================================================================ the arithmetic (exact fractions; all verified in --check)
TEMPOS = (100, 110, 120, 124, 128, 130)     # the timing table's rows
EX_BPM = 128                                # the project's tempo
CAROL_TEMPOS = (90, 100, 110, 120)          # class-choice "usual tempos" of a plain, un-remixed version (no tempo source was fetched: these are examples)
LEN_TEMPOS = (120, 124, 128)                # the length table's three tempos
LEN_BARS = (8, 16, 32, 64)
STEPS_BAR = 16                              # 16th-note steps in one bar of 4/4
BEATS_BAR = 4
PAT_BARS = 4                                # the pattern is 4 bars
ARR_BARS = 64                               # the arrangement
HOUSE_TYPICAL = (115, 130)                  # "a typical tempo of 115-130 beats per minute" (English Wikipedia, House music, lead)
HOUSE_CHARACTERISTIC = (120, 130)           # "a tempo of between 120 and 130 beats per minute" (same article, Characteristics)
THRESH_DB = -20                             # this kit's own example threshold for the sidechain graphs (dB)
RATIO = 4                                   # this kit's own example ratio: 4:1 is the ratio in Wikipedia's worked example
KICK_LEVELS = (-20, -16, -12, -8, -4, 0)    # the kick's level at the side chain (dB), for the gain-reduction table

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
    return f"{float(x):.10f}".rstrip("0").rstrip(".")


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

def padded(body, W, H, M=10):
    """Wrap a drawing's body with M units of clear padding on all four sides (wider than the thickest outer stroke), so no edge pixel is ever inked."""
    return f'<g transform="translate({M},{M})">{body}</g>', W + 2 * M, H + 2 * M

def meter(x, cy, level, cls="dot"):
    """Three dots, `level` of them filled."""
    out = []
    for i in range(3):
        on = i < level
        out.append(f'<circle class="{cls} {"on" if on else "off"}" cx="{x + i * 40:.1f}" cy="{cy:.1f}" r="13" fill="{ACCENT if on else "#fff"}" stroke="#000" stroke-width="3.5"/>')
    return "".join(out)



def ms(x):
    """Seconds as a Fraction -> milliseconds as a Fraction."""
    return Fraction(x) * 1000


def gain_reduction(level_db, thresh=THRESH_DB, ratio=RATIO):
    """Gain reduction (dB) applied to a ducked track when the side-chain signal is at level_db: 0 below the threshold, then (level - threshold) x (1 - 1/ratio).
    With a 4:1 ratio, a side-chain signal 4 dB over the threshold is brought to 1 dB over it, which is 3 dB of gain reduction (English Wikipedia, Dynamic range compression)."""
    over = Fraction(level_db) - thresh
    return Fraction(0) if over <= 0 else over * (1 - Fraction(1, ratio))


# ---- the six layers: (name, icon, role, pitch 1-3, length 1-3, side chain: TRIGGER / DUCKED / NO DUCK, what to use, what it plays)
PITCH_W = {1: "LOW", 2: "MID", 3: "HIGH"}
LEN_W = {1: "SHORT", 2: "MEDIUM", 3: "LONG"}
SOUNDS = [("KICK", "drum", "DRUMS", 1, 1, "TRIGGER", "A short, low kick from a drum machine or sample pack", "A thump on every beat: grid steps 1, 5, 9 and 13"),
          ("CLAP", "clap", "DRUMS", 2, 1, "NO DUCK", "A clap or snare sound", "Beats 2 and 4: grid steps 5 and 13"),
          ("HATS", "hats", "DRUMS", 3, 2, "NO DUCK", "A closed hat and an open hat", "Closed hat on the even steps; open hat on the off-beats 3, 7, 11 and 15"),
          ("BASS", "rollbass", "BASS", 1, 2, "DUCKED", "A low synth bass (Retro Synth or Alchemy, if your version has them)", "The chord's root note on the off-beats: grid steps 3, 7, 11 and 15"),
          ("PAD", "rollpad", "HARMONY", 2, 3, "DUCKED", "A soft, held synth chord sound", "The chord of the bar, held: one chord in each bar"),
          ("MELODY", "rolltune", "MELODY", 3, 2, "DUCKED", "A bright synth lead", "The song's tune, entered from a public-domain score or by ear")]
NSND = len(SOUNDS)                          # 6
ROLES = [("DRUMS", "Kick, clap and hats: the beat", "the kick, the clap and the hats"), ("BASS", "A low line that locks with the kick", "the bass"),
         ("HARMONY", "Chords that fill out the sound", "the pad"), ("MELODY", "The tune everyone knows", "the lead")]
LAYERS = [s[0] for s in SOUNDS]
DUCKED = [s[0] for s in SOUNDS if s[5] == "DUCKED"]          # BASS, PAD, MELODY

# ---- the model pattern: 4 bars of 16 steps; for each lane the grid steps (1-16) it plays in bars 1 to 4. Lanes may share a step (they are layered).
LANES = ["KICK", "CLAP", "CLOSED HAT", "OPEN HAT", "BASS"]
NLANE = len(LANES)
PATTERN = {"KICK": [[1, 5, 9, 13]] * 4,
           "CLAP": [[5, 13], [5, 13], [5, 13], [5, 13, 15, 16]],
           "CLOSED HAT": [[2, 4, 6, 8, 10, 12, 14, 16]] * 4,
           "OPEN HAT": [[3, 7, 11, 15]] * 4,
           "BASS": [[3, 7, 11, 15]] * 4}
PAT_HITS = [sum(len(PATTERN[l][b]) for l in LANES) for b in range(PAT_BARS)]       # 22, 22, 22, 24
LANE_HITS = {l: sum(len(x) for x in PATTERN[l]) for l in LANES}                    # 16, 10, 32, 16, 16
PAT_TOTAL = sum(PAT_HITS)                                                           # 90
OFFBEAT_STEPS = [3, 7, 11, 15]                                                      # the "and" of each beat: halfway between two kicks
FLOOR_STEPS = [1, 5, 9, 13]

# ---- the chords: I, IV, V and vi of a major key, built by stacking thirds in the scale (verified in --check)
SCALES = {"C": ["C", "D", "E", "F", "G", "A", "B"], "F": ["F", "G", "A", "Bb", "C", "D", "E"], "G": ["G", "A", "B", "C", "D", "E", "F#"]}
PC = {"C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3, "E": 4, "F": 5, "F#": 6, "Gb": 6, "G": 7, "G#": 8, "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B": 11}
DEGREES = [("I", 0, "major"), ("IV", 3, "major"), ("V", 4, "major"), ("vi", 5, "minor")]
WORK_KEY = "F"


def triad(key, deg):
    sc = SCALES[key]
    return [sc[deg % 7], sc[(deg + 2) % 7], sc[(deg + 4) % 7]]


def chord_name(key, deg, quality):
    root = SCALES[key][deg]
    return root + ("m" if quality == "minor" else "")


def loop_chords(key):
    return [(rn, chord_name(key, d, q), triad(key, d)) for rn, d, q in DEGREES]


LOOP_BARS = 4                                # one chord a bar: I, IV, V, vi, then again

# ---- the arrangement: 64 bars; rows (layers) and the bars each plays
ARR_ROWS = [("KICK", [(1, 8), (17, 32), (41, 64)]), ("CLAP", [(9, 32), (41, 56)]), ("HATS", [(5, 32), (41, 60)]), ("BASS", [(17, 32), (41, 56)]),
            ("PAD", [(1, 64)]), ("MELODY", [(17, 56)])]
ARR_SECTIONS = [("INTRO", 1, 8), ("BUILD", 9, 16), ("DROP", 17, 32), ("BREAK", 33, 40), ("DROP", 41, 56), ("OUTRO", 57, 64)]
ARR_LAYERS = [r for r, _ in ARR_ROWS]


def spans_text(spans):
    return ", ".join(f"{a}–{b}" if a != b else str(a) for a, b in spans)


def bars_of(nm):
    return [b for r, spans in ARR_ROWS if r == nm for a, c in spans for b in range(a, c + 1)]


def layers_in_bar(b):
    return [r for r, _ in ARR_ROWS if b in bars_of(r)]


def kick_on(b):
    return "KICK" in layers_in_bar(b)


# ================================================================ the project text (original; students read these pages)
SONG_FACTS = ("The song is “Deck the Halls”, a traditional Welsh melody that dates back to the sixteenth century and was in print by the 1790s under the name “Nos Galan”. "
              "It is far older than any copyright, so the tune is in the public domain. This kit uses the tune only: no words, no recordings and no existing remix.")
THEME = ("A remix keeps a song’s tune and changes everything around it. Here a traditional winter song is rebuilt as house music: a kick on every beat, hats between the beats, claps on beats 2 and 4, "
         "a bass that gets out of the kick’s way, and a build and a drop that make a room want to move. Students make every sound themselves, so there is no existing remix anywhere in the project.")
BUILD_NOTE = ("The skills here are the ones every dance track needs: a tempo that is worked out, not guessed; a pattern on a 16-step grid; a bass and chords that fit the key; a sidechain duck that lets the kick "
              "through; and an arrangement with a build, a drop and a break. They carry over to club music, game music and any project that needs a steady pulse.")
KEY_NOTE = ("Key and meter are choices for the remix, not facts about the song: this kit writes its examples in F major and in 4/4, and any key a student can play the tune in works. "
            "If your version of the tune is written in another meter, it can still be remixed in 4/4 by counting the same beats again.")
OVERVIEW = ("Remix one traditional winter song as a house track in Logic Pro. Students work out a tempo of 128 BPM with timing math, build a four-on-the-floor pattern on a 16-step grid (kick on every beat, open hat "
            "on the off-beats, clap on beats 2 and 4, bass between the kicks), add a four-chord loop, enter the tune, set up sidechain compression so the bass, pad and tune duck when the kick hits, "
            "and arrange a 64-bar track with an intro, a build, a drop, a break, a second drop and an outro. Nobody needs to read music: the tune can be entered from a public-domain score or by ear.")
GOALS = ["Plan the track with timing math: one beat = 60 ÷ BPM seconds (468.75 ms at 128 BPM), one 16th-note step = 15 ÷ BPM seconds, one bar = 240 ÷ BPM seconds (1.875 s)",
         "Build a four-on-the-floor pattern on a 16-step grid: kick on grid steps 1, 5, 9 and 13, open hat on the off-beats, clap on 2 and 4, and bass between the kicks",
         "Explain sidechain compression and set it up so the bass, pad and tune duck when the kick hits, with a release timed to the beat",
         "Add a I-IV-V-vi chord loop and the tune in one key, then arrange a 64-bar track with a build, a drop and a break, and mix it"]
VOCAB = [("Four on the floor", "A steady 4/4 rhythm in which the kick drum is hit on every beat: 1, 2, 3 and 4"),
         ("Sidechain", "A compressor input that lets one sound, such as the kick, control how much another sound is turned down"),
         ("Kick", "The low drum hit that plays on every beat in a house track; its job is the pulse"),
         ("Off-beat", "The halfway point between two beats, the “and” of each beat: grid steps 3, 7, 11 and 15"),
         ("Build", "A section that raises the tension, often with more layers, before the drop"),
         ("Drop", "The point where the full beat and bass arrive after a build; usually the loudest part of the track"),
         ("Breakdown", "A quieter section in which the beat drops out and the tune or chords are heard alone"),
         ("Release", "How long a compressor takes to let the level rise again after it has turned a sound down")]
REQS = ["Choose 128 BPM, set the project tempo and fill in the timing page: one beat = 60 ÷ BPM s (page @TIMING)",
        "Prepare the song: its tempo change, your key and the tune entered or played in (page @TUNE)",
        "Build the 4-bar, 16-step house pattern and draw its hits on the step grid (page @PATTERN)",
        "Add the I-IV-V-vi chord loop, a bass on the off-beats and check the tune against the chords (page @CHORDS)",
        "Set up the sidechain so the bass, pad and tune duck on every kick and write down your release time (pages @SIDECHAIN and @ROLES)",
        "Arrange 64 bars with an intro, build, drop, break, drop and outro; mix with the checklist and bounce (pages @ARRANGE and @MIX)",
        "Present your remix and reflect on your choices (pages @PRESENT and @REFLECT)"]
FILE_NAME = "“Your Name – House Remix”"
STEP_NAMES = ["Plan the tempo", "Prepare the song", "Build the house beat", "Add bass and chords", "Set up the sidechain", "Arrange and mix", "Present &amp; get feedback"]
STEPS = ["<b>Plan the tempo</b> — Use the timing page (page @TIMING) to work out how long one beat, one step and one bar last at 128 BPM, and set the project tempo",
         "<b>Prepare the song</b> — Read the song facts and compare the song’s usual tempo with 128 BPM, choose a key and get the tune from a public-domain score or play it by ear (page @TUNE)",
         "<b>Build the house beat</b> — Play or draw the kick, clap, hats and bass on a 16-step grid for 4 bars and draw the hits on the step grid (page @PATTERN; quick reference: page @LOGICREF)",
         "<b>Add bass and chords</b> — Play the I-IV-V-vi chord loop as a pad, put the bass roots on the off-beats and check each bar’s first tune note against its chord (page @CHORDS)",
         "<b>Set up the sidechain</b> — Duck the bass, pad and tune with a compressor whose side chain listens to the kick, and time the release to the beat (pages @SIDECHAIN and @ROLES)",
         "<b>Arrange and mix</b> — Build a 64-bar arrangement (page @ARRANGE), mix with the checklist (page @MIX) and bounce",
         "<b>Present &amp; get feedback</b> — Write three questions you want classmates to answer about your remix. Play it, point out the build, the drop and the sidechain duck as they arrive, "
         "and answer at least 2 of each classmate’s questions. Then reflect (page @REFLECT)."]
TIPS = ["Work out the tempo first: every later step, from the grid to the release time, comes from 128 BPM.",
        "Solo the kick and the bass together while you set the sidechain: you should hear the bass dip on every kick.",
        "Keep the kick, clap and hats at a sensible level before you add bass and chords, and leave headroom on the master.",
        "Save a new version of your project at the end of each class, so you can always go back."]
CHECK = ["Bounced .mp3 or .wav of your remix, 64 bars long",
         "Zipped .logicx project file handed in",
         f"Files named correctly: {FILE_NAME}",
         "Timing page, step grid and chord table handed in",
         "Rubric self-score done (page @RUBRIC)",
         "I can say my tempo, how long one bar lasts, my release time and where each section starts"]
RUBRIC_NOTE = "Each category is scored 1–5. Score yourself first; the final grade is the average of your score and your teacher’s."
LEVELS = [1, 2, 3, 4, 5]
RUBRIC = [
    ("Tempo & Timing", ["No tempo or timing work", "A tempo is chosen but the math is missing or wrong", "Tempo set at 128 BPM with some correct timing values",
                        "Correct beat, step and bar lengths at 128 BPM and the song’s tempo change", "All timing correct, plus section starts in bars and seconds and a clear explanation"]),
    ("Groove & Pattern", ["No pattern", "A pattern that does not repeat or has no kick on the beats", "A kick on every beat, but the clap or hats are off the grid",
                          "A 4-bar, 16-step pattern: kick on 1, 5, 9, 13, off-beat open hat, clap on 2 and 4", "A steady pattern with variation, and the tune and chords sit in one key"]),
    ("Sidechain", ["No sidechain", "Sidechain tried, but nothing ducks on the kick", "The bass ducks, but the release is not set to the beat",
                   "Bass, pad and tune duck on each kick, with a release timed to the beat", "A well-tuned duck: clean, musical, compared at two release times"]),
    ("Arrangement & Mix", ["No arrangement or mix", "Layers only, no sections", "Sections with an unclear mix or clipping",
                           "A 64-bar arrangement with all six sections, balanced levels and no clipping", "A clear build and a drop that lands, with a balanced mix that ends on time"]),
    ("Plan & Reflection", ["Plans, presentation or reflection missing", "Thin plan; little to say about choices", "Plan and reflection complete, with basic detail",
                           "Correct timing math, step grid and chord table; thoughtful reflection", "Insightful reflection and a polished presentation"]),
]
RUBRIC_TOTAL = 25
RUBRIC_SHORT = ["Correct timing math and a worked-out tempo",
                "A steady four-on-the-floor pattern in one key",
                "A clean sidechain with a release timed to the beat",
                "A build, a drop and a balanced mix",
                "Insightful reflection and a polished presentation"]
RUBRIC_SLIDE_LINE = "Scored 1–5 · final grade = average of your score and mine, out of 25"
RUBRIC_ROW_PITCH = 0.86
RUBRIC_LINE_Y = 6.3

TN_REINFORCES = ("Teaches how a house track is built and why it sounds the way it does. Students work out a tempo with arithmetic, place a four-on-the-floor pattern on a 16-step grid, "
                 "add a bass and chords in one key, use sidechain compression to make room for the kick, and arrange a build, a drop and a break, all in Logic Pro.")
STRUGGLES = ["The beat feels off or the loop drifts: check that the project tempo is 128 BPM and the time signature is 4/4, then count the steps on the step grid (pages @TIMING and @PATTERN).",
             "The bass and the kick fight and the low end is muddy: the bass should play between the kicks, on the off-beats, and the sidechain should turn it down on each kick (pages @CHORDS and @SIDECHAIN).",
             "The sidechain does nothing: the compressor’s side chain must be set to listen to the kick track, and the threshold low enough that the kick pushes the level over it (pages @SIDECHAIN and @ROLES).",
             "The tune clashes with the chords: check each bar’s first tune note against its chord, and try another chord from the table (page @CHORDS)."]
VAR_EASY = ("Keep one key (F major), use the chord loop on page " + str(pg("chords")) + " as written, build only the first 32 bars of the arrangement (intro, build and the first drop) "
            "and use a ready-made drum kit.")
VAR_HARD = ("Compare two release times by ear and write which sounds better (page " + str(pg("sidechain")) + "). Or add a second chord loop for the second drop, "
            "or move the whole remix to another key from the chord table.")
RESOURCES = [("Timing page (page @TIMING)",
              "Milliseconds per beat and per step and seconds per bar at six tempos, the length of 8, 16, 32 and 64 bars at three tempos and the way back from seconds to bars."),
             ("The song and the tune (page @TUNE)",
              "Song facts, a tempo-change table with ratio and percent change, a key and meter note, and a checklist for getting the tune into Logic Pro."),
             ("Step grid and chords (pages @PATTERN and @CHORDS)",
              "A 4-bar, 16-step four-on-the-floor grid with the hits per bar and in all, a blank grid, and a chord table for three keys with a tune-against-chord check."),
             ("Sidechain and layer table (pages @SIDECHAIN and @ROLES)",
              "A gain-reduction curve, a ducking graph at 128 BPM, release times as fractions of a beat, a signal chain and a table of who triggers and who ducks."),
             ("Arrangement, mix and worked example (pages @ARRANGE, @MIX and @EXAMPLE–@EXAMPLE2)",
              "A 64-bar arrangement map with section starts in bars and seconds, a mix checklist, and an invented remix at 128 BPM. A model, not a template.")]
TN_NOTE = ("A good listening day: play each remix and ask the class two questions. Where did the build start, and what changed at the drop? "
           "Can you hear the bass dip on each kick? If a layer is hard to hear, find it on the arrangement map together. This kit includes no recordings and names no existing remixes.")
GRADING = ["The rubric: five categories, each scored 1–5, /25 (page @RUBRIC). Students score themselves first; the final grade is the "
           "average of their score and yours.",
           "Tempo & Timing (rubric row 1): check the timing page and the tempo-change table (pages @TIMING and @TUNE).",
           "Groove & Pattern (rubric row 2): compare the step grid with what plays, and check the kick on every beat (pages @PATTERN and @CHORDS).",
           "Sidechain (rubric row 3): solo the kick and the bass and listen for the dip; ask the student to say their release time and why (pages @SIDECHAIN and @ROLES).",
           "Arrangement & Mix (rubric row 4): play the whole remix and find the intro, build, drops, break and outro on the arrangement map; check the mix checklist (pages @ARRANGE and @MIX).",
           "Plan & Reflection (rubric row 5): the timing page, the feedback questions and the Reflection page (page @REFLECT) are the evidence."]
PACING = [
    {"n": 1, "owner": "Hear the idea, work out the tempo, prepare the song and build the four-on-the-floor beat.",
     "do": "Slides 1–8: the think-and-share, the project, the three classes, four on the floor, the timing math, the step grid and the song. Hand out the timing page, the song page and the step grid. "
           "Before they leave, students have a tempo set to 128 BPM and a 4-bar kick, clap, hat and bass pattern.",
     "slides": (1, 8), "pages": ["timing", "tune", "pattern", "proj1", "proj2", "proj3", "vocab"],
     "deck": "Four on the floor · 128 BPM math · the 16-step grid"},
    {"n": 2, "owner": "Add the chords and the tune, then set up the sidechain.",
     "do": "Slides 9–14: bass and chords, the signal chain, the ducking graph, ratio and threshold, the Logic steps and who ducks. Demonstrate one chord loop, then the side chain on the bass: solo the kick and the bass and listen for the dip. "
           "Walk the room with one question: what is your release time and why?",
     "slides": (9, 14), "pages": ["chords", "sidechain", "roles", "present"], "deck": "Chords and bass · the duck · release time"},
    {"n": 3, "owner": "Arrange 64 bars, mix, bounce, present and reflect.",
     "do": "Slides 15–20: the arrangement, the mix, what to turn in, the rubric, presentation day and the wrap-up. Students arrange, mix, bounce and present.",
     "slides": (15, 20), "pages": ["arrange", "mix", "rubric", "present", "reflect"], "deck": "Arrangement · mix · checklist · presentations"},
]
PACING_EXTRA = (
    '<div class="cols" style="margin-top:4pt;gap:14pt"><div class="box acc-b"><span class="k">The one thing to do on Class 1</span>'
    '<p style="margin:0;font-size:10.6pt">Make sure every student leaves with the project tempo set to 128 BPM and a 4-bar pattern with a kick on every beat, so that Class 2 '
    'is all chords, tune and sidechain. Check the step grids before they go.</p></div>'
    '<div class="box"><span class="k">With two or four periods</span><p style="margin:0;font-size:10.6pt"><b>Two classes:</b> Class 1 is the tempo, the song and the beat; '
    'Class 2 is the chords, the sidechain, the arrangement, the mix and short presentations. <b>Four classes:</b> keep Classes 1 and 2, then spend Class 3 on the arrangement and the mix, and '
    'Class 4 on presentations and reflection.</p></div></div>')
PACING_SIZE = 10.6
TN2_SIZE = 9.6

SONG_NOTE = ("No audio, recordings, lyrics or melody notation are included, and no existing remix, artist or album is named. Students make every "
             "sound themselves and enter the tune from a public-domain score of their own choosing or by ear.")
VOICE_NOTE = ("Students make their OWN remix. They do not sample recordings, videos or games, and they do not copy anyone else’s remix. The only borrowed material is the public-domain tune, "
              "which students enter themselves.")
CREDITS = ["The timing page, the song page, the step grids, the chord table, the sidechain graphs, the layer table, the checklists and the worked example: original work, Hudson Beat. "
           "No melody notation, lyrics, recordings or published editions are included.",
           "The cover illustration was made with digital and AI tools. No audio, video, album art, screenshots, presets, templates, links or "
           "chart data from other sources are included. No student work is included. The compressor and mixing guidance is general practice, "
           "given as starting points to set by ear."]
LOGIC_INTRO = ("Where to find the tools a House Remix is likely to use. Demonstrate what your class needs on Classes 1 and 2 and then "
               "let students work. Names are from current Logic Pro versions; labels move between versions, so check yours.")
LOGIC_REF = [("Project and tempo", "File › New…, then a Software Instrument track. Set the project tempo in the control bar to 128 BPM and keep the time signature at 4/4. "
              "Set the snap or grid value to 16th notes (if your version shows one) so that every hit lands on a step."),
             ("Drums", "Add a Drum Machine Designer track (if your version has it) and load a kick, a clap, a closed hat and an open hat, or use a ready-made kit. The Step Sequencer (if your version has it) shows one row for each "
              "sound and a column for each step: 16 steps to a bar. Or draw notes in the Piano Roll with the grid set to 16th notes."),
             ("Bass and chords", "Add a Software Instrument track with a bass sound and another with a soft pad sound; Retro Synth or Alchemy (each if your version has it) are good places to look. Draw one chord in each bar on the pad, "
              "and the chord’s root on the off-beats for the bass, in the Piano Roll with the grid set to 16th notes."),
             ("Enter the tune", "Play the tune from a keyboard or draw it in the Piano Roll, using a public-domain score or your ear. Logic’s middle C is named C3 by default, so check the octave against the score. "
              "Look for a transpose option on the region (if your version has one) to move the tune to your key."),
             ("Sidechain compression", "Insert a Compressor plug-in on the bass, pad and tune tracks and look for a Side Chain menu in the plug-in window (if your version has it); choose the kick’s track as the side chain source. "
              "Set the ratio, lower the threshold until the gain-reduction meter dips on each kick, make the attack as fast as it will go and set the release by ear, starting near one beat (468.75 ms at 128 BPM). "
              "The control names and scales differ between versions, so listen."),
             ("Timing the release", "Many compressors show release in milliseconds. Work out the beat and the step from the timing page (page " + str(pg("timing")) + ") and type the number in, or turn the control until the meter is back at zero just before the next kick. "
              "Treat every number as a starting point and decide by ear."),
             ("Build and drop", "Arrange your regions along the timeline in sections of 8 or 16 bars. Look for the Marker track (if your version has one) to name the sections. Mute and unmute tracks, or use region automation, "
              "to bring layers in at the build and out at the break."),
             ("Mixer and bounce", "Open the Mixer (the key command is X by default, if your version has it) and set levels and pan. Keep the master peak below 0 dBFS with room to spare. Then File › Bounce › Project or Section (Command-B), MP3 or WAV, for the whole remix. "
              "In Finder, Control-click the .logicx and choose Compress.")]
PRESENT_CHECK = [f"Files named {FILE_NAME}; the .mp3 or .wav and the zipped .logicx handed in",
                 "Reflection page done (page @REFLECT)", "Three questions for classmates written",
                 "Rubric self-score done (page @RUBRIC)"]
VOCAB_PROMPT = "Where it shows up in my remix:"
TN1_EXTRA = (
    '<div class="box acc-b" style="margin-top:4pt"><span class="k">Where this kit helps with each struggle</span><ul style="margin:0">'
    '<li style="font-size:12pt;margin-bottom:3pt">A beat that drifts: the timing page (page @TIMING) gives the length of a beat, a step and a bar at six tempos, and the step grid (page @PATTERN) shows every hit.</li>'
    '<li style="font-size:12pt;margin-bottom:3pt">A muddy low end: the chord page (page @CHORDS) puts the bass between the kicks, and the sidechain page (page @SIDECHAIN) shows the dip.</li>'
    '<li style="font-size:12pt;margin-bottom:3pt">A sidechain that does nothing: the layer table (page @ROLES) shows who triggers and who ducks, with a signal-chain drawing.</li>'
    '<li style="font-size:12pt;margin-bottom:0">A tune that clashes: the chord table checks each bar, and the worked example (pages @EXAMPLE–@EXAMPLE2) shows a full set of choices.</li></ul></div>')
TN1_SIZE = 12.0
PROJ_SIZE = 10.9
VOCAB_GAP = 5
LOGIC_SIZE = 10.2
PROJ1_EXTRA = ""
RUBRIC_EXTRA = ('<div class="box acc-b" style="margin-top:6pt;padding:5pt 10pt"><span class="k">Evidence to look at</span>'
                '<p style="margin:0;font-size:9.6pt;line-height:1.35">Timing: pages @TIMING and @TUNE. Groove: pages @PATTERN and @CHORDS. Sidechain: pages @SIDECHAIN and @ROLES. '
                'Arrangement &amp; Mix: pages @ARRANGE and @MIX. Plan &amp; Reflection: pages @TIMING, @PRESENT and @REFLECT.</p></div>')

# ================================================================ the worked example: an invented remix at 128 BPM
EX_BAR_S = bar_len(EX_BPM)                  # 1.875 s
EX_STEP_S = step_len(EX_BPM)                # 0.1171875 s
EX_WEAK = "I will make a fast version of the song with a drum beat and some bass, and it will sound like a club track."
EX_STRONG = ("My remix is in 4/4 at 128 BPM in F major. One beat lasts 60 ÷ 128 = 0.46875 seconds, one 16th-note step lasts 15 ÷ 128 = 0.1171875 seconds and one bar 240 ÷ 128 = 1.875 seconds. "
             "The song’s plain tempo is about 100 BPM, so my remix is 1.28 times as fast, 28% faster. My 4-bar pattern has 22, 22, 22 and 24 hits, 90 in all, with the kick on grid steps 1, 5, 9 and 13 and the open hat and bass on the off-beats. "
             "The chord loop is F, B-flat, C and D minor. The bass, pad and tune duck on every kick with a release of one beat, 468.75 ms. "
             "My arrangement is 64 bars = 120 seconds: an intro in bars 1 to 8, a build in bars 9 to 16, the drop in bars 17 to 32, a break in bars 33 to 40, a second drop in bars 41 to 56 and an outro in bars 57 to 64, with 6 layers in all.")
EX_QUESTIONS = ["Could you hear the bass dip on every kick?",
                "Where did the build start, and what changed at the drop?",
                "Which layer did you notice first in the break?"]
EX_NOTE = ("the kick never stops in the drops, so the pulse is steady; the bass only plays in the drops, where the sidechain matters most; "
           "the break strips back to the pad and the tune, so the second drop feels bigger")


# ================================================================ drawings (all in code, labels logged for the fit check)
def icon(kind, x, y, s=1.0):
    """A 64 x 64 line icon, drawn at (x, y) scaled by s. Strokes are 4 units; every shape stays at least 3 units inside the 64 x 64 box."""
    k = f'<g transform="translate({x:.1f},{y:.1f}) scale({s})" fill="#fff" stroke="#000" stroke-width="4" stroke-linejoin="round" stroke-linecap="round">'
    if kind == "drum":
        k += (f'<path d="M10 18 V44 A22 9 0 0 0 54 44 V18"/><ellipse cx="32" cy="18" rx="22" ry="9" fill="{ACC_LIGHT}"/>'
              f'<line x1="32" y1="27" x2="32" y2="44" stroke-width="3"/>')
    elif kind == "clap":
        k += (f'<ellipse cx="24" cy="40" rx="9" ry="17" transform="rotate(30 24 40)" fill="{ACC_LIGHT}"/><ellipse cx="40" cy="40" rx="9" ry="17" transform="rotate(-30 40 40)"/>'
              f'<line x1="32" y1="6" x2="32" y2="13" stroke-width="3"/><line x1="14" y1="11" x2="19" y2="17" stroke-width="3"/><line x1="50" y1="11" x2="45" y2="17" stroke-width="3"/>')
    elif kind == "hats":
        k += (f'<ellipse cx="32" cy="20" rx="24" ry="6"/><ellipse cx="32" cy="31" rx="24" ry="6" fill="{ACC_LIGHT}"/>'
              f'<line x1="32" y1="37" x2="32" y2="57"/><line x1="20" y1="57" x2="44" y2="57"/>')
    elif kind in ("rollbass", "rollpad", "rolltune"):
        k += '<rect x="5" y="13" width="54" height="38" rx="5"/>'
        bars = {"rollbass": [(12, 42, 24), (30, 42, 14), (48, 34, 8)], "rollpad": [(12, 24, 40), (12, 32, 40), (12, 40, 40)],
                "rolltune": [(12, 40, 8), (24, 32, 8), (36, 24, 8), (48, 32, 6)]}[kind]
        for bx, by, bl in bars:
            k += f'<line x1="{bx}" y1="{by}" x2="{bx + bl}" y2="{by}" stroke="{ACCENT}" stroke-width="6"/>'
    elif kind == "send":
        k += (f'<circle cx="14" cy="32" r="8" fill="{ACC_LIGHT}"/><line x1="24" y1="32" x2="50" y2="32"/><polyline points="42,24 50,32 42,40"/>')
    elif kind == "comp":
        k += (f'<rect x="5" y="10" width="54" height="44" rx="6"/><circle cx="22" cy="32" r="9" fill="{ACC_LIGHT}"/><line x1="22" y1="32" x2="27" y2="27" stroke-width="3"/>'
              f'<line x1="40" y1="20" x2="40" y2="44" stroke-width="3"/><line x1="48" y1="20" x2="48" y2="44" stroke-width="3"/><line x1="40" y1="30" x2="48" y2="30" stroke-width="3"/>')
    elif kind == "dip":
        k += (f'<polyline points="8,18 24,18 26,48 56,18" fill="none"/><line x1="8" y1="54" x2="56" y2="54" stroke-width="3"/>')
    elif kind == "speaker":
        k += (f'<rect x="14" y="6" width="36" height="52" rx="5"/><circle cx="32" cy="20" r="5" fill="{ACC_LIGHT}"/><circle cx="32" cy="41" r="10" fill="{ACC_LIGHT}"/>')
    else:
        raise ValueError(kind)
    return k + "</g>"


ICON_KINDS = ("drum", "clap", "hats", "rollbass", "rollpad", "rolltune", "send", "comp", "dip", "speaker")


def roles_body(W=1600, name="roles"):
    """The layer table: 6 rows, each an icon, the layer's name, its role chip, two 3-dot meters (pitch, length) and a side-chain chip (TRIGGER, DUCKED or NO DUCK)."""
    out = []
    top = 70
    rh = 84
    cols = {"snd": 120, "role": 400, "pitch": 600, "len": 880, "sc": 1200}
    out.append(f'<rect x="0" y="6" width="{W - 40}" height="46" rx="8" fill="#000"/>')
    for key, lbl in (("snd", "LAYER"), ("role", "ROLE"), ("pitch", "PITCH"), ("len", "LENGTH"), ("sc", "SIDE CHAIN")):
        out.append(D.t_(cols[key] + (0 if key != "snd" else -60), 40, lbl, 26, 700, anchor="start", fill_="#fff"))
        D.lab(name + " heads", lbl, 26, 200)
    chip = {"DRUMS": ("#000", "#fff"), "BASS": (ACCENT, "#fff"), "HARMONY": (ACC_LIGHT, "#000"), "MELODY": ("#fff", "#000")}
    scchip = {"TRIGGER": ("#000", "#fff"), "DUCKED": (ACCENT, "#fff"), "NO DUCK": ("#fff", "#000")}
    for i, (nm, ic, role, p, ln, sc, _, _) in enumerate(SOUNDS):
        y = top + i * rh
        out.append(f'<rect class="row" x="0" y="{y}" width="{W - 40}" height="{rh - 8}" fill="{"#f4f4f4" if i % 2 == 0 else "#fff"}" stroke="#bbb" stroke-width="2"/>')
        out.append(f'<g class="icon">{icon(ic, 18, y + 3, 1.0)}</g>')
        out.append(D.t_(cols["snd"], y + 48, nm, 28, 700, anchor="start"))
        D.lab(name + " names", nm, 28, cols["role"] - cols["snd"] - 30)
        fl, tc = chip[role]
        out.append(f'<rect class="chip" x="{cols["role"]}" y="{y + 14}" width="170" height="42" rx="21" fill="{fl}" stroke="#000" stroke-width="3.5"/>')
        out.append(D.t_(cols["role"] + 85, y + 44, role, 26, 700, fill_=tc))
        D.lab(name + " chips", role, 26, 150)
        for key, lv, words in (("pitch", p, PITCH_W), ("len", ln, LEN_W)):
            out.append(meter(cols[key], y + 35, lv))
            out.append(D.t_(cols[key] + 124, y + 44, words[lv], 24, 700, anchor="start", fill_="#222"))
            D.lab(name + " words", "MEDIUM", 24, 110)
        fl, tc = scchip[sc]
        out.append(f'<rect class="scchip" x="{cols["sc"]}" y="{y + 14}" width="190" height="42" rx="21" fill="{fl}" stroke="#000" stroke-width="3.5"/>')
        out.append(D.t_(cols["sc"] + 95, y + 44, sc, 26, 700, fill_=tc))
        D.lab(name + " scchips", "NO DUCK", 26, 170)
    bot = top + NSND * rh
    cap = f"{NSND} layers, {len(ROLES)} roles. The kick triggers the duck; {len(DUCKED)} of them duck. The dots are what to listen for, not measurements."
    out.append(D.t_((W - 40) / 2, bot + 28, cap, 23, 700, "Source Sans 3"))
    D.lab(name + " cap", cap, 23, W - 80)
    return padded("".join(out), W - 40, bot + 44, 16)


def grid_body(W=1600, name="grid", blank=False):
    """The 4-bar pattern on a step grid: one lane for each of the 5 lanes by 64 steps (4 bars of 16). Hit cells carry class="hit", every cell class="cell"."""
    gx = 215
    pw = W - gx - 34
    cw = pw / (PAT_BARS * STEPS_BAR)
    ch = 46
    top = 92
    bot = top + NLANE * ch
    out = []
    for b in range(PAT_BARS):
        for s in range(STEPS_BAR):
            for ln in range(NLANE):
                out.append(f'<rect class="cell" x="{gx + (b * STEPS_BAR + s) * cw:.1f}" y="{top + ln * ch}" width="{cw:.1f}" height="{ch}" fill="{"#f4f4f4" if (s // 4) % 2 == 0 else "#fff"}" '
                           f'stroke="#bbb" stroke-width="1.5"/>')
    for ln, nm in enumerate(LANES):
        out.append(D.t_(gx - 14, top + ln * ch + 31, nm, 22, 700, anchor="end"))
        D.lab(name + " lanes", "CLOSED HAT", 22, gx - 22)
    if not blank:
        for ln, nm in enumerate(LANES):
            for b in range(PAT_BARS):
                for st in PATTERN[nm][b]:
                    x = gx + (b * STEPS_BAR + st - 1) * cw
                    out.append(f'<rect class="hit" x="{x + 2.5:.1f}" y="{top + ln * ch + 6}" width="{cw - 5:.1f}" height="{ch - 12}" rx="4" fill="{"#000" if nm == "KICK" else ACCENT}" stroke="#000" stroke-width="2.5"/>')
    for k in range(PAT_BARS * 4 + 1):
        x = gx + k * 4 * cw
        out.append(f'<line x1="{x:.1f}" y1="{top}" x2="{x:.1f}" y2="{bot}" stroke="{"#000" if k % 4 == 0 else "#777"}" stroke-width="{4 if k % 4 == 0 else 2}"/>')
    out.append(f'<rect x="{gx}" y="{top}" width="{pw}" height="{bot - top}" fill="none" stroke="#000" stroke-width="4"/>')
    for b in range(PAT_BARS):
        x0 = gx + b * STEPS_BAR * cw
        out.append(D.t_(x0 + 10, 36, f"BAR {b + 1}", 24, 700, anchor="start", fill_=ACCENT))
        for beat in range(BEATS_BAR):
            out.append(D.t_(x0 + (beat * 4 + 0.5) * cw, 76, str(beat + 1), 20, 700, "Source Sans 3", fill_="#222"))
            out.append(D.t_(x0 + (beat * 4 + 2.5) * cw, 76, "&", 20, 500, "Source Sans 3", fill_=ACCENT))
        lbl = "hits: ______" if blank else f"{PAT_HITS[b]} hits"
        out.append(D.t_(x0 + STEPS_BAR * cw / 2, bot + 38, lbl, 24, 700))
        D.lab(name + " hits", lbl, 24, STEPS_BAR * cw - 20)
    out.append(D.t_(gx - 14, 76, "BEAT", 20, 700, anchor="end", fill_=ACCENT))
    cap = (f"{PAT_BARS} bars of {STEPS_BAR} steps = {PAT_BARS * STEPS_BAR} steps. Each beat is 4 steps; the & is the off-beat. " + ("Draw a hit in the lane of each sound you play." if blank else f"{PAT_TOTAL} hits in all."))
    out.append(D.t_(gx + pw / 2, bot + 82, cap, 23, 500, "Source Sans 3"))
    D.lab(name + " cap", cap, 23, pw)
    return padded("".join(out), W, bot + 98, 16)


ARR_BAND = {"KICK": "#555", "CLAP": "#fff", "HATS": "#d9d9d9", "BASS": ACCENT, "PAD": ACC_LIGHT, "MELODY": "#999"}


def arr_body(W=1600, name="arrange"):
    """The 64-bar arrangement at 128 BPM: six sections, six layers (one for each row), bars along the top and seconds along the bottom."""
    gx = 200
    pw = W - gx - 34
    bw = pw / ARR_BARS
    rh, gap = 46, 8
    top = 126
    out = []
    for nm, a, b in ARR_SECTIONS:
        x0 = gx + (a - 1) * bw
        out.append(f'<rect class="sec" x="{x0 + 2:.1f}" y="12" width="{(b - a + 1) * bw - 4:.1f}" height="44" rx="8" fill="{ACCENT if nm == "DROP" else "#000"}"/>')
        lbl = f"{nm} {a}–{b}"
        out.append(D.t_(x0 + (b - a + 1) * bw / 2, 42, lbl, 21, 700, fill_="#fff"))
        D.lab(name + " sections", lbl, 21, (b - a + 1) * bw - 12)
    for nm, a, b in ARR_SECTIONS:
        out.append(D.t_(gx + (a - 1) * bw + 3, 94, str(a), 22, 700, anchor="start"))
    out.append(D.t_(gx - 14, 94, "BAR", 22, 700, anchor="end", fill_=ACCENT))
    for r, (nm, spans) in enumerate(ARR_ROWS):
        y = top + r * (rh + gap)
        out.append(f'<rect class="lane" x="{gx}" y="{y}" width="{pw}" height="{rh}" fill="#fff" stroke="#bbb" stroke-width="2"/>')
        out.append(D.t_(gx - 14, y + rh / 2 + 8, nm, 22, 700, anchor="end"))
        D.lab(name + " rows", "MELODY", 22, gx - 24)
        for a, b in spans:
            out.append(f'<rect class="block" x="{gx + (a - 1) * bw + 2:.1f}" y="{y + 5}" width="{(b - a + 1) * bw - 4:.1f}" height="{rh - 10}" rx="7" fill="{ARR_BAND[nm]}" stroke="#000" stroke-width="3"/>')
    bot = top + len(ARR_ROWS) * (rh + gap) - gap
    cy = bot + 30
    out.append(D.t_(gx - 14, cy + 36, "LAYERS", 22, 700, anchor="end", fill_=ACCENT))
    for b in range(1, ARR_BARS + 1):
        out.append(D.t_(gx + (b - 0.5) * bw, cy + 34, str(len(layers_in_bar(b))), 22, 700, extra='class="cnt"'))
    bounds = [a for _, a, _ in ARR_SECTIONS] + [ARR_BARS + 1]
    for k, bar in enumerate(bounds):
        x = gx + (bar - 1) * bw
        out.append(f'<line x1="{x:.1f}" y1="{top - 8}" x2="{x:.1f}" y2="{bot + 12}" stroke="#000" stroke-width="3" stroke-dasharray="9 7"/>')
        s = hit_time(EX_BPM, bar, 1)
        out.append(D.t_(x, cy + 86, exact(s), 24, 700, anchor="start" if k == 0 else ("end" if k == len(bounds) - 1 else "middle")))
    out.append(D.t_(gx - 14, cy + 86, "SECONDS", 22, 700, anchor="end", fill_=ACCENT))
    D.lab(name + " rows", "SECONDS", 22, gx - 24)
    cap = f"{ARR_BARS} bars at {EX_BPM} BPM = {fmt(ARR_BARS * EX_BAR_S)} seconds, with {len(ARR_ROWS)} layers. The number row shows how many layers sound in each bar."
    out.append(D.t_(gx + pw / 2, cy + 134, cap, 23, 700, "Source Sans 3"))
    D.lab(name + " cap", cap, 23, pw)
    return padded("".join(out), W, cy + 150, 16)


CHAIN_STAGES = [("KICK TRACK", "drum", "plays every beat"), ("SIDE CHAIN", "send", "sends its level"), ("COMPRESSOR", "comp", "on bass, pad, tune"),
                ("LEVEL DIPS", "dip", "on each kick"), ("MIX", "speaker", "kick stays clear")]


def chain_body(W=1620, name="chain"):
    """The sidechain signal chain from the kick to the mix: five stages (class "stage") joined by four arrows (class "arrow")."""
    stages = CHAIN_STAGES
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
    cap = f"From the kick to the mix in {len(stages)} stages: the kick is the trigger, the bass, pad and tune are turned down."
    out.append(D.t_(wtot / 2, 14 + sh + 48, cap, 25, 700, "Source Sans 3"))
    D.lab(name + " cap", cap, 25, wtot - 40)
    return padded("".join(out), wtot, 14 + sh + 66, 16)


def ptl_pos(db, xs, ys, frame_r):
    """Where the data label of the dot at kick level db sits: above the dot, except the dot on the threshold line (upper left) and the dot on the frame's right edge (the 15), whose label goes below and to the left so its halo stays clear of the frame and the curve."""
    x, y = xs(db), ys(gain_reduction(db))
    if x > frame_r - 40:
        return x - 16, y + 62, "end"
    if db == THRESH_DB:          # the dot on the dashed threshold line: label to its upper left, clear of the line
        return x - 18, y - 22, "end"
    if gain_reduction(db) >= 10:  # a two-digit label would run into the rising curve on its right: shift it left
        return x + 8, y - 22, "end"
    return x, y - 22, "middle"


def curve_body(W=1500, name="curve"):
    """The gain-reduction curve for the stated threshold and ratio: the kick's level at the side chain (-40 to 0 dB) against the gain reduction on a ducked track (0 to 16 dB),
    plotted from gain_reduction(). The polyline is the line; every dot (class "pt") is one level of the table, labeled with its gain reduction."""
    gx, gy0, gy1 = 210, 70, 400
    pw = W - gx - 70
    xs = lambda db: gx + (db + 40) / 40 * pw
    ys = lambda gr: gy1 - float(gr) / 16 * (gy1 - gy0)
    out = []
    for db in range(-40, 1, 10):
        out.append(f'<line x1="{xs(db):.1f}" y1="{gy0}" x2="{xs(db):.1f}" y2="{gy1}" stroke="#ccc" stroke-width="2"/>')
        out.append(D.t_(xs(db), gy1 + 36, str(db).replace("-", "−"), 30, 700))
    for gr in range(0, 17, 4):
        out.append(f'<line x1="{gx}" y1="{ys(gr):.1f}" x2="{gx + pw}" y2="{ys(gr):.1f}" stroke="#ccc" stroke-width="2"/>')
        out.append(D.t_(gx - 14, ys(gr) + 8, str(gr), 30, 700, anchor="end"))
    out.append(f'<rect x="{gx}" y="{gy0}" width="{pw}" height="{gy1 - gy0}" fill="none" stroke="#000" stroke-width="4"/>')
    out.append(f'<line x1="{xs(THRESH_DB):.1f}" y1="{gy0}" x2="{xs(THRESH_DB):.1f}" y2="{gy1}" stroke="{ACCENT}" stroke-width="4" stroke-dasharray="10 7"/>')
    lbl = f"threshold {THRESH_DB} dB".replace("-", "−")
    out.append(D.t_(xs(THRESH_DB) - 12, gy0 + 28, lbl, 30, 700, anchor="end", fill_=ACCENT))
    D.lab(name + " thr", lbl, 30, xs(THRESH_DB) - gx - 20)
    pts = " ".join(f"{xs(db):.1f},{ys(gain_reduction(db)):.1f}" for db in (-40, THRESH_DB, 0))
    out.append(f'<polyline class="line" points="{pts}" fill="none" stroke="#000" stroke-width="6" stroke-linejoin="round" stroke-linecap="round"/>')
    for db in KICK_LEVELS:
        g = gain_reduction(db)
        out.append(f'<circle class="pt" cx="{xs(db):.1f}" cy="{ys(g):.1f}" r="11" fill="{ACCENT}" stroke="#000" stroke-width="3.5"/>')
        lx, ly, la = ptl_pos(db, xs, ys, gx + pw)
        out.append(D.t_(lx, ly, exact(g), 30, 700, anchor=la, extra='class="ptl" paint-order="stroke" stroke="#fff" stroke-width="8" stroke-linejoin="round"'))
    ratio_txt = f"ratio {RATIO}:1"
    out.append(D.t_(xs(-30), ys(10), ratio_txt, 36, 700, fill_=ACCENT))
    D.lab(name + " ratio", ratio_txt, 36, 260)
    out.append(D.t_(gx + pw / 2, gy1 + 82, "KICK LEVEL AT THE SIDE CHAIN (dB)", 30, 700))
    D.lab(name + " xaxis", "KICK LEVEL AT THE SIDE CHAIN (dB)", 30, pw)
    out.append(D.t_(56, (gy0 + gy1) / 2, "GAIN REDUCTION (dB)", 30, 700, extra=f'transform="rotate(-90 56 {(gy0 + gy1) / 2})"'))
    D.lab(name + " yaxis", "GAIN REDUCTION (dB)", 30, gy1 - gy0)
    cap = f"Example settings: 4:1 turns 4 dB over the threshold into 3 dB down. Not Logic’s defaults."
    out.append(D.t_(gx + pw / 2, gy1 + 128, cap, 27, 700, "Source Sans 3"))
    D.lab(name + " cap", cap, 27, pw + 60)
    return padded("".join(out), W, gy1 + 146, 16)


REL_STEPS = 4                       # the example release is one beat = 4 steps


def duck_body(W=1500, name="duck"):
    """One bar at 128 BPM drawn in time: four kicks (class "kick", on grid steps 1, 5, 9 and 13) and the bass level, which dips at each kick (class "dip") and rises in a straight line over the release
    time (the example release is one beat). A schematic: a real compressor's recovery curve is rounder."""
    gx = 200
    pw = W - gx - 50
    bar_ms = ms(EX_BAR_S)
    px = lambda t_ms: gx + float(Fraction(t_ms) / bar_ms) * pw
    top_y, low_y, kick_y = 210, 330, 92
    out = []
    out.append(f'<rect x="{gx}" y="52" width="{pw}" height="{low_y + 40 - 52}" fill="none" stroke="#000" stroke-width="4"/>')
    for s in range(1, STEPS_BAR + 1):
        x = px(ms((s - 1) * step_len(EX_BPM)))
        out.append(f'<line x1="{x:.1f}" y1="52" x2="{x:.1f}" y2="{low_y + 40}" stroke="{"#777" if s in FLOOR_STEPS else "#ddd"}" stroke-width="{3 if s in FLOOR_STEPS else 1.5}"/>')
    out.append(D.t_(gx - 14, kick_y + 8, "KICK", 24, 700, anchor="end"))
    out.append(D.t_(gx - 14, top_y + 8, "BASS", 24, 700, anchor="end"))
    out.append(D.t_(gx - 14, top_y + 36, "LEVEL", 24, 700, anchor="end"))
    D.lab(name + " rows", "LEVEL", 24, gx - 24)
    rel = ms(REL_STEPS * step_len(EX_BPM))
    base = f'M{px(0):.1f},{top_y}'
    for s in FLOOR_STEPS:
        t0 = ms((s - 1) * step_len(EX_BPM))
        x0, x1 = px(t0), px(t0 + rel)
        out.append(f'<circle class="kick" cx="{x0 + 14:.1f}" cy="{kick_y}" r="16" fill="#000"/>')
        out.append(f'<polyline class="dip" points="{x0:.1f},{top_y} {x0 + 3:.1f},{low_y} {x1:.1f},{top_y}" fill="{ACC_LIGHT}" stroke="{ACCENT}" stroke-width="6" stroke-linejoin="round"/>')
        lbl = f"grid step {s}"
        out.append(D.t_(x0 + 10, low_y + 72, lbl, 22, 700, anchor="start"))
        D.lab(name + " steps", "grid step 13", 22, 150)
        t_lbl = f"{exact(t0)} ms"
        out.append(D.t_(x0 + 10, low_y + 100, t_lbl, 22, 500, "Source Sans 3", anchor="start", fill_="#222"))
        D.lab(name + " times", f"1406.25 ms", 22, 130)
    out.append(f'<line x1="{gx}" y1="{top_y}" x2="{gx + pw}" y2="{top_y}" stroke="#bbb" stroke-width="2" stroke-dasharray="6 6"/>')
    x0, x1 = px(0), px(rel)
    out.append(f'<line x1="{x0 + 3:.1f}" y1="{low_y + 24}" x2="{x1:.1f}" y2="{low_y + 24}" stroke="#000" stroke-width="4"/>')
    out.append(f'<polyline points="{x0 + 15:.1f},{low_y + 14} {x0 + 3:.1f},{low_y + 24} {x0 + 15:.1f},{low_y + 34}" fill="none" stroke="#000" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>')
    out.append(f'<polyline points="{x1 - 12:.1f},{low_y + 14} {x1:.1f},{low_y + 24} {x1 - 12:.1f},{low_y + 34}" fill="none" stroke="#000" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>')
    rl = f"release {exact(rel)} ms"
    out.append(D.t_((x0 + x1) / 2 + 40, low_y + 6, rl, 24, 700, "Oswald", fill_="#000", extra='paint-order="stroke" stroke="#fff" stroke-width="7"'))
    D.lab(name + " rel", rl, 24, float(x1 - x0) - 60)
    cap = f"One bar = {exact(bar_ms)} ms = 16 steps. The bass dips at each kick and returns over the release (a schematic)."
    out.append(D.t_(gx + pw / 2, low_y + 140, cap, 23, 700, "Source Sans 3"))
    D.lab(name + " cap", cap, 23, pw)
    return padded("".join(out), W, low_y + 158, 16)


def hero_body():
    """The library art (art/hero.png, used whole and unchanged). The viewBox is the whole 1400 x 1400 file plus 24 units of clear padding on every side, which --check proves from the file."""
    return (f'<image href="../art/hero.png" x="{-HX}" y="{-HY}" width="1400" height="1400"/>', HW, HH)


HX, HY, HW, HH = -24, -24, 1448, 1448

DRAWINGS = {"hero": hero_body, "grid": lambda: grid_body(1600, "grid deck"), "chain": lambda: chain_body(1620, "chain deck"), "duck": lambda: duck_body(1500, "duck deck"),
            "curve": lambda: curve_body(1500, "curve deck"), "roles": lambda: roles_body(1600, "roles deck"), "arrange": lambda: arr_body(1600, "arrange deck")}
DRAWING_PX = {"hero": 1340, "grid": 2000, "chain": 2000, "duck": 1800, "curve": 1800, "roles": 2000, "arrange": 2000}
SIDE = {"grid": ["16 steps in a bar, 4 beats of 4 steps", "Kick on grid steps 1, 5, 9 and 13"],
        "chain": ["The kick sends its level", "The compressor turns the others down"],
        "duck": ["The bass dips on every kick", "Release: one beat, 468.75 ms"],
        "curve": ["4:1 turns 4 dB over into 3 dB down", "Example settings, not defaults"],
        "roles": ["6 layers, 4 roles", "3 of the 6 layers duck on the kick"],
        "arrange": ["Intro, build, drop, break, drop, outro", "64 bars at 128 BPM are 120 seconds"]}
# extra drawings used on pages only, rendered alone on a transparent ground by --check as well
PAGE_DRAWINGS = {"chain-page": lambda: chain_body(1620, "chain page"), "roles-page": lambda: roles_body(1600, "roles page"), "grid-page": lambda: grid_body(1600, "grid page"),
                 "grid-blank-page": lambda: grid_body(1600, "grid blank page", blank=True), "duck-page": lambda: duck_body(1500, "duck page"), "curve-page": lambda: curve_body(1500, "curve page"),
                 "arrange-page": lambda: arr_body(1600, "arrange page")}


def label_extras():
    for k, fn in PAGE_DRAWINGS.items():
        fn()


# ================================================================ intro deck: (class, kind, title, body, speaker notes)
SLIDES = [
    (1, "title", "House Remix", "Four on the floor, ducked",
     "Class 1, the first minute. No audio is included in this deck. Open with the idea: you will remix one traditional winter song as a house track at 128 BPM. A kick lands on every beat, "
     "hats tick between the beats, the bass gets out of the kick's way, and you build a drop. Nobody needs to read music, and no existing remix or recording is used."),
    (1, "listen", "Hear the track", "Think, then share|Teacher: read aloud, no audio plays. A kick thumps on every beat. A hat ticks between the beats. Claps land on 2 and 4. "
     "Then the bass dips each time the kick hits.|Which sound would you build the track around?|Where would the bass go so it does not fight the kick?|"
     "What makes a room want to move?",
     "Read the scene aloud slowly and ask the three questions. Take a few answers. Nothing is played from a speaker. Students will say the kick or the bass. Write their words on the board. "
     "The project turns each idea into a tool with a number attached: a tempo, a step grid, a chord loop and a sidechain."),
    (1, "bullets", "What is the House Remix?", "Remix one traditional winter song|Work out the tempo: 128 BPM|Build a four-on-the-floor beat|Add bass, chords and a sidechain duck",
     "The project in four lines. Every student remixes one public-domain tune as a house track in Logic Pro. They work out the tempo with arithmetic, build a kick, clap, hat and bass pattern on a 16-step grid, "
     "add a four-chord loop and the tune, set up sidechain compression so the bass, pad and tune duck on each kick, and arrange 64 bars with a build and a drop. No audio ships: students make every sound."),
    (1, "days", "Three classes", "",
     "The shape of the project. Class 1: hook, four on the floor, the timing math, the step grid and the song. Class 2: chords, bass, the tune and the sidechain. Class 3: arrangement, mix, "
     "bounce, present and reflect. The badge on this slide reads Classes 1 to 3 because it covers all three. With two classes, do the tempo, song and beat in Class 1 and the rest in Class 2; "
     "with four, add a day for presentations. Hand out the timing page and the song page now."),
    (1, "bullets", "Four on the floor", "The kick is hit on every beat: 1, 2, 3 and 4|Open hats sit on the off-beats, halfway between kicks|Claps land on beats 2 and 4|House music is typically 115 to 130 BPM",
     "Class 1. Four on the floor is a steady 4/4 rhythm in which the bass drum is hit on every beat. In house music the bass drum is usually played on all four beats, with claps or snares on beats 2 and 4 and hi-hats "
     "on the off-beats, at a tempo that is typically 115 to 130 BPM, and 120 to 130 in its most typical form. 128 sits inside both ranges. The off-beat is the halfway point between two beats: the word and in one, and, two, and."),
    (1, "bullets", "The math: 128 BPM", "One beat lasts 60 ÷ 128 = 0.46875 s (468.75 ms)|One 16th-note step lasts 15 ÷ 128 = 0.1171875 s (117.19 ms)|One bar of 4/4 lasts 240 ÷ 128 = 1.875 s|16 bars last 30 s and 64 bars last 120 s",
     f"Class 1, the key idea. In 4/4 there are four beats in a bar and each beat holds four 16th-note steps, so a bar has 16 steps. One beat lasts 60 divided by the tempo, one step lasts 15 divided by the tempo and one bar lasts 240 divided by the tempo: "
     f"at 128 BPM that is 468.75 milliseconds, 117.19 milliseconds (the exact value is 117.1875) and 1.875 seconds. A 16-bar section lasts 30 seconds and 64 bars last 120 seconds. The timing page is page {pg('timing')}."),
    (1, "pic", "The 16-step house grid", "grid",
     f"Class 1. The model pattern on a step grid: 5 lanes and 64 steps, which is 4 bars of 16. Each beat is 4 steps. The kick plays on grid steps 1, 5, 9 and 13, the open hat and the bass on the off-beats 3, 7, 11 and 15, "
     f"the clap on 5 and 13, and the closed hat on the even steps. The hits per bar are 22, 22, 22 and 24, 90 in all; bar 4 adds a two-hit clap fill. At 128 BPM the kick on bar 2, grid step 5 is at (16 + 4) × 0.1171875 = 2.34375 seconds. "
     f"Students draw their own pattern on the blank grid on page {pg('pattern')}. The Step Sequencer (if your version has it) shows the same grid."),
    (1, "bullets", "Prepare the song", "The tune is public domain; its words are not used|Compare its usual tempo with 128 BPM|Choose a key; the examples use F major|Enter the tune from a score or by ear",
     f"Class 1. The song is a traditional Welsh melody that dates back to the sixteenth century and was in print by the 1790s; it is far older than any copyright. This kit uses the tune only. A plain version might run near 100 BPM: that is an example, "
     f"and 128 divided by 100 is 1.28, so the remix is 28 percent faster. The song page is page {pg('tune')}; it has a table for four plain tempos. Key and meter are choices for the remix: the examples use F major and 4/4."),
    (2, "bullets", "Bass and chords", "One chord in each bar: I, IV, V and vi|In F major: F, B-flat, C and D minor|The bass plays the chord’s root on the off-beats|Check each bar’s first tune note against its chord",
     f"Class 2. A four-chord loop: one chord a bar, I, IV, V and vi, so the loop lasts 4 bars, 7.5 seconds at 128 BPM. In F major the chords are F, B-flat, C and D minor, each made by stacking thirds in the scale. The bass plays the root of the chord on the off-beats, "
     f"grid steps 3, 7, 11 and 15, so it never lands on a kick. Students check the first tune note of each bar against the chord: if it is one of the chord's three notes it fits. The chord page is page {pg('chords')}."),
    (2, "pic", "Kick triggers the duck", "chain",
     f"Class 2. The sidechain in five stages. 1: the kick track plays on every beat. 2: its level is sent to the side chain input of a compressor. 3: the compressor sits on the bass, pad and tune tracks. 4: whenever the kick is loud enough, the compressor turns those tracks down. "
     f"5: the result is a mix where the kick stays clear. A compressor with a side chain input controls the gain of one signal from the level of another; in dance music it is often used on basslines, controlled by the kick drum, to keep the two from conflicting. "
     f"The layer table and the signal chain are on page {pg('roles')}; the quick reference is page {pg('logicref')}."),
    (2, "pic", "Ducking in time", "duck",
     f"Class 2. One bar at 128 BPM drawn in time. The kicks are on grid steps 1, 5, 9 and 13, at 0, 468.75, 937.5 and 1406.25 milliseconds. At each kick the bass level dips and then rises over the release time; here the release is one beat, 468.75 milliseconds, "
     f"so the level is back to full just as the next kick hits. This is a schematic: a real compressor recovers on a curve, and there is no industry standard for what the time numbers mean, so students set the release by ear. The ducking page is page {pg('sidechain')}."),
    (2, "pic", "Ratio and threshold", "curve",
     f"Class 2. The gain-reduction curve for this kit's example settings: a threshold of minus 20 dB and a ratio of 4:1. Below the threshold nothing happens. Above it, every 4 dB over is turned down by 3 dB, which is the ratio worked example. "
     f"A kick at 0 dB is 20 dB over the threshold, so it turns the bass down by 15 dB. The six plotted points are 0, 3, 6, 9, 12 and 15 dB. These are the kit's own example values, not Logic's defaults: in Logic students lower the threshold until the meter dips on each kick. The page is page {pg('sidechain')}."),
    (2, "steps", "Set up the sidechain in Logic", "Insert a Compressor on the bass, pad and tune tracks|Look for the Side Chain menu in the plug-in window, if your version has it|Choose the kick track as the source|"
     "Lower the threshold until the meter dips on each kick|Make the attack as fast as it goes; set the release by ear",
     f"Class 2. Demonstrate on the projector. Insert a Compressor plug-in on the bass, then look for a Side Chain menu in the plug-in window (if your version has it) and choose the kick's track. Solo the kick and the bass together. Lower the threshold until the "
     f"gain-reduction meter dips on every kick and returns before the next one. Make the attack as fast as it will go and start the release near one beat, 468.75 milliseconds, then decide by ear. Menu names and control scales move between versions; "
     f"the quick reference on page {pg('logicref')} hedges where they do. Repeat for the pad and the tune, or copy the settings."),
    (2, "pic", "Who triggers, who ducks", "roles",
     f"Class 2. The layer table: 6 layers, each with an icon, a role and a side chain chip. The kick triggers the duck. The bass, the pad and the tune are ducked. The clap and the hats are not ducked: they sit on different steps and do not need it. "
     f"The dots are descriptions to listen for, not measurements. Students use the table on page {pg('roles')} to check that every layer that should duck is routed to the kick."),
    (3, "pic", "Arrange 64 bars", "arrange",
     f"Class 3. A 64-bar arrangement at 128 BPM: an intro in bars 1 to 8, a build in bars 9 to 16, the drop in bars 17 to 32, a break in bars 33 to 40, a second drop in bars 41 to 56 and an outro in bars 57 to 64. There are 6 layers. "
     f"The number row shows how many layers sound in each bar: 2 in bars 1 to 4, 3 in bars 5 to 16, 6 in bars 17 to 32, 2 in bars 33 to 40, 6 in bars 41 to 56, 3 in bars 57 to 60 and 2 in bars 61 to 64. 64 bars of 1.875 seconds are 120 seconds, and the sections start at 0, 15, 30, 60, 75 and 105 seconds. The arrangement page is page {pg('arrange')}."),
    (3, "bullets", "Mix: start with the levels", "Set the kick and the bass first, then add the rest|Keep every layer audible in the drop|Leave the master below 0 dBFS with room to spare|Listen to the break: does the drop land?",
     f"Class 3. Set the kick and the bass first because they carry the track, then bring in the clap, hats, pad and tune. The sidechain duck should make room for the kick without making the bass disappear: if it does, shorten the release or raise the threshold. "
     f"Leave plenty of headroom on the master and keep the peak below 0 dBFS. The mix checklist is on page {pg('mix')}, and the quick reference is page {pg('logicref')}."),
    (3, "check", "What you turn in", "Bounced .mp3 or .wav, 64 bars long|Zipped .logicx project|Named: Your Name – House Remix|Timing page, step grid and chord table|Reflection page|Rubric self-score and three questions",
     "Class 3. The submission checklist, shortened to fit the slide. Show where students hand in. The file name is Your Name, then House Remix. Check the length before students bounce: "
     "the bounce should run all 64 bars, which is 120 seconds at 128 BPM; the timing page shows how many seconds that is at other tempos."),
    (3, "rubric", "How it’s scored", "",
     "The rubric: five categories, each scored 1 to 5, for a total out of 25. Students score themselves first; the final grade is the average of their score and yours. "
     "The slide reads the 5 column of each category aloud. Hand out the rubric page so students can self-score before they present."),
    (3, "bullets", "Presentation day", "Play your remix from the top|Point out the build, the drop and the duck|Your three questions for classmates|Answer at least 2 of each classmate’s questions",
     "Class 3, presentations. Each student plays the remix and points out the build, the drop, the break and the sidechain duck as they arrive, with their bar numbers. Students write three "
     "questions they want classmates to answer, and answer at least two of each classmate's. Ask the class where they heard the bass dip on the kick and when the drop landed."),
    (3, "closer", "One last thing…", "Work out the tempo.|Put the kick on every beat.|Duck what gets in its way.|Then let the drop land.",
     "Close with the listening day: play a remix and ask the class whether they could hear the kick under everything and where the track built. A remix that nobody can place by the second drop is a remix that was well planned. "
     "Ask a few students which choice did the most for their track. No audio is included in this resource; the sounds are the students' own."),
]
SHOTS1 = [("pacing", "Pacing guide", "3 class periods, slide by slide"), ("pattern", "Step grid", "4 bars, 16 steps, 5 lanes"),
          ("sidechain", "Sidechain", "gain curve, ducking graph, release")]
SHOTS2 = [1, 7, 10, 11, 12, 15]
SHOTS3 = [("timing", "Timing math"), ("tune", "The song"), ("pattern", "Step grid"), ("chords", "Chord table"), ("sidechain", "Sidechain"), ("roles", "Layer table"),
          ("arrange", "Arrangement"), ("mix", "Mix")]
PREVIEW_PICKS = ["pacing", "pattern", "sidechain", "arrange"]

COVER_A = "Kick, bass, sidechain, drop"
COVER_C = "Logic Pro · 128 BPM · Sidechain · Four on the Floor"
PDF_COVER = dict(a=26, b=42, c=15, art=5.0)
SQ_COVER = dict(a=36, b=140, c=27, art=470, gap=20)
SQ_B_LINES = ["House", "Remix"]
SQ_SUB = "3 class periods · one traditional song at 128 BPM"
SQ_HEADS = {1: ("Ready to teach Monday", 76, "Pacing, step grid, sidechain page and the /25 rubric in one PDF", 28),
            2: ("Intro deck included", 76, f"{len(SLIDES)} editable slides (.pptx + PDF) with speaker notes on every slide", 28),
            3: ("Everything inside", 72, "Timing math, step grid, chords, sidechain graphs and worked example", 28)}
SQ_BANDS = {1: "128 BPM <em>·</em> four on the floor <em>·</em> sidechain",
            2: "Step grid <em>·</em> sidechain <em>·</em> arrangement",
            3: f"{len(PLAN)} pages <em>·</em> US Letter PDF <em>·</em> no audio included"}


# ================================================================ small page helpers
CSS_CC = ("<style>table.cc td { text-align: center; padding: 2pt 3pt; font-size: 9.4pt; line-height: 1.15; } table.cc th { text-align: center; font-size: 9pt; } "
          "table.cc td.l { text-align: left; } table.cc tr.hi td { background: #eef5fb; }</style>")


def howto_page(n, wm=False):
    parts = [("Teacher pages", "howto", "example2", "How to use, overview, setup, pacing, teacher notes, Logic quick reference, worked example (2 pages)"),
             ("Student pages", "timing", "reflect", "Timing page, the song, step grid, chord table, sidechain pages (2), arrangement, mix checklist, "
              "project sheet (3 pages), rubric, vocabulary, feedback planner, reflection page"),
             ("Intro deck (separate file)", None, None, f"{len(SLIDES)} slides, .pptx + PDF, speaker notes on every slide")]
    trs = "".join(f"<tr><td><b>{a}</b></td><td style='white-space:nowrap'>{('pages ' + str(D.IX(f)) + '–' + str(D.IX(l))) if f else 'deck'}</td>"
                  f"<td>{u}</td></tr>" for a, f, l, u in parts)
    inner = (f'<div class="cols"><div>'
             f'{D.H2("What this is", True)}'
             f'<p style="font-size:12pt;line-height:1.45">A {CLASSES}-class-period house remix project for high school music technology. Every '
             f'student remixes one traditional winter song at 128 BPM: they work out the timing, build a four-on-the-floor pattern on a 16-step grid, add a four-chord loop and the tune, '
             f'set up sidechain compression so the bass, pad and tune duck on each kick, and arrange and mix 64 bars with a build and a drop. Students plan with simple arithmetic, present the result and reflect on it. It is an original Hudson Beat project.</p>'
             f'{D.H2("Quick start")}<ol>'
             f'<li style="margin-bottom:5pt">Read the pacing guide (page {D.IX("pacing")}) and the teacher notes (pages {D.IX("tn1")}–{D.IX("tn2")}).</li>'
             f'<li style="margin-bottom:5pt">Look at the timing page, the song page, the step grid, the chord page and the sidechain pages (pages {D.IX("timing")}–{D.IX("roles")}) and the setup (page {D.IX("setup")}).</li>'
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
             f'<li><b>Pace:</b> Class 1 tempo, song and beat; Class 2 chords, tune and sidechain; Class 3 arrangement, mix and presentations (page {D.IX("pacing")}, which also shows two and four periods).</li>'
             f'<li><b>Grading:</b> the rubric, /{RUBRIC_TOTAL}, the average of the student’s and your score (page {D.IX("rubric")}).</li></ul>'
             f'<div class="box" style="margin-top:6pt"><span class="k">In one sentence</span><p style="margin:0;font-size:12pt">Students learn that '
             f'a house track is planned: a tempo that sets the length of a step, a kick on every beat, a bass that makes room for it, and sections that build to a drop.</p></div>'
             f'<p class="small" style="margin-top:6pt">Logic Pro is a product of Apple Inc. This resource is not affiliated with Apple.</p>'
             f'</div></div>')
    return D.page("How to use this resource", "START HERE", "Teacher", inner, n, key="howto")


def overview_page(n, wm=False):
    inner = (f'<div class="cols"><div>'
             f'<div class="box inv" style="margin-bottom:6pt"><span class="k">The project in one line</span><p style="margin:0;font-size:12pt">'
             f'<b>{TITLE}</b> · Four on the floor, sidechain and a 64-bar arrangement · Logic Pro<br>One traditional winter song, rebuilt as a house track at 128 BPM.</p></div>'
             f'{D.H2("What students make")}'
             f'<p style="font-size:12.2pt;line-height:1.48">A 64-bar house remix of one traditional winter song, built in Logic Pro. A 4-bar pattern puts a kick on every beat, an open hat and a bass on the off-beats and a clap on beats 2 and 4. '
             f'A four-chord loop and the tune sit in one key. A compressor with a side chain turns the bass, pad and tune down each time the kick hits, and the layers become an arrangement with an intro, a build, a drop, a break, a second drop and an outro. '
             f'Students hand in a bounced file and the zipped .logicx project, plus their plans and a reflection, then play the remix and take questions.</p>'
             f'{D.H2("What this project reinforces")}<p style="font-size:12pt;line-height:1.5">{TN_REINFORCES}</p>'
             f'{D.H2("Standards")}<p style="font-size:11.4pt">Supports the National Core Arts Standards for Music (Music Technology, high school): generating '
             f'and developing ideas (MU:Cr1.1, MU:Cr2.1), presenting work (MU:Pr6.1) and responding to it (MU:Re7.2).</p>'
             f'</div><div>'
             f'{D.H2("Goals", True)}<ul>' + "".join(f"<li style='font-size:12pt;line-height:1.45'>{g}</li>" for g in GOALS) + '</ul>'
             f'{D.H2("About the song and the theme")}<div class="box acc-b" style="padding:5pt 9pt"><p style="margin:0 0 3pt;font-size:10.2pt;line-height:1.36">{SONG_FACTS}</p>'
             f'<p style="margin:0;font-size:10.2pt;line-height:1.36">{THEME}</p></div>'
             f'<div class="box" style="margin-top:6pt;padding:5pt 9pt"><span class="k">At a glance</span><p style="margin:0;font-size:10.2pt;line-height:1.38"><b>Grades</b> {GRADES_TEXT}, music technology or music production · '
             f'<b>Length</b> {CLASSES} class periods (two and four also shown) · <b>Software</b> Logic Pro · <b>You supply</b> Macs with Logic Pro, headphones and a place to hand in files · '
             f'<b>Assessment</b> rubric, 5 categories scored 1–5, /{RUBRIC_TOTAL} (page {D.IX("rubric")})</p></div>'
             f'</div></div>')
    return D.page("Project overview", "OVERVIEW", "House remix project", inner, n, key="overview")


def setup_page(n, wm=False):
    inner = (f'<style>.sb p, .sb li {{ font-size: 11.6pt; line-height: 1.44; margin-bottom: 5pt; }}</style><div class="cols"><div class="big sb">'
             f'{D.H2("You need", True)}<ul>'
             f'<li><b>A Mac with Logic Pro</b> for each student, and <b>headphones</b>. Speakers help for the listening day, because the kick and the bass are low sounds.</li>'
             f'<li><b>Drum and synth sounds</b>: the ones that come with Logic Pro are enough (a kick, a clap, hats, a bass and a pad or lead sound). A keyboard or pad controller helps but is not required.</li>'
             f'<li><b>A score of the tune</b> in the public domain, from the school or town library or a free score site, if students prefer not to play it by ear. This kit prints no notes.</li>'
             f'<li><b>A place to hand in</b> the .mp3 or .wav files, the zipped .logicx and the reflection.</li>'
             f'<li><b>Printed student pages</b>, one set each (pages {D.IX("timing")}–{D.IX("reflect")}).</li></ul>'
             f'{D.H2("Before Class 1")}'
             + "".join(D.chk(c, 13, "font-size:11.6pt;margin-bottom:7pt") for c in [
                 f"Read the timing page (page {D.IX('timing')}) so you can answer ‘how long is one beat at 128 BPM?’ and ‘how long are 64 bars?’",
                 f"Open Logic Pro on a student computer, set the tempo to 128 BPM and the time signature to 4/4, and play a kick on every beat (page {D.IX('pattern')}).",
                 f"Check which tools your version has: Drum Machine Designer, the Step Sequencer, the Compressor’s Side Chain menu, Retro Synth or Alchemy (see page {D.IX('logicref')}).",
                 f"Read the worked example (pages {D.IX('example')}–{D.IX('example2')})."]) +
             f'</div><div class="big sb">'
             f'{D.H2("What to watch", True)}'
             f'<p style="font-size:11.4pt">Watch for a kick that is not on every beat, a bass that plays on the same step as the kick, a sidechain whose source is not set to the kick track, a release so long that the bass never comes back, and a mix so loud that it clips. {TN_NOTE}</p>'
             f'<div class="box acc-b" style="margin-top:2pt"><span class="k">Key and meter</span><p style="margin:0;font-size:10.6pt;line-height:1.4">{KEY_NOTE}</p></div>'
             f'{D.H2("Their own work only")}'
             f'<div class="box"><p style="margin:0;font-size:10.6pt;line-height:1.4">{VOICE_NOTE}</p></div>'
             f'<div class="box" style="margin-top:6pt"><span class="k">Listening</span><p style="margin:0;font-size:10.6pt;line-height:1.4">House music is built on low sounds played loudly. Keep headphone volume at a comfortable level, and take a break from loud kicks and bass.</p></div>'
             f'</div></div>')
    return D.page("Setup and what to watch", "SETUP", "Teacher", inner, n, key="setup")


# ================================================================ the student pages
def tempo_rows():
    rows = []
    for bpm in TEMPOS:
        hi = ' class="hi"' if bpm == EX_BPM else ''
        b, e = ("<b>", "</b>") if bpm == EX_BPM else ("", "")
        rows.append(f"<tr{hi}><td>{b}{bpm}{e}</td><td>{dec(ms(spb(bpm)), 2)}</td><td>{b}{dec(ms(step_len(bpm)), 2)}{e}</td><td>{dec(bar_len(bpm), 3)}</td>"
                    f"<td>{dec(16 * bar_len(bpm), 3)}</td><td>{dec(ARR_BARS * bar_len(bpm), 3)}</td></tr>")
    return "".join(rows)


def len_rows():
    return "".join(f"<tr><td><b>{t}</b></td>" + "".join(f"<td>{dec(nb * bar_len(t), 3)}</td>" for nb in LEN_BARS) + "</tr>" for t in LEN_TEMPOS)


def timing_page(n, wm=False):
    inner = (CSS_CC +
             f'<p style="margin:0 0 4pt;font-size:10.2pt;line-height:1.36">Step 1: plan the tempo. In 4/4 there are 4 beats in a bar, and each beat holds four 16th-note steps, so a bar has 16 steps. '
             f'House music is typically {HOUSE_TYPICAL[0]} to {HOUSE_TYPICAL[1]} BPM, and {HOUSE_CHARACTERISTIC[0]} to {HOUSE_CHARACTERISTIC[1]} BPM in its most typical form, so 128 BPM fits. Every number below is computed, so you can check your own arithmetic against it.</p>'
             f'<div class="cols" style="gap:10pt;align-items:flex-start"><div class="box acc-b" style="padding:5pt 9pt;flex:1.15"><span class="k">The formulas (4/4)</span>'
             f'<p style="margin:0 0 2pt;font-size:9.8pt"><b>Seconds per beat</b> = 60 ÷ BPM (× 1000 for milliseconds)</p><p style="margin:0 0 2pt;font-size:9.8pt"><b>Seconds per 16th-note step</b> = 15 ÷ BPM</p>'
             f'<p style="margin:0 0 2pt;font-size:9.8pt"><b>Seconds per bar</b> = 240 ÷ BPM (16 steps, 4 beats)</p>'
             f'<p style="margin:0 0 2pt;font-size:9.8pt"><b>A hit on grid step s of bar b</b> is at ((b − 1) × 16 + (s − 1)) × 15 ÷ BPM seconds</p>'
             f'<p style="margin:0 0 2pt;font-size:9.8pt"><b>A piece of b bars</b> lasts b × 240 ÷ BPM seconds</p>'
             f'<p style="margin:0;font-size:9.8pt"><b>At 128 BPM:</b> 60 ÷ 128 = 0.46875 s = 468.75 ms per beat; 15 ÷ 128 = 0.1171875 s per step; 240 ÷ 128 = 1.875 s per bar.</p></div>'
             f'<div class="box" style="padding:5pt 9pt;flex:1"><span class="k">Rounding rules</span><p style="margin:0;font-size:9.2pt;line-height:1.32">Milliseconds per beat and per step to 2 decimals and seconds to 3; '
             f'a 5 rounds up. So 15 ÷ 128 = 0.1171875 s = 117.1875 ms prints as 117.19 ms. The 128 BPM beat (468.75 ms) and bar (1.875 s) are exact.</p></div></div>'
             f'<span class="k" style="margin-top:5pt">How long is a beat, a step, a bar and a section?</span>'
             f'<table class="t cc" style="margin-top:1pt"><tr><th>BPM</th><th>Milliseconds per beat</th><th>Milliseconds per step</th><th>Seconds per bar</th><th>16 bars (s)</th><th>64 bars (s)</th></tr>{tempo_rows()}</table>'
             f'<p class="small" style="margin:0 0 2pt;font-size:8.6pt">The shaded row is this project. The 64-bar arrangement lasts 64 × 240 ÷ BPM = 15360 ÷ BPM seconds, which is 120 seconds at 128 BPM; a 16-bar section lasts 30 seconds.</p>'
             f'<span class="k" style="margin-top:3pt">How long is my piece? (lengths in seconds at three tempos)</span>'
             f'<table class="t cc" style="margin-top:1pt"><tr><th>BPM</th>' + "".join(f"<th>{nb} bars</th>" for nb in LEN_BARS) + f'</tr>{len_rows()}</table>'
             f'<p class="small" style="margin:0 0 3pt;font-size:8.6pt">At 120 BPM a bar is 2 s, at 124 BPM it is 1.935 s and at 128 BPM it is 1.875 s. A faster tempo makes the same 64 bars shorter.</p>'
             f'<div class="box" style="padding:5pt 9pt"><span class="k">Going the other way: how many bars fit in a time?</span>'
             f'<p style="margin:0 0 2pt;font-size:9.8pt;line-height:1.32">Bars = seconds × BPM ÷ 240. Check: 120 seconds at 128 BPM is 120 × 128 ÷ 240 = 64 bars. '
             f'Try it: 60 seconds at 128 BPM = 60 × 128 ÷ 240 = 32 bars, and 30 seconds at 128 BPM = 30 × 128 ÷ 240 = 16 bars.</p>'
             f'<div class="fl" style="margin:3pt 0 0;font-size:10pt"><b>My time:</b><span style="flex:0 0 0.8in"></span><b>s at</b><span style="flex:0 0 0.8in"></span><b>BPM = time × BPM ÷ 240 =</b><span></span><b>bars</b></div></div>'
             f'<div class="box acc-b" style="margin-top:5pt;padding:5pt 9pt"><span class="k">My plan</span>'
             f'<div class="fl" style="margin:3pt 0 3pt;font-size:10pt"><b>Tempo:</b><span></span><b>BPM</b><b style="margin-left:8pt">One beat = 60 ÷ BPM =</b><span></span><b>s</b></div>'
             f'<div class="fl" style="margin:0 0 3pt;font-size:10pt"><b>One step = 15 ÷ BPM =</b><span></span><b>s</b><b style="margin-left:8pt">One bar = 240 ÷ BPM =</b><span></span><b>s</b></div>'
             f'<div class="fl" style="margin:0;font-size:10pt"><b>My 16 bars last</b><span style="flex:0 0 0.8in"></span><b>s</b><b style="margin-left:8pt">My 64 bars last</b><span style="flex:0 0 0.8in"></span><b>s</b></div></div>')
    return D.page("Timing page", "STUDENT", "Class 1", inner, n, wm, name=True, key="timing")


def tune_rows():
    rows = []
    for t in CAROL_TEMPOS:
        ratio = Fraction(EX_BPM, t)
        pct = (Fraction(EX_BPM, t) - 1) * 100
        rows.append(f"<tr><td><b>{t}</b></td><td>{dec(ratio, 4)}</td><td>{dec(pct, 2)}%</td><td>{dec(16 * bar_len(t), 3)}</td><td>{dec(16 * bar_len(EX_BPM), 3)}</td></tr>")
    return "".join(rows)


def tune_page(n, wm=False):
    blank = "".join("<tr><td style='height:17pt'></td><td></td><td></td><td></td></tr>" for _ in range(3))
    inner = (CSS_CC +
             f'<p style="margin:0 0 4pt;font-size:10.2pt;line-height:1.36">Step 2: prepare the song. A remix keeps the tune and changes the rest. Before you build anything, find out what you are keeping and how far you are moving it.</p>'
             f'<div class="box acc-b" style="padding:5pt 9pt"><span class="k">The song</span><p style="margin:0;font-size:10.2pt;line-height:1.36">{SONG_FACTS}</p></div>'
             f'<span class="k" style="margin-top:5pt">How much faster is 128 BPM? (four example tempos for a plain version)</span>'
             f'<table class="t cc" style="margin-top:1pt"><tr><th>Plain tempo (BPM)</th><th>Ratio 128 ÷ tempo</th><th>Faster by</th><th>16 bars at the plain tempo (s)</th><th>16 bars at 128 BPM (s)</th></tr>{tune_rows()}</table>'
             f'<p class="small" style="margin:1pt 0 3pt;font-size:8.6pt">Ratio = 128 ÷ plain tempo. Percent faster = (128 − plain tempo) ÷ plain tempo × 100. The four plain tempos are examples, not facts about the song: use the tempo of your own version. '
             f'At 100 BPM, 128 ÷ 100 = 1.28, so the remix is 28% faster, and 16 bars shrink from 38.4 s to 30 s.</p>'
             f'<div class="cols" style="gap:10pt;align-items:flex-start"><div class="box" style="padding:5pt 9pt;flex:1"><span class="k">Key and meter</span>'
             f'<p style="margin:0;font-size:9.8pt;line-height:1.34">{KEY_NOTE}</p></div>'
             f'<div class="box acc-b" style="padding:5pt 9pt;flex:1"><span class="k">Get the tune into Logic Pro</span>'
             + "".join(D.chk(c, 11, "font-size:9.4pt;line-height:1.26;margin-bottom:2pt") for c in [
                 "I have a public-domain score of the tune, or I will play it by ear.",
                 "I played the tune once at a slow tempo to learn it.",
                 "I entered it on a Software Instrument track in my key.",
                 "I checked the octave: Logic’s middle C is C3 by default."]) + '</div></div>'
             f'<span class="k" style="margin-top:5pt">The plan for my version</span>'
             f'<table class="t cc" style="margin-top:1pt"><tr><th>Plain tempo of my version (BPM)</th><th>128 ÷ tempo</th><th>Percent faster</th><th>My key</th></tr>{blank}</table>'
             f'<div class="box" style="margin-top:6pt;padding:5pt 9pt"><span class="k">Why not copy a recording?</span><p style="margin:0;font-size:9.8pt;line-height:1.34">A recording of a song has its own copyright, even when the song itself is old. '
             f'That is why this project asks you to enter the tune yourself and make every other sound from scratch.</p></div>'
             f'<div class="fl" style="margin:5pt 0 0;font-size:10pt"><b>Bars in one pass of my tune:</b><span style="flex:0 0 0.8in"></span><b>My sections, in bars:</b><span></span></div>')
    return D.page("The song and the tune", "STUDENT", "Class 1", inner, n, wm, name=True, key="tune")


def pat_rows():
    rows = []
    for nm in LANES:
        rows.append(f"<tr><td class='l'><b>{nm.title()}</b></td>" + "".join(f"<td>{len(PATTERN[nm][b])}</td>" for b in range(PAT_BARS)) + f"<td><b>{LANE_HITS[nm]}</b></td></tr>")
    rows.append("<tr class='hi'><td class='l'><b>All lanes</b></td>" + "".join(f"<td><b>{h}</b></td>" for h in PAT_HITS) + f"<td><b>{PAT_TOTAL}</b></td></tr>")
    return "".join(rows)


def pattern_page(n, wm=False):
    inner = (CSS_CC +
             f'<p style="margin:0 0 3pt;font-size:10.2pt;line-height:1.36">Step 3: build the house beat. Four on the floor puts the kick on every beat. Each lane is one sound and each column is one 16th-note step, so a bar has 16 steps '
             f'and the 4-bar pattern has {PAT_BARS * STEPS_BAR}. Lanes can share a step, so they play together. Play your own pattern, then draw it on the blank grid.</p>'
             f'<div style="margin:0 0 2pt">{D.body_svg(grid_body(1600, "grid page"))}</div>'
             f'<div class="cols" style="gap:10pt;align-items:flex-start"><div style="flex:1.2"><span class="k" style="margin-top:2pt">Hits in the model pattern</span>'
             f'<table class="t cc" style="margin-top:1pt"><tr><th>Lane</th><th>Bar 1</th><th>Bar 2</th><th>Bar 3</th><th>Bar 4</th><th>All bars</th></tr>{pat_rows()}</table>'
             f'<p class="small" style="margin:1pt 0 0;font-size:8.6pt">Hits per bar: {PAT_HITS[0]}, {PAT_HITS[1]}, {PAT_HITS[2]} and {PAT_HITS[3]}, {PAT_TOTAL} in all. The lanes add up to the same {sum(LANE_HITS.values())}. Bar 4 adds a clap fill on grid steps 15 and 16.</p></div>'
             f'<div class="box acc-b" style="padding:4pt 9pt;flex:1"><span class="k">Reading the grid</span>'
             f'<p style="margin:0 0 2pt;font-size:9.4pt;line-height:1.32">The kick plays on grid steps 1, 5, 9 and 13: one on each beat. The open hat and the bass play on the off-beats, grid steps 3, 7, 11 and 15, halfway between kicks. The clap plays on 5 and 13, which are beats 2 and 4.</p>'
             f'<p style="margin:0;font-size:9.4pt;line-height:1.32">A hit on grid step s of bar b starts at ((b − 1) × 16 + (s − 1)) × 15 ÷ BPM seconds. At 128 BPM, bar 2, grid step 5 (a kick on beat 2) is at (16 + 4) × 0.1171875 = 2.34375 s.</p></div></div>'
             f'<span class="k" style="margin-top:4pt">My pattern: draw a hit in the lane of each sound you play</span>'
             f'<div style="margin:1pt 0 2pt">{D.body_svg(grid_body(1600, "grid blank page", blank=True))}</div>'
             f'<div class="fl" style="margin:2pt 0 0;font-size:10pt"><b>My hits per bar:</b><span></span><b>Total:</b><span style="flex:0 0 0.8in"></span><b>Bar 2 starts at (s):</b><span style="flex:0 0 0.8in"></span></div>')
    return D.page("The 4-bar step grid", "STUDENT", "Class 1", inner, n, wm, name=True, key="pattern")


def chord_rows():
    rows = []
    for key in SCALES:
        ch = loop_chords(key)
        hi = ' class="hi"' if key == WORK_KEY else ''
        rows.append(f"<tr{hi}><td><b>{key} major</b></td><td class='l'>{' '.join(SCALES[key])}</td>"
                    + "".join(f"<td><b>{nm}</b><br>{' '.join(t)}</td>" for _, nm, t in ch) + "</tr>")
    return "".join(rows)


def chords_page(n, wm=False):
    fk = loop_chords(WORK_KEY)
    blank = "".join("<tr><td style='height:17pt'></td><td></td><td></td><td></td></tr>" for _ in range(8))
    inner = (CSS_CC +
             f'<p style="margin:0 0 3pt;font-size:10.2pt;line-height:1.36">Step 4: add bass and chords. A chord loop repeats a few chords under the tune. This one has one chord in each bar: the I, IV, V and vi chords of a major key. '
             f'Each chord is built by stacking thirds in the scale: a scale note, the note two steps up and the note two steps above that. The pad plays the chord and the bass plays its root.</p>'
             f'<span class="k" style="margin-top:2pt">The I, IV, V and vi chords in three keys (the shaded row is the key of the examples)</span>'
             f'<table class="t cc" style="margin-top:1pt"><tr><th>Key</th><th>Scale</th><th style="text-transform:none">I</th><th style="text-transform:none">IV</th><th style="text-transform:none">V</th><th style="text-transform:none">vi</th></tr>{chord_rows()}</table>'
             f'<div class="cols" style="gap:10pt;align-items:flex-start;margin-top:5pt"><div style="flex:1.1"><span class="k" style="margin-top:2pt">The loop in {WORK_KEY} major: one chord a bar</span>'
             f'<table class="t cc" style="margin-top:1pt"><tr><th>Bar</th><th>Chord</th><th>Chord tones</th><th>Bass plays</th></tr>'
             + "".join(f"<tr><td><b>{i + 1}</b></td><td>{nm}</td><td>{' '.join(t)}</td><td>{t[0]} on grid steps 3, 7, 11, 15</td></tr>" for i, (_, nm, t) in enumerate(fk)) +
             f'</table><p class="small" style="margin:1pt 0 0;font-size:8.6pt">The loop is {LOOP_BARS} bars long and lasts {LOOP_BARS} × 1.875 = {fmt(LOOP_BARS * EX_BAR_S)} s at 128 BPM, so 16 bars hold {16 // LOOP_BARS} loops. '
             f'To change key, use another row of the table: the pattern of chords stays the same.</p></div>'
             f'<div class="box acc-b" style="padding:4pt 9pt;flex:1"><span class="k">Bass between the kicks</span>'
             f'<p style="margin:0 0 2pt;font-size:9.4pt;line-height:1.32">The kick is on grid steps 1, 5, 9 and 13. The bass plays the root of the bar’s chord on the off-beats, grid steps 3, 7, 11 and 15, so it never lands on a kick. '
             f'That leaves each kick a clear moment, and the sidechain makes more room for it (page {D.IX("sidechain")}).</p>'
             f'<p style="margin:0;font-size:9.4pt;line-height:1.32">Draw the notes in the Piano Roll with the grid set to 16th notes, or play them in. A chord tone is one of the chord’s three notes.</p></div></div>'
             f'<span class="k" style="margin-top:5pt">Check the tune against the chords: first tune note of each bar</span>'
             f'<table class="t cc" style="margin-top:1pt"><tr><th>Bar</th><th>First tune note</th><th>Chord of the bar</th><th>Is it a chord tone? (yes or no)</th></tr>{blank}</table>'
             f'<p class="small" style="margin:1pt 0 0;font-size:8.6pt">If the answer is no, try another chord from the table for that bar, or move the chord to the bar before or after. Your ear decides: the loop is a starting point, not a rule.</p>')
    return D.page("Chords, bass and the tune", "STUDENT", "Class 2", inner, n, wm, name=True, key="chords")


def gr_rows():
    return "".join(f"<tr><td><b>{str(L).replace('-', '−')}</b></td><td>{str(L - THRESH_DB).replace('-', '−') if L > THRESH_DB else '0'}</td><td><b>{exact(gain_reduction(L))}</b></td></tr>" for L in KICK_LEVELS)


def rel_rows():
    rows = []
    for k in (1, 2, 3, 4):
        t = ms(k * step_len(EX_BPM))
        nm = {1: "1 step (a 16th)", 2: "half a beat (2 steps)", 3: "three-quarters of a beat (3 steps)", 4: "1 beat (4 steps)"}[k]
        rows.append(f"<tr><td><b>{nm}</b></td><td>{k}/16 bar</td><td>{exact(t)}</td></tr>")
    return "".join(rows)


def sidechain_page(n, wm=False):
    inner = (CSS_CC +
             f'<p style="margin:0 0 3pt;font-size:10.2pt;line-height:1.36">Step 5: set up the sidechain. A compressor with a side chain input controls the gain of one signal from the level of another. '
             f'In dance music it is often used on basslines, controlled by the kick drum, so the two do not conflict and the bass pulses with the beat. The kick plays; the bass, pad and tune are turned down for a moment each time it hits.</p>'
             f'<div class="cols" style="gap:10pt;align-items:flex-start"><div style="flex:1.7">{D.body_svg(curve_body(1500, "curve page"))}</div>'
             f'<div style="flex:1"><span class="k" style="margin-top:2pt">Gain reduction (example settings)</span>'
             f'<table class="t cc" style="margin-top:1pt"><tr><th>Kick level (dB)</th><th>dB over threshold</th><th>Gain reduction (dB)</th></tr>{gr_rows()}</table>'
             f'<p class="small" style="margin:1pt 0 0;font-size:8.6pt">Gain reduction = (level − threshold) × (1 − 1 ÷ ratio) = (level + 20) × 3/4. With a ratio of 4:1, 4 dB over the threshold is turned down by 3 dB. '
             f'These are the kit’s example settings, not Logic’s defaults.</p></div></div>'
             f'<span class="k" style="margin-top:4pt">The duck in time (one bar at 128 BPM)</span>'
             f'<div style="margin:1pt 0 2pt">{D.body_svg(duck_body(1500, "duck page"))}</div>'
             f'<div class="cols" style="gap:10pt;align-items:flex-start"><div style="flex:1"><span class="k" style="margin-top:2pt">Release times at 128 BPM</span>'
             f'<table class="t cc" style="margin-top:1pt"><tr><th>Release</th><th>Part of a bar</th><th>Milliseconds</th></tr>{rel_rows()}</table></div>'
             f'<div class="box acc-b" style="padding:4pt 9pt;flex:1.2"><span class="k">Starting points to set by ear</span>'
             f'<p style="margin:0 0 2pt;font-size:9.2pt;line-height:1.3"><b>Attack:</b> as fast as the control allows, so the bass is down by the time the kick sounds. <b>Release:</b> start near one beat, 468.75 ms, so the level is back as the next kick hits; shorten it if the bass sounds too quiet. '
             f'<b>Ratio and threshold:</b> start at 4:1 and lower the threshold until the meter dips on each kick and returns to zero between them.</p>'
             f'<p style="margin:0;font-size:9.2pt;line-height:1.3">There is no industry standard for what attack and release numbers mean, so the same number can sound different in two compressors. Listen, then decide.</p></div></div>')
    return D.page("Sidechain: the duck", "STUDENT", "Class 2", inner, n, wm, name=True, key="sidechain")


def source_rows():
    return "".join(f"<tr><td><b>{nm}</b></td><td class='l'>{use}</td><td class='l'>{how}</td></tr>" for nm, _, _, _, _, _, use, how in SOUNDS)


def roles_page(n, wm=False):
    def box(title, items, acc=False):
        return (f'<div class="box{" acc-b" if acc else ""}" style="padding:4pt 9pt"><span class="k">{title}</span>'
                + "".join(D.chk(c, 11, "font-size:9.6pt;line-height:1.26;margin-bottom:2pt") for c in items) + '</div>')
    inner = (CSS_CC +
             f'<p style="margin:0 0 3pt;font-size:10.2pt;line-height:1.36">Step 5: set up the sidechain, continued. Every layer has a job. The kick is the trigger; the bass, the pad and the tune are ducked, and the clap and the hats are left alone. '
             f'The chain below shows the path of the signal.</p>'
             f'<div style="margin:0 auto 2pt;width:84%">{D.body_svg(chain_body(1620, "chain page"))}</div>'
             f'<div style="margin:0 0 3pt">{D.body_svg(roles_body(1600, "roles page"))}</div>'
             f'<span class="k" style="margin-top:3pt">What each layer uses and plays</span>'
             f'<table class="t cc" style="margin-top:1pt;font-size:8.8pt"><tr><th>Layer</th><th>What to use</th><th>What it plays</th></tr>{source_rows()}</table>'
             f'<div class="cols" style="gap:9pt;align-items:flex-start;margin-top:4pt"><div>' +
             box("Check the sidechain", ["A Compressor is on the bass, the pad and the tune.", "Its side chain source is the kick track.",
                                         "I solo the kick and the bass and hear the bass dip on every kick.", "The meter returns to zero before the next kick."], True) +
             '</div><div>'
             f'<span class="k">My sidechain settings</span>'
             f'<table class="t cc" style="margin-top:1pt"><tr><th>Setting</th><th>My value</th><th>Why</th></tr>'
             + "".join(f"<tr><td style='height:19pt'><b>{v}</b></td><td></td><td></td></tr>" for v in ("Ratio", "Threshold", "Attack", "Release (ms)")) + '</table></div></div>')
    return D.page("Layer table and the signal chain", "STUDENT", "Class 2", inner, n, wm, name=True, key="roles")


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
             f'<p style="margin:0 0 3pt;font-size:10.2pt;line-height:1.36">Step 6: arrange and mix. An arrangement puts your layers into sections. This one is {ARR_BARS} bars with {len(ARR_SECTIONS)} sections: an intro, a build, the drop, a break, a second drop and an outro. '
             f'A build raises the tension, the drop is where the full beat and bass arrive, and the break strips back so the second drop feels bigger. This model has {len(ARR_ROWS)} layers.</p>'
             f'<div style="margin:0 0 3pt">{D.body_svg(arr_body(1600, "arrange page"))}</div>'
             f'<div class="cols" style="gap:10pt;align-items:flex-start"><div style="flex:1.6"><span class="k" style="margin-top:2pt">The sections at {EX_BPM} BPM</span>'
             f'<table class="t cc" style="margin-top:1pt"><tr><th>Section</th><th>Bars</th><th>Starts (s)</th><th>Ends (s)</th><th>Layers that play</th></tr>{sec_rows()}</table></div>'
             f'<div style="flex:1"><span class="k" style="margin-top:2pt">Layer-bars in the model</span>'
             f'<table class="t cc" style="margin-top:1pt"><tr><th>Layer</th><th>Bars</th></tr>'
             + "".join(f"<tr><td class='l'>{r.title()}</td><td>{len(bars_of(r))}</td></tr>" for r in ARR_LAYERS) + '</table></div></div>'
             f'<p class="small" style="margin:1pt 0 2pt;font-size:8.6pt">The layers play {sum(len(bars_of(r)) for r in ARR_LAYERS)} bars in all: {" + ".join(str(len(bars_of(r))) for r in ARR_LAYERS)}. The number row on the map adds to the same {sum(len(layers_in_bar(b)) for b in range(1, ARR_BARS + 1))}. '
             f'Length = bars × 240 ÷ BPM: at {EX_BPM} BPM, {ARR_BARS} bars × 1.875 s = {fmt(ARR_BARS * EX_BAR_S)} s.</p>'
             f'<span class="k" style="margin-top:3pt">My arrangement (my tempo: ________ BPM)</span>'
             f'<table class="t cc" style="margin-top:1pt"><tr><th>Section</th><th>Bars</th><th>Starts at (s)</th><th>Layers that play</th></tr>{mine}</table>'
             f'<div class="box acc-b" style="margin-top:4pt;padding:4pt 9pt"><span class="k">Check my arrangement</span>'
             + "".join(D.chk(c, 11, "font-size:9.8pt;line-height:1.28;margin-bottom:2pt") for c in [
                 "My sections add up to 64 bars, and every section starts on a bar I can name in seconds.",
                 "The drop has more layers than the build, and the break has fewer than the drop.",
                 "The kick is steady in the drops, and the number of layers in each bar matches my map."]) + '</div>')
    return D.page("Arrangement map", "STUDENT", "Class 3", inner, n, wm, name=True, key="arrange")


def mix_page(n, wm=False):
    def box(title, items, acc=False):
        return (f'<div class="box{" acc-b" if acc else ""}" style="padding:5pt 9pt"><span class="k">{title}</span>'
                + "".join(D.chk(c, 11, "font-size:10pt;line-height:1.3;margin-bottom:3pt") for c in items) + '</div>')
    inner = (f'<p style="margin:0 0 5pt;font-size:10.2pt;line-height:1.36">Step 6: arrange and mix, continued. A mix makes every layer clear. Work through the boxes with headphones at a low volume, '
             f'then check each one off. Make small moves and listen after each one.</p>'
             f'<div class="cols" style="gap:10pt;align-items:flex-start"><div>'
             + box("Kick and bass first", ["I set the kick and the bass levels before anything else.", "The bass ducks on every kick (sidechain) and comes back before the next one.",
                                          "I can hear the kick clearly under the bass in the drop."], True)
             + '<div style="height:6pt"></div>'
             + box("Levels", ["I can hear every layer, and I make a loud layer quieter before I make a quiet layer louder.",
                              "The master meter stays below 0 dBFS with plenty of room to spare.",
                              "I listened at a normal volume, not only loud."])
             + '</div><div>'
             + box("Sections", ["I can find every layer on my arrangement map by listening.", "The intro, build, drop, break, drop and outro are the lengths on my map.",
                                "The drops are the fullest parts, and the break strips back."], True)
             + '<div style="height:6pt"></div>'
             + box("Feel", ["The release sounds musical, not pumping too much or too little.", "No layer clicks or starts late.",
                            "When I mute the sidechain, I can tell the difference."])
             + '</div></div>'
             f'<div class="box" style="margin-top:6pt;padding:5pt 9pt"><span class="k">The listening test</span><p style="margin:0 0 3pt;font-size:10pt;line-height:1.36">Play the whole remix with your eyes closed and '
             f'rate each part from 1 (weak) to 5 (very strong). Can you hear the kick on every beat? Does the build land? Does the drop hit? Write what you hear:</p>'
             f'<div class="fl" style="margin:2pt 0;font-size:10pt"><b>Kick and bass:</b><span></span><b>Build:</b><span></span><b>Drop:</b><span></span></div></div>'
             f'<div class="box acc-b" style="margin-top:6pt;padding:5pt 9pt"><span class="k">Bounce</span>'
             + "".join(D.chk(c, 11, "font-size:10pt;margin-bottom:3pt") for c in [
                 "The bounce starts at bar 1 and ends at the planned length (64 bars; check the seconds for my tempo on page " + str(pg("timing")) + ").",
                 "MP3 or WAV bounced, and the .logicx project zipped.", f"Both files named {FILE_NAME}."]) + '</div>'
             f'<span class="k" style="margin-top:6pt">What I changed after the listening test</span>' + D.lines(7, 24))
    return D.page("Mix checklist", "STUDENT", "Class 3", inner, n, wm, name=True, key="mix")


# ================================================================ worked example (2 pages)
def ex_snd_rows():
    return "".join(f"<tr><td><b>{nm.title()}</b></td><td>{role.title()}</td><td>{PITCH_W[p].lower()}</td><td>{LEN_W[ln].lower()}</td><td>{sc.title()}</td><td>{len(bars_of(nm))}</td></tr>"
                   for nm, _, role, p, ln, sc, _, _ in SOUNDS)


def ex_bar_rows():
    return "".join(f"<tr><td><b>{b + 1}</b></td><td>{PAT_HITS[b]}</td><td>{exact(hit_time(EX_BPM, b + 1, 1))}</td><td>{exact(hit_time(EX_BPM, b + 2, 1))}</td></tr>" for b in range(PAT_BARS))


def ex_layer_rows():
    return "".join(f"<tr><td><b>{nm.title()}</b></td><td>{spans_text(spans)}</td><td>{len(bars_of(nm))}</td></tr>" for nm, spans in ARR_ROWS)


def ex_len_rows():
    return "".join(f"<tr><td><b>{t}</b></td><td>{dec(bar_len(t), 3)}</td><td>{dec(PAT_BARS * bar_len(t), 3)}</td><td>{dec(ARR_BARS * bar_len(t), 3)}</td></tr>" for t in LEN_TEMPOS)


def example_page(n, wm=False):
    inner = (f'<style>table.ec td {{ text-align: center; }}</style>'
             f'<p style="margin:0 0 4pt;font-size:10pt">An <b>invented plan on paper</b>: a house remix at {EX_BPM} BPM built from {NSND} layers. No audio is included. '
             f'Student projects will differ. Page 1 of 2: the plan, the layers and the pattern.</p>'
             f'<div class="cols" style="gap:10pt;align-items:flex-start"><div class="box"><span class="k">1 · A weak plan</span><p style="margin:0;font-size:10.2pt">{EX_WEAK}</p>'
             f'<p style="margin:3pt 0 0;font-size:9.2pt">It names no tempo, no key, no pattern, no sidechain and no sections.</p></div>'
             f'<div class="box acc-b"><span class="k">2 · A clear plan</span><p style="margin:0;font-size:8.2pt;line-height:1.26">{EX_STRONG}</p></div></div>'
             f'{D.H2("3 · The layers and their jobs")}'
             f'<table class="t ec" style="font-size:8.8pt;line-height:1.14"><tr><th>Layer</th><th>Role</th><th>Pitch</th><th>Length</th><th>Side chain</th><th>Bars it plays</th></tr>{ex_snd_rows()}</table>'
             f'<p style="margin:2pt 0 0;font-size:8.8pt;line-height:1.3">The {NSND} layers play {sum(len(bars_of(l)) for l in LAYERS)} bars in all ({" + ".join(str(len(bars_of(l))) for l in LAYERS)}). The kick triggers the duck and {len(DUCKED)} of them are ducked. '
             f'The words in the table are listening descriptions, not measurements.</p>'
             f'{D.H2("4 · The 4-bar step grid at 128 BPM")}'
             f'<div class="cols" style="gap:10pt;align-items:flex-start"><div style="flex:0 0 3.4in"><table class="t ec" style="font-size:8.8pt;line-height:1.14"><tr><th>Bar</th><th>Hits</th><th>Starts (s)</th><th>Ends (s)</th></tr>{ex_bar_rows()}</table></div>'
             f'<p style="margin:0;font-size:8.8pt;line-height:1.3">The pattern has {PAT_HITS[0]}, {PAT_HITS[1]}, {PAT_HITS[2]} and {PAT_HITS[3]} hits, {PAT_TOTAL} in all, on a grid of {PAT_BARS} bars of {STEPS_BAR} steps = {PAT_BARS * STEPS_BAR} steps. '
             f'It lasts {PAT_BARS} × {fmt(EX_BAR_S)} = {fmt(PAT_BARS * EX_BAR_S)} seconds. The kick on bar 2, grid step 5 starts at (16 + 4) × {exact(EX_STEP_S)} = {exact(hit_time(EX_BPM, 2, 5))} s. '
             f'The kick plays on grid steps 1, 5, 9 and 13, and the bass and the open hat on 3, 7, 11 and 15: the kick and the bass never share a step.</p></div>'
             f'<div style="margin:3pt auto 3pt;width:80%">{D.body_svg(grid_body(1600, "grid page"))}</div>'
             f'<p style="margin:3pt 0 0;font-size:8.8pt;line-height:1.3"><b>Kick and bass:</b> the kick never stops in the drops, and the bass never lands on a kick.</p>')
    return D.page("Worked example · the plan, the layers and the pattern", "EXAMPLE", "Teacher", inner, n, wm, ak=True, key="example")


def example2_page(n, wm=False):
    qs = " ".join(f"{i + 1}. {q}" for i, q in enumerate(EX_QUESTIONS))
    fk = loop_chords(WORK_KEY)
    inner = (f'{D.H2("5 · The chords and the bass", True)}'
             f'<p style="margin:0;font-size:9.6pt;line-height:1.34">In F major the loop is {", ".join(nm for _, nm, _ in fk)}, one chord a bar, {LOOP_BARS} bars = {fmt(LOOP_BARS * EX_BAR_S)} s. The bass plays each chord’s root ({", ".join(t[0] for _, _, t in fk)}) on grid steps 3, 7, 11 and 15, '
             f'between the kicks. The student checked the first tune note of each bar against its chord and moved one chord to fit.</p>'
             f'{D.H2("6 · The sidechain")}'
             f'<p style="margin:0;font-size:9.6pt;line-height:1.34">A compressor on the bass, pad and tune listens to the kick. Ratio {RATIO}:1, a threshold chosen so the meter dips on each kick, the attack as fast as it goes and a release of one beat, {exact(ms(spb(EX_BPM)))} ms. '
             f'With the example settings a kick at 0 dB turns the bass down by {exact(gain_reduction(0))} dB. The student also tried a release of 2 steps ({exact(ms(2 * step_len(EX_BPM)))} ms) and chose the longer one.</p>'
             f'{D.H2("7 · The timing at three tempos")}'
             f'<table class="t ec" style="font-size:8.8pt;line-height:1.14"><tr><th>BPM</th><th>One bar (s)</th><th>4-bar pattern (s)</th><th>64-bar arrangement (s)</th></tr>{ex_len_rows()}</table>'
             f'{D.H2("8 · The 64-bar arrangement")}'
             f'<div style="margin:1pt auto 3pt;width:68%">{D.body_svg(arr_body(1600, "arrange page"))}</div>'
             f'<div class="cols" style="gap:10pt;align-items:flex-start"><div style="flex:0 0 3.0in"><table class="t ec" style="font-size:8.8pt;line-height:1.14"><tr><th>Layer</th><th>Bars it plays</th><th>Bars</th></tr>{ex_layer_rows()}</table></div>'
             f'<p style="margin:0;font-size:9pt;line-height:1.32">{ARR_BARS} bars × {fmt(EX_BAR_S)} s = {fmt(ARR_BARS * EX_BAR_S)} s. The intro starts at {exact(hit_time(EX_BPM, 1, 1))} s, the build at {exact(hit_time(EX_BPM, 9, 1))} s, '
             f'the first drop at {exact(hit_time(EX_BPM, 17, 1))} s, the break at {exact(hit_time(EX_BPM, 33, 1))} s, the second drop at {exact(hit_time(EX_BPM, 41, 1))} s and the outro at {exact(hit_time(EX_BPM, 57, 1))} s. '
             f'The layers play {sum(len(bars_of(r)) for r in ARR_LAYERS)} bars in all.</p></div>'
             f'<div class="cols" style="gap:10pt;align-items:flex-start;margin-top:5pt"><div class="box"><span class="k">9 · Three feedback questions (invented)</span><p style="margin:0;font-size:9.6pt;line-height:1.32">{qs}</p></div>'
             f'<div class="box acc-b"><span class="k">10 · Moments to point out in class</span><ul style="margin:0">'
             f'<li style="font-size:9.6pt;margin-bottom:2pt">In the first drop, solo the kick and the bass and listen for the dip: that is the sidechain.</li>'
             f'<li style="font-size:9.6pt;margin-bottom:0">At {EX_BPM} BPM a bar is exactly 1.875 s, so the class can count bars and hear the break strip back at 60 seconds.</li></ul></div></div>')
    return D.page("Worked example · the chords, the sidechain and the arrangement", "EXAMPLE", "Teacher", inner, n, wm, ak=True, key="example2")


PAGES = {"howto": howto_page, "overview": overview_page, "setup": setup_page, "example": example_page, "example2": example2_page,
         "timing": timing_page, "tune": tune_page, "pattern": pattern_page, "chords": chords_page, "sidechain": sidechain_page, "roles": roles_page, "arrange": arrange_page, "mix": mix_page}


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



BADGE = {"timing": "Class 1", "tune": "Class 1", "pattern": "Class 1", "chords": "Class 2", "sidechain": "Class 2", "roles": "Class 2", "arrange": "Class 3", "mix": "Class 3",
         "present": f"Classes {CLASSES - 1}–{CLASSES}"}


FORBIDDEN_WORDS = ("cham" + "pagne", "toast", "cheers", "wine", "beer", "cocktail", "alcohol", "bub" + "bly", "church", "prayer", "pray ", "blessing", "holy", "sacred",
                   "religio", "god ", "santa", "christmas", "hanukkah", "chanukah", "kwanzaa", "sleigh", "reindeer", "ornament", "elf ", "elves", "sale", "shopping", "buy ", "lyrics are")
EXPECT_STEP = {"timing": {1}, "tune": {2}, "pattern": {3}, "chords": {4}, "sidechain": {5}, "roles": {5}, "arrange": {6}, "mix": {6}}
# the table rows the timing page prints (BPM: ms per beat, ms per step, s per bar, 16 bars, 64 bars), worked out by hand
WANT_TEMPO = {100: ("600.00", "150.00", "2.400", "38.400", "153.600"), 110: ("545.45", "136.36", "2.182", "34.909", "139.636"), 120: ("500.00", "125.00", "2.000", "32.000", "128.000"),
              124: ("483.87", "120.97", "1.935", "30.968", "123.871"), 128: ("468.75", "117.19", "1.875", "30.000", "120.000"), 130: ("461.54", "115.38", "1.846", "29.538", "118.154")}
WANT_LEN = {120: ["16.000", "32.000", "64.000", "128.000"], 124: ["15.484", "30.968", "61.935", "123.871"], 128: ["15.000", "30.000", "60.000", "120.000"]}
WANT_TUNE = {90: ("1.4222", "42.22%", "42.667"), 100: ("1.2800", "28.00%", "38.400"), 110: ("1.1636", "16.36%", "34.909"), 120: ("1.0667", "6.67%", "32.000")}
PER_BAR = [2] * 4 + [3] * 4 + [3] * 8 + [6] * 16 + [2] * 8 + [6] * 16 + [3] * 4 + [2] * 4
SLIDE_PAGE_REFS = ((5, "timing"), (6, "pattern"), (7, "tune"), (8, "chords"), (9, "roles"), (9, "logicref"), (10, "sidechain"), (11, "sidechain"), (12, "logicref"), (13, "roles"),
                   (14, "arrange"), (15, "mix"))       # (index into SLIDES, page the speaker notes must name)


def svg_count(svg, cls):
    return len(re.findall(rf'class="{cls}"', svg))


def verify_content():
    errs = []
    counts = dict(goals=(GOALS, 4), vocab=(VOCAB, 8), reqs=(REQS, 7), steps=(STEPS, 7), tips=(TIPS, 4), check=(CHECK, 6),
                  rubric=(RUBRIC, 5), struggles=(STRUGGLES, 4), resources=(RESOURCES, 5), slides=(SLIDES, 20), plan=(PLAN, 26),
                  logic=(LOGIC_REF, 8), sounds=(SOUNDS, 6), roles=(ROLES, 4), arrange=(ARR_ROWS, 6), sections=(ARR_SECTIONS, 6), lanes=(LANES, 5))
    for nm, (lst, nexp) in counts.items():
        if len(lst) != nexp:
            errs.append(f"{nm}: {len(lst)} items, expected {nexp}")
    if RUBRIC_TOTAL != 25 or LEVELS != [1, 2, 3, 4, 5] or len(RUBRIC_SHORT) != 5:
        errs.append("rubric is /25, levels 1-5")
    if FILE_NAME not in CHECK[2]:
        errs.append("file name format must be on the checklist")
    if [w for w, _ in VOCAB] != ["Four on the floor", "Sidechain", "Kick", "Off-beat", "Build", "Drop", "Breakdown", "Release"]:
        errs.append("vocabulary: four on the floor, sidechain, kick, off-beat, build, drop, breakdown, release")
    if set(TAGS) & {"Holiday", "Student Practice", "Theme", "Seasonal"} or "Performing Arts" in SUBJECTS:
        errs.append("tags and subjects must not be headings")
    if len(LISTING_TITLE) > 80 or "Logic Pro" not in LISTING_TITLE[:30]:
        errs.append("listing title: at most 80 characters, 'Logic Pro' in the first 30")
    for w in ("new year", "winter", "holiday", "christmas", "hanukkah", "chanukah", "sleigh", "carol", "snow", "eve ", "bells", "gift", "wrap", "deck", "halls"):
        if w in LISTING_TITLE.lower():
            errs.append(f"the listing title must not hold the seasonal word {w}")
    if len(STEP_NAMES) != len(STEPS) or any(not s.startswith(f"<b>{nm}</b>") for s, nm in zip(STEPS, STEP_NAMES)):
        errs.append("STEPS must start with the bold names in STEP_NAMES (the pages cite them)")
    # ---- the tempo arithmetic for 4/4, by hand first
    if [spb(b) for b in (120, 100, 128)] != [Fraction(1, 2), Fraction(3, 5), Fraction(15, 32)]:
        errs.append("seconds per beat = 60 / BPM: 0.5 at 120, 0.6 at 100, 0.46875 at 128")
    if spb(128) != Fraction(15, 32) or float(ms(spb(128))) != 468.75 or step_len(128) != Fraction(15, 128) or float(ms(step_len(128))) != 117.1875 or bar_len(128) != Fraction(15, 8) or float(bar_len(128)) != 1.875:
        errs.append("128 BPM: one beat = 60 / 128 = 0.46875 s = 468.75 ms, one step = 15 / 128 = 0.1171875 s = 117.1875 ms, one bar = 240 / 128 = 1.875 s")
    if [step_len(b) for b in (100, 120)] != [Fraction(3, 20), Fraction(1, 8)] or [bar_len(b) for b in (100, 120)] != [Fraction(12, 5), Fraction(2)]:
        errs.append("a step = 15 / BPM (0.15 and 0.125 s at 100 and 120 BPM) and a bar = 240 / BPM (2.4 and 2 s)")
    for b in TEMPOS:
        if bar_len(b) != BEATS_BAR * spb(b) or bar_len(b) != STEPS_BAR * step_len(b) or abs(float(bar_len(b)) - 240.0 / b) > 1e-12 or abs(float(step_len(b)) - 15.0 / b) > 1e-12 or \
           abs(float(spb(b)) - 60.0 / b) > 1e-12:
            errs.append(f"a bar of 4/4 is 4 beats and 16 steps at {b} BPM")
        if 16 * bar_len(b) != Fraction(3840, b) or ARR_BARS * bar_len(b) != Fraction(15360, b):
            errs.append(f"16 bars = 3840 / BPM and 64 bars = 15360 / BPM at {b} BPM")
        got = (dec(ms(spb(b)), 2), dec(ms(step_len(b)), 2), dec(bar_len(b), 3), dec(16 * bar_len(b), 3), dec(ARR_BARS * bar_len(b), 3))
        if got != WANT_TEMPO[b]:
            errs.append(f"timing row at {b} BPM is {got}, expected {WANT_TEMPO[b]}")
        # an independent float method (round half up through Decimal)
        from decimal import Decimal, ROUND_HALF_UP
        f_ = lambda x, nd: str(Decimal(x).quantize(Decimal(1).scaleb(-nd), rounding=ROUND_HALF_UP))
        if (f_(Decimal(60000) / Decimal(b), 2), f_(Decimal(15000) / Decimal(b), 2), f_(Decimal(240) / Decimal(b), 3)) != WANT_TEMPO[b][:3]:
            errs.append(f"independent decimal method disagrees at {b} BPM")
    for t in LEN_TEMPOS:
        if [dec(nb * bar_len(t), 3) for nb in LEN_BARS] != WANT_LEN[t] or any(abs(float(nb * bar_len(t)) - nb * 240.0 / t) > 1e-9 for nb in LEN_BARS):
            errs.append(f"lengths of 8, 16, 32 and 64 bars at {t} BPM")
        for nb in LEN_BARS:
            if Fraction(nb * bar_len(t)) * t / 240 != nb:
                errs.append(f"seconds x BPM / 240 gives the bars back at {t} BPM")
    if rnd(Fraction(5, 2), 0) != 3 or dec(Fraction(15, 128), 4) != "0.1172" or dec(ms(step_len(128)), 2) != "117.19" or exact(ms(step_len(128))) != "117.1875":
        errs.append("round half up: 117.1875 ms prints as 117.19")
    if ms(step_len(128)) * 4 != ms(spb(128)) or step_len(128) * 8 != bar_len(128) / 2 or ms(spb(128) / 2) != Fraction(1875, 8):
        errs.append("4 steps make a beat; an eighth note at 128 BPM is 234.375 ms")
    if not (HOUSE_TYPICAL[0] <= EX_BPM <= HOUSE_TYPICAL[1] and HOUSE_CHARACTERISTIC[0] <= EX_BPM <= HOUSE_CHARACTERISTIC[1]):
        errs.append("128 BPM must sit inside both house tempo ranges")
    if EX_BPM != 128 or 16 * bar_len(128) != 30 or 32 * bar_len(128) != 60 or ARR_BARS * bar_len(128) != 120:
        errs.append("128 BPM: 16 bars = 30 s, 32 bars = 60 s, 64 bars = 120 s")
    # ---- the song's tempo change
    for t, (ratio, pct, bars16) in WANT_TUNE.items():
        if (dec(Fraction(EX_BPM, t), 4), dec((Fraction(EX_BPM, t) - 1) * 100, 2) + "%", dec(16 * bar_len(t), 3)) != (ratio, pct, bars16):
            errs.append(f"tempo change from {t} to 128 BPM is {ratio}, {pct}, 16 bars = {bars16}")
        if abs((128 - t) / t * 100 - float(Fraction(EX_BPM, t) - 1) * 100) > 1e-9:
            errs.append(f"percent faster, float method, at {t} BPM")
    if Fraction(128, 100) != Fraction(32, 25) or (Fraction(128, 100) - 1) * 100 != 28 or 16 * bar_len(100) != Fraction(192, 5) or 16 * bar_len(128) != 30:
        errs.append("100 to 128 BPM: ratio 1.28, 28% faster, 16 bars from 38.4 s to 30 s")
    # ---- the sidechain numbers
    if [gain_reduction(L) for L in KICK_LEVELS] != [0, 3, 6, 9, 12, 15] or gain_reduction(-16) != 3 or gain_reduction(-30) != 0 or RATIO != 4 or THRESH_DB != -20:
        errs.append("gain reduction at -20, -16, -12, -8, -4, 0 dB with a -20 dB threshold and 4:1 = 0, 3, 6, 9, 12, 15 dB (4 dB over at 4:1 is 3 dB down)")
    if [exact(ms(k * step_len(EX_BPM))) for k in (1, 2, 3, 4)] != ["117.1875", "234.375", "351.5625", "468.75"] or ms(4 * step_len(EX_BPM)) != ms(spb(EX_BPM)):
        errs.append("release times: 1, 2, 3 and 4 steps = 117.1875, 234.375, 351.5625 and 468.75 ms; four steps are one beat")
    if [float(ms((s - 1) * step_len(EX_BPM))) for s in FLOOR_STEPS] != [0.0, 468.75, 937.5, 1406.25] or float(ms(bar_len(EX_BPM))) != 1875.0:
        errs.append("the four kicks of a bar fall at 0, 468.75, 937.5 and 1406.25 ms, and a bar is 1875 ms")
    # ---- the layers
    if [s[0] for s in SOUNDS] != ["KICK", "CLAP", "HATS", "BASS", "PAD", "MELODY"] or [s[5] for s in SOUNDS] != ["TRIGGER", "NO DUCK", "NO DUCK", "DUCKED", "DUCKED", "DUCKED"] or DUCKED != ["BASS", "PAD", "MELODY"]:
        errs.append("the six layers: kick (trigger), clap and hats (no duck), bass, pad and melody (ducked)")
    if {s[2] for s in SOUNDS} != {r for r, _, _ in ROLES} or any(not (1 <= v <= 3) for s in SOUNDS for v in s[3:5]):
        errs.append("every role is used by a layer, and pitch and length are 1 to 3")
    if set(ARR_LAYERS) != set(LAYERS):
        errs.append("arrangement layers are the six layers")
    # ---- the pattern
    for nm in LANES:
        if len(PATTERN[nm]) != PAT_BARS:
            errs.append(f"{nm}: {PAT_BARS} bars of steps")
        for bar in PATTERN[nm]:
            if bar != sorted(set(bar)) or any(not 1 <= s <= STEPS_BAR for s in bar):
                errs.append(f"{nm}: grid steps must be distinct, rising and in 1-16: {bar}")
    if PAT_HITS != [22, 22, 22, 24] or PAT_TOTAL != 90 or [LANE_HITS[l] for l in LANES] != [16, 10, 32, 16, 16] or sum(LANE_HITS.values()) != PAT_TOTAL:
        errs.append("pattern hits per bar 22, 22, 22, 24 = 90; per lane 16, 10, 32, 16, 16 = 90")
    if any(PATTERN["KICK"][b] != [1, 5, 9, 13] for b in range(PAT_BARS)):
        errs.append("four on the floor: the kick plays on grid steps 1, 5, 9 and 13 in every bar (4 a bar, one on every beat)")
    if [(s - 1) // 4 + 1 for s in PATTERN["KICK"][0]] != [1, 2, 3, 4] or any((s - 1) % 4 != 0 for b in range(PAT_BARS) for s in PATTERN["KICK"][b]):
        errs.append("the kick sits on the first step of each beat")
    if any(PATTERN["OPEN HAT"][b] != OFFBEAT_STEPS or PATTERN["BASS"][b] != OFFBEAT_STEPS for b in range(PAT_BARS)) or any((s - 1) % 4 != 2 for s in OFFBEAT_STEPS):
        errs.append("the open hat and the bass play on the off-beats, grid steps 3, 7, 11 and 15: the 'and' of each beat")
    if any(PATTERN["CLAP"][b][:2] != [5, 13] for b in range(PAT_BARS)) or PATTERN["CLAP"][3] != [5, 13, 15, 16] or [(5 - 1) // 4 + 1, (13 - 1) // 4 + 1] != [2, 4]:
        errs.append("the clap plays on grid steps 5 and 13 (beats 2 and 4); bar 4 adds a fill on 15 and 16")
    if any(PATTERN["CLOSED HAT"][b] != list(range(2, 17, 2)) for b in range(PAT_BARS)):
        errs.append("the closed hat plays on the even steps 2 to 16")
    if any(set(PATTERN["KICK"][b]) & set(PATTERN["BASS"][b]) for b in range(PAT_BARS)):
        errs.append("the bass never shares a step with the kick")
    if hit_time(EX_BPM, 2, 5) != Fraction(75, 32) or float(hit_time(EX_BPM, 2, 5)) != 2.34375 or hit_time(EX_BPM, 2, 5) != bar_len(128) + spb(128):
        errs.append("bar 2, grid step 5 at 128 BPM = (16 + 4) x 15 / 128 = 2.34375 s = one bar + one beat")
    if abs(float(hit_time(EX_BPM, 2, 5)) - ((2 - 1) * 16 + (5 - 1)) * 15.0 / 128) > 1e-12:
        errs.append("hit time formula, float method")
    gp, gb = grid_body(1600, "g check")[0], grid_body(1600, "gb check", blank=True)[0]
    if svg_count(gp, "hit") != PAT_TOTAL or svg_count(gp, "cell") != NLANE * PAT_BARS * STEPS_BAR or svg_count(gb, "hit") != 0 or svg_count(gb, "cell") != NLANE * PAT_BARS * STEPS_BAR:
        errs.append(f"the step grid drawing must hold {PAT_TOTAL} hits and {NLANE * PAT_BARS * STEPS_BAR} cells; the blank grid holds no hits")
    labels = [int(x) for x in re.findall(r">(\d+) hits<", gp)]
    if labels != PAT_HITS:
        errs.append(f"the drawn hits per bar {labels} do not match the data {PAT_HITS}")
    ys = [round(float(y)) for y in re.findall(r'class="hit" x="[\d.]+" y="([\d.]+)"', gp)]
    for ln, nm in enumerate(LANES):          # each lane's hit rectangles, counted again by row
        if len([y for y in ys if round(92 + ln * 46 + 6) == y]) != LANE_HITS[nm]:
            errs.append(f"lane {nm}: the drawing holds a different number of hits than the data ({LANE_HITS[nm]})")
    # ---- the chords: stacking thirds in the scale
    ivs = [2, 2, 1, 2, 2, 2, 1]
    for key, sc in SCALES.items():
        pcs = [PC[x] for x in sc]
        if PC[key] != pcs[0] or [(pcs[(i + 1) % 7] - pcs[i]) % 12 for i in range(7)] != ivs:
            errs.append(f"scale of {key} major is not whole, whole, half, whole, whole, whole, half")
        if [x[0] for x in sc] != [chr((ord(sc[0][0]) - 65 + i) % 7 + 65) for i in range(7)]:
            errs.append(f"scale of {key} major uses each letter once")
        for rn, d, q in DEGREES:
            t = triad(key, d)
            i1, i2 = (PC[t[1]] - PC[t[0]]) % 12, (PC[t[2]] - PC[t[1]]) % 12
            if (i1, i2) != ((4, 3) if q == "major" else (3, 4)):
                errs.append(f"{key} {rn}: thirds {i1}, {i2} do not make a {q} triad")
    if [(rn, nm, t) for rn, nm, t in loop_chords("F")] != [("I", "F", ["F", "A", "C"]), ("IV", "Bb", ["Bb", "D", "F"]), ("V", "C", ["C", "E", "G"]), ("vi", "Dm", ["D", "F", "A"])] or \
       [nm for _, nm, _ in loop_chords("C")] != ["C", "F", "G", "Am"] or [nm for _, nm, _ in loop_chords("G")] != ["G", "C", "D", "Em"]:
        errs.append("the I, IV, V and vi chords: F, Bb, C, Dm in F; C, F, G, Am in C; G, C, D, Em in G")
    if [t[0] for _, _, t in loop_chords("F")] != ["F", "Bb", "C", "D"] or LOOP_BARS != 4 or LOOP_BARS * EX_BAR_S != Fraction(15, 2):
        errs.append("bass roots F, Bb, C, D; the 4-bar loop lasts 7.5 s at 128 BPM")
    # ---- the arrangement
    for nm, spans in ARR_ROWS:
        last = 0
        for a, b in spans:
            if not (1 <= a <= b <= ARR_BARS) or a <= last:
                errs.append(f"layer {nm}: bars {a}-{b} outside 1-{ARR_BARS} or out of order")
            last = b
    secs = [(n_, a, b) for n_, a, b in ARR_SECTIONS]
    if secs != [("INTRO", 1, 8), ("BUILD", 9, 16), ("DROP", 17, 32), ("BREAK", 33, 40), ("DROP", 41, 56), ("OUTRO", 57, 64)] or any(secs[i][2] + 1 != secs[i + 1][1] for i in range(5)) or secs[-1][2] != ARR_BARS:
        errs.append("sections of the map: 8, 8, 16, 8, 16 and 8 bars, one after the other, 64 in all")
    if [exact(hit_time(EX_BPM, a, 1)) for _, a, _ in secs] != ["0", "15", "30", "60", "75", "105"] or hit_time(EX_BPM, ARR_BARS + 1, 1) != 120 or ARR_BARS * EX_BAR_S != 120:
        errs.append("section starts at 128 BPM: 0, 15, 30, 60, 75 and 105 s; the end at 120 s")
    if [(a - 1) * 1.875 for _, a, _ in secs] != [0.0, 15.0, 30.0, 60.0, 75.0, 105.0]:
        errs.append("section starts, float method")
    per_bar = [len(layers_in_bar(b)) for b in range(1, ARR_BARS + 1)]
    if per_bar != PER_BAR or sum(per_bar) != 272 or [len(bars_of(r)) for r in ARR_LAYERS] != [48, 40, 48, 32, 64, 40] or sum(len(bars_of(r)) for r in ARR_LAYERS) != 272:
        errs.append("layers sounding per bar 2 x4, 3 x12, 6 x16, 2 x8, 6 x16, 3 x4, 2 x4 = 272 layer-bars = 48 + 40 + 48 + 32 + 64 + 40")
    if len(ARR_LAYERS) != 6:
        errs.append("the arrangement has 6 layers")
    if any(b not in bars_of("KICK") for b in bars_of("BASS")) or any(b in bars_of("KICK") for b in range(33, 41)) or any(b in bars_of("KICK") for b in range(9, 17)):
        errs.append("the bass plays only where the kick plays (the trigger); the kick is out in the build and the break")
    if min(len(layers_in_bar(b)) for b in range(17, 33)) != 6 or min(len(layers_in_bar(b)) for b in range(41, 57)) != 6 or max(len(layers_in_bar(b)) for b in range(33, 41)) != 2:
        errs.append("all 6 layers play in both drops and 2 in the break")
    am = arr_body(1600, "a check")[0]
    if svg_count(am, "block") != sum(len(s) for _, s in ARR_ROWS) or svg_count(am, "cnt") != ARR_BARS or svg_count(am, "sec") != 6 or svg_count(am, "lane") != 6:
        errs.append(f"the arrangement drawing must hold {sum(len(s) for _, s in ARR_ROWS)} blocks, {ARR_BARS} layer counts, 6 section bars and 6 lanes")
    drawn = [int(x) for x in re.findall(r'class="cnt"[^>]*>(\d+)<', am)]
    if drawn != per_bar:
        errs.append(f"the drawn layer counts {drawn} do not match the data {per_bar}")
    if len(re.findall(r">(?:KICK|CLAP|HATS|BASS|PAD|MELODY)<", am)) != 6:
        errs.append("the arrangement drawing must name 6 layers")
    if [x for x in re.findall(r">(INTRO|BUILD|DROP|BREAK|OUTRO) \d+–\d+<", am)] != ["INTRO", "BUILD", "DROP", "BREAK", "DROP", "OUTRO"]:
        errs.append("the arrangement drawing must label its 6 sections in order")
    secs_drawn = re.findall(r">(?:INTRO|BUILD|DROP|BREAK|OUTRO) (\d+)–(\d+)<", am)
    if [(int(a), int(b)) for a, b in secs_drawn] != [(a, b) for _, a, b in secs]:
        errs.append("the drawn section bars do not match the data")
    secs_s = re.findall(r'text-anchor="(?:start|middle|end)" fill="#000" >(0|15|30|60|75|105|120)<', am)
    if secs_s != ["0", "15", "30", "60", "75", "105", "120"]:
        errs.append(f"the drawn section start seconds {secs_s} do not match 0, 15, 30, 60, 75, 105 and the end 120")
    # ---- the layer table, signal chain, gain curve and ducking drawings
    rb, cb = roles_body(1600, "r check")[0], chain_body(1620, "c check")[0]
    if svg_count(rb, "row") != NSND or svg_count(rb, "icon") != NSND or svg_count(rb, "chip") != NSND or svg_count(rb, "scchip") != NSND or svg_count(rb, "dot on") + svg_count(rb, "dot off") != NSND * 6 or \
       svg_count(rb, "dot on") != sum(s[3] + s[4] for s in SOUNDS):
        errs.append("the layer table drawing must hold 6 rows, 6 icons, 6 role chips, 6 side-chain chips and 36 dots, with as many filled dots as the levels add up to")
    for nm, _, role, p, ln, sc, _, _ in SOUNDS:
        if f">{nm}<" not in rb or f">{role}<" not in rb or f">{PITCH_W[p]}<" not in rb or f">{LEN_W[ln]}<" not in rb or f">{sc}<" not in rb:
            errs.append(f"the layer table drawing must print {nm}, {role}, {PITCH_W[p]}, {LEN_W[ln]} and {sc}")
    if [len(re.findall(rf">{w}<", rb)) for w in ("TRIGGER", "DUCKED", "NO DUCK")] != [1, 3, 2]:
        errs.append("the layer table drawing must show 1 TRIGGER, 3 DUCKED and 2 NO DUCK chips")
    if svg_count(cb, "stage") != 5 or svg_count(cb, "arrow") != 4 or re.findall(r">(KICK TRACK|SIDE CHAIN|COMPRESSOR|LEVEL DIPS|MIX)<", cb) != ["KICK TRACK", "SIDE CHAIN", "COMPRESSOR", "LEVEL DIPS", "MIX"]:
        errs.append("the signal chain drawing must hold 5 stages (kick track, side chain, compressor, level dips, mix) and 4 arrows")
    cu = curve_body(1500, "cu check")[0]
    if [int(x) for x in re.findall(r'class="ptl"[^>]*>(\d+)<', cu)] != [0, 3, 6, 9, 12, 15] or svg_count(cu, "pt") != 6 or svg_count(cu, "line") != 1:
        errs.append("the gain-reduction curve must plot 6 points labeled 0, 3, 6, 9, 12 and 15 dB and one line")
    m = re.search(r'class="line" points="([^"]+)"', cu)
    pts = [tuple(map(float, p.split(","))) for p in m.group(1).split()] if m else []
    gy0, gy1 = 70, 400
    ysf = lambda gr: gy1 - float(gr) / 16 * (gy1 - gy0)
    if len(pts) != 3 or abs(pts[0][1] - ysf(0)) > 0.06 or abs(pts[1][1] - ysf(0)) > 0.06 or abs(pts[2][1] - ysf(gain_reduction(0))) > 0.06:
        errs.append("the gain-reduction line must run flat to the threshold and end at 15 dB for a 0 dB kick")
    # no data label's box (text plus its 4 px halo) may come within 6 px of the plot frame, the dashed threshold line or the curve
    fx0, fy0, fx1, fy1 = 210, 70, 210 + (1500 - 210 - 70), 400
    thr_x = fx0 + (THRESH_DB + 40) / 40 * (fx1 - fx0)
    segs = [(fx0 + (a + 40) / 40 * (fx1 - fx0), ysf(gain_reduction(a)), fx0 + (b + 40) / 40 * (fx1 - fx0), ysf(gain_reduction(b))) for a, b in ((-40, THRESH_DB), (THRESH_DB, 0))]
    def seg_gap(bx0, by0, bx1, by1, sg):
        n = 400
        return min(max(bx0 - px_, 0, px_ - bx1) ** 2 + max(by0 - py_, 0, py_ - by1) ** 2
                   for px_, py_ in ((sg[0] + (sg[2] - sg[0]) * i / n, sg[1] + (sg[3] - sg[1]) * i / n) for i in range(n + 1))) ** 0.5
    for tm in re.finditer(r'<text x="([\d.]+)" y="([\d.]+)"[^>]*text-anchor="(\w+)"[^>]*class="ptl"[^>]*>(\d+)<', cu):
        lx, ly, la, txt = float(tm.group(1)), float(tm.group(2)), tm.group(3), tm.group(4)
        w = 0.52 * 30 * len(txt)
        bx0 = lx - (w if la == "end" else w / 2 if la == "middle" else 0) - 4
        bx1 = bx0 + w + 8
        by0, by1 = ly - 24 - 4, ly + 2 + 4
        if by0 - fy0 < 6 or fx1 - bx1 < 6 or fy1 - by1 < 6 or bx0 - fx0 < 6:
            errs.append(f"gain-curve label {txt} comes within 6 px of (or crosses) the plot frame")
        if max(bx0 - thr_x, thr_x - bx1) < 6:
            errs.append(f"gain-curve label {txt} comes within 6 px of the dashed threshold line")
        if any(seg_gap(bx0, by0, bx1, by1, sg) < 3 + 3 for sg in segs):   # the curve is 6 px wide: 3 px half-width plus a 3 px gap
            errs.append(f"gain-curve label {txt} touches the curve")
    du = duck_body(1500, "du check")[0]
    if svg_count(du, "kick") != 4 or svg_count(du, "dip") != 4 or re.findall(r">grid step (\d+)<", du) != ["1", "5", "9", "13"] or \
       re.findall(r">(0|468\.75|937\.5|1406\.25) ms<", du) != ["0", "468.75", "937.5", "1406.25"] or "release 468.75 ms" not in du or "One bar = 1875 ms = 16 steps" not in du:
        errs.append("the ducking drawing must hold 4 kicks (steps 1, 5, 9, 13 at 0, 468.75, 937.5, 1406.25 ms), 4 dips, a release of 468.75 ms and a bar of 1875 ms")
    for k in ICON_KINDS:
        if len(icon(k, 0, 0)) < 80:
            errs.append(f"icon {k} is empty")
    # ---- Logic wording: newer tools are hedged
    for nm, txt in LOGIC_REF:
        if any(w in txt for w in ("Drum Machine Designer", "Step Sequencer", "Retro Synth", "Alchemy", "Side Chain menu", "Marker track", "transpose option", "key command")) and \
           "if your version" not in txt.lower():
            errs.append(f"Logic reference '{nm}' must hedge a newer or version-specific tool with 'if your version'")
    joined = " ".join(t for _, t in LOGIC_REF)
    for w in ("Drum Machine Designer", "Step Sequencer", "Piano Roll", "Compressor", "Side Chain", "attack", "release", "threshold", "ratio", "Retro Synth", "Alchemy", "Mixer", "Bounce", "0 dBFS", "4/4", "468.75", "128 BPM"):
        if w.lower() not in joined.lower():
            errs.append(f"the Logic quick reference must name {w}")
    # ---- the worked example
    if EX_BPM != 128:
        errs.append("the example is at 128 BPM")
    for need in ("4/4 at 128 BPM", "60 ÷ 128 = 0.46875 seconds", "15 ÷ 128 = 0.1171875 seconds", "240 ÷ 128 = 1.875 seconds", "1.28 times as fast, 28% faster", "22, 22, 22 and 24 hits, 90 in all",
                 "468.75 ms", "64 bars = 120 seconds", "bars 1 to 8", "bars 9 to 16", "bars 17 to 32", "bars 33 to 40", "bars 41 to 56", "bars 57 to 64", "6 layers"):
        if need not in EX_STRONG:
            errs.append(f"the clear plan must say '{need}'")
    # ---- no forbidden themes in any text a buyer reads
    allt = " ".join([SONG_FACTS, THEME, BUILD_NOTE, KEY_NOTE, OVERVIEW, " ".join(GOALS), " ".join(f"{a} {b}" for a, b in VOCAB), " ".join(REQS), " ".join(STEPS), " ".join(TIPS), " ".join(CHECK),
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
    for w in ("wikipedia", "imslp", "wikimedia", "apple support", "commons", "cpdl", "mutopia"):
        if w in allt:
            errs.append(f"buyer-facing text must not name a source ({w})")
    for w in (" hz", "khz", "-12 to -6", "−12 to −6", "−6 dbfs", "-6 dbfs"):
        if w in allt:
            errs.append(f"no frequency or level numbers in a kit that has no source for them: '{w}'")
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
    for key, need in SLIDE_PAGE_REFS:
        if f"page {pg(need)}" not in SLIDES[key][4]:
            errs.append(f"slide {key + 1} notes must name page {pg(need)} ({need})")
    for i, s in enumerate(SLIDES, start=1):
        errs += step_ref_errors(" ".join((s[2], s[3], s[4])), f"slide {i}")
    if [s[0] for s in SLIDES] != [1] * 8 + [2] * 6 + [3] * 6 or SLIDES[3][1] != "days":
        errs.append("deck classes: slides 1-8 Class 1, 9-14 Class 2, 15-20 Class 3; slide 4 is the 'days' slide (it gets the Classes 1-3 badge)")
    if [d["slides"] for d in PACING] != [(1, 8), (9, 14), (15, 20)]:
        errs.append("pacing slide slots 1-8, 9-14, 15-20")
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
    """Every stated number of lanes, steps, hits, bars, roles, stages, sections or layers equals the drawings and the data."""
    errs = []
    allowed_bars = {0, 1, 2, 3, 4, 8, 16, 32, 40, 48, 64, 272}     # 0: a table cell next to the word 'bars' in the flattened page text
    allowed_steps = {1, 2, 3, 4, 16, 64}
    allowed_hits = {22, 24, 90}
    for label, t in texts:
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
                errs.append(f"{label}: '{m.group(0)}' is not a hit count from the model pattern (22, 22, 22, 24; 90 in all)")
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
            if int(m.group(1)) != NLANE:
                errs.append(f"{label}: '{m.group(0)}' but the step grid has {NLANE} lanes")
        for m in re.finditer(r"\b(\d+) kicks\b", t):
            if int(m.group(1)) != 4:
                errs.append(f"{label}: '{m.group(0)}' but a bar has 4 kicks")
    return errs


C1_BANNED = r"\bsidechain\b|\bside chain\b|\bcompressor\b|\bchords?\b|\barrange(ment|d)?\b|\bmix(ing)?\b|\bdrop\b|\bbuild\b|\bbreak\b|\brelease\b|\bduck(s|ed|ing)?\b|\bbass\b"
C2_BANNED = r"\barrange(ment|d)?\b|\bmix(ing)?\b|\bhigh-pass\b|\bEQ\b|\bbounce\b|\blayers?\b|\bintro\b|\boutro\b|\bdrop\b|\bbuild\b|\bbreak\b"


def class_step_errors():
    """A deck slide badged Class 2 does not name the arrangement, mix, layers, build, drop or break (the pacing table puts them in Class 3), and a Class 1 slide does not teach the
    chords, bass or sidechain (Class 2) or the arrangement (Class 3). Title, bullet, 'listen' and 'days' slides may preview the whole project."""
    errs = []
    for i, s in enumerate(SLIDES, start=1):
        shown = " ".join((s[2], s[3] if s[1] != "pic" else ""))
        if s[0] == 2 and re.search(C2_BANNED, shown, re.I):
            errs.append(f"deck slide {i} is badged Class 2 but names arrangement, mix or layer content, which the pacing page assigns to Class 3")
        if s[0] == 1 and re.search(C1_BANNED, shown, re.I) and s[1] not in ("title", "days", "listen") and i != 3:
            errs.append(f"deck slide {i} is badged Class 1 but teaches Class 2 or 3 content")
    return errs




def verify_outputs(flat, stext, notes):
    errs = []
    alldeck = " ".join(stext + notes)
    txt = " ".join(flat)
    if "No audio" not in notes[0]:
        errs.append("deck slide 1 notes must say 'No audio'")
    for need in ("No audio, recordings, lyrics or melody notation", "invented plan on paper", "Four on the floor", "four-on-the-floor", "sidechain", "side chain", "off-beat", "kick", "clap", "hat", "bass", "chord",
                 "drop", "build", "break", "release", "ratio", "threshold", "attack", "468.75", "117.19", "1.875", "128 BPM", "Deck the Halls", "Welsh", "1790s", "public domain", "tune",
                 "if your version", "Drum Machine Designer", "Step Sequencer", "Compressor", "0 dBFS", "16th-note", "60 ÷ BPM", "15 ÷ BPM", "240 ÷ BPM", "step grid", "arrangement", "intro", "outro", "listening descriptions",
                 "starting points", "not Logic’s defaults", "schematic", "F major", "115 to 130",
                 "Created with the help of digital and AI tools. Notation and answer keys are verified before release."):
        if need.lower() not in txt.lower().replace("- ", "-"):
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
    for w in (" Hz", "kHz", "−12 to −6", "−6 dBFS"):
        if w in txt or w in alldeck:
            errs.append(f"no frequency or level numbers without a source: '{w}'")
    if re.search(r"\b(lyrics? (?:of|from)|fa la|boughs|holly|jolly|yuletide)\b", (txt + " " + alldeck).lower()):
        errs.append("no lyrics of the song anywhere")
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
        row = f"{bpm} " + " ".join(WANT_TEMPO[bpm])
        if row not in rc:
            errs.append(f"timing page: row '{row}' is not printed")
    for t in LEN_TEMPOS:
        row = f"{t} " + " ".join(WANT_LEN[t])
        if row not in rc:
            errs.append(f"timing page: length row '{row}' is not printed")
    for need in ("Seconds per beat = 60 ÷ BPM", "Seconds per 16th-note step = 15 ÷ BPM", "Seconds per bar = 240 ÷ BPM (16 steps, 4 beats)", "60 ÷ 128 = 0.46875 s = 468.75 ms per beat", "15 ÷ 128 = 0.1171875 s per step",
                 "240 ÷ 128 = 1.875 s per bar", "Step 1: plan the tempo", "5 rounds up", "117.19", "15360 ÷ BPM", "120 seconds at 128 BPM", "120 × 128 ÷ 240 = 64 bars", "115 to 130", "120 to 130"):
        if need.lower() not in rc.lower():
            errs.append(f"timing page must say '{need}'")
    # ---- the song page
    rs = raw("tune")
    for t, (ratio, pct, b16) in WANT_TUNE.items():
        row = f"{t} {ratio} {pct} {b16} 30.000"
        if row not in rs:
            errs.append(f"song page: tempo-change row '{row}' is not printed")
    for need in ("Step 2: prepare the song", "Welsh", "sixteenth century", "1790s", "public domain", "128 ÷ 100 = 1.28", "28% faster", "38.4 s to 30 s", "F major", "4/4", "not facts about the song", "Why not copy a recording?",
                 "middle C is C3"):
        if need.lower() not in rs.lower():
            errs.append(f"song page must say '{need}'")
    # ---- the pattern page
    rp = raw("pattern")
    for nm in LANES:
        row = f"{nm.title()} " + " ".join(str(len(PATTERN[nm][b])) for b in range(PAT_BARS)) + f" {LANE_HITS[nm]}"
        if row not in rp:
            errs.append(f"pattern page: hit row '{row}' is not printed")
    row = "All lanes " + " ".join(str(h) for h in PAT_HITS) + f" {PAT_TOTAL}"
    if row not in rp:
        errs.append(f"pattern page: total row '{row}' is not printed")
    for need in ("Step 3: build the house beat", "64", "22 hits", "24 hits", "90 hits in all", "(16 + 4) × 0.1171875 = 2.34375 s", "grid steps 1, 5, 9 and 13", "3, 7, 11 and 15", "beats 2 and 4",
                 "BAR 1", "BAR 4", "My pattern", "hits: ______", "KICK", "CLAP", "CLOSED HAT", "OPEN HAT", "BASS"):
        if need.lower() not in rp.lower():
            errs.append(f"pattern page must say '{need}'")
    # ---- the chord page
    rch = raw("chords")
    for key in SCALES:
        for rn, nm, t in loop_chords(key):
            if f"{nm} {' '.join(t)}" not in rch:
                errs.append(f"chord page: chord {nm} ({' '.join(t)}) in {key} is not printed")
        if f"{key} major {' '.join(SCALES[key])}" not in rch:
            errs.append(f"chord page: the scale of {key} major is not printed")
    for need in ("Step 4: add bass and chords", "7.5 s", "4 loops", "chord tone", "Bass between the kicks", "never lands on a kick", "Check the tune against the chords"):
        if need.lower() not in rch.lower():
            errs.append(f"chord page must say '{need}'")
    # ---- the sidechain and layer pages
    rsc = raw("sidechain")
    for L in KICK_LEVELS:
        over = str(L - THRESH_DB).replace("-", "−") if L > THRESH_DB else "0"
        row = f"{str(L).replace('-', '−')} {over} {exact(gain_reduction(L))}"
        if row not in rsc:
            errs.append(f"sidechain page: gain-reduction row '{row}' is not printed")
    for k, nm in ((1, "1 step (a 16th)"), (2, "half a beat (2 steps)"), (3, "three-quarters of a beat (3 steps)"), (4, "1 beat (4 steps)")):
        row = f"{nm} {k}/16 bar {exact(ms(k * step_len(EX_BPM)))}"
        if row not in rsc:
            errs.append(f"sidechain page: release row '{row}' is not printed")
    for need in ("Step 5: set up the sidechain", "side chain input", "4 dB over the threshold is turned down by 3 dB", "(level + 20) × 3/4", "not Logic’s defaults", "no industry standard", "468.75 ms", "schematic",
                 "release 468.75 ms", "GAIN REDUCTION", "KICK LEVEL AT THE SIDE CHAIN", "threshold −20 dB", "ratio 4:1", "grid step 13"):
        if need.lower() not in rsc.lower():
            errs.append(f"sidechain page must say '{need}'")
    rr = raw("roles")
    for nm, _, role, p, ln, sc, use, how in SOUNDS:
        if nm not in rr or role not in rr or sc not in rr or f"{nm} {use} {how}" not in rr:
            errs.append(f"layer page: {nm}, {role}, {sc} and its source row must be printed")
    for need in ("Step 5: set up the sidechain, continued", "KICK TRACK", "SIDE CHAIN", "COMPRESSOR", "LEVEL DIPS", "From the kick to the mix in 5 stages", "6 layers, 4 roles", "3 of them duck", "TRIGGER", "DUCKED", "NO DUCK",
                 "My sidechain settings", "Check the sidechain", "not measurements"):
        if need.lower() not in rr.lower():
            errs.append(f"layer page must say '{need}'")
    # ---- the arrangement and mix pages
    ra = raw("arrange")
    for nm, a, b in ARR_SECTIONS:
        layers = [r for r, spans in ARR_ROWS if any(x <= b and a <= y for x, y in spans)]
        row = f"{nm.title()} {a}–{b} {exact(hit_time(EX_BPM, a, 1))} {exact(hit_time(EX_BPM, b + 1, 1))} {', '.join(x.lower() for x in layers)}"
        if row not in ra:
            errs.append(f"arrangement page: section row '{row}' is not printed")
    for need in ("Step 6: arrange and mix", "6 layers", "6 sections", "272 bars in all: 48 + 40 + 48 + 32 + 64 + 40", "64 bars × 1.875 s = 120 s", "INTRO 1–8", "OUTRO 57–64", "SECONDS", "LAYERS", "My arrangement"):
        if need.lower() not in ra.lower():
            errs.append(f"arrangement page must say '{need}'")
    rx = raw("mix")
    for need in ("Step 6: arrange and mix, continued", "0 dBFS", "sidechain", "small moves", "plenty of room to spare", "Kick and bass first"):
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
    for nm, _, role, p, ln, sc, _, _ in SOUNDS:
        row = f"{nm.title()} {role.title()} {PITCH_W[p].lower()} {LEN_W[ln].lower()} {sc.title()} {len(bars_of(nm))}"
        if row not in re1:
            errs.append(f"worked example: layer table row '{row}' is not printed")
    for need in ("60 ÷ 128 = 0.46875", "240 ÷ 128 = 1.875", "90 in all", "(16 + 4) × 0.1171875 = 2.34375 s", "64 bars × 1.875 s = 120 s", "the build at 15 s", "the second drop at 75 s", "15 dB", "468.75 ms", "234.375 ms",
                 "F, Bb, C, Dm", "7.5 s", "272 bars in all"):
        if need.lower() not in re1.lower():
            errs.append(f"worked example must say '{need}'")
    up = open(os.path.join(HERE, "UPLOAD.md"), encoding="utf8").read()
    errs += step_ref_errors(up, "UPLOAD.md")
    errs += count_claim_errors([("UPLOAD.md", up)])
    if "Grades 9-12" not in up or "`9th-grade`, `10th-grade`, `11th-grade`, `12th-grade`" not in up:
        errs.append("UPLOAD.md: grades 9-12 in the description and section 3")
    if "no audio" not in up.lower() or "Open questions" not in up or "Timing numbers" not in up or "Sources and credits" not in up:
        errs.append("UPLOAD.md: must say no audio is included, record the timing numbers checked, the sources and the open questions")
    for need in ("Four-on-the-floor (music)", "House music", "Dynamic range compression", "Ducking", "Drop (music)", "Time signature", "Tempo", "Hi-hat", "Deck the Halls", "could not", "not from any source",
                 "No melody chart", "CPDL", "403", "117.1875"):
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
    for banned in ["Billie", "Beatles", "Skrillex", "Disney", "Radiohead", "Billboard", "Ro" + "land", "Bensound", "Able" + "ton "]:
        if banned in alldeck or banned in txt:
            errs.append(f"must not name artists, albums, songs, sites, services or other brands ({banned})")
    for brand in ("Wikipedia", "Wikimedia", "Apple Support", "CPDL", "Mutopia"):
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
    return ("seconds per beat = 60 / BPM (468.75 ms at 128), per 16th-note step = 15 / BPM (117.1875 ms) and per bar of 4/4 = 240 / BPM (1.875 s; 4 beats, 16 steps) recomputed exactly (fractions), by an independent decimal method and by hand-typed "
            "expectations at six tempos; 16-bar and 64-bar lengths (3840 and 15360 / BPM; 64 bars = 120 s) and the length table for 8, 16, 32 and 64 bars at three tempos; the tempo change of four plain tempos to 128 BPM (ratio and percent); "
            "128 BPM inside both house tempo ranges; the sidechain numbers (gain reduction at six kick levels from the stated threshold and 4:1 ratio = 0, 3, 6, 9, 12, 15 dB; release times as fractions of a beat; kicks at 0, 468.75, 937.5, 1406.25 ms) "
            "plotted in the gain-curve and ducking drawings; the 5 lanes and the four-on-the-floor pattern (kick on 1, 5, 9, 13; open hat and bass on the off-beats 3, 7, 11, 15; clap on 5 and 13; hits per bar 22, 22, 22, 24 = 90, per lane "
            "16, 10, 32, 16, 16 = 90) counted again in the step-grid drawing; the chord table (I, IV, V, vi built by stacking thirds in C, F and G major); the 64-bar arrangement (6 layers, 6 sections, starts at 0, 15, 30, 60, 75, 105 s, "
            "bars per layer 48 + 40 + 48 + 32 + 64 + 40 = 272, layers per bar) counted again in the drawing; the layer-table drawing (6 rows, 6 icons, 6 role chips, 6 side-chain chips, 36 dots) and the signal chain (5 stages, 4 arrows); every "
            "'Step N' agrees with the project sheet on pages, slides, notes and UPLOAD.md; class badges agree with the pacing page, and the deck's 'three classes' slide carries Classes 1-3; Class 1 and 2 slides teach no later-class content; "
            "every stated step, hit, bar, role, stage, lane and layer count equals the drawing or the data; every drawing renders alone on a transparent ground with no ink at its edges; hero art used whole inside its viewBox; rendered-DOM "
            "footer gap on every page and deck slide, and clear space under text in dark boxes on pages and slides; no truncated slide bullets; edges of cover.png and previews clear; no audio, lyrics, melody notation, existing recordings, "
            "alcohol, religious wording, frequency numbers or student work; no source site named on a buyer page; grades 9-12; tags and subjects are not headings; no 'what changed' page (ORIGINAL).")


# ================================================================ UPLOAD.md (written by gen.py so every number matches the build)
def write_upload():
    np_, ns = len(PLAN), len(SLIDES)
    n_teacher = (PLAN.index("example2") + 1) - 1
    n_student = (PLAN.index("reflect") + 1) - (PLAN.index("timing") + 1) + 1
    assert 2 + n_teacher + n_student == np_, "page-count list must total the PDF"
    nt = len(LISTING_TITLE)
    desc = (f"{DESC_START} students remix one traditional winter song (the Welsh tune Deck the Halls, public domain) as a 128 BPM four-on-the-floor house track in Logic Pro. "
            f"They work out the timing with simple arithmetic, build a 4-bar pattern on a 16-step grid (kick on every beat, open hat and bass on the off-beat, clap on beats 2 and 4; use the Step Sequencer or Drum Machine Designer, if your version has them), "
            f"add a four-chord loop and the tune, set up sidechain compression so the bass, pad and tune duck when the kick hits, and arrange a 64-bar track with an intro, a build, a drop, a break, a second drop and an outro. "
            f"Math runs through every step: one beat at 128 BPM = 60 ÷ 128 = 0.46875 seconds = 468.75 ms, one 16th-note step = 15 ÷ 128 = 117.19 ms (0.1171875 s), one bar of 4/4 = 240 ÷ 128 = 1.875 seconds, 16 bars = 30 seconds and 64 bars = 120 seconds; "
            f"the release of the sidechain is timed to the beat, and the song's tempo change to 128 BPM is worked out as a ratio and a percent. "
            f"The gain-reduction curve and the ducking graph are drawn from stated example settings (a ratio of 4:1 and a threshold of -20 dB) and labeled as examples, not Logic defaults. "
            f"This House Remix takes {CLASSES} class periods (the pacing guide also shows two and four) and is an original Hudson Beat project; "
            f"the steps are written for Logic Pro, while the ideas (four on the floor, sidechain compression, chord loops, build and drop) carry over to GarageBand and other music software.\n\n"
            f"WHAT'S INCLUDED (ZIP: {np_}-page PDF = 1 cover + {n_teacher} teacher + {n_student} student + 1 terms page, plus {ns}-slide intro deck as .pptx and PDF)\n"
            f"• Teacher pages: how to use, project overview, setup, a {CLASSES}-class pacing guide with the deck slides for each class, "
            f"two pages of teacher notes (struggles, variations, resources, grading), a Logic quick reference and a two-page worked example (an invented remix at 128 BPM: "
            f"6 layers and their jobs, a 4-bar pattern of 90 hits, a chord loop, the sidechain numbers, timing at three tempos and a 64-bar arrangement of 6 layers = 120 seconds) ({n_teacher} pages)\n"
            f"• Student pages: a timing page (milliseconds per beat and per step and seconds per bar at six tempos, 16-bar and 64-bar lengths, and a length table at three tempos), a song page (facts, a tempo-change table, a key and meter note and a checklist for entering the tune), "
            f"a 4-bar step grid with the hits per bar and a blank grid, a chord page (I, IV, V and vi in three keys, the bass on the off-beats and a tune-against-chord check), a sidechain page (a gain-reduction curve, a ducking graph at 128 BPM and release times), "
            f"a layer table with a signal-chain drawing, an arrangement map with a blank table, a mix checklist, the 3-page project sheet (overview, goals, vocabulary, requirements, steps, tips, submission checklist), "
            f"the /{RUBRIC_TOTAL} rubric, a vocabulary page (four on the floor, sidechain, kick, off-beat, build, drop, breakdown, release), a feedback planner and a reflection page ({n_student} pages)\n"
            f"• Teacher-presented intro deck, {ns} slides with speaker notes on every slide: a think-and-share hook, what the project is, four on the floor, the timing math, the step grid, the song, bass and chords, the sidechain in three slides, "
            f"who ducks, the arrangement, the mix, what to turn in and the rubric\n\n"
            f"THE THREE CLASS PERIODS\n"
            f"• Class 1: hook; four on the floor; the timing math and a tempo of 128 BPM; prepare the song; build the 4-bar step grid\n"
            f"• Class 2: add the chord loop, the bass and the tune; set up the sidechain and time the release\n"
            f"• Class 3: arrange 64 bars, mix, bounce, present and reflect\n\n"
            f"WHAT STUDENTS LEARN\n"
            f"• Timing math: seconds per bar in 4/4 = 240 ÷ BPM; seconds per step = 15 ÷ BPM; 64 bars = 15360 ÷ BPM seconds; the ratio and percent change between two tempos\n"
            f"• Beats: a 16-step grid, hits per bar, the kick on every beat, the off-beat, claps on 2 and 4\n"
            f"• Harmony and bass: a I-IV-V-vi loop built by stacking thirds, bass roots between the kicks, checking the tune against the chords\n"
            f"• Mixing: sidechain compression (ratio, threshold, attack, release), headroom, and a build, a drop and a break\n\n"
            f"GOOD TO KNOW\n"
            f"• There is no audio in this resource, no lyrics, no melody notation and no student work. Students enter the public-domain tune from a score of their choice or by ear and make every other sound themselves\n"
            f"• Requires Logic Pro on a Mac; nobody has to read notation. Where a control may differ between versions, the pages say \"if your version has it\" and describe controls generically\n"
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
    md = f"""# UPLOAD: House Remix, original Logic Pro project (TpT 092)

These fields follow the order of TpT's "Add a resource" form. `tools/tpt.js publish` reads the title and description from the code blocks under 1 and 2, and everything else from `tpt.json`. This file is written by `gen.py`; edit the text there.

**Files to attach**
- Resource (digital download): `{SLUG}.zip`. It holds three files in a folder "{ZIP_DIR}":
  - `{SLUG}.pdf`: the teacher and student resource, {np_} pages, US Letter portrait.
  - `{SLUG}-intro-deck.pptx`: the teacher-presented intro deck, {ns} slides (16:9), speaker notes and a Class badge on every slide (the three-classes slide carries "Classes 1-3").
  - `{SLUG}-intro-deck.pdf`: a PDF copy of the deck, {ns} pages.
- Thumbnails, in this order: `cover.png`, `preview-1.png`, `preview-2.png`, `preview-3.png` (all 2000 × 2000).
- Preview file: `{SLUG}-PREVIEW.pdf`, 4 watermarked pages.

TpT takes one product file, so the PDF, the .pptx and the deck PDF go up together as the ZIP (`files.product` in tpt.json; `zip_contents` lists what is inside). **No audio, video, lyrics, melody notation, recordings, presets, screenshots, student work or Logic sessions are in the ZIP.**

**Page count, adding up to the PDF:** 1 cover + {n_teacher} teacher + {n_student} student + 1 terms page = {np_} pages; plus {ns} slides = {np_ + ns} for TpT's "Number of pages or slides".

## 1. Title

```
{LISTING_TITLE}
```
({nt} characters; the limit is 80.) The title leaves out Winter, Holiday, Christmas, Carol and the song's name because TpT's Seasonal Titles notice blocked a holiday-named title on 027 (see 080, 083, 087 and 090 for the working format); "House Remix", "Sidechain" and "Four on the Floor" are the plain search phrases. "Logic Pro" is in the first 30 characters as a compatibility word.

## 2. Description

```
{desc}
```

## 3. Grades

9th, 10th, 11th, 12th (`9th-grade`, `10th-grade`, `11th-grade`, `12th-grade` in tpt.json), as tpt/METADATA-GUIDE.md prescribes for every music-production item.

## 4. Subjects and tags

- Subjects in tpt.json: {"; ".join(SUBJECTS)} (all are in `tpt/SUBJECT-OPTIONS.json` and none is a heading)
- Tags in tpt.json: {", ".join(TAGS)} (four exact entries of `tpt/TAG-OPTIONS.json`, checked with `tools/tpt-validate.py`; the limit is 6). "Holiday" and "Student Practice" are headings and are not used; "Winter" is a real entry. "Christmas-Chanukah-Kwanzaa" is also a real entry but is left out because the kit is secular.
- Formats: PDF (add PowerPoint or ZIP if TpT offers it)
- Answer key: left out of tpt.json (there is none; the worked example is a model)

## 5. Resource type

- Projects
- Unit Plans
- PowerPoint Presentations

## 6. Standards (optional)

National Core Arts Standards, Music (Music Technology, high school): MU:Cr1.1, MU:Cr2.1, MU:Pr6.1, MU:Re7.2. Tag only if it matches how the teacher uses it.

## 7. Price

**${PRICE}** (paid), multiple-license price ${PRICE}. The price the queue set, at the low end of the $8-12 holiday Logic kit range, for a kit with {np_} pages + {ns} slides, a timing page, a song page, a 4-bar step grid with a blank grid, a chord page, two sidechain pages, a 64-bar arrangement map, a mix checklist and a two-page worked example, listed for winter.

## 8. Free or paid / free preview pages

Paid. Preview PDF (4 watermarked pages): the {CLASSES}-class pacing guide, the step grid, the sidechain page and the arrangement map. "Number of pages or slides" is {np_ + ns} ({np_} pages + {ns} slides).

## 9. Sources and credits

Fetched on 27 Nov 2026 (English Wikipedia, through its raw-text interface) unless a line says "could not". Each fact below says which source it came from; anything marked "not from any source" is an example value or a choice made for this kit.

- **Four on the floor.** English Wikipedia, "Four-on-the-floor (music)": "a steady, uniformly accented beat in 4/4 time in which the bass drum is hit on every beat (1, 2, 3, 4)"; used in dance genres such as disco and electronic dance music. The kit's definition follows this.
- **House music: tempo and the parts of the beat.** English Wikipedia, "House music": "a repetitive four-on-the-floor beat and a typical tempo of 115-130 beats per minute" (lead) and, in Characteristics, "repetitive 4/4 rhythms including bass drums, off-beat hi-hats, snare drums, claps, and/or snaps at a tempo of between 120 and 130 beats per minute"; "the bass drum is usually played on beats one, two, three, and four, and the snare drum, claps, or other higher-pitched percussion on beats two and four". The kit's kick on every beat, off-beat open hat and clap on beats 2 and 4, and the statement that 128 BPM lies inside both ranges, come from this article. The model pattern's closed hat on the even steps, the bass on the off-beats and the bar-4 clap fill are choices for this kit, not from any source.
- **Sidechain compression.** English Wikipedia, "Dynamic range compression": "A compressor with a side-chain input controls gain from main input to output based on the level of the signal at the side-chain input"; "In electronic dance music, side-chaining is often used on basslines, controlled by the kick drum or a similar percussive trigger, to prevent the two from conflicting, and provide a pulsating, rhythmic dynamic to the sound"; "a ratio of 4:1 means that if input level is 4 dB over the threshold, the output signal level is reduced to 1 dB over the threshold. The gain and output level has been reduced by 3 dB"; attack is when the compressor is decreasing gain and release when it is increasing gain; "There is no industry standard for the exact meaning of these time parameters". The gain-reduction formula (level - threshold) x (1 - 1 / ratio) follows from the 4:1 example, and the example threshold of -20 dB, the 0 to 15 dB table, the release of one beat and the fast attack are **starting points chosen for this kit, not from any source** and are labeled as such on the pages. The ducking graph is a schematic (straight-line recovery).
- **Ducking.** English Wikipedia, "Ducking": "one track is made quieter (the ducked track) whenever another (the ducking track) gets louder"; the bass timbre ducked under the kick drum is the dance-music use. The kit's word "duck" follows this.
- **Build, drop and break.** English Wikipedia, "Drop (music)": a drop is "a point in a music track where a sudden change of rhythm or bass line occurs, which is preceded by a build-up section and break", and "the loudest portion of an EDM song". The kit's definitions of build, drop and breakdown follow this and say what each means in the kit; the word "breakdown" means different things in different genres (English Wikipedia, "Breakdown (music)"), so the kit says what it means here. The section lengths of the 64-bar model (8, 8, 16, 8, 16, 8) are **not from any source**.
- **Meter, tempo and hi-hats.** English Wikipedia, "Time signature": the upper numeral "indicates how many such note values constitute a bar" and the lower numeral the note value being counted, so 4/4 is four quarter-note beats per bar. English Wikipedia, "Tempo": tempo is measured in beats per minute, and in electronic dance music it is typically simply stated in BPM. English Wikipedia, "Hi-hat": a hi-hat is a pair of cymbals that can be played open or closed. One beat = 60 / BPM s is the definition of beats per minute; the 16th-note step = 15 / BPM s (four steps to a beat), the bar = 240 / BPM s = 16 steps, 128 BPM: 468.75 ms per beat, 117.1875 ms (printed 117.19) per step, 1.875 s per bar, 30 s for 16 bars and 120 s for 64 bars, and every table are arithmetic computed in `gen.py --check` exactly with fractions and with an independent decimal method.
- **The song.** English Wikipedia, "Deck the Halls": "The melody is Welsh, dating back to the sixteenth century, and belongs to a winter carol, 'Nos Galan'"; the melody was published by Edward Jones in Musical and Poetical Relicks of the Welsh Bards (English Wikipedia dates the first known publication of "Nos Galan" to 1794; IMSLP's page for the tune gives 1784 and other sources cite both editions, so the kit says only "in print by the 1790s" and was corrected from "published in 1794" at QA on 27 Nov 2026); the English words are dated 1862. The melody is therefore far older than the 1930 cutoff and in the public domain. The kit prints no words (the 1862 words are not used). The kit calls it "a traditional winter song". **Key and meter:** the kit uses F major and 4/4 as working choices for its examples and says so; it does **not** claim them as facts from a source. Kit 076 (QA.md, 23 Nov 2026) recorded F major and 4/4 for this tune in CPDL editions no. 47663 and no. 502, but I **could not** re-fetch CPDL today (every request, page or file, returned HTTP 403 from Cloudflare's challenge page), so that is only a pointer. The "usual tempo" of the song: **no tempo source was fetched**, so the kit's tempo-change table uses four plain tempos (90, 100, 110, 120 BPM) as examples chosen for this kit and tells students to use their own version's tempo.
- **No melody chart (honest note).** The brief allowed a note chart only if checked note by note against two independent sources fetched by the builder. I tried CPDL (HTTP 403), Wikimedia Commons' MIDI file and image of the melody (HTTP 429, upload host refused this machine), Mutopia (no Deck the Halls in its catalog), IMSLP (page not found) and abcnotation.com / folktunefinder.com (a bot challenge or HTTP 503). **No melody chart is included**: students enter the tune from a public-domain score of their choice or by ear. The chord page therefore has a blank check (first tune note of each bar against the bar's chord) instead of a chord-versus-melody table verified in code. The chord table itself (I, IV, V and vi built by stacking thirds in C, F and G major) is computed and checked in `gen.py --check`.
- **Logic Pro.** Apple's Logic Pro User Guide page on side chains was fetched (support.apple.com) but returned only its table of contents, so **could not** read how Logic words the Side Chain menu, the Compressor controls, Drum Machine Designer, the Step Sequencer, Retro Synth, Alchemy or the Marker track. The kit therefore names the tools, says "if your version has it", and invents no menu paths or key commands, except File › Bounce › Project or Section (Command-B), the Mixer key command (X) and "Compress in Finder", carried over from kits 083, 087 and 090 (those kits confirmed the Bounce path and Command-B on Apple Support search results; I did not re-fetch them).
- **Level: 0 dBFS and headroom.** English Wikipedia, "DBFS" (read for kit 090, 27 Nov 2026; not re-fetched): "The level of 0 dBFS is assigned to the maximum possible digital level". The kit says "keep the master peak below 0 dBFS with room to spare" and prints no target peak level, because no source for a target was fetched.
- **Example values (not from any source).** The pattern's steps and hits, the pitch and length descriptors (low, mid, high, short, medium, long: listening guides, not measurements), the chord loop's order and the loop's use of F major, the arrangement's layers and bars, the invented example remix and every invented time are example values chosen for this kit and labeled as examples.
- **No recordings, no brands.** No recordings, remixes, artists or albums are named. The kit uses no film, game or pop-music reference.
- **Art:** the cover, previews and deck use a piece from the art library (`art/hero.png`: a pair of studio monitor speakers, no text), copied whole and unchanged from `tpt/_art/library/studio-monitors.png`; logged in `tpt/_art/USAGE.md`. There is no pre-made art for this item in `tpt/_art/next`. Everything else, including every number, table, icon, step grid, chord table, gain curve, ducking graph, layer table, signal chain and arrangement map, is drawn or printed in code.
- **Fonts:** Oswald and Source Sans 3 (SIL OFL 1.1). Logic Pro is named only to describe compatibility.

## 10. Before you click publish

- [ ] **Needs QA approval first.** This is a new kit (not yet on TpT); the Manager releases it only after a QA `**Verdict: APPROVED**`. Season rule: listing no sooner than the 2-8 week window before winter allows.
- [ ] Cover and previews show "HUDSON BEAT" in type; PDF footers read "© 2026 Brian Lotze · Hudson Beat · For single-classroom use".
- [ ] No school name, logo, student names or work, audio, video, lyrics, recording name or Logic session anywhere (`gen.py --check` scans every output and every file in this folder).
- [ ] **Secular and inclusive.** The song is described as a traditional winter song; no religious content, no alcohol imagery, no brands other than Logic Pro, no lyrics. `gen.py --check` fails on alcohol, religious and shopping words and on lines of the song's words.
- [ ] **Timing numbers (all recomputed in `gen.py --check`, exactly with fractions, with an independent decimal method and against hand-typed expectations).** Seconds per beat = 60 / BPM; per 16th-note step = 15 / BPM; per bar of 4/4 = 240 / BPM = 4 beats = 16 steps; 16 bars = 3840 / BPM; 64 bars = 15360 / BPM. At 128 BPM: 468.75 ms per beat, 117.1875 ms per step (117.19 rounded half up), 234.375 ms per eighth note, 1.875 s per bar, 7.5 s per 4-bar loop, 30 s per 16 bars, 60 s per 32 bars, 120 s per 64 bars. Lengths of 8 / 16 / 32 / 64 bars: 15 / 30 / 60 / 120 s at 128 BPM, 16 / 32 / 64 / 128 s at 120 BPM and 15.484 / 30.968 / 61.935 / 123.871 s at 124 BPM. Rounding: milliseconds per beat and step to 2 decimals, seconds to 3, half up. Section starts at 128 BPM: 0, 15, 30, 60, 75, 105 s; the arrangement ends at 120 s. Tempo change from a plain tempo T to 128 BPM: ratio 128 / T and percent (128 - T) / T x 100: 1.4222 and 42.22% at 90, 1.28 and 28% at 100, 1.1636 and 16.36% at 110, 1.0667 and 6.67% at 120.
- [ ] **Sidechain numbers.** Gain reduction (level - (-20)) x 3/4 dB for a kick at -20, -16, -12, -8, -4 and 0 dB = 0, 3, 6, 9, 12 and 15 dB (4 dB over at 4:1 is 3 dB down, as in the source's example); the example release is one beat = 4 steps = 468.75 ms (1, 2 and 3 steps = 117.1875, 234.375 and 351.5625 ms); the four kicks of a bar fall at 0, 468.75, 937.5 and 1406.25 ms. The gain-curve drawing plots those six points and one line; the ducking drawing shows 4 kicks and 4 dips.
- [ ] **Pattern and arrangement numbers (recomputed from the data and from the drawings).** 5 lanes (kick, clap, closed hat, open hat, bass); 4 bars of 16 steps = 64 steps; hits per bar 22, 22, 22, 24 = 90; hits per lane 16, 10, 32, 16, 16 = 90; kick on grid steps 1, 5, 9, 13 (4 a bar); open hat and bass on 3, 7, 11, 15 (the kick and the bass never share a step); clap on 5 and 13 (beats 2 and 4) plus a fill on 15 and 16 in bar 4; bar 2 grid step 5 = (16 + 4) x 15 / 128 = 2.34375 s. Arrangement: 64 bars, 6 sections (8, 8, 16, 8, 16, 8 bars), 6 layers; bars per layer 48, 40, 48, 32, 64, 40 = 272; layers sounding per bar 2 (bars 1-4), 3 (5-16), 6 (17-32), 2 (33-40), 6 (41-56), 3 (57-60), 2 (61-64) = 272. Layer table drawing: 6 rows, 6 icons, 6 role chips, 6 side-chain chips (1 trigger, 3 ducked, 2 not ducked), 36 dots; signal chain: 5 stages, 4 arrows.
- [ ] **Original project.** Built with `ORIGINAL = True` in `tpt/_dmp2_common/dmp2.py` (like 031, 036, 053, 057, 061, 063, 067, 070, 076, 080, 083, 087 and 090): no "what changed" page and the new disclosure line. The reflection page is the shared Reflection element, scored in the rubric's "Plan & Reflection" row. `dmp2.py` is unchanged; the deck's three-classes badge and the terms-page thank-you note are applied inside `gen.py`.
- [ ] **Logic Pro names to confirm on a Mac with a current Logic.** Drum Machine Designer (hedged), the Step Sequencer (hedged), Retro Synth and Alchemy (hedged), the Compressor's Side Chain menu (hedged), the gain-reduction meter, the Piano Roll's 16th-note grid, a transpose option on the region (hedged), the Marker track (hedged), the Mixer (X), Bounce (Command-B) and Compress in Finder.
- [ ] **Open questions for the owner:** (1) **No melody chart.** The tune could not be checked against two fetched sources, so students enter it from a public-domain score or by ear; if you want a chart, a builder with CPDL access can reuse the verified Deck the Halls chart from 076. (2) **Song tempo.** No source for the song's usual tempo was fetched; the tempo-change table uses four example tempos. (3) **Key and meter.** F major and 4/4 are stated as working choices, not as facts from a source. (4) **Title.** No Winter, Holiday, Christmas, Carol or song name in the title because of TpT's seasonal-title notice (see 1); the brief's longer example title was 83 characters, so this one drops "Project". (5) **Price.** $8.00, as queued. (6) **Art.** There is no pre-made art for this item; the studio-monitors library piece fits the low kick and bass. (7) **Logic details.** Apple's pages for the Side Chain menu and the Compressor could not be read, so the kit stays generic; say if you want a Mac check before release. (8) **Classes.** Three periods; Class 2 holds the chords, the tune and the sidechain, so the pacing page shows how to use two or four.
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
