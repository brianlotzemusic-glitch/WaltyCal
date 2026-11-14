"""Winter pictures for the colour-by-music-symbol set, drawn in code.

Style rules shared by all nine pictures (so they read as one product line):
  * every picture is a hero object on a simple scene, in a rounded frame
  * all outlines are one weight (the renderer strokes every region the same); no thick
    black strokes except small solid "ink" details: stems, eyes, antlers
  * shapes are soft and rounded
  * never more than five colours per picture (one per symbol in the key); every region is
    big enough for the largest symbol label (about 70 x 34 pt)
  * winter and secular only (snowman, mittens, penguin, cocoa, igloo, snowflake, pine tree, hat, skate);
    no holiday symbols, characters, brands or songs

Each picture is a list of layers in painter's order (bottom first). A layer is a shapely
geometry with a colour name; optional `cuts` split its visible part into more regions.
`ink` shapes are pre-printed black details (not regions). Coordinates are PostScript
points, y pointing down, on a W x H canvas.
"""
import math
import re
from shapely.geometry import Point, Polygon, LineString, box
from shapely import affinity
from shapely.ops import unary_union

W, H = 540, 500
OUTLINE = 1.6          # matches the stroke the renderer draws round every region


# ---------- geometry helpers ----------
def circle(cx, cy, r):
    return Point(cx, cy).buffer(r, quad_segs=32)


def ellipse(cx, cy, rx, ry, rot=0):
    e = affinity.scale(Point(0, 0).buffer(1, quad_segs=48), rx, ry)
    if rot:
        e = affinity.rotate(e, rot, origin=(0, 0))
    return affinity.translate(e, cx, cy)


def rrect(x0, y0, x1, y1, r):
    return box(x0 + r, y0 + r, x1 - r, y1 - r).buffer(r, quad_segs=12)


def _bez(p0, p1, p2, p3, n=22):
    out = []
    for k in range(1, n + 1):
        t = k / n
        u = 1 - t
        out.append((u ** 3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t ** 3 * p3[0],
                    u ** 3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t ** 3 * p3[1]))
    return out


def path_points(d):
    """Sample an SVG-style path (absolute M L C Q Z only) into a list of points."""
    toks = re.findall(r"[MLCQZ]|-?\d+\.?\d*", d)
    pts, i, cmd, cur = [], 0, None, (0, 0)
    while i < len(toks):
        t = toks[i]
        if t in "MLCQZ":
            cmd = t
            i += 1
            if cmd == "Z":
                continue
        nums = lambda k: [float(x) for x in toks[i:i + k]]
        if cmd == "M" or cmd == "L":
            x, y = nums(2)
            i += 2
            cur = (x, y)
            pts.append(cur)
            cmd = "L"
        elif cmd == "C":
            a = nums(6)
            i += 6
            pts += _bez(cur, (a[0], a[1]), (a[2], a[3]), (a[4], a[5]))
            cur = (a[4], a[5])
        elif cmd == "Q":
            a = nums(4)
            i += 4
            c1 = (cur[0] + 2 / 3 * (a[0] - cur[0]), cur[1] + 2 / 3 * (a[1] - cur[1]))
            c2 = (a[2] + 2 / 3 * (a[0] - a[2]), a[3] + 2 / 3 * (a[1] - a[3]))
            pts += _bez(cur, c1, c2, (a[2], a[3]))
            cur = (a[2], a[3])
    return pts


def P(d):
    """Closed filled shape from path data."""
    return Polygon(path_points(d)).buffer(0)


def S(d, w=OUTLINE):
    """Thin ink line (same weight as the outline) from path data."""
    return LineString(path_points(d)).buffer(w / 2, quad_segs=6)


def line(d):
    return LineString(path_points(d))


def soft(g, r=6):
    """Round off corners: opening rounds convex corners, closing rounds concave ones."""
    return g.buffer(-r, quad_segs=10).buffer(2 * r, quad_segs=10).buffer(-r, quad_segs=10)


def stem(d, w=5.5):
    """Small solid black stem or curl."""
    return LineString(path_points(d)).buffer(w / 2, quad_segs=8)


def dot(cx, cy, r=6.5):
    return circle(cx, cy, r)


def eye(cx, cy, r=8.5):
    """Black eye with a small white highlight (a hole in the ink)."""
    hr = min(r * .3, 6.0)          # small enough that the hole never becomes a colouring space
    return circle(cx, cy, r).difference(circle(cx + r * .32, cy - r * .32, hr))


