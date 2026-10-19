"""Builds the buyer ZIP and runs the checks. Run build.js and listing.js first."""
import json, os, subprocess, zipfile
Z = "thanksgiving-place-cards-printable.zip"
PDFS = [f"thanksgiving-place-cards-{k}.pdf" for k in ("US-Letter", "A4")]
with zipfile.ZipFile(Z, "w", zipfile.ZIP_DEFLATED) as z:
    for p in PDFS: z.write(f"bundle/{p}", p)
    z.write("README-LICENSE.txt")
ok = True
def chk(c, m):
    global ok; print(("PASS " if c else "FAIL ") + m); ok &= bool(c)
for p, (w, h) in zip(PDFS, [(612, 792), (595, 842)]):
    info = subprocess.run(["pdfinfo", f"bundle/{p}"], capture_output=True, text=True).stdout
    chk("Pages:           5" in info, f"{p} 5 pages")
    chk(f"{w} x {h}" in info or f"{w}.0 x {h}" in info or abs(float(info.split("Page size:")[1].split()[0]) - w) < 1.5, f"{p} size")
    fonts = subprocess.run(["pdffonts", f"bundle/{p}"], capture_output=True, text=True).stdout.splitlines()[2:]
    chk(fonts and all(" yes yes yes" in l for l in fonts), f"{p} fonts embedded")
    chk(os.path.getsize(f"bundle/{p}") < 20e6, f"{p} under 20 MB")
chk(sorted(zipfile.ZipFile(Z).namelist()) == sorted(PDFS + ["README-LICENSE.txt"]), "zip contents")
from PIL import Image
for i in json.load(open("listing.json"))["images"]:
    chk(Image.open(i).size == (3000, 2250), f"{i} 3000x2250")
j = json.load(open("listing.json"))
chk(len(j["title"]) <= 140 and j["title"].startswith("Thanksgiving Place Cards Printable"), "title")
chk(len(j["tags"]) == 13 and len(set(j["tags"])) == 13 and all(len(t) <= 20 for t in j["tags"]), "13 unique tags")
chk(j["description"].endswith("Designed with the help of digital and AI tools, and checked by hand."), "disclosure")
chk(j["price"] == 3.5 and j["taxonomy_id"] == 2102 and j["digital_file"] == Z, "price/taxonomy/file")
chk("&#" not in j["description"] and j["title"].count("&") == 0, "no entities")
print("ALL CHECKS PASS" if ok else "CHECKS FAILED")
