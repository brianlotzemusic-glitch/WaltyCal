"""Christmas Village Silhouettes - 6 single-path SVG/DXF cut files.

Two wide skyline / light-box panels and four standing buildings, drawn in a
snowy, cosy, moonlit mood. Buildings, pines, moon and smoke are solid
material; windows, doors, snowflakes and icing lines are cut-outs. Every
standing piece sits on a flat base strip so it stands up when cut from 3 mm
wood or acrylic or heavy cardstock. Everything is unioned into ONE connected
polygon; smoke puffs, stars and the bell are attached, never floating.
compose() closes the solid parts by 8 units (no pinched gaps between
buildings and trees) and finish() closes then opens by 6.5 units, so there
is no material and no gap narrower than ~13 units, and fills any
hole under MIN_HOLE. Coordinates are SVG-style (y grows downward) on a
~1000 unit canvas.
Output: SVG (6 in on the longest side), DXF (inches), stats json.
"""
import math, os, json, sys
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union
from shapely import affinity, make_valid, set_precision
import ezdxf

HERE = os.path.dirname(os.path.abspath(__file__))
SVG_DIR = os.path.join(HERE, "bundle", "SVG")
DXF_DIR = os.path.join(HERE, "bundle", "DXF")
for _d in (SVG_DIR, DXF_DIR):
    os.makedirs(_d, exist_ok=True)
MIN_HOLE = 600.0
SIZE_IN = 6.0
U = unary_union


# ---------------------------------------------------------------- helpers
def poly(pts):
    return Polygon(pts).buffer(0)


def rect(x0, y0, x1, y1, r=0):
    b = box(x0, y0, x1, y1)
    return b.buffer(-r).buffer(r, 16) if r else b


def line(pts, w):
    return LineString(pts).buffer(w / 2, cap_style=1, join_style=1, quad_segs=12)


def circ(x, y, r):
    return Point(x, y).buffer(r, 48)


def polar(x, y, r, deg):
    a = math.radians(deg)
    return x + r * math.cos(a), y + r * math.sin(a)


def arch(x0, x1, y_top, y_bot):
    """Round-topped opening (door / window): half-circle on a rectangle."""
    r = (x1 - x0) / 2
    return U([circ((x0 + x1) / 2, y_top + r, r), rect(x0, y_top + r, x1, y_bot)])


def lancet(x0, x1, y_top, y_bot):
    """Pointed gothic-arch window."""
    w = x1 - x0
    r = w * 0.9
    cy = y_top + math.sqrt(r * r - (r - w / 2) ** 2)
    a = circ(x0 + r, cy, r).intersection(circ(x1 - r, cy, r))
    a = a.intersection(rect(x0, y_top - 5, x1, cy))
    return U([a, rect(x0, cy - 0.5, x1, y_bot)])


def panes(win, cx, cy, mull=16, vertical=True, horizontal=True):
    """Window opening minus a cross of glazing bars -> separate pane holes."""
    bars = []
    x0, y0, x1, y1 = win.bounds
    if vertical:
        bars.append(rect(cx - mull / 2, y0 - 5, cx + mull / 2, y1 + 5))
    if horizontal:
        bars.append(rect(x0 - 5, cy - mull / 2, x1 + 5, cy + mull / 2))
    return win.difference(U(bars))


def star(cx, cy, R, r, n=5, rot=-90):
    pts = []
    for k in range(2 * n):
        rad = R if k % 2 == 0 else r
        pts.append(polar(cx, cy, rad, rot + 180 * k / n))
    return poly(pts)


def crescent(cx, cy, R, dx, dy, k=0.86):
    return circ(cx, cy, R).difference(circ(cx + dx, cy + dy, R * k))


def snowflake(cx, cy, R, w=14, rot=90, branches=True):
    """Six-armed snowflake (used as a cut-out): round centre, arms w wide,
    each ending in a round dot."""
    parts = [circ(cx, cy, R * 0.3)]
    for k in range(6):
        a = rot + 60 * k
        parts.append(line([(cx, cy), polar(cx, cy, R * 0.82, a)], w))
        if branches:
            parts.append(circ(*polar(cx, cy, R * 0.82, a), w * 0.68))
    return U(parts)


