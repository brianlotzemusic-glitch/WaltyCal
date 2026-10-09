"""Thanksgiving line art for Rhythm Match + Echo Cards, drawn in code (original, no clip art, no AI images).

Harvest-table theme only: a friendly turkey, pie, an ear of corn, an apple, plus
item 002's maple leaf, leaf, acorn and pumpkin (loaded from its art.py, so the
fall line looks like one family). No people, no history scenes, no religious images.

Same API as items 002/003: every picture is drawn in a 100 x 100 box, y pointing
down, placed with `art(name, x, y, size)`. Outlines are black with round joins;
`fill` swaps the main fill (accent on the cover, white elsewhere), so every
picture still works in black-and-white printing.
"""
import importlib.util
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location(
    "art002", os.path.join(os.path.dirname(HERE), "002-fall-rhythm-flashcards", "art.py"))
A2 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(A2)

NEW = ("turkey", "pie", "corn", "apple")
NAMES = NEW + ("maple", "leaf", "acorn", "pumpkin")


def _body(name, fill, sw):
    k = f'stroke="#000" stroke-width="{sw:.2f}" stroke-linejoin="round" stroke-linecap="round"'
    thin = f'stroke="#000" stroke-width="{sw * 0.6:.2f}" stroke-linecap="round" fill="none"'
    if name == "turkey":
        out = []
        # tail fan: seven rounded feathers behind the body, alternating fill and white
        for i, deg in enumerate(range(-165, -14, 25)):
            a = math.radians(deg)
            cx, cy = 50 + 27 * math.cos(a), 60 + 27 * math.sin(a)
            out.append(f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="9.5" ry="20" transform="rotate({deg + 90} {cx:.1f} {cy:.1f})" '
                       f'fill="{fill if i % 2 == 0 else "#fff"}" {k}/>')
        out.append(f'<path d="M43,84 L41,95 M41,95 L36,97 M41,95 L44,98 M57,84 L59,95 M59,95 L64,97 M59,95 L56,98" fill="none" {k}/>')
        out.append(f'<ellipse cx="50" cy="66" rx="21" ry="21" fill="#fff" {k}/>')
        out.append(f'<path d="M34,64 Q40,76 50,78 M66,64 Q60,76 50,78" {thin}/>')
        out.append(f'<circle cx="50" cy="42" r="12" fill="#fff" {k}/>')
        out.append('<circle cx="45.5" cy="40" r="2.4" fill="#000"/><circle cx="54.5" cy="40" r="2.4" fill="#000"/>'
                   '<circle cx="46.3" cy="39.2" r="0.8" fill="#fff"/><circle cx="55.3" cy="39.2" r="0.8" fill="#fff"/>')
        out.append(f'<path d="M46.5,45 L53.5,45 L50,51 Z" fill="{fill}" {k}/>')
        out.append(f'<path d="M52.5,48 C57,50 57,56 54,58 C52,56 52,52 52.5,48 Z" fill="#fff" {k}/>')
        return "".join(out)
    if name == "pie":
        return (f'<path d="M10,54 L90,54 L82,78 Q81,82 76,82 L24,82 Q19,82 18,78 Z" fill="#fff" {k}/>'
                f'<path d="M22,62 L26,80 M36,62 L38,82 M50,62 L50,82 M64,62 L62,82 M78,62 L74,80" {thin}/>'
                f'<ellipse cx="50" cy="54" rx="41" ry="13" fill="#fff" {k}/>'
                f'<ellipse cx="50" cy="54" rx="32" ry="8.5" fill="{fill}" {k}/>'
                f'<path d="M40,52 C36,46 42,40 46,42 C46,34 56,34 56,41 C61,39 65,46 60,52 Z" fill="#fff" {k}/>'
                f'<path d="M46,42 Q49,46 52,44" {thin}/>')
    if name == "corn":
        rows = "".join(f'M{40 + abs(y - 46) * 0.13:.1f},{y} Q50,{y + 3} {60 - abs(y - 46) * 0.13:.1f},{y} ' for y in range(22, 76, 7))
        return (f'<path d="M50,8 C63,11 66,52 58,82 L42,82 C34,52 37,11 50,8 Z" fill="{fill}" {k}/>'
                f'<path d="{rows} M46,12 Q44,46 46,80 M54,12 Q56,46 54,80" {thin}/>'
                f'<path d="M45,92 C24,78 18,52 26,28 C34,48 40,66 50,80 Z" fill="#fff" {k}/>'
                f'<path d="M55,92 C76,78 82,52 74,28 C66,48 60,66 50,80 Z" fill="#fff" {k}/>'
                f'<path d="M30,44 Q34,64 44,82 M70,44 Q66,64 56,82" {thin}/>'
                f'<path d="M45,91 L55,91 L53,98 L47,98 Z" fill="#fff" {k}/>')
    if name == "apple":
        return (f'<path d="M50,30 C40,20 14,24 16,52 C18,80 36,94 50,86 C64,94 82,80 84,52 C86,24 60,20 50,30 Z" fill="{fill}" {k}/>'
                f'<path d="M50,30 Q49,18 55,9" fill="none" stroke="#000" stroke-width="{sw * 1.7:.2f}" stroke-linecap="round"/>'
                f'<path d="M54,22 C60,10 76,10 80,16 C72,26 60,27 54,22 Z" fill="#fff" {k}/>'
                f'<path d="M58,20 Q67,17 76,16" {thin}/>'
                f'<path d="M26,46 Q26,36 34,32" {thin}/>')
    return A2._body(name, fill, sw)


def art(name, x, y, size, stroke_pt=1.6, fill="#fff", rotate=0):
    """SVG group drawing `name` with its 100x100 box at (x, y), `size` points wide."""
    if name not in NAMES:
        raise KeyError(name)
    sc = size / 100
    sw = stroke_pt / sc
    rot = f" rotate({rotate} 50 50)" if rotate else ""
    return f'<g transform="translate({x:.2f},{y:.2f}) scale({sc:.4f}){rot}">{_body(name, fill, sw)}</g>'
