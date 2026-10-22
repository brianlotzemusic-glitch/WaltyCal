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


def tangent_cut(pts, t, half=260, bow=0.0):
    """Curved line across a swept tube at fraction t of its centre line (bowed along the tube)."""
    cl = LineString(pts)
    p = cl.interpolate(t, normalized=True)
    q = cl.interpolate(min(1.0, t + .01), normalized=True)
    p0 = cl.interpolate(max(0.0, t - .01), normalized=True)
    dx, dy = q.x - p0.x, q.y - p0.y
    n = math.hypot(dx, dy)
    tx, ty = dx / n, dy / n
    nx, ny = -ty, tx
    out = []
    for k in range(-26, 27):
        sdist = half * k / 26
        off = bow * (1 - (sdist / 100.0) ** 2)
        out.append((p.x + nx * sdist + tx * off, p.y + ny * sdist + ty * off))
    return LineString(out)


BOW = 20


def band_layers(shape, cl_pts, ts, colours):
    """Split a swept shape into bands (perpendicular cuts at ts), one layer per band."""
    edges = [0.0] + list(ts) + [1.0]
    out = []
    for i in range(len(edges) - 1):
        lo, hi = edges[i], edges[i + 1]
        a = tangent_cut(cl_pts, lo, bow=BOW) if lo > 0 else None
        b = tangent_cut(cl_pts, hi, bow=BOW) if hi < 1 else None
        cutter = box(-100, -100, 700, 700)
        from shapely.ops import split
        part = shape
        if a is not None:
            pieces = [p for p in split(shape, a).geoms]
            part = max(pieces, key=lambda p: tangent_side(p, a, cl_pts[-1]))
        if b is not None:
            pieces = [p for p in split(part, b).geoms]
            part = min(pieces, key=lambda p: tangent_side(p, b, cl_pts[-1]))
        out.append(L(part, colours[i % len(colours)]))
    return out


def tangent_side(p, ln, ref):
    """Signed side of polygon p's centroid relative to line ln, using ref (a far point) as positive."""
    (x0, y0), (x1, y1) = list(ln.coords)[0], list(ln.coords)[-1]
    def sd(x, y):
        return (x1 - x0) * (y - y0) - (y1 - y0) * (x - x0)
    c = p.centroid
    return sd(c.x, c.y) * (1 if sd(*ref) > 0 else -1)