def wavy(p0, p1, amp, wl, step=2.0):
    """Wavy line from p0 to p1 (for piped-icing cut-outs)."""
    L = math.dist(p0, p1)
    tx, ty = (p1[0] - p0[0]) / L, (p1[1] - p0[1]) / L
    nx, ny = -ty, tx
    n = max(2, int(L / step))
    out = []
    for k in range(n + 1):
        s = L * k / n
        o = amp * math.sin(2 * math.pi * s / wl)
        out.append((p0[0] + tx * s + nx * o, p0[1] + ty * s + ny * o))
    return out


def pine(cx, gy, h, w, tiers=4, trunk=None, drip=True):
    """Snowy pine standing on ground line gy: stacked tiers with drooping,
    snow-scalloped lower edges and a short trunk."""
    trunk = trunk if trunk is not None else h * 0.09
    tw = max(16, w * 0.12)
    parts = [rect(cx - tw / 2, gy - trunk - 10, cx + tw / 2, gy + 2)]
    top, yb = gy - h, gy - trunk
    ch = yb - top
    seg = ch / (tiers * 0.78 + 0.22)
    for i in range(tiers):
        apex = top + i * seg * 0.78 - (0 if i == 0 else 0)
        bot = apex + seg if i < tiers - 1 else yb
        if i == 0:
            bot = top + seg
        hw = w / 2 * (0.42 + 0.58 * (i + 1) / tiers)
        n = 16
        right = [(cx + hw * t, apex + (bot - apex) * (t ** 0.85)) for t in (k / n for k in range(1, n + 1))]
        left = [(cx - x + cx, y) for x, y in right][::-1]
        m = max(2, int(round(2 * hw / 34)))
        bottom = []
        for k in range(1, m * 12):
            t = k / (m * 12)
            x = cx + hw - 2 * hw * t
            sag = 9 * abs(math.sin(math.pi * m * t)) if drip else 0
            bottom.append((x, bot - 9 + sag))
        pts = [(cx, apex)] + right + bottom + left
        parts.append(poly(pts))
    return U(parts)


def snow_roof(l, p, r, cap=13, drips=()):
    """Gable roof (triangle l-p-r) with a rounded snow edge and snow drips."""
    g = U([poly([l, p, r]), line([l, p, r], 2 * cap)])
    for (x, y, rr) in drips:
        g = U([g, circ(x, y, rr)])
    return g


def eave_drips(l, p, r, cap, n_each=2, over=1.0):
    """Drip circles along the outer ends of both roof slopes."""
    out = []
    for a, b in ((l, p), (r, p)):
        for k in range(n_each):
            t = 0.04 + 0.11 * k * over
            x = a[0] + (b[0] - a[0]) * t
            y = a[1] + (b[1] - a[1]) * t
            out.append((x, y + cap + 3 - 3 * k, 10 - 2 * k))
    return out


def smoke(x0, y0, pts, r0=13, r1=30):
    """Chimney smoke: overlapping puffs along a curve, growing as they rise."""
    P = [(x0, y0)] + pts
    ls = LineString(P)
    n = max(3, int(ls.length / ((r0 + r1) * 0.62)))
    parts = [line(P, r0 * 1.4)]
    for k in range(n + 1):
        t = k / n
        q = ls.interpolate(ls.length * t)
        parts.append(circ(q.x, q.y, r0 + (r1 - r0) * t ** 1.1))
    return U(parts)


def base_strip(x0, x1, y0, y1, drifts=()):
    """Flat-bottomed base strip with soft snow drifts on top."""
    g = rect(x0, y0, x1, y1, r=10)
    for (cx, w, h) in drifts:
        e = affinity.scale(circ(cx, y0 + 4, 1), w / 2, h)
        g = U([g, e.intersection(rect(cx - w, y0 - h - 2, cx + w, y0 + 10))])
    return g


def areal(g):
    if g.geom_type in ("Polygon", "MultiPolygon"):
        return g
    return U([p for p in getattr(g, "geoms", []) if p.geom_type in ("Polygon", "MultiPolygon")])


