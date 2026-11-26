#!/usr/bin/env python3
"""Logic Pro project kit: Bell Ostinato Lab (TpT 087): the teacher resource, the intro deck and the listing files.

    python3 gen.py            build everything into this folder (also writes UPLOAD.md)
    python3 gen.py --lowres   same, but square images at scale 1 and small page shots (self-check only; --check rejects it)
    python3 gen.py --check    verify content and layout: the motif (G minor, 3/4, Bb4 A4 Bb4 G4 as quarter, eighth, eighth, quarter = 3 beats, read from two public scores), its note numbers and
                              frequencies in two keys (original and 3 semitones lower: G4 F#4 G4 E4; every note is exactly 3 semitones lower), the interval table (-1, +1, -3; the intervals add up to
                              the last note minus the first; the motif spans a minor third), the tempo math for 3/4 (one beat = 60 / BPM s, one eighth note = 30 / BPM s, one bar = 180 / BPM s; 4 bars = 720 / BPM,
                              16 bars = 2880 / BPM; exact fractions and an independent float method), the layer map (5 layers, 16 bars, 4 sections, which bars each layer plays, layers sounding per bar, the drawing
                              counted again), the dynamics ramp (automation points at bars 1, 5, 9, 13 and 17, level at the start of every bar, never falling, crescendo 80 to 112 in bars 13 to 16),
                              octave layers (+12 doubles the frequency), Step N references on every page, slide and UPLOAD.md, class badges against the pacing page, count-vs-drawing (layers, bars, notes),
                              drawings (each rendered alone on a transparent ground: no ink within 4 px of its edge), the hero art, files, page and slide counts, class slots, fonts, fit and overlap, dead
                              space, footer gap (pages and deck slides), black-box padding (pages and deck slides), the edges of cover.png and the previews, banned strings, tpt.json and UPLOAD.md

An ORIGINAL Hudson Beat project (dmp2.ORIGINAL = True, like 063, 067, 070, 076, 080 and 083). Students build a short piece from a four-note ostinato: the motif of Mykola Leontovych's Ukrainian choral
piece Shchedryk (first performed in 1916). Only the four-note motif is used (public domain); the English words and the 1936 choral arrangement are a separate, copyrighted work and are NOT used. Students
enter the motif in Logic Pro, repeat it as an ostinato in 3/4, layer it at several octaves and instruments over a 16-bar form, answer it in a second key, and shape it with dynamics and volume automation.
No audio ships and no lyrics are printed. The art on the cover, the previews and the deck is the owner's pre-made hero (art/hero.png), used whole. Everything else is drawn in code. The shared builder is
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
SLUG = "bell-ostinato-lab"
TITLE = "Bell Ostinato Lab"
ACCENT = "#2F7FB8"          # this product's single accent: icy blue (a shade deeper than the art's #4FA3D9, so small labels read)
ACC_LIGHT = "#DCEBF6"
PRICE = "8.00"
CLASSES = 3
GRADES_TEXT = "9–12"
GRADE_SLUGS = ["9th-grade", "10th-grade", "11th-grade", "12th-grade"]
TAGS = ["Winter", "Project-based Learning", "Projects", "Activities"]     # exact entries of tpt/TAG-OPTIONS.json, none a heading
SUBJECTS = ["Music", "Music Composition", "Computer Science - Technology"]     # all in SUBJECT-OPTIONS.json, none a heading
ANSWER_KEY = None
LISTING_TITLE = "Logic Pro Ostinato Project | Layering, Dynamics, Automation | High School"
DESC_START = "Ostinato project for high school music technology:"
DESC_MUST = ["Bell Ostinato Lab", "Shchedryk", "3/4", "180 ÷ BPM", "90 BPM", "no audio", "automation", "crescendo", "Bb4"]
ZIP_DIR = "Bell Ostinato Lab - Hudson Beat"
ZIP_DATE = (2026, 11, 26, 12, 0, 0)
TYPE = "Original Project"
PROJ_LINE = "Music Technology | <i>Bell Ostinato Lab</i> | 3 class periods"
DECK_STRAP = "Four notes, five layers, one build"
REFLECT_ROW = "Plan &amp; Reflection"
# split so this file never contains them (the --check scan reads every file in this folder)
BANNED_EXTRA = ["Rud" + "olph", "Fro" + "sty", "Gri" + "nch", "Santa Claus " + "Is", "Jingle Bell " + "Rock", "Feliz " + "Navidad",
                "Mari" + "ah Carey", "Spoti" + "fy", "You" + "Tube", "Home " + "Alone", "Nin" + "tendo", "Ro" + "land",
                "Star " + "Wars", "Hans " + "Zimmer", "John " + "Williams", "Harry " + "Potter", "Pix" + "ar", "Lord of the " + "Rings",
                "Winter " + "Wonderland", "Let It " + "Snow", "Sleigh " + "Ride", "X" + "mas", "Times " + "Square", "Auld " + "Lang",
                "Ak" + "ai", "Ab" + "leton", "FL " + "Studio", "Sound" + "Cloud", "Tik" + "Tok", "Spl" + "ice", "Ser" + "um",
                "Trans-" + "Siberian", "Mannheim " + "Steamroller", "Pentato" + "nix"]

# ================================================================ page plan (teacher pages 2-10, student pages 11-24)
PLAN = ["cover", "howto", "overview", "setup", "pacing", "tn1", "tn2", "logicref", "example", "example2", "timing", "motif", "enter", "layers", "answer",
        "dynamics", "mix", "proj1", "proj2", "proj3", "rubric", "vocab", "present", "reflect", "terms"]


def pg(k):
    return PLAN.index(k) + 1


# ================================================================ the arithmetic (exact fractions; all verified in --check)
TEMPOS = (72, 80, 90, 100, 120, 144)        # the timing table's rows
EX_BPM = 90                                 # the worked example's tempo
LEN_TEMPOS = (72, 90, 120)                  # the form-length table's three tempos
LEN_BARS = (8, 12, 16, 32)
BEATS_BAR = 3                               # 3/4: three quarter-note beats
EIGHTHS_BAR = 6                             # six eighth notes in a bar of 3/4
SEC_BARS = 4                                # one section = 4 bars
ARR_BARS = 16                               # the form


def spb(bpm):
    """Seconds per quarter-note beat = 60 / BPM."""
    return Fraction(60, bpm)


def eighth_len(bpm):
    """Seconds per eighth note = 30 / BPM."""
    return Fraction(30, bpm)


def bar_len(bpm):
    """Seconds per bar of 3/4 = 180 / BPM (three beats)."""
    return Fraction(180, bpm)


def start_s(bpm, bar):
    """Seconds from the start of the piece to the first beat of bar `bar` = (bar - 1) x 180 / BPM."""
    return (bar - 1) * bar_len(bpm)


def rnd(x, nd):
    """Round half up (a 5 rounds up) to nd decimals, on exact fractions."""
    s = Fraction(10) ** nd
    return Fraction(math.floor(Fraction(x) * s + Fraction(1, 2)), 1) / s


def dec(x, nd):
    return f"{float(rnd(x, nd)):.{nd}f}".replace("-", "−")


def exact(x):
    """An exact decimal (the denominator has only the factors 2 and 5), with no trailing zeros: 9/4 -> 2.25."""
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


# ---- pitch: MIDI note numbers (middle C = 60 = C4, A4 = 69 = 440 Hz), frequency = 440 x 2^((m - 69) / 12)
SHIFT = -3                                  # the second key: 3 semitones lower (G minor to E minor)
# the motif: (note name, MIDI number, start in eighth-note slots from the start of the bar, length in eighth-note slots)
MOTIF = [("Bb4", 70, 0, 2), ("A4", 69, 2, 1), ("Bb4", 70, 3, 1), ("G4", 67, 4, 2)]
MOTIF_E = [("G4", 67, 0, 2), ("F#4", 66, 2, 1), ("G4", 67, 3, 1), ("E4", 64, 4, 2)]
START_BEAT = ["1", "2", "2 &", "3"]         # where each note starts in the bar (the & is the off-beat eighth)
LEN_BEATS = [Fraction(1), Fraction(1, 2), Fraction(1, 2), Fraction(1)]
IVL_NAME = {1: "minor second", 2: "major second", 3: "minor third", 4: "major third", 5: "perfect fourth", 7: "perfect fifth", 12: "octave"}
ROW_NAMES = {64: "E4", 65: "F4", 66: "F#4", 67: "G4", 68: "G#4", 69: "A4", 70: "Bb4"}
LOW, HIGH = 64, 70                          # rows of the piano-roll drawing


def freq(m):
    return 440 * 2 ** ((m - 69) / 12)


def hz1(m):
    return f"{math.floor(freq(m) * 10 + 0.5) / 10:.1f}"


def sgn(n):
    return "0" if n == 0 else (f"+{n}" if n > 0 else f"−{-n}")


def midi_name(m):
    """Note name with octave number (middle C = C4); flats for the black keys the kit uses."""
    names = ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"]
    return f"{names[m % 12]}{m // 12 - 1}"


def intervals(notes):
    """Semitone moves between neighboring notes of a motif."""
    return [b[1] - a[1] for a, b in zip(notes, notes[1:])]


# ---- the layer map: 16 bars, five layers, the bars each plays (inclusive spans)
ARR_ROWS = [("BELL", [(1, 9), (11, 11), (13, 16)]), ("CELESTA", [(5, 8), (13, 16)]), ("PAD", [(5, 16)]), ("LOW BELL", [(13, 16)]), ("ANSWER", [(10, 10), (12, 12)])]
ARR_SECTIONS = [("SOLO", 1, 4), ("BUILD", 5, 8), ("ANSWER", 9, 12), ("FINALE", 13, 16)]
ARR_LAYERS = [r for r, _ in ARR_ROWS]
SHIFT_OF = {"BELL": 0, "CELESTA": 12, "PAD": None, "LOW BELL": -12, "ANSWER": SHIFT}      # octave or key shift of each layer (the pad holds one note)
ROLE_OF = {"BELL": "The ostinato: the motif in G minor, every bar it plays",
           "CELESTA": "The same motif one octave higher, for sparkle",
           "PAD": "One long note per bar: G (MIDI 55), 3 beats, under everything",
           "LOW BELL": "The same motif one octave lower, for weight in the finale",
           "ANSWER": "The motif in E minor, 3 semitones lower, replying in the bell's rests"}
PAD_MIDI = 55                                # G3, held for the whole bar


def spans_text(spans):
    return ", ".join(f"{a}–{b}" if a != b else str(a) for a, b in spans)


def bars_of(nm):
    return [b for r, spans in ARR_ROWS if r == nm for a, c in spans for b in range(a, c + 1)]


def layers_in_bar(b):
    return [r for r, _ in ARR_ROWS if b in bars_of(r)]


# ---- the dynamics ramp: volume automation points (bar position, level 0-127); position 17 is the end of bar 16
DYN = [("pp", "very quiet", 32), ("p", "quiet", 48), ("mp", "moderately quiet", 64), ("mf", "moderately loud", 80), ("f", "loud", 96), ("ff", "very loud", 112)]
LEVEL_OF = {n: v for n, _, v in DYN}
POINTS = [(1, 32), (5, 32), (9, 64), (13, 80), (17, 112)]


def level_at(pos):
    """The automation line's level at bar position pos (1 = the start of bar 1, 17 = the end of bar 16): straight lines between the points."""
    for (x0, y0), (x1, y1) in zip(POINTS, POINTS[1:]):
        if x0 <= pos <= x1:
            return y0 + Fraction(y1 - y0, x1 - x0) * (pos - x0)
    raise ValueError(pos)


def mark_of(level):
    for n, _, v in DYN:
        if v == level:
            return n
    return ""


# ================================================================ the project text (original; students read these pages)
BB_NOTE = "Bb means B-flat and F# means F-sharp. The letters are written this way throughout the kit."
THEME = ("An ostinato is a short pattern that repeats, and bells are a good sound for it. This project starts from the four-note motif of the Ukrainian choral piece Shchedryk, which Mykola Leontovych (1877–1921) "
         "wrote and revised over several years and which was first performed in December 1916. In English-speaking countries the tune is known as “Carol of the Bells”. Only the four-note motif is used. "
         "There are no words, and students build their own original layers, answers and dynamics around it.")
BUILD_NOTE = ("The skills here carry over to every loop-based piece: enter a pattern exactly, repeat it, layer it in different registers and sounds, let a second voice answer it, "
              "and shape the whole thing with dynamics and automation. The math is the same too: beats, bars, seconds and semitones.")
OVERVIEW = ("Build a short piece in Logic Pro from one four-note motif. Students enter the motif in the Piano Roll (Bb4, A4, Bb4, G4: quarter, eighth, eighth, quarter, one bar of 3/4), "
            "repeat it as an ostinato, and layer it at different octaves and with different bell, celesta and pad sounds over a 16-bar form. They write an answer in a second key, "
            "E minor, 3 semitones lower, and shape the piece from pp to ff with volume automation. Tempo math drives every choice, and nobody has to read notation.")
GOALS = ["Plan a 16-bar form in 3/4 with tempo math: one bar = 180 ÷ BPM seconds (2 seconds at 90 BPM), so 16 bars last 32 seconds at 90 BPM",
         "Enter the four-note motif exactly (Bb4, A4, Bb4, G4) and name its intervals: −1, +1 and −3 semitones",
         "Layer the ostinato at several octaves and sounds, and write a call-and-response answer in E minor, 3 semitones lower",
         "Shape the piece from pp to ff with a volume automation line (if your version has it) and mix the layers so each can be heard"]
VOCAB = [("Ostinato", "A short musical pattern that repeats again and again, usually in the same voice and at the same pitch"),
         ("Motif", "A short musical idea that is easy to recognize; here it is four notes long"),
         ("Layer", "One part of the piece on its own track, with its own sound, register and bars"),
         ("Octave", "The distance of 12 semitones; a note one octave higher has twice the frequency"),
         ("Dynamics", "How loud or soft the music is, from pp (very quiet) to ff (very loud)"),
         ("Crescendo", "A gradual increase in loudness; automation can draw one as a rising line"),
         ("Automation", "Level or other settings that change over time, drawn as a line of points on a track"),
         ("Call and response", "A short phrase answered by a second phrase, like a conversation in music")]
REQS = ["Choose a tempo and fill in the timing page: one bar of 3/4 = 180 ÷ BPM seconds (page @TIMING)",
        "Learn the motif from the note chart and fill in its intervals in both keys (page @MOTIF)",
        "Enter the motif in the Piano Roll and repeat it as an ostinato in 3/4 (page @ENTER)",
        "Layer it over 16 bars with 5 layers and draw your layer map (page @LAYERS)",
        "Write an answer in a second key and place it in the bell’s rests (page @ANSWER)",
        "Draw a volume automation line from pp to ff, mix with the checklist and bounce (pages @DYNAMICS and @MIX)",
        "Present your piece and reflect on your choices (pages @PRESENT and @REFLECT)"]
FILE_NAME = "“Your Name – Bells”"
STEP_NAMES = ["Plan the form", "Learn the motif", "Build the ostinato", "Layer it", "Answer it", "Shape the sound", "Present &amp; get feedback"]
STEPS = ["<b>Plan the form</b> — Use the timing page (page @TIMING) to pick a tempo and work out how long one bar and the 16-bar form last",
         "<b>Learn the motif</b> — Read the note chart (page @MOTIF): four notes, three different pitches, one bar of 3/4. Fill in the intervals for the original key and for the second key",
         "<b>Build the ostinato</b> — Enter the motif in the Piano Roll with a bell sound and repeat it for 4 bars (page @ENTER; quick reference: page @LOGICREF)",
         "<b>Layer it</b> — Add a celesta, a pad and a low bell at other octaves and draw your 5-layer map over 16 bars (page @LAYERS)",
         "<b>Answer it</b> — Write an answer in a second key, 3 semitones lower, and place it where the bell rests (page @ANSWER)",
         "<b>Shape the sound</b> — Draw a volume automation line from pp to ff with a crescendo at the end (page @DYNAMICS), then mix with the checklist and bounce (page @MIX)",
         "<b>Present &amp; get feedback</b> — Write three questions you want classmates to answer about your piece. Play it, point out the layers, the answer and the crescendo as they arrive, "
         "and answer at least 2 of each classmate’s questions. Then reflect (page @REFLECT)."]
TIPS = ["Enter the motif once, check it note by note against the chart, and only then copy it. A wrong note repeated 16 times is 16 wrong notes.",
        "Keep the ostinato steady and let the layers change around it. The listener hears the pattern most clearly when it does not move.",
        "Add one layer at a time and listen after each. If you cannot hear a layer, make another one quieter instead of making it louder.",
        "Save a new version of your project at the end of each class, so you can always go back."]
CHECK = ["Bounced .mp3 or .wav of your piece, 16 bars long",
         "Zipped .logicx project file handed in",
         f"Files named correctly: {FILE_NAME}",
         "Timing page, note chart and layer map handed in",
         "Rubric self-score done (page @RUBRIC)",
         "I can say my tempo, how long my piece lasts, and which layer joins in which bar"]
RUBRIC_NOTE = "Each category is scored 1–5. Score yourself first; the final grade is the average of your score and your teacher’s."
LEVELS = [1, 2, 3, 4, 5]
RUBRIC = [
    ("Motif & Ostinato", ["No motif entered", "Notes or lengths wrong, and it does not repeat", "Motif mostly correct, but the repeat has gaps or slips",
                          "Motif correct in pitch and length, repeating cleanly in 3/4, with the intervals filled in", "Correct motif in two keys, steady repeat and a complete interval table"]),
    ("Layers & Form", ["No layers added", "One extra layer, with no plan", "Layers added, but the sections are unclear",
                       "A 16-bar form with layers that match the layer map, at more than one octave or sound", "A clear build, with octave and sound choices that are deliberate and explained"]),
    ("Dynamics & Automation", ["No dynamics", "Level changes by hand only", "One automation line, but no clear build",
                               "A volume line that builds from pp to ff with a crescendo at the end (if your version has automation)", "A shaped line that matches the plan, with a smooth crescendo"]),
    ("Answer & Mix", ["No answer layer", "An answer that is out of time or key", "An answer in the right key, but the mix is crowded",
                      "An answer in E minor placed in the bell’s rests, a clear mix and no clipping", "Call and response that is easy to hear, with every layer clear in the mix"]),
    ("Plan & Reflection", ["Plans, presentation or reflection missing", "Thin plan; little to say about choices", "Plan and reflection complete, with basic detail",
                           "Correct timing math and layer map; thoughtful reflection", "Insightful reflection and a polished presentation"]),
]
RUBRIC_TOTAL = 25
RUBRIC_SHORT = ["A correct motif in two keys that repeats steadily",
                "A clear build with deliberate octave and sound choices",
                "A shaped automation line with a smooth crescendo",
                "An answer that is easy to hear in a clear mix",
                "Insightful reflection and a polished presentation"]
RUBRIC_SLIDE_LINE = "Scored 1–5 · final grade = average of your score and mine, out of 25"
RUBRIC_ROW_PITCH = 0.86
RUBRIC_LINE_Y = 6.3

TN_REINFORCES = ("Teaches how a loop-based piece is built from one short pattern. Students enter a motif exactly, name its intervals, repeat it as an ostinato in 3/4, layer it at several octaves and sounds, "
                 "answer it in a second key and shape the result with dynamics and volume automation, all in Logic Pro.")
STRUGGLES = ["The motif sounds wrong: compare each note with the note chart note by note, and check the octave and the lengths (page @MOTIF). Software may label octaves differently, so compare the note letters and the distance in semitones.",
             "The repeat has a gap or a hiccup: check that the region is exactly one bar of 3/4 long, and that the last note ends on the barline (page @ENTER).",
             "The layers fight each other: take layers away until the motif is clear, then bring them back one at a time, and make the quiet ones quieter (page @LAYERS).",
             "The crescendo jumps instead of growing: check that the automation points are joined by straight lines, and that each point is higher than the one before it (page @DYNAMICS)."]
VAR_EASY = ("Keep the tempo at 90 BPM, where a bar lasts exactly 2 seconds and 16 bars last 32 seconds (page " + str(pg("timing")) + "); use only the original key, enter the motif once and loop it, "
            "and build only the bell, the celesta and the pad.")
VAR_HARD = ("Write an original answer phrase of your own in the bell’s rests, not only the motif in a second key, or build a 32-bar form with a second round of call and response "
            "(page " + str(pg("layers")) + ").")
