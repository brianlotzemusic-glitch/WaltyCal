"""Generate the Skull Holiday SVG cut-file bundle.

Every design is built from shapely primitives and unioned into ONE closed,
connected shape. Details (hat bands, holly veins, candy stripes...) are cut as
closed slits that stay inside the silhouette, so pieces never fall apart.
Holes smaller than MIN_HOLE are filled so nothing is too tiny to weed.
Outputs bundle/SVG/*.svg (6in) and bundle/DXF/*.dxf (inches).
"""
import math, os, json
from shapely.geometry import LineString, Point, Polygon, MultiPolygon, box
from shapely.ops import unary_union
from shapely import affinity
import ezdxf

HERE = os.path.dirname(os.path.abspath(__file__))
SVG_DIR = os.path.join(HERE, "bundle", "SVG")
DXF_DIR = os.path.join(HERE, "bundle", "DXF")
os.makedirs(SVG_DIR, exist_ok=True); os.makedirs(DXF_DIR, exist_ok=True)
MIN_HOLE = 600.0
GAP = 11       # width of detail slits
MARGIN = 16    # slits stop this far from any edge


def ellipse(cx, cy, rx, ry, rot=0):
    e = affinity.scale(Point(0, 0).buffer(1, 64), rx, ry)
    return affinity.translate(affinity.rotate(e, rot, origin=(0, 0)), cx, cy)


def rrect(x0, y0, x1, y1, r):
    return box(x0 + r, y0 + r, x1 - r, y1 - r).buffer(r, 32)


def bezier(pts, n=60):
    """Cubic/quadratic bezier from 3 or 4 control points."""
    out = []
    for i in range(n + 1):
        t = i / n
        if len(pts) == 3:
            p0, p1, p2 = pts
            out.append(((1-t)**2*p0[0] + 2*(1-t)*t*p1[0] + t*t*p2[0],
                        (1-t)**2*p0[1] + 2*(1-t)*t*p1[1] + t*t*p2[1]))
        else:
            p0, p1, p2, p3 = pts
            a, b, c, d = (1-t)**3, 3*(1-t)**2*t, 3*(1-t)*t*t, t**3
            out.append((a*p0[0]+b*p1[0]+c*p2[0]+d*p3[0], a*p0[1]+b*p1[1]+c*p2[1]+d*p3[1]))
    return out


def line(pts, w, cap=1):
    return LineString(pts).buffer(w / 2, 32, cap_style=cap, join_style=1)


def nparts(g):
    return len(g.geoms) if g.geom_type == "MultiPolygon" else 1


def solid(g):
    return unary_union([Polygon(p.exterior) for p in (g.geoms if g.geom_type == "MultiPolygon" else [g])])


def bridge_slit(slit, center, n, w=16, phase=45):
    cx, cy = center
    bars = [line([(cx, cy), (cx + 2000*math.cos(math.radians(phase + 360*k/n)),
                             cy + 2000*math.sin(math.radians(phase + 360*k/n)))], w, cap=2) for k in range(n)]
    return slit.difference(unary_union(bars))


def on_top(base, top, gap=GAP, margin=MARGIN, bridges=4, phase=45):
    """Place `top` over `base`, separated by a slit that never reaches the outer edge.
    If the slit would fully enclose `top`, bridges keep it attached."""
    ring = solid(top).buffer(gap, 32).difference(solid(top))
    slit = ring.intersection(base.buffer(-margin, 32))
    res = unary_union([base.difference(slit).difference(solid(top)), top])
    if nparts(res) > nparts(unary_union([base, top])):
        c = solid(top).centroid
        slit = bridge_slit(slit, (c.x, c.y), bridges, phase=phase)
        res = unary_union([base.difference(slit).difference(solid(top)), top])
    return res


def cut(shape, holes, margin=MARGIN):
    """Cut holes, clipped so they stay inside the shape."""
    return shape.difference(unary_union(holes).intersection(shape.buffer(-margin, 32)))


def star(cx, cy, R, r, n=5, rot=-90):
    pts = []
    for i in range(2 * n):
        a = math.radians(rot + i * 180 / n)
        rr = R if i % 2 == 0 else r
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return Polygon(pts)


def heart(cx, cy, s, flip=True):
    """Small heart (upside-down by default, used as a cute nose)."""
    h = unary_union([Point(-0.5, 0).buffer(0.55, 32), Point(0.5, 0).buffer(0.55, 32),
                     Polygon([(-1.02, 0.2), (1.02, 0.2), (0, 1.35)])])
    h = affinity.scale(h, s, -s if flip else s, origin=(0, 0))
    return affinity.translate(h, cx, cy)


