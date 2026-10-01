"""Filigree Christmas Ornaments - 6 single-path SVG/DXF cut files.

Light, lacy openwork: most designs are a thin outline frame filled with
botanical filigree strokes (snowflake lace, holly, fern, pine sprigs,
scrollwork); the tree is built from needled fir boughs. The strokes are the
material; the gaps between them are the cut-outs. Everything is unioned into ONE connected polygon with a hanging
loop at the top. Strokes are 13-20 units wide, and smooth() ends with an
opening pass so no material anywhere is narrower than 10 units (0.06 in at
6 in); cut-out corners are rounded and holes under MIN_HOLE are filled.
Coordinates are SVG-style (y grows downward) on a ~1000 unit canvas.
Output: SVG (6 in), DXF (inches), stats json.
"""
import math, os, json, sys
from shapely.geometry import LineString, Point, Polygon
from shapely.ops import unary_union
from shapely import affinity, make_valid, set_precision
import ezdxf
import shapely

HERE = os.path.dirname(os.path.abspath(__file__))
SVG_DIR = os.path.join(HERE, "bundle", "SVG")
DXF_DIR = os.path.join(HERE, "bundle", "DXF")
for _d in (SVG_DIR, DXF_DIR):
    os.makedirs(_d, exist_ok=True)
MIN_HOLE = 600.0
SIZE_IN = 6.0
W = 16      # standard filigree stroke
WF = 20     # frame stroke


# ---------------------------------------------------------------- helpers
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


def bez(p0, p1, p2, n=30):
    return [((1-t)**2*p0[0] + 2*(1-t)*t*p1[0] + t*t*p2[0],
             (1-t)**2*p0[1] + 2*(1-t)*t*p1[1] + t*t*p2[1]) for t in (i/n for i in range(n+1))]


def line(pts, w=W):
    return LineString(pts).buffer(w / 2, cap_style=1, join_style=1, quad_segs=12)


def ring(x, y, r, w=W):
    return Point(x, y).buffer(r + w / 2, 128).difference(Point(x, y).buffer(r - w / 2, 128))


def outline(poly, w=WF):
    return poly.difference(poly.buffer(-w, join_style=1))


def polar(x, y, r, deg):
    a = math.radians(deg)
    return x + r * math.cos(a), y + r * math.sin(a)


def leaf(x0, y0, ang, L, Wd, power=0.9):
    """Solid almond leaf from base (x0,y0) pointing at ang degrees."""
    n = 24
    top = [(L * t, Wd / 2 * math.sin(math.pi * t) ** power) for t in (i / n for i in range(n + 1))]
    pts = top + [(x, -y) for x, y in top[::-1][1:-1]]
    g = Polygon(pts).buffer(0)
    g = affinity.rotate(g, ang, origin=(0, 0))
    return affinity.translate(g, x0, y0)


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


def spiral(cx, cy, r0, r1, a0, turns, sgn=1, n=120):
    """Points of a spiral starting at radius r0 (outer) shrinking to r1."""
    return [(cx + (r0 + (r1 - r0) * t) * math.cos(math.radians(a0 + sgn * 360 * turns * t)),
             cy + (r0 + (r1 - r0) * t) * math.sin(math.radians(a0 + sgn * 360 * turns * t)))
            for t in (i / n for i in range(n + 1))]


def scroll(cx, cy, r0, r1, a0, turns, sgn=1, w=W, dot=None):
    pts = spiral(cx, cy, r0, r1, a0, turns, sgn)
    g = line(pts, w)
    if dot:
        g = g.union(Point(pts[-1]).buffer(dot, 48))
    return g


def snow_arm(cx, cy, ang, L, w=W, br=((0.38, 0.30), (0.66, 0.22)), bw=14, spread=50):
    parts = [line([(cx, cy), polar(cx, cy, L, ang)], w)]
    for t, bl in br:
        bx, by = polar(cx, cy, L * t, ang)
        for s in (-1, 1):
            parts.append(line([(bx, by), polar(bx, by, L * bl, ang + s * spread)], bw))
    return unary_union(parts)


