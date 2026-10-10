"""AI drafts -> finished clipart: transparent 300 DPI PNGs and single-layer SVGs (formats/clipart.md).

Inputs per design (all paid for once, see PROMPTS.md):
  art/raw/NN-slug.png    the chosen 1024 x 1024 flash draft on white
  art/alpha/NN-slug.png  its cut-out mask from Recraft `removebg` (1024 x 1024, 8-bit)
  art/up/NN-slug.png     the draft through Recraft `upscale` (4096 x 4096 on white; not committed,
                         ~12 MB each: re-run `imagegen.py upscale art/raw/X.png art/up/X.png`, $0.004, to rebuild)
Outputs:
  art/png/NN-slug.png    longest side 3600 px, 300 DPI, transparent, 256-colour palette PNG
  art/svg/NN-slug.svg    one-colour line-art version of the same design, one path, sized in inches
  art/stats.json         per design: size, file size, pieces, specks removed, ink share, SVG path count
Everything here is local and free.
"""
import json, os, re, sys
import numpy as np
from PIL import Image
from scipy import ndimage as nd

HERE = os.path.dirname(os.path.abspath(__file__))
Image.MAX_IMAGE_PIXELS = None
LONG = 3600            # px, longest side of the PNG (12 in at 300 DPI)
DPI = 300
SPECK_PX = 900         # at 3600 px: a piece of the cut-out smaller than this (~2.5 mm at 12 in) is a removebg speck
LINE_MAX = 105         # every channel below this = the dark plum linework, eyes and nostrils -> the SVG ink
                       # (a max-channel test, not luminance: red berries and green holly are as dark as the lines in luminance)
