#!/usr/bin/env python3
"""Key Signature and Scale Worksheets for Band (TpT 065): build the resource and verify it.

    python3 gen.py           build everything (PDFs, PNGs, UPLOAD.md, tpt.json) into this folder
    python3 gen.py --check   re-read every staff from the rendered HTML and verify the music, the transpositions, the layout and the images

Theory is computed in code (spelled pitches: letter + accidental; major scales; key signatures; transposition by interval). `--check` does not
trust that data. It parses the rendered SVG of every staff (clef glyph, key-signature accidentals and their staff positions, time signature,
noteheads, stems, ledger lines, barlines), works out the key signature and the scale that is really drawn, recomputes every transposition with a
different method (the line of fifths: written key = concert key + 2, +3 or +1 fifths, minus 12 when that passes 7 sharps or flats) and compares
the result with every answer printed in the charts, the worksheets and the answer keys.
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

SLUG = "key-signature-scale-worksheets-band"
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
TITLE = "Band Key Signatures"
LISTING_TITLE = "Key Signature & Scale Worksheets for Band: Transposition Charts, Keys, Gr 6-12"
PRICE = "5.00"
TAGS = ["Worksheets", "Printables", "Activities", "Assessment", "Study Guides"]
SUBJECTS = ["Music", "Instrumental Music"]
GRADES = ["6th-grade", "8th-grade", "10th-grade", "12th-grade"]

# ================================================================== theory (letters C D E F G A B = 0..6, accidental -1/0/+1)
LET = "CDEFGAB"
NPC = [0, 2, 4, 5, 7, 9, 11]
MAJ = [0, 2, 4, 5, 7, 9, 11]
SH, FL, NA = "", "", ""        # Bravura sharp, flat, natural


def pc(l, a):
    return (NPC[l] + a) % 12


def spell(l, p):
    """Accidental that letter l needs to sound pitch class p (range -6..5)."""
    return (p - NPC[l] + 6) % 12 - 6


def scale_of(l, a):
    return [((l + i) % 7, spell((l + i) % 7, (pc(l, a) + MAJ[i]) % 12)) for i in range(7)]


def sig_of(l, a):
    """Signed key signature of the major key with tonic (l, a): +n sharps, -n flats; None if the key needs a double sharp or flat."""
    if abs(a) > 1:
        return None
    accs = [x for _, x in scale_of(l, a)]
    if any(abs(x) > 1 for x in accs):
        return None
    assert not (any(x > 0 for x in accs) and any(x < 0 for x in accs))
    return sum(accs)


KEY_BY_SIG = {}
for _l in range(7):
    for _a in (-1, 0, 1):
        _n = sig_of(_l, _a)
        if _n is not None and abs(_n) <= 7:
            assert _n not in KEY_BY_SIG
            KEY_BY_SIG[_n] = (_l, _a)
assert sorted(KEY_BY_SIG) == list(range(-7, 8))
KEYS15 = [KEY_BY_SIG[n] for n in range(-7, 8)]          # Cb Gb Db Ab Eb Bb F C G D A E B F# C#
KEYS12 = [KEY_BY_SIG[n] for n in (0, 1, 2, 3, 4, 5, 6, -5, -4, -3, -2, -1)]   # circle of fifths from C: C G D A E B F# Db Ab Eb Bb F

# instrument groups: written = concert + interval. Interval = (letter steps up, semitones up).
GROUPS = ["C", "Bb", "Eb", "F"]
UP = {"C": (0, 0), "Bb": (1, 2), "Eb": (5, 9), "F": (4, 7)}
GROUP_NAME = {"C": "C instruments", "Bb": "B-flat instruments", "Eb": "E-flat instruments", "F": "F instruments"}
GROUP_SOUND = {"C": "sounds as written (unison)", "Bb": "sounds a major 2nd lower than written", "Eb": "sounds a major 6th lower than written",
               "F": "sounds a perfect 5th lower than written"}
GSHORT = {"C": "C", "Bb": "B-flat", "Eb": "E-flat", "F": "F"}
GROUP_UP = {"C": "the same key", "Bb": "up a major 2nd", "Eb": "up a major 6th", "F": "up a perfect 5th"}
GROUP_SHIFT = {"C": "no change", "Bb": "add 2 sharps (or take away 2 flats)", "Eb": "add 3 sharps (or take away 3 flats)",
               "F": "add 1 sharp (or take away 1 flat)"}
# instrument -> (group, how it sounds lower than written: (semitones down, words)), all intervals verified by `--check`
INSTR = {
    "flute": ("C", 0, "in unison"), "oboe": ("C", 0, "in unison"), "bassoon": ("C", 0, "in unison"), "trombone": ("C", 0, "in unison"),
    "tuba": ("C", 0, "in unison"), "euphonium (bass clef)": ("C", 0, "in unison"),
    "clarinet": ("Bb", 2, "a major 2nd lower"), "trumpet": ("Bb", 2, "a major 2nd lower"), "tenor sax": ("Bb", 14, "a major 9th lower"),
    "bass clarinet": ("Bb", 14, "a major 9th lower"),
    "alto sax": ("Eb", 9, "a major 6th lower"), "alto clarinet": ("Eb", 9, "a major 6th lower"), "baritone sax": ("Eb", 21, "an octave and a major 6th lower"),
    "horn in F": ("F", 7, "a perfect 5th lower"),
}


def transpose(l, a, steps, semis):
    nl = (l + steps) % 7
    return nl, spell(nl, (pc(l, a) + semis) % 12)


def best_key_for_pc(p):
    cands = []
    for L in range(7):
        A = spell(L, p)
        if abs(A) <= 1:
            c = sig_of(L, A)
            if c is not None and abs(c) <= 7:
                cands.append((abs(c), L, A, c))
    cands.sort()
    return cands[0][1], cands[0][2], cands[0][3]


def written_key(group, l, a):
    """(letter, acc, signed count, enharmonic?) of the written key for a concert key. Beyond 7 sharps or flats -> the enharmonic key."""
    st, se = UP[group]
    nl, na = transpose(l, a, st, se)
    c = sig_of(nl, na)
    if c is None or abs(c) > 7:
        L, A, c = best_key_for_pc(pc(nl, na))
        return L, A, c, True
    return nl, na, c, False


def concert_key(group, l, a):
    """Inverse: the concert key for a written key (move down by the same interval)."""
    st, se = UP[group]
    nl, na = transpose(l, a, (7 - st) % 7, (12 - se) % 12)
    c = sig_of(nl, na)
    assert c is not None and abs(c) <= 7, (group, l, a)
    return nl, na, c


def kn(l, a):
    """Key letter with a Bravura accidental, for tables and labels."""
    return LET[l] + ({1: f'<span class="ac">{SH}</span>', -1: f'<span class="ac">{FL}</span>', 0: ""}[a])


def kname(l, a):
    return kn(l, a) + " major"


def wname(l, a):
    return LET[l] + {1: "-sharp", -1: "-flat", 0: ""}[a]


def count_words(c):
    if c == 0:
        return "no sharps or flats"
    n = abs(c)
    return f"{n} {'sharp' if c > 0 else 'flat'}{'s' if n > 1 else ''}"


# ================================================================== notation drawing (Bravura, one staff per SVG)
G_CLEF, F_CLEF, SHARP, FLAT, NAT, HEAD, TS4 = 0xE050, 0xE062, 0xE262, 0xE260, 0xE261, 0xE0A4, 0xE084
CLEF_CP = {"G": G_CLEF, "F": F_CLEF}
CLEF_POS = {"G": 2, "F": 6}                 # staff position (0 = bottom line, 1 = first space ...) of the clef's own line
BOTTOM_D = {"G": 4 * 7 + 2, "F": 2 * 7 + 4}  # diatonic number (7*octave + letter) of the bottom line: E4 and G2
KS_SHARP = {"G": [(3, 5), (0, 5), (4, 5), (1, 5), (5, 4), (2, 5), (6, 4)], "F": [(3, 3), (0, 3), (4, 3), (1, 3), (5, 2), (2, 3), (6, 2)]}
KS_FLAT = {"G": [(6, 4), (2, 5), (5, 4), (1, 5), (4, 4), (0, 5), (3, 4)], "F": [(6, 2), (2, 3), (5, 2), (1, 3), (4, 2), (0, 3), (3, 3)]}
STEM_Y = 0.168
STEM_LEN = 3.5
_GB = {}


def gbox(cp):
    """Ink box of a Bravura glyph in staff spaces: (xmin, ymin, xmax, ymax), y up, origin at the glyph origin."""
    if not _GB:
        from fontTools.ttLib import TTFont
        from fontTools.pens.boundsPen import BoundsPen
        font = TTFont(os.path.join(FONTS, "bravura.woff2"))
        gs, cm, upm = font.getGlyphSet(), font.getBestCmap(), font["head"].unitsPerEm
        for c in (G_CLEF, F_CLEF, SHARP, FLAT, NAT, HEAD, TS4):
            bp = BoundsPen(gs)
            gs[cm[c]].draw(bp)
            _GB[c] = tuple(v / upm * 4 for v in bp.bounds)
    return _GB[cp]


def fx(v):
    return f"{v:.2f}"


def staff(clef, sig, S, uid, W=None, wmin=0.0, ts=False, bars=None, nblank=0, pad=3.0):
    """One five-line staff as an SVG string. sig = key signature drawn after the clef (signed count, 0 = none).
    bars: list of bars, each a list of notes (letter, octave, shown accidental or None): quarter notes in 4/4, filled in.
    nblank: number of empty bars (barlines only). Neither: a bare staff that ends after the key signature (width W or auto)."""
    sw = 0.13 * S
    d0 = BOTTOM_D[clef]
    order = (KS_SHARP if sig > 0 else KS_FLAT)[clef]
    nb = len(bars) if bars else nblank

    def draw(yb):
        els = []

        def add(svg, b):
            els.append((svg, b))

        def line(x1, y1, x2, y2, w, cls):
            add(f'<line class="{cls}" x1="{fx(x1)}" y1="{fx(y1)}" x2="{fx(x2)}" y2="{fx(y2)}" stroke="#000" stroke-width="{fx(w)}"/>',
                (min(x1, x2) - w / 2, min(y1, y2) - w / 2, max(x1, x2) + w / 2, max(y1, y2) + w / 2))

        def glyph(cp, x, y, cls):
            b = gbox(cp)
            add(f'<text class="{cls}" x="{fx(x)}" y="{fx(y)}" font-family="Bravura" font-size="{fx(4 * S)}" fill="#000">&#x{cp:X};</text>',
                (x + b[0] * S, y - b[3] * S, x + b[2] * S, y - b[1] * S))

        def ypos(p):
            return yb - p * S / 2

        x = 4.0
        glyph(CLEF_CP[clef], x, ypos(CLEF_POS[clef]), "clef")
        x += gbox(CLEF_CP[clef])[2] * S + 0.6 * S
        for i in range(abs(sig)):
            l, o = order[i]
            cp = SHARP if sig > 0 else FLAT
            glyph(cp, x, ypos(7 * o + l - d0), "kacc")
            x += gbox(cp)[2] * S + 0.22 * S
        if sig:
            x += 0.4 * S
        if ts:
            x += 0.5 * S
            glyph(TS4, x, ypos(6), "tsd")
            glyph(TS4, x, ypos(2), "tsd")
            x += gbox(TS4)[2] * S + 0.9 * S
        left0 = x
        Wd = W if W else max(wmin, left0 + 3 * S)
        xend = Wd - 4 - 0.5 * S - 0.45 * S      # thin barline of the final double bar
        for k in range(5):
            line(2, ypos(2 * k), Wd - 2, ypos(2 * k), sw, "sl")
        if nb:
            bw = (xend - left0) / nb
            for k in range(1, nb):
                line(left0 + k * bw, ypos(8), left0 + k * bw, ypos(0), 0.14 * S, "bar")
            line(xend, ypos(8), xend, ypos(0), 0.14 * S, "bar")
            add(f'<rect class="fin" x="{fx(Wd - 4 - 0.5 * S)}" y="{fx(ypos(8))}" width="{fx(0.5 * S)}" height="{fx(4 * S)}" fill="#000"/>',
                (Wd - 4 - 0.5 * S, ypos(8), Wd - 4, ypos(0)))
            for k, bar in enumerate(bars or []):
                slot = (bw - 1.2 * S) / 4
                for j, (l, o, acc) in enumerate(bar):
                    xc = left0 + k * bw + 1.2 * S + slot * (j + 0.5)
                    p = 7 * o + l - d0
                    y = ypos(p)
                    hl, hr = xc - 0.59 * S, xc + 0.59 * S
                    if acc is not None:
                        cp = {1: SHARP, -1: FLAT, 0: NAT}[acc]
                        b = gbox(cp)
                        glyph(cp, hl - 0.2 * S - b[2] * S, y, "nacc")
                    glyph(HEAD, hl, y, "head")
                    if p <= -2:
                        qs = [q for q in range(-2, p - 1, -2)]
                    elif p >= 10:
                        qs = [q for q in range(10, p + 1, 2)]
                    else:
                        qs = []
                    for q in qs:
                        line(hl - 0.4 * S, ypos(q), hr + 0.4 * S, ypos(q), 0.16 * S, "ledger")
                    if p >= 4:       # stem down on the left edge
                        sx = hl + sw / 2
                        line(sx, y + STEM_Y * S, sx, y + STEM_Y * S + STEM_LEN * S, sw, "stem")
                    else:            # stem up on the right edge
                        sx = hr - sw / 2
                        line(sx, y - STEM_Y * S, sx, y - STEM_Y * S - STEM_LEN * S, sw, "stem")
        return els, Wd

    els, Wd = draw(0.0)
    y0 = min(b[1] for _, b in els)
    y1 = max(b[3] for _, b in els)
    yb = pad - y0
    els, Wd = draw(yb)
    H = pad + (y1 - y0) + pad
    # horizontal padding: first ink and last ink are inside [pad, W - pad] by construction (clef at 4, staff lines 2..W-2)
    body = "".join(s for s, _ in els)
    return (f'<svg class="ns" data-id="{uid}" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {Wd:.2f} {H:.2f}" '
            f'width="{Wd:.2f}pt" height="{H:.2f}pt" style="display:block">{body}</svg>')


def scale_bars(l, a, octave=4, with_acc=False):
    """Notes of the ascending one-octave major scale as two bars of four quarter notes: (letter, octave, shown accidental). With with_acc the
    accidentals are shown on the notes (no key signature on the staff); otherwise the key signature supplies them."""
    sc = scale_of(l, a)
    notes = []
    for i in range(8):
        nl, na = sc[i % 7]
        notes.append((nl, octave + (l + i) // 7, (na if (with_acc and na != 0) else None)))
    return [notes[:4], notes[4:]]


# memory-trick facts, asserted here and re-checked from the drawings by --check
for _n in range(1, 8):
    _l, _a = KEY_BY_SIG[_n]
    assert (KS_SHARP["G"][_n - 1][0] + 1) % 7 == _l, "last sharp is a step below the tonic"
    _l, _a = KEY_BY_SIG[-_n]
    if _n >= 2:
        assert KS_FLAT["G"][_n - 2][0] == _l and _a == (0 if _n == 1 else _a)
assert [pc(*KEY_BY_SIG[n]) for n in range(8)] == [(7 * n) % 12 for n in range(8)]      # each sharp key is a fifth up
assert [pc(*KEY_BY_SIG[-n]) for n in range(8)] == [(-7 * n) % 12 for n in range(8)]     # each flat key is a fifth down

# ================================================================== worksheet content
W1_SIGS = [2, -3, 0, 1, -1, 4, -2, 3, -4, 1, -2, 4]
W2_SIGS = [-4, 3, 7, -1, 5, -6, 0, 2, -7, 6, -3, 1, -5, 4, -2]
W3_SIGS = [2, -3, 4, -5, 6, -2, 5, -4, 7, -6, 3, -1]
W4_SIGS = [1, -1, 2, -2, 3, -3]
W5_SIGS = [0, 4, -4, 5, -5, 6]
W6_ORDER = [3, 4, 5, 6, 0, 1, 2, -5, -4, -3, -2, -1]      # concert keys as signed counts, shuffled per sheet
CONCERT_SHEETS = {"Bb": [(-2, 0), (3, -3), (1, 5)], "Eb": [(2, -1), (4, -5), (6, 0)]}
SHEET_ORDER = {
    "Bb": [0, 3, -3, 1, -5, 4, 2, -1, 5, -2, -4, 6],
    "Eb": [-2, 1, 5, 0, -4, 3, -1, 2, 6, -3, 4, -5],
    "F": [4, -1, 2, -5, 0, 5, -3, 1, 6, -2, 3, -4],
}
for _g, _o in SHEET_ORDER.items():
    assert sorted(_o) == sorted(n for n in (0, 1, 2, 3, 4, 5, 6, -5, -4, -3, -2, -1)), _g
W9_ITEMS = [("clarinet", 3), ("alto sax", -2), ("horn in F", 2), ("trumpet", 0), ("baritone sax", 4), ("flute", -3),
            ("tenor sax", -1), ("horn in F", -4), ("alto clarinet", 1), ("trumpet", 6), ("alto sax", 5), ("bass clarinet", -5)]
W10_ITEMS = [("clarinet", 4), ("alto sax", 3), ("horn in F", 1), ("trumpet", -1), ("baritone sax", 0), ("tenor sax", 2),
             ("horn in F", -3), ("alto clarinet", 5), ("clarinet", -2), ("alto sax", -4), ("bass clarinet", 3), ("horn in F", 5)]
W11_KEYS = [-2, -3, -1, -4, 2, 3]            # concert keys: B-flat, E-flat, F, A-flat, D, A
Q_A = [-2, 3, -4, 5]
Q_B = [("trumpet", -4), ("alto sax", -2), ("horn in F", 2), ("clarinet", 2)]
Q_C = [("clarinet", 4), ("horn in F", 3)]
Q_D = ("alto sax", -3)                       # concert key E-flat for alto sax: write the written key signature
Q_E = -4                                      # write the A-flat major scale with accidentals
for _n, _l in ((n, KEY_BY_SIG[n]) for n in W1_SIGS + W2_SIGS):
    pass


def instr_group(name):
    return INSTR[name][0]


def key_of(n):
    return KEY_BY_SIG[n]


def written_of(inst, n):
    l, a = key_of(n)
    return written_key(instr_group(inst), l, a)


# every concert-to-written item used in a worksheet: no enharmonic surprises except on the mixed sheet and the quiz
for _g in ("Bb", "Eb", "F"):
    for _n in SHEET_ORDER[_g]:
        written_key(_g, *key_of(_n))
for _i, _n in W10_ITEMS:
    _l, _a = key_of(_n)
    concert_key(instr_group(_i), _l, _a)
for _i, _n in Q_C:
    concert_key(instr_group(_i), *key_of(_n))

# ================================================================== page registry
ORDER = ["cover", "teach", "pacing", "vocab", "rubric", "kschart", "circle", "overview", "tcC", "tcBb", "tcEb", "tcF",
         "w1", "w2", "w3", "w4", "w5", "w6", "w7", "w8", "w9", "w10", "w11", "quiz",
         "a12", "a3", "a45", "a678", "a910", "a11", "aq", "terms"]
P = {k: i + 1 for i, k in enumerate(ORDER)}
TOTAL_PAGES = len(ORDER)
PAGE_NAMES = {
    "cover": "cover", "teach": "Teacher notes", "pacing": "Pacing plan", "vocab": "Vocabulary", "rubric": "Rubric and score sheet",
    "kschart": "Key signature chart", "circle": "Circle of fifths and memory tricks", "overview": "Transposing instruments at a glance",
    "tcC": "Transposition chart: C instruments", "tcBb": "Transposition chart: B-flat instruments", "tcEb": "Transposition chart: E-flat instruments",
    "tcF": "Transposition chart: F instruments",
    "w1": "Worksheet 1: Name the key (up to 4 sharps or flats)", "w2": "Worksheet 2: Name the key (all 15 key signatures)",
    "w3": "Worksheet 3: Write the key signature", "w4": "Worksheet 4: Write the scale (key signature given)",
    "w5": "Worksheet 5: Write the scale (add the accidentals)", "w6": "Worksheet 6: Concert to written, B-flat instruments",
    "w7": "Worksheet 7: Concert to written, E-flat instruments", "w8": "Worksheet 8: Concert to written, horn in F",
    "w9": "Worksheet 9: Concert to written, mixed instruments", "w10": "Worksheet 10: Written to concert, mixed instruments",
    "w11": "Worksheet 11: One concert key, every section", "quiz": "Quiz: key signatures, scales and transposition",
    "a12": "Answer key: Worksheets 1 and 2", "a3": "Answer key: Worksheet 3", "a45": "Answer key: Worksheets 4 and 5",
    "a678": "Answer key: Worksheets 6, 7 and 8", "a910": "Answer key: Worksheets 9 and 10", "a11": "Answer key: Worksheet 11",
    "aq": "Answer key: Quiz", "terms": "Terms of use and credits",
}
KEY_PAGE = {"w1": "a12", "w2": "a12", "w3": "a3", "w4": "a45", "w5": "a45", "w6": "a678", "w7": "a678", "w8": "a678", "w9": "a910", "w10": "a910",
            "w11": "a11", "quiz": "aq"}
assert set(ORDER) == set(PAGE_NAMES)
WS_POINTS = {"w1": len(W1_SIGS), "w2": len(W2_SIGS), "w3": len(W3_SIGS), "w4": 2 * len(W4_SIGS), "w5": 2 * len(W5_SIGS), "w6": 12, "w7": 12, "w8": 12,
             "w9": len(W9_ITEMS), "w10": len(W10_ITEMS), "w11": 3 * len(W11_KEYS), "quiz": len(Q_A) + len(Q_B) + len(Q_C) + 2 + 8}
TOTAL_POINTS = sum(WS_POINTS.values())
assert WS_POINTS["quiz"] == 20
XREFS = []


def xref(frm, to, text):
    XREFS.append((P[frm], to, text))
    return text


def pg(key):
    return f"page {P[key]}"


# ================================================================== CSS and frame
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
.top .t small { display: block; font-family: 'Oswald'; font-weight: 300; text-transform: none; font-size: 11pt; letter-spacing: 0; margin-top: 3pt; white-space: nowrap; }
.top .tag { flex: none; white-space: nowrap; text-align: right; }
.tag .lv { display: inline-block; background: #000; color: #fff; font-family: 'Oswald'; font-weight: 700; font-size: 15pt; padding: 3pt 9pt 4pt; border-radius: 4pt; letter-spacing: .04em; }
.tag .lv.ak { background: ACCENT; }
.tag .ln { font-family: 'Oswald'; font-weight: 300; font-size: 11pt; margin-top: 3pt; }
.foot { display: flex; justify-content: space-between; font-size: 8.5pt; color: #333; border-top: .8pt solid #000; padding-top: 3pt; margin-top: auto; }
.wm { position: absolute; left: 50%; top: 50%; transform: translate(-50%, -50%) rotate(-38deg); font-family: 'Oswald'; font-weight: 700;
      font-size: 150pt; color: rgba(0,0,0,.13); letter-spacing: .06em; white-space: nowrap; pointer-events: none; z-index: 9; }
.ac { font-family: 'Bravura'; font-weight: 400; font-size: 1.2em; display: inline-block; width: .34em; height: .62em; line-height: .62em; overflow: hidden; vertical-align: baseline; position: relative; margin-left: .04em; }
.doc h1 { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 28pt; margin: 0 0 4pt; line-height: 1; }
.doc h2 { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 13.5pt; margin: 8pt 0 3pt; letter-spacing: .02em; }
.doc p, .doc li { font-size: 10.6pt; line-height: 1.34; margin: 0 0 5pt; }
.doc ul { margin: 0 0 4pt; padding-left: 16pt; }
.doc .rule { border-bottom: 2.2pt solid #000; margin-bottom: 8pt; padding-bottom: 6pt; }
.doc table { border-collapse: collapse; width: 100%; table-layout: fixed; font-size: 10pt; margin: 2pt 0 4pt; }
.doc td, .doc th { border: 1pt solid #000; padding: 3pt 6pt; text-align: left; vertical-align: middle; }
.doc th { font-family: 'Oswald'; font-weight: 500; text-transform: uppercase; font-size: 9.5pt; background: #000; color: #fff; }
.small { font-size: 9pt !important; color: #333; }
.box { border: 1.3pt solid #000; border-radius: 7pt; padding: 7pt 10pt 4pt; margin: 6pt 0; }
.box h3 { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 12.5pt; margin: 0 0 3pt; letter-spacing: .02em; }
.box p, .box li { font-size: 10.4pt !important; }
.box p { margin: 0 0 4pt !important; }
.cols { display: flex; gap: 12pt; }
.cols .box { flex: 1; margin: 6pt 0; }
.nd { display: flex; align-items: flex-end; gap: 6pt; font-size: 10pt; margin: 7pt 0 0; }
.nd .ln { flex: 1; border-bottom: 1pt solid #000; height: 11pt; }
.inst { font-size: 10.4pt; line-height: 1.3; margin: 6pt 0 0; }
.grid { flex: 1; display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); grid-auto-rows: 1fr; gap: 9pt 12pt; padding: 8pt 0 10pt; }
.grid.one { grid-template-columns: 1fr; }
.grid.three { grid-template-columns: repeat(3, minmax(0, 1fr)); }
.it, .ak { border: 1.3pt solid #000; border-radius: 7pt; padding: 5pt 8pt; display: flex; flex-direction: column; justify-content: center; position: relative; }
.it .nm, .ak .nm { position: absolute; left: 7pt; top: 4pt; font-family: 'Oswald'; font-weight: 700; font-size: 11pt; }
.it svg, .ak svg { margin: 2pt auto; }
.it .al, .ak .al { font-size: 10.4pt; display: flex; gap: 8pt; align-items: flex-end; justify-content: center; margin-top: 3pt; }
.it .al .ln { border-bottom: 1pt solid #000; width: 62pt; height: 11pt; }
.it .al .ln.w { width: 80pt; }
.it .pr { font-size: 10.4pt; text-align: center; margin: 0 0 2pt; padding: 0 12pt; }
.ak .ans { font-weight: 700; }
.ak .pr { text-align: center; padding: 0 14pt; }
.grid, .ksg { min-width: 0; }
.trow.akr td { height: 19pt; font-size: 9.8pt; padding: 1pt 5pt; }
.trow.akr.two td { height: 28pt; }
.trow.akr td.n { width: 20pt; }
.il { font-size: 9.6pt; line-height: 1.25; margin: 0 0 2pt; }
.ak .al { gap: 12pt; }
.sn { font-size: 10pt; text-align: center; letter-spacing: .05em; font-weight: 600; }
.trow td { height: 31pt; font-size: 11pt; }
.trow.tall td { height: 37pt; }
.trow td.n { width: 28pt; text-align: center; font-family: 'Oswald'; font-weight: 700; }
.trow td.q { font-weight: 600; }
.trow td.bl { background: #fff; }
.trow.akr td.bl { background: #fff; font-weight: 700; }
.tc td { text-align: center; padding: 2pt 4pt; height: 41pt; }
.tc td.k { font-size: 11pt; line-height: 1.15; }
.tc td.k b { font-size: 12.5pt; }
.tc td.k .cw { font-size: 9.2pt; color: #333; }
.tc td svg { margin: 0 auto; }
.tc td.arr { font-family: 'Oswald'; font-weight: 700; font-size: 14pt; padding: 0; }
.ksg { flex: 1; display: grid; grid-template-columns: 1fr 1fr 1fr; grid-auto-rows: 1fr; gap: 8pt; padding: 8pt 0 8pt; }
.ksc { border: 1.3pt solid #000; border-radius: 7pt; display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 3pt 6pt; }
.ksc b { font-size: 12.5pt; }
.ksc .cw { font-size: 9.5pt; color: #333; }
.exr { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8pt; margin: 6pt 0; }
.exr .ex { border: 1.3pt solid #000; border-radius: 7pt; padding: 3pt 4pt 5pt; text-align: center; font-size: 9.6pt; }
.exr .ex b { display: block; font-size: 10.4pt; }
.cfwrap { position: relative; width: 376pt; height: 376pt; flex: none; margin: 4pt auto; }
.cfwrap svg { position: absolute; left: 0; top: 0; }
.cfk { position: absolute; width: 60pt; height: 36pt; margin: -18pt 0 0 -30pt; white-space: nowrap; text-align: center; font-size: 10.5pt; line-height: 1.05; display: flex; flex-direction: column; justify-content: center; }
.cfk b { font-size: 11pt; }
.cfk .cc { font-size: 8.4pt; color: #333; }
.cfmid { position: absolute; left: 50%; top: 50%; transform: translate(-50%,-50%); text-align: center; font-family: 'Oswald'; font-weight: 500; font-size: 11pt; letter-spacing: .06em; text-transform: uppercase; }
.cfmid small { display: block; font-family: 'Source Sans 3'; text-transform: none; letter-spacing: 0; font-weight: 400; font-size: 9pt; }
.dtab td { vertical-align: top; }
.dtab td.t { font-family: 'Oswald'; font-weight: 700; text-transform: uppercase; font-size: 11pt; width: 118pt; letter-spacing: .02em; }
.rub td, .rub th { font-size: 9.4pt; }
.sct td { padding: 2pt 6pt; font-size: 9.8pt; }
.cover { align-items: center; justify-content: space-between; padding: 0.55in 0.6in 0.5in; }
.store { font-family: 'Oswald'; font-weight: 500; font-size: 13pt; letter-spacing: .32em; text-transform: uppercase; }
.ctitle { text-align: center; }
.ctitle .a { font-family: 'Oswald'; font-weight: 700; font-size: 40pt; line-height: 1; letter-spacing: .02em; }
.ctitle .b { font-family: 'Oswald'; font-weight: 700; white-space: nowrap; font-size: 68pt; line-height: .95; letter-spacing: .01em; }
.ctitle .c { font-family: 'Oswald'; font-weight: 300; font-size: 16pt; margin-top: 8pt; }
.cband { width: 100%; background: #000; color: #fff; text-align: center; font-family: 'Oswald'; font-weight: 500; font-size: 14pt;
         letter-spacing: .08em; text-transform: uppercase; padding: 8pt 0 9pt; border-radius: 4pt; white-space: nowrap; }
.cband em { font-style: normal; color: ACCENT; }
""".replace("ACCENT", ACCENT)


