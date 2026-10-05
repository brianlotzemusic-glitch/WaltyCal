"""Turn the chosen AI drafts (art/raw/NN-slug.png, 896x1152) into bold, closed, print-ready line art.

  python3 process.py           # all pages -> art/svg/NN-slug.svg + art/stats.json
  python3 process.py 06        # one page

Steps per page (free, local):
  1. grey -> 3x Lanczos upscale (2688x3456) -> threshold: smooth edges at print size
  2. drop black specks under SPECK_MM2 (stray dots, noise)
  3. thicken: dilate the lines so the median stroke reaches TARGET_MM (bold & easy)
  4. frame: a rounded border of the same weight closes every region that runs off the art
  5. fill any white region under FILL_MM2 with black (no fiddly slivers; eyes, holes and
     snowflake centres become solid accents)
  5b. erase small isolated solid blobs (BLOB_*), which read as ink stains, and ERASE boxes
  6. potrace -> one smooth SVG path (black, even-odd), plus the region stats the checks use
Scale: the art box is ART_W_MM wide on paper (US Letter, the smaller page), so 1 mm = PX_MM px.
"""
import json, os, sys
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as nd

HERE = os.path.dirname(os.path.abspath(__file__))
UP = 3
W, H = 896 * UP, 1152 * UP
ART_W_MM = 182.0                      # art box width on US Letter (see build.js)
PX_MM = W / ART_W_MM                  # ~14.8 px per mm
TARGET_MM = 1.6                       # median stroke after thickening
MAX_GROW_MM = 0.55                    # never add more than this on each side
SPECK_MM2 = 1.2
FILL_MM2 = 12.0                       # white regions smaller than this become black
FRAME_MM = 1.8
BLOB_MIN_MM, BLOB_MAX_MM, BLOB_FILL = 6.0, 18.0, 0.38
BLOB_OPEN_MM2 = 2500.0                # ...and only when they float in open background
# per-page: erase every ink shape lying wholly inside these boxes (draft coords), after review
ERASE = {"04-mushrooms-in-snow": [(0, 0, 896, 520)],      # 5 tiny snowflakes that filled solid (looked like ink stains)
         "19-hare-under-the-moon": [(0, 960, 896, 1152)]}  # 6 grass tufts that filled solid (nothing to colour in them)
# ...replaced by big, chunky code-drawn snowflakes (centre x, y, arm length, rotation deg; draft coords)
FLAKES = {"04-mushrooms-in-snow": [(170, 150, 62, 0), (450, 95, 50, 15), (720, 170, 66, 8), (300, 330, 44, 20), (640, 380, 46, 0)]}
BLOB_MIN_AREA_MM2 = 45.0             # faces (noses, smiles, eyes) are smaller and stay


def disk(r):
    y, x = np.ogrid[-r:r + 1, -r:r + 1]
    return x * x + y * y <= r * r


def stroke_median(mask):
    d = nd.distance_transform_edt(mask)
    ridge = (d > 0) & (d >= nd.maximum_filter(d, 3))
    return float(np.median(2 * d[ridge])) if ridge.any() else 0.0