# removebg treats some small white parts of the art as background (the white mistletoe berries in 11).
# Enclosed transparent holes smaller than this many px (at 3600 px) are put back as the art's own colour.
# Bigger holes in those designs (the ribbon loops) stay transparent. Found by marking every enclosed hole and looking.
FILL_HOLES = {}
WHITE_MIN = 236        # clear_white: a pixel this light in every channel...
WHITE_TINT = 20        # ...and this close to grey is paper, not paint (cream horns and pompoms are warmer)
EDGE_OPAQUE = 200      # clear_white: edge pixels darker than this in any channel stay fully opaque
# Messy bits found by looking at 100%: inside each box (final 3600 px coordinates) every pixel that is not
# ginger fur (red over 150 and 60 above green) or a plum line (green under 45, red 25 above it) becomes transparent.
# Pieces left wholly inside a box afterwards (loose needle tips) are dropped too.
ERASE_BOX = {}
# QA round 1: light grey and white paper slivers between pine needles (and fringe strands) that clear_white
# misses because they are enclosed or tinted. Inside each box, light neutral pixels (every channel >= LIGHT_MIN,
# tint <= LIGHT_TINT) in patches under CLEAR_MAX_PX become transparent, with soft edges. Big light areas
# (horns, cream muzzles, pompoms) are far bigger than CLEAR_MAX_PX, so they stay.
LIGHT_MIN = 190        # a margin under the check's 195 / 35: palette quantizing shifts colours a little
LIGHT_TINT = 45
CLEAR_MAX_PX = 4000
CLEAR_BOX = {
    "02-blue-morpho": [(1680, 1800, 1720, 2240), (1880, 1800, 1920, 2240)],   # 018: 1 px paper rims on the cream wing bases
    "04-red-admiral": [(1700, 820, 1800, 920)],                 # 018: a paper sliver between the antenna and the head
    "06-common-blue": [(1650, 1300, 1950, 1800)],               # 018: pale paper rims in the gaps beside the body
    "09-red-dragonfly": [(1690, 880, 1930, 960)],               # 018: 1 px paper lines along the thorax
    # 018: pale ragged rims where the wings overlap, too small to take the wing tint
    "12-dragonfly-on-water-lily": [(2200, 1100, 2350, 1220), (1500, 1200, 1620, 1280), (2180, 1170, 2230, 1215)],
}
# QA round 2 (S6): 03's whole-image box also punched ~30 pinholes into its cream horn tips and chin. In these
# designs a cleared patch under PINHOLE_PX that sits wholly inside the art (no transparency on its rim), has no
# green needle on its rim and is at least 30% rimmed by cream is a light spot in the horn or muzzle, not paper
# between needles or fringe strands: it stays. fill_pinholes then closes any small hole left inside warm art.
PINHOLE_KEEP = set()
# 016: the plum dancer silhouette in 05 has hairline white paper cracks between its outline and its fill. clear_white
# turns the ones that reach the background into transparent cracks with a grey fringe. In these designs, opaque light
# paper pixels inside a closing of the plum silhouette (gaps up to ~2 x CRACK_ITER px) are repainted with the nearest
# plum before the white clean-ups run.
CRACK_FILL = {}
# 016: a bigger speck size per design (10: a loose sparkle dot by the holly, ~1,600 px, reads as a stray bubble on dark)
SPECK_BY_SLUG = {}
HOLE_PX = 60           # S6: any transparent hole under this, wholly inside the art, is closed with its rim's colour
PINHOLE_PX = 400
LINE_MAX_BY_SLUG = {}
# 018: 04's wings are flat near-black (every channel under 20), darker than its plum linework (50-105): leaving them
# out of the ink keeps its SVG a line drawing (otherwise ink is 51% of the canvas, over the 45% check)
LINE_MIN_BY_SLUG = {"04-red-admiral": 20}
# 017: designs with many fine dark pine needles have so much anti-aliased edge that only ~97% of their solid pixels
# are alpha 255 (S2 wants >= 98%). In these designs, palette entries at alpha >= this are snapped to 255 too: the edge
# colours are already un-mixed from the white, so the needle edges just get ~1 px crisper, with no light fringe.
EDGE_SNAP = {}   # 018: not used (QA 017 note: no needle-edge snapping)
# 018 (QA 017 note: colours true to the design's name): per-design colour fixes on the cut-out, in final 3600 px
# coordinates. Each rule: (box or None, hue_min, hue_max (degrees), min value 0-1, new hue or None, sat x, value x).
# Pixels inside the box with a hue in range and at least that value (so the dark plum outlines are untouched) get
# the new hue and scaled saturation/value. Shading and linework inside the shapes are kept.
RECOLOR = {
    # the draft's milkweed leaf was sky blue and teal with a lilac stalk, a maroon leaflet and a yellow oval: all leaf green
    "05-monarch-caterpillar": [(None, 180, 345, 0.40, 125, 0.75, 0.9),
                               ((1900, 1100, 2350, 1300), 25, 70, 0.40, 125, 0.8, 0.95)],
    # red admiral: the draft's lilac and sage body becomes the real butterfly's near-black body
    "04-red-admiral": [((1620, 790, 2090, 2520), 90, 300, 0.35, None, 0.4, 0.32)],
    # damselfly: orange legs and thorax become dark (real blue damselflies have black legs and thorax stripes);
    # the yellow curl at the reed's foot becomes reed green
    "11-damselfly-on-reed": [((250, 850, 1300, 2200), 0, 50, 0.30, None, 0.5, 0.25),
                             ((0, 3150, 800, 3600), 12, 90, 0.30, 160, 1.0, 0.85)],
}
# 018: dragonfly wings came out near-white, so they vanish on white and fail the halo test as if they were paper.
# Light neutral areas (the wing cells) are multiplied by the pale wing tint the prompt asked for.
TINT = {"08-blue-dragonfly": (205, 225, 255), "11-damselfly-on-reed": (205, 225, 255),
        "12-dragonfly-on-water-lily": (205, 225, 255), "10-green-darner": (255, 236, 200)}
TINT_MIN_PX = 1        # every light neutral patch: wing cells, glints and slivers between veins (eye glints turn pale blue too)
# 018: 02's draft drew the morpho's body with white seams along its sides and between its segments; removebg took them
# as background (transparent slits, light rims on dark fabric). Inside the box they are painted with the body plum.
PAINT = {"02-blue-morpho": [((1650, 1750, 1950, 2300), None)]}
SVG_PX = 1800          # trace resolution for the SVG (potrace smooths it; the SVG scales freely)
SVG_HOLE_PX = 60       # at SVG_PX: white slivers smaller than this inside the ink are filled
SVG_SPECK_PX = 80      # at SVG_PX: ink crumbs smaller than this are dropped


