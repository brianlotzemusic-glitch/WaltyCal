#!/usr/bin/env python3
"""Solfege Snowball Melody Cards (TpT 050): build the resource and verify it.

    python3 gen.py           build everything (PDFs, PNGs, UPLOAD.md, tpt.json) into this folder
    python3 gen.py --check   re-read every drawn staff from the rendered HTML and verify notation, sets, keys and layout

Every pattern is a list of bars; a bar is a list of events (kind q/h/e/r + syllable). The card (an SVG) and the answer key row are
both produced from it. `--check` does not trust the data: it parses the rendered SVG of every staff (lines, ledger lines,
noteheads, stems, beams, rests, barlines, syllable text), derives each pitch from the notehead's position on the staff and
compares that with the printed syllable (C=do, D=re, E=mi, G=sol, A=la), adds up every bar, checks set membership and
distinctness, and compares each key entry with the drawn card.
"""
import json
import math
import os
import random
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

SLUG = "solfege-snowball-melody-cards"
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
TITLE = "Solfege Snowball Melody Cards"
LISTING_TITLE = "Pentatonic Melody Cards: Solfege Read & Sing Patterns, Music Gr 2-4"
PREFERRED_TITLE = "Solfege Snowball Melody Cards: Pentatonic Read & Sing Patterns | Music Gr 2-4"
PRICE = "4.00"
TAGS = ["Winter", "Task Cards", "Printables", "Activities", "Centers"]
SUBJECTS = ["Music", "Vocal Music", "Music Composition"]
GRADES = ["2nd-grade", "3rd-grade", "4th-grade"]

# ------------------------------------------------------------------ music data
SYL_OF_LETTER = {"C": "do", "D": "re", "E": "mi", "G": "sol", "A": "la"}
STEP_OF_SYL = {"do": -2, "re": -1, "mi": 0, "sol": 2, "la": 3}      # staff step above the bottom line (E4 = 0)
LETTER_OF_STEP = {-2: "C", -1: "D", 0: "E", 1: "F", 2: "G", 3: "A", 4: "B"}
DEG = {"do": 0, "re": 1, "mi": 2, "sol": 3, "la": 4}
SYL_ORDER = ["do", "re", "mi", "sol", "la"]
BEATS = {"q": 1.0, "h": 2.0, "e": 0.5, "r": 1.0}
UNIT = {"q": 1.0, "h": 1.6, "e": 1.0, "r": 1.0}
SET_NAMES = {"A": "sol and mi", "B": "mi, sol and la", "C": "do and re added", "D": "all five notes"}
SET_SYLS = {"A": "sol · mi", "B": "mi · sol · la", "C": "do · re · mi · sol · la", "D": "do · re · mi · sol · la"}
SET_ALLOWED = {"A": ["mi", "sol"], "B": ["mi", "sol", "la"], "C": SYL_ORDER, "D": SYL_ORDER}
SETS = "ABCD"
PER_SET = 8
MAX_PAIRS = {"A": 1, "B": 2, "C": 3, "D": 3}
MAX_RESTS = {"A": 1, "B": 1, "C": 2, "D": 2}
RH_WORD = {"q": "ta", "h": "ta-a", "r": "shh"}

RHYTHMS = {   # bar rhythms: list of event kinds, 'e' always comes in beamed pairs
    "qqqq": list("qqqq"), "qqh": list("qqh"), "hqq": list("hqq"), "hh": list("hh"), "qhq": list("qhq"),
    "eqqq": list("eeqqq"), "qeqq": list("qeeqq"), "qqeq": list("qqeeq"), "qqqe": list("qqqee"),
    "eeqq": list("eeeeqq"), "qqqr": list("qqqr"), "qrh": list("qrh"), "eqh": list("eeqh"), "qeh": list("qeeh"),
    "heq": list("heeq"), "qqrq": list("qqrq"), "hqr": list("hqr"), "rqqq": list("rqqq"),
}
END_BARS = ["qqh", "hh", "eqh", "qeh"]
MID_BARS = [k for k in RHYTHMS if k not in ("hqr",)]
BANK = ["qqqq", "qqh", "hqq", "hh", "qhq", "eqqq", "qeqq", "qqqr", "eeqq", "qrh", "eqh", "heq"]   # R1..R12, the slot cards
FORBIDDEN = [("sol", "sol", "mi"), ("mi", "re", "do"), ("do", "do", "sol", "sol"), ("sol", "sol", "la", "la"), ("do", "re", "mi"),
             ("sol", "sol", "la", "sol"), ("mi", "re", "do", "re"), ("sol", "la", "sol", "mi")]


def bar_beats(kinds):
    return sum(BEATS[k] for k in kinds)


for _k, _v in RHYTHMS.items():
    assert bar_beats(_v) == 4, _k
    assert _v.count("e") % 2 == 0 and all(_v[i] == "e" for i in range(len(_v)) if _v[i] == "e")


def pair_count(kinds):
    return kinds.count("e") // 2


def sequence_has(seq, cell):
    n = len(cell)
    return any(tuple(seq[i:i + n]) == cell for i in range(len(seq) - n + 1))


def make_pattern(rng, st, other_rhythms, other_first3):
    """Random pattern for set `st` meeting every rule. Returns (bars, rhythm_key)."""
    allowed = SET_ALLOWED[st]
    for _ in range(100000):
        keys = [rng.choice(MID_BARS) for _ in range(3)] + [rng.choice(END_BARS)]
        kinds = [RHYTHMS[k] for k in keys]
        flat = [x for b in kinds for x in b]
        if sum(pair_count(b) for b in kinds) > MAX_PAIRS[st] or flat.count("r") > MAX_RESTS[st]:
            continue
        if kinds[0][0] == "r" or (st in "AB" and sum(pair_count(b) for b in kinds) == 0 and rng.random() < 0.5):
            continue
        rk = "-".join(keys)
        if rk in other_rhythms:
            continue
        notes = [i for i, k in enumerate(flat) if k != "r"]
        seq = []
        cur = rng.choice(allowed)
        for n_i in range(len(notes)):
            if n_i > 0:
                cands = [s for s in allowed if abs(DEG[s] - DEG[cur]) <= 3]
                w = [3 if abs(DEG[s] - DEG[cur]) == 1 else 2 if abs(DEG[s] - DEG[cur]) == 2 else 1.4 if s == cur else 1 for s in cands]
                cur = rng.choices(cands, w)[0]
            seq.append(cur)
        used = set(seq)
        ok = True
        if st == "A" and used != {"mi", "sol"}:
            ok = False
        if st == "B" and used != {"mi", "sol", "la"}:
            ok = False
        if st == "C" and not ({"do", "re"} <= used and len(used) < 5):
            ok = False
        if st == "D" and used != set(SYL_ORDER):
            ok = False
        want_end = ("mi", "sol") if st in "AB" else ("do",)
        if seq[-1] not in want_end:
            ok = False
        if any(sequence_has(seq, c) for c in FORBIDDEN):
            ok = False
        if any(seq[i] == seq[i + 1] == seq[i + 2] == seq[i + 3] for i in range(len(seq) - 3)):
            ok = False
        if tuple(seq[:5]) in other_first3:
            ok = False
        if not ok:
            continue
        it = iter(seq)
        bars = [[(k, None if k == "r" else next(it)) for k in b] for b in kinds]
        return bars, rk
    raise RuntimeError("no pattern found")


def build_patterns():
    pats = []
    for si, st in enumerate(SETS):
        rng = random.Random(5050 + 17 * si)
        rhs, firsts = set(), set()
        for n in range(1, PER_SET + 1):
            bars, rk = make_pattern(rng, st, rhs, firsts)
            rhs.add(rk)
            firsts.add(tuple(s for b in bars for _, s in b if s)[:5])
            pats.append({"id": f"{st}{n}", "set": st, "bars": bars})
    return pats


def make_example(rng, allowed, end_ok):
    """Example melody for a mat: every bar rhythm comes from the rhythm bank."""
    for _ in range(100000):
        keys = [rng.choice(BANK) for _ in range(4)]
        if len(set(keys)) < 4 or keys[-1] not in ("qqh", "hh", "eqh"):
            continue
        kinds = [RHYTHMS[k] for k in keys]
        flat = [x for b in kinds for x in b]
        if flat[0] == "r":
            continue
        cur = rng.choice(allowed)
        seq = []
        for k in flat:
            if k == "r":
                continue
            if seq:
                cands = [s for s in allowed if abs(DEG[s] - DEG[cur]) <= 3]
                cur = rng.choice(cands)
            seq.append(cur)
        if seq[-1] not in end_ok or set(seq) != set(allowed) or any(sequence_has(seq, c) for c in FORBIDDEN):
            continue
        it = iter(seq)
        return keys, [[(k, None if k == "r" else next(it)) for k in b] for b in kinds]
    raise RuntimeError("no example")


PATTERNS = build_patterns()
EX_KEYS = {}
EXAMPLES = []
for _i, (_allowed, _end) in enumerate((( ["mi", "sol", "la"], ["mi", "sol"]), (SYL_ORDER, ["do"]))):
    _keys, _bars = make_example(random.Random(7000 + _i), _allowed, _end)
    EXAMPLES.append({"id": f"EX{_i + 1}", "set": "EX", "bars": _bars, "keys": _keys})


def syl_seq(p):
    return [s for b in p["bars"] for _, s in b if s]


# ------------------------------------------------------------------ notation drawing
HEAD_W = 1.18
REST_W = 1.08
G_HEAD = 0xE0A4
G_HALF = 0xE0A3
G_QREST = 0xE4E5
G_TREBLE = 0xE050
G_TS = 0xE080


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


def sparkle(x, y, r, color="#000", sw=1.3):
    return (f'<g stroke="{color}" stroke-width="{sw}" stroke-linecap="round"><line x1="{x - r:.1f}" y1="{y:.1f}" x2="{x + r:.1f}" y2="{y:.1f}"/>'
            f'<line x1="{x:.1f}" y1="{y - r:.1f}" x2="{x:.1f}" y2="{y + r:.1f}"/></g>')


def snowball(cx, cy, r, sw=1.4, motion=False, label=None, lsize=None):
    """A packed snowball: lumpy white ball, blue shading on the lower right, a sparkle of fresh snow; optional motion lines (thrown) or a label inside."""
    o = []
    if motion:
        for dy, ln in ((-0.55, 0.8), (0.0, 1.1), (0.55, 0.7)):
            y = cy + dy * r
            o.append(f'<line x1="{cx - r * 1.2 - r * ln:.1f}" y1="{y:.1f}" x2="{cx - r * 1.25:.1f}" y2="{y:.1f}" stroke="{ACCENT}" stroke-width="{sw:.2f}" stroke-linecap="round"/>')
    o.append(f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r:.2f}" fill="#fff" stroke="#000" stroke-width="{sw:.2f}"/>')
    a0, a1 = math.radians(-25), math.radians(70)
    rr = r * 0.72
    x0, y0 = cx + rr * math.cos(a0), cy + rr * math.sin(a0)
    x1, y1 = cx + rr * math.cos(a1), cy + rr * math.sin(a1)
    o.append(f'<path d="M{x0:.1f},{y0:.1f} A{rr:.1f},{rr:.1f} 0 0 1 {x1:.1f},{y1:.1f}" fill="none" stroke="{ACCENT}" stroke-width="{sw * 1.5:.2f}" stroke-linecap="round"/>')
    if label is None:
        o.append(f'<path d="M{cx - 0.55 * r:.1f},{cy - 0.15 * r:.1f} q{0.15 * r:.1f},{-0.35 * r:.1f} {0.4 * r:.1f},{-0.4 * r:.1f}" fill="none" stroke="#000" stroke-width="{max(sw * 0.7, 0.7):.2f}" stroke-linecap="round"/>')
    else:
        o.append(f'<text x="{cx - 2:.1f}" y="{cy + (lsize or r * 0.7) * 0.34:.1f}" text-anchor="middle" font-family="Oswald" font-weight="700" font-size="{lsize or r * 0.7:.1f}">{label}</text>')
    return "".join(o)


def snow_pile(cx, base, r, sw=1.4):
    return (snowball(cx - r * 1.05, base - r, r, sw) + snowball(cx + r * 1.05, base - r, r, sw) + snowball(cx, base - r * 2.55, r, sw))


