#!/usr/bin/env python3
"""Logic Pro project kit: Auld Lang Syne Reharmonized (TpT 070): the teacher resource, the intro deck and the listing files.

    python3 gen.py            build everything into this folder (also writes UPLOAD.md)
    python3 gen.py --lowres   same, but square images at scale 1 and small page shots (self-check only; --check rejects it)
    python3 gen.py --check    verify content and layout: the melody chart (stored in C major and G major; the G major copy is the C major copy
                              moved up 7 semitones; bars add up to 16 sixteenths; the chart equals a LilyPond transcription typed in F major and agrees
                              with a second score on every beat), the three chord tables (the melody note on every downbeat is a chord tone; Roman
                              numerals and letter names are recomputed from pitch classes in both keys), the tempo table (seconds per beat = 60 / BPM,
                              seconds per bar = 240 / BPM, 40 bars), the arrangement map, Step N references on every page, slide and UPLOAD.md, class
                              badges against the pacing page, drawings (each rendered alone on a transparent ground: no ink within 4 px of its edge),
                              the hero art, files, page and slide counts, class slots, fonts, fit and overlap, dead space, footer gap, truncated slide
                              bullets, the edges of cover.png and the previews, banned strings, tpt.json and UPLOAD.md

An ORIGINAL Hudson Beat project (dmp2.ORIGINAL = True, like 053, 057, 061, 063 and 067). Students re-harmonize a public-domain melody, the traditional Scottish
tune that goes with Robert Burns's 1788 poem "Auld Lang Syne" (the standard tune was first documented with the words in 1799). They enter the melody from a
note chart in C major or G major, choose a pop, ballad or EDM chord table (or write their own), build a groove and arrange 40 bars in four sections. No audio
ships and the poem's words are not printed. The art on the cover, the previews and the deck is the owner's pre-made hero (art/hero.png), used whole. Everything
else is drawn in code. The shared builder is ../_dmp2_common/dmp2.py.
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
SLUG = "auld-lang-syne-reharmonized"
TITLE = "Auld Lang Syne Reharmonized"
ACCENT = "#2F7FB8"          # this product's single accent: icy blue (a shade deeper than the art's #4FA3D9, so small labels read)
ACC_LIGHT = "#DCEBF6"
PRICE = "8.00"
CLASSES = 3
GRADES_TEXT = "9–12"
GRADE_SLUGS = ["9th-grade", "10th-grade", "11th-grade", "12th-grade"]
TAGS = ["New Year", "Project-based Learning", "Projects", "Activities"]     # exact entries of tpt/TAG-OPTIONS.json, none a heading
SUBJECTS = ["Music", "Computer Science - Technology", "Music Composition"]     # all in SUBJECT-OPTIONS.json, none a heading
ANSWER_KEY = None
LISTING_TITLE = "Logic Pro Reharmonize a Melody | Pop, Ballad, EDM Chords | High School"
DESC_START = "Reharmonizing project for high school music technology:"
DESC_MUST = ["Auld Lang Syne Reharmonized", "public domain", "no audio", "seconds per bar", "240 ÷ BPM", "Roman numeral", "sidechain", "Alchemy"]
ZIP_DIR = "Auld Lang Syne Reharmonized - Hudson Beat"
ZIP_DATE = (2026, 11, 22, 12, 0, 0)
TYPE = "Original Project"
PROJ_LINE = "Music Technology | <i>Reharmonizing Project</i> | 3 class periods"
DECK_STRAP = "New chords, old tune"
REFLECT_ROW = "Plan &amp; Reflection"
# split so this file never contains them (the --check scan reads every file in this folder)
BANNED_EXTRA = ["Rud" + "olph", "Fro" + "sty", "Gri" + "nch", "Santa Claus " + "Is", "Jingle Bell " + "Rock", "Feliz " + "Navidad",
                "Mari" + "ah Carey", "Spoti" + "fy", "You" + "Tube", "Home " + "Alone", "Nin" + "tendo", "Ro" + "land",
                "Star " + "Wars", "Hans " + "Zimmer", "John " + "Williams", "Harry " + "Potter", "Pix" + "ar", "Lord of the " + "Rings",
                "Winter " + "Wonderland", "Let It " + "Snow", "Sleigh " + "Ride", "X" + "mas", "Times " + "Square",
                "cham" + "pagne", "bub" + "bly", "Isaac " + "Nathan", "Marcus " + "Hast", "Rob" + "bie", "Dick " + "Clark", "Guy " + "Lombardo"]

# ================================================================ page plan (teacher pages 2-10, student pages 11-25)
PLAN = ["cover", "howto", "overview", "setup", "pacing", "tn1", "tn2", "logicref", "example", "example2",
        "tempo", "chart1", "chart2", "chords1", "chords2", "grooves", "map", "mix", "proj1", "proj2", "proj3", "rubric", "vocab", "present", "reflect", "terms"]


def pg(k):
    return PLAN.index(k) + 1


# ================================================================ the melody: stored in C major and in G major, checked against two scores
# Lengths are in sixteenth notes: 4 = quarter, 6 = dotted quarter, 2 = eighth, 12 = dotted half. "R" is a rest. One chart bar = one bar of 4/4 = 16 sixteenths.
# Chart bar 0 is the pickup bar (three beats of rest, then one note on beat 4); chart bars 1 to 16 are the tune. The last bar ends with a beat of rest, so the
# pickup and the last bar together add up to one bar.
LEN_NAMES = {1: "16th", 2: "eighth", 4: "quarter", 6: "dotted quarter", 8: "half", 12: "dotted half", 16: "whole"}
_PC = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
BLACK_PC = {1, 3, 6, 8, 10}
SHIFT_G = 7         # G major is C major moved up 7 semitones (a perfect fifth)


def midi(p):
    acc = 0 if len(p) == 2 else (1 if p[1] == "#" else -1)
    return 12 * (int(p[-1]) + 1) + _PC[p[0]] + acc


def pname(m):
    return NAMES[m % 12] + str(m // 12 - 1)


# The chart the students use, typed twice: C major (do = C4) and G major (do = G4). --check proves the G copy is the C copy moved up 7 semitones.
CHART_C = [
    [("R", 12), ("G3", 4)],
    [("C4", 6), ("C4", 2), ("C4", 4), ("E4", 4)],
    [("D4", 6), ("C4", 2), ("D4", 4), ("E4", 4)],
    [("C4", 6), ("C4", 2), ("E4", 4), ("G4", 4)],
    [("A4", 12), ("A4", 4)],
    [("G4", 6), ("E4", 2), ("E4", 4), ("C4", 4)],
    [("D4", 6), ("C4", 2), ("D4", 4), ("E4", 4)],
    [("C4", 6), ("A3", 2), ("A3", 4), ("G3", 4)],
    [("C4", 12), ("A4", 4)],
    [("G4", 6), ("E4", 2), ("E4", 4), ("C4", 4)],
    [("D4", 6), ("C4", 2), ("D4", 4), ("A4", 4)],
    [("G4", 6), ("E4", 2), ("E4", 4), ("G4", 4)],
    [("A4", 12), ("A4", 4)],
    [("G4", 6), ("E4", 2), ("E4", 4), ("C4", 4)],
    [("D4", 6), ("C4", 2), ("D4", 4), ("E4", 4)],
    [("C4", 6), ("A3", 2), ("A3", 4), ("G3", 4)],
    [("C4", 12), ("R", 4)],
]
CHART_G = [
    [("R", 12), ("D4", 4)],
    [("G4", 6), ("G4", 2), ("G4", 4), ("B4", 4)],
    [("A4", 6), ("G4", 2), ("A4", 4), ("B4", 4)],
    [("G4", 6), ("G4", 2), ("B4", 4), ("D5", 4)],
    [("E5", 12), ("E5", 4)],
    [("D5", 6), ("B4", 2), ("B4", 4), ("G4", 4)],
    [("A4", 6), ("G4", 2), ("A4", 4), ("B4", 4)],
    [("G4", 6), ("E4", 2), ("E4", 4), ("D4", 4)],
    [("G4", 12), ("E5", 4)],
    [("D5", 6), ("B4", 2), ("B4", 4), ("G4", 4)],
    [("A4", 6), ("G4", 2), ("A4", 4), ("E5", 4)],
    [("D5", 6), ("B4", 2), ("B4", 4), ("D5", 4)],
    [("E5", 12), ("E5", 4)],
    [("D5", 6), ("B4", 2), ("B4", 4), ("G4", 4)],
    [("A4", 6), ("G4", 2), ("A4", 4), ("B4", 4)],
    [("G4", 6), ("E4", 2), ("E4", 4), ("D4", 4)],
    [("G4", 12), ("R", 4)],
]
CHARTS = {"C": CHART_C, "G": CHART_G}
KEY_NAMES = {"C": "C major", "G": "G major"}
NBARS = 16          # tune bars; chart index 0 is the pickup bar

# Source 1, typed as printed: the LilyPond text of the 4/4 transcription in F major (with \relative c'), the melody of the traditional tune as engraved on
# the English Wikipedia article "Auld Lang Syne". Only the notes are used (no words). Bar lines separate the pickup and the 16 bars.
SRC_A_LY = ("c4 | f4. f8 f4 a4 | g4. f8 g4 a4 | f4. f8 a4 c4 | d2. d4 | c4. a8 a4 f4 | g4. f8 g4 a4 | f4.( d8) d4( c4) | f2. d'4 | "
            "c4.( a8) a4( f4) | g4. f8 g4 d'4 | c4.( a8) a4( c4) | d2. d4 | c4. a8 a4 f4 | g4. f8 g4 a4 | f4.( d8) d4( c4) | f2.")
# Source 2, typed as printed: the soprano line of a public-domain edition in F major (Brigid Baker's CPDL edition no. 21485, MusicXML): the pitch sounding at the start of
# each of the four beats of every bar, in scientific pitch names (C4 = middle C). The pickup is one note. Where that edition adds an extra eighth note after a beat
# (bar 2 and bar 6 of the tune), only the beat starts are compared.
SRC_B_BEATS = {"pickup": "C4",
               1: "F4 F4 F4 A4", 2: "G4 G4 G4 A4", 3: "F4 F4 A4 C5", 4: "D5 D5 D5 D5", 5: "C5 C5 A4 F4", 6: "G4 G4 G4 A4", 7: "F4 F4 D4 C4", 8: "F4 F4 F4 D5",
               9: "C5 C5 A4 F4", 10: "G4 G4 G4 D5", 11: "C5 C5 A4 C5", 12: "D5 D5 D5 D5", 13: "C5 C5 A4 F4", 14: "G4 G4 G4 A4", 15: "F4 F4 D4 C4", 16: "F4 F4 F4 R"}
SHIFT_F = 5         # F major is C major moved up 5 semitones (a perfect fourth): the chart's C major is the scores' F major moved down 5


def parse_ly(src):
    """LilyPond relative-mode notes (key of F: no accidentals appear) -> [(pitch name, sixteenths)], starting from c' (C4). The first note is the pickup."""
    step = {"c": 0, "d": 1, "e": 2, "f": 3, "g": 4, "a": 5, "b": 6}
    semis = [0, 2, 4, 5, 7, 9, 11]
    notes = []
    prev = 0 + 7 * 4        # c' = diatonic index 28 (C4): octave number 4 -> 7 * 4 steps from C0
    for tok in re.sub(r"[|()~]", " ", src).split():
        m = re.fullmatch(r"([a-g])([',]*)(\d+)(\.?)", tok)
        if not m:
            raise ValueError(f"cannot read LilyPond token {tok!r}")
        ltr, marks, dur, dot = m.groups()
        d = step[ltr]
        # nearest octave to the previous note (within a fourth), then the octave marks
        base = (prev // 7) * 7 + d
        cand = [base - 7, base, base + 7]
        idx = min(cand, key=lambda c: (abs(c - prev), c))
        idx += 7 * (marks.count("'") - marks.count(","))
        prev = idx
        octv, deg = divmod(idx, 7)
        pc = semis[deg]
        length = {"1": 16, "2": 8, "4": 4, "8": 2, "16": 1}[dur]
        if dot:
            length = length * 3 // 2
        notes.append((NAMES[pc] + str(octv), length))
    return notes


def chart_bars(chart):
    """[(pitch, sixteenths)] per bar -> flat list of (pitch, start, length) in sixteenths from the start of chart bar 0, rests skipped."""
    out, t = [], 0
    for bar in chart:
        for p, d in bar:
            if p != "R":
                out.append((p, t, d))
            t += d
    return out


def beat_pitches(chart):
    """The pitch sounding at the start of each beat (sixteenth 0, 4, 8, 12 of every bar), or 'R' for a rest, for chart bars 0 to 16."""
    ns = chart_bars(chart)
    res = []
    for b in range(len(chart)):
        row = []
        for beat in range(4):
            t = b * 16 + beat * 4
            hit = [p for p, s, d in ns if s <= t < s + d]
            row.append(hit[0] if hit else "R")
        res.append(row)
    return res


def moved(chart, semis):
    return [[(p if p == "R" else pname(midi(p) + semis), d) for p, d in bar] for bar in chart]


def note_count():
    return sum(1 for b in CHART_C for p, _ in b if p != "R")


def bar_text(bar):
    return " · ".join(f"rest {LEN_NAMES[d]}" if p == "R" else f"{p} {LEN_NAMES[d]}" for p, d in bar)


def downbeat(chart, bar):
    """The melody note that sounds on beat 1 of tune bar `bar` (1 to 16), as a pitch name."""
    return beat_pitches(chart)[bar][0]


def pc_of(p):
    return midi(p) % 12


# ================================================================ chords: pop, ballad, EDM (one chord a bar over the 16 tune bars), checked in code
# A chord is a letter name in C major plus a quality. The G major name is the same chord moved up 7 semitones.
QUAL = {"": (0, 4, 7), "m": (0, 3, 7), "maj7": (0, 4, 7, 11), "m7": (0, 3, 7, 10), "sus4": (0, 5, 7), "7sus4": (0, 5, 7, 10), "add9": (0, 4, 7, 2)}
QUAL_ROMAN = {"": "", "m": "", "maj7": "maj7", "m7": "7", "sus4": "sus4", "7sus4": "7sus4", "add9": "add9"}
MINORISH = {"m", "m7"}
KEY_SCALE = {"C": [0, 2, 4, 5, 7, 9, 11], "G": [7, 9, 11, 0, 2, 4, 6]}      # pitch classes of the major scale
KEY_NAMES_PC = {"C": {0: "C", 2: "D", 4: "E", 5: "F", 7: "G", 9: "A", 11: "B"}, "G": {7: "G", 9: "A", 11: "B", 0: "C", 2: "D", 4: "E", 6: "F#"}}
TONIC_PC = {"C": 0, "G": 7}
ROMAN_BASE = ["I", "II", "III", "IV", "V", "VI", "VII"]
ROOT_PC_C = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}

STYLES = ["pop", "ballad", "edm"]
STYLE_NAMES = {"pop": "Pop", "ballad": "Ballad", "edm": "EDM"}
CHORDS_C = {
    "pop":    ["C", "G", "Am", "F", "C", "G", "Am", "F", "C", "G", "Am7", "F", "C", "G", "F", "C"],
    "ballad": ["Cmaj7", "Gsus4", "Am7", "Fmaj7", "Cmaj7", "G7sus4", "Am7", "Fmaj7", "Am7", "Dm7", "Em7", "Fmaj7", "Cmaj7", "G7sus4", "Fmaj7", "Cadd9"],
    "edm":    ["Am", "G", "C", "F", "Am7", "G", "C", "F", "Am7", "G", "Em", "F", "Am7", "G", "F", "C"],
}
STYLE_FEEL = {"pop": "The I–V–vi–IV loop: C, G, Am, F. Four chords repeat, so the melody sits on a familiar bed. One chord a bar.",
              "ballad": "Slower, with added 7ths and suspended chords (sus4) that lean toward the next chord. One chord a bar, with room to breathe.",
              "edm": "A vi–V–I–IV loop (Am, G, C, F) that begins on the minor chord. Four on the floor drives it; a sidechain pump makes the pad breathe."}
STYLE_TEMPO = {"pop": "96 to 120 BPM", "ballad": "60 to 80 BPM", "edm": "120 to 128 BPM"}


def split_chord(name):
    """'Am7' -> ('A', 'm7'); 'G7sus4' -> ('G', '7sus4'); 'Cadd9' -> ('C', 'add9')."""
    root = name[0]
    q = name[1:]
    if q not in QUAL:
        raise ValueError(f"unknown chord quality in {name}")
    return root, q


def chord_pcs(name, key):
    """Pitch classes of a chord in `key` ('C' or 'G'): the C major chord moved up 0 or 7 semitones, in chord order (root, third, fifth, ...)."""
    r, q = split_chord(name)
    shift = 0 if key == "C" else SHIFT_G
    root = (ROOT_PC_C[r] + shift) % 12
    return [(root + i) % 12 for i in QUAL[q]]


def chord_letters(name, key):
    return [KEY_NAMES_PC[key][pc] for pc in chord_pcs(name, key)]


def chord_name(name, key):
    """The chord's letter name in the key: the root letter in that key plus the same quality."""
    r, q = split_chord(name)
    return KEY_NAMES_PC[key][chord_pcs(name, key)[0]] + q


def roman(name, key):
    """Roman numeral from the root's scale degree in the key: lower case for minor and minor-seventh chords."""
    r, q = split_chord(name)
    rel = (chord_pcs(name, key)[0] - TONIC_PC[key]) % 12
    deg = [0, 2, 4, 5, 7, 9, 11].index(rel)
    base = ROMAN_BASE[deg]
    return (base.lower() if q in MINORISH else base) + QUAL_ROMAN[q]


def role_of(pc, name, key):
    """What a chord tone is called: root, third, fifth, seventh, fourth (sus4) or ninth (add9)."""
    ps = chord_pcs(name, key)
    r, q = split_chord(name)
    rel = (pc - ps[0]) % 12
    return {0: "root", 3: "third", 4: "third", 5: "fourth (sus4)", 7: "fifth", 10: "seventh", 11: "seventh", 2: "ninth"}[rel]


