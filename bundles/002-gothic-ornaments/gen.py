"""Generate Gothic Christmas ornament SVG/DXF cut files.

Each ornament is built from shapely primitives: a solid silhouette (with a cap
and hanging loop) minus cut-out motifs. The result is ONE closed shape per
design; holes smaller than MIN_HOLE are filled so nothing is too tiny to weed.
Coordinates are SVG-style (y grows downward) on a ~1000 unit canvas.
"""
import math, os, json
import ezdxf
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union
from shapely import affinity

HERE = os.path.dirname(os.path.abspath(__file__))
SVG_DIR = os.path.join(HERE, "bundle", "SVG")
DXF_DIR = os.path.join(HERE, "bundle", "DXF")
for d in (SVG_DIR, DXF_DIR):
    os.makedirs(d, exist_ok=True)
MIN_HOLE = 600.0
SIZE_IN = 6.0


# ---------------------------------------------------------------- primitives
def bezier(p0, p1, p2, n=24):
    return [((1-t)**2*p0[0] + 2*(1-t)*t*p1[0] + t*t*p2[0],
             (1-t)**2*p0[1] + 2*(1-t)*t*p1[1] + t*t*p2[1])
            for t in (i/n for i in range(n+1))]


def star(cx, cy, R, r=None, n=5, rot=0):
    r = r if r is not None else R * 0.42
    pts = []
    for i in range(2 * n):
        a = math.radians(-90 + rot + i * 180 / n)
        rr = R if i % 2 == 0 else r
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return Polygon(pts)


def crescent(cx, cy, R, dx, dy, r2):
    return Point(cx, cy).buffer(R, 128).difference(Point(cx + dx, cy + dy).buffer(r2, 128))


def bat(cx, cy, w, rot=0):
    """Bat silhouette, width w, centred at cx,cy."""
    s = w / 2.0
    parts = []
    for side in (-1, 1):
        top = bezier((0.08, -0.12), (0.45, -0.52), (1.0, -0.30), 20)
        # scalloped trailing edge: tip -> 3 finger points -> body
        fingers = [(1.0, -0.30), (0.80, 0.02), (0.56, 0.08), (0.32, 0.16), (0.10, 0.26)]
        bottom = []
        for a, b in zip(fingers[:-1], fingers[1:]):
            mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2 - 0.13)
            bottom += bezier(a, mid, b, 12)[1:]
        pts = top + bottom
        parts.append(Polygon([(cx + side * x * s, cy + y * s) for x, y in pts]).buffer(0))
    body = affinity.scale(Point(cx, cy + 0.04 * s).buffer(1, 64), 0.13 * s, 0.25 * s)
    head = Point(cx, cy - 0.20 * s).buffer(0.12 * s, 64)
    ears = [Polygon([(cx + side * 0.03 * s, cy - 0.26 * s), (cx + side * 0.13 * s, cy - 0.42 * s),
                     (cx + side * 0.12 * s, cy - 0.20 * s)]) for side in (-1, 1)]
    g = unary_union(parts + [body, head] + ears)
    return affinity.rotate(g, rot, origin=(cx, cy))


def spider(x, y, s, rot=0):
    parts = [Point(0, 0).buffer(1.0 * s).union(Point(0, -1.25 * s).buffer(0.6 * s))]
    for side in (-1, 1):
        for i, ang in enumerate((-50, -15, 15, 50)):
            a = math.radians(ang)
            kx, ky = side * 1.9 * s * math.cos(a), 1.9 * s * math.sin(a) - 0.3 * s
            fx, fy = side * 2.7 * s * math.cos(a * 1.4), ky + (1.3 * s if i > 1 else -1.1 * s)
            parts.append(LineString([(0, -0.3 * s), (kx, ky), (fx, fy)]).buffer(0.24 * s, cap_style=1, join_style=1))
    g = affinity.rotate(unary_union(parts), rot, origin=(0, 0))
    return affinity.translate(g, x, y)


def lancet(cx, ybot, w, hrect):
    """Equilateral gothic (pointed) arch window, bottom at ybot."""
    ys = ybot - hrect
    rect = box(cx - w / 2, ys, cx + w / 2, ybot)
    arch = (Point(cx - w / 2, ys).buffer(w, 128)
            .intersection(Point(cx + w / 2, ys).buffer(w, 128))
            .intersection(box(cx - w, ys - 2 * w, cx + w, ys)))
    return rect.union(arch)


def quatrefoil(cx, cy, r, lobes=4, rot=45):
    lobe_r = r * 0.48
    g = [Point(cx, cy).buffer(r * 0.5)]
    for k in range(lobes):
        a = math.radians(rot + k * 360 / lobes - 90)
        g.append(Point(cx + (r - lobe_r) * math.cos(a), cy + (r - lobe_r) * math.sin(a)).buffer(lobe_r, 64))
    return unary_union(g)