def compose(solid, holes, bridge=8):
    """Union the solid parts, close them by `bridge` so that near-touching
    pieces (pine tips next to walls, eaves next to trees) are joined by a
    proper bridge instead of leaving a pinched hairline gap, then cut the
    designed openings."""
    S = U(solid).buffer(bridge, quad_segs=16).buffer(-bridge, quad_segs=16)
    return S.difference(U(holes))


def finish(g, r=6.5, simplify=0.12):
    """Close then open by r (no gaps or material under ~2r), drop small holes."""
    g = areal(make_valid(g))
    g = g.buffer(r, quad_segs=16).buffer(-r, quad_segs=16)
    g = g.buffer(-r, quad_segs=16).buffer(r, quad_segs=16)
    g = areal(set_precision(areal(make_valid(g.simplify(simplify))), 0.05))
    polys = list(g.geoms) if g.geom_type == "MultiPolygon" else [g]
    polys = [p for p in polys if p.area > 50]
    polys = [Polygon(p.exterior, [i for i in p.interiors if Polygon(i).area >= MIN_HOLE + 30]) for p in polys]
    return U(polys)


# ---------------------------------------------------------------- designs
def cottage_small(x0, x1, gy, wall_top, peak, chim=None, wins=1, door=True, eave=14):
    """Small panel cottage: walls + snowy gable roof, returns (solid, holes).
    Openings are plain arched windows and an arched door (bars would be too
    fine at panel scale)."""
    cx = (x0 + x1) / 2
    l, p, r = (x0 - eave, wall_top + 6), (cx, peak), (x1 + eave, wall_top + 6)
    solid = [rect(x0, wall_top, x1, gy + 4), snow_roof(l, p, r, 10)]
    holes = []
    if chim:
        cxh, ctop = chim
        solid += [rect(cxh - 15, ctop, cxh + 15, wall_top - 20), rect(cxh - 20, ctop - 6, cxh + 20, ctop + 10, 3)]
    w = x1 - x0
    wy0 = wall_top + 26
    if door:
        dx = cx if wins == 0 else x0 + w * 0.7
        holes.append(arch(dx - 19, dx + 19, gy - 70, gy - 12))
        xs = [] if wins == 0 else [(x0 + w * 0.3, wy0 + (76 if wins == 2 else 0))]
    else:
        xs = [(cx, wy0 + (76 if wins == 2 else 0))]
    if wins == 2:   # upper storey: a pair of windows
        xs += [(cx - 30, wy0), (cx + 30, wy0)]
    for wx, wy in xs:
        holes.append(arch(wx - 17, wx + 17, wy, wy + 50))
    if (wall_top - peak) > 70:
        holes.append(circ(cx, wall_top - (wall_top - peak) * 0.36, 18))
    return U(solid), U(holes)


def d1_village_street():
    G = 420
    solid, holes = [], []
    # snowy street: ground strip with a soft drifted top edge
    top = [(x, G - 6 * math.sin(x / 70) - 4 * math.sin(x / 23 + 1)) for x in range(0, 1001, 5)]
    solid.append(poly(top + [(1000, 478), (0, 478)]).buffer(-12).buffer(12, 16))
    # pines
    solid.append(pine(42, G, 210, 76, 3))
    solid.append(pine(316, G, 310, 94, 4))
    solid.append(pine(676, G, 250, 88, 4))
    solid.append(pine(958, G, 190, 74, 3))
    # cottage left with chimney
    s, h = cottage_small(104, 236, G, 300, 222, chim=(134, 234))
    solid.append(s); holes.append(h)
    # two-storey cottage right
    s, h = cottage_small(742, 892, G, 250, 162, chim=(857, 174), wins=2)
    solid.append(s); holes.append(h)
    # small cottage between chapel and right pine? (kept free: lamp post)
    # chapel: nave + front tower + spire + star
    nave_l, nave_r, nwt, npk = 384, 616, 290, 210
    l, p, r = (nave_l - 16, nwt + 6), (500, npk), (nave_r + 16, nwt + 6)
    solid += [rect(nave_l, nwt, nave_r, G + 4), snow_roof(l, p, r, 10)]
    solid += [rect(458, 175, 542, G + 4), rect(450, 168, 550, 184, 3)]
    solid += [rect(464, 110, 536, 176), rect(458, 104, 542, 118, 3)]
    solid.append(poly([(462, 108), (500, 26), (538, 108)]))
    solid.append(star(500, 22, 30, 13))
    holes.append(arch(482, 518, 120, 166))                 # belfry
    holes.append(circ(500, 222, 17))                        # rose window
    holes.append(arch(480, 520, G - 80, G - 12))            # door
    for x in (424, 576):
        holes.append(lancet(x - 16, x + 16, 318, 392))
    g = compose(solid, holes)
    return g


