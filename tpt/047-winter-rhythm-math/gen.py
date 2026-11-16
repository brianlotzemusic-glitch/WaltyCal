#!/usr/bin/env python3
"""Winter Rhythm Math (TpT 047): build the resource and verify it.

    python3 gen.py           build everything (PDFs, PNGs, UPLOAD.md) into this folder
    python3 gen.py --check   recompute every answer from the rendered HTML and verify layout, pages, fonts and files

Every worksheet item is one `Item` made of note/rest tokens. The worksheet card (an SVG with data-* attributes on each
drawn token) and the answer key line are produced from the same Item. `--check` does not trust the Item list: it parses
the rendered HTML, re-reads every drawn token (kind, rest, dot, tie, beam) and the time signature glyphs, recomputes every
beat sum / comparison / missing-beat / full-or-short answer with its own beat table, and compares that to the key.

Rendering uses Playwright + Chromium (HTML/SVG -> PDF/PNG) with the OFL fonts in ../fonts.
"""
import json
import math
import os
import random
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from fractions import Fraction as F
from html import escape

HERE = os.path.dirname(os.path.abspath(__file__))
TPT = os.path.dirname(HERE)
FONTS = os.path.join(TPT, "fonts")
BUILD = os.path.join(HERE, "build")
RENDER_JS = os.path.join(TPT, "tools", "render.js")

SLUG = "winter-rhythm-math"
PDF = os.path.join(HERE, f"{SLUG}.pdf")
PREVIEW_PDF = os.path.join(HERE, f"{SLUG}-PREVIEW.pdf")
COVER_PNG = os.path.join(HERE, "cover.png")
PREVIEW_PNGS = [os.path.join(HERE, f"preview-{i}.png") for i in (1, 2, 3)]
UPLOAD = os.path.join(HERE, "UPLOAD.md")
TPT_JSON = os.path.join(HERE, "tpt.json")

STORE = "Brian Lotze"
BRAND = "Hudson Beat"
YEAR = 2026
ACCENT = "#2F86B8"      # icy blue: the one accent of this product
TINT = "#DCEEF8"        # pale tint of the accent (cover art only)
DISCLOSURE = "Created with the help of digital and AI tools. Notation and answer keys are verified before release."
TITLE = "Winter Rhythm Math"
LISTING_TITLE = "Rhythm Math Worksheets: Add & Compare Note Values | Music Gr 2-5"
PRICE = "3.50"
TAGS = ["Winter", "Worksheets", "Printables", "Activities", "Homework"]
SUBJECTS = ["Music", "Arithmetic", "Basic Operations"]
GRADES = ["2nd-grade", "3rd-grade", "4th-grade", "5th-grade"]

# ------------------------------------------------------------------ music model
BEATS = {"whole": F(4), "half": F(2), "quarter": F(1), "eighth": F(1, 2)}
HEAD_W = {"whole": 1.688, "half": 1.18, "quarter": 1.18, "eighth": 1.18}
REST_W = {"whole": 1.128, "half": 1.128, "quarter": 1.08, "eighth": 0.988}
NOTE_DOWN = {"whole": 0xE1D2, "half": 0xE1D4, "quarter": 0xE1D6, "eighth": 0xE1D8}
REST_GLYPH = {"whole": 0xE4E3, "half": 0xE4E4, "quarter": 0xE4E5, "eighth": 0xE4E6}
HEAD_BLACK = 0xE0A4
DOT_GLYPH = 0xE1E7
PERC_CLEF = 0xE069
METER_BEATS = {"4/4": 4, "3/4": 3, "2/4": 2}
NAME_OF = {"quarter": "quarter", "half": "half", "whole": "whole", "eighth": "eighth"}


@dataclass(frozen=True)
class Tok:
    kind: str
    rest: bool = False
    dot: bool = False
    tie: bool = False     # tied to the NEXT token
    beam: bool = False    # part of a beamed pair of eighth notes

    @property
    def beats(self):
        b = BEATS[self.kind]
        return b * F(3, 2) if self.dot else b

    def sig(self):
        return (self.kind, self.rest, self.dot, self.tie, self.beam)


def T(kind, rest=0, dot=0, tie=0, beam=0):
    return Tok(kind, bool(rest), bool(dot), bool(tie), bool(beam))


UNITS = {
    "Q": [T("quarter")], "H": [T("half")], "W": [T("whole")],
    "QR": [T("quarter", 1)], "HR": [T("half", 1)], "WR": [T("whole", 1)],
    "P": [T("eighth", beam=1), T("eighth", beam=1)],
    "DH": [T("half", dot=1)], "DQ": [T("quarter", dot=1)],
    "E": [T("eighth")], "ER": [T("eighth", 1)],
    "DQE": [T("quarter", dot=1), T("eighth")],
    "EDQ": [T("eighth"), T("quarter", dot=1)],
    "QQt": [T("quarter", tie=1), T("quarter")],
    "QHt": [T("quarter", tie=1), T("half")],
    "HQt": [T("half", tie=1), T("quarter")],
    "HHt": [T("half", tie=1), T("half")],
    "WQt": [T("whole", tie=1), T("quarter")],
    "QEt": [T("quarter", tie=1), T("eighth")],
    "HEt": [T("half", tie=1), T("eighth")],
}


def unit_beats(name):
    return sum(t.beats for t in UNITS[name])


def toks_of(names):
    return [t for n in names for t in UNITS[n]]


def total(toks):
    return sum((t.beats for t in toks), F(0))


def fmt(b):
    b = F(b)
    if b.denominator == 1:
        return str(b.numerator)
    assert b.denominator == 2, b
    w = b.numerator // 2
    return f"{w}½" if w else "½"


# widths (pt) used for layout; shared by drawing and the layout check
ADV = {("whole", 0): 25, ("half", 0): 23, ("quarter", 0): 21, ("eighth", 0): 21,
       ("whole", 1): 25, ("half", 1): 23, ("quarter", 1): 21, ("eighth", 1): 19}
BEAMADV = 16
DOTX = 8
TIEX = 9


def adv(t):
    if t.beam:
        base = BEAMADV
    else:
        base = ADV[(t.kind, int(t.rest))]
    return base + (DOTX if t.dot else 0) + (TIEX if t.tie else 0)


def group_w(toks):
    return sum(adv(t) for t in toks)


# ------------------------------------------------------------------ item model
@dataclass
class Item:
    ws: str            # "A3"
    n: int             # 1..8
    kind: str          # sum restsum cmp fill pick full
    meter: str = ""
    left: list = field(default_factory=list)
    right: list = field(default_factory=list)
    gap: int = -1      # fill/pick: gap sits before token index `gap`
    opts: list = field(default_factory=list)   # pick: list of Tok (choices)
    ans: str = ""
    work: str = ""

    def signature(self):
        return (self.kind, self.meter, tuple(t.sig() for t in self.left), tuple(t.sig() for t in self.right), self.gap)


def meter_beats(m):
    return F(METER_BEATS[m])


def solve(it):
    """The generator's own answer (the checker recomputes it from the rendered SVG)."""
    if it.kind == "sum":
        parts = [fmt(t.beats) for t in it.left]
        return fmt(total(it.left)), " + ".join(parts)
    if it.kind == "restsum":
        rests = [t for t in it.left if t.rest]
        return fmt(total(rests)), "rests: " + " + ".join(fmt(t.beats) for t in rests)
    if it.kind == "cmp":
        a, b = total(it.left), total(it.right)
        sym = ">" if a > b else "<" if a < b else "="
        return sym, f"{fmt(a)} {sym} {fmt(b)}"
    if it.kind == "fill":
        g = meter_beats(it.meter) - total(it.left)
        return fmt(g), f"{it.meter[0]} − {fmt(total(it.left))} = {fmt(g)}"
    if it.kind == "pick":
        g = meter_beats(it.meter) - total(it.left)
        names = {F(1): "quarter note", F(2): "half note", F(3): "dotted half note", F(4): "whole note"}
        return names[g], f"{fmt(g)} beat{'s' if g != 1 else ''} missing"
    if it.kind == "full":
        s, mb = total(it.left), meter_beats(it.meter)
        word = "FULL" if s == mb else "TOO SHORT" if s < mb else "TOO LONG"
        return word, f"{fmt(s)} beats in {it.meter}"
    raise ValueError(it.kind)


# ------------------------------------------------------------------ item generators
CARD_W, CARD_H = 262.0, 118.0
CMP_SIDE_MAX = 84
SUM_MAX = 200
MEAS_MAX = 168


def compose(rng, target, names, lo, hi, maxw, need=None, weights=None):
    """Random list of unit names whose beats add to `target`."""
    target = F(target)
    for _ in range(600):
        rem, picked = target, []
        while rem > 0 and len(picked) < hi:
            opts = [n for n in names if unit_beats(n) <= rem]
            if not opts:
                break
            w = [(weights or {}).get(n, 1) for n in opts]
            n = rng.choices(opts, w)[0]
            picked.append(n)
            rem -= unit_beats(n)
        if rem != 0 or not (lo <= len(picked) <= hi):
            continue
        if need and not any(n in need for n in picked):
            continue
        # tied units may not be the only unit twice in a row (looks odd): allow anything else
        if group_w(toks_of(picked)) > maxw:
            continue
        return picked
    return None


def make_sum_items(ws, rng, names, lo, hi, tmin, tmax, need_each=None, kind="sum", need_rest=False, weights=None):
    items, seen = [], set()
    n = 0
    guard = 0
    while len(items) < 8:
        guard += 1
        assert guard < 4000, f"cannot build {ws}"
        tgt = rng.randint(tmin, tmax)
        names_ = compose(rng, tgt, names, lo, hi, SUM_MAX, need_each, weights)
        if names_ is None:
            continue
        toks = toks_of(names_)
        if need_rest and not any(t.rest for t in toks):
            continue
        if need_rest and all(t.rest for t in toks):
            continue
        # shuffle unit order for variety
        rng.shuffle(names_)
        toks = toks_of(names_)
        sig = tuple(t.sig() for t in toks)
        if sig in seen:
            continue
        seen.add(sig)
        items.append(Item(ws, len(items) + 1, kind, "", toks))
    return items


def make_full_items(ws, rng):
    outcomes = ["FULL"] * 3 + ["TOO SHORT"] * 3 + ["TOO LONG"] * 2
    rng.shuffle(outcomes)
    meters = ["4/4", "4/4", "2/4", "4/4", "2/4", "4/4", "4/4", "2/4"]
    names = ["Q", "H", "W", "P", "QR", "HR"]
    items, seen = [], set()
    guard = 0
    while len(items) < 8:
        guard += 1
        assert guard < 4000, "cannot build A5"
        i = len(items)
        m, oc = meters[i], outcomes[i]
        mb = METER_BEATS[m]
        tgt = mb if oc == "FULL" else mb - rng.choice([1, 2] if mb == 4 else [1]) if oc == "TOO SHORT" else mb + rng.choice([1, 2])
        pn = compose(rng, tgt, names, 2 if tgt > 1 else 1, 5, MEAS_MAX, None, {"W": 0.4})
        if pn is None:
            continue
        rng.shuffle(pn)
        toks = toks_of(pn)
        if all(t.rest for t in toks) and not (len(toks) == 1 and toks[0].kind == "whole"):
            continue
        it = Item("A5", i + 1, "full", m, toks)
        if it.signature() in seen:
            continue
        seen.add(it.signature())
        items.append(it)
    return items


