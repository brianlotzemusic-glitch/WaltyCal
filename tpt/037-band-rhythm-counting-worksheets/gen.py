#!/usr/bin/env python3
"""Beginning Band Rhythm Counting Worksheets (TpT 037): build the resource and verify it.

    python3 gen.py           build everything (PDFs, PNGs) into this folder
    python3 gen.py --check   verify rhythms, counts, answer keys, layout, pages, fonts and files

Every exercise is one `Ex` object: measures of tokens (note or rest, kind, dot, start, duration).
The worksheet and the answer key are drawn from the same object; the written-in count of each token
is computed from its start time in the measure and the meter. `--check` does not trust that data:
it parses the HTML that was rendered, re-adds the durations of every measure with exact fractions
and recomputes every count with a second, independent method.

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

SLUG = "band-rhythm-counting-worksheets"
PDF = os.path.join(HERE, f"{SLUG}.pdf")
PREVIEW_PDF = os.path.join(HERE, f"{SLUG}-PREVIEW.pdf")
COVER_PNG = os.path.join(HERE, "cover.png")
PREVIEW_PNGS = [os.path.join(HERE, f"preview-{i}.png") for i in (1, 2, 3)]
UPLOAD = os.path.join(HERE, "UPLOAD.md")
TPT_JSON = os.path.join(HERE, "tpt.json")

STORE = "Brian Lotze"
BRAND = "Hudson Beat"
YEAR = 2026
ACCENT = "#0E7C86"   # deep teal: the one accent of this product
DISCLOSURE = "Created with the help of digital and AI tools. Notation and answer keys are verified before release."
TITLE = "Band Rhythm Counting Worksheets"

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


# ------------------------------------------------------------------ the 20 worksheets
# (title, meters (cycled over the 6 exercises), allowed cells, featured cells, skill line, tip)
PAGES = [
    ("Quarter notes and quarter rests", ["4/4"], ["Q", "QR"], ["QR"], "Count every note and rest. Each quarter note or rest gets one beat.", "Unit 1"),
    ("Half notes", ["4/4"], ["Q", "QR", "H"], ["H"], "A half note lasts 2 beats. Write the count where the note begins.", "Unit 1"),
    ("Half rests", ["4/4"], ["Q", "QR", "H", "HR"], ["HR"], "A half rest is 2 beats of silence. Count it like a note.", "Unit 1"),
    ("Whole notes and whole rests", ["4/4"], ["Q", "H", "HR", "W", "WR"], ["W", "WR"], "A whole note or rest fills a whole measure of 4/4.", "Unit 1"),
    ("Three-four time", ["3/4"], ["Q", "QR", "H"], ["H"], "In 3/4 there are 3 beats in every measure. Count 1 2 3.", "Unit 2"),
    ("Two-four time", ["2/4"], ["Q", "QR", "H"], ["H", "QR"], "In 2/4 there are 2 beats in every measure. Count 1 2.", "Unit 2"),
    ("Dotted half notes in 3/4", ["3/4"], ["Q", "H", "DH"], ["DH"], "A dot adds half the note's value: a dotted half note lasts 3 beats.", "Unit 3"),
    ("Dotted half notes in 4/4", ["4/4"], ["Q", "QR", "H", "DH"], ["DH"], "A dotted half note lasts 3 beats. Count the beat that comes after it.", "Unit 3"),
    ("Eighth notes in 4/4", ["4/4"], ["Q", "H", "E2"], ["E2"], "Two eighth notes fill one beat: count them 1 & (one-and).", "Unit 4"),
    ("Eighth notes and quarter rests", ["4/4"], ["Q", "QR", "H", "E2"], ["E2", "QR"], "Beamed eighth notes share a beam. Write 1 on the beat and & between beats.", "Unit 4"),
    ("Eighth notes in 3/4", ["3/4"], ["Q", "QR", "H", "E2"], ["E2"], "Count eighth notes in 3/4 as 1 & 2 & 3 &.", "Unit 4"),
    ("Eighth rests", ["4/4"], ["Q", "QR", "H", "E2", "EER", "ERE"], ["EER", "ERE"], "An eighth rest is half a beat of silence. Count it like a note.", "Unit 4"),
    ("Dotted quarter and eighth", ["4/4"], ["Q", "H", "E2", "DQE"], ["DQE"], "A dotted quarter lasts 1½ beats. The eighth after it lands on the &.", "Unit 5"),
    ("Dotted quarter and eighth in 2/4", ["2/4"], ["Q", "E2", "DQE"], ["DQE"], "In 2/4 one dotted quarter and eighth fill the whole measure.", "Unit 5"),
    ("Six-eight time: first steps", ["6/8"], ["DQ", "EEE"], ["EEE", "DQ"], "In 6/8 there are 6 counts in every measure. The eighth note gets one count.", "Unit 6"),
    ("Six-eight time: quarters and eighths", ["6/8"], ["DQ", "EEE", "QE", "EQ"], ["QE", "EQ"], "In 6/8 a quarter note is 2 counts and a dotted quarter is 3 counts.", "Unit 6"),
    ("Six-eight time: rests and dotted half", ["6/8"], ["DQ", "EEE", "QE", "EQ", "QRER", "EEER", "DH"], ["QRER", "EEER", "DH"], "A dotted half note is 6 counts in 6/8: a whole measure.", "Unit 6"),
    ("Review: 4/4, 3/4 and 2/4", ["4/4", "3/4", "2/4"], ["Q", "QR", "H", "HR", "DH", "E2", "EER", "ERE"], ["DH", "EER", "HR"], "Check the time signature first, then count each measure.", "Unit 7"),
    ("Review: dotted rhythms and eighths", ["4/4", "2/4"], ["Q", "QR", "H", "DH", "E2", "EER", "ERE", "DQE"], ["DQE", "ERE"], "Dotted quarter and eighth patterns, with rests.", "Unit 7"),
    ("Challenge: all the meters", ["4/4", "6/8", "3/4", "6/8", "2/4", "4/4"], ["Q", "QR", "H", "DH", "E2", "EER", "DQE", "DQ", "EEE", "QE", "EQ", "QRER"], ["DQE", "QE", "EQ", "DH"], "Every meter and every rhythm in this book. Read the time signature of each line.", "Unit 7"),
]
NPAGES = len(PAGES)
assert NPAGES == 20
PER_PAGE = 6
FEATURE_MIN = 2   # each featured cell appears at least this many times on its page (in a meter where it exists)


def measures_per_line(meter):
    return 2 if meter in ("4/4", "6/8") else 3


def build_page(pi):
    title, meters, allowed, featured, _, _ = PAGES[pi]
    for attempt in range(400):
        rng = random.Random(f"band-rhythm-{pi}-{attempt}")
        used = []      # cell-name lists
        exs, seen = [], {}
        for n in range(PER_PAGE):
            meter = meters[n % len(meters)]
            ms = []
            for _ in range(measures_per_line(meter)):
                for _ in range(30):
                    names = random_measure(rng, meter, allowed, featured)
                    key = (meter, tuple(names))
                    if seen.get(key, 0) < (2 if len(names) == 1 else 1):
                        break
                seen[key] = seen.get(key, 0) + 1
                ms.append(names)
                used.append((meter, names))
            exs.append((meter, ms))
        # every featured cell is used at least FEATURE_MIN times, and no exercise is a copy of a neighbour
        ok = all(sum(nm.count(f) for _, nm in used) >= FEATURE_MIN for f in featured if any(f in cells_for(m) for m in meters))
        if ok and all(exs[i] != exs[i + 1] for i in range(len(exs) - 1)):
            return [Ex(pi + 1, n + 1, m, [make_measure(m, names) for names in ms]) for n, (m, ms) in enumerate(exs)], used
    raise RuntimeError(f"page {pi + 1}: no valid draw")


def make_exercises():
    exs, cells_by_page = [], []
    for pi in range(NPAGES):
        e, used = build_page(pi)
        exs.append(e)
        cells_by_page.append(used)
    return exs, cells_by_page


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


# ------------------------------------------------------------------ legend, names
def tok_name(kind, rest, dot):
    return f"{'dotted ' if dot else ''}{kind} {'rest' if rest else 'note'}"


def dur_text(meter, kind, dot):
    d = tok_dur(kind, dot)
    if meter == "6/8":
        n = int(d * 8)
        return f"{n} count{'s' if n != 1 else ''}"
    b = d * 4
    txt = {F(1, 2): "½ beat", F(1): "1 beat", F(3, 2): "1½ beats"}.get(b) or f"{int(b)} beats"
    return txt


def legend_items(exs):
    seen = {}
    for ex in exs:
        for toks in ex.measures:
            for t in toks:
                seen.setdefault((t.kind, t.rest, t.dot), set()).add(ex.meter)
    order = {"whole": 0, "half": 1, "quarter": 2, "eighth": 3}
    return sorted(seen.items(), key=lambda kv: (kv[0][1], -order[kv[0][0]] * -1, kv[0][2]))


def legend_html(exs):
    cells = []
    for (kind, rest, dot), meters in legend_items(exs):
        parts = []
        if meters - {"6/8"}:
            parts.append(dur_text("4/4", kind, dot))
        if "6/8" in meters:
            parts.append(dur_text("6/8", kind, dot) + (" in 6/8" if meters - {"6/8"} else ""))
        svg = (f'<svg class="lg" width="38pt" height="34pt" viewBox="0 0 38 34">'
               f'<line x1="2" y1="21" x2="36" y2="21" stroke="#000" stroke-width="1.1"/>'
               f'{token_svg(kind, rest, dot, 15, 21, 6.0)}</svg>')
        cells.append(f'<div class="lgc">{svg}<div class="lgt"><b>{tok_name(kind, rest, dot)}</b><span>{" · ".join(parts)}</span></div></div>')
    return f'<div class="legend">{"".join(cells)}</div>'


def counting_line(exs):
    out = []
    for m in dict.fromkeys(ex.meter for ex in exs):
        if m == "6/8":
            out.append("6/8: 1 2 3 4 5 6")
        else:
            n = METERS[m][0]
            out.append(f"{m}: " + " ".join(f"{i}" if j == 0 else "&" for i in range(1, n + 1) for j in (0, 1)))
    return " · ".join(out)


# ------------------------------------------------------------------ pages (html)
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
.doc td, .doc th { border: 1pt solid #000; padding: 3.5pt 6pt; text-align: left; vertical-align: top; }
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

# page numbers
P_COVER, P_TEACH, P_REF = 1, 2, 3
P_WS0 = 4
P_KEY0 = P_WS0 + NPAGES            # 24
N_KEYPAGES = NPAGES // 2
P_TERMS = P_KEY0 + N_KEYPAGES      # 34
TOTAL_PAGES = P_TERMS


def ws_page_no(pi):
    return P_WS0 + pi


def key_page_no(pi):
    return P_KEY0 + pi // 2


def worksheet_page(pi, exs, watermark=False):
    title, meters, _, _, skill, unit = PAGES[pi]
    wm = '<div class="wm">PREVIEW</div>' if watermark else ""
    mlabel = " · ".join(dict.fromkeys(meters))
    how = (f'<div class="how"><b>Write in the counts.</b> {escape(skill)} Write the count in the box under each note or rest, '
           f'at the place where it begins.</div>')
    return (f'<section class="page">{wm}'
            f'<div class="top"><div class="h t">Rhythm Counting<small>{pi + 1}. {escape(title)}</small></div>'
            f'<div class="tag"><div class="lv">WORKSHEET {pi + 1}</div><div class="ln">{unit} · {mlabel}</div></div></div>'
            f'<div class="name">Name<span></span>Date<span class="d"></span></div>{how}'
            f'{legend_html(exs)}<div class="cnt">Counts to use: {counting_line(exs)}</div>'
            f'<div class="exs">{"".join(exercise_svg(e, "ws") for e in exs)}</div>'
            f'{foot(COPY, f"Answer key on page {key_page_no(pi)} · Page {ws_page_no(pi)}")}</section>')


def key_block(pi, exs):
    title = PAGES[pi][0]
    return (f'<div class="keyblock"><div class="kt"><div>Worksheet {pi + 1}<span> · {escape(title)}</span></div>'
            f'<span>page {ws_page_no(pi)}</span></div>{"".join(exercise_svg(e, "key") for e in exs)}</div>')


def key_page(kp, all_exs, watermark=False):
    pis = [2 * kp, 2 * kp + 1]
    wm = '<div class="wm">PREVIEW</div>' if watermark else ""
    return (f'<section class="page">{wm}'
            f'<div class="top"><div class="h t">Answer Key<small>Worksheets {pis[0] + 1} and {pis[1] + 1}</small></div>'
            f'<div class="tag"><div class="lv ak">ANSWER KEY</div><div class="ln">Counts are written where each note begins</div></div></div>'
            f'{"".join(key_block(pi, all_exs[pi]) for pi in pis)}'
            f'<div style="flex:1"></div>{foot(COPY, f"Answer key · Page {P_KEY0 + kp}")}</section>')


def demo_ex(meter, names, num=1):
    return Ex(0, num, meter, [make_measure(meter, n) for n in names])


def cover_art():
    """Two staff lines drawn like the worksheets, counts in the accent colour."""
    a = demo_ex("4/4", [["Q", "E2", "H"], ["DQE", "QR", "Q"]], 1)
    b = demo_ex("3/4", [["Q", "E2", "Q"], ["DH"]], 2)
    c = demo_ex("6/8", [["DQ", "EEE"], ["QE", "EQ"]], 3)
    return [exercise_svg(x, "key", scale_class="cv", w=400) for x in (a, b, c)]


def cover_page():
    a, b, c = cover_art()
    return (f'<section class="page cover"><div class="store">{BRAND}</div>'
            f'<div style="width:6.6in">{a}<div style="height:22pt"></div>{b}<div style="height:22pt"></div>{c}</div>'
            f'<div class="ctitle"><div class="a">BEGINNING BAND</div><div class="b">RHYTHM COUNTING</div>'
            f'<div class="c">Write in the counts · quarter notes to dotted rhythms and 6/8 — with answer keys</div></div>'
            f'<div class="cband">Grades 5–8 <em>·</em> 20 worksheets <em>·</em> answer keys</div></section>')


def unit_rows():
    units = {}
    for i, p in enumerate(PAGES):
        units.setdefault(p[5], []).append(i)
    return units


UNIT_TOPIC = {"Unit 1": "Quarter, half and whole notes and rests (4/4)", "Unit 2": "3/4 and 2/4 time",
              "Unit 3": "Dotted half notes", "Unit 4": "Eighth notes and eighth rests",
              "Unit 5": "Dotted quarter and eighth", "Unit 6": "6/8 time", "Unit 7": "Mixed review and challenge"}


def teacher_page():
    rows = "".join(
        f'<tr><td style="white-space:nowrap"><b>{u}</b></td><td>{UNIT_TOPIC[u]}</td>'
        f'<td style="white-space:nowrap">Worksheets {idx[0] + 1}–{idx[-1] + 1}</td><td style="white-space:nowrap">pp. {ws_page_no(idx[0])}–{ws_page_no(idx[-1])}</td></tr>'
        for u, idx in unit_rows().items())
    return (f'<section class="page doc"><div class="rule"><h1>Teacher Notes</h1>'
            f'<div class="l" style="font-size:13pt">{TITLE} · 20 worksheets · grades 5–8</div></div>'
            f'<div class="cols"><div>'
            f'<h2>How to use</h2><ul>'
            f'<li>Students look at the time signature, then write the count in the box under every note and every rest.</li>'
            f'<li><b>Write the count where each note or rest begins.</b> A half note on beat 1 gets a 1; the 2 is held, so nothing is written for it.</li>'
            f'<li>Rests are counted exactly like notes. They are silent beats, not skipped ones.</li>'
            f'<li>In 4/4, 3/4 and 2/4 the beat is a quarter note: count 1 2 3 4, and write <b>&amp;</b> for the half beat between (the “and” of a beat).</li>'
            f'<li>In 6/8 the eighth note gets one count: count 1 2 3 4 5 6. Counts 1 and 4 are the strong pulses. If you count 6/8 in two (1-la-li 2-la-li), write the numbers 1–6 anyway.</li>'
            f'<li>Check with the answer key, or clap, tap or play on one note with the class: say the counts aloud, then play.</li>'
            f'<li>Print single-sided. Every worksheet has 6 lines of two or three measures.</li></ul>'
            f'<h2>Great for</h2><ul><li>Band, orchestra and general music, grades 5–8</li><li>Warm-ups, homework, sub plans and rhythm quizzes</li>'
            f'<li>Practice before sight-reading or a new method-book page</li></ul>'
            f'</div><div>'
            f'<h2>Unit guide</h2><table><tr><th>Unit</th><th>Skill</th><th>Sheets</th><th>Pages</th></tr>{rows}</table>'
            f'<p class="small">Pages 4–23 are the worksheets. Pages {P_KEY0}–{P_TERMS - 1} are the answer keys: two worksheets per page, with the count written in accent color under every note and rest. '
            f'Page 3 is a student reference for note values and counting.</p>'
            f'<h2>Standards</h2><p>Practices reading, counting and understanding rhythm and meter. Supports the National Core Arts Standards for Music, Performing '
            f'(MU:Pr4.2, understanding the elements of music), in grades 5–8.</p>'
            f'<h2>Good to know</h2><p class="small">The rhythms are written on a one-line staff so students focus on counting, not pitch. Every line is generated and checked so that its measures add up to the time signature; '
            f'the keys are built from the same data as the worksheets. Notes of the same line are beamed by beat. No ties, no sixteenth notes and no songs are used. '
            f'No songs, lyrics or copyrighted characters are used.</p>'
            f'</div></div>{foot(COPY, "Page 2")}</section>')


def ref_cells():
    items = [("whole", 0, 0, "4 beats"), ("half", 0, 0, "2 beats"), ("quarter", 0, 0, "1 beat"), ("eighth", 0, 0, "½ beat"),
             ("half", 0, 1, "3 beats"), ("quarter", 0, 1, "1½ beats"), ("whole", 1, 0, "4 beats of silence"), ("half", 1, 0, "2 beats of silence"),
             ("quarter", 1, 0, "1 beat of silence"), ("eighth", 1, 0, "½ beat of silence")]
    cells = []
    for kind, rest, dot, beats in items:
        svg = (f'<svg width="60pt" height="38pt" viewBox="0 0 60 38"><line x1="6" y1="24" x2="54" y2="24" stroke="#000" stroke-width="1.1"/>'
               f'{token_svg(kind, rest, dot, 28, 24, 7.5)}</svg>')
        cells.append(f'<div class="refcell">{svg}<b>{tok_name(kind, rest, dot)}</b><span>{beats}</span></div>')
    return "".join(cells)


def ref_page():
    ex1 = demo_ex("4/4", [["Q", "E2", "H"], ["DQE", "QR", "Q"]], 1)
    ex2 = demo_ex("6/8", [["DQ", "EEE"], ["QE", "EQ"]], 2)
    return (f'<section class="page doc"><div class="rule"><h1>Student Reference</h1>'
            f'<div class="l" style="font-size:13pt">Keep this page nearby while you count.</div></div>'
            f'<h2>Note and rest values <span class="acc">·</span> <span class="l" style="text-transform:none;font-size:11pt">(in 4/4, 3/4 and 2/4)</span></h2>'
            f'<div class="refgrid">{ref_cells()}</div>'
            f'<p class="small">A dot after a note makes it half as long again: a half note is 2 beats, a dotted half note is 2 + 1 = 3 beats; '
            f'a quarter note is 1 beat, a dotted quarter note is 1 + ½ = 1½ beats.</p>'
            f'<h2>Reading the time signature</h2>'
            f'<table><tr><th>Meter</th><th>Top number</th><th>Bottom number</th><th>Count it</th></tr>'
            f'<tr><td><b>4/4</b></td><td>4 beats in a measure</td><td>quarter note = 1 beat</td><td>1 2 3 4 · eighths: 1 &amp; 2 &amp; 3 &amp; 4 &amp;</td></tr>'
            f'<tr><td><b>3/4</b></td><td>3 beats in a measure</td><td>quarter note = 1 beat</td><td>1 2 3 · eighths: 1 &amp; 2 &amp; 3 &amp;</td></tr>'
            f'<tr><td><b>2/4</b></td><td>2 beats in a measure</td><td>quarter note = 1 beat</td><td>1 2 · eighths: 1 &amp; 2 &amp;</td></tr>'
            f'<tr><td><b>6/8</b></td><td>6 counts in a measure</td><td>eighth note = 1 count</td><td>1 2 3 4 5 6</td></tr></table>'
            f'<h2>Counting in 4/4 and 6/8</h2>{exercise_svg(ex1, "key", scale_class="rf")}<div style="height:6pt"></div>{exercise_svg(ex2, "key", scale_class="rf")}'
            f'<p class="small" style="margin-top:4pt">In 6/8 a quarter note is 2 counts, a dotted quarter note is 3 counts and a dotted half note is 6 counts. '
            f'Write the count under the place where each note begins.</p>'
            f'<div style="flex:1"></div>{foot(COPY, "Page 3")}</section>')


def terms_page():
    return (f'<section class="page doc"><div class="rule"><h1>Terms of Use</h1>'
            f'<div class="l" style="font-size:13pt">Thank you for your purchase!</div></div>'
            f'<p>© {YEAR} {STORE}. {BRAND} by {STORE}. All rights reserved. This purchase gives <b>one teacher</b> a license to use this resource with their own students.</p>'
            f'<h2>You may</h2><ul><li>Print and copy pages for your own classroom and students, year after year.</li>'
            f'<li>Share pages with your own students through a password-protected class site or learning platform.</li>'
            f'<li>Use the pages with your own students when you have a substitute teacher.</li></ul>'
            f'<h2>You may not</h2><ul><li>Share, email or copy this resource for other teachers, a whole school or a district. '
            f'Additional licenses are available on Teachers Pay Teachers.</li>'
            f'<li>Post any part of it on a public website, shared drive or social media.</li>'
            f'<li>Sell, give away or claim any part of it as your own, or edit it into a new product.</li></ul>'
            f'<h2>Questions?</h2><p>Please use the Q&amp;A tab on the {BRAND} by {STORE} store on Teachers Pay Teachers. '
            f'If something looks wrong, let me know there and I will fix it.</p>'
            f'<h2>Credits</h2><ul>'
            f'<li>Rhythms, layouts and answer keys: original work, {BRAND} by {STORE}.</li>'
            f'<li>Music notation font: Bravura © Steinberg Media Technologies GmbH, SIL Open Font License 1.1.</li>'
            f'<li>Text fonts: Oswald (The Oswald Project Authors) and Source Sans 3 (Adobe), SIL Open Font License 1.1.</li></ul>'
            f'<p class="small">{DISCLOSURE}</p>'
            f'<div style="flex:1"></div>{foot(COPY, f"Page {P_TERMS}")}</section>')


def full_pages(all_exs):
    pages = [cover_page(), teacher_page(), ref_page()]
    pages += [worksheet_page(pi, all_exs[pi]) for pi in range(NPAGES)]
    pages += [key_page(kp, all_exs) for kp in range(N_KEYPAGES)]
    pages.append(terms_page())
    return pages


PREVIEW_PICKS = [("ws", 2), ("ws", 11), ("ws", 15), ("key", 7)]   # ws index (0-based) / key page index (0-based)


def preview_pages(all_exs):
    return [worksheet_page(i, all_exs[i], True) if k == "ws" else key_page(i, all_exs, True) for k, i in PREVIEW_PICKS]


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
       color: rgba(0,0,0,.14); white-space: nowrap; letter-spacing: .06em; }
.card { box-sizing: border-box; border: 2px solid #000; border-radius: 6px; padding: 5px 6px 2px; background: #fff; }
.card .ct { font-family: 'Oswald'; font-weight: 700; font-size: 16px; min-height: 34px; text-transform: uppercase; line-height: 1.05; }
.card .cm { font-family: 'Oswald'; font-weight: 300; font-size: 13px; }
""".replace("ACCENT", ACCENT)