def html_doc(pages, title="doc"):
    return (f'<!doctype html><html><head><meta charset="utf-8"><title>{escape(title)}</title><style>{font_css()}{CSS}</style></head>'
            f'<body>{"".join(pages)}</body></html>')


COPY = f"© {YEAR} {STORE} · {BRAND} · For single-classroom use"


def wm_div(on):
    return '<div class="wm">PREVIEW</div>' if on else ""


def page(key, body, wm=False, tag="TEACHER", tagline="", ak=False, extra="", student=False):
    n = P[key]
    sub = PAGE_NAMES[key]
    right = f"Page {n}" + (f" · {extra}" if extra else "")
    top = (f'<div class="top"><div class="t">{TITLE}<small>{sub}</small></div>'
           f'<div class="tag"><div class="lv{" ak" if ak else ""}">{tag}</div><div class="ln">{tagline}</div></div></div>')
    nd = ('<div class="nd"><span>Name</span><span class="ln"></span><span>Date</span><span class="ln" style="flex:.45"></span>'
          '<span>Class</span><span class="ln" style="flex:.4"></span></div>') if student else ""
    return (f'<section class="page doc" data-p="{n}" data-k="{key}">{wm_div(wm)}{top}{nd}{body}'
            f'<div class="foot"><span>{COPY}</span><span>{right}</span></div></section>')


def sheet_page(key, body, wm=False):
    n = int(key[1:]) if key[0] == "w" else 0
    tag = f"WORKSHEET {n}" if key[0] == "w" else "QUIZ"
    return page(key, body, wm, tag=tag, tagline="Student page", extra=xref(key, KEY_PAGE[key], f"Answer key: page {P[KEY_PAGE[key]]}"), student=True)


def ak_page(key, body, wm=False):
    return page(key, body, wm, tag="ANSWER KEY", tagline="Teacher copy", ak=True)


def sig_staff(n, clef="G", S=5.6, W=200, uid=""):
    return staff(clef, n, S, uid, W=W)


def cw(n):
    return count_words(n)


def nm_html(n):
    l, a = key_of(n)
    return kname(l, a)


# ================================================================== pages
def cover_page():
    return (f'<section class="page cover" data-p="1" data-k="cover"><div class="store">{BRAND}</div>'
            f'<div style="height:4.5in;display:flex;align-items:center;justify-content:center"><img src="../art/hero.png" alt="" style="display:block;height:4.5in;width:auto"></div>'
            f'<div class="ctitle"><div class="a">BAND WORKSHEETS</div><div class="b">KEY SIGNATURES</div>'
            f'<div class="c">Scales and concert pitch transposition for C, B-flat, E-flat and F instruments</div></div>'
            f'<div class="cband">Grades 6–12 <em>·</em> 11 worksheets <em>·</em> {TOTAL_PAGES} pages</div></section>')


def teach_page(wm=False):
    body = (
        f'<div class="cols"><div class="box"><h3>What is inside</h3><ul>'
        f'<li>Reference: key signature chart ({pg("kschart")}), circle of fifths ({pg("circle")}), transposing instruments ({pg("overview")}) and four transposition charts (pages {P["tcC"]}–{P["tcF"]}).</li>'
        f'<li>Eleven worksheets and a quiz (pages {P["w1"]}–{P["quiz"]}), each with an answer key (pages {P["a12"]}–{P["aq"]}).</li>'
        f'<li>Pacing plan ({pg("pacing")}), vocabulary ({pg("vocab")}) and a rubric with a score sheet ({pg("rubric")}).</li></ul></div>'
        f'<div class="box"><h3>How to use</h3><ul><li>Teach the chart pages first, then assign the worksheets in order. Each takes 10 to 15 minutes.</li>'
        f'<li>Copy the student pages only. Keep the answer keys for yourself.</li>'
        f'<li>Students may keep the charts open while they work on Worksheets 1 to 8, then close them for the quiz.</li></ul></div></div>'
        f'<h2>Grade guide</h2><table><tr><th style="width:92pt">Grades</th><th>Worksheets</th><th style="width:150pt">Focus</th></tr>'
        f'<tr><td>6–7</td><td>1, 3, 4, 6</td><td>Reading and writing key signatures; scales</td></tr>'
        f'<tr><td>8–9</td><td>2, 5, 7, 8</td><td>All 15 key signatures; concert to written pitch</td></tr>'
        f'<tr><td>10–12</td><td>9, 10, 11 and the quiz</td><td>Mixed instruments; written to concert; score reading</td></tr></table>'
        f'<h2>Standards</h2><p>The activities support the Performing and Responding processes of the National Core Arts Standards for Music (for example, analyzing the structure of music selected for performance). Match them to your own curriculum.</p>'
        f'<h2>Facts that matter for the answer keys</h2><ul>'
        f'<li><b>Written key = concert key plus the instrument\'s interval.</b> B-flat instruments (clarinet, trumpet, tenor sax) sound a major 2nd below the written note, so the written key is a major 2nd higher. E-flat instruments (alto sax, baritone sax, alto clarinet) sound a major 6th lower, so the written key is a major 6th higher. Horn in F sounds a perfect 5th lower, so the written key is a perfect 5th higher.</li>'
        f'<li>Baritone sax sounds an octave plus a major 6th lower, tenor sax and bass clarinet an octave plus a major 2nd lower. The octave changes the register but not the key, so the charts apply to them too.</li>'
        f'<li><b>No key signature has more than 7 sharps or flats.</b> When a transposition would need 8 or more, the answer key gives the enharmonic key and marks it with an asterisk (for example, concert F-sharp major for B-flat instruments would be G-sharp major with 8 sharps, so it is written A-flat major with 4 flats). Students are told this on the chart pages.</li>'
        f'<li>Only major keys are covered. Treble clef is used for scales; both clefs appear in the key signature work.</li></ul>'
        f'<p class="small">No songs, lyrics or copyrighted characters are used. {DISCLOSURE}</p>')
    return page("teach", body, wm, tag="TEACHER", tagline="Read first")


