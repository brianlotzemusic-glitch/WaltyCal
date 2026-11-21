"""Drawings for the poster set (TpT 068). Every diagram is drawn in code as inline SVG.

Each plotted drawing carries data-* attributes (axis boxes and ranges) and its curves carry class "cv" so that
`gen.py --check` can read the real geometry back from the rendered HTML and recompute every plotted point itself.
"""
import math

K = "#000"
ACC = "#2F86B8"
TINT = "#DCEEF8"
GR = "#E4E4E4"
MID = "#6A6A6A"
SS = "Source Sans 3"
OS = "Oswald"
W = 720


def n(v):
    return f"{v:.2f}".rstrip("0").rstrip(".")


class Sv:
    def __init__(s, h, kind, w=W, **meta):
        s.w, s.h, s.kind, s.meta, s.parts = w, h, kind, meta, []

    def line(s, x1, y1, x2, y2, sw=1.6, col=K, dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        s.parts.append(f'<line x1="{n(x1)}" y1="{n(y1)}" x2="{n(x2)}" y2="{n(y2)}" stroke="{col}" stroke-width="{sw}" stroke-linecap="round"{d}/>')

    def rect(s, x, y, w, h, fill="none", sw=1.6, rx=0, col=K, dash=None, cls=""):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        c = f' class="{cls}"' if cls else ""
        st = f'stroke="{col}" stroke-width="{sw}"' if sw else 'stroke="none"'
        s.parts.append(f'<rect{c} x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" rx="{rx}" fill="{fill}" {st}{d}/>')

    def circ(s, cx, cy, r, fill="none", sw=1.6, col=K, cls=""):
        c = f' class="{cls}"' if cls else ""
        st = f'stroke="{col}" stroke-width="{sw}"' if sw else 'stroke="none"'
        s.parts.append(f'<circle{c} cx="{n(cx)}" cy="{n(cy)}" r="{n(r)}" fill="{fill}" {st}/>')

    def poly(s, pts, sw=1.8, fill="none", col=K, closed=False, dash=None, cls=""):
        if not closed and fill != "none" and col == K:
            col, fill = fill, "none"      # open lines are never filled: poly(pts, sw, colour)
        tag = "polygon" if closed else "polyline"
        d = f' stroke-dasharray="{dash}"' if dash else ""
        c = f' class="{cls}"' if cls else ""
        p = " ".join(f"{n(x)},{n(y)}" for x, y in pts)
        st = f'stroke="{col}" stroke-width="{sw}" stroke-linejoin="round" stroke-linecap="round"' if sw else 'stroke="none"'
        s.parts.append(f'<{tag}{c} points="{p}" fill="{fill}" {st}{d}/>')

    def text(s, x, y, t, size=15, anchor="start", weight=600, fill=K, font=SS, italic=False, halo=False):
        it = ' font-style="italic"' if italic else ""
        h = ' stroke="#fff" stroke-width="4" paint-order="stroke" stroke-linejoin="round"' if halo else ""
        s.parts.append(f'<text x="{n(x)}" y="{n(y)}" font-family="{font}" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}" fill="{fill}"{it}{h}>{t}</text>')

    def arrow(s, x1, y1, x2, y2, sw=1.8, col=K, head=9):
        ang = math.atan2(y2 - y1, x2 - x1)
        bx, by = x2 - head * math.cos(ang), y2 - head * math.sin(ang)
        s.line(x1, y1, bx, by, sw, col)
        px, py = -math.sin(ang), math.cos(ang)
        s.poly([(x2, y2), (bx + px * head * 0.5, by + py * head * 0.5), (bx - px * head * 0.5, by - py * head * 0.5)], sw=0, fill=col, closed=True)

    def svg(s):
        meta = "".join(f' data-{k}="{v}"' for k, v in s.meta.items())
        return (f'<svg class="dg" data-kind="{s.kind}"{meta} viewBox="0 0 {s.w} {s.h}" width="100%" style="display:block;margin:0 auto" '
                f'xmlns="http://www.w3.org/2000/svg">{"".join(s.parts)}</svg>')


# ---------------------------------------------------------------- formulas (used to draw; --check recomputes with its own copies)
def comp_out(x, thr, ratio):
    return x if x <= thr else thr + (x - thr) / ratio


def limit_out(x, ceil):
    return min(x, ceil)


def eq_gain(f, bells):
    return sum(g * math.exp(-(math.log2(f / fc)) ** 2 / (2 * 0.6 ** 2)) for fc, g in bells)


def hp_db(f, fc):
    return -10 * math.log10(1 + (fc / f) ** 4)


def lp_db(f, fc):
    return -10 * math.log10(1 + (f / fc) ** 4)


EQ_BELLS = [(150, -4.0), (2000, 5.0)]
COMP_THR, COMP_RATIO = -20, 4
LIM_CEIL = -3
HP_FC, LP_FC = 100, 8000
BPMS = [60, 90, 120, 150]
QUANT_BEFORE = [0.08, 0.57, 0.93, 1.54, 2.06, 2.46, 3.1, 3.43]
QUANT_GRID = 0.5
VELS = [40, 64, 96, 127]
RT60 = 1.5
DELAY_MS = [0, 500, 1000, 1500]
DELAY_AMP = [1.0, 0.5, 0.25, 0.125]
PAN_VALUES = [("Guitar", -100), ("Vocal", 0), ("Keys", 50)]
AUTO_PTS = [(1, None), (3, 0), (7, 0), (8, -12), (9, -12), (11, 0), (13, None)]
FADER_TICKS = [(6, 0.0), (0, 0.2), (-6, 0.36), (-12, 0.5), (-24, 0.72), (-48, 0.92)]
MIX_CAPS = [("Drums", -4), ("Bass", -6), ("Vocal", 0)]
FREQS = [100, 200, 400]
PIANO_NOTES = [(0, 0, 2), (4, 2, 2), (7, 4, 2), (12, 6, 2)]   # (semitones above C4, start column, columns long)
PIANO_BLACK = [0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0, 0]


def fader_pos(db):
    """0 = top of the fader slot, 1 = bottom; piecewise linear between the printed marks."""
    pts = FADER_TICKS
    for (d1, p1), (d2, p2) in zip(pts, pts[1:]):
        if d2 <= db <= d1:
            return p1 + (p2 - p1) * (d1 - db) / (d1 - d2)
    raise ValueError(db)


# ---------------------------------------------------------------- shared bits
def ruler(s, x0, x1, y, count, step_label=1, first=1, size=14, h=10):
    bw = (x1 - x0) / count
    for i in range(count + 1):
        s.line(x0 + i * bw, y, x0 + i * bw, y + h, 1.4)
    for i in range(count):
        if i % step_label == 0:
            s.text(x0 + i * bw + bw / 2, y - 5, str(first + i), size, "middle", 600)
    s.line(x0, y + h, x1, y + h, 1.6)
    return bw


def kbd_small(s, x0, y0, kw=30, kh=104):
    for i in range(8):
        s.rect(x0 + i * kw, y0, kw, kh, "#fff", 1.6, 0, cls="wk")
    s.rect(x0, y0, kw, kh, TINT, 1.6)
    for i in (0, 1, 3, 4, 5):
        s.rect(x0 + (i + 1) * kw - 9, y0, 18, kh * 0.62, K, 1.2)


def wave_pts(x0, x1, yc, amp, f, phase=0.0, env=None, count=220):
    out = []
    for i in range(count + 1):
        t = i / count
        e = env(t) if env else 1.0
        out.append((x0 + t * (x1 - x0), yc - amp * e * math.sin(2 * math.pi * f * t + phase)))
    return out


def label_box(s, x, y, w, h, txt, size=15, fill="#fff", weight=600):
    s.rect(x, y, w, h, fill, 1.6, 5)
    s.text(x + w / 2, y + h / 2 + size * 0.35, txt, size, "middle", weight)


def speaker(s, x, y, size=26):
    s.poly([(x, y + size * 0.3), (x + size * 0.35, y + size * 0.3), (x + size * 0.75, y), (x + size * 0.75, y + size), (x + size * 0.35, y + size * 0.7), (x, y + size * 0.7)], 1.6, "#fff", closed=True)
    s.poly([(x + size * 0.95, y + size * 0.3), (x + size * 1.1, y + size * 0.5), (x + size * 0.95, y + size * 0.7)], 1.6)


# ================================================================ 1 DAW
def d_daw():
    s = Sv(360, "daw")
    s.rect(14, 14, 692, 332, "#fff", 2, 8)
    s.line(14, 62, 706, 62, 1.6)
    s.poly([(36, 28), (36, 48), (54, 38)], 1.6, K, closed=True)
    s.rect(70, 29, 18, 18, K, 1.6)
    s.circ(114, 38, 10, ACC, 1.6)
    s.text(140, 45, "TRANSPORT", 16, "start", 700, K, OS)
    label_box(s, 560, 26, 130, 28, "120 BPM", 17)
    s.line(190, 62, 190, 250, 1.6)
    s.text(28, 84, "TRACKS", 14, "start", 700, MID, OS)
    names = [("Drums", ACC), ("Bass", None), ("Vocal", None)]
    bw = (700 - 198) / 8
    s.text(204, 77, "TIMELINE", 14, "start", 700, MID, OS)
    for i in range(8):
        s.line(198 + i * bw, 90, 198 + i * bw, 98, 1.2)
        s.text(198 + i * bw + 6, 88, str(i + 1), 13, "start", 600)
    rows = [(104, [(0, 3), (4, 7)]), (152, [(1, 5)]), (200, [(2, 4), (5, 8)])]
    for (y, regs), (nm, c) in zip(rows, names):
        s.rect(26, y, 150, 40, "#fff", 1.6, 5)
        s.text(38, y + 25, nm, 16, "start", 700)
        s.rect(112, y + 10, 20, 20, "#fff", 1.4, 3)
        s.text(122, y + 25, "M", 13, "middle", 700)
        s.rect(138, y + 10, 20, 20, "#fff", 1.4, 3)
        s.text(148, y + 25, "S", 13, "middle", 700)
        s.line(190, y + 44, 706, y + 44, 1.0, MID)
        for a, b in regs:
            s.rect(198 + a * bw, y + 4, (b - a) * bw - 4, 32, TINT if c else GR, 1.6, 4)
    s.line(14, 250, 706, 250, 1.6)
    s.text(28, 276, "MIXER", 14, "start", 700, MID, OS)
    for i, (x, nm) in enumerate(((250, "Drums"), (400, "Bass"), (550, "Vocal"))):
        s.line(x, 262, x, 334, 3)
        s.rect(x - 11, 278 + i * 8, 22, 14, ACC, 1.6, 3)
        s.text(x + 22, 304, nm, 14, "start", 600)
    return s


# ================================================================ 2 Track
def d_track():
    s = Sv(340, "track")
    s.text(28, 34, "Each lane is one track", 17, "start", 700, K, OS)
    lanes = [("Lead vocal", "Audio track", "wave"), ("Guitar", "Audio track", "wave"), ("Piano", "MIDI track", "notes"), ("Drums", "MIDI track", "notes")]
    for i, (nm, ty, kind) in enumerate(lanes):
        y = 52 + i * 64
        s.rect(20, y, 680, 54, "#fff", 1.6, 6)
        s.rect(20, y, 200, 54, GR, 1.6, 6)
        s.text(34, y + 24, nm, 17, "start", 700)
        s.text(34, y + 44, ty, 14, "start", 400)
        s.rect(160, y + 12, 22, 22, "#fff", 1.4, 3)
        s.text(171, y + 28, "M", 13, "middle", 700)
        s.rect(188, y + 12, 22, 22, "#fff", 1.4, 3)
        s.text(199, y + 28, "S", 13, "middle", 700)
        rx, rw = 250, 420
        s.rect(rx, y + 6, rw, 42, TINT if kind == "wave" else "#fff", 1.6, 4)
        if kind == "wave":
            pts = wave_pts(rx + 10, rx + rw - 10, y + 27, 16, 14 + i * 3, 0, lambda t: 0.35 + 0.65 * abs(math.sin(math.pi * (t * 3 + i))), 200)
            s.poly(pts, 1.4)
        else:
            for j in range(10):
                nx = rx + 14 + j * 40
                ny = y + 14 + ((j * 7 + i * 5) % 4) * 8
                s.rect(nx, ny, 26, 6, ACC, 1.2, 2)
    s.text(20, 326, "M = mute (silence this track)   S = solo (hear only this track)", 15, "start", 400)
    return s


# ================================================================ 3 Region
def d_region():
    s = Sv(340, "region", bars=16, rx0=60, rx1=700)
    x0, x1 = 60, 700
    bw = ruler(s, x0, x1, 46, 16, 1, 1)
    s.text(14, 30, "Bar", 14, "start", 700, MID, OS)
    s.text(14, 112, "Drums", 15, "start", 700)
    for i in range(4):
        a = x0 + i * 4 * bw
        s.rect(a + 2, 78, 4 * bw - 4, 56, TINT if i == 0 else "#fff", 1.8, 5)
        s.text(a + 12, 100, "Drum groove" if i == 0 else "copy", 15, "start", 600)
        for j in range(8):
            s.rect(a + 14 + j * (4 * bw - 28) / 8, 112, 8, 12, K, 0, 1)
    s.text(14, 192, "Bass", 15, "start", 700)
    s.rect(x0 + 4 * bw + 2, 160, 8 * bw - 4, 56, "#fff", 1.8, 5)
    s.text(x0 + 4 * bw + 12, 182, "Bass line (8 bars, bars 5 to 12)", 15, "start", 600)
    for j in range(5):
        s.rect(x0 + 4 * bw + 16 + j * 56, 194, 40, 10, ACC, 1.2, 2)
    s.arrow(x0 + 4 * bw - 3, 236, x0 + 4 * bw - 3, 140, 1.8)
    s.text(x0 + 4 * bw - 14, 252, "drag an edge to trim", 15, "end", 600)
    s.arrow(x0 + 4 * bw + 20, 272, x0 + 4 * bw + 200, 272, 1.8)
    s.text(x0 + 4 * bw + 20, 296, "drag the block to move it", 15, "start", 600)
    s.text(x1 - 4, 318, "4 bars x 4 = 16 bars", 15, "end", 600)
    return s


# ================================================================ 4 Loop
def d_loop():
    s = Sv(360, "loop", bars=12, rx0=40, rx1=700, loop=(5, 9))
    x0, x1 = 40, 700
    s.text(14, 28, "A. Loop part of the timeline", 17, "start", 700, K, OS)
    bw = (x1 - x0) / 12
    ruler(s, x0, x1, 60, 12, 1, 1)
    s.rect(x0 + 4 * bw, 70, 4 * bw, 70, TINT, 0)
    s.line(x0 + 4 * bw, 70, x0 + 8 * bw, 70, 5, ACC)
    s.line(x0 + 4 * bw, 70, x0 + 4 * bw, 140, 1.6, ACC)
    s.line(x0 + 8 * bw, 70, x0 + 8 * bw, 140, 1.6, ACC)
    s.line(x0, 140, x1, 140, 1.4, MID)
    s.text(x0 + 6 * bw, 108, "loop: bars 5 to 8", 17, "middle", 700)
    s.text(x0 + 6 * bw, 130, "(4 bars, plays again and again)", 14, "middle", 400)
    for i in range(12):
        if i < 4 or i >= 8:
            s.rect(x0 + i * bw + 4, 82, bw - 8, 18, GR, 1.2, 3)
    s.text(14, 190, "B. Loop as a repeating pattern (1 bar, repeated 4 times)", 17, "start", 700, K, OS)
    px0, pw = 40, 165
    for r in range(4):
        a = px0 + r * pw
        s.rect(a + 2, 206, pw - 4, 70, "#fff" if r else TINT, 1.8, 5)
        for j in range(8):
            s.circ(a + 16 + j * 18.5, 252 if j % 2 == 0 else 232, 5.5, K if j % 4 == 0 else ACC, 0)
        if r < 3:
            s.line(a + pw, 202, a + pw, 280, 1.4, MID, "4 4")
    s.text(px0 + 2 * pw, 306, "The end joins the start with no gap, so it can repeat forever.", 16, "middle", 600)
    return s


# ================================================================ 5 BPM
def d_bpm():
    bpm = 120
    s = Sv(360, "bpm", bpm=bpm, tx0=70, tx1=670)
    x0, x1 = 70, 670
    spb = 60 / bpm
    ppx = (x1 - x0) / 2.0
    s.text(14, 28, "120 BPM on a time line (seconds)", 17, "start", 700, K, OS)
    s.line(x0, 100, x1, 100, 2)
    for i in range(5):
        x = x0 + i * spb * ppx
        s.line(x, 84, x, 116, 2.2)
        s.text(x, 140, f"{i * spb:.1f} s", 16, "middle", 600)
        if i < 4:
            s.circ(x + spb * ppx / 2, 70, 15, ACC if i == 0 else "#fff", 1.8)
            s.text(x + spb * ppx / 2, 76, str(i + 1), 16, "middle", 700, "#fff" if i == 0 else K)
    s.text(x0 + 2 * ppx / 2, 172, "1 bar = 4 beats = 2 seconds", 17, "middle", 700)
    s.line(x0, 158, x1, 158, 1.4, MID)
    s.text(14, 214, "Seconds per beat = 60 ÷ BPM", 17, "start", 700, K, OS)
    for i, b in enumerate(BPMS):
        y = 232 + i * 30
        sec = 60 / b
        s.text(14, y + 16, f"{b} BPM", 16, "start", 700)
        s.rect(100, y, sec * 440, 22, TINT if b == 120 else "#fff", 1.6, 3, cls="sb")
        s.text(100 + sec * 440 + 12, y + 17, f"{sec:.2f} s per beat", 15, "start", 600)
    return s


# ================================================================ 6 Quantize
def d_quant():
    s = Sv(360, "quant", gx0=60, gx1=690, beats=4, grid=QUANT_GRID)
    x0, x1 = 60, 690
    ppb = (x1 - x0) / 4
    for title, y0, snapped in (("Before: played a little early or late", 40, False), ("After: quantized to eighth notes", 210, True)):
        s.text(14, y0 - 8, title, 17, "start", 700, K, OS)
        s.rect(x0 - 10, y0, x1 - x0 + 20, 120, "#fff", 1.6, 5)
        for i in range(9):
            x = x0 + i * 0.5 * ppb
            s.line(x, y0 + 8, x, y0 + 112, 1.2 if i % 2 else 2, MID if i % 2 else K, "3 4" if i % 2 else None)
        for j, b in enumerate(QUANT_BEFORE):
            pos = round(b / QUANT_GRID) * QUANT_GRID if snapped else b
            s.rect(x0 + pos * ppb, y0 + 34 + (j % 2) * 34, 38, 22, ACC if snapped else "#fff", 1.8, 3, cls="qa" if snapped else "qb")
    for b in range(4):
        s.text(x0 + b * ppb, 350, f"beat {b + 1}", 15, "start", 600)
    return s


# ================================================================ 7 MIDI
def d_midi():
    s = Sv(340, "midi")
    s.text(24, 34, "1. You play a note", 17, "start", 700, K, OS)
    kbd_small(s, 28, 56, 30, 104)
    s.text(28 + 15, 184, "C", 15, "middle", 700)
    s.text(28 + 15, 204, "60", 15, "middle", 600)
    s.arrow(285, 108, 340, 108, 2)
    s.text(350, 34, "2. MIDI message", 17, "start", 700, K, OS)
    s.rect(350, 50, 190, 138, "#fff", 1.8, 6)
    for i, (a, b) in enumerate((("Note on", ""), ("Note", "60 (middle C)"), ("Velocity", "90"), ("Note off", "1 beat later"))):
        y = 78 + i * 32
        s.text(364, y, a, 16, "start", 700)
        if b:
            s.text(446, y, b, 15, "start", 400)
        if i < 3:
            s.line(350, y + 12, 540, y + 12, 1.0, MID)
    s.arrow(552, 108, 600, 108, 2)
    s.text(606, 34, "3. Sound", 17, "start", 700, K, OS)
    s.rect(606, 66, 90, 90, TINT, 1.8, 8)
    speaker(s, 626, 90, 40)
    s.text(651, 178, "Instrument", 14, "middle", 600)
    s.rect(24, 250, 672, 66, "#fff", 1.8, 8)
    s.text(360, 278, "MIDI carries instructions, not recorded sound.", 18, "middle", 700)
    s.text(360, 304, "Change the instrument and the same notes make a new sound.", 16, "middle", 400)
    return s


# ================================================================ 8 Velocity
def d_velocity():
    s = Sv(340, "velocity", maxv=127, base=292, top=52, vals="/".join(map(str, VELS)))
    s.text(24, 32, "Velocity lane: one bar for each note", 17, "start", 700, K, OS)
    base, top = 292, 52
    s.line(80, base, 690, base, 2)
    s.line(80, top - 8, 80, base, 2)
    for v in (0, 64, 127):
        y = base - (base - top) * v / 127
        s.line(72, y, 80, y, 1.6)
        s.text(66, y + 5, str(v), 14, "end", 600)
    for i, v in enumerate(VELS):
        x = 130 + i * 140
        h = (base - top) * v / 127
        s.rect(x, base - h, 70, h, ACC if v == 127 else TINT, 1.8, 3, cls="vb")
        s.text(x + 35, base - h - 8, str(v), 17, "middle", 700)
        s.text(x + 35, base + 22, ["soft", "medium", "strong", "hardest"][i], 15, "middle", 600)
    return s


# ================================================================ 9 Piano roll
def d_piano():
    s = Sv(340, "piano", gx0=92, gx1=700, gy0=22, rowh=22, rows=13, cols=8)
    gx0, gx1, gy0, rh = 92, 700, 22, 22
    cw = (gx1 - gx0) / 8
    for i in range(13):
        y = gy0 + (12 - i) * rh
        if PIANO_BLACK[i]:
            s.rect(gx0, y, gx1 - gx0, rh, GR, 0)
        s.line(gx0, y, gx1, y, 1.0, MID)
    s.line(gx0, gy0 + 13 * rh, gx1, gy0 + 13 * rh, 1.0, MID)
    for c in range(9):
        s.line(gx0 + c * cw, gy0, gx0 + c * cw, gy0 + 13 * rh, 1.8 if c % 2 == 0 else 1.0, K if c % 2 == 0 else MID)
    for i in range(13):
        y = gy0 + (12 - i) * rh
        if PIANO_BLACK[i]:
            s.rect(20, y + 1, 48, rh - 2, K, 1.0, 2, cls="bk")
        else:
            s.rect(20, y, 72, rh, TINT if i in (0, 12) else "#fff", 1.4, 0, cls="wk")
    s.text(26, gy0 + 16, "C5", 14, "start", 700)
    s.text(26, gy0 + 13 * rh - 6, "C4", 14, "start", 700)
    for semi, c0, ln in PIANO_NOTES:
        y = gy0 + (12 - semi) * rh
        s.rect(gx0 + c0 * cw + 2, y + 3, ln * cw - 4, rh - 6, ACC, 1.6, 3, cls="pn")
    for c in range(0, 8, 2):
        s.text(gx0 + c * cw + 6, 328, f"beat {c // 2 + 1}", 14, "start", 600)
    return s


# ================================================================ 10 Sample
def d_sample():
    s = Sv(340, "sample")
    s.text(24, 32, "One recorded drum hit (the sample)", 17, "start", 700, K, OS)
    s.rect(24, 44, 300, 90, TINT, 1.8, 6)
    env = lambda t: math.exp(-5 * t)
    s.poly(wave_pts(34, 314, 89, 36, 22, 0, env, 300), 1.4)
    s.text(350, 76, "Load it once, then play it", 17, "start", 600)
    s.text(350, 100, "as many times as you like.", 17, "start", 600)
    s.arrow(174, 138, 174, 156, 2)
    x0, bw = 390, 76
    s.text(24, 176, "Timeline: the same sample triggered on every beat", 17, "start", 700, K, OS)
    for i in range(4):
        s.rect(40 + i * 164, 194, 148, 74, "#fff", 1.8, 5)
        s.poly(wave_pts(48 + i * 164, 48 + i * 164 + 40, 231, 22, 5, 0, env, 60), 1.2)
        s.text(40 + i * 164 + 74, 288, f"beat {i + 1}", 15, "middle", 700)
    s.text(40, 322, "Other meaning: one measurement of a sound wave (see Sample rate).", 15, "start", 400, K, SS, True)
    return s


# ================================================================ 11 Waveform
def d_wave():
    s = Sv(340, "wave", y0=170, amp=95)
    s.line(60, 175, 690, 175, 1.6, MID, "6 4")
    s.line(60, 50, 60, 290, 1.8)
    s.line(60, 290, 690, 290, 1.8)
    s.text(48, 60, "loud", 14, "end", 600)
    s.text(48, 179, "0", 14, "end", 600)
    s.text(48, 288, "loud", 14, "end", 600)
    env = lambda t: 0.08 + 0.92 * (math.exp(-((t - 0.28) ** 2) / 0.012) * 0.55 + math.exp(-((t - 0.7) ** 2) / 0.02) * 1.0)
    pts = wave_pts(70, 680, 175, 95, 46, 0, env, 800)
    s.poly(pts, 1.4, K, cls="cv")
    imax = max(range(len(pts)), key=lambda i: -(pts[i][1]))
    px, py = pts[imax]
    s.circ(px, py, 5, ACC, 1.6)
    s.text(px + 14, py + 2, "peak (the loudest point)", 15, "start", 700)
    s.text(380, 322, "time", 16, "middle", 700, K, OS)
    s.text(70, 322, "start", 15, "start", 600)
    s.text(680, 322, "end", 15, "end", 600)
    s.text(70, 36, "tall = loud", 15, "start", 600)
    s.text(300, 36, "short = quiet", 15, "start", 600)
    s.text(520, 36, "flat line = silence", 15, "start", 600)
    return s


# ================================================================ 12 Frequency
def d_freq():
    s = Sv(352, "freq", win_ms=10, px0=110, px1=690)
    x0, x1 = 110, 690
    for i, f in enumerate(FREQS):
        yc = 70 + i * 90
        s.line(x0, yc, x1, yc, 1.0, MID, "5 4")
        s.poly(wave_pts(x0, x1, yc, 30, f * 0.010, 0, None, 400), 2, K, cls="cv")
        s.text(14, yc - 4, f"{f} Hz", 18, "start", 700)
        s.text(14, yc + 18, f"{round(f * 0.010)} cycle{'s' if f * 0.010 > 1 else ''}", 14, "start", 400)
    s.line(x0, 318, x1, 318, 1.6)
    for ms in (0, 5, 10):
        x = x0 + (x1 - x0) * ms / 10
        s.line(x, 318, x, 326, 1.6)
        s.text(x, 338 - 0, f"{ms} ms", 14, "middle", 600)
    return s


# ================================================================ 13 Sample rate
def d_srate():
    s = Sv(340, "srate", per=(8, 16))
    for k, (per, x0) in enumerate(((8, 24), (16, 384))):
        w = 312
        s.text(x0, 30, "Few samples" if k == 0 else "Many samples", 17, "start", 700, K, OS)
        s.rect(x0, 44, w, 196, "#fff", 1.6, 6)
        yc, amp = 142, 70
        s.line(x0 + 10, yc, x0 + w - 10, yc, 1.0, MID, "5 4")
        cyc = 2
        s.poly(wave_pts(x0 + 16, x0 + w - 16, yc, amp, cyc, 0, None, 200), 1.2, "#9a9a9a")
        cnt = per * cyc
        pts = []
        for i in range(cnt + 1):
            t = i / cnt
            px = x0 + 16 + t * (w - 32)
            py = yc - amp * math.sin(2 * math.pi * cyc * t)
            pts.append((px, py))
            s.line(px, yc, px, py, 1.0, ACC)
            s.circ(px, py, 3.6, ACC, 0, cls="sp")
        s.poly(pts, 1.8, K, cls="cv")
        s.text(x0 + w / 2, 262, f"{per} samples per cycle", 16, "middle", 700)
    s.text(360, 300, "Real audio takes 44,100 or 48,000 samples every second.", 17, "middle", 700)
    s.text(360, 324, "Illustration only: the dots are drawn far apart so you can see them.", 14, "middle", 400, K, SS, True)
    return s


# ================================================================ 14 Bit depth
def d_bits():
    s = Sv(340, "bits", bits=(3, 4))
    for k, (bits, x0) in enumerate(((3, 24), (4, 384))):
        w = 312
        N = 2 ** bits
        s.text(x0, 30, f"{bits} bits = {N} levels", 17, "start", 700, K, OS)
        s.rect(x0, 44, w, 220, "#fff", 1.6, 6)
        top, bot = 58, 250
        ys = [top + (bot - top) * i / (N - 1) for i in range(N)]
        for y in ys:
            s.line(x0 + 10, y, x0 + w - 10, y, 1.0, "#b0b0b0")
        pts = []
        cnt = 48
        for i in range(cnt):
            v = math.sin(2 * math.pi * i / cnt)
            idx = round((1 - v) / 2 * (N - 1))
            y = ys[idx]
            xa = x0 + 16 + i * (w - 32) / cnt
            xb = x0 + 16 + (i + 1) * (w - 32) / cnt
            pts += [(xa, y), (xb, y)]
        s.poly(pts, 2, K, cls="cv")
    s.text(360, 296, "Real audio: 16 bits = 65,536 levels and 24 bits = 16,777,216 levels", 17, "middle", 700)
    s.text(360, 322, "More levels means a smoother copy of the wave and a lower noise floor.", 15, "middle", 400)
    return s


# ================================================================ 15 Headroom
def d_headroom():
    s = Sv(340, "headroom", mx=120, mt=34, mb=314, lo=-60, hi=0)
    mt, mb = 34, 314
    ypos = lambda d: mt + (mb - mt) * (0 - d) / 60
    s.rect(100, mt, 70, mb - mt, "#fff", 1.8, 3)
    for d in (0, -6, -12, -18, -24, -36, -48, -60):
        y = ypos(d)
        s.line(170, y, 182, y, 1.6)
        s.text(192, y + 5, "0 dBFS" if d == 0 else f"{d}", 15, "start", 700 if d == 0 else 600)
    peak = -6
    s.rect(104, ypos(peak), 62, mb - ypos(peak) - 2, ACC, 0, 0, cls="mb")
    s.line(100, ypos(0), 170, ypos(0), 3.2)
    s.line(250, ypos(0), 250, ypos(peak), 1.8)
    s.line(242, ypos(0), 258, ypos(0), 1.8)
    s.line(242, ypos(peak), 258, ypos(peak), 1.8)
    s.text(270, (ypos(0) + ypos(peak)) / 2 + 6, "6 dB of headroom", 18, "start", 700)
    s.text(270, ypos(peak) + 36, "loudest peak = -6 dBFS", 17, "start", 600)
    s.rect(340, 150, 350, 150, "#fff", 1.8, 8)
    s.text(356, 182, "Headroom = 0 - peak level", 17, "start", 700, K, OS)
    for i, t in enumerate(("Peak at -6 dBFS: 6 dB of headroom", "Peak at -18 dBFS: 18 dB of headroom", "Peak at 0 dBFS: no headroom left")):
        s.text(356, 214 + i * 30, t, 16, "start", 600)
    s.text(340, 330, "dBFS: decibels relative to full scale", 14, "start", 400, K, SS, True)
    return s


# ================================================================ 16 Clipping
def d_clip():
    s = Sv(340, "clip", cx=(24, 384), cw=312, yc=164, amp=80, limit=80, clipamp=1.55)
    for k, x0 in enumerate((24, 384)):
        w = 312
        yc, lim = 164, 80
        s.text(x0, 30, "Peaks under 0 dBFS" if k == 0 else "Peaks over 0 dBFS", 17, "start", 700, K, OS)
        s.rect(x0, 44, w, 240, "#fff", 1.6, 6)
        s.line(x0 + 10, yc - lim, x0 + w - 10, yc - lim, 1.8, ACC, "7 4")
        s.line(x0 + 10, yc + lim, x0 + w - 10, yc + lim, 1.8, ACC, "7 4")
        s.line(x0 + 10, yc, x0 + w - 10, yc, 1.0, MID, "5 4")
        s.text(x0 + w - 12, yc - lim - 6, "0 dBFS", 14, "end", 700, ACC)
        a = 0.7 if k == 0 else 1.55
        pts = []
        for i in range(0, 241):
            t = i / 240
            v = a * math.sin(2 * math.pi * 2 * t)
            v = max(-1.0, min(1.0, v))
            pts.append((x0 + 16 + t * (w - 32), yc - lim * v))
        s.poly(pts, 2.2, K, cls="cv")
        if k == 1:
            ghost = [(x0 + 16 + t / 240 * (w - 32), yc - lim * a * math.sin(2 * math.pi * 2 * t / 240)) for t in range(0, 241)]
            ghost = [(x, max(48, y)) for x, y in ghost]
    s.text(180, 308, "OK: the whole wave fits", 16, "middle", 600)
    s.text(540, 308, "Clipped: the tops are cut flat", 16, "middle", 600)
    s.text(360, 332, "Cut-off parts are gone for good.", 15, "middle", 400, K, SS, True)
    return s


# ================================================================ 17 EQ
def _logx(f, x0, x1):
    return x0 + (math.log10(f) - math.log10(20)) / 3.0 * (x1 - x0)


def d_eq():
    s = Sv(360, "eq", box="70,40,690,300", fr="20,20000", db="-12,12", bells="150:-4/2000:5")
    x0, x1, y0, y1 = 70, 690, 40, 300
    dby = lambda d: y1 - (d + 12) / 24 * (y1 - y0)
    bands = [("LOW", 20, 250), ("MID", 250, 4000), ("HIGH", 4000, 20000)]
    for i, (nm, a, b) in enumerate(bands):
        xa, xb = _logx(a, x0, x1), _logx(b, x0, x1)
        s.rect(xa, y0, xb - xa, y1 - y0, TINT if i == 1 else "#fff", 0)
        s.text((xa + xb) / 2, 32, nm, 16, "middle", 700, K, OS)
        if i:
            s.line(xa, y0, xa, y1, 1.4, MID, "6 4")
    s.rect(x0, y0, x1 - x0, y1 - y0, "none", 1.8)
    for d in (-12, -6, 0, 6, 12):
        s.line(x0, dby(d), x1, dby(d), 2 if d == 0 else 1.0, K if d == 0 else "#b0b0b0")
        s.text(x0 - 8, dby(d) + 5, f"{d:+d}" if d else "0", 14, "end", 600)
    for f, lab in ((20, "20"), (100, "100"), (1000, "1k"), (10000, "10k"), (20000, "20k")):
        x = _logx(f, x0, x1)
        s.line(x, y1, x, y1 + 7, 1.6)
        s.text(x, y1 + 24, lab, 14, "middle" if f not in (20, 20000) else ("start" if f == 20 else "end"), 600)
    pts = []
    for i in range(0, 201):
        f = 20 * (1000 ** (i / 200))
        pts.append((_logx(f, x0, x1), dby(eq_gain(f, EQ_BELLS))))
    s.poly(pts, 2.8, ACC, cls="cv")
    for fc, g in EQ_BELLS:
        s.circ(_logx(fc, x0, x1), dby(g), 5, K, 0)
    s.text(_logx(150, x0, x1) + 10, dby(-4) + 26, "cut 4 dB at 150 Hz", 15, "start", 700, halo=True)
    s.text(_logx(2000, x0, x1) - 8, dby(5) - 14, "boost 5 dB at 2,000 Hz", 15, "middle", 700, halo=True)
    s.text(14, 20, "dB", 14, "start", 700, MID, OS)
    s.text(380, 352, "Frequency (Hz)", 15, "middle", 700, K, OS)
    return s


# ================================================================ 18 Filter
def d_filter():
    s = Sv(360, "filter", hp=HP_FC, lp=LP_FC, fr="20,20000", db="-30,6")
    for k, (kind, fc, x0) in enumerate((("High-pass", HP_FC, 50), ("Low-pass", LP_FC, 394))):
        w = 280
        y0, y1 = 46, 270
        dby = lambda d: y1 - (d + 30) / 36 * (y1 - y0)
        s.text(x0, 28, f"{kind} filter, cutoff {fc:,} Hz", 16, "start", 700, K, OS)
        s.rect(x0, y0, w, y1 - y0, "#fff", 1.8)
        for d in (-30, -24, -18, -12, -6, -3, 0):
            s.line(x0, dby(d), x0 + w, dby(d), 1.0 if d != 0 else 1.8, "#b0b0b0" if d != 0 else K, None if d in (0, -30) else "3 4")
        for d in (0, -12, -24):
            s.text(x0 - 6, dby(d) + 5, str(d), 13, "end", 600)
        pts = []
        for i in range(0, 161):
            f = 20 * (1000 ** (i / 160))
            d = hp_db(f, fc) if kind == "High-pass" else lp_db(f, fc)
            pts.append((x0 + (math.log10(f) - math.log10(20)) / 3 * w, dby(max(d, -30))))
        s.poly(pts, 2.8, ACC, cls="cv", )
        cx = x0 + (math.log10(fc) - math.log10(20)) / 3 * w
        s.line(cx, y0, cx, y1, 1.4, MID, "6 4")
        s.circ(cx, dby(-3.0103), 5, K, 0)
        s.text(cx + (10 if kind == "High-pass" else -10), dby(-3) + 24, "-3 dB at cutoff", 14, "start" if kind == "High-pass" else "end", 700, halo=True)
        for f, lab in ((20, "20"), (1000, "1k"), (20000, "20k")):
            x = x0 + (math.log10(f) - math.log10(20)) / 3 * w
            s.line(x, y1, x, y1 + 6, 1.6)
            s.text(x, y1 + 22, lab, 13, "middle" if f == 1000 else ("start" if f == 20 else "end"), 600)
        s.text(x0 + w / 2, y1 + 44, "Frequency (Hz)", 14, "middle", 600)
        s.text(x0 + w - 8 if kind == "High-pass" else x0 + 8, y1 - 12, "removes lows" if kind == "High-pass" else "removes highs", 15, "end" if kind == "High-pass" else "start", 700)
    s.text(360, 346, "Past the cutoff, the level falls 12 dB for every octave.", 15, "middle", 400)
    return s


# ================================================================ 19 Compression / 20 Limiter (shared graph frame)
def _transfer(kind):
    s = Sv(376, kind, box="96,24,396,324", rng="-60,0,-60,0", thr=COMP_THR if kind == "comp" else LIM_CEIL, ratio=COMP_RATIO if kind == "comp" else 0)
    x0, y0, x1, y1 = 96, 24, 396, 324
    px = lambda d: x0 + (d + 60) / 60 * (x1 - x0)
    py = lambda d: y1 - (d + 60) / 60 * (y1 - y0)
    s.rect(x0, y0, 300, 300, "#fff", 1.8)
    for d in range(-60, 1, 10):
        s.line(px(d), y0, px(d), y1, 1.0, "#c8c8c8")
        s.line(x0, py(d), x1, py(d), 1.0, "#c8c8c8")
        s.text(px(d), y1 + 20, str(d), 13, "middle", 600)
        s.text(x0 - 7, py(d) + 5, str(d), 13, "end", 600)
    s.text(px(-30), y1 + 44, "Input level (dBFS)", 15, "middle", 700, K, OS)
    s.text(20, py(-30) + 5, "Output", 15, "start", 700, K, OS)
    s.text(20, py(-30) + 23, "(dBFS)", 15, "start", 700, K, OS)
    s.line(px(-60), py(-60), px(0), py(0), 1.6, MID, "7 5")
    return s, px, py


def d_comp():
    s, px, py = _transfer("comp")
    thr = COMP_THR
    s.line(px(thr), 24, px(thr), 324, 1.6, ACC, "6 4")
    pts = []
    for d in range(-60, 1, 2):
        pts.append((px(d), py(comp_out(d, thr, COMP_RATIO))))
    s.poly(pts, 3, K, cls="cv")
    s.text(px(thr) - 6, py(-54), "threshold", 15, "end", 700, ACC)
    s.text(px(thr) - 6, py(-54) + 18, "-20 dBFS", 15, "end", 700, ACC)
    for xin in (-12, 0):
        o = comp_out(xin, thr, COMP_RATIO)
        s.circ(px(xin), py(o), 6, ACC, 1.6, cls="mk")
    s.text(444, 50, "Ratio 4:1", 22, "start", 700, K, OS)
    s.text(444, 82, "Below the threshold: 1:1.", 16, "start", 600)
    s.text(444, 104, "The signal passes unchanged.", 16, "start", 400)
    s.text(444, 142, "Above the threshold:", 16, "start", 600)
    s.text(444, 164, "4 dB over comes out 1 dB over.", 16, "start", 400)
    s.rect(444, 188, 252, 104, "#fff", 1.6, 6)
    s.text(456, 214, "Example", 15, "start", 700, K, OS)
    s.text(456, 238, "In: -12 dBFS (8 dB over)", 16, "start", 600)
    s.text(456, 260, "Out: -18 dBFS (2 dB over)", 16, "start", 600)
    s.text(456, 282, "Dashed line = 1:1 (no change)", 14, "start", 400)
    return s


def d_limit():
    s, px, py = _transfer("limit")
    c = LIM_CEIL
    pts = [(px(d), py(limit_out(d, c))) for d in range(-60, 1, 1)]
    s.poly(pts, 3, K, cls="cv")
    s.line(96, py(c), 396, py(c), 1.6, ACC, "6 4")
    s.text(px(-57), py(c) + 24, "ceiling -3 dBFS", 15, "start", 700, ACC)
    s.text(444, 50, "Ratio: infinity to 1", 22, "start", 700, K, OS)
    s.text(444, 82, "Below the ceiling: unchanged.", 16, "start", 600)
    s.text(444, 142, "At the ceiling: nothing goes", 16, "start", 600)
    s.text(444, 164, "higher, however loud the input.", 16, "start", 400)
    s.rect(444, 188, 252, 104, "#fff", 1.6, 6)
    s.text(456, 214, "Example", 15, "start", 700, K, OS)
    s.text(456, 238, "In: -3 dBFS or lower: same", 16, "start", 600)
    s.text(456, 260, "In: 0 dBFS: out -3 dBFS", 16, "start", 600)
    s.text(456, 282, "Dashed line = 1:1 (no change)", 14, "start", 400)
    return s


# ================================================================ 21 Reverb
def d_reverb():
    s = Sv(350, "reverb", box="60,40,690,280", tmax=2.0, rt60=RT60)
    x0, x1, yc, amp = 60, 690, 160, 100
    ppx = (x1 - x0) / 2.0
    s.line(x0, 40, x0, 290, 1.8)
    s.line(x0, yc, x1, yc, 1.0, MID, "5 4")
    s.line(x0 + 6, yc - amp, x0 + 6, yc + amp, 5)
    for rt, col, sw, cls in ((RT60, ACC, 2.6, "cv"), (0.5, MID, 1.6, "cs")):
        up = [(x0 + (i / 200) * 2.0 * ppx, yc - amp * math.exp(-math.log(1000) * (i / 200) * 2.0 / rt)) for i in range(0, 201)]
        dn = [(x, 2 * yc - y) for x, y in up]
        s.poly(up, sw, col, cls=cls)
        s.poly(dn, sw, col)
    s.poly(wave_pts(x0 + 8, x1, yc, amp, 70, 0, lambda t: math.exp(-math.log(1000) * t * 2.0 / RT60) * (1 if t > 0 else 0), 900), 1.0, "#555")
    s.text(x0 + 16, 40, "dry hit", 15, "start", 700)
    s.text(x0 + 22, 58, "(the original sound)", 14, "start", 400)
    xr = x0 + RT60 * ppx
    s.line(xr, yc - 40, xr, yc + 40, 1.6, K, "4 4")
    s.text(xr, yc + 64, "RT60 = 1.5 s", 16, "middle", 700)
    s.text(xr, yc + 84, "tail has fallen by 60 dB", 14, "middle", 400)
    s.text(x0 + 330, 82, "reverb tail (long hall)", 15, "start", 700, ACC)
    s.text(x0 + 330, 100, "grey: short room, RT60 = 0.5 s", 14, "start", 600, MID)
    for t in (0, 0.5, 1.0, 1.5, 2.0):
        x = x0 + t * ppx
        s.line(x, 292, x, 300, 1.6)
        s.text(x, 318, f"{t:.1f}", 14, "middle", 600)
    s.line(x0, 292, x1, 292, 1.6)
    s.text(x1, 336 - 2, "seconds after the hit", 14, "end", 700, K, OS)
    return s


# ================================================================ 22 Delay
def d_delay():
    s = Sv(340, "delay", bpm=120, ppms=0.36, x0=70, base=250, hmax=150)
    x0, base, hmax = 70, 250, 150
    ppms = 0.36
    s.line(x0 - 10, base, 690, base, 2)
    for t, a in zip(DELAY_MS, DELAY_AMP):
        x = x0 + t * ppms
        h = hmax * a
        s.rect(x - 14, base - h, 28, h, ACC if t == 0 else TINT, 1.8, 3, cls="eb")
        s.text(x, base + 24, f"{t} ms", 16, "middle", 700)
        s.text(x, base - h - 10, "original" if t == 0 else f"repeat {DELAY_MS.index(t)}", 15, "middle", 600)
    for i in range(3):
        xa = x0 + DELAY_MS[i] * ppms + 22
        xb = x0 + DELAY_MS[i + 1] * ppms - 22
        s.arrow(xa, 56, xb, 56, 1.6)
        s.text((xa + xb) / 2, 42, "500 ms", 15, "middle", 700)
    s.text(380, 306, "At 120 BPM one beat is 0.5 s = 500 ms, so each repeat lands on a beat.", 16, "middle", 600)
    s.text(380, 328, "Feedback sets how many repeats you hear; each one is quieter.", 15, "middle", 400)
    return s


# ================================================================ 23 Pan
def d_pan():
    s = Sv(340, "pan", cx=360, half=250, rows="Guitar:-100/Vocal:0/Keys:50")
    cx, half = 360, 250
    for i, (nm, v) in enumerate(PAN_VALUES):
        y = 76 + i * 78
        s.text(14, y + 6, nm, 18, "start", 700)
        s.line(cx - half, y, cx + half, y, 4)
        for tx in (-100, -50, 0, 50, 100):
            s.line(cx + half * tx / 100, y - 9, cx + half * tx / 100, y + 9, 1.6)
        s.circ(cx + half * v / 100, y, 12, ACC, 2, cls="pd")
        lab = "L 100" if v == -100 else ("C" if v == 0 else f"R {v}")
        s.text(cx + half * v / 100, y + 34, lab, 15, "middle", 700)
    s.text(cx - half, 36, "LEFT", 17, "middle", 700, K, OS)
    s.text(cx, 36, "CENTER", 17, "middle", 700, K, OS)
    s.text(cx + half, 36, "RIGHT", 17, "middle", 700, K, OS)
    s.text(360, 322, "Hard left: only the left speaker. Center: both equally. 50% right: mostly the right.", 16, "middle", 600)
    return s


# ================================================================ 24 Automation
def d_auto():
    s = Sv(340, "automation", box="70,40,690,260", bars="1,13", dbs="6,-24")
    x0, x1, y0, y1 = 70, 690, 40, 260
    # vertical axis: +6 at the top, -24 at y_low, "off" (minus infinity) at the bottom edge
    ylow = 230
    def ydb(d):
        if d is None:
            return y1
        return y0 + (6 - d) / 30 * (ylow - y0)
    xb = lambda b: x0 + (b - 1) / 12 * (x1 - x0)
    s.rect(x0, y0, x1 - x0, y1 - y0, "#fff", 1.8)
    for d, lab in ((6, "+6"), (0, "0 dB"), (-12, "-12"), (-24, "-24")):
        s.line(x0, ydb(d), x1, ydb(d), 1.8 if d == 0 else 1.0, K if d == 0 else "#b0b0b0", None if d == 0 else "4 4")
        s.text(x0 - 8, ydb(d) + 5, lab, 14, "end", 600)
    s.text(x0 - 8, y1 + 5, "off", 14, "end", 600)
    for b in range(1, 14):
        s.line(xb(b), y1, xb(b), y1 + 7, 1.4)
        if b % 2 == 1:
            s.text(xb(b), y1 + 24, str(b), 14, "middle", 600)
    pts = [(xb(b), ydb(d)) for b, d in AUTO_PTS]
    s.poly(pts, 3, ACC, cls="cv")
    for x, y in pts:
        s.circ(x, y, 6, "#fff", 2.2, cls="bp")
    s.text(xb(2.15), 214, "fade in", 16, "start", 700)
    s.text(xb(11.85), 214, "fade out", 16, "end", 700)
    s.text(xb(8.5), ydb(-12) + 28, "dip", 16, "middle", 700)
    s.text(xb(5), ydb(0) - 12, "full level", 16, "middle", 700)
    s.text(380, 320, "Bar number.   Each dot is a breakpoint; the DAW draws the line between them.", 15, "middle", 600)
    s.text(14, 24, "Track volume", 15, "start", 700, K, OS)
    return s


# ================================================================ 25 Mixer
def d_mixer():
    s = Sv(380, "mixer", slot="68,300", ticks=";".join(f"{d}:{p}" for d, p in FADER_TICKS))
    top, bot = 122, 318
    names = [("Drums", -4), ("Bass", -6), ("Vocal", 0), ("Master", 0)]
    caps = {"Drums": -4, "Bass": -6, "Vocal": 0, "Master": 0}
    for i, (nm, db) in enumerate(names):
        x = 40 + i * 168
        s.rect(x, 12, 150, 358, "#fff", 1.8, 8)
        s.text(x + 75, 36, nm, 17, "middle", 700, K, OS)
                # pan knob
        if nm != "Master":
            s.circ(x + 40, 74, 13, "#fff", 1.8)
            ang = [-0.7, 0.0, 0.0][i]
            s.line(x + 40, 74, x + 40 + 11 * math.sin(ang), 74 - 11 * math.cos(ang), 2)
            s.text(x + 40, 100, "pan", 13, "middle", 600)
        else:
            s.text(x + 40, 80, "all", 14, "middle", 600)
            s.text(x + 40, 98, "tracks", 14, "middle", 600)
        # meter
        s.rect(x + 112, top + 10, 16, bot - top - 20 + 0, "#fff", 1.4, 2)
        lvl = {"Drums": 0.55, "Bass": 0.45, "Vocal": 0.62, "Master": 0.66}[nm]
        mh = (bot - top - 24) * lvl
        s.rect(x + 114.5, bot - 12 - mh, 11, mh, ACC, 0, 1)
        # fader slot and cap
        sx = x + 84
        s.line(sx, top + 10, sx, bot - 10, 4)
        for d, p in FADER_TICKS:
            y = top + 10 + (bot - top - 20) * p
            s.line(sx - 24, y, sx - 14, y, 1.4)
            s.text(sx - 28, y + 4, f"{d:+d}" if d else "0", 13, "end", 600)
        cy = top + 10 + (bot - top - 20) * fader_pos(db)
        s.rect(sx - 15, cy - 8, 30, 16, ACC, 1.8, 3, cls="cap")
        s.text(x + 75, 336, f"{db:+d} dB" if db else "0 dB", 16, "middle", 700)
        s.text(x + 75, 358, "fader", 13, "middle", 400)
    return s


# ================================================================ 26 Bounce
def d_bounce():
    s = Sv(340, "bounce")
    s.text(24, 32, "Your project: many tracks", 17, "start", 700, K, OS)
    for i, nm in enumerate(("Drums", "Bass", "Guitar", "Vocal")):
        y = 48 + i * 52
        s.rect(24, y, 230, 42, "#fff", 1.6, 5)
        s.text(36, y + 27, nm, 16, "start", 700)
        s.rect(112, y + 8, 130, 26, TINT, 1.4, 3)
    s.arrow(268, 150, 352, 150, 2.4)
    s.text(310, 130, "bounce", 16, "middle", 700)
    s.text(310, 178, "export", 16, "middle", 700)
    s.text(372, 32, "One audio file", 17, "start", 700, K, OS)
    s.rect(372, 48, 170, 200, "#fff", 2, 8)
    s.poly([(498, 48), (542, 92), (498, 92)], 1.6, GR, closed=True)
    s.poly(wave_pts(386, 528, 170, 28, 14, 0, lambda t: 0.3 + 0.7 * abs(math.sin(math.pi * t * 3)), 200), 1.4)
    s.text(457, 120, "song", 18, "middle", 700)
    s.text(457, 232, "stereo mix", 15, "middle", 600)
    s.text(570, 32, "Choose", 17, "start", 700, K, OS)
    for i, (a, b) in enumerate((("WAV", "full quality, large"), ("MP3", "small, lossy"), ("Sample rate", "48,000 Hz"), ("Bit depth", "24 bits"))):
        y = 48 + i * 52
        s.rect(570, y, 130, 42, "#fff", 1.6, 5)
        s.text(580, y + 18, a, 15, "start", 700)
        s.text(580, y + 36, b, 13, "start", 400)
    s.text(360, 300, "The DAW plays the whole project once and writes the sound to a file.", 16, "middle", 600)
    s.text(360, 324, "Check the level first: nothing should clip.", 15, "middle", 400)
    return s


DIAGRAMS = {"daw": d_daw, "track": d_track, "region": d_region, "loop": d_loop, "bpm": d_bpm, "quant": d_quant, "midi": d_midi,
            "velocity": d_velocity, "piano": d_piano, "sample": d_sample, "wave": d_wave, "freq": d_freq, "srate": d_srate,
            "bits": d_bits, "headroom": d_headroom, "clip": d_clip, "eq": d_eq, "filter": d_filter, "comp": d_comp, "limit": d_limit,
            "reverb": d_reverb, "delay": d_delay, "pan": d_pan, "auto": d_auto, "mixer": d_mixer, "bounce": d_bounce}
