"""AI image generation for the shop factory. Uses Recraft when RECRAFT_API_KEY is set (preferred),
otherwise OpenAI when OPENAI_API_KEY is set.

Commands:
  python3 tools/imagegen.py gen "<prompt>" <out.png> [--size 1024x1024] [--pro] [--flash] [--n 4] [--transparent]
        raster image(s); with --n, files are saved as out-1.png ... out-N.png
  python3 tools/imagegen.py vector "<prompt>" <out.svg> [--pro] [--n 4]
        true vector SVG (Recraft only) - use for cut files and clean print art
  python3 tools/imagegen.py vectorize <in.png> <out.svg>   raster -> SVG (Recraft, $0.01)
  python3 tools/imagegen.py removebg <in.png> <out.png>    transparent background (Recraft)
  python3 tools/imagegen.py upscale <in.png> <out.png>     crisp 4x upscale for print (Recraft, $0.004)
  python3 tools/imagegen.py trace <in.png> <out.svg>       local, free: black-on-white art -> one SVG path
  python3 tools/imagegen.py spend                           estimated spend this month vs the cap, plus the Recraft balance

Environment (cloud environment settings, never committed):
  RECRAFT_API_KEY or OPENAI_API_KEY
  IMAGE_MONTHLY_BUDGET_USD   optional, default 5 (owner's cap, 3 Oct 2026);
  IMAGE_ALLOW_PRO=1          optional; --pro ($0.21-0.30 each) is refused without it
  generation stops when this month's estimate reaches it

Every call is logged to log/image-spend.csv (time, provider, model, est_usd, prompt).
Prompts must describe original designs: no artist names, brands, characters, trademarked phrases or other sellers' work.
Start every prompt from the style block in shop-profile/STYLE.md.
"""
import base64, csv, datetime, json, mimetypes, os, sys, time, urllib.error, urllib.request, uuid

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG = os.path.join(ROOT, "log", "image-spend.csv")
RECRAFT = "https://external.api.recraft.ai/v1"
# Recraft list prices (recraft.ai/docs/api-reference/pricing, checked 2 Oct 2026)
PRICE = {"recraftv4_1": 0.035, "recraftv4_1_pro": 0.21, "recraftv4_1_flash": 0.007,
         "recraftv4_1_vector": 0.08, "recraftv4_1_pro_vector": 0.30,
         "vectorize": 0.01, "removebg": 0.01, "upscale": 0.004, "openai": 0.08}


def month_spend():
    if not os.path.exists(LOG):
        return 0.0
    month = datetime.date.today().strftime("%Y-%m")
    total = 0.0
    with open(LOG) as f:
        for r in csv.reader(f):
            if r and r[0].startswith(month):
                try:
                    total += float(r[3])
                except (IndexError, ValueError):
                    total += PRICE["openai"]  # rows from the older format
    return total


BUDGET_FILE = os.path.join(ROOT, "log", "image-budget.json")  # {"YYYY-MM": "credits"} = owner topped up that month


def recraft_credits():
    """Prepaid Recraft credits left (1,000 credits = $1), or None if unknown."""
    if not os.environ.get("RECRAFT_API_KEY"):
        return None
    try:
        raw = http(RECRAFT + "/users/me", headers={"Authorization": f"Bearer {os.environ['RECRAFT_API_KEY']}"}, method="GET", retries=1)
        return int(json.loads(raw).get("credits"))
    except (SystemExit, ValueError, TypeError):
        return None


def check_budget(cost):
    month = datetime.date.today().strftime("%Y-%m")
    rule = json.load(open(BUDGET_FILE)).get(month) if os.path.exists(BUDGET_FILE) else None
    if os.environ.get("RECRAFT_API_KEY"):
        credits = recraft_credits()
        if credits is not None and credits < cost * 1000:
            sys.exit(f"Recraft is out of credits ({credits} left, need about {cost * 1000:.0f}); draw in code until the owner tops up or next month")
    if rule == "credits":
        return  # owner's one-time top-up: the prepaid Recraft balance is the limit this month
    cap = float(os.environ.get("IMAGE_MONTHLY_BUDGET_USD", "5"))
    if month_spend() + cost > cap:
        sys.exit(f"monthly image budget reached (${month_spend():.2f} of ${cap:.2f}); skip AI images until next month")


