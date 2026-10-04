"""Woodland Christmas cross-stitch pattern: build everything and run the format checks (formats/cross-stitch.md).

  python3 gen.py           # motifs -> stitched renders -> PDFs -> listing images -> ZIP -> checks
  python3 gen.py --check   # checks only

Steps: motifs.py (12 pixel-grid motifs, motifs.json + contact-sheet.png), stitch.py (stitched-look hoops
for the listing images, art/), build.js (28-page pattern PDF in US Letter and A4; Playwright/Chromium),
thumbs.js (listing images), then the buyer ZIP and the checks. Needs poppler (pdfinfo, pdffonts,
pdftotext, pdftoppm) and Node Playwright (NODE_PATH=$(npm root -g)).
"""
import json, os, re, shutil, subprocess, sys, tempfile, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ZIP = "woodland-christmas-cross-stitch-pattern.zip"
PDFS = {  # file: (width pt, height pt)
    "woodland-christmas-cross-stitch-US-Letter.pdf": (612, 792),
    "woodland-christmas-cross-stitch-A4.pdf": (595.28, 841.89),
}
PAGES = 28
DISCLOSURE = "Designed with the help of digital and AI tools, and checked by hand."
LEAD = "Christmas Cross Stitch Pattern"
TAXONOMY = 6343  # Craft Supplies & Tools > Patterns & How To > Patterns & Blueprints


def run(*cmd):
    env = dict(os.environ)
    if cmd[0] == "node":
        env["NODE_PATH"] = subprocess.check_output("npm root -g", shell=True, text=True).strip()
    subprocess.run(cmd, cwd=HERE, check=True, env=env)


def build():
    run(sys.executable, "motifs.py")
    run(sys.executable, "stitch.py")
    run("node", "build.js")
    run("node", "thumbs.js")
    with zipfile.ZipFile(os.path.join(HERE, ZIP), "w", zipfile.ZIP_DEFLATED) as z:
        for f in PDFS:
            z.write(os.path.join(HERE, "bundle", f), f)
        z.write(os.path.join(HERE, "README-LICENSE.txt"), "README-LICENSE.txt")
    shutil.rmtree(os.path.join(HERE, "bundle"))


