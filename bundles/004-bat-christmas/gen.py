"""Generate Bat Christmas SVG/DXF cut files.

Every design is built from simple shapes (bat silhouettes, wings, hats, holly,
stars), unioned into ONE connected filled shape. Decorative cut-outs are
subtracted, holes smaller than MIN_HOLE are filled, and the result is exported
as a single evenodd <path> plus a DXF of closed polylines in inches.
"""
import math, os, json
from shapely.geometry import LineString, Point, Polygon, MultiPolygon, box
from shapely.ops import unary_union
from shapely import affinity
import ezdxf

HERE = os.path.dirname(os.path.abspath(__file__))
SVG_DIR = os.path.join(HERE, "bundle", "SVG")
DXF_DIR = os.path.join(HERE, "bundle", "DXF")
for d in (SVG_DIR, DXF_DIR):
    os.makedirs(d, exist_ok=True)
MIN_HOLE = 600.0
SIZE_IN = 6.0


def bez(p0, p1, p2, n=20):
    return [((1-t)**2*p0[0] + 2*(1-t)*t*p1[0] + t*t*p2[0],
             (1-t)**2*p0[1] + 2*(1-t)*t*p1[1] + t*t*p2[1])
            for t in (i/n for i in range(n+1))]


def scallop(a, b, depth):
    """Concave arc from a to b, bowing 'up' (negative y side, toward wing bone)."""
    mx, my = (a[0]+b[0])/2, (a[1]+b[1])/2
    dx, dy = b[0]-a[0], b[1]-a[1]
    L = math.hypot(dx, dy)
    nx, ny = dy/L, -dx/L  # normal
    if ny > 0:
        nx, ny = -nx, -ny
    return bez(a, (mx + nx*depth*L, my + ny*depth*L), b)


def wing_pts(spread=1.0):
    """Right wing outline in unit space (wing tip at x~1). y grows downward."""
    sh, wrist, tip = (0.09, 0.0), (0.46, -0.20), (1.0, -0.30*spread)
    fingers = [tip, (0.90, 0.10), (0.68, 0.26), (0.40, 0.29), (0.09, 0.22)]
    pts = bez(sh, (0.26, -0.16), wrist)[:-1] + bez(wrist, (0.74, -0.34), tip)[:-1]
    for a, b in zip(fingers, fingers[1:]):
        pts += scallop(a, b, 0.24)[:-1]
    pts.append(fingers[-1])
    return pts


def wing(side=1, spread=1.0):
    p = Polygon(wing_pts(spread)).buffer(0)
    return p if side > 0 else affinity.scale(p, -1, 1, origin=(0, 0))


def bat(cx, cy, s, eyes=False, rot=0, wings=True, ears=True, feet=False, eye_r=0.033):
    """Bat silhouette centred on the body, wingspan 2 s. Returns (solid, holes)."""
    parts = [affinity.scale(Point(0, 0.03).buffer(1), 0.125, 0.23, origin=(0, 0.03)),
             Point(0, -0.19).buffer(0.125)]
    if ears:
        for sd in (-1, 1):
            parts.append(Polygon([(sd*0.01, -0.25), (sd*0.13, -0.45), (sd*0.125, -0.17)]))
    if feet:
        for sd in (-1, 1):
            parts.append(LineString([(sd*0.035, 0.22), (sd*0.05, 0.31)]).buffer(0.025))
    if wings:
        parts += [wing(1), wing(-1)]
    g = unary_union(parts)
    holes = []
    if eyes:
        holes = [Point(sd*0.05, -0.19).buffer(eye_r) for sd in (-1, 1)]
    def place(x):
        x = affinity.scale(x, s, s, origin=(0, 0))
        x = affinity.rotate(x, rot, origin=(0, 0))
        return affinity.translate(x, cx, cy)
    return place(g), [place(h) for h in holes]


def star(cx, cy, r, ri=0.45, n=5, rot=-90):
    pts = []
    for i in range(2*n):
        a = math.radians(rot + i*180/n)
        rr = r if i % 2 == 0 else r*ri
        pts.append((cx + rr*math.cos(a), cy + rr*math.sin(a)))
    return Polygon(pts)


def holly_leaf(cx, cy, L, ang):
    """Elongated holly leaf with pointed spikes and concave bites, base at (cx,cy)."""
    W = 0.30*L
    xs = [0.22, 0.50, 0.76]
    spikes = [(L*x, -W*math.sin(math.pi*min(x, 0.92))**0.55) for x in xs]
    pts = [(0, 0), (L*0.06, -W*0.25)]
    chain = spikes + [(L, 0)]
    pts.append(chain[0])
    for p, q in zip(chain, chain[1:]):
        pts += _bite(p, q, 0.16*L)[1:]
    lower = [(x, -y) for x, y in pts[::-1]]
    poly = Polygon(pts + lower[1:-1]).buffer(0)
    poly = poly.union(LineString([(-L*0.1, 0), (L*0.1, 0)]).buffer(L*0.03))  # stem
    poly = affinity.rotate(poly, ang, origin=(0, 0))
    return affinity.translate(poly, cx, cy)


