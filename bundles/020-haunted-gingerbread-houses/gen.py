"""Haunted Gingerbread Houses - 6 single-path SVG/DXF cut files.

Spooky "Gothmas" gingerbread houses drawn in code (no AI images): crooked
walls, thick iced roof slabs with dripping or scalloped piped icing (cut
lines), gumdrops, candy canes, a skull topper, coffin door, spider web,
jack-o'-lantern, bats, crescent moon, dead trees, tombstones and an iron
fence. Five standing pieces on a flat base strip (or an ornament ring) and
one wide village panel. Everything is unioned into ONE connected polygon;
bats, moon, smoke and spider are attached, never floating. compose() closes
solid parts by a few units so near-touching pieces are bridged, house
openings are subtracted at the outer level, and finish() closes then opens
by 6.5 units (no material or gap narrower than ~13 units) and fills any
hole under MIN_HOLE. Coordinates are SVG-style (y down), ~1000-unit canvas.

Usage:  python3 gen.py            build bundle/SVG + bundle/DXF + README
        python3 gen.py --check    verify the files (unzips the ZIP into bundle/ if needed)
Helpers below the first marker are reused from bundle 008 (Christmas village).
"""
import math, os, json, sys
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


def arch(x0, x1, y_top, y_bot):
    """Round-topped opening (door / window): half-circle on a rectangle."""
    r = (x1 - x0) / 2
    return U([circ((x0 + x1) / 2, y_top + r, r), rect(x0, y_top + r, x1, y_bot)])


def lancet(x0, x1, y_top, y_bot):
    """Pointed gothic-arch window."""
    w = x1 - x0
    r = w * 0.9
    cy = y_top + math.sqrt(r * r - (r - w / 2) ** 2)
    a = circ(x0 + r, cy, r).intersection(circ(x1 - r, cy, r))
    a = a.intersection(rect(x0, y_top - 5, x1, cy))
    return U([a, rect(x0, cy - 0.5, x1, y_bot)])


def panes(win, cx, cy, mull=16, vertical=True, horizontal=True):
    """Window opening minus a cross of glazing bars -> separate pane holes."""
    bars = []
    x0, y0, x1, y1 = win.bounds
    if vertical:
        bars.append(rect(cx - mull / 2, y0 - 5, cx + mull / 2, y1 + 5))
    if horizontal:
        bars.append(rect(x0 - 5, cy - mull / 2, x1 + 5, cy + mull / 2))
    return win.difference(U(bars))


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


def wavy(p0, p1, amp, wl, step=2.0):
    """Wavy line from p0 to p1 (for piped-icing cut-outs)."""
    L = math.dist(p0, p1)
    tx, ty = (p1[0] - p0[0]) / L, (p1[1] - p0[1]) / L
    nx, ny = -ty, tx
    n = max(2, int(L / step))
    out = []
    for k in range(n + 1):
        s = L * k / n
        o = amp * math.sin(2 * math.pi * s / wl)
        out.append((p0[0] + tx * s + nx * o, p0[1] + ty * s + ny * o))
    return out


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


def snow_roof(l, p, r, cap=13, drips=()):
    """Gable roof (triangle l-p-r) with a rounded snow edge and snow drips."""
    g = U([poly([l, p, r]), line([l, p, r], 2 * cap)])
    for (x, y, rr) in drips:
        g = U([g, circ(x, y, rr)])
    return g


def eave_drips(l, p, r, cap, n_each=2, over=1.0):
    """Drip circles along the outer ends of both roof slopes."""
    out = []
    for a, b in ((l, p), (r, p)):
        for k in range(n_each):
            t = 0.04 + 0.11 * k * over
            x = a[0] + (b[0] - a[0]) * t
            y = a[1] + (b[1] - a[1]) * t
            out.append((x, y + cap + 3 - 3 * k, 10 - 2 * k))
    return out


def smoke(x0, y0, pts, r0=13, r1=30):
    """Chimney smoke: overlapping puffs along a curve, growing as they rise."""
    P = [(x0, y0)] + pts
    ls = LineString(P)
    n = max(3, int(ls.length / ((r0 + r1) * 0.62)))
    parts = [line(P, r0 * 1.4)]
    for k in range(n + 1):
        t = k / n
        q = ls.interpolate(ls.length * t)
        parts.append(circ(q.x, q.y, r0 + (r1 - r0) * t ** 1.1))
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
    return S.difference(U(holes))


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


import random


# ---------------------------------------------------------------- haunted helpers
def ellipse(cx, cy, rx, ry):
    return affinity.translate(affinity.scale(Point(0, 0).buffer(1, 48), rx, ry), cx, cy)


