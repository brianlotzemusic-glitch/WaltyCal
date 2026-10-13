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
BG, MOSS, FERN, FERN2, RED, CREAM, TAN, GOLD, FOX, BARK, LEAF = (
    "#efe6cf", "#9cb07a", "#4f7a5c", "#6f9a63", "#c4473d", "#f6ecd6", "#d9b98c", "#e8b54a", "#d9773a", "#8a5a3c", "#7a9a4c")

SPECS = {
    "02-frog-on-a-toadstool": [
        (450, 200, MOSS, "p"), (290, 190, MOSS, "p"), (610, 190, MOSS, "p"), (380, 80, "#b9cf8f", "p"), (515, 80, "#b9cf8f", "p"),
        (330, 450, RED, "p"), (190, 460, CREAM, "p"), (460, 490, CREAM, "p"), (735, 465, CREAM, "p"), (330, 350, CREAM, "p"),
        (580, 350, CREAM, "p"), (200, 620, TAN, "p"), (700, 620, TAN, "p"), (470, 850, CREAM, "p"),
        (290, 720, GOLD), (310, 820, "#f0cf86"), (120, 780, FERN2), (200, 850, FERN2), (280, 1040, LEAF), (790, 950, LEAF),
        (790, 690, TAN), (650, 760, GOLD), (620, 880, "#f0cf86"), (680, 880, "#f0cf86"),
        (60, 300, BG), (850, 300, BG), (40, 640, BG), (60, 900, BG), (860, 700, BG), (850, 1120, BG), (450, 1130, BG),
    ],
    "04-fox-in-the-ferns": [
        (560, 650, FOX, "p"), (300, 650, FOX, "p"), (520, 880, FOX, "p"), (390, 880, CREAM, "p"), (200, 620, CREAM, "p"),
        (400, 560, CREAM, "p"), (60, 560, RED), (840, 560, RED), (740, 700, CREAM), (130, 700, CREAM),
        ("box", 20, 470, 250, 690, CREAM), ("box", 640, 440, 880, 640, CREAM),
        ("box", 0, 40, 896, 520, FERN, "p"), ("box", 0, 760, 896, 1150, FERN2),
        (870, 60, BG), (20, 760, BG), (880, 1100, BG), (600, 1120, BG),
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
