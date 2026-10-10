"""Winter concert line art for the Winter Concert Planner, drawn in code (original, no clip art, no AI images).

Non-denominational on purpose: item 003's snowflake, mitten, knit hat and cocoa
mug (loaded from its art.py so the winter line looks like one family), plus a
music stand and a snare drum drawn here. No trees, stars, gifts, ornaments,
candles or religious symbols.

Same API as items 002-004: every picture is drawn in a 100 x 100 box, y pointing
down, placed with `art(name, x, y, size)`. Outlines are black with round joins;
`fill` swaps the main fill (accent on the cover, white elsewhere), so every
picture still works in black-and-white printing.
"""
import importlib.util
import os

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location(
    "art003", os.path.join(os.path.dirname(HERE), "003-winter-rhythm-bingo", "art.py"))
A3 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(A3)

NEW = ("stand", "drum")
NAMES = NEW + ("snowflake", "mitten", "hat", "mug")


def _body(name, fill, sw, line):
    k = f'stroke="{line}" stroke-width="{sw:.2f}" stroke-linejoin="round" stroke-linecap="round"'
    thin = f'stroke="{line}" stroke-width="{sw * 0.65:.2f}" stroke-linecap="round" fill="none"'
    if name == "stand":
        # a music stand: tilted desk with a lip and sheet music, a pole and a tripod base
        return (f'<path d="M50,52 L50,88 M50,88 L30,97 M50,88 L70,97 M50,88 L50,97" fill="none" {k}/>'
                f'<rect x="46" y="50" width="8" height="10" rx="2" fill="#fff" {k}/>'
                f'<path d="M14,10 L86,10 L82,50 L18,50 Z" fill="{fill}" {k}/>'
                f'<path d="M12,50 L88,50 L88,56 L12,56 Z" fill="#fff" {k}/>'
                f'<rect x="24" y="14" width="24" height="33" fill="#fff" {k}/>'
                f'<rect x="52" y="14" width="24" height="33" fill="#fff" {k}/>'
                f'<path d="M27,21 L45,21 M27,25 L45,25 M27,29 L45,29 M27,35 L45,35 M27,39 L45,39 M27,43 L45,43 '
                f'M55,21 L73,21 M55,25 L73,25 M55,29 L73,29 M55,35 L73,35 M55,39 L73,39 M55,43 L73,43" {thin}/>')
    if name == "drum":
        # a snare drum with two crossed sticks
        return (f'<path d="M58,6 L86,40 M42,6 L14,40" fill="none" stroke="{line}" stroke-width="{sw * 1.6:.2f}" stroke-linecap="round"/>'
                f'<circle cx="58" cy="6" r="3" fill="#fff" {k}/><circle cx="42" cy="6" r="3" fill="#fff" {k}/>'
                f'<path d="M12,46 L12,80 C12,92 88,92 88,80 L88,46" fill="{fill}" {k}/>'
                f'<ellipse cx="50" cy="46" rx="38" ry="11" fill="#fff" {k}/>'
                f'<path d="M12,52 C12,64 88,64 88,52 M12,74 C12,86 88,86 88,74" {thin}/>'
                f'<path d="M22,59 L30,80 L38,62 L46,83 L54,62 L62,83 L70,62 L78,80" {thin}/>')
    raise KeyError(name)


def art(name, x, y, size, stroke_pt=1.6, fill="#fff", rotate=0, line="#000"):
    """SVG group drawing `name` with its 100x100 box at (x, y), `size` points wide."""
    if name not in NEW:
        return A3.art(name, x, y, size, stroke_pt, fill=fill, rotate=rotate, line=line)
    sc = size / 100
    sw = stroke_pt / sc
    rot = f" rotate({rotate} 50 50)" if rotate else ""
    return f'<g transform="translate({x:.2f},{y:.2f}) scale({sc:.4f}){rot}">{_body(name, fill, sw, line)}</g>'
