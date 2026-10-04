"""Turn picture layers into colourable regions and place symbols inside them."""
import numpy as np
import shapely
from shapely.geometry import Polygon, MultiPolygon, GeometryCollection, box
from shapely.ops import unary_union, split, polylabel

from pictures import FRAME

MIN_SLIVER = 4.0      # pt^2; anything smaller is a numerical sliver and is merged away
BIG_AREA = 21000.0    # pt^2 per extra symbol in a large region


def explode(g):
    if g.is_empty:
        return []
    if isinstance(g, Polygon):
        return [g]
    if isinstance(g, (MultiPolygon, GeometryCollection)):
        out = []
        for p in g.geoms:
            out += explode(p)
        return out
    return []


def build_regions(layers, ink):
    ink_u = unary_union(ink) if ink else Polygon()
    covered = ink_u
    regions = []
    for layer in reversed(layers):
        geom = layer["geom"].intersection(FRAME)
        vis = geom.difference(covered)
        covered = unary_union([covered, geom])
        pieces = explode(vis)
        for cut in layer["cuts"]:
            nxt = []
            for p in pieces:
                nxt += explode(split(p, cut)) if p.intersects(cut) else [p]
            pieces = nxt
        for p in pieces:
            p = p.buffer(0)
            if p.area >= MIN_SLIVER:
                regions.append({"poly": p, "color": layer["color"]})
    regions.reverse()  # painter's order again, bottom first
    for i, r in enumerate(regions):
        r["id"] = i
    return regions, ink_u


def n_symbols(poly):
    return int(min(3, 1 + poly.area // BIG_AREA))


def place(poly, obstacles, bw, bh, count):
    """Find up to `count` centres where a bw x bh box fits inside poly, away from obstacles.

    Returns list of (cx, cy). Deterministic: grid search, best clearance first.
    """
    avail = poly.difference(obstacles) if not obstacles.is_empty else poly
    minx, miny, maxx, maxy = avail.bounds
    step = 2.0
    xs, ys = np.meshgrid(np.arange(minx, maxx, step), np.arange(miny, maxy, step))
    xs, ys = xs.ravel(), ys.ravel()
    inside = shapely.contains_xy(avail, xs, ys)
    xs, ys = xs[inside], ys[inside]
    if len(xs) == 0:
        return []
    pts = shapely.points(xs, ys)
    d = shapely.distance(avail.boundary, pts)
    order = np.argsort(-d, kind="stable")
    chosen = []
    min_sep = max(bw, bh) * 2.4
    for idx in order:
        cx, cy = float(xs[idx]), float(ys[idx])
        if any((cx - a) ** 2 + (cy - b) ** 2 < min_sep ** 2 for a, b in chosen):
            continue
        b = box(cx - bw / 2, cy - bh / 2, cx + bw / 2, cy + bh / 2)
        if b.within(avail):
            chosen.append((cx, cy))
            if len(chosen) >= count:
                break
    return chosen
