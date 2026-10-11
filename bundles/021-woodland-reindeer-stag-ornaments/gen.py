"""Woodland Reindeer & Stag Ornaments - 6 single-path SVG/DXF cut files.

Hanging Christmas ornaments drawn in code (no AI images): a front-facing
stag head with holly, a leaping reindeer over snowy pines under a crescent
moon, a stag in a pine wood, a reindeer in a scarf, a classic bauble with a
stag cut out of it, and two reindeer under a star. Each has a hanging loop
built in. Everything is unioned into ONE connected polygon; stars, moon and
trees are attached, never floating. compose() closes solid parts by a few
units so near-touching pieces are bridged, then cuts the openings; finish()
closes then opens by 6.5 units (no material or gap narrower than ~13 units)
and fills any hole under MIN_HOLE. Coordinates are SVG-style (y down),
~1000-unit canvas. Artwork is scaled so the longest side is a full 6 in.

Usage:  python3 gen.py            build bundle/SVG + bundle/DXF + README
        python3 gen.py --check    verify the files (unzips the ZIP into bundle/ if needed)
Helpers are reused from bundles 020 (haunted gingerbread), 008 and 006.
"""
import math, os, json, sys, random
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union
from shapely import affinity, make_valid, set_precision
import ezdxf

HERE = os.path.dirname(os.path.abspath(__file__))
SVG_DIR = os.path.join(HERE, "bundle", "SVG")
DXF_DIR = os.path.join(HERE, "bundle", "DXF")
for _d in (SVG_DIR, DXF_DIR):
    os.makedirs(_d, exist_ok=True)
MIN_HOLE = 600.0
SIZE_IN = 6.0
U = unary_union


# ---------------------------------------------------------------- helpers
def poly(pts):
    return Polygon(pts).buffer(0)


def rect(x0, y0, x1, y1, r=0):
    b = box(x0, y0, x1, y1)
    return b.buffer(-r).buffer(r, 16) if r else b


def line(pts, w):
    return LineString(pts).buffer(w / 2, cap_style=1, join_style=1, quad_segs=12)


def circ(x, y, r):
    return Point(x, y).buffer(r, 48)


def polar(x, y, r, deg):
    a = math.radians(deg)
    return x + r * math.cos(a), y + r * math.sin(a)


def star(cx, cy, R, r, n=5, rot=-90):
    pts = []
    for k in range(2 * n):
        rad = R if k % 2 == 0 else r
        pts.append(polar(cx, cy, rad, rot + 180 * k / n))
    return poly(pts)


def crescent(cx, cy, R, dx, dy, k=0.86):
    return circ(cx, cy, R).difference(circ(cx + dx, cy + dy, R * k))


def snowflake(cx, cy, R, w=14, rot=90, branches=True):
    """Six-armed snowflake (used as a cut-out): round centre, arms w wide,
    each ending in a round dot."""
    parts = [circ(cx, cy, R * 0.3)]
    for k in range(6):
        a = rot + 60 * k
        parts.append(line([(cx, cy), polar(cx, cy, R * 0.82, a)], w))
        if branches:
            parts.append(circ(*polar(cx, cy, R * 0.82, a), w * 0.68))
    return U(parts)


def pine(cx, gy, h, w, tiers=4, trunk=None, drip=True):
    """Snowy pine standing on ground line gy: stacked tiers with drooping,
    snow-scalloped lower edges and a short trunk."""
    trunk = trunk if trunk is not None else h * 0.09
    tw = max(16, w * 0.12)
    parts = [rect(cx - tw / 2, gy - trunk - 10, cx + tw / 2, gy + 2)]
    top, yb = gy - h, gy - trunk
    ch = yb - top
    seg = ch / (tiers * 0.78 + 0.22)
    for i in range(tiers):
        apex = top + i * seg * 0.78 - (0 if i == 0 else 0)
        bot = apex + seg if i < tiers - 1 else yb
        if i == 0:
            bot = top + seg
        hw = w / 2 * (0.42 + 0.58 * (i + 1) / tiers)
        n = 16
        right = [(cx + hw * t, apex + (bot - apex) * (t ** 0.85)) for t in (k / n for k in range(1, n + 1))]
        left = [(cx - x + cx, y) for x, y in right][::-1]
        m = max(2, int(round(2 * hw / 34)))
        bottom = []
        for k in range(1, m * 12):
            t = k / (m * 12)
            x = cx + hw - 2 * hw * t
            sag = 9 * abs(math.sin(math.pi * m * t)) if drip else 0
            bottom.append((x, bot - 9 + sag))
        pts = [(cx, apex)] + right + bottom + left
        parts.append(poly(pts))
    return U(parts)


