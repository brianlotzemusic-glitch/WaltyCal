"""Cut the two AI sheets (4x upscales of art/animals.png and art/botanicals.png, deleted to save space; re-run imagegen.py upscale) into 12 transparent motifs in art/motifs/.
Segments by connected components of the non-white area (after dilation), then makes the outside white transparent."""
import os
import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage as ndi
NAMES = {"animals": ["fox", "hedgehog", "squirrel", "owl", "turkey", "deer"],
         "botanicals": ["acorns", "mushrooms", "oakleaf", "wheat", "maple", "apple"]}
os.makedirs("art/motifs", exist_ok=True)
for sheet, names in NAMES.items():
    im = Image.open(f"art/{sheet}-4x.png").convert("RGB")
    a = np.array(im)
    ink = a.min(axis=2) < 236
    grown = ndi.binary_dilation(ink, iterations=90)
    lab, n = ndi.label(grown)
    sizes = ndi.sum(ink, lab, range(1, n + 1))
    keep = sorted(np.argsort(sizes)[-6:] + 1)
    comps = []
    for l in keep:
        ys, xs = np.where(lab == l)
        comps.append((int(ys.mean() > a.shape[0] / 2), xs.mean(), l))
    comps.sort()  # top row then bottom row, left to right
    for (row, x0, l), name in zip(comps, names):
        region = lab == l
        # outside = white connected to the image border once restricted to this component's grown area
        white = ~ink
        outside = ndi.binary_dilation(~region, iterations=1) | ~region
        # white pixels reachable from outside the component, through white only
        wl, wn = ndi.label(white)
        edge_labels = set(np.unique(wl[~region & white])) - {0}
        bg = np.isin(wl, list(edge_labels)) | ~region
        alpha = np.where(bg, 0, 255).astype("uint8")
        # fill tiny enclosed white specks inside the shape stays opaque (cream fills); soften edge
        al = Image.fromarray(alpha).filter(ImageFilter.GaussianBlur(1.3))
        rgba = np.dstack([a, np.array(al)])
        out = Image.fromarray(rgba, "RGBA")
        out = out.crop(out.getchannel("A").point(lambda v: 255 if v > 8 else 0).getbbox())
        s = 760 / max(out.size)
        if s < 1: out = out.resize((round(out.width * s), round(out.height * s)), Image.LANCZOS)
        out.save(f"art/motifs/{name}.png", optimize=True)
        print(name, out.size)
# make stray pure-white pixels (gaps between mushroom stems etc.) transparent so cards of any tint show through
for f in os.listdir("art/motifs"):
    p = f"art/motifs/{f}"; a = np.array(Image.open(p).convert("RGBA"))
    a[(a[..., :3].min(axis=2) >= 246), 3] = 0
    Image.fromarray(a).save(p, optimize=True)