def cutout(slug):
    up = np.array(Image.open(os.path.join(HERE, "art", "up", slug + ".png")).convert("RGB")).astype(np.float32)
    al = Image.open(os.path.join(HERE, "art", "alpha", slug + ".png")).convert("L")
    A = np.array(al.resize(up.shape[1::-1], Image.BICUBIC)).astype(np.float32) / 255
    A = np.clip((A - 0.5) * 2 + 0.5, 0, 1)            # the 4x mask is soft: steepen it back to a ~1 px edge
    # un-mix the white background from the edge pixels, so the art has no white halo on dark fabric
    a = np.maximum(A, 1e-3)[..., None]
    rgb = np.where(A[..., None] > 0.15, np.clip((up - 255 * (1 - a)) / a, 0, 255), up)
    ys, xs = np.nonzero(A > 0.02)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    im = Image.fromarray(np.dstack([rgb, A * 255]).astype(np.uint8)[y0:y1, x0:x1], "RGBA")
    s = LONG / max(im.size)
    im = im.resize((round(im.size[0] * s), round(im.size[1] * s)), Image.LANCZOS)
    arr = np.array(im)
    recolor(slug, arr)
    solidify(arr)
    paint(slug, arr)
    # put back art that removebg took as background first, so the clean-ups below leave it alone
    filled = 0
    protect = np.zeros(arr.shape[:2], bool)
    if slug in FILL_HOLES:
        solid = arr[..., 3] > 127
        lab, n = nd.label(~solid)
        edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]])))
        sizes = nd.sum(np.ones(lab.shape), lab, range(1, n + 1))
        holes = [i + 1 for i, sz in enumerate(sizes) if sz < FILL_HOLES[slug] and (i + 1) not in edge]
        put = nd.binary_dilation(np.isin(lab, holes), iterations=3) & (arr[..., 3] < 250)
        a = arr[..., 3:].astype(np.float32) / 255
        on_white = arr[..., :3] * a + 255 * (1 - a)       # what the draft showed there
        arr[..., :3][put] = on_white[put].astype(np.uint8)
        arr[..., 3][put] = 255
        filled = len(holes)
        protect = put
    if slug in CRACK_FILL:
        protect |= fill_cracks(arr, CRACK_FILL[slug])
    cleared = clear_white(arr, protect) + clear_box(slug, arr, protect)
    tint_wings(slug, arr)
    for x0, y0, x1, y1 in ERASE_BOX.get(slug, []):
        box = arr[y0:y1, x0:x1]
        r, g = box[..., 0].astype(int), box[..., 1].astype(int)
        rest = ~(((r > 150) & (r - g > 60)) | ((g < 45) & (r - g > 25)))
        box[..., 3][rest] = 0
    # drop removebg specks: tiny islands of the mask far from the subject
    lab, n = nd.label(arr[..., 3] > 127, np.ones((3, 3)))
    sizes = nd.sum(np.ones(lab.shape), lab, range(1, n + 1))
    specks = [i + 1 for i, sz in enumerate(sizes) if sz < SPECK_BY_SLUG.get(slug, SPECK_PX)]
    if slug in ERASE_BOX:
        inside = np.zeros(lab.shape, bool)
        for x0, y0, x1, y1 in ERASE_BOX[slug]:
            inside[y0:y1, x0:x1] = True
        outside_ids = set(np.unique(lab[~inside & (lab > 0)]))
        specks = sorted(set(specks) | {int(i) for i in np.unique(lab[inside & (lab > 0)]) if i not in outside_ids})
    if specks:
        kill = nd.binary_dilation(np.isin(lab, specks), iterations=3)
        arr[..., 3][kill] = 0
    pieces = int(n - len(specks))
    # faint haze more than 4 px from any solid pixel (leftovers of erased or dropped pieces) goes too
    far = nd.distance_transform_edt(arr[..., 3] <= 127) > 4
    arr[..., 3][far] = 0
    out = Image.fromarray(arr, "RGBA")
    bbox = out.getchannel("A").point(lambda v: 255 if v > 8 else 0).getbbox()
    if bbox != (0, 0) + out.size:                     # erasing emptied an edge: trim again, back to LONG px
        out = out.crop(bbox)
        k = LONG / max(out.size)
        out = out.resize((round(out.size[0] * k), round(out.size[1] * k)), Image.LANCZOS)
        # resampling can leave 1 px crumbs at the cut edges: sweep them again
        arr = np.array(out)
        lab, n = nd.label(arr[..., 3] > 127, np.ones((3, 3)))
        sizes = nd.sum(np.ones(lab.shape), lab, range(1, n + 1))
        crumbs = [i + 1 for i, sz in enumerate(sizes) if sz < SPECK_PX]
        if crumbs:
            arr[..., 3][nd.binary_dilation(np.isin(lab, crumbs), iterations=2)] = 0
        arr[..., 3][nd.distance_transform_edt(arr[..., 3] <= 127) > 4] = 0
        pieces = int(n - len(crumbs))
        out = Image.fromarray(arr, "RGBA")
    if slug in PINHOLE_KEEP:                          # last, on the final pixels (the re-trim resamples)
        arr = np.array(out)
        fill_pinholes(arr)
        out = Image.fromarray(arr, "RGBA")
    arr = np.array(out)                               # S6, all designs: no pinholes left inside the art
    fill_small_holes(arr)
    out = Image.fromarray(arr, "RGBA")
    return out, pieces, len(specks), filled, cleared


