"""Winter line art for Winter Rhythm Bingo, drawn in code (original, no clip art, no AI images).

Non-denominational on purpose: snowflakes, mittens, a sled, a knit hat, a cocoa
mug and an ice skate. No trees, stars, gifts, ornaments or religious symbols.

Same API as item 002's art.py: every picture is drawn in a 100 x 100 box,
y pointing down, placed with `art(name, x, y, size)`. Outlines are black with
round joins; `fill` swaps the main fill (accent on the cover, white elsewhere),
`line` the outline colour (used for accent snowflakes).
"""
import math

NAMES = ("snowflake", "mitten", "sled", "hat", "mug", "skate")


def _snowflake(sw, fill, line):
    k = f'stroke="{line}" stroke-width="{sw:.2f}" stroke-linecap="round" stroke-linejoin="round" fill="none"'
    d = []
    for i in range(6):
        a = math.radians(i * 60 - 90)
        ca, sa = math.cos(a), math.sin(a)

        def p(r, off=0.0):
            b = a + math.radians(off)
            return 50 + r * math.cos(b), 50 + r * math.sin(b)
        x, y = p(46)
        d.append(f"M{50 + 9 * ca:.1f},{50 + 9 * sa:.1f} L{x:.1f},{y:.1f}")
        for r, ln in ((22, 13), (34, 9)):
            bx, by = 50 + r * ca, 50 + r * sa
            for side in (-1, 1):
                b = a + side * math.radians(55)
                d.append(f"M{bx:.1f},{by:.1f} L{bx + ln * math.cos(b):.1f},{by + ln * math.sin(b):.1f}")
    hexa = " L".join(f"{50 + 9 * math.cos(math.radians(i * 60 - 90)):.1f},{50 + 9 * math.sin(math.radians(i * 60 - 90)):.1f}" for i in range(6))
    return (f'<path d="{" ".join(d)}" {k}/>'
            f'<path d="M{hexa} Z" fill="{fill}" stroke="{line}" stroke-width="{sw:.2f}" stroke-linejoin="round"/>')


def _body(name, fill, sw, line):
    k = f'stroke="{line}" stroke-width="{sw:.2f}" stroke-linejoin="round" stroke-linecap="round"'
    thin = f'stroke="{line}" stroke-width="{sw * 0.7:.2f}" stroke-linecap="round" fill="none"'
    if name == "snowflake":
        return _snowflake(sw, fill, line)
    if name == "mitten":
        return (f'<path d="M38,62 C22,64 12,52 16,42 C19,34 28,35 33,44" fill="{fill}" {k}/>'
                f'<path d="M30,72 L30,36 C30,10 74,8 74,36 L74,72 Z" fill="{fill}" {k}/>'
                f'<path d="M33,44 C35,50 37,56 38,62" fill="none" {k}/>'
                f'<path d="M36,50 l6,-6 l6,6 l6,-6 l6,6 l6,-6" {thin}/>'
                f'<rect x="26" y="70" width="52" height="20" rx="5" fill="#fff" {k}/>'
                f'<path d="M34,73 L34,87 M42,73 L42,87 M50,73 L50,87 M58,73 L58,87 M66,73 L66,87 M74,73 L74,87" {thin}/>')
    if name == "sled":
        return (f'<path d="M10,46 Q30,40 50,42 L50,48 Q30,46 10,52 Z" fill="none" {k}/>'
                f'<path d="M8,80 L80,80 C94,80 96,62 86,60 C80,59 79,66 84,67" fill="none" stroke="{line}" stroke-width="{sw * 1.5:.2f}" stroke-linecap="round" stroke-linejoin="round"/>'
                f'<path d="M20,64 L24,80 M46,64 L48,80 M70,64 L72,80" fill="none" {k}/>'
                f'<rect x="12" y="56" width="70" height="10" rx="4" fill="{fill}" {k}/>'
                f'<path d="M30,56 L30,66 M47,56 L47,66 M64,56 L64,66" {thin}/>'
                f'<path d="M80,58 C88,40 70,30 60,36" fill="none" {thin} stroke-dasharray="0.1 {sw * 1.6:.2f}"/>')
    if name == "hat":
        return (f'<circle cx="50" cy="20" r="11" fill="#fff" {k}/>'
                f'<path d="M18,68 C16,40 32,28 50,28 C68,28 84,40 82,68 Z" fill="{fill}" {k}/>'
                f'<path d="M24,48 Q50,40 76,48 M20,58 Q50,50 80,58" {thin}/>'
                f'<rect x="14" y="64" width="72" height="20" rx="6" fill="#fff" {k}/>'
                f'<path d="M22,67 L22,81 M30,67 L30,81 M38,67 L38,81 M46,67 L46,81 M54,67 L54,81 M62,67 L62,81 M70,67 L70,81 M78,67 L78,81" {thin}/>')
    if name == "mug":
        return (f'<path d="M70,46 C90,44 90,74 68,74" fill="none" stroke="{line}" stroke-width="{sw * 2.4:.2f}" stroke-linecap="round"/>'
                f'<path d="M70,46 C90,44 90,74 68,74" fill="none" stroke="#fff" stroke-width="{sw * 0.6:.2f}" stroke-linecap="round"/>'
                f'<path d="M22,38 L74,38 L70,88 Q69,93 64,93 L32,93 Q27,93 26,88 Z" fill="{fill}" {k}/>'
                f'<ellipse cx="48" cy="38" rx="26" ry="5" fill="#fff" {k}/>'
                f'<rect x="34" y="31" width="10" height="8" rx="2" fill="#fff" {k}/>'
                f'<rect x="48" y="30" width="10" height="8" rx="2" fill="#fff" {k} transform="rotate(12 53 34)"/>'
                f'<path d="M36,24 C30,18 42,14 36,6 M50,24 C44,18 56,14 50,6 M62,24 C56,18 68,14 62,6" {thin}/>')
    if name == "skate":
        return (f'<path d="M30,10 L54,10 C55,28 55,42 60,48 C74,51 86,56 86,68 L86,74 L26,74 L26,14 Q26,10 30,10 Z" fill="{fill}" {k}/>'
                f'<path d="M50,16 L58,22 M50,24 L58,30 M51,32 L59,38 M58,16 L50,22 M58,24 L50,30 M59,32 L51,38" {thin}/>'
                f'<path d="M26,62 L86,62" {thin}/>'
                f'<path d="M36,74 L36,85 M76,74 L76,85" fill="none" {k}/>'
                f'<path d="M18,86 L84,86 C94,86 96,76 90,74" fill="none" stroke="{line}" stroke-width="{sw * 1.6:.2f}" stroke-linecap="round"/>')
    raise KeyError(name)


def art(name, x, y, size, stroke_pt=1.6, fill="#fff", rotate=0, line="#000"):
    """SVG group drawing `name` with its 100x100 box at (x, y), `size` points wide."""
    sc = size / 100
    sw = stroke_pt / sc
    rot = f" rotate({rotate} 50 50)" if rotate else ""
    return f'<g transform="translate({x:.2f},{y:.2f}) scale({sc:.4f}){rot}">{_body(name, fill, sw, line)}</g>'
