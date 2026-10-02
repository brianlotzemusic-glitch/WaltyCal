"""Printify client for print-on-demand products (mugs, tees, etc.) published to the Etsy shop.

Printify prints and ships each order; the buyer pays the Etsy price and Printify charges
the owner's card the base cost + shipping when an order comes in.

Commands:
  python3 tools/printify.py shops                          list connected shops (find the Etsy one)
  python3 tools/printify.py blueprints <word>              search the product catalog (e.g. "mug", "tee")
  python3 tools/printify.py providers <blueprint_id>       print providers for a product
  python3 tools/printify.py variants <blueprint_id> <provider_id>   sizes/colours + placeholder sizes
  python3 tools/printify.py create <pod_dir>               create the product from pod_dir/product.json
  python3 tools/printify.py publish <pod_dir>              publish it to Etsy (writes pod_dir/etsy_published)

Environment: PRINTIFY_API_TOKEN (Printify → My account → Connections → API tokens).
Optional PRINTIFY_SHOP_ID; otherwise the first shop whose sales_channel is etsy is used.

product.json:
{
  "title": "...", "description": "...", "tags": ["..."],          # 13 tags, each <= 20 chars
  "blueprint_id": 68, "print_provider_id": 1,
  "price_cents": 1899,                                              # retail price for every enabled variant
  "variant_ids": [33719, 33720],                                    # from `variants`
  "placements": {"front": "art/front.png"}                          # position -> image path (PNG, 300 DPI)
}
"""
import base64, json, os, sys, time, urllib.error, urllib.request

API = "https://api.printify.com/v1"


def call(method, path, body=None, auth=True, retries=3):
    headers = {"User-Agent": "duskwood-shop-factory", "Content-Type": "application/json"}
    if auth:
        tok = os.environ.get("PRINTIFY_API_TOKEN") or sys.exit("missing PRINTIFY_API_TOKEN")
        headers["Authorization"] = f"Bearer {tok}"
    data = json.dumps(body).encode() if body is not None else None
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(urllib.request.Request(API + path, data, headers, method=method), timeout=120) as r:
                txt = r.read().decode()
                return json.loads(txt) if txt else {}
        except urllib.error.HTTPError as e:
            if e.code == 429 or e.code >= 500:
                time.sleep(2 ** (attempt + 1)); continue
            sys.exit(f"{method} {path} -> {e.code}: {e.read().decode()[:600]}")
    sys.exit(f"{method} {path} failed after {retries} retries")


def shop_id():
    if os.environ.get("PRINTIFY_SHOP_ID"):
        return os.environ["PRINTIFY_SHOP_ID"]
    shops = call("GET", "/shops.json")
    etsy = [s for s in shops if s.get("sales_channel") == "etsy"]
    if not etsy:
        sys.exit("no Etsy shop connected in Printify yet (Printify → My stores → Add new store → Etsy)")
    return str(etsy[0]["id"])


def upload(path):
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    return call("POST", "/uploads/images.json", {"file_name": os.path.basename(path), "contents": b64})["id"]


def create(pod_dir):
    spec = json.load(open(os.path.join(pod_dir, "product.json")))
    if os.path.exists(os.path.join(pod_dir, "printify_product_id")):
        sys.exit(f"already created: {pod_dir}")
    placeholders = []
    for position, img in spec["placements"].items():
        img_id = upload(os.path.join(pod_dir, img))
        placeholders.append({"position": position, "images": [{"id": img_id, "x": 0.5, "y": 0.5, "scale": spec.get("scale", 1), "angle": 0}]})
    body = {
        "title": spec["title"], "description": spec["description"], "tags": spec["tags"],
        "blueprint_id": spec["blueprint_id"], "print_provider_id": spec["print_provider_id"],
        "variants": [{"id": v, "price": spec["price_cents"], "is_enabled": True} for v in spec["variant_ids"]],
        "print_areas": [{"variant_ids": spec["variant_ids"], "placeholders": placeholders}],
    }
    p = call("POST", f"/shops/{shop_id()}/products.json", body)
    with open(os.path.join(pod_dir, "printify_product_id"), "w") as f:
        f.write(p["id"])
    print(f"created Printify product {p['id']}: {spec['title']}")
    for img in p.get("images", [])[:8]:
        print("mockup:", img.get("src"))


def publish(pod_dir):
    pid = open(os.path.join(pod_dir, "printify_product_id")).read().strip()
    call("POST", f"/shops/{shop_id()}/products/{pid}/publish.json",
         {"title": True, "description": True, "images": True, "variants": True, "tags": True,
          "keyFeatures": True, "shipping_template": True})
    open(os.path.join(pod_dir, "etsy_published"), "w").write(time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    print(f"publish requested for {pid}; Printify pushes it to Etsy within a few minutes")


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        sys.exit(__doc__)
    if a[0] == "shops":
        for s in call("GET", "/shops.json"):
            print(s["id"], s.get("sales_channel"), s.get("title"))
    elif a[0] == "blueprints":
        for b in call("GET", "/catalog/blueprints.json", auth=bool(os.environ.get("PRINTIFY_API_TOKEN"))):
            if len(a) < 2 or a[1].lower() in (b["title"] + " " + b.get("brand", "")).lower():
                print(b["id"], "|", b["title"], "|", b.get("brand"), b.get("model"))
    elif a[0] == "providers":
        for p in call("GET", f"/catalog/blueprints/{a[1]}/print_providers.json", auth=bool(os.environ.get("PRINTIFY_API_TOKEN"))):
            print(p["id"], p["title"], (p.get("location") or {}).get("country", ""))
    elif a[0] == "variants":
        v = call("GET", f"/catalog/blueprints/{a[1]}/print_providers/{a[2]}/variants.json", auth=bool(os.environ.get("PRINTIFY_API_TOKEN")))
        for x in v.get("variants", []):
            ph = ", ".join(f'{p["position"]} {p["width"]}x{p["height"]}' for p in x.get("placeholders", []))
            print(x["id"], x["title"], "|", ph)
    elif a[0] == "create":
        create(a[1])
    elif a[0] == "publish":
        publish(a[1])
    else:
        sys.exit(__doc__)