def fuzzy(cx, cy, r, bumps=11, br=None):
    br = br or r * 0.32
    parts = [Point(cx, cy).buffer(r, 48)]
    for i in range(bumps):
        a = 2 * math.pi * i / bumps
        parts.append(Point(cx + r * math.cos(a), cy + r * math.sin(a)).buffer(br, 24))
    return unary_union(parts)


def skull(cx, cy, s=1.0, face=True, eye_tilt=8):
    """Friendly skull: round cranium, short jaw, big oval eyes, heart nose, 4 teeth.
    (cx, cy) is the cranium centre; total height ~ 420*s."""
    cran = ellipse(cx, cy, 190*s, 178*s)
    jaw = rrect(cx - 112*s, cy + 60*s, cx + 112*s, cy + 238*s, 52*s)
    body = unary_union([cran, jaw])
    # cheek notches give the classic skull silhouette
    for sx in (-1, 1):
        body = body.difference(Point(cx + sx*168*s, cy + 196*s).buffer(62*s, 32))
    body = body.buffer(6*s, 32).buffer(-6*s, 32)
    if not face:
        return body, []
    holes = [ellipse(cx - 76*s, cy + 22*s, 50*s, 58*s, eye_tilt),
             ellipse(cx + 76*s, cy + 22*s, 50*s, 58*s, -eye_tilt),
             heart(cx, cy + 108*s, 34*s)]
    tw, tg = 26*s, 13*s
    x = cx - (4*tw + 3*tg) / 2
    for i in range(4):
        holes.append(rrect(x, cy + 168*s, x + tw, cy + 216*s, 8*s))
        x += tw + tg
    return body, holes


def with_face(shape, holes):
    return shape.difference(unary_union(holes))


def holly_leaf(cx, cy, L, W, rot):
    """Holly leaf along +x from its stem at (cx,cy): a pointed lens with round
    bites taken out of each edge, leaving sharp spikes between them."""
    h = W / 2
    R = ((L/2)**2 + h**2) / (2*h)
    leaf = Point(L/2, h - R).buffer(R, 128).intersection(Point(L/2, R - h).buffer(R, 128))
    bites = []
    n = 4
    for i in range(n):
        x = L * (0.13 + 0.74 * i / (n - 1))
        yy = math.sqrt(max(0.0, R*R - (x - L/2)**2)) - (R - h)
        r = L * 0.12
        for sg in (-1, 1):
            bites.append(Point(x, sg*(yy + r*0.5)).buffer(r, 32))
    leaf = leaf.difference(unary_union(bites))
    leaf = leaf.union(line([(-16, 0), (12, 0)], 14))
    leaf = leaf.difference(line([(L*0.12, 0), (L*0.8, 0)], 10))
    leaf = affinity.rotate(leaf, rot, origin=(0, 0))
    return affinity.translate(leaf, cx, cy)


def candy_cane(base, top, hook_dir, w=60, stripe=20, R=70):
    """Candy cane: straight stick base->top, then a hook curling toward hook_dir (+1/-1)."""
    bx, by = base; tx, ty = top
    dx, dy = tx - bx, ty - by
    ln = math.hypot(dx, dy); ux, uy = dx/ln, dy/ln
    nx, ny = -uy * hook_dir, ux * hook_dir   # perpendicular, toward hook side
    cxh, cyh = tx + nx*R, ty + ny*R
    a0 = math.atan2(ty - cyh, tx - cxh)
    arc = [(cxh + R*math.cos(a0 + hook_dir*(-1)*k*math.pi/40 * -1 * -1), 0) for k in range(0)]
    arc = []
    # sweep 200 degrees through the "top" side
    sweep = math.radians(200)
    # direction of sweep: go from the stick top, over the top, down the other side
    # choose sign so the first step moves along +u (continuing upward)
    for sgn in (1, -1):
        a1 = a0 + sgn * 0.05
        p = (cxh + R*math.cos(a1), cyh + R*math.sin(a1))
        if (p[0]-tx)*ux + (p[1]-ty)*uy > 0:
            break
    for k in range(41):
        a = a0 + sgn * sweep * k / 40
        arc.append((cxh + R*math.cos(a), cyh + R*math.sin(a)))
    center = [(bx, by)] + arc
    cane = line(center, w)
    # diagonal stripes as holes along the path
    path = LineString(center)
    stripes = []
    d = 30.0
    while d < path.length - 20:
        p = path.interpolate(d); q = path.interpolate(d + 1)
        tx2, ty2 = q.x - p.x, q.y - p.y
        tl = math.hypot(tx2, ty2); tx2, ty2 = tx2/tl, ty2/tl
        # stripe direction: perpendicular rotated 35 degrees
        ang = math.atan2(ty2, tx2) + math.radians(90 - 35)
        ex, ey = math.cos(ang) * w, math.sin(ang) * w
        stripes.append(line([(p.x - ex, p.y - ey), (p.x + ex, p.y + ey)], stripe, cap=2))
        d += 62
    return cut(cane, stripes, margin=10), cane


