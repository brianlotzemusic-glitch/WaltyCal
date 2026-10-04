"""Nativity Silhouettes - 6 single-path SVG/DXF cut files.

Six original, reverent nativity silhouettes in the classic public-domain
tradition: the Holy Family in the stable under the star, the manger under
the star, the three magi on camels travelling towards Bethlehem, the good
shepherd with his flock, the Star of Bethlehem, and a herald angel.
Figures are plain silhouettes (no faces). Organic outlines are written as a
few control points and rounded with Chaikin smoothing; everything is
unioned into ONE connected polygon (figures stand on a ground strip, the
star is joined by its long lower ray). compose() closes the solid parts by
8 units so near-touching parts are bridged, then cuts the openings;
finish() closes then opens by 6.5 units, so there is no material and no gap
narrower than ~13 units, and fills any hole under MIN_HOLE.
Coordinates are SVG-style (y grows downward) on a ~1000 unit canvas.
Output: SVG (6 in on the longest side), DXF (inches), stats json.
"""
import math, os, json, sys
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union
from shapely import affinity, make_valid, set_precision
import ezdxf

HERE = os.path.dirname(os.path.abspath(__file__))
SVG_DIR = os.path.join(HERE, "bundle", "SVG")
DXF_DIR = os.path.join(HERE, "bundle", "DXF")
MIN_HOLE = 600.0
SIZE_IN = 6.0
U = unary_union


# ---------------------------------------------------------------- helpers
def poly(pts):
    return make_valid(Polygon(pts)).buffer(0)


def chaikin(pts, n=3, closed=True):
    """Corner-cutting smoothing of a control polygon (or open polyline)."""
    for _ in range(n):
        out = []
        m = len(pts) if closed else len(pts) - 1
        if not closed:
            out.append(pts[0])
        for i in range(m):
            a, b = pts[i], pts[(i + 1) % len(pts)]
            out += [(0.75 * a[0] + 0.25 * b[0], 0.75 * a[1] + 0.25 * b[1]),
                    (0.25 * a[0] + 0.75 * b[0], 0.25 * a[1] + 0.75 * b[1])]
        if not closed:
            out.append(pts[-1])
        pts = out
    return pts


def blob(pts, n=4, flat=None):
    """Smooth closed shape through/near the control points. flat=y keeps
    the raw (unsmoothed) outline below y, so a robe stands on a flat hem."""
    g = poly(chaikin(pts, n))
    if flat is not None:
        x0, _, x1, y1 = poly(pts).bounds
        g = U([g, poly(pts).intersection(box(x0 - 1, flat, x1 + 1, y1 + 1))])
    return g


def T(pts, dx=0, dy=0, s=1.0, flip=False):
    """Transform control points: optional mirror (x -> -x), scale, move."""
    return [((-x if flip else x) * s + dx, y * s + dy) for x, y in pts]


def rect(x0, y0, x1, y1, r=0):
    b = box(x0, y0, x1, y1)
    return b.buffer(-r).buffer(r, 16) if r else b


def line(pts, w):
    return LineString(pts).buffer(w / 2, cap_style=1, join_style=1, quad_segs=12)


def curve(pts, w, n=3):
    return line(chaikin(pts, n, closed=False), w)


def circ(x, y, r):
    return Point(x, y).buffer(r, 48)


def ell(x, y, rx, ry, rot=0):
    return affinity.rotate(affinity.scale(circ(x, y, 1), rx, ry), rot, origin=(x, y))


def taper(p0, p1, w0, w1):
    return U([circ(*p0, w0 / 2), circ(*p1, w1 / 2)]).convex_hull


def polar(x, y, r, deg):
    a = math.radians(deg)
    return x + r * math.cos(a), y + r * math.sin(a)


def star(cx, cy, R, r, n=5, rot=-90):
    pts = []
    for k in range(2 * n):
        rad = R if k % 2 == 0 else r
        pts.append(polar(cx, cy, rad, rot + 180 * k / n))
    return poly(pts)