def recolor(slug, arr):
    """RECOLOR rules: shift hue / scale saturation and value of matching pixels inside each box."""
    for box, h0, h1, vmin, newh, sk, vk in RECOLOR.get(slug, []):
        x0, y0, x1, y1 = box or (0, 0, arr.shape[1], arr.shape[0])
        sub = arr[y0:y1, x0:x1]
        hsv = np.array(Image.fromarray(np.ascontiguousarray(sub[..., :3])).convert("HSV")).astype(np.float32)
        h = hsv[..., 0] * 360 / 255
        m = (h >= h0) & (h <= h1) & (hsv[..., 2] >= vmin * 255) & (hsv[..., 1] >= 20) & (sub[..., 3] > 0)
        if newh is not None:
            hsv[..., 0][m] = newh * 255 / 360
        hsv[..., 1][m] *= sk
        hsv[..., 2][m] *= vk
        rgb = np.array(Image.fromarray(np.clip(hsv, 0, 255).astype(np.uint8), "HSV").convert("RGB"))
        sub[..., :3][m] = rgb[m]


def interior_opaque(q):
    """018: the quantizer can merge solid interior colours (thin plum veins on the wings) with soft edge colours into a
    palette entry at alpha ~244. Interior pixels (more than 3 px inside the art) on such an entry are moved to the
    nearest fully opaque palette colour. The palette and the anti-aliased outer edge are not changed (no edge snap)."""
    idx = np.array(q)
    pal = np.array(q.getpalette("RGBA")).reshape(-1, 4)[:256]
    A = pal[idx, 3]
    bad = (A < 255) & (nd.distance_transform_edt(A > 127) > 3)
    opaque = np.nonzero(pal[:, 3] == 255)[0]
    if not bad.any() or not len(opaque):
        return 0
    used = np.unique(idx[bad])
    remap = {}
    for u in used:
        dist = ((pal[opaque, :3].astype(int) - pal[u, :3].astype(int)) ** 2).sum(axis=1)
        remap[u] = opaque[dist.argmin()]
    new = idx.copy()
    for u, v in remap.items():
        new[bad & (idx == u)] = v
    q.frombytes(new.astype(np.uint8).tobytes())
    return int(bad.sum())