PACING = [
    ("1", "Vocabulary and the key signature chart. Students read the chart and find where each sharp and flat goes.", "vocab, kschart", "w1"),
    ("2", "The circle of fifths and the order of sharps and flats. Practice the memory tricks.", "circle", "w2"),
    ("3", "Writing key signatures in treble and bass clef.", "kschart", "w3"),
    ("4", "Major scales with the key signature given. Check each half step.", "circle", "w4"),
    ("5", "Major scales with accidentals written on the notes.", "kschart", "w5"),
    ("6", "Transposing instruments: why a clarinet part looks different from a flute part. Concert to written for B-flat instruments.", "overview", "tcBb"),
    ("7", "Concert to written for E-flat instruments.", "tcEb", "w6"),
    ("8", "Concert to written for horn in F, then mixed instruments.", "tcF", "w8"),
    ("9", "Written to concert, then one concert key for every section.", "overview", "w10"),
    ("10", "Quiz and score sheet.", "rubric", "quiz"),
]
PACING_WS = {"1": "w1", "2": "w2", "3": "w3", "4": "w4", "5": "w5", "6": "w6", "7": "w7", "8": ("w8", "w9"), "9": ("w10", "w11"), "10": "quiz"}


def pacing_page(wm=False):
    rows = ""
    for d, txt, ref, ws in PACING:
        w = PACING_WS[d]
        rows += (f'<tr><td style="text-align:center;font-family:Oswald;font-weight:700;font-size:13pt">{d}</td><td>{txt}</td>'
                 f'<td>{xref("pacing", 0, f"page {P[ref.split(", ")[0]]}")}</td><td>{xref("pacing", 0, (f"pages {P[w[0]]}\u2013{P[w[1]]}" if isinstance(w, tuple) else f"page {P[w]}"))}</td></tr>')
    body = (f'<p>A ten-session plan for a band or orchestra class that meets daily or a few times a week. Each session is 10 to 15 minutes, so it fits at the start of rehearsal. Stretch it to two weeks of bell ringers, or run two sessions a day for a unit.</p>'
            f'<table style="margin-top:6pt"><tr><th style="width:44pt">Session</th><th>What happens</th><th style="width:70pt">Teach from</th><th style="width:70pt">Student page</th></tr>{rows}</table>'
            f'<div class="box"><h3>Rehearsal tie-in</h3><ul><li>Before a concert-key warm-up, ask each section to name its written key (for example: concert B-flat is clarinet C, alto sax G, horn F).</li>'
            f'<li>Play a scale from Worksheet 4 or 5 as a unison warm-up, one section at a time.</li>'
            f'<li>When a new piece arrives, students write the concert key and their written key at the top of the part.</li></ul></div>'
            f'<div class="box"><h3>Differentiation</h3><ul><li>Support: give students the charts and let them finish Worksheets 1, 3 and 4 only. Ask them to check the quiz with the circle of fifths open.</li>'
            f'<li>Extension: have students write the written key and signature for every key on Worksheet 11 for a section they play in a second instrument, or invent transposition questions for a partner.</li></ul></div>'
            f'<div class="box"><h3>Time check</h3><p>Worksheets 1, 3, 6, 7 and 8 take about 10 minutes. Worksheets 2, 4, 5, 9, 10 and 11 take about 15 minutes, and the quiz takes about 20 minutes in all.</p></div>')
    return page("pacing", body, wm, tag="TEACHER", tagline="Ten sessions")


VOCAB = [
    ("Concert pitch", "The pitch that actually sounds. Every player in the band hears the same concert pitch."),
    ("Written pitch", "The note printed in a player's own part. For a transposing instrument it is not the sounding pitch."),
    ("Transposing instrument", "An instrument whose written music sounds higher or lower than the printed notes, such as clarinet, alto sax or horn in F."),
    ("Key signature", "The sharps or flats at the start of each staff that tell you which notes are always raised or lowered."),
    ("Major scale", "Eight notes in a row built from the pattern whole, whole, half, whole, whole, whole, half."),
    ("Whole step / half step", "A whole step is two half steps. A half step is the smallest distance on the keyboard."),
    ("Tonic", "The first note of a scale. It gives the key its name."),
    ("Accidental", "A sharp, flat or natural sign written beside a note. It changes that note, not the whole key."),
    ("Sharp / flat / natural", "A sharp raises a note a half step, a flat lowers it a half step, and a natural cancels both."),
    ("Circle of fifths", "A diagram that puts the 12 major keys in order, each a perfect 5th above the last. It shows how many sharps or flats each key has."),
    ("Enharmonic", "Two names for the same pitch, such as G-sharp and A-flat. Enharmonic keys sound the same but are spelled differently."),
    ("Interval", "The distance between two pitches, such as a major 2nd, a major 6th or a perfect 5th."),
    ("Clef", "The sign at the start of a staff that fixes the note names. Treble clef is for high instruments and bass clef is for low ones."),
    ("Staff", "Five lines and four spaces on which music is written. Notes are named by their line or space."),
    ("Ledger line", "A short extra line used for notes above or below the staff."),
    ("Octave", "Eight scale steps apart. Two notes an octave apart have the same letter name."),
]


def vocab_page(wm=False):
    rows = "".join(f'<tr><td class="t" style="padding:5pt 6pt">{t}</td><td style="font-size:11.2pt;line-height:1.32;padding:5pt 8pt">{d}</td></tr>' for t, d in VOCAB)
    body = (f'<p>Use these 16 words with the charts and worksheets. Students can copy them into a notebook, add a drawing or an example, or use them as a word wall for a unit on band music theory.</p>'
            f'<table class="dtab" style="margin-top:4pt">{rows}</table>')
    return page("vocab", body, wm, tag="REFERENCE", tagline="16 words")


def rubric_page(wm=False):
    prows = "".join(f'<tr><td>{PAGE_NAMES[k].split(": ")[0]}: {PAGE_NAMES[k].split(": ")[1] if ": " in PAGE_NAMES[k] else ""}</td><td style="text-align:center">{WS_POINTS[k]}</td><td></td></tr>'
                    for k in ["w1", "w2", "w3", "w4", "w5", "w6", "w7", "w8", "w9", "w10", "w11", "quiz"])
    body = (f'<h2>How the points work</h2><p>Items on Worksheets 1, 2, 3, 6 to 10 and 11 are worth 1 point each. A transposition item earns its point only when the key name and the number of sharps or flats are both right. '
            f'A scale on Worksheets 4 and 5 is worth 2 points: 1 for the right notes and 1 for the right sharps or flats. The quiz is worth 20 points. A suggested scale for the quiz: 18–20 exceeds, 15–17 meets, 11–14 approaching, 10 or fewer beginning.</p>'
            f'<table class="rub"><tr><th style="width:90pt">Skill</th><th>4 Exceeds</th><th>3 Meets</th><th>2 Approaching</th><th>1 Beginning</th></tr>'
            f'<tr><td><b>Key signatures</b></td><td>Names and writes every key signature, in both clefs, with the sharps and flats in the correct order and places.</td><td>Names and writes most signatures correctly; one or two errors in order or position.</td><td>Needs the chart for most signatures; mixes up sharps and flats.</td><td>Cannot yet read or write a key signature.</td></tr>'
            f'<tr><td><b>Scales</b></td><td>Writes every scale with correct notes, accidentals, stems and ledger lines.</td><td>Notes are correct; a few accidentals missing or misplaced.</td><td>Right starting note, but half steps are in the wrong places.</td><td>Cannot yet build a scale.</td></tr>'
            f'<tr><td><b>Transposition</b></td><td>Names the written or concert key for any instrument and uses the enharmonic key when needed.</td><td>Correct for the common keys; one or two slips with extreme keys.</td><td>Needs the chart; uses the wrong interval for some instruments.</td><td>Cannot yet transpose a key.</td></tr></table>'
            f'<h2>Score sheet</h2><table class="sct"><tr><th>Page</th><th style="width:62pt">Possible</th><th style="width:62pt">Score</th></tr>{prows}'
            f'<tr><td><b>Total</b></td><td style="text-align:center"><b>{TOTAL_POINTS}</b></td><td></td></tr></table>'
)
    return page("rubric", body, wm, tag="TEACHER", tagline=f"{TOTAL_POINTS} points in all")


def kschart_page(wm=False):
    cells = ""
    for i, n in enumerate(range(0, 8)):
        pass
    order = [0] + list(range(1, 8)) + [-1, -2, -3, -4, -5, -6, -7]
    for i, n in enumerate(order):
        l, a = key_of(n)
        cells += (f'<div class="ksc" data-ws="KS" data-n="{i + 1}">{staff("G", n, 5.2, f"ks{i}", W=148)}'
                  f'<div><b>{kname(l, a)}</b></div><div class="cw">{cw(n)}</div></div>')
    body = (f'<p style="margin-top:6pt">All 15 major key signatures, from no sharps or flats through 7 sharps and then 7 flats. Three of the keys have a twin that sounds the same: B major and C-flat major, F-sharp major and G-flat major, C-sharp major and D-flat major. That makes 12 different major keys on the keyboard.</p>'
            f'<div class="ksg">{cells}</div>')
    return page("kschart", body, wm, tag="REFERENCE", tagline="Treble clef")


CF = 376


def circle_svg():
    c = CF / 2
    ro, ri = c - 4, c * 0.6
    return (f'<svg class="dg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {CF} {CF}" width="{CF}pt" height="{CF}pt">'
            f'<circle cx="{c}" cy="{c}" r="{ro}" fill="none" stroke="#000" stroke-width="1.6"/><circle cx="{c}" cy="{c}" r="{ri}" fill="none" stroke="#000" stroke-width="1.6"/>'
            + "".join(f'<line x1="{c + ri * math.sin(math.radians(30 * i + 15)):.2f}" y1="{c - ri * math.cos(math.radians(30 * i + 15)):.2f}" '
                      f'x2="{c + ro * math.sin(math.radians(30 * i + 15)):.2f}" y2="{c - ro * math.cos(math.radians(30 * i + 15)):.2f}" stroke="#000" stroke-width="1"/>' for i in range(12))
            + "</svg>")


CIRCLE_SLOTS = [(0,), (1,), (2,), (3,), (4,), (5, -7), (6, -6), (7, -5), (-4,), (-3,), (-2,), (-1,)]


def circle_page(wm=False):
    labels = ""
    for i, slot in enumerate(CIRCLE_SLOTS):
        ang = math.radians(30 * i)
        r = CF / 2 * 0.8
        x, y = CF / 2 + r * math.sin(ang), CF / 2 - r * math.cos(ang)
        names = " / ".join(kn(*key_of(n)) for n in slot)
        cnts = " / ".join((("0" if n == 0 else f"{abs(n)}{SH if n > 0 else FL}")) for n in slot)
        cnts_html = " / ".join((("0" if n == 0 else f'{abs(n)}<span class="ac">{SH if n > 0 else FL}</span>')) for n in slot)
        labels += f'<div class="cfk" style="left:{x:.1f}pt;top:{y:.1f}pt" data-i="{i}"><b>{names}</b><span class="cc">{cnts_html}</span></div>'
    mid = '<div class="cfmid">Circle of fifths<small>Clockwise: up a perfect 5th<br>Counterclockwise: up a perfect 4th</small></div>'
    cf = f'<div class="cfwrap">{circle_svg()}{labels}{mid}</div>'
    # order of sharps and flats on both clefs
    sh = staff("G", 7, 5.2, "ord-s-G", W=200) + staff("F", 7, 5.2, "ord-s-F", W=200)
    fl = staff("G", -7, 5.2, "ord-f-G", W=200) + staff("F", -7, 5.2, "ord-f-F", W=200)
    body = (f'<p style="margin:4pt 0 0">Each step clockwise adds one sharp, and each step counterclockwise adds one flat. The number under each key is its sharps or flats.</p>{cf}'
            f'<div class="cols"><div class="box"><h3>Sharps, in order</h3><p><b>F C G D A E B</b><br>Father Charles Goes Down And Ends Battle</p>'
            f'<div style="display:flex;gap:6pt;flex-wrap:wrap;justify-content:center">{sh}</div>'
            f'<p style="margin-top:4pt"><b>Trick:</b> the last sharp is a half step below the key name. Last sharp D-sharp? Then the key is E major.</p></div>'
            f'<div class="box"><h3>Flats, in order</h3><p><b>B E A D G C F</b><br>Battle Ends And Down Goes Charles\'s Father</p>'
            f'<div style="display:flex;gap:6pt;flex-wrap:wrap;justify-content:center">{fl}</div>'
            f'<p style="margin-top:4pt"><b>Trick:</b> the next-to-last flat names the key. Flats B, E, A, D? The next-to-last is A, so the key is A-flat major. One flat is always F major.</p></div></div>')
    return page("circle", body, wm, tag="REFERENCE", tagline="Fifths and order")


def overview_page(wm=False):
    rows = ""
    insts = {"C": "Flute, oboe, bassoon, trombone, euphonium (bass clef), tuba, mallet percussion",
             "Bb": "Clarinet, bass clarinet, trumpet, tenor sax, euphonium and baritone horn (treble clef)",
             "Eb": "Alto sax, baritone sax, alto clarinet", "F": "Horn in F"}
    for g in GROUPS:
        rows += (f'<tr><td><b>{GROUP_NAME[g]}</b></td><td>{insts[g]}</td><td>{GROUP_SOUND[g].replace("sounds ", "").capitalize()}</td>'
                 f'<td>{GROUP_UP[g].capitalize()}</td><td>{GROUP_SHIFT[g].capitalize()}</td></tr>')
    ex = ""
    cl, ca = key_of(-3)           # concert E-flat major
    for g, lab in (("C", "Flute"), ("Bb", "Clarinet"), ("Eb", "Alto sax"), ("F", "Horn in F")):
        wl, wa, wc, enh = written_key(g, cl, ca)
        ex += (f'<div class="ex" data-ws="EX" data-g="{g}">{staff("G", wc, 4.4, f"ex-{g}", W=112)}<b>{lab}</b>reads {kname(wl, wa)}<br>{cw(wc)}</div>')
    il = "".join(f'<p class="il" data-ws="IL"><b>{nm}</b> ({GSHORT[g_]}): {txt}</p>' for nm, (g_, _d, txt) in INSTR.items())
    body = (f'<p style="margin:4pt 0">A transposing instrument sounds a different pitch from the one written. A band director wants the whole band to sound in the same concert key, so each section reads its own written key. '
            f'<b>Written key = concert key + the instrument\'s interval.</b></p>'
            f'<table><tr><th style="width:80pt">Group</th><th>Instruments</th><th style="width:88pt">The sound</th><th style="width:64pt">Written key</th><th style="width:100pt">Signature shortcut</th></tr>{rows}</table>'
            f'<h2>One concert key, four written keys</h2><p>The band plays in concert E-flat major (3 flats). This is what each section reads.</p><div class="exr">{ex}</div>'
            f'<div class="box"><h3>Worked example and the 7-accidental limit</h3><p>Concert A-flat major, alto sax: A-flat up a major 6th is F major. Shortcut: 4 flats, add 3 sharps, leaves 1 flat. If a written key would need 8 or more sharps or flats, use the enharmonic key instead. Concert F-sharp major for a B-flat clarinet would be G-sharp major, so write A-flat major with 4 flats. Charts mark these keys with an asterisk (*).</p></div>'
            f'<h2>Instrument by instrument</h2><div style="columns:2;column-gap:14pt;margin-top:2pt">{il}</div>'
)
    return page("overview", body, wm, tag="REFERENCE", tagline="Concert vs written")


def tc_row(g, i, n):
    l, a = key_of(n)
    if g == "C":
        return (f'<tr data-ws="TC-C" data-n="{i}"><td class="k"><b>{kname(l, a)}</b><br><span class="cw">{cw(n)}</span></td>'
                f'<td>{staff("G", n, 4.4, f"tcC-G{i}", W=118)}</td><td>{staff("F", n, 4.4, f"tcC-F{i}", W=118)}</td></tr>')
    wl, wa, wc, enh = written_key(g, l, a)
    star = "*" if enh else ""
    return (f'<tr data-ws="TC-{g}" data-n="{i}"><td class="k"><b>{kname(l, a)}</b><br><span class="cw">{cw(n)}</span></td><td>{staff("G", n, 4.4, f"tc{g}-c{i}", W=118)}</td>'
            f'<td class="arr">→</td><td class="k"><b>{kname(wl, wa)}{star}</b><br><span class="cw">{cw(wc)}</span></td><td>{staff("G", wc, 4.4, f"tc{g}-w{i}", W=118)}</td></tr>')