def sparkle(cx, cy, up, down, side, p=4.6, rot=0, n=240):
    """Four-point star with concave curved sides (|x|^(2/p) + |y|^(2/p) = 1
    per quadrant), with its own length up, down and to each side."""
    pts = []
    for k in range(n):
        t = 2 * math.pi * k / n
        c, s = math.cos(t), math.sin(t)
        x = side * math.copysign(abs(c) ** p, c)
        y = (down if s > 0 else up) * math.copysign(abs(s) ** p, s)
        pts.append((x, y))
    g = poly([(cx + x, cy + y) for x, y in pts])
    return affinity.rotate(g, rot, origin=(cx, cy)) if rot else g


def beth_star(cx, cy, R, tail, side=None, diag=None, inner=False, waist=0.24):
    """Star of Bethlehem: an eight-point star whose four main points are
    long (the lower one stretched into a tail) with four short diagonals.
    inner=True adds a double-star cut-out (inner star held by four bars)."""
    side = side or R
    diag = diag or R * 0.5
    lens = {-90: R, 0: side, 90: tail, 180: side}

    def outline(k_len, k_w):
        pts = []
        for k in range(8):
            a = -90 + 45 * k
            a = a if a <= 180 else a - 360
            pts.append(polar(cx, cy, lens.get(a, diag) * k_len, a))
            pts.append(polar(cx, cy, R * waist * k_w, a + 22.5))
        return poly(pts)

    g = outline(1, 1)
    if tail > R * 1.2:   # a long tail: a slim ray tapering to a point
        tw = max(20, R * 0.17)
        g = U([g, poly([(cx - tw, cy), (cx + tw, cy), (cx, cy + tail)])])
    if inner:            # facet slits down the four main points
        cuts = []
        for a in (-90, 0, 90, 180):
            L = min(lens[a], R)
            cuts.append(taper(polar(cx, cy, R * waist * 0.9 + 14, a), polar(cx, cy, L * 0.62, a), 22, 13))
        g = g.difference(U(cuts))
    return g


def beams(cx, cy, r0, angles, y_end, w0=22, w1=14):
    """Slim beams of light from a star at (cx, cy) down to the line y_end."""
    out = []
    for a in angles:
        L = (y_end - cy) / math.sin(math.radians(a))
        out.append(taper(polar(cx, cy, r0, a), polar(cx, cy, L, a), w0, w1))
    return U(out)


def frond(p0, ang, L, w, droop=30):
    """Palm frond: a curved, tapering leaf from p0."""
    pts = [p0]
    for k in range(1, 7):
        t = k / 6
        a = ang + droop * t * t
        pts.append(polar(*pts[-1], L / 6, a))
    spine = chaikin(pts, 2, closed=False)
    left, right = [], []
    for i, p in enumerate(spine):
        t = i / (len(spine) - 1)
        q = spine[min(i + 1, len(spine) - 1)] if i < len(spine) - 1 else p
        pp = spine[i - 1] if i else p
        dx, dy = q[0] - pp[0], q[1] - pp[1]
        n = math.hypot(dx, dy) or 1
        h = w / 2 * math.sin(math.pi * min(1, t * 1.15)) ** 0.7 + 1
        left.append((p[0] - dy / n * h, p[1] + dx / n * h))
        right.append((p[0] + dy / n * h, p[1] - dx / n * h))
    return poly(left + right[::-1])


def palm(x, gy, h, lean=10, s=1.0):
    """Date palm: a gently leaning trunk with a crown of drooping fronds."""
    top = (x + lean, gy - h)
    trunk = taper((x, gy + 4), top, 24 * s, 16 * s)
    fr = [frond(top, a, L * s, 30 * s, d) for a, L, d in
          ((-160, 120, -40), (-130, 110, -40), (-95, 70, 0), (-50, 110, 40), (-20, 120, 40), (175, 90, -60), (5, 90, 60))]
    return U([trunk, circ(*top, 16 * s)] + fr)


def arch(x0, x1, y_top, y_bot):
    r = (x1 - x0) / 2
    return U([circ((x0 + x1) / 2, y_top + r, r), rect(x0, y_top + r, x1, y_bot)])