def paint(slug, arr):
    """PAINT: inside each box, the light seams and transparent slits within a closing of the plum body (gaps up to
    ~2 x 6 px) are painted with the nearest body plum at alpha 255."""
    for (x0, y0, x1, y1), _ in PAINT.get(slug, []):
        sub = arr[y0:y1, x0:x1]
        rgb = sub[..., :3].astype(int)
        r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
        plum = (sub[..., 3] > 127) & (r - g > 20) & (b - g > 10) & (rgb.max(axis=2) < 170)
        seam = nd.binary_closing(plum, iterations=6) & ~plum
        _, idx = nd.distance_transform_edt(~plum, return_indices=True)
        sub[..., :3][seam] = sub[idx[0][seam], idx[1][seam], :3]
        sub[..., 3][seam] = 255


def solidify(arr):
    """018: removebg left patches of the pale dragonfly wings part-transparent, deep inside the art. Pixels more than
    3 px inside the solid art with alpha 128-254 take the colour the draft showed there (on white) at alpha 255.
    The 1-3 px anti-aliased outer edge is left soft (no edge snapping, QA 017)."""
    A = arr[..., 3]
    m = (A > 127) & (A < 255) & (nd.distance_transform_edt(A > 127) > 3)
    a = A[m].astype(np.float32)[:, None] / 255
    arr[..., :3][m] = (arr[..., :3][m] * a + 255 * (1 - a)).astype(np.uint8)
    arr[..., 3][m] = 255


def tint_wings(slug, arr):
    """TINT: big light neutral areas (wing cells) are multiplied by the design's pale wing colour."""
    if slug not in TINT:
        return
    rgb = arr[..., :3].astype(np.float32)
    mn, mx = rgb.min(axis=2), rgb.max(axis=2)
    light = (arr[..., 3] > 127) & (mn >= 190) & (mx - mn <= 45)
    lab, n = nd.label(light, np.ones((3, 3)))
    sizes = nd.sum(light, lab, range(1, n + 1))
    big = np.isin(lab, [i + 1 for i, s in enumerate(sizes) if s >= TINT_MIN_PX])
    big = nd.binary_dilation(big, iterations=2) & (arr[..., 3] > 0) & (mn >= 150)   # their soft rims too
    arr[..., :3][big] = (rgb[big] * np.array(TINT[slug], np.float32) / 255).astype(np.uint8)


def clear_white(arr, protect):
    """removebg leaves the white paper between fine shapes (pine needles, fringe) opaque, which shows as
    white specks on dark fabric. Near-white pixels joined to the background through other near-white
    pixels become transparent, and the light edge pixels around them get a matching soft alpha.
    Enclosed whites (eye highlights, berries) are not joined to the background, so they stay."""
    a = arr[..., 3].astype(np.float32) / 255
    comp = arr[..., :3].astype(np.float32) * a[..., None] + 255 * (1 - a[..., None])   # the art on white
    mn, mx = comp.min(axis=2), comp.max(axis=2)
    white = (mn >= WHITE_MIN) & (mx - mn <= WHITE_TINT)
    bg = a < 0.5
    lab, n = nd.label(white | bg)
    keep = np.unique(lab[bg])
    clear = white & ~bg & np.isin(lab, keep[keep > 0]) & ~protect
    band = nd.binary_dilation(clear | bg, iterations=3) & ~bg & ~clear & ~protect
    soft = np.clip((255 - mn) / (255 - EDGE_OPAQUE), 0, 1)           # darker than EDGE_OPAQUE in any channel = opaque
    newa = a.copy()
    newa[clear] = 0
    newa[band] = np.minimum(a[band], soft[band])
    m = newa > 0.15
    arr[..., :3][m] = np.clip((comp[m] - 255 * (1 - newa[m, None])) / newa[m, None], 0, 255).astype(np.uint8)
    arr[..., 3] = (newa * 255).astype(np.uint8)
    return int(clear.sum())