def rot(g, a, origin):
    return affinity.rotate(g, a, origin=origin)


def mv(g, dx, dy):
    return affinity.translate(g, dx, dy)


def mirror(g, cx=W / 2):
    return affinity.scale(g, -1, 1, origin=(cx, 0))


def sym(g, cx=W / 2):
    return unary_union([g, mirror(g, cx)])


def sector(cx, cy, r0, r1, a0, a1, n=30):
    pts = []
    for i in range(n + 1):
        a = math.radians(a0 + (a1 - a0) * i / n)
        pts.append((cx + r1 * math.cos(a), cy + r1 * math.sin(a)))
    for i in range(n, -1, -1):
        a = math.radians(a0 + (a1 - a0) * i / n)
        pts.append((cx + r0 * math.cos(a), cy + r0 * math.sin(a)))
    return Polygon(pts)


def polar(cx, cy, r, a):
    return (cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a)))


def tube(centre_pts, radii, n=60):
    """Smooth tapering tube swept along a centre line (list of points) with radii list."""
    cl = LineString(centre_pts)
    parts = []
    for k in range(n + 1):
        t = k / n
        p = cl.interpolate(t, normalized=True)
        # piecewise-linear radius along the line
        x = t * (len(radii) - 1)
        j = min(int(x), len(radii) - 2)
        r = radii[j] + (radii[j + 1] - radii[j]) * (x - j)
        parts.append(circle(p.x, p.y, r))
    return unary_union(parts)


FRAME = rrect(0, 0, W, H, 28)


def L(geom, color, cuts=None):
    return {"geom": geom, "color": color, "cuts": cuts or []}


# ---------- shared scene pieces ----------
def hill(y, amp=14, left=-30, right=570):
    """Rolling ground, filled down to the bottom of the frame."""
    return P(f"M{left} {y + amp * .3} C 90 {y - amp} 200 {y - amp} 290 {y - amp * .1} "
             f"C 370 {y + amp * .7} 450 {y - amp * .9} {right} {y - amp * .2} L{right} 530 L{left} 530 Z")


def leaf_shape(length, width, bend=0.0):
    """Pointed leaf lying along +x from (0,0) to (length,0), with an optional bend."""
    h = width / 2
    return P(f"M0 0 C {length * .18} {-h * 1.05 - bend} {length * .62} {-h * 1.15 - bend} {length} 0 "
             f"C {length * .62} {h * 1.15 - bend} {length * .18} {h * 1.05 - bend} 0 0 Z")


def leaf_at(x, y, length, width, ang, bend=0.0):
    return rot(mv(leaf_shape(length, width, bend), x, y), ang, (x, y))


def scallops(cx, cy, r, n, rb, phase=0.0):
    return unary_union([circle(*polar(cx, cy, r, phase + k * 360 / n), rb) for k in range(n)])




# ---------- winter pictures ----------
def flake(cx, cy, r, w=2.6):
    """Small six-armed snowflake drawn as ink strokes."""
    parts = []
    for k in range(3):
        a = math.radians(90 + 60 * k)
        p0 = (cx - r * math.cos(a), cy - r * math.sin(a))
        p1 = (cx + r * math.cos(a), cy + r * math.sin(a))
        parts.append(LineString([p0, p1]).buffer(w / 2, quad_segs=4))
    return unary_union(parts)


def flakes(pts, r=9):
    return [flake(x, y, r) for x, y in pts]


# 1 ------------------------------------------------------------------ snowman
def snowman():
    layers = [L(FRAME, "blue"), L(hill(440, 10), "white")]
    layers.append(L(circle(270, 410, 100), "white"))
    layers.append(L(circle(270, 300, 90), "white"))
    layers.append(L(circle(270, 168, 76), "white"))
    hat = unary_union([rrect(218, 14, 322, 100, 10), rrect(190, 86, 350, 112, 8)])
    layers.append(L(hat, "purple"))
    scarf = unary_union([rrect(184, 226, 356, 270, 18), rrect(312, 258, 356, 350, 14)])
    layers.append(L(scarf, "red"))
    ink = [circle(248, 148, 6.5), circle(292, 148, 6.5), Polygon([(270, 160), (320, 170), (270, 178)]),
           circle(270, 304, 6), circle(270, 340, 6), circle(270, 394, 6), circle(270, 436, 6)]
    ink += [S("M184 290 L96 226", 6), S("M120 240 L108 194", 4.5), S("M150 260 L138 216", 4.5),
            S("M356 290 L444 226", 6), S("M420 240 L432 194", 4.5)]
    ink += flakes([(70, 90), (460, 70), (60, 360), (484, 330), (140, 40)], 12)
    return layers, ink


