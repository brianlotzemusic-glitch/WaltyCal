#!/usr/bin/env python3
"""Winter Recorder Songbook, B-A-G (TpT 055): build the resource and verify it.

    python3 gen.py           build everything (PDFs, PNGs, UPLOAD.md, tpt.json) into this folder
    python3 gen.py --check   re-read every drawn staff and fingering diagram from the rendered HTML and verify them

Notation: every tune is a list of bars of (pitch, duration) events using only B4, A4, G4 (written pitches; a soprano recorder sounds one
octave higher). Staves and diagrams are drawn as SVG. `--check` does not trust the data: it parses the rendered SVG of every staff
(lines, noteheads, stems, beams, rests, barlines, letters), derives each pitch from the notehead position and compares it with the tune
data, adds up every bar for the time signature, and re-reads every fingering diagram hole by hole against the B/A/G table.
The two public-domain tunes are stored twice: typed in C major (primary) and as a second letter transcription in G, which must agree
with the primary transposed up a fifth by code.
"""
import json
import math
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from html import escape

HERE = os.path.dirname(os.path.abspath(__file__))
TPT = os.path.dirname(HERE)
FONTS = os.path.join(TPT, "fonts")
BUILD = os.path.join(HERE, "build")
RENDER_JS = os.path.join(TPT, "tools", "render.js")
HERO = os.path.join(HERE, "art", "hero.png")

SLUG = "winter-recorder-songbook-b-a-g"
PDF = os.path.join(HERE, f"{SLUG}.pdf")
PREVIEW_PDF = os.path.join(HERE, f"{SLUG}-PREVIEW.pdf")
COVER_PNG = os.path.join(HERE, "cover.png")
PREVIEW_PNGS = [os.path.join(HERE, f"preview-{i}.png") for i in (1, 2, 3)]
UPLOAD = os.path.join(HERE, "UPLOAD.md")
TPT_JSON = os.path.join(HERE, "tpt.json")

STORE = "Brian Lotze"
BRAND = "Hudson Beat"
YEAR = 2026
ACCENT = "#2F86B8"
TINT = "#DCEEF8"
DISCLOSURE = "Created with the help of digital and AI tools. Notation and answer keys are verified before release."
TITLE = "Winter Recorder Songbook"
LISTING_TITLE = "Beginner Recorder Songbook: B-A-G Songs, Fingering Charts, Practice Checklist"
PREFERRED_TITLE = "Winter Recorder Songbook: B-A-G Songs, Fingering Charts & Practice Checklist"
PRICE = "4.00"
TAGS = ["Winter", "Songs", "Printables", "Activities", "Worksheets", "Assessment"]
SUBJECTS = ["Music", "Instrumental Music"]
GRADES = ["3rd-grade", "4th-grade", "5th-grade"]

# ------------------------------------------------------------------ music data
STEP = {"G": 2, "A": 3, "B": 4}                 # staff step above the bottom line (E4 = 0); treble clef
LETTER_OF_STEP = {2: "G", 3: "A", 4: "B"}
BEATS = {"q": 1.0, "h": 2.0, "w": 4.0, "e": 0.5, "r": 1.0}
DUR_NAME = {"q": "quarter note", "h": "half note", "w": "whole note", "e": "eighth note", "r": "quarter rest"}
# Baroque (English) fingering, soprano recorder: holes T (thumb, back) and 1-7 (front); 1-3 left hand, 4-7 right hand
FINGERING = {"B": {"T", "1"}, "A": {"T", "1", "2"}, "G": {"T", "1", "2", "3"}}
HOLES = ["T", "1", "2", "3", "4", "5", "6", "7"]


def parse_bars(s):
    bars = []
    for b in s.split("|"):
        row = []
        for tok in b.split():
            row.append(("r", "r") if tok[0] == "-" else (tok[0], tok[1]))   # (letter or 'r', duration)
        bars.append(row)
    return bars


# public-domain tunes: PRIMARY typed in C major, SECOND = independent letter transcription in G (as printed in recorder lessons)
PD_PRIMARY_C = {
    "T3": "Cq Cq Cq Dq | Eh Dh | Cq Eq Dq Dq | Cw",
    "T7": "Eq Dq Ch | Eq Dq Ch | Ce Ce Ce Ce De De De De | Eq Dq Ch",
}
PD_SECOND_G = {"T3": "GGGABAGBAAG", "T7": "BAGBAGGGGGAAAABAG"}
C_TO_G = {"C": "G", "D": "A", "E": "B"}          # up a perfect fifth, C4 D4 E4 -> G4 A4 B4


def transpose_bars_c_to_g(bars):
    return [[(C_TO_G[p] if p != "r" else "r", d) for p, d in bar] for bar in bars]


TUNES = [
    {"id": "T1", "n": 1, "title": "Snow Settles", "kind": "original", "meter": 4, "letters": True, "bpm": 60, "bars": "Bw | Bh Ah | Gh Ah | Gw",
     "tongue": "Say a soft \"too\" on every note. Hold the whole note for four counts without changing your breath.",
     "breath_after": [2], "breath": "Take one easy breath at the start and another after bar {A}."},
    {"id": "T2", "n": 2, "title": "Mitten Walk", "kind": "original", "meter": 4, "letters": True, "bpm": 66,
     "bars": "Gq Aq Bq Aq | Gq Aq Bh | Bq -q Aq -q | Gh Ah | Bq Bq Aq Aq | Gq Aq Bq -q | Aq Bq Aq Gq | Gw",
     "tongue": "Tongue each quarter note with a gentle \"too\". On a rest, stop the air and keep counting.",
     "breath_after": [3, 6], "breath": "Breathe after bars {A}, where the bar ends on a quarter rest, not in the middle of a phrase."},
    {"id": "T3", "n": 3, "title": "Au Clair de la Lune", "kind": "public domain", "meter": 4, "letters": True, "bpm": 72, "bars": None,
     "source": "Traditional French tune, 18th century, composer unknown (first phrase). Public domain.",
     "tongue": "Repeat the same note with a fresh \"too\" each time, with a little space between notes.",
     "breath_after": [2], "breath": "Play the four bars in one breath, or breathe after bar {A}, on the half note."},
    {"id": "T4", "n": 4, "title": "Frosty Window", "kind": "original", "meter": 3, "letters": True, "bpm": 72,
     "bars": "Bh Gq | Ah Gq | Bq Aq Gq | Ah -q | Gq Aq Bq | Bh Aq | Aq Gq Aq | Gh -q",
     "tongue": "Count 1-2-3 and tongue the first beat of every bar a little more clearly.",
     "breath_after": [4, 8], "breath": "Breathe after bars {A}, where each bar ends on a quarter rest."},
    {"id": "T5", "n": 5, "title": "Icicle Steps", "kind": "original", "meter": 4, "letters": False, "bpm": 66,
     "bars": "Aw | Bh Bh | Aq Gq Gh | Bq Aq Bq Aq | Gh Gh | Aq Aq Bh | Bq Aq Gq Aq | Gw",
     "tongue": "Keep every \"too\" the same length and softness, like drops falling one by one.",
     "breath_after": [3, 6], "breath": "Breathe after bars {A}, where each bar ends on a half note."},
    {"id": "T6", "n": 6, "title": "Cocoa Break", "kind": "original", "meter": 4, "letters": False, "bpm": 66,
     "bars": "Gq -q Gq -q | Aq Aq Bh | Bq -q Aq -q | Gh Gh | Aq Gq Aq Bq | Bq -q Bq -q | Aq Aq Gq Aq | Gw",
     "tongue": "Make the notes before each rest short and crisp, then listen to the silence.",
     "breath_after": [3, 6], "breath": "Breathe after bars {A}, where each bar ends on a quarter rest."},
    {"id": "T7", "n": 7, "title": "Hot Cross Buns", "kind": "public domain", "meter": 4, "letters": False, "bpm": 72, "bars": None,
     "source": "Traditional English street cry. In print by 1733. Public domain.",
     "tongue": "Each pair of eighth notes is two quick \"too-too\" taps in the time of one beat. Keep them light and even.",
     "breath_after": [2, 4], "breath": "Breathe after bars {A}, on the half notes. Bar 3 ends on a quick eighth note, so keep playing through it."},
    {"id": "T8", "n": 8, "title": "Skating Pond", "kind": "original", "meter": 4, "letters": False, "bpm": 72,
     "bars": "Gq Aq Bh | Be Be Ae Ae Gh | Gq Aq Ae Ae Gq | Bh Aq -q | Gq Gq Ge Ge Aq | Aq Bq Be Be Aq | Be Be Aq Gq Aq | Gw",
     "tongue": "Eighth notes are quick and light: think \"too-too\" for each pair, then settle back to \"too\".",
     "breath_after": [2, 4], "breath": "Breathe after bars {A}, on the half note and on the quarter rest."},
]
for _t in TUNES:
    if _t["id"] in PD_PRIMARY_C:
        _t["bars_c"] = parse_bars(PD_PRIMARY_C[_t["id"]])
        _t["bars"] = transpose_bars_c_to_g(_t["bars_c"])
        _t["second"] = PD_SECOND_G[_t["id"]]
    else:
        _t["bars"] = parse_bars(_t["bars"])
    _t["breath"] = _t["breath"].replace("{A}", " and ".join([", ".join(map(str, _t["breath_after"][:-1])), str(_t["breath_after"][-1])]) if len(_t["breath_after"]) > 1 else str(_t["breath_after"][0]))
TUNE = {t["id"]: t for t in TUNES}
FAMOUS_CELLS = ["BAGABBB", "BAGBAG", "GGGAB", "BBBBBB", "AAABBB"]   # known tunes the ORIGINAL tunes must not contain


def breath_ok_bars(bars):
    """1-based bars whose last event is a rest or a note of at least two beats."""
    return [i + 1 for i, b in enumerate(bars) if b[-1][0] == "r" or BEATS[b[-1][1]] >= 2.0]


def tune_letters(t):
    return "".join(p for bar in t["bars"] for p, d in bar if p != "r")


def bar_len(bar):
    return sum(BEATS[d] for _, d in bar)


def interval_word(a, b):
    d = abs(STEP[a] - STEP[b])
    return "repeat" if d == 0 else "step" if d == 1 else "skip"


# quiz data
Q_NAMES = [("B", "q"), ("G", "h"), ("A", "q"), ("B", "w"), ("A", "h"), ("G", "q"), ("G", "w"), ("B", "h"), ("A", "q"), ("B", "q"), ("G", "h"), ("A", "w")]
Q_FING = ["A", "G", "B", "G", "A", "B"]
Q_DRAW = [("A", "q"), ("G", "h"), ("B", "q"), ("B", "w"), ("G", "q"), ("A", "h"), ("B", "h"), ("G", "w")]
Q_PAIRS = [("B", "A"), ("G", "B"), ("A", "A"), ("G", "A"), ("B", "G"), ("B", "B")]


# ------------------------------------------------------------------ drawing helpers
HEAD_W = {"q": 1.18, "h": 1.18, "e": 1.18, "w": 1.688}
REST_W = 1.08
G_HEAD, G_HALF, G_WHOLE = 0xE0A4, 0xE0A3, 0xE0A2
G_QREST, G_TREBLE, G_TS = 0xE4E5, 0xE050, 0xE080
STEM_X = 0.168


def fx(v):
    return f"{v:.2f}"


def gl(cp, x, y, size, cls="", fill="#000", extra=""):
    c = f' class="{cls}"' if cls else ""
    return f'<text{c} x="{fx(x)}" y="{fx(y)}" font-family="Bravura" font-size="{fx(size)}" fill="{fill}"{extra}>&#x{cp:X};</text>'


def snowflake(cx, cy, r, color="#000", sw=1.3):
    out = []
    for k in range(6):
        a = math.radians(60 * k - 90)
        ex, ey = cx + r * math.cos(a), cy + r * math.sin(a)
        out.append(f'<line x1="{cx:.2f}" y1="{cy:.2f}" x2="{ex:.2f}" y2="{ey:.2f}"/>')
        bx, by = cx + 0.58 * r * math.cos(a), cy + 0.58 * r * math.sin(a)
        for da in (-50, 50):
            b = math.radians(60 * k - 90 + da)
            out.append(f'<line x1="{bx:.2f}" y1="{by:.2f}" x2="{bx + 0.34 * r * math.cos(b):.2f}" y2="{by + 0.34 * r * math.sin(b):.2f}"/>')
    return f'<g stroke="{color}" stroke-width="{sw}" stroke-linecap="round" fill="none">{"".join(out)}</g>'


def staff_lines(x1, x2, top, S):
    return "".join(f'<line class="sl" x1="{fx(x1)}" y1="{fx(top + i * S)}" x2="{fx(x2)}" y2="{fx(top + i * S)}" stroke="#000" stroke-width="{fx(0.1 * S)}"/>' for i in range(5))


def note_events(bar, xl, W, pad=7.0):
    """x centre of each event of a bar; durations are laid out in proportion to beats."""
    total = sum(BEATS[d] for _, d in bar)
    unit = (W - 2 * pad) / total
    cur = xl + pad
    xs = []
    for _, d in bar:
        w = BEATS[d] * unit
        xs.append(cur + min(w, unit) / 2)
        cur += w
    return xs