def bat(cx, cy, s, rot=0):
    """Bat silhouette, wingspan ~s. Scalloped wing edges, pointed ears."""
    u = s / 100.0
    parts = [ellipse(0, 5, 9, 17), circ(0, -14, 10),
             poly([(-9, -17), (-10, -33), (-1, -21)]), poly([(9, -17), (10, -33), (1, -21)])]
    top = [(3, -8), (14, -19), (27, -27), (41, -31), (55, -36)]
    fingers = [(55, -36), (49, 2), (35, -1), (21, 12), (4, 14)]
    wing = poly(top + fingers[1:])
    bites = []
    for a, b in zip(fingers[:-2], fingers[1:-1]):
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        L = math.dist(a, b)
        nx, ny = (b[1] - a[1]) / L, -(b[0] - a[0]) / L
        if ny < 0:
            nx, ny = -nx, -ny
        rr = 0.62 * L
        bites.append(circ(mx + nx * rr * 0.55, my + ny * rr * 0.55, rr))
    wing = wing.difference(U(bites))
    parts += [wing, affinity.scale(wing, -1, 1, origin=(0, 0))]
    g = U(parts)
    g = affinity.scale(g, u, u, origin=(0, 0))
    g = affinity.rotate(g, rot, origin=(0, 0))
    return affinity.translate(g, cx, cy)


def taper(p0, p1, w0, w1):
    a = math.atan2(p1[1] - p0[1], p1[0] - p0[0]) + math.pi / 2
    c, s = math.cos(a), math.sin(a)
    q = poly([(p0[0] + c * w0 / 2, p0[1] + s * w0 / 2), (p1[0] + c * w1 / 2, p1[1] + s * w1 / 2),
              (p1[0] - c * w1 / 2, p1[1] - s * w1 / 2), (p0[0] - c * w0 / 2, p0[1] - s * w0 / 2)])
    return U([q, circ(*p0, w0 / 2), circ(*p1, w1 / 2)])


def dead_tree(x, gy, h, w0=44, seed=1, lean=0, depth=4):
    """Gnarled bare tree: flared roots, a tapering crooked trunk splitting
    into crooked branches with small side twigs."""
    rnd = random.Random(seed)
    parts = [poly([(x - w0 * 2.0, gy + 2), (x - w0 * 0.9, gy - w0 * 0.5), (x - w0 * 0.45, gy - w0 * 1.6), (x + w0 * 0.45, gy - w0 * 1.6),
                   (x + w0 * 0.9, gy - w0 * 0.5), (x + w0 * 2.0, gy + 2)]).buffer(-8).buffer(8)]

    def grow(p, ang, length, w, d):
        mid = polar(p[0], p[1], length * 0.5, ang + rnd.uniform(-16, 16))
        end = polar(mid[0], mid[1], length * 0.5, ang + rnd.uniform(-20, 20))
        w1 = max(15, w * 0.7)
        parts.append(taper(p, mid, w, (w + w1) / 2))
        parts.append(taper(mid, end, (w + w1) / 2, w1))
        if d == 0:
            return
        spread = rnd.uniform(22, 34)
        for sgn in (-1, 1):
            grow(end, ang + sgn * spread + rnd.uniform(-8, 8), length * rnd.uniform(0.6, 0.78), max(15, w1 * 0.85), d - 1)
        if d >= 2 and rnd.random() < 0.7:
            grow(mid, ang + rnd.choice([-1, 1]) * rnd.uniform(45, 60), length * 0.42, max(15, w * 0.55), 0)

    grow((x, gy - 10), -90 + lean, h * 0.36, w0, depth)
    g = U(parts)
    return g


def drips(a, b, n, dmin, dmax, w, seed=3, margin=0.12):
    """Icing drips hanging straight down from the segment a-b."""
    rnd = random.Random(seed)
    out = []
    for k in range(n):
        t = margin + (1 - 2 * margin) * (k + 0.5) / n + rnd.uniform(-0.02, 0.02)
        x, y = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
        d = rnd.uniform(dmin, dmax)
        out.append(U([rect(x - w / 2, y - 10, x + w / 2, y + d), circ(x, y + d, w * 0.62)]))
    return U(out)


def outline_cut(shape, region, gap=15):
    """Cut a gap-wide line around `shape`, but only inside `region` (so the
    shape stays attached wherever it leaves the region)."""
    return shape.buffer(gap, quad_segs=16).difference(shape).intersection(region)


def gumdrop(cx, by, r):
    return U([circ(cx, by - r * 0.85, r), rect(cx - r, by - r * 0.85, cx + r, by, 4)])


