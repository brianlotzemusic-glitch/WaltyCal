#!/usr/bin/env python3
"""Roll and Compose, Winter (TpT 051): build the resource and verify it.

    python3 gen.py           build everything (PDFs, PNGs, UPLOAD.md, tpt.json) into this folder
    python3 gen.py --check   re-read every drawn staff from the rendered HTML and verify notation, dice tables, examples, rubric and layout

Students roll a die (1-6) and look the number up in a dice table:
  Level A  one roll = one beat of rhythm (4 bars of 4/4, one-line staff)
  Level B  rhythm die (one roll per beat) and pitch die (one roll per note), C pentatonic, 4 bars, treble staff
  Level C  rhythm die (one roll = one whole bar) and pitch die, 8 bars, call and response, given last notes (G, then C)
The three completed examples are generated from their rolls. `--check` does not trust that: it re-reads every drawn staff from the
rendered SVG (staff lines, clef, time signature, noteheads, stems, beams, ledger lines, rests, barlines, labels), derives each note
value and pitch from the drawing, rebuilds every example from the rolls printed in its roll table with a separate rule table, and
compares the two. It also checks the dice tables, die faces, bar sums, the rubric total and every page-count claim.
"""
import json
import math
import os
import random
import re
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

SLUG = "roll-and-compose-dice-composing"
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
TITLE = "Roll and Compose"
LISTING_TITLE = "Music Composition Dice Game: Rhythm and Melody Roll and Compose, Gr 2-5"
PREFERRED_TITLE = "Roll and Compose, Winter: Dice Composing for Rhythm and Melody | Music Gr 2-5"
PRICE = "4.00"
TAGS = ["Winter", "Games", "Activities", "Rubrics", "Printables"]
SUBJECTS = ["Music", "Music Composition"]
GRADES = ["2nd-grade", "3rd-grade", "4th-grade", "5th-grade"]

# ------------------------------------------------------------------ page map
P_COVER, P_TEACH, P_REF = 1, 2, 3
P_A_TBL, P_A_REC, P_B_TBL, P_B_REC, P_C_TBL, P_C_REC = 4, 5, 6, 7, 8, 9
P_ST4, P_ST8, P_EX1, P_EX2, P_RUB, P_SHARE, P_TERMS = 10, 11, 12, 13, 14, 15, 16
TOTAL_PAGES = P_TERMS
PAGE_KEYS = {   # a phrase that appears only on that page (the page-order check searches the PDF text for it)
    P_TEACH: "Teacher Notes", P_REF: "Student Reference", P_A_TBL: "Dice table: one roll, one beat", P_A_REC: "Roll and record: rhythm",
    P_B_TBL: "Dice tables: rhythm and pitch", P_B_REC: "Roll and record: melody", P_C_TBL: "Dice tables: two dice", P_C_REC: "Roll and record: 8 bars",
    P_ST4: "Blank staff paper, 4 bars", P_ST8: "Blank staff paper, 8 bars", P_EX1: "Examples for Level A and Level B",
    P_EX2: "Example for Level C", P_RUB: "Sharing Rubric", P_SHARE: "Share and perform", P_TERMS: "Terms of Use",
}

# ------------------------------------------------------------------ music rules (generator side)
# Step = diatonic steps above the bottom staff line of the treble staff (E4 = 0).
STEP = {"C4": -2, "D4": -1, "E4": 0, "G4": 2, "A4": 3, "C5": 5}
LETTER = {"C4": "C", "D4": "D", "E4": "E", "G4": "G", "A4": "A", "C5": "C"}
SOLFEGE = {"C4": "do", "D4": "re", "E4": "mi", "G4": "sol", "A4": "la", "C5": "do"}
BEATS = {"q": 1.0, "h": 2.0, "e": 0.5, "r": 1.0}
WORD = {"q": "ta", "h": "ta-a", "e": "ti", "r": "shh"}
A_FACE = {1: "q", 2: "q", 3: "ee", 4: "ee", 5: "r", 6: "q"}          # Level A: one roll fills one beat
B_RHY = {1: "q", 2: "q", 3: "q", 4: "ee", 5: "ee", 6: "ee"}          # Level B rhythm die: one roll fills one beat
B_PITCH = {1: "C4", 2: "D4", 3: "E4", 4: "G4", 5: "A4"}              # Level B pitch die (6 = free choice)
C_CELL = {1: "qqqq", 2: "qqh", 3: "qeeqq", 4: "eeeeh", 5: "hh", 6: "qqqr"}   # Level C rhythm die: one roll fills one bar
C_PITCH = {1: "C4", 2: "D4", 3: "E4", 4: "G4", 5: "A4", 6: "C5"}
C_GIVEN = {3: "G4", 7: "C4"}      # bar index (0-based) -> last note you play, printed on the sheet
B_GIVEN = {3: "C4"}
KINDS = {"q": ["q"], "ee": ["e", "e"], "r": ["r"]}
A_KINDS = {r: KINDS[v] for r, v in A_FACE.items()}
B_KINDS = {r: KINDS[v] for r, v in B_RHY.items()}
STEPS_NAMES = ["Roll", "Look", "Draw", "Play"]
for _c in C_CELL.values():
    assert sum(BEATS[k] for k in _c) == 4
for _v in A_FACE.values():
    assert sum(BEATS[k] for k in _v) == 1
for _v in B_RHY.values():
    assert sum(BEATS[k] for k in _v) == 1


def ev(d, p=None, given=False):
    return {"d": d, "p": p, "given": given}


def build_A(rolls):
    """rolls: 4 bars x 4 rolls -> bars of events."""
    return [[ev(k) for r in bar for k in A_FACE[r]] for bar in rolls]


def build_B(rr, pr):
    bars = []
    for b in range(len(rr)):
        evs = [ev(k) for r in rr[b] for k in B_RHY[r]]
        n = len(evs) - (1 if b in B_GIVEN else 0)
        assert len(pr[b]) == n, (b, len(pr[b]), n)
        for e, r in zip(evs, pr[b]):
            e["p"] = B_PITCH[r]
        if b in B_GIVEN:
            evs[-1]["p"], evs[-1]["given"] = B_GIVEN[b], True
        bars.append(evs)
    return bars


def build_C(cr, pr):
    bars = []
    for b in range(8):
        evs = [ev(k) for k in C_CELL[cr[b]]]
        idx = [i for i, e in enumerate(evs) if e["d"] != "r"]
        n = len(idx) - (1 if b in C_GIVEN else 0)
        assert len(pr[b]) == n, (b, len(pr[b]), n)
        for i, r in zip(idx, pr[b]):
            evs[i]["p"] = C_PITCH[r]
        if b in C_GIVEN:
            evs[idx[-1]]["p"], evs[idx[-1]]["given"] = C_GIVEN[b], True
        bars.append(evs)
    return bars


def make_examples():
    rng = random.Random(51)
    # Level A: 16 rolls, every face at least once, at least one rest and one bar of only quarters
    for _ in range(100000):
        rolls = [[rng.randint(1, 6) for _ in range(4)] for _ in range(4)]
        flat = [r for b in rolls for r in b]
        if set(flat) == set(range(1, 7)) and flat.count(5) <= 3 and not any(len(set(b)) == 1 for b in rolls):
            break
    ex_a = rolls
    # Level B: rhythm rolls, pitch rolls 1-5 only; all five notes appear; middle C appears twice or more
    for _ in range(100000):
        rr = [[rng.randint(1, 6) for _ in range(4)] for _ in range(4)]
        n_notes = [sum(len(B_RHY[r]) for r in bar) for bar in rr]
        if sum(1 for b in rr for r in b if r >= 4) < 4 or sum(1 for b in rr for r in b if r >= 4) > 7 or max(n_notes) > 7:
            continue
        pr = [[rng.randint(1, 5) for _ in range(n - (1 if i in B_GIVEN else 0))] for i, n in enumerate(n_notes)]
        flat = [p for b in pr for p in b]
        if set(flat) == set(range(1, 6)) and flat.count(1) >= 2 and not any(flat[i] == flat[i + 1] == flat[i + 2] for i in range(len(flat) - 2)):
            break
    ex_b = (rr, pr)
    # Level C: 8 rhythm rolls (>= 5 different cells, includes the rest cell), pitch rolls include middle C and high C
    for _ in range(200000):
        cr = [rng.randint(1, 6) for _ in range(8)]
        if len(set(cr)) < 5 or 6 not in cr[:7] or cr[3] == 5 or cr[7] == 4:
            continue
        pr = []
        for b in range(8):
            n = sum(1 for k in C_CELL[cr[b]] if k != "r") - (1 if b in C_GIVEN else 0)
            pr.append([rng.randint(1, 6) for _ in range(n)])
        flat = [p for b in pr for p in b]
        if 6 in flat and flat.count(1) >= 2 and flat.count(6) <= 4 and not any(flat[i] == flat[i + 1] == flat[i + 2] for i in range(len(flat) - 2)):
            break
    ex_c = (cr, pr)
    return ex_a, ex_b, ex_c


EX_A, EX_B, EX_C = make_examples()
TRY_A = [[1, 3, 5, 2]]      # the one-bar warm-up on the Level A dice table page
TRY_B = ([[4, 1, 2, 3]], [[3, 4, 5, 2, 1]])      # the one-bar warm-up on the Level B dice table page


# ------------------------------------------------------------------ notation drawing (Bravura, SMuFL)
HEAD_W = 1.18
REST_W = 1.08
G_HEAD, G_HALF, G_QREST, G_TREBLE, G_TS = 0xE0A4, 0xE0A3, 0xE4E5, 0xE050, 0xE080


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


def snowball(cx, cy, r, sw=1.4):
    o = [f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r:.2f}" fill="#fff" stroke="#000" stroke-width="{sw:.2f}"/>']
    a0, a1 = math.radians(-25), math.radians(70)
    rr = r * 0.72
    x0, y0 = cx + rr * math.cos(a0), cy + rr * math.sin(a0)
    x1, y1 = cx + rr * math.cos(a1), cy + rr * math.sin(a1)
    o.append(f'<path d="M{x0:.1f},{y0:.1f} A{rr:.1f},{rr:.1f} 0 0 1 {x1:.1f},{y1:.1f}" fill="none" stroke="{ACCENT}" stroke-width="{sw * 1.5:.2f}" stroke-linecap="round"/>')
    o.append(f'<path d="M{cx - 0.55 * r:.1f},{cy - 0.15 * r:.1f} q{0.15 * r:.1f},{-0.35 * r:.1f} {0.4 * r:.1f},{-0.4 * r:.1f}" fill="none" stroke="#000" stroke-width="{max(sw * 0.7, 0.7):.2f}" stroke-linecap="round"/>')
    return "".join(o)


def snow_pile(cx, base, r, sw=1.4):
    return snowball(cx - r * 1.05, base - r, r, sw) + snowball(cx + r * 1.05, base - r, r, sw) + snowball(cx, base - r * 2.55, r, sw)


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


PIPS = {1: [5], 2: [1, 9], 3: [1, 5, 9], 4: [1, 3, 7, 9], 5: [1, 3, 5, 7, 9], 6: [1, 3, 4, 6, 7, 9]}


DIE_BOX = 120   # die viewBox is 120 wide: 10 units of padding each side (the stroke is 4-5, a rotated corner reaches ~4 beyond the body)


def die_svg(n, size=22, unit="pt", fill="#fff", pip="#000", stroke="#000", sw=5, rot=0, inline=True):
    """A die face. Pips are circles with class 'pip' (the checker counts them)."""
    pts = {1: (24, 24), 2: (50, 24), 3: (76, 24), 4: (24, 50), 5: (50, 50), 6: (76, 50), 7: (24, 76), 8: (50, 76), 9: (76, 76)}
    pc = "".join(f'<circle class="pip" cx="{pts[k][0]}" cy="{pts[k][1]}" r="9" fill="{pip}"/>' for k in PIPS[n])
    st = "display:inline-block;vertical-align:middle" if inline else "display:block"
    box = f"{size * DIE_BOX / 100:g}{unit}"   # `size` is the die body; the render box is DIE_BOX% of it, so rotation and stroke never clip
    return (f'<svg class="die" data-n="{n}" data-sw="{sw}" viewBox="{-(DIE_BOX - 100) / 2:g} {-(DIE_BOX - 100) / 2:g} {DIE_BOX} {DIE_BOX}" width="{box}" height="{box}" style="{st}">'
            f'<g transform="rotate({rot} 50 50)"><rect x="5" y="5" width="90" height="90" rx="18" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>{pc}</g></svg>')


def ev_positions(bar, xl, W, beats, S):
    pad = 0.8 * S
    bw = (W - 2 * pad) / beats
    onset = 0.0
    xs = []
    i = 0
    while i < len(bar):
        d = bar[i]["d"]
        if d == "e":
            assert bar[i + 1]["d"] == "e"
            xs += [xl + pad + (onset + 0.25) * bw, xl + pad + (onset + 0.75) * bw]
            onset += 1
            i += 2
        else:
            xs.append(xl + pad + (onset + 0.5) * bw)
            onset += BEATS[d]
            i += 1
    assert abs(onset - beats) < 1e-9 or beats == 4 and onset <= 4, (onset, beats)
    return xs