def ground(x0, x1, y, h, wob=((0.0, 0.0),), r=12):
    """Ground strip with a gently rolling top edge; flat bottom."""
    top = []
    for x in range(int(x0), int(x1) + 1, 5):
        yy = y
        for amp, f in wob:
            if amp:
                yy -= amp * math.sin(x / f)
        top.append((x, yy))
    return poly(top + [(x1, y + h), (x0, y + h)]).buffer(-r).buffer(r, 16)


def tuft(x, y, s=1.0):
    """Grass tuft of three blades rising from (x, y)."""
    return U([taper((x, y + 4), (x - 16 * s, y - 34 * s), 15, 8),
              taper((x, y + 4), (x + 2 * s, y - 46 * s), 15, 8),
              taper((x, y + 4), (x + 18 * s, y - 30 * s), 15, 8)])


def sheep(x, gy, s=1.0, flip=False, grazing=False, lying=False):
    """Woolly sheep on ground line gy, facing right (or left): a scalloped
    fleece, a long head with a drooping ear, and slim legs."""
    f = -1 if flip else 1
    X = lambda dx: x + f * dx * s
    Y = lambda dy: gy - dy * s
    lift = 0 if lying else 50
    core = ell(X(0), Y(40 + lift), 66 * s, 38 * s)
    curls = [circ(X(66 * math.cos(math.radians(a))), Y(40 + lift + 38 * math.sin(math.radians(a))), 20 * s)
             for a in range(0, 360, 36) if not (lying and 200 < a < 340)]
    parts = [core] + curls
    if not lying:
        parts += [taper((X(dx), Y(54)), (X(dx + 2), Y(0)), 18 * s, 15 * s) for dx in (-44, -24, 26, 46)]
    if grazing:
        parts += [taper((X(56), Y(56 + lift)), (X(92), Y(22 + lift * 0.5)), 38 * s, 28 * s),
                  ell(X(104), Y(4 + lift * 0.5), 32 * s, 17 * s, f * 70),
                  ell(X(76), Y(52 + lift * 0.5), 21 * s, 8 * s, -f * 30)]
    else:
        hy = 134 if not lying else 92
        parts += [taper((X(46), Y(hy - 36)), (X(84), Y(hy + 4)), 42 * s, 30 * s),
                  ell(X(106), Y(hy), 34 * s, 17 * s, f * 55),
                  ell(X(74), Y(hy + 20), 24 * s, 8 * s, -f * 34)]
    parts.append(circ(X(-82), Y(52 + lift), 14 * s))
    return U(parts)


def areal(g):
    if g.geom_type in ("Polygon", "MultiPolygon"):
        return g
    return U([p for p in getattr(g, "geoms", []) if p.geom_type in ("Polygon", "MultiPolygon")])


def compose(solid, holes=(), bridge=8):
    S = U(solid).buffer(bridge, quad_segs=16).buffer(-bridge, quad_segs=16)
    return S.difference(U(list(holes))) if holes else S


def finish(g, r=6.5, simplify=0.12):
    """Close then open by r (no gaps or material under ~2r), drop small holes."""
    g = areal(make_valid(g))
    g = g.buffer(r, quad_segs=16).buffer(-r, quad_segs=16)
    g = g.buffer(-r, quad_segs=16).buffer(r, quad_segs=16)
    g = areal(set_precision(areal(make_valid(g.simplify(simplify))), 0.05))
    polys = list(g.geoms) if g.geom_type == "MultiPolygon" else [g]
    polys = [p for p in polys if p.area > 50]
    polys = [Polygon(p.exterior, [i for i in p.interiors if Polygon(i).area >= MIN_HOLE + 30]) for p in polys]
    return U(polys)


