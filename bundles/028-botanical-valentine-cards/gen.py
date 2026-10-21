"""Builds the buyer ZIP and runs the checks. Run build.js and listing.js first."""
import json, os, subprocess, zipfile
Z = "botanical-valentine-cards-printable.zip"
PDFS = [f"botanical-valentine-cards-{k}.pdf" for k in ("US-Letter", "A4")]
with zipfile.ZipFile(Z, "w", zipfile.ZIP_DEFLATED) as z:
    for p in PDFS: z.write(f"bundle/{p}", p)
    z.write("README-LICENSE.txt")
ok = True
def chk(c, m):
    global ok; print(("PASS " if c else "FAIL ") + m); ok &= bool(c)
for p, (w, h) in zip(PDFS, [(612, 792), (595, 842)]):
    info = subprocess.run(["pdfinfo", f"bundle/{p}"], capture_output=True, text=True).stdout
    chk("Pages:           5" in info, f"{p} 5 pages")
    chk(abs(float(info.split("Page size:")[1].split()[0]) - w) < 1.5, f"{p} size")
    fonts = subprocess.run(["pdffonts", f"bundle/{p}"], capture_output=True, text=True).stdout.splitlines()[2:]
    chk(fonts and all(" yes yes yes" in l for l in fonts), f"{p} fonts embedded")
    chk(os.path.getsize(f"bundle/{p}") < 20e6, f"{p} under 20 MB")
chk(sorted(zipfile.ZipFile(Z).namelist()) == sorted(PDFS + ["README-LICENSE.txt"]), "zip contents")
chk(open("README-LICENSE.txt").read() == zipfile.ZipFile(Z).read("README-LICENSE.txt").decode(), "readme in zip current")
chk(os.path.getsize(Z) < 20e6, "zip under 20 MB")
from PIL import Image
j = json.load(open("listing.json"))
for i in j["images"]:
    chk(Image.open(i).size == (3000, 2250), f"{i} 3000x2250")
chk(len(j["title"]) <= 140 and j["title"].startswith("Valentine Gift Tags and Cards Printable"), "title")
chk(len(j["tags"]) == 13 and len(set(j["tags"])) == 13 and all(len(t) <= 20 for t in j["tags"]), "13 unique tags")
chk(j["description"].endswith("Designed with the help of digital and AI tools, and checked by hand."), "disclosure")
chk(j["price"] == 3.5 and j["taxonomy_id"] == 12482 and j["digital_file"] == Z, "price/taxonomy/file")
chk("&#" not in j["description"], "no entities")
print("ALL CHECKS PASS" if ok else "CHECKS FAILED")