def d2_moonlit_lightbox():
    W, H, F = 1000, 620, 34
    outer = rect(0, 0, W, H, 34)
    opening = rect(F, F, W - F, H - F, 14)
    # night sky band along the top with a soft wavy lower edge
    edge = [(x, 168 + 9 * math.sin(x / 70 + 1)) for x in range(F - 10, W - F + 11, 4)]
    sky = poly([(F - 10, 0)] + edge + [(W - F + 10, 0)])
    solid = [outer.difference(opening), sky]
    holes = [crescent(814, 92, 48, -22, -10, 0.86)]
    for x, y in [(160, 96), (500, 94)]:
        holes.append(snowflake(x, y, 50))
    for x, y, r in [(76, 66, 15), (264, 64, 16), (290, 128, 15), (362, 82, 17), (420, 136, 15),
                    (612, 66, 15), (630, 132, 17), (712, 80, 15), (930, 66, 16), (916, 132, 15),
                    (76, 138, 15)]:
        holes.append(circ(x, y, r))
    G = 520
    top = [(x, G - 10 * math.sin(x / 90 + 0.5) - 5 * math.sin(x / 31)) for x in range(F - 10, W - F + 11, 5)]
    solid.append(poly(top + [(W - F + 10, H - F + 10), (F - 10, H - F + 10)]))
    # cottages
    s, h = cottage_small(150, 286, G, 400, 314, chim=(180, 326), eave=12)
    solid.append(s); holes.append(h)
    s, h = cottage_small(440, 600, G, 354, 256, chim=(563, 276), wins=2)
    solid.append(s); holes.append(h)
    s, h = cottage_small(738, 840, G, 420, 348, wins=0, eave=8)
    solid.append(s); holes.append(h)
    solid.append(smoke(180, 322, [(170, 300), (188, 278), (174, 256)], 10, 19))
    solid.append(smoke(563, 272, [(576, 250), (558, 230), (572, 210)], 10, 18))
    # pines; the tall ones reach up into the sky band
    solid.append(pine(367, G, 400, 96, 5))
    solid.append(pine(670, G, 290, 72, 4))
    solid.append(pine(906, G, 392, 80, 5))
    solid.append(pine(86, G, 250, 62, 3))
    return compose(solid, holes)


