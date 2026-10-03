"""Woodland Christmas Bingo: build everything and run the format checks.

  python3 gen.py          # icons -> cards -> PDFs -> contact sheet -> listing images -> ZIP -> checks

Steps: icons.py (30 code-drawn icons), cards.py (deal + prove 30 unique
cards), build.js (US Letter + A4 PDFs, Playwright/Chromium), contact.js
(contact-sheet.png), thumbs.js (listing-images/), then the buyer ZIP and the
checks from formats/bingo.md. Needs pdfinfo/pdftoppm (poppler) and Node
Playwright (NODE_PATH=$(npm root -g)).
"""
import json, os, re, shutil, subprocess, sys, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ZIP = "woodland-christmas-bingo-printable.zip"
PDFS = {"woodland-christmas-bingo-US-Letter.pdf": (612, 792), "woodland-christmas-bingo-A4.pdf": (595, 842)}
PAGES = 20
DISCLOSURE = "Designed with the help of digital and AI tools, and checked by hand."


def run(*cmd):
    env = dict(os.environ)
    if cmd[0] == "node":
        env["NODE_PATH"] = subprocess.check_output("npm root -g", shell=True, text=True).strip()
    subprocess.run(cmd, cwd=HERE, check=True, env=env)


def build():
    run(sys.executable, "icons.py")
    run(sys.executable, "cards.py")
    run("node", "build.js")
    run("node", "contact.js")
    run("node", "thumbs.js")
    with zipfile.ZipFile(os.path.join(HERE, ZIP), "w", zipfile.ZIP_DEFLATED) as z:
        for f in PDFS:
            z.write(os.path.join(HERE, "bundle", f), f)
        z.write(os.path.join(HERE, "README-LICENSE.txt"), "README-LICENSE.txt")
    shutil.rmtree(os.path.join(HERE, "bundle"))


def check():
    import tempfile
    from PIL import Image
    ok = True
    def res(name, cond, info=""):
        nonlocal ok
        ok &= bool(cond)
        print(f"{'PASS' if cond else 'FAIL'}  {name} {info}")
    # cards
    out = subprocess.check_output([sys.executable, "cards.py", "--check"], cwd=HERE, text=True)
    res("30 unique cards (sets, layouts, no shared line, 24 uses per icon)", json.loads(out)["unique_sets"] == 30, out.replace("\n", " "))
    # zip + pdfs
    with zipfile.ZipFile(os.path.join(HERE, ZIP)) as z:
        names = sorted(z.namelist())
        res("ZIP contents", names == sorted(list(PDFS) + ["README-LICENSE.txt"]), str(names))
        tmp = tempfile.mkdtemp()
        z.extractall(tmp)
    for f, (w, h) in PDFS.items():
        info = subprocess.check_output(["pdfinfo", os.path.join(tmp, f)], text=True)
        pages = int(re.search(r"Pages:\s+(\d+)", info).group(1))
        pw, ph = map(float, re.search(r"Page size:\s+([\d.]+) x ([\d.]+)", info).groups())
        res(f"{f}: {PAGES} pages, {w}x{h} pt", pages == PAGES and abs(pw - w) < 1 and abs(ph - h) < 1, f"({pages} pages, {pw}x{ph})")
        fonts = subprocess.check_output(["pdffonts", os.path.join(tmp, f)], text=True).splitlines()[2:]
        res(f"{f}: all fonts embedded", all(" yes " in l for l in fonts))
        res(f"{f}: size under 20 MB", os.path.getsize(os.path.join(tmp, f)) < 20e6, f"({os.path.getsize(os.path.join(tmp, f)) / 1e6:.1f} MB)")
    shutil.rmtree(tmp)
    # images
    lj = json.load(open(os.path.join(HERE, "listing.json")))
    for im in lj["images"]:
        res(f"{im} is 3000x2250", Image.open(os.path.join(HERE, im)).size == (3000, 2250))
    res("contact-sheet.png exists", os.path.exists(os.path.join(HERE, "contact-sheet.png")))
    # listing
    t = lj["title"]
    caps = [w for w in re.findall(r"[A-Za-z']+", t) if len(w) > 1 and w[:2].isupper()]
    res("title <=140 chars, leads with 'Christmas Bingo'", len(t) <= 140 and t.startswith("Christmas Bingo"), f"({len(t)})")
    res("title has at most 3 words starting with 2 capitals", len(caps) <= 3, str(caps))
    tags = lj["tags"]
    res("13 unique tags, each <=20 chars", len(tags) == 13 and len(set(tags)) == 13 and max(map(len, tags)) <= 20,
        f"(longest {max(map(len, tags))})")
    res("description ends with disclosure line", lj["description"].endswith(DISCLOSURE))
    res("no HTML entities", "&#" not in json.dumps(lj) and "&amp;" not in json.dumps(lj))
    res("taxonomy_id 1350, price 3.5, digital_file", lj["taxonomy_id"] == 1350 and lj["price"] == 3.5 and lj["digital_file"] == ZIP)
    print("ALL CHECKS PASS" if ok else "SOME CHECKS FAILED")
    return ok


if __name__ == "__main__":
    if "--check" not in sys.argv:
        build()
    sys.exit(0 if check() else 1)
