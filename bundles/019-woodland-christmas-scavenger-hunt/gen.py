"""Woodland Christmas Scavenger Hunt: build everything and run the format checks.

  python3 gen.py          # icons -> PDFs -> contact sheet -> listing images -> ZIP -> checks
  python3 gen.py --check  # checks only

Steps: icons.py (the 30 code-drawn icons of the approved 010 bingo, reused),
build.js (US Letter + A4 PDFs, 8 pages, stops on any overflow or wrapped rhyme
line), contact.js (contact-sheet.png), thumbs.js (listing-images/), then the
buyer ZIP and the checks from formats/bingo.md adapted to a scavenger hunt.
Needs pdfinfo/pdffonts/pdftoppm (poppler) and Node Playwright (NODE_PATH=$(npm root -g)).
"""
import json, os, re, shutil, subprocess, sys, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ZIP = "woodland-christmas-scavenger-hunt-printable.zip"
PDFS = {"woodland-christmas-scavenger-hunt-US-Letter.pdf": (612, 792), "woodland-christmas-scavenger-hunt-A4.pdf": (595, 842)}
PAGES = 8
DISCLOSURE = "Designed with the help of digital and AI tools, and checked by hand."


def run(*cmd):
    env = dict(os.environ)
    if cmd[0] == "node":
        env["NODE_PATH"] = subprocess.check_output("npm root -g", shell=True, text=True).strip()
    subprocess.run(cmd, cwd=HERE, check=True, env=env)


def build():
    run(sys.executable, "icons.py")
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

    cj = json.load(open(os.path.join(HERE, "clues.json")))
    clues = cj["clues"]
    codes = [c["code"] for c in clues]
    res("15 clues, codes A-O unique, 8 lines each", len(clues) == 15 and codes == list("ABCDEFGHIJKLMNO")
        and all(len(c["lines"]) == 8 for c in clues) and len(cj["treasure"]["lines"]) == 8)
    res("15 different hiding spots", len({c["spot"].lower() for c in clues}) == 15)
    named = [c["code"] for c in clues if c["spot"].lower() in " ".join(c["lines"]).lower()]
    res("no clue rhyme names its own answer", not named, str(named))
    # zip + pdfs
    with zipfile.ZipFile(os.path.join(HERE, ZIP)) as z:
        names = sorted(z.namelist())
        res("ZIP contents", names == sorted(list(PDFS) + ["README-LICENSE.txt"]), str(names))
        tmp = tempfile.mkdtemp()
        z.extractall(tmp)
    for f, (w, h) in PDFS.items():
        p = os.path.join(tmp, f)
        info = subprocess.check_output(["pdfinfo", p], text=True)
        pages = int(re.search(r"Pages:\s+(\d+)", info).group(1))
        pw, ph = map(float, re.search(r"Page size:\s+([\d.]+) x ([\d.]+)", info).groups())
        res(f"{f}: {PAGES} pages, {w}x{h} pt", pages == PAGES and abs(pw - w) < 1 and abs(ph - h) < 1, f"({pages} pages, {pw}x{ph})")
        fonts = subprocess.check_output(["pdffonts", p], text=True).splitlines()[2:]
        res(f"{f}: all fonts embedded", fonts and all(" yes " in l for l in fonts))
        res(f"{f}: size under 20 MB", os.path.getsize(p) < 20e6, f"({os.path.getsize(p) / 1e6:.1f} MB)")
        txt = subprocess.check_output(["pdftotext", "-raw", p, "-"], text=True)
        flat = re.sub(r"\s+", "", txt)
        miss = [c["code"] for c in clues if re.sub(r"\s+", "", c["lines"][0]) not in flat or re.sub(r"\s+", "", c["spot"]) not in flat]
        res(f"{f}: every clue's first line and spot on the pages", not miss, str(miss))
    shutil.rmtree(tmp)
    # images
    lj = json.load(open(os.path.join(HERE, "listing.json")))
    for im in lj["images"]:
        res(f"{im} is 3000x2250", Image.open(os.path.join(HERE, im)).size == (3000, 2250))
    res("4 listing images", len(lj["images"]) == 4)
    res("contact-sheet.png exists", os.path.exists(os.path.join(HERE, "contact-sheet.png")))
    # listing
    t = lj["title"]
    caps = [w for w in re.findall(r"[A-Za-z']+", t) if len(w) > 1 and w[:2].isupper()]
    res("title <=140 chars, leads with 'Christmas Scavenger Hunt'", len(t) <= 140 and t.startswith("Christmas Scavenger Hunt"), f"({len(t)})")
    res("title has at most 3 words starting with 2 capitals", len(caps) <= 3, str(caps))
    res("title has at most one '&'", t.count("&") <= 1)
    tags = lj["tags"]
    res("13 unique tags, each <=20 chars", len(tags) == 13 and len(set(tags)) == 13 and max(map(len, tags)) <= 20,
        f"(longest {max(map(len, tags))})")
    res("description ends with disclosure line", lj["description"].endswith(DISCLOSURE))
    blob = json.dumps(lj, ensure_ascii=False)
    res("no HTML entities, plain apostrophes", "&#" not in blob and "&amp;" not in blob and "’" not in blob)
    res("taxonomy_id 1350, price 3.5, digital_file", lj["taxonomy_id"] == 1350 and lj["price"] == 3.5 and lj["digital_file"] == ZIP)
    res("digital, i_did, 2020_2026, not a supply", lj["who_made"] == "i_did" and lj["when_made"] == "2020_2026" and lj["is_supply"] is False)
    md = open(os.path.join(HERE, "LISTING.md")).read()
    res("LISTING.md matches listing.json", t in md and lj["description"] in md and ", ".join(tags) in md)
    readme = open(os.path.join(HERE, "README-LICENSE.txt")).read()
    res("README page map: 8 pages, pages 3-6 clues, page 7 blank, page 8 tracker",
        "8 pages" in readme and "Pages 3-6" in readme and "Page 7" in readme and "Page 8" in readme)
    res("safety copy (oven handle, never inside) in README, description and PDF source",
        "never inside" in readme and "never inside" in lj["description"] and "never inside" in open(os.path.join(HERE, "build.js")).read())
    print("ALL CHECKS PASS" if ok else "SOME CHECKS FAILED")
    return ok


if __name__ == "__main__":
    if "--check" not in sys.argv:
        build()
    sys.exit(0 if check() else 1)