def hanger(cx, ytop, neck=34):
    """Hanging loop (ring, 0.25 in hole at 6 in) + bead, sitting on the body top at ytop."""
    ry = ytop - neck - 40
    loop = ring(cx, ry, 31, 20)
    stem = line([(cx, ry + 38), (cx, ytop + 8)], 20)
    bead = Point(cx, ytop - neck * 0.45).buffer(19, 48)
    return unary_union([loop, stem, bead])


def finish(g, simplify=0.15):
    ref = g
    g = g.buffer(0.01).buffer(-0.01).simplify(simplify)
    no_big_fill(ref, g)
    polys = list(g.geoms) if g.geom_type == "MultiPolygon" else [g]
    polys = [p for p in polys if p.area > 50]
    return unary_union([Polygon(p.exterior, [i for i in p.interiors if Polygon(i).area >= MIN_HOLE + 20])
                        for p in polys])


def areal(g):
    """Only the polygon parts of a geometry (make_valid can return stray lines)."""
    if g.geom_type in ("Polygon", "MultiPolygon"):
        return g
    return unary_union([p for p in getattr(g, "geoms", []) if p.geom_type in ("Polygon", "MultiPolygon")])


def smooth(g, r=4):
    """Round off acute inside corners of cut-outs (opening each hole by r),
    then remove any hairline point of material thinner than 10 units.
    Done hole-by-hole because a whole-shape closing can misfire in GEOS."""
    g = areal(set_precision(areal(make_valid(g)), 0.05))
    ref = g
    out = []
    for p in (g.geoms if g.geom_type == "MultiPolygon" else [g]):
        holes = [Polygon(i).buffer(-r, join_style=1).buffer(r, join_style=1) for i in p.interiors]
        out.append(Polygon(p.exterior).difference(unary_union(holes)))
    g = unary_union(out)
    g2 = g.buffer(-5, join_style=1).buffer(5, join_style=1)
    assert abs(g2.area - g.area) < 0.03 * g.area, "smoothing changed the shape too much"
    no_big_fill(ref, g2)
    return g2


def no_big_fill(ref, new, limit=400):
    """Guard against GEOS buffer glitches that fill a whole cut-out."""
    extra = shapely.difference(areal(make_valid(new)), areal(make_valid(ref.buffer(0.5, join_style=1))),
                               grid_size=0.05)
    for p in (extra.geoms if hasattr(extra, "geoms") else [extra]):
        assert p.area < limit, f"cut-out filled by mistake near {p.centroid}"


# ---------------------------------------------------------------- designs
def d1_snowflake_bauble():
    cx, cy, R = 500, 560, 340
    parts = [ring(cx, cy, R, WF)]
    # scalloped lace edge with eyelets
    n = 40
    for k in range(n):
        a = -90 + 360 * (k + 0.5) / n
        if abs(((a + 90 + 180) % 360) - 180) < 20:
            continue
        x, y = polar(cx, cy, R + 24, a)
        parts.append(Point(x, y).buffer(30, 48).difference(Point(x, y).buffer(14.5, 48)))
    # big snowflake
    for k in range(6):
        ang = -90 + 60 * k
        parts.append(snow_arm(cx, cy, ang, R, W + 2, br=((0.42, 0.34), (0.70, 0.22)), bw=14, spread=48))
    parts.append(ring(cx, cy, 52, W))
    hexa = Polygon([polar(cx, cy, 52, -90 + 60 * k) for k in range(6)])
    g = unary_union(parts)
    g = g.union(hanger(cx, cy - R - 8))
    return smooth(g)


def bell_shape(cx=500):
    right = [(0, 200), (70, 205), (140, 250), (172, 340), (186, 450), (206, 560), (240, 640), (290, 690),
             (300, 720)]
    side = catmull([(cx + x, y) for x, y in right], closed=False, n=10)
    body = make_valid(Polygon(side + [(2 * cx - x, y) for x, y in side[::-1]]))
    rim = Polygon([(cx - 330, 690), (cx + 330, 690), (cx + 330, 770), (cx - 330, 770)]).buffer(-24).buffer(24)
    return unary_union([body, rim]).buffer(10, join_style=1).buffer(-10, join_style=1)


