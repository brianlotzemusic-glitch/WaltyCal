"""008 Christmas bow tee: code-drawn satin bow, cranberry with blush highlights and gold-thread edge, cream pearls.
Free, deterministic. Output 4500x5100 transparent PNG (design ~11.5 in wide)."""
import os, math
from PIL import Image, ImageDraw, ImageFilter
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "008-christmas-bow-tee")
S = 4  # supersample over 1000-unit design box -> design drawn at 1000*S*... scaled below
U = 8  # px per unit while drawing (design box 1000x1100 -> 8000x8800)
W, H = 1000*U, 1100*U

def bez(p0, p1, p2, p3, n=60):
    return [tuple((1-t)**3*a + 3*(1-t)**2*t*b + 3*(1-t)*t**2*c + t**3*d for a, b, c, d in zip(p0, p1, p2, p3))
            for t in [i/n for i in range(n+1)]]
def path(*segs):
    pts = []
    for s in segs: pts += bez(*s)
    return pts
def mir(pts): return [(1000-x, y) for x, y in pts]
def sc(pts): return [(x*U, y*U) for x, y in pts]

# loop (left): outer, inner opening
outer = path(((478,505),(330,300),(90,250),(70,470)), ((70,470),(55,640),(250,720),(478,585)))
inner = path(((440,515),(330,380),(170,350),(150,470)), ((150,470),(145,590),(290,640),(440,568)))
# tails
tailL = [(450,560),(548,590)] + bez((548,590),(520,780),(470,930),(400,1060),20) + [(345,985)] + bez((345,985),(300,960),(280,940),(262,925),2)[1:] 
tailL = [(452,560),(548,592),(500,820),(420,1065),(350,985),(262,1060),(318,820),(400,690)]
tailL = bez((452,560),(430,700),(330,860),(262,1060),30) + [(335,985)] + [(420,1068)] + bez((420,1068),(490,900),(540,740),(548,592),30)
tailL = [p for p in tailL]
knot = [(452,500),(548,500),(560,545),(548,600),(452,600),(440,545)]

def build(draw, fill_main, fill_hi, fill_sh, fill_in):
    for m in (lambda p: p, mir):
        draw.polygon(sc(m(tailL)), fill=fill_main)
        draw.polygon(sc(m(outer)), fill=fill_main)
        draw.polygon(sc(m(inner)), fill=fill_in)
    draw.polygon(sc(knot), fill=fill_main)

CRAN, HI, SH, IN = (196, 44, 70, 255), (232, 96, 118, 255), (132, 22, 50, 255), (104, 14, 42, 255)
# gold edge via dilated union mask
m = Image.new("L", (W, H), 0); md = ImageDraw.Draw(m); build(md, 255, 255, 255, 255)
edge = m.resize((W//4, H//4), Image.LANCZOS).filter(ImageFilter.MaxFilter(2*8+1)).resize((W, H), Image.LANCZOS).point(lambda v: 255 if v > 100 else 0).filter(ImageFilter.GaussianBlur(2))
im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
im.paste(Image.new("RGBA", (W, H), (226, 188, 112, 255)), (0, 0), edge)
d = ImageDraw.Draw(im)
build(d, CRAN, HI, SH, IN)
# shading: highlights along loop crowns, shadow under knot, fold lines on tails
for mm in (lambda p: p, mir):
    d.line(sc(mm(path(((470,495),(340,310),(110,280),(88,440))))), fill=HI, width=48, joint="curve")
    d.line(sc(mm(path(((470,590),(300,700),(120,660),(100,560))))), fill=SH, width=34, joint="curve")
    d.line(sc(mm(bez((470,590),(440,720),(360,880),(300,1030),30))), fill=SH, width=20)
    d.line(sc(mm(bez((520,610),(490,760),(430,900),(375,1010),30))), fill=HI, width=26)
    d.line(sc(mm(bez((462,520),(380,470),(300,430),(240,420),30))), fill=HI, width=10)
d.polygon(sc(knot), fill=CRAN)
d.line(sc([(462,512),(538,512)]), fill=HI, width=26); d.line(sc([(460,590),(540,590)]), fill=SH, width=22)
d.line(sc([(500,505),(500,595)]), fill=SH, width=10)
# gold stitch dashes along loops
def dashes(pts, on=3, off=3):
    for i in range(0, len(pts)-on, on+off):
        d.line(sc(pts[i:i+on+1]), fill=(240, 214, 150, 255), width=9)
dashes(path(((455,520),(340,330),(130,300),(105,470)), ((105,470),(95,610),(260,690),(455,570))), 2, 2)
dashes(mir(path(((455,520),(340,330),(130,300),(105,470)), ((105,470),(95,610),(260,690),(455,570)))), 2, 2)
# pearls
pearls = [(120,235,22),(60,350,15),(30,500,12),(880,235,22),(940,350,15),(970,500,12),(500,330,18),(240,1010,16),(760,1010,16)]
for x, y, r in pearls:
    cx, cy, R = x*U, y*U, r*U
    d.ellipse([cx-R-10, cy-R-10, cx+R+10, cy+R+10], fill=(226, 188, 112, 255))
    d.ellipse([cx-R, cy-R, cx+R, cy+R], fill=(250, 242, 228, 255))
    d.ellipse([cx-R*0.55, cy-R*0.6, cx-R*0.1, cy-R*0.15], fill=(255, 255, 255, 255))
bb = im.getbbox(); im = im.crop(bb)
tw = int(11.5*300); th = round(im.height*tw/im.width)
im = im.resize((tw, th), Image.LANCZOS)
out = Image.new("RGBA", (4500, 5100), (0, 0, 0, 0))
out.paste(im, ((4500-tw)//2, 300), im)
os.makedirs(D, exist_ok=True)
out.save(os.path.join(D, "tee-front-4500x5100.png"), dpi=(300, 300))
print(im.size, out.getbbox())
bgs = {"black": (20,20,20), "navy": (28,38,66), "heather": (62,62,66), "asphalt": (78,80,82)}
sheet = Image.new("RGB", (1600, 400))
for i, c in enumerate(bgs.values()):
    t = Image.new("RGB", (400, 400), c); s = out.resize((353, 400)); t.paste(s, (23, 0), s); sheet.paste(t, (i*400, 0))
sheet.save("/tmp/claude-0/-home-user-WaltyCal/d2f7716a-a41f-5857-88c6-c344e17540fd/scratchpad/sheet8.png")
