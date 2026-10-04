"""Halloween line-art pictures for the colour-by-note set, drawn in code.

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
def jack_o_lantern():
    layers = [
        L(FRAME, "purple", cuts=[curve([(-10, 150), (120, 120), (260, 150), (550, 110)])]),
        L(circle(455, 75, 48), "yellow"),
        L(blob([(-20, 420), (140, 395), (300, 410), (460, 390), (560, 405), (560, 520), (-20, 520)]), "green"),
        L(ellipse(342, 122, 60, 34, rot=-20), "green"),
        L(thick([(266, 175), (272, 118), (292, 88)], 46), "green"),
        L(ellipse(180, 310, 120, 135), "orange"),
        L(ellipse(360, 310, 120, 135), "orange"),
        L(ellipse(270, 310, 100, 148), "orange"),
        L(ellipse(228, 262, 32, 38), "black"),
        L(ellipse(312, 262, 32, 38), "black"),
        L(blob([(196, 335), (235, 350), (270, 354), (305, 350), (344, 335), (330, 380), (300, 404), (270, 410), (240, 404), (210, 380)]), "black"),
    ]
    ink = [Polygon([(258, 315), (282, 315), (270, 297)])]
    return layers, ink


def bat():
    lw = Polygon(catmull([(244, 205), (170, 150), (110, 128), (36, 150), (66, 200), (60, 262), (108, 236), (128, 300), (170, 262), (244, 335)], closed=False, n=10)).buffer(0)
    layers = [
        L(FRAME, "purple", cuts=[curve([(-10, 70), (180, 40), (360, 70), (550, 40)])]),
        L(circle(455, 80, 55), "yellow"),
        L(blob([(-20, 430), (120, 400), (280, 420), (420, 390), (560, 410), (560, 520), (-20, 520)]), "green"),
        L(lw, "black", cuts=[LineString([(250, 235), (66, 200), (-40, 190)])]),
        L(mirror(lw), "black", cuts=[mirror(LineString([(250, 235), (66, 200), (-40, 190)]))]),
        L(unary_union([ellipse(270, 315, 70, 90),
                       Polygon([(208, 140), (212, 66), (250, 110)]).buffer(6).buffer(-6),
                       Polygon([(332, 140), (328, 66), (290, 110)]).buffer(6).buffer(-6),
                       circle(270, 180, 80)]), "black", cuts=[curve([(170, 262), (270, 276), (370, 262)])]),
        L(circle(233, 166, 31), "white"),
        L(circle(307, 166, 31), "white"),
    ]
    ink = [thick([(258, 210), (270, 216), (282, 210)], 4)]
    return layers, ink


def ghost():
    body = blob([(270, 70), (350, 95), (385, 180), (390, 300), (400, 420), (372, 398), (345, 428), (315, 400), (285, 432),
                 (255, 400), (225, 430), (195, 400), (168, 424), (150, 420), (155, 300), (158, 180), (190, 95)])
    layers = [
        L(FRAME, "blue", cuts=[curve([(-10, 250), (130, 230), (260, 260), (400, 225), (550, 250)])]),
        L(cloud(95, 85, 0.95), "gray"),
        L(cloud(450, 140, 0.9), "gray"),
        L(blob([(-20, 455), (150, 445), (300, 458), (450, 442), (560, 452), (560, 520), (-20, 520)]), "green"),
        L(ellipse(136, 272, 60, 37, rot=-35), "white"),
        L(ellipse(404, 272, 60, 37, rot=35), "white"),
        L(body, "white", cuts=[curve([(140, 330), (270, 315), (400, 330)])]),
        L(ellipse(232, 190, 28, 36), "black"),
        L(ellipse(308, 190, 28, 36), "black"),
    ]
    ink = [ellipse(270, 262, 12, 15)]
    return layers, ink


def haunted_house():
    layers = [
        L(FRAME, "blue", cuts=[curve([(-10, 190), (140, 170), (300, 200), (550, 175)])]),
        L(circle(462, 82, 46), "yellow"),
        L(blob([(-20, 430), (150, 412), (300, 425), (450, 405), (560, 420), (560, 520), (-20, 520)]), "green"),
        L(box(90, 290, 200, 445), "gray"),
        L(Polygon([(70, 300), (145, 215), (220, 300)]), "purple"),
        L(box(185, 205, 420, 445), "gray"),
        L(Polygon([(160, 215), (302, 95), (445, 215)]), "purple"),
        L(rrect(118, 330, 172, 392, 8), "yellow"),
        L(unary_union([box(210, 250, 262, 300), circle(236, 250, 26)]), "yellow"),
        L(unary_union([box(342, 250, 394, 300), circle(368, 250, 26)]), "yellow"),
        L(unary_union([box(272, 360, 332, 445), circle(302, 360, 30)]), "green"),
        L(circle(302, 168, 32), "yellow"),
        L(rrect(208, 340, 258, 395, 6), "yellow"),
        L(rrect(346, 340, 396, 395, 6), "yellow"),
    ]
    ink = [thick([(40, 120), (52, 110), (60, 118), (68, 110), (80, 120)], 4, smooth=False),
           thick([(395, 150), (405, 142), (412, 148), (419, 142), (429, 150)], 4, smooth=False),
           circle(318, 405, 4)]
    return layers, ink


def cat():
    pickets = []
    for x in (14, 308, 384, 460):
        pickets.append(unary_union([box(x, 275, x + 56, 425), Polygon([(x, 276), (x + 28, 248), (x + 56, 276)])]))
    cat_shape = unary_union([
        ellipse(210, 360, 92, 92),
        circle(210, 225, 72),
        Polygon([(150, 200), (150, 125), (196, 162)]).buffer(5).buffer(-5),
        Polygon([(270, 200), (270, 125), (224, 162)]).buffer(5).buffer(-5),
        thick([(270, 440), (340, 452), (400, 446), (432, 425)], 30),
    ])
    layers = [
        L(FRAME, "purple", cuts=[curve([(-10, 120), (140, 100), (300, 130), (550, 100)])]),
        L(circle(410, 120, 80), "yellow"),
        L(unary_union(pickets), "brown"),
        L(blob([(-20, 418), (150, 408), (300, 418), (450, 404), (560, 414), (560, 520), (-20, 520)]), "green"),
        L(cat_shape, "black", cuts=[curve([(130, 300), (210, 286), (290, 300)])]),
    ]
    ink = [thick([(180, 218), (190, 208), (200, 218)], 4, smooth=False),
           thick([(220, 218), (230, 208), (240, 218)], 4, smooth=False),
           Polygon([(202, 238), (218, 238), (210, 248)]),
           thick([(196, 256), (210, 262), (224, 256)], 3)]
    return layers, ink


def cauldron():
    pot = unary_union([ellipse(270, 315, 165, 100), rrect(90, 204, 450, 256, 22)])
    flames = blob([(135, 478), (145, 400), (180, 350), (205, 400), (235, 360), (270, 410), (305, 360),
                   (335, 400), (360, 350), (395, 400), (405, 478)])
    layers = [
        L(FRAME, "purple", cuts=[curve([(-10, 330), (140, 300), (300, 330), (550, 300)])]),
        L(flames, "orange"),
        L(rrect(100, 450, 440, 500, 20), "brown"),
        L(circle(230, 105, 36), "green"),
        L(circle(330, 66, 33), "green"),
        L(circle(395, 140, 30), "green"),
        L(blob([(110, 215), (170, 160), (270, 145), (370, 160), (430, 215), (270, 228)]), "green"),
        L(pot, "black", cuts=[LineString([(60, 257), (480, 257)])]),
        L(blob([(122, 254), (186, 254), (190, 305), (156, 330), (124, 305)]), "green"),
        L(blob([(326, 254), (390, 254), (388, 300), (358, 318), (330, 300)]), "green"),
    ]
    ink = [circle(160, 186, 7), circle(298, 160, 6), circle(250, 70, 5)]
    return layers, ink


def candy():
    corn = Polygon(catmull([(175, 60), (215, 120), (258, 250), (262, 330), (175, 345), (88, 330), (92, 250), (135, 120)], closed=True, n=10)).buffer(0)
    c_tip = corn.intersection(box(0, 0, W, 165))
    c_mid = corn.intersection(box(0, 165, W, 262))
    c_base = corn.intersection(box(0, 262, W, H))
    wrapped = unary_union([ellipse(410, 120, 62, 46)])
    end_l = Polygon([(356, 120), (280, 60), (280, 180)]).buffer(6).buffer(-6)
    end_r = Polygon([(464, 120), (536, 60), (536, 180)]).buffer(6).buffer(-6)
    pop = circle(410, 292, 86)
    layers = [
        L(FRAME, "white", cuts=[curve([(-10, 200), (100, 190), (200, 215), (300, 200)])]),
        L(blob([(-20, 380), (150, 372), (300, 384), (450, 370), (560, 378), (560, 520), (-20, 520)]), "purple"),
        L(rrect(388, 360, 432, 474, 5), "white"),
        L(end_l, "purple"), L(end_r, "purple"),
        L(wrapped, "green"),
        L(pop, "orange"),
        L(circle(410, 292, 38), "yellow"),
        L(c_tip, "white"), L(c_mid, "orange"), L(c_base, "yellow"),
        L(Polygon([(84, 438), (6, 384), (6, 492)]).buffer(6).buffer(-6), "orange"),
        L(Polygon([(186, 438), (264, 384), (264, 492)]).buffer(6).buffer(-6), "orange"),
        L(ellipse(135, 438, 58, 42), "green"),
    ]
    ink = []
    return layers, ink


def spider():
    web_layers = [L(sector(0, 0, 0, 95, 0, 90), "gray")]
    for a0 in (0, 30, 60):
        web_layers.append(L(sector(0, 0, 95, 175, a0, a0 + 30), "gray"))
        web_layers.append(L(sector(0, 0, 175, 255, a0, a0 + 30), "gray"))
    layers = [L(FRAME, "purple")] + web_layers + [
        L(ellipse(100, 436, 94, 58), "orange"),
        L(ellipse(100, 436, 36, 58), "orange"),
        L(circle(340, 350, 88), "black"),
        L(circle(340, 196, 84), "black"),
        L(circle(303, 180, 31), "white"),
        L(circle(377, 180, 31), "white"),
    ]
    legs = []
    for side in (-1, 1):
        for th in (-40, -10, 20, 50):
            c = (340, 350)

            def at(r, a):
                return (c[0] + side * r * math.cos(math.radians(a)), c[1] + r * math.sin(math.radians(a)))
            p0, p1, p2 = at(70, th), at(135, th - 12), at(185, th + 12)
            legs.append(thick([p0, p1, p2], 9, smooth=False))
    ink = legs + [LineString([(340, -5), (340, 116)]).buffer(1.2),
                  thick([(328, 226), (340, 232), (352, 226)], 4),
                  Polygon([(100, 382), (95, 362), (107, 360), (107, 384)])]
    return layers, ink


def moon_night():
    moon = circle(310, 190, 140).difference(circle(375, 150, 125))
    layers = [
        L(FRAME, "blue", cuts=[curve([(-10, 150), (130, 130), (260, 165), (550, 130)]),
                               curve([(-10, 300), (130, 285), (300, 315), (550, 290)])]),
        L(star(95, 85, 52, 26), "yellow"),
        L(star(462, 74, 56, 28), "yellow"),
        L(star(115, 262, 52, 26), "yellow"),
        L(moon, "yellow"),
        L(cloud(395, 290, 1.0), "gray"),
        L(blob([(-20, 400), (90, 360), (210, 375), (330, 420), (330, 520), (-20, 520)]), "purple"),
        L(blob([(180, 520), (230, 430), (360, 380), (470, 390), (560, 420), (560, 520)]), "green"),
        L(blob([(-20, 470), (100, 440), (220, 465), (300, 520), (-20, 520)]), "green"),
    ]
    ink = []
    return layers, ink


PICTURES = [
    ("pumpkin", "Jack-o'-Lantern", jack_o_lantern),
    ("bat", "Bat and Moon", bat),
    ("ghost", "Friendly Ghost", ghost),
    ("house", "Haunted House", haunted_house),
    ("cat", "Black Cat", cat),
    ("cauldron", "Cauldron", cauldron),
    ("candy", "Candy", candy),
    ("spider", "Spider", spider),
    ("moon", "Moon and Stars", moon_night),
]
