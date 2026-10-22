"""The 20 bee & honeycomb coloring pages, drawn in code (no AI). Writes art/raw/NN-slug.png (896 x 1152).

  python3 pages.py        # all pages
  python3 pages.py 03 07  # some pages

process.py then makes them bold, closed print art, exactly as for the other coloring sets.
Every page is composed from lib.py parts: bee(), daisy, leaf, hexagons, ... drawn back to front.
"""
import json, math, os, sys
from lib import *

HERE = os.path.dirname(os.path.abspath(__file__))
CX = 448


def ground(c, y, amp=22, n=6, color=255):
    """A rolling ground line from frame to frame, filled below (closes the bottom into colourable ground)."""
    pts = [(-20, y)]
    for i in range(n + 1):
        pts.append((i * 896 / n, y + (amp if i % 2 else -amp)))
    pts.append((916, y))
    sp = spline(pts, False, 12)
    poly = sp + [(916, 1170), (-20, 1170)]
    c.poly(poly, fill=255, outline=False)
    c.stroke(sp, W)


def grass(c, x, y, h=60, n=3):
    for i in range(n):
        dx = (i - (n - 1) / 2) * 22
        tip = (x + dx * 1.6, y - h + abs(i - (n - 1) / 2) * 10)
        c.stroke(spline([(x + dx * 0.3, y), (x + dx, y - h * 0.5), tip], False, 8), W)


def tulip(c, x, y, h=230, w=84, stem_curve=10):
    """Tulip: stem and two leaves, then a cup with three petal tips."""
    cup_h = w * 1.15
    top = y - h
    stem(c, [(x, y), (x + stem_curve, y - h * 0.5), (x, top + cup_h * 0.9)], 20, 18)
    leaf(c, x, y - 20, min(170, max(70, h * 0.42)), 26, -118)
    leaf(c, x, y - 30, min(160, max(64, h * 0.38)), 25, -62)
    L, R = x - w / 2, x + w / 2
    bot = top + cup_h
    left = spline([(x - w * 0.12, bot + 6), (L + 2, bot - cup_h * 0.35), (L - 4, top + cup_h * 0.12)], False, 10)
    right = spline([(R + 4, top + cup_h * 0.12), (R - 2, bot - cup_h * 0.35), (x + w * 0.12, bot + 6)], False, 10)
    outline = left + [(x - w * 0.2, top + cup_h * 0.46), (x, top - cup_h * 0.06), (x + w * 0.2, top + cup_h * 0.46)] + right
    c.poly(outline)
    # front petal edge lines
    c.stroke(spline([(x - w * 0.2, top + cup_h * 0.46), (x - w * 0.14, bot - cup_h * 0.3), (x, bot + 4)], False, 8), W * 0.9)
    c.stroke(spline([(x + w * 0.2, top + cup_h * 0.46), (x + w * 0.14, bot - cup_h * 0.3), (x, bot + 4)], False, 8), W * 0.9)


def lavender(c, x, y, h=420, tilt=0):
    top = (x + tilt, y - h)
    stem(c, [(x, y), (x + tilt * 0.4, y - h * 0.5), top], 20, 16)
    for i in range(5):
        t = 0.42 + i * 0.1
        px, py = x + tilt * (t ** 1.3), y - h * t
        s = 1.0 - 0.07 * i
        ellipse(c, px - 30 * s, py - 4, 15 * s, 30 * s, -32)
        ellipse(c, px + 30 * s, py - 4, 15 * s, 30 * s, 32)
    ellipse(c, top[0], top[1] - 26, 17, 34, 0)


def clover(c, x, y, r=46, rot=0):
    """Three heart-ish leaves round a centre, plus a stem."""
    c.stroke([(x, y), (x + 6, y + 70)], W + 2)
    for i in range(3):
        a = math.radians(rot - 90 + 120 * i)
        px, py = x + r * 0.8 * math.cos(a), y + r * 0.8 * math.sin(a)
        circle(c, px, py, r * 0.72)
    circle(c, x, y, r * 0.3)


