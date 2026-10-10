"""Woodland Christmas scavenger hunt: the 30 original icons from the approved
Woodland Christmas bingo (bundles/010), reused unchanged, drawn in code (shapely).

Same silhouette approach as the cut-file bundles (005, 009): every icon is
built from solid shapes in a 1000-unit box (y down), with cut-out details.
Each icon is a list of layers (geometry, fill, stroke) painted in order, in the
shop palette only. Light fills (gold, cream, white) get a plum outline so they
read on white paper. Output: icons/NN-name.svg and icons.json (path data).
"""
import math, os, json
from shapely.geometry import LineString, Point, Polygon, MultiPolygon, box
from shapely.ops import unary_union
from shapely import affinity

HERE = os.path.dirname(os.path.abspath(__file__))
PLUM, PINE, BERRY, GOLD, CREAM, WHITE = "#2c1b36", "#2f4a3a", "#8b2f3c", "#e8c97a", "#f1e6cf", "#ffffff"
OUT = 22  # plum outline width for light fills (1000-unit space)


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


def S(pts):            # smooth closed shape through points
    return Polygon(catmull(pts)).buffer(0)


def Pg(pts, r=0):      # straight polygon, optional rounded corners
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


def holly_leaf(x0, y0, ang, Ln, W, spikes=3):
    """Spiky holly leaf from base (x0,y0) pointing at ang degrees."""
    tips = []
    ts = [0.25 + 0.64 * k / spikes for k in range(spikes)]
    for s in (1, -1):
        tips.append([(t * Ln, s * W * 0.5 * (math.sin(math.pi * (0.04 + 0.9 * t)) ** 0.8) * 1.1) for t in ts])
    outline = [(0, 0)] + tips[0] + [(Ln * 1.04, 0)] + tips[1][::-1]
    leaf = Polygon(outline).buffer(0)
    bites = []
    for side in tips:
        seq = side + [(Ln * 1.04, 0)]
        for a, b in zip(seq[:-1], seq[1:]):
            mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
            dx, dy = b[0] - a[0], b[1] - a[1]
            d = math.hypot(dx, dy); nx, ny = -dy / d, dx / d
            if nx * (mx - Ln / 2) + ny * my < 0:
                nx, ny = -nx, -ny
            off = 0.30 * d
            bites.append(Point(mx + nx * off, my + ny * off).buffer(math.hypot(d / 2, off), 48))
    leaf = leaf.difference(unary_union(bites)).union(L([(-0.1 * Ln, 0), (0.15 * Ln, 0)], max(14, W * 0.1)))
    leaf = affinity.rotate(leaf, ang, origin=(0, 0))
    return affinity.translate(leaf, x0, y0)


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


def F(g, fill, stroke=None, sw=OUT):
    return (g, fill, stroke, sw)


def lit(g, fill=GOLD):  # light fill with plum outline
    return F(g, fill, PLUM, OUT)


# ---------------------------------------------------------------- icons
def fox():
    half = Pg([(500, 330), (590, 318), (715, 140), (745, 150), (770, 330), (815, 430), (890, 560),
               (770, 610), (650, 700), (548, 828), (500, 850)], r=14)
    head = sym(half)
    ear = sym(Pg([(612, 318), (718, 190), (742, 345)], r=6))
    mask = sym(Pg([(500, 640), (590, 590), (700, 560), (890, 560), (770, 610), (650, 700), (548, 828), (500, 850)])).intersection(head)
    eyes = sym(E(398, 480, 40, 25, -18))
    nose = E(500, 815, 50, 34)
    return [F(head, BERRY, PLUM, OUT), F(ear, PLUM), F(mask, CREAM), F(eyes, PLUM), F(nose, PLUM)]


def owl():
    body = sym(S([(500, 215), (585, 222), (655, 160), (690, 175), (705, 300), (750, 440), (752, 600),
                  (700, 745), (600, 822), (500, 840)][::1] + [(400, 822), (300, 745), (248, 600), (250, 440),
                  (295, 300), (310, 175), (345, 160), (415, 222)]))
    disc = sym(C(405, 385, 108))
    eye = sym(C(405, 385, 72))
    pupil = sym(C(412, 392, 38))
    hi = sym(C(395, 372, 13))
    beak = Pg([(462, 462), (538, 462), (500, 548)], r=8)
    wings = sym(L([(300, 470), (282, 600), (330, 730), (420, 800)], 18, smooth=True))
    chev = []
    for y, xs in ((600, (440, 560)), (680, (400, 500, 600)), (755, (450, 550))):
        for x in xs:
            chev.append(L([(x - 38, y - 18), (x, y + 14), (x + 38, y - 18)], 16))
    branch = L([(150, 870), (850, 870)], 46)
    feet = U(*[C(x, 842, 22) for x in (430, 465, 535, 570)])
    return [F(branch, PLUM), F(body, PLUM), F(wings, WHITE), F(U(*chev), CREAM), F(disc, CREAM),
            lit(eye), F(pupil, PLUM), F(hi, WHITE), lit(beak), lit(feet)]


