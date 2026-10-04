"""Woodland Christmas mini ornaments: the 12 cross-stitch motifs, drawn in code as pixel grids.

  python3 motifs.py           # writes motifs.json + contact-sheet.png
  python3 motifs.py --check   # re-checks motifs.json (sizes, palette, symbols, no stray stitches)

Each motif is painted on a small canvas with a tiny DSL (ellipses, polygons, lines, single cells),
mirrored where the subject is symmetrical, cropped, and given a one-stitch 3371 outline
(4-neighbour, so corners round off). Letters map to the shared DMC palette below.

One-colour version (3371 only), derived from the colour grid:
  - every outline cell and every fill cell is stitched,
  - "light" letters (per motif, default cream 712) become unstitched negative space,
  - interior 3371 details (eyes, nose, wing lines) become gaps too, except where they sit
    next to a light gap (a pupil inside a cream eye stays stitched).
"""
import json, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))

# Shared palette: letter -> (DMC number, DMC name, screen hex, chart symbol id)
PALETTE = {
    "K": ("3371", "Black Brown", "#1e1108", "dot"),
    "P": ("550", "Violet Very Dark", "#5c184e", "diamond"),
    "G": ("500", "Blue Green Very Dark", "#0b4d36", "tri"),
    "L": ("3363", "Pine Green Medium", "#728256", "otri"),
    "R": ("815", "Garnet Medium", "#87071f", "cross"),
    "C": ("920", "Copper Medium", "#a9583a", "ocircle"),
    "Y": ("729", "Old Gold Medium", "#d0a53e", "star"),
    "W": ("712", "Cream", "#f4ead0", "osquare"),
    "B": ("433", "Brown Medium", "#7a451f", "hsquare"),
    "T": ("436", "Tan", "#cb9051", "odiamond"),
}
MONO = ("3371", "Black Brown", "#1e1108", "cross")
STITCHES_PER_SKEIN = 1600  # full crosses, 2 strands on 14-count (8 m skein); conservative


