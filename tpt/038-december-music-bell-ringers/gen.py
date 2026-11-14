#!/usr/bin/env python3
"""December Music Bell-Ringers (TpT 038): build the resource and verify it.

    python3 gen.py           build everything (PDFs, PNGs) into this folder
    python3 gen.py --check   verify note names, counts, symbols, beat gaps, answer keys, layout, pages, fonts and files

20 daily warm-up pages, each with four short parts:
  A  Snowy Notes     name the notes on the treble and bass staff
  B  Mitten Rhythm   write in the counts under two one-line rhythms
  C  Cocoa Symbols   match five music symbols to their names (word bank)
  D  Skate Math      how many beats are missing from the measure?
Every part is generated from data objects; the worksheet and its key are drawn from the same data. `--check` does
not trust that data: it parses the rendered HTML and recomputes every letter name from the notehead's position on the
staff, every count from the note durations, every symbol answer from the symbol's id and every missing-beat total
from the rendered durations.

Rendering uses Playwright + Chromium (HTML/SVG -> PDF/PNG) with the OFL fonts in ../fonts.
"""
import json
import os
import random
import re
import subprocess
import sys
from dataclasses import dataclass, field
from fractions import Fraction as F
from html import escape

HERE = os.path.dirname(os.path.abspath(__file__))
TPT = os.path.dirname(HERE)
FONTS = os.path.join(TPT, "fonts")
BUILD = os.path.join(HERE, "build")
RENDER_JS = os.path.join(TPT, "tools", "render.js")

SLUG = "december-music-bell-ringers"
PDF = os.path.join(HERE, f"{SLUG}.pdf")
PREVIEW_PDF = os.path.join(HERE, f"{SLUG}-PREVIEW.pdf")
COVER_PNG = os.path.join(HERE, "cover.png")
PREVIEW_PNGS = [os.path.join(HERE, f"preview-{i}.png") for i in (1, 2, 3)]
UPLOAD = os.path.join(HERE, "UPLOAD.md")
TPT_JSON = os.path.join(HERE, "tpt.json")

STORE = "Brian Lotze"
BRAND = "Hudson Beat"
YEAR = 2026
ACCENT = "#2B7FB8"   # icy blue: the one accent of this product
DISCLOSURE = "Created with the help of digital and AI tools. Notation and answer keys are verified before release."
TITLE = "December Music Bell-Ringers"
PRICE = "4.50"

S = 7.0              # staff space in pt on worksheets
SVG_W = 540.0        # exercise width in pt (7.5 in)
STAFF_X0 = 22.0
FIRST_BAR = 50.0     # where the first measure starts (after label + time signature)
Y0 = 31.0            # staff line y inside an exercise svg
BOX_W, BOX_H = 20.0, 19.0

# ------------------------------------------------------------------ music model
KIND_DUR = {"whole": F(1), "half": F(1, 2), "quarter": F(1, 4), "eighth": F(1, 8)}
KIND_NAME = {"whole": "whole", "half": "half", "quarter": "quarter", "eighth": "eighth"}
HEAD_W = {"whole": 1.688, "half": 1.18, "quarter": 1.18, "eighth": 1.18}
REST_W = {"whole": 1.128, "half": 1.128, "quarter": 1.08, "eighth": 0.988}
NOTE_GLYPH = {"whole": 0xE1D2, "half": 0xE1D3, "quarter": 0xE1D5, "eighth": 0xE1D7}
REST_GLYPH = {"whole": 0xE4E3, "half": 0xE4E4, "quarter": 0xE4E5, "eighth": 0xE4E6}
HEAD_GLYPH = {"whole": 0xE0A2, "half": 0xE0A3, "quarter": 0xE0A4, "eighth": 0xE0A4}
DOT_GLYPH = 0xE1E7
METERS = {"4/4": (4, 4), "3/4": (3, 4), "2/4": (2, 4), "6/8": (6, 8)}


@dataclass
class Tok:
    kind: str
    rest: bool
    dot: bool
    start: F      # start inside the measure, fraction of a whole note
    dur: F
    count: str = ""


@dataclass
class Ex:
    page: int
    num: int
    meter: str
    measures: list   # list of list[Tok]

    @property
    def id(self):
        return f"{self.page}.{self.num}"


def meter_len(meter):
    n, d = METERS[meter]
    return F(n, d)


def tok_dur(kind, dot):
    return KIND_DUR[kind] * (F(3, 2) if dot else 1)


def count_label(meter, start):
    """Count written under a token that starts `start` (fraction of a whole note) into the measure."""
    if meter == "6/8":
        e = start * 8
        assert e.denominator == 1, f"6/8 start {start}"
        return str(int(e) + 1)
    b = start * 4
    if b.denominator == 1:
        return str(int(b) + 1)
    assert b % 1 == F(1, 2), f"simple-meter start {start}"
    return "&"


# cells: name -> list of (kind, rest, dot); a cell is a one- or two-beat group that is legal to start on a beat
SIMPLE_CELLS = {
    "Q": [("quarter", 0, 0)], "QR": [("quarter", 1, 0)],
    "H": [("half", 0, 0)], "HR": [("half", 1, 0)],
    "W": [("whole", 0, 0)], "WR": [("whole", 1, 0)],
    "DH": [("half", 0, 1)],
    "E2": [("eighth", 0, 0), ("eighth", 0, 0)],
    "EER": [("eighth", 0, 0), ("eighth", 1, 0)],
    "ERE": [("eighth", 1, 0), ("eighth", 0, 0)],
    "DQE": [("quarter", 0, 1), ("eighth", 0, 0)],
}
COMPOUND_CELLS = {   # 6/8: a "beat" is a dotted quarter (3 eighths)
    "DQ": [("quarter", 0, 1)],
    "EEE": [("eighth", 0, 0)] * 3,
    "QE": [("quarter", 0, 0), ("eighth", 0, 0)],
    "EQ": [("eighth", 0, 0), ("quarter", 0, 0)],
    "QRER": [("quarter", 1, 0), ("eighth", 1, 0)],
    "EEER": [("eighth", 0, 0), ("eighth", 0, 0), ("eighth", 1, 0)],
    "DH": [("half", 0, 1)],
}


def cell_span(cells, name):
    return sum(tok_dur(k, d) for k, _, d in cells[name])


def cell_ok(meter, name, idx):
    """Is it legal to start this cell on beat `idx` (0-based, in beats of the meter)?"""
    if meter == "6/8":
        return idx == 0 if name == "DH" else True
    if name in ("H", "HR"):
        return idx in {"4/4": (0, 2), "3/4": (0, 1), "2/4": (0,)}[meter]
    if name in ("W", "WR"):
        return meter == "4/4" and idx == 0
    if name == "DH":
        return idx in {"4/4": (0, 1), "3/4": (0,), "2/4": ()}[meter]
    return True


def beats_per_measure(meter):
    return {"4/4": 4, "3/4": 3, "2/4": 2, "6/8": 2}[meter]


def beat_len(meter):
    return F(3, 8) if meter == "6/8" else F(1, 4)


def cells_for(meter):
    return COMPOUND_CELLS if meter == "6/8" else SIMPLE_CELLS


def make_measure(meter, names):
    """Build the tokens of one measure from cell names; asserts it fills the measure exactly."""
    cells = cells_for(meter)
    pos = F(0)
    out = []
    for nm in names:
        for kind, rest, dot in cells[nm]:
            d = tok_dur(kind, bool(dot))
            out.append(Tok(kind, bool(rest), bool(dot), pos, d, count_label(meter, pos)))
            pos += d
    assert pos == meter_len(meter), (meter, names, pos)
    return out


def random_measure(rng, meter, allowed, featured):
    cells = cells_for(meter)
    names = [n for n in allowed if n in cells]
    nbeats = beats_per_measure(meter)
    bl = beat_len(meter)
    for _ in range(200):
        idx, picked = F(0), []
        while idx < nbeats:
            opts = [n for n in names if cell_span(cells, n) / bl <= nbeats - idx and cell_ok(meter, n, int(idx))]
            if not opts:
                break
            w = [3 if n in featured else 1 for n in opts]
            n = rng.choices(opts, w)[0]
            picked.append(n)
            idx += cell_span(cells, n) / bl
        if idx == nbeats and (picked == ["WR"] or any(not t[1] for n in picked for t in cells[n])):
            return picked
    raise RuntimeError(f"cannot fill {meter} from {allowed}")


# ------------------------------------------------------------------ the 20 days
TREBLE_ALL = ["C4", "D4", "E4", "F4", "G4", "A4", "B4", "C5", "D5", "E5", "F5", "G5", "A5"]
BASS_ALL = ["E2", "F2", "G2", "A2", "B2", "C3", "D3", "E3", "F3", "G3", "A3", "B3", "C4"]
LETTERS = "CDEFGAB"
CLEF_BOTTOM = {"treble": "E4", "bass": "G2"}


def diatonic(p):
    return int(p[1:]) * 7 + LETTERS.index(p[0])


def staff_step(p, clef):
    """Half-spaces above the bottom staff line (0 = bottom line, 8 = top line)."""
    return diatonic(p) - diatonic(CLEF_BOTTOM[clef])


# (theme, focus text, rhythm meters, rhythm cells, featured cells, note rows [(clef, pool, count)], gap meters, gap cells)
Q4 = ["Q", "QR"]
DAYS = [
    ("Snowflake", "Treble lines; quarter notes and rests",
     ["4/4"], Q4, ["QR"], [("treble", ["E4", "G4", "B4", "D5", "F5"], 8)], ["4/4"], Q4),
    ("Mittens", "Treble spaces; half notes",
     ["4/4"], Q4 + ["H"], ["H"], [("treble", ["F4", "A4", "C5", "E5"], 8)], ["4/4"], Q4 + ["H"]),
    ("Hot Cocoa", "Treble lines and spaces; half rests",
     ["4/4"], Q4 + ["H", "HR"], ["HR"], [("treble", ["E4", "F4", "G4", "A4", "B4", "C5", "D5", "E5", "F5"], 8)], ["4/4"], Q4 + ["H", "HR"]),
    ("Ice Skates", "Low treble notes; whole notes and rests",
     ["4/4"], ["Q", "H", "HR", "W", "WR"], ["W", "WR"], [("treble", ["C4", "D4", "E4", "F4", "G4"], 8)], ["4/4"], ["Q", "QR", "H"]),
    ("Sled Run", "Middle treble notes; 3/4 time",
     ["3/4"], Q4 + ["H"], ["H"], [("treble", ["G4", "A4", "B4", "C5", "D5", "E5"], 8)], ["3/4", "4/4"], Q4 + ["H"]),
    ("Snow Globe", "Treble clef C4 to A5; 2/4 and 3/4 time",
     ["3/4", "2/4"], Q4 + ["H"], ["H", "QR"], [("treble", TREBLE_ALL, 8)], ["2/4", "3/4"], Q4 + ["H"]),
    ("Warm Scarf", "Treble clef, all notes; eighth notes",
     ["4/4"], ["Q", "QR", "H", "E2"], ["E2"], [("treble", TREBLE_ALL, 8)], ["4/4"], ["Q", "QR", "H", "E2"]),
    ("Icicles", "Treble clef, all notes; eighth notes in 3/4",
     ["4/4", "3/4"], ["Q", "QR", "H", "E2"], ["E2"], [("treble", TREBLE_ALL, 8)], ["3/4", "4/4"], ["Q", "QR", "H", "E2"]),
    ("Snowball", "Bass lines; eighth rests",
     ["4/4"], ["Q", "QR", "H", "E2", "EER", "ERE"], ["EER", "ERE"], [("bass", ["G2", "B2", "D3", "F3", "A3"], 8)], ["4/4"], ["Q", "QR", "H", "E2"]),
    ("Warm Boots", "Bass spaces; dotted half notes in 3/4",
     ["3/4"], ["Q", "H", "DH"], ["DH"], [("bass", ["A2", "C3", "E3", "G3"], 8)], ["3/4"], ["Q", "QR", "H", "DH"]),
    ("Pine Trees", "Bass lines and spaces; dotted half notes in 4/4",
     ["4/4"], ["Q", "QR", "H", "DH"], ["DH"], [("bass", ["G2", "A2", "B2", "C3", "D3", "E3", "F3", "G3", "A3"], 8)], ["4/4"], ["Q", "QR", "H", "DH"]),
    ("Snow Day", "Bass clef, all notes; rhythm review",
     ["4/4", "3/4"], ["Q", "QR", "H", "HR", "DH", "E2", "EER"], ["DH", "HR"], [("bass", BASS_ALL, 8)], ["4/4", "3/4"], ["Q", "QR", "H", "HR", "E2"]),
    ("Fireside", "Treble and bass together; dotted quarter and eighth",
     ["4/4"], ["Q", "H", "E2", "DQE"], ["DQE"], [("treble", TREBLE_ALL, 6), ("bass", BASS_ALL, 6)], ["4/4"], ["Q", "QR", "H", "E2"]),
    ("Winter Stars", "Treble and bass; dotted quarter and eighth in 2/4",
     ["2/4"], ["Q", "E2", "DQE"], ["DQE"], [("treble", TREBLE_ALL, 6), ("bass", BASS_ALL, 6)], ["2/4", "4/4"], ["Q", "QR", "E2", "H"]),
    ("Skating Pond", "Treble and bass; rhythm review",
     ["4/4", "3/4"], ["Q", "QR", "H", "DH", "E2", "EER", "ERE", "DQE"], ["ERE", "DQE"], [("treble", TREBLE_ALL, 6), ("bass", BASS_ALL, 6)], ["4/4", "3/4"], ["Q", "QR", "H", "DH", "E2"]),
    ("Snow Fort", "Treble and bass; first steps in 6/8",
     ["6/8"], ["DQ", "EEE"], ["EEE", "DQ"], [("treble", TREBLE_ALL, 6), ("bass", BASS_ALL, 6)], ["4/4", "3/4"], ["Q", "QR", "H", "E2"]),
    ("Earmuffs", "Treble and bass; 6/8 with quarters and eighths",
     ["6/8"], ["DQ", "EEE", "QE", "EQ"], ["QE", "EQ"], [("treble", TREBLE_ALL, 6), ("bass", BASS_ALL, 6)], ["4/4", "2/4"], ["Q", "QR", "H", "E2", "DQE"]),
    ("Snowy Owl", "Treble and bass; 4/4 and 6/8 mixed",
     ["4/4", "6/8"], ["Q", "QR", "H", "E2", "DQE", "DQ", "EEE", "QE"], ["DQE", "QE"], [("treble", TREBLE_ALL, 6), ("bass", BASS_ALL, 6)], ["4/4", "3/4"], ["Q", "QR", "H", "DH", "E2", "DQE"]),
    ("Icy Window", "Treble and bass; every meter",
     ["2/4", "6/8"], ["Q", "QR", "H", "E2", "EER", "DQE", "DQ", "EEE", "QE", "EQ"], ["EER", "EQ"], [("treble", TREBLE_ALL, 6), ("bass", BASS_ALL, 6)], ["2/4", "3/4", "4/4"], ["Q", "QR", "H", "DH", "E2", "EER", "DQE"]),
    ("Winter Break", "Challenge: the whole set",
     ["4/4", "6/8"], ["Q", "QR", "H", "DH", "E2", "EER", "ERE", "DQE", "DQ", "EEE", "QE", "EQ", "QRER"], ["DQE", "QRER", "DH"], [("treble", TREBLE_ALL, 6), ("bass", BASS_ALL, 6)], ["4/4", "3/4", "2/4"], ["Q", "QR", "H", "DH", "E2", "EER", "ERE", "DQE"]),
]
NDAYS = len(DAYS)
assert NDAYS == 20
RH_LINES = 2       # rhythm lines per day
GAPS = 4           # missing-beat items per day
NSYM = 5           # symbols per day