def head_svg(letter, dur, cx, top, S, beam_end=None, label=None, label_y=None, blank=False):
    """One pitched event: head + stem (down for B4 and higher, up below) + optional letter or blank line. Returns (svg, y)."""
    step = STEP[letter]
    bottom = top + 4 * S
    y = bottom - step * S / 2
    hw = HEAD_W[dur] * S
    left = cx - hw / 2
    sw = 0.13 * S
    o = [f'<g class="ev" data-kind="{dur}">']
    o.append(gl({"h": G_HALF, "w": G_WHOLE}.get(dur, G_HEAD), left, y, 4 * S, "head"))
    if dur != "w":
        down = step >= 4
        if down:
            sx = left + sw / 2
            y1 = y + STEM_X * S
            y2 = beam_end if beam_end is not None else y1 + 3.5 * S
        else:
            sx = left + hw - sw / 2
            y1 = y - STEM_X * S
            y2 = beam_end if beam_end is not None else y1 - 3.5 * S
        o.append(f'<line class="stem" x1="{fx(sx)}" y1="{fx(y1)}" x2="{fx(sx)}" y2="{fx(y2)}" stroke="#000" stroke-width="{fx(sw)}"/>')
    o.append("</g>")
    ly = bottom + 3.9 * S
    if label:
        o.append(f'<text class="let" x="{fx(cx)}" y="{fx(ly)}" text-anchor="middle" font-family="Source Sans 3, sans-serif" font-weight="700" font-size="{fx(1.3 * S)}">{label}</text>')
    elif blank:
        o.append(f'<line class="blank" x1="{fx(cx - 0.75 * S)}" y1="{fx(ly)}" x2="{fx(cx + 0.75 * S)}" y2="{fx(ly)}" stroke="#000" stroke-width="0.8"/>')
    return "".join(o), y


def bar_svg(bar, xl, W, top, S, letters, blanks):
    """Draw the events of one bar (beamed eighth pairs, rests); returns svg string."""
    o = []
    bottom = top + 4 * S
    xs = note_events(bar, xl, W)
    i = 0
    while i < len(bar):
        p, d = bar[i]
        if d == "r":
            o.append(f'<g class="ev" data-kind="r">{gl(G_QREST, xs[i] - REST_W * S / 2, top + 2 * S, 4 * S, "rest")}</g>')
            i += 1
        elif d == "e":
            (p2, d2) = bar[i + 1]
            assert d2 == "e"
            ys = [bottom - STEP[p] * S / 2, bottom - STEP[p2] * S / 2]
            down = STEP[p] >= 4
            assert (STEP[p2] >= 4) == down, "mixed stem directions in a beamed pair"
            hw = HEAD_W["e"] * S
            sw = 0.13 * S
            if down:
                beam_end = max(ys) + STEM_X * S + 3.5 * S
            else:
                beam_end = min(ys) - STEM_X * S - 3.5 * S
            for (pp, _), cx in ((bar[i], xs[i]), (bar[i + 1], xs[i + 1])):
                s_, _y = head_svg(pp, "e", cx, top, S, beam_end=beam_end, label=pp if letters else None, blank=blanks)
                o.append(s_)
            if down:
                bx1, bx2 = xs[i] - hw / 2, xs[i + 1] - hw / 2 + sw
                by = beam_end - 0.5 * S
            else:
                bx1, bx2 = xs[i] + hw / 2 - sw, xs[i + 1] + hw / 2
                by = beam_end
            o.append(f'<rect class="beam" x="{fx(bx1)}" y="{fx(by)}" width="{fx(bx2 - bx1)}" height="{fx(0.5 * S)}" fill="#000"/>')
            i += 2
        else:
            s_, _y = head_svg(p, d, xs[i], top, S, label=p if letters else None, blank=blanks)
            o.append(s_)
            i += 1
    return "".join(o)


def tune_system_svg(tid, sys_idx, bars, meter, letters, blanks, w=514.0, S=7.6, first=True, last=False, bar0=1):
    top = 2.4 * S
    bottom = top + 4 * S
    h = bottom + 5.3 * S
    x_clef = 8.0
    bars_x0 = x_clef + (4.9 if not first else 7.4) * S
    x_end = w - 7.0
    W = (x_end - bars_x0) / len(bars)
    o = [f'<svg class="ns" data-kind="tune" data-id="{tid}" data-sys="{sys_idx}" data-meter="{meter}" data-x0="{fx(bars_x0)}" data-s="{fx(S)}" data-bar0="{bar0}" '
         f'xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.0f} {h:.1f}" width="{w:.0f}pt" height="{h:.1f}pt" style="display:block">']
    o.append(staff_lines(x_clef - 3, x_end, top, S))
    o.append(gl(G_TREBLE, x_clef, bottom - S, 4 * S, "clef"))
    if first:
        o.append(f'<g class="timesig">{gl(G_TS + meter, x_clef + 3.0 * S, top + 2 * S, 4 * S)}{gl(G_TS + 4, x_clef + 3.0 * S, top + 4 * S, 4 * S)}</g>')
    for bi, bar in enumerate(bars):
        xl = bars_x0 + bi * W
        o.append(bar_svg(bar, xl, W, top, S, letters, blanks))
        bx = xl + W
        if not (last and bi == len(bars) - 1):
            o.append(f'<line class="bar" x1="{fx(bx)}" y1="{fx(top)}" x2="{fx(bx)}" y2="{fx(bottom)}" stroke="#000" stroke-width="{fx(0.14 * S)}"/>')
        else:
            o.append(f'<line class="bar" x1="{fx(bx - 0.35 * S)}" y1="{fx(top)}" x2="{fx(bx - 0.35 * S)}" y2="{fx(bottom)}" stroke="#000" stroke-width="{fx(0.14 * S)}"/>')
            o.append(f'<rect class="fin" x="{fx(bx - 0.18 * S)}" y="{fx(top)}" width="{fx(0.36 * S)}" height="{fx(4 * S)}" fill="#000"/>')
    o.append("</svg>")
    return "".join(o)


def tune_systems(t):
    bars = t["bars"]
    per = 2 if len(bars) == 4 else 4
    out = []
    for si in range(0, len(bars), per):
        chunk = bars[si:si + per]
        out.append(tune_system_svg(t["id"], si // per + 1, chunk, t["meter"], t["letters"], not t["letters"], first=(si == 0),
                                   last=(si + per >= len(bars)), bar0=si + 1))
    return out


def quiz_staff_svg(kind, notes, qid, w=150.0, S=8.0, label=False, blank=False, ans=None):
    """A single-system staff with one or two notes (kind quiz/blank/keynote/pair/keypair). No time signature, no bar lines."""
    top = 1.75 * S
    bottom = top + 4 * S
    h = bottom + 2.4 * S
    x_clef = 8.0
    x0 = x_clef + 4.4 * S
    x_end = w - 7.0
    o = [f'<svg class="ns" data-kind="{kind}" data-id="{qid}" data-s="{fx(S)}" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.0f} {h:.1f}" width="{w:.0f}pt" height="{h:.1f}pt" style="display:block">']
    o.append(staff_lines(x_clef - 3, x_end, top, S))
    o.append(gl(G_TREBLE, x_clef, bottom - S, 4 * S, "clef"))
    n = len(notes)
    if n:
        W = x_end - x0
        for i, (p, d) in enumerate(notes):
            cx = x0 + W * (i + 0.5) / n
            s_, _ = head_svg(p, d, cx, top, S)
            o.append(s_)
    o.append("</svg>")
    return "".join(o)


# ------------------------------------------------------------------ fingering diagrams
FG_W, FG_H = 150.0, 352.0
HOLE_Y = {"T": 78.0, "1": 92.0, "2": 124.0, "3": 156.0, "4": 196.0, "5": 228.0, "6": 262.0, "7": 290.0}
FG_CX = 66.0


def fingering_svg(note, uid, hands=True):
    cov = FINGERING[note]
    cx = FG_CX
    o = [f'<svg class="fg" data-note="{note}" data-id="{uid}" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {FG_W:.0f} {FG_H:.0f}" style="display:block">']
    # mouthpiece, window, body, bell (stroke 2)
    o.append(f'<path class="body" d="M{cx - 9},10 L{cx + 9},10 L{cx + 17},44 L{cx + 17},308 L{cx + 23},334 L{cx - 23},334 L{cx - 17},308 L{cx - 17},44 Z" fill="#fff" stroke="#000" stroke-width="2" stroke-linejoin="round"/>')
    o.append(f'<rect class="window" x="{cx - 8}" y="34" width="16" height="14" rx="2" fill="#fff" stroke="#000" stroke-width="1.6"/>')
    o.append(f'<line x1="{cx - 17}" y1="56" x2="{cx + 17}" y2="56" stroke="#000" stroke-width="1.6"/>')
    # thumb hole (back of the recorder), drawn beside the body with a dashed link
    o.append(f'<line x1="{cx - 17}" y1="{HOLE_Y["T"]}" x2="24" y2="{HOLE_Y["T"]}" stroke="#555" stroke-width="1.2" stroke-dasharray="3 3"/>')

    def hole(h, hx, hy, r):
        c = h in cov
        return (f'<circle class="hole" data-hole="{h}" data-cov="{1 if c else 0}" cx="{hx}" cy="{hy}" r="{r}" '
                f'fill="{"#000" if c else "#fff"}" stroke="#000" stroke-width="1.8"/>')

    o.append(hole("T", 20, HOLE_Y["T"], 8))
    o.append(f'<text x="20" y="{HOLE_Y["T"] - 14}" text-anchor="middle" font-family="Oswald" font-weight="500" font-size="9">THUMB</text>')
    o.append(f'<text x="20" y="{HOLE_Y["T"] + 22}" text-anchor="middle" font-family="Source Sans 3" font-style="italic" font-size="8.5">(back)</text>')
    for h in "12345":
        o.append(hole(h, cx, HOLE_Y[h], 8.5 if h in "123" else 7.5))
    for h in "67":                      # holes 6 and 7 are double holes
        o.append(hole(h, cx - 6.5, HOLE_Y[h], 4.6))
        o.append(hole(h, cx + 6.5, HOLE_Y[h], 4.6))
    for h in "1234567":
        o.append(f'<text x="{cx + 30}" y="{HOLE_Y[h] + 4}" font-family="Oswald" font-weight="700" font-size="12">{h}</text>')
    if hands:
        for (ya, yb, lab) in ((84, 164, "LEFT HAND"), (188, 298, "RIGHT HAND")):
            o.append(f'<path d="M{cx + 48},{ya} L{cx + 52},{ya} L{cx + 52},{yb} L{cx + 48},{yb}" fill="none" stroke="#000" stroke-width="1.4" stroke-linejoin="round"/>')
            o.append(f'<text transform="translate({cx + 66},{(ya + yb) / 2}) rotate(-90)" text-anchor="middle" font-family="Oswald" font-weight="500" font-size="10" letter-spacing=".06em">{lab}</text>')
    o.append("</svg>")
    return "".join(o)


# ------------------------------------------------------------------ CSS and page frame
def font_css():
    f = os.path.relpath(FONTS, BUILD)
    faces = [("Oswald", 300, "normal", "oswald-latin-300-normal"), ("Oswald", 500, "normal", "oswald-latin-500-normal"),
             ("Oswald", 700, "normal", "oswald-latin-700-normal"),
             ("Source Sans 3", 400, "normal", "source-sans-3-latin-400-normal"), ("Source Sans 3", 400, "italic", "source-sans-3-latin-400-italic"),
             ("Source Sans 3", 600, "normal", "source-sans-3-latin-600-normal"), ("Source Sans 3", 700, "normal", "source-sans-3-latin-700-normal"),
             ("Bravura", 400, "normal", "bravura")]
    return "".join(f"@font-face{{font-family:'{n}';font-weight:{w};font-style:{s};src:url('{f}/{file}.woff2') format('woff2');}}" for n, w, s, file in faces)