def tc_page(g, wm=False):
    nums = [n for n in (0, 1, 2, 3, 4, 5, 6, -5, -4, -3, -2, -1)]
    rows = "".join(tc_row(g, i + 1, n) for i, n in enumerate(nums))
    key = "tc" + g
    if g == "C":
        head = (f'<tr><th>Concert key</th><th>Treble clef</th><th>Bass clef</th></tr>')
        intro = (f'<p style="margin:4pt 0">C instruments read the same key as the concert key. Flute, oboe and mallet percussion read treble clef. Trombone, bassoon, euphonium and tuba usually read bass clef, so the sharps and flats sit on different lines and spaces.</p>')
        foot = '<p class="small">Treble and bass clef signatures show the same key. Notice that the pattern of sharps and flats shifts in bass clef.</p>'
    else:
        head = ('<tr><th>Concert key</th><th>Concert signature</th><th style="width:26pt"></th><th>Written key</th><th>Written signature</th></tr>')
        who = {"Bb": "Clarinet, bass clarinet, trumpet, tenor sax and treble-clef euphonium or baritone horn", "Eb": "Alto sax, baritone sax and alto clarinet",
               "F": "Horn in F"}[g]
        intro = (f'<p style="margin:4pt 0"><b>{who}.</b> These instruments {GROUP_SOUND[g].replace('sounds ','sound ',1)}, so the written key is {GROUP_UP[g]} from the concert key. Shortcut: {GROUP_SHIFT[g]}.</p>')
        foot = ('<p class="small">* This key would need more than 7 sharps or flats, so the enharmonic key is written instead. The two keys sound the same.</p>'
                if any(written_key(g, *key_of(n))[3] for n in nums) else
                '<p class="small">Every written key on this page has 7 or fewer sharps or flats, so no enharmonic substitutions are needed.</p>')
    body = f'{intro}<table class="tc" style="margin:2pt 0">{head}{rows}</table>{foot}'
    return page(key, body, wm, tag="CHART", tagline="Concert to written")


# ---------- worksheets
def it_sig(ws, i, n, clef):
    return (f'<div class="it" data-ws="{ws}" data-n="{i}"><span class="nm">{i}</span>{staff(clef, n, 5.6, f"{ws}-{i}", W=206)}'
            f'<div class="al"><span>Key:</span><span class="ln w"></span><span>major</span><span>Sharps/flats:</span><span class="ln" style="width:30pt"></span></div></div>')


def w1_page(wm=False):
    items = "".join(it_sig("W1", i + 1, n, "G") for i, n in enumerate(W1_SIGS))
    body = (f'<p class="inst"><b>Directions:</b> Each staff shows a major key signature. Write the name of the key and how many sharps or flats it has. Use the key signature chart ({pg("kschart")}) if you need help.</p>'
            f'<div class="grid">{items}</div>')
    return sheet_page("w1", body, wm)


def it_sig3(ws, i, n, clef):
    return (f'<div class="it" data-ws="{ws}" data-n="{i}" style="padding:4pt 6pt"><span class="nm">{i}</span>{staff(clef, n, 5.0, f"{ws}-{i}", W=140)}'
            f'<div class="al" style="flex-wrap:wrap;gap:2pt 6pt;margin-top:1pt"><span>Key:</span><span class="ln" style="width:52pt"></span><span>major</span><span>Sharps/flats:</span><span class="ln" style="width:22pt"></span></div></div>')


def w2_page(wm=False):
    items = "".join(it_sig3("W2", i + 1, n, "F" if i % 2 else "G") for i, n in enumerate(W2_SIGS))
    body = (f'<p class="inst"><b>Directions:</b> Name each major key. Some staves use treble clef and some use bass clef. Also write how many sharps or flats each key has.</p>'
            f'<div class="grid three">{items}</div>'
            f'<div class="box" style="margin:0 0 6pt"><h3>Challenge</h3><p>Three pairs of major keys on this page sound the same. Write one pair here: <span style="display:inline-block;border-bottom:1pt solid #000;width:220pt">&nbsp;</span></p></div>')
    return sheet_page("w2", body, wm)


def it_write_sig(ws, i, n, clef, W=206):
    return (f'<div class="it" data-ws="{ws}" data-n="{i}"><span class="nm">{i}</span><p class="pr">{nm_html(n)} <span class="small">({"treble" if clef == "G" else "bass"} clef)</span></p>'
            f'{staff(clef, 0, 5.6, f"{ws}-{i}", W=W)}</div>')


def w3_page(wm=False):
    items = "".join(it_write_sig("W3", i + 1, n, "G" if i % 2 == 0 else "F") for i, n in enumerate(W3_SIGS))
    body = (f'<p class="inst"><b>Directions:</b> Write the key signature for each major key. Draw the sharps or flats in the correct order and on the correct lines and spaces. Check the order on page {P["circle"]}.</p>'
            f'<div class="grid">{items}</div>')
    return sheet_page("w3", body, wm)


def scale_item(ws, i, n, filled, with_acc):
    l, a = key_of(n)
    bars = scale_bars(l, a, with_acc=with_acc) if filled else None
    sg = 0 if with_acc else n
    st = staff("G", sg, 6.0, f"{ws}-{i}", W=500, ts=True, bars=bars, nblank=0 if filled else 2)
    return (f'<div class="it" data-ws="{ws}" data-n="{i}"><span class="nm">{i}</span><p class="pr">Write the <b>{kname(l, a)}</b> scale, one octave up, in quarter notes.</p>{st}</div>')


def w4_page(wm=False):
    items = "".join(scale_item("W4", i + 1, n, False, False) for i, n in enumerate(W4_SIGS))
    body = (f'<p class="inst"><b>Directions:</b> The key signature is printed for you. Write each major scale, starting on its tonic and going up one octave. Use quarter notes, and put stems on the correct side of each note. Say the half steps out loud: they fall between steps 3 and 4 and steps 7 and 8.</p>'
            f'<div class="grid one">{items}</div>')
    return sheet_page("w4", body, wm)


def w5_page(wm=False):
    items = "".join(scale_item("W5", i + 1, n, False, True) for i, n in enumerate(W5_SIGS))
    body = (f'<p class="inst"><b>Directions:</b> There is no key signature on these staves. Write each major scale one octave up in quarter notes, and put a sharp or flat sign in front of every note that needs one. The scale is the same one you would write with a key signature.</p>'
            f'<div class="grid one">{items}</div>')
    return sheet_page("w5", body, wm)


def trow_s(ws, i, q, extra_cols=2, w=None):
    return f'<tr class="trow" data-ws="{ws}" data-n="{i}"><td class="n">{i}</td>{q}<td class="bl"></td><td class="bl"></td></tr>'


def conc_page(key, g, wm=False):
    ws = "W" + key[1:]
    rows = "".join(f'<tr class="trow" data-ws="{ws}" data-n="{i + 1}"><td class="n">{i + 1}</td><td class="q">{nm_html(n)}</td><td class="bl"></td><td class="bl"></td></tr>' for i, n in enumerate(SHEET_ORDER[g]))
    who = {"Bb": "clarinet, trumpet or tenor sax", "Eb": "alto sax or baritone sax", "F": "horn in F"}[g]
    body = (f'<p class="inst"><b>Directions:</b> The band is playing in the concert key shown. Name the written key for a player on {who}, and write how many sharps or flats that key has. '
            f'Use the chart on {pg("tc" + g)} to check your work after you finish. If a written key would need more than 7 sharps or flats, write its enharmonic key and put an asterisk (*) after it.</p>'
            f'<div class="box" style="margin-top:6pt"><h3>Remember</h3><p>{GROUP_NAME[g]} {GROUP_SOUND[g].replace('sounds ','sound ',1)}. The written key is {GROUP_UP[g]}.</p></div>'
            f'<table style="margin-top:4pt"><tr><th style="width:28pt">#</th><th>Concert key</th><th>Written key</th><th style="width:130pt">Sharps or flats</th></tr>{rows}</table>'
            f'<div class="box"><h3>Think about it</h3><p>Which concert key gave you the written key with the most sharps or flats? Why does that happen?</p><div class="nd"><span class="ln"></span></div><div class="nd"><span class="ln"></span></div></div>')
    return sheet_page(key, body, wm)


def w9_page(wm=False):
    rows = "".join(f'<tr class="trow tall" data-ws="W9" data-n="{i + 1}"><td class="n">{i + 1}</td><td class="q">{ins}</td><td class="q">{nm_html(n)}</td><td class="bl"></td><td class="bl"></td></tr>'
                   for i, (ins, n) in enumerate(W9_ITEMS))
    body = (f'<p class="inst"><b>Directions:</b> Each player reads a different part. Given the concert key, write the key that player reads and how many sharps or flats it has. Remember: a flute is a C instrument, so it reads the same key as the band. '
            f'If a written key would need more than 7 sharps or flats, write its enharmonic key and add an asterisk (*).</p>'
            f'<table style="margin-top:6pt"><tr><th style="width:28pt">#</th><th style="width:110pt">Instrument</th><th>Concert key</th><th>Written key</th><th style="width:100pt">Sharps or flats</th></tr>{rows}</table>'
            f'<div class="box"><h3>Instrument groups</h3><p><b>C:</b> flute, oboe, bassoon, trombone, tuba. <b>B-flat:</b> clarinet, bass clarinet, trumpet, tenor sax. <b>E-flat:</b> alto sax, baritone sax, alto clarinet. <b>F:</b> horn.</p></div>')
    return sheet_page("w9", body, wm)


def w10_page(wm=False):
    rows = "".join(f'<tr class="trow tall" data-ws="W10" data-n="{i + 1}"><td class="n">{i + 1}</td><td class="q">{ins}</td><td class="q">{nm_html(n)}</td><td class="bl"></td><td class="bl"></td></tr>'
                   for i, (ins, n) in enumerate(W10_ITEMS))
    body = (f'<p class="inst"><b>Directions:</b> Now work backward. Each player sees the written key shown. Name the concert key the band hears, and write its sharps or flats. To go from written to concert, move down by the same interval: a major 2nd for B-flat instruments, a major 6th for E-flat instruments and a perfect 5th for horn in F.</p>'
            f'<table style="margin-top:6pt"><tr><th style="width:28pt">#</th><th style="width:110pt">Instrument</th><th>Written key</th><th>Concert key</th><th style="width:100pt">Sharps or flats</th></tr>{rows}</table>'
            f'<div class="box"><h3>Check yourself</h3><p>Pick one answer. Transpose your concert key up by the instrument\'s interval. Do you land back on the written key?</p><div class="nd"><span class="ln"></span></div></div>')
    return sheet_page("w10", body, wm)


W11_INSTR = [("Bb", "Clarinet, trumpet", "B-flat"), ("Eb", "Alto sax", "E-flat"), ("F", "Horn in F", "F")]


def w11_cell(filled, n, g, i, j):
    l, a = key_of(n)
    wl, wa, wc, enh = written_key(g, l, a)
    if filled:
        return (f'<div class="ak cell" data-ws="W11" data-n="{i}-{j}">{staff("G", wc, 4.2, f"W11-{i}-{j}", W=112)}'
                f'<div class="al"><span class="ans">{kname(wl, wa)}{"*" if enh else ""}</span></div></div>')
    return (f'<div class="it cell" data-ws="W11" data-n="{i}-{j}">{staff("G", 0, 4.2, f"W11-{i}-{j}", W=112)}<div class="al"><span>Key:</span><span class="ln" style="width:80pt"></span></div></div>')


def w11_body(filled):
    for n in W11_KEYS:
        for g, _, _ in W11_INSTR:
            written_key(g, *key_of(n))
    head = '<div style="display:grid;grid-template-columns:86pt repeat(3,minmax(0,1fr));gap:8pt;font-family:Oswald;font-weight:700;text-transform:uppercase;font-size:11pt;text-align:center;margin-top:6pt"><div>Concert key</div>' + "".join(
        f'<div>{lab}<div style="font-weight:300;text-transform:none;font-size:9.6pt">{who}</div></div>' for _, who, lab in W11_INSTR) + "</div>"
    rows = ""
    for i, n in enumerate(W11_KEYS):
        l, a = key_of(n)
        cells = "".join(w11_cell(filled, n, g, i + 1, j + 1) for j, (g, _, _) in enumerate(W11_INSTR))
        rows += (f'<div style="display:grid;grid-template-columns:86pt repeat(3,minmax(0,1fr));gap:8pt;align-items:stretch">'
                 f'<div class="{"ak" if filled else "it"} cell" data-ws="W11C" data-n="{i + 1}" style="align-items:center"><b style="font-size:12.5pt">{kname(l, a)}</b>'
                 f'<span style="font-size:9.4pt">{cw(n)}</span></div>{cells}</div>')
    return head, f'<div style="flex:1;display:grid;grid-auto-rows:1fr;gap:7pt;padding:6pt 0 8pt">{rows}</div>'


def w11_page(wm=False):
    head, rows = w11_body(False)
    body = (f'<p class="inst"><b>Directions:</b> One concert key is on each row. For each section, write the name of the written key and draw its key signature on the treble staff. The flute, oboe and other C instruments read the concert key, so they are not shown.</p>{head}{rows}')
    return sheet_page("w11", body, wm)


def quiz_page(wm=False):
    A = "".join(f'<div class="it" data-ws="QA" data-n="{i + 1}" style="padding:4pt 4pt"><span class="nm" style="position:static;display:block;line-height:1;margin:0 0 6pt 1pt">{i + 1}</span>{staff("G", n, 5.0, f"QA-{i}", W=118)}'
                f'<div class="al"><span class="ln" style="width:78pt"></span><span>major</span></div></div>' for i, n in enumerate(Q_A))
    Brows = "".join(f'<tr class="trow" data-ws="QB" data-n="{i + 1}"><td class="n">{i + 1}</td><td class="q">{ins}</td><td class="q">{nm_html(n)}</td><td class="bl"></td></tr>' for i, (ins, n) in enumerate(Q_B))
    Crows = "".join(f'<tr class="trow" data-ws="QC" data-n="{i + 1}"><td class="n">{i + 1}</td><td class="q">{ins}</td><td class="q">{nm_html(n)}</td><td class="bl"></td></tr>' for i, (ins, n) in enumerate(Q_C))
    dl, da = key_of(Q_D[1])
    el, ea = key_of(Q_E)
    body = (f'<h2 style="margin-top:6pt">A. Name the key (4 points)</h2><div style="display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:8pt">{A}</div>'
            f'<div class="cols"><div style="flex:1"><h2>B. Concert to written (4 points)</h2><table><tr><th style="width:22pt">#</th><th>Instrument</th><th>Concert</th><th>Written</th></tr>{Brows}</table></div>'
            f'<div style="flex:1"><h2>C. Written to concert (2 points)</h2><table><tr><th style="width:22pt">#</th><th>Instrument</th><th>Written</th><th>Concert</th></tr>{Crows}</table>'
            f'<h2>D. Write the key signature (2 points)</h2><p style="margin:0 0 2pt;font-size:10pt">The band plays in concert {kname(dl, da)}. Name the key an {Q_D[0]} reads, and draw its signature.</p>'
            f'<div class="it" data-ws="QD" data-n="1" style="padding:3pt 4pt">{staff("G", 0, 5.0, "QD-1", W=210)}<div class="al"><span>Written key:</span><span class="ln w"></span></div></div></div></div>'
            f'<h2>E. Write the scale (8 points)</h2><div class="it" data-ws="QE" data-n="1" style="padding:5pt 8pt"><p class="pr">Write the <b>{kname(el, ea)}</b> scale, one octave up, in quarter notes. Add accidentals: there is no key signature.</p>'
            f'{staff("G", 0, 5.6, "QE-1", W=500, ts=True, nblank=2)}</div>')
    return sheet_page("quiz", f'<div style="flex:1;display:flex;flex-direction:column;justify-content:space-evenly">{body}</div>', wm)


# ---------- answer keys
def ak_sig_cell(ws, i, n, clef, S=4.2, W=150):
    l, a = key_of(n)
    return (f'<div class="ak" data-ws="{ws}" data-n="{i}" style="padding:3pt 6pt"><span class="nm" style="position:static;display:block;line-height:1;margin:0 0 6pt 1pt">{i}</span>{staff(clef, n, S, f"{ws}k-{i}", W=W)}'
            f'<div class="al" style="margin-top:1pt;gap:6pt"><span class="ans">{kname(l, a)}</span><span class="cnt small">{cw(n)}</span></div></div>')


def ak_sig_cell_h(ws, i, n, clef):
    l, a = key_of(n)
    return (f'<div class="ak" data-ws="{ws}" data-n="{i}" style="padding:0 6pt;flex-direction:row;align-items:center;justify-content:flex-start;gap:5pt">'
            f'<b style="font-family:Oswald;font-size:10pt;width:14pt;flex:none">{i}</b>{staff(clef, n, 3.2, f"{ws}k-{i}", W=92)}'
            f'<div style="line-height:1.15"><span class="ans" style="font-size:10pt">{kname(l, a)}</span><br><span class="cnt small">{cw(n)}</span></div></div>')