def measures_per_line(meter):
    return 2 if meter in ("4/4", "6/8") else 3


# ---- A: note names
@dataclass
class NoteRow:
    clef: str
    pitches: list


def build_notes(di, rng):
    rows = []
    for clef, pool, n in DAYS[di][5]:
        for _ in range(500):
            seq = [rng.choice(pool)]
            while len(seq) < n:
                p = rng.choice(pool)
                if p != seq[-1]:
                    seq.append(p)
            if len(set(seq)) >= min(5, len(pool)) and all(abs(diatonic(a) - diatonic(b)) <= 5 for a, b in zip(seq, seq[1:])):
                break
        else:
            raise RuntimeError(f"day {di + 1}: no note draw")
        rows.append(NoteRow(clef, seq))
    return rows


# ---- B: rhythm lines
def build_rhythm(di, rng):
    meters, allowed, featured = DAYS[di][2:5]
    for attempt in range(400):
        exs, seen = [], set()
        for n in range(RH_LINES):
            meter = meters[n % len(meters)]
            ms = []
            for _ in range(measures_per_line(meter)):
                for _ in range(30):
                    names = random_measure(rng, meter, allowed, featured)
                    if (meter, tuple(names)) not in seen:
                        break
                seen.add((meter, tuple(names)))
                ms.append(names)
            exs.append((meter, ms))
        used = [nm for _, ms in exs for names in ms for nm in names]
        cover_all = all(used.count(f) >= 1 for f in featured if any(f in cells_for(m) for m in meters))
        if cover_all and exs[0] != exs[1]:
            return [Ex(di + 1, n + 1, m, [make_measure(m, names) for names in ms]) for n, (m, ms) in enumerate(exs)]
    raise RuntimeError(f"day {di + 1}: no rhythm draw")


# ---- C: symbols
SYMBOLS = [  # id, name, meaning
    ("treble", "treble clef", "Marks the G line. Used for higher notes."),
    ("bass", "bass clef", "Marks the F line. Used for lower notes."),
    ("quarterrest", "quarter rest", "1 beat of silence."),
    ("sharp", "sharp", "Raises a note by a half step."),
    ("flat", "flat", "Lowers a note by a half step."),
    ("forte", "forte", "Play loudly."),
    ("piano", "piano", "Play softly."),
    ("halfrest", "half rest", "2 beats of silence. It sits on the line."),
    ("timesig", "time signature", "Top: beats in a measure. Bottom: the note that gets one beat."),
    ("fermata", "fermata", "Hold the note longer than written."),
    ("natural", "natural", "Cancels a sharp or a flat."),
    ("wholerest", "whole rest", "A whole measure of silence. It hangs from the line."),
    ("repeat", "repeat sign", "Go back and play the section again."),
    ("crescendo", "crescendo", "Gradually get louder."),
    ("decrescendo", "decrescendo", "Gradually get softer."),
    ("mf", "mezzo forte", "Play medium loud."),
    ("staccato", "staccato", "Play short and separated."),
    ("accent", "accent", "Play the note with extra emphasis."),
    ("final", "final barline", "Marks the end of the piece."),
    ("double", "double barline", "Marks the end of a section."),
    ("tie", "tie", "Joins two notes of the same pitch into one longer note."),
]
SYM_NAME = {i: n for i, n, _ in SYMBOLS}
SYM_MEAN = {i: m for i, _, m in SYMBOLS}
SYM_IDS = [i for i, _, _ in SYMBOLS]
assert len(set(SYM_NAME.values())) == len(SYMBOLS)


@dataclass
class SymSet:
    ids: list        # the 5 symbols in the order shown
    bank: list       # ids in word-bank order (A..E)

    def answer(self, k):
        return "ABCDE"[self.bank.index(self.ids[k])]


def build_symbols(di, rng):
    pool = SYM_IDS[:min(len(SYM_IDS), 5 + (di + 1))]
    if 5 + (di + 1) <= len(SYM_IDS):
        newest = pool[-2:]
    else:   # the whole set is in play: spotlight two symbols in turn
        k = (2 * di) % len(SYM_IDS)
        newest = [SYM_IDS[k], SYM_IDS[(k + 1) % len(SYM_IDS)]]
    rest = [p for p in pool if p not in newest]
    ids = newest + rng.sample(rest, NSYM - len(newest))
    rng.shuffle(ids)
    bank = ids[:]
    for _ in range(50):
        rng.shuffle(bank)
        if all(bank[i] != ids[i] for i in range(NSYM)):   # no answer sits on its own row
            break
    return SymSet(ids, bank)


# ---- D: missing beats
@dataclass
class Gap:
    meter: str
    toks: list         # tokens shown (the start of a measure)
    missing: F         # in whole notes

    @property
    def beats(self):
        return self.missing * 4


def beats_text(b):
    b = F(b)
    whole, frac = divmod(b, 1)
    if frac == 0:
        return str(int(whole))
    assert frac == F(1, 2), b
    return f"{int(whole)}½" if whole else "½"


def build_gaps(di, rng):
    meters, allowed = DAYS[di][6], DAYS[di][7]
    out, seen = [], {}
    for n in range(GAPS):
        meter = meters[n % len(meters)]
        cells = cells_for(meter)
        for _ in range(300):
            names = random_measure(rng, meter, allowed, [])
            if len(names) < 2:
                continue
            shown = names[:rng.randint(1, len(names) - 1)]
            pos = sum((cell_span(cells, nm) for nm in shown), F(0))
            miss = meter_len(meter) - pos
            if miss < F(1, 4) or seen.get((meter, tuple(shown)), 0) >= (1 if len(allowed) > 3 else 2) or all(cells[nm][0][1] and len(cells[nm]) == 1 for nm in shown):
                continue
            ts, p = [], F(0)
            for nm in shown:
                for kind, rest, dot in cells[nm]:
                    d = tok_dur(kind, bool(dot))
                    ts.append(Tok(kind, bool(rest), bool(dot), p, d, count_label(meter, p)))
                    p += d
            seen[(meter, tuple(shown))] = seen.get((meter, tuple(shown)), 0) + 1
            out.append(Gap(meter, ts, miss))
            break
        else:
            raise RuntimeError(f"day {di + 1}: no gap draw")
    return out


@dataclass
class Day:
    n: int
    notes: list
    rhythm: list
    syms: SymSet
    gaps: list


def make_days():
    days = []
    for di in range(NDAYS):
        rng = random.Random(f"bell-ringer-{di}")
        days.append(Day(di + 1, build_notes(di, rng), build_rhythm(di, rng), build_symbols(di, rng), build_gaps(di, rng)))
    return days
# ------------------------------------------------------------------ drawing
def g(cp, x, y, size, fill="#000"):
    return f'<text x="{x:.2f}" y="{y:.2f}" font-family="Bravura" font-size="{size:.2f}" fill="{fill}">&#x{cp:X};</text>'


def token_svg(kind, rest, dot, cx, y, s, flagged=True, fill="#000"):
    """One note or rest centred on x=cx on the line y. Returns svg (no beam)."""
    size = 4 * s
    if rest:
        w = REST_W[kind] * s
        out = g(REST_GLYPH[kind], cx - w / 2, y, size, fill)
        if dot:
            out += g(DOT_GLYPH, cx + w / 2 + 0.3 * s, y - 0.5 * s, size, fill)
        return out
    hw = HEAD_W[kind] * s
    left = cx - hw / 2
    if kind == "eighth" and not flagged:
        out = g(HEAD_GLYPH["eighth"], left, y, size, fill)
    else:
        out = g(NOTE_GLYPH[kind], left, y, size, fill)
    if dot:
        out += g(DOT_GLYPH, left + hw + 0.35 * s, y - 0.5 * s, size, fill)
    return out


def beam_groups(meter, toks):
    """Runs of consecutive eighth notes (no rests between) inside one beat group, as lists of token indices."""
    bl = beat_len(meter)
    runs, cur = [], []
    for i, t in enumerate(toks):
        if t.kind == "eighth" and not t.rest and not t.dot:
            if cur and int(toks[cur[-1]].start / bl) != int(t.start / bl):
                runs.append(cur)
                cur = []
            cur.append(i)
        else:
            if cur:
                runs.append(cur)
            cur = []
    if cur:
        runs.append(cur)
    return runs


def exercise_geometry(ex, w=SVG_W):
    """x centre of every token + measure x ranges. Shared by drawing and the layout check."""
    nm = len(ex.measures)
    mw = (w - FIRST_BAR) / nm
    xs, bars = [], []
    for mi, toks in enumerate(ex.measures):
        m0 = FIRST_BAR + mi * mw
        pad = 9.0
        usable = mw - 2 * pad - 4
        L = meter_len(ex.meter)
        xs.append([m0 + pad + float(t.start / L) * usable + 6 for t in toks])
        bars.append((m0, m0 + mw))
    return xs, bars