def sq_doc(body):
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{font_css()}'
            f'html,body{{margin:0;background:#fff}}{SQ_CSS}</style></head><body>{body}</body></html>')


def cover_square():
    a, b, c = cover_art()
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div>'
        f'<div style="flex:1;display:flex;flex-direction:column;justify-content:space-evenly;align-items:center;width:100%;padding:0 0 80px">'
        f'<div style="width:900px">{a}<div style="height:10px"></div>{b}<div style="height:10px"></div>{c}</div>'
        f'<div><div class="hd" style="font-size:64px">Beginning Band</div>'
        f'<div class="hd" style="font-size:108px">Rhythm Counting</div>'
        f'<div class="sub" style="font-size:28px;margin-top:12px">Write in the counts \u00b7 quarter notes to dotted rhythms and 6/8</div></div>'
        f'</div><div class="band">Grades 5\u20138 <em>\u00b7</em> 20 worksheets <em>\u00b7</em> answer keys</div></div>')


def preview_square_1(img):
    labs = ["Quarter and half notes", "Eighth rests", "6/8 time"]
    shots = "".join(
        f'<div style="width:296px"><div class="shot"><img src="{img[i]}"><div class="swm" style="font-size:54px">PREVIEW</div></div>'
        f'<div class="lbl">{labs[i]}</div></div>' for i in range(3))
    units = "".join(f'<div><b style="font-weight:700">{u}</b> \u00b7 {UNIT_TOPIC[u]}</div>' for u in UNIT_TOPIC)
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div>'
        f'<div class="hd" style="font-size:76px;margin-top:20px">From quarter notes to 6/8</div>'
        f'<div class="sub" style="font-size:27px;margin-top:8px">Write the count under every note and every rest</div>'
        f'<div style="display:flex;gap:26px;margin-top:44px">{shots}</div>'
        f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:6px 30px;width:900px;margin-top:34px;font-family:Oswald;font-weight:300;font-size:21px">{units}</div>'
        f'<div class="band">20 worksheets <em>·</em> 7 units <em>·</em> grades 5–8</div></div>')


