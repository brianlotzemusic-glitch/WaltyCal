"""Twelve winter movement pictograms, drawn in code on a 100 x 100 grid.

Stroke 3.2, round caps. Every shape stays inside 6..94, so the padding is at least about twice the stroke; gen.py --check
renders each one and measures the ink to the edge of its box.
"""
SW = 3.2
ACC = "ACC"   # replaced by the accent colour in gen.py


def f(v):
    return f"{v:.1f}".rstrip("0").rstrip(".")


def line(*pts, **kw):
    d = " ".join(f"{f(x)},{f(y)}" for x, y in pts)
    st = kw.get("stroke")
    return f'<polyline points="{d}"' + (f' stroke="{st}"' if st else "") + "/>"


def person(hx, hy, neck, hip, arms, legs):
    """Stick child with a beanie. arms and legs are lists of point lists."""
    s = [f'<circle cx="{f(hx)}" cy="{f(hy)}" r="7" fill="#fff"/>',
         f'<path d="M{f(hx - 7.4)},{f(hy - 1.2)} A7.4,7.4 0 0 1 {f(hx + 7.4)},{f(hy - 1.2)} Z" fill="{ACC}"/>',
         f'<circle cx="{f(hx)}" cy="{f(hy - 9.4)}" r="2.4" fill="#fff"/>',
         line((hx, hy + 7), neck, hip)]
    for a in arms:
        s.append(line(*a))
    for lg in legs:
        s.append(line(*lg))
    return "".join(s)


def flake(cx, cy, r=7):
    return ("".join(f'<line x1="{f(cx - r * c)}" y1="{f(cy - r * s)}" x2="{f(cx + r * c)}" y2="{f(cy + r * s)}" stroke="{ACC}"/>'
                    for c, s in ((1, 0), (0.5, 0.866), (-0.5, 0.866))))


def mitten(cx, cy, rot, flip):
    sx = -1 if flip else 1
    return (f'<g transform="translate({cx},{cy}) rotate({rot}) scale({sx},1)">'
            f'<path d="M-10,20 V-6 Q-10,-22 0,-22 Q10,-22 10,-6 V20 Z" fill="#fff"/>'
            f'<path d="M10,2 Q21,-3 20,8 Q19,15 10,14" fill="#fff"/>'
            f'<rect x="-11" y="20" width="22" height="9" rx="2" fill="{ACC}"/></g>')


def penguin():
    return (f'<path d="M50,20 C66,20 72,40 72,58 C72,76 62,84 50,84 C38,84 28,76 28,58 C28,40 34,20 50,20 Z" fill="#000"/>'
            f'<path d="M50,40 C60,40 63,54 63,64 C63,76 57,80 50,80 C43,80 37,76 37,64 C37,54 40,40 50,40 Z" fill="#fff" stroke-width="0"/>'
            f'<circle cx="44" cy="31" r="2.6" fill="#fff" stroke-width="0"/><circle cx="56" cy="31" r="2.6" fill="#fff" stroke-width="0"/>'
            f'<path d="M46,36 L54,36 L50,43 Z" fill="{ACC}"/>'
            f'<path d="M29,44 L16,60 L21,64 L31,56" fill="#000"/>'
            f'<path d="M71,44 L84,34 L88,39 L71,56" fill="#000"/>'
            f'<ellipse cx="41" cy="88" rx="8" ry="3.4" fill="{ACC}"/><ellipse cx="62" cy="83" rx="7" ry="3" fill="{ACC}"/>')


def skate():
    return (line((8, 92), (92, 92), stroke=ACC)
            + person(46, 22, (46, 31), (48, 55), [[(46, 35), (30, 42), (20, 38)], [(46, 35), (62, 38), (76, 32)]],
                     [[(48, 55), (46, 72), (46, 83)], [(48, 55), (64, 64), (80, 70)]])
            + line((46, 83), (46, 87)) + line((36, 87), (57, 87)))


def snowshoe():
    sh = lambda cx, cy, rx: (f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="5" fill="#fff"/>'
                             f'<line x1="{cx - rx / 2}" y1="{cy}" x2="{cx + rx / 2}" y2="{cy}" stroke="{ACC}"/>')
    return (person(46, 20, (46, 29), (48, 54), [[(46, 34), (34, 44), (24, 50)], [(46, 34), (58, 44), (68, 40)]],
                   [[(48, 54), (60, 68), (64, 80)], [(48, 54), (38, 70), (30, 80)]])
            + sh(66, 84, 17) + sh(28, 84, 15))


def shovel():
    return (person(30, 26, (32, 35), (36, 58), [[(33, 40), (48, 44), (63, 52)]],
                   [[(36, 58), (30, 74), (22, 88)], [(36, 58), (42, 74), (40, 88)]])
            + line((72, 28), (56, 72))
            + f'<path d="M50,70 L64,76 L59,86 L45,80 Z" fill="{ACC}"/>'
            + '<path d="M72,90 Q82,68 92,90 Z" fill="#fff"/>')


def snowball():
    return (line((8, 92), (92, 92), stroke=ACC)
            + person(24, 32, (26, 41), (24, 62), [[(27, 46), (42, 52), (50, 58)]],
                     [[(24, 62), (18, 76), (12, 90)], [(24, 62), (30, 78), (34, 90)]])
            + '<circle cx="68" cy="64" r="24" fill="#fff"/>'
            + f'<path d="M54,62 Q60,50 72,54 Q80,58 76,68" stroke="{ACC}"/>')


