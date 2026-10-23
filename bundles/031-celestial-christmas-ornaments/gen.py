"""Celestial Christmas Ornaments - 6 single-path SVG/DXF cut files.

Hanging Christmas ornaments drawn in code (no AI images, $0): a crescent moon
with hanging stars, a star-and-moon bauble, a celestial wreath, moon phases,
a starburst and a moon over pines. Every design has a hanging loop and is
unioned into ONE connected polygon; no hole under 600 units^2, no material or
gap under ~13 units. Helpers are reused from bundle 023.

Usage:  python3 gen.py            build bundle/SVG + bundle/DXF + README
        python3 gen.py --check    verify the files
"""
import math, os, json, sys, random
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
    H = areal(U(holes))
    # fill any ring-shaped cut-out so no material is left floating inside it
    H = U([Polygon(p.exterior) for p in (H.geoms if H.geom_type == "MultiPolygon" else [H])])
    return S.difference(H)


def finish(g, r=6.5, simplify=0.12):
    """Close then open by r (no gaps or material under ~2r), drop small holes."""
    g = areal(make_valid(g))
    g = g.buffer(r, quad_segs=16).buffer(-r, quad_segs=16)
    g = g.buffer(-r, quad_segs=16).buffer(r, quad_segs=16)
    g = areal(set_precision(areal(make_valid(g.simplify(simplify))), 0.05))
    polys = list(g.geoms) if g.geom_type == "MultiPolygon" else [g]
    polys = [p for p in polys if p.area > 1500]   # crumbs between cut-outs would fall out anyway
    polys = [Polygon(p.exterior, [i for i in p.interiors if Polygon(i).area >= MIN_HOLE + 30]) for p in polys]
    return U(polys)




def catmull(pts, closed=True, n=16):
    out, P, m = [], list(pts), len(pts)
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


HOLLY = [(0.0, 0.0), (0.24, 0.40), (0.50, 0.50), (0.76, 0.38), (1.0, 0.0)]


def holly(x0, y0, ang, L, W, depth=1.0):
    """Holly leaf from its stalk end (x0, y0) pointing at ang (deg): three
    spikes a side joined by scooped edges, L long and about W/2 wide. Big
    enough (L >= 150) that the spikes survive finish()'s 6.5-unit rounding."""
    def edge(sg):
        out = []
        pts = [(x * L, sg * y * W) for x, y in HOLLY]
        for i, (a, b) in enumerate(zip(pts[:-1], pts[1:])):
            mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
            d = math.hypot(b[0] - a[0], b[1] - a[1])
            dp = depth * (0.45 if i == 0 else 1.0)    # gentler scoop next to the stalk
            nx, ny = -(b[1] - a[1]) / d, (b[0] - a[0]) / d
            if ny * sg > 0:                           # scoop toward the midrib
                nx, ny = -nx, -ny
            cx, cy = mx + nx * dp * d * 0.5, my + ny * dp * d * 0.5
            for k in range(12):
                t = k / 12
                out.append(((1 - t) ** 2 * a[0] + 2 * t * (1 - t) * cx + t * t * b[0],
                            (1 - t) ** 2 * a[1] + 2 * t * (1 - t) * cy + t * t * b[1]))
        out.append(pts[-1])
        return out
    lf = Polygon(edge(-1) + edge(1)[::-1][1:-1]).buffer(0)
    return affinity.translate(affinity.rotate(lf, ang, origin=(0, 0)), x0, y0)


def ellipse(cx, cy, rx, ry):
    return affinity.translate(affinity.scale(Point(0, 0).buffer(1, 48), rx, ry), cx, cy)


def taper(p0, p1, w0, w1):
    a = math.atan2(p1[1] - p0[1], p1[0] - p0[0]) + math.pi / 2
    c, s = math.cos(a), math.sin(a)
    q = poly([(p0[0] + c * w0 / 2, p0[1] + s * w0 / 2), (p1[0] + c * w1 / 2, p1[1] + s * w1 / 2),
              (p1[0] - c * w1 / 2, p1[1] - s * w1 / 2), (p0[0] - c * w0 / 2, p0[1] - s * w0 / 2)])
    return U([q, circ(*p0, w0 / 2), circ(*p1, w1 / 2)])


MINW = 15.0   # thinnest leg / antler tine after scaling (0.09 in at 6 in)


def limb(pts, ws):
    """Tapered leg / branch through joints pts with widths ws (one per joint)."""
    return U([taper(a, b, wa, wb) for a, b, wa, wb in zip(pts[:-1], pts[1:], ws[:-1], ws[1:])])