def ladybug(c, x, y, s=1.0, rot=0):
    def T(p):
        return xf(p, x, y, s, rot)
    for ang in (-52, 0, 52):
        pass
    c.poly(T(ellipse_pts(0, 0, 68, 58, 0, 72)))
    c.poly(T(ellipse_pts(62, 0, 28, 30, 0, 36)))
    c.stroke(T([(-68, 0), (62, 0)][:1] + [(30, 0)]), 0.1)
    c.stroke(T([(-66, 0), (36, 0)]), W)
    for (dx, dy) in ((-30, -26), (6, -30), (-30, 26), (6, 30)):
        c.dot(*T([(dx, dy)])[0], 9 * s)
    for ang in (-38, 38):
        a = math.radians(ang)
        c.stroke(T([(80, 22 * (1 if ang > 0 else -1)), (104, 44 * (1 if ang > 0 else -1))]), W * 0.9)


def star(c, x, y, r, rot=-90):
    pts = []
    for i in range(10):
        a = math.radians(rot + 36 * i)
        rr = r if i % 2 == 0 else r * 0.46
        pts.append((x + rr * math.cos(a), y + rr * math.sin(a)))
    c.poly(pts)


def heart(c, x, y, s):
    pts = [(0, 40), (-38, 4), (-40, -22), (-22, -40), (0, -22), (22, -40), (40, -22), (38, 4)]
    c.poly(spline(xf(pts, x, y, s), True, 8))


def drop(c, x, y, s):
    pts = [(0, -52), (30, -8), (34, 22), (14, 44), (-14, 44), (-34, 22), (-30, -8)]
    c.poly(spline(xf(pts, x, y, s), True, 8))


def hive(c, cx, base, w, h, door=True):
    """A straw skep: dome made of stacked curved bands."""
    n = 40
    left = [(cx - w / 2 * math.sqrt(1 - (i / n) ** 2), base - h * (i / n)) for i in range(0, n)]
    right = [(cx + w / 2 * math.sqrt(1 - (i / n) ** 2), base - h * (i / n)) for i in range(n, -1, -1)]
    top = [(cx, base - h)]
    sil = left + top + right[1:]
    c.poly(sil + [(cx + w / 2 + 14, base + 6), (cx - w / 2 - 14, base + 6)][:0])
    c.stroke([(cx - w / 2 - 16, base), (cx + w / 2 + 16, base)], W)
    for t in (0.2, 0.4, 0.6, 0.8):
        hw = w / 2 * math.sqrt(1 - t * t)
        y = base - h * t
        c.stroke(spline([(cx - hw, y), (cx, y + 22), (cx + hw, y)], False, 14), W)
    if door:
        dw, dh = w * 0.2, h * 0.34
        arch = [(cx - dw, base)] + [(cx + dw * math.cos(math.radians(a)), base - dh + dw * 0.1 - dw * math.sin(math.radians(a))) for a in range(180, -1, -15)] + [(cx + dw, base)]
        c.poly(arch, fill=0)


def stand(c, cx, top, w=300, h=40, legs=230):
    c.poly([(cx - w / 2, top), (cx + w / 2, top), (cx + w / 2, top + h), (cx - w / 2, top + h)])
    c.stroke([(cx - w / 2 + 30, top + h), (cx - w / 2 + 10, top + h + legs)], W + 4)
    c.stroke([(cx + w / 2 - 30, top + h), (cx + w / 2 - 10, top + h + legs)], W + 4)


def honeycomb(c, cx, cy, rows, L, drips=()):
    """rows = list of cell counts per row (flat-top hex layout, rows interleaved). Returns the cell centres."""
    dy = math.sqrt(3) * L
    dx = 1.5 * L
    centres = []
    # pointy layout by columns: columns of cells, offset every other column
    cols = rows
    ncol = len(cols)
    for ci, cnt in enumerate(cols):
        x = cx + (ci - (ncol - 1) / 2) * dx
        off = (dy / 2) if ci % 2 else 0
        for k in range(cnt):
            y = cy + (k - (cnt - 1) / 2) * dy + (0 if cnt % 2 == (1 if ci % 2 == 0 else 1) else 0)
            centres.append((x, y))
    for (x, y) in centres:
        hexcell(c, x, y, L)
    return centres