def d3_smoking_cottage():
    BY = 890
    solid, holes = [], []
    solid.append(base_strip(160, 840, BY, 940, [(300, 150, 16), (700, 170, 20)]))
    # main house
    x0, x1, wt = 280, 610, 590
    l, p, r = (246, 606), (445, 372), (644, 606)
    solid += [rect(x0, wt, x1, BY + 4), snow_roof(l, p, r, 16)]
    # lean-to on the right
    solid += [rect(600, 690, 750, BY + 4)]
    solid.append(U([poly([(596, 600), (776, 712), (596, 712)]), line([(612, 610), (776, 712)], 30)]))
    # chimney on the left slope + smoke
    solid += [rect(318, 380, 368, 520), rect(308, 368, 378, 392, 4)]
    solid.append(smoke(343, 362, [(328, 320), (354, 284), (336, 246), (362, 210), (396, 192)], 13, 28))
    # windows, gable window, two-panel door
    for wx in (352,):
        wv = rect(wx - 40, 650, wx + 40, 730, 4)
        holes.append(panes(wv, wx, 690))
    gw = circ(445, 512, 43)
    holes.append(panes(gw, 445, 512))
    holes.append(arch(462, 562, 730, BY - 22).difference(rect(504, 700, 520, 900)))
    # snow-line cuts along both roof slopes (the snow cap above them)
    keep_out = U([rect(292, 352, 394, 536), circ(*p, 46), circ(445, 512, 43 + 20), rect(570, 570, 700, 640)])
    for a in (l, r):
        ux, uy = p[0] - a[0], p[1] - a[1]
        L = math.hypot(ux, uy)
        ux, uy = ux / L, uy / L
        nx, ny = (-uy, ux) if a == l else (uy, -ux)
        if ny < 0:
            nx, ny = -nx, -ny
        s0 = (a[0] + ux * 64 + nx * 27, a[1] + uy * 64 + ny * 27)
        s1 = (a[0] + ux * (L - 10) + nx * 27, a[1] + uy * (L - 10) + ny * 27)
        ln = LineString([s0, s1]).difference(keep_out)
        for seg in (ln.geoms if hasattr(ln, "geoms") else [ln]):
            if seg.length > 50:
                holes.append(seg.buffer(8, cap_style=1))
    lw = rect(645, 760, 705, 820, 4)
    holes.append(panes(lw, 675, 790, 16, True, False))
    return compose(solid, holes)


def d4_starlit_chapel():
    BY = 890
    solid, holes = [], []
    solid.append(base_strip(130, 870, BY, 940, [(220, 160, 14), (780, 160, 14)]))
    # nave
    l, p, r = (272, 652), (500, 478), (728, 652)
    solid += [rect(300, 640, 700, BY + 4), snow_roof(l, p, r, 14, eave_drips(l, p, r, 14, 2))]
    # tower
    solid += [rect(432, 380, 568, BY + 4), rect(418, 364, 582, 390, 4)]
    solid += [rect(444, 236, 556, 372), rect(434, 226, 566, 248, 4)]
    solid.append(poly([(440, 232), (500, 92), (560, 232)]))
    solid.append(star(500, 76, 42, 18))
    # belfry with a hanging bell
    belfry = arch(461, 539, 252, 352)
    bell = U([line([(500, 250), (500, 290)], 14),
              poly([(486, 286), (514, 286), (518, 300), (522, 316), (530, 328), (470, 328), (478, 316), (482, 300)]).buffer(4),
              circ(500, 330, 8)])
    holes.append(belfry.difference(bell))
    holes.append(circ(500, 466, 30))
    holes.append(arch(456, 544, 760, BY - 22).difference(rect(492, 700, 508, 900)))
    holes.append(lancet(484, 516, 560, 650))
    for x in (360, 640):
        holes.append(lancet(x - 24, x + 24, 690, 820).difference(rect(x - 8, 600, x + 8, 900)))
    # snowy pines either side
    solid.append(pine(205, BY, 300, 150, 4))
    solid.append(pine(795, BY, 300, 150, 4))
    return compose(solid, holes)