def skull(cx, cy, r):
    """Solid skull (returns solid, holes)."""
    solid = U([circ(cx, cy, r), rect(cx - 0.6 * r, cy + 0.35 * r, cx + 0.6 * r, cy + 1.08 * r, 0.18 * r)])
    holes = U([ellipse(cx - 0.4 * r, cy + 0.14 * r, 0.27 * r, 0.31 * r),
               ellipse(cx + 0.4 * r, cy + 0.14 * r, 0.27 * r, 0.31 * r),
               poly([(cx, cy + 0.42 * r), (cx - 0.16 * r, cy + 0.72 * r), (cx + 0.16 * r, cy + 0.72 * r)]).buffer(2)])
    return solid, holes


def tombstone(cx, gy, w, h):
    """Rounded headstone with a cross cut-out. Returns solid, holes."""
    solid = U([rect(cx - w / 2, gy - h + w / 2, cx + w / 2, gy + 2), circ(cx, gy - h + w / 2, w / 2)])
    cy = gy - h + w * 0.62
    if w < 66:
        return solid, Polygon()
    holes = U([rect(cx - 9, cy - w * 0.28, cx + 9, cy + w * 0.5), rect(cx - w * 0.24, cy - 9 - w * 0.06, cx + w * 0.24, cy + 9 - w * 0.06)])
    return solid, holes


def candy_cane(x, gy, h, w=26, hook=46, left=False):
    sgn = -1 if left else 1
    top = gy - h
    cx, cy = x + sgn * hook, top + hook
    pts = [(x, gy + 2)]
    for k in range(0, 181, 10):
        a = math.radians(180 + k)
        pts.append((cx + sgn * hook * math.cos(a), cy + hook * math.sin(a)))
    pts.append((x + sgn * 2 * hook, top + hook + 22))
    return line(pts, w)


def spider(cx, cy, s=1.0):
    parts = [ellipse(cx, cy + 6 * s, 24 * s, 28 * s), circ(cx, cy - 26 * s, 16 * s)]
    for sgn in (-1, 1):
        for k, (a1, a2) in enumerate([(-35, -80), (-8, -40), (18, 40), (42, 80)]):
            p0 = (cx, cy - 4 * s + k * 6 * s)
            p1 = polar(cx, cy - 4 * s + k * 6 * s, 50 * s, (a1 if sgn > 0 else 180 - a1))
            p2 = polar(p1[0], p1[1], 38 * s, (a2 if sgn > 0 else 180 - a2) + (0 if k < 2 else 0))
            parts.append(line([p0, p1, p2], 14))
    return U(parts)


def web_holes(region, apex, spokes_deg, ring_r, w=15):
    """Spider web inside `region`: spokes from `apex` plus sagging rings; the
    returned holes are the web cells (region minus threads)."""
    threads = []
    for a in spokes_deg:
        threads.append(line([apex, polar(apex[0], apex[1], 2000, a)], w))
    for R in ring_r:
        pts = []
        for a0, a1 in zip(spokes_deg[:-1], spokes_deg[1:]):
            for k in range(0, 11):
                t = k / 10
                a = a0 + (a1 - a0) * t
                rr = R * (1 - 0.13 * math.sin(math.pi * t))
                pts.append(polar(apex[0], apex[1], rr, a))
        threads.append(line(pts, w))
    return region.difference(U(threads))


def web_window(cx, cy, R, spokes=8, rings=(0.36, 0.68), w=15, rot=-90):
    """Round window filled with a spider web: the cells are the holes."""
    th = [circ(cx, cy, R * 0.12)]
    angs = [rot + 360 * k / spokes for k in range(spokes)]
    for a in angs:
        th.append(line([(cx, cy), polar(cx, cy, R + 10, a)], w))
    for fr in rings:
        pts = []
        for a0 in angs + [angs[0] + 360]:
            pass
        for k in range(spokes):
            a0, a1 = angs[k], angs[k] + 360 / spokes
            for j in range(11):
                t = j / 10
                rr = R * fr * (1 - 0.2 * math.sin(math.pi * t))
                pts.append(polar(cx, cy, rr, a0 + (a1 - a0) * t))
        pts.append(pts[0])
        th.append(line(pts, w))
    return circ(cx, cy, R).difference(U(th))


def gable_house(x0, x1, gy, wt, peak, eave=44, band=48):
    """Walls + a gable roof drawn as a thick iced slab. Returns
    (walls, roof_band, gable_triangle, l, p, r)."""
    cx = (x0 + x1) / 2
    l, p, r = (x0 - eave, wt + 18), (cx, peak), (x1 + eave, wt + 18)
    walls = rect(x0, wt, x1, gy + 4)
    roof = line([l, p, r], band)
    gab = poly([l, p, r])
    return walls, roof, gab, l, p, r


