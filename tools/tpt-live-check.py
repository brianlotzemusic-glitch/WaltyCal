#!/usr/bin/env python3
"""Cloud-side check, no login needed: which released items are ALREADY live on TpT?

The Mac job publishes, then pushes `uploaded` markers back. When that push fails (it did on 12 Nov 2026) the
products are live but the repo still says "waiting". This reads the PUBLIC store page and matches each
released-but-unmarked item by its title.

  python3 tools/tpt-live-check.py              print one line per released item without `uploaded`
  python3 tools/tpt-live-check.py --json       machine-readable
  python3 tools/tpt-live-check.py --html FILE  use a saved store page instead of fetching (tests)

Output lines:  LIVE <NNN-slug> <url>   or   WAITING <NNN-slug>
The cloud must NOT write `uploaded` files for LIVE items: the Mac owns those files, and a file created in both
places makes the Mac's next `git pull` fail. Count LIVE as uploaded when deciding bundles and reports.
"""
import glob, json, os, re, sys, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STORE = "https://www.teacherspayteachers.com/store/brian-lotze?order=Most-Recent"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129 Safari/537.36"


def norm(s):
    """Title or URL slug -> lowercase words joined by '-': '&' and punctuation vanish, so both sides agree."""
    s = s.lower().replace("&", " ").replace("'", "")
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", s)).strip("-")


def store_products(html):
    """[(slug_without_id, url)] in page order (newest first)."""
    out, seen = [], set()
    for m in re.finditer(r'href="(/Product/([^"?#]+?)-(\d+))"', html):
        if m.group(3) not in seen:
            seen.add(m.group(3))
            out.append((norm(m.group(2)), "https://www.teacherspayteachers.com" + m.group(1)))
    return out


def item_title(folder):
    try:
        text = open(os.path.join(folder, "UPLOAD.md"), encoding="utf-8").read()
    except OSError:
        return None
    sec = re.search(r"##\s*1\.[^\n]*\n(.*?)(?=\n##\s*2\.)", text, re.S)
    if not sec:
        return None
    block = re.search(r"```[^\n]*\n(.*?)\n```", sec.group(1), re.S)
    return block.group(1).strip().splitlines()[0].strip() if block else None


def match(title, products):
    """TpT's page address carries the whole title, so require an exact match (a shorter address is accepted
    only when it is a long prefix of the title, in case TpT trims very long titles)."""
    t = norm(title)
    for slug, url in products:
        if slug == t or (len(slug) >= 60 and t.startswith(slug)):
            return url
    return None


def main():
    args = sys.argv[1:]
    if "--html" in args:
        html = open(args[args.index("--html") + 1], encoding="utf-8", errors="ignore").read()
    else:
        req = urllib.request.Request(STORE, headers={"User-Agent": UA})
        html = urllib.request.urlopen(req, timeout=40).read().decode("utf-8", "ignore")
    products = store_products(html)
    if not products:
        sys.exit("could not read any products from the store page (layout changed or request blocked)")
    rows = []
    for folder in sorted(glob.glob(os.path.join(ROOT, "tpt", "[0-9][0-9][0-9]-*"))):
        if not os.path.exists(os.path.join(folder, "release")) or os.path.exists(os.path.join(folder, "uploaded")):
            continue
        title = item_title(folder)
        url = match(title, products) if title else None
        rows.append({"item": os.path.basename(folder), "title": title, "live": bool(url), "url": url})
    if "--json" in args:
        print(json.dumps({"store_products_seen": len(products), "items": rows}, indent=1))
    else:
        for r in rows:
            print(("LIVE    " + r["item"] + " " + r["url"]) if r["live"] else ("WAITING " + r["item"]))
        if not rows:
            print("nothing released is waiting")


if __name__ == "__main__":
    main()