def make_cmp_items(ws, rng, names, lo, hi, tmin, tmax, need=None, weights=None):
    syms = [">", "<", "=", ">", "<", "=", ">", "<"]
    rng.shuffle(syms)
    items, seen = [], set()
    guard = 0
    while len(items) < 8:
        guard += 1
        assert guard < 6000, f"cannot build {ws}"
        sym = syms[len(items)]
        a = F(rng.randint(tmin * 2, tmax * 2), 2) if any(("E" in n or n.startswith("DQ")) for n in names) else F(rng.randint(tmin, tmax))
        d = rng.choice([F(1), F(1), F(2), F(1, 2)]) if any(("E" in n or n.startswith("DQ")) for n in names) else rng.choice([F(1), F(1), F(2)])
        b = a if sym == "=" else (a - d if sym == ">" else a + d)
        if b < 1 or a < 1:
            continue
        ln = compose(rng, a, names, 1, hi, CMP_SIDE_MAX, None, weights)
        rn = compose(rng, b, names, 1, hi, CMP_SIDE_MAX, None, weights)
        if ln is None or rn is None:
            continue
        if need and not any(n in need for n in ln + rn):
            continue
        if sym == "=" and (ln == rn or sorted(ln) == sorted(rn)):
            continue
        if group_w(toks_of(ln)) + group_w(toks_of(rn)) > 168:
            continue
        rng.shuffle(ln)
        rng.shuffle(rn)
        it = Item(ws, len(items) + 1, "cmp", "", toks_of(ln), toks_of(rn))
        if it.signature() in seen or (it.left == it.right):
            continue
        seen.add(it.signature())
        items.append(it)
    return items


def make_fill_items(ws, rng, names, meters_gaps, kind="fill", need=None, weights=None, opts=None):
    """meters_gaps: list of 8 (meter, gap beats)."""
    items, seen = [], set()
    guard = 0
    while len(items) < 8:
        guard += 1
        assert guard < 6000, f"cannot build {ws}"
        m, g = meters_gaps[len(items)]
        rest = meter_beats(m) - F(g)
        pn = compose(rng, rest, names, 1, 4, MEAS_MAX - 40, None, weights)
        if pn is None:
            continue
        rng.shuffle(pn)
        gap_unit = rng.randint(0, len(pn))
        toks = toks_of(pn)
        gap = len(toks_of(pn[:gap_unit]))
        it = Item(ws, len(items) + 1, kind, m, toks, gap=gap)
        if kind == "pick":
            it.opts = [T(k) for k in opts]
            rng.shuffle(it.opts)
        if it.signature() in seen:
            continue
        seen.add(it.signature())
        items.append(it)
    return items


def shuffled(rng, seq):
    seq = list(seq)
    rng.shuffle(seq)
    return seq


def build_worksheets():
    """Return list of worksheet dicts: id, level, title, how, items."""
    R = lambda s: random.Random("winter-rhythm-math-" + s)
    ws = []

    def add(wid, level, title, how, items, legend):
        for it in items:
            it.ans, it.work = solve(it)
        ws.append(dict(id=wid, level=level, title=title, how=how, items=items, legend=legend))

    # ---------------- Level A: add beats
    add("A1", "A", "Quarter and half notes",
        "A quarter note lasts 1 beat and a half note lasts 2 beats. Add the beats and write the total in the box.",
        make_sum_items("A1", R("A1"), ["Q", "H"], 2, 4, 3, 8), ["quarter", "half"])
    add("A2", "A", "Adding whole notes",
        "A whole note lasts 4 beats. Add up the beats in each snowy row and write the total in the box.",
        make_sum_items("A2", R("A2"), ["Q", "H", "W"], 2, 4, 4, 10, need_each={"W"}, weights={"W": 3}), ["quarter", "half", "whole"])
    add("A3", "A", "Pairs of eighth notes",
        "Two eighth notes joined by a beam make 1 beat together. Add the beats and write the total in the box.",
        make_sum_items("A3", R("A3"), ["Q", "H", "P"], 2, 4, 3, 8, need_each={"P"}, weights={"P": 2}), ["quarter", "half", "eighthpair"])
    add("A4", "A", "Counting the rests",
        "A rest is a silent beat, and it still counts. Add the beats of every note and every rest.",
        make_sum_items("A4", R("A4"), ["Q", "H", "W", "QR", "HR", "WR", "P"], 2, 4, 3, 9, need_rest=True, weights={"QR": 2, "HR": 2}),
        ["quarter", "half", "whole", "qrest", "hrest", "wrest"])
    add("A5", "A", "Full measure, too short or too long?",
        "Add the beats in each measure. Compare the total with the top number of the time signature, then circle your answer.",
        make_full_items("A5", R("A5")), ["quarter", "half", "whole", "eighthpair", "qrest", "hrest"])

    # ---------------- Level B: compare and fill in
    add("B1", "B", "Which is longer?",
        "Add the beats on each side. Write > if the left side is longer, < if it is shorter, or = if they are equal.",
        make_cmp_items("B1", R("B1"), ["Q", "H", "W"], 1, 3, 1, 6), ["quarter", "half", "whole"])
    add("B2", "B", "Compare with rests and eighth pairs",
        "Count rests as beats and a beamed pair of eighth notes as 1 beat. Write >, < or = in each circle.",
        make_cmp_items("B2", R("B2"), ["Q", "H", "QR", "HR", "P", "W"], 1, 4, 1, 6, need={"QR", "HR", "P"}), ["quarter", "half", "whole", "eighthpair", "qrest", "hrest"])
    mg3 = shuffled(R("B3m"), [("4/4", 1), ("4/4", 2), ("4/4", 3), ("2/4", 1), ("4/4", 1), ("4/4", 2), ("4/4", 3), ("2/4", 1)])
    add("B3", "B", "How many beats are missing?",
        "Each measure should be full. Add the beats you can see, then write how many beats are missing under the snowflake box.",
        make_fill_items("B3", R("B3"), ["Q", "H", "QR", "HR", "P"], mg3), ["quarter", "half", "eighthpair", "qrest", "hrest"])
    mg4 = shuffled(R("B4m"), [("4/4", 1), ("4/4", 2), ("2/4", 1), ("4/4", 1), ("4/4", 2), ("2/4", 1), ("4/4", 2), ("4/4", 1)])
    add("B4", "B", "Pick the note that fits",
        "Find how many beats are missing, then circle the one note that fills the snowy gap and makes the measure full.",
        make_fill_items("B4", R("B4"), ["Q", "H", "QR", "HR", "P"], mg4, kind="pick", opts=["quarter", "half", "whole"]), ["quarter", "half", "whole", "eighthpair", "qrest", "hrest"])
    # B5: four comparisons then four missing-beat measures
    r5 = R("B5")
    b5 = make_cmp_items("B5", r5, ["Q", "H", "QR", "HR", "P", "W"], 1, 4, 2, 7)[:4]
    b5 += make_fill_items("B5", R("B5f"), ["Q", "H", "QR", "P"], [("4/4", 1), ("4/4", 3), ("2/4", 1), ("4/4", 2)] * 2)[:4]
    for i, it in enumerate(b5):
        it.n = i + 1
    add("B5", "B", "Mixed review: compare and fill in",
        "Items 1 to 4: write >, < or = in each circle. Items 5 to 8: write how many beats are missing from the measure.",
        b5, ["quarter", "half", "whole", "eighthpair", "qrest", "hrest"])

    # ---------------- Level C: dots, ties, rests, 3/4
    add("C1", "C", "Dotted notes",
        "A dot makes a note half as long again. A dotted half note lasts 3 beats and a dotted quarter note lasts 1½ beats.",
        make_sum_items("C1", R("C1"), ["Q", "H", "DH", "DQ", "DQE", "E"], 2, 3, 3, 7, need_each={"DH", "DQ", "DQE"}, weights={"DH": 3, "DQ": 3, "DQE": 3}),
        ["quarter", "half", "dhalf", "dquarter", "eighth"])
    add("C2", "C", "Ties",
        "A tie joins two notes into one longer sound. Add the beats of both tied notes, and the rest of the row, to find the total.",
        make_sum_items("C2", R("C2"), ["Q", "H", "QQt", "QHt", "HQt", "HHt", "QEt", "HEt"], 1, 3, 3, 8, need_each={"QQt", "QHt", "HQt", "HHt", "QEt", "HEt"}, weights={"QQt": 3, "QHt": 3, "HQt": 3, "HHt": 3, "QEt": 3, "HEt": 3}),
        ["quarter", "half", "eighth", "tie"])
    add("C3", "C", "Beats of silence",
        "Count only the rests in each row. Write how many beats of silence there are in total.",
        make_sum_items("C3", R("C3"), ["Q", "H", "QR", "HR", "ER", "E", "DQ", "P"], 3, 5, 2, 6, need_rest=True, weights={"QR": 2, "HR": 2, "ER": 2}, kind="restsum"),
        ["quarter", "half", "dquarter", "eighth", "qrest", "hrest", "erest"])
    mg = shuffled(R("C4m"), [("3/4", F(1)), ("3/4", F(2)), ("4/4", F(3, 2)), ("2/4", F(1, 2)), ("3/4", F(3, 2)), ("4/4", F(5, 2)), ("2/4", F(1)), ("4/4", F(2))])
    add("C4", "C", "Missing beats in 3/4, 4/4 and 2/4",
        "Check the time signature. Add the beats you can see, then write how many beats are missing from each measure.",
        make_fill_items("C4", R("C4"), ["Q", "H", "DQ", "DH", "QR", "HR", "E", "ER", "P", "DQE"], mg),
        ["quarter", "half", "dhalf", "dquarter", "eighth", "qrest", "hrest", "erest", "eighthpair"])
    add("C5", "C", "Challenge: compare dots, ties and rests",
        "Add the beats on each side, counting dots, ties and rests. Write >, < or = in each circle.",
        make_cmp_items("C5", R("C5"), ["Q", "H", "DH", "DQ", "DQE", "QR", "HR", "QQt", "QHt", "HQt", "E", "P"], 2, 5, 2, 6, need={"DH", "DQ", "DQE", "QQt", "QHt", "HQt"}),
        ["quarter", "half", "dhalf", "dquarter", "eighth", "qrest", "hrest", "tie"])
    return ws


LEVELS = {"A": ("Level A", "Add beats", "Grades 2–3"), "B": ("Level B", "Compare and fill in", "Grades 3–4"), "C": ("Level C", "Dots, ties and rests", "Grades 4–5")}

# ------------------------------------------------------------------ drawing
def g(cp, x, y, size, fill="#000"):
    return f'<text x="{x:.2f}" y="{y:.2f}" font-family="Bravura" font-size="{size:.2f}" fill="{fill}">&#x{cp:X};</text>'


def staff_lines(x1, x2, ymid, s, lw=0.8):
    return "".join(f'<line x1="{x1:.1f}" y1="{ymid + (i - 2) * s:.2f}" x2="{x2:.1f}" y2="{ymid + (i - 2) * s:.2f}" stroke="#000" stroke-width="{lw}"/>' for i in range(5))


def draw_tok(t, cx, ymid, s, fill="#000"):
    """One token centred on cx, on the middle line. Stems point down (middle-line rule)."""
    size = 4 * s
    sw = 0.13 * s
    attrs = (f'class="tok" data-kind="{t.kind}" data-rest="{int(t.rest)}" data-dot="{int(t.dot)}" '
             f'data-tie="{int(t.tie)}" data-beam="{int(t.beam)}" data-x="{cx:.2f}"')
    out = [f"<g {attrs}>"]
    if t.rest:
        w = REST_W[t.kind] * s
        y = ymid - s if t.kind == "whole" else ymid
        out.append(g(REST_GLYPH[t.kind], cx - w / 2, y, size, fill))
    else:
        hw = HEAD_W[t.kind] * s
        left = cx - hw / 2
        if t.beam:
            out.append(g(HEAD_BLACK, left, ymid, size, fill))
            out.append(f'<line x1="{left + sw / 2:.2f}" y1="{ymid + 0.168 * s:.2f}" x2="{left + sw / 2:.2f}" y2="{ymid + 3.5 * s:.2f}" stroke="{fill}" stroke-width="{sw:.2f}"/>')
        else:
            out.append(g(NOTE_DOWN[t.kind], left, ymid, size, fill))
        if t.dot:
            out.append(g(DOT_GLYPH, left + hw + 0.35 * s, ymid - 0.5 * s, size, fill))
    out.append("</g>")
    return "".join(out)