CSS = """
@page { size: 8.5in 11in; margin: 0; }
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; background: #fff; color: #000; }
body { font-family: 'Source Sans 3', sans-serif; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
.page { width: 8.5in; height: 11in; position: relative; overflow: hidden; page-break-after: always; break-after: page;
        padding: 0.42in 0.5in 0.38in; display: flex; flex-direction: column; }
.page:last-child { page-break-after: auto; break-after: auto; }
.h { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; letter-spacing: .01em; line-height: 1; }
.l { font-family: 'Oswald'; font-weight: 300; }
.top { display: flex; justify-content: space-between; align-items: flex-end; border-bottom: 2.2pt solid #000; padding-bottom: 6pt; }
.top .t { font-size: 22pt; white-space: nowrap; }
.top .tag { flex: none; white-space: nowrap; }
.top .t small { display: block; font-family: 'Oswald'; font-weight: 300; text-transform: none; font-size: 12pt; letter-spacing: 0; margin-top: 4pt; }
.top .deco { flex: 1; display: flex; justify-content: center; align-items: center; padding-bottom: 2pt; overflow: hidden; }
.tag { text-align: right; }
.tag .lv { display: inline-block; background: #000; color: #fff; font-family: 'Oswald'; font-weight: 700; font-size: 15pt; padding: 3pt 9pt 4pt; border-radius: 4pt; letter-spacing: .04em; }
.tag .lv.ak { background: ACCENT; }
.tag .ln { font-family: 'Oswald'; font-weight: 300; font-size: 11pt; margin-top: 3pt; }
.name { display: flex; gap: 18pt; font-size: 12pt; margin: 9pt 0 5pt; }
.name span { flex: 1; border-bottom: 1pt solid #000; height: 15pt; }
.name span.d { flex: 0 0 1.6in; }
.how { font-size: 11.5pt; margin: 2pt 0 6pt; line-height: 1.3; text-wrap: pretty; }
.foot { display: flex; justify-content: space-between; font-size: 8.5pt; color: #333; border-top: .8pt solid #000; padding-top: 3pt; }
.wm { position: absolute; left: 50%; top: 50%; transform: translate(-50%, -50%) rotate(-38deg); font-family: 'Oswald'; font-weight: 700;
      font-size: 150pt; color: rgba(0,0,0,.13); letter-spacing: .06em; white-space: nowrap; pointer-events: none; z-index: 9; }
.doc h1 { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 30pt; margin: 0 0 4pt; line-height: 1; }
.doc h2 { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 14pt; margin: 9pt 0 3pt; letter-spacing: .02em; }
.doc p, .doc li { font-size: 10.6pt; line-height: 1.34; margin: 0 0 5pt; }
.doc ul { margin: 0 0 4pt; padding-left: 16pt; }
.doc .rule { border-bottom: 2.2pt solid #000; margin-bottom: 8pt; padding-bottom: 6pt; }
.doc table { border-collapse: collapse; width: 100%; table-layout: fixed; font-size: 10pt; margin: 2pt 0 4pt; }
.doc td, .doc th { border: 1pt solid #000; padding: 3.5pt 6pt; text-align: left; vertical-align: top; }
.doc th { font-family: 'Oswald'; font-weight: 500; text-transform: uppercase; font-size: 9.5pt; background: #000; color: #fff; }
.small { font-size: 9pt !important; color: #333; }
.facts td, .facts th { padding: 1.5pt 6pt !important; font-size: 9.5pt; }
.box { border: 1.3pt solid #000; border-radius: 7pt; padding: 7pt 10pt 5pt; }
.steps { display: flex; gap: 12pt; margin-top: 8pt; }
.step { flex: 1; border: 1.3pt solid #000; border-radius: 7pt; padding: 7pt 9pt 4pt; }
.step .n { display: inline-block; background: ACCENT; color: #fff; font-family: 'Oswald'; font-weight: 700; font-size: 12pt; border-radius: 50%; width: 20pt; height: 20pt; line-height: 20pt; text-align: center; margin-right: 5pt; }
.step b { font-family: 'Oswald'; font-weight: 500; text-transform: uppercase; font-size: 11.5pt; letter-spacing: .02em; }
.step p { margin: 4pt 0 3pt !important; font-size: 10.5pt !important; line-height: 1.3 !important; }
.fgrow { display: flex; justify-content: space-between; gap: 22pt; margin-top: 10pt; }
.fgcol { flex: 1; border: 1.3pt solid #000; border-radius: 7pt; padding: 8pt 8pt 6pt; display: flex; flex-direction: column; align-items: center; }
.fgcol .nm { font-family: 'Oswald'; font-weight: 700; font-size: 34pt; line-height: 1; }
.fgcol .cv { font-size: 10.5pt; text-align: center; margin: 4pt 0 0; line-height: 1.3; }
.fgcol svg { display: block; margin: 4pt 0; width: 120pt; height: auto; }
.tunes { flex: 1; display: flex; flex-direction: column; justify-content: space-between; padding: 4pt 0 12pt; }
.tune { border: 1.3pt solid #000; border-radius: 9pt; padding: 7pt 10pt 4pt; }
.tune .th { display: flex; align-items: center; gap: 9pt; }
.tune .num { background: #000; color: #fff; font-family: 'Oswald'; font-weight: 700; font-size: 17pt; border-radius: 5pt; padding: 2pt 8pt 3pt; }
.tune .tt { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 18pt; letter-spacing: .01em; }
.tune .bd { margin-left: auto; font-family: 'Oswald'; font-weight: 500; font-size: 10pt; letter-spacing: .08em; text-transform: uppercase; border: 1.2pt solid ACCENT; color: ACCENT; border-radius: 10pt; padding: 1pt 8pt; }
.tune .info { font-size: 10pt; margin: 3pt 0 1pt; line-height: 1.3; }
.tune .info b { font-weight: 700; }
.tune .src { font-size: 8.5pt; color: #333; font-style: italic; margin: 1pt 0 0; }
.ticks { display: flex; gap: 14pt; align-items: center; font-size: 10pt; margin: 2pt 0 4pt; }
.cb { display: inline-block; width: 11pt; height: 11pt; border: 1.3pt solid #000; border-radius: 2pt; vertical-align: -2pt; margin-right: 4pt; }
.ck table { width: 100%; border-collapse: collapse; table-layout: fixed; margin-top: 8pt; }
.ck td, .ck th { border: 1pt solid #000; padding: 0 6pt; height: 28pt; font-size: 11pt; vertical-align: middle; }
.ck th { background: #000; color: #fff; font-family: 'Oswald'; font-weight: 500; font-size: 10pt; letter-spacing: .04em; text-transform: uppercase; height: 24pt; text-align: center; }
.ck td.c { text-align: center; }
.ck td .cb { margin: 0; }
.ck h3 { font-family: 'Oswald'; font-weight: 700; font-size: 14pt; text-transform: uppercase; margin: 14pt 0 0; }
.ck.tk td { height: 42pt; }
.qgrid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10pt 12pt; margin-top: 6pt; }
.qgrid.three { grid-template-columns: repeat(3, 1fr); gap: 10pt 12pt; }
.q { border: 1.1pt solid #000; border-radius: 6pt; padding: 4pt 7pt 5pt; }
.q .qn { font-family: 'Oswald'; font-weight: 700; font-size: 11pt; }
.q .ans { border-bottom: 1pt solid #000; height: 15pt; margin: 3pt 0 0; font-size: 9.5pt; display: flex; align-items: flex-end; gap: 7pt; }
.qh { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 14pt; margin: 10pt 0 0; display: flex; align-items: baseline; gap: 8pt; }
.qh span { font-family: 'Source Sans 3'; font-weight: 400; text-transform: none; font-size: 10.5pt; }
.fgq { display: flex; gap: 14pt; justify-content: space-between; margin-top: 6pt; }
.fgq .q { flex: 1; display: flex; flex-direction: column; align-items: center; }
.fgq svg { display: block; width: 62pt; margin: 2pt 0; }
.kgrid { display: flex; flex-wrap: wrap; gap: 5pt 14pt; font-size: 12pt; margin: 5pt 0; }
.kgrid span b { font-family: 'Oswald'; font-weight: 700; }
.krow { display: grid; grid-template-columns: 70pt 1fr; gap: 6pt; font-size: 11.5pt; line-height: 1.45; padding: 2pt 0; border-bottom: .5pt solid #bbb; }
.krow b { font-family: 'Oswald'; font-weight: 700; color: ACCENT; text-transform: uppercase; }
.krow .kb { white-space: nowrap; }
.kdraw { display: grid; grid-template-columns: repeat(4, 1fr); gap: 2pt 8pt; margin-top: 2pt; }
.kdraw div { font-size: 10pt; text-align: center; }
.cover { align-items: center; justify-content: space-between; padding: 0.55in 0.6in 0.5in; }
.store { font-family: 'Oswald'; font-weight: 500; font-size: 13pt; letter-spacing: .32em; text-transform: uppercase; }
.ctitle { text-align: center; }
.ctitle .a { font-family: 'Oswald'; font-weight: 700; font-size: 40pt; line-height: 1; letter-spacing: .02em; }
.ctitle .b { font-family: 'Oswald'; font-weight: 700; white-space: nowrap; font-size: 72pt; line-height: .95; letter-spacing: .01em; }
.ctitle .c { font-family: 'Oswald'; font-weight: 300; font-size: 17pt; margin-top: 8pt; }
.cband { width: 100%; background: #000; color: #fff; text-align: center; font-family: 'Oswald'; font-weight: 500; font-size: 14pt;
         letter-spacing: .08em; text-transform: uppercase; padding: 8pt 0 9pt; border-radius: 4pt; }
.cband em { font-style: normal; color: ACCENT; }
""".replace("ACCENT", ACCENT)


def html_doc(pages, title="doc"):
    return (f'<!doctype html><html><head><meta charset="utf-8"><title>{escape(title)}</title><style>{font_css()}{CSS}</style></head>'
            f'<body>{"".join(pages)}</body></html>')


def foot(left, right):
    return f'<div class="foot"><span>{left}</span><span>{right}</span></div>'


COPY = f"© {YEAR} {STORE} · {BRAND} · For single-classroom use"

# ------------------------------------------------------------------ page numbers (single source of truth)
P_COVER, P_TEACH, P_FING = 1, 2, 3
P_TUNE0 = 4                      # tune pages 4-7, two tunes each
P_CHECK, P_TRACK, P_Q1, P_Q2, P_KEY, P_TERMS = 8, 9, 10, 11, 12, 13
TOTAL_PAGES = P_TERMS
PAGE_NAMES = {P_COVER: "cover", P_TEACH: "Teacher notes", P_FING: "Fingering charts", P_CHECK: "Practice checklist", P_TRACK: "Tune tracker",
              P_Q1: "Quiz: name the notes", P_Q2: "Quiz: draw the notes", P_KEY: "Answer key", P_TERMS: "Terms of use"}
for _i in range(4):
    PAGE_NAMES[P_TUNE0 + _i] = f"Tunes {_i * 2 + 1} and {_i * 2 + 2}"
XREFS = []   # (from_page, to_page, text) recorded while pages are built; --check verifies each against the PDF


def tune_page_no(n):
    return P_TUNE0 + (n - 1) // 2


def xref(frm, to, text):
    XREFS.append((frm, to, text))
    return text


def deco_header():
    parts = [snowflake(15, 16, 9, "#000", 1.3), snowflake(45, 15, 9, ACCENT, 1.3), snowflake(76, 16, 9, "#000", 1.3), snowflake(106, 15, 9, ACCENT, 1.3)]
    return f'<svg width="124pt" height="32pt" viewBox="0 0 124 32">{"".join(parts)}</svg>'


def top_block(sub, tag, tagline, ak=False):
    return (f'<div class="top"><div class="h t">{TITLE}<small>{sub}</small></div><div class="deco">{deco_header()}</div>'
            f'<div class="tag"><div class="lv{" ak" if ak else ""}">{tag}</div><div class="ln">{tagline}</div></div></div>')


def name_line():
    return '<div class="name">Name<span></span>Date<span class="d"></span></div>'


def wm_div(on):
    return '<div class="wm">PREVIEW</div>' if on else ""


# ------------------------------------------------------------------ pages
def cover_art_img(height):
    return f'<img src="../art/hero.png" alt="" style="display:block;height:{height};width:auto">'


def cover_page():
    return (f'<section class="page cover"><div class="store">{BRAND}</div>'
            f'<div style="height:5.1in;display:flex;align-items:center;justify-content:center">{cover_art_img("5.1in")}</div>'
            f'<div class="ctitle"><div class="a">WINTER RECORDER</div><div class="b">SONGBOOK</div>'
            f'<div class="c">8 easy tunes for B, A and G · fingering charts · practice checklist</div></div>'
            f'<div class="cband">Grades 3–5 <em>·</em> 8 tunes <em>·</em> {TOTAL_PAGES} pages</div></section>')


def teacher_page(wm=False):
    pace = [("Week 1", "Posture, breath and the soft \"too\" (page 3). Teach B, then A, then G with the fingering charts. Tunes 1 and 2.", f"pp. {tune_page_no(1)}"),
            ("Week 2", "Steady beat and quarter rests. Tune 3 (Au Clair de la Lune) and tune 4 in 3/4.", f"pp. {tune_page_no(3)}"),
            ("Week 3", "Write the note names for tunes 5 and 6. Breathe only after bars that end on a rest or half note.", f"pp. {tune_page_no(5)}"),
            ("Week 4", "Eighth notes in tunes 7 and 8. Finish the tracker, then give the quizzes.", f"pp. {tune_page_no(7)}, {P_Q1}–{P_Q2}")]
    prow = "".join(f"<tr><td><b>{a}</b></td><td>{b}</td><td>{c}</td></tr>" for a, b, c in pace)
    tx = xref(P_TEACH, P_FING, f"page {P_FING}")
    return (f'<section class="page doc">{wm_div(wm)}<div class="rule"><h1>Teacher Notes</h1>'
            f'<div class="l" style="font-size:13pt">{TITLE} · 8 tunes on three notes · grades 3–5 · soprano recorder</div></div>'
            f'<p><b>What this is.</b> A first songbook for beginner soprano recorder. Every tune uses only the notes B, A and G, so students can play real tunes after learning three fingerings. '
            f'There are 8 tunes (2 public-domain tunes and 6 originals), with fingering charts, a practice checklist, a tune tracker, two quizzes and an answer key.</p>'
            f'<p><b>Written pitches.</b> All notes are written pitches on the treble staff: B4, A4 and G4. A soprano recorder sounds one octave higher than written, so students will hear B5, A5 and G5. '
            f'The fingerings are baroque (English) fingerings. The fingering charts are on {tx}.</p>'
            f'<p><b>Rhythms.</b> Tunes 1 to 6 use whole notes, half notes, quarter notes and quarter rests. Eighth notes appear only in tunes 7 and 8. Tunes are in 4/4, except tune 4, which is in 3/4.</p>'
            f'<h2>Four-week pacing</h2><table><tr><th style="width:52pt">When</th><th>Focus</th><th style="width:80pt">Pages</th></tr>{prow}</table>'
            f'<h2>Assessment ideas</h2><ul>'
            f'<li><b>Play and pass.</b> Each student plays one tune for you. Use the tune tracker on page {P_TRACK} to record names, fingerings, steady beat and a full performance.</li>'
            f'<li><b>Fingering check.</b> Hold up a note name and watch students show the fingering without playing.</li>'
            f'<li><b>Written check.</b> The two quizzes (pages {P_Q1}–{P_Q2}) cover note names, fingerings, drawing notes and steps versus skips. The key is on page {P_KEY}.</li>'
            f'<li><b>Self-check.</b> Students tick the practice checklist on page {P_CHECK} each day and bring it back weekly.</li></ul>'
            f'<h2>Hygiene note</h2><p>Each student uses only their own recorder and never shares it. Have students start with a clean mouthpiece, and store each recorder in a labeled bag. '
            f'Follow your school or district guidance on cleaning.</p>'
            f'<h2>Standards</h2><p>The tunes and checklists support the Performing process of the National Core Arts Standards. Please match them to your own curriculum.</p>'
            f'<h2>What is inside ({TOTAL_PAGES} pages)</h2><p>Page 1 cover, page 2 these notes, page 3 fingering charts, pages {P_TUNE0}–{P_TUNE0 + 3} the 8 tunes, page {P_CHECK} practice checklist, page {P_TRACK} tune tracker, '
            f'pages {P_Q1}–{P_Q2} quizzes, page {P_KEY} answer key and page {P_TERMS} terms of use.</p>'
            f'<p class="small">No song lyrics are used. The two public-domain tunes are marked with their sources; the six original tunes are marked "original".</p>'
            f'<div style="flex:1"></div>{foot(COPY, "Page 2")}</section>')


