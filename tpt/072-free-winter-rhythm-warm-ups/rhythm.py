"""Rhythm lines in 4/4 for the warm-up pages, drawn as SVG with Bravura (SIL OFL 1.1).

A line is one to four bars on a one-line rhythm staff (five staff lines, unpitched percussion clef, 4/4). Every note sits on the middle
line, so every stem goes down (down on or above the middle line), attached to the LEFT edge of the notehead. Paired eighth notes (ti-ti)
share a beam at the stem ends. Half notes have an open head and a stem, whole notes an open head and no stem. A quarter rest hangs
from the middle line.

Symbols: Q = quarter note (ta, 1 beat), E = pair of eighth notes (ti-ti, 1 beat), R = quarter rest (shh, 1 beat),
H = half note (ta-a, 2 beats), W = whole note (ta-a-a-a, 4 beats).
"""
CP_PERC = 0xE069       # unpitched percussion clef
CP_TS4 = 0xE084        # time signature digit 4
CP_WHOLE = 0xE0A2      # open notehead, whole note
CP_HALF = 0xE0A3       # open notehead, half note
CP_HEAD = 0xE0A4       # black notehead
CP_QREST = 0xE4E5      # quarter rest
HEAD_W = {"Q": 1.18, "E": 1.18, "H": 1.18, "W": 1.688}   # spaces
STEM_W = 0.13
STEM_LEN = 3.5
STEM_DOWN_NW_Y = -0.168   # stem-down anchor: spaces above the notehead centre
BEAT_BEAM_T = 0.5
STAFF_W = 0.16
LEAD = 0.55            # spaces between a bar's (or beat's) left edge and the first note
BEATS = {"Q": 1, "E": 1, "R": 1, "H": 2, "W": 4}
SYL = {"Q": "ta", "E": "ti-ti", "R": "shh", "H": "ta-a", "W": "ta-a-a-a"}
PARTS = {"Q": 1, "E": 2, "R": 1, "H": 2, "W": 4}      # spoken parts (syllables) in the word or syllable text for each symbol


def f(v):
    return f"{v:.2f}".rstrip("0").rstrip(".")


def layout(sp, nbars, bw):
    """x positions in points before padding: clef, time signature, first bar's left edge, right edge of the last bar."""
    x_clef = 0.5 * sp
    x_ts = x_clef + 1.528 * sp + 0.9 * sp
    x0 = x_ts + 1.88 * sp + 0.9 * sp
    return x_clef, x_ts, x0, x0 + nbars * 4 * bw


def fit_bw(total_w, nbars, sp, pad=2.5):
    """Beat width that makes the whole svg exactly total_w points wide."""
    x0 = layout(sp, 1, 1)[2]
    return (total_w - 2 * pad - 0.9 * sp - x0) / (nbars * 4)