def preview_square_2(ws, key):
    pair = "".join(
        f'<div style="width:420px"><div class="shot"><img src="{src}"><div class="swm" style="font-size:80px">PREVIEW</div></div>'
        f'<div class="lbl">{lab}</div></div>' for src, lab in ((ws, "Worksheet"), (key, "Answer key")))
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div>'
        f'<div class="hd" style="font-size:70px;margin-top:20px">Answer keys included</div>'
        f'<div class="sub" style="font-size:27px;margin-top:8px">Every count is written in, ready to project or print</div>'
        f'<div style="display:flex;gap:40px;margin-top:30px">{pair}</div>'
        f'<div class="band">Keys for all 20 worksheets</div></div>')


def preview_square_3(all_exs):
    cards = []
    for pi in range(NPAGES):
        ex = all_exs[pi][0]
        one = Ex(0, 1, ex.meter, [ex.measures[0]])
        svg = exercise_svg(one, "key", scale_class="mini", w=250, pxw=190)
        cards.append(f'<div class="card" style="width:200px"><div class="ct">{pi + 1}. {escape(PAGES[pi][0])}</div>'
                     f'<div style="margin-top:3px">{svg}</div></div>')
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div>'
        f'<div class="hd" style="font-size:64px;margin-top:14px">20 worksheets, step by step</div>'
        f'<div style="display:flex;flex-wrap:wrap;gap:14px 14px;width:850px;margin-top:26px;justify-content:center">{"".join(cards)}</div>'
        f'<div class="band">Quarter notes <em>·</em> eighths <em>·</em> dotted rhythms <em>·</em> 6/8</div></div>')


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


