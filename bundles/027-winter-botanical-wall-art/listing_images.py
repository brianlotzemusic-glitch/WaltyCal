"""Four listing images (3000x2250) from the real art files: wall mockup (code-drawn room), what's included, sizes, close-up."""
import os, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter
W, H = 3000, 2250
NAVY, CREAM, ICE, GOLD, PLUM = (21, 36, 68), (241, 230, 207), (170, 196, 222), (232, 201, 122), (44, 27, 54)
F = lambda n, s: ImageFont.truetype(f"fonts/{n}.ttf", s)
ART = [("pine", "frosted-pine"), ("fern", "frosted-fern"), ("hellebore", "winter-rose")]
os.makedirs("listing-images", exist_ok=True)
def art(n, w, h=None):
    a = Image.open(f"art/unified/{n}.png"); s = w / a.width
    return a.resize((w, round(a.height * s)), Image.LANCZOS)
def shadow(img, box, off=(18, 26), blur=34, op=110):
    s = Image.new("RGBA", img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(s)
    d.rectangle((box[0] + off[0], box[1] + off[1], box[2] + off[0], box[3] + off[1]), fill=(20, 15, 10, op))
    img.alpha_composite(s.filter(ImageFilter.GaussianBlur(blur)))
def frame(img, cx, top, aw, n, wood=(46, 34, 28), mat=(246, 242, 234), matw=70, fw=22):
    a = art(n, aw); ah = a.height
    ow, oh = aw + 2 * (matw + fw), ah + 2 * (matw + fw)
    x0, y0 = cx - ow // 2, top
    shadow(img, (x0, y0, x0 + ow, y0 + oh))
    d = ImageDraw.Draw(img)
    d.rectangle((x0, y0, x0 + ow, y0 + oh), fill=wood)
    d.rectangle((x0 + fw, y0 + fw, x0 + ow - fw, y0 + oh - fw), fill=mat)
    d.rectangle((x0 + fw + matw - 5, y0 + fw + matw - 5, x0 + ow - fw - matw + 5, y0 + oh - fw - matw + 5), fill=(205, 200, 190))
    img.paste(a, (x0 + fw + matw, y0 + fw + matw))
    return oh
def text_c(d, y, t, f, fill, cx=W // 2, sp=0):
    w = d.textlength(t, font=f); d.text((cx - w / 2, y), t, font=f, fill=fill)
def band(img, line1, line2, y=0, h=330):
    d = ImageDraw.Draw(img); d.rectangle((0, y, W, y + h), fill=NAVY)
    d.rectangle((0, y + h, W, y + h + 8), fill=GOLD)
    text_c(d, y + 38, line1, F("Fraunces-900", 128), CREAM)
    text_c(d, y + 205, line2, F("Nunito-800", 62), ICE)
# 1 wall mockup
im = Image.new("RGBA", (W, H), (222, 214, 200, 255)); d = ImageDraw.Draw(im)
for y in range(H):  # soft wall light
    t = y / H; d.line((0, y, W, y), fill=(int(228 - 20 * t), int(220 - 20 * t), int(206 - 20 * t)))
top = 410; cxs = (520, 1500, 2480)
for (n, _), cx in zip(ART, cxs): frame(im, cx, top, 640, n)
d = ImageDraw.Draw(im)
d.rectangle((0, 1960, W, H), fill=(120, 88, 62))            # floor
d.rectangle((0, 1925, W, 1960), fill=(236, 230, 218))       # skirting
d.rectangle((560, 1700, 2440, 1750), fill=(70, 52, 40))     # shelf
d.rectangle((610, 1750, 630, 1880), fill=(70, 52, 40)); d.rectangle((2370, 1750, 2390, 1880), fill=(70, 52, 40))
d.rounded_rectangle((760, 1560, 880, 1700), 14, fill=(246, 240, 226))  # candle
d.rectangle((810, 1530, 830, 1562), fill=(60, 50, 50)); d.ellipse((804, 1488, 836, 1538), fill=GOLD)
d.polygon([(2050, 1700), (2080, 1560), (2210, 1560), (2240, 1700)], fill=(86, 112, 134))  # vase
for dx, dy in ((-70, -170), (0, -230), (80, -190)):
    d.line((2145, 1562, 2145 + dx, 1562 + dy), fill=(70, 96, 80), width=7)
    for k in range(6):
        t = k / 5; px, py = 2145 + dx * t, 1562 + dy * t
        d.ellipse((px - 20, py - 8, px + 20, py + 8), fill=(86, 118, 96))
im = im.filter(ImageFilter.GaussianBlur(0.6)); im = im.convert("RGBA")
band(im, "Winter Wall Art, Set of 3", "Midnight blue botanical prints  ·  printable PDF + JPG  ·  instant download", y=0)
d = ImageDraw.Draw(im); d.rounded_rectangle((2250, 2030, 2900, 2200), 30, fill=NAVY); text_c(d, 2050, "3 prints · 5 ratios", F("Fraunces-900", 56), GOLD, cx=2575); text_c(d, 2125, "up to 24 x 36 in", F("Nunito-800", 44), CREAM, cx=2575)
im.convert("RGB").save("listing-images/1-thumbnail.png")
# 2 what's included
im = Image.new("RGB", (W, H), NAVY); d = ImageDraw.Draw(im)
text_c(d, 70, "What you get", F("Fraunces-900", 120), CREAM)
text_c(d, 215, "3 prints  ·  5 ratios  ·  15 high-res JPGs  ·  5 PDFs", F("Nunito-800", 62), ICE)
aw = 800
for (n, slug), cx in zip(ART, (500, 1500, 2500)):
    a = art(n, aw); im.paste(a, (cx - aw // 2, 330))
    d.rectangle((cx - aw // 2, 330, cx + aw // 2, 330 + a.height), outline=ICE, width=3)
    text_c(d, 330 + a.height + 24, {"pine": "Frosted pine", "fern": "Frosted fern", "hellebore": "Winter rose"}[n], F("Fraunces-700", 60), CREAM, cx=cx)
d.rounded_rectangle((200, 1750, 2800, 2150), 40, fill=(33, 52, 92))
for i, (h1, h2) in enumerate((("15 JPG files", "3 prints in each of 5 ratios, up to 4400 x 6600 px"), ("5 PDF files", "one per ratio, 3 pages, sized for print shops"), ("Print at home or order a print", "any frame, any size from 4 x 6 to 24 x 36 in"))):
    x = 260 + i * 850
    text_c(d, 1790, h1, F("Fraunces-700", 56), GOLD, cx=x + 380); 
    f = F("Nunito-700", 42); words = h2.split(); line = ""; y = 1890
    for w in words:
        if d.textlength(line + w, font=f) > 700: text_c(d, y, line.strip(), f, CREAM, cx=x + 380); y += 62; line = ""
        line += w + " "
    text_c(d, y, line.strip(), f, CREAM, cx=x + 380)
im.save("listing-images/2-whats-included.png")
# 3 sizes
im = Image.new("RGB", (W, H), CREAM); d = ImageDraw.Draw(im)
text_c(d, 60, "Fits every standard frame", F("Fraunces-900", 118), NAVY)
text_c(d, 205, "Five ratios included, so you never have to crop or resize", F("Nunito-800", 58), (74, 44, 85))
R = [("2:3", "4x6  8x12  10x15\n12x18  16x24  20x30  24x36", 2 / 3), ("3:4", "6x8  9x12  12x16\n15x20  18x24", .75), ("4:5", "4x5  8x10\n12x15  16x20", .8), ("11x14", "11x14 in", 11 / 14), ("ISO", "A5  A4  A3  A2\n(1:1.41)", 1 / 1.414)]
for i, (lab, sizes, r) in enumerate(R):
    cx = 300 + i * 600; hh = 700; ww = int(hh * r)
    y0 = 340
    d.rectangle((cx - ww // 2 + 12, y0 + 12, cx + ww // 2 + 12, y0 + hh + 12), fill=(200, 188, 168))
    a = Image.open("art/unified/fern.png"); ar = a.width / a.height
    c = Image.new("RGB", (ww, hh), NAVY); s = min(ww / a.width, hh / a.height); aa = a.resize((round(a.width * s), round(a.height * s)), Image.LANCZOS)
    c.paste(aa, ((ww - aa.width) // 2, (hh - aa.height) // 2)); im.paste(c, (cx - ww // 2, y0))
    d.rectangle((cx - ww // 2, y0, cx + ww // 2, y0 + hh), outline=(46, 34, 28), width=10)
    text_c(d, y0 + hh + 50, lab, F("Fraunces-900", 84), NAVY, cx=cx)
    for k, ln in enumerate(sizes.split("\n")): text_c(d, y0 + hh + 165 + k * 56, ln, F("Nunito-800", 40), (74, 44, 85), cx=cx)
d.rounded_rectangle((200, 1790, 2800, 2170), 40, fill=NAVY)
text_c(d, 1820, "Print-ready files", F("Fraunces-700", 64), GOLD)
for k, ln in enumerate(("JPG at 300 DPI up to 11 x 14 in  ·  large sizes (up to 24 x 36 in) are high-resolution enlargements", "Home printing: pick the ratio closest to your paper and choose 'fit to page'", "Colours look slightly different on screen and on paper")):
    text_c(d, 1920 + k * 75, ln, F("Nunito-700", 44), CREAM)
im.save("listing-images/3-sizes.png")
# 4 close-up
im = Image.new("RGB", (W, H), NAVY); d = ImageDraw.Draw(im)
a = Image.open("art/unified/hellebore.png"); big = a.crop((500, 300, 2700, 2000)).resize((1650, 1275), Image.LANCZOS)
im.paste(big, (90, 480)); d.rectangle((90, 480, 1740, 1755), outline=GOLD, width=6)
b = Image.open("art/unified/pine.png").crop((600, 500, 1600, 1500)).resize((1000, 1000)); im.paste(b, (1850, 480)); d.rectangle((1850, 480, 2850, 1480), outline=GOLD, width=6)
text_c(d, 70, "Fine detail, soft midnight blue", F("Fraunces-900", 118), CREAM)
text_c(d, 215, "Detailed botanical drawings in cool blue, silver and cream", F("Nunito-800", 58), ICE)
text_c(d, 1530, "Pine needles, cones and frosted berries", F("Nunito-800", 42), CREAM, cx=2350)
text_c(d, 1790, "Winter rose, close up", F("Nunito-800", 42), CREAM, cx=915)
d.rounded_rectangle((200, 1930, 2800, 2150), 40, fill=(33, 52, 92))
text_c(d, 1960, "Calm, cool-toned art for a bedroom, hallway, nursery or winter mantel", F("Nunito-800", 50), CREAM)
text_c(d, 2050, "Instant digital download  ·  no physical item is shipped", F("Nunito-700", 44), ICE)
im.save("listing-images/4-closeup.png")