def bar_pcs(chart, bar):
    """The pitch classes of the notes sounding in tune bar `bar`, in order of appearance."""
    out = []
    for p, d in chart[bar]:
        if p != "R" and pc_of(p) not in out:
            out.append(pc_of(p))
    return out


def passing(style, bar, key):
    """The melody notes of the bar that are not in its chord (passing or neighbor notes), as letter names in order."""
    ch = CHORDS_C[style][bar - 1]
    ps = set(chord_pcs(ch, key))
    return [KEY_NAMES_PC[key][pc] for pc in bar_pcs(CHARTS[key], bar) if pc not in ps]


# ================================================================ time: tempo, bars, seconds
SEC_NAMES = ["Intro", "Pass 1", "Pass 2", "Outro"]
SEC_BARS = [4, 16, 16, 4]       # the track is 4 + 16 + 16 + 4 = 40 bars; the tune's pickup note is beat 4 of bar 4
TOTAL_BARS = sum(SEC_BARS)
TEMPOS = (66, 72, 80, 100, 110, 120, 124, 128)
STYLE_BPM = {"ballad": 72, "pop": 100, "edm": 128}       # the three tempos whose section starts are printed
EX_BPM = 72
EX_KEY = "G"
EX_STYLE = "ballad"


def spb(bpm):
    """Seconds per beat = 60 / BPM."""
    return Fraction(60, bpm)


def bar_len(bpm):
    """Seconds per bar of 4/4 = 240 / BPM (four beats)."""
    return Fraction(240, bpm)


def start_bar(i):
    return sum(SEC_BARS[:i]) + 1


def end_bar(i):
    return sum(SEC_BARS[:i + 1])


def start_s(bpm, i):
    """Seconds from the start of the track to the first beat of section i: bars gone by x 240 / BPM."""
    return sum(SEC_BARS[:i]) * bar_len(bpm)


def total_s(bpm):
    return TOTAL_BARS * bar_len(bpm)


def pass_s(bpm):
    return 16 * bar_len(bpm)


def rnd(x, nd):
    """Round half up (a 5 rounds up) to nd decimals, on exact fractions."""
    s = Fraction(10) ** nd
    return Fraction(math.floor(Fraction(x) * s + Fraction(1, 2)), 1) / s


def dec(x, nd):
    return f"{float(rnd(x, nd)):.{nd}f}"


def num(x, nd=2):
    return f"{float(rnd(x, nd)):g}"


def fmt(x):
    x = float(x)
    x = round(x + 1e-9, 3)
    return f"{x:.0f}" if x == int(x) else f"{x:g}"


def mmss(x):
    t = int(rnd(x, 0))
    return f"{t // 60}:{t % 60:02d}"


# ================================================================ the groove cards (16 steps a bar; x = a hit)
GROOVE_LANES = ["Hat", "Snare", "Kick"]
GROOVES = {
    "pop":    {"Hat": "x.x.x.x.x.x.x.x.", "Snare": "....x.......x...", "Kick": "x.....x.x......."},
    "ballad": {"Hat": "x...x...x...x...", "Snare": "........x.......", "Kick": "x.......x......."},
    "edm":    {"Hat": "..x...x...x...x.", "Snare": "....x.......x...", "Kick": "x...x...x...x..."},
}
GROOVE_SNARE = {"pop": "Snare", "ballad": "Side stick or soft snare", "edm": "Clap"}
GROOVE_TEXT = {
    "pop": ("Kick on beat 1, the “and” of 2 and beat 3; snare on beats 2 and 4; hat on every eighth note.",
            "Bass plays the chord root on beat 1, then repeats it on the eighths. Keys or guitar strum each chord once or twice a bar.",
            "Make the last bar of every four a little busier, such as an extra snare hit on the “and” of 4."),
    "ballad": ("Kick on beats 1 and 3; one soft snare or side stick on beat 3; hat or shaker on every quarter note.",
               "Bass holds each chord root for the whole bar. Piano or pad plays the chord as an arpeggio or with a slow roll.",
               "Leave space: if the melody has a long note, let the chords hold underneath it."),
    "edm": ("Four on the floor: a kick on every beat; clap on beats 2 and 4; hat on the off-beats (the “and” of each beat).",
            "Bass plays the chord root on the off-beats, so it sits between the kicks. A synth pad or pluck plays each chord and gets a sidechain pump from the kick.",
            "Sidechain: the kick turns the pad and bass down for an instant on every beat, then they swell back, so the track seems to breathe."),
}
GROOVE_FACTS = {"pop": (3, 2, 8), "ballad": (2, 1, 4), "edm": (4, 2, 4)}      # kick, snare and hat hits per bar: checked against the strings


def hits(style, ln):
    return [i for i, c in enumerate(GROOVES[style][ln]) if c == "x"]


# ================================================================ the arrangement map: which elements play in which of the four sections
ELEMENTS = [
    ("Chords (pad or keys)", ["soft", "plays", "full", "holds"]),
    ("Melody", ["pickup, bar 4", "lead", "octave doubled", ""]),
    ("Bass", ["", "plays", "full", "root only"]),
    ("Drums", ["", "light", "full", ""]),
    ("Hat or shaker", ["", "steady", "busier", ""]),
    ("Counter-line or arp", ["", "", "plays", ""]),
    ("Sidechain pump (EDM)", ["", "on", "on", ""]),
    ("Reverb tail", ["", "", "", "rings out"]),
]
ELEM_PLAYING = [sum(1 for _, cells in ELEMENTS if cells[i]) for i in range(4)]      # 2, 6, 7, 3


# ================================================================ the project text (original; students read these pages)
THEME = ("“Auld Lang Syne” is a Scottish song that people around the world sing as one year turns into the next. Its title is Scots for “old long since”, "
         "often put into English as “days gone by”, and its chorus line is often rendered “for the sake of old times”. It is a song of remembrance and friendship: "
         "it asks us to keep old friends and good memories close. This project borrows that tune and asks a music-technology question: what happens to one melody when the chords underneath it change?")
SOURCE_NOTE = ("The poem was written by Robert Burns in 1788. The tune students use is a traditional Scottish melody; its first documented use with the words is from 1799. "
               "Both are far older than the 1930 cutoff, so the tune is in the public domain worldwide. The poem’s words are not printed in this kit.")
OVERVIEW = ("Re-harmonize a public-domain melody in Logic Pro. Enter the traditional tune of “Auld Lang Syne” from a note chart (16 bars in 4/4 with a one-beat pickup, in C major or G major), then choose "
            "new chords under it in one of three styles: a pop loop, a slow ballad with added 7ths and suspended chords, or an EDM track with four on the floor and a sidechain pump. Every chord must "
            "hold the melody note on its downbeat. Students name each chord by Roman numeral and letter, build a groove, arrange 40 bars in four sections and mix. Nobody needs to compose a melody.")
GOALS = ["Enter a 16-bar public-domain melody into Logic Pro’s Piano Roll from a note chart, in C major or G major, with the right pitches and lengths",
         "Choose chords for each bar and check that the melody note on every downbeat is a chord tone, naming each chord by Roman numeral and by letter in the key",
         "Build a pop, ballad or EDM groove around the chords, with a bass line and, for EDM, a sidechain pump from the kick",
         "Use one bar = 240 ÷ BPM seconds to plan a 40-bar arrangement in four sections, then mix, bounce and reflect on the choices"]
VOCAB = [("Reharmonize", "To keep a melody the same and write new chords under it, so that the same notes sound happy, sad, calm or driving"),
         ("Chord tone", "A note that belongs to the chord that is playing. A melody note on a strong beat usually should be one; a note that is not is a passing tone"),
         ("Roman numeral", "A number for a chord’s place in the key: I is the chord on the first note of the scale, V on the fifth. Capitals are major chords and lower case are minor"),
         ("Sidechain", "Using one track to control another. A kick that turns the pad and bass down on every beat makes the pumping EDM sound"),
         ("Suspended chord (sus)", "A chord whose third is replaced by the fourth (a sus4 chord), so it sounds open and leans toward the next chord")]
REQS = ["Choose pop, ballad or EDM and a tempo from the tempo table (page @TEMPO)",
        "Enter the melody from the note chart (pages @CHART1–@CHART2) in C major or G major; every pitch and length matches the chart",
        "Use the chord table for your style (pages @CHORDS1–@CHORDS2), or write your own; the melody note on every downbeat is a chord tone",
        "Write the Roman numeral and the letter name of every chord in your key",
        "Build the groove for your style (page @GROOVES), a bass line on the chord roots and, for EDM, a sidechain pump",
        "Arrange 40 bars in four sections with markers (page @MAP), mix with the checklist (page @MIX) and bounce",
        "Reflect on your choices (page @REFLECT)"]
FILE_NAME = "“Your Name – Reharmonized”"
STEP_NAMES = ["Choose style and tempo", "Enter the melody", "Choose chords", "Build the groove", "Arrange the sections", "Mix and bounce", "Present &amp; get feedback"]
STEPS = ["<b>Choose style and tempo</b> — Use the tempo table (page @TEMPO) to pick pop, ballad or EDM and a tempo, and work out how long one bar, one pass of the tune and the whole track last",
         "<b>Enter the melody</b> — Read the note chart (pages @CHART1–@CHART2). Put the melody into a Software Instrument track in the Piano Roll, in C major or G major, and check every pitch and length against the chart",
         "<b>Choose chords</b> — Take the chord table for your style (pages @CHORDS1–@CHORDS2) or write your own, and check that the melody note on each downbeat is a chord tone. Write each chord’s Roman numeral and letter name in your key",
         "<b>Build the groove</b> — Use the groove card for your style (page @GROOVES) for the drums, add a bass line on the chord roots and, for EDM, a sidechain pump from the kick",
         "<b>Arrange the sections</b> — Lay out 40 bars with the arrangement map (page @MAP): a 4-bar intro, the tune twice and a 4-bar outro, with a marker at the start of each section (Logic quick reference: page @LOGICREF)",
         "<b>Mix and bounce</b> — Set levels, pan and effects with the mix checklist (page @MIX), then bounce your whole track and name the file as on the checklist",
         "<b>Present &amp; get feedback</b> — Write three questions you want classmates to answer about your chords. Play your track, say why you chose each chord progression, "
         "and answer at least 2 of each classmate’s questions. Then reflect (page @REFLECT)."]
TIPS = ["Play the melody over a chord before you commit to it. If it sounds wrong, look at the melody note on the downbeat first: is it in the chord?",
        "Change chords less often for a calmer feel and more often for a busier feel. One chord a bar is a good start.",
        "Let the melody be the loudest part in the first pass. Let the arrangement grow in the second.",
        "Save a new version of your project at the end of each class, so you can always go back."]
CHECK = ["Bounced .mp3 or .wav of your whole track, 40 bars long",
         "Zipped .logicx project file handed in",
         f"Files named correctly: {FILE_NAME}",
         "Chord table with a Roman numeral and a letter name for every chord",
         "Rubric self-score done (page @RUBRIC)",
         "I can say my style, my key and my tempo, and why each chord fits its downbeat"]
RUBRIC_NOTE = "Each category is scored 1–5. Score yourself first; the final grade is the average of your score and your teacher’s."
LEVELS = [1, 2, 3, 4, 5]
RUBRIC = [
    ("Melody & Chart", ["No melody entered", "Only a few bars entered, or many wrong pitches", "The whole tune is entered, with several wrong notes or lengths",
                        "Every pitch and length matches the chart in the chosen key, and the pickup is on beat 4",
                        "The melody matches the chart exactly and is shaped with velocity or timing so that it sings"]),
    ("Chords & Harmony", ["No chords", "Chords are added, but several downbeat notes are not chord tones", "Most downbeat notes are chord tones; names or numerals have errors",
                          "Every downbeat note is a chord tone, and every chord has the correct Roman numeral and letter name in the key",
                          "Correct chords and numerals, with a clear reason for each choice and one passing note explained"]),
    ("Style & Groove", ["No groove", "Drums or bass only, with little connection to the style", "A groove in the style, but it is not steady or the bass ignores the chords",
                        "Drums, bass and chords fit the chosen style; an EDM track has four on the floor and a sidechain pump",
                        "The groove is convincing, varies between the two passes and leaves room for the melody"]),
    ("Arrangement & Mix", ["Parts are too loud or too quiet to tell apart", "A few parts can be heard; others are buried or clip",
                           "Most parts can be heard; the sections are not clear", "Four sections of 4, 16, 16 and 4 bars with markers; every part can be heard and nothing clips",
                           "The second pass is bigger than the first, the melody stays clear and the low end is tight"]),
    ("Plan & Reflection", ["Plans, presentation or reflection missing", "Thin plan; little to say about choices", "Plan and reflection complete, with basic detail",
                           "Clear plan; thoughtful reflection and good answers to questions", "Insightful reflection and a polished, confident presentation"]),
]
RUBRIC_TOTAL = 25
RUBRIC_SHORT = ["Matches the chart exactly and is shaped so that it sings",
                "Correct chords and numerals, with a clear reason for each",
                "A convincing groove that leaves room for the melody",
                "The second pass is bigger, the melody stays clear",
                "Insightful reflection and a polished, confident presentation"]
RUBRIC_SLIDE_LINE = "Scored 1–5 · final grade = average of your score and mine, out of 25"
RUBRIC_ROW_PITCH = 0.86
RUBRIC_LINE_Y = 6.3

TN_REINFORCES = ("This project teaches what chords do. Students learn that a melody does not belong to one chord, that a chord that holds the melody’s downbeat note will fit, how Roman numerals "
                 "name chords in any key, how pop, ballad and EDM styles use different chords and grooves, and how to turn a tempo into bars and seconds, all in Logic Pro.")
STRUGGLES = ["The chords sound wrong: play the melody’s downbeat note alone, then the chord. If the note is not in the chord, choose another chord from the table or move one note of the chord (page @CHORDS2).",
             "The Roman numerals and letter names do not match: write the key’s scale on a staff of seven boxes, count the chord’s root in it, and use the chord key on page @CHORDS2.",
             "The melody is entered in the wrong octave: Logic calls middle C “C3” by default and the chart calls it C4, so subtract one from the chart’s octave number (page @CHART1).",
             "The EDM pump does not move: the Compressor must have the kick track chosen as its side chain, and the kick must play on every beat (page @GROOVES)."]
VAR_EASY = ("Use the pop table in C major, one chord a bar, with the groove card as given (pages " + str(pg("chords1")) + " and " + str(pg("grooves")) + "). Skip the second pass’s octave doubling, "
            "and ask for 2 questions at the presentation.")
VAR_HARD = ("Write your own chords for bars 9 to 16 and justify each downbeat, add a key change into the second pass (move it up two semitones with Transpose in the Region inspector), "
            "or make a second version in another style and compare the two (page " + str(pg("map")) + ").")
RESOURCES = [("Note chart (pages @CHART1–@CHART2)",
              "The melody in C major and G major as a piano roll and a bar-by-bar table, with the pickup bar and sources. Students enter it exactly, then check it against the chart."),
             ("Chord tables (pages @CHORDS1–@CHORDS2)",
              "Pop, ballad and EDM chords for all 16 bars, with Roman numerals and letter names in both keys, the chord tones, and a check that each downbeat is a chord tone."),
             ("Groove cards and arrangement map (pages @GROOVES and @MAP)",
              "One-bar drum patterns for the three styles, a four on the floor and sidechain explanation, and a map of which elements play in which section."),
             ("Worked example (pages @EXAMPLE–@EXAMPLE2)",
              "An invented ballad plan in G major at 72 BPM: a 40-bar track that lasts 133.33 seconds, with its chords, sections and mix notes. A model, not a template.")]
TN_NOTE = ("A good listening day: play each student’s track without saying the style and let the class name it and the chords they hear. Ask which chord changed the mood most. "
           "This kit names no songs or artists, and the melody is public domain.")
GRADING = ["The rubric: five categories, each scored 1–5, /25 (page @RUBRIC). Students score themselves first; the final grade is the "
           "average of their score and yours.",
           "Melody & Chart (rubric row 1): play the melody alone and compare it with the chart, bar by bar (pages @CHART1–@CHART2).",
           "Chords & Harmony (rubric row 2): for each bar, check that the downbeat note is in the chord, and that the numeral and letter name are right (page @CHORDS2).",
           "Style & Groove (rubric row 3): listen for the style’s drum pattern and a bass line that follows the chords (page @GROOVES).",
           "Arrangement & Mix (rubric row 4): check the markers against the map, listen for the melody over the chords and check the meter for clipping (pages @MAP and @MIX).",
           "Plan & Reflection (rubric row 5): the chord table, the feedback questions and the Reflection page (page @REFLECT) are the evidence."]
PACING = [
    {"n": 1, "owner": "Hear the idea, learn the tune and choose chords.",
     "do": "Slides 1–6: the think-and-share, what the project is, the three classes, the melody in a piano roll and how a chord fits a melody note. Hand out the tempo table, the note charts and the chord tables. "
           "Before they leave, students have a style, a key, a tempo and the first eight bars of the melody entered.",
     "slides": (1, 6), "pages": ["tempo", "chart1", "chart2", "chords1", "proj1", "proj2", "proj3", "vocab"],
     "deck": "Think and share · the melody · chord tones"},
    {"n": 2, "owner": "Finish the melody, set the chords and build the groove.",
     "do": "Slides 7–9: three styles and their chords, four on the floor with sidechain, and building it in Logic. Students finish the melody, enter their chords, check every downbeat, "
           "then build the drums and bass. Walk the room with one question: is that downbeat note in the chord?",
     "slides": (7, 9), "pages": ["chords1", "chords2", "grooves", "map", "present"], "deck": "Three styles · four on the floor · build it in Logic"},
    {"n": 3, "owner": "Arrange the sections, mix, present and reflect.",
     "do": "Slides 10–14: the arrangement map, what to turn in, the rubric and presentation day. Students lay out the intro, the two passes and the outro, add a marker for each, "
           "then mix with the checklist, bounce and present.",
     "slides": (10, 14), "pages": ["map", "mix", "rubric", "present", "reflect"], "deck": "Arrangement · checklist · rubric · presentations"},
]
PACING_EXTRA = (
    '<div class="cols" style="margin-top:4pt;gap:14pt"><div class="box acc-b"><span class="k">The one thing to do on Class 1</span>'
    '<p style="margin:0;font-size:10.6pt">Make sure every student leaves with a style and a tempo from the tempo table and the first eight bars of the melody entered correctly, so that Class 2 '
    'is all chords and groove. Play a few students’ melodies against the chart before they go.</p></div>'
    '<div class="box"><span class="k">With two or four periods</span><p style="margin:0;font-size:10.6pt"><b>Two classes:</b> Class 1 is the tempo, the melody and the chords; '
    'Class 2 is the groove, the arrangement, the mix and short presentations. <b>Four classes:</b> keep Classes 1 and 2, then spend Class 3 on the arrangement and the mix, and '
    'Class 4 on presentations and reflection.</p></div></div>')
