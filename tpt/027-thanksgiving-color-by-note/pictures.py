"""Thanksgiving / autumn line-art pictures for the colour-by-note set, drawn in code.

Each picture is a list of layers in painter's order (bottom first). A layer is
a shapely geometry with a colour name; optional `cuts` split its visible part
into more regions. `ink` shapes are pre-printed black details (not regions).
Coordinates are PostScript points, y pointing down, on a W x H canvas.
"""
import math
from shapely.geometry import Point, Polygon, LineString, box
from shapely import affinity
from shapely.ops import unary_union

W, H = 540, 500


# ---------- geometry helpers ----------
def circle(cx, cy, r):
    return Point(cx, cy).buffer(r, quad_segs=32)


def ellipse(cx, cy, rx, ry, rot=0):
    e = affinity.scale(Point(0, 0).buffer(1, quad_segs=48), rx, ry)
    if rot:
        e = affinity.rotate(e, rot, origin=(0, 0))
    return affinity.translate(e, cx, cy)


def rrect(x0, y0, x1, y1, r):
    return box(x0 + r, y0 + r, x1 - r, y1 - r).buffer(r, quad_segs=12)


def catmull(pts, closed=False, n=14):
    pts = list(pts)
    if closed:
        ext = [pts[-1]] + pts + [pts[0], pts[1]]
    else:
        ext = [pts[0]] + pts + [pts[-1]]
    out = []
    for i in range(1, len(ext) - 2):
        p0, p1, p2, p3 = ext[i - 1], ext[i], ext[i + 1], ext[i + 2]
        for k in range(n):
            t = k / n
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t
                                    + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2
                                    + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3)
                             for j in range(2)))
    if not closed:
        out.append(pts[-1])
    return out


def blob(pts):
    return Polygon(catmull(pts, closed=True)).buffer(0)


def curve(pts):
    return LineString(catmull(pts))


def thick(pts, w, smooth=True):
    line = LineString(catmull(pts)) if smooth else LineString(pts)
    return line.buffer(w / 2, quad_segs=8)


def star(cx, cy, R, r, n=5, rot=-90, round_=4):
    pts = []
    for i in range(2 * n):
        a = math.radians(rot + i * 180 / n)
        rad = R if i % 2 == 0 else r
        pts.append((cx + rad * math.cos(a), cy + rad * math.sin(a)))
    return Polygon(pts).buffer(round_).buffer(-round_)


def cloud(cx, cy, s=1.0):
    parts = [circle(cx - 45 * s, cy + 8 * s, 32 * s), circle(cx, cy - 12 * s, 42 * s),
             circle(cx + 48 * s, cy + 6 * s, 34 * s), rrect(cx - 78 * s, cy + 2 * s, cx + 82 * s, cy + 40 * s, 18 * s)]
    return unary_union(parts)


def mirror(g, cx=W / 2):
    return affinity.scale(g, -1, 1, origin=(cx, 0))


def sector(cx, cy, r0, r1, a0, a1, n=24):
    pts = []
    for i in range(n + 1):
        a = math.radians(a0 + (a1 - a0) * i / n)
        pts.append((cx + r1 * math.cos(a), cy + r1 * math.sin(a)))
    for i in range(n, -1, -1):
        a = math.radians(a0 + (a1 - a0) * i / n)
        pts.append((cx + r0 * math.cos(a), cy + r0 * math.sin(a)))
    return Polygon(pts)


FRAME = box(0, 0, W, H)


def L(geom, color, cuts=None):
    return {"geom": geom, "color": color, "cuts": cuts or []}


# ---------- pictures ----------
def ground(y, color="green", wob=12):
    return L(blob([(-20, y), (140, y - wob), (300, y + wob * .6), (450, y - wob), (560, y), (560, 520), (-20, 520)]), color)


def turkey():
    layers = [L(FRAME, "blue", cuts=[curve([(-10, 130), (140, 110), (300, 140), (550, 105)])]),
              ground(430, "brown")]
    cols = ["red", "orange", "yellow", "orange", "red"]
    for a, c in zip((-72, -36, 0, 36, 72), cols):
        r = math.radians(a)
        cx, cy = 270 + 150 * math.sin(r), 275 - 150 * math.cos(r)
        layers.append(L(ellipse(cx, cy, 46, 100, rot=a), c))
    layers += [
        L(ellipse(270, 372, 108, 100), "brown", cuts=[curve([(150, 385), (270, 360), (390, 385)])]),
        L(circle(270, 240, 76), "brown"),
    ]
    ink = [circle(240, 224, 7), circle(300, 224, 7),
           Polygon([(252, 262), (288, 262), (270, 296)]).buffer(2),
           blob([(286, 296), (306, 298), (308, 326), (292, 332), (284, 314)]),
           thick([(240, 466), (240, 486)], 5, smooth=False), thick([(300, 466), (300, 486)], 5, smooth=False)]
    return layers, ink