def base_strip(x0, x1, y0, y1, drifts=()):
    """Flat-bottomed base strip with soft snow drifts on top."""
    g = rect(x0, y0, x1, y1, r=10)
    for (cx, w, h) in drifts:
        e = affinity.scale(circ(cx, y0 + 4, 1), w / 2, h)
        g = U([g, e.intersection(rect(cx - w, y0 - h - 2, cx + w, y0 + 10))])
    return g


def areal(g):
    if g.geom_type in ("Polygon", "MultiPolygon"):
        return g
    return U([p for p in getattr(g, "geoms", []) if p.geom_type in ("Polygon", "MultiPolygon")])


def compose(solid, holes, bridge=8):
    """Union the solid parts, close them by `bridge` so that near-touching
    pieces (pine tips next to walls, eaves next to trees) are joined by a
    proper bridge instead of leaving a pinched hairline gap, then cut the
    designed openings."""
    S = U(solid).buffer(bridge, quad_segs=16).buffer(-bridge, quad_segs=16)
    H = areal(U(holes))
    # fill any ring-shaped cut-out so no material is left floating inside it
    H = U([Polygon(p.exterior) for p in (H.geoms if H.geom_type == "MultiPolygon" else [H])])
    return S.difference(H)


def finish(g, r=6.5, simplify=0.12):
    """Close then open by r (no gaps or material under ~2r), drop small holes."""
    g = areal(make_valid(g))
    g = g.buffer(r, quad_segs=16).buffer(-r, quad_segs=16)
    g = g.buffer(-r, quad_segs=16).buffer(r, quad_segs=16)
    g = areal(set_precision(areal(make_valid(g.simplify(simplify))), 0.05))
    polys = list(g.geoms) if g.geom_type == "MultiPolygon" else [g]
    polys = [p for p in polys if p.area > 1500]   # crumbs between cut-outs would fall out anyway
    polys = [Polygon(p.exterior, [i for i in p.interiors if Polygon(i).area >= MIN_HOLE + 30]) for p in polys]
    return U(polys)




def catmull(pts, closed=True, n=16):
    out, P, m = [], list(pts), len(pts)
    rng = range(m) if closed else range(m - 1)
    for i in rng:
        p0 = P[(i - 1) % m] if closed else P[max(i - 1, 0)]
        p1 = P[i]
        p2 = P[(i + 1) % m] if closed else P[i + 1]
        p3 = P[(i + 2) % m] if closed else P[min(i + 2, m - 1)]
        for k in range(n):
            t = k / n
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t +
                                    (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2 +
                                    (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3) for j in (0, 1)))
    if not closed:
        out.append(P[-1])
    return out


def holly_leaf(x0, y0, ang, L, Wd, spikes=3):
    """Spiky holly leaf from base (x0,y0) pointing at ang (deg)."""
    tips = []
    ts = [0.25 + 0.64 * k / spikes for k in range(spikes)]
    for s in (1, -1):
        tips.append([(t * L, s * Wd * 0.55 * (math.sin(math.pi * (0.04 + 0.9 * t)) ** 0.8)) for t in ts])
    base = [(0.04 * L, -Wd * 0.12), (0, 0), (0.04 * L, Wd * 0.12)]
    lf = Polygon(base[1:] + tips[0] + [(L * 1.04, 0)] + tips[1][::-1] + base[:1]).buffer(0)
    bites = []
    for side in tips:
        seq = side + [(L * 1.04, 0)]
        for a, b in zip(seq[:-1], seq[1:]):
            mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
            dx, dy = b[0] - a[0], b[1] - a[1]
            d = math.hypot(dx, dy)
            nx, ny = -dy / d, dx / d
            if nx * (mx - L / 2) + ny * my < 0:
                nx, ny = -nx, -ny
            off = 0.32 * d
            bites.append(Point(mx + nx * off, my + ny * off).buffer(math.hypot(d / 2, off), 48))
    lf = lf.difference(unary_union(bites))
    lf = affinity.rotate(lf, ang, origin=(0, 0))
    return affinity.translate(lf, x0, y0)