def snowflake_hole(cx, cy, R, w=14):
    parts = [Point(cx, cy).buffer(w*1.1, 24)]
    for k in range(6):
        a = math.radians(-90 + 60*k)
        ex, ey = cx + R*math.cos(a), cy + R*math.sin(a)
        parts.append(line([(cx, cy), (ex, ey)], w))
        bx, by = cx + 0.6*R*math.cos(a), cy + 0.6*R*math.sin(a)
        for sg in (-1, 1):
            b = a + sg*math.radians(45)
            parts.append(line([(bx, by), (bx + 0.35*R*math.cos(b), by + 0.35*R*math.sin(b))], w*0.85))
    return unary_union(parts)


# ---------------------------------------------------------------- designs
def d_santa_hat():
    sk, face = skull(500, 600, 1.0)
    g = with_face(sk, face)
    # floppy hat: tapered body following a curve that droops to the right
    spine = bezier([(500, 455), (480, 250), (640, 140), (770, 300)], 80)
    circles = []
    for i, (x, y) in enumerate(spine):
        t = i / (len(spine) - 1)
        circles.append(Point(x, y).buffer(205 * (1 - t) ** 1.15 + 18, 32))
    hat = unary_union(circles).intersection(box(0, 0, 1000, 470))
    g = on_top(g, hat)
    band = rrect(282, 415, 718, 505, 44)
    bumps = [Point(x, y).buffer(26, 24) for x in range(300, 701, 50) for y in (418, 502)]
    band = unary_union([band] + bumps)
    g = on_top(g, band)
    g = on_top(g, fuzzy(770, 318, 52, 10))
    return g


def d_holly_crown():
    cx, cy = 500, 640
    sk, face = skull(cx, cy, 1.0)
    g = with_face(sk, face)
    # big holly sprig on top of the head: two leaves in a wide V plus three berries
    hx, hy = 500, 462
    for ang in (-152, -28):
        a = math.radians(ang)
        g = on_top(g, holly_leaf(hx + 30*math.cos(a), hy + 30*math.sin(a), 225, 100, ang), gap=11, margin=9)
    for bx, by in ((466, 492), (534, 492), (500, 440)):
        berry = Point(bx, by).buffer(32, 32).difference(Point(bx - 6, by - 6).buffer(14.5, 24))
        g = on_top(g, berry, gap=10, margin=7)
    return g


def d_candy_crossbones():
    c1, _ = candy_cane((250, 960), (720, 300), +1, w=72, stripe=22)
    c2, _ = candy_cane((750, 960), (280, 300), -1, w=72, stripe=22)
    g = on_top(c1, c2, gap=10, margin=8)
    sk, face = skull(500, 470, 0.92)
    g = on_top(g, sk, gap=12, margin=10)
    g = g.difference(unary_union(face))
    return g


def d_ornament():
    cx, cy = 500, 610
    sk, face = skull(cx, cy, 1.0)
    g = with_face(sk, face)
    # festive band following the cranium curve: two arcs with a row of diamonds
    def arc(r, a0=-142, a1=-38):
        return LineString([(cx + r*math.cos(math.radians(t)), cy + r*math.sin(math.radians(t)))
                           for t in range(a0, a1 + 1, 2)])
    holes = [arc(100).buffer(6, 16)]
    for t in (-136, -113, -90, -67, -44):
        x, y = cx + 138*math.cos(math.radians(t)), cy + 134*math.sin(math.radians(t))
        holes.append(affinity.rotate(box(x-14, y-14, x+14, y+14), 45, origin=(x, y)))
    g = cut(g, holes, margin=12)
    cap = rrect(432, 385, 568, 455, 14)
    cap = cut(cap, [line([(x, 400), (x, 440)], 14) for x in (466, 500, 534)], margin=6)
    g = on_top(g, cap)
    loop = Point(500, 340).buffer(56, 48).difference(Point(500, 340).buffer(36, 48))
    g = unary_union([g, loop])
    # bow-tie ribbon knotted at the top of the loop
    bow = unary_union([Polygon([(500, 270), (500 + sg*125, 222), (500 + sg*112, 268), (500 + sg*125, 318)]).buffer(16, 16)
                       for sg in (-1, 1)] + [ellipse(500, 270, 28, 32)])
    inner = [Polygon([(500 + sg*48, 268), (500 + sg*112, 240), (500 + sg*104, 268), (500 + sg*112, 298)]) for sg in (-1, 1)]
    bow = cut(bow, inner, margin=8)
    g = on_top(g, bow, gap=10, margin=8)
    return g