# ----------------------------------------------------------------------------------------------
def p01(c):  # bee on a daisy
    sun(c, 760, 150, 52, 10)
    cloud(c, 170, 180, 0.9)
    ground(c, 1030, 18, 4)
    stem(c, [(CX, 1040), (CX - 12, 900), (CX + 6, 780)], 34, 30)
    leaf(c, CX - 6, 960, 190, 44, -160)
    leaf(c, CX + 2, 900, 200, 46, -22)
    petal_flower(c, CX, 600, 250, 12, 78, rot=8)
    bee(c, 330, 280, 1.45, -8)


def p02(c):  # honeycomb and bee
    cells = honeycomb(c, CX, 380, [3, 4, 3, 4, 3], 86)
    bee(c, 470, 880, 1.7, -6, flip=True)


def p03(c):  # skep beehive
    cloud(c, 700, 150, 0.8)
    ground(c, 1000, 16, 4)
    stand(c, CX, 800, 330, 42, 160)
    hive(c, CX, 800, 300, 400)
    bee(c, 150, 330, 0.7, -12)
    bee(c, 700, 420, 0.7, 10, flip=True)
    bee(c, 300, 560, 0.62, 25, flip=True)
    tulip(c, 110, 1040, 170, 66)
    tulip(c, 790, 1040, 150, 62)


def p04(c):  # honey jar and dipper
    ground(c, 1010, 12, 3)
    # jar
    x0, x1, top, bot = 210, 690, 480, 960
    body = [(x0 + 60, top)] + [(x1 - 60, top)] + [(x1, top + 60), (x1 + 14, top + 200), (x1 + 8, bot - 70), (x1 - 40, bot), (x0 + 40, bot), (x0 - 8, bot - 70), (x0 - 14, top + 200), (x0, top + 60)]
    c.poly(spline(body, True, 8))
    # honey level wave line
    c.stroke(spline([(x0 - 8, top + 130), (300, top + 160), (CX, top + 120), (600, top + 160), (x1 + 12, top + 130)], False, 12), W)
    # label
    c.poly(spline([(260, 650), (CX, 636), (640, 650), (650, 800), (CX, 818), (250, 800)], True, 8))
    heart(c, CX, 728, 1.2)
    # lid
    c.poly([(x0 + 40, top - 70), (x1 - 40, top - 70), (x1 - 40, top), (x0 + 40, top)])
    c.stroke([(x0 + 40, top - 30), (x1 - 40, top - 30)], W)
    # dipper leaning on the jar
    hx, hy = 660, 330
    c.poly(ribbon(spline([(hx + 60, hy + 40), (hx + 160, hy - 120), (hx + 210, hy - 230)], False, 8), 24, 24))
    ellipse(c, hx + 28, hy + 70, 70, 54, -32)
    for t in (-26, 0, 26):
        c.stroke(xf([(-52, t), (52, t)], hx + 28, hy + 70, 1, -32), W)
    bee(c, 250, 250, 1.05, -8)


def p05(c):  # sunflower with two bees
    ground(c, 1040, 14, 4)
    stem(c, [(CX, 1050), (CX + 8, 900), (CX - 4, 720)], 40, 36)
    leaf(c, CX + 4, 960, 220, 56, -22)
    leaf(c, CX - 4, 900, 210, 54, -158)
    petal_flower(c, CX, 520, 330, 16, 130, rot=4, pointed=True, dots=False)
    # sunflower seeds: dots in two rings
    for r, n in ((46, 8), (92, 14)):
        for i in range(n):
            a = 2 * math.pi * i / n + 0.3
            c.dot(CX + r * math.cos(a), 520 + r * math.sin(a), 6)
    c.dot(CX, 520, 7)
    bee(c, 190, 150, 0.8, -10)
    bee(c, 745, 945, 0.8, 8, flip=True)