PACING_SIZE = 10.6
TN2_SIZE = 10.3

SONG_NOTE = ("No audio, recordings or lyrics are included. The melody is a public-domain tune printed as a note chart; the poem’s words are not printed. "
             "Students make every sound themselves, from the instruments, samples and loops in Logic and from their own voices.")
CREDITS = ["The tempo table, chord tables, groove cards, arrangement map, checklists and worked example: original work, Hudson Beat. The melody is the traditional Scottish tune of "
           "“Auld Lang Syne” (public domain), entered as a note chart and checked against two public-domain scores: the transcription in F major published on the English Wikipedia article "
           "“Auld Lang Syne”, and Brigid Baker’s edition on the Choral Public Domain Library (CPDL no. 21485). No lyrics, recordings or other arrangements are included.",
           "The cover illustration was made with digital and AI tools. No audio, video, album art, screenshots, presets, templates or links from other sources are included. "
           "No student work is included. All timing facts are arithmetic shown in the product."]
LOGIC_INTRO = ("Where to find the tools a reharmonizing project is likely to use. Demonstrate what your class needs on Classes 1 and 2 and then "
               "let students work. Names are from current Logic Pro versions; labels move between versions, so check yours.")
LOGIC_REF = [("Project and tempo", "File › New…, then a Software Instrument track to start. Set the project tempo in the control bar to the tempo you chose and keep the time signature at 4/4. "
              "Smart Tempo, if your version has it, can detect the tempo of a recording; for this project set the tempo yourself so that the bar arithmetic on the tempo table holds."),
             ("Enter the melody", "Open the Piano Roll and draw the notes with the pencil tool on a grid of 1/16 or 1/8. Pitch names run down the left. Logic names middle C “C3” by default; the chart calls it C4, "
              "so subtract one from the chart’s octave number. The pickup is one note on beat 4 of the bar before bar 1. Transpose in the Region inspector moves a region by semitones: 7 semitones up turns C major into G major."),
             ("Chords", "Put the chord notes on a second Software Instrument track in the Piano Roll (a chord is three or four notes at the same start). The Chord Track, if your version has it, can show the chord symbols above the tracks; "
              "it only labels what you choose, and you must still check each downbeat against the chart."),
             ("Session Players", "Keyboard Player, Bass Player and Drummer, if your version has them, can play chords and a groove for you. Choose the chords yourself first and set the player to follow them; "
              "you still need to check the melody against every chord. Session Players are optional."),
             ("Drums", "Use Drum Machine Designer with a kick, a snare or clap and a hat on three pads. In the Piano Roll set the grid to 1/16 and click in the hits from your groove card, or draw them with the Step Sequencer if your version has it. "
              "Lower the velocity of the hats a little so the kick and the snare stand out."),
             ("Bass and chords sounds", "Use Alchemy for a pad, a pluck or an EDM bass (browse its presets by name), or a Retro Synth patch. Keep the bass to one note at a time in a low octave, on each chord’s root. "
              "Roll the chords on keys or a pad, and keep them below the melody’s register."),
             ("Sidechain for EDM", "On the pad or the bass track, add a Compressor and, in its Side Chain section, choose the kick track as the source, if your version’s Compressor has a side chain menu. "
              "Lower the threshold until the pad ducks on every kick. If your Compressor has no side chain, draw volume automation that dips on every beat and recovers before the next."),
             ("Sections with markers", "Show the Marker global track (the Global Tracks controls or the View menu). Add a marker with the plus (+) button in that track, "
              "or with a Create Marker key command if your version has one, then drag or type it to the bars on your arrangement map. Name them Intro, Pass 1, Pass 2 and Outro."),
             ("Mixer, automation and bounce", "Press X for the Mixer and set levels and pan. Press A to show automation. Keep the melody clear above the chords, and keep the master out of the red. "
              "Then File › Bounce › Project or Section (Command-B), MP3 or WAV, for the whole track. In Finder, Control-click the .logicx and choose Compress.")]
PRESENT_CHECK = [f"Files named {FILE_NAME}; the .mp3 or .wav and the zipped .logicx handed in",
                 "Reflection page done (page @REFLECT)", "Three questions for classmates written",
                 "Rubric self-score done (page @RUBRIC)"]
VOCAB_PROMPT = "Where it shows up in my track:"
TN1_EXTRA = (
    '<div class="box acc-b" style="margin-top:4pt"><span class="k">Where this kit helps with each struggle</span><ul style="margin:0">'
    '<li style="font-size:12pt;margin-bottom:3pt">Chords that clash: the chord tables (pages @CHORDS1–@CHORDS2) list the melody’s downbeat note, the chord tones and any passing notes for every bar.</li>'
    '<li style="font-size:12pt;margin-bottom:3pt">Numerals and names: the chord key on page @CHORDS2 gives every chord in C and in G with its Roman numeral and notes.</li>'
    '<li style="font-size:12pt;margin-bottom:3pt">The octave: the note chart (pages @CHART1–@CHART2) lists every note in both keys, and the Logic quick reference (page @LOGICREF) explains Logic’s octave names.</li>'
    '<li style="font-size:12pt;margin-bottom:0">The EDM pump: the groove cards (page @GROOVES) draw the kick and the ducking, and the quick reference (page @LOGICREF) names the side chain setting.</li></ul></div>')
TN1_SIZE = 12.0
PROJ_SIZE = 11.4
VOCAB_GAP = 8
LOGIC_SIZE = 8.7
PROJ1_EXTRA = ""
RUBRIC_EXTRA = ""

# ================================================================ the worked example: an invented ballad in G major at 72 BPM
EX_BAR_S = bar_len(EX_BPM)
EX_WEAK = "I will put nice chords under the tune and make it sound sad and slow."
EX_STRONG = ("My track is a ballad in G major at 72 BPM in 4/4. One bar lasts 240 ÷ 72 = 3.333 seconds, so one 16-bar pass lasts 53.33 seconds and the 40-bar track lasts 133.33 seconds. "
             "The intro is bars 1 to 4, Pass 1 is bars 5 to 20, Pass 2 is bars 21 to 36 and the outro is bars 37 to 40. The melody’s pickup is on beat 4 of bar 4. "
             "I use the ballad table: Imaj7, Vsus4, vi7 and IVmaj7, then ii7 and iii7 in the second half. Every downbeat note is a chord tone: the A in bar 2 is the fifth of Dsus4, and the E in bar 4 is the third of Cmaj7.")
EX_QUESTIONS = ["Which chord changed the mood the most, and why?",
                "Did the melody always sound like it belonged? Which bar felt strange, if any?",
                "Did the second pass feel bigger than the first? What made it feel that way?"]
EX_MIX = ("The pad and the piano stay under the melody; the bass holds one root a bar and is cut below 40 Hz with a Channel EQ, if I have it; the hat is very quiet; "
          "in Pass 2 a high pad doubles the melody an octave up; the reverb on the last chord rings out over bars 39 and 40")
EX_SEC_NOTES = ["A soft pad plays Gmaj7 for four bars; the melody’s pickup comes in on beat 4 of bar 4", "The melody on piano over the ballad chords; bass and a light kick and shaker join at bar 5",
                "The melody an octave higher as well; fuller drums and a second pad; a counter-line in the high keys", "The last chord, Gadd9, holds; the bass plays only the root; the reverb tail rings out"]


# ================================================================ drawings (all in code, labels logged for the fit check)
def padded(body, W, H, M=10):
    """Wrap a drawing's body with M units of clear padding on all four sides (wider than the thickest outer stroke), so no edge pixel is ever inked."""
    return f'<g transform="translate({M},{M})">{body}</g>', W + 2 * M, H + 2 * M


