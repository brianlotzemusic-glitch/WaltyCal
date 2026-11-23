B="#4FA3D9";K="#000"
def bars(x0,x1,cy,hs,w=14,fill=B):
    n=len(hs);step=(x1-x0)/(n-1)
    return "".join(f'<rect x="{x0+i*step-w/2:.1f}" y="{cy-h/2:.1f}" width="{w}" height="{h}" rx="{w/2}" fill="{fill}"/>' for i,h in enumerate(hs))
av={}
# 1 monogram
av[1]=f'''<rect width="600" height="600" fill="#fff"/><circle cx="300" cy="300" r="270" fill="{K}"/>
<text x="300" y="352" text-anchor="middle" font-family="Osw" font-weight="700" font-size="250" fill="#fff" letter-spacing="4">HB</text>
{bars(150,450,430,[18,34,52,34,64,40,22,46,28,16],w=14)}'''
# 2 H built from bars
hs=[260,260,260]
av[2]=f'''<rect width="600" height="600" fill="#fff"/><circle cx="300" cy="300" r="270" fill="none" stroke="{K}" stroke-width="14"/>
<rect x="165" y="160" width="46" height="280" rx="23" fill="{K}"/><rect x="389" y="160" width="46" height="280" rx="23" fill="{K}"/>
{bars(222,378,300,[40,90,150,90,40],w=16)}'''
# 3 river S-curve with waveform in circle
av[3]=f'''<defs><clipPath id="c"><circle cx="300" cy="300" r="270"/></clipPath></defs>
<rect width="600" height="600" fill="#fff"/><g clip-path="url(#c)"><rect width="600" height="600" fill="#fff"/>
<path d="M-20,250 C120,170 230,330 300,300 S470,230 620,300 L620,620 L-20,620 Z" fill="{B}"/>
<path d="M-20,250 C120,170 230,330 300,300 S470,230 620,300" fill="none" stroke="{K}" stroke-width="14" stroke-linecap="round"/>
{bars(130,470,440,[20,44,70,44,88,56,30,60,34,18],w=16,fill="#fff")}</g>
<circle cx="300" cy="300" r="270" fill="none" stroke="{K}" stroke-width="14"/>'''
# 4 sun over hills badge
av[4]=f'''<defs><clipPath id="c"><circle cx="300" cy="300" r="270"/></clipPath></defs>
<rect width="600" height="600" fill="#fff"/><g clip-path="url(#c)">
<circle cx="360" cy="215" r="70" fill="{B}" stroke="{K}" stroke-width="12"/>
<path d="M-20,360 C80,280 200,250 300,300 S480,330 620,260 L620,620 L-20,620Z" fill="#fff" stroke="{K}" stroke-width="12" stroke-linejoin="round"/>
<path d="M-20,400 C90,330 200,310 300,350 S480,380 620,320" fill="none" stroke="{K}" stroke-width="7"/>
<path d="M-20,440 C90,380 200,360 300,400 S480,430 620,380" fill="none" stroke="{K}" stroke-width="7"/>
<rect x="-20" y="440" width="640" height="180" fill="{B}"/><line x1="-20" y1="440" x2="620" y2="440" stroke="{K}" stroke-width="12"/>
{bars(150,450,510,[16,30,46,30,56,34,18],w=12,fill="#fff")}</g>
<circle cx="300" cy="300" r="270" fill="none" stroke="{K}" stroke-width="14"/>'''
# 5 headphones
av[5]=f'''<rect width="600" height="600" fill="#fff"/><circle cx="300" cy="300" r="270" fill="#fff" stroke="{K}" stroke-width="14"/>
<path d="M135,330 C135,140 465,140 465,330" fill="none" stroke="{K}" stroke-width="26" stroke-linecap="round"/>
<rect x="108" y="300" width="84" height="170" rx="34" fill="{B}" stroke="{K}" stroke-width="14"/>
<rect x="408" y="300" width="84" height="170" rx="34" fill="{B}" stroke="{K}" stroke-width="14"/>
{bars(236,364,390,[26,60,92,60,26],w=14,fill=K)}'''
html='<!doctype html><html><head><style>@font-face{font-family:Osw;font-weight:700;src:url(oswald-latin-700-normal.woff2)}body{margin:0;background:#fff}div{width:600px;height:600px}</style></head><body>'
for k,v in av.items(): html+=f'<div id="a{k}"><svg xmlns="http://www.w3.org/2000/svg" width="600" height="600" viewBox="0 0 600 600">{v}</svg></div>'
open("av.html","w").write(html+'</body></html>')
for k,v in av.items(): open(f"avatar-{k}.svg","w").write(f'<svg xmlns="http://www.w3.org/2000/svg" width="600" height="600" viewBox="0 0 600 600">{v}</svg>')
