"""Small Autumn Moments: build everything and run the format checks (formats/printable.md).

  python3 gen.py           # icons -> stickers -> PDFs + PNG -> contact sheet -> listing images -> ZIP -> checks
  python3 gen.py --check   # checks only

Steps: icons.py (22 code-drawn icons), stickers.py (20-sticker print-then-cut
sheet + proof), build.js (checklist + sticker PDFs in US Letter and A4, and the
transparent PNG; Playwright/Chromium), contact.js, thumbs.js, then the buyer
ZIP and the checks. Needs pdfinfo/pdffonts/pdftoppm (poppler) and Node
Playwright (NODE_PATH=$(npm root -g)).
"""
import json, os, re, shutil, subprocess, sys, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ZIP = "small-autumn-moments-printable.zip"
PNG = "small-autumn-moments-stickers-print-then-cut.png"
PDFS = {  # file: (width pt, height pt, pages)
    "small-autumn-moments-checklist-US-Letter.pdf": (612, 792, 4),
    "small-autumn-moments-checklist-A4.pdf": (595.28, 841.89, 4),
    "small-autumn-moments-stickers-US-Letter.pdf": (612, 792, 1),
    "small-autumn-moments-stickers-A4.pdf": (595.28, 841.89, 1),
}
DISCLOSURE = "Designed with the help of digital and AI tools, and checked by hand."
LEAD = "Fall Bucket List Printable"
TAXONOMY = 354  # Paper & Party Supplies > Paper > Calendars & Planners


def run(*cmd):
    env = dict(os.environ)
    if cmd[0] == "node":
        env["NODE_PATH"] = subprocess.check_output("npm root -g", shell=True, text=True).strip()
    subprocess.run(cmd, cwd=HERE, check=True, env=env)


def build():
    from PIL import Image
    run(sys.executable, "icons.py")
    run(sys.executable, "stickers.py")
    run("node", "build.js")
    png = os.path.join(HERE, "bundle", PNG)
    Image.open(png).save(png, dpi=(300, 300), optimize=True)   # Chromium writes no DPI tag
    run("node", "contact.js")
    run("node", "thumbs.js")
    with zipfile.ZipFile(os.path.join(HERE, ZIP), "w", zipfile.ZIP_DEFLATED) as z:
        for f in list(PDFS) + [PNG]:
            z.write(os.path.join(HERE, "bundle", f), f)
        z.write(os.path.join(HERE, "README-LICENSE.txt"), "README-LICENSE.txt")
    shutil.rmtree(os.path.join(HERE, "bundle"))


def lj_desc():
    return json.load(open(os.path.join(HERE, "listing.json")))["description"]


