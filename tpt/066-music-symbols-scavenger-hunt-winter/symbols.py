"""Music symbols for the scavenger hunt, drawn from Bravura (SMuFL, SIL OFL 1.1) glyphs plus plain rectangles for stems.

Geometry is in staff spaces (1 space = 1/4 em), y up. Every symbol is a list of parts:
  ("g", codepoint, x, y)          a glyph whose origin is at (x, y)
  ("r", x0, y0, x1, y1)           a filled rectangle (stems, the short line under a half rest)
"""
import math
import os
import random
from fontTools.ttLib import TTFont
from fontTools.pens.boundsPen import BoundsPen

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(os.path.dirname(HERE), "fonts")

HEAD_W = 1.18          # width of a notehead in staff spaces (Bravura)
STEM_T = 0.12          # stem thickness
STEM_Y = 0.168         # stem attaches this far above (below) the head centre
STEM_LEN = 3.5

CP = {"clefG": 0xE050, "clefF": 0xE062, "whole": 0xE0A2, "half": 0xE0A3, "black": 0xE0A4, "qrest": 0xE4E5, "hrest": 0xE4E4,
      "repeatR": 0xE041, "fermata": 0xE4C0, "sharp": 0xE262, "flat": 0xE260, "natural": 0xE261, "f": 0xE522, "p": 0xE520,
      "mf": 0xE52D, "mp": 0xE52C, "cresc": 0xE53E, "decresc": 0xE53F, "ts4": 0xE084, "dbl": 0xE031}

# id -> (name, meaning, drawing scale S in px for the scene)
SYMS = {
    "treble": ("Treble clef", "Marks the higher notes. It curls around the G line.", 9.5),
    "bass": ("Bass clef", "Marks the lower notes. Its two dots sit around the F line.", 12),
    "quarter": ("Quarter note", "Lasts 1 beat in 4/4.", 12),
    "half": ("Half note", "Lasts 2 beats in 4/4.", 12),
    "whole": ("Whole note", "Lasts 4 beats in 4/4.", 15),
    "qrest": ("Quarter rest", "Silence for 1 beat.", 12),
    "hrest": ("Half rest", "Silence for 2 beats. It sits on the line.", 15),
    "repeat": ("Repeat sign", "Go back and play the music again.", 11),
    "fermata": ("Fermata", "Hold the note longer than usual.", 16),
    "sharp": ("Sharp", "Raises a note by a half step.", 13),
    "flat": ("Flat", "Lowers a note by a half step.", 13),
    "natural": ("Natural", "Cancels a sharp or a flat.", 13),
    "f": ("Forte (f)", "Play loudly.", 16),
    "p": ("Piano (p)", "Play softly.", 16),
    "mf": ("Mezzo forte (mf)", "Play medium loud.", 15),
    "mp": ("Mezzo piano (mp)", "Play medium soft.", 15),
    "cresc": ("Crescendo", "Get gradually louder.", 17),
    "decresc": ("Decrescendo", "Get gradually softer.", 17),
    "ts44": ("Time signature 4/4", "Four beats in a bar. A quarter note gets one beat.", 12),
    "dbl": ("Double barline", "Marks the end of a section.", 12),
}
ORDER = list(SYMS)
HALO = 3.0             # white halo around every hidden symbol, px


def _bounds():
    f = TTFont(os.path.join(FONTS, "bravura.woff2"))
    gs, cm, upm = f.getGlyphSet(), f.getBestCmap(), f["head"].unitsPerEm
    out = {}
    for cp in CP.values():
        bp = BoundsPen(gs)
        gs[cm[cp]].draw(bp)
        out[cp] = tuple(v / upm * 4 for v in bp.bounds)
    return out


GB = _bounds()


