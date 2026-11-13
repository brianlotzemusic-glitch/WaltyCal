"""Music notation drawn as SVG with the Bravura SMuFL font (SIL OFL 1.1).

Units are points; SVG y points down. `s` is one staff space. In SMuFL one em is
four staff spaces, and every glyph's origin sits on the baseline, so a clef's
origin is placed on its own line (G line / F line) and a notehead's origin on
its pitch's line or space. Bounding boxes and anchors below are copied from
Bravura's metadata.json (v1.392), in staff spaces with y pointing up.
"""

GLYPH = {  # name: (codepoint, bBoxSW, bBoxNE)
    "gClef": (0xE050, (0.0, -2.632), (2.684, 4.392)),
    "fClef": (0xE062, (-0.02, -2.54), (2.736, 1.048)),
    "noteheadBlack": (0xE0A4, (0.0, -0.5), (1.18, 0.5)),
    "noteheadWhole": (0xE0A2, (0.0, -0.5), (1.688, 0.5)),
    "noteWhole": (0xE1D2, (0.0, -0.548), (1.836, 0.544)),
    "noteHalfUp": (0xE1D3, (0.0, -0.58), (1.364, 3.5)),
    "noteQuarterUp": (0xE1D5, (0.0, -0.564), (1.328, 3.5)),
    "note8thUp": (0xE1D7, (0.0, -0.552), (2.264, 3.492)),
    "restQuarter": (0xE4E5, (0.004, -1.5), (1.08, 1.492)),
}
STEM_UP_SE = (1.18, 0.168)     # noteheadBlack anchors
STEM_DOWN_NW = (0.0, -0.168)
STEM_LEN = 3.5                 # spaces (standard one-octave stem)
LEDGER_EXT = 0.4               # legerLineExtension
# Line weights in spaces: Bravura engraving defaults, nudged up for classroom photocopies
STAFF_W, STEM_W, LEDGER_W = 0.16, 0.13, 0.2

LETTERS = "CDEFGAB"

# Rhythm values for Level A: id -> (glyph, name, beats in 4/4)
RHYTHM = {
    "whole": ("noteWhole", "whole note", "4 beats"),
    "half": ("noteHalfUp", "half note", "2 beats"),
    "quarter": ("noteQuarterUp", "quarter note", "1 beat"),
    "eighth": ("note8thUp", "eighth note", "½ beat"),
    "qrest": ("restQuarter", "quarter rest", "1 beat of silence"),
}

CLEFS = {
    # bottom line pitch, clef glyph, line (1 = bottom) the clef origin sits on, middle-line pitch
    "treble": {"bottom": "E4", "glyph": "gClef", "line": 2, "range": ["C4", "D4", "E4", "F4", "G4", "A4", "B4", "C5", "D5", "E5", "F5", "G5", "A5"]},
    "bass": {"bottom": "G2", "glyph": "fClef", "line": 4, "range": ["E2", "F2", "G2", "A2", "B2", "C3", "D3", "E3", "F3", "G3", "A3", "B3", "C4"]},
}


def diatonic(p):
    return int(p[1:]) * 7 + LETTERS.index(p[0])


def step(pitch, clef):
    """Staff position in half-spaces above the bottom line (0 = bottom line, 8 = top line)."""
    return diatonic(pitch) - diatonic(CLEFS[clef]["bottom"])


def stem_up(st):
    # Notes below the middle line take stems up; on or above the middle line, stems down.
    return st < 4


def ledger_steps(st):
    if st <= -2:
        return list(range(-2, st - 1, -2))
    if st >= 10:
        return list(range(10, st + 1, 2))
    return []


def glyph(name, x, y, s, fill="#000"):
    cp = GLYPH[name][0]
    return f'<text x="{x:.2f}" y="{y:.2f}" font-family="Bravura" font-size="{4 * s:.2f}" fill="{fill}">&#x{cp:X};</text>'


# ---------- Level A: single rhythm glyphs ----------
A_SPACE = 9.0


def rhythm_box(s=A_SPACE):
    w = max(GLYPH[g][2][0] - GLYPH[g][1][0] for g, _, _ in RHYTHM.values()) * s
    h = max(GLYPH[g][2][1] - GLYPH[g][1][1] for g, _, _ in RHYTHM.values()) * s
    return w, h