def system_svg(sid, kind, bars, *, w=540.0, S=9.0, staff="five", meter=True, clef=True, first_bar=1, final=True, nbars=4, beats=4,
               labels=None, counts=False, phrase=None, chord=None, bar_nums=False, level="", attrs="", px=None, top=None,
               barlines=True, bottom_pad=None, rr=None, pr=None):
    """One system (a line of staff) with its notes. bars=None draws it blank. Everything the checker needs is in data-* and class names."""
    if top is None:
        top = (16 + 4.2 * S) if phrase else 4.2 * S
    bottom = top + 4 * S
    mid = top + 2 * S
    if labels or counts:
        h = bottom + 4.6 * S
    else:
        h = bottom + (bottom_pad if bottom_pad is not None else 3.0 * S)
    x_clef = 6.0
    if clef:
        bars_x0 = x_clef + (4.9 * S if meter else 3.2 * S)
    else:
        bars_x0 = x_clef + (3.4 * S if meter else 0.6 * S)
    x_end = w - 6
    W = (x_end - bars_x0) / nbars
    size = f'width="{w:.0f}pt" height="{h:.1f}pt"' if not px else f'width="{px}" height="{h * px / w:.1f}"'
    meter_attr = "4/4" if (meter and beats == 4) else ""
    o = [f'<svg class="ns" data-kind="{kind}" data-id="{sid}" data-staff="{staff}" data-clef="{1 if clef else 0}" data-meter="{meter_attr}" '
         f'data-nbars="{nbars}" data-beats="{beats}" data-barlines="{1 if barlines else 0}" data-first="{first_bar}" data-final="{1 if final else 0}" data-top="{fx(top)}" '
         f'data-x0="{fx(bars_x0)}" data-s="{fx(S)}" data-labels="{labels or ""}" data-level="{level}" data-phrase="{phrase or ""}" '
         f'data-rr="{rr or ""}" data-pr="{pr or ""}" {attrs} '
         f'xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.0f} {h:.1f}" {size} style="display:block">']
    lw = fx(0.14 * S)
    if staff == "five":
        for i in range(5):
            o.append(f'<line class="sl" x1="{fx(x_clef - 4)}" y1="{fx(top + i * S)}" x2="{fx(x_end)}" y2="{fx(top + i * S)}" stroke="#000" stroke-width="{lw}"/>')
    else:
        o.append(f'<line class="sl" x1="{fx(x_clef - 4)}" y1="{fx(mid)}" x2="{fx(x_end)}" y2="{fx(mid)}" stroke="#000" stroke-width="{lw}"/>')
    if clef:
        o.append(gl(G_TREBLE, x_clef, bottom - S, 4 * S, "clef"))
    if meter:
        xt = x_clef + (2.95 * S if clef else 0.4 * S)
        o.append(f'<g class="timesig">{gl(G_TS + 4, xt, top + 2 * S, 4 * S)}{gl(G_TS + 4, xt, top + 4 * S, 4 * S)}</g>')
    if phrase:
        label = {"CALL": "CALL · bars 1–4", "RESPONSE": "RESPONSE · bars 5–8"}[phrase]
        o.append(f'<line class="phr" x1="{fx(bars_x0)}" y1="17" x2="{fx(x_end)}" y2="17" stroke="{ACCENT}" stroke-width="1.6"/>'
                 f'<line class="phr" x1="{fx(bars_x0)}" y1="17" x2="{fx(bars_x0)}" y2="22" stroke="{ACCENT}" stroke-width="1.6"/>'
                 f'<line class="phr" x1="{fx(x_end)}" y1="17" x2="{fx(x_end)}" y2="22" stroke="{ACCENT}" stroke-width="1.6"/>')
        o.append(f'<text class="phl" x="{fx((bars_x0 + x_end) / 2)}" y="12" text-anchor="middle" font-family="Oswald" font-weight="700" font-size="11.5" '
                 f'letter-spacing=".1em" fill="{ACCENT}">{label}</text>')
    for bi in range(nbars):
        xl = bars_x0 + bi * W
        if bar_nums:
            o.append(f'<text class="bn" x="{fx(xl + 2.5)}" y="{fx(top - 1.9 * S)}" font-family="Source Sans 3, sans-serif" font-weight="600" font-size="{fx(0.85 * S)}" fill="#555">{first_bar + bi}</text>')
        if chord and bi in chord:
            o.append(f'<text class="chd" x="{fx(xl + 2.2 * S)}" y="{fx(top - 1.95 * S)}" font-family="Source Sans 3, sans-serif" font-weight="700" font-size="{fx(1.45 * S)}">{chord[bi]}</text>')
        if counts:
            pad = 0.8 * S
            bw = (W - 2 * pad) / beats
            for k in range(beats):
                o.append(f'<text class="cnt" x="{fx(xl + pad + (k + 0.5) * bw)}" y="{fx(bottom + 3.3 * S)}" text-anchor="middle" font-family="Source Sans 3, sans-serif" font-size="{fx(1.0 * S)}" fill="#666">{k + 1}</text>')
        if bars is not None:
            bar = bars[bi]
            xs = ev_positions(bar, xl, W, beats, S)
            i = 0
            while i < len(bar):
                e = bar[i]
                if e["d"] == "r":
                    o.append(f'<g class="ev" data-kind="r">{gl(G_QREST, xs[i] - REST_W * S / 2, mid, 4 * S, "rest")}</g>')
                    if labels == "rhythm":
                        o.append(f'<text class="lab" x="{fx(xs[i])}" y="{fx(bottom + 3.3 * S)}" text-anchor="middle" font-family="Source Sans 3, sans-serif" font-style="italic" font-weight="600" font-size="{fx(1.15 * S)}" fill="#555">shh</text>')
                    i += 1
                    continue
                group = [i, i + 1] if e["d"] == "e" else [i]
                steps = [STEP[bar[j]["p"]] if staff == "five" else 4 for j in group]
                ys = [bottom - s * S / 2 for s in steps]
                if len(group) == 2:
                    # beamed pair: the note farthest from the middle line decides; at equal distance the side decides
                    # (below the line = up, above = down); opposite sides at equal distance = down
                    da_, db_ = abs(steps[0] - 4), abs(steps[1] - 4)
                    if da_ != db_:
                        down = max(steps, key=lambda s_: abs(s_ - 4)) >= 4
                    elif steps[0] < 4 and steps[1] < 4:
                        down = False
                    else:
                        down = True
                else:
                    down = steps[0] >= 4
                hw = HEAD_W * S
                sw = 0.13 * S
                if len(group) == 2:
                    beam_end = (max(ys) + 0.168 * S + 3.5 * S) if down else (min(ys) - 0.168 * S - 3.5 * S)
                for gi, j in enumerate(group):
                    cx = xs[j]
                    left = cx - hw / 2
                    step, y = steps[gi], ys[gi]
                    o.append(f'<g class="ev" data-kind="{bar[j]["d"]}">')
                    for e_ in (range(-2, step - 1, -2) if step < 0 else []):
                        ly = bottom - e_ * S / 2
                        o.append(f'<line class="led" x1="{fx(left - 0.4 * S)}" y1="{fx(ly)}" x2="{fx(left + hw + 0.4 * S)}" y2="{fx(ly)}" stroke="#000" stroke-width="{fx(0.14 * S)}"/>')
                    o.append(gl(G_HALF if bar[j]["d"] == "h" else G_HEAD, left, y, 4 * S, "head"))
                    sx = (left + sw / 2) if down else (left + hw - sw / 2)
                    y1 = y + 0.168 * S if down else y - 0.168 * S
                    if len(group) == 2:
                        y2 = beam_end
                    else:
                        y2 = y1 + 3.5 * S if down else y1 - 3.5 * S
                    o.append(f'<line class="stem" x1="{fx(sx)}" y1="{fx(y1)}" x2="{fx(sx)}" y2="{fx(y2)}" stroke="#000" stroke-width="{fx(sw)}"/>')
                    o.append("</g>")
                    if labels:
                        if labels == "rhythm":
                            txt = WORD[bar[j]["d"]]
                        else:
                            txt = LETTER[bar[j]["p"]]
                        o.append(f'<text class="lab" x="{fx(cx)}" y="{fx(bottom + 3.3 * S)}" text-anchor="middle" font-family="Source Sans 3, sans-serif" font-weight="700" font-size="{fx(1.15 * S)}">{txt}</text>')
                if len(group) == 2:
                    if down:
                        bx1, bx2 = xs[group[0]] - hw / 2, xs[group[1]] - hw / 2 + sw
                        o.append(f'<rect class="beam" x="{fx(bx1)}" y="{fx(beam_end - 0.5 * S)}" width="{fx(bx2 - bx1)}" height="{fx(0.5 * S)}" fill="#000"/>')
                    else:
                        bx1, bx2 = xs[group[0]] + hw / 2 - sw, xs[group[1]] + hw / 2
                        o.append(f'<rect class="beam" x="{fx(bx1)}" y="{fx(beam_end)}" width="{fx(bx2 - bx1)}" height="{fx(0.5 * S)}" fill="#000"/>')
                i += len(group)
        if barlines:
            bx = xl + W
            if bi < nbars - 1 or not final:
                o.append(f'<line class="bar" x1="{fx(bx)}" y1="{fx(top)}" x2="{fx(bx)}" y2="{fx(bottom)}" stroke="#000" stroke-width="{fx(0.16 * S)}"/>')
            else:
                o.append(f'<line class="bar" x1="{fx(bx - 0.35 * S)}" y1="{fx(top)}" x2="{fx(bx - 0.35 * S)}" y2="{fx(bottom)}" stroke="#000" stroke-width="{fx(0.16 * S)}"/>')
                o.append(f'<rect class="fin" x="{fx(bx - 0.18 * S)}" y="{fx(top)}" width="{fx(0.36 * S)}" height="{fx(4 * S)}" fill="#000"/>')
    o.append("</svg>")
    return "".join(o)


def sym_beat(sid, roll, level, face_table, w=76.0, S=6.0):
    """A one-beat symbol for a dice table (one-line staff, no meter)."""
    bar = [ev(k) for k in face_table[roll]]
    return system_svg(sid, "sym", [bar], w=w, S=S, staff="one", meter=False, clef=False, nbars=1, beats=1, barlines=False, top=0.3 * S,
                      bottom_pad=2.0 * S, level=level, attrs=f'data-roll="{roll}"')


def sym_cell(sid, roll, w=120.0, S=5.2):
    bar = [ev(k) for k in C_CELL[roll]]
    return system_svg(sid, "sym", [bar], w=w, S=S, staff="one", meter=False, clef=False, nbars=1, beats=4, barlines=True, final=False, top=0.3 * S,
                      bottom_pad=2.0 * S, level="C", attrs=f'data-roll="{roll}"')


def sym_pitch(sid, roll, level, table, w=76.0, S=6.0):
    bar = [ev("q", table[roll])]
    return system_svg(sid, "sym", [bar], w=w, S=S, staff="five", meter=False, clef=True, nbars=1, beats=1, barlines=False, top=2.2 * S,
                      bottom_pad=1.8 * S, level=level, attrs=f'data-roll="{roll}"')


def pitch_bank_svg(sid, notes, w=500.0, S=9.5):
    """Quarter notes in a row with letter and solfege under each (student reference)."""
    top = 2.2 * S
    bottom = top + 4 * S
    h = bottom + 6.7 * S
    x_clef = 6.0
    x0 = x_clef + 3.4 * S
    gap = (w - 6 - x0) / len(notes)
    o = [f'<svg class="ns" data-kind="bank" data-id="{sid}" data-staff="five" data-clef="1" data-meter="" data-nbars="1" data-beats="6" data-barlines="0" data-first="1" data-final="0" '
         f'data-top="{fx(top)}" data-x0="{fx(x0)}" data-s="{fx(S)}" data-labels="bank" data-level="" data-phrase="" data-rr="" data-pr="" xmlns="http://www.w3.org/2000/svg" '
         f'viewBox="0 0 {w:.0f} {h:.1f}" width="{w:.0f}pt" height="{h:.1f}pt" style="display:block">']
    for i in range(5):
        o.append(f'<line class="sl" x1="2" y1="{fx(top + i * S)}" x2="{fx(w - 4)}" y2="{fx(top + i * S)}" stroke="#000" stroke-width="{fx(0.14 * S)}"/>')
    o.append(gl(G_TREBLE, x_clef, bottom - S, 4 * S, "clef"))
    hw, sw = HEAD_W * S, 0.13 * S
    for i, p in enumerate(notes):
        cx = x0 + gap * (i + 0.5)
        step = STEP[p]
        y = bottom - step * S / 2
        left = cx - hw / 2
        down = step >= 4
        o.append('<g class="ev" data-kind="q">')
        for e_ in (range(-2, step - 1, -2) if step < 0 else []):
            ly = bottom - e_ * S / 2
            o.append(f'<line class="led" x1="{fx(left - 0.4 * S)}" y1="{fx(ly)}" x2="{fx(left + hw + 0.4 * S)}" y2="{fx(ly)}" stroke="#000" stroke-width="{fx(0.14 * S)}"/>')
        o.append(gl(G_HEAD, left, y, 4 * S, "head"))
        sx = (left + sw / 2) if down else (left + hw - sw / 2)
        y1 = y + 0.168 * S if down else y - 0.168 * S
        y2 = y1 + 3.5 * S if down else y1 - 3.5 * S
        o.append(f'<line class="stem" x1="{fx(sx)}" y1="{fx(y1)}" x2="{fx(sx)}" y2="{fx(y2)}" stroke="#000" stroke-width="{fx(sw)}"/></g>')
        o.append(f'<text class="lab" x="{fx(cx)}" y="{fx(bottom + 3.6 * S)}" text-anchor="middle" font-family="Source Sans 3, sans-serif" font-weight="700" font-size="{fx(1.4 * S)}">{LETTER[p]}</text>')
        o.append(f'<text class="lab2" x="{fx(cx)}" y="{fx(bottom + 5.9 * S)}" text-anchor="middle" font-family="Oswald" font-weight="500" font-size="{fx(1.05 * S)}" fill="#444">{SOLFEGE[p]}</text>')
    o.append("</svg>")
    return "".join(o)


def sym_custom(sid, kinds, beats, w=80.0, S=6.0):
    bar = [ev(k) for k in kinds]
    return system_svg(sid, "sym", [bar], w=w, S=S, staff="one", meter=False, clef=False, nbars=1, beats=beats, barlines=False, top=0.3 * S,
                      bottom_pad=2.0 * S, level="R", attrs='data-roll="0"')