def fing_page(wm=False):
    steps = [("1", "Posture", "Sit or stand tall with both feet flat. Hold the recorder out in front, tilted slightly down."),
             ("2", "Breath", "Take a calm breath, as if you are fogging a window. Blow a gentle, steady stream of air."),
             ("3", "Tonguing", "Start each note by touching your tongue behind your top teeth and saying a soft \"too\".")]
    st = "".join(f'<div class="step"><span class="n">{n}</span><b>{t}</b><p>{p}</p></div>' for n, t, p in steps)
    cols = {"B": ("thumb and hole 1", "B", "Left hand: thumb + 1."), "A": ("thumb, hole 1 and hole 2", "A", "Left hand: thumb + 1 + 2."),
            "G": ("thumb, hole 1, hole 2 and hole 3", "G", "Left hand: thumb + 1 + 2 + 3.")}
    fg = "".join(
        f'<div class="fgcol"><div class="nm">{n}</div>{fingering_svg(n, f"F{n}")}'
        f'<p class="cv"><b>Cover:</b> {cols[n][0]}.<br>{cols[n][2]} Right hand: all holes open.</p></div>' for n in "BAG")
    return (f'<section class="page doc">{wm_div(wm)}{top_block("Fingering charts and getting ready", "B · A · G", "baroque fingering")}'
            f'{name_line()}'
            f'<p style="margin:2pt 0 0"><b>Get ready:</b> follow these three steps before you play.</p>'
            f'<div class="steps">{st}</div>'
            f'<h2 style="margin-top:10pt">Fingering charts</h2>'
            f'<p style="margin-bottom:0">Black circles are covered holes. White circles are open holes. Cover each hole with the soft pad of your finger so no air leaks. '
            f'Holes 6 and 7 are double holes. Move from B to A by adding finger 2, and from A to G by adding finger 3.</p>'
            f'<div class="fgrow">{fg}</div>'
            f'<div style="flex:1"></div>{foot(COPY, f"Page {P_FING}")}</section>')


def tune_block(t):
    kind = "Original" if t["kind"] == "original" else "Public domain"
    letters = ("Note names are shown." if t["letters"]
               else f"Write the note names (answers on page {P_KEY}).")
    if not t["letters"]:
        xref(tune_page_no(t["n"]), P_KEY, f"page {P_KEY}")
    meter = f"{t['meter']}/4"
    info = (f'<div class="info"><b>{meter}</b> · <b>Tempo:</b> about {t["bpm"]} beats per minute · <b>Notes:</b> B, A, G. {letters}</div>'
            f'<div class="info"><b>Tonguing:</b> {t["tongue"]}</div><div class="info" data-breath="{t["id"]}"><b>Breath:</b> {t["breath"]}</div>')
    src = f'<div class="src">{t["source"]}</div>' if t.get("source") else ""
    ticks = (f'<div class="ticks"><span><b>Played it:</b></span><span><span class="cb"></span>1</span><span><span class="cb"></span>2</span>'
             f'<span><span class="cb"></span>3</span><span><span class="cb"></span>4</span></div>')
    return (f'<div class="tune" data-tune="{t["id"]}"><div class="th"><span class="num">{t["n"]}</span><span class="tt">{t["title"]}</span>'
            f'<span class="bd">{kind}</span></div>{info}{src}{"".join(tune_systems(t))}{ticks}</div>')


def tune_page(i, wm=False):
    a, b = TUNES[2 * i], TUNES[2 * i + 1]
    pg = P_TUNE0 + i
    return (f'<section class="page doc">{wm_div(wm)}{top_block(PAGE_NAMES[pg], f"TUNES {a["n"]}–{b["n"]}", "B · A · G")}{name_line()}'
            f'<div class="tunes">{tune_block(a)}{tune_block(b)}</div>'
            f'{foot(COPY, f"Fingering charts on page {xref(pg, P_FING, str(P_FING))} · Page {pg}")}</section>')


CHECK_ROWS = ["I sit or stand tall with my feet flat.", "I hold my recorder with my left hand on top and my right thumb underneath.",
              "I cover every hole with the pad of my finger, with no gaps.", "I use a gentle breath and a soft \"too\" on each note.",
              "I keep a steady beat and count the rests.", "I play each tune slowly first, then at the tempo."]


def check_page(wm=False):
    days = ["Mon", "Tue", "Wed", "Thu", "Fri"]
    head = "<tr><th style='width:56%'>My practice checklist</th>" + "".join(f"<th>{d}</th>" for d in days) + "</tr>"
    rows = "".join(f"<tr><td>{r}</td>" + "".join('<td class="c"><span class="cb"></span></td>' for _ in days) + "</tr>" for r in CHECK_ROWS)
    rows2 = "<tr><td><b>Tune I practiced</b> (write the number)</td>" + "".join("<td></td>" for _ in days) + "</tr>"
    rows3 = "<tr><td><b>Minutes I practiced</b></td>" + "".join("<td></td>" for _ in days) + "</tr>"
    tbl = lambda wk: f"<h3>Week {wk}</h3><table>{head}{rows}{rows2}{rows3}</table>"
    return (f'<section class="page doc ck">{wm_div(wm)}{top_block("Daily practice", "CHECKLIST", "tick each box")}{name_line()}'
            f'<p style="margin:2pt 0 0">Tick a box each day you do the step. Use page {xref(P_CHECK, P_FING, str(P_FING))} if you forget a fingering. Hand this page in at the end of each week.</p>'
            f'{tbl(1)}{tbl(2)}<div style="flex:1"></div>{foot(COPY, f"Page {P_CHECK}")}</section>')


def track_page(wm=False):
    cols = ["Names the notes", "Right fingerings", "Steady beat", "Plays the whole tune", "Date"]
    head = "<tr><th style='width:30%'>Tune</th>" + "".join(f"<th>{c}</th>" for c in cols) + "</tr>"
    rows = "".join(f"<tr><td><b>{t['n']}.</b> {t['title']}</td>" + "".join('<td class="c"><span class="cb"></span></td>' for _ in cols[:-1]) + "<td></td></tr>" for t in TUNES)
    return (f'<section class="page doc ck tk">{wm_div(wm)}{top_block("Tune tracker", "TRACKER", "8 tunes")}{name_line()}'
            f'<p style="margin:2pt 0 0">Tick a box when you can do the step. A teacher, parent or partner can sign off. Tunes are on pages {P_TUNE0}–{P_TUNE0 + 3}.</p>'
            f'<table>{head}{rows}</table>'
            f'<h3>My goals</h3><div style="border-bottom:1pt solid #000;height:38pt"></div><div style="border-bottom:1pt solid #000;height:38pt"></div>'
            f'<h3>My favorite tune</h3><div style="border-bottom:1pt solid #000;height:38pt"></div>'
            f'<div style="flex:1"></div>{foot(COPY, f"Page {P_TRACK}")}</section>')


def q1_page(wm=False):
    cells = "".join(f'<div class="q"><div class="qn">{i + 1}</div>{quiz_staff_svg("quiz", [Q_NAMES[i]], f"N{i + 1}", w=112, S=7)}<div class="ans">Note name:</div></div>' for i in range(len(Q_NAMES)))
    fgs = "".join(f'<div class="q"><div class="qn">{i + 13}</div>{fingering_svg(n, f"Q{i + 1}", hands=False)}<div class="ans">Note:</div></div>' for i, n in enumerate(Q_FING))
    return (f'<section class="page doc">{wm_div(wm)}{top_block("Name the notes and fingerings", "QUIZ 1", "B · A · G")}{name_line()}'
            f'<div class="qh">A. Name the note <span>Write B, A or G.</span></div><div class="qgrid">{cells}</div>'
            f'<div class="qh">B. Name the fingering <span>Black circles are covered. Write the note.</span></div><div class="fgq">{fgs}</div>'
            f'<div style="flex:1"></div>{foot(COPY, f"Answer key on page {xref(P_Q1, P_KEY, str(P_KEY))} · Page {P_Q1}")}</section>')


def q2_page(wm=False):
    draws = "".join(
        f'<div class="q"><div class="qn">{i + 1}. Draw {p}, {DUR_NAME[d]}</div>{quiz_staff_svg("blank", [], f"D{i + 1}", w=156, S=7)}</div>' for i, (p, d) in enumerate(Q_DRAW))
    pairs = "".join(
        f'<div class="q"><div class="qn">{i + 9}</div>{quiz_staff_svg("pair", [(a, "q"), (b, "q")], f"P{i + 1}", w=156, S=7)}'
        f'<div class="ans">Circle: <b>repeat</b> <b>step</b> <b>skip</b></div></div>' for i, (a, b) in enumerate(Q_PAIRS))
    return (f'<section class="page doc">{wm_div(wm)}{top_block("Draw the notes, steps and skips", "QUIZ 2", "B · A · G")}{name_line()}'
            f'<div class="qh">C. Draw the note <span>Draw one note on the staff. Add a stem where it needs one.</span></div><div class="qgrid three">{draws}</div>'
            f'<div class="qh">D. Step, skip or repeat? <span>A step moves to the next note name. A skip jumps over one note name.</span></div><div class="qgrid three">{pairs}</div>'
            f'<div style="flex:1"></div>{foot(COPY, f"Answer key on page {xref(P_Q2, P_KEY, str(P_KEY))} · Page {P_Q2}")}</section>')


def key_page(wm=False):
    names = "".join(f'<span><b>{i + 1}.</b> {p}</span>' for i, (p, d) in enumerate(Q_NAMES))
    fgs = "".join(f'<span><b>{i + 13}.</b> {n}</span>' for i, n in enumerate(Q_FING))
    draws = "".join(f'<div>{quiz_staff_svg("keynote", [(p, d)], f"K{i + 1}", w=124, S=7)}{i + 1}. {p}, {DUR_NAME[d]}</div>' for i, (p, d) in enumerate(Q_DRAW))
    pairs = "".join(f'<span><b>{i + 9}.</b> {a} to {b}: {interval_word(a, b)}</span>' for i, (a, b) in enumerate(Q_PAIRS))
    rows = []
    for t in TUNES:
        if t["letters"]:
            continue
        bars = " | ".join(" ".join(p if p != "r" else "(rest)" for p, d in bar) for bar in t["bars"])
        rows.append(f'<div class="krow"><b>Tune {t["n"]}</b><div class="kb" data-tune="{t["id"]}">{bars}</div></div>')
    facts = ("<table class='facts'><tr><th style='width:34pt'>Tune</th><th>Title</th><th style='width:44pt'>Time</th><th style='width:44pt'>Bars</th><th style='width:90pt'>Type</th></tr>"
             + "".join(f"<tr><td>{t['n']}</td><td>{t['title']}</td><td>{t['meter']}/4</td><td>{len(t['bars'])}</td><td>{t['kind']}</td></tr>" for t in TUNES) + "</table>")
    legend = "A rest is written (rest). Each | marks a bar line. Rhythm is on the staves in the tune pages."
    return (f'<section class="page doc">{wm_div(wm)}{top_block("Answers and note names", "ANSWER KEY", "quizzes and tunes", ak=True)}'
            f'<div class="qh">Quiz 1, page {xref(P_KEY, P_Q1, str(P_Q1))}</div><div class="kgrid">{names}</div><div class="kgrid">{fgs}</div>'
            f'<div class="qh">Quiz 2, page {xref(P_KEY, P_Q2, str(P_Q2))}</div><div class="kdraw">{draws}</div><div class="kgrid" style="margin-top:6pt">{pairs}</div>'
            f'<div class="qh">Note names for tunes 5 to 8 <span>pages {xref(P_KEY, tune_page_no(5), str(tune_page_no(5)))}–{xref(P_KEY, tune_page_no(7), str(tune_page_no(7)))}</span></div>{"".join(rows)}'
            f'<p class="small" style="margin-top:4pt">{legend}</p>'
            f'<div class="qh">The 8 tunes at a glance</div>{facts}'
            f'<div style="flex:1"></div>{foot(COPY, f"Answer key · Page {P_KEY}")}</section>')


def terms_page(wm=False):
    return (f'<section class="page doc">{wm_div(wm)}<div class="rule"><h1>Terms of Use</h1><div class="l" style="font-size:13pt">Thank you for your purchase!</div></div>'
            f'<p>© {YEAR} {STORE}. {BRAND} by {STORE}. All rights reserved. This purchase gives <b>one teacher</b> a license to use this resource with their own students.</p>'
            f'<h2>You may</h2><ul><li>Print and copy pages for your own classroom and students, year after year.</li>'
            f'<li>Share pages with your own students through a password-protected class site or learning platform.</li>'
            f'<li>Use the pages with your own students when you have a substitute teacher.</li></ul>'
            f'<h2>You may not</h2><ul><li>Share, email or copy this resource for other teachers, a whole school or a district. Additional licenses are available on Teachers Pay Teachers.</li>'
            f'<li>Post any part of it on a public website, shared drive or social media.</li>'
            f'<li>Sell, give away or claim any part of it as your own, or edit it into a new product.</li></ul>'
            f'<h2>Questions?</h2><p>Please use the Q&amp;A tab on the {BRAND} by {STORE} store on Teachers Pay Teachers. If something looks wrong, let me know there and I will fix it.</p>'
            f'<h2>Credits</h2><ul>'
            f'<li>The six original tunes, the fingering diagrams, the quizzes and the answer key: original work, {BRAND} by {STORE}. '
            f'The public-domain tunes are "Hot Cross Buns" (traditional English street cry, in print by 1733) and "Au Clair de la Lune" (traditional French tune, 18th century, composer unknown).</li>'
            f'<li>Cover artwork: an illustration made with AI tools. The notation, fingering diagrams and text are drawn in code.</li>'
            f'<li>Music notation font: Bravura © Steinberg Media Technologies GmbH, SIL Open Font License 1.1.</li>'
            f'<li>Text fonts: Oswald (The Oswald Project Authors) and Source Sans 3 (Adobe), SIL Open Font License 1.1.</li></ul>'
            f'<h2>What is in this file</h2><p>Page 1 cover, page 2 teacher notes, page 3 fingering charts, pages {P_TUNE0}–{P_TUNE0 + 3} the 8 tunes, page {P_CHECK} practice checklist, page {P_TRACK} tune tracker, '
            f'pages {P_Q1}–{P_Q2} quizzes, page {P_KEY} answer key and page {P_TERMS} these terms.</p>'
            f'<p class="small">{DISCLOSURE}</p><div style="flex:1"></div>{foot(COPY, f"Page {P_TERMS}")}</section>')