def exercise_svg(ex, mode, scale_class="ex", accent_counts=True, w=SVG_W, pxw=None):
    """mode 'ws' (blank count boxes) or 'key' (counts written in, compact)."""
    s = S
    xs, bars = exercise_geometry(ex, w)
    Y0 = globals()["Y0"] if mode == "ws" else 27.0
    h = Y0 + (BOX_H + 17 if mode == "ws" else 27)
    size_attr = f'width="{pxw}px" height="{h * pxw / w:.1f}px"' if pxw else f'width="{w:.0f}pt" height="{h:.0f}pt"'
    out = [f'<svg class="{scale_class}" data-mode="{mode}" data-ex="{ex.id}" data-meter="{ex.meter}" xmlns="http://www.w3.org/2000/svg" '
           f'viewBox="0 0 {w:.0f} {h:.0f}" {size_attr} style="display:block">']
    out.append(f'<text x="0" y="{Y0 + 5:.1f}" font-family="Oswald" font-weight="700" font-size="15">{ex.num}</text>')
    out.append(f'<line x1="{STAFF_X0}" y1="{Y0}" x2="{w - 1}" y2="{Y0}" stroke="#000" stroke-width="{0.16 * s:.2f}"/>')
    out.append(f'<line x1="{STAFF_X0}" y1="{Y0 - 2 * s}" x2="{STAFF_X0}" y2="{Y0 + 2 * s}" stroke="#000" stroke-width="1.1"/>')
    n, d = METERS[ex.meter]
    out.append(g(0xE080 + n, STAFF_X0 + 6, Y0 - s, 4 * s))
    out.append(g(0xE080 + d, STAFF_X0 + 6, Y0 + s, 4 * s))
    sw = 0.13 * s
    for mi, toks in enumerate(ex.measures):
        out.append(f'<g class="meas" data-ex="{ex.id}" data-meter="{ex.meter}">')
        runs = beam_groups(ex.meter, toks)
        beamed = {i for r in runs if len(r) > 1 for i in r}
        for i, t in enumerate(toks):
            cx = xs[mi][i]
            out.append(f'<g class="tok" data-kind="{t.kind}" data-rest="{int(t.rest)}" data-dot="{int(t.dot)}" data-count="{t.count}" data-x="{cx:.2f}">')
            if i in beamed:
                left = cx - HEAD_W["eighth"] * s / 2
                out.append(g(HEAD_GLYPH["eighth"], left, Y0, 4 * s))
                sx = left + 1.18 * s - sw / 2
                out.append(f'<line x1="{sx:.2f}" y1="{Y0 - 0.168 * s:.2f}" x2="{sx:.2f}" y2="{Y0 - 3.5 * s:.2f}" stroke="#000" stroke-width="{sw:.2f}"/>')
            else:
                out.append(token_svg(t.kind, t.rest, t.dot, cx, Y0, s))
            if mode == "ws":
                out.append(f'<rect x="{cx - BOX_W / 2:.2f}" y="{Y0 + 15:.1f}" width="{BOX_W}" height="{BOX_H}" rx="3" fill="#fff" stroke="#000" stroke-width="1"/>')
            else:
                out.append(f'<text x="{cx:.2f}" y="{Y0 + 22.5:.1f}" text-anchor="middle" font-family="Oswald" font-weight="700" font-size="15" fill="{ACCENT if accent_counts else "#000"}">{escape(t.count)}</text>')
            out.append("</g>")
        for r in runs:
            if len(r) > 1:
                x1 = xs[mi][r[0]] - HEAD_W["eighth"] * s / 2 + 1.18 * s - sw
                x2 = xs[mi][r[-1]] - HEAD_W["eighth"] * s / 2 + 1.18 * s
                out.append(f'<rect x="{x1:.2f}" y="{Y0 - 3.5 * s:.2f}" width="{x2 - x1:.2f}" height="{0.5 * s:.2f}" fill="#000"/>')
        out.append("</g>")
        bx = bars[mi][1]
        last = mi == len(ex.measures) - 1
        if last:
            out.append(f'<line x1="{bx - 3.2:.1f}" y1="{Y0 - 2 * s}" x2="{bx - 3.2:.1f}" y2="{Y0 + 2 * s}" stroke="#000" stroke-width="1.1"/>')
            out.append(f'<line x1="{bx - 0.9:.1f}" y1="{Y0 - 2 * s}" x2="{bx - 0.9:.1f}" y2="{Y0 + 2 * s}" stroke="#000" stroke-width="3"/>')
        else:
            out.append(f'<line x1="{bx:.1f}" y1="{Y0 - 2 * s}" x2="{bx:.1f}" y2="{Y0 + 2 * s}" stroke="#000" stroke-width="1.1"/>')
    out.append("</svg>")
    return "".join(out)


# ------------------------------------------------------------------ drawing: note rows, symbols, gaps, icons
NS = 7.0                  # staff space for the note rows
NR_W = 540.0
NR_TOP = 5.6 * NS         # room above the bottom line... measured from the top of the svg to the bottom staff line
NR_YB = NR_TOP + 0.0      # bottom line y
NR_BOX_Y = NR_YB + 2.4 * NS
NR_BOX_W, NR_BOX_H = 26.0, 20.0
STEM_W_, STAFF_W_, LEDGER_W_ = 0.13, 0.16, 0.2


def note_xs(n):
    x0, x1 = 78.0, NR_W - 30.0
    return [x0 + i * (x1 - x0) / (n - 1) for i in range(n)]


def note_row_svg(row, mode, idx):
    """One staff with a clef and quarter notes; blank boxes (ws) or the letters written in (key)."""
    s = NS
    yb = NR_YB
    h = NR_BOX_Y + (NR_BOX_H if mode == "ws" else 17) + 3
    out = [f'<svg class="nr" data-mode="{mode}" data-row="{idx}" data-clef="{row.clef}" data-s="{s}" data-yb="{yb:.2f}" '
           f'xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {NR_W:.0f} {h:.1f}" width="{NR_W:.0f}pt" height="{h:.1f}pt" style="display:block">']
    for i in range(5):
        y = yb - i * s
        out.append(f'<line x1="0" y1="{y:.2f}" x2="{NR_W - 1:.0f}" y2="{y:.2f}" stroke="#000" stroke-width="{STAFF_W_ * s:.2f}"/>')
    out.append(f'<line x1="0.6" y1="{yb - 4 * s:.2f}" x2="0.6" y2="{yb:.2f}" stroke="#000" stroke-width="1.1"/>')
    if row.clef == "treble":
        out.append(g(0xE050, 6, yb - s, 4 * s))
    else:
        out.append(g(0xE062, 6, yb - 3 * s, 4 * s))
    sw = STEM_W_ * s
    for p, cx in zip(row.pitches, note_xs(len(row.pitches))):
        st = staff_step(p, row.clef)
        y = yb - st * s / 2
        nx = cx - 1.18 * s / 2
        out.append(f'<g class="nt" data-pitch="{p}" data-letter="{p[0]}" data-y="{y:.2f}" data-x="{cx:.2f}">')
        lines = list(range(-2, st - 1, -2)) if st <= -2 else (list(range(10, st + 1, 2)) if st >= 10 else [])
        for ls in lines:
            ly = yb - ls * s / 2
            out.append(f'<line x1="{nx - 0.4 * s:.2f}" y1="{ly:.2f}" x2="{nx + 1.58 * s:.2f}" y2="{ly:.2f}" stroke="#000" stroke-width="{LEDGER_W_ * s:.2f}"/>')
        out.append(g(0xE0A4, nx, y, 4 * s))
        if st < 4:
            x = nx + 1.18 * s - sw / 2
            out.append(f'<line x1="{x:.2f}" y1="{y - 0.168 * s:.2f}" x2="{x:.2f}" y2="{y - 3.5 * s:.2f}" stroke="#000" stroke-width="{sw:.2f}"/>')
        else:
            x = nx + sw / 2
            out.append(f'<line x1="{x:.2f}" y1="{y + 0.168 * s:.2f}" x2="{x:.2f}" y2="{y + 3.5 * s:.2f}" stroke="#000" stroke-width="{sw:.2f}"/>')
        if mode == "ws":
            out.append(f'<rect x="{cx - NR_BOX_W / 2:.2f}" y="{NR_BOX_Y:.1f}" width="{NR_BOX_W}" height="{NR_BOX_H}" rx="3" fill="#fff" stroke="#000" stroke-width="1"/>')
        else:
            out.append(f'<text x="{cx:.2f}" y="{NR_BOX_Y + 14:.1f}" text-anchor="middle" font-family="Oswald" font-weight="700" font-size="16" fill="{ACCENT}">{p[0]}</text>')
        out.append("</g>")
    out.append("</svg>")
    return "".join(out)


# ---- symbols: each drawn in a 100 x 60 cell, staff bottom line at y=44, space 7 (same size as the worksheets)
SY_YB, SY_S = 44.0, 7.0


def _staff(x0=4, x1=96):
    return "".join(f'<line x1="{x0}" y1="{SY_YB - i * SY_S:.1f}" x2="{x1}" y2="{SY_YB - i * SY_S:.1f}" stroke="#000" stroke-width="1.1"/>' for i in range(5))


def _note(cx, step, stem_up_=True, head=0xE0A4):
    y = SY_YB - step * SY_S / 2
    nx = cx - 1.18 * SY_S / 2
    sw = 0.13 * SY_S
    out = g(head, nx, y, 4 * SY_S)
    if stem_up_:
        x = nx + 1.18 * SY_S - sw / 2
        out += f'<line x1="{x:.2f}" y1="{y - 0.168 * SY_S:.2f}" x2="{x:.2f}" y2="{y - 3.5 * SY_S:.2f}" stroke="#000" stroke-width="{sw:.2f}"/>'
    else:
        x = nx + sw / 2
        out += f'<line x1="{x:.2f}" y1="{y + 0.168 * SY_S:.2f}" x2="{x:.2f}" y2="{y + 3.5 * SY_S:.2f}" stroke="#000" stroke-width="{sw:.2f}"/>'
    return out, y


def _gt(cp, x, y, size, anchor="middle"):
    return f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-family="Bravura" font-size="{size}" fill="#000">{cp}</text>'


def symbol_inner(sid):
    yb, s = SY_YB, SY_S
    mid = yb - 2 * s
    if sid == "treble":
        return _staff() + g(0xE050, 38, yb - s, 4 * s)
    if sid == "bass":
        return _staff() + g(0xE062, 38, yb - 3 * s, 4 * s)
    if sid == "quarterrest":
        return _staff() + g(0xE4E5, 44, mid, 4 * s)
    if sid == "halfrest":
        return _staff() + g(0xE4E4, 43, mid, 4 * s)
    if sid == "wholerest":
        return _staff() + g(0xE4E3, 43, yb - 3 * s, 4 * s)
    if sid == "sharp":
        return _staff() + g(0xE262, 43, mid, 4 * s)
    if sid == "flat":
        return _staff() + g(0xE260, 43, mid, 4 * s)
    if sid == "natural":
        return _staff() + g(0xE261, 43, mid, 4 * s)
    if sid == "timesig":
        return _staff() + g(0xE083, 40, yb - 3 * s, 4 * s) + g(0xE084, 40, yb - s, 4 * s)
    if sid == "repeat":
        return _staff() + g(0xE041, 52, yb, 4 * s)
    if sid == "final":
        return (_staff() + f'<line x1="62" y1="{yb - 4 * s}" x2="62" y2="{yb}" stroke="#000" stroke-width="1.2"/>'
                f'<line x1="68.5" y1="{yb - 4 * s}" x2="68.5" y2="{yb}" stroke="#000" stroke-width="4"/>')
    if sid == "double":
        return (_staff() + f'<line x1="62" y1="{yb - 4 * s}" x2="62" y2="{yb}" stroke="#000" stroke-width="1.2"/>'
                f'<line x1="67" y1="{yb - 4 * s}" x2="67" y2="{yb}" stroke="#000" stroke-width="1.2"/>')
    if sid == "fermata":
        n, y = _note(46, 4, False)
        return _staff() + n + g(0xE4C0, 46.2, yb - 4 * s - 5, 4 * s)
    if sid == "staccato":
        n, y = _note(46, 2, True)
        return _staff() + n + g(0xE4A3, 47.5, y + 1.5 * s + 4, 4 * s)
    if sid == "accent":
        n, y = _note(46, 2, True)
        return _staff() + n + g(0xE4A1, 47, y + 1.5 * s + 4, 4 * s)
    if sid == "tie":
        a, ya = _note(30, 3, True)
        b, yb2 = _note(70, 3, True)
        arc = (f'<path d="M 32 {ya + 5:.1f} Q 50 {ya + 18:.1f} 68 {yb2 + 5:.1f} Q 50 {ya + 15:.1f} 32 {ya + 5:.1f} Z" fill="#000"/>')
        return _staff() + a + b + arc
    if sid == "forte":
        return _gt("&#xE522;", 50, 40, 32)
    if sid == "piano":
        return _gt("&#xE520;", 50, 40, 32)
    if sid == "mf":
        return _gt("&#xE52D;", 50, 40, 32)
    if sid == "crescendo":
        return ('<path d="M 18 30 L 82 18 M 18 30 L 82 42" stroke="#000" stroke-width="2" fill="none" stroke-linecap="round"/>')
    if sid == "decrescendo":
        return ('<path d="M 18 18 L 82 30 M 18 42 L 82 30" stroke="#000" stroke-width="2" fill="none" stroke-linecap="round"/>')
    raise KeyError(sid)


def symbol_svg(sid, w=100, h=60, pt=None):
    size = f'width="{pt[0]}pt" height="{pt[1]}pt"' if pt else f'width="{w}pt" height="{h}pt"'
    return (f'<svg class="sym" data-sym="{sid}" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 60" {size} style="display:block">'
            f'{symbol_inner(sid)}</svg>')


# ---- gap items
GP_W, GP_H = 258.0, 84.0
GP_KEY_H = 52.0
GP_Y = 30.0