def fmt_rolls(rolls):
    return "|".join(" ".join(str(x) for x in b) for b in rolls)


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
.top { display: flex; justify-content: space-between; align-items: flex-end; gap: 26pt; border-bottom: 2.2pt solid #000; padding-bottom: 6pt; }
.top .t { font-size: 22pt; white-space: nowrap; flex: none; }
.top .tag { flex: none; white-space: nowrap; }
.top .t small { display: block; font-family: 'Oswald'; font-weight: 300; text-transform: none; font-size: 12pt; letter-spacing: 0; margin-top: 4pt; }
.top .deco { flex: 1; display: flex; justify-content: center; align-items: center; gap: 8pt; padding-bottom: 2pt; overflow: hidden; }
.tag { text-align: right; }
.tag .lv { display: inline-block; background: #000; color: #fff; font-family: 'Oswald'; font-weight: 700; font-size: 15pt; padding: 3pt 9pt 4pt; border-radius: 4pt; letter-spacing: .04em; }
.tag .lv.ak { background: ACCENT; }
.tag .ln { font-family: 'Oswald'; font-weight: 300; font-size: 11pt; margin-top: 3pt; }
.name { display: flex; gap: 18pt; font-size: 12pt; margin: 9pt 0 5pt; }
.name span { flex: 1; border-bottom: 1pt solid #000; height: 15pt; }
.name span.d { flex: 0 0 1.6in; }
.how { font-size: 11.5pt; margin: 2pt 0 7pt; line-height: 1.3; text-wrap: balance; }
.how b { font-weight: 700; }
.foot { display: flex; justify-content: space-between; font-size: 8.5pt; color: #333; border-top: .8pt solid #000; padding-top: 3pt; margin-top: auto; }
.wm { position: absolute; left: 50%; top: 50%; transform: translate(-50%, -50%) rotate(-38deg); font-family: 'Oswald'; font-weight: 700;
      font-size: 150pt; color: rgba(0,0,0,.13); letter-spacing: .06em; white-space: nowrap; pointer-events: none; z-index: 9; }
.doc h1 { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 30pt; margin: 0 0 4pt; line-height: 1; }
.doc h2, h2.s { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 14pt; margin: 12pt 0 4pt; letter-spacing: .02em; }
.doc p, .doc li { font-size: 11pt; line-height: 1.38; margin: 0 0 5pt; text-wrap: pretty; }
.doc ul { margin: 0 0 4pt; padding-left: 16pt; }
.doc .rule { border-bottom: 2.2pt solid #000; margin-bottom: 8pt; padding-bottom: 6pt; }
table { border-collapse: collapse; width: 100%; table-layout: fixed; font-size: 10pt; margin: 2pt 0 4pt; }
td, th { border: 1pt solid #000; padding: 3.5pt 6pt; text-align: left; vertical-align: top; }
th { font-family: 'Oswald'; font-weight: 500; text-transform: uppercase; font-size: 9.5pt; background: #000; color: #fff; text-align: center; vertical-align: middle; }
table.dt td { text-align: center; vertical-align: middle; padding: 2pt 3pt; }
table.dt td.lb { font-family: 'Oswald'; font-weight: 500; text-transform: uppercase; font-size: 9pt; background: #EEF5FA; }
table.dt td b { font-weight: 700; }
table.dt svg.ns { margin: 0 auto; }
table.dt.tall td { height: 50pt; }
table.dt.tallc td { height: 40pt; }
table.dt .sm { font-size: 9.5pt; color: #222; }
table.rec td { height: 22pt; text-align: center; vertical-align: middle; padding: 0; font-size: 11pt; font-weight: 700; }
table.rec.big td { height: 25pt; }
table.rec td.bn { background: #EEF5FA; font-family: 'Oswald'; font-weight: 500; font-size: 10pt; }
table.rec td.g { background: #E4E9ED; }
table.rec td.gv { background: TINT; color: ACCENT; font-family: 'Oswald'; font-size: 13pt; }
table.rolls td { height: 24pt; text-align: center; vertical-align: middle; padding: 0 1pt; font-size: 12pt; line-height: 1.05; }
table.rolls td span { display: block; font-size: 8.5pt; font-weight: 400; color: #333; }
table.rolls td b { font-family: 'Oswald'; font-weight: 700; font-size: 13pt; }
table.rolls td.bn { background: #EEF5FA; font-family: 'Oswald'; font-weight: 500; font-size: 10pt; }
table.rolls td.g { background: #E4E9ED; }
table.rolls td.gv { background: TINT; color: ACCENT; font-family: 'Oswald'; font-weight: 700; font-size: 13pt; }
table.rub td { font-size: 10.5pt; line-height: 1.28; padding: 5pt 6pt; height: 76pt; }
table.rub td.cr { background: #EEF5FA; }
table.rub td.cr b { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 10.5pt; display: block; margin-bottom: 3pt; }
table.rub td.cr span { display: block; margin-top: 6pt; font-weight: 600; }
.steps { display: flex; gap: 10pt; margin-top: 8pt; }
.step { flex: 1; border: 1.3pt solid #000; border-radius: 7pt; padding: 7pt 9pt 4pt; }
.step .n { display: inline-block; background: ACCENT; color: #fff; font-family: 'Oswald'; font-weight: 700; font-size: 12pt; border-radius: 50%; width: 20pt; height: 20pt; line-height: 20pt; text-align: center; margin-right: 5pt; }
.step b { font-family: 'Oswald'; font-weight: 500; text-transform: uppercase; font-size: 11.5pt; letter-spacing: .02em; }
.step p { margin: 4pt 0 3pt !important; font-size: 10pt !important; line-height: 1.3 !important; text-wrap: balance; }
.cols { display: flex; gap: 22pt; }
.cols > div { flex: 1; min-width: 0; }
.small { font-size: 9.5pt !important; color: #333; }
.box { border: 1.3pt solid #000; border-radius: 7pt; padding: 6pt 10pt 4pt; }
.box p { margin: 0 0 4pt; font-size: 10.5pt; line-height: 1.35; text-wrap: pretty; }
.cap { font-family: 'Oswald'; font-weight: 700; font-size: 12pt; text-transform: uppercase; margin: 8pt 0 3pt; letter-spacing: .02em; }
.cap span { font-weight: 300; text-transform: none; font-size: 10.5pt; letter-spacing: 0; }
.comp { margin-top: 12pt; }
.comp .ch { display: flex; align-items: baseline; gap: 10pt; font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 12.5pt; margin-bottom: 3pt; }
.comp .ch .tl { flex: 1; font-weight: 300; text-transform: none; font-size: 11pt; display: flex; gap: 6pt; }
.comp .ch .tl i { flex: 1; border-bottom: 1pt solid #000; height: 11pt; }
.chk { display: flex; gap: 16pt; font-size: 10.5pt; margin-top: 4pt; align-items: center; }
.chk span.bx { display: inline-block; width: 10pt; height: 10pt; border: 1.2pt solid #000; border-radius: 2pt; vertical-align: -1.5pt; margin-right: 4pt; }
.cover { align-items: center; justify-content: space-between; padding: 0.55in 0.6in 0.5in; }
.store { font-family: 'Oswald'; font-weight: 500; font-size: 13pt; letter-spacing: .32em; text-transform: uppercase; }
.ctitle { text-align: center; }
.ctitle .a { font-family: 'Oswald'; font-weight: 700; font-size: 44pt; line-height: 1; letter-spacing: .02em; }
.ctitle .b { font-family: 'Oswald'; font-weight: 700; white-space: nowrap; font-size: 78pt; line-height: .95; letter-spacing: .01em; }
.ctitle .c { font-family: 'Oswald'; font-weight: 300; font-size: 17pt; margin-top: 8pt; }
.cband { width: 100%; background: #000; color: #fff; text-align: center; font-family: 'Oswald'; font-weight: 500; font-size: 14pt;
         letter-spacing: .08em; text-transform: uppercase; padding: 8pt 0 9pt; border-radius: 4pt; }
.cband em { font-style: normal; color: ACCENT; }
.idea { border: 1.3pt solid #000; border-radius: 7pt; padding: 7pt 10pt 4pt; }
.idea b { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 11.5pt; letter-spacing: .02em; }
.idea .n { display: inline-block; background: ACCENT; color: #fff; font-family: 'Oswald'; font-weight: 700; font-size: 11pt; border-radius: 50%; width: 18pt; height: 18pt; line-height: 18pt; text-align: center; margin-right: 6pt; }
.idea p { margin: 3pt 0 3pt; font-size: 10.5pt; line-height: 1.32; text-wrap: pretty; }
.ideas { display: grid; grid-template-columns: 1fr 1fr; gap: 10pt; margin-top: 6pt; }
.line { border-bottom: 1pt solid #000; height: 17pt; }
""".replace("ACCENT", ACCENT).replace("TINT", TINT)


def html_doc(pages, title="doc"):
    return (f'<!doctype html><html><head><meta charset="utf-8"><title>{escape(title)}</title>'
            f'<style>{font_css()}{CSS}</style></head><body>{"".join(pages)}</body></html>')


def foot(left, right):
    return f'<div class="foot"><span>{left}</span><span>{right}</span></div>'


COPY = f"© {YEAR} {STORE} · {BRAND} · For single-classroom use"
WM = '<div class="wm">PREVIEW</div>'


def deco_header():
    s = lambda body: f'<svg data-icon="flake" data-icon-sw="1.6" width="25.7pt" height="25.7pt" viewBox="-2 -2 28 28">{body}</svg>'
    return (die_svg(3, 21) + s(snowflake(12, 12, 10, ACCENT, 1.6)) + die_svg(5, 21) + s(snowflake(12, 12, 10, ACCENT, 1.6)) + die_svg(2, 21))


def top_block(sub, tag, tagline, ak=False, deco=True):
    return (f'<div class="top"><div class="h t">{TITLE}<small>{sub}</small></div>'
            f'<div class="deco">{deco_header() if deco else ""}</div>'
            f'<div class="tag"><div class="lv{" ak" if ak else ""}">{tag}</div><div class="ln">{tagline}</div></div></div>')


NAME = '<div class="name">Name<span></span>Date<span class="d"></span></div>'

STEP_TEXT = {
    "A": ["Roll the die once for each beat. Write the number in the next roll box.",
          "Find your number in the dice table. It tells you the rhythm for that beat.",
          "Draw that rhythm on the line, in the same beat. Four rolls fill one bar.",
          "Clap and say your rhythm. Then share it with a partner."],
    "B": ["Roll the rhythm die for each of the 4 beats in a bar. Then roll the pitch die once for each note.",
          "Find each number in the two dice tables.",
          "Draw the notes on the staff. The last note of bar 4 is given: it is C.",
          "Play or sing your melody. Then share it with a partner."],
    "C": ["Roll the rhythm die once for each bar. Roll the pitch die once for each note.",
          "Find each number in the dice tables. The last note you play is given in bars 4 and 8.",
          "Draw the notes on the staff. Bars 1–4 are the call and bars 5–8 are the response.",
          "Play or sing all 8 bars. Then share your piece with a partner."],
}


def steps_html(level):
    return '<div class="steps">' + "".join(
        f'<div class="step"><span class="n">{i + 1}</span><b>{STEPS_NAMES[i]}</b><p>{STEP_TEXT[level][i]}</p></div>' for i in range(4)) + "</div>"


def nobreak(html):
    """Keep ranges such as 5–8 on one line (outside the SVG drawings)."""
    parts = re.split(r"(<svg.*?</svg>)", html, flags=re.S)
    return "".join(p if p.startswith("<svg") else re.sub(r"(?<=\d)–(?=\d)", "\u2060–\u2060", p) for p in parts)


def page_wrap(body, wm=False, cls="page"):
    body = nobreak(body)
    return f'<section class="{cls}">{WM if wm else ""}{body}</section>'


# ---- Level A
def a_table_page(wm=False):
    names = {"q": ("Quarter note", "ta", "1 beat"), "ee": ("Two eighth notes", "ti-ti", "1 beat"), "r": ("Quarter rest", "shh", "1 beat of silence")}
    rows = ""
    for r in range(1, 7):
        nm, say, ln = names[A_FACE[r]]
        rows += (f'<tr><td>{die_svg(r, 30)}</td><td>{sym_beat(f"SYM-A{r}", r, "A", A_KINDS, 80, 6.5)}</td>'
                 f'<td>{nm}</td><td><b>{say}</b></td><td>{ln}</td></tr>')
    tbl = (f'<table class="dt tall"><tr><th>Roll</th><th>Symbol</th><th>Name</th><th>Say</th><th>Length</th></tr>{rows}</table>')
    try_svg = system_svg("TRY-A", "ex", build_A(TRY_A), w=300, S=8, staff="one", meter=True, clef=False, nbars=1, final=False, labels="rhythm", level="A", rr=fmt_rolls(TRY_A))
    try_dice = "".join(die_svg(r, 24) for r in TRY_A[0])
    body = (top_block(P_KEYS(P_A_TBL), "LEVEL A", "Grades 2–3") + NAME +
            '<div class="how"><b>Roll a die for each beat.</b> One roll fills one beat, so four rolls always make one full bar of 4/4. '
            'Look up each roll in the table and draw that rhythm.</div>' + tbl + steps_html("A") +
            f'<div class="box" style="margin-top:9pt;display:flex;gap:14pt;align-items:center"><div style="flex:none;width:190pt"><div class="cap" style="margin-top:0">Try one bar</div>'
            f'<p style="margin:0 0 5pt">Roll these four numbers:</p><div style="display:flex;gap:5pt">{try_dice}</div></div><div style="flex:1;display:flex;justify-content:center">{try_svg}</div></div>'
            f'<p class="small" style="margin:6pt 0 0">Every symbol lasts exactly 1 beat, so you can never run out of room: 1 + 1 + 1 + 1 = 4.</p>'
            + foot(COPY, f"Roll and record on page {P_A_REC} · Page {P_A_TBL}"))
    return page_wrap(body, wm)


def P_KEYS(p):
    return PAGE_KEYS[p]


def rec_table(cols, rows, header, groups=None):
    colg = "<colgroup>" + "".join("<col>" for _ in range(cols)) + "</colgroup>"
    return f'<table class="rec">{colg}{header}{rows}</table>'


def checks_row():
    return '<div class="chk"><span><span class="bx"></span>I clapped it</span><span><span class="bx"></span>I said it</span><span><span class="bx"></span>I shared it</span></div>'


def a_record_page(wm=False):
    comps = ""
    for n in (1, 2):
        rows = "".join(f'<tr><td class="bn">Bar {b}</td>' + "<td></td>" * 4 + "</tr>" for b in range(1, 5))
        head = '<tr><th>Bar</th><th>Beat 1</th><th>Beat 2</th><th>Beat 3</th><th>Beat 4</th></tr>'
        staff = system_svg(f"REC-A{n}", "rec", None, w=540, S=9.5, staff="one", meter=True, clef=False, counts=True, level="A", top=2.6 * 9.5)
        comps += (f'<div class="comp"><div class="ch">Composition {n}<span class="tl">Title <i></i></span></div>'
                  f'{rec_table(5, rows, head)}<div style="margin-top:6pt">{staff}</div>{checks_row()}</div>')
    body = (top_block(P_KEYS(P_A_REC), "LEVEL A", "Grades 2–3") + NAME +
            f'<div class="how"><b>Roll, look up, draw, play.</b> Write each roll in a box. Then draw the rhythm on the line. Use the dice table on page {P_A_TBL}.</div>'
            + comps + foot(COPY, f"Example on page {P_EX1} · Page {P_A_REC}"))
    return page_wrap(body, wm)


# ---- Level B
def b_table_page(wm=False):
    try_b = system_svg("TRY-B", "ex", build_B(*TRY_B), w=300, S=8, staff="five", meter=True, clef=True, nbars=1, final=False, labels="letter", level="B",
                       rr=fmt_rolls(TRY_B[0]), pr=fmt_rolls(TRY_B[1]))
    nm = {"q": ("ta", "Quarter note"), "ee": ("ti-ti", "Two eighth notes")}
    hdr = '<tr><td class="lb">Roll</td>' + "".join(f"<td>{die_svg(r, 26)}</td>" for r in range(1, 7)) + "</tr>"
    rh_cells = '<tr><td class="lb">Rhythm</td>' + "".join(f'<td>{sym_beat(f"SYM-BR{r}", r, "B", B_KINDS, 62, 5.0)}</td>' for r in range(1, 7)) + "</tr>"
    rh_say = '<tr><td class="lb">Say</td>' + "".join(f'<td><b>{nm[B_RHY[r]][0]}</b></td>' for r in range(1, 7)) + "</tr>"
    rh_name = '<tr><td class="lb">Name</td>' + "".join(f'<td class="sm">{nm[B_RHY[r]][1]}</td>' for r in range(1, 7)) + "</tr>"
    colg = "<colgroup>" + "<col>" * 7 + "</colgroup>"
    t1 = f'<table class="dt">{colg}{hdr}{rh_cells}{rh_say}{rh_name}</table>'
    pc = '<tr><td class="lb">Note</td>' + "".join(f'<td>{sym_pitch(f"SYM-BP{r}", r, "B", B_PITCH, 64, 5.4)}</td>' for r in range(1, 6)) + '<td class="sm">Your choice</td></tr>'
    pl = '<tr><td class="lb">Letter</td>' + "".join(f'<td><b>{LETTER[B_PITCH[r]]}</b></td>' for r in range(1, 6)) + '<td class="sm">C, D, E, G or A</td></tr>'
    ps = '<tr><td class="lb">Solfege</td>' + "".join(f'<td>{SOLFEGE[B_PITCH[r]]}</td>' for r in range(1, 6)) + '<td class="sm">any of the five</td></tr>'
    t2 = f'<table class="dt">{colg}{hdr}{pc}{pl}{ps}</table>'
    body = (top_block(P_KEYS(P_B_TBL), "LEVEL B", "Grades 3–4") + NAME +
            '<div class="how"><b>Roll for rhythm and for pitch.</b> The rhythm die fills one beat per roll, so every bar still adds up to 4 beats. '
            'The pitch die gives the notes of the C pentatonic scale.</div>'
            '<div class="cap">Rhythm die <span>· roll once for each beat</span></div>' + t1 +
            '<div class="cap">Pitch die <span>· roll once for each note (a pair of eighth notes needs two rolls)</span></div>' + t2 +
            steps_html("B") +
            f'<div class="box" style="margin-top:9pt;display:flex;gap:14pt;align-items:center"><div style="flex:none;width:190pt"><div class="cap" style="margin-top:0">Try one bar</div>'
            f'<p style="margin:0 0 3pt">Rhythm rolls:</p><div style="display:flex;gap:5pt">{"".join(die_svg(r, 20) for r in TRY_B[0][0])}</div>'
            f'<p style="margin:5pt 0 3pt">Pitch rolls:</p><div style="display:flex;gap:5pt">{"".join(die_svg(r, 20) for r in TRY_B[1][0])}</div></div>'
            f'<div style="flex:1;display:flex;justify-content:center">{try_b}</div></div>'
            f'<p class="small" style="margin:7pt 0 0">The last note of bar 4 is always C, so it is printed on your sheet and has no roll. '
            f'All notes stay between middle C and A. Middle C sits on its own short line below the staff.</p>'
            + foot(COPY, f"Roll and record on page {P_B_REC} · Page {P_B_TBL}"))
    return page_wrap(body, wm)


def b_record_page(wm=False):
    comps = ""
    for n in (1, 2):
        head = ('<tr><th>Bar</th><th colspan="4">Rhythm rolls</th><th colspan="8">Pitch rolls</th></tr>'
                '<tr><th></th>' + "".join(f"<th>R{i}</th>" for i in range(1, 5)) + "".join(f"<th>P{i}</th>" for i in range(1, 9)) + "</tr>")
        rows = ""
        for b in range(1, 5):
            rows += f'<tr><td class="bn">{b}</td>' + "<td></td>" * 12 + "</tr>"
        rows = rows.replace('<td class="bn">4</td>' + "<td></td>" * 12, '<td class="bn">4</td>' + "<td></td>" * 12)
        staff = system_svg(f"REC-B{n}", "rec", None, w=540, S=9.5, staff="five", meter=True, clef=True, level="B", top=2.6 * 9.5)
        comps += (f'<div class="comp" style="margin-top:9pt"><div class="ch">Composition {n}<span class="tl">Title <i></i></span></div>'
                  f'{rec_table(13, rows, head)}<div style="margin-top:4pt">{staff}</div>{checks_row()}</div>')
    body = (top_block(P_KEYS(P_B_REC), "LEVEL B", "Grades 3–4") + NAME +
            f'<div class="how"><b>Roll, look up, draw, play.</b> Roll the rhythm die four times for a bar, then roll the pitch die for each note. Use the dice tables on page {P_B_TBL}.</div>'
            + comps + foot(COPY, f"Example on page {P_EX1} · Page {P_B_REC}"))
    return page_wrap(body, wm)


# ---- Level C
def c_table_page(wm=False):
    rows = ""
    for r in range(1, 7):
        kinds = C_CELL[r]
        nn = sum(1 for k in kinds if k != "r")
        words = []
        i = 0
        while i < len(kinds):
            if kinds[i] == "e":
                words.append("ti-ti"); i += 2
            else:
                words.append(WORD[kinds[i]]); i += 1
        rows += (f'<tr><td>{die_svg(r, 26)}</td><td>{sym_cell(f"SYM-C{r}", r, 122, 5.0)}</td><td>{" ".join(words)}</td><td>{nn} notes</td></tr>')
    t1 = ('<table class="dt tallc"><tr><th>Roll</th><th>One bar of rhythm</th><th>Say</th><th>Notes in the bar</th></tr>' + rows + "</table>")
    colg = "<colgroup>" + "<col>" * 7 + "</colgroup>"
    hdr = '<tr><td class="lb">Roll</td>' + "".join(f"<td>{die_svg(r, 24)}</td>" for r in range(1, 7)) + "</tr>"
    pc = '<tr><td class="lb">Note</td>' + "".join(f'<td>{sym_pitch(f"SYM-CP{r}", r, "C", C_PITCH, 64, 5.4)}</td>' for r in range(1, 7)) + "</tr>"
    pl = '<tr><td class="lb">Letter</td>' + "".join(f'<td><b>{LETTER[C_PITCH[r]]}</b></td>' for r in range(1, 7)) + "</tr>"
    ps = '<tr><td class="lb">Name</td>' + "".join(f'<td class="sm">{n_}</td>' for n_ in ("middle C", "D", "E", "G", "A", "high C")) + "</tr>"
    t2 = f'<table class="dt">{colg}{hdr}{pc}{pl}{ps}</table>'
    body = (top_block(P_KEYS(P_C_TBL), "LEVEL C", "Grades 4–5") + NAME +
            '<div class="how"><b>Roll two dice.</b> The rhythm die gives a whole bar. The pitch die gives each note. The chord is C (C, E and G), and your piece ends on C.</div>'
            '<div class="cap">Rhythm die <span>· roll once for each bar</span></div>' + t1 +
            '<div class="cap">Pitch die <span>· roll once for each note</span></div>' + t2 + steps_html("C") +
            foot(COPY, f"Roll and record on page {P_C_REC} · Page {P_C_TBL}"))
    return page_wrap(body, wm)


def c_record_page(wm=False):
    colg = "<colgroup>" + "<col>" * 8 + "</colgroup>"
    head = '<tr><th>Bar</th><th>Rhythm</th>' + "".join(f"<th>P{i}</th>" for i in range(1, 6)) + "<th>Last note</th></tr>"
    rows = ""
    for b in range(1, 9):
        last = '<td class="gv">G</td>' if b == 4 else ('<td class="gv">C</td>' if b == 8 else '<td class="g"></td>')
        rows += f'<tr><td class="bn">{b}</td>' + "<td></td>" * 6 + last + "</tr>"
    tbl = f'<table class="rec big">{colg}{head}{rows}</table>'
    s1 = system_svg("REC-C1", "rec", None, w=540, S=10.0, staff="five", meter=True, clef=True, first_bar=1, final=False, phrase="CALL",
                    chord={0: "C"}, bar_nums=True, level="C")
    s2 = system_svg("REC-C2", "rec", None, w=540, S=10.0, staff="five", meter=False, clef=True, first_bar=5, final=True, phrase="RESPONSE",
                    chord={0: "C"}, bar_nums=True, level="C")
    body = (top_block(P_KEYS(P_C_REC), "LEVEL C", "Grades 4–5") + NAME +
            f'<div class="how"><b>Roll, look up, draw, play.</b> Use the dice tables on page {P_C_TBL}. '
            'Write the rhythm roll for each bar and one pitch roll for each note. The last note you play in bar 4 is G and in bar 8 it is C.</div>'
            f'{tbl}<div style="margin-top:8pt">{s1}</div><div style="margin-top:6pt">{s2}</div>{checks_row()}'
            f'<div class="comp" style="margin-top:8pt"><div class="ch" style="font-size:11pt">Title of my piece<span class="tl"><i></i></span></div></div>'
            + foot(COPY, f"Example on page {P_EX2} · Page {P_C_REC}"))
    return page_wrap(body, wm)


# ---- staff paper
def staff4_page(wm=False):
    sy = "".join(f'<div style="margin-top:{4 if i == 0 else 7}pt">' + system_svg(f"ST4-{i + 1}", "blank", None, w=540, S=9.0, staff="five", meter=True, clef=True, level="P", top=2.3 * 9.0, bottom_pad=2.2 * 9.0) + "</div>"
                 for i in range(7))
    body = (top_block(P_KEYS(P_ST4), "STAFF PAPER", "Treble clef · 4/4") + NAME +
            '<div class="how" style="margin-bottom:0">Use these staves for any Level A, B or C idea that fits in 4 bars. Write the title above the staff.</div>' + sy
            + foot(COPY, f"Page {P_ST4}"))
    return page_wrap(body, wm)


def staff8_page(wm=False):
    comps = ""
    S = 8.5
    for n in range(3):
        a = system_svg(f"ST8-{n + 1}A", "blank", None, w=540, S=S, staff="five", meter=True, clef=True, first_bar=1, final=False, phrase="CALL", level="P",
                       top=16 + 2.2 * S, bottom_pad=2.2 * S)
        b = system_svg(f"ST8-{n + 1}B", "blank", None, w=540, S=S, staff="five", meter=False, clef=True, first_bar=5, final=True, phrase="RESPONSE", level="P",
                       top=16 + 2.2 * S, bottom_pad=2.2 * S)
        comps += f'<div style="margin-top:{4 if n == 0 else 9}pt">{a}<div style="margin-top:6pt">{b}</div></div>'
    body = (top_block(P_KEYS(P_ST8), "STAFF PAPER", "Treble clef · 4/4") + NAME +
            '<div class="how" style="margin-bottom:0">Three 8-bar pieces to a page: a 4-bar call and a 4-bar response. Number your bars and write the chord symbol C above the staff.</div>'
            + comps + foot(COPY, f"Page {P_ST8}"))
    return page_wrap(body, wm)


# ---- examples
def ex_a_block():
    bars = build_A(EX_A)
    rows = ""
    for b in range(4):
        cells = "".join(
            f'<td data-ex="EXA" data-bar="{b + 1}" data-kind="rr" data-roll="{r}"><b>{r}</b><span>{ {"q": "ta", "ee": "ti-ti", "r": "shh"}[A_FACE[r]] }</span></td>'
            for r in EX_A[b])
        rows += f'<tr><td class="bn">Bar {b + 1}</td>{cells}</tr>'
    head = '<tr><th>Bar</th><th>Beat 1</th><th>Beat 2</th><th>Beat 3</th><th>Beat 4</th></tr>'
    staff = system_svg("EXA", "ex", bars, w=540, S=9.5, staff="one", meter=True, clef=False, labels="rhythm", level="A", rr=fmt_rolls(EX_A))
    return (f'<div class="cap" style="margin-top:6pt">Example A <span>· Level A · 16 rolls, 4 bars</span></div>'
            f'<table class="rolls">{head}{rows}</table><div style="margin-top:4pt">{staff}</div>')


def ex_b_block():
    rr, pr = EX_B
    bars = build_B(rr, pr)
    rows = ""
    for b in range(4):
        c = "".join(f'<td data-ex="EXB" data-bar="{b + 1}" data-kind="rr" data-roll="{r}"><b>{r}</b></td>' for r in rr[b])
        for i in range(8):
            if i < len(pr[b]):
                c += f'<td data-ex="EXB" data-bar="{b + 1}" data-kind="pr" data-roll="{pr[b][i]}"><b>{pr[b][i]}</b></td>'
            elif b in B_GIVEN and i == len(pr[b]):
                c += f'<td class="gv" data-ex="EXB" data-bar="{b + 1}" data-kind="given" data-roll="C">C</td>'
            else:
                c += '<td class="g"></td>'
        rows += f'<tr><td class="bn">{b + 1}</td>{c}</tr>'
    head = ('<tr><th>Bar</th><th colspan="4">Rhythm rolls</th><th colspan="8">Pitch rolls</th></tr>'
            '<tr><th></th>' + "".join(f"<th>R{i}</th>" for i in range(1, 5)) + "".join(f"<th>P{i}</th>" for i in range(1, 9)) + "</tr>")
    colg = "<colgroup>" + "<col>" * 13 + "</colgroup>"
    staff = system_svg("EXB", "ex", bars, w=540, S=9.5, staff="five", meter=True, clef=True, labels="letter", level="B", rr=fmt_rolls(rr), pr=fmt_rolls(pr))
    return (f'<div class="cap" style="margin-top:10pt">Example B <span>· Level B · rhythm rolls and pitch rolls, 4 bars</span></div>'
            f'<table class="rolls">{colg}{head}{rows}</table><div style="margin-top:4pt">{staff}</div>')


def ex1_page(wm=False):
    body = (top_block(P_KEYS(P_EX1), "EXAMPLES", "With the rolls shown", ak=True, deco=False) +
            '<div class="how" style="margin-top:8pt"><b>How to read an example.</b> Each roll is shown in its box. Look it up in the dice table and you get the notation below. '
            'Your own rolls will make a different piece.</div>' + ex_a_block() + ex_b_block() +
            '<p class="small" style="margin:7pt 0 0">Check: every bar adds up to 4 beats. In Example B the last note of bar 4 is C and has no roll. Eighth notes always come in beamed pairs.</p>'
            + foot(COPY, f"Dice tables on pages {P_A_TBL} and {P_B_TBL} · Page {P_EX1}"))
    return page_wrap(body, wm)


def ex2_page(wm=False):
    cr, pr = EX_C
    bars = build_C(cr, pr)
    colg = "<colgroup>" + "<col>" * 8 + "</colgroup>"
    head = '<tr><th>Bar</th><th>Rhythm</th>' + "".join(f"<th>P{i}</th>" for i in range(1, 6)) + "<th>Last note</th></tr>"
    rows = ""
    for b in range(8):
        c = f'<td data-ex="EXC" data-bar="{b + 1}" data-kind="rr" data-roll="{cr[b]}"><b>{cr[b]}</b></td>'
        for i in range(5):
            if i < len(pr[b]):
                c += f'<td data-ex="EXC" data-bar="{b + 1}" data-kind="pr" data-roll="{pr[b][i]}"><b>{pr[b][i]}</b></td>'
            else:
                c += '<td class="g"></td>'
        if b in C_GIVEN:
            c += f'<td class="gv" data-ex="EXC" data-bar="{b + 1}" data-kind="given" data-roll="{LETTER[C_GIVEN[b]]}">{LETTER[C_GIVEN[b]]}</td>'
        else:
            c += '<td class="g"></td>'
        rows += f'<tr><td class="bn">{b + 1}</td>{c}</tr>'
    s1 = system_svg("EXC1", "ex", bars[:4], w=540, S=9.0, staff="five", meter=True, clef=True, first_bar=1, final=False, labels="letter", phrase="CALL",
                    chord={0: "C"}, bar_nums=True, level="C", rr=fmt_rolls([[x] for x in cr[:4]]), pr=fmt_rolls(pr[:4]))
    s2 = system_svg("EXC2", "ex", bars[4:], w=540, S=9.0, staff="five", meter=False, clef=True, first_bar=5, final=True, labels="letter", phrase="RESPONSE",
                    chord={0: "C"}, bar_nums=True, level="C", rr=fmt_rolls([[x] for x in cr[4:]]), pr=fmt_rolls(pr[4:]))
    body = (top_block(P_KEYS(P_EX2), "EXAMPLE", "With the rolls shown", ak=True, deco=False) +
            '<div class="how" style="margin-top:8pt"><b>Level C, 8 bars.</b> The rhythm roll in each bar picks one of the six bars in the dice table. '
            'Each pitch roll picks one note. The last note you play in bar 4 (G) and in bar 8 (C) is given.</div>'
            f'<div class="cap" style="margin-top:4pt">Example C <span>· 8 rhythm rolls and the pitch rolls</span></div>'
            f'<table class="rolls">{colg}{head}{rows}</table>'
            f'<div style="margin-top:8pt">{s1}</div><div style="margin-top:6pt">{s2}</div>'
            '<div class="box" style="margin-top:9pt"><p><b>What to notice.</b> Bars 1–4 are the call. It ends on G, which sounds unfinished, like a question. '
            'Bars 5–8 are the response. It ends on C, which sounds like home. Every bar adds up to 4 beats, and a quarter rest still counts as a beat.</p></div>'
            + foot(COPY, f"Dice tables on page {P_C_TBL} · Page {P_EX2}"))
    return page_wrap(body, wm)


# ---- rubric
RUBRIC = [
    ("Rolls match the table", "Every roll matches the symbol or note in the dice table.", "One or two rolls do not match the table.",
     "Several rolls do not match the table.", "Most rolls do not match the table."),
    ("Bars add up", "Every bar adds up to 4 beats.", "One bar has too many or too few beats.",
     "Two or three bars do not add up.", "Most bars do not add up."),
    ("Notation", "Heads, stems, beams and rests are all drawn correctly.", "A few small mistakes in the drawing.",
     "Many mistakes make it hard to read.", "The notation cannot be read."),
    ("Performance", "Steady beat from start to finish, with every rhythm and note clear.", "Mostly steady, with one or two stops.",
     "Often unsteady, with several stops.", "Needs help to get through it."),
    ("Sharing", "Explains the rolls and gives kind, helpful feedback.", "Explains the rolls or gives feedback, but not both.",
     "Shares with a lot of help.", "Does not share yet."),
]
RUBRIC_MAX = 4


def rubric_page(wm=False):
    rows = "".join(
        f'<tr><td class="cr"><b>{c[0]}</b><span>Score ____ / {RUBRIC_MAX}</span></td><td>{c[1]}</td><td>{c[2]}</td><td>{c[3]}</td><td>{c[4]}</td></tr>' for c in RUBRIC)
    total = len(RUBRIC) * RUBRIC_MAX
    colg = "<colgroup>" + "<col>" * 5 + "</colgroup>"
    tbl = (f'<table class="rub">{colg}<tr><th>Criterion</th><th>4 · Excellent</th><th>3 · Good</th><th>2 · Almost</th><th>1 · Not yet</th></tr>{rows}</table>')
    body = (top_block(P_KEYS(P_RUB), "RUBRIC", "Levels A, B and C") + NAME +
            '<div class="how"><b>Score each row from 1 to 4.</b> Students can score themselves first and then a partner or the teacher can score. '
            'Add the five scores for the total.</div>' + tbl +
            f'<div class="box" style="margin-top:8pt;display:flex;justify-content:space-between;align-items:center;gap:12pt">'
            f'<div class="h" style="font-size:16pt">Total <span class="l" style="text-transform:none;font-size:15pt"> ______ / {total}</span></div>'
            f'<div style="font-size:10.5pt;line-height:1.4"><b>{total - 2}–{total}</b> Excellent · <b>{total - 7}–{total - 3}</b> Good · <b>{total - 12}–{total - 8}</b> Almost there · <b>{len(RUBRIC)}–{total - 13}</b> Not yet</div></div>'
            '<div class="cap">Two stars and a wish <span>· for the partner who listened</span></div>'
            '<div style="display:grid;grid-template-columns:auto 1fr;gap:4pt 8pt;align-items:end;font-size:11pt">'
            '<b>Star 1</b><div class="line"></div><b>Star 2</b><div class="line"></div><b>Wish</b><div class="line"></div></div>'
            + foot(COPY, f"Page {P_RUB}"))
    return page_wrap(body, wm)


# ---- share ideas
IDEAS = [
    ("Clap and say", "Clap the rhythm while saying ta, ti-ti and shh. Count 1 2 3 4 out loud before you start."),
    ("Body percussion", "Pat, clap, snap or stomp the rhythm. Use a different sound for each symbol in Level A."),
    ("Classroom percussion", "Play the rhythm on drums, wood blocks or shakers. Rests stay silent."),
    ("Bells and keyboards", "Set up C, D, E, G and A. On xylophones and bells, lift off the F and B bars."),
    ("Call and response", "One player performs the call (bars 1–4). A partner answers with the response (bars 5–8)."),
    ("Swap and play", "Trade sheets with a partner and perform each other's compositions."),
    ("Gallery walk", "Post the compositions. Classmates read them and leave a star and a wish on a sticky note."),
    ("Class piece", "Join four 4-bar compositions end to end. Play them in order as a class piece."),
    ("Add an ostinato", "A partner plays a short pattern that repeats over and over while you perform your piece."),
    ("Record and listen", "Record each performance on a tablet or phone. Listen back and talk about what worked well."),
]


def share_page(wm=False):
    cards = "".join(f'<div class="idea"><b><span class="n">{i + 1}</span>{t}</b><p>{d}</p></div>' for i, (t, d) in enumerate(IDEAS))
    body = (top_block(P_KEYS(P_SHARE), "SHARE", "Performance ideas") + NAME +
            '<div class="how"><b>Every composition deserves a performance.</b> Pick one idea for each lesson, or let students choose their own way to share.</div>'
            f'<div class="ideas">{cards}</div>'
            '<div class="cap" style="margin-top:12pt">A sharing routine in three steps</div>'
            '<div class="steps" style="margin-top:2pt">'
            '<div class="step"><span class="n">1</span><b>Introduce</b><p>Say your title. Tell the class which dice rolls you used.</p></div>'
            '<div class="step"><span class="n">2</span><b>Perform</b><p>Count in 1 2 3 4. Play or say your piece with a steady beat.</p></div>'
            '<div class="step"><span class="n">3</span><b>Respond</b><p>Listeners name one star and one wish. Then fill in the rubric on page ' + str(P_RUB) + '.</p></div></div>'
            '<div class="box" style="margin-top:10pt"><p><b>Tip for teachers.</b> Let students choose whether to play or say their piece. Keep each performance short, and ask listeners to tap the beat quietly. '
            'Celebrate every composition: the dice make each one different.</p></div>'
            + foot(COPY, f"Rubric on page {P_RUB} · Page {P_SHARE}"))
    return page_wrap(body, wm)


# ---- teacher notes, reference, terms, cover
def cover_art(width=900, height=500):
    o = [f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" style="display:block;width:100%;height:auto">']
    mound = ('M70,456 C70,422 250,406 450,406 C650,406 830,422 830,456 C830,480 650,492 450,492 C250,492 70,480 70,456 Z')
    o.append(f'<path d="{mound}" fill="{TINT}" stroke="#000" stroke-width="3" stroke-linejoin="round"/>')
    for fx_, fy_, fr, col in ((62, 62, 26, ACCENT), (842, 70, 28, ACCENT), (92, 150, 13, "#000"), (818, 170, 14, "#000"), (866, 268, 10, ACCENT), (56, 262, 10, "#000")):
        o.append(snowflake(fx_, fy_, fr, col, 2.4))
    o.append(snowman(140, 466, 50, "#fff", ACCENT, 3))
    o.append(snow_pile(760, 468, 30, 3))
    rr, pr = EX_B
    bars = build_B(rr[:2], pr[:2])
    o.append('<rect x="150" y="20" width="600" height="200" rx="20" fill="#fff" stroke="#000" stroke-width="3"/>')
    st = system_svg("COVER-B", "cover", bars, w=540, S=13, staff="five", meter=True, clef=True, nbars=2, final=False, level="B",
                    rr=fmt_rolls(rr[:2]), pr=fmt_rolls(pr[:2]), px=570, top=3.4 * 13, bottom_pad=3.4 * 13)
    o.append(f'<g transform="translate(165,34)">{st}</g>')
    for i, (n, rot) in enumerate(((2, -10), (5, 7), (3, -4))):
        cx = 330 + i * 120
        o.append(f'<g transform="translate({cx - 54},253)">{die_svg(n, 90, "px", fill=ACCENT, pip="#fff", stroke="#000", sw=4, rot=rot, inline=False)}</g>')
    o.append("</svg>")
    return "".join(o)


def cover_page():
    return (f'<section class="page cover"><div class="store">{BRAND}</div>'
            f'<div style="width:7.3in">{cover_art()}</div>'
            f'<div class="ctitle"><div class="a">ROLL AND</div><div class="b">COMPOSE</div>'
            f'<div class="c">Winter dice games for rhythm and melody · staff paper · sharing rubric</div></div>'
            f'<div class="cband">Grades 2–5 <em>·</em> 3 levels <em>·</em> {TOTAL_PAGES} pages</div></section>')


def teacher_page():
    lv = ("<colgroup>" + "<col>" * 4 + "</colgroup>"
          f'<tr><th>Level</th><th>Grades</th><th>Length</th><th>Pages</th></tr>'
          f'<tr><td><b>A</b></td><td>2–3</td><td>4 bars</td><td>{P_A_TBL}–{P_A_REC}</td></tr>'
          f'<tr><td><b>B</b></td><td>3–4</td><td>4 bars</td><td>{P_B_TBL}–{P_B_REC}</td></tr>'
          f'<tr><td><b>C</b></td><td>4–5</td><td>8 bars</td><td>{P_C_TBL}–{P_C_REC}</td></tr>')
    body = (f'<div class="rule"><h1>Teacher Notes</h1><div class="l" style="font-size:13pt">{TITLE} · dice composing in 3 levels · grades 2–5</div></div>'
            '<div class="cols"><div>'
            '<h2>How it works</h2><ul>'
            '<li>Students roll a die (1 to 6) and look the number up in a dice table. The table turns each roll into a rhythm or a note.</li>'
            '<li>Every bar adds up. In Levels A and B one rhythm roll fills one beat, and in Level C one rhythm roll fills a whole bar, so any sequence of rolls can be finished.</li>'
            '<li>Level A rolls rhythm only, on a one-line staff. Level B adds pitch from C, D, E, G and A. Level C uses two dice, 8 bars and a call and response.</li>'
            '<li>No die in the room? A classroom die, a paper cube or an online dice roller all work. Any way of getting a number from 1 to 6 is fine.</li>'
            '<li>Every composition is different, so there is no single answer. Pages ' + f'{P_EX1}–{P_EX2}' + ' show one completed example for each level, with the rolls beside the notation.</li></ul>'
            '<h2>Materials</h2><ul><li>A die for each pair of students (or a paper cube, or a device with an online dice roller) and pencils with erasers.</li>'
            '<li>Optional: unpitched percussion, and bells or keyboards set to C, D, E, G and A.</li></ul>'
            '</div><div>'
            '<h2>Levels and pages</h2>'
            f'<table class="dt">{lv}</table>'
            f'<p class="small">Pages {P_ST4}–{P_ST8} are blank staff paper (4 bars and 8 bars). Page {P_RUB} is the sharing rubric, page {P_SHARE} has performance ideas, and page {P_REF} is a student reference.</p>'
            '<h2>Pacing</h2><ul>'
            '<li>Level A: two lessons of about 20 minutes. Learn the table and compose one piece, then compose a second and share.</li>'
            '<li>Level B: two or three lessons of 20 to 30 minutes.</li>'
            '<li>Level C: three or four lessons of 25 to 30 minutes, with the last one for sharing.</li>'
            '<li>Short on time? Use only the level that fits your grade.</li></ul>'
            '<h2>Differentiation</h2><ul>'
            '<li>Support: start with Level A for everyone, or let students keep the dice table and the student reference on their desks.</li>'
            '<li>Challenge: ask students to roll again for any bar they do not like, or to write a second 4-bar piece that answers the first.</li></ul>'
            '</div></div>'
            '<h2>Every level, four steps</h2><div class="steps">'
            '<div class="step"><span class="n">1</span><b>Roll</b><p>Roll a die and write the number in the next box.</p></div>'
            '<div class="step"><span class="n">2</span><b>Look</b><p>Find the number in the dice table.</p></div>'
            '<div class="step"><span class="n">3</span><b>Draw</b><p>Draw what the table shows on the staff.</p></div>'
            '<div class="step"><span class="n">4</span><b>Play</b><p>Perform it, share it and score it with the rubric.</p></div></div>'
            '<h2>Good to know</h2><p class="small">Model the first bar with the whole class on the board. Skills: reading and writing rhythm, notating pitch on the treble staff, '
            'and creating and sharing short pieces. This supports the Creating strand of the National Core Arts Standards for music; please match the skills to your own curriculum. '
            'No songs, lyrics or copyrighted characters are used.</p>'
            + foot(COPY, "Page 2"))
    return page_wrap(body, cls="page doc")


def ref_page():
    rows = ""
    for sid, kinds, beats, nm, say, ln in (("REF-q", ["q"], 1, "Quarter note", "ta", "1 beat"), ("REF-ee", ["e", "e"], 1, "Two eighth notes", "ti-ti", "1 beat in all"),
                                             ("REF-h", ["h"], 2, "Half note", "ta-a", "2 beats"), ("REF-r", ["r"], 1, "Quarter rest", "shh", "1 beat of silence")):
        rows += f'<tr><td>{sym_custom(sid, kinds, beats, 70, 5.2)}</td><td>{nm}</td><td><b>{say}</b></td><td>{ln}</td></tr>'
    tbl = ('<table class="dt"><colgroup>' + "<col>" * 4 + '</colgroup><tr><th>Symbol</th><th>Name</th><th>Say</th><th>Length</th></tr>' + rows + "</table>")
    bank = pitch_bank_svg("REF-BANK", ["C4", "D4", "E4", "G4", "A4", "C5"], 480, 9.0)
    body = (f'<div class="rule"><h1>Student Reference</h1><div class="l" style="font-size:13pt">Keep this page beside you while you roll and compose.</div></div>'
            '<h2>Rhythm symbols</h2>' + tbl +
            '<h2>The notes you can roll</h2><div class="box" style="display:flex;justify-content:center;padding:6pt 10pt 2pt">' + bank + '</div>'
            '<p class="small" style="margin-top:4pt">The notes are C, D, E, G and A, and then high C. Middle C sits on its own short line below the staff, and high C sits in the third space.</p>'
            '<div class="cols"><div><h2>Stems and beams</h2><ul>'
            '<li>Below the middle line, the stem goes up on the right side of the note.</li>'
            '<li>On or above the middle line, the stem goes down on the left side.</li>'
            '<li>Two eighth notes share a beam.</li></ul></div>'
            '<div><h2>Three ways to roll</h2><ul>'
            '<li>A classroom die.</li><li>A paper cube numbered 1 to 6.</li><li>An online dice roller.</li></ul></div></div>'
            '<h2>Roll, look, draw, play</h2><div class="steps">'
            '<div class="step"><span class="n">1</span><b>Roll</b><p>Roll a die and write the number in the next box.</p></div>'
            '<div class="step"><span class="n">2</span><b>Look</b><p>Find the number in the dice table.</p></div>'
            '<div class="step"><span class="n">3</span><b>Draw</b><p>Draw what the table shows on the staff.</p></div>'
            '<div class="step"><span class="n">4</span><b>Play</b><p>Perform it, share it and score it with the rubric.</p></div></div>'
            + foot(COPY, "Page 3"))
    return page_wrap(body, cls="page doc")


def terms_page():
    body = (f'<div class="rule"><h1>Terms of Use</h1><div class="l" style="font-size:13pt">Thank you for your purchase!</div></div>'
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
            f'<li>The dice tables, examples, staff paper, rubric and snow art (snowflakes, snowballs and snowmen): original work, {BRAND} by {STORE}. No songs are used.</li>'
            f'<li>Music notation font: Bravura © Steinberg Media Technologies GmbH, SIL Open Font License 1.1.</li>'
            f'<li>Text fonts: Oswald (The Oswald Project Authors) and Source Sans 3 (Adobe), SIL Open Font License 1.1.</li></ul>'
            f'<h2>What is in this file</h2><p>Page 1 cover, page 2 teacher notes, page 3 student reference, pages {P_A_TBL}–{P_C_REC} the dice tables and roll-and-record sheets for Levels A, B and C, '
            f'pages {P_ST4}–{P_ST8} staff paper, pages {P_EX1}–{P_EX2} the examples, page {P_RUB} the sharing rubric, page {P_SHARE} the share ideas and page {P_TERMS} these terms.</p>'
            f'<p class="small">{DISCLOSURE}</p>'
            + foot(COPY, f"Page {P_TERMS}"))
    return page_wrap(body, cls="page doc")


def full_pages():
    pages = [cover_page(), teacher_page(), ref_page(), a_table_page(), a_record_page(), b_table_page(), b_record_page(), c_table_page(), c_record_page(),
             staff4_page(), staff8_page(), ex1_page(), ex2_page(), rubric_page(), share_page(), terms_page()]
    assert len(pages) == TOTAL_PAGES, len(pages)
    return pages


def preview_pages():
    return [a_table_page(True), b_record_page(True), c_table_page(True), ex1_page(True)]


def extra_pages():     # watermarked pages used only as shots inside the preview images
    return [c_record_page(True), ex2_page(True), rubric_page(True), staff4_page(True), share_page(True)]


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
.lbl { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 24px; text-align: center; margin-top: 20px; }
.cp { font-family: 'Oswald'; font-weight: 300; font-size: 21px; line-height: 1.25; text-align: center; text-wrap: balance; margin-top: 6px; }
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
        f'<div><div class="hd" style="font-size:74px">Roll and</div>'
        f'<div class="hd" style="font-size:132px">Compose</div>'
        f'<div class="sub" style="font-size:27px;margin-top:12px">Winter dice games for rhythm and melody · staff paper · sharing rubric</div></div>'
        f'</div><div class="band">Grades 2–5 <em>·</em> 3 levels <em>·</em> {TOTAL_PAGES} pages</div></div>')


def dice_row(n=5, size=68, flake=30):
    parts = []
    for i in range(n):
        d = [3, 6, 1, 4, 2][i % 5]
        parts.append(die_svg(d, size, "px", fill=ACCENT, pip="#fff", stroke="#000", sw=4, rot=(-8, 6, -4, 8, -6)[i % 5], inline=True))
        if i < n - 1:
            parts.append(f'<svg data-icon="flake" data-icon-sw="1.8" width="{flake * 28 / 24:g}" height="{flake * 28 / 24:g}" viewBox="-2 -2 28 28" style="margin:0 4px">{snowflake(12, 12, 10, "#000", 1.8)}</svg>')
    return f'<div style="display:flex;align-items:center;justify-content:center;gap:10px">{"".join(parts)}</div>'


def shots_row(imgs, caps, width=300, gap=26):
    cols = "".join(
        f'<div style="width:{width}px;display:flex;flex-direction:column;align-items:center"><div class="shot"><img src="{imgs[i]}"></div>'
        f'<div class="lbl">{caps[i][0]}</div><div class="cp" style="width:{width - 10}px">{caps[i][1]}</div></div>' for i in range(len(imgs)))
    return f'<div style="display:flex;gap:{gap}px;align-items:flex-start;justify-content:center">{cols}</div>'


def preview_square_1(img):
    caps = [("Level A · grades 2–3", "One roll, one beat. Four rolls fill a bar."),
            ("Level B · grades 3–4", "Roll for rhythm and for pitch."),
            ("Level C · grades 4–5", "Two dice, 8 bars, call and response.")]
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div>'
        f'<div class="hd" style="font-size:74px;margin-top:24px">3 levels of dice composing</div>'
        f'<div class="sub" style="font-size:29px;margin-top:10px">Roll a die, look it up, compose a piece</div>'
        f'<div style="margin-top:20px">{dice_row()}</div>'
        f'<div style="flex:1;display:flex;align-items:center;justify-content:center;padding-bottom:56px">{shots_row(img, caps)}</div>'
        f'<div class="band">Rhythm <em>·</em> melody <em>·</em> call and response</div></div>')


def preview_square_2(a, b):
    caps = [("Roll and record sheet", "Write each roll, then draw the notes."), ("Completed example", "The rolls are shown beside the notation.")]
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div>'
        f'<div class="hd" style="font-size:74px;margin-top:24px">Completed examples included</div>'
        f'<div class="sub" style="font-size:28px;margin-top:10px">See exactly how the rolls turn into notation</div>'
        f'<div style="flex:1;display:flex;align-items:center;justify-content:center;padding-bottom:56px">{shots_row([a, b], caps, 380, 56)}</div>'
        f'<div class="band">One example for every level</div></div>')


def preview_square_3(imgs):
    caps = [("Sharing rubric", "Five rows, 20 points in all."), ("Staff paper", "Blank 4-bar and 8-bar staves."), ("Share ideas", "Ten ways to perform.")]
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div>'
        f'<div class="hd" style="font-size:64px;margin-top:30px">Rubric, staff paper, sharing</div>'
        f'<div class="sub" style="font-size:28px;margin-top:10px">Everything for the lesson, ready to print</div>'
        f'<div style="margin-top:20px">{dice_row()}</div>'
        f'<div style="flex:1;display:flex;align-items:center;justify-content:center;padding-bottom:56px">{shots_row(imgs, caps)}</div>'
        f'<div class="band">Printable PDF <em>·</em> US Letter <em>·</em> {TOTAL_PAGES} pages</div></div>')


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
    return f"""# UPLOAD: {LISTING_TITLE} (TpT 051)

These fields follow the order of TpT's "Add a resource" form. Winter theme: build window is December to February. Never put Winter, Snow or Holiday in the title field (TpT's Seasonal Titles notice).

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
Roll and Compose, Winter: a dice composing activity for music class. Students roll a die (1 to 6), look the number up in a dice table and turn it into rhythm and melody. Three levels, blank staff paper, completed examples and a sharing rubric are included. Snowflakes, snowballs and snowmen decorate the pages. The content is winter themed and non-denominational. For music classes in grades 2 to 5.

WHAT'S INCLUDED ({TOTAL_PAGES} pages, PDF, US Letter)
• Cover (1 page)
• Teacher notes with pacing and the four steps: roll, look, draw, play (1 page)
• Student reference: rhythm symbols, the notes on the staff, stems and beams (1 page)
• Level A, grades 2-3: dice table and a roll-and-record sheet. Roll for rhythm, one roll per beat, 4 bars in 4/4 (2 pages)
• Level B, grades 3-4: dice tables and a roll-and-record sheet. Roll for rhythm and for pitch using C, D, E, G and A on the treble staff, 4 bars (2 pages)
• Level C, grades 4-5: dice tables and a roll-and-record sheet. Two dice, 8 bars, call and response, ending on C (2 pages)
• Blank staff paper with treble clef: 4-bar staves and 8-bar staves (2 pages)
• Completed examples with the rolls shown beside the notation: Levels A and B on one page, Level C on another (2 pages)
• Sharing rubric with a total score out of 20 (1 page)
• Performance and share ideas (1 page)
• Terms of use and credits (1 page)
Total: {TOTAL_PAGES} pages.

HOW TO USE
Students roll a die and write each number in a box. In Level A one roll fills one beat with a quarter note, a pair of eighth notes or a quarter rest, so every bar adds up to 4 beats. Level B adds a pitch die for the notes C, D, E, G and A. Level C uses a rhythm die for each bar and a pitch die for each note, with a call (bars 1-4) and a response (bars 5-8) that ends on C. Any way of getting a number from 1 to 6 works: a classroom die, a paper cube or an online dice roller. Good for centers, early finishers, sub plans and composition units.

• Grades 2–5 (choose the level that fits)
• Prints well in black and white
• Pacing and performance ideas included

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
- Level A dice table and roll-and-record sheet: 2
- Level B dice tables and roll-and-record sheet: 2
- Level C dice tables and roll-and-record sheet: 2
- Blank staff paper, 4 bars and 8 bars: 2
- Completed examples: 2
- Sharing rubric: 1
- Performance and share ideas: 1
- Terms of use and credits: 1
- Total: {TOTAL_PAGES}

## 6. Standards

None cited by code. The teacher notes name the Creating strand of the National Core Arts Standards for music and ask teachers to match the skills to their own curriculum.

## 7. Price

**${PRICE}** (paid; owner range $3-5).

## 8. Preview

Paid. Preview PDF: Level A dice table, Level B roll-and-record sheet, Level C dice tables and the completed examples for Levels A and B, all watermarked.

## 9. Before you click publish

- [ ] Season: winter (December to February). Build for 2 to 8 weeks ahead of that.
- All music is original and generated from dice rules; the examples come from fixed roll sequences.
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
    extra = write("extra.html", html_doc(extra_pages(), "Extra"))
    render([{"html": full, "pdf": PDF}, {"html": prev, "pdf": PREVIEW_PDF}, {"html": extra, "pdf": os.path.join(BUILD, "extra.pdf")}])
    for i in range(1, 5):
        subprocess.run(["pdftoppm", "-png", "-r", "130", "-f", str(i), "-l", str(i), "-singlefile", PREVIEW_PDF, os.path.join(BUILD, f"pv{i}")], check=True)
    for i in range(1, 6):
        subprocess.run(["pdftoppm", "-png", "-r", "130", "-f", str(i), "-l", str(i), "-singlefile", os.path.join(BUILD, "extra.pdf"), os.path.join(BUILD, f"ex{i}")], check=True)
    # pv1 A table, pv2 B record, pv3 C table, pv4 examples; ex1 C record, ex2 example C, ex3 rubric, ex4 staff paper, ex5 share
    sq = [write("cover.html", cover_square()),
          write("p1.html", preview_square_1(["pv1.png", "pv2.png", "pv3.png"])),
          write("p2.html", preview_square_2("ex1.png", "ex2.png")),
          write("p3.html", preview_square_3(["ex3.png", "ex4.png", "ex5.png"]))]
    outs = [COVER_PNG] + PREVIEW_PNGS
    render([{"html": h, "png": o, "width": 1000, "height": 1000, "scale": 2} for h, o in zip(sq, outs)])
    with open(UPLOAD, "w") as f:
        f.write(upload_md())
    with open(TPT_JSON, "w") as f:
        json.dump(tpt_json(), f, indent=2)
        f.write("\n")
    print(f"built {PDF}, {PREVIEW_PDF}, cover + 3 previews, UPLOAD.md, tpt.json")



# ------------------------------------------------------------------ checks (independent of the generator's tables)
SVG_RE = re.compile(r'<svg class="ns".*?</svg>', re.S)
LET7 = "CDEFGAB"
CK_A_BEAT = {1: "N1", 2: "N1", 3: "N.5 N.5", 4: "N.5 N.5", 5: "R1", 6: "N1"}
CK_B_BEAT = {1: "N1", 2: "N1", 3: "N1", 4: "N.5 N.5", 5: "N.5 N.5", 6: "N.5 N.5"}
CK_C_BAR = {1: "N1 N1 N1 N1", 2: "N1 N1 N2", 3: "N1 N.5 N.5 N1 N1", 4: "N.5 N.5 N.5 N.5 N2", 5: "N2 N2", 6: "N1 N1 N1 R1"}
CK_B_NOTE = {1: "C4", 2: "D4", 3: "E4", 4: "G4", 5: "A4"}
CK_C_NOTE = {1: "C4", 2: "D4", 3: "E4", 4: "G4", 5: "A4", 6: "C5"}
CK_GIVEN = {"B": {4: "C4"}, "C": {4: "G4", 8: "C4"}}      # 1-based bar -> last note you play
CK_WORD = {Fraction(1): "ta", Fraction(2): "ta-a", Fraction(1, 2): "ti"}
CK_SOL = {"C": "do", "D": "re", "E": "mi", "G": "sol", "A": "la"}
ALLOWED_PITCH = {"C4", "D4", "E4", "G4", "A4", "C5"}


def ck_tokens(txt):
    """'N1 N.5 R1' -> [(Fraction, is_rest)]"""
    return [(Fraction(t[1:]).limit_denominator(4), t[0] == "R") for t in txt.split()]


def strip_ns(s):
    return re.sub(r'\sxmlns="[^"]+"', "", s)


def cp_of(el):
    t = (el.text or "").strip()
    return ord(t[0]) if t else None


def pitch_from_y(y, bottom, S):
    n = round((bottom - S - y) / (S / 2))          # diatonic steps above G4 (the G clef's line)
    dn = 4 * 7 + LET7.index("G") + n
    return LET7[dn % 7] + str(dn // 7), abs((bottom - S - y) / (S / 2) - n) < 0.01


def parse_staff(svg_text):
    """Re-read one drawn staff. Returns (info, errors). info['bars'] is a list of bars; each bar is a list of (duration, pitch or None, is_rest, label)."""
    errs = []
    root = ET.fromstring(strip_ns(svg_text))
    A = root.attrib
    S, top = float(A["data-s"]), float(A["data-top"])
    staff, kind, sid = A["data-staff"], A["data-kind"], A["data-id"]
    tag = f"{sid}[{kind}]"
    bottom, mid = top + 4 * S, top + 2 * S
    sls = sorted(float(l.get("y1")) for l in root.iter("line") if l.get("class") == "sl")
    want = [top + i * S for i in range(5)] if staff == "five" else [mid]
    if len(sls) != len(want) or any(abs(a - b) > 0.02 for a, b in zip(sls, want)):
        return None, [f"{tag}: staff lines are wrong {sls}"]
    for l in root.iter("line"):
        if l.get("class") == "sl" and float(l.get("stroke-width")) < 0.13 * S - 0.01:
            errs.append(f"{tag}: staff line too thin")
    heads, rests, stems, leds, labs, labs2, bars, beams, clefs, tsig, fins, cnts, bns, chds, phl = [], [], [], [], [], [], [], [], [], [], [], [], [], [], []
    for el in root.iter():
        c = el.get("class")
        if el.tag == "text" and c == "head":
            heads.append((float(el.get("x")), float(el.get("y")), cp_of(el)))
        elif el.tag == "text" and c == "rest":
            rests.append((float(el.get("x")), float(el.get("y")), cp_of(el)))
        elif el.tag == "text" and c == "lab":
            labs.append((float(el.get("x")), (el.text or "").strip()))
        elif el.tag == "text" and c == "lab2":
            labs2.append((float(el.get("x")), (el.text or "").strip()))
        elif el.tag == "text" and c == "clef":
            clefs.append((float(el.get("x")), float(el.get("y")), cp_of(el)))
        elif el.tag == "text" and c == "cnt":
            cnts.append((el.text or "").strip())
        elif el.tag == "text" and c == "bn":
            bns.append((el.text or "").strip())
        elif el.tag == "text" and c == "chd":
            chds.append((el.text or "").strip())
        elif el.tag == "text" and c == "phl":
            phl.append((el.text or "").strip())
        elif el.tag == "line" and c == "stem":
            stems.append((float(el.get("x1")), float(el.get("y1")), float(el.get("x2")), float(el.get("y2")), float(el.get("stroke-width"))))
        elif el.tag == "line" and c == "led":
            leds.append((float(el.get("x1")), float(el.get("x2")), float(el.get("y1"))))
        elif el.tag == "line" and c == "bar":
            bars.append(float(el.get("x1")))
        elif el.tag == "rect" and c == "beam":
            beams.append((float(el.get("x")), float(el.get("y")), float(el.get("width")), float(el.get("height"))))
        elif el.tag == "rect" and c == "fin":
            fins.append(float(el.get("x")))
    for tg in root.iter("g"):
        if tg.get("class") == "timesig":
            tsig = [(cp_of(t), float(t.get("y"))) for t in tg.iter("text")]
    # clef and time signature
    if A["data-clef"] == "1":
        if len(clefs) != 1 or clefs[0][2] != G_TREBLE or abs(clefs[0][1] - (bottom - S)) > 0.02:
            errs.append(f"{tag}: treble clef missing or not curled round the G line")
    elif clefs:
        errs.append(f"{tag}: unexpected clef")
    if A["data-meter"] == "4/4":
        if [t[0] for t in tsig] != [G_TS + 4, G_TS + 4] or abs(tsig[0][1] - (top + 2 * S)) > 0.02 or abs(tsig[1][1] - (top + 4 * S)) > 0.02:
            errs.append(f"{tag}: time signature is not 4 over 4 in place")
    elif tsig:
        errs.append(f"{tag}: unexpected time signature")
    hw = HEAD_W * S
    events, used_stems, used_led = [], set(), set()
    parsed = []
    for (x, y, cp) in heads:
        cx = x + hw / 2
        if staff == "five":
            name, ok = pitch_from_y(y, bottom, S)
            if not ok:
                errs.append(f"{tag}: notehead at x={cx:.0f} is not on a line or space")
            step = round((bottom - y) / (S / 2))
        else:
            name, step = None, 4
            if abs(y - mid) > 0.02:
                errs.append(f"{tag}: notehead at x={cx:.0f} is not on the line")
        if name is not None and kind != "blank" and name not in ALLOWED_PITCH:
            errs.append(f"{tag}: {name} is outside C pentatonic (C D E G A, high C)")
        sw0 = 0.13 * S
        ups = [s for s in stems if abs(s[0] - (x + hw - sw0 / 2)) < 0.05 and abs(s[1] - (y - 0.168 * S)) < 0.02 and s[3] < s[1]]
        dns = [s for s in stems if abs(s[0] - (x + sw0 / 2)) < 0.05 and abs(s[1] - (y + 0.168 * S)) < 0.02 and s[3] > s[1]]
        if len(ups) + len(dns) != 1:
            errs.append(f"{tag}: note {name} at x={cx:.0f} has {len(ups) + len(dns)} correctly attached stems (right edge going up, left edge going down)")
            continue
        s = (ups or dns)[0]
        used_stems.add(s)
        up = bool(ups)
        length = abs(s[3] - s[1])
        if length < 3.5 * S - 0.05 or length > 8 * S:
            errs.append(f"{tag}: stem of {name} at x={cx:.0f} has length {length / S:.2f} spaces")
        if up and s[3] > mid + 0.02:
            errs.append(f"{tag}: up stem of {name} does not reach the middle line")
        if (not up) and s[3] < mid - 0.02:
            errs.append(f"{tag}: down stem of {name} does not reach the middle line")
        need = list(range(-2, step - 1, -2)) if step < 0 else []
        need += list(range(10, step + 1, 2)) if step > 8 else []
        for e_ in need:
            ly = bottom - e_ * S / 2
            m = [l for l in leds if abs(l[2] - ly) < 0.02 and l[0] < x and l[1] > x + hw]
            if len(m) != 1:
                errs.append(f"{tag}: ledger line missing for {name} at x={cx:.0f}")
            else:
                used_led.add(m[0])
        parsed.append({"x": cx, "step": step, "name": name, "head": "open" if cp == G_HALF else ("filled" if cp == G_HEAD else "?"), "stem": s, "up": up, "y": y})
    for l in leds:
        if l not in used_led:
            errs.append(f"{tag}: stray ledger line at y={l[2]:.1f}")
    for s in stems:
        if s not in used_stems:
            errs.append(f"{tag}: stem without a notehead")
    # beams: each joins exactly two stems, same direction, ends on the beam, direction follows the farther note
    beamed = set()
    for (bx, by, bw, bh) in beams:
        if abs(bh - 0.5 * S) > 0.02:
            errs.append(f"{tag}: beam thickness is {bh / S:.2f} spaces")
        grp = []
        for i, p in enumerate(parsed):
            s = p["stem"]
            inx = bx - 0.03 <= s[0] - s[4] / 2 and s[0] + s[4] / 2 <= bx + bw + 0.03
            end_ok = abs(s[3] - by) < 0.02 if p["up"] else abs(s[3] - (by + bh)) < 0.02
            if inx and end_ok:
                grp.append(i)
        if len(grp) != 2:
            errs.append(f"{tag}: a beam joins {len(grp)} stems (should be 2)")
            continue
        a_, b_ = (parsed[i] for i in grp)
        if a_["up"] != b_["up"]:
            errs.append(f"{tag}: beamed stems point opposite ways")
        oa, ob = a_["step"] - 4, b_["step"] - 4          # signed distance from the middle line (negative = below)
        if abs(oa) != abs(ob):
            lead = oa if abs(oa) > abs(ob) else ob
            want_down = not (lead < 0)
        else:                                            # equal distance: same side below -> up, otherwise down
            want_down = not (oa < 0 and ob < 0)
        if (not a_["up"]) != want_down:
            errs.append(f"{tag}: beamed pair at x={a_['x']:.0f} has stems {'down' if not a_['up'] else 'up'}, rule says {'down' if want_down else 'up'}")
        if a_["up"]:   # the beam sits at the stem tips, on the side away from the heads
            if not (by < min(a_["y"], b_["y"])):
                errs.append(f"{tag}: beam is not beyond the noteheads")
        beamed.update(grp)
    for i, p in enumerate(parsed):
        if i in beamed:
            continue
        want_up = p["step"] < 4
        if p["up"] != want_up:
            errs.append(f"{tag}: note {p['name'] or 'on the line'} at x={p['x']:.0f} has its stem {'up' if p['up'] else 'down'} (should be {'up' if want_up else 'down'})")
        if p["head"] == "filled" and kind != "bank" and False:
            pass
    for i, p in enumerate(parsed):
        if p["head"] == "open":
            p["dur"] = Fraction(2)
            if i in beamed:
                errs.append(f"{tag}: half note is beamed")
        elif p["head"] == "filled":
            p["dur"] = Fraction(1, 2) if i in beamed else Fraction(1)
        else:
            p["dur"] = None
            errs.append(f"{tag}: unknown notehead glyph")
        events.append({"x": p["x"], "dur": p["dur"], "pitch": p["name"], "rest": False})
    for (x, y, cp) in rests:
        cx = x + REST_W * S / 2
        if cp != G_QREST:
            errs.append(f"{tag}: unknown rest glyph")
        if abs(y - mid) > 0.02:
            errs.append(f"{tag}: quarter rest is not on the middle line")
        events.append({"x": cx, "dur": Fraction(1), "pitch": None, "rest": True})
    events.sort(key=lambda e: e["x"])
    # labels
    mode = A["data-labels"]
    if mode == "bank":
        for e in events:
            m1 = [t for t in labs if abs(t[0] - e["x"]) < 1.0]
            m2 = [t for t in labs2 if abs(t[0] - e["x"]) < 1.0]
            if len(m1) != 1 or len(m2) != 1 or m1[0][1] != e["pitch"][0] or m2[0][1] != CK_SOL[e["pitch"][0]]:
                errs.append(f"{tag}: label under {e['pitch']} is wrong")
    elif mode in ("rhythm", "letter"):
        n_lab = len([e for e in events if not (mode == "letter" and e["rest"])])
        if len(labs) != n_lab:
            errs.append(f"{tag}: {len(labs)} labels for {n_lab} labelled events")
        for e in events:
            m = [t for t in labs if abs(t[0] - e["x"]) < 1.0]
            if mode == "letter" and e["rest"]:
                if m:
                    errs.append(f"{tag}: a rest has a letter label")
                continue
            if len(m) != 1:
                errs.append(f"{tag}: event at x={e['x']:.0f} has {len(m)} labels")
                continue
            if mode == "rhythm":
                want_l = "shh" if e["rest"] else CK_WORD[e["dur"]]
            else:
                want_l = None if e["rest"] else e["pitch"][0]
            if want_l is not None and m[0][1] != want_l:
                errs.append(f"{tag}: label '{m[0][1]}' under a {'rest' if e['rest'] else e['pitch'] or e['dur']} should be '{want_l}'")
            if want_l is None and mode == "letter":
                errs.append(f"{tag}: a rest has a letter label")
    elif labs:
        errs.append(f"{tag}: labels on an unlabelled staff")
    # bars
    nb = int(A["data-nbars"])
    x0 = float(A["data-x0"])
    ends = sorted(bars)
    final = A["data-final"] == "1"
    if A["data-barlines"] == "1":
        if len(ends) != nb:
            errs.append(f"{tag}: {len(ends)} barlines for {nb} bars")
        if final and len(fins) != 1:
            errs.append(f"{tag}: final double barline missing")
        if (not final) and fins:
            errs.append(f"{tag}: unexpected final barline")
        bounds = [x0] + [b + (0.35 * S if (final and i == len(ends) - 1) else 0) for i, b in enumerate(ends)]
        groups = [[e for e in events if bounds[i] <= e["x"] < bounds[i + 1]] for i in range(len(bounds) - 1)]
        if sum(len(g_) for g_ in groups) != len(events):
            errs.append(f"{tag}: some notes fall outside the bars")
    else:
        if ends or fins:
            errs.append(f"{tag}: unexpected barlines")
        groups = [events]
    beats = Fraction(A["data-beats"])
    out_bars = []
    for bi, g_ in enumerate(groups):
        tot = sum(e["dur"] for e in g_) if g_ else Fraction(0)
        if g_ and tot != beats:
            errs.append(f"{tag}: bar {bi + 1} adds up to {tot} beats, expected {beats}")
        pos, i = Fraction(0), 0
        while i < len(g_):
            e = g_[i]
            if e["dur"] == Fraction(1, 2):
                if not (i + 1 < len(g_) and g_[i + 1]["dur"] == Fraction(1, 2) and pos.denominator == 1):
                    errs.append(f"{tag}: bar {bi + 1} has an eighth note that is not in a pair starting on a beat")
                pos += 1
                i += 2
                continue
            if e["dur"] == Fraction(2) and pos % 2 != 0:
                errs.append(f"{tag}: bar {bi + 1} has a half note starting on beat {int(pos) + 1}")
            pos += e["dur"]
            i += 1
        out_bars.append([(e["dur"], e["pitch"], e["rest"]) for e in g_])
    if A["data-labels"] == "" and A["data-kind"] in ("rec", "blank") and events:
        errs.append(f"{tag}: a blank staff has notes")
    # phrase labels, chord symbols, bar numbers, counts
    ph = A["data-phrase"]
    first = int(A["data-first"])
    if ph:
        want_ph = {"CALL": "CALL · bars 1–4", "RESPONSE": "RESPONSE · bars 5–8"}[ph]
        if (ph == "CALL") != (first == 1) or phl != [want_ph]:
            errs.append(f"{tag}: phrase label {phl} does not fit bars starting at {first}")
    if chds and any(c != "C" for c in chds):
        errs.append(f"{tag}: chord symbol is not C")
    if bns and bns != [str(first + i) for i in range(nb)]:
        errs.append(f"{tag}: bar numbers {bns}")
    if cnts and cnts != [str(k + 1) for _ in range(nb) for k in range(int(beats))]:
        errs.append(f"{tag}: beat counts {cnts}")
    info = {"id": sid, "kind": kind, "level": A["data-level"], "first": first, "bars": out_bars, "rr": A["data-rr"], "pr": A["data-pr"], "events": events, "staff": staff,
            "nbars": nb, "roll": A.get("data-roll")}
    return info, errs


def expected_bars(level, rr, pr, first):
    """Rebuild bars from printed rolls with the checker's own tables. rr/pr: lists per bar."""
    out = []
    for i, bar_rolls in enumerate(rr):
        absbar = first + i
        toks = []
        if level == "A":
            for r in bar_rolls:
                toks += ck_tokens(CK_A_BEAT[r])
            out.append([(d, None, rest) for d, rest in toks])
            continue
        if level == "B":
            for r in bar_rolls:
                toks += ck_tokens(CK_B_BEAT[r])
            table = CK_B_NOTE
        else:
            toks = ck_tokens(CK_C_BAR[bar_rolls[0]])
            table = CK_C_NOTE
        idx = [k for k, (d, rest) in enumerate(toks) if not rest]
        given = CK_GIVEN[level].get(absbar)
        need = len(idx) - (1 if given else 0)
        if len(pr[i]) != need:
            return None, f"bar {absbar}: {len(pr[i])} pitch rolls printed, {need} needed"
        names = [table[r] for r in pr[i]] + ([given] if given else [])
        it = iter(names)
        out.append([(d, None if rest else next(it), rest) for d, rest in toks])
    return out, None


def split_rolls(s):
    return [[int(x) for x in b.split()] for b in s.split("|")] if s else []


def verify_html():
    errs = []
    n_staff = n_dice = 0
    res = open(os.path.join(BUILD, "resource.html")).read().replace("\u2060", "")
    srcs = {"resource": res}
    for name in ("preview.html", "extra.html", "cover.html"):
        p = os.path.join(BUILD, name)
        if not os.path.exists(p):
            return [f"{name} missing: run gen.py first"], 0, 0
        srcs[name] = open(p).read()
    infos = {}
    for sname, text in srcs.items():
        for m in SVG_RE.finditer(text):
            info, e = parse_staff(m.group(0))
            errs += [f"{sname}: {x}" for x in e]
            if info is None:
                continue
            n_staff += 1
            infos.setdefault((sname, info["id"]), []).append(info)
        for m in re.finditer(r'<svg class="die" data-n="(\d)"[^>]*>(.*?)</svg>', text, re.S):
            n_dice += 1
            if m.group(2).count('class="pip"') != int(m.group(1)):
                errs.append(f"{sname}: a die face labelled {m.group(1)} has {m.group(2).count('class=\"pip\"')} pips")
    R = {k[1]: v for k, v in infos.items() if k[0] == "resource"}
    # dice-table symbols
    def one(sid):
        v = R.get(sid, [])
        if len(v) != 1:
            errs.append(f"{sid}: drawn {len(v)} times in the product")
            return None
        return v[0]
    def cmp_bar(sid, want, got_bar):
        got = [(d, p, r) for d, p, r in got_bar]
        if got != want:
            errs.append(f"{sid}: drawn {got} but the rule table gives {want}")
    for r in range(1, 7):
        for pre, tbl, lvl in (("SYM-A", CK_A_BEAT, "A"), ("SYM-BR", CK_B_BEAT, "B")):
            x = one(f"{pre}{r}")
            if x:
                want = [(d, None, rest) for d, rest in ck_tokens(tbl[r])]
                cmp_bar(f"{pre}{r}", want, x["bars"][0])
                if x["roll"] != str(r):
                    errs.append(f"{pre}{r}: roll attribute {x['roll']}")
        x = one(f"SYM-C{r}")
        if x:
            cmp_bar(f"SYM-C{r}", [(d, None, rest) for d, rest in ck_tokens(CK_C_BAR[r])], x["bars"][0])
        for pre, tbl, cnt in (("SYM-BP", CK_B_NOTE, 5), ("SYM-CP", CK_C_NOTE, 6)):
            if r > cnt:
                continue
            x = one(f"{pre}{r}")
            if x:
                cmp_bar(f"{pre}{r}", [(Fraction(1), tbl[r], False)], x["bars"][0])
    for sid, want in (("REF-q", "N1"), ("REF-ee", "N.5 N.5"), ("REF-h", "N2"), ("REF-r", "R1")):
        x = one(sid)
        if x:
            cmp_bar(sid, [(d, None, rest) for d, rest in ck_tokens(want)], x["bars"][0])
    x = one("REF-BANK")
    if x:
        got = [p for d, p, r in x["bars"][0]]
        if got != ["C4", "D4", "E4", "G4", "A4", "C5"]:
            errs.append(f"REF-BANK: notes {got}")
    # every eighth pair in a dice-table symbol must carry a beam, and the beam and stems must lie inside the drawing (not clipped)
    n_sym_pairs = 0
    for m in re.finditer(r'<svg class="ns" data-kind="sym" data-id="([^"]+)"[^>]*viewBox="0 0 ([\d.]+) ([\d.]+)"[^>]*>(.*?)</svg>', res, re.S):
        sid_, vw_, vh_, body_ = m.group(1), float(m.group(2)), float(m.group(3)), m.group(4)
        n_e = body_.count('data-kind="e"')
        n_b = body_.count('class="beam"')
        if n_e != 2 * n_b:
            errs.append(f"{sid_}: {n_e} eighth notes but {n_b} beams (every eighth pair needs a beam)")
        n_sym_pairs += n_b
        for bm in re.finditer(r'<rect class="beam" x="([\d.]+)" y="([\d.]+)" width="([\d.]+)" height="([\d.]+)"', body_):
            bx_, by_, bw_, bh_ = map(float, bm.groups())
            if by_ < 0 or by_ + bh_ > vh_ or bx_ + bw_ > vw_:
                errs.append(f"{sid_}: beam is clipped by the edge of the drawing")
        for sm in re.finditer(r'<line class="stem" x1="[\d.]+" y1="([\d.]+)" x2="[\d.]+" y2="([\d.]+)"', body_):
            if max(float(sm.group(1)), float(sm.group(2))) > vh_ or min(float(sm.group(1)), float(sm.group(2))) < 0:
                errs.append(f"{sid_}: a stem is clipped by the edge of the drawing")
    if n_sym_pairs < 9:
        errs.append(f"only {n_sym_pairs} beamed eighth pairs found in dice-table symbols")
    # examples and artwork: rebuild from the printed rolls
    n_ex = 0
    for (sname, sid), lst in infos.items():
        for x in lst:
            if not x["rr"]:
                continue
            rr = split_rolls(x["rr"])
            pr = split_rolls(x["pr"]) if x["pr"] else [[] for _ in rr]
            want, err = expected_bars(x["level"], rr, pr, x["first"])
            if err:
                errs.append(f"{sname}/{sid}: {err}")
                continue
            if x["bars"] != want:
                errs.append(f"{sname}/{sid}: drawn notation differs from the rolls.\n    drawn {x['bars']}\n    rolls give {want}")
            n_ex += 1
    # example roll tables must show the same numbers as the staff attributes
    cells = {}
    for m in re.finditer(r'<td[^>]*?data-ex="(\w+)" data-bar="(\d)" data-kind="(\w+)" data-roll="(\w+)"[^>]*>(.*?)</td>', res, re.S):
        ex_, bar, kd, roll, inner = m.groups()
        cells.setdefault((ex_, int(bar), kd), []).append((roll, re.sub(r"<[^>]+>", "|", inner).strip("|").split("|")))
        txt = re.sub(r"<[^>]+>", "", inner).strip()
        if not txt.startswith(roll):
            errs.append(f"{ex_} bar {bar}: printed cell '{txt}' differs from its roll {roll}")
    def table_rolls(ex_, nbars, first, kd):
        return [[int(r) for r, _ in cells.get((ex_, first + i, kd), [])] for i in range(nbars)]
    for ex_, svgs in (("EXA", ["EXA"]), ("EXB", ["EXB"]), ("EXC", ["EXC1", "EXC2"])):
        for sid in svgs:
            x = one(sid)
            if not x:
                continue
            rr, pr = split_rolls(x["rr"]), (split_rolls(x["pr"]) if x["pr"] else [])
            if table_rolls(ex_, x["nbars"], x["first"], "rr") != rr:
                errs.append(f"{ex_}: rhythm rolls in the table differ from the rolls behind {sid}")
            if pr and table_rolls(ex_, x["nbars"], x["first"], "pr") != pr:
                errs.append(f"{ex_}: pitch rolls in the table differ from the rolls behind {sid}")
            for i in range(x["nbars"]):
                g_ = cells.get((ex_, x["first"] + i, "given"))
                want_g = CK_GIVEN.get(x["level"], {}).get(x["first"] + i)
                got_g = g_[0][0] if g_ else None
                if want_g is not None and got_g != want_g[0]:
                    errs.append(f"{ex_} bar {x['first'] + i}: given note {got_g} should be {want_g[0]}")
                if want_g is None and g_:
                    errs.append(f"{ex_} bar {x['first'] + i}: unexpected given note")
    for r_, inner in cells.get(("EXA", 1, "rr"), []):
        pass
    for key, lst in cells.items():
        if key[0] == "EXA":
            for roll, parts in lst:
                word = {"N1": "ta", "N.5 N.5": "ti-ti", "R1": "shh"}[CK_A_BEAT[int(roll)]]
                if parts[-1] != word:
                    errs.append(f"EXA bar {key[1]}: word '{parts[-1]}' under roll {roll} should be '{word}'")
    # example endings
    xb, xc1, xc2 = one("EXB"), one("EXC1"), one("EXC2")
    if xb:
        last = [p for d, p, r in xb["bars"][-1] if not r][-1]
        if last != "C4":
            errs.append(f"EXB ends on {last}, not C")
    if xc1 and xc2:
        if [p for d, p, r in xc1["bars"][3] if not r][-1] != "G4":
            errs.append("EXC bar 4 does not end on G")
        if [p for d, p, r in xc2["bars"][3] if not r][-1] != "C4":
            errs.append("EXC bar 8 does not end on C")
        used = {p for x in (xc1, xc2) for b in x["bars"] for d, p, r in b if p}
        if "C5" not in used or "C4" not in used:
            errs.append("EXC should show both middle C and high C")
    # blank and record staves are really blank, and the staff-paper pages have the right counts
    blanks = [k for k in R if k.startswith("ST4-")]
    if len(blanks) != 7 or sum(1 for k in R if k.startswith("ST8-")) != 6:
        errs.append("staff paper pages do not hold 7 four-bar staves and 6 eight-bar staves")
    for k, v in R.items():
        if k.startswith("ST4-") and (v[0]["nbars"] != 4 or v[0]["first"] != 1):
            errs.append(f"{k}: not a 4-bar staff")
        if k.startswith("ST8-") and (v[0]["nbars"] != 4 or v[0]["first"] != (1 if k.endswith("A") else 5)):
            errs.append(f"{k}: not half of an 8-bar piece")
    # rubric
    rub = re.search(r'<table class="rub">.*?</table>', res, re.S).group(0)
    rows = re.findall(r'<td class="cr">.*?Score ____ / (\d+)</span></td>', rub, re.S)
    maxes = [int(x) for x in rows]
    total = sum(maxes)
    m = re.search(r"Total <span[^>]*> ______ / (\d+)</span>", res)
    if len(maxes) != 5 or not m or int(m.group(1)) != total:
        errs.append(f"rubric: rows {maxes} sum to {total} but the printed total is {m.group(1) if m else None}")
    bands = re.search(r"<b>(\d+)–(\d+)</b> Excellent · <b>(\d+)–(\d+)</b> Good · <b>(\d+)–(\d+)</b> Almost there · <b>(\d+)–(\d+)</b> Not yet", res)
    if not bands:
        errs.append("rubric: score bands not found")
    else:
        b = [int(x) for x in bands.groups()]
        if b[1] != total or b[6] != len(maxes) * 1 or any(b[i] != b[i + 1 + 1] + 1 for i in (0, 2, 4)) and False:
            errs.append(f"rubric: bands {b} do not span {len(maxes)}-{total}")
        if not (b[0] == b[3] + 1 and b[2] == b[5] + 1 and b[4] == b[7] + 1):
            errs.append(f"rubric: score bands have gaps {b}")
    # die faces on the dice-table pages
    return errs, n_staff, n_ex


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
      const cls = el => (el.className && el.className.baseVal !== undefined ? el.className.baseVal : el.className);
      document.querySelectorAll('.page').forEach((pg, i) => {
        const pr = pg.getBoundingClientRect();
        const ft = pg.querySelector('.foot');
        const ftop = ft ? ft.getBoundingClientRect().top : pr.bottom;
        if (pg.scrollHeight > pg.clientHeight + 1) res.push(`page ${i + 1}: content overflows the page`);
        const boxes = [];
        pg.querySelectorAll('svg.ns, svg.die, table, .box, .step, .idea, .how, .name, .top, .doc p, .doc ul, .comp, .chk, h2, .cap').forEach(el => {
          if (ft && ft.contains(el)) return;
          if (el.closest('.top') && !el.matches('.top')) return;
          const r = el.getBoundingClientRect();
          if (r.height === 0) return;
          if (r.bottom > ftop - 10) res.push(`page ${i + 1}: ${el.tagName}.${cls(el)} bottom is ${(r.bottom - ftop).toFixed(1)}px vs the footer rule (needs <= -10)`);
          if (r.right > pr.right - 0.35 * 96 + 0.5 || r.left < pr.left + 0.35 * 96 - 0.5) res.push(`page ${i + 1}: ${el.tagName}.${cls(el)} too close to the page edge`);
          if (el.matches('svg.ns, svg.die, table, .box, .step, .idea') && !(el.parentNode.closest && el.parentNode.closest('svg'))) boxes.push([el, r]);
        });
        for (let a = 0; a < boxes.length; a++) for (let c = a + 1; c < boxes.length; c++) {
          const A = boxes[a][1], C = boxes[c][1];
          if (boxes[a][0].contains(boxes[c][0]) || boxes[c][0].contains(boxes[a][0])) continue;
          const gx = Math.max(A.left, C.left) - Math.min(A.right, C.right);
          const gy = Math.max(A.top, C.top) - Math.min(A.bottom, C.bottom);
          if (gx < 4 && gy < 4) res.push(`page ${i + 1}: ${cls(boxes[a][0])} and ${cls(boxes[c][0])} touch or overlap (gap ${Math.max(gx, gy).toFixed(1)}px)`);
        }
        // header: the title keeps >= 20px from the icons and the badge
        const top = pg.querySelector('.top');
        if (top) {
          const t = top.querySelector('.t').getBoundingClientRect();
          const tg = top.querySelector('.tag').getBoundingClientRect();
          const kids = [...top.querySelectorAll('.deco > *')].map(k => k.getBoundingClientRect());
          if (kids.length) {
            const l = Math.min(...kids.map(k => k.left)), rr = Math.max(...kids.map(k => k.right));
            if (l - t.right < 20) res.push(`page ${i + 1}: title is ${(l - t.right).toFixed(1)}px from the header icons`);
            if (tg.left - rr < 20) res.push(`page ${i + 1}: header icons are ${(tg.left - rr).toFixed(1)}px from the badge`);
          } else if (tg.left - t.right < 20) res.push(`page ${i + 1}: title is ${(tg.left - t.right).toFixed(1)}px from the badge`);
        }
        // labels inside one staff must not touch
        pg.querySelectorAll('svg.ns').forEach(sv => {
          const ts = [...sv.querySelectorAll('text.lab, text.lab2, text.bn, text.chd, text.cnt')].map(t => [t, t.getBoundingClientRect()]);
          for (let a = 0; a < ts.length; a++) for (let c = a + 1; c < ts.length; c++) {
            const A = ts[a][1], C = ts[c][1];
            if (Math.min(A.right, C.right) - Math.max(A.left, C.left) > -0.3 && Math.min(A.bottom, C.bottom) - Math.max(A.top, C.top) > 0) res.push(`page ${i + 1}: two labels touch in ${sv.getAttribute('data-id')}`);
          }
        });
        // table text must stay inside its cell and cells must not wrap to one-word orphans
        pg.querySelectorAll('td, th').forEach(td => {
          if (td.scrollWidth > td.clientWidth + 1) res.push(`page ${i + 1}: text overflows a table cell: "${td.innerText.trim().slice(0, 30)}"`);
        });
        pg.querySelectorAll('.doc p, .doc li, .how, .step p, .idea p, .box p').forEach(el => {
          const range = document.createRange(); range.selectNodeContents(el);
          const rects = [...range.getClientRects()].filter(q => q.width > 1);
          const lines = {};
          rects.forEach(q => { const k = Math.round(q.top / 3); lines[k] = lines[k] ? [Math.min(lines[k][0], q.left), Math.max(lines[k][1], q.right)] : [q.left, q.right]; });
          const ks = Object.keys(lines).map(Number).sort((a, b) => a - b);
          if (ks.length >= 2) {
            const last = lines[ks[ks.length - 1]];
            const w = el.getBoundingClientRect().width;
            const txt = el.innerText.trim().split(/\s+/);
            const lastWords = (() => { const rg = document.createRange(); return 0; })();
            if (last[1] - last[0] < 0.12 * w && txt.length > 5) res.push(`page ${i + 1}: short last line in "${el.innerText.trim().slice(0, 40)}..."`);
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
    files = [os.path.join(BUILD, n) for n in ("resource.html", "preview.html", "extra.html")]
    if not all(os.path.exists(x) for x in files):
        return ["build html missing: run gen.py first"]
    r = subprocess.run(["node", js, *files], capture_output=True, text=True, env=node_env())
    if r.returncode != 0:
        return [f"layout script failed: {r.stderr[-300:]}"]
    return json.loads(r.stdout.strip().splitlines()[-1])


EDGE_JS = r"""
const { chromium } = require('playwright');
const url = require('url');
(async () => {
  const b = await chromium.launch();
  const out = [];
  const SC = 6;
  for (const f of process.argv.slice(2)) {
    const p = await b.newPage({ viewport: { width: 816, height: 1056 } });
    await p.goto(url.pathToFileURL(f).href, { waitUntil: 'load' });
    const items = await p.evaluate(() => [...document.querySelectorAll('svg.die, svg[data-icon]')].map(e => {
      const o = e.cloneNode(true);
      return { html: o.outerHTML, w: e.getBoundingClientRect().width, h: e.getBoundingClientRect().height, sw: Number(e.getAttribute('data-sw') || e.getAttribute('data-icon-sw') || 2), vb: e.getAttribute('viewBox') };
    }));
    const seen = new Set();
    for (const it of items) {
      if (seen.has(it.html)) continue;
      seen.add(it.html);
      const q = await b.newPage({ viewport: { width: Math.ceil(it.w) + 8, height: Math.ceil(it.h) + 8 }, deviceScaleFactor: SC });
      await q.setContent('<html><body style="margin:0;background:transparent"><div id="x" style="position:absolute;left:4px;top:4px">' + it.html.replace(/display:inline-block;vertical-align:middle/, 'display:block') + '</div></body></html>');
      const buf = await q.locator('#x svg').screenshot({ omitBackground: true });
      const png = buf.toString('base64');
      const r = await q.evaluate(async (png) => {
        const im = new Image(); im.src = 'data:image/png;base64,' + png; await im.decode();
        const c = document.createElement('canvas'); c.width = im.width; c.height = im.height;
        const g = c.getContext('2d'); g.drawImage(im, 0, 0);
        const d = g.getImageData(0, 0, c.width, c.height).data;
        let x0 = 1e9, y0 = 1e9, x1 = -1, y1 = -1;
        for (let y = 0; y < c.height; y++) for (let x = 0; x < c.width; x++) if (d[(y * c.width + x) * 4 + 3] > 8) { x0 = Math.min(x0, x); x1 = Math.max(x1, x); y0 = Math.min(y0, y); y1 = Math.max(y1, y); }
        return { W: c.width, H: c.height, x0, y0, x1, y1 };
      }, png);
      const vbw = Number(it.vb.split(/\s+/)[2]);
      const upu = r.W / vbw;               // pixels per viewBox unit
      const need = Math.max(1, it.sw * upu * 0.999);
      const m = [r.x0, r.y0, r.W - 1 - r.x1, r.H - 1 - r.y1];
      if (r.x1 < 0) out.push(f.split('/').pop() + ': an icon rendered empty');
      else if (Math.min(...m) < 1) out.push(f.split('/').pop() + ': ' + (it.html.match(/data-n="(\d)"/) ? 'die ' + it.html.match(/data-n="(\d)"/)[1] : 'icon') + ' touches the edge of its render box (margins ' + m.join('/') + 'px)');
      else if (Math.min(...m) < need) out.push(f.split('/').pop() + ': ' + (it.html.match(/data-n="(\d)"/) ? 'die ' + it.html.match(/data-n="(\d)"/)[1] : 'icon') + ' has less padding than its stroke (margins ' + m.join('/') + 'px, needs ' + need.toFixed(1) + ')');
      await q.close();
    }
    await p.close();
  }
  await b.close();
  console.log(JSON.stringify(out));
})().catch(e => { console.error(e); process.exit(1); });
"""


def verify_edges():
    """Render every die (and other drawn icon) alone on a transparent ground: no ink on the box edge, and padding >= the stroke width."""
    js = os.path.join(BUILD, "edges.js")
    with open(js, "w") as f:
        f.write(EDGE_JS)
    files = [os.path.join(BUILD, n) for n in ("resource.html", "preview.html", "extra.html", "cover.html")]
    files = [x for x in files if os.path.exists(x)]
    r = subprocess.run(["node", js, *files], capture_output=True, text=True, env=node_env())
    if r.returncode != 0:
        return [f"edge script failed: {r.stderr[-300:]}"]
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
        last = max((y for y in range(0, ytop, 2) if rows[y // 2] > 0), default=0)
        if ytop - last > 200:
            errs.append(f"{os.path.basename(p)}: {ytop - last}px blank above the bottom band (more than 10%)")
        run = best = 0
        for y in range(120, ytop, 2):
            run, best = (run + 2, max(best, run + 2)) if rows[y // 2] == 0 else (0, best)
        if best > 260 and os.path.basename(p) != "cover.png":
            errs.append(f"{os.path.basename(p)}: blank band of {best}px")
        # nothing (a die, an icon) may touch the image edges: the top row and the side columns above the bottom band stay background
        top_ink = sum(1 for x in range(2000) if px[x, 0] < 200)
        band = 2000
        while band > 0 and px[0, band - 1] < 200 and px[1999, band - 1] < 200:
            band -= 1                      # the designed black bottom band reaches the edges; nothing else may
        side_ink = sum(1 for y in range(0, band) if px[0, y] < 200 or px[1999, y] < 200)
        if top_ink or side_ink:
            errs.append(f"{os.path.basename(p)}: ink touches the image edge ({top_ink}px on top, {side_ink}px on the sides)")
        # margins: left and right ink must be roughly even (a mockup must not hug one edge)
        cols = [sum(1 for y in range(130, ytop, 6) if px[x, y] < 200) for x in range(0, 2000, 2)]
        l = next((i * 2 for i, c in enumerate(cols) if c > 0), 0)
        r = next((2000 - i * 2 for i, c in enumerate(reversed(cols)) if c > 0), 2000)
        if abs(l - (2000 - r)) > 80:
            errs.append(f"{os.path.basename(p)}: uneven side margins ({l}px left, {2000 - r}px right)")
    return errs


def verify_files():
    errs = []
    from pypdf import PdfReader
    for p in [PDF, PREVIEW_PDF, COVER_PNG, *PREVIEW_PNGS, UPLOAD, TPT_JSON, os.path.join(TPT, "STYLE.md"), RENDER_JS, os.path.join(BUILD, "extra.pdf")]:
        if not os.path.exists(p):
            errs.append(f"missing {os.path.relpath(p, TPT)}")
    if errs:
        return errs
    for path, want in ((PDF, TOTAL_PAGES), (PREVIEW_PDF, 4), (os.path.join(BUILD, "extra.pdf"), 5)):
        rd = PdfReader(path)
        if len(rd.pages) != want:
            errs.append(f"{os.path.basename(path)}: {len(rd.pages)} pages, expected {want}")
        for i, pg in enumerate(rd.pages):
            if abs(float(pg.mediabox.width) - 612) > 1 or abs(float(pg.mediabox.height) - 792) > 1:
                errs.append(f"{os.path.basename(path)} p{i + 1}: not US Letter")
        if path != PDF or True:
            fonts = pdf_fonts(path)
            for name, emb in fonts:
                if emb != "yes":
                    errs.append(f"{os.path.basename(path)}: font {name} not embedded")
            names = " ".join(n for n, _ in fonts).lower().replace(" ", "")
            for fam in ("bravura", "oswald", "sourcesans3"):
                if fam not in names:
                    errs.append(f"{os.path.basename(path)}: {fam} not found in PDF fonts")
    rd = PdfReader(PDF)
    norm = lambda s: re.sub(r"(\d) – (\d)", r"\1–\2", " ".join((s or "").replace("\u2060", "").split()))
    texts = [norm(pg.extract_text()) for pg in rd.pages]
    for i, t in enumerate(texts):
        if len(t) < 40:
            errs.append(f"PDF page {i + 1} looks blank")
        if "PREVIEW" in t.upper():
            errs.append(f"product PDF page {i + 1} carries a PREVIEW watermark")
        if i >= 1 and not re.search(rf"Page {i + 1}\b", t):
            errs.append(f"PDF page {i + 1}: footer does not say Page {i + 1}")
    for p, key in PAGE_KEYS.items():
        if key.lower() not in texts[p - 1].lower():
            errs.append(f"page order: expected '{key}' on page {p}")
    # every watermarked page carries one PREVIEW, and the preview shows the right pages
    prd = PdfReader(PREVIEW_PDF)
    for i, key in enumerate([PAGE_KEYS[P_A_TBL], PAGE_KEYS[P_B_REC], PAGE_KEYS[P_C_TBL], PAGE_KEYS[P_EX1]]):
        t = norm(prd.pages[i].extract_text())
        if t.count("PREVIEW") != 1:
            errs.append(f"preview PDF page {i + 1}: expected exactly one PREVIEW watermark")
        if key.lower() not in t.lower():
            errs.append(f"preview PDF page {i + 1} should be '{key}'")
    for i, pg in enumerate(PdfReader(os.path.join(BUILD, "extra.pdf")).pages):
        if (pg.extract_text() or "").count("PREVIEW") != 1:
            errs.append(f"extra preview page {i + 1}: expected exactly one PREVIEW watermark")
    for n in ("p1.html", "p2.html", "p3.html", "cover.html"):
        h = open(os.path.join(BUILD, n)).read()
        if "PREVIEW" in h or 'class="wm"' in h:
            errs.append(f"{n}: has its own watermark text (the page shots already carry one)")
    errs += verify_images()
    # page-count claims
    first = texts[0].lower()
    if f"{TOTAL_PAGES} pages" not in first or "3 levels" not in first:
        errs.append("cover text does not state the page and level counts")
    t2 = texts[P_TEACH - 1]
    for need in (f"Pages {P_EX1}–{P_EX2}", f"Pages {P_ST4}–{P_ST8}", f"page {P_RUB}", f"page {P_SHARE}", f"page {P_REF}"):
        if need.lower() not in t2.lower():
            errs.append(f"teacher notes: missing '{need}'")
    for lvl, (a, b) in {"A": (P_A_TBL, P_A_REC), "B": (P_B_TBL, P_B_REC), "C": (P_C_TBL, P_C_REC)}.items():
        if not re.search(rf"{lvl} \d–\d (?:\d bars )?{a}–{b}", t2) and f"{a}–{b}" not in t2:
            errs.append(f"teacher notes: level {lvl} pages {a}–{b} missing")
    tt = texts[-1]
    if DISCLOSURE not in tt:
        errs.append("terms page lacks the disclosure line")
    for need in (f"pages {P_A_TBL}–{P_C_REC}", f"pages {P_ST4}–{P_ST8}", f"pages {P_EX1}–{P_EX2}", f"page {P_RUB}", f"page {P_SHARE}", f"page {P_TERMS}"):
        if need not in tt:
            errs.append(f"terms page: missing '{need}'")
    # cross-references printed in footers and text point at the right pages
    refs = {P_A_TBL: [f"Roll and record on page {P_A_REC}"], P_A_REC: [f"Example on page {P_EX1}", f"table on page {P_A_TBL}"], P_B_TBL: [f"Roll and record on page {P_B_REC}"],
            P_B_REC: [f"Example on page {P_EX1}", f"tables on page {P_B_TBL}"], P_C_TBL: [f"Roll and record on page {P_C_REC}"],
            P_C_REC: [f"Example on page {P_EX2}", f"tables on page {P_C_TBL}"], P_EX1: [f"pages {P_A_TBL} and {P_B_TBL}"], P_EX2: [f"page {P_C_TBL}"],
            P_SHARE: [f"Rubric on page {P_RUB}", f"rubric on page {P_RUB}"]}
    for p, needs in refs.items():
        for need in needs:
            if need not in texts[p - 1]:
                errs.append(f"page {p}: missing cross-reference '{need}'")
    # upload description and json
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
    for need in (DISCLOSURE, f"${PRICE}", f"{TOTAL_PAGES} pages", "Total: " + str(TOTAL_PAGES)):
        if need not in up:
            errs.append(f"UPLOAD.md: missing '{need}'")
    sec = up.split("## 5. Page count by section")[1].split("##")[0]
    nums = [int(x) for x in re.findall(r"^- (?!Total)[^\n]*: (\d+)$", sec, re.M)]
    if sum(nums) != TOTAL_PAGES:
        errs.append(f"UPLOAD.md page list sums to {sum(nums)}, PDF has {TOTAL_PAGES}")
    desc = up.split("## 2. Description")[1].split("## 3.")[0]
    dn = [int(x) for x in re.findall(r"\((\d+) pages?\)\s*$", desc, re.M)]
    if sum(dn) != TOTAL_PAGES:
        errs.append(f"UPLOAD.md description page list sums to {sum(dn)}, PDF has {TOTAL_PAGES}")
    low = up.lower()
    for bad in ("checked by hand", "handmade", "recomputed", "classroom-tested", "classroom tested", "in code", "answer key", "colour", "teachers' pay"):
        if bad in low and bad != "answer key":
            errs.append(f"UPLOAD.md says '{bad}'")
    tj = json.load(open(TPT_JSON))
    tags, subs = set(load_json("TAG-OPTIONS.json")["options"]), set(load_json("SUBJECT-OPTIONS.json"))
    if any(t not in tags for t in tj["tags"]) or any(s not in subs for s in tj["subjects"]):
        errs.append(f"tpt.json tags or subjects invalid")
    if tj.get("pages") != TOTAL_PAGES or tj["price"] != PRICE or not 1 <= len(tj["grades"]) <= 4:
        errs.append("tpt.json pages, price or grades mismatch")
    # US spelling and banned phrases in buyer-facing text
    for i, t in enumerate(texts):
        for bad in ("colour", "centre", "favourite", "practise", "organise", "grey"):
            if re.search(bad, t, re.I):
                errs.append(f"page {i + 1}: non-US spelling '{bad}'")
        for bad in ("recomputed", "in code", "verified by", "handmade", "hand-checked", "classroom-tested"):
            if bad in t.lower() and not (bad == "verified by" and DISCLOSURE.lower() in t.lower()):
                errs.append(f"page {i + 1}: internal wording '{bad}'")
    return errs


def check():
    errs, nstaff, nex = verify_html()
    errs += verify_layout()
    errs += verify_edges()
    errs += verify_files()
    if errs:
        print("CHECK FAILED")
        print("\n".join(" - " + e for e in errs[:80]))
        sys.exit(1)
    print(f"CHECK OK: {nstaff} drawn staves re-read from the rendered SVG (staff lines, treble clef, 4/4, noteheads vs staff positions, stems on the right/left edge and "
          f"direction, beams, ledger line for middle C, rests, barlines, labels); {nex} compositions and symbols rebuilt from their rolls with an independent rule table; "
          f"every bar sums to its meter; dice faces, dice tables, example roll tables, rubric total, page order and page-count claims verified; layout clear; "
          f"PDF {TOTAL_PAGES} Letter pages, preview 4 (one watermark each); images 2000x2000; UPLOAD.md and tpt.json ok.")


if __name__ == "__main__":
    if "--check" in sys.argv:
        import importlib
        check()
    else:
        build()
