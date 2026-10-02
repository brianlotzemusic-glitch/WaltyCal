"""Gingerbread Letter Ornaments - 26 single-path SVG/DXF cut files, A to Z.

Each letter is a chunky, rounded "cookie dough" letterform drawn from our own
skeleton strokes (straight lines and elliptical arcs) buffered with round caps
and joins, then closed slightly so inside corners look puffy like baked dough.
The "icing" is a piped wavy line that follows each stroke's centreline and is
cut out of the dough. Icing runs break at sharp corners, at junctions with
other strokes and at stroke ends, so it never encloses an island of material.
A hanging loop (ring + bead) sits above the letter's centre of mass so the
ornament hangs straight; letters with an open top (H, K, M, N, U, V, X, Y) get
a low, flat two-armed arch (25 units thick) resting on the two stroke tops,
and L gets an angled arm.
All letters share one scale, cap height and baseline, so names line up.
Coordinates are SVG-style (y grows downward) on a ~1000 unit canvas.
Output: SVG (6 in box, letter height ~5.8 in), DXF (inches), stats json.
"""
import math, os, json, sys
from shapely.geometry import LineString, Point, Polygon, MultiPoint
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

R = 70          # dough half-width (stroke 140 units)
CLOSE = 16      # puffy inside corners
CAP = 420       # skeleton cap height (local y 0 = top, 420 = baseline)
ICE_W = 8       # icing half-width (16 units wide)
ICE_A = 5.5     # icing wave amplitude (max slope ~17 deg to the stroke)
ICE_L = 110     # icing wavelength
EDGE_GAP = 30   # min distance from icing centre to the dough edge
DOT_R = 17      # icing dot radius (908 u2)
ICE_GAP = 40    # min distance between icing runs (centre to centre)
RING_Y = -170   # hanging ring centre (local)
Y_OFF = 380     # local -> canvas y
BOX = None      # fixed square box shared by all letters (set in main)


# ---------------------------------------------------------------- helpers
def arc(cx, cy, rx, ry, a0, a1, n=None):
    n = n or max(8, int(abs(a1 - a0)))
    return [(cx + rx * math.cos(math.radians(a0 + (a1 - a0) * k / n)),
             cy + ry * math.sin(math.radians(a0 + (a1 - a0) * k / n))) for k in range(n + 1)]


def cubic(p0, p1, p2, p3, n=40):
    out = []
    for k in range(n + 1):
        t = k / n
        u = 1 - t
        out.append(tuple(u ** 3 * p0[j] + 3 * u * u * t * p1[j] + 3 * u * t * t * p2[j] + t ** 3 * p3[j] for j in range(2)))
    return out


def resample(pts, step=2.0):
    ls = LineString(pts)
    n = max(2, int(ls.length / step))
    return [ls.interpolate(ls.length * k / n).coords[0] for k in range(n + 1)]


def split_corners(pts, max_turn=38):
    """Split a skeleton polyline at sharp corners so icing breaks there."""
    pts = [p for i, p in enumerate(pts) if i == 0 or math.dist(p, pts[i - 1]) > 1e-6]
    runs, cur = [], [pts[0]]
    for i in range(1, len(pts) - 1):
        a = math.atan2(pts[i][1] - pts[i - 1][1], pts[i][0] - pts[i - 1][0])
        b = math.atan2(pts[i + 1][1] - pts[i][1], pts[i + 1][0] - pts[i][0])
        turn = abs((math.degrees(b - a) + 180) % 360 - 180)
        cur.append(pts[i])
        if turn > max_turn:
            runs.append(cur)
            cur = [pts[i]]
    cur.append(pts[-1])
    runs.append(cur)
    return [r for r in runs if LineString(r).length > 1]


def wave(pts):
    """Wavy piped-icing centreline along a run (phase anchored at the run centre)."""
    P = resample(pts, 1.0)
    s = [0.0]
    for i in range(1, len(P)):
        s.append(s[-1] + math.dist(P[i], P[i - 1]))
    mid = s[-1] / 2
    out = []
    for i, (x, y) in enumerate(P):
        a, b = P[max(i - 10, 0)], P[min(i + 10, len(P) - 1)]   # local tangent, smoothed
        tx, ty = b[0] - a[0], b[1] - a[1]
        L = math.hypot(tx, ty) or 1
        nx, ny = -ty / L, tx / L
        o = ICE_A * math.sin(2 * math.pi * (s[i] - mid) / ICE_L)
        out.append((x + nx * o, y + ny * o))
    return out