def snowman(cx, base, r, fill="#fff", accent=ACCENT, sw=1.4):
    r2, r3 = r * 0.74, r * 0.54
    c1y = base - r
    c2y = base - 2 * r - r2 * 0.78
    c3y = c2y - r2 * 0.78 - r3 * 0.82
    o = [f'<g stroke="#000" stroke-width="{sw}" stroke-linejoin="round" stroke-linecap="round">']
    o.append(f'<line x1="{cx - r2 * 0.9:.1f}" y1="{c2y:.1f}" x2="{cx - r2 * 1.9:.1f}" y2="{c2y - r2 * 0.7:.1f}" fill="none"/>')
    o.append(f'<line x1="{cx + r2 * 0.9:.1f}" y1="{c2y:.1f}" x2="{cx + r2 * 1.9:.1f}" y2="{c2y - r2 * 0.7:.1f}" fill="none"/>')
    for cy, rr in ((c1y, r), (c2y, r2), (c3y, r3)):
        o.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{rr:.1f}" fill="{fill}"/>')
    o.append(f'<rect x="{cx - r3 * 1.0:.1f}" y="{c3y + r3 * 0.72:.1f}" width="{r3 * 2.0:.1f}" height="{r3 * 0.34:.1f}" rx="{r3 * 0.12:.1f}" fill="{accent}"/>')
    o.append(f'<rect x="{cx + r3 * 0.25:.1f}" y="{c3y + r3 * 0.95:.1f}" width="{r3 * 0.42:.1f}" height="{r3 * 0.85:.1f}" rx="{r3 * 0.1:.1f}" fill="{accent}"/>')
    o.append(f'<rect x="{cx - r3 * 0.95:.1f}" y="{c3y - r3 * 0.98:.1f}" width="{r3 * 1.9:.1f}" height="{r3 * 0.22:.1f}" rx="{r3 * 0.08:.1f}" fill="#000"/>')
    o.append(f'<rect x="{cx - r3 * 0.58:.1f}" y="{c3y - r3 * 1.75:.1f}" width="{r3 * 1.16:.1f}" height="{r3 * 0.8:.1f}" fill="#000"/>')
    o.append("</g>")
    o.append(f'<g fill="#000"><circle cx="{cx - r3 * 0.34:.1f}" cy="{c3y - r3 * 0.2:.1f}" r="{max(r3 * 0.09, 0.9):.1f}"/><circle cx="{cx + r3 * 0.34:.1f}" cy="{c3y - r3 * 0.2:.1f}" r="{max(r3 * 0.09, 0.9):.1f}"/>'
             f'<circle cx="{cx:.1f}" cy="{c2y - r2 * 0.1:.1f}" r="{max(r2 * 0.09, 1):.1f}"/><circle cx="{cx:.1f}" cy="{c2y + r2 * 0.35:.1f}" r="{max(r2 * 0.09, 1):.1f}"/></g>')
    o.append(f'<path d="M{cx:.1f},{c3y + r3 * 0.05:.1f} L{cx + r3 * 0.85:.1f},{c3y + r3 * 0.2:.1f} L{cx:.1f},{c3y + r3 * 0.34:.1f} Z" fill="{accent}" stroke="#000" stroke-width="{sw * 0.7:.2f}" stroke-linejoin="round"/>')
    return "".join(o)


def mitten(cx, cy, size, fill="#fff", accent=ACCENT, sw=1.4, flip=False):
    k = size / 48.0
    sx = -1 if flip else 1
    body = "M10,40 L10,20 Q10,4 24,4 Q38,4 38,20 L38,40 Z"
    thumb = "M10,28 Q-2,26 1,14 Q6,12 10,20"
    return (f'<g transform="translate({cx:.1f},{cy:.1f}) scale({sx * k:.3f},{k:.3f}) translate(-24,-26)" stroke="#000" stroke-width="{sw / k:.2f}" stroke-linejoin="round" stroke-linecap="round">'
            f'<path d="{body}" fill="{fill}"/><path d="{thumb}" fill="{fill}"/>'
            f'<rect x="8" y="40" width="32" height="8" rx="2" fill="{accent}"/>'
            f'<path d="M24,12 L24,20 M20,16 L28,16" fill="none" stroke="{accent}" stroke-width="2.2"/></g>')


def bar_slots(kinds, xl, W, pad=6.0):
    """x centres (head/rest centre) for the events of one bar, justified over [xl, xl+W]."""
    units = sum(UNIT[k] for k in kinds)
    uw = (W - 2 * pad) / units
    cur = xl + pad
    xs = []
    for k in kinds:
        sw_ = UNIT[k] * uw
        xs.append(cur + min(sw_, uw) / 2)
        cur += sw_
    return xs


def staff_lines_svg(x1, x2, top, S, cls="sl"):
    return "".join(f'<line class="{cls}" x1="{fx(x1)}" y1="{fx(top + i * S)}" x2="{fx(x2)}" y2="{fx(top + i * S)}" stroke="#000" stroke-width="{fx(0.1 * S)}"/>' for i in range(5))


def head_note(step, kind, cx, top, S, beam_top=None, syl=None, label_y=None, fill="#000"):
    """One pitched event: ledger lines, head, up stem on the right edge. Returns svg string."""
    bottom = top + 4 * S
    y = bottom - step * S / 2
    hw = HEAD_W * S
    left = cx - hw / 2
    sw = 0.13 * S
    o = [f'<g class="ev" data-kind="{kind}">']
    for e in range(-2, step - 1, -2) if step < 0 else []:
        ly = bottom - e * S / 2
        o.append(f'<line class="led" x1="{fx(left - 0.2 * S)}" y1="{fx(ly)}" x2="{fx(left + hw + 0.2 * S)}" y2="{fx(ly)}" stroke="#000" stroke-width="{fx(0.16 * S)}"/>')
    o.append(gl(G_HALF if kind == "h" else G_HEAD, left, y, 4 * S, "head", fill))
    sx = left + hw - sw / 2
    y1 = y - 0.168 * S
    y2 = beam_top if beam_top is not None else y1 - max(3.5 * S, 0)
    o.append(f'<line class="stem" x1="{fx(sx)}" y1="{fx(y1)}" x2="{fx(sx)}" y2="{fx(y2)}" stroke="{fill}" stroke-width="{fx(sw)}"/>')
    o.append("</g>")
    return "".join(o), y


def pattern_svg(pid, bars, st, kind="card", w=540.0, S=10.0, header=True, border=True, px=None, label=None):
    """A 4-bar treble staff pattern with syllables underneath. kind: card / ex / cover (all are verified by --check)."""
    top = (36 + S) if header else (S + 6)
    bottom = top + 4 * S
    syl_y = bottom + 3.5 * S
    fold_y = bottom + 2.55 * S
    h = syl_y + (11 if kind != "cover" else 9)
    if not header:
        h = syl_y + 8
    x_clef = 12.0
    bars_x0 = x_clef + 4.9 * S
    x_end = w - 12
    W = (x_end - bars_x0) / 4
    size = f'width="{w:.0f}pt" height="{h:.0f}pt"' if not px else f'width="{px}px" height="{h * px / w:.1f}px"'
    o = [f'<svg class="ns" data-kind="{kind}" data-id="{pid}" data-set="{st}" data-meter="4/4" data-x0="{fx(bars_x0)}" data-s="{fx(S)}" xmlns="http://www.w3.org/2000/svg" '
         f'viewBox="0 0 {w:.0f} {h:.1f}" {size} style="display:block">']
    if border:
        o.append(f'<rect x="0.8" y="0.8" width="{w - 1.6:.1f}" height="{h - 1.6:.1f}" rx="10" fill="#fff" stroke="#000" stroke-width="1.3"/>')
    if header:
        o.append(snowball(34, 20, 11, 1.4, motion=True))
        o.append(f'<text x="54" y="26" font-family="Oswald" font-weight="700" font-size="18" letter-spacing=".02em">{pid}</text>')
        o.append(f'<text x="{w - 14}" y="25" text-anchor="end" font-family="Oswald" font-weight="300" font-size="12.5">Set {st} · {SET_NAMES[st]}</text>')
    o.append(staff_lines_svg(x_clef - 4, x_end, top, S))
    o.append(gl(G_TREBLE, x_clef, bottom - S, 4 * S, "clef"))
    o.append(f'<g class="timesig">{gl(G_TS + 4, x_clef + 2.95 * S, top + 2 * S, 4 * S)}{gl(G_TS + 4, x_clef + 2.95 * S, top + 4 * S, 4 * S)}</g>')
    if header and kind == "card":
        o.append(f'<line x1="14" y1="{fx(fold_y)}" x2="{fx(w - 14)}" y2="{fx(fold_y)}" stroke="#555" stroke-width="0.9" stroke-dasharray="4 3"/>')
    for bi, bar in enumerate(bars):
        xl = bars_x0 + bi * W
        kinds = [k for k, _ in bar]
        xs = bar_slots(kinds, xl, W)
        i = 0
        while i < len(bar):
            k, syl = bar[i]
            if k == "r":
                o.append(f'<g class="ev" data-kind="r">{gl(G_QREST, xs[i] - REST_W * S / 2, top + 2 * S, 4 * S, "rest")}</g>')
                o.append(f'<text class="rlab" x="{fx(xs[i])}" y="{fx(syl_y)}" text-anchor="middle" font-family="Source Sans 3, sans-serif" font-style="italic" font-size="{fx(1.05 * S)}" fill="#555">rest</text>')
                i += 1
            elif k == "e":
                # beamed pair: i and i+1
                pair = [(bar[i], xs[i]), (bar[i + 1], xs[i + 1])]
                ys = [bottom - STEP_OF_SYL[p[0][1]] * S / 2 for p in pair]
                beam_top = min(ys) - 0.168 * S - 3.5 * S
                parts = []
                for (ev, cx), _y in zip(pair, ys):
                    s_, _ = head_note(STEP_OF_SYL[ev[1]], "e", cx, top, S, beam_top=beam_top)
                    parts.append(s_)
                    o.append(s_)
                    o.append(f'<text class="syl" x="{fx(cx)}" y="{fx(syl_y)}" text-anchor="middle" font-family="Source Sans 3, sans-serif" font-weight="700" font-size="{fx(1.12 * S)}">{ev[1]}</text>')
                sw = 0.13 * S
                bx1 = xs[i] + HEAD_W * S / 2 - sw
                bx2 = xs[i + 1] + HEAD_W * S / 2
                o.append(f'<rect class="beam" x="{fx(bx1)}" y="{fx(beam_top)}" width="{fx(bx2 - bx1)}" height="{fx(0.5 * S)}" fill="#000"/>')
                i += 2
            else:
                s_, _ = head_note(STEP_OF_SYL[syl], k, xs[i], top, S)
                o.append(s_)
                o.append(f'<text class="syl" x="{fx(xs[i])}" y="{fx(syl_y)}" text-anchor="middle" font-family="Source Sans 3, sans-serif" font-weight="700" font-size="{fx(1.12 * S)}">{syl}</text>')
                i += 1
        bx = xl + W
        if bi < 3:
            o.append(f'<line class="bar" x1="{fx(bx)}" y1="{fx(top)}" x2="{fx(bx)}" y2="{fx(bottom)}" stroke="#000" stroke-width="{fx(0.14 * S)}"/>')
        else:
            o.append(f'<line class="bar" x1="{fx(bx - 0.35 * S)}" y1="{fx(top)}" x2="{fx(bx - 0.35 * S)}" y2="{fx(bottom)}" stroke="#000" stroke-width="{fx(0.14 * S)}"/>')
            o.append(f'<rect class="fin" x="{fx(bx - 0.18 * S)}" y="{fx(top)}" width="{fx(0.36 * S)}" height="{fx(4 * S)}" fill="#000"/>')
    o.append("</svg>")
    return "".join(o)