# 2 ------------------------------------------------------------------ mittens
def mittens():
    layers = [L(FRAME, "blue"), L(hill(450, 10), "white")]
    ink = []

    def one(body_c, band_c, mirror_it):
        body = soft(unary_union([rrect(40, 50, 190, 260, 62), ellipse(206, 190, 34, 62, 24)]), 5)
        band = rrect(40, 50, 190, 260, 62).intersection(box(0, 138, 600, 190))
        cuff = rrect(30, 252, 200, 336, 12)
        cut = LineString([(115, 240), (115, 350)])
        gs = [(body, body_c, []), (band, band_c, []), (cuff, "white", [cut])]
        res = []
        for g, c, cuts in gs:
            gg = rot(g, -8, (115, 300))
            cc = [rot(x, -8, (115, 300)) for x in cuts]
            if mirror_it:
                gg = mirror(gg)
                cc = [mirror(x) for x in cc]
            res.append(L(gg, c, cc))
        return res
    layers += one("red", "green", False) + one("purple", "green", True)
    ink += flakes([(250, 70), (290, 110), (270, 40), (60, 30), (490, 30), (250, 380), (290, 420), (260, 460)], 11)
    return layers, ink


# 3 ------------------------------------------------------------------ penguin
def penguin():
    layers = [L(FRAME, "blue"), L(hill(452, 10), "white")]
    body = soft(rrect(112, 52, 428, 456, 158), 4)
    layers.append(L(body, "black"))
    layers.append(L(body.intersection(ellipse(270, 360, 250, 170)).intersection(box(0, 220, 600, 600)), "white"))
    layers.append(L(ellipse(200, 458, 70, 30), "orange"))
    layers.append(L(ellipse(340, 458, 70, 30), "orange"))
    layers.append(L(rot(ellipse(112, 292, 40, 106), -12, (112, 292)), "black"))
    layers.append(L(rot(ellipse(428, 292, 40, 106), 12, (428, 292)), "black"))
    scarf = unary_union([rrect(120, 196, 420, 246, 22), rrect(346, 232, 396, 330, 14)])
    layers.append(L(scarf, "red"))
    ink = [circle(246, 118, 9).difference(circle(249, 115, 3)), circle(294, 118, 9).difference(circle(297, 115, 3)),
           Polygon([(270, 130), (286, 144), (270, 158), (254, 144)])]
    ink += flakes([(60, 60), (480, 60), (40, 230), (500, 240), (270, 30)], 12)
    return layers, ink


# 4 ------------------------------------------------------------- cocoa mug
def cocoa():
    layers = [L(FRAME, "blue"), L(hill(430, 8), "gray")]
    layers.append(L(ellipse(384, 318, 74, 78), "brown"))
    mug = P("M146 210 L388 210 L378 396 Q376 436 338 436 L196 436 Q158 436 156 396 Z")
    layers.append(L(mug, "red"))
    layers.append(L(mug.intersection(box(0, 290, 600, 356)), "white"))
    layers.append(L(ellipse(267, 214, 122, 30), "brown"))
    layers.append(L(rrect(170, 152, 262, 202, 20), "white"))
    layers.append(L(rrect(276, 146, 368, 196, 20), "white"))
    ink = [S("M206 118 C 180 90 232 66 206 36", 5), S("M270 112 C 244 84 296 60 270 30", 5), S("M334 118 C 308 90 360 66 334 36", 5)]
    ink += flakes([(60, 90), (480, 100), (60, 300), (490, 330), (440, 40)], 12)
    return layers, ink