def lace_holly(x0, y0, ang, L, Wd, spikes=4):
    """Holly leaf with an almond cut-out split by a solid midrib."""
    hl = holly_leaf(x0, y0, ang, L, Wd, spikes)
    a = math.radians(ang)
    bx, by = x0 + 0.17 * L * math.cos(a), y0 + 0.17 * L * math.sin(a)
    cut = leaf(bx, by, ang, 0.72 * L, 0.40 * Wd)
    rib = line([(x0, y0), (x0 + 0.95 * L * math.cos(a), y0 + 0.95 * L * math.sin(a))], 14)
    return hl.difference(cut).union(rib)


def d2_holly_bell():
    cx = 500
    bell = bell_shape(cx)
    parts = [outline(bell, WF)]
    # solid rim band with a row of eyelets (lace edge)
    rim = bell.intersection(Polygon([(0, 700), (1000, 700), (1000, 800), (0, 800)]))
    parts.append(rim.difference(unary_union([Point(x, 734).buffer(15, 48) for x in range(cx - 270, cx + 271, 45)])))
    parts.append(Point(cx, 788).buffer(38, 64))          # clapper
    by = 340
    parts.append(line([(cx, 205), (cx, 705)], 15))
    for s in (-1, 1):
        ang = 90 - s * 52
        parts.append(lace_holly(cx, by, ang, 215, 110, 4).intersection(bell.buffer(-4)))
        tip = polar(cx, by, 215, ang)
        parts.append(line([tip, (cx + s * 200, tip[1] + 10)], 14).intersection(bell.buffer(-4)))
        # lower C-scrolls rising from the rim centre
        C = (cx + s * 125, 612)
        st = polar(*C, 55, 180 if s > 0 else 0)
        parts.append(line(bez((cx, 700), (cx + s * 20, 650), st, 20), 15))
        parts.append(scroll(*C, 55, 14, 180 if s > 0 else 0, 1.05, sgn=s, w=15, dot=12))
    berries = [(cx - 32, by - 6), (cx + 32, by - 6), (cx, by - 58)]
    parts += [Point(p).buffer(30, 64) for p in berries]
    g = unary_union(parts)
    g = g.difference(unary_union([Point(p).buffer(15, 48) for p in berries]))   # berry eyelets
    g = g.union(hanger(cx, 205))
    return smooth(g)


def star_poly(cx, cy, R, r, n=5, rot=-90):
    return Polygon([polar(cx, cy, R if k % 2 == 0 else r, rot + 180 * k / n) for k in range(2 * n)])


def fern(x0, y0, ang, L, w=13, n=7, lf0=62, lf1=20):
    """Fern frond: stem with alternating solid leaflets shrinking to the tip."""
    parts = [line([(x0, y0), polar(x0, y0, L, ang)], w)]
    for i in range(n):
        t = 0.14 + 0.78 * i / (n - 1)
        bx, by = polar(x0, y0, L * t, ang)
        ll = lf0 + (lf1 - lf0) * i / (n - 1)
        for s in (-1, 1):
            parts.append(leaf(bx, by, ang + s * 52, ll, ll * 0.42))
    parts.append(leaf(*polar(x0, y0, L * 0.95, ang), ang, 28, 14))
    return unary_union(parts)


def d3_fern_star():
    cx, cy = 500, 540
    st = star_poly(cx, cy, 440, 205).buffer(18, join_style=1).buffer(-18, join_style=1)
    parts = [outline(st, WF), Point(cx, cy).buffer(62, 96).difference(Point(cx, cy).buffer(24, 64))]
    for k in range(5):
        ang = -90 + 72 * k
        parts.append(fern(*polar(cx, cy, 64, ang), ang, 340, 14, n=6, lf0=70, lf1=26))
        # inner valley: small lace drop joined to the frame
        va = ang + 36
        x, y = polar(cx, cy, 150, va)
        parts.append(Point(x, y).buffer(19, 48))
        parts.append(line([polar(cx, cy, 64, va), (x, y)], 13))
        parts.append(line([polar(x, y, 22, va), polar(cx, cy, 225, va)], 13).intersection(st.buffer(-4)))
    g = unary_union(parts)
    g = g.union(hanger(cx, cy - 440 + 6, neck=30))
    return smooth(g)


