"""Raven & Mistletoe Ornaments - 6 single-path SVG/DXF cut files (gothic Christmas).

Hanging Christmas ornaments drawn in code (no AI images), built around solid
raven silhouettes: a raven on a branch under a crescent moon, a bauble with a
flying raven cut out, a raven perched on a candle-lit gothic lantern, two
ravens kissing under mistletoe in a gothic arched window, a raven on a
crescent moon, and a raven flying through a mistletoe wreath. Every design
has a hanging loop and is unioned into ONE connected polygon; stars,
mistletoe and moons are attached, never floating. Ravens are solid shapes
(no thin-line faces); the only cut-out detail on a bird is a round eye about
0.18 in across at 6 in. compose() closes solid parts by a few units so
near-touching pieces are bridged, then cuts the openings; finish() closes
then opens by 6.5 units (no material or gap narrower than ~13 units) and
fills any hole under MIN_HOLE. Coordinates are SVG-style (y down),
~1000-unit canvas. Artwork is scaled so the longest side is a full 6 in.

Usage:  python3 gen.py            build bundle/SVG + bundle/DXF + README
        python3 gen.py --check    verify the files (unzips the ZIP into bundle/ if needed)
Helpers are reused from bundles 021, 020, 008 and 006.
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


HOLLY = [(0.0, 0.0), (0.24, 0.40), (0.50, 0.50), (0.76, 0.38), (1.0, 0.0)]


def holly(x0, y0, ang, L, W, depth=1.0):
    """Holly leaf from its stalk end (x0, y0) pointing at ang (deg): three
    spikes a side joined by scooped edges, L long and about W/2 wide. Big
    enough (L >= 150) that the spikes survive finish()'s 6.5-unit rounding."""
    def edge(sg):
        out = []
        pts = [(x * L, sg * y * W) for x, y in HOLLY]
        for i, (a, b) in enumerate(zip(pts[:-1], pts[1:])):
            mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
            d = math.hypot(b[0] - a[0], b[1] - a[1])
            dp = depth * (0.45 if i == 0 else 1.0)    # gentler scoop next to the stalk
            nx, ny = -(b[1] - a[1]) / d, (b[0] - a[0]) / d
            if ny * sg > 0:                           # scoop toward the midrib
                nx, ny = -nx, -ny
            cx, cy = mx + nx * dp * d * 0.5, my + ny * dp * d * 0.5
            for k in range(12):
                t = k / 12
                out.append(((1 - t) ** 2 * a[0] + 2 * t * (1 - t) * cx + t * t * b[0],
                            (1 - t) ** 2 * a[1] + 2 * t * (1 - t) * cy + t * t * b[1]))
        out.append(pts[-1])
        return out
    lf = Polygon(edge(-1) + edge(1)[::-1][1:-1]).buffer(0)
    return affinity.translate(affinity.rotate(lf, ang, origin=(0, 0)), x0, y0)


def ellipse(cx, cy, rx, ry):
    return affinity.translate(affinity.scale(Point(0, 0).buffer(1, 48), rx, ry), cx, cy)


def taper(p0, p1, w0, w1):
    a = math.atan2(p1[1] - p0[1], p1[0] - p0[0]) + math.pi / 2
    c, s = math.cos(a), math.sin(a)
    q = poly([(p0[0] + c * w0 / 2, p0[1] + s * w0 / 2), (p1[0] + c * w1 / 2, p1[1] + s * w1 / 2),
              (p1[0] - c * w1 / 2, p1[1] - s * w1 / 2), (p0[0] - c * w0 / 2, p0[1] - s * w0 / 2)])
    return U([q, circ(*p0, w0 / 2), circ(*p1, w1 / 2)])


MINW = 15.0   # thinnest leg / antler tine after scaling (0.09 in at 6 in)


def limb(pts, ws):
    """Tapered leg / branch through joints pts with widths ws (one per joint)."""
    return U([taper(a, b, wa, wb) for a, b, wa, wb in zip(pts[:-1], pts[1:], ws[:-1], ws[1:])])


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