def ellipse(cx, cy, rx, ry):
    return affinity.translate(affinity.scale(Point(0, 0).buffer(1, 48), rx, ry), cx, cy)


def taper(p0, p1, w0, w1):
    a = math.atan2(p1[1] - p0[1], p1[0] - p0[0]) + math.pi / 2
    c, s = math.cos(a), math.sin(a)
    q = poly([(p0[0] + c * w0 / 2, p0[1] + s * w0 / 2), (p1[0] + c * w1 / 2, p1[1] + s * w1 / 2),
              (p1[0] - c * w1 / 2, p1[1] - s * w1 / 2), (p0[0] - c * w0 / 2, p0[1] - s * w0 / 2)])
    return U([q, circ(*p0, w0 / 2), circ(*p1, w1 / 2)])


# ---------------------------------------------------------------- deer
MINW = 15.0   # thinnest leg / antler tine after scaling (0.09 in at 6 in)


def limb(pts, ws):
    """Tapered leg / branch through joints pts with widths ws (one per joint)."""
    return U([taper(a, b, wa, wb) for a, b, wa, wb in zip(pts[:-1], pts[1:], ws[:-1], ws[1:])])


def hoof(p, ang, w=24):
    """Small pointed hoof at the end of a leg (p = fetlock, ang = leg direction)."""
    tip = polar(*p, 15, ang)
    return poly([polar(*p, w * 0.42, ang - 90), polar(*p, w * 0.42, ang + 90),
                 polar(*tip, w * 0.5, ang + 90), polar(*tip, w * 0.5, ang - 90)]).buffer(3)


def antler(base, s=1.0, kind="stag", flip=1, rot=0, minw=0):
    """One antler from `base` (skull top). A stag antler is an upright, back-
    curving main beam with forward tines; a reindeer antler sweeps further
    back with a palmate brow shovel and tines on the top. flip=-1 mirrors."""
    rnd = random.Random(7 if kind == "stag" else 9)
    if kind == "stag":
        beam = [(0, 0), (-28, -50), (-56, -120), (-62, -190), (-42, -250), (-6, -292)]
        tines = [(0.13, 68, 80, 20), (0.43, 60, 84, 18), (0.72, 52, 70, 16)]
        w0, w1 = 30, 16
    else:
        beam = [(0, 0), (-46, -44), (-98, -100), (-124, -176), (-112, -248), (-76, -300)]
        tines = [(0.36, 72, 66, 18), (0.62, 62, 70, 17), (0.86, 50, 56, 15)]
        w0, w1 = 30, 16
    pts = catmull(beam, closed=False, n=8)
    ls = LineString(pts)
    n = len(pts)
    parts = [limb(pts, [max(minw, w0 + (w1 - w0) * k / (n - 1)) for k in range(n)])]
    for t, ang_off, L, w in tines:
        q = ls.interpolate(ls.length * t)
        q2 = ls.interpolate(min(ls.length, ls.length * t + 4))
        beam_ang = math.degrees(math.atan2(q2.y - q.y, q2.x - q.x))
        a = beam_ang + ang_off  # forward side of the beam (beam goes up, +offset tilts forward/right)
        mid = polar(q.x, q.y, L * 0.55, a + 8)
        tip = polar(mid[0], mid[1], L * 0.5, a - 14)
        parts.append(limb([(q.x, q.y), mid, tip], [max(minw, w), max(minw, w * 0.8), max(minw, w * 0.55)]))
    if kind == "reindeer":
        # long brow tine reaching forward over the face
        q = ls.interpolate(ls.length * 0.07)
        parts.append(limb([(q.x, q.y), (q.x + 40, q.y - 22), (q.x + 86, q.y - 20)], [max(minw, 20), max(minw, 17), max(minw, 14)]))
    g = U(parts)
    g = affinity.scale(g, flip * s, s, origin=(0, 0))
    g = affinity.rotate(g, rot, origin=(0, 0))
    return affinity.translate(g, *base)