def fill_pinholes(arr):
    """S6: transparent holes under 60 px wholly inside warm art (no green on the rim) get the rim's own warm colour."""
    A = arr[..., 3]
    hole = A < 200                                     # soft-edged holes too (removebg leaves some inside the fur)
    lab, n = nd.label(hole)
    edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]])))
    sizes = nd.sum(hole, lab, range(1, n + 1))
    rgb = arr[..., :3].astype(int)
    warm = (rgb[..., 0] > 180) & (rgb[..., 0] - rgb[..., 2] > 30) & (A >= 200)
    green = (rgb[..., 1] > rgb[..., 0] + 8) & (A >= 200)          # needle green; pale yellow cream is G ~ R
    for i, (sl, sz) in enumerate(zip(nd.find_objects(lab), sizes), 1):
        if i in edge or sz >= 60 or (A[sl][lab[sl] == i] >= 128).all():
            continue
        y0, y1, x0, x1 = max(sl[0].start - 3, 0), sl[0].stop + 3, max(sl[1].start - 3, 0), sl[1].stop + 3
        c = lab[y0:y1, x0:x1] == i
        ring = nd.binary_dilation(c, iterations=2) & ~c
        w = warm[y0:y1, x0:x1][ring]
        if w.mean() >= 0.5 and not green[y0:y1, x0:x1][ring].any():
            sub = arr[y0:y1, x0:x1]
            sub[..., :3][c] = np.median(rgb[y0:y1, x0:x1][ring][w], axis=0).astype(np.uint8)
            sub[..., 3][c] = 255


def fill_cracks(arr, iters):
    """Opaque light paper in thin cracks of a plum silhouette -> the nearest plum colour (016, design 05)."""
    a = arr[..., 3].astype(np.float32) / 255
    comp = arr[..., :3].astype(np.float32) * a[..., None] + 255 * (1 - a[..., None])
    r, g, b = comp[..., 0], comp[..., 1], comp[..., 2]
    plum = (a > 0.5) & (r - g > 30) & (b - g > 10) & (comp.max(axis=2) < 200)
    mn, mx = comp.min(axis=2), comp.max(axis=2)
    light = (a > 0.5) & (mn >= 140) & (mx - mn <= 70)
    crack = nd.binary_closing(plum, iterations=iters) & ~plum & light
    _, idx = nd.distance_transform_edt(~plum, return_indices=True)
    arr[..., :3][crack] = arr[idx[0][crack], idx[1][crack], :3]
    arr[..., 3][crack] = 255
    return crack


def fill_small_holes(arr):
    """S6: every transparent hole under HOLE_PX that sits wholly inside the art takes its rim's colour, opaque."""
    A = arr[..., 3]
    hole = A < 128
    lab, n = nd.label(hole)
    edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]])))
    sizes = nd.sum(hole, lab, range(1, n + 1))
    filled = 0
    for i, (sl, sz) in enumerate(zip(nd.find_objects(lab), sizes), 1):
        if i in edge or sz >= HOLE_PX:
            continue
        y0, y1, x0, x1 = max(sl[0].start - 3, 0), sl[0].stop + 3, max(sl[1].start - 3, 0), sl[1].stop + 3
        c = lab[y0:y1, x0:x1] == i
        grow = nd.binary_dilation(c, iterations=2)
        ring = grow & ~c & (A[y0:y1, x0:x1] >= 200)
        if not ring.any():
            ring = grow & ~c & (A[y0:y1, x0:x1] >= 128)
        if not ring.any():
            continue
        sub = arr[y0:y1, x0:x1]
        put = c
        sub[..., :3][put] = np.median(sub[..., :3][ring], axis=0).astype(np.uint8)
        sub[..., 3][put] = 255
        filled += 1
    return filled