def cap_and_loop(cx, ytop_body, cap_w=130, cap_h=62):
    """Ornament cap (with ridges) + hanging loop above y = ytop_body."""
    y1 = ytop_body + 25  # overlap into body
    y0 = ytop_body - cap_h
    cap = box(cx - cap_w / 2, y0, cx + cap_w / 2, y1).buffer(8, join_style=1)
    ridges = [box(cx + dx - 6, y0 + 14, cx + dx + 6, y0 + cap_h - 12).buffer(6) for dx in (-36, 0, 36)]
    cap = cap.difference(unary_union(ridges)) if cap_w >= 110 else cap
    loop = Point(cx, y0 - 30).buffer(50, 64).difference(Point(cx, y0 - 34).buffer(27, 64))
    return cap.union(loop)


def finish(g):
    g = g.buffer(0).simplify(0.3)
    polys = list(g.geoms) if g.geom_type == "MultiPolygon" else [g]
    polys = [p for p in polys if p.area > 50]  # drop crumbs
    return unary_union([Polygon(p.exterior, [i for i in p.interiors if Polygon(i).area >= MIN_HOLE]) for p in polys])


# ---------------------------------------------------------------- designs
def d01_moon_bauble():
    cx, cy, R = 500, 570, 380
    body = Point(cx, cy).buffer(R, 256)
    cuts = [crescent(420, 600, 215, 70, -55, 185),
            bat(650, 430, 210, rot=-10),
            star(680, 660, 50), star(740, 540, 28, rot=15), star(600, 800, 28, rot=-10),
            star(320, 330, 26), star(700, 790, 22, rot=20)]
    # dotted inner rim
    for k in range(36):
        a = math.radians(k * 10)
        cuts.append(Point(cx + (R - 34) * math.cos(a), cy + (R - 34) * math.sin(a)).buffer(15, 32))
    return body.difference(unary_union(cuts)).union(cap_and_loop(cx, cy - R))


def d02_web_bauble():
    cx, cy, R = 500, 570, 380
    rim = Point(cx, cy).buffer(R, 256).difference(Point(cx, cy).buffer(R - 30, 256))
    inner = Point(cx, cy).buffer(R - 15, 256)
    lines = []
    n = 10
    for k in range(n):
        a = math.radians(-90 + k * 360 / n)
        b = a + math.radians(360 / n)
        lines.append(LineString([(cx, cy), (cx + R * math.cos(a), cy + R * math.sin(a))]).buffer(8))
        for r in (95, 170, 245, 320):
            p0 = (cx + r * math.cos(a), cy + r * math.sin(a))
            p2 = (cx + r * math.cos(b), cy + r * math.sin(b))
            m = (cx + r * 0.84 * math.cos((a + b) / 2), cy + r * 0.84 * math.sin((a + b) / 2))
            lines.append(LineString(bezier(p0, m, p2)).buffer(6))
    web = unary_union(lines).intersection(inner)
    hub = Point(cx, cy).buffer(26)
    sx, sy = 640, 760
    thread = LineString([(sx, cy - R + 20), (sx, sy)]).buffer(5.5)
    sp = spider(sx, sy, 34)
    g = unary_union([rim, web, hub, thread, sp])
    return g.union(cap_and_loop(cx, cy - R))


def d03_coffin():
    cx = 500
    pts = [(cx - 120, 160), (cx + 120, 160), (cx + 230, 380), (cx + 120, 930), (cx - 120, 930), (cx - 230, 380)]
    body = Polygon(pts).buffer(-22, join_style=1).buffer(22, join_style=1)
    inset = Polygon(pts).buffer(-48, join_style=2)
    # dashed inner border: short slots along the inset outline
    cuts = []
    ring = inset.exterior
    L = ring.length
    nd = 32
    for k in range(nd):
        p0 = ring.interpolate(L * k / nd + 9)
        p1 = ring.interpolate(L * (k + 0.42) / nd + 9)
        cuts.append(LineString([p0, p1]).buffer(9, cap_style=1))
    cuts.append(bat(cx, 400, 290))
    cuts.append(crescent(cx, 640, 92, 34, -26, 80))
    cuts += [star(cx, 805, 40)]
    return body.difference(unary_union(cuts)).union(cap_and_loop(cx, 160, cap_w=110, cap_h=50))


def d04_gothic_window():
    cx = 500
    w, h = 520, 860
    d = ((h / 2) ** 2 - (w / 2) ** 2) / w  # vesica: R-d = w/2, R^2-d^2=(h/2)^2
    R = w / 2 + d
    cy = 560
    body = Point(cx - d, cy).buffer(R, 512).intersection(Point(cx + d, cy).buffer(R, 512))
    top = cy - h / 2
    cuts = [lancet(cx - 62, 690, 104, 150), lancet(cx + 62, 690, 104, 150),
            quatrefoil(cx, 362, 66),
            lancet(cx, 830, 58, 30),
            Point(cx - 70, 770).buffer(18), Point(cx + 70, 770).buffer(18)]
    # outer pointed-arch frame line made of two arcs (left and right) leaving solid bridges at top/bottom
    frame = (Point(cx - d, cy).buffer(R - 30, 512).intersection(Point(cx + d, cy).buffer(R - 30, 512))
             .difference(Point(cx - d, cy).buffer(R - 48, 512).intersection(Point(cx + d, cy).buffer(R - 48, 512))))
    frame = frame.difference(box(cx - 40, 0, cx + 40, 1200)).difference(box(0, 0, 1000, top + 190)) \
                 .difference(box(0, cy + h / 2 - 170, 1000, 1200))
    cuts.append(frame)
    return body.difference(unary_union(cuts)).union(cap_and_loop(cx, top + 30, cap_w=100, cap_h=50))