def under_drips(l, p, r, band, n, dmin, dmax, w, seed):
    """Icing drips hanging from the under-side of both roof slopes."""
    out = []
    for a, b, sd in ((l, p, seed), (p, r, seed + 7)):
        # shift the slope line down to the slab's lower edge
        ux, uy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(ux, uy)
        nx, ny = -uy / L, ux / L
        if ny < 0:
            nx, ny = -nx, -ny
        off = band / 2 - 4
        out.append(drips((a[0] + nx * off, a[1] + ny * off), (b[0] + nx * off, b[1] + ny * off), n, dmin, dmax, w, sd))
    return U(out)


def scallop_eaves(l, p, r, rr, n, off=12):
    sc = []
    for a, b in ((l, p), (r, p)):
        for k in range(n):
            t = 0.03 + 0.8 * k / max(1, n - 1)
            sc.append(circ(a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t + off, rr))
    return U(sc)


def shingle_cuts(tri, rows_gap=54, w=16, rr=28, amp=0.72):
    """Rows of fish-scale shingle lines cut into the gable `tri`: half-round
    scallops hanging from each row, alternate rows offset by half a scale.
    Rows are rows_gap apart so neighbouring lines never touch."""
    x0, y0, x1, y1 = tri.bounds
    cuts = []
    y = y0 + rows_gap * 0.8
    i = 0
    while y < y1 - 10:
        pts = []
        for k in range(int((x1 - x0) / 2) + 1):
            xx = x0 + 2 * k
            ph = ((xx - x0) / (2 * rr) + (0.5 if i % 2 else 0)) % 1.0
            pts.append((xx, y + rr * amp * math.sqrt(max(0.0, 1 - (2 * ph - 1) ** 2))))
        cuts.append(line(pts, w))
        y += rows_gap
        i += 1
    return U(cuts).intersection(tri)


def iron_fence(x0, x1, top, bot, gap=20, bar=16):
    """Spear-topped iron fence: bars between two rails, diamond spear tips."""
    parts = [rect(x0, bot - 22, x1, bot + 4), rect(x0, top + 40, x1, top + 58)]
    n = int((x1 - x0 - bar) / (bar + gap))
    sp = (x1 - x0 - bar) / n
    for k in range(n + 1):
        x = x0 + bar / 2 + k * sp
        parts.append(rect(x - bar / 2, top + 12, x + bar / 2, bot))
        parts.append(poly([(x, top - 16), (x + 15, top + 10), (x, top + 24), (x - 15, top + 10)]))
    return U(parts)


def coffin(cx, y0, y1, w):
    h = y1 - y0
    return poly([(cx - w * 0.32, y0), (cx + w * 0.32, y0), (cx + w * 0.5, y0 + h * 0.28),
                 (cx + w * 0.36, y1), (cx - w * 0.36, y1), (cx - w * 0.5, y0 + h * 0.28)])


def broken_heart(cx, cy, s):
    heart = U([circ(cx - 19 * s, cy - 8 * s, 21 * s), circ(cx + 19 * s, cy - 8 * s, 21 * s),
               poly([(cx - 38 * s, cy - 2 * s), (cx + 38 * s, cy - 2 * s), (cx, cy + 40 * s)])])
    crack = line([(cx + 2 * s, cy - 40 * s), (cx - 8 * s, cy - 12 * s), (cx + 8 * s, cy + 4 * s),
                  (cx - 4 * s, cy + 22 * s), (cx + 2 * s, cy + 50 * s)], 15)
    return heart.difference(crack)


def pumpkin(cx, gy, rx, ry):
    cy = gy - ry
    body = U([ellipse(cx - rx * 0.42, cy, rx * 0.6, ry), ellipse(cx + rx * 0.42, cy, rx * 0.6, ry),
              ellipse(cx, cy, rx * 0.62, ry * 1.04)])
    stem = line([(cx, cy - ry * 0.9), (cx + 4, cy - ry * 1.18), (cx + 18, cy - ry * 1.32)], 20)
    solid = U([body, stem, rect(cx - rx * 0.6, gy - 12, cx + rx * 0.6, gy + 2)])
    e = rx * 0.2
    holes = U([poly([(cx - rx * 0.56, cy - ry * 0.02), (cx - rx * 0.12, cy - ry * 0.02), (cx - rx * 0.34, cy - ry * 0.56)]),
               poly([(cx + rx * 0.56, cy - ry * 0.02), (cx + rx * 0.12, cy - ry * 0.02), (cx + rx * 0.34, cy - ry * 0.56)]),
               poly([(cx - rx * 0.6, cy + ry * 0.2), (cx - rx * 0.3, cy + ry * 0.32), (cx - rx * 0.16, cy + ry * 0.18),
                     (cx, cy + ry * 0.34), (cx + rx * 0.16, cy + ry * 0.18), (cx + rx * 0.3, cy + ry * 0.32),
                     (cx + rx * 0.6, cy + ry * 0.2), (cx + rx * 0.3, cy + ry * 0.62), (cx - rx * 0.3, cy + ry * 0.62)])])
    return solid, holes




