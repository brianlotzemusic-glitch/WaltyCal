"""Duskwood Designs Co brand kit: mark, wordmark lockups, shop icon, Etsy cover.

Everything is real vector geometry (text converted to outlines) so the SVGs
work as cut files, print files and web images.
"""
import math, os, random
from shapely.geometry import Polygon, Point, box
from shapely.ops import unary_union
from shapely import affinity
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
os.makedirs(OUT, exist_ok=True)

PLUM_DEEP = "#170f1e"
PLUM = "#2c1b36"
DUSK = "#4a2c55"
CREAM = "#f1e6cf"
GOLD = "#e8c97a"


# ---------- geometry helpers ----------
def pine(x, base, h, w, tiers, rng):
    """Pine silhouette: stacked drooping tiers, trunk stub."""
    pts_l, pts_r = [], []
    top = base - h
    for i in range(tiers):
        t0 = i / tiers
        t1 = (i + 1) / tiers
        y_tip = top + h * 0.92 * t1
        half = w / 2 * (0.25 + 0.75 * t1) * (1 + rng.uniform(-0.08, 0.08))
        y_in = top + h * 0.92 * t1 - h * 0.92 / tiers * 0.45
        inner = half * 0.45
        pts_l += [(x - inner, y_in), (x - half, y_tip)]
        pts_r += [(x + inner, y_in), (x + half, y_tip)]
    trunk_w = max(2.0, w * 0.08)
    poly = [(x, top)] + pts_r + [(x + trunk_w, pts_r[-1][1]), (x + trunk_w, base), (x - trunk_w, base),
                                 (x - trunk_w, pts_l[-1][1])] + pts_l[::-1]
    return Polygon(poly).buffer(0)


def treeline(x0, x1, base, hmin, hmax, rng, density=1.0, scale=None):
    trees, x = [], x0
    while x < x1:
        h = rng.uniform(hmin, hmax) * (scale(x) if scale else 1.0)
        w = h * rng.uniform(0.36, 0.46)
        trees.append(pine(x, base, h, w, rng.randint(4, 6), rng))
        x += w * rng.uniform(0.45, 0.7) / density
    return unary_union(trees)


def crescent(cx, cy, r, offset=(0.38, -0.22)):
    return Point(cx, cy).buffer(r, 128).difference(
        Point(cx + r * offset[0], cy + r * offset[1]).buffer(r * 0.86, 128))


def star(cx, cy, r):
    pts = []
    for i in range(8):
        a = math.pi / 4 * i - math.pi / 2
        rr = r if i % 2 == 0 else r * 0.28
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return Polygon(pts)


def to_d(geom):
    if geom.is_empty:
        return ""
    polys = geom.geoms if geom.geom_type in ("MultiPolygon", "GeometryCollection") else [geom]
    d = []
    for p in polys:
        if p.geom_type != "Polygon":
            continue
        for ring in [p.exterior, *p.interiors]:
            c = list(ring.coords)[:-1]
            d.append("M" + " L".join(f"{x:.2f},{y:.2f}" for x, y in c) + "Z")
    return " ".join(d)


# ---------- text to outlines ----------
class Font:
    def __init__(self, path, wght=None):
        self.f = TTFont(path)
        if wght and "fvar" in self.f:
            from fontTools.varLib.instancer import instantiateVariableFont
            self.f = instantiateVariableFont(self.f, {"wght": wght})
        self.gs = self.f.getGlyphSet()
        self.cmap = self.f.getBestCmap()
        self.upm = self.f["head"].unitsPerEm

    def path(self, text, size, x, y, tracking=0.0):
        """Return (svg path d, advance width) for text with baseline at y."""
        s = size / self.upm
        pen = SVGPathPen(self.gs)
        cx = 0
        hmtx = self.f["hmtx"]
        for ch in text:
            g = self.cmap.get(ord(ch))
            if g is None:
                continue
            tp = TransformPen(pen, (s, 0, 0, -s, x + cx, y))
            self.gs[g].draw(tp)
            cx += hmtx[g][0] * s + tracking * size
        return pen.getCommands(), cx - tracking * size

    def width(self, text, size, tracking=0.0):
        return self.path(text, size, 0, 0, tracking)[1]