def a12_page(wm=False):
    g1 = "".join(ak_sig_cell_h("W1", i + 1, n, "G") for i, n in enumerate(W1_SIGS))
    g2 = "".join(ak_sig_cell_h("W2", i + 1, n, "F" if i % 2 else "G") for i, n in enumerate(W2_SIGS))
    body = (f'<h2 style="margin:4pt 0 2pt">Worksheet 1 ({WS_POINTS["w1"]} points)</h2><div class="grid three" style="padding:2pt 0 2pt;gap:4pt 8pt">{g1}</div>'
            f'<h2 style="margin:2pt 0 2pt">Worksheet 2 ({WS_POINTS["w2"]} points) <span style="font-family:&quot;Source Sans 3&quot;;text-transform:none;font-weight:400;letter-spacing:0;font-size:9pt">Challenge: any one pair of {kn(6, 0)} and {kn(0, -1)}, {kn(3, 1)} and {kn(4, -1)}, or {kn(0, 1)} and {kn(1, -1)} (major keys).</span></h2><div class="grid three" style="padding:2pt 0 9pt;gap:4pt 8pt">{g2}</div>')
    return ak_page("a12", body, wm)


def a3_page(wm=False):
    items = ""
    for i, n in enumerate(W3_SIGS):
        clef = "G" if i % 2 == 0 else "F"
        l, a = key_of(n)
        items += (f'<div class="ak" data-ws="W3" data-n="{i + 1}" data-clef="{clef}"><span class="nm">{i + 1}</span>{staff(clef, n, 4.3, f"W3k-{i}", W=206)}'
                  f'<div class="al"><span class="ans">{kname(l, a)}</span><span class="cnt small">{cw(n)}, {"treble" if clef == "G" else "bass"} clef</span></div></div>')
    body = (f'<p class="inst"><b>Worksheet 3</b> ({WS_POINTS["w3"]} points). Accept each sharp or flat in the right order and on the right line or space. '
            f'Sharps go F, C, G, D, A, E, B and flats go B, E, A, D, G, C, F, as on page {P["circle"]}.</p><div class="grid">{items}</div>')
    return ak_page("a3", body, wm)


def scale_ak(ws, i, n, with_acc):
    l, a = key_of(n)
    st = staff("G", 0 if with_acc else n, 3.8, f"{ws}k-{i}", W=250, ts=True, bars=scale_bars(l, a, with_acc=with_acc))
    names = " ".join(LET[sl] + {1: SH, -1: FL, 0: ""}[sa] for sl, sa in scale_of(l, a)) + " " + LET[l] + {1: SH, -1: FL, 0: ""}[a]
    names = names.replace(SH, f'<span class="ac">{SH}</span>').replace(FL, f'<span class="ac">{FL}</span>')
    return (f'<div class="ak" data-ws="{ws}" data-n="{i}"><span class="nm">{i}</span><p class="pr" style="margin:0"><b>{kname(l, a)}</b></p>{st}<div class="sn">{names}</div></div>')


def a45_page(wm=False):
    w4 = "".join(scale_ak("W4", i + 1, n, False) for i, n in enumerate(W4_SIGS))
    w5 = "".join(scale_ak("W5", i + 1, n, True) for i, n in enumerate(W5_SIGS))
    body = (f'<h2 style="margin:4pt 0 0">Worksheet 4: key signature given ({WS_POINTS["w4"]} points, 2 per scale)</h2><div class="grid" style="padding:3pt 0 3pt;gap:5pt 10pt">{w4}</div>'
            f'<h2 style="margin:2pt 0 0">Worksheet 5: accidentals written on the notes ({WS_POINTS["w5"]} points, 2 per scale)</h2><div class="grid" style="padding:3pt 0 9pt;gap:5pt 10pt">{w5}</div>')
    return ak_page("a45", body, wm)


def conc_rows(g, ws):
    rows = ""
    for i, n in enumerate(SHEET_ORDER[g]):
        l, a = key_of(n)
        wl, wa, wc, enh = written_key(g, l, a)
        rows += (f'<tr class="trow akr two" data-ws="{ws}" data-n="{i + 1}"><td class="n">{i + 1}</td><td class="c">{kname(l, a)}</td>'
                 f'<td class="bl"><span class="ans">{kname(wl, wa)}{"*" if enh else ""}</span><br><span class="cnt small">{cw(wc)}</span></td></tr>')
    return rows


def a678_page(wm=False):
    cols = ""
    for g, ws in (("Bb", "W6"), ("Eb", "W7"), ("F", "W8")):
        cols += (f'<div style="flex:1;min-width:0"><h2 style="margin:6pt 0 2pt;font-size:11.5pt">{ws.replace("W", "Worksheet ")}</h2><p class="small" style="margin:0 0 2pt">{GROUP_NAME[g]}, 12 points</p>'
                 f'<table class="rub" style="margin:0"><tr><th style="width:20pt">#</th><th>Concert</th><th>Written</th></tr>{conc_rows(g, ws)}</table></div>')
    notes = []
    for g in ("Bb", "Eb", "F"):
        for n in SHEET_ORDER[g]:
            l, a = key_of(n)
            wl, wa, wc, enh = written_key(g, l, a)
            if enh:
                dl, da = transpose(l, a, *UP[g])
                notes.append(f"<li>Concert {wname(l, a)}, {GSHORT[g]} instruments: {wname(dl, da)} needs {abs(sig_of_direct(dl, da))} sharps, so write {wname(wl, wa)}.</li>")
    body = (f'<div class="cols" style="gap:9pt;align-items:flex-start">{cols}</div>'
            f'<div class="box"><h3>Asterisks (*)</h3><ul>{"".join(notes)}</ul><p>A student who writes a key with 8 or more sharps has not finished the problem.</p></div>'
            f'<div class="box"><h3>Check method</h3><p>On the circle of fifths ({pg("circle")}), B-flat instruments move the key 2 steps clockwise, E-flat instruments move it 3 steps and horn in F moves it 1 step. If the result passes 7 sharps, use the flat key with the same sound.</p></div>')
    return ak_page("a678", body, wm)


def sig_of_direct(l, a):
    """Number of sharps or flats a key would need even when it passes 7 (counted by spelling its scale)."""
    return sum(x for _, x in scale_of(l, a)) if abs(a) <= 1 or True else 0


def a910_page(wm=False):
    def tbl(ws, items, mode):
        rows = ""
        for i, (ins, n) in enumerate(items):
            l, a = key_of(n)
            g = instr_group(ins)
            if mode == "cw":
                wl, wa, wc, enh = written_key(g, l, a)
                rows += (f'<tr class="trow akr" data-ws="{ws}" data-n="{i + 1}"><td class="n">{i + 1}</td><td>{ins}</td><td class="c">{kname(l, a)}</td>'
                         f'<td class="bl ans">{kname(wl, wa)}{"*" if enh else ""}</td><td class="bl cnt">{cw(wc)}</td></tr>')
            else:
                cl, ca, cc = concert_key(g, l, a)
                rows += (f'<tr class="trow akr" data-ws="{ws}" data-n="{i + 1}"><td class="n">{i + 1}</td><td>{ins}</td><td class="c">{kname(l, a)}</td>'
                         f'<td class="bl ans">{kname(cl, ca)}</td><td class="bl cnt">{cw(cc)}</td></tr>')
        h = ("Concert", "Written") if mode == "cw" else ("Written", "Concert")
        return (f'<table class="rub" style="margin:0"><tr><th style="width:20pt">#</th><th style="width:92pt">Instrument</th><th>{h[0]}</th><th>{h[1]}</th><th>Sharps or flats</th></tr>{rows}</table>')
    note = []
    for ins, n in W9_ITEMS:
        l, a = key_of(n)
        wl, wa, wc, enh = written_key(instr_group(ins), l, a)
        if enh:
            dl, da = transpose(l, a, *UP[instr_group(ins)])
            note.append(f"Item {W9_ITEMS.index((ins, n)) + 1}: {wname(dl, da)} major would need {abs(sig_of_direct(dl, da))} sharps, so the enharmonic {wname(wl, wa)} major is the answer.")
    body = (f'<h2 style="margin:6pt 0 2pt">Worksheet 9: concert to written ({WS_POINTS["w9"]} points)</h2>{tbl("W9", W9_ITEMS, "cw")}'
            f'<p class="small" style="margin:2pt 0 0">* {" ".join(note)}</p>'
            f'<h2 style="margin:10pt 0 2pt">Worksheet 10: written to concert ({WS_POINTS["w10"]} points)</h2>{tbl("W10", W10_ITEMS, "wc")}'
            f'<p class="small" style="margin:2pt 0 0">Concert key = written key moved down by the instrument\'s interval. The same keys, moved up again, return to the written key.</p>')
    return ak_page("a910", f'<div style="flex:1">{body}</div>', wm)


def a11_page(wm=False):
    head, rows = w11_body(True)
    body = (f'<p class="inst"><b>Worksheet 11</b> ({WS_POINTS["w11"]} points). Each cell earns 1 point when the key name and the key signature are both right. C instruments (not shown) read the concert key.</p>{head}{rows}')
    return ak_page("a11", body, wm)


def aq_page(wm=False):
    A = "".join(ak_sig_cell("QA", i + 1, n, "G", 4.2, 118) for i, n in enumerate(Q_A))
    def qrows(ws, items, mode):
        out = ""
        for i, (ins, n) in enumerate(items):
            l, a = key_of(n)
            g = instr_group(ins)
            if mode == "cw":
                wl, wa, wc, enh = written_key(g, l, a)
                out += (f'<tr class="trow akr" data-ws="{ws}" data-n="{i + 1}"><td class="n">{i + 1}</td><td>{ins}</td><td class="c">{kname(l, a)}</td>'
                        f'<td class="bl ans">{kname(wl, wa)}{"*" if enh else ""}</td><td class="bl cnt">{cw(wc)}</td></tr>')
            else:
                cl, ca, cc = concert_key(g, l, a)
                out += (f'<tr class="trow akr" data-ws="{ws}" data-n="{i + 1}"><td class="n">{i + 1}</td><td>{ins}</td><td class="c">{kname(l, a)}</td>'
                        f'<td class="bl ans">{kname(cl, ca)}</td><td class="bl cnt">{cw(cc)}</td></tr>')
        return out
    enh_note = ""
    for ins, n in Q_B:
        l, a = key_of(n)
        wl, wa, wc, enh = written_key(instr_group(ins), l, a)
        if enh:
            dl, da = transpose(l, a, *UP[instr_group(ins)])
            enh_note = f"* Item B1: {wname(dl, da)} major would need {abs(sig_of_direct(dl, da))} sharps, so the enharmonic {wname(wl, wa)} major is the answer."
    dl, da = key_of(Q_D[1])
    wl, wa, wc, enh = written_key(instr_group(Q_D[0]), dl, da)
    el, ea = key_of(Q_E)
    D = (f'<div class="ak" data-ws="QD" data-n="1" style="padding:3pt 6pt">{staff("G", wc, 5.0, "QDk-1", W=210)}'
         f'<div class="al"><span class="ans">{kname(wl, wa)}</span><span class="cnt small">{cw(wc)}</span></div></div>')
    names = " ".join(LET[sl] + {1: SH, -1: FL, 0: ""}[sa] for sl, sa in scale_of(el, ea)) + " " + LET[el] + {1: SH, -1: FL, 0: ""}[ea]
    names = names.replace(SH, f'<span class="ac">{SH}</span>').replace(FL, f'<span class="ac">{FL}</span>')
    E = (f'<div class="ak" data-ws="QE" data-n="1" style="padding:4pt 8pt">{staff("G", 0, 5.6, "QEk-1", W=500, ts=True, bars=scale_bars(el, ea, with_acc=True))}<div class="sn">{names}</div></div>')
    body = (f'<h2 style="margin:6pt 0 2pt">A. Name the key (4 points)</h2><div style="display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:8pt">{A}</div>'
            f'<div class="cols"><div style="flex:1"><h2>B. Concert to written (4 points)</h2><table class="rub" style="margin:0"><tr><th style="width:20pt">#</th><th>Instrument</th><th>Concert</th><th>Written</th><th>Count</th></tr>{qrows("QB", Q_B, "cw")}</table>'
            f'<p class="small" style="margin:2pt 0 0">{enh_note}</p></div>'
            f'<div style="flex:1"><h2>C. Written to concert (2 points)</h2><table class="rub" style="margin:0"><tr><th style="width:20pt">#</th><th>Instrument</th><th>Written</th><th>Concert</th><th>Count</th></tr>{qrows("QC", Q_C, "wc")}</table>'
            f'<h2>D. Write the key signature (2 points)</h2>{D}</div></div>'
            f'<h2>E. Write the scale (8 points)</h2>{E}'
            f'<p class="small" style="margin-top:4pt">Total {WS_POINTS["quiz"]} points. Section D: 1 point for the key name and 1 for the key signature. Section E: 1 point for each note, including its accidental.</p>')
    return ak_page("aq", f'<div style="flex:1;display:flex;flex-direction:column;justify-content:space-evenly">{body}</div>', wm)


def terms_page(wm=False):
    body = (f'{doc_head("Terms of Use", "Thank you for your purchase!")}'
            f'<p>© {YEAR} {STORE}. {BRAND} by {STORE}. All rights reserved. This purchase gives <b>one teacher</b> a license to use this resource with their own students.</p>'
            f'<h2>You may</h2><ul><li>Print and copy pages for your own classroom and students, year after year.</li>'
            f'<li>Share pages with your own students through a password-protected class site or learning platform.</li>'
            f'<li>Use the pages with your own students when you have a substitute teacher.</li></ul>'
            f'<h2>You may not</h2><ul><li>Share, email or copy this resource for other teachers, a whole school or a district. Additional licenses are available on Teachers Pay Teachers.</li>'
            f'<li>Post any part of it on a public website, shared drive or social media.</li>'
            f'<li>Sell, give away or claim any part of it as your own, or edit it into a new product.</li></ul>'
            f'<h2>Questions?</h2><p>Please use the Q&amp;A tab on the {BRAND} by {STORE} store on Teachers Pay Teachers. If something looks wrong, let me know there and I will fix it.</p>'
            f'<h2>Credits</h2><ul>'
            f'<li>The worksheets, charts, answer keys and all music notation are original work, {BRAND} by {STORE}.</li>'
            f'<li>The cover clarinet illustration is made with AI tools. The notation, charts, circle of fifths and text are drawn in code.</li>'
            f'<li>Music notation font: Bravura © Steinberg Media Technologies GmbH, SIL Open Font License 1.1.</li>'
            f'<li>Text fonts: Oswald (The Oswald Project Authors) and Source Sans 3 (Adobe), SIL Open Font License 1.1.</li></ul>'
            f'<h2>Printing tips</h2><ul><li>Print the student pages single-sided in black and white. Staff lines and notes print clearly without color.</li>'
            f'<li>Keep the answer keys for yourself. Copy only the student pages for your class, so students never see the answers.</li></ul>'
            f'<h2>What is in this file ({TOTAL_PAGES} pages)</h2><p>Page 1 cover, page {P["teach"]} teacher notes, page {P["pacing"]} pacing plan, page {P["vocab"]} vocabulary, page {P["rubric"]} rubric and score sheet, '
            f'pages {P["kschart"]}–{P["tcF"]} charts and references, pages {P["w1"]}–{P["quiz"]} worksheets 1–11 and the quiz, pages {P["a12"]}–{P["aq"]} answer keys and page {P["terms"]} these terms.</p>'
            f'<p class="small">{DISCLOSURE}</p>')
    return page("terms", body, wm, tag="TERMS", tagline="Please read")


def doc_head(h1, sub):
    return f'<div class="rule" style="margin-top:8pt"><h1>{h1}</h1><div style="font-family:Oswald;font-weight:300;font-size:13pt">{sub}</div></div>'


FUNCS = {"teach": teach_page, "pacing": pacing_page, "vocab": vocab_page, "rubric": rubric_page, "kschart": kschart_page, "circle": circle_page,
         "overview": overview_page, "tcC": lambda wm: tc_page("C", wm), "tcBb": lambda wm: tc_page("Bb", wm), "tcEb": lambda wm: tc_page("Eb", wm),
         "tcF": lambda wm: tc_page("F", wm), "w1": w1_page, "w2": w2_page, "w3": w3_page, "w4": w4_page, "w5": w5_page,
         "w6": lambda wm: conc_page("w6", "Bb", wm), "w7": lambda wm: conc_page("w7", "Eb", wm), "w8": lambda wm: conc_page("w8", "F", wm),
         "w9": w9_page, "w10": w10_page, "w11": w11_page, "quiz": quiz_page, "a12": a12_page, "a3": a3_page, "a45": a45_page, "a678": a678_page,
         "a910": a910_page, "a11": a11_page, "aq": aq_page, "terms": terms_page}


def full_pages():
    XREFS.clear()
    out = [cover_page()] + [FUNCS[k](False) for k in ORDER[1:]]
    assert len(out) == TOTAL_PAGES
    return out


PREVIEW_KEYS = ["circle", "tcBb", "w4", "a45"]


def preview_pages():
    return [FUNCS[k](True) for k in PREVIEW_KEYS]


# ================================================================== square images
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
        f'<div style="height:460px;display:flex;align-items:center"><img src="../art/hero.png" alt="" style="display:block;height:460px;width:auto"></div>'
        f'<div><div class="hd" style="font-size:64px">Band worksheets</div><div class="hd" style="font-size:112px">Key Signatures</div>'
        f'<div class="sub" style="font-size:27px;margin-top:12px">Scales and concert pitch transposition for C, B-flat, E-flat and F instruments</div></div>'
        f'</div><div class="band">Grades 6–12 <em>·</em> 11 worksheets <em>·</em> {TOTAL_PAGES} pages</div></div>')


def swm_over(size=230):
    return f'<div class="swm" style="font-size:{size}px">PREVIEW</div>'


