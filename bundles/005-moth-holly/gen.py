"""Winter Moths & Holly - 6 single-path SVG/DXF cut files.

Every design is assembled from solid shapes (wings, body, leaves, moon...)
minus cut-out details (snowflakes, crescents, vein slits), unioned into ONE
connected polygon. Holes smaller than MIN_HOLE are filled so nothing is too
small to cut or weed. Output: SVG (6 in), DXF (inches), meta json.
"""
import math, os, json
from shapely.geometry import LineString, Point, Polygon, MultiPolygon
from shapely.ops import unary_union
from shapely import affinity
import ezdxf

HERE = os.path.dirname(os.path.abspath(__file__))
SVG_DIR = os.path.join(HERE, "bundle", "SVG")
DXF_DIR = os.path.join(HERE, "bundle", "DXF")
os.makedirs(SVG_DIR, exist_ok=True)
os.makedirs(DXF_DIR, exist_ok=True)
MIN_HOLE = 600.0
SIZE_IN = 6.0


# ---------------------------------------------------------------- helpers
def catmull(pts, closed=True, n=16):
    """Smooth Catmull-Rom spline through pts."""
    out = []
    P = list(pts)
    m = len(P)
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


def line(pts, w, cap=1):
    return LineString(pts).buffer(w / 2, cap_style=cap, join_style=1)


def mirror(g, cx):
    return affinity.scale(g, -1, 1, origin=(cx, 0))


def sym(g, cx):
    return unary_union([g, mirror(g, cx)])


def snowflake(x, y, r, w, rot=0, branch=True):
    parts = [Point(x, y).buffer(w * 0.9)]
    for k in range(6):
        a = math.radians(rot + 60 * k - 90)
        parts.append(line([(x, y), (x + r * math.cos(a), y + r * math.sin(a))], w))
        if branch:
            bx, by = x + 0.58 * r * math.cos(a), y + 0.58 * r * math.sin(a)
            for s in (-1, 1):
                b = a + s * math.radians(50)
                parts.append(line([(bx, by), (bx + 0.36 * r * math.cos(b), by + 0.36 * r * math.sin(b))], w * 0.85))
    return unary_union(parts)


def crescent(x, y, r, phase=0.42, rot=0):
    """Crescent moon: disc minus shifted disc; opening faces +x before rot."""
    c = Point(x, y).buffer(r, 64).difference(Point(x + r * phase * 1.25, y - r * 0.12).buffer(r * 0.9, 64))
    return affinity.rotate(c, rot, origin=(x, y))


def holly_leaf(x0, y0, ang, L, W, spikes=3, midrib=0):
    """Holly leaf from base (x0,y0) pointing at angle ang (deg). Spiky with
    concave bites between spikes. midrib>0 cuts a vein slit of that width."""
    tips = []
    ts = [0.25 + 0.64 * k / spikes for k in range(spikes)]
    for s in (1, -1):
        side = []
        for t in ts:
            w = W * 0.5 * (math.sin(math.pi * (0.04 + 0.9 * t)) ** 0.8) * 1.1
            side.append((t * L, s * w))
        tips.append(side)
    base = [(0.04 * L, -W * 0.12), (0, 0), (0.04 * L, W * 0.12)]
    outline = base[1:] + tips[0] + [(L * 1.04, 0)] + tips[1][::-1] + base[:1]
    leaf = Polygon(outline).buffer(0)
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
            r = math.hypot(d / 2, off)
            bites.append(Point(mx + nx * off, my + ny * off).buffer(r, 48))
    leaf = leaf.difference(unary_union(bites))
    # petiole
    leaf = leaf.union(line([(-0.12 * L, 0), (0.15 * L, 0)], max(5, W * 0.1)))
    if midrib:
        leaf = leaf.difference(line([(0.14 * L, 0), (0.8 * L, 0)], midrib))
    leaf = affinity.rotate(leaf, ang, origin=(0, 0))
    return affinity.translate(leaf, x0, y0)


