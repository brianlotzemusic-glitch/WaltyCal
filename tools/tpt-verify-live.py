#!/usr/bin/env python3
"""Manager-side check: scrape the PUBLIC TpT page of every item with an `uploaded` file and compare
price / free / preview / page count with its tpt.json. Prints expected-vs-live and exits 1 on any
mismatch, fetch failure or unparsable page (so a shift can run it and stop on a non-zero exit).

  python3 tools/tpt-verify-live.py                 all items with `uploaded`
  python3 tools/tpt-verify-live.py 027 026         only these item numbers / slugs
  python3 tools/tpt-verify-live.py --offline DIR   read DIR/<slug>.html instead of fetching (tests)
  python3 tools/tpt-verify-live.py --json          machine-readable result

Read-only; needs no TpT login. The parsing mirrors tools/tpt-live.js (tested by tools/test-tpt-live.js).
"""
import argparse, glob, json, os, re, sys, time, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UA = "Mozilla/5.0"
def parse_live(html, product_id=None):
    """Real TpT page: JSON-LD Offer price + embedded app JSON isFree / pageCount / previewUrl; first occurrence of each
    is the product's own. Mirrors tools/tpt-live.js. Missing field -> "error" (never passes as a match)."""
    def first(pat):
        m = re.search(pat, html)
        return m.group(1) if m else None
    offer = re.search(r'@type\\?"\s*:\s*\\?"Offer\\?"[\s\S]{0,600}?price\\?"\s*:\s*\\?"?(-?\d+(?:\.\d+)?)', html)
    free = first(r'isFree\\?"\s*:\s*(true|false)')
    prev = first(r'previewUrl\\?"\s*:\s*(null|\\?"[^"]+)')
    pages = first(r'pageCount\\?"\s*:\s*\\?"?(\d+)')
    out = {
        "price": "%.2f" % float(offer.group(1)) if offer else None,
        "isFree": None if free is None else free == "true",
        "previewUrl": None if prev in (None, "null") else re.sub(r'^\\?"', "", prev),
        "pageCount": int(pages) if pages else None,
    }
    missing = [k for k, v in (("price", offer), ("isFree", free), ("previewUrl", prev)) if not v]
    if missing:
        out["error"] = "no %s field found in the page (blocked, login wall or TpT changed the page)" % "/".join(missing)
    return out


def compare_live(expected, live):
    p = []
    if live.get("error"):
        p.append(live["error"])
    want_free = expected.get("free") is True
    if live.get("price") is not None and float(live["price"]) != float(expected.get("price") or 0):
        p.append("price: live %s, tpt.json %.2f" % (live["price"], float(expected.get("price") or 0)))
    if live.get("isFree") is not None and live["isFree"] != want_free:
        p.append("isFree: live %s, expected %s" % (str(live["isFree"]).lower(), str(want_free).lower()))
    if (expected.get("files") or {}).get("preview") and not live.get("previewUrl") and not live.get("error"):
        p.append("previewUrl: live page has no preview file (tpt.json declares one)")
    return p


def page_warning(expected, live):
    """Page count differs: a WARNING only (TpT derives it; does not affect the exit code)."""
    if expected.get("pages") and live.get("pageCount") is not None and int(expected["pages"]) != live["pageCount"]:
        return "pages: live %s, tpt.json %s" % (live["pageCount"], expected["pages"])
    return None


def fetch(url):
    last = None
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html"})
            with urllib.request.urlopen(req, timeout=40) as r:
                return r.read().decode("utf-8", "replace")
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(2 * (attempt + 1))
    raise RuntimeError("fetch failed: %s" % last)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("items", nargs="*", help="item numbers or slugs (default: every item with an `uploaded` file)")
    ap.add_argument("--offline", metavar="DIR", help="read DIR/<slug>.html instead of fetching")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    rows, bad, skipped = [], 0, []
    for d in sorted(glob.glob(os.path.join(ROOT, "tpt", "[0-9][0-9][0-9]-*"))):
        slug = os.path.basename(d)
        up = os.path.join(d, "uploaded")
        if not os.path.exists(up):
            continue
        if a.items and not any(slug == i or slug.startswith(i.zfill(3) + "-") for i in a.items):
            continue
        lines = open(up).read().split("\n")
        url = lines[1].strip() if len(lines) > 1 else ""
        m = re.search(r"/Product/.*-(\d+)$", url)
        exp = json.load(open(os.path.join(d, "tpt.json")))
        row = {"item": slug, "url": url, "expected": {"price": "%.2f" % float(exp.get("price") or 0), "free": exp.get("free") is True,
               "preview": bool((exp.get("files") or {}).get("preview")), "pages": exp.get("pages")}}
        if not m and re.search(r"URL not yet recorded", "\n".join(lines), re.I):
            skipped.append(slug + ": no URL recorded in `uploaded` (owner confirmed it live; add the URL on line 2 to check it)")
            continue
        try:
            if not m:
                raise RuntimeError("`uploaded` line 2 is not a TpT product URL: %r" % url)
            html = open(os.path.join(a.offline, slug + ".html"), encoding="utf-8").read() if a.offline else fetch(url)
            live = parse_live(html, m.group(1))
            row["live"] = {"price": live.get("price"), "free": live.get("isFree"), "preview": bool(live.get("previewUrl")), "pages": live.get("pageCount")}
            row["problems"] = compare_live(exp, live)
            row["warnings"] = [w for w in [page_warning(exp, live)] if w]
        except Exception as e:  # noqa: BLE001
            row["live"] = None
            row["problems"] = [str(e)]
        bad += bool(row["problems"])
        rows.append(row)

    if a.json:
        print(json.dumps({"checked": len(rows), "mismatched": bad, "skipped": skipped, "items": rows}, indent=2))
    else:
        print("%-38s %-16s %-16s %-14s %-9s" % ("item", "price exp/live", "free exp/live", "preview e/l", "pages e/l"))
        for r in rows:
            e, l = r["expected"], r["live"] or {}
            yn = lambda v: "-" if v is None else ("yes" if v else "no")
            print("%-38s %-16s %-16s %-14s %-9s %s" % (
                r["item"][:38], "%s/%s" % (e["price"], l.get("price") or "-"),
                "%s/%s" % (yn(e["free"]), yn(l.get("free"))), "%s/%s" % (yn(e["preview"]), yn(l.get("preview"))),
                "%s/%s" % (e["pages"] or "-", l.get("pages") or "-"), "MISMATCH" if r["problems"] else ("OK (page warning)" if r.get("warnings") else "OK")))
            for w in r.get("warnings", []):
                print("    ~ warning: " + w)
            for p in r["problems"]:
                print("    - " + p)
        for k in skipped:
            print("SKIPPED (not a failure): " + k)
        print("\nchecked %d live items, %d with problems, %d page-count warnings, %d skipped" % (len(rows), bad, sum(bool(r.get("warnings")) for r in rows), len(skipped)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
