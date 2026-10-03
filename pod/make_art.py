"""Build the print files for the POD pilot from the chosen Recraft candidates.

python3 pod/make_art.py      (free, local; reruns are deterministic)

Mugs (blueprint 68, SPOKE): full wrap 2700x1120 px (9 x 3.73 in at 300 DPI), flat background colour
sampled from the source. Printify's mug cameras look at 1/4 (left), 1/2 (front) and 3/4 (right) of the
wrap, so every one of those points carries a motif: the moth mug has moths at 1/4 and 3/4 with a
code-drawn gold crescent and sparkles at the front; the ornament mug has three baubles in a row.
Tees (blueprint 12, Monster Digital): 4500x5100 px transparent PNG (15 x 17 in at 300 DPI), design
10 in wide, centred, 1 in below the top of the print area. Background keyed out locally with a soft
ramp so edges stay anti-aliased: light-on-black art keys out black, dark-on-white art keys out white.
"""
import os
import numpy as np
from PIL import Image, ImageFilter

POD = os.path.dirname(os.path.abspath(__file__))


def load(rel):
    return np.asarray(Image.open(os.path.join(POD, rel)).convert("RGB")).astype(np.float64)


def bg_colour(a):
    border = np.concatenate([a[:150].reshape(-1, 3), a[-150:].reshape(-1, 3), a[:, :150].reshape(-1, 3), a[:, -150:].reshape(-1, 3)])
    return np.median(border, 0)


def bbox(a, bg, tol=30):
    ys, xs = np.where(np.abs(a - bg).max(2) > tol)
    return xs.min(), ys.min(), xs.max() + 1, ys.max() + 1


def mug(src, out, fix=None, height=1000, pad=24, centres=(675, 2025), accent=None):
    a = load(src)
    bg = bg_colour(a)
    if fix:  # paint stray marks with the background colour
        for x0, y0, x1, y1 in fix:
            a[y0:y1, x0:x1] = bg
    x0, y0, x1, y1 = bbox(a, bg)
    crop = a[y0 - pad:y1 + pad, x0 - pad:x1 + pad]
    motif = Image.fromarray(crop.round().astype(np.uint8))
    # feathered mask: design pixels opaque, background fades to the flat fill so no paste edge can show
    diff = np.abs(crop - bg).max(2)
    mask = Image.fromarray((np.clip((diff - 4) / 10, 0, 1) * 255).astype(np.uint8))
    mask = mask.filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(4))
    s = height / motif.height
    size = (round(motif.width * s), height)
    motif, mask = motif.resize(size, Image.LANCZOS), mask.resize(size, Image.LANCZOS)
    W, H = 2700, 1120
    canvas = Image.new("RGB", (W, H), tuple(int(round(c)) for c in bg))
    for cx in centres:
        canvas.paste(motif, (cx - motif.width // 2, (H - motif.height) // 2), mask)
    if accent:
        canvas = accent(canvas)
    canvas.save(os.path.join(POD, out), dpi=(300, 300))
    print(out, canvas.size, "motif", motif.size, "scale %.2f" % s, "bg", bg)


def moon_accent(canvas, gold=(250, 194, 104), cx=1350, cy=540, S=4):
    """Simple geometry, drawn at 4x and downsampled: a crescent opening to the upper right (like the
    moons on the moth's wings) and four-pointed sparkles in the moth art's gold."""
    from PIL import ImageDraw
    W, H = canvas.size
    layer = Image.new("L", (W * S, H * S), 0)
    d = ImageDraw.Draw(layer)
    r = 150
    d.ellipse([(cx - r) * S, (cy - r) * S, (cx + r) * S, (cy + r) * S], fill=255)
    ox, oy, ri = 62, -48, 132  # the bite that turns the disc into a crescent
    d.ellipse([(cx + ox - ri) * S, (cy + oy - ri) * S, (cx + ox + ri) * S, (cy + oy + ri) * S], fill=0)
    def sparkle(x, y, R):
        pts = []
        import math
        for k in range(8):
            ang = math.pi / 2 * (k // 2) + (math.pi / 4 if k % 2 else 0)
            rad = R if k % 2 == 0 else R * 0.22
            pts.append(((x + rad * math.cos(ang)) * S, (y + rad * math.sin(ang)) * S))
        d.polygon(pts, fill=255)
    for x, y, R in [(1265, 330, 26), (1452, 352, 15), (1440, 735, 22), (1262, 770, 13), (1350, 905, 17), (1300, 180, 11), (1415, 205, 9)]:
        sparkle(x, y, R)
    mask = layer.resize((W, H), Image.LANCZOS)
    canvas.paste(Image.new("RGB", (W, H), gold), (0, 0), mask)
    return canvas


def tee(src, out, on, width_px=3000, top=300, lo=20, hi=70):
    a = load(src)
    if on == "black":  # light art on black: alpha from brightest channel, unpremultiply against black
        alpha = np.clip((a.max(2) - lo) / (hi - lo), 0, 1)
        rgb = np.where(alpha[..., None] > 0, a / np.maximum(alpha[..., None], 1e-6), 0)
    else:  # dark art on white: alpha from darkness, unpremultiply against white
        alpha = np.clip((255 - a.min(2) - lo) / (hi - lo), 0, 1)
        rgb = np.where(alpha[..., None] > 0, (a - (1 - alpha[..., None]) * 255) / np.maximum(alpha[..., None], 1e-6), 255)
    rgba = np.dstack([np.clip(rgb, 0, 255), alpha * 255]).round().astype(np.uint8)
    ys, xs = np.where(alpha > 0.5)  # solid design only; faint upscale specks at the image border are dropped
    pad = 30
    box = (max(xs.min() - pad, 0), max(ys.min() - pad, 0), xs.max() + 1 + pad, ys.max() + 1 + pad)
    art = Image.fromarray(rgba, "RGBA").crop(box)
    s = width_px / art.width
    art = art.resize((width_px, round(art.height * s)), Image.LANCZOS)
    W, H = 4500, 5100
    canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    canvas.alpha_composite(art, ((W - art.width) // 2, top))
    canvas.save(os.path.join(POD, out), dpi=(300, 300))
    print(out, canvas.size, "design", art.size, "= %.1f x %.1f in" % (art.width / 300, art.height / 300), "upsample %.2f" % s)


if __name__ == "__main__":
    mug("001-luna-moth-mug/candidates/moth-3.png", "001-luna-moth-mug/mug-wrap-2700x1120.png", height=920, accent=moon_accent)
    mug("002-gothic-ornament-mug/candidates/ornament-3.png", "002-gothic-ornament-mug/mug-wrap-2700x1120.png",
        fix=[(1010, 1575, 1036, 1598)], height=960, centres=(675, 1350, 2025))
    tee("003-holly-skull-tee/candidates/skullB-2-up.png", "003-holly-skull-tee/tee-front-4500x5100.png", on="black")
    tee("004-bat-wing-tree-tee/candidates/battree-3-up.png", "004-bat-wing-tree-tee/tee-front-4500x5100.png", on="white")