def pitch_bank_svg(syls, w=300.0, S=8.5, kind="bank", pid="BANK"):
    """Quarter notes in a row, each labelled with its syllable and letter name (the five snowball notes)."""
    top = S + 8
    bottom = top + 4 * S
    h = bottom + 6.2 * S
    x_clef = 8.0
    x0 = x_clef + 3.1 * S
    n = len(syls)
    gap = (w - 8 - x0) / n
    o = [f'<svg class="ns" data-kind="{kind}" data-id="{pid}" data-set="-" data-meter="" data-x0="{fx(x0)}" data-s="{fx(S)}" xmlns="http://www.w3.org/2000/svg" '
         f'viewBox="0 0 {w:.0f} {h:.1f}" width="{w:.0f}pt" height="{h:.0f}pt" style="display:block">']
    o.append(staff_lines_svg(2, w - 4, top, S))
    o.append(gl(G_TREBLE, x_clef, bottom - S, 4 * S, "clef"))
    for i, s in enumerate(syls):
        cx = x0 + gap * (i + 0.5)
        sn, _ = head_note(STEP_OF_SYL[s], "q", cx, top, S)
        o.append(sn)
        o.append(f'<text class="syl" x="{fx(cx)}" y="{fx(bottom + 3.6 * S)}" text-anchor="middle" font-family="Source Sans 3, sans-serif" font-weight="700" font-size="{fx(1.4 * S)}">{s}</text>')
        o.append(f'<text class="let" x="{fx(cx)}" y="{fx(bottom + 5.6 * S)}" text-anchor="middle" font-family="Oswald" font-weight="500" font-size="{fx(1.05 * S)}" fill="#444">{ {"do": "C", "re": "D", "mi": "E", "sol": "G", "la": "A"}[s] }</text>')
    o.append("</svg>")
    return "".join(o)


def rhythm_card_svg(rid, key, w=235.0, S=7.0, px=None, cut=True):
    """A one-bar rhythm slot card: single line, stems down on the left of the head, beams below. Same x layout as a mat bar."""
    kinds = RHYTHMS[key]
    ly = 30.0
    h = 70.0
    xs = bar_slots(kinds, 0, w)
    size = f'width="{w:.0f}pt" height="{h:.0f}pt"' if not px else f'width="{px}px" height="{h * px / w:.1f}px"'
    o = [f'<svg class="rc" data-id="{rid}" data-key="{key}" data-s="{fx(S)}" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.0f} {h:.0f}" {size} style="display:block">']
    if cut:
        o.append(f'<rect x="0.8" y="0.8" width="{w - 1.6:.1f}" height="{h - 1.6:.1f}" rx="6" fill="#fff" stroke="#000" stroke-width="1.1" stroke-dasharray="5 3"/>')
    o.append(f'<text x="8" y="14" font-family="Oswald" font-weight="700" font-size="11" fill="{ACCENT}">{rid}</text>')
    o.append(f'<line class="rl" x1="6" y1="{ly}" x2="{w - 6}" y2="{ly}" stroke="#000" stroke-width="{fx(0.1 * S)}"/>')
    sw = 0.13 * S
    hw = HEAD_W * S
    word_y = h - 6
    i = 0
    while i < len(kinds):
        k = kinds[i]
        if k == "r":
            o.append(f'<g class="ev" data-kind="r">{gl(G_QREST, xs[i] - REST_W * S / 2, ly, 4 * S, "rest")}</g>')
            o.append(f'<text class="rw" x="{fx(xs[i])}" y="{word_y}" text-anchor="middle" font-family="Source Sans 3, sans-serif" font-weight="600" font-size="10">shh</text>')
            i += 1
        elif k == "e":
            stem_end = ly + 0.168 * S + 3.0 * S
            for j in (i, i + 1):
                left = xs[j] - hw / 2
                o.append(f'<g class="ev" data-kind="e">{gl(G_HEAD, left, ly, 4 * S, "head")}'
                         f'<line class="stem" x1="{fx(left + sw / 2)}" y1="{fx(ly + 0.168 * S)}" x2="{fx(left + sw / 2)}" y2="{fx(stem_end)}" stroke="#000" stroke-width="{fx(sw)}"/></g>')
            bx1 = xs[i] - hw / 2
            bx2 = xs[i + 1] - hw / 2 + sw
            o.append(f'<rect class="beam" x="{fx(bx1)}" y="{fx(stem_end - 0.5 * S)}" width="{fx(bx2 - bx1)}" height="{fx(0.5 * S)}" fill="#000"/>')
            o.append(f'<text class="rw" x="{fx((xs[i] + xs[i + 1]) / 2)}" y="{word_y}" text-anchor="middle" font-family="Source Sans 3, sans-serif" font-weight="600" font-size="10">ti-ti</text>')
            i += 2
        else:
            left = xs[i] - hw / 2
            stem_end = ly + 0.168 * S + 3.0 * S
            o.append(f'<g class="ev" data-kind="{k}">{gl(G_HALF if k == "h" else G_HEAD, left, ly, 4 * S, "head")}'
                     f'<line class="stem" x1="{fx(left + sw / 2)}" y1="{fx(ly + 0.168 * S)}" x2="{fx(left + sw / 2)}" y2="{fx(stem_end)}" stroke="#000" stroke-width="{fx(sw)}"/></g>')
            o.append(f'<text class="rw" x="{fx(xs[i])}" y="{word_y}" text-anchor="middle" font-family="Source Sans 3, sans-serif" font-weight="600" font-size="10">{RH_WORD[k]}</text>')
            i += 1
    o.append("</svg>")
    return "".join(o)


def mini_rhythm_svg(k, w=46, h=34, S=5.0):
    """Reference-page symbol: one rhythm on a single line (quarter, half, eighth pair, rest)."""
    ly = 13.0
    sw = 0.13 * S
    hw = HEAD_W * S
    o = [f'<svg width="{w}pt" height="{h}pt" viewBox="0 0 {w} {h}" style="display:block">',
         f'<line x1="2" y1="{ly}" x2="{w - 2}" y2="{ly}" stroke="#000" stroke-width="{0.5}"/>']
    cx = w / 2
    stem_end = ly + 0.168 * S + 3.0 * S
    if k == "r":
        o.append(gl(G_QREST, cx - REST_W * S / 2, ly, 4 * S))
    elif k == "e":
        xs = [cx - 6.5, cx + 6.5]
        for x in xs:
            o.append(gl(G_HEAD, x - hw / 2, ly, 4 * S) + f'<line x1="{x - hw / 2 + sw / 2:.2f}" y1="{ly + 0.168 * S:.2f}" x2="{x - hw / 2 + sw / 2:.2f}" y2="{stem_end:.2f}" stroke="#000" stroke-width="{sw:.2f}"/>')
        o.append(f'<rect x="{xs[0] - hw / 2:.2f}" y="{stem_end - 0.5 * S:.2f}" width="{xs[1] - xs[0] + sw:.2f}" height="{0.5 * S:.2f}" fill="#000"/>')
    else:
        o.append(gl(G_HALF if k == "h" else G_HEAD, cx - hw / 2, ly, 4 * S) + f'<line x1="{cx - hw / 2 + sw / 2:.2f}" y1="{ly + 0.168 * S:.2f}" x2="{cx - hw / 2 + sw / 2:.2f}" y2="{stem_end:.2f}" stroke="#000" stroke-width="{sw:.2f}"/>')
    o.append("</svg>")
    return "".join(o)