# ---------------------------------------------------------------- figures
# Control points are in a local frame: feet on y = 0, figure facing right,
# about 1 unit = 1 canvas unit at s = 1.
MARY_KNEEL = [  # veiled, kneeling, head bowed, hands folded in prayer
    (-24, -286), (0, -302), (28, -302), (46, -288),                  # veil over the head
    (52, -274), (60, -258), (54, -252), (56, -244), (48, -234),      # brow, nose, chin (bowed)
    (36, -232), (40, -216),                                          # under the chin, veil edge
    (54, -206), (74, -208), (98, -228), (108, -224), (100, -202),    # forearms up to folded hands
    (76, -180), (58, -166), (54, -150),                              # elbow back to the waist
    (70, -100), (96, -24), (104, 0),                                 # lap and knee
    (-108, 0), (-112, -12), (-84, -40), (-76, -70),                  # robe pooled behind
    (-62, -130), (-62, -196), (-56, -230), (-40, -262)]              # veil falling down the back
JOSEPH = [  # standing, hooded, bearded, one hand on his staff
    (-30, -462), (-8, -480), (20, -482), (40, -468), (48, -450),     # hood
    (52, -440), (62, -426), (54, -420), (58, -406), (52, -392),      # brow, nose, beard
    (40, -386), (44, -372),                                          # hood edge at the throat
    (60, -360), (78, -340), (100, -326), (110, -326), (112, -306),   # arm forward to the staff
    (96, -300), (88, -270), (72, -262),                              # hanging sleeve
    (66, -240), (74, -130), (94, 0),                                 # robe front
    (-88, 0), (-76, -120), (-68, -250), (-66, -350),                 # robe back
    (-50, -392), (-36, -420), (-32, -444)]                           # shoulder, back of the hood
SHEPHERD = [  # standing, head cloth, looking up towards the star
    (-34, -540), (-12, -562), (14, -566), (36, -556), (48, -540),    # head cloth
    (56, -534), (66, -522), (60, -514), (62, -502), (52, -492),      # face tilted up
    (40, -488), (44, -472),
    (60, -458), (82, -424), (102, -396), (118, -380), (118, -362), (100, -360),  # arm to the crook
    (90, -340), (74, -330),                                          # sleeve
    (68, -300), (76, -150), (98, 0),
    (-92, 0), (-80, -140), (-72, -300), (-70, -420), (-52, -462), (-38, -490), (-36, -516)]
ANGEL_ROBE = [  # herald angel in a long flowing robe, facing right
    (488, 340), (512, 346), (540, 390), (546, 470), (552, 520), (580, 620),
    (600, 740), (636, 840), (662, 900), (640, 912), (430, 912),
    (330, 902), (272, 886), (330, 856), (386, 760), (406, 620),
    (424, 520), (428, 470), (432, 400), (456, 360)]


def mary(x, gy, s=1.0, flip=False):
    return blob(T(MARY_KNEEL, x, gy, s, flip), 3, gy - 40 * s)


def joseph(x, gy, s=1.0, flip=True):
    return blob(T(JOSEPH, x, gy, s, flip), 3, gy - 40 * s)


def manger(cx, gy, w=170, h=120, baby=True):
    """X-legged wooden manger with straw and the swaddled infant."""
    top = gy - h
    hw = w / 2
    parts = [poly([(cx - hw, top), (cx + hw, top), (cx + hw * 0.8, top + h * 0.42), (cx - hw * 0.8, top + h * 0.42)])]
    parts.append(line([(cx - hw * 0.72, top + 20), (cx + hw * 0.92, gy)], 18))
    parts.append(line([(cx + hw * 0.72, top + 20), (cx - hw * 0.92, gy)], 18))
    # straw spilling over the rim
    for k in range(7):
        t = (k + 0.5) / 7
        x = cx - hw * 1.02 + 2.04 * hw * t
        a = -90 + (t - 0.5) * 110
        parts.append(taper((x, top + 8), polar(x, top + 8, 34 + 8 * math.sin(k * 2.1), a), 16, 9))
    holes = []
    if w > 220:   # big manger: plank slots in the box
        holes.append(rect(cx - hw * 0.62, top + h * 0.12, cx + hw * 0.62, top + h * 0.12 + 16, 6))
    if baby:
        parts.append(ell(cx - w * 0.04, top - h * 0.1 - 6, w * 0.27, max(24, h * 0.13)))
        parts.append(circ(cx + w * 0.27, top - h * 0.1 - 14, max(20, w * 0.075)))
    return U(parts), holes


