import math
BLUE="#4FA3D9"; K="#000"; SW=6
def cr(pts, closed=False, t=0.5):
    # Catmull-Rom -> cubic bezier path (smooth, no kinks)
    P=pts
    d=f"M{P[0][0]:.1f},{P[0][1]:.1f}"
    n=len(P)
    for i in range(n-1):
        p0=P[i-1] if i>0 else P[i]; p1=P[i]; p2=P[i+1]; p3=P[i+2] if i+2<n else P[i+1]
        c1=(p1[0]+(p2[0]-p0[0])*t/3*2*0.5*1.0, p1[1]+(p2[1]-p0[1])*t/3*2*0.5*1.0)
        c2=(p2[0]-(p3[0]-p1[0])*t/3*2*0.5*1.0, p2[1]-(p3[1]-p1[1])*t/3*2*0.5*1.0)
        d+=f" C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}"
    return d
W,H=1100,600; RIVER=412
out=[]
defs=[]
def ridge(idx, pts, shifts, fill="#fff"):
    top=cr(pts)
    shape=top+f" L{pts[-1][0]},{RIVER+10} L{pts[0][0]},{RIVER+10} Z"
    defs.append(f'<clipPath id="r{idx}"><path d="{shape}"/></clipPath>')
    s=f'<path d="{shape}" fill="{fill}"/>'
    s+=f'<g clip-path="url(#r{idx})" fill="none" stroke="{K}" stroke-width="3.6" stroke-linecap="round">'
    for dy in shifts:
        s+=f'<path d="{cr([(x,y+dy) for x,y in pts])}"/>'
    s+='</g>'
    s+=f'<path d="{top}" fill="none" stroke="{K}" stroke-width="{SW}" stroke-linejoin="round" stroke-linecap="round"/>'
    return s
A=[(-20,300),(100,250),(230,196),(370,236),(500,208),(640,262),(800,330)]
B=[(-20,370),(90,318),(210,288),(340,326),(470,362),(620,396),(800,420)]
out.append(f'<circle cx="470" cy="170" r="62" fill="#fff" stroke="{K}" stroke-width="{SW}"/><circle cx="470" cy="170" r="40" fill="{BLUE}"/>')
out.append(ridge(0,A,[20,40,60,80,100]))
out.append(ridge(1,B,[18,36,54]))
# cliffs (Palisades)
top=[(742,422),(748,300),(776,250),(800,206),(890,184),(1000,156),(1120,138)]
cl=cr(top)+f" L1120,{RIVER+10} L742,{RIVER+10} Z"
defs.append(f'<clipPath id="cl"><path d="{cl}"/></clipPath>')
s=f'<path d="{cl}" fill="#fff"/><g clip-path="url(#cl)" stroke="{K}" stroke-width="3.6" stroke-linecap="round">'
x=782
k=0
def topy(x):
    # approximate top edge y by linear interpolation of points
    for (x0,y0),(x1,y1) in zip(top,top[1:]):
        if x0<=x<=x1: return y0+(y1-y0)*(x-x0)/(x1-x0)
    return 150
lens=[0.0,0.28,0.12,0.46,0.2,0.36,0.08,0.5,0.24,0.4,0.14,0.3]
while x<1110:
    y0=topy(x)+20
    y1=RIVER-8-lens[k%len(lens)]*120
    s+=f'<line x1="{x}" y1="{y0:.1f}" x2="{x}" y2="{y1:.1f}"/>'
    x+=36;k+=1
s+='</g>'
s+=f'<path d="{cr(top)}" fill="none" stroke="{K}" stroke-width="{SW}" stroke-linejoin="round" stroke-linecap="round"/>'
out.append(s)
# river
out.append(f'<rect x="0" y="{RIVER}" width="{W}" height="{H-RIVER}" fill="{BLUE}"/><line x1="0" y1="{RIVER}" x2="{W}" y2="{RIVER}" stroke="{K}" stroke-width="{SW}"/>')
# waveform bars (white, rounded)
cy=506
bars=""
n=0
for x in range(44,1070,22):
    env=math.exp(-((x-640)/300)**2)
    wob=0.55+0.45*abs(math.sin(x*0.071+0.8))
    h=10+96*env*wob+8*abs(math.sin(x*0.19))
    bars+=f'<rect x="{x-5}" y="{cy-h/2:.1f}" width="10" height="{h:.1f}" rx="5" fill="#fff"/>'
out.append(bars)
# sailboat
bx,by=235,RIVER+2
boat=f'''<g stroke="{K}" stroke-width="4.5" stroke-linejoin="round" stroke-linecap="round">
<path d="M{bx-48},{by+22} L{bx+52},{by+22} L{bx+34},{by+46} L{bx-30},{by+46} Z" fill="#fff"/>
<line x1="{bx}" y1="{by+22}" x2="{bx}" y2="{by-76}"/>
<path d="M{bx},{by-70} L{bx},{by+14} L{bx+48},{by+14} Z" fill="#fff"/>
<path d="M{bx},{by-52} L{bx},{by+14} L{bx-40},{by+14} Z" fill="{BLUE}"/></g>'''
out.append(boat)
svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}"><defs>{"".join(defs)}</defs><rect width="{W}" height="{H}" fill="#fff"/>{"".join(out)}</svg>'
open("river.svg","w").write(svg)
