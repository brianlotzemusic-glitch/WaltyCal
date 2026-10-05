"""Fall line art for the rhythm flashcards, drawn in code (original, no clip art).

Every picture is drawn in a 100 x 100 box, y pointing down, and placed with
`art(name, x, y, size)`. Outlines are black with round joins; fills default to
white so the art works in black-and-white printing. `fill` swaps the main fill
(the cover uses the accent colour there; everything else stays black and white).
"""
import math

NAMES = ("maple", "leaf", "acorn", "pumpkin", "owl")


def _maple_points():
    """Maple leaf outline: (angle from straight up in degrees, radius) pairs, clockwise, centre (50, 54)."""
    half = [  # right half, from the top tip down to the stem notch
        (0, 47), (8, 30), (14, 33), (20, 20),            # top lobe tip, tooth, sinus
        (34, 25), (42, 38), (50, 35), (57, 47),          # upper-right lobe: teeth to tip
        (64, 35), (72, 37), (80, 22),                    # lower edge of upper lobe -> sinus
        (100, 25), (108, 33), (118, 29), (127, 36),      # lower lobe: teeth to tip
        (142, 18), (166, 12),                            # into the stem notch
    ]
    pts = half + [(-a, r) for a, r in reversed(half)]
    out = []
    for a, r in pts:
        t = math.radians(a)
        out.append((50 + r * math.sin(t), 54 - r * math.cos(t)))
    return out


def _path(pts, close=True):
    d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    return d + ("Z" if close else "")


MAPLE = _path(_maple_points())


def _body(name, fill, sw):
    k = f'stroke="#000" stroke-width="{sw:.2f}" stroke-linejoin="round" stroke-linecap="round"'
    if name == "maple":
        return (f'<path d="M50,66 Q50,86 45,98" fill="none" {k}/>'
                f'<path d="{MAPLE}" fill="{fill}" {k}/>'
                f'<path d="M50,66 L50,14 M50,58 L84,33 M50,58 L16,33 M50,64 L74,73 M50,64 L26,73" fill="none" {k}/>')
    if name == "leaf":
        return (f'<path d="M30,86 Q36,80 40,74" fill="none" {k}/>'
                f'<path d="M40,74 C14,60 22,24 78,12 C80,52 66,82 40,74 Z" fill="{fill}" {k}/>'
                f'<path d="M40,74 Q58,48 78,12 M50,58 L38,46 M50,58 L64,58 M58,44 L46,32 M58,44 L71,42 M66,30 L60,20" fill="none" {k}/>')
    if name == "acorn":
        return (f'<path d="M32,46 C31,70 43,84 50,92 C57,84 69,70 68,46 Z" fill="{fill}" {k}/>'
                f'<path d="M40,60 Q39,72 45,80" fill="none" {k}/>'
                f'<path d="M50,30 C51,22 54,17 60,13" fill="none" stroke="#000" stroke-width="{sw * 2.2:.2f}" stroke-linecap="round"/>'
                f'<path d="M23,47 C22,25 78,25 77,47 C66,53 34,53 23,47 Z" fill="#fff" {k}/>'
                f'<path d="M32,34 L44,48 M42,29 L56,49 M54,28 L66,46 M66,33 L72,42 M34,46 L46,30 M45,49 L58,29 M57,49 L69,34" fill="none" stroke="#000" stroke-width="{sw * 0.55:.2f}" stroke-linecap="round"/>')
    if name == "pumpkin":
        return (f'<ellipse cx="32" cy="62" rx="22" ry="25" fill="{fill}" {k}/>'
                f'<ellipse cx="68" cy="62" rx="22" ry="25" fill="{fill}" {k}/>'
                f'<ellipse cx="50" cy="62" rx="17" ry="27" fill="{fill}" {k}/>'
                f'<path d="M45,37 C46,30 46,25 44,19 L52,17 C54,24 54,31 54,37 Z" fill="#fff" {k}/>'
                f'<path d="M54,28 C62,20 72,22 74,30 C70,27 63,26 56,32" fill="#fff" {k}/>'
                f'<path d="M40,27 C34,24 31,30 35,32 C38,34 40,30 37,29" fill="none" {k}/>')
    if name == "owl":
        return (f'<path d="M36,96 L64,96" fill="none" stroke="#000" stroke-width="{sw * 1.8:.2f}" stroke-linecap="round"/>'
                f'<path d="M50,20 C76,20 82,40 80,62 C78,82 66,92 50,92 C34,92 22,82 20,62 C18,40 24,20 50,20 Z" fill="{fill}" {k}/>'
                f'<path d="M24,30 L22,10 L38,22 M76,30 L78,10 L62,22" fill="#fff" {k}/>'
                f'<path d="M22,56 C14,70 22,84 32,86 M78,56 C86,70 78,84 68,86" fill="none" {k}/>'
                f'<circle cx="38" cy="43" r="11" fill="#fff" {k}/><circle cx="62" cy="43" r="11" fill="#fff" {k}/>'
                f'<circle cx="39" cy="44" r="5" fill="#000"/><circle cx="61" cy="44" r="5" fill="#000"/>'
                f'<circle cx="40.6" cy="42.2" r="1.6" fill="#fff"/><circle cx="62.6" cy="42.2" r="1.6" fill="#fff"/>'
                f'<path d="M46,52 L54,52 L50,59 Z" fill="#000" {k}/>'
                f'<path d="M40,68 l4,4 l4,-4 M52,68 l4,4 l4,-4 M46,78 l4,4 l4,-4" fill="none" {k}/>'
                f'<path d="M42,92 l-2,5 M46,92 l0,5 M54,92 l0,5 M58,92 l2,5" fill="none" {k}/>')
    raise KeyError(name)


def art(name, x, y, size, stroke_pt=1.6, fill="#fff", rotate=0):
    """SVG group drawing `name` with its 100x100 box at (x, y), `size` points wide."""
    sc = size / 100
    sw = stroke_pt / sc
    rot = f" rotate({rotate} 50 50)" if rotate else ""
    return f'<g transform="translate({x:.2f},{y:.2f}) scale({sc:.4f}){rot}">{_body(name, fill, sw)}</g>'