def snow_ground(cx, gy, R, cy, amp=16, phase=0.0):
    """Snowy hill clipped to the inside of a circular frame (cx, cy, R)."""
    top = [(x, gy - amp * math.sin((x - cx) / 140 + phase) - 10 * math.cos((x - cx) / 300)) for x in range(int(cx - R), int(cx + R) + 1, 5)]
    return circ(cx, cy, R - 4).intersection(poly(top + [(cx + R, cy + R + 10), (cx - R, cy + R + 10)]))


def hung_star(x, y_top, y, r, w=14):
    """Star hanging on a thread from the frame at y_top."""
    return U([line([(x, y_top), (x, y - r * 0.6)], w), star(x, y, r, r * 0.45)])




# ---------------------------------------------------------------- raven
CUT = 24.0    # every designed cut line is at least this wide (0.14 in at 6 in)


def _place(g, s, x, y, flip, rot):
    g = affinity.scale(g, s * flip, s, origin=(0, 0))
    if rot:
        g = affinity.rotate(g, rot, origin=(0, 0))
    return affinity.translate(g, x, y)


# Perched raven in profile facing right, feet at (0, 0), about 390 long and
# 350 tall: heavy arched beak, shaggy throat hackles, wedge tail angled down
# past the perch, one wide cut line for the folded wing.
PERCH_BODY = [(100, -270), (76, -292), (40, -294), (6, -276), (-22, -240), (-54, -198), (-92, -152),
              (-124, -104), (-156, -46), (-186, 10), (-214, 58), (-222, 80), (-200, 84), (-170, 58),
              (-132, 22), (-84, 6), (-34, 8), (8, -2), (40, -30), (64, -72), (78, -122), (84, -166),
              (94, -200), (100, -226)]
PERCH_BEAK = [(84, -276), (126, -276), (162, -262), (192, -230), (160, -230), (124, -222), (92, -208)]
PERCH_HACKLES = [[(92, -214), (116, -196), (84, -186)], [(86, -190), (108, -168), (78, -160)], [(80, -164), (98, -140), (72, -134)]]
PERCH_WING = [(36, -196), (-20, -150), (-80, -86), (-126, -22)]


def raven_perch(s=1.0, x=0, y=0, flip=1, rot=0, wing=False, feet=True, eye=True):
    body = poly(catmull(PERCH_BODY, n=10))
    parts = [body, poly(PERCH_BEAK).buffer(5).buffer(-5)] + [poly(h).buffer(4) for h in PERCH_HACKLES]
    if feet:
        for fx in (-30, 12):
            parts.append(line([(fx, -12), (fx + 4, 22)], 20))
            for a in (-14, 30, 196):   # toes round the branch
                parts.append(line([(fx + 4, 22), polar(fx + 4, 22, 30, a)], 15))
    holes = []
    if eye:
        holes.append(circ(66, -256, 15))
    if wing:
        wp = catmull(PERCH_WING, closed=False, n=8)
        holes.append(limb(wp, [CUT] * len(wp)))
    return _place(U(parts), s, x, y, flip, rot), [_place(h, s, x, y, flip, rot) for h in holes]


# Flying raven in profile facing right, body centre at (0, 0): near wing
# raised with five fingered primaries, far wing tip peeking behind it,
# wedge tail, heavy beak.
FLY_BODY = [(150, -52), (110, -60), (60, -50), (0, -42), (-80, -34), (-130, -26), (-150, -24), (-236, -52), (-250, -50), (-270, -8),
            (-250, 30), (-236, 32), (-150, 26), (-120, 30), (-60, 50), (20, 62), (90, 46), (140, 22), (172, -6), (172, -32)]
FLY_BEAK = [(156, -46), (200, -42), (248, -18), (206, -6), (166, 0)]
# raised near wing: leading edge to the wrist, five fingers, scalloped trailing edge
FLY_WING = [(76, -30), (68, -96), (44, -164), (8, -224), (-28, -266),
            (-64, -336), (-74, -284), (-108, -340), (-108, -276), (-150, -326), (-138, -262),
            (-188, -302), (-162, -244), (-216, -268), (-176, -214),
            (-190, -186), (-156, -160), (-168, -132), (-126, -112), (-134, -86), (-86, -62), (-40, -30)]