# ---------------------------------------------------------------- celestial parts
def ring(x, y, r, w):
    return circ(x, y, r + w / 2).difference(circ(x, y, r - w / 2))


def hanger(cx, ytop, neck=30):
    """Hanging loop (0.25 in hole at 6 in) + bead, sitting on the frame top at ytop."""
    ry = ytop - neck - 40
    loop = ring(cx, ry, 31, 22)
    stem = line([(cx, ry + 38), (cx, ytop + 8)], 22)
    bead = circ(cx, ytop - neck * 0.45, 20)
    return U([loop, stem, bead]), circ(cx, ry, 20)


def snow_ground(cx, gy, R, cy, amp=16, phase=0.0):
    """Snowy hill clipped to the inside of a circular frame (cx, cy, R)."""
    top = [(x, gy - amp * math.sin((x - cx) / 140 + phase) - 10 * math.cos((x - cx) / 300)) for x in range(int(cx - R), int(cx + R) + 1, 5)]
    return circ(cx, cy, R - 4).intersection(poly(top + [(cx + R, cy + R + 10), (cx - R, cy + R + 10)]))


def hung_star(x, y_top, y, r, w=24):
    """Star hanging on a thread (>= 24 wide, cut-safe) from the frame at y_top."""
    return U([line([(x, y_top), (x, y - r * 0.6)], w), star(x, y, r, r * 0.45)])


def sparkle(cx, cy, R, r=None, n=4, rot=-90):
    """Four-point twinkle star: concave sides, long points."""
    r = r if r is not None else R * 0.26
    return star(cx, cy, R, r, n=n, rot=rot)


def phase(cx, cy, R, kind):
    """Moon-phase shape for a cut-out: crescent, half, gibbous, full (waxing
    lit side on the right; waning is a flipped copy)."""
    full = circ(cx, cy, R)
    if kind == "full":
        return full
    if kind == "half":
        return full.intersection(box(cx, cy - R - 1, cx + R + 1, cy + R + 1))
    if kind == "crescent":
        return full.difference(circ(cx - R * 0.55, cy, R * 0.92))
    if kind == "gibbous":
        return full.difference(circ(cx - R * 1.45, cy, R * 1.12))
    raise ValueError(kind)


# ---------------------------------------------------------------- designs
C, R = (500, 520), 440


def d1_crescent_stars():
    """A big crescent moon cradling a star (the star's points overlap the
    moon), small stars cut out of the moon's body, hanging loop on the
    upper horn."""
    mc, mR = (470, 520), 430
    moon = crescent(*mc, mR, 190, -50, 0.88)
    h, hh = hanger(400, 130, neck=30)
    solid, holes = [moon, h, star(440, 500, 190, 84)], [hh]
    for (x, y, rr) in ((150, 360, 46), (120, 540, 38), (190, 720, 44)):
        holes.append(star(x, y, rr, rr * 0.5))
    return compose(solid, holes)


def d2_star_moon_bauble():
    """Classic bauble with a crescent moon and a scatter of stars and
    sparkles cut out of it."""
    cx, cy, Rb = 500, 570, 400
    cap = rect(cx - 74, cy - Rb - 58, cx + 74, cy - Rb + 26, 10)
    h, hh = hanger(cx, cy - Rb - 58)
    solid, holes = [circ(cx, cy, Rb), cap, h], [hh, rect(cx - 54, cy - Rb - 42, cx + 54, cy - Rb - 24, 8)]
    holes.append(crescent(400, 520, 190, 80, -50, 0.86))
    for (x, y, rr) in ((680, 330, 56), (720, 640, 44), (330, 840, 42), (560, 850, 34), (250, 310, 34)):
        holes.append(star(x, y, rr, rr * 0.5))
    for (x, y, rr) in ((700, 480, 46), (580, 760, 40), (240, 700, 38)):
        holes.append(sparkle(x, y, rr, rr * 0.3))
    return compose(solid, holes)


def d3_celestial_wreath():
    """A wreath ring with stars and four-point twinkles round the outside and
    a big star in the middle whose five points run out as rays to the ring."""
    cx, cy, Rw, bw = 500, 560, 330, 36
    h, hh = hanger(cx, cy - Rw - bw / 2 + 4, neck=26)
    solid, holes = [ring(cx, cy, Rw, bw), h], [hh]
    n = 12
    for k in range(1, n):
        th = -90 + 360 / n * k
        x, y = polar(cx, cy, Rw + 62, th)
        solid.append(star(x, y, 70, 32, rot=th) if k % 2 else sparkle(x, y, 74, 20, rot=th))
    for a in (-90, -18, 54, 126, 198):
        solid.append(line([polar(cx, cy, 120, a), polar(cx, cy, Rw, a)], 28))
    solid.append(star(cx, cy, 190, 84))
    return compose(solid, holes)


