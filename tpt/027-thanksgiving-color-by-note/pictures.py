"""Thanksgiving / autumn pictures for the colour-by-note set, drawn in code.

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
def feather(cx, cy, r1, a0, a1, rr):
    """Fan feather: wedge from the fan centre with a softly rounded outer end."""
    return unary_union([soft(sector(cx, cy, 30, r1, a0, a1), rr), sector(cx, cy, 0, 90, a0, a1)])




def pumpkin():
    cx, cy = 226, 312
    layers = [L(FRAME, "blue"),
              L(circle(446, 82, 46), "yellow"),
              L(hill(396, 16), "green")]
    outer = ellipse(cx - 124, cy + 6, 92, 120, rot=-9)
    mid = ellipse(cx - 64, cy, 88, 132, rot=-4)
    ctr = ellipse(cx, cy - 2, 76, 138)
    stem_g = soft(P(f"M{cx - 30} 182 C{cx - 28} 150 {cx - 22} 122 {cx - 10} 102 C{cx} 94 {cx + 20} 96 {cx + 28} 108 "
                    f"C{cx + 28} 134 {cx + 32} 160 {cx + 30} 182 Z"), 4)
    layers += [L(soft(leaf_at(cx - 10, 176, 160, 84, 206, 12), 4), "green"),
               L(soft(leaf_at(cx + 10, 176, 160, 84, -26, 12), 4), "green"),
               L(outer, "orange"), L(mirror(outer, cx), "orange"),
               L(mid, "orange"), L(mirror(mid, cx), "orange"), L(ctr, "orange"),
               L(stem_g, "brown"),
               L(ellipse(458, 410, 58, 48), "orange")]
    ink = [stem("M458 366 C458 354 462 348 470 344", 6)]
    return layers, ink


MAPLE_PROFILE = [(0, 236), (6, 184), (11, 204), (16, 150), (22, 124), (30, 150), (38, 180), (42, 160), (49, 200),
                 (55, 210), (62, 168), (67, 188), (73, 132), (80, 108), (88, 122), (96, 156), (106, 188), (112, 204), (118, 172),
                 (123, 188), (129, 138), (137, 86), (150, 62), (165, 56), (180, 54)]


def maple_outline(cx, cy, sc=1.0):
    """Five-lobed maple leaf from a hand-tuned polar profile (angle clockwise from up, radius), mirrored."""
    right = [(cx + r * sc * math.sin(math.radians(a)), cy - r * sc * math.cos(math.radians(a))) for a, r in MAPLE_PROFILE]
    left = [(2 * cx - x, y) for x, y in reversed(right[1:-1])]
    return Polygon(right + left).buffer(0)




def small_maple(cx, cy, sc, ang):
    """A small maple leaf (the same outline as the big one) to fall through a scene."""
    g = soft(maple_outline(cx, cy, sc), 4)
    return rot(g, ang, (cx, cy))


def acorn():
    cap = soft(P("M120 280 C116 180 190 104 270 104 C350 104 424 180 420 280 C376 308 164 308 120 280 Z"), 6)
    nut = soft(P("M142 268 C144 350 180 438 270 490 C360 438 396 350 398 268 Z"), 10)

    def scallop_line(y, depth, x0=100, x1=440, nb=7):
        w = (x1 - x0) / nb
        pts = []
        for k in range(nb):
            for j in range(0, 11):
                t = j / 10
                x = x0 + w * (k + t)
                pts.append((x, y + depth * math.sin(math.pi * t)))
        return LineString(pts)

    layers = [L(FRAME, "blue"),
              L(circle(470, 74, 42), "yellow"),
              L(hill(452, 12), "green"),
              L(soft(leaf_at(20, 330, 112, 76, -20, 8), 4), "orange"),
              L(soft(leaf_at(520, 352, 112, 76, 200, 8), 4), "orange"),
              L(nut, "orange"),
              L(cap, "brown", cuts=[scallop_line(172, 16), scallop_line(238, 16)])]
    ink = [stem("M270 108 C268 84 278 66 298 56", 11)]
    return layers, ink


def apple_shape(cx, cy, r):
    base = unary_union([circle(cx - r * .28, cy - r * .02, r * .76), circle(cx + r * .28, cy - r * .02, r * .76),
                        circle(cx, cy + r * .14, r * .74)])
    dent = ellipse(cx, cy - r * .84, r * .13, r * .09)
    return soft(base.difference(dent), 5)


def apple_basket():
    cx = 270
    body = soft(P("M92 322 L448 322 C440 400 420 452 396 484 L144 484 C120 452 100 400 92 322 Z"), 10)
    rim = rrect(62, 296, 478, 358, 26)
    arch = ellipse(cx, 322, 210, 276).difference(ellipse(cx, 322, 150, 214)).intersection(box(0, 0, 540, 312))
    layers = [L(FRAME, "blue"), L(hill(418, 12), "green"),
              L(arch, "brown"),
              L(apple_shape(cx, 252, 98), "green"),
              L(apple_shape(172, 280, 86), "red"),
              L(apple_shape(368, 280, 86), "red")]
    top, bot = 358, 484
    nrow, ncol = 2, 5

    def xs(y):
        f = (y - 322) / (484 - 322)
        return 92 + 48 * f, 448 - 48 * f

    for j in range(nrow):
        y0 = top + (bot - top) * j / nrow
        y1 = top + (bot - top) * (j + 1) / nrow
        for i in range(ncol):
            xa0, xb0 = xs(y0)
            xa1, xb1 = xs(y1)
            q = Polygon([(xa0 + (xb0 - xa0) * i / ncol, y0), (xa0 + (xb0 - xa0) * (i + 1) / ncol, y0),
                         (xa1 + (xb1 - xa1) * (i + 1) / ncol, y1), (xa1 + (xb1 - xa1) * i / ncol, y1)])
            layers.append(L(body.intersection(q.buffer(.4, join_style=2)), "yellow" if (i + j) % 2 else "brown"))
    layers.append(L(rim, "brown"))
    ink = [stem("M270 182 C268 166 274 154 284 146"), stem("M172 222 C170 206 176 194 186 186"),
           stem("M368 222 C366 206 372 194 382 186")]
    return layers, ink


def cloud(cx, cy, s=1.0):
    parts = [circle(cx - 40 * s, cy + 6 * s, 30 * s), circle(cx, cy - 12 * s, 40 * s), circle(cx + 44 * s, cy + 4 * s, 32 * s),
             rrect(cx - 72 * s, cy + 2 * s, cx + 76 * s, cy + 36 * s, 17 * s)]
    return soft(unary_union(parts), 4)


def rosette(cx, cy, r):
    return unary_union([circle(cx, cy, r * .78), scallops(cx, cy, r * .66, 9, r * .3)])






def sunflower():
    cx, cy = 270, 212
    layers = [L(FRAME, "blue"), L(hill(434, 12), "green")]
    lf = P("M268 456 C196 384 96 392 60 440 C94 498 206 508 268 456 Z")
    layers += [L(soft(lf, 5), "green"), L(soft(mirror(lf), 5), "green")]
    layers.append(L(soft(P("M240 300 C244 360 238 430 228 500 L312 500 C302 430 296 360 300 300 Z"), 4), "green"))
    n = 12
    petal = P("M0 -60 C -58 -92 -64 -176 0 -206 C 64 -176 58 -92 0 -60 Z")
    for k in range(n):
        g = mv(rot(petal, k * 360 / n + 15, (0, 0)), cx, cy)
        layers.append(L(g, "yellow" if k % 2 == 0 else "orange"))
    layers.append(L(circle(cx, cy, 94), "brown"))
    # seed dots round the edge of the disc (tiny, same ink as the eyes and stems)
    ink = [circle(cx + 80 * math.cos(math.radians(k * 15)), cy + 80 * math.sin(math.radians(k * 15)), 2.6) for k in range(24)]
    return layers, ink


def teardrop(r0, r1, w):
    """Feather lying along +x from the fan centre: narrow base, round outer end of width w."""
    return soft(unary_union([tube([(r0, 0), (r1 - w / 2, 0)], [w * .12, w / 2], n=40), circle(r1 - w / 2, 0, w / 2)]), 3)


def turkey():
    """Classic front-facing turkey: two rows of tail feathers, a pear-shaped body with the head on
    top, a round bib, two wings, a big red wattle and three-toed feet on the grass."""
    cx, cy = 270, 300                    # fan centre (hidden behind the body)
    layers = [L(FRAME, "blue"), L(hill(452, 10), "green")]
    # back row: nine long red feathers, drawn from the sides in
    n, step = 9, 20.5
    angs = [-90 + (k - 4) * step for k in range(n)]
    for k in sorted(range(n), key=lambda k: -abs(k - 4)):
        f = rot(mv(teardrop(30, 258, 72), cx, cy), angs[k], (cx, cy))
        layers.append(L(f, "red"))
    # front row: eight shorter orange feathers sitting between the long ones
    for k in range(n - 1):
        a = (angs[k] + angs[k + 1]) / 2
        f = rot(mv(teardrop(30, 200, 70), cx, cy), a, (cx, cy))
        layers.append(L(f, "orange"))
    body = soft(unary_union([ellipse(270, 376, 108, 96), circle(270, 236, 66),
                             Polygon([(214, 262), (326, 262), (360, 330), (180, 330)])]), 16)
    layers += [L(body, "brown"),
               L(ellipse(270, 416, 86, 72).intersection(body), "orange"),
               L(soft(rot(ellipse(178, 392, 34, 64), 24, (178, 392)), 3), "brown"),
               L(soft(rot(ellipse(362, 392, 34, 64), -24, (362, 392)), 3), "brown"),
               L(soft(unary_union([circle(270, 312, 30), Polygon([(262, 248), (278, 248), (296, 306), (244, 306)])]), 4), "red")]
    ink = [eye(246, 214, 9), eye(294, 214, 9),
           soft(Polygon([(253, 230), (287, 230), (270, 256)]), 3)]
    for x in (232, 308):          # legs and three-toed feet
        ink.append(stem(f"M{x} 466 L{x} 476", 7))
        for dx in (-15, 0, 15):
            ink.append(stem(f"M{x} 474 L{x + dx} 488", 5))
    return layers, ink


def mushrooms():
    """Two spotted forest mushrooms on a grassy hill, with fallen leaves."""
    layers = [L(FRAME, "blue"), L(cloud(458, 74, .78), "white"), L(hill(430, 14), "green")]
    cap = soft(P("M60 262 C60 120 160 52 262 52 C364 52 464 120 464 262 C400 292 124 292 60 262 Z"), 8)
    stem_g = soft(P("M206 270 C200 330 186 390 190 446 C230 470 294 470 334 446 C338 390 324 330 318 270 Z"), 10)
    cap2 = soft(P("M352 352 C352 290 400 252 448 252 C496 252 532 290 532 352 C500 368 384 368 352 352 Z"), 6)
    stem2 = soft(P("M418 356 C414 392 410 428 412 462 C432 474 468 474 488 462 C490 428 484 392 480 356 Z"), 8)
    spots = [circle(150, 196, 36), circle(268, 118, 38), circle(388, 186, 36), circle(264, 236, 30).union(circle(264, 230, 30))]
    layers += [L(soft(leaf_at(34, 474, 112, 68, -16, 6), 4), "orange"),
               L(stem_g, "white"), L(cap, "red"),
               *[L(sp.intersection(cap), "white") for sp in spots],
               L(stem2, "white"), L(cap2, "orange"),
               L(circle(452, 300, 31).intersection(cap2), "white")]
    return layers, []


def pie():
    """Pumpkin pie seen from above on a yellow plate: fluted crust, eight slices with one
    lifted out a little, a whipped-cream swirl in the middle and autumn leaves in the corners."""
    cx, cy = 270, 250
    n_b = 32
    R = 170
    step = 360 / n_b
    fluted = unary_union([circle(cx, cy, R)] + [circle(*polar(cx, cy, R, k * step), 15) for k in range(n_b)])
    filling = circle(cx, cy, 124)
    a0 = step * 1.5                           # slice edges sit in the valleys between scallops
    a1 = a0 + 4 * step                        # the slice that is lifted out (lower right), 45 degrees
    off = polar(0, 0, 30, (a0 + a1) / 2)

    def wedge(r, b0, b1):
        return sector(cx, cy, 0, r, b0, b1, n=40)
    out_crust = mv(fluted.intersection(wedge(260, a0, a1)).difference(filling), *off)
    out_fill = mv(filling.intersection(wedge(260, a0, a1)), *off)
    rest = wedge(260, a1, a0 + 360)
    cuts = [LineString([(cx, cy), polar(cx, cy, 260, a1 + 45 * k)]) for k in range(1, 7)]
    leaf = lambda x, y, a, c: L(soft(leaf_at(x, y, 124, 76, a, 6), 4), c)
    plate = circle(cx, cy, 236)
    layers = [L(FRAME, "blue"),
              leaf(-6, 36, 24, "orange"), leaf(546, 36, 156, "orange"), leaf(-6, 466, -24, "orange"),
              leaf(546, 466, 204, "orange"),
              L(soft(plate, 3), "yellow"),
              L(fluted.intersection(rest).difference(filling), "brown", cuts=cuts),
              L(filling.intersection(rest), "orange", cuts=cuts),
              L(rosette(cx, cy, 58), "white"),
              L(out_crust, "brown"), L(out_fill, "orange")]
    return layers, []


def owl():
    """Round owl on a branch in front of a full moon: ear tufts, heart-shaped face mask,
    big eyes, scalloped belly, two wings, and leaves on the branch."""
    cx = 262
    layers = [L(FRAME, "blue"), L(circle(420, 128, 90), "yellow")]
    branch = soft(P("M-20 432 C120 416 300 414 560 398 L560 446 C300 462 120 466 -20 482 Z"), 4)
    layers += [L(soft(leaf_at(40, 436, 124, 76, 252, 6), 4), "red"),
               L(soft(leaf_at(92, 432, 112, 72, 292, 6), 4), "orange"),
               L(soft(leaf_at(442, 414, 124, 76, 246, 6), 4), "orange"),
               L(soft(leaf_at(488, 410, 118, 72, 286, 6), 4), "red")]
    body = soft(unary_union([ellipse(cx, 286, 118, 156),
                             P(f"M{cx - 112} 210 L{cx - 106} 76 L{cx - 34} 140 Z"),
                             P(f"M{cx + 112} 210 L{cx + 106} 76 L{cx + 34} 140 Z")]), 8)
    belly = ellipse(cx, 362, 134, 112).intersection(body)

    def scallop_line(y, depth=14, x0=150, x1=390, nb=5):
        w = (x1 - x0) / nb
        return LineString([(x0 + w * (k + j / 10) - 8, y + depth * math.sin(math.pi * j / 10)) for k in range(nb) for j in range(11)])
    mask = soft(unary_union([circle(cx - 50, 218, 58), circle(cx + 50, 218, 58)]), 6)
    # wings: the sides of the body, split off by a curved inner edge
    wing = soft(body.intersection(P(f"M{cx - 200} 200 L{cx - 92} 220 C{cx - 60} 290 {cx - 62} 380 {cx - 96} 440 L{cx - 200} 440 Z")), 3)
    layers += [L(body, "brown"),
               L(belly, "orange", cuts=[scallop_line(350)]),
               L(wing, "brown"), L(mirror(wing, cx), "brown"),
               L(mask, "yellow"),
               L(branch, "brown")]
    ink = [eye(cx - 50, 214, 23), eye(cx + 50, 214, 23),
           soft(Polygon([(cx - 15, 246), (cx + 15, 246), (cx, 276)]), 3)]
    for x in (cx - 42, cx + 42):          # toes gripping the branch
        for dx in (-12, 0, 12):
            ink.append(stem(f"M{x + dx} 410 C{x + dx} 420 {x + dx * 1.3} 428 {x + dx * 1.5 - 3} 434", 6))
    return layers, ink


def maple():
    cx, cy, sc = 270, 252, 1.02
    leaf = soft(maple_outline(cx, cy, sc), 5)
    pv = (cx, cy + 18)
    m = {'Y': 'yellow', 'O': 'orange', 'R': 'red'}
    layers = [L(FRAME, "blue"), L(circle(78, 80, 44), "yellow"), L(hill(452, 12), "green")]
    # five lobes, each split down the middle vein into two halves (red/orange per lobe pair)
    bis = [-146, -83.5, -33.5, 33.5, 83.5, 146]      # boundaries between lobes (angle from up)
    veins = [-112, -55, 0, 55, 112]
    cuts = []
    for a in bis + veins:
        d = (math.sin(math.radians(a)), -math.cos(math.radians(a)))
        cuts.append(LineString([pv, (pv[0] + d[0] * 700, pv[1] + d[1] * 700)]))
    layers.append(L(leaf, "red", cuts=cuts))
    # alternate colours by painting orange/yellow halves over the base
    def half(a0, a1):
        pts = [pv]
        for k in range(21):
            a = math.radians(a0 + (a1 - a0) * k / 20)
            pts.append((pv[0] + 700 * math.sin(a), pv[1] - 700 * math.cos(a)))
        return leaf.intersection(Polygon(pts))
    layers.pop()
    edges = [-146, -112, -83.5, -55, -33.5, 0, 33.5, 55, 83.5, 112, 146]
    cols = ['Y', 'O', 'Y', 'O', 'R', 'R', 'O', 'Y', 'O', 'Y']
    edges = [-146, -83.5, -33.5, 0, 33.5, 83.5, 146]
    cols = ['Y', 'O', 'R', 'R', 'O', 'Y']
    spec = [(edges[i], edges[i + 1], m[cols[i]]) for i in range(6)]
    for a0, a1, c in spec:
        layers.append(L(half(a0, a1), c))
    ink = []                      # thin veins run out along each side lobe (the sinus rays close the lobes)
    for ang_, r0_, r1_ in ((58.5, 36, 168), (-58.5, 36, 168), (114.7, 36, 136), (-114.7, 36, 136)):
        d_ = (math.sin(math.radians(ang_)), -math.cos(math.radians(ang_)))
        ink.append(LineString([(pv[0] + d_[0] * r0_, pv[1] + d_[1] * r0_), (pv[0] + d_[0] * r1_, pv[1] + d_[1] * r1_)]).buffer(0.2, quad_segs=4))
    ink.append(stem(f"M{cx} {cy + 8} C{cx} {cy + 110} {cx + 2} {cy + 170} {cx} {cy + 196}", 2.2))
    return layers, ink


PICTURES = [
    ("turkey", "Friendly Turkey", turkey),
    ("pumpkin", "Harvest Pumpkin", pumpkin),
    ("mushrooms", "Forest Mushrooms", mushrooms),
    ("maple", "Maple Leaf", maple),
    ("acorn", "Acorn", acorn),
    ("basket", "Apple Basket", apple_basket),
    ("pie", "Pumpkin Pie", pie),
    ("owl", "Autumn Owl", owl),
    ("sunflower", "Sunflower", sunflower),
]
