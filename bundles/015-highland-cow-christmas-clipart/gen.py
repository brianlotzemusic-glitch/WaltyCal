"""Highland Cow Christmas Clipart: build everything and run the format checks (formats/clipart.md).

  python3 gen.py            # PNG + SVG -> mockup -> listing images -> contact sheet -> ZIP -> checks
  python3 gen.py --skip-art # same, but keep the existing art/png + art/svg (process.py takes ~2 min)
  python3 gen.py --check    # checks only

Steps: process.py (art/raw + art/alpha + art/up -> art/png, art/svg, art/stats.json), mockup.py (the real
PNGs on a blank AI flat-lay photo), thumbs.js (listing images; Playwright/Chromium), contact sheet, buyer ZIP,
checks. Needs scipy, pillow, potracer, numpy, cairosvg and Node Playwright (NODE_PATH=$(npm root -g)).
No AI calls: the drafts, cut-out masks, upscales and the mockup photo are already paid for (PROMPTS.md).
"""
import io, json, os, re, shutil, subprocess, sys, zipfile
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ZIP = "highland-cow-christmas-clipart.zip"
PREFIX = "highland-cow-"          # buyer file names: highland-cow-01-holly-crown.png / .svg
DISCLOSURE = "Designed with the help of digital and AI tools, and checked by hand."
LEAD = "Highland Cow Christmas Clipart"
TAXONOMY = 6844   # Craft Supplies & Tools > Canvas & Surfaces > Stencils, Templates & Transfers > Clip Art & Image Files
PRICE = 3.49
N = 12
LONG = 3600       # px, longest side of every PNG (12 in at 300 dpi)
DPI = 300
MAX_ZIP_MB = 20   # Etsy's limit per digital file
MAX_PNG_MB = 3
MIN_PIECE_PX = 900          # no loose speck in a PNG (a piece of the art smaller than ~2.5 mm at 12 in)
MAX_WHITE_EDGE_PCT = 3.0    # opaque pixels on the art's outer edge that are paper-white (a halo on dark fabric)
# Halo test (QA round 1, S1): light neutral pixels (every channel >= 195, tint <= 35, alpha > 127) within 12 px of
# transparency (alpha < 20) are paper left by the cut-out. At most HALO_MAX_PX per design and no patch over
# HALO_PATCH_PX, except inside HALO_OK boxes (final PNG coordinates) that hold real light art.
HALO_MAX_PX = 5000
HALO_PATCH_PX = 30
HALO_OK = {"11-mistletoe": [((1650, 400, 2000, 800), "the white mistletoe berries, beside the open ribbon loops")]}
# Opacity (QA round 1, S2): no near-opaque alpha (250-254) anywhere; >= 99% of the solid interior (> 3 px inside
# the edge) and >= 98% of all pixels with alpha > 127 are exactly 255. The rest is anti-aliased edge and 08's glow.
MIN_HASH_BITS = 60          # of 576: no two designs alike


def run(*cmd):
    env = dict(os.environ)
    if cmd[0] == "node":
        env["NODE_PATH"] = subprocess.check_output("npm root -g", shell=True, text=True).strip()
    subprocess.run(cmd, cwd=HERE, check=True, env=env)


def designs():
    return json.load(open(os.path.join(HERE, "subjects.json")))["designs"]


def render_svg(path, w):
    import cairosvg
    from PIL import Image
    return Image.open(io.BytesIO(cairosvg.svg2png(url=path, output_width=w))).convert("RGBA")