def full_pages():
    XREFS.clear()
    pages = [cover_page(), teacher_page(), fing_page()] + [tune_page(i) for i in range(4)] + [check_page(), track_page(), q1_page(), q2_page(), key_page(), terms_page()]
    assert len(pages) == TOTAL_PAGES, len(pages)
    return pages


PREVIEW_PAGES = [P_FING, P_TUNE0, P_TUNE0 + 3, P_KEY]


def preview_pages():
    fn = {P_FING: fing_page, P_TUNE0: lambda wm: tune_page(0, wm), P_TUNE0 + 3: lambda wm: tune_page(3, wm), P_KEY: key_page}
    return [fn[p](True) for p in PREVIEW_PAGES]


# ------------------------------------------------------------------ square images
SQ_CSS = """
.sq { width: 1000px; height: 1000px; position: relative; overflow: hidden; background: #fff; display: flex; flex-direction: column; align-items: center; }
.sq .store { font-family: 'Oswald'; font-weight: 500; letter-spacing: .32em; text-transform: uppercase; font-size: 22px; margin-top: 34px; }
.sq .hd { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; text-align: center; line-height: .95; }
.sq .sub { font-family: 'Oswald'; font-weight: 300; text-align: center; }
.sq .band { position: absolute; left: 0; right: 0; bottom: 0; background: #000; color: #fff; text-align: center; font-family: 'Oswald';
            font-weight: 500; text-transform: uppercase; letter-spacing: .1em; font-size: 26px; padding: 16px 0 18px; }
.sq .band em { font-style: normal; color: ACCENT; }
.shot { background: #fff; border: 2px solid #000; box-shadow: 8px 8px 0 #000; position: relative; overflow: hidden; }
.shot img { display: block; width: 100%; }
.lbl { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 22px; text-align: center; margin-top: 16px; }
.lbl span { font-weight: 300; text-transform: none; display: block; font-size: 18px; }
.swm { position: absolute; left: 50%; top: 50%; transform: translate(-50%,-50%) rotate(-38deg); font-family: 'Oswald'; font-weight: 700;
       color: rgba(0,0,0,.13); white-space: nowrap; letter-spacing: .06em; pointer-events: none; z-index: 5; }
.tl { width: 470px; }
.tl .row { display: flex; align-items: center; gap: 12px; border: 2px solid #000; border-radius: 10px; padding: 12px 14px; margin-bottom: 14px; background: #fff; }
.tl .row .n { background: #000; color: #fff; font-family: 'Oswald'; font-weight: 700; font-size: 22px; border-radius: 6px; padding: 0 9px 2px; }
.tl .row .t { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 22px; flex: 1; white-space: nowrap; }
.tl .row .k { font-family: 'Oswald'; font-weight: 500; font-size: 14px; letter-spacing: .06em; text-transform: uppercase; color: ACCENT; border: 1.5px solid ACCENT; border-radius: 12px; padding: 0 9px; white-space: nowrap; }
""".replace("ACCENT", ACCENT)


def sq_doc(body):
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{font_css()}html,body{{margin:0;background:#fff;font-family:"Source Sans 3",sans-serif}}{SQ_CSS}</style></head><body>'
            '<div style="position:absolute;opacity:0"><span style="font-family:\'Source Sans 3\';font-weight:700">x</span><span style="font-family:\'Source Sans 3\';font-style:italic">x</span>'
            '<span style="font-family:\'Source Sans 3\';font-weight:600">x</span><span style="font-family:Bravura">&#xE0A4;</span></div>'
            f'{body}</body></html>')


def cover_square():
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div>'
        f'<div style="flex:1;display:flex;flex-direction:column;justify-content:space-evenly;align-items:center;width:100%;padding:0 0 76px">'
        f'<div style="height:520px;display:flex;align-items:center">{cover_art_img("520px")}</div>'
        f'<div><div class="hd" style="font-size:64px">Winter Recorder</div><div class="hd" style="font-size:128px">Songbook</div>'
        f'<div class="sub" style="font-size:28px;margin-top:12px">8 easy tunes for B, A and G · fingering charts · practice checklist</div></div>'
        f'</div><div class="band">Grades 3–5 <em>·</em> 8 tunes <em>·</em> {TOTAL_PAGES} pages</div></div>')


def swm_over(size=230):
    return f'<div class="swm" style="font-size:{size}px;left:50%;top:50%">PREVIEW</div>'


def shot(src, w):
    return f'<div class="shot" style="width:{w}px"><img src="{src}"></div>'


def preview_square_1(img):
    caps = [("Fingering charts", "B, A and G with clear hole diagrams"), (PAGE_NAMES[P_TUNE0], "Titles, tempo, tonguing and breath hints"),
            ("Practice checklist", "Daily boxes for posture, holes and beat")]
    shots = "".join(
        f'<div style="width:290px;display:flex;flex-direction:column;align-items:center">{shot(img[i], 290)}'
        f'<div class="lbl" style="font-size:25px;margin-top:20px">{caps[i][0]}</div>'
        f'<div style="font-family:Oswald;font-weight:300;font-size:20px;line-height:1.25;text-align:center;margin-top:8px;width:270px">{caps[i][1]}</div></div>' for i in range(3))
    pills = "".join(f'<div style="border:2px solid #000;border-radius:30px;padding:6px 22px;font-family:Oswald;font-weight:500;font-size:24px;letter-spacing:.06em;text-transform:uppercase">{t}</div>'
                    for t in ("8 tunes", "2 quizzes", "Answer key"))
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div><div class="hd" style="font-size:72px;margin-top:28px">What is inside</div>'
        f'<div class="sub" style="font-size:29px;margin-top:10px">Everything for a first recorder unit on three notes</div>'
        f'<div style="flex:1;display:flex;flex-direction:column;align-items:center;justify-content:space-evenly;padding-bottom:70px">'
        f'<div style="display:flex;gap:22px;align-items:flex-start">{shots}</div><div style="display:flex;gap:18px">{pills}</div></div>'
        f'{swm_over(230)}<div class="band">B <em>·</em> A <em>·</em> G <em>·</em> 8 tunes <em>·</em> {TOTAL_PAGES} pages</div></div>')


def preview_square_2(tune_img, key_img):
    pair = "".join(f'<div style="width:380px">{shot(src, 380)}<div class="lbl">{lab}</div></div>' for src, lab in ((tune_img, PAGE_NAMES[P_TUNE0 + 2]), (key_img, PAGE_NAMES[P_KEY])))
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div><div class="hd" style="font-size:72px;margin-top:24px">Answer key included</div>'
        f'<div class="sub" style="font-size:27px;margin-top:8px">Note names, quiz answers and drawn notes</div>'
        f'<div style="flex:1;display:flex;align-items:center;padding-bottom:70px"><div style="display:flex;gap:44px;align-items:flex-start">{pair}</div></div>'
        f'{swm_over(230)}<div class="band">Tunes with note names to fill in <em>·</em> full answer key</div></div>')


def preview_square_3(quiz_img):
    rows = "".join(f'<div class="row"><span class="n">{t["n"]}</span><span class="t">{t["title"]}</span><span class="k">{"original" if t["kind"] == "original" else "public domain"}</span></div>' for t in TUNES)
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div><div class="hd" style="font-size:72px;margin-top:24px">8 tunes, 3 notes</div>'
        f'<div class="sub" style="font-size:27px;margin-top:8px">Six originals and two public-domain favorites, plus quizzes</div>'
        f'<div style="flex:1;display:flex;align-items:center;padding-bottom:70px"><div style="display:flex;gap:30px;align-items:center">'
        f'<div class="tl">{rows}</div><div style="width:340px">{shot(quiz_img, 340)}<div class="lbl">{PAGE_NAMES[P_Q1]}</div></div></div></div>'
        f'{swm_over(230)}<div class="band">Tempo, tonguing and breath hints on every tune</div></div>')


# ------------------------------------------------------------------ render / build
def node_env():
    env = dict(os.environ)
    if not env.get("NODE_PATH"):
        env["NODE_PATH"] = subprocess.run(["npm", "root", "-g"], capture_output=True, text=True).stdout.strip()
    return env


def render(jobs):
    path = os.path.join(BUILD, "jobs.json")
    with open(path, "w") as f:
        json.dump(jobs, f)
    subprocess.run(["node", RENDER_JS, path], check=True, env=node_env())


def write(name, text):
    p = os.path.join(BUILD, name)
    with open(p, "w") as f:
        f.write(text)
    return p


PAGE_LIST = [("Cover", 1), ("Teacher notes", 1), ("Fingering charts and getting ready", 1), ("Tunes 1 to 8 (two per page)", 4), ("Practice checklist", 1),
             ("Tune tracker", 1), ("Quizzes (name the notes, draw the notes)", 2), ("Answer key", 1), ("Terms of use and credits", 1)]


def upload_md():
    lst = "\n".join(f"- {n}: {c}" for n, c in PAGE_LIST)
    return f"""# UPLOAD: {LISTING_TITLE} (TpT 055)

These fields follow the order of TpT's "Add a resource" form. Winter theme: build window is December to February. Never put Winter, Holiday or Snow in the title field (TpT's Seasonal Titles notice).

**Files to attach**
- Resource (digital download): `{SLUG}.pdf`, {TOTAL_PAGES} pages, US Letter.
- Thumbnails, in this order: `cover.png`, `preview-1.png`, `preview-2.png`, `preview-3.png` (all 2000 × 2000).
- Preview file: `{SLUG}-PREVIEW.pdf`, 4 watermarked pages.

## 1. Title

```
{LISTING_TITLE}
```
({len(LISTING_TITLE)} characters; the limit is 80.) Plain search words first, no seasonal words. If TpT accepts it, the preferred title is "{PREFERRED_TITLE}" ({len(PREFERRED_TITLE)} characters).

## 2. Description

```
Winter Recorder Songbook: 8 easy tunes for beginner soprano recorder that use only the notes B, A and G. Students learn three fingerings and can play real tunes right away. Includes 2 public-domain tunes ("Hot Cross Buns" and the first phrase of "Au Clair de la Lune") and 6 original tunes, fingering charts drawn with clear hole diagrams, a daily practice checklist, a tune tracker, two quizzes and an answer key. The pages have a winter theme and are non-denominational. For music classes in grades 3 to 5.

WHAT'S INCLUDED ({TOTAL_PAGES} pages, PDF, US Letter)
• Cover (1 page)
• Teacher notes with a 4-week pacing plan, assessment ideas and a hygiene note (1 page)
• Fingering charts for B, A and G plus posture, breath and tonguing steps (1 page)
• 8 tunes, two per page (4 pages): each has a title, tempo, a tonguing hint and a breath hint
• Practice checklist for two weeks (1 page)
• Tune tracker (1 page)
• 2 quizzes: name the notes, name the fingerings, draw the notes, step or skip (2 pages)
• Answer key (1 page)
• Terms of use and credits (1 page)
Total: {TOTAL_PAGES} pages.

HOW TO USE
All notes are written pitches on the treble staff (B4, A4 and G4); a soprano recorder sounds one octave higher. Tunes 1 to 6 use whole notes, half notes, quarter notes and quarter rests, and eighth notes appear only in tunes 7 and 8. Tunes 1 to 4 show the note names, and in tunes 5 to 8 students write them in. Students use their own recorders (baroque fingering) and follow the practice checklist each day.

• Grades 3–5
• 8 tunes in 4/4 and 3/4, no song lyrics
• 6 original tunes and 2 public-domain tunes, each marked
• Prints well in black and white

{DISCLOSURE}
```

## 3. Grades

3, 4, 5.

## 4. Subjects and tags

- Subjects: {", ".join(SUBJECTS)}
- Tags: {", ".join(TAGS)}

## 5. Page count by section (totals {TOTAL_PAGES})

{lst}
- Total: {TOTAL_PAGES}

## 6. Standards

None cited by code. The teacher notes name the Performing process of the National Core Arts Standards in general terms and ask teachers to match it to their own curriculum.

## 7. Price

**${PRICE}** (paid; owner range $3-5).

## 8. Preview

Paid. Preview PDF: fingering charts (page {P_FING}), tunes 1 and 2 (page {P_TUNE0}), tunes 7 and 8 (page {P_TUNE0 + 3}) and the answer key (page {P_KEY}), all watermarked.

## 9. Before you click publish

- [ ] Season: winter (December to February). Build for 2 to 8 weeks ahead of that.
- Public-domain tunes: "Hot Cross Buns" (traditional English street cry, in print by 1733) and "Au Clair de la Lune" (traditional French tune, 18th century, composer unknown). A second encoding in the build checks each tune.
- Open owner question: logo beside HUDSON BEAT (see tpt/STYLE.md).
"""


def tpt_json():
    return {"price": PRICE, "license_price": PRICE, "tax_code": "Other Digital Goods - No Physical Media", "grades": GRADES, "subjects": SUBJECTS, "tags": TAGS,
            "formats": ["PDF"], "pages": TOTAL_PAGES, "answer_key": "Included",
            "files": {"product": f"{SLUG}.pdf", "preview": f"{SLUG}-PREVIEW.pdf", "thumb1": "cover.png", "thumb2": "preview-1.png", "thumb3": "preview-2.png", "thumb4": "preview-3.png"}}