def stag():
    head = sym(S([(500, 420), (575, 430), (622, 480), (612, 580), (580, 700), (552, 815), (522, 862),
                  (500, 868), (478, 862), (448, 815), (420, 700), (388, 580), (378, 480), (425, 430)]))
    ears = sym(E(690, 500, 105, 42, -22))
    inner = sym(E(700, 497, 66, 20, -22))
    ant = []
    main = [(565, 445), (630, 340), (690, 240), (712, 110)]
    ant.append(L(main, 38, smooth=True))
    ant.append(L([(625, 352), (735, 330), (835, 255)], 32, smooth=True))
    ant.append(L([(678, 262), (790, 205), (860, 120)], 28, smooth=True))
    ant.append(L([(598, 400), (548, 320)], 30))
    antlers = sym(U(*ant))
    eyes = sym(E(560, 590, 26, 20, 15))
    muzzle = E(500, 815, 70, 56)
    nose = E(500, 800, 38, 26)
    return [F(antlers, PLUM), F(ears, PLUM), F(inner, CREAM), F(head, PLUM), F(eyes, WHITE), lit(muzzle, CREAM), F(nose, PLUM)]


def robin():
    body = E(530, 560, 255, 215, -12)
    head = C(335, 395, 145)
    tail = Pg([(720, 520), (905, 360), (950, 420), (780, 640)], r=20)
    bird = U(body, head, tail)
    breast = E(360, 580, 175, 185, 0).intersection(U(body, head)).difference(C(335, 360, 120))
    beak = Pg([(205, 368), (105, 402), (205, 430)], r=6)
    wing = L([(500, 470), (640, 470), (760, 560)], 20, smooth=True)
    eye = C(305, 370, 26)
    pupil = C(300, 372, 14)
    legs = U(L([(470, 760), (455, 880)], 22), L([(570, 755), (580, 880)], 22),
             L([(410, 885), (500, 885)], 20), L([(540, 885), (630, 885)], 20))
    return [F(legs, PLUM), F(bird, PLUM), F(breast, BERRY), F(wing, WHITE), lit(beak), F(eye, WHITE), F(pupil, PLUM)]


def pine():
    tiers = []
    for top, base, hw in ((95, 370, 180), (240, 580, 265), (420, 790, 345)):
        tiers.append(Pg([(500, top), (500 + hw, base), (500 + hw * 0.55, base - 32), (500, base + 4),
                         (500 - hw * 0.55, base - 32), (500 - hw, base)], r=10))
    tree = U(*tiers)
    trunk = R(450, 760, 550, 905, 6)
    garland = []
    for y0, hw in ((300, 120), (500, 190)):
        garland.append(L([(500 - hw, y0 - 30), (500, y0 + 20), (500 + hw, y0 + 70)], 16, smooth=True))
    return [F(trunk, PLUM), F(tree, PINE), F(U(*garland).intersection(tree.buffer(-30)), WHITE)]


def mushroom():
    cap = S([(140, 520), (185, 340), (330, 195), (500, 155), (670, 195), (815, 340), (860, 520),
             (700, 545), (500, 555), (300, 545)])
    spots = U(C(330, 330, 52), C(515, 250, 44), C(680, 330, 58), C(455, 430, 46), C(770, 460, 34), C(220, 455, 32), C(610, 465, 30))
    stem = S([(420, 530), (405, 700), (370, 860), (500, 885), (630, 860), (595, 700), (580, 530)])
    grass = U(L([(250, 890), (750, 890)], 30), L([(300, 890), (270, 800)], 22), L([(700, 890), (735, 805)], 22))
    return [F(grass, PINE), lit(stem, CREAM), F(cap.difference(spots), BERRY)]