def icing(strokes, dough, extra_breaks=()):
    """Icing cut-outs: wavy runs along each stroke, clipped away from the
    dough edge, from each other and from optional break points."""
    edge = dough.exterior if dough.geom_type == "Polygon" else dough.boundary
    edges = dough.boundary
    accepted = []
    acc_geom = None
    runs = [r for st in strokes for r in split_corners(st)]
    # longest runs first so the main strokes keep continuous icing
    runs.sort(key=lambda r: -LineString(r).length)
    for r in runs:
        W = wave(r)
        keep = []
        for p in W:
            q = Point(p)
            ok = edges.distance(q) >= EDGE_GAP and dough.contains(q)
            if ok and acc_geom is not None:
                ok = acc_geom.distance(q) >= ICE_GAP
            if ok and extra_breaks:
                ok = all(math.dist(p, b) >= 26 for b in extra_breaks)
            keep.append(ok)
        seg = []
        segs = []
        for p, k in zip(W, keep):
            if k:
                seg.append(p)
            else:
                if len(seg) > 1:
                    segs.append(seg)
                seg = []
        if len(seg) > 1:
            segs.append(seg)
        for sg in segs:
            if LineString(sg).length < 60:
                continue
            ln = LineString(sg)
            accepted.append(ln)
            acc_geom = unary_union(accepted)
    return unary_union([ln.buffer(ICE_W, 24) for ln in accepted]) if accepted else Polygon()


def dough_of(strokes):
    g = unary_union([LineString(s).buffer(R, 48) for s in strokes])
    return g.buffer(CLOSE, 32).buffer(-CLOSE, 32)


HW = 12.5       # hanger stem / arch half-width (25 units)


def hanger(dough, prongs=None):
    """Ring + bead above the centre of mass. prongs: None = straight stem down
    to the letter; two skeleton top points = a low, flat arch resting on the
    two stroke tops; one point = an angled arm (L)."""
    hx = dough.centroid.x
    ring_c = (hx, RING_Y)
    ring = Point(ring_c).buffer(42, 48).difference(Point(ring_c).buffer(21, 48))
    bead_y = RING_Y + 52
    bead = Point(hx, bead_y).buffer(18, 48)
    parts = [ring, bead, LineString([(hx, RING_Y + 36), (hx, bead_y)]).buffer(HW, 24)]
    if prongs is None:
        probe = LineString([(hx, -400), (hx, 2 * CAP)]).intersection(dough)
        top = probe.bounds[1]
        parts.append(LineString([(hx, bead_y), (hx, top + 24)]).buffer(HW, 24))
    elif len(prongs) == 1:
        (px, py), = prongs
        y_end = py - R + 26
        pts = cubic((hx, bead_y), (hx + (px - hx) * 0.55, bead_y),
                    (px, bead_y + 0.25 * (y_end - bead_y)), (px, y_end))
        parts.append(LineString(pts).buffer(HW, 24))
    else:
        # flat arch: rises only ~40 units above the stroke tops
        ya = -R - 38
        parts.append(LineString([(hx, bead_y), (hx, ya)]).buffer(HW, 24))
        for px, py in prongs:
            y_end = py - R + 30
            pts = cubic((px, y_end), (px, ya + 4), (hx + (px - hx) * 0.45, ya), (hx, ya))
            parts.append(LineString(pts).buffer(HW, 24))
    return unary_union(parts)


def finish(g, simplify=0.04):
    ref = g
    g = g.buffer(0.01).buffer(-0.01).simplify(simplify)
    polys = list(g.geoms) if g.geom_type == "MultiPolygon" else [g]
    polys = [p for p in polys if p.area > 50]
    return unary_union([Polygon(p.exterior, [i for i in p.interiors if Polygon(i).area >= MIN_HOLE + 20])
                        for p in polys])


def smooth(g):
    g = set_precision(make_valid(g), 0.05)
    g2 = g.buffer(-5, join_style=1).buffer(5, join_style=1)
    assert abs(g2.area - g.area) < 0.03 * g.area, "smoothing changed the shape too much"
    return g2


# ---------------------------------------------------------------- letters
# Each returns (strokes, hanger prongs or None). Local coords: y 0 top, 420 baseline.
B_ = CAP
M_ = CAP / 2


