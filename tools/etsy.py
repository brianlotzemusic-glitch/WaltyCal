"""Etsy Open API v3 client for the shop factory.

Commands:
  python3 tools/etsy.py ping                    check the API key works
  python3 tools/etsy.py whoami                  check the login works; prints shop id and name
  python3 tools/etsy.py taxonomy <word>         find taxonomy ids by name
  python3 tools/etsy.py upload <bundle_dir>     create a listing from listing.json
  python3 tools/etsy.py update <bundle_dir>     push edited listing.json text to an uploaded listing (and turn auto-renew on)
  python3 tools/etsy.py stats                   write stats/listings.csv (views, favorites, sales)
  python3 tools/etsy.py lead-photos <dir> <img>...  add photos to a live listing as #1, #2, ... (existing photos move down);
                                                used for Printify products, whose API cannot choose the main photo
  python3 tools/etsy.py rerank <dir> <image_id>...  put these image ids first, in this order (the rest follow)

Environment (set in the cloud environment settings, never committed):
  ETSY_KEYSTRING, ETSY_SHARED_SECRET   from the Etsy developer app
  ETSY_REFRESH_TOKEN                   from the one-time OAuth step (tools/etsy_auth.py)
  ETSY_USER_ID                         printed by etsy_auth.py (shop id is looked up from it)
  ETSY_SHOP_ID                         optional; numeric shop id if you already know it
  ETSY_TAXONOMY_ID                     default taxonomy id for cut-file listings
  ETSY_PUBLISH=0                       keep new listings as drafts (default: publish immediately)
"""
import csv, json, mimetypes, os, sys, time
import urllib.request, urllib.parse, urllib.error, uuid

API = "https://openapi.etsy.com/v3/application"
TOKEN_URL = "https://api.etsy.com/v3/public/oauth/token"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def env(name, required=True):
    v = os.environ.get(name, "")
    if required and not v:
        sys.exit(f"missing environment variable {name}")
    return v


def api_key():
    return f"{env('ETSY_KEYSTRING')}:{env('ETSY_SHARED_SECRET')}"


_token = None


def access_token():
    global _token
    if _token is None:
        body = urllib.parse.urlencode({"grant_type": "refresh_token", "client_id": env("ETSY_KEYSTRING"),
                                       "refresh_token": env("ETSY_REFRESH_TOKEN")}).encode()
        _token = json.load(urllib.request.urlopen(urllib.request.Request(TOKEN_URL, body)))["access_token"]
    return _token


def call(method, path, form=None, files=None, auth=True, retries=3):
    headers = {"x-api-key": api_key()}
    if auth:
        headers["Authorization"] = f"Bearer {access_token()}"
    data = None
    if files:
        boundary = uuid.uuid4().hex
        parts = []
        for k, v in (form or {}).items():
            parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode())
        for k, path_ in files.items():
            ctype = mimetypes.guess_type(path_)[0] or "application/octet-stream"
            parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{k}"; filename="{os.path.basename(path_)}"\r\n'
                         f'Content-Type: {ctype}\r\n\r\n'.encode() + open(path_, "rb").read() + b"\r\n")
        data = b"".join(parts) + f"--{boundary}--\r\n".encode()
        headers["Content-Type"] = f"multipart/form-data; boundary={boundary}"
    elif form is not None:
        data = urllib.parse.urlencode(form, doseq=True).encode()
        headers["Content-Type"] = "application/x-www-form-urlencoded"
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(urllib.request.Request(API + path, data, headers, method=method)) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 429 or e.code >= 500:
                time.sleep(2 ** (attempt + 1))
                continue
            sys.exit(f"{method} {path} -> {e.code}: {e.read().decode()[:500]}")
    sys.exit(f"{method} {path} failed after {retries} retries")


def shop_id():
    sid = os.environ.get("ETSY_SHOP_ID")
    if sid:
        return sid
    return str(call("GET", f"/users/{env('ETSY_USER_ID')}/shops")["shop_id"])


def upload(bundle_dir):
    spec = json.load(open(os.path.join(bundle_dir, "listing.json")))
    if os.path.exists(os.path.join(bundle_dir, "etsy_listing_id")):
        sys.exit(f"already uploaded: {bundle_dir}")
    shop = shop_id()
    listing = call("POST", f"/shops/{shop}/listings", form={
        "quantity": 999, "title": spec["title"], "description": spec["description"], "price": spec["price"],
        "who_made": spec.get("who_made", "i_did"), "when_made": spec.get("when_made", "2020_2026"),
        "is_supply": str(spec.get("is_supply", False)).lower(), "type": "download",
        "taxonomy_id": spec.get("taxonomy_id") or env("ETSY_TAXONOMY_ID"),
        "tags": ",".join(spec["tags"]), "should_auto_renew": "true",
    })
    lid = listing["listing_id"]
    for rank, img in enumerate(spec["images"], 1):
        call("POST", f"/shops/{shop}/listings/{lid}/images", form={"rank": rank}, files={"image": os.path.join(bundle_dir, img)})
    call("POST", f"/shops/{shop}/listings/{lid}/files", form={"name": os.path.basename(spec["digital_file"]), "rank": 1},
         files={"file": os.path.join(bundle_dir, spec["digital_file"])})
    if os.environ.get("ETSY_PUBLISH") != "0":
        call("PATCH", f"/shops/{shop}/listings/{lid}", form={"state": "active"})
    with open(os.path.join(bundle_dir, "etsy_listing_id"), "w") as f:
        f.write(str(lid))
    print(f"listing {lid} {'published' if os.environ.get('ETSY_PUBLISH') != '0' else 'saved as draft'}: {spec['title']}")


