"""Small Autumn Moments: 22 original woodland icons drawn in code (shapely).

Line-art style with spot colour: every shape is outlined in plum (LW units in
a 1000-unit box, y down) and filled with one of the shop colours; details are
plum strokes. Same helpers as bundle 010. Output: icons/NN-name.svg,
icons.json (SVG body + the silhouette used for sticker cut lines).
"""
import math, os, json
from shapely.geometry import LineString, Point, Polygon, box, mapping
from shapely.ops import unary_union
from shapely import affinity

HERE = os.path.dirname(os.path.abspath(__file__))
PLUM, PINE, BERRY, GOLD, CREAM, WHITE = "#2c1b36", "#2f4a3a", "#8b2f3c", "#e8c97a", "#f1e6cf", "#ffffff"
LW = 26   # outline width (1000-unit space, before fit)


# ---------------------------------------------------------------- helpers
def catmull(pts, closed=True, n=14):
    out, P, m = [], list(pts), len(pts)
    rng = range(m) if closed else range(m - 1)
    for i in rng:
        p0 = P[(i - 1) % m] if closed else P[max(i - 1, 0)]
        p1, p2 = P[i], P[(i + 1) % m] if closed else P[i + 1]
        p3 = P[(i + 2) % m] if closed else P[min(i + 2, m - 1)]
        for k in range(n):
            t = k / n; t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2 +
                                    (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3) for j in (0, 1)))
    if not closed:
        out.append(P[-1])
    return out


def S(pts):
    return Polygon(catmull(pts)).buffer(0)


def Pg(pts, r=0):
    g = Polygon(pts).buffer(0)
    return g.buffer(-r).buffer(r) if r else g


def L(pts, w, cap=1, smooth=False):
    if smooth:
        pts = catmull(pts, closed=False)
    return LineString(pts).buffer(w / 2, cap_style=cap, join_style=1)


def C(x, y, r):
    return Point(x, y).buffer(r, 64)


def E(x, y, rx, ry, rot=0):
    return affinity.rotate(affinity.scale(Point(x, y).buffer(1, 64), rx, ry), rot, origin=(x, y))


def R(x0, y0, x1, y1, r=0):
    return box(x0, y0, x1, y1).buffer(-r).buffer(r) if r else box(x0, y0, x1, y1)


def mir(g, cx=500):
    return affinity.scale(g, -1, 1, origin=(cx, 0))


def sym(g, cx=500):
    return unary_union([g, mir(g, cx)])


def U(*gs):
    return unary_union(list(gs))


def star(x, y, Ro, Ri, n=5, rot=-90, round_=0):
    pts = []
    for k in range(2 * n):
        a = math.radians(rot + 180 * k / n)
        rr = Ro if k % 2 == 0 else Ri
        pts.append((x + rr * math.cos(a), y + rr * math.sin(a)))
    g = Polygon(pts)
    return g.buffer(-round_).buffer(round_) if round_ else g


def sparkle(x, y, r):
    return star(x, y, r, r * 0.3, n=4, rot=-90, round_=3)


def snowflake(x, y, r, w, rot=0):
    parts = [C(x, y, w * 1.1)]
    for k in range(6):
        a = math.radians(rot + 60 * k - 90)
        parts.append(L([(x, y), (x + r * math.cos(a), y + r * math.sin(a))], w))
        for f, bl in ((0.5, 0.36), (0.76, 0.24)):
            bx, by = x + f * r * math.cos(a), y + f * r * math.sin(a)
            for s in (-1, 1):
                b = a + s * math.radians(55)
                parts.append(L([(bx, by), (bx + bl * r * math.cos(b), by + bl * r * math.sin(b))], w * 0.85))
    return unary_union(parts)


def F(g, fill, stroke=PLUM, sw=LW):      # outlined shape (the default line-art layer)
    return (g, fill, stroke, sw)


def D(g, fill=PLUM):                     # solid detail (lines, dots) with no outline
    return (g, fill, None, 0)


def tf(layers, s=1, rot=0, dx=0, dy=0, ox=500, oy=500):
    out = []
    for g, f, st, sw in layers:
        g = affinity.scale(g, s, s, origin=(ox, oy))
        g = affinity.rotate(g, rot, origin=(ox, oy))
        out.append((affinity.translate(g, dx, dy), f, st, sw))
    return out


