"""Music symbols for Color by Music Symbol, drawn as SVG (points, y down).

Level A: dynamics set in Bravura (SMuFL, SIL OFL 1.1), centred by their glyph bounds.
Level B: Italian tempo terms in Source Sans 3 italic (width measured from the font file).
Level C: notation symbols drawn as plain SVG shapes (fermata, repeat sign, hairpins, staccato, accent, slur).
"""
import os
from fontTools.ttLib import TTFont
from fontTools.pens.boundsPen import BoundsPen

FONTS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "fonts")

# ---------------------------------------------------------------- data (id -> (printed form, meaning, gloss))
DYNAMICS = {  # id: (Bravura codepoint, Italian name, key word)
    "pp": (0xE52B, "pianissimo", "very soft"),
    "p": (0xE520, "piano", "soft"),
    "mp": (0xE52C, "mezzo piano", "medium soft"),
    "mf": (0xE52D, "mezzo forte", "medium loud"),
    "f": (0xE522, "forte", "loud"),
    "ff": (0xE52F, "fortissimo", "very loud"),
}
TEMPO = {  # id: (Italian term, key word, bpm range as taught)
    "largo": ("largo", "very slow", "very slow, broad"),
    "adagio": ("adagio", "slow", "slow and calm"),
    "andante": ("andante", "walking speed", "at a walking pace"),
    "moderato": ("moderato", "medium", "a medium speed"),
    "allegro": ("allegro", "fast", "fast and lively"),
    "presto": ("presto", "very fast", "very fast"),
}
SYMBOLS = {  # id: (name, meaning)
    "fermata": ("fermata", "hold the note longer"),
    "repeat": ("repeat sign", "play the music again"),
    "cresc": ("crescendo", "get louder"),
    "decresc": ("decrescendo", "get softer"),
    "staccato": ("staccato", "short and detached"),
    "accent": ("accent", "play the note stronger"),
    "slur": ("slur", "smooth and connected"),
}

DYN_FS = 40.0
TERM_FS = 14.5


def _bravura():
    f = TTFont(os.path.join(FONTS, "bravura.woff2"))
    gs, cm = f.getGlyphSet(), f.getBestCmap()
    out = {}
    for k, (cp, _, _) in DYNAMICS.items():
        bp = BoundsPen(gs)
        gs[cm[cp]].draw(bp)
        out[k] = bp.bounds  # x0, y0, x1, y1 in 1/1000 em, y up
    return out


def _term_widths():
    f = TTFont(os.path.join(FONTS, "source-sans-3-latin-400-italic.woff2"))
    cm, hm = f.getBestCmap(), f["hmtx"]
    upm = f["head"].unitsPerEm
    return {k: sum(hm[cm[ord(c)]][0] for c in v[0]) / upm * TERM_FS for k, v in TEMPO.items()}


BOUNDS = _bravura()
TERM_W = _term_widths()


def box(level):
    """(w, h) of the largest symbol of a level, in pt (before the gen.py margin)."""
    if level == "A":
        w = max((b[2] - b[0]) for b in BOUNDS.values()) * DYN_FS / 1000
        h = max((b[3] - b[1]) for b in BOUNDS.values()) * DYN_FS / 1000
        return round(w + 4, 1), round(h + 4, 1)
    if level == "B":
        return round(max(TERM_W.values()) + 4, 1), 20.0
    return 42.0, 33.0


def dynamic_svg(sym, cx, cy, fs=DYN_FS):
    cp = DYNAMICS[sym][0]
    x0, y0, x1, y1 = BOUNDS[sym]
    x = cx - (x0 + x1) / 2 * fs / 1000
    y = cy + (y0 + y1) / 2 * fs / 1000
    return f'<text x="{x:.2f}" y="{y:.2f}" font-family="Bravura" font-size="{fs}" fill="#000">&#x{cp:X};</text>'


def term_svg(sym, cx, cy, fs=TERM_FS):
    w = TERM_W[sym] * fs / TERM_FS
    return (f'<text x="{cx - w / 2:.2f}" y="{cy + fs * .32:.2f}" font-family="Source Sans 3" font-style="italic" '
            f'font-size="{fs}" fill="#000">{TEMPO[sym][0]}</text>')