def check():
    import tempfile
    from PIL import Image
    ok = True

    def res(name, cond, info=""):
        nonlocal ok
        ok &= bool(cond)
        print(f"{'PASS' if cond else 'FAIL'}  {name} {info}")

    out = subprocess.run([sys.executable, "stickers.py", "--check"], cwd=HERE, text=True, capture_output=True)
    res("sticker sheet: 20 stickers inside 6.75x9.25 in, one cut piece each, gaps >= 0.15 in", out.returncode == 0, out.stdout.strip())
    with zipfile.ZipFile(os.path.join(HERE, ZIP)) as z:
        names = sorted(z.namelist())
        res("ZIP contents", names == sorted(list(PDFS) + [PNG, "README-LICENSE.txt"]), str(names))
        tmp = tempfile.mkdtemp()
        z.extractall(tmp)
    for f, (w, h, n) in PDFS.items():
        p = os.path.join(tmp, f)
        info = subprocess.check_output(["pdfinfo", p], text=True)
        pages = int(re.search(r"Pages:\s+(\d+)", info).group(1))
        pw, ph = map(float, re.search(r"Page size:\s+([\d.]+) x ([\d.]+)", info).groups())
        res(f"{f}: {n} pages, {w}x{h} pt", pages == n and abs(pw - w) < 1 and abs(ph - h) < 1, f"({pages} pages, {pw}x{ph})")
        fonts = subprocess.check_output(["pdffonts", p], text=True).splitlines()[2:]
        res(f"{f}: fonts embedded", fonts and all(" yes " in l for l in fonts), f"({len(fonts)} fonts)")
        res(f"{f}: under 20 MB", os.path.getsize(p) < 20e6, f"({os.path.getsize(p) / 1e6:.1f} MB)")
    im = Image.open(os.path.join(tmp, PNG))
    dpi = im.info.get("dpi", (0, 0))
    res("PNG 2025x2775 px (6.75x9.25 in), 300 DPI, RGBA", im.size == (2025, 2775) and round(dpi[0]) == 300 and im.mode == "RGBA",
        f"({im.size}, {dpi}, {im.mode})")
    a = im.getchannel("A")
    corners = [a.getpixel(c) for c in ((0, 0), (2024, 0), (0, 2774), (2024, 2774), (1012, 5))]
    hist = a.histogram()
    res("PNG background transparent, stickers opaque", max(corners) == 0 and hist[0] > 0.3 * 2025 * 2775 and hist[255] > 0.3 * 2025 * 2775,
        f"(transparent {hist[0] / (2025 * 2775):.0%}, opaque {hist[255] / (2025 * 2775):.0%})")
    x0, y0, x1, y1 = a.getbbox()
    bw, bh = (x1 - x0) / 300, (y1 - y0) / 300
    by_h = (bw * 9.25 / bh, 9.25)
    res("PNG trimmed art fits 6.75x9.25 in when set to height 9.25 in", by_h[0] <= 6.75,
        f"(trimmed {x1 - x0}x{y1 - y0} px; height 9.25 -> width {by_h[0]:.2f} in; width 6.75 -> height {bh * 6.75 / bw:.2f} in)")
    readme = open(os.path.join(HERE, "README-LICENSE.txt")).read()
    res("README + description: height-9.25 Cricut step, what-you-need line, no 'width 6.75' step",
        "HEIGHT to\n     9.25 in" in readme and "set the height to 9.25 in" in lj_desc() and "sticker paper, plus either scissors" in readme
        and "sticker paper, plus either scissors" in lj_desc() and "width to 6.75" not in readme + lj_desc())
    shutil.rmtree(tmp)
    lj = json.load(open(os.path.join(HERE, "listing.json")))
    for img in lj["images"]:
        res(f"{img} is 3000x2250", Image.open(os.path.join(HERE, img)).size == (3000, 2250))
    res("4 listing images", len(lj["images"]) == 4)
    res("contact-sheet.png exists", os.path.exists(os.path.join(HERE, "contact-sheet.png")))
    t = lj["title"]
    caps = [w for w in re.findall(r"[A-Za-z']+", t) if len(w) > 1 and w[:2].isupper()]
    res(f"title <=140 chars, leads with '{LEAD}'", len(t) <= 140 and t.startswith(LEAD), f"({len(t)})")
    res("title: at most 3 words starting with 2 capitals, at most one '&'", len(caps) <= 3 and t.count("&") <= 1, f"{caps} &x{t.count('&')}")
    tags = lj["tags"]
    res("13 unique tags, each <=20 chars", len(tags) == 13 and len(set(tags)) == 13 and max(map(len, tags)) <= 20, f"(longest {max(map(len, tags))})")
    blob = json.dumps(lj, ensure_ascii=False)
    res("no HTML entities, plain apostrophes", not re.search(r"&#\d+;|&amp;|&quot;|&lt;|&gt;", blob) and "’" not in blob)
    res("description ends with disclosure line", lj["description"].endswith(DISCLOSURE))
    res(f"taxonomy_id {TAXONOMY}, price 3.5, digital_file", lj["taxonomy_id"] == TAXONOMY and lj["price"] == 3.5 and lj["digital_file"] == ZIP)
    md = open(os.path.join(HERE, "LISTING.md")).read()
    res("LISTING.md has the same title and tags", t in md and ", ".join(tags) in md)
    print("ALL CHECKS PASS" if ok else "SOME CHECKS FAILED")
    return ok


if __name__ == "__main__":
    if "--check" not in sys.argv:
        build()
    sys.exit(0 if check() else 1)
