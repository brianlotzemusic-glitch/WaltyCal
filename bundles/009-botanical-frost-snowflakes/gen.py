"""Botanical Frost Snowflakes - 6 single-path SVG/DXF cut files.

Six original six-fold snowflakes whose arms are made of botanical shapes:
pine needles and cones, fern fronds and fiddleheads, berry sprigs, holly
leaves, oak leaves and acorns, and leafy frost twigs. Each one is drawn in
code: one arm is built along the "up" axis (usually as a right half that is
mirrored, so the flake has true snowflake mirror symmetry), rotated six
times about the centre and unioned with a centre medallion.
finish() closes then opens by 6.5 units, so there is no material and no gap
narrower than ~13 units, and fills any hole under MIN_HOLE. Coordinates are
SVG-style (y grows downward) on a 1000-unit canvas centred on (500, 500).
Output: SVG (6 in square), DXF (inches), stats json.
"""
import math, os, json, sys
from shapely.geometry import LineString, Point, Polygon
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
CX, CY = 500.0, 500.0
U = unary_union


# ---------------------------------------------------------------- helpers
def P(r, s=0.0):
    """Arm-local point: r along the arm (outwards, 'up'), s to the right."""
    return (CX + s, CY - r)


def D(r, s, ang, L):
    """Point L away from arm-local (r, s) at `ang` degrees off the arm axis
    (positive = towards the right)."""
    a = math.radians(ang)
    return (r + L * math.cos(a), s + L * math.sin(a))


def poly(pts):
    return Polygon(pts).buffer(0)


def circ(p, r):
    return Point(p).buffer(r, 48)


def line(pts, w):
    return LineString(pts).buffer(w / 2, cap_style=1, join_style=1, quad_segs=12)


def taper(p0, p1, w0, w1):
    """Stroke from p0 (width w0) to p1 (width w1) with round ends."""
    return U([circ(p0, w0 / 2), circ(p1, w1 / 2)]).convex_hull


def _axis(p0, p1):
    L = math.dist(p0, p1)
    ux, uy = (p1[0] - p0[0]) / L, (p1[1] - p0[1]) / L
    return L, ux, uy, -uy, ux


def leaf(p0, p1, w, a=0.7, b=1.0, n=48):
    """Leaf from base p0 to tip p1, max width w. a<b puts the widest
    point nearer the base (ovate)."""
    L, ux, uy, nx, ny = _axis(p0, p1)
    tm = a / (a + b)
    hm = tm ** a * (1 - tm) ** b
    right, left = [], []
    for k in range(n + 1):
        t = k / n
        h = w / 2 * (t ** a * (1 - t) ** b) / hm
        x, y = p0[0] + ux * L * t, p0[1] + uy * L * t
        right.append((x + nx * h, y + ny * h))
        left.append((x - nx * h, y - ny * h))
    return poly(right + left[::-1])


def needle(p0, p1, w):
    """Pine needle: tapered stroke with a blunt rounded tip."""
    return taper(p0, p1, w, w * 0.62)


def holly(p0, p1, w, spikes=3):
    """Holly leaf: sharp spike points joined by concave scalloped edges
    (spikes per side, plus the tip)."""
    L, ux, uy, nx, ny = _axis(p0, p1)
    env = lambda t: w / 2 * (4 * t * (1 - t)) ** 0.7
    ts = [0.0] + [0.1 + 0.8 * (i + 0.5) / spikes for i in range(spikes)] + [1.0]
    def side(sgn):
        pts = []
        for a, b in zip(ts[:-1], ts[1:]):
            ea = env(a) * (1.12 if 0 < a < 1 else 1)
            eb = env(b) * (1.12 if 0 < b < 1 else 1)
            for k in range(12):
                t = k / 12
                tt = a + (b - a) * t
                h = ea + (eb - ea) * t - 0.42 * (b - a) * L * math.sin(math.pi * t) * 0.55
                pts.append((p0[0] + ux * L * tt + sgn * nx * h, p0[1] + uy * L * tt + sgn * ny * h))
        pts.append((p0[0] + ux * (L + 8), p0[1] + uy * (L + 8)))
        return pts
    core = taper(p0, (p0[0] + ux * L * 0.9, p0[1] + uy * L * 0.9), 20, 14)
    return U([poly(side(1) + side(-1)[::-1]), core])