def deer_body(pose="stand"):
    """Deer profile facing right, ground at y=0 (y down). Returns the head/
    neck/torso outline as one smooth closed shape (no legs)."""
    if pose == "stand":
        pts = [(-196, -318), (-160, -306), (-40, -300), (62, -318), (100, -372), (124, -436), (150, -462),
               (182, -458), (218, -434), (234, -416), (228, -401), (198, -394), (164, -386), (150, -350), (152, -290),
               (128, -228), (80, -200), (-40, -202), (-118, -210), (-180, -238), (-200, -280), (-206, -304)]
    else:  # leap: body level and long, neck stretched forward and up
        pts = [(-206, -332), (-168, -322), (-40, -318), (66, -332), (118, -378), (162, -428), (190, -452),
               (222, -446), (262, -418), (274, -400), (266, -386), (236, -380), (202, -378), (168, -346), (154, -296),
               (126, -244), (76, -224), (-40, -226), (-120, -234), (-182, -258), (-204, -292), (-214, -318)]
    return poly(catmull(pts, n=10))


LEGS = {
    "stand": [  # (joints, widths)  front near, front far, hind near, hind far
        ([(108, -240), (116, -122), (122, -20)], [46, 22, 16]),
        ([(72, -236), (56, -120), (40, -20)], [40, 21, 15]),
        ([(-150, -250), (-122, -170), (-190, -98), (-186, -20)], [62, 32, 20, 15]),
        ([(-150, -240), (-96, -172), (-142, -100), (-124, -20)], [50, 28, 19, 15]),
    ],
    "leap": [
        ([(110, -262), (190, -232), (150, -168)], [42, 22, 16]),
        ([(84, -258), (168, -206), (138, -138)], [38, 21, 15]),
        ([(-160, -276), (-214, -214), (-296, -210), (-372, -192)], [62, 32, 20, 15]),
        ([(-176, -280), (-238, -246), (-312, -268), (-384, -270)], [52, 30, 19, 15]),
    ],
}


def deer(pose="stand", kind="stag", s=1.0, x=0, y=0, flip=1, tail=True, ear=True, antlers=True, rot=0):
    """Whole deer: body, 4 legs with hooves, ears, tail, two antlers (the far
    antler slightly behind and smaller). Facing right unless flip=-1."""
    parts = [deer_body(pose)]
    mw = MINW / s
    for joints, ws in LEGS[pose]:
        ws = [max(mw, w) for w in ws]
        parts.append(limb(joints, ws))
        a = math.degrees(math.atan2(joints[-1][1] - joints[-2][1], joints[-1][0] - joints[-2][0]))
        parts.append(hoof(joints[-1], a, max(24, mw * 1.3)))
    hx, hy = (150, -452) if pose == "stand" else (190, -440)
    if ear:
        e = affinity.rotate(ellipse(0, 0, 36, 13), -38, origin=(0, 0))
        parts.append(affinity.translate(e, hx - 38, hy + 2))
    if tail:
        parts.append(affinity.translate(affinity.rotate(ellipse(0, 0, 18, 10), -55 if pose == "stand" else -25, origin=(0, 0)),
                                        -220, -302 if pose == "stand" else -322))
    if antlers:
        far = antler((hx + 16, hy - 4), 0.78, kind, 1, 30, MINW / (s * 0.78))
        near = antler((hx - 6, hy - 2), 0.92, kind, 1, -8, MINW / (s * 0.92))
        parts += [far, near]
    g = U(parts)
    if rot:
        g = affinity.rotate(g, rot, origin=(0, -250))
    g = affinity.scale(g, flip * s, s, origin=(0, 0))
    return affinity.translate(g, x, y)


# ---------------------------------------------------------------- ornament parts
def ring(x, y, r, w):
    return circ(x, y, r + w / 2).difference(circ(x, y, r - w / 2))


def hanger(cx, ytop, neck=30):
    """Hanging loop (0.25 in hole at 6 in) + bead, sitting on the frame top at ytop."""
    ry = ytop - neck - 40
    loop = ring(cx, ry, 31, 22)
    stem = line([(cx, ry + 38), (cx, ytop + 8)], 22)
    bead = circ(cx, ytop - neck * 0.45, 20)
    return U([loop, stem, bead]), circ(cx, ry, 20)


def mirror(g, cx=500):
    return U([g, affinity.scale(g, -1, 1, origin=(cx, 0))])