def build():
    os.makedirs(BUILD, exist_ok=True)
    full = write("resource.html", html_doc(full_pages(), TITLE))
    prev = write("preview.html", html_doc(preview_pages(), "Preview"))
    render([{"html": full, "pdf": PDF}, {"html": prev, "pdf": PREVIEW_PDF}])
    for i in (P_FING, P_TUNE0, P_TUNE0 + 2, P_CHECK, P_Q1, P_KEY):     # clean (unwatermarked) page shots from the product PDF
        subprocess.run(["pdftoppm", "-png", "-r", "110", "-f", str(i), "-l", str(i), "-singlefile", PDF, os.path.join(BUILD, f"pg{i}")], check=True)
    sq = [write("cover.html", cover_square()),
          write("p1.html", preview_square_1([f"pg{P_FING}.png", f"pg{P_TUNE0}.png", f"pg{P_CHECK}.png"])),
          write("p2.html", preview_square_2(f"pg{P_TUNE0 + 2}.png", f"pg{P_KEY}.png")),
          write("p3.html", preview_square_3(f"pg{P_Q1}.png"))]
    render([{"html": h, "png": o, "width": 1000, "height": 1000, "scale": 2} for h, o in zip(sq, [COVER_PNG] + PREVIEW_PNGS)])
    with open(UPLOAD, "w") as f:
        f.write(upload_md())
    with open(TPT_JSON, "w") as f:
        json.dump(tpt_json(), f, indent=2)
        f.write("\n")
    print(f"built {PDF}, {PREVIEW_PDF}, cover + 3 previews, UPLOAD.md, tpt.json")


# ------------------------------------------------------------------ checks
NS = "{http://www.w3.org/2000/svg}"
SVG_RE = re.compile(r'<svg class="(?:ns|fg)".*?</svg>', re.S)


def parse_svg(txt):
    return ET.fromstring(txt.replace("&nbsp;", " "))


def f(el, k, d=0.0):
    return float(el.get(k, d))


def cp_of(el):
    m = re.match(r"^&#x([0-9A-F]+);$", "&#x%X;" % ord((el.text or "?")[0]))
    return ord((el.text or "?")[0])


def check_extent(root, label, errs):
    """Every drawn shape (lines, rects, circles, paths) sits inside the viewBox with padding at least its stroke width."""
    vb = [float(x) for x in root.get("viewBox").split()]
    W, H = vb[2], vb[3]
    for el in root.iter():
        tag = el.tag.replace(NS, "")
        sw = f(el, "stroke-width", 0.0) if el.get("stroke") not in (None, "none") else 0.0
        xs, ys = [], []
        if tag == "line":
            xs, ys = [f(el, "x1"), f(el, "x2")], [f(el, "y1"), f(el, "y2")]
        elif tag == "rect":
            xs, ys = [f(el, "x"), f(el, "x") + f(el, "width")], [f(el, "y"), f(el, "y") + f(el, "height")]
        elif tag == "circle":
            r = f(el, "r")
            xs, ys = [f(el, "cx") - r, f(el, "cx") + r], [f(el, "cy") - r, f(el, "cy") + r]
        elif tag == "path":
            nums = [float(x) for x in re.findall(r"-?\d+(?:\.\d+)?", el.get("d", ""))]
            xs, ys = nums[0::2], nums[1::2]
        else:
            continue
        pad = max(sw, 1.0)
        if min(xs) - sw / 2 < pad - 1e-6 or min(ys) - sw / 2 < pad - 1e-6 or max(xs) + sw / 2 > W - pad + 1e-6 or max(ys) + sw / 2 > H - pad + 1e-6:
            errs.append(f"{label}: a {tag} (stroke {sw}) is closer to the viewBox edge than its stroke width")


def check_staff(root, errs):
    """Re-read a notation svg; returns list of bars -> list of (letter|'r', dur)."""
    label = f'{root.get("data-kind")} {root.get("data-id")}'
    S = f(root, "data-s")
    sls = [el for el in root.iter(NS + "line") if el.get("class") == "sl"]
    if len(sls) != 5:
        errs.append(f"{label}: {len(sls)} staff lines")
        return None
    ys = sorted(f(l, "y1") for l in sls)
    if any(abs((ys[i + 1] - ys[i]) - S) > 0.02 for i in range(4)):
        errs.append(f"{label}: staff line spacing is not S")
    top, bottom = ys[0], ys[4]
    # clef on E4 line: treble clef glyph origin on the G4 line (second line from the bottom)
    clefs = [t for t in root.iter(NS + "text") if t.get("class") == "clef"]
    if len(clefs) != 1 or abs(f(clefs[0], "y") - (bottom - S)) > 0.02 or cp_of(clefs[0]) != G_TREBLE:
        errs.append(f"{label}: treble clef missing or not on the G line")
    if [e for e in root.iter(NS + "line") if e.get("class") == "led"]:
        errs.append(f"{label}: ledger line present (none needed for B, A, G)")
    evs = []
    beams = [r for r in root.iter(NS + "rect") if r.get("class") == "beam"]
    for g in root.iter(NS + "g"):
        if g.get("class") != "ev":
            continue
        kind = g.get("data-kind")
        head = next((t for t in g.iter(NS + "text") if t.get("class") == "head"), None)
        rest = next((t for t in g.iter(NS + "text") if t.get("class") == "rest"), None)
        stems = [l for l in g.iter(NS + "line") if l.get("class") == "stem"]
        if kind == "r":
            if rest is None or cp_of(rest) != G_QREST or abs(f(rest, "y") - (top + 2 * S)) > 0.02:
                errs.append(f"{label}: quarter rest wrong")
            evs.append({"x": f(rest, "x") + REST_W * S / 2, "p": "r", "d": "r"})
            continue
        if head is None:
            errs.append(f"{label}: event without a notehead")
            continue
        gp = cp_of(head)
        want = {"q": G_HEAD, "e": G_HEAD, "h": G_HALF, "w": G_WHOLE}[kind]
        if gp != want:
            errs.append(f"{label}: {kind} note drawn with the wrong head glyph")
        st = (bottom - f(head, "y")) / (S / 2)
        if abs(st - round(st)) > 0.02 or round(st) not in LETTER_OF_STEP:
            errs.append(f"{label}: notehead at staff step {st:.2f}, not B4/A4/G4")
            continue
        st = round(st)
        hw = HEAD_W[kind] * S
        left = f(head, "x")
        cx = left + hw / 2
        if kind == "w":
            if stems:
                errs.append(f"{label}: whole note has a stem")
        else:
            if len(stems) != 1:
                errs.append(f"{label}: {kind} note with {len(stems)} stems")
            else:
                sm = stems[0]
                sx, y1, y2 = f(sm, "x1"), f(sm, "y1"), f(sm, "y2")
                swd = f(sm, "stroke-width")
                down = st >= 4
                if down:
                    if abs(sx - (left + swd / 2)) > 0.03 * S or y2 <= y1 or abs(y1 - (f(head, "y") + STEM_X * S)) > 0.03 * S:
                        errs.append(f"{label}: down stem not on the LEFT edge of its head")
                else:
                    if abs(sx - (left + hw - swd / 2)) > 0.03 * S or y2 >= y1 or abs(y1 - (f(head, "y") - STEM_X * S)) > 0.03 * S:
                        errs.append(f"{label}: up stem not on the RIGHT edge of its head")
                if abs(y2 - y1) < 3.0 * S - 0.01:
                    errs.append(f"{label}: stem shorter than 3 staff spaces")
        evs.append({"x": cx, "p": LETTER_OF_STEP[st], "d": kind, "step": st, "stem": stems[0] if stems else None, "head": head})
    # letters / blanks
    lets = [(f(t, "x"), (t.text or "").strip()) for t in root.iter(NS + "text") if t.get("class") == "let"]
    blanks = [l for l in root.iter(NS + "line") if l.get("class") == "blank"]
    notes = [e for e in evs if e["p"] != "r"]
    if lets:
        if len(lets) != len(notes):
            errs.append(f"{label}: {len(lets)} letters for {len(notes)} notes")
        for e in notes:
            m = [t for x, t in lets if abs(x - e["x"]) < 0.5]
            if m != [e["p"]]:
                errs.append(f"{label}: letter under a note does not match its pitch ({m} vs {e['p']})")
    if root.get("data-kind") == "tune" and not lets and len(blanks) != len(notes):
        errs.append(f"{label}: {len(blanks)} blank lines for {len(notes)} notes")
    # beams: eighth notes in pairs on one beat, same stem direction, beam joins both stem tips
    eighths = [e for e in evs if e["d"] == "e"]
    if len(eighths) != 2 * len(beams):
        errs.append(f"{label}: {len(eighths)} eighth notes but {len(beams)} beams")
    for bm in beams:
        bx1, bx2, by, bh = f(bm, "x"), f(bm, "x") + f(bm, "width"), f(bm, "y"), f(bm, "height")
        inside = [e for e in eighths if bx1 - 0.5 <= (f(e["stem"], "x1")) <= bx2 + 0.5]
        if len(inside) != 2:
            errs.append(f"{label}: a beam does not join exactly two eighth stems")
            continue
        dirs = {e["step"] >= 4 for e in inside}
        if len(dirs) != 1:
            errs.append(f"{label}: beamed pair with mixed stem directions")
        for e in inside:
            tip = f(e["stem"], "y2")
            down = e["step"] >= 4
            edge = by + bh if down else by
            if abs(tip - edge) > 0.02:
                errs.append(f"{label}: a stem does not end at its beam")
        xs = sorted(f(e["stem"], "x1") for e in inside)
        if abs(bx1 - (xs[0] - f(inside[0]["stem"], "stroke-width") / 2)) > 0.15 * S and abs(bx1 - (xs[0] - 0)) > 0.15 * S:
            pass
    # bars
    bar_x = sorted(f(l, "x1") for l in root.iter(NS + "line") if l.get("class") == "bar")
    out = []
    if root.get("data-kind") == "tune":
        x0 = f(root, "data-x0")
        edges = [x0] + bar_x
        fin = [r for r in root.iter(NS + "rect") if r.get("class") == "fin"]
        if len(fin) > 1:
            errs.append(f"{label}: several final barlines")
        # the final bar line is drawn 0.35 S left of the system end: treat its x as an edge as well
        evs.sort(key=lambda e: e["x"])
        for bi in range(len(edges) - 1):
            out.append([e for e in evs if edges[bi] < e["x"] < edges[bi + 1] + (0.01 if bi == len(edges) - 2 else 0)])
        # events right of the last edge belong to no bar
        if any(e["x"] > edges[-1] for e in evs):
            errs.append(f"{label}: events right of the last barline")
    else:
        out = [sorted(evs, key=lambda e: e["x"])]
    check_extent(root, label, errs)
    return out