def parts(sym, down=False):
    if sym == "treble": return [("g", CP["clefG"], 0, 0)]
    if sym == "bass": return [("g", CP["clefF"], 0, 0)]
    if sym in ("quarter", "half"):
        head = CP["black"] if sym == "quarter" else CP["half"]
        if down:
            return [("g", head, 0, 0), ("r", 0, -STEM_Y - STEM_LEN, STEM_T, -STEM_Y)]
        return [("g", head, 0, 0), ("r", HEAD_W - STEM_T, STEM_Y, HEAD_W, STEM_Y + STEM_LEN)]
    if sym == "whole": return [("g", CP["whole"], 0, 0)]
    if sym == "qrest": return [("g", CP["qrest"], 0, 0)]
    if sym == "hrest": return [("g", CP["hrest"], 0, 0), ("r", -0.3, -0.13, 1.43, 0.0)]
    if sym == "repeat": return [("g", CP["repeatR"], 0, 0)]
    if sym == "fermata": return [("g", CP["fermata"], 0, 0)]
    if sym in ("sharp", "flat", "natural", "f", "p", "mf", "mp", "cresc", "decresc"): return [("g", CP[sym], 0, 0)]
    if sym == "ts44": return [("g", CP["ts4"], 0, 1), ("g", CP["ts4"], 0, -1)]
    if sym == "dbl": return [("g", CP["dbl"], 0, 0)]
    raise KeyError(sym)


def bbox(pts):
    xs, ys = [], []
    for p in pts:
        if p[0] == "g":
            b = GB[p[1]]
            xs += [p[2] + b[0], p[2] + b[2]]
            ys += [p[3] + b[1], p[3] + b[3]]
        else:
            xs += [p[1], p[3]]
            ys += [p[2], p[4]]
    return min(xs), min(ys), max(xs), max(ys)


def f2(v):
    return f"{v:.3f}".rstrip("0").rstrip(".") if "." in f"{v:.3f}" else f"{v:.3f}"


def svg_parts(pts, S, style):
    out = []
    for p in pts:
        if p[0] == "g":
            out.append(f'<text x="{f2(p[2] * S)}" y="{f2(-p[3] * S)}" font-family="Bravura" font-size="{f2(4 * S)}" {style}>&#x{p[1]:X};</text>')
        else:
            out.append(f'<rect x="{f2(p[1] * S)}" y="{f2(-p[4] * S)}" width="{f2((p[3] - p[1]) * S)}" height="{f2((p[4] - p[2]) * S)}" {style}/>')
    return "".join(out)


def local_box(sym, S, down=False):
    """ink box in px, y down, relative to the glyph origin: (x0, y0, x1, y1)"""
    b = bbox(parts(sym, down))
    return b[0] * S, -b[3] * S, b[2] * S, -b[1] * S


def sym_group(sym, cx, cy, rot, S, down=False, cls="hs", extra=""):
    """A symbol centred (by its ink box) on (cx, cy) and turned by rot degrees. Returns (svg, aabb with halo)."""
    pts = parts(sym, down)
    x0, y0, x1, y1 = local_box(sym, S, down)
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    hw = HALO
    halo = svg_parts(pts, S, f'fill="#fff" stroke="#fff" stroke-width="{2 * hw}" stroke-linejoin="round"')
    ink = svg_parts(pts, S, 'fill="#000"')
    tr = f'translate({f2(cx)} {f2(cy)}) rotate({f2(rot)}) translate({f2(-mx)} {f2(-my)})'
    svg = (f'<g class="{cls}" data-sym="{sym}" data-s="{f2(S)}" data-down="{1 if down else 0}" data-rot="{f2(rot)}" data-cx="{f2(cx)}" data-cy="{f2(cy)}" {extra} '
           f'transform="{tr}"><g class="halo">{halo}</g><g class="ink">{ink}</g></g>')
    return svg, aabb(sym, cx, cy, rot, S, down)