def clear_box(slug, arr, protect):
    """Light neutral slivers inside the CLEAR_BOX boxes -> transparent, enclosed or not (QA round 1, fix 1)."""
    if slug not in CLEAR_BOX:
        return 0
    a = arr[..., 3].astype(np.float32) / 255
    comp = arr[..., :3].astype(np.float32) * a[..., None] + 255 * (1 - a[..., None])
    mn, mx = comp.min(axis=2), comp.max(axis=2)
    light = (a > 0.5) & (mn >= LIGHT_MIN) & (mx - mn <= LIGHT_TINT) & ~protect
    lab, n = nd.label(light, np.ones((3, 3)))
    sizes = nd.sum(light, lab, range(1, n + 1))
    small = np.isin(lab, [i + 1 for i, sz in enumerate(sizes) if sz < CLEAR_MAX_PX])
    inbox = np.zeros(light.shape, bool)
    for x0, y0, x1, y1 in CLEAR_BOX[slug]:
        inbox[y0:y1, x0:x1] = True
    clear = small & inbox
    if slug in PINHOLE_KEEP:
        clab, cn = nd.label(clear, np.ones((3, 3)))
        csize = nd.sum(clear, clab, range(1, cn + 1))
        green = (comp[..., 1] > comp[..., 0] + 8) & (a > 0.5)
        for i, (sl, sz) in enumerate(zip(nd.find_objects(clab), csize), 1):
            if sz >= PINHOLE_PX:
                continue
            y0, y1, x0, x1 = max(sl[0].start - 3, 0), sl[0].stop + 3, max(sl[1].start - 3, 0), sl[1].stop + 3
            comp_i = clab[y0:y1, x0:x1] == i
            ring = nd.binary_dilation(comp_i, iterations=2) & ~comp_i & ~light[y0:y1, x0:x1]
            cream = (comp[y0:y1, x0:x1, 0] > 200) & (comp[y0:y1, x0:x1, 0] - comp[y0:y1, x0:x1, 2] > 25)
            if ring.any() and not green[y0:y1, x0:x1][ring].any() and (a[y0:y1, x0:x1][ring] > 0.5).all() \
                    and cream[ring].mean() >= 0.3:
                clear[y0:y1, x0:x1][comp_i] = False
    # the pixels around each cleared sliver, and the pale 1-2 px rim round the needle tips (a frosty outline on dark)
    rim = inbox & nd.binary_dilation(a < 0.1, iterations=2) & (mn >= 140) & (mx - mn <= 50)
    band = (nd.binary_dilation(clear, iterations=2) | rim) & ~clear & (a > 0) & ~protect
    soft = np.clip((235 - mn) / (235 - 140), 0, 1)                   # pale edge pixels fade, needles stay solid
    newa = a.copy()
    newa[clear] = 0
    newa[band] = np.minimum(a[band], soft[band])
    m = band & (newa > 0.15)
    arr[..., :3][m] = np.clip((comp[m] - 255 * (1 - newa[m, None])) / newa[m, None], 0, 255).astype(np.uint8)
    arr[..., 3] = (newa * 255).astype(np.uint8)
    return int(clear.sum())


def line_art(im, line_max=LINE_MAX, line_min=0):
    """One-colour version: the dark linework plus a closed outer contour, as a boolean ink mask at SVG_PX."""
    small = im.copy()
    small.thumbnail((SVG_PX, SVG_PX), Image.LANCZOS)
    arr = np.array(small).astype(np.float32)
    A = arr[..., 3] > 127
    ink = A & (arr[..., :3].max(axis=2) < line_max) & (arr[..., :3].max(axis=2) >= line_min)
    # outer contour band, about one drawn line wide, so every outline is closed
    dist = nd.distance_transform_edt(A)
    lw = max(3.0, float(np.median(nd.distance_transform_edt(ink)[ink]) * 2.5)) if ink.any() else 4.0
    ink |= A & (dist <= lw)
    # tidy: fill tiny white slivers, drop crumbs
    lab, n = nd.label(~ink)
    if n:
        sz = nd.sum(np.ones(lab.shape), lab, range(1, n + 1))
        edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]])))
        fill = [i + 1 for i, s in enumerate(sz) if s < SVG_HOLE_PX and (i + 1) not in edge]
        ink |= np.isin(lab, fill)
    lab, n = nd.label(ink)
    if n:
        sz = nd.sum(np.ones(lab.shape), lab, range(1, n + 1))
        ink &= ~np.isin(lab, [i + 1 for i, s in enumerate(sz) if s < SVG_SPECK_PX])
    return ink, small.size


