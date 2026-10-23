import sys, importlib
from PIL import Image, ImageDraw
import birds
from lib import *
def raster(g, size=700):
    x0,y0,x1,y1 = 0,0,1000,1000
    sc = size/1000
    im = Image.new("L",(size,size),255); d = ImageDraw.Draw(im)
    f = lambda c: [(x*sc,y*sc) for x,y in c]
    for p in (g.geoms if g.geom_type=="MultiPolygon" else [g]):
        d.polygon(f(p.exterior.coords), fill=0)
        for i in p.interiors: d.polygon(f(i.coords), fill=255)
    return im
names = sys.argv[2:]
ims=[]
for n in names:
    g = finish(getattr(birds,n)()) if n.startswith("d_") else fit(getattr(birds,n)())
    print(n, stats(g) if n.startswith("d_") else g.bounds)
    ims.append(raster(g))
sheet = Image.new("L",(700*len(ims),700),255)
for k,i in enumerate(ims): sheet.paste(i,(700*k,0))
sheet.save(sys.argv[1])