FELL = Font(os.path.join(HERE, "fonts/IMFeENsc28P.ttf.ttf"))
CORM = Font(os.path.join(HERE, "fonts/CormorantGaramond.ttf"), wght=600)


# ---------- the mark ----------
def mark_layers(cx, cy, R, seed=7):
    """Circular badge: dusk disc, moon, stars, treeline. Returns dict of geoms."""
    rng = random.Random(seed)
    disc = Point(cx, cy).buffer(R, 256)
    ring = Point(cx, cy).buffer(R, 256).difference(Point(cx, cy).buffer(R * 0.93, 256))
    inner = Point(cx, cy).buffer(R * 0.88, 256)
    trees_far = treeline(cx - R, cx + R, cy + R * 0.62, R * 0.38, R * 0.62, rng, 1.25).intersection(inner)
    rng2 = random.Random(seed + 1)
    valley = lambda x: 0.55 + 0.45 * min(1.0, abs(x - cx) / (R * 0.75))
    trees_near = unary_union([
        treeline(cx - R, cx + R, cy + R * 0.95, R * 0.62, R * 0.92, rng2, 1.0, valley),
        box(cx - R, cy + R * 0.72, cx + R, cy + R)]).intersection(inner)
    moon = crescent(cx + R * 0.22, cy - R * 0.36, R * 0.24)
    stars = unary_union([star(cx - R * 0.42, cy - R * 0.40, R * 0.05), star(cx - R * 0.12, cy - R * 0.58, R * 0.035),
                         star(cx + R * 0.55, cy - R * 0.02, R * 0.03), star(cx - R * 0.58, cy - R * 0.08, R * 0.025)])
    return dict(disc=disc, ring=ring, far=trees_far, near=trees_near, moon=moon, stars=stars)


def mark_svg_color(cx, cy, R, ring=CREAM):
    L = mark_layers(cx, cy, R)
    return (f'<defs><linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0" stop-color="{PLUM_DEEP}"/><stop offset="0.55" stop-color="{PLUM}"/><stop offset="1" stop-color="{DUSK}"/></linearGradient></defs>'
            f'<path fill="url(#sky)" d="{to_d(L["disc"])}"/>'
            f'<path fill="{GOLD}" d="{to_d(L["moon"])}"/><path fill="{CREAM}" d="{to_d(L["stars"])}"/>'
            f'<path fill="#3b2446" d="{to_d(L["far"])}"/><path fill="{PLUM_DEEP}" d="{to_d(L["near"])}"/>'
            f'<path fill="{ring}" d="{to_d(L["ring"])}"/>')


def mark_geom_onecolor(cx, cy, R):
    """Single-ink version: ring + moon + stars + near trees (far trees dropped)."""
    L = mark_layers(cx, cy, R)
    return unary_union([L["ring"], L["moon"], L["stars"], L["near"]])


# ---------- wordmark ----------
def wordmark(x_center, y_base, size, color, sub_color=None):
    sub_color = sub_color or color
    w1 = FELL.width("Duskwood", size, 0.02)
    d1, _ = FELL.path("Duskwood", size, x_center - w1 / 2, y_base, 0.02)
    ss = size * 0.24
    sub = "DESIGNS CO"
    w2 = CORM.width(sub, ss, 0.42)
    y2 = y_base + size * 0.48
    d2, _ = CORM.path(sub, ss, x_center - w2 / 2, y2, 0.42)
    # hairlines either side of the subline
    gap, ln = ss * 0.9, size * 0.9
    yl = y2 - ss * 0.33
    lines = unary_union([box(x_center - w2 / 2 - gap - ln, yl - 1.2, x_center - w2 / 2 - gap, yl + 1.2),
                         box(x_center + w2 / 2 + gap, yl - 1.2, x_center + w2 / 2 + gap + ln, yl + 1.2)])
    return (f'<path fill="{color}" d="{d1}"/><path fill="{sub_color}" d="{d2}"/>'
            f'<path fill="{sub_color}" d="{to_d(lines)}"/>'), max(w1, w2 + 2 * (gap + ln)), y2


