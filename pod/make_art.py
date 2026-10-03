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


# ---- 004: replace AI-garbled gold stars with clean drawn ones -------------------------------
def gold_mask(a):
    r,g,b=a[...,0],a[...,1],a[...,2]
    return (r>150)&(g>90)&(r-b>50)&(r>=g)
def label(mask):
    """4-connected components via union-find over runs (numpy-free BFS is slow on 4k images)."""
    H,W=mask.shape
    lab=np.zeros((H,W),np.int32); parent=[0]; n=0
    def find(x):
        while parent[x]!=x:
            parent[x]=parent[parent[x]]; x=parent[x]
        return x
    prev=[]
    for y in range(H):
        row=mask[y]
        if not row.any(): prev=[]; continue
        d=np.diff(np.concatenate([[0],row.astype(np.int8),[0]]))
        starts=np.where(d==1)[0]; ends=np.where(d==-1)[0]
        cur=[]
        for s,e in zip(starts,ends):
            n+=1; parent.append(n); cur.append((s,e,n))
            for ps,pe,pl in prev:
                if ps<e and s<pe:
                    ra,rb=find(n),find(pl)
                    if ra!=rb: parent[max(ra,rb)]=min(ra,rb)
        for s,e,l in cur: lab[y,s:e]=l
        prev=cur
    roots=np.array([find(i) for i in range(n+1)],np.int32)
    return roots[lab]
def components(a):
    m=gold_mask(a); lab=label(m)
    ids=np.unique(lab[lab>0]); out=[]
    ys,xs=np.nonzero(lab)
    L=lab[ys,xs]; order=np.argsort(L); L=L[order]; ys=ys[order]; xs=xs[order]
    cuts=np.where(np.diff(L))[0]+1
    for yy,xx in zip(np.split(ys,cuts),np.split(xs,cuts)):
        x0,x1,y0,y1=xx.min(),xx.max()+1,yy.min(),yy.max()+1
        w,h=x1-x0,y1-y0; area=len(xx)
        out.append(dict(x0=x0,y0=y0,x1=x1,y1=y1,w=w,h=h,area=area,fill=area/(w*h),cx=xx.mean(),cy=yy.mean(),ys=yy,xs=xx))
    return out


def inpaint(crop, unknown):
    """Onion-peel fill: unknown pixels take the mean of their known 8-neighbours, ring by ring."""
    crop = crop.copy(); known = ~unknown
    while (~known).any():
        acc = np.zeros_like(crop); cnt = np.zeros(known.shape)
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if dy == dx == 0: continue
                k = np.roll(np.roll(known, dy, 0), dx, 1); v = np.roll(np.roll(crop, dy, 0), dx, 1)
                acc += v * k[..., None]; cnt += k
        new = (~known) & (cnt > 0)
        if not new.any(): break
        crop[new] = acc[new] / cnt[new][:, None]; known = known | new
    return crop


def inpaint_limited(crop, unknown, iters):
    """inpaint() limited to a few rings (for wide images where only a thin band needs filling)."""
    crop = crop.copy(); known = ~unknown
    for _ in range(iters):
        acc = np.zeros_like(crop); cnt = np.zeros(known.shape)
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if dy == dx == 0: continue
                k = np.roll(np.roll(known, dy, 0), dx, 1); v = np.roll(np.roll(crop, dy, 0), dx, 1)
                acc += v * k[..., None]; cnt += k
        new = (~known) & (cnt > 0)
        if not new.any(): break
        crop[new] = acc[new] / cnt[new][:, None]; known = known | new
    return crop


def clean_stars(a, gold=None, keep_fill=0.72, speck=20):
    """Baubles (round, fill >= 0.72) are kept. Every other gold mark (stars, squiggles, smudges) is
    erased and redrawn as a clean upright 5-point star of the same size; specks are just erased."""
    from PIL import ImageDraw
    import math
    a = a.copy(); comps = components(a)
    if gold is None:
        stars = [c for c in comps if 0.40 <= c["fill"] <= 0.48 and c["area"] > 500]
        gold = np.median(np.concatenate([a[c["ys"], c["xs"]] for c in stars]), 0)
    redraw = []
    for c in comps:
        if c["fill"] >= keep_fill and c["area"] >= 300 and 0.8 < c["w"] / c["h"] < 1.25:
            continue
        pad = 12
        x0, y0 = max(c["x0"] - pad, 0), max(c["y0"] - pad, 0)
        x1, y1 = min(c["x1"] + pad, a.shape[1]), min(c["y1"] + pad, a.shape[0])
        m = np.zeros((y1 - y0, x1 - x0), bool); m[c["ys"] - y0, c["xs"] - x0] = True
        # grow the mask 3 px to take the brownish anti-aliased halo with it
        mi = Image.fromarray(m.astype(np.uint8) * 255).filter(ImageFilter.MaxFilter(7))
        a[y0:y1, x0:x1] = inpaint(a[y0:y1, x0:x1], np.asarray(mi) > 0)
        if c["area"] >= speck:
            redraw.append(((c["x0"] + c["x1"]) / 2, (c["y0"] + c["y1"]) / 2, max(c["w"], c["h"]) / 2))
    S = 4
    for cx, cy, R in redraw:
        R = max(R, 6)
        x0, y0 = int(cx - R - 4), int(cy - R - 4); size = int(2 * R + 9)
        layer = Image.new("L", (size * S, size * S), 0); d = ImageDraw.Draw(layer)
        pts = []
        for k in range(10):
            ang = -math.pi / 2 + k * math.pi / 5
            rad = R if k % 2 == 0 else R * 0.45
            pts.append(((cx - x0 + rad * math.cos(ang)) * S, (cy - y0 + rad * math.sin(ang) + R * 0.08) * S))
        d.polygon(pts, fill=255)
        al = np.asarray(layer.resize((size, size), Image.LANCZOS)).astype(np.float64)[..., None] / 255
        reg = a[y0:y0 + size, x0:x0 + size]
        al = al[:reg.shape[0], :reg.shape[1]]
        a[y0:y0 + size, x0:x0 + size] = reg * (1 - al) + gold * al
    print("  clean_stars: kept", len(comps) - len(redraw) - sum(1 for c in comps if c["area"] < speck and not (c["fill"] >= keep_fill and c["area"] >= 300)),
          "baubles, redrew", len(redraw), "stars, gold", gold.round())
    return a