def rhythm_svg(bars, sp=6.5, bw=58, rows=("num", "word", "syl"), words=None, label=None, pad=2.5):
    """bars = list of strings of symbols (each must add up to 4 beats; None for a blank staff of `n` empty bars = len(bars)).
    words = list (per bar) of lists of cue words (one per symbol), shown in the 'word' row. Returns (svg, width, height)."""
    blank = all(b is None for b in bars)
    nb = len(bars)
    x_clef, x_ts, x0, x_end = layout(sp, nb, bw)
    width = x_end + 0.9 * sp + 2 * pad
    x_clef += pad
    x_ts += pad
    x0 += pad
    x_end += pad
    top = pad + 0.6 * sp
    mid = top + 2 * sp
    stem_top = mid + STEM_DOWN_NW_Y * sp
    stem_bot = stem_top + STEM_LEN * sp
    y = (top + 4 * sp + 0.4 * sp) if blank else stem_bot + 0.3 * sp
    row_y = {}
    fs = max(8.5, sp * 1.85)
    if not blank:
        for r in rows:
            y += fs * 1.0
            row_y[r] = y
            y += fs * 0.18
    height = y + 3
    g = []
    ff = "font-family:Bravura"
    for i in range(5):
        yy = top + i * sp
        g.append(f'<line class="sl" x1="{f(pad)}" y1="{f(yy)}" x2="{f(x_end + 0.9 * sp)}" y2="{f(yy)}" stroke="#000" stroke-width="{f(STAFF_W * sp)}"/>')
    g.append(f'<rect class="bar" x="{f(pad)}" y="{f(top)}" width="{f(0.16 * sp)}" height="{f(4 * sp)}"/>')   # start of the staff
    for k in range(1, nb):
        g.append(f'<rect class="bar" x="{f(x0 + k * 4 * bw - 0.08 * sp)}" y="{f(top)}" width="{f(0.16 * sp)}" height="{f(4 * sp)}"/>')
    g.append(f'<rect class="bar" x="{f(x_end)}" y="{f(top)}" width="{f(0.16 * sp)}" height="{f(4 * sp)}"/>')                # final barline: thin
    g.append(f'<rect class="bar" x="{f(x_end + 0.4 * sp)}" y="{f(top)}" width="{f(0.5 * sp)}" height="{f(4 * sp)}"/>')     # and thick
    g.append(f'<text class="clef" x="{f(x_clef)}" y="{f(mid)}" style="{ff}" font-size="{f(4 * sp)}">{chr(CP_PERC)}</text>')
    g.append(f'<text class="ts" x="{f(x_ts)}" y="{f(mid - sp)}" style="{ff}" font-size="{f(4 * sp)}">{chr(CP_TS4)}</text>')
    g.append(f'<text class="ts" x="{f(x_ts)}" y="{f(mid + sp)}" style="{ff}" font-size="{f(4 * sp)}">{chr(CP_TS4)}</text>')
    if not blank:
        for bi, bar in enumerate(bars):
            beat = 0
            for si, c in enumerate(bar):
                bx = x0 + bi * 4 * bw + beat * bw + LEAD * sp
                hw = HEAD_W.get(c, 0) * sp
                if c == "E":
                    heads = [bx, bx + bw / 2]
                elif c in "QHW":
                    heads = [bx]
                else:
                    heads = []
                glyph = {"Q": CP_HEAD, "E": CP_HEAD, "H": CP_HALF, "W": CP_WHOLE}.get(c)
                for hx in heads:
                    g.append(f'<text class="nh" x="{f(hx)}" y="{f(mid)}" style="{ff}" font-size="{f(4 * sp)}">{chr(glyph)}</text>')
                    if c != "W":
                        g.append(f'<rect class="stem" x="{f(hx)}" y="{f(stem_top)}" width="{f(STEM_W * sp)}" height="{f(STEM_LEN * sp)}"/>')
                if c == "E":
                    bt = BEAT_BEAM_T * sp
                    g.append(f'<rect class="beam" x="{f(heads[0])}" y="{f(stem_bot - bt)}" width="{f(heads[1] + STEM_W * sp - heads[0])}" height="{f(bt)}"/>')
                if c == "R":
                    g.append(f'<text class="rest" x="{f(bx)}" y="{f(mid)}" style="{ff}" font-size="{f(4 * sp)}">{chr(CP_QREST)}</text>')
                    cx = bx + 0.54 * sp
                elif c == "E":
                    cx = (heads[0] + heads[1] + HEAD_W["E"] * sp) / 2
                else:
                    cx = bx + hw / 2
                tx = {}
                if "word" in rows and words:
                    tx["word"] = words[bi][si]
                tx["syl"] = SYL[c]
                for r in rows:
                    if r == "num":
                        continue
                    g.append(f'<text class="{r}" x="{f(cx)}" y="{f(row_y[r])}" text-anchor="middle" '
                             f'style="font-family:Oswald;font-weight:{500 if r == "syl" else 400}" font-size="{f(fs)}" fill="#000">{tx[r]}</text>')
                beat += BEATS[c]
            if "num" in rows:
                for k in range(4):
                    g.append(f'<text class="num" x="{f(x0 + bi * 4 * bw + k * bw + LEAD * sp + 0.59 * sp)}" y="{f(row_y["num"])}" text-anchor="middle" '
                             f'style="font-family:Oswald;font-weight:400" font-size="{f(fs * 0.9)}" fill="#555">{k + 1}</text>')
    attrs = f'class="rh" data-label="{label or ""}" data-sp="{f(sp)}" data-bw="{f(bw)}" data-pad="{f(pad)}"'
    svg = (f'<svg {attrs} xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {f(width)} {f(height)}" width="{f(width)}" height="{f(height)}">'
           + "".join(g) + "</svg>")
    return svg, width, height