def lantern():
    ring = C(500, 130, 52).difference(C(500, 130, 28))
    cap = Pg([(400, 265), (440, 180), (560, 180), (600, 265)], r=8)
    frame = R(355, 255, 645, 770, 18)
    glass = R(395, 295, 605, 730, 6)
    bar = R(486, 295, 514, 730)
    base = Pg([(330, 760), (670, 760), (630, 850), (370, 850)], r=10)
    candle = R(455, 560, 545, 730, 6)
    flame = S([(500, 410), (530, 470), (522, 520), (500, 535), (478, 520), (470, 470)])
    return [F(ring, PLUM), F(frame, PLUM), F(glass, GOLD), F(candle, BERRY), F(flame, WHITE),
            F(cap, PLUM), F(base, PLUM)]


def mitten():
    hand = S([(360, 640), (345, 420), (360, 250), (440, 175), (560, 170), (650, 230), (690, 380), (690, 640)])
    thumb = E(300, 440, 82, 150, 28)
    m = U(hand, thumb, R(345, 520, 690, 650))
    cuff = R(320, 630, 715, 820, 30)
    rib = U(*[L([(x, 660), (x, 790)], 14) for x in range(385, 680, 55)])
    flake = snowflake(530, 400, 110, 22)
    g = [F(m.difference(flake), BERRY), lit(cuff, CREAM), F(rib, PLUM)]
    return [(affinity.rotate(a, -12, origin=(500, 500)), b, c, d) for a, b, c, d in g]


def star_icon():
    s = star(500, 520, 395, 170, round_=18)
    shine = L([(395, 380), (440, 330)], 26)
    return [lit(s), F(shine, WHITE)]


def sled():
    runner = L([(880, 760), (220, 760), (120, 740), (70, 660), (90, 560), (160, 520), (220, 560), (200, 620)], 40, smooth=True)
    struts = U(*[L([(x, 760), (x, 600)], 36) for x in (300, 540, 780)])
    deck = U(*[R(200 + i * 0, 470 + i * 0, 880, 600, 24) for i in (0,)])
    slats = U(*[L([(x, 485), (x, 585)], 18) for x in (430, 660)])
    rope = L([(210, 520), (150, 400), (200, 300), (300, 290)], 18, smooth=True)
    return [F(rope, PLUM), F(runner, PLUM), F(struts, PLUM), F(deck.difference(slats), BERRY)]


def cabin():
    walls = R(225, 470, 775, 860)
    logs = U(*[L([(225, y), (775, y)], 12) for y in (540, 610, 680, 750, 820)])
    chim = R(630, 210, 710, 400)
    roof = Pg([(140, 500), (500, 205), (860, 500), (800, 520), (500, 290), (200, 520)], r=8)
    roof = U(roof, Pg([(500, 205), (860, 500), (140, 500)]))
    window = R(290, 575, 430, 705, 8)
    cross = U(L([(360, 575), (360, 705)], 16), L([(290, 640), (430, 640)], 16))
    door = U(R(545, 650, 685, 860), C(615, 650, 70).intersection(R(545, 570, 685, 650)))
    knob = C(655, 760, 14)
    smoke = L([(670, 180), (700, 130), (660, 90), (690, 40)], 20, smooth=True)
    return [F(smoke, PLUM), F(chim, PLUM), F(walls.difference(logs), PLUM), F(roof, BERRY), lit(window), F(cross, PLUM),
            F(door, PINE), F(knob, GOLD)]


def snowflake_icon():
    return [F(snowflake(500, 500, 400, 46), PLUM)]


def acorn():
    nut = S([(320, 440), (330, 610), (410, 760), (500, 860), (590, 760), (670, 610), (680, 440)])
    cap = S([(270, 450), (290, 340), (380, 270), (500, 250), (620, 270), (710, 340), (730, 450), (500, 480)])
    hatch = []
    for k in range(-6, 7):
        hatch.append(L([(500 + k * 60 - 200, 260), (500 + k * 60 + 200, 470)], 12))
        hatch.append(L([(500 + k * 60 + 200, 260), (500 + k * 60 - 200, 470)], 12))
    stem = L([(500, 260), (520, 190), (560, 150)], 40, smooth=True)
    hi = L([(390, 540), (410, 650), (450, 720)], 22, smooth=True)
    return [lit(nut), F(hi, WHITE), F(stem, PLUM), F(cap.difference(U(*hatch).intersection(cap.buffer(-26))), PLUM)]