def pumpkin():
    layers = [L(FRAME, "blue", cuts=[curve([(-10, 140), (140, 120), (300, 150), (550, 115)])]),
              L(circle(95, 85, 46), "yellow"),
              ground(430, "green"),
              L(ellipse(175, 320, 105, 125), "orange"), L(ellipse(365, 320, 105, 125), "orange"),
              L(ellipse(270, 320, 105, 135), "orange"),
              L(rrect(240, 118, 302, 205, 12), "brown"),
              L(ellipse(358, 160, 66, 34, rot=-22), "green")]
    ink = [thick([(270, 200), (270, 450)], 3), thick([(185, 210), (125, 330), (180, 440)], 3), thick([(355, 210), (415, 330), (360, 440)], 3),
           ]
    return layers, ink


def cornucopia():
    path = [(190, 245, 98), (265, 295, 86), (340, 340, 66), (410, 372, 46), (465, 378, 30), (505, 350, 16)]
    pts = []
    for (x0, y0, r0), (x1, y1, r1) in zip(path, path[1:]):
        for k in range(9):
            t = k / 9
            pts.append(circle(x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, r0 + (r1 - r0) * t))
    horn = unary_union(pts)
    layers = [
        L(FRAME, "yellow"),
        L(horn, "brown", cuts=[LineString([(255, 140), (270, 280), (300, 460)]), LineString([(345, 200), (362, 330), (380, 460)])]),
        L(circle(88, 232, 60), "red"),
        L(circle(100, 110, 52), "red"),
        L(ellipse(205, 150, 72, 60), "orange"),
        L(ellipse(290, 112, 50, 32, rot=15), "green"),
        L(ellipse(190, 46, 44, 26, rot=-8), "green"),
        L(ellipse(60, 360, 52, 30, rot=25), "green"),
    ]
    ink = [thick([(205, 92), (210, 74)], 4, smooth=False), thick([(100, 60), (106, 42)], 4, smooth=False)]
    return layers, ink


def maple():
    cx, cy = 270, 255
    spec = [(-90, 185), (-45, 160), (-10, 112), (30, 135), (65, 108), (115, 108), (150, 135), (190, 112), (225, 160)]
    pts = []
    for a, r in spec:
        pts.append((cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a))))
        n = a + 17
        pts.append((cx + 78 * math.cos(math.radians(n)), cy + 78 * math.sin(math.radians(n))))
    big = affinity.scale(Polygon(pts).buffer(8).buffer(-16).buffer(8), 1.25, 1.25, origin=(cx, cy))
    layers = [
        L(FRAME, "yellow"),
        L(ellipse(105, 425, 100, 44, rot=-22), "green"),
        L(ellipse(440, 430, 100, 44, rot=18), "orange"),
        L(big, "red"),
    ]
    ink = [thick([(270, 255), (270, 475)], 9, smooth=False),
           thick([(270, 255), (270, 50)], 4, smooth=False),
           thick([(270, 255), (180, 165)], 4, smooth=False), thick([(270, 255), (360, 165)], 4, smooth=False),
           thick([(270, 255), (185, 315)], 4, smooth=False), thick([(270, 255), (355, 315)], 4, smooth=False),
           thick([(55, 445), (140, 418)], 4, smooth=False), thick([(400, 440), (480, 420)], 4, smooth=False)]
    return layers, ink


def acorn():
    nut = blob([(165, 245), (375, 245), (385, 330), (345, 410), (270, 465), (195, 410), (155, 330)])
    cap = unary_union([ellipse(270, 235, 128, 82), box(142, 235, 398, 262)])
    layers = [
        L(FRAME, "blue", cuts=[curve([(-10, 130), (140, 115), (300, 140), (550, 108)])]),
        L(circle(455, 75, 44), "yellow"),
        ground(450, "green"),
        L(nut, "orange"),
        L(cap, "brown", cuts=[curve([(130, 235), (270, 205), (410, 235)])]),
        L(ellipse(105, 95, 80, 38, rot=-20), "green"),
        L(ellipse(440, 205, 76, 36, rot=25), "green"),
    ]
    ink = [thick([(270, 155), (272, 120), (290, 100)], 12), thick([(60, 110), (125, 85)], 3, smooth=False),
           thick([(405, 220), (460, 195)], 3, smooth=False)]
    return layers, ink