def L_A():
    ya = 285
    return [[(0, B_), (140, 0), (270, 0), (410, B_)],
            [(140 * (1 - ya / B_), ya), (410 - 140 * (1 - ya / B_), ya)]], None


def L_B():
    up = [(0, 0), (130, 0)] + arc(130, 100, 105, 100, -90, 90) + [(0, 200)]
    lo = [(0, 200), (150, 200)] + arc(150, 310, 115, 110, -90, 90) + [(0, B_)]
    return [[(0, 0), (0, B_)], up, lo], None


def L_C():
    return [arc(200, M_, 195, M_, -42, -318)], None


def L_D():
    bowl = [(0, 0), (90, 0)] + arc(90, M_, 210, M_, -90, 90) + [(0, B_)]
    return [[(0, 0), (0, B_)], bowl], None


def L_E():
    return [[(270, 0), (0, 0), (0, B_), (270, B_)], [(0, 205), (225, 205)]], None


def L_F():
    return [[(270, 0), (0, 0), (0, B_)], [(0, 200), (220, 200)]], None


def L_G():
    a = arc(205, M_, 200, M_, -55, -348)
    return [a, [(392, 245), (255, 245)]], None


def L_H():
    return [[(0, 0), (0, B_)], [(310, 0), (310, B_)], [(0, 210), (310, 210)]], [(0, 0), (310, 0)]


def L_I():
    # serifs too short for a wavy line: plain stem icing plus icing dots
    return [[(0, 0), (0, B_)], [(-95, 0), (95, 0)], [(-95, B_), (95, B_)]], None, \
        {"ice_only": [0], "dots": [(-78, 0), (78, 0), (-78, B_), (78, B_)]}


def L_J():
    return [[(60, 0), (260, 0)], [(200, 0), (200, 290)] + arc(95, 290, 105, 130, 0, 165)], None


def L_K():
    return [[(0, 0), (0, B_)], [(290, 0), (20, 235)], [(115, 152), (300, B_)]], [(0, 0), (290, 0)]


def L_L():
    return [[(0, 0), (0, B_), (265, B_)]], [(0, 0)]


def L_M():
    return [[(0, B_), (30, 0), (220, 300), (410, 0), (440, B_)]], [(30, 0), (410, 0)]


def L_N():
    return [[(0, B_), (0, 0), (320, B_), (320, 0)]], [(0, 0), (320, 0)]


def L_O():
    return [arc(205, M_, 205, M_, -90, 90), arc(205, M_, 205, M_, 90, 270)], None


def L_P():
    bowl = [(0, 0), (130, 0)] + arc(130, 118, 125, 118, -90, 90) + [(0, 236)]
    return [[(0, 0), (0, B_)], bowl], None


def L_Q():
    o = L_O()[0]
    return o + [[(345, 372), (490, B_)]], None


def L_R():
    bowl = [(0, 0), (130, 0)] + arc(130, 115, 125, 115, -90, 90) + [(0, 230)]
    return [[(0, 0), (0, B_)], bowl, [(120, 230), (300, B_)]], None


def L_S():
    up = arc(170, 105, 160, 105, -28, -270)
    lo = arc(170, 315, 165, 105, -90, 152)
    return [up + lo[1:]], None


def L_T():
    return [[(0, 0), (360, 0)], [(180, 0), (180, B_)]], None


def L_U():
    return [[(0, 0), (0, 260)] + arc(160, 260, 160, 160, 180, 0) + [(320, 0)]], [(0, 0), (320, 0)]


def L_V():
    return [[(0, 0), (175, B_), (350, 0)]], [(0, 0), (350, 0)]


def L_W():
    return [[(0, 0), (120, B_), (240, 30), (360, B_), (480, 0)]], None


def L_X():
    return [[(0, 0), (340, B_)], [(340, 0), (0, B_)]], [(0, 0), (340, 0)]


def L_Y():
    return [[(0, 0), (175, 215)], [(350, 0), (175, 215)], [(175, 215), (175, B_)]], [(0, 0), (350, 0)]


def L_Z():
    return [[(0, 0), (320, 0), (0, B_), (320, B_)]], None


