"""Builds the buyer ZIP and runs the checks. Run mk.py (JPGs + PDFs) and listing_images.py first. `python3 gen.py --check` re-runs only the checks."""
import json, os, subprocess, sys, zipfile
from PIL import Image
Z = "winter-botanical-wall-art-set-of-3.zip"
RAT = {"2x3": ((4400, 6600), (24, 36)), "3x4": ((3300, 4400), (18, 24)), "4x5": ((3200, 4000), (16, 20)), "11x14": ((3300, 4200), (11, 14)), "ISO-A": ((3508, 4961), (16.54, 23.39))}
SL = ["frosted-pine", "frosted-fern", "winter-rose"]
if "--check" not in sys.argv:
    with zipfile.ZipFile(Z, "w", zipfile.ZIP_STORED) as z:
        for r in RAT:
            for s in SL: z.write(f"out/{r}/{s}-{r}.jpg", f"JPG/{r}/{s}-{r}.jpg")
            z.write(f"out/{r}/winter-botanical-wall-art-{r}.pdf", f"PDF/winter-botanical-wall-art-{r}.pdf")
        z.write("README-LICENSE.txt")
ok = True
def chk(c, m):
    global ok; print(("PASS " if c else "FAIL ") + m); ok &= bool(c)
names = zipfile.ZipFile(Z).namelist()
exp = [f"JPG/{r}/{s}-{r}.jpg" for r in RAT for s in SL] + [f"PDF/winter-botanical-wall-art-{r}.pdf" for r in RAT] + ["README-LICENSE.txt"]
chk(sorted(names) == sorted(exp), "zip holds 15 JPG + 5 PDF + README")
chk(os.path.getsize(Z) < 19.8e6, f"zip {os.path.getsize(Z)/1e6:.1f} MB (<20 MB Etsy limit)")
for r, (px, inch) in RAT.items():
    for s in SL:
        im = Image.open(f"out/{r}/{s}-{r}.jpg")
        chk(im.size == px and im.format == "JPEG" and round(im.info["dpi"][0]) == 300, f"{s}-{r}.jpg {im.size} 300 DPI tag")
    pdf = f"out/{r}/winter-botanical-wall-art-{r}.pdf"
    info = subprocess.run(["pdfinfo", pdf], capture_output=True, text=True).stdout
    chk("Pages:           3" in info, f"{r} pdf 3 pages")
    wpt = float(info.split("Page size:")[1].split()[0]); chk(abs(wpt - inch[0] * 72) < 1.5, f"{r} pdf page width {wpt:.0f} pt")
    chk(abs(px[0] / px[1] - inch[0] / inch[1]) < 0.002, f"{r} JPG ratio matches print size")
j = json.load(open("listing.json"))
chk(len(j["title"]) <= 140 and j["title"].startswith("Winter Wall Art Set of 3"), "title")
chk(sum(1 for w in j["title"].split() if w[:2].isupper()) <= 3 and j["title"].count("&") <= 1, "title caps/&")
chk(len(j["tags"]) == 13 and len(set(j["tags"])) == 13 and all(len(t) <= 20 for t in j["tags"]), "13 unique tags")
chk(j["description"].endswith("Designed with the help of digital and AI tools, and checked by hand."), "disclosure")
chk(j["price"] == 5.0 and j["taxonomy_id"] == 2078 and j["digital_file"] == Z, "price/taxonomy/file")
chk("&#" not in j["description"] and "’" not in j["description"], "no entities / curly quotes")
chk(open("LISTING.md").read().count(j["title"]) == 1 and j["description"] in open("LISTING.md").read(), "LISTING.md matches listing.json")
for i in j["images"]: chk(Image.open(i).size == (3000, 2250), f"{i} 3000x2250")
print("ALL CHECKS PASS" if ok else "CHECKS FAILED")