def process(slug):
    src = Image.open(os.path.join(HERE, "art", "raw", slug + ".png")).convert("L")
    big = np.array(src.resize((W, H), Image.LANCZOS))
    ink = big < 150
    # 2. specks
    lab, n = nd.label(ink)
    sizes = nd.sum(ink, lab, range(1, n + 1))
    small = np.zeros(n + 1, bool)
    small[1:] = sizes < SPECK_MM2 * PX_MM ** 2
    ink[small[lab]] = False
    # 3. thicken
    before = stroke_median(ink) / PX_MM
    grow = int(round(min(MAX_GROW_MM, max(0.0, (TARGET_MM - before) / 2)) * PX_MM))
    if grow:
        ink = nd.binary_dilation(ink, structure=disk(grow))
    # 4. frame: its outer edge is the art box edge
    fr = int(FRAME_MM * PX_MM)
    im = Image.fromarray((ink * 255).astype(np.uint8))
    ImageDraw.Draw(im).rounded_rectangle([0, 0, W - 1, H - 1], radius=int(8 * PX_MM), outline=255, width=fr)
    ink = np.array(im) > 127
    # outside the rounded frame corners: paper, not a region
    outside = np.zeros_like(ink)
    o = Image.fromarray(np.zeros((H, W), np.uint8))
    ImageDraw.Draw(o).rounded_rectangle([0, 0, W - 1, H - 1], radius=int(8 * PX_MM), fill=255)
    outside = np.array(o) == 0
    ink[outside] = False
    erased_box = 0
    for x0, y0, x1, y1 in ERASE.get(slug, []):
        lab, n = nd.label(ink)
        for i, sl in enumerate(nd.find_objects(lab), 1):
            if sl[1].start >= x0 * UP and sl[0].start >= y0 * UP and sl[1].stop <= x1 * UP and sl[0].stop <= y1 * UP:
                ink[sl][lab[sl] == i] = False
                erased_box += 1
    if FLAKES.get(slug):
        from shapely.geometry import LineString
        from shapely.ops import unary_union
        import math
        im = Image.fromarray((ink * 255).astype(np.uint8))
        dr = ImageDraw.Draw(im)
        for cx, cy, r, rot in FLAKES[slug]:
            cx, cy, r = cx * UP, cy * UP, r * UP
            parts = []
            for k in range(6):
                a = math.radians(rot + 60 * k)
                ex, ey = cx + r * math.cos(a), cy + r * math.sin(a)
                parts.append(LineString([(cx, cy), (ex, ey)]))
                bx, by = cx + 0.62 * r * math.cos(a), cy + 0.62 * r * math.sin(a)
                for s_ in (-1, 1):   # a short V branch on each arm
                    b = a + s_ * math.radians(50)
                    parts.append(LineString([(bx, by), (bx + 0.3 * r * math.cos(b), by + 0.3 * r * math.sin(b))]))
            shape = unary_union(parts).buffer(0.13 * r, quad_segs=8)
            w = TARGET_MM * PX_MM / 2
            dr.polygon(list(shape.buffer(w).exterior.coords), fill=255)
            dr.polygon(list(shape.buffer(-w).exterior.coords), fill=0)
        ink = np.array(im) > 127
    # 5. fill tiny regions
    paper = ~ink & ~outside
    lab, n = nd.label(paper)
    sizes = nd.sum(paper, lab, range(1, n + 1)) / PX_MM ** 2
    tiny = np.zeros(n + 1, bool)
    tiny[1:] = sizes < FILL_MM2
    ink[tiny[lab]] = True
    # 5b. small isolated shapes that the fill turned into solid blobs (tiny snowflakes, grass
    #     tufts) read as ink stains, so they are erased; faces (< BLOB_MIN_AREA_MM2 of ink) and anything touching
    #     another line stay
    lab, n = nd.label(ink)
    erased = 0
    pre = ink.copy()
    plab, pn = nd.label(~ink & ~outside)
    psize = np.concatenate([[0], nd.sum(~ink & ~outside, plab, range(1, pn + 1)) / PX_MM ** 2])
    for i, sl in enumerate(nd.find_objects(lab), 1):
        hh, ww = (sl[0].stop - sl[0].start) / PX_MM, (sl[1].stop - sl[1].start) / PX_MM
        if BLOB_MIN_MM < max(hh, ww) < BLOB_MAX_MM:
            comp = lab[sl] == i
            solid = nd.binary_fill_holes(comp).sum() == comp.sum()   # encloses no paper: not an outline
            # only blobs floating in open background (sky, snow); a nose inside a face sits in a small region
            ring = nd.binary_dilation(comp, iterations=3) & ~comp
            around = psize[plab[sl][ring]].max() if ring.any() else 0
            if solid and comp.sum() / comp.size > BLOB_FILL and comp.sum() >= BLOB_MIN_AREA_MM2 * PX_MM ** 2 \
                    and around >= BLOB_OPEN_MM2:
                ink[sl][comp] = False
                erased += 1
    if os.environ.get("DEBUG_DIR"):                      # red = erased blobs, for review
        rgb = np.stack([~pre * 255] * 3, -1).astype(np.uint8)
        rgb[pre & ~ink] = (230, 0, 0)
        Image.fromarray(rgb).resize((W // 3, H // 3)).save(os.path.join(os.environ["DEBUG_DIR"], slug + ".png"))
    paper = ~ink & ~outside
    lab, n = nd.label(paper)
    sizes = np.sort(nd.sum(paper, lab, range(1, n + 1)) / PX_MM ** 2)
    after = stroke_median(ink) / PX_MM
    stats = {"stroke_before_mm": round(before, 2), "grow_mm": round(grow / PX_MM, 2), "stroke_after_mm": round(after, 2),
             "regions": int(n), "smallest_region_mm2": round(float(sizes[0]), 1),
             "regions_under_40mm2": int((sizes < 40).sum()), "filled_tiny": int(tiny.sum()), "blobs_erased": erased + erased_box,
             "ink_pct": round(float(ink.mean() * 100), 1)}
    # 6. potrace
    import potrace
    bmp = potrace.Bitmap(~ink)            # potracer fills the False pixels
    path = bmp.trace(turdsize=20, opttolerance=0.4, alphamax=1.0)
    d = []
    for c in path:
        d.append(f"M{c.start_point.x:.1f},{c.start_point.y:.1f}")
        for s in c.segments:
            if s.is_corner:
                d.append(f"L{s.c.x:.1f},{s.c.y:.1f}L{s.end_point.x:.1f},{s.end_point.y:.1f}")
            else:
                d.append(f"C{s.c1.x:.1f},{s.c1.y:.1f} {s.c2.x:.1f},{s.c2.y:.1f} {s.end_point.x:.1f},{s.end_point.y:.1f}")
        d.append("Z")
    os.makedirs(os.path.join(HERE, "art", "svg"), exist_ok=True)
    with open(os.path.join(HERE, "art", "svg", slug + ".svg"), "w") as f:
        f.write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}">'
                f'<path fill="#000" fill-rule="evenodd" d="{"".join(d)}"/></svg>')
    os.makedirs(os.path.join(HERE, "art", "mask"), exist_ok=True)
    Image.fromarray((~ink * 255).astype(np.uint8)).convert("1").save(os.path.join(HERE, "art", "mask", slug + ".png"))
    return stats


if __name__ == "__main__":
    S = json.load(open(os.path.join(HERE, "subjects.json")))["pages"]
    only = sys.argv[1:]
    sp = os.path.join(HERE, "art", "stats.json")
    allstats = json.load(open(sp)) if os.path.exists(sp) else {}
    for slug, _, _ in S:
        if only and slug[:2] not in only:
            continue
        allstats[slug] = process(slug)
        print(slug, allstats[slug], flush=True)
    json.dump(allstats, open(sp, "w"), indent=1)