def check():
    from PIL import Image
    sys.path.insert(0, HERE)
    import motifs as MO
    ok = True

    def res(name, cond, info=""):
        nonlocal ok
        ok &= bool(cond)
        print(f"{'PASS' if cond else 'FAIL'}  {name} {info}")

    D = json.load(open(os.path.join(HERE, "motifs.json")))
    pal = D["palette"]
    # --- the charts themselves
    res("motifs.py --check: sizes 23-35, 3-6 colours, no stray stitches, mono inside colour shape, one-colour readable "
        "(keeps >= 65% of stitches, no enclosed gap > 25% of the motif, no new parts > 6 stitches)", MO.check(D, verbose=False))
    for m in D["motifs"]:
        kept, gap, extra = MO.readability(m)
        print(f"      {m['key']:<10} one-colour keeps {kept:.0%}, largest gap {gap:.0%}" + (f", new small parts {extra} (look: pupils/eyes only)" if extra else ""))
    R = MO.ranges(D["motifs"])
    res("size ranges in motifs.json match the grids", D.get("ranges") == R, f"({R['stitches']}; {R['in14']} on 14-count, {R['in18']} on 18-count)")
    res("12 motifs", len(D["motifs"]) == 12, str([m["key"] for m in D["motifs"]]))
    res("shared palette of 8-10 DMC colours, each with a number, name, colour and symbol",
        8 <= len(pal) <= 10 and all(p["dmc"] and p["name"] and re.match(r"#[0-9a-f]{6}$", p["hex"]) and p["symbol"] for p in pal.values()),
        f"({len(pal)}: {', '.join(p['dmc'] for p in pal.values())})")
    res("palette DMC numbers unique", len({p["dmc"] for p in pal.values()}) == len(pal))
    for m in D["motifs"]:
        c, mo = m["colour"], m["mono"]
        dims = len(c) == m["h"] and all(len(r) == m["w"] for r in c) and len(mo) == m["h"] and all(len(r) == m["w"] for r in mo)
        cells = [ch for r in c for ch in r if ch != "."]
        every = all(ch in pal and pal[ch]["symbol"] for ch in cells) and all(ch in ".X" for r in mo for ch in r)
        counts = {k: cells.count(k) for k in set(cells)}
        syms = [pal[k]["symbol"] for k in m["counts"]]
        res(f"{m['n']:2d} {m['key']}: grid {m['w']}x{m['h']}, every stitched cell has a palette colour + symbol, key symbols unique, counts match",
            dims and every and len(set(syms)) == len(syms) and counts == m["counts"] and m["mono_count"] == sum(r.count("X") for r in mo),
            f"({len(cells)} colour / {m['mono_count']} one-colour stitches)")
    # --- ZIP and PDFs
    with zipfile.ZipFile(os.path.join(HERE, ZIP)) as z:
        names = sorted(z.namelist())
        res("ZIP holds exactly both PDFs + README-LICENSE.txt", names == sorted(list(PDFS) + ["README-LICENSE.txt"]), str(names))
        tmp = tempfile.mkdtemp()
        z.extractall(tmp)
    for f, (w, h) in PDFS.items():
        p = os.path.join(tmp, f)
        info = subprocess.check_output(["pdfinfo", p], text=True)
        pages = int(re.search(r"Pages:\s+(\d+)", info).group(1))
        sizes = set()
        for line in subprocess.check_output(["pdfinfo", "-f", "1", "-l", str(pages), p], text=True).splitlines():
            mm = re.match(r"Page\s+\d+ size:\s+([\d.]+) x ([\d.]+)", line)
            if mm:
                sizes.add((round(float(mm.group(1))), round(float(mm.group(2)))))
        res(f"{f}: {PAGES} pages, every page {round(w)}x{round(h)} pt", pages == PAGES and sizes == {(round(w), round(h))}, f"({pages} pages, sizes {sizes})")
        fonts = subprocess.check_output(["pdffonts", p], text=True).splitlines()[2:]
        res(f"{f}: all fonts embedded", fonts and all(" yes " in l for l in fonts), f"({len(fonts)} fonts)")
        res(f"{f}: under 20 MB", os.path.getsize(p) < 20e6, f"({os.path.getsize(p) / 1e6:.1f} MB)")
        txt = subprocess.check_output(["pdftotext", "-layout", p, "-"], text=True)
        pg = txt.split("\f")
        okc = True
        for m in D["motifs"]:
            for page_no, kind in ((4 + m["n"], "Colour chart"), (16 + m["n"], "One-colour chart")):
                t = pg[page_no - 1]
                if not (m["title"] in t and kind.upper().replace(" ", "") in t.upper().replace(" ", "")
                        and re.search(rf"Stitch count:\s*{m['w']}\s*W\s*×\s*{m['h']}\s*H", t)):
                    okc = False; print(f"      page {page_no}: {m['title']} / {kind} / {m['w']}x{m['h']} not found")
        res(f"{f}: chart pages 5-28 carry the right motif, version and stitch count", okc)
        flat = re.sub(r"\s+", " ", subprocess.check_output(["pdftotext", p, "-"], text=True))
        res(f"{f}: size copy uses the computed ranges, fat quarter = 9 pieces, no stale names",
            R["stitches"] in flat and R["in14"] in flat and R["in18"] in flat and "cuts 9 pieces" in flat
            and "fat quarter for all 12" not in flat and "Snowy Owl" not in flat and "2 to 2.5 in" not in flat)
    shutil.rmtree(tmp)
    readme = open(os.path.join(HERE, "README-LICENSE.txt")).read()
    res("README: files, page map, licence (personal use, small-quantity finished items, no sharing)",
        all(s in readme for s in list(PDFS) + ["Pages 5-16", "Pages 17-28", "up to 50 finished pieces", "You may NOT share"]))
    rflat = re.sub(r"\s+", " ", readme)
    rows_ok = all(re.search(rf"{m['n']} {re.escape(m['title'])} +{m['w']} x {m['h']} +{m['w'] / 14:.1f} x {m['h'] / 14:.1f} in", readme) for m in D["motifs"])
    res("README: motif table matches the grids; ranges and fat quarter correct", rows_ok and R["stitches"] in rflat and R["in14"] in rflat
        and R["in18"] in rflat and "cuts 9 pieces" in rflat and "Snowy" + " Owl" not in readme)
    # --- listing
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
    res("no HTML entities, plain apostrophes", not re.search(r"&#\d+;|&amp;|&quot;|&lt;|&gt;|&apos;", blob) and "’" not in blob and "‘" not in blob)
    res("description ends with disclosure line", lj["description"].endswith(DISCLOSURE))
    res(f"taxonomy_id {TAXONOMY}, price 3.5, digital_file, type fields",
        lj["taxonomy_id"] == TAXONOMY and lj["price"] == 3.5 and lj["digital_file"] == ZIP and lj["who_made"] == "i_did"
        and lj["when_made"] == "2020_2026" and lj["is_supply"] is False)
    desc = lj["description"]
    res("description: computed size + stitch ranges, fat quarter = 9, no stale copy",
        R["stitches"] in desc and R["in14"] in desc and R["in18"] in desc and "cuts 9 pieces" in desc
        and "snowy owl" not in desc.lower() and "2 to 2.5 in" not in desc and "25 × 25" not in desc)
    ai = os.path.exists(os.path.join(HERE, "art", "bg-scene.png"))
    res("AI background recorded in PROMPTS.md (image 1 is a lifestyle composite)", not ai or os.path.exists(os.path.join(HERE, "PROMPTS.md")))
    md = open(os.path.join(HERE, "LISTING.md")).read()
    res("LISTING.md has the same title, tags and description", t in md and ", ".join(tags) in md and lj["description"] in md)
    print("ALL CHECKS PASS" if ok else "SOME CHECKS FAILED")
    return ok


if __name__ == "__main__":
    if "--check" not in sys.argv:
        build()
    sys.exit(0 if check() else 1)