def p06(c):  # queen bee
    for (x, y) in ((130, 150), (770, 190), (450, 90)):
        star(c, x, y, 46)
    ground(c, 1010, 14, 4)
    for (x, h) in ((150, 200), (746, 240)):
        stem(c, [(x, 1020), (x + 4, 1020 - h / 2), (x, 1020 - h)], 18, 16)
        petal_flower(c, x, 1020 - h - 40, 60, 6, 30, dots=False)
    bee(c, 410, 560, 1.75, -4, crown=True, wings_up=True)
    heart(c, 770, 360, 1.1)
    heart(c, 120, 520, 0.9)
    heart(c, 450, 900, 0.8)
    bee(c, 190, 300, 0.62, -12)
    bee(c, 600, 700, 0.62, 10, flip=True)


def p07(c):  # lavender
    ground(c, 1050, 14, 4)
    lavender(c, 160, 1060, 560, 20)
    lavender(c, 330, 1060, 720, -14)
    lavender(c, 740, 1060, 640, -10)
    lavender(c, 590, 1060, 520, 20)
    bee(c, 480, 300, 1.0, -8)


def p08(c):  # bumblebee on clover
    ground(c, 980, 18, 4)
    for (x, y, r, rot) in ((130, 880, 70, 5), (330, 900, 64, 20), (560, 920, 70, -15), (760, 860, 80, 40)):
        clover(c, x, y, r, rot)
    bee(c, 440, 520, 1.8, 6, fuzzy=True, stripes=3)
    cloud(c, 190, 150, 0.8)
    sun(c, 760, 160, 46, 10)
    petal_flower(c, 450, 1060, 40, 5, 16, dots=False)


def p09(c):  # bee parade
    bee(c, 330, 240, 0.95, -5)
    bee(c, 570, 560, 0.95, 5, flip=True)
    bee(c, 340, 880, 0.95, -6)
    for (x, y) in ((740, 190), (130, 590), (760, 930)):
        petal_flower(c, x, y, 84, 6, 34, dots=False)
    for (x, y) in ((470, 330), (200, 760), (700, 780), (470, 1060)):
        petal_flower(c, x, y, 54, 5, 21, dots=False)


def p10(c):  # teacup of honey with a bee
    ground(c, 980, 10, 3)
    ellipse(c, CX, 880, 310, 64)                     # saucer
    c.poly(ellipse_pts(CX, 880, 150, 28, 0, 40))     # cup foot ring
    # handle
    c.poly(ribbon(spline([(660, 610), (790, 590), (800, 710), (690, 760)], False, 12), 36, 36))
    c.poly(spline([(210, 580), (230, 740), (320, 840), (CX, 862), (576, 840), (666, 740), (686, 580)], True, 10))
    ellipse(c, CX, 580, 238, 56)                     # rim
    ellipse(c, CX, 584, 190, 36)                     # honey surface
    c.stroke(spline([(250, 700), (CX, 745), (646, 700)], False, 12), W)
    heart(c, CX, 790, 0.7)
    c.stroke(spline([(380, 440), (410, 400), (380, 360), (410, 320)], False, 10), W)
    c.stroke(spline([(520, 440), (550, 400), (520, 360), (550, 320)], False, 10), W)
    bee(c, 300, 200, 0.95, -6)
    sun(c, 760, 150, 46, 10)
    for x in (90, 810):
        stem(c, [(x, 1010), (x + 4, 930), (x, 860)], 16, 14)
        petal_flower(c, x, 820, 46, 6, 24, dots=False)
    bee(c, 650, 300, 0.6, 8, flip=True)


def p11(c):  # bee above a giant tulip
    ground(c, 1040, 12, 3)
    tulip(c, CX, 1070, 640, 320)
    bee(c, 330, 200, 1.15, -10)
    tulip(c, 110, 1070, 330, 110, -12)
    tulip(c, 800, 1070, 390, 120, 12)


def p12(c):  # baby bee on a leaf
    ground(c, 1030, 10, 3)
    leaf(c, 110, 880, 700, 210, -12)
    bee(c, 420, 560, 1.85, 0, mood="happy")
    heart(c, 740, 230, 1.0)
    star(c, 150, 220, 42)
    petal_flower(c, 130, 960, 74, 6, 28, dots=False)
    petal_flower(c, 770, 930, 78, 6, 30, dots=False)
    sun(c, 760, 130, 48, 10)
    cloud(c, 150, 130, 0.9)