RESOURCES = [("Timing page (page @TIMING)",
              "Seconds per beat, eighth note and bar of 3/4 at six tempos, the length of a section and of the form, and form lengths at three tempos."),
             ("Note chart (page @MOTIF)",
              "The motif on a piano-roll drawing in two keys, with note numbers, frequencies, lengths and an interval table."),
             ("Enter and test the ostinato (page @ENTER)",
              "A setup checklist, an entry log and a check that the repeat is clean."),
             ("Layer map and answer (pages @LAYERS and @ANSWER)",
              "A 5-layer, 16-bar layer map with a blank to fill in, octave shifts, and a call-and-response page in a second key."),
             ("Dynamics, mix and worked example (pages @DYNAMICS, @MIX and @EXAMPLE–@EXAMPLE2)",
              "A dynamics ramp from pp to ff with automation points, a mix checklist, and an invented piece at 90 BPM. A model, not a template.")]
TN_NOTE = ("A good listening day: play each piece and ask the class two questions. Which layer joined last? Where did you first hear the answer? "
           "If a layer is hard to hear, find it on the layer map together. This kit includes no recordings and prints no words.")
GRADING = ["The rubric: five categories, each scored 1–5, /25 (page @RUBRIC). Students score themselves first; the final grade is the "
           "average of their score and yours.",
           "Motif & Ostinato (rubric row 1): check the entry log and the intervals against the note chart, and listen for a clean repeat (pages @MOTIF and @ENTER).",
           "Layers & Form (rubric row 2): compare the student’s layer map with what plays, bar by bar (page @LAYERS).",
           "Dynamics & Automation (rubric row 3): ask the student to show the automation line and read the level at bars 1, 9, 13 and 16 (page @DYNAMICS).",
           "Answer & Mix (rubric row 4): play bars 9 to 12 and find the call and the answer; then check the mix checklist (pages @ANSWER and @MIX).",
           "Plan & Reflection (rubric row 5): the timing page, the feedback questions and the Reflection page (page @REFLECT) are the evidence."]
PACING = [
    {"n": 1, "owner": "Hear the idea, plan the timing, learn the motif and enter it as an ostinato.",
     "do": "Slides 1–8: the think-and-share, the project, the three classes, the motif, the timing math, entering the motif and the ostinato check. Hand out the timing, note chart and entry pages.",
     "slides": (1, 8), "pages": ["timing", "motif", "enter", "proj1", "proj2", "proj3", "vocab"],
     "deck": "Hear the bells · one bar = 180 ÷ BPM · the motif · enter it"},
    {"n": 2, "owner": "Layer the ostinato over 16 bars and write an answer in a second key.",
     "do": "Slides 9–11: the layer map, call and response and layering at other octaves. Demonstrate copying a region to a new track and moving it 12 semitones, then the answer 3 lower. "
           "Walk the room with one question: which layer is this, and which bars does it play?",
     "slides": (9, 11), "pages": ["layers", "answer", "present"], "deck": "Layer it · call and response · octaves"},
    {"n": 3, "owner": "Shape the piece with dynamics and automation, mix, bounce, present and reflect.",
     "do": "Slides 12–17: the dynamics ramp, drawing volume automation, what to turn in, the rubric, presentation day and the wrap-up. Students mix, bounce and present.",
     "slides": (12, 17), "pages": ["dynamics", "mix", "rubric", "present", "reflect"], "deck": "Dynamics ramp · automation · checklist · presentations"},
]
PACING_EXTRA = (
    '<div class="cols" style="margin-top:4pt;gap:14pt"><div class="box acc-b"><span class="k">The one thing to do on Class 1</span>'
    '<p style="margin:0;font-size:10.6pt">Make sure every student leaves with a tempo and a one-bar motif that has been checked note by note against the note chart and repeats for 4 bars without a gap, so that '
    'Class 2 is all layers and the answer.</p></div>'
    '<div class="box"><span class="k">With two or four periods</span><p style="margin:0;font-size:10.6pt"><b>Two classes:</b> Class 1 is the plan, the motif, the ostinato and the first layers; '
    'Class 2 is the answer, the automation, the mix and short presentations. <b>Four classes:</b> keep Classes 1 and 2, then spend Class 3 on the automation and the mix, and '
    'Class 4 on presentations and reflection.</p></div></div>')
PACING_SIZE = 10.6
TN2_SIZE = 9.9

SONG_NOTE = ("No audio, recordings or words are included. The only existing music is the four-note motif, which students enter themselves. Students make every "
             "sound themselves, from the instruments that come with Logic, and write their own layers and answers.")
MOTIF_NOTE = ("The motif comes from Shchedryk, a choral piece by Mykola Leontovych (1877–1921) that was first performed in December 1916. The music is old enough to be in the public domain. "
              "The English words and the 1936 choral arrangement that made it famous as “Carol of the Bells” are a separate work: this kit does not use them, and students must not copy "
              "any later arrangement. Students build their own original layers.")
CREDITS = ["The timing page, the note chart drawings, the layer map, the dynamics ramp, the checklists and the worked example: original work, Hudson Beat. "
           "The four-note motif is from Leontovych’s Shchedryk (first performed in 1916), which is in the public domain. No words, recordings or published arrangements are included.",
           "The cover illustration was made with digital and AI tools. No audio, video, album art, screenshots, presets, templates, links or "
           "chart data from other sources are included. No student work is included. The level and mixing guidance is general practice, "
           "given as starting points to set by ear."]
LOGIC_INTRO = ("Where to find the tools a Bell Ostinato Lab is likely to use. Demonstrate what your class needs on Classes 1 and 2 and then "
               "let students work. Names are from current Logic Pro versions; labels move between versions, so check yours.")
LOGIC_REF = [("Project, tempo and meter", "Create a project with a Software Instrument track. Set the project tempo in the control bar to the BPM on your timing page, and set the time signature to 3/4 "
              "(look in the control bar or the project settings; the place differs between versions)."),
             ("Choose a bell sound", "Open the Software Instrument library and look for a bell, glockenspiel, celesta or mallet sound (if your version has one). Synths such as Alchemy (if your version has it) can make "
              "a bell sound from scratch."),
             ("Enter the motif", "Open the region in the Piano Roll and set the grid to eighth notes. Draw Bb, A, Bb, G with the lengths on the note chart: a quarter note, two eighth notes and a quarter note, "
              "so the four notes fill exactly one bar. Octave numbers differ between versions, so compare the note letters and the distance in semitones."),
             ("Check the pitches", "Click or play each note and read its name from the Piano Roll or a help tag (if your version shows one), or compare the position of the notes on the piano keys. "
              "The distance between notes is what matters: down 1, up 1, down 3 semitones."),
             ("Repeat the region", "Make the one-bar region repeat for 4 bars with the loop option on the region, or copy it end to end (the loop option is in the region’s settings, if your version has it). "
              "A tiny gap or overlap at the barline shows up as a hiccup, so check the region ends exactly at the end of the bar."),
             ("Layer and transpose", "Copy the region to new tracks and give each its own sound. To move a layer by an octave, transpose its notes by +12 or −12 semitones in the Piano Roll "
              "or with a transpose control (if your version has one). For the answer, transpose a copy by −3 semitones."),
             ("Velocity", "In the Piano Roll look for the velocity display (if your version has it). Velocity runs from 1 to 127 and controls how hard a note is played; the dynamics table uses it as a "
              "starting point: pp 32 up to ff 112."),
             ("Volume automation", "On a track, show its automation (look for an Automation button or menu in your version) and choose Volume as the parameter. Click on the line to add points, "
              "drag them to the levels on your plan and check that straight lines join them. Reading and writing modes (if your version has them) record fader moves instead."),
             ("Mixer and bounce", "Open the Mixer (the key command is X by default, if your version has it) and set levels and pan. Keep the master peak below 0 dBFS with room to spare. Then File › Bounce › Project or Section (Command-B), MP3 or WAV, for the whole piece. "
              "In Finder, Control-click the .logicx and choose Compress.")]
PRESENT_CHECK = [f"Files named {FILE_NAME}; the .mp3 or .wav and the zipped .logicx handed in",
                 "Reflection page done (page @REFLECT)", "Three questions for classmates written",
                 "Rubric self-score done (page @RUBRIC)"]
VOCAB_PROMPT = "Where it shows up in my piece:"
TN1_EXTRA = (
    '<div class="box acc-b" style="margin-top:4pt"><span class="k">Where this kit helps with each struggle</span><ul style="margin:0">'
    '<li style="font-size:12pt;margin-bottom:3pt">A wrong motif: the note chart (page @MOTIF) shows every note by name, number and length, in two keys.</li>'
    '<li style="font-size:12pt;margin-bottom:3pt">A repeat with a gap: the entry page (page @ENTER) has a checklist for the region length and the barline.</li>'
    '<li style="font-size:12pt;margin-bottom:3pt">Crowded layers: the layer map (page @LAYERS) shows which of 5 layers plays in each bar, and the worked example (pages @EXAMPLE–@EXAMPLE2) shows a full set of choices.</li>'
    '<li style="font-size:12pt;margin-bottom:0">A jumpy crescendo: the dynamics page (page @DYNAMICS) gives the level at the start of every bar.</li></ul></div>')
TN1_SIZE = 12.0
PROJ_SIZE = 11.2
VOCAB_GAP = 5
LOGIC_SIZE = 9.4
PROJ1_EXTRA = ""
RUBRIC_EXTRA = ""

# ================================================================ the worked example: an invented piece at 90 BPM
EX_BAR_S = bar_len(EX_BPM)                  # 2 s
EX_BEAT_S = spb(EX_BPM)                     # 2/3 s
EX_WEAK = "I will enter some bell notes, repeat them, add more sounds and make it louder at the end, and it will sound cool."
EX_STRONG = ("My piece is in 3/4 at 90 BPM. One beat lasts 60 ÷ 90 = 0.667 seconds and one bar lasts 180 ÷ 90 = 2 seconds. My form is 16 bars = 32 seconds: a solo bell in bars 1 to 4, "
             "the celesta and the pad joining in bars 5 to 8, the bell and an answer taking turns in bars 9 to 12, and all of the layers except the answer playing in bars 13 to 16. I use 5 layers in all. "
             "My motif is Bb4, A4, Bb4, G4 in G minor, and my answer is G4, F#4, G4, E4 in E minor, 3 semitones lower. My volume line starts at pp (32), "
             "reaches mp (64) at bar 9 and mf (80) at bar 13, and rises to ff (112) at the end of bar 16.")
EX_QUESTIONS = ["Which layer joined last, and when did you notice it?",
                "Could you hear the answer reply to the bell?",
                "Where did the crescendo start, and did it feel smooth?"]
EX_NOTE = ("the bell never stops except in bars 10 and 12, where the answer takes its place; the pad holds one note under every bar from bar 5; "
           "the low bell arrives with the finale, and the line from mf to ff in bars 13 to 16 is the crescendo")


# ================================================================ drawings (all in code, labels logged for the fit check)
def padded(body, W, H, M=10):
    """Wrap a drawing's body with M units of clear padding on all four sides (wider than the thickest outer stroke), so no edge pixel is ever inked."""
    return f'<g transform="translate({M},{M})">{body}</g>', W + 2 * M, H + 2 * M


def section_headers(out, name, gx, bw, y=12, h=44, size=24):
    """The four section bars along the top of a 16-bar drawing: black, accent, black, accent."""
    for k, (nm, a, b) in enumerate(ARR_SECTIONS):
        x0 = gx + (a - 1) * bw
        out.append(f'<rect x="{x0 + 2:.1f}" y="{y}" width="{(b - a + 1) * bw - 4:.1f}" height="{h}" rx="8" fill="{ACCENT if k % 2 else "#000"}"/>')
        lbl = f"{nm} · bars {a}–{b}"
        out.append(D.t_(x0 + (b - a + 1) * bw / 2, y + h - 12, lbl, size, 700, fill_="#fff"))
        D.lab(name + " sections", lbl, size, (b - a + 1) * bw - 16)


def motif_body(W=1600, name="motif", nb=2, blank=False):
    """The motif as a piano roll in two bars: bar 1 in G minor (Bb4 A4 Bb4 G4) and bar 2 in E minor, 3 semitones lower (G4 F#4 G4 E4). Rows are semitones E4 to Bb4, columns are
    eighth notes (6 to a bar of 3/4). Every note is a rect of class "nt"; the semitone move between neighboring notes is printed under the grid (class "ivl")."""
    gx = 150
    pw = W - gx - 34
    slots = 6 * nb
    cw = pw / slots
    rows = HIGH - LOW + 1
    ch = 50
    top = 124
    bot = top + rows * ch
    out = []
    for i in range(rows):
        m = HIGH - i
        black = (m % 12) in (1, 3, 6, 8, 10)
        out.append(f'<rect x="{gx}" y="{top + i * ch}" width="{pw}" height="{ch}" fill="{"#e6e6e6" if black else "#fff"}" stroke="#bbb" stroke-width="1.5"/>')
        out.append(D.t_(gx - 14, top + i * ch + ch / 2 + 9, ROW_NAMES[m], 24, 700, anchor="end"))
        D.lab(name + " rows", "F#4", 24, gx - 24)
    for s in range(slots + 1):
        x = gx + s * cw
        wide = s % 2 == 0
        bar = s % 6 == 0
        out.append(f'<line x1="{x:.1f}" y1="{top}" x2="{x:.1f}" y2="{bot}" stroke="{"#000" if bar else ("#777" if wide else "#ccc")}" stroke-width="{4 if bar else (2 if wide else 1.5)}"/>')
    out.append(f'<rect x="{gx}" y="{top}" width="{pw}" height="{bot - top}" fill="none" stroke="#000" stroke-width="4"/>')
    heads = [("BAR 1 · G MINOR", "the original key"), ("BAR 2 · E MINOR", "3 semitones lower")] if not blank else [("MY SKETCH · ONE BAR OF 3/4", "6 eighth notes: 1 & 2 & 3 &")]
    for b in range(nb):
        x0 = gx + b * 6 * cw
        out.append(D.t_(x0 + 6 * cw / 2, 34, heads[b][0], 28, 700, fill_=ACCENT))
        out.append(D.t_(x0 + 6 * cw / 2, 66, heads[b][1], 22, 500, "Source Sans 3", fill_="#222"))
        D.lab(name + " heads", heads[b][0], 28, 6 * cw - 20)
        for s, c in enumerate(["1", "&", "2", "&", "3", "&"]):
            out.append(D.t_(x0 + (s + 0.5) * cw, 106, c, 22, 500 if c == "&" else 700, "Source Sans 3", fill_="#222"))
    out.append(D.t_(gx - 14, 106, "BEAT", 20, 700, anchor="end", fill_=ACCENT))
    for b, notes in enumerate(() if blank else (MOTIF, MOTIF_E)):
        cx_list = []
        for nm, m, st, ln in notes:
            x = gx + (b * 6 + st) * cw
            y = top + (HIGH - m) * ch
            out.append(f'<rect class="nt" x="{x + 3:.1f}" y="{y + 4}" width="{ln * cw - 6:.1f}" height="{ch - 8}" rx="6" fill="{ACCENT if b == 0 else ACC_LIGHT}" stroke="#000" stroke-width="3"/>')
            out.append(D.t_(x + ln * cw / 2, y + ch / 2 + 9, nm, 26, 700, fill_="#fff" if b == 0 else "#000"))
            D.lab(name + " notes", nm, 26, cw - 14)
            cx_list.append(x + ln * cw / 2)
        for (a, c), iv in zip(zip(cx_list, cx_list[1:]), intervals(notes)):
            out.append(D.t_((a + c) / 2, bot + 40, sgn(iv), 28, 700, extra='class="ivl"'))
    if not blank:
        out.append(D.t_(gx - 14, bot + 40, "SEMITONES", 20, 700, anchor="end", fill_=ACCENT))
        D.lab(name + " rows", "SEMITONES", 20, gx - 24)
    cap = ("Draw the 4 notes: quarter, eighth, eighth, quarter." if blank else
           "The same 4 notes in two keys: every note in bar 2 is 3 semitones below its twin in bar 1.")
    out.append(D.t_(gx + pw / 2, bot + (50 if blank else 94), cap, 24, 700, "Source Sans 3"))
    D.lab(name + " cap", cap, 24, pw)
    return padded("".join(out), W, bot + (66 if blank else 110), 16)


