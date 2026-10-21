"""Unify the three AI images onto one flat midnight-blue background (art/*-4x.png -> art/unified/*.png).
Estimates each image's own background colour from its border, then shifts pixels close to it onto the shared colour,
so the set matches on the wall and any ratio can be made by padding with the flat colour."""
import os
import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage as ndi
TARGET = np.array([21, 36, 68], float)  # #152444 midnight blue
os.makedirs("art/unified", exist_ok=True)
for n in ("pine", "fern", "hellebore"):
    im = Image.open(f"art/{n}-4x.png").convert("RGB")
    a = np.asarray(im, float)
    h, w, _ = a.shape
    b = 60
    border = np.concatenate([a[:b].reshape(-1, 3), a[-b:].reshape(-1, 3), a[:, :b].reshape(-1, 3), a[:, -b:].reshape(-1, 3)])
    # local background (gradients/vignette): heavy blur of the image with ink replaced by the median bg
    bg0 = np.median(border, axis=0)
    d0 = np.linalg.norm(a - bg0, axis=2)
    ink = ndi.binary_dilation(d0 > 38, iterations=6)
    fill = a.copy(); fill[ink] = bg0
    sm = fill[::8, ::8]
    loc = np.stack([ndi.gaussian_filter(sm[..., c], 15) for c in range(3)], axis=2)
    loc = np.stack([ndi.zoom(loc[..., c], (h / sm.shape[0], w / sm.shape[1]), order=1)[:h, :w] for c in range(3)], axis=2)
    d = np.linalg.norm(a - loc, axis=2)
    wgt = 1 - np.clip((d - 14) / 36, 0, 1)         # 1 = pure background, 0 = art
    wgt = ndi.gaussian_filter(wgt, 1.2)
    out = a + (TARGET - loc) * wgt[..., None]
    Image.fromarray(np.clip(out, 0, 255).astype("uint8")).save(f"art/unified/{n}.png")
    print(n, bg0.round(), im.size)