def berries(x, y, r, n=3, rot=0):
    pts = [(x, y)] if n == 1 else [(x + r * 1.05 * math.cos(math.radians(rot + 360 * k / n - 90)),
                                    y + r * 1.05 * math.sin(math.radians(rot + 360 * k / n - 90))) for k in range(n)]
    return unary_union([Point(p).buffer(r, 32) for p in pts] + [Point(x, y).buffer(r * 0.8)])


# ---------------------------------------------------------------- moth
WINGS = {
    # forewing, hindwing control points (right side; body centre at 0,0; y down)
    "classic": dict(
        fore=[(3, -20), (25, -42), (60, -60), (95, -66), (104, -56), (96, -32), (78, -10), (48, 2), (18, 4), (4, 0)],
        hind=[(4, -4), (30, 0), (60, 10), (78, 30), (74, 54), (54, 70), (30, 70), (12, 54), (4, 26)]),
    "luna": dict(
        fore=[(3, -20), (22, -46), (52, -66), (88, -78), (96, -70), (86, -44), (66, -16), (40, 0), (16, 4), (4, 0)],
        hind=[(4, -4), (28, 0), (56, 12), (66, 34), (60, 56), (52, 82), (50, 112), (56, 138), (44, 132), (34, 104), (24, 76), (10, 56), (4, 28)]),
    "round": dict(
        fore=[(3, -22), (26, -50), (62, -66), (94, -62), (102, -44), (92, -20), (66, -2), (36, 4), (12, 4), (4, 0)],
        hind=[(4, -4), (34, 2), (64, 14), (80, 36), (72, 62), (48, 76), (24, 72), (10, 54), (4, 26)]),
}


def moth_parts(cx, cy, s, style="classic", antenna="feather", aw=None):
    """Return dict of solid parts in final coordinates. s = units per local unit
    (wing half-span is ~100 local units)."""
    P = lambda pts: [(cx + x * s, cy + y * s) for x, y in pts]
    wd = WINGS[style]
    fore_r = Polygon(catmull(P(wd["fore"])))
    hind_r = Polygon(catmull(P(wd["hind"])))
    fore = sym(fore_r, cx)
    hind = sym(hind_r, cx)
    head = Point(cx, cy - 27 * s).buffer(7 * s)
    thorax = affinity.scale(Point(cx, cy - 9 * s).buffer(1), 10 * s, 18 * s)
    abd_pts = [(0, -2), (8, 6), (7.5, 24), (5, 40), (2, 50), (0, 52), (-2, 50), (-5, 40), (-7.5, 24), (-8, 6)]
    abdomen = Polygon(catmull(P(abd_pts)))
    body = unary_union([head, thorax, abdomen])
    aw = aw or max(6, 2.2 * s)
    ants = []
    for sg in (1, -1):
        p0, p1, p2 = (cx + sg * 3 * s, cy - 32 * s), (cx + sg * 10 * s, cy - 62 * s), (cx + sg * 34 * s, cy - 74 * s)
        c = bez(p0, p1, p2, 40)
        ants.append(line(c, aw))
        if antenna == "feather":
            for i in range(8, 38, 4):
                (x0, y0), (x1, y1) = c[i], c[i + 1]
                dx, dy = x1 - x0, y1 - y0
                d = math.hypot(dx, dy)
                L = (5 + 4 * math.sin(math.pi * (i - 6) / 34)) * s
                for ss in (-1, 1):
                    nx, ny = -dy / d * ss, dx / d * ss
                    ants.append(line([(x0, y0), (x0 + (nx + dx / d * 0.9) * L, y0 + (ny + dy / d * 0.9) * L)], aw * 0.8))
        else:
            ants.append(Point(p2).buffer(aw * 1.3))
    return dict(fore=fore, hind=hind, fore_r=fore_r, hind_r=hind_r, body=body, abdomen=abdomen,
                antennae=unary_union(ants), P=P)