def save(name, w, h, body, bg=None):
    rect = f'<rect width="{w}" height="{h}" fill="{bg}"/>' if bg else ""
    with open(os.path.join(OUT, name), "w") as f:
        f.write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">{rect}{body}</svg>')


# 1. Mark alone (color + one-color cream + one-color plum)
save("mark-color.svg", 1000, 1000, mark_svg_color(500, 500, 480))
mg = mark_geom_onecolor(500, 500, 480)
save("mark-cream.svg", 1000, 1000, f'<path fill="{CREAM}" fill-rule="evenodd" d="{to_d(mg)}"/>')
save("mark-plum.svg", 1000, 1000, f'<path fill="{PLUM}" fill-rule="evenodd" d="{to_d(mg)}"/>')

# 2. Stacked logo (mark above wordmark) on light and dark
for nm, bg, ink, sub in (("logo-stacked-light.svg", "#f6f0e4", PLUM, "#6b4a78"), ("logo-stacked-dark.svg", PLUM_DEEP, CREAM, GOLD)):
    body = mark_svg_color(600, 400, 300, CREAM if bg == PLUM_DEEP else PLUM)
    wm, _, _ = wordmark(600, 900, 190, ink, sub)
    save(nm, 1200, 1060, body + wm, bg)

# 3. Horizontal logo
for nm, bg, ink, sub in (("logo-horizontal-light.svg", "#f6f0e4", PLUM, "#6b4a78"), ("logo-horizontal-dark.svg", PLUM_DEEP, CREAM, GOLD)):
    body = mark_svg_color(230, 230, 190, CREAM if bg == PLUM_DEEP else PLUM)
    wm, ww, _ = wordmark(0, 0, 150, ink, sub)
    save(nm, 1500, 460, body + f'<g transform="translate({480 + ww / 2:.1f},245)">{wm}</g>', bg)

# 4. Etsy shop icon (500x500): mark on deep plum
save("shop-icon-500.svg", 500, 500, mark_svg_color(250, 250, 232), PLUM_DEEP)

# 5. Etsy cover photo 3360x840: dusk sky, moon, full-width treeline, wordmark centred
rng = random.Random(3)
W, H = 3360, 840
far = treeline(-60, W + 60, H - 30, 90, 170, rng, 1.3)
near = unary_union([treeline(-80, 1050, H + 10, 300, 470, rng, 1.0),
                    treeline(2330, W + 80, H + 10, 300, 470, rng, 1.0),
                    box(0, H - 40, W, H)])
moon = crescent(2620, 250, 120)
stars = unary_union([star(rng.uniform(80, W - 80), rng.uniform(40, 420), rng.uniform(6, 14)) for _ in range(38)])
wm, _, _ = wordmark(W / 2, 420, 210, CREAM, GOLD)
tag, tw = CORM.path("Dark & whimsical cut files  ·  SVG  ·  DXF  ·  PNG", 46, 0, 0, 0.08)
cover = (f'<defs><linearGradient id="sk" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{PLUM_DEEP}"/>'
         f'<stop offset="0.6" stop-color="{PLUM}"/><stop offset="1" stop-color="{DUSK}"/></linearGradient></defs>'
         f'<rect width="{W}" height="{H}" fill="url(#sk)"/>'
         f'<path fill="{CREAM}" opacity="0.8" d="{to_d(stars)}"/><path fill="{GOLD}" d="{to_d(moon)}"/>'
         f'<path fill="#271a31" d="{to_d(far)}"/><path fill="{PLUM_DEEP}" d="{to_d(near)}"/>'
         f'{wm}<g transform="translate({W / 2 - tw / 2:.1f},610)"><path fill="#c9b6d6" d="{tag}"/></g>')
save("shop-cover-3360x840.svg", W, H, cover)
print("ok")