def build():
    os.makedirs(BUILD, exist_ok=True)
    all_exs, _ = make_exercises()
    problems = verify_data(all_exs)
    if problems:
        print("\n".join(problems))
        sys.exit("data check failed; not rendering")
    full = write("resource.html", html_doc(full_pages(all_exs), TITLE))
    prev = write("preview.html", html_doc(preview_pages(all_exs), "Preview"))
    render([{"html": full, "pdf": PDF}, {"html": prev, "pdf": PREVIEW_PDF}])
    for i in range(1, 5):
        subprocess.run(["pdftoppm", "-png", "-r", "110", "-f", str(i), "-l", str(i), "-singlefile", PREVIEW_PDF,
                        os.path.join(BUILD, f"pv{i}")], check=True)
    sq = [write("cover.html", cover_square()), write("p1.html", preview_square_1(["pv1.png", "pv2.png", "pv3.png"])),
          write("p2.html", preview_square_2("pv3.png", "pv4.png")), write("p3.html", preview_square_3(all_exs))]
    outs = [COVER_PNG] + PREVIEW_PNGS
    render([{"html": h, "png": o, "width": 1000, "height": 1000, "scale": 2} for h, o in zip(sq, outs)])
    print(f"built {PDF}, {PREVIEW_PDF}, cover + 3 previews")