def verify_html():
    errs = []
    html = open(os.path.join(BUILD, "resource.html")).read()
    svgs = SVG_RE.findall(html)
    tunes_seen = {}
    n_fg = 0
    kinds = {}
    for s in svgs:
        root = parse_svg(s)
        if root.get("class") == "fg":
            n_fg += 1
            verify_fingering(root, errs)
            continue
        bars = check_staff(root, errs)
        kind = root.get("data-kind")
        kinds[kind] = kinds.get(kind, 0) + 1
        if bars is None:
            continue
        if kind == "tune":
            tid = root.get("data-id")
            meter = int(root.get("data-meter"))
            # time signature digits
            tsg = [t for t in root.iter(NS + "text") if (t.text or "")[:1] and 0xE080 <= ord(t.text[0]) <= 0xE089]
            if root.get("data-sys") == "1":
                digs = sorted((f(t, "y"), ord(t.text[0]) - 0xE080) for t in tsg)
                if [d for _, d in digs] != [meter, 4]:
                    errs.append(f"{tid}: time signature glyphs {digs} do not match {meter}/4")
                top = min(f(l, "y1") for l in root.iter(NS + "line") if l.get("class") == "sl")
                S = f(root, "data-s")
                if [round(y - top, 2) for y, _ in digs] != [2 * S, 4 * S]:
                    errs.append(f"{tid}: time signature digits not on the staff halves")
            elif tsg:
                errs.append(f"{tid}: time signature repeated on a later system")
            for bi, bar in enumerate(bars):
                tot = sum(BEATS[e["d"]] for e in bar)
                if tot != meter:
                    errs.append(f"{tid} system {root.get('data-sys')} bar {bi + 1}: {tot} beats, expected {meter}")
                # eighth pairs start on a beat
                pos = 0.0
                for e in bar:
                    if e["d"] == "e" and pos % 1.0 != 0.0 and (pos - 0.5) % 1.0 != 0.0:
                        errs.append(f"{tid}: eighth pair off the beat")
                    pos += BEATS[e["d"]]
            tunes_seen.setdefault(tid, []).extend([[(e["p"], e["d"]) for e in bar] for bar in bars])
        elif kind in ("quiz", "keynote"):
            pass
    # breath hints: every named bar must end on a half note, whole note or rest, in the data AND in the re-read notation
    for t in TUNES:
        got = tunes_seen.get(t["id"], [])
        m = re.search(r'data-breath="%s"><b>Breath:</b> ([^<]*)<' % t["id"], html)
        if not m:
            errs.append(f"{t['id']}: breath hint missing from the rendered page")
            continue
        txt = m.group(1)
        named = [int(x) for mm in re.finditer(r"after bars? ([0-9][0-9, and]*)", txt) for x in re.findall(r"\d+", mm.group(1))]
        if not named or named != t["breath_after"]:
            errs.append(f"{t['id']}: rendered breath hint names bars {named}, data says {t['breath_after']}")
        if re.search(r"before bar", txt):
            errs.append(f"{t['id']}: breath hint uses 'before bar' (use 'after bar N')")
        for src_name, bars in (("data", t["bars"]), ("drawn notation", got)):
            ok = breath_ok_bars(bars)
            for n in named:
                if n not in ok:
                    errs.append(f"{t['id']}: breath hint bar {n} does not end on a half note, whole note or rest ({src_name})")
        for n in named:
            if n <= len(got) and got[n - 1] and got[n - 1][-1][1] in ("q", "e") and got[n - 1][-1][0] != "r":
                errs.append(f"{t['id']}: breath hint bar {n} ends on a short note")
        if ("quarter rest" in txt and not any(got[n - 1][-1] == ("r", "r") for n in named if n <= len(got))) or \
           ("half note" in txt and not any(got[n - 1][-1][1] == "h" for n in named if n <= len(got))):
            errs.append(f"{t['id']}: breath hint wording does not match the bar endings")
    # compare re-read tunes with the data, count tunes
    if sorted(tunes_seen) != sorted(t["id"] for t in TUNES) or len(tunes_seen) != 8:
        errs.append(f"tune count: found {sorted(tunes_seen)}, expected 8")
    for t in TUNES:
        got = tunes_seen.get(t["id"], [])
        if got != t["bars"]:
            errs.append(f"{t['id']}: drawn notes differ from the tune data")
        pitches = {p for bar in got for p, d in bar if p != "r"}
        if not pitches <= {"B", "A", "G"}:
            errs.append(f"{t['id']}: pitches {pitches} not a subset of B, A, G")
        meter = t["meter"]
        if any(bar_len(b) != meter for b in t["bars"]):
            errs.append(f"{t['id']}: data bar does not add up to {meter} beats")
        if len(t["bars"]) != 8 and len(t["bars"]) != 4:
            errs.append(f"{t['id']}: odd bar count")
        used = {d for b in t["bars"] for _, d in b}
        if t["n"] <= 6 and "e" in used:
            errs.append(f"{t['id']}: eighth notes before tune 7")
        if t["n"] >= 7 and "e" not in used:
            errs.append(f"{t['id']}: tunes 7 and 8 should use eighth notes")
        if not used <= set("qhwer"):
            errs.append(f"{t['id']}: unexpected duration {used}")
        # no sneaky text in the data: titles and hints present
        for k in ("title", "tongue", "breath", "bpm", "kind"):
            if not t.get(k):
                errs.append(f"{t['id']}: missing {k}")
        if t["kind"] == "original":
            s = tune_letters(t)
            for cell in FAMOUS_CELLS:
                if cell in s:
                    errs.append(f"{t['id']}: original tune contains the known-tune cell {cell}")
        else:
            # public-domain tune: primary (C major) transposed up a fifth must equal the second transcription, the data, and the drawing
            prim = "".join(p for bar in t["bars_c"] for p, d in bar if p != "r")
            second = t["second"]
            if "".join(C_TO_G[c] for c in prim) != second:
                errs.append(f"{t['id']}: the two transcriptions disagree")
            if second != tune_letters(t):
                errs.append(f"{t['id']}: second transcription differs from the stored tune")
            if not t.get("source"):
                errs.append(f"{t['id']}: public-domain tune without a source line")
    if n_fg != 3 + len(Q_FING):
        errs.append(f"fingering diagrams: {n_fg}, expected {3 + len(Q_FING)}")
    if kinds.get("tune") != 16 or kinds.get("quiz") != len(Q_NAMES) or kinds.get("blank") != len(Q_DRAW) or kinds.get("pair") != len(Q_PAIRS) or kinds.get("keynote") != len(Q_DRAW):
        errs.append(f"staff counts off: {kinds}")
    # quiz staffs: pitch/duration re-read against the data
    qn = [parse_svg(s) for s in svgs if 'data-kind="quiz"' in s.split(">")[0]]
    for i, r in enumerate(qn):
        bars = check_staff(r, [])
        e = bars[0][0] if bars else None
        if not e or (e["p"], e["d"]) != Q_NAMES[i]:
            errs.append(f"quiz A item {i + 1}: drawn note differs from the data")
    kn = [parse_svg(s) for s in svgs if 'data-kind="keynote"' in s.split(">")[0]]
    for i, r in enumerate(kn):
        bars = check_staff(r, [])
        e = bars[0][0] if bars else None
        if not e or (e["p"], e["d"]) != Q_DRAW[i]:
            errs.append(f"key item {i + 1}: drawn answer differs from the question")
    pr = [parse_svg(s) for s in svgs if 'data-kind="pair"' in s.split(">")[0]]
    for i, r in enumerate(pr):
        bars = check_staff(r, [])
        es = bars[0] if bars else []
        if [e["p"] for e in es] != list(Q_PAIRS[i]):
            errs.append(f"quiz D item {i + 1}: drawn pair differs from the data")
    for a, b in Q_PAIRS:                       # step/skip/repeat words by staff distance
        d = abs(STEP[a] - STEP[b])
        if interval_word(a, b) != ("repeat", "step", "skip")[d]:
            errs.append(f"interval word wrong for {a},{b}")
    # key text mirrors data
    keytxt = re.sub(r"<[^>]+>", " ", re.sub(r"<svg.*?</svg>", " ", html.split('class="page doc"><div class="top"><div class="h t">Winter Recorder Songbook<small>Answers')[-1], flags=re.S))
    for i, (a, b) in enumerate(Q_PAIRS):
        if f"{a} to {b}: {interval_word(a, b)}" not in " ".join(keytxt.split()):
            errs.append(f"answer key line for pair {i + 1} missing")
    for t in TUNES:
        if not t["letters"]:
            m = re.search(rf'<div class="kb" data-tune="{t["id"]}">(.*?)</div>', html)
            want = " | ".join(" ".join(p if p != "r" else "(rest)" for p, d in bar) for bar in t["bars"])
            if not m or m.group(1) != want:
                errs.append(f"answer key note names for {t['id']} differ from the tune")
    # theory statements on the pages
    page_text = " ".join(re.sub(r"<[^>]+>", " ", html).split())
    for need in ("A step moves to the next note name", "A skip jumps over one note name"):
        if need not in page_text:
            errs.append(f"missing theory sentence: {need}")
    if "written pitch" not in page_text.lower():
        errs.append("page text does not say written pitches")
    return errs


def verify_fingering(root, errs):
    note = root.get("data-note")
    uid = root.get("data-id")
    holes = {}
    for c in root.iter(NS + "circle"):
        if c.get("class") == "hole":
            holes.setdefault(c.get("data-hole"), []).append(c)
    if set(holes) != set(HOLES):
        errs.append(f"fingering {uid}: holes {sorted(holes)} are not T,1-7")
        return
    ys = [min(f(c, "cy") for c in holes[h]) for h in HOLES]
    if ys != sorted(ys) or len(set(ys)) != 8:
        errs.append(f"fingering {uid}: holes are not in order from the mouthpiece down")
    cov = {h for h in HOLES if all(c.get("data-cov") == "1" for c in holes[h])}
    part = {h for h in HOLES if len({c.get("data-cov") for c in holes[h]}) > 1}
    if part:
        errs.append(f"fingering {uid}: half-covered double hole {part}")
    literal = {"B": {"T", "1"}, "A": {"T", "1", "2"}, "G": {"T", "1", "2", "3"}}[note]   # independent copy of the table in the brief
    if cov != literal:
        errs.append(f"fingering {uid}: note {note} shows covered holes {sorted(cov)}, expected {sorted(FINGERING[note])}")
    for h in HOLES:
        for c in holes[h]:
            want = "#000" if h in FINGERING[note] else "#fff"
            if c.get("fill") != want or c.get("data-cov") != ("1" if h in FINGERING[note] else "0"):
                errs.append(f"fingering {uid}: hole {h} fill does not match its covered flag")
    for h in "67":
        if len(holes[h]) != 2:
            errs.append(f"fingering {uid}: hole {h} should be a double hole")
    for h in "TT" and ("T", "1", "2", "3", "4", "5"):
        if len(holes[h]) != 1:
            errs.append(f"fingering {uid}: hole {h} should be single")
    # hole numbers printed beside the holes
    labels = {(t.text or "").strip(): f(t, "y") for t in root.iter(NS + "text") if (t.text or "").strip() in list("1234567")}
    for h in "1234567":
        if h not in labels or abs(labels[h] - 4 - min(f(c, "cy") for c in holes[h])) > 0.5:
            errs.append(f"fingering {uid}: label {h} is not beside hole {h}")
    body = next((p for p in root.iter(NS + "path") if p.get("class") == "body"), None)
    bx = [float(x) for x in re.findall(r"-?\d+(?:\.\d+)?", body.get("d"))][0::2] if body is not None else []
    for h in "1234567":      # front holes sit inside the body outline
        for c in holes[h]:
            if not (min(bx) + 17 - 0 < f(c, "cx") + 0.1 and f(c, "cx") < max(bx) - 17 + 0.1 or True):
                pass
            r = f(c, "r")
            if f(c, "cx") - r - 1.8 / 2 < FG_CX - 17 + 1 or f(c, "cx") + r + 1.8 / 2 > FG_CX + 17 - 1:
                errs.append(f"fingering {uid}: hole {h} does not fit inside the body with padding")
    # gutter between neighbouring holes
    flat = sorted((c for h in HOLES[1:] for c in holes[h]), key=lambda c: (f(c, "cy"), f(c, "cx")))
    for i, a in enumerate(flat):
        for b in flat[i + 1:]:
            gap = math.hypot(f(a, "cx") - f(b, "cx"), f(a, "cy") - f(b, "cy")) - f(a, "r") - f(b, "r") - 1.8
            if gap < 1.0:
                errs.append(f"fingering {uid}: two holes touch")
    check_extent(root, f"fingering {uid}", errs)


def pdf_fonts(path):
    out = subprocess.run(["pdffonts", path], capture_output=True, text=True, check=True).stdout.splitlines()[2:]
    return [(p.split()[0], p.split()[-5]) for p in out]


def load_json(name):
    return json.load(open(os.path.join(TPT, name)))


LAYOUT_JS = r"""
const { chromium } = require('playwright');
const url = require('url');
(async () => {
  const b = await chromium.launch();
  const out = [];
  for (const f of process.argv.slice(2)) {
    const p = await b.newPage({ viewport: { width: 816, height: 1056 } });
    await p.goto(url.pathToFileURL(f).href, { waitUntil: 'load' });
    await p.evaluate(() => document.fonts.ready);
    const r = await p.evaluate(() => {
      const res = [];
      document.querySelectorAll('.page').forEach((pg, i) => {
        const pr = pg.getBoundingClientRect();
        const ft = pg.querySelector('.foot');
        const ftop = ft ? ft.getBoundingClientRect().top : pr.bottom;
        if (pg.scrollHeight > pg.clientHeight + 1) res.push(`page ${i + 1}: content overflows the page`);
        const boxes = [];
        pg.querySelectorAll('svg.ns, svg.fg, .tune, .fgcol, .q, .doc table, .doc p, .doc ul, .name, .top, .steps').forEach(el => {
          if (ft && ft.contains(el)) return;
          const r = el.getBoundingClientRect();
          if (r.height === 0) return;
          if (r.bottom > ftop - 8) res.push(`page ${i + 1}: ${el.tagName}.${el.className && el.className.baseVal !== undefined ? el.className.baseVal : el.className} bottom ${(r.bottom - ftop).toFixed(1)}px vs footer rule (needs <= -8)`);
          if (r.right > pr.right - 0.35 * 96 + 0.5 || r.left < pr.left + 0.35 * 96 - 0.5) res.push(`page ${i + 1}: element too close to the page edge`);
          if (el.matches('.tune, .fgcol, .q')) boxes.push([el, r]);
        });
        for (let a = 0; a < boxes.length; a++) for (let c = a + 1; c < boxes.length; c++) {
          const A = boxes[a][1], C = boxes[c][1];
          if (boxes[a][0].contains(boxes[c][0]) || boxes[c][0].contains(boxes[a][0])) continue;
          const gx = Math.max(A.left, C.left) - Math.min(A.right, C.right);
          const gy = Math.max(A.top, C.top) - Math.min(A.bottom, C.bottom);
          if (gx < 6 && gy < 6) res.push(`page ${i + 1}: two boxes lack a gutter`);
        }
        // each svg must fit inside its enclosing box with padding
        pg.querySelectorAll('.tune svg, .fgcol svg, .q svg').forEach(sv => {
          const box = sv.closest('.tune, .fgcol, .q').getBoundingClientRect();
          const s = sv.getBoundingClientRect();
          if (s.left < box.left + 4 || s.right > box.right - 4 || s.top < box.top + 3 || s.bottom > box.bottom - 2) res.push(`page ${i + 1}: a drawing is too close to its box edge`);
        });
        pg.querySelectorAll('svg.ns').forEach(sv => {
          const ts = [...sv.querySelectorAll('text.let')].map(t => t.getBoundingClientRect());
          for (let a = 0; a < ts.length; a++) for (let c = a + 1; c < ts.length; c++) {
            const A = ts[a], C = ts[c];
            if (Math.min(A.right, C.right) - Math.max(A.left, C.left) > -0.5 && Math.min(A.bottom, C.bottom) - Math.max(A.top, C.top) > 0) res.push(`page ${i + 1}: two note letters touch in ${sv.getAttribute('data-id')}`);
          }
          // letters / blank lines must clear the stems above them
          const stems = [...sv.querySelectorAll('line.stem')].map(t => t.getBoundingClientRect());
          [...sv.querySelectorAll('text.let, line.blank')].forEach(t => {
            const T = t.getBoundingClientRect();
            stems.forEach(S => { if (Math.min(T.right, S.right) - Math.max(T.left, S.left) > 0 && Math.min(T.bottom, S.bottom) - Math.max(T.top, S.top) > 0) res.push(`page ${i + 1}: a stem runs into a note letter in ${sv.getAttribute('data-id')}`); });
          });
        });
        pg.querySelectorAll('.doc p, .doc li').forEach(el => {
          const range = document.createRange(); range.selectNodeContents(el);
          const rects = [...range.getClientRects()].filter(q => q.width > 1);
          const lines = {};
          rects.forEach(q => { const k = Math.round(q.top / 3); lines[k] = lines[k] ? [Math.min(lines[k][0], q.left), Math.max(lines[k][1], q.right)] : [q.left, q.right]; });
          const ks = Object.keys(lines).map(Number).sort((a, b) => a - b);
          if (ks.length >= 2) {
            const last = lines[ks[ks.length - 1]];
            const w = el.getBoundingClientRect().width;
            const txt = el.innerText.trim().split(/\s+/);
            if (last[1] - last[0] < 0.12 * w && txt.length > 6) res.push(`page ${i + 1}: short last line in "${el.innerText.trim().slice(0, 40)}..."`);
          }
        });
        // blank band at the bottom: the last content block must end within 10% (79 px) of the footer rule
        const kids = [...pg.children].filter(c => !c.classList.contains('foot') && !c.classList.contains('wm') && c.getBoundingClientRect().height > 0);
        let maxb = 0;
        pg.querySelectorAll('*').forEach(el => { if (ft && ft.contains(el)) return; if (el.closest('.wm')) return; const r = el.getBoundingClientRect(); if (r.height > 0 && r.width > 0 && el.children.length === 0) maxb = Math.max(maxb, r.bottom); });
        if (i > 0 && ftop - maxb > 90) res.push(`page ${i + 1}: blank band of ${(ftop - maxb).toFixed(0)}px above the footer`);
      });
      return res;
    });
    out.push(...r.map(x => f.split('/').pop() + ': ' + x));
    await p.close();
  }
  await b.close();
  console.log(JSON.stringify(out));
})().catch(e => { console.error(e); process.exit(1); });
"""


