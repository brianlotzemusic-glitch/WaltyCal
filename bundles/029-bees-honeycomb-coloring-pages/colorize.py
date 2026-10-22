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
BG, SKY, WING, YEL, BRN, CREAM, GOLD, RED, LEAF, GRASS, STRAW, STRAW2, WOOD = (
    "#f3ead2", "#cfe6f0", "#bfe0f0", "#f4cf4a", "#5a3a2a", "#fbf4e2", "#e8a83a", "#d9506a", "#6f9a63", "#9cb07a",
    "#e8b54a", "#f0cf86", "#8a5a3c")

SPECS = {
    "01-bee-on-a-daisy": [
        (457, 256, YEL, "p"), (377, 299, YEL, "p"), (307, 301, BRN, "p"), (229, 312, YEL, "p"), (249, 163, WING, "p"), (356, 152, WING, "p"),
        (448, 600, GOLD, "p"), (472, 416, CREAM, "p"), (562, 451, CREAM, "p"), (619, 531, CREAM, "p"), (385, 451, CREAM, "p"),
        (299, 486, CREAM), (262, 575, CREAM), (637, 626, CREAM), (274, 672, CREAM), (597, 714, CREAM), (334, 749, CREAM), (520, 773, CREAM),
        (423, 786, CREAM), (760, 150, "#f6d96b", "p"), (150, 166, BG), (540, 871, LEAF), (353, 927, LEAF), (441, 961, LEAF),
        (448, 1090, GRASS), (460, 60, SKY, "p"), (40, 500, SKY, "p"),
    ],
    "03-skep-beehive": [
        (448, 456, STRAW), (458, 535, STRAW2), (465, 609, STRAW), (346, 689, STRAW2), (550, 689, STRAW2), (342, 764, STRAW), (554, 764, STRAW),
        (448, 821, WOOD), (448, 919, SKY), (448, 1075, GRASS), (449, 300, SKY), (703, 138, BG),
        (158, 267, WING), (106, 276, WING), (209, 314, YEL), (173, 338, YEL), (140, 341, BRN), (102, 348, YEL),
        (690, 357, WING), (741, 364, WING), (640, 406, YEL), (677, 429, YEL), (711, 430, BRN), (748, 437, YEL),
        (305, 503, WING), (348, 522, WING), (252, 535, YEL), (278, 562, YEL), (307, 571, BRN), (337, 585, YEL),
        (110, 909, RED), (90, 918, RED), (130, 918, RED), (790, 926, RED), (771, 935, RED), (809, 935, RED),
        (125, 980, LEAF), (86, 986, LEAF), (806, 982, LEAF), (766, 987, LEAF),
        (40, 700, SKY), (860, 700, SKY), (40, 300, SKY), (860, 300, SKY),
    ],
    "06-queen-bee": [
        (565, 546, YEL), (465, 587, YEL), (380, 583, BRN), (286, 590, YEL), (449, 407, WING), (322, 413, WING), (560, 446, GOLD),
        (770, 357, RED), (120, 518, RED), (450, 900, RED), (450, 90, GOLD), (130, 150, GOLD), (770, 190, GOLD),
        (197, 244, WING), (151, 252, WING), (241, 286, YEL), (211, 308, YEL), (181, 309, BRN), (148, 316, YEL),
        (150, 930, GOLD), (749, 927, GOLD), (448, 1079, GRASS),
        (452, 300, "#e4dcf0"), (449, 850, "#e4dcf0"), (40, 600, "#e4dcf0"), (860, 600, "#e4dcf0"),
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
            if not i:
                yy0, xx0 = min(H - 1, y * UP), min(W - 1, x * UP)
                win = lab[max(0, yy0 - 90):yy0 + 90, max(0, xx0 - 90):xx0 + 90]
                vals = win[win > 0]
                if len(vals):
                    i = np.bincount(vals).argmax()
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
