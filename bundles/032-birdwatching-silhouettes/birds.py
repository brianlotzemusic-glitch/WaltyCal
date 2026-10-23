"""Birdwatching silhouettes - six single-path cut files drawn in code ($0 AI).
Canvas 1000 x 1000 (y down). Every design is unioned into ONE piece."""
from lib import *


def leaf(x, y, ang, L, W):
    """Pointed leaf from base (x,y) pointing at angle ang (deg, screen coords)."""
    pts = [(0, 0, 'c'), (L*0.3, -W*0.55), (L*0.7, -W*0.38), (L, 0, 'c'), (L*0.7, W*0.38), (L*0.3, W*0.55)]
    g = shape(pts)
    return affinity.translate(affinity.rotate(g, ang, origin=(0, 0)), x, y)


def eye(x, y, r=17):
    return circ(x, y, r)


# ------------------------------------------------------------------ wren
def wren_bird():
    pts = [(222, 436, 'c'), (270, 424), (312, 396), (372, 378), (440, 384), (520, 400), (600, 405),
           (645, 392), (678, 310), (696, 232, 'c'), (726, 240, 'c'), (734, 320), (736, 410), (722, 500),
           (690, 575), (620, 635), (530, 668), (440, 656), (368, 606), (322, 540), (292, 486), (262, 452)]
    return shape(pts)


def d_wren():
    solid, holes = [wren_bird()], [eye(342, 436, 17)]
    # legs and feet gripping the branch
    solid.append(line([(500, 640), (498, 770)], 20))
    solid.append(line([(570, 625), (574, 765)], 20))
    # branch with twig and leaves
    solid.append(curve_taper([(110, 835), (330, 800), (560, 785), (800, 750), (910, 700)], 46, 24))
    solid.append(curve_taper([(780, 758), (830, 640), (880, 570)], 22, 12))
    solid.append(curve_taper([(250, 815), (200, 880), (150, 925)], 22, 12))
    for a, x, y in ((-70, 880, 575), (-20, 862, 600), (-125, 876, 580)):
        solid.append(leaf(x, y, a, 130, 56))
    for a, x, y in ((60, 160, 920), (110, 152, 922), (20, 164, 918)):
        solid.append(leaf(x, y, a, 110, 50))
    solid.append(leaf(640, 780, -60, 110, 48))
    # two berries
    return fit(U(solid).difference(U(holes)), 900)


# ------------------------------------------------------------------ swallow
def d_swallow():
    # side view, flying left, wings swept back; head at left
    body = shape([(-190, 8, 'c'), (-165, -18), (-120, -38), (-50, -44), (40, -36), (120, -14), (190, 8),
                  (120, 28), (30, 48), (-50, 52), (-120, 44), (-168, 28)])
    head = circ(-150, -2, 36)
    beak = Polygon([(-176, -14), (-232, 4), (-170, 20)])
    # long forked tail
    tail = U([curve_taper([(120, 6), (260, 40), (390, 78)], 30, 10),
              curve_taper([(120, 8), (265, 4), (400, 14)], 30, 10)])
    wing_n = curve_taper([(-70, -30), (-10, -130), (110, -230), (260, -300)], 110, 8)
    wing_f = curve_taper([(-40, 20), (60, 90), (190, 130), (310, 130)], 70, 8)
    g = U([body, head, beak, tail, wing_n, wing_f])
    return fit(g)


# ------------------------------------------------------------------ flyer (flock unit)
def flyer():
    """Small bird seen from in front/below, wings spread in a shallow V. ~ 700 units wide."""
    body = U([ellipse(0, 6, 34, 66, 0), circ(0, -62, 30), Polygon([(-26, -66), (0, -112), (26, -66)])])
    tail = Polygon([(-24, 50), (0, 150), (24, 50)])
    wl = curve_taper([(-10, -10), (-110, -105), (-240, -135), (-350, -75)], 62, 8)
    wr = curve_taper([(10, -10), (110, -105), (240, -135), (350, -75)], 62, 8)
    return U([body, tail, wl, wr])


# ------------------------------------------------------------------ hummingbird
def d_hummingbird():
    solid, holes = [], []
    body = ellipse(0, 0, 135, 58, 42)
    body = affinity.translate(body, 530, 470)
    head = circ(425, 365, 50)
    bill = curve_taper([(395, 372), (300, 420), (200, 462)], 24, 12)
    throat = ellipse(470, 420, 60, 40, 40)
    tail = place(shape([(-20, -26, 'c'), (150, -62, 'c'), (125, -30, 'c'), (172, 0, 'c'), (125, 30, 'c'), (150, 62, 'c'), (-20, 26, 'c')]), 585, 548, 1.0, 62)
    wing = curve_taper([(500, 430), (580, 300), (700, 220), (830, 190)], 92, 8)
    wing2 = curve_taper([(520, 440), (640, 380), (760, 360), (870, 380)], 64, 8)
    solid += [body, head, bill, throat, tail, wing, wing2]
    holes.append(circ(418, 352, 14))
    # flower: five petals around a centre, with stem and leaves
    fx, fy = 165, 478
    for k in range(5):
        a = -90 + 72 * k + 20
        px, py = polar(fx, fy, 78, a)
        solid.append(ellipse(0, 0, 88, 52, a)); solid[-1] = affinity.translate(solid[-1], px, py)
    solid.append(circ(fx, fy, 50))
    solid.append(curve_taper([(fx - 10, fy + 80), (130, 650), (170, 800), (260, 930)], 30, 22))
    solid.append(leaf(150, 735, 195, 190, 70))
    solid.append(leaf(180, 800, -20, 200, 74))
    g = U(solid)
    return fit(g.difference(U(holes)), 900)


