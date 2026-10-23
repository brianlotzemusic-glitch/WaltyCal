"""Birdwatching Silhouettes - 6 single-path SVG/DXF/PNG cut files drawn in code ($0 AI).
Usage: python3 gen.py [names]  build bundle/SVG + DXF (+ README);  python3 gen.py --check
PNG export: node render.js bundle/SVG 1800 bundle/PNG (playwright)."""
import os, sys, json, zipfile
from lib import *
import birds, ezdxf

HERE = os.path.dirname(os.path.abspath(__file__))
B = os.path.join(HERE, "bundle")
SVG_DIR, DXF_DIR, PNG_DIR = (os.path.join(B, d) for d in ("SVG", "DXF", "PNG"))
for d in (SVG_DIR, DXF_DIR, PNG_DIR):
    os.makedirs(d, exist_ok=True)
SIZE_IN = 6.0
DESIGNS = {
    "01-heron-and-reeds-silhouette": birds.d_heron,
    "02-swallow-in-flight-silhouette": birds.d_swallow,
    "03-hummingbird-and-flower-silhouette": birds.d_hummingbird,
    "04-wren-on-a-branch-silhouette": birds.d_wren,
    "05-flock-of-birds-in-flight-disc": birds.d_flock_disc,
    "06-heron-in-flight-silhouette": birds.d_heron_flight,
}
README = """BIRDWATCHING SILHOUETTES - 6 SVG CUT FILES
by Duskwood Designs Co (etsy.com/shop/DuskwoodDesignsCo)
Thank you for your purchase!

DESIGNS
  01 Heron and Reeds Silhouette
  02 Swallow in Flight Silhouette
  03 Hummingbird and Flower Silhouette
  04 Wren on a Branch Silhouette
  05 Flock of Birds in Flight (round disc, birds cut out)
  06 Heron in Flight Silhouette

FILES
  SVG/  Cricut Design Space, Silhouette Designer Edition, Inkscape, Illustrator
  DXF/  Silhouette Studio Basic Edition, laser/CNC software (inches)
  PNG/  transparent background, 1800 px on the longest side (6 in at 300 DPI)

Each design is a single-layer shape with one connected cut path. Default
size is about 6 inches on the longest side. Fine tips (bills, wing tips, reed
tips) taper to about 0.07 in at 6 in; sizes below 4 in are not recommended.

LICENSE
  Personal use: unlimited.
  Small-business commercial use: you may sell finished physical products
  (decals, signs, cards, shirts, wall art, etc.) made with these designs,
  up to 500 units per design.
  You may NOT resell, share or redistribute the digital files themselves,
  in original or modified form, or include them in other digital products.
"""


def write_dxf(geom, path, vb):
    bx, by, w, h = vb
    k = SIZE_IN / max(w, h)
    doc = ezdxf.new("R2010"); doc.header["$INSUNITS"] = 1; doc.header["$MEASUREMENT"] = 0
    msp = doc.modelspace()
    for p in (geom.geoms if geom.geom_type == "MultiPolygon" else [geom]):
        for r in [p.exterior, *p.interiors]:
            msp.add_lwpolyline([((x - bx) * k, (h - (y - by)) * k) for x, y in list(r.coords)[:-1]], close=True)
    doc.saveas(path)


def check():
    from PIL import Image
    ok = True
    for name, fn in DESIGNS.items():
        g = finish(fn()); st = stats(g)
        svg = open(os.path.join(SVG_DIR, f"{name}.svg")).read()
        doc = ezdxf.readfile(os.path.join(DXF_DIR, f"{name}.dxf"))
        pl = doc.modelspace().query("LWPOLYLINE")
        xs = [x for e in pl for x, y, *_ in e.get_points()]; ys = [y for e in pl for x, y, *_ in e.get_points()]
        L = max(max(xs) - min(xs), max(ys) - min(ys))
        im = Image.open(os.path.join(PNG_DIR, f"{name}.png"))
        # thinnest wall: erode by 5 units must keep one part (tips may vanish; reported)
        good = (st["parts"] == 1 and st["valid"] and (st["holes"] == 0 or st["smallest_hole"] >= MIN_HOLE) and svg.count("<path") == 1
                and len(pl) == 1 + st["holes"] and 5.0 < L <= 6.0 and max(im.size) == 1800 and im.mode == "RGBA" and im.getextrema()[3][0] == 0)
        ok &= good
        print("OK  " if good else "FAIL", name, st, f"dxf {L:.2f} in", im.size)
    print("ALL CHECKS PASS" if ok else "CHECKS FAILED")
    return ok


if __name__ == "__main__":
    if "--check" in sys.argv:
        sys.exit(0 if check() else 1)
    for name, fn in DESIGNS.items():
        if sys.argv[1:] and not any(o in name for o in sys.argv[1:]):
            continue
        g = finish(fn()); vb = view_box(g); k = SIZE_IN / max(vb[2], vb[3])
        open(os.path.join(SVG_DIR, f"{name}.svg"), "w").write(
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb[0]:.1f} {vb[1]:.1f} {vb[2]:.1f} {vb[3]:.1f}" '
            f'width="{vb[2]*k:.3f}in" height="{vb[3]*k:.3f}in"><path fill="#000" fill-rule="evenodd" d="{to_path(g)}"/></svg>')
        write_dxf(g, os.path.join(DXF_DIR, f"{name}.dxf"), vb)
        print(name, stats(g))
    open(os.path.join(B, "README-LICENSE.txt"), "w").write(README)