def holly_sprig(x, y, s=1.0, rot=0):
    """Two holly leaves and three berries, centred on (x, y)."""
    g = U([holly_leaf(0, 0, 200, 92, 46), holly_leaf(0, 0, -20, 92, 46),
           circ(-16, -18, 17), circ(16, -18, 17), circ(0, -40, 17)])
    g = affinity.rotate(affinity.scale(g, s, s, origin=(0, 0)), rot, origin=(0, 0))
    return affinity.translate(g, x, y)


def snow_ground(cx, gy, R, cy, amp=16, phase=0.0):
    """Snowy hill clipped to the inside of a circular frame (cx, cy, R)."""
    top = [(x, gy - amp * math.sin((x - cx) / 140 + phase) - 10 * math.cos((x - cx) / 300)) for x in range(int(cx - R), int(cx + R) + 1, 5)]
    return circ(cx, cy, R - 4).intersection(poly(top + [(cx + R, cy + R + 10), (cx - R, cy + R + 10)]))


def stag_front(cx, top, s=1.0):
    """Front-facing stag head and neck. Returns (solid, holes)."""
    def P(x, y):
        return (cx + x * s, top + y * s)
    right = [(0, 0), (56, -2), (92, 20), (104, 60), (98, 110), (80, 160), (58, 215), (48, 262), (36, 292), (14, 306)]
    pts = [P(x, y) for x, y in right] + [P(0, 308)] + [P(-x, y) for x, y in right[::-1][:-1]]
    head = poly(catmull(pts, n=10))
    nr = [(0, 200), (60, 200), (66, 300), (96, 410), (170, 560), (250, 700)]
    neck = poly(catmull([P(x, y) for x, y in nr] + [P(-x, y) for x, y in nr[::-1]], n=10))
    ears, holes = [], []
    for sg in (1, -1):
        e = affinity.rotate(ellipse(0, 0, 74 * s, 30 * s), -sg * 22, origin=(0, 0))
        ears.append(affinity.translate(e, *P(sg * 156, 62)))
        ei = affinity.rotate(ellipse(0, 0, 46 * s, 12 * s), -sg * 22, origin=(0, 0))
        holes.append(affinity.translate(ei, *P(sg * 168, 58)))
        eye = affinity.rotate(ellipse(0, 0, 25 * s, 13 * s), sg * 14, origin=(0, 0))
        holes.append(affinity.translate(eye, *P(sg * 54, 118)))
    holes.append(poly([P(-30, 252), P(30, 252), P(0, 284)]).buffer(6 * s))
    ants = []
    for sg in (1, -1):
        beam = [(0, 0), (40, -40), (100, -70), (160, -130), (190, -210), (186, -290)]
        bp = catmull([P(sg * (30 + x), 6 + y) for x, y in beam], closed=False, n=8)
        n = len(bp)
        ants.append(limb(bp, [36 * s - 18 * s * k / (n - 1) for k in range(n)]))
        ls = LineString(bp)
        for t, a, L in ((0.18, -95, 92), (0.42, -100, 112), (0.62, -112, 100), (0.82, -128, 78)):
            q = ls.interpolate(ls.length * t)
            ang = a if sg > 0 else -180 - a
            mid = polar(q.x, q.y, L * s * 0.55, ang + sg * 6)
            tip = polar(*mid, L * s * 0.5, ang - sg * 12)
            ants.append(limb([(q.x, q.y), mid, tip], [24 * s, 20 * s, 17 * s]))
    return U([head, neck] + ears + ants), U(holes)


def hung_star(x, y_top, y, r, w=14):
    """Star hanging on a thread from the frame at y_top."""
    return U([line([(x, y_top), (x, y - r * 0.6)], w), star(x, y, r, r * 0.45)])


# ---------------------------------------------------------------- designs
C, R = (500, 520), 440


def framed(w=34):
    h, hh = hanger(500, C[1] - R)
    return [ring(*C, R, w), h], [hh]


def d1_stag_head():
    solid, holes = framed()
    s, h = stag_front(500, 400, 1.06)
    s = s.intersection(circ(*C, R))
    solid.append(s)
    holes.append(h)
    # holly sprig on the chest, outlined where it overlaps the neck
    hs = U([holly_leaf(470, 850, 192, 170, 70, 4), holly_leaf(530, 850, -12, 170, 70, 4)])
    solid.append(hs)
    holes.append(outline_cut(hs, s.buffer(-16), 14))
    holes += [circ(474, 826, 21), circ(526, 826, 21), circ(500, 788, 21)]   # berries
    return compose(solid, holes)