def roll_body(notes, nsteps, bar_len, beat, lo, hi, W=1100, row_h=24, first_bar=0, chords=None, name="roll", key_w=80, head=30, fs_note=None):
    """A piano roll: rows are pitches lo..hi (MIDI numbers, black-key rows gray), columns are sixteenth notes, bars in bold, beats in gray.
    notes = [(pitch name, start, length)]; chords = [(start, length, name)]. Returns (svg body, w, h)."""
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
        elif row_h >= 14:
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
    for b in range(nsteps // bar_len):
        lbl = "pickup" if first_bar + b == 0 else str(first_bar + b)
        out.append(D.t_(x0 + (b + .5) * bar_len * cw, head - 9, lbl, 18, 700))
        D.lab(name + " bars", lbl, 18, bar_len * cw - 6)
    fs = fs_note or min(row_h - 9, 16)
    for p, s, d in notes:
        r = hi - midi(p)
        assert 0 <= r < rows, (p, lo, hi)
        x, y, w, h = x0 + s * cw + 1.2, head + r * row_h + 2.5, d * cw - 2.4, row_h - 5
        out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="4" fill="#000"/>')
        txt = p[:-1]
        if fs >= 9 and w >= D.text_w(txt, fs) + 8:
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
    return padded("".join(out), W, H, 8)


ROLL_RANGE = {"C": (midi("G3"), midi("A4")), "G": (midi("D4"), midi("E5"))}      # the rows each key's chart needs: 15 rows


def tune_roll(key, a, b, W=1100, name=None, chords=None, row_h=20):
    """Chart bars a..b-1 (0 = the pickup bar) in `key` as a roll, optionally with one style's chords (C major names)."""
    chart = CHARTS[key]
    nts = [(p, s - a * 16, d) for p, s, d in chart_bars(chart) if a * 16 <= s < b * 16]
    chs = None
    if chords:
        chs = [(((i - a) * 16), 16, chord_name(CHORDS_C[chords][i - 1], key)) for i in range(max(a, 1), b)]
    lo, hi = ROLL_RANGE[key]
    return roll_body(nts, (b - a) * 16, 16, 4, lo, hi, W, row_h, a, chs, name or f"roll {key} {a}-{b}")


def hero_body():
    """The owner's pre-made art (art/hero.png, used whole). The viewBox only trims fully transparent margin: the art's own pixels
    (x 58-1348, y 149-1324 of 1400) stay at least 40 units inside it, which --check proves from the file."""
    return (f'<image href="../art/hero.png" x="{-HX}" y="{-HY}" width="1400" height="1400"/>', HW, HH)


HX, HY, HW, HH = 0, 100, 1400, 1280


def styles_body(W=1600, name="styles"):
    """Chords of bars 1 to 8 in the three styles, one box a bar: the letter name (C major) over the Roman numeral."""
    gx = 200
    cw = (W - gx - 24) / 8
    out = []
    for i in range(8):
        lbl = f"BAR {i + 1}"
        out.append(D.t_(gx + (i + .5) * cw, 34, lbl, 24, 700, fill_=ACCENT))
        D.lab(name + " bars", lbl, 24, cw - 10)
    for r, st in enumerate(STYLES):
        y = 56 + r * 124
        lbl = STYLE_NAMES[st].upper()
        out.append(D.t_(gx - 18, y + 62, lbl, 32, 700, anchor="end"))
        D.lab(name + " rows", lbl, 32, gx - 30)
        for i in range(8):
            ch = CHORDS_C[st][i]
            x = gx + i * cw + 4
            out.append(f'<rect x="{x:.1f}" y="{y}" width="{cw - 8:.1f}" height="108" rx="8" fill="{ACC_LIGHT}" stroke="#000" stroke-width="2.5"/>')
            out.append(D.t_(x + (cw - 8) / 2, y + 50, ch, 34, 700))
            D.lab(name + " chords", ch, 34, cw - 26)
            rn = roman(ch, "C")
            out.append(D.t_(x + (cw - 8) / 2, y + 90, rn, 26, 600, fill_="#333"))
            D.lab(name + " roman", rn, 26, cw - 26)
    cap = "Chords in C major, bars 1 to 8; the second eight bars are on the chord tables"
    out.append(D.t_(W / 2, 56 + 3 * 124 + 20, cap, 24, 500))
    D.lab(name + " cap", cap, 24, W - 40)
    return padded("".join(out), W, 56 + 3 * 124 + 36, 14)


def sidechain_body(W=1500, name="sidechain"):
    """Four on the floor and the sidechain pump over two bars: a kick on every beat (top) and the pad's level, which dips at every kick and swells back (bottom)."""
    gx = 250
    gw = W - gx - 40
    bw = gw / 8
    out = []
    for k in range(8):
        x = gx + k * bw
        lbl = str(k % 4 + 1)
        out.append(D.t_(x + bw / 2, 34, lbl, 26, 700, fill_="#555"))
        out.append(f'<line x1="{x:.1f}" y1="48" x2="{x:.1f}" y2="372" stroke="{"#000" if k % 4 == 0 else "#bbb"}" stroke-width="{3 if k % 4 == 0 else 1.5}"/>')
    out.append(f'<line x1="{gx + gw:.1f}" y1="48" x2="{gx + gw:.1f}" y2="372" stroke="#000" stroke-width="3"/>')
    out.append(D.t_(gx - 20, 126, "KICK", 28, 700, anchor="end"))
    D.lab(name + " rows", "KICK", 28, gx - 34)
    for k in range(8):
        x = gx + k * bw
        out.append(f'<rect x="{x + 14:.1f}" y="82" width="{bw - 28:.1f}" height="74" rx="8" fill="{ACCENT}" stroke="#000" stroke-width="3"/>')
    out.append(D.t_(gx - 20, 296, "PAD LEVEL", 28, 700, anchor="end"))
    D.lab(name + " rows", "PAD LEVEL", 28, gx - 34)
    top, bot = 214, 346
    pts = []
    for k in range(8):
        x = gx + k * bw
        pts += [(x + 2, bot - 8), (x + bw * .12, bot - 8), (x + bw * .9, top + 4)]
    pts.append((gx + gw - 2, top + 4))
    out.append(f'<polyline points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}" fill="none" stroke="#000" stroke-width="7" stroke-linejoin="round" stroke-linecap="round"/>')
    out.append(f'<polyline points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}" fill="none" stroke="{ACCENT}" stroke-width="3.5" stroke-linejoin="round" stroke-linecap="round"/>')
    cap = "A kick on every beat turns the pad down for an instant; it swells back before the next kick."
    out.append(D.t_(gx + gw / 2, 410, cap, 26, 500))
    D.lab(name + " cap", cap, 26, W - 40)
    return padded("".join(out), W, 428, 14)


def grid_for(style, name=None, cw=26):
    meas = [{ln: GROOVES[style][ln] for ln in GROOVE_LANES}]
    return D.grid_body(name or f"grid {style}", meas, [STYLE_NAMES[style] + " groove"], GROOVE_LANES, cw=cw, ch=26, gut=100, ls=20, accent_from=0)


def groove_body(name="groove"):
    parts = [grid_for(s, f"{name} {s}") for s in STYLES]
    return D.stack(parts, 14)


def map_body(W=1500, with_time=False, name="map", lf=23, lh=40):
    """The arrangement map: 8 elements (rows) x 4 sections (columns). A cell is filled when the element plays in that section and says what it does there."""
    gx = 350
    pw = W - gx - 30
    cw = pw / 4
    hh = 100 if with_time else 74
    out = []
    for i, nm in enumerate(SEC_NAMES):
        cx = gx + (i + 0.5) * cw
        l1 = nm.upper()
        l2 = f"bars {start_bar(i)}–{end_bar(i)}"
        out.append(D.t_(cx, 32, l1, 26, 700))
        D.lab(name + " heads", l1, 26, cw - 14)
        out.append(D.t_(cx, 60, l2, 21, 500, fill_="#555"))
        D.lab(name + " bars", l2, 21, cw - 14)
        if with_time:
            l3 = f"{fmt(start_s(EX_BPM, i))}–{fmt(start_s(EX_BPM, i + 1))} s".replace(".333", ".33").replace(".667", ".67")
            l3 = f"{dec(start_s(EX_BPM, i), 2)}–{dec(start_s(EX_BPM, i + 1), 2)} s"
            out.append(D.t_(cx, 88, l3, 21, 500, fill_=ACCENT))
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
    out.append(D.t_(gx - 16, yb + 32, lbl, lf, 700, anchor="end", fill_=ACCENT))
    D.lab(name + " rows", lbl, lf, gx - 30)
    for i in range(4):
        out.append(D.t_(gx + (i + 0.5) * cw, yb + 34, str(ELEM_PLAYING[i]), 34, 700))
    if with_time:
        cap = f"{TOTAL_BARS} bars at {EX_BPM} BPM in 4/4: {TOTAL_BARS} × {num(bar_len(EX_BPM), 3)} s = {dec(total_s(EX_BPM), 2)} seconds"
    else:
        cap = "Shaded: the element plays in that section. The second pass has the most elements, so it is the biggest."
    out.append(D.t_(gx + pw / 2, yb + 82, cap, 23, 500))
    D.lab(name + " cap", cap, 23, pw)
    return padded("".join(out), W, yb + 96, 14)


def deck_roll():
    return tune_roll("C", 0, 5, 1300, "roll deck", "pop", 24)


DRAWINGS = {"hero": hero_body, "roll": deck_roll, "styles": lambda: styles_body(1600, "styles deck"), "sidechain": lambda: sidechain_body(1500, "sidechain deck"),
            "map": lambda: map_body(1500, False, "map deck", 23, 44)}
DRAWING_PX = {"hero": 1340, "roll": 2000, "styles": 2000, "sidechain": 2000, "map": 2000}
SIDE = {"roll": ["Black bars are the melody notes", "Each chord holds the downbeat note"],
        "styles": ["Pop, ballad and EDM: one melody", "Different chords, different moods"],
        "sidechain": ["The pad ducks on every kick", "Then it swells back: the EDM pump"],
        "map": ["The second pass is the biggest", "Every element has a job"]}
# extra drawings used on pages only, rendered alone on a transparent ground by --check as well
PAGE_DRAWINGS = {"roll-1": lambda: tune_roll("C", 0, 5, 1100, "page roll 1", None, 18), "roll-2": lambda: tune_roll("C", 5, 9, 1100, "page roll 2", None, 18),
                 "roll-3": lambda: tune_roll("C", 9, 13, 1100, "page roll 3", None, 18), "roll-4": lambda: tune_roll("C", 13, 17, 1100, "page roll 4", None, 18),
                 "groove-page": lambda: groove_body("groove page"), "map-page": lambda: map_body(1500, False, "map page", 23, 38),
                 "exmap-page": lambda: map_body(1500, True, "exmap page", 23, 38), "sidechain-page": lambda: sidechain_body(1500, "sidechain page"),
                 "styles-page": lambda: styles_body(1500, "styles page")}


def label_extras():
    for fn in PAGE_DRAWINGS.values():
        fn()


# ================================================================ intro deck: (class, kind, title, body, speaker notes)
SLIDES = [
    (1, "title", "Auld Lang Syne", "Reharmonized: same tune, new chords, your style",
     "Class 1, the first minute. No audio is included in this deck. Open with the idea: you will take a traditional Scottish tune that everyone knows, enter its melody in Logic Pro, "
     "and put new chords under it in a pop, ballad or EDM style. The melody stays the same; the chords, the groove and the arrangement change how it feels. Nobody needs to compose a melody, "
     "and the poem's words are not used."),
    (1, "listen", "Same tune, three moods", "Think, then share|Teacher: hum the first phrase, with no audio. Now imagine it over a slow piano, a pop band and a dance beat.|"
     "What changes when the same melody sits over different chords?|What does the drum pattern tell you about the style?|Which note of the melody must the chord include?",
     "Read the scene aloud, or hum the first phrase yourself; nothing is played from a speaker. Take a few answers to each question and write the words on the board. Students will say that the chords "
     "change the mood, that the drums set the style and that the chord has to include the note the melody is holding. The project turns each of those ideas into a tool: a chord table, a groove card and a check."),
    (1, "bullets", "What is the Reharmonized project?", "Enter a public-domain melody from a note chart|Choose pop, ballad or EDM chords for 16 bars|"
     "Check that every downbeat note is a chord tone|Build a groove and arrange 40 bars",
     "The project in four lines. Every student enters the traditional tune of Auld Lang Syne from a chart, in C major or G major. They choose a style and a chord table, or write their own, and check "
     "that the melody note on each downbeat is a chord tone. They build a groove and arrange the tune twice between a short intro and a short outro, then mix and present. The poem's words are not printed."),
    (1, "days", "Three classes", "",
     "The shape of the project. Class 1: the think-and-share, the melody and the chords. Class 2: finish the melody, enter the chords, build the groove. Class 3: arrange the sections, mix, bounce, "
     "present and reflect. With two classes, plan the tempo, melody and chords in Class 1 and build everything else in Class 2; with four, add a day for the arrangement and the mix. "
     "Hand out the tempo table, the note charts and the chord tables now."),
    (1, "pic", "The melody in a piano roll", "roll",
     f"Class 1. This is the start of the melody in Logic's Piano Roll: the pickup on beat 4, then bars 1 to 4, with the pop chords underneath. The black bars are the notes, the bold lines are bars and the gray lines are beats. "
     f"Point out that all of the notes come from five pitches, C, D, E, G and A, so the tune is pentatonic. The full chart in C major and G major is on pages {pg('chart1')} and {pg('chart2')}; "
     f"check against it, bar by bar, as you enter the notes."),
    (1, "bullets", "A chord fits when it holds the note", "The melody note on beat 1 must be in the chord|Chord tones are the root, third, fifth and seventh|Other notes in the bar can pass through|Name each chord by Roman numeral and letter",
     f"Class 1, the key idea. Play a melody note, then play a chord that contains it, and then a chord that does not: students hear the difference. A chord tone is a note of the chord, such as C, E and G in C major. "
     f"A passing note is a melody note that is not in the chord but moves on, usually on a weaker beat. Roman numerals name a chord by its place in the key: in C major, I is C, V is G, vi is Am and IV is F. "
     f"The chord tables are on pages {pg('chords1')} and {pg('chords2')}."),
    (2, "pic", "Three styles, three chord loops", "styles",
     f"Class 2. The same first eight bars of the melody with three sets of chords. Pop uses the I–V–vi–IV loop, C, G, Am and F. The ballad uses added 7ths and suspended chords, such as Cmaj7, Gsus4 and Am7, for a softer, leaning sound. "
     f"The EDM table starts on the minor chord, Am, and loops vi–V–I–IV. Each table checks that the downbeat note is a chord tone. The full 16-bar tables, in C and in G, are on pages {pg('chords1')} and {pg('chords2')}."),
    (2, "pic", "Four on the floor and the sidechain pump", "sidechain",
     f"Class 2. In an EDM groove the kick plays on every beat, which is four on the floor. A sidechain compressor listens to the kick and turns the pad and bass down for an instant each time it hits, "
     f"then they swell back, so the track seems to breathe. The groove cards for the three styles are on page {pg('grooves')}. In Logic, put a Compressor on the pad or bass and choose the kick as its side chain, "
     f"if your version's Compressor has that menu; otherwise draw volume automation that dips on every beat."),
    (2, "steps", "Build it in Logic", "Set the tempo; keep 4/4|Enter the melody in the Piano Roll|Add the chords on a second track|Build the drums and the bass from the groove card|Add the sidechain pump for EDM",
     f"Class 2. Demonstrate on the projector. Set the tempo from the tempo table and keep 4/4. Enter the melody in the Piano Roll, remembering that Logic calls middle C C3 where the chart says C4. "
     f"Add the chords on a second track, then the drums and the bass from the groove card. Menu names and button places move between Logic versions; the quick reference on page {pg('logicref')} hedges where they do, "
     f"and says which tools to use only if your version has them."),
    (3, "pic", "Arrange 40 bars in four sections", "map",
     f"Class 3. This is the arrangement map: eight elements down the side and four sections across, an intro of 4 bars, Pass 1 of 16, Pass 2 of 16 and an outro of 4. A shaded cell means the element plays in that section. "
     f"Count the elements playing in each section: 2, 6, 7 and 3. The second pass has the most, so it is the biggest. At 72 BPM one bar lasts 3.333 seconds and the track lasts 133.33 seconds. "
     f"The map is on page {pg('map')} and the tempo table on page {pg('tempo')}."),
    (3, "check", "What you turn in", "Bounced .mp3 or .wav, 40 bars long|Zipped .logicx project|Named: Your Name – Reharmonized|Chord table with numerals and letter names|"
     "Reflection page|Rubric self-score and three questions",
     "Class 3. The submission checklist, shortened to fit the slide. Show where students hand in. The file name is Your Name, then Reharmonized. Check the length before students bounce: "
     "the bounce should run the whole track, which is 40 bars, or 133.33 seconds at 72 BPM, 96 seconds at 100 BPM and 75 seconds at 128 BPM."),
    (3, "rubric", "How it’s scored", "",
     "The rubric: five categories, each scored 1 to 5, for a total out of 25. Students score themselves first; the final grade is the average of their score and yours. "
     "The slide reads the 5 column of each category aloud. Hand out the rubric page so students can self-score before they present."),
    (3, "bullets", "Presentation day", "Play your track from the top|Say your style, key and tempo|Explain one chord and why it fits its downbeat|Answer at least 2 of each classmate’s questions",
     "Class 3, presentations. Each student plays the track from the top and names the style, the key and the tempo. Then each student picks one chord, says its Roman numeral and letter name and explains why it fits the melody note "
     "on its downbeat. Students write three questions they want classmates to answer, and answer at least two of each classmate's. Ask the class to say which chord changed the mood most."),
    (3, "closer", "One last thing…", "Keep the tune.|Change the chords.|Change the feeling.|Keep old friends close.",
     "Close with the listening day: play a track and ask the class to name its style and call out the chord that changed the mood most. The song is about remembering friends and good times, "
     "and a reharmonization is a way to hear an old tune freshly. Ask a few students which chord they would keep. No audio is included in this resource; the sounds are the students' own."),
]
SHOTS1 = [("pacing", "Pacing guide", "3 class periods, slide by slide"), ("chart1", "Note chart", "A public-domain melody in two keys"),
          ("chords1", "Chord tables", "Pop and ballad, bar by bar")]
SHOTS2 = [1, 5, 7, 8, 10, 12]
SHOTS3 = [("tempo", "Tempo table"), ("chart1", "Note chart"), ("chords1", "Chord tables"), ("grooves", "Groove cards"), ("map", "Arrangement map"),
          ("mix", "Mix checklist"), ("example", "Worked example"), ("rubric", "Rubric")]
PREVIEW_PICKS = ["pacing", "chart1", "chords1", "rubric"]

COVER_A = "New chords under an old tune"
COVER_C = "Logic Pro · Pop, ballad or EDM · Chord tables"
PDF_COVER = dict(a=26, b=38, c=15, art=5.0)
SQ_COVER = dict(a=36, b=134, c=27, art=400, gap=20)
SQ_B_LINES = ["Auld Lang Syne", "Reharmonized"]
SQ_SUB = "3 class periods · a public-domain melody · intro slides"
SQ_HEADS = {1: ("Ready to teach Monday", 76, "Pacing, note chart, chord tables and the /25 rubric in one PDF", 28),
            2: ("Intro deck included", 76, f"{len(SLIDES)} editable slides (.pptx + PDF) with speaker notes on every slide", 28),
            3: ("Everything inside", 72, "Tempo table, chords, groove cards, arrangement map and worked example", 28)}
SQ_BANDS = {1: "Melody <em>·</em> chords <em>·</em> groove <em>·</em> arrangement",
            2: "Chord tables <em>·</em> groove cards <em>·</em> arrangement map",
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
             ("Student pages", "tempo", "reflect", "Tempo table, note charts, chord tables, groove cards, arrangement map, mix checklist, "
              "project sheet (3 pages), rubric, vocabulary, feedback planner, reflection page"),
             ("Intro deck (separate file)", None, None, f"{len(SLIDES)} slides, .pptx + PDF, speaker notes on every slide")]
    trs = "".join(f"<tr><td><b>{a}</b></td><td style='white-space:nowrap'>{('pages ' + str(D.IX(f)) + '–' + str(D.IX(l))) if f else 'deck'}</td>"
                  f"<td>{u}</td></tr>" for a, f, l, u in parts)
    inner = (f'<div class="cols"><div>'
             f'{D.H2("What this is", True)}'
             f'<p style="font-size:12pt;line-height:1.45">A {CLASSES}-class-period reharmonizing project for high school music technology. Every '
             f'student enters the traditional tune of “Auld Lang Syne” in Logic Pro from a note chart, puts new chords under it in a pop, ballad or EDM style, builds a groove, '
             f'arranges 40 bars, mixes, presents and reflects. It is an original Hudson Beat project, and the melody is in the public domain.</p>'
             f'{D.H2("Quick start")}<ol>'
             f'<li style="margin-bottom:5pt">Read the pacing guide (page {D.IX("pacing")}) and the teacher notes (pages {D.IX("tn1")}–{D.IX("tn2")}).</li>'
             f'<li style="margin-bottom:5pt">Look at the tempo table, the note charts and the chord tables (pages {D.IX("tempo")}–{D.IX("chords2")}) and the setup (page {D.IX("setup")}).</li>'
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
             f'<li><b>Pace:</b> Class 1 is the tempo, the melody and the chords, Class 2 the groove, Class 3 the arrangement, the mix and the presentations (page {D.IX("pacing")}); the pacing page also shows two and four periods.</li>'
             f'<li><b>Grading:</b> the rubric, /{RUBRIC_TOTAL}, the average of the student’s and your score (page {D.IX("rubric")}).</li></ul>'
             f'<div class="box" style="margin-top:6pt"><span class="k">In one sentence</span><p style="margin:0;font-size:12pt">Students learn that '
             f'a melody can wear different chords: a chord fits when it holds the melody’s downbeat note, and the style comes from the chords, the groove and the arrangement.</p></div>'
             f'<p class="small" style="margin-top:6pt">Logic Pro is a product of Apple Inc. This resource is not affiliated with Apple.</p>'
             f'</div></div>')
    return D.page("How to use this resource", "START HERE", "Teacher", inner, n, key="howto")


def overview_page(n, wm=False):
    inner = (f'<div class="cols"><div>'
             f'<div class="box inv" style="margin-bottom:6pt"><span class="k">The project in one line</span><p style="margin:0;font-size:12pt">'
             f'<b>{TITLE}</b> · Reharmonizing · Logic Pro<br>One melody, three styles, your chords.</p></div>'
             f'{D.H2("What students make")}'
             f'<p style="font-size:12.2pt;line-height:1.48">A 40-bar track in Logic Pro: a 4-bar intro, the 16-bar tune twice and a 4-bar outro. The melody is entered from the note chart in C major or G major. '
             f'The chords come from the pop, ballad or EDM table, or are the student’s own, and every chord holds the melody note on its downbeat. Students name each chord by Roman numeral and by letter, '
             f'build a groove, mix, and hand in a bounced file and the zipped .logicx project, plus their chord table and a reflection, then play the track and take questions.</p>'
             f'{D.H2("What this project reinforces")}<p style="font-size:12pt;line-height:1.5">{TN_REINFORCES}</p>'
             f'{D.H2("Standards")}<p style="font-size:11.4pt">Supports the National Core Arts Standards for Music (Music Technology, high school): generating '
             f'and developing ideas (MU:Cr1.1, MU:Cr2.1), presenting work (MU:Pr6.1) and responding to it (MU:Re7.2).</p>'
             f'</div><div>'
             f'{D.H2("Goals", True)}<ul>' + "".join(f"<li style='font-size:12pt;line-height:1.45'>{g}</li>" for g in GOALS) + '</ul>'
             f'{D.H2("About the tune")}<div class="box acc-b" style="padding:5pt 9pt"><p style="margin:0 0 3pt;font-size:10pt;line-height:1.34">{THEME}</p>'
             f'<p style="margin:0;font-size:10pt;line-height:1.34">{SOURCE_NOTE}</p></div>'
             f'<div class="box" style="margin-top:6pt;padding:5pt 9pt"><span class="k">At a glance</span><p style="margin:0;font-size:10.2pt;line-height:1.38"><b>Grades</b> {GRADES_TEXT}, music technology or music production · '
             f'<b>Length</b> {CLASSES} class periods (two and four also shown) · <b>Software</b> Logic Pro · <b>You supply</b> Macs with Logic Pro, headphones and a place to hand in files · '
             f'<b>Assessment</b> rubric, 5 categories scored 1–5, /{RUBRIC_TOTAL} (page {D.IX("rubric")})</p></div>'
             f'</div></div>')
    return D.page("Project overview", "OVERVIEW", "Reharmonizing project", inner, n, key="overview")


def setup_page(n, wm=False):
    inner = (f'<style>.sb p, .sb li {{ font-size: 11.6pt; line-height: 1.44; margin-bottom: 5pt; }}</style><div class="cols"><div class="big sb">'
             f'{D.H2("You need", True)}<ul>'
             f'<li><b>A Mac with Logic Pro</b> for each student, and <b>headphones</b>.</li>'
             f'<li><b>A place to hand in</b> the .mp3 or .wav files, the zipped .logicx and the reflection.</li>'
             f'<li><b>The tempo table, note charts and chord tables</b>, printed (pages {D.IX("tempo")}–{D.IX("chords2")}), or shown on the projector.</li>'
             f'<li><b>Printed student pages</b>, one set each (pages {D.IX("tempo")}–{D.IX("reflect")}).</li>'
             f'<li><b>A MIDI keyboard</b> is optional: the notes can be drawn in the Piano Roll. Nobody has to read music, only the note chart.</li></ul>'
             f'{D.H2("Before Class 1")}'
             + "".join(D.chk(c, 13, "font-size:11.6pt;margin-bottom:7pt") for c in [
                 f"Read the note chart (pages {D.IX('chart1')}–{D.IX('chart2')}) and enter its first four bars in Logic so you know how long it takes.",
                 f"Open Logic Pro on a student computer and check which tools your version has: Alchemy, Drum Machine Designer, Step Sequencer, Chord Track, Session Players, Compressor side chain (see page {D.IX('logicref')}).",
                 f"Check that you can add a marker and draw volume automation.",
                 f"Read the worked example (pages {D.IX('example')}–{D.IX('example2')})."]) +
             f'</div><div class="big sb">'
             f'{D.H2("What to watch", True)}'
             f'<p style="font-size:11.4pt">Watch for melodies entered an octave off, chords that do not hold the downbeat note, Roman numerals copied from the wrong key, a bass line that fights the kick and a melody buried under the chords. {TN_NOTE}</p>'
             f'<div class="box acc-b" style="margin-top:2pt"><span class="k">Ideas for the room</span><ul style="margin:0">'
             f'<li style="font-size:11.2pt">Ask while students work: is that downbeat note in the chord? What would a different chord do to the mood?</li>'
             f'<li style="font-size:11.2pt">Say the theme plainly: the song is about remembering friends and good times, and the project is about how chords change a tune’s feeling.</li>'
             f'<li style="font-size:11.2pt">A student who is stuck can enter the melody once and use the pop table in C major: that already works.</li></ul></div>'
             f'{D.H2("The tune")}'
             f'<div class="box"><p style="margin:0;font-size:10.8pt;line-height:1.4">The traditional Scottish tune is in the public domain worldwide. The poem’s words are not printed, so students work from the melody alone. '
             f'If a student wants to use another tune, check its first publication date: in 2026 it must be 1930 or earlier.</p></div>'
             f'<div class="box" style="margin-top:6pt"><span class="k">Keep the volume moderate</span><p style="margin:0;font-size:11pt;line-height:1.4">'
             f'A loud kick and a pumping pad can be tiring in headphones. Tell students to start low and check the final mix at a normal level.</p></div>'
             f'</div></div>')
    return D.page("Setup and what to watch", "SETUP", "Teacher", inner, n, key="setup")


# ================================================================ the tempo table, note charts, chord tables, groove cards, arrangement map and mix pages
def tempo_a_rows():
    hint = {66: "Ballad", 72: "Ballad", 80: "Ballad or slow pop", 100: "Pop", 110: "Pop", 120: "Pop or EDM", 124: "EDM", 128: "EDM"}
    rows = []
    for bpm in TEMPOS:
        hi = ' class="hi"' if bpm in STYLE_BPM.values() else ''
        rows.append(f"<tr{hi}><td>{bpm}</td><td>{dec(spb(bpm), 3)}</td><td>{dec(bar_len(bpm), 3)}</td><td>{dec(pass_s(bpm), 2)}</td><td>{dec(total_s(bpm), 2)}</td>"
                    f"<td class='l'>{hint[bpm]}</td></tr>")
    return "".join(rows)


def tempo_b_rows():
    rows = []
    for st in ("ballad", "pop", "edm"):
        bpm = STYLE_BPM[st]
        rows.append(f"<tr><td><b>{bpm}</b></td><td>{STYLE_NAMES[st]}</td><td>{dec(start_s(bpm, 1), 2)}</td><td>{dec(start_s(bpm, 2), 2)}</td><td>{dec(start_s(bpm, 3), 2)}</td>"
                    f"<td><b>{dec(total_s(bpm), 2)}</b></td></tr>")
    return "".join(rows)


def tempo_page(n, wm=False):
    inner = (CSS_CC +
             f'<p style="margin:0 0 4pt;font-size:10.2pt;line-height:1.36">Step 1: choose style and tempo. In 4/4 there are 4 beats in a bar. These formulas turn a tempo into seconds and bars. '
             f'Every number below is computed, so you can check your own arithmetic against it. The track is 40 bars: an intro of 4, two 16-bar passes of the tune and an outro of 4.</p>'
             f'<div class="cols" style="gap:10pt;align-items:flex-start"><div class="box acc-b" style="padding:5pt 9pt;flex:1.15"><span class="k">The formulas (4/4)</span>'
             f'<p style="margin:0 0 2pt;font-size:9.8pt"><b>Seconds per beat</b> = 60 ÷ BPM</p><p style="margin:0 0 2pt;font-size:9.8pt"><b>Seconds per bar</b> = 240 ÷ BPM</p>'
             f'<p style="margin:0 0 2pt;font-size:9.8pt"><b>One pass</b> (16 bars) = 16 × 240 ÷ BPM seconds; <b>the track</b> (40 bars) = 40 × 240 ÷ BPM</p>'
             f'<p style="margin:0 0 2pt;font-size:9.8pt"><b>A section starts at</b> (bars gone by) × 240 ÷ BPM seconds</p>'
             f'<p style="margin:0;font-size:9.8pt"><b>Example:</b> 100 BPM: 240 ÷ 100 = 2.4 s per bar, so 40 bars = 96 s.</p></div>'
             f'<div class="box" style="padding:5pt 9pt;flex:1"><span class="k">Rounding rules</span><p style="margin:0;font-size:9.2pt;line-height:1.32">Seconds per beat and per bar to 3 decimals, '
             f'and seconds for passes, section starts and the track to 2; a 5 rounds up. So 240 ÷ 72 = 3.333 seconds per bar, and the 4 bars before Pass 1 at 72 BPM last '
             f'13.33 seconds (13.333… rounds down). Every start time is rounded from its exact value.</p></div></div>'
             f'<span class="k" style="margin-top:5pt">Tempos by style: shaded rows are used for the section starts below</span>'
             f'<table class="t cc" style="margin-top:1pt"><tr><th>BPM</th><th>Seconds per beat</th><th>Seconds per bar</th><th>One pass (s)</th><th>40-bar track (s)</th><th>Good for</th></tr>{tempo_a_rows()}</table>'
             f'<p class="small" style="margin:0 0 2pt;font-size:8.6pt">Pop sits between 96 and 120 BPM, a ballad between 60 and 80 and EDM between 120 and 128. Any tempo works for the math; these are the ones that fit the styles.</p>'
             f'<span class="k" style="margin-top:3pt">Where does each section start? One tempo for each style</span>'
             f'<table class="t cc" style="margin-top:1pt"><tr><th rowspan="2">BPM</th><th rowspan="2">Style</th><th colspan="3">Section starts at (seconds)</th><th rowspan="2">Track ends (s)</th></tr>'
             f'<tr><th>Pass 1 (bar 5)</th><th>Pass 2 (bar 21)</th><th>Outro (bar 37)</th></tr>{tempo_b_rows()}</table>'
             f'<p class="small" style="margin:0 0 3pt;font-size:8.6pt">The intro starts at bar 1 (0 seconds). The melody’s one-beat pickup is on beat 4 of bar 4, one beat before Pass 1 starts, and it comes in again on beat 4 of bar 20.</p>'
             f'<div class="box acc-b" style="padding:5pt 9pt"><span class="k">My style and tempo</span>'
             f'<div class="fl" style="margin:3pt 0 3pt;font-size:10pt"><b>Style (pop, ballad or EDM):</b><span></span><b>Key (C or G):</b><span></span><b>Tempo:</b><span></span><b>BPM</b></div>'
             f'<div class="fl" style="margin:0;font-size:10pt"><b>One bar = 240 ÷ BPM =</b><span></span><b>s</b><b style="margin-left:8pt">Track = 40 × one bar =</b><span></span><b>s</b></div></div>')
    return D.page("Tempo table", "STUDENT", "Class 1", inner, n, wm, name=True, key="tempo")


def key_table_rows(a, b):
    rows = ""
    for i in range(a, b + 1):
        c, g = CHART_C[i], CHART_G[i]
        rows += f"<tr><td style='width:7%'><b>{'0' if i == 0 else i}</b></td><td>{bar_text(c)}</td><td>{bar_text(g)}</td></tr>"
    return (f'<style>table.tt td, table.tt th {{ padding: 1.5pt 5pt; }}</style><table class="t tt" style="font-size:8.6pt;line-height:1.18;margin:3pt 0 3pt">'
            f'<tr><th>Bar</th><th>C major (do = C4)</th><th>G major (do = G4)</th></tr>{rows}</table>')


def roll_html(names):
    return "".join(f'<div style="margin:0 0 3pt">{D.body_svg(PAGE_DRAWINGS[k]())}</div>' for k in names)


def chart1_page(n, wm=False):
    inner = (f'<p style="margin:0 0 3pt;font-size:10.2pt;line-height:1.34"><b>Auld Lang Syne</b>, part 1 of 2: the pickup and bars 1–8 · traditional Scottish tune, a public-domain melody '
             f'(first documented with Burns’s words in 1799) · 4/4 · 16 bars and a one-beat pickup · {note_count()} notes in all · five different pitches in each key</p>'
             + roll_html(["roll-1", "roll-2"]) + key_table_rows(0, 8) +
             f'<div class="box acc-b" style="margin-top:3pt;padding:4pt 10pt"><span class="k">About this chart</span><p style="margin:0;font-size:9.4pt;line-height:1.3">'
             f'Step 2: enter the melody. The chart shown is C major; the table also lists G major, the same notes moved up 7 semitones. Bar 0 is the <b>pickup bar</b>: three beats of rest, then one note on beat 4. '
             f'Pitch names run down the left; middle C is C4 here, but Logic calls it C3, so subtract one from the octave number when you read your Piano Roll. Bold lines are bars and gray lines are beats. '
             f'A dotted quarter is one and a half beats.</p></div>')
    return D.page("Note chart · the melody, 1 of 2", "STUDENT", "Class 1", inner, n, wm, name=True, key="chart1")


def chart2_page(n, wm=False):
    inner = (f'<p style="margin:0 0 3pt;font-size:10.2pt;line-height:1.34"><b>Auld Lang Syne</b>, part 2 of 2: bars 9–16 · the second half of the tune, which begins with a pickup note on beat 4 of bar 8</p>'
             + roll_html(["roll-3", "roll-4"]) + key_table_rows(9, 16) +
             f'<div class="box acc-b" style="margin-top:3pt;padding:4pt 10pt"><span class="k">About this chart</span><p style="margin:0;font-size:9.4pt;line-height:1.3">'
             f'Step 2: enter the melody. Bars 5, 9 and 13 start alike, and bars 6, 10 (apart from its last note) and 14 do too, so you can copy a region and edit it. Bar 16 ends on a long note and a beat of rest; '
             f'the rest is where the pickup of the next pass comes in, so the pickup bar and bar 16 together add up to one bar. Every note comes from five pitches, so the tune is pentatonic.</p></div>'
             f'<div class="box" style="margin-top:3pt;padding:4pt 10pt"><span class="k">Where the notes come from</span><p style="margin:0;font-size:9pt;line-height:1.28">'
             f'The notes were typed in C major and in G major, and checked note by note against two public-domain sources: a 4/4 transcription of the melody in F major (the English Wikipedia article “Auld Lang Syne”) '
             f'and the melody line of Brigid Baker’s edition on the Choral Public Domain Library, both moved to C major. Other editions vary some pickup notes and rhythms; this chart follows the plain 4/4 version.</p></div>')
    return D.page("Note chart · the melody, 2 of 2", "STUDENT", "Class 1", inner, n, wm, name=True, key="chart2")


def chord_rows(style):
    rows = ""
    for i in range(1, NBARS + 1):
        ch = CHORDS_C[style][i - 1]
        dbc, dbg = downbeat(CHART_C, i), downbeat(CHART_G, i)
        tones_c = " ".join(chord_letters(ch, "C"))
        tones_g = " ".join(chord_letters(ch, "G"))
        pc_ = " ".join(passing(style, i, "C")) or "none"
        pg_ = " ".join(passing(style, i, "G")) or "none"
        role = role_of(pc_of(dbc), ch, "C")
        rows += (f"<tr><td><b>{i}</b></td><td>{dbc[:-1]} · {dbg[:-1]}</td><td><b>{chord_name(ch, 'C')}</b> · <b>{chord_name(ch, 'G')}</b></td><td>{roman(ch, 'C')}</td>"
                 f"<td>{tones_c} · {tones_g}</td><td>{role}</td><td>{pc_} · {pg_}</td></tr>")
    return rows


def chord_table(style, size=8.4):
    return (f'<span class="k" style="margin:4pt 0 1pt;font-size:12pt">{STYLE_NAMES[style]} · {STYLE_TEMPO[style]}</span>'
            f'<p style="margin:0 0 2pt;font-size:9pt;line-height:1.26">{STYLE_FEEL[style]}</p>'
            f'<style>table.ct td, table.ct th {{ padding: 1pt 3pt; text-align: center; }}</style>'
            f'<table class="t ct" style="font-size:{size}pt;line-height:1.1;margin:0"><tr><th>Bar</th><th>Beat 1 note (C · G)</th><th>Chord (C · G)</th><th>Numeral</th><th>Chord tones (C · G)</th>'
            f'<th>Beat 1 is the</th><th>Passing notes (C · G)</th></tr>{chord_rows(style)}</table>')


def chords1_page(n, wm=False):
    inner = (f'<p style="margin:0 0 2pt;font-size:9.6pt;line-height:1.3">Step 3: choose chords. One chord a bar over the 16 bars of the tune. Each row gives the melody note on beat 1 in C major and in G major, '
             f'the chord in both keys, its Roman numeral, the chord tones, and which part of the chord the beat 1 note is. Every beat 1 note is a chord tone. <b>Passing notes</b> are the other melody notes in the bar '
             f'that are not in the chord; they move on and are not a problem. Use the pop table or the ballad table, or write your own and check each bar the same way.</p>'
             + chord_table("pop") + chord_table("ballad"))
    return D.page("Chord tables · pop and ballad", "STUDENT", "Classes 1–2", inner, n, wm, name=True, key="chords1")


def key_rows():
    used = {}
    for st in STYLES:
        for ch in CHORDS_C[st]:
            used.setdefault(ch, [])
            if STYLE_NAMES[st] not in used[ch]:
                used[ch].append(STYLE_NAMES[st])
    order = sorted(used, key=lambda c: (ROOT_PC_C[c[0]], c))
    rows = ""
    for ch in order:
        rows += (f"<tr><td><b>{chord_name(ch, 'C')}</b></td><td>{roman(ch, 'C')}</td><td>{' '.join(chord_letters(ch, 'C'))}</td><td><b>{chord_name(ch, 'G')}</b></td>"
                 f"<td>{' '.join(chord_letters(ch, 'G'))}</td><td>{', '.join(used[ch])}</td></tr>")
    return rows, len(order)


def chords2_page(n, wm=False):
    rows, nk = key_rows()
    inner = (f'<p style="margin:0 0 2pt;font-size:9.6pt;line-height:1.3">Step 3: choose chords, continued. The EDM table is read the same way as the others (page {pg("chords1")}). '
             f'Below it is the chord key: every chord used on these pages, in C major and in G major.</p>'
             + chord_table("edm") +
             f'<span class="k" style="margin:5pt 0 1pt;font-size:12pt">Chord key · {nk} chords</span>'
             f'<style>table.ck td, table.ck th {{ padding: 1pt 4pt; text-align: center; }}</style>'
             f'<table class="t ck" style="font-size:8.6pt;line-height:1.12;margin:0"><tr><th>Chord in C</th><th>Numeral</th><th>Notes in C</th><th>Chord in G</th><th>Notes in G</th><th>Used in</th></tr>{rows}</table>'
             f'<div class="cols" style="gap:9pt;margin-top:4pt;align-items:flex-start"><div class="box acc-b" style="padding:4pt 9pt"><span class="k">How to check a chord</span>'
             f'<p style="margin:0;font-size:9pt;line-height:1.28">1. Find the melody note on beat 1 (page {pg("chart1")} or {pg("chart2")}). 2. List the chord’s notes (the key above). 3. Is the note in the list? '
             f'If yes, the chord fits. If not, change the chord. 4. Name it: count the root in the key’s scale (the numeral), then write the letter name.</p></div>'
             f'<div class="box" style="padding:4pt 9pt"><span class="k">Reading the names</span><p style="margin:0;font-size:9pt;line-height:1.28">A capital numeral is a major chord and lower case is minor. '
             f'<b>7</b> adds the seventh, <b>maj7</b> the major seventh, <b>sus4</b> swaps the third for the fourth and <b>add9</b> adds the ninth, a step above the root.</p></div></div>')
    return D.page("Chord tables · EDM and the chord key", "STUDENT", "Class 2", inner, n, wm, name=True, key="chords2")


def groove_card(st):
    body, w, h = grid_for(st, cw=30)
    t1, t2, t3 = GROOVE_TEXT[st]
    txt = (f'<p style="margin:0 0 2pt;font-size:9.2pt;line-height:1.26"><b>Drums.</b> {t1}</p>'
           f'<p style="margin:0 0 2pt;font-size:9.2pt;line-height:1.26"><b>Bass and chords.</b> {t2}</p>'
           f'<p style="margin:0;font-size:9.2pt;line-height:1.26"><b>Try.</b> {t3}</p>')
    head = f'<span class="k" style="font-size:12.5pt;margin:0">{STYLE_NAMES[st]} groove · {STYLE_TEMPO[st]}</span>'
    return (f'<div class="box" style="margin-bottom:4pt;padding:4pt 10pt">{head}<div style="display:flex;gap:12pt;margin-top:2pt;align-items:flex-start">'
            f'<div style="flex:1">{txt}</div><div style="width:3.35in;flex:0 0 3.35in">{D.body_svg(padded(body, w, h, 8))}</div></div></div>')


def grooves_page(n, wm=False):
    inner = (f'<p style="margin:0 0 3pt;font-size:10pt;line-height:1.34">Step 4: build the groove. Each card is a one-bar drum pattern (16 steps, 4 to a beat; shaded steps are the beats). '
             f'Click it into a Drum Machine Designer track (or draw it in the Piano Roll with the grid on 1/16) and repeat it for the whole track. The {GROOVE_SNARE["ballad"].lower()} and the clap sit on the snare lane.</p>'
             + "".join(groove_card(s) for s in STYLES) +
             f'<div style="width:5.7in;margin:2pt auto 2pt">{D.body_svg(PAGE_DRAWINGS["sidechain-page"]())}</div>'
             f'<div class="box acc-b" style="padding:5pt 10pt"><span class="k">EDM: the sidechain pump</span><p style="margin:0;font-size:9.8pt;line-height:1.32">'
             f'Add a Compressor to the pad or the bass and choose the kick as its side chain (see page {pg("logicref")}). Lower the threshold until the pad ducks on every kick. '
             f'No side chain menu? Draw volume automation that dips on each beat and recovers before the next.</p></div>')
    return D.page("Groove cards · pop, ballad and EDM", "STUDENT", "Class 2", inner, n, wm, name=True, key="grooves")


def map_page(n, wm=False):
    rows = ""
    for i, nm in enumerate(SEC_NAMES):
        rows += (f"<tr><td class='l'>{nm}</td><td>{SEC_BARS[i]}</td><td>{start_bar(i)}–{end_bar(i)}</td>"
                 + "".join(f"<td>{dec(start_s(b, i), 2)}</td>" for b in STYLE_BPM.values()) + "</tr>")
    rows += f"<tr><td class='l'>Total</td><td><b>{TOTAL_BARS}</b></td><td>1–{TOTAL_BARS}</td>" + "".join(f"<td><b>{dec(total_s(b), 2)}</b></td>" for b in STYLE_BPM.values()) + "</tr>"
    mine = "".join(f"<tr><td class='l' style='height:22pt'>{nm}</td><td></td><td></td><td></td><td></td><td></td></tr>" for nm in SEC_NAMES)
    bp = list(STYLE_BPM.values())
    inner = (CSS_SG +
             f'<p style="margin:0 0 4pt;font-size:10.2pt;line-height:1.36">Step 5: arrange the sections. Your track has four sections: an intro (4 bars), Pass 1 of the tune (16 bars), Pass 2 (16 bars) and an outro (4 bars), 40 bars in all. '
             f'The tune’s pickup is on beat 4 of bar 4. The map shows which elements play in each section.</p>'
             f'<div style="margin:0 0 3pt">{D.body_svg(PAGE_DRAWINGS["map-page"]())}</div>'
             f'<table class="sg" style="margin-top:3pt"><tr><th style="width:1.45in">Section</th><th>Bars</th><th>Bar numbers</th><th>Starts (s) at {bp[0]} BPM</th><th>{bp[1]} BPM</th><th>{bp[2]} BPM</th></tr>{rows}</table>'
             f'<p class="small" style="margin:2pt 0 3pt;font-size:8.6pt">The elements playing in the four sections are {", ".join(str(c) for c in ELEM_PLAYING)}, which add up to {sum(ELEM_PLAYING)}. '
             f'The second pass has the most elements, so it feels like the biggest part. The sidechain pump is for EDM tracks; other styles leave that row empty.</p>'
             f'<span class="k" style="margin-top:3pt">My map: my tempo and the numbers for each section</span>'
             f'<table class="sg" style="margin-top:2pt"><tr><th style="width:1.45in">Section</th><th>Bars</th><th>Starts at bar</th><th>Ends at bar</th><th>Starts at (s)</th><th>Lasts (s)</th></tr>{mine}</table>'
             f'<div class="fl" style="margin:4pt 0 3pt;font-size:10pt"><b>My style:</b><span></span><b>My tempo:</b><span></span><b>Total bars:</b><span></span></div>'
             f'<p class="small" style="margin:0;font-size:8.6pt">Check: your sections add up to 40 bars, and each start time is bars gone by × 240 ÷ BPM.</p>')
    return D.page("Arrangement map", "STUDENT", "Classes 2–3", inner, n, wm, name=True, key="map")


def mix_page(n, wm=False):
    def box(title, items, acc=False):
        return (f'<div class="box{" acc-b" if acc else ""}" style="padding:5pt 9pt"><span class="k">{title}</span>'
                + "".join(D.chk(c, 11, "font-size:10pt;line-height:1.3;margin-bottom:3pt") for c in items) + '</div>')
    inner = (f'<p style="margin:0 0 5pt;font-size:10.2pt;line-height:1.36">Step 6: mix and bounce. A mix keeps the melody clear over the chords and makes the second pass bigger. Work through the boxes with headphones, '
             f'then check each one off.</p>'
             f'<div class="cols" style="gap:10pt;align-items:flex-start"><div>'
             + box("Melody and chords", ["The melody is the clearest part in Pass 1 and still clear in Pass 2.", "The chords sit under the melody’s notes, not above them.",
                                         "Every downbeat note is still a chord tone when I play it with the final chords."], True)
             + '<div style="height:6pt"></div>'
             + box("Groove", ["The kick and the snare stand out; the hat is quiet.", "The bass plays the chord roots and does not fight the kick.",
                              "For EDM: the pad ducks on every kick and swells back."])
             + '</div><div>'
             + box("Arrangement", ["There is a marker at the start of each of the four sections.", "Pass 2 is bigger than Pass 1: more parts, an octave doubling or a fuller groove.",
                                   "The outro takes layers away and the last chord rings out."], True)
             + '<div style="height:6pt"></div>'
             + box("Low end and levels", ["I cut the low notes from the pad and keys (Channel EQ, if I like).", "The bass and the kick do not cover each other.",
                                          "The master level never reaches red (no clipping)."])
             + '</div></div>'
             f'<div class="box" style="margin-top:6pt;padding:5pt 9pt"><span class="k">The listening test</span><p style="margin:0 0 3pt;font-size:10pt;line-height:1.36">Play from bar 5 with your eyes closed and '
             f'rate each part from 1 (flat) to 5 (very strong). Is the melody clear? Do the chords fit the style? Does Pass 2 feel bigger than Pass 1? Write what you hear:</p>'
             f'<div class="fl" style="margin:2pt 0;font-size:10pt"><b>Melody:</b><span></span><b>Chords:</b><span></span><b>Pass 2:</b><span></span></div></div>'
             f'<div class="box acc-b" style="margin-top:6pt;padding:5pt 9pt"><span class="k">Bounce</span>'
             + "".join(D.chk(c, 11, "font-size:10pt;margin-bottom:3pt") for c in [
                 "The bounce starts at bar 1 and ends after the last bar of the outro (40 bars: " + dec(total_s(EX_BPM), 2) + " seconds at 72 BPM; check your own tempo on page " + str(pg("tempo")) + ").",
                 "MP3 or WAV bounced, and the .logicx project zipped.", f"Both files named {FILE_NAME}."]) + '</div>'
             f'<span class="k" style="margin-top:6pt">What I changed after the listening test</span>' + D.lines(7, 24))
    return D.page("Mix checklist", "STUDENT", "Class 3", inner, n, wm, name=True, key="mix")


# ================================================================ worked example (2 pages): an invented ballad in G major at 72 BPM
def ex_chord_rows():
    out = ""
    for i in range(1, NBARS + 1):
        ch = CHORDS_C[EX_STYLE][i - 1]
        db = downbeat(CHARTS[EX_KEY], i)
        out += (f"<tr><td><b>{i}</b></td><td>{db[:-1]}</td><td><b>{chord_name(ch, EX_KEY)}</b></td><td>{roman(ch, EX_KEY)}</td><td>{' '.join(chord_letters(ch, EX_KEY))}</td>"
                f"<td>{role_of(pc_of(db), ch, EX_KEY)}</td></tr>")
    return out


def ex_rows():
    out = []
    for i, nm in enumerate(SEC_NAMES):
        out.append(f"<tr><td style='text-align:left'><b>{nm}</b></td><td>{start_bar(i)}–{end_bar(i)}</td><td>{SEC_BARS[i]}</td><td>{dec(start_s(EX_BPM, i), 2)}</td><td>{dec(start_s(EX_BPM, i + 1), 2)}</td>"
                   f"<td style='text-align:left'>{EX_SEC_NOTES[i]}</td></tr>")
    return "".join(out)


def example_page(n, wm=False):
    inner = (f'<style>table.ec td {{ text-align: center; }}</style>'
             f'<p style="margin:0 0 4pt;font-size:10pt">An <b>invented plan on paper</b>: a ballad in {KEY_NAMES[EX_KEY]} at {EX_BPM} BPM. No audio is included. '
             f'Student projects will differ. Page 1 of 2: the plan and the chords.</p>'
             f'<div class="cols" style="gap:10pt;align-items:flex-start"><div class="box"><span class="k">1 · A weak plan</span><p style="margin:0;font-size:10.2pt">{EX_WEAK}</p>'
             f'<p style="margin:3pt 0 0;font-size:9.2pt">It names no key, no tempo, no chords and no checks.</p></div>'
             f'<div class="box acc-b"><span class="k">2 · A clear plan</span><p style="margin:0;font-size:8.6pt;line-height:1.28">{EX_STRONG}</p></div></div>'
             f'{D.H2("3 · The ballad chords in G major, with every downbeat checked")}'
             f'<style>table.ex3 td, table.ex3 th {{ padding: 1.4pt 4pt; }}</style>'
             f'<table class="t ec ex3" style="font-size:8.8pt;line-height:1.12"><tr><th>Bar</th><th>Beat 1 note</th><th>Chord</th><th>Numeral</th><th>Chord tones</th><th>Beat 1 is the</th></tr>{ex_chord_rows()}</table>'
             f'<p style="margin:2pt 0 0;font-size:8.8pt;line-height:1.3">All 16 beat 1 notes are chord tones. The other melody notes in a bar may pass through: for example in bar 2 the melody walks A, G, A, B over Dsus4, and only {" ".join(passing(EX_STYLE, 2, EX_KEY))} is not in the chord: '
             f'it is a weak-beat step that leads on.</p>'
             f'<div class="box acc-b" style="margin-top:6pt"><span class="k">Why these chords suit a ballad</span><p style="margin:0;font-size:10pt;line-height:1.38">'
             f'Added 7ths (Gmaj7, Em7, Cmaj7) soften each chord, and the suspended chords (Dsus4 and D7sus4) lean toward the chord that follows. The harmony changes once a bar, so the melody’s long notes have room, '
             f'and the move from Cmaj7 back to Gmaj7 in bars 4 and 5 sounds like coming home.</p></div>'
             f'<div class="box" style="margin-top:6pt"><span class="k">Try it yourself</span><p style="margin:0;font-size:10pt;line-height:1.38">Swap the ballad chord in bar 10 (Am7, ii7) for the pop chord D in G major '
             f'(the V chord). Is the melody note on beat 1 still a chord tone? Then say how the mood changes.</p></div>')
    return D.page("Worked example · the plan and the chords", "EXAMPLE", "Teacher", inner, n, wm, ak=True, key="example")


def example2_page(n, wm=False):
    qs = " ".join(f"{i + 1}. {q}" for i, q in enumerate(EX_QUESTIONS))
    inner = (f'<p style="margin:0 0 3pt;font-size:10pt">The same track, page 2 of 2: the arrangement map, the section times, the mix and the questions.</p>'
             f'{D.H2("4 · The map: 40 bars, 4 sections, 8 elements")}'
             f'<div style="width:5.6in;margin:1pt auto 3pt">{D.body_svg(PAGE_DRAWINGS["exmap-page"]())}</div>'
             f'{D.H2("5 · The four sections at 72 BPM")}'
             f'<style>table.ex5 td, table.ex5 th {{ padding: 1.6pt 4pt; }}</style>'
             f'<table class="t ec ex5" style="font-size:8.8pt;line-height:1.15"><tr><th>Section</th><th>Bars</th><th>Length (bars)</th><th>Starts (s)</th><th>Ends (s)</th><th>What happens</th></tr>{ex_rows()}</table>'
             f'<p style="margin:2pt 0 0;font-size:9pt">One beat lasts 60 ÷ {EX_BPM} = {dec(spb(EX_BPM), 3)} s and one bar lasts 240 ÷ {EX_BPM} = {dec(EX_BAR_S, 3)} s. The track has 4 + 16 + 16 + 4 = {TOTAL_BARS} bars, '
             f'which last {TOTAL_BARS} × {dec(EX_BAR_S, 3)} = {dec(total_s(EX_BPM), 2)} seconds ({mmss(total_s(EX_BPM))}).</p>'
             f'<div class="box" style="margin-top:5pt"><span class="k">6 · The mix</span><p style="margin:0;font-size:10pt;line-height:1.36">{EX_MIX}.</p></div>'
             f'<div class="box" style="margin-top:5pt"><span class="k">7 · Three feedback questions (invented)</span><p style="margin:0;font-size:10pt;line-height:1.36">{qs}</p></div>'
             f'<div class="box acc-b" style="margin-top:5pt"><span class="k">8 · Moments to point out in class</span><ul style="margin:0">'
             f'<li style="font-size:10pt;margin-bottom:2pt">The Vsus4 in bar 2 leans toward the next chord, which is why the melody’s A feels unfinished until Em7 arrives in bar 3.</li>'
             f'<li style="font-size:10pt;margin-bottom:0">Pass 2 starts at bar 21, 66.67 seconds in, with the melody doubled an octave up, so the class can hear the same notes grow.</li></ul></div>')
    return D.page("Worked example · the map, the times and the mix", "EXAMPLE", "Teacher", inner, n, wm, ak=True, key="example2")


PAGES = {"howto": howto_page, "overview": overview_page, "setup": setup_page, "example": example_page, "example2": example2_page,
         "tempo": tempo_page, "chart1": chart1_page, "chart2": chart2_page, "chords1": chords1_page, "chords2": chords2_page, "grooves": grooves_page,
         "map": map_page, "mix": mix_page}
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





BADGE = {"tempo": "Class 1", "chart1": "Class 1", "chart2": "Class 1", "chords1": "Classes 1–2", "chords2": "Class 2", "grooves": "Class 2", "map": "Classes 2–3",
         "mix": "Class 3", "present": f"Classes {CLASSES - 1}–{CLASSES}"}

FORBIDDEN_WORDS = ("cham" + "pagne", "toast", "cheers", "wine", "beer", "cocktail", "drink", "alcohol", "bub" + "bly", "church", "prayer", "pray ", "blessing", "holy", "sacred",
                   "religio", "god ", "santa", "christmas", "hanukkah", "chanukah", "kwanzaa", "resolution")
LYRIC_FRAGMENTS = ("auld acquaintance", "never brought to mind", "cup o", "cup of kindness", "my jo", "my dear", "we’ll tak", "we'll tak", "pint-stowp", "gie's a hand")

EXPECT_ROMAN = {"C": "I", "G": "V", "Am": "vi", "F": "IV", "Am7": "vi7", "Cmaj7": "Imaj7", "Gsus4": "Vsus4", "Fmaj7": "IVmaj7", "G7sus4": "V7sus4", "Dm7": "ii7",
                "Em7": "iii7", "Cadd9": "Iadd9", "Em": "iii"}
EXPECT_NAME_G = {"C": "G", "G": "D", "Am": "Em", "F": "C", "Am7": "Em7", "Cmaj7": "Gmaj7", "Gsus4": "Dsus4", "Fmaj7": "Cmaj7", "G7sus4": "D7sus4", "Dm7": "Am7",
                 "Em7": "Bm7", "Cadd9": "Gadd9", "Em": "Bm"}
EXPECT_TONES_C = {"C": "C E G", "G": "G B D", "Am": "A C E", "F": "F A C", "Am7": "A C E G", "Cmaj7": "C E G B", "Gsus4": "G C D", "Fmaj7": "F A C E", "G7sus4": "G C D F",
                  "Dm7": "D F A C", "Em7": "E G B D", "Cadd9": "C E G D", "Em": "E G B"}
EXPECT_TONES_G = {"C": "G B D", "G": "D F# A", "Am": "E G B", "F": "C E G", "Am7": "E G B D", "Cmaj7": "G B D F#", "Gsus4": "D G A", "Fmaj7": "C E G B", "G7sus4": "D G A C",
                  "Dm7": "A C E G", "Em7": "B D F# A", "Cadd9": "G B D A", "Em": "B D F#"}
EXPECT_DOWNBEATS_C = "C4 D4 C4 A4 G4 D4 C4 C4 G4 D4 G4 A4 G4 D4 C4 C4".split()


def diatonic_errors(name, key):
    """An independent check of one chord in one key: stack thirds on the key's scale (not by interval formulas) and compare with the chord's pitch classes."""
    errs = []
    sc = KEY_SCALE[key]
    r, q = split_chord(name)
    pcs = chord_pcs(name, key)
    d = sc.index(pcs[0]) if pcs[0] in sc else None
    if d is None:
        return [f"{name} in {key}: the root is not in the key's scale"]
    third, fifth, seventh, fourth, ninth = sc[(d + 2) % 7], sc[(d + 4) % 7], sc[(d + 6) % 7], sc[(d + 3) % 7], sc[(d + 1) % 7]
    want = {"": [sc[d], third, fifth], "m": [sc[d], third, fifth], "maj7": [sc[d], third, fifth, seventh], "m7": [sc[d], third, fifth, seventh],
            "sus4": [sc[d], fourth, fifth], "7sus4": [sc[d], fourth, fifth, seventh], "add9": [sc[d], third, fifth, ninth]}[q]
    if pcs != want:
        errs.append(f"{name} in {key}: pitch classes {pcs} differ from the chord stacked on the scale {want}")
    # the third's size gives the quality of a triad: 4 semitones is major, 3 is minor
    if q in ("", "maj7", "add9") and (third - sc[d]) % 12 != 4:
        errs.append(f"{name} in {key}: a major-type chord needs a major third")
    if q in ("m", "m7") and (third - sc[d]) % 12 != 3:
        errs.append(f"{name} in {key}: a minor-type chord needs a minor third")
    return errs


def verify_content():
    errs = []
    counts = dict(goals=(GOALS, 4), vocab=(VOCAB, 5), reqs=(REQS, 7), steps=(STEPS, 7), tips=(TIPS, 4), check=(CHECK, 6),
                  rubric=(RUBRIC, 5), struggles=(STRUGGLES, 4), resources=(RESOURCES, 4), slides=(SLIDES, 14), plan=(PLAN, 26),
                  logic=(LOGIC_REF, 9), elements=(ELEMENTS, 8))
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
    for w in ("new year", "winter", "holiday", "christmas", "hanukkah", "chanukah", "sleigh", "carol", "snow", "eve ", "auld", "syne"):
        if w in LISTING_TITLE.lower():
            errs.append(f"the listing title must not hold the seasonal word {w}")
    if len(STEP_NAMES) != len(STEPS) or any(not s.startswith(f"<b>{nm}</b>") for s, nm in zip(STEPS, STEP_NAMES)):
        errs.append("STEPS must start with the bold names in STEP_NAMES (the pages cite them)")
    # ---- the melody chart: bar sums, two keys, two sources
    if len(CHART_C) != 17 or len(CHART_G) != 17:
        errs.append("the chart is a pickup bar plus 16 bars in each key")
    for key, chart in CHARTS.items():
        for i, bar in enumerate(chart):
            if sum(d for _, d in bar) != 16:
                errs.append(f"{key} major chart bar {i} adds up to {sum(d for _, d in bar)} sixteenths, not 16")
        if chart[0] != [("R", 12), chart[0][1]] or chart[0][1][1] != 4 or chart[16][-1] != ("R", 4) or chart[16][0][1] != 12 or len(chart[16]) != 2:
            errs.append(f"{key} major: the pickup bar is three beats of rest and one note; the last bar is a dotted half note and a beat of rest")
        if chart[0][1][1] + chart[16][0][1] != 16:
            errs.append(f"{key} major: the pickup note and the last bar's note must add up to one bar")
    if CHART_G != moved(CHART_C, SHIFT_G):
        errs.append("transposition check: the G major chart must be the C major chart moved up 7 semitones, note for note and length for length")
    for a, b in zip(chart_bars(CHART_C), chart_bars(CHART_G)):
        if midi(b[0]) - midi(a[0]) != 7 or a[1:] != b[1:]:
            errs.append(f"transposition check: {a} and {b} are not 7 semitones apart with the same start and length")
    if len(chart_bars(CHART_C)) != len(chart_bars(CHART_G)) or note_count() != 56:
        errs.append(f"the chart has 56 notes in each key (found {note_count()})")
    # source 1: the LilyPond transcription in F major, moved down 5 semitones, equals the chart note for note and length for length
    src1 = parse_ly(SRC_A_LY)
    mine = [(p, d) for p, s, d in chart_bars(moved(CHART_C, SHIFT_F))]
    if src1 != mine:
        for k, (a, b) in enumerate(zip(src1, mine)):
            if a != b:
                errs.append(f"source 1 (LilyPond, F major) differs from the chart (moved to F) at note {k + 1}: {a} versus {b}")
                break
        else:
            errs.append(f"source 1 has {len(src1)} notes, the chart {len(mine)}")
    # the lengths in source 1 also fill the bars: pickup 4, then 16 bars of 16 sixteenths, the last note 12
    if sum(d for _, d in src1) != 4 + 16 * 16 - 4:
        errs.append("source 1: pickup plus 16 bars with a last bar of a dotted half note: 4 + 252 sixteenths")
    # source 2: the pitch sounding at the start of every beat in the other edition
    bp = beat_pitches(moved(CHART_C, SHIFT_F))
    if bp[0] != ["R", "R", "R", SRC_B_BEATS["pickup"]]:
        errs.append(f"source 2: the pickup note {SRC_B_BEATS['pickup']} on beat 4 of the pickup bar")
    for i in range(1, 17):
        if " ".join(bp[i]) != SRC_B_BEATS[i]:
            errs.append(f"source 2 (second score) differs from the chart at bar {i}: beats {SRC_B_BEATS[i]} versus {' '.join(bp[i])} (chart moved to F)")
    pcs = {pc_of(p) for p, _, _ in chart_bars(CHART_C)}
    if pcs != {0, 2, 4, 7, 9}:
        errs.append("the tune is pentatonic: C D E G A only")
    lo, hi = ROLL_RANGE["C"]
    if not (midi("G3") == min(midi(p) for p, _, _ in chart_bars(CHART_C)) and midi("A4") == max(midi(p) for p, _, _ in chart_bars(CHART_C)) and lo == midi("G3") and hi == midi("A4")):
        errs.append("C major range G3 to A4 (15 piano roll rows)")
    lo, hi = ROLL_RANGE["G"]
    if not (midi("D4") == min(midi(p) for p, _, _ in chart_bars(CHART_G)) and midi("E5") == max(midi(p) for p, _, _ in chart_bars(CHART_G)) and lo == midi("D4") and hi == midi("E5")):
        errs.append("G major range D4 to E5")
    if [downbeat(CHART_C, i) for i in range(1, 17)] != EXPECT_DOWNBEATS_C:
        errs.append("the 16 downbeat notes in C major: C D C A G D C C G D G A G D C C")
    if [downbeat(CHART_G, i) for i in range(1, 17)] != [pname(midi(p) + 7) for p in EXPECT_DOWNBEATS_C]:
        errs.append("the 16 downbeat notes in G major are the C major ones moved up 7 semitones")
    if tuple(len(s.split()) for s in SRC_B_BEATS.values())[1:] != (4,) * 16:
        errs.append("source 2 lists four beats for each of the 16 bars")
    # ---- the chords: every downbeat is a chord tone in both keys; names, numerals and tones recomputed
    for st in STYLES:
        if len(CHORDS_C[st]) != 16:
            errs.append(f"{st}: one chord for each of the 16 bars")
        for i, ch in enumerate(CHORDS_C[st], start=1):
            for key in ("C", "G"):
                db = pc_of(downbeat(CHARTS[key], i))
                if db not in chord_pcs(ch, key):
                    errs.append(f"{st} bar {i} in {KEY_NAMES[key]}: the downbeat note {downbeat(CHARTS[key], i)} is not in {chord_name(ch, key)}")
                errs += diatonic_errors(ch, key)
                # a passing note is a melody note that is not in the chord; it never sits on beat 1
                for p, s, d in chart_bars(CHARTS[key]):
                    if s // 16 == i and s % 16 == 0 and pc_of(p) not in chord_pcs(ch, key):
                        errs.append(f"{st} bar {i}: a non-chord note on beat 1")
    allch = sorted({c for st in STYLES for c in CHORDS_C[st]})
    for ch in allch:
        if ch not in EXPECT_ROMAN or roman(ch, "C") != EXPECT_ROMAN[ch] or roman(ch, "G") != EXPECT_ROMAN[ch]:
            errs.append(f"Roman numeral of {ch}: {roman(ch, 'C')} / {roman(ch, 'G')}, expected {EXPECT_ROMAN.get(ch)} in both keys")
        if chord_name(ch, "C") != ch or chord_name(ch, "G") != EXPECT_NAME_G[ch]:
            errs.append(f"letter names of {ch}: C {chord_name(ch, 'C')}, G {chord_name(ch, 'G')}; expected {ch} and {EXPECT_NAME_G[ch]}")
        if " ".join(chord_letters(ch, "C")) != EXPECT_TONES_C[ch] or " ".join(chord_letters(ch, "G")) != EXPECT_TONES_G[ch]:
            errs.append(f"chord tones of {ch}: {' '.join(chord_letters(ch, 'C'))} / {' '.join(chord_letters(ch, 'G'))}")
    if len(allch) != 13:
        errs.append(f"the chord key lists 13 different chords (found {len(allch)})")
    if CHORDS_C["pop"][:4] != ["C", "G", "Am", "F"] or [roman(c, "C") for c in CHORDS_C["pop"][:4]] != ["I", "V", "vi", "IV"]:
        errs.append("pop begins with the I-V-vi-IV loop: C G Am F")
    if [roman(c, "C") for c in CHORDS_C["edm"][:4]] != ["vi", "V", "I", "IV"]:
        errs.append("EDM begins with the vi-V-I-IV loop")
    if not any("sus4" in c for c in CHORDS_C["ballad"]) or sum(1 for c in CHORDS_C["ballad"] if "7" in c) < 8 or any(c in ("C", "G", "F") for c in CHORDS_C["ballad"]):
        errs.append("the ballad uses added 7ths and suspended chords, not plain triads")
    if [role_of(pc_of(downbeat(CHART_C, i)), CHORDS_C["ballad"][i - 1], "C") for i in (1, 2, 3, 4)] != ["root", "fifth", "third", "third"]:
        errs.append("ballad roles of the downbeat notes in bars 1 to 4: root, fifth, third, third")
    if passing("pop", 2, "C") != ["C", "E"] or passing("ballad", 2, "G") != ["B"] or passing("pop", 1, "C") != []:
        errs.append("passing notes: bar 2 of pop in C is C and E; bar 2 of the ballad in G is B; bar 1 of pop has none")
    # ---- the grooves
    for st in STYLES:
        g = GROOVES[st]
        if any(len(g[ln]) != 16 for ln in GROOVE_LANES):
            errs.append(f"groove {st}: every lane has 16 steps")
        if (len(hits(st, "Kick")), len(hits(st, "Snare")), len(hits(st, "Hat"))) != GROOVE_FACTS[st]:
            errs.append(f"groove {st}: kick, snare and hat hits per bar should be {GROOVE_FACTS[st]}")
    if hits("edm", "Kick") != [0, 4, 8, 12] or hits("edm", "Hat") != [2, 6, 10, 14] or hits("edm", "Snare") != [4, 12]:
        errs.append("EDM groove: four on the floor (kick on every beat), clap on beats 2 and 4, hat on the off-beats")
    if hits("pop", "Snare") != [4, 12] or hits("ballad", "Snare") != [8] or hits("ballad", "Kick") != [0, 8]:
        errs.append("pop snare on 2 and 4; ballad snare on beat 3 only and kick on 1 and 3")
    # ---- the time: seconds per beat, per bar, the 40-bar track
    if [spb(b) for b in (120, 72, 100, 128)] != [Fraction(1, 2), Fraction(5, 6), Fraction(3, 5), Fraction(15, 32)]:
        errs.append("seconds per beat = 60 / BPM")
    if [bar_len(b) for b in (72, 100, 128, 120)] != [Fraction(10, 3), Fraction(12, 5), Fraction(15, 8), 2] or any(bar_len(b) != 4 * spb(b) for b in TEMPOS):
        errs.append("seconds per bar = 240 / BPM, four beats")
    if sum(SEC_BARS) != 40 or SEC_BARS != [4, 16, 16, 4] or [start_bar(i) for i in range(4)] != [1, 5, 21, 37] or [end_bar(i) for i in range(4)] != [4, 20, 36, 40]:
        errs.append("sections: 4 + 16 + 16 + 4 = 40 bars starting at bars 1, 5, 21 and 37")
    for b in TEMPOS:
        for i in range(5):
            if abs(float(sum(SEC_BARS[:i]) * bar_len(b)) - sum(SEC_BARS[:i]) * 240 / b) > 1e-9:
                errs.append(f"section {i} start at {b} BPM: float check fails")
        if total_s(b) != Fraction(40 * 240, b) or pass_s(b) != 16 * bar_len(b):
            errs.append(f"track and pass seconds at {b} BPM")
    if [dec(spb(b), 3) for b in TEMPOS] != ["0.909", "0.833", "0.750", "0.600", "0.545", "0.500", "0.484", "0.469"] or \
       [dec(bar_len(b), 3) for b in TEMPOS] != ["3.636", "3.333", "3.000", "2.400", "2.182", "2.000", "1.935", "1.875"]:
        errs.append("seconds per beat and per bar to 3 decimals at 66, 72, 80, 100, 110, 120, 124, 128 BPM")
    if [dec(pass_s(b), 2) for b in TEMPOS] != ["58.18", "53.33", "48.00", "38.40", "34.91", "32.00", "30.97", "30.00"] or \
       [dec(total_s(b), 2) for b in TEMPOS] != ["145.45", "133.33", "120.00", "96.00", "87.27", "80.00", "77.42", "75.00"]:
        errs.append("one pass and the 40-bar track in seconds at the table's tempos")
    if [[dec(start_s(b, i), 2) for i in (1, 2, 3, 4)] for b in (72, 100, 128)] != [["13.33", "66.67", "120.00", "133.33"], ["9.60", "48.00", "86.40", "96.00"], ["7.50", "37.50", "67.50", "75.00"]]:
        errs.append("section starts at 72, 100 and 128 BPM")
    if rnd(Fraction(5, 2), 0) != 3 or dec(Fraction(40, 3), 2) != "13.33" or dec(Fraction(20, 3), 2) != "6.67" or mmss(total_s(72)) != "2:13":
        errs.append("round half up; 133.33 seconds is 2:13")
    # ---- the map: which elements play where
    if len(ELEMENTS) != 8 or any(len(c) != 4 for _, c in ELEMENTS) or ELEM_PLAYING != [2, 6, 7, 3] or sum(ELEM_PLAYING) != 18:
        errs.append("the map: 8 elements x 4 sections; 2, 6, 7 and 3 playing (18 in all)")
    if ELEM_PLAYING[2] != max(ELEM_PLAYING):
        errs.append("the second pass has the most elements")
    cells = dict(ELEMENTS)
    if [bool(c) for c in cells["Melody"]] != [True, True, True, False] or "bar 4" not in cells["Melody"][0]:
        errs.append("the melody plays in the intro (the pickup in bar 4) and both passes, not the outro")
    if [bool(c) for c in cells["Counter-line or arp"]] != [False, False, True, False]:
        errs.append("the counter-line plays only in the second pass")
    # ---- Logic wording: newer tools are hedged
    for nm, txt in LOGIC_REF:
        for w in ("Step Sequencer", "Chord Track", "Session Players", "Smart Tempo", "Keyboard Player", "side chain menu", "Create Marker"):
            if w in txt and "if your version" not in txt.lower():
                errs.append(f"Logic reference '{nm}' must hedge {w} with 'if your version'")
    for w in ("Alchemy", "Drum Machine Designer", "Compressor", "Piano Roll", "Chord Track", "Session Players", "Smart Tempo", "Marker", "Step Sequencer", "Retro Synth"):
        if w not in " ".join(t for _, t in LOGIC_REF):
            errs.append(f"the Logic quick reference must name {w}")
    # ---- the worked example
    if EX_BPM != 72 or EX_KEY != "G" or EX_STYLE != "ballad" or dec(EX_BAR_S, 3) != "3.333" or dec(total_s(EX_BPM), 2) != "133.33" or dec(pass_s(EX_BPM), 2) != "53.33":
        errs.append("the example: ballad in G major at 72 BPM, 3.333 s per bar, 133.33 s, one pass 53.33 s")
    for need in ("72 BPM", "240 ÷ 72 = 3.333 seconds", "53.33 seconds", "133.33 seconds", "bars 1 to 4", "bars 5 to 20", "bars 21 to 36", "bars 37 to 40", "beat 4 of bar 4",
                 "the A in bar 2 is the fifth of Dsus4", "the E in bar 4 is the third of Cmaj7", "Imaj7, Vsus4, vi7 and IVmaj7"):
        if need not in EX_STRONG:
            errs.append(f"the clear plan must say '{need}'")
    if downbeat(CHART_G, 2) != "A4" or role_of(pc_of("A4"), CHORDS_C["ballad"][1], "G") != "fifth" or chord_name(CHORDS_C["ballad"][1], "G") != "Dsus4":
        errs.append("example: the downbeat of bar 2 in G is A, the fifth of Dsus4")
    if downbeat(CHART_G, 4) != "E5" or role_of(pc_of("E5"), CHORDS_C["ballad"][3], "G") != "third":
        errs.append("example: the downbeat of bar 4 in G is E, the third of Cmaj7")
    # ---- no forbidden themes in any text a buyer reads; the poem's words are not printed
    allt = " ".join([THEME, SOURCE_NOTE, OVERVIEW, " ".join(GOALS), " ".join(f"{a} {b}" for a, b in VOCAB), " ".join(REQS), " ".join(STEPS), " ".join(TIPS), " ".join(CHECK),
                     " ".join(d for _, ds in RUBRIC for d in ds), TN_REINFORCES, " ".join(STRUGGLES), VAR_EASY, VAR_HARD, " ".join(f"{a} {b}" for a, b in RESOURCES), TN_NOTE,
                     " ".join(GRADING), " ".join(d["do"] for d in PACING), SONG_NOTE, " ".join(CREDITS), " ".join(t for _, t in LOGIC_REF), EX_STRONG, EX_MIX, " ".join(EX_QUESTIONS),
                     " ".join(EX_SEC_NOTES), " ".join(" ".join((s[2], s[3], s[4])) for s in SLIDES), " ".join(" ".join(c) for _, c in ELEMENTS),
                     " ".join(" ".join(v) for v in GROOVE_TEXT.values()), " ".join(STYLE_FEEL.values())]).lower()
    for w in FORBIDDEN_WORDS:
        if re.search(rf"\b{re.escape(w.strip())}\b", allt):
            errs.append(f"no alcohol, religious or seasonal-holiday wording in a neutral kit: '{w.strip()}'")
    for w in LYRIC_FRAGMENTS:
        if w in allt:
            errs.append(f"the poem's words are not printed: '{w}'")
    if "old long since" not in allt or "1788" not in allt or "1799" not in allt or "public domain" not in allt:
        errs.append("the theme and source note must give the title's translation (old long since), 1788, 1799 and public domain")
    for w in ("colour", "favour", "centre", "licence", "grey", "metre ", "organis", "recognis", "practise", "analyse", "whilst", "milli-second", "harmonis", "rhythmn"):
        if w in allt.replace("gray", ""):
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
    for need, key in ((f"pages {pg('chart1')} and {pg('chart2')}", 4), (f"pages {pg('chords1')} and {pg('chords2')}", 5), (f"pages {pg('chords1')} and {pg('chords2')}", 6),
                      (f"page {pg('grooves')}", 7), (f"page {pg('logicref')}", 8), (f"page {pg('map')}", 9), (f"page {pg('tempo')}", 9)):
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
    for need in ("No audio, recordings or lyrics", "invented plan on paper", "Drum Machine Designer", "Alchemy", "Compressor", "Piano Roll", "Chord Track", "Session Players", "Smart Tempo",
                 "Marker", "60 ÷ BPM", "240 ÷ BPM", "Roman numeral", "chord tone", "if your version", "sidechain", "four on the floor", "public domain", "old long since",
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
    for w in LYRIC_FRAGMENTS:
        if w in (txt + " " + alldeck).lower():
            errs.append(f"the poem's words are not printed: '{w}'")
    for w in ("colour", "favour", "centre", "licence", "grey", "metre", "organis", "recognis", "practise", "analyse", "whilst", "milli-second", "colourful", "harmonis"):
        if w in txt.lower().replace("greyscale", ""):
            errs.append(f"US spelling: '{w}' in the PDF")
    # ---- Step N on every page, in the deck PDF text, the deck notes and UPLOAD.md agrees with the project sheet
    expect = {"tempo": {1}, "chart1": {2}, "chart2": {2}, "chords1": {3}, "chords2": {3}, "grooves": {4}, "map": {5}, "mix": {6}}
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
                                          capture_output=True, text=True, check=True).stdout).replace("- ", "-")
    # ---- the tempo page prints every number
    rc = raw("tempo")
    hint = {66: "Ballad", 72: "Ballad", 80: "Ballad or slow pop", 100: "Pop", 110: "Pop", 120: "Pop or EDM", 124: "EDM", 128: "EDM"}
    for bpm in TEMPOS:
        row = f"{bpm} {dec(spb(bpm), 3)} {dec(bar_len(bpm), 3)} {dec(pass_s(bpm), 2)} {dec(total_s(bpm), 2)} {hint[bpm]}"
        if row not in rc:
            errs.append(f"tempo page: row '{row}' is not printed")
    for st in ("ballad", "pop", "edm"):
        bpm = STYLE_BPM[st]
        row = f"{bpm} {STYLE_NAMES[st]} " + " ".join(dec(start_s(bpm, i), 2) for i in (1, 2, 3, 4))
        if row not in rc:
            errs.append(f"tempo page: section row '{row}' is not printed")
    for need in ("Seconds per beat = 60 ÷ BPM", "Seconds per bar = 240 ÷ BPM", "40 × 240 ÷ BPM", "240 ÷ 100 = 2.4 s per bar", "40 bars = 96 s", "Step 1: choose style and tempo",
                 "5 rounds up", "13.33", "240 ÷ 72 = 3.333"):
        if need not in rc:
            errs.append(f"tempo page must say '{need}'")
    # ---- the chart pages print every note in both keys
    rn = raw("chart1") + " " + raw("chart2")
    for i in range(0, 17):
        for key in ("C", "G"):
            t = bar_text(CHARTS[key][i])
            if t not in rn:
                errs.append(f"chart page: bar {i} in {KEY_NAMES[key]} '{t}' is not printed")
    for need in ("Step 2: enter the melody", "pickup bar", "subtract one", "pentatonic", "public-domain", "Brigid Baker", "F major"):
        if need not in rn:
            errs.append(f"chart pages must say '{need}'")
    # ---- the chord pages print every row
    rch = raw("chords1") + " " + raw("chords2")
    for st in STYLES:
        for i in range(1, 17):
            ch = CHORDS_C[st][i - 1]
            dbc, dbg = downbeat(CHART_C, i)[:-1], downbeat(CHART_G, i)[:-1]
            row = (f"{i} {dbc} · {dbg} {chord_name(ch, 'C')} · {chord_name(ch, 'G')} {roman(ch, 'C')} {' '.join(chord_letters(ch, 'C'))} · {' '.join(chord_letters(ch, 'G'))} "
                   f"{role_of(pc_of(downbeat(CHART_C, i)), ch, 'C')} {' '.join(passing(st, i, 'C')) or 'none'} · {' '.join(passing(st, i, 'G')) or 'none'}")
            if row not in rch:
                errs.append(f"chord pages: {st} row '{row}' is not printed")
    for need in ("Step 3: choose chords", "Every beat 1 note is a chord tone", "Chord key · 13 chords", "How to check a chord"):
        if need.lower() not in rch.lower():
            errs.append(f"chord pages must say '{need}'")
    # ---- the arrangement map page and the groove page
    rm = raw("map")
    for need in ("Step 5: arrange the sections", "2, 6, 7, 3", "add up to 18", "40 bars"):
        if need not in rm:
            errs.append(f"arrangement map page must say '{need}'")
    for i, nm in enumerate(SEC_NAMES):
        row = f"{nm} {SEC_BARS[i]} {start_bar(i)}–{end_bar(i)} " + " ".join(dec(start_s(b, i), 2) for b in STYLE_BPM.values())
        if row not in rm:
            errs.append(f"arrangement map page: row '{row}' is not printed")
    rg = raw("grooves")
    for need in ("Step 4: build the groove", "four on the floor", "Four on the floor", "side chain", "Pop groove", "Ballad groove", "EDM groove"):
        if need.lower() not in rg.lower():
            errs.append(f"groove page must say '{need}'")
    # ---- the worked example prints its numbers
    re1 = (raw("example") + " " + raw("example2"))
    for i in range(1, 17):
        ch = CHORDS_C[EX_STYLE][i - 1]
        db = downbeat(CHARTS[EX_KEY], i)
        row = f"{i} {db[:-1]} {chord_name(ch, EX_KEY)} {roman(ch, EX_KEY)} {' '.join(chord_letters(ch, EX_KEY))} {role_of(pc_of(db), ch, EX_KEY)}"
        if row not in re1:
            errs.append(f"worked example: chord row '{row}' is not printed")
    for i, nm in enumerate(SEC_NAMES):
        row = f"{nm} {start_bar(i)}–{end_bar(i)} {SEC_BARS[i]} {dec(start_s(EX_BPM, i), 2)} {dec(start_s(EX_BPM, i + 1), 2)} {EX_SEC_NOTES[i]}"
        if row not in re1:
            errs.append(f"worked example: section row '{row}' is not printed")
    for need in ("60 ÷ 72 = 0.833 s", "240 ÷ 72 = 3.333 s", "4 + 16 + 16 + 4 = 40 bars", "40 × 3.333 = 133.33 seconds (2:13)", "All 16 beat 1 notes are chord tones", "66.67 seconds"):
        if need not in re1:
            errs.append(f"worked example must say '{need}'")
    up = open(os.path.join(HERE, "UPLOAD.md"), encoding="utf8").read()
    errs += step_ref_errors(up, "UPLOAD.md")
    if "Grades 9-12" not in up or "`9th-grade`, `10th-grade`, `11th-grade`, `12th-grade`" not in up:
        errs.append("UPLOAD.md: grades 9-12 in the description and section 3")
    if "no audio" not in up.lower() or "Open question" not in up or "Timing numbers" not in up or "Sources and credits" not in up or "Melody sources" not in up:
        errs.append("UPLOAD.md: must say no audio is included, record the timing numbers checked, the melody sources, the credits and the open questions")
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
    for w in LYRIC_FRAGMENTS:
        if w in up.lower():
            errs.append(f"UPLOAD.md prints the poem's words: '{w}'")
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
    return ("the melody chart: every bar adds up to 16 sixteenths in both keys (pickup bar and last bar together make one bar); the G major chart equals the C major chart moved up 7 semitones "
            "note by note; the chart equals a LilyPond transcription in F major (source 1) note by note and length by length, and agrees with a second public-domain edition (source 2) on the pitch "
            "at every beat of all 16 bars; five pitches only (pentatonic); the three chord tables (16 bars each, in C and in G): the melody note on every downbeat is a chord tone, every chord is "
            "recomputed by stacking thirds on the key's scale, and Roman numerals, letter names and chord tones match an independent list in both keys; passing notes computed; groove cards "
            "(kick, snare and hat hits; EDM four on the floor); seconds per beat = 60 / BPM and per bar = 240 / BPM at eight tempos, the 40-bar track and section starts at 72, 100 and 128 BPM "
            "(exact fractions and a float method); the arrangement map (8 elements x 4 sections, 2, 6, 7, 3 playing); every 'Step N' agrees with the project sheet on pages, slides, notes and "
            "UPLOAD.md; class badges agree with the pacing page; every drawing renders alone on a transparent ground with no ink at its edges; hero art inside its viewBox; rendered-DOM footer gap "
            "on every page; no truncated slide bullets; edges of cover.png and previews clear; no audio, lyrics, alcohol, religious or brand wording or student work; grades 9-12; "
            "tags and subjects are not headings; no 'what changed' page (ORIGINAL).")
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