def log(provider, model, cost, prompt):
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    with open(LOG, "a", newline="") as f:
        csv.writer(f).writerow([datetime.datetime.utcnow().isoformat(timespec="seconds"), provider, model, f"{cost:.3f}", prompt[:300]])


def http(url, data=None, headers=None, method="POST", retries=3):
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, data, headers or {}, method=method), timeout=300) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            body = e.read().decode(errors="replace")[:500]
            if e.code in (429, 500, 502, 503) and attempt < retries - 1:
                time.sleep(2 ** (attempt + 1)); continue
            sys.exit(f"HTTP {e.code} from {url.split('/v1')[0]}: {body}")


def recraft_json(path, body):
    key = os.environ["RECRAFT_API_KEY"]
    raw = http(RECRAFT + path, json.dumps(body).encode(), {"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    return json.loads(raw)


def recraft_file(path, src, extra=None):
    key = os.environ["RECRAFT_API_KEY"]
    b = uuid.uuid4().hex
    parts = [f'--{b}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode() for k, v in (extra or {}).items()]
    ctype = mimetypes.guess_type(src)[0] or "image/png"
    parts.append(f'--{b}\r\nContent-Disposition: form-data; name="file"; filename="{os.path.basename(src)}"\r\nContent-Type: {ctype}\r\n\r\n'.encode()
                 + open(src, "rb").read() + b"\r\n")
    raw = http(RECRAFT + path, b"".join(parts) + f"--{b}--\r\n".encode(),
               {"Authorization": f"Bearer {key}", "Content-Type": f"multipart/form-data; boundary={b}"})
    return json.loads(raw)


def save_results(data, out, n):
    stem, ext = os.path.splitext(out)
    os.makedirs(os.path.dirname(os.path.abspath(out)) or ".", exist_ok=True)
    paths = []
    for i, item in enumerate(data["data"]):
        p = out if n == 1 else f"{stem}-{i + 1}{ext}"
        blob = base64.b64decode(item["b64_json"]) if item.get("b64_json") else http(item["url"], method="GET")
        with open(p, "wb") as f:
            f.write(blob)
        paths.append(p)
    return paths


def gen(prompt, out, size=None, pro=False, flash=False, n=1, transparent=False, vector=False):
    if os.environ.get("RECRAFT_API_KEY"):
        model = ("recraftv4_1_pro_vector" if pro else "recraftv4_1_vector") if vector else \
                ("recraftv4_1_flash" if flash else "recraftv4_1_pro" if pro else "recraftv4_1")
        if pro and os.environ.get("IMAGE_ALLOW_PRO") != "1":
            sys.exit("--pro is off (owner's rule, 3 Oct 2026): use --flash drafts, a standard final, then `upscale` ($0.004) or `vectorize` ($0.01) for print size")
        cost = PRICE[model] * n
        check_budget(cost)
        body = {"prompt": prompt, "model": model, "n": n, "response_format": "url"}
        if size:
            body["size"] = size
        if not vector:
            body["image_format"] = "png"
        data = recraft_json("/images/generations/vector" if vector else "/images/generations", body)
        paths = save_results(data, out, n)
        log("recraft", model, cost, prompt)
        if transparent and not vector:
            for p in paths:
                removebg(p, p)
    elif os.environ.get("OPENAI_API_KEY"):
        if vector:
            sys.exit("vector output needs RECRAFT_API_KEY; use gen + trace with OpenAI")
        model = os.environ.get("OPENAI_IMAGE_MODEL", "gpt-image-2")
        cost = PRICE["openai"] * n
        check_budget(cost)
        body = {"model": model, "prompt": prompt, "size": size or "1024x1024", "quality": "high", "n": n}
        if transparent:
            body.update(background="transparent", output_format="png")
        raw = http("https://api.openai.com/v1/images/generations", json.dumps(body).encode(),
                   {"Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}", "Content-Type": "application/json"})
        paths = save_results(json.loads(raw), out, n)
        log("openai", model, cost, prompt)
    else:
        sys.exit("no image generator configured: set RECRAFT_API_KEY (or OPENAI_API_KEY) in the environment")
    print(f"saved {', '.join(paths)} · ${month_spend():.2f} spent this month")


def vectorize(src, out):
    check_budget(PRICE["vectorize"])
    data = recraft_file("/images/vectorize", src, {"response_format": "url"})
    save_results(data if "data" in data else {"data": [data["image"]]}, out, 1)
    log("recraft", "vectorize", PRICE["vectorize"], src)
    print(f"vectorized {src} -> {out}")


def removebg(src, out):
    check_budget(PRICE["removebg"])
    data = recraft_file("/images/removeBackground", src, {"response_format": "url"})
    save_results(data if "data" in data else {"data": [data["image"]]}, out, 1)
    log("recraft", "removebg", PRICE["removebg"], src)


def upscale(src, out):
    check_budget(PRICE["upscale"])
    data = recraft_file("/images/crispUpscale", src, {"response_format": "url"})
    save_results(data if "data" in data else {"data": [data["image"]]}, out, 1)
    log("recraft", "upscale", PRICE["upscale"], src)
    print(f"upscaled {src} -> {out}")


def trace(src, out, threshold=128):
    """Local and free: black-on-white artwork -> one filled SVG path (evenodd)."""
    from PIL import Image
    import numpy as np, potrace
    im = Image.open(src).convert("RGBA")
    bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
    gray = Image.alpha_composite(bg, im).convert("L")
    bmp = potrace.Bitmap(np.array(gray) >= threshold)  # potracer fills the False (dark) pixels
    path = bmp.trace(turdsize=40, opttolerance=0.4)
    d = []
    for curve in path:
        d.append(f"M{curve.start_point.x:.1f},{curve.start_point.y:.1f}")
        for seg in curve.segments:
            if seg.is_corner:
                d.append(f"L{seg.c.x:.1f},{seg.c.y:.1f} L{seg.end_point.x:.1f},{seg.end_point.y:.1f}")
            else:
                d.append(f"C{seg.c1.x:.1f},{seg.c1.y:.1f} {seg.c2.x:.1f},{seg.c2.y:.1f} {seg.end_point.x:.1f},{seg.end_point.y:.1f}")
        d.append("Z")
    w, h = im.size
    with open(out, "w") as f:
        f.write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="6in" height="{6*h/w:.3f}in">'
                f'<path fill="#000" fill-rule="evenodd" d="{" ".join(d)}"/></svg>')
    print(f"traced {src} -> {out} ({len(path)} curves)")


def opt(a, name, default=None):
    return a[a.index(name) + 1] if name in a else default


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        sys.exit(__doc__)
    cmd = a[0]
    if cmd in ("gen", "vector") and len(a) >= 3:
        gen(a[1], a[2], size=opt(a, "--size"), pro="--pro" in a, flash="--flash" in a,
            n=int(opt(a, "--n", 1)), transparent="--transparent" in a, vector=(cmd == "vector"))
    elif cmd == "vectorize" and len(a) == 3:
        vectorize(a[1], a[2])
    elif cmd == "removebg" and len(a) == 3:
        removebg(a[1], a[2])
    elif cmd == "upscale" and len(a) == 3:
        upscale(a[1], a[2])
    elif cmd == "trace" and len(a) == 3:
        trace(a[1], a[2])
    elif cmd == "spend":
        month = datetime.date.today().strftime("%Y-%m")
        topped = os.path.exists(BUDGET_FILE) and json.load(open(BUDGET_FILE)).get(month) == "credits"
        print(f"${month_spend():.2f} spent this month" + (" (owner top-up month: the Recraft balance is the limit)" if topped
              else f" of ${float(os.environ.get('IMAGE_MONTHLY_BUDGET_USD', '5')):.2f}"))
        c = recraft_credits()
        if c is not None:
            print(f"Recraft balance: {c} credits (about ${c / 1000:.2f})")
    else:
        sys.exit(__doc__)
