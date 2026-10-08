"""Rhythm notation for Winter Rhythm Bingo (grades 3-6), engraved with Bravura.

Builds on item 002's rhythm.py (which itself reuses item 001's notation.py glyph
table and line weights) and adds sixteenth-note groups and dotted rhythms.
Units are points, y pointing down; `s` is one staff space.

Tokens (each starts on a beat):
    q  quarter note                      1 beat
    e  two eighth notes (beamed)         1 beat
    r  quarter rest                      1 beat
    h  half note                         2 beats
    t  dotted half note                  3 beats
    s  four sixteenth notes (beamed)     1 beat
    a  eighth + two sixteenths           1 beat
    b  two sixteenths + eighth           1 beat
    d  dotted quarter + eighth           2 beats

Spacing is by note count, not strictly beat-proportional, so sixteenth groups
get room to breathe at normal printed-music size (s ~ 5 pt).
"""
import importlib.util
import os
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location(
    "rhythm002", os.path.join(os.path.dirname(HERE), "002-fall-rhythm-flashcards", "rhythm.py"))
R2 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(R2)

GLYPH = R2.GLYPH          # private copy of 002's module, so extending it is safe
GLYPH.update({
    "augmentationDot": (0xE1E7, (0.0, -0.2), (0.4, 0.2)),   # checked against bravura.woff2 with fontTools
})
glyph = R2.glyph
STEM_UP_SE = R2.STEM_UP_SE
STEM_LEN = R2.STEM_LEN
STEM_W = R2.STEM_W
STAFF_W = R2.STAFF_W
BEAM_T = R2.BEAM_T            # 0.5 space
BEAM_GAP = 0.3                # a little over Bravura beamSpacing (0.25) so photocopies keep the gap
HEAD_W = R2.HEAD_W

# Durations of each sound in beats (negative = rest). This table is independent
# of "beats" below; gen.py --check confirms the two agree.
TOKENS = {
    "q": {"beats": 1, "dur": [F(1)], "name": "quarter note", "kodaly": "ta", "count": ["{n}"]},
    "e": {"beats": 1, "dur": [F(1, 2)] * 2, "name": "two eighth notes", "kodaly": "ti-ti", "count": ["{n}", "&"]},
    "r": {"beats": 1, "dur": [F(-1)], "name": "quarter rest", "kodaly": "(rest)", "count": ["({n})"]},
    "h": {"beats": 2, "dur": [F(2)], "name": "half note", "kodaly": "ta-a", "count": ["{n}", "({n1})"]},
    "t": {"beats": 3, "dur": [F(3)], "name": "dotted half note", "kodaly": "ta-a-a", "count": ["{n}", "({n1})", "({n2})"]},
    "s": {"beats": 1, "dur": [F(1, 4)] * 4, "name": "four sixteenth notes", "kodaly": "ti-ka-ti-ka", "count": ["{n}", "e", "&", "a"]},
    "a": {"beats": 1, "dur": [F(1, 2), F(1, 4), F(1, 4)], "name": "eighth + two sixteenths", "kodaly": "ti-tika", "count": ["{n}", "&", "a"]},
    "b": {"beats": 1, "dur": [F(1, 4), F(1, 4), F(1, 2)], "name": "two sixteenths + eighth", "kodaly": "tika-ti", "count": ["{n}", "e", "&"]},
    "d": {"beats": 2, "dur": [F(3, 2), F(1, 2)], "name": "dotted quarter + eighth", "kodaly": "tam-ti", "count": ["{n}", "({n1})", "&"]},
}
SIXTEENTHS = set("sab")

PAD = 0.75   # spaces of air either side of each token
# head-left x offsets (spaces) inside a token, and its drawn width
HEADS = {"q": [0], "e": [0, 2.3], "s": [0, 1.6, 3.2, 4.8], "a": [0, 2.1, 3.7], "b": [0, 1.6, 3.7]}
INK_W = {"q": 1.33, "r": 1.08, "h": 1.36 + 1.0, "t": 1.36 + 0.75 + 1.2, "e": 2.3 + HEAD_W,
         "s": 4.8 + HEAD_W, "a": 3.7 + HEAD_W, "b": 3.7 + HEAD_W, "d": 3.15 + 2.264}


def beats(pattern):
    return sum(TOKENS[t]["beats"] for t in pattern)


def onsets(pattern):
    """Beat index (0-based) at which each token starts."""
    out, b = [], 0
    for t in pattern:
        out.append(b)
        b += TOKENS[t]["beats"]
    return out


