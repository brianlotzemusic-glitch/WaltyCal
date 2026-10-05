"""Rhythm notation for the fall flashcards: engraved (Bravura) and hand-drawn (stick / tracing).

Reuses the Bravura glyph table and line weights from item 001's notation.py and
adds the glyphs this item needs. Units are points, y pointing down; `s` is one
staff space. Glyph metrics were checked against bravura.woff2 with fontTools.

Tokens (one per beat group):
    q  quarter note       1 beat, 1 sound
    e  two eighth notes   1 beat, 2 sounds (beamed pair)
    r  quarter rest       1 beat, silent
    h  half note          2 beats, 1 sound
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "001-halloween-color-by-note"))
import notation as N001  # noqa: E402

GLYPH = dict(N001.GLYPH)
GLYPH.update({
    "noteheadHalf": (0xE0A3, (0.0, -0.5), (1.18, 0.5)),
    "timeSig4": (0xE084, (0.08, -1.0), (1.8, 1.004)),
})
STEM_UP_SE = N001.STEM_UP_SE        # (1.18, 0.168) noteheadBlack/noteheadHalf
STEM_LEN = N001.STEM_LEN            # 3.5 spaces
STEM_W = N001.STEM_W
STAFF_W = N001.STAFF_W
BEAM_T = 0.5                        # Bravura beamThickness
HEAD_W = 1.18

TOKENS = {
    "q": {"beats": 1, "sounds": 1, "name": "quarter note", "kodaly": "ta", "word": "leaf", "art": "maple"},
    "e": {"beats": 1, "sounds": 2, "name": "two eighth notes", "kodaly": "ti-ti", "word": "pump-kin", "art": "pumpkin"},
    "r": {"beats": 1, "sounds": 0, "name": "quarter rest", "kodaly": "silent beat (some say “rest”)", "word": "shh", "art": "acorn"},
    "h": {"beats": 2, "sounds": 1, "name": "half note", "kodaly": "ta-a", "word": "whoo-oo (owl)", "art": "owl"},
}


def beats(pattern):
    return sum(TOKENS[t]["beats"] for t in pattern)


def glyph(name, x, y, s, fill="#000"):
    return f'<text x="{x:.2f}" y="{y:.2f}" font-family="Bravura" font-size="{4 * s:.2f}" fill="{fill}">&#x{GLYPH[name][0]:X};</text>'


def _line(x1, y1, x2, y2, w, extra=""):
    return f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="#000" stroke-width="{w:.2f}" {extra}/>'


# ------------------------------------------------------------ engraved (Bravura)
def eighth_pair(h1, h2, yl, s, fill="#000"):
    """Two beamed eighths, stems up; h1/h2 are notehead centres, noteheads on y = yl."""
    out = []
    sw = STEM_W * s
    top = yl - STEM_LEN * s
    xs = []
    for hc in (h1, h2):
        nx = hc - HEAD_W / 2 * s
        out.append(glyph("noteheadBlack", nx, yl, s, fill))
        x = nx + STEM_UP_SE[0] * s - sw / 2
        xs.append(x)
        out.append(f'<line x1="{x:.2f}" y1="{yl - STEM_UP_SE[1] * s:.2f}" x2="{x:.2f}" y2="{top:.2f}" stroke="{fill}" stroke-width="{sw:.2f}"/>')
    out.append(f'<rect x="{xs[0] - sw / 2:.2f}" y="{top:.2f}" width="{xs[1] - xs[0] + sw:.2f}" height="{BEAM_T * s:.2f}" fill="{fill}"/>')
    return "".join(out)


def engraved(tok, cx, yl, s, pair_gap=2.4, fill="#000"):
    """One token centred on cx. Noteheads sit on y = yl (the rhythm line); the rest is centred on it."""
    if tok == "q":
        return glyph("noteQuarterUp", cx - HEAD_W / 2 * s, yl, s, fill)
    if tok == "h":
        return glyph("noteHalfUp", cx - HEAD_W / 2 * s, yl, s, fill)
    if tok == "r":
        (x0, _), (x1, _) = GLYPH["restQuarter"][1], GLYPH["restQuarter"][2]
        return glyph("restQuarter", cx - (x0 + x1) / 2 * s, yl, s, fill)
    if tok == "e":
        return eighth_pair(cx - pair_gap / 2 * s, cx + pair_gap / 2 * s, yl, s, fill)
    raise KeyError(tok)


def slots(pattern, x0, W):
    """Beat-proportional layout: (token, centre x of its first beat slot, beat index)."""
    out, b = [], 0
    for t in pattern:
        out.append((t, x0 + (b + 0.5) * W, b))
        b += TOKENS[t]["beats"]
    return out


def engraved_pattern(pattern, x0, yl, s, W, staff=True, timesig=True, fill="#000"):
    """A pattern on a one-line rhythm staff with a 4/4 time signature and final barline.
    Returns (svg, list of beat-centre x positions, right edge)."""
    out = []
    x = x0
    if timesig:
        out.append(glyph("timeSig4", x, yl - s, s, fill))
        out.append(glyph("timeSig4", x, yl + s, s, fill))
        x += 2.6 * s
    for t, cx, _ in slots(pattern, x, W):
        out.append(engraved(t, cx, yl, s, pair_gap=min(2.4, W / s / 2), fill=fill))
    end = x + beats(pattern) * W
    centres = [x + (i + 0.5) * W for i in range(beats(pattern))]
    if staff:
        thick = 0.5 * s
        out.insert(0, _line(x0 - 0.4 * s, yl, end + 0.6 * s + thick, yl, STAFF_W * s * 1.3))
        out.append(_line(end, yl - 2 * s, end, yl + 2 * s, 0.16 * s))
        out.append(f'<rect x="{end + 0.6 * s:.2f}" y="{yl - 2 * s:.2f}" width="{thick:.2f}" height="{4 * s:.2f}" fill="{fill}"/>')
        end += 0.6 * s + thick
    return "".join(out), centres, end


# ------------------------------------------------------------ hand-drawn (stick notation and tracing)
# Shapes are stroke paths, so they can be drawn solid (stick notation), dotted
# (tracing) or both. Heads are ellipses tilted like an engraved notehead.
HEAD_RX, HEAD_RY, HEAD_ROT = 0.66, 0.46, -20


def _rest_path(cx, cy, s):
    """Handwritten quarter rest: a 'Z' with a hook, 3 spaces tall, centred on (cx, cy)."""
    p = [(-0.32, -1.5), (0.38, -0.62), (-0.30, 0.18), (0.40, 0.90)]
    d = "M" + " L".join(f"{cx + x * s:.2f},{cy + y * s:.2f}" for x, y in p)
    d += f" C{cx - 0.30 * s:.2f},{cy + 0.62 * s:.2f} {cx - 0.55 * s:.2f},{cy + 1.30 * s:.2f} {cx + 0.02 * s:.2f},{cy + 1.52 * s:.2f}"
    return d, (cx - 0.32 * s, cy - 1.5 * s)


def hand_parts(tok, cx, yb, s, heads=True, pair_gap=2.4):
    """Return a list of drawable parts for a token whose noteheads (or stick feet) sit on y = yb:
    ("path", d, start_xy) | ("head", hx, hy, filled, start_xy) | ("beam", x1, x2, y, start_xy)."""
    parts = []
    stem_dx = HEAD_RX * 0.92 * s     # stem on the right edge of the head
    top = yb - STEM_LEN * s
    if tok == "r":
        d, st = _rest_path(cx, yb - 1.6 * s if not heads else yb, s)
        return [("path", d, st)]
    if tok in ("q", "h"):
        has_head = heads or tok == "h"   # stick notation keeps the open head of the half note
        sx = cx + stem_dx if has_head else cx
        if has_head:
            parts.append(("head", cx, yb, tok == "q", (cx - HEAD_RX * s, yb)))
        y0 = yb - 0.15 * s if has_head else yb
        parts.append(("path", f"M{sx:.2f},{top:.2f} L{sx:.2f},{y0:.2f}", (sx, top)))
        return parts
    if tok == "e":
        xs = []
        for hc in (cx - pair_gap / 2 * s, cx + pair_gap / 2 * s):
            sx = hc + stem_dx if heads else hc
            xs.append(sx)
            if heads:
                parts.append(("head", hc, yb, True, (hc - HEAD_RX * s, yb)))
            parts.append(("path", f"M{sx:.2f},{top:.2f} L{sx:.2f},{yb - (0.15 * s if heads else 0):.2f}", (sx, top)))
        parts.append(("beam", xs[0], xs[1], top, (xs[0], top)))
        return parts
    raise KeyError(tok)


def hand(tok, cx, yb, s, heads=True, mode="solid", pair_gap=2.4, accent="#000", w=None, start_dots=True):
    """Draw a token by hand. mode: 'solid' (stick notation / model), 'dotted' (tracing), 'faint' (guide)."""
    w = w or 0.24 * s
    colour = "#bbb" if mode == "faint" else "#000"

    def st(width=None, fill="none"):
        if mode == "dotted":
            width = width or w * 0.5
            return (f'stroke="#000" stroke-width="{width:.2f}" stroke-linecap="round" stroke-linejoin="round" '
                    f'fill="{fill}" stroke-dasharray="0 {width * 2.0:.2f}"')
        return f'stroke="{colour}" stroke-width="{width or w:.2f}" stroke-linecap="round" stroke-linejoin="round" fill="{fill}"'

    out, starts = [], []
    for p in hand_parts(tok, cx, yb, s, heads, pair_gap):
        if p[0] == "path":
            out.append(f'<path d="{p[1]}" {st()}/>')
            starts.append(p[2])
        elif p[0] == "head":
            _, hx, hy, filled, sxy = p
            fill = colour if (filled and mode != "dotted") else "none"
            out.append(f'<ellipse cx="{hx:.2f}" cy="{hy:.2f}" rx="{HEAD_RX * s:.2f}" ry="{HEAD_RY * s:.2f}" '
                       f'transform="rotate({HEAD_ROT} {hx:.2f} {hy:.2f})" {st(fill=fill)}/>')
            starts.append(sxy)
        elif p[0] == "beam":
            _, x1, x2, y, sxy = p
            if heads:   # engraved-style thick beam: a band 0.5 space tall
                bw = 0.5 * s
                if mode != "dotted":
                    out.append(f'<rect x="{x1 - w / 2:.2f}" y="{y:.2f}" width="{x2 - x1 + w:.2f}" height="{bw:.2f}" fill="{colour}"/>')
                else:   # dotted outline of the beam, coloured in like the noteheads
                    out.append(f'<rect x="{x1:.2f}" y="{y:.2f}" width="{x2 - x1:.2f}" height="{bw:.2f}" {st()}/>')
                    sxy = None
            else:       # stick notation: one line joining the sticks
                out.append(f'<path d="M{x1:.2f},{y:.2f} L{x2:.2f},{y:.2f}" {st()}/>')
            if sxy:
                starts.append(sxy)
    if mode == "dotted" and start_dots:
        for x, y in starts:
            out.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{w * 0.85:.2f}" fill="{accent}" stroke="#000" stroke-width="{w * 0.18:.2f}"/>')
    return "".join(out)


def stick_pattern(pattern, x0, yb, s, W, mode="solid", accent="#000"):
    out = []
    for t, cx, _ in slots(pattern, x0, W):
        out.append(hand(t, cx, yb, s, heads=False, mode=mode, pair_gap=min(2.4, W / s / 2), accent=accent))
    centres = [x0 + (i + 0.5) * W for i in range(beats(pattern))]
    return "".join(out), centres, x0 + beats(pattern) * W


def hand_pattern(pattern, x0, yb, s, W, mode="solid", accent="#000"):
    out = []
    for t, cx, _ in slots(pattern, x0, W):
        out.append(hand(t, cx, yb, s, heads=True, mode=mode, pair_gap=min(2.4, W / s / 2), accent=accent))
    return "".join(out)