OAK_R = [(500, 100), (572, 122), (604, 190), (568, 275), (640, 245), (708, 292), (700, 368), (592, 405),
         (698, 410), (752, 470), (728, 545), (606, 568), (705, 590), (730, 660), (680, 715), (585, 712),
         (628, 765), (598, 815), (520, 800)]


def oak_leaf_shape(cx=500, cy=500, s=1.0, rot=0):
    pts = OAK_R + [(1000 - x, y) for x, y in OAK_R[::-1]][1:-1]
    g = S(pts)
    g = Polygon(g.exterior) if g.geom_type == "Polygon" else g
    g = affinity.scale(g, s, s, origin=(500, 500))
    g = affinity.rotate(g, rot, origin=(500, 500))
    return affinity.translate(g, cx - 500, cy - 500)


def oak_leaf_layers(cx=500, cy=500, s=1.0, rot=0, fill=GOLD):
    leaf = oak_leaf_shape(500, 500, 1, 0)
    stem = L([(500, 780), (500, 930)], 34)
    veins = [L([(500, 190), (500, 800)], 16)]
    for y, dx in ((680, 140), (510, 180), (360, 150), (250, 90)):
        veins += [L([(500, y + 45), (500 - dx, y)], 13), L([(500, y + 45), (500 + dx, y)], 13)]
    lay = [F(stem, PLUM, None, 0), F(leaf, fill), D(U(*veins).intersection(leaf.buffer(-30)))]
    return tf(lay, s, rot, cx - 500, cy - 500)


def acorn_layers(cx=500, cy=500, s=1.0, rot=0):
    nut = S([(330, 450), (338, 610), (410, 755), (500, 850), (590, 755), (662, 610), (670, 450)])
    cap = S([(275, 455), (295, 345), (382, 275), (500, 255), (618, 275), (705, 345), (725, 455), (500, 480)])
    hatch = []
    for k in range(-6, 7):
        hatch.append(L([(500 + k * 70 - 200, 260), (500 + k * 70 + 200, 470)], 11))
        hatch.append(L([(500 + k * 70 + 200, 260), (500 + k * 70 - 200, 470)], 11))
    stem = L([(500, 265), (515, 195), (555, 160)], 36, smooth=True)
    hi = L([(400, 550), (418, 650), (455, 715)], 20, smooth=True)
    lay = [F(nut, GOLD), D(hi, WHITE), D(stem), F(cap, PINE), D(U(*hatch).intersection(cap.buffer(-30)), CREAM)]
    return tf(lay, s, rot, cx - 500, cy - 500)


def steam(xs, y0=330, h=200, w=20):
    return U(*[L([(x, y0), (x + 28, y0 - h * 0.3), (x - 12, y0 - h * 0.62), (x + 18, y0 - h)], w, smooth=True) for x in xs])


# ---------------------------------------------------------------- icons
def soup():
    bowl = E(500, 520, 360, 300).intersection(R(0, 520, 1000, 1000))
    foot = R(390, 790, 610, 850, 14)
    band = bowl.intersection(R(0, 610, 1000, 665))
    surf = E(500, 520, 360, 62)
    soup_ = E(500, 522, 318, 44)
    spoon = U(L([(640, 500), (860, 250)], 46), E(605, 520, 70, 34, -45))
    garnish = U(E(430, 515, 46, 16, -20), E(470, 528, 40, 14, 25))
    return [D(steam((390, 500, 610), 400, 230)), F(foot, PLUM), F(bowl, CREAM), D(band, BERRY), F(surf, CREAM),
            F(soup_, GOLD, PLUM, 14), F(spoon, CREAM), D(garnish, PINE)]


def candle():
    plate = U(E(500, 860, 270, 52))
    body = U(R(370, 420, 630, 860, 18), E(500, 420, 130, 32))
    top = E(500, 420, 130, 32)
    drips = U(L([(420, 430), (420, 540)], 30), L([(585, 430), (585, 490)], 30), C(420, 545, 15))
    wick = L([(500, 420), (500, 350)], 14)
    flame = S([(500, 130), (558, 245), (553, 315), (500, 352), (447, 315), (442, 245)])
    inner = S([(500, 230), (526, 290), (500, 322), (474, 290)])
    rays = U(*[L([(500 + 150 * math.cos(math.radians(a)), 250 + 150 * math.sin(math.radians(a))),
                  (500 + 215 * math.cos(math.radians(a)), 250 + 215 * math.sin(math.radians(a)))], 20) for a in (-150, -30, 180, 0)])
    leaf = oak_leaf_layers(720, 820, 0.28, 60, BERRY)
    return [D(rays, GOLD), F(plate, BERRY), F(body, CREAM), D(drips.difference(top), PLUM),
            F(top, CREAM), D(wick), F(flame, GOLD), D(inner, WHITE)] + leaf