def camel(x, gy, s=1.0, stride=0):
    """Dromedary walking right; returns the camel with a saddle cloth."""
    body = [(-118, -232), (-86, -270), (-40, -302), (6, -312), (46, -294), (82, -262),
            (116, -250), (142, -268), (160, -312), (178, -346), (212, -350),
            (244, -330), (246, -312), (212, -304), (188, -298), (170, -262),
            (150, -222), (120, -194), (70, -180), (-40, -182), (-96, -188), (-124, -210)]
    g = [blob(T(body, x, gy, s), 3)]
    # legs (knees, slim lower legs, padded feet); stride swings a pair
    for hip, knee_dx, foot_dx in ((98, 6 + stride, 16 + 2 * stride), (44, -6 - stride, -14 - 2 * stride),
                                  (-46, -6 - stride, -14 - 2 * stride), (-100, 6 + stride, 16 + 2 * stride)):
        hp = (x + hip * s, gy - 196 * s)
        kn = (x + (hip + knee_dx) * s, gy - 104 * s)
        ft = (x + (hip + foot_dx) * s, gy - 8 * s)
        g += [taper(hp, kn, 34 * s, max(18, 24 * s)), taper(kn, ft, max(18, 24 * s), max(16, 18 * s)),
              ell(ft[0] + 6 * s, ft[1] + 2 * s, max(17, 20 * s), max(10, 10 * s))]
    g.append(curve(T([(-120, -228), (-136, -200), (-134, -160)], x, gy, s), 13 * s))  # tail
    return U(g)


def magus(x, gy, s=1.0, hat="crown", gift="box"):
    """Robed king seated on the camel's hump, holding a gift forward."""
    P = lambda pts: T(pts, x, gy, s)
    cloak = [(-46, -296), (-22, -380), (-6, -412), (24, -414), (40, -390), (52, -340),
             (60, -300), (44, -262), (20, -228), (-40, -224), (-74, -246)]
    g = [blob(P(cloak), 3)]
    g.append(circ(x + 10 * s, gy - 438 * s, 24 * s))          # head
    g.append(curve(P([(30, -392), (64, -374), (88, -380)]), 22 * s))   # arm
    if hat == "crown":
        g.append(poly(P([(-14, -452), (-18, -490), (-4, -472), (10, -498), (24, -472), (38, -490), (34, -452)])))
    elif hat == "turban":
        g.append(ell(x + 10 * s, gy - 462 * s, 30 * s, 20 * s))
        g.append(circ(x + 10 * s, gy - 486 * s, 10 * s))
    else:
        g.append(poly(P([(-14, -450), (2, -508), (18, -508), (34, -450)])))
    if gift == "box":
        g.append(rect(x + 80 * s, gy - 410 * s, x + 114 * s, gy - 376 * s, 3 * s))
        g.append(ell(x + 97 * s, gy - 414 * s, 12 * s, 7 * s))
    elif gift == "jar":
        g.append(ell(x + 98 * s, gy - 390 * s, 17 * s, 20 * s))
        g.append(rect(x + 88 * s, gy - 422 * s, x + 108 * s, gy - 404 * s, 2 * s))
    else:
        g.append(poly(P([(80, -372), (116, -372), (110, -400), (86, -400)])))
        g.append(ell(x + 98 * s, gy - 404 * s, 18 * s, 8 * s))
    return U(g)


