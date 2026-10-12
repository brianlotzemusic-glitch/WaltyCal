"""Winter Mushroom & Toadstool Ornaments - 6 single-path SVG/DXF cut files.

Woodland Christmas ornaments drawn in code (no AI images), all built around
spotted fly-agaric toadstools: a toadstool trio in a snowy round frame, a
toadstool cottage, a bauble with mushrooms cut out of it, a woodland
gnome beside a big toadstool, a crescent moon with toadstools, and a snow
globe.
Each has a hanging loop built in. Everything is unioned into ONE connected
polygon; stars and trees are attached, never floating. compose() closes solid
parts by a few units so near-touching pieces are bridged, then cuts the
openings; finish() closes then opens by 6.5 units (no material or gap
narrower than ~13 units) and fills any hole under MIN_HOLE. Coordinates are
SVG-style (y down), ~1000-unit canvas, scaled so the longest side is 6 in.

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
    """Snowy pine standing on ground line gy (from 008/021)."""
    trunk = trunk if trunk is not None else h * 0.09
    tw = max(16, w * 0.12)
    parts = [rect(cx - tw / 2, gy - trunk - 10, cx + tw / 2, gy + 2)]
    top, yb = gy - h, gy - trunk
    ch = yb - top
    seg = ch / (tiers * 0.78 + 0.22)
    for i in range(tiers):
        apex = top + i * seg * 0.78
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
        parts.append(poly([(cx, apex)] + right + bottom + left))
    return U(parts)


def areal(g):
    if g.geom_type in ("Polygon", "MultiPolygon"):
        return g
    return U([p for p in getattr(g, "geoms", []) if p.geom_type in ("Polygon", "MultiPolygon")])


def compose(solid, holes, bridge=8):
    """Union the solid parts, close them by `bridge`, then cut the openings.
    Ring-shaped cut-outs are filled first so nothing floats inside them."""
    S = U(solid).buffer(bridge, quad_segs=16).buffer(-bridge, quad_segs=16)
    H = areal(U(holes))
    H = U([Polygon(p.exterior) for p in (H.geoms if H.geom_type == "MultiPolygon" else [H])])
    return S.difference(H)


def finish(g, r=6.5, simplify=0.12):
    """Close then open by r (no gaps or material under ~2r), drop small holes."""
    g = areal(make_valid(g))
    g = g.buffer(r, quad_segs=16).buffer(-r, quad_segs=16)
    g = g.buffer(-r, quad_segs=16).buffer(r, quad_segs=16)
    g = areal(set_precision(areal(make_valid(g.simplify(simplify))), 0.05))
    polys = list(g.geoms) if g.geom_type == "MultiPolygon" else [g]
    polys = [p for p in polys if p.area > 1500]
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


def ellipse(cx, cy, rx, ry):
    return affinity.translate(affinity.scale(Point(0, 0).buffer(1, 48), rx, ry), cx, cy)


def taper(p0, p1, w0, w1):
    a = math.atan2(p1[1] - p0[1], p1[0] - p0[0]) + math.pi / 2
    c, s = math.cos(a), math.sin(a)
    q = poly([(p0[0] + c * w0 / 2, p0[1] + s * w0 / 2), (p1[0] + c * w1 / 2, p1[1] + s * w1 / 2),
              (p1[0] - c * w1 / 2, p1[1] - s * w1 / 2), (p0[0] - c * w0 / 2, p0[1] - s * w0 / 2)])
    return U([q, circ(*p0, w0 / 2), circ(*p1, w1 / 2)])


def limb(pts, ws):
    return U([taper(a, b, wa, wb) for a, b, wa, wb in zip(pts[:-1], pts[1:], ws[:-1], ws[1:])])


def ring(x, y, r, w):
    return circ(x, y, r + w / 2).difference(circ(x, y, r - w / 2))


def hanger(cx, ytop, neck=30):
    """Hanging loop (0.25 in hole at 6 in) + bead, sitting on the frame top at ytop."""
    ry = ytop - neck - 40
    loop = ring(cx, ry, 31, 22)
    stem = line([(cx, ry + 38), (cx, ytop + 8)], 22)
    bead = circ(cx, ytop - neck * 0.45, 20)
    return U([loop, stem, bead]), circ(cx, ry, 20)


def hung_star(x, y_top, y, r, w=14):
    """Star hanging on a thread from y_top."""
    return U([line([(x, y_top), (x, y - r * 0.6)], w), star(x, y, r, r * 0.45)])


def snow_ground(cx, gy, R, cy, amp=16, phase=0.0):
    """Snowy hill clipped to the inside of a circular frame (cx, cy, R)."""
    top = [(x, gy - amp * math.sin((x - cx) / 140 + phase) - 10 * math.cos((x - cx) / 300)) for x in range(int(cx - R), int(cx + R) + 1, 5)]
    return circ(cx, cy, R - 4).intersection(poly(top + [(cx + R, cy + R + 10), (cx - R, cy + R + 10)]))


def mound(x0, x1, gy, depth, amp=10, phase=0.0):
    """Free-standing snowy mound from x0 to x1 with a gently wavy top at gy."""
    top = [(x, gy - amp * math.sin((x - x0) / 90 + phase)) for x in range(int(x0), int(x1) + 1, 5)]
    m = poly(top + [(x1, gy + depth), (x0, gy + depth)])
    return m.buffer(-24).buffer(24, quad_segs=16)


# ---------------------------------------------------------------- toadstools
CAP = [(-0.50, 0.03), (-0.47, -0.30), (-0.37, -0.68), (-0.19, -0.94), (0.0, -1.0), (0.19, -0.94),
       (0.37, -0.68), (0.47, -0.30), (0.50, 0.03), (0.30, 0.11), (0.0, 0.14), (-0.30, 0.11)]


def cap_shape(cw, ch):
    return poly(catmull([(x * cw, y * ch) for x, y in CAP], n=10))


def toadstool(cx, gy, H, cw, ch, sw, tilt=0, spots=7, seed=1, skirt=True, rmax=None):
    """Fly agaric standing on ground line gy, cap rim H above the ground.
    cw/ch: cap width/height; sw: stem width. Returns (solid, holes): the
    spots are cut-outs (one near the crown first, so a small cap never ends
    up with just two side-by-side 'eyes')."""
    yb = gy - H
    L = [(-0.66, 0.0), (-0.74, -0.10), (-0.66, -0.26), (-0.52, -0.48), (-0.45, -0.75), (-0.42, -1.0)]
    sh = H + ch * 0.1
    left = [(cx + sw * x, gy + sh * y) for x, y in L]
    stem = poly(catmull(left, closed=False, n=8) + [(2 * cx - x, y) for x, y in catmull(left, closed=False, n=8)[::-1]])
    solid = [stem]
    holes_l = []
    if skirt and H > 120:
        ys = yb + 0.16 * H
        solid.append(poly([(cx - sw * 0.44, ys - 10), (cx + sw * 0.44, ys - 10), (cx + sw * 0.66, ys + 0.09 * H),
                           (cx - sw * 0.66, ys + 0.09 * H)]).buffer(5))
    cap = cap_shape(cw, ch)
    zone = cap.buffer(-17)
    rnd = random.Random(seed * 31 + 7)
    rmax = rmax or max(19, cw * 0.064)
    rmin = max(17.5, cw * 0.042)
    placed = []
    if spots:
        e0 = ellipse(0.04 * cw, -0.62 * ch, rmax, rmax * 0.8)
        if zone.contains(e0):
            placed.append(e0)
    for k in range(1500):
        if len(placed) >= spots:
            break
        r = rmax - (rmax - rmin) * min(1, k / 900)
        x, y = rnd.uniform(-cw / 2, cw / 2), rnd.uniform(-ch, 0.1 * ch)
        e = ellipse(x, y, r, r * 0.8)
        if zone.contains(e.buffer(1)) and all(e.distance(o) >= 19 for o in placed):
            placed.append(e)
    holes_l += placed
    tr = lambda g: affinity.translate(affinity.rotate(g, tilt, origin=(0, 0)), cx, yb)
    solid.append(tr(cap))
    return solid, [tr(h) for h in holes_l]


def add(solid, holes, parts):
    s, h = parts
    solid += s
    holes += h


def outline_cut(shape, region, gap=16):
    return shape.buffer(gap, quad_segs=16).difference(shape).intersection(region)


# ---------------------------------------------------------------- designs
C, R = (500, 520), 440


def framed(w=34):
    h, hh = hanger(500, C[1] - R)
    return [ring(*C, R, w), h], [hh]


def d1_toadstool_trio():
    """Three toadstools on a snowy hill in a round frame, with stars hanging
    from the frame and snowflakes cut into the snow."""
    solid, holes = framed()
    solid.append(snow_ground(500, 850, R, C[1], 12, 0.6))
    add(solid, holes, toadstool(560, 862, 330, 380, 200, 92, tilt=5, spots=9, seed=3))
    add(solid, holes, toadstool(300, 866, 200, 230, 128, 62, tilt=-12, spots=6, seed=5))
    add(solid, holes, toadstool(790, 862, 132, 150, 86, 44, tilt=14, spots=4, seed=8))
    for x in (420, 690):
        holes.append(snowflake(x, 906, 26, 14))
    top = lambda x: C[1] - math.sqrt((R - 10) ** 2 - (x - 500) ** 2)
    solid.append(hung_star(330, top(330), 300, 58))
    solid.append(hung_star(770, top(770), 330, 44))
    return compose(solid, holes)


def d2_toadstool_cottage():
    """A toadstool house: spotted cap roof with a chimney, a
    stem cottage with round cross-paned windows and an arched door, a lantern
    on a post and a little toadstool, on a snowy mound."""
    solid, holes = [], []
    cx, rim = 500, 470
    cw, ch = 680, 310
    cap = affinity.translate(cap_shape(cw, ch), cx, rim)
    h, hh = hanger(cx, rim - ch + 6)
    solid += [h]
    holes += [hh]
    # chimney (behind the cap, left)
    solid.append(rect(270, 250, 330, 380, 6))
    solid.append(rect(258, 236, 342, 268, 8))
    # house body
    body = [(-0.30, 0), (-0.33, 0.35), (-0.37, 0.75), (-0.40, 1.0), (0.40, 1.0), (0.37, 0.75), (0.33, 0.35), (0.30, 0)]
    gy = 880
    hb = poly(catmull([(cx + x * cw * 0.62, rim - 20 + y * (gy + 12 - rim + 20)) for x, y in body], n=8))
    solid.append(hb)
    solid.append(cap)
    # spots on the roof
    zone = cap.buffer(-17)
    for (x, y, r) in ((500, 228, 36), (392, 262, 30), (618, 270, 32), (300, 340, 30), (470, 320, 26), (560, 350, 30),
                      (700, 352, 28), (380, 392, 26), (240, 420, 22), (650, 420, 24), (480, 420, 22), (770, 430, 20)):
        e = ellipse(x, y, r, r * 0.78)
        if zone.contains(e):
            holes.append(e)
    # gill line under the roof edge
    holes.append(LineString([(cx - cw * 0.40, rim + 12), (cx, rim + 32), (cx + cw * 0.40, rim + 12)]).buffer(8).intersection(cap.buffer(-14)))
    # round windows with cross panes
    for wx in (402, 598):
        win = circ(wx, 600, 46)
        holes.append(win.difference(U([rect(wx - 8, 540, wx + 8, 660), rect(wx - 60, 592, wx + 60, 608)])))
    # arched door with planks and a knob (door stays attached at the bottom)
    door = U([rect(450, 735, 550, gy), circ(500, 735, 50)])
    holes.append(outline_cut(door, rect(0, 0, 1000, gy - 4), 16))
    win = circ(500, 750, 26)                                            # little round window in the door
    holes.append(win.difference(U([rect(492, 700, 508, 800), rect(450, 742, 550, 758)])))
    holes.append(circ(533, 808, 16))                                    # knob
    # snowy mound, stepping stones
    solid.append(mound(170, 830, gy, 70, 8, 1.0))
    for x, y, rx in ((500, 912, 40), (420, 924, 30), (585, 924, 30)):
        holes.append(ellipse(x, y, rx, 12.5))
    # lantern on a crook post (right)
    solid.append(line([(770, gy), (770, 650)], 22))
    solid.append(limb(catmull([(770, 660), (790, 628), (830, 630), (842, 660)], closed=False, n=6), [18] * 19))
    lan = U([rect(816, 690, 868, 760, 6), poly([(808, 692), (876, 692), (842, 664)]), rect(812, 756, 872, 770, 4)])
    solid += [lan, line([(842, 660), (842, 680)], 14)]
    holes.append(rect(828, 704, 856, 748, 4))
    # small toadstool (left) + grass
    add(solid, holes, toadstool(222, gy + 4, 120, 150, 84, 42, tilt=-10, spots=3, seed=2, skirt=False))
    return compose(solid, holes)


def d3_mushroom_bauble():
    """Classic bauble with three toadstools cut out of it (cap and stem split
    by a gill band), snowflakes and a pine sprig line."""
    cx, cy, Rb = 500, 570, 400
    cap = rect(cx - 74, cy - Rb - 58, cx + 74, cy - Rb + 26, 10)
    h, hh = hanger(cx, cy - Rb - 58)
    solid, holes = [circ(cx, cy, Rb), cap, h], [hh]
    holes.append(rect(cx - 54, cy - Rb - 42, cx + 54, cy - Rb - 24, 8))
    inner = circ(cx, cy, Rb - 40)
    for (x, gy, H, cw, chh, sw, tilt) in ((520, 860, 300, 330, 170, 84, 4), (300, 830, 180, 200, 108, 56, -12),
                                          (720, 840, 150, 170, 92, 48, 12)):
        s, _ = toadstool(x, gy, H, cw, chh, sw, tilt=tilt, spots=0, skirt=False)
        stem, capg = s[0], s[-1]
        holes.append(capg.intersection(inner))
        holes.append(stem.difference(capg.buffer(18)).intersection(inner))
    # snowy ground band left solid; snowflakes in the sky
    for (x, y, r) in ((330, 330, 42), (690, 320, 44), (505, 285, 30), (225, 480, 30), (800, 520, 34)):
        holes.append(snowflake(x, y, r, 16))
    return compose(solid, holes)


def gnome(x, gy, s=1.0, flip=1):
    """Woodland gnome facing out: floppy pointed hat with a pompom and a cut
    hat band, round nose, long beard with cut strands over a coat, two boots.
    Returns (solid, holes)."""
    T = lambda g: affinity.translate(affinity.scale(g, flip * s, s, origin=(0, 0)), x, gy)
    hat = poly(catmull([(-132, -276), (-118, -360), (-80, -450), (-20, -530), (60, -572), (128, -556), (168, -506),
                        (176, -452), (150, -470), (122, -500), (84, -494), (80, -430), (102, -350), (132, -276)], n=10))
    brim = rect(-148, -300, 148, -248, 22)
    pom = circ(178, -436, 32)
    coat = poly(catmull([(-104, -240), (-140, -120), (-150, -40), (150, -40), (140, -120), (104, -240)], n=8))
    beard = poly(catmull([(-108, -262), (-120, -196), (-98, -128), (-56, -80), (0, -62), (56, -80), (98, -128), (120, -196),
                          (108, -262)], n=10))
    nose = ellipse(0, -250, 54, 46)
    boots = U([ellipse(-62, -24, 58, 26), ellipse(62, -24, 58, 26)])
    arms = U([ellipse(-150, -150, 34, 56), ellipse(150, -150, 34, 56)])
    solid = [hat, brim, pom, coat, beard, nose, boots, arms]
    holes = [line([(-128, -310), (-60, -318), (0, -320), (60, -318), (128, -310)], 16).intersection(hat.buffer(-14)),
             line([(66 * math.cos(math.radians(a)), -250 + 58 * math.sin(math.radians(a))) for a in range(-40, 221, 6)], 15),  # nose outline, open at the top
             outline_cut(beard, U([coat, arms]).buffer(-16), 15)]
    for o in (-46, 0, 46):
        holes.append(line(catmull([(o * 0.9, -170), (o * 1.1, -136), (o * 0.95, -104)], closed=False, n=6), 15))
    holes.append(line([(0, -96), (0, -46)], 14).intersection(coat.buffer(-30)))
    return [T(g) for g in solid], [T(h) for h in holes]


def d4_gnome_toadstool():
    """A woodland gnome beside a big toadstool on a snowy hill in a round
    frame, with a small toadstool, stars and snowflakes."""
    solid, holes = framed()
    solid.append(snow_ground(500, 850, R, C[1], 12, 2.2))
    add(solid, holes, toadstool(640, 862, 340, 360, 190, 86, tilt=6, spots=8, seed=31))
    add(solid, holes, gnome(300, 872, 0.88, flip=-1))
    solid.append(pine(800, 866, 220, 118, 3))
    top = lambda x: C[1] - math.sqrt((R - 10) ** 2 - (x - 500) ** 2)
    solid.append(hung_star(250, top(250), 300, 46))
    solid.append(hung_star(470, top(470), 200, 40))
    for x in (520, 760):
        holes.append(snowflake(x, 906, 26, 14))
    return compose(solid, holes)


def d5_crescent_moon():
    """Crescent moon with two toadstools growing in its lower curve,
    and stars hanging from the upper horn."""
    solid, holes = [], []
    oc, orr = (450, 540), 400
    ic, irr = (610, 500), 330
    moon = circ(*oc, orr).difference(circ(*ic, irr))
    solid.append(moon)
    h, hh = hanger(430, oc[1] - orr + 2)
    solid.append(h)
    holes.append(hh)
    inner_y = lambda x: ic[1] + math.sqrt(irr ** 2 - (x - ic[0]) ** 2)
    top_y = lambda x: ic[1] - math.sqrt(irr ** 2 - (x - ic[0]) ** 2)
    add(solid, holes, toadstool(500, inner_y(500) + 16, 280, 300, 164, 74, tilt=6, spots=7, seed=12))
    add(solid, holes, toadstool(660, inner_y(660) + 14, 150, 170, 94, 46, tilt=16, spots=4, seed=13))
    for x, y, r in ((462, 300, 46), (548, 250, 34)):
        seg = moon.intersection(LineString([(x, 0), (x, 520)]))
        yt = max(c[1] for g in getattr(seg, "geoms", [seg]) for c in g.coords) - 6   # underside of the upper horn
        solid.append(hung_star(x, yt, y, r))
    return compose(solid, holes)


def d6_snow_globe():
    """Snow globe: toadstools and a pine on a snowy mound inside a glass dome
    with a shine line, on a base with snowflakes cut into it."""
    gx, gyc, Rg = 500, 450, 350
    solid, holes = [ring(gx, gyc, Rg, 30)], []
    h, hh = hanger(gx, gyc - Rg - 14)
    solid.append(h)
    holes.append(hh)
    # base
    base = poly([(250, 760), (750, 760), (800, 930), (200, 930)]).buffer(-14).buffer(14, quad_segs=16)
    rim = rect(230, 740, 770, 790, 12)
    solid += [base, rim]
    for x in (340, 500, 660):
        holes.append(snowflake(x, 865, 40, 15))
    # inside the dome
    inside = circ(gx, gyc, Rg - 6)
    solid.append(inside.intersection(mound(100, 900, 690, 200, 12, 0.4)))
    add(solid, holes, toadstool(540, 700, 270, 290, 160, 74, tilt=5, spots=7, seed=21))
    add(solid, holes, toadstool(350, 706, 150, 170, 94, 46, tilt=-12, spots=4, seed=22))
    solid.append(pine(730, 706, 220, 130, 4))
    # shine: an arc that peels off the glass on the upper left
    arc = [polar(gx, gyc, Rg - 12 - 34 * k / 20, 200 + 46 * k / 20) for k in range(21)]
    solid.append(limb(arc, [24 - 6 * k / 20 for k in range(21)]))
    return compose(solid, holes)


DESIGNS = {
    "01-toadstool-trio-ornament": d1_toadstool_trio,
    "02-toadstool-cottage-ornament": d2_toadstool_cottage,
    "03-mushroom-bauble-ornament": d3_mushroom_bauble,
    "04-gnome-and-toadstool-ornament": d4_gnome_toadstool,
    "05-crescent-moon-mushroom-ornament": d5_crescent_moon,
    "06-mushroom-snow-globe-ornament": d6_snow_globe,
}


README = """WINTER MUSHROOM & TOADSTOOL ORNAMENTS - 6 SVG CUT FILES
by Duskwood Designs Co (etsy.com/shop/DuskwoodDesignsCo)
Thank you for your purchase!