def d5_gingerbread_house():
    BY = 890
    solid, holes = [], []
    solid.append(base_strip(110, 890, BY, 940))
    x0, x1, wt = 310, 690, 600
    solid.append(rect(x0, wt, x1, BY + 4))
    # roof with big scalloped (frosting) eaves
    l, p, r = (250, 640), (500, 336), (750, 640)
    roof = poly([l, p, r])
    roof = U([roof, line([l, p, r], 30)])
    sc = []
    for a, b in ((l, p), (r, p)):
        for k in range(7):
            t = 0.02 + 0.115 * k
            sc.append(circ(a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t + 14, 18))
    solid += [roof, U(sc)]
    # gumdrop on the peak, chimney with candy stripes
    solid.append(U([circ(500, 318, 19), rect(483, 318, 517, 336)]))
    solid += [rect(582, 380, 658, 520), rect(572, 368, 668, 394, 6)]
    # piped icing lines along both roof slopes + icing dots
    for a, b in ((l, p), (r, p)):
        ux, uy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(ux, uy)
        ux, uy = ux / L, uy / L
        nx, ny = (uy, -ux) if a == l else (-uy, ux)
        inset = 52
        s0 = (a[0] + ux * 70 - nx * inset, a[1] + uy * 70 - ny * inset)
        s1 = (a[0] + ux * (L - 150) - nx * inset, a[1] + uy * (L - 150) - ny * inset)
        holes.append(line(wavy(s0, s1, 7, 50), 16))
    # heart in the gable
    hx, hy, hs = 500, 470, 1.0
    heart = U([circ(hx - 19, hy - 8, 21), circ(hx + 19, hy - 8, 21),
               poly([(hx - 38, hy - 2), (hx + 38, hy - 2), (hx, hy + 40)])])
    holes.append(heart)
    # icing wave under the eaves
    holes.append(line(wavy((334, 668), (666, 668), 7, 48), 16))
    # peppermint windows and the door
    for wx in (385, 615):
        holes.append(panes(circ(wx, 755, 46), wx, 755))
    holes.append(arch(456, 544, 728, BY - 22))
    # lollipop on the left, iced pine on the right
    lx, ly = 178, 730
    solid.append(U([rect(lx - 9, ly + 40, lx + 9, BY + 4), circ(lx, ly, 62)]))
    sp = [(lx + (36 - 30 * t) * math.cos(2 * math.pi * 1.0 * t - 1), ly + (36 - 30 * t) * math.sin(2 * math.pi * 1.0 * t - 1))
          for t in (k / 160 for k in range(161))]
    holes.append(line(sp, 15))
    tree = pine(815, BY, 330, 140, 4, drip=True)
    solid.append(tree)
    return compose(solid, holes)


def d6_pine_cabin():
    BY = 890
    solid, holes = [], []
    solid.append(base_strip(92, 902, BY, 940, [(518, 220, 12)]))
    x0, x1, wt = 370, 650, 690
    solid.append(rect(x0, wt, x1, BY + 4))
    # log ends sticking out at the corners
    for k in range(6):
        y = wt + 20 + k * 32
        solid += [circ(x0 - 4, y, 15), circ(x1 + 4, y, 15)]
    l, p, r = (330, 702), (510, 510), (690, 702)
    solid.append(snow_roof(l, p, r, 16, eave_drips(l, p, r, 16, 2)))
    solid += [rect(590, 540, 630, 640), rect(582, 530, 638, 552, 4)]
    solid.append(smoke(610, 526, [(622, 494), (604, 462), (624, 426)], 11, 24))
    # window, door, gable vent
    wv = rect(392, 742, 472, 818, 4)
    holes.append(panes(wv, 432, 780))
    door = arch(546, 614, 750, BY - 22)
    holes.append(door)
    holes.append(circ(510, 636, 26))
    # pines all around
    solid.append(pine(198, BY, 560, 210, 5))
    solid.append(pine(790, BY, 430, 180, 4))
    return compose(solid, holes)


DESIGNS = {
    "01-village-street-skyline": d1_village_street,
    "02-moonlit-cottages-light-box": d2_moonlit_lightbox,
    "03-cottage-with-smoking-chimney": d3_smoking_cottage,
    "04-starlit-chapel": d4_starlit_chapel,
    "05-gingerbread-house": d5_gingerbread_house,
    "06-cabin-among-pines": d6_pine_cabin,
}


