"""Turn the chosen AI drafts (art/raw/NN-slug.png, 896x1152) into bold, closed, print-ready line art.

  python3 process.py           # all pages -> art/svg/NN-slug.svg + art/stats.json
  python3 process.py 06        # one page

Steps per page (free, local):
  0. per-page RAW_WIPE / RAW_LINES on the upscaled draft: remove a stray stroke, redraw a line it hid
  1. grey -> 3x Lanczos upscale (2688x3456) -> threshold: smooth edges at print size
  2. drop black specks under SPECK_MM2 (stray dots, noise)
  3. thicken: dilate the lines so the median stroke reaches TARGET_MM (bold & easy)
  4. frame: a rounded border of the same weight closes every region that runs off the art
  5. fill any white region under FILL_MM2 with black (no fiddly slivers; eyes, holes and
     snowflake centres become solid accents)
  4b. ERASE boxes, then SHAPES drawn in code (chunky snowflakes, snow mounds); every snowflake is
      checked for wide gaps between its arms (FLAKE_*), or the fill would black it out
  5b. erase small isolated solid blobs (BLOB_*), which read as ink stains
  5c. CLUMPS: neighbouring spaces the fill turned black that together make a dark patch over
      CLUMP_MM2 (a splat, not an eye or a nose). Each must be fixed or accepted in CLUMP_OK
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
# Per-page fixes after review (draft coords, 896x1152). See formats/coloring.md.
# RAW_WIPE: ("line", [(x, y), ...], radius), ("box", x0, y0, x1, y1) or ("poly", [(x, y), ...]): painted white on the draft
# RAW_LINES: ([(x, y), ...], width): drawn black on the draft (redraws a line a wipe cut)
RAW_WIPE = {
    "04-mushrooms-in-snow": [("poly", [(745, 774), (797, 774), (799, 805), (791, 830), (778, 850), (768, 870), (758, 890),
                                       (750, 912), (708, 912), (711, 900), (710, 880), (714, 860), (742, 858),
                                       (749, 848), (754, 838), (755, 825), (754, 812), (752, 800), (749, 790)])],
                            # crowded fern leaves between the right mushroom and its stem that filled into one black clump
    "18-reindeer-with-wreath": [("line", [(225, 293), (236, 346)], 5),      # loose second stroke beside the left antler
                                ("line", [(240, 400), (259, 385)], 5)],     # short tick that closed a black wedge with the tree
    "19-hare-under-the-moon": [("box", 60, 862, 216, 962), ("box", 608, 866, 802, 968),     # 4 grass tufts that thickened
                               ("box", 30, 1025, 255, 1150), ("box", 650, 1028, 850, 1150)],  # into solid splats
}
RAW_LINES = {
    "04-mushrooms-in-snow": [([(812, 772), (803, 810), (799, 830), (788, 842), (777, 860), (771, 878), (762, 890),
                               (757, 900), (749, 920), (739, 950), (736, 962)], 8)],   # the fern's double stem as one line
    "18-reindeer-with-wreath": [([(229, 383), (238, 397), (247, 411)], 6),  # tree edge and antler beam the tick wipe cut
                                ([(244, 367), (258, 385), (272, 402)], 7)],
    "19-hare-under-the-moon": [([(55, 941), (80, 936), (120, 928), (160, 914), (192, 897), (212, 882), (228, 869),
                                 (238, 864)], 5),                                        # hill line behind tufts 1
                               ([(728, 860), (750, 866), (770, 873), (790, 882), (808, 892)], 5)],  # ...and tuft 2
}
# ERASE: every ink shape lying wholly inside these boxes, after thickening
ERASE = {"04-mushrooms-in-snow": [(0, 0, 896, 520)],      # 5 tiny AI snowflakes that filled solid (ink stains)
         "15-birdhouse-in-snow": [(520, 0, 860, 320)],      # 2 AI snowflakes whose inner details filled solid
         "18-reindeer-with-wreath": [(255, 538, 292, 568)]}  # lone ink tick inside the tree
# SHAPES drawn in code: ("flake", cx, cy, arm length, rotation deg) / ("mound", cx, base y, width, height)
SHAPES = {"04-mushrooms-in-snow": [("flake", 150, 140, 80, 0), ("flake", 450, 105, 75, 15), ("flake", 745, 150, 80, 8),
                                   ("flake", 290, 335, 75, 20), ("flake", 615, 345, 75, 0)],
          "15-birdhouse-in-snow": [("flake", 640, 108, 75, 10), ("flake", 790, 262, 75, 25)],
          "19-hare-under-the-moon": [("mound", 150, 1110, 230, 70), ("mound", 745, 1118, 200, 58)]}
FLAKE_HW, FLAKE_BPOS, FLAKE_BLEN, FLAKE_BANG = 0.13, 0.62, 0.22, 35   # arm half-width, branch position/length/angle
FLAKE_GAP_MM = 3.0                    # min gap between the branches of neighbouring arms
FLAKE_POCKET_MM2 = 12.0               # every space a flake encloses (its arms + hub) at least this
# CLUMPS: filled spaces within CLUMP_JOIN_MM of each other merge into one patch
CLUMP_JOIN_MM, CLUMP_MM2 = 1.2, 25.0
CLUMP_OK = {                          # slug: [((x0, y0, x1, y1), "reason")] for reviewed, accepted patches
    "06-hedgehog-with-mug": [((480, 520, 595, 580), "the cocoa in the mug: one dark drink with a wavy top, reads as intended")],
    "14-mouse-by-candlelight": [((235, 595, 420, 715), "the open book's page block: reads as a dark book, the cover stays open")],
    "16-tree-in-the-clearing": [((555, 740, 660, 810), "the gift's bow: a solid black bow on an outlined box")],
}
BLOB_MIN_AREA_MM2 = 45.0             # faces (noses, smiles, eyes) are smaller and stay


def disk(r):
    y, x = np.ogrid[-r:r + 1, -r:r + 1]
    return x * x + y * y <= r * r


def stroke_median(mask):
    d = nd.distance_transform_edt(mask)
    ridge = (d > 0) & (d >= nd.maximum_filter(d, 3))
    return float(np.median(2 * d[ridge])) if ridge.any() else 0.0


def flake_geometry(cx, cy, r, rot):
    """A chunky six-arm snowflake as an outline ring (outline minus inner), in px. Also the per-arm shapes."""
    import math
    from shapely.geometry import LineString
    from shapely.ops import unary_union
    cx, cy, r = cx * UP, cy * UP, r * UP
    w = TARGET_MM * PX_MM / 2
    arms = []
    for k in range(6):
        a = math.radians(rot + 60 * k)
        parts = [LineString([(cx, cy), (cx + r * math.cos(a), cy + r * math.sin(a))])]
        bx, by = cx + FLAKE_BPOS * r * math.cos(a), cy + FLAKE_BPOS * r * math.sin(a)
        for sgn in (-1, 1):
            b = a + sgn * math.radians(FLAKE_BANG)
            parts.append(LineString([(bx, by), (bx + FLAKE_BLEN * r * math.cos(b), by + FLAKE_BLEN * r * math.sin(b))]))
        arms.append(unary_union(parts))
    shape = unary_union(arms).buffer(FLAKE_HW * r, quad_segs=8)
    return shape.buffer(w), shape.buffer(-w), (arms, (cx, cy), r)


def flake_check(outline, inner, arms_info):
    """Gap between the branches of neighbouring arms (mm) and the smallest enclosed space (mm2)."""
    from shapely.geometry import Point
    arms, (cx, cy), r = arms_info
    w = TARGET_MM * PX_MM / 2
    hub = Point(cx, cy).buffer(0.9 * FLAKE_BPOS * r)
    outer = [a.buffer(FLAKE_HW * r + w).difference(hub) for a in arms]
    gap = min(outer[k].distance(outer[(k + 1) % 6]) for k in range(6)) / PX_MM
    pockets = [inner] if inner.geom_type == "Polygon" else list(inner.geoms)
    return {"gap_mm": round(gap, 2), "pocket_mm2": round(min(p.area for p in pockets) / PX_MM ** 2, 1),
            "pockets": len(pockets)}


def mound_geometry(cx, base, wd, ht):
    """An outlined snow mound: half an ellipse closed by its base line."""
    import math
    from shapely.geometry import Polygon
    pts = [((cx + wd / 2 * math.cos(t)) * UP, (base - ht * math.sin(t)) * UP) for t in np.linspace(0, math.pi, 60)]
    shape = Polygon(pts).buffer(0)
    w = TARGET_MM * PX_MM / 2
    return shape.buffer(w), shape.buffer(-w)


def process(slug):
    src = Image.open(os.path.join(HERE, "art", "raw", slug + ".png")).convert("L")
    bigim = src.resize((W, H), Image.LANCZOS)
    dr = ImageDraw.Draw(bigim)
    for item in RAW_WIPE.get(slug, []):
        if item[0] == "box":
            dr.rectangle([v * UP for v in item[1:5]], fill=255)
        elif item[0] == "poly":
            dr.polygon([(x * UP, y * UP) for x, y in item[1]], fill=255)
        else:
            from shapely.geometry import LineString
            poly = LineString([(x * UP, y * UP) for x, y in item[1]]).buffer(item[2] * UP)
            dr.polygon(list(poly.exterior.coords), fill=255)
    for pts, width in RAW_LINES.get(slug, []):
        dr.line([(x * UP, y * UP) for x, y in pts], fill=0, width=width * UP, joint="curve")
        for x, y in (pts[0], pts[-1]):
            r = width * UP / 2
            dr.ellipse([x * UP - r, y * UP - r, x * UP + r, y * UP + r], fill=0)
    big = np.array(bigim)
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
    flake_checks = []
    if SHAPES.get(slug):
        im = Image.fromarray((ink * 255).astype(np.uint8))
        dr = ImageDraw.Draw(im)
        w = TARGET_MM * PX_MM / 2
        for sh in SHAPES[slug]:
            if sh[0] == "flake":
                outline, inner, arms = flake_geometry(*sh[1:])
                flake_checks.append(flake_check(outline, inner, arms))
                dr.polygon(list(outline.exterior.coords), fill=255)
                dr.polygon(list(inner.exterior.coords), fill=0)
            else:
                outline, inner = mound_geometry(*sh[1:])
                dr.polygon(list(outline.exterior.coords), fill=255)
                dr.polygon(list(inner.exterior.coords), fill=0)
        ink = np.array(im) > 127
    # 5. fill tiny regions
    paper = ~ink & ~outside
    lab, n = nd.label(paper)
    sizes = nd.sum(paper, lab, range(1, n + 1)) / PX_MM ** 2
    tiny = np.zeros(n + 1, bool)
    tiny[1:] = sizes < FILL_MM2
    filled = tiny[lab]
    ink[filled] = True
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
    # 5c. clumps: filled spaces close together that make one dark patch
    filled &= ink
    join = nd.binary_dilation(filled, structure=disk(int(CLUMP_JOIN_MM * PX_MM)))
    clab, cn = nd.label(join)
    clumps = []
    for i, sl in enumerate(nd.find_objects(clab), 1):
        area = (filled[sl] & (clab[sl] == i)).sum() / PX_MM ** 2
        if area > CLUMP_MM2:
            box = [round(sl[1].start / UP), round(sl[0].start / UP), round(sl[1].stop / UP), round(sl[0].stop / UP)]
            cx, cy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
            ok = [r for (x0, y0, x1, y1), r in CLUMP_OK.get(slug, []) if x0 <= cx <= x1 and y0 <= cy <= y1]
            clumps.append({"box": box, "mm2": round(float(area), 1), "accepted": ok[0] if ok else None})
    paper = ~ink & ~outside
    lab, n = nd.label(paper)
    sizes = np.sort(nd.sum(paper, lab, range(1, n + 1)) / PX_MM ** 2)
    after = stroke_median(ink) / PX_MM
    stats = {"stroke_before_mm": round(before, 2), "grow_mm": round(grow / PX_MM, 2), "stroke_after_mm": round(after, 2),
             "regions": int(n), "smallest_region_mm2": round(float(sizes[0]), 1),
             "regions_under_40mm2": int((sizes < 40).sum()), "filled_tiny": int(tiny.sum()), "blobs_erased": erased + erased_box,
             "ink_pct": round(float(ink.mean() * 100), 1),
             "clumps": clumps, "clumps_unreviewed": sum(1 for c in clumps if not c["accepted"]),
             "flakes": flake_checks}
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
        st = allstats[slug]
        for c in st["clumps"]:
            if not c["accepted"]:
                print(f"  CLUMP {c['box']} {c['mm2']} mm2: fix it (RAW_WIPE / ERASE / SHAPES) or accept it in CLUMP_OK", flush=True)
        for f in st["flakes"]:
            if f["gap_mm"] < FLAKE_GAP_MM or f["pocket_mm2"] < FLAKE_POCKET_MM2:
                print(f"  FLAKE too tight ({f}): make it bigger; it needs {FLAKE_GAP_MM} mm between the arms", flush=True)
    json.dump(allstats, open(sp, "w"), indent=1)
