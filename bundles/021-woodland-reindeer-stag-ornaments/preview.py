"""Low-res contact sheet straight from the shapely geometry (self-check only)."""
import sys
from PIL import Image, ImageDraw
import gen

def raster(g, size=300):
    x0, y0, x1, y1 = g.bounds
    sc = (size - 20) / max(x1 - x0, y1 - y0)
    im = Image.new("L", (size, size), 255)
    d = ImageDraw.Draw(im)
    f = lambda c: [((x - x0) * sc + 10, (y - y0) * sc + 10) for x, y in c]
    polys = g.geoms if g.geom_type == "MultiPolygon" else [g]
    for p in polys:
        d.polygon(f(p.exterior.coords), fill=0)
        for i in p.interiors:
            d.polygon(f(i.coords), fill=255)
    return im

if __name__ == "__main__":
    names = [n for n in gen.DESIGNS if not sys.argv[2:] or any(o in n for o in sys.argv[2:])]
    size = 360
    sheet = Image.new("L", (size * min(3, len(names)), size * ((len(names) + 2) // 3)), 255)
    for k, n in enumerate(names):
        g = gen.finish(gen.DESIGNS[n]())
        print(n, gen.stats(g))
        sheet.paste(raster(g, size), ((k % 3) * size, (k // 3) * size))
    sheet.save(sys.argv[1])
