"""Generate spiderweb-snowflake SVG cut files.

Each design is built from centerlines, buffered to a fixed stroke width and
unioned into a single filled shape, so cutting machines see one clean outline
(no open strokes, no overlapping paths).
"""
import math, os, json
from shapely.geometry import LineString, Point, Polygon
from shapely.ops import unary_union
from shapely import affinity

OUT = os.path.join(os.path.dirname(__file__), "webflakes")
os.makedirs(OUT, exist_ok=True)
MIN_HOLE = 600.0  # fill holes too small to cut/weed cleanly
C = 500.0  # canvas centre (1000 x 1000 viewBox)


def polar(r, a):
    return (C + r * math.cos(a), C + r * math.sin(a))


def bezier(p0, p1, p2, n=24):
    return [((1-t)**2*p0[0] + 2*(1-t)*t*p1[0] + t*t*p2[0],
             (1-t)**2*p0[1] + 2*(1-t)*t*p1[1] + t*t*p2[1])
            for t in (i/n for i in range(n+1))]


def spider(x, y, s, rot=0):
    """Small spider silhouette centred at x,y with scale s."""
    parts = [Point(0, 0).buffer(1.0 * s).union(Point(0, -1.25 * s).buffer(0.6 * s))]
    for side in (-1, 1):
        for i, ang in enumerate((-50, -15, 15, 50)):
            a = math.radians(ang)
            kx, ky = side * 1.9 * s * math.cos(a), 1.9 * s * math.sin(a) - 0.3 * s
            fx, fy = side * 2.7 * s * math.cos(a * 1.4), ky + (1.3 * s if i > 1 else -1.1 * s)
            parts.append(LineString([(0, -0.3 * s), (kx, ky), (fx, fy)]).buffer(0.22 * s, cap_style=1, join_style=1))
    g = unary_union(parts)
    g = affinity.rotate(g, rot, origin=(0, 0))
    return affinity.translate(g, x, y)


def webflake(rings, sag, branches, tips, stroke, hub, spoke_len=440, ring_stroke=None, spider_at=None):
    lines, solids = [], [Point(C, C).buffer(hub)]
    ring_stroke = ring_stroke or stroke * 0.7
    for k in range(6):
        a = math.radians(-90 + 60 * k)
        b = a + math.radians(60)
        lines.append((LineString([(C, C), polar(spoke_len, a)]), stroke))
        # web rings sag inward between spokes
        for r in rings:
            p0, p2 = polar(r, a), polar(r, b)
            mid = polar(r * math.cos(math.radians(30)) * sag, (a + b) / 2)
            lines.append((LineString(bezier(p0, mid, p2)), ring_stroke))
        # snowflake branches: (radius along spoke, length, angle in degrees)
        for r, length, ang in branches:
            base = polar(r, a)
            for sgn in (-1, 1):
                d = a + sgn * math.radians(ang)
                lines.append((LineString([base, (base[0] + length * math.cos(d), base[1] + length * math.sin(d))]), stroke * 0.85))
        tx, ty = polar(spoke_len, a)
        if tips == "diamond":
            solids.append(affinity.rotate(Polygon([(tx, ty-22), (tx+13, ty), (tx, ty+22), (tx-13, ty)]), math.degrees(a) + 90, origin=(tx, ty)))
        elif tips == "dot":
            solids.append(Point(tx, ty).buffer(16))
        elif tips == "drop":
            # little dew drop
            solids.append(Point(tx, ty).buffer(14).union(
                affinity.rotate(Polygon([(tx-10, ty-8), (tx+10, ty-8), (tx, ty-34)]), math.degrees(a) + 90, origin=(tx, ty))))
    geoms = [ln.buffer(w / 2, cap_style=1, join_style=1) for ln, w in lines] + solids
    if spider_at:
        r, k, s = spider_at
        a = math.radians(-90 + 60 * k)
        sx, sy = polar(r, a)
        # thread from spoke tip down to spider
        geoms.append(LineString([polar(spoke_len, a), (sx, sy)]).buffer(stroke * 0.3))
        geoms.append(spider(sx, sy, s, rot=math.degrees(a) + 90))
    g = unary_union(geoms).simplify(0.4)
    polys = g.geoms if g.geom_type == "MultiPolygon" else [g]
    g = unary_union([Polygon(p.exterior, [i for i in p.interiors if Polygon(i).area >= MIN_HOLE]) for p in polys])
    return g


def to_path(geom):
    polys = geom.geoms if geom.geom_type == "MultiPolygon" else [geom]
    d = []
    for p in polys:
        for ring in [p.exterior, *p.interiors]:
            pts = list(ring.coords)
            d.append("M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts[:-1]) + " Z")
    return " ".join(d)


def bbox_viewbox(geom, pad=10):
    x0, y0, x1, y1 = geom.bounds
    return f"{x0-pad:.0f} {y0-pad:.0f} {x1-x0+2*pad:.0f} {y1-y0+2*pad:.0f}"


DESIGNS = {
    "01-classic-web": dict(rings=[110, 190, 270, 350], sag=0.92, branches=[(380, 55, 40)], tips="diamond", stroke=12, hub=34),
    "02-frost-weaver": dict(rings=[150, 270], sag=0.85, branches=[(200, 45, 45), (330, 50, 40), (405, 35, 45)], tips="dot", stroke=12, hub=40),
    "03-dew-drop": dict(rings=[100, 160, 220, 280, 340], sag=0.95, branches=[(380, 50, 30)], tips="drop", stroke=11, hub=30, ring_stroke=7),
    "04-wide-web": dict(rings=[160, 300], sag=0.78, branches=[(90, 45, 50), (225, 55, 42), (370, 60, 38)], tips="diamond", stroke=14, hub=46),
    "05-hanging-spider": dict(rings=[120, 210, 300], sag=0.9, branches=[(340, 60, 40)], tips="dot", stroke=12, hub=36, spoke_len=400, spider_at=(470, 3, 26)),
    "06-ice-lace": dict(rings=[90, 140, 190, 240, 290, 340], sag=0.97, branches=[(390, 45, 35)], tips="dot", stroke=10, hub=26, ring_stroke=6),
}

meta = {}
for name, params in DESIGNS.items():
    g = webflake(**params)
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{bbox_viewbox(g)}" width="6in" height="6in">'
           f'<path fill="#000" fill-rule="evenodd" d="{to_path(g)}"/></svg>')
    with open(os.path.join(OUT, f"{name}.svg"), "w") as f:
        f.write(svg)
    meta[name] = {"parts": 1 if g.geom_type == "Polygon" else len(g.geoms),
                  "holes": sum(len(p.interiors) for p in (g.geoms if g.geom_type == "MultiPolygon" else [g])),
                  "smallest_hole_area": round(min([Polygon(i).area for p in (g.geoms if g.geom_type == "MultiPolygon" else [g]) for i in p.interiors] or [0]), 1)}
print(json.dumps(meta, indent=1))