def holly():
    leaves = U(holly_leaf(500, 560, -148, 420, 220), holly_leaf(500, 560, -32, 420, 220), holly_leaf(500, 560, 92, 300, 170))
    veins = U(L([(500, 560), (500 - 330 * math.cos(math.radians(32)), 560 - 330 * math.sin(math.radians(32)))], 14),
              L([(500, 560), (500 + 330 * math.cos(math.radians(32)), 560 - 330 * math.sin(math.radians(32)))], 14),
              L([(500, 560), (500 + 220 * math.cos(math.radians(92)), 560 + 220 * math.sin(math.radians(92)))], 14))
    berries = U(C(440, 555, 68), C(560, 555, 68), C(500, 470, 68))
    shine = U(C(420, 535, 15), C(540, 535, 15), C(480, 450, 15))
    return [F(leaves.difference(veins), PINE), F(berries.buffer(10), WHITE), F(berries, BERRY), F(shine, WHITE)]


def pinecone():
    cone = S([(500, 230), (610, 260), (690, 380), (700, 540), (650, 700), (560, 830), (500, 870),
              (440, 830), (350, 700), (300, 540), (310, 380), (390, 260)])
    lines = []
    for k in range(-7, 8):
        x0 = 500 + k * 85
        lines.append(L([(x0 - 260, 230), (x0, 560), (x0 + 120, 880)], 14, smooth=False))
    for k in range(-7, 8):
        x0 = 500 + k * 85
        lines.append(L([(x0 + 260, 230), (x0, 560), (x0 - 120, 880)], 14, smooth=False))
    scales = cone.difference(U(*lines).intersection(cone.buffer(-14)))
    stem = L([(500, 240), (505, 150)], 40)
    needles = U(*[L([(505, 160), (505 + 180 * math.cos(math.radians(a)), 160 + 180 * math.sin(math.radians(a)))], 16)
                  for a in (-160, -140, -120, -60, -40, -20)])
    return [F(needles, PINE), F(stem, PLUM), F(scales, PLUM)]


def hedgehog():
    cx, cy = 560, 600
    pts = []
    for i in range(0, 25):
        a = math.radians(195 + i * (165 / 24))
        rr = 340 if i % 2 == 0 else 270
        pts.append((cx + rr * math.cos(a) * 1.05, cy + rr * math.sin(a) * 0.85))
    pts += [(cx + 300, cy + 120), (cx + 200, cy + 230), (cx - 100, cy + 240), (cx - 250, cy + 150)]
    spines = Pg(pts, r=6)
    face = S([(130, 690), (220, 600), (330, 500), (420, 520), (450, 650), (420, 800), (320, 830), (200, 760)])
    feet = U(E(330, 840, 50, 28), E(690, 840, 50, 28))
    lines = U(*[L([(cx + 210 * math.cos(math.radians(a)), cy + 170 * math.sin(math.radians(a))),
                   (cx + 270 * math.cos(math.radians(a + 6)), cy + 215 * math.sin(math.radians(a + 6)))], 14)
                for a in range(215, 350, 22)])
    nose = C(140, 690, 30)
    eye = C(300, 620, 22)
    return [F(feet, PLUM), F(spines.difference(lines), PLUM), lit(face, GOLD), F(nose, PLUM), F(eye, PLUM)]


def rabbit():
    body = E(560, 640, 230, 215, 0)
    head = E(360, 440, 145, 120, -15)
    ear1 = E(420, 230, 55, 170, 18)
    ear2 = E(495, 245, 52, 165, 34)
    foot = E(520, 845, 190, 42)
    paw = E(360, 830, 70, 35)
    bunny = U(body, head, ear1, ear2, foot, paw, R(330, 520, 520, 700, 40))
    inner = E(425, 245, 26, 120, 18)
    tail = C(795, 690, 72)
    eye = C(330, 420, 22)
    nose = E(225, 450, 22, 18)
    return [F(bunny.difference(inner), PLUM), lit(tail, WHITE), F(eye, WHITE), F(nose, BERRY)]


