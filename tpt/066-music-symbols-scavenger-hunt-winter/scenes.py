"""Six winter scenes drawn in code (non-religious: snow, skates, cocoa, mittens). 720 x 450 viewBox, outline art for colouring."""
import math

W, H = 720, 450
INK = "#5a5a5a"
BASE = f'fill="#fff" stroke="{INK}" stroke-width="1.6" stroke-linejoin="round" stroke-linecap="round"'
NOF = 'fill="none"'


def R(x, y, w, h, rx=0, e=""): return f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" rx="{rx:g}" {e}/>'
def C(x, y, r, e=""): return f'<circle cx="{x:g}" cy="{y:g}" r="{r:g}" {e}/>'
def E(x, y, rx, ry, e=""): return f'<ellipse cx="{x:g}" cy="{y:g}" rx="{rx:g}" ry="{ry:g}" {e}/>'
def P(pts, e=""): return '<polygon points="' + " ".join(f"{a:g},{b:g}" for a, b in pts) + f'" {e}/>'
def D(d, e=""): return f'<path d="{d}" {e}/>'
def L(x1, y1, x2, y2, e=""): return f'<line x1="{x1:g}" y1="{y1:g}" x2="{x2:g}" y2="{y2:g}" {NOF} {e}/>'


def flake(x, y, r=7):
    o = ""
    for a in (0, 60, 120):
        dx, dy = r * math.cos(math.radians(a)), r * math.sin(math.radians(a))
        o += L(x - dx, y - dy, x + dx, y + dy)
    return o


def tree(x, yb, h):
    w = h * 0.6
    o = R(x - h * 0.05, yb - h * 0.2, h * 0.1, h * 0.2)
    o += P([(x - w / 2, yb - .16 * h), (x, yb - .56 * h), (x + w / 2, yb - .16 * h)])
    o += P([(x - .38 * w, yb - .42 * h), (x, yb - .80 * h), (x + .38 * w, yb - .42 * h)])
    o += P([(x - .26 * w, yb - .68 * h), (x, yb - h), (x + .26 * w, yb - .68 * h)])
    return o