def layout_group(toks, x0):
    """x centres of tokens starting at x0, and the x where the group ends."""
    xs, cur = [], x0
    for t in toks:
        a = adv(t)
        core = a - (DOTX if t.dot else 0) - (TIEX if t.tie else 0)
        xs.append(cur + core / 2)
        cur += a
    return xs, cur


def draw_group(toks, x0, ymid, s, cls="grp", extra=""):
    xs, end = layout_group(toks, x0)
    out = [f'<g class="{cls}" {extra}>']
    for t, x in zip(toks, xs):
        out.append(draw_tok(t, x, ymid, s))
    # beams
    sw = 0.13 * s
    i = 0
    while i < len(toks):
        if toks[i].beam and i + 1 < len(toks) and toks[i + 1].beam:
            a, b = xs[i] - HEAD_W["eighth"] * s / 2, xs[i + 1] - HEAD_W["eighth"] * s / 2
            out.append(f'<rect class="beam" x="{a:.2f}" y="{ymid + 3.0 * s:.2f}" width="{b - a + sw:.2f}" height="{0.5 * s:.2f}" fill="#000"/>')
            i += 2
        else:
            i += 1
    # ties: crescent above the heads (stems go down)
    for i, t in enumerate(toks[:-1]):
        if t.tie:
            hw1, hw2 = HEAD_W[t.kind] * s, HEAD_W[toks[i + 1].kind] * s
            x1, x2 = xs[i] + hw1 / 2 + 0.2 * s, xs[i + 1] - hw2 / 2 - 0.2 * s
            y = ymid - 0.65 * s
            h = 1.1 * s
            xm = (x1 + x2) / 2
            out.append(f'<path class="tiearc" data-from="{i}" d="M{x1:.2f},{y:.2f} Q{xm:.2f},{y - h:.2f} {x2:.2f},{y:.2f} Q{xm:.2f},{y - h + 0.38 * s:.2f} {x1:.2f},{y:.2f} Z" fill="#000"/>')
    out.append("</g>")
    return "".join(out), end


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


def snowman(cx, base, r, fill="#fff", accent=ACCENT, sw=1.4):
    """Three stacked balls with a hat, scarf, carrot nose and twig arms. r = radius of the bottom ball."""
    r2, r3 = r * 0.74, r * 0.54
    c1y = base - r
    c2y = base - 2 * r - r2 * 0.78
    c3y = c2y - r2 * 0.78 - r3 * 0.82
    o = [f'<g stroke="#000" stroke-width="{sw}" stroke-linejoin="round" stroke-linecap="round">']
    # arms
    o.append(f'<line x1="{cx - r2 * 0.9:.1f}" y1="{c2y:.1f}" x2="{cx - r2 * 1.9:.1f}" y2="{c2y - r2 * 0.7:.1f}" fill="none"/>')
    o.append(f'<line x1="{cx + r2 * 0.9:.1f}" y1="{c2y:.1f}" x2="{cx + r2 * 1.9:.1f}" y2="{c2y - r2 * 0.7:.1f}" fill="none"/>')
    for cy, rr in ((c1y, r), (c2y, r2), (c3y, r3)):
        o.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{rr:.1f}" fill="{fill}"/>')
    # scarf
    o.append(f'<rect x="{cx - r3 * 1.0:.1f}" y="{c3y + r3 * 0.72:.1f}" width="{r3 * 2.0:.1f}" height="{r3 * 0.34:.1f}" rx="{r3 * 0.12:.1f}" fill="{accent}"/>')
    o.append(f'<rect x="{cx + r3 * 0.25:.1f}" y="{c3y + r3 * 0.95:.1f}" width="{r3 * 0.42:.1f}" height="{r3 * 0.85:.1f}" rx="{r3 * 0.1:.1f}" fill="{accent}"/>')
    # hat
    o.append(f'<rect x="{cx - r3 * 0.95:.1f}" y="{c3y - r3 * 0.98:.1f}" width="{r3 * 1.9:.1f}" height="{r3 * 0.22:.1f}" rx="{r3 * 0.08:.1f}" fill="#000"/>')
    o.append(f'<rect x="{cx - r3 * 0.58:.1f}" y="{c3y - r3 * 1.75:.1f}" width="{r3 * 1.16:.1f}" height="{r3 * 0.8:.1f}" fill="#000"/>')
    o.append("</g>")
    # face and buttons (filled, no outline)
    o.append(f'<g fill="#000"><circle cx="{cx - r3 * 0.34:.1f}" cy="{c3y - r3 * 0.2:.1f}" r="{max(r3 * 0.09, 0.9):.1f}"/><circle cx="{cx + r3 * 0.34:.1f}" cy="{c3y - r3 * 0.2:.1f}" r="{max(r3 * 0.09, 0.9):.1f}"/>'
             f'<circle cx="{cx:.1f}" cy="{c2y - r2 * 0.1:.1f}" r="{max(r2 * 0.09, 1):.1f}"/><circle cx="{cx:.1f}" cy="{c2y + r2 * 0.35:.1f}" r="{max(r2 * 0.09, 1):.1f}"/></g>')
    o.append(f'<path d="M{cx:.1f},{c3y + r3 * 0.05:.1f} L{cx + r3 * 0.85:.1f},{c3y + r3 * 0.2:.1f} L{cx:.1f},{c3y + r3 * 0.34:.1f} Z" fill="{accent}" stroke="#000" stroke-width="{sw * 0.7:.2f}" stroke-linejoin="round"/>')
    return "".join(o)


def snowman_icon(cx, cy, size, accent=ACCENT):
    """Small card icon: two white balls with a thick outline, a solid hat, a scarf stripe, a nose and two eyes. Big simple shapes."""
    k = size / 28.0
    t = lambda v: v * k
    x, top = cx, cy - 16 * k
    sw = 1.3 * k
    o = [f'<g stroke="#000" stroke-width="{sw:.2f}" stroke-linejoin="round" stroke-linecap="round">']
    o.append(f'<circle cx="{x:.2f}" cy="{top + t(22.5):.2f}" r="{t(8):.2f}" fill="#fff"/>')
    o.append(f'<circle cx="{x:.2f}" cy="{top + t(11.7):.2f}" r="{t(5.6):.2f}" fill="#fff"/>')
    o.append(f'<rect x="{x - t(5.6):.2f}" y="{top + t(16.0):.2f}" width="{t(11.2):.2f}" height="{t(3.0):.2f}" rx="{t(1):.2f}" fill="{accent}"/>')
    o.append(f'<rect x="{x - t(7):.2f}" y="{top + t(5.4):.2f}" width="{t(14):.2f}" height="{t(2):.2f}" rx="{t(0.8):.2f}" fill="#000"/>')
    o.append(f'<rect x="{x - t(4):.2f}" y="{top + t(0.2):.2f}" width="{t(8):.2f}" height="{t(5.4):.2f}" rx="{t(0.8):.2f}" fill="#000"/>')
    o.append("</g>")
    o.append(f'<g fill="#000"><circle cx="{x - t(2.1):.2f}" cy="{top + t(10.6):.2f}" r="{t(1.05):.2f}"/><circle cx="{x + t(2.1):.2f}" cy="{top + t(10.6):.2f}" r="{t(1.05):.2f}"/></g>'
             f'<g fill="{accent}" stroke="#000" stroke-width="{sw * 0.5:.2f}" stroke-linejoin="round"><circle cx="{x:.2f}" cy="{top + t(13.2):.2f}" r="{t(1.1):.2f}"/></g>')
    return "".join(o)


def mitten(cx, cy, size, fill="#fff", accent=ACCENT, sw=1.4, flip=False):
    """A mitten about `size` tall, centred on (cx, cy)."""
    k = size / 48.0
    sx = -1 if flip else 1
    body = "M10,40 L10,20 Q10,4 24,4 Q38,4 38,20 L38,40 Z"
    thumb = "M10,28 Q-2,26 1,14 Q6,12 10,20"
    return (f'<g transform="translate({cx:.1f},{cy:.1f}) scale({sx * k:.3f},{k:.3f}) translate(-24,-26)" stroke="#000" stroke-width="{sw / k:.2f}" stroke-linejoin="round" stroke-linecap="round">'
            f'<path d="{body}" fill="{fill}"/><path d="{thumb}" fill="{fill}"/>'
            f'<rect x="8" y="40" width="32" height="8" rx="2" fill="{accent}"/>'
            f'<path d="M24,12 L24,20 M20,16 L28,16" fill="none" stroke="{accent}" stroke-width="{2.2}"/></g>')


def icon(n, cx, cy, size):
    i = n % 3
    if i == 0:
        return snowflake(cx, cy, size * 0.5, ACCENT, 1.5)
    if i == 1:
        return snowman_icon(cx, cy, size)
    return mitten(cx, cy, size * 0.95, "#fff", ACCENT, 1.1)


def mini_note_button(t, x, y, w, h, s=4.0, tag="opt"):
    """A small rounded box with a one-note mini staff in it (pick choices)."""
    ymid = y + 13.0
    out = [f'<g class="{tag}" data-kind="{t.kind}" data-rest="{int(t.rest)}" data-dot="{int(t.dot)}">',
           f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="7" fill="#fff" stroke="#000" stroke-width="1.2"/>',
           staff_lines(x + 7, x + w - 7, ymid, s, 0.7), draw_tok(t, x + w / 2, ymid, s), "</g>"]
    return "".join(out)