def d4_moon_phases():
    """A round ornament with the moon phases cut out in a row, stars above
    and below."""
    cx, cy, Rb = 500, 540, 440
    h, hh = hanger(cx, cy - Rb)
    solid, holes = [circ(cx, cy, Rb), h], [hh]
    kinds = ["crescent", "half", "full", "half", "crescent"]
    for i, kd in enumerate(kinds):
        x = 500 + (i - 2) * 170
        p = phase(0, 0, 70, kd)
        if i > 2:
            p = affinity.scale(p, -1, 1, origin=(0, 0))
        holes.append(affinity.translate(p, x, 540))
    for (x, y, rr) in ((500, 300, 60), (330, 360, 40), (670, 360, 40), (500, 790, 52), (330, 730, 36), (670, 730, 36)):
        holes.append(star(x, y, rr, rr * 0.5))
    return compose(solid, holes)


def d5_starburst():
    """An eight-point starburst: a star cut out of the middle with a smaller
    star inside, and a ring of round holes between the points."""
    cx, cy = 500, 540
    big = star(cx, cy, 470, 250, n=8, rot=-90)
    h, hh = hanger(cx, cy - 470 + 6, neck=26)
    solid, holes = [big, h], [hh]
    holes.append(star(cx, cy, 210, 100, n=8, rot=-90 + 22.5))
    for k in range(8):
        th = -90 + 22.5 + 45 * k
        holes.append(circ(*polar(cx, cy, 308, th), 30))
    return compose(solid, holes)


def d6_moon_pines():
    """A round frame: a crescent moon on the upper left, stars hanging from
    the top of the frame, and three pines standing on a snowy hill."""
    solid, holes = [ring(*C, R, 34)], []
    h, hh = hanger(500, C[1] - R)
    solid.append(h); holes.append(hh)
    solid.append(crescent(330, 330, 150, 64, -40, 0.8).intersection(circ(*C, R)))
    solid.append(line([(300, 100), (300, 215)], 26))
    solid.append(snow_ground(500, 820, R, C[1], amp=20))
    for x, hgt, w in ((300, 330, 200), (520, 460, 270), (720, 300, 190)):
        solid.append(pine(x, 835, hgt, w, tiers=4))
    solid.append(hung_star(640, 90, 300, 58))
    solid.append(hung_star(780, 170, 420, 44))
    return compose(solid, holes)


DESIGNS = {
    "01-crescent-moon-and-stars-ornament": d1_crescent_stars,
    "02-star-and-moon-bauble-ornament": d2_star_moon_bauble,
    "03-celestial-wreath-ornament": d3_celestial_wreath,
    "04-moon-phases-ornament": d4_moon_phases,
    "05-starburst-ornament": d5_starburst,
    "06-moon-over-pines-ornament": d6_moon_pines,
}


README = """CELESTIAL CHRISTMAS ORNAMENTS - 6 SVG CUT FILES
by Duskwood Designs Co (etsy.com/shop/DuskwoodDesignsCo)
Thank you for your purchase!

DESIGNS
  01 Crescent Moon & Stars Ornament
  02 Star & Moon Bauble Ornament
  03 Celestial Wreath Ornament
  04 Moon Phases Ornament
  05 Starburst Ornament
  06 Moon Over Pines Ornament

FILES
  SVG/  Cricut Design Space, Silhouette Designer Edition, Inkscape, Illustrator
  DXF/  Silhouette Studio Basic Edition, laser/CNC software (inches)
  PNG/  transparent background, 1800 px on the longest side (6 in at 300 DPI)

Each design is a single-layer shape with one cut path and a hanging loop
built in. Default size is about 6 inches on the longest side. Thinnest
parts are about 0.08 in wide at 6 in; sizes below 4 in are not recommended.

LICENSE
  Personal use: unlimited.
  Small-business commercial use: you may sell finished physical products
  (ornaments, decals, signs, shirts, cards, etc.) made with these designs,
  up to 500 units per design.
  You may NOT resell, share or redistribute the digital files themselves,
  in original or modified form, or include them in other digital products.
"""


# ---------------------------------------------------------------- export
PANELS = ()


def to_path(geom):
    polys = geom.geoms if geom.geom_type == "MultiPolygon" else [geom]
    d = []
    for p in polys:
        for r in [p.exterior, *p.interiors]:
            pts = list(r.coords)
            d.append("M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts[:-1]) + " Z")
    return " ".join(d)


def view_box(geom, square, pad=2):
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
