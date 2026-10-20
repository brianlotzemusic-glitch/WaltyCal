"""007 reading mug wrap: one large luna moth rising from an open book (front), small holly sprigs and stars on the back."""
import os, math
import numpy as np
from PIL import Image, ImageFilter, ImageDraw
POD = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(POD, "007-moth-reading-mug")

def cut(path, pad=20):
    im = Image.open(path).convert("RGB"); a = np.asarray(im).astype(float)
    b = np.concatenate([a[:100].reshape(-1,3), a[-100:].reshape(-1,3)]); bg = np.median(b, 0)
    diff = np.abs(a - bg).max(2)
    ys, xs = np.where(diff > 30)
    x0, y0, x1, y1 = xs.min()-pad, ys.min()-pad, xs.max()+pad, ys.max()+pad
    im = im.crop((x0,y0,x1,y1)); diff = diff[y0:y1, x0:x1]
    m = Image.fromarray((np.clip((diff-4)/10,0,1)*255).astype(np.uint8)).filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(4))
    return im, m, bg

def put(canvas, im, m, cx, top=None, h=None, w=None, cy=None):
    s = (h/im.height) if h else (w/im.width)
    size = (round(im.width*s), round(im.height*s))
    im, m = im.resize(size, Image.LANCZOS), m.resize(size, Image.LANCZOS)
    y = top if top is not None else cy - size[1]//2
    canvas.paste(im, (cx-size[0]//2, y), m)
    return size

def star(canvas, cx, cy, R, col=(236,196,120)):
    S = 4; n = int(2*R*2+8)
    layer = Image.new("L", (n*S, n*S), 0); d = ImageDraw.Draw(layer); c = n*S/2
    pts = []
    for k in range(8):
        r = R*S if k % 2 == 0 else R*S*0.14
        ang = -math.pi/2 + k*math.pi/4
        pts.append((c + r*math.cos(ang), c + r*math.sin(ang)))
    d.polygon(pts, fill=255)
    canvas.paste(Image.new("RGB", (n,n), col), (round(cx-n/2), round(cy-n/2)), layer.resize((n,n), Image.LANCZOS))

moth, mm, bg = cut(os.path.join(POD, "006-moth-holly-tee/candidates/moth-2-up.png"))
book, bm, _ = cut(os.path.join(D, "candidates/book-1-up.png"))
W, H = 2700, 1120
canvas = Image.new("RGB", (W, H), tuple(int(round(c)) for c in bg))
# front: moth rises out of the open book
put(canvas, moth, mm, 1350, top=50, h=680)
put(canvas, book, bm, 1350, cy=715, w=840)
for x, y, R in [(900,230,14),(1860,200,12),(700,520,9),(2010,470,10),(1000,110,8),(1700,90,9),(620,330,6),(2090,330,6),(1000,700,7),(1700,700,7)]:
    star(canvas, x, y, R)
# back: stars only
for x, y, R in [(330,420,13),(240,540,8),(440,780,7),(560,300,6),(300,820,6),(2370,420,13),(2290,540,8),(2460,790,7),(2140,300,6),(2400,830,6),(1010,1010,6),(1700,1020,6)]:
    star(canvas, x, y, R)
canvas.save(os.path.join(D, "mug-wrap-2700x1120.png"), dpi=(300,300))
print(canvas.size)