def radiator():
    rails = U(R(170, 330, 830, 380, 20), R(170, 700, 830, 750, 20))
    cols = [R(x, 270, x + 92, 800, 40) for x in range(190, 800, 106)]
    valve = U(R(90, 705, 175, 745, 8))
    knob = C(110, 660, 42)
    feet = U(R(230, 800, 270, 860, 6), R(730, 800, 770, 860, 6))
    heat = U(*[L([(x, 220), (x + 30, 170), (x - 10, 120), (x + 20, 70)], 22, smooth=True) for x in (330, 500, 670)])
    lay = [D(heat, BERRY), F(feet, PLUM), F(rails, CREAM), F(valve, PLUM), F(knob, BERRY)]
    for c in cols:
        lay.append(F(c, CREAM))
    lay.append(D(U(*[L([(x + 46, 330), (x + 46, 740)], 10) for x in range(190, 800, 106)])))
    return lay


def boots():
    def boot(dx, dy, fill):
        shaft = R(250, 230, 470, 720, 30)
        foot = Pg([(250, 600), (600, 610), (690, 680), (700, 770), (250, 770)], r=30)
        b = U(shaft, foot)
        sole = R(240, 745, 715, 800, 18)
        cuff = R(235, 215, 485, 300, 22)
        lay = [F(b, fill), F(sole, PLUM), F(cuff, GOLD), D(L([(300, 380), (300, 640)], 14), CREAM)]
        return tf(lay, 1, 0, dx, dy)
    return (boot(160, -90, PINE) + boot(-40, 0, BERRY) + oak_leaf_layers(820, 840, 0.3, -70, GOLD)
            + oak_leaf_layers(110, 830, 0.24, 50, GOLD))


def frost():
    flake = snowflake(500, 500, 380, 40)
    hexa = Pg([(500 + 70 * math.cos(math.radians(a)), 500 + 70 * math.sin(math.radians(a))) for a in range(-90, 270, 60)])
    return [D(flake, PINE), F(hexa, CREAM, PINE, 20), F(sparkle(820, 190, 90), GOLD), F(sparkle(170, 800, 70), GOLD),
            F(sparkle(840, 790, 50), GOLD)]


def umbrella():
    canopy = C(500, 500, 380).intersection(R(0, 0, 1000, 500))
    bites = U(*[C(x, 520, 75) for x in (215, 405, 595, 785)])
    canopy = canopy.difference(bites)
    ribs = U(*[L([(500, 130), (x, 470)], 12) for x in (310, 500, 690)])
    tip = L([(500, 130), (500, 70)], 22)
    handle = L([(500, 480), (500, 800), (520, 870), (590, 880), (630, 820)], 30, smooth=True)
    rain = U(*[L([(x, y), (x - 30, y + 80)], 18) for x, y in ((140, 600), (250, 760), (840, 600), (760, 760), (130, 160), (880, 170))])
    return [D(rain, PINE), D(tip), D(handle), F(canopy, BERRY), D(ribs.intersection(canopy.buffer(-20)), CREAM)]


def rain_cloud():
    cloud = U(C(330, 420, 150), C(520, 340, 200), C(700, 430, 140), R(200, 420, 820, 560, 70))
    drops = U(*[L([(x, y), (x - 30, y + 90)], 20) for x, y in ((320, 650), (480, 700), (640, 650), (400, 830), (580, 840))])
    return [D(drops, PINE), F(cloud, CREAM)]


def mug():
    handle = E(680, 590, 140, 150).difference(E(680, 590, 72, 82))
    body = R(240, 390, 660, 840, 70)
    band = body.intersection(R(0, 560, 1000, 660))
    rim = E(450, 395, 210, 42)
    tea = E(450, 397, 175, 26)
    leaf = oak_leaf_layers(450, 611, 0.13, 90, GOLD)
    return [D(steam((360, 460, 560), 320, 230)), F(handle, CREAM), F(body, CREAM), D(band, BERRY), F(rim, CREAM), D(tea, PLUM)] + leaf