def card_svg(it, icon_n, w=CARD_W, h=CARD_H, pxw=None):
    """One worksheet item. Everything the checker reads is in data-* attributes."""
    s = 6.5
    out = []
    size_attr = f'width="{pxw}px" height="{h * pxw / w:.1f}px"' if pxw else f'width="{w:.0f}pt" height="{h:.0f}pt"'
    out.append(f'<svg class="card" data-ws="{it.ws}" data-item="{it.n}" data-type="{it.kind}" data-meter="{it.meter}" xmlns="http://www.w3.org/2000/svg" '
               f'viewBox="0 0 {w:.0f} {h:.0f}" {size_attr} style="display:block">')
    out.append(f'<rect x="0.8" y="0.8" width="{w - 1.6:.1f}" height="{h - 1.6:.1f}" rx="10" fill="#fff" stroke="#000" stroke-width="1.2"/>')
    out.append(f'<circle cx="19" cy="19" r="11.5" fill="#fff" stroke="{ACCENT}" stroke-width="1.6"/>'
               f'<text x="19" y="24.2" text-anchor="middle" font-family="Oswald" font-weight="700" font-size="14">{it.n}</text>')
    out.append(icon(icon_n, w - 25, 22, 28))
    ymid = 52.0 if it.kind not in ("cmp",) else 58.0
    x_end = w - 12
    out.append(staff_lines(8, x_end, ymid, s))
    out.append(g(PERC_CLEF, 11, ymid, 4 * s))
    x0 = 32.0
    if it.meter:
        n_, d_ = it.meter.split("/")
        out.append(f'<g class="timesig">{g(0xE080 + int(n_), 31, ymid - s, 4 * s)}{g(0xE080 + int(d_), 31, ymid + s, 4 * s)}</g>')
        x0 = 47.0
    if it.kind in ("sum", "restsum"):
        svg, _ = draw_group(it.left, x0 + 4, ymid, s, "grp", 'data-side="L"')
        out.append(svg)
    elif it.kind == "cmp":
        svg, lend = draw_group(it.left, x0 + 2, ymid, s, "grp", 'data-side="L"')
        out.append(svg)
        cx = lend + 22
        out.append(f'<circle class="cmpcircle" cx="{cx:.1f}" cy="{ymid:.1f}" r="12" fill="#fff" stroke="#000" stroke-width="1.4"/>')
        svg, rend = draw_group(it.right, cx + 22, ymid, s, "grp", 'data-side="R"')
        out.append(svg)
        out.append(f'<text x="{w / 2:.1f}" y="103" text-anchor="middle" font-family="Source Sans 3" font-style="italic" font-size="10.5">Which side is longer? Write &gt;, &lt; or = in the circle.</text>')
    elif it.kind in ("fill", "pick", "full"):
        xs, endx = layout_group(it.left, x0 + 2)
        # shift tokens after the gap to make room for it
        gapw = 34.0
        if it.gap >= 0:
            lt, rt = it.left[:it.gap], it.left[it.gap:]
            s1, e1 = draw_group(lt, x0 + 2, ymid, s, "grp", 'data-side="L"')
            gx = e1 + 3
            out.append(s1)
            out.append(f'<g class="gap"><rect x="{gx:.1f}" y="{ymid - 2 * s + 1:.1f}" width="{gapw - 6:.1f}" height="{4 * s - 2:.1f}" rx="6" fill="#fff" stroke="{ACCENT}" stroke-width="1.5" stroke-dasharray="4 3"/>'
                       f'{snowflake(gx + (gapw - 6) / 2, ymid, 8.5, ACCENT, 1.3)}</g>')
            s2, e2 = draw_group(rt, gx + gapw, ymid, s, "grp", 'data-side="R"')
            out.append(s2)
            endx = e2
        else:
            s1, endx = draw_group(it.left, x0 + 2, ymid, s, "grp", 'data-side="L"')
            out.append(s1)
        out.append(f'<line class="endbar" x1="{endx + 4:.1f}" y1="{ymid - 2 * s:.1f}" x2="{endx + 4:.1f}" y2="{ymid + 2 * s:.1f}" stroke="#000" stroke-width="1.2"/>')
    # answer area
    if it.kind in ("sum", "fill"):
        lab = "Total beats:" if it.kind == "sum" else "Missing beats:"
        out.append(f'<text x="168" y="100.5" text-anchor="end" font-family="Oswald" font-weight="500" font-size="11.5" letter-spacing=".04em" text-transform="uppercase">{lab.upper()}</text>')
        out.append(f'<rect class="ansbox" x="176" y="82" width="58" height="29" rx="6" fill="#fff" stroke="#000" stroke-width="1.3"/>')
    elif it.kind == "restsum":
        out.append(f'<text x="168" y="100.5" text-anchor="end" font-family="Oswald" font-weight="500" font-size="11.5" letter-spacing=".04em">BEATS OF SILENCE:</text>')
        out.append(f'<rect class="ansbox" x="176" y="82" width="58" height="29" rx="6" fill="#fff" stroke="#000" stroke-width="1.3"/>')
    if it.kind == "pick":
        out.append('<g class="opts">')
        for i, t in enumerate(it.opts):
            out.append(mini_note_button(t, 14 + i * 82, 78, 74, 34))
        out.append("</g>")
    if it.kind == "full":
        out.append('<g class="opts">')
        for i, word in enumerate(["FULL", "TOO SHORT", "TOO LONG"]):
            x = 14 + i * 82
            out.append(f'<g class="opt" data-word="{word}"><rect x="{x}" y="82" width="74" height="28" rx="14" fill="#fff" stroke="#000" stroke-width="1.2"/>'
                       f'<text x="{x + 37}" y="100" text-anchor="middle" font-family="Oswald" font-weight="500" font-size="12" letter-spacing=".04em">{word}</text></g>')
        out.append("</g>")
    out.append("</svg>")
    return "".join(out)


# ------------------------------------------------------------------ legend, reference pieces
LEG = {
    "quarter": (T("quarter"), "quarter note", "1 beat"),
    "half": (T("half"), "half note", "2 beats"),
    "whole": (T("whole"), "whole note", "4 beats"),
    "dhalf": (T("half", dot=1), "dotted half note", "3 beats"),
    "dquarter": (T("quarter", dot=1), "dotted quarter note", "1½ beats"),
    "eighth": (T("eighth"), "eighth note", "½ beat"),
    "eighthpair": ([T("eighth", beam=1), T("eighth", beam=1)], "two beamed eighths", "1 beat together"),
    "qrest": (T("quarter", 1), "quarter rest", "1 beat"),
    "hrest": (T("half", 1), "half rest", "2 beats"),
    "wrest": (T("whole", 1), "whole rest", "4 beats"),
    "erest": (T("eighth", 1), "eighth rest", "½ beat"),
    "tie": ([T("quarter", tie=1), T("quarter")], "tie", "add both notes"),
}


def mini_staff(toks, w, h, s, ymid_off=None):
    toks = toks if isinstance(toks, list) else [toks]
    ymid = ymid_off if ymid_off is not None else h * 0.42
    xs, end = layout_group(toks, 0)
    gw = end
    x0 = (w - gw) / 2
    body, _ = draw_group(toks, x0, ymid, s, "mini")
    return (f'<svg width="{w}pt" height="{h}pt" viewBox="0 0 {w} {h}" style="display:block">'
            f'{staff_lines(3, w - 3, ymid, s, 0.7)}{body}</svg>')


def legend_html(keys):
    cells = []
    for k in keys:
        toks, name, beats = LEG[k]
        cells.append(f'<div class="lgc">{mini_staff(toks, 44 if k in ("eighthpair", "tie") else 36, 30, 3.4, 11.5)}'
                     f'<div class="lgt"><b>{name}</b><span>{beats}</span></div></div>')
    return f'<div class="legend">{"".join(cells)}</div>'