README = """CHRISTMAS VILLAGE SILHOUETTES - 6 SVG CUT FILES
by Duskwood Designs Co (etsy.com/shop/DuskwoodDesignsCo)
Thank you for your purchase!

DESIGNS
  Wide panels:      01 Village Street Skyline
                    02 Moonlit Cottages Light Box
  Standing pieces:  03 Cottage with Smoking Chimney
                    04 Starlit Chapel
                    05 Gingerbread House
                    06 Cabin Among Pines

FILES
  SVG/  Cricut Design Space, Silhouette Designer Edition, Inkscape, Illustrator
  DXF/  Silhouette Studio Basic Edition, laser/CNC software (inches)
  PNG/  transparent background, 1800 px on the longest side (6 in at 300 DPI)

Each design is a single-layer shape with one clean cut path. Windows, doors,
snowflakes and icing lines are cut-outs; smoke, stars and the chapel bell
are attached, so nothing falls out. Default size is 6 inches on the longest
side; resize freely, but keep the proportions locked.

SIZING TIPS
  Panels (01, 02): use them as window decals, light-box fronts, mantel or
  shelf silhouettes. The windows and snow dots are small at 6 in, so we
  recommend 10 in wide or larger for vinyl and cardstock and 12 in or larger
  for laser-cut wood. For a light box, back the panel with vellum or
  tracing paper and put a battery tea light or LED strip behind it.
  Standing pieces (03-06): each sits on a flat base strip, so it stands up
  on its own when cut from 3 mm wood or acrylic, or from heavy cardstock
  (glue two layers together for extra stiffness). We recommend 5 in tall or
  larger in wood or acrylic and 4 in or larger in cardstock. Line them up
  on a shelf or mantel to build a little village.
  The narrowest material is about 0.07 in at 6 in. Do a test cut first on a
  new material.

LICENSE
  Personal use: unlimited.
  Small-business commercial use: you may sell finished physical products
  (ornaments, gift tags, cards, decals, shirts, etc.) made with these
  designs, up to 500 units per design.
  You may NOT resell, share or redistribute the digital files themselves,
  in original or modified form, or include them in other digital products.
"""


# ---------------------------------------------------------------- export
PANELS = ("01-village-street-skyline", "02-moonlit-cottages-light-box")


def to_path(geom):
    polys = geom.geoms if geom.geom_type == "MultiPolygon" else [geom]
    d = []
    for p in polys:
        for r in [p.exterior, *p.interiors]:
            pts = list(r.coords)
            d.append("M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts[:-1]) + " Z")
    return " ".join(d)


def view_box(geom, square, pad=12):
    """(x, y, w, h): square box for standing pieces, tight box for panels."""
    x0, y0, x1, y1 = geom.bounds
    w, h = x1 - x0 + 2 * pad, y1 - y0 + 2 * pad
    if square:
        w = h = max(w, h)
    return (x0 + x1) / 2 - w / 2, (y0 + y1) / 2 - h / 2, w, h


def write_dxf(geom, path, vb):
    bx, by, w, h = vb
    k = SIZE_IN / max(w, h)
    doc = ezdxf.new("R2010")
    doc.header["$INSUNITS"] = 1
    doc.header["$MEASUREMENT"] = 0
    msp = doc.modelspace()
    polys = geom.geoms if geom.geom_type == "MultiPolygon" else [geom]
    for p in polys:
        for r in [p.exterior, *p.interiors]:
            msp.add_lwpolyline([((x - bx) * k, (h - (y - by)) * k) for x, y in list(r.coords)[:-1]], close=True)
    doc.saveas(path)


def stats(g):
    polys = list(g.geoms) if g.geom_type == "MultiPolygon" else [g]
    hs = [Polygon(i).area for p in polys for i in p.interiors]
    return {"parts": len(polys), "holes": len(hs), "smallest_hole": round(min(hs or [0]), 1), "valid": g.is_valid}


if __name__ == "__main__":
    only = sys.argv[1:]
    meta = {}
    for name, fn in DESIGNS.items():
        if only and not any(o in name for o in only):
            continue
        g = finish(fn())
        vb = view_box(g, name not in PANELS)
        k = SIZE_IN / max(vb[2], vb[3])
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb[0]:.1f} {vb[1]:.1f} {vb[2]:.1f} {vb[3]:.1f}" '
               f'width="{vb[2] * k:.3f}in" height="{vb[3] * k:.3f}in"><path fill="#000" fill-rule="evenodd" d="{to_path(g)}"/></svg>')
        with open(os.path.join(SVG_DIR, f"{name}.svg"), "w") as f:
            f.write(svg)
        write_dxf(g, os.path.join(DXF_DIR, f"{name}.dxf"), vb)
        meta[name] = stats(g)
    with open(os.path.join(HERE, "bundle", "README-LICENSE.txt"), "w") as f:
        f.write(README)
    print(json.dumps(meta, indent=1))
