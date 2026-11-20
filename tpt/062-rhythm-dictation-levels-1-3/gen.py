#!/usr/bin/env python3
"""Rhythm Dictation, Levels 1-3 (TpT 062): build the resource and verify it.

    python3 gen.py           build everything (PDFs, PNGs, UPLOAD.md, tpt.json) into this folder
    python3 gen.py --check   re-read every staff from the rendered HTML and verify the exercises, layout and images

30 exercises in 3 levels. Each exercise has a teacher script (meter, tempo, count-in, plays, the syllables and counts to perform),
a student page (blank bars with the barlines and time signature printed) and an answer key (notation, syllables, counts).
Exercises are stored as bars of syllable tokens. `--check` does not trust that data: it parses the rendered SVG of every key staff
(one line, neutral clef, time signature glyphs, noteheads, stems, flags, beams, dots, rests, barlines), derives every note value from
the glyph, the flags or beams and the dot, adds up each bar against the time signature, recomputes the rhythm syllables and the counts
from the notation with its own rules, and compares them with the printed script and the printed key. It then checks that the student
page has the same time signature and number of bars, that each level uses only its own values, that no two exercises are alike, and that
counts and page references agree across the pages, the previews and UPLOAD.md.
"""
import json
import math
import os
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from fractions import Fraction
from html import escape

HERE = os.path.dirname(os.path.abspath(__file__))
TPT = os.path.dirname(HERE)
FONTS = os.path.join(TPT, "fonts")
BUILD = os.path.join(HERE, "build")
RENDER_JS = os.path.join(TPT, "tools", "render.js")
HERO = os.path.join(HERE, "art", "hero.png")
SPOT = os.path.join(HERE, "art", "spot-metronome.png")

SLUG = "rhythm-dictation-levels-1-3"
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
TITLE = "Rhythm Dictation"
LISTING_TITLE = "Rhythm Dictation Levels 1-3: 30 Exercises, Teacher Scripts & Keys, Grades 3-8"
PRICE = "4.00"
TAGS = ["Worksheets", "Printables", "Activities", "Assessment", "Bell Ringers"]
SUBJECTS = ["Music", "Instrumental Music"]
GRADES = ["4th-grade", "5th-grade", "6th-grade", "7th-grade"]
LEVEL_GRADES = {1: "3–4", 2: "4–6", 3: "6–8"}

# ------------------------------------------------------------------ rhythm vocabulary
# Durations are in quarter-note beats. A token is one rhythm word (one or two beats of a simple meter, one big beat of 6/8).
H = Fraction(1, 2)
Q = Fraction(1, 4)
TOK_SIMPLE = {
    "ta": [("n", Fraction(1))],
    "shh": [("r", Fraction(1))],
    "ti-ti": [("n", H), ("n", H)],
    "ta-a": [("n", Fraction(2))],
    "ta-a-a": [("n", Fraction(3))],
    "ta-a-a-a": [("n", Fraction(4))],
    "ti-ka-ti-ka": [("n", Q)] * 4,
    "ti-ti-ka": [("n", H), ("n", Q), ("n", Q)],
    "ti-ka-ti": [("n", Q), ("n", Q), ("n", H)],
    "ti-ta-ti": [("n", H), ("n", Fraction(1)), ("n", H)],
    "tam-ti": [("n", Fraction(3, 2)), ("n", H)],
}
TOK_COMP = {
    "ta": [("n", Fraction(3, 2))],
    "ti-ti-ti": [("n", H)] * 3,
    "ta-ti": [("n", Fraction(1)), ("n", H)],
    "ti-ta": [("n", H), ("n", Fraction(1))],
}
METERS = {
    "4/4": {"top": 4, "bot": 4, "barlen": Fraction(4), "win": Fraction(1), "comp": False},
    "3/4": {"top": 3, "bot": 4, "barlen": Fraction(3), "win": Fraction(1), "comp": False},
    "6/8": {"top": 6, "bot": 8, "barlen": Fraction(3), "win": Fraction(3, 2), "comp": True},
}
TS_GLYPH = {3: 0xE083, 4: 0xE084, 6: 0xE086, 8: 0xE088}
TS_DIGIT = {v: k for k, v in TS_GLYPH.items()}

L1_VALUES = {"ta", "shh", "ti-ti", "ta-a"}
L2_NEW = {"ta-a-a", "ta-a-a-a", "ti-ta-ti"}
L3_NEW_SIMPLE = {"ti-ka-ti-ka", "ti-ti-ka", "ti-ka-ti", "tam-ti"}
SIXTEENTH = {"ti-ka-ti-ka", "ti-ti-ka", "ti-ka-ti"}
ALLOWED = {1: L1_VALUES, 2: L1_VALUES | L2_NEW, 3: L1_VALUES | L2_NEW | L3_NEW_SIMPLE}
COMP_ALLOWED = set(TOK_COMP)
LEVEL_METERS = {1: {"4/4"}, 2: {"4/4", "3/4"}, 3: {"4/4", "3/4", "6/8"}}
LEVEL_BARS = {1: (2, 2), 2: (2, 4), 3: (4, 4)}

# (level, meter, BPM, bars). "|" separates bars. In 6/8 the BPM is the dotted-quarter pulse.
EX_SRC = [
    (1, "4/4", 60, "ta ta ta ta | ta ta ta-a"),
    (1, "4/4", 60, "ta ti-ti ta ta | ta ta ta shh"),
    (1, "4/4", 66, "ti-ti ta ti-ti ta | ta-a ta ta"),
    (1, "4/4", 66, "ta-a ta ta | ta ti-ti ta shh"),
    (1, "4/4", 66, "ta shh ta ta | ti-ti ti-ti ta ta"),
    (1, "4/4", 72, "ti-ti ta shh ta | ta ta ti-ti ti-ti"),
    (1, "4/4", 72, "ta-a ta-a | ta ti-ti ta-a"),
    (1, "4/4", 72, "ta ta shh ta | ti-ti ti-ti ti-ti ta"),
    (1, "4/4", 76, "ta-a ti-ti ta | ti-ti ta shh ta"),
    (1, "4/4", 76, "ta ti-ti ti-ti ta | ta-a ta shh"),
    (2, "4/4", 66, "ta ta ta-a | ta-a-a-a"),
    (2, "4/4", 66, "ta-a-a ta | ta ti-ti ta-a"),
    (2, "3/4", 72, "ta ta ta | ta-a-a"),
    (2, "3/4", 72, "ta ti-ti ta | ta-a ta | ta-a-a"),
    (2, "4/4", 72, "ta ti-ta-ti ta | ta-a ta shh | ta-a-a-a"),
    (2, "4/4", 76, "ti-ta-ti ta ta | ta ti-ti ti-ta-ti"),
    (2, "3/4", 76, "ta ta shh | ta-a ta | ti-ti ta ta | ta-a-a"),
    (2, "4/4", 80, "ta ta ta-a | ti-ta-ti ta ta | ta-a-a ta | ta ti-ti ta shh"),
    (2, "3/4", 72, "ta ti-ta-ti | ti-ta-ti ta | ta-a-a"),
    (2, "4/4", 84, "ti-ta-ti ti-ta-ti | ta shh ta-a | ta-a-a ta | ta-a-a-a"),
    (3, "4/4", 72, "ti-ka-ti-ka ta ta ta | ta ti-ti ta shh | ti-ti-ka ta ta ta | ta-a ta ta"),
    (3, "4/4", 76, "ta ti-ka-ti ta ta | ti-ka-ti-ka ti-ti ta-a | ta ta ti-ti-ka ta | ta-a-a ta"),
    (3, "4/4", 72, "tam-ti ta ta | ta ta tam-ti | ti-ka-ti ti-ka-ti ta shh | tam-ti tam-ti"),
    (3, "4/4", 80, "ta tam-ti ta | ti-ti-ka ti-ka-ti ta-a | ta-a tam-ti | ti-ka-ti-ka ti-ti ta shh"),
    (3, "3/4", 84, "ti-ka-ti-ka ta ta | ta tam-ti | ta-a ti-ka-ti | ti-ti-ka ta-a"),
    (3, "3/4", 88, "tam-ti ta | ti-ka-ti ti-ti ta | ta ti-ti-ka ta | ta-a-a"),
    (3, "6/8", 60, "ta ti-ti-ti | ta ta | ti-ti-ti ti-ti-ti | ta ta"),
    (3, "6/8", 60, "ta-ti ta | ti-ti-ti ta-ti | ta ti-ti-ti | ta-ti ta"),
    (3, "6/8", 66, "ti-ti-ti ta-ti | ta ta-ti | ti-ta ti-ti-ti | ta ta"),
    (3, "6/8", 72, "ta-ti ti-ta | ti-ti-ti ta | ta-ti ta-ti | ta ti-ti-ti"),
]


def tokens_of(meter):
    return TOK_COMP if METERS[meter]["comp"] else TOK_SIMPLE


def expand(tokens, meter):
    """Events of one bar from its tokens: [{kind, dur, t, tok}], the token spans, and the bar length."""
    tk = tokens_of(meter)
    ev, spans, t = [], [], Fraction(0)
    for ti, name in enumerate(tokens):
        first = len(ev)
        for kind, dur in tk[name]:
            ev.append({"kind": kind, "dur": dur, "t": t, "tok": ti})
            t += dur
        spans.append((first, len(ev) - 1))
    return ev, spans, t


def make_exercises():
    exs = []
    for i, (lvl, meter, bpm, src) in enumerate(EX_SRC):
        bars = [b.split() for b in src.split("|")]
        for b in bars:
            ev, _sp, tot = expand(b, meter)
            assert tot == METERS[meter]["barlen"], (i + 1, b, tot)
            assert all(n in (TOK_COMP if METERS[meter]["comp"] else TOK_SIMPLE) for n in b)
            if not METERS[meter]["comp"]:
                for e in ev:
                    if e["kind"] == "n" and e["dur"] == 2:
                        assert e["t"] in ((0, 2) if meter == "4/4" else (0, 1)), (i + 1, "half note off its beat", b)
                    if e["kind"] == "n" and e["dur"] in (3, 4):
                        assert e["t"] == 0, (i + 1, "long note not on beat 1", b)
        assert meter in LEVEL_METERS[lvl], (i + 1, meter)
        lo, hi = LEVEL_BARS[lvl]
        assert lo <= len(bars) <= hi, (i + 1, len(bars))
        names = {n for b in bars for n in b}
        if METERS[meter]["comp"]:
            assert lvl == 3 and names <= COMP_ALLOWED
        else:
            assert names <= ALLOWED[lvl], (i + 1, names - ALLOWED[lvl])
        plays = 3 if len(bars) <= 2 else 4
        exs.append({"num": i + 1, "level": lvl, "meter": meter, "bpm": bpm, "bars": bars, "plays": plays, "secs": 30 * len(bars),
                    "src": src})
    return exs


EXS = make_exercises()
assert len(EXS) == 30 and [sum(1 for e in EXS if e["level"] == k) for k in (1, 2, 3)] == [10, 10, 10]
for _k in (1, 2, 3):
    _seen = set()
    for _e in EXS:
        if _e["level"] == _k:
            _key = (_e["meter"], tuple(tuple(b) for b in _e["bars"]))
            assert _key not in _seen, "duplicate exercise in a level"
            _seen.add(_key)
assert len({(e["meter"], tuple(tuple(b) for b in e["bars"])) for e in EXS}) == 30
for _e in EXS:
    _names = {n for b in _e["bars"] for n in b}
    if _e["level"] == 2:
        assert _names & L2_NEW, ("level 2 exercise without a new value", _e["num"])
    if _e["level"] == 3:
        assert METERS[_e["meter"]]["comp"] or _names & L3_NEW_SIMPLE, ("level 3 exercise without a new value", _e["num"])
LEVEL_EXS = {k: [e for e in EXS if e["level"] == k] for k in (1, 2, 3)}
LEVEL_BARS_TOTAL = {k: sum(len(e["bars"]) for e in LEVEL_EXS[k]) for k in (1, 2, 3)}
LEVEL_POINTS = {k: 2 * v for k, v in LEVEL_BARS_TOTAL.items()}
TOTAL_POINTS = sum(LEVEL_POINTS.values())


def bpm_text(e):
    if e["meter"] == "6/8":
        return f'{e["bpm"]} BPM (dotted quarter note = {e["bpm"]})'
    return f'{e["bpm"]} BPM (quarter note = {e["bpm"]})'


def count_in(meter):
    return {"4/4": "1 2 3 4", "3/4": "1 2 3", "6/8": "1 2 1 2"}[meter]


def count_in_note(meter):
    return {"4/4": "one bar of four beats", "3/4": "one bar of three beats", "6/8": "four dotted-quarter pulses, two bars"}[meter]


def features(e):
    names = {n for b in e["bars"] for n in b}
    out = []
    comp = METERS[e["meter"]]["comp"]
    if comp:
        out.append("6/8 in groups of three eighths")
        if "ta-ti" in names or "ti-ta" in names:
            out.append("quarter and eighth together")
        return out
    if "shh" in names:
        out.append("quarter rests")
    if "ta-a" in names:
        out.append("half notes")
    if "ta-a-a" in names:
        out.append("dotted half notes")
    if "ta-a-a-a" in names:
        out.append("a whole note")
    if "ti-ta-ti" in names:
        out.append("syncopation (eighth, quarter, eighth)")
    if names & SIXTEENTH:
        out.append("sixteenth notes")
    if "tam-ti" in names:
        out.append("dotted quarter and eighth")
    if not out:
        out.append("quarter notes and eighth pairs")
    return out[:3]


# ------------------------------------------------------------------ counting (one rule set, used for the printed counts)
def counts_of_bar(evs, meter, span=None):
    """Count tokens for one bar from its events: [(time, text, is_onset)]. Held beats show a dash, rests show the beat number in
    parentheses. In 6/8 every eighth gets a count (1 la li 2 la li). `span` limits the count to the first span beats (chart rows)."""
    at = {e["t"]: e for e in evs}
    out = []
    span = METERS[meter]["barlen"] if span is None else Fraction(span)
    if METERS[meter]["comp"]:
        lab = ["1", "la", "li", "2", "la", "li"]
        for j in range(int(span * 2)):
            t = Fraction(j, 2)
            out.append((t, lab[j] if t in at else "–", t in at))
        return out
    for b in range(math.ceil(span)):
        tb = Fraction(b)
        e = at.get(tb)
        out.append((tb, (f"({b + 1})" if e["kind"] == "r" else str(b + 1)) if e else "–", e is not None))
        for fr, sym in ((Fraction(1, 4), "e"), (Fraction(1, 2), "+"), (Fraction(3, 4), "a")):
            if tb + fr in at:
                out.append((tb + fr, sym, True))
    return out


def count_text(evs, meter, span=None):
    return " ".join(t for _, t, _ in counts_of_bar(evs, meter, span))


# ------------------------------------------------------------------ drawing
HEAD_W = 1.18
WHOLE_W = 1.688
REST_W = 1.08
G_WHOLE, G_HALF, G_HEAD, G_QREST, G_NEUTRAL, G_FLAG8 = 0xE0A2, 0xE0A3, 0xE0A4, 0xE4E5, 0xE069, 0xE240
STEM_X = 0.168
STEM_LEN = 3.5
CLEF_W, TS_W = 1.528, 1.9
SUBF = 0.8
LEAD, TAIL = 2.1, 0.7           # staff spaces: barline to first onset, and last window end back to the barline


def fx(v):
    return f"{v:.2f}"


def gl(cp, x, y, size, cls="", fill="#000"):
    c = f' class="{cls}"' if cls else ""
    return f'<text{c} x="{fx(x)}" y="{fx(y)}" font-family="Bravura" font-size="{fx(size)}" fill="{fill}">&#x{cp:X};</text>'


def beam_groups(evs, meter):
    L = METERS[meter]["win"]
    groups, cur = [], []
    for i, e in enumerate(evs):
        sub = e["kind"] == "n" and e["dur"] < 1
        if sub and cur and cur[-1] == i - 1 and evs[cur[-1]]["t"] // L == e["t"] // L:
            cur.append(i)
            continue
        if cur:
            groups.append(cur)
        cur = [i] if sub else []
    if cur:
        groups.append(cur)
    return groups


def win_units(bar_events, meter):
    """Natural width (staff spaces) of every beat window of a bar, from what starts inside it."""
    M = METERS[meter]
    L = M["win"]
    n = int(M["barlen"] / L)
    groups = beam_groups(bar_events, meter)
    beamed = {i for g in groups if len(g) >= 2 for i in g}
    out = []
    for i in range(n):
        st = L * i
        ons = [e["t"] - st for e in bar_events if st <= e["t"] < st + L]
        if M["comp"]:
            u = 7.2 if len(ons) >= 2 else 5.4
        else:
            u = 7.2 if any(o in (Q, 3 * Q) for o in ons) else 5.0 if H in ons else 3.6
        # a flagged eighth needs room before the next note in its window, so the flag does not touch it
        for j, e in enumerate(bar_events):
            if e["kind"] == "n" and e["dur"] < 1 and j not in beamed and st <= e["t"] < st + L and j + 1 < len(bar_events):
                nx = bar_events[j + 1]
                if nx["t"] < st + L:
                    u = max(u, 2.5 / (SUBF * float((nx["t"] - e["t"]) / L)))
            if e["kind"] == "n" and e["dur"] < 1 and j not in beamed and j == len(bar_events) - 1 and st <= e["t"] < st + L:
                u = max(u, 3.6 / (1 - SUBF * float((e["t"] - st) / L)))
        out.append((st, L, u))
    return out