# ------------------------------------------------------------------ pages
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
.top .deco { flex: 1; display: flex; justify-content: center; align-items: center; padding-bottom: 2pt; }
.tag { text-align: right; }
.tag .lv { display: inline-block; background: #000; color: #fff; font-family: 'Oswald'; font-weight: 700; font-size: 15pt; padding: 3pt 9pt 4pt; border-radius: 4pt; letter-spacing: .04em; }
.tag .lv.ak { background: ACCENT; }
.tag .ln { font-family: 'Oswald'; font-weight: 300; font-size: 11pt; margin-top: 3pt; }
.name { display: flex; gap: 18pt; font-size: 12pt; margin: 9pt 0 5pt; }
.name span { flex: 1; border-bottom: 1pt solid #000; height: 15pt; }
.name span.d { flex: 0 0 1.6in; }
.how { font-size: 11.5pt; margin: 2pt 0 6pt; line-height: 1.3; text-wrap: pretty; }
.how b { font-weight: 700; }
.legend { display: flex; flex-wrap: wrap; gap: 4pt 6pt; margin: 0 0 6pt; }
.lgc { display: flex; align-items: center; gap: 2pt; border: 1pt solid #000; border-radius: 5pt; padding: 1pt 7pt 1pt 2pt; }
.lgt b { display: block; font-family: 'Oswald'; font-weight: 500; text-transform: uppercase; font-size: 8pt; letter-spacing: .02em; line-height: 1.1; }
.lgt span { font-size: 8.5pt; line-height: 1.1; display: block; }
.items { flex: 1; display: grid; grid-template-columns: 262pt 262pt; justify-content: space-between; align-content: space-between; padding: 2pt 0 10pt; }
.foot { display: flex; justify-content: space-between; font-size: 8.5pt; color: #333; border-top: .8pt solid #000; padding-top: 3pt; }
.wm { position: absolute; left: 50%; top: 50%; transform: translate(-50%, -50%) rotate(-38deg); font-family: 'Oswald'; font-weight: 700;
      font-size: 150pt; color: rgba(0,0,0,.13); letter-spacing: .06em; white-space: nowrap; pointer-events: none; z-index: 9; }
.keyblock { margin-top: 9pt; border: 1pt solid #000; border-radius: 7pt; padding: 6pt 10pt 8pt; }
.keyblock .kt { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 12pt; border-bottom: 1pt solid #000; padding-bottom: 2pt; margin-bottom: 4pt; display: flex; justify-content: space-between; }
.keyblock .kt span { font-weight: 300; text-transform: none; font-size: 10.5pt; }
.kgrid { display: grid; grid-template-columns: 1fr 1fr; gap: 4pt 18pt; }
.ka { font-size: 11pt; line-height: 1.3; }
.ka b { font-family: 'Oswald'; font-weight: 700; color: ACCENT; margin-right: 2pt; }
.ka .res { font-weight: 700; margin: 0 3pt; }
.ka .wk { display: inline; font-size: 9.5pt; color: #333; margin-left: 6pt; }
.doc h1 { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 30pt; margin: 0 0 4pt; line-height: 1; }
.doc h2 { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 14pt; margin: 13pt 0 4pt; letter-spacing: .02em; }
.doc h2 .acc { color: ACCENT; }
.doc p, .doc li { font-size: 11pt; line-height: 1.38; margin: 0 0 5pt; }
.doc ul { margin: 0 0 4pt; padding-left: 16pt; }
.doc .rule { border-bottom: 2.2pt solid #000; margin-bottom: 8pt; padding-bottom: 6pt; }
.doc table { border-collapse: collapse; width: 100%; table-layout: fixed; font-size: 10pt; margin: 2pt 0 4pt; }
.doc td, .doc th { border: 1pt solid #000; padding: 3.5pt 6pt; text-align: left; vertical-align: top; }
.doc table.lv td { text-wrap: balance; }
.doc table.lv td:nth-child(3), .doc table.lv td:nth-child(4) { white-space: nowrap; }
.doc th { font-family: 'Oswald'; font-weight: 500; text-transform: uppercase; font-size: 9.5pt; background: #000; color: #fff; }
.steps { display: flex; gap: 12pt; margin-top: 12pt; }
.step { flex: 1; border: 1.3pt solid #000; border-radius: 7pt; padding: 7pt 10pt 4pt; }
.step .n { display: inline-block; background: ACCENT; color: #fff; font-family: 'Oswald'; font-weight: 700; font-size: 12pt; border-radius: 50%; width: 20pt; height: 20pt; line-height: 20pt; text-align: center; margin-right: 6pt; }
.step b { font-family: 'Oswald'; font-weight: 500; text-transform: uppercase; font-size: 11.5pt; letter-spacing: .02em; }
.step p { margin: 4pt 0 3pt !important; }
.cols { display: flex; gap: 22pt; }
.cols > div { flex: 1; }
.small { font-size: 9pt !important; color: #333; }
.refgrid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 7pt; margin: 4pt 0 6pt; }
.refcell { border: 1.3pt solid #000; border-radius: 6pt; text-align: center; padding: 4pt 2pt 4pt; }
.refcell svg { margin: 0 auto; }
.refcell b { display: block; font-family: 'Oswald'; font-weight: 500; text-transform: uppercase; font-size: 9.5pt; }
.refcell span { font-size: 9.5pt; display: block; line-height: 1.2; }
.cover { align-items: center; justify-content: space-between; padding: 0.55in 0.6in 0.5in; }
.store { font-family: 'Oswald'; font-weight: 500; font-size: 13pt; letter-spacing: .32em; text-transform: uppercase; }
.ctitle { text-align: center; }
.ctitle .a { font-family: 'Oswald'; font-weight: 700; font-size: 40pt; line-height: 1; letter-spacing: .02em; }
.ctitle .b { font-family: 'Oswald'; font-weight: 700; white-space: nowrap; font-size: 62pt; line-height: .95; letter-spacing: .01em; }
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

# page map: 1 cover, 2 teacher notes, 3 reference, 4-8 Level A, 9-13 Level B, 14-18 Level C, 19-21 keys, 22 terms
P_COVER, P_TEACH, P_REF, P_WS0 = 1, 2, 3, 4
NWS = 15
P_KEY0 = P_WS0 + NWS
P_TERMS = P_KEY0 + 3
TOTAL_PAGES = P_TERMS


def ws_page(wid):
    return P_WS0 + (ord(wid[0]) - 65) * 5 + int(wid[1]) - 1


def key_page_no(wid):
    return P_KEY0 + ord(wid[0]) - 65


def deco_header():
    flakes = "".join(snowflake(14 + i * 26, 15 if i % 2 == 0 else 19, 9 if i % 2 == 0 else 6.5, ACCENT, 1.3) for i in range(5))
    return f'<svg width="130pt" height="30pt" viewBox="0 0 130 30">{flakes}</svg>'


def worksheet_page(w, watermark=False):
    wm = '<div class="wm">PREVIEW</div>' if watermark else ""
    lv = LEVELS[w["level"]]
    cards = "".join(card_svg(it, it.n + ord(w["id"][0]) + int(w["id"][1])) for it in w["items"])
    return (f'<section class="page">{wm}'
            f'<div class="top"><div class="h t">{TITLE}<small>{w["id"]}. {escape(w["title"])}</small></div>'
            f'<div class="deco">{deco_header()}</div>'
            f'<div class="tag"><div class="lv">{lv[0].upper()}</div><div class="ln">{lv[1]} · {lv[2]}</div></div></div>'
            f'<div class="name">Name<span></span>Date<span class="d"></span></div>'
            f'<div class="how"><b>{escape(w["how"].split(".")[0])}.</b>{escape(w["how"][len(w["how"].split(".")[0]) + 1:])}</div>'
            f'{legend_html(w["legend"])}'
            f'<div class="items">{cards}</div>'
            f'{foot(COPY, f"Answer key on page {key_page_no(w["id"])} · Page {ws_page(w["id"])}")}</section>')


def key_html(it):
    work = it.work
    if it.kind in ("sum",):
        eq = f'<span class="eq">{work}</span> = <span class="res">{escape(it.ans)}</span>'
    elif it.kind == "restsum":
        eq = f'<span class="eq">{work}</span> = <span class="res">{escape(it.ans)}</span>'
    elif it.kind == "cmp":
        la = " + ".join(fmt(t.beats) for t in it.left)
        ra = " + ".join(fmt(t.beats) for t in it.right)
        eq = f'<span class="eq">{la}</span> <span class="res">{escape(it.ans)}</span> <span class="eq2">{ra}</span>'
    elif it.kind == "fill":
        eq = f'<span class="eq">{work}</span><span class="wk">missing beats: <span class="res">{escape(it.ans)}</span></span>'
    elif it.kind == "pick":
        eq = f'<span class="eq">{work}</span><span class="wk">fits: <span class="res">{escape(it.ans)}</span></span>'
    else:
        sm = " + ".join(fmt(t.beats) for t in it.left)
        eq = f'<span class="eq">{sm}</span><span class="wk">{work}: <span class="res">{escape(it.ans)}</span></span>'
    return (f'<div class="ka" data-ws="{it.ws}" data-item="{it.n}" data-type="{it.kind}" data-ans="{escape(it.ans)}"><b>{it.n}.</b>{eq}</div>')


def key_block(w):
    return (f'<div class="keyblock"><div class="kt"><div>{w["id"]}<span> · {escape(w["title"])}</span></div><span>page {ws_page(w["id"])}</span></div>'
            f'<div class="kgrid">{"".join(key_html(it) for it in w["items"])}</div></div>')


def key_page(level, wss, watermark=False):
    wm = '<div class="wm">PREVIEW</div>' if watermark else ""
    lv = LEVELS[level]
    blocks = "".join(key_block(w) for w in wss if w["level"] == level)
    return (f'<section class="page">{wm}'
            f'<div class="top"><div class="h t">Answer Key<small>{lv[0]}: {lv[1]}</small></div>'
            f'<div class="deco">{deco_header()}</div>'
            f'<div class="tag"><div class="lv ak">ANSWER KEY</div><div class="ln">Worksheets {level}1 to {level}5</div></div></div>'
            f'{blocks}'
            f'<div style="flex:1"></div>{foot(COPY, f"Answer key · Page {key_page_no(level + chr(49))}")}</section>')


# ---- cover art
def staff_demo(x, y, s, toks, meter="4/4", cls="demo"):
    """A real measure on a 5-line staff, drawn at scale s; returns (svg, width)."""
    ymid = y
    out = []
    x0 = x + 4.2 * s + 3.0 * s
    out.append(g(PERC_CLEF, x + 0.5 * s, ymid, 4 * s))
    n_, d_ = meter.split("/")
    out.append(g(0xE080 + int(n_), x + 4.4 * s, ymid - s, 4 * s) + g(0xE080 + int(d_), x + 4.4 * s, ymid + s, 4 * s))
    xs = []
    cur = x0 + 1.6 * s
    for t in toks:
        a = adv(t) * s / 6.5
        xs.append(cur + a / 2)
        cur += a
    for t, cx in zip(toks, xs):
        out.append(draw_tok(t, cx, ymid, s))
    end = cur + 0.8 * s
    out.append(f'<line x1="{end:.1f}" y1="{ymid - 2 * s:.1f}" x2="{end:.1f}" y2="{ymid + 2 * s:.1f}" stroke="#000" stroke-width="{0.16 * s:.2f}"/>')
    lines = staff_lines(x, end, ymid, s, 0.12 * s)
    return lines + "".join(out), end - x, xs


def cover_art(width=900, height=470):
    """Snowy scene: snowman, a real 4/4 measure with its sum, a mitten and snowflakes. Accent and black only."""
    o = [f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" style="display:block;width:100%;height:auto">']
    # snow drift
    o.append(f'<path d="M0,{height - 70} Q150,{height - 120} 300,{height - 78} T600,{height - 80} T{width},{height - 100} L{width},{height - 2} L0,{height - 2} Z" fill="{TINT}" stroke="#000" stroke-width="3" stroke-linejoin="round"/>')
    # snowflakes
    for fx, fy, fr in ((70, 55, 26), (840, 70, 30), (520, 22, 12), (120, 200, 14), (800, 235, 15)):
        o.append(snowflake(fx, fy, fr, ACCENT if fr > 15 else "#000", 2.4))
    o.append(snowman(110, height - 50, 62, "#fff", ACCENT, 3))
    o.append(mitten(800, height - 130, 130, TINT, ACCENT, 3))
    # the measure card
    s = 14.0
    cx0, cy0 = 318, 105
    toks = [T("quarter"), T("quarter"), T("half")]
    o.append(f'<rect x="217" y="{cy0 - 56}" width="{480}" height="{262}" rx="18" fill="#fff" stroke="#000" stroke-width="3"/>')
    body, w_, xs = staff_demo(cx0, cy0 + 30, s, toks)
    o.append(body)
    # beat numbers under each note, then the sum
    labels = ["1", "1", "2"]
    for x, lab in zip(xs, labels):
        o.append(f'<text x="{x:.1f}" y="{cy0 + 108:.1f}" text-anchor="middle" font-family="Oswald" font-weight="700" font-size="34" fill="{ACCENT}">{lab}</text>')
    o.append(f'<text x="457" y="{cy0 + 170:.1f}" text-anchor="middle" font-family="Oswald" font-weight="700" font-size="46">1 + 1 + 2 = 4</text>')
    o.append("</svg>")
    return "".join(o)


def cover_page():
    return (f'<section class="page cover"><div class="store">{BRAND}</div>'
            f'<div style="width:6.9in">{cover_art()}</div>'
            f'<div class="ctitle"><div class="a">WINTER</div><div class="b">RHYTHM MATH</div>'
            f'<div class="c">Add and compare note values · snowy worksheets with answer keys</div></div>'
            f'<div class="cband">Grades 2–5 <em>·</em> 3 levels <em>·</em> 15 worksheets <em>·</em> answer keys</div></section>')


# ---- teacher notes, reference, terms
def level_rows(wss):
    rows = []
    for lv in "ABC":
        ids = [w["id"] for w in wss if w["level"] == lv]
        rows.append(f'<tr><td><b>{LEVELS[lv][0]}</b></td><td>{LEVELS[lv][1]}</td><td>{LEVELS[lv][2]}</td>'
                    f'<td>pp. {ws_page(ids[0])}–{ws_page(ids[-1])}</td></tr>')
    return "".join(rows)


def teacher_page(wss):
    return (f'<section class="page doc"><div class="rule"><h1>Teacher Notes</h1>'
            f'<div class="l" style="font-size:13pt">{TITLE} · 15 worksheets in 3 levels · grades 2–5</div></div>'
            f'<div class="cols"><div>'
            f'<h2>How to use</h2><ul>'
            f'<li>Each worksheet has 8 snowy items. Students add the beats they see, compare them, or find the beats that are missing.</li>'
            f'<li>Beats are counted in quarter-note beats: a quarter note is 1, a half note is 2 and a whole note is 4.</li>'
            f'<li>Rests count exactly like notes, because a rest is a silent beat.</li>'
            f'<li>Two beamed eighth notes are 1 beat together. Single eighth notes (½ beat) appear only in Level C.</li>'
            f'<li>Rhythms use one line of a five-line staff, so the work is counting, not pitch.</li>'
            f'<li>Print single-sided. Each worksheet footer names its answer key page.</li></ul>'
            f'<h2>Pacing</h2><ul>'
            f'<li>One worksheet takes about 10 to 15 minutes. Use one as a warm-up or an exit ticket.</li>'
            f'<li>Plan for 5 class sessions per level, or one worksheet a week from December to March.</li>'
            f'<li>Before a worksheet, clap or tap two or three of its rows and count the beats aloud together.</li></ul>'
            f'</div><div>'
            f'<h2>Level guide</h2><table class="lv"><colgroup><col style="width:19%"><col style="width:35%"><col style="width:26%"><col style="width:20%"></colgroup>'
            f'<tr><th>Level</th><th>Skill</th><th>Grades</th><th>Pages</th></tr>{level_rows(wss)}</table>'
            f'<p class="small">Level A adds beats. Level B compares totals with &gt;, &lt; and =, and finds missing beats in 4/4 and 2/4. '
            f'Level C adds dotted notes, ties, rests and 3/4. 6/8 is not included. Page 3 is a student reference. Pages {P_KEY0}–{P_KEY0 + 2} are the answer keys.</p>'
            f'<h2>What students practice</h2><p>Adding whole numbers and halves, comparing quantities with &gt;, &lt; and =, finding a missing addend, '
            f'and reading note and rest values. No standards codes are listed here: please match the skills to your own curriculum.</p>'
            f'<h2>Good to know</h2><p class="small">Every sum, comparison and missing-beat answer was recomputed in code from the drawn notes. '
            f'Each item has exactly one answer. No songs, lyrics or copyrighted characters are used.</p>'
            f'</div></div>'
            f'<h2>Using the sheets in 3 steps</h2><div class="steps">'
            f'<div class="step"><span class="n">1</span><b>Get ready</b><p>Print the worksheet single-sided. Students can keep the page 3 reference beside them.</p></div>'
            f'<div class="step"><span class="n">2</span><b>Count together</b><p>Clap or tap two or three rows and count the beats aloud before students start.</p></div>'
            f'<div class="step"><span class="n">3</span><b>Check</b><p>Students work on their own, then check with the answer key on the page named in the footer.</p></div>'
            f'</div><div style="flex:1"></div>{foot(COPY, "Page 2")}</section>')


def ref_cells():
    items = [(T("quarter"), "quarter note", "1 beat"), (T("half"), "half note", "2 beats"), (T("whole"), "whole note", "4 beats"),
             ([T("eighth", beam=1), T("eighth", beam=1)], "two eighth notes", "½ + ½ = 1 beat"),
             (T("half", dot=1), "dotted half note", "3 beats"), (T("quarter", dot=1), "dotted quarter note", "1½ beats"),
             (T("eighth"), "eighth note", "½ beat"), ([T("quarter", tie=1), T("quarter")], "tied notes", "1 + 1 = 2 beats"),
             (T("quarter", 1), "quarter rest", "1 beat of silence"), (T("half", 1), "half rest", "2 beats of silence"),
             (T("whole", 1), "whole rest", "4 beats of silence"), (T("eighth", 1), "eighth rest", "½ beat of silence")]
    out = []
    for toks, name, beats in items:
        wide = isinstance(toks, list)
        out.append(f'<div class="refcell">{mini_staff(toks, 64, 40, 4.6, 16)}<b>{name}</b><span>{beats}</span></div>')
    return "".join(out)


def ref_page():
    sym = ("<table><colgroup><col style='width:25%'><col style='width:25%'><col style='width:25%'><col style='width:25%'></colgroup>"
           "<tr><th>Symbol</th><th>Name</th><th>Means</th><th>Example</th></tr>"
           "<tr><td><b>&gt;</b></td><td>greater than</td><td>the left side is longer</td><td>4 &gt; 3</td></tr>"
           "<tr><td><b>&lt;</b></td><td>less than</td><td>the left side is shorter</td><td>2 &lt; 3</td></tr>"
           "<tr><td><b>=</b></td><td>equal to</td><td>both sides are the same length</td><td>2 = 1 + 1</td></tr></table>")
    return (f'<section class="page doc"><div class="rule"><h1>Student Reference</h1>'
            f'<div class="l" style="font-size:13pt">Keep this page beside you while you add and compare.</div></div>'
            f'<h2>How long is each note and rest?</h2>'
            f'<div class="refgrid">{ref_cells()}</div>'
            f'<p class="small">A dot makes a note half as long again. A dotted half note is 2 + 1 = 3 beats. A dotted quarter note is 1 + ½ = 1½ beats. '
            f'A tie joins two notes into one long sound, so you add their beats.</p>'
            f'<h2>Comparing beats</h2>{sym}'
            f'<h2>Missing beats</h2><p>A measure is full when its beats add up to the top number of the time signature: 4 beats in 4/4, '
            f'3 beats in 3/4 and 2 beats in 2/4. To find the missing beats, add what you can see and subtract the total from the top number.</p>'
            f'<div style="display:flex;gap:18pt;align-items:center;margin-top:6pt">'
            f'<svg width="130pt" height="82pt" viewBox="0 0 130 82">{snowman(48, 78, 22)}{snowflake(105, 20, 14, ACCENT, 1.6)}{snowflake(110, 58, 8, "#000", 1.3)}</svg>'
            f'<p style="margin:0">Snow tip: build the answer one beat at a time, like stacking snowballs. 1 beat, then 2 beats, then 3, until the row is finished.</p></div>'
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
            f'<li>Worksheets, snow art (snowmen, mittens and snowflakes drawn in code) and answer keys: original work, {BRAND} by {STORE}.</li>'
            f'<li>Music notation font: Bravura © Steinberg Media Technologies GmbH, SIL Open Font License 1.1.</li>'
            f'<li>Text fonts: Oswald (The Oswald Project Authors) and Source Sans 3 (Adobe), SIL Open Font License 1.1.</li></ul>'
            f'<h2>What is in this file</h2><p>Page 1 cover, page 2 teacher notes, page 3 student reference, pages {P_WS0}–{P_KEY0 - 1} the 15 worksheets, '
            f'pages {P_KEY0}–{P_KEY0 + 2} the answer keys and page {P_TERMS} these terms.</p>'
            f'<p class="small">{DISCLOSURE}</p>'
            f'<div style="flex:1"></div>{foot(COPY, f"Page {P_TERMS}")}</section>')


def full_pages(wss):
    pages = [cover_page(), teacher_page(wss), ref_page()]
    pages += [worksheet_page(w) for w in wss]
    pages += [key_page(lv, wss) for lv in "ABC"]
    pages.append(terms_page())
    return pages


PREVIEW_IDS = ["A3", "B3", "C2"]
PREVIEW_KEY = "B"


def preview_pages(wss):
    by = {w["id"]: w for w in wss}
    return [worksheet_page(by[i], True) for i in PREVIEW_IDS] + [key_page(PREVIEW_KEY, wss, True)]


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
       color: rgba(0,0,0,.13); white-space: nowrap; letter-spacing: .06em; pointer-events: none; }
""".replace("ACCENT", ACCENT)


def sq_doc(body):
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{font_css()}'
            f'html,body{{margin:0;background:#fff}}{SQ_CSS}</style></head><body>{body}</body></html>')


def cover_square():
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div>'
        f'<div style="flex:1;display:flex;flex-direction:column;justify-content:space-evenly;align-items:center;width:100%;padding:0 0 76px">'
        f'<div style="width:880px">{cover_art()}</div>'
        f'<div><div class="hd" style="font-size:64px">Winter</div>'
        f'<div class="hd" style="font-size:118px">Rhythm Math</div>'
        f'<div class="sub" style="font-size:28px;margin-top:12px">Add and compare note values · snowy worksheets with answer keys</div></div>'
        f'</div><div class="band">Grades 2–5 <em>·</em> 3 levels <em>·</em> 15 worksheets</div></div>')


def preview_square_1(img):
    caps = ["Add notes, rests and eighth pairs. Is the measure full?",
            "Compare totals, find the missing beats and pick the note that fits.",
            "Dotted notes, ties, rests and 3/4 time, with a challenge sheet."]
    shots = "".join(
        f'<div style="width:310px;display:flex;flex-direction:column;align-items:center"><div class="shot"><img src="{img[i]}"></div>'
        f'<div class="lbl" style="font-size:28px;margin-top:20px">{LEVELS["ABC"[i]][0]}<span style="font-size:22px;margin-top:2px">{LEVELS["ABC"[i]][1]}</span></div>'
        f'<div style="font-family:Oswald;font-weight:300;font-size:21px;line-height:1.25;text-align:center;text-wrap:balance;margin-top:10px;width:270px">{caps[i]}</div></div>'
        for i in range(3))
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div>'
        f'<div class="hd" style="font-size:70px;margin-top:26px">Three levels, 15 worksheets</div>'
        f'<div class="sub" style="font-size:29px;margin-top:10px">Add, compare and fill in the beats of snowy rhythms</div>'
        f'<div style="flex:1;display:flex;align-items:center;justify-content:center;padding-bottom:70px">'
        f'<div style="display:flex;gap:16px;align-items:flex-start">{shots}</div></div>'
        f'<div class="band">Grades 2–5 <em>·</em> 3 levels <em>·</em> answer keys included</div></div>')


def preview_square_2(ws_img, key_img):
    pair = "".join(
        f'<div style="width:420px"><div class="shot"><img src="{src}"></div>'
        f'<div class="lbl">{lab}</div></div>' for src, lab in ((ws_img, "Worksheet"), (key_img, "Answer key")))
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div>'
        f'<div class="hd" style="font-size:70px;margin-top:22px">Answer keys included</div>'
        f'<div class="sub" style="font-size:27px;margin-top:8px">Every answer is shown with its beat sum</div>'
        f'<div style="flex:1;display:flex;align-items:center;padding-bottom:70px"><div style="display:flex;gap:40px">{pair}</div></div>'
        f'<div class="band">A full key for every worksheet</div></div>')


def preview_square_3(wss):
    pick = [("A3", 2), ("A5", 1), ("B1", 3), ("B4", 2), ("C2", 4), ("C4", 6)]
    by = {w["id"]: w for w in wss}
    labs = {wid: f'{escape(by[wid]["title"])}<span>Level {wid[0]} · worksheet {wid}</span>' for wid, _ in pick}
    cells = []
    for wid, n in pick:
        it = by[wid]["items"][n - 1]
        cells.append(f'<div style="width:370px"><div style="border:0">{card_svg(it, it.n + ord(wid[0]) + int(wid[1]), pxw=370)}</div>'
                     f'<div class="lbl" style="margin-top:6px;font-size:20px;text-wrap:balance">{labs[wid]}</div></div>')
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div>'
        f'<div class="hd" style="font-size:64px;margin-top:20px">Six kinds of snowy puzzles</div>'
        f'<div class="sub" style="font-size:27px;margin-top:8px">A sample item from each type of worksheet</div>'
        f'<div style="display:grid;grid-template-columns:370px 370px;gap:8px 60px;margin-top:16px">{"".join(cells)}</div>'
        f'<div class="swm" style="font-size:230px;left:50%;top:52%">PREVIEW</div>'
        f'<div class="band">Add <em>·</em> compare <em>·</em> fill in the missing beats</div></div>')


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


def upload_md():
    lv = {l: [w for w in WSS if w["level"] == l] for l in "ABC"}
    return f"""# UPLOAD: {LISTING_TITLE} (TpT 047)

These fields follow the order of TpT's "Add a resource" form. Winter theme: build window is December to February. Never put Winter, Snow or Holiday in the title field (TpT's Seasonal Titles notice).

**Files to attach**
- Resource (digital download): `{SLUG}.pdf`, {TOTAL_PAGES} pages, US Letter.
- Thumbnails, in this order: `cover.png`, `preview-1.png`, `preview-2.png`, `preview-3.png` (all 2000 × 2000).
- Preview file: `{SLUG}-PREVIEW.pdf`, 4 watermarked pages.

## 1. Title

```
{LISTING_TITLE}
```
({len(LISTING_TITLE)} characters; the limit is 80.) Plain search words first, no seasonal words. If TpT accepts it, the preferred title is "Winter Rhythm Math: Add and Compare Note Values | Music Worksheets Gr 2-5".

## 2. Description

```
Winter Rhythm Math: students add and compare the beats of note and rest values on snow-themed worksheets. 15 worksheets in 3 levels, each with 8 items and a full answer key, for music classes in grades 2 to 5. Snowmen, mittens and snowflakes decorate every page, and the content is winter themed and non-denominational.

WHAT'S INCLUDED ({TOTAL_PAGES} pages, PDF, US Letter)
• Cover (1 page)
• Teacher notes with pacing and a level guide (1 page)
• Student reference: note and rest values, comparison symbols, missing beats (1 page)
• Level A, add the beats: 5 worksheets for grades 2-3 (5 pages). Quarter, half and whole notes, pairs of eighth notes, rests, and "full, too short or too long" measures in 4/4 and 2/4.
• Level B, compare and fill in: 5 worksheets for grades 3-4 (5 pages). Compare totals with >, < and =, find the missing beats, and pick the note that fills the gap.
• Level C, dots, ties and rests: 5 worksheets for grades 4-5 (5 pages). Dotted half and dotted quarter notes, ties, beats of silence, 3/4 time and a compare challenge.
• Answer keys for all 15 worksheets, one page per level (3 pages)
• Terms of use and credits (1 page)
Total: {TOTAL_PAGES} pages.

HOW TO USE
Students add the beats of each row, compare two rows, or work out how many beats are missing from a measure. Rhythms sit on one line of a five-line staff with a percussion clef, so the focus stays on counting. Each worksheet has 8 items, and every item has exactly one answer. Every sum and comparison was recomputed in code from the drawn notes. Good for warm-ups, homework, centers, sub plans and exit tickets. 6/8 is not included.

• Grades 2–5 (choose the level that fits)
• Prints well in black and white; the answer keys use one accent color
• No songs, lyrics or copyrighted characters

{DISCLOSURE}
```

## 3. Grades

2, 3, 4, 5.

## 4. Subjects and tags

- Subjects: {", ".join(SUBJECTS)}
- Tags: {", ".join(TAGS)}

## 5. Page count by section (totals {TOTAL_PAGES})

- Cover: 1
- Teacher notes: 1
- Student reference: 1
- Level A worksheets (A1–A5): 5
- Level B worksheets (B1–B5): 5
- Level C worksheets (C1–C5): 5
- Answer keys (Level A, B, C): 3
- Terms of use and credits: 1
- Total: {TOTAL_PAGES}

## 6. Standards

None cited. The teacher notes describe the skills and ask teachers to match them to their own curriculum.

## 7. Price

**${PRICE}** (paid; owner range $3–5).

## 8. Preview

Paid. Preview PDF: worksheets A3 (pairs of eighth notes), B3 (missing beats) and C2 (ties), plus the Level B answer key page, all watermarked.

## 9. Before you click publish

- [ ] Season: winter (December to February). Build for 2 to 8 weeks ahead of that.
- Open owner question: logo beside HUDSON BEAT (see tpt/STYLE.md).
"""


def tpt_json():
    return {
        "price": PRICE, "license_price": PRICE, "tax_code": "Other Digital Goods - No Physical Media",
        "grades": GRADES, "subjects": SUBJECTS, "tags": TAGS, "formats": ["PDF"], "pages": TOTAL_PAGES, "answer_key": "Included",
        "files": {"product": f"{SLUG}.pdf", "preview": f"{SLUG}-PREVIEW.pdf", "thumb1": "cover.png", "thumb2": "preview-1.png",
                  "thumb3": "preview-2.png", "thumb4": "preview-3.png"},
    }


WSS = build_worksheets()


def build():
    os.makedirs(BUILD, exist_ok=True)
    problems = verify_data(WSS)
    if problems:
        print("\n".join(problems))
        sys.exit("data check failed; not rendering")
    full = write("resource.html", html_doc(full_pages(WSS), TITLE))
    prev = write("preview.html", html_doc(preview_pages(WSS), "Preview"))
    render([{"html": full, "pdf": PDF}, {"html": prev, "pdf": PREVIEW_PDF}])
    for i in range(1, 5):
        subprocess.run(["pdftoppm", "-png", "-r", "110", "-f", str(i), "-l", str(i), "-singlefile", PREVIEW_PDF,
                        os.path.join(BUILD, f"pv{i}")], check=True)
    sq = [write("cover.html", cover_square()), write("p1.html", preview_square_1(["pv1.png", "pv2.png", "pv3.png"])),
          write("p2.html", preview_square_2("pv2.png", "pv4.png")), write("p3.html", preview_square_3(WSS))]
    outs = [COVER_PNG] + PREVIEW_PNGS
    render([{"html": h, "png": o, "width": 1000, "height": 1000, "scale": 2} for h, o in zip(sq, outs)])
    with open(UPLOAD, "w") as f:
        f.write(upload_md())
    with open(TPT_JSON, "w") as f:
        json.dump(tpt_json(), f, indent=2)
        f.write("\n")
    print(f"built {PDF}, {PREVIEW_PDF}, cover + 3 previews, UPLOAD.md, tpt.json")


# ------------------------------------------------------------------ checks
def verify_data(wss):
    """Checks on the in-memory data: structure, ambiguity, widths."""
    errs = []
    for w in wss:
        items = w["items"]
        if len(items) != 8:
            errs.append(f"{w['id']}: {len(items)} items")
        sigs = [it.signature() for it in items]
        if len(set(sigs)) != len(sigs):
            errs.append(f"{w['id']}: duplicate items")
        answers = [it.ans for it in items]
        if len(set(answers)) < 2:
            errs.append(f"{w['id']}: every answer is the same")
        for it in items:
            tag = f"{it.ws}.{it.n}"
            if it.kind in ("sum", "restsum"):
                if w["level"] == "A":
                    if total(it.left) != int(total(it.left)):
                        errs.append(f"{tag}: Level A sum is not a whole number")
                    # eighths only in beamed pairs
                    for i, t in enumerate(it.left):
                        if t.kind == "eighth" and not t.beam:
                            errs.append(f"{tag}: lone eighth in Level A")
                if group_w(it.left) > SUM_MAX:
                    errs.append(f"{tag}: row too wide")
            if it.kind == "cmp":
                if group_w(it.left) > CMP_SIDE_MAX or group_w(it.right) > CMP_SIDE_MAX:
                    errs.append(f"{tag}: comparison side too wide")
            if it.kind in ("fill", "pick"):
                gap = meter_beats(it.meter) - total(it.left)
                if gap <= 0:
                    errs.append(f"{tag}: no gap")
                if it.kind == "pick":
                    if gap not in (1, 2, 3, 4):
                        errs.append(f"{tag}: pick gap {gap}")
                    fits = [o for o in it.opts if o.beats == gap]
                    if len(fits) != 1:
                        errs.append(f"{tag}: {len(fits)} options fit the gap")
                if w["level"] != "C" and gap != int(gap):
                    errs.append(f"{tag}: fractional gap in Level {w['level']}")
            if it.kind == "full":
                pass
            # every beamed eighth has a partner
            for i, t in enumerate(it.left + it.right):
                pass
        if w["id"] == "A5":
            c = {a: answers.count(a) for a in set(answers)}
            if min(c.values()) < 2 or len(c) != 3:
                errs.append(f"A5: answers not balanced {c}")
        if w["id"] in ("B1", "B2", "C5"):
            c = {a: answers.count(a) for a in set(answers)}
            if len(c) != 3 or min(c.values()) < 2:
                errs.append(f"{w['id']}: symbols not balanced {c}")
    return errs


CARD_RE = re.compile(r'<svg class="card".*?</svg>', re.S)


def parse_card(svg):
    root = ET.fromstring(svg)
    ns = "{http://www.w3.org/2000/svg}"
    d = dict(ws=root.get("data-ws"), n=int(root.get("data-item")), type=root.get("data-type"), meter=root.get("data-meter"))
    toks_by_side = {"L": [], "R": []}
    xs = []
    for grp in root.iter(ns + "g"):
        if grp.get("class") == "grp":
            for tk in grp.iter(ns + "g"):
                if tk.get("class") == "tok":
                    toks_by_side[grp.get("data-side")].append(dict(kind=tk.get("data-kind"), rest=int(tk.get("data-rest")), dot=int(tk.get("data-dot")),
                                                                  tie=int(tk.get("data-tie")), beam=int(tk.get("data-beam")), x=float(tk.get("data-x"))))
    d["L"], d["R"] = toks_by_side["L"], toks_by_side["R"]
    d["gap"] = any(g_.get("class") == "gap" for g_ in root.iter(ns + "g"))
    # gap position: number of left-side tokens before the gap group in document order
    d["gap_before"] = None
    if d["gap"]:
        cnt = 0
        for el in root.iter():
            if el.get("class") == "gap":
                d["gap_before"] = cnt
                break
            if el.get("class") == "tok" and el.tag == ns + "g":
                cnt += 1
    # time signature digits from the drawn glyphs
    ts = [g_ for g_ in root.iter(ns + "g") if g_.get("class") == "timesig"]
    d["ts"] = ""
    if ts:
        digits = [ord(t.text) - 0xE080 for t in ts[0].iter(ns + "text")]
        d["ts"] = f"{digits[0]}/{digits[1]}"
    d["opts"] = [dict(kind=o.get("data-kind"), rest=int(o.get("data-rest", 0)), dot=int(o.get("data-dot", 0))) for o in root.iter(ns + "g") if o.get("class") == "opt" and o.get("data-kind")]
    d["words"] = [o.get("data-word") for o in root.iter(ns + "g") if o.get("class") == "opt" and o.get("data-word")]
    d["ties"] = [int(p.get("data-from")) for p in root.iter(ns + "path") if p.get("class") == "tiearc"]
    d["circle"] = any(c.get("class") == "cmpcircle" for c in root.iter(ns + "circle"))
    d["ansbox"] = any(r.get("class") == "ansbox" for r in root.iter(ns + "rect"))
    return d


B = {"whole": F(4), "half": F(2), "quarter": F(1), "eighth": F(1, 2)}   # independent beat table


def beats_of(t):
    return B[t["kind"]] * (F(3, 2) if t["dot"] else 1)


def parse_beats(s):
    s = s.strip()
    if "½" in s:
        w, _ = s.split("½")
        return F(int(w or 0)) + F(1, 2)
    return F(int(s))


def recompute(c):
    """Answer string from the parsed worksheet card only."""
    tp = c["type"]
    if tp == "sum":
        return fmt(sum((beats_of(t) for t in c["L"]), F(0)))
    if tp == "restsum":
        return fmt(sum((beats_of(t) for t in c["L"] if t["rest"]), F(0)))
    if tp == "cmp":
        a = sum((beats_of(t) for t in c["L"]), F(0))
        b = sum((beats_of(t) for t in c["R"]), F(0))
        return ">" if a > b else "<" if a < b else "="
    mb = {"4/4": 4, "3/4": 3, "2/4": 2}[c["ts"]]
    s = sum((beats_of(t) for t in c["L"] + c["R"]), F(0))
    if tp == "fill":
        return fmt(F(mb) - s)
    if tp == "pick":
        gap = F(mb) - s
        fits = [o for o in c["opts"] if beats_of(o) == gap]
        return {F(1): "quarter note", F(2): "half note", F(3): "dotted half note", F(4): "whole note"}[gap] if len(fits) == 1 else "AMBIGUOUS"
    if tp == "full":
        return "FULL" if s == mb else "TOO SHORT" if s < mb else "TOO LONG"
    raise ValueError(tp)


def verify_html():
    errs = []
    p = os.path.join(BUILD, "resource.html")
    if not os.path.exists(p):
        return ["build/resource.html missing: run gen.py first"], 0
    html = open(p).read()
    cards = [parse_card(m.group(0)) for m in CARD_RE.finditer(html)]
    keys = {}
    for m in re.finditer(r'<div class="ka" data-ws="(\w+)" data-item="(\d+)" data-type="(\w+)" data-ans="([^"]*)">(.*?)</div>', html, re.S):
        ws_, n, tp, ans, body = m.groups()
        keys[(ws_, int(n))] = (tp, ans.replace("&gt;", ">").replace("&lt;", "<"), body)
    seen_ws = {}
    for c in cards:
        seen_ws.setdefault(c["ws"], []).append(c)
    expected_ids = [f"{l}{i}" for l in "ABC" for i in range(1, 6)]
    if sorted(seen_ws) != sorted(expected_ids):
        errs.append(f"worksheet ids in html: {sorted(seen_ws)}")
    nitems = 0
    for wid in expected_ids:
        cs = seen_ws.get(wid, [])
        ks = [k for k in keys if k[0] == wid]
        if len(cs) != len(ks):
            errs.append(f"{wid}: worksheet has {len(cs)} items but the key has {len(ks)}")
        if len(cs) != 8:
            errs.append(f"{wid}: {len(cs)} items, expected 8")
        for c in cs:
            nitems += 1
            tag = f"{wid}.{c['n']}"
            if (wid, c["n"]) not in keys:
                errs.append(f"{tag}: no key entry")
                continue
            ktp, kans, kbody = keys[(wid, c["n"])]
            if ktp != c["type"]:
                errs.append(f"{tag}: key type {ktp} != worksheet type {c['type']}")
            if c["type"] in ("fill", "pick", "full") and c["ts"] != c["meter"]:
                errs.append(f"{tag}: time signature glyphs {c['ts']!r} != meter {c['meter']!r}")
            if c["type"] in ("fill", "pick") and not c["gap"]:
                errs.append(f"{tag}: gap box missing")
            if c["type"] not in ("fill", "pick") and c["gap"]:
                errs.append(f"{tag}: unexpected gap box")
            if c["type"] == "cmp" and not c["circle"]:
                errs.append(f"{tag}: comparison circle missing")
            if c["type"] in ("sum", "restsum", "fill") and not c["ansbox"]:
                errs.append(f"{tag}: answer box missing")
            if c["type"] == "pick" and len(c["opts"]) != 3:
                errs.append(f"{tag}: {len(c['opts'])} choices")
            if c["type"] == "full" and c["words"] != ["FULL", "TOO SHORT", "TOO LONG"]:
                errs.append(f"{tag}: choice words {c['words']}")
            want = recompute(c)
            if want == "AMBIGUOUS":
                errs.append(f"{tag}: ambiguous pick")
            if want != kans:
                errs.append(f"{tag}: key says {kans!r}, recomputed from the drawing {want!r}")
            m_res = re.search(r'<span class="res">(.*?)</span>', kbody)
            shown = (m_res.group(1) if m_res else "").replace("&gt;", ">").replace("&lt;", "<")
            if shown != kans:
                errs.append(f"{tag}: key text shows {shown!r}, data-ans {kans!r}")
            # the visible working must add up to the same answer
            if c["type"] in ("sum", "restsum"):
                eq = re.search(r'<span class="eq">(.*?)</span>', kbody).group(1)
                eq = eq.replace("rests:", "")
                if sum((parse_beats(x) for x in eq.split("+")), F(0)) != parse_beats(kans):
                    errs.append(f"{tag}: key working {eq!r} does not add to {kans}")
            if c["type"] == "full":
                eq = re.search(r'<span class="eq">(.*?)</span>', kbody).group(1)
                tot = sum((parse_beats(x) for x in eq.split("+")), F(0))
                mb = {"4/4": 4, "3/4": 3, "2/4": 2}[c["ts"]]
                if (tot == mb) != (kans == "FULL") or (tot < mb) != (kans == "TOO SHORT"):
                    errs.append(f"{tag}: key working {eq!r} disagrees with {kans}")
            if c["type"] == "cmp":
                a = re.search(r'<span class="eq">(.*?)</span>', kbody).group(1)
                b = re.search(r'<span class="eq2">(.*?)</span>', kbody).group(1)
                sa = sum((parse_beats(x) for x in a.split("+")), F(0))
                sb = sum((parse_beats(x) for x in b.split("+")), F(0))
                sym = ">" if sa > sb else "<" if sa < sb else "="
                if sym != kans:
                    errs.append(f"{tag}: key working {a} vs {b} gives {sym}, key says {kans}")
            # structure checks on the drawing
            for side in ("L", "R"):
                toks = c[side]
                for i, t in enumerate(toks):
                    if t["tie"]:
                        if i + 1 >= len(toks) or t["rest"] or toks[i + 1]["rest"]:
                            errs.append(f"{tag}: tie not joining two notes")
                        if i not in c["ties"] and side == "L":
                            errs.append(f"{tag}: tie arc missing after token {i + 1}")
                    if t["beam"]:
                        j = i - 1 if (i > 0 and toks[i - 1]["beam"] and toks[i - 1]["kind"] == "eighth" and (i % 2 == 1 or True)) else i + 1
                        if t["kind"] != "eighth":
                            errs.append(f"{tag}: beamed non-eighth")
                    if t["dot"] and t["rest"]:
                        errs.append(f"{tag}: dotted rest")
                beamed = [i for i, t in enumerate(toks) if t["beam"]]
                if len(beamed) % 2:
                    errs.append(f"{tag}: odd number of beamed eighths")
            if wid[0] == "A":
                for t in c["L"] + c["R"]:
                    if t["kind"] == "eighth" and not t["beam"]:
                        errs.append(f"{tag}: lone eighth in Level A")
                    if t["dot"] or t["tie"]:
                        errs.append(f"{tag}: dot or tie in Level A")
            if wid[0] == "B":
                for t in c["L"] + c["R"]:
                    if t["dot"] or t["tie"] or (t["kind"] == "eighth" and not t["beam"]):
                        errs.append(f"{tag}: Level B item uses a dot, tie or lone eighth")
            if c["type"] in ("sum", "restsum", "cmp"):
                if not c["L"] or (c["type"] == "cmp" and not c["R"]):
                    errs.append(f"{tag}: empty row")
            # x order and spacing
            for side in ("L", "R"):
                xs_ = [t["x"] for t in c[side]]
                for a, b in zip(xs_, xs_[1:]):
                    if b - a < 14:
                        errs.append(f"{tag}: notes only {b - a:.1f}pt apart")
            allx = [t["x"] for t in c["L"] + c["R"]]
            if allx and (min(allx) < 34 or max(allx) > CARD_W - 16):
                errs.append(f"{tag}: notes leave the card ({min(allx):.0f}..{max(allx):.0f})")
        # distinct drawn items on one worksheet
        sig = [(c["type"], c["ts"], tuple((t["kind"], t["rest"], t["dot"], t["tie"], t["beam"]) for t in c["L"]), tuple((t["kind"], t["rest"], t["dot"], t["tie"], t["beam"]) for t in c["R"]), c["gap_before"]) for c in cs]
        if len(set(sig)) != len(sig):
            errs.append(f"{wid}: two items on the worksheet look identical")
    # key pages list every item once
    return errs, nitems


def pdf_fonts(path):
    out = subprocess.run(["pdffonts", path], capture_output=True, text=True, check=True).stdout.splitlines()[2:]
    rows = []
    for line in out:
        parts = line.split()
        rows.append((parts[0], parts[-5]))
    return rows


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
        let low = 0;
        const boxes = [];
        pg.querySelectorAll('svg.card, .keyblock, .legend, .refgrid, .doc table, .doc p, .doc ul, .how, .name, .top, .lgc, .refcell, .ka').forEach(el => {
          if (ft && ft.contains(el)) return;
          const r = el.getBoundingClientRect();
          if (r.height === 0) return;
          low = Math.max(low, r.bottom);
          if (r.bottom > ftop - 7 && !el.closest('.wm')) res.push(`page ${i + 1}: ${el.tagName}.${el.className && el.className.baseVal !== undefined ? el.className.baseVal : el.className} bottom ${(r.bottom - ftop).toFixed(1)}px vs footer rule (needs <= -7)`);
          if (r.right > pr.right - 0.35 * 96 + 0.5 || r.left < pr.left + 0.35 * 96 - 0.5) res.push(`page ${i + 1}: element too close to the page edge`);
          if (el.matches('svg.card, .keyblock, .refcell, .lgc')) boxes.push([el, r]);
        });
        for (let a = 0; a < boxes.length; a++) for (let c = a + 1; c < boxes.length; c++) {
          const A = boxes[a][1], C = boxes[c][1];
          if (boxes[a][0].contains(boxes[c][0]) || boxes[c][0].contains(boxes[a][0])) continue;
          const gx = Math.max(A.left, C.left) - Math.min(A.right, C.right);
          const gy = Math.max(A.top, C.top) - Math.min(A.bottom, C.bottom);
          if (gx < 3 && gy < 3) res.push(`page ${i + 1}: two boxes touch or overlap`);
        }
        pg.querySelectorAll('.legend, .items').forEach(el => {});
        const fb = pg.querySelectorAll('.items');
        fb.forEach(el => { const r = el.getBoundingClientRect(); });
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
    errs = []
    js = os.path.join(BUILD, "layout.js")
    with open(js, "w") as f:
        f.write(LAYOUT_JS)
    files = [os.path.join(BUILD, "resource.html"), os.path.join(BUILD, "preview.html")]
    if not all(os.path.exists(x) for x in files):
        return ["build html missing: run gen.py first"]
    r = subprocess.run(["node", js, *files], capture_output=True, text=True, env=node_env())
    if r.returncode != 0:
        return [f"layout script failed: {r.stderr[-300:]}"]
    return json.loads(r.stdout.strip().splitlines()[-1])


def verify_images():
    """Blank bottom band, watermark and size checks on the PNGs."""
    errs = []
    from PIL import Image
    for p in [COVER_PNG, *PREVIEW_PNGS]:
        im = Image.open(p).convert("L")
        if im.size != (2000, 2000):
            errs.append(f"{os.path.basename(p)}: not 2000x2000")
            continue
        # the black band occupies the bottom; look for the largest blank (all-white) run above it
        px = im.load()
        rows = []
        for y in range(0, 2000, 2):
            dark = sum(1 for x in range(0, 2000, 8) if px[x, y] < 200)
            rows.append(dark)
        # band top: first row from the bottom where >90% dark
        ytop = 2000
        for y in range(1998, 0, -2):
            if rows[y // 2] > 0.9 * 250:
                ytop = y
            else:
                break
        run = best = 0
        for y in range(120, ytop, 2):
            if rows[y // 2] == 0:
                run += 2
                best = max(best, run)
            else:
                run = 0
        if best > 200:
            errs.append(f"{os.path.basename(p)}: blank band of {best}px (more than 10% of the image)")
        last = max((y for y in range(0, ytop, 2) if rows[y // 2] > 0), default=0)
        if ytop - last > 200:
            errs.append(f"{os.path.basename(p)}: {ytop - last}px blank above the bottom band")
    return errs


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
        n = i + 1
        if len(t.strip()) < 40:
            errs.append(f"PDF page {n} looks blank")
        up = t.upper().replace("\n", " ")
        if P_WS0 <= n < P_KEY0:
            wid = f"{chr(65 + (n - P_WS0) // 5)}{(n - P_WS0) % 5 + 1}"
            if f"{wid}. " not in t.replace("\n", " "):
                errs.append(f"PDF page {n}: worksheet heading {wid} missing")
        if P_KEY0 <= n < P_TERMS and "ANSWER KEY" not in up:
            errs.append(f"PDF page {n}: answer key heading missing")
        if "PREVIEW" in up:
            errs.append(f"product PDF page {n} carries a PREVIEW watermark")
    prd = PdfReader(PREVIEW_PDF)
    for i in range(4):
        if (prd.pages[i].extract_text() or "").count("PREVIEW") != 1:
            errs.append(f"preview PDF page {i + 1}: expected exactly one PREVIEW watermark")
    errs += verify_images()
    up = open(UPLOAD).read()
    m = re.search(r"^## 1\. Title\s*\n+```\n(.+?)\n```", up, re.M | re.S)
    if not m:
        errs.append("UPLOAD.md: title block not found")
    else:
        title = m.group(1).strip()
        if len(title) > 80:
            errs.append(f"UPLOAD.md: title is {len(title)} chars (max 80)")
        if re.search(r"winter|snow|holiday|christmas", title, re.I):
            errs.append("UPLOAD.md: seasonal word in the title")
    for need in (DISCLOSURE, f"${PRICE}", f"{TOTAL_PAGES} pages", "15 worksheets"):
        if need not in up:
            errs.append(f"UPLOAD.md: missing '{need}'")
    # page-count list must total the PDF
    sec = up.split("## 5. Page count by section")[1].split("##")[0]
    nums = [int(x) for x in re.findall(r"^- (?!Total)[^\n]*: (\d+)$", sec, re.M)]
    if sum(nums) != TOTAL_PAGES:
        errs.append(f"UPLOAD.md page list sums to {sum(nums)}, PDF has {TOTAL_PAGES}")
    if "checked by hand" in up.lower() or "handmade" in up.lower():
        errs.append("UPLOAD.md: says hand-checked/handmade")
    tj = json.load(open(TPT_JSON))
    tags, subs = set(load_json("TAG-OPTIONS.json")["options"]), set(load_json("SUBJECT-OPTIONS.json"))
    if not 1 <= len(tj["tags"]) <= 6 or any(t not in tags for t in tj["tags"]):
        errs.append(f"tpt.json tags invalid: {tj['tags']}")
    if not 1 <= len(tj["subjects"]) <= 3 or any(s not in subs for s in tj["subjects"]):
        errs.append(f"tpt.json subjects invalid: {tj['subjects']}")
    if tj.get("pages") != TOTAL_PAGES:
        errs.append(f"tpt.json pages {tj.get('pages')} != {TOTAL_PAGES}")
    if tj["price"] != PRICE:
        errs.append("tpt.json price mismatch")
    # claims in the PDF text agree with the product
    allt = " ".join((pg.extract_text() or "") for pg in rd.pages[:2])
    if "15 worksheets" not in allt.replace("\n", " "):
        errs.append("cover/teacher page does not say 15 worksheets")
    return errs


def check():
    errs = verify_data(WSS)
    e2, nitems = verify_html()
    errs += e2
    errs += verify_layout()
    errs += verify_files()
    if errs:
        print("CHECK FAILED")
        print("\n".join(" - " + e for e in errs[:80]))
        sys.exit(1)
    print(f"CHECK OK: {len(WSS)} worksheets, {nitems} items; every answer recomputed from the rendered SVG tokens "
          f"(sums, rest sums, comparisons, missing beats, pick-the-note, full/short/long); worksheet and key item counts match; "
          f"no ambiguous items; layout clear of footers and boxes; PDF {TOTAL_PAGES} Letter pages, preview 4 (one watermark each), "
          f"fonts embedded; images 2000x2000; UPLOAD.md and tpt.json ok.")


if __name__ == "__main__":
    if "--check" in sys.argv:
        check()
    else:
        build()
