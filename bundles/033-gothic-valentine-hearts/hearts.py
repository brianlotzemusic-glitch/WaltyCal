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


# ------------------------------------------------------------------ 01 anatomical heart
def d_anatomical():
    body = shape([(452, 888, 'c'), (560, 820), (680, 705), (770, 570), (790, 450), (748, 358), (672, 322),
                  (596, 338), (540, 392), (470, 372), (396, 340), (312, 346), (246, 410), (222, 510),
                  (252, 628), (330, 748), (402, 832)])
    aorta = curve_taper([(560, 400), (556, 260), (490, 170), (390, 150)], 104, 88)
    pulm = curve_taper([(400, 380), (350, 330), (300, 290)], 96, 84)
    cava = curve_taper([(690, 360), (700, 250), (700, 140)], 100, 88)
    g = U([body, aorta, pulm, cava]).buffer(16, quad_segs=16).buffer(-16, quad_segs=16)
    holes = [
        slit([(520, 470), (500, 580), (478, 690), (454, 780)], 19),
        slit([(430, 470), (350, 510), (318, 590), (350, 680)], 17),
        slit([(600, 470), (676, 500), (706, 570), (690, 650)], 17),
        slit([(556, 700), (610, 650), (640, 600)], 17),
        slit([(406, 700), (372, 750)], 17),
    ]
    return fit(g.difference(U(holes)), 900)


# ------------------------------------------------------------------ 02 bat heart
def d_bat_heart():
    body = heart_shape(500, 570, 14)
    ears = sym(Polygon([(520, 400), (556, 290), (606, 420)]))
    wing = shape([(580, 480, 'c'), (650, 385), (740, 325), (850, 292), (975, 300, 'c'), (895, 400),
                  (930, 520, 'c'), (840, 545), (800, 640, 'c'), (745, 590), (690, 660, 'c'), (640, 610), (590, 620, 'c')])
    solid = U([body, ears, wing, mirror_x(wing)]).buffer(14, quad_segs=16).buffer(-14, quad_segs=16)
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
        th = thorn(p, q, 58, 125)
        if (k // 34) % 2:
            th = affinity.rotate(th, 180, origin=p)
        solid.append(th)
    for k in range(23, len(base) - 8, 60):
        if not ok(k):
            continue
        p, q = base[k], base[k + 3]
        ang = math.degrees(math.atan2(q[1] - p[1], q[0] - p[0]))
        solid.append(leaf_at(p, ang + (75 if (k // 60) % 2 else -75), 130, 66))
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
    rivets = [circ(x, y, 17) for x, y in ((300, 520), (700, 520))]
    g = U([body, shackle]).buffer(14, quad_segs=16).buffer(-14, quad_segs=16)
    return fit(g.difference(U([keyhole] + rivets)), 900)


# ------------------------------------------------------------------ 05 skeleton key with heart bow
def d_key():
    bow = heart_shape(500, 200, 15.5)
    bow_hole = heart_shape(500, 207, 7.8)
    collar = Point(500, 380).buffer(0.01)
    shaft = taper((500, 372), (500, 880), 40, 46)
    bit = U([box(500, 700, 700, 744), box(500, 770, 640, 814), box(500, 840, 700, 884), box(500, 700, 530, 884)])
    tip = Polygon([(477, 880), (523, 880), (508, 920), (492, 920)])
    g = U([bow.difference(bow_hole), collar, shaft, bit, tip]).buffer(10, quad_segs=16).buffer(-10, quad_segs=16)
    g = affinity.rotate(g, -32, origin=(500, 500))
    return fit(g, 900)


# ------------------------------------------------------------------ 06 gothic arch window with heart
def d_arch_window():
    outer = shape([(220, 940, 'c'), (220, 420), (250, 300), (330, 200), (410, 130), (500, 60, 'c'),
                   (590, 130), (670, 200), (750, 300), (780, 420), (780, 940, 'c')])
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
