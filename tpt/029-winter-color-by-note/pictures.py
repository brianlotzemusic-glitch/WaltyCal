"""Winter and holiday pictures for the colour-by-note set, drawn in code.

Style rules shared by all nine pictures (so they read as one product line):
  * every picture is a hero object on a simple scene (sky + rolling hill), in a rounded frame
  * all outlines are one weight (the renderer strokes every region the same); no thick
    black strokes except small solid "ink" details: stems and eyes
  * thin ink lines (same weight as the outline) are used only for fine detail that sits
    away from where the notes go (curls, quill marks, stitches)
  * shapes are soft and rounded (corners are rounded with a morphological opening/closing)
  * never more than five colours per picture (one per note in the key); every region is
    big enough for the largest note label (a staff of about 40 x 43 pt)

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


def snowman():
    layers = [L(FRAME, "blue"), L(circle(84, 96, 44), "yellow"), L(hill(436, 10), "white")]
    layers += [L(circle(270, 432, 92), "white"), L(circle(270, 326, 80), "white"), L(circle(270, 190, 66), "white")]
    # scarf: a band wrapped round the neck (curving with the body) plus a dangling tail
    band = P("M196 228 C226 256 314 256 344 228 L350 268 C318 298 222 298 190 268 Z")
    tail = rot(rrect(298, 256, 354, 358, 14), -6, (326, 256))
    layers.append(L(soft(unary_union([band, tail]), 4), "red"))
    layers.append(L(rrect(214, 4, 326, 126, 10), "black"))
    layers.append(L(rrect(202, 70, 338, 126, 8), "red"))
    ink = [stem("M194 314 C158 310 126 290 98 250", 7), stem("M136 292 C128 280 126 270 130 258", 5), stem("M116 270 C106 270 98 268 90 260", 5),
           stem("M346 314 C382 310 414 290 442 250", 7), stem("M404 292 C412 280 414 270 410 258", 5), stem("M424 270 C434 270 442 268 450 260", 5),
           dot(250, 176, 6.5), dot(290, 176, 6.5),
           soft(Polygon([(266, 192), (266, 208), (330, 202)]), 3)]
    ink += [dot(258, y, 6.5) for y in (330, 372, 414)]
    ink += flakes([(44, 200), (150, 160), (170, 400), (50, 370), (490, 120), (480, 250), (420, 390), (500, 410), (440, 50), (140, 40)])
    return layers, ink


def mitten_parts():
    """One mitten in local coordinates: cuff top edge at y = 0, short thumb on the right."""
    palm = P("M-72 8 L-76 -112 C-78 -170 -44 -196 0 -196 C44 -196 78 -170 76 -112 L72 8 Z")
    thumb = rot(ellipse(90, -78, 25, 44), -34, (90, -78))
    body = soft(unary_union([palm, thumb]), 9)
    cuff = rrect(-80, 0, 80, 62, 14)
    badge = star_shape(0, -100, 58, 33)
    ribs = unary_union([stem(f"M{x} 12 L{x} 50", 1.6) for x in (-64, -52, 52, 64)])
    return body, cuff, badge, ribs


def place_mitten(g, side):
    cx = 158 if side < 0 else 382
    if side < 0:
        g = affinity.scale(g, -1, 1, origin=(0, 0))
    g = affinity.scale(g, 1.22, 1.22, origin=(0, 0))
    g = mv(g, 0, 400)
    g = rot(g, 6 * side, (0, 400))
    return mv(g, cx, 0)


def mittens():
    layers = [L(FRAME, "blue"), L(hill(450, 12), "white")]
    ink = []
    for side, col in ((-1, "red"), (1, "green")):
        body, cuff, badge, ribs = mitten_parts()
        for g, c in ((body, col), (cuff, "white"), (badge, "yellow")):
            layers.append(L(place_mitten(g, side), c))
        ink.append(place_mitten(ribs, side))
    ink += flakes([(270, 70), (60, 60), (480, 60), (270, 190), (40, 150), (500, 150), (110, 30), (430, 30), (270, 120)])
    return layers, ink


def cabin():
    layers = [L(FRAME, "blue"), L(circle(456, 62, 36), "yellow"),
              L(pine(54, 130, 440, 52, 3), "green"), L(pine(486, 150, 440, 52, 3), "green"),
              L(hill(430, 14), "white")]
    layers.append(L(rrect(332, 84, 380, 236, 4), "brown"))
    layers.append(L(rrect(128, 250, 412, 448, 4), "brown"))
    roof = soft(P("M92 278 L270 100 L448 278 Z"), 6)
    layers.append(L(roof, "green"))
    cap = roof.intersection(unary_union([box(0, 0, 540, 178)] + [circle(100 + 46 * k, 178, 28) for k in range(0, 9)]))
    layers.append(L(cap, "white"))
    layers.append(L(unary_union([box(244, 352, 296, 448), ellipse(270, 352, 26, 26)]), "brown"))
    layers += [L(rrect(152, 296, 218, 362, 10), "yellow"), L(rrect(322, 296, 388, 362, 10), "yellow")]
    ink = [dot(282, 392, 3.8), stem("M358 78 C332 58 384 42 356 18", 3.2)]
    ink += flakes([(70, 60), (190, 50), (300, 40), (150, 110), (440, 150), (500, 40), (30, 110), (250, 60)])
    return layers, ink


def star_shape(cx, cy, R, r=None):
    r = r or R * .5
    pts = []
    for k in range(10):
        a = math.radians(-90 + k * 36)
        rr = R if k % 2 == 0 else r
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return soft(Polygon(pts), 4)


def xmas_tree():
    layers = [L(FRAME, "blue"), L(hill(408, 10), "white")]
    def tier(top, base, hw, teeth=5, flat=False):
        pts = [(270, top), (270 + hw, base - 16)]
        if flat:
            pts += [(270 + hw, base), (270 - hw, base)]
        else:
            for k in range(teeth * 2 + 1):
                x = 270 + hw - 2 * hw * k / (teeth * 2)
                pts.append((x, base if k % 2 == 0 else base - 26))
        pts.append((270 - hw, base - 16))
        return soft(Polygon(pts), 5)
    layers += [L(tier(250, 440, 208, 6), "green"), L(tier(170, 352, 154, 5), "green"), L(tier(100, 244, 102, 4), "green")]
    layers.append(L(rrect(214, 428, 326, 486, 8), "red"))
    layers.append(L(star_shape(270, 60, 58, 29), "yellow"))
    for (x, y, c) in ((176, 392, "red"), (364, 392, "yellow"), (196, 300, "yellow"), (344, 300, "red")):
        layers.append(L(circle(x, y, 30), c))
    ink = flakes([(60, 90), (120, 200), (50, 300), (480, 80), (430, 190), (490, 300), (90, 400), (460, 410)])
    return layers, ink


def snowflake():
    cx, cy = 270, 250
    layers = [L(FRAME, "purple")]
    def stroke(p0, p1, w):
        return LineString([p0, p1]).buffer(w / 2, quad_segs=12)
    parts = [stroke((0, 0), (204, 0), 62)]
    for r0, ln, w in ((100, 56, 38), (156, 46, 34)):
        for sgn in (-1, 1):
            a = math.radians(60 * sgn)
            parts.append(stroke((r0, 0), (r0 + ln * math.cos(a), ln * math.sin(a)), w))
    flake = unary_union(parts)
    for k in range(6):
        layers.append(L(rot(mv(flake, cx, cy), k * 60 - 90, (cx, cy)), "white"))
    for k in range(6):
        x, y = polar(cx, cy, 206, k * 60 - 60)
        layers.append(L(circle(x, y, 31), "blue"))
    layers.append(L(soft(Polygon([polar(cx, cy, 84, k * 60 - 90) for k in range(6)]), 8), "yellow"))
    ink = flakes([(40, 40), (500, 40), (40, 460), (500, 460), (270, 16), (270, 484), (30, 250), (510, 250)])
    return layers, ink


def cardinal():
    layers = [L(FRAME, "blue")]
    branch = soft(P("M-20 400 C120 388 320 392 560 358 L560 424 C320 456 120 456 -20 466 Z"), 4)
    layers.append(L(branch, "brown"))

    def top(x):
        return 400 - 42 * (x + 20) / 580
    def lump(x0, x1, h):
        mid = (x0 + x1) / 2
        cloud = unary_union([ellipse(mid, top(mid) - h * .35, (x1 - x0) * .36, h * .62), ellipse(x0 + (x1 - x0) * .25, top(x0) - h * .1, (x1 - x0) * .26, h * .45),
                             ellipse(x1 - (x1 - x0) * .25, top(x1) - h * .1, (x1 - x0) * .26, h * .45)])
        return soft(cloud.intersection(P(f"M{x0 - 40} {top(x0) + 16} L{x1 + 40} {top(x1) + 16} L{x1 + 40} 200 L{x0 - 40} 200 Z")), 6)
    layers.append(L(lump(8, 200, 66), "white"))
    big = lambda g: affinity.scale(g, 1.1, 1.1, origin=(262, 392))
    tail = soft(tube([(320, 336), (400, 384), (470, 444)], [46, 36, 22]), 4)
    body = soft(unary_union([ellipse(262, 292, 122, 100), circle(206, 196, 66),
                             Polygon([(176, 150), (212, 70), (252, 156)])]), 16)
    wing = soft(rot(ellipse(298, 304, 72, 50), 30, (298, 304)), 4)
    mask = ellipse(172, 212, 62, 56).intersection(body)
    layers += [L(big(tail), "red"), L(big(body), "red"), L(big(wing), "red"), L(big(mask), "black")]
    ink = [eye(190, 192, 11), soft(Polygon([(112, 196), (112, 224), (154, 208)]), 2)]
    for x in (240, 282):
        ink.append(stem(f"M{x} 384 L{x} 396", 6))
        for dx in (-12, 0, 12):
            ink.append(stem(f"M{x} 394 L{x + dx} 404", 4.5))
    ink = [big(g) for g in ink]
    ink += flakes([(70, 90), (140, 40), (420, 70), (490, 150), (60, 250), (460, 250), (330, 40), (500, 50)])
    return layers, ink


def gingerbread():
    layers = [L(FRAME, "blue"), L(hill(440, 10), "white")]
    layers.append(L(rrect(84, 262, 456, 434, 4), "brown"))
    layers.append(L(rrect(376, 112, 432, 270, 6), "brown"))
    layers.append(L(rrect(366, 82, 442, 134, 14), "white"))
    layers.append(L(soft(P("M44 300 L270 86 L496 300 Z"), 6), "red"))
    n = 9
    drip = unary_union([rrect(52, 250, 488, 296, 10)] + [circle(52 + 436 * (k + .5) / n, 296, 24) for k in range(n)])
    layers.append(L(drip, "white"))
    for (x, y) in ((196, 236), (270, 166), (344, 236)):
        layers.append(L(circle(x, y, 33), "green"))
    layers.append(L(unary_union([box(242, 366, 298, 434), ellipse(270, 366, 28, 28)]), "green"))
    layers += [L(rrect(132, 338, 200, 404, 12), "white"), L(rrect(340, 338, 408, 404, 12), "white")]
    ink = flakes([(180, 50), (360, 40), (270, 24), (80, 130), (460, 150), (36, 200), (504, 220), (150, 474), (390, 474), (40, 60), (500, 60)])
    return layers, ink


def ornament():
    cx, cy, R = 270, 300, 164
    layers = [L(FRAME, "blue")]
    ball = circle(cx, cy, R)
    layers.append(L(ball, "white"))
    layers.append(L(ball.intersection(ellipse(cx, cy, 116, R + 4)), "red"))
    layers.append(L(ball.intersection(ellipse(cx, cy, 52, R + 4)), "green"))
    layers.append(L(star_shape(cx, cy + 6, 78, 42), "yellow"))
    layers.append(L(rrect(216, 112, 324, 170, 12), "yellow"))
    ink = [circle(270, 88, 15).difference(circle(270, 88, 6)), stem("M270 100 L270 112", 4)]
    ink += flakes([(50, 100), (490, 100), (60, 270), (480, 270), (60, 400), (484, 400), (110, 470), (430, 470), (40, 190), (500, 190)])
    return layers, ink


def gift():
    layers = [L(FRAME, "blue"), L(hill(452, 12), "white")]
    layers.append(L(rrect(88, 340, 452, 464, 6), "red"))
    layers.append(L(rrect(150, 190, 390, 306, 10), "green"))
    layers.append(L(rrect(72, 288, 468, 344, 10), "red"))
    layers.append(L(rrect(236, 288, 304, 464, 0), "yellow"))
    layers.append(L(rrect(236, 190, 304, 290, 0), "yellow"))
    loop = soft(ellipse(-58, -26, 64, 42, -22), 4)
    for g in (loop, mirror(loop, 0)):
        layers.append(L(mv(g, 270, 186), "yellow"))
    layers.append(L(ellipse(270, 188, 36, 30), "yellow"))
    ink = [stem("M236 160 C214 138 180 136 160 148", 1.6), stem("M304 160 C326 138 360 136 380 148", 1.6)]
    ink += flakes([(60, 80), (140, 60), (60, 230), (480, 90), (420, 50), (490, 230), (270, 40), (44, 400), (500, 410)])
    return layers, ink


PICTURES = [
    ("snowman", "Friendly Snowman", snowman),
    ("mittens", "Cozy Mittens", mittens),
    ("cabin", "Snowy Cabin", cabin),
    ("tree", "Holiday Tree", xmas_tree),
    ("snowflake", "Snowflake", snowflake),
    ("cardinal", "Winter Cardinal", cardinal),
    ("gingerbread", "Gingerbread House", gingerbread),
    ("ornament", "Striped Ornament", ornament),
    ("gift", "Wrapped Gifts", gift),
]