def wreath():
    cx, cy, rr = 500, 470, 285
    leaves = []
    for i in range(22):
        a = 360 * i / 22
        for off, rad in ((-1, rr - 55), (1, rr + 55)):
            x = cx + rad * math.cos(math.radians(a + off * 6)); y = cy + rad * math.sin(math.radians(a + off * 6))
            leaves.append(E(x, y, 85, 36, a + 90 + off * 35))
    ring = U(*leaves, C(cx, cy, rr + 40).difference(C(cx, cy, rr - 40)))
    berries = U(*[C(cx + rr * math.cos(math.radians(a)), cy + rr * math.sin(math.radians(a)), 34) for a in (200, 250, 300, 340, 20, 160)])
    bow = U(E(410, 760, 105, 62, 20), E(590, 760, 105, 62, -20),
            Pg([(480, 770), (420, 900), (470, 890), (500, 800)], r=8), Pg([(520, 770), (580, 900), (530, 890), (500, 800)], r=8))
    loops = U(E(420, 760, 50, 22, 20), E(580, 760, 50, 22, -20))
    knot = E(500, 765, 48, 44)
    return [F(ring, PINE), F(berries.buffer(9), WHITE), F(berries, BERRY), F(bow.buffer(12), WHITE),
            F(bow.difference(loops), BERRY), F(knot, BERRY, WHITE, 14)]


def candle():
    dish = U(E(500, 830, 280, 55), R(420, 780, 580, 830))
    handle = C(800, 790, 60).difference(C(800, 790, 30))
    body = U(R(390, 400, 610, 800, 10), E(500, 400, 110, 26))
    drip = U(L([(440, 400), (440, 520)], 26), L([(560, 400), (560, 470)], 26))
    top = E(500, 400, 110, 26)
    wick = L([(500, 400), (500, 345)], 14)
    flame = S([(500, 140), (555, 250), (550, 315), (500, 345), (450, 315), (445, 250)])
    inner = S([(500, 230), (525, 290), (500, 318), (475, 290)])
    return [F(handle, PLUM), F(dish, PLUM), F(body, BERRY), lit(top, CREAM), F(drip.difference(top), CREAM),
            F(wick, PLUM), lit(flame), F(inner, WHITE)]


def cocoa():
    mug = R(220, 420, 690, 870, 60)
    handle = E(700, 620, 135, 140).difference(E(700, 620, 75, 80))
    rim = E(455, 425, 235, 50)
    cocoa_ = E(455, 425, 200, 34)
    mallows = U(R(360, 365, 430, 425, 12), R(450, 370, 520, 430, 12), R(530, 360, 590, 415, 12))
    steam = U(*[L([(x, 330), (x + 30, 270), (x - 10, 210), (x + 20, 140)], 22, smooth=True) for x in (360, 460, 560)])
    hx, hy = 455, 650
    heart = U(C(hx - 45, hy - 20, 52), C(hx + 45, hy - 20, 52), Pg([(hx - 94, hy - 5), (hx + 94, hy - 5), (hx, hy + 100)]))
    return [F(steam, PLUM), F(handle, BERRY), F(mug.difference(heart), BERRY), lit(rim, CREAM), F(cocoa_, PLUM),
            lit(mallows, WHITE)]


def scarf():
    loop = L([(330, 560), (318, 340), (500, 215), (682, 340), (670, 520)], 120, smooth=True)
    t1 = L([(600, 470), (500, 650), (430, 860)], 130, cap=2, smooth=True)
    t2 = L([(610, 470), (660, 650), (690, 840)], 130, cap=2, smooth=True)
    knot = E(610, 470, 85, 75)
    fringe = []
    for (x0, y0, ang) in ((430, 860, 108), (690, 840, 84)):
        for d in (-45, -15, 15, 45):
            px = x0 + d * math.cos(math.radians(ang - 90)); py = y0 + d * math.sin(math.radians(ang - 90))
            fringe.append(L([(px, py), (px + 70 * math.cos(math.radians(ang)), py + 70 * math.sin(math.radians(ang)))], 16))
    stripes = U(*[L([(300, y), (800, y + 40)], 34) for y in (690, 770)])
    lay = []
    for part in (loop, t2, t1):
        lay += [F(part, PINE, WHITE, 16), F(part.intersection(stripes), BERRY)]
    return [F(U(*fringe), PINE)] + lay + [F(knot, PINE, WHITE, 16)]


def gift():
    boxg = R(240, 470, 760, 860, 10)
    lid = R(205, 380, 795, 480, 10)
    rib = U(R(455, 380, 545, 860))
    band = R(205, 405, 795, 450)
    bow = U(E(395, 305, 115, 70, 22), E(605, 305, 115, 70, -22))
    loops = U(E(400, 305, 55, 26, 22), E(600, 305, 55, 26, -22))
    knot = C(500, 330, 50)
    return [F(boxg, BERRY), F(lid, BERRY, WHITE, 16), F(rib, PINE), F(band.difference(rib), WHITE),
            F(bow.difference(loops), PINE), F(knot, PINE, WHITE, 14)]