# ================================================================ UPLOAD.md (written by gen.py so every number matches the build)
def write_upload():
    np_, ns = len(PLAN), len(SLIDES)
    n_teacher = (PLAN.index("example2") + 1) - 1
    n_student = (PLAN.index("reflect") + 1) - (PLAN.index("tempo") + 1) + 1
    assert 2 + n_teacher + n_student == np_, "page-count list must total the PDF"
    nt = len(LISTING_TITLE)
    desc = (f"{DESC_START} students re-harmonize a public-domain melody in Logic Pro. They enter the traditional Scottish tune of “Auld Lang Syne” from a note chart (16 bars in 4/4 with a pickup, "
            f"in C major or G major), then put new chords under it in a pop, ballad or EDM style: a pop loop (I–V–vi–IV), a slower ballad with added 7ths and suspended chords, or an EDM track with four on the floor "
            f"and a sidechain pump. Every chord must hold the melody note on its downbeat, and students name each chord by Roman numeral and letter. The tune is a song of remembrance and friendship, so the "
            f"theme is secular and fits any class. This Auld Lang Syne Reharmonized project takes {CLASSES} class periods (the pacing guide also shows two and four) and is an original Hudson Beat project; "
            f"the steps are written for Logic Pro, while the ideas (chord tones, Roman numerals, grooves, arrangement) carry over to GarageBand.\n\n"
            f"WHAT'S INCLUDED (ZIP: {np_}-page PDF = 1 cover + {n_teacher} teacher + {n_student} student + 1 terms page, plus {ns}-slide intro deck as .pptx and PDF)\n"
            f"• Teacher pages: how to use, project overview, setup, a {CLASSES}-class pacing guide with the deck slides for each class, "
            f"two pages of teacher notes (struggles, variations, resources, grading), a Logic quick reference and a two-page worked example (an invented ballad in G major at 72 BPM: "
            f"40 bars = 133.33 seconds, every chord with its numeral and the check that each downbeat is a chord tone, the section times and the mix) ({n_teacher} pages)\n"
            f"• Student pages: a tempo table (seconds per beat and per bar, one pass and the 40-bar track at eight tempos, and the start of every section at 72, 100 and 128 BPM), a two-page note chart of the melody "
            f"in C major and G major (piano roll and bar-by-bar table), pop, ballad and EDM chord tables for all 16 bars in both keys with Roman numerals, chord tones and passing notes, a chord key of 13 chords, "
            f"groove cards for the three styles with the sidechain explained, an arrangement map of eight elements by four sections, a mix checklist, the 3-page project sheet "
            f"(overview, goals, vocabulary, requirements, steps, tips, submission checklist), the /{RUBRIC_TOTAL} rubric, a vocabulary page, a feedback planner and a reflection page ({n_student} pages)\n"
            f"• Teacher-presented intro deck, {ns} slides with speaker notes on every slide: a think-and-share hook, what the project is, the melody in a piano roll, how a chord fits a melody note, "
            f"three styles, four on the floor and the sidechain pump, building it in Logic, the arrangement map, what to turn in and the rubric\n\n"
            f"THE THREE CLASS PERIODS\n"
            f"• Class 1: hook; the tempo table, the melody and the chord tables; enter the first eight bars\n"
            f"• Class 2: finish the melody, enter and check the chords, build the groove\n"
            f"• Class 3: arrange the four sections, mix, bounce, present and reflect\n\n"
            f"WHAT STUDENTS LEARN\n"
            f"• Harmony: a chord fits a melody when it holds the downbeat note (a chord tone); Roman numerals and letter names in two keys; what pop, ballad and EDM chords have in common and where they differ\n"
            f"• Timing math: seconds per bar in 4/4 = 240 ÷ BPM; a 40-bar track at 72 BPM lasts 133.33 seconds, at 100 BPM 96 seconds and at 128 BPM 75 seconds\n"
            f"• Building in Logic Pro: the Piano Roll, Alchemy or Retro Synth, Drum Machine Designer, a Compressor side chain, markers, automation and bounce; the Chord Track, Session Players, the Step Sequencer and Smart Tempo if your version has them\n"
            f"• Mixing so the melody stays clear and the second pass is bigger, and explaining their choices in a reflection\n\n"
            f"GOOD TO KNOW\n"
            f"• There is no audio in this resource and no student work. The melody is public domain and appears only as a note chart; the poem’s words are not printed. Students make every sound themselves in Logic Pro\n"
            f"• Requires Logic Pro on a Mac. A MIDI keyboard is optional; students need only read the note chart. Where a control may differ between versions, the pages say \"if your version has it\"\n"
            f"• Rubric: 5 categories scored 1-5, /{RUBRIC_TOTAL}; the final grade is the average of the student's and the teacher's score\n"
            f"• Grades 9-12; music technology or music production classes\n"
            f"• The deck uses the free Oswald and Source Sans 3 fonts (built into Google Slides); install them for PowerPoint or Keynote, or present "
            f"the PDF copy, which shows the intended look\n"
            f"• Every student page prints well in black and white\n\n"
            f"Logic Pro is a product of Apple Inc., named only to describe compatibility. This resource is not affiliated with Apple.\n\n"
            f"{D.DISCLOSURE_NEW}")
    tbl = "; ".join(f"{b} BPM ({STYLE_NAMES[s]}): {dec(bar_len(b), 3)} s per bar, one pass {dec(pass_s(b), 2)} s, 40 bars {dec(total_s(b), 2)} s, Pass 2 starts at {dec(start_s(b, 2), 2)} s"
                    for s, b in STYLE_BPM.items())
    allch = sorted({c for st in STYLES for c in CHORDS_C[st]})
    rom = ", ".join(f"{c} = {roman(c, 'C')} ({chord_name(c, 'G')} in G)" for c in allch)
    md = f"""# UPLOAD: Auld Lang Syne Reharmonized, original Logic Pro project (TpT 070)

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
({nt} characters; the limit is 80.) The title leaves out New Year, Winter, Holiday and the song's name because TpT's Seasonal Titles notice blocked a holiday-named title on 027 (see 032, 033 and 034); "Reharmonize a Melody" is the plain search phrase. "Logic Pro" sits in the first 30 characters.

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

**${PRICE}** (paid), multiple-license price ${PRICE}. Inside the $7-9 holiday-kit range, for a kit with {np_} pages + {ns} slides, a note chart in two keys, three chord tables, groove cards, an arrangement map, a tempo table and a two-page worked example, listed in late December.

## 8. Free or paid / free preview pages

Paid. Preview PDF (4 watermarked pages): the {CLASSES}-class pacing guide, the first note chart page, the pop and ballad chord tables and the /{RUBRIC_TOTAL} rubric. "Number of pages or slides" is {np_ + ns} ({np_} pages + {ns} slides).

## 9. Sources and credits

- **Melody sources (public domain).** The tune is a traditional Scottish melody; Robert Burns wrote the poem in 1788 and the standard tune's first documented use with the words is from 1799 (George Thomson's *Select Songs of Scotland*), both far before the 1930 cutoff, so the melody is in the public domain worldwide. The chart (16 bars in 4/4 plus a one-beat pickup, 56 notes, five pitches) was typed in C major and in G major and checked in `gen.py --check` against two sources fetched on 22 Nov 2026: (1) the LilyPond transcription in F major engraved on the English Wikipedia article "Auld Lang Syne" (note for note and length for length, after moving it down 5 semitones; the melody only, no words are used); (2) Brigid Baker's public-domain edition on the Choral Public Domain Library (CPDL no. 21485, MusicXML), compared on the pitch at the start of every beat of all 16 bars (the same on all 64 beats; it splits two beat-4 quarter notes into two eighths). The G major chart is the C major chart moved up 7 semitones, checked note by note. Also read and compared, but not used as the chart: Philip Rice's CPDL edition (no. 37897, public domain), which differs in one place (the last pickup note of the third phrase, tune bar 12, is F5 in F major instead of D5), and two 19th-century arrangements, Felix Horetzky's for guitar (Mutopia Project, public domain) and Beethoven's WoO 156 (CPDL, from the 1814 *Scottish Folksongs*). Published editions vary some pickup notes and rhythms (Horetzky's guitar setting is in 2/4 and in D major, for example), which the plain 4/4 chart does not follow. This is stated on the chart page.
- **Poem and facts.** The poem's words are not printed. The kit gives only the facts: written by Robert Burns in 1788 (from older Scottish song), the title is Scots for "old long since" (often "days gone by"), the chorus line is often rendered "for the sake of old times", and the tune is traditional and pentatonic (English Wikipedia and Britannica agree; the Library of Congress blog on the song says the tune derives from a traditional Scottish folk-dance tune).
- **Art:** the cover, previews and deck use the owner's pre-made art (`art/hero.png`: a laptop with a waveform, headphones, a small keyboard controller and sparkles), copied whole from `tpt/_art/next/auld-lang-syne-reharmonized/`; the file is logged in `tpt/_art/USAGE.md`. Everything else, including every note, chord and number, is drawn or printed in code.
- **Music:** only the public-domain melody is notated. No songs, artists, recordings or other arrangements are named or included. Students make every sound.
- **Fonts:** Oswald and Source Sans 3 (SIL OFL 1.1). Logic Pro is named only to describe compatibility.

## 10. Before you click publish

- [ ] **Needs QA approval first.** This is a new kit (not yet on TpT); the Manager releases it only after a QA `**Verdict: APPROVED**`. Season rule: build for late December; listing no sooner than the 2-8 week window allows.
- [ ] Cover and previews show "HUDSON BEAT" in type; PDF footers read "© 2026 Brian Lotze · Hudson Beat · For single-classroom use".
- [ ] No school name, logo, student names or work, audio, video, lyrics, song title other than the tune's own title, or Logic session anywhere (`gen.py --check` scans every output and every file in this folder).
- [ ] **Neutral and secular.** The theme is remembrance and friendship; no religious content, no alcohol imagery (the song's drinking lines are not quoted), no brands, no real recordings. `gen.py --check` fails on alcohol, religious and holiday-specific words and on fragments of the poem.
- [ ] **Timing numbers (all recomputed in `gen.py --check`, exactly with fractions and again with an independent float method).** Seconds per beat = 60 / BPM; seconds per bar in 4/4 = 240 / BPM. The track is 4 + 16 + 16 + 4 = 40 bars (sections start at bars 1, 5, 21, 37). Printed: {tbl}. Rounding: seconds per beat and per bar to 3 decimals, passes, starts and totals to 2, half up.
- [ ] **Chords (recomputed in `gen.py --check` from pitch classes, in C major and in G major).** Every one of the 48 downbeat notes (16 bars in three styles) is a chord tone in both keys; each chord is also rebuilt by stacking thirds on the key's scale. Roman numerals and letter names: {rom}.
- [ ] **Original project.** Built with `ORIGINAL = True` in `tpt/_dmp2_common/dmp2.py` (like 031, 036, 053, 057, 061, 063 and 067): no "what changed" page and the new disclosure line. The reflection page is the shared Reflection element, scored in the rubric's "Plan & Reflection" row. `dmp2.py` is unchanged.
- [ ] **Logic Pro names to confirm on a Mac with a current Logic.** Piano Roll (middle C is C3 in Logic and C4 on the chart), Alchemy and Retro Synth, Drum Machine Designer, Compressor with a Side Chain source menu (hedged), Chord Track, Session Players, Step Sequencer and Smart Tempo ("if your version has it"), the Marker global track with a plus (+) button and a Create Marker key command (hedged), automation (A), Mixer (X), Command-B bounce. No menu path beyond File › New and File › Bounce is given.
- [ ] **Open questions for the owner:** (1) **Title.** No New Year, Winter, Holiday or song name in the title because of TpT's seasonal-title notice (see 1). (2) **Price.** ${PRICE}, inside the $7-9 range. (3) **Classes.** Three periods; the pacing page shows how to run it in two or four. (4) **Melody variants.** Published settings differ in a few pickup notes (see 9); the chart follows the plain 4/4 version that two sources agree on. (5) **Release date.** Late December per the queue; the song is New Year's Eve music but the kit is secular and year-round.
"""
    with open(os.path.join(HERE, "UPLOAD.md"), "w", encoding="utf8") as f:
        f.write(md)


if __name__ == "__main__":
    if "--check" not in sys.argv:
        write_upload()
        D.deck_art = deck_art_transparent
    D.main(sys.modules[__name__])