# ---------------------------------------------------------------- designs
BY = 890


def icing_line(a, b, off, kind="drips", n=5, dmin=24, dmax=60, wd=26, amp=14, period=52, w=16, seed=1, m0=0.1, m1=0.1):
    """Piped-icing cut line running parallel to the roof slope a->b, `off`
    units below its centre line: either a line with smooth drips hanging
    straight down ('drips') or a row of scallops ('scallops'). A single open
    line never encloses material, so it can't create islands."""
    ux, uy = b[0] - a[0], b[1] - a[1]
    L = math.hypot(ux, uy)
    ux, uy = ux / L, uy / L
    nx, ny = -uy, ux
    if ny < 0:
        nx, ny = -nx, -ny
    rnd = random.Random(seed)
    s0, s1 = L * m0, L * (1 - m1)
    cs = [s0 + (s1 - s0) * (k + 0.5) / n for k in range(n)]
    ds = [rnd.uniform(dmin, dmax) for _ in range(n)]
    pts = []
    for k in range(int((s1 - s0) / 2) + 1):
        sv = s0 + 2 * k
        x, y = a[0] + ux * sv + nx * off, a[1] + uy * sv + ny * off
        if kind == "drips":
            for c, d in zip(cs, ds):
                q = (sv - c) / wd
                if abs(q) < 1:
                    y += d * math.cos(math.pi * q / 2) ** 2
        else:
            y += amp * abs(math.sin(math.pi * (sv - s0) / period))
        pts.append((x, y))
    return line(pts, w)


def eave_drip(x, y_top, length, w=18):
    return U([rect(x - w / 2, y_top, x + w / 2, y_top + length), circ(x, y_top + length, w * 0.62)])


def iced_house(x0, x1, wt, peak, eave=44, band=50, style="drips", n=5, seed=1, dmin=26, dmax=70, dw=26, gap=17, gy=BY,
               off=None, amp=14, period=52, edrip=True):
    """Gingerbread house body: walls, gable and a thick roof slab. Piped icing
    is a cut line under each slope (drips or scallops), and icing drips hang
    off both eaves where they show against the sky. Returns (solid list,
    hole list, (l, p, r))."""
    walls, roof, gab, l, p, r = gable_house(x0, x1, gy, wt, peak, eave, band)
    off = band / 2 + gap / 2 + 9 if off is None else off
    holes = []
    inside = U([walls, gab.intersection(rect(x0, 0, x1, gy))]).buffer(-20)
    for k, (a, b) in enumerate(((l, p), (r, p))):
        if style != "none":
            ic = icing_line(a, b, off, style, n, dmin, dmax, dw, amp, period, gap, seed + 7 * k, 0.12, 0.2)
            holes.append(ic.intersection(inside))
    solid = [walls, roof, gab]
    if edrip:
        for (e, side) in ((l, -1), (r, 1)):
            xd = e[0] - side * eave * 0.25
            solid.append(eave_drip(xd - side * 0, e[1], band * 0.5 + 18, max(16, band * 0.36)))
    return solid, holes, (l, p, r)


def roof_gumdrops(l, p, r, band, ts, rr=20):
    """Gumdrops sitting on the top edge of both roof slopes."""
    out = []
    for a in (l, r):
        ux, uy = p[0] - a[0], p[1] - a[1]
        L = math.hypot(ux, uy)
        nx, ny = uy / L, -ux / L
        if ny > 0:
            nx, ny = -nx, -ny
        for t in ts:
            x, y = a[0] + ux * t + nx * (band / 2 + rr * 0.55), a[1] + uy * t + ny * (band / 2 + rr * 0.55)
            out.append(circ(x, y, rr))
    return U(out)