def counts(pattern):
    """Counting line, e.g. '1 e & a  2 &  3 (4)'. Held or silent beats are in parentheses."""
    words = []
    for t, b in zip(pattern, onsets(pattern)):
        n = b + 1
        words.append(" ".join(c.format(n=n, n1=n + 1, n2=n + 2) for c in TOKENS[t]["count"]))
    return "   ".join(words)


def syllables(pattern):
    return "  ".join(TOKENS[t]["kodaly"] for t in pattern)


def width(pattern):
    """Width in staff spaces of the notes alone (no time signature or barlines)."""
    return sum(INK_W[t] + 2 * PAD for t in pattern)


def _dot(x, yl, s, fill):
    # notes sit on the line, so the dot goes in the space above (SMuFL convention)
    return glyph("augmentationDot", x, yl - 0.5 * s, s, fill)


def beamed(xs, yl, s, secondary=(), fill="#000"):
    """Beamed black notes with stems up. xs: head-left x of each head. secondary: (i, j) pairs of
    note indices joined by a second (sixteenth) beam."""
    out = []
    sw = STEM_W * s
    top = yl - STEM_LEN * s
    stems = []
    for nx in xs:
        out.append(glyph("noteheadBlack", nx, yl, s, fill))
        x = nx + STEM_UP_SE[0] * s - sw / 2
        stems.append(x)
        out.append(f'<line x1="{x:.2f}" y1="{yl - STEM_UP_SE[1] * s:.2f}" x2="{x:.2f}" y2="{top:.2f}" stroke="{fill}" stroke-width="{sw:.2f}"/>')
    out.append(f'<rect x="{stems[0] - sw / 2:.2f}" y="{top:.2f}" width="{stems[-1] - stems[0] + sw:.2f}" height="{BEAM_T * s:.2f}" fill="{fill}"/>')
    y2 = top + (BEAM_T + BEAM_GAP) * s
    for i, j in secondary:
        out.append(f'<rect x="{stems[i] - sw / 2:.2f}" y="{y2:.2f}" width="{stems[j] - stems[i] + sw:.2f}" height="{BEAM_T * s:.2f}" fill="{fill}"/>')
    return "".join(out)


def token(tok, x, yl, s, fill="#000"):
    """Draw one token with its ink starting at x (no padding). Noteheads sit on y = yl."""
    if tok == "q":
        return glyph("noteQuarterUp", x, yl, s, fill)
    if tok == "r":
        return glyph("restQuarter", x, yl, s, fill)
    if tok == "h":
        return glyph("noteHalfUp", x, yl, s, fill)
    if tok == "t":
        return glyph("noteHalfUp", x, yl, s, fill) + _dot(x + (1.18 + 0.35) * s, yl, s, fill)
    if tok == "d":
        return (glyph("noteQuarterUp", x, yl, s, fill) + _dot(x + (1.18 + 0.35) * s, yl, s, fill)
                + glyph("note8thUp", x + 3.15 * s, yl, s, fill))
    xs = [x + o * s for o in HEADS[tok]]
    sec = {"e": (), "s": ((0, 3),), "a": ((1, 2),), "b": ((0, 1),)}[tok]
    return beamed(xs, yl, s, sec, fill)


def pattern(p, x0, yl, s, line=True, fill="#000", extend=0.6):
    """Notes only, starting at x0. Returns (svg, right edge)."""
    out, x = [], x0
    for t in p:
        x += PAD * s
        out.append(token(t, x, yl, s, fill))
        x += (INK_W[t] + PAD) * s
    if line:
        out.insert(0, R2._line(x0 - extend * s, yl, x + extend * s, yl, STAFF_W * s * 1.3))
    return "".join(out), x


def measure(p, x0, yl, s, fill="#000"):
    """A full 4/4 bar on a one-line rhythm staff: time signature, notes, final barline.
    Returns (svg, right edge)."""
    out = [glyph("timeSig4", x0, yl - s, s, fill), glyph("timeSig4", x0, yl + s, s, fill)]
    body, end = pattern(p, x0 + 2.4 * s, yl, s, line=False, fill=fill)
    out.append(body)
    end += 0.3 * s
    thick = 0.5 * s
    out.insert(0, R2._line(x0 - 0.4 * s, yl, end + 0.6 * s + thick, yl, STAFF_W * s * 1.3))
    out.append(R2._line(end, yl - 2 * s, end, yl + 2 * s, 0.16 * s))
    out.append(f'<rect x="{end + 0.6 * s:.2f}" y="{yl - 2 * s:.2f}" width="{thick:.2f}" height="{4 * s:.2f}" fill="{fill}"/>')
    return "".join(out), end + 0.6 * s + thick


def measure_width(p):
    return 2.4 + width(p) + 0.3 + 0.6 + 0.5
