"""Kid-friendly rhythm notation in 4/4, drawn as SVG with Bravura (SIL OFL 1.1).

One bar of unpitched rhythm on a five-line staff. Every note sits on the middle line, so every stem goes down (down on or above the
middle line), attached to the LEFT edge of the notehead. Paired eighth notes (ti-ti) share a beam at the stem ends. A quarter rest
sits on the middle line. Pattern letters: Q = quarter note (ta), E = pair of eighth notes (ti-ti), R = quarter rest.
Every pattern letter fills exactly one beat, so a pattern of four letters always adds up to 4/4.
"""
CP_PERC = 0xE069       # unpitched percussion clef
CP_TS4 = 0xE084        # time signature digit 4
CP_HEAD = 0xE0A4       # black notehead
CP_QREST = 0xE4E5      # quarter rest
HEAD_W = 1.18          # spaces
STEM_W = 0.13
STEM_LEN = 3.5
STEM_DOWN_NW_Y = -0.168   # notehead anchor, spaces above the notehead centre
BEAM_T = 0.5
STAFF_W = 0.16
LEAD = 0.55            # spaces between a beat's left edge and its first note
SYL = {"Q": "ta", "E": "ti-ti", "R": "rest"}
BEATS = {"Q": 1, "E": 1, "R": 1}


def f(v):
    return f"{v:.2f}".rstrip("0").rstrip(".")


def words(pat):
    """The spoken syllables for a pattern, with the rest in brackets."""
    return " ".join("(rest)" if c == "R" else SYL[c] for c in pat)


def layout(sp, beats, bw):
    """x positions in points: staff start, clef, time signature, first beat edge, final barline."""
    x_clef = 0.5 * sp
    x_ts = x_clef + 1.528 * sp + 0.9 * sp
    x0 = x_ts + 1.88 * sp + 0.9 * sp
    x_end = x0 + beats * bw
    return x_clef, x_ts, x0, x_end