def ink_extent(e, S, flagged):
    """(left, right) of the ink of one event around its x, in points."""
    hw, sw = HEAD_W * S, 0.13 * S
    if e["kind"] == "r":
        return e["x"] - REST_W * S / 2, e["x"] + REST_W * S / 2
    if e["dur"] >= 4:
        return e["x"] - WHOLE_W * S / 2, e["x"] + WHOLE_W * S / 2
    r = e["x"] + hw / 2
    if e["dur"] in (3, Fraction(3, 2)):
        r = max(r, e["x"] + hw / 2 + 0.55 * S + 0.2 * S)
    if flagged:
        r = max(r, e["x"] + hw / 2 - sw + 1.056 * S)
    return e["x"] - hw / 2, r


def layout_key(bar_evs, units, meter, S, k, first_x):
    """Window lists per bar and the barline x after every bar. Each barline sits midway between the last note of its bar and the first note of
    the next one (or the end of the line), pushed right when a flag or dot needs the room."""
    wl_all, acc = [], first_x
    for bi, evs in enumerate(bar_evs):
        wl = []
        for st, L, u in units[bi]:
            wl.append((st, L, acc, u * S * k))
            acc += u * S * k
        for e in evs:
            for st, L, xl, wd in wl:
                if st <= e["t"] < st + L:
                    e["x"] = xl + SUBF * float((e["t"] - st) / L) * wd
        wl_all.append(wl)
    barlines = []
    for bi, evs in enumerate(bar_evs):
        beamed = {i for g in beam_groups(evs, meter) if len(g) >= 2 for i in g}
        li = len(evs) - 1
        _l, R = ink_extent(evs[li], S, evs[li]["dur"] < 1 and li not in beamed)
        if bi + 1 < len(bar_evs):
            nx = bar_evs[bi + 1][0]
            nxl, _r = ink_extent(nx, S, False)
            nxx = nx["x"]
        else:
            nxx, nxl = acc, acc - HEAD_W * S / 2
        win = METERS[meter]["win"]
        unit = Fraction(1, 2) if METERS[meter]["comp"] else Fraction(1)
        tl = METERS[meter]["barlen"] - unit
        wl = wl_all[bi]
        last_lab = max(evs[li]["x"], next(xl + SUBF * float((tl - st) / L) * wd for st, L, xl, wd in wl if st <= tl < st + L))
        b = max((last_lab + nxx) / 2, R + 0.45 * S, last_lab + 1.4 * S)
        if b > nxl - 0.45 * S + 1e-6:
            raise ValueError(f"bar {bi + 1}: no room for the barline")
        barlines.append(b)
    return wl_all, barlines


def staff_svg(meter, bars, S, W, kind, uid, labels=False, nblank=0, nbeats=None):
    """kind: key (clef, time signature, bars with notes), blank (same, empty bars), sym (just the notes of one bar on the line)."""
    M = METERS[meter]
    hw = HEAD_W * S
    y0 = (4.3 if kind == "sym" else 4.9) * S
    sw = 0.13 * S
    withbar = kind in ("key", "blank")
    n = nblank if kind == "blank" else len(bars)
    bar_evs = [expand(b, meter)[0] for b in bars] if bars else []
    xclef = 6.0
    xts = xclef + CLEF_W * S + 0.9 * S
    ts_right = xts + TS_W * S
    left0 = ts_right + 0.7 * S if withbar else 2.0
    units = [win_units(ev, meter) for ev in bar_evs]
    wl_all = []
    if kind == "sym":
        acc = left0 + LEAD * S
        wl = []
        for st, L, u in units[0]:
            wl.append((st, L, acc, u * S))
            acc += u * S
        wl_all = [wl]
        W = acc - 0.9 * S + 4.0
    x_thin = W - 3.0 - 0.18 * S - 0.5 * S
    barlines = []
    if kind == "key":
        first_x = left0 + LEAD * S
        try:
            def fin_bar(kk):
                return layout_key(bar_evs, units, meter, S, kk, first_x)[1][-1] - x_thin
            if fin_bar(1.0) > 0:
                raise ValueError(f"{uid}: staff too narrow at S={S}")
        except ValueError as err:
            raise ValueError(f"{uid}: {err}")
        lo, hi = 1.0, 2.0
        while fin_bar(hi) < 0:
            hi *= 2
        for _ in range(60):
            mid = (lo + hi) / 2
            if fin_bar(mid) < 0:
                lo = mid
            else:
                hi = mid
        wl_all, barlines = layout_key(bar_evs, units, meter, S, hi, first_x)
    H_ = y0 + (6.6 * S if labels else 2.6 * S if withbar else 1.9 * S)
    o = [f'<svg class="ns" data-kind="{kind}" data-id="{uid}" data-meter="{meter}" data-s="{fx(S)}" data-y0="{fx(y0)}" '
         f'xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.2f} {H_:.2f}" width="{W:.2f}pt" height="{H_:.2f}pt" style="display:block">']
    o.append(f'<line class="sl" x1="2" y1="{fx(y0)}" x2="{fx(W - 2)}" y2="{fx(y0)}" stroke="#000" stroke-width="{fx(sw)}"/>')
    if withbar:
        o.append(gl(G_NEUTRAL, xclef, y0, 4 * S, "clef"))
        o.append(gl(TS_GLYPH[M["top"]], xts, y0 - 1.25 * S, 4 * S, "tsd"))
        o.append(gl(TS_GLYPH[M["bot"]], xts, y0 + 1.25 * S, 4 * S, "tsd"))
        if kind == "blank":
            step = (x_thin - left0) / n
            barlines = [left0 + step * (i + 1) for i in range(n - 1)] + [x_thin]
        else:
            assert abs(barlines[-1] - x_thin) < 0.05, (barlines[-1], x_thin)
        for bx in barlines:
            o.append(f'<line class="bar" x1="{fx(bx)}" y1="{fx(y0 - 2 * S)}" x2="{fx(bx)}" y2="{fx(y0 + 2 * S)}" stroke="#000" stroke-width="{fx(0.14 * S)}"/>')
        bxf = W - 3.0 - 0.18 * S
        o.append(f'<rect class="fin" x="{fx(bxf - 0.18 * S)}" y="{fx(y0 - 2 * S)}" width="{fx(0.36 * S)}" height="{fx(4 * S)}" fill="#000"/>')
    tip = y0 - STEM_X * S - STEM_LEN * S
    lab_cnt, lab_syl = [], []
    for bi, evs in enumerate(bar_evs):
        wl = wl_all[bi]

        def X(t, wl=wl):
            for st, L, xl, wd in wl:
                if st <= t < st + L:
                    return xl + SUBF * float((t - st) / L) * wd
            raise ValueError(t)
        groups = beam_groups(evs, meter)
        in_beam = {i for g in groups if len(g) >= 2 for i in g}
        stem_x = {}
        for i, e in enumerate(evs):
            xc = X(e["t"])
            e["x"] = xc
            if e["kind"] == "r":
                o.append(f'<g class="ev">{gl(G_QREST, xc - REST_W * S / 2, y0, 4 * S, "rest")}</g>')
                continue
            if e["dur"] >= 4:
                o.append(f'<g class="ev">{gl(G_WHOLE, xc - WHOLE_W * S / 2, y0, 4 * S, "head")}</g>')
                continue
            glyph = G_HALF if e["dur"] in (2, 3) else G_HEAD
            left = xc - hw / 2
            sx = left + hw - sw / 2
            stem_x[i] = sx
            parts = [gl(glyph, left, y0, 4 * S, "head"),
                     f'<line class="stem" x1="{fx(sx)}" y1="{fx(y0 - STEM_X * S)}" x2="{fx(sx)}" y2="{fx(tip)}" stroke="#000" stroke-width="{fx(sw)}"/>']
            if e["dur"] in (3, Fraction(3, 2)):
                parts.append(f'<circle class="dot" cx="{fx(xc + hw / 2 + 0.55 * S)}" cy="{fx(y0 - 0.5 * S)}" r="{fx(0.2 * S)}" fill="#000"/>')
            if e["dur"] < 1 and i not in in_beam:
                parts.append(gl(G_FLAG8, sx - sw / 2, tip, 4 * S, "flag"))
            o.append(f'<g class="ev">{"".join(parts)}</g>')
        for g in groups:
            if len(g) < 2:
                continue
            x1, x2 = stem_x[g[0]] - sw / 2, stem_x[g[-1]] + sw / 2
            o.append(f'<rect class="beam" data-lvl="1" x="{fx(x1)}" y="{fx(tip)}" width="{fx(x2 - x1)}" height="{fx(0.5 * S)}" fill="#000"/>')
            run = []
            for i in g + [None]:
                if i is not None and evs[i]["dur"] == Q:
                    run.append(i)
                    continue
                if len(run) >= 2:
                    a, b = stem_x[run[0]] - sw / 2, stem_x[run[-1]] + sw / 2
                    o.append(f'<rect class="beam" data-lvl="2" x="{fx(a)}" y="{fx(tip + 0.75 * S)}" width="{fx(b - a)}" height="{fx(0.5 * S)}" fill="#000"/>')
                run = []
        if labels:
            cfs = max(7.0, 0.95 * S)
            sfs = max(7.2, 1.0 * S)
            for t, txt, onset in counts_of_bar(evs, meter):
                lab_cnt.append(f'<text class="cnt" data-bar="{bi + 1}" x="{fx(X(t))}" y="{fx(y0 + 3.55 * S)}" text-anchor="middle" font-family="Source Sans 3, sans-serif" '
                               f'font-weight="600" font-size="{fx(cfs)}" fill="#555">{txt}</text>')
            _e, spans, _t = expand(bars[bi], meter)
            for ti, name in enumerate(bars[bi]):
                a, b = spans[ti]
                cx = (evs[a]["x"] + evs[b]["x"]) / 2
                lab_syl.append(f'<text class="syl" data-bar="{bi + 1}" x="{fx(cx)}" y="{fx(y0 + 5.75 * S)}" text-anchor="middle" font-family="Source Sans 3, sans-serif" '
                               f'font-weight="700" font-size="{fx(sfs)}">{name}</text>')
    o.extend(lab_cnt)
    o.extend(lab_syl)
    o.append("</svg>")
    return "".join(o)


def key_svg(e, S, W=520.0):
    return staff_svg(e["meter"], e["bars"], S, W, "key", f'K{e["num"]:02d}', labels=True)


def blank_svg(e, W=520.0, S=7.5):
    return staff_svg(e["meter"], None, S, W, "blank", f'B{e["num"]:02d}', nblank=len(e["bars"]))


def sym_svg(tokens, meter, uid, S=6.2):
    return staff_svg(meter, [tokens], S, 0, "sym", uid)


def icon_svg(name):
    sw = 1.8
    st = f'stroke="#000" stroke-width="{sw}" stroke-linejoin="round" stroke-linecap="round"'
    if name == "listen":
        body = (f'<polygon points="6,16 11,16 17,10 17,30 11,24 6,24" fill="{TINT}" {st}/>'
                f'<polyline points="22,15 25,20 22,25" fill="none" {st}/><polyline points="27,11 32,20 27,29" fill="none" {st}/>')
    elif name == "echo":
        body = (f'<rect x="4" y="6" width="19" height="13" rx="3" fill="{TINT}" {st}/><polygon points="8,19 8,25 14,19" fill="{TINT}" {st}/>'
                f'<rect x="17" y="21" width="19" height="12" rx="3" fill="#fff" {st}/><polygon points="32,33 32,37 27,33" fill="#fff" {st}/>')
    elif name == "audiate":
        body = (f'<circle cx="21" cy="14" r="10" fill="{TINT}" {st}/><circle cx="9" cy="29" r="3" fill="#fff" {st}/><circle cx="5.5" cy="35" r="1.8" fill="#fff" {st}/>'
                f'<circle cx="18" cy="17" r="2.6" fill="#000" stroke="#000" stroke-width="1"/><line x1="20.6" y1="17" x2="20.6" y2="8" {st}/>')
    elif name == "write":
        body = (f'<polygon points="28,5 35,12 15,32 7,33 8,25" fill="{TINT}" {st}/><line x1="24" y1="9" x2="31" y2="16" {st}/>'
                f'<line x1="8" y1="25" x2="15" y2="32" {st}/>')
    else:
        body = f'<circle cx="20" cy="20" r="14" fill="{TINT}" {st}/><polyline points="12,20 18,27 29,13" fill="none" {st}/>'
    return (f'<svg class="ic" data-name="{name}" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 40" width="34pt" height="34pt" '
            f'style="display:block">{body}</svg>')


STEP_NAMES = ["Listen", "Echo", "Audiate", "Write", "Check"]
STEP_ICONS = ["listen", "echo", "audiate", "write", "check"]


# ------------------------------------------------------------------ staff sizes per level
SVG_W = 508.0


def level_S(level):
    S = {1: 7.0, 2: 6.6, 3: 6.0}[level]
    while S >= 5.0:
        try:
            for e in LEVEL_EXS[level]:
                key_svg(e, S, SVG_W)
            return S
        except ValueError:
            S = round(S - 0.2, 2)
    raise SystemExit(f"level {level}: staves do not fit the page")


