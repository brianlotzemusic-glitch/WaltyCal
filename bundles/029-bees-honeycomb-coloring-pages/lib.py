"""Tiny line-art toolkit for the bee coloring pages: everything is drawn in code, no AI.

Canvas = the 896 x 1152 'draft' space that process.py expects (art/raw/NN-slug.png). Shapes are drawn back to
front: each closed shape is filled white (hiding what is behind it) and then outlined, so wings can sit behind
a body and a bee in front of a flower. Stroke weight W is fixed in draft units (10 units is ~2 mm printed).
"""
import math
from PIL import Image, ImageDraw

K = 3                     # supersampling: draw at 3x, store at 1x
CW, CH = 896, 1152
W = 10.0                  # outline weight, draft units (~2 mm printed)


class Canvas:
    def __init__(self):
        self.im = Image.new("L", (CW * K, CH * K), 255)
        self.d = ImageDraw.Draw(self.im)

    # --- low level -----------------------------------------------------------------------------
    def _p(self, pts):
        return [(x * K, y * K) for x, y in pts]

    def stroke(self, pts, w=W):
        """Open polyline with round joins and caps."""
        pp = self._p(pts)
        self.d.line(pp, fill=0, width=int(w * K), joint="curve")
        r = w * K / 2
        for x, y in (pp[0], pp[-1]):
            self.d.ellipse([x - r, y - r, x + r, y + r], fill=0)

    def poly(self, pts, fill=255, w=W, outline=True):
        pp = self._p(pts)
        if fill is not None:
            self.d.polygon(pp, fill=fill)
        if outline:
            self.stroke(list(pts) + [pts[0]], w)

    def dot(self, x, y, r):
        self.d.ellipse([(x - r) * K, (y - r) * K, (x + r) * K, (y + r) * K], fill=0)

    def save(self, path):
        self.im.resize((CW, CH), Image.LANCZOS).save(path)


def spline(pts, closed=False, n=14):
    """Catmull-Rom through pts."""
    P = list(pts)
    if closed:
        P = [P[-1]] + P + [P[0], P[1]]
    else:
        P = [P[0]] + P + [P[-1]]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for j in range(n):
            t = j / n
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * ((2 * p1[k]) + (-p0[k] + p2[k]) * t + (2 * p0[k] - 5 * p1[k] + 4 * p2[k] - p3[k]) * t2
                                    + (-p0[k] + 3 * p1[k] - 3 * p2[k] + p3[k]) * t3) for k in (0, 1)))
    if not closed:
        out.append(tuple(pts[-1]))
    return out


def ellipse_pts(cx, cy, rx, ry, rot=0.0, n=72, a0=0.0, a1=360.0):
    out = []
    cr, sr = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    for i in range(n + 1 if a1 - a0 < 360 else n):
        a = math.radians(a0 + (a1 - a0) * i / n)
        x, y = rx * math.cos(a), ry * math.sin(a)
        out.append((cx + x * cr - y * sr, cy + x * sr + y * cr))
    return out


def xf(pts, ox, oy, s=1.0, rot=0.0, flip=False):
    cr, sr = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    out = []
    for x, y in pts:
        x, y = x * s, y * s
        if flip:
            x = -x
        out.append((ox + x * cr - y * sr, oy + x * sr + y * cr))
    return out


def ellipse(c, cx, cy, rx, ry, rot=0.0, fill=255):
    c.poly(ellipse_pts(cx, cy, rx, ry, rot), fill=fill)


def circle(c, cx, cy, r, fill=255):
    ellipse(c, cx, cy, r, r, 0, fill)


def smooth(c, pts, closed=True, fill=255, w=W):
    sp = spline(pts, closed)
    if closed:
        c.poly(sp, fill=fill, w=w)
    else:
        c.stroke(sp, w)