def raven_fly(s=1.0, x=0, y=0, flip=1, rot=0, eye=True, far=True):
    wing = poly(FLY_WING).buffer(8, quad_segs=8).buffer(-8, quad_segs=8)
    parts = [wing, poly(catmull(FLY_BODY, n=10)), poly(FLY_BEAK).buffer(5).buffer(-5)]
    if far:   # far wing: lowered, its fingers showing below the body
        fw = affinity.scale(poly(FLY_WING).buffer(8).buffer(-8), 0.62, -0.5, origin=(40, 0))
        parts.append(affinity.translate(fw, -10, 30))
    holes = [circ(140, -24, 14)] if eye else []
    return _place(U(parts), s, x, y, flip, rot), [_place(h, s, x, y, flip, rot) for h in holes]


# ---------------------------------------------------------------- mistletoe
def leaf(x0, y0, ang, L, W):
    """Mistletoe leaf from its stalk end: a blunt paddle, narrow at the
    stalk, widest near the rounded tip (no points, so it never reads as a
    spiky leaf)."""
    pts = []
    for k in range(41):
        t = k / 40
        if t < 0.72:
            w = W / 2 * (0.32 + 0.68 * min(1, t / 0.55) ** 0.9)
        else:
            w = W / 2 * math.sqrt(max(0, 1 - ((t - 0.72) / 0.28) ** 2))
        pts.append((t * L, w))
    pts += [(x, -y) for x, y in pts[::-1][1:-1]]
    return affinity.translate(affinity.rotate(poly(pts), ang, origin=(0, 0)), x0, y0)


def leaf_pair(x, y, ang, L, W, open_=26):
    return U([leaf(x, y, ang - open_, L, W), leaf(x, y, ang + open_, L, W)])


def mistletoe(x, y, ang=90, s=1.0, stem=80, L=130, W=50, br=22, spread=(28, 78)):
    """Mistletoe sprig hanging from (x, y) along ang: a stem to a node, a
    long pair of paddle leaves in a V with a shorter pair outside it, and a
    cluster of three berries sitting on the node above them."""
    nx, ny = polar(x, y, stem * s, ang)
    parts = [line([(x, y), (nx, ny)], 16 * s)]
    for d, k in zip(spread, (1.0, 0.78)):
        for sg in (-1, 1):
            parts.append(line([(nx, ny), polar(nx, ny, 34 * s, ang + sg * d)], 14 * s))
            parts.append(leaf(*polar(nx, ny, 28 * s, ang + sg * d), ang + sg * d, L * k * s, W * s))
    for (dx, dy) in ((0, 14), (-24, -10), (24, -10)):
        q = (nx + (dx * math.cos(math.radians(ang - 90)) - dy * math.sin(math.radians(ang - 90))) * s,
             ny + (dx * math.sin(math.radians(ang - 90)) + dy * math.cos(math.radians(ang - 90))) * s)
        parts.append(circ(*q, br * s))
    return U(parts)


# ---------------------------------------------------------------- designs
C, R = (500, 520), 440


def framed(w=34):
    h, hh = hanger(500, C[1] - R)
    return [ring(*C, R, w), h], [hh]


def branch(pts, w0, w1, n=8):
    bp = catmull(pts, closed=False, n=n)
    return limb(bp, [w0 + (w1 - w0) * k / (len(bp) - 1) for k in range(len(bp))])


def d1_moonlit_raven():
    """Raven perched on a bare branch across a round frame, a big crescent
    moon behind, mistletoe and a star hanging from the frame."""
    solid, holes = framed()
    solid.append(crescent(330, 300, 170, 70, -48, 0.84))
    solid.append(branch([(40, 800), (200, 770), (380, 772), (560, 770), (760, 740), (960, 700)], 34, 22))
    solid.append(branch([(700, 752), (780, 800), (850, 812)], 20, 16))
    r, rh = raven_perch(1.2, 520, 762)
    solid.append(r); holes += rh
    solid.append(mistletoe(650, 90, 90, 1.1, stem=90))
    solid.append(hung_star(860, 200, 320, 44))
    return compose(solid, holes)