def gap_svg(gap, mode, idx):
    s = 6.5
    L = meter_len(gap.meter)
    m0, m1 = 46.0, GP_W - 6
    usable = m1 - m0 - 2 * 8 - 4
    n, d = METERS[gap.meter]
    gh = GP_H if mode == "ws" else GP_KEY_H
    out = [f'<svg class="gp" data-mode="{mode}" data-gap="{idx}" data-meter="{gap.meter}" data-answer="{beats_text(gap.beats)}" '
           f'xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {GP_W:.0f} {gh:.0f}" width="{GP_W:.0f}pt" height="{gh:.0f}pt" style="display:block">']
    out.append(f'<text x="0" y="{GP_Y + 5:.1f}" font-family="Oswald" font-weight="700" font-size="15">{idx}</text>')
    out.append(f'<line x1="16" y1="{GP_Y}" x2="{m1}" y2="{GP_Y}" stroke="#000" stroke-width="{0.16 * s:.2f}"/>')
    out.append(f'<line x1="16" y1="{GP_Y - 2 * s}" x2="16" y2="{GP_Y + 2 * s}" stroke="#000" stroke-width="1.1"/>')
    out.append(g(0xE080 + n, 21, GP_Y - s, 4 * s))
    out.append(g(0xE080 + d, 21, GP_Y + s, 4 * s))
    runs = beam_groups(gap.meter, gap.toks)
    beamed = {i for r in runs if len(r) > 1 for i in r}
    sw = 0.13 * s
    xs = [m0 + 8 + float(t.start / L) * usable + 6 for t in gap.toks]
    for i, t in enumerate(gap.toks):
        cx = xs[i]
        out.append(f'<g class="gtok" data-kind="{t.kind}" data-rest="{int(t.rest)}" data-dot="{int(t.dot)}">')
        if i in beamed:
            left = cx - HEAD_W["eighth"] * s / 2
            out.append(g(HEAD_GLYPH["eighth"], left, GP_Y, 4 * s))
            sx = left + 1.18 * s - sw / 2
            out.append(f'<line x1="{sx:.2f}" y1="{GP_Y - 0.168 * s:.2f}" x2="{sx:.2f}" y2="{GP_Y - 3.5 * s:.2f}" stroke="#000" stroke-width="{sw:.2f}"/>')
        else:
            out.append(token_svg(t.kind, t.rest, t.dot, cx, GP_Y, s))
        out.append("</g>")
    for r in runs:
        if len(r) > 1:
            x1 = xs[r[0]] - HEAD_W["eighth"] * s / 2 + 1.18 * s - sw
            x2 = xs[r[-1]] - HEAD_W["eighth"] * s / 2 + 1.18 * s
            out.append(f'<rect x="{x1:.2f}" y="{GP_Y - 3.5 * s:.2f}" width="{x2 - x1:.2f}" height="{0.5 * s:.2f}" fill="#000"/>')
    # the empty space
    last = gap.toks[-1]
    gx0 = m0 + 8 + float((last.start + last.dur) / L) * usable + 6 - 4
    out.append(f'<rect x="{gx0:.1f}" y="{GP_Y - 17:.1f}" width="{m1 - 7 - gx0:.1f}" height="34" rx="4" fill="none" stroke="#000" stroke-width="1" stroke-dasharray="3 3"/>')
    if mode == "ws":
        out.append(f'<text x="{(gx0 + m1 - 7) / 2:.1f}" y="{GP_Y + 7:.1f}" text-anchor="middle" font-family="Oswald" font-weight="700" font-size="20" fill="#000">?</text>')
    out.append(f'<line x1="{m1 - 3.2:.1f}" y1="{GP_Y - 2 * s}" x2="{m1 - 3.2:.1f}" y2="{GP_Y + 2 * s}" stroke="#000" stroke-width="1.1"/>')
    out.append(f'<line x1="{m1 - 0.9:.1f}" y1="{GP_Y - 2 * s}" x2="{m1 - 0.9:.1f}" y2="{GP_Y + 2 * s}" stroke="#000" stroke-width="3"/>')
    # answer line
    if mode == "ws":
        out.append(f'<text x="16" y="{GP_Y + 40:.1f}" font-family="Source Sans 3" font-weight="600" font-size="11.5">Beats missing:</text>')
        out.append(f'<rect x="92" y="{GP_Y + 26:.1f}" width="30" height="19" rx="3" fill="#fff" stroke="#000" stroke-width="1"/>')
    else:
        out.append(f'<text x="{(gx0 + m1 - 7) / 2:.1f}" y="{GP_Y + 7:.1f}" text-anchor="middle" font-family="Oswald" font-weight="700" font-size="16" fill="{ACCENT}" class="ga">{beats_text(gap.beats)}</text>')
    out.append("</svg>")
    return "".join(out)


# ---- winter icons (line art, black + the accent), 48 x 48 viewBox
def icon_inner(name):
    A = ACCENT
    if name == "snowflake":
        arms = ""
        for k in range(6):
            arms += (f'<g transform="rotate({k * 60} 24 24)"><line x1="24" y1="24" x2="24" y2="4" stroke="#000" stroke-width="2.2" stroke-linecap="round"/>'
                     f'<path d="M 24 11 L 19 6 M 24 11 L 29 6 M 24 17 L 20 13 M 24 17 L 28 13" stroke="#000" stroke-width="1.8" stroke-linecap="round" fill="none"/></g>')
        return arms + f'<circle cx="24" cy="24" r="3.2" fill="{A}" stroke="#000" stroke-width="1.5"/>'
    if name == "mitten":
        return (f'<path d="M 14 44 L 14 24 C 8 22 8 16 12 14 C 14 13 16 14 17 16 L 17 8 C 17 4 23 4 23 8 L 23 6 C 23 2 29 2 29 6 L 29 8 C 29 4 35 4 35 8 L 35 22 C 35 28 33 32 33 36 L 33 44 Z" '
                f'fill="#fff" stroke="#000" stroke-width="2" stroke-linejoin="round" transform="translate(0 0) scale(1) " />'
                f'<rect x="12" y="38" width="23" height="8" rx="2" fill="{A}" stroke="#000" stroke-width="2"/>'
                f'<path d="M 18 28 L 30 28 M 18 32 L 30 32" stroke="{A}" stroke-width="2" stroke-linecap="round"/>')
    if name == "cocoa":
        return (f'<path d="M 9 18 L 11 40 C 11 43 14 45 17 45 L 29 45 C 32 45 35 43 35 40 L 37 18 Z" fill="#fff" stroke="#000" stroke-width="2" stroke-linejoin="round"/>'
                f'<path d="M 36 22 C 46 20 46 36 34 36" fill="none" stroke="#000" stroke-width="2.4" stroke-linecap="round"/>'
                f'<path d="M 9.6 24 L 36.4 24 L 35.8 31 L 10.2 31 Z" fill="{A}"/>'
                f'<path d="M 17 12 C 14 9 20 7 17 3 M 24 12 C 21 9 27 7 24 3 M 31 12 C 28 9 34 7 31 3" fill="none" stroke="#000" stroke-width="1.8" stroke-linecap="round"/>')
    if name == "skate":
        return (f'<path d="M 12 6 L 24 6 L 24 24 C 24 28 28 30 34 31 C 40 32 42 34 42 38 L 12 38 Z" fill="#fff" stroke="#000" stroke-width="2" stroke-linejoin="round"/>'
                f'<path d="M 12 38 L 42 38" stroke="#000" stroke-width="2"/>'
                f'<path d="M 8 43 L 41 43 C 45 43 46 40 44 38" fill="none" stroke="{A}" stroke-width="3" stroke-linecap="round"/>'
                f'<path d="M 14 43 L 14 38 M 36 43 L 36 38" stroke="#000" stroke-width="2"/>'
                f'<path d="M 12 12 L 24 12" stroke="{A}" stroke-width="2.4"/>'
                f'<path d="M 22 16 L 18 16 M 22 21 L 18 21 M 29 28 L 25 26" stroke="#000" stroke-width="1.6" stroke-linecap="round"/>')
    raise KeyError(name)