# Spot fixes for 004 that QA found at 100%, in tee-space px (x0, y0, x1, y1). Each rect is inpainted
# entirely from its border in RGBA (so gap pixels return to transparent), then clean stars are redrawn.
FIX_004_RECTS = [
    (2177, 793, 2192, 813), (2187, 786, 2202, 806), (2197, 780, 2212, 800), (2206, 775, 2224, 789),  # pale streak, tier 2 left
    (2304, 793, 2317, 809),   # grey smudge, tier 2 right
    (2068, 1160, 2103, 1189),  # three overlapping stars + brown smear, tier 3 centre
    (2066, 1476, 2076, 1489),  # pink halo left above a redrawn star, tier 4
]
FIX_004_CLEAR = [(2306, 724, 2326, 740)]  # red speck sitting in the gap on the tier-2 wing edge: made transparent
FIX_004_STARS = [(2079, 1171, 9), (2097, 1180, 6)]  # (cx, cy, R): the cluster redrawn as two separate stars


def draw_star(img, cx, cy, R, colour=(230, 183, 118, 255), S=4):
    from PIL import ImageDraw
    import math
    n = int(2 * R + 8)
    layer = Image.new("L", (n * S, n * S), 0); d = ImageDraw.Draw(layer)
    pts = [((n / 2 + (R if k % 2 == 0 else R * 0.45) * math.cos(-math.pi / 2 + k * math.pi / 5)) * S,
            (n / 2 + (R if k % 2 == 0 else R * 0.45) * math.sin(-math.pi / 2 + k * math.pi / 5) + R * 0.08) * S) for k in range(10)]
    d.polygon(pts, fill=255)
    img.paste(Image.new("RGBA", (n, n), colour), (round(cx - n / 2), round(cy - n / 2)), layer.resize((n, n), Image.LANCZOS))


def fix_004(rgba):
    a = rgba.astype(np.float64)
    a[..., :3] *= a[..., 3:] / 255  # premultiply so transparent pixels don't bleed colour into the fill
    for x0, y0, x1, y1 in FIX_004_RECTS:
        p = 3
        crop = a[y0 - p:y1 + p, x0 - p:x1 + p]
        unknown = np.zeros(crop.shape[:2], bool); unknown[p:-p, p:-p] = True
        a[y0 - p:y1 + p, x0 - p:x1 + p] = inpaint(crop, unknown)
    al = a[..., 3:]
    a[..., :3] = np.where(al > 0, a[..., :3] * 255 / np.maximum(al, 1e-6), 0)
    for x0, y0, x1, y1 in FIX_004_CLEAR:
        a[y0:y1, x0:x1] = 0
    a[740:743, 2309:2321] = a[740:743, 2322:2334]  # red base of the speck inside the edge line: copy the edge beside it
    # decontaminate the anti-aliased fringe: semi-transparent pixels take the colour of the nearest opaque
    # pixels, so the soft edge stays but the light halo from the white background/upscale is gone
    ys, xs = np.where(a[..., 3] > 0)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    sub = a[y0:y1, x0:x1]
    rgb = inpaint_limited(sub[..., :3], sub[..., 3] < 250, iters=6)
    semi = (sub[..., 3] > 0) & (sub[..., 3] < 250)
    sub[..., :3][semi] = rgb[semi]
    img = Image.fromarray(np.clip(a, 0, 255).round().astype(np.uint8), "RGBA")
    for cx, cy, R in FIX_004_STARS:
        draw_star(img, cx, cy, R)
    return img


def tee(src, out, on, width_px=3000, top=300, lo=20, hi=70, prep=None, post=None):
    a = load(src)
    if prep:
        a = prep(a)
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
    if post:
        canvas = post(np.asarray(canvas))
    canvas.save(os.path.join(POD, out), dpi=(300, 300))
    print(out, canvas.size, "design", art.size, "= %.1f x %.1f in" % (art.width / 300, art.height / 300), "upsample %.2f" % s)


if __name__ == "__main__":
    mug("001-luna-moth-mug/candidates/moth-3.png", "001-luna-moth-mug/mug-wrap-2700x1120.png", height=920, accent=moon_accent)
    mug("002-gothic-ornament-mug/candidates/ornament-3.png", "002-gothic-ornament-mug/mug-wrap-2700x1120.png",
        fix=[(1010, 1575, 1036, 1598)], height=960, centres=(675, 1350, 2025))
    tee("003-holly-skull-tee/candidates/skullB-2-up.png", "003-holly-skull-tee/tee-front-4500x5100.png", on="black")
    # lo=45: anything paler than min-channel 210 is background (an off-white AI patch at a wing tip was
    # only 36% keyed at lo=20 and would print as a light patch on Ash); gold (min channel ~122) stays opaque
    tee("004-bat-wing-tree-tee/candidates/battree-3-up.png", "004-bat-wing-tree-tee/tee-front-4500x5100.png", on="white",
        lo=45, hi=95, prep=clean_stars, post=fix_004)