def bauble(cx=500, cy=570, Rb=400):
    cap = rect(cx - 74, cy - Rb - 58, cx + 74, cy - Rb + 26, 10)
    h, hh = hanger(cx, cy - Rb - 58)
    return [circ(cx, cy, Rb), cap, h], [hh, rect(cx - 54, cy - Rb - 42, cx + 54, cy - Rb - 24, 8)]


def d2_raven_bauble():
    """Classic bauble with a flying raven, a mistletoe sprig and stars cut out."""
    solid, holes = bauble()
    r, rh = raven_fly(1.04, 530, 700)
    holes.append(r)
    holes.append(mistletoe(640, 250, 90, 0.95, stem=36))
    for (x, y, rr) in ((300, 330, 38), (420, 260, 24), (200, 560, 28), (320, 900, 30), (700, 890, 36), (840, 600, 26)):
        holes.append(star(x, y, rr, rr * 0.5))
    return compose(solid, holes)


def d3_raven_lantern():
    """Raven perched on top of a gothic lantern with a candle glowing in
    each arched window; a mistletoe sprig hangs from the roof ledge. The
    hanging loop sits on the raven's back."""
    cx, top = 500, 330
    solid, holes, light = [], [], []
    solid.append(arch(cx, 440, 130, top).intersection(box(0, 0, 1000, 440)))   # dome
    solid.append(rect(cx - 15, top - 150, cx + 15, top + 10))                  # finial post the raven stands on
    solid.append(rect(cx - 34, top - 158, cx + 34, top - 134, 8))
    solid.append(rect(cx - 250, 436, cx + 250, 478, 10))                       # roof ledge
    solid.append(rect(cx - 160, 470, cx + 160, 900, 6))                        # body
    solid.append(rect(cx - 190, 896, cx + 190, 940, 10))                       # base plate
    solid.append(poly([(cx - 70, 936), (cx + 70, 936), (cx, 1000)]).buffer(8))  # finial below
    for dx in (-80, 80):                                                       # two pointed-arch windows
        holes.append(arch(cx + dx, 640, 56, 510).intersection(box(0, 0, 1000, 860)))
        light.append(rect(cx + dx - 22, 730, cx + dx + 22, 870, 4))            # candle
        light.append(poly(catmull([(cx + dx, 616), (cx + dx + 24, 668), (cx + dx + 17, 700), (cx + dx, 712),
                                   (cx + dx - 17, 700), (cx + dx - 24, 668)], n=8)))   # flame
        light.append(line([(cx + dx, 700), (cx + dx, 740)], 18))               # wick
    s, fx = 0.86, cx - 10
    r, rh = raven_perch(s, fx, top - 158)
    solid.append(r); holes += rh
    h, hh = hanger(fx + 20 * s, top - 158 - 270 * s, neck=10)
    solid.append(h); holes.append(hh)
    solid.append(mistletoe(cx + 240, 470, 66, 0.95, stem=50))
    return U([compose(solid, holes)] + light)


def arch(cx, base, half, apex):
    """Pointed (gothic) arch: two circle arcs meeting at the apex."""
    h = base - apex
    # circles centred on the base line at cx +/- (r - half) passing through the apex
    r = (h * h + half * half) / (2 * half) if h > half else 2 * half
    d = r - half
    left = circ(cx + d, base, r)
    right = circ(cx - d, base, r)
    top = left.intersection(right)
    return U([top.intersection(box(0, 0, 1000, base)), box(cx - half, base - 1, cx + half, 1000)])


def d4_gothic_window():
    """Two ravens facing each other on the sill of a gothic arched window,
    a mistletoe sprig hanging from the point of the arch between them."""
    cx, base, half, apex, w, sill = 500, 560, 380, 80, 34, 880
    outer = arch(cx, base, half, apex).intersection(box(0, 0, 1000, sill + 50))
    inner = arch(cx, base, half - w, apex + w * 1.6).intersection(box(0, 0, 1000, sill))
    solid = [outer.difference(inner), rect(cx - half - 26, sill, cx + half + 26, sill + 56, 8)]
    h, hh = hanger(cx, apex)
    solid.append(h); holes = [hh]
    for x, f in ((300, 1), (700, -1)):
        r, rh = raven_perch(1.15, x, sill, flip=f)
        solid.append(r); holes += rh
    solid.append(mistletoe(cx, apex + 40, 90, 1.4, stem=50))
    return compose(solid, holes)


