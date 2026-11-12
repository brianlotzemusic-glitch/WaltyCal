"""Christmas pictures for the colour-by-note set, drawn in code.

Style rules shared by all nine pictures (so they read as one product line):
  * every picture is a hero object on a simple scene, in a rounded frame
  * all outlines are one weight (the renderer strokes every region the same); no thick
    black strokes except small solid "ink" details: stems, eyes, antlers
  * shapes are soft and rounded
  * never more than five colours per picture (one per note in the key); every region is
    big enough for the largest note label (a staff of about 40 x 43 pt)
  * religious content is limited to a plain star; no characters, brands or songs

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


# ---------- pictures ----------
def flakes(pts, r=3.4):
    """Little ink snowflakes drifting through the sky."""
    return [circle(x, y, r) for x, y in pts]


def pine(cx, top, base, hw, tiers=3):
    """A stacked-triangle fir tree: one smooth green shape with soft tiers."""
    parts = []
    h = base - top
    for k in range(tiers):
        t0 = top + h * k * .27
        t1 = top + h * (.5 + k * .25)
        w = hw * (.5 + .5 * k / (tiers - 1)) if tiers > 1 else hw
        parts.append(soft(Polygon([(cx, t0), (cx + w, t1), (cx - w, t1)]), 7))
    return unary_union(parts)


def star_shape(cx, cy, R, r=None):
    r = r or R * .5
    pts = []
    for k in range(10):
        a = math.radians(-90 + k * 36)
        rr = R if k % 2 == 0 else r
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return soft(Polygon(pts), 4)


def tier_shape(cx, top, base, hw, teeth, drop=26):
    pts = [(cx, top), (cx + hw, base - 16)]
    for k in range(teeth * 2 + 1):
        x = cx + hw - 2 * hw * k / (teeth * 2)
        pts.append((x, base if k % 2 == 0 else base - drop))
    pts.append((cx - hw, base - 16))
    return soft(Polygon(pts), 5)


def bow(cx, cy, s=1.0, tails=True):
    """Ribbon bow: two loops, two tails and a knot (one geometry per part)."""
    loops = unary_union([rot(ellipse(cx - 58 * s, cy - 6 * s, 58 * s, 36 * s), -18, (cx, cy)),
                         rot(ellipse(cx + 58 * s, cy - 6 * s, 58 * s, 36 * s), 18, (cx, cy))])
    t = []
    if tails:
        for sg in (-1, 1):
            t.append(rot(P(f"M0 0 L{24 * s} 0 L{34 * s} {90 * s} L{17 * s} {76 * s} L{-2 * s} {96 * s} Z"), 14 * sg, (0, 0)) if sg > 0 else
                     rot(P(f"M0 0 L{-24 * s} 0 L{-34 * s} {90 * s} L{-17 * s} {76 * s} L{2 * s} {96 * s} Z"), 14 * sg, (0, 0)))
    tails_g = mv(unary_union(t), cx, cy) if t else Polygon()
    return soft(unary_union([loops, tails_g, circle(cx, cy, 30 * s)]), 3)


# 1 ------------------------------------------------------------------ tree
def tree():
    layers = [L(FRAME, "blue"), L(hill(440, 10), "white")]
    layers += [L(tier_shape(270, 232, 446, 214, 6, drop=0), "green"), L(tier_shape(270, 152, 330, 150, 5), "green"),
               L(tier_shape(270, 84, 232, 100, 4), "green")]
    layers.append(L(star_shape(270, 52, 54, 27), "yellow"))
    for (x, y, c) in ((160, 400, "red"), (380, 400, "yellow"), (222, 286, "yellow"), (322, 286, "red"), (270, 200, "red")):
        layers.append(L(circle(x, y, 30), c))
    layers.append(L(rrect(30, 380, 116, 470, 6), "yellow"))
    layers.append(L(rrect(424, 390, 510, 470, 6), "red"))
    ink = []
    ink += flakes([(60, 90), (120, 200), (50, 300), (480, 80), (430, 190), (490, 300), (80, 190), (460, 330)])
    return layers, ink


# 2 --------------------------------------------------------------- stocking
def stocking():
    layers = [L(FRAME, "green"), L(rrect(-10, -20, 550, 70, 6), "brown")]
    leg = P("M170 120 L350 120 L350 310 C350 345 380 352 420 362 C470 376 492 416 462 448 C430 478 360 470 318 438 "
            "C262 396 170 372 170 306 Z")
    layers.append(L(soft(leg, 8), "red"))
    layers.append(L(rrect(150, 96, 370, 186, 14), "white"))
    heel = soft(unary_union([ellipse(222, 352, 60, 60)]).intersection(leg), 4)
    toe = soft(ellipse(450, 424, 66, 56, -35).intersection(leg), 4)
    layers += [L(heel, "yellow"), L(toe, "yellow")]
    ink = [stem("M300 100 L300 80", 4)]
    ink += flakes([(70, 170), (90, 300), (60, 420), (460, 170), (480, 300), (80, 470)], 3.4)
    return layers, ink


# 3 ---------------------------------------------------------------- wreath
def wreath():
    cx, cy = 270, 232
    layers = [L(FRAME, "blue")]
    ring = unary_union([Point(cx, cy).buffer(150, quad_segs=48).difference(Point(cx, cy).buffer(72, quad_segs=48))]
                       + [leaf_at(*polar(cx, cy, 112, a), 78, 42, a + 8) for a in range(0, 360, 20)])
    cuts = [LineString([polar(cx, cy, 40, a), polar(cx, cy, 260, a)]) for a in range(0, 360, 45)]
    layers.append(L(Point(cx, cy).buffer(80, quad_segs=48), "white"))
    layers.append(L(ring, "green", cuts))
    for a in (200, 300, 20):
        layers.append(L(circle(*polar(cx, cy, 112, a), 31), "red"))
    for a in (250, 340, 70):
        layers.append(L(circle(*polar(cx, cy, 112, a), 31), "yellow"))
    layers.append(L(bow(cx, 392, 0.9), "red"))
    ink = flakes([(50, 60), (480, 60), (44, 250), (496, 250), (60, 440), (480, 450), (270, 30)])
    return layers, ink


# 4 ---------------------------------------------------------------- reindeer
def reindeer():
    layers = [L(FRAME, "blue"), L(circle(448, 76, 42), "yellow"), L(hill(450, 12), "white")]
    ears = unary_union([rot(ellipse(166, 214, 70, 46), -35, (166, 214)), rot(ellipse(374, 214, 70, 46), 35, (374, 214))])
    layers.append(L(ears, "brown"))
    head = soft(ellipse(270, 290, 112, 140), 10)
    layers.append(L(head, "brown"))
    layers.append(L(ellipse(270, 396, 96, 66).intersection(head), "white"))
    scarf = soft(unary_union([rrect(110, 440, 430, 500, 22), rot(rrect(340, 460, 410, 540, 14), -8, (360, 460))]), 4)
    layers.append(L(scarf, "red"))
    ink = [stem("M222 198 C214 150 196 110 176 70", 9), stem("M206 140 C180 136 160 120 146 98", 7), stem("M196 108 C176 108 160 98 148 84", 6),
           stem("M318 198 C326 150 344 110 364 70", 9), stem("M334 140 C360 136 380 120 394 98", 7), stem("M344 108 C364 108 380 98 392 84", 6),
           eye(220, 286, 10), eye(320, 286, 10), ellipse(270, 362, 24, 16)]
    ink += flakes([(60, 120), (60, 260), (480, 180), (490, 290), (110, 30), (270, 40), (40, 400), (500, 410)])
    return layers, ink


# 5 ------------------------------------------------------------ candy canes
def cane(cx_base, y_base, color, tilt, r=32, band=58, h=300, hook=72):
    """Candy cane: stripes are flat-capped slices swept along a straight shaft and a hooked top."""
    pts = [(0, 0), (0, -h)]
    for k in range(1, 61):
        a = math.radians(180 + 180 * k / 60)
        pts.append((hook + hook * math.cos(a), -h + hook * math.sin(a)))
    pts.append((2 * hook, -h + 40))
    cl = LineString(pts)
    n = int(round(cl.length / band))
    seg = cl.length / n
    pieces = {"white": [], color: []}
    for i in range(n):
        sub = [cl.interpolate(i * seg + seg * s / 14) for s in range(15)]
        g = LineString([(p.x, p.y) for p in sub]).buffer(r, cap_style=2, join_style=1)
        pieces[color if i % 2 == 0 else "white"].append(g)
    return {c: mv(rot(unary_union(gs), tilt, (0, 0)), cx_base, y_base) for c, gs in pieces.items()}


def candy_canes():
    layers = [L(FRAME, "blue"), L(hill(440, 10), "white")]
    left = cane(80, 470, "red", -4)
    right = cane(250, 470, "green", 4)
    for cn in (left, right):
        for c, g in cn.items():
            layers.append(L(g, c))
    layers.append(L(star_shape(468, 330, 54, 28), "yellow"))
    ink = flakes([(60, 60), (200, 40), (300, 30), (420, 260), (500, 240), (490, 400), (40, 120), (400, 380)])
    return layers, ink


# 6 ------------------------------------------------------------------ bells
def bell_shape():
    b = P("M-52 0 C-52 -74 -30 -104 0 -104 C30 -104 52 -74 52 0 C52 28 66 42 74 58 L-74 58 C-66 42 -52 28 -52 0 Z")
    return soft(b, 6)


def bells():
    layers = [L(FRAME, "blue"), L(hill(450, 12), "white")]
    ink = []
    for sgn, cxb in ((1, 190), (-1, 350)):
        g = affinity.scale(mv(bell_shape(), 0, 104), 1.32, 1.32, origin=(0, 0))
        g = mv(rot(g, 14 * sgn, (0, 0)), cxb, 130)
        layers.append(L(g, "yellow"))
        ink.append(mv(rot(circle(0, 218, 13), 14 * sgn, (0, 0)), cxb, 130))
    layers.append(L(leaf_at(250, 446, 170, 86, 188), "green"))
    layers.append(L(leaf_at(290, 446, 170, 86, -8), "green"))
    layers.append(L(bow(270, 100, 0.95, tails=False), "red"))
    for x in (238, 302):
        layers.append(L(circle(x, 442, 34), "red"))
    ink += flakes([(50, 70), (490, 70), (40, 220), (500, 220), (260, 30), (120, 30), (420, 30), (50, 360), (490, 360)])
    return layers, ink


# 7 ---------------------------------------------------------------- candle
def candle():
    layers = [L(FRAME, "blue"), L(circle(270, 150, 150), "yellow")]
    layers.append(L(rrect(190, 196, 350, 400, 10), "red"))
    layers.append(L(soft(P("M270 40 C310 86 322 122 300 168 C288 188 252 188 240 168 C218 122 230 86 270 40 Z"), 4), "orange"))
    layers.append(L(leaf_at(262, 420, 215, 84, 197), "green"))
    layers.append(L(leaf_at(278, 420, 215, 84, -17), "green"))
    for (x, y) in ((236, 440), (304, 440)):
        layers.append(L(circle(x, y, 33), "red"))
    ink = [stem("M270 188 L270 196", 5)]
    ink += flakes([(40, 60), (500, 60), (36, 220), (504, 230), (40, 380), (500, 380), (120, 30), (430, 30)])
    return layers, ink


# 8 ------------------------------------------------------------------ star
def christmas_star():
    layers = [L(FRAME, "purple")]
    layers.append(L(hill(430, 18), "white"))
    layers.append(L(pine(70, 300, 456, 60, 3), "green"))
    layers.append(L(pine(470, 300, 456, 60, 3), "green"))
    big = star_shape(270, 190, 172, 84)
    layers.append(L(big, "yellow"))
    layers.append(L(circle(270, 200, 58), "orange"))
    ink = flakes([(60, 80), (480, 80), (40, 200), (500, 210), (150, 40), (400, 30)])
    return layers, ink


# 9 -------------------------------------------------------------- santa hat
def santa_hat():
    layers = [L(FRAME, "blue"), L(circle(88, 90, 44), "yellow"), L(hill(452, 12), "white")]
    hat = soft(P("M96 360 C100 250 160 140 270 108 C350 86 430 110 456 190 C466 224 462 250 446 360 Z"), 12)
    layers.append(L(hat, "red"))
    layers.append(L(circle(452, 206, 50), "white"))
    layers.append(L(rrect(66, 330, 490, 430, 30), "white"))
    layers.append(L(star_shape(250, 224, 64, 34), "yellow"))
    layers.append(L(leaf_at(262, 382, 150, 72, 190), "green"))
    layers.append(L(leaf_at(288, 382, 150, 72, -10), "green"))
    for x in (250, 300):
        layers.append(L(circle(x, 382, 33), "red"))
    ink = [stem("M96 380 L96 392", 3)]
    ink += flakes([(40, 220), (60, 300), (500, 100), (500, 300), (200, 50), (330, 40), (60, 470), (480, 470)])
    return layers, ink


PICTURES = [
    ("tree", "Christmas Tree", tree),
    ("stocking", "Christmas Stocking", stocking),
    ("wreath", "Holly Wreath", wreath),
    ("reindeer", "Reindeer", reindeer),
    ("canes", "Candy Canes", candy_canes),
    ("bells", "Jingle Bells and Holly", bells),
    ("candle", "Candle and Holly", candle),
    ("star", "Christmas Star", christmas_star),
    ("hat", "Holiday Hat", santa_hat),
]