def _bite(a, b, depth):
    """Arc from a to b bowing toward the leaf midrib (y -> 0)."""
    mx, my = (a[0]+b[0])/2, (a[1]+b[1])/2
    return bez(a, (mx, my + depth), b, 12)


def finish(solids, holes=()):
    g = unary_union(solids)
    if holes:
        g = g.difference(unary_union(list(holes)))
    x0, y0, x1, y1 = g.bounds
    k = 1000.0 / max(x1-x0, y1-y0)  # normalise: longest side = 1000 units
    g = affinity.translate(affinity.scale(g, k, k, origin=(x0, y0)), -x0, -y0)
    g = g.buffer(1.5, join_style=1).buffer(-1.5, join_style=1).simplify(0.4)
    polys = g.geoms if g.geom_type == "MultiPolygon" else [g]
    polys = [p for p in polys if p.area > 50]
    g = unary_union([Polygon(p.exterior, [i for i in p.interiors if Polygon(i).area >= MIN_HOLE]) for p in polys])
    return g


def smile(cx, cy, s):
    """Small fanged grin cut-out under the eyes."""
    m = LineString(bez((-0.055, -0.135), (0, -0.095), (0.055, -0.135), 10)).buffer(0.013, cap_style=1)
    return affinity.translate(affinity.scale(m, s, s, origin=(0, 0)), cx, cy)


# ------------------------------------------------------------------ designs

def d_tree():
    solids, holes = [], []
    tiers = [(800, 330), (650, 265), (505, 200), (375, 140)]  # (y, scale)
    for y, s in tiers:
        for sd in (-1, 1):
            w = affinity.rotate(wing(sd), sd*30, origin=(0, 0))
            w = affinity.scale(w, s, s, origin=(0, 0))
            solids.append(affinity.translate(w, 500, y))
    solids.append(Polygon([(500, 300), (330, 820), (670, 820)]))
    solids.append(box(490, 280, 510, 340))
    solids.append(box(455, 780, 545, 965))  # trunk
    b, h = bat(500, 300, 140, eyes=True)
    solids.append(b); holes += h
    for x, y in [(500, 480), (430, 620), (570, 640), (370, 780), (500, 760), (630, 800)]:
        holes.append(Point(x, y).buffer(19))
    return finish(solids, holes)


def d_santa_hat():
    b, h = bat(0, 0, 1, eyes=True)
    solids, holes = [b], list(h) + [smile(0, 0, 1)]
    # floppy hat sitting on the head, tip falling to the right
    hat = Polygon(bez((-0.19, -0.29), (-0.10, -0.80), (0.42, -0.66), 24)
                  + bez((0.42, -0.66), (0.10, -0.55), (0.19, -0.29), 16)[1:])
    solids += [hat, box(-0.23, -0.34, 0.23, -0.25).buffer(0.035), Point(0.43, -0.64).buffer(0.08)]
    holes.append(LineString([(-0.11, -0.385), (0.11, -0.385)]).buffer(0.014, cap_style=1))
    sc = lambda x: affinity.scale(x, 500, 500, origin=(0, 0))
    return finish([sc(x) for x in solids], [sc(x) for x in holes])


def d_candy_cane():
    b, h = bat(0, 0, 1, eyes=True, feet=True)
    solids, holes = [b], list(h) + [smile(0, 0, 1)]
    # cane hooked over the right foot, shaft hanging down and slightly out
    r, w, x0, ytop = 0.085, 0.11, 0.05, 0.29
    cxh = x0 + r  # hook centre; hook passes over the foot
    arc = [(cxh + r*math.cos(math.radians(a)), ytop + r - r*math.sin(math.radians(a))) for a in range(180, -1, -6)]
    # arc goes from left end (x0, ytop+r) over the top to the right side, then shaft down
    line = LineString([(x0, ytop + r + 0.05)] + arc + [(cxh + r, ytop + 0.78)])
    solids.append(line.buffer(w/2, cap_style=1, join_style=1))
    shaft_x = cxh + r
    for i in range(6):
        yc = ytop + r + 0.08 + i*0.105
        band = Polygon([(shaft_x - w/2 + 0.02, yc + 0.02), (shaft_x + w/2 - 0.02, yc - 0.025),
                        (shaft_x + w/2 - 0.02, yc + 0.015), (shaft_x - w/2 + 0.02, yc + 0.06)])
        holes.append(band)
    sc = lambda x: affinity.scale(x, 500, 500, origin=(0, 0))
    return finish([sc(x) for x in solids], [sc(x) for x in holes])