def p13(c):  # honeycomb cells with a different picture in each
    cells = []
    L = 118
    dy, dx = math.sqrt(3) * L, 1.5 * L
    layout = [(0, 0)] + [(dx * math.cos(math.radians(60 * i + 30)) * 2 / math.sqrt(3) * 0 + 0, 0) for i in range(0)]
    cx, cy = CX, 580
    centers = [(cx, cy)]
    for i in range(6):
        a = math.radians(90 + 60 * i)
        centers.append((cx + math.sqrt(3) * L * math.cos(a), cy + math.sqrt(3) * L * math.sin(a)))
    # flat-top hexes arranged around the centre one: neighbours are at distance sqrt(3)*L along 30 + 60i degrees
    centers = [(cx, cy)] + [(cx + math.sqrt(3) * L * math.cos(math.radians(30 + 60 * i)), cy + math.sqrt(3) * L * math.sin(math.radians(30 + 60 * i))) for i in range(6)]
    for (x, y) in centers:
        hexcell(c, x, y, L)
    mx, my = centers[0]
    bee(c, mx, my + 6, 0.52, 0)
    petal_flower(c, *centers[1], 56, 6, 22, dots=False)
    drop(c, *centers[2], 1.5)
    heart(c, *centers[3], 1.6)
    petal_flower(c, *centers[4], 56, 5, 22, dots=False)
    star(c, centers[5][0], centers[5][1], 62)
    ladybug(c, centers[6][0], centers[6][1], 0.78, -20)
    bee(c, 190, 150, 0.6, -10)
    bee(c, 720, 1000, 0.6, 10, flip=True)


def p14(c):  # bee and ladybug on a leaf
    ground(c, 1040, 10, 3)
    leaf(c, 70, 860, 760, 230, -8)
    leaf(c, 790, 780, 330, 110, -140)
    bee(c, 300, 450, 1.25, -8)
    ladybug(c, 640, 760, 1.35, -10)
    petal_flower(c, 160, 200, 78, 6, 30, dots=False)
    petal_flower(c, 770, 190, 86, 6, 32, dots=False)


def p15(c):  # meadow flight
    sun(c, 740, 150, 60, 12)
    cloud(c, 190, 200, 1.0)
    ground(c, 880, 24, 5)
    for (x, h, kind) in ((120, 250, 0), (290, 330, 1), (470, 240, 0), (650, 330, 1), (800, 250, 0)):
        stem(c, [(x, 1000), (x + 5, 1000 - h * 0.5), (x, 1000 - h)], 18, 16)
        if kind == 0:
            petal_flower(c, x, 1000 - h - 30, 62, 6, 30, dots=False)
        else:
            petal_flower(c, x, 1000 - h - 30, 58, 6, 30, dots=False)
    bee(c, 290, 420, 0.95, -10)
    bee(c, 650, 520, 0.85, 10, flip=True)


def p16(c):  # watering can with flowers and a bee
    ground(c, 1000, 12, 3)
    c.poly(ribbon(spline([(230, 660), (140, 600), (180, 500), (330, 500), (400, 600)], False, 12), 30, 30))   # handle
    c.poly(ribbon(spline([(520, 900), (660, 820), (780, 640)], False, 10), 62, 40))                         # spout
    c.poly(xf(ellipse_pts(0, 0, 66, 32, 0, 40), 795, 615, 1, -58))                                          # rose
    c.poly(spline([(190, 650), (390, 622), (580, 650), (600, 930), (390, 962), (180, 930)], True, 8))       # body
    ellipse(c, 390, 650, 200, 36)
    c.stroke(spline([(190, 780), (390, 810), (592, 780)], False, 12), W)
    heart(c, 390, 870, 0.8)
    for (x, y) in ((850, 700), (860, 790), (800, 770)):
        drop(c, x, y, 0.5)
    stem(c, [(125, 1010), (130, 900), (125, 820)], 18, 16)
    petal_flower(c, 125, 770, 70, 6, 30, dots=False)
    bee(c, 420, 250, 1.2, -8)