# 5 ------------------------------------------------------------------ igloo
def igloo():
    layers = [L(FRAME, "blue"), L(circle(110, 100, 56), "yellow"), L(hill(412, 8), "gray")]
    dome = circle(290, 420, 214).intersection(box(0, 0, 600, 420))
    cuts = [LineString([(0, 290), (600, 290)]), LineString([(290, 150), (290, 290)])]
    layers.append(L(dome, "white", cuts))
    door = unary_union([box(236, 360, 344, 420), circle(290, 360, 54)])
    layers.append(L(door, "brown"))
    ink = flakes([(480, 70), (400, 40), (60, 230), (500, 200), (200, 50)], 12)
    return layers, ink


# 6 --------------------------------------------------------- snowflake medallion
def snowflake():
    cx, cy = 270, 250
    layers = [L(FRAME, "blue")]
    cols = ["white", "purple", "green"]
    for k in range(12):
        layers.append(L(sector(cx, cy, 150, 236, k * 30, (k + 1) * 30), cols[k % 3]))
    layers.append(L(circle(cx, cy, 150), "gray"))
    ink = []
    for k in range(6):
        a = 90 + 60 * k
        e = polar(cx, cy, 128, a)
        ink.append(S(f"M{cx} {cy} L{e[0]:.1f} {e[1]:.1f}", 5))
        for f, ln in ((.45, 34), (.75, 28)):
            b = polar(cx, cy, 128 * f, a)
            for da in (-45, 45):
                e2 = polar(b[0], b[1], ln, a + da)
                ink.append(S(f"M{b[0]:.1f} {b[1]:.1f} L{e2[0]:.1f} {e2[1]:.1f}", 4))
    ink += flakes([(40, 40), (500, 40), (40, 460), (500, 460)], 12)
    return layers, ink


# 7 ------------------------------------------------------------------ pine tree
def pine():
    layers = [L(FRAME, "blue"), L(circle(450, 90, 50), "yellow"), L(hill(440, 10), "white")]
    layers.append(L(rrect(214, 380, 326, 472, 8), "brown"))
    ink = []
    for apex, base, half, f in ((150, 404, 196, 0.0), (40, 250, 130, .58)):
        tier = soft(Polygon([(270, apex), (270 + half, base), (270 - half, base)]), 6)
        layers.append(L(tier, "green"))
        if f:
            layers.append(L(tier.intersection(box(0, 0, 600, apex + (base - apex) * f)), "white"))
    ink += flakes([(60, 70), (110, 210), (480, 230), (60, 320), (490, 360), (170, 30)], 12)
    return layers, ink


# 8 ------------------------------------------------------------------ winter hat
def hat():
    layers = [L(FRAME, "blue"), L(hill(446, 10), "white")]
    dome = circle(270, 300, 176).intersection(box(0, 0, 600, 300))
    layers.append(L(dome, "red"))
    layers.append(L(dome.intersection(box(0, 196, 600, 252)), "green"))
    layers.append(L(rrect(88, 296, 452, 384, 20), "white", [LineString([(208, 280), (208, 400)]), LineString([(332, 280), (332, 400)])]))
    layers.append(L(circle(270, 108, 52), "yellow"))
    ink = flakes([(50, 60), (490, 60), (50, 250), (490, 250), (60, 420), (480, 420)], 12)
    return layers, ink


# 9 ------------------------------------------------------------------ ice skate
def skate():
    layers = [L(FRAME, "blue"), L(hill(440, 8), "white")]
    boot = soft(unary_union([rrect(170, 44, 314, 330, 22), rrect(170, 250, 456, 350, 48)]), 6)
    layers.append(L(boot, "red"))
    layers.append(L(rrect(160, 36, 324, 112, 26), "white"))
    layers.append(L(rrect(166, 342, 458, 392, 12), "brown"))
    layers.append(L(rrect(150, 390, 480, 440, 20), "gray"))
    ink = []
    ink += [circle(x, y, 4.2) for x, y in ((226, 140), (258, 140), (226, 176), (258, 176), (226, 212), (258, 212))]
    ink += flakes([(70, 80), (470, 80), (60, 250), (500, 190), (100, 340), (500, 330)], 12)
    return layers, ink


PICTURES = [
    ("snowman", "Snowman", snowman),
    ("mittens", "Mittens", mittens),
    ("penguin", "Penguin", penguin),
    ("cocoa", "Cocoa Mug", cocoa),
    ("igloo", "Igloo", igloo),
    ("snowflake", "Snowflake", snowflake),
    ("pine", "Snowy Pine Tree", pine),
    ("hat", "Winter Hat", hat),
    ("skate", "Ice Skate", skate),
]
