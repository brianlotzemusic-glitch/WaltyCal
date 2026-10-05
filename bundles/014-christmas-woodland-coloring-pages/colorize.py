"""Coloured-in examples of real pages, for the listing images only (not in the buyer ZIP).

  python3 colorize.py   -> art/colored/NN-slug.jpg (full) and NN-slug-partial.jpg (half done)

Each spec fills the real page's own regions (from art/mask) with a soft coloured-pencil
texture, so the example can only show shapes the buyer actually gets.
Spec items (coords in the 896x1152 draft space):
  (x, y, colour)                 fill the region under the point
  ("box", x0, y0, x1, y1, colour) fill every region whose centre lies in the box (max 4000 mm2)
A trailing "p" marks items that are also in the partial (in-progress) version.
"""
import os
import numpy as np
from PIL import Image
from scipy import ndimage as nd

HERE = os.path.dirname(os.path.abspath(__file__))
UP = 3
PX_MM = 896 * UP / 182.0
SKY, NIGHT, MOON, PINE, PINE2, BARK, FOX, CREAM, BERRY, SNOW, PLUM, GOLD = (
    "#c9b8d8", "#5b4470", "#e8c97a", "#4f7a5c", "#3f6a4e", "#8a5a3c", "#d9773a", "#f4e7cf", "#a8384a", "#dde8f0", "#7a5a8c", "#e8c97a")

SPECS = {
    "01-fox-in-scarf": [
        (450, 60, SKY), (40, 300, SKY), (860, 300, SKY), (560, 470, SKY), (270, 600, SKY),
        (180, 330, PINE, "p"), (170, 440, PINE, "p"), (150, 530, PINE2, "p"), (150, 640, PINE, "p"), (180, 760, BARK, "p"),
        (690, 350, PINE), (690, 470, PINE), (700, 600, PINE2), (780, 650, PINE), (690, 760, BARK),
        (450, 610, FOX, "p"), (385, 530, CREAM, "p"), (500, 530, CREAM, "p"), (590, 820, FOX, "p"),
        ("box", 330, 860, 560, 960, FOX, "p"),
        ("box", 330, 690, 545, 790, BERRY, "p"),
        ("box", 0, 820, 896, 1140, SNOW),
    ],
    "02-owl-on-snowy-pine": [
        (40, 60, NIGHT, "p"), (300, 250, MOON, "p"),
        (155, 135, GOLD, "p"), (655, 150, GOLD, "p"), (780, 320, GOLD, "p"), (130, 350, GOLD, "p"),
        ("box", 430, 280, 720, 740, "#a77c5a"), (620, 330, "#c9a27c"), (470, 600, "#c9a27c"), (548, 420, GOLD), (660, 900, "#a77c5a"),
        ("box", 60, 500, 360, 640, BERRY), ("box", 60, 940, 240, 1060, BERRY),
        ("box", 230, 740, 360, 900, BARK), ("box", 310, 930, 450, 1100, BARK),
        ("box", 180, 600, 860, 1000, "#6b4a35"),
    ],
}


def hexrgb(h):
    return np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)], float)


def colorize(slug, spec, partial):
    mask = np.array(Image.open(os.path.join(HERE, "art", "mask", slug + ".png")).convert("L")) > 127
    lab, n = nd.label(mask)
    H, W = mask.shape
    cent = nd.center_of_mass(mask, lab, range(1, n + 1))
    area = nd.sum(mask, lab, range(1, n + 1)) / PX_MM ** 2
    colour = {}
    for it in spec:
        if partial and it[-1] != "p":
            continue
        if it[0] == "box":
            _, x0, y0, x1, y1, c = it[:6]
            for i, (cy, cx) in enumerate(cent, 1):
                if x0 * UP <= cx <= x1 * UP and y0 * UP <= cy <= y1 * UP and area[i - 1] < 4000 and i not in colour:
                    colour[i] = c
        else:
            x, y, c = it[:3]
            i = lab[min(H - 1, y * UP), min(W - 1, x * UP)]
            if i:
                colour[i] = c
    rng = np.random.default_rng(7)
    out = np.full((H, W, 3), 255.0)
    # pencil grain: diagonal strokes + noise, so fills look hand-coloured, not flat
    yy, xx = np.mgrid[0:H, 0:W]
    grain = 0.9 + 0.07 * np.sin((xx + yy) * 0.9) * np.sin(yy * 0.05) + rng.normal(0, 0.04, (H, W))
    for i, c in colour.items():
        m = lab == i
        rgb = hexrgb(c)
        # a light-catching edge: pencil fills fade slightly near the outline
        out[m] = 255 - (255 - rgb) * np.clip(grain[m], 0.75, 1.05)[:, None]
    out[~mask] = (34, 26, 38)
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).resize((W // 2, H // 2), Image.LANCZOS)


if __name__ == "__main__":
    os.makedirs(os.path.join(HERE, "art", "colored"), exist_ok=True)
    for slug, spec in SPECS.items():
        colorize(slug, spec, False).save(os.path.join(HERE, "art", "colored", slug + ".jpg"), quality=92)
        colorize(slug, spec, True).save(os.path.join(HERE, "art", "colored", slug + "-partial.jpg"), quality=92)
        print("coloured", slug)