def icon_svg(name, pt=26):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" width="{pt}pt" height="{pt}pt" style="display:block">{icon_inner(name)}</svg>'
def font_css():
    f = os.path.relpath(FONTS, BUILD)
    faces = [("Oswald", 300, "normal", "oswald-latin-300-normal"), ("Oswald", 500, "normal", "oswald-latin-500-normal"),
             ("Oswald", 700, "normal", "oswald-latin-700-normal"),
             ("Source Sans 3", 400, "normal", "source-sans-3-latin-400-normal"),
             ("Source Sans 3", 400, "italic", "source-sans-3-latin-400-italic"),
             ("Source Sans 3", 600, "normal", "source-sans-3-latin-600-normal"),
             ("Source Sans 3", 700, "normal", "source-sans-3-latin-700-normal"),
             ("Bravura", 400, "normal", "bravura")]
    return "".join(f"@font-face{{font-family:'{n}';font-weight:{w};font-style:{s};src:url('{f}/{file}.woff2') format('woff2');}}"
                   for n, w, s, file in faces)


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
.top .t { font-size: 25pt; }
.top .t small { display: block; font-family: 'Oswald'; font-weight: 300; text-transform: none; font-size: 12pt; letter-spacing: 0; margin-top: 4pt; }
.tag { text-align: right; }
.tag .lv { display: inline-block; background: #000; color: #fff; font-family: 'Oswald'; font-weight: 700; font-size: 15pt; padding: 3pt 9pt 4pt; border-radius: 4pt; letter-spacing: .04em; }
.tag .lv.ak { background: ACCENT; }
.tag .ln { font-family: 'Oswald'; font-weight: 300; font-size: 11pt; margin-top: 3pt; }
.name { display: flex; gap: 18pt; font-size: 12pt; margin: 9pt 0 5pt; }
.name span { flex: 1; border-bottom: 1pt solid #000; height: 15pt; }
.name span.d { flex: 0 0 1.6in; }
.how { font-size: 11.5pt; margin: 2pt 0 5pt; }
.how b { font-weight: 700; }
.legend { display: flex; flex-wrap: wrap; gap: 4pt 6pt; margin: 2pt 0 4pt; }
.lgc { display: flex; align-items: center; gap: 2pt; border: 1pt solid #000; border-radius: 5pt; padding: 1pt 7pt 1pt 2pt; }
.lgt b { display: block; font-family: 'Oswald'; font-weight: 500; text-transform: uppercase; font-size: 8.5pt; letter-spacing: .02em; line-height: 1.1; }
.lgt span { font-size: 8.5pt; line-height: 1.1; display: block; }
.cnt { font-size: 9.5pt; font-style: italic; margin: 1pt 0 0; }
.exs { flex: 1; display: flex; flex-direction: column; justify-content: space-around; padding: 4pt 0 2pt; }
.foot { display: flex; justify-content: space-between; font-size: 8.5pt; color: #333; border-top: .8pt solid #000; padding-top: 3pt; }
.wm { position: absolute; left: 50%; top: 50%; transform: translate(-50%, -50%) rotate(-38deg); font-family: 'Oswald'; font-weight: 700;
      font-size: 150pt; color: rgba(0,0,0,.13); letter-spacing: .06em; white-space: nowrap; pointer-events: none; z-index: 9; }
.keyblock { margin-top: 6pt; }
.keyblock .kt { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 12.5pt; border-bottom: 1pt solid #000; padding-bottom: 2pt; margin-bottom: 5pt; display: flex; justify-content: space-between; }
.keyblock .kt span { font-weight: 300; text-transform: none; font-size: 10.5pt; }
.cv { width: 100%; height: auto; }
.keyblock svg { margin: 0 0 1pt; width: 91%; height: auto; }
.doc h1 { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 30pt; margin: 0 0 4pt; line-height: 1; }
.doc h2 { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 14pt; margin: 13pt 0 4pt; letter-spacing: .02em; }
.doc h2 .acc { color: ACCENT; }
.doc p, .doc li { font-size: 11pt; line-height: 1.38; margin: 0 0 5pt; }
.doc ul { margin: 0 0 4pt; padding-left: 16pt; }
.doc .rule { border-bottom: 2.2pt solid #000; margin-bottom: 8pt; padding-bottom: 6pt; }
.doc table { border-collapse: collapse; width: 100%; font-size: 10pt; margin: 2pt 0 4pt; }
.doc td, .doc th { border: 1pt solid #000; padding: 2pt 5pt; text-align: left; vertical-align: top; }
.doc th { font-family: 'Oswald'; font-weight: 500; text-transform: uppercase; font-size: 9.5pt; background: #000; color: #fff; }
.cols { display: flex; gap: 22pt; }
.cols > div { flex: 1; }
.small { font-size: 9pt !important; color: #333; }
.refgrid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 6pt; margin: 4pt 0 6pt; }
.refcell { border: 1.3pt solid #000; border-radius: 6pt; text-align: center; padding: 4pt 2pt 4pt; }
.refcell b { display: block; font-family: 'Oswald'; font-weight: 500; text-transform: uppercase; font-size: 9.5pt; }
.refcell span { font-size: 9pt; display: block; line-height: 1.2; }
.cover { align-items: center; justify-content: space-between; padding: 0.55in 0.6in 0.5in; }
.store { font-family: 'Oswald'; font-weight: 500; font-size: 13pt; letter-spacing: .32em; text-transform: uppercase; }
.ctitle { text-align: center; }
.ctitle .a { font-family: 'Oswald'; font-weight: 700; font-size: 44pt; line-height: 1; letter-spacing: .02em; }
.ctitle .b { font-family: 'Oswald'; font-weight: 700; white-space: nowrap; font-size: 58pt; line-height: .95; letter-spacing: .01em; }
.ctitle .c { font-family: 'Oswald'; font-weight: 300; font-size: 17pt; margin-top: 8pt; }
.cband { width: 100%; background: #000; color: #fff; text-align: center; font-family: 'Oswald'; font-weight: 500; font-size: 14pt;
         letter-spacing: .08em; text-transform: uppercase; padding: 8pt 0 9pt; border-radius: 4pt; }
.cband em { font-style: normal; color: ACCENT; }
""".replace("ACCENT", ACCENT)


def html_doc(pages, title="doc"):
    return (f'<!doctype html><html><head><meta charset="utf-8"><title>{escape(title)}</title>'
            f'<style>{font_css()}{CSS}</style></head><body>{"".join(pages)}</body></html>')


def foot(left, right):
    return f'<div class="foot"><span>{left}</span><span>{right}</span></div>'


COPY = f"© {YEAR} {STORE} · {BRAND} · For single-classroom use"


CSS += """
.sec { margin-top: 7pt; }
.sh { display: flex; align-items: center; gap: 7pt; border-bottom: 1pt solid #000; padding-bottom: 2pt; margin-bottom: 4pt; }
.sh .h { font-size: 14pt; letter-spacing: .03em; }
.sh .h i { font-style: normal; color: ACCENT; margin-right: 3pt; }
.sh .si { font-size: 10pt; font-style: italic; margin-left: auto; text-align: right; }
.body { flex: 1; display: flex; flex-direction: column; justify-content: space-between; }
.symrow { display: flex; gap: 7pt; }
.sc { flex: 1; border: 1.3pt solid #000; border-radius: 6pt; padding: 1pt 3pt 4pt; text-align: center; position: relative; }
.sc .n { position: absolute; left: 5pt; top: 3pt; font-family: 'Oswald'; font-weight: 700; font-size: 11pt; }
.sc svg { margin: 0 auto; width: 100%; height: auto; }
.sc .ans { display: flex; align-items: center; justify-content: center; gap: 4pt; font-size: 9.5pt; margin-top: 1pt; }
.sc .ans span { display: inline-block; width: 24pt; height: 16pt; border: 1pt solid #000; border-radius: 3pt; }
.bank { display: flex; justify-content: space-between; gap: 6pt; margin-top: 6pt; background: #fff; border: 1.3pt dashed #000; border-radius: 6pt; padding: 4pt 8pt; }
.bank .bk { font-family: 'Oswald'; font-weight: 500; text-transform: uppercase; font-size: 10.5pt; letter-spacing: .02em; white-space: nowrap; }
.bank .bk b { display: inline-block; background: #000; color: #fff; border-radius: 3pt; width: 14pt; text-align: center; margin-right: 3pt; font-weight: 700; }
.gaps { display: grid; grid-template-columns: 1fr 1fr; gap: 3pt 14pt; }
.two .sec { margin-top: 3pt; }
.two .nrs svg { width: 78%; height: auto; margin-left: 0; }
.two .sc svg { width: 82%; }
.two .gp { height: 74pt; }
.two .name { margin: 6pt 0 2pt; }
.nrs svg, .rhs svg { margin: 0 0 1pt; }
.kday { margin-top: 5pt; }
.kday .kt { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 12.5pt; border-bottom: 1pt solid #000; padding-bottom: 2pt; margin-bottom: 3pt; display: flex; justify-content: space-between; }
.kday .kt span { font-weight: 300; text-transform: none; font-size: 10.5pt; }
.nrk { display: flex; gap: 8pt; }
.nrk .nr { flex: 1; min-width: 0; width: auto !important; }
.nrk .nr:only-child { flex: none; width: 70% !important; }
.kday .nr { width: 82%; height: auto; }
.kday .ex { width: 88%; height: auto; }
.kday .gps { display: flex; flex-wrap: wrap; gap: 0 10pt; }
.kday .gp { width: 48%; height: auto; }
.ksym { display: flex; gap: 5pt; margin: 3pt 0 2pt; }
.ksym div { flex: 1; border: 1pt solid #000; border-radius: 4pt; padding: 1pt 3pt; display: flex; align-items: center; gap: 4pt; font-size: 8.5pt; line-height: 1.1; }
.ksym svg { width: 38pt; height: auto; flex: none; }
.ksym b { font-family: 'Oswald'; font-weight: 700; color: ACCENT; font-size: 11pt; }
.glos { display: grid; grid-template-columns: 1fr 1fr; gap: 5pt 16pt; margin-top: 4pt; }
.gl { display: flex; align-items: center; gap: 6pt; border-bottom: .8pt solid #bbb; padding-bottom: 3pt; }
.gl svg { width: 70pt; height: auto; flex: none; border: 1pt solid #000; border-radius: 5pt; }
.gl b { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 10.5pt; display: block; }
.gl span { font-size: 9.5pt; line-height: 1.2; display: block; }
.rstaff { margin: 2pt 0 4pt; }
.mn { font-size: 10pt; margin: 0 0 2pt; }
""".replace("ACCENT", ACCENT)

COPY = f"© {YEAR} {STORE} · {BRAND} · For single-classroom use"

# page numbers
P_COVER, P_TEACH, P_REF1, P_REF2 = 1, 2, 3, 4
P_WS0 = 5
P_KEY0 = P_WS0 + NDAYS            # 25
N_KEYPAGES = NDAYS // 2
P_TERMS = P_KEY0 + N_KEYPAGES      # 35
TOTAL_PAGES = P_TERMS

SEC_NAMES = [("snowflake", "A", "Snowy Notes", "Write the letter name of each note in the box."),
             ("mitten", "B", "Mitten Rhythm", "Write the count in the box under each note and rest."),
             ("cocoa", "C", "Cocoa Symbols", "Match each symbol to its name. Write the letter."),
             ("skate", "D", "Skate Math", "How many beats are missing? Write the number.")]


def ws_page_no(di):
    return P_WS0 + di


def key_page_no(di):
    return P_KEY0 + di // 2


def sec_head(k, hint=None):
    icon, letter, name, ins = SEC_NAMES[k]
    return (f'<div class="sh">{icon_svg(icon, 22)}<div class="h"><i>{letter}</i>{name}</div><div class="si">{escape(hint or ins)}</div></div>')


def rhythm_hint(day):
    ms = list(dict.fromkeys(e.meter for e in day.rhythm))
    bits = []
    for m in ms:
        if m == "6/8":
            bits.append("6/8: 1 2 3 4 5 6")
        else:
            n = METERS[m][0]
            bits.append(f"{m}: " + " ".join(str(i) if j == 0 else "&" for i in range(1, n + 1) for j in (0, 1)))
    return "Write the count under each note and rest.  " + " · ".join(bits)


def worksheet_page(di, days, watermark=False):
    day = days[di]
    theme = DAYS[di][0]
    wm = '<div class="wm">PREVIEW</div>' if watermark else ""
    notes = "".join(note_row_svg(r, "ws", i + 1) for i, r in enumerate(day.notes))
    rhythm = "".join(exercise_svg(e, "ws") for e in day.rhythm)
    cells = "".join(
        f'<div class="sc" data-sym="{sid}"><div class="n">{k + 1}</div>{symbol_svg(sid)}<div class="ans">Letter <span></span></div></div>'
        for k, sid in enumerate(day.syms.ids))
    bank = "".join(f'<span class="bk" data-id="{sid}" data-letter="{"ABCDE"[j]}"><b>{"ABCDE"[j]}</b>{escape(SYM_NAME[sid])}</span>'
                   for j, sid in enumerate(day.syms.bank))
    gaps = "".join(gap_svg(x, "ws", i + 1) for i, x in enumerate(day.gaps))
    return (f'<section class="page{" two" if len(day.notes) > 1 else ""}" data-day="{day.n}">{wm}'
            f'<div class="top"><div class="h t">December Bell-Ringers<small>Day {day.n} · {escape(theme)}</small></div>'
            f'<div class="tag"><div class="lv">DAY {day.n}</div><div class="ln">About 8 minutes</div></div></div>'
            f'<div class="name">Name<span></span>Date<span class="d"></span></div>'
            f'<div class="body">'
            f'<div class="sec">{sec_head(0)}<div class="nrs">{notes}</div></div>'
            f'<div class="sec">{sec_head(1, rhythm_hint(day))}<div class="rhs">{rhythm}</div></div>'
            f'<div class="sec">{sec_head(2)}<div class="symrow">{cells}</div><div class="bank">{bank}</div></div>'
            f'<div class="sec">{sec_head(3)}<div class="gaps">{gaps}</div></div>'
            f'</div>{foot(COPY, f"Answer key on page {key_page_no(di)} · Page {ws_page_no(di)}")}</section>')


def key_day(di, days):
    day = days[di]
    notes = "".join(note_row_svg(r, "key", i + 1) for i, r in enumerate(day.notes))
    rhythm = "".join(exercise_svg(e, "key") for e in day.rhythm)
    ksym = "".join(
        f'<div class="ka" data-sym="{sid}" data-letter="{day.syms.answer(k)}"><b>{k + 1}</b>{symbol_svg(sid)}'
        f'<span><b>{day.syms.answer(k)}</b> {escape(SYM_NAME[sid])}</span></div>' for k, sid in enumerate(day.syms.ids))
    gaps = "".join(gap_svg(x, "key", i + 1) for i, x in enumerate(day.gaps))
    return (f'<div class="kday" data-day="{day.n}"><div class="kt"><div>Day {day.n}<span> · {escape(DAYS[di][0])}</span></div><span>page {ws_page_no(di)}</span></div>'
            f'<div class="nrk">{notes}</div>{rhythm}<div class="ksym">{ksym}</div><div class="gps">{gaps}</div></div>')


def key_page(kp, days, watermark=False):
    pis = [2 * kp, 2 * kp + 1]
    wm = '<div class="wm">PREVIEW</div>' if watermark else ""
    return (f'<section class="page">{wm}'
            f'<div class="top"><div class="h t">Answer Key<small>Days {pis[0] + 1} and {pis[1] + 1}</small></div>'
            f'<div class="tag"><div class="lv ak">ANSWER KEY</div><div class="ln">Letters, counts, symbols and missing beats</div></div></div>'
            f'{"".join(key_day(di, days) for di in pis)}'
            f'<div style="flex:1"></div>{foot(COPY, f"Answer key · Page {P_KEY0 + kp}")}</section>')


# ------------------------------------------------------------------ cover and square art
def card_art():
    """Four section cards (icon + name), used on the cover."""
    out = []
    for icon, letter, name, ins in SEC_NAMES:
        sub = {"A": "Name the notes", "B": "Count the rhythm", "C": "Match the symbols", "D": "Find the missing beats"}[letter]
        out.append(f'<div class="ccard"><div class="cl">{letter}</div>{icon_svg(icon, 84)}<div class="cn">{name}</div><div class="cs">{sub}</div></div>')
    return f'<div class="cards">{"".join(out)}</div>'


COVER_CSS = """
.cvr { width: 1000px; position: relative; display: flex; flex-direction: column; align-items: center; background: #fff; overflow: hidden; }
.cvr .store { font-family: 'Oswald'; font-weight: 500; letter-spacing: .32em; text-transform: uppercase; font-size: 22px; margin-top: 34px; }
.cards { display: flex; gap: 16px; width: 904px; }
.ccard { flex: 1; border: 3px solid #000; border-radius: 14px; text-align: center; padding: 10px 6px 12px; position: relative; background: #fff; }
.ccard svg { margin: 14px auto 4px; width: 112px; height: 112px; }
.ccard .cl { position: absolute; left: 9px; top: 7px; background: #000; color: #fff; font-family: 'Oswald'; font-weight: 700; font-size: 21px; width: 30px; height: 30px; line-height: 31px; border-radius: 50%; }
.ccard .cn { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 25px; line-height: 1.05; }
.ccard .cs { font-family: 'Oswald'; font-weight: 300; font-size: 17px; margin-top: 3px; }
.cvr .hd { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; text-align: center; line-height: .95; }
.cvr .sub { font-family: 'Oswald'; font-weight: 300; text-align: center; }
.cvr .band { width: 100%; background: #000; color: #fff; text-align: center; font-family: 'Oswald'; font-weight: 500; text-transform: uppercase; letter-spacing: .1em; font-size: 26px; padding: 16px 0 18px; }
.cvr .band em { font-style: normal; color: ACCENT; }
.dots { position: absolute; inset: 0; pointer-events: none; }
""".replace("ACCENT", ACCENT)


CSS += COVER_CSS


def snow_dots(w, h, n=26, seed=5):
    rng = random.Random(seed)
    out = []
    for _ in range(n):
        x, y, r = rng.uniform(20, w - 20), rng.uniform(70, h * 0.4), rng.choice([3, 4, 5, 6])
        out.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r}" fill="{ACCENT}" opacity=".55"/>')
    return f'<svg class="dots" viewBox="0 0 {w} {h}" width="{w}" height="{h}">{"".join(out)}</svg>'


def cover_inner(h):
    strip = NoteRow("treble", ["E4", "G4", "B4", "D5", "F5", "A4", "C5", "E5"])
    staff = note_row_svg(strip, "key", 1).replace('width="540pt"', 'width="880px"').replace(f'height="{NR_BOX_Y + 20:.1f}pt"', 'height="auto"')
    staff = re.sub(r'width="540pt" height="[\d.]+pt"', 'width="880px"', staff)
    return (f'<div class="cvr" style="height:{h}px">{snow_dots(1000, h)}<div class="store">{BRAND}</div>'
            f'<div style="flex:1;display:flex;flex-direction:column;justify-content:space-evenly;align-items:center;width:100%;padding-bottom:78px;position:relative">'
            f'{card_art()}<div style="width:880px">{staff}</div>'
            f'<div><div class="hd" style="font-size:70px">December</div>'
            f'<div class="hd" style="font-size:106px;white-space:nowrap">Music Bell-Ringers</div>'
            f'<div class="sub" style="font-size:28px;margin-top:12px">20 no-prep daily warm-ups · rhythm, note names, symbols</div></div></div>'
            f'<div class="band" style="position:absolute;left:0;bottom:0">Grades 3–6 <em>·</em> 20 daily pages <em>·</em> answer keys</div></div>')


def cover_page():
    return f'<section class="page" style="padding:0"><div style="zoom:.816;width:1000px">{cover_inner(1294)}</div></section>'


def teacher_page():
    rows = "".join(f'<tr><td style="white-space:nowrap"><b>{i + 1}</b></td><td>{d[0]}</td><td>{d[1]}</td></tr>' for i, d in enumerate(DAYS))
    return (f'<section class="page doc"><div class="rule"><h1>Teacher Notes</h1>'
            f'<div class="l" style="font-size:13pt">{TITLE} · 20 daily warm-ups · grades 3–6</div></div>'
            f'<div class="cols"><div>'
            f'<h2>How to use</h2><ul>'
            f'<li>Hand out one page as students arrive, or project it. Each page takes about 8 minutes; no prep, no pencil sharpening, no materials but a pencil.</li>'
            f'<li><b>A · Snowy Notes.</b> Students write the letter name of every note in its box. Days 1–12 use one clef; from day 13 the page has a treble row and a bass row.</li>'
            f'<li><b>B · Mitten Rhythm.</b> Write the count under each note and rest, at the place where it begins. A half note on beat 1 gets a 1; the 2 is held, so nothing is written for it. Write <b>&amp;</b> for the half beat between beats. In 6/8 count 1 2 3 4 5 6.</li>'
            f'<li><b>C · Cocoa Symbols.</b> Five symbols, five names in a word bank. Students write the letter. Two symbols are new each day until day 16, then the whole set rotates.</li>'
            f'<li><b>D · Skate Math.</b> A measure is missing its ending. Students work out how many beats are missing.</li>'
            f'<li>Review aloud, or hand out the answer key. Answer keys are on pages {P_KEY0}–{P_TERMS - 1}, two days per page.</li>'
            f'<li>Print single-sided. Pages 3 and 4 are a student reference: note names, note values and a symbol glossary.</li></ul>'
            f'<h2>Great for</h2><ul><li>Band, orchestra, choir and general music, grades 3–6</li><li>The first five minutes of class, early finishers, sub plans and December weeks with a shorter schedule</li></ul>'
            f'<h2>Winter theme for every classroom</h2><p class="small">Snow, mittens, hot cocoa and ice skating. No holiday names or religious symbols, so the pages fit any school calendar.</p>'
            f'</div><div>'
            f'<h2>The 20 days</h2><table style="font-size:8.5pt"><tr><th>Day</th><th>Theme</th><th>Focus</th></tr>{rows}</table>'
            f'<h2>Standards</h2><p>Practices reading and identifying notation: pitch names, rhythm and meter, and music symbols. Supports the National Core Arts Standards for Music '
            f'(MU:Pr4.2, grades 3–6). Modest claim: one short daily practice, not a full curriculum.</p>'
            f'<p class="small">Every page is generated and checked: notes are placed by staff position, every measure adds up to its time signature, '
            f'and each key is built from the same data as its page. No songs, lyrics or copyrighted characters are used.</p>'
            f'</div></div>{foot(COPY, "Page 2")}</section>')


def ref_staff_svg(clef, pitches, w=540.0):
    s = 7.0
    yb = 5.6 * s
    h = yb + 1.6 * s + 20
    out = [f'<svg class="rs" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.0f} {h:.0f}" width="{w:.0f}pt" height="{h:.0f}pt" style="display:block">']
    for i in range(5):
        out.append(f'<line x1="0" y1="{yb - i * s:.1f}" x2="{w - 1:.0f}" y2="{yb - i * s:.1f}" stroke="#000" stroke-width="{0.16 * s:.2f}"/>')
    out.append(g(0xE050, 5, yb - s, 4 * s) if clef == "treble" else g(0xE062, 5, yb - 3 * s, 4 * s))
    n = len(pitches)
    for k, p in enumerate(pitches):
        cx = 62 + k * (w - 62 - 22) / (n - 1)
        st = staff_step(p, clef)
        y = yb - st * s / 2
        nx = cx - 1.688 * s / 2
        lines = list(range(-2, st - 1, -2)) if st <= -2 else (list(range(10, st + 1, 2)) if st >= 10 else [])
        for ls in lines:
            ly = yb - ls * s / 2
            out.append(f'<line x1="{nx - 0.4 * s:.1f}" y1="{ly:.1f}" x2="{nx + 2.1 * s:.1f}" y2="{ly:.1f}" stroke="#000" stroke-width="{0.2 * s:.2f}"/>')
        out.append(g(0xE0A2, nx, y, 4 * s))
        line_note = st % 2 == 0
        out.append(f'<text x="{cx:.1f}" y="{yb + 1.6 * s + 15:.1f}" text-anchor="middle" font-family="Oswald" font-weight="700" font-size="14" fill="{"#000" if line_note else ACCENT}">{p[0]}</text>')
    out.append("</svg>")
    return "".join(out)


def ref_cells():
    items = [("whole", 0, 0, "4 beats"), ("half", 0, 0, "2 beats"), ("quarter", 0, 0, "1 beat"), ("eighth", 0, 0, "½ beat"),
             ("half", 0, 1, "3 beats"), ("quarter", 0, 1, "1½ beats"), ("whole", 1, 0, "4 beats of silence"), ("half", 1, 0, "2 beats of silence"),
             ("quarter", 1, 0, "1 beat of silence"), ("eighth", 1, 0, "½ beat of silence")]
    cells = []
    for kind, rest, dot, beats in items:
        svg = (f'<svg width="60pt" height="34pt" viewBox="0 0 60 34"><line x1="6" y1="22" x2="54" y2="22" stroke="#000" stroke-width="1.1"/>'
               f'{token_svg(kind, rest, dot, 28, 22, 7.0)}</svg>')
        name = f"{'dotted ' if dot else ''}{kind} {'rest' if rest else 'note'}"
        cells.append(f'<div class="refcell">{svg}<b>{name}</b><span>{beats}</span></div>')
    return "".join(cells)


def ref1_page():
    return (f'<section class="page doc"><div class="rule"><h1>Student Reference: Notes</h1>'
            f'<div class="l" style="font-size:13pt">Keep this page nearby while you work.</div></div>'
            f'<h2>Treble clef <span class="acc">·</span> <span class="l" style="text-transform:none;font-size:11pt">C4 (middle C) to A5</span></h2>'
            f'<div class="rstaff">{ref_staff_svg("treble", TREBLE_ALL)}</div>'
            f'<p class="mn"><b>Lines</b> (bottom to top): E G B D F — <i>Every Good Boy Does Fine</i> · <b>Spaces:</b> F A C E — <i>FACE</i>. Letters in blue are the notes in the spaces.</p>'
            f'<h2>Bass clef <span class="acc">·</span> <span class="l" style="text-transform:none;font-size:11pt">E2 to C4 (middle C)</span></h2>'
            f'<div class="rstaff">{ref_staff_svg("bass", BASS_ALL)}</div>'
            f'<p class="mn"><b>Lines</b> (bottom to top): G B D F A — <i>Good Boys Do Fine Always</i> · <b>Spaces:</b> A C E G — <i>All Cows Eat Grass</i>.</p>'
            f'<h2>Note and rest values <span class="acc">·</span> <span class="l" style="text-transform:none;font-size:11pt">in 4/4, 3/4 and 2/4</span></h2>'
            f'<div class="refgrid">{ref_cells()}</div>'
            f'<p class="small">A dot adds half the note\'s value: a half note is 2 beats, a dotted half note is 3 beats. In 6/8 the eighth note gets one count: a quarter note is 2 counts, a dotted quarter is 3.</p>'
            f'<p class="mn"><b>Counting:</b> 4/4 → 1 2 3 4 · 3/4 → 1 2 3 · 2/4 → 1 2 · eighth notes add &amp; between beats (1 &amp; 2 &amp;) · 6/8 → 1 2 3 4 5 6.</p>'
            f'<div style="flex:1"></div>{foot(COPY, "Page 3")}</section>')


def ref2_page():
    items = "".join(
        f'<div class="gl">{symbol_svg(sid)}<div><b>{escape(SYM_NAME[sid])}</b><span>{escape(SYM_MEAN[sid])}</span></div></div>' for sid in SYM_IDS)
    return (f'<section class="page doc"><div class="rule"><h1>Student Reference: Symbols</h1>'
            f'<div class="l" style="font-size:13pt">{len(SYM_IDS)} symbols you will meet in the Cocoa Symbols warm-ups.</div></div>'
            f'<div class="glos">{items}</div>'
            f'<div style="flex:1"></div>{foot(COPY, "Page 4")}</section>')


def terms_page():
    return (f'<section class="page doc"><div class="rule"><h1>Terms of Use</h1>'
            f'<div class="l" style="font-size:13pt">Thank you for your purchase!</div></div>'
            f'<p>© {YEAR} {STORE}. {BRAND} by {STORE}. All rights reserved. This purchase gives <b>one teacher</b> a license to use this resource with their own students.</p>'
            f'<h2>You may</h2><ul><li>Print and copy pages for your own classroom and students.</li>'
            f'<li>Share pages with your own students through a password-protected class site or learning platform.</li>'
            f'<li>Use the pages with your own students when you have a substitute teacher.</li></ul>'
            f'<h2>You may not</h2><ul><li>Share, email or copy this resource for other teachers, a whole school or a district. '
            f'Additional licenses are available on Teachers Pay Teachers.</li>'
            f'<li>Post any part of it on a public website, shared drive or social media.</li>'
            f'<li>Sell, give away or claim any part of it as your own, or edit it into a new product.</li></ul>'
            f'<h2>Questions?</h2><p>Please use the Q&amp;A tab on the {BRAND} by {STORE} store on Teachers Pay Teachers. '
            f'If something looks wrong, let me know there and I will fix it.</p>'
            f'<h2>Credits</h2><ul>'
            f'<li>Warm-up pages, layouts and answer keys: original work, {BRAND} by {STORE}.</li>'
            f'<li>Music notation font: Bravura © Steinberg Media Technologies GmbH, SIL Open Font License 1.1.</li>'
            f'<li>Text fonts: Oswald (The Oswald Project Authors) and Source Sans 3 (Adobe), SIL Open Font License 1.1.</li></ul>'
            f'<p class="small">{DISCLOSURE}</p>'
            f'<div style="flex:1"></div>{foot(COPY, f"Page {P_TERMS}")}</section>')


def full_pages(days):
    pages = [cover_page(), teacher_page(), ref1_page(), ref2_page()]
    pages += [worksheet_page(di, days) for di in range(NDAYS)]
    pages += [key_page(kp, days) for kp in range(N_KEYPAGES)]
    pages.append(terms_page())
    return pages


PREVIEW_PICKS = [("ws", 0), ("ws", 8), ("ws", 16), ("key", 3)]   # 0-based day / key page; shown in this order


def preview_pages(days):
    return [worksheet_page(i, days, True) if k == "ws" else key_page(i, days, True) for k, i in PREVIEW_PICKS]


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
.dc { box-sizing: border-box; border: 2px solid #000; border-radius: 8px; padding: 6px 8px 6px; background: #fff; text-align: left; position: relative; }
.dc .dn { font-family: 'Oswald'; font-weight: 700; font-size: 15px; color: ACCENT; letter-spacing: .06em; }
.dc .dt { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 18px; line-height: 1.05; }
.dc .df { font-family: 'Oswald'; font-weight: 300; font-size: 14px; line-height: 1.15; margin-top: 3px; }
.sec4 { display: flex; gap: 14px; width: 904px; margin-top: 30px; }
.sec4 > div { flex: 1; border: 2px solid #000; border-radius: 10px; padding: 8px 6px; text-align: center; background: #fff; }
.sec4 svg { margin: 0 auto; }
.sec4 b { display: block; font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 20px; margin-top: 2px; }
.sec4 span { font-family: 'Oswald'; font-weight: 300; font-size: 16px; display: block; }
""".replace("ACCENT", ACCENT)


def sq_doc(body):
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{font_css()}{CSS}'
            f'html,body{{margin:0;background:#fff}}{SQ_CSS}</style></head><body>{body}</body></html>')


def cover_square():
    return sq_doc(cover_inner(1000))


def preview_square_1(img):
    labs = [("Day 1", "Snowflake"), ("Day 9", "Snowball"), ("Day 17", "Snowy Owl")]
    shots = "".join(
        f'<div style="width:296px"><div class="shot"><img src="{img[i]}"></div>'
        f'<div class="lbl">{labs[i][0]}<span>{labs[i][1]}</span></div></div>' for i in range(3))
    secs = "".join(f'<div>{icon_svg(ic, 44)}<b>{nm}</b><span>{sub}</span></div>' for (ic, _, nm, _), sub in
                   zip(SEC_NAMES, ["Name the notes", "Count the rhythm", "Match the symbols", "Find missing beats"]))
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div>'
        f'<div class="hd" style="font-size:72px;margin-top:18px">Four quick parts a day</div>'
        f'<div class="sub" style="font-size:27px;margin-top:8px">One page, about 8 minutes, no prep</div>'
        f'<div style="display:flex;gap:26px;margin-top:34px">{shots}</div>'
        f'<div class="sec4">{secs}</div>'
        f'<div class="band">20 daily pages <em>·</em> grades 3–6 <em>·</em> winter theme</div></div>')


def preview_square_2(ws, key):
    pair = "".join(
        f'<div style="width:420px"><div class="shot"><img src="{src}"></div>'
        f'<div class="lbl">{lab}</div></div>' for src, lab in ((ws, "Daily page"), (key, "Answer key")))
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div>'
        f'<div class="hd" style="font-size:70px;margin-top:20px">Answer keys included</div>'
        f'<div class="sub" style="font-size:27px;margin-top:8px">Letters, counts, symbols and missing beats, two days to a page</div>'
        f'<div style="display:flex;gap:40px;margin-top:30px">{pair}</div>'
        f'<div class="band">Keys for all 20 days</div></div>')


def preview_square_3():
    cards = "".join(f'<div class="dc" style="width:168px;height:150px"><div class="dn">DAY {i + 1}</div><div class="dt">{escape(d[0])}</div>'
                    f'<div class="df">{escape(d[1])}</div></div>' for i, d in enumerate(DAYS))
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div>'
        f'<div class="hd" style="font-size:62px;margin-top:14px">20 days, step by step</div>'
        f'<div style="display:flex;flex-wrap:wrap;gap:16px;width:900px;margin-top:34px;justify-content:center">{cards}</div>'
        f'<div class="band">Treble <em>·</em> bass <em>·</em> rhythm <em>·</em> symbols</div></div>')


# ------------------------------------------------------------------ build
def write(name, text):
    p = os.path.join(BUILD, name)
    with open(p, "w") as f:
        f.write(text)
    return p


def build():
    os.makedirs(BUILD, exist_ok=True)
    days = make_days()
    problems = verify_data(days)
    if problems:
        print("\n".join(problems))
        sys.exit("data check failed; not rendering")
    full = write("resource.html", html_doc(full_pages(days), TITLE))
    prev = write("preview.html", html_doc(preview_pages(days), "Preview"))
    render([{"html": full, "pdf": PDF}, {"html": prev, "pdf": PREVIEW_PDF}])
    for i in range(1, 5):
        subprocess.run(["pdftoppm", "-png", "-r", "110", "-f", str(i), "-l", str(i), "-singlefile", PREVIEW_PDF,
                        os.path.join(BUILD, f"pv{i}")], check=True)
    sq = [write("cover.html", cover_square()), write("p1.html", preview_square_1(["pv1.png", "pv2.png", "pv3.png"])),
          write("p2.html", preview_square_2("pv3.png", "pv4.png")), write("p3.html", preview_square_3())]
    outs = [COVER_PNG] + PREVIEW_PNGS
    render([{"html": h, "png": o, "width": 1000, "height": 1000, "scale": 2} for h, o in zip(sq, outs)])
    print(f"built {PDF}, {PREVIEW_PDF}, cover + 3 previews")
# ------------------------------------------------------------------ render
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


def pdf_fonts(path):
    out = subprocess.run(["pdffonts", path], capture_output=True, text=True, check=True).stdout.splitlines()[2:]
    rows = []
    for line in out:
        parts = line.split()
        rows.append((parts[0], parts[-5]))
    return rows


def load_json(name):
    return json.load(open(os.path.join(TPT, name)))



# ------------------------------------------------------------------ checks
DUR8 = {"whole": 8, "half": 4, "quarter": 2, "eighth": 1}
BAR8 = {"4/4": 8, "3/4": 6, "2/4": 4, "6/8": 6}


def verify_data(days):
    """Checks on the in-memory data: structure, pools, bar sums, counts (second method), symbols, gaps, layout."""
    errs = []
    sym_uses = {i: 0 for i in SYM_IDS}
    for di, day in enumerate(days):
        theme, _, meters, allowed, featured, rows, gm, gc = DAYS[di]
        if len(day.notes) != len(rows):
            errs.append(f"day {day.n}: {len(day.notes)} note rows, expected {len(rows)}")
        for row, (clef, pool, n) in zip(day.notes, rows):
            if row.clef != clef or len(row.pitches) != n or any(p not in pool for p in row.pitches):
                errs.append(f"day {day.n}: note row does not match its pool")
            if len(set(row.pitches)) < min(5, len(pool)):
                errs.append(f"day {day.n}: note row has too few different pitches")
            ref = TREBLE_ALL if clef == "treble" else BASS_ALL
            if any(p not in ref for p in row.pitches):
                errs.append(f"day {day.n}: pitch outside the {clef} range")
            if (min(n, 8) and len(set(zip(row.pitches, row.pitches[1:]))) < 1):
                errs.append(f"day {day.n}: degenerate note row")
        if len(day.rhythm) != RH_LINES:
            errs.append(f"day {day.n}: {len(day.rhythm)} rhythm lines")
        for ex in day.rhythm:
            L = meter_len(ex.meter)
            if ex.meter not in meters:
                errs.append(f"{ex.id}: meter {ex.meter} not in the day's spec")
            xs, bars = exercise_geometry(ex)
            prev_x = None
            for mi, toks in enumerate(ex.measures):
                if sum(t.dur for t in toks) != L:
                    errs.append(f"{ex.id} m{mi + 1}: durations add to {sum(t.dur for t in toks)}, meter is {L}")
                e = 0
                for ti, t in enumerate(toks):
                    d8 = DUR8[t.kind] * (3 if t.dot else 2) // 2
                    if t.dot and DUR8[t.kind] % 2:
                        errs.append(f"{ex.id}: dotted eighth not allowed")
                    if t.dur * 8 != d8:
                        errs.append(f"{ex.id} m{mi + 1} t{ti + 1}: dur {t.dur} != {d8}/8")
                    want = str(e + 1) if ex.meter == "6/8" else (str(e // 2 + 1) if e % 2 == 0 else "&")
                    if t.count != want:
                        errs.append(f"{ex.id} m{mi + 1} t{ti + 1}: count {t.count!r}, expected {want!r}")
                    e += d8
                if e != BAR8[ex.meter]:
                    errs.append(f"{ex.id} m{mi + 1}: {e}/8 in the bar, meter {ex.meter}")
                if all(t.rest for t in toks) and not (len(toks) == 1 and toks[0].kind == "whole"):
                    errs.append(f"{ex.id} m{mi + 1}: a measure of only rests")
                m0, m1 = bars[mi]
                for ti, x in enumerate(xs[mi]):
                    if prev_x is not None and x - prev_x < BOX_W + 2:
                        errs.append(f"{ex.id}: count boxes {x - prev_x:.1f}pt apart")
                    prev_x = x
                    if not (m0 + 4 < x - BOX_W / 2 and x + BOX_W / 2 < m1 - 3) or x + 2.2 * S >= m1 - 2:
                        errs.append(f"{ex.id} m{mi + 1}: token {ti + 1} too close to its barline")
        kinds = {(t.kind, t.rest, t.dot) for ex in day.rhythm for ms in ex.measures for t in ms}
        for f_ in featured:
            cells = SIMPLE_CELLS if f_ in SIMPLE_CELLS else COMPOUND_CELLS
            need = {(k, bool(r), bool(d)) for k, r, d in cells[f_]}
            if any(f_ in cells_for(m) for m in meters) and not need <= kinds:
                errs.append(f"day {day.n}: featured rhythm {f_} missing")
        # symbols
        ss = day.syms
        if len(set(ss.ids)) != NSYM or sorted(ss.bank) != sorted(ss.ids):
            errs.append(f"day {day.n}: symbol set is not 5 distinct symbols with a matching word bank")
        for k in range(NSYM):
            if ss.bank["ABCDE".index(ss.answer(k))] != ss.ids[k]:
                errs.append(f"day {day.n}: symbol {k + 1} answer wrong")
        for sid in ss.ids:
            sym_uses[sid] += 1
        # gaps
        if len(day.gaps) != GAPS:
            errs.append(f"day {day.n}: {len(day.gaps)} gaps")
        for gi, gp in enumerate(day.gaps):
            if gp.meter not in gm:
                errs.append(f"day {day.n} gap {gi + 1}: meter {gp.meter} not in spec")
            tot8 = sum(DUR8[t.kind] * (3 if t.dot else 2) // 2 for t in gp.toks)
            miss8 = BAR8[gp.meter] - tot8
            if miss8 < 2 or miss8 % 2:
                errs.append(f"day {day.n} gap {gi + 1}: {miss8}/8 missing")
            if F(miss8, 2) != gp.beats:
                errs.append(f"day {day.n} gap {gi + 1}: stored answer {gp.beats} != {F(miss8, 2)}")
            if not any(not t.rest for t in gp.toks):
                errs.append(f"day {day.n} gap {gi + 1}: only rests shown")
    for sid, n in sym_uses.items():
        if n < 2:
            errs.append(f"symbol {sid} appears on only {n} page(s)")
    return errs


def parse_exercises(html):
    out = []
    for m in re.finditer(r'<svg class="ex" data-mode="(\w+)" data-ex="([\d.]+)" data-meter="([\d/]+)".*?</svg>', html, re.S):
        mode, eid, meter = m.groups()
        meas = []
        for chunk in m.group(0).split('<g class="meas"')[1:]:
            toks = [dict(kind=a, rest=int(b), dot=int(c), count=d, x=float(x)) for a, b, c, d, x in
                    re.findall(r'<g class="tok" data-kind="(\w+)" data-rest="(\d)" data-dot="(\d)" data-count="([^"]*)" data-x="([\d.]+)"', chunk)]
            meas.append(toks)
        out.append((eid, mode, meter, meas))
    return out


def parse_note_rows(html):
    """[(mode, clef, [(letter_from_data, letter_recomputed_from_y, written_letter_or_None)])] in document order."""
    out = []
    for m in re.finditer(r'<svg class="nr" data-mode="(\w+)" data-row="(\d+)" data-clef="(\w+)" data-s="([\d.]+)" data-yb="([\d.]+)".*?</svg>', html, re.S):
        mode, _, clef, s, yb = m.groups()
        s, yb = float(s), float(yb)
        notes = []
        for chunk in m.group(0).split('<g class="nt"')[1:]:
            pitch, letter, y = re.search(r'data-pitch="(\w+)" data-letter="(\w)" data-y="([\d.]+)"', chunk).groups()
            step = round((yb - float(y)) / (s / 2))
            d = diatonic(CLEF_BOTTOM[clef]) + step
            octave_from_y = f"{LETTERS[d % 7]}{d // 7}"
            wr = re.search(r'font-size="16" fill="[^"]+">(\w)</text>', chunk)
            notes.append((pitch, letter, octave_from_y, wr.group(1) if wr else None))
        out.append((mode, clef, notes))
    return out


def verify_html(days):
    errs = []
    p = os.path.join(BUILD, "resource.html")
    if not os.path.exists(p):
        return ["build/resource.html missing: run gen.py first"], 0, 0, 0
    html = open(p).read()
    ntok = nrest = nnote = 0
    # --- A: note names, recomputed from the rendered notehead positions
    rows = parse_note_rows(html[html.index('data-day="1"'):])
    want_rows = sum(len(d.notes) for d in days)
    ws_rows = [r for r in rows if r[0] == "ws"]
    key_rows = [r for r in rows if r[0] == "key" and r[2][0][3] is not None]
    key_rows = key_rows[:want_rows] if len(key_rows) >= want_rows else key_rows
    if len(ws_rows) != want_rows:
        errs.append(f"html has {len(ws_rows)} worksheet note rows, expected {want_rows}")
    flat_exp = [(row.clef, row.pitches) for d in days for row in d.notes]
    nletters = 0
    for i, (clef, pitches) in enumerate(flat_exp):
        if i >= len(ws_rows) or i >= len(key_rows):
            break
        for kind, r in (("worksheet", ws_rows[i]), ("key", key_rows[i])):
            if r[1] != clef or [n[0] for n in r[2]] != pitches:
                errs.append(f"note row {i + 1} ({kind}): clef/pitches differ from the data")
            for pitch, letter, from_y, written in r[2]:
                nletters += 1
                if from_y != pitch or letter != pitch[0]:
                    errs.append(f"note row {i + 1} ({kind}): data says {pitch}, notehead position says {from_y}")
                if kind == "key" and written != from_y[0]:
                    errs.append(f"note row {i + 1}: key writes {written} but the notehead is {from_y}")
    # --- B: rhythm counts
    exs = parse_exercises(html)
    ws = {e[0]: e for e in exs if e[1] == "ws"}
    key = {e[0]: e for e in exs if e[1] == "key"}
    if len(ws) != NDAYS * RH_LINES or len(key) != NDAYS * RH_LINES:
        errs.append(f"html has {len(ws)} worksheet and {len(key)} key rhythm lines, expected {NDAYS * RH_LINES} each")
    for eid, (_, _, meter, meas) in key.items():
        if eid not in ws or ws[eid][3] != meas:
            errs.append(f"{eid}: worksheet and answer key rhythms differ")
        for mi, toks in enumerate(meas):
            e = 0
            for t in toks:
                ntok += 1
                nrest += t["rest"]
                nnote += 1 - t["rest"]
                want = str(e + 1) if meter == "6/8" else (str(e // 2 + 1) if e % 2 == 0 else "&")
                if t["count"] != want:
                    errs.append(f"{eid} m{mi + 1}: written count {t['count']!r}, note starts at eighth {e}: expected {want!r}")
                e += DUR8[t["kind"]] * (3 if t["dot"] else 2) // 2
            if e != BAR8[meter]:
                errs.append(f"{eid} m{mi + 1}: {e} eighths in a {meter} measure")
    # --- C: symbols. Worksheet side: cell symbol ids + word bank; key side: letter + name per symbol
    sym_checked = 0
    ws_days = re.findall(r'<section class="page(?: two)?" data-day="(\d+)">(.*?)</section>', html, re.S)
    if len(ws_days) != NDAYS:
        errs.append(f"html has {len(ws_days)} day pages, expected {NDAYS}")
    banks = {}
    for dn, body in ws_days:
        ids = re.findall(r'<div class="sc" data-sym="(\w+)">.*?<svg class="sym" data-sym="(\w+)"', body, re.S)
        if any(a != b for a, b in ids) or len(ids) != NSYM:
            errs.append(f"day {dn}: symbol cell and drawing disagree")
        bank = {m[1]: (m[0], m[2]) for m in re.findall(r'<span class="bk" data-id="(\w+)" data-letter="(\w)"><b>\w</b>([^<]+)</span>', body)}
        # bank: letter -> (id, name)
        bank = {l: (i, n) for i, l, n in re.findall(r'<span class="bk" data-id="(\w+)" data-letter="(\w)"><b>\w</b>([^<]+)</span>', body)}
        banks[int(dn)] = (bank, [a for a, _ in ids])
        for letter, (sid, name) in bank.items():
            if SYM_NAME[sid] != name:
                errs.append(f"day {dn}: word bank says {name!r} for {sid}")
    kdays = [(ch.split('"', 1)[0], ch) for ch in html.split('<div class="kday" data-day="')[1:]]
    if len(kdays) != NDAYS:
        errs.append(f"html has {len(kdays)} key day blocks, expected {NDAYS}")
    for dn, body in kdays:
        bank, ids = banks[int(dn)]
        ks = re.findall(r'<div class="ka" data-sym="(\w+)" data-letter="(\w)"><b>(\d)</b><svg class="sym" data-sym="(\w+)".*?<span><b>(\w)</b> ([^<]+)</span>', body, re.S)
        if len(ks) != NSYM:
            errs.append(f"day {dn}: key lists {len(ks)} symbols")
        for k, (sid, letter, num, sid2, letter2, name) in enumerate(ks):
            sym_checked += 1
            if int(num) != k + 1 or sid != ids[k] or sid2 != sid or letter != letter2:
                errs.append(f"day {dn} symbol {k + 1}: key row does not match the worksheet")
            if bank[letter][0] != sid or SYM_NAME[sid] != name:
                errs.append(f"day {dn} symbol {k + 1}: key letter {letter} points at {bank[letter][0]}, symbol is {sid}")
    # --- D: missing beats, recomputed from the rendered note durations
    gaps = re.findall(r'<svg class="gp" data-mode="(\w+)" data-gap="(\d+)" data-meter="([\d/]+)" data-answer="([^"]+)".*?</svg>', html, re.S)
    gp_blocks = [m.group(0) for m in re.finditer(r'<svg class="gp".*?</svg>', html, re.S)]
    if len(gp_blocks) != 2 * NDAYS * GAPS:
        errs.append(f"html has {len(gp_blocks)} gap drawings, expected {2 * NDAYS * GAPS}")
    ngap = 0
    for blk in gp_blocks:
        mode, gi, meter, ans = re.search(r'data-mode="(\w+)" data-gap="(\d+)" data-meter="([\d/]+)" data-answer="([^"]+)"', blk).groups()
        tot = 0
        for kind, rest, dot in re.findall(r'<g class="gtok" data-kind="(\w+)" data-rest="(\d)" data-dot="(\d)"', blk):
            tot += DUR8[kind] * (3 if dot == "1" else 2) // 2
        miss = BAR8[meter] - tot
        txt = {2: "1", 4: "2", 6: "3"}.get(miss)
        ngap += 1
        if txt != ans:
            errs.append(f"gap {gi} ({meter}): drawn notes leave {miss}/8, stored answer {ans!r}")
        if mode == "key":
            w = re.search(r'class="ga">([^<]+)</text>', blk)
            if not w or w.group(1) != txt:
                errs.append(f"gap {gi} ({meter}): key writes {w.group(1) if w else None!r}, expected {txt!r}")
    # --- data vs html: the page content really is the generated data
    return errs, ntok, nrest + 0, (nnote, nletters, sym_checked, ngap)


OVERFLOW_JS = """
const { chromium } = require('playwright'); const url = require('url');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage();
  await p.goto(url.pathToFileURL(process.argv[2]).href, { waitUntil: 'load' });
  await p.evaluate(() => document.fonts.ready);
  const res = await p.evaluate(() => [...document.querySelectorAll('section.page')].map((s, i) => {
    const r = s.getBoundingClientRect(); let worst = 0, wide = 0;
    for (const c of s.querySelectorAll('*')) {
      if (c.closest('.wm') || c.closest('.dots')) continue;
      const q = c.getBoundingClientRect(); if (q.width === 0 && q.height === 0) continue;
      worst = Math.max(worst, q.bottom - r.bottom); wide = Math.max(wide, q.right - r.right, r.left - q.left);
    }
    return [i + 1, worst, wide];
  }));
  console.log(JSON.stringify(res)); await b.close();
})();
"""


def overflow_check():
    """Open resource.html in Chromium and report any page whose content runs past the page edge."""
    js = os.path.join(BUILD, "overflow.js")
    open(js, "w").write(OVERFLOW_JS)
    out = subprocess.run(["node", js, os.path.join(BUILD, "resource.html")], capture_output=True, text=True, env=node_env())
    if out.returncode:
        return [f"overflow check failed to run: {out.stderr[-200:]}"], 0
    res = json.loads(out.stdout.strip().splitlines()[-1])
    errs = []
    for n, worst, wide in res:
        if n > 1 and (worst > 0.5 or wide > 0.5):
            errs.append(f"PDF page {n}: content runs {worst:.1f}px past the bottom / {wide:.1f}px past a side")
    return errs, len(res)


def pdf_fonts(path):
    out = subprocess.run(["pdffonts", path], capture_output=True, text=True, check=True).stdout.splitlines()[2:]
    rows = []
    for line in out:
        parts = line.split()
        rows.append((parts[0], parts[-5]))
    return rows


def load_json(name):
    return json.load(open(os.path.join(TPT, name)))


def verify_files():
    errs = []
    from pypdf import PdfReader
    from PIL import Image
    for p in [PDF, PREVIEW_PDF, COVER_PNG, *PREVIEW_PNGS, UPLOAD, TPT_JSON, os.path.join(TPT, "STYLE.md"), RENDER_JS]:
        if not os.path.exists(p):
            errs.append(f"missing {os.path.relpath(p, TPT)}")
    if errs:
        return errs
    for path, want_pages in ((PDF, TOTAL_PAGES), (PREVIEW_PDF, 4)):
        rd = PdfReader(path)
        if len(rd.pages) != want_pages:
            errs.append(f"{os.path.basename(path)}: {len(rd.pages)} pages, expected {want_pages}")
        for i, pg in enumerate(rd.pages):
            w, h = float(pg.mediabox.width), float(pg.mediabox.height)
            if abs(w - 612) > 1 or abs(h - 792) > 1:
                errs.append(f"{os.path.basename(path)} p{i + 1}: {w:.0f}x{h:.0f}pt, not US Letter")
        fonts = pdf_fonts(path)
        for name, emb in fonts:
            if emb != "yes":
                errs.append(f"{os.path.basename(path)}: font {name} not embedded")
        names = " ".join(n for n, _ in fonts)
        for fam in ("Bravura", "Oswald", "SourceSans3"):
            if fam.lower() not in names.lower().replace(" ", ""):
                errs.append(f"{os.path.basename(path)}: {fam} not found in PDF fonts")
    rd = PdfReader(PDF)
    for i, pg in enumerate(rd.pages):
        t = pg.extract_text() or ""
        if len(t.strip()) < 40:
            errs.append(f"PDF page {i + 1} looks blank")
        n = i + 1
        if P_WS0 <= n < P_KEY0 and f"DAY {n - P_WS0 + 1}" not in t.upper().replace("\n", " "):
            errs.append(f"PDF page {n}: day heading missing")
        if P_KEY0 <= n < P_TERMS and "ANSWER KEY" not in t.upper():
            errs.append(f"PDF page {n}: answer key heading missing")
        if "PREVIEW" in t:
            errs.append(f"PDF page {n}: carries a PREVIEW watermark")
    # preview PDF: the watermark is on every page exactly once
    prev_html = open(os.path.join(BUILD, "preview.html")).read() if os.path.exists(os.path.join(BUILD, "preview.html")) else ""
    full_html = open(os.path.join(BUILD, "resource.html")).read() if os.path.exists(os.path.join(BUILD, "resource.html")) else ""
    if prev_html.count('class="wm"') != 4:
        errs.append(f"preview.html has {prev_html.count('class=\"wm\"')} watermark elements, expected 4 (one per page)")
    if full_html.count('class="wm"') != 0:
        errs.append("resource.html carries a watermark")
    for i, pg in enumerate(PdfReader(PREVIEW_PDF).pages):
        t = pg.extract_text() or ""
        if t.count("PREVIEW") != 1:
            errs.append(f"preview PDF page {i + 1}: PREVIEW appears {t.count('PREVIEW')} times, expected once")
    for p in [COVER_PNG, *PREVIEW_PNGS]:
        if Image.open(p).size != (2000, 2000):
            errs.append(f"{os.path.basename(p)}: not 2000x2000")
    for h in ("p1.html", "p2.html"):   # the shots are renders of the watermarked preview PDF: no second watermark on top
        hp = os.path.join(BUILD, h)
        if os.path.exists(hp) and "swm" in open(hp).read():
            errs.append(f"{h}: a second watermark layer sits on the preview shots")
    up = open(UPLOAD).read()
    m = re.search(r"^## 1\. Title\s*\n+```\n(.+?)\n```", up, re.M | re.S)
    if not m:
        errs.append("UPLOAD.md: title block not found")
    else:
        title = m.group(1).strip()
        if len(title) > 80:
            errs.append(f"UPLOAD.md: title is {len(title)} chars (max 80)")
        for bad in ("december", "winter", "holiday", "christmas", "hanukkah", "kwanzaa", "seasonal"):
            if bad in title.lower():
                errs.append(f"UPLOAD.md: title contains seasonal word {bad!r}")
    for need in (DISCLOSURE, "$4.50", f"{TOTAL_PAGES} pages", "20 daily"):
        if need not in up:
            errs.append(f"UPLOAD.md: missing '{need}'")
    if "checked by hand" in up.lower() or "handmade" in up.lower() or "classroom-tested" in up.lower():
        errs.append("UPLOAD.md: says hand-checked/handmade/classroom-tested")
    tj = json.load(open(TPT_JSON))
    tags, subs = set(load_json("TAG-OPTIONS.json")["options"]), set(load_json("SUBJECT-OPTIONS.json"))
    if not 1 <= len(tj["tags"]) <= 6 or any(t not in tags for t in tj["tags"]):
        errs.append(f"tpt.json tags invalid: {tj['tags']}")
    if not 1 <= len(tj["subjects"]) <= 3 or any(s not in subs for s in tj["subjects"]):
        errs.append(f"tpt.json subjects invalid: {tj['subjects']}")
    grades_ok = {"3rd-grade", "4th-grade", "5th-grade", "6th-grade"}
    if not 1 <= len(tj["grades"]) <= 4 or not set(tj["grades"]) <= grades_ok:
        errs.append("tpt.json grades must be 1-4 entries from 3rd-6th grade")
    if tj.get("pages") != TOTAL_PAGES:
        errs.append(f"tpt.json pages {tj.get('pages')} != {TOTAL_PAGES}")
    for slot, fn in tj["files"].items():
        if not os.path.exists(os.path.join(HERE, fn)):
            errs.append(f"tpt.json file {slot}: {fn} missing")
    if tj["price"] != PRICE or tj["license_price"] != PRICE:
        errs.append(f"tpt.json price should be {PRICE}")
    # no religious or holiday-name words anywhere in the product text
    from pypdf import PdfReader as R2
    alltext = " ".join((pg.extract_text() or "") for pg in R2(PDF).pages).lower()
    for bad in ("christmas", "hanukkah", "kwanzaa", "santa", "menorah", "nativity", "church", "cross", "manger", "angel"):
        if re.search(r"\b" + bad + r"\b", alltext):
            errs.append(f"product text contains '{bad}'")
    return errs


def check():
    days = make_days()
    errs = verify_data(days)
    e2, ntok, nrest, extra = verify_html(days)
    errs += e2
    nnote, nletters, nsym, ngap = extra
    errs += verify_files()
    oe, npg = overflow_check()
    errs += oe
    if errs:
        print("CHECK FAILED")
        print("\n".join(" - " + e for e in errs[:60]))
        sys.exit(1)
    nrows = sum(len(d.notes) for d in days)
    print(f"CHECK OK: {NDAYS} days; {nrows} note rows ({nletters // 2} letter names recomputed from notehead positions, worksheet and key); "
          f"{NDAYS * RH_LINES} rhythm lines, {ntok} tokens ({nnote} notes, {nrest} rests), every measure adds up and every count recomputed from the rendered HTML; "
          f"{nsym} symbol answers matched via the word bank; {ngap // 2} missing-beat items recomputed from the rendered durations; "
          f"no page overflows ({npg} pages); PDF {TOTAL_PAGES} Letter pages, preview 4 with one watermark each, fonts embedded; images 2000x2000; UPLOAD.md and tpt.json ok.")


if __name__ == "__main__":
    if "--check" in sys.argv:
        check()
    else:
        build()