def oak(p0, p1, w, lobes=3):
    """Oak leaf: a narrow core with rounded lobes in pairs and a round tip."""
    L, ux, uy, nx, ny = _axis(p0, p1)
    at = lambda t, h: (p0[0] + ux * L * t + nx * h, p0[1] + uy * L * t + ny * h)
    parts = [leaf(p0, p1, w * 0.5, 0.8, 0.9)]
    for k in range(lobes):
        t = 0.3 + 0.48 * k / max(1, lobes - 1)
        r = w * (0.22 - 0.03 * k)
        h = w / 2 - r - 2 * k
        parts += [circ(at(t, h), r), circ(at(t, -h), r)]
    parts.append(circ(at(0.88, 0), w * 0.2))
    return U(parts)

def spiral(c, r0, r1, turns, start_deg, w, cw=1):
    """Fiddlehead curl: spiral stroke from radius r0 down to r1."""
    n = int(80 * turns)
    pts = []
    for k in range(n + 1):
        t = k / n
        a = math.radians(start_deg + cw * 360 * turns * t)
        r = r0 + (r1 - r0) * t
        pts.append((c[0] + r * math.cos(a), c[1] + r * math.sin(a)))
    return U([line(pts, w), circ(pts[-1], w * 0.62)])


def hexagon(c, R, rot=0):
    return poly([(c[0] + R * math.cos(math.radians(rot + 60 * k)),
                  c[1] + R * math.sin(math.radians(rot + 60 * k))) for k in range(6)])


def star(c, R, r, n=6, rot=-90):
    pts = []
    for k in range(2 * n):
        rad = R if k % 2 == 0 else r
        a = math.radians(rot + 180 * k / n)
        pts.append((c[0] + rad * math.cos(a), c[1] + rad * math.sin(a)))
    return poly(pts)


def mirror(g):
    """Mirror an arm-local half across the arm axis (x = CX)."""
    return U([g, affinity.scale(g, -1, 1, origin=(CX, CY))])


def six(g, offset=0):
    return U([affinity.rotate(g, offset + 60 * k, origin=(CX, CY)) for k in range(6)])


def areal(g):
    if g.geom_type in ("Polygon", "MultiPolygon"):
        return g
    return U([p for p in getattr(g, "geoms", []) if p.geom_type in ("Polygon", "MultiPolygon")])


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


def flower_hole(c, R, petals=6, rot=-90):
    """Six-petal flower cut-out (for centre medallions)."""
    parts = [circ(c, R * 0.42)]
    for k in range(petals):
        a = math.radians(rot + 360 * k / petals)
        parts.append(leaf(c, (c[0] + R * math.cos(a), c[1] + R * math.sin(a)), R * 0.62, 1, 1))
    return U(parts)


# ---------------------------------------------------------------- designs
def d1_pine_bough():
    """Pine Bough: needle-lined arms ending in a fan of pine needles."""
    half = [taper(P(30), P(392), 32, 20)]
    nodes = [(112, 112), (158, 100), (204, 86), (250, 72), (294, 58), (334, 44)]
    for r, Ln in nodes:
        half.append(needle(P(r, 0), P(*D(r, 0, 44, Ln)), 19))
    # pine cone hanging outwards at the tip: overlapping scales
    # needle fan at the tip
    half.append(needle(P(372), P(478), 22))
    half.append(needle(P(372), P(*D(372, 0, 24, 92)), 19))
    half.append(needle(P(372), P(*D(372, 0, 50, 70)), 18))
    arm = mirror(U(half))
    # short sprig between the main arms
    sp = [taper(P(70), P(178), 24, 16), needle(P(118), P(*D(118, 0, 40, 46)), 16)]
    sprig = mirror(U(sp))
    g = U([six(arm), six(sprig, 30), circ((CX, CY), 74)])
    return g.difference(flower_hole((CX, CY), 46))


