"""AI image generation for the shop factory (OpenAI Images API).

Commands:
  python3 tools/imagegen.py gen "<prompt>" <out.png> [--size 1024x1024] [--transparent] [--quality high]
  python3 tools/imagegen.py trace <in.png> <out.svg>     bitmap -> single-colour vector (for cut files)
  python3 tools/imagegen.py spend                         images generated this month vs the cap

Environment (cloud environment settings, never committed):
  OPENAI_API_KEY            OpenAI API key (platform.openai.com, not a ChatGPT subscription)
  OPENAI_IMAGE_MODEL        optional, default gpt-image-2
  IMAGE_MONTHLY_CAP         optional, max images per calendar month, default 400

Every generation is logged to log/image-spend.csv (date, model, size, quality, prompt).
Prompts must describe original designs: no artist names, brands, characters, or other sellers' work.
"""
import base64, csv, datetime, json, os, sys, urllib.error, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG = os.path.join(ROOT, "log", "image-spend.csv")
API = "https://api.openai.com/v1/images/generations"


def month_count():
    if not os.path.exists(LOG):
        return 0
    month = datetime.date.today().strftime("%Y-%m")
    with open(LOG) as f:
        return sum(1 for r in csv.reader(f) if r and r[0].startswith(month))


def gen(prompt, out, size="1024x1024", transparent=False, quality="high"):
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        sys.exit("missing OPENAI_API_KEY")
    cap = int(os.environ.get("IMAGE_MONTHLY_CAP", "400"))
    if month_count() >= cap:
        sys.exit(f"monthly image cap reached ({cap}); skip AI images until next month")
    model = os.environ.get("OPENAI_IMAGE_MODEL", "gpt-image-2")
    body = {"model": model, "prompt": prompt, "size": size, "quality": quality, "n": 1}
    if transparent:
        body["background"] = "transparent"
        body["output_format"] = "png"
    for attempt in range(3):
        req = urllib.request.Request(API, json.dumps(body).encode(),
                                     {"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
        try:
            data = json.load(urllib.request.urlopen(req, timeout=300))
            break
        except urllib.error.HTTPError as e:
            msg = e.read().decode()[:400]
            if e.code == 400 and "background" in msg and "background" in body:
                body.pop("background"); body.pop("output_format", None)  # model can't do transparency
                continue
            if e.code in (429, 500, 502, 503) and attempt < 2:
                continue
            sys.exit(f"OpenAI {e.code}: {msg}")
    img = base64.b64decode(data["data"][0]["b64_json"])
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    with open(out, "wb") as f:
        f.write(img)
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    with open(LOG, "a", newline="") as f:
        csv.writer(f).writerow([datetime.datetime.utcnow().isoformat(timespec="seconds"), model, size, quality, prompt[:300]])
    print(f"saved {out} ({len(img)//1024} KB) · {month_count()}/{cap} images this month")


def trace(src, out, threshold=128):
    """Black-on-white artwork -> one filled SVG path (evenodd), ready for the cut-file checks."""
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


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        sys.exit(__doc__)
    if a[0] == "gen" and len(a) >= 3:
        opts = dict(size="1024x1024", transparent="--transparent" in a, quality="high")
        if "--size" in a:
            opts["size"] = a[a.index("--size") + 1]
        if "--quality" in a:
            opts["quality"] = a[a.index("--quality") + 1]
        gen(a[1], a[2], **opts)
    elif a[0] == "trace" and len(a) == 3:
        trace(a[1], a[2])
    elif a[0] == "spend":
        print(f"{month_count()}/{os.environ.get('IMAGE_MONTHLY_CAP', '400')} images this month")
    else:
        sys.exit(__doc__)