def sock():
    s = S([(380, 260), (620, 260), (620, 620), (590, 760), (460, 850), (250, 850), (170, 790), (185, 700),
           (300, 660), (380, 600)])
    toe = s.intersection(C(190, 820, 140))
    heel = s.intersection(C(625, 780, 120))
    stripes = U(*[L([(330, y), (680, y)], 26) for y in (420, 500)]).intersection(s)
    cuff = R(345, 150, 655, 300, 26)
    ribs = U(*[L([(x, 180), (x, 270)], 12) for x in range(400, 620, 50)])
    return [F(s, GOLD), D(toe.buffer(-13), BERRY), D(heel.buffer(-13), BERRY), D(stripes, BERRY), F(cuff, CREAM), D(ribs)]


def scarf():
    loop = L([(330, 560), (318, 340), (500, 215), (682, 340), (670, 520)], 120, smooth=True)
    t1 = L([(600, 470), (520, 660), (480, 860)], 130, cap=2, smooth=True)
    t2 = L([(615, 470), (665, 650), (690, 840)], 130, cap=2, smooth=True)
    knot = E(612, 470, 88, 76)
    fringe = []
    for (x0, y0) in ((480, 865), (690, 845)):
        for d in (-45, -15, 15, 45):
            fringe.append(L([(x0 + d, y0), (x0 + d, y0 + 75)], 16))
    stripes = U(*[L([(300, y), (800, y)], 30) for y in (700, 770)])
    lay = []
    for part in (loop, t2, t1):
        lay += [F(part, BERRY), D(part.intersection(stripes).buffer(-13), GOLD)]
    return [D(U(*fringe))] + lay + [F(knot, BERRY)]


def acorns():
    return acorn_layers(370, 520, 0.85, -18) + acorn_layers(640, 600, 0.68, 20) + oak_leaf_layers(720, 260, 0.38, 45, BERRY)


def mushrooms():
    def shroom(dx, dy, s, fill):
        cap = S([(140, 520), (185, 340), (330, 195), (500, 155), (670, 195), (815, 340), (860, 520),
                 (700, 545), (500, 555), (300, 545)])
        spots = U(C(330, 330, 50), C(515, 250, 42), C(680, 330, 56), C(455, 430, 44), C(735, 450, 30), C(240, 450, 30))
        stem = S([(420, 530), (405, 700), (380, 860), (500, 880), (620, 860), (595, 700), (580, 530)])
        gills = U(*[L([(x, 520), (x * 0.6 + 200, 548)], 10) for x in (300, 400, 600, 700)])
        return tf([F(stem, CREAM), F(cap, fill), D(spots.intersection(cap.buffer(-30)), CREAM), D(gills)], s, 0, dx, dy, 500, 880)
    grass = U(L([(80, 880), (920, 880)], 26), L([(160, 880), (130, 800)], 20), L([(860, 880), (895, 800)], 20),
              L([(560, 880), (575, 820)], 18))
    return shroom(260, 0, 0.55, PINE) + shroom(-90, 0, 0.9, BERRY) + [D(grass, PINE)]


def oak_leaf():
    return oak_leaf_layers(500, 500, 1.0, -28, GOLD)


def apple():
    body = U(C(405, 570, 245), C(595, 570, 245), E(500, 700, 250, 170)).difference(E(500, 330, 60, 40))
    body = body.buffer(20).buffer(-20)
    stem = L([(500, 360), (510, 250), (545, 190)], 30, smooth=True)
    leaf = S([(520, 260), (600, 190), (720, 180), (660, 260), (560, 285)])
    vein = L([(540, 262), (680, 205)], 12)
    hi = L([(300, 480), (280, 580), (310, 680)], 26, smooth=True)
    return [D(stem), F(leaf, PINE), D(vein, CREAM), F(body, BERRY), D(hi, CREAM)]


def moon():
    cres = C(450, 520, 340).difference(C(610, 430, 300))
    return [F(cres, GOLD), F(sparkle(760, 760, 60), CREAM), F(star(720, 300, 90, 38, round_=6), GOLD),
            F(star(860, 470, 55, 23, round_=4), GOLD), F(sparkle(700, 130, 45), CREAM)]


def lantern():
    ring = C(500, 120, 52).difference(C(500, 120, 28))
    cap = Pg([(385, 265), (430, 175), (570, 175), (615, 265)], r=8)
    glass = R(375, 255, 625, 760, 14)
    bars = U(L([(500, 265), (500, 750)], 18), L([(375, 330), (625, 330)], 14))
    base = Pg([(330, 750), (670, 750), (630, 845), (370, 845)], r=10)
    cand = R(455, 560, 545, 750, 6)
    flame = S([(500, 400), (532, 465), (523, 515), (500, 532), (477, 515), (468, 465)])
    return [D(ring), F(glass, GOLD), F(cand, CREAM, PLUM, 16), F(flame, WHITE, PLUM, 14), D(bars), F(cap, PLUM), F(base, PLUM)]