def d2_leaping_reindeer():
    solid, holes = framed()
    top = C[1] - R
    solid.append(crescent(268, 330, 96, 40, -30, 0.84))
    solid.append(rect(180, 250, 210, 300).intersection(circ(*C, R + 10)))
    solid.append(snow_ground(500, 850, R, C[1], 16))
    solid.append(pine(150, 870, 200, 120, 3))
    solid.append(pine(815, 870, 290, 170, 5))
    solid.append(pine(720, 870, 170, 110, 3))
    solid.append(deer("leap", "reindeer", 1.0, 560, 868, rot=-12))
    solid.append(hung_star(440, top, 214, 66))
    return compose(solid, holes)


def d3_forest_stag():
    solid, holes = framed()
    solid.append(crescent(250, 290, 96, 40, -28, 0.84))
    solid.append(snow_ground(500, 850, R, C[1], 14, 1.2))
    for (x, hgt, w, t) in ((140, 330, 150, 4), (245, 220, 116, 3), (840, 380, 170, 5), (750, 250, 124, 3)):
        solid.append(pine(x, 870, hgt, w, t))
    solid.append(deer("stand", "stag", 0.92, 470, 862))
    return compose(solid, holes)


def outline_cut(shape, region, gap=15):
    """Cut a gap-wide line around `shape`, but only inside `region` (so the
    shape stays attached wherever it leaves the region)."""
    return shape.buffer(gap, quad_segs=16).difference(shape).intersection(region)


def d4_scarf_reindeer():
    s, ox, oy = 1.2, 450, 872
    P = lambda x, y: (ox + x * s, oy + y * s)
    dr = deer("stand", "reindeer", s, ox, oy)
    solid, holes = [dr], []
    solid.append(base_strip(P(-270, 0)[0], P(250, 0)[0], P(0, -8)[1], P(0, 34)[1], drifts=((P(-150, 0)[0], 120, 16), (P(120, 0)[0], 150, 20))))
    # knitted scarf: a band round the neck and a long tail blowing back over the back
    band = poly([P(90, -404), P(150, -398), P(176, -392), P(174, -348), P(118, -352), P(84, -364)]).buffer(8 * s)
    path = catmull([(98, -386), (50, -396), (10, -428), (-36, -420), (-80, -446), (-126, -444)], closed=False, n=8)
    tail = U([taper(P(*a), P(*b), (40 + 14 * k / len(path)) * s, (40 + 14 * (k + 1) / len(path)) * s) for k, (a, b) in enumerate(zip(path[:-1], path[1:]))])
    end = path[-1]
    fringe = U([line([P(end[0] + 6 - 14 * k, end[1] - 6 + 10 * k), P(end[0] - 26 - 14 * k, end[1] - 26 + 10 * k)], 13)
                for k in range(3)])
    sc = U([band, tail, fringe])
    solid.append(sc)
    holes.append(outline_cut(band, dr.buffer(-18), 14))   # stops short of the neck edges: stays attached
    # knitted stripes across the tail
    for t in (0.3, 0.55):
        q = LineString([P(*p) for p in path]).interpolate(t, normalized=True)
        holes.append(ellipse(q.x, q.y, 9, 15 * s))
    holes.append(circ(*P(0, -270), 22))   # hanging hole through the back
    return compose(solid, holes)


def d5_stag_bauble():
    cx, cy, Rb = 500, 570, 400
    cap = rect(cx - 74, cy - Rb - 58, cx + 74, cy - Rb + 26, 10)
    h, hh = hanger(cx, cy - Rb - 58)
    solid, holes = [circ(cx, cy, Rb), cap, h], [hh]
    holes.append(rect(cx - 54, cy - Rb - 42, cx + 54, cy - Rb - 24, 8))   # cap groove
    sd = 1.28
    d = deer("stand", "stag", sd, 560 - 150 * sd, 640 + 452 * sd)
    holes.append(d.intersection(circ(cx, cy, Rb - 40)))
    for (x, y, r) in ((300, 330, 54), (230, 520, 40), (330, 660, 46), (790, 740, 40)):
        holes.append(snowflake(x, y, r, 16))
    return compose(solid, holes)