# ------------------------------------------------------------------ heron
def d_heron():
    solid, holes = [], []
    body = ellipse(0, 0, 195, 95, 22); body = affinity.translate(body, 560, 560)
    breast = ellipse(0, 0, 100, 80, 50); breast = affinity.translate(breast, 450, 500)
    tail = shape([(660, 540, 'c'), (770, 620, 'c'), (800, 700, 'c'), (730, 690, 'c'), (640, 640, 'c')])
    neck = curve_taper([(455, 500), (395, 420), (430, 330), (372, 255), (345, 195)], 80, 42)
    head = ellipse(338, 172, 54, 34, -10)
    bill = curve_taper([(300, 168), (230, 182), (150, 200)], 30, 12)
    crest = curve_taper([(365, 160), (420, 150), (470, 168)], 20, 13)
    solid += [body, breast, tail, neck, head, bill, crest]
    # legs
    solid.append(curve_taper([(580, 630), (600, 740), (590, 900)], 28, 20))
    solid.append(curve_taper([(640, 625), (665, 735), (665, 905)], 26, 20))
    # water bar
    wave = [(x, 905 + 9 * math.sin(x / 45.0)) for x in range(120, 921, 20)]
    solid.append(line(wave, 44))
    # reeds
    for (x0, x1, top, w) in ((835, 810, 470, 20), (880, 905, 540, 18), (255, 230, 600, 20), (205, 170, 660, 18)):
        solid.append(curve_taper([(x0, 910), ((x0 + x1) / 2 + 8, (910 + top) / 2), (x1, top)], w, w * 0.6))
    solid.append(ellipse(0, 0, 17, 62, 0)); solid[-1] = affinity.translate(solid[-1], 810, 440)
    solid.append(ellipse(0, 0, 15, 55, 4)); solid[-1] = affinity.translate(solid[-1], 906, 510)
    for (x, ang, L) in ((300, -80, 220), (360, -65, 190), (955, -95, 150)):
        solid.append(curve_taper([(x, 905), (x + L * 0.3 * math.cos(math.radians(ang)) , 905 + L * 0.5 * math.sin(math.radians(ang))), polar(x, 905, L, ang)], 34, 8))
    return fit(U(solid).difference(U(holes)), 900)


# ------------------------------------------------------------------ flock in a disc
def d_flock_disc():
    disc = circ(500, 500, 455)
    birds = []
    # V formation heading up-right; (dx, dy) trail behind the leader
    f = flyer()
    holes = []
    # (x, y, scale, rotation) hand placed: a loose V heading up-right
    for x, y, sc, r in ((570, 340, 0.72, -10), (300, 440, 0.58, 6), (730, 520, 0.52, -14),
                        (480, 610, 0.5, 4), (260, 650, 0.34, 10), (640, 730, 0.36, -8),
                        (400, 760, 0.3, 8), (720, 250, 0.34, -18), (330, 250, 0.32, 8)):
        holes.append(place(f, x, y, sc, r).buffer(16).buffer(-16).buffer(-3).buffer(3))
    return disc.difference(U(holes))


# ------------------------------------------------------------------ heron in flight
def d_heron_flight():
    solid, holes = [], []
    body = ellipse(0, 0, 170, 62, 10); body = affinity.translate(body, 520, 560)
    neck = curve_taper([(380, 540), (320, 560), (290, 520), (255, 500)], 64, 40)
    head = ellipse(238, 492, 40, 28, 8)
    bill = curve_taper([(210, 492), (150, 505), (70, 528)], 30, 12)
    legs = U([curve_taper([(660, 580), (780, 620), (930, 640)], 26, 12),
              curve_taper([(660, 592), (770, 650), (905, 690)], 26, 12)])
    wing = curve_taper([(470, 520), (500, 360), (600, 230), (760, 150), (900, 130)], 170, 14)
    wing2 = curve_taper([(500, 560), (610, 460), (760, 400), (900, 390)], 90, 12)
    far = curve_taper([(430, 540), (390, 400), (430, 270), (520, 180)], 100, 12)
    solid += [body, neck, head, bill, legs, wing, wing2, far]
    holes.append(circ(230, 486, 12))
    return fit(U(solid).difference(U(holes)), 900)


# ------------------------------------------------------------------ swallows on a wire
def perched_swallow():
    """Perched swallow facing left; feet at (0, 0). Forked tail trails to the right."""
    body = ellipse(0, 0, 112, 50, 16); body = affinity.translate(body, 10, -88)
    head = circ(-84, -112, 38)
    beak = Polygon([(-110, -126), (-164, -108), (-110, -96)])
    tail = U([curve_taper([(95, -70), (200, -48), (340, -18)], 40, 12),
              curve_taper([(95, -62), (190, -30), (300, 24)], 38, 12)])
    legs = U([line([(-12, -50), (-12, 0)], 18), line([(34, -50), (34, 0)], 18)])
    return U([body, head, beak, tail, legs])


def d_swallows_wire():
    f = perched_swallow()
    solid = []
    wire = [(x, 520 + 60 * math.sin(math.pi * x / 1000.0)) for x in range(0, 1001, 25)]
    solid.append(line(wire, 24))
    for x, sc, fl in ((130, 0.92, False), (480, 1.0, False), (800, 0.86, False)):
        y = 520 + 60 * math.sin(math.pi * x / 1000.0) - 4
        solid.append(place(f, x, y, sc, 0))
    return fit(U(solid), 900)