def house(x, yb, w, h, roof, wins=2):
    yt = yb - h
    o = R(x, yt, w, h)
    o += P([(x - 8, yt), (x + w / 2, yt - roof), (x + w + 8, yt)])
    for i in range(int(w // 14)):
        o += C(x - 4 + i * 14 + 7, yt + 1, 4.5)
    o += R(x + w * .68, yt - roof * .72, 14, roof * .5)
    for i in range(wins):
        wx = x + 14 + i * (w - 28 - 22) / max(1, wins - 1) if wins > 1 else x + w * .2
        o += R(wx, yt + 20, 22, 22) + L(wx + 11, yt + 20, wx + 11, yt + 42) + L(wx, yt + 31, wx + 22, yt + 31)
    dx = x + w * .5 - 11 if wins == 1 else x + w * .5 - 11
    o += R(dx, yb - 40, 22, 40, 3) + C(dx + 17, yb - 20, 1.8)
    return o


def snowman(x, yb, r):
    o = C(x, yb - r, r) + C(x, yb - 2 * r - r * .72, r * .72) + C(x, yb - 2 * r - 1.44 * r - r * .52, r * .52)
    hy = yb - 2 * r - 1.44 * r - r * .52
    o += R(x - r * .4, hy - r * .9, r * .8, r * .5) + R(x - r * .62, hy - r * .45, r * 1.24, r * .12)
    o += P([(x, hy), (x + r * .7, hy + r * .1), (x, hy + r * .2)]) + C(x - r * .2, hy - r * .15, 1.4, f'fill="{INK}"') + C(x + r * .2, hy - r * .15, 1.4, f'fill="{INK}"')
    o += L(x - r * .72, yb - 2.2 * r, x - r * 1.5, yb - 2.9 * r) + L(x + r * .72, yb - 2.2 * r, x + r * 1.5, yb - 2.9 * r)
    return o


def lamp(x, yb, h):
    return L(x, yb, x, yb - h) + R(x - 8, yb - h - 18, 16, 18, 2) + P([(x - 11, yb - h - 18), (x, yb - h - 28), (x + 11, yb - h - 18)]) + R(x - 7, yb - 7, 14, 7)


def mug(x, y, s=1.0):
    o = R(x, y, 26 * s, 24 * s, 4) + D(f"M{x + 26 * s:g} {y + 5 * s:g} q{12 * s:g} {2 * s:g} {0} {14 * s:g}", NOF)
    o += D(f"M{x + 7 * s:g} {y - 3 * s:g} q-4 -6 0 -10 M{x + 15 * s:g} {y - 3 * s:g} q-4 -6 0 -10", NOF)
    return o


def cloud(x, y, s=1.0):
    return D(f"M{x:g} {y:g} q{-6 * s:g} {-16 * s:g} {18 * s:g} {-16 * s:g} q{8 * s:g} {-18 * s:g} {32 * s:g} {-6 * s:g} q{26 * s:g} {-4 * s:g} {22 * s:g} {22 * s:g} Z")


def ground(y, wave=10):
    return D(f"M2 {y} Q 120 {y - wave} 240 {y} T 480 {y} T 718 {y} V448 H2 Z")


def skater(x, y, s=1.0, scarf=True):
    o = C(x, y - 62 * s, 10 * s) + D(f"M{x - 11 * s:g} {y - 66 * s:g} Q{x:g} {y - 88 * s:g} {x + 11 * s:g} {y - 66 * s:g} Z") + C(x, y - 85 * s, 4 * s)
    o += P([(x - 9 * s, y - 50 * s), (x + 9 * s, y - 50 * s), (x + 14 * s, y - 22 * s), (x - 14 * s, y - 22 * s)])
    o += L(x - 9 * s, y - 44 * s, x - 26 * s, y - 34 * s) + L(x + 9 * s, y - 44 * s, x + 26 * s, y - 52 * s)
    o += L(x - 6 * s, y - 22 * s, x - 10 * s, y - 4 * s) + L(x + 6 * s, y - 22 * s, x + 12 * s, y - 4 * s)
    o += L(x - 18 * s, y - 1 * s, x - 3 * s, y - 1 * s) + L(x + 4 * s, y - 1 * s, x + 20 * s, y - 1 * s)
    if scarf:
        o += R(x - 10 * s, y - 53 * s, 20 * s, 5 * s, 2) + R(x + 3 * s, y - 50 * s, 6 * s, 16 * s, 2)
    return o


def mitten(x, y, s=1.0):
    o = D(f"M{x:g} {y:g} h{28 * s:g} v{42 * s:g} q0 {16 * s:g} {-14 * s:g} {16 * s:g} q{-14 * s:g} {0} {-14 * s:g} {-16 * s:g} Z")
    o += D(f"M{x + 28 * s:g} {y + 20 * s:g} q{14 * s:g} {-2 * s:g} {13 * s:g} {12 * s:g} q{-2 * s:g} {10 * s:g} {-13 * s:g} {8 * s:g}")
    o += R(x - 2 * s, y - 2 * s, 32 * s, 10 * s, 2) + L(x + 4 * s, y + 22 * s, x + 4 * s, y + 38 * s) + L(x + 12 * s, y + 22 * s, x + 12 * s, y + 38 * s)
    o += R(x + 10 * s, y - 12 * s, 6 * s, 14 * s, 2)
    return o


def hat(x, y, s=1.0):
    o = D(f"M{x:g} {y + 40 * s:g} Q{x:g} {y:g} {x + 30 * s:g} {y:g} Q{x + 60 * s:g} {y:g} {x + 60 * s:g} {y + 40 * s:g} Z")
    o += R(x - 3 * s, y + 38 * s, 66 * s, 13 * s, 4) + C(x + 30 * s, y - 6 * s, 7 * s)
    o += L(x + 10 * s, y + 38 * s, x + 12 * s, y + 8 * s) + L(x + 30 * s, y + 38 * s, x + 30 * s, y + 4 * s) + L(x + 50 * s, y + 38 * s, x + 48 * s, y + 8 * s)
    return o


def scarf(x, y, s=1.0):
    o = R(x, y, 26 * s, 64 * s, 3) + L(x, y + 14 * s, x + 26 * s, y + 14 * s) + L(x, y + 28 * s, x + 26 * s, y + 28 * s)
    for i in range(5):
        o += L(x + 3 * s + i * 5 * s, y + 64 * s, x + 3 * s + i * 5 * s, y + 74 * s)
    return o


def peg(x, y):
    return R(x - 3, y - 6, 6, 12, 1.5)


def sled(x, y, s=1.0):
    o = R(x, y - 12 * s, 66 * s, 8 * s, 3) + D(f"M{x - 4 * s:g} {y + 2 * s:g} Q{x - 10 * s:g} {y - 6 * s:g} {x + 2 * s:g} {y - 5 * s:g}")
    o += L(x - 4 * s, y + 2 * s, x + 70 * s, y + 2 * s) + L(x + 12 * s, y - 4 * s, x + 12 * s, y + 2 * s) + L(x + 54 * s, y - 4 * s, x + 54 * s, y + 2 * s)
    return o


def kid(x, y, s=1.0):
    o = C(x, y - 34 * s, 9 * s) + D(f"M{x - 10 * s:g} {y - 38 * s:g} Q{x:g} {y - 56 * s:g} {x + 10 * s:g} {y - 38 * s:g} Z") + C(x, y - 56 * s, 4 * s)
    o += P([(x - 9 * s, y - 24 * s), (x + 9 * s, y - 24 * s), (x + 13 * s, y), (x - 13 * s, y)])
    o += L(x + 8 * s, y - 20 * s, x + 28 * s, y - 8 * s)
    return o


def stars(pts):
    return "".join(L(x - 3, y, x + 3, y) + L(x, y - 3, x, y + 3) for x, y in pts)


# ------------------------------------------------------------------------------ scenes
def scene1():
    o = C(630, 70, 30) + C(620, 62, 5) + C(640, 80, 3.5) + cloud(150, 80, 1.1) + cloud(420, 60, 0.9)
    o += D("M2 300 Q 150 230 300 290 T 600 270 T 718 290 V448 H2 Z")
    o += tree(690, 300, 90)
    o += house(40, 335, 120, 100, 60) + house(190, 330, 100, 120, 55, 2) + house(330, 340, 140, 95, 65, 2) + house(520, 335, 110, 105, 55, 2)
    o += ground(335, 8)
    o += D("M300 448 Q 330 380 390 345 L 450 345 Q 400 385 420 448 Z")
    o += lamp(300, 372, 70) + lamp(660, 400, 60)
    o += snowman(110, 430, 24) + tree(560, 440, 100) + tree(250, 440, 80) + tree(30, 420, 70)
    for x, y in ((70, 110), (250, 130), (340, 170), (520, 140), (580, 200), (60, 210), (440, 200), (690, 170), (200, 250), (400, 260)):
        o += flake(x, y, 6)
    return o


def scene2():
    o = "".join(tree(x, 175, h) for x, h in ((40, 90), (110, 70), (190, 100), (290, 75), (400, 95), (510, 70), (600, 100), (690, 80)))
    o += cloud(80, 70, 1.0) + cloud(480, 50, 1.2)
    o += R(2, 175, 716, 3, 0) + ground(178, 4)
    o += E(360, 320, 330, 100) + E(360, 320, 306, 82) + E(360, 320, 60, 22) + L(360, 238, 360, 402) + L(54, 320, 666, 320)
    # cocoa stand
    o += R(560, 150, 100, 68) + P([(552, 150), (610, 118), (668, 150)]) + R(572, 168, 46, 50) + mug(628, 170, 1.0)
    o += L(562, 150, 562, 218) + lamp(40, 252, 80) + lamp(680, 252, 80)
    o += skater(160, 312, 1.1) + skater(330, 340, 1.2) + skater(500, 300, 1.0) + skater(600, 345, 1.05, False)
    o += D("M2 400 Q 100 370 220 395 T 460 400 T 718 385 V448 H2 Z")
    for x, y in ((100, 120), (260, 110), (360, 90), (430, 140), (540, 90), (690, 100)):
        o += flake(x, y, 6)
    return o


def scene3():
    o = C(80, 70, 28) + stars([(180, 50), (260, 90), (330, 40), (440, 70), (520, 40), (610, 90), (670, 50), (400, 110)])
    o += tree(50, 330, 160) + tree(130, 340, 120) + tree(640, 330, 170) + tree(690, 345, 120) + tree(580, 345, 110)
    o += ground(330, 12)
    # cabin
    o += R(200, 200, 320, 190)
    for y in range(216, 390, 16):
        o += L(200, y, 520, y)
    o += P([(176, 200), (360, 100), (544, 200)])
    for i in range(14):
        o += C(184 + i * 26, 200, 8)
    o += R(450, 80, 28, 60) + R(444, 72, 40, 10, 2)
    o += D("M464 66 q-14 -14 0 -26 q14 -12 4 -26", NOF) + D("M470 52 q-12 -10 0 -20", NOF)
    o += R(230, 240, 76, 66) + L(268, 240, 268, 306) + L(230, 273, 306, 273) + R(224, 306, 88, 8, 2)
    o += R(400, 262, 70, 128, 3) + C(455, 330, 3) + R(386, 386, 98, 14, 2) + R(374, 398, 122, 14, 2)
    o += "".join(C(70 + (i % 4) * 22, 425 - (i // 4) * 18, 10) for i in range(8))
    o += sled(560, 410, 1.0) + snowman(120, 420, 22)
    for x, y in ((250, 140), (140, 120), (600, 150), (60, 180), (520, 100), (340, 40)):
        o += flake(x, y, 5)
    return o


def scene4():
    o = cloud(100, 70, 1.2) + cloud(520, 60, 1.0) + C(660, 50, 24)
    o += D("M2 190 C 160 170 300 250 460 300 C 560 330 640 340 718 345 V448 H2 Z")
    o += D("M2 330 C 140 320 260 380 400 400 C 500 415 600 410 718 420 V448 H2 Z")
    o += tree(60, 230, 110) + tree(135, 245, 85) + tree(560, 340, 90) + tree(640, 350, 80)
    o += "".join(L(x, y, x, y - 28) + P([(x, y - 28), (x + 16, y - 22), (x, y - 16)]) for x, y in ((250, 262), (330, 292), (410, 322)))
    o += sled(180, 290, 1.2) + kid(205, 281, 1.2) + sled(430, 380, 1.1) + kid(450, 372, 1.1)
    o += sled(60, 420, 1.0) + kid(80, 412, 1.0) + snowman(690, 440, 22)
    o += "".join(R(x, 410, 4, 24) for x in range(590, 690, 26)) + L(590, 418, 668, 418) + L(590, 428, 668, 428)
    for x, y in ((240, 110), (330, 80), (410, 140), (560, 130), (690, 120), (60, 130), (300, 200), (600, 240)):
        o += flake(x, y, 6)
    return o


def moon():
    """Crescent drawn as one closed outline (no white cutter), so the arc ends are round and never clipped."""
    cx, cy, r = MOON
    r2, dx, dy = 0.8 * r, 0.4 * r, -0.27 * r          # inner (cut-out) circle
    d = math.hypot(dx, dy)
    a = (r * r - r2 * r2 + d * d) / (2 * d)
    h = math.sqrt(r * r - a * a)
    ux, uy = dx / d, dy / d
    mx, my = cx + a * ux, cy + a * uy
    p1 = (mx - h * uy, my + h * ux)
    p2 = (mx + h * uy, my - h * ux)
    return D(f"M{p1[0]:.2f} {p1[1]:.2f} A{r:g} {r:g} 0 1 0 {p2[0]:.2f} {p2[1]:.2f} A{r2:g} {r2:g} 0 0 1 {p1[0]:.2f} {p1[1]:.2f} Z")


# decorative outlines (moons, clouds) that no hidden symbol's knock-out halo may touch
MOON = (120, 46, 22)
KEEPOUT = {1: [(600, 40, 660, 100), (148, 47, 230, 80), (418, 33, 486, 60)], 2: [(78, 40, 152, 70), (478, 14, 567, 50)], 3: [(52, 42, 108, 98)],
           4: [(98, 34, 187, 70), (518, 30, 592, 60), (636, 26, 684, 74)], 5: [(MOON[0] - 22, MOON[1] - 22, MOON[0] + 22, MOON[1] + 22)],
           6: [(118, 30, 192, 60), (558, 17, 640, 50)]}   # moon and cloud outlines, as (x0, y0, x1, y1)


def scene5():
    o = moon() + stars([(180, 40), (260, 80), (350, 40), (460, 70), (520, 110), (620, 60), (400, 120)])
    o += tree(40, 300, 190) + tree(120, 320, 140) + tree(300, 310, 150) + tree(640, 305, 200) + tree(560, 320, 130) + tree(700, 330, 120)
    o += ground(325, 14)
    # big tree with owl branch
    o += R(400, 120, 40, 230, 4) + L(420, 140, 420, 200) + D("M440 200 q60 -10 90 -40 M400 230 q-60 -10 -90 -50", NOF)
    o += P([(340, 140), (420, 40), (500, 140)]) + P([(360, 100), (420, 20), (480, 100)])
    o += E(520, 150, 20, 26) + C(512, 144, 6) + C(530, 144, 6) + P([(517, 152), (525, 152), (521, 160)], f'fill="{INK}"') + L(500, 126, 506, 118) + L(540, 126, 534, 118)
    # feeder and stumps
    o += L(180, 200, 180, 300) + R(160, 300, 40, 12, 3) + R(166, 286, 28, 14, 3) + P([(158, 286), (180, 268), (202, 286)])
    o += R(240, 380, 50, 36, 4) + E(265, 380, 25, 8) + R(600, 395, 44, 30, 4) + E(622, 395, 22, 7)
    o += "".join(E(x, y, 5, 8) for x, y in ((90, 390), (118, 400), (146, 390), (174, 402), (202, 392), (330, 400), (358, 408)))
    o += "".join(C(x, y, r) for x, y, r in ((340, 425, 18), (370, 430, 14), (60, 430, 20), (680, 420, 16)))
    for x, y in ((230, 130), (330, 220), (480, 250), (80, 170), (560, 210), (680, 190)):
        o += flake(x, y, 5)
    return o


def scene6():
    o = cloud(120, 60, 1.0) + cloud(560, 50, 1.1)
    o += R(40, 120, 12, 300, 2) + R(668, 120, 12, 300, 2) + R(34, 112, 24, 12, 3) + R(662, 112, 24, 12, 3)
    o += D("M52 140 Q 360 220 668 140", NOF) + D("M52 250 Q 360 330 668 250", NOF)
    # upper line items follow the curve y = 140 + 160*t*(1-t)*... approximate by sampling
    def curve_y(top, x):
        t = (x - 52) / 616
        return top + 160 * t * (1 - t)

    up = [("m", 110), ("h", 170), ("m", 250), ("s", 330), ("h", 400), ("m", 480), ("s", 540), ("m", 610)]
    for kind, x in up:
        y = curve_y(140, x)
        o += peg(x, y)
        o += mitten(x - 14, y + 4) if kind == "m" else hat(x - 30, y + 4, .9) if kind == "h" else scarf(x - 13, y + 4)
    low = [("h", 110), ("m", 190), ("m", 270), ("s", 350), ("h", 430), ("m", 520), ("s", 580), ("m", 630)]
    for kind, x in low:
        y = curve_y(250, x)
        o += peg(x, y)
        o += mitten(x - 14, y + 4) if kind == "m" else hat(x - 30, y + 4, .9) if kind == "h" else scarf(x - 13, y + 4)
    o += ground(395, 8)
    o += mug(300, 405, 1.2) + mug(400, 408, 1.1) + snowman(150, 440, 20) + tree(690, 440, 80)
    o += "".join(R(x, 415, 4, 28) for x in range(480, 590, 22)) + L(480, 424, 586, 424)
    for x, y in ((90, 80), (230, 90), (360, 50), (470, 100), (640, 90), (210, 200), (500, 210), (680, 200)):
        o += flake(x, y, 5)
    return o


SCENES = {
    1: dict(title="Snowy Town", art=scene1, seed=101, counts=[("treble", 2), ("bass", 2), ("quarter", 5), ("half", 4), ("whole", 3), ("qrest", 3), ("hrest", 2)],
            colors=["Red", "Blue", "Green", "Orange", "Purple", "Brown", "Pink"]),
    2: dict(title="Ice Rink", art=scene2, seed=202, counts=[("qrest", 4), ("hrest", 3), ("quarter", 3), ("repeat", 2), ("fermata", 3), ("dbl", 4), ("ts44", 2)],
            colors=["Red", "Blue", "Green", "Orange", "Purple", "Brown", "Pink"]),
    3: dict(title="Cozy Cabin", art=scene3, seed=303, counts=[("sharp", 4), ("flat", 3), ("natural", 5), ("ts44", 2), ("treble", 2), ("whole", 2), ("half", 3)],
            colors=["Red", "Blue", "Green", "Orange", "Purple", "Brown", "Pink"]),
    4: dict(title="Sledding Hill", art=scene4, seed=404, counts=[("f", 4), ("p", 3), ("mf", 2), ("mp", 3), ("cresc", 3), ("decresc", 2), ("quarter", 4), ("bass", 2)],
            colors=["Red", "Blue", "Green", "Orange", "Purple", "Brown", "Pink", "Teal"]),
    5: dict(title="Snowy Forest", art=scene5, seed=505, counts=[("treble", 3), ("bass", 1), ("fermata", 2), ("repeat", 3), ("sharp", 2), ("flat", 2), ("dbl", 3), ("hrest", 2), ("p", 2), ("whole", 2)],
            colors=["Red", "Blue", "Green", "Orange", "Purple", "Brown", "Pink", "Teal", "Yellow", "Gray"]),
    6: dict(title="Mitten Clothesline", art=scene6, seed=606, counts=[("quarter", 3), ("half", 2), ("qrest", 3), ("natural", 2), ("ts44", 3), ("f", 2), ("mf", 2), ("cresc", 2), ("decresc", 2), ("treble", 1)],
            colors=["Red", "Blue", "Green", "Orange", "Purple", "Brown", "Pink", "Teal", "Yellow", "Gray"]),
}
COLOR_HEX = {"Red": "#E03C31", "Blue": "#2F6FD0", "Green": "#2E9E4F", "Orange": "#F28C1B", "Purple": "#8450B8", "Brown": "#8B5A2B",
             "Pink": "#EE7FB0", "Teal": "#1AA6A6", "Yellow": "#F2C81B", "Gray": "#8A8A8A"}