def moon():
    cres = C(470, 520, 335).difference(C(625, 440, 300))
    s1 = star(720, 640, 95, 40, round_=6)
    s2 = star(640, 820, 55, 23, round_=4)
    return [lit(cres), lit(s1), lit(s2)]


def birdhouse():
    post = R(465, 700, 535, 900)
    body = Pg([(290, 430), (500, 270), (710, 430), (710, 740), (290, 740)])
    roof = L([(225, 485), (500, 250), (775, 485)], 80, cap=2)
    hole = C(500, 500, 70)
    perch = L([(500, 600), (500, 660)], 22)
    hang = C(500, 190, 45).difference(C(500, 190, 22))
    heart = U(C(470, 690, 17), C(530, 690, 17))
    return [F(post, PLUM), F(hang, PLUM), F(body.difference(hole), BERRY), F(perch, PLUM), F(roof, PLUM), F(hole, PLUM)]


def squirrel():
    tail = S([(600, 830), (770, 780), (880, 620), (895, 420), (830, 240), (700, 160), (600, 210), (590, 300),
              (680, 330), (730, 430), (720, 590), (640, 700), (560, 760)])
    body = E(490, 650, 155, 205, 12)
    head = E(380, 400, 120, 102, -10)
    ear = Pg([(395, 320), (430, 220), (470, 330)], r=10)
    snout = E(285, 425, 45, 40)
    foot = E(510, 850, 125, 40)
    sq = U(body, head, ear, snout, foot)
    ac_nut = E(330, 590, 42, 52)
    ac_cap = E(330, 545, 50, 24)
    eye = C(360, 385, 20)
    nose = C(245, 420, 16)
    arm = L([(430, 520), (360, 580)], 46)
    return [F(tail, BERRY), F(sq, BERRY, WHITE, 16), lit(ac_nut), F(ac_cap, PLUM), F(arm, BERRY), F(eye, WHITE), F(nose, PLUM)]


def bear():
    head = C(500, 540, 295)
    ears = sym(C(275, 300, 100))
    inner = sym(C(282, 308, 50))
    muzzle = E(500, 665, 150, 115)
    nose = E(500, 615, 60, 40)
    mouth = U(L([(500, 640), (500, 700), (450, 730)], 14), L([(500, 700), (550, 730)], 14))
    eyes = sym(C(400, 480, 30))
    pup = sym(C(404, 484, 17))
    hat = Pg([(300, 330), (500, 120), (700, 330)], r=10)
    pom = C(500, 125, 50)
    brim = R(270, 300, 730, 370, 30)
    return [F(ears, PLUM), F(inner, CREAM), F(head, PLUM), lit(muzzle, CREAM), F(nose, PLUM), F(mouth, PLUM),
            F(eyes, WHITE), F(pup, PLUM), F(hat, BERRY), lit(brim, CREAM), lit(pom, WHITE)]


def stocking():
    sock = S([(375, 300), (610, 300), (610, 640), (575, 780), (450, 860), (260, 860), (180, 800), (195, 710),
              (300, 670), (375, 610)])
    toe = sock.intersection(C(205, 820, 130))
    heel = sock.intersection(C(615, 790, 110))
    stripes = U(*[L([(330, y), (650, y)], 30) for y in (420, 500)]).intersection(sock)
    cuff = R(335, 170, 655, 330, 26)
    loop = C(655, 190, 55).difference(C(655, 190, 30))
    return [F(loop, PLUM), F(sock, BERRY), F(toe, PINE), F(heel, PINE), F(stripes, WHITE), lit(cuff, CREAM)]


def bell():
    b = sym(S([(500, 250), (590, 268), (640, 350), (658, 520), (690, 640), (760, 730), (500, 760)][::1] +
              [(240, 730), (310, 640), (342, 520), (360, 350), (410, 268)]))
    lip = R(230, 700, 770, 770, 30)
    clap = C(500, 820, 52)
    bow = U(E(410, 210, 95, 52, 25), E(590, 210, 95, 52, -25))
    knot = C(500, 225, 40)
    holly_ = U(holly_leaf(500, 230, -160, 190, 90), holly_leaf(500, 230, -20, 190, 90))
    shine = L([(410, 380), (395, 520), (370, 620)], 26, smooth=True)
    return [F(clap, PLUM), lit(b), F(shine, WHITE), lit(lip), F(holly_, PINE), F(bow, BERRY), F(knot, BERRY, WHITE, 12)]


