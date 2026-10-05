"""Christmas Woodland Coloring Pages: build everything and run the format checks (formats/coloring.md).

  python3 gen.py           # line art -> PDFs -> coloured examples -> listing images -> contact sheet -> ZIP -> checks
  python3 gen.py --skip-art  # same, but keep the existing art/svg + art/mask (process.py takes ~5 min)
  python3 gen.py --check   # checks only

Steps: process.py (art/raw AI drafts -> bold closed line art, art/svg + art/mask + art/stats.json),
build.js (20-page PDFs in US Letter and A4; Playwright/Chromium), colorize.py (coloured examples
for the photos only), thumbs.js (listing images), contact sheet, buyer ZIP, checks.
Needs scipy, shapely, pillow, potracer, numpy, poppler (pdfinfo/pdffonts/pdftotext/pdftoppm) and
Node Playwright (NODE_PATH=$(npm root -g)). No AI calls: the drafts are already in art/raw.
"""
import json, os, re, shutil, subprocess, sys, tempfile, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ZIP = "christmas-woodland-coloring-pages-printable.zip"
PDFS = {  # file: (width pt, height pt, pages)
    "christmas-woodland-coloring-pages-US-Letter.pdf": (612, 792, 20),
    "christmas-woodland-coloring-pages-A4.pdf": (595.28, 841.89, 20),
}
DISCLOSURE = "Designed with the help of digital and AI tools, and checked by hand."
LEAD = "Christmas Coloring Pages"
TAXONOMY = 339  # Books, Movies & Music > Books > Coloring Books
PRICE = 3.99
MIN_REGION_MM2 = 10.0     # a colourable space on the printed page (process.py fills anything under 12 mm2)
MIN_SPACES = 15           # colourable spaces per page
MAX_NOOKS = 16            # spaces under MIN_REGION_MM2: pinch points where two thick lines meet, under 1 mm wide.
MAX_NOOK_AREA_PCT = 0.25  # They exist in hand-style line art at any resolution, so they are bounded, not banned:
                          # at most this many per page and this share of the page's colourable area.
MIN_STROKE_MM = 1.5
MIN_MARGIN_MM = 12.0      # ink to paper edge (home printers clip ~6 mm)
CHECK_DPI = 200


def run(*cmd):
    env = dict(os.environ)
    if cmd[0] == "node":
        env["NODE_PATH"] = subprocess.check_output("npm root -g", shell=True, text=True).strip()
    subprocess.run(cmd, cwd=HERE, check=True, env=env)