def d1_crooked_house():
    solid, holes = [], []
    solid.append(base_strip(110, 890, BY, 940))
    hs, hh, (l, p, r) = iced_house(320, 630, 590, 330, eave=46, band=52, n=5, seed=11)
    hs.append(roof_gumdrops(l, p, r, 52, (0.3, 0.62), 21))
    hs.append(gumdrop(p[0], p[1] - 22, 27))
    hs += [rect(552, 330, 604, 470), rect(540, 314, 616, 342, 6)]
    hh.append(panes(circ(475, 512, 34), 475, 512, 14))
    hh.append(panes(lancet(350, 424, 640, 792), 387, 728, 16))
    hh.append(arch(530, 614, 770, BY - 18).difference(rect(564, 760, 580, 900)))
    hh.append(candy_cane(512, BY - 24, 120, 18, 22, left=True))
    hh.append(line(wavy((340, 610), (612, 610), 7, 46), 15).difference(U(hs[1:4]).buffer(10)))
    tf = lambda g: affinity.rotate(affinity.skew(g, xs=-5, origin=(475, BY)), 1.5, origin=(475, BY))
    solid.append(tf(compose(hs, [], 6))); holes.append(tf(U(hh)))
    # chimney smoke curling up to a bat; crescent moon caught in the dead tree
    sky = U([smoke(578, 312, [(604, 288), (590, 258), (626, 232), (668, 226)], 12, 26), bat(716, 196, 160, -10)])
    solid.append(affinity.rotate(affinity.skew(sky, xs=-5, origin=(475, BY)), 1.5, origin=(475, BY)))
    solid.append(crescent(205, 352, 112, 44, -30, 0.86))
    solid.append(dead_tree(190, BY, 470, 36, seed=2, lean=-3))
    s, h = tombstone(805, BY, 96, 158)
    solid.append(s); holes.append(h)
    return compose(solid, holes)


def d2_turret_manor():
    solid, holes = [], []
    solid.append(base_strip(130, 905, BY, 940))
    hs, hh, (l, p, r) = iced_house(430, 760, 580, 330, eave=40, band=48, style="scallops")
    hs.append(gumdrop(p[0], p[1] - 22, 25))
    hs.append(roof_gumdrops(l, p, r, 48, (0.35, 0.68), 19))
    # round tower with a crooked witch-hat roof
    hs.append(rect(240, 430, 395, BY + 4))
    cone = []
    for t in [k / 30 for k in range(31)]:
        cone.append(((1 - t) ** 2 * 200 + 2 * (1 - t) * t * 290 + t * t * 318, (1 - t) ** 2 * 440 + 2 * (1 - t) * t * 340 + t * t * 140))
    for t in [k / 30 for k in range(31)]:
        cone.append(((1 - t) ** 2 * 318 + 2 * (1 - t) * t * 340 + t * t * 435, (1 - t) ** 2 * 140 + 2 * (1 - t) * t * 340 + t * t * 440))
    hs.append(poly(cone))
    hs.append(U([taper((304, 200), (330, 130), 36, 28), taper((330, 130), (366, 96), 28, 22), taper((366, 96), (408, 84), 22, 18)]))
    brim = rect(188, 426, 447, 454, 12)
    hs.append(brim)
    sc = U([circ(x, 460, 15) for x in range(206, 432, 28)])
    hs.append(sc)
    hh.append(outline_cut(U([sc, brim]), rect(258, 420, 377, 560), 14))
    hh.append(panes(lancet(286, 350, 500, 620), 318, 566, 15, True, False))
    hh.append(lancet(292, 344, 680, 790))
    # house openings: bat in the round gable window, two arched windows, door
    hh.append(panes(circ(595, 500, 36), 595, 500, 14))
    for wx in (500, 690):
        hh.append(panes(arch(wx - 36, wx + 36, 640, 752), wx, 700, 15))
    hh.append(arch(555, 635, 770, BY - 18).difference(rect(587, 760, 603, 900)))
    hh.append(line(wavy((452, 600), (738, 600), 7, 46), 15).difference(U(hs[1:4]).buffer(10)))
    solid.append(compose(hs, [], 6)); holes.append(U(hh))
    solid.append(bat(446, 64, 160, 6))
    solid.append(candy_cane(818, BY, 200, 24, 30))
    solid.append(candy_cane(872, BY, 150, 24, 26))
    return compose(solid, holes)


def d3_spiderweb_house():
    solid, holes = [], []
    solid.append(base_strip(90, 885, BY, 940))
    hs, hh, (l, p, r) = iced_house(310, 690, 600, 292, eave=62, band=52, style="scallops")
    hs.append(gumdrop(p[0], p[1] - 22, 27))
    hh.append(web_window(500, 500, 104, 8, (0.58,)))
    for wx in (385, 615):
        hh.append(panes(circ(wx, 716, 44), wx, 716, 16))
    hh.append(arch(455, 545, 740, BY - 18).difference(rect(492, 730, 508, 900)))
    solid.append(compose(hs, [], 6)); holes.append(U(hh))
    # spider dangling from the right eave
    solid.append(line([(790, 628), (790, 752)], 15))
    solid.append(spider(790, 790, 0.85))
    s, h = pumpkin(185, BY, 108, 80)
    solid.append(s); holes.append(h)
    return compose(solid, holes)