def town(x0, gy, s=1.0):
    """Little Bethlehem: flat-roofed houses and a dome."""
    P = lambda a, b, c, d: rect(x0 + a * s, gy - b * s, x0 + c * s, gy + 4, 2)
    g = [P(0, 90, 70, 0), P(60, 150, 140, 0), P(130, 110, 220, 0), P(210, 70, 270, 0)]
    g.append(circ(x0 + 100 * s, gy - 150 * s, 40 * s).intersection(rect(x0, gy - 200 * s, x0 + 300 * s, gy - 150 * s)))
    holes = [arch(x0 + 22 * s, x0 + 46 * s, gy - 66 * s, gy - 28 * s),
             arch(x0 + 88 * s, x0 + 112 * s, gy - 120 * s, gy - 80 * s),
             arch(x0 + 160 * s, x0 + 186 * s, gy - 84 * s, gy - 44 * s),
             arch(x0 + 226 * s, x0 + 250 * s, gy - 50 * s, gy - 18 * s)]
    return U(g), U(holes)


# ---------------------------------------------------------------- designs
def d1_holy_family():
    """Holy Family in a stable under the star."""
    BY = 870
    solid, holes = [], []
    solid.append(ground(110, 890, BY, 48, ((5, 60),)))
    # stable: rough posts, cross beam with braces and a gable roof
    for x in (184, 816):
        solid.append(rect(x - 17, 430, x + 17, BY + 6, 3))
    solid.append(rect(150, 420, 850, 448, 4))
    for x, sg in ((184, 1), (816, -1)):
        solid.append(line([(x, 520), (x + sg * 86, 436)], 18))
    roof = [(118, 452), (500, 252), (882, 452)]
    solid.append(line(roof, 36))
    solid.append(line([(500, 252), (500, 424)], 18))       # king post
    # the star rests on the ridge
    solid.append(beth_star(500, 168, 104, 104, 92, 52, waist=0.3))
    # figures
    solid.append(mary(332, BY + 4, 1.0))
    solid.append(joseph(690, BY + 4, 0.86))
    sx = 690 - 111 * 0.86
    solid.append(line([(sx, 470), (sx, BY + 2)], 18))       # Joseph's staff
    mg, mh = manger(512, BY + 4, 150, 104)
    solid.append(mg); holes.append(mh)
    return compose(solid, holes)


def arch_frame(x0, x1, y_top, y_bot, t=26):
    """Round-arched window frame, t wide; returns (frame, opening)."""
    outer = arch(x0, x1, y_top, y_bot)
    inner = arch(x0 + t, x1 - t, y_top + t, y_bot - t)
    return outer.difference(inner), inner


def d2_manger_star():
    """Manger with the infant, the star shining just above."""
    solid, holes = [], []
    BY = 880
    solid.append(ground(110, 890, BY, 46, ((4, 50),)))
    mg, mh = manger(500, BY + 4, 330, 200)
    solid.append(mg); holes.append(mh)
    # a glowing arc over the child, joined to the manger rim, with rays;
    # the star's lower point rests on the top of the arc
    cx, cy, R = 500, BY + 4 - 200 + 4, 150
    arc = circ(cx, cy, R + 9).difference(circ(cx, cy, R - 9)).intersection(box(0, 0, 1000, cy))
    solid.append(arc)
    for a in (-162, -142, -122, -58, -38, -18):
        solid.append(taper(polar(cx, cy, R, a), polar(cx, cy, R + (66 if a in (-122, -58) else 52), a), 18, 13))
    solid.append(beth_star(500, 452, 116, 140, 116, 62, waist=0.3))
    solid.append(sheep(214, BY + 2, 0.9))
    solid.append(sheep(790, BY + 2, 0.86, flip=True, grazing=True))
    solid += [tuft(340, BY + 2, 0.9), tuft(668, BY + 2, 0.8)]
    return compose(solid, holes)


def d3_magi_procession():
    """Three magi on camels following the star to Bethlehem (framed panel)."""
    W, H, F = 1000, 600, 24
    solid, holes = [], []
    solid.append(rect(0, 0, W, H, 40).difference(rect(F, F, W - F, H - F, 18)))
    BY = 500
    solid.append(ground(F - 4, W - F + 4, BY, 80, ((7, 80), (3, 23)), r=2))
    for x, s, stride, hat, gift in ((136, 0.6, 6, "turban", "jar"), (384, 0.6, 2, "crown", "box"),
                                    (632, 0.6, 4, "tall", "bowl")):
        solid.append(camel(x, BY + 4, s, stride))
        solid.append(magus(x, BY + 4, s, hat, gift))
    t, th = town(800, BY + 4, 0.66)
    solid.append(t); holes.append(th)
    solid.append(beth_star(866, 76, 96, 110, 84, 48, waist=0.32))
    return compose(solid, holes)