def ribbon(path, w0, w1=None):
    """Closed outline of a stem following path (list of pts), width tapering w0 -> w1."""
    w1 = w0 if w1 is None else w1
    n = len(path)
    L, R = [], []
    for i, (x, y) in enumerate(path):
        a = path[max(i - 1, 0)]
        b = path[min(i + 1, n - 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        d = math.hypot(dx, dy) or 1
        nx, ny = -dy / d, dx / d
        w = (w0 + (w1 - w0) * i / (n - 1)) / 2
        L.append((x + nx * w, y + ny * w))
        R.append((x - nx * w, y - ny * w))
    return L + R[::-1]


def stem(c, pts, w0=26, w1=None, fill=255):
    path = spline(pts, False, 10)
    w1 = w0 if w1 is None else w1
    c.poly(ribbon(path, max(w0, 30), max(w1, 28)), fill=fill)


def leaf(c, x, y, length, width, rot, vein=True):
    """Pointed leaf from base (x, y) pointing along rot (deg, 0 = right)."""
    cr, sr = math.cos(math.radians(rot)), math.sin(math.radians(rot))

    def T(u, v):
        return (x + u * cr - v * sr, y + u * sr + v * cr)
    top = [T(length * t, -width * math.sin(math.pi * t) ** 0.8 * (1 - 0.2 * t)) for t in [i / 10 for i in range(0, 11)]]
    bot = [T(length * t, width * math.sin(math.pi * t) ** 0.8 * (1 - 0.2 * t)) for t in [i / 10 for i in range(10, -1, -1)]]
    pts = spline(top + bot[1:-1], True, 6)
    c.poly(pts)
    if vein:
        c.stroke([T(length * 0.12, 0), T(length * 0.6, 0)], W * 0.9)


def petal_flower(c, cx, cy, R, n, r_center, petal_w=None, rot=0.0, pointed=False, dots=True):
    """Daisy: n petals around a centre disc. R is roughly the petal length measured from the disc edge."""
    inner = r_center * 0.9
    outer = R + r_center * 0.6
    mid, ln = (inner + outer) / 2, (outer - inner) / 2
    petal_w = petal_w or min(mid * math.sin(math.pi / n) * (1.0 if pointed else 0.98), ln * 0.9)
    for i in range(n):
        a = rot + 360.0 * i / n
        px, py = cx + mid * math.cos(math.radians(a)), cy + mid * math.sin(math.radians(a))
        if pointed:
            pts = [(-ln, 0), (-ln * 0.3, -petal_w), (ln, 0), (-ln * 0.3, petal_w)]
            c.poly(xf(spline(pts, True, 8), px, py, 1, a))
        else:
            ellipse(c, px, py, ln, petal_w, a)
    circle(c, cx, cy, r_center)
    if dots:
        k = max(r_center * 0.45, 12)
        for dx, dy in [(0, 0), (k, 0), (-k, 0), (0, k), (0, -k)][:5 if r_center > 38 else 1]:
            c.dot(cx + dx, cy + dy, 5)


def hexagon(cx, cy, L, rot=0.0):
    return [(cx + L * math.cos(math.radians(rot + 60 * i)), cy + L * math.sin(math.radians(rot + 60 * i))) for i in range(6)]


def hexcell(c, cx, cy, L, fill=255):
    c.poly(hexagon(cx, cy, L), fill=fill, w=W)


def cloud(c, cx, cy, s=1.0):
    pts = [(-90, 20), (-95, -10), (-60, -30), (-35, -62), (5, -70), (40, -50), (70, -42), (100, -10), (90, 20)]
    pts = xf(pts, cx, cy, s)
    c.poly(spline(pts, True, 10))


def sun(c, cx, cy, r, rays=12):
    for i in range(rays):
        a = 360 * i / rays
        p0 = (cx + (r + 18) * math.cos(math.radians(a)), cy + (r + 18) * math.sin(math.radians(a)))
        p1 = (cx + (r + 62) * math.cos(math.radians(a)), cy + (r + 62) * math.sin(math.radians(a)))
        c.stroke([p0, p1], W + 2)
    circle(c, cx, cy, r)


# --- the bee -------------------------------------------------------------------------------------
def bee(c, ox, oy, s=1.0, rot=0.0, flip=False, mood="happy", crown=False, wings_up=True, fuzzy=False, stripes=2):
    """A chunky cartoon bee facing right in local coords: body ~200 long, ~125 tall at s=1."""
    def T(pts):
        return xf(pts, ox, oy, s, rot, flip)

    # wings (behind the body): two teardrops rising from the back
    for ang, bx, ln in ((-118, -20, 92), (-80, 22, 80)):
        a = math.radians(ang)
        cxw, cyw = bx + (ln / 2) * math.cos(a), -40 + (ln / 2) * math.sin(a)
        if not wings_up:
            cyw += 25
        wing = ellipse_pts(cxw, cyw, ln / 2 + 6, 32, ang, 48)
        c.poly(T(wing))
        v = [(cxw - (ln / 2 - 18) * math.cos(a), cyw - (ln / 2 - 18) * math.sin(a)), (cxw + (ln / 6) * math.cos(a), cyw + (ln / 6) * math.sin(a))]
        c.stroke(T(v), W * 0.9)
    # legs
    for lx in (-40, 5, 50):
        c.stroke(T([(lx, 54), (lx - 6, 78), (lx + 8, 92)]), W)
    # antennae
    for ang, ln in ((-62, 66), (-28, 62)):
        a = math.radians(ang)
        base = (96, -36)
        tip = (base[0] + ln * math.cos(a), base[1] + ln * math.sin(a))
        mid = ((base[0] + tip[0]) / 2 - 8, (base[1] + tip[1]) / 2 - 6)
        c.stroke(T(spline([base, mid, tip], False, 8)), W)
        circle_pts = xf(ellipse_pts(0, 0, 11, 11, 0, 24), tip[0], tip[1])
        c.poly(T(circle_pts))
    # stinger
    c.poly(T([(-100, 8), (-136, 20), (-100, 32)]))
    # body
    if fuzzy:
        pts = []
        for i in range(28):
            a = 2 * math.pi * i / 28
            r = 1 + (0.045 if i % 2 else -0.01)
            pts.append((-8 + 104 * r * math.cos(a), 12 + 68 * r * math.sin(a)))
        c.poly(T(spline(pts, True, 5)))
    else:
        c.poly(T(ellipse_pts(-8, 12, 104, 66, 0, 90)))
    # stripes: curved bands bowed toward the head, endpoints on the body outline
    xs = {2: (-52, -2), 3: (-62, -25, 12)}[stripes]
    for xline in xs:
        t = (xline + 8) / 104.0
        yy = 66 * math.sqrt(max(0.0, 1 - t * t))
        top, bot = (xline, 12 - yy + 2), (xline, 12 + yy - 2)
        c.stroke(T(spline([top, (xline + 15, 12), bot], False, 12)), W)
    # head
    c.poly(T(ellipse_pts(90, -4, 50, 47, 0, 72)))
    # eyes + smile + cheek
    ex, ey = (102, -16)
    if mood == "sleep":
        c.stroke(T(spline([(ex - 14, ey), (ex, ey + 8), (ex + 14, ey)], False, 8)), W * 0.9)
    else:
        c.dot(*T([(ex, ey)])[0], 7.5 * s ** 0.3)
    smile = ellipse_pts(ex + 6, ey + 14, 16, 11, 0, 14, 10, 170)
    c.stroke(T(smile), W * 0.9)
    if crown:
        cr = [(52, -42), (56, -88), (74, -62), (90, -98), (106, -62), (124, -88), (128, -40)]
        c.poly(T(cr))
    return None