def pear_shape(cx, cy, s=1.0):
    return soft(tube([(cx, cy - 36 * s), (cx, cy + 24 * s)], [27 * s, 46 * s]), 5)




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

    shine = rot(ellipse(232, 376, 25, 60), 10, (232, 376))
    layers = [L(FRAME, "blue"),
              L(circle(470, 74, 42), "yellow"),
              L(hill(452, 12), "green"),
              L(soft(leaf_at(20, 330, 112, 76, -20, 8), 4), "orange"),
              L(soft(leaf_at(520, 352, 112, 76, 200, 8), 4), "orange"),
              L(nut, "orange"),
              L(shine.intersection(nut), "yellow"),
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
    cx, cy = 270, 318
    layers = [L(FRAME, "blue"), L(hill(452, 10), "green")]
    # one clean fan of seven matching teardrop feathers, drawn from the sides in toward the middle
    n, step = 7, 29.0
    angs = [-90 + (k - 3) * step for k in range(n)]
    order = sorted(range(n), key=lambda k: -abs(k - 3))
    ink = []
    for k in order:
        f = rot(mv(teardrop(40, 262, 92), cx, cy), angs[k], (cx, cy))
        layers.append(L(f, "red" if k % 2 == 0 else "orange"))
    for k in range(n):               # quill line up the middle of each feather
        q = LineString([(cx + 84, cy), (cx + 150, cy)]).buffer(OUTLINE / 2, quad_segs=4)
        ink.append(rot(q, angs[k], (cx, cy)))
    layers += [L(ellipse(270, 392, 104, 92), "brown"),
               L(rot(mv(ellipse(0, 0, 34, 56), 190, 424), 24, (190, 424)), "orange"),
               L(rot(mv(ellipse(0, 0, 34, 56), 350, 424), -24, (350, 424)), "orange"),
               L(circle(270, 304, 68), "brown")]
    ink += [dot(247, 280, 7), dot(293, 280, 7),
            soft(Polygon([(258, 292), (282, 292), (270, 310)]), 3),
            soft(P("M266 310 C260 318 261 326 270 329 C279 326 280 318 274 310 Z"), 2)]
    for x in (236, 304):          # legs and three-toed feet
        ink.append(stem(f"M{x} 462 L{x} 478", 7))
        for dx in (-16, 0, 16):
            ink.append(stem(f"M{x} 476 L{x + dx} 490", 5))
    return layers, ink


def horn_centre():
    pts = _bez((236, 292), (320, 430), (490, 440), (488, 270), n=60)
    pts += _bez((484, 270), (490, 180), (456, 110), (410, 100), n=40)
    return [(236, 292)] + pts


def horn_radii(n):
    return [92 - 76 * (i / (n - 1)) ** 1.15 for i in range(n)]


def cornucopia():
    pts = horn_centre()
    n = len(pts)
    horn = tube(pts, horn_radii(n), n=n - 1)
    tx, ty = pts[4][0] - pts[0][0], pts[4][1] - pts[0][1]
    ang = math.degrees(math.atan2(ty, tx))
    nrm = math.hypot(tx, ty); tx, ty = tx / nrm, ty / nrm
    p0 = pts[0]
    cut = Polygon([(p0[0] - 130 * ty, p0[1] + 130 * tx), (p0[0] + 130 * ty, p0[1] - 130 * tx),
                   (p0[0] + 130 * ty - 70 * tx, p0[1] - 130 * tx - 70 * ty) if False else (p0[0] + 130 * ty - 90 * tx, p0[1] - 130 * tx - 90 * ty),
                   (p0[0] - 130 * ty - 90 * tx, p0[1] + 130 * tx - 90 * ty)])
    horn = soft(horn.difference(cut), 4)
    cuts = [tangent_cut(pts, t, half=140, bow=0) for t in (0.22, 0.42, 0.6, 0.78)]
    # opening: ellipse at the mouth, perpendicular to the horn
    mouth = rot(mv(ellipse(0, 0, 34, 94), pts[0][0] + 4, pts[0][1]), ang, pts[0])
    layers = [L(FRAME, "blue"), L(hill(416, 12), "green")]
    # horn bands drawn as separate layers (alternating colours)
    edges = [0.0, .2, .4, .58, .76, 1.0]
    from shapely.ops import split as _split
    cls = ["orange", "brown", "orange", "brown", "orange"]
    cl = LineString(pts)
    for i in range(5):
        part = horn
        if i > 0:
            ps = list(_split(horn, cuts[i - 1]).geoms)
            part = max(ps, key=lambda p: cl.project(p.centroid))
        if i < 4:
            ps = list(_split(part, cuts[i]).geoms)
            part = min(ps, key=lambda p: cl.project(p.centroid))
        layers.append(L(part, cls[i]))
    layers += [L(mouth, "brown"),
               L(soft(leaf_at(190, 140, 140, 70, -24, 6), 3), "green"),
               L(pear_shape(160, 170, 1.0), "green"),
               L(circle(104, 306, 58), "orange"),
               L(apple_shape(180, 262, 56), "red"),
               L(apple_shape(150, 366, 66), "red"),
               L(circle(228, 412, 38), "orange")]
    ink = [stem("M160 122 C162 110 168 104 178 100", 5),
           stem("M180 212 C178 202 184 196 194 192", 5), stem("M150 314 C148 302 154 296 164 292", 5),
           stem("M96 242 C96 232 100 226 108 222", 5)]
    return layers, ink


def pie():
    # three-quarter view: tin wall, fluted crust ring, filling cut in 6 slices, cream swirl in the middle
    cx, cy = 270, 232
    rx, ry = 234, 124
    n_b = 38
    bumps = unary_union([circle(cx + rx * math.cos(2 * math.pi * k / n_b), cy + ry * math.sin(2 * math.pi * k / n_b), 12)
                         for k in range(n_b)])
    rim = unary_union([ellipse(cx, cy, rx, ry), bumps])
    inner = ellipse(cx, cy + 6, 176, 88)
    base = ellipse(cx, cy + 104, 190, 100)
    wall = unary_union([rim, base, Polygon([(cx - rx, cy), (cx - 190, cy + 104), (cx + 190, cy + 104), (cx + rx, cy)])]).difference(rim)
    layers = [L(FRAME, "blue"),
              L(soft(leaf_at(14, 46, 130, 78, 14, 6), 4), "orange"), L(soft(leaf_at(526, 52, 130, 78, 166, 6), 4), "orange"),
              L(soft(leaf_at(14, 462, 130, 78, -14, 6), 4), "orange"), L(soft(leaf_at(526, 452, 130, 78, 194, 6), 4), "orange"),
              L(wall, "gray"), L(rim, "brown"), L(inner, "orange")]
    cuts = [LineString([(cx, cy + 6), (cx + 400 * math.cos(math.radians(a)), cy + 6 + 400 * 0.46 * math.sin(math.radians(a)))])
            for a in (30, 90, 150)]
    layers[-1] = L(inner, "orange", cuts=[LineString([(cx - 300, cy + 6), (cx + 300, cy + 6)]),
                                          LineString([(cx, cy - 100), (cx, cy + 112)])])
    layers.append(L(rosette(cx, cy + 6, 52), "white"))
    return layers, []


def corn():
    """Corn cob on the diagonal: tapered cob, curved rows of kernels in barrel-shaped columns, husks peeling down."""
    cx = 270
    ear = P("M270 6 C354 6 384 110 384 206 C384 300 352 382 270 408 C188 382 156 300 156 206 C156 110 186 6 270 6 Z")
    rows = [6, 96, 156, 216, 276, 330]
    fr = [-1.0, -0.5, 0.0, 0.5, 1.0]
    PIV = (270, 250)
    ANG = 0

    def R(g):
        return rot(mv(g, 0, 20), ANG, PIV)

    def hw(y):
        seg = ear.intersection(LineString([(0, y), (540, y)]))
        return max(30.0, (seg.bounds[2] - seg.bounds[0]) / 2) if not seg.is_empty else 30.0

    def cell(ri, ci, fr=fr):
        def xat(f, y):
            return cx + f * hw(min(max(y, 40), 400)) * 1.04

        def ycurve(y0, x):
            return y0 + 9 * (1 - ((x - cx) / 100.0) ** 2)
        pts = []
        for k in range(13):
            f = fr[ci] + (fr[ci + 1] - fr[ci]) * k / 12
            x = xat(f, rows[ri])
            pts.append((x, ycurve(rows[ri], x)))
        for k in range(13):
            f = fr[ci + 1] + (fr[ci] - fr[ci + 1]) * k / 12
            x = xat(f, rows[ri + 1])
            pts.append((x, ycurve(rows[ri + 1], x)))
        return Polygon(pts).buffer(0)

    fl = P("M262 470 C150 462 96 380 108 270 C112 250 124 248 132 262 C160 322 214 342 270 346 Z")
    mid = P("M270 494 C206 450 200 360 270 296 C340 360 334 450 270 494 Z")
    front = [soft(mv(fl, 0, 30), 6), soft(mv(mirror(fl), 0, 30), 6)]
    midg = soft(mv(mid, 0, 30), 4)
    hide = unary_union(front + [midg])
    layers = [L(FRAME, "blue"), L(circle(86, 84, 44), "yellow"), L(hill(446, 14), "brown")]
    for ri in range(len(rows) - 1):
        last = ri == len(rows) - 2
        for ci in range(2 if last else 4):
            c = ear.intersection(cell(ri, ci, [-1.0, 0.0, 1.0] if last else fr).buffer(.3, join_style=2))
            if ri == 0:
                if ci > 0:
                    continue
                c = ear.intersection(Polygon([(0, 0), (540, 0), (540, rows[1] + 10), (0, rows[1] + 10)]).intersection(box(0, 0, 540, rows[1]))) if False else ear.intersection(box(0, 0, 540, rows[1] + 9))
            if c.area > 120:
                layers.append(L(R(c), "yellow" if ri == 0 or (ci in (1, 2) and not last) else "orange"))
    layers += [L(R(f), "green") for f in front] + [L(R(midg), "green")]
    ink = [R(stem("M270 8 C270 -6 274 -14 282 -20", 6)), R(S("M270 520 C262 470 262 410 270 366", 1.6))]
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
    centre = half(-33.5, 33.5)
    veins_ink = []
    for ang_, r_ in ((58.5, 150), (-58.5, 150), (114.7, 120), (-114.7, 120)):
        d_ = (math.sin(math.radians(ang_)), -math.cos(math.radians(ang_)))
        veins_ink.append(LineString([(pv[0] + d_[0] * 40, pv[1] + d_[1] * 40), (pv[0] + d_[0] * r_, pv[1] + d_[1] * r_)]).buffer(OUTLINE / 2, quad_segs=4))
    ink = veins_ink + [stem(f"M{cx} {cy + 8} C{cx} {cy + 110} {cx + 2} {cy + 170} {cx} {cy + 196}", 5)]
    return layers, ink


PICTURES = [
    ("turkey", "Friendly Turkey", turkey),
    ("pumpkin", "Harvest Pumpkin", pumpkin),
    ("cornucopia", "Cornucopia", cornucopia),
    ("maple", "Maple Leaf", maple),
    ("acorn", "Acorn", acorn),
    ("basket", "Apple Basket", apple_basket),
    ("pie", "Pumpkin Pie", pie),
    ("corn", "Corn on the Cob", corn),
    ("sunflower", "Sunflower", sunflower),
]