def _head(x, y):
    return f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="6.6" ry="4.9" transform="rotate(-20 {x:.1f} {y:.1f})" fill="#000"/>'


def _ln(x0, y0, x1, y1, w=2.4):
    return f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" y2="{y1:.1f}" stroke="#000" stroke-width="{w}" stroke-linecap="round"/>'


def symbol_art_svg(sym, cx, cy, k=1.0):
    """Level C symbols. k scales the drawing (reference page)."""
    def X(dx): return cx + dx * k
    def Y(dy): return cy + dy * k
    sw = 2.4 * k
    if sym == "fermata":
        return (f'<path d="M{X(-19):.1f} {Y(9):.1f} C{X(-19):.1f} {Y(-15):.1f} {X(19):.1f} {Y(-15):.1f} {X(19):.1f} {Y(9):.1f}" fill="none" '
                f'stroke="#000" stroke-width="{3 * k:.1f}" stroke-linecap="round"/><circle cx="{X(0):.1f}" cy="{Y(3):.1f}" r="{3.4 * k:.1f}" fill="#000"/>')
    if sym == "repeat":
        out = "".join(_ln(X(-22), Y(dy), X(22), Y(dy), .9 * k) for dy in (-13, -6.5, 0, 6.5, 13))
        out += _ln(X(2), Y(-13), X(2), Y(13), 1.8 * k) + _ln(X(8), Y(-13), X(8), Y(13), 4.6 * k)
        out += f'<circle cx="{X(-6):.1f}" cy="{Y(-3.2):.1f}" r="{2.5 * k:.1f}" fill="#000"/><circle cx="{X(-6):.1f}" cy="{Y(3.2):.1f}" r="{2.5 * k:.1f}" fill="#000"/>'
        return out
    if sym == "cresc":
        return _ln(X(-20), Y(0), X(20), Y(-11), sw) + _ln(X(-20), Y(0), X(20), Y(11), sw)
    if sym == "decresc":
        return _ln(X(-20), Y(-11), X(20), Y(0), sw) + _ln(X(-20), Y(11), X(20), Y(0), sw)
    if sym == "staccato":
        return (_head(X(0), Y(2)).replace('rx="6.6" ry="4.9"', f'rx="{6.6 * k:.1f}" ry="{4.9 * k:.1f}"') + _ln(X(-6.2), Y(3), X(-6.2), Y(15), 1.9 * k)
                + f'<circle cx="{X(0):.1f}" cy="{Y(-11):.1f}" r="{2.8 * k:.1f}" fill="#000"/>')
    if sym == "accent":
        return (_head(X(0), Y(11)).replace('rx="6.6" ry="4.9"', f'rx="{6.6 * k:.1f}" ry="{4.9 * k:.1f}"') + _ln(X(6.2), Y(10), X(6.2), Y(-5), 1.9 * k)
                + f'<polyline points="{X(-8):.1f},{Y(-15):.1f} {X(8):.1f},{Y(-11):.1f} {X(-8):.1f},{Y(-7):.1f}" fill="none" stroke="#000" '
                f'stroke-width="{2.2 * k:.1f}" stroke-linecap="round" stroke-linejoin="round"/>')
    if sym == "slur":
        out = ""
        for dx, dy in ((-13, 3), (13, -2)):
            out += _head(X(dx), Y(dy)).replace('rx="6.6" ry="4.9"', f'rx="{6.6 * k:.1f}" ry="{4.9 * k:.1f}"') + _ln(X(dx - 6.2), Y(dy), X(dx - 6.2), Y(dy + 14), 1.9 * k)
        out += (f'<path d="M{X(-13):.1f} {Y(-5):.1f} Q{X(0):.1f} {Y(-22):.1f} {X(13):.1f} {Y(-10):.1f}" fill="none" stroke="#000" '
                f'stroke-width="{2 * k:.1f}" stroke-linecap="round"/>')
        return out
    raise KeyError(sym)


def symbol_svg(level, sym, cx, cy):
    if level == "A":
        return dynamic_svg(sym, cx, cy)
    if level == "B":
        return term_svg(sym, cx, cy)
    return symbol_art_svg(sym, cx, cy)
