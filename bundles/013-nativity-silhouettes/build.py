"""Build and self-check the Nativity Silhouettes bundle.

  python3 build.py          # gen.py -> PNG -> listing images -> contact sheet -> ZIP -> checks
  python3 build.py check    # checks only (on the files inside the ZIP)
"""
import io, json, os, re, shutil, subprocess, sys, tempfile, zipfile
import ezdxf
from PIL import Image
from shapely.geometry import Polygon
from shapely.ops import unary_union

HERE = os.path.dirname(os.path.abspath(__file__))
ZIP = "nativity-silhouettes-svg.zip"
DISCLOSURE = "Designed with the help of digital and AI tools, and checked by hand for clean cuts."
NODE_ENV = dict(os.environ, NODE_PATH=subprocess.run(["npm", "root", "-g"], capture_output=True, text=True).stdout.strip())


def run(*cmd):
    subprocess.run(cmd, cwd=HERE, check=True, env=NODE_ENV)


def build():
    shutil.rmtree(os.path.join(HERE, "bundle"), ignore_errors=True)
    run("python3", "gen.py")
    os.makedirs(os.path.join(HERE, "bundle", "PNG"), exist_ok=True)
    run("node", "render.js", "bundle/SVG", "1800", "bundle/PNG")
    for f in os.listdir(os.path.join(HERE, "bundle", "PNG")):
        p = os.path.join(HERE, "bundle", "PNG", f)
        Image.open(p).save(p, dpi=(300, 300), optimize=True)
    run("node", "thumbs.js")
    run("node", "contact.js")
    with zipfile.ZipFile(os.path.join(HERE, ZIP), "w", zipfile.ZIP_DEFLATED) as z:
        for sub in ("SVG", "PNG", "DXF"):
            for f in sorted(os.listdir(os.path.join(HERE, "bundle", sub))):
                z.write(os.path.join(HERE, "bundle", sub, f), f"{sub}/{f}")
        z.write(os.path.join(HERE, "bundle", "README-LICENSE.txt"), "README-LICENSE.txt")
    shutil.rmtree(os.path.join(HERE, "bundle"))


FAIL = []


def res(name, ok, info=""):
    print(("PASS " if ok else "FAIL ") + name + (f"  ({info})" if info else ""))
    if not ok:
        FAIL.append(name)


def svg_geom(txt):
    vb = [float(v) for v in re.search(r'viewBox="([^"]*)"', txt).group(1).split()]
    d = re.findall(r' d="([^"]*)"', txt)
    rings = [[tuple(map(float, p.split(","))) for p in re.findall(r"-?[\d.]+,-?[\d.]+", r)] for r in d[0].split("Z") if r.strip()]
    # even-odd: XOR all rings
    g = Polygon()
    for r in rings:
        g = g.symmetric_difference(Polygon(r).buffer(0))
    return g, vb, len(d)


