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
           (645, 392), (676, 312), (694, 252), (712, 222), (730, 250), (736, 330), (736, 410), (722, 500),
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
    front = U([body, head, beak, wing_n, wing_f]).buffer(14, quad_segs=16).buffer(-14, quad_segs=16)   # fillet head/wing notch
    g = U([front, tail])
    return fit(g)


# ------------------------------------------------------------------ flyer (flock unit)
def flyer():
    """Small bird seen from below, wings in a shallow gull V, short rounded body, short tail. ~700 wide.
    One closed outline; the wing roots meet in a single smooth shallow V (no head bump, no hanging spike)."""
    top = [(-352, -70, 'c'), (-262, -128), (-140, -118), (-52, -58), (0, -44),
           (52, -58), (140, -118), (262, -128), (352, -70, 'c')]
    under = [(262, -86), (150, -64), (56, -4), (34, 54), (22, 96), (0, 112), (-22, 96), (-34, 54), (-56, -4), (-150, -64), (-262, -86)]
    return shape(top + under)


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
def heron_stalks_fitted():
    """The reed/cattail stalks in the same final coordinates as d_heron()."""
    from shapely.geometry import GeometryCollection
    gc = fit(GeometryCollection([d_heron(raw=True)] + heron_stalks()), 900)
    return list(gc.geoms)[1:]


def heron_stalks():
    out = []
    for (x0, x1, top, w) in ((835, 810, 470, 26), (880, 905, 540, 24), (255, 230, 600, 26), (205, 170, 660, 24)):
        out.append(curve_taper([(x0, 910), ((x0 + x1) / 2 + 8, (910 + top) / 2), (x1, top)], w, 17))
    return out


def d_heron(raw=False):
    solid, holes = [], []
    body = ellipse(0, 0, 195, 95, 22); body = affinity.translate(body, 560, 560)
    breast = ellipse(0, 0, 100, 80, 50); breast = affinity.translate(breast, 450, 500)
    tail = shape([(660, 540, 'c'), (770, 620, 'c'), (800, 700, 'c'), (730, 690, 'c'), (640, 640, 'c')])
    neck = curve_taper([(455, 500), (395, 420), (430, 330), (372, 255), (345, 195)], 80, 42)
    head = ellipse(338, 172, 54, 34, -10)
    bill = curve_taper([(300, 168), (230, 182), (150, 200)], 30, 12)
    crest = curve_taper([(365, 160), (420, 150), (470, 168)], 20, 13)
    solid += [U([body, breast, tail, neck, head]).buffer(16, quad_segs=16).buffer(-16, quad_segs=16), bill, crest]   # fillet neck/body notches
    # legs
    solid.append(curve_taper([(580, 630), (600, 740), (590, 900)], 28, 20))
    solid.append(curve_taper([(640, 625), (665, 735), (665, 905)], 26, 20))
    # water bar
    wave = [(x, 905 + 9 * math.sin(x / 45.0)) for x in range(120, 921, 20)]
    solid.append(line(wave, 44))
    # reeds
    # stalks >= 0.10 in (>= 17 units here; 0.10 in = 15.2 units) along their whole length, round-ended
    for st in heron_stalks():
        solid.append(st)
    solid.append(ellipse(0, 0, 17, 62, 0)); solid[-1] = affinity.translate(solid[-1], 810, 440)
    solid.append(ellipse(0, 0, 15, 55, 4)); solid[-1] = affinity.translate(solid[-1], 906, 510)
    for (x, ang, L) in ((300, -80, 220), (360, -65, 190), (955, -95, 150)):
        solid.append(curve_taper([(x, 905), (x + L * 0.3 * math.cos(math.radians(ang)) , 905 + L * 0.5 * math.sin(math.radians(ang))), polar(x, 905, L, ang)], 34, 8))
    if raw:
        return U(solid).difference(U(holes))
    return fit(U(solid).difference(U(holes)), 900)


# ------------------------------------------------------------------ flock in a disc
FLOCK = ((590, 330, 0.6, -10), (330, 470, 0.5, 5), (690, 545, 0.46, -10), (480, 665, 0.42, 4),
         (250, 725, 0.36, 8), (670, 775, 0.36, -8), (335, 235, 0.36, 6))   # x, y, scale, rotation


def d_flock_disc():
    disc = circ(500, 500, 455)
    f = flyer()
    return disc.difference(U([place(f, x, y, sc, r) for x, y, sc, r in FLOCK]))


def flock_gaps():
    """(smallest gap between two bird cut-outs, smallest distance from a cut-out to the disc rim), units."""
    f = flyer(); disc = circ(500, 500, 455)
    bs = [place(f, x, y, sc, r) for x, y, sc, r in FLOCK]
    gap = min(a.distance(b) for i, a in enumerate(bs) for b in bs[i + 1:])
    return gap, min(disc.exterior.distance(a) for a in bs)


# ------------------------------------------------------------------ heron in flight
def d_heron_flight():
    solid, holes = [], []
    body = ellipse(0, 0, 170, 62, 10); body = affinity.translate(body, 520, 560)
    # neck: a smooth S that rises from the shoulder, head carried above the body line, bill forward
    neck = curve_taper([(400, 560), (335, 548), (302, 495), (308, 435), (276, 392), (250, 378)], 62, 34)
    head = ellipse(234, 372, 40, 27, 14)
    bill = curve_taper([(208, 376), (150, 398), (70, 432)], 30, 12)
    legs = U([curve_taper([(660, 580), (780, 620), (930, 640)], 26, 12),
              curve_taper([(660, 592), (770, 650), (905, 690)], 26, 12)])
    wing = curve_taper([(515, 520), (545, 360), (645, 230), (805, 150), (945, 130)], 170, 14)
    wing2 = curve_taper([(545, 560), (655, 460), (805, 400), (945, 390)], 90, 15)
    far = curve_taper([(475, 540), (435, 400), (475, 270), (565, 180)], 90, 12)
    # fillet the neck / shoulder / far-wing joins with a closing (main wing added after, so the feather slit stays open)
    crown = U([head, Point(250, 378).buffer(17)]).convex_hull   # one dome over head + neck end (no two-lobe nick)
    core = U([body, neck, head, crown, far]).buffer(30, quad_segs=24).buffer(-30, quad_segs=24)
    solid += [core, bill, legs, wing, wing2]
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