LETTERS = {c: globals()[f"L_{c}"] for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"}


def build(c):
    spec = LETTERS[c]()
    strokes, prongs = spec[:2]
    opt = spec[2] if len(spec) > 2 else {}
    d = dough_of(strokes)
    # centre the letter on x = 0 by its dough bounding box
    x0, _, x1, _ = d.bounds
    dx = -(x0 + x1) / 2
    strokes = [[(x + dx, y) for x, y in s] for s in strokes]
    prongs = None if prongs is None else [(x + dx, y) for x, y in prongs]
    d = affinity.translate(d, dx, 0)
    ice_strokes = [strokes[i] for i in opt["ice_only"]] if "ice_only" in opt else strokes
    ice = icing(ice_strokes, d)
    dots = [Point(x + dx, y).buffer(DOT_R, 48) for x, y in opt.get("dots", [])]
    ice = unary_union([ice, *dots])
    h = hanger(d, prongs)
    # fillet the joins between hanger and dough (before the icing is cut)
    body = unary_union([d, h]).buffer(10, 32).buffer(-10, 32)
    g = body.difference(ice)
    g = affinity.translate(g, 500, Y_OFF)
    return smooth(g), ice


README = """GINGERBREAD LETTER ORNAMENTS - FULL A-Z ALPHABET, 26 SVG CUT FILES
by Duskwood Designs Co (etsy.com/shop/DuskwoodDesignsCo)
Thank you for your purchase!

DESIGNS
  26 gingerbread-cookie letter ornaments, A to Z (01-letter-a ... 26-letter-z).
  Each letter has piped-icing cut-outs and a hanging loop built in.
  Cut one letter per ornament, or cut several to spell a name.

FILES
  SVG/  Cricut Design Space, Silhouette Designer Edition, Inkscape, Illustrator
  DXF/  Silhouette Studio Basic Edition, laser/CNC software (inches)
  PNG/  1800 x 1800 px, transparent background (6 in at 300 DPI)

Each letter is a single-layer shape with one clean cut path, including the
hanging loop at the top. Resize freely, but keep the proportions locked.

SIZING TIPS
  Every letter is drawn at the same height, with the same cap height and
  baseline. To spell a name, give every letter the SAME HEIGHT (not the same
  width) and the letters will line up; wide letters like M and W are simply
  wider. At the default size each letter is about 5.8 in tall including the
  hanging loop.
  Popular sizes: 3 to 4 in tall for tree ornaments and gift tags, 5 to 6 in
  for door or wall letters. The icing lines are about 0.13 in wide at 5.8 in;
  we recommend 3 in or taller for cardstock and vinyl, and 3.5 in or taller
  for laser-cut wood or acrylic. Use 4 in or larger in wood/acrylic for
  H K M N U V X Y (the hanger arch). Do a test cut first on a new material.

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
    x0, y0, x1, y1 = g.bounds
    return {"parts": len(polys), "holes": len(hs), "smallest_hole": round(min(hs or [0]), 1),
            "valid": g.is_valid, "w": round(x1 - x0), "h": round(y1 - y0), "top": round(y0), "bottom": round(y1)}


if __name__ == "__main__":
    only = sys.argv[1:]
    geoms = {c: finish(build(c)[0]) for c in LETTERS if not only or c in only}
    # one shared square box so every letter has the same scale and baseline
    y0 = min(g.bounds[1] for g in geoms.values())
    y1 = max(g.bounds[3] for g in geoms.values())
    wmax = max(g.bounds[2] - g.bounds[0] for g in geoms.values())
    side = max(y1 - y0, wmax) + 24
    box_ = (500 - side / 2, (y0 + y1) / 2 - side / 2, side)
    meta = {"box_side": round(side, 1)}
    for i, (c, g) in enumerate(geoms.items()):
        name = f"{ord(c) - 64:02d}-letter-{c.lower()}"
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{box_[0]:.1f} {box_[1]:.1f} {box_[2]:.1f} {box_[2]:.1f}" '
               f'width="6in" height="6in"><path fill="#000" fill-rule="evenodd" d="{to_path(g)}"/></svg>')
        with open(os.path.join(SVG_DIR, f"{name}.svg"), "w") as f:
            f.write(svg)
        write_dxf(g, os.path.join(DXF_DIR, f"{name}.dxf"), box_)
        meta[name] = stats(g)
    with open(os.path.join(HERE, "bundle", "README-LICENSE.txt"), "w") as f:
        f.write(README)
    # letter x-extents for the listing images (not shipped in the ZIP)
    with open(os.path.join(HERE, "bundle", "bounds.json"), "w") as f:
        json.dump({"box": box_, "x": {c: geoms[c].bounds[0::2] for c in geoms}}, f)
    print(json.dumps(meta))