def d_garland():
    """Two-bat repeatable strip: string ends sit at the same height so copies join."""
    solids, holes = [], []
    W, n = 1000, 2
    pts = []
    for i in range(n):
        x0, x1 = i*W/n, (i+1)*W/n
        pts += bez((x0, 60), ((x0+x1)/2, 250), (x1, 60), 30)[(1 if i else 0):]
    solids.append(LineString(pts).buffer(9, cap_style=1))
    for i in range(n):
        cx = (i+0.5)*W/n
        cy = 275
        solids.append(LineString([(cx, 150), (cx, cy - 0.28*200)]).buffer(7))
        b, h = bat(cx, cy, 200)
        solids.append(b)
    for i in range(n+1):
        x = min(max(i*W/n, 50), W-50)
        solids.append(star(x, 62, 55, 0.46))
        holes.append(Point(x, 66).buffer(17))  # hanging hole in each star
    return finish(solids, holes)


def d_holly():
    solids, holes = [], []
    C, R = 500, 410
    solids.append(Point(C, C).buffer(R + 10).difference(Point(C, C).buffer(R - 10)))
    nc = 6
    for i in range(nc):
        a = -90 + 360*i/nc
        x, y = C + R*math.cos(math.radians(a)), C + R*math.sin(math.radians(a))
        for sd in (-1, 1):
            # leaf runs along the ring, tilted slightly outward
            solids.append(holly_leaf(x, y, 170, a + sd*90 - sd*20))
        for k in range(3):
            t = math.radians(a + 90 + 120*k)
            solids.append(Point(x + 22*math.cos(t), y + 22*math.sin(t)).buffer(24))
    b, h = bat(C, C + 30, 390, eyes=True, eye_r=0.04)
    solids.append(b); holes += h + [smile(C, C + 30, 390)]
    return finish(solids, holes)


def d_topper():
    solids, holes = [], []
    solids.append(star(500, 400, 250, 0.48))
    holes.append(star(500, 412, 135, 0.48))
    for sd in (-1, 1):
        w = affinity.rotate(wing(sd), -sd*6, origin=(0, 0))
        w = affinity.scale(w, 360, 360, origin=(0, 0))
        solids.append(affinity.translate(w, 500 + sd*95, 430))
    # clip tab below the star with a slot to slide over a branch
    solids.append(box(462, 540, 538, 690).buffer(18))
    holes.append(box(484, 600, 516, 684).buffer(4))
    return finish(solids, holes)


DESIGNS = {
    "01-bat-wing-tree": d_tree,
    "02-santa-hat-bat": d_santa_hat,
    "03-candy-cane-bat": d_candy_cane,
    "04-bat-garland": d_garland,
    "05-holly-bat": d_holly,
    "06-bat-wing-star": d_topper,
}


def to_path(g):
    polys = g.geoms if g.geom_type == "MultiPolygon" else [g]
    d = []
    for p in polys:
        for ring in [p.exterior, *p.interiors]:
            pts = list(ring.coords)
            d.append("M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts[:-1]) + " Z")
    return " ".join(d)


def write(name, g):
    x0, y0, x1, y1 = g.bounds
    pad = 10
    w, h = x1-x0+2*pad, y1-y0+2*pad
    k = SIZE_IN / max(w, h)
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0-pad:.0f} {y0-pad:.0f} {w:.0f} {h:.0f}" '
           f'width="{w*k:.2f}in" height="{h*k:.2f}in"><path fill="#000" fill-rule="evenodd" d="{to_path(g)}"/></svg>')
    open(os.path.join(SVG_DIR, name + ".svg"), "w").write(svg)
    doc = ezdxf.new("R2010")
    doc.header["$INSUNITS"] = 1  # inches
    msp = doc.modelspace()
    kk = SIZE_IN / max(x1-x0, y1-y0)
    for p in (g.geoms if g.geom_type == "MultiPolygon" else [g]):
        for ring in [p.exterior, *p.interiors]:
            pts = [((x-x0)*kk, (y1-y)*kk) for x, y in list(ring.coords)[:-1]]
            msp.add_lwpolyline(pts, close=True)
    doc.saveas(os.path.join(DXF_DIR, name + ".dxf"))


if __name__ == "__main__":
    meta = {}
    for name, fn in DESIGNS.items():
        g = fn()
        write(name, g)
        polys = g.geoms if g.geom_type == "MultiPolygon" else [g]
        hole_areas = [Polygon(i).area for p in polys for i in p.interiors]
        meta[name] = {"parts": len(polys), "holes": len(hole_areas),
                      "smallest_hole": round(min(hole_areas or [0]), 1)}
    print(json.dumps(meta, indent=1))