def to_svg(ink, size, out, scale_in):
    import potrace
    bmp = potrace.Bitmap(~ink)          # potracer fills the False pixels
    path = bmp.trace(turdsize=10, opttolerance=0.3)
    d = []
    for curve in path:
        d.append(f"M{curve.start_point.x:.1f},{curve.start_point.y:.1f}")
        for seg in curve.segments:
            if seg.is_corner:
                d.append(f"L{seg.c.x:.1f},{seg.c.y:.1f} L{seg.end_point.x:.1f},{seg.end_point.y:.1f}")
            else:
                d.append(f"C{seg.c1.x:.1f},{seg.c1.y:.1f} {seg.c2.x:.1f},{seg.c2.y:.1f} {seg.end_point.x:.1f},{seg.end_point.y:.1f}")
        d.append("Z")
    w, h = size
    with open(out, "w") as f:
        f.write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w * scale_in:.3f}in" height="{h * scale_in:.3f}in">'
                f'<path fill="#2c1b36" fill-rule="evenodd" d="{" ".join(d)}"/></svg>')
    return len(path)


def main(only=None):
    S = json.load(open(os.path.join(HERE, "subjects.json")))["designs"]
    stats_path = os.path.join(HERE, "art", "stats.json")
    stats = json.load(open(stats_path)) if os.path.exists(stats_path) else {}
    for d in ("png", "svg"):
        os.makedirs(os.path.join(HERE, "art", d), exist_ok=True)
    for slug, name, _ in S:
        if only and not any(slug.startswith(o) for o in only):
            continue
        im, pieces, specks, filled, cleared = cutout(slug)
        png = os.path.join(HERE, "art", "png", slug + ".png")
        for _ in range(3):
            q = im.quantize(256, method=Image.Quantize.FASTOCTREE, dither=Image.Dither.NONE)
            # the quantizer averages solid art to alpha 254: snap near-opaque palette entries to 255 (QA round 1, fix 2)
            pal = q.getpalette("RGBA")
            snap = EDGE_SNAP.get(slug, 250)
            pal[3::4] = [255 if v >= snap else v for v in pal[3::4]]
            q.putpalette(pal, "RGBA")
            # quantized alpha can split a soft crack into new pinholes (S6): close them and quantize again
            arr = np.array(q.convert("RGBA"))
            changed = fill_small_holes(arr)
            lab, n = nd.label(arr[..., 3] > 127, np.ones((3, 3)))      # ...and drop crumbs it lifts over alpha 127
            sizes = nd.sum(np.ones(lab.shape), lab, range(1, n + 1))
            crumbs = [i + 1 for i, sz in enumerate(sizes) if sz < SPECK_PX]
            if crumbs:
                arr[..., 3][nd.binary_dilation(np.isin(lab, crumbs), iterations=1)] = 0
            if not changed and not crumbs:
                break
            im = Image.fromarray(arr, "RGBA")
        interior_opaque(q)
        q.save(png, optimize=True, dpi=(DPI, DPI))
        ink, size = line_art(im, LINE_MAX_BY_SLUG.get(slug, LINE_MAX), LINE_MIN_BY_SLUG.get(slug, 0))
        scale_in = (im.size[0] / DPI) / size[0]      # the SVG opens at the PNG's print size
        paths = to_svg(ink, size, os.path.join(HERE, "art", "svg", slug + ".svg"), scale_in)
        alpha = np.array(im)[..., 3] > 127
        stats[slug] = {"name": name, "px": list(im.size), "inches": [round(v / DPI, 2) for v in im.size],
                       "png_mb": round(os.path.getsize(png) / 1e6, 2), "pieces": pieces, "specks_removed": specks, "holes_filled": filled, "white_px_cleared": cleared,
                       "coverage_pct": round(float(100 * alpha.mean()), 1),
                       "svg_ink_pct_of_shape": round(float(100 * ink.sum()) / max(1, (np.array(Image.fromarray(alpha).resize(size)) > 0).sum()), 1),
                       "svg_paths": paths}
        print(slug, stats[slug])
    json.dump(dict(sorted(stats.items())), open(stats_path, "w"), indent=1)


if __name__ == "__main__":
    main(sys.argv[1:] or None)