def shot(src, w):
    return f'<div class="shot" style="width:{w}px"><img src="{src}"></div>'


def pill_row(items):
    return '<div style="display:flex;gap:18px">' + "".join(f'<div class="pill">{t}</div>' for t in items) + "</div>"


def trio(imgs, caps, w=290):
    return "".join(
        f'<div style="width:{w}px;display:flex;flex-direction:column;align-items:center">{shot(imgs[i], w)}'
        f'<div class="lbl" style="font-size:22px;margin-top:20px">{caps[i][0]}</div>'
        f'<div style="font-family:Oswald;font-weight:300;font-size:20px;line-height:1.25;text-align:center;margin-top:8px;width:{w - 20}px">{caps[i][1]}</div></div>'
        for i in range(len(imgs)))


def preview_square_1(img):
    caps = [(PAGE_NAMES["kschart"], "All 15 major key signatures"), (PAGE_NAMES["circle"], "The order of sharps and flats"),
            (PAGE_NAMES["tcEb"], "Concert key to written key")]
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div><div class="hd" style="font-size:72px;margin-top:28px">What is inside</div>'
        f'<div class="sub" style="font-size:29px;margin-top:10px">Charts for every kind of band instrument</div>'
        f'<div style="flex:1;display:flex;flex-direction:column;align-items:center;justify-content:space-evenly;padding-bottom:70px">'
        f'<div style="display:flex;gap:22px;align-items:flex-start">{trio(img, caps)}</div>{pill_row(["4 chart pages", "15 key signatures", "4 instrument groups"])}</div>'
        f'{swm_over(230)}<div class="band">Concert pitch <em>·</em> written pitch <em>·</em> answer keys</div></div>')


def preview_square_2(a, b):
    pair = "".join(f'<div style="width:380px">{shot(src, 380)}<div class="lbl">{lab}<span>{sub}</span></div></div>'
                   for src, lab, sub in ((a, PAGE_NAMES["w4"], "Blank staves with the key signature printed"), (b, PAGE_NAMES["a45"], "Every scale drawn and named")))
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div><div class="hd" style="font-size:72px;margin-top:24px">Worksheet and key</div>'
        f'<div class="sub" style="font-size:27px;margin-top:8px">Scales in every key, ready to print</div>'
        f'<div style="flex:1;display:flex;align-items:center;padding-bottom:70px"><div style="display:flex;gap:44px;align-items:flex-start">{pair}</div></div>'
        f'{swm_over(230)}<div class="band">Write the scale <em>·</em> check the key <em>·</em> 11 worksheets</div></div>')


def preview_square_3(img):
    caps = [(PAGE_NAMES["w9"], "Mixed instruments"), (PAGE_NAMES["w11"], "Every section reads a different key"), (PAGE_NAMES["rubric"], f"{TOTAL_POINTS} points in all")]
    return sq_doc(
        f'<div class="sq"><div class="store">{BRAND}</div><div class="hd" style="font-size:72px;margin-top:28px">Transpose with ease</div>'
        f'<div class="sub" style="font-size:27px;margin-top:10px">Grades 6–12, from key signatures to score reading</div>'
        f'<div style="flex:1;display:flex;flex-direction:column;align-items:center;justify-content:space-evenly;padding-bottom:70px">'
        f'<div style="display:flex;gap:22px;align-items:flex-start">{trio(img, caps)}</div>{pill_row(["Quiz included", "Rubric and score sheet"])}</div>'
        f'{swm_over(230)}<div class="band">Clarinet <em>·</em> alto sax <em>·</em> horn <em>·</em> flute</div></div>')


# ================================================================== render / build
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


PAGE_LIST = [("Cover", 1), ("Teacher notes", 1), ("Pacing plan", 1), ("Vocabulary", 1), ("Rubric and score sheet", 1),
             ("Key signature chart, circle of fifths and transposing instruments overview", 3), ("Transposition charts for C, B-flat, E-flat and F instruments", 4),
             ("Worksheets 1-11 (student pages)", 11), ("Quiz", 1), ("Answer keys for the worksheets", 6), ("Answer key for the quiz", 1), ("Terms of use and credits", 1)]
assert sum(c for _, c in PAGE_LIST) == TOTAL_PAGES, sum(c for _, c in PAGE_LIST)


def upload_md():
    lst = "\n".join(f"- {n}: {c}" for n, c in PAGE_LIST)
    return f"""# UPLOAD: {LISTING_TITLE} (TpT 065)

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
Key Signature and Scale Worksheets for Band teaches band and orchestra students to read, write and transpose key signatures for every kind of instrument. It covers all 15 major key signatures, major scales, and concert pitch to written pitch for C instruments (flute, oboe, trombone), B-flat instruments (clarinet, trumpet, tenor sax), E-flat instruments (alto sax, baritone sax) and horn in F. There are 11 worksheets, a quiz and a complete answer key for every page.

Every transposition is worked out with the correct interval: B-flat instruments sound a major 2nd lower than written, alto and baritone sax a major 6th lower, and horn in F a perfect 5th lower, so the written key is higher than the concert key by that interval. No key needs more than 7 sharps or flats: where a transposition would, the answer key gives the enharmonic key and explains why (for example, concert F-sharp major for a B-flat clarinet is written A-flat major). All the music notation is drawn with correct clefs, accidentals in the correct order and places, stems and ledger lines.

WHAT'S INCLUDED ({TOTAL_PAGES} pages, PDF, US Letter)
• Cover (1 page)
• Teacher notes with grade guide and standards (1 page)
• Pacing plan, ten sessions (1 page)
• Vocabulary, 16 words (1 page)
• Rubric and score sheet, {TOTAL_POINTS} points (1 page)
• Key signature chart for all 15 major keys, circle of fifths with memory tricks, and a transposing instruments overview (3 pages)
• Transposition charts for C, B-flat, E-flat and F instruments (4 pages)
• Worksheets 1-11: name the key, write the key signature, write scales, concert to written, written to concert and a whole-band grid (11 pages)
• Quiz, 20 points (1 page)
• Answer keys for the worksheets (6 pages)
• Answer key for the quiz (1 page)
• Terms of use and credits (1 page)
Total: {TOTAL_PAGES} pages.

HOW TO USE
Teach the chart pages, then assign the worksheets in order. Each takes 10 to 15 minutes, so they work as bell ringers or warm-ups. Copy the student pages and keep the answer keys. Use the rubric and score sheet to grade, and the quiz at the end.

• Grades 6-12 with a grade guide for each worksheet
• Treble and bass clef key signatures
• Concert pitch and written pitch for the four instrument groups
• Prints well in black and white

{DISCLOSURE}
```

## 3. Grades

TpT allows only 4 grade levels, so the form gets 6th, 8th, 10th and 12th. They are spread across the 6-12 range the product is written for: Worksheets 1, 3, 4 and 6 suit grades 6-7, Worksheets 2, 5, 7 and 8 suit grades 8-9, and Worksheets 9-11 and the quiz suit grades 10-12. The listing title and description say grades 6-12.

## 4. Subjects and tags

- Subjects: {", ".join(SUBJECTS)}
- Tags: {", ".join(TAGS)}

## 5. Page count by section (totals {TOTAL_PAGES})

{lst}
- Total: {TOTAL_PAGES}

## 6. Standards

None cited by code. The teacher notes name the Performing and Responding processes of the National Core Arts Standards for Music in general terms and ask teachers to match them to their own curriculum.

## 7. Price

**${PRICE}** (paid; owner range $3-5).

## 8. Preview

Paid. Preview PDF: circle of fifths and memory tricks (page {P["circle"]}), the B-flat instruments transposition chart (page {P["tcBb"]}), Worksheet 4 (page {P["w4"]}) and the answer key for Worksheets 4 and 5 (page {P["a45"]}), all watermarked.

## 9. Before you click publish

- Evergreen: no season check needed.
- Art: the cover clarinet is made with AI tools (the disclosure line covers it); notation, charts and the circle of fifths are drawn in code.
- Enharmonic rule: any transposition that would need more than 7 sharps or flats is answered with the enharmonic key, marked with an asterisk on the charts and keys.
- Open owner question: logo beside HUDSON BEAT (see tpt/STYLE.md).
"""


def tpt_json():
    return {"price": PRICE, "license_price": PRICE, "tax_code": "Other Digital Goods - No Physical Media", "grades": GRADES, "subjects": SUBJECTS, "tags": TAGS,
            "formats": ["PDF"], "pages": TOTAL_PAGES, "answer_key": "Included",
            "files": {"product": f"{SLUG}.pdf", "preview": f"{SLUG}-PREVIEW.pdf", "thumb1": "cover.png", "thumb2": "preview-1.png", "thumb3": "preview-2.png", "thumb4": "preview-3.png"}}


SHOT_KEYS = ["kschart", "circle", "tcEb", "w4", "a45", "w9", "w11", "rubric"]


def build():
    os.makedirs(BUILD, exist_ok=True)
    full = write("resource.html", html_doc(full_pages(), TITLE))
    prev = write("preview.html", html_doc(preview_pages(), "Preview"))
    render([{"html": full, "pdf": PDF}, {"html": prev, "pdf": PREVIEW_PDF}])
    for k in SHOT_KEYS:
        subprocess.run(["pdftoppm", "-png", "-r", "150", "-f", str(P[k]), "-l", str(P[k]), "-singlefile", PDF, os.path.join(BUILD, f"pg-{k}")], check=True)
    sq = [write("cover.html", cover_square()),
          write("p1.html", preview_square_1(["pg-kschart.png", "pg-circle.png", "pg-tcEb.png"])),
          write("p2.html", preview_square_2("pg-w4.png", "pg-a45.png")),
          write("p3.html", preview_square_3(["pg-w9.png", "pg-w11.png", "pg-rubric.png"]))]
    render([{"html": h, "png": o, "width": 1000, "height": 1000, "scale": 2} for h, o in zip(sq, [COVER_PNG] + PREVIEW_PNGS)])
    with open(UPLOAD, "w") as fh:
        fh.write(upload_md())
    with open(TPT_JSON, "w") as fh:
        json.dump(tpt_json(), fh, indent=2)
        fh.write("\n")
    print(f"built {PDF}, {PREVIEW_PDF}, cover + 3 previews, UPLOAD.md, tpt.json")


if __name__ == "__main__" and "--check" not in sys.argv:
    build()


# ================================================================== checks
import lxml.html as LH

# Knowledge held separately from the generator: the line of fifths, the instrument table and the staff-position tables.
C_FIF = {"F": -1, "C": 0, "G": 1, "D": 2, "A": 3, "E": 4, "B": 5}
C_LINE = ["F", "C", "G", "D", "A", "E", "B"]
C_PC = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
C_SHIFT = {"C": 0, "Bb": 2, "Eb": 3, "F": 1}                      # fifths added to the key going concert -> written
C_INSTR = {"flute": ("C", 0), "oboe": ("C", 0), "bassoon": ("C", 0), "trombone": ("C", 0), "tuba": ("C", 0), "euphonium (bass clef)": ("C", 0),
           "clarinet": ("Bb", 2), "trumpet": ("Bb", 2), "tenor sax": ("Bb", 14), "bass clarinet": ("Bb", 14),
           "alto sax": ("Eb", 9), "alto clarinet": ("Eb", 9), "baritone sax": ("Eb", 21), "horn in F": ("F", 7)}
C_DROP_TEXT = {0: "in unison", 2: "a major 2nd lower", 14: "a major 9th lower", 9: "a major 6th lower", 21: "an octave and a major 6th lower", 7: "a perfect 5th lower"}
C_GROUP_NAME = {"C": "C instruments", "Bb": "B-flat instruments", "Eb": "E-flat instruments", "F": "F instruments"}
C_SIG_POS = {("G", 1): [8, 5, 9, 6, 3, 7, 4], ("G", -1): [4, 7, 3, 6, 2, 5, 1], ("F", 1): [6, 3, 7, 4, 1, 5, 2], ("F", -1): [2, 5, 1, 4, 0, 3, 6]}
C_BOTTOM = {"G": 30, "F": 18}
C_CLEFPOS = {"G": 2, "F": 6}
C_MAJ_STEPS = [2, 2, 1, 2, 2, 2, 1]


def c_fifths(l, a):
    return C_FIF[l] + 7 * a


def c_key(f):
    idx = f + 1
    return C_LINE[idx % 7], idx // 7


def c_written(group, f):
    w = f + C_SHIFT[group]
    enh = w > 7
    if enh:
        w -= 12
    return w, enh


def c_concert(group, f):
    c = f - C_SHIFT[group]
    assert -7 <= c <= 7
    return c


def c_pcof(l, a):
    return (C_PC[l] + a) % 12


def c_text(el):
    import copy
    e2 = copy.deepcopy(el)
    for sv in list(e2.iter("svg")):
        sv.drop_tree()
    return " ".join(e2.text_content().replace(SH, "#").replace(FL, "b").split())


def c_keys_in(t):
    return [(m.group(1), {"#": 1, "b": -1, "": 0}[m.group(2)]) for m in re.finditer(r"\b([A-G])(#|b)?\s*major", t.replace("b major", "b major"))
            if True] if False else [(m.group(1), {"#": 1, "b": -1, None: 0}[m.group(2)]) for m in re.finditer(r"(?<![A-Za-z])([A-G])(#|b)? major", t)]


def c_count(t):
    t = t.lower()
    if "no sharps or flats" in t:
        return 0
    m = re.search(r"(\d) (sharp|flat)", t)
    return int(m.group(1)) * (1 if m.group(2) == "sharp" else -1)


def pcs_of(letter, acc):
    return (C_PC[letter] + acc) % 12


def f_(el, k, d=0.0):
    return float(el.get(k, d))


def c_glyph_box(cp):
    return gbox(cp)


def check_extent_el(sv, label, errs):
    vb = [float(x) for x in sv.get("viewbox").split()]
    W, H_ = vb[2], vb[3]
    for el in sv.iter():
        tag = el.tag
        sw = f_(el, "stroke-width", 0.0) if el.get("stroke") not in (None, "none") else 0.0
        if tag == "line":
            xs, ys = [f_(el, "x1"), f_(el, "x2")], [f_(el, "y1"), f_(el, "y2")]
        elif tag == "rect":
            xs, ys = [f_(el, "x"), f_(el, "x") + f_(el, "width")], [f_(el, "y"), f_(el, "y") + f_(el, "height")]
        elif tag == "circle":
            r = f_(el, "r")
            xs, ys = [f_(el, "cx") - r, f_(el, "cx") + r], [f_(el, "cy") - r, f_(el, "cy") + r]
        elif tag == "text":
            S = f_(el, "font-size") / 4
            x0, y0b, x1, y1b = c_glyph_box(ord(el.text))
            xs = [f_(el, "x") + x0 * S, f_(el, "x") + x1 * S]
            ys = [f_(el, "y") - y1b * S, f_(el, "y") - y0b * S]
        else:
            continue
        pad = max(sw, 1.0)
        if min(xs) - sw / 2 < pad - 1e-6 or min(ys) - sw / 2 < pad - 1e-6 or max(xs) + sw / 2 > W - pad + 1e-6 or max(ys) + sw / 2 > H_ - pad + 1e-6:
            errs.append(f"{label}: a {tag} (stroke {sw}) is closer to the viewBox edge than max(stroke, 1)")