def check():
    with zipfile.ZipFile(os.path.join(HERE, ZIP)) as z:
        names = z.namelist()
        svgs = sorted(n for n in names if n.startswith("SVG/") and n.endswith(".svg"))
        pngs = sorted(n for n in names if n.startswith("PNG/") and n.endswith(".png"))
        dxfs = sorted(n for n in names if n.startswith("DXF/") and n.endswith(".dxf"))
        res("ZIP has 6 SVG, 6 PNG, 6 DXF + README-LICENSE.txt",
            len(svgs) == len(pngs) == len(dxfs) == 6 and "README-LICENSE.txt" in names, f"{len(svgs)}/{len(pngs)}/{len(dxfs)}")
        tmp = tempfile.mkdtemp()
        for n in svgs:
            txt = z.read(n).decode()
            g, vb, npaths = svg_geom(txt)
            k = 1000.0 / max(vb[2], vb[3])          # normalise to a 1000-unit design space
            polys = list(g.geoms) if g.geom_type == "MultiPolygon" else [g]
            holes = [Polygon(i).area * k * k for p in polys for i in p.interiors]
            w, h = re.search(r'width="([\d.]+)in" height="([\d.]+)in"', txt).groups()
            res(f"{n}: one path, one connected shape, valid", npaths == 1 and len(polys) == 1 and g.is_valid, f"{len(polys)} part(s)")
            res(f"{n}: smallest hole >= 600 u2", min(holes or [1e9]) >= 600, f"{len(holes)} holes, min {min(holes or [0]):.0f}")
            res(f"{n}: 6 in on the longest side", abs(max(float(w), float(h)) - 6.0) < 0.01, f"{w} x {h} in")
            # min material width: opening at r=6 (12 units) must not split or remove real material
            r = 6.0 / k
            op = g.buffer(-r, quad_segs=16).buffer(r, quad_segs=16)
            lost = g.difference(op)
            lost_parts = [p.area * k * k for p in (lost.geoms if hasattr(lost, "geoms") else [lost]) if not p.is_empty]
            nop = len(op.geoms) if op.geom_type == "MultiPolygon" else 1
            res(f"{n}: no material under ~12 units", nop == 1 and max(lost_parts or [0]) < 25, f"largest loss {max(lost_parts or [0]):.1f} u2")
            # min gap: closing at r=6 must not add real area
            worst = 0
            for rr in (2, 4, 6):
                rr /= k
                cl = g.buffer(rr, quad_segs=16).buffer(-rr, quad_segs=16)
                add = cl.difference(g)
                parts = [p.area * k * k for p in (add.geoms if hasattr(add, "geoms") else [add]) if not p.is_empty]
                worst = max(worst, max(parts or [0]))
            res(f"{n}: no gap under ~12 units", worst < 25, f"largest fill {worst:.1f} u2")
        for n in pngs:
            im = Image.open(io.BytesIO(z.read(n)))
            a = im.getchannel("A") if im.mode == "RGBA" else None
            res(f"{n}: 1800 px longest side, RGBA, transparent corner",
                max(im.size) == 1800 and im.mode == "RGBA" and a.getpixel((0, 0)) == 0 and a.getextrema()[1] == 255, f"{im.size}")
        for n in dxfs:
            p = os.path.join(tmp, os.path.basename(n))
            open(p, "wb").write(z.read(n))
            doc = ezdxf.readfile(p)
            ents = list(doc.modelspace())
            ok = doc.header.get("$INSUNITS") == 1 and ents and all(e.dxftype() == "LWPOLYLINE" and e.closed for e in ents)
            xs = [pt[0] for e in ents for pt in e.get_points()]
            ys = [pt[1] for e in ents for pt in e.get_points()]
            res(f"{n}: reopens in ezdxf, inches, closed polylines", bool(ok), f"{max(xs) - min(xs):.2f} x {max(ys) - min(ys):.2f} in")
        readme = z.read("README-LICENSE.txt").decode()
        res("README names the shop and all 6 designs", "Duskwood Designs Co" in readme and all(f"0{i} " in readme for i in range(1, 7)))
    for i in ("1-thumbnail", "2-whats-included", "3-formats", "4-color-ideas"):
        p = os.path.join(HERE, "listing-images", f"{i}.png")
        res(f"{i}.png is 3000x2250", os.path.exists(p) and Image.open(p).size == (3000, 2250))
    res("contact-sheet.png exists", os.path.exists(os.path.join(HERE, "contact-sheet.png")))
    lj = json.load(open(os.path.join(HERE, "listing.json")))
    t = lj["title"]
    caps = [w for w in re.findall(r"[A-Za-z']+", t) if len(w) > 1 and w[0].isupper() and w[1].isupper()]
    res("title <= 140 chars, leads with 'Nativity SVG Bundle'", len(t) <= 140 and t.startswith("Nativity SVG Bundle"), f"{len(t)} chars")
    res("title: <= 3 words starting with 2 capitals", len(caps) <= 3, ", ".join(caps))
    res("title: at most one '&'", t.count("&") <= 1)
    tags = lj["tags"]
    res("13 unique tags, each <= 20 chars", len(tags) == 13 and len(set(tags)) == 13 and all(len(x) <= 20 for x in tags),
        f"longest {max(len(x) for x in tags)}")
    blob = json.dumps(lj, ensure_ascii=False) + open(os.path.join(HERE, "LISTING.md")).read()
    res("no HTML entities, plain apostrophes", not re.search(r"&#\d+;|&[a-z]+;|[‘’]", blob))
    res("description ends with the disclosure line", lj["description"].rstrip().endswith(DISCLOSURE) and
        lj["description"].rstrip().endswith("\n\n" + DISCLOSURE))
    res("taxonomy 12394, price 4.0, digital file", lj["taxonomy_id"] == 12394 and lj["price"] == 4.0 and lj["digital_file"] == ZIP)
    print("\nALL CHECKS PASSED" if not FAIL else f"\n{len(FAIL)} CHECK(S) FAILED")
    return not FAIL


if __name__ == "__main__":
    if sys.argv[1:] != ["check"]:
        build()
    sys.exit(0 if check() else 1)