def contact_sheet():
    """Every design on a transparency checkerboard and on dark fabric, its SVG, and its numbers."""
    from PIL import Image, ImageDraw, ImageFont
    stats = json.load(open(os.path.join(HERE, "art", "stats.json")))
    T, cap = 300, 70
    cols = 4
    rows = (N + cols - 1) // cols
    W, H = cols * (3 * T + 40) + 20, rows * (T + cap + 20) + 90
    sheet = Image.new("RGB", (W, H), "#d8d2dc")
    d = ImageDraw.Draw(sheet)
    try:
        f = ImageFont.truetype(os.path.join(HERE, "fonts", "Nunito-700.ttf"), 17)
        fb = ImageFont.truetype(os.path.join(HERE, "fonts", "Fraunces-900.ttf"), 40)
    except OSError:
        f = fb = ImageFont.load_default()
    d.text((20, 18), "Highland Cow Christmas Clipart: 12 PNG (checker, dark) + SVG", font=fb, fill="#2c1b36")
    checker = Image.new("RGBA", (T, T), "white")
    cd = ImageDraw.Draw(checker)
    for y in range(0, T, 20):
        for x in range(0, T, 20):
            if (x // 20 + y // 20) % 2:
                cd.rectangle([x, y, x + 19, y + 19], fill="#e4e0e8")
    for i, (slug, name, _) in enumerate(designs()):
        x, y = 20 + (i % cols) * (3 * T + 40), 90 + (i // cols) * (T + cap + 20)
        art = Image.open(os.path.join(HERE, "art", "png", slug + ".png")).convert("RGBA")
        art.thumbnail((T - 16, T - 16))
        for k, bg in enumerate([checker.copy(), Image.new("RGBA", (T, T), "#2f4a3a")]):
            bg.alpha_composite(art, ((T - art.size[0]) // 2, (T - art.size[1]) // 2))
            sheet.paste(bg.convert("RGB"), (x + k * T, y))
        sv = render_svg(os.path.join(HERE, "art", "svg", slug + ".svg"), art.size[0])
        bg = Image.new("RGBA", (T, T), "white")
        bg.alpha_composite(sv, ((T - sv.size[0]) // 2, max(0, (T - sv.size[1]) // 2)))
        sheet.paste(bg.convert("RGB"), (x + 2 * T, y))
        st = stats[slug]
        d.text((x, y + T + 4), f"{slug}  ({name})", font=f, fill="#2c1b36")
        d.text((x, y + T + 24), f"{st['px'][0]}x{st['px'][1]} px, {st['png_mb']} MB, {st['pieces']} piece(s), "
               f"{st['specks_removed']} specks removed", font=f, fill="#2f4a3a")
        d.text((x, y + T + 44), f"white px cleared {st['white_px_cleared']}, holes filled {st['holes_filled']}, "
               f"SVG {st['svg_paths']} subpaths", font=f, fill="#2f4a3a")
    sheet.save(os.path.join(HERE, "contact-sheet.png"), optimize=True)


def build(skip_art):
    if not skip_art:
        run(sys.executable, "process.py")
    run(sys.executable, "mockup.py")
    run("node", "thumbs.js")
    contact_sheet()
    with zipfile.ZipFile(os.path.join(HERE, ZIP), "w", zipfile.ZIP_DEFLATED) as z:
        for slug, _, _ in designs():
            z.write(os.path.join(HERE, "art", "png", slug + ".png"), f"PNG/{PREFIX}{slug}.png")
            z.write(os.path.join(HERE, "art", "svg", slug + ".svg"), f"SVG/{PREFIX}{slug}.svg")
        z.write(os.path.join(HERE, "README-LICENSE.txt"), "README-LICENSE.txt")


def png_checks(im):
    """(longest side, dpi ok, transparent share %, smallest piece px, white outer-edge %, corners clear)."""
    from scipy import ndimage as nd
    a = np.array(im.convert("RGBA"))
    A = a[..., 3]
    solid = A > 127
    lab, n = nd.label(solid, np.ones((3, 3)))
    smallest = int(nd.sum(np.ones(lab.shape), lab, range(1, n + 1)).min()) if n else 0
    edge = solid & nd.binary_dilation(~solid)                      # the art's outer boundary pixels
    rgb = a[..., :3][edge].astype(int)
    white = ((rgb.min(axis=1) >= 236) & (rgb.max(axis=1) - rgb.min(axis=1) <= 20)).mean() * 100 if edge.any() else 0
    corners = all(A[y, x] == 0 for y, x in [(0, 0), (0, -1), (-1, 0), (-1, -1)])
    return max(im.size), 100 * (A == 0).mean(), smallest, white, corners


def halo(slug, im):
    """(light neutral px near transparency outside HALO_OK, biggest such patch)."""
    from scipy import ndimage as nd
    a = np.array(im.convert("RGBA")).astype(int)
    A = a[..., 3]
    mn, mx = a[..., :3].min(axis=2), a[..., :3].max(axis=2)
    m = (A > 127) & (mn >= 195) & (mx - mn <= 35) & (nd.distance_transform_edt(A >= 20) <= 12)
    for (x0, y0, x1, y1), _ in HALO_OK.get(slug, []):
        m[y0:y1, x0:x1] = False
    lab, n = nd.label(m, np.ones((3, 3)))
    return int(m.sum()), int(nd.sum(m, lab, range(1, n + 1)).max()) if n else 0


def opacity(im):
    """(any alpha 250-254, % of interior solid px at 255, % of all solid px at 255)."""
    from scipy import ndimage as nd
    A = np.array(im.convert("RGBA"))[..., 3]
    solid = A > 127
    inner = nd.distance_transform_edt(solid) > 3
    return bool(((A >= 250) & (A < 255)).any()), 100 * (A[inner] == 255).mean(), 100 * (A[solid] == 255).mean()


def art_hash(im):
    from PIL import Image
    a = np.array(im.convert("RGBA"))
    g = np.array(Image.fromarray(a[..., 3]).resize((24, 24), Image.BILINEAR), float)
    c = np.array(im.convert("RGBA").convert("L").resize((24, 24), Image.BILINEAR), float)
    return np.concatenate([(g > g.mean()).flatten(), (c > c.mean()).flatten()])


def check():
    from PIL import Image
    import xml.etree.ElementTree as ET
    ok = True

    def res(name, cond, info=""):
        nonlocal ok
        ok &= bool(cond)
        print(f"{'PASS' if cond else 'FAIL'}  {name} {info}")

    S = designs()
    slugs = [s[0] for s in S]
    res(f"{N} distinct designs (slugs, names, subjects)", len(S) == N and len(set(slugs)) == N
        and len({s[1] for s in S}) == N and len({s[2] for s in S}) == N)
    picks = json.load(open(os.path.join(HERE, "picks.json")))
    res("picks.json names the kept draft of every design", sorted(picks) == sorted(slugs))
    stats = json.load(open(os.path.join(HERE, "art", "stats.json")))
    res("art/stats.json covers every design", sorted(stats) == sorted(slugs))
    for d in ("raw", "alpha"):
        res(f"art/{d}/ holds the paid-for input of every design",
            all(os.path.exists(os.path.join(HERE, "art", d, s + ".png")) for s in slugs))

    with zipfile.ZipFile(os.path.join(HERE, ZIP)) as z:
        names = sorted(z.namelist())
        want = sorted([f"PNG/{PREFIX}{s}.png" for s in slugs] + [f"SVG/{PREFIX}{s}.svg" for s in slugs] + ["README-LICENSE.txt"])
        res("ZIP holds exactly PNG/ x12, SVG/ x12 and README-LICENSE.txt", names == want, f"({len(names)} files)")
        zmb = os.path.getsize(os.path.join(HERE, ZIP)) / 1e6
        res(f"ZIP under Etsy's {MAX_ZIP_MB} MB file limit", zmb < MAX_ZIP_MB, f"({zmb:.1f} MB)")
        bad, worst, hashes, halos, opac = [], [0, 100.0, 1e9, 0.0], {}, [], []
        for s in slugs:
            raw = z.read(f"PNG/{PREFIX}{s}.png")
            im = Image.open(io.BytesIO(raw))
            dpi = im.info.get("dpi", (0, 0))
            transparent = im.mode == "RGBA" or (im.mode == "P" and "transparency" in im.info)
            longest, clear_pct, smallest, white, corners = png_checks(im)
            worst = [max(worst[0], len(raw) / 1e6), min(worst[1], clear_pct), min(worst[2], smallest), max(worst[3], white)]
            if not (transparent and longest == LONG and round(dpi[0]) == DPI and round(dpi[1]) == DPI and corners
                    and clear_pct >= 15 and smallest >= MIN_PIECE_PX and white <= MAX_WHITE_EDGE_PCT and len(raw) / 1e6 <= MAX_PNG_MB):
                bad.append(f"{s}: mode {im.mode}, {im.size}, dpi {dpi}, {clear_pct:.0f}% clear, corners {corners}, "
                           f"smallest piece {smallest} px, white edge {white:.1f}%, {len(raw) / 1e6:.1f} MB")
            hashes[s] = art_hash(im)
            hpx, hpatch = halo(s, im)
            near, inner, allsolid = opacity(im)
            halos.append((s, hpx, hpatch))
            opac.append((s, near, inner, allsolid))
        res(f"every PNG: transparent, longest side {LONG} px, {DPI} dpi, clear corners, >= 15% transparent, "
            f"no piece under {MIN_PIECE_PX} px, <= {MAX_WHITE_EDGE_PCT}% paper-white on the outer edge, <= {MAX_PNG_MB} MB",
            not bad, f"(largest {worst[0]:.2f} MB, least clear {worst[1]:.0f}%, smallest piece {worst[2]} px, "
            f"whitest edge {worst[3]:.2f}%)" + ("\n      " + "\n      ".join(bad) if bad else ""))
        hb = [f"{s}: {p} px, biggest patch {q} px" for s, p, q in halos if p > HALO_MAX_PX or q > HALO_PATCH_PX]
        res(f"halo test: <= {HALO_MAX_PX} light neutral px within 12 px of transparency and no patch over {HALO_PATCH_PX} px "
            f"(outside HALO_OK)", not hb, f"(most {max(p for _, p, _ in halos)} px, biggest patch {max(q for _, _, q in halos)} px)"
            + ("\n      " + "\n      ".join(hb) if hb else ""))
        ob = [f"{s}: alpha 250-254 {n}, interior {i:.2f}%, all solid {a:.2f}%" for s, n, i, a in opac if n or i < 99 or a < 98]
        res("full opacity: no alpha 250-254, >= 99% of the solid interior and >= 98% of all solid px at alpha 255", not ob,
            f"(lowest interior {min(i for _, _, i, _ in opac):.2f}%, lowest overall {min(a for _, _, _, a in opac):.2f}%)"
            + ("\n      " + "\n      ".join(ob) if ob else ""))
        dmin = min(((hashes[a] != hashes[b]).sum(), a, b) for i, a in enumerate(slugs) for b in slugs[i + 1:])
        res(f"no two designs alike (24x24 shape + tone hash, >= {MIN_HASH_BITS} of 1152 bits differ)", dmin[0] >= MIN_HASH_BITS,
            f"(closest pair {dmin[1][:2]}/{dmin[2][:2]}: {dmin[0]})")

        bad = []
        for s in slugs:
            raw = z.read(f"SVG/{PREFIX}{s}.svg").decode()
            try:
                root = ET.fromstring(raw)
            except ET.ParseError as e:
                bad.append(f"{s}: does not parse ({e})")
                continue
            paths = root.findall("{http://www.w3.org/2000/svg}path")
            fills = {p.get("fill") for p in paths}
            w_in = float(root.get("width").rstrip("in"))
            png_in = stats[s]["px"][0] / DPI
            tmp = os.path.join(HERE, ".check.svg")
            open(tmp, "w").write(raw)
            r = np.array(render_svg(tmp, 400))[..., 3] > 127
            os.remove(tmp)
            ink = r.mean() * 100
            vb = [float(v) for v in root.get("viewBox").split()]
            aspect_svg, aspect_png = vb[2] / vb[3], stats[s]["px"][0] / stats[s]["px"][1]
            if len(paths) != 1 or len(fills) != 1 or "text" in raw or "<image" in raw or abs(w_in - png_in) > 0.05 \
                    or not 3 < ink < 45 or abs(aspect_svg - aspect_png) > 0.02:
                bad.append(f"{s}: {len(paths)} paths, fills {fills}, {w_in:.2f} in vs PNG {png_in:.2f} in, ink {ink:.0f}%, "
                           f"aspect {aspect_svg:.3f} vs {aspect_png:.3f}")
        res("every SVG: parses, one path in one color (single layer), no text or embedded image, opens at the PNG's "
            "print size and aspect, ink 3-45% of the canvas", not bad, "\n      " + "\n      ".join(bad) if bad else "")

    readme = open(os.path.join(HERE, "README-LICENSE.txt")).read()
    res("README lists every design name", all(re.search(rf"\b{i + 1} {re.escape(s[1])}\b", readme) for i, s in enumerate(S)))
    lj = json.load(open(os.path.join(HERE, "listing.json")))
    for img in lj["images"]:
        p = os.path.join(HERE, img)
        res(f"{img} is 3000x2250, under 10 MB", Image.open(p).size == (3000, 2250) and os.path.getsize(p) < 10e6,
            f"({os.path.getsize(p) / 1e6:.1f} MB)")
    res("5 listing images", len(lj["images"]) == 5)
    res("contact-sheet.png exists", os.path.exists(os.path.join(HERE, "contact-sheet.png")))
    t = lj["title"]
    caps = [w for w in re.findall(r"[A-Za-z']+", t) if len(w) > 1 and w[:2].isupper()]
    res(f"title <=140 chars, leads with '{LEAD}'", len(t) <= 140 and t.startswith(LEAD), f"({len(t)})")
    res("title: at most 3 words starting with 2 capitals, at most one '&'", len(caps) <= 3 and t.count("&") <= 1, f"{caps} &x{t.count('&')}")
    tags = lj["tags"]
    res("13 unique tags, each <=20 chars", len(tags) == 13 and len(set(tags)) == 13 and max(map(len, tags)) <= 20, f"(longest {max(map(len, tags))})")
    blob = json.dumps(lj, ensure_ascii=False)
    res("no HTML entities, plain apostrophes", not re.search(r"&#\d+;|&amp;|&quot;|&lt;|&gt;|&nbsp;", blob) and "’" not in blob)
    res("description ends with the non-cut-file disclosure line", lj["description"].endswith(DISCLOSURE))
    res("description names every design", all(f"{i + 1} {s[1]}" in lj["description"] for i, s in enumerate(S)))
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