def book():
    cover = Pg([(500, 380), (120, 320), (110, 790), (500, 840), (890, 790), (880, 320)], r=10)
    lp = S([(500, 360), (390, 300), (160, 290), (150, 740), (380, 745), (500, 795)])
    lp = Pg([(500, 360), (370, 290), (160, 285), (150, 740), (370, 750), (500, 800)], r=8)
    rp = mir(lp)
    lines = []
    for k in range(6):
        y = 370 + k * 62
        lines.append(L([(200, y), (450, y + 20)], 12))
        lines.append(L([(550, y + 20), (800 if k != 5 else 680, y)], 12))
    ribbon = Pg([(600, 330), (650, 330), (650, 930), (625, 900), (600, 930)])
    cup = []
    return [F(cover, PINE), F(lp, CREAM), F(rp, CREAM), D(U(*lines)), D(L([(500, 365), (500, 800)], 14)), F(ribbon, BERRY, PLUM, 16)]


def clock():
    legs = U(L([(330, 800), (270, 880)], 34), L([(670, 800), (730, 880)], 34))
    bells = U(C(270, 255, 110), C(730, 255, 110)).intersection(U(*[R(0, 0, 1000, 285)]))
    bells = U(affinity.rotate(C(270, 270, 115).intersection(R(0, 0, 1000, 270)), -35, origin=(270, 270)),
              affinity.rotate(C(730, 270, 115).intersection(R(0, 0, 1000, 270)), 35, origin=(730, 270)))
    case = C(500, 550, 310)
    face = C(500, 550, 245)
    ticks = U(*[C(500 + 205 * math.cos(math.radians(a)), 550 + 205 * math.sin(math.radians(a)), 15) for a in range(0, 360, 30)])
    hands = U(L([(500, 550), (500, 390)], 26), L([(500, 550), (620, 600)], 26), C(500, 550, 26))
    handle = L([(380, 210), (500, 165), (620, 210)], 26, smooth=True)
    return [D(legs), D(handle), F(bells, GOLD), F(case, BERRY), F(face, CREAM), D(ticks), D(hands)]


def pie():
    dish = Pg([(140, 600), (860, 600), (790, 800), (210, 800)], r=14)
    crust = E(500, 600, 360, 150).intersection(R(0, 0, 1000, 600))
    lattice = U(*[L([(x, 430), (x + 120, 600)], 22) for x in range(180, 820, 110)],
                *[L([(x + 120, 430), (x, 600)], 22) for x in range(180, 820, 110)])
    filling = crust.difference(lattice).buffer(-14)
    rim = U(*[C(x, 600, 40) for x in range(160, 860, 70)])
    return [D(steam((390, 500, 610), 400, 220)), F(dish, BERRY), F(crust, GOLD), D(filling, BERRY), F(rim, GOLD)]


def sleeping_fox():
    body = E(560, 620, 300, 195)
    tail = L([(820, 600), (850, 740), (720, 830), (480, 850), (270, 800)], 160, smooth=True)
    tip = tail.intersection(C(250, 800, 120))
    head = S([(140, 640), (215, 560), (300, 500), (400, 505), (450, 580), (420, 660), (300, 700), (190, 690)])
    ears = U(Pg([(270, 540), (285, 390), (360, 510)], r=8), Pg([(345, 510), (410, 400), (430, 560)], r=8))
    cheek = head.intersection(Pg([(120, 660), (300, 610), (450, 640), (450, 720), (120, 720)]))
    eye = L([(270, 590), (300, 607), (335, 598)], 16, smooth=True)
    nose = C(148, 642, 24)
    back = L([(640, 470), (760, 520)], 14)
    return [F(body, BERRY), F(tail, BERRY), F(tip, CREAM), F(ears, BERRY), F(head, BERRY), F(cheek, CREAM, PLUM, 16),
            D(eye), D(nose), D(back, CREAM)]


