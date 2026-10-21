"""Builds the wall-art JPGs (+ PDFs) per ratio from art/unified/*.png (flat midnight-blue padding makes any ratio)."""
import os, sys
from PIL import Image, ImageFilter
BG = (21, 36, 68)
ART = [("pine", "frosted-pine"), ("fern", "frosted-fern"), ("hellebore", "winter-rose")]
# ratio folder, largest print size in inches, JPG pixels, PDF pixels (PDF page = the largest print size)
RATIOS = [("2x3", (24, 36), (4400, 6600), (1920, 2880)), ("3x4", (18, 24), (3300, 4400), (1440, 1920)),
          ("4x5", (16, 20), (3200, 4000), (1280, 1600)), ("11x14", (11, 14), (3300, 4200), (1320, 1680)),
          ("ISO-A", (16.54, 23.39), (3508, 4961), (1403, 1984))]
def canvas(name, wpx, hpx):
    a = Image.open(f"art/unified/{name}.png")
    s = min(wpx / a.width, hpx / a.height)
    a = a.resize((round(a.width * s), round(a.height * s)), Image.LANCZOS)
    if s > 1.05: a = a.filter(ImageFilter.UnsharpMask(radius=2.2, percent=60, threshold=2))
    c = Image.new("RGB", (wpx, hpx), BG)
    c.paste(a, ((wpx - a.width) // 2, (hpx - a.height) // 2))
    return c
if __name__ == "__main__":
    from reportlab.pdfgen import canvas as rl
    q = int(sys.argv[1]) if len(sys.argv) > 1 else 76
    only = sys.argv[2] if len(sys.argv) > 2 else None
    for r, (w, h), (jw, jh), (pw, ph) in RATIOS:
        if only and r != only: continue
        os.makedirs(f"out/{r}", exist_ok=True)
        pdf = rl.Canvas(f"out/{r}/winter-botanical-wall-art-{r}.pdf", pagesize=(w * 72, h * 72))
        pdf.setTitle(f"Midnight Blue Winter Botanical Wall Art, set of 3 ({r})"); pdf.setAuthor("Duskwood Designs Co")
        for n, slug in ART:
            p = f"out/{r}/{slug}-{r}.jpg"
            canvas(n, jw, jh).save(p, "JPEG", quality=q, optimize=True, dpi=(300, 300), subsampling=2)
            pp = f"/tmp/_pdf_{r}_{slug}.jpg"
            canvas(n, pw, ph).save(pp, "JPEG", quality=68, optimize=True, subsampling=2)
            pdf.drawImage(pp, 0, 0, w * 72, h * 72); pdf.showPage()
            print(p, os.path.getsize(p) // 1024, "KB")
        pdf.save()
        print(r, "pdf", os.path.getsize(f"out/{r}/winter-botanical-wall-art-{r}.pdf") // 1024, "KB")