def update(bundle_dir):
    """Push listing.json's title, description, tags and price to an uploaded listing, and keep auto-renew on."""
    spec = json.load(open(os.path.join(bundle_dir, "listing.json")))
    lid = open(os.path.join(bundle_dir, "etsy_listing_id")).read().strip()
    call("PATCH", f"/shops/{shop_id()}/listings/{lid}", form={
        "title": spec["title"], "description": spec["description"],
        "tags": ",".join(spec["tags"]), "price": spec["price"], "should_auto_renew": "true"})
    print(f"listing {lid} updated: {spec['title']}")


def lead_photos(item_dir, images):
    """Upload images to an existing listing and make them photos #1..n, ahead of the photos already there.
    Etsy's upload `rank` alone is unreliable (tested 4 Oct 2026), so every image is re-ranked explicitly afterwards."""
    lid = open(os.path.join(item_dir, "etsy_listing_id")).read().strip()
    shop = shop_id()
    before = [im["listing_image_id"] for im in call("GET", f"/listings/{lid}/images")["results"]]
    ours = []
    for img in images:
        path = img if os.path.exists(img) else os.path.join(item_dir, img)
        ours.append(call("POST", f"/shops/{shop}/listings/{lid}/images", form={"rank": 1}, files={"image": path})["listing_image_id"])
    order = ours + [i for i in before if i not in ours]
    for rank, iid in enumerate(order, 1):
        call("POST", f"/shops/{shop}/listings/{lid}/images", form={"listing_image_id": iid, "rank": rank})
    shown = [im["listing_image_id"] for im in call("GET", f"/listings/{lid}/images")["results"]]
    for rank, (iid, img) in enumerate(zip(ours, images), 1):
        print(f"listing {lid}: photo #{rank} = {os.path.basename(img)} ({iid})")
    if shown[:len(ours)] != ours:
        sys.exit(f"listing {lid}: order check failed, Etsy shows {shown}; fix with `etsy.py rerank`")


def rerank(item_dir, ids):
    """Set the listing's photo order explicitly: the given image ids first, then the rest in their current order."""
    lid = open(os.path.join(item_dir, "etsy_listing_id")).read().strip()
    shop = shop_id()
    ids = [int(i) for i in ids]
    before = [im["listing_image_id"] for im in call("GET", f"/listings/{lid}/images")["results"]]
    for rank, iid in enumerate(ids + [i for i in before if i not in ids], 1):
        call("POST", f"/shops/{shop}/listings/{lid}/images", form={"listing_image_id": iid, "rank": rank})
    print(f"listing {lid}: order now", [im["listing_image_id"] for im in call("GET", f"/listings/{lid}/images")["results"]])


def stats():
    shop = shop_id()
    sold = {}
    offset = 0
    while True:
        page = call("GET", f"/shops/{shop}/transactions?limit=100&offset={offset}")
        for t in page["results"]:
            s = sold.setdefault(t["listing_id"], [0, 0.0])
            s[0] += t["quantity"]
            s[1] += t["quantity"] * t["price"]["amount"] / t["price"]["divisor"]
        offset += 100
        if offset >= page["count"]:
            break
    rows = []
    for state in ("active", "inactive", "draft"):
        for l in call("GET", f"/shops/{shop}/listings?state={state}&limit=100")["results"]:
            n, rev = sold.get(l["listing_id"], [0, 0.0])
            views = l.get("views") or 0
            rows.append({"listing_id": l["listing_id"], "state": state, "title": l["title"], "views": views,
                         "favorites": l.get("num_favorers", 0), "sales": n, "revenue": round(rev, 2),
                         "conversion_pct": round(100 * n / views, 2) if views else 0})
    os.makedirs(os.path.join(ROOT, "stats"), exist_ok=True)
    out = os.path.join(ROOT, "stats", "listings.csv")
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]) if rows else ["listing_id"])
        w.writeheader(); w.writerows(rows)
    print(f"{len(rows)} listings, revenue ${sum(r['revenue'] for r in rows):.2f} -> {out}")


def taxonomy(word):
    def walk(nodes, trail):
        for n in nodes:
            path = trail + [n["name"]]
            if word.lower() in n["name"].lower():
                print(n["id"], " > ".join(path))
            walk(n.get("children", []), path)
    walk(call("GET", "/seller-taxonomy/nodes", auth=False)["results"], [])


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "ping":
        print(call("GET", "/openapi-ping", auth=False))
    elif cmd == "whoami":
        sid = shop_id()
        s = call("GET", f"/shops/{sid}")
        print(sid, s.get("shop_name"), s.get("url"))
    elif cmd == "taxonomy":
        taxonomy(sys.argv[2])
    elif cmd == "upload":
        upload(sys.argv[2])
    elif cmd == "lead-photos":
        lead_photos(sys.argv[2], sys.argv[3:])
    elif cmd == "rerank":
        rerank(sys.argv[2], sys.argv[3:])
    elif cmd == "publish":
        lid = open(os.path.join(sys.argv[2], "etsy_listing_id")).read().strip()
        call("PATCH", f"/shops/{shop_id()}/listings/{lid}", form={"state": "active"})
        print(f"listing {lid} published")
    elif cmd == "update":
        update(sys.argv[2])
    elif cmd == "stats":
        stats()
    else:
        sys.exit(__doc__)