def fir_branch(pts, w=14, nw=13, every=36, needle=40, spread=48, taper=0.45):
    """Fir branch along a polyline: stem plus paired needles angled to the tip."""
    ls = LineString(pts)
    parts = [line(pts, w)]
    n = int(ls.length // every)
    for i in range(1, n):
        d = i * every
        p, q = ls.interpolate(d), ls.interpolate(min(d + 2, ls.length))
        a = math.degrees(math.atan2(q.y - p.y, q.x - p.x))
        nl = needle * (1 - taper * d / ls.length)
        for s in (-1, 1):
            parts.append(line([(p.x, p.y), polar(p.x, p.y, nl, a + s * spread)], nw))
    tip = ls.interpolate(ls.length)
    return unary_union(parts + [Point(tip.x, tip.y).buffer(w * 0.6)])


def needled_branch(pts, keep_clear, room, w=15, nw=13, every=34, needle=40, spread=45, taper=0.35, start=30):
    """Fir bough along pts: a stem plus needle ticks on both sides, angled to the tip.
    A needle is kept only if it stays at least 11 units clear of keep_clear (other
    boughs and their needles, trunk, frame) and of the previous needle on its own
    side, and its tip lies inside room, so every gap stays cuttable."""
    ls = LineString(pts)
    stem = line(pts, w)
    needles, last = [], {-1: None, 1: None}
    d = start
    while d < ls.length - 10:
        p, q = ls.interpolate(d), ls.interpolate(min(d + 2, ls.length))
        a = math.degrees(math.atan2(q.y - p.y, q.x - p.x))
        nl = needle * (1 - taper * d / ls.length)
        for sgn in (-1, 1):
            tip = polar(p.x, p.y, nl, a + sgn * spread)
            probe = line([polar(p.x, p.y, 10, a + sgn * spread), tip], nw).buffer(11)
            if room.contains(Point(tip)) and not probe.intersects(keep_clear) \
                    and (last[sgn] is None or not probe.intersects(last[sgn])):
                last[sgn] = line([(p.x, p.y), tip], nw)
                needles.append(last[sgn])
        d += every
    return stem, needles


def d4_fir_tree():
    """A tree built from drooping fir boughs: trunk, six pairs of needled branches
    getting longer toward the base, star topper and a little pot."""
    cx = 500
    trunk_line = line([(cx, 190), (cx, 770)], 20)
    pot = Polygon([(cx - 50, 760), (cx + 50, 760), (cx + 56, 860), (cx - 56, 860)]).buffer(6)
    pot = pot.difference(Polygon([(cx - 26, 790), (cx + 26, 790), (cx + 30, 834), (cx - 30, 834)]).buffer(4))
    starp = star_poly(cx, 150, 72, 33).buffer(5, join_style=1)
    star = starp.difference(star_poly(cx, 152, 34, 15))
    boughs = []
    levels, y0, y1, L0, L1 = 6, 250, 690, 70, 300
    for k in range(levels):
        t = k / (levels - 1)
        y, L = y0 + (y1 - y0) * t, L0 + (L1 - L0) * t
        for sg in (-1, 1):
            boughs.append(bez((cx, y), (cx + sg * 0.50 * L, y + 0.20 * L), (cx + sg * 0.93 * L, y + 0.40 * L), 40))
    stems = [line(b, 15) for b in boughs]
    structure = unary_union([trunk_line, pot, star])
    room = Polygon([(0, 0), (1000, 0), (1000, 1000), (0, 1000)])
    placed = []
    for k, b in enumerate(boughs):
        clear = unary_union([structure] + stems[:k] + stems[k + 1:] + placed)
        _, nds = needled_branch(b, clear, room, w=15, nw=12, every=34, needle=38, spread=45, taper=0.35, start=30)
        placed += nds
    g = unary_union([structure] + stems + placed)
    g = g.union(hanger(cx, 86, neck=26))
    return smooth(g)


def drop_shape(cx=500):
    right = [(0, 170), (60, 190), (120, 260), (175, 380), (215, 500), (222, 600), (190, 700), (120, 790),
             (40, 870), (0, 905)]
    pts = right + [(-x, y) for x, y in right[::-1][1:-1]]
    return Polygon(catmull([(cx + x, y) for x, y in pts], n=10)).buffer(0)


def d5_scroll_drop():
    cx = 500
    dr = drop_shape(cx)
    parts = [outline(dr, WF)]
    parts.append(line([(cx, 175), (cx, 900)], W))
    for s in (-1, 1):
        st = polar(cx + s * 120, 630, 64, 0 if s > 0 else 180)
        parts.append(line(bez((cx, 520), (cx + s * 150, 470), st), W))
        parts.append(scroll(cx + s * 120, 630, 64, 16, 0 if s > 0 else 180, 1.1, sgn=s, w=W, dot=13))
        parts.append(line(bez((cx, 390), (cx + s * 120, 330), (cx + s * 110, 260)), W))
        parts.append(scroll(cx + s * 72, 285, 40, 10, 0 if s > 0 else 180, 0.9, sgn=-s, w=14, dot=11))
        parts.append(leaf(cx, 455, -90 + s * 58, 110, 44))
        parts.append(leaf(cx + s * 121, 522, -90 + s * 38, 74, 30))      # leaf on the C-scroll
        parts.append(leaf(cx, 805, -90 + s * 52, 86, 34).intersection(dr.buffer(-4)))
    parts.append(Point(cx, 690).buffer(30, 64))
    parts.append(Point(cx, 905).buffer(24, 48))
    g = unary_union(parts).difference(Point(cx, 690).buffer(15, 48))    # bead eyelet
    g = g.union(hanger(cx, 176, neck=30))
    return smooth(g)


def d6_pinecone():
    cx = 500
    right = [(0, 300), (95, 308), (180, 360), (225, 450), (232, 550), (205, 660), (150, 770), (75, 850), (0, 880)]
    pts = right + [(-x, y) for x, y in right[::-1][1:-1]]
    cone = Polygon(catmull([(cx + x, y) for x, y in pts], n=10)).buffer(0)
    interior = cone.buffer(-WF, join_style=1)          # open space inside the frame
    clip = cone.buffer(-4)
    # overlapping rounded scales: rows of U-arcs, offset every other row
    arcs = []                                          # (centreline, stroke)
    rs, dy = 48, 58
    for j, y in enumerate(range(330, 900, dy)):
        off = 0 if j % 2 == 0 else rs
        for i in range(-6, 7):
            x = cx + off + i * 2 * rs
            c = LineString([(x + rs * math.cos(math.radians(a)), y + rs * math.sin(math.radians(a)))
                            for a in range(0, 181, 6)])
            if c.intersects(interior):
                arcs.append((c, line(list(c.coords), 14)))

    def cells_of(arc_list):
        lat = unary_union([st for _, st in arc_list]).intersection(clip)
        return lat, [c for c in getattr(interior.difference(lat), "geoms", []) if c.area > 1]

    # A partial scale cell at the sides that is too small to cut would be filled
    # solid and leave a blot. Instead drop the short edge arc that closes it off,
    # whole, so the cell joins its neighbour and no arc stub is left behind.
    min_cell = MIN_HOLE + 40
    while True:
        lattice, cells = cells_of(arcs)
        small = [c for c in cells if c.area < min_cell]
        best = None
        for c in small:
            for k, (cl, st) in enumerate(arcs):
                if st.distance(c) > 1:
                    continue
                _, trial = cells_of(arcs[:k] + arcs[k + 1:])
                home = [t for t in trial if t.contains(c.representative_point())]
                if home and home[0].area >= min_cell:
                    ln = cl.intersection(interior).length
                    if best is None or ln < best[0]:
                        best = (ln, k)
        if best is None:
            break
        arcs.pop(best[1])
    parts = [outline(cone, WF), lattice]
    # twig across the top with fir needles; the cone hangs from it on a slim stem
    for s in (-1, 1):
        parts.append(fir_branch(bez((cx, 250), (cx + s * 120, 235), (cx + s * 230, 270), 30),
                                needle=54, every=40, spread=45, taper=0.45))
    parts.append(line([(cx, 240), (cx, 306)], 20))     # round end stays inside the frame band
    g = unary_union(parts)
    g = g.union(hanger(cx, 232, neck=26))
    return smooth(g)


DESIGNS = {
    "01-snowflake-lace-bauble": d1_snowflake_bauble,
    "02-holly-filigree-bell": d2_holly_bell,
    "03-fern-lace-star": d3_fern_star,
    "04-fir-branch-tree": d4_fir_tree,
    "05-scrollwork-drop": d5_scroll_drop,
    "06-filigree-pinecone": d6_pinecone,
}


README = """FILIGREE CHRISTMAS ORNAMENTS - 6 SVG CUT FILES
by Duskwood Designs Co (etsy.com/shop/DuskwoodDesignsCo)
Thank you for your purchase!

DESIGNS
  01 Snowflake Lace Bauble    04 Fir Branch Tree
  02 Holly Filigree Bell      05 Scrollwork Drop
  03 Fern Lace Star           06 Filigree Pinecone

FILES
  SVG/  Cricut Design Space, Silhouette Designer Edition, Inkscape, Illustrator
  DXF/  Silhouette Studio Basic Edition, laser/CNC software (inches)
  PNG/  1800 x 1800 px, transparent background (6 in at 300 DPI)

Each design is a single-layer shape with one clean cut path, including the
hanging loop at the top. Default size is 6 inches; resize freely (keep the
proportions locked). These are lacy, openwork designs: at 6 inches the main
lines are about 0.08 to 0.12 inch wide. We recommend 4 inches or larger for
vinyl, 5 inches or larger for cardstock and laser-cut wood, and the full
6 inches for acrylic, which is more brittle. The finest details are in the
Fir Branch Tree, Fern Lace Star and Scrollwork Drop; do a test cut first on
a new material.

LICENSE
  Personal use: unlimited.
  Small-business commercial use: you may sell finished physical products
  (ornaments, gift tags, cards, decals, shirts, etc.) made with these
  designs, up to 500 units per design.
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


def square_box(geom, pad=12):
    x0, y0, x1, y1 = geom.bounds
    side = max(x1 - x0, y1 - y0) + 2 * pad
    return (x0 + x1) / 2 - side / 2, (y0 + y1) / 2 - side / 2, side


def write_dxf(geom, path, bx_):
    bx, by, side = bx_
    k = SIZE_IN / side
    doc = ezdxf.new("R2010")
    doc.header["$INSUNITS"] = 1
    doc.header["$MEASUREMENT"] = 0
    msp = doc.modelspace()
    polys = geom.geoms if geom.geom_type == "MultiPolygon" else [geom]
    for p in polys:
        for r in [p.exterior, *p.interiors]:
            msp.add_lwpolyline([((x - bx) * k, (side - (y - by)) * k) for x, y in list(r.coords)[:-1]], close=True)
    doc.saveas(path)


def stats(g):
    polys = list(g.geoms) if g.geom_type == "MultiPolygon" else [g]
    hs = [Polygon(i).area for p in polys for i in p.interiors]
    return {"parts": len(polys), "holes": len(hs), "smallest_hole": round(min(hs or [0]), 1), "valid": g.is_valid}


if __name__ == "__main__":
    only = sys.argv[1:]
    meta = {}
    for name, fn in DESIGNS.items():
        if only and not any(o in name for o in only):
            continue
        g = finish(fn())
        box_ = square_box(g)
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{box_[0]:.1f} {box_[1]:.1f} {box_[2]:.1f} {box_[2]:.1f}" '
               f'width="6in" height="6in"><path fill="#000" fill-rule="evenodd" d="{to_path(g)}"/></svg>')
        with open(os.path.join(SVG_DIR, f"{name}.svg"), "w") as f:
            f.write(svg)
        write_dxf(g, os.path.join(DXF_DIR, f"{name}.dxf"), box_)
        meta[name] = stats(g)
    with open(os.path.join(HERE, "bundle", "README-LICENSE.txt"), "w") as f:
        f.write(README)
    print(json.dumps(meta, indent=1))