def moth_solid(m, gap=0):
    """Union of the moth parts. gap>0 cuts a thin outline between the abdomen
    and the hindwings so the furry body reads clearly (joined at the thorax)."""
    g = unary_union([m["fore"], m["hind"], m["body"], m["antennae"]])
    if gap:
        P = m["P"]
        (x0, y0), (x1, y1) = P([(-60, 4), (60, 200)])
        clip = Polygon([(x0, y0), (x1, y0), (x1, y1), (x0, y1)])
        ring = m["abdomen"].buffer(gap).difference(m["abdomen"]).intersection(clip)
        g = g.difference(ring)
    return g


def abdomen_stripes(g, m, ys, w=6):
    P = m["P"]
    for yy in ys:
        g = g.difference(line(P([(-3.2, yy), (3.2, yy)]), w))
    return g


def mirror_holes(holes_r, cx):
    return sym(unary_union(holes_r), cx)


def largest(g):
    if g.geom_type == "MultiPolygon":
        return max(g.geoms, key=lambda p: p.area)
    return g


# ---------------------------------------------------------------- finish
def finish(g, simplify=0.35):
    g = g.buffer(0.01).buffer(-0.01).simplify(simplify)
    polys = list(g.geoms) if g.geom_type == "MultiPolygon" else [g]
    polys = [p for p in polys if p.area > 50]  # drop numerical dust only
    g = unary_union([Polygon(p.exterior, [i for i in p.interiors if Polygon(i).area >= MIN_HOLE + 20]) for p in polys])  # +20 margin for 0.1-unit rounding
    return g


# ---------------------------------------------------------------- designs
def d1_snow_moth():
    cx, cy, s = 500, 500, 4.3
    m = moth_parts(cx, cy, s, "classic", "feather")
    g = moth_solid(m, gap=8)
    P = m["P"]
    holes = []
    (fx, fy), = P([(58, -36)])
    holes.append(snowflake(fx, fy, 82, 13, rot=10))
    (hx, hy), = P([(44, 36)])
    holes.append(snowflake(hx, hy, 52, 11, rot=0))
    for p in P([(90, -54), (82, -20)]):
        holes.append(Point(p).buffer(16))
    holes.append(Point(P([(66, 56)])[0]).buffer(15))
    g = g.difference(mirror_holes(holes, cx))
    # scalloped hindwing edge
    ring = m["hind_r"].exterior
    bites = [ring.interpolate(k / 34 * ring.length) for k in range(34)]
    bites = [p.buffer(15) for p in bites if p.x > cx + 30 * s and p.y > cy + 6 * s]
    g = g.difference(sym(unary_union(bites), cx))
    return abdomen_stripes(g, m, (12, 22, 32))


def d2_luna_moth():
    cx, cy, s = 500, 400, 4.4
    m = moth_parts(cx, cy, s, "luna", "feather")
    g = moth_solid(m, gap=8)
    P = m["P"]
    holes = []
    (fx, fy), = P([(50, -42)])
    holes.append(crescent(fx, fy, 38, rot=200))
    (hx, hy), = P([(40, 36)])
    holes.append(crescent(hx, hy, 46, rot=210))
    for a, b in [((14, -14), (38, -30)), ((20, -6), (62, -18)), ((70, -50), (86, -64))]:
        holes.append(line(P([a, b]), 9))
    holes.append(line(P([(44, 74), (46, 112)]), 10))
    holes.append(Point(P([(20, 56)])[0]).buffer(15))
    g = g.difference(mirror_holes(holes, cx))
    return abdomen_stripes(g, m, (12, 22, 32))