def layers_body(W=1600, name="layers", blank=False):
    """The 16-bar layer map at 90 BPM: four sections of 4 bars, five layers (rows), blocks where a layer plays (class "block"), the number of layers sounding in each bar
    (class "cnt") and the seconds at each section start."""
    gx = 190
    pw = W - gx - 34
    bw = pw / ARR_BARS
    rh, gap = 54, 10
    top = 126
    out = []
    section_headers(out, name, gx, bw)
    for b in range(ARR_BARS):
        out.append(D.t_(gx + (b + 0.5) * bw, 94, str(b + 1), 24, 700))
    out.append(D.t_(gx - 14, 94, "BAR", 22, 700, anchor="end", fill_=ACCENT))
    fills = {"BELL": ACCENT, "CELESTA": ACC_LIGHT, "PAD": "#d9d9d9", "LOW BELL": "#555", "ANSWER": "#fff"}
    for r, (nm, spans) in enumerate(ARR_ROWS):
        y = top + r * (rh + gap)
        out.append(f'<rect x="{gx}" y="{y}" width="{pw}" height="{rh}" fill="#fff" stroke="#bbb" stroke-width="2"/>')
        for b in range(1, ARR_BARS):
            out.append(f'<line x1="{gx + b * bw:.1f}" y1="{y}" x2="{gx + b * bw:.1f}" y2="{y + rh}" stroke="#e2e2e2" stroke-width="1.5"/>')
        out.append(D.t_(gx - 14, y + rh / 2 + 9, nm, 24, 700, anchor="end"))
        D.lab(name + " rows", nm, 24, gx - 24)
    bot = top + len(ARR_ROWS) * (rh + gap) - gap
    for k in range(ARR_BARS // SEC_BARS + 1):
        x = gx + k * SEC_BARS * bw
        out.append(f'<line x1="{x:.1f}" y1="{top - 8}" x2="{x:.1f}" y2="{bot + 62}" stroke="#000" stroke-width="3" stroke-dasharray="9 7"/>')
    for r, (nm, spans) in enumerate(ARR_ROWS):
        y = top + r * (rh + gap)
        if not blank:
            for a, b in spans:
                out.append(f'<rect class="block" x="{gx + (a - 1) * bw + 3:.1f}" y="{y + 5}" width="{(b - a + 1) * bw - 6:.1f}" height="{rh - 10}" rx="7" fill="{fills[nm]}" '
                           f'stroke="#000" stroke-width="3"/>')
    cy = bot + 30
    out.append(D.t_(gx - 14, cy + 38, "LAYERS", 22, 700, anchor="end", fill_=ACCENT))
    D.lab(name + " rows", "LAYERS", 22, gx - 24)
    for b in range(1, ARR_BARS + 1):
        if blank:
            out.append(f'<rect x="{gx + (b - 1) * bw + bw * 0.2:.1f}" y="{cy + 8}" width="{bw * 0.6:.1f}" height="38" rx="6" fill="#fff" stroke="#000" stroke-width="2.5"/>')
        else:
            out.append(D.t_(gx + (b - 0.5) * bw, cy + 38, str(len(layers_in_bar(b))), 28, 700, extra='class="cnt"'))
    out.append(D.t_(gx - 14, cy + 90, "SECONDS", 22, 700, anchor="end", fill_=ACCENT))
    D.lab(name + " rows", "SECONDS", 22, gx - 24)
    for k in range(ARR_BARS // SEC_BARS + 1):
        s = start_s(EX_BPM, SEC_BARS * k + 1)
        out.append(D.t_(gx + k * SEC_BARS * bw, cy + 90, fmt(s), 24, 700, anchor="start" if k == 0 else ("end" if k == ARR_BARS // SEC_BARS else "middle")))
    if blank:
        cap = f"{ARR_BARS} bars with {len(ARR_ROWS)} layers. Draw a block where each layer plays, then write how many layers sound in each bar."
    else:
        cap = f"{ARR_BARS} bars at {EX_BPM} BPM = {fmt(ARR_BARS * EX_BAR_S)} seconds, with {len(ARR_ROWS)} layers. The number row shows how many layers sound in each bar."
    out.append(D.t_(gx + pw / 2, cy + 142, cap, 24, 700, "Source Sans 3"))
    D.lab(name + " cap", cap, 24, pw)
    return padded("".join(out), W, cy + 160, 16)


def callresp_body(W=1500, name="callresp"):
    """Bars 9 to 12 of the layer map up close: the bell calls in bars 9 and 11, the answer replies in bars 10 and 12 (class "block"), and the pad holds under all four."""
    gx = 170
    pw = W - gx - 34
    bw = pw / SEC_BARS
    rh, gap = 64, 12
    top = 90
    out = []
    first = ARR_SECTIONS[2][1]
    for i in range(SEC_BARS):
        b = first + i
        call = b in bars_of("BELL")
        x0 = gx + i * bw
        lbl = f"BAR {b} · {'CALL' if call else 'REPLY'}"
        out.append(f'<rect x="{x0 + 2:.1f}" y="12" width="{bw - 4:.1f}" height="50" rx="8" fill="{"#000" if call else ACCENT}"/>')
        out.append(D.t_(x0 + bw / 2, 46, lbl, 26, 700, fill_="#fff"))
        D.lab(name + " heads", lbl, 26, bw - 20)
    rows = [("BELL", ACCENT, "#fff", "G minor"), ("ANSWER", ACC_LIGHT, "#000", "E minor"), ("PAD", "#d9d9d9", "#000", "holds G")]
    for r, (nm, fl, tc, tx) in enumerate(rows):
        y = top + r * (rh + gap)
        out.append(f'<rect x="{gx}" y="{y}" width="{pw}" height="{rh}" fill="#fff" stroke="#bbb" stroke-width="2"/>')
        out.append(D.t_(gx - 14, y + rh / 2 + 9, nm, 26, 700, anchor="end"))
        D.lab(name + " rows", nm, 26, gx - 24)
    bot = top + len(rows) * (rh + gap) - gap
    for k in range(SEC_BARS + 1):
        x = gx + k * bw
        out.append(f'<line x1="{x:.1f}" y1="{top - 8}" x2="{x:.1f}" y2="{bot + 14}" stroke="#000" stroke-width="3" stroke-dasharray="9 7"/>')
        out.append(D.t_(x, bot + 50, fmt(start_s(EX_BPM, first + k)), 24, 700, anchor="start" if k == 0 else ("end" if k == SEC_BARS else "middle")))
    for r, (nm, fl, tc, tx) in enumerate(rows):
        y = top + r * (rh + gap)
        if nm == "PAD":
            spans = [(first, first + SEC_BARS - 1)]
        else:
            inb = [b for b in bars_of(nm) if first <= b < first + SEC_BARS]
            spans = []
            for b in inb:
                if spans and spans[-1][1] == b - 1:
                    spans[-1] = (spans[-1][0], b)
                else:
                    spans.append((b, b))
        for a, b in spans:
            bx, bw2 = gx + (a - first) * bw + 4, (b - a + 1) * bw - 8
            out.append(f'<rect class="block" x="{bx:.1f}" y="{y + 6}" width="{bw2:.1f}" height="{rh - 12}" rx="8" fill="{fl}" stroke="#000" stroke-width="3"/>')
            out.append(D.t_(bx + bw2 / 2, y + rh / 2 + 9, tx, 26, 700, fill_=tc))
            D.lab(name + " blocks", tx, 26, bw2 - 20)
    out.append(D.t_(gx - 14, bot + 50, "SECONDS", 22, 700, anchor="end", fill_=ACCENT))
    D.lab(name + " rows", "SECONDS", 22, gx - 24)
    cap = "The bell calls, the answer replies 3 semitones lower, and the pad holds one note under both."
    out.append(D.t_(gx + pw / 2, bot + 98, cap, 24, 700, "Source Sans 3"))
    D.lab(name + " cap", cap, 24, pw)
    return padded("".join(out), W, bot + 114, 16)


def ramp_body(W=1600, name="ramp", blank=False):
    """The volume automation line over 16 bars (an example velocity-style plan, 0 to 127): five points joined by straight lines (class "pt"), the dynamic marks pp to ff on the left,
    four section bars and bar numbers underneath, and a crescendo hairpin over the last 4 bars."""
    gx = 168
    pw = W - gx - 44
    top, ph = 108, 262
    bot = top + ph
    out = []

    def X(pos):
        return gx + (pos - 1) / ARR_BARS * pw

    def Y(v):
        return bot - float(v) / 140 * ph
    for k, (nm, a, b) in enumerate(ARR_SECTIONS):
        out.append(f'<rect x="{X(a):.1f}" y="{top}" width="{X(b + 1) - X(a):.1f}" height="{ph}" fill="{"#f1f1f1" if k % 2 == 0 else "#fff"}" stroke="none"/>')
    for n, _, v in DYN:
        out.append(f'<line x1="{gx}" y1="{Y(v):.1f}" x2="{gx + pw}" y2="{Y(v):.1f}" stroke="#aaa" stroke-width="2" stroke-dasharray="8 7"/>')
        lbl = f"{n} · {v}"
        out.append(D.t_(gx - 14, Y(v) + 7, lbl, 20, 700, anchor="end"))
        D.lab(name + " marks", lbl, 20, gx - 22)
    for k in range(ARR_BARS // SEC_BARS + 1):
        out.append(f'<line x1="{X(SEC_BARS * k + 1):.1f}" y1="{top}" x2="{X(SEC_BARS * k + 1):.1f}" y2="{bot}" stroke="#000" stroke-width="3"/>')
    out.append(f'<rect x="{gx}" y="{top}" width="{pw}" height="{ph}" fill="none" stroke="#000" stroke-width="4"/>')
    for b in range(1, ARR_BARS + 1):
        out.append(D.t_(X(b + 0.5), bot + 36, str(b), 22, 700))
    out.append(D.t_(gx - 14, bot + 36, "BAR", 22, 700, anchor="end", fill_=ACCENT))
    section_headers(out, name, gx, pw / ARR_BARS, y=bot + 56, h=44)
    if not blank:
        pts = " ".join(f"{X(p):.1f},{Y(v):.1f}" for p, v in POINTS)
        out.append(f'<polyline points="{pts}" fill="none" stroke="#000" stroke-width="7" stroke-linejoin="round" stroke-linecap="round"/>')
        for i, (p, v) in enumerate(POINTS):
            out.append(f'<circle class="pt" cx="{X(p):.1f}" cy="{Y(v):.1f}" r="13" fill="{ACCENT}" stroke="#000" stroke-width="4"/>')
            lbl = f"{mark_of(v)} {v}"
            anc = "start" if i == 0 else ("end" if i == len(POINTS) - 1 else "middle")
            dx = 18 if i == 0 else (-18 if i == len(POINTS) - 1 else 0)
            out.append(D.t_(X(p) + dx, Y(v) - 26, lbl, 24, 700, anchor=anc))
            D.lab(name + " pts", lbl, 24, 110)
        x0, x1 = X(13), X(17)
        yc = 48
        out.append(f'<polyline points="{x0:.1f},{yc} {x1:.1f},{yc - 18} " fill="none" stroke="#000" stroke-width="4" stroke-linecap="round"/>')
        out.append(f'<polyline points="{x0:.1f},{yc} {x1:.1f},{yc + 18} " fill="none" stroke="#000" stroke-width="4" stroke-linecap="round"/>')
        out.append(D.t_(x0 - 14, yc + 8, "crescendo", 24, 700, anchor="end", fill_=ACCENT))
        D.lab(name + " cresc", "crescendo", 24, X(13) - gx - 20)
    out.append(D.t_(gx + pw / 2, bot + 140, ("Volume automation: draw your own line, one point at each bar where the level changes." if blank else
                                              f"Volume automation: {len(POINTS)} points joined by straight lines. In bars 13 to 16 the line rises from 80 (mf) to 112 (ff)."), 24, 700, "Source Sans 3"))
    D.lab(name + " cap", "Volume automation: draw your own line, one point at each bar where the level changes.", 24, pw)
    D.lab(name + " cap", f"Volume automation: {len(POINTS)} points joined by straight lines. In bars 13 to 16 the line rises from 80 (mf) to 112 (ff).", 24, pw)
    return padded("".join(out), W, bot + 156, 16)


def hero_body():
    """The owner's pre-made art (art/hero.png, used whole). The viewBox only trims fully transparent margin: the art's own pixels
    (x 48-1349, y 338-1226 of 1400) stay at least 40 units inside it, which --check proves from the file."""
    return (f'<image href="../art/hero.png" x="{-HX}" y="{-HY}" width="1400" height="1400"/>', HW, HH)


HX, HY, HW, HH = 8, 298, 1382, 969

DRAWINGS = {"hero": hero_body, "motif": lambda: motif_body(1600, "motif deck"), "layers": lambda: layers_body(1600, "layers deck"),
            "callresp": lambda: callresp_body(1500, "callresp deck"), "ramp": lambda: ramp_body(1600, "ramp deck")}
DRAWING_PX = {"hero": 1500, "motif": 2000, "layers": 2000, "callresp": 1800, "ramp": 2000}
SIDE = {"motif": ["The same shape in two keys", "Bar 2 is 3 semitones lower than bar 1"],
        "layers": ["5 layers over 16 bars", "Each 4-bar section adds or changes a layer"],
        "callresp": ["The bell calls, the answer replies", "The pad holds one note under both"],
        "ramp": ["From pp at bar 1 to ff at the end", "Bars 13 to 16 rise from mf to ff"]}
# extra drawings used on pages only, rendered alone on a transparent ground by --check as well
PAGE_DRAWINGS = {"motif-page": lambda: motif_body(1600, "motif page"), "motif-blank-page": lambda: motif_body(1000, "motif blank page", nb=1, blank=True), "layers-page": lambda: layers_body(1600, "layers page"),
                 "layers-blank-page": lambda: layers_body(1600, "layers blank page", blank=True), "callresp-page": lambda: callresp_body(1500, "callresp page"),
                 "ramp-page": lambda: ramp_body(1600, "ramp page"), "ramp-blank-page": lambda: ramp_body(1600, "ramp blank page", blank=True)}


def label_extras():
    for k, fn in PAGE_DRAWINGS.items():
        fn()


# ================================================================ intro deck: (class, kind, title, body, speaker notes)
SLIDES = [
    (1, "title", "Bell Ostinato Lab", "Four notes. Five layers. One build.",
     "Class 1, the first minute. No audio is included in this deck. Open with the idea: you will build a short piece from one four-note motif, repeat it as an ostinato, layer it at different octaves "
     "and sounds, answer it in a second key and shape it from soft to loud with automation. Nobody needs to read notation, and the only existing music is the four-note motif, which is in the public domain."),
    (1, "listen", "Hear the bells", "Think, then share|Teacher: read aloud, no audio plays. Four bell notes ring, then ring again, and again, always the same. "
     "Then a second bell joins in a higher register, then a third, and the sound grows.|What stays the same while new sounds arrive?|What would make the bells feel like they are getting closer?|"
     "How could a sound get louder without anyone playing harder?",
     "Read the scene aloud slowly and ask the three questions. Take a few answers. Nothing is played from a speaker. Students will say the pattern stays the same, the new sounds are higher or lower, "
     "and the sound seems nearer when it is louder. Write their words on the board. The project turns each idea into a tool with a number attached: a bar length, an interval, an octave, a level."),
    (1, "bullets", "What is the Bell Ostinato Lab?", "Start from one four-note motif|Repeat it as an ostinato in 3/4|"
     "Layer it in 5 layers over 16 bars|Shape it with dynamics and automation",
     "The project in four lines. Every student enters the same four-note motif (Bb4, A4, Bb4, G4) in Logic Pro and repeats it as an ostinato. They layer it at different octaves and with different sounds, "
     "answer it in a second key, and draw a volume line from pp to ff. The motif is from Leontovych's Shchedryk (first performed in 1916); this kit uses only the motif and no words, and students build their own layers."),
    (1, "days", "Three classes", "",
     "The shape of the project. Class 1: hook, the timing math, the motif and entering the ostinato. Class 2: layering, the answer in a second key and octaves. Class 3: dynamics and automation, mix, "
     "bounce, present and reflect. The badge on this slide reads Classes 1 to 3 because it covers all three. With two classes, do the plan, motif, ostinato and layers in Class 1 and the rest in Class 2; "
     "with four, add a day for presentations. Hand out the timing page, the note chart and the entry page now."),
    (1, "pic", "The four-note motif", "motif",
     f"Class 1. The motif as a piano roll: bar 1 is the original key, G minor, with Bb4, A4, Bb4 and G4 as a quarter note, two eighth notes and a quarter note, which adds up to 3 beats, one bar of 3/4. "
     f"Bar 2 is the same shape 3 semitones lower, in E minor: G4, F#4, G4 and E4. The moves between notes are −1, +1 and −3 semitones in both keys. Two public scores show this motif the same way; "
     f"the note chart is on page {pg('motif')} and the entry page is page {pg('enter')}."),
    (1, "bullets", "The math: one bar of 3/4 = 180 ÷ BPM", "A bar of 3/4 has 3 beats|One beat lasts 60 ÷ BPM seconds|One bar lasts 180 ÷ BPM seconds|At 90 BPM a bar is 2 seconds and 16 bars are 32 seconds",
     f"Class 1, the key idea. In 3/4 there are three quarter-note beats in a bar, and a beat lasts 60 divided by the tempo, so a bar lasts 3 × 60 ÷ BPM = 180 ÷ BPM seconds. At 90 BPM that is 2 seconds, "
     f"so a 16-bar piece lasts 32 seconds; at 72 BPM it lasts 40 seconds and at 120 BPM 24 seconds. An eighth note is 30 ÷ BPM seconds, and the motif has 6 eighth-note slots in its bar. The timing page is page {pg('timing')}."),
    (1, "steps", "Enter the ostinato in Logic Pro", "Set the project to 3/4 and the tempo from your timing page|Add a Software Instrument track with a bell sound|Draw the four notes in the Piano Roll|"
     "Check each pitch and length against the note chart|Repeat the one-bar region for 4 bars",
     f"Class 1. Demonstrate on the projector. Create a project, set 3/4 and a tempo, add a Software Instrument track and pick a bell-like sound (if your version has one). Open the Piano Roll, set the grid to eighth notes "
     f"and draw Bb, A, Bb, G with the lengths on the note chart. Octave numbers differ between versions, so students compare note letters and distances. Repeat the region by looping or copying it (if your version has a loop option). "
     f"The quick reference is page {pg('logicref')} and the entry page is page {pg('enter')}."),
    (1, "check", "Check your ostinato", "Time signature 3/4, tempo from my timing page|The motif fills exactly one bar: 3 beats|Pitches: Bb, A, Bb, G (or G, F#, G, E)|"
     "Lengths: quarter, eighth, eighth, quarter|It repeats for 4 bars with no gap|No words and no other melody",
     f"Class 1. The entry checklist, shortened to fit the slide. Ask students to play the ostinato for you before they leave and to name the three intervals: down 1, up 1 and down 3 semitones. "
     f"A gap at the barline usually means the region is a little too long or too short. The entry page is page {pg('enter')}; the full checklist and the entry log are on it."),
    (2, "pic", "Layer it: five layers, 16 bars", "layers",
     f"Class 2. The layer map: four sections of 4 bars and 5 layers. The bell plays the ostinato in bars 1 to 9, 11 and 13 to 16. The celesta, the same motif an octave higher, plays in bars 5 to 8 and 13 to 16. "
     f"The pad holds one note per bar from bar 5 to bar 16. The low bell, an octave lower, joins in bars 13 to 16, and the answer plays in bars 10 and 12. The number row shows how many of the 5 layers sound: at most 1, 3, 2 and 4 in the four "
     f"sections. At 90 BPM the sections start at 0, 8, 16 and 24 seconds. The layer map is on page {pg('layers')}."),
    (2, "pic", "Call and response", "callresp",
     f"Class 2. Bars 9 to 12 up close. The bell calls in bars 9 and 11 and rests in bars 10 and 12, where the answer replies with the same motif 3 semitones lower, in E minor: G4, F#4, G4, E4. "
     f"The pad holds one note under all four bars. A call and a reply are like a conversation in music. Students write their own answer on page {pg('answer')}; it can be the motif in a second key, as here, "
     f"or an original phrase of their own."),
    (2, "bullets", "Layering at other octaves", "An octave is 12 semitones: twice the frequency|Move a copy of the motif by +12 for a higher layer|Move it by −12 for a lower layer|"
     "Try a bell, a celesta and a pad if your version has them",
     f"Class 2. Layering is mostly register and sound. A copy of the motif moved up 12 semitones sounds an octave higher: Bb4 becomes Bb5, and its frequency doubles from 466.2 to 932.3 Hz. A copy moved down 12 semitones halves it. "
     f"Different sounds, such as a bell, a celesta or a soft pad, help each layer stand apart. Demonstrate copying a region to a new track and transposing it. The layer map and the octave table are on page {pg('layers')}."),
    (3, "pic", "A crescendo with automation", "ramp",
     f"Class 3. A volume line across the 16 bars: five automation points joined by straight lines, at 32 (pp) in bars 1 to 5, 64 (mp) at bar 9, 80 (mf) at bar 13 and 112 (ff) at the end of bar 16. "
     f"The last four bars rise from 80 to 112, which is a crescendo, 8 levels per bar. The numbers are an example plan on a 0 to 127 scale, like MIDI velocity; students draw their own line on page {pg('dynamics')}. "
     f"If your version has automation, the line is drawn on the track's automation lane."),
    (3, "steps", "Draw volume automation", "Show the track's automation, if your version has it|Choose Volume as the parameter|Click to add a point at each bar where the level changes|"
     "Drag the points to the levels on your plan|Play it back and listen for the crescendo",
     f"Class 3. Demonstrate on the projector. Describe the controls generically: there is a way to show a track's automation and a parameter menu with Volume in it; clicking the line adds a point and dragging moves it. "
     f"Menu names and button places move between versions, so check yours; the quick reference on page {pg('logicref')} hedges where they do. Students then use the mix checklist on page {pg('mix')}."),
    (3, "check", "What you turn in", "Bounced .mp3 or .wav, 16 bars long|Zipped .logicx project|Named: Your Name – Bells|Timing page, note chart and layer map|Reflection page|Rubric self-score and three questions",
     "Class 3. The submission checklist, shortened to fit the slide. Show where students hand in. The file name is Your Name, then Bells. Check the length before students bounce: "
     "the bounce should run all 16 bars, which is 32 seconds at 90 BPM; the timing page shows how many seconds that is at each tempo."),
    (3, "rubric", "How it’s scored", "",
     "The rubric: five categories, each scored 1 to 5, for a total out of 25. Students score themselves first; the final grade is the average of their score and yours. "
     "The slide reads the 5 column of each category aloud. Hand out the rubric page so students can self-score before they present."),
    (3, "bullets", "Presentation day", "Play your piece from the top|Point out the layers, the answer and the crescendo|Your three questions for classmates|Answer at least 2 of each classmate’s questions",
     "Class 3, presentations. Each student plays the piece and points out each layer as it arrives, the call and the answer, and the crescendo, with their bar numbers. Students write three "
     "questions they want classmates to answer, and answer at least two of each classmate's. Ask the class which layer they heard last and where the crescendo began."),
    (3, "closer", "One last thing…", "Repeat it.|Layer it.|Answer it.|Then let it grow.",
     "Close with the listening day: play a piece and ask the class which layer they would take away first, and why. A piece that grows without anyone noticing the join is a piece that was well planned and well timed. "
     "Ask a few students which choice did the most for their piece. No audio is included in this resource; the sounds are the students' own."),
]
SHOTS1 = [("pacing", "Pacing guide", "3 class periods, slide by slide"), ("motif", "Note chart", "One motif in two keys"),
          ("dynamics", "Dynamics ramp", "Automation and a crescendo")]
SHOTS2 = [1, 5, 7, 9, 10, 12]
SHOTS3 = [("timing", "Timing math"), ("motif", "Note chart"), ("enter", "Enter the motif"), ("layers", "Layer map"), ("answer", "Call and response"), ("dynamics", "Dynamics ramp"),
          ("mix", "Mix"), ("example", "Worked example")]
PREVIEW_PICKS = ["pacing", "motif", "layers", "dynamics"]

COVER_A = "Four notes, five layers, one build"
COVER_C = "Logic Pro · Ostinato · Layering · Automation"
PDF_COVER = dict(a=26, b=42, c=15, art=5.0)
SQ_COVER = dict(a=36, b=140, c=27, art=560, gap=20)
SQ_B_LINES = ["Bell", "Ostinato Lab"]
SQ_SUB = "3 class periods · one motif, 5 layers, a 16-bar form"
SQ_HEADS = {1: ("Ready to teach Monday", 76, "Pacing, note chart, dynamics ramp and the /25 rubric in one PDF", 28),
            2: ("Intro deck included", 76, f"{len(SLIDES)} editable slides (.pptx + PDF) with speaker notes on every slide", 28),
            3: ("Everything inside", 72, "Timing math, note chart, layer map, dynamics ramp and worked example", 28)}
SQ_BANDS = {1: "Motif <em>·</em> layers <em>·</em> automation <em>·</em> crescendo",
            2: "Note chart <em>·</em> layer map <em>·</em> dynamics ramp",
            3: f"{len(PLAN)} pages <em>·</em> US Letter PDF <em>·</em> no audio included"}


# ================================================================ small page helpers
CSS_CC = ("<style>table.cc td { text-align: center; padding: 2pt 3pt; font-size: 9.4pt; line-height: 1.15; } table.cc th { text-align: center; font-size: 9pt; } "
          "table.cc td.l { text-align: left; } table.cc tr.hi td { background: #eef5fb; }</style>")


def howto_page(n, wm=False):
    parts = [("Teacher pages", "howto", "example2", "How to use, overview, setup, pacing, teacher notes, Logic quick reference, worked example (2 pages)"),
             ("Student pages", "timing", "reflect", "Timing page, note chart, entry page, layer map, answer page, dynamics ramp, mix checklist, "
              "project sheet (3 pages), rubric, vocabulary, feedback planner, reflection page"),
             ("Intro deck (separate file)", None, None, f"{len(SLIDES)} slides, .pptx + PDF, speaker notes on every slide")]
    trs = "".join(f"<tr><td><b>{a}</b></td><td style='white-space:nowrap'>{('pages ' + str(D.IX(f)) + '–' + str(D.IX(l))) if f else 'deck'}</td>"
                  f"<td>{u}</td></tr>" for a, f, l, u in parts)
    inner = (f'<div class="cols"><div>'
             f'{D.H2("What this is", True)}'
             f'<p style="font-size:12pt;line-height:1.45">A {CLASSES}-class-period ostinato project for high school music technology. Every '
             f'student enters the same four-note motif in Logic Pro, repeats it as an ostinato in 3/4, layers it at several octaves and sounds over a 16-bar form, '
             f'answers it in a second key and shapes the piece from pp to ff with volume automation (if their version has it). Students plan the timing with simple arithmetic, present the result and reflect on it. '
             f'It is an original Hudson Beat project.</p>'
             f'{D.H2("Quick start")}<ol>'
             f'<li style="margin-bottom:5pt">Read the pacing guide (page {D.IX("pacing")}) and the teacher notes (pages {D.IX("tn1")}–{D.IX("tn2")}).</li>'
             f'<li style="margin-bottom:5pt">Look at the timing page, the note chart, the layer map and the dynamics ramp (pages {D.IX("timing")}–{D.IX("dynamics")}) and the setup (page {D.IX("setup")}).</li>'
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
             f'<li><b>Pace:</b> Class 1 is the plan, motif and ostinato; Class 2 is layering and the answer; Class 3 is dynamics, automation and presentations (page {D.IX("pacing")}, which also shows two and four periods).</li>'
             f'<li><b>Grading:</b> the rubric, /{RUBRIC_TOTAL}, the average of the student’s and your score (page {D.IX("rubric")}).</li></ul>'
             f'<div class="box" style="margin-top:6pt"><span class="k">In one sentence</span><p style="margin:0;font-size:12pt">Students learn that '
             f'a piece built from one short pattern is planned: a tempo that sets the length of a bar, a motif entered exactly, layers placed in chosen bars and octaves, an answer in a second key and a level that grows on purpose.</p></div>'
             f'<p class="small" style="margin-top:6pt">Logic Pro is a product of Apple Inc. This resource is not affiliated with Apple.</p>'
             f'</div></div>')
    return D.page("How to use this resource", "START HERE", "Teacher", inner, n, key="howto")


def overview_page(n, wm=False):
    inner = (f'<div class="cols"><div>'
             f'<div class="box inv" style="margin-bottom:6pt"><span class="k">The project in one line</span><p style="margin:0;font-size:12pt">'
             f'<b>{TITLE}</b> · Motif, layers, dynamics and automation · Logic Pro<br>One four-note motif, five layers, a piece that grows from pp to ff.</p></div>'
             f'{D.H2("What students make")}'
             f'<p style="font-size:12.2pt;line-height:1.48">A piece of 16 bars of 3/4 built in Logic Pro from one four-note motif. The motif is entered in the Piano Roll and repeated as an ostinato. '
             f'It is layered at other octaves and with other sounds, answered in a second key in the bell’s rests, and shaped with a volume automation line that builds from pp to ff. '
             f'Students hand in a bounced file and the zipped .logicx project, plus their plans and a reflection, '
             f'then play the piece and take questions.</p>'
             f'{D.H2("What this project reinforces")}<p style="font-size:12pt;line-height:1.5">{TN_REINFORCES}</p>'
             f'{D.H2("Standards")}<p style="font-size:11.4pt">Supports the National Core Arts Standards for Music (Music Technology, high school): generating '
             f'and developing ideas (MU:Cr1.1, MU:Cr2.1), presenting work (MU:Pr6.1) and responding to it (MU:Re7.2).</p>'
             f'</div><div>'
             f'{D.H2("Goals", True)}<ul>' + "".join(f"<li style='font-size:12pt;line-height:1.45'>{g}</li>" for g in GOALS) + '</ul>'
             f'{D.H2("About the motif")}<div class="box acc-b" style="padding:5pt 9pt"><p style="margin:0 0 3pt;font-size:10.2pt;line-height:1.36">{THEME}</p>'
             f'<p style="margin:0;font-size:10.2pt;line-height:1.36">{BUILD_NOTE}</p></div>'
             f'<div class="box" style="margin-top:6pt;padding:5pt 9pt"><span class="k">At a glance</span><p style="margin:0;font-size:10.2pt;line-height:1.38"><b>Grades</b> {GRADES_TEXT}, music technology or music production · '
             f'<b>Length</b> {CLASSES} class periods (two and four also shown) · <b>Software</b> Logic Pro · <b>You supply</b> Macs with Logic Pro, headphones and a place to hand in files; no microphone is needed · '
             f'<b>Assessment</b> rubric, 5 categories scored 1–5, /{RUBRIC_TOTAL} (page {D.IX("rubric")})</p></div>'
             f'</div></div>')
    return D.page("Project overview", "OVERVIEW", "Ostinato project", inner, n, key="overview")


def setup_page(n, wm=False):
    inner = (f'<style>.sb p, .sb li {{ font-size: 11.6pt; line-height: 1.44; margin-bottom: 5pt; }}</style><div class="cols"><div class="big sb">'
             f'{D.H2("You need", True)}<ul>'
             f'<li><b>A Mac with Logic Pro</b> for each student, and <b>headphones</b>. Nothing is recorded: every sound comes from software instruments.</li>'
             f'<li><b>A keyboard is optional.</b> Students can draw the notes in the Piano Roll, so a MIDI keyboard is a convenience, not a requirement.</li>'
             f'<li><b>A place to hand in</b> the .mp3 or .wav files, the zipped .logicx and the reflection.</li>'
             f'<li><b>The timing page, note chart, layer map and dynamics ramp</b>, printed (pages {D.IX("timing")}–{D.IX("dynamics")}), or shown on the projector.</li>'
             f'<li><b>Printed student pages</b>, one set each (pages {D.IX("timing")}–{D.IX("reflect")}).</li></ul>'
             f'{D.H2("Before Class 1")}'
             + "".join(D.chk(c, 13, "font-size:11.6pt;margin-bottom:7pt") for c in [
                 f"Read the timing page (page {D.IX('timing')}) so you can answer ‘how long is one bar at 100 BPM?’ and ‘how long is a 16-bar piece?’",
                 f"Read the note chart (page {D.IX('motif')}) and play the motif once: Bb, A, Bb, G.",
                 f"Open Logic Pro on a student computer and check which tools your version has: a bell or celesta sound, the Piano Roll, automation (see page {D.IX('logicref')}).",
                 f"Read the worked example (pages {D.IX('example')}–{D.IX('example2')})."]) +
             f'</div><div class="big sb">'
             f'{D.H2("What to watch", True)}'
             f'<p style="font-size:11.4pt">Watch for a motif with a wrong note or the wrong length, a repeat that has a gap at the barline, a layer that hides the ostinato, and an automation line that jumps instead of rising. {TN_NOTE}</p>'
             f'<div class="box acc-b" style="margin-top:2pt"><span class="k">Ideas for the room</span><ul style="margin:0">'
             f'<li style="font-size:11.2pt">Ask while students work: which layer is this, and which bars does it play?</li>'
             f'<li style="font-size:11.2pt">Use only the four-note motif and the sounds that come with Logic. No other existing songs, videos or recordings.</li>'
             f'<li style="font-size:11.2pt">A student who is stuck can build the bell, one higher copy and a rising volume line: those already make a piece.</li></ul></div>'
             f'{D.H2("The motif and copyright")}'
             f'<div class="box"><p style="margin:0;font-size:10.4pt;line-height:1.4">{MOTIF_NOTE}</p></div>'
             f'<div class="box" style="margin-top:6pt"><span class="k">Keep the volume moderate</span><p style="margin:0;font-size:11pt;line-height:1.4">'
             f'Students hear a short pattern over and over in headphones, and the finale is the loudest part. Tell them to start low and check the final mix at a normal level.</p></div>'
             f'</div></div>')
    return D.page("Setup and what to watch", "SETUP", "Teacher", inner, n, key="setup")


# ================================================================ the student pages
def tempo_rows():
    rows = []
    for bpm in TEMPOS:
        hi = ' class="hi"' if bpm == EX_BPM else ''
        b, e = ("<b>", "</b>") if bpm == EX_BPM else ("", "")
        rows.append(f"<tr{hi}><td>{b}{bpm}{e}</td><td>{dec(spb(bpm), 3)}</td><td>{dec(eighth_len(bpm), 4)}</td><td>{b}{dec(bar_len(bpm), 3)}{e}</td>"
                    f"<td>{dec(SEC_BARS * bar_len(bpm), 3)}</td><td>{b}{dec(ARR_BARS * bar_len(bpm), 3)}{e}</td></tr>")
    return "".join(rows)


def len_rows():
    return "".join(f"<tr><td><b>{t}</b></td>" + "".join(f"<td>{dec(nb * bar_len(t), 3)}</td>" for nb in LEN_BARS) + "</tr>" for t in LEN_TEMPOS)


def timing_page(n, wm=False):
    inner = (CSS_CC +
             f'<p style="margin:0 0 4pt;font-size:10.2pt;line-height:1.36">Step 1: plan the form. In 3/4 there are 3 beats in a bar, each beat is a quarter note, and a bar holds 6 eighth notes. '
             f'These formulas turn a tempo into seconds. Every number below is computed, so you can check your own arithmetic against it.</p>'
             f'<div class="cols" style="gap:10pt;align-items:flex-start"><div class="box acc-b" style="padding:5pt 9pt;flex:1.15"><span class="k">The formulas (3/4)</span>'
             f'<p style="margin:0 0 2pt;font-size:9.8pt"><b>Seconds per beat</b> = 60 ÷ BPM</p><p style="margin:0 0 2pt;font-size:9.8pt"><b>Seconds per eighth note</b> = 30 ÷ BPM</p>'
             f'<p style="margin:0 0 2pt;font-size:9.8pt"><b>Seconds per bar</b> = 180 ÷ BPM = 3 beats = 6 eighth notes</p>'
             f'<p style="margin:0 0 2pt;font-size:9.8pt"><b>A section or piece of b bars</b> lasts b × 180 ÷ BPM seconds</p>'
             f'<p style="margin:0 0 2pt;font-size:9.8pt"><b>Bar b starts at</b> (b − 1) × 180 ÷ BPM seconds</p>'
             f'<p style="margin:0;font-size:9.8pt"><b>Example:</b> 90 BPM: 60 ÷ 90 = 0.667 s per beat, and 180 ÷ 90 = 2 s per bar.</p></div>'
             f'<div class="box" style="padding:5pt 9pt;flex:1"><span class="k">Rounding rules</span><p style="margin:0;font-size:9.2pt;line-height:1.32">Seconds per beat, bar and section to 3 decimals and seconds per eighth note to 4; '
             f'a 5 rounds up. So 30 ÷ 72 = 0.4167 seconds (the exact value is 0.41666…). The form-length table is exact at these three tempos.</p></div></div>'
             f'<span class="k" style="margin-top:5pt">How long is a beat, a bar and a section?</span>'
             f'<table class="t cc" style="margin-top:1pt"><tr><th>BPM</th><th>Seconds per beat</th><th>Seconds per eighth note</th><th>Seconds per bar</th><th>4-bar section (s)</th>'
             f'<th>16-bar form (s)</th></tr>{tempo_rows()}</table>'
             f'<p class="small" style="margin:0 0 2pt;font-size:8.6pt">The shaded row is the worked example. The 16-bar form lasts 16 × 180 ÷ BPM = 2880 ÷ BPM seconds, which is 32 seconds at 90 BPM.</p>'
             f'<span class="k" style="margin-top:3pt">How long is my piece? (form lengths at three tempos, in seconds)</span>'
             f'<table class="t cc" style="margin-top:1pt"><tr><th>BPM</th>' + "".join(f"<th>{nb} bars</th>" for nb in LEN_BARS) + f'</tr>{len_rows()}</table>'
             f'<p class="small" style="margin:0 0 3pt;font-size:8.6pt">At 72 BPM a bar is 2.5 s, at 90 BPM it is 2 s and at 120 BPM it is 1.5 s. A slower tempo makes the same 16 bars last longer.</p>'
             f'<div class="box" style="padding:5pt 9pt"><span class="k">Going the other way: how many bars fit in a time?</span>'
             f'<p style="margin:0 0 2pt;font-size:9.8pt;line-height:1.32">Bars = seconds × BPM ÷ 180. Check: 32 seconds at 90 BPM is 32 × 90 ÷ 180 = 16 bars. '
             f'Try it: 30 seconds at 90 BPM = 30 × 90 ÷ 180 = 15 bars, and 36 seconds at 100 BPM = 36 × 100 ÷ 180 = 20 bars.</p>'
             f'<div class="fl" style="margin:3pt 0 0;font-size:10pt"><b>My time:</b><span style="flex:0 0 0.8in"></span><b>s at</b><span style="flex:0 0 0.8in"></span><b>BPM = time × BPM ÷ 180 =</b><span></span><b>bars</b></div></div>'
             f'<div class="box acc-b" style="margin-top:5pt;padding:5pt 9pt"><span class="k">My plan</span>'
             f'<div class="fl" style="margin:3pt 0 3pt;font-size:10pt"><b>Tempo:</b><span></span><b>BPM</b><b style="margin-left:8pt">One beat = 60 ÷ BPM =</b><span></span><b>s</b></div>'
             f'<div class="fl" style="margin:0 0 3pt;font-size:10pt"><b>One bar = 180 ÷ BPM =</b><span></span><b>s</b><b style="margin-left:8pt">One section (4 bars) =</b><span></span><b>s</b></div>'
             f'<div class="fl" style="margin:0;font-size:10pt"><b>My piece: 16 bars =</b><span style="flex:0 0 0.8in"></span><b>s</b><b style="margin-left:8pt">The crescendo (bars 13 to 16) lasts</b><span style="flex:0 0 0.8in"></span><b>s</b></div></div>')
    return D.page("Timing page", "STUDENT", "Class 1", inner, n, wm, name=True, key="timing")


def note_rows():
    rows = []
    for i, ((nm, m, st, ln), (nm2, m2, _, _)) in enumerate(zip(MOTIF, MOTIF_E)):
        rows.append(f"<tr><td><b>{i + 1}</b></td><td>{START_BEAT[i]}</td><td>{fmt(LEN_BEATS[i])}</td><td><b>{nm}</b></td><td>{m}</td><td>{hz1(m)}</td><td><b>{nm2}</b></td><td>{m2}</td><td>{hz1(m2)}</td>"
                    f"<td>{sgn(m2 - m)}</td></tr>")
    return "".join(rows)


def ivl_rows():
    rows = []
    a, b = intervals(MOTIF), intervals(MOTIF_E)
    for i in range(3):
        v = a[i]
        rows.append(f"<tr><td><b>{i + 1} to {i + 2}</b></td><td>{MOTIF[i][0]} to {MOTIF[i + 1][0]}</td><td>{MOTIF_E[i][0]} to {MOTIF_E[i + 1][0]}</td><td>{sgn(v)}</td>"
                    f"<td class='l'>{IVL_NAME[abs(v)]}, {'down' if v < 0 else 'up'}</td></tr>")
    return "".join(rows)


def motif_page(n, wm=False):
    inner = (CSS_CC +
             f'<p style="margin:0 0 3pt;font-size:10.2pt;line-height:1.36">Step 2: learn the motif. The motif is four notes long and fills one bar of 3/4: a quarter note, two eighth notes and a quarter note, which add up to 3 beats. '
             f'It uses three different pitches and sits in G minor (two flats, Bb and Eb). Read the picture as a piano roll: each row is one semitone and each column is one eighth note. '
             f'{BB_NOTE}</p>'
             f'<div style="margin:0 0 3pt">{D.body_svg(motif_body(1600, "motif page"))}</div>'
             f'<span class="k" style="margin-top:3pt">The note chart: the motif in two keys</span>'
             f'<table class="t cc" style="margin-top:1pt"><tr><th rowspan="2">Note</th><th rowspan="2">Starts on beat</th><th rowspan="2">Lasts (beats)</th><th colspan="3">G minor (original)</th><th colspan="3">E minor (3 lower)</th><th rowspan="2">Change</th></tr>'
             f'<tr><th>Name</th><th>MIDI</th><th>Hz</th><th>Name</th><th>MIDI</th><th>Hz</th></tr>{note_rows()}</table>'
             f'<p class="small" style="margin:1pt 0 2pt;font-size:8.6pt">The lengths add up to {fmt(sum(LEN_BEATS))} beats, one bar of 3/4. MIDI note 60 is middle C (C4) and A4 is note 69 at 440 Hz; a note’s frequency is 440 × 2^((MIDI − 69) ÷ 12). '
             f'Software may number octaves differently, so compare the letters and the semitone distances.</p>'
             f'<div class="cols" style="gap:10pt;align-items:flex-start"><div style="flex:1.25"><span class="k" style="margin-top:2pt">The intervals</span>'
             f'<table class="t cc" style="margin-top:1pt"><tr><th>Notes</th><th>G minor</th><th>E minor</th><th>Semitones</th><th>Interval</th></tr>{ivl_rows()}</table>'
             f'<p class="small" style="margin:1pt 0 0;font-size:8.6pt">−1 + 1 + (−3) = −3: the last note is 3 semitones below the first, a minor third. The highest and lowest notes are Bb4 and G4, so the whole motif spans a minor third.</p></div>'
             f'<div class="box acc-b" style="padding:4pt 9pt;flex:1"><span class="k">Moving the motif to a new key</span>'
             f'<p style="margin:0 0 2pt;font-size:9.4pt;line-height:1.32">New MIDI number = old number + shift. Every note in the second key is 3 semitones lower, so the intervals do not change: −1, +1 and −3.</p>'
             f'<p style="margin:0;font-size:9.4pt;line-height:1.32">Try your own shift: ______ semitones. New numbers: ____ ____ ____ ____</p></div></div>'
             f'<div class="box" style="margin-top:4pt;padding:4pt 9pt"><span class="k">My notes</span>'
             f'<div class="fl" style="margin:2pt 0 2pt;font-size:10pt"><b>The motif in my own words:</b><span></span></div>'
             f'<div class="fl" style="margin:0 0 2pt;font-size:10pt"><b>Which interval is the biggest?</b><span></span><b>Is it up or down?</b><span style="flex:0 0 0.8in"></span></div></div>')
    return D.page("The motif: note chart and intervals", "STUDENT", "Class 1", inner, n, wm, name=True, key="motif")


def enter_page(n, wm=False):
    def box(title, items, acc=False):
        return (f'<div class="box{" acc-b" if acc else ""}" style="padding:4pt 9pt"><span class="k">{title}</span>'
                + "".join(D.chk(c, 11, "font-size:9.8pt;line-height:1.28;margin-bottom:2.5pt") for c in items) + '</div>')
    log = "".join(f"<tr><td style='height:21pt'><b>{i}</b></td><td></td><td></td><td></td><td></td><td></td></tr>" for i in range(1, 5))
    inner = (CSS_CC +
             f'<p style="margin:0 0 4pt;font-size:10.2pt;line-height:1.36">Step 3: build the ostinato. An ostinato is a short pattern that repeats in the same voice. Your first job is to enter the four notes exactly, '
             f'then repeat them. Take your time: every layer you add later is a copy of this one bar. The quick reference is on page {pg("logicref")}.</p>'
             f'<div class="cols" style="gap:9pt;align-items:flex-start"><div>'
             + box("Set up the project", ["The tempo is the BPM on my timing page, and the time signature is 3/4.",
                                          "I have a Software Instrument track with a bell, glockenspiel or celesta sound, if my version has one.",
                                          "My headphones are on and the volume is low.",
                                          "The Piano Roll grid is set to eighth notes."], True)
             + '</div><div>'
             + box("Enter the motif", ["I draw 4 notes in one bar: Bb, A, Bb, G.",
                                       "The lengths are a quarter note, an eighth note, an eighth note and a quarter note.",
                                       "The first note starts on beat 1 and the last note ends at the end of the bar.",
                                       "I compare every note with the note chart, letter by letter."])
             + '</div></div>'
             f'<div class="cols" style="gap:9pt;align-items:flex-start;margin-top:4pt"><div>'
             + box("Repeat it", ["The region is exactly one bar of 3/4 long.", "I repeat it for 4 bars, with the loop option or by copying, with no gap or overlap at the barlines.",
                                 "I listen to all 4 bars with my eyes closed: the pattern is steady.", "I save a new version of the project."], True)
             + '</div><div class="box" style="padding:4pt 9pt"><span class="k">If it sounds wrong</span>'
             f'<p style="margin:0 0 2pt;font-size:9.6pt;line-height:1.32">Check the notes one at a time. If every note sounds right but the pattern sounds odd, check the lengths. '
             f'If the pattern sounds right but too high or too low, check the octave; the shape and the distances are what matter.</p>'
             f'<p style="margin:0;font-size:9.6pt;line-height:1.32">Use only the motif. Do not copy any other melody or arrangement into your project.</p></div></div>'
             f'<span class="k" style="margin-top:5pt">Entry log</span>'
             f'<table class="t cc" style="margin-top:1pt"><tr><th>Note</th><th>Starts on beat</th><th>Length (beats)</th><th>Name I entered</th><th>Piano Roll shows</th><th>Matches the chart?</th></tr>{log}</table>'
             f'<span class="k" style="margin-top:5pt">My sketch: draw the motif before you enter it</span>'
             f'<div style="margin:1pt auto 2pt;width:40%">{D.body_svg(motif_body(1000, "motif blank page", nb=1, blank=True))}</div>'
             f'<div class="box" style="margin-top:5pt;padding:4pt 9pt"><span class="k">My setup</span>'
             f'<div class="fl" style="margin:2pt 0 2pt;font-size:10pt"><b>Sound name:</b><span></span><b>Tempo (BPM):</b><span style="flex:0 0 0.9in"></span><b>One bar lasts (s):</b><span style="flex:0 0 0.8in"></span></div>'
             f'<div class="fl" style="margin:0 0 2pt;font-size:10pt"><b>Octave label my software shows for the first note:</b><span></span></div></div>')
    return D.page("Enter and test the ostinato", "STUDENT", "Class 1", inner, n, wm, name=True, key="enter")


def layer_rows():
    rows = []
    for nm, spans in ARR_ROWS:
        sh = SHIFT_OF[nm]
        if nm == "PAD":
            names, shift = f"{midi_name(PAD_MIDI)} held", "one held note"
        else:
            base = MOTIF if nm != "ANSWER" else MOTIF
            names = " ".join(midi_name(m + (sh or 0)) for _, m, _, _ in base)
            shift = sgn(sh) if sh else "0"
        rows.append(f"<tr><td><b>{nm.title()}</b></td><td>{spans_text(spans)}</td><td>{len(bars_of(nm))}</td><td>{shift}</td><td class='l'>{names}</td></tr>")
    return "".join(rows)


def oct_rows():
    return "".join(f"<tr><td><b>{sgn(sh)}</b></td><td class='l'>{lbl}</td><td>{'× ' + ('2.000' if sh == 12 else '0.500')}</td><td>{hz1(70 + sh)}</td></tr>"
                   for sh, lbl in ((12, "octave up"), (-12, "octave down")))


def layers_page(n, wm=False):
    inner = (CSS_CC +
             f'<p style="margin:0 0 3pt;font-size:10.2pt;line-height:1.36">Step 4: layer it. A layer is one part of the piece on its own track, with its own sound and its own bars. This form is {ARR_BARS} bars, four sections of {SEC_BARS} bars, and it has '
             f'{len(ARR_ROWS)} layers. A new idea joins or changes in each section, so the listener hears the piece grow.</p>'
             f'<div style="margin:0 0 3pt">{D.body_svg(layers_body(1600, "layers page"))}</div>'
             f'<div class="cols" style="gap:10pt;align-items:flex-start"><div style="flex:1.7"><span class="k" style="margin-top:2pt">The layers in the model</span>'
             f'<table class="t cc" style="margin-top:1pt"><tr><th>Layer</th><th>Bars it plays</th><th>Bars</th><th>Shift (semitones)</th><th>Notes it plays</th></tr>{layer_rows()}</table>'
             f'<p class="small" style="margin:1pt 0 0;font-size:8.6pt">The layers play {sum(len(bars_of(r)) for r in ARR_LAYERS)} bars in all: {" + ".join(str(len(bars_of(r))) for r in ARR_LAYERS)}. '
             f'The number row on the map adds to the same {sum(len(layers_in_bar(b)) for b in range(1, ARR_BARS + 1))}.</p></div>'
             f'<div style="flex:1"><span class="k" style="margin-top:2pt">Octaves: the first note</span>'
             f'<table class="t cc" style="margin-top:1pt"><tr><th>Shift</th><th>Name</th><th>Frequency</th><th>First note becomes (Hz)</th></tr>{oct_rows()}</table>'
             f'<p class="small" style="margin:1pt 0 0;font-size:8.6pt">12 semitones make an octave, and an octave doubles the frequency: Bb4 is {hz1(70)} Hz, Bb5 is {hz1(82)} Hz.</p></div></div>'
             f'<span class="k" style="margin-top:4pt">My layer map: draw a block where each layer plays</span>'
             f'<div style="margin:1pt auto 2pt;width:82%">{D.body_svg(layers_body(1600, "layers blank page", blank=True))}</div>'
             f'<div class="fl" style="margin:2pt 0 0;font-size:10pt"><b>My layers:</b><span></span><b>Sections start at (s):</b><span style="flex:0 0 1.3in"></span></div>')
    return D.page("The layer map", "STUDENT", "Class 2", inner, n, wm, name=True, key="layers")


def shift_rows():
    rows = []
    for sh, key in ((-3, "E minor"), (-5, "D minor"), (2, "A minor")):
        ms = [m + sh for _, m, _, _ in MOTIF]
        rows.append(f"<tr><td><b>{sgn(sh)}</b></td><td>{key}</td><td class='l'>{' '.join(midi_name(m) for m in ms)}</td><td>{' '.join(str(m) for m in ms)}</td></tr>")
    return "".join(rows)


def answer_page(n, wm=False):
    inner = (CSS_CC +
             f'<p style="margin:0 0 3pt;font-size:10.2pt;line-height:1.36">Step 5: answer it. Call and response is a short phrase answered by a second phrase, like a conversation in music. Here the bell calls and the answer replies. '
             f'The model answer is the same motif 3 semitones lower, in E minor, placed in the bars where the bell rests: bars 10 and 12.</p>'
             f'<div style="margin:0 0 3pt;width:88%;margin-left:auto;margin-right:auto">{D.body_svg(callresp_body(1500, "callresp page"))}</div>'
             f'<div class="cols" style="gap:10pt;align-items:flex-start"><div style="flex:1"><span class="k" style="margin-top:2pt">The call and the answer</span>'
             f'<table class="t cc" style="margin-top:1pt"><tr><th>Part</th><th>Bars</th><th>Notes</th><th>MIDI</th></tr>'
             f'<tr><td><b>Call (bell)</b></td><td>9 and 11</td><td class="l">{" ".join(x[0] for x in MOTIF)}</td><td>{" ".join(str(x[1]) for x in MOTIF)}</td></tr>'
             f'<tr><td><b>Answer</b></td><td>10 and 12</td><td class="l">{" ".join(x[0] for x in MOTIF_E)}</td><td>{" ".join(str(x[1]) for x in MOTIF_E)}</td></tr></table>'
             f'<p class="small" style="margin:1pt 0 0;font-size:8.6pt">The answer starts {abs(SHIFT)} semitones below the call and moves the same way: −1, +1, −3. Its notes are 3 below each note of the call.</p></div>'
             f'<div style="flex:1"><span class="k" style="margin-top:2pt">Other keys to try (optional)</span>'
             f'<table class="t cc" style="margin-top:1pt"><tr><th>Shift</th><th>Key</th><th>Notes</th><th>MIDI</th></tr>{shift_rows()}</table>'
             f'<p class="small" style="margin:1pt 0 0;font-size:8.6pt">Each row is the motif moved by that many semitones from G minor.</p></div></div>'
             f'<div class="box acc-b" style="margin-top:4pt;padding:4pt 9pt"><span class="k">Rules for a good answer</span>'
             + "".join(D.chk(c, 11, "font-size:9.8pt;line-height:1.28;margin-bottom:2pt") for c in [
                 "It plays in the bell’s rests, so the call and the answer take turns and never fight.",
                 "It uses the same tempo and lines up on the first beat of its bar.",
                 "I can say its key and its shift in semitones, and I have checked its notes against the chart.",
                 "It has its own sound or octave, so I can tell it from the call."]) + '</div>'
             f'<div class="box" style="margin-top:4pt;padding:4pt 9pt"><span class="k">My answer</span>'
             f'<div class="fl" style="margin:2pt 0 2pt;font-size:10pt"><b>My answer’s shift:</b><span style="flex:0 0 0.9in"></span><b>Key:</b><span style="flex:0 0 1.0in"></span><b>Bars:</b><span></span></div>'
             f'<div class="fl" style="margin:0 0 2pt;font-size:10pt"><b>Notes (names):</b><span></span><b>MIDI numbers:</b><span></span></div>'
             f'<div class="fl" style="margin:0;font-size:10pt"><b>Sound I chose, and why:</b><span></span></div></div>'
             f'<span class="k" style="margin-top:4pt">Make it my own (optional)</span>'
             f'<p style="margin:1pt 0 0;font-size:9.8pt;line-height:1.32">Write a short phrase of your own instead of the transposed motif, no longer than one bar, and use it as the answer. Draw its notes here: write each note’s name and length.</p>'
             + D.lines(2, 24))
    return D.page("Call and response: the answer", "STUDENT", "Class 2", inner, n, wm, name=True, key="answer")


def bar_level_rows():
    bars = range(1, ARR_BARS + 1)
    r1 = "".join(f"<th>{b}</th>" for b in bars)
    r2 = "".join(f"<td>{exact(level_at(b))}</td>" for b in bars)
    r3 = "".join(f"<td>{mark_of(level_at(b)) or '·'}</td>" for b in bars)
    return f"<tr><th>Bar</th>{r1}</tr><tr><td><b>Level</b></td>{r2}</tr><tr><td><b>Mark</b></td>{r3}</tr>"


def dyn_rows():
    return "".join(f"<tr><td><b>{n}</b></td><td class='l'>{m}</td><td>{v}</td></tr>" for n, m, v in DYN)


def dynamics_page(n, wm=False):
    inner = (CSS_CC +
             f'<p style="margin:0 0 3pt;font-size:10.2pt;line-height:1.36">Step 6: shape the sound. Dynamics are how loud or soft the music is. A crescendo is a gradual increase in loudness. '
             f'In Logic Pro you can draw one as a volume automation line: points on a track’s volume that you place and drag (if your version has automation). '
             f'The plan is an example on a 0 to 127 scale, like MIDI velocity, not a rule.</p>'
             f'<div style="margin:0 auto 3pt;width:80%">{D.body_svg(ramp_body(1600, "ramp page"))}</div>'
             f'<div class="cols" style="gap:10pt;align-items:flex-start"><div style="flex:1"><span class="k" style="margin-top:2pt">Dynamic marks and example levels</span>'
             f'<table class="t cc" style="margin-top:1pt"><tr><th>Mark</th><th>Meaning</th><th>Level</th></tr>{dyn_rows()}</table></div>'
             f'<div class="box acc-b" style="padding:4pt 9pt;flex:1.1"><span class="k">Reading the line</span>'
             f'<p style="margin:0 0 2pt;font-size:9.4pt;line-height:1.32">Between two points the level changes by the same amount each bar: (end level − start level) ÷ number of bars. '
             f'Bars 13 to 16: (112 − 80) ÷ 4 = 8 levels per bar, so the line is at 80 at bar 13 and 104 at bar 16.</p>'
             f'<p style="margin:0;font-size:9.4pt;line-height:1.32">Velocity sets how hard each note is played; volume automation sets the level of the whole track. '
             f'Try both and listen to the difference.</p></div></div>'
             f'<span class="k" style="margin-top:3pt">The model line: the level at the start of every bar</span>'
             f'<table class="t cc" style="margin-top:1pt;font-size:8.6pt">{bar_level_rows()}</table>'
             f'<p class="small" style="margin:1pt 0 2pt;font-size:8.6pt">The line never falls. It ends at 112 (ff) at the end of bar 16. The · means a level between two marks.</p>'
             f'<span class="k" style="margin-top:3pt">My volume line: draw it, then fill in my points</span>'
             f'<div style="margin:1pt auto 2pt;width:60%">{D.body_svg(ramp_body(1600, "ramp blank page", blank=True))}</div>'
             f'<table class="t cc" style="margin-top:1pt"><tr><th>Point</th><th>1</th><th>2</th><th>3</th><th>4</th><th>5</th></tr>'
             f'<tr><td><b>Bar position</b></td><td style="height:19pt"></td><td></td><td></td><td></td><td></td></tr>'
             f'<tr><td><b>Level</b></td><td style="height:19pt"></td><td></td><td></td><td></td><td></td></tr></table>')
    return D.page("Dynamics and automation", "STUDENT", "Class 3", inner, n, wm, name=True, key="dynamics")


def mix_page(n, wm=False):
    def box(title, items, acc=False):
        return (f'<div class="box{" acc-b" if acc else ""}" style="padding:5pt 9pt"><span class="k">{title}</span>'
                + "".join(D.chk(c, 11, "font-size:10pt;line-height:1.3;margin-bottom:3pt") for c in items) + '</div>')
    inner = (f'<p style="margin:0 0 5pt;font-size:10.2pt;line-height:1.36">Step 6: shape the sound, continued. A mix makes every layer clear and the ending strong. Work through the boxes with headphones, '
             f'then check each one off.</p>'
             f'<div class="cols" style="gap:10pt;align-items:flex-start"><div>'
             + box("The ostinato", ["The motif is steady and clear in every section.", "Every note matches the chart, and nothing has a gap at a barline.",
                                    "The bell is never fully hidden by another layer."], True)
             + '<div style="height:6pt"></div>'
             + box("Layers and answer", ["I can find every layer on my layer map by listening.", "The answer plays in the bell’s rests and sounds like a reply.",
                                         "If I cannot hear a layer, I make another one quieter instead of making it louder."])
             + '</div><div>'
             + box("Automation", ["My volume line starts at pp and ends at ff, and it never falls.", "The crescendo is smooth: the points are joined by straight lines, with no jumps.",
                                  "The loudest part is the end of the finale, not by accident."], True)
             + '<div style="height:6pt"></div>'
             + box("Levels", ["The master meter never reaches 0 dBFS; I leave room to spare.", "The low bell and pad do not make the mix muddy.",
                              "I listened at a normal volume, not only loud."])
             + '</div></div>'
             f'<div class="box" style="margin-top:6pt;padding:5pt 9pt"><span class="k">The listening test</span><p style="margin:0 0 3pt;font-size:10pt;line-height:1.36">Play the whole piece with your eyes closed and '
             f'rate each part from 1 (weak) to 5 (very strong). Does the ostinato stay steady? Can you hear each layer join? Does the crescendo feel smooth? Write what you hear:</p>'
             f'<div class="fl" style="margin:2pt 0;font-size:10pt"><b>Ostinato:</b><span></span><b>Layers:</b><span></span><b>Crescendo:</b><span></span></div></div>'
             f'<div class="box acc-b" style="margin-top:6pt;padding:5pt 9pt"><span class="k">Bounce</span>'
             + "".join(D.chk(c, 11, "font-size:10pt;margin-bottom:3pt") for c in [
                 "The bounce starts at bar 1 and ends at the planned length (16 bars; check the seconds for my tempo on page " + str(pg("timing")) + ").",
                 "MP3 or WAV bounced, and the .logicx project zipped.", f"Both files named {FILE_NAME}."]) + '</div>'
             f'<span class="k" style="margin-top:6pt">What I changed after the listening test</span>' + D.lines(7, 24))
    return D.page("Mix checklist", "STUDENT", "Class 3", inner, n, wm, name=True, key="mix")


# ================================================================ worked example (2 pages)
def ex_len_rows():
    return "".join(f"<tr><td><b>{t}</b></td><td>{dec(bar_len(t), 3)}</td><td>{dec(SEC_BARS * bar_len(t), 3)}</td><td>{dec(ARR_BARS * bar_len(t), 3)}</td></tr>" for t in LEN_TEMPOS)


def ex_layer_rows():
    rows = []
    for nm, spans in ARR_ROWS:
        sh = SHIFT_OF[nm]
        names = f"{midi_name(PAD_MIDI)} held" if nm == "PAD" else " ".join(midi_name(m + (sh or 0)) for _, m, _, _ in MOTIF)
        rows.append(f"<tr><td><b>{nm.title()}</b></td><td>{spans_text(spans)}</td><td class='l'>{names}</td></tr>")
    return "".join(rows)


def ex_point_rows():
    return "".join(f"<tr><td><b>{i + 1}</b></td><td>{p}</td><td>{v}</td><td>{mark_of(v)}</td><td>{exact(start_s(EX_BPM, p))}</td></tr>" for i, (p, v) in enumerate(POINTS))


def example_page(n, wm=False):
    inner = (f'<style>table.ec td {{ text-align: center; }}</style>'
             f'<p style="margin:0 0 4pt;font-size:10pt">An <b>invented plan on paper</b>: a piece at {EX_BPM} BPM from the four-note motif. No audio is included. '
             f'Student pieces will differ. Page 1 of 2: the plan, the timing and the layer map.</p>'
             f'<div class="cols" style="gap:10pt;align-items:flex-start"><div class="box"><span class="k">1 · A weak plan</span><p style="margin:0;font-size:10.2pt">{EX_WEAK}</p>'
             f'<p style="margin:3pt 0 0;font-size:9.2pt">It names no tempo, no length, no key, no layers and no dynamics.</p></div>'
             f'<div class="box acc-b"><span class="k">2 · A clear plan</span><p style="margin:0;font-size:8.6pt;line-height:1.28">{EX_STRONG}</p></div></div>'
             f'{D.H2("3 · The timing at three tempos")}'
             f'<div class="cols" style="gap:10pt;align-items:flex-start"><div style="flex:0 0 3.6in"><table class="t ec" style="font-size:8.8pt;line-height:1.14"><tr><th>BPM</th><th>One bar (s)</th><th>4-bar section (s)</th><th>16-bar form (s)</th></tr>{ex_len_rows()}</table></div>'
             f'<p style="margin:0;font-size:8.8pt;line-height:1.3">At {EX_BPM} BPM one beat is 60 ÷ {EX_BPM} = {dec(EX_BEAT_S, 3)} s and one bar is 3 × 60 ÷ {EX_BPM} = {fmt(EX_BAR_S)} s, so 16 bars last {fmt(ARR_BARS * EX_BAR_S)} s. '
             f'The same 16 bars last {fmt(ARR_BARS * bar_len(72))} s at 72 BPM and {fmt(ARR_BARS * bar_len(120))} s at 120 BPM. The sections start at '
             f'{", ".join(exact(start_s(EX_BPM, a)) for _, a, _ in ARR_SECTIONS)} seconds.</p></div>'
             f'{D.H2("4 · The layers: which bars, which notes, and the map")}'
             f'<table class="t ec" style="font-size:8.8pt;line-height:1.14"><tr><th>Layer</th><th>Bars it plays</th><th>Notes it plays</th></tr>{ex_layer_rows()}</table>'
             f'<p style="margin:2pt 0 0;font-size:8.8pt;line-height:1.3">The motif is Bb4, A4, Bb4, G4 (MIDI {", ".join(str(m) for _, m, _, _ in MOTIF)}). The celesta moves it +12 and the low bell −12; the answer moves it {sgn(SHIFT)}, '
             f'which gives G4, F#4, G4, E4 (MIDI {", ".join(str(m) for _, m, _, _ in MOTIF_E)}). The pad holds {midi_name(PAD_MIDI)} for 3 beats in each of its bars. '
             f'The layers play {sum(len(bars_of(r)) for r in ARR_LAYERS)} bars in all.</p>'
             f'<div style="margin:3pt auto 3pt;width:66%">{D.body_svg(layers_body(1600, "layers page"))}</div>'
             f'<div class="box" style="margin-top:4pt;padding:4pt 9pt"><span class="k">What to notice</span><p style="margin:0;font-size:9.2pt;line-height:1.3">{EX_NOTE[0].upper() + EX_NOTE[1:]}.</p></div>')
    return D.page("Worked example · the plan, the timing and the layers", "EXAMPLE", "Teacher", inner, n, wm, ak=True, key="example")


def example2_page(n, wm=False):
    qs = " ".join(f"{i + 1}. {q}" for i, q in enumerate(EX_QUESTIONS))
    inner = (f'<p style="margin:0 0 3pt;font-size:10pt">The same piece, page 2 of 2: the motif in two keys, the volume line, then the moments to point out.</p>'
             f'{D.H2("5 · The motif in two keys")}'
             f'<div style="margin:1pt auto 3pt;width:62%">{D.body_svg(motif_body(1600, "motif page"))}</div>'
             f'<p style="margin:0;font-size:9.6pt;line-height:1.34">{ARR_BARS} bars × {fmt(EX_BAR_S)} s = {fmt(ARR_BARS * EX_BAR_S)} s. The solo starts at {exact(start_s(EX_BPM, 1))} s, the build at {exact(start_s(EX_BPM, 5))} s, '
             f'the call and response at {exact(start_s(EX_BPM, 9))} s and the finale at {exact(start_s(EX_BPM, 13))} s. The bell plays the first key and the answer plays the second.</p>'
             f'{D.H2("6 · The volume line")}'
             f'<div style="margin:1pt auto 3pt;width:90%">{D.body_svg(ramp_body(1600, "ramp page"))}</div>'
             f'<div class="cols" style="gap:10pt;align-items:flex-start"><div style="flex:0 0 3.6in"><table class="t ec" style="font-size:8.8pt;line-height:1.14"><tr><th>Point</th><th>Bar position</th><th>Level</th><th>Mark</th><th>Time (s)</th></tr>{ex_point_rows()}</table></div>'
             f'<p style="margin:0;font-size:8.8pt;line-height:1.3">Bar position 17 is the end of bar 16, at {exact(start_s(EX_BPM, 17))} s. The line stays at 32 until bar 5, rises 8 per bar to 64 at bar 9 and 4 per bar to 80 at bar 13; '
             f'the crescendo in bars 13 to 16 rises 32 levels in 4 bars, 8 per bar, and lasts {fmt(SEC_BARS * EX_BAR_S)} s.</p></div>'
             f'<div class="box" style="margin-top:5pt"><span class="k">7 · Three feedback questions (invented)</span><p style="margin:0;font-size:10pt;line-height:1.36">{qs}</p></div>'
             f'<div class="box acc-b" style="margin-top:5pt"><span class="k">8 · Moments to point out in class</span><ul style="margin:0">'
             f'<li style="font-size:10pt;margin-bottom:2pt">The same one-bar motif makes every note in the piece, so the note chart explains everything the listener hears.</li>'
             f'<li style="font-size:10pt;margin-bottom:0">At {EX_BPM} BPM a bar is exactly 2 s, so the class can count bars out loud and hear each new layer arrive.</li></ul></div>')
    return D.page("Worked example · the motif and the volume line", "EXAMPLE", "Teacher", inner, n, wm, ak=True, key="example2")


PAGES = {"howto": howto_page, "overview": overview_page, "setup": setup_page, "example": example_page, "example2": example2_page,
         "timing": timing_page, "motif": motif_page, "enter": enter_page, "layers": layers_page, "answer": answer_page, "dynamics": dynamics_page, "mix": mix_page}


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





BADGE = {"timing": "Class 1", "motif": "Class 1", "enter": "Class 1", "layers": "Class 2", "answer": "Class 2", "dynamics": "Class 3", "mix": "Class 3",
         "present": f"Classes {CLASSES - 1}–{CLASSES}"}


FORBIDDEN_WORDS = ("cham" + "pagne", "toast", "cheers", "wine", "beer", "cocktail", "alcohol", "bub" + "bly", "church", "prayer", "pray ", "blessing", "holy", "sacred",
                   "religio", "god ", "santa", "christmas", "hanukkah", "chanukah", "kwanzaa", "holiday", "sleigh", "reindeer", "ornament", "elf ", "elves", "lyrics were", "sing along")
EXPECT_STEP = {"timing": {1}, "motif": {2}, "enter": {3}, "layers": {4}, "answer": {5}, "dynamics": {6}, "mix": {6}}


def svg_count(svg, cls):
    return len(re.findall(rf'class="{cls}"', svg))


def verify_content():
    errs = []
    counts = dict(goals=(GOALS, 4), vocab=(VOCAB, 8), reqs=(REQS, 7), steps=(STEPS, 7), tips=(TIPS, 4), check=(CHECK, 6),
                  rubric=(RUBRIC, 5), struggles=(STRUGGLES, 4), resources=(RESOURCES, 5), slides=(SLIDES, 17), plan=(PLAN, 25),
                  logic=(LOGIC_REF, 9), motif=(MOTIF, 4), motif_e=(MOTIF_E, 4), arrange=(ARR_ROWS, 5), sections=(ARR_SECTIONS, 4), points=(POINTS, 5), dyn=(DYN, 6))
    for nm, (lst, nexp) in counts.items():
        if len(lst) != nexp:
            errs.append(f"{nm}: {len(lst)} items, expected {nexp}")
    if RUBRIC_TOTAL != 25 or LEVELS != [1, 2, 3, 4, 5] or len(RUBRIC_SHORT) != 5:
        errs.append("rubric is /25, levels 1-5")
    if FILE_NAME not in CHECK[2]:
        errs.append("file name format must be on the checklist")
    if [w for w, _ in VOCAB] != ["Ostinato", "Motif", "Layer", "Octave", "Dynamics", "Crescendo", "Automation", "Call and response"]:
        errs.append("vocabulary: ostinato, motif, layer, octave, dynamics, crescendo, automation, call and response")
    if set(TAGS) & {"Holiday", "Student Practice", "Theme", "Seasonal"} or "Performing Arts" in SUBJECTS:
        errs.append("tags and subjects must not be headings")
    if len(LISTING_TITLE) > 80 or "Logic Pro" not in LISTING_TITLE[:30]:
        errs.append("listing title: at most 80 characters, 'Logic Pro' in the first 30")
    for w in ("new year", "winter", "holiday", "christmas", "hanukkah", "chanukah", "sleigh", "carol", "snow", "eve ", "bells"):
        if w in LISTING_TITLE.lower():
            errs.append(f"the listing title must not hold the seasonal word {w}")
    if len(STEP_NAMES) != len(STEPS) or any(not s.startswith(f"<b>{nm}</b>") for s, nm in zip(STEPS, STEP_NAMES)):
        errs.append("STEPS must start with the bold names in STEP_NAMES (the pages cite them)")
    # ---- the tempo arithmetic for 3/4, by hand first
    if [spb(b) for b in (120, 90, 100, 80, 72, 144)] != [Fraction(1, 2), Fraction(2, 3), Fraction(3, 5), Fraction(3, 4), Fraction(5, 6), Fraction(5, 12)]:
        errs.append("seconds per beat = 60 / BPM: 0.5 at 120, 0.6667 at 90, 0.6 at 100, 0.75 at 80, 0.8333 at 72, 0.4167 at 144")
    if [bar_len(b) for b in TEMPOS] != [Fraction(5, 2), Fraction(9, 4), Fraction(2), Fraction(9, 5), Fraction(3, 2), Fraction(5, 4)]:
        errs.append("seconds per bar of 3/4 = 180 / BPM: 2.5, 2.25, 2, 1.8, 1.5, 1.25 at 72, 80, 90, 100, 120, 144 BPM")
    if [eighth_len(b) for b in TEMPOS] != [Fraction(5, 12), Fraction(3, 8), Fraction(1, 3), Fraction(3, 10), Fraction(1, 4), Fraction(5, 24)]:
        errs.append("seconds per eighth note = 30 / BPM")
    for b in TEMPOS:
        if bar_len(b) != BEATS_BAR * spb(b) or bar_len(b) != EIGHTHS_BAR * eighth_len(b) or abs(float(bar_len(b)) - 180.0 / b) > 1e-12 or abs(float(eighth_len(b)) - 30.0 / b) > 1e-12 or \
           abs(float(spb(b)) - 60.0 / b) > 1e-12:
            errs.append(f"a bar of 3/4 is 3 beats and 6 eighth notes at {b} BPM")
        if SEC_BARS * bar_len(b) != Fraction(720, b) or ARR_BARS * bar_len(b) != Fraction(2880, b):
            errs.append(f"4 bars = 720 / BPM and 16 bars = 2880 / BPM at {b} BPM")
    if [dec(spb(b), 3) for b in TEMPOS] != ["0.833", "0.750", "0.667", "0.600", "0.500", "0.417"] or \
       [dec(eighth_len(b), 4) for b in TEMPOS] != ["0.4167", "0.3750", "0.3333", "0.3000", "0.2500", "0.2083"] or \
       [dec(bar_len(b), 3) for b in TEMPOS] != ["2.500", "2.250", "2.000", "1.800", "1.500", "1.250"]:
        errs.append("seconds per beat, eighth note and bar, rounded half up")
    if [dec(SEC_BARS * bar_len(b), 3) for b in TEMPOS] != ["10.000", "9.000", "8.000", "7.200", "6.000", "5.000"] or \
       [dec(ARR_BARS * bar_len(b), 3) for b in TEMPOS] != ["40.000", "36.000", "32.000", "28.800", "24.000", "20.000"]:
        errs.append("4-bar and 16-bar lengths at the six tempos")
    want = {72: ["20.000", "30.000", "40.000", "80.000"], 90: ["16.000", "24.000", "32.000", "64.000"], 120: ["12.000", "18.000", "24.000", "48.000"]}
    for t in LEN_TEMPOS:
        if [dec(nb * bar_len(t), 3) for nb in LEN_BARS] != want[t] or [nb * bar_len(t) for nb in LEN_BARS] != [Fraction(180 * nb, t) for nb in LEN_BARS]:
            errs.append(f"form lengths for 8, 12, 16 and 32 bars at {t} BPM")
    if rnd(Fraction(5, 2), 0) != 3 or dec(Fraction(5, 12), 4) != "0.4167" or dec(Fraction(5, 6), 3) != "0.833":
        errs.append("round half up")
    if [exact(start_s(EX_BPM, a)) for _, a, _ in ARR_SECTIONS] != ["0", "8", "16", "24"] or start_s(EX_BPM, 17) != 32 or ARR_BARS * EX_BAR_S != 32 or EX_BAR_S != 2 or SEC_BARS * EX_BAR_S != 8:
        errs.append("90 BPM: a bar is 2 s, sections start at 0, 8, 16 and 24 s, 16 bars = 32 s")
    # ---- the motif: two public scores agree on G minor, 3/4, Bb4 (quarter) A4 (eighth) Bb4 (eighth) G4 (quarter)
    if [(n_, m) for n_, m, _, _ in MOTIF] != [("Bb4", 70), ("A4", 69), ("Bb4", 70), ("G4", 67)]:
        errs.append("the motif is Bb4 (70), A4 (69), Bb4 (70), G4 (67)")
    if [(n_, m) for n_, m, _, _ in MOTIF_E] != [("G4", 67), ("F#4", 66), ("G4", 67), ("E4", 64)]:
        errs.append("the second key is G4 (67), F#4 (66), G4 (67), E4 (64)")
    for notes in (MOTIF, MOTIF_E):
        for n_, m, _, _ in notes:
            if midi_name(m) != n_:
                errs.append(f"note name {n_} does not match MIDI number {m} (middle C = 60 = C4)")
        if [st for _, _, st, _ in notes] != [0, 2, 3, 4] or [ln for _, _, _, ln in notes] != [2, 1, 1, 2] or sum(ln for _, _, _, ln in notes) != EIGHTHS_BAR:
            errs.append("the motif lasts 6 eighth-note slots: 2 + 1 + 1 + 2, starting at 0, 2, 3 and 4")
        if any(st + ln != nxt for (_, _, st, ln), (_, _, nxt, _) in zip(notes, notes[1:])):
            errs.append("the motif's notes follow each other with no gap or overlap")
    if LEN_BEATS != [Fraction(ln, 2) for _, _, _, ln in MOTIF] or sum(LEN_BEATS) != BEATS_BAR:
        errs.append("the motif's lengths in beats (1, 1/2, 1/2, 1) add up to 3 beats, one bar of 3/4")
    if [(a[1] - SHIFT, a[2], a[3]) for a in MOTIF_E] != [(b[1], b[2], b[3]) for b in MOTIF] or SHIFT != -3:
        errs.append("every note of the second key is exactly 3 semitones below the original, with the same start and length")
    if intervals(MOTIF) != [-1, 1, -3] or intervals(MOTIF_E) != [-1, 1, -3]:
        errs.append("intervals of the motif: -1, +1, -3 in both keys")
    if sum(intervals(MOTIF)) != MOTIF[-1][1] - MOTIF[0][1] or max(m for _, m, _, _ in MOTIF) - min(m for _, m, _, _ in MOTIF) != 3 or IVL_NAME[3] != "minor third" or IVL_NAME[1] != "minor second":
        errs.append("the intervals add up to the last note minus the first (-3); the motif spans a minor third (3 semitones)")
    if len({m for _, m, _, _ in MOTIF}) != 3:
        errs.append("four notes, three different pitches")
    if abs(freq(69) - 440) > 1e-9 or [hz1(m) for _, m, _, _ in MOTIF] != ["466.2", "440.0", "466.2", "392.0"] or [hz1(m) for _, m, _, _ in MOTIF_E] != ["392.0", "370.0", "392.0", "329.6"]:
        errs.append("frequencies 440 x 2^((m - 69) / 12): Bb4 466.2, A4 440.0, G4 392.0, F#4 370.0, E4 329.6 Hz")
    if abs(freq(82) / freq(70) - 2) > 1e-12 or abs(freq(58) / freq(70) - 0.5) > 1e-12 or hz1(82) != "932.3" or hz1(58) != "233.1" or abs(freq(60) - 261.6256) > 1e-3:
        errs.append("an octave (12 semitones) doubles the frequency: Bb5 = 932.3 Hz, Bb3 = 233.1 Hz; middle C = 261.63 Hz")
    if (SEMITONE := 2 ** (1 / 12)) and abs(SEMITONE ** 12 - 2) > 1e-12:
        errs.append("a semitone is 2^(1/12)")
    shifts = {sh: [midi_name(m + sh) for _, m, _, _ in MOTIF] for sh in (-3, -5, 2)}
    if shifts != {-3: ["G4", "F#4", "G4", "E4"], -5: ["F4", "E4", "F4", "D4"], 2: ["C5", "B4", "C5", "A4"]}:
        errs.append("other keys: -3 G4 F#4 G4 E4, -5 F4 E4 F4 D4, +2 C5 B4 C5 A4")
    # ---- the layer map
    for nm, spans in ARR_ROWS:
        last = 0
        for a, b in spans:
            if not (1 <= a <= b <= ARR_BARS) or a <= last:
                errs.append(f"layer {nm}: bars {a}-{b} outside 1-{ARR_BARS} or out of order")
            last = b
    if ARR_LAYERS != ["BELL", "CELESTA", "PAD", "LOW BELL", "ANSWER"] or [(n_, a, b) for n_, a, b in ARR_SECTIONS] != [("SOLO", 1, 4), ("BUILD", 5, 8), ("ANSWER", 9, 12), ("FINALE", 13, 16)]:
        errs.append("layers and sections of the map")
    per_bar = [len(layers_in_bar(b)) for b in range(1, ARR_BARS + 1)]
    if per_bar != [1, 1, 1, 1, 3, 3, 3, 3, 2, 2, 2, 2, 4, 4, 4, 4] or sum(per_bar) != 40 or [len(bars_of(r)) for r in ARR_LAYERS] != [14, 8, 12, 4, 2] or sum(len(bars_of(r)) for r in ARR_LAYERS) != 40:
        errs.append("layers sounding per bar 1,1,1,1,3,3,3,3,2,2,2,2,4,4,4,4 = 40 layer-bars = 14 + 8 + 12 + 4 + 2")
    if bars_of("ANSWER") != [10, 12] or [b for b in range(9, 13) if b not in bars_of("BELL")] != [10, 12] or set(bars_of("ANSWER")) & set(bars_of("BELL")):
        errs.append("the answer plays exactly in the bell's rests, bars 10 and 12")
    first_seen = {}
    for sec, a, b in ARR_SECTIONS:
        new = [r for r in ARR_LAYERS if r not in first_seen and any(x in bars_of(r) for x in range(a, b + 1))]
        if not new:
            errs.append(f"the {sec} section adds no new layer (the deck says a new layer joins every 4 bars)")
        for r in new:
            first_seen[r] = sec
    if first_seen != {"BELL": "SOLO", "CELESTA": "BUILD", "PAD": "BUILD", "ANSWER": "ANSWER", "LOW BELL": "FINALE"}:
        errs.append("layers join: bell in the solo, celesta and pad in the build, answer in the answer section, low bell in the finale")
    lm, lb, cr, mp_ = layers_body(1600, "l check")[0], layers_body(1600, "lb check", blank=True)[0], callresp_body(1500, "c check")[0], motif_body(1600, "m check")[0]
    if svg_count(lm, "block") != sum(len(s) for _, s in ARR_ROWS) or svg_count(lm, "cnt") != ARR_BARS or svg_count(lb, "block") != 0 or svg_count(lb, "cnt") != 0:
        errs.append(f"the layer map drawing must hold {sum(len(s) for _, s in ARR_ROWS)} blocks and {ARR_BARS} layer counts; the blank map has none")
    drawn = [int(x) for x in re.findall(r'class="cnt"[^>]*>(\d+)<', lm)]
    if drawn != per_bar:
        errs.append(f"the drawn layer counts {drawn} do not match the data {per_bar}")
    if len(re.findall(r'y="[\d.]+" width="[\d.]+" height="44" rx="8"', lm)) != 4 or len(re.findall(r">(?:BELL|CELESTA|PAD|LOW BELL|ANSWER)<", lm)) != 5:
        errs.append("the layer map must show 4 section bars and 5 layer names")
    if svg_count(cr, "block") != 5:
        errs.append("bars 9 to 12 drawing: bell 2 blocks, answer 2 blocks and 1 pad block")
    if svg_count(mp_, "nt") != 8 or svg_count(mp_, "ivl") != 6 or [x for x in re.findall(r'class="ivl">([^<]+)<', mp_)] != ["−1", "+1", "−3"] * 2:
        errs.append("the note chart drawing must hold 8 notes (4 in each key) and the interval labels −1, +1, −3 twice")
    # ---- the dynamics ramp
    if [(n_, v) for n_, _, v in DYN] != [("pp", 32), ("p", 48), ("mp", 64), ("mf", 80), ("f", 96), ("ff", 112)]:
        errs.append("dynamic marks pp 32, p 48, mp 64, mf 80, f 96, ff 112 (Logic Pro 9 defaults as listed on Wikipedia's Dynamics page)")
    if POINTS != [(1, 32), (5, 32), (9, 64), (13, 80), (17, 112)]:
        errs.append("automation points: bar 1 = 32, bar 5 = 32, bar 9 = 64, bar 13 = 80, end of bar 16 (17) = 112")
    if [exact(level_at(b)) for b in range(1, ARR_BARS + 1)] != ["32", "32", "32", "32", "32", "40", "48", "56", "64", "68", "72", "76", "80", "88", "96", "104"] or level_at(17) != 112:
        errs.append("levels at the start of bars 1 to 16: 32 x5, 40, 48, 56, 64, 68, 72, 76, 80, 88, 96, 104; 112 at the end")
    for i in range(0, 161):                # independent float method on a fine grid: straight lines, never falling
        pos = 1 + i * 0.1
        pts = POINTS
        k = max(j for j in range(len(pts) - 1) if pts[j][0] <= pos) if pos < 17 else len(pts) - 2
        y = pts[k][1] + (pts[k + 1][1] - pts[k][1]) * (pos - pts[k][0]) / (pts[k + 1][0] - pts[k][0])
        if abs(float(level_at(Fraction(i, 10) + 1)) - y) > 1e-9 or (i and level_at(Fraction(i, 10) + 1) < level_at(Fraction(i - 1, 10) + 1)):
            errs.append(f"the automation line at position {pos:.1f}: exact and float disagree, or it falls")
    if (level_at(17) - level_at(13)) / 4 != 8 or level_at(13) != LEVEL_OF["mf"] or level_at(17) != LEVEL_OF["ff"] or level_at(16) != 104:
        errs.append("the crescendo: bars 13 to 16 rise from 80 (mf) to 112 (ff), 8 per bar, 104 at bar 16")
    if [mark_of(level_at(b)) for b in (1, 5, 7, 9, 13, 15)] != ["pp", "pp", "p", "mp", "mf", "f"]:
        errs.append("marks at bars 1, 5, 7, 9, 13, 15: pp, pp, p, mp, mf, f")
    rp, rb = ramp_body(1600, "r check")[0], ramp_body(1600, "rb check", blank=True)[0]
    if svg_count(rp, "pt") != len(POINTS) or svg_count(rb, "pt") != 0 or len(re.findall(r'<polyline points="[^"]*" fill="none" stroke="#000" stroke-width="7"', rp)) != 1:
        errs.append(f"the dynamics drawing must hold {len(POINTS)} automation points on one line; the blank one has none")
    # ---- Logic wording: newer tools are hedged
    for nm, txt in LOGIC_REF:
        if any(w in txt for w in ("Alchemy", "automation (look", "loop option", "transpose control", "help tag", "velocity display", "Reading and writing")) and "if your version" not in txt.lower() and "look for" not in txt.lower():
            errs.append(f"Logic reference '{nm}' must hedge a newer or version-specific tool with 'if your version'")
    joined = " ".join(t for _, t in LOGIC_REF)
    for w in ("Piano Roll", "velocity", "automation", "Volume", "Mixer", "Bounce", "transpose", "loop", "bell", "3/4", "Alchemy"):
        if w.lower() not in joined.lower():
            errs.append(f"the Logic quick reference must name {w}")
    # ---- the worked example
    if EX_BPM != 90:
        errs.append("the example is at 90 BPM")
    for need in ("3/4 at 90 BPM", "60 ÷ 90 = 0.667 seconds", "180 ÷ 90 = 2 seconds", "16 bars = 32 seconds", "bars 1 to 4", "bars 5 to 8", "bars 9 to 12", "bars 13 to 16", "5 layers",
                 "Bb4, A4, Bb4, G4", "G4, F#4, G4, E4", "3 semitones lower", "pp (32)", "mp (64)", "mf (80)", "ff (112)", "bar 9", "bar 13", "end of bar 16"):
        if need not in EX_STRONG:
            errs.append(f"the clear plan must say '{need}'")
    # ---- no forbidden themes in any text a buyer reads
    allt = " ".join([THEME, BUILD_NOTE, OVERVIEW, " ".join(GOALS), " ".join(f"{a} {b}" for a, b in VOCAB), " ".join(REQS), " ".join(STEPS), " ".join(TIPS), " ".join(CHECK),
                     " ".join(d for _, ds in RUBRIC for d in ds), TN_REINFORCES, " ".join(STRUGGLES), VAR_EASY, VAR_HARD, " ".join(f"{a} {b}" for a, b in RESOURCES), TN_NOTE,
                     " ".join(GRADING), " ".join(d["do"] for d in PACING), SONG_NOTE, MOTIF_NOTE, " ".join(t for _, t in LOGIC_REF), EX_STRONG, EX_NOTE, " ".join(EX_QUESTIONS),
                     " ".join(" ".join((s[2], s[3], s[4])) for s in SLIDES)]).lower()
    for w in FORBIDDEN_WORDS:
        if re.search(rf"\b{re.escape(w.strip())}\b", allt):
            errs.append(f"no alcohol, religious or holiday wording in a secular kit: '{w.strip()}'")
    for w in ("colour", "favour", "centre", "licence", "grey", "metre ", "organis", "recognis", "practise", "analyse", "whilst", "milli-second", "equalis", "normalis", "behaviour", "sulph", "crotchet", "quaver"):
        if w in allt:
            errs.append(f"US spelling: '{w}'")
    for w in ("qa ", "inspector", "verified by", "--check", "gen.py"):
        if w in allt.replace("verified before", ""):
            errs.append(f"internal wording in buyer-facing text: '{w}'")
    for w in ("wilhousky", "imslp", "wikipedia", "commons"):
        if w in allt:
            errs.append(f"buyer-facing text must not name a source or the 1936 arranger ({w})")
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
    for need, key in ((f"page {pg('motif')}", 4), (f"page {pg('enter')}", 4), (f"page {pg('timing')}", 5), (f"page {pg('logicref')}", 6), (f"page {pg('enter')}", 6),
                      (f"page {pg('enter')}", 7), (f"page {pg('layers')}", 8), (f"page {pg('answer')}", 9), (f"page {pg('layers')}", 10), (f"page {pg('dynamics')}", 11),
                      (f"page {pg('logicref')}", 12), (f"page {pg('mix')}", 12)):
        if need not in SLIDES[key][4]:
            errs.append(f"slide {key + 1} notes must name {need}")
    for i, s in enumerate(SLIDES, start=1):
        errs += step_ref_errors(" ".join((s[2], s[3], s[4])), f"slide {i}")
    if [s[0] for s in SLIDES] != [1] * 8 + [2] * 3 + [3] * 6 or SLIDES[3][1] != "days":
        errs.append("deck classes: slides 1-8 Class 1, 9-11 Class 2, 12-17 Class 3; slide 4 is the 'days' slide (it gets the Classes 1-3 badge)")
    if [d["slides"] for d in PACING] != [(1, 8), (9, 11), (12, 17)]:
        errs.append("pacing slide slots 1-8, 9-11, 12-17")
    # ---- the hero art, used whole: its pixels sit inside the viewBox with room to spare, and 40 units from the file's own edges
    hp = os.path.join(HERE, "art", "hero.png")
    if not os.path.exists(hp):
        errs.append("art/hero.png is missing")
    else:
        x0, y0, x1, y1 = alpha_bbox(hp)
        if min(x0 - HX, y0 - HY, HX + HW - 1 - x1, HY + HH - 1 - y1) < 40:
            errs.append(f"hero art {x0, y0, x1, y1} is closer than 40 units to the viewBox {HX, HY, HX + HW, HY + HH}")
        if min(x0, y0, 1399 - x1, 1399 - y1) < 40:
            errs.append(f"hero art {x0, y0, x1, y1} comes within 40 px of an edge of its file")
    if "--check" in sys.argv:
        errs += drawing_edge_errors() + footer_gap_errors()
    return errs


COUNT_WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "twelve": 12, "sixteen": 16}


def count_claim_errors(texts):
    """Every stated number of notes, bars or layer-bars equals the drawings: 'N notes' is 4 (one motif) or 8 (two keys); 'N bars' is a bar count the kit uses; 'N layers' is checked
    by layer_count_errors."""
    errs = []
    allowed_bars = {0, 1, 2, 3, 4, 5, 8, 12, 14, 15, 16, 20, 32, 40}      # 0: a table cell next to the word 'bars' in the flattened page text
    for label, t in texts:
        for m in re.finditer(r"\b(\d+|four|eight) notes\b", t):
            w = m.group(1).lower()
            v = int(w) if w.isdigit() else COUNT_WORDS[w]
            if v not in (4, 8):
                errs.append(f"{label}: '{m.group(0)}' but the motif has 4 notes (8 in two keys)")
        for m in re.finditer(r"(?<![\d.–])\b(\d+) bars\b", t):
            if int(m.group(1)) not in allowed_bars:
                errs.append(f"{label}: {t[max(0, m.start() - 30):m.end()]!r} is not a bar count from the plan")
        for m in re.finditer(r"\b(\d+)-bar\b", t):
            if int(m.group(1)) not in allowed_bars:
                errs.append(f"{label}: '{m.group(0)}' is not a bar count from the plan")
        for m in re.finditer(r"\b(\d+) sections\b", t):
            if int(m.group(1)) != len(ARR_SECTIONS):
                errs.append(f"{label}: '{m.group(0)}' but the form has {len(ARR_SECTIONS)} sections")
        for m in re.finditer(r"\b(\d+) points\b", t):
            if int(m.group(1)) != len(POINTS):
                errs.append(f"{label}: '{m.group(0)}' but the volume line has {len(POINTS)} points")
    return errs


C1_BANNED = r"\blayers?\b|\bautomation\b|\bcrescendo\b|\bdynamics\b|\bcall and response\b|\bvolume\b|\boctaves?\b|\bvelocity\b|\banswer\b"
C2_BANNED = r"\bdynamics\b|\bautomation\b|\bcrescendo\b|\bvolume\b|\bmix\b|\bpp\b|\bff\b|\bvelocity\b|\bmf\b"


def class_step_errors():
    """A deck slide badged Class 2 does not name dynamics, automation, volume or the mix (the pacing table puts them in Class 3), and a Class 1 slide does not teach layering, the answer or
    dynamics. Title, bullet and 'days' slides may preview the whole project."""
    errs = []
    for i, s in enumerate(SLIDES, start=1):
        shown = " ".join((s[2], s[3] if s[1] != "pic" else ""))
        if s[0] == 2 and re.search(C2_BANNED, shown, re.I):
            errs.append(f"deck slide {i} is badged Class 2 but names dynamics, automation, volume or mix content, which the pacing page assigns to Class 3")
        if s[0] == 1 and re.search(C1_BANNED, shown, re.I) and s[1] not in ("title", "bullets", "days"):
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
    for need in ("No audio, recordings or words", "invented plan on paper", "if your version", "ostinato", "Shchedryk", "public domain", "3/4", "semitone", "180 ÷ BPM", "60 ÷ BPM", "30 ÷ BPM",
                 "crescendo", "automation", "velocity", "call and response", "answer", "octave", "layer", "dynamics", "pp", "ff", "0 dBFS", "interval", "minor third", "E minor", "G minor",
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
    for w in ("colour", "favour", "centre", "licence", "grey", "metre", "organis", "recognis", "practise", "analyse", "whilst", "milli-second", "colourful", "equalis", "crotchet"):
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
        row = f"{bpm} {dec(spb(bpm), 3)} {dec(eighth_len(bpm), 4)} {dec(bar_len(bpm), 3)} {dec(SEC_BARS * bar_len(bpm), 3)} {dec(ARR_BARS * bar_len(bpm), 3)}"
        if row not in rc:
            errs.append(f"timing page: row '{row}' is not printed")
    for t in LEN_TEMPOS:
        row = f"{t} " + " ".join(dec(nb * bar_len(t), 3) for nb in LEN_BARS)
        if row not in rc:
            errs.append(f"timing page: form-length row '{row}' is not printed")
    for need in ("Seconds per beat = 60 ÷ BPM", "Seconds per eighth note = 30 ÷ BPM", "Seconds per bar = 180 ÷ BPM = 3 beats = 6 eighth notes", "60 ÷ 90 = 0.667 s per beat", "180 ÷ 90 = 2 s per bar",
                 "Step 1: plan the form", "5 rounds up", "0.4167", "2880 ÷ BPM", "32 seconds at 90 BPM"):
        if need.lower() not in rc.lower():
            errs.append(f"timing page must say '{need}'")
    # ---- the note chart page
    rm = raw("motif")
    for i, ((nm, m, _, _), (nm2, m2, _, _)) in enumerate(zip(MOTIF, MOTIF_E)):
        row = f"{i + 1} {START_BEAT[i]} {fmt(LEN_BEATS[i])} {nm} {m} {hz1(m)} {nm2} {m2} {hz1(m2)} {sgn(m2 - m)}"
        if row not in rm:
            errs.append(f"note chart page: row '{row}' is not printed")
    for i, v in enumerate(intervals(MOTIF)):
        row = f"{i + 1} to {i + 2} {MOTIF[i][0]} to {MOTIF[i + 1][0]} {MOTIF_E[i][0]} to {MOTIF_E[i + 1][0]} {sgn(v)} {IVL_NAME[abs(v)]}, {'down' if v < 0 else 'up'}"
        if row not in rm:
            errs.append(f"note chart page: interval row '{row}' is not printed")
    for need in ("Step 2: learn the motif", "G minor", "E minor", "3 lower", "a minor third", "MIDI note 60 is middle C", "440 × 2^((MIDI − 69) ÷ 12)", "−1 + 1 + (−3) = −3", "BAR 1 · G MINOR", "BAR 2 · E MINOR",
                 "Bb means B-flat", "add up to 3 beats", "three different pitches", "SEMITONES"):
        if need.lower() not in rm.lower():
            errs.append(f"note chart page must say '{need}'")
    # ---- the entry page
    re_ = raw("enter")
    for need in ("Step 3: build the ostinato", "Entry log", "Bb, A, Bb, G", "3/4", "quarter note, an eighth note, an eighth note and a quarter note", "one bar"):
        if need.lower() not in re_.lower():
            errs.append(f"entry page must say '{need}'")
    # ---- the layer map page
    rl = raw("layers")
    for nm, spans in ARR_ROWS:
        sh = SHIFT_OF[nm]
        if nm == "PAD":
            row = f"{nm.title()} {spans_text(spans)} {len(bars_of(nm))} one held note {midi_name(PAD_MIDI)} held"
        else:
            row = f"{nm.title()} {spans_text(spans)} {len(bars_of(nm))} {sgn(sh) if sh else '0'} " + " ".join(midi_name(m + (sh or 0)) for _, m, _, _ in MOTIF)
        if row not in rl:
            errs.append(f"layer map page: row '{row}' is not printed")
    for need in ("Step 4: layer it", "5 layers", "four sections of 4 bars", "40 bars in all: 14 + 8 + 12 + 4 + 2", "16 bars at 90 BPM = 32 seconds", "SECONDS", "SOLO · bars 1–4", "FINALE · bars 13–16",
                 "Bb5 is 932.3 Hz", "LAYERS", "My layer map", "doubles the frequency"):
        if need.lower() not in rl.lower():
            errs.append(f"layer map page must say '{need}'")
    # ---- the answer page
    ra = raw("answer")
    for sh, key in ((-3, "E minor"), (-5, "D minor"), (2, "A minor")):
        ms = [m + sh for _, m, _, _ in MOTIF]
        row = f"{sgn(sh)} {key} {' '.join(midi_name(m) for m in ms)} {' '.join(str(m) for m in ms)}"
        if row not in ra:
            errs.append(f"answer page: key row '{row}' is not printed")
    for need in ("Step 5: answer it", "bars 10 and 12", "call and response", "BAR 9 · CALL", "BAR 10 · REPLY", "G4 F#4 G4 E4", "67 66 67 64", "Bb4 A4 Bb4 G4", "70 69 70 67", "Rules for a good answer", "My answer"):
        if need.lower() not in ra.lower():
            errs.append(f"answer page must say '{need}'")
    # ---- the dynamics page
    rd = raw("dynamics")
    row = "Level " + " ".join(exact(level_at(b)) for b in range(1, ARR_BARS + 1))
    if row not in rd:
        errs.append(f"dynamics page: level row '{row}' is not printed")
    for n_, m, v in DYN:
        if f"{n_} {m} {v}" not in rd:
            errs.append(f"dynamics page: mark row '{n_} {m} {v}' is not printed")
    for need in ("Step 6: shape the sound", "(112 − 80) ÷ 4 = 8 levels per bar", "80 at bar 13 and 104 at bar 16", "crescendo", "pp · 32", "ff · 112", "5 points joined by straight lines",
                 "Velocity", "never falls", "automation", "My volume line", "BAR"):
        if need.lower() not in rd.lower():
            errs.append(f"dynamics page must say '{need}'")
    rx = raw("mix")
    if "Step 6: shape the sound, continued" not in rx or "0 dBFS" not in rx:
        errs.append("mix page: Step 6 and the 0 dBFS line")
    # ---- the worked example prints its numbers
    re1 = raw("example") + " " + raw("example2")
    for t in LEN_TEMPOS:
        row = f"{t} {dec(bar_len(t), 3)} {dec(SEC_BARS * bar_len(t), 3)} {dec(ARR_BARS * bar_len(t), 3)}"
        if row not in re1:
            errs.append(f"worked example: timing row '{row}' is not printed")
    for nm, spans in ARR_ROWS:
        sh = SHIFT_OF[nm]
        names = f"{midi_name(PAD_MIDI)} held" if nm == "PAD" else " ".join(midi_name(m + (sh or 0)) for _, m, _, _ in MOTIF)
        row = f"{nm.title()} {spans_text(spans)} {names}"
        if row not in re1:
            errs.append(f"worked example: layer row '{row}' is not printed")
    for i, (p, v) in enumerate(POINTS):
        row = f"{i + 1} {p} {v} {mark_of(v)} {exact(start_s(EX_BPM, p))}"
        if row not in re1:
            errs.append(f"worked example: point row '{row}' is not printed")
    for need in ("60 ÷ 90 = 0.667 s", "3 × 60 ÷ 90 = 2 s", "16 bars last 32 s", "40 s at 72 BPM", "24 s at 120 BPM", "0, 8, 16, 24 seconds", "G4, F#4, G4, E4", "+12", "−12", "−3",
                 "The layers play 40 bars in all", "16 bars × 2 s = 32 s", "at 32 s", "8 per bar", "32 until bar 5"):
        if need.lower() not in re1.lower():
            errs.append(f"worked example must say '{need}'")
    up = open(os.path.join(HERE, "UPLOAD.md"), encoding="utf8").read()
    errs += step_ref_errors(up, "UPLOAD.md")
    errs += count_claim_errors([("UPLOAD.md", up)])
    if "Grades 9-12" not in up or "`9th-grade`, `10th-grade`, `11th-grade`, `12th-grade`" not in up:
        errs.append("UPLOAD.md: grades 9-12 in the description and section 3")
    if "no audio" not in up.lower() or "Open questions" not in up or "Timing numbers" not in up or "Sources and credits" not in up:
        errs.append("UPLOAD.md: must say no audio is included, record the timing numbers checked, the sources and the open questions")
    for need in ("Shchedryk (song)", "4-note motif", "bes4 a8 bes g4", "could not", "Wilhousky", "public domain", "Dynamics (music)", "Interval (music)", "Ostinato", "Call and response", "Scientific pitch notation",
                 "Time signature", "Semitone", "Mykola Leontovych", "not from any source", "1921", "Logic Pro 9"):
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
    for brand in ("Shure", "Sound on Sound", "MusicRadar", "Wikipedia", "Wikimedia", "IMSLP", "Wilhousky", "Apple Support"):
        if brand in alldeck or brand in txt:
            errs.append(f"buyer-facing pages and slides must not name a source site, brand or the 1936 arranger ({brand}); sources are listed in UPLOAD.md")
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
    return ("seconds per beat = 60 / BPM, per eighth note = 30 / BPM and per bar of 3/4 = 180 / BPM (3 beats, 6 eighth notes) recomputed exactly (fractions) and by an independent float method at six tempos; "
            "4-bar and 16-bar lengths (720 and 2880 / BPM; 16 bars = 32 s at 90 BPM) and form lengths of 8, 12, 16 and 32 bars at 72, 90 and 120 BPM; the motif (Bb4 A4 Bb4 G4 = MIDI 70 69 70 67, quarter, eighth, eighth, quarter = 3 beats "
            "= one bar of 3/4) and its second key (G4 F#4 G4 E4, every note exactly 3 semitones lower), note names against note numbers, frequencies 440 x 2^((m - 69) / 12), the intervals (-1, +1, -3; their sum equals last minus first; "
            "the span is a minor third), the octave (+12 doubles the frequency), other keys; the 16-bar layer map (5 layers, 4 sections, bars per layer 14 + 8 + 12 + 4 + 2 = 40, layers per bar, the answer only in the bell's rests, a new layer in "
            "every section) counted again in the drawings (blocks, counts, section bars, notes, intervals); the dynamics ramp (5 automation points, levels at every bar start, never falling, 80 to 112 in bars 13 to 16 = 8 per bar, "
            "exact and float); every 'Step N' agrees with the project sheet on pages, slides, notes and UPLOAD.md; class badges agree with the pacing page, and the deck's 'three classes' slide carries Classes 1-3; "
            "Class 1 and 2 slides teach no later-class content; every stated note, bar, section, point and layer count equals the drawing; every drawing renders alone on a transparent ground with no ink at its edges; "
            "hero art inside its viewBox and 40 units from the file's edges; rendered-DOM footer gap on every page and deck slide, and clear space under text in dark boxes on pages and slides; no truncated slide bullets; "
            "edges of cover.png and previews clear; no audio, lyrics, arrangement, alcohol, religious or holiday wording or student work; no source site named on a buyer page; grades 9-12; tags and subjects are not headings; "
            "no 'what changed' page (ORIGINAL).")


# ================================================================ UPLOAD.md (written by gen.py so every number matches the build)
def write_upload():
    np_, ns = len(PLAN), len(SLIDES)
    n_teacher = (PLAN.index("example2") + 1) - 1
    n_student = (PLAN.index("reflect") + 1) - (PLAN.index("timing") + 1) + 1
    assert 2 + n_teacher + n_student == np_, "page-count list must total the PDF"
    nt = len(LISTING_TITLE)
    desc = (f"{DESC_START} students build a short piece in Logic Pro from the four-note motif of Mykola Leontovych's Ukrainian choral piece Shchedryk (first performed in 1916), "
            f"entered as Bb4, A4, Bb4, G4 (G minor, one bar of 3/4: quarter, eighth, eighth, quarter). They repeat it as an ostinato, layer it at several octaves and sounds over a 16-bar form (a bell, a celesta, a pad, a low bell and an answer), "
            f"write a call-and-response answer in E minor (3 semitones lower: G4, F#4, G4, E4), and shape the piece from pp to ff with a volume automation line and a crescendo, if their version has automation. "
            f"Math runs through every step: one bar of 3/4 = 180 ÷ BPM seconds (2 seconds at 90 BPM, so 16 bars last 32 seconds), one beat = 60 ÷ BPM, and an octave is 12 semitones, which doubles the frequency. "
            f"Only the four-note motif is used. The English words and the 1936 choral arrangement known as “Carol of the Bells” are a separate, copyrighted work and are NOT used; students write their own original layers. "
            f"The bells are a sound idea only, with no holiday imagery. This Bell Ostinato Lab takes {CLASSES} class periods (the pacing guide also shows two and four) and is an original Hudson Beat project; "
            f"the steps are written for Logic Pro, while the ideas (ostinato, layering, dynamics, automation) carry over to GarageBand and other music software.\n\n"
            f"WHAT'S INCLUDED (ZIP: {np_}-page PDF = 1 cover + {n_teacher} teacher + {n_student} student + 1 terms page, plus {ns}-slide intro deck as .pptx and PDF)\n"
            f"• Teacher pages: how to use, project overview, setup, a {CLASSES}-class pacing guide with the deck slides for each class, "
            f"two pages of teacher notes (struggles, variations, resources, grading), a Logic quick reference and a two-page worked example (an invented piece at 90 BPM: "
            f"the timing at three tempos, 5 layers over 16 bars = 32 seconds, a motif in two keys, and a volume line from pp to ff) ({n_teacher} pages)\n"
            f"• Student pages: a timing page (seconds per beat, eighth note and bar of 3/4 at six tempos, 4-bar and 16-bar lengths, and form lengths at three tempos), a note chart with a piano-roll drawing of the motif in two keys, "
            f"MIDI numbers, frequencies and an interval table, an entry page with a checklist and entry log, a layer map (5 layers over 16 bars, with octave shifts and a blank map to fill in), a call-and-response page "
            f"with other keys to try, a dynamics and automation page (pp 32 to ff 112, the level at every bar, a blank ramp), a mix checklist, the 3-page project sheet (overview, goals, vocabulary, requirements, steps, tips, submission checklist), "
            f"the /{RUBRIC_TOTAL} rubric, a vocabulary page, a feedback planner and a reflection page ({n_student} pages)\n"
            f"• Teacher-presented intro deck, {ns} slides with speaker notes on every slide: a think-and-share hook, what the project is, the motif, the timing math, entering the ostinato, the layer map, call and response, "
            f"octave layers, the dynamics ramp, drawing volume automation, what to turn in and the rubric\n\n"
            f"THE THREE CLASS PERIODS\n"
            f"• Class 1: hook; the timing math and a tempo; the motif and its intervals; entering the ostinato and checking it\n"
            f"• Class 2: layer the ostinato over 16 bars at other octaves and sounds; write an answer in a second key\n"
            f"• Class 3: dynamics and volume automation, mix, bounce, present and reflect\n\n"
            f"WHAT STUDENTS LEARN\n"
            f"• Timing math: seconds per bar in 3/4 = 180 ÷ BPM; seconds per beat = 60 ÷ BPM; 16 bars = 2880 ÷ BPM seconds\n"
            f"• Pitch: MIDI note numbers, the motif's intervals (−1, +1, −3 semitones, a minor third in all), transposing by 3 semitones, octaves (+12 doubles the frequency)\n"
            f"• Layering: ostinato, register, sound choice, call and response and a form that builds in 4-bar sections\n"
            f"• Dynamics: pp to ff, crescendo, and drawing a volume automation line\n\n"
            f"GOOD TO KNOW\n"
            f"• There is no audio in this resource and no student work. No words are printed. The only existing music is the four-note motif, which is in the public domain; students enter it themselves and build their own layers. They make every sound with Logic Pro\n"
            f"• Requires Logic Pro on a Mac. No microphone is needed, and a MIDI keyboard is optional; nobody has to read notation. Where a control may differ between versions, the pages say \"if your version has it\" and describe controls generically\n"
            f"• The dynamic levels (pp 32 to ff 112) are an example plan on a 0-127 scale, a starting point to set by ear, not a rule\n"
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
    tbl = "; ".join(f"{b} BPM: {dec(bar_len(b), 3)} s per bar, 16 bars = {dec(ARR_BARS * bar_len(b), 3)} s" for b in TEMPOS)
    md = f"""# UPLOAD: Bell Ostinato Lab, original Logic Pro project (TpT 087)

These fields follow the order of TpT's "Add a resource" form. `tools/tpt.js publish` reads the title and description from the code blocks under 1 and 2, and everything else from `tpt.json`. This file is written by `gen.py`; edit the text there.

**Files to attach**
- Resource (digital download): `{SLUG}.zip`. It holds three files in a folder "{ZIP_DIR}":
  - `{SLUG}.pdf`: the teacher and student resource, {np_} pages, US Letter portrait.
  - `{SLUG}-intro-deck.pptx`: the teacher-presented intro deck, {ns} slides (16:9), speaker notes and a Class badge on every slide (the three-classes slide carries "Classes 1-3").
  - `{SLUG}-intro-deck.pdf`: a PDF copy of the deck, {ns} pages.
- Thumbnails, in this order: `cover.png`, `preview-1.png`, `preview-2.png`, `preview-3.png` (all 2000 × 2000).
- Preview file: `{SLUG}-PREVIEW.pdf`, 4 watermarked pages.

TpT takes one product file, so the PDF, the .pptx and the deck PDF go up together as the ZIP (`files.product` in tpt.json; `zip_contents` lists what is inside). **No audio, video, lyrics, recordings, arrangements, presets, screenshots, student work or Logic sessions are in the ZIP.** Students build their own original layers; the kit prints only the four-note motif (as a note chart) and no words.

**Page count, adding up to the PDF:** 1 cover + {n_teacher} teacher + {n_student} student + 1 terms page = {np_} pages; plus {ns} slides = {np_ + ns} for TpT's "Number of pages or slides".

## 1. Title

```
{LISTING_TITLE}
```
({nt} characters; the limit is 80.) The title leaves out Winter, Holiday, Christmas and Carol because TpT's Seasonal Titles notice blocked a holiday-named title on 027 (see 067, 070, 076, 080 and 083 for the working format); "Ostinato Project" and "Layering, Dynamics, Automation" are the plain search phrases. "Logic Pro" is in the first 30 characters as a compatibility word.

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

**${PRICE}** (paid), multiple-license price ${PRICE}. The price the queue set, at the low end of the $8-12 holiday Logic kit range, for a kit with {np_} pages + {ns} slides, a timing page, a note chart in two keys, an entry page, a 5-layer 16-bar layer map with a blank map, a call-and-response page, a dynamics ramp with automation points, a mix checklist and a two-page worked example, listed in December.

## 8. Free or paid / free preview pages

Paid. Preview PDF (4 watermarked pages): the {CLASSES}-class pacing guide, the note chart, the layer map and the dynamics page. "Number of pages or slides" is {np_ + ns} ({np_} pages + {ns} slides).

## 9. Sources and credits

All sources were fetched on 26 Nov 2026 unless a line says "could not". The motif and its status are the sensitive part of this kit, so each fact below says which source it came from.

- **The motif: pitches, key, meter and rhythm (two public scores read).**
  (1) English Wikipedia, "Shchedryk (song)", the "Melody" section's embedded score. I read the score's LilyPond source from the page's raw wikitext: `\\key g \\minor \\time 3/4`, then `\\relative c''` with the motif `bes4 a8 bes g4`, which is Bb4 (quarter note), A4 (eighth), Bb4 (eighth), G4 (quarter), repeated for many bars: one bar of 3/4 = 3 beats. The page text agrees: the chant is "based on an ostinato four-note pattern within the range of a minor third", "The melody score is marked 3/4", and the folk text uses a hemiola, which alternates accents between 3/4 and 6/8.
  (2) **Independent second source:** Wikimedia Commons "File:Щедрик.pdf" (public-domain-tagged typeset score for mixed choir, 2 pages, made by a different Commons user from the Ukrainian print edition M. Леонтович, "Хорові твори", Kyiv: Музична Україна, 1970, ed. M. Gordiychuk). QA read the PDF (fetched through its upload.wikimedia.org file URL) and viewed it at 130 and 300 dpi: treble clef, two flats (G minor), "Alegretto", the opening solo bar and the repeated bars show a quarter note on the middle line (Bb4), an eighth on the space below (A4), an eighth on the middle line (Bb4) and a quarter on the second line (G4), repeated bar after bar. The note values add up to 3 quarter-note beats per bar with the other staff resting for a bar. This score prints no time-signature numerals in its opening bars, so the meter 3/4 rests on source 1 and on the note values. This source is separate from the Wikipedia LilyPond code (a different file, typesetter and printed edition), so the two agree on the four notes, the rhythm and the key. The Commons image "File:Shchedryk 4-note motif.jpg" shows the same Wikipedia motif and is NOT counted as a source.
  The brief for this kit guessed G-F#-G-E; that is the same motif moved 3 semitones lower (E minor), which the kit shows as the second key. In G minor, the original key in both scores, it is Bb-A-Bb-G.
  **Could not fetch:** the Commons MIDI file; IMSLP's Drew Weymouth score (PDF #304704; IMSLP returned a bot-check page instead of the file); the 1921 print itself (no scan was found). The IMSLP work page itself was read, so the kit relies on the two scores above and does not claim to have checked the 1921 print. Because the motif is only four notes and the sources agree on them, the kit claims nothing more than that.
- **Meter and the length of a bar.** English Wikipedia, "Time signature": 3/4 means "three quarter notes (crotchets) per measure (bar)". One beat = 60 / BPM s is the definition of beats per minute; the bar = 3 x 60 / BPM = 180 / BPM s, the eighth note = 30 / BPM s, and every table, are arithmetic computed in `gen.py --check` exactly with fractions and with an independent float method. Six tempos: {tbl}.
- **Who and when; public-domain status.** English Wikipedia, "Mykola Leontovych": born 13 Dec 1877, died 23 Jan 1921; Shchedryk premiered in 1916 (the Shchedryk page gives 29 Dec 1916 as the first performance in Kyiv and calls the older claim of 25 Dec incorrect). English Wikipedia, "Shchedryk (song)": first performed on 29 December 1916 in the Kyiv Merchants' Assembly Hall; the infobox lists 1901 (first version) and 1919 (final revision). IMSLP, "Carol of the Bells (Leontovych, Mykola)" (the work page; composition year 1904, first performance 1916, first publication 1921, Kiev: Mystetstvo, in "Vybrani khorovi tvory"). The sources disagree about when it was composed (1901 to 1919 depending on the page), so the kit says only "first performed in December 1916", which every page supports. **Public-domain status:** the composer died in 1921 and the first print is dated 1921, so the music is old enough to be in the public domain (the factory's rule for 2026 is first published in 1930 or earlier). This is my reading of dates, not legal advice, and I did not check any registration.
  **The 1936 arrangement and English words are copyrighted and are NOT used.** IMSLP's page notes: "The popular English lyrics by Peter Wilhousky (1902-1978) are under copyright." English Wikipedia, "Carol of the Bells": "Wilhousky secured copyright to the new lyrics and the published song." The kit prints no words and no arrangement: only the four-note motif as a note chart, and tells students to write their own layers and not to copy any later arrangement. The English title "Carol of the Bells" appears only in the description and once in the teacher pages, to say what the tune is known as.
- **Ostinato.** English Wikipedia, "Ostinato": a motif or phrase that "persistently repeats in the same musical voice, frequently in the same pitch". The same page lists "Carol of the Bells" among ostinato-based pieces.
- **Dynamics and crescendo; the levels.** English Wikipedia, "Dynamics (music)": pp "very quiet", p "quiet", mp "moderately quiet", mf "moderately loud", f "loud", ff "very loud"; crescendo = "increasing"; a table of default MIDI velocities (0-127) that some programs assign to each marking lists Logic Pro 9 as pp 32, p 48, mp 64, mf 80, f 96, ff 112 (other programs list different values). The kit uses the Logic Pro 9 values as an example plan on a 0-127 scale, not as a standard and not as Logic Pro's current behavior. The automation line's points (bars 1, 5, 9, 13 and the end of bar 16 at 32, 32, 64, 80 and 112) are an example chosen for this kit.
- **Intervals and octaves.** English Wikipedia, "Interval (music)": minor second 1 semitone, major second 2, minor third 3, octave 12; "any two notes an octave apart have a frequency ratio of 2:1". English Wikipedia, "Semitone": 12-tone equal temperament, each semitone a ratio of the twelfth root of 2 (about 1.05946). The kit's intervals (−1, +1, −3) and the minor-third span are computed in `gen.py --check` from the MIDI numbers.
- **MIDI numbers and frequencies.** English Wikipedia, "Scientific pitch notation": middle C = C4 = MIDI 60; A4 = MIDI 69 = 440 Hz; frequency = 440 x 2^((m - 69) / 12). Bb4 466.2, A4 440.0, G4 392.0, F#4 370.0, E4 329.6 Hz, Bb5 932.3 Hz and Bb3 233.1 Hz are computed from it in `gen.py --check`. The page does not say how any particular software labels octaves, so the kit only says "software may number octaves differently" and names no program; it tells students to compare note letters and semitone distances.
- **Call and response.** English Wikipedia, "Call and response (music)": "a compositional technique, often a succession of two distinct phrases that works like a conversation in music".
- **Logic Pro automation.** Apple, "Automation overview" in the Logic Pro User Guide: **could not read the page body** (the fetch returned only the guide's navigation, whose entries include "Automation overview", "Show automation curves", "Add automation points" and "Adjust automation points on the automation track"). The kit therefore describes automation generically (show the track's automation, choose Volume, click to add points, drag them), says "if your version has it", and invents no menu paths or key commands. Piano Roll, velocity, region looping, transposing by semitones, the Mixer and Bounce are standard Logic Pro features named without paths, except the File › Bounce › Project or Section (Command-B) and Mixer (X) lines carried over from earlier kits.
- **Example values (not from any source).** The 90 BPM tempo, the layer map (which layer plays in which bar), the pad note G3, the choice of E minor (and D minor and A minor) as other keys, the section names, the example volume points and every invented time are example values chosen for this kit and labeled as examples. "Bell, celesta, pad" are sound ideas; the kit does not promise that any named preset exists in a given version of Logic Pro.
- **No recordings, no brands.** No recordings, artists or albums are named. The kit uses no film, game or pop-music reference.
- **Art:** the cover, previews and deck use the owner's pre-made art (`art/hero.png`: five handbells, a laptop showing an abstract waveform, a monitor speaker, headphones on a stand, an audio interface and a stack of three layer blocks, no screen text), copied whole from `tpt/_art/next/bell-ostinato-lab/`; logged in `tpt/_art/USAGE.md`. Everything else, including every number, table, piano-roll drawing, layer map and dynamics ramp, is drawn or printed in code.
- **Fonts:** Oswald and Source Sans 3 (SIL OFL 1.1). Logic Pro is named only to describe compatibility.

## 10. Before you click publish

- [ ] **Needs QA approval first.** This is a new kit (not yet on TpT); the Manager releases it only after a QA `**Verdict: APPROVED**`. Season rule: listing no sooner than the 2-8 week window before winter allows.
- [ ] Cover and previews show "HUDSON BEAT" in type; PDF footers read "© 2026 Brian Lotze · Hudson Beat · For single-classroom use".
- [ ] No school name, logo, student names or work, audio, video, lyrics, arrangement, recording name or Logic session anywhere (`gen.py --check` scans every output and every file in this folder).
- [ ] **Secular.** The theme is a bell sound as an idea: no holiday imagery, no religious content, no alcohol imagery, no brands other than Logic Pro, no recordings. The motif is from a Ukrainian New Year's choral piece; the kit does not describe any holiday. `gen.py --check` fails on alcohol, religious and holiday words.
- [ ] **Timing numbers (all recomputed in `gen.py --check`, exactly with fractions and again with an independent float method).** Seconds per beat = 60 / BPM; per eighth note = 30 / BPM; per bar of 3/4 = 180 / BPM = 3 beats = 6 eighth notes; 4 bars = 720 / BPM; 16 bars = 2880 / BPM. Form lengths at three tempos: 8 / 12 / 16 / 32 bars = 20 / 30 / 40 / 80 s at 72 BPM, 16 / 24 / 32 / 64 s at 90 BPM and 12 / 18 / 24 / 48 s at 120 BPM. Rounding: seconds per beat, bar and section to 3 decimals, per eighth note to 4, half up. Section starts at 90 BPM: 0, 8, 16, 24 s; the form ends at 32 s.
- [ ] **Motif and pitch numbers (recomputed).** Bb4 A4 Bb4 G4 = MIDI 70 69 70 67; second key G4 F#4 G4 E4 = 67 66 67 64, every note exactly 3 lower; lengths 1, 1/2, 1/2, 1 beats = 3 beats; intervals −1, +1, −3, which add up to −3 = last minus first; span 3 semitones = a minor third; three different pitches in four notes. Octave: +12 doubles the frequency (Bb4 466.2 Hz, Bb5 932.3 Hz). Other keys: −5 gives F4 E4 F4 D4 (D minor), +2 gives C5 B4 C5 A4 (A minor).
- [ ] **Layer and dynamics numbers (recomputed from the data and from the drawings).** 16 bars, 4 sections of 4 bars, 5 layers; bars per layer 14, 8, 12, 4 and 2 = 40; layers sounding per bar 1 (bars 1-4), 3 (5-8), 2 (9-12), 4 (13-16) = 40; the answer plays only in bars 10 and 12, the bell's rests. Volume line: 5 points (bar 1 = 32, bar 5 = 32, bar 9 = 64, bar 13 = 80, end of bar 16 = 112); levels at the start of bars 1 to 16: 32 x5, 40, 48, 56, 64, 68, 72, 76, 80, 88, 96, 104; the line never falls; crescendo in bars 13-16 = (112 − 80) / 4 = 8 per bar.
- [ ] **Original project.** Built with `ORIGINAL = True` in `tpt/_dmp2_common/dmp2.py` (like 031, 036, 053, 057, 061, 063, 067, 070, 076, 080 and 083): no "what changed" page and the new disclosure line. The reflection page is the shared Reflection element, scored in the rubric's "Plan & Reflection" row. `dmp2.py` is unchanged; the deck's three-classes badge and the terms-page thank-you note are applied inside `gen.py`.
- [ ] **Logic Pro names to confirm on a Mac with a current Logic.** The Piano Roll with an eighth-note grid, a bell, glockenspiel or celesta sound in the Software Instrument library (hedged), Alchemy (hedged), the project time signature setting (location differs by version), looping or copying a region, transposing by +12, −12 and −3 semitones, the velocity display (hedged), automation (show, choose Volume, add and drag points; hedged), the Mixer (X), Bounce (Command-B) and Compress in Finder.
- [ ] **Open questions for the owner:** (1) **Naming the tune.** The pages say the motif is from Shchedryk and "known in English-speaking countries as Carol of the Bells" (teacher pages and description only); say if you want the English title removed. (2) **Public-domain wording.** The kit says the music is old enough to be in the public domain and that the 1936 English words and arrangement are a separate work not used; I could not read the 1921 print or a Commons/IMSLP full score, so a quick check by you or a lawyer would settle it. (3) **Title.** No Winter, Holiday, Christmas or Carol in the title because of TpT's seasonal-title notice (see 1). (4) **Price.** ${PRICE}, as queued. (5) **Logic automation details.** Apple's automation pages could not be read in full, so the kit stays generic; say if you want a Mac check before release. (6) **Dynamic levels.** The pp 32 to ff 112 values come from a Wikipedia table of Logic Pro 9 defaults and are described as an example plan. (7) **Classes.** Three periods; Class 1 holds the motif and the ostinato, so the pacing page shows how to use two or four.
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