DESIGNS
  01 Toadstool Trio Ornament (three toadstools on a snowy hill, hanging stars)
  02 Toadstool Cottage Ornament (mushroom house with windows and a lantern)
  03 Mushroom Bauble Ornament (classic bauble with toadstools cut out)
  04 Gnome and Toadstool Ornament (woodland gnome beside a big toadstool)
  05 Crescent Moon Mushroom Ornament (toadstools growing on the moon)
  06 Mushroom Snow Globe Ornament (toadstools and a pine in a snow globe)

FILES
  SVG/  Cricut Design Space, Silhouette Designer Edition, Inkscape, Illustrator
  DXF/  Silhouette Studio Basic Edition, laser/CNC software (inches)
  PNG/  transparent background, 1800 px on the longest side (6 in at 300 DPI)

Each design is a single-layer shape with one clean cut path and a hanging
loop built in. Stars, trees and toadstools are attached, so nothing
falls out. Default size is about 6 inches on the longest side; resize
freely, but keep the proportions locked.

SIZING TIPS
  Cardstock, glitter card, felt or vinyl: 4 in or larger.
  Laser-cut wood or acrylic (3 mm or thinner): 4.5 in or larger.
  The thinnest parts (star threads and the narrow cut lines of the gnome's
  beard and the cottage door) are about 0.08 in wide at 6 in, so do not
  go below 4 in, and do a test cut on a new material first.

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
        zipfile.ZipFile(os.path.join(HERE, zp[0])).extractall(os.path.join(HERE, "bundle"))
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