def d3_holly_wreath():
    cx, cy, R = 500, 500, 330
    parts = [Point(cx, cy).buffer(R + 8).difference(Point(cx, cy).buffer(R - 8))]
    n = 13
    for k in range(n):
        a = 360 * k / n
        ar = math.radians(a)
        bx, by = cx + R * math.cos(ar), cy + R * math.sin(ar)
        parts.append(holly_leaf(bx, by, a + 90 - 22, 165, 78, spikes=4, midrib=7))
        parts.append(holly_leaf(bx, by, a + 90 + 30, 130, 62, spikes=3, midrib=6))
    for k in range(n):
        if k % 2:
            continue
        a = math.radians(360 * k / n + 16)
        parts.append(berries(cx + (R + 10) * math.cos(a), cy + (R + 10) * math.sin(a), 20, 3, rot=math.degrees(a)))
    wreath = unary_union(parts)
    # moth in front of the wreath, wings overlapping it left and right
    m = moth_parts(cx, cy + 20, 2.95, "round", "feather", aw=8)
    moth = moth_solid(m, gap=7)
    P = m["P"]
    (lx, ly), = P([(26, -22)])
    la = -22
    leafhole = holly_leaf(lx, ly, la, 170, 86, 4)
    rib = line([(lx - 20 * math.cos(math.radians(la)), ly - 20 * math.sin(math.radians(la))),
                (lx + 200 * math.cos(math.radians(la)), ly + 200 * math.sin(math.radians(la)))], 9)
    holes = [leafhole.difference(rib).difference(m["fore_r"].exterior.buffer(14)),
             berries(*P([(42, 36)])[0], 15, 3, rot=0).difference(Point(P([(42, 36)])[0]).buffer(13))]
    hb = berries(*P([(42, 36)])[0], 15, 3, rot=0)
    holes[1] = unary_union([Point(p).buffer(15) for p in
                            [(P([(42, 36)])[0][0] + 20 * math.cos(math.radians(a)), P([(42, 36)])[0][1] + 20 * math.sin(math.radians(a))) for a in (-90, 30, 150)]])
    moth = moth.difference(mirror_holes(holes, cx))
    moth = abdomen_stripes(moth, m, (14, 26))
    halo = unary_union([m["fore"], m["hind"]]).buffer(14)
    ringband = parts[0]
    tabs = ringband.intersection(halo).difference(halo.buffer(-30))
    g = unary_union([wreath.difference(halo), moth, tabs])
    return largest(g)


def star_poly(cx, cy, R, r, n=5, rot=-90):
    pts = []
    for k in range(2 * n):
        rr = R if k % 2 == 0 else r
        a = math.radians(rot + 180 * k / n)
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return Polygon(pts)


def d4_moth_star():
    cx, cy = 500, 500
    st = star_poly(cx, cy + 30, 485, 205)
    band = st.difference(st.buffer(-22, join_style=2))
    band2 = star_poly(cx, cy + 30, 430, 180)
    band2 = band2.difference(band2.buffer(-9, join_style=2))
    m = moth_parts(cx, cy + 35, 3.25, "classic", "feather", aw=8)
    moth = moth_solid(m, gap=7)
    P = m["P"]
    holes = []
    for ring_poly, n in ((m["fore_r"], 22), (m["hind_r"], 16)):
        inner = ring_poly.buffer(-30).exterior
        for k in range(n):
            p = inner.interpolate(k / n * inner.length)
            if p.x > cx + 30 * 3.25:
                holes.append(p.buffer(15))
    holes.append(star_poly(*P([(54, -30)])[0], 40, 17))
    holes.append(Point(P([(42, 34)])[0]).buffer(24))
    moth = moth.difference(mirror_holes(holes, cx))
    moth = abdomen_stripes(moth, m, (12, 24, 34))
    halo = unary_union([m["fore"], m["hind"], m["antennae"].buffer(6)]).buffer(13)
    g = unary_union([band.difference(halo), moth])
    # tabs where the outer band meets the wings so it stays one piece
    tabs = band.intersection(halo).difference(halo.buffer(-30))
    g = unary_union([g, tabs])
    return largest(g)