def d4_good_shepherd():
    """Shepherd with his crook looking up, with his flock."""
    BY = 880
    solid, holes = [], []
    solid.append(ground(110, 890, BY, 46, ((8, 70),)))
    x0, s = 420, 1.0
    solid.append(blob(T(SHEPHERD, x0, BY + 4, s), 3, BY - 36))
    cx = x0 + 116 * s
    solid.append(line([(cx, 330), (cx, BY + 2)], 20))
    solid.append(curve([(cx, 336), (cx, 292), (cx + 18, 262), (cx + 54, 258), (cx + 76, 282), (cx + 72, 312), (cx + 56, 324)], 20))
    solid.append(sheep(230, BY + 2, 0.9, flip=True))
    solid.append(sheep(700, BY + 2, 0.96))
    solid.append(sheep(842, BY + 2, 0.62, grazing=True))
    solid += [tuft(140, BY + 2, 0.8), tuft(330, BY + 2, 0.9), tuft(600, BY + 2, 0.8)]
    return compose(solid, holes)


def d5_bethlehem_star():
    """The Star of Bethlehem: eight points, a long lower ray and a burst of
    slender rays between the points."""
    solid, holes = [], []
    cx, cy = 500, 380
    solid.append(beth_star(cx, cy, 330, 540, 300, 170, inner=True, waist=0.3))
    for k in range(8):
        a = -90 + 22.5 + 45 * k
        solid.append(taper(polar(cx, cy, 60, a), polar(cx, cy, 250 if k in (3, 4) else 220, a), 22, 13))
    holes.append(circ(cx, cy, 30))
    return compose(solid, holes)


def wing(S, bone, d0, d1, L0, L1, w=60, n=10, solid_to=0.62):
    """Wing: a bone line from the shoulder S through `bone` points, with n
    long rounded feathers along it whose direction turns from d0 to d1
    degrees and whose length grows from L0 to L1. The inner part of the
    wing is solid; only the feather tips separate into a scalloped edge."""
    ls = LineString(chaikin([S] + bone, 3, closed=False))
    parts = [ls.buffer(30, quad_segs=12)]
    inner = []
    for k in range(n):
        t = 0.06 + 0.94 * k / (n - 1)
        q = ls.interpolate(ls.length * t)
        a = d0 + (d1 - d0) * t
        L = L0 + (L1 - L0) * t ** 1.2
        base = (q.x, q.y)
        tip = polar(*base, L, a)
        mid = polar(*base, L * 0.55, a)
        parts.append(blob([polar(*base, w * 0.4, a - 90), polar(*mid, w / 2, a - 90), polar(*tip, w * 0.3, a - 90),
                           polar(*tip, 6, a), polar(*tip, w * 0.3, a + 90), polar(*mid, w / 2, a + 90),
                           polar(*base, w * 0.4, a + 90)], 3))
        inner.append(polar(*base, L * solid_to, a))
    bases = [(p.x, p.y) for p in (ls.interpolate(ls.length * (0.06 + 0.94 * k / (n - 1))) for k in range(n))]
    parts.append(poly(bases + inner[::-1]))
    return U(parts)


