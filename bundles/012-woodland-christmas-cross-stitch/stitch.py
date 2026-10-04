"""Renders the motifs as stitched pieces (X stitches on Aida, in wooden hoops) for the listing images.

  python3 stitch.py   # writes art/hoop-<key>-{colour,mono}.png (RGBA) from motifs.json

Drawn straight from the chart grids, so the pictures show exactly what the charts make.
"""
import json, math, os, random
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
D = json.load(open(os.path.join(HERE, "motifs.json")))
SS = 3  # supersampling


def rgb(h):
    h = h.lstrip("#"); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def shade(c, f):
    return tuple(max(0, min(255, int(v * f))) for v in c)


def fabric(wc, hc, s, base=(249, 247, 241)):
    """Aida patch wc x hc cells, s px per cell (already supersampled)."""
    im = Image.new("RGB", (wc * s, hc * s), base)
    d = ImageDraw.Draw(im)
    rnd = random.Random(7)
    for y in range(hc):
        for x in range(wc):
            f = 0.97 + rnd.random() * 0.04
            x0, y0 = x * s, y * s
            d.rounded_rectangle([x0 + s * .12, y0 + s * .12, x0 + s * .88, y0 + s * .88], radius=s * .25, fill=shade(base, f * 1.02))
    hole = shade(base, 0.72)
    r = s * 0.13
    for y in range(hc + 1):
        for x in range(wc + 1):
            d.ellipse([x * s - r, y * s - r, x * s + r, y * s + r], fill=hole)
    return im


def stitch(d, x, y, s, col):
    c = rgb(col)
    w = s * 0.42
    a, b = s * 0.12, s * 0.88
    # bottom leg (/), darker
    d.line([(x + a, y + b), (x + b, y + a)], fill=shade(c, 0.78), width=int(w))
    # top leg (\) with a highlight
    d.line([(x + a, y + a), (x + b, y + b)], fill=c, width=int(w))
    hl = tuple(min(255, int(v + (255 - v) * 0.28)) for v in c)
    d.line([(x + a + w * .15, y + a - w * .12), (x + b - w * .1, y + b - w * .37)], fill=hl, width=max(1, int(w * 0.22)))


def stitched(m, mono, s, pad):
    g = m["mono"] if mono else m["colour"]
    wc, hc = m["w"] + 2 * pad, m["h"] + 2 * pad
    im = fabric(wc, hc, s)
    sh = Image.new("L", im.size, 0); dsh = ImageDraw.Draw(sh)
    for y, r in enumerate(g):
        for x, ch in enumerate(r):
            if ch != ".":
                X, Y = (x + pad) * s, (y + pad) * s
                dsh.rectangle([X + s * .1, Y + s * .2, X + s * 1.0, Y + s * 1.05], fill=110)
    sh = sh.filter(ImageFilter.GaussianBlur(s * 0.18))
    im = Image.composite(Image.new("RGB", im.size, (150, 140, 128)), im, sh)
    d = ImageDraw.Draw(im)
    for y, r in enumerate(g):
        for x, ch in enumerate(r):
            if ch != ".":
                col = D["mono"]["hex"] if mono else D["palette"][ch]["hex"]
                if not mono and ch == "W":
                    col = "#f6ecd2"
                stitch(d, (x + pad) * s, (y + pad) * s, s, col)
    return im


def hoop(m, mono, size=1200):
    """RGBA image size x size: motif stitched on Aida in a wooden hoop with a brass screw."""
    S = size * SS
    ring = int(S * 0.055)
    inner = S - 2 * ring - int(S * 0.04)
    span = max(m["w"], m["h"]) / 0.66          # motif fills 66% of the fabric circle
    s = int(inner / span)
    pad = int(math.ceil((span - min(m["w"], m["h"])) / 2)) + 2
    patch = stitched(m, mono, s, pad)
    out = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    cx = cy = S // 2
    px = cx - patch.width // 2; py = cy - patch.height // 2 + int(S * 0.012)
    mask = Image.new("L", (S, S), 0); ImageDraw.Draw(mask).ellipse([cx - inner // 2, cy - inner // 2, cx + inner // 2, cy + inner // 2], fill=255)
    layer = Image.new("RGBA", (S, S), (0, 0, 0, 0)); layer.paste(patch, (px, py))
    out.paste(layer, (0, 0), mask)
    d = ImageDraw.Draw(out)
    # wooden ring: concentric bands
    R0 = inner // 2; R1 = R0 + ring
    for i in range(ring):
        t = i / ring
        f = 0.82 + 0.3 * math.sin(t * math.pi)
        c = shade((196, 150, 98), f)
        r = R0 + i
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=c, width=2)
    d.ellipse([cx - R1, cy - R1, cx + R1, cy + R1], outline=(120, 82, 48), width=max(2, SS * 2))
    d.ellipse([cx - R0, cy - R0, cx + R0, cy + R0], outline=(130, 92, 56), width=max(2, SS * 2))
    # brass clasp at the top
    bw, bh = int(S * 0.07), int(S * 0.05)
    d.rounded_rectangle([cx - bw // 2, cy - R1 - bh // 2, cx + bw // 2, cy - R1 + bh // 2], radius=bh // 4, fill=(184, 146, 72), outline=(120, 90, 40), width=SS * 2)
    d.rounded_rectangle([cx - bw // 4, cy - R1 - bh, cx + bw // 4, cy - R1 - bh // 2], radius=bh // 6, fill=(204, 168, 92), outline=(120, 90, 40), width=SS * 2)
    return out.resize((size, size), Image.LANCZOS)


if __name__ == "__main__":
    os.makedirs(os.path.join(HERE, "art"), exist_ok=True)
    for m in D["motifs"]:
        for mono in (False, True):
            hoop(m, mono).save(os.path.join(HERE, "art", f"hoop-{m['key']}-{'mono' if mono else 'colour'}.png"))
    # a flat close-up patch for image 3/4
    m = next(x for x in D["motifs"] if x["key"] == "fox")
    stitched(m, False, 60, 3).save(os.path.join(HERE, "art", "patch-fox-colour.png"))
    print("art/ written")
