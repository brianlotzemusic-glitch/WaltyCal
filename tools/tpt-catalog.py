#!/usr/bin/env python3
"""Regenerate tpt/CATALOG.md: one row per product folder tpt/NNN-slug/. Standard library only.

  python3 tools/tpt-catalog.py             write tpt/CATALOG.md (tries the public store page, falls back to offline)
  python3 tools/tpt-catalog.py --offline   never touch the network (Live links come from `uploaded` markers only)
  python3 tools/tpt-catalog.py --out FILE  write somewhere else ('-' = stdout)
  python3 tools/tpt-catalog.py --html FILE use a saved store page instead of fetching (tests)

Read-only on the product folders. The live check reuses tools/tpt-live-check.py (parsing and title matching).
"""
import datetime, glob, importlib.util, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TPT = os.path.join(ROOT, "tpt")
STATUSES = ["Live", "Waiting", "Upload failed", "Not released", "Held"]
KINDS = ["Classroom", "Logic kit", "Bundle", "Free"]


def load_live_check():
    spec = importlib.util.spec_from_file_location("tpt_live_check", os.path.join(ROOT, "tools", "tpt-live-check.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def read(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            return f.read()
    except OSError:
        return ""


def fetch_store(lc, html_file=None):
    """Public store products [(slug, url)], or None when unavailable (offline, blocked, layout changed)."""
    import urllib.request
    try:
        if html_file:
            html = read(html_file)
        else:
            html, seen = "", set()
            for p in range(1, 11):
                url = lc.STORE if p == 1 else f"{lc.STORE}&page={p}"
                page = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": lc.UA}),
                                              timeout=10).read().decode("utf-8", "ignore")
                ids = set(re.findall(r'href="/Product/[^"?#]+?-(\d+)"', page))
                if not ids - seen:
                    break
                seen |= ids
                html += page
        return lc.store_products(html) or None
    except Exception:
        return None


def upload_title(text):
    """First line of the code block under '## 1.' (same rule as tpt-live-check.item_title)."""
    sec = re.search(r"##\s*1\.[^\n]*\n(.*?)(?=\n##\s*2\.)", text, re.S)
    blk = re.search(r"```[^\n]*\n(.*?)\n```", sec.group(1), re.S) if sec else None
    return blk.group(1).strip().splitlines()[0].strip() if blk and blk.group(1).strip() else ""


def queue_info(text):
    """([held lines], set of normalized titles per section) from QUEUE.md."""
    held = [l for l in text.splitlines() if re.match(r"\s*-\s*\[!\]", l) and "HELD" in l]
    secs, cur = {}, None
    for l in text.splitlines():
        if l.startswith("## "):
            cur = "logic" if "Holiday Logic" in l else "bundle" if l.startswith("## Bundles") else \
                  "classroom" if l.startswith("## Classroom") else None
        elif cur and re.match(r"\s*-\s*\[.\]", l):
            secs.setdefault(cur, []).append(re.sub(r"^\s*-\s*\[.\]\s*", "", l))
    return held, secs


def words(s):
    return set(re.findall(r"[a-z0-9]+", s.lower().replace("&", " ").replace("'", "")))


def kind_of(slug, price, title, text, secs):
    if price is not None and price == 0:
        return "Free"
    if "bundle" in slug:
        return "Bundle"
    if re.search(r"(^|-)dmp\d|-logic(-|$)", slug) or re.search(r"\bLogic Pro\b|\bLogic kit\b", title):
        return "Logic kit"
    sw = words(slug.split("-", 1)[1].replace("-", " "))
    for sec, kind in (("logic", "Logic kit"), ("bundle", "Bundle")):   # queue lines name the product, not the folder
        for line in secs.get(sec, []):
            if sw and sw <= words(line):
                return kind
    return "Classroom"


def money(v):
    return f"${v:.2f}" if v is not None else ""


def esc(s):
    return s.replace("\\", "\\\\").replace("|", "\\|").replace("\n", " ")


def build(live_products, lc):
    held_lines, secs = queue_info(read(os.path.join(TPT, "QUEUE.md")))
    rows = []
    for folder in sorted(glob.glob(os.path.join(TPT, "[0-9][0-9][0-9]-*"))):
        if not os.path.isdir(folder):
            continue
        name = os.path.basename(folder)
        num, slug = name[:3], name
        has = lambda f: os.path.exists(os.path.join(folder, f))
        try:
            meta = json.loads(read(os.path.join(folder, "tpt.json")) or "{}")
        except ValueError:
            meta = {}
        up = read(os.path.join(folder, "UPLOAD.md"))
        title = str(meta.get("title") or "").strip() or upload_title(up) or "(untitled)"
        try:
            price = float(meta["price"])
        except (KeyError, TypeError, ValueError):
            price = None
        grades = ", ".join(meta.get("grades") or []) if isinstance(meta.get("grades"), list) else str(meta.get("grades") or "")
        pages = meta.get("pages")
        if not pages:
            m = re.search(r"(?im)^\s*[-*]?\s*(?:pages|page count)\s*[:=]\s*(\d+)", up) or \
                re.search(r"(?i)\*\*Files to attach\*\*.*?\((\d+)\s*pages?[,)]", up, re.S)
            pages = m.group(1) if m else ""
        released = ""
        if has("release"):
            m = re.search(r"\d{4}-\d{2}-\d{2}", read(os.path.join(folder, "release")))
            released = m.group(0) if m else ""
        # product link: `uploaded` marker URL, else live-check URL match
        link = ""
        m = re.search(r"https?://\S+", read(os.path.join(folder, "uploaded"))) if has("uploaded") else None
        if m:
            link = m.group(0)
        elif live_products is not None and has("release") and title != "(untitled)":
            link = lc.match(title, live_products) or ""
        # status
        held = any(num in l or name in l for l in held_lines)
        if held:
            status = "Held"
        elif has("uploaded") or (has("release") and link):
            status = "Live"      # an uploaded marker proves it is live even when an old item has no release file
        elif not has("release"):
            status = "Not released"
        elif has("publish-failed"):
            status = "Upload failed"
        else:
            status = "Waiting"
        notes = []
        if has("reupload") and not has("reuploaded"):
            notes.append("reupload failed" if has("reupload-failed") else
                         "reupload unverified" if has("reupload-unverified") else "reupload pending")
        if any(os.path.basename(p).startswith("republish") for p in glob.glob(os.path.join(folder, "republish*"))):
            notes.append("republish marker")
        if has("publish-failed") and status != "Upload failed":
            notes.append("publish-failed marker")
        if status == "Waiting" and live_products is None and not link:
            link = "unchecked"
        rows.append(dict(num=num, title=title, kind=kind_of(slug, price, title, up, secs), price=price,
                         grades=grades, pages=str(pages), released=released, status=status,
                         note="; ".join(notes), link=link))
    return rows


def render(rows, checked):
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    sc = {s: sum(r["status"] == s for r in rows) for s in STATUSES}
    kc = {k: sum(r["kind"] == k for r in rows) for k in KINDS}
    live_total = sum(r["price"] or 0 for r in rows if r["status"] == "Live")
    out = ["# TpT catalog", "",
           "Generated file: do not edit by hand. Regenerate with `python3 tools/tpt-catalog.py`.", "",
           f"- Generated: {now}",
           f"- Products: {len(rows)}",
           "- By status: " + ", ".join(f"{s} {sc[s]}" for s in STATUSES),
           "- By kind: " + ", ".join(f"{k} {kc[k]}" for k in KINDS),
           f"- Total price of live items: ${live_total:.2f} ({sc['Live']} items)",
           "- Live check against the public store page: " + ("done" if checked else "unchecked (offline or unavailable)"),
           "",
           "| # | Title | Kind | Price | Grades | Pages | Released | Status | Note | TpT link |",
           "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for r in rows:
        link = f"[link]({r['link']})" if r["link"].startswith("http") else r["link"]
        out.append("| " + " | ".join([r["num"], esc(r["title"]), r["kind"], money(r["price"]), esc(r["grades"]),
                                      r["pages"], r["released"], r["status"], esc(r["note"]), link]) + " |")
    out += ["", "## Legend", "",
            "Status:", "",
            "- **Held**: `tpt/QUEUE.md` has a `[!] HELD` line mentioning the folder.",
            "- **Live**: an `uploaded` marker exists in the folder (even if an old item has no `release` file), or a released item was found on the public store page by the live check.",
            "- **Not released**: no `release` marker file (and no `uploaded` marker) in the product folder.",
            "- **Waiting**: released, but not uploaded and not found live.",
            "- **Upload failed**: released, not live, and a `publish-failed` marker exists (checked before Waiting).",
            "",
            "Note: `reupload pending` = `reupload` marker without `reuploaded`; `reupload failed` = also a `reupload-failed` marker; "
            "`reupload unverified` = `reupload-unverified` marker.", "",
            "Columns:", "",
            "- **#, folder**: `tpt/NNN-slug/`; one row per folder.",
            "- **Title**: `title` in `tpt.json` if present, else the first line of the code block under `## 1.` in `UPLOAD.md` (the TpT listing title).",
            "- **Kind**: Free if `tpt.json` price is 0; Bundle if the folder name says bundle; Logic kit if the folder or title is a Logic Pro "
            "project (`dmp` folders, `-logic` names) or the product is listed under Holiday Logic kits in `QUEUE.md`; otherwise Classroom.",
            "- **Price, Grades, Pages**: `price`, `grades`, `pages` in `tpt.json` (pages blank if absent there and in `UPLOAD.md`).",
            "- **Released**: the date in the `release` marker file in the product folder.",
            "- **TpT link**: the URL in the `uploaded` marker; else the live check's title match on the store page; `unchecked` for a waiting item when the store page could not be read.",
            ""]
    return "\n".join(out)


def main():
    args = sys.argv[1:]
    lc = load_live_check()
    products = None
    if "--offline" not in args:
        products = fetch_store(lc, args[args.index("--html") + 1] if "--html" in args else None)
    rows = build(products, lc)
    text = render(rows, products is not None)
    dest = args[args.index("--out") + 1] if "--out" in args else os.path.join(TPT, "CATALOG.md")
    if dest == "-":
        sys.stdout.write(text)
    else:
        with open(dest, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"{len(rows)} rows -> {dest}")


if __name__ == "__main__":
    main()