def rhythm_svg(sym, cx, cy, s=A_SPACE):
    g = RHYTHM[sym][0]
    (x0, y0), (x1, y1) = GLYPH[g][1], GLYPH[g][2]
    ox = cx - (x0 + x1) / 2 * s
    oy = cy + (y0 + y1) / 2 * s  # svg y-down: origin = centre + mid(y) (since y-up -> y-down)
    return glyph(g, ox, oy, s)


# ---------- Levels B and C: one note on a mini staff with clef ----------
B_SPACE = 5.4
STAFF_LEN = 6.6                       # spaces
NOTE_X = 4.0                          # notehead left edge, spaces from staff start
BLOCK_LO, BLOCK_HI = -1.64, 5.5       # vertical extent (spaces above bottom line) covering clef + notes C4..A5 / E2..C4


def staff_box(s=B_SPACE):
    return STAFF_LEN * s, (BLOCK_HI - BLOCK_LO) * s


def mini_staff_svg(pitch, clef, cx, cy, s=B_SPACE, length=STAFF_LEN, note_x=NOTE_X, notehead="quarter"):
    """One clef + one note, centred on (cx, cy). Returns svg string."""
    x0 = cx - STAFF_LEN * s / 2
    yb = cy + (BLOCK_HI + BLOCK_LO) / 2 * s  # bottom staff line
    out = []
    for i in range(5):
        y = yb - i * s
        out.append(f'<line x1="{x0:.2f}" y1="{y:.2f}" x2="{x0 + length * s:.2f}" y2="{y:.2f}" stroke="#000" stroke-width="{STAFF_W * s:.2f}"/>')
    c = CLEFS[clef]
    out.append(glyph(c["glyph"], x0 + 0.15 * s, yb - (c["line"] - 1) * s, s))
    out.append(note_svg(pitch, clef, x0 + note_x * s, yb, s, notehead))
    return "".join(out)


def note_svg(pitch, clef, nx, yb, s, notehead="quarter"):
    st = step(pitch, clef)
    y = yb - st * s / 2
    out = []
    head_w = GLYPH["noteheadWhole" if notehead == "whole" else "noteheadBlack"][2][0]
    for ls in ledger_steps(st):
        ly = yb - ls * s / 2
        out.append(f'<line x1="{nx - LEDGER_EXT * s:.2f}" y1="{ly:.2f}" x2="{nx + (head_w + LEDGER_EXT) * s:.2f}" y2="{ly:.2f}" stroke="#000" stroke-width="{LEDGER_W * s:.2f}"/>')
    if notehead == "whole":
        out.append(glyph("noteheadWhole", nx, y, s))
        return "".join(out)
    out.append(glyph("noteheadBlack", nx, y, s))
    sw = STEM_W * s
    if stem_up(st):
        x = nx + STEM_UP_SE[0] * s - sw / 2
        out.append(f'<line x1="{x:.2f}" y1="{y - STEM_UP_SE[1] * s:.2f}" x2="{x:.2f}" y2="{y - STEM_LEN * s:.2f}" stroke="#000" stroke-width="{sw:.2f}"/>')
    else:
        x = nx + STEM_DOWN_NW[0] * s + sw / 2
        out.append(f'<line x1="{x:.2f}" y1="{y - STEM_DOWN_NW[1] * s:.2f}" x2="{x:.2f}" y2="{y + STEM_LEN * s:.2f}" stroke="#000" stroke-width="{sw:.2f}"/>')
    return "".join(out)


def reference_staff_svg(clef, x0, yb, s, labels=True, label_font="Source Sans 3"):
    """A full staff showing every pitch of the level's range as whole notes, named underneath."""
    rng = CLEFS[clef]["range"]
    gap = 2.9
    start = 4.0
    length = start + gap * len(rng) + 0.6
    out = []
    for i in range(5):
        y = yb - i * s
        out.append(f'<line x1="{x0:.2f}" y1="{y:.2f}" x2="{x0 + length * s:.2f}" y2="{y:.2f}" stroke="#000" stroke-width="{STAFF_W * s:.2f}"/>')
    c = CLEFS[clef]
    out.append(glyph(c["glyph"], x0 + 0.3 * s, yb - (c["line"] - 1) * s, s))
    for i, p in enumerate(rng):
        nx = x0 + (start + gap * i) * s
        out.append(note_svg(p, clef, nx, yb, s, notehead="whole"))
        if labels:
            out.append(f'<text x="{nx + 0.844 * s:.2f}" y="{yb + 3.6 * s:.2f}" font-family="{label_font}" font-weight="700" font-size="{1.5 * s:.2f}" text-anchor="middle">{p[0]}</text>')
    return "".join(out), length * s