def p17(c):  # flower wreath with a bee in the middle
    cx, cy, R = CX, 570, 330
    for i in range(12):
        a = 360 * i / 12
        x, y = cx + R * math.cos(math.radians(a)), cy + R * math.sin(math.radians(a))
        leaf(c, x, y, 130, 40, a + 90 + 20)
        leaf(c, x, y, 130, 40, a - 90 - 20)
    for i in range(6):
        a = 360 * i / 6 + 15
        x, y = cx + R * math.cos(math.radians(a)), cy + R * math.sin(math.radians(a))
        petal_flower(c, x, y, 86, 6, 34, dots=False, rot=a)
    bee(c, cx - 10, cy, 1.05, -6)


def p18(c):  # three flower pots with a bee
    ground(c, 1040, 8, 3)
    for (x, kind, h) in ((200, 0, 330), (CX, 1, 420), (700, 2, 300)):
        top = 880
        c.poly([(x - 100, top), (x + 100, top), (x + 76, 1040), (x - 76, 1040)])
        c.poly([(x - 116, top - 36), (x + 116, top - 36), (x + 116, top + 6), (x - 116, top + 6)])
        stem(c, [(x, top - 36), (x + 4, top - h * 0.55), (x, top - h)], 18, 16)
        if kind == 0:
            petal_flower(c, x, top - h - 50, 96, 6, 38, dots=False)
        elif kind == 1:
            petal_flower(c, x, top - h - 50, 104, 8, 40, dots=False)
        else:
            petal_flower(c, x, top - h - 50, 90, 6, 36, dots=False)
        leaf(c, x, top - 80, 90, 26, -150 if kind != 1 else 20)
    bee(c, 400, 150, 0.9, -8)


def p19(c):  # apple blossom branch with a bee
    c.poly(ribbon(spline([(-20, 330), (200, 400), (420, 370), (640, 450), (916, 390)], False, 12), 32, 24), fill=255)
    for (x, y, a) in ((300, 410, 80), (560, 430, 80), (110, 380, 90)):
        leaf(c, x, y, 130, 40, a)
    for (x, y, r, rot) in ((190, 340, 105, 0), (430, 300, 115, 20), (710, 420, 108, 10)):
        petal_flower(c, x, y, r, 5, 34, rot=rot, dots=False)
    for (x, y) in ((110, 650), (700, 700), (560, 1040)):
        petal_flower(c, x, y, 56, 5, 22, dots=False)
    bee(c, 400, 870, 1.45, -8)


def p20(c):  # sleepy bee on a crescent moon
    from shapely.geometry import Point
    moon = Point(450, 640).buffer(330, 64).difference(Point(600, 550).buffer(270, 64))
    c.poly(list(moon.exterior.coords))
    for (x, y, r) in ((170, 150, 46), (420, 100, 34), (730, 170, 42), (110, 400, 34), (800, 400, 36), (90, 640, 36)):
        star(c, x, y, r)
    bee(c, 560, 540, 1.25, -8, mood="sleep")
    cloud(c, 700, 90, 0.5)
    ground(c, 1040, 14, 4)
    for x in (110, 780):
        stem(c, [(x, 1050), (x + 4, 960), (x, 900)], 16, 14)
        petal_flower(c, x, 860, 50, 6, 26, dots=False)


PAGES = {}
for k, v in list(globals().items()):
    if k.startswith("p") and k[1:].isdigit():
        PAGES[int(k[1:])] = v

if __name__ == "__main__":
    S = json.load(open(os.path.join(HERE, "subjects.json")))["pages"]
    only = sys.argv[1:]
    os.makedirs(os.path.join(HERE, "art", "raw"), exist_ok=True)
    for i, (slug, name, _) in enumerate(S, 1):
        if only and slug[:2] not in only:
            continue
        c = Canvas()
        PAGES[i](c)
        c.save(os.path.join(HERE, "art", "raw", slug + ".png"))
        print("drew", slug)
