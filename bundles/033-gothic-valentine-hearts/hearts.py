"""Gothic Valentine hearts - six single-path cut files drawn in code ($0 AI).
Canvas 1000 x 1000 (y down). Every design is unioned into ONE connected piece."""
import math
from lib import *


def heart_curve(cx, cy, s, n=240):
    pts = []
    for i in range(n):
        t = 2 * math.pi * i / n
        x = 16 * math.sin(t) ** 3
        y = 13 * math.cos(t) - 5 * math.cos(2*t) - 2 * math.cos(3*t) - math.cos(4*t)
        pts.append((cx + x * s, cy - y * s))
    return pts


def heart_shape(cx, cy, s):
    return Polygon(heart_curve(cx, cy, s)).buffer(0)


def mirror_x(g, cx=500):
    return affinity.scale(g, -1, 1, origin=(cx, 0))


def sym(g, cx=500):
    return U([g, mirror_x(g, cx)])


def slit(pts, w=17):
    return line(pts, w, smooth=True)


def tube(pts, w0, w1, n=14, flat=True):
    """Smooth tapering vessel along a spline: flat-cut far end (like a severed vessel), width w0 -> w1."""
    sp = spline(pts, closed=False, n=n)
    N = len(sp)
    left, right = [], []
    for i, (x, y) in enumerate(sp):
        a, b = sp[max(i - 1, 0)], sp[min(i + 1, N - 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L, dx / L
        w = (w0 + (w1 - w0) * i / (N - 1)) / 2
        left.append((x + nx * w, y + ny * w)); right.append((x - nx * w, y - ny * w))
    return Polygon(left + right[::-1]).buffer(0)


def d_anatomical():
    body = shape([(452, 888, 'c'), (560, 820), (680, 705), (770, 570), (790, 450), (748, 358), (672, 322),
                  (596, 338), (540, 392), (470, 372), (396, 340), (312, 346), (246, 410), (222, 510),
                  (252, 628), (330, 748), (402, 832)])
    # aortic arch (largest, ~0.45 in): rises from the top centre, arches over to the left, runs down as a tapering stump
    aorta = tube([(552, 440), (556, 320), (532, 220), (466, 165), (400, 178), (368, 232), (360, 276)], 82, 50)
    # pulmonary trunk (medium, ~0.35 in): leans out to the upper left, behind the arch
    pulm = tube([(372, 420), (306, 372), (250, 330), (216, 300)], 64, 42)
    # superior vena cava (slimmest, ~0.25 in): straight stub on the right, flared at its base
    cava = tube([(704, 440), (702, 330), (706, 220), (710, 150)], 66, 38)
    # short branch stubs (brachiocephalic-style) off the arch and the cava
    br1 = tube([(478, 190), (472, 150), (474, 112)], 34, 26)
    br2 = tube([(704, 300), (742, 276), (772, 262)], 30, 24)
    g = U([body, aorta, pulm, cava, br1, br2]).buffer(26, quad_segs=16).buffer(-26, quad_segs=16)
    # coronary-style grooves: taper from wide (top) to narrow and branch like arteries (all slots >= 0.10 in = 15 units)
    holes = [
        tube([(528, 478), (512, 570), (496, 660), (472, 770)], 25, 18),      # anterior descending trunk
        tube([(510, 580), (556, 620), (584, 668)], 20, 17),                  # branch right
        tube([(490, 672), (450, 700), (424, 742)], 20, 17),                  # branch left
        tube([(450, 486), (380, 512), (338, 566), (330, 636)], 25, 18),      # circumflex
        tube([(352, 540), (398, 574), (410, 628)], 20, 17),                  # branch
        tube([(608, 478), (672, 510), (700, 570), (696, 644)], 25, 18),      # right coronary
        tube([(688, 540), (648, 566), (630, 606)], 20, 17),                  # branch
    ]
    return fit(g.difference(U(holes)), 900)


# ------------------------------------------------------------------ 02 bat heart
def d_bat_heart():
    body = heart_shape(500, 570, 14)
    ears = sym(Polygon([(520, 400), (556, 290), (606, 420)]))
    wing = shape([(580, 480, 'c'), (650, 385), (740, 325), (850, 292), (975, 300, 'c'), (895, 400),
                  (930, 520, 'c'), (840, 545), (800, 640, 'c'), (745, 590), (690, 660, 'c'), (640, 610), (590, 620, 'c')])
    notch_fill = Polygon([(476, 392), (500, 432), (524, 392), (524, 505), (476, 505)])   # clean simple V between the ears
    solid = U([body, ears, notch_fill, wing, mirror_x(wing)]).buffer(14, quad_segs=16).buffer(-14, quad_segs=16)
    holes = [circ(455, 540, 22), circ(545, 540, 22),
             slit([(745, 390), (850, 430), (900, 480)], 17),
             slit([(730, 420), (770, 520), (790, 580)], 17)]
    holes += [mirror_x(h) for h in holes[2:]]
    return fit(solid.difference(U(holes)), 900)


# ------------------------------------------------------------------ 03 thorned heart wreath
def vine_points(phase, amp, s=33, n=420, cx=500, cy=520):
    pts = []
    for i in range(n + 1):
        t = 2 * math.pi * i / n
        x = 16 * math.sin(t) ** 3
        y = 13 * math.cos(t) - 5 * math.cos(2*t) - 2 * math.cos(3*t) - math.cos(4*t)
        dx = 16 * 3 * math.sin(t) ** 2 * math.cos(t)
        dy = -13 * math.sin(t) + 10 * math.sin(2*t) + 6 * math.sin(3*t) + 4 * math.sin(4*t)
        L = math.hypot(dx, dy) or 1
        nx, ny = dy / L, -dx / L      # outward-ish normal (screen y flipped handled below)
        off = amp * math.sin(t * 9 + phase)
        pts.append((cx + x * s + nx * off, cy - y * s + ny * off * -1))
    return pts


def thorn(p, q, base=30, length=46):
    """Thorn at p pointing along direction p->q normal."""
    dx, dy = q[0] - p[0], q[1] - p[1]
    L = math.hypot(dx, dy) or 1
    ux, uy = dx / L, dy / L
    nx, ny = -uy, ux
    return Polygon([(p[0] - ux*base/2, p[1] - uy*base/2), (p[0] + ux*base/2, p[1] + uy*base/2),
                    (p[0] + nx*length + ux*8, p[1] + ny*length + uy*8)])


def rose(x, y, r=62, rot=0):
    petals = [ellipse(x + r*0.55*math.cos(math.radians(a)), y + r*0.55*math.sin(math.radians(a)), r*0.62, r*0.5, a)
              for a in [rot + k * 72 for k in range(5)]]
    return U(petals + [circ(x, y, r*0.5)])


def d_thorn_wreath():
    A = vine_points(0.0, 8)
    base = vine_points(0.0, 0)
    solid = [line(A, 44)]
    ridx = [int(len(base) * f) for f in (0.16, 0.84, 0.5)]
    def ok(k):
        return all(abs(k - r) > 28 for r in ridx) and 40 < k < len(base) - 40
    for k in range(8, len(base) - 8, 34):
        if not ok(k):
            continue
        p, q = base[k], base[k + 2]
        th = thorn(p, q, 38, 112)
        if (k // 34) % 2:
            th = affinity.rotate(th, 180, origin=p)
        solid.append(th)
    for k in range(23, len(base) - 8, 60):
        if not ok(k):
            continue
        p, q = base[k], base[k + 3]
        ang = math.degrees(math.atan2(q[1] - p[1], q[0] - p[0]))
        solid.append(leaf_at(p, ang + (75 if (k // 60) % 2 else -75), 112, 36))
    roses = []
    for idx in (int(len(base) * 0.16), int(len(base) * 0.84), int(len(base) * 0.5)):
        x, y = base[idx]
        roses.append(rose(x, y, 76, idx))
    g = U(solid + roses).buffer(10, quad_segs=16).buffer(-10, quad_segs=16)
    g = U([Polygon(p.exterior, [i for i in p.interiors if Polygon(i).area > 20000]) for p in (g.geoms if g.geom_type == 'MultiPolygon' else [g])])
    g = g.difference(U([circ(r.centroid.x, r.centroid.y, 26) for r in roses]))
    return fit(g, 900)


def leaf_at(p, ang, L, W):
    pts = [(0, 0, 'c'), (L*0.3, -W*0.55), (L*0.7, -W*0.38), (L, 0, 'c'), (L*0.7, W*0.38), (L*0.3, W*0.55)]
    g = shape(pts)
    return affinity.translate(affinity.rotate(g, ang, origin=(0, 0)), p[0], p[1])


# ------------------------------------------------------------------ 04 heart padlock
def d_padlock():
    body = heart_shape(500, 612, 25)
    # pointed (ogee-style) shackle, joined into the heart's top dip
    sh_out = shape([(330, 470, 'c'), (322, 320), (380, 190), (500, 100, 'c'), (620, 190), (678, 320), (670, 470, 'c')])
    sh_in = shape([(384, 480, 'c'), (378, 330), (424, 232), (500, 168, 'c'), (576, 232), (622, 330), (616, 480, 'c')])
    shackle = sh_out.difference(sh_in)
    keyhole = U([circ(500, 600, 52), Polygon([(466, 640), (534, 640), (560, 790), (440, 790)])])
    # rivet holes dropped: with the keyhole they read as a face
    g = U([body, shackle]).buffer(14, quad_segs=16).buffer(-14, quad_segs=16)
    return fit(g.difference(keyhole), 900)


# ------------------------------------------------------------------ 05 skeleton key with heart bow
def d_key():
    bow = heart_shape(500, 255, 13.5)
    bow_hole = bow.buffer(-38, quad_segs=16)       # even wall all round (about 0.25 in after fitting)
    shaft = box(480, 450, 520, 884)                # starts inside the heart point, one clean squared end
    bit = U([box(500, 700, 700, 744), box(500, 770, 640, 814), box(500, 840, 700, 884), box(500, 700, 530, 884)])
    g = U([bow.difference(bow_hole), shaft, bit]).buffer(10, quad_segs=16).buffer(-10, quad_segs=16)
    g = affinity.rotate(g, -40, origin=(500, 500))
    return fit(g, 900)


# ------------------------------------------------------------------ 06 gothic arch window with heart
def d_arch_window():
    half = [(500, 60), (580, 124), (655, 192), (718, 268), (758, 346), (775, 430), (780, 540), (780, 700), (780, 940)]
    outer = shape([(500, 60, 'c')] + [(x, y) for x, y in half[1:-1]] + [(780, 940, 'c'), (220, 940, 'c')] + [(1000 - x, y) for x, y in half[1:-1]][::-1])
    # arched lancet windows (pointed heads)
    def lancet(cx, w, top, bot):
        h = w / 2
        return shape([(cx - h, bot, 'c'), (cx - h, top + 150), (cx - h*0.7, top + 70), (cx, top, 'c'),
                      (cx + h*0.7, top + 70), (cx + h, top + 150), (cx + h, bot, 'c')])
    win = [lancet(375, 140, 470, 880), lancet(625, 140, 470, 880)]
    ht = heart_shape(500, 330, 9.5)
    small = [circ(500, 232, 0.01)]
    sill = []
    g = outer.difference(U(win + [ht]))
    # little bats in the upper corners are not drawn: frame stays plain and strong
    return fit(g, 900)