LEVEL_S = {k: level_S(k) for k in (1, 2, 3)}


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
.top { display: flex; justify-content: space-between; align-items: flex-end; border-bottom: 2.2pt solid #000; padding-bottom: 6pt; }
.top .t { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; letter-spacing: .01em; line-height: 1; font-size: 19pt; white-space: nowrap; }
.top .t small { display: block; font-family: 'Oswald'; font-weight: 300; text-transform: none; font-size: 11pt; letter-spacing: 0; margin-top: 3pt; }
.top .tag { flex: none; white-space: nowrap; text-align: right; }
.tag .lv { display: inline-block; background: #000; color: #fff; font-family: 'Oswald'; font-weight: 700; font-size: 15pt; padding: 3pt 9pt 4pt; border-radius: 4pt; letter-spacing: .04em; }
.tag .lv.ak { background: ACCENT; }
.tag .ln { font-family: 'Oswald'; font-weight: 300; font-size: 11pt; margin-top: 3pt; }
.foot { display: flex; justify-content: space-between; font-size: 8.5pt; color: #333; border-top: .8pt solid #000; padding-top: 3pt; }
.wm { position: absolute; left: 50%; top: 50%; transform: translate(-50%, -50%) rotate(-38deg); font-family: 'Oswald'; font-weight: 700;
      font-size: 150pt; color: rgba(0,0,0,.13); letter-spacing: .06em; white-space: nowrap; pointer-events: none; z-index: 9; }
.doc h1 { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 30pt; margin: 0 0 4pt; line-height: 1; }
.doc h2 { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 14pt; margin: 9pt 0 3pt; letter-spacing: .02em; }
.doc p, .doc li { font-size: 10.6pt; line-height: 1.34; margin: 0 0 5pt; }
.doc ul { margin: 0 0 4pt; padding-left: 16pt; }
.doc .rule { border-bottom: 2.2pt solid #000; margin-bottom: 8pt; padding-bottom: 6pt; }
.doc table { border-collapse: collapse; width: 100%; table-layout: fixed; font-size: 10pt; margin: 2pt 0 4pt; }
.doc td, .doc th { border: 1pt solid #000; padding: 3pt 6pt; text-align: left; vertical-align: middle; }
.doc th { font-family: 'Oswald'; font-weight: 500; text-transform: uppercase; font-size: 9.5pt; background: #000; color: #fff; }
.small { font-size: 9pt !important; color: #333; }
.box { border: 1.3pt solid #000; border-radius: 7pt; padding: 7pt 10pt 4pt; margin: 6pt 0; }
.box h3 { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 12.5pt; margin: 0 0 3pt; letter-spacing: .02em; }
.box p { margin: 0 0 4pt !important; font-size: 10.4pt !important; }
.cols { display: flex; gap: 12pt; }
.cols .box { flex: 1; margin: 6pt 0; }
.steps { display: flex; flex-direction: column; gap: 6.5pt; margin: 4pt 0 2pt; }
.step { display: flex; gap: 10pt; align-items: center; border: 1.3pt solid #000; border-radius: 7pt; padding: 4pt 10pt 2pt 10pt; }
.step .ic { flex: none; }
.step .n { flex: none; background: ACCENT; color: #fff; font-family: 'Oswald'; font-weight: 700; font-size: 13pt; border-radius: 50%; width: 22pt; height: 22pt; line-height: 22pt; text-align: center; }
.step p { margin: 0 0 3pt !important; font-size: 10.6pt !important; line-height: 1.3 !important; }
.nd { display: flex; align-items: flex-end; gap: 6pt; font-size: 10pt; margin: 7pt 0 0; }
.nd .ln { flex: 1; border-bottom: 1pt solid #000; height: 11pt; }
.stack { flex: 1; display: flex; flex-direction: column; justify-content: space-between; gap: 8pt; padding: 8pt 0 10pt; }
.sc, .sp, .kb { border: 1.3pt solid #000; border-radius: 7pt; padding: 5pt 10pt 5pt; }
.sch { display: flex; align-items: center; gap: 8pt; }
.en { background: #000; color: #fff; font-family: 'Oswald'; font-weight: 700; font-size: 12.5pt; padding: 2pt 8pt 3pt; border-radius: 4pt; white-space: nowrap; letter-spacing: .02em; }
.mt { font-family: 'Oswald'; font-weight: 700; font-size: 14pt; white-space: nowrap; }
.meta { font-size: 9.6pt; line-height: 1.2; }
.meta b { font-weight: 700; }
.sch .sp1 { flex: 1; }
.focus { font-size: 9pt; color: #333; text-align: right; }
.scbars { display: grid; grid-template-columns: 1fr 1fr; gap: 3pt 12pt; margin: 5pt 0 4pt; }
.bc { border-left: 2.4pt solid ACCENT; padding-left: 6pt; display: flex; gap: 7pt; align-items: flex-start; }
.bc .bl { font-family: 'Oswald'; font-weight: 500; font-size: 8pt; letter-spacing: .1em; text-transform: uppercase; color: #555; flex: none; width: 27pt; margin-top: 3.5pt; line-height: 1.1; }
.bc .sylbar { font-family: 'Oswald'; font-weight: 700; font-size: 12.5pt; display: block; line-height: 1.15; word-spacing: 2pt; }
.bc .cntbar { font-weight: 600; font-size: 9.2pt; color: #444; display: block; line-height: 1.2; letter-spacing: .04em; }
.stp { font-size: 9.4pt; line-height: 1.27; margin: 0; }
.sph { display: flex; align-items: center; justify-content: space-between; margin-bottom: 3pt; }
.cbs { font-size: 9.4pt; white-space: nowrap; }
.cb { display: inline-block; width: 9pt; height: 9pt; border: 1.2pt solid #000; border-radius: 2pt; margin: 0 3pt -1pt 9pt; }
.spl { display: flex; align-items: flex-end; gap: 7pt; font-size: 10pt; margin-top: 4pt; }
.spl .ln { flex: 1; border-bottom: 1pt solid #000; height: 11pt; }
.spl .sc2 { white-space: nowrap; font-weight: 600; }
.sp svg, .kb svg { margin: 0 auto; }
.kbh { display: flex; align-items: center; gap: 8pt; margin-bottom: 2pt; }
.kbh .meta { flex: 1; }
.syt td.sy { text-align: center; padding: 1pt 4pt !important; }
.syt td.sy svg { margin: 1pt auto; }
.syt td.sd { font-family: 'Oswald'; font-weight: 700; font-size: 13pt; letter-spacing: .02em; text-align: center; }
.syt td.ct { font-weight: 600; font-size: 10.5pt; text-align: center; letter-spacing: .05em; }
.syt td.ctr { text-align: center; }
.exbox { border: 1.3pt solid #000; border-radius: 7pt; padding: 5pt 8pt 3pt; margin: 6pt 0; }
.exbox svg { margin: 0 auto; }
.trk { border-collapse: collapse; width: 100%; table-layout: fixed; font-size: 9.6pt; }
.trk th { background: #000; color: #fff; font-family: 'Oswald'; font-weight: 500; text-transform: uppercase; font-size: 9pt; padding: 3pt 4pt; border: 1pt solid #000; text-align: center; }
.trk td { border: 1pt solid #000; padding: 0 4pt; height: 26pt; text-align: center; }
.ilist { list-style: none; padding: 0 !important; margin: 0 !important; }
.ilist li { font-size: 10pt !important; line-height: 1.25 !important; margin: 0 0 7pt !important; padding-left: 15pt; position: relative; }
.ilist li::before { content: ''; position: absolute; left: 0; top: 2.2pt; width: 9pt; height: 9pt; border: 1.2pt solid #000; border-radius: 2pt; }
.tempo { display: flex; gap: 12pt; align-items: center; }
.tempo img { display: block; height: 0.95in; width: auto; flex: none; }
.cover { align-items: center; justify-content: space-between; padding: 0.55in 0.6in 0.5in; }
.store { font-family: 'Oswald'; font-weight: 500; font-size: 13pt; letter-spacing: .32em; text-transform: uppercase; }
.ctitle { text-align: center; }
.ctitle .a { font-family: 'Oswald'; font-weight: 700; font-size: 40pt; line-height: 1; letter-spacing: .02em; }
.ctitle .b { font-family: 'Oswald'; font-weight: 700; white-space: nowrap; font-size: 64pt; line-height: .95; letter-spacing: .01em; }
.ctitle .c { font-family: 'Oswald'; font-weight: 300; font-size: 17pt; margin-top: 8pt; }
.cband { width: 100%; background: #000; color: #fff; text-align: center; font-family: 'Oswald'; font-weight: 500; font-size: 14pt;
         letter-spacing: .08em; text-transform: uppercase; padding: 8pt 0 9pt; border-radius: 4pt; white-space: nowrap; }
.cband em { font-style: normal; color: ACCENT; }
""".replace("ACCENT", ACCENT)


def html_doc(pages, title="doc"):
    return (f'<!doctype html><html><head><meta charset="utf-8"><title>{escape(title)}</title><style>{font_css()}{CSS}</style></head>'
            f'<body>{"".join(pages)}</body></html>')


def foot(left, right):
    return f'<div class="foot"><span>{left}</span><span>{right}</span></div>'


COPY = f"© {YEAR} {STORE} · {BRAND} · For single-classroom use"

# ------------------------------------------------------------------ page numbers (single source of truth)
P_COVER, P_TEACH, P_SCORE, P_ABOUT, P_CHART, P_CHART2 = 1, 2, 3, 4, 5, 6
P_TRACK, P_TERMS = 25, 26
TOTAL_PAGES = P_TERMS


def half_of(n):
    return ((n - 1) % 10) // 5


def level_of(n):
    return (n - 1) // 10 + 1


def p_script(n):
    return 7 + 6 * (level_of(n) - 1) + half_of(n)


def p_student(n):
    return p_script(n) + 2


def p_key(n):
    return p_script(n) + 4


def ex_range(level, half):
    a = (level - 1) * 10 + half * 5 + 1
    return a, a + 4


PAGE_NAMES = {P_COVER: "cover", P_TEACH: "Teacher notes", P_SCORE: "Scoring and assessment", P_ABOUT: "About rhythm dictation",
              P_CHART: "Syllables and counting chart", P_CHART2: "Chart: 6/8 and the three meters", P_TRACK: "Progress tracker", P_TERMS: "Terms of use"}
for _l in (1, 2, 3):
    for _h in (0, 1):
        _a, _b = ex_range(_l, _h)
        PAGE_NAMES[7 + 6 * (_l - 1) + _h] = f"Level {_l} teacher scripts (exercises {_a}–{_b})"
        PAGE_NAMES[9 + 6 * (_l - 1) + _h] = f"Level {_l} student pages (exercises {_a}–{_b})"
        PAGE_NAMES[11 + 6 * (_l - 1) + _h] = f"Level {_l} answer key (exercises {_a}–{_b})"
assert sorted(PAGE_NAMES) == list(range(1, TOTAL_PAGES + 1))
XREFS = []


def xref(frm, to, text):
    XREFS.append((frm, to, text))
    return text


def wm_div(on):
    return '<div class="wm">PREVIEW</div>' if on else ""


def top_block(sub, tag, tagline, ak=False):
    return (f'<div class="top"><div class="t">{TITLE}<small>{sub}</small></div>'
            f'<div class="tag"><div class="lv{" ak" if ak else ""}">{tag}</div><div class="ln">{tagline}</div></div></div>')


def doc_head(h1, sub):
    return f'<div class="rule"><h1>{h1}</h1><div style="font-family:Oswald;font-weight:300;font-size:13pt">{sub}</div></div>'


# ------------------------------------------------------------------ pages
def cover_art_img(height):
    return f'<img src="../art/hero.png" alt="" style="display:block;height:{height};width:auto">'


def cover_page():
    return (f'<section class="page cover"><div class="store">{BRAND}</div>'
            f'<div style="height:4.7in;display:flex;align-items:center;justify-content:center">{cover_art_img("4.7in")}</div>'
            f'<div class="ctitle"><div class="a">LEVELS 1–3</div><div class="b">RHYTHM DICTATION</div>'
            f'<div class="c">Teacher scripts, student pages and answer keys · 4/4, 3/4 and 6/8</div></div>'
            f'<div class="cband">Grades 3–8 <em>·</em> 30 exercises <em>·</em> {TOTAL_PAGES} pages</div></section>')


PACING = [("Week 1", "Teach the five steps (page %d) and the syllables chart (page %d), then start Level 1.", "1–5"),
          ("Week 2", "Finish Level 1, score each bar (page %d) and fill in the progress tracker (page %d).", "6–10"),
          ("Week 3", "Teach 3/4, whole notes, dotted half notes and syncopation with the chart (page %d).", "11–15"),
          ("Week 4", "Finish Level 2 with three- and four-bar exercises.", "16–20"),
          ("Week 5", "Teach 6/8 and sixteenth-note groups with the charts (pages %d and %d).", "21–25"),
          ("Week 6", "Finish Level 3 and review the tracker.", "26–30")]


def teacher_page(wm=False):
    refs = [(P_ABOUT, P_CHART), (P_SCORE, P_TRACK), (P_CHART,), (), (P_CHART, P_CHART2), ()]
    rows = ""
    for (a, b, c), r in zip(PACING, refs):
        rows += f"<tr><td><b>{a}</b></td><td>{b % r if r else b}</td><td>{c}</td></tr>"
    return (f'<section class="page doc">{wm_div(wm)}{doc_head("Teacher Notes", f"{TITLE} · Levels 1–3 · 30 exercises · grades 3–8")}'
            f'<p><b>What this is.</b> Thirty rhythm dictation exercises in three levels. Students hear a rhythm, echo it, hear it in their heads and then write it in notation. '
            f'Each exercise has a <b>teacher script</b> with the meter, tempo, count-in and the exact syllables and counts to perform, a <b>student page</b> with blank bars, and an <b>answer key</b>. '
            f'No audio is included. You perform each rhythm yourself by clapping, tapping or playing it on one pitch.</p>'
            f'<div class="box"><div class="tempo"><img src="../art/spot-metronome.png" alt=""><div><h3>Tempo and count-in</h3>'
            f'<p>Every script gives a tempo in beats per minute (BPM) and a count-in. Count in aloud before every play: four beats in 4/4, three beats in 3/4 and, in 6/8, '
            f'the two big beats twice (1 2 1 2). In 6/8 the BPM is the pulse of the dotted quarter note.</p></div></div></div>'
            f'<h2>Levels and pages</h2><table><tr><th style="width:62pt">Level</th><th style="width:48pt">Grades</th><th>What it adds</th><th style="width:70pt">Exercises</th><th style="width:66pt">Pages</th></tr>'
            f'<tr><td><b>Level 1</b></td><td>3–4</td><td>4/4, two bars: quarter notes, quarter rests, eighth pairs, half notes</td><td>1–10</td><td>{xref(P_TEACH, 7, "7–12")}</td></tr>'
            f'<tr><td><b>Level 2</b></td><td>4–6</td><td>Adds 3/4, whole notes, dotted half notes, eighth-quarter-eighth syncopation; 2–4 bars</td><td>11–20</td><td>{xref(P_TEACH, 13, "13–18")}</td></tr>'
            f'<tr><td><b>Level 3</b></td><td>6–8</td><td>Adds 6/8 in groups of three eighths, sixteenth-note groups, dotted quarter plus eighth; four bars</td><td>21–30</td><td>{xref(P_TEACH, 19, "19–24")}</td></tr></table>'
            f'<h2>Suggested pacing</h2><table><tr><th style="width:56pt">When</th><th>Focus</th><th style="width:70pt">Exercises</th></tr>{rows}</table>'
            f'<h2>Differentiation</h2><ul>'
            f'<li><b>Support.</b> Let students keep the chart (page {P_CHART}) beside them, or write the first bar together on the board.</li>'
            f'<li><b>Extension.</b> Students write their own two-bar rhythm and check a partner\'s dictation.</li></ul>'
            f'<h2>Standards</h2><p>The exercises support the Performing process (reading and writing rhythmic notation) of the National Core Arts Standards. Please match them to your own curriculum. '
            f'No songs, lyrics or copyrighted characters are used.</p>'
            f'<div style="flex:1"></div>{foot(COPY, f"Page {P_TEACH}")}</section>')


def score_page(wm=False):
    bands = ""
    for k in (1, 2, 3):
        T = LEVEL_POINTS[k]
        sec, dev = math.ceil(0.9 * T), math.ceil(0.7 * T)
        bands += (f'<tr data-lv="{k}"><td><b>Level {k}</b></td><td class="tb">{LEVEL_BARS_TOTAL[k]}</td><td class="tp">{T}</td>'
                  f'<td>{sec} to {T}</td><td>{dev} to {sec - 1}</td><td>0 to {dev - 1}</td></tr>')
    return (f'<section class="page doc">{wm_div(wm)}{doc_head("Scoring and Assessment", "Score every bar, then add up the exercise")}'
            f'<p>Score each <b>bar</b> separately, so a student who writes one bar wrongly still earns credit for the others. Every bar is worth 2 points. '
            f'An exercise is worth 2 points for each of its bars: 4 points for two bars, 6 for three bars and 8 for four bars.</p>'
            f'<table><tr><th style="width:56pt">Points</th><th>What the bar looks like</th></tr>'
            f'<tr><td><b>2</b></td><td>Exactly right. Every note and rest value is correct and in the right order, stems and beams are correct, and the bar adds up to the time signature.</td></tr>'
            f'<tr><td><b>1</b></td><td>Almost. The bar adds up to the time signature but one note or rest value is wrong, or the rhythm is right but has one notation slip such as a missing beam or a stem on the wrong side.</td></tr>'
            f'<tr><td><b>0</b></td><td>The bar does not add up to the time signature, or it is blank.</td></tr></table>'
            f'<h2>Totals for each level</h2>'
            f'<table class="bands"><tr><th style="width:52pt">Level</th><th style="width:44pt">Bars</th><th style="width:50pt">Points</th><th>Secure (90% or more)</th><th>Developing (70% to 89%)</th><th>Needs another pass</th></tr>{bands}</table>'
            f'<p class="small">All 30 exercises together are worth {TOTAL_POINTS} points. Students record their points on the progress tracker (page {xref(P_SCORE, P_TRACK, str(P_TRACK))}).</p>'
            f'<h2>How to assess quickly</h2><ul>'
            f'<li><b>Check the sum first.</b> Have students count each bar aloud against the time signature. A bar that does not add up scores 0 and is easy to spot.</li>'
            f'<li><b>Then check the pattern.</b> Compare the bar with the answer key beat by beat. Look first at the rests, then at the held notes and then at the beams.</li>'
            f'<li><b>Name the error.</b> Write one word beside a lost point: <i>sum</i>, <i>rest</i>, <i>value</i>, <i>beam</i> or <i>stem</i>. Students fix the bar and clap it back for full credit.</li>'
            f'<li><b>Peer check.</b> Partners swap papers, clap each other\'s bars from the notation and mark them with the answer key before you collect the pages.</li></ul>'
            f'<h2>Example</h2><p>A student writes Exercise 4 (two bars, 4 points). Bar 1 is exactly right and earns 2 points. Bar 2 adds up to four beats but has a quarter note where the quarter rest belongs, so it earns 1 point. The exercise score is 3 out of 4.</p>'
            f'<h2>Where to look in the key</h2><p>Each answer key shows the notation with the syllables under the notes and the counts under the syllables. '
            f'Level 1 keys are on pages {xref(P_SCORE, p_key(1), str(p_key(1)))} and {p_key(6)}, Level 2 keys on pages {p_key(11)} and {p_key(16)}, and Level 3 keys on pages {p_key(21)} and {p_key(26)}.</p>'
            f'<div style="flex:1"></div>{foot(COPY, f"Page {P_SCORE}")}</section>')


EXAMPLE_BAR = ["ta", "ti-ti", "ta", "shh"]


def about_page(wm=False):
    desc = ["Your teacher performs the rhythm. Keep a steady beat and notice the time signature and the number of bars.",
            "Clap or say the rhythm back with the syllables so you know what you heard.",
            "Hear the rhythm silently in your head while your finger keeps the beat. This is called audiating, and it is the step that makes writing easier.",
            "Write the notes and rests bar by bar. Make every bar add up to the time signature.",
            "Clap what you wrote, count each bar and compare it with the answer key."]
    srows = "".join(f'<div class="step" data-step="{i + 1}">{icon_svg(STEP_ICONS[i])}<span class="n">{i + 1}</span><div><p><b>{STEP_NAMES[i]}.</b> {desc[i]}</p></div></div>' for i in range(5))
    ex = staff_svg("4/4", [EXAMPLE_BAR], 7.0, 330.0, "key", "EXAMPLE", labels=True)
    return (f'<section class="page doc">{wm_div(wm)}{doc_head("About Rhythm Dictation", "Hear it, say it, write it")}'
            f'<p>In rhythm dictation you listen to a rhythm and write it in notation. Every exercise has blank bars with the barlines and the time signature already printed. '
            f'Follow the same five steps each time.</p>'
            f'<div class="steps">{srows}</div>'
            f'<h2>Worked example</h2><div class="box" style="display:flex;gap:14pt;align-items:center"><div style="flex:none">{ex}</div>'
            f'<div><p><b>You hear:</b> ta ti-ti ta shh.</p><p><b>Add it up:</b> ta is 1 beat, ti-ti is 1 beat, ta is 1 beat and shh (a quarter rest) is 1 beat. That makes 4 beats, which fills one bar of 4/4.</p></div></div>'
            f'<h2>Your turn</h2><div class="box"><p>Your teacher performs a two-bar rhythm in 4/4. Listen, echo, audiate, then write it here.</p>'
            f'{staff_svg("4/4", None, 7.0, 400.0, "blank", "YOURTURN", nblank=2)}</div>'
            f'<h2>Remember</h2><ul><li>The top number of a time signature tells you how many beats fill a bar.</li>'
            f'<li>The bottom number names the note that gets one beat.</li>'
            f'<li>A rest is silence, but it still counts and it still needs to be written.</li></ul>'
            f'<div style="flex:1"></div>{foot(COPY, f"Page {P_ABOUT}")}</section>')


CHART_SIMPLE = [("ta", "Quarter note", 1), ("shh", "Quarter rest (silence)", 1), ("ti-ti", "Two eighth notes, joined by a beam", 1),
                ("ta-a", "Half note", 1), ("ta-a-a", "Dotted half note", 2), ("ta-a-a-a", "Whole note", 2),
                ("ti-ta-ti", "Syncopation: eighth, quarter, eighth", 2), ("ti-ka-ti-ka", "Four sixteenth notes, joined by two beams", 3),
                ("ti-ti-ka", "Eighth note, then two sixteenth notes", 3), ("ti-ka-ti", "Two sixteenth notes, then an eighth note", 3),
                ("tam-ti", "Dotted quarter note, then an eighth note", 3)]
CHART_COMP = [("ta", "Dotted quarter note", 3), ("ti-ti-ti", "Three eighth notes, joined by a beam", 3),
              ("ta-ti", "Quarter note, then an eighth note", 3), ("ti-ta", "Eighth note, then a quarter note", 3)]


def beats_text(tokname, meter):
    _e, _s, tot = expand([tokname], meter)
    b = tot / METERS[meter]["win"]
    assert b.denominator == 1
    b = int(b)
    return f"{b} beat" + ("" if b == 1 else "s")


def chart_rows(rows, meter, tag):
    out = ""
    for tokname, nm, lvl in rows:
        ev, _s, tot = expand([tokname], meter)
        svg = sym_svg([tokname], meter, f"sym-{tag}-{tokname}")
        out += (f'<tr data-say="{tokname}" data-meter="{meter}"><td class="sy">{svg}</td><td class="nm"><b>{nm}</b></td><td class="bt ctr">{beats_text(tokname, meter)}</td>'
                f'<td class="sd">{tokname}</td><td class="ct">{count_text(ev, meter, tot)}</td><td class="lv ctr">Level {lvl}</td></tr>')
    return out


CHART_HEAD = ('<tr><th style="width:150pt">Notation</th><th>Name</th><th style="width:52pt">Length</th><th style="width:84pt">Say</th>'
              '<th style="width:70pt">Count</th><th style="width:46pt">Level</th></tr>')


def chart_page(wm=False):
    return (f'<section class="page doc">{wm_div(wm)}{doc_head("Syllables and Counting Chart", "Simple meters: 4/4 and 3/4")}'
            f'<table class="syt" data-chart="simple">{CHART_HEAD}{chart_rows(CHART_SIMPLE, "4/4", "s")}</table>'
            f'<p class="small"><b>Reading the Count column.</b> A number is a note that starts on that beat, a plus is the half of the beat, and e and a are the other quarters. '
            f'A dash means a held note is still sounding, and a number in parentheses is a rest. Every row is shown starting on beat 1.</p>'
            f'<ul><li><b>Clap every note.</b> Clap where a note starts. A rest is silence, so say "shh" with your hands apart. Hold a long note by keeping your hands together while you say the syllable.</li>'
            f'<li><b>Beams.</b> Eighth notes joined by a beam share one beat, so each is half a beat. Four sixteenth notes with two beams share one beat, so each is a quarter of a beat.</li>'
            f'<li><b>Dots.</b> A dot adds half of the note\'s value. A dotted half note lasts 3 beats. A dotted quarter note lasts 1 and a half beats.</li></ul>'
            f'<div style="flex:1"></div>{foot(COPY, f"Page {P_CHART}")}</section>')


METER_EXAMPLES = [("4/4", ["ta", "ta", "ta", "ta"], "M44", "Four beats in a bar, and a quarter note gets one beat."),
                  ("3/4", ["ta", "ta", "ta"], "M34", "Three beats in a bar, and a quarter note gets one beat."),
                  ("6/8", ["ta", "ta"], "M68", "Six eighth notes in a bar, felt as two big beats of three eighths each.")]


def chart2_page(wm=False):
    exs = "".join(f'<div class="exbox" data-meterex="{m}"><div style="display:flex;gap:12pt;align-items:center"><div style="flex:none">'
                  f'{staff_svg(m, [toks], 7.0, 300.0, "key", uid, labels=True)}</div><p style="margin:0;font-size:10.4pt;line-height:1.3"><b>{m}.</b> {txt}</p></div></div>'
                  for m, toks, uid, txt in METER_EXAMPLES)
    return (f'<section class="page doc">{wm_div(wm)}{doc_head("Chart: 6/8 and the Three Meters", "Compound meter and how each meter counts")}'
            f'<table class="syt" data-chart="comp">{CHART_HEAD}{chart_rows(CHART_COMP, "6/8", "c")}</table>'
            f'<p class="small"><b>Reading 6/8.</b> In 6/8 every eighth note gets a count, 1 la li 2 la li, and each big beat is a dotted quarter note. The rows above show one big beat starting on count 1.</p>'
            f'<h2>The three meters</h2>{exs}'
            f'<ul><li><b>Compound meter.</b> 6/8 is a compound meter because each beat divides into three. Eighth notes are beamed in groups of three, one group for each big beat.</li>'
            f'<li><b>Tempo in 6/8.</b> The scripts give the BPM of the dotted quarter note, the big beat.</li></ul>'
            f'<div style="flex:1"></div>{foot(COPY, f"Page {P_CHART2}")}</section>')


def script_block(e):
    bars = ""
    for bi, b in enumerate(e["bars"]):
        evs = expand(b, e["meter"])[0]
        bars += (f'<div class="bc"><span class="bl">Bar {bi + 1}</span><div><span class="sylbar" data-bar="{bi + 1}">{" ".join(b)}</span>'
                 f'<span class="cntbar" data-bar="{bi + 1}">{count_text(evs, e["meter"])}</span></div></div>')
    plays = e["plays"]
    steps = ("1 listen, 2 echo, 3 audiate" if plays == 3 else "1 listen, 2 echo, 3 audiate, 4 write along")
    unit = "dotted quarter note" if e["meter"] == "6/8" else "quarter note"
    foc = ", ".join(features(e))
    return (f'<div class="sc" data-ex="{e["num"]}" data-meter="{e["meter"]}" data-bars="{len(e["bars"])}" data-lv="{e["level"]}">'
            f'<div class="sch"><span class="en">Exercise {e["num"]}</span><span class="mt">{e["meter"]}</span>'
            f'<span class="meta"><b class="nb">{len(e["bars"])}</b> bars · <b class="bpm">{e["bpm"]}</b> BPM ({unit} = {e["bpm"]})</span><span class="sp1"></span>'
            f'<span class="meta">Count in: <b class="ci">{count_in(e["meter"])}</b></span></div>'
            f'<div class="scbars">{bars}</div>'
            f'<p class="stp"><b>Play it <span class="plays">{plays}</span> times:</b> {steps}. Writing time: <span class="secs">{e["secs"]}</span> seconds.<br>'
            f'<b>Listen for:</b> <span class="foc">{foc}</span>.</p></div><!--/sc-->')


def exercise_page_head(level, half, kind):
    a, b = ex_range(level, half)
    n = a
    sp, st, kp = p_script(n), p_student(n), p_key(n)
    if kind == "script":
        page, name = sp, PAGE_NAMES[sp]
        top = top_block(name, f"LEVEL {level}", f"Grades {LEVEL_GRADES[level]}")
        right = f"Page {page} · Student pages: page {st} · Answer key: page {kp}"
    elif kind == "student":
        page, name = st, PAGE_NAMES[st]
        top = top_block(name, f"LEVEL {level}", f"Grades {LEVEL_GRADES[level]}")
        right = f"Page {page} · Teacher scripts: page {sp} · Answer key: page {kp}"
    else:
        page, name = kp, PAGE_NAMES[kp]
        top = top_block(name, "ANSWER KEY", f"Level {level} · exercises {a}–{b}", ak=True)
        right = f"Page {page} · Teacher scripts: page {sp} · Student pages: page {st}"
    return a, b, page, top, right


def scripts_page(level, half, wm=False):
    a, b, page, top, right = exercise_page_head(level, half, "script")
    blocks = "".join(script_block(EXS[n - 1]) for n in range(a, b + 1))
    return (f'<section class="page" data-page="{page}">{wm_div(wm)}{top}'
            f'<div class="stack">{blocks}</div>{foot(COPY, right)}</section>')


def student_block(e):
    cbs = "".join(f'<span class="cb"></span>{s}' for s in STEP_NAMES)
    return (f'<div class="sp" data-ex="{e["num"]}" data-meter="{e["meter"]}" data-bars="{len(e["bars"])}">'
            f'<div class="sph"><span class="sch"><span class="en">Exercise {e["num"]}</span><span class="mt">{e["meter"]}</span>'
            f'<span class="meta">{len(e["bars"])} bars</span></span><span class="cbs">{cbs}</span></div>'
            f'{blank_svg(e, SVG_W)}'
            f'<div class="spl"><span>Syllables:</span><span class="ln"></span><span class="sc2">Score ____ / <span class="mx">{2 * len(e["bars"])}</span></span></div></div><!--/sp-->')


def student_page(level, half, wm=False):
    a, b, page, top, right = exercise_page_head(level, half, "student")
    blocks = "".join(student_block(EXS[n - 1]) for n in range(a, b + 1))
    return (f'<section class="page" data-page="{page}">{wm_div(wm)}{top}'
            f'<div class="nd"><span>Name</span><span class="ln"></span><span>Date</span><span class="ln" style="max-width:110pt"></span>'
            f'<span>Class</span><span class="ln" style="max-width:90pt"></span></div>'
            f'<div class="stack">{blocks}</div>{foot(COPY, right)}</section>')


def key_block(e):
    return (f'<div class="kb" data-ex="{e["num"]}" data-meter="{e["meter"]}" data-bars="{len(e["bars"])}">'
            f'<div class="kbh"><span class="en" style="background:{ACCENT}">Exercise {e["num"]}</span><span class="mt">{e["meter"]}</span>'
            f'<span class="meta">{len(e["bars"])} bars · {e["bpm"]} BPM · {2 * len(e["bars"])} points</span></div>'
            f'{key_svg(e, LEVEL_S[e["level"]], SVG_W)}</div><!--/kb-->')


def key_page(level, half, wm=False):
    a, b, page, top, right = exercise_page_head(level, half, "key")
    blocks = "".join(key_block(EXS[n - 1]) for n in range(a, b + 1))
    return (f'<section class="page" data-page="{page}">{wm_div(wm)}{top}'
            f'<div class="stack">{blocks}</div>{foot(COPY, right)}</section>')


I_CAN = {1: ["write quarter notes and quarter rests", "write two eighth notes joined by a beam", "write half notes",
             "make each bar add up to 4 beats", "echo a rhythm before I write it"],
         2: ["write 3/4 bars that add up to 3 beats", "write whole notes and dotted half notes", "write eighth-quarter-eighth syncopation",
             "keep three or four bars in my head", "check my bars against the beat"],
         3: ["write groups of four sixteenth notes", "write a dotted quarter note and an eighth note", "write 6/8 with eighths in groups of three",
             "write four bars in 4/4, 3/4 or 6/8", "find and fix my own mistakes"]}


def track_page(wm=False):
    tabs = ""
    for k in (1, 2, 3):
        rows = "".join(f'<tr data-ex="{e["num"]}"><td>{e["num"]}</td><td>{e["meter"]}</td><td>____ / <span class="mx">{2 * len(e["bars"])}</span></td></tr>' for e in LEVEL_EXS[k])
        tabs += (f'<div style="flex:1"><table class="trk" data-lv="{k}"><tr><th colspan="3">Level {k} · grades {LEVEL_GRADES[k]}</th></tr>'
                 f'<tr><th style="width:30pt">No.</th><th style="width:34pt">Meter</th><th>Points</th></tr>{rows}'
                 f'<tr><td colspan="2"><b>Total</b></td><td>____ / <b class="lt">{LEVEL_POINTS[k]}</b></td></tr></table></div>')
    ican = "".join(f'<div class="box" style="flex:1"><h3>Level {k}: I can</h3><ul class="ilist">{"".join(f"<li>{t}</li>" for t in I_CAN[k])}</ul></div>' for k in (1, 2, 3))
    return (f'<section class="page doc">{wm_div(wm)}{doc_head("Progress Tracker", "Record your points after each exercise and check off what you can do")}'
            f'<div class="nd" style="margin:0 0 8pt"><span>Name</span><span class="ln"></span><span>Class</span><span class="ln" style="max-width:120pt"></span></div>'
            f'<div style="display:flex;gap:12pt">{tabs}</div>'
            f'<p class="small" style="margin-top:6pt">Each bar is worth 2 points (see page {xref(P_TRACK, P_SCORE, str(P_SCORE))}). All 30 exercises together are worth <span class="tt">{TOTAL_POINTS}</span> points.</p>'
            f'<h2>Self-assessment</h2><div class="cols" style="margin-top:2pt">{ican}</div>'
            f'<div style="flex:1"></div>{foot(COPY, f"Page {P_TRACK}")}</section>')


def terms_page(wm=False):
    return (f'<section class="page doc">{wm_div(wm)}{doc_head("Terms of Use", "Thank you for your purchase!")}'
            f'<p>© {YEAR} {STORE}. {BRAND} by {STORE}. All rights reserved. This purchase gives <b>one teacher</b> a license to use this resource with their own students.</p>'
            f'<h2>You may</h2><ul><li>Print and copy pages for your own classroom and students, year after year.</li>'
            f'<li>Share pages with your own students through a password-protected class site or learning platform.</li>'
            f'<li>Use the pages with your own students when you have a substitute teacher.</li></ul>'
            f'<h2>You may not</h2><ul><li>Share, email or copy this resource for other teachers, a whole school or a district. Additional licenses are available on Teachers Pay Teachers.</li>'
            f'<li>Post any part of it on a public website, shared drive or social media.</li>'
            f'<li>Sell, give away or claim any part of it as your own, or edit it into a new product.</li></ul>'
            f'<h2>Questions?</h2><p>Please use the Q&amp;A tab on the {BRAND} by {STORE} store on Teachers Pay Teachers. If something looks wrong, let me know there and I will fix it.</p>'
            f'<h2>Credits</h2><ul>'
            f'<li>The rhythms, scripts, student pages, answer keys and step icons are original work, {BRAND} by {STORE}.</li>'
            f'<li>The cover artwork and the metronome picture are illustrations made with AI tools. The notation, charts, step icons and text are drawn in code.</li>'
            f'<li>Music notation font: Bravura © Steinberg Media Technologies GmbH, SIL Open Font License 1.1.</li>'
            f'<li>Text fonts: Oswald (The Oswald Project Authors) and Source Sans 3 (Adobe), SIL Open Font License 1.1.</li></ul>'
            f'<h2>Printing tips</h2><ul><li>Print the student pages single-sided in black and white. Staff lines and notes print clearly without color.</li>'
            f'<li>Keep the teacher scripts and answer keys for yourself. Copy only the student pages and the progress tracker for your class, so students never see the answers.</li></ul>'
            f'<h2>What is in this file ({TOTAL_PAGES} pages)</h2><p>Page 1 cover, page {P_TEACH} teacher notes, page {P_SCORE} scoring and assessment, page {P_ABOUT} about rhythm dictation, '
            f'pages {P_CHART}–{P_CHART2} syllables and counting charts, pages {p_script(1)}–{p_key(30)} the teacher scripts, student pages and answer keys for Levels 1, 2 and 3, '
            f'page {P_TRACK} progress tracker and page {P_TERMS} these terms.</p>'
            f'<p class="small">{DISCLOSURE}</p><div style="flex:1"></div>{foot(COPY, f"Page {P_TERMS}")}</section>')


def full_pages():
    XREFS.clear()
    pages = [cover_page(), teacher_page(), score_page(), about_page(), chart_page(), chart2_page()]
    for lv in (1, 2, 3):
        for kind, fn in (("script", scripts_page), ("student", student_page), ("key", key_page)):
            for h in (0, 1):
                pages.append(fn(lv, h))
    pages += [track_page(), terms_page()]
    assert len(pages) == TOTAL_PAGES, len(pages)
    return pages


PREVIEW_PAGES = [P_ABOUT, 7, 15, 23]       # about, Level 1 scripts, Level 2 student pages, Level 3 answer key


def preview_pages():
    fn = {P_ABOUT: about_page, 7: lambda wm: scripts_page(1, 0, wm), 15: lambda wm: student_page(2, 0, wm), 23: lambda wm: key_page(3, 0, wm)}
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
.pill { border: 2px solid #000; border-radius: 30px; padding: 6px 22px; font-family: Oswald; font-weight: 500; font-size: 24px; letter-spacing: .06em; text-transform: uppercase; white-space: nowrap; }
""".replace("ACCENT", ACCENT)


def sq_doc(body):
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{font_css()}html,body{{margin:0;background:#fff;font-family:"Source Sans 3",sans-serif}}{SQ_CSS}</style></head><body>'
            f'{body}</body></html>')


def cover_square():
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div>'
        f'<div style="flex:1;display:flex;flex-direction:column;justify-content:space-evenly;align-items:center;width:100%;padding:0 0 76px">'
        f'<div style="height:470px;display:flex;align-items:center">{cover_art_img("470px")}</div>'
        f'<div><div class="hd" style="font-size:64px">Levels 1–3</div><div class="hd" style="font-size:108px">Rhythm Dictation</div>'
        f'<div class="sub" style="font-size:28px;margin-top:12px">Teacher scripts, student pages and answer keys · 4/4, 3/4 and 6/8</div></div>'
        f'</div><div class="band">Grades 3–8 <em>·</em> 30 exercises <em>·</em> {TOTAL_PAGES} pages</div></div>')


def swm_over(size=230):
    return f'<div class="swm" style="font-size:{size}px">PREVIEW</div>'


def shot(src, w):
    return f'<div class="shot" style="width:{w}px"><img src="{src}"></div>'


def pill_row(items):
    return '<div style="display:flex;gap:18px">' + "".join(f'<div class="pill">{t}</div>' for t in items) + "</div>"


def preview_square_1(img):
    caps = [(PAGE_NAMES[P_ABOUT], "The five steps students follow"), (PAGE_NAMES[7], "Meter, tempo, count-in and the exact syllables"),
            (PAGE_NAMES[15], "Blank bars with the time signature printed")]
    shots = "".join(
        f'<div style="width:290px;display:flex;flex-direction:column;align-items:center">{shot(img[i], 290)}'
        f'<div class="lbl" style="font-size:22px;margin-top:20px">{caps[i][0]}</div>'
        f'<div style="font-family:Oswald;font-weight:300;font-size:20px;line-height:1.25;text-align:center;margin-top:8px;width:270px">{caps[i][1]}</div></div>' for i in range(3))
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div><div class="hd" style="font-size:72px;margin-top:28px">What is inside</div>'
        f'<div class="sub" style="font-size:29px;margin-top:10px">Everything for 30 rhythm dictation lessons</div>'
        f'<div style="flex:1;display:flex;flex-direction:column;align-items:center;justify-content:space-evenly;padding-bottom:70px">'
        f'<div style="display:flex;gap:22px;align-items:flex-start">{shots}</div>{pill_row(["3 levels", "30 exercises", "Scripts + pages + keys"])}</div>'
        f'{swm_over(230)}<div class="band">Listen <em>·</em> Echo <em>·</em> Audiate <em>·</em> Write <em>·</em> Check</div></div>')


def preview_square_2(a, b):
    pair = "".join(f'<div style="width:380px">{shot(src, 380)}<div class="lbl">{lab}<span>{sub}</span></div></div>'
                   for src, lab, sub in ((a, PAGE_NAMES[9], "Blank bars for the student"), (b, PAGE_NAMES[11], "Notation, syllables and counts")))
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div><div class="hd" style="font-size:72px;margin-top:24px">Student page and key</div>'
        f'<div class="sub" style="font-size:27px;margin-top:8px">Every exercise has both, ready to print</div>'
        f'<div style="flex:1;display:flex;align-items:center;padding-bottom:70px"><div style="display:flex;gap:44px;align-items:flex-start">{pair}</div></div>'
        f'{swm_over(230)}<div class="band">Blank bars <em>·</em> answer key <em>·</em> 30 exercises</div></div>')


def preview_square_3(img):
    caps = [(PAGE_NAMES[23], "Sixteenth notes and 6/8"), (PAGE_NAMES[P_SCORE], "Score every bar"), (PAGE_NAMES[P_TRACK], "Points and self-assessment")]
    shots = "".join(
        f'<div style="width:290px;display:flex;flex-direction:column;align-items:center">{shot(img[i], 290)}'
        f'<div class="lbl" style="font-size:22px;margin-top:20px">{caps[i][0]}</div>'
        f'<div style="font-family:Oswald;font-weight:300;font-size:20px;line-height:1.25;text-align:center;margin-top:8px;width:270px">{caps[i][1]}</div></div>' for i in range(3))
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div><div class="hd" style="font-size:72px;margin-top:28px">Keys, scoring, tracking</div>'
        f'<div class="sub" style="font-size:27px;margin-top:10px">Grades 3–8 across three levels</div>'
        f'<div style="flex:1;display:flex;flex-direction:column;align-items:center;justify-content:space-evenly;padding-bottom:70px">'
        f'<div style="display:flex;gap:22px;align-items:flex-start">{shots}</div>{pill_row(["2 points a bar", f"{TOTAL_POINTS} points in all"])}</div>'
        f'{swm_over(230)}<div class="band">Level 1 <em>·</em> Level 2 <em>·</em> Level 3</div></div>')


# ------------------------------------------------------------------ render / build
def node_env():
    env = dict(os.environ)
    if not env.get("NODE_PATH"):
        env["NODE_PATH"] = subprocess.run(["npm", "root", "-g"], capture_output=True, text=True).stdout.strip()
    return env


def render(jobs):
    path = os.path.join(BUILD, "jobs.json")
    with open(path, "w") as fh:
        json.dump(jobs, fh)
    subprocess.run(["node", RENDER_JS, path], check=True, env=node_env())


def write(name, text):
    p = os.path.join(BUILD, name)
    with open(p, "w") as fh:
        fh.write(text)
    return p


PAGE_LIST = [("Cover", 1), ("Teacher notes", 1), ("Scoring and assessment", 1), ("About rhythm dictation", 1), ("Syllables and counting charts", 2),
             ("Level 1 teacher scripts, exercises 1-10", 2), ("Level 1 student pages, exercises 1-10", 2), ("Level 1 answer keys, exercises 1-10", 2),
             ("Level 2 teacher scripts, exercises 11-20", 2), ("Level 2 student pages, exercises 11-20", 2), ("Level 2 answer keys, exercises 11-20", 2),
             ("Level 3 teacher scripts, exercises 21-30", 2), ("Level 3 student pages, exercises 21-30", 2), ("Level 3 answer keys, exercises 21-30", 2),
             ("Progress tracker", 1), ("Terms of use and credits", 1)]
assert sum(c for _, c in PAGE_LIST) == TOTAL_PAGES


def upload_md():
    lst = "\n".join(f"- {n}: {c}" for n, c in PAGE_LIST)
    return f"""# UPLOAD: {LISTING_TITLE} (TpT 062)

These fields follow the order of TpT's "Add a resource" form. Evergreen item: no season, any month of the school year.

**Files to attach**
- Resource (digital download): `{SLUG}.pdf`, {TOTAL_PAGES} pages, US Letter.
- Thumbnails, in this order: `cover.png`, `preview-1.png`, `preview-2.png`, `preview-3.png` (all 2000 × 2000).
- Preview file: `{SLUG}-PREVIEW.pdf`, 4 watermarked pages.

## 1. Title

```
{LISTING_TITLE}
```
({len(LISTING_TITLE)} characters; the limit is 80.) Plain search words first, no seasonal words.

## 2. Description

```
Rhythm Dictation, Levels 1-3 gives you 30 ready-to-teach rhythm dictation exercises for grades 3-8. Every exercise comes with a teacher script, a student page with blank bars and an answer key, so you can run a dictation with no audio and no prep. The script tells you the meter, the tempo in BPM, the count-in, how many times to perform the rhythm and exactly what to say and clap, in rhythm syllables (such as ta ti-ti ta shh) and counts (such as 1 + 2 3 4). Students listen, echo, audiate, write and check on a blank one-line staff with the barlines and time signature already printed.

Level 1 (grades 3-4) uses 4/4 with quarter notes, quarter rests, pairs of eighth notes and half notes in two-bar exercises. Level 2 (grades 4-6) adds 3/4, whole notes, dotted half notes and eighth-quarter-eighth syncopation in exercises of two to four bars. Level 3 (grades 6-8) adds 6/8 in groups of three eighths, sixteenth-note groups and dotted quarter plus eighth, in four-bar exercises. No audio is included: you perform each rhythm yourself from the script by clapping, tapping or playing it on any instrument.

WHAT'S INCLUDED ({TOTAL_PAGES} pages, PDF, US Letter)
• Cover (1 page)
• Teacher notes with levels, pacing, differentiation and standards (1 page)
• Scoring and assessment: a 2-1-0 scale for every bar and level totals (1 page)
• About rhythm dictation: the five steps and a worked example (1 page)
• Syllables and counting charts for 4/4, 3/4 and 6/8 (2 pages)
• Level 1: 10 teacher scripts, 10 student pages and 10 answer keys (6 pages)
• Level 2: 10 teacher scripts, 10 student pages and 10 answer keys (6 pages)
• Level 3: 10 teacher scripts, 10 student pages and 10 answer keys (6 pages)
• Progress tracker with a self-assessment checklist (1 page)
• Terms of use and credits (1 page)
Total: {TOTAL_PAGES} pages, 30 exercises.

HOW TO USE
Read the teacher script aloud and clap it: count in, then perform the syllables bar by bar the number of times the script says. Students echo the rhythm, audiate it, write it in the blank bars and check it with the answer key. Score each bar from 0 to 2 points. An exercise takes about eight minutes, so it works as a bell ringer, a warm-up or a quick assessment.

• Grades 3-8, three levels of 10 exercises each
• Meters 4/4, 3/4 and 6/8 on a one-line staff with a neutral clef
• Rhythm syllables and counts for every exercise
• Prints well in black and white

{DISCLOSURE}
```

## 3. Grades

TpT allows only 4 grade levels, so the form gets 4th, 5th, 6th and 7th. They sit in the middle of the 3-8 range and cover all three levels (Level 1 grades 3-4, Level 2 grades 4-6, Level 3 grades 6-8). The listing title and description say grades 3-8.

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

Paid. Preview PDF: about rhythm dictation (page {P_ABOUT}), Level 1 teacher scripts 1-5 (page 7), Level 2 student pages 11-15 (page 15) and the Level 3 answer key 21-25 (page 23), all watermarked.

## 9. Before you click publish

- Evergreen: no season check needed.
- Art: cover illustration (headphones) and the metronome picture are made with AI tools (the disclosure line covers them); notation, charts and icons are drawn in code.
- Open owner question: logo beside HUDSON BEAT (see tpt/STYLE.md).
"""


def tpt_json():
    return {"price": PRICE, "license_price": PRICE, "tax_code": "Other Digital Goods - No Physical Media", "grades": GRADES, "subjects": SUBJECTS, "tags": TAGS,
            "formats": ["PDF"], "pages": TOTAL_PAGES, "answer_key": "Included",
            "files": {"product": f"{SLUG}.pdf", "preview": f"{SLUG}-PREVIEW.pdf", "thumb1": "cover.png", "thumb2": "preview-1.png", "thumb3": "preview-2.png", "thumb4": "preview-3.png"}}


SHOT_PAGES = [P_ABOUT, 7, 15, 9, 11, 23, P_SCORE, P_TRACK]


def build():
    os.makedirs(BUILD, exist_ok=True)
    full = write("resource.html", html_doc(full_pages(), TITLE))
    prev = write("preview.html", html_doc(preview_pages(), "Preview"))
    render([{"html": full, "pdf": PDF}, {"html": prev, "pdf": PREVIEW_PDF}])
    for i in SHOT_PAGES:      # clean (unwatermarked) page shots from the product PDF
        subprocess.run(["pdftoppm", "-png", "-r", "150", "-f", str(i), "-l", str(i), "-singlefile", PDF, os.path.join(BUILD, f"pg{i}")], check=True)
    sq = [write("cover.html", cover_square()),
          write("p1.html", preview_square_1([f"pg{P_ABOUT}.png", "pg7.png", "pg15.png"])),
          write("p2.html", preview_square_2("pg9.png", "pg11.png")),
          write("p3.html", preview_square_3(["pg23.png", f"pg{P_SCORE}.png", f"pg{P_TRACK}.png"]))]
    render([{"html": h, "png": o, "width": 1000, "height": 1000, "scale": 2} for h, o in zip(sq, [COVER_PNG] + PREVIEW_PNGS)])
    with open(UPLOAD, "w") as fh:
        fh.write(upload_md())
    with open(TPT_JSON, "w") as fh:
        json.dump(tpt_json(), fh, indent=2)
        fh.write("\n")
    print(f"built {PDF}, {PREVIEW_PDF}, cover + 3 previews, UPLOAD.md, tpt.json")


if __name__ == "__main__" and "--check" not in sys.argv:
    build()


# ------------------------------------------------------------------ checks
NS = "{http://www.w3.org/2000/svg}"
SVG_RE = re.compile(r'<svg class="(?:ns|ic)".*?</svg>', re.S)
_GLYPH = {}


def f(el, k, d=0.0):
    return float(el.get(k, d))


def cp_of(el):
    return ord((el.text or "?")[0])


def glyph_box(cp):
    """Ink box of a Bravura glyph in staff spaces: (xmin, ymin, xmax, ymax), y up, origin at the glyph origin."""
    if not _GLYPH:
        from fontTools.ttLib import TTFont
        from fontTools.pens.boundsPen import BoundsPen
        font = TTFont(os.path.join(FONTS, "bravura.woff2"))
        gs, cm, upm = font.getGlyphSet(), font.getBestCmap(), font["head"].unitsPerEm
        for c in (G_WHOLE, G_HALF, G_HEAD, G_QREST, G_NEUTRAL, G_FLAG8, *TS_GLYPH.values()):
            bp = BoundsPen(gs)
            gs[cm[c]].draw(bp)
            _GLYPH[c] = tuple(v / upm * 4 for v in bp.bounds)
    return _GLYPH[cp]


def check_extent(root, label, errs):
    """Every drawn shape and glyph sits inside the viewBox with padding at least its stroke width (and at least 1 unit)."""
    vb = [float(x) for x in root.get("viewBox").split()]
    W, H_ = vb[2], vb[3]
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
        elif tag in ("polygon", "polyline"):
            nums = [float(x) for x in re.findall(r"-?\d+(?:\.\d+)?", el.get("points", ""))]
            xs, ys = nums[0::2], nums[1::2]
        elif tag == "text":
            if el.get("font-family") == "Bravura":
                S = f(el, "font-size") / 4
                x0, y0b, x1, y1b = glyph_box(cp_of(el))
                xs = [f(el, "x") + x0 * S, f(el, "x") + x1 * S]
                ys = [f(el, "y") - y1b * S, f(el, "y") - y0b * S]
            else:
                fs = f(el, "font-size")
                wd = len((el.text or "").strip()) * 0.56 * fs
                cx = f(el, "x")
                xs = [cx - wd / 2, cx + wd / 2]
                ys = [f(el, "y") - 0.75 * fs, f(el, "y") + 0.25 * fs]
        else:
            continue
        pad = max(sw, 1.0)
        if min(xs) - sw / 2 < pad - 1e-6 or min(ys) - sw / 2 < pad - 1e-6 or max(xs) + sw / 2 > W - pad + 1e-6 or max(ys) + sw / 2 > H_ - pad + 1e-6:
            errs.append(f"{label}: a {tag} (stroke {sw}) is closer to the viewBox edge than max(stroke, 1)")


def syl_rules(evs, comp):
    """Rhythm syllables of one bar worked out from the note values alone: [(syllable, first event, last event)], or (None, reason)."""
    out, i, n = [], 0, len(evs)
    D = lambda j: evs[j]["dur"]
    K = lambda j: evs[j]["kind"]
    while i < n:
        t = evs[i]["t"]
        if comp:
            if t % Fraction(3, 2) != 0:
                return None, "an event starts off a big beat"
            if K(i) != "n":
                return None, "rest in 6/8"
            if D(i) == Fraction(3, 2):
                out.append(("ta", i, i))
                i += 1
            elif D(i) == H and i + 2 < n and D(i + 1) == H and D(i + 2) == H:
                out.append(("ti-ti-ti", i, i + 2))
                i += 3
            elif D(i) == 1 and i + 1 < n and D(i + 1) == H:
                out.append(("ta-ti", i, i + 1))
                i += 2
            elif D(i) == H and i + 1 < n and D(i + 1) == 1:
                out.append(("ti-ta", i, i + 1))
                i += 2
            else:
                return None, f"no 6/8 pattern at {t}"
            continue
        if t.denominator != 1:
            return None, f"an event starts off the beat at {t}"
        d = D(i)
        if K(i) == "r":
            if d != 1:
                return None, "rest other than a quarter rest"
            out.append(("shh", i, i))
            i += 1
        elif d == 1:
            out.append(("ta", i, i))
            i += 1
        elif d in (2, 3, 4):
            out.append(("ta" + "-a" * (int(d) - 1), i, i))
            i += 1
        elif d == Fraction(3, 2):
            if not (i + 1 < n and D(i + 1) == H and K(i + 1) == "n"):
                return None, "dotted quarter not followed by an eighth"
            out.append(("tam-ti", i, i + 1))
            i += 2
        elif d == H:
            if i + 2 < n and D(i + 1) == 1 and D(i + 2) == H:
                out.append(("ti-ta-ti", i, i + 2))
                i += 3
            elif i + 1 < n and D(i + 1) == H:
                out.append(("ti-ti", i, i + 1))
                i += 2
            elif i + 2 < n and D(i + 1) == Q and D(i + 2) == Q:
                out.append(("ti-ti-ka", i, i + 2))
                i += 3
            else:
                return None, f"eighth note with no pattern at {t}"
        elif d == Q:
            if i + 3 < n and all(D(j) == Q for j in (i + 1, i + 2, i + 3)):
                out.append(("ti-ka-ti-ka", i, i + 3))
                i += 4
            elif i + 2 < n and D(i + 1) == Q and D(i + 2) == H:
                out.append(("ti-ka-ti", i, i + 2))
                i += 3
            else:
                return None, f"sixteenth note with no pattern at {t}"
        else:
            return None, f"unknown value {d}"
    return out, None


def read_staff(root, errs):
    """Re-read one staff svg from its geometry only. Returns {label, kind, uid, meter, nbars, bars:[{evs, syl, cnt, total}]} or None."""
    kind, uid = root.get("data-kind"), root.get("data-id")
    label = f"{kind} {uid}"
    S, y0 = f(root, "data-s"), f(root, "data-y0")
    hw, sw0 = HEAD_W * S, 0.13 * S
    res = {"label": label, "kind": kind, "uid": uid, "meter": None, "bars": []}
    sls = [el for el in root.iter(NS + "line") if el.get("class") == "sl"]
    if len(sls) != 1 or abs(f(sls[0], "y1") - y0) > 0.02 or abs(f(sls[0], "y2") - y0) > 0.02:
        errs.append(f"{label}: expected exactly one horizontal staff line")
        return None
    if f(sls[0], "stroke-width") < 0.1 * S:
        errs.append(f"{label}: staff line too thin")
    clefs = [t for t in root.iter(NS + "text") if t.get("class") == "clef"]
    tsd = sorted((f(t, "y"), cp_of(t)) for t in root.iter(NS + "text") if t.get("class") == "tsd")
    barl = sorted(f(l, "x1") for l in root.iter(NS + "line") if l.get("class") == "bar")
    fins = [r for r in root.iter(NS + "rect") if r.get("class") == "fin"]
    if kind in ("key", "blank"):
        if len(clefs) != 1 or cp_of(clefs[0]) != G_NEUTRAL or abs(f(clefs[0], "y") - y0) > 0.02:
            errs.append(f"{label}: neutral clef missing or off the line")
        if len(tsd) != 2 or tsd[0][1] not in TS_DIGIT or tsd[1][1] not in TS_DIGIT or abs(tsd[0][0] - (y0 - 1.25 * S)) > 0.02 or abs(tsd[1][0] - (y0 + 1.25 * S)) > 0.02:
            errs.append(f"{label}: time signature is not two digits around the line")
            return None
        res["meter"] = f"{TS_DIGIT[tsd[0][1]]}/{TS_DIGIT[tsd[1][1]]}"
        if res["meter"] not in METERS:
            errs.append(f"{label}: time signature {res['meter']} is not used in this product")
            return None
        if not barl or len(fins) != 1 or f(fins[0], "x") + f(fins[0], "width") / 2 <= barl[-1]:
            errs.append(f"{label}: barlines or the thick final barline missing")
            return None
        if any(abs(f(l, "y1") - (y0 - 2 * S)) > 0.02 or abs(f(l, "y2") - (y0 + 2 * S)) > 0.02 for l in root.iter(NS + "line") if l.get("class") == "bar"):
            errs.append(f"{label}: a barline does not span the staff")
    elif clefs or tsd or barl or fins:
        errs.append(f"{label}: symbol example should have no clef, time signature or barline")
    meter = res["meter"] or root.get("data-meter")
    comp = METERS[meter]["comp"]
    Lw = METERS[meter]["win"]
    beams = [(f(r, "x"), f(r, "x") + f(r, "width"), f(r, "y"), f(r, "height")) for r in root.iter(NS + "rect") if r.get("class") == "beam"]
    evs = []
    for g in root.iter(NS + "g"):
        if g.get("class") != "ev":
            continue
        heads = [t for t in g.iter(NS + "text") if t.get("class") == "head"]
        rests = [t for t in g.iter(NS + "text") if t.get("class") == "rest"]
        flags = [t for t in g.iter(NS + "text") if t.get("class") == "flag"]
        stems = [l for l in g.iter(NS + "line") if l.get("class") == "stem"]
        dots = [c for c in g.iter(NS + "circle") if c.get("class") == "dot"]
        if rests:
            r = rests[0]
            if len(rests) != 1 or heads or stems or flags or dots or cp_of(r) != G_QREST or abs(f(r, "y") - y0) > 0.02:
                errs.append(f"{label}: rest is not a single quarter rest on the line")
                continue
            evs.append({"kind": "r", "dur": Fraction(1), "x": f(r, "x") + REST_W * S / 2, "l": f(r, "x"), "r": f(r, "x") + REST_W * S, "lv": 0})
            continue
        if len(heads) != 1:
            errs.append(f"{label}: an event without exactly one head")
            continue
        hd = heads[0]
        gp = cp_of(hd)
        if abs(f(hd, "y") - y0) > 0.02 or gp not in (G_WHOLE, G_HALF, G_HEAD):
            errs.append(f"{label}: notehead glyph or position wrong")
            continue
        left = f(hd, "x")
        wid = WHOLE_W * S if gp == G_WHOLE else hw
        e = {"kind": "n", "head": gp, "x": left + wid / 2, "l": left, "r": left + wid, "lv": 0, "flag": False, "dot": False}
        if gp == G_WHOLE:
            if stems or flags or dots:
                errs.append(f"{label}: a whole note has a stem, flag or dot")
            e["dur"] = Fraction(4)
            e["sx"] = None
            evs.append(e)
            continue
        if len(stems) != 1:
            errs.append(f"{label}: a note without exactly one stem")
            continue
        sm = stems[0]
        sx, y1, y2, swd = f(sm, "x1"), f(sm, "y1"), f(sm, "y2"), f(sm, "stroke-width")
        if abs(sx - (left + hw - swd / 2)) > 0.03 * S or abs(f(sm, "x2") - sx) > 0.01 or abs(y1 - (y0 - STEM_X * S)) > 0.03 * S or y2 >= y1:
            errs.append(f"{label}: stem is not on the RIGHT edge of its head going up")
        if y1 - y2 < 3.0 * S - 0.01:
            errs.append(f"{label}: stem shorter than 3 staff spaces")
        e.update({"sx": sx, "swd": swd, "tip": y2})
        if len(flags) > 1 or (flags and (cp_of(flags[0]) != G_FLAG8 or abs(f(flags[0], "x") - (sx - swd / 2)) > 0.05 * S or abs(f(flags[0], "y") - y2) > 0.05 * S)):
            errs.append(f"{label}: flag glyph or position wrong")
        if flags:
            e["flag"] = True
            e["lv"] += 1
            e["r"] = max(e["r"], f(flags[0], "x") + glyph_box(G_FLAG8)[2] * S)
        if len(dots) > 1:
            errs.append(f"{label}: more than one dot")
        if dots:
            c = dots[0]
            e["dot"] = True
            if abs(f(c, "cx") - (left + hw + 0.55 * S)) > 0.05 * S or abs(f(c, "cy") - (y0 - 0.5 * S)) > 0.03 * S or abs(f(c, "r") - 0.2 * S) > 0.02 * S:
                errs.append(f"{label}: dot is not in the space above the line, right of the head")
            e["r"] = max(e["r"], f(c, "cx") + f(c, "r"))
        evs.append(e)
    evs.sort(key=lambda e: e["x"])
    notes = [e for e in evs if e["kind"] == "n" and e.get("sx") is not None]
    # beams: level by distance below the stem tip; each joins >= 2 neighbouring stems from the first stem's left edge to the last stem's right edge
    lvl_sets = {1: [], 2: []}
    for bx1, bx2, by, bh in beams:
        cov = [e for e in notes if bx1 - 0.02 <= e["sx"] - e["swd"] / 2 and e["sx"] + e["swd"] / 2 <= bx2 + 0.02]
        if len(cov) < 2:
            errs.append(f"{label}: a beam joins fewer than two stems")
            continue
        top = min(e["tip"] for e in cov)
        lvl = 1 if abs(by - top) < 0.03 else 2 if abs(by - (top + 0.75 * S)) < 0.03 else 0
        if lvl == 0 or abs(bh - 0.5 * S) > 0.03:
            errs.append(f"{label}: beam at an unexpected height")
            continue
        if abs(bx1 - (cov[0]["sx"] - cov[0]["swd"] / 2)) > 0.03 or abs(bx2 - (cov[-1]["sx"] + cov[-1]["swd"] / 2)) > 0.03:
            errs.append(f"{label}: beam does not end exactly at its outer stems")
        if lvl == 1 and any(abs(e["tip"] - by) > 0.03 for e in cov):
            errs.append(f"{label}: a stem does not end at its beam")
        idx = [evs.index(e) for e in cov]
        if idx != list(range(idx[0], idx[0] + len(idx))):
            errs.append(f"{label}: a note sits under a beam without being joined to it")
        for e in cov:
            e["lv"] += 1
            e[f"b{lvl}"] = len(lvl_sets[lvl])
        lvl_sets[lvl].append(frozenset(id(e) for e in cov))
    for s2 in lvl_sets[2]:
        if not any(s2 <= s1 for s1 in lvl_sets[1]):
            errs.append(f"{label}: a second beam is not inside a first beam")
    # note values from the glyph, flags/beams and the dot
    for e in evs:
        if e["kind"] != "n" or e["head"] == G_WHOLE:
            continue
        if e["head"] == G_HALF:
            e["dur"] = Fraction(2)
            if e["lv"]:
                errs.append(f"{label}: half note with a flag or beam")
        else:
            if e["lv"] > 2:
                errs.append(f"{label}: more than two beams or flags on a stem")
            e["dur"] = Fraction(1, 2 ** min(e["lv"], 2))
        if e["dot"]:
            if e["lv"]:
                errs.append(f"{label}: a dotted note with a flag or beam")
            e["dur"] = e["dur"] * Fraction(3, 2)
    if any("dur" not in e for e in evs):
        return None
    # no ink overlaps the next event
    for a, b in zip(evs, evs[1:]):
        if a["r"] + 0.15 * S > b["l"]:
            errs.append(f"{label}: neighbouring notes or their flags and dots crowd or overlap")
    # bars
    if kind == "sym":
        groups = [evs]
    else:
        groups = [[] for _ in barl]
        for e in evs:
            k = sum(1 for bx in barl if bx < e["x"])
            if k >= len(barl):
                errs.append(f"{label}: a note sits after the last barline")
                return None
            groups[k].append(e)
            for bx in barl:
                if e["l"] - 0.3 * S < bx < e["r"] + 0.3 * S:
                    errs.append(f"{label}: a note touches a barline")
        if kind == "blank" and evs:
            errs.append(f"{label}: a blank bar has notes in it")
    for gi, ge in enumerate(groups):
        t = Fraction(0)
        for e in ge:
            e["t"] = t
            t += e["dur"]
        bar = {"evs": ge, "total": t}
        if kind in ("key", "blank"):
            if t != METERS[meter]["barlen"] and kind == "key":
                errs.append(f"{label}: bar {gi + 1} adds up to {t} beats, the time signature {meter} needs {METERS[meter]['barlen']}")
        if kind != "blank":
            sy, why = syl_rules(ge, comp)
            if sy is None:
                errs.append(f"{label}: bar {gi + 1}: {why}")
                bar["syl"] = None
            else:
                bar["syl"] = sy
                bar["cnt"] = counts_of_bar(ge, meter, None if kind == "key" else math.ceil(t / (Lw if comp else 1)) * (Lw if comp else 1))
            # long notes and half notes sit where the meter allows
            for e in ge:
                if e["kind"] == "n" and not comp:
                    if e["dur"] == 2 and e["t"] not in ((0, 2) if meter == "4/4" else (0, 1)):
                        errs.append(f"{label}: half note on an off-beat position")
                    if e["dur"] in (3, 4) and e["t"] != 0:
                        errs.append(f"{label}: long note not on beat 1")
            # beaming: runs of eighths and sixteenths inside one beat are joined by one beam; a lone one carries a flag
            runs, cur = [], []
            for i, e in enumerate(ge):
                if e["kind"] == "n" and e["dur"] < 1:
                    if cur and ge[cur[-1]]["t"] // Lw == e["t"] // Lw:
                        cur.append(i)
                        continue
                    if cur:
                        runs.append(cur)
                    cur = [i]
                else:
                    if cur:
                        runs.append(cur)
                    cur = []
                    if e["kind"] == "n" and (e["lv"] or e["flag"]):
                        errs.append(f"{label}: a note of a quarter or longer has a flag or beam")
            if cur:
                runs.append(cur)
            for r in runs:
                if len(r) == 1:
                    if not ge[r[0]]["flag"] or ge[r[0]].get("b1") is not None:
                        errs.append(f"{label}: a lone eighth note must carry a flag and no beam")
                else:
                    ids = {ge[i].get("b1") for i in r}
                    if None in ids or len(ids) != 1 or any(ge[i]["flag"] for i in r):
                        errs.append(f"{label}: a run of eighths or sixteenths in one beat is not joined by one beam")
                    sixteenth = [i for i in r if ge[i]["dur"] == Q]
                    run16, c16 = [], []
                    for i in r + [None]:
                        if i is not None and ge[i]["dur"] == Q:
                            c16.append(i)
                        else:
                            if c16:
                                run16.append(c16)
                            c16 = []
                    for c16 in run16:
                        ids2 = {ge[i].get("b2") for i in c16}
                        if len(c16) < 2 or None in ids2 or len(ids2) != 1:
                            errs.append(f"{label}: sixteenth notes are not joined by a second beam")
            if comp and kind != "sym":
                if any(e["kind"] == "n" and e["dur"] == H for e in ge) and not all(len(r) in (1, 3) or ge[r[0]]["dur"] == H for r in runs):
                    errs.append(f"{label}: 6/8 eighths are not beamed in groups of three")
        res["bars"].append(bar)
    res["nbars"] = len(groups)
    # labels on the key staves
    cnt = [(f(t, "x"), (t.text or "").strip(), int(t.get("data-bar"))) for t in root.iter(NS + "text") if t.get("class") == "cnt"]
    sy = [(f(t, "x"), (t.text or "").strip(), int(t.get("data-bar"))) for t in root.iter(NS + "text") if t.get("class") == "syl"]
    if kind == "key":
        for gi, bar in enumerate(res["bars"]):
            if bar.get("syl") is None:
                continue
            got_s = [(x, tx) for x, tx, b in sy if b == gi + 1]
            if [tx for _, tx in got_s] != [n for n, _a, _b in bar["syl"]]:
                errs.append(f"{label}: bar {gi + 1} printed syllables {[tx for _, tx in got_s]} differ from the notation {[n for n, _a, _b in bar['syl']]}")
            else:
                for (x, _tx), (n, a, b2) in zip(got_s, bar["syl"]):
                    if abs(x - (bar["evs"][a]["x"] + bar["evs"][b2]["x"]) / 2) > 1.0:
                        errs.append(f"{label}: syllable '{n}' is not centered under its notes")
            got_c = [(x, tx) for x, tx, b in cnt if b == gi + 1]
            want = bar["cnt"]
            if [tx for _, tx in got_c] != [tx for _t, tx, _o in want]:
                errs.append(f"{label}: bar {gi + 1} printed counts {[tx for _, tx in got_c]} differ from the notation {[tx for _t, tx, _o in want]}")
            else:
                at = {e["t"]: e for e in bar["evs"]}
                for (x, _tx), (tt, _t2, onset) in zip(got_c, want):
                    if onset and abs(x - at[tt]["x"]) > 0.6:
                        errs.append(f"{label}: a count is not under its note")
            xs = [x for x, _ in got_c]
            if xs != sorted(xs):
                errs.append(f"{label}: counts out of order")
    elif cnt or sy:
        errs.append(f"{label}: unexpected labels")
    check_extent(root, label, errs)
    res["meter"] = meter
    return res


def blocks_of(html, tag):
    out = {}
    for m in re.finditer(rf'<div class="{tag}" data-ex="(\d+)"(.*?)<!--/{tag}-->', html, re.S):
        out[int(m.group(1))] = m.group(2)
    return out


def verify_html():
    errs = []
    html = open(os.path.join(BUILD, "resource.html")).read()
    svgs = SVG_RE.findall(html)
    res, icons, uids = {}, [], []
    for sv in svgs:
        root = ET.fromstring(sv)
        if root.get("class") == "ic":
            icons.append(root.get("data-name"))
            check_extent(root, f"icon {root.get('data-name')}", errs)
            continue
        uid = root.get("data-id")
        if uid in res:
            errs.append(f"staff id {uid} appears twice")
        r = read_staff(root, errs)
        if r is not None:
            res[uid] = r
        uids.append(uid)
    if sorted(icons) != sorted(STEP_ICONS):
        errs.append(f"step icons {icons}")
    sc, sp, kb = blocks_of(html, "sc"), blocks_of(html, "sp"), blocks_of(html, "kb")
    for nm, d in (("script", sc), ("student", sp), ("key", kb)):
        if sorted(d) != list(range(1, 31)):
            errs.append(f"{nm} blocks found for exercises {sorted(d)}, expected 1-30")
    if errs and (len(sc) != 30 or len(sp) != 30 or len(kb) != 30):
        return errs
    # ---- per exercise: key notation is the truth
    sig, levels = {}, {1: set(), 2: set(), 3: set()}
    per_level = {1: 0, 2: 0, 3: 0}
    bars_by_ex = {}
    for e in EXS:
        n = e["num"]
        K, B = res.get(f"K{n:02d}"), res.get(f"B{n:02d}")
        if K is None or B is None:
            errs.append(f"exercise {n}: key or student staff missing")
            continue
        if K["meter"] != e["meter"]:
            errs.append(f"exercise {n}: key time signature {K['meter']}, data says {e['meter']}")
        if any(b.get("syl") is None for b in K["bars"]):
            continue
        syl_bars = [[x[0] for x in b["syl"]] for b in K["bars"]]
        bars_by_ex[n] = len(syl_bars)
        if syl_bars != e["bars"]:
            errs.append(f"exercise {n}: notation reads {syl_bars} but the data says {e['bars']}")
        # student page: same time signature, same number of bars, nothing written
        if B["meter"] != K["meter"] or B["nbars"] != K["nbars"]:
            errs.append(f"exercise {n}: student page is {B['meter']} with {B['nbars']} bars, key is {K['meter']} with {K['nbars']}")
        # level content
        lv = level_of(n)
        names = {x for b in syl_bars for x in b}
        comp = METERS[K["meter"]]["comp"]
        if K["meter"] not in LEVEL_METERS[lv]:
            errs.append(f"exercise {n}: meter {K['meter']} not allowed in Level {lv}")
        lo, hi = LEVEL_BARS[lv]
        if not lo <= K["nbars"] <= hi:
            errs.append(f"exercise {n}: {K['nbars']} bars not allowed in Level {lv}")
        if comp:
            if lv != 3 or not names <= COMP_ALLOWED:
                errs.append(f"exercise {n}: 6/8 values outside Level 3")
        else:
            if not names <= ALLOWED[lv]:
                errs.append(f"exercise {n}: values {sorted(names - ALLOWED[lv])} are not allowed in Level {lv}")
            if lv == 2 and not names & L2_NEW:
                errs.append(f"exercise {n}: a Level 2 exercise with no Level 2 value")
            if lv == 3 and not names & L3_NEW_SIMPLE:
                errs.append(f"exercise {n}: a Level 3 exercise with no Level 3 value")
        if lv == 1 and (names & (L2_NEW | L3_NEW_SIMPLE)):
            errs.append(f"exercise {n}: Level 1 uses a later value")
        key = (K["meter"], tuple(tuple(b) for b in syl_bars))
        if key in sig:
            errs.append(f"exercise {n} is identical to exercise {sig[key]}")
        sig[key] = n
        per_level[lv] += 1
        # script text
        blk = sc.get(n, "")
        mt = re.search(r'<span class="mt">([^<]+)</span>', blk)
        nb = re.search(r'<b class="nb">(\d+)</b> bars · <b class="bpm">(\d+)</b> BPM \(([a-z ]+) = (\d+)\)', blk)
        ci = re.search(r'<b class="ci">([^<]+)</b>', blk)
        sy = {int(a): b for a, b in re.findall(r'<span class="sylbar" data-bar="(\d+)">([^<]+)</span>', blk)}
        ct = {int(a): b for a, b in re.findall(r'<span class="cntbar" data-bar="(\d+)">([^<]+)</span>', blk)}
        pl = re.search(r'<span class="plays">(\d+)</span>', blk)
        sc2 = re.search(r'<span class="secs">(\d+)</span>', blk)
        if not (mt and nb and ci and pl and sc2):
            errs.append(f"exercise {n}: script block incomplete")
            continue
        if mt.group(1) != K["meter"] or int(nb.group(1)) != K["nbars"]:
            errs.append(f"exercise {n}: script says {mt.group(1)} and {nb.group(1)} bars, key is {K['meter']} with {K['nbars']}")
        unit = "dotted quarter note" if comp else "quarter note"
        if nb.group(3) != unit or nb.group(2) != nb.group(4) or int(nb.group(2)) != e["bpm"] or not 50 <= int(nb.group(2)) <= 120:
            errs.append(f"exercise {n}: tempo text wrong")
        if ci.group(1) != {"4/4": "1 2 3 4", "3/4": "1 2 3", "6/8": "1 2 1 2"}[K["meter"]]:
            errs.append(f"exercise {n}: count-in does not fit {K['meter']}")
        if sorted(sy) != list(range(1, K["nbars"] + 1)) or sorted(ct) != sorted(sy):
            errs.append(f"exercise {n}: script bars {sorted(sy)} do not match the key's {K['nbars']} bars")
        else:
            for bi, bar in enumerate(K["bars"]):
                want_s = " ".join(x[0] for x in bar["syl"])
                want_c = " ".join(tx for _t, tx, _o in bar["cnt"])
                if sy[bi + 1] != want_s:
                    errs.append(f"exercise {n} bar {bi + 1}: script says '{sy[bi + 1]}', the notation reads '{want_s}'")
                if ct[bi + 1] != want_c:
                    errs.append(f"exercise {n} bar {bi + 1}: script counts '{ct[bi + 1]}', the notation gives '{want_c}'")
        if int(pl.group(1)) != (3 if K["nbars"] <= 2 else 4) or int(sc2.group(1)) != 30 * K["nbars"]:
            errs.append(f"exercise {n}: plays or writing time inconsistent with {K['nbars']} bars")
        foc = re.search(r'<span class="foc">([^<]+)</span>', blk)
        if not foc:
            errs.append(f"exercise {n}: no 'Listen for' line")
        # student block and key block
        sblk, kblk = sp.get(n, ""), kb.get(n, "")
        if f'data-meter="{K["meter"]}"' not in sblk or f'data-bars="{K["nbars"]}"' not in sblk or f"{K['nbars']} bars" not in sblk:
            errs.append(f"exercise {n}: student block meter or bar count differs from the key")
        mx = re.search(r'<span class="mx">(\d+)</span>', sblk)
        if not mx or int(mx.group(1)) != 2 * K["nbars"]:
            errs.append(f"exercise {n}: student score maximum is not 2 points a bar")
        km = re.search(r'(\d+) bars · (\d+) BPM · (\d+) points', kblk)
        if not km or int(km.group(1)) != K["nbars"] or int(km.group(2)) != e["bpm"] or int(km.group(3)) != 2 * K["nbars"]:
            errs.append(f"exercise {n}: key header bars, BPM or points wrong")
        if f'data-meter="{K["meter"]}"' not in kblk or f'data-bars="{K["nbars"]}"' not in kblk:
            errs.append(f"exercise {n}: key block attributes differ from its staff")
        for nm, blkx in (("script", blk), ("student", sblk), ("key", kblk)):
            if f"Exercise {n}<" not in blkx:
                errs.append(f"exercise {n}: {nm} block lacks its exercise number")
        for nm, blkx in (("student", sblk),):
            if blkx.count('class="cb"') != 5:
                errs.append(f"exercise {n}: student page needs five checkboxes")
    if per_level != {1: 10, 2: 10, 3: 10} or len(sig) != 30:
        errs.append(f"exercise counts per level {per_level}, distinct {len(sig)}")
    # ---- page placement of blocks
    for m in re.finditer(r'<section class="page" data-page="(\d+)">(.*?)</section>', html, re.S):
        pg, body = int(m.group(1)), m.group(2)
        for tag, fn in (("sc", p_script), ("sp", p_student), ("kb", p_key)):
            nums = [int(x) for x in re.findall(rf'<div class="{tag}" data-ex="(\d+)"', body)]
            if nums and any(fn(x) != pg for x in nums):
                errs.append(f"page {pg}: holds {tag} blocks {nums} that belong on other pages")
            if nums and len(nums) != 5:
                errs.append(f"page {pg}: {len(nums)} {tag} blocks, expected 5")
        if pg not in PAGE_NAMES or PAGE_NAMES[pg] not in body:
            errs.append(f"page {pg}: its name is not on the page")
    # ---- charts
    rows = re.findall(r'<tr data-say="([^"]+)" data-meter="([^"]+)">(.*?)</tr>', html, re.S)
    if len(rows) != len(CHART_SIMPLE) + len(CHART_COMP):
        errs.append(f"chart rows: {len(rows)}")
    for say, meter, body in rows:
        sv = re.search(r'<svg class="ns".*?</svg>', body, re.S)
        r = read_staff(ET.fromstring(sv.group(0)), errs) if sv else None
        if r is None or r["bars"][0].get("syl") is None:
            errs.append(f"chart row {say}: notation not readable")
            continue
        bar = r["bars"][0]
        got = [x[0] for x in bar["syl"]]
        if got != [say]:
            errs.append(f"chart row '{say}': the notation reads {got}")
        txt = re.sub(r"<[^>]+>", "|", body)
        cells = [c.strip() for c in txt.split("|") if c.strip()]
        win = METERS[meter]["win"]
        want_len = bar["total"] / win
        lenc = next((c for c in cells if re.fullmatch(r"\d+ beats?", c)), None)
        if want_len.denominator != 1 or lenc != f"{int(want_len)} beat" + ("" if want_len == 1 else "s"):
            errs.append(f"chart row '{say}': printed length {lenc}, notation adds up to {want_len} beats")
        cc = count_text(bar["evs"], meter, math.ceil(bar["total"] / win) * win)
        if cc not in cells:
            errs.append(f"chart row '{say}': printed count differs from '{cc}'")
        names = set(x for x in (say,))
        lvc = next((c for c in cells if c.startswith("Level ")), "")
        simple = meter != "6/8"
        want_lv = "Level 3" if not simple else "Level 1" if say in L1_VALUES else "Level 2" if say in L2_NEW else "Level 3"
        if lvc != want_lv:
            errs.append(f"chart row '{say}': level label {lvc}, expected {want_lv}")
    # ---- worked example, your turn, meter examples
    ex = res.get("EXAMPLE")
    if not ex or ex["bars"][0]["total"] != 4 or [x[0] for x in ex["bars"][0]["syl"]] != EXAMPLE_BAR:
        errs.append("worked example does not add up to 4 beats or differs from its text")
    yt = res.get("YOURTURN")
    if not yt or yt["nbars"] != 2 or yt["meter"] != "4/4":
        errs.append("'your turn' staff is not two bars of 4/4")
    for m, toks, uid, _t in METER_EXAMPLES:
        r = res.get(uid)
        if not r or r["meter"] != m or r["bars"][0]["total"] != METERS[m]["barlen"]:
            errs.append(f"meter example {m} wrong")
    # ---- scoring page and tracker use the parsed bar counts
    total_pts = 0
    for k in (1, 2, 3):
        bars = sum(bars_by_ex.get(e["num"], 0) for e in LEVEL_EXS[k])
        pts = 2 * bars
        total_pts += pts
        m = re.search(rf'<tr data-lv="{k}"><td><b>Level {k}</b></td><td class="tb">(\d+)</td><td class="tp">(\d+)</td><td>(\d+) to (\d+)</td><td>(\d+) to (\d+)</td><td>0 to (\d+)</td></tr>', html)
        if not m:
            errs.append(f"scoring table row for Level {k} not found")
            continue
        vals = [int(x) for x in m.groups()]
        sec, dev = math.ceil(0.9 * pts), math.ceil(0.7 * pts)
        if vals != [bars, pts, sec, pts, dev, sec - 1, dev - 1]:
            errs.append(f"scoring table Level {k}: {vals}, expected {[bars, pts, sec, pts, dev, sec - 1, dev - 1]}")
        t = re.search(rf'<table class="trk" data-lv="{k}">(.*?)</table>', html, re.S)
        if not t:
            errs.append(f"tracker table for Level {k} missing")
            continue
        trs = re.findall(r'<tr data-ex="(\d+)"><td>\d+</td><td>([^<]+)</td><td>____ / <span class="mx">(\d+)</span></td></tr>', t.group(1))
        want_ids = [e["num"] for e in LEVEL_EXS[k]]
        if [int(a) for a, _b, _c in trs] != want_ids:
            errs.append(f"tracker Level {k}: exercises {[a for a, _b, _c in trs]}")
        for a, mt_, mx_ in trs:
            if int(mx_) != 2 * bars_by_ex.get(int(a), -1) or mt_ != res[f"K{int(a):02d}"]["meter"]:
                errs.append(f"tracker exercise {a}: meter or points differ from the key")
        lt = re.search(r'<b class="lt">(\d+)</b>', t.group(1))
        if not lt or int(lt.group(1)) != pts:
            errs.append(f"tracker Level {k}: total differs from {pts}")
    tt = re.search(r'<span class="tt">(\d+)</span>', html)
    if not tt or int(tt.group(1)) != total_pts or total_pts != TOTAL_POINTS:
        errs.append(f"tracker grand total differs from {total_pts}")
    # ---- element counts
    n_key = sum(1 for u in uids if re.fullmatch(r"K\d\d", u))
    n_blank = sum(1 for u in uids if re.fullmatch(r"B\d\d", u))
    if (n_key, n_blank) != (30, 30):
        errs.append(f"key staves {n_key}, student staves {n_blank}")
    # ---- theory sentences
    text = " ".join(re.sub(r"<[^>]+>", " ", html).split())
    for need in ("a quarter note gets one beat", "each is half a beat", "each is a quarter of a beat", "A dot adds half of the note's value",
                 "A dotted half note lasts 3 beats", "a dotted quarter note lasts 1 and a half beats", "Four sixteenth notes with two beams",
                 "6/8 is a compound meter because each beat divides into three", "beamed in groups of three", "six eighth notes in a bar",
                 "which fills one bar of 4/4", "A rest is silence"):
        if need.lower() not in text.lower():
            errs.append(f"missing theory sentence: {need}")
    return errs


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
    const p = await b.newPage({ viewport: { width: 1000, height: 1056 }, deviceScaleFactor: 1 });
    await p.goto(url.pathToFileURL(f).href, { waitUntil: 'load' });
    await p.evaluate(() => document.fonts.ready);
    const r = await p.evaluate(() => {
      const res = [];
      const BOX = '.sc, .sp, .kb, .box, .step, .exbox, .top, .nd, .doc table, .trk, .cols, .stp, .doc p, .doc ul';
      document.querySelectorAll('.page').forEach((pg, i) => {
        const pr = pg.getBoundingClientRect();
        const ft = pg.querySelector('.foot');
        if (pg.scrollHeight > pg.clientHeight + 1) res.push(`page ${i + 1}: content overflows the page`);
        if (!ft) return;
        const ftop = ft.getBoundingClientRect().top;
        const skip = el => ft.contains(el) || el.closest('.wm');
        const boxes = [];
        pg.querySelectorAll(BOX + ', svg, img').forEach(el => {
          if (skip(el)) return;
          const r = el.getBoundingClientRect();
          if (r.height === 0) return;
          if (r.bottom > ftop - 8) res.push(`page ${i + 1}: ${el.tagName}.${el.getAttribute('class')} bottom ${(r.bottom - ftop).toFixed(1)}px vs footer rule (needs <= -8)`);
          if (r.right > pr.right - 0.35 * 96 + 0.5 || r.left < pr.left + 0.35 * 96 - 0.5) res.push(`page ${i + 1}: ${el.tagName}.${el.getAttribute('class')} too close to the page edge`);
          if (el.matches('.sc, .sp, .kb, .box, .step, .exbox')) boxes.push([el, r]);
        });
        pg.querySelectorAll('*').forEach(el => {
          if (skip(el) || el.children.length || !(el.textContent || '').trim()) return;
          if (el.closest('svg')) return;
          const r = el.getBoundingClientRect();
          if (r.height && r.bottom > ftop - 8) res.push(`page ${i + 1}: text "${el.textContent.trim().slice(0, 30)}" ends ${(r.bottom - ftop).toFixed(1)}px from the footer rule`);
        });
        for (let a = 0; a < boxes.length; a++) for (let c = a + 1; c < boxes.length; c++) {
          const A = boxes[a][1], C = boxes[c][1];
          if (boxes[a][0].contains(boxes[c][0]) || boxes[c][0].contains(boxes[a][0])) continue;
          const gx = Math.max(A.left, C.left) - Math.min(A.right, C.right);
          const gy = Math.max(A.top, C.top) - Math.min(A.bottom, C.bottom);
          if (gx < 8 && gy < 8) res.push(`page ${i + 1}: two boxes lack a gutter of 8px`);
        }
        pg.querySelectorAll('.sc, .sp, .kb, .box, .step, .exbox').forEach(bx => {
          if (bx.scrollWidth > bx.clientWidth + 1 || bx.scrollHeight > bx.clientHeight + 1) res.push(`page ${i + 1}: content overflows a ${bx.className} box`);
          const br = bx.getBoundingClientRect();
          bx.querySelectorAll('svg').forEach(sv => {
            const s = sv.getBoundingClientRect();
            if (s.left < br.left + 4 || s.right > br.right - 4 || s.top < br.top + 2 || s.bottom > br.bottom - 2) res.push(`page ${i + 1}: a drawing is too close to its box edge`);
          });
        });
        pg.querySelectorAll('.syt td').forEach(td => {
          const br = td.getBoundingClientRect();
          td.querySelectorAll('svg').forEach(sv => {
            const s = sv.getBoundingClientRect();
            if (s.left < br.left + 2 || s.right > br.right - 2 || s.top < br.top + 1 || s.bottom > br.bottom - 1) res.push(`page ${i + 1}: a chart drawing is too close to its cell edge`);
          });
        });
        pg.querySelectorAll('.sylbar, .cntbar').forEach(el => {
          const lh = parseFloat(getComputedStyle(el).lineHeight);
          if (el.getBoundingClientRect().height > lh * 1.4) res.push(`page ${i + 1}: script line wraps: "${el.textContent.slice(0, 30)}"`);
        });
        pg.querySelectorAll('svg.ns').forEach(sv => {
          const vb = sv.viewBox.baseVal;
          const texts = [...sv.querySelectorAll('text')].filter(t => t.getAttribute('font-family') !== 'Bravura').map(t => ({ t, b: t.getBBox() }));
          texts.forEach(({ t, b }) => {
            if (b.x < 1 || b.y < 1 || b.x + b.width > vb.width - 1 || b.y + b.height > vb.height - 1) res.push(`page ${i + 1}: svg text "${t.textContent}" outside its drawing`);
          });
          for (let a = 0; a < texts.length; a++) for (let c = a + 1; c < texts.length; c++) {
            const A = texts[a].b, C = texts[c].b;
            if (A.x < C.x + C.width + 0.8 && C.x < A.x + A.width + 0.8 && A.y < C.y + C.height && C.y < A.y + A.height) res.push(`page ${i + 1}: labels "${texts[a].t.textContent}" and "${texts[c].t.textContent}" overlap`);
          }
        });
        pg.querySelectorAll('.doc p, .doc li').forEach(el => {
          if (el.classList.contains('small')) return;
          const range = document.createRange(); range.selectNodeContents(el);
          const rects = [...range.getClientRects()].filter(q => q.width > 1);
          const lines = {};
          rects.forEach(q => { const k = Math.round(q.top / 3); lines[k] = lines[k] ? [Math.min(lines[k][0], q.left), Math.max(lines[k][1], q.right)] : [q.left, q.right]; });
          const ks = Object.keys(lines).map(Number).sort((a, b) => a - b);
          if (ks.length >= 2) {
            const last = lines[ks[ks.length - 1]];
            const w = el.getBoundingClientRect().width;
            if (last[1] - last[0] < 0.12 * w && el.innerText.trim().split(/\s+/).length > 6) res.push(`page ${i + 1}: short last line in "${el.innerText.trim().slice(0, 40)}..."`);
          }
        });
        let maxb = 0;
        pg.querySelectorAll('*').forEach(el => { if (skip(el)) return; const r = el.getBoundingClientRect(); if (r.height > 0 && r.width > 0 && ((el.children.length === 0 && ((el.textContent || '').trim() || el.matches('svg, img'))) || el.matches('.sc, .sp, .kb, .box, table'))) maxb = Math.max(maxb, r.bottom); });
        if (i > 0 && ftop - maxb > 105) res.push(`page ${i + 1}: blank band of ${(ftop - maxb).toFixed(0)}px above the footer (over 10% of the page)`);
      });
      document.querySelectorAll('.sq').forEach((sq, i) => {
        const sr = sq.getBoundingClientRect();
        const band = sq.querySelector('.band');
        const btop = band.getBoundingClientRect().top;
        const shots = [];
        sq.querySelectorAll('.shot').forEach(sh => {
          const r = sh.getBoundingClientRect();
          shots.push(r);
          if (r.left < sr.left + 24 || r.right + 8 > sr.right - 24) res.push(`square ${i + 1}: a page shot is too close to the side edge`);
          if (r.bottom + 8 > btop - 8) res.push(`square ${i + 1}: a page shot shadow is within 8px of the band`);
        });
        for (let a = 0; a < shots.length; a++) for (let c = a + 1; c < shots.length; c++) if (shots[a].right + 8 + 8 > shots[c].left && shots[a].left < shots[c].left && shots[a].bottom > shots[c].top) res.push(`square ${i + 1}: page shots lack a gutter`);
        sq.querySelectorAll('.lbl, .lbl span, .pill, .sub, .hd').forEach(el => {
          const r = el.getBoundingClientRect();
          if (r.bottom > btop - 8) res.push(`square ${i + 1}: text "${el.textContent.trim().slice(0, 24)}" within 8px of the band`);
          if (r.left < sr.left + 24 || r.right > sr.right - 24) res.push(`square ${i + 1}: text "${el.textContent.trim().slice(0, 24)}" too close to the side edge`);
        });
        sq.querySelectorAll('.pill').forEach(el => { if (el.scrollWidth > el.clientWidth + 1) res.push(`square ${i + 1}: pill text overflows`); });
        const sh = sq.querySelectorAll('.shot img');
        sh.forEach(im => { if (!im.complete || im.naturalWidth === 0) res.push(`square ${i + 1}: an image did not load`); });
      });
      document.querySelectorAll('.cover').forEach((pg, i) => {
        const pr = pg.getBoundingClientRect();
        pg.querySelectorAll('.ctitle .b, .cband, .ctitle .c, img').forEach(el => {
          const r = el.getBoundingClientRect();
          if (r.left < pr.left + 0.45 * 96 || r.right > pr.right - 0.45 * 96) res.push(`cover: ${el.className || el.tagName} too close to the side edge`);
        });
        const kids = [...pg.children].map(c => c.getBoundingClientRect());
        for (let a = 0; a < kids.length - 1; a++) if (kids[a].bottom + 8 > kids[a + 1].top) res.push('cover: blocks lack a gutter');
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

ALONE_JS = r"""
const { chromium } = require('playwright');
const url = require('url');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 900, height: 600 }, deviceScaleFactor: 4 });
  await p.goto(url.pathToFileURL(process.argv[2]).href, { waitUntil: 'load' });
  await p.evaluate(() => document.fonts.ready);
  const hs = await p.$$('svg');
  let n = 0;
  for (const h of hs) { await h.screenshot({ path: process.argv[3] + '/a' + String(n++).padStart(4, '0') + '.png', omitBackground: true }); }
  await b.close();
  console.log(n);
})().catch(e => { console.error(e); process.exit(1); });
"""


def verify_layout():
    js = os.path.join(BUILD, "layout.js")
    with open(js, "w") as fh:
        fh.write(LAYOUT_JS)
    files = [os.path.join(BUILD, x) for x in ("resource.html", "preview.html", "cover.html", "p1.html", "p2.html", "p3.html")]
    if not all(os.path.exists(x) for x in files):
        return ["build html missing: run gen.py first"]
    r = subprocess.run(["node", js, *files], capture_output=True, text=True, env=node_env())
    if r.returncode != 0:
        return [f"layout script failed: {r.stderr[-300:]}"]
    errs = json.loads(r.stdout.strip().splitlines()[-1])
    # rendered-pixel check: every drawing rendered ALONE on a transparent ground; the outer ring must be fully transparent
    html = open(os.path.join(BUILD, "resource.html")).read()
    uniq = []
    for sv in SVG_RE.findall(html):
        if sv not in uniq:
            uniq.append(sv)
    page = (f'<!doctype html><html><head><meta charset="utf-8"><style>{font_css()}html,body{{margin:0;background:transparent}}'
            f'svg{{display:block;margin:12px}}</style></head><body>{"".join(uniq)}</body></html>')
    write("alone.html", page)
    shots = os.path.join(BUILD, "aloneshots")
    os.makedirs(shots, exist_ok=True)
    for x in os.listdir(shots):
        os.remove(os.path.join(shots, x))
    jsa = os.path.join(BUILD, "alone.js")
    with open(jsa, "w") as fh:
        fh.write(ALONE_JS)
    r = subprocess.run(["node", jsa, os.path.join(BUILD, "alone.html"), shots], capture_output=True, text=True, env=node_env())
    if r.returncode != 0:
        return errs + [f"alone-drawing script failed: {r.stderr[-300:]}"]
    from PIL import Image
    names = sorted(os.listdir(shots))
    if len(names) != len(uniq):
        errs.append(f"drawings rendered alone: {len(names)}, expected {len(uniq)}")
    for nme in names:
        im = Image.open(os.path.join(shots, nme)).convert("RGBA")
        al = im.getchannel("A").load()
        w, h = im.size
        ring = 4
        if any(al[x, y] > 8 for x in range(w) for y in list(range(0, ring)) + list(range(h - ring, h))) or \
           any(al[x, y] > 8 for y in range(h) for x in list(range(0, ring)) + list(range(w - ring, w))):
            errs.append(f"rendered pixels: a drawing alone on a transparent ground touches its edge ({nme})")
        if not any(al[x, y] > 8 for x in range(0, w, 3) for y in range(0, h, 3)):
            errs.append(f"rendered pixels: a drawing rendered blank ({nme})")
    return errs


def verify_images():
    errs = []
    from PIL import Image
    for art, need in ((HERO, 10), (SPOT, 10)):
        h = Image.open(art)
        a = h.getchannel("A").point(lambda v: 255 if v > 24 else 0)
        bb = a.getbbox()
        if bb is None or bb[0] < need or bb[1] < need or h.width - bb[2] < need or h.height - bb[3] < need:
            errs.append(f"{os.path.basename(art)} touches its image edge: {bb}")
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
        cols = [x for x in range(0, 2000, 2) if any(px[x, y] < 200 for y in range(120, ytop - 4, 4))]
        if cols and (min(cols) < 40 or max(cols) > 1960):
            errs.append(f"{name}: content within 40px of the left or right edge")
    # the preview images show real page names only
    names = set(PAGE_NAMES.values())
    for hn in ("p1.html", "p2.html", "p3.html"):
        t = open(os.path.join(BUILD, hn)).read()
        for cap in re.findall(r'<div class="lbl"[^>]*>([^<]+)(?:<span>[^<]*</span>)?</div>', t):
            if cap not in names:
                errs.append(f"{hn}: label '{cap}' is not a page name")
        if t.count('class="swm"') != 1:
            errs.append(f"{hn}: expected exactly one PREVIEW watermark")
    return errs


def verify_files():
    errs = []
    from pypdf import PdfReader
    for p in [PDF, PREVIEW_PDF, COVER_PNG, *PREVIEW_PNGS, UPLOAD, TPT_JSON, HERO, SPOT, os.path.join(TPT, "STYLE.md"), RENDER_JS]:
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
        if i + 1 != 1 and f"Page {i + 1}" not in t and f"Page {i + 1}".upper() not in t.upper():
            errs.append(f"PDF page {i + 1} does not print its own page number")
    for pg, name in PAGE_NAMES.items():
        if pg == P_COVER:
            continue
        if name.lower() not in texts[pg - 1].lower():
            errs.append(f"page {pg} does not show its name '{name}'")
    full_pages()
    for frm, to, text in XREFS:
        if text not in texts[frm - 1]:
            errs.append(f"page {frm}: cross-reference text '{text}' not found")
    # every exercise appears on the three pages that hold it, and those pages point at each other
    for e in EXS:
        n = e["num"]
        for nm, pg in (("script", p_script(n)), ("student", p_student(n)), ("key", p_key(n))):
            if not re.search(rf"Exercise {n}(?!\d)", texts[pg - 1]):
                errs.append(f"exercise {n} is not on its {nm} page {pg}")
        for pg, want in ((p_script(n), f"Student pages: page {p_student(n)} Answer key: page {p_key(n)}"),
                         (p_student(n), f"Teacher scripts: page {p_script(n)} Answer key: page {p_key(n)}"),
                         (p_key(n), f"Teacher scripts: page {p_script(n)} Student pages: page {p_student(n)}")):
            if want.replace(" Answer", " · Answer").replace(" Student pages", " · Student pages") not in texts[pg - 1] and want not in texts[pg - 1]:
                errs.append(f"page {pg}: cross-references to the other pages of exercise {n} not found")
    # every "page N" / "pages N–M" mention names a real page
    for i, t in enumerate(texts):
        for m in re.finditer(r"(?i)\bpages? (\d+)(?:–(\d+))?", t):
            a, b = int(m.group(1)), int(m.group(2) or m.group(1))
            if a < 1 or b > TOTAL_PAGES or b < a:
                errs.append(f"page {i + 1}: reference '{m.group(0)}' is outside the {TOTAL_PAGES}-page file")
    teach, terms, score, track = texts[P_TEACH - 1], texts[P_TERMS - 1], texts[P_SCORE - 1], texts[P_TRACK - 1]
    for need in (f"page {P_ABOUT}", f"page {P_CHART}", f"pages {P_CHART} and {P_CHART2}", f"page {P_SCORE}", f"page {P_TRACK}", "7–12", "13–18", "19–24"):
        if need not in teach:
            errs.append(f"teacher notes lack the reference '{need}'")
    if f"pages {P_CHART}–{P_CHART2}" not in terms or f"pages {p_script(1)}–{p_key(30)}" not in terms or f"page {P_TRACK}" not in terms or f"({TOTAL_PAGES} pages)" not in terms.lower():
        errs.append("terms page 'what is in this file' does not match the page numbers")
    if f"page {P_TRACK}" not in score or f"{TOTAL_POINTS} points" not in score:
        errs.append("scoring page: tracker reference or total points missing")
    if f"{TOTAL_POINTS}" not in track or f"page {P_SCORE}" not in track:
        errs.append("tracker page: total points or scoring reference missing")
    for k, pg in ((1, p_key(1)), (1, p_key(6)), (2, p_key(11)), (2, p_key(16)), (3, p_key(21)), (3, p_key(26))):
        if str(pg) not in score:
            errs.append(f"scoring page does not name key page {pg}")
    prd = PdfReader(PREVIEW_PDF)
    for i in range(4):
        t = prd.pages[i].extract_text() or ""
        if t.count("PREVIEW") != 1:
            errs.append(f"preview PDF page {i + 1}: expected exactly one PREVIEW watermark")
        want = PAGE_NAMES[PREVIEW_PAGES[i]]
        if want.lower() not in t.lower():
            errs.append(f"preview PDF page {i + 1} is not '{want}'")
    errs += verify_images()
    up = open(UPLOAD).read()
    m = re.search(r"^## 1\. Title\s*\n+```\n(.+?)\n```", up, re.M | re.S)
    if not m:
        errs.append("UPLOAD.md: title block not found")
    else:
        title = m.group(1).strip()
        if len(title) > 80 or title != LISTING_TITLE:
            errs.append(f"UPLOAD.md: title is {len(title)} chars or differs from the generator")
        if re.search(r"winter|snow|holiday|christmas|december|halloween|thanksgiving", title, re.I):
            errs.append("UPLOAD.md: seasonal word in the title")
    for need in (DISCLOSURE, f"${PRICE}", f"{TOTAL_PAGES} pages", "30 exercises", "grades 3-8", "TpT allows only 4 grade levels", "4th, 5th, 6th and 7th"):
        if need not in up:
            errs.append(f"UPLOAD.md: missing '{need}'")
    sec = up.split("## 5. Page count by section")[1].split("##")[0]
    nums = [int(x) for x in re.findall(r"^- (?!Total)[^\n]*: (\d+)$", sec, re.M)]
    if sum(nums) != TOTAL_PAGES:
        errs.append(f"UPLOAD.md page list sums to {sum(nums)}, PDF has {TOTAL_PAGES}")
    desc = up.split("## 2. Description")[1].split("## 3.")[0]
    dn = [int(x) for x in re.findall(r"^• [^\n]*\((\d+) pages?\)", desc, re.M)]
    if sum(dn) != TOTAL_PAGES:
        errs.append(f"UPLOAD.md description page list sums to {sum(dn)}, PDF has {TOTAL_PAGES}")
    # section counts in the upload list agree with the real page names
    want_secs = {"Cover": 1, "Teacher notes": 1, "Scoring and assessment": 1, "About rhythm dictation": 1, "Progress tracker": 1, "Terms of use and credits": 1}
    for nm, cnt_ in want_secs.items():
        if f"- {nm}: {cnt_}" not in sec:
            errs.append(f"UPLOAD.md page list lacks '{nm}: {cnt_}'")
    for lv in (1, 2, 3):
        a, b = (lv - 1) * 10 + 1, lv * 10
        for kind in ("teacher scripts", "student pages", "answer keys"):
            if f"- Level {lv} {kind}, exercises {a}-{b}: 2" not in sec:
                errs.append(f"UPLOAD.md page list lacks Level {lv} {kind}")
        if f"Level {lv} (grades {LEVEL_GRADES[lv].replace('–', '-')})" not in desc:
            errs.append(f"UPLOAD.md description lacks the grades of Level {lv}")
    low = up.lower()
    for bad in ("checked by hand", "handmade", "recomputed", "classroom-tested", "classroom tested", "hand-checked"):
        if bad in low:
            errs.append(f"UPLOAD.md says '{bad}'")
    tj = json.load(open(TPT_JSON))
    tags, subs = set(load_json("TAG-OPTIONS.json")["options"]), set(load_json("SUBJECT-OPTIONS.json"))
    if any(t not in tags for t in tj["tags"]) or any(s not in subs for s in tj["subjects"]):
        errs.append("tpt.json tags or subjects invalid")
    if tj.get("pages") != TOTAL_PAGES or tj["price"] != PRICE or not 1 <= len(tj["grades"]) <= 4:
        errs.append("tpt.json pages, price or grades mismatch")
    first = texts[0].lower()
    if f"{TOTAL_PAGES} pages" not in first or "30 exercises" not in first or "grades 3–8" not in first:
        errs.append("cover text does not state the page count, exercise count and grades")
    if DISCLOSURE not in terms:
        errs.append("terms page lacks the disclosure line")
    allt = " ".join(texts).lower()
    for bad in ("qa ", "checker", "recomputed", "verified by code"):
        if bad in allt.replace("answer keys are verified", ""):
            errs.append(f"buyer-facing text contains internal wording '{bad}'")
    for bad in ("colour", "favourite", "rhythmn", "metre", "crotchet", "quaver", "minim", "semibreve", "analyse"):
        if bad in allt:
            errs.append(f"non-US spelling '{bad}'")
    return errs


def check():
    errs = verify_html()
    errs += verify_layout()
    errs += verify_files()
    if errs:
        print("CHECK FAILED")
        print("\n".join(" - " + e for e in errs[:80]))
        if len(errs) > 80:
            print(f" ... and {len(errs) - 80} more")
        sys.exit(1)
    print("CHECK OK: 30 exercises re-read from the rendered SVG (key staves, student bars, 15 chart rows, worked example, meter examples); every key bar adds to its "
          "time signature (4/4 = 4 beats, 3/4 = 3, 6/8 = six eighths); syllables and counts recomputed from the notation equal the teacher scripts and the printed key labels; "
          "student pages have the same time signature and bar count as their keys; each level uses only its own values; all 30 exercises distinct; stems on the right of up-stem heads, "
          f"beams, flags, dots and rests correct, compound beaming in threes; scoring and tracker totals ({TOTAL_POINTS} points) recomputed; no drawing touches its edge when rendered alone on a transparent ground; "
          f"layout and footer gaps clear; PDF {TOTAL_PAGES} Letter pages, preview 4 (one watermark each); images 2000x2000 with clean edges; cross-references, UPLOAD.md and tpt.json agree.")


if __name__ == "__main__" and "--check" in sys.argv:
    check()
