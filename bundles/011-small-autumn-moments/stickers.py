"""Small Autumn Moments: lay out the print-then-cut sticker sheet.

20 badge stickers (cream disc + line-art icon + a phrase pill), each with a
white offset border whose outer edge is the cut line. Sizes are in pixels at
300 DPI on a 6.75 x 9.25 in sheet (2025 x 2775 px): Cricut Print Then Cut's
maximum printable area. Text is measured with the real font (Fraunces 700) so
the pills fit their phrases.

  python3 stickers.py           # writes stickers.json (sticker SVGs + sheet SVG + proof)
  python3 stickers.py --check   # re-checks the sheet: inside the area, gaps, one cut piece each
"""
import json, os, sys
from PIL import ImageFont
from shapely.geometry import Polygon, Point, box
from shapely.ops import unary_union
from shapely import affinity
import icons as IC

HERE = os.path.dirname(os.path.abspath(__file__))
DPI = 300
SHEET_W, SHEET_H = int(6.75 * DPI), int(9.25 * DPI)      # 2025 x 2775
COLS, ROWS = 4, 5
MARGIN = 24            # px from the sheet edge to the cell grid
BORDER = 24            # white offset border (0.08 in, about 2 mm)
MIN_GAP = 45           # px between cut lines (0.15 in): room for Cricut's bleed
DISC_R = 178
ICON = 300             # icon box inside the disc (the 1000-unit icon box maps to this)
PILL_H, PILL_Y, FONT_PX = 80, 172, 43
PILLS = [IC.PLUM, IC.PINE, IC.BERRY]
FONT = ImageFont.truetype(os.path.join(HERE, "fonts", "Fraunces-700.ttf"), FONT_PX)


def d_of(g):
    return IC.path_d(g)


def sticker(icon, k):
    """Return (svg body in local coords centred on the disc, outline polygon)."""
    tw = FONT.getlength(icon["phrase"])
    pw = tw + 54
    pill = box(-pw / 2, PILL_Y - PILL_H / 2, pw / 2, PILL_Y + PILL_H / 2).buffer(-PILL_H / 2 + 1).buffer(PILL_H / 2 - 1)
    disc = Point(0, 0).buffer(DISC_R, 96)
    s = ICON / 1000
    layers = IC.fit(dict((n, f) for n, f, p in IC.ICONS)[icon["name"]]())
    sil = unary_union([g.buffer(sw / 2 if st else 0) for g, f, st, sw in layers])
    sil = affinity.translate(affinity.scale(sil, s, s, origin=(500, 500)), -500, -510)
    body = unary_union([disc, pill, sil])
    out = body.buffer(BORDER + 30, 48).buffer(-30, 48)
    if out.geom_type != "Polygon":
        raise SystemExit(f"{icon['phrase']}: outline is not one piece")
    out = Polygon(out.exterior).simplify(0.8)
    col = PILLS[k % 3]
    svg = (f'<path class=cut fill="#fff" d="{d_of(out)}"/>'
           f'<circle r="{DISC_R}" fill="{IC.CREAM}" stroke="{IC.PLUM}" stroke-width="5"/>'
           f'<circle r="{DISC_R - 14}" fill="none" stroke="{IC.GOLD}" stroke-width="3" stroke-dasharray="2 12" stroke-linecap="round"/>'
           f'<g transform="translate({-ICON / 2},{-ICON / 2 - 10}) scale({s})">{icon["svg"]}</g>'
           f'<path fill="{col}" stroke="{IC.PLUM}" stroke-width="4" d="{d_of(pill)}"/>'
           f'<text x="0" y="{PILL_Y + FONT_PX * 0.34:.1f}" text-anchor="middle" font-family="Fr" font-weight="700" '
           f'font-size="{FONT_PX}" fill="{IC.CREAM if col != IC.GOLD else IC.PLUM}">{icon["phrase"]}</text>')
    return svg, out


def build():
    data = json.load(open(os.path.join(HERE, "icons.json")))
    items = [i for i in data["icons"] if i["phrase"]]
    assert len(items) == COLS * ROWS, len(items)
    cw, ch = (SHEET_W - 2 * MARGIN) / COLS, (SHEET_H - 2 * MARGIN) / ROWS
    stickers, outlines, parts = [], [], []
    for k, icon in enumerate(items):
        r, c = divmod(k, COLS)
        svg, out = sticker(icon, r + c)
        x0, y0, x1, y1 = out.bounds
        cx = MARGIN + cw * (c + 0.5) - (x0 + x1) / 2
        cy = MARGIN + ch * (r + 0.5) - (y0 + y1) / 2
        placed = affinity.translate(out, cx, cy)
        outlines.append(placed)
        w, h = x1 - x0, y1 - y0
        stickers.append({"name": icon["name"], "phrase": icon["phrase"], "x": round(cx, 1), "y": round(cy, 1),
                         "w_in": round(w / DPI, 2), "h_in": round(h / DPI, 2),
                         "svg": f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0 - 4:.0f} {y0 - 4:.0f} {w + 8:.0f} {h + 8:.0f}">{svg}</svg>'})
        parts.append(f'<g transform="translate({cx:.1f},{cy:.1f})">{svg}</g>')
    sheet = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {SHEET_W} {SHEET_H}" width="6.75in" height="9.25in">{"".join(parts)}</svg>'
    proof = check_outlines(outlines)
    json.dump({"sheet_px": [SHEET_W, SHEET_H], "dpi": DPI, "stickers": stickers, "sheet_svg": sheet,
               "proof": proof}, open(os.path.join(HERE, "stickers.json"), "w"))
    print(json.dumps(proof))


def check_outlines(outlines):
    area = box(0, 0, SHEET_W, SHEET_H)
    edge = min(min(o.bounds[0], o.bounds[1], SHEET_W - o.bounds[2], SHEET_H - o.bounds[3]) for o in outlines)
    gap = min(a.distance(b) for i, a in enumerate(outlines) for b in outlines[i + 1:])
    sizes = [((o.bounds[2] - o.bounds[0]) / DPI, (o.bounds[3] - o.bounds[1]) / DPI) for o in outlines]
    return {"count": len(outlines), "inside_area": all(area.contains(o) for o in outlines),
            "min_edge_px": round(edge, 1), "min_gap_px": round(gap, 1),
            "one_piece_each": all(o.geom_type == "Polygon" and not o.interiors for o in outlines),
            "sticker_w_in": [round(min(s[0] for s in sizes), 2), round(max(s[0] for s in sizes), 2)],
            "sticker_h_in": [round(min(s[1] for s in sizes), 2), round(max(s[1] for s in sizes), 2)]}


def check():
    d = json.load(open(os.path.join(HERE, "stickers.json")))
    p = d["proof"]
    ok = (p["count"] == 20 and p["inside_area"] and p["one_piece_each"] and p["min_gap_px"] >= MIN_GAP
          and p["min_edge_px"] >= 15 and d["sheet_px"] == [2025, 2775])
    print(json.dumps(p))
    return ok


if __name__ == "__main__":
    if "--check" in sys.argv:
        sys.exit(0 if check() else 1)
    build()
    sys.exit(0 if check() else 1)