def geese():
    def goose(x, y, s, up):
        body = E(0, 0, 105, 34, -8)
        neck = L([(70, -14), (175, -40)], 30)
        head = E(190, -44, 32, 24, -15)
        beak = Pg([(212, -54), (262, -46), (214, -32)], r=3)
        tail = Pg([(-95, -8), (-150, -28), (-145, 14)], r=6)
        if up:
            wing = Pg([(-45, -12), (45, -16), (20, -80), (-40, -170), (-70, -120)], r=14)
        else:
            wing = Pg([(-45, 10), (45, 10), (10, 70), (-60, 150), (-80, 90)], r=14)
        g = U(body, neck, head, beak, tail, wing)
        return affinity.translate(affinity.scale(g, -s, s, origin=(0, 0)), x, y)
    flock = U(goose(300, 300, 1.15, True), goose(560, 520, 1.0, False), goose(780, 740, 0.85, True))
    return [D(flock), F(sparkle(160, 700, 70), GOLD), F(C(330, 860, 30), GOLD, PLUM, 16), F(sparkle(860, 230, 50), GOLD)]


def oak_sprig():
    branch = L([(120, 880), (360, 640), (560, 480), (860, 200)], 28, smooth=True)
    return ([D(branch)] + oak_leaf_layers(330, 430, 0.5, -60, GOLD) + oak_leaf_layers(700, 520, 0.5, 70, BERRY)
            + oak_leaf_layers(820, 170, 0.36, 40, PINE) + acorn_layers(470, 690, 0.4, 10))


ICONS = [
    # (name, fn, sticker phrase or None)
    ("soup bowl", soup, "first soup"),
    ("candle", candle, "candle season"),
    ("radiator", radiator, "heating on"),
    ("rain boots", boots, "leaf walk"),
    ("frost", frost, "first frost"),
    ("umbrella", umbrella, "rainy commute"),
    ("mug", mug, "warm mug"),
    ("cozy sock", sock, "thick socks"),
    ("scarf", scarf, "first scarf"),
    ("acorns", acorns, "pocket acorns"),
    ("mushrooms", mushrooms, "mushroom hunt"),
    ("oak leaf", oak_leaf, "pressed leaf"),
    ("apple", apple, "apple crunch"),
    ("moon", moon, "moonrise"),
    ("lantern", lantern, "lantern light"),
    ("book", book, "one more page"),
    ("clock", clock, "extra hour"),
    ("pie", pie, "baking day"),
    ("sleeping fox", sleeping_fox, "do nothing day"),
    ("geese", geese, "geese overhead"),
    ("rain cloud", rain_cloud, None),
    ("oak sprig", oak_sprig, None),
]


# ---------------------------------------------------------------- SVG out
def path_d(g):
    if g.is_empty:
        return ""
    polys = g.geoms if hasattr(g, "geoms") else [g]
    out = []
    for p in polys:
        if p.geom_type != "Polygon" or p.area < 1:
            continue
        for ring in [p.exterior] + list(p.interiors):
            cs = list(ring.coords)
            out.append("M" + " L".join(f"{x:.0f},{y:.0f}" for x, y in cs[:-1]) + "Z")
    return " ".join(out)


def fit(layers, size=880):
    allg = unary_union([g.buffer(sw / 2 if st else 0) for g, f, st, sw in layers])
    x0, y0, x1, y1 = allg.bounds
    k = size / max(x1 - x0, y1 - y0)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    return [(affinity.translate(affinity.scale(g, k, k, origin=(cx, cy)), 500 - cx, 500 - cy), f, st, sw) for g, f, st, sw in layers]


def render(layers):
    layers = fit(layers)
    parts = []
    for g, fill, stroke, sw in layers:
        g = g.buffer(0).simplify(0.6)
        d = path_d(g)
        if not d:
            continue
        st = f' stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round" paint-order="stroke"' if stroke else ""
        parts.append(f'<path fill="{fill}" fill-rule="evenodd"{st} d="{d}"/>')
    return "".join(parts)


def main():
    os.makedirs(os.path.join(HERE, "icons"), exist_ok=True)
    data = []
    for i, (name, fn, phrase) in enumerate(ICONS):
        body = render(fn())
        data.append({"id": i, "name": name, "phrase": phrase, "svg": body})
        with open(os.path.join(HERE, "icons", f"{i + 1:02d}-{name.replace(' ', '-')}.svg"), "w") as f:
            f.write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000" width="1000" height="1000">{body}</svg>')
    with open(os.path.join(HERE, "icons.json"), "w") as f:
        json.dump({"icons": data}, f)
    print(len(data), "icons")


if __name__ == "__main__":
    main()