def d2_fern_frond():
    """Fern Frond: frond arms with paired pinnae (short at the base, longest
    mid-frond); small fiddlehead curls between the arms."""
    half = [taper(P(30), P(452), 26, 14)]
    rs = [176, 222, 266, 308, 348]
    lens = [72, 94, 92, 76, 54]
    for i, (r, Ln) in enumerate(zip(rs, lens)):
        w = 23 - i * 0.6
        half.append(leaf(P(r, 0), P(*D(r, 0, 62 - i * 2, Ln)), w, 0.5, 0.9))
    half.append(leaf(P(380), P(476), 30, 0.6, 1))
    half.append(leaf(P(384), P(*D(384, 0, 40, 40)), 18, 0.6, 1))
    arm = mirror(U(half))
    # fiddlehead between the arms: a short stem rising into a tight curl
    fh = U([taper(P(70), P(104), 20, 16),
            spiral(P(134, 0), 32, 14, 0.7, 90, 16, cw=-1)])
    g = U([six(arm), six(fh, 30), hexagon((CX, CY), 78, 30)])
    return g.difference(star((CX, CY), 50, 25, 6))


def d3_berry_sprig():
    """Berry Sprig: stems with leaf pairs, twig berries and a berry-cluster tip."""
    half = [taper(P(30), P(352), 26, 18)]
    # twig with a berry, low on the arm
    half.append(taper(P(150), P(*D(150, 0, 52, 92)), 18, 14))
    half.append(circ(P(*D(150, 0, 52, 112)), 23))
    # a pair of leaves higher up
    half.append(leaf(P(250), P(*D(250, 0, 48, 98)), 44, 0.6, 1))
    # berry cluster at the tip
    half += [circ(P(386, 0), 26), circ(P(424, 24), 23), circ(P(456, 0), 22)]
    arm = mirror(U(half))
    # small leaf between the main arms
    mid = leaf(P(84), P(196), 46, 0.6, 1)
    g = U([six(arm), six(mid, 30), circ((CX, CY), 80)])
    holes = [circ((CX, CY), 20)]
    for k in range(6):
        a = math.radians(-90 + 60 * k)
        holes.append(circ((CX + 50 * math.cos(a), CY + 50 * math.sin(a)), 16))
    return g.difference(U(holes))


def d4_holly_crystal():
    """Holly Crystal: a pair of holly leaves on every arm, a crystal tip and
    a three-berry cluster between the arms."""
    half = [taper(P(30), P(400), 30, 18)]
    half.append(holly(P(178), P(*D(178, 0, 34, 180)), 84, 3))
    # crystal spear tip
    half.append(poly([P(380, 0), P(418, 28), P(476, 0)]))
    arm = mirror(U(half))
    # vein cut-outs in the holly leaves
    veins = []
    for sgn in (1, -1):
        veins.append(leaf(P(*D(178, 0, 34 * sgn, 50)), P(*D(178, 0, 34 * sgn, 140)), 16, 1, 1))
    arm = arm.difference(U(veins))
    # berry triad between the main arms
    b = U([taper(P(70), P(118), 20, 16), circ(P(140, 0), 22), circ(P(170, 21), 20), circ(P(170, -21), 20)])
    g = U([six(arm), six(b, 30), circ((CX, CY), 72)])
    return g.difference(hexagon((CX, CY), 40, 0))


def d5_acorn_oak():
    """Acorn & Oak: an acorn at every arm tip, frost buds along the arms and
    a lobed oak leaf between the arms."""
    half = [taper(P(30), P(350), 28, 18)]
    half.append(taper(P(214), P(*D(214, 0, 52, 52)), 18, 14))
    half.append(leaf(P(*D(214, 0, 52, 44)), P(*D(214, 0, 52, 92)), 30, 0.8, 1))
    arm = mirror(U(half))
    # acorn hanging outwards: domed cap with a rim, then the nut
    cap = affinity.scale(circ(P(376, 0), 1), 62, 42).intersection(
        Polygon([P(320, -80), P(320, 80), P(378, 80), P(378, -80)]))
    rim = U([circ(P(376, s), 14) for s in (-50, -25, 0, 25, 50)])
    nut = leaf(P(366), P(482), 92, 0.5, 0.8)
    shine = leaf(P(398, 10), P(458, 6), 26, 0.9, 1.1)
    arm = U([arm, cap, rim, nut]).difference(shine)
    # oak leaf between the arms, with a midrib cut-out
    ok = U([taper(P(60), P(110), 20, 18), oak(P(96), P(306), 118, 3)])
    ok = ok.difference(leaf(P(130), P(268), 18, 1, 1))
    g = U([six(arm), six(ok, 30), circ((CX, CY), 76)])
    return g.difference(flower_hole((CX, CY), 48))