def d4_village_panel():
    G = 430
    solid, holes = [], []
    top = [(x, G - 6 * math.sin(x / 70) - 4 * math.sin(x / 23 + 1)) for x in range(0, 1001, 5)]
    solid.append(poly(top + [(1000, 488), (0, 488)]).buffer(-12).buffer(12, 16))
    # full moon with bats, behind the tall middle house
    solid.append(circ(318, 104, 88))
    holes.append(bat(290, 80, 72, -8))
    holes.append(bat(352, 128, 66, 10))
    # left: crooked little house
    hs, hh, (l, p, r) = iced_house(92, 232, 290, 196, gy=G, eave=22, band=30, n=3, dmin=14, dmax=34, dw=14, gap=14)
    hs.append(gumdrop(p[0], p[1] - 14, 16))
    hh.append(arch(142, 182, G - 74, G - 10))
    hh.append(panes(circ(162, 318, 25), 162, 318, 13))
    tf = lambda g: affinity.rotate(affinity.skew(g, xs=-5, origin=(162, G)), 1.5, origin=(162, G))
    solid.append(tf(compose(hs, [], 6))); holes.append(tf(U(hh)))
    # middle: tall house with a tower
    hs, hh, (l, p, r) = iced_house(420, 620, 250, 128, gy=G, eave=26, band=32, style="scallops", amp=9, period=34, gap=14)
    hs.append(gumdrop(p[0], p[1] - 14, 17))
    hh.append(arch(495, 545, G - 86, G - 10))
    for wx in (455, 585):
        hh.append(arch(wx - 18, wx + 18, 290, 345))
    hh.append(broken_heart(520, 212, 0.66))
    solid.append(compose(hs, [], 6)); holes.append(U(hh))
    # right: cottage with a chimney
    hs, hh, (l, p, r) = iced_house(760, 900, 300, 212, gy=G, eave=22, band=30, n=3, dmin=14, dmax=34, dw=14, gap=14, seed=5)
    hs += [rect(860, 200, 890, 270), rect(852, 192, 898, 210, 4)]
    hh.append(arch(808, 852, G - 76, G - 10))
    hh.append(panes(circ(830, 328, 24), 830, 328, 13))
    solid.append(compose(hs, [], 6)); holes.append(U(hh))
    solid.append(bat(915, 132, 92, 6))
    solid.append(smoke(875, 188, [(888, 168), (905, 150)], 9, 14))
    solid.append(dead_tree(318, G, 330, 26, seed=3, depth=2))
    solid.append(dead_tree(700, G, 260, 24, seed=4, depth=3, lean=6))
    for (x, w, h) in ((262, 46, 76), (968, 44, 70), (378, 40, 62)):
        s, hl = tombstone(x, G + 4, w, h)
        solid.append(s); holes.append(hl)
    return compose(solid, holes)


def d5_shingle_house():
    solid, holes = [], []
    solid.append(base_strip(110, 890, BY, 940))
    hs, hh, (l, p, r) = iced_house(330, 670, 620, 312, eave=56, band=50, n=5, seed=21, dmin=22, dmax=56)
    hh.append(panes(circ(500, 540, 44), 500, 540, 15))
    sk, skh = skull(500, p[1] - 64, 54)
    hs.append(sk); hh.append(skh)
    hs.append(roof_gumdrops(l, p, r, 50, (0.22, 0.5), 20))
    hh.append(coffin(500, 712, BY - 16, 112))
    for wx in (400, 600):
        hh.append(panes(lancet(wx - 32, wx + 32, 676, 812), wx, 750, 15, True, False))
    hh.append(line(wavy((350, 646), (650, 646), 7, 46), 16))
    solid.append(compose(hs, [], 6)); holes.append(U(hh))
    solid.append(iron_fence(150, 330, 742, BY))
    solid.append(iron_fence(670, 850, 742, BY))
    return compose(solid, holes)