class Canvas:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.g = [["." for _ in range(w)] for _ in range(h)]

    def _paint(self, test, col, only=None):
        for y in range(self.h):
            for x in range(self.w):
                if test(x + 0.5, y + 0.5) and (only is None or self.g[y][x] in only):
                    self.g[y][x] = col

    def ellipse(self, cx, cy, rx, ry, col, only=None, cut=None):
        def t(x, y):
            return ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1 and (cut is None or cut(x, y))
        self._paint(t, col, only)

    def poly(self, pts, col, only=None):
        def t(x, y):
            inside = False
            n = len(pts)
            for i in range(n):
                (x1, y1), (x2, y2) = pts[i], pts[(i + 1) % n]
                if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1):
                    inside = not inside
            return inside
        self._paint(t, col, only)

    def rect(self, x0, y0, x1, y1, col, only=None):  # cell coords, inclusive
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                if only is None or self.g[y][x] in only:
                    self.g[y][x] = col

    def cells(self, pts, col):
        for x, y in pts:
            self.g[y][x] = col

    def line(self, x0, y0, x1, y1, col):  # Bresenham, cell coords
        dx, dy = abs(x1 - x0), -abs(y1 - y0)
        sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
        err = dx + dy
        while True:
            self.g[y0][x0] = col
            if (x0, y0) == (x1, y1):
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy; x0 += sx
            if e2 <= dx:
                err += dx; y0 += sy

    def ascii(self, x, y, rows):  # '.' is transparent
        for j, r in enumerate(rows):
            for i, ch in enumerate(r):
                if ch != ".":
                    self.g[y + j][x + i] = ch

    def mirror(self):  # copy the left half onto the right
        for row in self.g:
            for x in range(self.w // 2):
                row[self.w - 1 - x] = row[x]

    def result(self, outline=True):
        g = [r[:] for r in self.g]
        ys = [y for y in range(self.h) if any(c != "." for c in g[y])]
        xs = [x for x in range(self.w) if any(g[y][x] != "." for y in range(self.h))]
        g = [r[min(xs):max(xs) + 1] for r in g[min(ys):max(ys) + 1]]
        if outline:
            g = [["."] + r + ["."] for r in g]
            g = [["."] * len(g[0])] + g + [["."] * len(g[0])]
            H, W = len(g), len(g[0])
            out = [r[:] for r in g]
            for y in range(H):
                for x in range(W):
                    if g[y][x] == "." and any(0 <= y + dy < H and 0 <= x + dx < W and g[y + dy][x + dx] != "."
                                              for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                        out[y][x] = "K"
            g = out
        return ["".join(r) for r in g]


def star5(c, cx, cy, R, col, r_ratio=0.45, rot=-90):
    pts = []
    for i in range(10):
        a = math.radians(rot + i * 36)
        rr = R if i % 2 == 0 else R * r_ratio
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    c.poly(pts, col)


# ---------------------------------------------------------------- motifs
def fox():
    c = Canvas(30, 34)
    # tail first (behind the body), curling up the right side, cream tip
    c.ellipse(21.6, 25.6, 4.4, 7.4, "C")
    c.ellipse(22.2, 19.6, 3.0, 2.4, "W", only="C")
    # body + cream chest
    c.ellipse(12, 25.6, 7.6, 8.0, "C", cut=lambda x, y: y < 33.2)
    c.ellipse(12, 22.8, 3.6, 7.6, "W", only="C", cut=lambda x, y: y < 31)
    # paws
    c.rect(8, 31, 10, 32, "K"); c.rect(13, 31, 15, 32, "K")
    # head
    c.ellipse(12, 9.8, 9.4, 6.4, "C")
    c.poly([(2.8, 9.5), (21.2, 9.5), (12, 19.4)], "C")
    # ears: dark tips, cream inside
    c.poly([(3.6, 8.5), (4.6, 0.2), (10.4, 5.2)], "C")
    c.poly([(4.6, 0.2), (5.2, 3.0), (3.9, 3.4)], "K")
    c.poly([(5.0, 7.6), (5.6, 3.8), (8.6, 5.9)], "W")
    # cream cheeks with a copper stripe down the nose
    c.poly([(2.6, 10.6), (21.4, 10.6), (12, 19.6)], "W", only="C")
    c.poly([(9.2, 9.0), (14.8, 9.0), (12, 17.2)], "C", only="W")
    c.mirror_rows = None
    # mirror only the head area (rows 0-19); the tail stays on the right
    for y in range(0, 20):
        for x in range(12):
            c.g[y][23 - x] = c.g[y][x]
    c.rect(11, 15, 12, 16, "K")              # nose
    c.cells([(7, 9), (7, 10), (16, 9), (16, 10)], "K")  # eyes
    return c.result(), {"light": "W"}


def owl():
    c = Canvas(26, 31)
    c.ellipse(13, 17, 10.4, 12.6, "B")
    c.poly([(3.3, 9.5), (4.4, 1.0), (10.4, 6.0)], "B")           # ear tufts
    c.ellipse(13, 22.2, 6.4, 6.4, "T", only="B")                # belly
    c.ellipse(8.8, 11.6, 3.9, 3.9, "W")                          # facial discs
    c.ellipse(8.8, 11.6, 2.5, 2.5, "Y")                          # iris
    c.rect(8, 11, 9, 12, "K")                                    # pupil
    c.mirror()
    c.poly([(11.4, 13.0), (14.6, 13.0), (13, 16.6)], "Y")        # beak
    for (x, y) in [(10, 19), (15, 19), (12, 22), (13, 22), (9, 23), (16, 23), (11, 25), (14, 25)]:
        c.cells([(x, y), (x + (1 if x < 13 else -1), y - 1)], "B")  # feather chevrons
    # pine branch under the feet
    c.rect(0, 29, 25, 29, "G")
    c.cells([(1, 28), (4, 28), (21, 28), (24, 28), (2, 30), (6, 30), (19, 30), (23, 30)], "G")
    c.cells([(9, 28), (11, 28), (14, 28), (16, 28)], "Y")        # toes
    return c.result(), {"light": "WY"}


def stag():
    c = Canvas(30, 32)
    A = "T"
    segs = [((11, 14), (9, 11)), ((9, 11), (6, 7)), ((6, 7), (4, 3)), ((4, 3), (3, 0)),
            ((9, 11), (11, 6)), ((11, 6), (11, 3)), ((6, 7), (7, 3)), ((7, 3), (7, 1)), ((4, 3), (1, 2))]
    for (p, q) in segs:
        c.line(*p, *q, A)
        c.line(p[0] + 1, p[1], q[0] + 1, q[1], A)                # two stitches thick
    c.ellipse(15, 19.2, 6.4, 5.6, "B")                           # head
    c.poly([(9.6, 19), (20.4, 19), (18.4, 29.6), (11.6, 29.6)], "B")
    c.ellipse(15, 27.2, 3.6, 3.2, "T", only="B")                 # muzzle
    c.poly([(9.8, 16.2), (3.2, 13.8), (2.6, 15.6), (9.2, 19.4)], "B")   # ear
    c.poly([(8.6, 16.6), (4.4, 15.0), (4.2, 15.6), (8.4, 18.2)], "T")
    c.cells([(11, 20), (11, 21)], "K")                           # eye
    c.mirror()
    c.rect(14, 26, 15, 27, "K")                                  # nose
    return c.result(), {"light": "WR"}


def robin():
    c = Canvas(31, 30)
    c.poly([(21, 10), (28.6, 5.4), (30.0, 8.4), (24, 15)], "B")   # tail
    c.ellipse(15, 13, 10.6, 9.6, "B")                             # body
    c.ellipse(10.6, 14.4, 7.2, 6.8, "C", only="B")                # breast
    c.ellipse(15.6, 20.6, 7.6, 3.8, "W", only="BC")               # belly
    for x, y in [(17, 9), (18, 10), (19, 11), (20, 12), (21, 13), (21, 14), (20, 15), (19, 15)]:
        c.g[y][x] = "K"                                           # wing line
    c.cells([(8, 9), (8, 8)], "K")                                # eye
    c.cells([(2, 11), (3, 11), (4, 11), (3, 12), (4, 12)], "K")   # beak
    c.cells([(13, 23), (13, 24), (17, 23), (17, 24)], "K")        # legs
    # holly sprig perch
    c.rect(3, 25, 28, 25, "B")
    c.poly([(10.5, 25.8), (5.5, 25.6), (1.6, 29.2), (6.6, 28.6)], "G")
    c.poly([(19.5, 25.8), (24.5, 25.6), (28.4, 29.2), (23.4, 28.6)], "G")
    c.ellipse(13.4, 27.8, 1.8, 1.8, "R"); c.ellipse(16.6, 27.8, 1.8, 1.8, "R")
    return c.result(), {"light": "W", "split": "CB"}


def mushroom():
    c = Canvas(28, 29)
    c.ellipse(14, 13.6, 13.4, 11.6, "R", cut=lambda x, y: y < 13.6)   # cap
    c.rect(2, 13, 25, 14, "T")                                         # gills
    c.poly([(10, 14.6), (18, 14.6), (19.4, 26.2), (8.6, 26.2)], "W")  # stem
    for cx, cy, r in [(8.0, 8.4, 1.9), (14, 4.6, 2.0), (14, 10.4, 1.5), (3.6, 11.6, 1.1)]:
        c.ellipse(cx, cy, r, r, "W", only="R")
    c.mirror()
    c.rect(2, 25, 25, 26, "G")                                         # grass
    c.cells([(3, 24), (5, 23), (5, 24), (7, 24), (20, 24), (22, 23), (22, 24), (24, 24)], "G")
    c.cells([(4, 24), (6, 22), (21, 22), (23, 24)], "L")
    return c.result(), {"light": "W"}


def pine():
    c = Canvas(29, 34)
    star5(c, 14.5, 3.4, 3.4, "Y")
    tiers = [(6.0, 13.5, 4.0), (10.0, 20.5, 6.0), (15.0, 28.0, 8.0)]  # top y, bottom y, half width below
    for i, (top, bot, hw) in enumerate(tiers):
        w = hw + 3.0 * i + 3.5
        c.poly([(14.5, top), (14.5 + w, bot), (14.5 - w, bot)], "G")
    c.rect(13, 28, 15, 31, "B")                                       # trunk
    # light green highlights on the left of each tier
    c.poly([(14.5, 7.4), (10.4, 13.0), (12.6, 13.0)], "L")
    c.poly([(13.6, 13.0), (7.4, 20.0), (10.0, 20.0)], "L", only="G")
    c.poly([(13.2, 19.4), (4.2, 27.6), (7.2, 27.6)], "L", only="G")
    # berry baubles
    for x, y in [(17, 11), (11, 17), (19, 18), (9, 25), (15, 24), (21, 25)]:
        c.rect(x, y, x + 1, y + 1, "R")
    return c.result(), {"light": "R"}


def moon():
    c = Canvas(30, 30)
    c.ellipse(13.0, 15.0, 12.6, 12.6, "Y")
    c.ellipse(19.6, 12.6, 10.4, 10.8, ".", only="Y")
    # tidy the inner curve into a soft profile: nose bump
    c.cells([(9, 16), (10, 16), (9, 17)], "Y")
    c.cells([(6, 12), (7, 13), (8, 13)], "K")                        # sleepy closed eye
    c.cells([(6, 18), (7, 18)], "R")                                 # cheek
    star5(c, 24.4, 20.6, 4.6, "P")
    c.cells([(23, 3), (23, 4), (23, 5), (23, 6), (23, 7), (21, 5), (22, 5), (24, 5), (25, 5)], "P")
    return c.result(), {"light": "WR"}


def holly():
    c = Canvas(31, 30)
    def leaf(base, tip, half, col):
        bx, by = base; tx, ty = tip
        L = math.hypot(tx - bx, ty - by); ux, uy = (tx - bx) / L, (ty - by) / L; nx, ny = -uy, ux
        left, right = [], []
        steps = 7
        for i in range(steps + 1):
            t = i / steps
            wv = half * math.sin(math.pi * t) ** 0.8
            wv = wv * (1.25 if i % 2 == 1 else 0.82)
            px, py = bx + ux * L * t, by + uy * L * t
            left.append((px + nx * wv, py + ny * wv)); right.append((px - nx * wv, py - ny * wv))
        c.poly(left + right[::-1], col)
        return (bx, by, tx, ty)
    bx, by, tx, ty = leaf((14.0, 13.0), (1.2, 26.5), 5.0, "G")
    c.line(13, 14, 4, 24, "L")                                       # midrib
    c.mirror()
    c.poly([(15.5, 12), (15.5, 0.4), (25.0, 2.0), (17.5, 12)], ".")  # keep the top clear
    for cx, cy in [(12.4, 9.6), (18.6, 9.6), (15.5, 5.4)]:
        c.ellipse(cx, cy, 3.0, 3.0, "R")
    c.cells([(11, 8), (17, 8), (14, 4)], "W")                         # berry highlights
    return c.result(), {"light": "WL"}


def snowflake():
    N = 29; c = Canvas(N, N); o = 14
    pts = {}
    def put(dx, dy, col):
        for a, b in {(dx, dy), (dy, dx)}:
            for sx in (1, -1):
                for sy in (1, -1):
                    pts[(o + sx * a, o + sy * b)] = col
    for d in range(0, 12):
        put(d, 0, "P")                                   # axis arms
    for d in range(1, 9):
        put(d, d, "P")                                   # diagonal arms
    for k in (1, 2, 3):
        put(5 + k, k, "P")                               # axis branches (V)
    for k in (1, 2):
        put(9 + k, k, "P")
    for k in (1, 2):
        put(5 + k, 5, "P")                               # diagonal branches
    put(12, 0, "Y"); put(13, 0, "Y"); put(12, 1, "Y")    # axis tips: small diamond
    put(14, 0, "Y")
    put(9, 9, "Y"); put(10, 10, "Y"); put(10, 9, "Y")    # diagonal tips
    put(0, 0, "R"); put(1, 0, "R"); put(1, 1, "R")       # berry centre
    for (x, y), col in pts.items():
        c.g[y][x] = col
    return c.result(outline=False), {"light": ""}


def lantern():
    c = Canvas(27, 34)
    c.ellipse(13.5, 3.2, 3.8, 3.4, "P"); c.ellipse(13.5, 3.2, 2.0, 1.7, ".", only="P")   # ring
    c.poly([(13.5, 5.0), (24.0, 11.6), (3.0, 11.6)], "P")                                   # roof
    c.rect(2, 11, 24, 11, "P")
    c.rect(4, 12, 22, 27, "P")                                                              # frame
    c.rect(6, 13, 12, 26, "Y"); c.rect(14, 13, 20, 26, "Y")                                 # glowing panes
    c.rect(9, 19, 17, 25, "Y")
    c.rect(12, 19, 14, 26, "W")                                                             # candle
    c.cells([(13, 15), (13, 16), (12, 17), (13, 17), (14, 17), (13, 18)], "C")              # flame
    c.rect(2, 28, 24, 29, "P")                                                              # base
    c.rect(4, 30, 22, 30, "P")
    c.cells([(15, 7), (16, 7), (17, 8), (18, 8), (17, 7), (16, 6), (19, 9), (15, 6), (20, 8), (18, 7), (19, 8)], "G")
    return c.result(), {"light": "Y"}


def cottage():
    c = Canvas(32, 30)
    c.rect(21, 3, 24, 10, "R")                                    # chimney
    c.rect(20, 2, 25, 2, "W")                                     # snow on chimney
    c.poly([(16, 1.6), (31.2, 13.6), (0.8, 13.6)], "R")          # roof
    c.poly([(16, 1.6), (31.2, 13.6), (29.0, 13.6), (16, 3.6), (3.0, 13.6), (0.8, 13.6)], "W")  # snow edge
    c.rect(4, 14, 27, 27, "T")                                    # walls
    c.rect(13, 19, 18, 27, "P")                                   # door
    c.cells([(17, 23)], "Y")                                      # door knob
    for x0 in (6, 21):
        c.rect(x0, 17, x0 + 4, 22, "Y")                          # windows
        c.rect(x0 + 2, 17, x0 + 2, 22, "K"); c.rect(x0, 19, x0 + 4, 19, "K")
    c.rect(13, 9, 18, 12, "Y"); c.rect(15, 9, 16, 12, "K")       # attic window
    c.cells([(15, 9), (16, 9)], "Y")
    c.rect(1, 28, 30, 28, "W")                                    # snow on the ground
    c.ellipse(16, 29.6, 15.4, 1.8, "W")
    return c.result(), {"light": "WY"}


def acorn():
    c = Canvas(31, 33)
    # one oak leaf behind, rising to the upper right from the stem
    for t, r in [(0.18, 2.3), (0.38, 3.0), (0.58, 3.1), (0.78, 2.6), (0.95, 1.7)]:
        x, y = 15.0 + t * 13.5, 9.0 - t * 8.0
        c.ellipse(x, y, r, r, "G")
    c.poly([(15.0, 9.4), (21.0, 3.0), (27.0, 0.6), (24.0, 6.4)], "G")
    c.line(15, 9, 28, 1, "L")                                                   # midrib
    c.cells([(19, 5), (19, 4), (22, 4), (22, 3), (24, 2), (25, 2)], "L")        # side veins
    # nut, cap, stem
    c.ellipse(13.5, 20.4, 7.6, 9.6, "C", cut=lambda x, y: y > 15.0)
    c.ellipse(13.5, 15.0, 9.8, 6.0, "B", cut=lambda x, y: y < 17.0)
    c.rect(12, 5, 14, 9, "B")                                                   # stem
    for y in range(9, 17):                                                      # crosshatch on the cap
        for x in range(c.w):
            if c.g[y][x] == "B" and y > 9 and ((x + y) % 4 == 0 or (x - y) % 4 == 0) and 4 < x < 23:
                c.g[y][x] = "T"
    for x in range(c.w):                                                        # dark rim under the cap
        if c.g[17][x] == "C" and c.g[16][x] in "BT":
            c.g[17][x] = "K"
    c.cells([(9, 20), (9, 21), (9, 22), (10, 23)], "T")                         # highlight on the nut
    # dark line where the leaf meets the stem and cap
    snap = [r[:] for r in c.g]
    for y in range(c.h):
        for x in range(c.w):
            if snap[y][x] in "GL" and any(0 <= y + dy < c.h and 0 <= x + dx < c.w and snap[y + dy][x + dx] in "BT"
                                          for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                c.g[y][x] = "K"
    return c.result(), {"light": "TL"}


MOTIFS = [
    ("fox", "Little Fox", fox), ("owl", "Wise Owl", owl), ("stag", "Woodland Stag", stag),
    ("robin", "Robin on Holly", robin), ("mushroom", "Toadstool", mushroom), ("pine", "Little Pine", pine),
    ("moon", "Moon & Star", moon), ("holly", "Holly Sprig", holly), ("snowflake", "Snowflake", snowflake),
    ("lantern", "Lantern", lantern), ("cottage", "Snowy Cottage", cottage), ("acorn", "Acorn & Oak", acorn),
]


def mono_of(rows, light, split=None):
    H, W = len(rows), len(rows[0])
    g = [list(r) for r in rows]
    def at(x, y):
        return g[y][x] if 0 <= x < W and 0 <= y < H else "."
    # exterior: flood fill of empty cells from the border
    ext = set(); stack = [(x, y) for x in range(W) for y in (0, H - 1)] + [(x, y) for y in range(H) for x in (0, W - 1)]
    while stack:
        x, y = stack.pop()
        if (x, y) in ext or not (0 <= x < W and 0 <= y < H) or g[y][x] != ".":
            continue
        ext.add((x, y)); stack += [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
    def touches_ext(x, y):
        return any((x + dx, y + dy) in ext or not (0 <= x + dx < W and 0 <= y + dy < H)
                   for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
    out = []
    for y in range(H):
        r = ""
        for x in range(W):
            ch = g[y][x]
            if ch == ".":
                r += "."
            elif ch in light:
                r += "."
            elif ch == "K" and not touches_ext(x, y):
                near_light = any(at(x + dx, y + dy) in light for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)) if at(x + dx, y + dy) != ".")
                near_outline = any(at(x + dx, y + dy) == "K" and touches_ext(x + dx, y + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
                r += "X" if near_light or near_outline else "."
            elif split and ch == split[0] and any(at(x + dx, y + dy) == split[1] for dx, dy in ((1, 0), (0, -1))):
                r += "."
            else:
                r += "X"
        out.append(r)
    return out


def parts(rows, big=0):
    """8-connected parts of stitched cells; returns sizes."""
    H, W = len(rows), len(rows[0]); seen = set(); sizes = []
    for y in range(H):
        for x in range(W):
            if rows[y][x] != "." and (x, y) not in seen:
                st = [(x, y)]; seen.add((x, y)); n = 0
                while st:
                    a, b = st.pop(); n += 1
                    for dx in (-1, 0, 1):
                        for dy in (-1, 0, 1):
                            p = (a + dx, b + dy)
                            if 0 <= p[0] < W and 0 <= p[1] < H and p not in seen and rows[p[1]][p[0]] != ".":
                                seen.add(p); st.append(p)
                sizes.append(n)
    return sorted(sizes, reverse=True)


def readability(m):
    """One-colour readability: share of colour stitches kept, the largest enclosed gap as a share of the
    shape, and parts the one-colour version gains (small ones, e.g. pupils, are allowed)."""
    c, mo = m["colour"], m["mono"]
    kept = m["mono_count"] / sum(m["counts"].values())
    H, W = len(mo), len(mo[0])
    ext = set(); st = [(x, y) for x in range(W) for y in (0, H - 1)] + [(x, y) for y in range(H) for x in (0, W - 1)]
    while st:
        x, y = st.pop()
        if (x, y) in ext or not (0 <= x < W and 0 <= y < H) or c[y][x] != ".":
            continue
        ext.add((x, y)); st += [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
    gaps = ["".join("g" if c[y][x] != "." and mo[y][x] == "." else "." for x in range(W)) for y in range(H)]
    gap = max(parts(gaps) or [0]) / sum(m["counts"].values())
    pc, pm = parts(c), parts(mo)
    extra = pm[len(pc):] if len(pm) > len(pc) else []
    return kept, gap, extra


def stray(rows):
    """Stitched cells with no stitched 8-neighbour."""
    H, W = len(rows), len(rows[0]); bad = []
    for y in range(H):
        for x in range(W):
            if rows[y][x] != "." and not any(0 <= y + dy < H and 0 <= x + dx < W and rows[y + dy][x + dx] != "."
                                            for dx in (-1, 0, 1) for dy in (-1, 0, 1) if (dx, dy) != (0, 0)):
                bad.append((x + 1, y + 1))
    return bad


def ranges(ms):
    """Size ranges for the copy, computed from the grids (inches rounded to 0.1)."""
    ws, hs = [m["w"] for m in ms], [m["h"] for m in ms]
    lo, hi = min(ws + hs), max(ws + hs)
    return {"w": [min(ws), max(ws)], "h": [min(hs), max(hs)],
            "stitches": f"{min(ws)} to {max(ws)} stitches wide and {min(hs)} to {max(hs)} high",
            "in14": f"{lo / 14:.1f} to {hi / 14:.1f} in", "in18": f"{lo / 18:.1f} to {hi / 18:.1f} in"}


def build():
    data = {"palette": {k: dict(zip(("dmc", "name", "hex", "symbol"), v)) for k, v in PALETTE.items()},
            "mono": dict(zip(("dmc", "name", "hex", "symbol"), MONO)), "stitches_per_skein": STITCHES_PER_SKEIN, "motifs": []}
    for i, (key, title, fn) in enumerate(MOTIFS):
        rows, opt = fn()
        mono = mono_of(rows, opt["light"], opt.get("split"))
        counts = {}
        for r in rows:
            for ch in r:
                if ch != ".":
                    counts[ch] = counts.get(ch, 0) + 1
        order = [k for k in PALETTE if k in counts]
        data["motifs"].append({"n": i + 1, "key": key, "title": title, "w": len(rows[0]), "h": len(rows),
                               "colour": rows, "mono": mono, "counts": {k: counts[k] for k in order},
                               "mono_count": sum(r.count("X") for r in mono)})
    data["ranges"] = ranges(data["motifs"])
    json.dump(data, open(os.path.join(HERE, "motifs.json"), "w"), indent=1)
    return data


def check(data=None, verbose=True):
    data = data or json.load(open(os.path.join(HERE, "motifs.json")))
    ok = True; msgs = []
    syms = [v["symbol"] for v in data["palette"].values()]
    if len(set(syms)) != len(syms):
        ok = False; msgs.append("palette symbols not unique")
    if len(data["palette"]) > 10 or len(data["palette"]) < 8:
        ok = False; msgs.append("palette size")
    for m in data["motifs"]:
        c, mo = m["colour"], m["mono"]
        dims = len(c[0]), len(c)
        good = (all(len(r) == m["w"] for r in c) and len(c) == m["h"] and all(len(r) == m["w"] for r in mo) and len(mo) == m["h"])
        size_ok = 23 <= m["w"] <= 35 and 23 <= m["h"] <= 35
        letters = set("".join(c)) - {"."}
        pal_ok = letters <= set(data["palette"]) and set("".join(mo)) <= {".", "X"}
        ncol_ok = 3 <= len(letters) <= 6
        s_c, s_m = stray(c), stray(mo)
        mono_cover = all(mo[y][x] == "." or c[y][x] != "." for y in range(m["h"]) for x in range(m["w"]))
        line = (f"{m['n']:2d} {m['key']:<10} {dims[0]}x{dims[1]} colours {len(letters)} "
                f"({' '.join(data['palette'][k]['dmc'] for k in m['counts'])}) stitches {sum(m['counts'].values())}/{m['mono_count']}")
        bad = []
        if not good: bad.append("ragged grid")
        if not size_ok: bad.append("size out of 23-35")
        if not pal_ok: bad.append("unknown letter")
        if not ncol_ok: bad.append("needs 3-6 colours")
        if s_c: bad.append(f"stray colour stitches {s_c}")
        if s_m: bad.append(f"stray mono stitches {s_m}")
        if not mono_cover: bad.append("mono stitch outside colour shape")
        kept, gap, extra = readability(m)
        line += f"  one-colour keeps {kept:.0%}, largest gap {gap:.0%}" + (f", new small parts {extra}" if extra else "")
        if kept < 0.65: bad.append("one-colour keeps < 65% of the stitches")
        if gap > 0.25: bad.append("one-colour has an enclosed gap > 25% of the motif (hollow)")
        if any(n > 6 for n in extra): bad.append("one-colour breaks into new parts > 6 stitches")
        if bad:
            ok = False
        msgs.append(line + ("  " + "; ".join(bad) if bad else ""))
    if verbose:
        print("\n".join(msgs))
    return ok


def contact(data):
    from PIL import Image, ImageDraw, ImageFont
    cs = 12; pad = 30; cols = 4
    fpath = os.path.join(HERE, "fonts", "Nunito-800.ttf")
    font = ImageFont.truetype(fpath, 26); small = ImageFont.truetype(fpath, 18)
    cellw = 2 * 37 * cs + 3 * pad; cellh = 37 * cs + 80
    rows = math.ceil(len(data["motifs"]) / cols)
    W, H = cols * cellw + pad, rows * cellh + 110
    im = Image.new("RGB", (W, H), "white"); d = ImageDraw.Draw(im)
    d.text((pad, 24), "Woodland Christmas mini ornaments: 12 motifs, colour + one-colour (1 square = 1 stitch)", fill="#2c1b36", font=font)
    pal = data["palette"]
    for i, m in enumerate(data["motifs"]):
        ox = pad + (i % cols) * cellw; oy = 90 + (i // cols) * cellh
        d.text((ox, oy), f"{m['n']}. {m['title']}  {m['w']}x{m['h']}  ({len(m['counts'])} colours)", fill="#2c1b36", font=small)
        for v, grid in enumerate((m["colour"], m["mono"])):
            gx = ox + v * (37 * cs + pad); gy = oy + 34
            d.rectangle([gx - 2, gy - 2, gx + m["w"] * cs + 1, gy + m["h"] * cs + 1], fill="#f7f4ee")
            for y, r in enumerate(grid):
                for x, ch in enumerate(r):
                    if ch != ".":
                        col = pal[ch]["hex"] if ch in pal else data["mono"]["hex"]
                        d.rectangle([gx + x * cs, gy + y * cs, gx + x * cs + cs - 1, gy + y * cs + cs - 1], fill=col)
    im.save(os.path.join(HERE, "contact-sheet.png"))


if __name__ == "__main__":
    if "--check" in sys.argv:
        sys.exit(0 if check() else 1)
    data = build()
    contact(data)
    sys.exit(0 if check(data) else 1)