def scallop_frame(cx, cy, R, w=30, n=28, rr=26):
    outer = U([circ(cx, cy, R)] + [circ(*polar(cx, cy, R, 360 * k / n), rr) for k in range(n)])
    return outer.difference(circ(cx, cy, R - w))


def d6_reindeer_pair():
    cy, Rs = 540, 420
    h, hh = hanger(500, cy - Rs - 26)
    solid, holes = [scallop_frame(500, cy, Rs), h], [hh]
    solid.append(snow_ground(500, 850, Rs - 10, cy, 10))
    for x, f in ((262, 1), (738, -1)):
        solid.append(deer("stand", "reindeer", 0.76, x, 862, flip=f))
    solid.append(hung_star(500, cy - Rs + 10, 240, 66))
    return compose(solid, holes)


DESIGNS = {
    "01-stag-head-ornament": d1_stag_head,
    "02-leaping-reindeer-ornament": d2_leaping_reindeer,
    "03-woodland-stag-ornament": d3_forest_stag,
    "04-reindeer-with-scarf-ornament": d4_scarf_reindeer,
    "05-stag-bauble-ornament": d5_stag_bauble,
    "06-reindeer-pair-ornament": d6_reindeer_pair,
}


README = """WOODLAND REINDEER & STAG ORNAMENTS - 6 SVG CUT FILES
by Duskwood Designs Co (etsy.com/shop/DuskwoodDesignsCo)
Thank you for your purchase!

DESIGNS
  01 Stag Head Ornament (front-facing stag with holly)
  02 Leaping Reindeer Ornament (moon, star and snowy pines)
  03 Woodland Stag Ornament (stag in a pine wood under a crescent moon)
  04 Reindeer with Scarf Ornament (shaped ornament on a snowy base)
  05 Stag Bauble Ornament (classic bauble with a stag cut out of it)
  06 Reindeer Pair Ornament (two reindeer under a star, scalloped frame)

FILES
  SVG/  Cricut Design Space, Silhouette Designer Edition, Inkscape, Illustrator
  DXF/  Silhouette Studio Basic Edition, laser/CNC software (inches)
  PNG/  transparent background, 1800 px on the longest side (6 in at 300 DPI)

Each design is a single-layer shape with one clean cut path and a hanging
loop or hole built in. Stars, moons and trees are attached, so nothing
falls out. Default size is about 6 inches on the longest side; resize
freely, but keep the proportions locked.

SIZING TIPS
  Cardstock, glitter card, felt or vinyl: 4 in or larger.
  Laser-cut wood or acrylic (3 mm or thinner): 4.5 in or larger.
  The thinnest parts (antler tines and legs) are about 0.08 in wide at
  6 in, so do not go below 4 in, and do a test cut on a new material first.
  04 stands on its snowy base when cut from 3 mm wood or acrylic, or hang
  it by the hole in its back.

LICENSE
  Personal use: unlimited.
  Small-business commercial use: you may sell finished physical products
  (ornaments, decals, signs, shirts, cards, etc.) made with these designs,
  up to 500 units per design.
  You may NOT resell, share or redistribute the digital files themselves,
  in original or modified form, or include them in other digital products.
"""


# ---------------------------------------------------------------- export
PANELS = ()