def d6_ornament():
    solid, holes = [], []
    C, R = (500, 500), 466
    ring = circ(*C, R).difference(circ(*C, R - 32))
    solid.append(ring)
    solid.append(circ(500, 22, 44))
    holes.append(circ(500, 18, 22))
    ground = circ(*C, R - 10).intersection(rect(0, 800, 1000, 1000))
    gtop = [(x, 800 - 14 * math.sin((x - 60) / 120)) for x in range(20, 981, 5)]
    ground = circ(*C, R - 10).intersection(poly(gtop + [(980, 1000), (20, 1000)]))
    solid.append(ground)
    hs, hh, (l, p, r) = iced_house(390, 620, 570, 352, gy=800, eave=40, band=42, n=4, seed=8, dmin=20, dmax=52, dw=18)
    hs.append(gumdrop(p[0], p[1] - 18, 22))
    hs += [rect(548, 360, 592, 470), rect(538, 346, 602, 370, 5)]
    hh.append(arch(468, 542, 690, 798).difference(rect(497, 680, 513, 820)))
    for wx in (430, 582):
        hh.append(arch(wx - 24, wx + 24, 610, 676))
    tf = lambda g: affinity.rotate(affinity.skew(affinity.scale(affinity.translate(g, 0, 10), 1.28, 1.28, origin=(505, 810)),
                                                 xs=-4, origin=(505, 810)), 1.2, origin=(505, 810))
    solid.append(tf(compose(hs + [rect(390, 760, 620, 830)], [], 6))); holes.append(tf(U(hh)))
    solid.append(crescent(208, 272, 96, 34, 26, 0.84))
    solid.append(bat(785, 248, 165, 8))
    for x, w, hgt in ((238, 74, 122), (318, 58, 92), (790, 74, 122)):
        s, h = tombstone(x, 806, w, hgt)
        solid.append(s); holes.append(h)
    return compose(solid, holes)


DESIGNS = {
    "01-crooked-haunted-gingerbread-house": d1_crooked_house,
    "02-gingerbread-manor-with-witch-hat-tower": d2_turret_manor,
    "03-spiderweb-gingerbread-house": d3_spiderweb_house,
    "04-haunted-gingerbread-village": d4_village_panel,
    "05-skull-topped-gingerbread-house": d5_shingle_house,
    "06-haunted-gingerbread-ornament": d6_ornament,
}


README = """HAUNTED GINGERBREAD HOUSES - 6 SVG CUT FILES
by Duskwood Designs Co (etsy.com/shop/DuskwoodDesignsCo)
Thank you for your purchase!

DESIGNS
  Standing pieces:  01 Crooked Haunted Gingerbread House
                    02 Gingerbread Manor with Witch-Hat Tower
                    03 Spiderweb Gingerbread House
                    05 Skull-Topped Gingerbread House
  Wide panel:       04 Haunted Gingerbread Village
  Ornament:         06 Haunted Gingerbread Ornament

FILES
  SVG/  Cricut Design Space, Silhouette Designer Edition, Inkscape, Illustrator
  DXF/  Silhouette Studio Basic Edition, laser/CNC software (inches)
  PNG/  transparent background, 1800 px on the longest side (6 in at 300 DPI)

Each design is a single-layer shape with one clean cut path. Windows,
doors, piped icing, the spider web and the pumpkin face are cut-outs; the
bats, moon, chimney smoke and dangling spider are attached, so nothing
falls out. Default size is 6 inches on the longest side; resize freely,
but keep the proportions locked.

SIZING TIPS
  Standing pieces (01, 02, 03, 05): each sits on a flat base strip, so it
  stands up on its own when cut from 3 mm wood or acrylic, or from heavy
  cardstock (glue two layers together for extra stiffness). We recommend
  5 in tall or larger in wood or acrylic and 4 in or larger in cardstock.
  Panel (04): use it as a window decal, light-box or shadow-box front, or a
  mantel silhouette. It has small windows, so we recommend 10 in wide or
  larger for vinyl and cardstock and 12 in or larger for laser-cut wood.
  Ornament (06): cut from cardstock, wood or acrylic at 4 in or larger and
  hang it from the loop at the top.
  The narrowest material is about 0.08 in at 6 in. Do a test cut first on
  a new material. Put a battery tea light behind any of them for a glow.

LICENSE
  Personal use: unlimited.
  Small-business commercial use: you may sell finished physical products
  (ornaments, decals, signs, shirts, cards, etc.) made with these designs,
  up to 500 units per design.
  You may NOT resell, share or redistribute the digital files themselves,
  in original or modified form, or include them in other digital products.
"""


# ---------------------------------------------------------------- export
PANELS = ("04-haunted-gingerbread-village",)


def to_path(geom):
    polys = geom.geoms if geom.geom_type == "MultiPolygon" else [geom]
    d = []
    for p in polys:
        for r in [p.exterior, *p.interiors]:
            pts = list(r.coords)
            d.append("M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts[:-1]) + " Z")
    return " ".join(d)


def view_box(geom, square, pad=12):
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