# ------------------------------------------------------------------ checks
def verify_data(all_exs):
    """Checks on the in-memory data: structure, bar sums, counts (second method), layout."""
    errs = []
    for pi, exs in enumerate(all_exs):
        if len(exs) != PER_PAGE:
            errs.append(f"page {pi + 1}: {len(exs)} exercises")
        for ex in exs:
            L = meter_len(ex.meter)
            xs, bars = exercise_geometry(ex)
            prev_x = None
            for mi, toks in enumerate(ex.measures):
                if sum(t.dur for t in toks) != L:
                    errs.append(f"{ex.id} m{mi + 1}: durations add to {sum(t.dur for t in toks)}, meter is {L}")
                # second counting method: running total in eighth notes
                e = 0
                for ti, t in enumerate(toks):
                    d8 = {"whole": 8, "half": 4, "quarter": 2, "eighth": 1}[t.kind]
                    if t.dot:
                        d8 = d8 * 3 // 2
                        if {"whole": 8, "half": 4, "quarter": 2, "eighth": 1}[t.kind] % 2:
                            errs.append(f"{ex.id}: dotted eighth not allowed")
                    if t.dur * 8 != d8:
                        errs.append(f"{ex.id} m{mi + 1} t{ti + 1}: dur {t.dur} != {d8}/8")
                    if ex.meter == "6/8":
                        want = str(e + 1)
                    else:
                        want = str(e // 2 + 1) if e % 2 == 0 else "&"
                    if t.count != want:
                        errs.append(f"{ex.id} m{mi + 1} t{ti + 1}: count {t.count!r}, expected {want!r}")
                    if t.start * 8 != e:
                        errs.append(f"{ex.id} m{mi + 1} t{ti + 1}: start {t.start} != {e}/8")
                    e += d8
                if e != int(L * 8):
                    errs.append(f"{ex.id} m{mi + 1}: {e}/8 in the bar, meter {ex.meter}")
                if all(t.rest for t in toks) and not (len(toks) == 1 and toks[0].kind == "whole"):
                    errs.append(f"{ex.id} m{mi + 1}: a measure of only rests")
                # layout: spacing, order and staff limits
                m0, m1 = bars[mi]
                for ti, x in enumerate(xs[mi]):
                    if prev_x is not None and x - prev_x < BOX_W + 2:
                        errs.append(f"{ex.id}: count boxes {x - prev_x:.1f}pt apart (need {BOX_W + 2:.0f})")
                    prev_x = x
                    if not (m0 + 4 < x - BOX_W / 2 and x + BOX_W / 2 < m1 - 3):
                        errs.append(f"{ex.id} m{mi + 1}: token {ti + 1} leaves its measure box")
                    right = x + 2.2 * S
                    if right >= m1 - 2:
                        errs.append(f"{ex.id} m{mi + 1}: token {ti + 1} too close to the barline")
        # features and variety
    for pi in range(NPAGES):
        _, meters, allowed, featured, _, _ = PAGES[pi]
        toks_by_cell = {}
        for ex in all_exs[pi]:
            if ex.meter not in meters:
                errs.append(f"{ex.id}: meter {ex.meter} not on the page spec")
        kinds = {(t.kind, t.rest, t.dot) for ex in all_exs[pi] for ms in ex.measures for t in ms}
        for f_ in featured:
            cells = SIMPLE_CELLS if f_ in SIMPLE_CELLS else COMPOUND_CELLS
            need = set(cells[f_])
            need = {(k, bool(r), bool(d)) for k, r, d in need}
            if not need <= kinds:
                errs.append(f"page {pi + 1}: featured rhythm {f_} missing")
    return errs


def parse_exercises(html):
    """Independent view of the rendered HTML: every <svg class='ex'> as (id, mode, meter, [measure [tok dict]])."""
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


def verify_html():
    errs = []
    p = os.path.join(BUILD, "resource.html")
    if not os.path.exists(p):
        return ["build/resource.html missing: run gen.py first"]
    html = open(p).read()
    exs = parse_exercises(html)
    ws = {e[0]: e for e in exs if e[1] == "ws" and not e[0].startswith("0.")}
    key = {e[0]: e for e in exs if e[1] == "key" and not e[0].startswith("0.")}
    if len(ws) != NPAGES * PER_PAGE or len(key) != NPAGES * PER_PAGE:
        errs.append(f"html has {len(ws)} worksheet lines and {len(key)} key lines, expected {NPAGES * PER_PAGE} each")
    dur8 = {"whole": 8, "half": 4, "quarter": 2, "eighth": 1}
    nrest = nnote = ntok = 0
    for eid, (_, _, meter, meas) in key.items():
        if eid not in ws or ws[eid][3] != [[{**t, 'count': t['count']} for t in m] for m in meas]:
            errs.append(f"{eid}: worksheet and answer key rhythms differ")
        want_bar = {"4/4": 8, "3/4": 6, "2/4": 4, "6/8": 6}[meter]
        for mi, toks in enumerate(meas):
            e = 0
            for t in toks:
                ntok += 1
                nrest += t["rest"]
                nnote += 1 - t["rest"]
                if t["kind"] not in dur8:
                    errs.append(f"{eid}: unknown kind {t['kind']}")
                    continue
                want = str(e + 1) if meter == "6/8" else (str(e // 2 + 1) if e % 2 == 0 else "&")
                if t["count"] != want:
                    errs.append(f"{eid} m{mi + 1}: written count {t['count']!r} but the note starts at eighth {e}: expected {want!r}")
                e += dur8[t["kind"]] * (3 if t["dot"] else 2) // 2
            if e != want_bar:
                errs.append(f"{eid} m{mi + 1}: {e} eighths in the measure, {meter} has {want_bar}")
    # the key text pages really show those counts: the preview/product PDF text of a key page lists them
    return errs, ntok, nrest, nnote


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
    # every worksheet page and key page carries the right heading and nothing is empty
    for i, pg in enumerate(rd.pages):
        t = pg.extract_text() or ""
        if len(t.strip()) < 40:
            errs.append(f"PDF page {i + 1} looks blank")
        n = i + 1
        if P_WS0 <= n < P_KEY0 and f"WORKSHEET {n - P_WS0 + 1}" not in t.upper().replace("\n", " "):
            errs.append(f"PDF page {n}: worksheet heading missing")
        if P_KEY0 <= n < P_TERMS and "ANSWER KEY" not in t.upper():
            errs.append(f"PDF page {n}: answer key heading missing")
    txt = " ".join(PdfReader(PREVIEW_PDF).pages[i].extract_text() for i in range(4))
    if txt.count("PREVIEW") < 4:
        errs.append("preview PDF: watermark missing on some pages")
    for p in [COVER_PNG, *PREVIEW_PNGS]:
        if Image.open(p).size != (2000, 2000):
            errs.append(f"{os.path.basename(p)}: not 2000x2000")
    up = open(UPLOAD).read()
    m = re.search(r"^## 1\. Title\s*\n+```\n(.+?)\n```", up, re.M | re.S)
    if not m:
        errs.append("UPLOAD.md: title block not found")
    elif len(m.group(1).strip()) > 80:
        errs.append(f"UPLOAD.md: title is {len(m.group(1).strip())} chars (max 80)")
    for need in (DISCLOSURE, "$5", f"{TOTAL_PAGES} pages", "20 worksheets"):
        if need not in up:
            errs.append(f"UPLOAD.md: missing '{need}'")
    if "checked by hand" in up.lower() or "handmade" in up.lower():
        errs.append("UPLOAD.md: says hand-checked/handmade")
    tj = json.load(open(TPT_JSON))
    tags, subs = set(load_json("TAG-OPTIONS.json")["options"]), set(load_json("SUBJECT-OPTIONS.json"))
    if not 1 <= len(tj["tags"]) <= 6 or any(t not in tags for t in tj["tags"]):
        errs.append(f"tpt.json tags invalid: {tj['tags']}")
    if not 1 <= len(tj["subjects"]) <= 3 or any(s not in subs for s in tj["subjects"]):
        errs.append(f"tpt.json subjects invalid: {tj['subjects']}")
    if not 1 <= len(tj["grades"]) <= 4:
        errs.append("tpt.json grades must be 1-4")
    if tj.get("pages") != TOTAL_PAGES:
        errs.append(f"tpt.json pages {tj.get('pages')} != {TOTAL_PAGES}")
    for slot, fn in tj["files"].items():
        if not os.path.exists(os.path.join(HERE, fn)):
            errs.append(f"tpt.json file {slot}: {fn} missing")
    if tj["price"] != "5.00":
        errs.append("tpt.json price should be 5.00")
    return errs


def check():
    all_exs, _ = make_exercises()
    errs = verify_data(all_exs)
    res = verify_html()
    ntok = nrest = nnote = 0
    if isinstance(res, tuple):
        e2, ntok, nrest, nnote = res
        errs += e2
    else:
        errs += res
    errs += verify_files()
    if errs:
        print("CHECK FAILED")
        print("\n".join(" - " + e for e in errs[:60]))
        sys.exit(1)
    nmeas = sum(len(ex.measures) for exs in all_exs for ex in exs)
    print(f"CHECK OK: {NPAGES * PER_PAGE} exercises, {nmeas} measures, {ntok} tokens ({nnote} notes, {nrest} rests) in the rendered key; "
          f"every measure adds up to its meter; every written count recomputed from the rendered HTML; worksheets and keys match; "
          f"layout spacing ok; PDF {TOTAL_PAGES} Letter pages, preview 4, fonts embedded; images 2000x2000; UPLOAD.md and tpt.json ok.")


if __name__ == "__main__":
    if "--check" in sys.argv:
        check()
    else:
        build()