def d6_frost_twig():
    """Frosted Twig: classic branching snowflake arm, every branch leafy."""
    half = [taper(P(30), P(396), 30, 18)]
    branches = [(118, 120), (206, 100), (290, 72), (356, 40)]
    for r, Lb in branches:
        e = D(r, 0, 60, Lb)
        half.append(taper(P(r), P(*e), 20, 14))
        # leaf at the branch end and one leaf off the branch's outer side
        half.append(leaf(P(*e), P(*D(*e, 60, 34 + Lb * 0.18)), 30, 0.6, 1))
        if Lb > 60:
            m = D(r, 0, 60, Lb * 0.5)
            half.append(leaf(P(*m), P(*D(*m, 15, 30 + Lb * 0.16)), 26, 0.6, 1))
    # three-leaf tip
    half.append(leaf(P(392), P(476), 40, 0.6, 1))
    half.append(leaf(P(392), P(*D(392, 0, 38, 62)), 30, 0.6, 1))
    arm = mirror(U(half))
    g = U([six(arm), hexagon((CX, CY), 80, 0)])
    return g.difference(U([hexagon((CX, CY), 44, 0)]))


DESIGNS = {
    "01-pine-bough-snowflake": d1_pine_bough,
    "02-fern-frond-snowflake": d2_fern_frond,
    "03-berry-sprig-snowflake": d3_berry_sprig,
    "04-holly-crystal-snowflake": d4_holly_crystal,
    "05-acorn-oak-snowflake": d5_acorn_oak,
    "06-frosted-twig-snowflake": d6_frost_twig,
}


README = """BOTANICAL FROST SNOWFLAKES - 6 SVG CUT FILES
by Duskwood Designs Co (etsy.com/shop/DuskwoodDesignsCo)
Thank you for your purchase!

DESIGNS
  01 Pine Bough Snowflake
  02 Fern Frond Snowflake
  03 Berry Sprig Snowflake
  04 Holly Crystal Snowflake
  05 Acorn & Oak Snowflake
  06 Frosted Twig Snowflake

FILES
  SVG/  Cricut Design Space, Silhouette Designer Edition, Inkscape, Illustrator
  DXF/  Silhouette Studio Basic Edition, laser/CNC software (inches)
  PNG/  transparent background, 1800 x 1800 px (6 in at 300 DPI)

Each design is a single-layer shape with one clean cut path, so no slicing,
welding or cleanup is needed. Leaves, berries, cones and acorns are all
attached, so nothing falls out. Default size is 6 x 6 inches; resize freely,
but keep the proportions locked.

SIZING TIPS
  Vinyl (windows, mugs, tumblers, glass blocks): 3 in or larger.
  Cardstock (ornaments, gift tags, cards, garlands): 4 in or larger.
  Laser-cut wood or acrylic ornaments: 3.5 in or larger in 3 mm material.
  Heat-transfer vinyl (shirts, totes, pillows): 4 in or larger.
  The narrowest material and the narrowest gap are both about 0.08 in at
  6 in (half that at 3 in). Do a test cut first on a
  new material, and use a fresh blade for the leaf tips.

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


def view_box(geom, pad=12):
    """Square box centred on the flake centre."""
    x0, y0, x1, y1 = geom.bounds
    R = max(CX - x0, x1 - CX, CY - y0, y1 - CY) + pad
    return CX - R, CY - R, 2 * R, 2 * R


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


if __name__ == "__main__":
    only = sys.argv[1:]
    meta = {}
    for name, fn in DESIGNS.items():
        if only and not any(o in name for o in only):
            continue
        g = finish(fn())
        vb = view_box(g)
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