def to_path(geom):
    polys = geom.geoms if geom.geom_type == "MultiPolygon" else [geom]
    d = []
    for p in polys:
        for r in [p.exterior, *p.interiors]:
            pts = list(r.coords)
            d.append("M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts[:-1]) + " Z")
    return " ".join(d)


def view_box(geom, square, pad=2):
    """(x, y, w, h): square box for standing pieces, tight box for panels."""
    x0, y0, x1, y1 = geom.bounds
    w, h = x1 - x0 + 2 * pad, y1 - y0 + 2 * pad
    if square:
        w = h = max(w, h)
    return (x0 + x1) / 2 - w / 2, (y0 + y1) / 2 - h / 2, w, h


def write_dxf(geom, path, vb):
    bx, by, w, h = vb
    k = SIZE_IN / max(w, h)
    doc = ezdxf.new("R2010")
    doc.header["$INSUNITS"] = 1
    doc.header["$MEASUREMENT"] = 0
    msp = doc.modelspace()
    polys = geom.geoms if geom.geom_type == "MultiPolygon" else [geom]
    for p in polys:
        for r in [p.exterior, *p.interiors]:
            msp.add_lwpolyline([((x - bx) * k, (h - (y - by)) * k) for x, y in list(r.coords)[:-1]], close=True)
    doc.saveas(path)


def stats(g):
    polys = list(g.geoms) if g.geom_type == "MultiPolygon" else [g]
    hs = [Polygon(i).area for p in polys for i in p.interiors]
    return {"parts": len(polys), "holes": len(hs), "smallest_hole": round(min(hs or [0]), 1), "valid": g.is_valid}


def check():
    """Verify the built files: one shape per design, holes >= MIN_HOLE, DXF
    re-opens in inches, PNG 1800 px transparent, ZIP layout."""
    import zipfile
    from PIL import Image
    ok = True
    zp = [f for f in os.listdir(HERE) if f.endswith(".zip")]
    if zp and not os.path.exists(os.path.join(HERE, "bundle", "PNG")):
        zipfile.ZipFile(os.path.join(HERE, zp[0])).extractall(os.path.join(HERE, "bundle"))   # check the shipped files
    for name, fn in DESIGNS.items():
        g = finish(fn())
        st = stats(g)
        svg = open(os.path.join(SVG_DIR, f"{name}.svg")).read()
        doc = ezdxf.readfile(os.path.join(DXF_DIR, f"{name}.dxf"))
        n_dxf = len(doc.modelspace().query("LWPOLYLINE"))
        xs = [x for e in doc.modelspace().query("LWPOLYLINE") for x, y, *_ in e.get_points()]
        ys = [y for e in doc.modelspace().query("LWPOLYLINE") for x, y, *_ in e.get_points()]
        dxf_long = max(max(xs) - min(xs), max(ys) - min(ys))
        im = Image.open(os.path.join(HERE, "bundle", "PNG", f"{name}.png"))
        good = (st["parts"] == 1 and st["valid"] and st["smallest_hole"] >= MIN_HOLE and svg.count("<path") == 1
                and n_dxf == 1 + st["holes"] and doc.header["$INSUNITS"] == 1 and 5.5 < dxf_long <= 6.0
                and max(im.size) == 1800 and im.mode == "RGBA" and im.getextrema()[3][0] == 0)
        ok &= good
        print(("OK  " if good else "FAIL"), name, st, f"dxf={n_dxf} polylines, {dxf_long:.2f} in", f"png={im.size}")
    if zp:
        names = zipfile.ZipFile(os.path.join(HERE, zp[0])).namelist()
        zok = all(any(n.startswith(d + "/") and n.endswith(e) for n in names) for d, e in (("SVG", ".svg"), ("PNG", ".png"), ("DXF", ".dxf")))
        zok &= "README-LICENSE.txt" in names and sum(n.endswith((".svg", ".png", ".dxf")) for n in names) == 18
        print(("OK  " if zok else "FAIL"), "zip", zp[0], len(names), "entries")
        ok &= zok
    print("ALL CHECKS PASS" if ok else "CHECKS FAILED")
    return ok


if __name__ == "__main__":
    if "--check" in sys.argv:
        sys.exit(0 if check() else 1)
    only = sys.argv[1:]
    meta = {}
    for name, fn in DESIGNS.items():
        if only and not any(o in name for o in only):
            continue
        g = finish(fn())
        vb = view_box(g, name not in PANELS)
        k = SIZE_IN / max(vb[2], vb[3])
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb[0]:.1f} {vb[1]:.1f} {vb[2]:.1f} {vb[3]:.1f}" '
               f'width="{vb[2] * k:.3f}in" height="{vb[3] * k:.3f}in"><path fill="#000" fill-rule="evenodd" d="{to_path(g)}"/></svg>')
        with open(os.path.join(SVG_DIR, f"{name}.svg"), "w") as f:
            f.write(svg)
        write_dxf(g, os.path.join(DXF_DIR, f"{name}.dxf"), vb)
        meta[name] = stats(g)
    with open(os.path.join(HERE, "bundle", "README-LICENSE.txt"), "w") as f:
        f.write(README)
    print(json.dumps(meta, indent=1))