def apple_basket():
    layers = [
        L(FRAME, "blue"),
        ground(405, "green"),
        L(circle(270, 175, 76), "yellow"),
        L(circle(205, 245, 76), "red"),
        L(circle(335, 245, 76), "red"),
        L(Polygon([(95, 290), (445, 290), (410, 460), (130, 460)]).buffer(10).buffer(-10), "brown",
          cuts=[LineString([(80, 348), (460, 348)]), LineString([(80, 404), (460, 404)])]),
    ]
    ink = [thick([(270, 100), (276, 70)], 5, smooth=False), thick([(205, 170), (211, 142)], 5, smooth=False),
           thick([(335, 170), (341, 142)], 5, smooth=False)]
    return layers, ink


def pie():
    cx, cy = 270, 250
    layers = [L(FRAME, "red"), L(circle(cx, cy, 228), "brown"), L(circle(cx, cy, 150), "orange")]
    for k in range(6):
        if k % 2:
            wedge = sector(cx, cy, 0, 150, k * 60 + 30, k * 60 + 90)
            layers.append(L(wedge, "yellow"))
    layers.append(L(circle(cx, cy, 62), "white"))
    ink = []
    for k in range(6):
        a = math.radians(k * 60 + 30)
        ink.append(thick([(cx + 62 * math.cos(a), cy + 62 * math.sin(a)), (cx + 228 * math.cos(a), cy + 228 * math.sin(a))], 4, smooth=False))
    return layers, ink


def corn():
    ear = ellipse(270, 235, 82, 185)
    husk_l = Polygon(catmull([(270, 440), (150, 330), (140, 230), (200, 330), (270, 400)], closed=True, n=8)).buffer(0)
    layers = [
        L(FRAME, "blue", cuts=[curve([(-10, 120), (140, 105), (300, 130), (550, 100)])]),
        L(circle(455, 80, 46), "orange"),
        ground(440, "brown"),
        L(ellipse(105, 300, 40, 150, rot=12), "green"),
        L(ellipse(435, 300, 40, 150, rot=-12), "green"),
        L(ear, "yellow", cuts=[curve([(150, 160), (270, 135), (390, 160)]), curve([(150, 260), (270, 235), (390, 260)]),
                               curve([(150, 360), (270, 335), (390, 360)])]),
        L(Polygon(catmull([(270, 470), (170, 400), (160, 270), (225, 380), (270, 420)], closed=True, n=8)).buffer(0), "green"),
        L(Polygon(catmull([(270, 470), (370, 400), (380, 270), (315, 380), (270, 420)], closed=True, n=8)).buffer(0), "green"),
    ]
    ink = [thick([(270, 60), (270, 50)], 3, smooth=False)]
    return layers, ink


def sunflower():
    cx, cy = 270, 215
    layers = [L(FRAME, "blue"),
              ground(372, "green", 8),
              L(rrect(242, 280, 298, 480, 8), "green")]
    for k in range(10):
        a = k * 36 + 18
        r = math.radians(a)
        layers.append(L(ellipse(cx + 128 * math.sin(r), cy - 128 * math.cos(r), 42, 80, rot=a), "orange" if k % 2 else "yellow"))
    layers += [L(ellipse(150, 440, 90, 34, rot=-18), "green"), L(ellipse(390, 440, 90, 34, rot=18), "green"),
               L(circle(cx, cy, 84), "brown")]
    return layers, []


PICTURES = [
    ("turkey", "Friendly Turkey", turkey),
    ("pumpkin", "Harvest Pumpkin", pumpkin),
    ("cornucopia", "Cornucopia", cornucopia),
    ("maple", "Maple Leaf", maple),
    ("acorn", "Acorn", acorn),
    ("basket", "Apple Basket", apple_basket),
    ("pie", "Pumpkin Pie", pie),
    ("corn", "Corn on the Cob", corn),
    ("sunflower", "Sunflower", sunflower),
]