def d5_raven_moon():
    """Raven perched on the lower horn of a slim crescent moon, a mistletoe
    sprig and a star hanging inside the curve."""
    mc, mR = (420, 500), 400
    moon = crescent(*mc, mR, 210, -60, 0.9)
    solid = [moon]
    h, hh = hanger(mc[0] - 30, mc[1] - mR + 4)
    solid.append(h); holes = [hh]
    r, rh = raven_perch(1.1, 600, 862)
    solid.append(r); holes += rh
    ic = (mc[0] + 210, mc[1] - 60)
    solid.append(mistletoe(*polar(*ic, mR * 0.9 + 10, -120), 90, 1.0, stem=120))
    for (x, y, rr) in ((150, 470, 46), (210, 650, 34), (130, 300, 30)):
        holes.append(star(x, y, rr, rr * 0.5))
    return compose(solid, holes)


def d6_mistletoe_wreath():
    """Mistletoe wreath (leaves all sweeping one way round a ring, berry
    clusters between) with a raven flying through the middle."""
    cx, cy, Rw = 500, 540, 360
    h, hh = hanger(cx, cy - Rw - 60)
    solid, holes = [ring(cx, cy, Rw, 30), h, rect(cx - 12, cy - Rw - 70, cx + 12, cy - Rw, 4)], [hh]
    n = 30
    for k in range(n):
        th = -90 + 360 * (k + 0.5) / n
        bx, by = polar(cx, cy, Rw, th)
        out = 1 if k % 2 == 0 else -1
        solid.append(leaf(bx, by, th + 90 - out * 30, 112, 44))
        if k % 5 == 2:
            for a, rr in ((0, 0), (120, 1), (240, 1)):
                solid.append(circ(*polar(*polar(cx, cy, Rw + 40, th), 30 * rr, a + th), 24))
    r, rh = raven_fly(1.2, cx + 20, cy + 50)
    solid.append(r); holes += rh
    return compose(solid, holes)


DESIGNS = {
    "01-moonlit-raven-ornament": d1_moonlit_raven,
    "02-raven-bauble-ornament": d2_raven_bauble,
    "03-raven-lantern-ornament": d3_raven_lantern,
    "04-gothic-window-ravens-ornament": d4_gothic_window,
    "05-raven-on-the-moon-ornament": d5_raven_moon,
    "06-mistletoe-wreath-raven-ornament": d6_mistletoe_wreath,
}


README = """RAVEN & MISTLETOE ORNAMENTS - 6 SVG CUT FILES
by Duskwood Designs Co (etsy.com/shop/DuskwoodDesignsCo)
Thank you for your purchase!

DESIGNS
  01 Moonlit Raven Ornament (raven on a branch, crescent moon, mistletoe, star)
  02 Raven Bauble Ornament (bauble with a flying raven, mistletoe and stars cut out)
  03 Raven Lantern Ornament (raven perched on a candle-lit gothic lantern)
  04 Gothic Window Ravens Ornament (two ravens under mistletoe in an arched window)
  05 Raven on the Moon Ornament (raven on a crescent moon with mistletoe)
  06 Mistletoe Wreath Raven Ornament (raven flying through a mistletoe wreath)

FILES
  SVG/  Cricut Design Space, Silhouette Designer Edition, Inkscape, Illustrator
  DXF/  Silhouette Studio Basic Edition, laser/CNC software (inches)
  PNG/  transparent background, 1800 px on the longest side (6 in at 300 DPI)

Each design is a single-layer shape with one clean cut path and a hanging
loop built in. Stars, moons, mistletoe and candle flames are attached, so
nothing falls out. Default size is about 6 inches on the longest side;
resize freely, but keep the proportions locked.

SIZING TIPS
  Cardstock, glitter card, felt or vinyl: 4 in or larger.
  Laser-cut wood or acrylic (3 mm or thinner): 4.5 in or larger.
  The thinnest parts (raven toes and mistletoe stems) are about 0.08 in
  wide at 6 in, so do not go below 4 in, and do a test cut on a new
  material first.

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