def d05_batwing_bauble():
    cx, cy, R = 500, 560, 250
    body = Point(cx, cy).buffer(R, 256)
    wings = bat(cx, cy - 10, 900).difference(Point(cx, cy).buffer(R - 40))
    ears = unary_union([Polygon([(cx + s * 120, cy - 200), (cx + s * 175, cy - 300), (cx + s * 200, cy - 150)]) .buffer(10, join_style=1)
                        for s in (-1, 1)])
    g = unary_union([body, wings, ears])
    cuts = [crescent(cx - 30, cy + 20, 140, 55, -40, 122), star(cx + 95, cy - 70, 42), star(cx + 120, cy + 90, 24, rot=12),
            star(cx - 330, cy - 70, 26), star(cx + 330, cy - 70, 26, rot=0)]
    return g.difference(unary_union(cuts)).union(cap_and_loop(cx, cy - R))


def d06_rose_window():
    cx, cy, R = 500, 570, 300
    spikes = [affinity.rotate(lancet(cx, cy - R + 40, 110, 40), k * 30, origin=(cx, cy)) for k in range(12)]
    body = unary_union([Point(cx, cy).buffer(R, 256)] + spikes)
    cuts = [quatrefoil(cx, cy, 72)]
    for k in range(8):
        cuts.append(affinity.rotate(lancet(cx, cy - 100, 66, 80), k * 45, origin=(cx, cy)))
    for k in range(12):
        cuts.append(affinity.rotate(lancet(cx, cy - 262, 40, 18), k * 30, origin=(cx, cy)))
    for k in range(8):
        cuts.append(affinity.rotate(Point(cx, cy - 215).buffer(17, 32), k * 45 + 22.5, origin=(cx, cy)))
    return body.difference(unary_union(cuts)).union(cap_and_loop(cx, cy - R - 85))


DESIGNS = {
    "01-moon-and-bat-bauble": d01_moon_bauble,
    "02-spiderweb-bauble": d02_web_bauble,
    "03-coffin-ornament": d03_coffin,
    "04-gothic-window-drop": d04_gothic_window,
    "05-bat-wing-bauble": d05_batwing_bauble,
    "06-rose-window-ornament": d06_rose_window,
}


# ---------------------------------------------------------------- export
def rings_of(g):
    polys = g.geoms if g.geom_type == "MultiPolygon" else [g]
    for p in polys:
        for r in [p.exterior, *p.interiors]:
            yield list(r.coords)


def square_viewbox(g, pad=12):
    x0, y0, x1, y1 = g.bounds
    s = max(x1 - x0, y1 - y0) + 2 * pad
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    return mx - s / 2, my - s / 2, s


def write_svg(g, path):
    vx, vy, s = square_viewbox(g)
    d = " ".join("M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts[:-1]) + " Z" for pts in rings_of(g))
    with open(path, "w") as f:
        f.write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vx:.1f} {vy:.1f} {s:.1f} {s:.1f}" '
                f'width="{SIZE_IN:g}in" height="{SIZE_IN:g}in"><path fill="#000" fill-rule="evenodd" d="{d}"/></svg>')


def write_dxf(g, path):
    vx, vy, s = square_viewbox(g)
    k = SIZE_IN / s
    doc = ezdxf.new("R2010", setup=False)
    doc.units = ezdxf.units.IN
    msp = doc.modelspace()
    for pts in rings_of(g):
        msp.add_lwpolyline([((x - vx) * k, (vy + s - y) * k) for x, y in pts[:-1]], close=True)
    doc.saveas(path)


def stats(g):
    polys = list(g.geoms) if g.geom_type == "MultiPolygon" else [g]
    holes = [Polygon(i).area for p in polys for i in p.interiors]
    opened = g.buffer(-5).buffer(5)  # features thinner than ~10 units vanish
    lost = g.difference(opened)
    lost_parts = [p for p in (lost.geoms if lost.geom_type == "MultiPolygon" else [lost]) if p.area > 60]
    return {"parts": len(polys), "holes": len(holes), "smallest_hole": round(min(holes or [0]), 1),
            "opened_parts": 1 if opened.geom_type == "Polygon" else len(opened.geoms),
            "thin_spots": len(lost_parts)}


if __name__ == "__main__":
    meta = {}
    for name, fn in DESIGNS.items():
        g = finish(fn())
        write_svg(g, os.path.join(SVG_DIR, name + ".svg"))
        write_dxf(g, os.path.join(DXF_DIR, name + ".dxf"))
        meta[name] = stats(g)
    print(json.dumps(meta, indent=1))
