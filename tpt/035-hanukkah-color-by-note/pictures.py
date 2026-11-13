"""Hanukkah pictures for the colour-by-note set, drawn in code.

Style rules shared by all nine pictures (so they read as one product line):
  * every picture is a hero object on a simple scene, in a rounded frame
  * all outlines are one weight (the renderer strokes every region the same); no thick
    black strokes except small solid "ink" details: stems, eyes, antlers
  * shapes are soft and rounded
  * never more than five colours per picture (one per note in the key); every region is
    big enough for the largest note label (a staff of about 40 x 43 pt)
  * Hanukkah symbols only (menorah with nine branches, dreidel, Star of David, oil lamp, olive branch);
    nothing from other holidays; no characters, brands or songs

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



# ---------- Hanukkah shapes ----------
def hexagram(cx, cy, R):
    up = Polygon([polar(cx, cy, R, a) for a in (-90, 30, 150)])
    dn = Polygon([polar(cx, cy, R, a) for a in (90, 210, 330)])
    return up.union(dn)


def hex_parts(cx, cy, R):
    """Inner hexagon and the six points of a point-up hexagram."""
    ri = R / math.sqrt(3)
    hexa = Polygon([polar(cx, cy, ri, a) for a in range(-60, 300, 60)])
    pts = []
    for k in range(6):
        a = -90 + 60 * k
        pts.append(Polygon([polar(cx, cy, R, a), polar(cx, cy, ri, a - 30), polar(cx, cy, ri, a + 30)]))
    return hexa, pts


def flame(cx, base, h=44, w=26):
    """Solid ink flame (teardrop) standing on y=base."""
    return P(f"M{cx} {base - h} C {cx + w * .55} {base - h * .55} {cx + w * .6} {base - 2} {cx} {base - 2} "
             f"C {cx - w * .6} {base - 2} {cx - w * .55} {base - h * .55} {cx} {base - h} Z")


def twinkle(pts, r=3.4):
    return [circle(x, y, r) for x, y in pts]


def candle_row(candles, ytop, ybar, shamash_top, cw=46, step=56, cx=270):
    """Nine candles on a bar: returns (list of (x, top, bottom)), shamash is the middle, raised one."""
    out = []
    for k in range(-4, 5):
        x = cx + k * step
        if k == 0:
            out.append((x, shamash_top, ybar - 58))
        else:
            out.append((x, ytop, ybar))
    return out


# 1 / 9 --------------------------------------------------------------- menorah
def menorah_scene(night=False):
    base_c, can_c, sha_c = ("yellow", "orange", "white") if not night else ("orange", "white", "yellow")
    layers = [L(FRAME, "blue"), L(hill(456, 8), "gray" if night else "white")]
    ink = []
    bar = rrect(24, 336, 516, 382, 12)
    holder = rrect(236, 276, 304, 346, 8)
    stand = P("M246 372 L294 372 L300 424 L240 424 Z")
    foot = rrect(176, 418, 364, 470, 14)
    layers.append(L(unary_union([bar, holder, stand, foot]), base_c))
    for k in range(-4, 5):
        x = 270 + k * 56
        if k == 0:
            layers.append(L(box(x - 23, 150, x + 23, 282), sha_c))
            ink.append(flame(x, 148, 46, 28))
        else:
            layers.append(L(box(x - 23, 206, x + 23, 340), can_c))
            ink.append(flame(x, 204, 42, 26))
    if night:
        layers.append(L(circle(86, 82, 48), "yellow"))
        ink += twinkle([(180, 50), (250, 90), (400, 50), (470, 100), (500, 190), (40, 200), (130, 160)])
    else:
        ink += twinkle([(60, 60), (150, 100), (400, 60), (480, 110), (500, 200), (40, 200), (110, 150), (270, 60)])
    return layers, ink


def menorah():
    return menorah_scene(False)


def menorah_night():
    return menorah_scene(True)


# dreidel (side view): ink handle, shoulders, body, tapering point
def dreidel_parts(cx, top, w, h_sh, h_body, h_cone, cols, cuts=False, tilt=0.0, handle=60):
    c1, c2, c3 = cols
    y1, y2, y3 = top + h_sh, top + h_sh + h_body, top + h_sh + h_body + h_cone
    shoulder = soft(Polygon([(cx - w * .26, top), (cx + w * .26, top), (cx + w / 2, y1), (cx - w / 2, y1)]), 3)
    body = box(cx - w / 2, y1, cx + w / 2, y2)
    cone = soft(Polygon([(cx - w / 2, y2), (cx + w / 2, y2), (cx, y3)]), 3)
    cs = [LineString([(cx - w * .22, y1 - 5), (cx - w * .22, y2 + 5)]), LineString([(cx + w * .22, y1 - 5), (cx + w * .22, y2 + 5)])] if cuts else []
    ink = [stem(f"M{cx} {top + 2} L{cx} {top - handle}", 11), circle(cx, top - handle - 4, 11)]
    parts = [L(shoulder, c1), L(body, c2, cs), L(cone, c3)]
    o = (cx, y2)
    if tilt:
        parts = [{"geom": rot(p["geom"], tilt, o), "color": p["color"], "cuts": [rot(c, tilt, o) for c in p["cuts"]]} for p in parts]
        ink = [rot(g, tilt, o) for g in ink]
    return parts, ink


# 2 ------------------------------------------------------------------ dreidel
def dreidel():
    layers = [L(FRAME, "blue"), L(hill(450, 12), "white")]
    parts, ink = dreidel_parts(270, 118, 270, 64, 160, 150, ("orange", "yellow", "orange"), cuts=True, handle=68)
    layers += parts
    ink += [S("M92 220 C60 270 70 340 100 380", 3.4), S("M448 220 C480 270 470 340 440 380", 3.4)]
    ink += twinkle([(70, 80), (480, 80), (150, 40), (400, 36), (500, 400), (40, 440)])
    return layers, ink


# 3 -------------------------------------------------------------- Star of David
def star_of_david():
    cx, cy, R = 270, 250, 208
    hexa, pts = hex_parts(cx, cy, R)
    layers = [L(FRAME, "blue")]
    for k, p in enumerate(pts):
        layers.append(L(p, "yellow" if k % 2 == 0 else "orange"))
    layers.append(L(hexa, "white"))
    ink = twinkle([(50, 50), (490, 50), (40, 250), (500, 250), (50, 450), (490, 450), (270, 22), (270, 478)])
    return layers, ink


# 4 -------------------------------------------------------- oil jar + olive branch
def oil_jar():
    layers = [L(FRAME, "blue"), L(hill(458, 8), "white")]
    body = ellipse(270, 340, 118, 112)
    neck = rrect(226, 190, 314, 280, 10)
    jar = soft(unary_union([body, neck]), 10)
    layers.append(L(jar, "yellow"))
    layers.append(L(jar.intersection(box(0, 330, 540, 384)), "orange"))
    layers.append(L(rrect(206, 168, 334, 214, 14), "orange"))
    layers.append(L(leaf_at(152, 370, 130, 100, 190), "green"))
    layers.append(L(leaf_at(388, 370, 130, 100, -10), "green"))
    ink = [flame(270, 164, 74, 38), stem("M270 168 L270 150", 4)]
    ink.append(S("M386 270 C434 262 446 330 400 372", 9))
    ink += twinkle([(60, 60), (150, 100), (400, 60), (480, 110), (500, 200), (40, 200)])
    return layers, ink


# 5 -------------------------------------------------------------- three dreidels
def three_dreidels():
    layers = [L(FRAME, "blue"), L(hill(452, 12), "gray")]
    ink = []
    sets = [(100, 150, -9, ("orange", "yellow", "white")), (270, 110, 0, ("yellow", "white", "orange")), (440, 150, 9, ("white", "orange", "yellow"))]
    for cx, top, tilt, cols in sets:
        p, i = dreidel_parts(cx, top, 152, 60, 84, 112, cols, tilt=tilt, handle=40)
        layers += p
        ink += i
    ink += twinkle([(40, 60), (200, 40), (350, 40), (500, 60), (190, 240), (360, 250), (30, 460), (510, 470)])
    return layers, ink


# 6 ----------------------------------------------------------- menorah in the window
def window():
    layers = [L(FRAME, "gray")]
    arch = unary_union([rrect(56, 150, 484, 480, 8), circle(270, 160, 214).intersection(box(0, 0, 540, 200))])
    layers.append(L(arch, "white"))
    pane = unary_union([box(120, 170, 420, 424), circle(270, 160, 150).intersection(box(0, 0, 540, 180))])
    layers.append(L(pane, "blue"))
    layers.append(L(circle(270, 338, 120).intersection(pane), "orange"))
    layers.append(L(rrect(40, 424, 500, 488, 10), "yellow"))
    ink = [box(124, 392, 416, 424)]
    for k in range(-4, 5):
        x = 270 + k * 28
        top = 262 if k == 0 else 318
        ink.append(box(x - 6, top, x + 6, 396))
        ink.append(flame(x, top - 2, 28, 16))
    ink.append(box(256, 380, 284, 396))
    ink += twinkle([(40, 40), (500, 40), (40, 330), (500, 330), (270, 30), (150, 70), (390, 70)])
    return layers, ink


# 7 --------------------------------------------------------------- star garland
def star_garland():
    layers = [L(FRAME, "blue"), L(hill(462, 8), "gray")]
    ink = [S("M-20 66 C 140 168 400 168 560 66", 3.6)]
    spots = [(104, 262, "yellow", 84), (270, 296, "orange", 92), (436, 262, "white", 84)]
    xs_y = {104: 118, 270: 150, 436: 118}
    for x, y, c, R in spots:
        layers.append(L(hexagram(x, y, R), c))
        ink.append(S(f"M{x} {xs_y[x]} L{x} {y - R + 2}", 3.2))
        ink.append(circle(x, xs_y[x], 5))
    ink += twinkle([(40, 300), (500, 300), (190, 380), (350, 410), (40, 400), (500, 400)])
    return layers, ink


# 8 --------------------------------------------------------------- star medallion
def medallion():
    cx, cy = 270, 250
    layers = [L(FRAME, "blue")]
    for k in range(12):
        layers.append(L(sector(cx, cy, 150, 236, k * 30, (k + 1) * 30), "yellow" if k % 2 == 0 else "white"))
    layers.append(L(circle(cx, cy, 150), "gray"))
    layers.append(L(hexagram(cx, cy, 118), "orange"))
    ink = twinkle([(36, 40), (504, 40), (36, 460), (504, 460)])
    return layers, ink


PICTURES = [
    ("menorah", "Menorah", menorah),
    ("dreidel", "Dreidel", dreidel),
    ("star", "Star of David", star_of_david),
    ("oiljar", "Oil Lamp and Olive Leaves", oil_jar),
    ("dreidels", "Three Dreidels", three_dreidels),
    ("window", "Menorah in the Window", window),
    ("garland", "Star Garland", star_garland),
    ("medallion", "Star Medallion", medallion),
    ("nightmenorah", "Menorah Under the Moon", menorah_night),
]