def rhythm_svg(pat, sp=5.5, bw=50, cls="rh", rows=("num", "syl"), label=None, clef=True, pad=2.5):
    """Return (svg_string, width, height). pat = string of Q/E/R, or None for an empty staff."""
    beats = 4 if pat is None else sum(BEATS[c] for c in pat)
    if not clef:   # bare symbol sample: no clef or time signature
        x_clef, x_ts, x0, x_end = 0, 0, 1.0 * sp, 1.0 * sp + beats * bw
    else:
        x_clef, x_ts, x0, x_end = layout(sp, beats, bw)
    width = x_end + 0.9 * sp + pad
    x_clef += pad
    x_ts += pad
    x0 += pad
    x_end += pad
    top = pad + 0.6 * sp
    mid = top + 2 * sp
    bottom = top + 4 * sp
    stem_top = mid + STEM_DOWN_NW_Y * sp          # the stem starts 0.168 spaces above the notehead centre
    stem_bot = stem_top + STEM_LEN * sp
    y = stem_bot + 0.3 * sp
    row_y = {}
    fs = max(8.5, sp * 1.85)
    for r in rows:
        y += fs * 1.0
        row_y[r] = y
        y += fs * 0.18
    height = y + 3
    g = []
    ff = "font-family:Bravura"
    for i in range(5):
        yy = top + i * sp
        g.append(f'<line class="sl" x1="{f(pad)}" y1="{f(yy)}" x2="{f(x_end)}" y2="{f(yy)}" stroke="#000" stroke-width="{f(STAFF_W * sp)}"/>')
    # barlines: thin line at the start of the staff, final barline (thin + thick) at the end
    g.append(f'<rect class="bar" x="{f(pad)}" y="{f(top)}" width="{f(0.16 * sp)}" height="{f(4 * sp)}"/>')
    g.append(f'<rect class="bar" x="{f(x_end - 0.9 * sp)}" y="{f(top)}" width="{f(0.16 * sp)}" height="{f(4 * sp)}"/>')
    g.append(f'<rect class="bar" x="{f(x_end - 0.5 * sp)}" y="{f(top)}" width="{f(0.5 * sp)}" height="{f(4 * sp)}"/>')
    if clef:
        g.append(f'<text class="clef" x="{f(x_clef)}" y="{f(mid)}" style="{ff}" font-size="{f(4 * sp)}">{chr(CP_PERC)}</text>')
        g.append(f'<text class="ts" data-n="4" x="{f(x_ts)}" y="{f(mid - sp)}" style="{ff}" font-size="{f(4 * sp)}">{chr(CP_TS4)}</text>')
        g.append(f'<text class="ts" data-n="4" x="{f(x_ts)}" y="{f(mid + sp)}" style="{ff}" font-size="{f(4 * sp)}">{chr(CP_TS4)}</text>')
    cx_labels = []   # (beat index, centre x of the beat's first sound group)
    if pat is not None:
        for k, c in enumerate(pat):
            bx = x0 + k * bw + LEAD * sp
            if c == "Q":
                heads = [bx]
            elif c == "E":
                heads = [bx, bx + bw / 2]
            else:
                heads = []
            for hx in heads:
                g.append(f'<text class="nh" x="{f(hx)}" y="{f(mid)}" style="{ff}" font-size="{f(4 * sp)}">{chr(CP_HEAD)}</text>')
                g.append(f'<rect class="stem" x="{f(hx)}" y="{f(stem_top)}" width="{f(STEM_W * sp)}" height="{f(STEM_LEN * sp)}"/>')
            if c == "E":
                bt = BEAM_T * sp
                g.append(f'<rect class="beam" x="{f(heads[0])}" y="{f(stem_bot - bt)}" width="{f(heads[1] + STEM_W * sp - heads[0])}" height="{f(bt)}"/>')
            if c == "R":
                g.append(f'<text class="rest" x="{f(bx)}" y="{f(mid)}" style="{ff}" font-size="{f(4 * sp)}">{chr(CP_QREST)}</text>')
                cx = bx + 0.54 * sp
            elif c == "Q":
                cx = bx + HEAD_W * sp / 2
            else:
                cx = (heads[0] + heads[1] + HEAD_W * sp) / 2
            cx_labels.append(cx)
        for r in rows:
            for k, c in enumerate(pat):
                txt = str(k + 1) if r == "num" else ("(rest)" if c == "R" else SYL[c])
                if r == "num":
                    # the counting number sits under the first sound of the beat
                    cx = x0 + k * bw + LEAD * sp + (0.54 * sp if c == "R" else HEAD_W * sp / 2)
                else:
                    cx = cx_labels[k]
                weight = 500 if r == "syl" else 400
                g.append(f'<text class="{r}" x="{f(cx)}" y="{f(row_y[r])}" text-anchor="middle" '
                         f'style="font-family:Oswald;font-weight:{weight}" font-size="{f(fs)}" fill="#000">{txt}</text>')
    attrs = (f'class="{cls}" data-pat="{"" if pat is None else pat}" data-beats="{beats}" data-sp="{f(sp)}" data-bw="{f(bw)}" data-x0="{f(x0)}" '
             f'data-lead="{f(LEAD * sp)}" data-clef="{1 if clef else 0}" data-label="{label or ""}"')
    svg = (f'<svg {attrs} xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {f(width)} {f(height)}" width="{f(width)}" height="{f(height)}">'
           + "".join(g) + "</svg>")
    return svg, width, height


def beat_xs(sp, bw, beats=4, clef=True, pad=2.5):
    """Centre x of the first sound of each beat, as rhythm_svg places it."""
    x0 = (layout(sp, beats, bw)[2] if clef else 1.0 * sp) + pad
    return [x0 + k * bw + LEAD * sp + HEAD_W * sp / 2 for k in range(beats)]


def dots_svg(xs, width, r=7, nums=True, cls="dots", label=None):
    """The beat-dot row: one dot per beat at the given centre x values (evenly spaced), numbered 1-4 underneath."""
    pad = 3
    cy = pad + r
    h = pad * 2 + 2 * r + (16 if nums else 0)
    cs = "".join(f'<circle class="dot" cx="{f(x)}" cy="{f(cy)}" r="{r}" fill="ACC" stroke="#000" stroke-width="1.6"/>' for x in xs)
    if nums:
        cs += "".join(f'<text class="cnt" x="{f(x)}" y="{f(cy + r + 14)}" text-anchor="middle" style="font-family:Oswald;font-weight:400" font-size="13">{i + 1}</text>'
                      for i, x in enumerate(xs))
    return (f'<svg class="{cls}" data-label="{label or ""}" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {f(width)} {f(h)}" width="{f(width)}" height="{f(h)}">{cs}</svg>', width, h)
