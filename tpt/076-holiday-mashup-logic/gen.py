#!/usr/bin/env python3
"""Logic Pro project kit: Holiday Mashup (TpT 076): the teacher resource, the intro deck and the listing files.

    python3 gen.py            build everything into this folder (also writes UPLOAD.md)
    python3 gen.py --lowres   same, but square images at scale 1 and small page shots (self-check only; --check rejects it)
    python3 gen.py --check    verify content and layout: both melody charts (Jingle Bells in G major, Deck the Halls in F major, 16 bars of 4/4 each; every bar adds up
                              to 16 sixteenths; each chart is compared note by note with the scores it was typed from: Jingle Bells with two CPDL editions (a 4/4 edition in G
                              major and a 2/4 edition in A-flat major) and Deck the Halls with three (two in F major and one in E-flat major); every difference between
                              editions is listed and must be the expected one), the moved charts (G -> F is 2 semitones down, F -> G is 2 up; pitch classes recomputed), the key
                              table (12 major keys: pitch class, circle-of-fifths step, key signature, relative minor, shortest shift between any two keys), the tempo math (ratios,
                              target tempos, percent change = (target / original - 1) x 100, seconds per beat and per bar for 2/4, 3/4 and 4/4, 44-bar section starts), the Smart Tempo
                              and Flex numbers (audio length change, semitones from speed), the layering check (beat-by-beat interval classes of the two melodies for every shift from
                              -6 to +5; the key-matched shift has the fewest hard clashes) and the suggested chords (computed), the arrangement map, Step N references on every
                              page, slide and UPLOAD.md, class badges against the pacing page (the "three classes" slide carries Classes 1-3), drawings (each rendered alone on a
                              transparent ground: no ink within 4 px of its edge), the hero art, files, page and slide counts, class slots, fonts, fit and overlap, dead space,
                              footer gap (pages and deck slides), truncated slide bullets, the edges of cover.png and the previews, banned strings, tpt.json and UPLOAD.md

An ORIGINAL Hudson Beat project (dmp2.ORIGINAL = True, like 053, 057, 061, 063, 067 and 070). Students make a DJ-style mashup of two public-domain winter carols, "Jingle Bells"
(James Lord Pierpont, published 1857) and "Deck the Halls" (a Welsh melody; the English words date from 1862), by matching their tempo and key. They work out the tempo ratio, a
target tempo and the percent speed change for each carol, find the shortest transposition between the two keys, enter both melodies from a note chart, check the match with Smart
Tempo and Flex (if their version has them), layer the two melodies over one groove and arrange 44 bars in six sections. No audio ships and no lyrics are printed. The art on the
cover, the previews and the deck is the library's mixing-console line art (art/hero.png), used whole. Everything else is drawn in code. The shared builder is
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
SLUG = "holiday-mashup"
TITLE = "Holiday Mashup"
ACCENT = "#2F7FB8"          # this product's single accent: icy blue (a shade deeper than the art's #4FA3D9, so small labels read)
ACC_LIGHT = "#DCEBF6"
PRICE = "9.00"
CLASSES = 3
GRADES_TEXT = "9–12"
GRADE_SLUGS = ["9th-grade", "10th-grade", "11th-grade", "12th-grade"]
TAGS = ["Winter", "Christmas-Chanukah-Kwanzaa", "Project-based Learning", "Projects", "Activities"]     # exact entries of tpt/TAG-OPTIONS.json, none a heading
SUBJECTS = ["Music", "Computer Science - Technology", "Music Composition"]     # all in SUBJECT-OPTIONS.json, none a heading
ANSWER_KEY = None
LISTING_TITLE = "Logic Pro Mashup Project | Match Tempo and Key, Smart Tempo, Flex | High School"
DESC_START = "Mashup project for high school music technology:"
DESC_MUST = ["Holiday Mashup", "public domain", "no audio", "seconds per bar", "240 ÷ BPM", "semitone", "Smart Tempo", "Flex Time", "Flex Pitch", "Jingle Bells", "Deck the Halls"]
ZIP_DIR = "Holiday Mashup - Hudson Beat"
ZIP_DATE = (2026, 11, 23, 12, 0, 0)
TYPE = "Original Project"
PROJ_LINE = "Music Technology | <i>Mashup Project</i> | 3 class periods"
DECK_STRAP = "Two carols, one tempo, one key"
REFLECT_ROW = "Plan &amp; Reflection"
# split so this file never contains them (the --check scan reads every file in this folder)
BANNED_EXTRA = ["Rud" + "olph", "Fro" + "sty", "Gri" + "nch", "Santa Claus " + "Is", "Jingle Bell " + "Rock", "Feliz " + "Navidad",
                "Mari" + "ah Carey", "Spoti" + "fy", "You" + "Tube", "Home " + "Alone", "Nin" + "tendo", "Ro" + "land",
                "Star " + "Wars", "Hans " + "Zimmer", "John " + "Williams", "Harry " + "Potter", "Pix" + "ar", "Lord of the " + "Rings",
                "Winter " + "Wonderland", "Let It " + "Snow", "Sleigh " + "Ride", "X" + "mas", "Times " + "Square",
                "Ser" + "ato", "Ser" + "ato DJ", "Tra" + "ktor", "Vir" + "tual DJ", "Ser" + "ato Pro", "Ableton " + "Live", "Mac" + "Rumors"]

# ================================================================ page plan (teacher pages 2-10, student pages 11-26)
PLAN = ["cover", "howto", "overview", "setup", "pacing", "tn1", "tn2", "logicref", "example", "example2",
        "tempo", "keys", "chart1", "chart2", "flex", "layer", "groove", "map", "mix", "proj1", "proj2", "proj3", "rubric", "vocab", "present", "reflect", "terms"]


def pg(k):
    return PLAN.index(k) + 1



# ================================================================ the two melodies: Jingle Bells (notated in G major) and Deck the Halls (notated in F major)
# Lengths are in sixteenth notes: 4 = quarter, 6 = dotted quarter, 3 = dotted eighth, 2 = eighth, 8 = half, 1 = sixteenth. One chart bar = one bar of 4/4 = 16 sixteenths.
LEN_NAMES = {1: "16th", 2: "eighth", 3: "dotted eighth", 4: "quarter", 6: "dotted quarter", 8: "half", 12: "dotted half", 16: "whole"}
LEN_ABBR = {1: "s", 2: "e", 3: "de", 4: "q", 6: "dq", 8: "h", 12: "dh", 16: "w"}
_PC = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
SHARP_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
FLAT_NAMES = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"]
FLAT_KEYS = {"F", "Bb", "Eb", "Ab", "Db"}      # keys whose notes are spelled with flats
BLACK_PC = {1, 3, 6, 8, 10}


def midi(p):
    acc = 0 if len(p) == 2 else (1 if p[1] == "#" else -1)
    return 12 * (int(p[-1]) + 1) + _PC[p[0]] + acc


def spell(m, key):
    """The name of MIDI note m as it is written in `key` (flats in F major, sharps in G major)."""
    return (FLAT_NAMES if key in FLAT_KEYS else SHARP_NAMES)[m % 12] + str(m // 12 - 1)


def pname(m):
    return SHARP_NAMES[m % 12] + str(m // 12 - 1)


def pcname(m, key):
    return spell(m, key)[:-1]


def bars_from(txt):
    """'D4/2 B4/2 ...' per bar -> [(pitch, length)]"""
    out = []
    for bar in txt:
        out.append([(a.split("/")[0], int(a.split("/")[1])) for a in bar.split()])
    return out


# The two charts as the students use them, typed from the first source; --check compares them with every source.
CHART_JB_G = bars_from([
    "D4/2 B4/2 A4/2 G4/2 D4/6 D4/1 D4/1", "D4/2 B4/2 A4/2 G4/2 E4/8", "E4/2 C5/2 B4/2 A4/2 F#4/8", "D5/2 D5/2 C5/2 A4/2 B4/8",
    "D4/2 B4/2 A4/2 G4/2 D4/6 D4/2", "D4/2 B4/2 A4/2 G4/2 E4/8", "E4/2 C5/2 B4/2 A4/2 D5/2 D5/2 D5/3 D5/1", "E5/2 D5/2 C5/2 A4/2 G4/8",
    "B4/2 B4/2 B4/4 B4/2 B4/2 B4/4", "B4/2 D5/2 G4/3 A4/1 B4/8", "C5/2 C5/2 C5/2 C5/2 C5/2 B4/2 B4/2 B4/1 B4/1", "B4/2 A4/2 A4/2 B4/2 A4/8",
    "B4/2 B4/2 B4/4 B4/2 B4/2 B4/4", "B4/2 D5/2 G4/3 A4/1 B4/8", "C5/2 C5/2 C5/2 C5/2 C5/2 B4/2 B4/2 B4/1 B4/1", "D5/2 D5/2 C5/2 A4/2 G4/8"])
CHART_DH_F = bars_from([
    "C5/6 Bb4/2 A4/4 G4/4", "F4/4 G4/4 A4/4 F4/4", "G4/2 A4/2 Bb4/2 G4/2 A4/6 G4/2", "F4/4 E4/4 F4/8",
    "C5/6 Bb4/2 A4/4 G4/4", "F4/4 G4/4 A4/4 F4/4", "G4/2 A4/2 Bb4/2 G4/2 A4/6 G4/2", "F4/4 E4/4 F4/8",
    "G4/6 A4/2 Bb4/4 G4/4", "A4/6 Bb4/2 C5/4 G4/4", "A4/2 B4/2 C5/4 D5/2 E5/2 F5/4", "E5/4 D5/4 C5/8",
    "C5/6 Bb4/2 A4/4 G4/4", "F4/4 G4/4 A4/4 F4/4", "D5/2 D5/2 D5/2 D5/2 C5/6 Bb4/2", "A4/4 G4/4 F4/8"])
NBARS = 16
KEY_JB, KEY_DH = "G", "F"          # the keys the charts are notated in
JB_ROWS = (midi("D4"), midi("E5"))
DH_ROWS = (midi("E4"), midi("F5"))


def moved(chart, semis, key):
    """The chart moved by `semis` semitones and spelled for `key` ('F' or 'G')."""
    return [[(spell(midi(p) + semis, key), d) for p, d in bar] for bar in chart]


def chart_notes(chart):
    """[(midi, start, length)] in sixteenths from the start of bar 1."""
    out, t = [], 0
    for bar in chart:
        for p, d in bar:
            out.append((midi(p), t, d))
            t += d
    return out


def bar_text(bar):
    return " · ".join(f"{p} {LEN_ABBR[d]}" for p, d in bar)


def bar_pcs(chart, i):
    return sorted({midi(p) % 12 for p, _ in chart[i]})


def sound(notes, t):
    """The MIDI note sounding at sixteenth t in [(midi, start, length)], or None."""
    for m, s, d in notes:
        if s <= t < s + d:
            return m
    return None


# ---- the scores the charts were typed from (fetched 23 Nov 2026; each note is pitch:start+length in sixteenths from the start of its bar)

# Source 1 for Jingle Bells: CPDL no. 38153 (John Brown, SAB, MusicXML), the soprano line, G major, 4/4. Bars are the file's own (1-8 chorus, 9-16 verse); each note is pitch:start+length in sixteenths from the start of its bar.
SRC_BROWN = {
    1: "B4:0+2 B4:2+2 B4:4+4 B4:8+2 B4:10+2 B4:12+4",
    2: "B4:0+2 D5:2+2 G4:4+3 A4:7+1 B4:8+8",
    3: "C5:0+2 C5:2+2 C5:4+2 C5:6+2 C5:8+2 B4:10+2 B4:12+2 B4:14+1 B4:15+1",
    4: "B4:0+2 A4:2+2 A4:4+2 B4:6+2 A4:8+4 D5:12+4",
    5: "B4:0+2 B4:2+2 B4:4+4 B4:8+2 B4:10+2 B4:12+4",
    6: "B4:0+2 D5:2+2 G4:4+3 A4:7+1 B4:8+8",
    7: "C5:0+2 C5:2+2 C5:4+2 C5:6+2 C5:8+2 B4:10+2 B4:12+2 B4:14+1 B4:15+1",
    8: "D5:0+2 D5:2+2 C5:4+2 A4:6+2 G4:8+8",
    9: "D4:0+2 B4:2+2 A4:4+2 G4:6+2 D4:8+6 D4:14+1 D4:15+1",
    10: "D4:0+2 B4:2+2 A4:4+2 G4:6+2 E4:8+8",
    11: "E4:0+2 C5:2+2 B4:4+2 A4:6+2 F#4:8+8",
    12: "D5:0+2 D5:2+2 C5:4+2 A4:6+2 B4:8+8",
    13: "D4:0+2 B4:2+2 A4:4+2 G4:6+2 D4:8+6 D4:14+2",
    14: "D4:0+2 B4:2+2 A4:4+2 G4:6+2 E4:8+8",
    15: "E4:0+2 C5:2+2 B4:4+2 A4:6+2 D5:8+2 D5:10+2 D5:12+3 D5:15+1",
    16: "E5:0+2 D5:2+2 C5:4+2 A4:6+2 G4:8+4 D5:12+4",
}
# Source 2 for Jingle Bells: CPDL no. 66808 (William Hale, adapted to the modern tune, MusicXML), the voice line (bars 9-24, the verse) and the soprano of the S.A. staff (bars 25-40, the chorus), A-flat major, 2/4 (a bar is 8 sixteenths).
SRC_HALE = {
    9: "Eb4:0+2 C5:2+2 Bb4:4+2 Ab4:6+2",
    10: "Eb4:0+4 Eb4:6+1 Eb4:7+1",
    11: "Eb4:0+2 C5:2+2 Bb4:4+2 Ab4:6+2",
    12: "F4:0+8",
    13: "F4:0+2 Db5:2+2 C5:4+2 Bb4:6+2",
    14: "G4:0+6 G4:6+2",
    15: "Eb5:0+2 Eb5:2+2 Db5:4+2 Bb4:6+2",
    16: "C5:0+6 Eb4:6+2",
    17: "Eb4:0+2 C5:2+2 Bb4:4+2 Ab4:6+2",
    18: "Eb4:0+6 Eb4:6+2",
    19: "Eb4:0+2 C5:2+2 Bb4:4+2 Ab4:6+2",
    20: "F4:0+6 F4:6+2",
    21: "F4:0+2 Db5:2+2 C5:4+2 Bb4:6+2",
    22: "Eb5:0+2 Eb5:2+2 Eb5:4+2 Eb5:6+2",
    23: "F5:0+2 Eb5:2+2 Db5:4+2 Bb4:6+2",
    24: "Ab4:0+8",
    25: "C5:0+2 C5:2+2 C5:4+4",
    26: "C5:0+2 C5:2+2 C5:4+4",
    27: "C5:0+2 Eb5:2+2 Ab4:4+3 Bb4:7+1",
    28: "C5:0+8",
    29: "Db5:0+2 Db5:2+2 Db5:4+2 Db5:6+2",
    30: "Db5:0+2 C5:2+2 C5:4+2 C5:6+1 C5:7+1",
    31: "C5:0+2 Bb4:2+2 Bb4:4+2 C5:6+2",
    32: "Bb4:0+8",
    33: "C5:0+2 C5:2+2 C5:4+4",
    34: "C5:0+2 C5:2+2 C5:4+4",
    35: "C5:0+2 Eb5:2+2 Ab4:4+3 Bb4:7+1",
    36: "C5:0+8",
    37: "Db5:0+2 Db5:2+2 Db5:4+2 Db5:6+2",
    38: "Db5:0+2 C5:2+2 C5:4+2 C5:6+1 C5:7+1",
    39: "Eb5:0+2 Eb5:2+2 Db5:4+2 Bb4:6+2",
    40: "Ab4:0+4",
}
# Source 1 for Deck the Halls: CPDL no. 47663 (Andrew Sims, MusicXML), the top line, F major, 4/4.
SRC_SIMS = {
    1: "C5:0+6 Bb4:6+2 A4:8+4 G4:12+4",
    2: "F4:0+4 G4:4+4 A4:8+4 F4:12+4",
    3: "G4:0+2 A4:2+2 Bb4:4+2 G4:6+2 A4:8+6 G4:14+2",
    4: "F4:0+4 E4:4+4 F4:8+8",
    5: "C5:0+6 Bb4:6+2 A4:8+4 G4:12+4",
    6: "F4:0+4 G4:4+4 A4:8+4 F4:12+4",
    7: "G4:0+2 A4:2+2 Bb4:4+2 G4:6+2 A4:8+6 G4:14+2",
    8: "F4:0+4 E4:4+4 F4:8+8",
    9: "G4:0+6 A4:6+2 Bb4:8+4 G4:12+4",
    10: "A4:0+6 Bb4:6+2 C5:8+4 G4:12+4",
    11: "A4:0+2 B4:2+2 C5:4+4 D5:8+2 E5:10+2 F5:12+4",
    12: "E5:0+4 D5:4+4 C5:8+8",
    13: "C5:0+6 Bb4:6+2 A4:8+4 G4:12+4",
    14: "F4:0+4 G4:4+4 A4:8+4 F4:12+4",
    15: "D5:0+2 D5:2+2 D5:4+2 D5:6+2 C5:8+6 Bb4:14+2",
    16: "A4:0+4 G4:4+4 F4:8+8",
}
# Source 2 for Deck the Halls: CPDL no. 502 (Rafael Ornes, MusicXML), the top note of each chord on the upper staff, F major, 4/4; its first bar is empty on that staff.
SRC_ORNES = {
    1: "",
    2: "F4:0+4 G4:4+4 A4:8+4 F4:12+4",
    3: "G4:0+2 A4:2+2 Bb4:4+2 G4:6+2 A4:8+6 G4:14+2",
    4: "F4:0+4 E4:4+4 F4:8+8",
    5: "C5:0+6 Bb4:6+2 A4:8+4 G4:12+4",
    6: "F4:0+4 G4:4+4 A4:8+4 F4:12+4",
    7: "G4:0+2 A4:2+2 Bb4:4+2 G4:6+2 A4:8+6 G4:14+2",
    8: "F4:0+4 E4:4+4 F4:8+8",
    9: "G4:0+6 A4:6+2 Bb4:8+4 G4:12+4",
    10: "A4:0+6 Bb4:6+2 C5:8+4 G4:12+4",
    11: "A4:0+2 B4:2+2 C5:4+4 D5:8+2 E5:10+2 F5:12+4",
    12: "E5:0+4 D5:4+4 C5:8+8",
    13: "C5:0+6 Bb4:6+2 A4:8+4 G4:12+4",
    14: "F4:0+4 G4:4+4 A4:8+4 F4:12+4",
    15: "D5:0+2 D5:2+2 D5:4+2 D5:6+2 C5:8+6 Bb4:14+2",
    16: "A4:0+4 G4:4+4 F4:8+8",
}
# Source 3 for Deck the Halls: CPDL no. 39398 (James Gibb's edition of Charles Wood's harmonization, MusicXML), the soprano, E-flat major, 4/4.
SRC_WOOD = {
    1: "Bb4:0+6 Ab4:6+2 G4:8+4 F4:12+4",
    2: "Eb4:0+4 F4:4+4 G4:8+4 Eb4:12+4",
    3: "F4:0+2 G4:2+2 Ab4:4+2 F4:6+2 G4:8+6 F4:14+2",
    4: "Eb4:0+4 D4:4+4 Eb4:8+8",
    5: "Bb4:0+6 Ab4:6+2 G4:8+4 F4:12+4",
    6: "Eb4:0+4 F4:4+4 G4:8+4 Eb4:12+4",
    7: "F4:0+2 G4:2+2 Ab4:4+2 F4:6+2 G4:8+6 F4:14+2",
    8: "Eb4:0+4 D4:4+4 Eb4:8+8",
    9: "F4:0+6 G4:6+2 Ab4:8+4 F4:12+4",
    10: "G4:0+6 Ab4:6+2 Bb4:8+4 F4:12+4",
    11: "G4:0+2 A4:2+2 Bb4:4+4 C5:8+2 D5:10+2 Eb5:12+4",
    12: "D5:0+4 C5:4+4 Bb4:8+8",
    13: "Bb4:0+6 Ab4:6+2 G4:8+4 F4:12+4",
    14: "Eb4:0+4 F4:4+4 G4:8+4 Eb4:12+4",
    15: "C5:0+2 C5:2+2 C5:4+2 C5:6+2 Bb4:8+6 Ab4:14+2",
    16: "G4:0+4 F4:4+4 Eb4:8+8",
}



def src_notes(src, offset_of_bar, shift=0):
    """Parse a typed source ({bar: 'pitch:start+length ...'}) into [(midi, onset, length)], onsets in sixteenths along the tune (bar 1 = 0)."""
    out = []
    for b, txt in src.items():
        off = offset_of_bar(b)
        if off is None:
            continue
        for tok in txt.split():
            p, rest = tok.split(":")
            s, d = rest.split("+")
            out.append((midi(p) + shift, off + int(s), int(d)))
    return sorted(out)


def jb_brown_off(b):          # the file lists the chorus first (bars 1-8), then the verse (bars 9-16); the chart plays the verse first
    return (b - 9) * 16 if b >= 9 else 128 + (b - 1) * 16


def jb_hale_off(b):           # 2/4 bars of 8 sixteenths: verse bars 9-24, chorus bars 25-40
    return (b - 9) * 8 if b <= 24 else 128 + (b - 25) * 8


def dh_off(b):
    return (b - 1) * 16


def note_diffs(chart_n, other_n):
    """Compare two note lists by start and pitch. Returns (only in chart, only in other, same note with another length): each a sorted list of (start, pitch name, ...)."""
    A = {(s, m): d for m, s, d in chart_n}
    B = {(s, m): d for m, s, d in other_n}
    only_a = sorted((s, pname(m)) for (s, m) in A if (s, m) not in B)
    only_b = sorted((s, pname(m)) for (s, m) in B if (s, m) not in A)
    lens = sorted((s, pname(m), A[(s, m)], B[(s, m)]) for (s, m) in A if (s, m) in B and A[(s, m)] != B[(s, m)])
    return only_a, only_b, lens



# the differences between the chart and each typed source that --check expects (the chart is the first source's notes, with the two lyric pickups dropped and two held notes
# written as a half note; the others differ only where an edition splits a held note into a note and a rest or re-strikes it, or adds a pickup)
EXPECT_JB_BROWN = ([], [(124, "D5"), (188, "D5")], [(120, "G4", 8, 4), (184, "A4", 8, 4)])
EXPECT_JB_HALE = ([(111, "D5")], [(46, "F#4"), (62, "D4"), (94, "E4"), (110, "D5")],
                  [(8, "D4", 6, 4), (40, "F#4", 8, 6), (56, "B4", 8, 6), (88, "E4", 8, 6), (108, "D5", 3, 2), (248, "G4", 8, 4)])
EXPECT_DH_ORNES = ([(0, "C5"), (6, "A#4"), (8, "A4"), (12, "G4")], [], [])      # the Ornes edition leaves bar 1 of its top line empty
JB_NOTES = chart_notes(CHART_JB_G)
DH_NOTES = chart_notes(CHART_DH_F)
JB_SRC = {"brown": 38153, "hale": 66808}
DH_SRC = {"sims": 47663, "ornes": 502, "wood": 39398}


# ================================================================ keys: the circle of fifths, semitone distance, the shortest shift
MINUS = "−"
KEY_ORDER = [("C", 0), ("G", 7), ("D", 2), ("A", 9), ("E", 4), ("B", 11), ("F#", 6), ("Db", 1), ("Ab", 8), ("Eb", 3), ("Bb", 10), ("F", 5)]      # clockwise from the top
MINOR_OF = {"C": "A", "G": "E", "D": "B", "A": "F#", "E": "C#", "B": "G#", "F#": "D#", "Db": "Bb", "Ab": "F", "Eb": "C", "Bb": "G", "F": "D"}
KEY_PC = dict(KEY_ORDER)
KEY_SIG = {"C": "no sharps or flats", "G": "1 sharp", "D": "2 sharps", "A": "3 sharps", "E": "4 sharps", "B": "5 sharps", "F#": "6 sharps", "Db": "5 flats", "Ab": "4 flats",
           "Eb": "3 flats", "Bb": "2 flats", "F": "1 flat"}


def circle_pos(pc):
    """Steps clockwise round the circle of fifths from C: a fifth up is 7 semitones, and 7 x 7 = 49 = 1 (mod 12), so the step count of a key is 7 x its pitch class (mod 12)."""
    return (7 * pc) % 12


def sig_of(pc):
    p = circle_pos(pc)
    if p == 0:
        return "no sharps or flats"
    if p <= 6:
        return f"{p} sharp{'s' if p > 1 else ''}"
    return f"{12 - p} flat{'s' if 12 - p > 1 else ''}"


def up_semis(a, b):
    """Semitones going up from key a to key b (0 to 11)."""
    return (KEY_PC[b] - KEY_PC[a]) % 12


def short_shift(a, b):
    """The shorter way from key a to key b in semitones: -5 to +6 (6 is a tie: up or down is the same distance)."""
    d = up_semis(a, b)
    return d if d <= 6 else d - 12


def signed(n):
    return f"+{n}" if n > 0 else (MINUS + str(-n) if n < 0 else "0")


def fifths_apart(a, b):
    """The shorter count of steps round the circle of fifths between two keys (0 to 6)."""
    d = (circle_pos(KEY_PC[b]) - circle_pos(KEY_PC[a])) % 12
    return min(d, 12 - d)


KEY_PAIRS = [("G", "F", "Jingle Bells in G, Deck the Halls in F"), ("Ab", "F", "the 1857 edition of Jingle Bells is in Ab"), ("Eb", "F", "one Deck the Halls edition is in Eb"),
             ("D", "G", "any two keys one fifth apart"), ("C", "F#", "the tritone: up and down are equal"), ("A", "Eb", "another tritone")]


# ================================================================ tempo: ratio, target, percent change, seconds
def ratio(a, b):
    """Faster : slower as a reduced fraction."""
    hi, lo = max(a, b), min(a, b)
    f = Fraction(hi, lo)
    return f.numerator, f.denominator


def pct(orig, target):
    """Percent speed change = (target / original - 1) x 100, as an exact fraction."""
    return (Fraction(target, orig) - 1) * 100


def pct_text(x):
    x = Fraction(x)
    s = f"{float(x):g}" if x.denominator in (1, 2, 4, 5, 8, 10) else f"{float(x):.2f}".rstrip("0").rstrip(".")
    if x > 0:
        return f"+{s}%"
    if x < 0:
        return f"{MINUS}{s.lstrip('-')}%"
    return "0%"


def spb(bpm):
    return Fraction(60, bpm)


def bar_len(bpm, beats=4):
    """Seconds per bar = beats per bar x 60 / BPM (4/4: 240 / BPM; 3/4: 180 / BPM; 2/4: 120 / BPM)."""
    return Fraction(60 * beats, bpm)


A_NAME, A_BPM, A_KEY = "Jingle Bells", 120, "G"       # typical class tempos, inside the range of the tempo marks in the files read
B_NAME, B_BPM, B_KEY = "Deck the Halls", 96, "F"
TARGET = Fraction(A_BPM + B_BPM, 2)       # the mean: 108
TARGET_KEY = "F"
TEMPO_MARKS = {"Jingle Bells": [80, 100, 130, 144], "Deck the Halls": [96, 120, 160]}      # the tempo marks stored in the files read (80 and 144: CPDL 38153 and 66808; 100: a third Jingle Bells file read for its key only)
TEMPOS = (80, 90, 96, 100, 108, 110, 120, 128)
TEMPO_HI = (96, 108, 120)
PAIRS = [(120, 60), (128, 64), (120, 80), (120, 96), (120, 100), (100, 90)]


def pair_meaning(a, b):
    n, d = ratio(a, b)
    if d == 1:
        return f"{n}:1, double-time or half-time"
    if (n, d) == (3, 2):
        return "3:2, a stretch of one third"
    return f"{n}:{d}, close but not a simple multiple"


# ================================================================ the arrangement: 44 bars in six sections
SEC_NAMES = ["Intro", "Jingle Bells", "Bridge", "Deck the Halls", "Mashup", "Outro"]
SEC_BARS = [4, 8, 4, 8, 16, 4]
TOTAL_BARS = sum(SEC_BARS)


def start_bar(i):
    return sum(SEC_BARS[:i]) + 1


def end_bar(i):
    return sum(SEC_BARS[:i + 1])


def start_s(bpm, i):
    return sum(SEC_BARS[:i]) * bar_len(bpm)


def total_s(bpm):
    return TOTAL_BARS * bar_len(bpm)


def rnd(x, nd):
    """Round half up (a 5 rounds up) to nd decimals, on exact fractions."""
    s = Fraction(10) ** nd
    return Fraction(math.floor(Fraction(x) * s + Fraction(1, 2)), 1) / s


def dec(x, nd):
    return f"{float(rnd(x, nd)):.{nd}f}"


def dshort(x, nd):
    """dec() without trailing zeros: 2.500 -> 2.5, 2.000 -> 2."""
    t = dec(x, nd)
    return t.rstrip("0").rstrip(".") if "." in t else t


def fmt(x):
    x = float(x)
    x = round(x + 1e-9, 3)
    return f"{x:.0f}" if x == int(x) else f"{x:g}"


def mmss(x):
    t = int(rnd(x, 0))
    return f"{t // 60}:{t % 60:02d}"


# ================================================================ Smart Tempo and Flex numbers
def length_change(orig, target):
    """How much longer (+) or shorter (-) a stretched audio region gets when the tempo goes from orig to target: orig / target - 1, as percent."""
    return (Fraction(orig, target) - 1) * 100


def semis_from_speed(orig, target):
    """Changing playback speed by target / orig with no time-stretch moves the pitch by 12 x log2(target / orig) semitones."""
    return 12 * math.log2(target / orig)


def freq_ratio(semis):
    return 2 ** (semis / 12)


# ================================================================ layering the two melodies (a quick check on the beats; not a rule of harmony)
SMOOTH, MILD, HARD = 0, 1, 2
CAT_NAMES = ["smooth", "mild", "hard"]
SHIFTS = list(range(-6, 6))


def ic_cat(a, b):
    """Interval class of two notes (0 to 6): 0 unison or octave, 3 and 4 thirds and sixths, 5 fourths and fifths are smooth; 2 (a whole step or minor seventh) is mild;
    1 (a half step or major seventh) and 6 (the tritone) are hard clashes."""
    iv = abs(a - b) % 12
    ic = min(iv, 12 - iv)
    return SMOOTH if ic in (0, 3, 4, 5) else (MILD if ic == 2 else HARD)


def mash_samples(shift, pas, bar=None):
    """Category counts [smooth, mild, hard] on the beats where Jingle Bells' chorus (moved by `shift` semitones) is layered over Deck the Halls bars 1-8 (pass 0) or 9-16 (pass 1)."""
    c = [0, 0, 0]
    rng_ = range(0, 128, 4) if bar is None else range(bar * 16, bar * 16 + 16, 4)
    for t in rng_:
        c[ic_cat(sound(JB_NOTES, 128 + t) + shift, sound(DH_NOTES, pas * 128 + t))] += 1
    return c