def sled():
    return (f'<rect x="26" y="62" width="48" height="8" rx="3" fill="{ACC}"/>'
            + line((32, 70), (32, 80)) + line((68, 70), (68, 80))
            + '<path d="M18,80 L72,80 Q84,80 85,68" fill="none"/>'
            + person(44, 30, (44, 38), (46, 60), [[(45, 43), (58, 50), (68, 54)]], [[(46, 60), (62, 60), (72, 56)]])
            + line((8, 56), (18, 56)) + line((10, 66), (18, 66)) + line((8, 76), (14, 76)))


def tiptoe():
    return (f'<ellipse cx="50" cy="90" rx="40" ry="3.6" fill="#fff" stroke="{ACC}"/>'
            + person(50, 20, (50, 29), (50, 54), [[(50, 34), (34, 38), (24, 48)], [(50, 34), (66, 38), (76, 48)]],
                     [[(50, 54), (44, 72), (45, 82), (50, 87)], [(50, 54), (58, 70), (58, 80), (63, 85)]])
            + flake(82, 20, 7))


def stomp():
    boot = lambda x, y: f'<path d="M{x},{y} h8 v6 h8 v5 h-16 Z" fill="{ACC}"/>'
    return (person(46, 22, (46, 31), (46, 55), [[(46, 36), (32, 44), (26, 32)], [(46, 36), (60, 44), (66, 32)]],
                   [[(46, 55), (46, 70), (46, 80)], [(46, 55), (64, 60), (68, 70)]])
            + boot(38, 80) + boot(62, 70)
            + '<circle cx="20" cy="84" r="4.5" fill="#fff"/><circle cx="12" cy="76" r="3.4" fill="#fff"/><circle cx="82" cy="86" r="4.5" fill="#fff"/>')


def cocoa():
    return ('<rect x="22" y="44" width="42" height="42" rx="6" fill="#fff"/>'
            f'<rect x="23.6" y="58" width="38.8" height="10" fill="{ACC}" stroke-width="0"/>'
            '<path d="M64,52 H72 A9,9 0 0 1 72,70 H64" fill="none"/>'
            '<path d="M32,38 q-5,-5 0,-10 q5,-5 0,-10" fill="none"/><path d="M44,38 q-5,-5 0,-10 q5,-5 0,-10" fill="none"/>'
            + line((58, 20), (46, 56))
            + f'<path d="M86.5,35.1 A9,9 0 1 1 74.9,23.5" fill="none" stroke="{ACC}"/>' + f'<path d="M69.6,22.1 L74.9,23.5 L71.8,28.0" fill="none" stroke="{ACC}"/>')


def mittens():
    return (mitten(30, 52, 22, False) + mitten(70, 52, -22, True)
            + f'<line x1="50" y1="12" x2="50" y2="22" stroke="{ACC}"/><line x1="36" y1="18" x2="40" y2="26" stroke="{ACC}"/>'
            f'<line x1="64" y1="18" x2="60" y2="26" stroke="{ACC}"/>')


def flakes():
    return (person(50, 42, (50, 51), (50, 70), [[(50, 56), (36, 46), (30, 32)], [(50, 56), (64, 46), (70, 32)]],
                   [[(50, 70), (44, 80), (42, 90)], [(50, 70), (56, 80), (58, 90)]])
            + flake(20, 18, 7) + flake(50, 15, 7) + flake(82, 20, 7))


def drift():
    return ('<path d="M6,90 Q28,64 50,66 Q72,64 94,90 Z" fill="#fff"/>'
            + person(46, 20, (46, 29), (50, 46), [[(46, 33), (32, 28), (24, 18)], [(46, 33), (60, 28), (70, 18)]],
                     [[(50, 46), (64, 50), (62, 58)], [(50, 46), (40, 54), (46, 62)]])
            + line((12, 52), (20, 56)) + line((80, 54), (88, 50)))


MOVES = [  # id, drawing, title, beat direction, rhythm verb
    ("penguin", penguin, "March like a penguin", "Waddle in place with one step on every beat.", "Waddle"),
    ("skate", skate, "Skate on the ice", "Glide one foot forward on every beat.", "Glide"),
    ("snowshoe", snowshoe, "Snowshoe walk", "Lift your big snowshoes high and step on every beat.", "Step"),
    ("shovel", shovel, "Shovel the snow", "Scoop and toss one shovelful on every beat.", "Scoop"),
    ("snowball", snowball, "Roll a snowball", "Push the snowball once on every beat.", "Push"),
    ("sled", sled, "Sled slide", "Rock side to side on your sled on every beat.", "Rock"),
    ("tiptoe", tiptoe, "Tiptoe on ice", "Take one tiny tiptoe step on every beat.", "Tiptoe"),
    ("stomp", stomp, "Stomp your boots", "Stomp the snow off your boots on every beat.", "Stomp"),
    ("cocoa", cocoa, "Stir the cocoa", "Stir a big circle in the air on every beat.", "Stir"),
    ("mittens", mittens, "Clap your mittens", "Clap your mittens together on every beat.", "Clap"),
    ("flakes", flakes, "Catch snowflakes", "Reach up and catch a snowflake on every beat.", "Reach"),
    ("drift", drift, "Hop the snowdrift", "Bend your knees and bounce on every beat.", "Bounce"),
]


def pic_svg(i, accent, size=None, cls="pic"):
    pid, fn, title = MOVES[i][0], MOVES[i][1], MOVES[i][2]
    body = fn().replace(ACC, accent)
    dim = f' width="{size}" height="{size}"' if size else ""
    return (f'<svg class="{cls}" data-pic="{pid}" data-sw="{SW}" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"{dim}>'
            f'<title>{title}</title><g fill="none" stroke="#000" stroke-width="{SW}" stroke-linecap="round" stroke-linejoin="round">{body}</g></svg>')
