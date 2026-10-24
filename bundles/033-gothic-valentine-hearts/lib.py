"""Shared helpers: splines, shapes, finishing, export (derived from bundle 031 gen.py)."""
import math, os, json, sys
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union
from shapely import affinity, make_valid, set_precision
U = unary_union
MIN_HOLE = 600.0


def spline(pts, closed=True, n=14, tension=1.0):
    """Hermite spline through pts. A point given as (x, y, 'c') is a sharp corner."""
    P = [(p[0], p[1]) for p in pts]
    C = [len(p) > 2 for p in pts]
    m = len(P)
    out = []
    rng = range(m) if closed else range(m - 1)
    def tan(i, side):
        if not closed and (i == 0 or i == m - 1):
            j = 1 if i == 0 else m - 2
            return None
        if C[i % m]:
            return None
        a, b = P[(i - 1) % m], P[(i + 1) % m]
        return ((b[0] - a[0]) * 0.5 * tension, (b[1] - a[1]) * 0.5 * tension)
    for i in rng:
        p0, p1 = P[i], P[(i + 1) % m]
        t0, t1 = tan(i, 1), tan(i + 1, 0)
        d = (p1[0] - p0[0], p1[1] - p0[1])
        if t0 is None: t0 = (d[0] * 0.5, d[1] * 0.5) if True else None
        if t1 is None: t1 = (d[0] * 0.5, d[1] * 0.5)
        for k in range(n):
            t = k / n
            h00, h10, h01, h11 = 2*t**3-3*t**2+1, t**3-2*t**2+t, -2*t**3+3*t**2, t**3-t**2
            out.append((h00*p0[0]+h10*t0[0]+h01*p1[0]+h11*t1[0], h00*p0[1]+h10*t0[1]+h01*p1[1]+h11*t1[1]))
    if not closed:
        out.append(P[-1])
    return out


def shape(pts, **kw):
    return Polygon(spline(pts, **kw)).buffer(0)


def line(pts, w, smooth=False):
    if smooth:
        pts = spline(pts, closed=False)
    return LineString(pts).buffer(w / 2, cap_style=1, join_style=1, quad_segs=12)


def taper(p0, p1, w0, w1):
    (x0, y0), (x1, y1) = p0, p1
    L = math.hypot(x1 - x0, y1 - y0)
    nx, ny = -(y1 - y0) / L, (x1 - x0) / L
    body = Polygon([(x0 + nx*w0/2, y0 + ny*w0/2), (x1 + nx*w1/2, y1 + ny*w1/2),
                    (x1 - nx*w1/2, y1 - ny*w1/2), (x0 - nx*w0/2, y0 - ny*w0/2)])
    return U([body, Point(x0, y0).buffer(w0/2, 24), Point(x1, y1).buffer(w1/2, 24)])


def curve_taper(pts, w0, w1, n=40):
    """Tapering stroke along a spline through pts."""
    sp = spline(pts, closed=False, n=12)
    N = len(sp)
    parts = []
    for i in range(N - 1):
        t = i / (N - 2)
        parts.append(taper(sp[i], sp[i+1], w0 + (w1 - w0) * t, w0 + (w1 - w0) * (t + 1.0/(N-1))))
    return U(parts)


def circ(x, y, r):
    return Point(x, y).buffer(r, 48)


def ellipse(cx, cy, rx, ry, rot=0):
    e = affinity.scale(Point(0, 0).buffer(1, 48), rx, ry)
    return affinity.translate(affinity.rotate(e, rot, origin=(0, 0)), cx, cy)


def polar(x, y, r, deg):
    a = math.radians(deg)
    return x + r*math.cos(a), y + r*math.sin(a)


def place(g, x, y, s=1.0, rot=0, flip=False):
    if flip:
        g = affinity.scale(g, -1, 1, origin=(0, 0))
    g = affinity.scale(g, s, s, origin=(0, 0))
    g = affinity.rotate(g, rot, origin=(0, 0))
    return affinity.translate(g, x, y)


def areal(g):
    if g.geom_type in ("Polygon", "MultiPolygon"):
        return g
    return U([p for p in getattr(g, "geoms", []) if p.geom_type in ("Polygon", "MultiPolygon")])


MIN_TIP = 6.3   # units; rounding radius => tips/slits no narrower than 2*6.3 = 12.6 units = 0.083 in at 6 in


def finish(g, r=MIN_TIP, simplify=0.15):
    g = areal(make_valid(g))
    g = g.buffer(r, quad_segs=16).buffer(-r, quad_segs=16)       # fill pinches / round slit ends (>= 0.08 in)
    g = g.buffer(-r, quad_segs=16).buffer(r, quad_segs=16)       # round tips to >= 0.08 in, drop slivers
    g = areal(set_precision(areal(make_valid(g.simplify(simplify))), 0.05))
    polys = list(g.geoms) if g.geom_type == "MultiPolygon" else [g]
    polys = [p for p in polys if p.area > 1500]
    polys = [Polygon(p.exterior, [i for i in p.interiors if Polygon(i).area >= MIN_HOLE + 30]) for p in polys]
    return U(polys)


def to_path(geom):
    polys = geom.geoms if geom.geom_type == "MultiPolygon" else [geom]
    d = []
    for p in polys:
        for r in [p.exterior, *p.interiors]:
            pts = list(r.coords)
            d.append("M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts[:-1]) + " Z")
    return " ".join(d)


def view_box(geom, pad=4):
    x0, y0, x1, y1 = geom.bounds
    w, h = x1 - x0 + 2*pad, y1 - y0 + 2*pad
    w = h = max(w, h)
    return (x0 + x1)/2 - w/2, (y0 + y1)/2 - h/2, w, h


def stats(g):
    polys = list(g.geoms) if g.geom_type == "MultiPolygon" else [g]
    hs = [Polygon(i).area for p in polys for i in p.interiors]
    return {"parts": len(polys), "holes": len(hs), "smallest_hole": round(min(hs or [0]), 1), "valid": g.is_valid}


def fit(g, size=900, cx=500, cy=500):
    x0, y0, x1, y1 = g.bounds
    s = size / max(x1 - x0, y1 - y0)
    g = affinity.scale(g, s, s, origin=(0, 0))
    x0, y0, x1, y1 = g.bounds
    return affinity.translate(g, cx - (x0 + x1) / 2, cy - (y0 + y1) / 2)