def d6_herald_angel():
    """Herald angel in a flowing robe, wing raised, sounding a trumpet."""
    solid, holes = [], []
    solid.append(blob(ANGEL_ROBE, 3, 880))
    solid.append(ell(498, 294, 30, 35, 12))                               # head
    solid.append(blob([(466, 264), (496, 254), (480, 292), (468, 340), (446, 396), (428, 372), (446, 300)], 3))  # hair
    # wing raised behind the shoulders, feathers sweeping back
    solid.append(wing((446, 392), [(410, 300), (360, 200), (300, 112), (236, 64)],
                      108, 192, 160, 250, 62, 9))
    # arm raised to the trumpet with a wide hanging sleeve
    solid.append(taper((506, 404), (640, 268), 44, 26))
    solid.append(poly([(492, 396), (634, 262), (646, 290), (586, 380), (552, 470), (508, 472)]))
    # trumpet: mouthpiece at the lips, long tube, flared bell
    solid.append(taper((530, 300), (790, 200), 14, 22))
    solid.append(poly([(776, 196), (784, 220), (868, 222), (842, 146)]))
    # halo ring
    solid.append(circ(484, 282, 80).difference(circ(484, 282, 64)))
    # robe folds: slim cut-outs that follow the flare of the skirt
    for p0, p1 in (((468, 610), (420, 850)), ((508, 640), (528, 860)), ((536, 612), (572, 822))):
        holes.append(taper(p0, p1, 14, 24))
    return compose(solid, holes)


DESIGNS = {
    "01-holy-family-stable": d1_holy_family,
    "02-manger-under-the-star": d2_manger_star,
    "03-three-magi-on-camels": d3_magi_procession,
    "04-good-shepherd": d4_good_shepherd,
    "05-star-of-bethlehem": d5_bethlehem_star,
    "06-herald-angel": d6_herald_angel,
}
SQUARE = ("01", "02", "04", "05", "06")  # 03 keeps its wide frame


README = """NATIVITY SILHOUETTES - 6 SVG CUT FILES
by Duskwood Designs Co (etsy.com/shop/DuskwoodDesignsCo)
Thank you for your purchase!

DESIGNS
  01 Holy Family in the Stable
  02 Manger Under the Star
  03 Three Magi on Camels (wide panel)
  04 The Good Shepherd
  05 Star of Bethlehem
  06 Herald Angel

FILES
  SVG/  Cricut Design Space, Silhouette Designer Edition, Inkscape, Illustrator
  DXF/  Silhouette Studio Basic Edition, laser/CNC software (inches)
  PNG/  transparent background, 1800 px on the longest side (6 in at 300 DPI)

Each design is a single-layer shape with one clean cut path, so no slicing,
welding or cleanup is needed. Stars, figures and animals are all attached,
so nothing falls out. Default size is 6 in on the longest side; resize
freely, but keep the proportions locked.

SIZING TIPS
  Vinyl (windows, glass blocks, mugs, signs): 4 in or larger.
  Cardstock (cards, ornaments, mantel scenes): 5 in or larger.
  Laser-cut wood or acrylic: 5 in or larger in 3 mm material. The scenes
  with a flat ground strip (01, 02, 04, 05, 06) stand up on their own when
  set in a slotted base.
  Heat-transfer vinyl (shirts, totes, pillows): 5 in or larger.
  The wide Three Magi panel (03) works best at 8 in wide or larger.
  The narrowest material and the narrowest gap are both about 0.08 in at
  6 in. Do a test cut first on a new material.

LICENSE
  Personal use: unlimited.
  Small-business commercial use: you may sell finished physical products
  (ornaments, cards, decals, signs, shirts, etc.) made with these designs,
  up to 500 units per design.
  You may NOT resell, share or redistribute the digital files themselves,
  in original or modified form, or include them in other digital products.
"""


# ---------------------------------------------------------------- export
def to_path(geom):
    polys = geom.geoms if geom.geom_type == "MultiPolygon" else [geom]
    d = []
    for p in polys:
        for r in [p.exterior, *p.interiors]:
            pts = list(r.coords)
            d.append("M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts[:-1]) + " Z")
    return " ".join(d)


def view_box(geom, square, pad=12):
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


def build(name):
    return finish(DESIGNS[name]())


if __name__ == "__main__":
    for _d in (SVG_DIR, DXF_DIR):
        os.makedirs(_d, exist_ok=True)
    only = sys.argv[1:]
    meta = {}
    for name in DESIGNS:
        if only and not any(o in name for o in only):
            continue
        g = build(name)
        vb = view_box(g, name[:2] in SQUARE)
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