def shift_counts(shift):
    a, b = mash_samples(shift, 0), mash_samples(shift, 1)
    return [x + y for x, y in zip(a, b)]


BEST_SHIFT = min(SHIFTS, key=lambda s: (shift_counts(s)[HARD], -shift_counts(s)[SMOOTH]))
CHORDS_F = [("F", "I", (5, 9, 0)), ("C", "V", (0, 4, 7)), ("Bb", "IV", (10, 2, 5)), ("Dm", "vi", (2, 5, 9)), ("Gm", "ii", (7, 10, 2)), ("Am", "iii", (9, 0, 4))]   # in priority order
CHORD_G = {"F": "G", "C": "D", "Bb": "C", "Dm": "Em", "Gm": "Am", "Am": "Bm"}


ROUGH = min(range(1, 17), key=lambda m: (mash_samples(BEST_SHIFT, (m - 1) // 8, (m - 1) % 8)[SMOOTH], -mash_samples(BEST_SHIFT, (m - 1) // 8, (m - 1) % 8)[HARD]))


def best_chord(m):
    """The triad in F major (I, ii, iii, IV, V or vi) with the most chord tones among the 8 beat notes of mashup bar m (1 to 16): 4 beats x 2 melodies. Ties go in the order of CHORDS_F."""
    pas, j = (m - 1) // 8, (m - 1) % 8
    notes = []
    for k in range(4):
        t = j * 16 + k * 4
        notes += [(sound(JB_NOTES, 128 + t) + BEST_SHIFT) % 12, sound(DH_NOTES, pas * 128 + t) % 12]
    scores = [(sum(1 for n in notes if n in pcs), -i, name, rn) for i, (name, rn, pcs) in enumerate(CHORDS_F)]
    n, _, name, rn = max(scores)
    return name, rn, n


# ================================================================ the groove cards (16 steps a bar; x = a hit)
GROOVE_LANES = ["Hat", "Snare", "Kick"]
GROOVES = {
    "steady": {"Hat": "x.x.x.x.x.x.x.x.", "Snare": "....x.......x...", "Kick": "x.....x.x......."},
    "half":   {"Hat": "x.x.x.x.x.x.x.x.", "Snare": "........x.......", "Kick": "x.........x....."},
}
GROOVE_NAMES = {"steady": "Steady groove", "half": "Half-time groove"}
GROOVE_FACTS = {"steady": (3, 2, 8), "half": (2, 1, 8)}      # kick, snare and hat hits per bar: checked against the strings
GROOVE_TEXT = {
    "steady": ("Kick on beat 1, the “and” of 2 and beat 3; snare on beats 2 and 4; hat on every eighth note.",
               "Bass plays the chord root on beat 1 and again on the eighths. Keys or guitar play each chord once or twice a bar.",
               "Add a snare hit on the “and” of 4 in the last bar of every four to push into the next phrase."),
    "half": ("Kick on beat 1 and the “and” of 3; one snare hit on beat 3; hat on every eighth note. The backbeat lands half as often, so it feels half as fast.",
             "Bass holds each chord root for half a bar. Pads or keys play the chord for the whole bar.",
             "Use it under the Deck the Halls section, or under the intro, then switch to the steady groove for the mashup."),
}


def hits(g, ln):
    return [i for i, c in enumerate(GROOVES[g][ln]) if c == "x"]


# ================================================================ the arrangement map: which elements play in which of the six sections
ELEMENTS = [
    ("Drums", ["light", "plays", "fill", "plays", "full", ""]),
    ("Bass", ["", "plays", "", "plays", "full", "root only"]),
    ("Chords (pad or keys)", ["pad", "plays", "holds", "plays", "full", "holds"]),
    ("Jingle Bells line", ["", "lead", "hook", "", "layered", ""]),
    ("Deck the Halls line", ["", "", "hook", "lead", "layered", ""]),
    ("Counter-line or arp", ["", "", "", "", "plays", ""]),
    ("Riser or reverb tail", ["", "", "riser", "", "", "rings out"]),
]
ELEM_PLAYING = [sum(1 for _, cells in ELEMENTS if cells[i]) for i in range(len(SEC_NAMES))]      # 2, 4, 5, 4, 6, 3



# ================================================================ the project text (original; students read these pages)
THEME = ("“Jingle Bells” and “Deck the Halls” are two of the best-known winter carols in English. A DJ-style mashup plays two songs together, or one after the other, "
         "and it only works when the songs agree on two things: how fast they go and what key they are in. This project asks a music-technology question: "
         "how do you make two tunes that were never meant to meet fit together? The answer is arithmetic and listening: ratios, percents and semitones, and a careful ear.")
SOURCE_NOTE = ("“Jingle Bells” was written by James Lord Pierpont and published in Boston on September 16, 1857, under the title “The One Horse Open Sleigh”; the chorus that people "
               "sing today is a later form that is documented on a recording from 1898. “Deck the Halls” is a Welsh melody, commonly dated to the sixteenth century, that belongs "
               "to a winter song called “Nos Galan”; its English words, by Thomas Oliphant, date to 1862. All of this is far older than the 1930 cutoff, so both tunes are in the "
               "public domain. Only the titles are given: no lyrics are printed, and nobody needs to sing.")
OVERVIEW = ("Make a DJ-style mashup in Logic Pro from two public-domain carols, “Jingle Bells” and “Deck the Halls”. Work out the ratio of their tempos, choose a target tempo and calculate "
            "each song’s percent speed change and the seconds per bar. Find the shortest transposition between their keys and name each song’s new key. Enter both melodies from a note chart "
            "(16 bars of 4/4 each), check the match with Smart Tempo and Flex Time or Flex Pitch if your version has them, and layer the two melodies over one groove. Arrange 44 bars in six sections: "
            "an intro, each carol, a bridge, the mashup and an outro. Nobody needs to compose a melody.")
GOALS = ["Compare two tempos as a ratio, choose a target tempo, and calculate each song’s percent speed change and the seconds per bar at the target",
         "Find the semitone distance between two keys, choose the shorter direction (at most 6 semitones) and name each song’s key after the move",
         "Enter two public-domain melodies into Logic Pro’s Piano Roll from note charts, and check the match with Smart Tempo and Flex if your version has them",
         "Layer both melodies over one groove, arrange 44 bars with a bar-and-time table, then mix, bounce and reflect on the choices"]
VOCAB = [("Mashup", "A track that plays parts of two songs together or back to back. It works when the two songs share a tempo and a key"),
         ("Tempo match", "Making two songs run at the same speed: compare the BPM numbers as a ratio, choose a target tempo and change each song by a percent"),
         ("Semitone", "The smallest step on a keyboard, from one key to the very next. Twelve semitones make an octave; moving every note by the same number of semitones is transposing"),
         ("Time stretch (Flex Time)", "Making an audio recording longer or shorter without changing its pitch, so that it can follow a new tempo"),
         ("Smart Tempo", "A Logic Pro feature, if your version has it, that listens to a recording and works out its tempo")]
REQS = ["Choose a target tempo on the tempo page (page @TEMPO) and work out each carol’s percent change and the seconds per bar",
        "Choose a target key on the key page (page @KEYS) with each carol’s shift and new key",
        "Enter both melodies from the note charts (pages @CHART1–@CHART2) in your target key; every pitch and length matches the chart",
        "Check the match with Smart Tempo and Flex if your version has them, and compare the audio lengths with page @FLEX",
        "Layer the two melodies with the clash check (page @LAYER) and build the groove (page @GROOVE)",
        "Arrange 44 bars in six sections with markers (page @MAP), mix with the checklist (page @MIX) and bounce",
        "Reflect on your choices (page @REFLECT)"]
FILE_NAME = "“Your Name – Holiday Mashup”"
STEP_NAMES = ["Match the tempo", "Match the key", "Enter the melodies", "Check with Smart Tempo and Flex", "Layer and build the groove", "Arrange and mix", "Present &amp; get feedback"]
STEPS = ["<b>Match the tempo</b> — Use the tempo page (page @TEMPO) to find the ratio of the two carols’ tempos, choose a target tempo and calculate each carol’s percent change; then work out how long one bar and the 44-bar track last",
         "<b>Match the key</b> — Use the key page (page @KEYS) to count the semitones between the two keys, choose the shorter direction and name each carol’s new key and its relative minor",
         "<b>Enter the melodies</b> — Read the note charts (pages @CHART1–@CHART2). Put each melody on its own Software Instrument track in the Piano Roll, in your target key, and check every pitch and length against the chart",
         "<b>Check with Smart Tempo and Flex</b> — Bounce one melody to audio, then use Smart Tempo and Flex Time, if your version has them, to follow the target tempo, and compare the lengths with the numbers on page @FLEX",
         "<b>Layer and build the groove</b> — Run the clash check on page @LAYER, choose the chords for the mashup and build a steady or half-time groove from the cards on page @GROOVE",
         "<b>Arrange and mix</b> — Lay out 44 bars with the map (page @MAP): an intro, each carol, a bridge, the mashup and an outro, with a marker at the start of each section "
         "(Logic quick reference: page @LOGICREF). Then mix with the checklist (page @MIX) and bounce",
         "<b>Present &amp; get feedback</b> — Write three questions you want classmates to answer about your match. Play your track, say how you matched the tempo and the key, "
         "and answer at least 2 of each classmate’s questions. Then reflect (page @REFLECT)."]
TIPS = ["Match the tempo and the key before you layer anything: two melodies in different keys cannot be rescued by the mix.",
        "Move the song that needs the smaller change, or meet in the middle: the tempo page shows both choices side by side.",
        "Listen to each melody alone at the target tempo before you layer them.",
        "Save a new version of your project at the end of each class, so you can always go back."]
CHECK = ["Bounced .mp3 or .wav of your whole track, 44 bars long",
         "Zipped .logicx project file handed in",
         f"Files named correctly: {FILE_NAME}",
         "Tempo page and key page filled in, with both percent changes and both shifts",
         "Rubric self-score done (page @RUBRIC)",
         "I can say my target tempo, my target key and why I chose them"]
RUBRIC_NOTE = "Each category is scored 1–5. Score yourself first; the final grade is the average of your score and your teacher’s."
LEVELS = [1, 2, 3, 4, 5]
RUBRIC = [
    ("Tempo Match", ["No tempo work", "Tempos are listed, but the ratio or the percent changes are missing or wrong", "The ratio and the target tempo are right; some percent changes or seconds per bar have errors",
                     "The ratio, the target tempo, both percent changes and the seconds per bar are right, and the project tempo is set to the target",
                     "All the tempo math is right and the choice of target tempo is explained"]),
    ("Key Match", ["No key work", "The keys are named, but the shift is missing or wrong", "The shift is right, but a new key or a relative minor is wrong",
                   "The shift is the shorter direction (at most 6 semitones) and both new keys are named correctly",
                   "The shift, both new keys and their relative minors are correct, with a reason for the direction"]),
    ("Melodies & Layering", ["No melodies entered", "One melody entered, or many wrong pitches", "Both melodies are entered, with several wrong notes or lengths",
                             "Both melodies match the charts in the target key and play together over one groove",
                             "The melodies match exactly, the clash check is used to choose the layering and the layered section sounds clean"]),
    ("Arrangement & Mix", ["Parts are too loud or too quiet to tell apart", "A few parts can be heard; others are buried or clip",
                           "Most parts can be heard; the sections are not clear", "Six sections of 4, 8, 4, 8, 16 and 4 bars with markers; every part can be heard and nothing clips",
                           "The mashup section is the biggest, both melodies stay clear and the low end is tight"]),
    ("Plan & Reflection", ["Plans, presentation or reflection missing", "Thin plan; little to say about choices", "Plan and reflection complete, with basic detail",
                           "Clear plan; thoughtful reflection and good answers to questions", "Insightful reflection and a polished, confident presentation"]),
]
RUBRIC_TOTAL = 25
RUBRIC_SHORT = ["All the tempo math is right and the target is explained",
                "The shift and both new keys are right, with a reason",
                "Exact melodies and a clean layered section",
                "The mashup is the biggest section and the mix is clean",
                "Insightful reflection and a polished, confident presentation"]
RUBRIC_SLIDE_LINE = "Scored 1–5 · final grade = average of your score and mine, out of 25"
RUBRIC_ROW_PITCH = 0.86
RUBRIC_LINE_Y = 6.3

TN_REINFORCES = ("This project teaches why two songs do not fit together by default and what it takes to make them fit. Students learn to compare tempos as a ratio, to choose a target tempo "
                 "and turn it into a percent change and seconds per bar, to count semitones between keys with the circle of fifths and choose the shorter move, and to check the result by ear, "
                 "with a simple clash test and with Logic Pro’s Smart Tempo and Flex tools if their version has them.")
STRUGGLES = ["The percent change comes out backwards: it is (target ÷ original − 1) × 100, so a song that has to speed up is positive and one that has to slow down is negative (page @TEMPO).",
             "The key shift goes the long way round: count both directions on the circle of fifths or the table, and take the one that is 6 semitones or fewer (page @KEYS).",
             "The melody is entered in the wrong octave: Logic calls middle C “C3” by default and the chart calls it C4, so subtract one from the chart’s octave number (page @CHART1).",
             "Flex Time makes the audio sound strange, or the tool is missing in their version: keep the stretch small by meeting in the middle, and remember that MIDI melodies need neither tool (page @FLEX)."]
VAR_EASY = ("Let students choose one carol’s tempo as the target, so that only one song changes (page " + str(pg("tempo")) + "), enter both melodies in F major, "
            "and skip the Smart Tempo and Flex step (page " + str(pg("flex")) + "). Ask for 2 questions at the presentation.")
VAR_HARD = ("Add a third carol from a score you may legally use and find its ratio and shift against the other two, or put a key change into the mashup section (page " + str(pg("keys")) + "), "
            "or write a second chord loop for the mashup and compare the two by ear and with the clash check (page " + str(pg("layer")) + ").")
RESOURCES = [("Tempo and key pages (pages @TEMPO–@KEYS)",
              "Formulas, three target tempos with percent changes and seconds per bar, six tempo pairs with their ratios, and the semitone distance between key pairs with the circle of fifths."),
             ("Note charts (pages @CHART1–@CHART2)",
              "Both melodies as piano rolls and bar-by-bar tables, in the key each is usually printed in and in the target key, with the sources the notes were checked against."),
             ("Smart Tempo and Flex page and the clash check (pages @FLEX–@LAYER)",
              "Audio-length numbers, pitch ratios and a beat-by-beat check of how the two melodies sound together for every possible shift, with suggested chords for the mashup."),
             ("Worked example (pages @EXAMPLE–@EXAMPLE2)",
              "An invented plan at 108 BPM in F major: a 44-bar track that lasts 97.78 seconds, with its tempo and key math, sections and mix notes. A model, not a template.")]
TN_NOTE = ("A good listening day: play the two carols one after the other with no matching, then play a student’s matched version, and ask the class what changed. Ask which was harder to fix, "
           "the tempo or the key. This kit names no recordings or artists, and both melodies are public domain.")
GRADING = ["The rubric: five categories, each scored 1–5, /25 (page @RUBRIC). Students score themselves first; the final grade is the "
           "average of their score and yours.",
           "Tempo Match (rubric row 1): check the ratio, the target tempo and both percent changes against the tempo page (page @TEMPO).",
           "Key Match (rubric row 2): check that the shift is the shorter direction and that the new key names are right (page @KEYS).",
           "Melodies & Layering (rubric row 3): play each melody alone against the chart, then the layered section (pages @CHART1–@CHART2 and @LAYER).",
           "Arrangement & Mix (rubric row 4): check the markers against the map, listen for both melodies over the groove and check the meter for clipping (pages @MAP and @MIX).",
           "Plan & Reflection (rubric row 5): the tempo and key pages, the feedback questions and the Reflection page (page @REFLECT) are the evidence."]
PACING = [
    {"n": 1, "owner": "Hear the problem, then match the tempo and the key.",
     "do": "Slides 1–7: the think-and-share, what the project is, the three classes, the tempo ratio, seconds per bar and the circle of fifths. Hand out the tempo page, the key page and the note charts. "
           "Before they leave, students have a target tempo, a target key, both percent changes and both shifts, and the first melody started.",
     "slides": (1, 7), "pages": ["tempo", "keys", "chart1", "chart2", "proj1", "proj2", "proj3", "vocab"],
     "deck": "Think and share · tempo ratio · seconds per bar · the circle of fifths"},
    {"n": 2, "owner": "Enter and check the melodies, then layer them over a groove.",
     "do": "Slides 8–10: the clash check, Smart Tempo and Flex, and building it in Logic. Students finish both melodies, run the Smart Tempo and Flex check, layer the melodies and choose chords, "
           "then build the groove. Walk the room with one question: do the two melodies sound as if they belong together?",
     "slides": (8, 10), "pages": ["chart1", "chart2", "flex", "layer", "groove", "present"], "deck": "The clash check · Smart Tempo and Flex · build it in Logic"},
    {"n": 3, "owner": "Arrange 44 bars, mix, present and reflect.",
     "do": "Slides 11–15: the arrangement map, what to turn in, the rubric, presentation day and the close. Students lay out the six sections, add a marker for each, "
           "then mix with the checklist, bounce and present.",
     "slides": (11, 15), "pages": ["map", "mix", "rubric", "present", "reflect"], "deck": "Arrangement · checklist · rubric · presentations"},
]
PACING_EXTRA = (
    '<div class="cols" style="margin-top:4pt;gap:14pt"><div class="box acc-b"><span class="k">The one thing to do on Class 1</span>'
    '<p style="margin:0;font-size:10.6pt">Make sure every student leaves with a target tempo and a target key from the tempo and key pages, with both percent changes and both shifts written down, '
    'so that Class 2 is all melodies and layering. Ask a few students to say their numbers aloud before they go.</p></div>'
    '<div class="box"><span class="k">With two or four periods</span><p style="margin:0;font-size:10.6pt"><b>Two classes:</b> Class 1 is the tempo, the key and the melodies; '
    'Class 2 is the check, the layering, the arrangement, the mix and short presentations. <b>Four classes:</b> keep Classes 1 and 2, then spend Class 3 on the arrangement and the mix, and '
    'Class 4 on presentations and reflection.</p></div></div>')
PACING_SIZE = 10.6
TN2_SIZE = 10.3

SONG_NOTE = ("No audio, recordings or lyrics are included. Both melodies are public-domain tunes printed as note charts, and only the titles are given. "
             "Students make every sound themselves, from the instruments, samples and loops in Logic and from their own playing.")
CREDITS = ["The tempo, key and layering pages, groove cards, arrangement map, checklists and worked example: original work, Hudson Beat. The melodies are the public-domain tunes of "
           "“Jingle Bells” (James Lord Pierpont, 1857) and “Deck the Halls” (a Welsh melody), entered as note charts and compared note by note with scores on the Choral Public Domain Library: "
           "for Jingle Bells, CPDL nos. 38153 and 66808; for Deck the Halls, CPDL nos. 47663, 502 and 39398. Those editions carry their editors’ own CPDL licenses; this kit prints only the melody "
           "notes, which are in the public domain, and none of their engraving, words or arrangements. Facts about the songs come from the English Wikipedia articles “Jingle Bells” and “Deck the Halls”. "
           "No lyrics, recordings or other arrangements are included.",
           "The cover illustration was made with digital and AI tools. No audio, video, album art, screenshots, presets, templates or links from other sources are included. "
           "No student work is included. All timing facts are arithmetic shown in the product."]
LOGIC_INTRO = ("Where to find the tools a mashup project is likely to use. Demonstrate what your class needs on Classes 1 and 2 and then "
               "let students work. Names are from current Logic Pro versions; labels move between versions, so check yours.")
LOGIC_REF = [("Project and tempo", "File › New…, then a Software Instrument track to start. Set the project tempo in the control bar to your target tempo and keep the time signature at 4/4. "
              "Smart Tempo, if your version has it, can detect the tempo of a recording; for the MIDI melodies in this project set the tempo yourself so that the bar arithmetic on the tempo page holds."),
             ("Enter the melodies", "Open the Piano Roll and draw the notes with the pencil tool on a grid of 1/16 or 1/8, one melody per track. Pitch names run down the left. Logic names middle C “C3” by default; "
              "the chart calls it C4, so subtract one from the chart’s octave number."),
             ("Move a melody to the target key", "To move a MIDI region by semitones, look for Transpose in the region inspector, or select its notes in the Piano Roll and move them up or down by the number of "
              "semitones from the key page. If your version labels it differently, use the Piano Roll. The charts list every note in both keys, so you can check the result."),
             ("Smart Tempo", "Smart Tempo, if your version has it, analyzes the tempo of a recording that you import or record, and you choose whether the project follows the recording or the recording follows the project. "
              "Look in the project settings, the tempo display and the region inspector for its options, since the places vary between versions. A detected tempo that is half or double what you expect means the tempos are in a 2:1 ratio."),
             ("Flex Time", "Flex Time, if your version has it, stretches an audio region so that it follows a new tempo without changing its pitch. Look in the region or track inspector for the Flex and Follow settings and "
              "turn them on for the audio region, then change the project tempo to your target and compare the region’s length with the numbers on the Smart Tempo and Flex page. Small stretches sound natural; large ones can sound artificial."),
             ("Flex Pitch", "Flex Pitch, if your version has it, edits the pitch of a single-line audio recording without changing its length: look in the region or track inspector for the Flex settings and choose Flex Pitch as the mode. "
              "It is made for fine pitch corrections; to move a whole MIDI melody by semitones, use Transpose instead."),
             ("Drums, bass and chords", "Use Drum Machine Designer with a kick, a snare or clap and a hat on three pads. In the Piano Roll set the grid to 1/16 and click in the hits from your groove card. "
              "Use Alchemy or Retro Synth for a bass and a pad, and keep the bass to one note at a time in a low octave. Session Players, if your version has them, can play chords and a groove once you choose the chords yourself; they are optional."),
             ("Sections with markers", "Show the Marker global track (the Global Tracks controls or the View menu). Add a marker with the plus (+) button in that track, "
              "or with a Create Marker key command if your version has one, then drag or type it to the bars on your arrangement map. Name them Intro, Jingle Bells, Bridge, Deck the Halls, Mashup and Outro."),
             ("Mixer, automation and bounce", "Press X for the Mixer and set levels and pan. Press A to show automation. Keep both melodies clear above the groove, and keep the master out of the red. "
              "Then File › Bounce › Project or Section (Command-B), MP3 or WAV, for the whole track. In Finder, Control-click the .logicx and choose Compress.")]
PRESENT_CHECK = [f"Files named {FILE_NAME}; the .mp3 or .wav and the zipped .logicx handed in",
                 "Reflection page done (page @REFLECT)", "Three questions for classmates written",
                 "Rubric self-score done (page @RUBRIC)"]
VOCAB_PROMPT = "Where it shows up in my track:"
TN1_EXTRA = (
    '<div class="box acc-b" style="margin-top:4pt"><span class="k">Where this kit helps with each struggle</span><ul style="margin:0">'
    '<li style="font-size:12pt;margin-bottom:3pt">The percent change: the tempo page (page @TEMPO) gives the formula, a worked pair and a table for six tempo pairs.</li>'
    '<li style="font-size:12pt;margin-bottom:3pt">The shift: the key page (page @KEYS) counts the semitones both ways round for six key pairs and draws the circle of fifths.</li>'
    '<li style="font-size:12pt;margin-bottom:3pt">The octave: the note charts (pages @CHART1–@CHART2) list every note in both keys, and the Logic quick reference (page @LOGICREF) explains Logic’s octave names.</li>'
    '<li style="font-size:12pt;margin-bottom:0">Flex: the Smart Tempo and Flex page (page @FLEX) gives the audio lengths to expect, so students can tell a good stretch from a bad one.</li></ul></div>')
TN1_SIZE = 11.8
PROJ_SIZE = 11.4
VOCAB_GAP = 8
LOGIC_SIZE = 9.6
PROJ1_EXTRA = ""
RUBRIC_EXTRA = ""

# ================================================================ the worked example: an invented plan at 108 BPM in F major
EX_BPM = int(TARGET)
EX_BAR_S = bar_len(EX_BPM)
EX_WEAK = "I will speed up one song and slow the other and hope that they match."
EX_STRONG = ("My mashup joins Jingle Bells (typical class tempo 120 BPM, notated in G major) and Deck the Halls (96 BPM, notated in F major), both in 4/4. The tempos are in the ratio 120 : 96 = 5 : 4, "
             "so neither is half or double the other. I chose the mean, (120 + 96) ÷ 2 = 108 BPM. Jingle Bells changes by (108 ÷ 120 − 1) × 100 = −10% and Deck the Halls by (108 ÷ 96 − 1) × 100 = +12.5%. "
             "One bar lasts 240 ÷ 108 = 2.222 seconds, so my 44-bar track lasts 97.78 seconds. The keys are 2 semitones apart: G down to F is −2 and F up to G is +10, so the shorter move is −2. "
             "Jingle Bells goes down to F major (its relative minor goes from E minor to D minor) and Deck the Halls stays in F major. I layer the Jingle Bells chorus over Deck the Halls twice, "
             "and with the −2 shift the beat check finds 45 smooth, 14 mild and 5 hard pairs out of 64, the fewest hard clashes of any shift.")
EX_QUESTIONS = ["Did the two carols sound as if they belong together in the mashup section? Which bar felt strange, if any?",
                "Could you tell which carol changed more when I matched the tempo?",
                "Was the second layered pass different enough from the first?"]
EX_MIX = ("The chords and the groove sit under the melodies; the bass holds one root for half a bar and is cut below 40 Hz with a Channel EQ, if I have it; the Jingle Bells line is an octave higher than "
          "the Deck the Halls line in the mashup, so that the two can be told apart; the hat is quiet; the reverb on the last chord rings out over bars 43 and 44")
EX_SEC_NOTES = ["A soft pad and a light half-time kick and hat", "Jingle Bells chorus on piano; bass and steady groove join",
                "Two bars of each melody, a drum fill and a riser", "Deck the Halls, bars 1 to 8, on a pluck over half-time drums",
                "Both melodies over the steady groove; Jingle Bells an octave up", "The pad holds the last chord; bass root only; reverb rings out"]



# ================================================================ drawings (all in code, labels logged for the fit check)
def padded(body, W, H, M=10):
    """Wrap a drawing's body with M units of clear padding on all four sides (wider than the thickest outer stroke), so no edge pixel is ever inked."""
    return f'<g transform="translate({M},{M})">{body}</g>', W + 2 * M, H + 2 * M


def roll_body(notes, nsteps, bar_len, beat, lo, hi, W=1100, row_h=24, first_bar=0, chords=None, name="roll", key_w=80, head=30, fs_note=None, namer=None):
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
        nm = (namer or pname)(m)
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




def tune_roll(which, a, b, W=1100, name=None, row_h=18):
    """Bars a..b-1 (0-based) of a chart in its notated key as a roll. which = 'JB' (G major) or 'DH' (F major)."""
    chart, key, (lo, hi) = (CHART_JB_G, KEY_JB, JB_ROWS) if which == "JB" else (CHART_DH_F, KEY_DH, DH_ROWS)
    nts = [(spell(m, key), s - a * 16, d) for m, s, d in chart_notes(chart) if a * 16 <= s < b * 16]
    return roll_body(nts, (b - a) * 16, 16, 4, lo, hi, W, row_h, a + 1, None, name or f"roll {which} {a}-{b}", namer=lambda m: spell(m, key))


def hero_body():
    """The library's mixing-console line art (art/hero.png, used whole). The viewBox only trims fully transparent margin: the art's own pixels
    (x 22-1377, y 181-1217 of 1400) stay at least 40 units inside it, which --check proves from the file."""
    return (f'<image href="../art/hero.png" x="{-HX}" y="{-HY}" width="1400" height="1400"/>', HW, HH)


HX, HY, HW, HH = -20, 140, 1440, 1120


def circle_body(W=1000, name="circle"):
    """The circle of fifths: 12 major keys round the outside (a fifth up each step clockwise), their relative minors inside. G and F, the keys of the two carols,
    are filled; the short arc between them runs through C."""
    cx = cy = W / 2
    R, r = 372, 56
    out = []
    pos = {}
    for i, (k, pc) in enumerate(KEY_ORDER):
        ang = math.radians(-90 + 30 * i)
        pos[k] = (cx + R * math.cos(ang), cy + R * math.sin(ang), ang)
    # the short way from G to F, through C
    gx, gy, ga = pos["G"]
    fx, fy, fa = pos["F"]
    out.append(f'<path d="M {gx:.1f} {gy:.1f} A {R} {R} 0 0 0 {fx:.1f} {fy:.1f}" fill="none" stroke="{ACCENT}" stroke-width="16" stroke-linecap="round"/>')
    out.append(f'<circle cx="{cx}" cy="{cy}" r="{R - r - 12}" fill="none" stroke="#bbb" stroke-width="2"/>')
    for k, pc in KEY_ORDER:
        x, y, ang = pos[k]
        hi = k in ("G", "F")
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{ACCENT if hi else (ACC_LIGHT if k == "C" else "#fff")}" stroke="#000" stroke-width="5"/>')
        lbl = "F#" if k == "F#" else k
        out.append(D.t_(x, y + 13, lbl, 40, 700, fill_="#fff" if hi else "#000"))
        D.lab(name + " keys", lbl, 40, 2 * r - 22)
        mx_, my_ = cx + (R - 118) * math.cos(ang), cy + (R - 118) * math.sin(ang)
        mn = MINOR_OF[k] + "m"
        out.append(f'<circle cx="{mx_:.1f}" cy="{my_:.1f}" r="44" fill="#fff" stroke="#555" stroke-width="3"/>')
        out.append(D.t_(mx_, my_ + 11, mn, 32, 600, fill_="#333"))
        D.lab(name + " minors", mn, 32, 2 * 44 - 14)
    t1, t2, t3 = "G TO F", "2 semitones down", "major outside, minor in"
    out.append(D.t_(cx, cy - 10, t1, 56, 700, fill_=ACCENT))
    D.lab(name + " mid", t1, 56, 330)
    out.append(D.t_(cx, cy + 34, t2, 34, 600))
    D.lab(name + " mid", t2, 34, 340)
    out.append(D.t_(cx, cy + 74, t3, 26, 500, fill_="#444"))
    D.lab(name + " mid", t3, 26, 340)
    return padded("".join(out), W, W, 14)


def tempo_body(W=1500, name="tempo"):
    """A tempo line from 90 to 130 BPM: Deck the Halls at 96, the target at 108 and Jingle Bells at 120, arrows to the target with the percent change, and the seconds per bar."""
    lo, hi = 88, 128
    x0, x1 = 90, W - 90
    X = lambda b: x0 + (b - lo) / (hi - lo) * (x1 - x0)
    y = 190
    out = [f'<line x1="{x0}" y1="{y}" x2="{x1}" y2="{y}" stroke="#000" stroke-width="5" stroke-linecap="round"/>']
    for b in range(88, 129, 4):
        out.append(f'<line x1="{X(b):.1f}" y1="{y - 10}" x2="{X(b):.1f}" y2="{y + 10}" stroke="#000" stroke-width="3"/>')
        out.append(D.t_(X(b), y + 42, str(b), 22, 500, fill_="#555"))
        D.lab(name + " axis", str(b), 22, 60)
    out.append(D.t_(x1, y + 128, "beats per minute (BPM)", 22, 500, anchor="end", fill_="#555"))
    D.lab(name + " axis", "beats per minute (BPM)", 22, 400)
    for bpm, nm_, col in ((B_BPM, B_NAME, "#000"), (int(TARGET), "TARGET", ACCENT), (A_BPM, A_NAME, "#000")):
        x = X(bpm)
        out.append(f'<circle cx="{x:.1f}" cy="{y}" r="22" fill="{col}" stroke="#000" stroke-width="4"/>')
        l1 = f"{bpm} BPM"
        out.append(D.t_(x, 78, nm_.upper(), 28, 700, fill_=ACCENT if col == ACCENT else "#000"))
        D.lab(name + " names", nm_.upper(), 28, 300)
        out.append(D.t_(x, 118, l1, 30, 700))
        D.lab(name + " bpm", l1, 30, 200)
        l2 = f"{dshort(bar_len(bpm), 3)} s per bar"
        out.append(D.t_(x, y + 92, l2, 24, 500, fill_="#333"))
        D.lab(name + " spb", l2, 24, 230)
    # arrows from each carol to the target
    for bpm in (B_BPM, A_BPM):
        xa, xb = X(bpm), X(TARGET)
        d = 1 if xb > xa else -1
        xs, xe = xa + d * 34, xb - d * 34
        out.append(f'<line x1="{xs:.1f}" y1="{y - 36}" x2="{xe:.1f}" y2="{y - 36}" stroke="{ACCENT}" stroke-width="7" stroke-linecap="round"/>')
        out.append(f'<polygon points="{xe + d * 4:.1f},{y - 36} {xe - d * 18:.1f},{y - 50} {xe - d * 18:.1f},{y - 22}" fill="{ACCENT}"/>')
        lbl = pct_text(pct(bpm, TARGET))
        out.append(D.t_((xs + xe) / 2, y - 52, lbl, 32, 700, fill_=ACCENT))
        D.lab(name + " pct", lbl, 32, abs(xe - xs) - 10)
    return padded("".join(out), W, y + 146, 14)


def shift_body(W=1500, name="shift"):
    """Stacked bars: for each shift of Jingle Bells from -6 to +5 semitones, the 64 beats of the mashup split into smooth, mild and hard pairs. The key-matched shift has the fewest hard."""
    gx, gy, gh = 120, 70, 300
    bw = (W - gx - 30) / len(SHIFTS)
    sc = gh / 64
    out = []
    for v in (0, 16, 32, 48, 64):
        yy = gy + gh - v * sc
        out.append(f'<line x1="{gx}" y1="{yy:.1f}" x2="{W - 30}" y2="{yy:.1f}" stroke="#ccc" stroke-width="1.5"/>')
        out.append(D.t_(gx - 14, yy + 8, str(v), 22, 500, anchor="end", fill_="#555"))
    out.append(D.t_(gx - 14, gy - 22, "of 64", 22, 600, anchor="end", fill_="#555"))
    fills = [ACC_LIGHT, "#b9b9b9", "#000"]
    for i, s in enumerate(SHIFTS):
        cnt = shift_counts(s)
        x = gx + i * bw + 8
        w = bw - 16
        yb = gy + gh
        for cat in (SMOOTH, MILD, HARD):
            h = cnt[cat] * sc
            if h <= 0:
                continue
            yb -= h
            out.append(f'<rect x="{x:.1f}" y="{yb:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{fills[cat]}" stroke="#000" stroke-width="2.5"/>')
            if h >= 26:
                out.append(D.t_(x + w / 2, yb + h / 2 + 8, str(cnt[cat]), 24, 700, fill_="#fff" if cat == HARD else "#000"))
                D.lab(name + " counts", str(cnt[cat]), 24, w - 8)
        lbl = signed(s)
        best = s == BEST_SHIFT
        out.append(D.t_(x + w / 2, gy + gh + 38, lbl, 28 if best else 24, 700 if best else 500, fill_=ACCENT if best else "#000"))
        D.lab(name + " shifts", lbl, 28, w)
        if best:
            out.append(f'<rect x="{x - 6:.1f}" y="{gy - 8}" width="{w + 12:.1f}" height="{gh + 16 + 54}" rx="8" fill="none" stroke="{ACCENT}" stroke-width="5"/>')
    out.append(D.t_(gx + (W - gx - 30) / 2, gy + gh + 86, "Jingle Bells moved by this many semitones (Deck the Halls stays in F)", 24, 500, fill_="#333"))
    D.lab(name + " cap", "Jingle Bells moved by this many semitones (Deck the Halls stays in F)", 24, W - gx - 40)
    # legend
    lx = gx
    for cat, nm_ in ((SMOOTH, "smooth pairs"), (MILD, "mild"), (HARD, "hard clashes")):
        out.append(f'<rect x="{lx}" y="12" width="30" height="24" fill="{fills[cat]}" stroke="#000" stroke-width="2.5"/>')
        out.append(D.t_(lx + 42, 32, nm_, 24, 600, anchor="start"))
        D.lab(name + " legend", nm_, 24, 200)
        lx += 42 + D.text_w(nm_, 24) + 40
    return padded("".join(out), W, gy + gh + 104, 14)


def grid_for(g, name=None, cw=26):
    meas = [{ln: GROOVES[g][ln] for ln in GROOVE_LANES}]
    return D.grid_body(name or f"grid {g}", meas, [GROOVE_NAMES[g]], GROOVE_LANES, cw=cw, ch=26, gut=100, ls=20, accent_from=0)


def map_body(W=1500, with_time=False, name="map", lf=23, lh=40, cf=20, hf=21, gx=330):
    """The arrangement map: 7 elements (rows) x 6 sections (columns). A cell is filled when the element plays in that section and says what it does there.
    Section names longer than 12 characters are set on two lines."""
    pw = W - gx - 24
    ns = len(SEC_NAMES)
    cw = pw / ns
    hh = (118 if with_time else 90)
    out = []
    for i, nm_ in enumerate(SEC_NAMES):
        cx = gx + (i + 0.5) * cw
        words = nm_.upper().split(" ")
        lines = [nm_.upper()] if len(nm_) <= 12 else [" ".join(words[:-1]), words[-1]]
        yy_ = 28
        for ln_ in lines:
            out.append(D.t_(cx, yy_, ln_, hf, 700))
            D.lab(name + " heads", ln_, hf, cw - 10)
            yy_ += hf + 4
        if len(lines) == 1:
            yy_ += hf + 4
        l2 = f"bars {start_bar(i)}–{end_bar(i)}"
        out.append(D.t_(cx, yy_ + 4, l2, hf - 1, 500, fill_="#555"))
        D.lab(name + " bars", l2, hf - 1, cw - 10)
        if with_time:
            l3 = f"{dec(start_s(EX_BPM, i), 2)}–{dec(start_s(EX_BPM, i + 1), 2)} s"
            out.append(D.t_(cx, yy_ + hf + 8, l3, hf - 2, 500, fill_=ACCENT))
            D.lab(name + " times", l3, hf - 2, cw - 10)
    y0 = hh + 6
    gap = 6
    for r, (el, cells) in enumerate(ELEMENTS):
        yy = y0 + r * (lh + gap)
        lbl = el.upper()
        out.append(D.t_(gx - 14, yy + lh / 2 + lf * .35, lbl, lf, 700, anchor="end"))
        D.lab(name + " rows", lbl, lf, gx - 26)
        for i, txt in enumerate(cells):
            x = gx + i * cw + 3
            if txt:
                out.append(f'<rect x="{x:.1f}" y="{yy}" width="{cw - 6:.1f}" height="{lh}" rx="6" fill="{ACC_LIGHT}" stroke="#000" stroke-width="2.5"/>')
                out.append(D.t_(x + (cw - 6) / 2, yy + lh / 2 + cf * .35, txt, cf, 600))
                D.lab(name + " cells", txt, cf, cw - 22)
            else:
                out.append(f'<rect x="{x:.1f}" y="{yy}" width="{cw - 6:.1f}" height="{lh}" rx="6" fill="#fff" stroke="#bbb" stroke-width="1.5"/>')
    yb = y0 + len(ELEMENTS) * (lh + gap) + 6
    out.append(f'<line x1="{gx}" y1="{yb - 6}" x2="{gx + pw:.1f}" y2="{yb - 6}" stroke="#000" stroke-width="2.5"/>')
    lbl = "ELEMENTS PLAYING"
    out.append(D.t_(gx - 14, yb + 32, lbl, lf, 700, anchor="end", fill_=ACCENT))
    D.lab(name + " rows", lbl, lf, gx - 26)
    for i in range(ns):
        out.append(D.t_(gx + (i + 0.5) * cw, yb + 34, str(ELEM_PLAYING[i]), lf + 11, 700))
    cap = "The mashup section has the most elements playing, so it is the biggest part."
    out.append(D.t_(gx + pw / 2, yb + 82, cap, lf, 500))
    D.lab(name + " cap", cap, lf, pw)
    return padded("".join(out), W, yb + 96, 14)


def groove_body(name="groove"):
    parts = [grid_for(g, f"{name} {g}") for g in GROOVES]
    return D.stack(parts, 14)


DRAWINGS = {"hero": hero_body, "tempo": lambda: tempo_body(1500, "tempo deck"), "circle": lambda: circle_body(1000, "circle deck"),
            "shift": lambda: shift_body(1500, "shift deck"), "map": lambda: map_body(1500, False, "map deck", 23, 44)}
DRAWING_PX = {"hero": 1340, "tempo": 2000, "circle": 1400, "shift": 2000, "map": 2000}
SIDE = {"tempo": ["Both songs move to the same tempo", "The percent change shows how far each moves"],
        "shift": ["The key-matched shift has the fewest clashes", "Smooth pairs sound like they belong"]}
# extra drawings used on pages only, rendered alone on a transparent ground by --check as well
PAGE_DRAWINGS = {"jb-1": lambda: tune_roll("JB", 0, 8, 1100, "page jb 1", 15), "jb-2": lambda: tune_roll("JB", 8, 16, 1100, "page jb 2", 15),
                 "dh-1": lambda: tune_roll("DH", 0, 8, 1100, "page dh 1", 14), "dh-2": lambda: tune_roll("DH", 8, 16, 1100, "page dh 2", 14),
                 "circle-page": lambda: circle_body(1000, "circle page"), "tempo-page": lambda: tempo_body(1500, "tempo page"),
                 "shift-page": lambda: shift_body(1500, "shift page"), "groove-page": lambda: groove_body("groove page"),
                 "map-page": lambda: map_body(1250, False, "map page", 22, 40, 19, 20, 292), "exmap-page": lambda: map_body(1100, True, "exmap page", 21, 36, 18, 19, 268)}


def label_extras():
    for fn in PAGE_DRAWINGS.values():
        fn()



# ================================================================ intro deck: (class, kind, title, body, speaker notes)
SLIDES = [
    (1, "title", "Holiday Mashup", "Two carols, one tempo, one key",
     "Class 1, the first minute. No audio is included in this deck. Open with the idea: you will make a DJ-style mashup of two public-domain carols, Jingle Bells and Deck the Halls, in Logic Pro. "
     "Played side by side the two songs do not fit: they run at different speeds and sit in different keys. The project is the arithmetic and the listening that fix both. Nobody needs to compose a melody, "
     "and the songs’ words are not used."),
    (1, "listen", "Do these two songs fit?", "Think, then share|Teacher: hum the first phrase of each carol, one after the other, with no audio. Are they the same speed?|"
     "Which carol feels faster, and by how much?|If two songs are in different keys, what do you hear?|What could you change so that they fit?",
     "Read the scene aloud, or hum the first phrase of each carol yourself; nothing is played from a speaker. Take a few answers to each question and write the words on the board. Students will say that one feels "
     "faster, that the notes clash and that you could change the speed or move the notes up or down. The project turns each of those ideas into a tool: a ratio and a percent for the speed, a semitone count for the key."),
    (1, "bullets", "What is the Holiday Mashup project?", "Match the tempo of two public-domain carols|Match their keys with the shortest transposition|"
     "Enter both melodies and layer them over one groove|Arrange 44 bars and check the match with Flex",
     "The project in four lines. Every student takes Jingle Bells and Deck the Halls, works out a target tempo and each song’s percent change, and finds the shortest move between the two keys. They enter both melodies "
     "from note charts, check the match with Smart Tempo and Flex if their version has them, layer the melodies over one groove, and arrange 44 bars in six sections. The songs’ words are not printed."),
    (1, "days", "Three classes", "",
     "The shape of the project. Class 1: the think-and-share, the tempo ratio, seconds per bar and the key shift. Class 2: finish the melodies, check with Smart Tempo and Flex, layer the melodies and build the groove. "
     "Class 3: arrange the six sections, mix, bounce, present and reflect. The badge on this slide reads Classes 1 to 3 because it covers all three. With two classes, do the tempo, key and melodies in Class 1 and "
     "everything else in Class 2; with four, add a day for the arrangement and the mix. Hand out the tempo page, the key page and the note charts now."),
    (1, "pic", "Match the tempo", "tempo",
     f"Class 1. Deck the Halls is notated at 96 BPM and Jingle Bells at 120, a ratio of 5 to 4. Neither is half or double the other, so one or both must change. The mean, 108 BPM, is a fair target: Jingle Bells slows by "
     f"10 percent and Deck the Halls speeds up by 12.5 percent. The formula is (target ÷ original − 1) × 100. At 108 BPM one bar lasts 240 ÷ 108 = 2.222 seconds. The tempo page is page {pg('tempo')}; "
     f"students fill in their own numbers there."),
    (1, "bullets", "Bars, beats and seconds", "Seconds per beat = 60 ÷ BPM|Seconds per bar in 4/4 = 240 ÷ BPM|Percent change = (target ÷ original − 1) × 100|At 108 BPM, 44 bars last 97.78 seconds",
     f"Class 1, the formulas. A beat lasts 60 ÷ BPM seconds and a 4/4 bar has four beats, so a bar lasts 240 ÷ BPM. A 3/4 bar would last 180 ÷ BPM and a 2/4 bar 120 ÷ BPM. Percent change is positive when a song speeds up "
     f"and negative when it slows down. Check one example together on the board: at 120 BPM a bar lasts 2 seconds, at 96 BPM it lasts 2.5, and at 108 it lasts 2.222. All of this is on page {pg('tempo')}."),
    (1, "pic", "Match the key", "circle",
     f"Class 1. The circle of fifths shows how closely related two keys are. Jingle Bells is usually printed in G major and Deck the Halls in F major, which are two steps apart on the circle. In semitones, G down to F is 2 "
     f"and G up to F is 10, so the shorter move is 2 down, and the rule is: never move more than 6 semitones. Relative minors sit inside the circle: E minor for G and D minor for F. The steps on the circle and the semitones "
     f"are different counts; the key page, page {pg('keys')}, gives both."),
    (2, "pic", "Layer them: the clash check", "shift",
     f"Class 2. This chart tests the idea. For every shift of Jingle Bells from 6 down to 5 up, it layers the chorus over Deck the Halls and counts how the two melody notes sound together on every beat: smooth pairs "
     f"such as thirds and fifths, mild pairs such as whole steps, and hard clashes such as half steps and tritones. The shift that matches the keys, 2 down, has the fewest hard clashes. This is a quick check on the beats, "
     f"not a rule of harmony. The check and the suggested chords are on page {pg('layer')}."),
    (2, "bullets", "Smart Tempo and Flex, if you have them", "Smart Tempo finds a recording’s tempo|Flex Time stretches audio to follow the tempo|Flex Pitch fixes pitch without changing length|Look in the region or track inspector",
     f"Class 2. These tools are for audio, and each is available only if your version of Logic Pro has it. Smart Tempo analyzes a recording and tells you its tempo. Flex Time stretches an audio region so that it follows "
     f"a new tempo without changing its pitch. Flex Pitch edits the pitch of a single-line recording without changing its length. Do not invent menu paths: say that the settings are in the region or track inspector "
     f"and let students find them. The numbers to expect are on page {pg('flex')}."),
    (2, "steps", "Build it in Logic", "Set the project tempo to your target; keep 4/4|Enter both melodies in the Piano Roll, in your key|Bounce one melody and try Flex Time, if you have it|"
     "Add chords, then drums and bass from a groove card|Layer the two melodies and listen for clashes",
     f"Class 2. Demonstrate on the projector. Set the project tempo to the target and keep 4/4. Enter each melody on its own track in the Piano Roll, remembering that Logic calls middle C C3 where the chart says C4. "
     f"Bounce one melody to audio and try Flex Time on it if the version has it. Then add chords, drums and bass, and layer the melodies. Menu names move between Logic versions; the quick reference on page {pg('logicref')} "
     f"hedges where they do."),
    (3, "pic", "Arrange 44 bars in six sections", "map",
     f"Class 3. This is the arrangement map: seven elements down the side and six sections across, an intro of 4 bars, Jingle Bells 8, a bridge of 4, Deck the Halls 8, the mashup 16 and an outro of 4. "
     f"A shaded cell means the element plays in that section. The elements playing in each section are 2, 4, 5, 4, 6 and 3, so the mashup is the biggest. At 108 BPM one bar lasts 2.222 seconds and the track lasts 97.78 seconds. "
     f"The map is on page {pg('map')} and the tempo page on page {pg('tempo')}."),
    (3, "check", "What you turn in", "Bounced .mp3 or .wav, 44 bars long|Zipped .logicx project|Named: Your Name – Holiday Mashup|Tempo and key pages completed|Reflection page|Rubric self-score and three questions",
     "Class 3. The submission checklist, shortened to fit the slide. Show where students hand in. The file name is Your Name, then Holiday Mashup. Check the length before students bounce: the bounce should run the whole track, "
     "which is 44 bars, or 97.78 seconds at 108 BPM, 110 seconds at 96 BPM and 88 seconds at 120 BPM."),
    (3, "rubric", "How it’s scored", "",
     "The rubric: five categories, each scored 1 to 5, for a total out of 25. Students score themselves first; the final grade is the average of their score and yours. "
     "The slide reads the 5 column of each category aloud. Hand out the rubric page so students can self-score before they present."),
    (3, "bullets", "Presentation day", "Play your track from the top|Say your target tempo and your key|Explain one percent change or one shift|Answer at least 2 of each classmate’s questions",
     "Class 3, presentations. Each student plays the track from the top and names the target tempo and the key. Then each student explains one calculation, either a percent change or a key shift, and says why they chose it. "
     "Students write three questions they want classmates to answer, and answer at least two of each classmate's. Ask the class to say which carol had to change more."),
    (3, "closer", "One last thing…", "Match the speed.|Match the key.|Layer the tunes.|Make two songs one.",
     "Close with the listening day: play a track and ask the class which carol changed more and whether they can hear where the two melodies meet. A mashup is arithmetic and listening together. "
     "Ask a few students what they would change next time. No audio is included in this resource; the sounds are the students' own."),
]
SHOTS1 = [("pacing", "Pacing guide", "3 class periods, slide by slide"), ("tempo", "Tempo page", "Ratio, target tempo, percent change"),
          ("keys", "Key page", "Semitones and the circle of fifths")]
SHOTS2 = [1, 5, 7, 8, 11, 13]
SHOTS3 = [("tempo", "Tempo page"), ("keys", "Key page"), ("chart1", "Note chart"), ("layer", "Clash check"), ("flex", "Smart Tempo and Flex"), ("map", "Arrangement map"),
          ("example", "Worked example"), ("rubric", "Rubric")]
PREVIEW_PICKS = ["pacing", "tempo", "keys", "rubric"]

COVER_A = "Match two carols’ tempo and key"
COVER_C = "Logic Pro · Smart Tempo and Flex · Tempo and key pages"
PDF_COVER = dict(a=26, b=38, c=15, art=5.0)
SQ_COVER = dict(a=36, b=134, c=27, art=400, gap=20)
SQ_B_LINES = ["Holiday", "Mashup"]
SQ_SUB = "3 class periods · two public-domain carols · intro slides"
SQ_HEADS = {1: ("Ready to teach Monday", 76, "Pacing, tempo and key pages, note charts and the /25 rubric in one PDF", 28),
            2: ("Intro deck included", 76, f"{len(SLIDES)} editable slides (.pptx + PDF) with speaker notes on every slide", 28),
            3: ("Everything inside", 72, "Tempo and key math, clash check, grooves, map and worked example", 28)}
SQ_BANDS = {1: "Tempo <em>·</em> key <em>·</em> melodies <em>·</em> arrangement",
            2: "Tempo page <em>·</em> key page <em>·</em> clash check",
            3: f"{len(PLAN)} pages <em>·</em> US Letter PDF <em>·</em> no audio included"}


# ================================================================ small page helpers
CSS_SG = ("<style>table.sg { border-collapse: collapse; width: 100%; table-layout: fixed; } table.sg td, table.sg th { border: 1pt solid #000; text-align: center; "
          "padding: 0; font-size: 8.6pt; } table.sg th { background: #000; color: #fff; font-family: Oswald; font-weight: 500; height: 14pt; } "
          "table.sg td.l { text-align: left; padding: 0 4pt; font-weight: 700; width: 1.45in; font-size: 8.8pt; } "
          "table.sg td.g { background: #e4e4e4; } </style>")
CSS_CC = ("<style>table.cc td { text-align: center; padding: 2pt 3pt; font-size: 9.4pt; line-height: 1.15; } table.cc th { text-align: center; font-size: 9pt; } "
          "table.cc td.lt { text-align: left; } table.cc tr.hi td { background: #eef5fb; }</style>")



def howto_page(n, wm=False):
    parts = [("Teacher pages", "howto", "example2", "How to use, overview, setup, pacing, teacher notes, Logic quick reference, worked example (2 pages)"),
             ("Student pages", "tempo", "reflect", "Tempo and key pages, note charts, Smart Tempo and Flex, clash check, groove cards, arrangement map, mix checklist, "
              "project sheet (3 pages), rubric, vocabulary, planner, reflection"),
             ("Intro deck (separate file)", None, None, f"{len(SLIDES)} slides, .pptx + PDF, speaker notes on every slide")]
    trs = "".join(f"<tr><td><b>{a}</b></td><td style='white-space:nowrap'>{('pages ' + str(D.IX(f)) + '–' + str(D.IX(l))) if f else 'deck'}</td>"
                  f"<td>{u}</td></tr>" for a, f, l, u in parts)
    inner = (f'<div class="cols"><div>'
             f'{D.H2("What this is", True)}'
             f'<p style="font-size:11.4pt;line-height:1.42">A {CLASSES}-class-period mashup project for high school music technology. Every '
             f'student makes a DJ-style mashup of two public-domain carols, “Jingle Bells” and “Deck the Halls”, in Logic Pro: they match the tempo and the key with ratios, percents and semitones, '
             f'enter both melodies from a note chart, check the match with Smart Tempo and Flex if their version has them, layer the melodies over one groove, arrange 44 bars, mix, present and reflect. '
             f'It is an original Hudson Beat project, and both melodies are in the public domain.</p>'
             f'{D.H2("Quick start")}<ol>'
             f'<li style="margin-bottom:5pt">Read the pacing guide (page {D.IX("pacing")}) and the teacher notes (pages {D.IX("tn1")}–{D.IX("tn2")}).</li>'
             f'<li style="margin-bottom:5pt">Look at the tempo page, the key page and the note charts (pages {D.IX("tempo")}–{D.IX("chart2")}) and the setup (page {D.IX("setup")}).</li>'
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
             f'<li><b>Pace:</b> Class 1 is the tempo and the key, Class 2 the melodies, the check and the layering, Class 3 the arrangement and presentations (page {D.IX("pacing")}, which also shows two and four periods).</li>'
             f'<li><b>Grading:</b> the rubric, /{RUBRIC_TOTAL}, the average of the student’s and your score (page {D.IX("rubric")}).</li></ul>'
             f'<div class="box" style="margin-top:6pt"><span class="k">In one sentence</span><p style="margin:0;font-size:11pt">Students learn that '
             f'two songs fit together only when they share a tempo and a key, and that both are matched with arithmetic: a ratio and a percent for the speed, a count of semitones for the key.</p></div>'
             f'<p class="small" style="margin-top:6pt">Logic Pro is a product of Apple Inc. This resource is not affiliated with Apple.</p>'
             f'</div></div>')
    return D.page("How to use this resource", "START HERE", "Teacher", inner, n, key="howto")


def facts_rows():
    rows = [("Tune and year", "James Lord Pierpont, published September 16, 1857; the familiar chorus is documented by 1898",
             "A Welsh melody, commonly dated to the sixteenth century; the English words are from 1862"),
            ("Notated in", "G major in the 4/4 edition charted here; an adaptation of the 1857 edition is in A-flat major and 2/4 (two bars of 2/4 make one of 4/4)",
             "F major in two of the three editions compared; the third is in E-flat major"),
            ("Tempo marks in the files read", ", ".join(str(t) for t in TEMPO_MARKS["Jingle Bells"][:-1]) + " and " + str(TEMPO_MARKS["Jingle Bells"][-1]) + " BPM",
             ", ".join(str(t) for t in TEMPO_MARKS["Deck the Halls"][:-1]) + " and " + str(TEMPO_MARKS["Deck the Halls"][-1]) + " BPM"),
            ("Typical class tempo", f"<b>{A_BPM} BPM</b>", f"<b>{B_BPM} BPM</b>"),
            ("Charted here", "16 bars of 4/4: the verse (bars 1–8) and the chorus (bars 9–16)", "16 bars of 4/4: the whole tune")]
    return "".join(f"<tr><td><b>{a}</b></td><td>{b}</td><td>{c}</td></tr>" for a, b, c in rows)


def overview_page(n, wm=False):
    inner = (f'<div class="cols"><div>'
             f'<div class="box inv" style="margin-bottom:6pt"><span class="k">The project in one line</span><p style="margin:0;font-size:12pt">'
             f'<b>{TITLE}</b> · Mashup · Logic Pro<br>Two carols, one tempo, one key.</p></div>'
             f'{D.H2("What students make")}'
             f'<p style="font-size:10.4pt;line-height:1.36">A 44-bar track in Logic Pro: a 4-bar intro, the chorus of “Jingle Bells”, a 4-bar bridge, eight bars of “Deck the Halls”, a 16-bar mashup with both melodies layered over one groove and a 4-bar outro. '
             f'Both melodies are entered from the note charts in the same key and at the same tempo. Students work out the tempo ratio, a target tempo and each song’s percent change, find the shortest key shift, '
             f'check the match with Smart Tempo and Flex if their version has them, and hand in a bounced file and the zipped .logicx project, plus their tempo and key pages and a reflection, then play the track and take questions.</p>'
             f'{D.H2("Standards")}<p style="font-size:11pt">Supports the National Core Arts Standards for Music (Music Technology, high school): generating '
             f'and developing ideas (MU:Cr1.1, MU:Cr2.1), presenting work (MU:Pr6.1) and responding to it (MU:Re7.2).</p>'
             f'</div><div>'
             f'{D.H2("Goals", True)}<ul>' + "".join(f"<li style='font-size:10.6pt;line-height:1.36'>{g}</li>" for g in GOALS) + '</ul>'
             f'<div class="box" style="margin-top:4pt;padding:5pt 9pt"><span class="k">At a glance</span><p style="margin:0;font-size:10pt;line-height:1.36"><b>Grades</b> {GRADES_TEXT}, music technology or music production · '
             f'<b>Length</b> {CLASSES} class periods (two and four also shown) · <b>Software</b> Logic Pro · <b>You supply</b> Macs with Logic Pro, headphones and a place to hand in files · '
             f'<b>Assessment</b> rubric, 5 categories scored 1–5, /{RUBRIC_TOTAL} (page {D.IX("rubric")})</p></div>'
             f'</div></div>'
             f'{D.H2("About the two carols")}<div class="box acc-b" style="padding:4pt 9pt"><p style="margin:0 0 2pt;font-size:9.6pt;line-height:1.3">A DJ-style mashup plays two songs together, and it works only when they share a tempo and a key. {SOURCE_NOTE}</p></div>'
             f'<style>table.fa td, table.fa th {{ padding: 2pt 5pt; font-size: 9pt; }}</style>'
             f'<table class="t fa" style="margin-top:5pt"><tr><th style="width:19%"></th><th>Jingle Bells</th><th>Deck the Halls</th></tr>{facts_rows()}</table>'
             f'<p class="small" style="margin:0;font-size:8.6pt">Published editions disagree about tempo and sometimes about key, so the “typical class tempo” is a class choice inside the range of the marks in the files read, not a fact about the song.</p>')
    return D.page("Project overview", "OVERVIEW", "Mashup project", inner, n, key="overview")


def setup_page(n, wm=False):
    inner = (f'<style>.sb p, .sb li {{ font-size: 11.6pt; line-height: 1.44; margin-bottom: 5pt; }}</style><div class="cols"><div class="big sb">'
             f'{D.H2("You need", True)}<ul>'
             f'<li><b>A Mac with Logic Pro</b> for each student, and <b>headphones</b>.</li>'
             f'<li><b>A place to hand in</b> the .mp3 or .wav files, the zipped .logicx and the reflection.</li>'
             f'<li><b>The tempo page, key page and note charts</b>, printed (pages {D.IX("tempo")}–{D.IX("chart2")}), or shown on the projector.</li>'
             f'<li><b>Printed student pages</b>, one set each (pages {D.IX("tempo")}–{D.IX("reflect")}).</li>'
             f'<li><b>A MIDI keyboard</b> is optional: the notes can be drawn in the Piano Roll. Nobody has to read music, only the note chart.</li></ul>'
             f'{D.H2("Before Class 1")}'
             + "".join(D.chk(c, 13, "font-size:11.6pt;margin-bottom:7pt") for c in [
                 f"Read the note charts (pages {D.IX('chart1')}–{D.IX('chart2')}) and enter the first four bars of one melody in Logic so you know how long it takes.",
                 f"Open Logic Pro on a student computer and check which tools your version has: Smart Tempo, Flex Time, Flex Pitch, Alchemy, Drum Machine Designer, Session Players (see page {D.IX('logicref')}).",
                 f"Check that you can add a marker and change the project tempo.",
                 f"Read the worked example (pages {D.IX('example')}–{D.IX('example2')})."]) +
             f'</div><div class="big sb">'
             f'{D.H2("What to watch", True)}'
             f'<p style="font-size:11.4pt">Watch for percent changes with the wrong sign, key shifts that go the long way round, melodies entered an octave off, a Flex stretch that is too big and two melodies that are still in different keys when they are layered. {TN_NOTE}</p>'
             f'<div class="box acc-b" style="margin-top:2pt"><span class="k">Ideas for the room</span><ul style="margin:0">'
             f'<li style="font-size:11.2pt">Ask while students work: which carol changed more, and by what percent? Which way did you move the key?</li>'
             f'<li style="font-size:11.2pt">Say the theme plainly: two songs fit together when they share a tempo and a key, and both can be matched with arithmetic.</li>'
             f'<li style="font-size:11.2pt">A student who is stuck can use the mean tempo and the key of F, as in the worked example: that already works.</li></ul></div>'
             f'{D.H2("The tunes")}'
             f'<div class="box"><p style="margin:0;font-size:10.8pt;line-height:1.4">Both tunes are in the public domain. The words are not printed, so students work from the melodies alone. '
             f'If a student wants to use another carol, check its first publication date: in 2026 it must be 1930 or earlier.</p></div>'
             f'<div class="box" style="margin-top:6pt"><span class="k">Keep the volume moderate</span><p style="margin:0;font-size:11pt;line-height:1.4">'
             f'Two melodies layered over a groove can be tiring in headphones. Tell students to start low and check the final mix at a normal level.</p></div>'
             f'</div></div>')
    return D.page("Setup and what to watch", "SETUP", "Teacher", inner, n, key="setup")



# ================================================================ the tempo page, key page, note charts, Smart Tempo and Flex page, clash check, groove cards, map and mix pages
def tempo_target_rows():
    rows = ""
    for label, t in (("Jingle Bells’ tempo", A_BPM), ("Deck the Halls’ tempo", B_BPM), ("The mean of the two", int(TARGET))):
        hi = ' class="hi"' if t == TARGET else ""
        rows += (f"<tr{hi}><td class='lt'>{label}</td><td><b>{t}</b></td><td>{pct_text(pct(A_BPM, t))}</td><td>{pct_text(pct(B_BPM, t))}</td>"
                 f"<td>{dshort(bar_len(t), 3)}</td><td>{dec(total_s(t), 2)}</td></tr>")
    return rows


def pair_rows():
    rows = ""
    for a, b in PAIRS:
        n_, d_ = ratio(a, b)
        mean = Fraction(a + b, 2)
        rows += (f"<tr><td><b>{a} and {b}</b></td><td>{n_} : {d_}</td><td class='lt'>{pair_meaning(a, b).split(', ', 1)[1]}</td><td>{dshort(mean, 2)}</td>"
                 f"<td>{pct_text(pct(a, mean))} · {pct_text(pct(b, mean))}</td></tr>")
    return rows


def tempo_page(n, wm=False):
    inner = (CSS_CC +
             f'<p style="margin:0 0 4pt;font-size:10pt;line-height:1.34">Step 1: match the tempo. Published editions mark very different tempos (Jingle Bells {TEMPO_MARKS["Jingle Bells"][0]} to {TEMPO_MARKS["Jingle Bells"][-1]} BPM and Deck the Halls '
             f'{TEMPO_MARKS["Deck the Halls"][0]} to {TEMPO_MARKS["Deck the Halls"][-1]} BPM in the files read), so this page uses a <b>typical class tempo</b> for each: {A_BPM} BPM for Jingle Bells and {B_BPM} BPM for Deck the Halls. '
             f'Both charts are in 4/4. Every number below is computed, so you can check your own arithmetic against it.</p>'
             f'<div class="cols" style="gap:10pt;align-items:flex-start"><div class="box acc-b" style="padding:4pt 9pt;flex:1.25"><span class="k">The formulas</span>'
             f'<p style="margin:0 0 1pt;font-size:9.2pt;line-height:1.28"><b>Seconds per beat</b> = 60 ÷ BPM · <b>Seconds per bar</b> in 4/4 = 240 ÷ BPM (3/4: 180 ÷ BPM; 2/4: 120 ÷ BPM)</p>'
             f'<p style="margin:0 0 1pt;font-size:9.2pt;line-height:1.28"><b>Ratio</b> = faster ÷ slower, reduced: {A_BPM} ÷ {B_BPM} = 5 ÷ 4. A 2 : 1 ratio is <b>double-time</b> or <b>half-time</b>.</p>'
             f'<p style="margin:0 0 1pt;font-size:9.2pt;line-height:1.28"><b>Percent speed change</b> = (target ÷ original − 1) × 100. Positive: speed up. Negative: slow down.</p>'
             f'<p style="margin:0;font-size:9.2pt;line-height:1.28"><b>Target</b>: one song’s tempo, or the mean. <b>Track</b> = 44 bars × seconds per bar.</p></div>'
             f'<div class="box" style="padding:4pt 9pt;flex:1"><span class="k">Rounding</span><p style="margin:0;font-size:9.2pt;line-height:1.28">Seconds per bar to 3 decimals (240 ÷ 108 = 2.222) and the track to 2 (97.78); '
             f'a 5 rounds up. Percents are exact or to 2 decimals. Both carols have the same tempo after the match, so they share one bar length.</p></div></div>'
             f'<div style="width:6.6in;margin:3pt auto 0">{D.body_svg(PAGE_DRAWINGS["tempo-page"]())}</div>'
             f'<span class="k" style="margin-top:3pt">Choose a target: three choices for Jingle Bells and Deck the Halls (shaded row: the worked example)</span>'
             f'<table class="t cc" style="margin-top:1pt"><tr><th>Target is</th><th>Target BPM</th><th>Jingle Bells change</th><th>Deck the Halls change</th><th>Seconds per bar</th><th>44-bar track (s)</th></tr>{tempo_target_rows()}</table>'
             f'<span class="k" style="margin-top:2pt">More pairs: what the ratio tells you</span>'
             f'<table class="t cc" style="margin-top:1pt"><tr><th>Tempos</th><th>Ratio</th><th>What it means</th><th>Mean</th><th>Change to the mean (first · second)</th></tr>{pair_rows()}</table>'
             f'<div class="box acc-b" style="padding:4pt 9pt;margin-top:3pt"><span class="k">My tempos</span>'
             f'<div class="fl" style="margin:2pt 0 3pt;font-size:9.8pt"><b>Carol A:</b><span></span><b>BPM · Carol B:</b><span></span><b>BPM · Ratio:</b><span></span><b>: </b><span></span><b>Target:</b><span></span><b>BPM</b></div>'
             f'<div class="fl" style="margin:0 0 3pt;font-size:9.8pt"><b>Change A = (</b><span></span><b>÷</b><span></span><b>− 1) × 100 =</b><span></span><b>% · Change B =</b><span></span><b>%</b></div>'
             f'<div class="fl" style="margin:0;font-size:9.8pt"><b>One bar = 240 ÷</b><span></span><b>=</b><span></span><b>s · Track = 44 ×</b><span></span><b>=</b><span></span><b>s</b></div></div>')
    return D.page("Tempo page", "STUDENT", "Class 1", inner, n, wm, name=True, key="tempo")


def key_pair_rows():
    rows = ""
    for a, b, note in KEY_PAIRS:
        up = up_semis(a, b)
        down = (12 - up) % 12
        sh = short_shift(a, b)
        shift_txt = "±6 (a tie)" if up == 6 else signed(sh)
        rows += (f"<tr><td><b>{a} to {b}</b></td><td>{up}</td><td>{down}</td><td><b>{shift_txt}</b></td><td>{fifths_apart(a, b)}</td><td class='lt'>{note}</td></tr>")
    return rows


TARGET_OPTIONS = [("F", "Deck the Halls stays put"), ("G", "Jingle Bells stays put"), ("F#", "meet in the middle")]


def key_option_rows():
    rows = ""
    for t, why in TARGET_OPTIONS:
        sj, sd = short_shift(KEY_JB, t), short_shift(KEY_DH, t)
        hi = ' class="hi"' if t == TARGET_KEY else ""
        sig = sig_of(KEY_PC[t])
        rows += (f"<tr{hi}><td><b>{t} major</b></td><td>{signed(sj)}</td><td>{signed(sd)}</td><td>{abs(sj) + abs(sd)}</td><td>{MINOR_OF[t]} minor</td><td>{sig}</td><td class='lt'>{why}</td></tr>")
    return rows


def keys_page(n, wm=False):
    inner = (CSS_CC +
             f'<p style="margin:0 0 4pt;font-size:10pt;line-height:1.34">Step 2: match the key. The 4/4 edition of Jingle Bells charted here is in <b>G major</b> and Deck the Halls is in <b>F major</b> in two of the three editions compared '
             f'(an adaptation of the 1857 edition of Jingle Bells is in A-flat major, and one Deck the Halls edition is in E-flat major, so check the key of any score you use). '
             f'To layer the songs, move one or both so that they share a key. <b>#</b> means sharp and <b>b</b> means flat.</p>'
             f'<div class="cols" style="gap:12pt;align-items:flex-start"><div style="flex:0 0 3.0in">{D.body_svg(PAGE_DRAWINGS["circle-page"]())}</div>'
             f'<div><div class="box acc-b" style="padding:4pt 9pt;margin-bottom:4pt"><span class="k">The rules</span>'
             f'<p style="margin:0 0 2pt;font-size:9.2pt;line-height:1.28"><b>Semitones up</b> from key A to key B = (B − A) mod 12, counting each key as a number of semitones above C (C = 0, C# = 1 … B = 11).</p>'
             f'<p style="margin:0 0 2pt;font-size:9.2pt;line-height:1.28"><b>Shorter move:</b> if the count up is more than 6, subtract 12 (10 up is 2 down). Never move more than 6 semitones. A count of exactly 6 is a tie.</p>'
             f'<p style="margin:0 0 2pt;font-size:9.2pt;line-height:1.28"><b>The circle</b> counts how related two keys are: each step clockwise adds a sharp (G has 1, D has 2) and each step counterclockwise adds a flat (F has 1, Bb has 2). It is a different count from the semitones.</p>'
             f'<p style="margin:0;font-size:9.2pt;line-height:1.28"><b>Relative minor</b> = 3 semitones below the major key: G major and E minor share a key signature, and so do F major and D minor.</p></div>'
             f'<div class="box" style="padding:4pt 9pt"><span class="k">The arc on the circle</span><p style="margin:0;font-size:9.2pt;line-height:1.28">G and F are two steps apart on the circle, through C. '
             f'Two steps down is G to C to F, and it is also 2 semitones down from G to F.</p></div></div></div>'
             f'<span class="k" style="margin-top:3pt">Six key pairs: both ways round, and the shorter move</span>'
             f'<table class="t cc" style="margin-top:1pt"><tr><th>From to</th><th>Semitones up</th><th>Semitones down</th><th>Shorter move</th><th>Steps on the circle</th><th>Note</th></tr>{key_pair_rows()}</table>'
             f'<span class="k" style="margin-top:3pt">Choose a target key: three choices for the two carols (shaded row: the worked example)</span>'
             f'<table class="t cc" style="margin-top:1pt"><tr><th>Target key</th><th>Jingle Bells moves</th><th>Deck the Halls moves</th><th>Semitones moved in all</th><th>Relative minor</th><th>Key signature</th><th>Why</th></tr>{key_option_rows()}</table>'
             f'<p class="small" style="margin:0 0 3pt;font-size:8.6pt">Every choice moves the two songs 2 semitones closer in all, and the gap between the songs is the same. A target of F or G is easiest to read; F# is fine in a Piano Roll. '
             f'Go to page {pg("chart1")} and page {pg("chart2")} for the notes in the key you choose.</p>'
             f'<div class="box acc-b" style="padding:4pt 9pt"><span class="k">My keys</span>'
             f'<div class="fl" style="margin:2pt 0 3pt;font-size:9.8pt"><b>Carol A is in</b><span></span><b>· Carol B is in</b><span></span><b>· Semitones up</b><span></span><b>· Shorter move</b><span></span></div>'
             f'<div class="fl" style="margin:0;font-size:9.8pt"><b>My target key:</b><span></span><b>· Carol A new key:</b><span></span><b>· Carol B new key:</b><span></span><b>· Relative minor:</b><span></span></div></div>')
    return D.page("Key page", "STUDENT", "Class 1", inner, n, wm, name=True, key="keys")


def chart_table(which, a, b):
    """Bar rows a..b (1-based) of a chart: the notated key and the other key."""
    if which == "JB":
        base, bkey, other, okey, shift = CHART_JB_G, KEY_JB, moved(CHART_JB_G, -2, "F"), "F", -2
    else:
        base, bkey, other, okey, shift = CHART_DH_F, KEY_DH, moved(CHART_DH_F, 2, "G"), "G", 2
    rows = ""
    for i in range(a, b + 1):
        rows += f"<tr><td style='width:6%'><b>{i}</b></td><td>{bar_text(base[i - 1])}</td><td>{bar_text(other[i - 1])}</td></tr>"
    return (f'<style>table.tt td, table.tt th {{ padding: 1.1pt 5pt; }}</style><table class="t tt" style="font-size:8.1pt;line-height:1.12;margin:2pt 0 2pt">'
            f'<tr><th>Bar</th><th>{bkey} major (as notated)</th><th>{okey} major (moved {signed(shift)})</th></tr>{rows}</table>')


def roll_html(names):
    return "".join(f'<div style="margin:0 0 2pt">{D.body_svg(PAGE_DRAWINGS[k]())}</div>' for k in names)


def chart1_page(n, wm=False):
    inner = (f'<p style="margin:0 0 3pt;font-size:10pt;line-height:1.32"><b>Jingle Bells</b> · James Lord Pierpont, published 1857 · a public-domain tune · 4/4 · 16 bars: the verse (bars 1–8) and the chorus (bars 9–16) · '
             f'{len(JB_NOTES)} notes · the roll shows G major, the key of the 4/4 edition</p>'
             + roll_html(["jb-1", "jb-2"]) + chart_table("JB", 1, 16) +
             f'<div class="box acc-b" style="margin-top:2pt;padding:3pt 10pt"><span class="k">About this chart</span><p style="margin:0;font-size:8.8pt;line-height:1.26">'
             f'Step 3: enter the melodies. Use the G major column for a target of G and the F major column for a target of F; the F column is the G notes moved 2 semitones down. Pitch names run down the left; middle C is C4 here, '
             f'but Logic calls it C3, so subtract one from the octave number. Lengths: s = 16th, e = eighth, de = dotted eighth, q = quarter, dq = dotted quarter, h = half. Bold lines are bars and gray lines are beats. '
             f'The chart leaves out the two D5 “pickup” notes that some editions add: one at the end of the verse and one in the middle of the chorus.</p></div>')
    return D.page("Note chart · Jingle Bells", "STUDENT", "Classes 1–2", inner, n, wm, name=True, key="chart1")


def chart2_page(n, wm=False):
    inner = (f'<p style="margin:0 0 3pt;font-size:10pt;line-height:1.32"><b>Deck the Halls</b> · a Welsh melody, a public-domain tune · 4/4 · 16 bars · {len(DH_NOTES)} notes · '
             f'the roll shows F major, the key of two of the three editions compared</p>'
             + roll_html(["dh-1", "dh-2"]) + chart_table("DH", 1, 16) +
             f'<div class="box acc-b" style="margin-top:2pt;padding:3pt 10pt"><span class="k">About this chart</span><p style="margin:0;font-size:8.8pt;line-height:1.26">'
             f'Step 3: enter the melodies. Use the F major column for a target of F and the G major column for a target of G (the F notes moved 2 semitones up). '
             f'Bars 5–8 repeat bars 1–4, and bars 13 and 14 repeat bars 1 and 2, so you can copy a region. B natural in bar 11 is a passing note that leads up to C.</p></div>'
             f'<div class="box" style="margin-top:3pt;padding:3pt 10pt"><span class="k">Where the notes come from</span><p style="margin:0;font-size:8.2pt;line-height:1.22">'
             f'Compared note by note with scores on the Choral Public Domain Library (CPDL). Jingle Bells: nos. 38153 (4/4, G major) and 66808 (2/4, A-flat major, from the 1857 edition) agree on every pitch except lyric pickups '
             f'and re-struck held notes, and the chart leaves out two pickups. Deck the Halls: nos. 47663 and 502 (F major) and 39398 (E-flat major) agree on every note (no. 502 leaves bar 1 empty). '
             f'Only the public-domain notes are printed.</p></div>')
    return D.page("Note chart · Deck the Halls", "STUDENT", "Classes 1–2", inner, n, wm, name=True, key="chart2")


def flex_rows():
    rows = ""
    for t in (A_BPM, int(TARGET), B_BPM):
        for nm_, o in ((A_NAME, A_BPM), (B_NAME, B_BPM)):
            hi = ' class="hi"' if t == TARGET else ""
            rows += (f"<tr{hi}><td class='lt' style='white-space:nowrap'>{nm_}</td><td>{o}</td><td><b>{t}</b></td><td>{pct_text(pct(o, t))}</td><td>{pct_text(length_change(o, t))}</td>"
                     f"<td>{dec(8 * bar_len(o), 2)}</td><td>{dec(8 * bar_len(t), 2)}</td></tr>")
    return rows


def pitch_rows():
    rows = ""
    for lbl, v in (("Jingle Bells sped by 108 ÷ 120 = 0.9", semis_from_speed(A_BPM, int(TARGET))), ("Deck the Halls sped by 108 ÷ 96 = 1.125", semis_from_speed(B_BPM, int(TARGET)))):
        rows += f"<tr><td class='lt'>{lbl}</td><td>12 × log2(speed) =</td><td><b>{v:+.2f}</b></td><td>{freq_ratio(v):.3f}</td></tr>".replace("-", MINUS)
    for lbl, v in (("Jingle Bells moved from G to F", -2), ("Deck the Halls moved from F to G", 2)):
        rows += f"<tr><td class='lt'>{lbl}</td><td>2 ^ (semitones ÷ 12)</td><td><b>{signed(v)}</b></td><td>{freq_ratio(v):.3f}</td></tr>"
    return rows


def flex_page(n, wm=False):
    inner = (CSS_CC +
             f'<p style="margin:0 0 4pt;font-size:10pt;line-height:1.34">Step 4: check with Smart Tempo and Flex. A MIDI melody follows the project tempo by itself, but a recording has a fixed length. '
             f'These tools are for audio, and each is there only <b>if your version has it</b>; look in the region or track inspector for the settings. <b>Smart Tempo</b> works out the tempo of a recording. '
             f'<b>Flex Time</b> stretches a recording so that it follows a new tempo without changing its pitch. <b>Flex Pitch</b> edits the pitch of a single-line recording without changing its length.</p>'
             f'<span class="k" style="margin-top:2pt">What to expect when a bounced 8-bar melody follows a new tempo (shaded rows: the worked example)</span>'
             f'<table class="t cc" style="margin-top:1pt"><tr><th>Melody</th><th>Bounced at (BPM)</th><th>New tempo (BPM)</th><th>Speed change</th><th>Audio length change</th><th>8 bars before (s)</th><th>8 bars after (s)</th></tr>{flex_rows()}</table>'
             f'<p class="small" style="margin:0 0 3pt;font-size:8.8pt">Speed and length move in opposite directions: a song that speeds up by 12.5% gets 11.11% shorter, because the length changes by (original ÷ target − 1) × 100. '
             f'At the mean tempo both 8-bar melodies last the same 17.78 seconds, so they end on the same bar line.</p>'
             f'<span class="k" style="margin-top:2pt">Speed and pitch: why Flex exists</span>'
             f'<table class="t cc" style="margin-top:1pt"><tr><th>Change</th><th>Rule</th><th>Semitones</th><th>Frequency ratio</th></tr>{pitch_rows()}</table>'
             f'<p class="small" style="margin:0 0 3pt;font-size:8.8pt">Speeding up a recording with no stretch raises its pitch too. Moving to the mean tempo this way would push Jingle Bells down by {abs(semis_from_speed(A_BPM, int(TARGET))):.2f} semitones '
             f'and Deck the Halls up by {semis_from_speed(B_BPM, int(TARGET)):.2f}, which is not what either key needs. Flex Time changes the length alone and a transposition changes the pitch alone, so you can set each by its own number. '
             f'100 cents make 1 semitone.</p>'
             f'<div class="cols" style="gap:10pt;align-items:flex-start"><div class="box acc-b" style="padding:4pt 9pt"><span class="k">Try it, if your version has the tools</span>'
             + "".join(D.chk(c, 10, "font-size:9pt;line-height:1.25;margin-bottom:2pt") for c in [
                 "Enter the Jingle Bells chorus at 120 BPM and bounce it to audio (Bounce in Place or a track bounce).",
                 "Set the project tempo to 108 and turn on Flex Time for the region.",
                 "Measure the region: 8 bars should now last 17.78 s, not 16.00 s.",
                 "Let Smart Tempo analyze the audio: is the tempo close to the one you bounced at?",
                 "Repeat with Deck the Halls (bounce at 96)."]) +
             f'</div><div class="box" style="padding:4pt 9pt"><span class="k">My numbers</span>'
             f'<div class="fl" style="margin:2pt 0 3pt;font-size:9.4pt"><b>Length before:</b><span></span><b>s · after:</b><span></span><b>s</b></div>'
             f'<div class="fl" style="margin:0 0 3pt;font-size:9.4pt"><b>Smart Tempo says:</b><span></span><b>BPM</b></div>'
             f'<div class="fl" style="margin:0 0 3pt;font-size:9.4pt"><b>Flex sounded:</b><span></span></div>'
             f'<div class="fl" style="margin:0;font-size:9.4pt"><b>Half or double?</b><span></span></div></div></div>'
             f'<div class="box" style="padding:4pt 9pt;margin-top:5pt"><span class="k">If something sounds wrong</span><ul style="margin:0">'
             f'<li style="font-size:9.6pt;line-height:1.3;margin-bottom:2pt"><b>Smart Tempo says half or double.</b> That is a 2 : 1 ratio, not an error: it counted a different level of the beat.</li>'
             f'<li style="font-size:9.6pt;line-height:1.3;margin-bottom:2pt"><b>Flex Time sounds strange.</b> Try another Flex mode if your version offers one, or meet in the middle so the stretch is smaller.</li>'
             f'<li style="font-size:9.6pt;line-height:1.3;margin-bottom:0"><b>A MIDI melody needs no Flex.</b> It follows the project tempo, so use Flex only on bounced or recorded audio.</li></ul></div>')
    return D.page("Smart Tempo and Flex", "STUDENT", "Class 2", inner, n, wm, name=True, key="flex")


def mash_rows():
    rows = ""
    for m in range(1, 17):
        pas, j = (m - 1) // 8, (m - 1) % 8
        c = mash_samples(BEST_SHIFT, pas, j)
        ch, rn, fit = best_chord(m)
        rows += (f"<tr><td><b>{m}</b></td><td>{9 + j}</td><td>{pas * 8 + j + 1}</td><td>{c[SMOOTH]}</td><td>{c[MILD]}</td><td>{c[HARD]}</td>"
                 f"<td><b>{ch}</b> ({rn}) · {CHORD_G[ch]}</td><td>{fit} of 8</td></tr>")
    return rows


def layer_page(n, wm=False):
    best = shift_counts(BEST_SHIFT)
    inner = (CSS_CC +
             f'<p style="margin:0 0 3pt;font-size:9.8pt;line-height:1.32">Step 5: layer and build the groove. Layer the chorus of Jingle Bells (chart bars 9–16) over Deck the Halls twice: over bars 1–8, then over bars 9–16. '
             f'On every beat, compare the two melody notes by interval: a <b>smooth</b> pair is a unison or octave, a third or sixth, or a fourth or fifth; a <b>mild</b> pair is a whole step or a minor seventh; '
             f'a <b>hard</b> clash is a half step, a major seventh or a tritone. The chart below counts the 64 beats for each shift of Jingle Bells.</p>'
             f'<div style="width:6.9in;margin:0 auto">{D.body_svg(PAGE_DRAWINGS["shift-page"]())}</div>'
             f'<p style="margin:2pt 0 3pt;font-size:9pt;line-height:1.3">With the keys matched (a shift of {signed(BEST_SHIFT)}) the beats split {best[SMOOTH]} smooth, {best[MILD]} mild and {best[HARD]} hard, the fewest hard clashes of any shift. '
             f'Moving both carols by the same amount changes nothing: a target of G gives the same counts. This is a quick check on the beats, not a rule of harmony, so trust your ears too.</p>'
             f'<span class="k" style="margin-top:1pt">Bar by bar at the key-matched shift, with a suggested chord</span>'
             f'<style>table.mr td, table.mr th {{ padding: 1pt 3pt; }}</style>'
             f'<table class="t cc mr" style="margin-top:1pt;font-size:8.4pt;line-height:1.1"><tr><th>Mashup bar</th><th>Jingle Bells chart bar</th><th>Deck the Halls chart bar</th><th>Smooth</th><th>Mild</th><th>Hard</th><th>Chord in F · in G</th><th>Chord tones on the beat</th></tr>{mash_rows()}</table>'
             f'<p class="small" style="margin:2pt 0 0;font-size:8.4pt">Suggested chord: the triad (I, ii, iii, IV, V or vi) with the most chord tones among the 8 beat notes of the bar; ties go to I, V, IV, vi, ii, iii in that order. It is a starting point to check by ear, and you can write your own.</p>')
    return D.page("Layer the melodies · the clash check", "STUDENT", "Class 2", inner, n, wm, name=True, key="layer")


def chord_key_rows():
    rows = ""
    for nm_, rn, pcs in CHORDS_F:
        f_notes = " ".join(pcname(60 + p, "F") for p in pcs)
        g_notes = " ".join(pcname(60 + (p + 2) % 12, "G") for p in pcs)
        rows += f"<tr><td><b>{nm_}</b></td><td>{rn}</td><td>{f_notes}</td><td><b>{CHORD_G[nm_]}</b></td><td>{g_notes}</td></tr>"
    return rows


def groove_card(g):
    body, w, h = grid_for(g, cw=30)
    t1, t2, t3 = GROOVE_TEXT[g]
    txt = (f'<p style="margin:0 0 2pt;font-size:9.6pt;line-height:1.28"><b>Drums.</b> {t1}</p>'
           f'<p style="margin:0 0 2pt;font-size:9.6pt;line-height:1.28"><b>Bass and chords.</b> {t2}</p>'
           f'<p style="margin:0;font-size:9.6pt;line-height:1.28"><b>Try.</b> {t3}</p>')
    head = f'<span class="k" style="font-size:12.5pt;margin:0">{GROOVE_NAMES[g]} · {"108 BPM feels like 108" if g == "steady" else "108 BPM feels like 54"}</span>'
    return (f'<div class="box" style="margin-bottom:5pt;padding:4pt 10pt">{head}<div style="display:flex;gap:12pt;margin-top:2pt;align-items:flex-start">'
            f'<div style="flex:1">{txt}</div><div style="width:3.35in;flex:0 0 3.35in">{D.body_svg(padded(body, w, h, 8))}</div></div></div>')


def groove_page(n, wm=False):
    inner = (CSS_CC +
             f'<p style="margin:0 0 4pt;font-size:10pt;line-height:1.34">Step 5: layer and build the groove, continued. Each card is a one-bar drum pattern (16 steps, 4 to a beat; shaded steps are the beats). '
             f'Click it into a Drum Machine Designer track (or draw it in the Piano Roll with the grid on 1/16) and repeat it. Both melodies share <b>one groove</b>, so the groove is where the mashup is glued together.</p>'
             + "".join(groove_card(g) for g in GROOVES) +
             f'<div class="box acc-b" style="padding:5pt 10pt;margin-bottom:4pt"><span class="k">Half-time and double-time</span><p style="margin:0;font-size:9.8pt;line-height:1.32">'
             f'A 2 : 1 tempo ratio is a half-time or double-time match. Putting the snare on beat 3 instead of beats 2 and 4 makes a groove feel half as fast: at {EX_BPM} BPM it feels like {EX_BPM // 2} BPM, and the steady groove at {EX_BPM // 2} BPM would feel like {EX_BPM}. '
             f'This is a way to match two songs a 2 : 1 apart with no stretch at all, and a way to make the intro and the second carol feel different from the mashup.</p></div>'
             f'<span class="k" style="margin:2pt 0 1pt">The six chords the suggestions use, in F and in G (a chord in G is the chord in F moved up 2 semitones)</span>'
             f'<table class="t cc" style="margin-top:1pt"><tr><th>Chord in F</th><th>Numeral</th><th>Notes in F</th><th>Chord in G</th><th>Notes in G</th></tr>{chord_key_rows()}</table>'
             f'<div class="box" style="padding:4pt 9pt;margin-top:4pt"><span class="k">My groove and chords</span>'
             f'<div class="fl" style="margin:2pt 0 3pt;font-size:9.8pt"><b>Groove for the mashup (steady or half-time):</b><span></span></div>'
             f'<div class="fl" style="margin:0 0 3pt;font-size:9.8pt"><b>Chords, bars 1–4 of the mashup:</b><span></span></div>'
             f'<div class="fl" style="margin:0;font-size:9.8pt"><b>Chords, bars 5–8 (and again for 9–16):</b><span></span></div></div>')
    return D.page("Groove cards · half-time and chords", "STUDENT", "Class 2", inner, n, wm, name=True, key="groove")


def map_page(n, wm=False):
    bp = (B_BPM, EX_BPM, A_BPM)
    rows = ""
    for i, nm_ in enumerate(SEC_NAMES):
        rows += (f"<tr><td class='l'>{nm_}</td><td>{SEC_BARS[i]}</td><td>{start_bar(i)}–{end_bar(i)}</td>"
                 + "".join(f"<td>{dec(start_s(b, i), 2)}</td>" for b in bp) + "</tr>")
    rows += f"<tr><td class='l'>Total</td><td><b>{TOTAL_BARS}</b></td><td>1–{TOTAL_BARS}</td>" + "".join(f"<td><b>{dec(total_s(b), 2)}</b></td>" for b in bp) + "</tr>"
    mine = "".join(f"<tr><td class='l' style='height:21pt'>{nm_}</td><td></td><td></td><td></td><td></td><td></td></tr>" for nm_ in SEC_NAMES)
    inner = (CSS_SG +
             f'<p style="margin:0 0 4pt;font-size:10pt;line-height:1.34">Step 6: arrange and mix. Your track has six sections: an intro (4 bars), the Jingle Bells chorus (8), a bridge (4), eight bars of Deck the Halls (8), the mashup (16) and an outro (4), '
             f'{TOTAL_BARS} bars in all. In the bridge, trade two bars of each melody. In the mashup, layer the Jingle Bells chorus over Deck the Halls bars 1–8, then bars 9–16 (page {pg("layer")}). The map shows which elements play in each section.</p>'
             f'<div style="margin:0 0 3pt">{D.body_svg(PAGE_DRAWINGS["map-page"]())}</div>'
             f'<table class="sg" style="margin-top:3pt"><tr><th style="width:1.45in">Section</th><th>Bars</th><th>Bar numbers</th><th>Starts (s) at {bp[0]} BPM</th><th>{bp[1]} BPM</th><th>{bp[2]} BPM</th></tr>{rows}</table>'
             f'<p class="small" style="margin:2pt 0 3pt;font-size:8.6pt">The elements playing in the six sections are {", ".join(str(c) for c in ELEM_PLAYING)}, which add up to {sum(ELEM_PLAYING)}. '
             f'The mashup has the most elements, so it feels like the biggest part. Every start time is (bars gone by) × 240 ÷ BPM, rounded from its exact value.</p>'
             f'<span class="k" style="margin-top:3pt">My map: my target tempo and the numbers for each section</span>'
             f'<table class="sg" style="margin-top:2pt"><tr><th style="width:1.45in">Section</th><th>Bars</th><th>Starts at bar</th><th>Ends at bar</th><th>Starts at (s)</th><th>Lasts (s)</th></tr>{mine}</table>'
             f'<div class="fl" style="margin:4pt 0 3pt;font-size:10pt"><b>My target tempo:</b><span></span><b>My target key:</b><span></span><b>Total bars:</b><span></span></div>'
             f'<p class="small" style="margin:0;font-size:8.6pt">Check: your sections add up to 44 bars, and each start time is bars gone by × 240 ÷ BPM.</p>')
    return D.page("Arrangement map", "STUDENT", "Class 3", inner, n, wm, name=True, key="map")


def mix_page(n, wm=False):
    def box(title, items, acc=False):
        return (f'<div class="box{" acc-b" if acc else ""}" style="padding:5pt 9pt"><span class="k">{title}</span>'
                + "".join(D.chk(c, 11, "font-size:10pt;line-height:1.3;margin-bottom:3pt") for c in items) + '</div>')
    inner = (f'<p style="margin:0 0 5pt;font-size:10.2pt;line-height:1.36">Step 6: arrange and mix, continued. A mix keeps both melodies clear over the groove and makes the mashup the biggest part. Work through the boxes with headphones, '
             f'then check each one off.</p>'
             f'<div class="cols" style="gap:10pt;align-items:flex-start"><div>'
             + box("Melodies and chords", ["Each melody is the clearest part in its own section.", "In the mashup the two melodies sit in different registers (for example one an octave up) so that both can be heard.",
                                          "Both melodies are still in the same key when I play them with the final chords."], True)
             + '<div style="height:6pt"></div>'
             + box("Groove", ["The kick and the snare stand out; the hat is quiet.", "The bass plays the chord roots and does not fight the kick.",
                              "The groove changes between the half-time sections and the mashup."])
             + '</div><div>'
             + box("Arrangement", ["There is a marker at the start of each of the six sections.", "The mashup is bigger than the sections before it: more parts or a fuller groove.",
                                   "The outro takes layers away and the last chord rings out."], True)
             + '<div style="height:6pt"></div>'
             + box("Low end and levels", ["I cut the low notes from the pad and keys (Channel EQ, if I like).", "The bass and the kick do not cover each other.",
                                          "The master level never reaches red (no clipping)."])
             + '</div></div>'
             f'<div class="box" style="margin-top:6pt;padding:5pt 9pt"><span class="k">The listening test</span><p style="margin:0 0 3pt;font-size:10pt;line-height:1.36">Play from bar 25 (the start of the mashup) with your eyes closed and '
             f'rate each part from 1 (flat) to 5 (very strong). Can you hear both carols? Do they sound as if they share one key and one tempo? Is the mashup bigger than the sections before it? Write what you hear:</p>'
             f'<div class="fl" style="margin:2pt 0;font-size:10pt"><b>Both carols:</b><span></span><b>Same key and tempo:</b><span></span><b>Mashup size:</b><span></span></div></div>'
             f'<div class="box acc-b" style="margin-top:6pt;padding:5pt 9pt"><span class="k">Bounce</span>'
             + "".join(D.chk(c, 11, "font-size:10pt;margin-bottom:3pt") for c in [
                 "The bounce starts at bar 1 and ends after the last bar of the outro (44 bars: " + dec(total_s(EX_BPM), 2) + " seconds at 108 BPM; check your own tempo on page " + str(pg("tempo")) + ").",
                 "MP3 or WAV bounced, and the .logicx project zipped.", f"Both files named {FILE_NAME}."]) + '</div>'
             f'<span class="k" style="margin-top:6pt">What I changed after the listening test</span>' + D.lines(7, 24))
    return D.page("Mix checklist", "STUDENT", "Class 3", inner, n, wm, name=True, key="mix")



# ================================================================ worked example (2 pages): an invented plan at 108 BPM in F major
def ex_number_rows():
    A, B = A_BPM, B_BPM
    t = int(TARGET)
    sj, sd = short_shift(KEY_JB, TARGET_KEY), short_shift(KEY_DH, TARGET_KEY)
    rows = [("Notated key", f"{KEY_JB} major", f"{KEY_DH} major"),
            ("Typical class tempo (BPM)", str(A), str(B)),
            ("Ratio, faster ÷ slower", f"{ratio(A, B)[0]} : {ratio(A, B)[1]}", "(same pair)"),
            ("Target tempo: the mean (BPM)", str(t), str(t)),
            ("Percent speed change", pct_text(pct(A, t)), pct_text(pct(B, t))),
            ("Seconds per bar: before, after", f"{dshort(bar_len(A), 3)}, {dshort(bar_len(t), 3)}", f"{dshort(bar_len(B), 3)}, {dshort(bar_len(t), 3)}"),
            ("Bounced audio, 8 bars: before, after (s)", f"{dec(8 * bar_len(A), 2)}, {dec(8 * bar_len(t), 2)}", f"{dec(8 * bar_len(B), 2)}, {dec(8 * bar_len(t), 2)}"),
            ("Audio length change", pct_text(length_change(A, t)), pct_text(length_change(B, t))),
            ("Key shift to F major (semitones)", signed(sj), signed(sd)),
            ("New key and relative minor", f"F major, D minor", "F major, D minor"),
            ("Pitch change if only sped up (semitones)", f"{semis_from_speed(A, t):+.2f}".replace("-", MINUS), f"{semis_from_speed(B, t):+.2f}")]
    return "".join(f"<tr><td class='lt'>{a}</td><td>{b}</td><td>{c}</td></tr>" for a, b, c in rows)


def example_page(n, wm=False):
    inner = (f'<style>table.ec td {{ text-align: center; }} table.ec td.lt {{ text-align: left; font-weight: 600; }}</style>'
             f'<p style="margin:0 0 4pt;font-size:10pt">An <b>invented plan on paper</b>: a mashup at {EX_BPM} BPM in {TARGET_KEY} major. No audio is included. '
             f'Student projects will differ. Page 1 of 2: the plan and the numbers.</p>'
             f'<div class="cols" style="gap:10pt;align-items:flex-start"><div class="box"><span class="k">1 · A weak plan</span><p style="margin:0;font-size:10.2pt">{EX_WEAK}</p>'
             f'<p style="margin:3pt 0 0;font-size:9.2pt">It names no tempo, no ratio, no percent, no key and no checks.</p></div>'
             f'<div class="box acc-b"><span class="k">2 · A clear plan</span><p style="margin:0;font-size:8.4pt;line-height:1.28">{EX_STRONG}</p></div></div>'
             f'{D.H2("3 · The numbers behind the plan")}'
             f'<style>table.ex3 td, table.ex3 th {{ padding: 1.8pt 5pt; }}</style>'
             f'<table class="t ec ex3" style="font-size:8.8pt;line-height:1.14"><tr><th style="width:44%"></th><th>Jingle Bells</th><th>Deck the Halls</th></tr>{ex_number_rows()}</table>'
             f'<p style="margin:2pt 0 0;font-size:8.8pt;line-height:1.3">The last row shows why the match needs Flex or a transposition: speeding each song up or down like a record would push the two pitches the wrong way, so the speed and the key are set separately.</p>'
             f'<div class="box acc-b" style="margin-top:5pt"><span class="k">Why these choices</span><p style="margin:0;font-size:10pt;line-height:1.38">'
             f'The mean tempo asks each song for a change of about a tenth, and the two audio stretches are equal and opposite (+11.11% and {MINUS}11.11%), so neither song is bent far. '
             f'F major keeps Deck the Halls exactly as notated and asks only Jingle Bells to move, 2 semitones down. The beat check backs the choice up: no other shift has fewer hard clashes (page {pg("layer")}).</p></div>'
             f'<div class="box" style="margin-top:5pt"><span class="k">Try it yourself</span><p style="margin:0;font-size:10pt;line-height:1.38">Change the target key to G major: Jingle Bells stays, Deck the Halls moves {signed(short_shift(KEY_DH, "G"))}. '
             f'Run the beat check on page {pg("layer")} again: the counts are {shift_counts(BEST_SHIFT)[SMOOTH]} smooth, {shift_counts(BEST_SHIFT)[MILD]} mild and {shift_counts(BEST_SHIFT)[HARD]} hard, the same as before. Why?</p></div>')
    return D.page("Worked example · the plan and the numbers", "EXAMPLE", "Teacher", inner, n, wm, ak=True, key="example")


def ex_rows():
    out = []
    for i, nm_ in enumerate(SEC_NAMES):
        out.append(f"<tr><td style='text-align:left;white-space:nowrap'><b>{nm_}</b></td><td>{start_bar(i)}–{end_bar(i)}</td><td>{SEC_BARS[i]}</td><td>{dec(start_s(EX_BPM, i), 2)}</td><td>{dec(start_s(EX_BPM, i + 1), 2)}</td>"
                   f"<td style='text-align:left'>{EX_SEC_NOTES[i]}</td></tr>")
    return "".join(out)


def example2_page(n, wm=False):
    qs = " ".join(f"{i + 1}. {q}" for i, q in enumerate(EX_QUESTIONS))
    inner = (f'<p style="margin:0 0 3pt;font-size:10pt">The same track, page 2 of 2: the arrangement map, the section times, the mix and the questions.</p>'
             f'{D.H2("4 · The map: 44 bars, 6 sections, 7 elements")}'
             f'<div style="width:5.1in;margin:0 auto 2pt">{D.body_svg(PAGE_DRAWINGS["exmap-page"]())}</div>'
             f'{D.H2("5 · The six sections at 108 BPM")}'
             f'<style>table.ex5 td, table.ex5 th {{ padding: 1.6pt 4pt; }}</style>'
             f'<table class="t ec ex5" style="font-size:8.8pt;line-height:1.15"><tr><th>Section</th><th>Bars</th><th>Length (bars)</th><th>Starts (s)</th><th>Ends (s)</th><th>What happens</th></tr>{ex_rows()}</table>'
             f'<p style="margin:2pt 0 0;font-size:9pt">One beat lasts 60 ÷ {EX_BPM} = {dec(spb(EX_BPM), 3)} s and one bar lasts 240 ÷ {EX_BPM} = {dec(EX_BAR_S, 3)} s. The track has 4 + 8 + 4 + 8 + 16 + 4 = {TOTAL_BARS} bars, '
             f'which last {TOTAL_BARS} × {dec(EX_BAR_S, 3)} = {dec(total_s(EX_BPM), 2)} seconds ({mmss(total_s(EX_BPM))}).</p>'
             f'<div class="box" style="margin-top:5pt"><span class="k">6 · The mix</span><p style="margin:0;font-size:10pt;line-height:1.36">{EX_MIX}.</p></div>'
             f'<div class="box" style="margin-top:5pt"><span class="k">7 · Three feedback questions (invented)</span><p style="margin:0;font-size:10pt;line-height:1.36">{qs}</p></div>'
             f'<div class="box acc-b" style="margin-top:5pt"><span class="k">8 · Moments to point out in class</span><ul style="margin:0">'
             f'<li style="font-size:10pt;margin-bottom:2pt">The mashup starts at bar 25, {dec(start_s(EX_BPM, 4), 2)} seconds in: the class can hear the match at work.</li>'
             f'<li style="font-size:10pt;margin-bottom:0">Bar {ROUGH} of the mashup, the first bar of the second pass, is the roughest spot in the clash table (page {pg("layer")}): {mash_samples(BEST_SHIFT, (ROUGH - 1) // 8, (ROUGH - 1) % 8)[SMOOTH]} smooth pairs out of 4. A good place to ask what a different chord or a rest would change.</li></ul></div>')
    return D.page("Worked example · the map, the times and the mix", "EXAMPLE", "Teacher", inner, n, wm, ak=True, key="example2")


PAGES = {"howto": howto_page, "overview": overview_page, "setup": setup_page, "example": example_page, "example2": example2_page,
         "tempo": tempo_page, "keys": keys_page, "chart1": chart1_page, "chart2": chart2_page, "flex": flex_page, "layer": layer_page, "groove": groove_page,
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




BADGE = {"tempo": "Class 1", "keys": "Class 1", "chart1": "Classes 1–2", "chart2": "Classes 1–2", "flex": "Class 2", "layer": "Class 2", "groove": "Class 2",
         "map": "Class 3", "mix": "Class 3", "present": f"Classes {CLASSES - 1}–{CLASSES}"}
STEP_PAGES = {"tempo": {1}, "keys": {2}, "chart1": {3}, "chart2": {3}, "flex": {4}, "layer": {5}, "groove": {5}, "map": {6}, "mix": {6}}

FORBIDDEN_WORDS = ("church", "prayer", "pray ", "blessing", "holy", "sacred", "religio", "god ", "santa", "christmas", "hanukkah", "chanukah", "kwanzaa", "alcohol", "beer", "wine", "cocktail",
                   "toast", "cheers")
LYRIC_FRAGMENTS = ("dashing through", "dashing thro", "what fun it is", "oh what fun", "jingle all the way", "bells on bob", "bob tail", "bobtail", "boughs of", "fa la la", "fa-la-la",
                   "tis the season", "’tis the season", "don we now", "gay apparel", "yuletide", "yule tide", "troll the ancient", "laughing all the way", "in a one-horse", "in a one horse",
                   "o’er the fields", "spirits bright", "sleighing song", "miss fanny", "fannie bright")
EXPECT_CHORDS = ["F", "F", "Gm", "F", "F", "F", "Gm", "F", "F", "F", "Bb", "C", "F", "F", "Bb", "F"]      # the suggested chord for each of the 16 mashup bars
EXPECT_SHIFT_COUNTS = {-6: [42, 10, 12], -5: [34, 5, 25], -4: [29, 23, 12], -3: [31, 6, 27], -2: [45, 14, 5], -1: [31, 11, 22], 0: [28, 19, 17], 1: [46, 4, 14],
                       2: [38, 6, 20], 3: [46, 10, 8], 4: [32, 12, 20], 5: [46, 8, 10]}


def triad_pcs(root_pc, deg, scale):
    """The triad on scale degree `deg` (0-6) of a major scale, by stacking two thirds on the scale (independent of the interval formulas)."""
    return sorted({scale[deg % 7], scale[(deg + 2) % 7], scale[(deg + 4) % 7]})


def verify_content():
    errs = []
    counts = dict(goals=(GOALS, 4), vocab=(VOCAB, 5), reqs=(REQS, 7), steps=(STEPS, 7), tips=(TIPS, 4), check=(CHECK, 6),
                  rubric=(RUBRIC, 5), struggles=(STRUGGLES, 4), resources=(RESOURCES, 4), slides=(SLIDES, 15), plan=(PLAN, 27),
                  logic=(LOGIC_REF, 9), elements=(ELEMENTS, 7), sections=(SEC_NAMES, 6))
    for nm_, (lst, nexp) in counts.items():
        if len(lst) != nexp:
            errs.append(f"{nm_}: {len(lst)} items, expected {nexp}")
    if RUBRIC_TOTAL != 25 or LEVELS != [1, 2, 3, 4, 5] or len(RUBRIC_SHORT) != 5:
        errs.append("rubric is /25, levels 1-5")
    if FILE_NAME not in CHECK[2]:
        errs.append("file name format must be on the checklist")
    if set(TAGS) & {"Holiday", "Student Practice", "Theme", "Seasonal"} or "Performing Arts" in SUBJECTS:
        errs.append("tags and subjects must not be headings")
    tag_opts = json.load(open(os.path.join(os.path.dirname(HERE), "TAG-OPTIONS.json"), encoding="utf8"))["options"]
    sub_opts = json.load(open(os.path.join(os.path.dirname(HERE), "SUBJECT-OPTIONS.json"), encoding="utf8"))
    for t in TAGS:
        if t not in tag_opts:
            errs.append(f"tag {t} is not in tpt/TAG-OPTIONS.json")
    for s_ in SUBJECTS:
        if s_ not in sub_opts:
            errs.append(f"subject {s_} is not in tpt/SUBJECT-OPTIONS.json")
    if len(TAGS) > 6:
        errs.append("at most 6 tags")
    if len(LISTING_TITLE) > 80 or "Logic Pro" not in LISTING_TITLE[:30]:
        errs.append("listing title: at most 80 characters, 'Logic Pro' in the first 30")
    for w in ("new year", "winter", "holiday", "christmas", "hanukkah", "chanukah", "sleigh", "carol", "snow", "eve ", "jingle", "deck the", "halls"):
        if w in LISTING_TITLE.lower():
            errs.append(f"the listing title must not hold the seasonal word {w}")
    if len(STEP_NAMES) != len(STEPS) or any(not s.startswith(f"<b>{nm_}</b>") for s, nm_ in zip(STEPS, STEP_NAMES)):
        errs.append("STEPS must start with the bold names in STEP_NAMES (the pages cite them)")
    # ---- the charts: bar sums, ranges, scales, moved copies
    for nm_, ch in (("Jingle Bells", CHART_JB_G), ("Deck the Halls", CHART_DH_F)):
        if len(ch) != NBARS:
            errs.append(f"{nm_}: {NBARS} bars")
        for i, bar in enumerate(ch, start=1):
            if sum(d for _, d in bar) != 16:
                errs.append(f"{nm_} bar {i} adds up to {sum(d for _, d in bar)} sixteenths, not 16")
            for p, d in bar:
                if d not in LEN_ABBR or d not in LEN_NAMES:
                    errs.append(f"{nm_} bar {i}: unknown length {d}")
    if len(JB_NOTES) != 96 or len(DH_NOTES) != 68:
        errs.append(f"note counts: Jingle Bells 96 and Deck the Halls 68 (found {len(JB_NOTES)} and {len(DH_NOTES)})")
    if (min(m for m, _, _ in JB_NOTES), max(m for m, _, _ in JB_NOTES)) != JB_ROWS or (min(m for m, _, _ in DH_NOTES), max(m for m, _, _ in DH_NOTES)) != DH_ROWS:
        errs.append("the roll rows are the lowest and highest notes: Jingle Bells D4 to E5, Deck the Halls E4 to F5")
    gmaj, fmaj = {7, 9, 11, 0, 2, 4, 6}, {5, 7, 9, 10, 0, 2, 4}
    if not {m % 12 for m, _, _ in JB_NOTES} <= gmaj:
        errs.append("Jingle Bells uses only G major notes")
    if {m % 12 for m, _, _ in DH_NOTES} - fmaj != {11} or sum(1 for m, _, _ in DH_NOTES if m % 12 == 11) != 1:
        errs.append("Deck the Halls uses F major notes and one passing B natural (bar 11)")
    jb_f = moved(CHART_JB_G, -2, "F")
    dh_g = moved(CHART_DH_F, 2, "G")
    for a, b in zip(chart_notes(CHART_JB_G), chart_notes(jb_f)):
        if a[0] - b[0] != 2 or a[1:] != b[1:]:
            errs.append(f"Jingle Bells in F must be the G chart 2 semitones down, note for note: {a} {b}")
    for a, b in zip(chart_notes(CHART_DH_F), chart_notes(dh_g)):
        if b[0] - a[0] != 2 or a[1:] != b[1:]:
            errs.append(f"Deck the Halls in G must be the F chart 2 semitones up, note for note: {a} {b}")
    if any("#" in p for bar in jb_f for p, _ in bar) or any("b" in p[1:] for bar in dh_g for p, _ in bar):
        errs.append("spelling: flats in F major, sharps in G major")
    if not any(p == "Bb4" for bar in jb_f for p, _ in bar) or not any(p == "C#5" for bar in dh_g for p, _ in bar):
        errs.append("Jingle Bells in F has Bb4 (from C5) and Deck the Halls in G has C#5 (from the passing B)")
    for k in range(4):
        if CHART_DH_F[4 + k] != CHART_DH_F[k]:
            errs.append(f"Deck the Halls bar {5 + k} repeats bar {1 + k}")
    if CHART_DH_F[12] != CHART_DH_F[0] or CHART_DH_F[13] != CHART_DH_F[1]:
        errs.append("Deck the Halls bars 13 and 14 repeat bars 1 and 2")
    # ---- the sources: every difference between the chart and each typed source is the expected one
    got = note_diffs(JB_NOTES, src_notes(SRC_BROWN, jb_brown_off))
    if got != EXPECT_JB_BROWN:
        errs.append(f"Jingle Bells chart versus CPDL 38153: {got}, expected {EXPECT_JB_BROWN}")
    got = note_diffs(JB_NOTES, src_notes(SRC_HALE, jb_hale_off, -1))
    if got != EXPECT_JB_HALE:
        errs.append(f"Jingle Bells chart versus CPDL 66808 (A-flat moved down 1): {got}, expected {EXPECT_JB_HALE}")
    for nm_, src, off, sh, exp in (("CPDL 47663", SRC_SIMS, dh_off, 0, ([], [], [])), ("CPDL 502", SRC_ORNES, dh_off, 0, EXPECT_DH_ORNES), ("CPDL 39398 (E-flat moved up 2)", SRC_WOOD, dh_off, 2, ([], [], []))):
        got = note_diffs(DH_NOTES, src_notes(src, off, sh))
        if got != exp:
            errs.append(f"Deck the Halls chart versus {nm_}: {got}, expected {exp}")
    # the pitch pickups the chart leaves out are the only extra notes in the 4/4 edition, and both are D5 on beat 4
    if [(s % 16, p) for s, p in EXPECT_JB_BROWN[1]] != [(12, "D5"), (12, "D5")]:
        errs.append("the two dropped pickups are D5 on beat 4")
    for src, bars_ in ((SRC_BROWN, 16), (SRC_SIMS, 16), (SRC_WOOD, 16)):
        for b, txt in src.items():
            tot = sum(int(t.split("+")[1]) for t in txt.split())
            if tot != 16:
                errs.append(f"source bar {b} adds up to {tot} sixteenths")
    # ---- keys
    if [circle_pos(pc) for _, pc in KEY_ORDER] != list(range(12)):
        errs.append("the circle of fifths: each key is a fifth (7 semitones) after the one before it")
    for k, pc in KEY_ORDER:
        if sig_of(pc) != KEY_SIG[k] and not (k == "F#"):
            errs.append(f"key signature of {k}: {sig_of(pc)} versus {KEY_SIG[k]}")
        mn = MINOR_OF[k]
        mpc = midi(mn + "4") % 12
        if mpc != (pc + 9) % 12:
            errs.append(f"relative minor of {k} major is {mn}: pitch class {mpc}, expected {(pc + 9) % 12}")
    if sig_of(6) != "6 sharps":
        errs.append("F# major has 6 sharps")
    names = dict(KEY_ORDER)
    for a in names:
        for b in names:
            sh = short_shift(a, b)
            if abs(sh) > 6 or (names[a] + sh - names[b]) % 12 != 0 or up_semis(a, b) != (names[b] - names[a]) % 12:
                errs.append(f"shorter shift {a} to {b}: {sh}")
            if fifths_apart(a, b) > 6 or fifths_apart(a, b) != fifths_apart(b, a):
                errs.append(f"fifths apart {a} {b}")
    want = {("G", "F"): (10, 2, -2, 2), ("Ab", "F"): (9, 3, -3, 3), ("Eb", "F"): (2, 10, 2, 2), ("D", "G"): (5, 7, 5, 1), ("C", "F#"): (6, 6, 6, 6), ("A", "Eb"): (6, 6, 6, 6)}
    for a, b, _ in KEY_PAIRS:
        up, down, sh, fa = want[(a, b)]
        if (up_semis(a, b), (12 - up_semis(a, b)) % 12, short_shift(a, b), fifths_apart(a, b)) != (up, down, sh, fa):
            errs.append(f"key pair {a} to {b}: {(up_semis(a, b), (12 - up_semis(a, b)) % 12, short_shift(a, b), fifths_apart(a, b))}, expected {(up, down, sh, fa)}")
    if [(t, short_shift(KEY_JB, t), short_shift(KEY_DH, t)) for t, _ in TARGET_OPTIONS] != [("F", -2, 0), ("G", 0, 2), ("F#", -1, 1)]:
        errs.append("target keys: F (-2, 0), G (0, +2), F# (-1, +1)")
    if KEY_JB != "G" or KEY_DH != "F" or up_semis("G", "F") != 10 or sig_of(KEY_PC["F"]) != "1 flat" or sig_of(KEY_PC["G"]) != "1 sharp" or MINOR_OF["G"] != "E" or MINOR_OF["F"] != "D":
        errs.append("G major (1 sharp, relative minor E) and F major (1 flat, relative minor D)")
    # ---- tempo math
    if ratio(120, 96) != (5, 4) or ratio(120, 60) != (2, 1) or ratio(120, 80) != (3, 2) or ratio(120, 100) != (6, 5) or ratio(100, 90) != (10, 9) or ratio(128, 64) != (2, 1):
        errs.append("tempo ratios: 120:96 = 5:4, 120:60 = 2:1, 120:80 = 3:2, 120:100 = 6:5, 100:90 = 10:9")
    if TARGET != 108 or pct(120, 108) != -10 or pct(96, 108) != Fraction(25, 2) or pct(96, 120) != 25 or pct(120, 96) != -20 or pct(120, 120) != 0:
        errs.append("percent changes: 120 to 108 is -10, 96 to 108 is +12.5, 96 to 120 is +25, 120 to 96 is -20")
    if [pct_text(x) for x in (pct(120, 108), pct(96, 108), pct(96, 120), pct(120, 96), pct(120, 120), pct(120, 90), pct(60, 90), pct(120, 100), pct(100, 110), pct(90, 95))] != \
       [MINUS + "10%", "+12.5%", "+25%", MINUS + "20%", "0%", MINUS + "25%", "+50%", MINUS + "16.67%", "+10%", "+5.56%"]:
        errs.append("percent text: -10%, +12.5%, +25%, -20%, 0%, -25%, +50%, -16.67%, +10%, +5.56%")
    if [dec(bar_len(b), 3) for b in (120, 96, 108, 100, 128, 80, 90, 110)] != ["2.000", "2.500", "2.222", "2.400", "1.875", "3.000", "2.667", "2.182"]:
        errs.append("seconds per bar in 4/4 = 240 / BPM at 120, 96, 108, 100, 128, 80, 90, 110")
    if [bar_len(108, b) for b in (2, 3, 4)] != [Fraction(10, 9), Fraction(5, 3), Fraction(20, 9)] or any(bar_len(b, 4) != 4 * spb(b) for b in TEMPOS):
        errs.append("seconds per bar at 108 BPM: 2/4 is 120/108, 3/4 is 180/108, 4/4 is 240/108 and always beats x seconds per beat")
    for b in TEMPOS + (96, 108):
        if abs(float(bar_len(b)) - 240 / b) > 1e-9:
            errs.append(f"float check of 240 / {b}")
    if SEC_BARS != [4, 8, 4, 8, 16, 4] or sum(SEC_BARS) != 44 or [start_bar(i) for i in range(6)] != [1, 5, 13, 17, 25, 41] or [end_bar(i) for i in range(6)] != [4, 12, 16, 24, 40, 44]:
        errs.append("sections: 4 + 8 + 4 + 8 + 16 + 4 = 44 bars starting at bars 1, 5, 13, 17, 25 and 41")
    if [dec(start_s(108, i), 2) for i in range(7)] != ["0.00", "8.89", "26.67", "35.56", "53.33", "88.89", "97.78"] or [dec(total_s(b), 2) for b in (96, 108, 120)] != ["110.00", "97.78", "88.00"]:
        errs.append("section starts at 108 BPM and the 44-bar track at 96, 108 and 120 BPM")
    for b in (96, 108, 120):
        for i in range(7):
            if abs(float(sum(SEC_BARS[:i]) * bar_len(b)) - sum(SEC_BARS[:i]) * 240 / b) > 1e-9:
                errs.append(f"section {i} start at {b} BPM: float check fails")
    if rnd(Fraction(5, 2), 0) != 3 or mmss(total_s(108)) != "1:38" or dec(Fraction(88, 9), 2) != "9.78":
        errs.append("round half up; 97.78 seconds is 1:38")
    if A_BPM not in range(TEMPO_MARKS["Jingle Bells"][0], TEMPO_MARKS["Jingle Bells"][-1] + 1) or B_BPM not in range(TEMPO_MARKS["Deck the Halls"][0], TEMPO_MARKS["Deck the Halls"][-1] + 1):
        errs.append("the typical class tempos lie inside the range of the tempo marks in the files read")
    # ---- Smart Tempo and Flex numbers
    if [pct_text(length_change(o, t)) for o, t in ((120, 108), (96, 108), (96, 120), (120, 96))] != ["+11.11%", MINUS + "11.11%", MINUS + "20%", "+25%"]:
        errs.append("audio length change = orig / target - 1: +11.11%, -11.11%, -20%, +25%")
    if [dec(8 * bar_len(b), 2) for b in (120, 108, 96)] != ["16.00", "17.78", "20.00"]:
        errs.append("8 bars last 16.00 s at 120, 17.78 s at 108 and 20.00 s at 96 BPM")
    if round(semis_from_speed(120, 108), 2) != -1.82 or round(semis_from_speed(96, 108), 2) != 2.04 or round(freq_ratio(-2), 3) != 0.891 or round(freq_ratio(2), 3) != 1.122 or round(freq_ratio(12), 6) != 2:
        errs.append("pitch from speed: 12 x log2(0.9) = -1.82 and 12 x log2(1.125) = +2.04 semitones; frequency ratio of -2 is 0.891 and of +2 is 1.122")
    if abs(1 / (1 + float(pct(120, 108)) / 100) - float(1 + length_change(120, 108) / 100)) > 1e-12:
        errs.append("length change is the inverse of the speed change")
    # ---- layering: counts for every shift, recomputed with an independent loop over the chart bars
    for s in SHIFTS:
        if shift_counts(s) != EXPECT_SHIFT_COUNTS[s] or sum(shift_counts(s)) != 64:
            errs.append(f"clash counts for shift {s}: {shift_counts(s)}, expected {EXPECT_SHIFT_COUNTS[s]}")
    if BEST_SHIFT != -2 or any(shift_counts(s)[HARD] <= shift_counts(-2)[HARD] for s in SHIFTS if s != -2):
        errs.append("the key-matched shift (-2) has strictly the fewest hard clashes")
    # the other target (Deck the Halls up 2, Jingle Bells unmoved) gives the same pairs: both moved together, intervals unchanged
    c2 = [0, 0, 0]
    for pas in range(2):
        for t in range(0, 128, 4):
            c2[ic_cat(sound(JB_NOTES, 128 + t), sound(DH_NOTES, pas * 128 + t) + 2)] += 1
    if c2 != shift_counts(-2):
        errs.append("a target of G (Deck the Halls +2) must give the same beat counts as a target of F")
    indep = [0, 0, 0]
    jb_chorus = [(m - 2, s - 128, d) for m, s, d in JB_NOTES if s >= 128]
    for pas in range(2):
        dh = [(m, s - pas * 128, d) for m, s, d in DH_NOTES if pas * 128 <= s < pas * 128 + 128]
        for t in range(0, 128, 4):
            a = [m for m, s, d in jb_chorus if s <= t < s + d][0]
            b = [m for m, s, d in dh if s <= t < s + d][0]
            ic = min((a - b) % 12, (b - a) % 12)
            indep[0 if ic in (0, 3, 4, 5) else 1 if ic == 2 else 2] += 1
    if indep != [45, 14, 5]:
        errs.append(f"independent beat count at the matched shift: {indep}")
    if [best_chord(m)[0] for m in range(1, 17)] != EXPECT_CHORDS:
        errs.append(f"suggested chords: {[best_chord(m)[0] for m in range(1, 17)]}")
    scale_f = [5, 7, 9, 10, 0, 2, 4]
    for nm_, rn, pcs in CHORDS_F:
        deg = ["I", "ii", "iii", "IV", "V", "vi"].index(rn)
        deg = {"I": 0, "ii": 1, "iii": 2, "IV": 3, "V": 4, "vi": 5}[rn]
        if sorted(pcs) != triad_pcs(5, deg, scale_f):
            errs.append(f"chord {nm_} ({rn}) in F: {sorted(pcs)} versus the triad on the scale {triad_pcs(5, deg, scale_f)}")
        if SHARP_NAMES[pcs[0] % 12] != nm_.rstrip("m") and FLAT_NAMES[pcs[0] % 12] != nm_.rstrip("m"):
            errs.append(f"chord {nm_} root")
        if CHORD_G[nm_] not in (SHARP_NAMES[(pcs[0] + 2) % 12], SHARP_NAMES[(pcs[0] + 2) % 12] + ("m" if nm_ in ("Dm", "Gm", "Am") else "")):
            errs.append(f"chord {nm_} in G is {CHORD_G[nm_]}")
    for m in range(1, 17):
        pas, j = (m - 1) // 8, (m - 1) % 8
        if sum(mash_samples(BEST_SHIFT, pas, j)) != 4:
            errs.append(f"mashup bar {m}: four beats")
        if not 1 <= best_chord(m)[2] <= 8:
            errs.append(f"mashup bar {m}: chord fit")
    if ROUGH != 9:
        errs.append(f"the roughest mashup bar is 9 (no smooth pair), found {ROUGH}")
    if sum(sum(mash_samples(BEST_SHIFT, p, j)[HARD] for j in range(8)) for p in range(2)) != 5:
        errs.append("the bars add up to the 5 hard clashes")
    # ---- the grooves
    for g in GROOVES:
        gg = GROOVES[g]
        if any(len(gg[ln]) != 16 for ln in GROOVE_LANES):
            errs.append(f"groove {g}: every lane has 16 steps")
        if (len(hits(g, "Kick")), len(hits(g, "Snare")), len(hits(g, "Hat"))) != GROOVE_FACTS[g]:
            errs.append(f"groove {g}: kick, snare and hat hits per bar should be {GROOVE_FACTS[g]}")
    if hits("steady", "Snare") != [4, 12] or hits("half", "Snare") != [8] or hits("half", "Kick") != [0, 10] or hits("steady", "Kick") != [0, 6, 8]:
        errs.append("steady: snare on beats 2 and 4, kick on 1, the and of 2 and 3; half-time: snare on beat 3, kick on beat 1 and the and of 3")
    if EX_BPM // 2 != 54 or EX_BPM != 108:
        errs.append("half-time at 108 BPM feels like 54")
    # ---- the map
    if len(ELEMENTS) != 7 or any(len(c) != 6 for _, c in ELEMENTS) or ELEM_PLAYING != [2, 4, 5, 4, 6, 3] or sum(ELEM_PLAYING) != 24:
        errs.append("the map: 7 elements x 6 sections; 2, 4, 5, 4, 6 and 3 playing (24 in all)")
    if ELEM_PLAYING[4] != max(ELEM_PLAYING) or ELEM_PLAYING.count(max(ELEM_PLAYING)) != 1:
        errs.append("the mashup section has strictly the most elements")
    cells = dict(ELEMENTS)
    if [bool(c) for c in cells["Jingle Bells line"]] != [False, True, True, False, True, False] or [bool(c) for c in cells["Deck the Halls line"]] != [False, False, True, True, True, False]:
        errs.append("Jingle Bells plays in its section, the bridge and the mashup; Deck the Halls in its section, the bridge and the mashup")
    # ---- Logic wording: newer tools are hedged
    for nm_, txt in LOGIC_REF:
        for w in ("Smart Tempo", "Flex Time", "Flex Pitch", "Session Players", "Create Marker"):
            if w in txt and "if your version" not in txt.lower():
                errs.append(f"Logic reference '{nm_}' must hedge {w} with 'if your version'")
    for w in ("Smart Tempo", "Flex Time", "Flex Pitch", "Alchemy", "Drum Machine Designer", "Piano Roll", "Session Players", "Marker", "Transpose", "region inspector", "Retro Synth"):
        if w not in " ".join(t for _, t in LOGIC_REF):
            errs.append(f"the Logic quick reference must name {w}")
    for bad in ("Settings › ", "Preferences › ", "Smart Tempo Editor", "Project Settings ›"):
        if bad in " ".join(t for _, t in LOGIC_REF):
            errs.append(f"no invented menu path: {bad}")
    # ---- the worked example
    if EX_BPM != 108 or dec(EX_BAR_S, 3) != "2.222" or dec(total_s(EX_BPM), 2) != "97.78" or TARGET_KEY != "F":
        errs.append("the example: 108 BPM, 2.222 s per bar, 97.78 s, target key F")
    for need in ("120 : 96 = 5 : 4", "(120 + 96) ÷ 2 = 108", "(108 ÷ 120 − 1) × 100 = −10%", "(108 ÷ 96 − 1) × 100 = +12.5%", "240 ÷ 108 = 2.222 seconds", "97.78 seconds", "44-bar",
                 "G down to F is −2", "F up to G is +10", "E minor to D minor", "45 smooth, 14 mild and 5 hard", "out of 64"):
        if need not in EX_STRONG:
            errs.append(f"the clear plan must say '{need}'")
    # ---- no forbidden themes in any text a buyer reads; the carols' words are not printed
    allt = " ".join([THEME, SOURCE_NOTE, OVERVIEW, " ".join(GOALS), " ".join(f"{a} {b}" for a, b in VOCAB), " ".join(REQS), " ".join(STEPS), " ".join(TIPS), " ".join(CHECK),
                     " ".join(d for _, ds in RUBRIC for d in ds), TN_REINFORCES, " ".join(STRUGGLES), VAR_EASY, VAR_HARD, " ".join(f"{a} {b}" for a, b in RESOURCES), TN_NOTE,
                     " ".join(GRADING), " ".join(d["do"] for d in PACING), SONG_NOTE, " ".join(CREDITS), " ".join(t for _, t in LOGIC_REF), EX_STRONG, EX_MIX, " ".join(EX_QUESTIONS),
                     " ".join(EX_SEC_NOTES), " ".join(" ".join((s[2], s[3], s[4])) for s in SLIDES), " ".join(" ".join(c) for _, c in ELEMENTS),
                     " ".join(" ".join(v) for v in GROOVE_TEXT.values())]).lower()
    for w in FORBIDDEN_WORDS:
        if re.search(rf"\b{re.escape(w.strip())}\b", allt):
            errs.append(f"no religious teaching, alcohol or seasonal-holiday wording in a neutral kit: '{w.strip()}'")
    for w in LYRIC_FRAGMENTS:
        if w in allt:
            errs.append(f"the carols' words are not printed: '{w}'")
    for need in ("1857", "1862", "public domain", "sixteenth century", "1898"):
        if need not in allt:
            errs.append(f"the theme and source note must give '{need}'")
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
    for need, key in ((f"page {pg('tempo')}", 4), (f"page {pg('tempo')}", 5), (f"page {pg('keys')}", 6), (f"page {pg('layer')}", 7), (f"page {pg('flex')}", 8), (f"page {pg('logicref')}", 9),
                      (f"page {pg('map')}", 10), (f"page {pg('tempo')}", 10)):
        if need not in SLIDES[key][4]:
            errs.append(f"slide {key + 1} notes must name {need}")
    for i, s in enumerate(SLIDES, start=1):
        errs += step_ref_errors(" ".join((s[2], s[3], s[4])), f"slide {i}")
    if [s[0] for s in SLIDES] != [1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 3, 3, 3, 3, 3] or SLIDES[3][1] != "days":
        errs.append("deck classes: slides 1-7 Class 1, 8-10 Class 2, 11-15 Class 3; slide 4 is the 'days' slide (it gets the Classes 1-3 badge)")
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
    for need in ("No audio, recordings or lyrics", "invented plan on paper", "Drum Machine Designer", "Alchemy", "Piano Roll", "Session Players", "Smart Tempo", "Flex Time", "Flex Pitch",
                 "Marker", "60 ÷ BPM", "240 ÷ BPM", "semitone", "circle of fifths", "if your version", "public domain", "half-time", "Jingle Bells", "Deck the Halls",
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
            errs.append(f"no religious teaching, alcohol or holiday-specific wording in this product ({w.strip()})")
    for w in LYRIC_FRAGMENTS:
        if w in (txt + " " + alldeck).lower():
            errs.append(f"the carols' words are not printed: '{w}'")
    for w in ("colour", "favour", "centre", "licence", "grey", "metre", "organis", "recognis", "practise", "analyse", "whilst", "milli-second", "colourful", "harmonis"):
        if w in txt.lower().replace("greyscale", ""):
            errs.append(f"US spelling: '{w}' in the PDF")
    # ---- Step N on every page, in the deck PDF text, the deck notes and UPLOAD.md agrees with the project sheet
    for k in PLAN:
        t = flat[D.IX(k) - 1]
        errs += step_ref_errors(t, f"page {D.IX(k)} ({k})")
        found = {int(m.group(1)) for m in re.finditer(r"\bStep (\d+)\b", t)}
        if k in STEP_PAGES and found != STEP_PAGES[k]:
            errs.append(f"page {D.IX(k)} ({k}) should cite Step {sorted(STEP_PAGES[k])}, cites {sorted(found)}")
        if k not in STEP_PAGES and found:
            errs.append(f"page {D.IX(k)} ({k}) cites Step {sorted(found)} unexpectedly")
    errs += step_ref_errors(" ".join(stext), "deck slides")
    errs += badge_errors(flat)
    import subprocess as sp

    def raw(key):
        return re.sub(r"\s+", " ", sp.run(["pdftotext", "-raw", "-f", str(D.IX(key)), "-l", str(D.IX(key)), D.files()["pdf"], "-"],
                                          capture_output=True, text=True, check=True).stdout).replace("- ", "-")
    # ---- the tempo page prints every number
    rt = raw("tempo")
    for label, t in (("Jingle Bells’ tempo", A_BPM), ("Deck the Halls’ tempo", B_BPM), ("The mean of the two", 108)):
        row = f"{label} {t} {pct_text(pct(A_BPM, t))} {pct_text(pct(B_BPM, t))} {dshort(bar_len(t), 3)} {dec(total_s(t), 2)}"
        if row not in rt:
            errs.append(f"tempo page: row '{row}' is not printed")
    for a, b in PAIRS:
        n_, d_ = ratio(a, b)
        mean = Fraction(a + b, 2)
        row = f"{a} and {b} {n_} : {d_} {pair_meaning(a, b).split(', ', 1)[1]} {dshort(mean, 2)} {pct_text(pct(a, mean))} · {pct_text(pct(b, mean))}"
        if row not in rt:
            errs.append(f"tempo page: pair row '{row}' is not printed")
    for need in ("Step 1: match the tempo", "Seconds per beat = 60 ÷ BPM", "Seconds per bar in 4/4 = 240 ÷ BPM", "3/4: 180 ÷ BPM", "2/4: 120 ÷ BPM", "(target ÷ original − 1) × 100", "120 ÷ 96 = 5 ÷ 4",
                 "double-time", "half-time", "240 ÷ 108 = 2.222", "97.78", "5 rounds up", "typical class tempo", "80 to 144", "96 to 160", "108 BPM"):
        if need not in rt.replace("108 BPM", "108 BPM") and need not in rt:
            errs.append(f"tempo page must say '{need}'")
    # ---- the key page
    rk = raw("keys")
    for a, b, note in KEY_PAIRS:
        up = up_semis(a, b)
        sh = "±6 (a tie)" if up == 6 else signed(short_shift(a, b))
        row = f"{a} to {b} {up} {(12 - up) % 12} {sh} {fifths_apart(a, b)} {note}"
        if row not in rk:
            errs.append(f"key page: row '{row}' is not printed")
    for t, why in TARGET_OPTIONS:
        sj, sd = short_shift(KEY_JB, t), short_shift(KEY_DH, t)
        row = f"{t} major {signed(sj)} {signed(sd)} {abs(sj) + abs(sd)} {MINOR_OF[t]} minor {sig_of(KEY_PC[t])} {why}"
        if row not in rk:
            errs.append(f"key page: target row '{row}' is not printed")
    for need in ("Step 2: match the key", "(B − A) mod 12", "subtract 12", "Never move more than 6 semitones", "relative minor", "circle", "G major", "F major", "A-flat major", "E-flat major"):
        if need.lower() not in rk.lower():
            errs.append(f"key page must say '{need}'")
    # ---- the chart pages print every note in both keys
    for key_, base, other, bk, ok in (("chart1", CHART_JB_G, moved(CHART_JB_G, -2, "F"), "G", "F"), ("chart2", CHART_DH_F, moved(CHART_DH_F, 2, "G"), "F", "G")):
        rn = raw(key_)
        for i in range(16):
            for ch in (base, other):
                t = bar_text(ch[i])
                if f"{t}" not in rn:
                    errs.append(f"{key_}: bar {i + 1} '{t}' is not printed")
        for need in (("Step 3: enter the melodies", "subtract one", "public-domain") if key_ == "chart1" else ("Step 3: enter the melodies", "public-domain", "CPDL")):
            if need not in rn:
                errs.append(f"{key_} must say '{need}'")
    # ---- the Smart Tempo and Flex page
    rf = raw("flex")
    for t in (A_BPM, 108, B_BPM):
        for nm_, o in ((A_NAME, A_BPM), (B_NAME, B_BPM)):
            row = f"{nm_} {o} {t} {pct_text(pct(o, t))} {pct_text(length_change(o, t))} {dec(8 * bar_len(o), 2)} {dec(8 * bar_len(t), 2)}"
            if row not in rf:
                errs.append(f"flex page: row '{row}' is not printed")
    for need in ("Step 4: check with Smart Tempo and Flex", "if your version has it", "Smart Tempo", "Flex Time", "Flex Pitch", "region or track inspector", "11.11%", "17.78", "1.82", "2.04", "0.891", "1.122", "100 cents"):
        if need.lower() not in rf.lower():
            errs.append(f"flex page must say '{need}'")
    # ---- the layering page prints the counts and chords
    rl = raw("layer")
    for m in range(1, 17):
        pas, j = (m - 1) // 8, (m - 1) % 8
        c = mash_samples(-2, pas, j)
        ch, rn, fit = best_chord(m)
        row = f"{m} {9 + j} {pas * 8 + j + 1} {c[0]} {c[1]} {c[2]} {ch} ({rn}) · {CHORD_G[ch]} {fit} of 8"
        if row not in rl:
            errs.append(f"layer page: row '{row}' is not printed")
    for need in ("Step 5: layer and build the groove", "45 smooth, 14 mild and 5 hard", "fewest hard clashes", "quick check on the beats", "−2"):
        if need not in rl:
            errs.append(f"layer page must say '{need}'")
    rg = raw("groove")
    for need in ("Step 5: layer and build the groove", "Steady groove", "Half-time groove", "half-time", "double-time", "54 BPM", "108 BPM"):
        if need.lower() not in rg.lower():
            errs.append(f"groove page must say '{need}'")
    for nm_, rn, pcs in CHORDS_F:
        row = f"{nm_} {rn} " + " ".join(pcname(60 + p, "F") for p in pcs) + f" {CHORD_G[nm_]} " + " ".join(pcname(60 + (p + 2) % 12, "G") for p in pcs)
        if row not in rg:
            errs.append(f"groove page: chord row '{row}' is not printed")
    # ---- the arrangement map page
    rm = raw("map")
    for need in ("Step 6: arrange and mix", "2, 4, 5, 4, 6, 3", "add up to 24", "44 bars"):
        if need not in rm:
            errs.append(f"arrangement map page must say '{need}'")
    for i, nm_ in enumerate(SEC_NAMES):
        row = f"{nm_} {SEC_BARS[i]} {start_bar(i)}–{end_bar(i)} " + " ".join(dec(start_s(b, i), 2) for b in (96, 108, 120))
        if row not in rm:
            errs.append(f"arrangement map page: row '{row}' is not printed")
    # ---- the worked example prints its numbers
    re1 = raw("example") + " " + raw("example2")
    for i, nm_ in enumerate(SEC_NAMES):
        row = f"{nm_} {start_bar(i)}–{end_bar(i)} {SEC_BARS[i]} {dec(start_s(EX_BPM, i), 2)} {dec(start_s(EX_BPM, i + 1), 2)} {EX_SEC_NOTES[i]}"
        if row not in re1:
            errs.append(f"worked example: section row '{row}' is not printed")
    for need in ("60 ÷ 108 = 0.556 s", "240 ÷ 108 = 2.222 s", "4 + 8 + 4 + 8 + 16 + 4 = 44 bars", "44 × 2.222 = 97.78 seconds (1:38)", "17.78", "+11.11%", "−11.11%", "−1.82", "+2.04", "5 : 4",
                 "−10%", "+12.5%", "F major, D minor"):
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
            errs.append(f"UPLOAD.md prints the carols' words: '{w}'")
    for banned in ["Billie", "Beatles", "Daft", "Skrillex", "Disney", "Radiohead", "Billboard", "Ro" + "land", "Bensound", "Ableton "]:
        if banned in alldeck or banned in txt:
            errs.append(f"must not name artists, albums, songs, sites, services or other brands ({banned})")
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
    return ("both melody charts (16 bars of 4/4 each; every bar adds up to 16 sixteenths; Jingle Bells D4 to E5 in G major, Deck the Halls E4 to F5 in F major with one passing B natural) compared note by note "
            "with the typed scores they came from (Jingle Bells: two CPDL editions; Deck the Halls: three), every difference being the expected one; the moved charts (G down 2 to F, F up 2 to G) recomputed note "
            "by note and spelled with flats or sharps; the key table (12 keys, circle steps, key signatures, relative minors, shorter shift for all 144 pairs, six printed pairs, three target keys); tempo ratios, "
            "percent changes (exact fractions), seconds per beat and per bar in 2/4, 3/4 and 4/4, 44-bar section starts at 96, 108 and 120 BPM (exact fractions and a float method); audio length changes, "
            "8-bar lengths, pitch from speed and frequency ratios; the beat-by-beat clash counts for every shift from -6 to +5 (recomputed by an independent loop; -2 has the fewest hard clashes; a target of G gives "
            "the same counts) and the 16 suggested chords; groove cards; the arrangement map (7 elements x 6 sections, 2, 4, 5, 4, 6, 3 playing); every 'Step N' agrees with the project sheet on pages, slides, "
            "notes and UPLOAD.md; class badges agree with the pacing page, and the deck's 'three classes' slide carries Classes 1-3; every drawing renders alone on a transparent ground with no ink at its edges; "
            "hero art inside its viewBox; rendered-DOM footer gap on every page; no truncated slide bullets; edges of cover.png and previews clear; no audio, lyrics, religious, alcohol or brand wording or student "
            "work; grades 9-12; tags and subjects are not headings; no 'what changed' page (ORIGINAL).")



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
    desc = (f"{DESC_START} students make a DJ-style mashup of two public-domain carols in Logic Pro. They compare the tempos of “Jingle Bells” and “Deck the Halls” as a ratio, choose a target tempo and "
            f"calculate each song’s percent speed change and the seconds per bar (240 ÷ BPM in 4/4). They find the shortest semitone shift between the two keys with the circle of fifths, enter both melodies "
            f"from a note chart, check the match with Smart Tempo, Flex Time and Flex Pitch (if your version has them), and layer the melodies over one groove in a 44-bar arrangement. The theme is secular and "
            f"fits any winter lesson. This Holiday Mashup project takes {CLASSES} class periods (the pacing guide also shows two and four) and is an original Hudson Beat project; "
            f"the steps are written for Logic Pro, while the ideas (tempo ratios, transposition, layering, arrangement) carry over to GarageBand.\n\n"
            f"WHAT'S INCLUDED (ZIP: {np_}-page PDF = 1 cover + {n_teacher} teacher + {n_student} student + 1 terms page, plus {ns}-slide intro deck as .pptx and PDF)\n"
            f"• Teacher pages: how to use, project overview with the two carols at a glance, setup, a {CLASSES}-class pacing guide with the deck slides for each class, "
            f"two pages of teacher notes (struggles, variations, resources, grading), a Logic quick reference and a two-page worked example (an invented plan at 108 BPM in F major: "
            f"a 44-bar track of 97.78 seconds, with every percent change, shift and section time) ({n_teacher} pages)\n"
            f"• Student pages: a tempo page (formulas, ratios, three target tempos with percent changes and six more tempo pairs), a key page (the circle of fifths, semitones up and down for six key pairs and three target keys), "
            f"note charts of both melodies as piano rolls and bar-by-bar tables in two keys each, a Smart Tempo and Flex page (audio lengths, pitch from speed, frequency ratios), a beat-by-beat clash check "
            f"for every shift with suggested chords, groove cards (steady and half-time), an arrangement map of seven elements by six sections with a time table, a mix checklist, the 3-page project sheet "
            f"(overview, goals, vocabulary, requirements, steps, tips, submission checklist), the /{RUBRIC_TOTAL} rubric, a vocabulary page, a feedback planner and a reflection page ({n_student} pages)\n"
            f"• Teacher-presented intro deck, {ns} slides with speaker notes on every slide: a think-and-share hook, what the project is, the tempo ratio, seconds per bar, the circle of fifths, "
            f"the clash check, Smart Tempo and Flex, building it in Logic, the arrangement map, what to turn in and the rubric\n\n"
            f"THE THREE CLASS PERIODS\n"
            f"• Class 1: hook; match the tempo and the key; start the first melody\n"
            f"• Class 2: finish both melodies, check with Smart Tempo and Flex, layer them over a groove\n"
            f"• Class 3: arrange the six sections, mix, bounce, present and reflect\n\n"
            f"WHAT STUDENTS LEARN\n"
            f"• Tempo math: the ratio of two tempos (half-time and double-time are 2 : 1), a target tempo, percent change = (target ÷ original − 1) × 100, and seconds per bar in 4/4 = 240 ÷ BPM; a 44-bar track at 108 BPM lasts 97.78 seconds\n"
            f"• Key math: the semitone distance between two keys, the shorter direction (never more than 6), new key names and relative minors\n"
            f"• Building in Logic Pro: the Piano Roll, Transpose, Alchemy or Retro Synth, Drum Machine Designer, markers, automation and bounce; Smart Tempo, Flex Time, Flex Pitch and Session Players if your version has them\n"
            f"• Layering two melodies, mixing so both stay clear, and explaining their choices in a reflection\n\n"
            f"GOOD TO KNOW\n"
            f"• There is no audio in this resource and no student work. Both melodies are public domain and appear only as note charts; no lyrics are printed. Students make every sound themselves in Logic Pro\n"
            f"• Requires Logic Pro on a Mac. A MIDI keyboard is optional; students need only read the note chart. Where a control may differ between versions, the pages say \"if your version has it\"\n"
            f"• Rubric: 5 categories scored 1-5, /{RUBRIC_TOTAL}; the final grade is the average of the student's and the teacher's score\n"
            f"• Grades 9-12; music technology or music production classes\n"
            f"• The deck uses the free Oswald and Source Sans 3 fonts (built into Google Slides); install them for PowerPoint or Keynote, or present "
            f"the PDF copy, which shows the intended look\n"
            f"• Every student page prints well in black and white\n\n"
            f"Logic Pro is a product of Apple Inc., named only to describe compatibility. This resource is not affiliated with Apple.\n\n"
            f"Please leave a rating: you earn TpT credits for feedback, and it helps other teachers find this\n"
            f"Follow the Hudson Beat store for new music resources every week\n\n"
            f"{D.DISCLOSURE_NEW}")
    tbl = "; ".join(f"{b} BPM: {dshort(bar_len(b), 3)} s per bar, 44 bars {dec(total_s(b), 2)} s" for b in (96, 108, 120))
    md = f"""# UPLOAD: Holiday Mashup, original Logic Pro project (TpT 076)

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
({nt} characters; the limit is 80.) The title leaves out Holiday, Winter, Christmas and the song names because TpT's Seasonal Titles notice blocked a holiday-named title on 027 (see 032, 033 and 034); "Mashup Project" and "Match Tempo and Key" are the plain search phrases. "Logic Pro" is in the first 30 characters as a compatibility word.

## 2. Description

```
{desc}
```

## 3. Grades

9th, 10th, 11th, 12th (`9th-grade`, `10th-grade`, `11th-grade`, `12th-grade` in tpt.json), as tpt/METADATA-GUIDE.md prescribes for every music-production item.

## 4. Subjects and tags

- Subjects in tpt.json: Music; Computer Science - Technology; Music Composition (all three are in `tpt/SUBJECT-OPTIONS.json` and none is a heading)
- Tags in tpt.json: {", ".join(TAGS)} (five exact entries of `tpt/TAG-OPTIONS.json`, checked with `tools/tpt-validate.py`; the limit is 6). "Holiday" and "Student Practice" are headings and are not used; "Winter" and "Christmas-Chanukah-Kwanzaa" are real entries.
- Formats: PDF (add PowerPoint or ZIP if TpT offers it)
- Answer key: left out of tpt.json (there is none; the worked example is a model)

## 5. Resource type

- Projects
- Unit Plans
- PowerPoint Presentations

## 6. Standards (optional)

National Core Arts Standards, Music (Music Technology, high school): MU:Cr1.1, MU:Cr2.1, MU:Pr6.1, MU:Re7.2. Tag only if it matches how the teacher uses it.

## 7. Price

**${PRICE}** (paid), multiple-license price ${PRICE}. Inside the $8-12 holiday Logic kit range, for a kit with {np_} pages + {ns} slides, two note charts in two keys each, a tempo page, a key page, a Smart Tempo and Flex page, a beat-by-beat clash check, groove cards, an arrangement map and a two-page worked example, listed in late December.

## 8. Free or paid / free preview pages

Paid. Preview PDF (4 watermarked pages): the {CLASSES}-class pacing guide, the tempo page, the key page and the /{RUBRIC_TOTAL} rubric. "Number of pages or slides" is {np_ + ns} ({np_} pages + {ns} slides).

## 9. Sources and credits

- **Melody sources (public domain).** Jingle Bells: James Lord Pierpont, published September 16, 1857 by Oliver Ditson & Co., Boston, as "The One Horse Open Sleigh" (English Wikipedia, "Jingle Bells", fetched 23 Nov 2026); the familiar chorus is a later form that the same article dates to a recording from 1898 at the latest. Deck the Halls: a Welsh melody, dated by the same kind of source to the sixteenth century (English Wikipedia, "Deck the Halls"); the English words are by Thomas Oliphant, 1862. Both are far older than the 1930 cutoff, so the melodies are in the public domain. The charts (Jingle Bells: 16 bars of 4/4, 96 notes, G major; Deck the Halls: 16 bars of 4/4, 68 notes, F major) were typed from MusicXML files fetched from the Choral Public Domain Library (CPDL) on 23 Nov 2026 and are compared in `gen.py --check` with the typed scores: **Jingle Bells** with CPDL no. 38153 (John Brown, SAB, 4/4, G major, soprano line) and CPDL no. 66808 (William Hale, adapted to the modern tune, 2/4, A-flat major, moved down 1 semitone); **Deck the Halls** with CPDL no. 47663 (Andrew Sims, F major), CPDL no. 502 (Rafael Ornes, F major, top note of each chord; its first bar is empty on the staff read) and CPDL no. 39398 (James Gibb's edition of Charles Wood's harmonization, E-flat major, soprano, moved up 2). Differences found and kept in the check: the 4/4 Jingle Bells edition adds a D5 lyric pickup at the end of the verse (leading into the chorus) and after the fourth bar of the chorus (the chart leaves both out and writes the two held notes before them as half notes); the 2/4 edition splits some held notes into a note and a rest or re-strikes them (F#4, B4 and E4 in the verse, G4 at the end) and adds a D4 pickup in the verse; every pitch on the beats agrees. All three Deck the Halls scores agree with the chart on every pitch, start and length (the Ornes file has no top-line notes in bar 1). The editions carry their editors' CPDL licenses (Hale: personal use); nothing from them is copied except the pitches and lengths of the public-domain tunes. Also opened for key, meter or tempo marks only: CPDL no. 66801 (the 1857 edition, A-flat major, 2/4, 130 BPM) and CPDL no. 20578 (a Jingle Bells edition in F major, 100 BPM).
- **Keys and tempos.** Notated keys in the files read: Jingle Bells A-flat major (two editions), G major, F major; Deck the Halls F major (two editions) and E-flat major. Tempo marks in the files: Jingle Bells 80, 100, 130 and 144 BPM; Deck the Halls 96, 120 and 160 BPM. The kit says plainly that these vary and uses "typical class tempo" values of 120 and 96 BPM, which lie inside those ranges. The 4/4 Jingle Bells chart equals two bars of the 2/4 edition for one bar of 4/4 with the same quarter-note beat.
- **Lyrics and words.** Not printed. Only the titles and the facts above are given.
- **Art:** the cover, previews and deck use the library's mixing-console line art (`art/hero.png`, copied whole from `tpt/_art/library/mixing-console.png`; logged in `tpt/_art/USAGE.md`). Everything else, including every note, number, table, chart and drawing, is drawn or printed in code.
- **Music:** only the two public-domain melodies are notated. No recordings, artists or other arrangements are named or included. Students make every sound.
- **Fonts:** Oswald and Source Sans 3 (SIL OFL 1.1). Logic Pro is named only to describe compatibility.

## 10. Before you click publish

- [ ] **Needs QA approval first.** This is a new kit (not yet on TpT); the Manager releases it only after a QA `**Verdict: APPROVED**`. Season rule: build for late December; listing no sooner than the 2-8 week window allows.
- [ ] Cover and previews show "HUDSON BEAT" in type; PDF footers read "© 2026 Brian Lotze · Hudson Beat · For single-classroom use".
- [ ] No school name, logo, student names or work, audio, video, lyrics, song title other than the two tunes' own titles, or Logic session anywhere (`gen.py --check` scans every output and every file in this folder).
- [ ] **Neutral and secular.** The carols are treated as public-domain tunes: no religious teaching, no alcohol imagery, no brands, no real recordings. `gen.py --check` fails on religious, alcohol and holiday-specific words and on fragments of the lyrics.
- [ ] **Timing numbers (all recomputed in `gen.py --check`, exactly with fractions and again with an independent float method).** Seconds per beat = 60 / BPM; seconds per bar = beats x 60 / BPM (4/4: 240 / BPM). The track is 4 + 8 + 4 + 8 + 16 + 4 = 44 bars (sections start at bars 1, 5, 13, 17, 25, 41). Printed: {tbl}. Ratio 120 : 96 = 5 : 4; mean 108; percent changes −10% and +12.5%; audio length changes +11.11% and −11.11%; 8 bars last 16.00, 17.78 and 20.00 s at 120, 108 and 96 BPM.
- [ ] **Keys (recomputed in `gen.py --check`).** G down to F is −2 (up 10); the shorter move is never more than 6; the circle of fifths positions, key signatures and relative minors of all 12 keys; the shorter shift for all 144 key pairs; three target keys.
- [ ] **Clash check (recomputed in `gen.py --check` by two independent loops).** At the key-matched shift (−2) the 64 beats split 45 smooth, 14 mild and 5 hard; every other shift from −6 to +5 has more hard clashes; a target of G gives the same counts. It is a quick check, labeled as one on the page.
- [ ] **Original project.** Built with `ORIGINAL = True` in `tpt/_dmp2_common/dmp2.py` (like 031, 036, 053, 057, 061, 063, 067 and 070): no "what changed" page and the new disclosure line. The reflection page is the shared Reflection element, scored in the rubric's "Plan & Reflection" row. `dmp2.py` is unchanged; the deck's three-classes badge and the terms-page thank-you note are applied inside `gen.py`.
- [ ] **Logic Pro names to confirm on a Mac with a current Logic.** Piano Roll (middle C is C3 in Logic and C4 on the chart), Transpose in the region inspector, Smart Tempo, Flex Time and Flex Pitch (all "if your version has it", with "look in the region or track inspector" and no invented menu paths), Bounce in Place (hedged), Alchemy and Retro Synth, Drum Machine Designer, Session Players (hedged), the Marker global track with a plus (+) button and a Create Marker key command (hedged), the Mixer (X), automation (A), Bounce (Command-B) and Compress in Finder.
- [ ] **Open questions for the owner:** (1) **Title.** No Holiday, Winter or song name in the title because of TpT's seasonal-title notice (see 1). (2) **Price.** ${PRICE}, inside the $8-12 range. (3) **Classes.** Three periods; the pacing page shows two and four. (4) **Typical tempos.** 120 and 96 BPM are class choices inside the range of published tempo marks, stated as such. (5) **Editions.** The notes were compared with CPDL editions that carry their editors' own licenses; confirm you are comfortable with the sources line in section 9.
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


if __name__ == "__main__":
    if "--check" not in sys.argv:
        write_upload()
        D.deck_art = deck_art_transparent
    D.main(sys.modules[__name__])