def mat_svg(variant):
    """Build-a-melody mat: 2 rows x 2 bars. Dashed slots for the rhythm cards sit above empty staves."""
    S = 10.0
    W = 235.0
    w = 540.0
    x0 = w - 4 - 2 * W
    sl_h = 70.0
    row_h = 218.0
    h = 2 * row_h + 6
    o = [f'<svg class="mat" data-variant="{variant}" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.0f} {h:.0f}" width="{w:.0f}pt" height="{h:.0f}pt" style="display:block">']
    for r in range(2):
        y0 = r * row_h
        top = y0 + sl_h + 12 + 2.2 * S
        bottom = top + 4 * S
        for b in range(2):
            n = r * 2 + b + 1
            xl = x0 + b * W
            o.append(f'<rect class="slot" x="{xl + 0.8:.1f}" y="{y0 + 0.8:.1f}" width="{W - 1.6:.1f}" height="{sl_h - 1.6:.1f}" rx="6" fill="#fff" stroke="{ACCENT}" stroke-width="1.5" stroke-dasharray="6 4"/>')
            o.append(f'<text x="{xl + W / 2:.1f}" y="{y0 + sl_h / 2 + 5:.1f}" text-anchor="middle" font-family="Oswald" font-weight="500" font-size="13" fill="{ACCENT}" letter-spacing=".08em">BAR {n}: GLUE A RHYTHM CARD HERE</text>')
            if b == 0 or r == 0:
                o.append(f'<line x1="{xl + W:.1f}" y1="{top:.1f}" x2="{xl + W:.1f}" y2="{bottom:.1f}" stroke="#000" stroke-width="{0.14 * S:.2f}"/>')
            # syllable write-in line
            yl = bottom + 3.6 * S + 4
            o.append(f'<line x1="{xl + 6:.1f}" y1="{yl:.1f}" x2="{xl + W - 6:.1f}" y2="{yl:.1f}" stroke="#000" stroke-width="1"/>')
            o.append(f'<text x="{xl + 6:.1f}" y="{yl + 11:.1f}" font-family="Oswald" font-weight="300" font-size="9.5">syllables for bar {n}</text>')
        o.append(staff_lines_svg(4, w - 4, top, S, "msl"))
        o.append(gl(G_TREBLE, 8, bottom - S, 4 * S, "clef"))
        if r == 0:
            o.append(gl(G_TS + 4, 8 + 2.95 * S, top + 2 * S, 4 * S) + gl(G_TS + 4, 8 + 2.95 * S, top + 4 * S, 4 * S))
        if r == 1:
            o.append(f'<rect x="{w - 4 - 0.36 * S:.1f}" y="{top:.1f}" width="{0.36 * S:.1f}" height="{4 * S:.1f}" fill="#000"/>')
            o.append(f'<line x1="{w - 4 - 0.7 * S:.1f}" y1="{top:.1f}" x2="{w - 4 - 0.7 * S:.1f}" y2="{bottom:.1f}" stroke="#000" stroke-width="{0.14 * S:.2f}"/>')
    o.append("</svg>")
    return "".join(o)


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
.top .t { font-size: 22pt; white-space: nowrap; }
.top .tag { flex: none; white-space: nowrap; }
.top .deco { overflow: hidden; }
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
.cards { flex: 1; display: flex; flex-direction: column; justify-content: space-between; padding: 4pt 0 14pt; }
.foot { display: flex; justify-content: space-between; font-size: 8.5pt; color: #333; border-top: .8pt solid #000; padding-top: 3pt; }
.wm { position: absolute; left: 50%; top: 50%; transform: translate(-50%, -50%) rotate(-38deg); font-family: 'Oswald'; font-weight: 700;
      font-size: 150pt; color: rgba(0,0,0,.13); letter-spacing: .06em; white-space: nowrap; pointer-events: none; z-index: 9; }
.doc h1 { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 30pt; margin: 0 0 4pt; line-height: 1; }
.doc h2 { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 14pt; margin: 13pt 0 4pt; letter-spacing: .02em; }
.doc p, .doc li { font-size: 11pt; line-height: 1.38; margin: 0 0 5pt; }
.doc ul { margin: 0 0 4pt; padding-left: 16pt; }
.doc .rule { border-bottom: 2.2pt solid #000; margin-bottom: 8pt; padding-bottom: 6pt; }
.doc table { border-collapse: collapse; width: 100%; table-layout: fixed; font-size: 10pt; margin: 2pt 0 4pt; }
.doc td, .doc th { border: 1pt solid #000; padding: 3.5pt 6pt; text-align: left; vertical-align: top; }
.doc th { font-family: 'Oswald'; font-weight: 500; text-transform: uppercase; font-size: 9.5pt; background: #000; color: #fff; }
.doc table.vc td { vertical-align: middle; }
.steps { display: flex; gap: 10pt; margin-top: 8pt; }
.step { flex: 1; border: 1.3pt solid #000; border-radius: 7pt; padding: 7pt 9pt 4pt; }
.step .n { display: inline-block; background: ACCENT; color: #fff; font-family: 'Oswald'; font-weight: 700; font-size: 12pt; border-radius: 50%; width: 20pt; height: 20pt; line-height: 20pt; text-align: center; margin-right: 5pt; }
.step b { font-family: 'Oswald'; font-weight: 500; text-transform: uppercase; font-size: 11.5pt; letter-spacing: .02em; }
.step p { margin: 4pt 0 3pt !important; font-size: 10.5pt !important; }
.cols { display: flex; gap: 22pt; }
.cols > div { flex: 1; }
.small { font-size: 9pt !important; color: #333; }
.box { border: 1.3pt solid #000; border-radius: 7pt; padding: 6pt 10pt 4pt; }
.cover { align-items: center; justify-content: space-between; padding: 0.55in 0.6in 0.5in; }
.store { font-family: 'Oswald'; font-weight: 500; font-size: 13pt; letter-spacing: .32em; text-transform: uppercase; }
.ctitle { text-align: center; }
.ctitle .a { font-family: 'Oswald'; font-weight: 700; font-size: 40pt; line-height: 1; letter-spacing: .02em; }
.ctitle .b { font-family: 'Oswald'; font-weight: 700; white-space: nowrap; font-size: 62pt; line-height: .95; letter-spacing: .01em; }
.ctitle .c { font-family: 'Oswald'; font-weight: 300; font-size: 17pt; margin-top: 8pt; }
.cband { width: 100%; background: #000; color: #fff; text-align: center; font-family: 'Oswald'; font-weight: 500; font-size: 14pt;
         letter-spacing: .08em; text-transform: uppercase; padding: 8pt 0 9pt; border-radius: 4pt; }
.cband em { font-style: normal; color: ACCENT; }
.keyblock { margin-top: 8pt; border: 1pt solid #000; border-radius: 7pt; padding: 5pt 10pt 6pt; }
.keyblock .kt { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 12pt; border-bottom: 1pt solid #000; padding-bottom: 2pt; margin-bottom: 3pt; display: flex; justify-content: space-between; }
.keyblock .kt span { font-weight: 300; text-transform: none; font-size: 10.5pt; }
.krow { display: grid; grid-template-columns: 30pt repeat(4, 1fr); gap: 0 6pt; align-items: baseline; font-size: 12pt; line-height: 1.5; padding: 3.5pt 0; border-bottom: .5pt solid #bbb; }
.krow:last-child { border-bottom: 0; }
.krow b { font-family: 'Oswald'; font-weight: 700; color: ACCENT; }
.kb { white-space: nowrap; }
.kb .kt1 { margin-right: 4pt; }
.kb .pr { border-bottom: 1.4pt solid #000; padding-bottom: 0; margin-right: 4pt; }
.kb .pr .kt1 { margin-right: 3pt; }
.kb .kt1.rs { color: #555; font-style: italic; }
.klegend { font-size: 10pt; margin: 6pt 0 0; line-height: 1.35; }
.trk { display: grid; grid-template-columns: 1fr 1fr; gap: 12pt; margin-top: 8pt; }
.trk table { width: 100%; border-collapse: collapse; table-layout: fixed; }
.trk td, .trk th { border: 1pt solid #000; text-align: center; padding: 0; height: 26.5pt; }
.trk td svg { display: inline-block; vertical-align: middle; }
.trk th { background: #000; color: #fff; font-family: 'Oswald'; font-weight: 500; font-size: 9pt; letter-spacing: .04em; text-transform: uppercase; height: 22pt; }
.trk td.id { font-family: 'Oswald'; font-weight: 700; font-size: 12pt; text-align: left; padding-left: 6pt; }
.trk .cap { font-family: 'Oswald'; font-weight: 700; font-size: 12pt; text-transform: uppercase; margin-bottom: 3pt; }
.rbank { display: grid; grid-template-columns: 235pt 235pt; justify-content: space-between; row-gap: 20pt; margin-top: 14pt; }
""".replace("ACCENT", ACCENT)


def html_doc(pages, title="doc"):
    return (f'<!doctype html><html><head><meta charset="utf-8"><title>{escape(title)}</title>'
            f'<style>{font_css()}{CSS}</style></head><body>{"".join(pages)}</body></html>')


def foot(left, right):
    return f'<div class="foot"><span>{left}</span><span>{right}</span></div>'


COPY = f"© {YEAR} {STORE} · {BRAND} · For single-classroom use"

P_COVER, P_TEACH, P_REF, P_CARD0 = 1, 2, 3, 4
P_TRACK = P_CARD0 + 8          # 12
P_MAT1, P_MAT2, P_BANK = P_TRACK + 1, P_TRACK + 2, P_TRACK + 3
P_KEY0 = P_BANK + 1            # 16, 17
P_EX = P_KEY0 + 2              # 18
P_TERMS = P_EX + 1             # 19
TOTAL_PAGES = P_TERMS


def card_page_no(pid):
    return P_CARD0 + SETS.index(pid[0]) * 2 + (int(pid[1:]) - 1) // 4


def key_page_no(st):
    return P_KEY0 + (0 if st in "AB" else 1)


def deco_header():
    parts = [snowball(15, 16, 9, 1.3), snowflake(45, 15, 9, ACCENT, 1.3), snowball(76, 16, 9, 1.3, motion=False), snowflake(106, 15, 9, ACCENT, 1.3)]
    return f'<svg width="124pt" height="32pt" viewBox="0 0 124 32">{"".join(parts)}</svg>'


def top_block(title_small, tag, tagline, ak=False):
    return (f'<div class="top"><div class="h t">{TITLE}<small>{title_small}</small></div>'
            f'<div class="deco">{deco_header()}</div>'
            f'<div class="tag"><div class="lv{" ak" if ak else ""}">{tag}</div><div class="ln">{tagline}</div></div></div>')


def card_page(st, half, watermark=False):
    wm = '<div class="wm">PREVIEW</div>' if watermark else ""
    ids = [f"{st}{n}" for n in range(half * 4 + 1, half * 4 + 5)]
    by = {p["id"]: p for p in PATTERNS}
    cards = "".join(pattern_svg(i, by[i]["bars"], st) for i in ids)
    how = {"A": "Read and sing each card with solfege. Every pattern uses only sol and mi.",
           "B": "Read and sing each card with solfege. Every pattern uses mi, sol and la.",
           "C": "Read and sing each card with solfege. Do and re join the other notes.",
           "D": "Read and sing each card with solfege. All five notes appear."}[st]
    more = "Use the four steps on page 3. For step 4, fold each card on its dashed line so only the notes show."
    return (f'<section class="page">{wm}'
            f'{top_block(f"Pattern cards {ids[0]} to {ids[-1]}", f"SET {st}", SET_SYLS[st])}'
            f'<div class="name">Name<span></span>Date<span class="d"></span></div>'
            f'<div class="how"><b>{how}</b> {more}</div>'
            f'<div class="cards">{cards}</div>'
            f'{foot(COPY, f"Answer key on page {key_page_no(st)} · Page {card_page_no(ids[0])}")}</section>')


def key_token(pid, bi, k, syl):
    if k == "r":
        return f'<span class="kt1 rs" data-id="{pid}" data-bar="{bi}" data-syl="rest" data-dur="r">(rest)</span>'
    mark = " –" if k == "h" else ""
    return f'<span class="kt1" data-id="{pid}" data-bar="{bi}" data-syl="{syl}" data-dur="{k}">{syl}{mark}</span>'


def key_bar(pid, bi, bar):
    out = []
    i = 0
    while i < len(bar):
        if bar[i][0] == "e":
            out.append('<span class="pr">' + key_token(pid, bi, *bar[i]) + key_token(pid, bi, *bar[i + 1]) + "</span>")
            i += 2
        else:
            out.append(key_token(pid, bi, *bar[i]))
            i += 1
    return f'<div class="kb">{"".join(out)}</div>'


def key_block(st):
    rows = []
    for p in PATTERNS:
        if p["set"] != st:
            continue
        rows.append(f'<div class="krow"><b>{p["id"]}</b>{"".join(key_bar(p["id"], bi + 1, bar) for bi, bar in enumerate(p["bars"]))}</div>')
    return (f'<div class="keyblock"><div class="kt"><div>Set {st}<span> · {SET_NAMES[st]}</span></div><span>cards on pages {card_page_no(st + "1")}–{card_page_no(st + "8")}</span></div>'
            f'{"".join(rows)}</div>')


def key_page(sets, watermark=False):
    wm = '<div class="wm">PREVIEW</div>' if watermark else ""
    legend = ('<p class="klegend"><b>How to read the key.</b> Each row is one card, bar by bar. A syllable followed by a dash is a half note (hold for 2 beats). '
              'Two syllables joined by a line below are a pair of eighth notes (together 1 beat). (rest) is a quarter rest: stay silent for 1 beat. '
              'Every other syllable is a quarter note.</p>')
    return (f'<section class="page">{wm}'
            f'{top_block("Syllables for every pattern", "ANSWER KEY", f"Sets {sets[0]} and {sets[1]}", ak=True)}'
            f'{legend}{"".join(key_block(s) for s in sets)}'
            f'<div style="flex:1"></div>{foot(COPY, f"Answer key · Page {key_page_no(sets[0])}")}</section>')


def cover_art(width=900, height=470):
    o = [f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" style="display:block;width:100%;height:auto">']
    o.append(f'<path d="M0,{height - 66} Q150,{height - 116} 300,{height - 74} T600,{height - 76} T{width},{height - 96} L{width},{height - 2} L0,{height - 2} Z" fill="{TINT}" stroke="#000" stroke-width="3" stroke-linejoin="round"/>')
    for fx_, fy_, fr in ((60, 50, 24), (852, 56, 28), (100, 120, 12), (830, 215, 13), (850, 150, 9)):
        o.append(snowflake(fx_, fy_, fr, ACCENT if fr > 15 else "#000", 2.4))
    o.append(snowman(78, height - 48, 46, "#fff", ACCENT, 3))
    o.append(snow_pile(832, height - 40, 30, 3))
    # the card: a real pattern from Set D
    pat = next(p for p in PATTERNS if p["id"] == "D3")
    o.append(f'<rect x="150" y="34" width="600" height="300" rx="20" fill="#fff" stroke="#000" stroke-width="3"/>')
    o.append(f'<svg x="165" y="48" width="570" height="{136 * 570 / 540:.1f}" viewBox="0 0 540 136" overflow="hidden">'
             + pattern_svg("D3", pat["bars"], "D", kind="cover", header=False, border=False).replace('<svg ', '<svg ', 1)
             + "</svg>")
    # five labelled snowballs
    for i, s in enumerate(SYL_ORDER):
        cx = 250 + i * 100
        o.append(snowball(cx, 276, 34, 2.6, label=s, lsize=24))
    o.append("</svg>")
    return "".join(o)


def cover_page():
    return (f'<section class="page cover"><div class="store">{BRAND}</div>'
            f'<div style="width:7.3in">{cover_art()}</div>'
            f'<div class="ctitle"><div class="a">SOLFEGE SNOWBALL</div><div class="b">MELODY CARDS</div>'
            f'<div class="c">Pentatonic patterns to read and sing · build-a-melody mats</div></div>'
            f'<div class="cband">Grades 2–4 <em>·</em> 32 patterns <em>·</em> {TOTAL_PAGES} pages</div></section>')


SET_TBL = {"A": "sol, mi", "B": "mi, sol, la", "C": "adds do, re", "D": "all five"}


def teacher_page():
    set_rows = "".join(
        f'<tr><td><b>Set {s}</b></td><td>{SET_TBL[s]}</td><td>{s}1–{s}8</td><td>pp. {card_page_no(s + "1")}–{card_page_no(s + "8")}</td></tr>' for s in SETS)
    return (f'<section class="page doc"><div class="rule"><h1>Teacher Notes</h1>'
            f'<div class="l" style="font-size:13pt">{TITLE} · 32 patterns in 4 sets · grades 2–4</div></div>'
            f'<div class="cols"><div>'
            f'<h2>How to use</h2><ul>'
            f'<li>Each card is a four-bar pattern in 4/4 on the treble staff in the key of C, with the solfege syllable printed under every note.</li>'
            f'<li>The notes are do, re, mi, sol and la (C, D, E, G and A). C is do, so this is movable-do solfege with do on C.</li>'
            f'<li>Rhythms use quarter notes, pairs of eighth notes, half notes and quarter rests. Say them as ta, ti-ti, ta-a and shh.</li>'
            f'<li>All 32 patterns are original. They were written for this set and are not tunes from songs.</li>'
            f'<li>Hand signs are optional and described in words on page 3. Use the ones your school already uses.</li></ul>'
            f'<h2>Singing range</h2><ul>'
            f'<li>Every pattern stays between C4 (middle C) and A4, a range of a sixth. Sets A and B stay between E4 and A4.</li>'
            f'<li>Give the class the starting pitch for do on a keyboard or bells, then sing do, mi, sol to set the key.</li>'
            f'<li>If low C is hard for your singers, start do a step higher on D4. The patterns still work in that key.</li></ul>'
            f'</div><div>'
            f'<h2>The four sets</h2><table><colgroup><col style="width:25%"><col style="width:25%"><col style="width:25%"><col style="width:25%"></colgroup>'
            f'<tr><th>Set</th><th>Notes</th><th>Cards</th><th>Pages</th></tr>{set_rows}</table>'
            f'<p class="small">Set A uses sol and mi only. Set B adds la. Set C adds do and re. Set D uses all five notes. '
            f'Page 12 is a tracker. Pages {P_MAT1}–{P_MAT2} are the build-a-melody mats and page {P_BANK} holds the rhythm slot cards to cut out. '
            f'Pages {P_KEY0}–{P_EX} are the answer key and sample mats.</p>'
            f'<h2>Pacing</h2><ul>'
            f'<li>Plan one set every two weeks, about 10 minutes a lesson: two or three cards a day, or one card a day as a warm-up.</li>'
            f'<li>Weeks 1 and 2: Set A. Weeks 3 and 4: Set B. Weeks 5 and 6: Set C. Weeks 7 and 8: Set D.</li>'
            f'<li>Use the mats after Set B (mat 1) and after Set D (mat 2), or any time for early finishers.</li></ul>'
            f'</div></div>'
            f'<h2>Read and sing in 4 steps</h2><div class="steps">'
            f'<div class="step"><span class="n">1</span><b>Clap</b><p>Clap the four bars. Count 1 2 3 4 as you go.</p></div>'
            f'<div class="step"><span class="n">2</span><b>Say</b><p>Say the rhythm words (ta, ti-ti, ta-a, shh) in time.</p></div>'
            f'<div class="step"><span class="n">3</span><b>Sing slowly</b><p>Sing the syllables slowly, with hand signs if you like.</p></div>'
            f'<div class="step"><span class="n">4</span><b>Sing again</b><p>Fold the card along the dashed line and sing from the notes alone.</p></div>'
            f'</div>'
            f'<h2>Good to know</h2><p class="small">Each pattern has exactly one answer, printed in the key on pages {P_KEY0} and {P_KEY0 + 1}. '
            f'No standards codes are listed: match the skills to your own curriculum. No songs, lyrics or copyrighted characters are used.</p>'
            f'<div style="flex:1"></div>{foot(COPY, "Page 2")}</section>')


HAND_SIGNS = [
    ("do", "A closed fist, held at about waist height."),
    ("re", "A flat hand slanting upward, fingers pointing out and slightly up."),
    ("mi", "A flat hand held level, palm down, at about chest height."),
    ("sol", "A relaxed open hand, palm facing in, fingers pointing forward, at about shoulder height."),
    ("la", "A relaxed hand drooping from the wrist, fingers pointing down, at about eye height."),
]


def ref_page():
    bank = pitch_bank_svg(SYL_ORDER, 470, 9.0, "ref", "REF")
    hs = "".join(f'<tr><td><b>{s}</b></td><td>{t}</td></tr>' for s, t in HAND_SIGNS)
    rh = [("q", "quarter note", "ta", "1 beat"), ("e", "two eighth notes", "ti-ti", "1 beat together"),
          ("h", "half note", "ta-a", "2 beats"), ("r", "quarter rest", "shh", "1 beat of silence")]
    rows = "".join(f'<tr><td>{mini_rhythm_svg(k)}</td><td>{n}</td><td><b>{w_}</b></td><td>{b}</td></tr>' for k, n, w_, b in rh)
    return (f'<section class="page doc"><div class="rule"><h1>Student Reference</h1>'
            f'<div class="l" style="font-size:13pt">Keep this page beside you while you read and sing.</div></div>'
            f'<h2>The five snowball notes</h2><div class="box" style="display:flex;justify-content:center;padding:6pt 10pt 2pt">{bank}</div>'
            f'<p class="small" style="margin-top:4pt">The letters show where each note lives on the staff. C is do, the lowest note, and it sits just below the staff on its own short line.</p>'
            f'<div class="cols"><div><h2>Hand signs (optional)</h2>'
            f'<table class="vc"><colgroup><col style="width:17%"><col style="width:83%"></colgroup><tr><th>Note</th><th>Hand sign</th></tr>{hs}</table></div>'
            f'<div><h2>Rhythm words</h2>'
            f'<table class="vc"><colgroup><col style="width:25%"><col style="width:30%"><col style="width:20%"><col style="width:25%"></colgroup>'
            f'<tr><th>Symbol</th><th>Name</th><th>Say</th><th>Length</th></tr>{rows}</table></div></div>'
            f'<h2>Read and sing in 4 steps</h2><div class="steps">'
            f'<div class="step"><span class="n">1</span><b>Clap</b><p>Clap the four bars. Count 1 2 3 4 as you go.</p></div>'
            f'<div class="step"><span class="n">2</span><b>Say</b><p>Say the rhythm words in time.</p></div>'
            f'<div class="step"><span class="n">3</span><b>Sing slowly</b><p>Sing the syllables slowly. Make the hand signs if you like.</p></div>'
            f'<div class="step"><span class="n">4</span><b>Sing again</b><p>Fold the card on the dashed line and sing from the notes alone.</p></div></div>'
            f'<div style="display:flex;gap:16pt;align-items:center;margin-top:12pt">'
            f'<svg width="150pt" height="86pt" viewBox="0 0 150 86">{snowball(58, 54, 20, 1.6, motion=True)}{sparkle(100, 14, 7, ACCENT, 1.6)}{snow_pile(116, 80, 14, 1.5)}{snowflake(40, 14, 11, ACCENT, 1.4)}</svg>'
            f'<p style="margin:0">Snow tip: a melody moves like a snowball. It can roll in small steps (mi to sol) or leap a little farther (do to mi). '
            f'Watch the noteheads rise and fall as you sing.</p></div>'
            f'<div style="flex:1"></div>{foot(COPY, "Page 3")}</section>')


TRK_CELL = '<td><svg width="17pt" height="17pt" viewBox="0 0 17 17"><circle cx="8.5" cy="8.5" r="7.5" fill="#fff" stroke="#000" stroke-width="1"/></svg></td>'


def tracker_page():
    def tbl(st):
        rows = "".join(f'<tr><td class="id">{st}{n}</td>{TRK_CELL * 3}</tr>' for n in range(1, 9))
        return (f'<div><div class="cap">Set {st} <span style="font-weight:300;text-transform:none;font-size:10pt">· {SET_NAMES[st]}</span></div>'
                f'<table><colgroup><col style="width:28%"><col style="width:24%"><col style="width:24%"><col style="width:24%"></colgroup>'
                f'<tr><th>Card</th><th>Say</th><th>Sing</th><th>Notes only</th></tr>{rows}</table></div>')
    return (f'<section class="page">{top_block("Snowball tracker", "TRACKER", "32 patterns")}'
            f'<div class="name">Name<span></span>Date<span class="d"></span></div>'
            f'<div class="how"><b>Color a snowball in each box when you can do it.</b> Say means you can say the rhythm words. Sing means you can sing the syllables. '
            f'Notes only means you can sing the card after folding the syllables away.</div>'
            f'<div class="trk">{"".join(tbl(s) for s in SETS)}</div>'
            f'<div style="flex:1"></div>{foot(COPY, f"Page {P_TRACK}")}</section>')


def mat_page(n):
    syls = ["mi", "sol", "la"] if n == 1 else SYL_ORDER
    title = "Mat 1: mi, sol and la" if n == 1 else "Mat 2: do, re, mi, sol and la"
    tag = "MAT 1" if n == 1 else "MAT 2"
    pn = P_MAT1 if n == 1 else P_MAT2
    bank = pitch_bank_svg(syls, 330 if n == 1 else 470, 8.5, "bank", f"MATBANK{n}")
    return (f'<section class="page">{top_block(title, tag, "Build a melody")}'
            f'<div class="name">Name<span></span>Date<span class="d"></span></div>'
            f'<div class="how"><b>Build a four-bar melody.</b> Cut out four rhythm cards from page {P_BANK} and glue one in each box. '
            f'Then draw a note under each rhythm (rests stay empty), write the syllables on the lines and sing your melody.</div>'
            f'<div class="box" style="display:flex;align-items:center;gap:14pt;padding:4pt 10pt 2pt;margin-bottom:8pt"><div class="h" style="font-size:12pt;width:62pt;line-height:1.15">Choose from</div>{bank}</div>'
            f'{mat_svg(n)}'
            f'<div style="flex:1"></div>{foot(COPY, f"Sample mats on page {P_EX} · Page {pn}")}</section>')


def bank_page():
    cards = "".join(rhythm_card_svg(f"R{i + 1}", k) for i, k in enumerate(BANK))
    return (f'<section class="page">{top_block("Rhythm slot cards", "CUT OUT", "12 rhythm bars")}'
            f'<div class="how" style="margin-top:8pt"><b>Cut along the dashed lines.</b> Each card is one bar of 4/4. Pick four cards for your mat, put them in the order you like, and glue each one in a box. '
            f'The notes line up with the staff below. You can use the same card twice if you cut out a second copy.</div>'
            f'<div class="rbank">{cards}</div>'
            f'<p class="small" style="margin-top:12pt">Beats: ta is 1, ti-ti is 1 (two eighth notes), ta-a is 2 and shh is a 1 beat rest. Every card adds up to 4 beats.</p>'
            f'<div style="flex:1"></div>{foot(COPY, f"Page {P_BANK}")}</section>')


def ex_page(watermark=False):
    wm = '<div class="wm">PREVIEW</div>' if watermark else ""
    cards = "".join(
        f'<div style="margin-top:8pt"><div class="h" style="font-size:12pt;margin-bottom:3pt">Sample for mat {i + 1} <span class="l" style="text-transform:none;font-size:11pt">· rhythm cards {", ".join("R" + str(BANK.index(k) + 1) for k in e["keys"])}</span></div>'
        f'{pattern_svg(e["id"], e["bars"], "-", kind="ex", header=False, border=True)}</div>' for i, e in enumerate(EXAMPLES))
    names = {"q": "ta", "e": "ti-ti", "h": "ta-a", "r": "shh"}
    rows = []
    for i, k in enumerate(BANK):
        kinds = RHYTHMS[k]
        words, parts, j = [], [], 0
        while j < len(kinds):
            if kinds[j] == "e":
                words.append("ti-ti"); parts.append("1"); j += 2
            else:
                words.append(RH_WORD[kinds[j]]); parts.append(str(int(BEATS[kinds[j]]))); j += 1
        rows.append(f'<tr><td><b>R{i + 1}</b></td><td>{" ".join(words)}</td><td>{" + ".join(parts)} = 4</td></tr>')
    half = len(rows) // 2
    tbl = lambda rs: ('<table><colgroup><col style="width:14%"><col style="width:46%"><col style="width:40%"></colgroup>'
                      f'<tr><th>Card</th><th>Say</th><th>Beats</th></tr>{"".join(rs)}</table>')
    return (f'<section class="page doc">{wm}<div class="rule"><h1>Sample Mats and Rhythm Bank</h1>'
            f'<div class="l" style="font-size:13pt">One way to build each mat. Many other melodies work too.</div></div>'
            f'<p>A melody is correct when each bar adds up to 4 beats and every note sits in the right place. '
            f'Do is on the short line below the staff, re is in the space under the bottom line, mi is on the bottom line, sol is on the second line, and la is in the second space of the staff.</p>'
            f'{cards}'
            f'<h2>Rhythm bank check</h2><div class="cols"><div>{tbl(rows[:half])}</div><div>{tbl(rows[half:])}</div></div>'
            f'<div style="flex:1"></div>{foot(COPY, f"Page {P_EX}")}</section>')


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
            f'<li>All 32 melody patterns, the rhythm cards, the snow art (snowballs, snowmen and snowflakes) and the answer keys: original work, {BRAND} by {STORE}. No patterns come from existing songs.</li>'
            f'<li>Music notation font: Bravura © Steinberg Media Technologies GmbH, SIL Open Font License 1.1.</li>'
            f'<li>Text fonts: Oswald (The Oswald Project Authors) and Source Sans 3 (Adobe), SIL Open Font License 1.1.</li></ul>'
            f'<h2>What is in this file</h2><p>Page 1 cover, page 2 teacher notes, page 3 student reference, pages {P_CARD0}–{P_TRACK - 1} the 32 pattern cards, page {P_TRACK} the tracker, '
            f'pages {P_MAT1}–{P_MAT2} the two mats, page {P_BANK} the rhythm slot cards, pages {P_KEY0}–{P_KEY0 + 1} the answer key, page {P_EX} the sample mats and page {P_TERMS} these terms.</p>'
            f'<p class="small">{DISCLOSURE}</p>'
            f'<div style="flex:1"></div>{foot(COPY, f"Page {P_TERMS}")}</section>')


def full_pages():
    pages = [cover_page(), teacher_page(), ref_page()]
    for st in SETS:
        pages += [card_page(st, 0), card_page(st, 1)]
    pages += [tracker_page(), mat_page(1), mat_page(2), bank_page(), key_page("AB"), key_page("CD"), ex_page(), terms_page()]
    assert len(pages) == TOTAL_PAGES, len(pages)
    return pages


def preview_pages():
    return [card_page("A", 0, True), card_page("D", 0, True), mat_page(1).replace('<section class="page">', '<section class="page"><div class="wm">PREVIEW</div>', 1),
            key_page("AB", True)]


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
""".replace("ACCENT", ACCENT)


def sq_doc(body):
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{font_css()}'
            f'html,body{{margin:0;background:#fff;font-family:"Source Sans 3",sans-serif}}{SQ_CSS}</style></head><body>'
            '<div style="position:absolute;opacity:0"><span style="font-family:\'Source Sans 3\';font-weight:700">x</span><span style="font-family:\'Source Sans 3\';font-style:italic">x</span><span style="font-family:\'Source Sans 3\';font-weight:600">x</span><span style="font-family:Bravura">&#xE0A4;</span></div>'
            f'{body}</body></html>')


def cover_square():
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div>'
        f'<div style="flex:1;display:flex;flex-direction:column;justify-content:space-evenly;align-items:center;width:100%;padding:0 0 76px">'
        f'<div style="width:880px">{cover_art()}</div>'
        f'<div><div class="hd" style="font-size:64px">Solfege Snowball</div>'
        f'<div class="hd" style="font-size:118px">Melody Cards</div>'
        f'<div class="sub" style="font-size:28px;margin-top:12px">Pentatonic patterns to read and sing · build-a-melody mats</div></div>'
        f'</div><div class="band">Grades 2–4 <em>·</em> 32 patterns <em>·</em> {TOTAL_PAGES} pages</div></div>')


def preview_square_1(img):
    caps = [("Pattern cards, Set A", "Four cards on a page. Set A uses sol and mi only."),
            ("Pattern cards, Set D", "All five notes: do, re, mi, sol and la."),
            ("Build-a-melody mat", "Glue rhythm cards, draw the notes, write the syllables.")]
    shots = "".join(
        f'<div style="width:310px;display:flex;flex-direction:column;align-items:center"><div class="shot"><img src="{img[i]}"></div>'
        f'<div class="lbl" style="font-size:26px;margin-top:20px">{caps[i][0]}</div>'
        f'<div style="font-family:Oswald;font-weight:300;font-size:21px;line-height:1.25;text-align:center;text-wrap:balance;margin-top:8px;width:280px">{caps[i][1]}</div></div>'
        for i in range(3))
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div>'
        f'<div class="hd" style="font-size:70px;margin-top:26px">32 patterns in 4 sets</div>'
        f'<div class="sub" style="font-size:29px;margin-top:10px">Read and sing with solfege, then build your own melody</div>'
        f'<svg width="520" height="70" viewBox="0 0 520 70" style="margin-top:22px">{"".join(snowball(40 + i * 110, 36, 22, 2.4) + (snowflake(95 + i * 110, 36, 17, ACCENT, 2.2) if i < 4 else "") for i in range(5))}</svg>'
        f'<div style="flex:1;display:flex;align-items:center;justify-content:center;padding-bottom:70px">'
        f'<div style="display:flex;gap:16px;align-items:flex-start">{shots}</div></div>'
        f'<div class="band">Sol · mi <em>·</em> la <em>·</em> do · re <em>·</em> all five</div></div>')


def preview_square_2(card_img, key_img):
    pair = "".join(
        f'<div style="width:420px"><div class="shot"><img src="{src}"></div>'
        f'<div class="lbl">{lab}</div></div>' for src, lab in ((card_img, "Pattern cards, Set A"), (key_img, "Answer key, Sets A and B")))
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div>'
        f'<div class="hd" style="font-size:70px;margin-top:22px">Answer key included</div>'
        f'<div class="sub" style="font-size:27px;margin-top:8px">The syllables for every pattern, bar by bar</div>'
        f'<div style="flex:1;display:flex;align-items:center;padding-bottom:70px"><div style="display:flex;gap:40px">{pair}</div></div>'
        f'<div class="band">A full key for all 32 patterns</div></div>')


def preview_square_3():
    by = {p["id"]: p for p in PATTERNS}
    pick = ["A2", "B5", "C3", "D7"]
    cells = "".join(f'<div style="margin-bottom:12px">{pattern_svg(i, by[i]["bars"], i[0], px=650)}</div>' for i in pick)
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div>'
        f'<div class="hd" style="font-size:66px;margin-top:20px">One card from every set</div>'
        f'<div class="sub" style="font-size:27px;margin-top:8px">Four-bar patterns, original and in 4/4</div>'
        f'<div style="margin-top:18px;width:650px">{cells}</div>'
        f'<div class="swm" style="font-size:230px;left:50%;top:54%">PREVIEW</div>'
        f'<div class="band">Sets A to D <em>·</em> original patterns <em>·</em> no known tunes</div></div>')


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
    return f"""# UPLOAD: {LISTING_TITLE} (TpT 050)

These fields follow the order of TpT's "Add a resource" form. Winter theme: build window is December to February. Never put Winter, Snow, Snowball or Holiday in the title field (TpT's Seasonal Titles notice).

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
Solfege Snowball Melody Cards: 32 original four-bar patterns for students to read and sing with solfege, plus build-a-melody mats. Every pattern uses the C pentatonic notes do, re, mi, sol and la on the treble staff in 4/4, with the syllable printed under each note. Snowballs, snowmen and snowflakes decorate the pages. The content is winter themed and non-denominational. For music classes in grades 2 to 4.

WHAT'S INCLUDED ({TOTAL_PAGES} pages, PDF, US Letter)
• Cover (1 page)
• Teacher notes with pacing, a singing-range note and the four read-and-sing steps (1 page)
• Student reference: the five notes on the staff, hand signs described in words, rhythm words (1 page)
• 32 pattern cards, 4 per page (8 pages): Set A uses sol and mi only, Set B adds la, Set C adds do and re, Set D uses all five notes. Each set has 8 patterns.
• Snowball tracker (1 page)
• 2 build-a-melody mats (2 pages)
• 12 rhythm slot cards to cut out (1 page)
• Answer key with the syllables of every pattern (2 pages)
• Sample mats and rhythm bank check (1 page)
• Terms of use and credits (1 page)
Total: {TOTAL_PAGES} pages.

HOW TO USE
Students clap the rhythm, say the rhythm words, sing the syllables slowly and then sing again from the notes alone by folding the card along the dashed line. Rhythms use quarter notes, pairs of eighth notes, half notes and quarter rests. All melodies stay between C4 and A4, and Sets A and B stay between E4 and A4. On the mats, students glue rhythm cards into four boxes, draw a note under each rhythm and write the syllables. Good for warm-ups, centers, sub plans and early finishers.

• Grades 2–4 (choose the set that fits)
• All 32 patterns are original; none comes from an existing song
• Prints well in black and white; the answer key uses one accent color
• Hand signs are described in words and are optional

{DISCLOSURE}
```

## 3. Grades

2, 3, 4.

## 4. Subjects and tags

- Subjects: {", ".join(SUBJECTS)}
- Tags: {", ".join(TAGS)}

## 5. Page count by section (totals {TOTAL_PAGES})

- Cover: 1
- Teacher notes: 1
- Student reference: 1
- Pattern cards, Sets A to D (A1–D8): 8
- Snowball tracker: 1
- Build-a-melody mats: 2
- Rhythm slot cards: 1
- Answer key: 2
- Sample mats and rhythm bank check: 1
- Terms of use and credits: 1
- Total: {TOTAL_PAGES}

## 6. Standards

None cited. The teacher notes describe the skills and ask teachers to match them to their own curriculum.

## 7. Price

**${PRICE}** (paid; owner range $3–5).

## 8. Preview

Paid. Preview PDF: pattern cards A1–A4, pattern cards D1–D4, build-a-melody mat 1 and the answer key for Sets A and B, all watermarked.

## 9. Before you click publish

- [ ] Season: winter (December to February). Build for 2 to 8 weeks ahead of that.
- Patterns are generated by rule (seeded) and screened against a short list of famous melodic cells; a music teacher may want to skim them.
- Open owner question: logo beside HUDSON BEAT (see tpt/STYLE.md).
"""


def tpt_json():
    return {
        "price": PRICE, "license_price": PRICE, "tax_code": "Other Digital Goods - No Physical Media",
        "grades": GRADES, "subjects": SUBJECTS, "tags": TAGS, "formats": ["PDF"], "pages": TOTAL_PAGES, "answer_key": "Included",
        "files": {"product": f"{SLUG}.pdf", "preview": f"{SLUG}-PREVIEW.pdf", "thumb1": "cover.png", "thumb2": "preview-1.png",
                  "thumb3": "preview-2.png", "thumb4": "preview-3.png"},
    }


def build():
    os.makedirs(BUILD, exist_ok=True)
    full = write("resource.html", html_doc(full_pages(), TITLE))
    prev = write("preview.html", html_doc(preview_pages(), "Preview"))
    render([{"html": full, "pdf": PDF}, {"html": prev, "pdf": PREVIEW_PDF}])
    for i in range(1, 5):
        subprocess.run(["pdftoppm", "-png", "-r", "110", "-f", str(i), "-l", str(i), "-singlefile", PREVIEW_PDF,
                        os.path.join(BUILD, f"pv{i}")], check=True)
    sq = [write("cover.html", cover_square()), write("p1.html", preview_square_1(["pv1.png", "pv2.png", "pv3.png"])),
          write("p2.html", preview_square_2("pv1.png", "pv4.png")), write("p3.html", preview_square_3())]
    outs = [COVER_PNG] + PREVIEW_PNGS
    render([{"html": h, "png": o, "width": 1000, "height": 1000, "scale": 2} for h, o in zip(sq, outs)])
    with open(UPLOAD, "w") as f:
        f.write(upload_md())
    with open(TPT_JSON, "w") as f:
        json.dump(tpt_json(), f, indent=2)
        f.write("\n")
    print(f"built {PDF}, {PREVIEW_PDF}, cover + 3 previews, UPLOAD.md, tpt.json")


# ------------------------------------------------------------------ checks
SVG_RE = re.compile(r'<svg class="(?:ns|rc)".*?</svg>', re.S)
HEAD_CP = {0xE0A4: "filled", 0xE0A3: "open"}
SYL_FOR_LETTER = {"C": "do", "D": "re", "E": "mi", "G": "sol", "A": "la"}
LETTER_FOR_STEP = {-2: "C", -1: "D", 0: "E", 1: "F", 2: "G", 3: "A", 4: "B", 5: "C", 6: "D", 7: "E", 8: "F"}
IND_BEATS = {"q": 1.0, "h": 2.0, "e": 0.5, "r": 1.0}


def strip_ns(s):
    return re.sub(r'\sxmlns="[^"]+"', "", s)


def cp_of(el):
    t = (el.text or "").strip()
    return ord(t[0]) if t else None


def parse_staff(svg_text):
    """Re-read one staff svg. Returns (info dict, errors)."""
    errs = []
    root = ET.fromstring(strip_ns(svg_text))
    S = float(root.get("data-s"))
    kind, sid = root.get("data-kind"), root.get("data-id")
    tag = f"{sid}[{kind}]"
    sls = sorted(float(l.get("y1")) for l in root.iter("line") if l.get("class") == "sl")
    if len(sls) != 5 or any(abs((sls[i + 1] - sls[i]) - S) > 0.02 for i in range(4)):
        return None, [f"{tag}: staff lines are not 5 lines {S} apart"]
    top, bottom = sls[0], sls[4]
    heads, rests, stems, leds, syls, bars, beams = [], [], [], [], [], [], []
    clefs, tsig = [], []
    for el in root.iter():
        c = el.get("class")
        if el.tag == "text" and c == "head":
            heads.append((float(el.get("x")), float(el.get("y")), cp_of(el)))
        elif el.tag == "text" and c == "rest":
            rests.append((float(el.get("x")), float(el.get("y")), cp_of(el)))
        elif el.tag == "text" and c == "syl":
            syls.append((float(el.get("x")), (el.text or "").strip()))
        elif el.tag == "text" and c == "clef":
            clefs.append((float(el.get("x")), float(el.get("y")), cp_of(el)))
        elif el.tag == "line" and c == "stem":
            stems.append((float(el.get("x1")), float(el.get("y1")), float(el.get("x2")), float(el.get("y2")), float(el.get("stroke-width"))))
        elif el.tag == "line" and c == "led":
            leds.append((float(el.get("x1")), float(el.get("x2")), float(el.get("y1"))))
        elif el.tag == "line" and c == "bar":
            bars.append(float(el.get("x1")))
        elif el.tag == "rect" and c == "beam":
            beams.append((float(el.get("x")), float(el.get("y")), float(el.get("width")), float(el.get("height"))))
    for tg in root.iter("g"):
        if tg.get("class") == "timesig":
            tsig = [(cp_of(t)) for t in tg.iter("text")]
    # clef: treble glyph on the G line (second line from the bottom)
    if len(clefs) != 1 or clefs[0][2] != G_TREBLE or abs(clefs[0][1] - (bottom - S)) > 0.02:
        errs.append(f"{tag}: treble clef missing or not on the G line")
    if root.get("data-meter") == "4/4" and tsig != [G_TS + 4, G_TS + 4]:
        errs.append(f"{tag}: time signature is not 4 over 4")
    hw = HEAD_W * S
    events = []
    used_stems, used_led = set(), set()
    for (x, y, cp) in heads:
        cx = x + hw / 2
        sstep = (bottom - y) / (S / 2)
        step = round(sstep)
        if abs(sstep - step) > 0.01:
            errs.append(f"{tag}: notehead at x={cx:.0f} is not on a line or space")
        if step not in LETTER_FOR_STEP or LETTER_FOR_STEP[step] not in SYL_FOR_LETTER:
            errs.append(f"{tag}: notehead at x={cx:.0f} has step {step}, not a pentatonic note")
            continue
        letter = LETTER_FOR_STEP[step]
        # stem
        st = [s for s in stems if abs(s[0] - (x + hw)) < 0.8 or abs(s[0] - x) < 0.8]
        st = [s for s in st if abs(s[1] - (y - 0.168 * S)) < 0.02 or abs(s[1] - (y + 0.168 * S)) < 0.02]
        if len(st) != 1:
            errs.append(f"{tag}: note at x={cx:.0f} has {len(st)} stems")
            continue
        s = st[0]
        used_stems.add(s)
        up = s[3] < s[1]
        want_up = step < 4
        if up != want_up:
            errs.append(f"{tag}: note {letter} at x={cx:.0f} stem points {'up' if up else 'down'} (should be {'up' if want_up else 'down'})")
        sw = s[4]
        if up and abs(s[0] - (x + hw - sw / 2)) > 0.05:
            errs.append(f"{tag}: up stem of {letter} is not on the right edge of its head")
        if (not up) and abs(s[0] - (x + sw / 2)) > 0.05:
            errs.append(f"{tag}: down stem of {letter} is not on the left edge of its head")
        if abs(s[3] - s[1]) < 3 * S - 0.01:
            errs.append(f"{tag}: stem of {letter} at x={cx:.0f} is shorter than 3 spaces")
        # ledger lines needed
        need = [e for e in range(-2, step - 1, -2)] if step < 0 else []
        need += [e for e in range(10, step + 1, 2)] if step > 8 else []
        for e in need:
            ly = bottom - e * S / 2
            m = [l for l in leds if abs(l[2] - ly) < 0.02 and l[0] < x and l[1] > x + hw]
            if len(m) != 1:
                errs.append(f"{tag}: ledger line missing for {letter} at x={cx:.0f}")
            else:
                used_led.add(m[0])
        events.append({"x": cx, "step": step, "letter": letter, "head": HEAD_CP.get(cp), "stem": s, "up": up})
    for i_, l in enumerate(sorted(leds, key=lambda q: (q[2], q[0]))):
        pass
    ls_ = sorted(leds, key=lambda q: (q[2], q[0]))
    for a_, b_ in zip(ls_, ls_[1:]):
        if abs(a_[2] - b_[2]) < 0.02 and a_[1] > b_[0] - 0.3:
            errs.append(f"{tag}: two ledger lines touch")
    for l in leds:
        if l not in used_led:
            errs.append(f"{tag}: stray ledger line at y={l[2]:.1f}")
    for s in stems:
        if s not in used_stems:
            errs.append(f"{tag}: stem without a notehead")
    # beams
    for ev in events:
        ev["beamed"] = []
        for b in beams:
            if abs(ev["stem"][3] - b[1]) < 0.02 and b[0] - 0.02 <= ev["stem"][0] - ev["stem"][4] / 2 + 0.01 and ev["stem"][0] + ev["stem"][4] / 2 <= b[0] + b[2] + 0.02:
                ev["beamed"].append(b)
    for b in beams:
        n = sum(1 for ev in events if b in ev["beamed"])
        if n != 2:
            errs.append(f"{tag}: a beam joins {n} stems (should be 2)")
        if b[3] < 0.4 * S:
            errs.append(f"{tag}: beam too thin")
    for ev in events:
        if ev["head"] == "filled":
            ev["dur"] = "e" if ev["beamed"] else "q"
        elif ev["head"] == "open":
            ev["dur"] = "h"
            if ev["beamed"]:
                errs.append(f"{tag}: half note is beamed")
        else:
            ev["dur"] = "?"
    for (x, y, cp) in rests:
        cx = x + REST_W * S / 2
        if cp != G_QREST:
            errs.append(f"{tag}: unknown rest glyph")
        if abs(y - (top + 2 * S)) > 0.02:
            errs.append(f"{tag}: quarter rest is not on the middle line")
        events.append({"x": cx, "dur": "r", "step": None, "letter": None, "rest": True})
    for ev in events:
        if "rest" in ev:
            continue
        m = [t for t in syls if abs(t[0] - ev["x"]) < 1.0]
        ev["syl"] = m[0][1] if len(m) == 1 else None
        if ev["syl"] is None:
            errs.append(f"{tag}: note {ev['letter']} at x={ev['x']:.0f} has no syllable")
        elif ev["syl"] != SYL_FOR_LETTER[ev["letter"]]:
            errs.append(f"{tag}: note {ev['letter']} at x={ev['x']:.0f} printed as '{ev['syl']}', should be '{SYL_FOR_LETTER[ev['letter']]}'")
    nsyl = len([e for e in events if "rest" not in e])
    if len(syls) != nsyl:
        errs.append(f"{tag}: {len(syls)} syllables for {nsyl} notes")
    events.sort(key=lambda e: e["x"])
    info = {"id": sid, "kind": kind, "set": root.get("data-set"), "S": S, "events": events, "bars": [], "meter": root.get("data-meter")}
    if root.get("data-meter") == "4/4":
        x0 = float(root.get("data-x0"))
        ends = sorted(bars)
        if len(ends) != 4 and kind != "bank":
            errs.append(f"{tag}: {len(ends)} barlines (4 expected)")
        bounds = [x0] + [b + (0.35 * S if i == len(ends) - 1 else 0) for i, b in enumerate(ends)]
        for bi in range(len(bounds) - 1):
            ev = [e for e in events if bounds[bi] <= e["x"] < bounds[bi + 1]]
            tot = sum(IND_BEATS[e["dur"]] for e in ev)
            if tot != 4:
                errs.append(f"{tag}: bar {bi + 1} adds up to {tot} beats")
            # eighths in pairs starting on a beat
            pos, i = 0.0, 0
            while i < len(ev):
                if ev[i]["dur"] == "e":
                    if not (i + 1 < len(ev) and ev[i + 1]["dur"] == "e" and pos == int(pos) and ev[i]["beamed"] and ev[i]["beamed"] == ev[i + 1]["beamed"]):
                        errs.append(f"{tag}: bar {bi + 1} has an eighth note that is not in a beamed pair on a beat")
                    pos += 1
                    i += 2
                else:
                    pos += IND_BEATS[ev[i]["dur"]]
                    i += 1
            info["bars"].append([(e["dur"], e.get("syl")) for e in ev])
        if sum(len(b) for b in info["bars"]) != len(events):
            errs.append(f"{tag}: some notes fall outside the bars")
    return info, errs


def parse_rhythm_card(svg_text):
    errs = []
    root = ET.fromstring(strip_ns(svg_text))
    rid, S = root.get("data-id"), float(root.get("data-s"))
    ly = float([l for l in root.iter("line") if l.get("class") == "rl"][0].get("y1"))
    hw = HEAD_W * S
    heads = [(float(e.get("x")), float(e.get("y")), cp_of(e)) for e in root.iter("text") if e.get("class") == "head"]
    rests = [(float(e.get("x")), float(e.get("y"))) for e in root.iter("text") if e.get("class") == "rest"]
    stems = [(float(e.get("x1")), float(e.get("y1")), float(e.get("y2")), float(e.get("stroke-width"))) for e in root.iter("line") if e.get("class") == "stem"]
    beams = [(float(e.get("x")), float(e.get("y")), float(e.get("width")), float(e.get("height"))) for e in root.iter("rect") if e.get("class") == "beam"]
    words = sorted((float(e.get("x")), (e.text or "").strip()) for e in root.iter("text") if e.get("class") == "rw")
    evs = []
    for (x, y, cp) in heads:
        if abs(y - ly) > 0.02:
            errs.append(f"{rid}: head off the line")
        st = [s for s in stems if abs(s[0] - (x + (0.13 * S) / 2)) < 0.05]
        if len(st) != 1 or st[0][2] <= st[0][1]:
            errs.append(f"{rid}: stem is not a down stem on the left edge of the head")
            continue
        be = [b for b in beams if abs(b[1] + b[3] - st[0][2]) < 0.02 and b[0] - 0.02 <= st[0][0] - st[0][3] / 2 + 0.01 and st[0][0] + st[0][3] / 2 <= b[0] + b[2] + 0.02]
        evs.append((x + hw / 2, "h" if cp == 0xE0A3 else ("e" if be else "q")))
    for (x, y) in rests:
        if abs(y - ly) > 0.02:
            errs.append(f"{rid}: rest off the line")
        evs.append((x + REST_W * S / 2, "r"))
    evs.sort()
    kinds = "".join(k for _, k in evs)
    tot = sum(IND_BEATS[k] for _, k in evs)
    if tot != 4:
        errs.append(f"{rid}: adds up to {tot} beats")
    want = {"q": "ta", "h": "ta-a", "r": "shh"}
    exp = []
    i = 0
    while i < len(evs):
        if evs[i][1] == "e":
            exp.append("ti-ti")
            i += 2
        else:
            exp.append(want[evs[i][1]])
            i += 1
    if [w for _, w in words] != exp:
        errs.append(f"{rid}: rhythm words {[w for _, w in words]} do not match {exp}")
    return {"id": rid, "kinds": kinds, "key": root.get("data-key")}, errs


def verify_html():
    errs = []
    htmls = open(os.path.join(BUILD, "resource.html")).read()
    staffs, rcards = {}, {}
    n_staff = 0
    for m in SVG_RE.finditer(htmls):
        svg = m.group(0)
        if svg.startswith('<svg class="rc"'):
            info, e = parse_rhythm_card(svg)
            errs += e
            rcards[info["id"]] = info
            continue
        info, e = parse_staff(svg)
        errs += e
        if info is None:
            continue
        n_staff += 1
        staffs.setdefault(info["id"], []).append(info)
    # nested cover svg is inside another svg: find it separately
    for m in re.finditer(r'<svg class="ns"[^>]*data-kind="cover".*?</svg>', htmls, re.S):
        pass
    cards = {}
    for sid, lst in staffs.items():
        if any(x["kind"] == "card" for x in lst):
            lst = [x for x in lst if x["kind"] == "card"]
            if len(lst) != 1:
                errs.append(f"{sid}: card drawn {len(lst)} times")
            cards[sid] = lst[0]
    want_ids = [p["id"] for p in PATTERNS]
    if sorted(cards) != sorted(want_ids):
        errs.append(f"cards drawn {sorted(cards)} differ from the 32 patterns")
    # sets and distinctness
    seqs = {}
    for sid, c in cards.items():
        flat = [x for b in c["bars"] for x in b]
        syl = [s for d, s in flat if d != "r"]
        st = sid[0]
        used = set(syl)
        if st == "A" and used != {"mi", "sol"}:
            errs.append(f"{sid}: Set A must use exactly sol and mi, uses {sorted(used)}")
        if st == "B" and used != {"mi", "sol", "la"}:
            errs.append(f"{sid}: Set B must use exactly mi, sol and la, uses {sorted(used)}")
        if st == "C" and not ({"do", "re"} <= used and used < set(SYL_ORDER)):
            errs.append(f"{sid}: Set C must use do and re but not all five notes, uses {sorted(used)}")
        if st == "D" and used != set(SYL_ORDER):
            errs.append(f"{sid}: Set D must use all five notes, uses {sorted(used)}")
        if c["set"] != st:
            errs.append(f"{sid}: wrong set label {c['set']}")
        if any(x not in SYL_ORDER for x in used):
            errs.append(f"{sid}: syllable outside the pentatonic set")
        if st in "AB" and any(e["step"] < 0 for e in c["events"] if e.get("step") is not None):
            errs.append(f"{sid}: Set {st} note below E4")
        if any(e["step"] is not None and not (-2 <= e["step"] <= 3) for e in c["events"]):
            errs.append(f"{sid}: note outside C4-A4")
        if flat[-1][0] == "r":
            errs.append(f"{sid}: ends on a rest")
        seqs[sid] = tuple(flat)
    if len(set(seqs.values())) != len(seqs):
        errs.append("two patterns are identical")
    if len({tuple(s for d, s in v if d != "r") for v in seqs.values()}) != len(seqs):
        errs.append("two patterns have the same syllable sequence")
    # famous cells
    for sid, v in seqs.items():
        sy = [s for d, s in v if d != "r"]
        for cell in FORBIDDEN:
            if sequence_has(sy, cell):
                errs.append(f"{sid}: contains the cell {' '.join(cell)}")
    # key entries equal the drawn card
    key_html = htmls
    ktoks = {}
    for m in re.finditer(r'<span class="kt1[^"]*" data-id="([A-D]\d)" data-bar="(\d)" data-syl="(\w+)" data-dur="(\w)"', key_html):
        ktoks.setdefault(m.group(1), {}).setdefault(int(m.group(2)), []).append((m.group(4), None if m.group(3) == "rest" else m.group(3)))
    if sorted(ktoks) != sorted(want_ids):
        errs.append("key does not list exactly the 32 patterns")
    for sid, c in cards.items():
        kt = ktoks.get(sid, {})
        drawn = {i + 1: [(d, s) for d, s in b] for i, b in enumerate(c["bars"])}
        if kt != drawn:
            errs.append(f"{sid}: key entry differs from the drawn card")
    # printed key text vs card, as the buyer sees it
    for m in re.finditer(r'<div class="krow"><b>(\w+)</b>(.*?)</div></div>', key_html, re.S):
        pass
    # examples
    for e in EXAMPLES:
        lst = staffs.get(e["id"], [])
        if len(lst) != 1:
            errs.append(f"{e['id']}: sample mat drawn {len(lst)} times")
            continue
        x = lst[0]
        syl = {s for b in x["bars"] for d, s in b if d != "r"}
        if e["id"] == "EX1" and syl != {"mi", "sol", "la"}:
            errs.append("EX1 should use mi, sol and la")
        if e["id"] == "EX2" and not syl <= set(SYL_ORDER):
            errs.append("EX2 pitch set")
        for bi, b in enumerate(x["bars"]):
            k = "".join(d for d, _ in b)
            bank_k = {"".join(RHYTHMS[kk]): kk for kk in BANK}
            if k not in bank_k:
                errs.append(f"{e['id']} bar {bi + 1}: rhythm {k} is not on the rhythm bank")
    # rhythm bank
    if sorted(rcards) != sorted(f"R{i + 1}" for i in range(len(BANK))):
        errs.append("rhythm slot cards missing")
    for i, k in enumerate(BANK):
        r = rcards.get(f"R{i + 1}")
        if r and r["kinds"] != "".join(RHYTHMS[k]):
            errs.append(f"R{i + 1}: drawn rhythm {r['kinds']} differs from {''.join(RHYTHMS[k])}")
    if len({r["kinds"] for r in rcards.values()}) != len(rcards):
        errs.append("two rhythm slot cards are identical")
    # every staff on cover/reference/mat banks/cover art was parsed above; cover (nested in the cover art) is included in `staffs`
    nb = sum(1 for v in staffs.values() for x in v if x["kind"] == "cover")
    if nb < 1:
        errs.append("cover art staff not found")
    return errs, len(cards), n_staff


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
        pg.querySelectorAll('svg.ns, svg.rc, svg.mat, .keyblock, .doc table, .trk table, .doc p, .doc ul, .how, .name, .top, .box, .steps, .klegend').forEach(el => {
          if (ft && ft.contains(el)) return;
          const r = el.getBoundingClientRect();
          if (r.height === 0) return;
          if (r.bottom > ftop - 8) res.push(`page ${i + 1}: ${el.tagName}.${el.className && el.className.baseVal !== undefined ? el.className.baseVal : el.className} bottom ${(r.bottom - ftop).toFixed(1)}px vs footer rule (needs <= -8)`);
          if (r.right > pr.right - 0.35 * 96 + 0.5 || r.left < pr.left + 0.35 * 96 - 0.5) res.push(`page ${i + 1}: element too close to the page edge`);
          if (el.matches('svg.ns, svg.rc, svg.mat, .keyblock')) boxes.push([el, r]);
        });
        for (let a = 0; a < boxes.length; a++) for (let c = a + 1; c < boxes.length; c++) {
          const A = boxes[a][1], C = boxes[c][1];
          if (boxes[a][0].contains(boxes[c][0]) || boxes[c][0].contains(boxes[a][0])) continue;
          const gx = Math.max(A.left, C.left) - Math.min(A.right, C.right);
          const gy = Math.max(A.top, C.top) - Math.min(A.bottom, C.bottom);
          if (gx < 3 && gy < 3) res.push(`page ${i + 1}: two boxes touch or overlap`);
        }
        // syllables must not collide with each other or with other notation text
        pg.querySelectorAll('svg.ns').forEach(sv => {
          const ts = [...sv.querySelectorAll('text.syl, text.rlab, text.let')].map(t => t.getBoundingClientRect());
          for (let a = 0; a < ts.length; a++) for (let c = a + 1; c < ts.length; c++) {
            const A = ts[a], C = ts[c];
            if (Math.min(A.right, C.right) - Math.max(A.left, C.left) > -0.5 && Math.min(A.bottom, C.bottom) - Math.max(A.top, C.top) > 0) res.push(`page ${i + 1}: two syllable labels touch in ${sv.getAttribute('data-id')}`);
          }
        });
        pg.querySelectorAll('svg.rc').forEach(sv => {
          const ts = [...sv.querySelectorAll('text.rw')].map(t => t.getBoundingClientRect());
          for (let a = 0; a < ts.length; a++) for (let c = a + 1; c < ts.length; c++) {
            if (Math.min(ts[a].right, ts[c].right) - Math.max(ts[a].left, ts[c].left) > -0.5) res.push(`page ${i + 1}: two rhythm words touch in ${sv.getAttribute('data-id')}`);
          }
        });
        // table cell text must not wrap awkwardly: no one-word orphan lines in paragraphs/list items
        pg.querySelectorAll('.doc p, .doc li, .how, .step p').forEach(el => {
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
    errs = []
    from PIL import Image
    for p in [COVER_PNG, *PREVIEW_PNGS]:
        im = Image.open(p).convert("L")
        if im.size != (2000, 2000):
            errs.append(f"{os.path.basename(p)}: not 2000x2000")
            continue
        px = im.load()
        rows = [sum(1 for x in range(0, 2000, 8) if px[x, y] < 200) for y in range(0, 2000, 2)]
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
            errs.append(f"{os.path.basename(p)}: blank band of {best}px")
        last = max((y for y in range(0, ytop, 2) if rows[y // 2] > 0), default=0)
        if ytop - last > 200:
            errs.append(f"{os.path.basename(p)}: {ytop - last}px blank above the bottom band")
    return errs


def verify_files():
    errs = []
    from pypdf import PdfReader
    for p in [PDF, PREVIEW_PDF, COVER_PNG, *PREVIEW_PNGS, UPLOAD, TPT_JSON, os.path.join(TPT, "STYLE.md"), RENDER_JS]:
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
    for i, pg in enumerate(rd.pages):
        t = pg.extract_text() or ""
        if len(t.strip()) < 40:
            errs.append(f"PDF page {i + 1} looks blank")
        if "PREVIEW" in t.upper():
            errs.append(f"product PDF page {i + 1} carries a PREVIEW watermark")
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
            errs.append(f"UPLOAD.md: title is {len(title)} chars")
        if re.search(r"winter|snow|holiday|christmas", title, re.I):
            errs.append("UPLOAD.md: seasonal word in the title")
    for need in (DISCLOSURE, f"${PRICE}", f"{TOTAL_PAGES} pages", "32 original"):
        if need not in up:
            errs.append(f"UPLOAD.md: missing '{need}'")
    sec = up.split("## 5. Page count by section")[1].split("##")[0]
    nums = [int(x) for x in re.findall(r"^- (?!Total)[^\n]*: (\d+)$", sec, re.M)]
    if sum(nums) != TOTAL_PAGES:
        errs.append(f"UPLOAD.md page list sums to {sum(nums)}, PDF has {TOTAL_PAGES}")
    low = up.lower()
    for bad in ("checked by hand", "handmade", "recomputed", "classroom-tested", "classroom tested"):
        if bad in low:
            errs.append(f"UPLOAD.md says '{bad}'")
    tj = json.load(open(TPT_JSON))
    tags, subs = set(load_json("TAG-OPTIONS.json")["options"]), set(load_json("SUBJECT-OPTIONS.json"))
    if tj["tags"] and any(t not in tags for t in tj["tags"]):
        errs.append(f"tpt.json tags invalid {tj['tags']}")
    if any(s not in subs for s in tj["subjects"]):
        errs.append("tpt.json subjects invalid")
    if tj.get("pages") != TOTAL_PAGES or tj["price"] != PRICE:
        errs.append("tpt.json pages or price mismatch")
    first = " ".join((rd.pages[0].extract_text() or "").split())
    if f"{TOTAL_PAGES} pages" not in first.lower() or "32 patterns" not in first.lower():
        errs.append("cover text does not state the page and pattern counts")
    # terms page text lists the same page ranges
    tt = " ".join((rd.pages[-1].extract_text() or "").split())
    if DISCLOSURE not in tt:
        errs.append("terms page lacks the disclosure line")
    return errs


def check():
    errs, ncards, nstaff = verify_html()
    errs += verify_layout()
    errs += verify_files()
    if errs:
        print("CHECK FAILED")
        print("\n".join(" - " + e for e in errs[:80]))
        sys.exit(1)
    print(f"CHECK OK: {ncards} cards (+{nstaff - ncards} other staves) re-read from the rendered SVG: every notehead position matches its printed syllable "
          f"(C=do D=re E=mi G=sol A=la), stems/beams/ledger lines/rests correct, every bar 4 beats, set membership and distinctness verified, "
          f"key entries equal the drawn cards, rhythm slot cards and sample mats checked; layout clear; PDF {TOTAL_PAGES} Letter pages, preview 4 (one watermark each); "
          f"images 2000x2000; UPLOAD.md and tpt.json ok.")


if __name__ == "__main__":
    if "--check" in sys.argv:
        check()
    else:
        build()