def read_staff(sv, label, errs):
    """Everything drawn in one staff SVG: clef, key signature (type, positions), time signature, notes (letter, octave, shown accidental), bars."""
    out = {"label": label}
    sl = sorted(f_(e, "y1") for e in sv.iter("line") if e.get("class") == "sl")
    if len(sl) != 5:
        errs.append(f"{label}: {len(sl)} staff lines")
        return None
    yb, yt = sl[-1], sl[0]
    S = (yb - yt) / 4
    if any(abs(sl[i] - (yt + i * S)) > 0.02 for i in range(5)):
        errs.append(f"{label}: staff lines are not evenly spaced")

    def pos(y, what):
        v = (yb - y) / (S / 2)
        if abs(v - round(v)) > 0.06:
            errs.append(f"{label}: {what} is off the lines and spaces ({v:.2f})")
        return round(v)

    texts = [e for e in sv.iter("text")]
    clefs = [e for e in texts if e.get("class") == "clef"]
    if len(clefs) != 1:
        errs.append(f"{label}: {len(clefs)} clefs")
        return None
    cp = ord(clefs[0].text)
    clef = {0xE050: "G", 0xE062: "F"}.get(cp)
    if clef is None:
        errs.append(f"{label}: unknown clef glyph")
        return None
    if pos(f_(clefs[0], "y"), "clef") != C_CLEFPOS[clef]:
        errs.append(f"{label}: {clef} clef sits on the wrong line")
    out["clef"] = clef
    ks = sorted((e for e in texts if e.get("class") == "kacc"), key=lambda e: f_(e, "x"))
    kinds = {ord(e.text) for e in ks}
    if len(kinds) > 1:
        errs.append(f"{label}: key signature mixes sharps and flats")
    sig = 0
    if ks:
        sign = 1 if kinds == {0xE262} else -1 if kinds == {0xE260} else 0
        if sign == 0:
            errs.append(f"{label}: key signature glyph is neither sharp nor flat")
        sig = sign * len(ks)
        got = [pos(f_(e, "y"), "key signature accidental") for e in ks]
        if got != C_SIG_POS[(clef, sign)][:len(ks)]:
            errs.append(f"{label}: accidentals in {clef} clef on positions {got}, expected {C_SIG_POS[(clef, sign)][:len(ks)]}")
        xs = [f_(e, "x") for e in ks]
        wid = 0.996 * S if sign > 0 else 0.904 * S
        if any(b - a < wid + 0.1 * S for a, b in zip(xs, xs[1:])):
            errs.append(f"{label}: key signature accidentals overlap")
        if xs[0] - (f_(clefs[0], "x") + 2.6 * S) < 0.2 * S:
            errs.append(f"{label}: key signature touches the clef")
    out["sig"] = sig
    ts = [e for e in texts if e.get("class") == "tsd"]
    out["ts"] = len(ts) == 2 and all(ord(e.text) == 0xE084 for e in ts) and sorted(pos(f_(e, "y"), "time signature") for e in ts) == [2, 6]
    if ts and not out["ts"]:
        errs.append(f"{label}: time signature is not 4/4 on the right lines")
    heads = sorted((e for e in texts if e.get("class") == "head"), key=lambda e: f_(e, "x"))
    naccs = [e for e in texts if e.get("class") == "nacc"]
    stems = [e for e in sv.iter("line") if e.get("class") == "stem"]
    ledgers = [e for e in sv.iter("line") if e.get("class") == "ledger"]
    bars = sorted(f_(e, "x1") for e in sv.iter("line") if e.get("class") == "bar")
    fin = [e for e in sv.iter("rect") if e.get("class") == "fin"]
    out["fin"] = bool(fin)
    out["nbars"] = len(bars)
    sig_letters = {}
    if sig:
        for i in range(abs(sig)):
            sig_letters[C_SIG_POS[(clef, 1 if sig > 0 else -1)][i] % 7 if False else None] = None
        sig_letters = {}
        for p in got:
            sig_letters[(p + C_BOTTOM[clef]) % 7] = 1 if sig > 0 else -1
    notes = []
    sw = 0.13 * S
    used_stems = set()
    for h in heads:
        if ord(h.text) != 0xE0A4:
            errs.append(f"{label}: a notehead is not a filled quarter-note head")
        p = pos(f_(h, "y"), "notehead")
        d = p + C_BOTTOM[clef]
        letter, octave = LET_C[d % 7], d // 7
        x = f_(h, "x")
        y = f_(h, "y")
        up = p < 4
        want_x = x + 1.18 * S - sw / 2 if up else x + sw / 2
        cand = [i for i, st in enumerate(stems) if abs(f_(st, "x1") - want_x) < 0.03 * S and abs(f_(st, "y1") - (y - 0.168 * S if up else y + 0.168 * S)) < 0.03 * S]
        if len(cand) != 1:
            errs.append(f"{label}: note {letter}{octave} has no stem on the correct edge for a stem-{'up' if up else 'down'} note")
        else:
            st = stems[cand[0]]
            used_stems.add(cand[0])
            ln = abs(f_(st, "y2") - f_(st, "y1")) / S
            if (f_(st, "y2") < f_(st, "y1")) != up:
                errs.append(f"{label}: note {letter}{octave} stem points the wrong way")
            if not 3.3 <= ln <= 3.7:
                errs.append(f"{label}: note {letter}{octave} stem is {ln:.2f} spaces long")
            tip = (yb - f_(st, "y2")) / (S / 2)
            if up and tip < 4 - 0.01:
                errs.append(f"{label}: up stem of {letter}{octave} does not reach the middle line")
            if not up and tip > 4 + 0.01:
                errs.append(f"{label}: down stem of {letter}{octave} does not reach the middle line")
        want_led = set(range(-2, p - 1, -2)) if p <= -2 else set(range(10, p + 1, 2)) if p >= 10 else set()
        got_led = {pos(f_(ld, "y1"), "ledger line") for ld in ledgers if f_(ld, "x1") <= x + 0.59 * S <= f_(ld, "x2") and f_(ld, "x1") >= x - 0.7 * S and f_(ld, "x2") <= x + 1.9 * S}
        if got_led != want_led:
            errs.append(f"{label}: ledger lines {sorted(got_led)} for {letter}{octave}, expected {sorted(want_led)}")
        acc = None
        na = [a for a in naccs if abs(f_(a, "y") - y) < 0.01 and 0 < x - f_(a, "x") < 2.5 * S]
        if len(na) > 1:
            errs.append(f"{label}: two accidentals before one note")
        if na:
            acc = {0xE262: 1, 0xE260: -1, 0xE261: 0}[ord(na[0].text)]
            if x - (f_(na[0], "x") + {1: 0.996, -1: 0.904, 0: 0.672}[acc] * S) < 0.15 * S:
                errs.append(f"{label}: accidental touches its notehead")
        eff = acc if acc is not None else sig_letters.get(d % 7, 0)
        notes.append({"l": letter, "o": octave, "acc": acc, "eff": eff, "x": x, "pos": p})
    if len(used_stems) != len(stems):
        errs.append(f"{label}: stems without a head")
    if len(naccs) != sum(1 for n in notes if n["acc"] is not None):
        errs.append(f"{label}: an accidental is not attached to a note")
    out["notes"] = notes
    if bars:
        perbar = []
        for n in notes:
            perbar.append(sum(1 for b in bars if b < n["x"]))
        counts = [perbar.count(i) for i in range(len(bars))]
        out["perbar"] = counts
        if notes and any(c != 4 for c in counts):
            errs.append(f"{label}: bars hold {counts} quarter notes, 4/4 needs 4 each")
        if not fin:
            errs.append(f"{label}: no final barline")
    return out


LET_C = "CDEFGAB"


def read_html(name):
    return LH.fromstring(open(os.path.join(BUILD, name), encoding="utf-8").read())


def scale_verify(info, tonic, label, errs):
    """The drawn notes are the ascending major scale of tonic = (letter, acc) in one octave."""
    ns = info["notes"]
    if len(ns) != 8:
        errs.append(f"{label}: {len(ns)} notes, expected 8")
        return
    tl, ta = tonic
    if (ns[0]["l"], ns[0]["eff"]) != (tl, ta):
        errs.append(f"{label}: scale starts on {ns[0]['l']}{ns[0]['eff']}, expected {tl}{ta}")
    for i in range(7):
        a, b = ns[i], ns[i + 1]
        da = (LET_C.index(b["l"]) + 7 * b["o"]) - (LET_C.index(a["l"]) + 7 * a["o"])
        if da != 1:
            errs.append(f"{label}: notes {i + 1} and {i + 2} are not on adjacent letters")
        semis = (C_PC[b["l"]] + 12 * b["o"] + b["eff"]) - (C_PC[a["l"]] + 12 * a["o"] + a["eff"])
        if semis != C_MAJ_STEPS[i]:
            errs.append(f"{label}: step {i + 1} is {semis} semitones, expected {C_MAJ_STEPS[i]}")
    if (ns[7]["l"], ns[7]["eff"]) != (tl, ta) or ns[7]["o"] != ns[0]["o"] + 1:
        errs.append(f"{label}: the scale does not end on the tonic an octave higher")


def parse_name_line(t):
    return [(m.group(1), {"#": 1, "b": -1, None: 0}[m.group(2)]) for m in re.finditer(r"([A-G])(#|b)?(?=\s|$)", t)]