def aabb(sym, cx, cy, rot, S, down=False, grow=HALO):
    x0, y0, x1, y1 = local_box(sym, S, down)
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    a = math.radians(rot)
    xs, ys = [], []
    for px, py in ((x0, y0), (x1, y0), (x1, y1), (x0, y1)):
        dx, dy = px - mx, py - my
        xs.append(cx + dx * math.cos(a) - dy * math.sin(a))
        ys.append(cy + dx * math.sin(a) + dy * math.cos(a))
    return min(xs) - grow, min(ys) - grow, max(xs) + grow, max(ys) + grow


def sample_svg(sym, maxw, maxh, cls="smp", inline=False):
    """The same drawing on its own, scaled to fit maxw x maxh (pt), for lists and tables."""
    S = SYMS[sym][2]
    x0, y0, x1, y1 = local_box(sym, S)
    k = min(1.0, (maxw - 6) / (x1 - x0), (maxh - 6) / (y1 - y0))
    S *= k
    x0, y0, x1, y1 = local_box(sym, S)
    pad = 3
    w, h = x1 - x0 + 2 * pad, y1 - y0 + 2 * pad
    g = (f'<g class="{cls}" data-sym="{sym}" data-s="{f2(S)}" data-down="0" transform="translate({f2(pad - x0)} {f2(pad - y0)})">'
         f'<g class="ink">{svg_parts(parts(sym), S, "fill=" + chr(34) + "#000" + chr(34))}</g></g>')
    return (f'<svg class="sm" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.2f} {h:.2f}" width="{w:.2f}pt" height="{h:.2f}pt" '
            f'style="{"display:inline-block;vertical-align:middle;margin:0 8pt" if inline else "display:block;margin:0 auto"}">{g}</svg>')


def place(counts, seed, W=720, H=450, inset=24, gap=22, skip_boxes=(), keepout=()):
    """Scatter the hidden symbols. counts: list of (sym, n). Returns [(sym, cx, cy, rot, down, S)]. Best-candidate sampling, seeded."""
    rng = random.Random(seed)
    items = []
    for sym, n in counts:
        items += [sym] * n
    items.sort(key=lambda s: -((bbox(parts(s))[2] - bbox(parts(s))[0]) * (bbox(parts(s))[3] - bbox(parts(s))[1])) * SYMS[s][2] ** 2)
    placed = []
    for sym in items:
        S = SYMS[sym][2]
        best = None
        for _ in range(80):
            down = sym in ("quarter", "half") and rng.random() < 0.4
            rot = rng.uniform(-9, 9)
            x0, y0, x1, y1 = local_box(sym, S, down)
            cx = rng.uniform(inset + (x1 - x0) / 2 + 12, W - inset - (x1 - x0) / 2 - 12)
            cy = rng.uniform(inset + (y1 - y0) / 2 + 12, H - inset - (y1 - y0) / 2 - 12)
            bb = aabb(sym, cx, cy, rot, S, down)
            if bb[0] < inset or bb[1] < inset or bb[2] > W - inset or bb[3] > H - inset:
                continue
            if any(bb[0] < o[2] + gap and o[0] < bb[2] + gap and bb[1] < o[3] + gap and o[1] < bb[3] + gap for o in (p[6] for p in placed)):
                continue
            if any(bb[0] < k[2] + 2 and k[0] < bb[2] + 2 and bb[1] < k[3] + 2 and k[1] < bb[3] + 2 for k in keepout):
                continue
            if any(p[0] == sym and math.hypot(p[1] - cx, p[2] - cy) < 110 for p in placed):
                continue
            dmin = min([math.hypot(p[1] - cx, p[2] - cy) for p in placed] or [999])
            if best is None or dmin > best[0]:
                best = (dmin, cx, cy, rot, down, bb)
        if best is None:
            raise SystemExit(f"could not place {sym} in scene seed {seed}")
        placed.append((sym, best[1], best[2], best[3], best[4], S, best[5]))
    placed.sort(key=lambda p: (p[2], p[1]))
    return placed