def d_beanie():
    cx, cy = 500, 655
    sk, face = skull(cx, cy, 1.0)
    g = with_face(sk, face)
    dome = ellipse(500, 540, 212, 250).intersection(box(0, 0, 1000, 540))
    dome = cut(dome, [snowflake_hole(500, 410, 88, 15)], margin=10)
    g = on_top(g, dome)
    cuff = rrect(272, 505, 728, 598, 34)
    ribs = [line([(x, 528), (x, 575)], 13) for x in range(314, 700, 34)]
    cuff = cut(cuff, ribs, margin=10)
    g = on_top(g, cuff)
    g = on_top(g, fuzzy(500, 282, 62, 12, 22), gap=10, margin=10)
    return g


def d_star_topper():
    st = star(500, 440, 450, 205).buffer(-22, 32).buffer(30, 32)
    inner = star(500, 452, 360, 168).buffer(-10, 16).buffer(10, 16)
    slit = inner.exterior.buffer(GAP / 2, 16).intersection(st.buffer(-MARGIN))
    slit = bridge_slit(slit, (500, 452), 5, w=18, phase=-90 + 36)
    g = st.difference(slit)
    sk, face = skull(500, 430, 0.72, eye_tilt=10)
    g = on_top(g, sk, gap=12, margin=8, bridges=5, phase=-90 + 36)
    g = g.difference(unary_union(face))
    # sleeve that slides over the tree tip, with coil slits
    sleeve = Polygon([(448, 640), (552, 640), (575, 975), (425, 975)]).buffer(10, 16)
    coils = [line([(440, y), (560, y + 14)], 12) for y in range(810, 960, 40)]
    g = cut(unary_union([g, sleeve]), coils, margin=10)
    return g


DESIGNS = {
    "01-santa-hat-skull": d_santa_hat,
    "02-holly-sprig-skull": d_holly_crown,
    "03-candy-cane-crossbones": d_candy_crossbones,
    "04-skull-ornament": d_ornament,
    "05-snowflake-beanie-skull": d_beanie,
    "06-star-topper-skull": d_star_topper,
}


def clean(g):
    g = g.buffer(-1.5, 16).buffer(1.5, 16)          # drop hairline slivers
    g = g.simplify(0.4)
    polys = list(g.geoms) if g.geom_type == "MultiPolygon" else [g]
    polys = [p for p in polys if p.area > 50]
    return unary_union([Polygon(p.exterior, [i for i in p.interiors if Polygon(i).area >= MIN_HOLE]) for p in polys])


def polys_of(g):
    return list(g.geoms) if g.geom_type == "MultiPolygon" else [g]


def to_path(g):
    d = []
    for p in polys_of(g):
        for ring in [p.exterior, *p.interiors]:
            pts = list(ring.coords)
            d.append("M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts[:-1]) + " Z")
    return " ".join(d)


def write(name, g):
    x0, y0, x1, y1 = g.bounds
    side = max(x1 - x0, y1 - y0) + 20
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    vb = f"{cx - side/2:.1f} {cy - side/2:.1f} {side:.1f} {side:.1f}"
    with open(os.path.join(SVG_DIR, name + ".svg"), "w") as f:
        f.write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" width="6in" height="6in">'
                f'<path fill="#000" fill-rule="evenodd" d="{to_path(g)}"/></svg>')
    # DXF in inches, longest side 6in, y flipped
    k = 6.0 / max(x1 - x0, y1 - y0)
    doc = ezdxf.new("R2010"); doc.units = ezdxf.units.IN
    msp = doc.modelspace()
    for p in polys_of(g):
        for ring in [p.exterior, *p.interiors]:
            pts = [((x - x0) * k, (y1 - y) * k) for x, y in list(ring.coords)[:-1]]
            msp.add_lwpolyline(pts, close=True)
    doc.saveas(os.path.join(DXF_DIR, name + ".dxf"))


if __name__ == "__main__":
    meta = {}
    for name, fn in DESIGNS.items():
        g = clean(fn())
        write(name, g)
        ps = polys_of(g)
        holes = [Polygon(i).area for p in ps for i in p.interiors]
        meta[name] = {"parts": len(ps), "holes": len(holes),
                      "smallest_hole": round(min(holes or [0]), 1),
                      "bbox": [round(v) for v in g.bounds]}
    print(json.dumps(meta, indent=1))