def contact_sheet(pdf):
    """All 20 Letter pages at ~1/4 size, with each page's stats underneath."""
    from PIL import Image, ImageDraw, ImageFont
    stats = json.load(open(os.path.join(HERE, "art", "stats.json")))
    tmp = tempfile.mkdtemp()
    subprocess.run(["pdftoppm", "-r", "60", "-png", pdf, os.path.join(tmp, "p")], check=True)
    files = sorted(os.listdir(tmp))
    w, h = Image.open(os.path.join(tmp, files[0])).size
    cols, cap = 5, 64
    sheet = Image.new("RGB", (cols * (w + 20) + 20, 4 * (h + cap + 20) + 90), "#d8d2dc")
    d = ImageDraw.Draw(sheet)
    try:
        f = ImageFont.truetype(os.path.join(HERE, "fonts", "Nunito-700.ttf"), 17)
        fb = ImageFont.truetype(os.path.join(HERE, "fonts", "Fraunces-900.ttf"), 40)
    except OSError:
        f = fb = ImageFont.load_default()
    d.text((20, 18), "Christmas Woodland Coloring Pages: 20 pages (US Letter, 60 dpi)", font=fb, fill="#2c1b36")
    for i, (fn, (slug, st)) in enumerate(zip(files, stats.items())):
        x, y = 20 + (i % cols) * (w + 20), 90 + (i // cols) * (h + cap + 20)
        sheet.paste(Image.open(os.path.join(tmp, fn)), (x, y))
        d.text((x, y + h + 4), f"{slug}", font=f, fill="#2c1b36")
        d.text((x, y + h + 24), f"{st['regions']} spaces, smallest {st['smallest_region_mm2']} mm2", font=f, fill="#2f4a3a")
        d.text((x, y + h + 44), f"line {st['stroke_after_mm']} mm (was {st['stroke_before_mm']})", font=f, fill="#2f4a3a")
    sheet.save(os.path.join(HERE, "contact-sheet.png"), optimize=True)
    shutil.rmtree(tmp)


def build(skip_art):
    if not skip_art:
        run(sys.executable, "process.py")
    run("node", "build.js")
    run(sys.executable, "colorize.py")
    run("node", "thumbs.js")
    contact_sheet(os.path.join(HERE, "bundle", "christmas-woodland-coloring-pages-US-Letter.pdf"))
    with zipfile.ZipFile(os.path.join(HERE, ZIP), "w", zipfile.ZIP_DEFLATED) as z:
        for f in PDFS:
            z.write(os.path.join(HERE, "bundle", f), f)
        z.write(os.path.join(HERE, "README-LICENSE.txt"), "README-LICENSE.txt")
    shutil.rmtree(os.path.join(HERE, "bundle"))


def page_regions(png, dpi=CHECK_DPI):
    """A rendered page: (spaces >= MIN_REGION_MM2, nooks under it, nook area %, smallest space, ink margin mm, ink %).

    The ink is closed by one pixel first: at any render resolution two lines that meet leave a
    hairline white nook, which is not a space anyone colours."""
    import numpy as np
    from PIL import Image
    from scipy import ndimage as nd
    a = np.array(Image.open(png).convert("L")) < 128
    mm = dpi / 25.4
    ink = nd.binary_closing(a, np.ones((3, 3)))
    lab, n = nd.label(~ink)
    edge = set(lab[0, :]) | set(lab[-1, :]) | set(lab[:, 0]) | set(lab[:, -1])   # the page margin
    sz = np.array([s for i, s in enumerate(nd.sum(~ink, lab, range(1, n + 1)) / mm ** 2, 1) if i not in edge])
    small = sz < MIN_REGION_MM2
    ys, xs = np.nonzero(a)
    H, W = a.shape
    margin = min(xs.min(), ys.min(), W - 1 - xs.max(), H - 1 - ys.max()) / mm
    return (int((~small).sum()), int(small.sum()), 100 * sz[small].sum() / sz.sum(),
            float(sz[~small].min()), margin, a.mean() * 100)


def page_hash(png):
    """Average hash of the page's art only (trimmed to the ink), so the shared frame doesn't mask differences."""
    import numpy as np
    from PIL import Image
    a = np.array(Image.open(png).convert("L")) < 128
    ys, xs = np.nonzero(a)
    crop = Image.fromarray((a[ys.min():ys.max(), xs.min():xs.max()] * 255).astype(np.uint8))
    g = np.array(crop.resize((24, 24), Image.BILINEAR), float)
    return (g > g.mean()).flatten()


def check():
    from PIL import Image
    ok = True

    def res(name, cond, info=""):
        nonlocal ok
        ok &= bool(cond)
        print(f"{'PASS' if cond else 'FAIL'}  {name} {info}")

    S = json.load(open(os.path.join(HERE, "subjects.json")))["pages"]
    res("20 distinct subjects", len(S) == 20 and len({s[0] for s in S}) == 20 and len({s[1] for s in S}) == 20)
    stats = json.load(open(os.path.join(HERE, "art", "stats.json")))
    res("art/stats.json covers all 20 pages", sorted(stats) == sorted(s[0] for s in S))
    res(f"line art: median stroke >= {MIN_STROKE_MM} mm on every page", all(v["stroke_after_mm"] >= MIN_STROKE_MM for v in stats.values()),
        f"(min {min(v['stroke_after_mm'] for v in stats.values())} mm)")
    res("line art: no space under 12 mm2 (process.py)", all(v["smallest_region_mm2"] >= 12 for v in stats.values()),
        f"(min {min(v['smallest_region_mm2'] for v in stats.values())} mm2)")
    with zipfile.ZipFile(os.path.join(HERE, ZIP)) as z:
        names = sorted(z.namelist())
        res("ZIP contents", names == sorted(list(PDFS) + ["README-LICENSE.txt"]), str(names))
        tmp = tempfile.mkdtemp()
        z.extractall(tmp)
    for f, (w, h, n) in PDFS.items():
        p = os.path.join(tmp, f)
        info = subprocess.check_output(["pdfinfo", p], text=True)
        pages = int(re.search(r"Pages:\s+(\d+)", info).group(1))
        pw, ph = map(float, re.search(r"Page size:\s+([\d.]+) x ([\d.]+)", info).groups())
        res(f"{f}: {n} pages, {w}x{h} pt", pages == n and abs(pw - w) < 1 and abs(ph - h) < 1, f"({pages} pages, {pw}x{ph})")
        fonts = subprocess.check_output(["pdffonts", p], text=True).splitlines()[2:]
        text = subprocess.check_output(["pdftotext", p, "-"], text=True)
        res(f"{f}: no text on the pages (no fonts, no extractable text)", not fonts and not text.strip(), f"({len(fonts)} fonts)")
        res(f"{f}: under 20 MB", os.path.getsize(p) < 20e6, f"({os.path.getsize(p) / 1e6:.1f} MB)")
        rd = os.path.join(tmp, f[:-4])
        os.makedirs(rd)
        subprocess.run(["pdftoppm", "-r", str(CHECK_DPI), "-gray", p, os.path.join(rd, "p")], check=True)
        bad = []
        worst = (1e9, 1e9, 0, 0.0)
        for pg in sorted(os.listdir(rd)):
            spaces, nooks, nookpct, small, margin, ink = page_regions(os.path.join(rd, pg))
            worst = (min(worst[0], small), min(worst[1], margin), max(worst[2], nooks), max(worst[3], nookpct))
            if spaces < MIN_SPACES or small < MIN_REGION_MM2 or margin < MIN_MARGIN_MM \
                    or nooks > MAX_NOOKS or nookpct > MAX_NOOK_AREA_PCT or not (8 < ink < 32):
                bad.append(f"{pg}: {spaces} spaces, smallest {small:.0f} mm2, {nooks} nooks ({nookpct:.2f}%), "
                           f"margin {margin:.0f} mm, ink {ink:.0f}%")
        res(f"{f}: every page has >= {MIN_SPACES} colourable spaces, all >= {MIN_REGION_MM2} mm2, <= {MAX_NOOKS} hairline nooks "
            f"(<= {MAX_NOOK_AREA_PCT}% of the art), art >= {MIN_MARGIN_MM} mm from the edge, ink 8-32% (rendered at {CHECK_DPI} dpi)",
            not bad, f"(smallest space {worst[0]:.0f} mm2, margin {worst[1]:.0f} mm, worst page {worst[2]} nooks / {worst[3]:.2f}%)"
            + ("\n      " + "\n      ".join(bad) if bad else ""))
        if f.endswith("Letter.pdf"):
            hs = [page_hash(os.path.join(rd, pg)) for pg in sorted(os.listdir(rd))]
            dmin = min((hs[i] != hs[j]).sum() for i in range(20) for j in range(i + 1, 20))
            res("no two pages alike (24x24 average hash of the art, >= 60 of 576 bits differ)", dmin >= 60, f"(closest pair {dmin})")
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
    res(f"taxonomy_id {TAXONOMY}, price {PRICE}, digital_file", lj["taxonomy_id"] == TAXONOMY and lj["price"] == PRICE and lj["digital_file"] == ZIP)
    md = open(os.path.join(HERE, "LISTING.md")).read()
    res("LISTING.md has the same title, tags and description", t in md and ", ".join(tags) in md and lj["description"] in md)
    res("PROMPTS.md present (AI drafts used)", os.path.exists(os.path.join(HERE, "PROMPTS.md")))
    print("ALL CHECKS PASS" if ok else "SOME CHECKS FAILED")
    return ok


if __name__ == "__main__":
    if "--check" not in sys.argv:
        build("--skip-art" in sys.argv)
    sys.exit(0 if check() else 1)