def d5_corner():
    mx, my, mr = 225, 225, 200
    moon = Point(mx, my).buffer(mr, 96).difference(Point(mx + 95, my + 95).buffer(175, 96))
    vine_pts = [(250, 48), (360, 80), (490, 60), (620, 92), (760, 66), (880, 88), (965, 72)]
    vine = catmull(vine_pts, closed=False, n=20)
    v = [line(vine, 16)]
    ls = LineString(vine)
    for k, t in enumerate([0.24, 0.42, 0.60, 0.78]):
        p = ls.interpolate(t, normalized=True)
        q = ls.interpolate(t + 0.01, normalized=True)
        a = math.degrees(math.atan2(q.y - p.y, q.x - p.x))
        sz = 1.15 - 0.45 * t
        v.append(holly_leaf(p.x, p.y, a + 42, 165 * sz, 76 * sz, 4, midrib=7))
        v.append(holly_leaf(p.x, p.y, a - 25, 130 * sz, 60 * sz, 3, midrib=6))
        v.append(holly_leaf(p.x, p.y, a + 95, 105 * sz, 50 * sz, 3, midrib=5))
        v.append(berries(p.x + 30 * sz, p.y + 10, 17, 3, rot=25 * k))
    v.append(holly_leaf(960, 72, 12, 80, 42, 3))
    top = unary_union(v)
    side = affinity.scale(affinity.rotate(top, 90, origin=(0, 0)), -1, 1, origin=(0, 0))
    # moth resting in the crook of the moon, wings touching the inner curve
    ox, oy = mx + 100, my + 100
    m = moth_parts(ox, oy, 1.6, "round", "feather", aw=6)
    moth = moth_solid(m, gap=5)
    P = m["P"]
    moth = moth.difference(mirror_holes([Point(P([(60, -34)])[0]).buffer(18),
                                         Point(P([(40, 38)])[0]).buffer(17)], ox))
    moth = abdomen_stripes(moth, m, (14, 26), w=5)
    moth = affinity.rotate(moth, -45, origin=(ox, oy))
    g = unary_union([moon, top, side, moth])
    return largest(g)


def d6_ornament():
    cx, cy, R = 500, 575, 395
    disc = Point(cx, cy).buffer(R, 128)
    cap = Polygon([(432, 128), (568, 128), (575, 196), (425, 196)])
    loop = Point(cx, 88).buffer(46).difference(Point(cx, 88).buffer(28))
    g = unary_union([disc, cap.buffer(6), loop])
    for x in (465, 500, 535):
        g = g.difference(line([(x, 142), (x, 182)], 10))
    g = g.union(holly_leaf(445, 192, 197, 150, 72, 4, midrib=7))
    g = g.union(holly_leaf(555, 192, -17, 150, 72, 4, midrib=7))
    g = g.union(berries(500, 210, 20, 3, rot=0))
    # moth as negative space; body and veins stay solid as bridges
    m = moth_parts(cx, cy + 10, 2.9, "round", "plain", aw=7)
    P = m["P"]
    wings = unary_union([m["fore"], m["hind"]])
    hole = wings.difference(m["body"].buffer(9))
    veins = []
    for a, b, c in [((6, -16), (40, -44), (96, -58)), ((8, -8), (50, -22), (100, -36)),
                    ((8, -1), (44, -4), (80, -10)), ((6, 4), (44, 18), (78, 38)), ((6, 10), (30, 42), (48, 74))]:
        veins.append(line(bez(*P([a, b, c]), 30), 13))
    veins = sym(unary_union(veins), cx)
    hole = hole.difference(veins)
    hole = hole.difference(sym(Point(P([(58, -30)])[0]).buffer(24), cx))
    hole = hole.difference(sym(Point(P([(40, 34)])[0]).buffer(20), cx))
    g = g.difference(hole)
    # feathery antennae slits
    for sg in (1, -1):
        c = bez(*P([(sg * 3, -32), (sg * 10, -60), (sg * 32, -74)]), 30)
        g = g.difference(line(c, 8))
        for i in range(6, 28, 4):
            (x0, y0), (x1, y1) = c[i], c[i + 1]
            dx, dy = x1 - x0, y1 - y0
            d = math.hypot(dx, dy)
            for ss in (-1, 1):
                nx, ny = -dy / d * ss, dx / d * ss
                L = 22
                g = g.difference(line([(x0, y0), (x0 + (nx + dx / d) * L * 0.7, y0 + (ny + dy / d) * L * 0.7)], 6))
    for k in range(36):
        a = math.degrees(2 * math.pi * k / 36)
        if abs(a - 270) < 25:
            continue
        ar = math.radians(a)
        g = g.difference(Point(cx + (R - 30) * math.cos(ar), cy + (R - 30) * math.sin(ar)).buffer(14.5))
    for (x, y, r) in [(cx - 250, cy + 185, 40), (cx + 250, cy + 185, 40), (cx, cy + 300, 36),
                      (cx - 285, cy - 140, 32), (cx + 285, cy - 140, 32)]:
        g = g.difference(snowflake(x, y, r, 9))
    return largest(g)