def verify_html():
    errs = []
    doc = read_html("resource.html")
    pages = {int(p.get("data-p")): p for p in doc.xpath("//section[contains(@class,'page')]")}
    if len(pages) != TOTAL_PAGES:
        errs.append(f"{len(pages)} pages in the HTML, expected {TOTAL_PAGES}")
    # --- every staff: structure and padding
    infos = {}
    nsv = 0
    for pn, p in pages.items():
        for k, sv in enumerate(p.iter("svg")):
            nsv += 1
            lab = f"p{pn}/{sv.get('data-id') or sv.get('class')}"
            check_extent_el(sv, lab, errs)
            if sv.get("class") == "ns":
                infos[doc.getroottree().getpath(sv)] = read_staff(sv, lab, errs)
    stat = {"svgs": nsv}

    def rs(sv):
        return infos[doc.getroottree().getpath(sv)]

    def items(ws, cls):
        return {el.get("data-n"): el for el in doc.xpath(f"//*[@data-ws='{ws}' and contains(concat(' ',@class,' '),' {cls} ')]")}

    def sig_of_item(el):
        sv = el.xpath(".//svg[@class='ns']")
        return rs(sv[0]) if sv else None

    # --- key signature chart (all 15) and the staves drawn in each box
    ks = items("KS", "ksc")
    order = [0] + list(range(1, 8)) + [-1, -2, -3, -4, -5, -6, -7]
    for i, n in enumerate(order):
        el = ks.get(str(i + 1))
        info = sig_of_item(el)
        if info["sig"] != n or info["clef"] != "G":
            errs.append(f"key chart item {i + 1}: drawn signature {info['sig']}, expected {n}")
        t = c_text(el)
        key = c_keys_in(t)
        if key != [c_key(n)] or c_count(t) != n:
            errs.append(f"key chart item {i + 1}: printed '{t}' does not match {c_key(n)} with {n}")
    # --- circle of fifths: printed labels, in order, each a perfect fifth above the last
    labs = doc.xpath("//div[contains(@class,'cfk')]")
    if len(labs) != 12:
        errs.append(f"circle: {len(labs)} labels")
    prev = None
    for i, el in enumerate(labs):
        names = [parse_name_line(x.strip())[0] for x in el.xpath("./b")[0].text_content().replace(SH, "#").replace(FL, "b").split("/")]
        cnts = [c for c in el.xpath("./span")[0].text_content().replace(SH, "#").replace(FL, "b").split("/")]
        for (l, a), c in zip(names, cnts):
            c = c.strip()
            v = 0 if c == "0" else int(c[:-1]) * (1 if c[-1] == "#" else -1)
            if c_fifths(l, a) != v:
                errs.append(f"circle label {i}: {l}{a} printed with {c}, line of fifths says {c_fifths(l, a)}")
        pcnow = c_pcof(*names[0])
        if prev is not None and (pcnow - prev) % 12 != 7:
            errs.append(f"circle label {i}: not a perfect 5th above the previous key")
        if i == 0 and names[0] != ("C", 0):
            errs.append("circle does not start at C major")
        prev = pcnow
    if prev is not None and (pcof_first := c_pcof("C", 0)) is not None and (pcof_first - prev) % 12 != 7:
        errs.append("circle does not close back to C")
    # --- order of sharps/flats staves on the circle page
    # (covered by the staff reader: positions in both clefs) ; instrument list
    ilist = doc.xpath("//p[@data-ws='IL']")
    if {p.xpath("./b")[0].text_content() for p in ilist} != set(C_INSTR):
        errs.append("instrument list: names differ from the table")
    for p in ilist:
        nm = p.xpath("./b")[0].text_content()
        g, drop = C_INSTR[nm]
        t = p.text_content()
        if f"({ {'C': 'C', 'Bb': 'B-flat', 'Eb': 'E-flat', 'F': 'F'}[g] })" not in t or C_DROP_TEXT[drop] not in t:
            errs.append(f"instrument list: '{t}' disagrees with group {g} and a drop of {drop} semitones")
        if (7 * C_SHIFT[g]) % 12 != drop % 12:
            errs.append(f"instrument {nm}: {C_SHIFT[g]} fifths is not {drop % 12} semitones")
    # --- one concert key, four written keys (concert E-flat, 3 flats)
    for ex in doc.xpath("//*[@data-ws='EX']"):
        g = ex.get("data-g")
        w, enh = c_written(g, -3)
        info = sig_of_item(ex)
        t = c_text(ex)
        if info["sig"] != w or c_keys_in(t) != [c_key(w)] or c_count(t) != w:
            errs.append(f"example {g}: drawn {info['sig']}, printed '{t}', expected {w}")
    # --- transposition charts
    for g in GROUPS:
        rows = doc.xpath(f"//tr[@data-ws='TC-{g}']")
        want = [0, 1, 2, 3, 4, 5, 6, -5, -4, -3, -2, -1]
        if [int(r.get("data-n")) for r in rows] != list(range(1, 13)):
            errs.append(f"chart {g}: rows missing")
        for r, n in zip(rows, want):
            tds = r.xpath("./td")
            svs = [rs(sv) for sv in r.iter("svg")]
            if g == "C":
                keys = c_keys_in(c_text(tds[0]))
                if keys != [c_key(n)] or c_count(c_text(tds[0])) != n or [s_["sig"] for s_ in svs] != [n, n] or [s_["clef"] for s_ in svs] != ["G", "F"]:
                    errs.append(f"chart C row {n}: printed or drawn signature wrong")
                continue
            w, enh = c_written(g, n)
            tc, tw = c_text(tds[0]), c_text(tds[3])
            if (c_keys_in(tc) != [c_key(n)] or c_count(tc) != n or c_keys_in(tw) != [c_key(w)] or c_count(tw) != w or ("*" in tw) != enh
                    or [s_["sig"] for s_ in svs] != [n, w] or any(s_["clef"] != "G" for s_ in svs)):
                errs.append(f"chart {g} row concert {c_key(n)}: printed '{tc}' -> '{tw}', drawn {[s_['sig'] for s_ in svs]}, expected written {c_key(w)} ({w}), enharmonic {enh}")
            # sounding pitch: written pitch class minus the drop is the concert pitch class
            drop = {"Bb": 2, "Eb": 9, "F": 7}[g]
            wl, wa = c_key(w)
            if (c_pcof(wl, wa) - drop) % 12 != c_pcof(*c_key(n)):
                errs.append(f"chart {g}: written {wl}{wa} sounded {drop} semitones lower is not concert {c_key(n)}")
    # --- name-the-key worksheets against their keys
    for ws, sigs in (("W1", W1_SIGS), ("W2", W2_SIGS), ("QA", Q_A)):
        st, ak = items(ws, "it"), items(ws, "ak")
        if len(st) != len(sigs) or len(ak) != len(sigs):
            errs.append(f"{ws}: {len(st)} student items and {len(ak)} key items, expected {len(sigs)}")
        for i in range(len(sigs)):
            a, b = st.get(str(i + 1)), ak.get(str(i + 1))
            ia, ib = sig_of_item(a), sig_of_item(b)
            exp = ia["sig"]
            t = c_text(b)
            if ia["sig"] != ib["sig"] or ia["clef"] != ib["clef"] or c_keys_in(t) != [c_key(exp)] or c_count(t) != exp:
                errs.append(f"{ws} item {i + 1}: drawn {exp}, key prints '{t}' (expected {c_key(exp)})")
    # --- write-the-key-signature worksheets
    for ws in ("W3",):
        st, ak = items(ws, "it"), items(ws, "ak")
        for i, el in st.items():
            ia = sig_of_item(el)
            t = c_text(el)
            key = c_keys_in(t)
            want_clef = "G" if "treble" in t else "F" if "bass" in t else "G"
            exp = c_fifths(*key[0])
            ib = sig_of_item(ak[i])
            if ia["sig"] != 0 or ib["sig"] != exp or ib["clef"] != ia["clef"] or ia["clef"] != want_clef:
                errs.append(f"{ws} item {i}: key {key} needs {exp}, key staff has {ib['sig']} in {ib['clef']} (student staff clef {ia['clef']}, prompt says {want_clef})")
            tk = c_text(ak[i])
            if c_keys_in(tk)[:1] != key and ws == "W3":
                errs.append(f"{ws} item {i}: key prints '{tk}'")
    # --- scales
    for ws in ("W4", "W5", "QE"):
        st, ak = items(ws, "it"), items(ws, "ak")
        if not st or len(st) != len(ak):
            errs.append(f"{ws}: scale items {len(st)} vs {len(ak)}")
        for i, el in st.items():
            ia = sig_of_item(el)
            key = c_keys_in(c_text(el))[0]
            f = c_fifths(*key)
            exp_sig = f if ws == "W4" else 0
            ib = sig_of_item(ak[i])
            if ia["sig"] != exp_sig or ia["notes"] or ia["nbars"] != 2 or ib["sig"] != exp_sig or ib["clef"] != "G" or not ib["ts"]:
                errs.append(f"{ws} item {i}: staves wrong (student sig {ia['sig']}, key sig {ib['sig']}, expected {exp_sig})")
                continue
            scale_verify(ib, key, f"{ws} item {i}", errs)
            shown = sum(1 for n in ib["notes"] if n["acc"] is not None)
            want_shown = 0 if ws == "W4" else sum(1 for n in ib["notes"] if n["eff"] != 0)
            if shown != want_shown:
                errs.append(f"{ws} item {i}: {shown} accidentals drawn on the notes, expected {want_shown}")
            if ws != "W4" and any(n["acc"] is None and n["eff"] != 0 for n in ib["notes"]):
                errs.append(f"{ws} item {i}: an altered note has no accidental")
            names = parse_name_line(c_text(ak[i].xpath(".//div[@class='sn']")[0]))
            drawn = [(n["l"], n["eff"]) for n in ib["notes"]]
            if names != drawn:
                errs.append(f"{ws} item {i}: printed note names {names} differ from the drawn notes {drawn}")
    # --- transposition tables (student prompt against answer key)
    def table_rows(ws):
        return {r.get("data-n"): r for r in doc.xpath(f"//tr[@data-ws='{ws}']")}

    def cells(r, cls):
        return r.xpath(f"./td[contains(concat(' ',@class,' '),' {cls} ')]")

    for ws, g in (("W6", "Bb"), ("W7", "Eb"), ("W8", "F")):
        st = [r for r in doc.xpath(f"//tr[@data-ws='{ws}']") if "akr" not in r.get("class")]
        ak = [r for r in doc.xpath(f"//tr[@data-ws='{ws}']") if "akr" in r.get("class")]
        if len(st) != 12 or len(ak) != 12:
            errs.append(f"{ws}: {len(st)} student rows, {len(ak)} key rows")
        concerts = []
        for a, b in zip(st, ak):
            ck = c_keys_in(c_text(cells(a, "q")[0]))[0]
            concerts.append(c_fifths(*ck))
            ck2 = c_keys_in(c_text(cells(b, "c")[0]))[0]
            w, enh = c_written(g, c_fifths(*ck))
            t = " ".join(c_text(x) for x in cells(b, "bl"))
            if ck != ck2 or c_keys_in(t) != [c_key(w)] or c_count(t) != w or ("*" in t) != enh:
                errs.append(f"{ws} item {a.get('data-n')}: concert {ck}, key prints '{t}', expected {c_key(w)} ({w}) enharmonic {enh}")
        if sorted(concerts) != sorted([0, 1, 2, 3, 4, 5, 6, -5, -4, -3, -2, -1]):
            errs.append(f"{ws}: does not cover the 12 concert keys exactly once")
    for ws, mode in (("W9", "cw"), ("W10", "wc"), ("QB", "cw"), ("QC", "wc")):
        st = [r for r in doc.xpath(f"//tr[@data-ws='{ws}']") if "akr" not in r.get("class")]
        ak = [r for r in doc.xpath(f"//tr[@data-ws='{ws}']") if "akr" in r.get("class")]
        if not st or len(st) != len(ak):
            errs.append(f"{ws}: {len(st)} student rows, {len(ak)} key rows")
        for a, b in zip(st, ak):
            qs = a.xpath("./td[contains(@class,'q')]")
            inst = qs[0].text_content().strip()
            g, _d = C_INSTR[inst]
            k_in = c_fifths(*c_keys_in(c_text(qs[1]))[0])
            if b.xpath("./td")[1].text_content().strip() != inst or c_fifths(*c_keys_in(c_text(cells(b, "c")[0]))[0]) != k_in:
                errs.append(f"{ws} item {a.get('data-n')}: key row repeats a different question")
            t = " ".join(c_text(x) for x in cells(b, "bl"))
            if mode == "cw":
                w, enh = c_written(g, k_in)
            else:
                w, enh = c_concert(g, k_in), False
                back, _e = c_written(g, w)
                if back != k_in:
                    errs.append(f"{ws} item {a.get('data-n')}: transposing the answer back does not return the question")
            if c_keys_in(t) != [c_key(w)] or c_count(t) != w or ("*" in t) != enh:
                errs.append(f"{ws} item {a.get('data-n')}: {inst} {c_key(k_in)} -> key prints '{t}', expected {c_key(w)} ({w}) enharmonic {enh}")
    # --- whole-band grid
    st = items("W11C", "it")
    ak = items("W11C", "ak")
    cs = {el.get("data-n"): el for el in doc.xpath("//*[@data-ws='W11' and contains(@class,'ak')]")}
    for i, n in enumerate(W11_KEYS):
        ci = c_text(ak[str(i + 1)])
        if c_keys_in(ci) != [c_key(c_fifths(*c_keys_in(c_text(st[str(i + 1)]))[0]))]:
            errs.append(f"W11 row {i + 1}: concert key differs between student page and key")
        k_in = c_fifths(*c_keys_in(ci)[0])
        for j, g in enumerate(["Bb", "Eb", "F"]):
            el = cs[f"{i + 1}-{j + 1}"]
            w, enh = c_written(g, k_in)
            info = sig_of_item(el)
            t = c_text(el.xpath(".//span[@class='ans']")[0])
            if info["sig"] != w or c_keys_in(t) != [c_key(w)] or ("*" in t) != enh:
                errs.append(f"W11 cell {i + 1}-{j + 1}: drawn {info['sig']}, prints '{t}', expected {c_key(w)} ({w})")
    # quiz D: concert key and instrument printed in the prompt
    qtxt = [c_text(p) for p in doc.xpath("//section[@data-k='quiz']//p") if "The band plays in concert" in c_text(p)]
    if len(qtxt) != 1:
        errs.append("quiz section D prompt not found")
    else:
        mk = c_keys_in(qtxt[0])[0]
        inst = [nm for nm in C_INSTR if f"an {nm} reads" in qtxt[0] or f"a {nm} reads" in qtxt[0]]
        if len(inst) != 1:
            errs.append("quiz section D: instrument not found")
        else:
            w, enh = c_written(C_INSTR[inst[0]][0], c_fifths(*mk))
            qs_, qa_ = items("QD", "it"), items("QD", "ak")
            ib, ia = sig_of_item(qa_["1"]), sig_of_item(qs_["1"])
            t = c_text(qa_["1"])
            if ia["sig"] != 0 or ib["sig"] != w or c_keys_in(t) != [c_key(w)] or c_count(t) != w:
                errs.append(f"quiz D: {inst[0]} in concert {mk} reads {c_key(w)} ({w}); key staff {ib['sig']}, prints '{t}'")
    # --- point totals recomputed from the items on the pages
    counts = {"w1": len(items("W1", "it")), "w2": len(items("W2", "it")), "w3": len(items("W3", "it")), "w4": 2 * len(items("W4", "it")),
              "w5": 2 * len(items("W5", "it")), "w6": len(doc.xpath("//tr[@data-ws='W6'][not(contains(@class,'akr'))]")),
              "w7": len(doc.xpath("//tr[@data-ws='W7'][not(contains(@class,'akr'))]")), "w8": len(doc.xpath("//tr[@data-ws='W8'][not(contains(@class,'akr'))]")),
              "w9": len(doc.xpath("//tr[@data-ws='W9'][not(contains(@class,'akr'))]")), "w10": len(doc.xpath("//tr[@data-ws='W10'][not(contains(@class,'akr'))]")),
              "w11": len(doc.xpath("//*[@data-ws='W11' and contains(@class,'it')]")),
              "quiz": len(items("QA", "it")) + len(doc.xpath("//tr[@data-ws='QB'][not(contains(@class,'akr'))]")) + len(doc.xpath("//tr[@data-ws='QC'][not(contains(@class,'akr'))]")) + 2 * len(items("QD", "it")) + 8 * len(items("QE", "it"))}
    for k, v in counts.items():
        if v != WS_POINTS[k]:
            errs.append(f"points for {k}: {v} items on the pages, score sheet says {WS_POINTS[k]}")
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
      const BOX = '.it, .ak, .ksc, .box, .ex, .top, .nd, .doc table, .doc p, .doc ul, .cfwrap, .inst';
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
          if (el.matches('.it, .ak, .ksc, .box, .ex')) boxes.push([el, r]);
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
          if (gx < 4 && gy < 4) res.push(`page ${i + 1}: two boxes lack a gutter`);
        }
        pg.querySelectorAll('.it, .ak, .ksc, .box, .ex').forEach(bx => {
          if (bx.scrollWidth > bx.clientWidth + 1 || bx.scrollHeight > bx.clientHeight + 1) res.push(`page ${i + 1}: content overflows a ${bx.className} box`);
          const br = bx.getBoundingClientRect();
          bx.querySelectorAll('svg').forEach(sv => {
            const s = sv.getBoundingClientRect();
            if (s.left < br.left + 3 || s.right > br.right - 3 || s.top < br.top + 2 || s.bottom > br.bottom - 2) res.push(`page ${i + 1}: a drawing is too close to its box edge`);
          });
        });
        pg.querySelectorAll('.tc td').forEach(td => {
          const br = td.getBoundingClientRect();
          td.querySelectorAll('svg').forEach(sv => {
            const s = sv.getBoundingClientRect();
            if (s.left < br.left + 2 || s.right > br.right - 2 || s.top < br.top + 1 || s.bottom > br.bottom - 1) res.push(`page ${i + 1}: a chart drawing is too close to its cell edge`);
          });
        });
        const cfk = [...pg.querySelectorAll('.cfk')].map(e => e.getBoundingClientRect());
        for (let a = 0; a < cfk.length; a++) for (let c = a + 1; c < cfk.length; c++) {
          if (cfk[a].left < cfk[c].right - 1 && cfk[c].left < cfk[a].right - 1 && cfk[a].top < cfk[c].bottom - 1 && cfk[c].top < cfk[a].bottom - 1) res.push(`page ${i + 1}: circle labels overlap`);
        }
        pg.querySelectorAll('.cfk').forEach(k => { if (k.scrollWidth > k.clientWidth + 4 || k.scrollHeight > k.clientHeight + 2) res.push(`page ${i + 1}: circle label overflows`); });
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
            if (last[1] - last[0] < 0.1 * w && el.innerText.trim().split(/\s+/).length > 8) res.push(`page ${i + 1}: short last line in "${el.innerText.trim().slice(0, 40)}..."`);
          }
        });
        let maxb = 0;
        pg.querySelectorAll('*').forEach(el => { if (skip(el)) return; const r = el.getBoundingClientRect(); if (r.height > 0 && r.width > 0 && ((el.children.length === 0 && ((el.textContent || '').trim() || el.matches('svg, img'))) || el.matches('.it, .ak, .ksc, .box, table'))) maxb = Math.max(maxb, r.bottom); });
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
        sq.querySelectorAll('.shot img').forEach(im => { if (!im.complete || im.naturalWidth === 0) res.push(`square ${i + 1}: an image did not load`); });
        sq.querySelectorAll('img').forEach(im => { if (!im.complete || im.naturalWidth === 0) res.push(`square ${i + 1}: an image did not load`); });
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
SVG_RE = re.compile(r'<svg class="(?:ns|dg)".*?</svg>', re.S)


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
    html = open(os.path.join(BUILD, "resource.html")).read()
    uniq = []
    for sv in SVG_RE.findall(html):
        if sv not in uniq:
            uniq.append(sv)
    page_ = (f'<!doctype html><html><head><meta charset="utf-8"><style>{font_css()}html,body{{margin:0;background:transparent}}'
             f'svg{{display:block;margin:12px}}</style></head><body>{"".join(uniq)}</body></html>')
    write("alone.html", page_)
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
    h = Image.open(HERO)
    a = h.getchannel("A").point(lambda v: 255 if v > 24 else 0)
    bb = a.getbbox()
    if bb is None or bb[0] < 10 or bb[1] < 10 or h.width - bb[2] < 10 or h.height - bb[3] < 10:
        errs.append(f"hero.png touches its image edge: {bb}")
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
    for p in [PDF, PREVIEW_PDF, COVER_PNG, *PREVIEW_PNGS, UPLOAD, TPT_JSON, HERO, os.path.join(TPT, "STYLE.md"), RENDER_JS]:
        if not os.path.exists(p):
            errs.append(f"missing {os.path.relpath(p, TPT)}")
    if errs:
        return errs
    for path, want in ((PDF, TOTAL_PAGES), (PREVIEW_PDF, 4)):
        rd = PdfReader(path)
        if len(rd.pages) != want:
            errs.append(f"{os.path.basename(path)}: {len(rd.pages)} pages, expected {want}")
        for i, pg_ in enumerate(rd.pages):
            if abs(float(pg_.mediabox.width) - 612) > 1 or abs(float(pg_.mediabox.height) - 792) > 1:
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
    texts = [" ".join((pg_.extract_text() or "").split()) for pg_ in rd.pages]
    for i, t in enumerate(texts):
        if len(t) < 40:
            errs.append(f"PDF page {i + 1} looks blank")
        if "PREVIEW" in t.upper():
            errs.append(f"product PDF page {i + 1} carries a PREVIEW watermark")
        if i + 1 != 1 and f"Page {i + 1}" not in t:
            errs.append(f"PDF page {i + 1} does not print its own page number")
    for k, name in PAGE_NAMES.items():
        if k == "cover":
            continue
        if name.lower() not in texts[P[k] - 1].lower():
            errs.append(f"page {P[k]} does not show its name '{name}'")
    full_pages()
    for frm, to, text in XREFS:
        if text not in texts[frm - 1]:
            errs.append(f"page {frm}: cross-reference text '{text}' not found")
    for i, t in enumerate(texts):
        for m in re.finditer(r"(?i)\bpages? (\d+)(?:–(\d+))?", t):
            a, b = int(m.group(1)), int(m.group(2) or m.group(1))
            if a < 1 or b > TOTAL_PAGES or b < a:
                errs.append(f"page {i + 1}: reference '{m.group(0)}' is outside the {TOTAL_PAGES}-page file")
    # each worksheet points at its key page and the key page is the one holding that worksheet's answers
    for k, kp in KEY_PAGE.items():
        if f"Answer key: page {P[kp]}" not in texts[P[k] - 1]:
            errs.append(f"{k} does not point at its answer key page {P[kp]}")
        label = PAGE_NAMES[k].split(":")[0].replace("Worksheet ", "")
        keyname = PAGE_NAMES[kp]
        if k != "quiz" and not re.search(rf"\b{label}\b", keyname.replace(",", " ").replace(" and ", " ")):
            errs.append(f"{k} is not named on {keyname}")
    teach, terms, score, pace = texts[P["teach"] - 1], texts[P["terms"] - 1], texts[P["rubric"] - 1], texts[P["pacing"] - 1]
    for need in (f"page {P['kschart']}", f"page {P['circle']}", f"page {P['overview']}", f"pages {P['tcC']}–{P['tcF']}", f"pages {P['w1']}–{P['quiz']}",
                 f"pages {P['a12']}–{P['aq']}", f"page {P['pacing']}", f"page {P['vocab']}", f"page {P['rubric']}"):
        if need not in teach:
            errs.append(f"teacher notes lack the reference '{need}'")
    if (f"pages {P['kschart']}–{P['tcF']}" not in terms or f"pages {P['w1']}–{P['quiz']}" not in terms or f"pages {P['a12']}–{P['aq']}" not in terms
            or f"({TOTAL_PAGES} pages)" not in terms.lower()):
        errs.append("terms page 'what is in this file' does not match the page numbers")
    if f"{TOTAL_POINTS}" not in score:
        errs.append("score sheet lacks the total")
    for d, (day, _t, ref, ws) in zip(range(10), PACING):
        want_ref, want_ws = f"page {P[ref.split(', ')[0]]}", (lambda w: f"pages {P[w[0]]}\u2013{P[w[1]]}" if isinstance(w, tuple) else f"page {P[w]}")(PACING_WS[day])
        if want_ref not in pace or want_ws not in pace:
            errs.append(f"pacing session {day}: page references missing")
    prd = PdfReader(PREVIEW_PDF)
    for i in range(4):
        t = prd.pages[i].extract_text() or ""
        if t.count("PREVIEW") != 1:
            errs.append(f"preview PDF page {i + 1}: expected exactly one PREVIEW watermark")
        if PAGE_NAMES[PREVIEW_KEYS[i]].lower() not in " ".join(t.split()).lower():
            errs.append(f"preview PDF page {i + 1} is not '{PAGE_NAMES[PREVIEW_KEYS[i]]}'")
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
    for need in (DISCLOSURE, f"${PRICE}", f"{TOTAL_PAGES} pages", "grades 6-12", "TpT allows only 4 grade levels", "6th, 8th, 10th and 12th", "11 worksheets"):
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
    if f"{TOTAL_POINTS} points" not in desc:
        errs.append("UPLOAD.md description lacks the score total")
    low = up.lower()
    for bad in ("checked by hand", "handmade", "recomputed", "classroom-tested", "classroom tested", "hand-checked"):
        if bad in low:
            errs.append(f"UPLOAD.md says '{bad}'")
    tj = json.load(open(TPT_JSON))
    tags, subs = set(load_json("TAG-OPTIONS.json")["options"]), set(load_json("SUBJECT-OPTIONS.json"))
    heads = {"Performing Arts", "Holiday", "Student Practice"}
    if any(t not in tags or t in heads for t in tj["tags"]) or any(s not in subs or s in heads for s in tj["subjects"]):
        errs.append("tpt.json tags or subjects invalid")
    if tj.get("pages") != TOTAL_PAGES or tj["price"] != PRICE or not 1 <= len(tj["grades"]) <= 4:
        errs.append("tpt.json pages, price or grades mismatch")
    first = texts[0].lower()
    if f"{TOTAL_PAGES} pages" not in first or "11 worksheets" not in first or "grades 6–12" not in first:
        errs.append("cover text does not state the page count, worksheet count and grades")
    if DISCLOSURE not in terms:
        errs.append("terms page lacks the disclosure line")
    allt = " ".join(texts).lower()
    for bad in ("qa ", "checker", "recomputed", "verified by code"):
        if bad in allt.replace("answer keys are verified", ""):
            errs.append(f"buyer-facing text contains internal wording '{bad}'")
    for bad in ("colour", "favourite", "metre", "crotchet", "quaver", "minim", "semibreve", "analyse"):
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
    print("CHECK OK: every staff re-read from the rendered SVG (clef glyph and line, key-signature accidentals on their staff positions in treble and bass clef, 4/4, noteheads, "
          "stem side, direction and length, ledger lines, barlines, 4 quarter notes in every bar); all 15 key signatures, the circle of fifths (each step a perfect 5th), the four "
          "transposition charts, every worksheet item and every answer key recomputed on the line of fifths (written = concert + 2, 3 or 1 fifths, minus 12 past 7 sharps or flats) "
          "and cross-checked by pitch class (written minus the sounding drop = concert); every scale verified as whole, whole, half, whole, whole, whole, half on adjacent letters; "
          f"point totals ({TOTAL_POINTS}) recounted from the pages; no drawing touches its edge; layout and footer gaps clear; PDF {TOTAL_PAGES} Letter pages, preview 4 (one watermark each); "
          "images 2000x2000 with clean edges; cross-references, UPLOAD.md and tpt.json agree.")


if __name__ == "__main__" and "--check" in sys.argv:
    check()