def snowman():
    bot = C(500, 715, 185)
    mid = C(500, 455, 135)
    head = C(500, 260, 100)
    arms = U(L([(380, 450), (200, 360), (150, 300)], 22), L([(200, 360), (170, 400)], 18),
             L([(620, 450), (800, 360), (850, 300)], 22), L([(800, 360), (830, 400)], 18))
    hat = U(R(385, 160, 615, 190, 8), R(430, 50, 570, 175, 8))
    band = R(430, 135, 570, 162)
    scarf = U(R(395, 330, 605, 380, 20), Pg([(540, 360), (600, 360), (630, 500), (570, 505)], r=8))
    nose = Pg([(505, 255), (505, 290), (625, 285)], r=4)
    dots = U(sym(C(465, 240, 16)), C(500, 440, 16), C(500, 510, 16), C(500, 640, 18), C(500, 720, 18))
    thick = lambda g: F(g, WHITE, PLUM, 40)
    return [F(arms, PLUM), thick(bot), thick(mid), thick(head), F(dots, PLUM), lit(nose),
            F(scarf, BERRY), F(hat, PLUM), F(band, BERRY)]


def skate():
    boot = S([(300, 150), (560, 150), (565, 420), (700, 500), (800, 580), (805, 690), (300, 700), (270, 500)])
    cuff = R(285, 140, 580, 230, 22)
    laces = U(*[L([(560, y), (500, y + 50)], 16) for y in (270, 340, 410)], *[L([(500, y), (560, y + 50)], 16) for y in (270, 340, 410)])
    blade = L([(250, 790), (820, 790), (870, 760), (880, 715)], 34, smooth=True)
    posts = U(R(330, 690, 380, 800), R(690, 690, 740, 800))
    sole = R(280, 680, 815, 720, 14)
    return [F(blade, PLUM), F(posts, PLUM), F(boot.difference(laces), BERRY), F(sole, PLUM), lit(cuff, CREAM)]


ICONS = [
    ("fox", fox), ("owl", owl), ("stag", stag), ("robin", robin), ("pine tree", pine), ("mushroom", mushroom),
    ("lantern", lantern), ("mitten", mitten), ("star", star_icon), ("sled", sled), ("cabin", cabin),
    ("snowflake", snowflake_icon), ("acorn", acorn), ("holly", holly), ("pinecone", pinecone),
    ("hedgehog", hedgehog), ("rabbit", rabbit), ("wreath", wreath), ("candle", candle), ("cocoa", cocoa),
    ("scarf", scarf), ("gift", gift), ("moon", moon), ("bird house", birdhouse), ("squirrel", squirrel),
    ("bear", bear), ("stocking", stocking), ("bell", bell), ("snowman", snowman), ("ice skate", skate),
]


def free_space():
    """Three little stars in an arc: deliberately unlike the moon and star icons."""
    return [lit(star(500, 330, 230, 100, round_=12)), lit(star(170, 560, 140, 60, round_=8)),
            lit(star(830, 560, 140, 60, round_=8))]


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


def fit(layers, size=860):
    """Scale and centre so every icon fills the same box (consistent size on the card)."""
    allg = unary_union([g.buffer(sw / 2 if st else 0) for g, f, st, sw in layers])
    x0, y0, x1, y1 = allg.bounds
    k = size / max(x1 - x0, y1 - y0)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    out = []
    for g, f, st, sw in layers:
        g = affinity.translate(affinity.scale(g, k, k, origin=(cx, cy)), 500 - cx, 500 - cy)
        out.append((g, f, st, sw))
    return out


def layers_svg(layers):
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
    for i, (name, fn) in enumerate(ICONS):
        body = layers_svg(fn())
        data.append({"id": i, "name": name, "svg": body})
        with open(os.path.join(HERE, "icons", f"{i + 1:02d}-{name.replace(' ', '-')}.svg"), "w") as f:
            f.write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000" width="1000" height="1000">{body}</svg>')
    free = layers_svg(free_space())
    with open(os.path.join(HERE, "icons.json"), "w") as f:
        json.dump({"icons": data, "free": free}, f)
    print(len(data), "icons")


if __name__ == "__main__":
    main()