DESIGNS = {
    "01-snowflake-moth": d1_snow_moth,
    "02-luna-moon-moth": d2_luna_moth,
    "03-holly-wreath-moth": d3_holly_wreath,
    "04-moth-over-star": d4_moth_star,
    "05-holly-moon-corner": d5_corner,
    "06-moth-ornament": d6_ornament,
}


# ---------------------------------------------------------------- export
def to_path(geom):
    polys = geom.geoms if geom.geom_type == "MultiPolygon" else [geom]
    d = []
    for p in polys:
        for ring in [p.exterior, *p.interiors]:
            pts = list(ring.coords)
            d.append("M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts[:-1]) + " Z")
    return " ".join(d)


def square_box(geom, pad=12):
    x0, y0, x1, y1 = geom.bounds
    side = max(x1 - x0, y1 - y0) + 2 * pad
    return (x0 + x1) / 2 - side / 2, (y0 + y1) / 2 - side / 2, side


def write_dxf(geom, path, box):
    bx, by, side = box
    k = SIZE_IN / side
    doc = ezdxf.new("R2010")
    doc.header["$INSUNITS"] = 1  # inches
    doc.header["$MEASUREMENT"] = 0
    msp = doc.modelspace()
    polys = geom.geoms if geom.geom_type == "MultiPolygon" else [geom]
    for p in polys:
        for ring in [p.exterior, *p.interiors]:
            pts = [((x - bx) * k, (side - (y - by)) * k) for x, y in list(ring.coords)[:-1]]
            msp.add_lwpolyline(pts, close=True)
    doc.saveas(path)


def stats(g):
    polys = list(g.geoms) if g.geom_type == "MultiPolygon" else [g]
    hs = [Polygon(i).area for p in polys for i in p.interiors]
    return {"parts": len(polys), "holes": len(hs), "smallest_hole": round(min(hs or [0]), 1),
            "valid": g.is_valid}


if __name__ == "__main__":
    import sys
    only = sys.argv[1:]
    meta = {}
    for name, fn in DESIGNS.items():
        if only and not any(o in name for o in only):
            continue
        g = finish(fn())
        box = square_box(g)
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{box[0]:.1f} {box[1]:.1f} {box[2]:.1f} {box[2]:.1f}" '
               f'width="6in" height="6in"><path fill="#000" fill-rule="evenodd" d="{to_path(g)}"/></svg>')
        with open(os.path.join(SVG_DIR, f"{name}.svg"), "w") as f:
            f.write(svg)
        write_dxf(g, os.path.join(DXF_DIR, f"{name}.dxf"), box)
        meta[name] = stats(g)
    print(json.dumps(meta, indent=1))