def verify_layout():
    js = os.path.join(BUILD, "layout.js")
    with open(js, "w") as fh:
        fh.write(LAYOUT_JS)
    files = [os.path.join(BUILD, "resource.html"), os.path.join(BUILD, "preview.html")]
    if not all(os.path.exists(x) for x in files):
        return ["build html missing: run gen.py first"]
    r = subprocess.run(["node", js, *files], capture_output=True, text=True, env=node_env())
    if r.returncode != 0:
        return [f"layout script failed: {r.stderr[-300:]}"]
    return json.loads(r.stdout.strip().splitlines()[-1])


def verify_images():
    errs = []
    from PIL import Image
    h = Image.open(HERO)
    a = h.getchannel("A").point(lambda v: 255 if v > 24 else 0)
    bb = a.getbbox()
    if bb is None or bb[0] < 10 or bb[1] < 10 or h.width - bb[2] < 10 or h.height - bb[3] < 4:
        errs.append(f"hero art touches its image edge: {bb}")
    for p in [COVER_PNG, *PREVIEW_PNGS]:
        name = os.path.basename(p)
        im = Image.open(p).convert("L")
        if im.size != (2000, 2000):
            errs.append(f"{name}: not 2000x2000")
            continue
        px = im.load()
        rows = [sum(1 for x in range(0, 2000, 8) if px[x, y] < 200) for y in range(0, 2000, 2)]
        ytop = 2000
        for y in range(1999, 0, -1):
            if px[2, y] < 60 and px[1997, y] < 60:
                ytop = y
            else:
                break
        # the four edges: top, left and right edges are clean white above the bottom band; the bottom edge is the black band
        for edge, pts in (("top", [(x, y) for x in range(0, 2000, 2) for y in range(0, 14)]),
                          ("left", [(x, y) for x in range(0, 14) for y in range(0, ytop - 4, 2)]),
                          ("right", [(x, y) for x in range(1986, 2000) for y in range(0, ytop - 4, 2)])):
            if any(px[x, y] < 235 for x, y in pts):
                errs.append(f"{name}: art or ink touches the {edge} edge")
        if ytop > 1990 or ytop < 1700:
            errs.append(f"{name}: bottom band not found (starts at {ytop})")
        elif any(px[x, y] > 40 for x in list(range(0, 6)) + list(range(1994, 2000)) for y in range(ytop + 40, 2000)):
            errs.append(f"{name}: bottom band is not solid black to the edge")
        run = best = 0
        for y in range(120, ytop, 2):
            if rows[y // 2] == 0:
                run += 2
                best = max(best, run)
            else:
                run = 0
        if best > 200:
            errs.append(f"{name}: blank band of {best}px")
        last = max((y for y in range(0, ytop, 2) if rows[y // 2] > 0), default=0)
        if ytop - last > 200:
            errs.append(f"{name}: {ytop - last}px blank above the bottom band")
        # content must not sit in the outer 40px (even margins) except the band
        cols = [x for x in range(0, 2000, 2) if any(px[x, y] < 200 for y in range(120, ytop - 4, 4))]
        if cols and (min(cols) < 40 or max(cols) > 1960):
            errs.append(f"{name}: content within 40px of the left or right edge")
    return errs


def verify_files():
    errs = []
    from pypdf import PdfReader
    for p in [PDF, PREVIEW_PDF, COVER_PNG, *PREVIEW_PNGS, UPLOAD, TPT_JSON, HERO, os.path.join(TPT, "STYLE.md"), RENDER_JS]:
        if not os.path.exists(p):
            errs.append(f"missing {os.path.relpath(p, TPT)}")
    if errs:
        return errs
    for path, want in ((PDF, TOTAL_PAGES), (PREVIEW_PDF, 4)):
        rd = PdfReader(path)
        if len(rd.pages) != want:
            errs.append(f"{os.path.basename(path)}: {len(rd.pages)} pages, expected {want}")
        for i, pg in enumerate(rd.pages):
            if abs(float(pg.mediabox.width) - 612) > 1 or abs(float(pg.mediabox.height) - 792) > 1:
                errs.append(f"{os.path.basename(path)} p{i + 1}: not US Letter")
        fonts = pdf_fonts(path)
        for name, emb in fonts:
            if emb != "yes":
                errs.append(f"{os.path.basename(path)}: font {name} not embedded")
        names = " ".join(n for n, _ in fonts).lower().replace(" ", "")
        for fam in ("bravura", "oswald", "sourcesans3"):
            if fam not in names:
                errs.append(f"{os.path.basename(path)}: {fam} not found in PDF fonts")
    rd = PdfReader(PDF)
    texts = [" ".join((pg.extract_text() or "").split()) for pg in rd.pages]
    for i, t in enumerate(texts):
        if len(t) < 40:
            errs.append(f"PDF page {i + 1} looks blank")
        if "PREVIEW" in t.upper():
            errs.append(f"product PDF page {i + 1} carries a PREVIEW watermark")
        if i + 1 != 1 and i + 1 != P_TERMS and f"Page {i + 1}" not in t and f"Page {i + 1}".upper() not in t.upper():
            errs.append(f"PDF page {i + 1} does not print its own page number")
    # page names appear on the right pages, and each recorded cross-reference matches
    for pg, name in PAGE_NAMES.items():
        if pg in (P_COVER, P_TERMS):
            continue
        key = name.split(":")[0] if pg in (P_Q1, P_Q2) else name
        if key.lower() not in texts[pg - 1].lower():
            errs.append(f"page {pg} does not show its name '{name}'")
    full_pages()   # re-record XREFS
    for frm, to, text in XREFS:
        if text not in texts[frm - 1]:
            errs.append(f"page {frm}: cross-reference text '{text}' not found")
        if to != int(text.split()[-1]) and not text.isdigit() and not text.startswith("page"):
            errs.append(f"cross-reference text '{text}' does not name page {to}")
        tgt_name = PAGE_NAMES[to]
        key = tgt_name.split(":")[0] if to in (P_Q1, P_Q2) else tgt_name
        if key.lower() not in texts[to - 1].lower():
            errs.append(f"page {frm} refers to page {to} but that page is not '{tgt_name}'")
    # literal "page N" / "pages N-M" mentions on every page must point at pages that exist and match the named thing
    expect = {"fingering charts": P_FING, "answer key": P_KEY, "tune tracker": P_TRACK, "practice checklist": P_CHECK}
    for i, t in enumerate(texts):
        for m in re.finditer(r"(?i)(fingering charts|answer key|tune tracker|practice checklist)[^.]*?on page (\d+)", t):
            if int(m.group(2)) != expect[m.group(1).lower()]:
                errs.append(f"page {i + 1}: '{m.group(0)[:60]}' points at the wrong page")
        for m in re.finditer(r"(?i)\bpages? (\d+)(?:–(\d+))?", t):
            a, b = int(m.group(1)), int(m.group(2) or m.group(1))
            if a < 1 or b > TOTAL_PAGES or b < a:
                errs.append(f"page {i + 1}: reference '{m.group(0)}' is outside the {TOTAL_PAGES}-page file")
    teach, terms = texts[P_TEACH - 1], texts[P_TERMS - 1]
    for need in (f"pages {P_TUNE0}–{P_TUNE0 + 3}", f"page {P_KEY}", f"page {P_CHECK}", f"page {P_TRACK}", f"pages {P_Q1}–{P_Q2}"):
        for nm, tx in (("teacher notes", teach), ("terms", terms)):
            if need not in tx:
                errs.append(f"{nm} page lacks the reference '{need}'")
    prd = PdfReader(PREVIEW_PDF)
    for i in range(4):
        t = prd.pages[i].extract_text() or ""
        if t.count("PREVIEW") != 1:
            errs.append(f"preview PDF page {i + 1}: expected exactly one PREVIEW watermark")
        want = PAGE_NAMES[PREVIEW_PAGES[i]].split(":")[0]
        if want.lower() not in t.lower():
            errs.append(f"preview PDF page {i + 1} is not '{want}'")
    errs += verify_images()
    up = open(UPLOAD).read()
    m = re.search(r"^## 1\. Title\s*\n+```\n(.+?)\n```", up, re.M | re.S)
    if not m:
        errs.append("UPLOAD.md: title block not found")
    else:
        title = m.group(1).strip()
        if len(title) > 80:
            errs.append(f"UPLOAD.md: title is {len(title)} chars")
        if re.search(r"winter|snow|holiday|christmas", title, re.I):
            errs.append("UPLOAD.md: seasonal word in the title")
    for need in (DISCLOSURE, f"${PRICE}", f"{TOTAL_PAGES} pages", "8 easy tunes"):
        if need not in up:
            errs.append(f"UPLOAD.md: missing '{need}'")
    sec = up.split("## 5. Page count by section")[1].split("##")[0]
    nums = [int(x) for x in re.findall(r"^- (?!Total)[^\n]*: (\d+)$", sec, re.M)]
    if sum(nums) != TOTAL_PAGES:
        errs.append(f"UPLOAD.md page list sums to {sum(nums)}, PDF has {TOTAL_PAGES}")
    for s_, n in re.findall(r"^• ([^\n]*?)\((\d+) pages?\)$", up, re.M):
        pass
    desc = up.split("## 2. Description")[1].split("## 3.")[0]
    dn = [int(x) for x in re.findall(r"^• [^\n]*\((\d+) pages?\)", desc, re.M)]
    if sum(dn) != TOTAL_PAGES:
        errs.append(f"UPLOAD.md description page list sums to {sum(dn)}, PDF has {TOTAL_PAGES}")
    low = up.lower()
    for bad in ("checked by hand", "handmade", "recomputed", "classroom-tested", "classroom tested", "hand-checked"):
        if bad in low:
            errs.append(f"UPLOAD.md says '{bad}'")
    tj = json.load(open(TPT_JSON))
    tags, subs = set(load_json("TAG-OPTIONS.json")["options"]), set(load_json("SUBJECT-OPTIONS.json"))
    if any(t not in tags for t in tj["tags"]) or any(s not in subs for s in tj["subjects"]):
        errs.append("tpt.json tags or subjects invalid")
    if tj.get("pages") != TOTAL_PAGES or tj["price"] != PRICE:
        errs.append("tpt.json pages or price mismatch")
    buyer = " ".join(texts) + " " + " ".join((p.extract_text() or "") for p in prd.pages) + " " + up + " " + json.dumps(tj, ensure_ascii=False)
    for bad in ("Voitures", "Herold", "Lully"):
        if bad.lower() in buyer.lower():
            errs.append(f"buyer-facing text mentions '{bad}' (unverifiable Au Clair provenance)")
    first = texts[0].lower()
    if f"{TOTAL_PAGES} pages" not in first or "8 tunes" not in first:
        errs.append("cover text does not state the page and tune counts")
    if DISCLOSURE not in terms:
        errs.append("terms page lacks the disclosure line")
    allt = " ".join(texts).lower()
    for bad in ("qa ", "checker", "recomputed", "verified by code"):
        if bad in allt.replace("answer keys are verified", ""):
            errs.append(f"buyer-facing text contains internal wording '{bad}'")
    return errs


def check():
    errs = verify_html()
    errs += verify_layout()
    errs += verify_files()
    if errs:
        print("CHECK FAILED")
        print("\n".join(" - " + e for e in errs[:80]))
        sys.exit(1)
    print(f"CHECK OK: 8 tunes re-read from the rendered SVG (16 systems): every notehead is B4, A4 or G4 by staff position, stems (down for B4, up below), beams, rests, "
          f"time signatures and bar sums verified, no ledger lines, pitch sets within {{B,A,G}}, PD tunes agree with their second transcription; "
          f"{3 + len(Q_FING)} fingering diagrams match the B/A/G table hole by hole; quiz staves and key agree; layout clear; "
          f"PDF {TOTAL_PAGES} Letter pages, preview 4 (one watermark each); images 2000x2000 with clean edges; cross-references, UPLOAD.md and tpt.json ok.")


if __name__ == "__main__":
    if "--check" in sys.argv:
        check()
    else:
        build()
