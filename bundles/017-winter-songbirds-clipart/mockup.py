"""Usage mockup for the listing: the real PNGs printed onto a blank AI flat-lay photo (local, free).

mockup/blank-flatlay.jpg is one flash draft of a blank tee, card and tote ($0.028 for 4 drafts) put
through Recraft `upscale` ($0.004); see PROMPTS.md. The designs are multiplied onto the fabric and
paper, so the folds and the window light show through the print as they would on a real transfer.
Writes mockup/flatlay.jpg (used by thumbs.js).
"""
import os
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
# design, centre (x, y) and width in the 4096 x 3186 photo, rotation in degrees (counter-clockwise),
# found by laying a 200 px grid over the photo
PLACES = [
    ("01-cardinal-on-holly", (1890, 1470), 780, 0),       # tee chest (the 015 blank flat-lay photo, reused for free)
    ("07-bluebird-on-berries", (3368, 1700), 430, -3.7),  # square card, tilted to match its edges
    ("10-holly-sprig", (2470, 2900), 420, 26),            # tote bag panel, beside the handles
]
INK = 0.94   # print opacity: a little of the fabric shows through, as on a real print


def main():
    bg = np.array(Image.open(os.path.join(HERE, "mockup", "blank-flatlay.jpg")).convert("RGB")).astype(np.float32) / 255
    for slug, (cx, cy), w, rot in PLACES:
        art = Image.open(os.path.join(HERE, "art", "png", slug + ".png")).convert("RGBA")
        art = art.resize((w, round(art.size[1] * w / art.size[0])), Image.LANCZOS)
        if rot:
            art = art.rotate(rot, Image.BICUBIC, expand=True)
        a = np.array(art).astype(np.float32) / 255
        h, ww = a.shape[:2]
        x0, y0 = cx - ww // 2, cy - h // 2
        x1, y1 = min(x0 + ww, bg.shape[1]), min(y0 + h, bg.shape[0])
        a = a[: y1 - y0, : x1 - x0]
        region = bg[y0:y1, x0:x1]
        light = region.mean(axis=2, keepdims=True)                     # the fabric's light and shadow
        printed = a[..., :3] * np.clip(light / 0.92, 0, 1.05)          # ink lit by the same light
        alpha = a[..., 3:] * INK
        bg[y0:y1, x0:x1] = region * (1 - alpha) + printed * alpha
    Image.fromarray((np.clip(bg, 0, 1) * 255).astype(np.uint8)).save(os.path.join(HERE, "mockup", "flatlay.jpg"), quality=90)


if __name__ == "__main__":
    main()
